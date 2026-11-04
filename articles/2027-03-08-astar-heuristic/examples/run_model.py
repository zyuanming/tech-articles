"""跑出正文与图片要用的全部数字，写进 results.json。"""

import json
from pathlib import Path

import astar as A

HERE = Path(__file__).resolve().parent


def scatter_map(n, density, seed, diagonal=True, diag_cost=None):
    """随机撒障碍的地图：起点左上、终点右下，两者都留空。"""
    rng = A.SplitMix64(seed)
    walls = set()
    for x in range(n):
        for y in range(n):
            if (x, y) in ((0, 0), (n - 1, n - 1)):
                continue
            if rng.below(100) < density:
                walls.add((x, y))
    return A.Grid(n, n, walls, diagonal=diagonal, diag_cost=diag_cost), walls


def variants_of(grid, start, goal, variants, keep_trace=False):
    rows = []
    for name, kw in variants:
        r = A.search(grid, start, goal, **kw)
        row = dict(name=name, expansions=r['expansions'],
                   generated=r['generated'], open_max=r['open_max'],
                   cost=None if r['cost'] is None else round(r['cost'], 4),
                   length=len(r['path']),
                   path=[[int(c[0]), int(c[1])] for c in r['path']],
                   expanded=[[int(t['cell'][0]), int(t['cell'][1])]
                             for t in r['trace']])
        if keep_trace:
            row['trace'] = [dict(cell=t['cell'], g=t['g'], h=t['h'], f=t['f'])
                            for t in r['trace']]
        rows.append(row)
    return rows


def open_grid():
    """空地：所有 f 都相等的那一张纪念照。"""
    g4 = A.Grid(6, 6)
    g8 = A.Grid(6, 6, diagonal=True)
    start, goal = (0, 0), (5, 5)
    return dict(
        four=dict(width=6, height=6, start=list(start), goal=list(goal),
                  walls=[], diagonal=False, diag_cost=1.0,
                  variants=variants_of(g4, start, goal, [
                      ('dijkstra', dict(h=A.h_zero)),
                      ('astar', dict(h=A.h_manhattan)),
                      ('astar_tie', dict(h=A.h_manhattan, tie_break=True))],
                      keep_trace=True)),
        eight=dict(width=6, height=6, start=list(start), goal=list(goal),
                   walls=[], diagonal=True, diag_cost=round(g8.diag_cost, 4),
                   variants=variants_of(g8, start, goal, [
                       ('dijkstra', dict(h=A.h_zero)),
                       ('astar', dict(h=A.h_octile)),
                       ('astar_tie', dict(h=A.h_octile, tie_break=True))],
                       keep_trace=True)))


def wall_grid():
    """一道只有顶部缺口的竖墙：h 太平，省得很少。"""
    walls = [(4, y) for y in range(7) if y != 0]
    g4 = A.Grid(9, 7, walls)
    g8 = A.Grid(9, 7, walls, diagonal=True)
    start, goal = (0, 3), (8, 3)
    return dict(
        four=dict(width=9, height=7, start=list(start), goal=list(goal),
                  walls=[list(w) for w in sorted(walls)], diagonal=False,
                  diag_cost=1.0,
                  variants=variants_of(g4, start, goal, [
                      ('dijkstra', dict(h=A.h_zero)),
                      ('astar', dict(h=A.h_manhattan)),
                      ('astar_tie', dict(h=A.h_manhattan, tie_break=True))],
                      keep_trace=True)),
        eight=dict(width=9, height=7, start=list(start), goal=list(goal),
                   walls=[list(w) for w in sorted(walls)], diagonal=True,
                   diag_cost=round(g8.diag_cost, 4),
                   variants=variants_of(g8, start, goal, [
                       ('dijkstra', dict(h=A.h_zero)),
                       ('astar', dict(h=A.h_octile)),
                       ('astar_tie', dict(h=A.h_octile, tie_break=True))],
                       keep_trace=True)))


