"""Teaching implementation for connected undirected multigraphs. CC0-1.0."""
import random


def prepare(n, edges):
    if not isinstance(n, int) or n < 2:
        raise ValueError('need at least two vertices')
    clean = []
    adj = [[] for _ in range(n)]
    for u, v in edges:
        if not (isinstance(u, int) and isinstance(v, int)
                and 0 <= u < n and 0 <= v < n):
            raise ValueError('vertex outside 0..n-1')
        if u != v:  # loops never cross a cut
            clean.append((u, v))  # retain every parallel copy
            adj[u].append(v)
            adj[v].append(u)
    seen = {0}
    stack = [0]
    while stack:
        for v in adj[stack.pop()]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    if len(seen) != n:
        raise ValueError('graph must be connected')
    return clean


def trial(n, edges, rng):
    active = prepare(n, edges)
    groups = {i: {i} for i in range(n)}
    chosen = []
    while len(groups) > 2:
        index = rng.randrange(len(active))
        u, v = active[index]
        chosen.append([u, v])  # representative IDs, O(1) per step
        groups[u].update(groups.pop(v))
        updated = []
        for a, b in active:
            a = u if a == v else a
            b = u if b == v else b
            if a != b:
                updated.append((a, b))
        active = updated
    parts = sorted([sorted(g) for g in groups.values()])
    return {'value': len(active), 'parts': parts, 'chosen': chosen}


def repeat(n, edges, repetitions, seed):
    if repetitions < 1:
        raise ValueError('positive repetition count required')
    edges = list(edges)  # also allow a one-use iterator
    rng = random.Random(seed)  # do not reset inside the loop
    best = None
    for _ in range(repetitions):
        result = trial(n, edges, rng)
        if best is None or result['value'] < best['value']:
            best = result
    return best
