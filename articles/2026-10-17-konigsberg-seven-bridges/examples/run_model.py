#!/usr/bin/env python3
"""Seven Bridges: degrees, Euler's rule, Hierholzer's route, and the modern uses.

Standard library only. Writes results.json next to this file. MIT.
"""
from __future__ import annotations
import json
from itertools import combinations, combinations_with_replacement
from pathlib import Path

from graphs import (degrees, odd_vertices, parity_rule, hierholzer,
                    check_trail, brute_force_exists, route_inspection,
                    de_bruijn, connected, directed_parity_rule,
                    hierholzer_directed, out_in_degrees,
                    route_inspection_naive)

HERE = Path(__file__).resolve().parent

# Königsberg in 1736. A = Kneiphof island, B and C = the two banks,
# D = Lomse island. Two bridges join A to B, two join A to C, and one each
# joins A-D, B-D, C-D.
KONIGSBERG_1736 = [('A', 'B'), ('A', 'B'), ('A', 'C'), ('A', 'C'),
                   ('A', 'D'), ('B', 'D'), ('C', 'D')]

# Five bridges remain at the same sites today. The source records the degrees
# (two vertices of degree 2, two of degree 3) but not the exact adjacency, so
# this is a labelled reconstruction with those degrees, not a survey.
KALININGRAD_TODAY = [('A', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'D'), ('C', 'D')]


def exhaustive_check(max_edges=5, n_vertices=4):
    """Compare Euler's parity rule against brute force on every small graph.

    This is the article's own verification: we do not take the rule on trust,
    we try every walk on every graph with at most `max_edges` edges and see
    whether the rule ever disagrees.
    """
    possible = list(combinations_with_replacement(
        range(n_vertices), 2))
    possible = [e for e in possible if e[0] != e[1]]      # no self-loops here
    checked = agreed = 0
    counterexamples = []
    for size in range(0, max_edges + 1):
        for combo in combinations_with_replacement(range(len(possible)), size):
            edges = [possible[i] for i in combo]
            if not connected(edges):
                continue
            rule, _ = parity_rule(edges)
            brute = brute_force_exists(edges)
            checked += 1
            if rule == brute:
                agreed += 1
            else:
                counterexamples.append(edges)
    return dict(graphs_checked=checked, agreements=agreed,
                counterexamples=counterexamples[:5])


def distinct_rebuilds(edges, limit=4000):
    """Every distinct sequence consistent with this set of k-mers.

    The de Bruijn graph is DIRECTED: an edge (prefix, suffix) may only be
    walked prefix -> suffix. An earlier version of this code walked the graph
    as if it were undirected, which invented sequences whose k-mer sets did
    not match. See README.
    """
    out = set()

    def walk(rem, at, path):
        if len(out) >= limit:
            return
        if not rem:
            out.add(path[0] + ''.join(x[-1] for x in path[1:]))
            return
        for i, (u, v) in enumerate(rem):
            if u == at:
                walk(rem[:i] + rem[i + 1:], v, path + [v])

    o, i_ = out_in_degrees(edges)
    verts = set(o) | set(i_)
    starts = [v for v in verts if o.get(v, 0) - i_.get(v, 0) == 1]
    for s in (starts or list(verts)):
        walk(list(edges), s, [s])
    return out


def assembly_ambiguity(trials=300, seed=3, k=4):
    """How often do the k-mers pin the sequence down uniquely?"""
    import random
    rng = random.Random(seed)
    dist = {}
    total = 0
    example = None
    for _ in range(trials):
        n = rng.randint(8, 12)
        seq = ''.join(rng.choice('ACGT') for _ in range(n))
        outs = distinct_rebuilds(de_bruijn(seq, k))
        assert seq in outs
        dist[len(outs)] = dist.get(len(outs), 0) + 1
        total += len(outs)
        if len(outs) == 2 and example is None:
            example = seq
    return dict(trials=trials, seed=seed, k=k,
                distribution={str(a): b for a, b in sorted(dist.items())},
                unique_solutions=dist.get(1, 0),
                mean_ambiguity=round(total / trials, 2),
                example_two_solutions=example)