MAP_VARIANTS = [
    ('dijkstra', dict(h=A.h_zero)),
    ('astar', dict(h=A.h_octile)),
    ('astar_tie', dict(h=A.h_octile, tie_break=True)),
    ('w=2', dict(h=A.h_octile, weight=2.0)),
    ('w=3', dict(h=A.h_octile, weight=3.0)),
    ('manhattan', dict(h=A.h_manhattan)),
]


def map_run(n, density, seed, label):
    g, walls = scatter_map(n, density, seed)
    start, goal = (0, 0), (n - 1, n - 1)
    opt = A.optimal_cost(g, start, goal)
    rows = variants_of(g, start, goal, MAP_VARIANTS)
    for r in rows:
        r['ratio'] = round(r['cost'] / opt, 4)
    return dict(label=label, width=n, height=n, density=density, seed=seed,
                start=list(start), goal=list(goal), wall_count=len(walls),
                walls=[list(w) for w in sorted(walls)],
                optimal=round(opt, 4), rows=rows)


def weight_sweep():
    """同一张地图上把 w 从 1 拉到 5，看省下多少、亏掉多少。"""
    g, _ = scatter_map(33, 18, 77)
    start, goal = (0, 0), (32, 32)
    opt = A.optimal_cost(g, start, goal)
    rows = []
    for i in range(0, 17):
        w = 1.0 + 0.25 * i
        r = A.search(g, start, goal, h=A.h_octile, weight=w)
        rows.append(dict(weight=round(w, 2), expansions=r['expansions'],
                         open_max=r['open_max'],
                         cost=round(r['cost'], 4),
                         ratio=round(r['cost'] / opt, 4),
                         bound=round(w, 2)))
    return dict(map='33x33 density=18 seed=77', optimal=round(opt, 4), rows=rows)


def consistency():
    """一致性检查：√2 斜走的网格上欧氏是一致，斜走同价时就不是了。"""
    g, _ = scatter_map(21, 20, 20270301)
    goal = (20, 20)
    rows = []
    for name, h in (('octile', A.h_octile), ('chebyshev', A.h_chebyshev),
                    ('euclid', A.h_euclid)):
        worst, worst_edge = 0.0, None
        for u in ((x, y) for y in range(21) for x in range(21)):
            if u in g.walls:
                continue
            for v in g.neighbors(u):
                c = g.step_cost(u, v)
                drop = h(u, goal) - h(v, goal)
                if drop - c > worst:
                    worst = drop - c
                    worst_edge = dict(u=list(u), v=list(v), step=round(c, 4),
                                      hu=round(h(u, goal), 4),
                                      hv=round(h(v, goal), 4),
                                      excess=round(drop - c, 4))
        rows.append(dict(name=name, worst_excess=round(worst, 4),
                         edge=worst_edge))
    same_price, _ = scatter_map(21, 20, 20270301, diag_cost=1.0)
    rows2 = []
    for name, h in (('euclid', A.h_euclid), ('octile', A.h_octile)):
        worst, worst_edge = 0.0, None
        for u in ((x, y) for y in range(21) for x in range(21)):
            if u in same_price.walls:
                continue
            for v in same_price.neighbors(u):
                c = same_price.step_cost(u, v)
                drop = h(u, goal) - h(v, goal)
                if drop - c > worst:
                    worst = drop - c
                    worst_edge = dict(u=list(u), v=list(v), step=round(c, 4),
                                      hu=round(h(u, goal), 4),
                                      hv=round(h(v, goal), 4),
                                      excess=round(drop - c, 4))
        rows2.append(dict(name=name, worst_excess=round(worst, 4),
                          edge=worst_edge))
    return dict(sqrt2_grid=rows, same_price_grid=rows2)


