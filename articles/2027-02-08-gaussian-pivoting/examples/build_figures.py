#!/usr/bin/env python3
"""主元一文的原创教学插图。MIT。

带数字的图全部读 results.json；矩阵格子里的小数都是从账本里原样取的，
不在画图时另算一遍。
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import ImageFont

from figkit import (Fig, PALETTE, BG, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER,
                    RED, GRAY, LIGHT, PALE, GREEN, CREAM, TINT_T, TINT_B,
                    TINT_A, TINT_R, TINT_G)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []

MONO_PATH = '/System/Library/Fonts/Menlo.ttc'
_MONO = {}
VIOLET = '#5b4b8a'
PALETTE.update({VIOLET})


def mono(fig, xy, s, size=38, color=INK, anchor='la'):
    if size not in _MONO:
        _MONO[size] = ImageFont.truetype(MONO_PATH, size, index=0)
    f = _MONO[size]
    bb = fig.d.textbbox(xy, s, font=f, anchor=anchor)
    fig.d.text(xy, s, font=f, fill=color, anchor=anchor)
    fig.labels.append(dict(s=s, size=size, bold=False, bbox=bb, inside=None,
                           anchor=anchor, allow_overlap=False, tag=None,
                           skip_audit=False))
    fig.min_px = min(fig.min_px, size)
    return bb


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


def legend(fig, y, items, x0=52, step=300):
    x = x0
    for color, text in items:
        fig.rect(x, y + 4, x + 30, y + 34, fill=color, outline=None, radius=6)
        fig.text((x + 44, y - 2), text, 38, color=INK)
        x += step
    return y + 52


def card(fig, name, x0, y0, x1, y1, head, lines, accent, size=40, head_size=42):
    fig.box(name, x0, y0, x1, y1, fill=WHITE, outline=accent)
    fig.text((x0 + 24, y0 + 18), head, head_size, bold=True, color=accent,
             inside=name)
    y = y0 + 24 + head_size * 1.85
    for ln in lines:
        y += int(fig.wrap((x0 + 24, y), ln, size, (x1 - x0) - 48, color=INK,
                          inside=name) * size * 1.35) + 6
    return y


def axes(fig, x0, y0, x1, y1, xr, yr, xticks, yticks, xlabel, ylabel,
         fx=None, fy=None):
    """一根 x 轴一根 y 轴；返回 (fx, fy) 两个数据到像素的函数。"""
    def px(v):
        return x0 + (v - xr[0]) / (xr[1] - xr[0]) * (x1 - x0)

    def py(v):
        return y1 - (v - yr[0]) / (yr[1] - yr[0]) * (y1 - y0)

    for t in yticks:
        fig.line((x0, py(t)), (x1, py(t)), color=LIGHT, width=2)
    fig.line((x0, y1), (x1, y1), color=INK, width=3)
    fig.line((x0, y0), (x0, y1), color=INK, width=3)
    for t in xticks:
        fig.text((px(t), y1 + 14), str(t), 38, color=INK_SOFT, anchor='ma')
    for t in yticks:
        fig.text((x0 - 16, py(t) - 22), str(t), 38, color=INK_SOFT, anchor='ra')
    fig.text((x1, y1 + 66), xlabel, 38, color=INK_SOFT, anchor='ra')
    fig.text((x0 - 16, y0 - 54), ylabel, 38, color=INK_SOFT, anchor='la')
    return px, py


# ---------------------------------------------------------------- 图 01

def fig02():
    fig, y = fig_new1 = new(
        1, '两个方程，就是两条线',
        '每个方程在平面上画出一条直线，满足两个方程的 (x, y) 只有两个线同时经过的那个点。'
        ' 解方程组的几何意思就是找交点。')
    fig, y = fig_new1
    x0, x1 = 150, 900
    ytop, ybot = y + 30, y + 560
    px, py = axes(fig, x0, ytop, x1, ybot, (-1, 5), (-2, 5),
                  [-1, 0, 1, 2, 3, 4, 5], [-2, 0, 2, 4], 'x', 'y')

    def clip(f, g, fmin, fmax):
        pts = []
        for i in range(201):
            v = fmin + (fmax - fmin) * i / 200
            w = f(v)
            if g(w):
                pts.append((px(v), py(w)))
        return pts

    inside = lambda w: -2.3 <= w <= 5.3
    for coeff, col in (((1, 1, 4), BLUE), ((2, -1, 2), AMBER)):
        a, b, c = coeff
        pts = clip(lambda v: (c - a * v) / b, inside, -1.4, 5.4)
        for p, q in zip(pts, pts[1:]):
            fig.line(p, q, color=col, width=5)
    fig.circle(px(2), py(2), 12, fill=RED, outline=RED)
    fig.text((px(2) + 26, py(2) - 60), '交点 (2, 2)', 42, bold=True, color=RED)
    fig.text((px(4.4), py(4.4) - 52), 'x + y = 4', 42, bold=True, color=BLUE,
             anchor='ma')
    fig.text((px(3.1), py(-0.5)), '2x − y = 2', 42, bold=True, color=AMBER,
             anchor='ma')
    y = fig_new1[1] + 660
    y = note(fig, y, '两条线不平行，就有一个交点；平行（或者重合）时，方程组没有唯一解，'
                     '这一点决定了后面「除以零」意味着什么。')
    save(fig, '02-two-lines.png', '两个方程在平面上是两条线，解是交点')


# ---------------------------------------------------------------- 图 02

def fig03():
    fig, y = new(
        2, '消元：把第二条线拉平',
        '用第一个方程乘一个数，从第二个方程里减掉，第二个方程里的 x 就消失了。'
        ' 几何上，这条线绕着交点被「压」成一条水平线。')
    x0, x1 = 150, 880
    ytop, ybot = y + 30, y + 550
    px, py = axes(fig, x0, ytop, x1, ybot, (-1, 5), (-2, 5),
                  [-1, 0, 1, 2, 3, 4, 5], [-2, 0, 2, 4], 'x', 'y')

    def seg(a, b, c, col, width, dash=None):
        pts = []
        for v in (x for x in [(-1.3 + 6.7 * i / 200) for i in range(201)]):
            w = (c - a * v) / b
            if -2.3 <= w <= 5.3:
                pts.append((px(v), py(w)))
        for p, q in zip(pts, pts[1:]):
            fig.line(p, q, color=col, width=width, dash=dash)

    seg(1, 1, 4, BLUE, 5)
    seg(2, -1, 2, AMBER, 5, dash=14)
    fig.text((px(4.35), py(4.35) - 52), 'x + y = 4', 42, bold=True, color=BLUE,
             anchor='ma')
    fig.text((px(3.4), py(-0.9)), '2x − y = 2', 42, color=AMBER, anchor='ma')
    fig.circle(px(2), py(2), 12, fill=RED, outline=RED)
    fig.arrow((px(2.55), py(0.4)), (px(2.55), py(1.86)), color=GREEN, width=5,
              head=16)
    fig.text((px(2.72), py(1.1)), '减去 2 × 第一条', 38, color=GREEN)
    fig.line((px(-0.2), py(2)), (px(4.9), py(2)), color=GREEN, width=6)
    fig.text((px(4.7), py(2) + 10), '−3y = −6', 42, bold=True, color=GREEN,
             anchor='ma')
    y = ybot + 110
    y = note(fig, y, '交点没动，因为「一条线减去另一条线的若干倍」得到的线仍然经过同一个交点。'
                     ' 方程组变成「一条斜线 + 一条水平线」，y 立刻就能读出来：y = 2。')
    save(fig, '03-eliminate.png', '一次消元的几何效果：第二条线绕交点变成水平线')


# ---------------------------------------------------------------- 图 03

def _matrix(fig, x, y, rows, cols, cell=112, hl=None, hl_color=TINT_A,
            row_labels=None, label_color=GRAY):
    """画一个带方括号的矩阵。rows: [[str]]，最后一列可以是右端项。"""
    n = len(rows)
    h = cell * n
    w = cell * len(rows[0])
    fig.line((x - 14, y), (x - 14, y + h), color=INK, width=3)
    fig.line((x - 14, y), (x - 4, y), color=INK, width=3)
    fig.line((x - 14, y + h), (x - 4, y + h), color=INK, width=3)
    fig.line((x + w + 14, y), (x + w + 14, y + h), color=INK, width=3)
    fig.line((x + w + 14, y), (x + w + 4, y), color=INK, width=3)
    fig.line((x + w + 14, y + h), (x + w + 4, y + h), color=INK, width=3)
    for i, row in enumerate(rows):
        for j, cell_text in enumerate(row):
            cx = x + j * cell + cell / 2
            cy = y + i * cell + cell / 2
            if hl and (i, j) in hl:
                fig.rect(x + j * cell + 4, y + i * cell + 4,
                         x + j * cell + cell - 4, y + i * cell + cell - 4,
                         fill=hl_color, outline=None, radius=8)
            mono(fig, (cx, cy - 24), cell_text, 42, anchor='ma')
    if row_labels:
        for i, lab in enumerate(row_labels):
            fig.text((x - 26, y + i * cell + cell / 2 - 20), lab, 36,
                     color=label_color, anchor='ra')
    return y + h


def fig04():
    st = R['toy']['steps']
    fig, y = new(4, '三阶方程组的消元账本',
                 '左边一列是三个方程，右边是右端项。每一步只做两个动作：挑一行当主元，'
                 '用它的倍数把下面几行的这一列清成 0。')
    cell = 96
    panels = [(0, '原始', None), (1, '第 1 步后', (1, 0)),
              (2, '第 2 步后', (2, 0))]
    A = [row + [b] for row, b in zip(R['toy']['A'], R['toy']['b'])]
    images = [A, st[0]['M'], st[1]['M']]
    xs = [110, 560]
    ys = [y + 30, y + 30 + cell * 3 + 150]
    labels = ['原始', '第 1 步后', '第 2 步后（上三角）']
    for i, M in enumerate(images):
        cx, cy = xs[i % 2], ys[i // 2]
        if i == 2:
            cx = xs[0] + 90
        _matrix(fig, cx, cy, M, None, cell=cell,
                hl={(0, 0)} if i == 1 else ({(0, 0), (1, 0), (1, 1)} if i == 2
                                            else {(1, 0)}))
        fig.text((cx, cy - 54), labels[i], 40, bold=True, color=INK_SOFT)
    y2 = ys[1] + cell * 3 + 70
    y2 = note(fig, y2, '第一步选 −3（第 2 行）当主元，因为第 1 个元素 2 不是 0、'
                       '但 −3 的绝对值更大；第二步在剩下的 1/3 和 5/3 里选 5/3。')
    save(fig, '04-ledger.png', '三阶方程组的消元过程，每一步的矩阵形态')


# ---------------------------------------------------------------- 图 04

def fig05():
    fig, y = new(5, '回代：从最后一个未知数往回退',
                 '上三角矩阵的意思是：最后一个方程只有一个未知数，'
                 ' 解出来以后，把它代回上一个方程，再解一个，一直退到第一行。')
    st = R['toy']['steps']
    M = st[-1]['M']
    x = R['toy']['x']
    cell = 96
    top = y + 20
    _matrix(fig, 120, top, M, None, cell=cell, hl={(2, 2), (1, 1), (0, 0)})
    base = top + cell * 3 + 40
    steps = [
        ('1 · x3 = −1', 'x3 = −1', RED),
        ('1/3 · x2 + 1/3 · x3 = 2/3', 'x2 = 3', AMBER),
        ('−3x1 − x2 + 2x3 = −11', 'x1 = 2', GREEN),
    ]
    yy = base
    for formula, res, col in steps:
        fig.text((120, yy), formula, 38, color=INK)
        fig.text((1000, yy - 4), res, 46, bold=True, color=col, anchor='ra')
        yy += 80
    yy += 20
    yy = note(fig, yy, '解得 x1 = 2、x2 = 3、x3 = −1。代回原始三个方程，'
                       '右端正好是 8、−11、−3，没有一个分数剩下。')
    save(fig, '05-backsub.png', '回代过程：从上三角矩阵的最后一行往回解')


# ---------------------------------------------------------------- 图 05

def fig06():
    z = R['zero']
    fig, y = new(6, '主元是 0：除以零',
                 '轮到消去第 1 个未知数时，除数就是左上角那个元素。'
                 ' 它正好是 0，程序只会得到 inf 或者 NaN，而不是一个解。')
    top = y + 20
    rows = [r + [b] for r, b in zip(z['A'], z['b'])]
    _matrix(fig, 120, top, rows, None, cell=96, hl={(0, 0)}, hl_color=TINT_R)
    fig.text((520, top + 20), '第 1 个主元 = 0', 44, bold=True, color=RED)
    fig.text((520, top + 96), '乘数 = 1 / 0', 40, color=INK)
    fig.text((520, top + 156), '程序里是 inf 或 NaN', 40, color=RED)
    fig.text((520, top + 216), '手算时是「除不下去」', 40, color=INK_SOFT)

    y2 = top + 96 * 3 + 120
    y2 = note(fig, y2, '这组方程有唯一解：x1 = 1、x2 = 1、x3 = 2。问题不在题目，'
                       '在「拿哪一行当主元」这个动作上。')
    save(fig, '06-zero-pivot.png', '主元为零时消元无法继续，而方程本身有解')


# ---------------------------------------------------------------- 图 06

def fig07():
    z = R['zero']
    fig, y = new(7, '换一行，就换了一个除数',
                 '交换两个方程的顺序，方程组一点没变。但左上角的元素从 0 变成了 1，'
                 ' 除法又能做了。')
    top = y + 20
    rows = [r + [b] for r, b in zip(z['A'], z['b'])]
    swapped = [rows[1], rows[0], rows[2]]
    _matrix(fig, 90, top, rows, None, cell=92, hl={(0, 0)}, hl_color=TINT_R)
    fig.arrow((470, top + 120), (585, top + 120), color=TEAL, width=5, head=18)
    fig.text((528, top + 40), '交换前两行', 40, color=TEAL, anchor='ma')
    _matrix(fig, 640, top, swapped, None, cell=92, hl={(0, 0)}, hl_color=TINT_G)
    fig.text((640, top + 92 * 3 + 24), '第 1 个主元 = 1', 42, bold=True, color=GREEN)
    fig.text((90, top + 92 * 3 + 24), '第 1 个主元 = 0', 42, bold=True, color=RED)
    y2 = top + 92 * 3 + 110
    y2 = note(fig, y2, '换行后的解还是 x = (1, 1, 2)。行交换只改变方程在纸上的顺序，'
                       '不改变哪个 (x1, x2, x3) 同时满足三个方程。')
    save(fig, '07-row-swap.png', '行交换把 0 主元换成非零主元，解不变')


# ---------------------------------------------------------------- 图 07

def fig08():
    fig, y = new(8, '部分主元：每一步在剩下的列里挑最大的',
                 '不是随便换一行，而是拿当前列的绝对值最大的那一行当主元。'
                 ' 这样每个乘数的绝对值都不会超过 1。')
    cols = [('第 1 步：看第 1 列', ['2', '−3', '−2'], 1, '−3'),
            ('第 2 步：看第 2 列', ['1/3', '5/3'], 1, '5/3')]
    x = 90
    for title, vals, pick, pick_text in cols:
        fig.text((x, y + 6), title, 40, bold=True, color=INK_SOFT)
        yy = y + 80
        for i, v in enumerate(vals):
            name = 'b%d%d' % (x, i)
            fig.box(name, x, yy, x + 240, yy + 92,
                    fill=TINT_G if i == pick else WHITE,
                    outline=GREEN if i == pick else LIGHT)
            fig.text((x + 14, yy + 24), '第 %d 行' % (i + 1), 38, color=GRAY,
                     inside=name)
            mono(fig, (x + 226, yy + 20), v, 46, anchor='ra')
            yy += 108
        fig.text((x, yy + 12), '挑 %s 当主元' % pick_text, 42, bold=True,
                 color=GREEN)
        x += 460
    fig.text((90, y + 530), '乘数 = 被消掉的那个元素 ÷ 主元，绝对值 ≤ 1',
             42, bold=True, color=TEAL)
    note(fig, y + 600,
         '第一步选 −3（不是 2），第二步在 1/3 和 5/3 里选 5/3。'
         ' 两次都挑了最大的，剩下的乘数是 −2/3、2/3 和 −1/2。')
    save(fig, '08-partial-pivot.png', '部分主元：每列挑绝对值最大的元素')


# ---------------------------------------------------------------- 图 08

def fig09():
    fig, y = new(9, '乘数不超过 1，元素就只能翻倍',
                 '消元时被改写的元素是「自己 − 乘数 × 主元行」。乘数绝对值 ≤ 1，'
                 ' 每一步最多让一个元素长到原来的两倍。')
    cy = y + 60
    vals = [1, 2, 4, 8, 16, 32]
    x = 90
    for i, v in enumerate(vals):
        fig.box('c%d' % i, x, cy, x + 120, cy + 120, fill=WHITE, outline=INK_SOFT,
                radius=12)
        mono(fig, (x + 60, cy + 36), str(v), 44, anchor='ma')
        fig.text((x + 60, cy + 138), '第 %d 步' % (i + 1), 38, color=GRAY,
                 anchor='ma')
        if i < len(vals) - 1:
            fig.arrow((x + 124, cy + 60), (x + 150, cy + 60), color=GRAY,
                      width=3, head=10)
        x += 156
    fig.text((90, cy + 230), 'n 行矩阵最坏能长到 2 的 n−1 次方', 44, bold=True,
             color=RED)
    yy = note(fig, cy + 300,
              '这不是平均值，是上界：每一步只允许翻一倍，走 n−1 步就是 2 的 n−1 次方。'
              ' 双精度有 53 位有效数字，所以 n 到五十几时，这个上界本身就会把数字撑爆。')
    save(fig, '09-doubling.png', '乘数有界时元素增长的 2 倍链条')


# ---------------------------------------------------------------- 图 09

def fig10():
    wil = R['wilkinson']
    rnd = R['random_growth']
    fig, y = new(10, '两种矩阵，两种增长',
                 '红点是 Wilkinson 构造的矩阵：连部分主元也挡不住，'
                 '元素真的长到 2 的 n−1 次方。蓝点是 [−5, 5] 上的随机整数矩阵，'
                 '部分主元下增长只有几十倍。')
    x0, x1 = 170, 960
    ytop, ybot = y + 70, y + 520
    lo, hi = 0.0, 9.0

    def fx(n):
        return x0 + (math.log10(n) - 1.0) / (math.log10(400) - 1.0) * (x1 - x0)

    def fy(v):
        t = (math.log10(max(v, 1)) - lo) / (hi - lo)
        return ybot - max(0.0, min(t, 1.0)) * (ybot - ytop)

    for e in range(0, 10, 2):
        yy = fy(10 ** e)
        fig.line((x0, yy), (x1, yy), color=LIGHT, width=2)
        mono(fig, (x0 - 18, yy - 22), '1e%d' % e, 38, color=GRAY, anchor='ra')
    fig.line((x0, ybot), (x1, ybot), color=INK, width=3)
    for n in (10, 30, 100, 300):
        fig.text((fx(n), ybot + 14), str(n), 38, color=INK_SOFT, anchor='ma')
    fig.text((x1, ybot + 66), 'n（矩阵阶数）', 38, color=INK_SOFT, anchor='ra')
    fig.text((44, ytop - 56), '增长因子', 38, color=INK_SOFT)

    pts = [(fx(r['n']), fy(r['no_pivot'])) for r in wil]
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=RED, width=5)
    for p in pts:
        fig.circle(p[0], p[1], 8, fill=RED, outline=RED)
    fig.text((pts[-1][0] + 24, pts[-1][1] - 30), '2 的 n−1 次方',
             40, bold=True, color=RED)

    pts2 = [(fx(r['n']), fy(r['partial_median'])) for r in rnd]
    for a, b in zip(pts2, pts2[1:]):
        fig.line(a, b, color=BLUE, width=5)
    for p in pts2:
        fig.circle(p[0], p[1], 8, fill=BLUE, outline=BLUE)
    fig.text((pts2[-1][0] - 6, pts2[-1][1] - 54), '随机矩阵 + 部分主元',
             40, color=BLUE, anchor='ra')
    legend(fig, ybot + 108, [(RED, 'Wilkinson：2^(n−1)'), (BLUE, '随机整数：几十倍')],
           step=470)
    save(fig, '10-growth.png', 'Wilkinson 矩阵与随机矩阵的增长因子实测')


# ---------------------------------------------------------------- 图 10

def fig01():
    c = R['cancel']
    exact = c['exact']
    fig, y = new(1, '0.0001 当主元，三位有效数字就崩了',
                 '方程组 0.0001·x1 + x2 = 1，x1 + x2 = 2。真解是 x1 ≈ 1.0001、x2 ≈ 0.9999，'
                 ' 但用手算精度（三位有效数字）先消 x1，就要除以 0.0001。')
    rows = [
        [('做法', INK, True), ('x1', INK, True), ('x2', INK, True)],
        [('真解（分数）', INK, False), ('%.4f' % exact[0], GREEN, False),
         ('%.4f' % exact[1], GREEN, False)],
        [('先除 0.0001', INK, False),
         ('%.4f' % c['digits3_no_pivot'][0], RED, False),
         ('%.4f' % c['digits3_no_pivot'][1], RED, False)],
        [('先换行', INK, False),
         ('%.4f' % c['digits3_partial'][0], BLUE, False),
         ('%.4f' % c['digits3_partial'][1], BLUE, False)],
        [('双精度，不换行', INK, False),
         ('%.6f' % c['f64_no_pivot'][0], INK_SOFT, False),
         ('%.6f' % c['f64_no_pivot'][1], INK_SOFT, False)],
    ]
    y2 = y + 20
    y2 = table(fig, y2, [(54, 'la'), (480, 'la'), (780, 'la')], rows, row_h=86)
    fig.text((54, y2 + 6), '不换行时，1 − 10000 被舍成 −10000，', 40, color=INK)
    fig.text((54, y2 + 66), 'x2 变成 1.000，x1 于是算成 0。', 40, color=INK)
    fig.text((54, y2 + 126), '双精度下同一个毛病看着无害，只是因为它有 16 位。',
             40, color=INK_SOFT)
    save(fig, '01-small-pivot.png', '小主元把舍入误差放大：三位有效数字的例子')


# ---------------------------------------------------------------- 图 11

def fig12():
    H = R['hilbert']
    fig, y = new(12, '方程满足得极好，答案却错了',
                 'Hilbert 矩阵在 n = 10 时：把算出来的解代回去，残差小到 1e−17；'
                 ' 但解本身已经偏了 0.06%。')
    r = [h for h in H if h['n'] == 10][0]
    cy = y + 40
    fig.box('l', 60, cy, 500, cy + 260, fill=WHITE, outline=TEAL)
    fig.text((84, cy + 26), '残差 ‖Ax − b‖ / ‖b‖', 40, color=INK_SOFT)
    mono(fig, (84, cy + 96), '%.1e' % max(r['rel_residual'], 1e-18), 52,
         color=GREEN)
    fig.text((84, cy + 186), '代入方程几乎完全吻合', 38, color=INK)
    fig.box('r', 560, cy, 1000, cy + 260, fill=WHITE, outline=RED)
    fig.text((584, cy + 26), '解与真值的差距', 40, color=INK_SOFT)
    mono(fig, (584, cy + 96), '%.2e' % r['fwd_err'], 52, color=RED)
    fig.text((584, cy + 186), 'x 已经错了千分之几', 38, color=INK)
    yy = note(fig, cy + 320,
              '高斯消元是「向后稳定」的：它给出的解，是某个邻近方程组的精确解。'
              ' 但若原问题本身把误差放大 3.5e13 倍，邻近方程组的解离真解就很远。')
    save(fig, '12-residual.png', '向后稳定：残差小不等于解正确')


# ---------------------------------------------------------------- 图 11

def fig11():
    s = R['sweep']
    fig, y = new(11, '把同一段算术换成单精度',
                 '方程组 p·x1 + x2 = 1 + p，x1 + x2 = 2，真解永远是 (1, 1)。'
                 ' 只把每一步算术舍入成 float32（约 7 位有效数字），再让 p 一路变小。')
    x0, x1 = 210, 950
    ytop, ybot = y + 70, y + 450

    def fx(p):
        return x0 + (math.log10(0.1) - math.log10(p)) / 6.0 * (x1 - x0)

    def fy(v):
        t = (math.log10(max(v, 1e-9)) + 9.0) / 9.0
        return ybot - max(0.0, min(t, 1.0)) * (ybot - ytop)

    for e in (-8, -6, -4, -2, 0):
        yy = fy(10 ** e)
        fig.line((x0, yy), (x1, yy), color=LIGHT, width=2)
        mono(fig, (x0 - 16, yy - 22), '1e%d' % e, 38, color=GRAY, anchor='ra')
    fig.line((x0, ybot), (x1, ybot), color=INK, width=3)
    fig.line((x0, ytop), (x0, ybot), color=INK, width=3)
    for pv in (0.1, 0.001, 1e-5, 1e-7):
        fig.text((fx(pv), ybot + 14), '1e%d' % round(math.log10(pv)), 38,
                 color=INK_SOFT, anchor='ma')
    fig.text((x1, ybot + 64), '主元的绝对值 p', 38, color=INK_SOFT, anchor='ra')
    fig.text((44, ytop - 54), 'x1 的绝对误差', 38, color=INK_SOFT)

    eps32 = 1.1920929e-07
    fig.line((x0, fy(eps32)), (x1, fy(eps32)), color=GRAY, width=3, dash=12)
    fig.text((x1 - 8, fy(eps32) - 46), 'float32 的机器精度 1.2e−7', 38,
             color=GRAY, anchor='ra')

    for key, col, lab in (('err_no_pivot', RED, '不换行'),
                          ('err_partial', BLUE, '部分主元')):
        pts = [(fx(r['p']), fy(max(r[key], 1e-9))) for r in s]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=col, width=5)
        for p_ in pts:
            fig.circle(p_[0], p_[1], 8, fill=col, outline=col)
    fig.text((fx(1e-7) - 16, fy(0.19) - 70), '误差 0.19', 40, bold=True,
             color=RED, anchor='ra')
    fig.text((fx(1e-3) + 10, fy(1.2e-7) + 22), '一直停在 1.2e−7', 38, color=BLUE)
    legend(fig, ybot + 104, [(RED, '不换行'), (BLUE, '部分主元')], step=300)
    y2 = note(fig, ybot + 186,
              '误差大约是「机器精度 ÷ 主元」。p = 1e−7 时单精度的七位有效数字全部用在'
              '除以这个小得可怜的除数上，x1 偏了 19%。换成部分主元，除数永远是 1，'
              '误差就趴回机器精度。')
    save(fig, '11-float32.png', '单精度下主元大小与解的误差')


# ---------------------------------------------------------------- 图 12

def fig13():
    H = R['hilbert']
    fig, y = new(13, 'Hilbert 矩阵：条件数涨，误差跟着涨',
                 'Hilbert 矩阵的元素是 1/(i+j−1)。它的条件数随 n 指数上升，'
                 ' 而双精度只有约 16 位十进制有效数字。')
    x0, x1 = 170, 900
    ytop, ybot = y + 70, y + 440
    ns = [h['n'] for h in H]
    lo, hi = 4.0, 17.0

    def fx(n):
        return x0 + (n - 4) / 8.0 * (x1 - x0)

    def fy(v):
        t = (math.log10(max(v, 1e-30)) - lo) / (hi - lo)
        return ybot - max(0.0, min(t, 1.0)) * (ybot - ytop)

    for e in range(4, 18, 4):
        yy = fy(10 ** e)
        fig.line((x0, yy), (x1, yy), color=LIGHT, width=2)
        mono(fig, (x0 - 16, yy - 22), '1e%d' % e, 38, color=GRAY, anchor='ra')
    fig.line((x0, ybot), (x1, ybot), color=INK, width=3)
    for n in ns:
        fig.text((fx(n), ybot + 14), str(n), 38, color=INK_SOFT, anchor='ma')
    fig.text((x1, ybot + 66), 'n', 38, color=INK_SOFT, anchor='ra')
    fig.text((44, ytop - 56), '数值（对数刻度）', 38, color=INK_SOFT)

    for key, col, lab in (('cond', RED, '条件数'),
                          ('fwd_err', BLUE, '解的相对误差')):
        pts = [(fx(r['n']), fy(r[key])) for r in H]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=col, width=5)
        for p in pts:
            fig.circle(p[0], p[1], 7, fill=col, outline=col)
    fig.text((fx(12) - 14, fy(H[-1]['cond']) - 60), '条件数 4.1e16', 40,
             bold=True, color=RED, anchor='ra')
    fig.text((fx(12) - 14, fy(H[-1]['fwd_err']) - 56), '误差 0.6%', 40,
             bold=True, color=BLUE, anchor='ra')
    y2 = ybot + 110
    y2 = note(fig, y2, '两条线几乎平行地上升：每把 n 加 2，条件数大约乘 1000，'
                       '解得对的位数就少三位。双精度的 16 位在 n = 12 时基本用光。')
    save(fig, '13-hilbert.png', 'Hilbert 矩阵的条件数与向前误差')


# ---------------------------------------------------------------- 图 13

def fig14():
    s = R['sensitivity']
    fig, y = new(14, '条件数在几何上是什么',
                 '两条线的夹角越小，交点对右端项的抖动越敏感。'
                 ' 一个 0.001 的扰动，在夹角 0.03° 时能把交点推出去将近两格。')
    x0, x1 = 200, 940
    ytop, ybot = y + 70, y + 460
    degs = [r['deg'] for r in s]

    def fx(d):
        return x0 + (math.log10(max(d, 0.02)) + 1.6) / (2.0 + 1.6) * (x1 - x0)

    def fy(v):
        t = math.log10(max(v, 1e-4))
        return ybot - (t - (-4.0)) / (1.0 - (-4.0)) * (ybot - ytop)

    for e in (-3, -2, -1, 0):
        yy = fy(10 ** e)
        fig.line((x0, yy), (x1, yy), color=LIGHT, width=2)
        mono(fig, (x0 - 16, yy - 22), '1e%d' % e, 38, color=GRAY, anchor='ra')
    fig.line((x0, ybot), (x1, ybot), color=INK, width=3)
    for d in (0.1, 1, 10, 90):
        fig.text((fx(d), ybot + 14), ('%g°' % d), 38, color=INK_SOFT, anchor='ma')
    fig.text((x1, ybot + 66), '两条线的夹角', 38, color=INK_SOFT, anchor='ra')
    fig.text((44, ytop - 56), '交点位移', 38, color=INK_SOFT)

    for key, col in (('shift_1e3', RED), ('shift_1e6', BLUE)):
        pts = [(fx(r['deg']), fy(r[key])) for r in s]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=col, width=5)
        for p in pts:
            fig.circle(p[0], p[1], 7, fill=col, outline=col)
    legend(fig, ybot + 108, [(RED, '扰动 0.001'), (BLUE, '扰动 0.000001')],
           step=420)
    y2 = ybot + 190
    y2 = note(fig, y2, '位移 = 扰动 ÷ tan(夹角)。夹角 90° 时扰动原样传过去；'
                       '夹角 0.1° 时放大约 570 倍。')
    save(fig, '14-angle.png', '条件数的几何图像：夹角越小，交点越敏感')


# ---------------------------------------------------------------- 图 14

def fig15():
    c = R['cost']
    fig, y = new(15, '消元的代价',
                 '消元要做的乘法大约是 n³/3 次，加减同样多；选主元只是每列比较 n 个元素，'
                 ' 所以它便宜到可以忽略，却在数值上救了整件事。')
    rows = [[('n', INK, True), ('乘法', INK, True), ('加减', INK, True),
             ('比较', INK, True), ('比较占比', INK, True)]]
    for r in c:
        rows.append([('%d' % r['n'], INK, False),
                     ('%.3g' % r['mult'], INK, False),
                     ('%.3g' % r['add'], INK, False),
                     ('%.3g' % r['cmp'], TEAL, False),
                     ('%.2g%%' % (100 * r['pivot_share']), TEAL, False)])
    y2 = table(fig, y + 10,
               [(70, 'la'), (280, 'la'), (470, 'la'), (660, 'la'), (1016, 'ra')],
               rows, row_h=78)
    y2 = note(fig, y2 + 10, 'n = 10000 时，消元约 6.7e11 次乘加，主元的比较只有 5e7 次，'
                            '占比千分之一。')
    save(fig, '15-cost.png', '消元的浮点运算次数与选主元的开销')


# ---------------------------------------------------------------- 图 15

def fig16():
    fig, y = new(16, '三种选主元的办法',
                 '同一套消元步骤，区别只在「拿谁做除数」。'
                 ' 越靠右越贵，也越少用。')
    rows = [
        [('做法', INK, True), ('每一列做什么', INK, True), ('乘数界', INK, True)],
        [('不选', INK, False), ('直接用对角线元素', RED, False),
         ('没有，可能无穷', RED, False)],
        [('部分主元', INK, False), ('在整列里挑绝对值最大的行', TEAL, False),
         ('≤ 1', TEAL, False)],
        [('完全主元', INK, False), ('在子矩阵里挑最大值', INK, False),
         ('≤ 1，上界更小', INK, False)],
    ]
    y2 = table(fig, y + 10, [(70, 'la'), (330, 'la'), (1016, 'ra')], rows, row_h=80)
    y2 = note(fig, y2 + 6,
              '部分主元是几乎所有通用库的默认做法：它便宜，并且保证乘数不超过 1。'
              ' 完全主元的增长上界更小，但每步都要在整块子矩阵里找最大值，'
              ' 比较次数从 n²/2 变成 n³/3，和消元本身一样贵。')
    y2 = note(fig, y2 + 6,
              '两种办法都不分析行和列之间的相关性，所以病态问题照样病态 ——'
              ' 主元管的是「算术不爆」，不管「问题本身有多敏感」。')
    save(fig, '16-strategies.png', '不选、部分、完全三种主元策略的对照')


# ---------------------------------------------------------------- 图 16

def fig17():
    fig, y = new(17, '真实库里的那四步',
                 'LAPACK 的 dgesv（双精度一般矩阵直接解）内部就是这套流程，'
                 ' 只是把更新部分拼成矩阵乘法，好让 BLAS 跑满。')
    steps = [
        ('选主元并换行', '在当前列里找绝对值最大的行，同时记下交换历史，'
                    '供后面的三角求解还原。'),
        ('分解一小块列', '对一列块做不带 BLAS 的消元，得到这一块的主元和乘数。'),
        ('秩-k 更新', '把乘数作用到剩下的子矩阵上，写成一次大矩阵乘法，交给 BLAS。'),
        ('三角求解', '先用 L 解 Ly = Pb，再用上三角解 Ux = y；主元顺序就是 P。'),
    ]
    yy = y + 10
    for i, (head, body) in enumerate(steps):
        name = 's%d' % i
        fig.box(name, 48, yy, 1014, yy + 190, fill=WHITE, outline=TEAL)
        fig.text((76, yy + 22), '%d' % (i + 1), 46, bold=True, color=TEAL,
                 inside=name)
        fig.text((132, yy + 22), head, 42, bold=True, inside=name)
        fig.wrap((132, yy + 82), body, 38, 840, color=INK, inside=name)
        yy += 212
    yy = note(fig, yy,
              '为什么分成这两层：小块分解的循环没法向量化，而秩-k 更新可以；'
              '分块之后，绝大部分浮点运算落在后者，实际速度能差几倍。')
    save(fig, '17-lapack.png', 'LAPACK dgesv 的分块流程')


# ---------------------------------------------------------------- 图 17

def fig18():
    fig, y = new(18, '三句话',
                 '一篇讲完，能带走的东西不多，就这三条。')
    items = [
        ('消元在做什么', '用一行的倍数把下面几行的某一列清零，几何上是把线/面绕交点转平。', TEAL),
        ('为什么必须选主元', '除数是 0 就崩；除数很小就把舍入误差放大，换成绝对值最大的那一行即可。', AMBER),
        ('它救不了什么', '主元只保证算术本身不爆；问题病态时，残差再小，解也可能差很多。', RED),
    ]
    yy = y + 10
    for head, body, col in items:
        fig.box('c%d' % yy, 48, yy, 1014, yy + 190, fill=WHITE, outline=col)
        fig.text((76, yy + 26), head, 44, bold=True, color=col)
        fig.wrap((76, yy + 96), body, 40, 900, color=INK)
        yy += 214
    save(fig, '18-takeaways.png', '全文三句话总结')


def cover():
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill=BG, outline=None)
    fig.text((70, 64), '先拿哪个数', 100, bold=True, color=INK)
    fig.text((70, 182), '当除数', 100, bold=True, color=INK)
    fig.text((74, 308), '高斯消元里的一次换行', 44, color=INK_SOFT)
    mono(fig, (74, 400), '0.0001 x1 + x2 = 1', 52, color=RED)
    mono(fig, (74, 470), 'x1 + x2 = 2', 52, color=RED)
    fig.text((74, 570), '三位有效数字，先除 0.0001：', 40, color=INK)
    fig.text((74, 634), 'x1 = 0.0000', 86, bold=True, color=RED)
    fig.text((74, 770), '先换行，再除 1：x1 = 1.0000', 42, color=GREEN)
    fig.text((74, 946), '2027-02-08 · 原创 · CC BY 4.0', 40, color=GRAY)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png', optimize=True)
    print('   cover.png', (ART / 'cover.png').stat().st_size, 'bytes')


def main():
    for fn in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
               fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17,
               fig18):
        print(fn.__name__)
        fn()
    meta = HERE / 'figure-metadata.json'
    meta.write_text(json.dumps(META, ensure_ascii=False, indent=1) + '\n')
    print('wrote', meta, len(META), 'figures')
    cover()


if __name__ == '__main__':
    main()
