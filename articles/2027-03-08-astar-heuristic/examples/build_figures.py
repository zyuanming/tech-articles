#!/usr/bin/env python3
"""A* 一文的原创教学插图。MIT。

带数字的图都读 results.json，画图时不另算一遍。
"""
from __future__ import annotations

import json
from pathlib import Path

from figkit import (Fig, PALETTE, BG, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER,
                    RED, GRAY, LIGHT, PALE, GREEN, CREAM, TINT_T, TINT_B,
                    TINT_A, TINT_R, TINT_G)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []

VIOLET = '#5b4b8a'
PALETTE.add(VIOLET)


# ---------------------------------------------------------------- 通用零件

def new(n, title, sub=None):
    fig = Fig(900)
    fig.text((44, 26), title, 46, bold=True)
    fig.text((1018, 32), '图 %02d' % n, 40, color=GRAY, anchor='ra')
    y = 112
    if sub:
        y += int(fig.wrap((44, y), sub, 40, 974, color=INK_SOFT) * 40 * 1.35) + 20
    return fig, y


def note(fig, y, text, size=40, color=INK_SOFT):
    return y + int(fig.wrap((44, y), text, size, 974, color=color) * size * 1.35) + 16


def bullets(fig, y, items, accent=TEAL, size=40):
    for text in items:
        fig.circle(76, y + 20, 14, fill=accent, outline=accent)
        y += int(fig.wrap((114, y), text, size, 900, color=INK) * size * 1.35) + 24
    return y


def table(fig, y, cols, rows, size=38, row_h=70, zebra=True):
    for i, row in enumerate(rows):
        if zebra and i % 2 == 1:
            fig.rect(48, y - 14, 1014, y + row_h - 16, fill=PALE, outline=None)
        for (text, color, bold), (x, anchor) in zip(row, cols):
            if not text:
                continue
            w = fig.width_of(text, size, bold)
            span = (x, x + w) if anchor == 'la' else (x - w, x)
            assert span[0] >= 44 and span[1] <= 1020, 'cell out of band: %r' % (text,)
            fig.text((x, y + 2), text, size, bold=bold, color=color, anchor=anchor)
        y += row_h
    return y + 14


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def legend(fig, y, items, x0=52, step=250):
    x = x0
    for color, text in items:
        fig.rect(x, y + 4, x + 30, y + 34, fill=color, outline=None, radius=6)
        fig.text((x + 44, y - 2), text, 38, color=INK)
        x += step
    return y + 52


def axes(fig, x0, y0, x1, y1, xr, yr, xticks, yticks, xlabel, ylabel,
         xtick_labels=None, ytick_labels=None):
    def px(v):
        return x0 + (v - xr[0]) / (xr[1] - xr[0]) * (x1 - x0)

    def py(v):
        return y1 - (v - yr[0]) / (yr[1] - yr[0]) * (y1 - y0)

    for t in yticks:
        fig.line((x0, py(t)), (x1, py(t)), color=LIGHT, width=2)
    for t in xticks:
        fig.line((px(t), y0), (px(t), y1), color=LIGHT, width=2)
    fig.line((x0, y1), (x1, y1), color=INK, width=3)
    fig.line((x0, y0), (x0, y1), color=INK, width=3)
    labels = xtick_labels or [str(t) for t in xticks]
    for t, lab in zip(xticks, labels):
        fig.text((px(t), y1 + 14), lab, 38, color=INK_SOFT, anchor='ma')
    ylabs = ytick_labels or [str(t) for t in yticks]
    for t, lab in zip(yticks, ylabs):
        fig.text((x0 - 16, py(t) - 22), lab, 38, color=INK_SOFT, anchor='ra')
    fig.text((x1, y1 + 62), xlabel, 38, color=INK_SOFT, anchor='ra')
    fig.text((x0 - 16, y0 - 52), ylabel, 38, color=INK_SOFT, anchor='la')
    return px, py


# ---------------------------------------------------------------- 网格

