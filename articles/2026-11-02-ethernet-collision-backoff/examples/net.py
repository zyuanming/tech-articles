"""Shared-wire Ethernet: ALOHA, slotted ALOHA, and binary exponential backoff.

Every number in the article comes out of this file. The models are small on
purpose, and each one is stated in its docstring so a reader can check the
assumptions rather than take the picture's word for it.

* `aloha_pure` / `aloha_slotted` follow the textbook models exactly: Poisson
  arrivals, frames of unit length, a collision kills every frame involved.
  The measured throughput can therefore be compared against `G·e^(-2G)` and
  `G·e^(-G)`.
* `contention` is the backoff experiment: n stations all want the wire, each
  draws a retry slot from a window, and the one with the smallest unique draw
  wins. Window policy is the parameter (binary exponential / fixed).
* `efficiency` is arithmetic on top of the measured collision counts. It is a
  model, not a measurement, and the article says so.

MIT.
"""
from __future__ import annotations

import math
import random

FRAME_BITS = 8 * 1500          # a full-size Ethernet frame, for timing maths
SLOT_BITS = 512                # 802.3 slot time
MIN_FRAME_BYTES = 64
MAX_FRAME_BYTES = 1518
PREAMBLE_BYTES = 8
HEADER_BYTES = 14
FCS_BYTES = 4
MIN_PAYLOAD = 46
MAX_PAYLOAD = 1500


# ------------------------------------------------------------ ALOHA, measured

def aloha_pure(g, hours=40000.0, seed=1):
    """Unsynchronised ALOHA: a frame starts the instant it is ready.

    Frames last one time unit. A frame succeeds only if no other frame starts
    within one unit of it — the famous two-frame vulnerable window.
    """
    rng = random.Random(seed)
    starts = []
    t = 0.0
    while True:
        t += rng.expovariate(g)
        if t > hours:
            break
        starts.append(t)
    good = 0.0
    for i, s in enumerate(starts):
        if i and s - starts[i - 1] < 1.0:
            continue
        if i + 1 < len(starts) and starts[i + 1] - s < 1.0:
            continue
        good += 1.0
    return dict(g=round(g, 3), measured=round(good / hours, 4),
                theory=round(g * math.exp(-2 * g), 4))


def aloha_slotted(g, slots=20000, seed=2):
    """Slotted ALOHA: every frame must start on a slot boundary."""
    rng = random.Random(seed)
    good = 0
    for _ in range(slots):
        limit = math.exp(-g)
        prod = 1.0
        k = 0
        while True:
            prod *= rng.random()
            if prod <= limit:
                break
            k += 1
        if k == 1:
            good += 1
    return dict(g=round(g, 3), measured=round(good / slots, 4),
                theory=round(g * math.exp(-g), 4))


# ------------------------------------------------------- backoff, measured

def _window(kind, k, n, cap=10):
    if kind == 'binary':
        return 2 ** min(k, cap)
    if kind == 'fixed2':
        return 2
    return n                                  # 'fixedn': the crowd size


def contention(n, kind='binary', trials=3000, cap=16, seed=100):
    """How many collisions before one station gets the wire alone?

    Every station has a frame ready. A round is one attempt: each station
    draws a slot number from the current window; if exactly one station drew
    the smallest number, it transmits and the rest wait for the next round.
    Otherwise everyone involved tries again with a larger window.
    """
    rng = random.Random(seed)
    total = 0
    worst = 0
    for _ in range(trials):
        k = 0
        while k < cap:
            w = _window(kind, k, n)
            draws = [rng.randint(0, w - 1) for _ in range(n)]
            low = min(draws)
            if draws.count(low) == 1:
                break
            k += 1
        total += k
        worst = max(worst, k)
    return dict(stations=n, kind=kind, mean=round(total / trials, 3), worst=worst)


# -------------------------------------------------- efficiency, arithmetic

