"""Patience diff: anchor on lines that are unique in both inputs. MIT.

Bram Cohen proposed this in 2007; Git ships it as `--patience` and the
`histogram` variant extends it. The idea is that a line appearing exactly
once in each file is a far more trustworthy anchor than a line that appears
twenty times, so the recursion should be driven by those anchors first.
"""
from __future__ import annotations
from collections import Counter

from myers import myers, Trace


def unique_common(a, b):
    """Positions of lines that occur exactly once in a and exactly once in b."""
    ca, cb = Counter(a), Counter(b)
    pa = {x: i for i, x in enumerate(a) if ca[x] == 1}
    pb = {x: i for i, x in enumerate(b) if cb[x] == 1}
    pairs = [(pa[x], pb[x]) for x in pa if x in pb]
    pairs.sort()
    return pairs


def longest_increasing(pairs):
    """Longest strictly increasing subsequence of (i, j) pairs, by j."""
    import bisect
    tails, back, idx = [], [], []
    for k, (i, j) in enumerate(pairs):
        pos = bisect.bisect_left(tails, j)
        if pos == len(tails):
            tails.append(j)
            back.append(idx[-1] if idx else -1)
            idx.append(k)
        else:
            tails[pos] = j
            back.append(idx[pos - 1] if pos else -1)
            idx[pos] = k
    out, cur = [], idx[-1] if idx else -1
    while cur >= 0:
        out.append(pairs[cur])
        cur = back[cur]
    out.reverse()
    return out


def patience(a, b, lo_a=0, lo_b=0, trace=None):
    tr = trace or Trace()
    anchors = longest_increasing(unique_common(a, b))
    script = []
    pa, pb = 0, 0
    for ia, ib in anchors + [(len(a), len(b))]:
        if ia > pa or ib > pb:
            script.extend(_shift(myers(a[pa:ia], b[pb:ib], tr), pa, pb))
        if ia < len(a) and ib < len(b):
            script.append(('=', ia, ib))
        pa, pb = ia + 1, ib + 1
    return script


def _shift(script, da, db):
    out = []
    for op, i, j in script:
        out.append((op, None if i is None else i + da,
                    None if j is None else j + db))
    return out


def patience_flat(a, b, trace=None):
    """Patience where each anchor gap is resolved by Myers, recursively."""
    tr = trace or Trace()
    return patience(a, b, 0, 0, tr)
