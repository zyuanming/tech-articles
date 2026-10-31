"""A small LZ77 that you can read end to end. MIT.

Everything the article claims is measured here: how many bytes turn into how
many tokens, how far back the pointers reach, what happens on data that has no
repeats, and what a bigger window actually buys you.

No third-party imports. Python 3.10+.
"""
from __future__ import annotations

import math
import zlib

WINDOW = 32768          # the number deflate settled on
MIN_MATCH = 3           # shorter than this is cheaper to send literally
MAX_MATCH = 258         # deflate's limit, so a length fits in one byte


def find_matches(data: bytes, pos: int, window: int = WINDOW,
                 chain: dict | None = None, max_chain: int = 64,
                 lazy: bool = False):
    """Longest match for the bytes starting at `pos`, looking back `window`."""
    best_len, best_off = 0, 0
    limit = max(0, pos - window)
    if chain is None:
        start = max(limit, 0)
        for cand in range(pos - 1, start - 1, -1):
            if data[cand] != data[pos]:
                continue
            n = 0
            while (n < MAX_MATCH and pos + n < len(data)
                   and data[cand + n] == data[pos + n]):
                n += 1
            if n > best_len:
                best_len, best_off = n, pos - cand
                if n == MAX_MATCH:
                    break
        return best_off, best_len
    # hash chains: only walk backwards through positions with the same prefix
    key = data[pos:pos + MIN_MATCH]
    for cand in reversed(chain.get(key, [])[-max_chain:]):
        if cand < limit:
            break
        n = MIN_MATCH
        while (n < MAX_MATCH and pos + n < len(data)
               and data[cand + n] == data[pos + n]):
            n += 1
        if n > best_len:
            best_len, best_off = n, pos - cand
            if n == MAX_MATCH:
                break
    return best_off, best_len


def compress(data: bytes, window: int = WINDOW, lazy: bool = False,
             max_chain: int = 64) -> list:
    """Greedy LZ77. Returns tokens: ('lit', byte) or ('match', dist, length)."""
    chain: dict = {}
    tokens = []
    pos = 0
    n = len(data)

    def remember(p):
        if p + MIN_MATCH <= n:
            chain.setdefault(data[p:p + MIN_MATCH], []).append(p)

    while pos < n:
        off, length = find_matches(data, pos, window, chain, max_chain)
        if length < MIN_MATCH:
            tokens.append(('lit', data[pos]))
            remember(pos)
            pos += 1
            continue
        if lazy and pos + 1 < n:
            off2, len2 = find_matches(data, pos + 1, window, chain, max_chain)
            if len2 > length:
                tokens.append(('lit', data[pos]))
                remember(pos)
                pos += 1
                continue
        tokens.append(('match', off, length))
        for p in range(pos, min(pos + length, n)):
            remember(p)
        pos += length
    return tokens


def decompress(tokens) -> bytes:
    """The decoder: a long slide, and a rule that copies can overlap."""
    out = bytearray()
    for tok in tokens:
        if tok[0] == 'lit':
            out.append(tok[1])
        else:
            _, dist, length = tok
            start = len(out) - dist
            for i in range(length):
                out.append(out[start + i])
    return bytes(out)


def bit_cost(tokens, window: int = WINDOW) -> int:
    """A fixed-width costing: 1 flag bit, then literal byte or (dist, len)."""
    obits = max(1, math.ceil(math.log2(window)))
    lbits = math.ceil(math.log2(MAX_MATCH))
    return sum(9 if t[0] == 'lit' else 1 + obits + lbits for t in tokens)


def ratio(data: bytes, tokens) -> float:
    return bit_cost(tokens) / (8 * len(data))


def window_curve(data: bytes, windows=(64, 256, 1024, 4096, 16384, 32768,
                                       65536, 262144)):
    rows = []
    for w in windows:
        toks = compress(data, window=w)
        assert decompress(toks) == data
        rows.append(dict(window=w, tokens=len(toks),
                         bits=bit_cost(toks, w), ratio=round(ratio(data, toks), 4),
                         matches=sum(1 for t in toks if t[0] == 'match')))
    return rows


