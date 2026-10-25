"""Exact integer Chinese remainder reconstruction, original teaching code. CC0."""
from math import gcd, prod

def integer(x):
    if type(x) is not int:
        raise TypeError('expected Python int, not float/bool')
    return x

def modulus(m):
    m = integer(m)
    if m < 1:
        raise ValueError('modulus must be positive')
    return m

def egcd(a, b):
    """Nonnegative inputs; return (g,s,t) with s*a+t*b=g."""
    integer(a); integer(b)
    if a < 0 or b < 0:
        raise ValueError('egcd expects nonnegative inputs')
    r0, r1, s0, s1, t0, t1 = a, b, 1, 0, 0, 1
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q*r1
        s0, s1 = s1, s0 - q*s1
        t0, t1 = t1, t0 - q*t1
    return r0, s0, t0

def inverse(a, m):
    integer(a); modulus(m)
    if m == 1:
        raise ValueError('inverse uses modulus >= 2')
    g, s, _ = egcd(a % m, m)
    if g != 1:
        raise ValueError('inverse does not exist')
    return s % m

def coprime_basis(moduli):
    ms = list(moduli)
    if not ms:
        raise ValueError('supply at least one modulus')
    for m in ms:
        modulus(m)
        if m == 1:
            raise ValueError('basis example uses moduli >= 2')
    M = prod(ms)
    es = []
    for m in ms:
        q = M // m
        es.append(q * inverse(q, m))
    return M, es

def reconstruct(residues, moduli):
    rs, ms = list(residues), list(moduli)
    if len(rs) != len(ms):
        raise ValueError('length mismatch')
    for r in rs:
        integer(r)
    M, es = coprime_basis(ms)
    return sum((r % m)*e for r, m, e in zip(rs, ms, es)) % M, M

def merge(a, m, b, n):
    """Return least nonnegative x and lcm(m,n), or None if inconsistent."""
    integer(a); integer(b); modulus(m); modulus(n)
    a, b = a % m, b % n
    g = gcd(m, n)
    delta = b - a
    if delta % g:
        return None
    m1, n1 = m // g, n // g
    # Modulo one imposes no new condition: avoid calling inverse(..., 1).
    t = 0 if n1 == 1 else ((delta // g) * inverse(m1, n1)) % n1
    L = m * n1
    return (a + m*t) % L, L

def solve(pairs):
    """Pairs are (residue, positive modulus); empty system is rejected."""
    pairs = list(pairs)
    if not pairs:
        raise ValueError('empty system rejected by this teaching interface')
    # Validate the whole input before a valid inconsistent prefix can return None.
    validated = []
    for pair in pairs:
        try:
            b, n = pair
        except (TypeError, ValueError):
            raise ValueError('each condition must contain exactly two fields') from None
        integer(b)
        modulus(n)
        validated.append((b, n))
    a, m = 0, 1
    for b, n in validated:
        result = merge(a, m, b, n)
        if result is None:
            return None
        a, m = result
    return a, m

def centered(x, M):
    """Representative in (-M/2, M/2], including +M/2 for even M."""
    integer(x); modulus(M)
    x %= M
    return x - M if 2*x > M else x
