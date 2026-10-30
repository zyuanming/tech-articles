"""Everything this article claims about binary64, computed rather than asserted.

Only the Python standard library is used. Nothing here trusts a printed decimal
string: the bit patterns come from `struct`, the exact differences come from
`fractions.Fraction`, and the long divisions are carried out by hand.
"""
from __future__ import annotations

import math
import struct
from fractions import Fraction

SIGN_BITS = 1
EXP_BITS = 11
FRAC_BITS = 52
BIAS = 1023


# --------------------------------------------------------------- bit patterns
def bits(x: float) -> int:
    """The 64 bits of a float64, as one integer."""
    return struct.unpack('<Q', struct.pack('<d', x))[0]


def bitstring(x: float) -> str:
    """'0 01111111011 1001100110011001100110011001100110011001100110011010'."""
    b = bits(x)
    s = format(b >> (EXP_BITS + FRAC_BITS), '01b')
    e = format((b >> FRAC_BITS) & ((1 << EXP_BITS) - 1), '0%db' % EXP_BITS)
    f = format(b & ((1 << FRAC_BITS) - 1), '0%db' % FRAC_BITS)
    return '%s %s %s' % (s, e, f)


def from_bits(b: int) -> float:
    return struct.unpack('<d', struct.pack('<Q', b))[0]


def decode(x: float) -> dict:
    """Split a float64 into the three fields IEEE 754 actually stores."""
    b = bits(x)
    sign = b >> 63
    raw_exp = (b >> FRAC_BITS) & ((1 << EXP_BITS) - 1)
    frac = b & ((1 << FRAC_BITS) - 1)
    if raw_exp == 0:
        kind = 'subnormal' if frac else 'zero'
        significand = Fraction(frac, 1 << FRAC_BITS)
        exponent = 1 - BIAS
    elif raw_exp == (1 << EXP_BITS) - 1:
        kind = 'nan' if frac else 'infinity'
        significand = Fraction(0)
        exponent = 0
    else:
        kind = 'normal'
        significand = Fraction((1 << FRAC_BITS) + frac, 1 << FRAC_BITS)
        exponent = raw_exp - BIAS
    return dict(bits=b, bitstr=bitstring(x), hex='0x%016X' % b,
                sign=sign, raw_exponent=raw_exp,
                exponent=exponent, fraction=frac, kind=kind,
                significand=significand,
                exact=Fraction(-1) ** sign * significand * Fraction(2) ** exponent)


def exact(x: float) -> Fraction:
    """The exact rational value of the float. 0.1 is *not* 1/10."""
    return decode(x)['exact']


# ------------------------------------------------------- binary long division
def long_division(numerator: int, denominator: int, max_digits: int = 80) -> dict:
    """Binary expansion of numerator/denominator by repeated doubling.

    Returns the integer part, the digits, and the first repeated state so the
    caller can say where the cycle begins and how long it is.
    """
    whole, rem = divmod(numerator, denominator)
    digits, seen, cycle_at, period = [], {}, None, None
    while len(digits) < max_digits:
        if rem == 0:
            break
        if rem in seen:
            # The remainder came back: everything from there on repeats.
            cycle_at = seen[rem]
            period = len(digits) - cycle_at
            break
        seen[rem] = len(digits)
        rem *= 2
        d, rem = divmod(rem, denominator)
        digits.append(str(d))
    terminated = rem == 0
    return dict(whole=whole, digits=''.join(digits), cycle_at=cycle_at,
                period=period, terminated=terminated,
                exact_value=Fraction(numerator, denominator))