def draw_grid(fig, g, x0, y0, cell, expanded=(), shade=PALE, path=None,
              path_color=TEAL, path_width=5, gap=1):
    walls = {(w[0], w[1]) for w in g['walls']}
    expanded = {(c[0], c[1]) for c in expanded}
    for x in range(g['width']):
        for y in range(g['height']):
            X, Y = x0 + x * cell, y0 + y * cell
            if (x, y) in walls:
                fill = outline = INK
            elif (x, y) in expanded:
                fill = outline = shade
            else:
                fill, outline = WHITE, LIGHT
            fig.rect(X, Y, X + cell - gap, Y + cell - gap, fill=fill,
                     outline=outline, width=1)
    if path:
        pts = [(x0 + c[0] * cell + cell / 2 - gap / 2,
                y0 + c[1] * cell + cell / 2 - gap / 2) for c in path]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=path_color, width=path_width)


def paint_cells(fig, g, x0, y0, cell, cells, color):
    walls = {(w[0], w[1]) for w in g['walls']}
    for c in cells:
        if (c[0], c[1]) in walls:
            continue
        X, Y = x0 + c[0] * cell, y0 + c[1] * cell
        fig.rect(X, Y, X + cell - 1, Y + cell - 1, fill=color, outline=color,
                 width=1)


def marked(fig, g, cell, x0, y0, color=GREEN):
    """起点和终点的小圆点，放在格子左上角，不压路径。"""
    for key in ('start', 'goal'):
        c = g[key]
        cx = x0 + c[0] * cell + cell * 0.24
        cy = y0 + c[1] * cell + cell * 0.24
        fig.circle(cx, cy, max(7, cell * 0.15), fill=color, outline=color)


def variant(g, name):
    for row in g.get('variants', ()):
        if row['name'] == name:
            return row
    for row in g.get('rows', ()):
        if row['name'] == name:
            return row
    raise KeyError(name)


# ---------------------------------------------------------------- 图 01

def fig01():
    fig, y = new(1, 'f = g + h：一条直路走到底',
                 '空地 6×6，四方向，步长 1。起点 (0,0)，终点 (5,5)，'
                 '曼哈顿距离 10。下表是沿上边框走的六个格子。')
    cell, x0, ty = 140, 92, y + 60
    for i in range(6):
        X = x0 + i * cell
        fig.rect(X, ty, X + cell - 8, ty + 120, fill=TINT_T, outline=LIGHT,
                 width=2, radius=10)
        fig.text((X + cell / 2 - 4, ty - 46), 'h=%d' % (10 - i), 40,
                 color=STEEL, anchor='ma')
        fig.text((X + cell / 2 - 4, ty + 34), 'f=%d' % 10, 44, bold=True,
                 color=INK, anchor='ma')
        fig.text((X + cell / 2 - 4, ty + 140), 'g=%d' % i, 40,
                 color=AMBER, anchor='ma')
        if i:
            fig.arrow((X - 8, ty + 60), (X + 12, ty + 60), color=GRAY, width=3)
    y = ty + 240
    y = note(fig, y, 'g 一路加，h 一路减，加起来一直是 10。'
                     'f 是「已经付的 + 估计还欠的」，'
                     '而在这条路上它的值从头到尾不变。')
    y = note(fig, y, '于是 A* 把每个格子都看成同样有希望。'
                     '这不是启发式失灵，是这张地图上它确实没有信息可用。')
    save(fig, '01-f-split.png', 'f = g + h 的构成，沿一条直线走到底时 f 恒定')


STEEL = '#4a6570'
PALETTE.add(STEEL)


# ---------------------------------------------------------------- 图 02

def fig02():
    g = R['open_grid']['four']
    fig, y = new(2, '空地上，36 个格子的 f 全是 10',
                 '四方向、每步 1。任何格子到起点的曼哈顿距离，'
                 '加上它到终点的曼哈顿距离，正好是 10。')
    cell, x0, ty = 138, 66, y + 40
    dij = variant(g, 'dijkstra')
    ast = variant(g, 'astar')
    for x in range(6):
        for yy in range(6):
            X, Y = x0 + x * cell, ty + yy * cell
            fig.rect(X, Y, X + cell - 8, Y + cell - 8, fill=TINT_A,
                     outline=LIGHT, width=2)
            fig.text((X + cell / 2 - 4, Y + cell / 2 - 26), '10', 44,
                     color=INK, anchor='ma')
    marked(fig, g, cell, x0, ty)
    y = ty + 6 * cell + 24
    y = note(fig, y, '所有格子同分。A* 挑哪个先展开，'
                     '只看它们进开表的先后——效果和 Dijkstra 一模一样：'
                     '%d 个格子，全部展开。' % ast['expansions'])
    y = note(fig, y, '这张图上 A* 省下 0 个格子。'
                     '「A* 比 Dijkstra 快」这句话，没有地图形状做前提就是空的。')
    save(fig, '02-empty-four.png', '空地上所有格子的 f 相等，A* 与 Dijkstra 展开数相同')


