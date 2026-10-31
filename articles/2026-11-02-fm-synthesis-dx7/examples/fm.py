"""FM / phase-modulation synthesis, measured. Written for the DX7 article.

The point of this file is that every claim in the article can be checked here:
what a phase-modulated sine looks like, how many sidebands a given modulation
index produces, what happens when the ratio is not an integer, and where
digital FM breaks down (aliasing).

No numpy. The FFT is 30 lines of radix-2, so the transform itself is also
inspectable. MIT.
"""
from __future__ import annotations

import cmath
import math

SR = 44100


# --------------------------------------------------------------- waveforms

def pm(fc, fm, index, seconds=0.5, sr=SR, feedback=0.0):
    """Return samples of sin(2π fc t + I sin(2π fm t)).

    `feedback` adds one-sample self-modulation: the previous output sample
    feeds back into the phase, which is how a DX7 operator turns a sine into
    something closer to a sawtooth or noise.
    """
    n = int(seconds * sr)
    out = [0.0] * n
    prev = 0.0
    for i in range(n):
        t = i / sr
        phase = 2 * math.pi * fc * t + index * math.sin(2 * math.pi * fm * t)
        if feedback:
            phase += feedback * prev
        prev = math.sin(phase)
        out[i] = prev
    return out


def am(fc, fm, depth, seconds=0.5, sr=SR):
    """Amplitude modulation, for comparison: x = (1 + depth·sin) · sin."""
    return [(1 + depth * math.sin(2 * math.pi * fm * i / sr))
            * math.sin(2 * math.pi * fc * i / sr)
            for i in range(int(seconds * sr))]


def sine(freq, seconds=0.5, sr=SR):
    return [math.sin(2 * math.pi * freq * i / sr) for i in range(int(seconds * sr))]


# --------------------------------------------------------------------- FFT

def fft(values):
    """Iterative radix-2 FFT. Length must be a power of two."""
    n = len(values)
    assert n & (n - 1) == 0, 'length must be a power of two'
    a = [complex(v) for v in values]
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j |= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    size = 2
    while size <= n:
        half = size // 2
        step = cmath.exp(-2j * math.pi / size)
        for start in range(0, n, size):
            w = 1 + 0j
            for k in range(half):
                u = a[start + k]
                v = a[start + k + half] * w
                a[start + k] = u + v
                a[start + k + half] = u - v
                w *= step
        size *= 2
    return a


