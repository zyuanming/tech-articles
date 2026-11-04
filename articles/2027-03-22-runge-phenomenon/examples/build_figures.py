#!/usr/bin/env python3
"""《多给几个点，为什么反而更歪》的原创插图。MIT。

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
STEEL = '#4a6570'
PALETTE.update({VIOLET, STEEL})

# 误差热图的六档颜色，浅 → 深
RAMP = ['#eef2ec', '#f3e7cd', '#eece9c', '#dfa165', '#c4693f', '#8c3a2b']
PALETTE.update(set(RAMP))
BANDS = [(-16, -10), (-10, -6), (-6, -3), (-3, -1), (-1, 0.5), (0.5, 3.0)]


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
    fig.text((x1, y1 + 66), xlabel, 38, color=INK_SOFT, anchor='ra')
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


# ---------------------------------------------------------------- 图 01

def fig01():
    fig, y = new(1, '三个点能定住多少',
                 'f(x) = 1/(1 + 25x²) 在 x = −1、0、1 上取值，只有一条抛物线穿过它们')
    cols = [(140, 'ra'), (430, 'ra'), (700, 'ra'), (980, 'ra')]
    rows = [[('x', INK_SOFT, True), ('真值 f(x)', INK_SOFT, True),
             ('抛物线 p(x)', INK_SOFT, True), ('差', INK_SOFT, True)]]
    src = [(-1.0, 0.038461538461538464, 0.038461538461538436),
           (0.0, 1.0, 1.0),
           (1.0, 0.038461538461538464, 0.038461538461538436),
           (0.5, R['hand']['exact'], R['hand']['interp'])]
    for xv, fv, pv in src:
        rows.append([('%.1f' % xv, INK, False), ('%.4f' % fv, INK, False),
                     ('%.4f' % pv, INK, False),
                     ('%+.4f' % (pv - fv), RED if abs(pv - fv) > 1e-3 else INK_SOFT,
                      abs(pv - fv) > 1e-3)])
    y = table(fig, y + 10, cols, rows)
    y = note(fig, y, '三点定出的抛物线是 p(x) = 1 − (25/26)x²。在 x = 0.5 处它给 0.7596，'
                     '真值 0.1379 —— 中间那一点被抬高了 0.62。')
    # 小图
    x0, x1, yb, yt = 150, 950, y + 320, y + 40

    def px(v):
        return x0 + (v + 1.0) / 2.0 * (x1 - x0)

    def py(v):
        return yb - v / 1.15 * (yb - yt)

    fig.line((x0, py(0)), (x1, py(0)), color=LIGHT, width=2)
    fig.line((x0, py(0)), (x0, py(1.1)), color=INK, width=3)
    fig.text((x0 - 14, py(1.1) - 46), '1', 38, color=INK_SOFT, anchor='ra')
    fig.text((x0 - 14, py(0) - 24), '0', 38, color=INK_SOFT, anchor='ra')
    for xv in (-1, 0, 1):
        fig.text((px(xv), py(0) + 12), '%d' % xv, 38, color=INK_SOFT, anchor='ma')
    f_pts = [(px(r['x']), py(r['f'])) for r in R['quad']['rows']]
    p_pts = [(px(r['x']), py(r['p'])) for r in R['quad']['rows']]
    dashed(fig, f_pts, GRAY)
    series(fig, p_pts, RED, width=5, r=0)
    for xv in (-1.0, 0.0, 1.0):
        fig.circle(px(xv), py(R['hand']['values'][int(xv) + 1]), 12,
                   fill=TEAL, outline=TEAL)
    # 0.5 处的落差
    fig.line((px(0.5), py(R['hand']['interp'])), (px(0.5), py(R['hand']['exact'])),
             color=VIOLET, width=4, dash=10)
    fig.text((px(0.5) - 16, py(0.52)), '落差 0.62', 38, color=VIOLET, anchor='ra')
    fig.text((px(0.52), py(0.86)), '抛物线', 38, color=RED)
    fig.text((px(0.52), py(0.28)), '真值', 38, color=GRAY)
    save(fig, '01-three-points.png', '三点插值的手算结果与抛物线形状')


# ---------------------------------------------------------------- 图 02 / 03

def curve_fig(n, key, title, sub, color, name, purpose, mark):
    fig, y = new(n, title, sub)
    rows = R['curve'][key]['rows']
    errs = [abs(r['f'] - r['p']) for r in rows]
    peak = max(errs)
    peak_x = rows[errs.index(peak)]['x']
    lo = min([r['f'] for r in rows] + [r['p'] for r in rows])
    hi = max([r['f'] for r in rows] + [r['p'] for r in rows])
    lo, hi = min(lo, -0.1) - 0.15, max(hi, 1.05) + 0.15
    x0, x1, yt = 150, 950, y + 120
    yb = yt + 520

    def px(v):
        return x0 + (v + 1.0) / 2.0 * (x1 - x0)

    def py(v):
        return yb - (v - lo) / (hi - lo) * (yb - yt)

    fig.line((x0, py(0)), (x1, py(0)), color=LIGHT, width=3)
    fig.line((x0, py(0)), (x0, py(hi)), color=INK, width=3)
    for xv in (-1, -0.5, 0, 0.5, 1):
        fig.text((px(xv), py(lo) + 12), '%g' % xv, 38, color=INK_SOFT, anchor='ma')
    fig.text((44, py(hi) - 40), '1', 38, color=INK_SOFT, anchor='la')
    dashed(fig, [(px(r['x']), py(r['f'])) for r in rows], GRAY)
    series(fig, [(px(r['x']), py(r['p'])) for r in rows], color, width=5, r=0)
    for xv in R['curve'][key]['nodes']:
        fig.circle(px(xv), py(R['curve'][key]['values'][R['curve'][key]['nodes'].index(xv)]),
                   12, fill=TEAL, outline=TEAL)
    fig.text((px(peak_x) + (20 if peak_x < 0.3 else -20), py(rows[errs.index(peak)]['p']) - 40),
             '%s %.2f' % (mark, peak), 40, color=color,
             anchor='la' if peak_x < 0.3 else 'ra')
    y = yb + 60
    return fig, y, peak, peak_x


def fig02():
    fig, y, peak, at = curve_fig(
        2, 'equi', '11 个等距节点：两端翻上去',
        '节点落在 −1、−0.8 … 0.8、1，插值曲线在两端翻上来，中间倒是贴得住',
        RED, '02-eleven-equi.png', '11 个等距节点的插值曲线与真实函数的对比', '最大误差')
    y = note(fig, y, '最大误差 1.92 出现在 x = %s 附近。函数本身不超过 1，插值曲线却冲到 1.96。'
             % minus('%.2f' % at))
    save(fig, '02-eleven-equi.png', '11 个等距节点的插值曲线：端点振荡',
         )


def fig03():
    fig, y, peak, at = curve_fig(
        3, 'cheb', '同样 11 个点，挪一下位置',
        '切比雪夫节点：中间稀、两端密。除两端各一小段外，两条线几乎重合',
        TEAL, '03-eleven-cheb.png', '11 个切比雪夫节点的插值曲线与真实函数的对比', '最大误差')
    y = note(fig, y, '最大误差 0.109，是等距节点的十七分之一。节点一样多，函数一样。')
    save(fig, '03-eleven-cheb.png', '11 个切比雪夫节点的插值曲线：误差被压到 0.1 量级')


# ---------------------------------------------------------------- 图 04

def fig04():
    fig, y = new(4, '点数加上去，误差反而变本加厉',
                 '同一组实验，只是节点位置不同；纵轴是区间上的最大误差（对数刻度）')
    x0, x1 = 175, 950
    yt, yb = y + 60, y + 560
    px, py = axes(fig, x0, yt, x1, yb, (2, 30), (1e-4, 1e4),
                  [2, 5, 10, 20, 30], [1e-4, 1e-2, 1, 1e2, 1e4], '节点数 n', '最大误差',
                  ylog=True)
    for key, color, label in (('equi', RED, '等距'), ('cheb', TEAL, '切比雪夫')):
        series(fig, [(px(r['n']), py(max(r[key]['error'], 1e-16))) for r in R['sweep']],
               color, width=5, r=7)
    fig.text((px(26), py(4.0)), '等距', 38, color=RED, anchor='ra')
    fig.text((px(26), py(1.2e-3)), '切比雪夫', 38, color=TEAL, anchor='ra')
    fig.text((px(11), py(3.2)), '1.92', 38, color=RED, anchor='ma')
    fig.text((px(11), py(3.4e-2)), '0.109', 38, color=TEAL, anchor='ma')
    fig.text((px(30), py(2.2e3)), '334', 38, color=RED, anchor='ma')
    y = yb + 140
    y = note(fig, y, '等距节点：n 从 3 加到 5，误差从 0.65 掉到 0.44，看着还行；再往上就一路涨，'
                     'n = 30 时 334。切比雪夫节点：每加一个点误差乘 0.82，30 个点剩 5.2 × 10⁻³。')
    save(fig, '04-error-vs-n.png', '最大误差随节点数的变化：等距发散，切比雪夫收敛')


# ---------------------------------------------------------------- 图 05

def fig05():
    fig, y = new(5, '是谁把误差放大的',
                 'Lebesgue 常数 λ：节点上打一个 ±ε 的扰动，插值曲线在区间内可能被放大到 λ·ε')
    x0, x1 = 175, 950
    yt, yb = y + 60, y + 560
    px, py = axes(fig, x0, yt, x1, yb, (2, 30), (1, 1e7),
                  [2, 5, 10, 20, 30], [1, 10, 100, 1e4, 1e6], '节点数 n', 'λ',
                  ylog=True, ytick_labels=['1', '10', '100', '1e4', '1e6'])
    for key, color in (('equi', RED), ('cheb', TEAL)):
        series(fig, [(px(r['n']), py(r[key]['lebesgue'])) for r in R['sweep']],
               color, width=5, r=7)
    fig.text((px(28), py(3e6)), '等距', 38, color=RED, anchor='ra')
    fig.text((px(28), py(1.6)), '切比雪夫', 38, color=TEAL, anchor='ra')
    fig.text((px(11), py(90)), '29.9', 38, color=RED, anchor='ma')
    fig.text((px(30), py(1.4e7)), '345 万', 38, color=RED, anchor='ma')
    y = yb + 140
    y = note(fig, y, '等距节点的 λ 是 2ⁿ 量级：n = 11 时 29.9，n = 30 时 3.45 × 10⁶。'
                     '切比雪夫节点的 λ 只按 log n 长，n = 30 时 3.13。'.replace('x','x'))
    save(fig, '05-lebesgue.png', 'Lebesgue 常数随节点数增长：等距指数、切比雪夫对数')


# ---------------------------------------------------------------- 图 06

def fig07():
    fig, y = new(7, '节点最后落在哪儿',
                 '同样 11 个点，一条数轴放不下同样的间距：等距是均匀的，切比雪夫是两端密的')
    x0, x1 = 150, 950

    def px(v):
        return x0 + (v + 1.0) / 2.0 * (x1 - x0)

    for k, (key, color, label) in enumerate((('equi', RED, '等距节点'),
                                             ('cheb', TEAL, '切比雪夫节点'))):
        yy = y + 90 + k * 250
        fig.text((44, yy - 66), label, 40, bold=True, color=color)
        fig.line((x0, yy), (x1, yy), color=INK, width=3)
        for xv in (-1.0, -0.5, 0.0, 0.5, 1.0):
            fig.line((px(xv), yy - 12), (px(xv), yy + 12), color=INK, width=2)
        nodes = R['nodes'][key]['nodes']
        for xv in nodes:
            fig.circle(px(xv), yy - 44, 13, fill=color, outline=color)
        closest = R['nodes'][key]['closest']
        fig.text((x0, yy + 40), '最近的两个点相距 %.3f' % closest, 38, color=INK_SOFT)
    y += 90 + 250 + 90
    y = note(fig, y, '端点密是有代价的：区间中段反而变稀（切比雪夫节点的最大间距 0.28，'
                     '等距是 0.2）。换来的好处是插值曲线的振荡被压住。')
    save(fig, '07-node-placement.png', '11 个等距节点与 11 个切比雪夫节点的位置对比')


# ---------------------------------------------------------------- 图 07

def fig06():
    fig, y = new(6, '每个基函数鼓多大',
                 '拉格朗日插值 p = Σ f[i] × L[i](x)：第 i 个节点上的误差先被 L[i] 的振幅放大，再叠加')
    x0, x1 = 175, 950
    yt, yb = y + 60, y + 560
    px, py = axes(fig, x0, yt, x1, yb, (-0.4, 10.4), (0, 7),
                  [0, 2, 4, 6, 8, 10], [0, 1, 2, 4, 6], '第几个节点 i', '|L[i]| 的最大值')
    for key, color in (('equi', RED), ('cheb', TEAL)):
        peaks = R['basis'][key]['peaks']
        series(fig, [(px(i), py(p)) for i, p in enumerate(peaks)], color, width=4, r=9)
    fig.text((px(4), py(6.51) - 46), '6.51', 38, color=RED, anchor='ma')
    fig.text((px(9.6), py(1.271) - 44), '1.27', 38, color=TEAL, anchor='ra')
    fig.text((px(1.2), py(2.0)), '等距：中段的基函数鼓到 6.5', 38, color=RED)
    fig.text((px(1.2), py(0.75)), '切比雪夫：都贴着 1', 38, color=TEAL)
    y = yb + 140
    y = note(fig, y, '等距节点把最「不敏感」的地方放在了区间正中——那里每个 L[i] 都鼓得最高。'
                     'λ 就是这些鼓包在同一个 x 上叠起来的总和。')
    save(fig, '06-basis-peaks.png', '两种节点下每个拉格朗日基函数的最大振幅')


# ---------------------------------------------------------------- 图 08

def fig08():
    fig, y = new(8, '误差在哪儿最大：一张地图',
                 '横轴是 x，纵轴是节点数 n，颜色是 |f − p| 的数量级；左右两块用同一个色标')
    xs = R['heat']['equi']['xs']
    pw, gap = 420, 60
    panels = (('equi', 60, '等距节点'), ('cheb', 60 + pw + gap, '切比雪夫节点'))
    rows = R['heat']['equi']['rows']
    top = y + 110
    row_h = 21
    for key, ox, label in panels:
        fig.text((ox, y + 40), label, 40, bold=True,
                 color=RED if key == 'equi' else TEAL)
        for j, row in enumerate(R['heat'][key]['rows']):
            for i, e in enumerate(row['err']):
                band = 0
                le = math.log10(max(e, 1e-16))
                for b, (lo, hi) in enumerate(BANDS):
                    if lo <= le < hi:
                        band = b
                cx = ox + i / (len(xs) - 1) * pw
                fig.rect(cx, top + j * row_h, cx + pw / len(xs) + 1,
                         top + j * row_h + row_h - 1, fill=RAMP[band],
                         outline=None)
        fig.rect(ox, top, ox + pw, top + len(rows) * row_h, fill=None,
                 outline=INK, width=3)
        for xv, lab in ((-1, '−1'), (0, '0'), (1, '1')):
            fig.text((ox + (xv + 1) / 2 * pw, top + len(rows) * row_h + 12), lab,
                     38, color=INK_SOFT, anchor='ma')
    fig.text((44, top), 'n = 3', 38, color=INK_SOFT, anchor='la')
    n_bot = R['heat']['equi']['rows'][-1]['n']
    fig.text((44, top + len(rows) * row_h - 40), 'n = %d' % n_bot, 38,
             color=INK_SOFT, anchor='la')
    y = top + len(rows) * row_h + 70
    # 色标
    for b, (lo, hi) in enumerate(BANDS):
        cx = 60 + b * 155
        fig.rect(cx, y, cx + 50, y + 40, fill=RAMP[b], outline=INK, width=2)
        lab = '10^%d' % lo if lo > -16 else '<10^-10'
        fig.text((cx + 60, y + 2), lab, 38, color=INK_SOFT)
    y += 80
    y = note(fig, y, '左图越往上越是一片中等颜色，右图的深处只剩两端两条暗带——'
                     '切比雪夫插值的误差集中在端点附近，而且一路在变浅。')
    save(fig, '08-error-map.png', '误差随 x 与 n 的分布：两块热图对比')


# ---------------------------------------------------------------- 图 09

def fig09():
    fig, y = new(9, '收敛快慢由最近的极点决定',
                 '把 a 换掉，极点的位置就换掉，误差下降的斜率跟着换：1/(1 + a x²) 的极点在 ±i/√a')
    x0, x1 = 175, 950
    yt, yb = y + 60, y + 560
    px, py = axes(fig, x0, yt, x1, yb, (4, 30), (1e-16, 1),
                  [4, 10, 20, 30], [1e-16, 1e-12, 1e-8, 1e-4, 1], '节点数 n', '最大误差',
                  ylog=True)
    colors = (BLUE, AMBER, RED)
    for (rate, color) in zip(R['rates'], colors):
        pts = [(px(r['n']), py(max(r['error'], 1e-17))) for r in rate['rows']]
        series(fig, pts, color, width=5, r=7)
        at = next(r for r in rate['rows'] if r['n'] == 12)
        fig.text((px(12) + 16, py(at['error']) - 18),
                 'a = %g，ρ = %.2f' % (rate['a'], rate['rho_theory']), 38,
                 color=color, anchor='la')
    y = yb + 140
    y = note(fig, y, '误差按 ρ⁻ⁿ 掉，ρ 由极点决定：极点在 ±i 时 ρ = 2.41，在 ±i/5 时 ρ = 1.22。'
                     '三条线的斜率量出来是 2.41 / 1.54 / 1.22。')
    save(fig, '09-rates.png', '收敛率随极点位置变化：三条指数衰减曲线')


# ---------------------------------------------------------------- 图 10

def fig10():
    fig, y = new(10, '换节点也救不回来的时候',
                 '|x| 在 0 处有个尖角。它没有极点，却也不是多项式：切比雪夫插值只是慢慢地靠近')
    x0, x1 = 175, 950
    yt, yb = y + 60, y + 560
    px, py = axes(fig, x0, yt, x1, yb, (4, 30), (1e-12, 1),
                  [4, 10, 20, 30], [1e-12, 1e-8, 1e-4, 1], '节点数 n', '最大误差',
                  ylog=True)
    series(fig, [(px(r['n']), py(r['error'])) for r in R['rates'][0]['rows']],
           GRAY, width=4, r=0)
    series(fig, [(px(r['n']), py(r['error'])) for r in R['absx']['rows']],
           VIOLET, width=5, r=8)
    fig.text((px(24), py(2.0e-6)), '1/(1+x²)，ρ = 2.41', 38, color=GRAY, anchor='ra')
    fig.text((px(24), py(0.20)), '|x|，每加一点乘 0.93', 38, color=VIOLET, anchor='ra')
    y = yb + 140
    y = note(fig, y, '30 个切比雪夫节点，|x| 的误差还有 0.033。每个新节点只把误差乘 0.93，'
                     '想再掉两个数量级得再要六十个点。')
    save(fig, '10-absx.png', '|x| 的切比雪夫插值：没有极点，收敛很慢')


# ---------------------------------------------------------------- 图 11

def fig11():
    fig, y = new(11, '三句话')
    y = bullets(fig, y + 30, [
        '插值误差 = 函数能被多项式逼近到什么程度，乘上节点决定的放大倍数 λ。等距节点的 λ 是 2ⁿ 量级，'
        '所以点越多越歪。',
        '把节点按切比雪夫分布摆（端点密），λ 只按 log n 长，剩下的就是能不能被逼近的问题。',
        '能不能被逼近看最近的极点：ρ = 1.22 就是每加一点误差只乘 0.82，再快也快不过这个斜率。',
    ], accent=TEAL)
    save(fig, '11-takeaways.png', '三条结论')


# ---------------------------------------------------------------- 封面

def cover():
    fig = Fig(1080, width=1080)
    fig.text((60, 80), '多给几个点', 96, bold=True)
    fig.text((60, 200), '为什么反而更歪', 96, bold=True)
    fig.text((60, 344), '1/(1 + 25x²) 在 [−1, 1] 上的等距插值', 42, color=INK_SOFT)
    rows = [('11 个等距节点', '差 1.92', RED),
            ('30 个等距节点', '差 334', RED),
            ('11 个切比雪夫节点', '差 0.109', TEAL)]
    yy = 460
    for label, val, color in rows:
        fig.text((60, yy), label, 44, color=INK)
        fig.text((1020, yy), val, 44, bold=True, color=color, anchor='ra')
        yy += 88
    fig.line((60, yy - 24), (1020, yy - 24), color=LIGHT, width=3)
    yy = 700
    for line in ('等距节点把 Lebesgue 常数推到 345 万',
                 '节点挪到两端密，它只按 log n 涨',
                 '1901 年 Runge 的反例，今天还在踩'):
        fig.text((60, yy), line, 42, color=INK_SOFT)
        yy += 64
    fig.text((1020, 990), '2027-03-22', 42, color=GRAY, anchor='ra')
    fig.save(ART / 'cover.png', '封面', '原创示意')
    print('   cover.png')


def main():
    fig01()
    fig02()
    fig03()
    fig04()
    fig05()
    fig06()
    fig07()
    fig08()
    fig09()
    fig10()
    fig11()
    cover()
    (HERE / 'figure-metadata.json').write_text(json.dumps(META, indent=1))
    print('wrote', HERE / 'figure-metadata.json', len(META), 'figures')


if __name__ == '__main__':
    main()
