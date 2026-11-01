"""What the magic constant 0x5f3759df actually does, in plain IEEE-754 bits.

The Quake III routine is three lines of C. This module rebuilds it in Python
with real float32 rounding at every step, so the numbers printed here are the
numbers the 1999 code produced on x86 (modulo x87 80-bit temporaries, which
the model does not emulate). Standard library only, MIT.
"""
import math
import struct

MAGIC = 0x5F3759DF          # as shipped in q_math.c
MAGIC_LOMONT = 0x5F375A86   # Chris Lomont's 2003 search result
MAGIC_RYS = 0x5F375A86      # Rys Sommerville's independent answer
MAGIC_OFF = 0x5F37642F      # a common "close but worse" value
SIGMA = 0.0450465           # the offset the derivation wants


# ---------------------------------------------------------------- float32 bits
def f32(x):
    """Round a Python float to the nearest float32, like a C `float` store."""
    return struct.unpack('<f', struct.pack('<f', x))[0]


def bits(x):
    return struct.unpack('<I', struct.pack('<f', f32(x)))[0]


def from_bits(i):
    return struct.unpack('<f', struct.pack('<I', i & 0xFFFFFFFF))[0]


def bitstring(i, n=32):
    s = format(i & 0xFFFFFFFF, '032b')
    return s[:1], s[1:9], s[9:9 + n - 9]


# ---------------------------------------------------------------- the routine
def fast_inv_sqrt(x, iters=1, magic=MAGIC):
    """Exactly the shipped sequence: shift, subtract, Newton, Newton."""
    y = from_bits(magic - (bits(x) >> 1))
    for _ in range(iters):
        y = f32(y * f32(1.5 - f32(f32(0.5 * x) * f32(y * y))))
    return y


def exact_inv_sqrt(x):
    return 1.0 / math.sqrt(x)


def rel_err(x, y):
    return abs(y - exact_inv_sqrt(x)) / exact_inv_sqrt(x)


# ---------------------------------------------------------------- log2 model
def log2_float_bits(x):
    """log2(x) recovered from the bit pattern, with no fitting at all."""
    return bits(x) / 2.0 ** 23 - 127.0


def log2_true(x):
    return math.log2(x)


def log2_fit(x, sigma=SIGMA):
    """Same thing with one constant added: the straight line through log2(1+m)."""
    return bits(x) / 2.0 ** 23 - 127.0 + sigma


def fit_error_by_mantissa(n=64):
    """How badly log2(1+m) is approximated by m, over the whole mantissa."""
    rows = []
    for k in range(n):
        m = k / (n - 1.0)
        rows.append(dict(m=round(m, 4),
                         true=round(math.log2(1 + m), 6),
                         lin=round(m, 6),
                         diff=round(math.log2(1 + m) - m, 6)))
    return rows


# ---------------------------------------------------------------- magic constant
def magic_from_sigma(sigma=SIGMA):
    """The derivation: solve for the integer that makes the two log2 forms agree.

    A = 3/2 * 2^23, and the answer is A * (127 - sigma) truncated, not rounded.
    """
    return int(1.5 * 2.0 ** 23 * (127.0 - sigma))


def sigma_of(magic):
    """The reverse: which offset does a given magic constant imply?"""
    a = 1.5 * 2.0 ** 23
    return round((a * 127.0 - magic) / a, 7)


def magic_local_search(span=300, n=600):
    """Search the integers either side of the shipped constant.

    This is Lomont's 2003 experiment in miniature: minimise the error *after*
    one Newton step, not the error of the raw bit trick.
    """
    best = None
    for m in range(MAGIC - span, MAGIC + span + 1):
        e = max_err(iters=1, magic=m, n=n)
        if best is None or e < best['err']:
            best = dict(magic='0x%08x' % m, delta=m - MAGIC, err=round(e, 8),
                        sigma=sigma_of(m))
    return best


# ---------------------------------------------------------------- error scans
def scan(n=400, lo=0.01, hi=100.0, iters=1, magic=MAGIC):
    out = []
    for k in range(n):
        x = lo * (hi / lo) ** (k / (n - 1.0))
        out.append((x, rel_err(x, fast_inv_sqrt(x, iters, magic))))
    return out


def max_err(iters=1, magic=MAGIC, n=2000, lo=0.01, hi=100.0):
    """Worst relative error over 14+ octaves -- the number people quote."""
    worst = 0.0
    for k in range(n):
        x = lo * (hi / lo) ** (k / (n - 1.0))
        worst = max(worst, rel_err(x, fast_inv_sqrt(x, iters, magic)))
    return worst


