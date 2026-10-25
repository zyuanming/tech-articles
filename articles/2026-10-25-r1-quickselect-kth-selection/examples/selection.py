"""Three-list teaching Quickselect. Code: CC0-1.0."""
import random


def quickselect(values, k, rng=None):
    """Return the 1-based kth smallest integer; keep duplicates and input."""
    a = list(values)
    if not a or type(k) is not int or not 1 <= k <= len(a):
        raise ValueError("k must be an integer from 1 to len(values)")
    if any(type(x) is not int for x in a):
        raise TypeError("this teaching version accepts integers only")
    rng = rng if rng is not None else random.Random()
    while True:
        p = rng.choice(a)
        less, equal, greater = [], [], []
        for x in a:
            if x < p:
                less.append(x)
            elif x > p:
                greater.append(x)
            else:
                equal.append(x)
        L, E = len(less), len(equal)
        if k <= L:
            a = less
        elif k <= L + E:
            return p
        else:
            k -= L + E
            a = greater


def trace(values, k, pick):
    """Instrument same partition rules. pick(a, round) supplies teaching pivots."""
    a, rows, offset = list(values), [], 0
    while True:
        p = pick(a, len(rows))
        assert p in a
        less, equal, greater = [], [], []
        for x in a:
            (less if x < p else greater if x > p else equal).append(x)
        L, E = len(less), len(equal)
        branch = 'less' if k <= L else 'equal' if k <= L + E else 'greater'
        next_k = k - L - E if branch == 'greater' else k
        rows.append(dict(a=a, k=k, p=p, less=less, equal=equal, greater=greater,
                         L=L, E=E, branch=branch, next_k=next_k, offset=offset))
        if branch == 'equal':
            return dict(answer=p, rows=rows, visits=sum(len(r['a']) for r in rows))
        if branch == 'greater':
            offset += L + E
        a, k = (less if branch == 'less' else greater), next_k
