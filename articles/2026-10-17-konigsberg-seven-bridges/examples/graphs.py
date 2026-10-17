"""Eulerian trails: parity rule, Hierholzer's algorithm, route inspection. MIT.

A graph here is just a list of edges (u, v) with integer vertex labels.
Multiple edges between the same pair are allowed, because Königsberg had two
bridges between some pairs and that is exactly what the problem turns on.
"""
from __future__ import annotations
from collections import defaultdict, deque
from itertools import combinations


def degrees(edges):
    d = defaultdict(int)
    for u, v in edges:
        d[u] += 1
        d[v] += 1
    return dict(d)


def odd_vertices(edges):
    return sorted(v for v, k in degrees(edges).items() if k % 2 == 1)


def connected(edges):
    """Are all vertices that touch an edge in one component?"""
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    if not adj:
        return True
    start = next(iter(adj))
    seen, stack = {start}, [start]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return len(seen) == len(adj)


def parity_rule(edges):
    """Euler's condition: connected and 0 or 2 odd vertices."""
    if not connected(edges):
        return False, 'not connected'
    k = len(odd_vertices(edges))
    if k == 0:
        return True, 'circuit (starts and ends at the same place)'
    if k == 2:
        return True, 'trail (starts at one odd vertex, ends at the other)'
    return False, f'{k} odd vertices'


def hierholzer(edges, start=None):
    """Return an Eulerian trail as a list of vertices, or None if impossible.

    Hierholzer's algorithm: keep walking and removing edges until you are
    stuck, then splice the loops together. Carl Hierholzer published it in
    1873, and it is what turns Euler's test into an actual route.
    """
    ok, why = parity_rule(edges)
    if not ok:
        return None
    adj = defaultdict(list)
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    odd = odd_vertices(edges)
    if start is None:
        start = odd[0] if odd else next(iter(adj))
    used = [False] * len(edges)
    trail, stack = [], [start]
    while stack:
        x = stack[-1]
        nxt = None
        while adj[x]:
            y, i = adj[x][-1]
            if used[i]:
                adj[x].pop()
                continue
            nxt = (y, i)
            break
        if nxt is None:
            trail.append(stack.pop())
        else:
            y, i = nxt
            used[i] = True
            adj[x].pop()
            stack.append(y)
    if not all(used):
        return None                     # should not happen once the rule passes
    trail.reverse()
    return trail


def check_trail(edges, trail):
    """A trail is valid if it uses every edge exactly once and is connected."""
    if trail is None:
        return False
    if len(trail) != len(edges) + 1:
        return False
    remaining = list(edges)
    for a, b in zip(trail, trail[1:]):
        pair = (a, b) if (a, b) in remaining else (b, a)
        if pair not in remaining:
            return False
        remaining.remove(pair)
    return not remaining


def brute_force_exists(edges):
    """Try every starting vertex and every walk order. Tiny graphs only."""
    if not edges:
        return True
    for start in sorted({v for e in edges for v in e}):
        if _walk(edges, start, [start]):
            return True
    return False


def _walk(edges, at, path):
    if not edges:
        return True
    for i, (u, v) in enumerate(edges):
        if u == at:
            rest = edges[:i] + edges[i + 1:]
            if _walk(rest, v, path + [v]):
                return True
        elif v == at:
            rest = edges[:i] + edges[i + 1:]
            if _walk(rest, u, path + [u]):
                return True
    return False


def shortest_path_length(edges, s, t):
    """Number of edges on a shortest path between two vertices (BFS)."""
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen, queue = {s}, deque([(s, 0)])
    while queue:
        x, d = queue.popleft()
        if x == t:
            return d
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                queue.append((y, d + 1))
    return None


def route_inspection(edges):
    """Chinese postman, unweighted: fewest edges that must be repeated.

    The correct rule is NOT "odd vertices / 2". You have to pair the odd
    vertices up so that the total shortest-path distance between the paired
    vertices is as small as possible (a minimum-weight perfect matching), and
    that total is the number of repeated edges.

    The two agree whenever every matched pair happens to be adjacent, which is
    true for the two graphs in this article but not in general -- see
    `route_inspection_vs_naive` in run_model.py for a counterexample.
    """
    odd = odd_vertices(edges)
    if not odd:
        return 0
    best = [10 ** 9]

    def match(rest, acc):
        if acc >= best[0]:
            return
        if not rest:
            best[0] = acc
            return
        a = rest[0]
        for i in range(1, len(rest)):
            b = rest[i]
            match(rest[1:i] + rest[i + 1:], acc + shortest_path_length(edges, a, b))

    match(odd, 0)
    return best[0]


def route_inspection_naive(edges):
    """The tempting but wrong rule: odd vertices / 2."""
    return len(odd_vertices(edges)) // 2


def de_bruijn(sequence, k):
    """de Bruijn graph of a string: vertices are (k-1)-mers, edges are k-mers."""
    edges = []
    for i in range(len(sequence) - k + 1):
        edges.append((sequence[i:i + k - 1], sequence[i + 1:i + k]))
    return edges


def out_in_degrees(edges):
    out, inn = defaultdict(int), defaultdict(int)
    for u, v in edges:
        out[u] += 1
        inn[v] += 1
    return dict(out), dict(inn)


def directed_parity_rule(edges):
    """Euler's rule for a DIRECTED graph.

    Every vertex must have in-degree == out-degree, except at most one vertex
    with out = in + 1 (the start) and one with in = out + 1 (the finish).
    """
    out, inn = out_in_degrees(edges)
    verts = set(out) | set(inn)
    starts = [v for v in verts if out.get(v, 0) - inn.get(v, 0) == 1]
    ends = [v for v in verts if inn.get(v, 0) - out.get(v, 0) == 1]
    bad = [v for v in verts
           if abs(out.get(v, 0) - inn.get(v, 0)) > 1]
    if bad:
        return False, 'in/out degrees differ by more than 1 somewhere'
    if len(starts) == 0 and len(ends) == 0:
        return True, 'directed circuit'
    if len(starts) == 1 and len(ends) == 1:
        return True, 'directed trail from %s to %s' % (starts[0], ends[0])
    return False, 'unbalanced in/out degrees'


def hierholzer_directed(edges, start=None):
    """Eulerian trail that must follow each edge in its own direction."""
    ok, why = directed_parity_rule(edges)
    if not ok:
        return None
    out, inn = out_in_degrees(edges)
    verts = set(out) | set(inn)
    if start is None:
        starts = [v for v in verts if out.get(v, 0) - inn.get(v, 0) == 1]
        start = starts[0] if starts else next(iter(verts))
    adj = defaultdict(list)
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
    used = [False] * len(edges)
    trail, stack = [], [start]
    while stack:
        x = stack[-1]
        nxt = None
        while adj[x]:
            y, i = adj[x][-1]
            if used[i]:
                adj[x].pop()
                continue
            nxt = (y, i)
            break
        if nxt is None:
            trail.append(stack.pop())
        else:
            y, i = nxt
            used[i] = True
            adj[x].pop()
            stack.append(y)
    trail.reverse()
    return trail if all(used) else None
