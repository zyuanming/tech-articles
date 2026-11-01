#!/usr/bin/env python3
"""USB-C / USB Power Delivery, measured on a small deterministic model. MIT.

Nothing here talks to a real port.  It reproduces the arithmetic that decides
what a charger and a phone agree on: the two pull-down resistors, the
biphase-mark encoding, the packet, the contract, the cable limits.

Every number the article quotes comes out of build().
"""
from __future__ import annotations

import json
import math

# ---------------------------------------------------------------- constants

RD = 5100.0                      # sink pull-down, ohm (spec: 5.1k +/- 10%)
V_RD_USB = (0.15, 0.61)          # legal window for "default USB" current
V_RD_1_5 = (0.61, 1.16)          # legal window for 1.5 A
V_RD_3_0 = (1.16, 2.45)          # legal window for 3 A
VCONN = 5.0

SOURCES = [                      # name, advertised current, model current source
    ('default USB', 0.5, 80e-6),
    ('1.5 A', 1.5, 180e-6),
    ('3 A', 3.0, 330e-6),
]

# 4b5b data symbols, the table 100BASE-TX / FDDI use (and USB PD reuses)
FOURB5B = {
    0x0: 0b11110, 0x1: 0b01001, 0x2: 0b10100, 0x3: 0b10101,
    0x4: 0b01010, 0x5: 0b01011, 0x6: 0b01110, 0x7: 0b01111,
    0x8: 0b10010, 0x9: 0b10011, 0xA: 0b10110, 0xB: 0b10111,
    0xC: 0b11010, 0xD: 0b11011, 0xE: 0b11100, 0xF: 0b11101,
}
INV_4B5B = {v: k for k, v in FOURB5B.items()}

MSG = {  # the handful of message types this model needs
    0x01: 'Source_Capabilities',
    0x02: 'Request',
    0x03: 'Accept',
    0x04: 'Reject',
    0x06: 'PS_RDY',
    0x07: 'Get_Source_Cap',
    0x09: 'DR_Swap',
    0x0A: 'PR_Swap',
    0x11: 'EPR_Mode',
    0x12: 'EPR_Source_Caps',
}
MSG_ID = {v: k for k, v in MSG.items()}


# ---------------------------------------------------------------- CRC-32

def _crc_table():
    out = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ 0xEDB88320 if c & 1 else c >> 1
        out.append(c)
    return out


CRC_TABLE = _crc_table()


def crc32(data: bytes) -> int:
    """Reflected CRC-32, the same polynomial USB PD uses for its frame."""
    c = 0xFFFFFFFF
    for b in data:
        c = CRC_TABLE[(c ^ b) & 0xFF] ^ (c >> 8)
    return c ^ 0xFFFFFFFF


# ---------------------------------------------------------------- headers

def header(msg_type: int, ndo: int, msg_id: int, rev: int = 2,
           power_role: int = 0, data_role: int = 0, ext: int = 0) -> int:
    """16-bit PD message header, laid out the way the spec numbers its bits."""
    h = 0
    h |= (ext & 1) << 15
    h |= (ndo & 7) << 12
    h |= (msg_id & 7) << 9
    h |= (power_role & 1) << 8
    h |= (rev & 3) << 6
    h |= (data_role & 1) << 5
    h |= (msg_type & 0x1F)
    return h


def decode_header(h: int) -> dict:
    return dict(
        ext=(h >> 15) & 1,
        ndo=(h >> 12) & 7,
        msg_id=(h >> 9) & 7,
        power_role=(h >> 8) & 1,
        rev=(h >> 6) & 3,
        data_role=(h >> 5) & 1,
        type=(h >> 0) & 0x1F,
        name=MSG.get(h & 0x1F, 'type %d' % (h & 0x1F)),
    )


# ---------------------------------------------------------------- PDOs

