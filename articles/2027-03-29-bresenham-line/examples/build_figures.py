#!/usr/bin/env python3
"""《一条直线怎么变成一串像素》的原创插图。MIT。

带数字的图都读 results.json，画图时不另算一遍公式。
"""
from __future__ import annotations

import json
import math
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
PALETTE.update({VIOLET})


# ---------------------------------------------------------------- 通用零件

def minus(s):
    return str(s).replace('-', '−')


def new(n, title, sub=None):
    fig = Fig(900)
    fig.text((44, 26), title, 46, bold=True)
    fig.text((1018, 32), '图 %02d' % n, 40, color=GRAY, anchor='ra')
    y = 112
    if sub:
        y += int(fig.wrap((44, y), sub, 40, 974, color=INK_SOFT) * 40 * 1.35) + 20
    return fig, y


def note(fig, y, text, size=40, color=INK_SOFT):
    return y + int(fig.wrap((44, y), text, 40, 974, color=color) * 40 * 1.35) + 16


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
         xtick_labels=None, ytick_labels=None, xlog=False, ylog=False):
    fx = math.log10 if xlog else (lambda v: v)
    fy = math.log10 if ylog else (lambda v: v)

    def px(v):
        return x0 + (fx(v) - fx(xr[0])) / (fx(xr[1]) - fx(xr[0])) * (x1 - x0)

    def py(v):
        return y1 - (fy(v) - fy(yr[0])) / (fy(yr[1]) - fy(yr[0])) * (y1 - y0)

    for t in yticks:
        fig.line((x0, py(t)), (x1, py(t)), color=LIGHT, width=2)
    for t in xticks:
        fig.line((px(t), y0), (px(t), y1), color=LIGHT, width=2)
    fig.line((x0, y1), (x1, y1), color=INK, width=3)
    fig.line((x0, y0), (x0, y1), color=INK, width=3)
    for t, lab in zip(xticks, xtick_labels or [str(t) for t in xticks]):
        fig.text((px(t), y1 + 14), lab, 38, color=INK_SOFT, anchor='ma')
    for t, lab in zip(yticks, ytick_labels or [str(t) for t in yticks]):
        fig.text((x0 - 16, py(t) - 22), lab, 38, color=INK_SOFT, anchor='ra')
    if xlabel:
        fig.text((x1, y1 + 66), xlabel, 38, color=INK_SOFT, anchor='ra')
    if ylabel:
        fig.text((x0, y0 - 62), ylabel, 38, color=INK_SOFT, anchor='la')
    return px, py


def series(fig, pts, color, width=5, r=9):
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=color, width=width)
    for p in pts:
        fig.circle(p[0], p[1], r, fill=color, outline=color)


def dashed(fig, pts, color, width=4):
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=color, width=width, dash=14)


def bars(fig, x0, x1, ybase, h, items, width=None, label_size=38, colors=None):
    """items: [(标签, 高度分数 0..1, 颜色)]，从左到右排。"""
    n = len(items)
    step = (x1 - x0) / n
    w = width or step * 0.62
    for i, (lab, frac, color) in enumerate(items):
        cx = x0 + step * (i + 0.5)
        top = ybase - max(3, frac * h)
        fig.rect(cx - w / 2, top, cx + w / 2, ybase, fill=color, outline=None, radius=4)
        if lab:
            fig.text((cx, ybase + 10), lab, label_size, color=INK_SOFT, anchor='ma')
    fig.line((x0, ybase), (x1, ybase), color=INK, width=3)


# ---------------------------------------------------------------- 图 01

