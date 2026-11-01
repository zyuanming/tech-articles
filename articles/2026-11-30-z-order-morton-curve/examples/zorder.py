"""Z-order (Morton) curve: bit interleaving, locality, range queries.

Standard library only.  Every number in the article comes from build().
The vocabulary is deliberately small: an integer key per grid cell, three
ways to assign those keys (row-major, Morton, Hilbert), and two questions
asked of every assignment -- how far does the curve jump between
consecutive keys, and how many contiguous runs does a rectangle occupy?
"""

import math
import json


# ---------------------------------------------------------------- bit tricks

def spread(x, stride=2):
    """Space the bits of x out with zeros: stride 2 for 2D, 3 for 3D.

    pdep() is a single instruction on x86 since Haswell; here it is a loop.
    """
    out = 0
    bit = 0
    while x:
        if x & 1:
            out |= 1 << (stride * bit)
        x >>= 1
        bit += 1
    return out


def compress(x):
    """Inverse of spread(): keep every other bit."""
    out = 0
    bit = 0
    while x:
        if x & 1:
            out |= 1 << bit
        x >>= 2
        bit += 1
    return out


def morton2(x, y):
    """Interleave: x goes in the even bit positions, y in the odd ones."""
    return spread(x) | (spread(y) << 1)


def demorton2(code):
    return compress(code), compress(code >> 1)


def morton3(x, y, z):
    return spread(x, 3) | (spread(y, 3) << 1) | (spread(z, 3) << 2)


def row_major(x, y, n):
    return y * n + x


def hilbert_xy2d(n, x, y):
    """Hilbert index of (x, y) in an n x n square, n a power of two."""
    d = 0
    s = n >> 1
    while s:
        rx = 1 if (x & s) else 0
        ry = 1 if (y & s) else 0
        d += s * s * ((3 * rx) ^ ry)
        if ry == 0:
            if rx == 1:
                x = n - 1 - x
                y = n - 1 - y
            x, y = y, x
        s >>= 1
    return d


def hilbert_d2xy(n, d):
    x = y = 0
    t = d
    s = 1
    while s < n:
        rx = 1 & (t >> 1)
        ry = 1 & (t ^ rx)
        if ry == 0:
            if rx == 1:
                x = s - 1 - x
                y = s - 1 - y
            x, y = y, x
        x += s * rx
        y += s * ry
        t >>= 2
        s *= 2
    return x, y


# ---------------------------------------------------------------- orders

def order_keys(n, how):
    """Return a list of (key, x, y) sorted by key, for one ordering."""
    cells = [(x, y) for y in range(n) for x in range(n)]
    if how == 'row':
        keyed = [(row_major(x, y, n), x, y) for x, y in cells]
    elif how == 'morton':
        keyed = [(morton2(x, y), x, y) for x, y in cells]
    elif how == 'hilbert':
        keyed = [(hilbert_xy2d(n, x, y), x, y) for x, y in cells]
    else:
        raise ValueError(how)
    keyed.sort()
    return keyed


def curve_cost(n, how):
    """How far the curve jumps between consecutive keys, over all keys."""
    seq = order_keys(n, how)
    jumps = []
    for a, b in zip(seq, seq[1:]):
        jumps.append(math.hypot(a[1] - b[1], a[2] - b[2]))
    jumps.sort()
    total = sum(jumps)
    return dict(order=how, cells=len(seq),
                mean=total / len(jumps),
                longest=jumps[-1],
                p95=jumps[int(0.95 * (len(jumps) - 1))],
                over_4=sum(1 for j in jumps if j > 4))


