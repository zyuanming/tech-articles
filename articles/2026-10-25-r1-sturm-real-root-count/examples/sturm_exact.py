"""Exact rational Sturm teaching implementation. Original code: CC0.
Coefficients are LOW degree first. No floats are accepted by the core API.
Counts DISTINCT real roots in (a,b]; square-free reduction is automatic.
"""
from fractions import Fraction as F


def rational(x):
    if isinstance(x, float):
        raise TypeError('Use an int, Fraction, or exact rational string')
    return F(x)


def poly(values):
    p = [rational(x) for x in values]
    while p and not p[-1]:
        p.pop()
    return tuple(p)


def derivative(p):
    return poly(i*p[i] for i in range(1, len(p)))


def evaluate(p, x):
    x = rational(x)
    value = F(0)
    for c in reversed(p):
        value = value*x + c
    return value


def divide(a, b):
    a, b = list(poly(a)), poly(b)
    if not b:
        raise ZeroDivisionError('Zero polynomial divisor')
    q = [F(0)] * max(0, len(a)-len(b)+1)
    while a and len(a) >= len(b):
        shift = len(a)-len(b)
        factor = a[-1]/b[-1]
        q[shift] += factor
        for j, c in enumerate(b):
            a[j+shift] -= factor*c
        a = list(poly(a))
    return poly(q), poly(a)


def multiply(a, b):
    if not a or not b:
        return ()
    out = [F(0)]*(len(a)+len(b)-1)
    for i, u in enumerate(a):
        for j, v in enumerate(b):
            out[i+j] += u*v
    return poly(out)


def gcd(a, b):
    a, b = poly(a), poly(b)
    while b:
        a, b = b, divide(a, b)[1]
    return poly(v/a[-1] for v in a) if a else ()


def squarefree(p):
    p = poly(p)
    if not p:
        raise ValueError('The zero polynomial has infinitely many roots')
    if len(p) == 1:
        return p
    q, remainder = divide(p, gcd(p, derivative(p)))
    assert not remainder
    return q


def chain(p):
    q = squarefree(p)
    seq = [q]
    if len(q) == 1:
        return seq
    seq.append(derivative(q))
    while True:
        remainder = divide(seq[-2], seq[-1])[1]
        if not remainder:
            break
        # Do NOT force each entry to have leading coefficient +1.
        seq.append(poly(-v for v in remainder))
    return seq


def signs(seq, x):
    values = [evaluate(p, x) for p in seq]
    return [(v > 0)-(v < 0) for v in values]


def variations(seq, x):
    nz = [s for s in signs(seq, x) if s]
    return sum(a != b for a, b in zip(nz, nz[1:]))


def count(p, a, b, ends='(]'):
    a, b = rational(a), rational(b)
    if not a < b:
        raise ValueError('Require a < b')
    if ends not in ('(]', '[]', '()', '[)'):
        raise ValueError('Unknown endpoint convention')
    seq = chain(p)
    n = variations(seq, a)-variations(seq, b)
    if ends[0] == '[':
        n += int(evaluate(seq[0], a) == 0)
    if ends[1] == ')':
        n -= int(evaluate(seq[0], b) == 0)
    return n


def isolate(p, a, b, max_width=F(1, 4), max_nodes=10000):
    """Disjoint (left,right] intervals, each contains one distinct root.
    Only covers (a,b]; no all-roots bound is implied. Resource cap raises.
    """
    a, b, max_width = map(rational, (a, b, max_width))
    if a >= b or max_width <= 0:
        raise ValueError('Require a<b and max_width>0')
    seq = chain(p)
    pending = [(a, b, None)]
    nodes, leaves = [], []
    while pending:
        if len(nodes) >= max_nodes:
            raise RuntimeError('Isolation resource cap reached')
        lo, hi, parent = pending.pop()
        va, vb = variations(seq, lo), variations(seq, hi)
        n = va-vb
        node = dict(a=str(lo), b=str(hi), va=va, vb=vb,
                    count=n, parent=parent, id=len(nodes))
        nodes.append(node)
        if n == 0:
            node['status'] = 'empty'
        elif n == 1 and hi-lo <= max_width:
            node['status'] = 'isolated'
            leaves.append((lo, hi))
        else:
            node['status'] = 'split'
            mid = (lo+hi)/2
            pending.append((mid, hi, node['id']))
            pending.append((lo, mid, node['id']))
    return leaves, nodes