def fixed_pdo(volts: float, amps: float, dual_role_power: int = 1) -> int:
    """A fixed supply PDO: voltage in 50 mV steps, current in 10 mA steps."""
    mv = int(round(volts * 1000))
    ma = int(round(amps * 1000))
    assert mv % 50 == 0 and ma % 10 == 0
    p = 0
    p |= (0 << 30)                       # 00 = fixed supply
    p |= (dual_role_power & 1) << 29
    p |= (0 << 28)                       # usable in USB suspend: no
    p |= (1 << 27)                       # unconstrained power: yes
    p |= (1 << 26)                       # USB communications capable: yes
    p |= (0 << 25)                       # dual-role data: no
    p |= (0 << 20)                       # peak current: none
    p |= ((mv // 50) & 0x3FF) << 10
    p |= ((ma // 10) & 0x3FF)
    return p


def decode_pdo(p: int) -> dict:
    kind = (p >> 30) & 3
    return dict(
        kind={0: 'fixed', 1: 'battery', 2: 'variable', 3: 'APDO'}[kind],
        dual_role_power=(p >> 29) & 1,
        unconstrained=(p >> 27) & 1,
        usb_comm=(p >> 26) & 1,
        mv=((p >> 10) & 0x3FF) * 50,
        ma=(p & 0x3FF) * 10,
    )


def pct(a: float, b: float) -> float:
    return 100.0 * a / b


# ---------------------------------------------------------------- 1. CC pins

def cc_detect() -> dict:
    """What voltage a 5.1k pull-down produces, and which band it lands in."""
    bands = [('0.15 - 0.61 V', *V_RD_USB, 0.5),
             ('0.61 - 1.16 V', *V_RD_1_5, 1.5),
             ('1.16 - 2.45 V', *V_RD_3_0, 3.0)]
    rows = []
    for name, amps, ip in SOURCES:
        v = ip * RD
        hit = [b for b in bands if b[1] <= v < b[2]][0]
        # worst case: Rd low, Ip high; and Rd high, Ip low
        v_hi = ip * 1.10 * RD * 1.10
        v_lo = ip * 0.90 * RD * 0.90
        rows.append(dict(name=name, advertised_a=amps, ip_ua=round(ip * 1e6, 1),
                         rd_ohm=RD, v_cc=round(v, 4),
                         band=hit[0], decided_a=hit[3],
                         v_lo=round(v_lo, 4), v_hi=round(v_hi, 4),
                         band_lo=[b[0] for b in bands if b[1] <= v_lo < b[2]][0],
                         band_hi=[b[0] for b in bands if b[1] <= v_hi < b[2]][0],
                         margin_lo=round(v - hit[1], 4),
                         margin_hi=round(hit[2] - v, 4)))
    # what a sink with no pull-down looks like: a third scenario, nothing there
    open_circuit = dict(name='nothing on the pin', v_cc=None, note='source keeps 3.3 V')
    return dict(rd_ohm=RD, bands=[dict(label=b[0], lo=b[1], hi=b[2], amps=b[3])
                                 for b in bands],
                rows=rows, open_circuit=open_circuit,
                worst_band_change=any(r['band_lo'] != r['band'] or
                                      r['band_hi'] != r['band'] for r in rows))


def cc_flip() -> dict:
    """Two orientations of the plug, one pull-down: which pin goes low."""
    cases = []
    for label, rd_on in (('正常插', 'CC1'), ('翻转插', 'CC2')):
        pins = {'CC1': 'Rd' if rd_on == 'CC1' else '浮空',
                'CC2': 'Rd' if rd_on == 'CC2' else '浮空'}
        low = [k for k, v in pins.items() if v == 'Rd'][0]
        cases.append(dict(label=label, pins=pins, v_cc1=0.408 if low == 'CC1' else 3.3,
                          v_cc2=0.408 if low == 'CC2' else 3.3,
                          low_pin=low,
                          source_reads='3 A 档' if low else '无设备'))
    return dict(cases=cases, low_pin_differs=True,
                both_low_note='两端都接了 Rd（非合规直连）会两脚都低')


# ---------------------------------------------------------------- 2. BMC

UI_SAMPLES = 64


def bmc_encode(bits, ui=UI_SAMPLES):
    """One transition per bit cell, plus one in the middle for a 1."""
    level = 0
    wave = []
    edges = []
    for i, b in enumerate(bits):
        level ^= 1
        edges.append(i * ui)
        for _ in range(ui // 2):
            wave.append(level)
        if b:
            level ^= 1
            edges.append(i * ui + ui // 2)
        for _ in range(ui - ui // 2):
            wave.append(level)
    return wave, edges


def bmc_decode(wave, nbits, ui=UI_SAMPLES, offset=0.0):
    """Sample at 1/4 and 3/4 of each cell; a 1 toggles between them."""
    out = []
    for i in range(nbits):
        t1 = int(round((i + 0.25 + offset) * ui))
        t2 = int(round((i + 0.75 + offset) * ui))
        if t1 < 0 or t2 >= len(wave):
            out.append(None)
            continue
        out.append(1 if wave[t1] != wave[t2] else 0)
    return out


def bmc() -> dict:
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    wave, edges = bmc_encode(bits)
    rec = bmc_decode(wave, len(bits))
    # edges per bit, counted from the encoder
    per_bit = []
    for i, b in enumerate(bits):
        per_bit.append(sum(1 for e in edges if i * UI_SAMPLES <= e < (i + 1) * UI_SAMPLES))

    # clock offset sweep: how far can the receiver's sampling instant drift?
    import random
    rng = random.Random(20261228)
    payload = [rng.randrange(2) for _ in range(176)]   # one 22-byte frame
    w2, _ = bmc_encode(payload)
    sweep = []
    for k in range(0, 61):
        off = k / 100.0
        got = bmc_decode(w2, len(payload), offset=off)
        err = sum(1 for a, b in zip(got, payload) if a != b)
        sweep.append(dict(offset_ui=off, errors=err, ber=err / len(payload)))
    first_bad = next((r for r in sweep if r['errors'] > 0), None)

    # a receiver whose own clock runs fast or slow: the sampling point drifts
    fsweep = []
    for ppm in range(0, 5001, 50):
        eps = ppm * 1e-6
        got = []
        for i in range(len(payload)):
            t1 = int(round((i + 0.25) * (1 + eps) * UI_SAMPLES))
            t2 = int(round((i + 0.75) * (1 + eps) * UI_SAMPLES))
            if t2 >= len(w2):
                got.append(None)
            else:
                got.append(1 if w2[t1] != w2[t2] else 0)
        err = sum(1 for a, b in zip(got, payload) if a != b)
        fsweep.append(dict(ppm=ppm, errors=err, ber=round(err / len(payload), 5)))
    first_freq = next((r for r in fsweep if r['errors'] > 0), None)
    limit_ppm = int(0.25 / len(payload) / 1e-6)
    return dict(bits=bits, ui_samples=UI_SAMPLES, wave=wave[:UI_SAMPLES * 8],
                edges=edges, edges_per_bit=per_bit, decoded=rec,
                round_trip=rec == bits, sweep=sweep, fsweep=fsweep,
                payload_bits=len(payload), first_freq=first_freq,
                limit_ppm=limit_ppm,
                window_ui=0.25, first_bad=first_bad,
                samples_per_bit_used=UI_SAMPLES)


# ---------------------------------------------------------------- 3. 4b5b

def bits_of(data: bytes) -> list:
    out = []
    for b in data:
        for k in range(8):
            out.append((b >> k) & 1)      # low bit first
    return out


def nibbles_of(data: bytes) -> list:
    out = []
    for b in data:
        out.append(b & 0xF)
        out.append(b >> 4)
    return out


def fourb5b(data: bytes) -> list:
    bits = []
    for n in nibbles_of(data):
        code = FOURB5B[n]
        for k in range(4, -1, -1):
            bits.append((code >> k) & 1)
    return bits


def unfourb5b(bits) -> bytes:
    nib = []
    for i in range(0, len(bits) - 4, 5):
        code = 0
        for k in range(5):
            code = (code << 1) | bits[i + k]
        nib.append(INV_4B5B[code])
    out = bytearray()
    for i in range(0, len(nib) - 1, 2):
        out.append(nib[i] | (nib[i + 1] << 4))
    return bytes(out)


def max_run(bits) -> int:
    best = cur = 1
    for a, b in zip(bits, bits[1:]):
        cur = cur + 1 if a == b else 1
        best = max(best, cur)
    return best


def ones_share(bits) -> float:
    return sum(bits) / len(bits)


def fourb5b_stats() -> dict:
    import random
    rng = random.Random(20261228)
    raw_runs, c5_runs = [], []
    for _ in range(2000):
        payload = bytes(rng.randrange(256) for _ in range(6))
        raw_runs.append(max_run(bits_of(payload)))
        c5_runs.append(max_run(fourb5b(payload)))
    # the pathological payload: all zero bytes
    zero = bytes(6)
    zero_raw = max_run(bits_of(zero))
    zero_c5 = max_run(fourb5b(zero))
    ok = unfourb5b(fourb5b(b'USB PD')) == b'USB PD'
    ones_per_code = [bin(c).count('1') for c in FOURB5B.values()]
    return dict(ones_per_symbol_min=min(ones_per_code),
                ones_per_symbol_max=max(ones_per_code),
                trials=2000, raw_min=min(raw_runs), raw_max=max(raw_runs),
                raw_mean=round(sum(raw_runs) / len(raw_runs), 2),
                c5_min=min(c5_runs), c5_max=max(c5_runs),
                c5_mean=round(sum(c5_runs) / len(c5_runs), 2),
                zero_raw=zero_raw, zero_c5=zero_c5,
                ones_raw=round(ones_share(bits_of(zero)), 3),
                ones_c5=round(ones_share(fourb5b(zero)), 3),
                round_trip=ok, raw_hist=_hist(raw_runs), c5_hist=_hist(c5_runs))


def _hist(vals):
    h = {}
    for v in vals:
        h[v] = h.get(v, 0) + 1
    return {str(k): h[k] for k in sorted(h)}


# ---------------------------------------------------------------- 4. frame

def build_message(caps_mv_ma, msg_type='Source_Capabilities', msg_id=0,
                  rev=2, power_role=0) -> dict:
    header_word = header(MSG_ID[msg_type], len(caps_mv_ma), msg_id,
                         rev=rev, power_role=power_role)
    body = b''.join(header_word.to_bytes(2, 'little')[i:i + 1] for i in range(2))
    for mv, ma in caps_mv_ma:
        body += fixed_pdo(mv / 1000.0, ma / 1000.0).to_bytes(4, 'little')
    crc = crc32(body)
    frame = body + crc.to_bytes(4, 'little')
    return dict(msg_type=msg_type, header=header_word,
                header_fields=decode_header(header_word),
                ndo=len(caps_mv_ma), body_len=len(body), frame_len=len(frame),
                crc=crc, crc_hex='%08X' % crc, bytes=list(frame),
                bits=len(frame) * 8)


def frame_check() -> dict:
    m = build_message([(5000, 3000), (9000, 3000), (15000, 3000), (20000, 3250)])
    # a single flipped bit anywhere must be visible to the CRC
    caught = 0
    total = m['frame_len'] * 8
    for k in range(total):
        b = bytearray(m['bytes'])
        b[k // 8] ^= 1 << (k % 8)
        if crc32(bytes(b[:-4])) != int.from_bytes(bytes(b[-4:]), 'little'):
            caught += 1
    # and the standard check value for this CRC
    return dict(message=m, single_bit_flipped=total, single_bit_caught=caught,
                check_value='%08X' % crc32(b'123456789'),
                fourb5b_bits=len(fourb5b(bytes(m['bytes']))),
                bmc_samples=len(fourb5b(bytes(m['bytes']))) * UI_SAMPLES)


# ---------------------------------------------------------------- 5. trace

def negotiation() -> dict:
    """Source_Caps -> Request -> Accept -> PS_RDY, then a PPS setpoint."""
    caps = [(5000, 3000), (9000, 3000), (15000, 3000), (20000, 3250)]
    t0 = 0.150                       # tCCDebounce, this model's assumption
    ev = []
    mid = 0

    def add(t, src, dst, mtype, note, v=None, a=None):
        nonlocal mid
        ev.append(dict(t=round(t, 4), src=src, dst=dst, msg=mtype,
                       msg_id=mid % 8, v=v, a=a, note=note))
        mid += 1

    add(0.000, 'sink', 'source', 'attach', '插上，CC 被拉低')
    add(t0, 'source', 'sink', 'Source_Capabilities', '4 档固定电压', 20.0, 3.25)
    add(t0 + 0.006, 'sink', 'source', 'Request', '选中 20 V 档', 20.0, 3.25)
    add(t0 + 0.012, 'source', 'sink', 'Accept', '同意，但还没通电')
    ramp = 100.0                     # mV per ms, this model's assumption
    steps_ms = int((20000 - 5000) / ramp)
    t_ready = 0.162 + steps_ms / 1000.0
    add(round(t_ready, 3), 'source', 'sink', 'PS_RDY', '电压已到位', 20.0, 3.25)
    add(round(t_ready + 0.008, 3), 'sink', 'source', 'Request', '改用 PPS 9.0 V', 9.0, 3.0)
    add(round(t_ready + 0.016, 3), 'source', 'sink', 'Accept', 'PPS 以 20 mV 步进')
    add(round(t_ready + 0.034, 3), 'source', 'sink', 'PS_RDY', 'PPS 到位', 9.0, 3.0)
    # vbus as a function of time, 5 V -> 20 V at the model's ramp rate
    vbus = []
    for k in range(0, steps_ms + 1, 5):
        vbus.append(dict(t=round(0.162 + k / 1000.0, 3), mv=5000 + k * ramp))
    return dict(tcc_debounce=t0, events=ev, ramp_mv_per_ms=ramp,
                ramp_ms_5_to_20=steps_ms, vbus=vbus,
                accept_to_ready=round(t_ready - 0.162, 3),
                attach_to_ready=round(t_ready, 3))


# ---------------------------------------------------------------- 6. rules

def power_rules() -> dict:
    """The rule table, plus what it costs to hit a given wattage."""
    rules = [
        dict(max_w=15, v=5.0, a=3.0, cable='任意线缆'),
        dict(max_w=27, v=9.0, a=3.0, cable='任意线缆'),
        dict(max_w=45, v=15.0, a=3.0, cable='任意线缆'),
        dict(max_w=60, v=20.0, a=3.0, cable='任意线缆'),
        dict(max_w=100, v=20.0, a=5.0, cable='5 A 线，带 e-marker'),
        dict(max_w=140, v=28.0, a=5.0, cable='EPR 线，带 e-marker'),
        dict(max_w=180, v=36.0, a=5.0, cable='EPR 线，带 e-marker'),
        dict(max_w=240, v=48.0, a=5.0, cable='EPR 线，印 240 W'),
    ]
    wanted = [18, 27, 30, 45, 60, 65, 96, 100, 140, 180, 240]
    picks = []
    for w in wanted:
        r = next(r for r in rules if r['max_w'] >= w)
        picks.append(dict(want_w=w, v=r['v'], a=round(w / r['v'], 3),
                          need_a=math.ceil(w / r['v'] * 10) / 10,
                          cable=r['cable'], rule_w=r['max_w'],
                          headroom_w=round(r['max_w'] - w, 2)))
    # 100 W at 5 V would need this much current; the connector cannot do it
    return dict(rules=rules, picks=picks,
                at_5v_for_100w=round(100 / 5, 2),
                at_20v_for_100w=round(100 / 20, 2),
                spr_max_w=100, epr_max_w=240)


# ---------------------------------------------------------------- 7. PPS

def pps() -> dict:
    v_lo, v_hi, step_mv = 3.3, 21.0, 0.020
    v_steps = int(round((v_hi - v_lo) / step_mv)) + 1
    i_steps = int(round(5.0 / 0.05)) + 1
    targets = [3.7, 4.2, 8.437, 9.0, 11.1, 20.0]
    rows = []
    for t in targets:
        n = round((t - v_lo) / step_mv)
        got = v_lo + n * step_mv
        err = round((got - t) * 1000, 2)
        rows.append(dict(target=t, steps=n, set=round(got, 3),
                         err_mv=0.0 if abs(err) < 0.005 else err))
    # cable drop: the charger regulates at its own terminals
    r_cable = 0.10
    loads = [(9.0, 3.0), (9.0, 1.5), (20.0, 3.0)]
    drop = []
    for v, a in loads:
        drop.append(dict(setpoint=v, amps=a, cable_v=round(a * r_cable, 3),
                         device_v=round(v - a * r_cable, 3),
                         comp_setpoint=round(v + a * r_cable, 3),
                         comp_steps=int(round((a * r_cable) / step_mv))))
    return dict(v_lo=v_lo, v_hi=v_hi, step_mv=step_mv, v_steps=v_steps,
                i_step_ma=50, i_steps=i_steps, rows=rows,
                max_err_mv=round(step_mv * 1000 / 2, 2),
                r_cable=r_cable, drop=drop)


# ---------------------------------------------------------------- 8. e-marker

def emarker() -> dict:
    cases = [
        dict(need_v=20.0, need_a=3.0, cable='无 e-marker', emarked=False, epr=False),
        dict(need_v=20.0, need_a=5.0, cable='无 e-marker', emarked=False, epr=False),
        dict(need_v=20.0, need_a=5.0, cable='5 A e-marker', emarked=True, epr=False),
        dict(need_v=28.0, need_a=5.0, cable='5 A e-marker（非 EPR）', emarked=True, epr=False),
        dict(need_v=28.0, need_a=5.0, cable='EPR e-marker', emarked=True, epr=True),
        dict(need_v=48.0, need_a=5.0, cable='EPR e-marker', emarked=True, epr=True),
    ]
    for c in cases:
        max_a = 3.0 if not c['emarked'] else 5.0
        max_v = 20.0 if not c['epr'] else 48.0
        c['max_a'] = max_a
        c['max_v'] = max_v
        c['ok'] = c['need_a'] <= max_a and c['need_v'] <= max_v
        c['fallback_v'] = min(c['need_v'], max_v)
        c['fallback_a'] = min(c['need_a'], max_a)
        c['fallback_w'] = round(c['fallback_v'] * c['fallback_a'], 2)
        c['want_w'] = round(c['need_v'] * c['need_a'], 2)
    return dict(cases=cases,
                lost_100w=next(c for c in cases
                               if c['need_a'] == 5.0 and not c['emarked']))


# ---------------------------------------------------------------- 9. loss

def loss() -> dict:
    r_cable = 0.10                   # ohm, both conductors, this model's value
    rows = []
    for watts, v in ((100, 5.0), (100, 9.0), (100, 15.0), (100, 20.0),
                     (100, 28.0), (100, 48.0), (240, 48.0)):
        a = watts / v
        rows.append(dict(watts=watts, v=v, a=round(a, 3),
                         loss_w=round(a * a * r_cable, 3),
                         loss_pct=round(100 * a * a * r_cable / watts, 3),
                         drop_v=round(a * r_cable, 3)))
    return dict(r_cable=r_cable, rows=rows,
                ratio_5v_over_20v=round((100 / 5.0) ** 2 / (100 / 20.0) ** 2, 2))


# ---------------------------------------------------------------- build

def build() -> dict:
    return dict(
        config=dict(rd_ohm=RD, ui_samples=UI_SAMPLES, seed=20261228,
                    ramp_mv_per_ms=100.0, tcc_debounce=0.150,
                    cable_ohm=0.10, pps_step_mv=20, pps_lo=3.3, pps_hi=21.0,
                    crc='reflected CRC-32, poly 0x04C11DB7'),
        cc=cc_detect(), flip=cc_flip(), bmc=bmc(), fourb5b=fourb5b_stats(),
        frame=frame_check(), trace=negotiation(), rules=power_rules(),
        pps=pps(), emarker=emarker(), loss=loss(),
    )


if __name__ == '__main__':
    out = build()
    print(json.dumps(out, indent=1, ensure_ascii=False))
