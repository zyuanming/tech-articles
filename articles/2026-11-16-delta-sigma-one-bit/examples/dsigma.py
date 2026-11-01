"""A delta-sigma modulator, sample by sample, plus the decimation maths.

Everything the article claims is produced here: the loop, the one-bit
quantiser, the shaped noise, the SNR, and the stability edge. Standard
library only; MIT.
"""
import math

# ------------------------------------------------------------------ settings
BW = 22050.0          # audio band edge, Hz (Nyquist of 44.1 kHz)
FS0 = 44100.0         # the rate a CD stores
NFFT = 32768          # simulation length, power of two
KBIN = 16             # input tone sits on this bin: 16 * fs / NFFT
DITHER = 1.0          # triangular dither, in units of one LSB of the 1-bit quantiser


# ------------------------------------------------------------------ tiny FFT
def fft(re, im):
    n = len(re)
    assert n & (n - 1) == 0, 'length must be a power of two'
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j |= bit
        if i < j:
            re[i], re[j] = re[j], re[i]
            im[i], im[j] = im[j], im[i]
    length = 2
    while length <= n:
        ang = -2.0 * math.pi / length
        wr, wi = math.cos(ang), math.sin(ang)
        for i in range(0, n, length):
            cr, ci = 1.0, 0.0
            half = length // 2
            for k in range(half):
                ur, ui = re[i + k], im[i + k]
                vr = re[i + k + half] * cr - im[i + k + half] * ci
                vi = re[i + k + half] * ci + im[i + k + half] * cr
                re[i + k], im[i + k] = ur + vr, ui + vi
                re[i + k + half], im[i + k + half] = ur - vr, ui - vi
                cr, ci = cr * wr - ci * wi, cr * wi + ci * wr
        length <<= 1
    return re, im