def long_division_steps(numerator: int, denominator: int, steps: int = 10) -> list[dict]:
    """The long division written out row by row, the way you would do it on paper."""
    whole, rem = divmod(numerator, denominator)
    rows = []
    for i in range(steps):
        doubled = rem * 2
        digit, rem = divmod(doubled, denominator)
        rows.append(dict(index=i + 1, remainder_in=doubled // 2, doubled=doubled,
                         digit=digit, remainder_out=rem,
                         fraction_before=Fraction(doubled // 2, denominator)))
    return rows


def drift_curve(points: int = 40, top: int = 100000, value: float = 0.1) -> list[dict]:
    """How the error of a running sum grows with the number of terms."""
    out = []
    for i in range(points):
        n = max(1, int(round(10 ** (i * math.log10(top) / (points - 1)))))
        naive = sum_naive([value] * n)
        kahan = sum_kahan([value] * n)
        exact_total = Fraction(value) * n
        out.append(dict(n=n, truth=float(exact_total),
                        naive=naive, kahan=kahan,
                        naive_error=float(Fraction(naive) - exact_total),
                        kahan_error=float(Fraction(kahan) - exact_total)))
    return out


# ------------------------------------------------------------------ the gaps
def ulp(x: float) -> float:
    """Distance to the next representable float above |x| (a unit in the last place)."""
    x = abs(x)
    if x == 0:
        return 5e-324
    return math.nextafter(x, math.inf) - x


def gap_profile(lo: float, hi: float, samples: int = 9) -> list[dict]:
    """Show that the spacing between neighbouring floats is not constant."""
    out = []
    for i in range(samples):
        t = i / (samples - 1)
        v = 2.0 ** (math.log2(lo) + t * (math.log2(hi) - math.log2(lo)))
        out.append(dict(value=v, ulp=ulp(v), exponent=math.floor(math.log2(v))))
    return out


def neighbours(x: float, k: int = 3) -> dict:
    below = [from_bits(bits(x) - i) for i in range(k, 0, -1)]
    above = [from_bits(bits(x) + i) for i in range(1, k + 1)]
    return dict(below=below, above=above,
                step_up=math.nextafter(x, math.inf) - x,
                step_down=x - math.nextafter(x, -math.inf))


# --------------------------------------------------------------- the addition
def addition_trace(a: float, b: float) -> dict:
    """What the hardware really adds, before the result is rounded back."""
    exact_sum = exact(a) + exact(b)
    rounded = a + b
    return dict(a=a, b=b, a_hex='0x%016X' % bits(a), b_hex='0x%016X' % bits(b),
                a_bits=bitstring(a), b_bits=bitstring(b),
                exact_sum=exact_sum, exact_sum_float=float(exact_sum),
                rounded=rounded, rounded_hex='0x%016X' % bits(rounded),
                rounded_bits=bitstring(rounded),
                rounding_error=exact_sum - exact(rounded),
                exact_sum_decimal=decimal_digits_of(exact_sum),
                rounded_decimal=decimal_digits_of(rounded))


def error_of_sum(a: float, b: float, expected: float) -> dict:
    """How far a+b lands from the decimal number the reader typed."""
    got = a + b
    return dict(got=got, expected=expected,
                difference=Fraction(got) - Fraction(expected),
                ulps=abs((Fraction(got) - Fraction(expected)) / exact(ulp(expected))),
                got_repr=repr(got), expected_repr=repr(expected))


# ------------------------------------------------------------------ summing up
def sum_naive(values) -> float:
    total = 0.0
    for v in values:
        total += v
    return total


def sum_kahan(values) -> float:
    """Kahan compensated summation: carry the lost low bits in a second variable."""
    total = 0.0
    c = 0.0
    for v in values:
        y = v - c
        t = total + y
        c = (t - total) - y
        total = t
    return total


def sum_pairwise(values) -> float:
    """Split in half and add the halves; errors grow like log n, not n."""
    if len(values) <= 8:
        return sum_naive(values)
    mid = len(values) // 2
    return sum_pairwise(values[:mid]) + sum_pairwise(values[mid:])


def sum_sorted(values) -> float:
    return sum_naive(sorted(values, key=abs))


def accumulation_study(n: int = 100000, value: float = 0.1) -> dict:
    """Add the same number n times. The exact answer is n copies of fl(value)."""
    values = [value] * n
    exact_total = Fraction(value) * n
    rows = [('朴素从左到右', sum_naive(values)),
            ('Kahan 补偿', sum_kahan(values)),
            ('二分两两相加', sum_pairwise(values)),
            ('按绝对值从小到大', sum_sorted(values))]
    return dict(n=n, value=value,
                exact=float(exact_total),
                exact_fraction=exact_total,
                truth=n / 10.0,
                rows=[dict(name=name, got=v,
                           error=Fraction(v) - exact_total,
                           ulps=abs((Fraction(v) - exact_total) / exact(ulp(exact_total))))
                      for name, v in rows])


def mixed_sum_study(seed: int = 20261017, count: int = 20000) -> dict:
    """A list whose terms differ wildly in size: order starts to matter a lot."""
    import random
    rng = random.Random(seed)
    values = []
    for _ in range(count):
        values.append(rng.choice([1.0, 1e-3, 1e-6, 1e-9, 1e-12, 1e-15]))
    exact_total = sum(Fraction(v) for v in values)
    rows = [('朴素从左到右', sum_naive(values)),
            ('按绝对值从小到大', sum_sorted(values)),
            ('Kahan 补偿', sum_kahan(values)),
            ('二分两两相加', sum_pairwise(values))]
    return dict(seed=seed, count=count,
                exact=float(exact_total), exact_fraction=exact_total,
                rows=[dict(name=name, got=v, error=Fraction(v) - exact_total)
                      for name, v in rows])


# --------------------------------------------------------- where it really hurts
def big_eats_small(big: float = 1e16) -> dict:
    return dict(big=big, plus_one=big + 1.0, equal=big + 1.0 == big,
                ulp=ulp(big), one_is_smaller=1.0 < ulp(big))


def cancellation_table(xs=(1e-4, 1e-6, 1e-8, 1e-9)) -> list[dict]:
    """Relative error of 1-cos(x) as x shrinks. The formula is right; the arithmetic is not.

    Reference values come from the exact power series
    1 - cos x = x^2/2! - x^4/4! + x^6/6! - ..., summed in exact rational arithmetic.
    """
    out = []
    for x in xs:
        naive = 1.0 - math.cos(x)
        xf = Fraction(x)
        series = Fraction(0)
        for k in range(1, 14):
            series += ((-1) ** (k + 1)) * xf ** (2 * k) / math.factorial(2 * k)
        rel = abs(Fraction(naive) - series) / series
        stable = 2.0 * math.sin(x / 2.0) ** 2
        rel_stable = abs(Fraction(stable) - series) / series
        out.append(dict(x=x, naive=naive, stable=stable, reference=float(series),
                        relative_error=rel, relative_error_stable=rel_stable,
                        good_digits=-math.log10(float(rel)) if rel else None,
                        good_digits_stable=-math.log10(float(rel_stable)) if rel_stable else None))
    return out


def quadratic_roots(a: float, b: float, c: float) -> dict:
    """The textbook formula loses precision when b*b >> 4*a*c."""
    disc = b * b - 4 * a * c
    root = math.sqrt(disc)
    x1 = (-b + root) / (2 * a)
    x2 = (-b - root) / (2 * a)
    # Numerically stable form: use the sign that avoids subtracting近 equal numbers.
    q = -0.5 * (b + math.copysign(root, b))
    s1, s2 = q / a, c / q
    return dict(a=a, b=b, c=c, discriminant=disc, naive=(x1, x2), stable=(s1, s2),
                product_naive=x1 * x2, product_stable=s1 * s2, expected_product=c / a)


def rounding_tie() -> dict:
    """Why the sum rounds *up*: the exact total sits exactly halfway, and ties go even."""
    a, b, c = 0.1, 0.2, 0.3
    exact_sum = exact(a) + exact(b)
    lower, upper = c, from_bits(bits(c) + 1)
    midpoint = (exact(lower) + exact(upper)) / 2
    return dict(lower=lower, upper=upper,
                lower_hex='0x%016X' % bits(lower), upper_hex='0x%016X' % bits(upper),
                lower_bits=bitstring(lower), upper_bits=bitstring(upper),
                lower_last_bit=bits(lower) & 1, upper_last_bit=bits(upper) & 1,
                exact_sum=exact_sum, midpoint=midpoint,
                exactly_halfway=exact_sum == midpoint,
                distance_to_lower=exact_sum - exact(lower),
                distance_to_upper=exact(upper) - exact_sum,
                chosen=from_bits(bits(c) + 1),
                chosen_repr=repr(from_bits(bits(c) + 1)))


# ----------------------------------------------------------------- odd corners
def special_values() -> list[dict]:
    zero, neg_zero = 0.0, -0.0
    inf, ninf = math.inf, -math.inf
    nan = float('nan')
    rows = [
        ('0.0', zero, bitstring(zero), '1/0 在数学上没有定义，但 IEEE 754 给了它一个位模式'),
        ('-0.0', neg_zero, bitstring(neg_zero), '与 0.0 相等，但符号位是 1'),
        ('1/0.0', inf, bitstring(inf), '溢出与除以零都得到无穷，不抛异常'),
        ('-1/0.0', ninf, bitstring(ninf), ''),
        ('0.0/0.0', nan, bitstring(nan), 'NaN：不是数'),
        ('1e308*10', 1e308 * 10, bitstring(1e308 * 10), '上溢'),
    ]
    return [dict(name=n, value=v, bits=b, hex='0x%016X' % bits(v), note=note)
            for n, v, b, note in rows]


def nan_facts() -> dict:
    nan = float('nan')
    return dict(equal_to_itself=nan == nan, less_than=nan < 1.0,
                greater_than=nan > 1.0, in_list=nan in [nan],
                correct_check=math.isnan(nan))


def subnormal_facts() -> dict:
    smallest_normal = from_bits(1 << FRAC_BITS)          # 2**-1022
    smallest_subnormal = from_bits(1)                    # 2**-1074
    return dict(smallest_normal=smallest_normal,
                smallest_normal_hex='0x%016X' % bits(smallest_normal),
                smallest_subnormal=smallest_subnormal,
                smallest_subnormal_hex='0x%016X' % bits(smallest_subnormal),
                ratio=Fraction(smallest_normal) / Fraction(smallest_subnormal),
                normal_ulp=ulp(smallest_normal),
                subnormal_ulp=ulp(smallest_subnormal),
                underflow=smallest_subnormal / 2.0)


def float32_view(x: float) -> dict:
    """The same number squeezed into 32 bits, to show what fewer bits cost."""
    packed = struct.pack('<f', x)
    back = struct.unpack('<f', packed)[0]
    b = struct.unpack('<I', packed)[0]
    return dict(input=x, float32=back, hex='0x%08X' % b,
                bits='%s %s %s' % (format(b >> 31, '01b'),
                                   format((b >> 23) & 0xFF, '08b'),
                                   format(b & 0x7FFFFF, '023b')),
                relative_error=abs(Fraction(back) - exact(x)) / exact(x))


# ------------------------------------------------------- bits are just bits
def fast_inverse_sqrt(x: float, iterations: int = 3) -> dict:
    """The Quake III trick: read a float as an integer, do integer maths, read it back.

    The whole method lives in 32 bits, so the input is rounded to float32 first.
    """
    magic = 0x5F3759DF
    i32 = struct.unpack('<I', struct.pack('<f', x))[0]
    seed_bits = (magic - (i32 >> 1)) & 0xFFFFFFFF
    y = struct.unpack('<f', struct.pack('<I', seed_bits))[0]
    steps = []
    for _ in range(iterations):
        y = y * (1.5 - 0.5 * x * y * y)
        steps.append(y)
    truth = 1.0 / math.sqrt(x)
    return dict(x=x, magic='0x%08X' % magic, input32='0x%08X' % i32,
                seed_bits='0x%08X' % seed_bits, after_magic=struct.unpack(
                    '<f', struct.pack('<I', seed_bits))[0],
                steps=steps, final=y, truth=truth,
                errors=[abs(v - truth) / truth for v in steps])


def rounding_demo() -> list[dict]:
    """Ties go to the even neighbour. Python's round() on floats does the same."""
    rows = []
    for v in (0.5, 1.5, 2.5, 3.5, 4.5, -0.5, -2.5):
        rows.append(dict(value=v, rounded=round(v), floor=math.floor(v),
                         ceil=math.ceil(v),
                         note='正好在中间，取偶数那一侧' if abs(v) % 2 == 0.5 else ''))
    return rows


# --------------------------------------------------- what a decimal literal is
def representable(numerator: int, denominator: int) -> bool:
    """A fraction is exact in binary only when its denominator is a power of two."""
    d = denominator
    while d % 2 == 0:
        d //= 2
    return d == 1


def exactness_table() -> list[dict]:
    rows = []
    for num, den in ((1, 2), (1, 4), (3, 4), (1, 8), (1, 5), (1, 10), (2, 10), (3, 10),
                     (1, 3), (1, 20), (1, 100), (7, 40)):
        v = num / den
        rows.append(dict(fraction='%d/%d' % (num, den), decimal=repr(v),
                         binary_exact=representable(num, den),
                         stored_exactly=exact(v) == Fraction(num, den),
                         stored=float(exact(v)),
                         error=Fraction(v) - Fraction(num, den)))
    return rows


def power_gallery() -> list[dict]:
    """Powers of two: only the exponent field changes, the fraction stays zero."""
    rows = []
    for e in range(-4, 6):
        v = 2.0 ** e
        d = decode(v)
        rows.append(dict(value=v, exponent=e, raw_exponent=d['raw_exponent'],
                         fraction=d['fraction'], bits=bitstring(v),
                         hex=d['hex']))
    return rows


def decimal_digits_of(x, n: int = 60) -> str:
    """The exact decimal expansion of a float or Fraction, no rounding shortcut.

    Pass the Fraction when you mean the exact value. Passing float(fraction)
    rounds it first, which silently turns "the exact sum" into "the rounded
    sum" -- and those are the two things this article exists to tell apart.
    """
    f = x if isinstance(x, Fraction) else exact(x)
    sign = '-' if f < 0 else ''
    f = abs(f)
    whole, rem = divmod(f.numerator, f.denominator)
    out = []
    for _ in range(n):
        if rem == 0:
            break
        rem *= 10
        d, rem = divmod(rem, f.denominator)
        out.append(str(d))
    tail = ''.join(out) if out else '0'
    return '%s%d.%s' % (sign, whole, tail)


def tolerance_table() -> list[dict]:
    """What an absolute tolerance of 1e-9 actually means at different magnitudes."""
    rows = []
    for v in (1e-6, 1.0, 1e6, 1e12, 1e15):
        rows.append(dict(value=v, ulp=ulp(v), tol_in_ulps=1e-9 / ulp(v),
                         safe_digits=max(0, int(math.floor(math.log10(v / ulp(v)))))
                         if v else 0))
    return rows


def article_numbers() -> dict:
    """Every number the prose and the figures quote, in one place."""
    a, b, c = 0.1, 0.2, 0.3
    got = a + b
    return dict(
        sum_repr=repr(got), sum_hex='0x%016X' % bits(got),
        three_hex='0x%016X' % bits(c),
        difference=float(Fraction(got) - Fraction(c)),
        difference_ulps=float(abs((Fraction(got) - Fraction(c)) / exact(ulp(c)))),
        exact_sum_decimal=decimal_digits_of(exact(a) + exact(b), 60),
        rounded_decimal=decimal_digits_of(got, 60),
        three_decimal=decimal_digits_of(c, 60),
        one_tenth_exact=decimal_digits_of(a, 60),
        tenth_binary=long_division(1, 10, 40),
        one_fourth_binary=long_division(1, 4, 20),
        one_third_binary=long_division(1, 3, 24),
        ulp1=ulp(1.0), ulp_1e16=ulp(1e16),
        big_eats_small=big_eats_small(),
        float32_of_tenth=float32_view(0.1),
        subnormal=subnormal_facts(),
        nan=nan_facts(),
        fast_inv=fast_inverse_sqrt(0.5, 3),
        accumulation=accumulation_study(100000, 0.1),
        mixed=mixed_sum_study(),
        cancellation=cancellation_table(),
        quadratic=quadratic_roots(1.0, -1e8, 1.0),
        tolerance=tolerance_table(),
    )