def worst_at(x, iters=1, magic=MAGIC):
    """Worst error across the mantissa for one exponent: the peak of the saw."""
    worst = (0.0, x)
    for k in range(400):
        xx = x * (2.0 ** (k / 400.0))
        e = rel_err(xx, fast_inv_sqrt(xx, iters, magic))
        if e > worst[0]:
            worst = (e, xx)
    return dict(err=round(worst[0], 8), at=round(worst[1], 6))


def error_heat(nexp=14, nmant=48, iters=1, magic=MAGIC):
    """Relative error on an (exponent, mantissa) grid -- the map of the saw."""
    rows = []
    for e in range(nexp):
        x0 = 2.0 ** (e - 7)
        row = []
        for k in range(nmant):
            x = x0 * (1 + k / (nmant - 1.0))
            row.append(round(rel_err(x, fast_inv_sqrt(x, iters, magic)) * 100, 3))
        rows.append(dict(x0=round(x0, 6), err_pct=row))
    return rows


# ---------------------------------------------------------------- worked notes
def steps(x):
    """The three steps for one input, with the intermediate bit patterns."""
    b = bits(x)
    half = b >> 1
    approx = (MAGIC - half) & 0xFFFFFFFF
    y0 = from_bits(approx)
    y1 = f32(y0 * f32(1.5 - f32(f32(0.5 * x) * f32(y0 * y0))))
    y2 = f32(y1 * f32(1.5 - f32(f32(0.5 * x) * f32(y1 * y1))))
    return dict(x=x, bits=format(b, '08x'), halves=format(half, '08x'),
                approx=format(approx, '08x'), y0=y0, y1=y1, y2=y2,
                exact=exact_inv_sqrt(x))


def examples():
    xs = [4.0, 0.25, 9.0, 100.0, 2.0, 1000000.0]
    return [steps(x) for x in xs]


def table():
    rows = []
    for m, name in ((MAGIC, '原版 0x5f3759df'),
                    (MAGIC_LOMONT, 'Lomont 2003'),
                    (MAGIC_OFF, '按 log2 拟合')):
        rows.append(dict(name=name, magic='0x%08x' % m, sigma=sigma_of(m),
                         e0=round(max_err(0, m), 6),
                         e1=round(max_err(1, m), 8),
                         e2=round(max_err(2, m), 10)))
    return rows


def iteration_threshold():
    """How many Newton steps before the error drops under a visible threshold."""
    out = []
    for iters in (0, 1, 2, 3):
        out.append(dict(iters=iters, max_rel_err=max_err(iters)))
    return out


def op_count():
    """Instructions in the fast path, versus a textbook sqrt-then-divide."""
    return dict(
        fast=dict(shift=1, subtract=1, mul=4, sub=2, total=8),
        textbook=dict(shift=0, subtract=0, mul=0, sub=0, total=2),
        note='教科书路线只有两条指令，但 sqrt 与 div 是微码，延迟几十个周期',
    )


def payload(normals=2500000, ns_fast=1.2, ns_sqrt_div=22.0):
    """A frame's worth of normalisations, at two per-normal cost estimates."""
    t_fast = normals * ns_fast / 1e9
    t_slow = normals * ns_sqrt_div / 1e9
    return dict(normals=normals, ns_fast=ns_fast, ns_sqrt_div=ns_sqrt_div,
                ms_fast=round(t_fast * 1e3, 1), ms_slow=round(t_slow * 1e3, 1),
                ratio=round(t_slow / t_fast, 1))


def build():
    return dict(
        magic=hex(MAGIC), magic_dec=MAGIC, sigma=SIGMA,
        magic_from_sigma=magic_from_sigma(),
        magic_from_sigma_hex=hex(magic_from_sigma()),
        bit_layout=dict(sign=1, exp=8, mantissa=23, bias=127),
        one_bit=steps(1.0),
        examples=examples(),
        max_err=iteration_threshold(),
        sweep=magic_local_search(),
        sigma_shipped=sigma_of(MAGIC),
        table=table(),
        ops=op_count(),
        payload=payload(),
        fit=fit_error_by_mantissa(),
        worst=dict(e0=worst_at(1.0, 0), e1=worst_at(1.0, 1), e2=worst_at(1.0, 2)),
        scan=dict(
            e0=[(round(x, 6), round(e, 6)) for x, e in scan(240, iters=0)],
            e1=[(round(x, 6), round(e, 8)) for x, e in scan(240, iters=1)],
            e2=[(round(x, 6), round(e, 10)) for x, e in scan(240, iters=2)],
        ),
        heat=error_heat(nmant=48, iters=1),
        heat0=error_heat(nmant=48, iters=0),
    )