# ---------------------------------------------------------------- 图 03

def fig03():
    g = R['open_grid']['four']
    a = variant(g, 'astar')
    t = variant(g, 'astar_tie')
    fig, y = new(3, '同分的时候先展开谁',
                 '同样的空地、同样的 f=10。左边按进表先后，'
                 '右边在 f 相同时优先挑 h 更小的（更靠近终点的）。')
    cell = 66
    for i, (row, title, shade) in enumerate((
            (a, '先来后到：%d 个格子' % a['expansions'], TINT_A),
            (t, '同分挑 h 小的：%d 个格子' % t['expansions'], TINT_T))):
        x0 = 74 + i * 470
        ty = y + 90
        draw_grid(fig, g, x0, ty, cell, expanded=row['expanded'], shade=shade,
                  path=row['path'], path_width=4)
        marked(fig, g, cell, x0, ty)
        fig.text((x0, ty - 46), title, 40, bold=True, color=INK)
    y = y + 90 + 6 * cell + 40
    y = note(fig, y, '代价都是 10，一个格子也没多走；'
                     '省下来的只是展开次数，%d 对 %d。'
                     '排序里加一条「f 相同看 h」，几乎不花成本。'
                     % (a['expansions'], t['expansions']))
    y = note(fig, y, '这是 A* 在空地上唯一能省的地方：'
                     '它还是全知，只是不再漫无边际地铺开。')
    save(fig, '03-tie-break.png', '同分时按 h 优先，展开数从 36 降到 11')


# ---------------------------------------------------------------- 图 04

def fig04():
    g = R['open_grid']['eight']
    dij = variant(g, 'dijkstra')
    ast = variant(g, 'astar')
    fig, y = new(4, '八方向：一直斜着走就够了',
                 '斜走代价 √2。空地上最优路线是一条对角线，'
                 '而 h 给这条线的值是所有格子里最小的。')
    cell, x0, ty = 126, 96, y + 30
    draw_grid(fig, g, x0, ty, cell, expanded=ast['expanded'], shade=TINT_T,
              path=ast['path'], path_width=6)
    marked(fig, g, cell, x0, ty)
    y = ty + 6 * cell + 20
    y = legend(fig, y, [(TINT_T, '被展开'), (INK, '障碍'), (GREEN, '起点/终点')],
               step=230)
    y = note(fig, y, 'Dijkstra 展开 %d 个格子，A* 只展开 %d 个——'
                     '就是对角线上那几格。代价都是 %.2f。'
                     % (dij['expansions'], ast['expansions'], ast['cost']))
    save(fig, '04-empty-eight.png', '八方向空地上 A* 只展开对角线上的格子')


# ---------------------------------------------------------------- 图 05

def fig05():
    f4 = R['wall']['four']
    f8 = R['wall']['eight']
    fig, y = new(5, '一道墙，两种走法',
                 '9×7，中间竖着一道只剩顶部一格的墙。'
                 '灰色是 Dijkstra 展开的，深色是 A* 展开的。')
    cell = 44
    for i, (g, title) in enumerate(((f4, '四方向'), (f8, '八方向'))):
        dij = variant(g, 'dijkstra')
        ast = variant(g, 'astar')
        x0 = 60 + i * 500
        ty = y + 70
        draw_grid(fig, g, x0, ty, cell)
        paint_cells(fig, g, x0, ty, cell, dij['expanded'], LIGHT)
        paint_cells(fig, g, x0, ty, cell, ast['expanded'], TINT_T)
        pts = [(x0 + c[0] * cell + cell / 2, ty + c[1] * cell + cell / 2)
               for c in ast['path']]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=TEAL, width=4)
        marked(fig, g, cell, x0, ty)
        fig.text((x0, ty - 44), title, 40, bold=True, color=INK)
        fig.text((x0, ty + 7 * cell + 14),
                 'D %d / A* %d' % (dij['expansions'], ast['expansions']),
                 40, color=INK_SOFT)
    y = y + 70 + 7 * cell + 100
    y = note(fig, y, '四方向只从 48 省到 45：墙挡在中间，'
                     '离终点远近差不多的格子太多，h 分不开它们。')
    y = note(fig, y, '八方向从 46 省到 25。多出来的方向让 h 更会指路，'
                     '斜着绕过墙的那半边直接不用展开。')
    save(fig, '05-wall.png', '同一道墙下四方向与八方向的展开数对比')


