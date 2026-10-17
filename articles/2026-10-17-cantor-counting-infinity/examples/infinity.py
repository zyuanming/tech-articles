"""Cantor's infinities, made concrete and checkable. MIT.

Everything here is finite and computable: we build explicit pairings, check
them on finite ranges, and run the diagonal construction on a real list of
decimals. Nothing depends on the reader accepting an infinite process on
faith -- each claim is checked on the part of it a computer can hold.
"""
from __future__ import annotations
from fractions import Fraction


# ---------------------------------------------------------------- pairings
def naturals_evens(n):
    """0,1,2,3,...  <->  0,2,4,6,...   the simplest bijection."""
    return 2 * n


def naturals_integers(n):
    """Cantor's zigzag: 0,1,2,3,4,... <-> 0,-1,1,-2,2,..."""
    return n // 2 if n % 2 == 0 else -(n // 2 + 1)


def integers_naturals(z):
    """The inverse of the zigzag."""
    return 2 * z if z >= 0 else -2 * z - 1


def cantor_pair(a, b):
    """Pair two naturals into one: the standard diagonal enumeration."""
    s = a + b
    return s * (s + 1) // 2 + b


def naturals_pairs(n):
    """Walk the (a, b) grid along diagonals, so every pair is reached."""
    s = 0
    while cantor_pair(s, 0) <= n:
        base = s * (s + 1) // 2
        if n - base <= s:
            return (s - (n - base), n - base)
        s += 1
    raise ValueError(n)


def rationals_enumeration(limit):
    """List positive fractions by walking diagonals of the (numerator,
    denominator) grid and skipping fractions that are not in lowest terms.

    Returns [(index, Fraction)] for the first `limit` reduced fractions.
    """
    out = []
    s = 1
    while len(out) < limit:
        for num in range(1, s + 1):
            den = s + 1 - num
            f = Fraction(num, den)
            if f.numerator == num and f.denominator == den:
                out.append(f)
                if len(out) >= limit:
                    break
        s += 1
    return list(enumerate(out))


def check_bijection(f, lo, hi):
    """Is f injective on [lo, hi] and does its image look like a range?"""
    images = [f(i) for i in range(lo, hi + 1)]
    return dict(domain=hi - lo + 1, distinct=len(set(images)),
                injective=(len(set(images)) == len(images)),
                images=images)


# ---------------------------------------------------------------- diagonal
def diagonal_number(strings, safe_digits='12345678', width=None):
    """Build a decimal that differs from strings[n] at position n.

    The digits are kept inside 1..8 so the result can never end in a tail of
    9s or 0s, which would make two different decimal expansions name the same
    number (0.4999... = 0.5000...).
    """
    digits = [s.split('.')[1] if '.' in s else s for s in strings]
    if width is None:
        width = len(digits)
    out = []
    for i in range(width):
        d = int(digits[i][i])
        out.append(safe_digits[d % len(safe_digits)])
    return ''.join(out)


def diagonal_escapes(strings, width=None):
    """Where does the diagonal differ from each listed number?"""
    diag = diagonal_number(strings, width=width)
    rows = []
    for i, s in enumerate(strings):
        body = s.split('.')[1] if '.' in s else s
        first_diff = next((j for j in range(len(body)) if body[j] != diag[j]),
                          None)
        rows.append(dict(index=i + 1, listed=s,
                         differs_at=(first_diff + 1) if first_diff is not None
                         else None,
                         differs=(body != diag)))
    return diag, rows


def power_set_sizes(n_max=10):
    """|P(S)| = 2^|S|, strictly bigger than |S|."""
    return [dict(size=n, subsets=2 ** n, bigger=(2 ** n > n))
            for n in range(0, n_max + 1)]


def binary_strings(n):
    """All 2^n binary strings of length n."""
    return [format(i, '0%db' % n) for i in range(2 ** n)]


def pad_decimal(s, width):
    """Pad a decimal expansion to a fixed number of digits after the point."""
    head, _, body = s.partition('.')
    return head + '.' + (body + '0' * width)[:width]


def diagonal_rounds(start, rounds=3, width=14):
    """Run the diagonal construction, then add the result and run it again.

    Each round shows the same thing: whatever list you hand it, the diagonal
    is not on that list. Adding it just gives the next round something new to
    escape.
    """
    listing = [pad_decimal(s, width) for s in start]
    out = []
    for r in range(rounds):
        diag, rows = diagonal_escapes(listing, width=len(listing))
        out.append(dict(round=r + 1, how_many_listed=len(listing),
                        diagonal='0.' + diag,
                        differs_from_all=all(x['differs'] for x in rows),
                        escapes=[dict(listed=x['listed'],
                                      differs_at=x['differs_at'])
                                 for x in rows]))
        listing.append(pad_decimal('0.' + diag, width))
    return out