def de_bruijn_demo(sequence='CGTAATGCC'):
    """Rebuild a sequence from its k-mers using an Eulerian path.

    This is the real modern use: a DNA sequencer hands you short overlapping
    reads and no order, and assembling them is exactly an Eulerian path
    problem on a de Bruijn graph.
    """
    k = 4
    edges = de_bruijn(sequence, k)
    ok, why = directed_parity_rule(edges)
    trail = hierholzer_directed(edges)
    rebuilt = None
    if trail:
        rebuilt = trail[0] + ''.join(t[-1] for t in trail[1:])
    alternatives = sorted(distinct_rebuilds(edges))
    return dict(sequence=sequence, k=k, kmers=[a + b[-1] for a, b in edges],
                graph_edges=len(edges), odd_vertices=odd_vertices(edges),
                rule=why, eulerian_path_exists=ok,
                rebuilt=rebuilt, matches=(rebuilt == sequence),
                trail=trail, distinct_sequences=alternatives,
                how_many_sequences=len(alternatives))


def main():
    out = {}
    k = KONIGSBERG_1736
    ok, why = parity_rule(k)
    out['konigsberg_1736'] = dict(
        bridges=len(k), degrees=degrees(k), odd=odd_vertices(k),
        rule_ok=ok, rule_reason=why,
        brute_force_found_a_route=brute_force_exists(k),
        hierholzer_result=hierholzer(k),
        route_inspection_extra_crossings=route_inspection(k),
        route_inspection_naive=route_inspection_naive(k))

    n = KALININGRAD_TODAY
    ok2, why2 = parity_rule(n)
    trail = hierholzer(n)
    out['kaliningrad_today'] = dict(
        bridges=len(n), degrees=degrees(n), odd=odd_vertices(n),
        rule_ok=ok2, rule_reason=why2, trail=trail,
        trail_valid=check_trail(n, trail),
        route_inspection_extra_crossings=route_inspection(n),
        route_inspection_naive=route_inspection_naive(n),
        note='现有五座桥的度数由来源给出；具体连接是本文按该度数重建的模型')

    out['exhaustive_check'] = exhaustive_check()

    # the tempting rule "odd vertices / 2" is wrong in general
    counter = [('A', 'B'), ('B', 'C'), ('C', 'A'), ('C', 'D'), ('D', 'E')]
    out['route_inspection_counterexample'] = dict(
        graph=counter, degrees=degrees(counter), odd=odd_vertices(counter),
        naive_rule=route_inspection_naive(counter),
        correct_value=route_inspection(counter),
        why='两个奇点 C 和 E 相距 2 条边；要一次走完所有边，'
            '必须把 C-D 和 D-E 各重走一遍，所以是 2 趟而不是 1 趟',
        note='本文正文里的两张图恰好都能用单条边配对，所以简单公式碰巧算对；'
             '它并不普遍成立')

    # a one-stroke drawing: which of these can be drawn without lifting the pen?
    shapes = {
        '正方形（四条边）': [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')],
        '信封（正方形加两条对角线）':
            [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A'), ('A', 'C'), ('B', 'D')],
        '房子（正方形加屋顶）':
            [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A'), ('A', 'E'), ('E', 'B')],
        '三角形加一条尾巴':
            [('A', 'B'), ('B', 'C'), ('C', 'A'), ('C', 'D')],
    }
    rows = []
    for name, edges in shapes.items():
        okk, whyy = parity_rule(edges)
        t = hierholzer(edges)
        rows.append(dict(shape=name, edges=len(edges), degrees=degrees(edges),
                         odd=odd_vertices(edges), drawable_in_one_stroke=okk,
                         reason=whyy, trail=t, trail_valid=check_trail(edges, t)))
    out['one_stroke'] = rows

    out['de_bruijn_unique'] = de_bruijn_demo('CGTAATGCC')
    out['de_bruijn_ambiguous'] = de_bruijn_demo('TGTATCTCTTCT')
    out['assembly_ambiguity'] = assembly_ambiguity()

    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(out, ensure_ascii=False, indent=2)[:900])


if __name__ == '__main__':
    main()