# ---------------------------------------------------------------- 图 06

def fig06():
    g = R['map18']
    dij = variant(g, 'dijkstra')
    ast = variant(g, 'astar')
    fig, y = new(6, '33×33 的地图，障碍占 18%',
                 '左上角到右下角。最浅色只有 Dijkstra 走过，'
                 '青色 A* 也走过，深色是障碍。')
    cell = 27
    x0, ty = 63, y + 30
    draw_grid(fig, g, x0, ty, cell)
    paint_cells(fig, g, x0, ty, cell, dij['expanded'], LIGHT)
    paint_cells(fig, g, x0, ty, cell, ast['expanded'], TINT_T)
    pts = [(x0 + c[0] * cell + cell / 2, ty + c[1] * cell + cell / 2)
           for c in ast['path']]
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=TEAL, width=4)
    marked(fig, g, cell, x0, ty, color=GREEN)
    y = ty + 33 * cell + 20
    y = legend(fig, y, [(LIGHT, '只有 D 走过'), (TINT_T, '两边都走过'),
                        (INK, '障碍')], step=250)
    y = note(fig, y, 'Dijkstra %d 个格子，A* %d 个——少 %.1f%%，代价一样是 %.2f。'
                     % (dij['expansions'], ast['expansions'],
                        100 * (1 - ast['expansions'] / dij['expansions']),
                        ast['cost']))
    save(fig, '06-map18.png', '18% 障碍地图上 Dijkstra 与 A* 的展开范围')


# ---------------------------------------------------------------- 图 07

def fig07():
    g = R['map25']
    dij = variant(g, 'dijkstra')
    ast = variant(g, 'astar')
    fig, y = new(7, '障碍加到 25%，h 的收益缩水',
                 '同样的尺寸与起终点。空地变少，'
                 '绕路的格子离终点也差不多远，h 能分出的高下变少。')
    cell = 27
    x0, ty = 63, y + 30
    draw_grid(fig, g, x0, ty, cell, expanded=dij['expanded'], shade=LIGHT)
    draw_grid(fig, g, x0, ty, cell, expanded=ast['expanded'], shade=TINT_T,
              path=ast['path'], path_width=4)
    marked(fig, g, cell, x0, ty, color=GREEN)
    y = ty + 33 * cell + 20
    y = note(fig, y, 'Dijkstra %d 个格子，A* %d 个——只少 %.1f%%（18%% 那张是 %.0f%%）。'
                     % (dij['expansions'], ast['expansions'],
                        100 * (1 - ast['expansions'] / dij['expansions']),
                        100 * (1 - variant(R['map18'], 'astar')['expansions']
                               / variant(R['map18'], 'dijkstra')['expansions'])))
    y = note(fig, y, '启发式的强弱不是算法的属性，是地图的属性。'
                     '同一份代码，换个关卡就从省 3.3 倍变成省 1.8 倍。')
    save(fig, '07-map25.png', '25% 障碍地图上 A* 的收益缩水')


# ---------------------------------------------------------------- 图 08