def fig01():
    fig, y = new(1, '手算一条 10 乘 4 的线',
                 '每列点亮一个像素，误差项 D 决定这一列要不要往下挪一格')
    cols = [(70, 'la'), (300, 'ra'), (470, 'ra'), (760, 'la')]
    rows = [[('k', INK_SOFT, False), ('D', INK_SOFT, False), ('判据', INK_SOFT, False),
             ('画在', INK_SOFT, False)]]
    for k, d, mark in R['hand']['steps'][:11]:
        yv = R['hand']['pixels'][k][1]
        rows.append([(str(k), INK, False), (minus(d), INK, False),
                     ('+1' if mark == 'y' else '·', RED if mark == 'y' else GRAY, False),
                     ('(%d, %d)' % (k, yv), INK, False)])
    y = table(fig, y, cols, rows, row_h=62)
    y += 24

    # 栅格：11 列 5 行
    cell = 74
    gx, gy = 88, y
    for j in range(5):
        for i in range(11):
            x = gx + i * cell
            yy = gy + (4 - j) * cell
            fig.rect(x, yy, x + cell, yy + cell, fill=WHITE, outline=LIGHT, width=2)
    # 理想线
    def gpx(k):
        return gx + (k + 0.5) * cell

    def gpy(v):
        return gy + (4.5 - v) * cell

    ideal = [(gpx(k) / 1.0, gpy(0.4 * k)) for k in range(11)]
    for i in range(11):
        x = gx + i * cell
        yy = gy + (4 - R['hand']['pixels'][i][1]) * cell
        fig.rect(x + 6, yy + 6, x + cell - 6, yy + cell - 6, fill=TINT_R, outline=None)
        fig.circle(x + cell / 2, yy + cell / 2, 11, fill=RED, outline=RED)
    dashed(fig, ideal, BLUE)
    fig.text((44, gy - 44), '理想线', 38, color=BLUE)
    fig.text((gx + 11 * cell + 12, gy + 2.5 * cell), 'y', 38, color=INK_SOFT)
    fig.text((gx, gy + 5 * cell + 14), 'x', 38, color=INK_SOFT)
    fig.text((gx + 11 * cell - 10, gy + 5 * cell + 14), '0..10', 38,
             color=INK_SOFT, anchor='ra')
    save(fig, '01-hand-line.png', '从 (0,0) 到 (10,4) 的 Bresenham 逐步取值与像素')


# ---------------------------------------------------------------- 图 02

def fig02():
    fig, y = new(2, 'D 每列走一步，走成一个锯齿',
                 '从 −2 起，每列加 2dy = 8；一旦越过 0 就减 2dx = 20 并往下一格')
    px, py = axes(fig, 150, y + 40, 980, y + 520, (-0.5, 10.5), (-22, 10),
                  [0, 2, 4, 6, 8, 10], [-20, -10, 0, 5],
                  '第几列', '误差项 D')
    fig.line((px(-0.5), py(0)), (px(10.5), py(0)), color=GRAY, width=3, dash=10)
    pts = [(px(k), py(d)) for (k, d, _) in R['hand']['steps']]
    series(fig, pts, RED, width=5, r=10)
    for (k, d, mark) in R['hand']['steps']:
        if mark == 'y':
            fig.text((px(k) + 16, py(d) - 40), '往下', 38, color=RED)
    y = y + 620
    y = note(fig, y, 'D 的符号就是判据：正数说明理想线已经越过这一格的中线，'
                    '该往下挪一格。它永远不会超过 2dy，也永远不会低于 −2dx。')
    save(fig, '02-error-term.png', '误差项 D 在 11 列上的取值')


# ---------------------------------------------------------------- 图 03

