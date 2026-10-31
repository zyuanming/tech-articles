#!/usr/bin/env python3
"""Diffie–Hellman, small enough to do by hand, large enough to be real. MIT.

Everything the article prints as a number comes from here: the powers of 5
modulo 23, the two shared secrets, the baby-step giant-step step counts, the
key exchange over the 2048-bit group from RFC 3526, and the man in the
middle's two different keys.
"""
from __future__ import annotations

import math
import random
import time

# RFC 3526, section 3: the 2048-bit MODP group (id 14). A real Internet
# parameter, not something made up for the article.
MODP14_HEX = (
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
    "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
    "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF"
)
MODP14 = int(MODP14_HEX, 16)


def is_probable_prime(n: int, rounds: int = 24) -> bool:
    """Miller–Rabin. Deterministic enough for the sizes used here."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    rng = random.Random(20261031)
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def small_prime(bits: int, seed: int) -> int:
    rng = random.Random(seed)
    while True:
        p = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(p):
            return p


def pow_table(p: int, g: int):
    """Every power of g modulo p, until it repeats."""
    rows, seen, value = [], {}, 1
    k = 0
    while value not in seen:
        seen[value] = k
        rows.append((k, value))
        value = value * g % p
        k += 1
    return rows


def key_exchange(p: int, g: int, a: int, b: int) -> dict:
    A = pow(g, a, p)
    B = pow(g, b, p)
    return dict(p=p, g=g, a=a, b=b, A=A, B=B,
                s_alice=pow(B, a, p), s_bob=pow(A, b, p))


def brute_force(g: int, target: int, p: int):
    """Try every exponent; count the modular multiplies it takes."""
    value, steps = 1, 0
    for a in range(1, p):
        value = value * g % p
        steps += 1
        if value == target:
            return a, steps
    return None, steps


def bsgs(g: int, target: int, p: int, order: int | None = None):
    """Baby-step giant-step: sqrt(order) memory, ~2 sqrt(order) multiplies."""
    n = order or (p - 1)
    m = math.isqrt(n) + 1
    table, steps = {}, 0
    e = 1
    for j in range(m):
        table.setdefault(e, j)
        e = e * g % p
        steps += 1
    factor = pow(g, (p - 1 - m) % (p - 1), p)
    gamma, steps = target, steps + 1
    for i in range(m):
        if gamma in table:
            return i * m + table[gamma], steps
        gamma = gamma * factor % p
        steps += 1
    return None, steps


def mitm(p: int, g: int, a: int, m1: int, m2: int, b: int) -> dict:
    """Mallory terminates two exchanges and forwards between them."""
    return dict(
        alice=key_exchange(p, g, a, m1),
        bob=key_exchange(p, g, m2, b),
        alice_to_mallory=pow(g, a, p),
        mallory_to_bob=pow(g, m2, p),
    )


def measure(bit_sizes=(16, 20, 24, 28), seed=7) -> list[dict]:
    """Actually run the attack on growing primes and time it."""
    out = []
    for bits in bit_sizes:
        p = small_prime(bits, seed + bits)
        g = 2
        rng = random.Random(bits)
        a = rng.randrange(2, p - 1)
        t_a = time.perf_counter()
        A = pow(g, a, p)
        pow_seconds = time.perf_counter() - t_a
        t0 = time.perf_counter()
        found_brute, brute_steps = brute_force(g, A, p)
        t1 = time.perf_counter()
        found_bsgs, bsgs_steps = bsgs(g, A, p, order=p - 1)
        t2 = time.perf_counter()
        out.append(dict(bits=bits, p=p, p_digits=len(str(p)), a=a,
                        brute_steps=brute_steps,
                        brute_seconds=round(t1 - t0, 6),
                        bsgs_steps=bsgs_steps,
                        bsgs_seconds=round(t2 - t1, 6),
                        pow_seconds=round(pow_seconds, 8),
                        bsgs_ok=pow(g, found_bsgs, p) == A,
                        brute_ok=pow(g, found_brute, p) == A,
                        sqrt_p=int(math.isqrt(p))))
    return out


if __name__ == "__main__":
    ex = key_exchange(23, 5, 6, 15)
    print("p=23 g=5 a=6 b=15:", ex)
    print("powers of 5 mod 23:", pow_table(23, 5))
    for row in measure():
        print(row)
    print("MODP14 digits:", len(str(MODP14)),
          "is prime:", is_probable_prime(MODP14))


# --- a tiny elliptic curve, for the ECDH section -------------------------

def ec_points(a: int, b: int, p: int):
    """All affine points on y^2 = x^3 + ax + b over F_p."""
    pts = []
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        for y in range(p):
            if y * y % p == rhs:
                pts.append((x, y))
    return pts


def ec_add(P, Q, a: int, p: int):
    """Chord-and-tangent addition; None is the point at infinity."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return (x3, y3)


def ec_mul(k: int, P, a: int, p: int):
    out, addend = None, P
    while k:
        if k & 1:
            out = ec_add(out, addend, a, p)
        addend = ec_add(addend, addend, a, p)
        k >>= 1
    return out


def ecdh_demo(a_curve=0, b_curve=7, p=17, g=(6, 6), ka=5, kb=7) -> dict:
    pts = ec_points(a_curve, b_curve, p)
    A = ec_mul(ka, g, a_curve, p)
    B = ec_mul(kb, g, a_curve, p)
    s1 = ec_mul(ka, B, a_curve, p)
    s2 = ec_mul(kb, A, a_curve, p)
    order = 1
    cur = g
    while cur is not None:
        cur = ec_add(cur, g, a_curve, p)
        order += 1
    return dict(p=p, a=a_curve, b=b_curve, points=[list(q) for q in pts],
                g=list(g), ka=ka, kb=kb, A=list(A), B=list(B),
                s1=list(s1), s2=list(s2), equal=s1 == s2, order=order)