def rect_runs(n, how, w, h, trials=400, seed=20261130, aligned=True):
    """Contiguous runs needed to cover a w x h rectangle in key order.

    This is the cost of a range query when the index is just a sorted list of
    keys: one seek plus one sequential scan per run.
    """
    seq = order_keys(n, how)
    rank = {}
    for i, (key, x, y) in enumerate(seq):
        rank[(x, y)] = i
    rng = _Rng(seed)
    step = max(w, h)
    xs = list(range(0, n - w + 1, step))
    ys = list(range(0, n - h + 1, step))
    total = 0
    for t in range(trials):
        if aligned:
            x0 = xs[t % len(xs)]
            y0 = ys[(t // len(xs)) % len(ys)]
        else:
            x0 = rng.randrange(0, n - w + 1)
            y0 = rng.randrange(0, n - h + 1)
        inside = [rank[(x, y)] for y in range(y0, y0 + h) for x in range(x0, x0 + w)]
        inside.sort()
        runs = 1
        for a, b in zip(inside, inside[1:]):
            if b != a + 1:
                runs += 1
        total += runs
    return total / trials


def rect_table(n=256):
    """Runs per rectangle for three orders: grid-aligned and random offset."""
    shapes = [(1, 16), (16, 1), (4, 4), (8, 8), (16, 16), (32, 32), (64, 8)]
    rows = []
    for w, h in shapes:
        rows.append(dict(w=w, h=h, area=w * h,
                         row=rect_runs(n, 'row', w, h),
                         morton=rect_runs(n, 'morton', w, h),
                         hilbert=rect_runs(n, 'hilbert', w, h),
                         row_free=rect_runs(n, 'row', w, h, aligned=False),
                         morton_free=rect_runs(n, 'morton', w, h, aligned=False),
                         hilbert_free=rect_runs(n, 'hilbert', w, h, aligned=False)))
    return rows


def sector_table(n=256, tile=8):
    """Distinct 32-byte sectors touched by one square tile, per layout.

    A cache line holds `n` bytes of the tile; a square tile in row-major order
    is `tile` separate lines, in Morton order it is `tile`-ish contiguous
    blocks.  Counts are exact, not sampled.
    """
    out = []
    line = 32
    for how in ('row', 'morton', 'hilbert'):
        for name, (w, h) in (('8x8', (tile, tile)), ('16x16', (tile * 2, tile * 2))):
            x0 = y0 = 0
            idx = [_key(how, x, y, n)
                   for y in range(y0, y0 + h) for x in range(x0, x0 + w)]
            lines = {i // line for i in idx}
            out.append(dict(order=how, tile=name, cells=len(idx),
                            lines=len(lines), span=max(idx) - min(idx) + 1))
    return out


# ---------------------------------------------------------------- structure

def prefix_is_square(n=8):
    """Morton's selling point: a k-bit prefix (k even) is one aligned square."""
    rows = []
    for bits in (1, 2, 3, 4, 5, 6):
        seen = {}
        for y in range(n):
            for x in range(n):
                pre = morton2(x, y) >> (2 * int(math.log2(n)) - bits)
                seen.setdefault(pre, []).append((x, y))
        widths = set()
        for cells in seen.values():
            xs = [c[0] for c in cells]
            ys = [c[1] for c in cells]
            widths.add((max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
        rows.append(dict(bits=bits, groups=len(seen),
                         shapes=sorted({f'{w}x{h}' for w, h in widths})[:6]))
    return rows


def jump_profile(n=8):
    """Every jump in the 8x8 Morton curve that is longer than one cell."""
    seq = order_keys(n, 'morton')
    out = []
    for a, b in zip(seq, seq[1:]):
        d = math.hypot(a[1] - b[1], a[2] - b[2])
        if d > 1:
            out.append(dict(a=[a[1], a[2]], b=[b[1], b[2]],
                            ka=a[0], kb=b[0], dist=d))
    return dict(total=len(out), jumps=out)


def clustered_points(n=1024, count=4096, centres=16, sigma=12.0, seed=7):
    """Points in blobs, the way real coordinates arrive (cities, stars, pixels)."""
    rng = _Rng(seed)
    cx = [rng.randrange(n) for _ in range(centres)]
    cy = [rng.randrange(n) for _ in range(centres)]
    pts = []
    for i in range(count):
        gx, gy = _gauss(rng), _gauss(rng)
        x = int(cx[i % centres] + sigma * gx)
        y = int(cy[i % centres] + sigma * gy)
        pts.append((min(n - 1, max(0, x)), min(n - 1, max(0, y))))
    return pts


def _gauss(rng):
    u1 = (rng.next() + 1) / 4294967297.0
    u2 = rng.next() / 4294967296.0
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


def compression(n=1024, count=4096, seed=7):
    """Sorted keys over clustered points: bits per delta, after sorting."""
    pts = clustered_points(n, count, seed=seed)
    out = []
    for how in ('row', 'morton', 'hilbert'):
        keys = sorted((_key(how, x, y, n) for x, y in pts))
        deltas = [b - a for a, b in zip(keys, keys[1:]) if b > a]
        bits = [max(1, int(math.log2(d)) + 1) for d in deltas]
        out.append(dict(order=how, mean_bits=sum(bits) / len(bits),
                        mean_delta=sum(deltas) / len(deltas)))
    return out


def three_d(n=32, side=4, aligned=True):
    """Same run-count question one dimension up: Morton vs row-major in 3D."""
    out = []
    for how in ('row', 'morton'):
        cells = []
        for z in range(n):
            for y in range(n):
                for x in range(n):
                    if how == 'row':
                        cells.append(((z * n + y) * n + x, x, y, z))
                    else:
                        cells.append((morton3(x, y, z), x, y, z))
        cells.sort()
        rank = {(x, y, z): i for i, (k, x, y, z) in enumerate(cells)}
        rng = _Rng(99)
        total = 0
        for t in range(60):
            if aligned:
                x0 = (t * side) % (n - side + 1) // side * side
                y0 = (t * side * 3) % (n - side + 1) // side * side
                z0 = (t * side * 7) % (n - side + 1) // side * side
            else:
                x0 = rng.randrange(0, n - side + 1)
                y0 = rng.randrange(0, n - side + 1)
                z0 = rng.randrange(0, n - side + 1)
            idx = sorted(rank[(x, y, z)]
                         for z in range(z0, z0 + side)
                         for y in range(y0, y0 + side)
                         for x in range(x0, x0 + side))
            runs = 1 + sum(1 for a, b in zip(idx, idx[1:]) if b != a + 1)
            total += runs
        out.append(dict(order=how, cube=side, aligned=aligned, runs=total / 60))
    return out


def bit_layout(x=5, y=3, bits=3):
    """One cell, encoded: the table the article can read off."""
    rows = []
    for i in range(bits):
        rows.append(dict(bit=bits - 1 - i,
                         x=(x >> (bits - 1 - i)) & 1,
                         y=(y >> (bits - 1 - i)) & 1))
    return dict(x=x, y=y, code=morton2(x, y),
                x_bits=format(x, '0%db' % bits),
                y_bits=format(y, '0%db' % bits),
                code_bits=format(morton2(x, y), '0%db' % (2 * bits)),
                rows=rows)


def _key(how, x, y, n):
    if how == 'row':
        return row_major(x, y, n)
    if how == 'morton':
        return morton2(x, y)
    return hilbert_xy2d(n, x, y)


class _Rng:
    """xorshift32; the low bits of an LCG would leak into these tests."""

    def __init__(self, seed):
        self.s = ((seed * 1103515245 + 12345) & 0x7FFFFFFF) or 1

    def next(self):
        s = self.s
        s ^= (s << 13) & 0xFFFFFFFF
        s ^= s >> 17
        s ^= (s << 5) & 0xFFFFFFFF
        self.s = s & 0xFFFFFFFF
        return self.s

    def randrange(self, lo, hi=None):
        if hi is None:
            lo, hi = 0, lo
        return lo + self.next() % (hi - lo)


def build():
    n = 8
    return dict(
        bit_layout=bit_layout(),
        cells=[dict(code=morton2(x, y), x=x, y=y) for y in range(n) for x in range(n)],
        prefix=prefix_is_square(n),
        jumps=jump_profile(n),
        cost=[curve_cost(256, how) for how in ('row', 'morton', 'hilbert')],
        rects=rect_table(256),
        sectors=sector_table(256, 8),
        compression=compression(1024, 4096),
        three_d=three_d(32, 4, True) + three_d(32, 4, False),
    )


if __name__ == '__main__':
    print(json.dumps(build(), indent=1, ensure_ascii=False)[:600])