def fig08():
    s = R['sweep']
    rows = s['rows']
    fig, y = new(8, '把 h 乘上一个系数 w',
                 'f = g + w·h。w=1 是标准 A*，w 越大越信 h。'
                 '同一张 18% 障碍地图、同一个起终点。')
    x0, y0, x1, y1 = 150, y + 90, 990, y + 470
    ws = [r['weight'] for r in rows]
    px, py = axes(fig, x0, y0, x1, y1, (1.0, 5.0), (0, 340),
                  [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                  [0, 100, 200, 300], 'w', '展开格子数')
    pts = [(px(r['weight']), py(min(r['expansions'], 300))) for r in rows]
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=TEAL, width=5)
    for (X, Y), r in zip(pts, rows):
        fig.circle(X, Y, 9, fill=TEAL, outline=TEAL)
        if r['weight'] == 1.0:
            fig.text((X + 20, Y - 24), str(r['expansions']), 38, color=TEAL)
        elif r['weight'] in (1.25, 2.0, 5.0):
            fig.text((X, Y - 40), str(r['expansions']), 38, color=TEAL,
                     anchor='ma')
    y = y1 + 96
    y = note(fig, y, 'w 只从 1 提到 1.25，展开数就从 %d 掉到 %d；'
                     '再往上几乎不动，一直是 %d 左右。'
                     % (rows[0]['expansions'], rows[1]['expansions'],
                        rows[-1]['expansions']))
    y = note(fig, y, '代价那边：最优 %.4f，w≥1.25 都是 %.4f，多付 %.2f%%。'
                     '这一次运气好，多付得很少；但没有任何东西保证它少。'
                     % (s['optimal'], rows[1]['cost'],
                        100 * (rows[1]['ratio'] - 1)))
    save(fig, '08-weight-sweep.png', 'w 从 1 加到 5 时展开数的变化')


# ---------------------------------------------------------------- 图 09

def fig09():
    fig, y = new(9, '两笔账：省了多少格子，多付多少路',
                 '同样的起终点、同样的 h（八方向 octile），只改 w。'
                 '代价是实际走出来的路长，比一行是相对最优路的比例。')
    for tag, key, title in (('18', 'map18', '18% 障碍'), ('25', 'map25', '25% 障碍')):
        g = R[key]
        fig.text((52, y), title, 40, bold=True, color=INK)
        y += 62
        rows = []
        for name in ('dijkstra', 'astar', 'w=2', 'w=3'):
            r = variant(g, name) if name in [x['name'] for x in g['rows']] else None
            label = 'Dijkstra' if name == 'dijkstra' else ('A*' if name == 'astar' else name)
            rows.append([(label, INK, False),
                         (str(r['expansions']), INK, False),
                         ('%.4f' % r['cost'], INK, False),
                         ('%.2f×' % r['ratio'], RED if r['ratio'] > 1.0001 else INK, False),
                         ('%d' % r['open_max'], INK_SOFT, False)])
        cols = [(60, 'la'), (300, 'ra'), (470, 'ra'), (660, 'ra'), (830, 'ra')]
        rows.insert(0, [('配置', GRAY, True), ('展开', GRAY, True),
                        ('代价', GRAY, True), ('相对最优', GRAY, True),
                        ('开表峰值', GRAY, True)])
        y = table(fig, y, cols, rows, row_h=64)
    y = note(fig, y, 'A* 的展开数只有 Dijkstra 的三分之一到一半，'
                     '开表峰值反而更高——它一次就把邻居全塞进去。')
    save(fig, '09-two-bills.png', '两种地图上四种配置的展开数、代价与开表峰值')


# ---------------------------------------------------------------- 图 10

def fig10():
    g = R['closed_set']
    fig, y = new(10, '高估一步，就错到底',
                 '8×8，八方向，斜走也算 1 步。'
                 '红色是 h 用欧氏距离走出来的路，青色是最优路。')
    cell = 96
    x0, ty = 96, y + 40
    draw_grid(fig, g, x0, ty, cell, path=None)
    bad = g['variants'][0]
    good = g['variants'][2]
    for row, color, off in ((bad, RED, -8), (good, TEAL, 8)):
        pts = [(x0 + c[0] * cell + cell / 2 + off,
                ty + c[1] * cell + cell / 2 + off) for c in row['path']]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=color, width=5)
    marked(fig, g, cell, x0, ty, color=GREEN)
    y = ty + 8 * cell + 20
    y = legend(fig, y, [(RED, '欧氏：%.1f' % bad['cost']),
                        (TEAL, '切比雪夫：%.1f' % good['cost']),
                        (INK, '障碍')], step=250)
    y = note(fig, y, '最优是 %.1f，欧氏给出 %.1f。允许重开闭表也是 %.1f——'
                     '重开能补的是一致性，补不了高估。'
                     % (g['optimal'], bad['cost'], g['variants'][1]['cost']))
    y = note(fig, y, '欧氏距离在斜走同价的格子上会高估：'
                     '起点到终点直线 9.9，实际一步一步只需 %d 步。'
                     % int(g['optimal']))
    save(fig, '10-overestimate.png', '欧氏启发式在斜走同价网格上给出次优路径')