def closed_set_counterexample():
    """8 方向同价（每一步都算 1）时，欧氏距离会高估，闭表重不重开都救不回来。"""
    walls = [(0, 3), (0, 5), (1, 5), (1, 7), (2, 2), (3, 0), (3, 6),
             (5, 1), (6, 5), (7, 2)]
    g = A.Grid(8, 8, walls, diagonal=True, diag_cost=1.0)
    start, goal = (0, 0), (7, 7)
    opt = A.optimal_cost(g, start, goal)
    rows = []
    for name, kw in (('euclid 闭表不重开', dict(h=A.h_euclid, reopen=False)),
                     ('euclid 允许重开', dict(h=A.h_euclid, reopen=True)),
                     ('chebyshev 闭表不重开',
                      dict(h=A.h_chebyshev, reopen=False)),
                     ('octile 闭表不重开', dict(h=A.h_octile, reopen=False))):
        r = A.search(g, start, goal, **kw)
        rows.append(dict(name=name, expansions=r['expansions'],
                         cost=r['cost'], reopenings=r['reopenings'],
                         path=[[int(c[0]), int(c[1])] for c in r['path']],
                         trace=[dict(cell=t['cell'], g=t['g'], h=t['h'],
                                     f=t['f']) for t in r['trace']]))
    return dict(width=8, height=8, diag_cost=1.0, start=list(start),
                goal=list(goal), walls=[list(w) for w in walls],
                optimal=round(opt, 4), variants=rows)


def overestimate(trials=300):
    """同价斜走的随机小地图上，欧氏距离错了多少次、错多少。"""
    rng = A.SplitMix64(20270308)
    stats = dict(trials=0, suboptimal_noclose=0, suboptimal_reopen=0,
                 worst_gap=0.0, example=None)
    while stats['trials'] < trials:
        n = 6 + rng.below(4)
        walls = set()
        for x in range(n):
            for y in range(n):
                if (x, y) in ((0, 0), (n - 1, n - 1)):
                    continue
                if rng.below(100) < 20:
                    walls.add((x, y))
        g = A.Grid(n, n, walls, diagonal=True, diag_cost=1.0)
        start, goal = (0, 0), (n - 1, n - 1)
        opt = A.optimal_cost(g, start, goal)
        if opt is None:
            continue
        stats['trials'] += 1
        a = A.search(g, start, goal, h=A.h_euclid, reopen=False)
        b = A.search(g, start, goal, h=A.h_euclid, reopen=True)
        for key, r in (('suboptimal_noclose', a), ('suboptimal_reopen', b)):
            if r['cost'] is None or r['cost'] > opt + 1e-9:
                stats[key] += 1
        gap = (a['cost'] or 0.0) - opt
        if gap > stats['worst_gap']:
            stats['worst_gap'] = round(gap, 4)
            stats['example'] = dict(n=n, walls=sorted(walls), optimal=opt,
                                    got=a['cost'])
    return stats


def main():
    out = dict(
        open_grid=open_grid(),
        wall=wall_grid(),
        map18=map_run(33, 18, 77, 'density=18 seed=77'),
        map25=map_run(33, 25, 77, 'density=25 seed=77'),
        sweep=weight_sweep(),
        consistency=consistency(),
        closed_set=closed_set_counterexample(),
        overestimate=overestimate(),
    )
    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1))
    return out


if __name__ == '__main__':
    d = main()
    for key, val in d.items():
        print('<', key, '>')
        if key in ('open_grid', 'wall'):
            for gk in ('four', 'eight'):
                print(' ', gk, [(v['name'], v['expansions'], v['open_max'],
                                 v['cost']) for v in val[gk]['variants']])
        elif key in ('map18', 'map25'):
            print('  optimal', val['optimal'], 'walls', val['wall_count'])
            for r in val['rows']:
                print('   ', r['name'], r['expansions'], r['open_max'],
                      r['cost'], r['ratio'])
        elif key == 'sweep':
            print('  optimal', val['optimal'])
            for r in val['rows']:
                print('   w=%.2f' % r['weight'], r['expansions'], r['cost'],
                      r['ratio'])
        elif key == 'consistency':
            print('  sqrt2', val['sqrt2_grid'])
            print('  same', val['same_price_grid'])
        elif key == 'overestimate':
            print(' ', val)
        else:
            print('  optimal', val['optimal'])
            for v in val['variants']:
                print('   ', v['name'], v['expansions'], v['cost'], v['path'])