def fig03():
    fig, y = new(5, '同一个算法，两种量法',
                 '按整数坐标量，偏差处处不超过 0.5；按像素中心量，能到 1.5')
    px, py = axes(fig, 150, y + 40, 980, y + 460, (0, 1.0), (0, 1.6),
                  [0, 0.25, 0.5, 0.75, 1.0], [0, 0.5, 1.0, 1.5],
                  '斜率（Δy / Δx）', '最大偏差（像素）',
                  ['0', '1/4', '1/2', '3/4', '1'])
    fig.line((px(0), py(0.5)), (px(1.0), py(0.5)), color=BLUE, width=5)
    pts = [(px(s['slope']), py(s['integer'])) for s in R['slope_scan']]
    series(fig, pts, BLUE, width=4, r=5)
    pts = [(px(s['slope']), py(min(s['center'], 1.55))) for s in R['slope_scan']]
    series(fig, pts, RED, width=4, r=6)
    fig.text((px(0.02), py(0.56)), '整数坐标：0.5，一条直线', 38, color=BLUE)
    fig.text((px(0.30), py(1.18)), '像素中心：随斜率起伏', 38, color=RED)
    y += 620
    y = note(fig, y, '横轴是斜率，纵轴是 65 条线段（Δx = 64）里最大的那个偏差。'
                    '两条线量的是同一批像素，只是量的位置不同：一个在整数格点上，'
                    '一个在格子中心。中心比格点偏了半个格子，两端一起偏，就差出一个像素。')
    save(fig, '05-two-metrics.png', '两种偏差度量在 65 条斜率上的对比')


# ---------------------------------------------------------------- 图 04

def fig04():
    fig, y = new(3, '分歧只发生在偶数长度上',
                 '4000 条随机线段里，与四舍五入不一致的条数按主轴长度分组')
    rows = [r for r in R['compare']['by_major'] if 3 <= r['major'] <= 20]
    px, py = axes(fig, 150, y + 40, 980, y + 470, (0.5, len(rows) + 0.5),
                  (0, 1.0), [], [], '主轴长度', '分歧占比')
    xt, xl = [], []
    for i, r in enumerate(rows):
        frac = r['diff'] / float(r['n'])
        color = RED if r['major'] % 2 == 0 else LIGHT
        cx = px(i + 1)
        top = py(frac)
        fig.rect(cx - 16, top, cx + 16, py(0), fill=color, outline=None, radius=4)
        if r['major'] % 2 == 0 and frac > 0.02:
            fig.text((cx, top - 46), '%d' % round(frac * 100), 38, color=RED, anchor='ma')
        xt.append(i + 1)
        xl.append(str(r['major']) if r['major'] % 2 == 0 else '')
    fig.line((px(0.5), py(0)), (px(len(rows) + 0.5), py(0)), color=INK, width=3)
    for i, (t, lab) in enumerate(zip(xt, xl)):
        if lab:
            fig.text((px(t), py(0) + 14), lab, 38, color=INK_SOFT, anchor='ma')
    y = y + 600
    y = note(fig, y, '灰色柱子是奇数长度，全部为 0——一条长度是奇数的线，'
                    '理想值永远落不到正中间，四舍五入和 Bresenham 就不会吵。'
                    '偶数长度里大约有 %d%% 会差一个像素。' % round(
                        R['compare']['differing_share'] * 100))
    save(fig, '03-diff-by-length.png', '与四舍五入的分歧按主轴长度分布')


# ---------------------------------------------------------------- 图 05

