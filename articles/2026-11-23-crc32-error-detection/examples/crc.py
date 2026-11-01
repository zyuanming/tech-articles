"""CRC-32, bit by bit, without any library help.

Everything here is plain Python: no zlib, no binascii. The point is that a
CRC is small enough to write out in full and check against known-good
values, so the article's numbers and the figures share one source.

MIT licensed; see LICENSE-CODE.txt.
"""

import math
import struct


# ---------------------------------------------------------------- GF(2) basics

def poly_bits(poly, width):
    """Bit string of a polynomial of degree < width, leading bit first."""
    return format(poly, '0%db' % width)


def deg(poly):
    return poly.bit_length() - 1


def poly_mul(a, b):
    """Multiply two GF(2) polynomials (carry-less)."""
    out = 0
    while b:
        if b & 1:
            out ^= a
        a <<= 1
        b >>= 1
    return out


def poly_mod(a, b):
    """Remainder of a divided by b, carry-less."""
    db = deg(b)
    while a and deg(a) >= db:
        a ^= b << (deg(a) - db)
    return a


def poly_divmod(a, b):
    """Quotient and remainder, so the long division can be drawn."""
    db = deg(b)
    q = 0
    steps = []
    while a and deg(a) >= db:
        shift = deg(a) - db
        q ^= 1 << shift
        before = a
        a ^= b << shift
        steps.append((before, b << shift, shift, a))
    return q, a, steps


# ------------------------------------------------------- the classic CRC-32

POLY32 = 0x04C11DB7        # x^32 + x^26 + x^23 + ... + 1, the IEEE 802.3 one