def spectrum(samples, sr=SR):
    """Magnitude spectrum of the first 8192 samples, normalised to peak 1."""
    n = 8192
    window = [0.5 - 0.5 * math.cos(2 * math.pi * i / (n - 1)) for i in range(n)]
    chunk = [samples[i] * window[i] for i in range(n)]
    bins = fft(chunk)
    half = bins[:n // 2]
    peak = max(abs(b) for b in half) or 1.0
    return [dict(hz=round(i * sr / n, 1), mag=round(abs(b) / peak, 6))
            for i, b in enumerate(half)]


def peaks(spec, floor_db=-60.0, count=40):
    """Local maxima above `floor_db`, strongest first."""
    out = []
    for i in range(1, len(spec) - 1):
        s = spec[i]
        if s['mag'] <= 0:
            continue
        db = 20 * math.log10(s['mag'])
        if db < floor_db:
            continue
        if s['mag'] >= spec[i - 1]['mag'] and s['mag'] >= spec[i + 1]['mag']:
            out.append(dict(hz=s['hz'], db=round(db, 2), mag=s['mag']))
    out.sort(key=lambda p: -p['mag'])
    return out[:count]


def partial_count(spec, floor_db=-60.0):
    return len(peaks(spec, floor_db=floor_db, count=10 ** 6))


# --------------------------------------------------------------- Bessel J_n

def bessel_j(n, x, steps=20000):
    """J_n(x) = (1/π) ∫_0^π cos(n τ - x sin τ) dτ, Simpson's rule."""
    if n < 0:
        return (-1) ** n * bessel_j(-n, x, steps)
    h = math.pi / steps
    total = 0.0
    for i in range(steps + 1):
        t = i * h
        v = math.cos(n * t - x * math.sin(t))
        weight = 1 if i in (0, steps) else (4 if i % 2 else 2)
        total += weight * v
    return total * h / 3 / math.pi


def sidebands(index, n_max=8):
    rows = []
    for n in range(n_max + 1):
        amp = bessel_j(n, index)
        rows.append(dict(n=n, amp=round(amp, 4),
                         db=round(20 * math.log10(abs(amp)), 2) if abs(amp) > 1e-6 else None))
    return rows


# ------------------------------------------------------------- experiments

# The examples all use one pitch and one modulation frequency, so the
# sidebands land on the harmonic series of 110 Hz: fc = 440 = 4 x 110.
FC = 440.0
FM = 110.0


def index_sweep(indices=(0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0)):
    """How many lines the spectrum has, as the modulation index grows.

    `partials` counts local maxima above -40 dB (carrier plus both sidebands),
    `reach` is the highest one as a multiple of fm. For a 4:1 ratio the
    highest significant sideband sits near n = index + 1.
    """
    rows = []
    for I in indices:
        found = peaks(spectrum(pm(FC, FM, I)), floor_db=-40.0, count=200)
        rows.append(dict(index=I,
                         partials=len(found),
                         reach=int(max(round(p['hz'] / FM) for p in found)),
                         carson=round(2 * (I + 1) * FM, 1)))
    return rows


def bandwidth_check():
    """Measured bandwidth against Carson's rule 2(I+1)·fm, in Hz."""
    rows = []
    for fm in (110.0, 220.0, 440.0):
        for I in (1.0, 2.0, 4.0):
            fc = 1200.0
            spec = spectrum(pm(fc, fm, I, seconds=0.4))
            top = max(p['hz'] for p in peaks(spec, floor_db=-40.0, count=500))
            rows.append(dict(fm=fm, index=I,
                             measured=round(top - fc, 1),
                             carson=round((I + 1) * fm, 1)))
    return rows


def ratio_check():
    """Integer fc/fm gives harmonics of fm; anything else does not."""
    rows = []
    for fm, label in ((110.0, '4 : 1'), (220.0, '2 : 1'),
                      (440.0 / 1.5, '1.5 : 1'), (440.0 / 2 ** 0.5, '1.414 : 1')):
        found = peaks(spectrum(pm(FC, fm, 2.0, seconds=0.4)),
                      floor_db=-45.0, count=12)
        mult = [round(p['hz'] / fm, 2) for p in found]
        integer = all(abs(m - round(m)) < 0.03 for m in mult)
        rows.append(dict(ratio=label, fm=round(fm, 1), partials=len(found),
                         multiples=sorted(mult), harmonic=integer))
    return rows


def aliasing_check(cases=((3000.0, 750.0), (6000.0, 1500.0),
                         (9000.0, 2250.0), (12000.0, 3000.0), (15000.0, 3750.0))):
    """Which sidebands cross Nyquist, and where they come back.

    A partial at f > 22050 Hz does not vanish: it lands at |44100 - f|.
    For each case we work out the highest significant sideband (|J_n| > 0.01),
    then check whether the spectrum really has a line at the folded position.
    """
    rows = []
    index = 4.0
    for fc, fm in cases:
        n_max = 0
        for n in range(1, 40):
            if abs(bessel_j(n, index, 4000)) > 0.01:
                n_max = n
        top = fc + n_max * fm
        row = dict(fc=fc, fm=fm, index=index, n_max=n_max, top=round(top, 1),
                   beyond=top > 22050)
        if row['beyond']:
            alias = abs(SR - top)
            spec = spectrum(pm(fc, fm, index, seconds=0.4))
            near = min(spec, key=lambda s: abs(s['hz'] - alias))
            row['alias_hz'] = round(alias, 1)
            row['found_hz'] = near['hz']
            row['found_db'] = round(20 * math.log10(max(near['mag'], 1e-9)), 1)
        rows.append(row)
    return rows


def feedback_check():
    rows = []
    for beta in (0.0, 0.5, 1.0, 2.0, 3.0):
        spec = spectrum(pm(220.0, 55.0, 0.0, feedback=beta))
        found = peaks(spec, floor_db=-40.0, count=500)
        rows.append(dict(feedback=beta, partials=len(found),
                         top=round(max(p['hz'] for p in found), 1)))
    return rows


def example_spectrum(index=2.0, fc=FC, fm=FM):
    """The spectrum the article draws: peaks only, in dB."""
    return peaks(spectrum(pm(fc, fm, index)), floor_db=-70.0, count=200)


def bessel_curves(step=0.25, x_max=8.0, steps=4000):
    rows = []
    x = 0.0
    while x <= x_max + 1e-9:
        rows.append(dict(x=round(x, 2),
                         j0=round(bessel_j(0, x, steps), 4),
                         j1=round(bessel_j(1, x, steps), 4),
                         j2=round(bessel_j(2, x, steps), 4)))
        x += step
    return rows


def am_spectrum(depth=0.8):
    # same carrier and a modulation frequency that puts both sidebands on
    # the 110 Hz grid, so the two panels of figure 6 can share a scale
    return peaks(spectrum(am(FC, FM, depth)), floor_db=-70.0, count=40)


def envelope(attack=0.01, decay=0.4, sustain=0.5, release=0.6,
             peak=1.0, rate=200.0):
    """A four-stage EG like the DX7's, sampled at `rate` points per second.

    Rates here are the *slopes*, not the stage times: the DX7's own EG is
    rate-based (each of the four stages runs at a rate until it reaches a
    level), which is why the release time depends on where the sustain sits.
    """
    rows = []
    total = attack + decay + 2.0 + release
    n = int(total * rate)
    for i in range(n):
        t = i / rate
        if t < attack:
            v = peak * t / attack
        elif t < attack + decay:
            v = peak + (sustain - peak) * (t - attack) / decay
        elif t < attack + decay + 2.0:
            v = sustain
        else:
            rel = (t - attack - decay - 2.0) / release
            v = sustain * max(0.0, 1 - rel) if rel <= 1 else 0.0
        rows.append(dict(t=round(t, 4), v=round(v, 4)))
    return rows


def measure():
    return dict(
        sr=SR,
        index_sweep=index_sweep(),
        bandwidth=bandwidth_check(),
        ratios=ratio_check(),
        aliasing=aliasing_check(),
        feedback=feedback_check(),
        sidebands=sidebands(2.0),
        sidebands_half=sidebands(0.5),
        fc=FC, fm=FM,
        pure=peaks(spectrum(sine(FC)), floor_db=-70.0, count=20),
        example=example_spectrum(2.0),
        example_low=example_spectrum(0.5),
        example_high=example_spectrum(6.0),
        inharmonic=example_spectrum(2.0, FC, FC / 1.414),
        bessel_curves=bessel_curves(),
        am=am_spectrum(0.8),
        envelope=envelope(),
        bessel_peaks=[dict(x=x, j0=round(bessel_j(0, x), 4),
                           j1=round(bessel_j(1, x), 4),
                           j2=round(bessel_j(2, x), 4))
                      for x in (0.0, 0.5, 1.0, 2.0, 4.0)],
    )


if __name__ == '__main__':
    r = measure()
    print('index -> partials:', [(x['index'], x['partials']) for x in r['index_sweep']])
    print('bandwidth:', [(x['fm'], x['index'], x['measured'], x['carson'])
                         for x in r['bandwidth']])
    print('ratios:', [(x['ratio'], x['harmonic'], x['partials']) for x in r['ratios']])
    print('aliasing:', [(x['fc'], x['top_partial']) for x in r['aliasing']])
    print('feedback:', [(x['feedback'], x['partials'], x['top']) for x in r['feedback']])
    print('J2(2.0)=', bessel_j(2, 2.0), ' expected 0.3528')