def match_stats(data: bytes, window: int = WINDOW):
    toks = compress(data, window=window)
    lengths = [t[2] for t in toks if t[0] == 'match']
    dists = [t[1] for t in toks if t[0] == 'match']
    covered = sum(lengths)
    hist = {}
    for L in lengths:
        bucket = ('3' if L < 4 else '4-5' if L < 6 else '6-7' if L < 8
                  else '8-15' if L < 16 else '16-31' if L < 32
                  else '32-63' if L < 64 else '64-127' if L < 128
                  else '128-257' if L < 258 else '258')
        hist[bucket] = hist.get(bucket, 0) + 1
    order = ['3', '4-5', '6-7', '8-15', '16-31', '32-63', '64-127',
             '128-257', '258']
    return dict(tokens=len(toks), matches=len(lengths), literals=len(toks) - len(lengths),
                covered=covered, total=len(data),
                coverage=round(covered / len(data), 4),
                mean_length=round(sum(lengths) / max(len(lengths), 1), 2),
                median_length=sorted(lengths)[len(lengths) // 2] if lengths else 0,
                mean_distance=round(sum(dists) / max(len(dists), 1), 1),
                hist=[(b, hist[b]) for b in order if b in hist],
                distances=dist_density(dists))


def dist_density(dists, buckets=(1, 4, 16, 64, 256, 1024, 4096, 16384, 65536)):
    rows = []
    for i, lo in enumerate(buckets):
        hi = buckets[i + 1] if i + 1 < len(buckets) else 10 ** 9
        rows.append((lo, sum(1 for d in dists if lo <= d < hi)))
    return rows


def random_bytes(n: int, seed: int = 7) -> bytes:
    """A deterministic pseudo-random stream (no `random` module state involved)."""
    out = bytearray()
    x = seed
    while len(out) < n:
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        out.append((x >> 16) & 0xFF)
    return bytes(out[:n])


def make_log(n: int = 24000) -> bytes:
    """Synthetic access log: a few shapes repeated with varying numbers."""
    lines = []
    i = 0
    paths = ('/index.html', '/api/v1/orders', '/api/v1/orders/42',
             '/static/app.css', '/static/app.js', '/healthz')
    status = ('200', '200', '200', '404', '304')
    while sum(len(l) for l in lines) < n:
        i += 1
        lines.append('10.0.%d.%d - - [02/Nov/2026:10:%02d:%02d +0000] '
                     '"GET %s HTTP/1.1" %s %d "-" "curl/8.%d"\n'
                     % (i % 7, i % 251, i % 60, (i * 7) % 60,
                        paths[i % len(paths)], status[i % len(status)],
                        100 + i % 4000, i % 9))
    return ''.join(lines).encode()[:n]


def lazy_compare(data: bytes, window: int = WINDOW):
    greedy = compress(data, window=window, lazy=False)
    patient = compress(data, window=window, lazy=True)
    return dict(greedy_ratio=round(ratio(data, greedy), 4),
                lazy_ratio=round(ratio(data, patient), 4),
                greedy_tokens=len(greedy), lazy_tokens=len(patient),
                same=decompress(patient) == data)


def run_length_demo():
    """The extreme case: every match can point one byte back."""
    data = b'a' * 400
    toks = compress(data, window=1024)
    return dict(input=len(data), tokens=len(toks),
                kinds=[t[0] for t in toks][:8],
                lengths=[t[2] for t in toks if t[0] == 'match'][:4],
                ratio=round(ratio(data, toks), 4))


def repeat_demo(block: bytes = b'', n: int = 3):
    """Copy a paragraph three times: one literal run, then two long matches."""
    if not block:
        block = (b'Alice was beginning to get very tired of sitting by her '
                 b'sister on the bank.\n')
    data = block * n
    toks = compress(data, window=4096)
    return dict(input=len(data), tokens=len(toks),
                matches=[[t[1], t[2]] for t in toks if t[0] == 'match'],
                literals=sum(1 for t in toks if t[0] == 'lit'),
                ratio=round(ratio(data, toks), 4))


def entropy(data: bytes) -> float:
    counts = {}
    for b in data:
        counts[b] = counts.get(b, 0) + 1
    n = len(data)
    return round(-sum(c / n * math.log2(c / n) for c in counts.values()), 3)


def deflate_ratio(data: bytes) -> float:
    return round(len(zlib.compress(data, 9)) * 8 / (8 * len(data)), 4)


def available_window(data: bytes, window: int) -> int:
    """How much of the window the file can actually use at its very end."""
    return min(window, len(data))


def measure(corpus: dict) -> dict:
    rows = []
    for name, data in corpus.items():
        toks = compress(data, window=WINDOW)
        assert decompress(toks) == data, name
        rows.append(dict(name=name, size=len(data), entropy=entropy(data),
                         tokens=len(toks),
                         lz77=round(ratio(data, toks), 4),
                         deflate=deflate_ratio(data),
                         size_deflate=len(zlib.compress(data, 9))))
    return rows