def spectrum(x):
    n = len(x)
    re = list(x)
    im = [0.0] * n
    fft(re, im)
    return [(re[k] ** 2 + im[k] ** 2) for k in range(n // 2 + 1)]


# ------------------------------------------------------------ the modulator
class Rng:
    """Tiny LCG so the whole article is reproducible to the bit."""

    def __init__(self, seed=12345):
        self.s = seed
        for _ in range(8):
            self.step()

    def step(self):
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s / 2147483648.0

    def tri(self):
        return self.step() - self.step()


def run(order=1, osr=64, amp=0.5, k=KBIN, n=NFFT, dither=DITHER, seed=12345):
    """Simulate one modulator. Returns bits, integrator states, spectrum.

    order 1:  i1 += u - y_prev ;  y = sign(i1 + dither)
    order 2:  i1 += u - y_prev ;  i2 += i1 - y_prev ;  y = sign(i2 + dither)
    """
    fs = FS0 * osr
    f_in = k * fs / n
    w = 2.0 * math.pi * f_in / fs
    rng = Rng(seed)
    bits, states = [], []
    i1 = i2 = 0.0
    for idx in range(n):
        u = amp * math.sin(w * idx)
        y_prev = bits[-1] if bits else 0.0
        d = rng.tri() * dither
        if order == 1:
            i1 = i1 + u - y_prev
            y = 1.0 if i1 + d >= 0 else -1.0
            states.append(i1)
        else:
            i1 = i1 + u - y_prev
            i2 = i2 + i1 - y_prev
            y = 1.0 if i2 + d >= 0 else -1.0
            states.append(i2)
        bits.append(y)
    return dict(fs=fs, f_in=f_in, k=k, n=n, bits=bits, states=states,
                amp=amp, order=order, osr=osr, ps=spectrum(bits))


def snr(sim, guard=3):
    """In-band SNR: signal bin against every other in-band bin, harmonics
    (multiples of the tone) left out so this is noise, not distortion."""
    ps, n = sim['ps'], sim['n']
    k_sig = sim['k']
    band = max(1, int(round(n / (2.0 * sim['osr']))))
    sig = ps[k_sig]
    harm = [h * k_sig for h in range(1, band // k_sig + 1)]
    noise = sum(ps[k] for k in range(1, min(band, len(ps) - 1) + 1)
                if all(abs(k - h) > guard for h in harm))
    noise = max(noise, 1e-30)
    return dict(snr_db=10.0 * math.log10(sig / noise), sig=sig,
                noise=noise, band_bins=band)


def sinad(sim):
    """Same, but harmonics stay in: what a datasheet would call THD+N."""
    ps, n = sim['ps'], sim['n']
    band = max(1, int(round(n / (2.0 * sim['osr']))))
    sig = sim['ps'][sim['k']]
    noise = sum(ps[1:min(band, len(ps) - 1) + 1]) - sig
    return 10.0 * math.log10(sig / max(noise, 1e-30))


def spur(sim, guard=3):
    """Largest in-band tone that is not the signal or one of its harmonics,
    relative to the signal: the "bird chirp" a 1-bit loop sings without dither."""
    ps, n = sim['ps'], sim['n']
    band = max(1, int(round(n / (2.0 * sim['osr']))))
    sig = ps[sim['k']]
    harm = [h * sim['k'] for h in range(1, band // sim['k'] + 1)]
    top = 0.0
    for kb in range(1, min(band, len(ps) - 1) + 1):
        if all(abs(kb - h) > guard for h in harm):
            top = max(top, ps[kb])
    return 10.0 * math.log10(max(top, 1e-30) / max(sig, 1e-30))


def noise_density(sim, slices=48):
    """Average power per bin over log-spaced slices of the spectrum."""
    ps, n = sim['ps'], sim['n']
    half = n // 2
    out = []
    for s in range(slices):
        a = int(half ** (s / float(slices)))
        b = int(half ** ((s + 1) / float(slices)))
        a, b = max(1, a), max(a + 1, b)
        b = min(b, half)
        avg = sum(ps[a:b]) / float(b - a)
        out.append(dict(f=(a + b) / 2.0 * sim['fs'] / n, p=avg))
    return out


def slope_db_per_octave(curve):
    """Fit a straight line to the density curve between the two ends."""
    lo, hi = curve[3], curve[-4]
    return 10.0 * math.log10(hi['p'] / lo['p']) / math.log2(hi['f'] / lo['f'])


# --------------------------------------------------------------- theory side
def sqnr_theory(order=1, osr=64, bits=1):
    """Textbook estimate for a full-scale sine. Noise shaped by (1-z^-1)^order."""
    q = 6.02 * bits + 1.76
    shape = 10.0 * math.log10(math.pi ** (2 * order) / (2 * order + 1))
    gain = 10.0 * (2 * order + 1) * math.log10(osr)
    return q - shape + gain


def ntf_mag(f_norm, order=1):
    """|1 - e^-jw|^order, the noise transfer function, f_norm = f / fs."""
    return abs(1.0 - complex(math.cos(2 * math.pi * f_norm),
                             -math.sin(2 * math.pi * f_norm))) ** order


def ntf_table(order=2, points=16):
    return [dict(f=k / 2.0 / points, mag=ntf_mag(k / 2.0 / points, order))
            for k in range(points + 1)]


def oversample_curve():
    """SNR against oversampling ratio, for 1, 2 and 3 bits of loop order."""
    rows = []
    for osr in (1, 2, 4, 8, 16, 32, 64, 128):
        r = dict(osr=osr, fs=round(FS0 * osr / 1e3, 1))
        for order in (1, 2):
            s = run(order, osr, amp=0.5)
            r['sim%d' % order] = round(snr(s)['snr_db'], 1)
            r['th%d' % order] = round(sqnr_theory(order, osr, 1), 1)
        rows.append(r)
    return rows


def amp_curve():
    """SNR against input level: the second-order loop has a floor, then dies."""
    rows = []
    for amp in (0.01, 0.03, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        s1 = run(1, 64, amp=amp)
        s2 = run(2, 64, amp=amp)
        rows.append(dict(amp=amp, db=round(20 * math.log10(amp), 1),
                         o1=round(snr(s1)['snr_db'], 1),
                         o2=round(snr(s2)['snr_db'], 1),
                         peak2=round(max(abs(v) for v in s2['states']), 2)))
    return rows


def dither_curve():
    """Dither kills the idle tones but costs a little noise."""
    rows = []
    for d in (0.0, 0.25, 0.5, 1.0, 2.0):
        s = run(1, 64, amp=0.5, dither=d)
        rows.append(dict(dither=d, sinad=round(sinad(s), 1),
                         spur=round(spur(s), 1), noise=round(snr(s)['snr_db'], 1)))
    return rows


def dc_idle():
    """A silent input: the first-order loop still toggles, a duty cycle."""
    out = []
    for order in (1, 2):
        bits, i1, i2 = [], 0.0, 0.0
        for _ in range(4096):
            y_prev = bits[-1] if bits else 0.0
            if order == 1:
                i1 = i1 - y_prev
                y = 1.0 if i1 >= 0 else -1.0
            else:
                i1 = i1 - y_prev
                i2 = i2 + i1 - y_prev
                y = 1.0 if i2 >= 0 else -1.0
            bits.append(y)
        ones = sum(1 for b in bits if b > 0)
        out.append(dict(order=order, duty=round(ones / 4096.0, 4),
                        pattern=''.join('1' if b > 0 else '0' for b in bits[:32])))
    return out


def bit_budget():
    return [
        dict(name='CD 原始 PCM', rate=44100 * 16, note='16 bit，单声道'),
        dict(name='1 bit，OSR 64', rate=44100 * 64, note='2.8224 Mbit/s'),
        dict(name='DSD64', rate=44100 * 64, note='同一串 0/1，换了个名字'),
        dict(name='1 bit，OSR 128', rate=44100 * 128, note='DSD128'),
        dict(name='4 bit，OSR 64', rate=44100 * 64 * 4, note='多级调制器'),
    ]


def decimation_stages(osr=64):
    """A three-stage chain: what comes out of each stage."""
    return [
        dict(stage=1, kind='CIC / sinc³', factor=8, rate=osr * FS0 / 8,
             width=4, taps=24),
        dict(stage=2, kind='半带 FIR', factor=4, rate=osr * FS0 / 32,
             width=12, taps=31),
        dict(stage=3, kind='半带 FIR', factor=2, rate=FS0, width=16, taps=63),
    ]


def tracking(order=1, amp=0.85, samples=40, osr=8):
    """The first few samples of a slow ramp: what the loop actually does."""
    fs = FS0 * osr
    w = 2.0 * math.pi * (1.0 * fs / NFFT) / fs
    rng = Rng(7)
    bits, states, ins = [], [], []
    i1 = i2 = 0.0
    for idx in range(samples):
        u = amp * math.sin(w * idx * 200)
        ins.append(u)
        y_prev = bits[-1] if bits else 0.0
        d = rng.tri() * 0.0
        if order == 1:
            i1 = i1 + u - y_prev
            y = 1.0 if i1 + d >= 0 else -1.0
            states.append(i1)
        else:
            i1 = i1 + u - y_prev
            i2 = i2 + i1 - y_prev
            y = 1.0 if i2 + d >= 0 else -1.0
            states.append(i2)
        bits.append(y)
    # running average of the bit stream: the "reconstructed" signal
    acc, avg = 0.0, []
    for idx, b in enumerate(bits):
        acc += b
        avg.append(acc / (idx + 1))
    return dict(inp=[round(v, 3) for v in ins],
                state=[round(v, 3) for v in states],
                bits=[int(b > 0) for b in bits],
                runavg=[round(v, 3) for v in avg])


def quantiser_steps(bits=1, samples=25):
    """Staircase of a mid-rise quantiser on +/-1.2 full scale."""
    if bits == 1:                      # two levels, output +/-1
        step, top = 2.0, 1.0
    else:                              # mid-rise, 2**bits levels inside +/-1
        step = 2.0 / 2 ** bits
        top = (2 ** bits - 1) * step / 2.0
    out = []
    for i in range(samples):
        x = -1.2 + 2.4 * i / (samples - 1)
        y = (math.floor(x / step) + 0.5) * step
        y = max(-top, min(top, y))
        out.append(dict(x=round(x, 4), y=round(y, 4)))
    return out


def sqnr_bits():
    """The plain PCM line: SNR against word length, and where 1 bit sits."""
    return [dict(bits=b, snr=round(6.02 * b + 1.76, 1)) for b in
            (1, 2, 4, 8, 12, 16, 20, 24)]


def dc_tone(amp=0.001, dither=0.0, n=8192):
    """Constant input: a first-order loop locks onto one in-band tone."""
    osr = 64
    bits, i1 = [], 0.0
    rng = Rng(99)
    for _ in range(n):
        y_prev = bits[-1] if bits else 0.0
        i1 = i1 + amp - y_prev
        bits.append(1.0 if i1 + rng.tri() * dither >= 0 else -1.0)
    ps = spectrum(bits)
    band = int(n / (2.0 * osr))
    peak = max(range(2, band), key=lambda kb: ps[kb])
    return dict(amp=amp, dither=dither, f_hz=round(peak * FS0 * osr / n, 1),
                level_db=round(10 * math.log10(max(ps[peak], 1e-30) / n ** 2), 1))


def dc_tone_scan():
    rows = []
    for amp in (0.0005, 0.001, 0.005, 0.01):
        for d in (0.0, 1.0):
            rows.append(dc_tone(amp, d))
    return rows


def dc_spectrum(amp=0.001, dither=0.0, n=8192, osr=64, points=120):
    """In-band spectrum of a silent-ish input, as (f, dB) with 0 dB = a full
    scale square wave (power 1)."""
    bits, i1 = [], 0.0
    rng = Rng(99)
    for _ in range(n):
        y_prev = bits[-1] if bits else 0.0
        i1 = i1 + amp - y_prev
        bits.append(1.0 if i1 + rng.tri() * dither >= 0 else -1.0)
    ps = spectrum(bits)
    band = int(n / (2.0 * osr))
    step = max(1, band // points)
    out = []
    for kb in range(2, band, step):
        out.append((round(kb * FS0 * osr / n, 1),
                    round(10 * math.log10(max(ps[kb], 1e-30) / n ** 2), 1)))
    return out


def spec_env(kind, points=110, n=32768):
    """Log-spaced envelope of the output spectrum: max bin per slice, in dB
    with 0 dB = a full-scale square wave (power 1). Returns (curve, sig_db)."""
    if kind == 'pcm16':
        fs = FS0
        w = 2 * math.pi * 5 / n
        step = 2.0 / 2 ** 16
        rng = Rng(31)
        q = []
        for i in range(n):
            v = 0.5 * math.sin(w * i)
            q.append(round((v + step * rng.tri()) / step) * step)
        ps = spectrum(q)
    elif kind == 'onebit_raw':
        fs = FS0
        w = 2 * math.pi * 5 / n
        ps = spectrum([0.5 * math.sin(w * i) for i in range(n)])
        ps = spectrum([1.0 if 0.5 * math.sin(w * i) >= 0 else -1.0
                       for i in range(n)])
    else:
        order = 1 if kind == 'o1' else 2
        sim = run(order, 64, amp=0.5, n=n, dither=1.0)
        fs, ps = sim['fs'], sim['ps']
    f_lo, f_hi = 20.0, fs / 2.0
    curve = []
    for s_i in range(points):
        a = f_lo * (f_hi / f_lo) ** (s_i / float(points))
        b = f_lo * (f_hi / f_lo) ** ((s_i + 1) / float(points))
        ka = max(1, int(a * n / fs))
        kb = max(ka + 1, int(b * n / fs))
        kb = min(kb, n // 2)
        best = max(ps[ka:kb + 1])
        curve.append((round((a + b) / 2.0, 1),
                      round(10 * math.log10(max(best, 1e-30) / n ** 2), 1)))
    sig_bin = 16 if kind in ('o1', 'o2') else (5 if kind != 'pcm16' else 5)
    sig_db = round(10 * math.log10(max(ps[sig_bin], 1e-30) / n ** 2), 1)
    return curve, sig_db


def spectra(points=110):
    out = {}
    for kind in ('pcm16', 'onebit_raw', 'o1', 'o2'):
        curve, sig = spec_env(kind, points)
        out[kind] = dict(curve=curve, sig_db=sig)
    return out


def build():
    o1 = run(1, 64, amp=0.5)
    o2 = run(2, 64, amp=0.5)
    d1 = noise_density(o1)
    d2 = noise_density(o2)
    return dict(
        bw=BW, fs0=FS0, nfft=NFFT, kbin=KBIN, dither=DITHER,
        theory=dict(o1=round(sqnr_theory(1, 64, 1), 2),
                    o2=round(sqnr_theory(2, 64, 1), 2),
                    pcm16=round(sqnr_theory(0, 1, 16), 2)),
        sim=dict(o1=round(snr(o1)['snr_db'], 2),
                 o2=round(snr(o2)['snr_db'], 2),
                 o1_sinad=round(sinad(o1), 2),
                 o2_sinad=round(sinad(o2), 2),
                 band_bins=snr(o1)['band_bins']),
        slope=dict(o1=round(slope_db_per_octave(d1), 1),
                   o2=round(slope_db_per_octave(d2), 1)),
        density1=d1, density2=d2,
        ntf1=ntf_table(1), ntf2=ntf_table(2), ntf3=ntf_table(3),
        oversample=oversample_curve(),
        amp=amp_curve(),
        dither_scan=dither_curve(),
        idle=dc_idle(),
        bits=bit_budget(),
        decimation=decimation_stages(),
        tracking=tracking(),
        quant=dict(one=quantiser_steps(1, 9), three=quantiser_steps(3, 9)),
        pcm=sqnr_bits(),
        quant_noise=round(4.0 / 12.0, 4),
        dc_tones=dc_tone_scan(),
        dc_spec=[dc_spectrum(0.001, 0.0), dc_spectrum(0.001, 1.0)],
        first_bits=[int(b > 0) for b in o1['bits'][:48]],
        first_states=[round(v, 3) for v in o1['states'][:48]],
    )
