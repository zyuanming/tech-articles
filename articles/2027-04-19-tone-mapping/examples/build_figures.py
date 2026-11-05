#!/usr/bin/env python3
"""《太亮的地方，全挤在最后一格》的原创插图。MIT。

带数字的图都读 results.json。
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

COLORS = {'截断': RED, 'Reinhard': BLUE, '白点 8': TEAL, 'ACES 拟合': VIOLET}


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


def table(fig, y, cols, rows, row_h=68):
    for i, row in enumerate(rows):
        if i % 2 == 1:
            fig.rect(48, y - 14, 1014, y + row_h - 26, fill=PALE, outline=None)
        for (text, color, bold), (x, anchor) in zip(row, cols):
            if not text:
                continue
            fig.text((x, y), text, 38, bold=bold, color=color, anchor=anchor)
        y += row_h
    return y


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


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
        if lab:
            fig.text((px(t), y1 + 14), lab, 38, color=INK_SOFT, anchor='ma')
    for t, lab in zip(yticks, ytick_labels or [str(t) for t in yticks]):
        if lab:
            fig.text((x0 - 16, py(t) - 22), lab, 38, color=INK_SOFT, anchor='ra')
    if xlabel:
        fig.text((x1, y1 + 66), xlabel, 38, color=INK_SOFT, anchor='ra')
    if ylabel:
        fig.text((x0, y0 - 62), ylabel, 38, color=INK_SOFT, anchor='la')
    return px, py


def series(fig, pts, color, width=5, r=10, fill=True):
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=color, width=width)
    for p in pts:
        if fill:
            fig.circle(p[0], p[1], r, fill=color, outline=color)
        else:
            fig.circle(p[0], p[1], r, fill=WHITE, outline=color, width=5)


def legend_block(fig, x, y, items, gap=54):
    """独立的图例块：小线段 + 文字，纵向排开，不贴曲线。"""
    for label, color in items:
        fig.line((x, y + 16), (x + 54, y + 16), color=color, width=8)
        fig.text((x + 72, y), label, 40, color=color)
        y += gap
    return y


def legend2(fig, y, items, gap=56):
    """两列图例块。返回下一行的 y。"""
    for i, (label, color) in enumerate(items):
        x = 60 if i % 2 == 0 else 540
        yy = y + (i // 2) * gap
        fig.line((x, yy + 16), (x + 54, yy + 16), color=color, width=8)
        fig.text((x + 72, yy), label, 40, color=color)
    return y + ((len(items) + 1) // 2) * gap

def fmt(x, digits=2):
    if x == 0:
        return '0'
    if abs(x) < 1e-3 or abs(x) >= 1e5:
        mant, exp = ('%.*e' % (digits - 1, x)).split('e')
        return '%se%s' % (mant, minus(int(exp)))
    return ('%.' + str(digits) + 'g') % x


def curve_fn(name):
    from tone import (clamp01, reinhard, reinhard_white, aces_fit)
    return {'截断': clamp01, 'Reinhard': reinhard,
            '白点 8': lambda x: reinhard_white(x, 8.0),
            'ACES 拟合': aces_fit}[name]


def srgb_hex(y):
    """把显示值变成 sRGB 颜色，并登记进 figkit 的色板。"""
    from tone import srgb_encode
    v = int(round(srgb_encode(y) * 255))
    c = '#%02x%02x%02x' % (v, v, v)
    PALETTE.add(c)
    return c


# ---------------------------------------------------------------- 图 01
def fig01():
    fig, y = new(1, '四条曲线，各压各的',
                 '横轴是场景亮度（对数），纵轴是显示值；输入 1.0 = 直接显示就白了')
    x0, x1 = 150, 1000
    y0, y1 = y + 40, y + 560
    px, py = axes(fig, x0, y0, x1, y1, (0.001, 64), (0, 1),
                  [0.001, 0.01, 0.1, 1, 10], [0, 0.25, 0.5, 0.75, 1],
                  '场景亮度', '', xtick_labels=['', '0.01', '0.1', '1', '10'],
                  ytick_labels=['0', '0.25', '0.5', '0.75', '1'], xlog=True)
    for i in range(0, 60):
        a = 0.001 * (10 ** (i / 20))
        b = 0.001 * (10 ** ((i + 1) / 20))
        fig.line((px(a), py(a)), (px(b), py(b)), color=GRAY, width=3)
    pts = []
    for i in range(0, 121):
        v = 0.001 * (10 ** (i / 33.0))
        pts.append((px(min(v, 64)), py(curve_fn('Reinhard')(v))))
    series(fig, pts, BLUE, width=6, fill=False)
    pts = []
    for i in range(0, 121):
        v = 0.001 * (10 ** (i / 33.0))
        pts.append((px(min(v, 64)), py(curve_fn('白点 8')(v))))
    series(fig, pts, TEAL, width=6, fill=False)
    pts = []
    for i in range(0, 121):
        v = 0.001 * (10 ** (i / 33.0))
        pts.append((px(min(v, 64)), py(curve_fn('ACES 拟合')(v))))
    series(fig, pts, VIOLET, width=6, fill=False)
    pts = []
    for i in range(0, 121):
        v = 0.001 * (10 ** (i / 33.0))
        pts.append((px(min(v, 64)), py(curve_fn('截断')(v))))
    series(fig, pts, RED, width=6, fill=False)
    # 中灰那一点
    gx, gy = px(0.18), py(curve_fn('Reinhard')(0.18))
    fig.circle(gx, gy, 16, fill=WHITE, outline=BLUE, width=6)
    y = y1 + 112
    y = legend2(fig, y, [(n, COLORS[n]) for n in
                         ('截断', 'Reinhard', '白点 8', 'ACES 拟合')])
    y = note(fig, y + 6, '灰虚线是 y = x：不做任何映射时，场景值就是显示值。截断的红线在 1 之前'
                         '和它重合，到 1 就折平；蓝圈是中灰 0.18。')
    save(fig, '01-curves.png', '四条色调映射曲线的整体形状')


# ---------------------------------------------------------------- 图 02
def fig02():
    fig, y = new(2, '同样八个亮度，四条曲线排出来不一样',
                 '每一格是一次输入；格子颜色就是它在屏幕上的样子')
    vals = [0.05, 0.18, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
    names = ['截断', 'Reinhard', '白点 8', 'ACES 拟合']
    left, right = 250, 1014
    w = (right - left) / len(vals)
    for r, name in enumerate(names):
        yy = y + 30 + r * 118
        fig.text((44, yy + 26), name, 40, color=COLORS[name])
        for i, v in enumerate(vals):
            c = srgb_hex(curve_fn(name)(v))
            fig.rect(left + i * w, yy, left + (i + 1) * w - 6, yy + 84, fill=c,
                     outline=INK, width=2)
    yy = y + 30 + len(names) * 118
    for i, v in enumerate(vals):
        fig.text((left + i * w + w / 2, yy), fmt(v), 38, color=INK_SOFT, anchor='ma')
    y = note(fig, yy + 54, '最左一列是暗部 0.05，最右一列是比白点还亮 16 倍的天空。'
                           '截断那一行的右边四格全白，因为它们都超过了 1。')
    note(fig, y, 'Reinhard 那一行右边几格是灰的：它永远不会显示成纯白，'
                 '所以要靠「白点」告诉它哪里算白。')
    save(fig, '02-swatches.png', '同一组输入在四条曲线下的显示颜色')


# ---------------------------------------------------------------- 图 03
def fig03():
    fig, y = new(3, '多一倍的亮度，只剩几个码值',
                 '每根柱子是一档曝光（输入翻倍）在 8 位屏上占的码值个数；'
                 '横轴标签是这一档的起点')
    rows = R['octaves']
    x0, x1 = 140, 1000
    y0, y1 = y + 40, y + 540
    maxv = 74
    px, py = axes(fig, x0, y0, x1, y1, (0, len(rows)), (0, maxv),
                  list(range(len(rows))), [0, 20, 40, 60],
                  '', '', xtick_labels=[fmt(r['lo']) for r in rows],
                  ytick_labels=['0', '20', '40', '60'])
    names = ['截断', 'Reinhard', 'ACES 拟合']
    bw = 24
    for i, row in enumerate(rows):
        cx = x0 + (i + 0.5) * (x1 - x0) / len(rows)
        for j, name in enumerate(names):
            v = row[name]
            bx = cx - 1.5 * bw + j * bw + 4
            fig.rect(bx, py(v), bx + bw - 8, y1, fill=COLORS[name], outline=None)
            fig.text((bx + (bw - 8) / 2, py(v) - 46), str(v), 38,
                     color=COLORS[name], anchor='ma')
    y = y1 + 118
    y = legend2(fig, y, [(n, COLORS[n]) for n in names])
    y = note(fig, y + 6, '最右一档（8 到 16）里，三条曲线都只剩个位数的码值：这段信息没地方放。')
    note(fig, y, '截断在 1 以后每一档都是 1 个码值——255 那一格，装下了从 1 到无穷的所有亮度。')
    save(fig, '03-codes-per-stop.png', '每档曝光占用的 8 位码值个数')


# ---------------------------------------------------------------- 图 04
def fig04():
    fig, y = new(4, '亮处只剩一成对比度',
                 '纵轴是「输入亮一档，屏幕亮几档」；1 = 对比度原样，0 = 彻底压平')
    x0, x1 = 150, 1000
    y0, y1 = y + 40, y + 520
    xs = [0.01 * (10 ** (i / 24.0)) for i in range(0, 73)]
    px, py = axes(fig, x0, y0, x1, y1, (0.01, 8), (0, 1.6),
                  [0.01, 0.1, 1, 8], [0, 0.5, 1, 1.5],
                  '场景亮度', '', xtick_labels=['0.01', '0.1', '1', '8'],
                  ytick_labels=['0', '0.5', '1', '1.5'], xlog=True)
    for name in ('截断', 'Reinhard', 'ACES 拟合'):
        f = curve_fn(name)
        from tone import loglog_slope
        pts = [(px(v), py(loglog_slope(f, v))) for v in xs if v <= 8]
        series(fig, pts, COLORS[name], width=6, fill=False)
    fig.line((x0, py(1)), (x1, py(1)), color=GRAY, width=3)
    fig.text((x0 + 12, py(1) - 50), '1：对比度原样', 38, color=GRAY)
    y = y1 + 118
    y = legend2(fig, y, [(n, COLORS[n]) for n in ('截断', 'Reinhard', 'ACES 拟合')])
    yy = note(fig, y + 6, 'Reinhard 在中灰处还剩 0.85，到 8 只剩 0.11：比白点亮 8 倍的地方，'
                      '再多一倍亮度的差别，屏幕上只差一成。')
    note(fig, yy, 'ACES 拟合在暗部高于 1（拉对比），在高光低于 Reinhard（压得更狠），'
                  '这是它「看着更有胶片味」的直接原因。')
    save(fig, '04-slope.png', '对数斜率（局部对比度）随输入变化')


# ---------------------------------------------------------------- 图 05
def fig05():
    fig, y = new(5, '白点定在哪里，哪里就成为纯白',
                 '横轴是 1 到 16 倍的过曝亮度，纵轴是显示值')
    x0, x1 = 150, 980
    y0, y1 = y + 40, y + 500
    px, py = axes(fig, x0, y0, x1, y1, (1, 16), (0.4, 1.05),
                  [1, 4, 8, 12, 16], [0.5, 0.7, 0.9],
                  '场景亮度（倍数）', '', xtick_labels=['1', '4', '8', '12', '16'],
                  ytick_labels=['0.5', '0.7', '0.9'])
    for name in ('Reinhard', '白点 8', 'ACES 拟合'):
        f = curve_fn(name)
        pts = []
        for i in range(0, 121):
            v = 1 + 15 * i / 120
            pts.append((px(v), py(max(min(f(v), 1.05), 0.4))))
        series(fig, pts, COLORS[name], width=6, fill=False)
    fig.line((px(8), y0), (px(8), y1), color=INK_SOFT, width=4)
    fig.text((px(8) + 16, y0 + 16), '白点 8', 38, color=INK_SOFT)
    y = y1 + 118
    y = legend2(fig, y, [(n, COLORS[n]) for n in ('Reinhard', '白点 8', 'ACES 拟合')])
    yy = note(fig, y + 6, '白点 8 的那条（青）在 8 处碰到 1，之后一路平；Reinhard 到 16 倍还只有 0.94，'
                      '屏幕看上去始终灰蒙蒙。')
    note(fig, yy, '同一件事的另一面：白点 8 的曲线在 8 之后没有任何起伏，8 倍和 16 倍的云'
                  '会变成同一块白。')
    save(fig, '05-shoulder.png', '高光段：白点选择决定的截断位置')


# ---------------------------------------------------------------- 图 06
def fig06():
    fig, y = new(6, '暗部：ACES 把它整个压下去',
                 '横轴 0 到 0.2 的场景亮度，纵轴是显示值；虚线是 y = x')
    x0, x1 = 150, 980
    y0, y1 = y + 40, y + 470
    px, py = axes(fig, x0, y0, x1, y1, (0, 0.2), (0, 0.2),
                  [0, 0.05, 0.1, 0.15, 0.2], [0, 0.05, 0.1, 0.15, 0.2],
                  '场景亮度', '',
                  xtick_labels=['0', '0.05', '0.1', '0.15', '0.2'],
                  ytick_labels=['0', '0.05', '0.1', '0.15', '0.2'])
    for i in range(0, 30):
        a = 0.2 * i / 30
        b = 0.2 * (i + 1) / 30
        fig.line((px(a), py(a)), (px(b), py(b)), color=GRAY, width=3)
    for name in ('Reinhard', 'ACES 拟合'):
        f = curve_fn(name)
        pts = [(px(0.2 * i / 120), py(f(0.2 * i / 120))) for i in range(0, 121)]
        series(fig, pts, COLORS[name], width=6, fill=False)
    fig.text((px(0.115), py(0.15)), 'ACES 拟合', 38, color=VIOLET, anchor='la')
    fig.text((px(0.145), py(0.128)), 'Reinhard', 38, color=BLUE, anchor='la')
    y = y1 + 118
    y = note(fig, y, 'Reinhard 在暗部几乎贴着虚线：小数值时 x/(1+x) 约等于 x，阴影基本不变。')
    y = note(fig, y, 'ACES 拟合在 0 处的斜率是 0.03/0.14 = 0.214，比 1 小得多：'
                     '同样的阴影，屏幕上暗了将近 5 倍。')
    save(fig, '06-toe.png', '暗部：ACES 拟合整体压暗')


# ---------------------------------------------------------------- 图 07
def fig07():
    fig, y = new(7, '渐变压成色带',
                 '每一条是把 0 到 8 的连续渐变送进曲线之后，屏幕上真正出现的颜色')
    names = ['截断', 'Reinhard', '白点 8', 'ACES 拟合']
    from tone import srgb_encode
    left, right = 210, 1014
    for r, name in enumerate(names):
        f = curve_fn(name)
        yy = y + 20 + r * 96
        fig.text((44, yy + 22), name, 40, color=COLORS[name])
        n = 260
        for i in range(n):
            v0 = 8.0 * i / n
            v1 = 8.0 * (i + 1) / n
            y0 = f(v0)
            c = int(round(srgb_encode(y0) * 255))
            hexc = '#%02x%02x%02x' % (c, c, c)
            PALETTE.add(hexc)
            fig.rect(left + i * (right - left) / n, yy,
                     left + (i + 1) * (right - left) / n - 1, yy + 74,
                     fill=hexc, outline=None)
    yy = y + 20 + len(names) * 96
    fig.text((left, yy + 10), '← 0 处', 38, color=INK_SOFT)
    fig.text((right, yy + 10), '8 倍亮度处 →', 38, color=INK_SOFT, anchor='ra')
    y = yy + 70
    for r in R['ramps']:
        pass
    y = note(fig, y, '截断那一行的右边一大段是同一格白：8192 个采样里有 7171 个落在同一个码值上，'
                     '占 87.5%。')
    y = note(fig, y, 'Reinhard 用掉 225 个码值，最长的一段重复 584 个采样；白点 8 是 238 / 316。'
                     'ACES 拟合虽然用掉 248 个码值，最长的一段却有 1661——暗部被压扁了。')
    save(fig, '07-banding.png', '连续渐变经过四条曲线后的实际色带')


# ---------------------------------------------------------------- 图 08
def fig08():
    fig, y = new(8, '按场合选那张表',
                 '左列是你手上的画面，右列是要付出的代价')
    cols = [(70, 'la'), (330, 'la'), (640, 'la'), (1010, 'ra')]
    rows = [
        [('情形', INK_SOFT, False), ('选哪条', INK_SOFT, False),
         ('还要做什么', INK_SOFT, False), ('代价', INK_SOFT, False)],
        [('先做对', RED, True), ('曝光', INK, False), ('定中灰', INK, False), ('没有', INK, False)],
        [('只要高光不乱', BLUE, True), ('Reinhard', INK, False), ('定白点', INK, False), ('中灰变暗', INK, False)],
        [('云要层次', BLUE, True), ('白点 8', INK, False), ('选好白点', INK, False), ('更高处平', INK, False)],
        [('像电影', VIOLET, True), ('ACES 拟合', INK, False), ('再调曝光', INK, False), ('暗部压暗', INK, False)],
        [('暗部要留', GREEN, True), ('Reinhard', INK, False), ('-', INK, False), ('高光更平', INK, False)],
        [('要局部对比', AMBER, True), ('局部算子', INK, False), ('-', INK, False), ('光晕', INK, False)],
    ]
    y = table(fig, y, cols, rows, row_h=72)
    y += 10
    y = note(fig, y, '「局部算子」指先算出大尺度亮度、再按比例局部压缩的做法（如双边滤波那一路），'
                     '它能把亮处对比留住，代价是亮暗交界处出现光晕。')
    save(fig, '08-decide.png', '按情形选色调映射做法')


# ---------------------------------------------------------------- 图 09
def fig09():
    fig, y = new(9, '三句话')
    items = [
        '8 位屏只有 256 格；亮过白点之后，再多亮度也只能占同一格。',
        '曲线决定的是对比度怎么分：x/(1+x) 让中灰保留 0.85、亮处只剩 0.11。',
        '动手之前先定曝光与白点；曲线只是后面那一步。',
    ]
    for i, t in enumerate(items):
        fig.text((60, y + i * 150), '%d' % (i + 1), 40, color=TEAL)
        fig.wrap((140, y + i * 150 - 6), t, 40, 860, color=INK)
    save(fig, '09-takeaways.png', '三句话')


# ---------------------------------------------------------------- 封面
def cover():
    """封面：同一段过曝场景，截断是一条白条，Reinhard 还看得出层次。"""
    from tone import srgb_encode, clamp01, reinhard
    fig = Fig(1080, width=1080)
    fig.text((60, 84), '太亮的地方', 70, bold=True)
    fig.text((60, 176), '全挤在最后一格', 70, bold=True)
    fig.text((60, 296), '色调映射：把 1000 倍亮度压进 256 格', 40, color=INK_SOFT)

    def band(y0, y1, fn, label):
        n = 216
        for i in range(n):
            v0 = 8.0 * i / n
            c = int(round(srgb_encode(fn(v0)) * 255))
            hexc = '#%02x%02x%02x' % (c, c, c)
            PALETTE.add(hexc)
            fig.rect(60 + i * 960 / n, y0, 60 + (i + 1) * 960 / n, y1,
                     fill=hexc, outline=None)
        fig.text((60, y1 + 12), label, 38, color=INK_SOFT)

    band(410, 530, clamp01, '截断：一半以上是一条白')
    band(620, 740, reinhard, 'Reinhard：同一段还看得出起伏')

    fig.rect(0, 966, 1080, 1028, fill=INK, outline=None)
    fig.text((60, 978), '原创示意 · 色调映射', 38, color=WHITE)
    fig.text((1020, 978), 'CC BY 4.0', 38, color=TINT_T, anchor='ra')
    row = fig.save(ART / 'cover.png', '文章封面')
    META.append({k: row[k] for k in ('path', 'width', 'height', 'min_label_px',
                                     'effective_min_at_354px', 'purpose', 'identity')})
    print('   cover.png', row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def main():
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09):
        f()
    cover()
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, ensure_ascii=False, indent=1) + '\n')
    print('wrote figure-metadata.json', len(META), 'figures')


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(HERE))
    main()