def crc32_reflected(data):
    """CRC-32/ISO-HDLC: what zlib, PNG, Ethernet and ZIP all compute."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xEDB88320 if crc & 1 else 0)
    return crc ^ 0xFFFFFFFF


def crc32_table():
    table = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ (0xEDB88320 if c & 1 else 0)
        table.append(c)
    return table


def crc32_tablewise(data, table=None):
    table = table or crc32_table()
    crc = 0xFFFFFFFF
    for byte in data:
        crc = table[(crc ^ byte) & 0xFF] ^ (crc >> 8)
    return crc ^ 0xFFFFFFFF


# --------------------------------------------- the same thing, MSB first
# Readable arithmetic version: shift the message left by `width` bits and
# take the remainder modulo the generator. Slow, obvious, used for figures.

def crc_msb(data, poly=POLY32, width=32, init=0, xorout=0):
    reg = init
    top = 1 << (width - 1)
    mask = (1 << width) - 1
    for byte in data:
        reg ^= (byte << (width - 8)) & mask
        for _ in range(8):
            if reg & top:
                reg = ((reg << 1) ^ poly) & mask
            else:
                reg = (reg << 1) & mask
    return reg ^ xorout


def remainder_of_message(data, poly=POLY32, width=32):
    """True long division: message(x)·x^width mod G(x)."""
    msg = int.from_bytes(data, 'big') << width
    g = (1 << width) | poly
    return poly_mod(msg, g)


# ------------------------------------------------------- check values
# The catalogue's "check" value: CRC of the ASCII string "123456789".
# If these match, the implementation is the textbook one.

STANDARDS = [
    # name, width, poly, init, refin, refout, xorout, check, where it lives
    ('CRC-32/ISO-HDLC', 32, 0x04C11DB7, 0xFFFFFFFF, True, True, 0xFFFFFFFF,
     0xCBF43926, 'Ethernet, ZIP, PNG, gzip'),
    ('CRC-32/BZIP2', 32, 0x04C11DB7, 0xFFFFFFFF, False, False, 0xFFFFFFFF,
     0xFC891918, 'bzip2'),
    ('CRC-32/MPEG-2', 32, 0x04C11DB7, 0xFFFFFFFF, False, False, 0x00000000,
     0x0376E6E7, 'MPEG-2 transport stream'),
    ('CRC-32C (Castagnoli)', 32, 0x1EDC6F41, 0xFFFFFFFF, True, True, 0xFFFFFFFF,
     0xE3069283, 'iSCSI, ext4, SSE4.2'),
    ('CRC-32K (Koopman)', 32, 0x741B8CD7, 0xFFFFFFFF, True, True, 0xFFFFFFFF,
     0x2D3DD0AE, 'research, strongest 32-bit'),
    ('CRC-16/ARC', 16, 0x8005, 0x0000, True, True, 0x0000,
     0xBB3D, 'IBM bisync, modems'),
    ('CRC-16/CCITT-FALSE', 16, 0x1021, 0xFFFF, False, False, 0x0000,
     0x29B1, 'XMODEM, older protocols'),
    ('CRC-8', 8, 0x07, 0x00, False, False, 0x00,
     0xF4, 'SMBus, 1-Wire, NFC'),
]


def check_values():
    data = b'123456789'
    out = []
    for name, width, poly, init, refin, refout, xorout, expect, where in STANDARDS:
        if refin:
            got = crc_reflected(data, poly, width, init, xorout)
        else:
            got = crc_msb(data, poly, width, init, xorout)
        out.append(dict(name=name, width=width, poly=poly, check=got,
                        expected=expect, ok=got == expect, where=where))
    return out


def crc_reflected(data, poly, width, init, xorout):
    """Bit-reversed form: input and output bit order both reversed."""
    rpoly = int(format(poly, '0%db' % width)[::-1], 2)
    crc = init
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (rpoly if crc & 1 else 0)
    return crc ^ xorout


# --------------------------------------------------- what gets caught

def burst_exhaustive(maxlen=16, poly=POLY32, width=32):
    """Every burst of length <= maxlen, all of them, checked one by one."""
    g = (1 << width) | poly
    rows = []
    for L in range(1, maxlen + 1):
        free = max(0, L - 2)
        missed = []
        for v in range(1 << free):
            pat = 1
            for i in range(free):
                pat = (pat << 1) | ((v >> (free - 1 - i)) & 1)
            pat = (pat << 1) | 1
            if poly_mod(pat, g) == 0:
                missed.append(pat)
        rows.append(dict(length=L, patterns=1 << free, missed=len(missed)))
    return rows


def first_undetectable_burst(poly=POLY32, width=32, limit=64):
    """The shortest burst the generator cannot see is the generator itself."""
    g = (1 << width) | poly
    return dict(length=g.bit_length(), hex='%09X' % g,
                missed=poly_mod(g, g) == 0, weight=bin(g).count('1'))


def burst_examples(poly=POLY32, width=32, k=2):
    """Bursts of length exactly width+1 that slip through: G shifted by k bits."""
    g = (1 << width) | poly
    return [dict(shift=sh, length=g.bit_length() + sh,
                 hex='%09X' % (g << sh), remainder=poly_mod(g << sh, g))
            for sh in range(k + 1)]


def small_width_demo(span=10):
    """Exhaustive on a narrow CRC, where the algebra is actually visible.

    Two 4-bit generators: x^4+x^2+x+1 (has the factor x+1) and x^4+x+1
    (a trinomial, no x+1). Enumerate every error pattern of weight 1..4
    inside a `span`-bit window and count the ones that divide evenly.
    """
    gens = [('x^4+x^2+x+1', 0b10111), ('x^4+x+1', 0b10011)]
    out = []
    for name, poly in gens:
        g = poly
        width = deg(poly)
        per_weight = []
        for k in range(1, span + 1):
            missed = 0
            count = 0
            for mask in range(1 << span):
                if bin(mask).count('1') != k:
                    continue
                count += 1
                if poly_mod(mask, g) == 0:
                    missed += 1
            if count:
                per_weight.append(dict(weight=k, patterns=count, missed=missed))
        out.append(dict(gen=name, poly=poly, width=width,
                        has_x_plus_1=has_factor(poly & ~(1 << width), width, 0b11),
                        rows=per_weight))
    return out


def has_factor(poly, width, factor):
    """Does the generator have `factor` as a polynomial factor?"""
    return poly_mod(poly | (1 << width), factor) == 0


def factor_table():
    out = []
    for name, f in (('x+1', 0b11), ('x^2+x+1', 0b111), ('x^3+x+1', 0b1011),
                    ('x^4+x+1', 0b10011), ('x^5+x^2+1', 0b100101),
                    ('x^7+x^6+1', 0b11000001)):
        out.append(dict(name=name, poly=f,
                        crc32=has_factor(POLY32, 32, f),
                        crc32c=has_factor(0x1EDC6F41, 32, f),
                        crc32k=has_factor(0x741B8CD7, 32, f)))
    return out


def odd_weight_detection(poly=POLY32, width=32, trials=4000, seed=4242):
    """If (x+1) divides the generator, every odd number of bit flips is caught."""
    rng = Rng(seed)
    g = poly | (1 << width)
    rows = []
    for k in (1, 2, 3, 4, 5):
        missed = 0
        for _ in range(trials):
            pat = 0
            for _ in range(k):
                pat ^= 1 << rng.randrange(0, 96)
            if pat % g == 0:
                missed += 1
        rows.append(dict(weight=k, odd=bool(k % 2), missed=missed,
                         trials=trials))
    return rows


def code_distance(poly, width, maxlen):
    """Minimum Hamming distance of the code: codewords are data·x^n + CRC.

    Small message lengths only; the search is exponential in the worst case,
    so this exists to show the number, not to be a proof.
    """
    g = (1 << width) | poly
    best = None
    for m in range(1, maxlen + 1):
        worst = 0
        for v in range(1 << m):
            code = (v << width) | poly_mod(v << width, g)
            if code == 0:
                continue
            w = bin(code).count('1')
            if best is None or w < best[0]:
                best = (w, m, v)
            if w > worst:
                worst = w
        if best and best[1] == m:
            pass
    return best


def hamming_distance(poly, width, msglen):
    """Minimum distance between distinct codewords for messages of `msglen`."""
    g = (1 << width) | poly
    words = []
    for v in range(1 << msglen):
        words.append((v << width) | poly_mod(v << width, g))
    best = width + msglen
    arg = None
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            w = bin(words[i] ^ words[j]).count('1')
            if w < best:
                best, arg = w, (i, j)
    return dict(distance=best, pair=arg, msglen=msglen, width=width)


# --------------------------------------------------------- weaker schemes

def naive_sum(data):
    return sum(data) & 0xFF


def naive_xor(data):
    out = 0
    for b in data:
        out ^= b
    return out


def fletcher16(data):
    a = b = 0
    for byte in data:
        a = (a + byte) % 255
        b = (b + a) % 255
    return (b << 8) | a


def swap_failures(trials=20000, msglen=64, seed=777):
    """A transposition error (two bytes swapped): who notices, who does not."""
    rng = Rng(seed)
    schemes = [('8 位累加和', naive_sum), ('8 位异或', naive_xor),
               ('Fletcher-16', fletcher16),
               ('CRC-16/CCITT', lambda d: crc_msb(d, 0x1021, 16, 0xFFFF, 0)),
               ('CRC-32', lambda d: crc32_reflected(d))]
    rows = []
    for label, fn in schemes:
        missed = 0
        for _ in range(trials):
            good = bytearray(rng.randrange(0, 256) for _ in range(msglen))
            i = rng.randrange(0, msglen)
            j = rng.randrange(0, msglen)
            # swapping two equal bytes changes nothing; those cases are not
            # misses, they are non-errors
            while j == i or good[i] == good[j]:
                j = rng.randrange(0, msglen)
            bad = bytearray(good)
            bad[i], bad[j] = bad[j], bad[i]
            good = bytes(good)
            if fn(good) == fn(bytes(bad)):
                missed += 1
        rows.append(dict(scheme=label, missed=missed, trials=trials,
                         miss_rate=missed / trials))
    return rows


def random_error_rate(poly=0x07, width=8, nbits=2048, trials=20000, seed=31337):
    """Uniformly random error patterns: how many slip through a narrow CRC."""
    rng = Rng(seed)
    g = (1 << width) | poly
    missed = 0
    for _ in range(trials):
        pat = 0
        for _ in range(nbits):
            pat = (pat << 1) | rng.randrange(0, 2)
        if poly_mod(pat, g) == 0:
            missed += 1
    return dict(missed=missed, trials=trials, rate=missed / trials,
                predicted=2.0 ** -width)


def collision_by_length():
    """Birthday bound: how many messages before a collision is likely."""
    rows = []
    for width in (8, 16, 32, 64):
        rows.append(dict(width=width,
                         half=round(math.sqrt(2 ** width * math.log(2)))))
    return rows


# ---------------------------------------------------------------- utilities

class Rng:
    """xorshift32, seeded through an LCG: deterministic and good enough that
    the error patterns are not secretly periodic (the low bits of an LCG are).
    """

    def __init__(self, seed):
        s = seed & 0xFFFFFFFF or 0x1234567
        s = (1103515245 * s + 12345) & 0xFFFFFFFF
        self.s = s or 0x9E3779B9

    def next(self):
        s = self.s
        s ^= (s << 13) & 0xFFFFFFFF
        s ^= s >> 17
        s ^= (s << 5) & 0xFFFFFFFF
        self.s = s
        return s

    def randrange(self, lo, hi=None):
        if hi is None:
            lo, hi = 0, lo
        return lo + self.next() % (hi - lo)

    def bit(self):
        return self.next() & 1


def division_demo(msg=0b1101011011, poly=0b10011):
    """The textbook long division, step by step."""
    width = deg(poly)
    m = msg << width
    q, r, steps = poly_divmod(m, poly)
    return dict(message=msg, poly=poly, width=width,
                dividend=m, quotient=q, remainder=r,
                steps=[dict(before=b, sub=s, shift=k, after=a)
                       for b, s, k, a in steps])


def bit_trace(data=b'\xd3', poly=POLY32, width=32, init=0):
    """Every single shift of the MSB-first register, to animate one byte."""
    reg = init
    top = 1 << (width - 1)
    mask = (1 << width) - 1
    rows = []
    reg ^= (data[0] << (width - 8)) & mask
    rows.append(dict(bit=None, reg=reg, xored=False))
    for i in range(8):
        xored = bool(reg & top)
        reg = ((reg << 1) ^ poly) & mask if xored else (reg << 1) & mask
        rows.append(dict(bit=(data[0] >> (7 - i)) & 1, reg=reg, xored=xored))
    return dict(byte=data[0], rows=rows, final=reg)


def frame_layout(payload=64):
    """Ethernet II: preamble, addresses, type, payload, FCS."""
    fields = [
        ('前导码', 7, 'SFD'),
        ('SFD', 1, ''),
        ('目的 MAC', 6, ''),
        ('源 MAC', 6, ''),
        ('类型', 2, '0x0800 = IPv4'),
        ('载荷', payload, '最小 46 字节'),
        ('FCS', 4, 'CRC-32'),
    ]
    total = sum(f[1] for f in fields)
    return dict(fields=[dict(name=n, bytes=b, note=t) for n, b, t in fields],
                total=total)


def throughput(bits=32, bytes_overhead=4):
    """What the check costs, in percent, for a few payload sizes."""
    rows = []
    for payload in (64, 512, 1500, 9000):
        rows.append(dict(payload=payload, overhead=bytes_overhead / payload * 100))
    return rows


def collision_bound():
    """Birthday bound: how many messages before a collision is likely."""
    rows = []
    for width in (8, 16, 32, 64):
        rows.append(dict(width=width,
                         half=round(math.sqrt(2 ** width * math.log(2)))))
    return rows


def forging_demo(msg=b'ATTACK AT DAWN', span=5):
    """Find an edit that leaves the real (reflected) CRC-32 untouched.

    The CRC of a fixed-length message is an affine map from its bits to 32
    bits, so edits live in a kernel of dimension 8n-32.  Rather than trust a
    hand-derived pattern, solve for one: Gaussian elimination over GF(2) on
    the last `span` bytes gives a combination whose CRC difference is zero.
    """
    n = len(msg)
    base = crc32_reflected(msg)
    bits = span * 8
    vecs = []
    for i in range(bits):
        pos = n - span + i // 8
        pat = bytes((1 << (i % 8)) if j == pos else 0 for j in range(n))
        vecs.append(base ^ crc32_reflected(bytes(a ^ b for a, b in zip(msg, pat))))
    basis, sol = {}, 0
    for i, v in enumerate(vecs):
        mask = 1 << i
        while v:
            p = v.bit_length() - 1
            if p in basis:
                bv, bm = basis[p]
                v ^= bv
                mask ^= bm
            else:
                basis[p] = (v, mask)
                break
        if v == 0:
            sol = mask
            break
    delta = bytearray(n)
    for j in range(span):
        delta[n - span + j] = (sol >> (j * 8)) & 0xFF
    other = bytes(a ^ b for a, b in zip(msg, delta))
    return dict(text=msg.decode(), forged=other.hex(' '), span=span,
                changed_bits=bin(sol).count('1'),
                crc='%08X' % base,
                forged_crc='%08X' % crc32_reflected(other),
                same=crc32_reflected(other) == base)


def build():
    msg = b'The quick brown fox jumps over the lazy dog'
    return dict(
        standards=check_values(),
        demo=division_demo(),
        trace=bit_trace(),
        table=crc32_table()[:16],
        fox=dict(text=msg.decode(), crc=crc32_reflected(msg),
                 crc_hex='%08X' % crc32_reflected(msg),
                 tablewise=crc32_tablewise(msg),
                 remainder=remainder_of_message(msg)),
        burst=burst_exhaustive(16),
        burst_min=first_undetectable_burst(),
        burst_examples=burst_examples(),
        narrow=random_error_rate(),
        small_width=small_width_demo(),
        factors=factor_table(),
        distance=[hamming_distance(POLY32, 32, 2),
                  hamming_distance(POLY32, 32, 3),
                  hamming_distance(0x1EDC6F41, 32, 3)],
        swap=swap_failures(),
        frame=frame_layout(),
        overhead=throughput(),
        birthday=collision_bound(),
        forging=forging_demo(),
        polys=[format(POLY32, '032b'), format(0x1EDC6F41, '032b')],
    )


if __name__ == '__main__':
    import json
    r = build()
    for row in r['standards']:
        print('%-22s %02X %s' % (row['name'], row['check'],
                                 'ok' if row['ok'] else 'MISMATCH %08X' % row['expected']))
    print('fox', r['fox']['crc_hex'], r['fox']['tablewise'] == r['fox']['crc'])