def efficiency(collisions, collision_cost):
    """Share of the wire that carries good frames.

    One frame of payload needs `1 + collisions * collision_cost` frame times:
    the frame itself, plus the wasted time of every collision that had to be
    resolved first.
    """
    return round(1.0 / (1.0 + collisions * collision_cost), 4)


# -------------------------------------------------------------- frame maths

def speed_table(speeds=(10, 100, 1000, 10000)):
    """Slot time, and how far a signal can travel before the slot runs out.

    The 802.3 slot time is 512 bit times *by definition*, so it shrinks as the
    clock speeds up. Copper does not get faster. The last column is the span
    that keeps a minimum-size frame legal: `slot * v / 2`, with v = 2e8 m/s.
    The real standards are shorter than this budget, because repeaters and
    transceivers eat into it.
    """
    rows = []
    for mbps in speeds:
        bps = mbps * 1e6
        slot = SLOT_BITS / bps * 1e6
        rows.append(dict(mbps=mbps, slot_us=round(slot, 3),
                         span_m=round(slot * 1e-6 * 2e8 / 2)))
    return rows


def reach(meters, speed=2.0e8):
    """Round trip along a bus, in microseconds."""
    return round(2 * meters / speed * 1e6, 2)


def overhead_table(sizes=(46, 64, 128, 256, 512, 1024, 1500)):
    rows = []
    for payload in sizes:
        frame = PREAMBLE_BYTES + HEADER_BYTES + payload + FCS_BYTES
        rows.append(dict(payload=payload, frame=frame,
                         efficiency=round(payload / frame, 4)))
    return rows


def backoff_windows(cap=10, slot_us=51.2):
    rows = []
    for k in range(0, cap + 1):
        w = 2 ** k
        rows.append(dict(k=k, window=w,
                         worst_ms=round(w * slot_us / 1000.0, 2)))
    return rows


# ------------------------------------------------------------------ gather

def measure():
    loads = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2, 1.5, 1.8]
    pure = [aloha_pure(g, hours=30000.0, seed=11) for g in loads]
    slotted = [aloha_slotted(g, slots=6000, seed=12) for g in loads]

    backoff = []
    for n in (2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64):
        backoff.append(contention(n, 'binary', trials=1500, seed=200 + n))
    controls = []
    for n in (2, 4, 8, 16, 32, 64):
        controls.append(contention(n, 'fixed2', trials=300, cap=12, seed=300 + n))
        controls.append(contention(n, 'fixedn', trials=1500, seed=400 + n))

    # The two levers, on the same measured collision count.
    c_frame = [b for b in backoff if b['stations'] == 32][0]['mean']
    levers = [
        dict(name='ALOHA', collisions=c_frame, cost=1.0,
             efficiency=efficiency(c_frame, 1.0)),
        dict(name='CSMA/CD', collisions=c_frame, cost=0.05,
             efficiency=efficiency(c_frame, 0.05)),
    ]

    return dict(
        aloha=pure, slotted=slotted, backoff=backoff, controls=controls,
        levers=levers, ceiling=dict(aloha=round(1 / (2 * math.e), 4),
                                    slotted=round(1 / math.e, 4)),
        speeds=speed_table(), reach=dict(m500=reach(500), m2500=reach(2500)),
        overhead=overhead_table(), windows=backoff_windows(),
        frame=dict(min_bytes=MIN_FRAME_BYTES, max_bytes=MAX_FRAME_BYTES,
                   preamble=PREAMBLE_BYTES, header=HEADER_BYTES,
                   fcs=FCS_BYTES, min_payload=MIN_PAYLOAD,
                   max_payload=MAX_PAYLOAD),
    )


if __name__ == '__main__':
    import json
    r = measure()
    for key in ('ceiling', 'levers', 'reach'):
        print(key, json.dumps(r[key], ensure_ascii=False))
    print('backoff', [(b['stations'], b['mean']) for b in r['backoff']])
    print('speeds', [(r['mbps'], r['slot_us'], r['span_m']) for r in r['speeds']])
    print('controls', [(c['stations'], c['kind'], c['mean']) for c in r['controls']])
