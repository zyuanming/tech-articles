"""Audio fingerprinting, from waveform to offset histogram. Standard library only. MIT.

The model is deliberately small: 4 kHz sample rate, 512-point FFT, three
synthetic songs. Everything the article prints comes out of here.
"""
from __future__ import annotations

import cmath
import math

SR = 4000                 # sample rate (Hz). Real systems use 8 kHz or 44.1 kHz.
FRAME = 512               # FFT window
HOP = 128                 # window step -> 31.25 frames per second
FPS = SR / HOP
BINS = FRAME // 2         # 0 .. 2000 Hz in 7.8 Hz steps
DUR = 8.0                 # seconds per song
NOTE = 0.25               # seconds per note

# ---------------------------------------------------------------- synthesis


def lcg(seed: int):
    state = seed & 0xFFFFFFFF

    def nxt():
        nonlocal state
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        return state / 0x7FFFFFFF
    return nxt


SCALE = [0, 2, 3, 5, 7, 8, 10, 12]      # minor pentatonic-ish, in semitones
BASE = 220.0


def song(seed: int, dur: float = DUR, sr: int = SR):
    """A melody: one note per 0.25 s, three harmonics, plucked envelope."""
    rnd = lcg(seed)
    out = [0.0] * int(dur * sr)
    notes = []
    t0 = 0.0
    while t0 < dur - 1e-9:
        step = SCALE[int(rnd() * len(SCALE)) % len(SCALE)]
        f0 = BASE * 2 ** (step / 12.0)
        notes.append(round(f0, 2))
        n = int(min(NOTE, dur - t0) * sr)
        start = int(t0 * sr)
        for i in range(n):
            t = i / sr
            env = math.exp(-6.0 * t) * (1 - math.exp(-300.0 * t))
            v = 0.0
            for h, amp in ((1, 1.0), (2, 0.45), (3, 0.22)):
                v += amp * math.sin(2 * math.pi * f0 * h * t)
            out[start + i] += 0.22 * env * v
        t0 += NOTE
    return out, notes


def noise(sig, snr_db: float, seed: int = 7):
    rnd = lcg(seed)
    power = sum(v * v for v in sig) / max(1, len(sig))
    npow = power / (10 ** (snr_db / 10.0))
    sigma = math.sqrt(npow)
    return [v + sigma * (rnd() * 2 - 1) for v in sig]


def stretch(sig, factor: float):
    """Resample by `factor` (1.01 = 1% longer). Linear interpolation."""
    n = int(len(sig) / factor)
    out = []
    for i in range(n):
        pos = i * factor
        j = int(pos)
        frac = pos - j
        if j + 1 >= len(sig):
            out.append(sig[-1])
        else:
            out.append(sig[j] * (1 - frac) + sig[j + 1] * frac)
    return out


# ---------------------------------------------------------------- analysis


def hann(n):
    return [0.5 - 0.5 * math.cos(2 * math.pi * i / (n - 1)) for i in range(n)]


WINDOW = hann(FRAME)


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


def spectrogram(sig, frame=FRAME, hop=HOP):
    """Magnitude spectrogram in dB. Returns (frames, bins)."""
    rows = []
    for start in range(0, len(sig) - frame + 1, hop):
        chunk = sig[start:start + frame]
        spec = fft([chunk[k] * WINDOW[k] for k in range(frame)])
        rows.append([20 * math.log10(abs(spec[k]) + 1e-9) for k in range(BINS)])
    return rows


def pick_peaks(spec, nbr_t=3, nbr_f=3, max_peaks=140):
    """Local maxima in a time-frequency neighbourhood, kept strongest first."""
    nf, nb = len(spec), len(spec[0])
    flat = [v for row in spec for v in row]
    floor = sorted(flat)[int(0.72 * len(flat))]
    cands = []
    for t in range(nf):
        for f in range(nb):
            v = spec[t][f]
            if v < floor:
                continue
            ok = True
            for dt in range(-nbr_t, nbr_t + 1):
                tt = t + dt
                if tt < 0 or tt >= nf:
                    continue
                for df in range(-nbr_f, nbr_f + 1):
                    ff = f + df
                    if ff < 0 or ff >= nb or (dt == 0 and df == 0):
                        continue
                    if spec[tt][ff] > v:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                cands.append((v, t, f))
    cands.sort(reverse=True)
    chosen = []
    for v, t, f in cands:                     # keep peaks that are not too close
        if all(abs(t - t2) > nbr_t or abs(f - f2) > nbr_f for _v2, t2, f2 in chosen):
            chosen.append((v, t, f))
        if len(chosen) >= max_peaks:
            break
    chosen.sort(key=lambda p: (p[1], p[2]))
    return [(t, f) for _v, t, f in chosen]


def hashes(peaks, fan=5, dt_min=1, dt_max=63, df_max=64):
    """Combinatorial hashing: each anchor pairs with a few later peaks."""
    out = []
    peaks = sorted(peaks)
    for i, (t1, f1) in enumerate(peaks):
        taken = 0
        for t2, f2 in peaks[i + 1:]:
            dt = t2 - t1
            if dt > dt_max:
                break
            if dt < dt_min or abs(f2 - f1) > df_max:
                continue
            out.append(((f1, f2, dt), t1))
            taken += 1
            if taken >= fan:
                break
    return out


class Database:
    def __init__(self):
        self.table = {}

    def add(self, song_id, pairs):
        for key, t1 in pairs:
            self.table.setdefault(key, []).append((song_id, t1))

    def votes(self, pairs, offset):
        """Vote per (song, database time - query time - offset)."""
        tally = {}
        for key, t1 in pairs:
            for song_id, t_db in self.table.get(key, ()):
                slot = (song_id, t_db - t1 - offset)
                tally[slot] = tally.get(slot, 0) + 1
        return tally

    def best(self, pairs):
        tally = self.votes(pairs, 0)
        if not tally:
            return None, 0, {}
        (song_id, _shift), count = max(tally.items(), key=lambda kv: kv[1])
        return song_id, count, tally


# ---------------------------------------------------------------- experiments


def identify(db, sig, snr_db, factor=1.0, offset_frames=94, clip_frames=94,
             max_peaks=140):
    """Query a clip. `offset_frames` must be a whole number of analysis hops,
    otherwise the true alignment falls between two offset bins and the votes
    split in half."""
    start = offset_frames * HOP
    clip = sig[start:start + clip_frames * HOP]
    if factor != 1.0:
        clip = stretch(clip, factor)
    spec = spectrogram(noise(clip, snr_db))
    peaks = pick_peaks(spec, max_peaks=max_peaks)
    pairs = hashes(peaks)
    song_id, count, tally = db.best(pairs)
    return dict(peaks=len(peaks), hashes=len(pairs), song=song_id,
                votes=count, tally=tally, spec=spec)


def correlation(a, b, lag):
    """Normalised cross-correlation of two signals at one lag."""
    n = min(len(a), len(b) - lag)
    if n <= 0:
        return 0.0
    num = sum(a[i] * b[i + lag] for i in range(n))
    ea = math.sqrt(sum(a[i] * a[i] for i in range(n)))
    eb = math.sqrt(sum(b[i + lag] ** 2 for i in range(n)))
    return num / (ea * eb + 1e-12)