def fig05():
    fig, y = new(4, '差的那一个像素长什么样',
                 '左：Bresenham 选的；右：四舍五入选的。理想线正好穿过两条格线的交点')
    ex = R['compare']['examples'][0]
    ax, ay, bx, by = ex['seg']
    left = set(map(tuple, ex['bresenham_only']))
    right = set(map(tuple, ex['dda_only']))
    cell = 92
    for panel in range(2):
        gx = 120 + panel * 470
        gy = y + 60
        # 取分歧像素周围 3x3 的窗口
        base = (sorted(left) + sorted(right))[0]
        for j in range(-1, 2):
            for i in range(-1, 2):
                cx = base[0] + i
                cy = base[1] + j
                x = gx + (i + 1) * cell
                yy = gy + (1 - j) * cell
                fig.rect(x, yy, x + cell, yy + cell, fill=WHITE, outline=LIGHT, width=2)
                fig.circle(x + cell / 2, yy + cell / 2, 10, fill=GRAY, outline=GRAY)
        # 理想线在窗口里的一段（用参数式画折线）
        pts = []
        for i in range(-12, 13):
            t = i / 12.0
            xv = ax + t * (bx - ax)
            yv = ay + t * (by - ay)
            fx = gx + (xv + 0.5 - base[0] + 1) * cell
            fy = gy + (1.5 - (yv - base[1])) * cell
            if gx - 40 <= fx <= gx + 3 * cell + 40 and gy - 40 <= fy <= gy + 3 * cell + 40:
                pts.append((fx, fy))
        if len(pts) > 1:
            dashed(fig, pts, BLUE)
        pick = left if panel == 0 else right
        color = RED if panel == 0 else TEAL
        for (qx, qy) in sorted(pick):
            i, j = qx - base[0], qy - base[1]
            x = gx + (i + 1) * cell
            yy = gy + (1 - j) * cell
            fig.rect(x + 8, yy + 8, x + cell - 8, yy + cell - 8, fill=color, outline=None)
            fig.circle(x + cell / 2, yy + cell / 2, 12, fill=WHITE, outline=WHITE)
        fig.text((gx, gy - 46), 'Bresenham' if panel == 0 else '四舍五入', 40,
                 bold=True, color=RED if panel == 0 else TEAL)
    y += 60 + 3 * cell + 40
    y = note(fig, y, '这一段是 (%d, %d) 到 (%d, %d)。理想线在某一列正好穿过两条格线的交点，'
                    '两边一样远，于是两个实现各挑一个。整条线上只差这一处。'
             % (ax, ay, bx, by))
    save(fig, '04-one-pixel-diff.png', 'Bresenham 与四舍五入在一个平局像素上的分歧')


# ---------------------------------------------------------------- 图 06

def fig06():
    fig, y = new(6, '把同一条线反过来画',
                 '600 条线段里，同一个端点先画和后画，有 %d%% 得到不同的像素' % round(
                     R['reverse']['differ_share'] * 100))
    byd = [r for r in R['reverse']['by_delta'] if r['delta'] <= 10]
    items = [('%d' % r['delta'], r['n'] / 120.0, RED if r['delta'] == 1 else TEAL)
             for r in byd]
    px0, px1 = 150, 980
    ybase = y + 460
    bars(fig, px0, px1, ybase, 340, items, width=44)
    fig.text((px0, ybase + 86), '差几个像素（柱子上方的数字是条数）', 38, color=INK_SOFT)
    idx = 0
    for r in byd:
        cx = px0 + (px1 - px0) / len(items) * (idx + 0.5)
        fig.text((cx, ybase - max(3, r['n'] / 120.0 * 340) - 44), str(r['n']), 38,
                 color=RED if r['delta'] == 1 else TEAL, anchor='ma')
        idx += 1
    y = ybase + 130
    y = note(fig, y, '差值 1 的最多（%d 条），但也有差到 41 个像素的：斜率正好是 1/2 的那种线，'
                    '每两列就是一个平局，反向之后整套台阶错开半格。'
             % [r['n'] for r in R['reverse']['by_delta'] if r['delta'] == 1][0])
    save(fig, '06-reversed.png', '反向绘制时像素差异的分布')


# ---------------------------------------------------------------- 图 07

