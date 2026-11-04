#!/usr/bin/env python3
"""《深度缓冲只记得住 48 厘米》的原创插图。MIT。

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

NEAR = R['meta']['near']
FAR = R['meta']['far']


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
    fig.text((x1, y1 + 64), xlabel, 38, color=INK_SOFT, anchor='ra')
    fig.text((x0 - 16, y0 - 54), ylabel, 38, color=INK_SOFT, anchor='la')
    return px, py


def series(fig, pts, color, width=5, r=8):
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=color, width=width)
    for p in pts:
        fig.circle(p[0], p[1], r, fill=color, outline=color)


def dot_label(fig, x, y, text, anchor='ma', color=INK, dx=0, dy=-30):
    fig.text((x + dx, y + dy), text, 38, color=color, anchor=anchor)


def fmt_m(v):
    """把米数写成人能读的单位。"""
    if v >= 0.1:
        return '%.2f 米' % v if v >= 1 else '%.1f 厘米' % (v * 100)
    if v >= 0.001:
        return '%.1f 毫米' % (v * 1000)
    if v >= 1e-6:
        return '%.1f 微米' % (v * 1e6)
    return '%.0f 纳米' % (v * 1e9)


def step_row(z, near=NEAR):
    for row in R['steps']:
        if abs(row['z'] - z) < 1e-9 and abs(row['near'] - near) < 1e-12:
            return row
    raise KeyError(z)


# ---------------------------------------------------------------- 图 01

def fig01():
    fig, y = new(1, '前 10 米吃掉 90% 的缓冲',
                 'near = 0.1 米、far = 1000 米的标准映射：1677 万个格子怎么铺在距离上')
    x0, x1 = 90, 970
    seg = (x1 - x0) / 4.0
    fig.text((44, y), '把距离按十倍一段切开（米），四段在对数刻度上等宽', 40, bold=True)
    y += 74
    labels = ['0.1–1', '1–10', '10–100', '100–1000']
    for i, lab in enumerate(labels):
        a = x0 + i * seg
        fig.rect(a, y, a + seg - 6, y + 78, fill=TINT_T, outline=INK, width=2)
        fig.text((a + seg / 2 - 3, y + 18), lab, 38, color=INK, anchor='ma')
    y += 116

    fig.text((44, y), '同样这四段，在深度缓冲里占的格子', 40, bold=True)
    y += 74
    cut = x0 + (x1 - x0) * 0.9
    fig.rect(x0, y, x1, y + 96, fill=TINT_R, outline=INK, width=3)
    fig.rect(x0, y, cut, y + 96, fill=TINT_T, outline=INK, width=3)
    fig.text(((x0 + cut) / 2, y + 24), '90%', 46, bold=True, color=INK, anchor='ma')
    fig.text(((cut + x1) / 2, y + 24), '10%', 46, bold=True, color=INK, anchor='ma')
    y += 130
    y = note(fig, y, '1 米处的深度值是 0.900，10 米是 0.990，100 米是 0.999，500 米是 0.9999。'
                     '相机脚下的第一米就占掉九成格子，剩下 999 米分那一成。')
    y = note(fig, y, '这不是实现的选择，是 d = 1/z 的形状决定的：距离翻十倍，'
                     '深度值只往终点挪了一个数量级里的九成。')
    save(fig, '01-decades.png', '前十年吃掉九成深度范围',
         '原创示意，数值取自 results.json 的 depth_values')


# ---------------------------------------------------------------- 图 02

def fig02():
    fig, y = new(2, '深度值随距离冲得有多快',
                 '横轴是距离（对数），纵轴是存进去的深度值 d，0 是近平面、1 是远平面')
    px, py = axes(fig, 120, y + 40, 970, y + 520, (0.1, 1000.0), (0.0, 1.0),
                  [0.1, 1, 10, 100, 1000], [0.0, 0.5, 0.9, 1.0],
                  '到相机的距离（米）', '深度值 d', xlog=True)
    pts = [(px(r['z']), py(r['d_std'])) for r in R['curve']]
    series(fig, pts, TEAL)
    for z in (1.0, 10.0, 100.0, 500.0):
        row = next(r for r in R['depth_values'] if abs(r['z'] - z) < 1e-9)
        fig.circle(px(z), py(row['d_std']), 11, fill=RED, outline=RED)
    # 曲线在右上角压平，标签只能挪到下半边的空白处
    ty = py(0.62)
    for z in (1.0, 10.0, 100.0, 500.0):
        row = next(r for r in R['depth_values'] if abs(r['z'] - z) < 1e-9)
        fig.circle(566, ty + 20, 10, fill=RED, outline=RED)
        fig.text((596, ty), '%g 米 → %.4g' % (z, row['d_std']), 38, color=INK)
        ty += 66
    y = y + 620
    y = note(fig, y, '曲线在前三格里几乎贴着 0，最后一段突然贴到 1。'
                     '把同样的曲线换到距离轴上读，就是「精度全挤在近处」。')
    save(fig, '02-d-curve.png', '标准映射下深度值随距离的变化',
         '原创示意，曲线取自 results.json 的 curve')


# ---------------------------------------------------------------- 图 03

def fig03():
    fig, y = new(3, '24 位定点的格子，摊到距离上是什么样',
                 '纵轴是「这个距离上还能分开多小的间隔」，三条线只差近平面')
    px, py = axes(fig, 210, y + 40, 970, y + 540, (1.0, 1000.0), (1e-6, 1.0),
                  [1, 10, 100, 1000], [1e-6, 1e-4, 1e-2, 1.0],
                  '到相机的距离（米）', '能分开的最小间隔',
                  ylog=True, xlog=True,
                  ytick_labels=['1 微米', '0.1 毫米', '1 厘米', '1 米'])
    colors = (TEAL, BLUE, AMBER)
    names = ('near = 0.1 米', 'near = 1 米', 'near = 10 米')
    for curve, color, name in zip(R['step_curves'], colors, names):
        pts = [(px(r['z']), py(r['step'])) for r in curve['rows']]
        series(fig, pts, color, width=5, r=0)
        x, yy = pts[-1]
        fig.circle(x, yy, 11, fill=color, outline=color)
        dot_label(fig, x, yy, name, anchor='ra', dx=-18, dy=8, color=color)
    y = y + 660
    y = note(fig, y, '三条线斜率都是 2：间隔随距离平方长。1 米到 100 米，格子从 0.6 微米涨到 6 毫米，'
                     '一万倍。')
    y = note(fig, y, '纵向一比：near 从 0.1 拉到 1，整条线往下挪十倍——这就是「近平面是唯一旋钮」的样子。')
    save(fig, '03-step-curves.png', '三种近平面下 24 位定点的间隔曲线',
         '原创示意，曲线取自 results.json 的 step_curves')


# ---------------------------------------------------------------- 图 04

def fig04():
    fig, y = new(4, '近平面挪一倍，精度就好一倍',
                 '固定距离 500 米，只改 near。纵轴是 24 位定点在 500 米处的间隔')
    px, py = axes(fig, 150, y + 40, 970, y + 500, (0.05, 100.0), (0.1, 1000.0),
                  [0.05, 0.1, 1, 10, 100], [0.1, 1, 10, 100, 1000],
                  '近平面（米）', '500 米处的间隔（毫米）', xlog=True, ylog=True,
                  xtick_labels=['0.05', '0.1', '1', '10', '100'])
    pts = [(px(r['near']), py(r['fixed24'] * 1000)) for r in R['near_sweep']]
    series(fig, pts, TEAL, width=5, r=9)
    for near in (0.1, 1.0, 10.0):
        row = next(r for r in R['near_sweep'] if abs(r['near'] - near) < 1e-12)
        x, yy = px(near), py(row['fixed24'] * 1000)
        dot_label(fig, x, yy, '%.3g 毫米' % (row['fixed24'] * 1000),
                  anchor='la', dx=14, dy=6)
    y = y + 620
    y = note(fig, y, '双对数下是一条斜率 −1 的直线：间隔和 near 成反比。'
                     'near 从 0.1 走到 10，500 米处从 149 毫米降到 1.5 毫米；再走到 100，降到 0.13 毫米。')
    y = note(fig, y, '代价是近处的东西开始被切掉。这是纯粹的取舍，没有免费的旋钮。')
    save(fig, '04-near-sweep.png', '近平面与 500 米处间隔的关系',
         '原创示意，数值取自 results.json 的 near_sweep')


# ---------------------------------------------------------------- 图 05

def fig05():
    fig, y = new(5, '远平面几乎不参与',
                 '固定 near = 0.1 米、距离 500 米，只改 far')
    rows = R['far_sweep']
    x0, y1 = 150, y + 460
    px_lo, px_hi = 150, 930
    step = (px_hi - px_lo) / len(rows)
    base = y1
    top = y + 40
    scale = (base - top) / 200.0  # 毫米

    fig.line((px_lo - 20, base), (px_hi + 20, base), color=INK, width=3)
    fig.line((px_lo - 20, top), (px_lo - 20, base), color=INK, width=3)
    fig.text((px_lo - 26, top - 46), '间隔（毫米）', 38, color=INK_SOFT, anchor='la')
    for tick in (0, 100, 200):
        yy = base - tick * scale
        fig.line((px_lo - 20, yy), (px_hi + 20, yy), color=LIGHT, width=2)
        fig.text((px_lo - 32, yy - 22), str(tick), 38, color=INK_SOFT, anchor='ra')
    for i, row in enumerate(rows):
        cx = px_lo + step * (i + 0.5)
        h = (row['fixed24'] * 1000) * scale
        fig.rect(cx - 38, base - h, cx + 38, base, fill=TEAL, outline=None, radius=4)
        fig.text((cx, base + 14), ('%g' % row['far']) if row['far'] < 1e5 else '100 万',
                 38, color=INK_SOFT, anchor='ma')
        fig.text((cx, base - h - 46), '%.1f' % (row['fixed24'] * 1000), 38,
                 color=INK, anchor='ma')
    y = base + 84
    y = note(fig, y, 'far 从 600 米拉到一百万米，六根柱子一样高：500 米处的间隔都是 149.1 毫米，'
                     '差在第三位有效数字。')
    y = note(fig, y, '因为 (far − near) / (far · near) 里 far 一变大就等于 1 / near，far 自己消失了。'
                     '省精度从来不是远平面干的。')
    save(fig, '05-far-sweep.png', '远平面对 500 米处间隔几乎没有影响',
         '原创示意，数值取自 results.json 的 far_sweep')


# ---------------------------------------------------------------- 图 06

def fig06():
    fig, y = new(6, '换成 float32 也一样，一模一样',
                 '同样六个距离，定点 24 位与 float32 标准映射的间隔')
    cols = [(48, 'la'), (430, 'ra'), (760, 'ra')]
    rows = [[('距离', INK_SOFT, True), ('24 位定点', INK_SOFT, True),
             ('float32 标准', INK_SOFT, True)]]
    for z in (1.0, 10.0, 100.0, 250.0, 500.0, 900.0):
        row = step_row(z)
        rows.append([
            ('%g 米' % z, INK, False),
            ('%.3g' % row['fixed24'], INK, False),
            ('%.3g' % row['f32_std'], TEAL, False),
        ])
    y = table(fig, y + 20, cols, rows, size=40, row_h=76)
    y = note(fig, y, '两列数字逐位相同，不是巧合：float32 在 [0.5, 1) 里的间距是 2 的 −24 次方，'
                     '和 24 位定点的格距完全一样。')
    y = note(fig, y, '而远端那一片格子，深度值全都贴在 1 附近。float 的指数位在这里什么也没帮上——'
                     '它把精度铺在了 0 附近，也就是相机脚下。')
    save(fig, '06-float-vs-fixed.png', 'float32 标准映射与 24 位定点在远端完全重合',
         '原创示意，数值取自 results.json 的 steps')


# ---------------------------------------------------------------- 图 07

def fig07():
    fig, y = new(7, '反转：把 1/z 的镜子翻过来',
                 '同样一根曲线，纵轴换成 1 − d，近平面到 1、远平面到 0')
    px, py = axes(fig, 120, y + 40, 970, y + 520, (0.1, 1000.0), (0.0, 1.0),
                  [0.1, 1, 10, 100, 1000], [0.0, 0.5, 1.0],
                  '到相机的距离（米）', '存进去的值', xlog=True)
    std = [(px(r['z']), py(r['d_std'])) for r in R['curve']]
    rev = [(px(r['z']), py(r['d_rev'])) for r in R['curve']]
    series(fig, std, TEAL, width=5, r=0)
    series(fig, rev, AMBER, width=5, r=0)
    fig.text((px(1.6), py(0.93) - 40), '标准：近 → 0', 38, color=TEAL)
    fig.text((px(1.6), py(0.06)), '反转：近 → 1', 38, color=AMBER)
    y = y + 620
    y = note(fig, y, '两条线互为 1 − d。翻转本身不改变任何东西——除非存的是浮点数，'
                     '而浮点数的间距随数值缩小而缩小。')
    y = note(fig, y, '反转之后，远处存的是很小的数，指数位自动给出更多相对精度；'
                     '「1/z 越远越挤」和「浮点越靠近 0 越密」正好互相抵消。')
    save(fig, '07-reversed-curve.png', '标准映射与反转映射互为镜像',
         '原创示意，曲线取自 results.json 的 curve')


# ---------------------------------------------------------------- 图 08

def fig08():
    fig, y = new(8, '反转之后，格子几乎不随距离长大',
                 'near = 0.1 米、far = 1000 米。纵轴是还能分开多小的间隔')
    px, py = axes(fig, 210, y + 40, 970, y + 540, (1.0, 1000.0), (1e-6, 1.0),
                  [1, 10, 100, 1000], [1e-6, 1e-4, 1e-2, 1.0],
                  '到相机的距离（米）', '能分开的最小间隔',
                  ylog=True, xlog=True,
                  ytick_labels=['1 微米', '0.1 毫米', '1 厘米', '1 米'])
    fixed = [(px(r['z']), py(r['step'])) for r in R['step_curves'][0]['rows']]
    series(fig, fixed, TEAL, width=5, r=0)
    rev = [(px(r['z']), py(r['step'])) for r in R['rev_curve']]
    series(fig, rev, AMBER, width=5, r=0)
    worst = R['rev_worst']
    wx, wy = px(worst['z']), py(worst['step'])
    fig.circle(wx, wy, 12, fill=RED, outline=RED)
    dot_label(fig, wx, wy, '最差 %.0f 微米（%.0f 米处）' % (worst['step'] * 1e6, worst['z']),
              anchor='ra', dx=-24, dy=-54, color=RED)
    fig.text((px(1.4), py(0.02)), '24 位定点（float32 标准与它重合）', 38, color=TEAL)
    fig.text((px(1.4), py(2.6e-5)), 'float32 反转', 38, color=AMBER)
    y = y + 660
    y = note(fig, y, '定点那条一路上扬，900 米处要 48 厘米；反转那条是锯齿，峰谷差一倍，'
                     '但包络几乎走平，900 米处还有 7.4 微米。')
    y = note(fig, y, '锯齿是浮点自己的形状：存的值每跨过一个 2 的幂，格距就减半，而距离平方那一项还在长。'
                     '最差的齿在 587 米，25 微米。')
    save(fig, '08-reversed-vs-fixed.png', '反转 float32 与 24 位定点的间隔对比',
         '原创示意，曲线取自 results.json 的 step_curves 与 rev_curve')


# ---------------------------------------------------------------- 图 09

def fig09():
    fig, y = new(9, '两个面相隔多远，才会开始闪',
                 'near = 0.1 米、far = 1000 米，24 位定点。竖轴是「两个面被压成同一个深度值」的比例')
    px, py = axes(fig, 170, y + 40, 970, y + 500, (0.5, 1000.0), (0.0, 1.0),
                  [0.5, 1, 10, 100, 1000], [0.0, 0.5, 1.0],
                  '到相机的距离（米）', '合并的比例', xlog=True,
                  xtick_labels=['0.5', '1', '10', '100', '1000'])
    colors = (AMBER, TEAL, BLUE, RED)
    names = ('1 毫米', '1 厘米', '10 厘米', '1 米')
    for curve, color in zip(R['merge_curves'], colors):
        pts = [(px(r['z']), py(r['p'])) for r in curve['rows']]
        series(fig, pts, color, width=5, r=0)
    row = R['threshold'][1]
    x = px(row['z_guarantee'])
    fig.line((x, py(0.0)), (x, py(1.0)), color=GRAY, width=3, dash=10)
    fig.text((x - 16, py(0.30)), '1 厘米：129 米', 38, color=GRAY, anchor='ra')
    # 四条曲线在左下角都还贴着 0，图例放那里
    for i, (color, name) in enumerate(zip(colors, names)):
        lx = 210 + (i % 2) * 310
        lyy = py(0.72) + (i // 2) * 96
        fig.rect(lx, lyy + 4, lx + 30, lyy + 34, fill=color, outline=None, radius=6)
        fig.text((lx + 44, lyy - 2), name, 38, color=INK)
    y = y + 620
    y = note(fig, y, '1 厘米的间隙，129 米之前一定分得开；183 米时有一半的对子已经并在一起；'
                     '409 米以后全部合并。')
    y = note(fig, y, '远处墙面开始闪就是这个形状：不是贴图、光照或者法线出了问题，'
                     '是两个面的深度落进了同一个格子。')
    save(fig, '09-threshold.png', '不同间隙被压成同一深度值的比例随距离的变化',
         '原创示意，数值取自 results.json 的 merge_curves 与 threshold')


# ---------------------------------------------------------------- 图 10

def fig10():
    fig, y = new(10, '「算完再减 1」会把好处全丢掉',
                 '1000 个点，在 100 米处相邻两点相隔 1 毫米。每个小格是一对相邻点')
    sa = R['subtract_after']
    cell = 17
    cols = 50
    rows = math.ceil(len(sa['trap_mask']) / cols)
    for idx, (title, mask, color) in enumerate((
            ('矩阵直接算出反转深度：0 对被压成同一个值', sa['matrix_mask'], TINT_T),
            ('事后做一次 1 − d：834 对被压成同一个值', sa['trap_mask'], RED))):
        fig.text((44, y), title, 40, bold=True, color=INK if idx else INK)
        y += 74
        gx = 90
        for i, bit in enumerate(mask):
            cx = gx + (i % cols) * cell
            cy = y + (i // cols) * cell
            fill = TINT_R if bit else (TINT_T if idx == 0 else TINT_G)
            if idx == 1:
                fill = RED if bit else TINT_G
            fig.rect(cx, cy, cx + cell - 2, cy + cell - 2, fill=fill, outline=None)
        y += rows * cell + 40
    y = note(fig, y, '1 − d 在 float32 里做：d 已经贴到 0.999，减出来的差值有效位数只剩几位，'
                     '等于把 24 位精度又还回去了。')
    y = note(fig, y, '反转深度必须是投影矩阵直接算出来的（25 角取 1 − d 的矩阵形式），'
                     '不是算完再补一刀。')
    save(fig, '10-subtract-trap.png', '事后相减与矩阵直算的对比',
         '原创示意，掩码取自 results.json 的 subtract_after')


# ---------------------------------------------------------------- 图 11

def fig11():
    fig, y = new(11, '相机离原点很远时，还有一个坑',
                 '相机放在 1000 米外、远平面 10000 米。每格写「被合并的对数 / 顺序颠倒的对数」：'
                 '一共 999 对相邻点')
    cols = [(48, 'la'), (470, 'ra'), (750, 'ra'), (990, 'ra')]
    rows = [[('两个面的间距', INK_SOFT, True), ('预乘', INK_SOFT, True),
             ('分开乘', INK_SOFT, True), ('反转深度', INK_SOFT, True)]]
    for row in R['premultiply']['standard']['rows']:
        rows.append([
            ('%.2f 米' % row['sep'], INK, False),
            ('%d / %d' % (row['premultiplied']['indist'], row['premultiplied']['swap']), RED, False),
            ('%d / %d' % (row['separate']['indist'], row['separate']['swap']), BLUE, False),
            ('0 / 0', TEAL, False),
        ])
    y = table(fig, y + 20, cols, rows, size=38, row_h=76)
    y = note(fig, y, '预乘会把平移量乘进投影矩阵，相邻两点的深度在相减时丢位，出现顺序颠倒；'
                     '分开乘不丢位，但深度本身在那一带已经挤成一团。')
    y = note(fig, y, '分开乘把颠倒压成「合并」，总数没少——这和 Nathan Reed 复现 Upchurch 与 Desbrun'
                     ' 时的结论一致：它换来的是错误类型变温和，不是错误消失。')
    y = note(fig, y, '反转深度那一列三个间距都是 0 / 0，比表里任何一格都干净。')
    save(fig, '11-premultiply.png', '预乘与分开乘的深度顺序误差',
         '原创示意，数值取自 results.json 的 premultiply')


# ---------------------------------------------------------------- 图 12

def fig12():
    fig, y = new(12, '记三句')
    y = bullets(fig, y + 20, [
        '深度值存的是 1/z 的线性重映射，所以精度按距离平方衰减，不是均匀的。',
        '能调的旋钮只有一个：near。远平面几乎不参与，float32 也救不了它。',
        '反转深度把「1/z 越远越挤」和「浮点越近 0 越密」对上，代价是整套深度约定要改。',
    ])
    y += 10
    save(fig, '12-takeaways.png', '三句话总结')


# ---------------------------------------------------------------- 封面

def cover():
    fig = Fig(1080, width=1080)
    fig.text((60, 96), '深度缓冲', 64, bold=True, color=INK)
    fig.text((60, 176), '只记得住', 64, bold=True, color=INK)
    fig.text((60, 256), '48 厘米', 96, bold=True, color=RED)
    fig.text((60, 392), 'near 0.1 米、far 1000 米时，900 米处的分辨力', 40, color=INK_SOFT)
    rows = [
        ('24 位定点', '48 厘米', RED),
        ('float32 标准', '48 厘米', RED),
        ('float32 反转', '7.4 微米', TEAL),
    ]
    y = 470
    for name, val, color in rows:
        fig.text((60, y), name, 42, color=INK)
        fig.text((1020, y), val, 42, bold=True, color=color, anchor='ra')
        fig.line((60, y + 56), (1020, y + 56), color=LIGHT, width=2)
        y += 86
    fig.text((60, 760), '前 10 米吃掉 90% 的深度缓冲', 42, color=INK)
    fig.text((60, 830), '近平面是唯一的旋钮', 42, color=INK)
    fig.text((60, 900), '远平面几乎无关', 42, color=INK)
    fig.text((1020, 991), '2027-03-15', 40, color=GRAY, anchor='ra')
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
    fig12()
    out = HERE / 'figure-metadata.json'
    out.write_text(json.dumps(META, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('wrote', out, len(META), 'figures')
    cover()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        globals()['fig%02d' % int(sys.argv[1])]()
        out = HERE / 'figure-metadata.json'
        out.write_text(json.dumps(META, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    else:
        main()