# ---------------------------------------------------------------- 图 11

def fig11():
    c = R['consistency']
    fig, y = new(11, '一致性：h 掉下去不能比一步还快',
                 '检查每条边：h(u) − h(v) 有没有超过这一步的代价。'
                 '下面两个数是一批地图里超出的最大值，0 表示一次都没超。')
    rows = [[('启发式', GRAY, True), ('斜走代价 √2', GRAY, True),
             ('斜走代价 1', GRAY, True)]]
    for a, b in zip(c['sqrt2_grid'], c['same_price_grid']):
        rows.append([(a['name'], INK, False),
                     ('%.3f' % a['worst_excess'], INK, False),
                     ('%.3f' % b['worst_excess'],
                      RED if b['worst_excess'] > 0 else INK, False)])
    cols = [(80, 'la'), (480, 'ra'), (900, 'ra')]
    y = table(fig, y, cols, rows, row_h=76)
    y = note(fig, y, '斜走按 √2 计价时，三种 h 都满足；'
                     '斜走只算 1 的时候，八方向的 octile 与欧氏都超出了 %.3f，'
                     '正好是 √2 − 1。' % c['same_price_grid'][0]['worst_excess'])
    y = note(fig, y, 'h 的定义里如果默认「斜走贵一点」，而地图上并不贵，'
                     '它就不是在估距离，而是在猜规则。')
    save(fig, '11-consistency.png', '三种启发式在两种斜走定价下的一致性检查')


# ---------------------------------------------------------------- 图 12

def fig12():
    fig, y = new(12, '三句话')
    items = [
        'A* 不会自己变聪明：空地上一格都省不下，因为所有 f 相等。'
        '省下来的格子数取决于地图和 h，不取决于算法名字。',
        'h 必须不高估，否则第一次弹出的终点就可能是错的，重开也救不回来。'
        'w>1 是主动放弃最优性，换来几倍的展开数差距。',
        'A* 省的是时间不是内存：开表峰值常常比 Dijkstra 还高。'
        '真正卡住游戏的时候，往往卡在这里。',
    ]
    y = bullets(fig, y + 30, items)
    save(fig, '12-takeaways.png', '全文三句话')


def cover():
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill=BG, outline=None)
    fig.rect(0, 0, 1080, 12, fill=TEAL, outline=None)
    fig.text((80, 120), 'A* 为什么会', 104, bold=True)
    fig.text((80, 250), '白忙一场', 104, bold=True)
    fig.text((80, 400), 'g + h 的两张账，和它保证不了的事', 42, color=INK_SOFT)
    fig.text((80, 500), '空地 6×6：Dijkstra 36 格，A* 也 36 格', 42, color=INK)
    fig.text((80, 570), '八方向：同一个起终点，A* 只碰 6 格', 42, color=INK)
    fig.text((80, 640), '33×33 有障碍：906 格 → 278 格', 42, color=INK)
    fig.text((80, 710), '代价 51.11 与 51.11，一个不差', 42, color=INK)
    fig.text((80, 800), '斜走同价时，欧氏距离给出 10', 48, color=RED)
    fig.text((80, 868), '最优是 9', 48, color=RED)
    fig.text((80, 1000), '2027-03-08', 40, color=GRAY)
    fig.trim(margin=60)
    fig.im = fig.im.crop((0, 0, 1080, 1080))
    fig.im.save(ART / 'cover.png')
    print('   cover.png', (ART / 'cover.png').stat().st_size, 'bytes')


def main():
    for fn in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08,
               fig09, fig10, fig11, fig12):
        fn()
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, indent=1, ensure_ascii=False))
    print('wrote', HERE / 'figure-metadata.json', len(META), 'figures')
    cover()


if __name__ == '__main__':
    main()