def fig07():
    fig, y = new(7, '圆只用第一八分圆算一遍',
                 'r = 13：只算 0 到 45 度那 %d 个点，其余七段靠交换坐标和变号得到'
                 % len(R['octant']['first']))
    r = R['octant']['r']
    cell = 26
    gx, gy = 480, y + 30
    pts = R['octant']['first']
    # 八个镜像区的颜色
    oct_colors = [TEAL, BLUE, AMBER, VIOLET, GREEN, RED, GRAY, INK_SOFT]
    drawn = {}
    for (x, yv) in pts:
        drawn[(x, yv)] = TEAL

    def plot(xv, yv, color, solid=True):
        cx = gx + xv * cell
        cy = gy + (26 - yv) * cell
        fig.rect(cx - cell / 2 + 2, cy - cell / 2 + 2, cx + cell / 2 - 2,
                 cy + cell / 2 - 2, fill=color if solid else WHITE,
                 outline=color if not solid else None, width=2)

    for (x, yv) in pts:
        for sx in (1, -1):
            for sy in (1, -1):
                plot(sx * x, sy * yv, TEAL)
                plot(sx * yv, sy * x, BLUE if (sx * sy) > 0 else AMBER)
    for (x, yv) in pts:
        plot(x, yv, RED)
    fig.text((gx - 14, gy + 26 * cell), '第一八分圆（红）加 7 次镜像', 38, color=INK_SOFT)
    # 45 度分隔线
    fig.line((gx, gy + 26 * cell), (gx + 26 * cell, gy), color=GRAY, width=3, dash=12)
    y = gy + 26 * cell + 76
    y = note(fig, y, '判定量从 d = 1 − r 出发，每步只加 2x + 1 或者 2(x − y) + 1：'
                    '没有乘法，没有开方。蓝色和琥珀色是两组镜像，红色是第一八分圆本身。')
    y = note(fig, y, 'r = %d 时全圆 %d 个像素，其中只有 %d 个是真算出来的，'
                    '其余 %d 个靠交换坐标和变号得到。'
             % (r, R['octant']['total'], len(pts),
                R['octant']['total'] - len(pts)))
    save(fig, '07-midpoint-circle.png', 'r = 13 的中点圆像素与八路镜像')


# ---------------------------------------------------------------- 图 08

def fig08():
    fig, y = new(8, '圆画出来比周长短一点',
                 '中点圆的像素数除以 2πr，r 从 3 到 64')
    px, py = axes(fig, 150, y + 40, 980, y + 470, (2, 65), (0.8, 0.98),
                  [10, 20, 30, 40, 50, 60], [0.8, 0.85, 0.9, 0.95],
                  '半径 r', '像素数 / 2πr')
    pts = [(px(r['r']), py(r['ratio'])) for r in R['circle']]
    series(fig, pts, TEAL, width=4, r=7)
    fig.line((px(2), py(0.9)), (px(65), py(0.9)), color=GRAY, width=3, dash=10)
    fig.text((px(46), py(0.9) - 44), '0.90', 38, color=GRAY)
    y += 610
    y = note(fig, y, '一个像素宽的数字圆并不是「周长的像素数」：8 连通的一步顶 √2 个像素，'
                    '所以比值稳定在 0.90 附近，包围盒的对角线也帮不上忙。'
                    '径向误差最大 %s 像素（r = 64）。'
             % minus('%.2f' % max(r['max_radial_error'] for r in R['circle'])))
    save(fig, '08-circle-count.png', '中点圆像素数与周长的比值随半径变化')


# ---------------------------------------------------------------- 图 09

def fig09():
    fig, y = new(9, '一条线，两种画法',
                 '上：Bresenham 每列一个像素，非黑即白。下：Wu 1991，按覆盖比例上灰度')
    seg = R['wu']['seg']
    x0, y0, x1, y1 = seg
    cell = 68
    gx, gy = 124, y + 40
    ncol = x1 - x0 + 1
    nrow = y1 - y0 + 3
    for panel in range(2):
        oy = gy + panel * (nrow * cell + 96)
        fig.text((44, oy - 6), 'Bresenham 1965' if panel == 0 else 'Wu 1991', 40,
                 bold=True, color=RED if panel == 0 else AMBER)
        for j in range(nrow):
            for i in range(ncol):
                x = gx + i * cell
                yy = oy + (nrow - 1 - j) * cell
                fig.rect(x, yy, x + cell, yy + cell, fill=WHITE, outline=LIGHT, width=2)
    bres = set(map(tuple, R['wu']['bresenham']))
    for (qx, qy) in sorted(bres):
        i, j = qx - x0, qy - y0
        x = gx + i * cell
        yy = gy + (nrow - 1 - j) * cell
        fig.rect(x + 4, yy + 4, x + cell - 4, yy + cell - 4, fill=RED, outline=None)
    oy = gy + nrow * cell + 96
    for (qx, qy, cov) in R['wu']['pixels']:
        if cov == 0:
            continue
        i, j = qx - x0, qy - y0
        if not (0 <= i < ncol and 0 <= j < nrow):
            continue
        x = gx + i * cell
        yy = oy + (nrow - 1 - j) * cell
        # 覆盖度映射到灰度
        v = 255 - int(230 * cov / 255.0)
        shade = '#%02x%02x%02x' % (v, v, v)
        PALETTE.add(shade)
        fig.rect(x + 4, yy + 4, x + cell - 4, yy + cell - 4, fill=shade, outline=None)
    y = oy + nrow * cell + 40
    y = note(fig, y, '同一段 (0,0) 到 (12,5)。Bresenham 只在每列落一个像素；'
                    'Wu 在每列落两个，深浅加起来正好是一整格。'
                    '代价是每像素要多算一次取整和一次乘法。')
    save(fig, '09-antialias.png', 'Bresenham 与 Wu 抗锯齿画线的对照')


# ---------------------------------------------------------------- 图 10

def fig10():
    fig, y = new(10, '三句话')
    items = [
        '一步只做加法和比较：误差项 D 记住「理想线比当前像素高多少」，够半格就往下挪，'
        '不需要除法，也不会累积浮点误差。',
        '偏差不超过半格，但那只在整数格点上成立；按像素中心量会到 1.5 格，'
        '同一条线反过来画也可能得出不同的像素。',
        '圆只算一个八分圆，其余靠镜像；这条思路一直用到今天的直线与多边形栅格化规则里，'
        '因为 GPU 也要保证相邻三角形共享边时不留缝。',
    ]
    y = bullets(fig, y + 20, items, accent=RED, size=40)
    save(fig, '10-takeaways.png', '三条结论')


# ---------------------------------------------------------------- 封面

def cover():
    fig = Fig(1080, width=1080)
    fig.text((60, 150), '一条直线', 104, bold=True)
    fig.text((60, 280), '怎么变成一串像素', 104, bold=True)
    fig.text((60, 470), '1965 年，IBM 的绘图仪需要一个只用加法', 40, color=INK_SOFT)
    fig.text((60, 528), '就能把线段变成打点命令的办法', 40, color=INK_SOFT)
    rows = [('10 乘 4 的线', '11 个像素，D 从 −2 起跳'),
            ('4000 条随机线段', '23% 与四舍五入差一个像素'),
            ('r = 13 的圆', '72 个像素，只算 10 个点')]
    y = 660
    for a, b in rows:
        fig.rect(60, y - 10, 76, y + 26, fill=RED, outline=None, radius=4)
        fig.text((96, y - 8), a, 40, bold=True, color=INK)
        fig.text((96 + fig.width_of(a, 40, True) + 28, y - 8), b, 38, color=INK_SOFT)
        y += 82
    fig.text((1020, 993), '2027-03-29', 38, color=GRAY, anchor='ra')
    row = fig.save(ART / 'cover.png', '文章封面')
    META.append(row)
    print('   cover.png', row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def main():
    for f in (fig01, fig02, fig04, fig05, fig03, fig06, fig07, fig08, fig09, fig10):
        f()
    cover()
    (HERE / 'figure-metadata.json').write_text(json.dumps(META, indent=1))
    print('wrote', HERE / 'figure-metadata.json', len(META), 'figures')


if __name__ == '__main__':
    main()
