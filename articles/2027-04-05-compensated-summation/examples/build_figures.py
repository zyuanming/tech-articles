#!/usr/bin/env python3
"""《一亿次加法之后，和少了多少》的原创插图。MIT。

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


def series(fig, pts, color, width=5, r=9):
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=color, width=width)
    for p in pts:
        fig.circle(p[0], p[1], r, fill=color, outline=color)


def bars(fig, x0, x1, ybase, h, items, width=None, label_size=38):
    n = len(items)
    step = (x1 - x0) / n
    w = width or step * 0.58
    for i, (lab, frac, color) in enumerate(items):
        cx = x0 + step * (i + 0.5)
        top = ybase - max(3, frac * h)
        fig.rect(cx - w / 2, top, cx + w / 2, ybase, fill=color, outline=None, radius=4)
        if lab:
            fig.text((cx, ybase + 12), lab, label_size, color=INK_SOFT, anchor='ma')
    fig.line((x0, ybase), (x1, ybase), color=INK, width=3)


def fmt(x, digits=2):
    """把 1.776e-15 写成 1.8e−15 这种图里能读懂的样子。"""
    if x == 0:
        return '0'
    if abs(x) < 1e-4 or abs(x) >= 1e5:
        mant, exp = ('%.*e' % (digits - 1, x)).split('e')
        return '%s e%s' % (mant, minus(int(exp)))
    return ('%.' + str(digits) + 'g') % x


# ---------------------------------------------------------------- 图 01

def fig01():
    s = R['swallow']
    fig, y = new(1, '2^53 之后，加 1 什么也不会发生',
                 '浮点数在 2^53 处的间距是 2；加 1 正好落在两个可表示数的正中间，'
                 '取偶之后停在原地')
    base = s['base']
    y0 = y + 120
    x0, x1 = 150, 950
    fig.line((x0, y0), (x1, y0), color=INK, width=4)
    ticks = [(base, '2^53'), (base + 2, '2^53+2'), (base + 4, '2^53+4'),
             (base + 6, '2^53+6')]
    for i, (v, lab) in enumerate(ticks):
        x = x0 + (x1 - x0) * i / (len(ticks) - 1)
        fig.line((x, y0 - 18), (x, y0 + 18), color=INK, width=4)
        fig.text((x, y0 + 36), lab, 38, color=INK, anchor='ma')
    # 加 1 落在中点
    xm = x0 + (x1 - x0) / (len(ticks) - 1) * 0.5
    fig.line((xm, y0 - 90), (xm, y0 - 26), color=RED, width=4, dash=12)
    fig.circle(xm, y0, 12, fill=WHITE, outline=RED, width=5)
    fig.text((xm + 22, y0 - 116), '加 1 落在这里：没有对应的数', 38, color=RED)
    fig.circle(x0, y0, 13, fill=RED, outline=RED)
    fig.text((x0 - 4, y0 - 76), '起点', 38, color=RED)
    y = y0 + 130
    y = note(fig, y, '把 1 加十万次也一样：每次都在正中间，每次都取偶，所以总和停在 2^53。'
                     '要动，得一次加 2——那才是这个量级上真实的步长。')
    y = note(fig, y, '「小量被大和吞掉」的所有版本都是这件事：不是加法算错了，'
                     '是这个量级上根本没有更细的刻度。')
    save(fig, '01-swallow.png', '2^53 处加 1 不改变结果')


# ---------------------------------------------------------------- 图 02

def fig02():
    t = R['traces']
    fig, y = new(2, 'Kahan 丢了那个 1，Neumaier 没丢',
                 '序列是 1、1e16、−1e16，精确和是 1')

    def num(v):
        if v == 0:
            return '0'
        if abs(v) == 1:
            return minus(int(v))
        if abs(v) >= 1e15:
            m = v / 10 ** int(math.floor(math.log10(abs(v))))
            e = int(math.floor(math.log10(abs(v))))
            return minus('%de%d' % (int(m), e))
        return minus('%g' % v)

    cols = [(60, 'la'), (250, 'la'), (430, 'la'), (610, 'la'), (740, 'la'), (860, 'la')]
    rows = [[('x', INK_SOFT, False), ('y', INK_SOFT, False),
             ('t', INK_SOFT, False), ('c', INK_SOFT, False),
             ('s', INK_SOFT, False), ('c 另一法', INK_SOFT, False)]]
    for i, ks in enumerate(t['kahan_steps']):
        ns = t['neumaier_steps'][i]
        rows.append([(num(ks['x']), INK, False), (num(ks['y']), INK, False),
                     (num(ks['t']), INK, False), (num(ks['c']), RED, False),
                     (num(ks['s']), INK, False), (num(ns['c']), TEAL, False)])
    rows.append([('结果', INK_SOFT, False), ('', INK, False), ('', INK, False),
                 (num(t['kahan']), RED, True), ('', INK, False),
                 (num(t['neumaier']), TEAL, True)])
    y = table(fig, y, cols, rows, row_h=66)
    y += 6
    y = note(fig, y, '各列是 Kahan 的三步：y = x − c、t = s + y、c = (t − s) − y；'
                     '最后一列是 Neumaier 在同一串数上算出的 c。')
    y = note(fig, y, '第二行是出事的地方：s = 1、y = 1e16，相加只能得到 1e16，'
                     '丢掉的 1 本该由 c 记住。可是算 c 要减 t − s = 1e16 − 1，'
                     '这个差在 1e16 处同样只能给 1e16，于是 c 还是 0。')
    y = note(fig, y, 'Neumaier 换掉了减法的两个对象：|x| 比 |s| 大时改算 (x − t) + s，'
                     '小量 s 直接留下来，不经过两个大数相减，那个 1 就保住了。')
    save(fig, '02-trace.png', '[1, 1e16, -1e16] 上两种补偿的逐步取值')


# ---------------------------------------------------------------- 图 03

def fig03():
    fig, y = new(3, '误差随项数增长，补偿求和把它按回 0',
                 '求和 1 + 1/2 + … + 1/n，参照值是 math.fsum')
    data = R['harmonic']
    ns = [d['n'] for d in data]
    FLOOR = 1e-17
    px, py = axes(fig, 190, y + 40, 900, y + 470, (1e3, 1e6), (FLOOR, 1e-11),
                  ns, [1e-17, 1e-15, 1e-13, 1e-11],
                  '项数 n', '绝对误差',
                  xtick_labels=['1000', '10000', '100000', '1000000'],
                  ytick_labels=['0', '1e−15', '1e−13', '1e−11'],
                  xlog=True, ylog=True)
    for name, color in (('naive', RED), ('pairwise', AMBER)):
        pts = [(px(d['n']), py(max(d[name + '_err'], FLOOR))) for d in data]
        series(fig, pts, color, width=5, r=10)
    for name, color in (('kahan', TEAL), ('neumaier', BLUE)):
        pts = [(px(d['n']), py(max(d[name + '_err'], FLOOR))) for d in data]
        for p in pts:
            fig.circle(p[0], p[1], 10, fill=WHITE, outline=color, width=5)
    fig.text((px(1e3) + 8, py(1e-17) - 54), 'Kahan / Neumaier：四种规模全部精确', 38, color=TEAL)
    fig.text((px(1e6) - 10, py(data[-1]['naive_err']) - 52), 'naive', 38, color=RED, anchor='ra')
    fig.text((px(1e6) - 10, py(data[-1]['pairwise_err']) + 20), '两两相加', 38, color=AMBER, anchor='ra')
    y = y + 620
    y = note(fig, y, '空心圈在坐标轴最下面那一行，意思是这四组数据算出来与 math.fsum 逐位相同；'
                     '纵轴是对数的，标 0 的那一格只是为了把它们画出来。')
    y = note(fig, y, 'naive 的误差从 1.8e−15 长到 7.4e−13，涨了 400 倍；'
                     '两两相加（pairwise）差不多慢，但在 n = 10000 和 100000 上就掉到了 0。')
    save(fig, '03-harmonic.png', '调和级数求和：四种方法的误差随 n 变化')


# ---------------------------------------------------------------- 图 04

def fig04():
    fig, y = new(4, '同一批数，只换加法顺序',
                 '还是 1 + 1/2 + … + 1/1000000，只是把加的顺序换掉')
    data = R['order']
    errs = [d['naive_err'] for d in data]
    top = max(errs) * 1.7
    labels = ['1→1/n', '1/n→1', '打乱', '小在前']
    y0 = y + 340
    bars(fig, 90, 980, y0, 240,
         [(labels[i], d['naive_err'] / top, RED) for i, d in enumerate(data)])
    for i, d in enumerate(data):
        cx = 90 + (980 - 90) / len(data) * (i + 0.5)
        fig.text((cx, y0 - d['naive_err'] / top * 240 - 48), fmt(d['naive_err']),
                 38, color=INK, anchor='ma')
    fig.text((90, y + 110), 'naive 的绝对误差', 38, color=RED)
    y = y0 + 70
    y = note(fig, y, '最坏的原顺序 7.4e−13，最好（倒着加、或把小的排前面）4.8e−14，差 15 倍。'
                     '这四种顺序下 Kahan 都是 0：补偿求和的结果基本不受顺序影响。')
    y = note(fig, y, '「先加小的」这条老建议就是这么来的——它把误差从最坏情况拉回最好情况，'
                     '但拉不到 0；要 0，得让每一步都记住自己丢了多少。')
    save(fig, '04-order.png', '同一批数换四种加法顺序后的 naive 误差')


# ---------------------------------------------------------------- 图 05

def fig05():
    c = R['cancel']
    fig, y = new(5, '两千组抵消的短序列，谁更常算对',
                 '纵轴是与精确值逐位相同的比例；每组的符号与量级都随机，n 在 3 到 12 之间')
    y0 = y + 400
    h = 250
    scale = 1.2
    items = [('naive', c['naive_exact_share'], GRAY),
             ('Kahan', c['kahan_exact_share'], RED),
             ('Neumaier', c['neumaier_exact_share'], TEAL)]
    bars(fig, 110, 960, y0, h, [(lab, share / scale, col) for lab, share, col in items])
    for i, (lab, share, col) in enumerate(items):
        cx = 110 + (960 - 110) / 3 * (i + 0.5)
        fig.text((cx, y0 - share / scale * h - 50), '%.1f%%' % (share * 100), 40,
                 color=INK, anchor='ma')
    y = y0 + 76
    y = note(fig, y, 'Neumaier 在 %d 组里给出精确结果的占 99.94%%，Kahan 是 92.1%%，'
                     '直接相加是 86.2%%。' % c['trials'])
    y = note(fig, y, '但 Kahan 不是处处更好：有 %d 组（1.3%%）它的误差比直接相加还大。'
                     '补偿求和降低的是典型误差，不是给每条序列打包票。'
                     % c['kahan_worse_than_naive'])
    save(fig, '05-cancel.png', '抵消测试中三种方法给出精确结果的比例')


# ---------------------------------------------------------------- 图 06

def fig07():
    v = R['variance']
    fig, y = new(7, '同一个毛病在方差上更凶',
                 '数据均值 1e8、标准差 1；表里是 n 个数上算出的方差与真值之差')
    cols = [(70, 'la'), (640, 'ra'), (900, 'ra')]
    rows = [[('做法', INK_SOFT, False), ('n = 1000', INK_SOFT, False),
             ('n = 100000', INK_SOFT, False)]]
    label = {'onescan': '一次扫（减两个大数）', 'twopass': '两遍（先求均值）',
             'welford': 'Welford（边来边更新）'}
    for key in ('onescan', 'twopass', 'welford'):
        bad = key == 'onescan'
        rows.append([(label[key], INK, False),
                     (fmt(v[0][key + '_err']), RED if bad else INK, bad),
                     (fmt(v[1][key + '_err']), RED if bad else INK, bad)])
    rows.append([('真值（两遍精确算）', INK_SOFT, False), (fmt(v[0]['ref']), INK_SOFT, False),
                 (fmt(v[1]['ref']), INK_SOFT, False)])
    y = table(fig, y, cols, rows, row_h=76)
    y += 8
    y = note(fig, y, '一次扫算的是 Σx²/n − (Σx/n)²，两项都在 1e16 量级，相减之后只剩噪声：'
                     '真值 1.03 的那一行它给出 10.0，n = 100000 时给出 434。')
    y = note(fig, y, 'Welford 的误差是 2.6e−9，不是 0——它把 1e8 的均值一路带着走，'
                     '每次减法仍会掉最后几位。要逐位精确，还是得两遍遍历。')
    save(fig, '07-variance.png', '偏移数据上方差三种算法的误差')


# ---------------------------------------------------------------- 图 07

def fig06():
    ops = R['ops']
    fig, y = new(6, '代价是每个数多三次减法',
                 '内循环里对每个数要做的四则运算次数（静态计数，不是耗时）')
    y0 = y + 300
    order = [('naive', GRAY), ('pairwise', AMBER), ('kahan', RED), ('neumaier', TEAL)]
    bars(fig, 100, 970, y0, 240,
         [(name, ops[name]['total'] / 5.0, color) for name, color in order])
    for i, (name, color) in enumerate(order):
        cx = 100 + (970 - 100) / 4 * (i + 0.5)
        fig.text((cx, y0 - ops[name]['total'] / 5.0 * 240 - 48),
                 str(ops[name]['total']), 40, color=INK, anchor='ma')
    fig.text((100, y + 66), '每个数的运算次数', 38, color=INK_SOFT)
    y = y0 + 76
    y = note(fig, y, 'naive 一次加法；Kahan 一加三减（先减补偿量、再加、再把新的误差减出来）；'
                     'Neumaier 两加两减外带一次比较；两两相加摊到每个数约一次，代价在递归调用上。')
    y = note(fig, y, '这四倍的代价在多数程序里不值一提；它拦住人的地方通常是「c 得跟着一起传」——'
                     '求和变成两个状态，写成并行或向量化就不那么直接了。')
    save(fig, '06-cost.png', '四种求和方式每个数的运算次数')


# ---------------------------------------------------------------- 图 08

def fig08():
    fig, y = new(8, '什么时候值得换',
                 '先看和本身能不能表示，再看误差是不是会累积')
    cols = [(70, 'la'), (430, 'la'), (1000, 'ra')]
    rows = [[('情形', INK_SOFT, False), ('做法', INK_SOFT, False), ('代价', INK_SOFT, False)],
            [('几十个数', INK, False), ('直接加', INK, False), ('0', GRAY, False)],
            [('几万到几亿个数', INK, False), ('Kahan / Neumaier', INK, False),
             ('4 次运算', GRAY, False)],
            [('正负抵消严重', INK, False), ('Neumaier', TEAL, False), ('多一次比较', GRAY, False)],
            [('要逐位精确', INK, False), ('fsum', INK, False), ('更贵，但确定', GRAY, False)],
            [('和超出表示范围', INK, False), ('换表示', RED, False), ('算法救不了', GRAY, False)],
            [('方差、协方差', INK, False), ('两遍或 Welford', INK, False), ('1 或 2 遍', GRAY, False)]]
    for i, row in enumerate(rows):
        if i % 2 == 1:
            fig.rect(48, y - 14, 1014, y + 58, fill=PALE, outline=None)
        for (text, color, bold), (x, anchor) in zip(row, cols):
            if not text:
                continue
            fig.text((x, y + 2), text, 38, bold=bold, color=color, anchor=anchor)
        y += 74
    y += 20
    y = note(fig, y, '最后两行是这一篇最想让人记住的边界：补偿求和修的是「加的过程丢东西」，'
                     '不是「结果存不下」。1e16 + 0.01 在双精度里就是 1e16，换什么算法都一样。')
    save(fig, '08-decide.png', '按情形选择求和方式的对照表')


# ---------------------------------------------------------------- 图 09

def fig09():
    fig, y = new(9, '三句话')
    items = [
        '误差不是加错了，是加不进去：和到了 2^53 这个量级，1 就是两个刻度正中间的那一点，'
        '四舍六入之后消失。',
        '补偿求和把那一点单独存起来、下一步补回去，于是百万项的和能逐位精确；'
        '代价是每个数多三次减法。',
        '它不是保险：正负抵消厉害时 Kahan 仍会翻车（20000 组里 263 组比直接加还差），'
        '而和本身超出表示范围时，任何算法都救不了。',
    ]
    y = bullets(fig, y + 20, items, accent=RED, size=40)
    save(fig, '09-takeaways.png', '三条结论')


# ---------------------------------------------------------------- 封面

def cover():
    fig = Fig(1080, width=1080)
    fig.text((60, 150), '一亿次加法之后', 104, bold=True)
    fig.text((60, 280), '和少了多少', 104, bold=True)
    fig.text((60, 470), '1965 年，Kahan 在每一步都记下丢掉的那一点，', 40, color=INK_SOFT)
    fig.text((60, 528), '下一步再补回去', 40, color=INK_SOFT)
    rows = [('2^53', '加 1 什么也不会发生'),
            ('调和级数 1e6 项', '直接加差 7.4e−13'),
            ('20000 组抵消', 'Kahan 有 263 组不如直接加')]
    y = 660
    for a, b in rows:
        fig.rect(60, y - 10, 76, y + 26, fill=RED, outline=None, radius=4)
        fig.text((96, y - 8), a, 40, bold=True, color=INK)
        fig.text((96 + fig.width_of(a, 40, True) + 28, y - 8), b, 38, color=INK_SOFT)
        y += 82
    fig.text((1020, 993), '2027-04-05', 38, color=GRAY, anchor='ra')
    row = fig.save(ART / 'cover.png', '文章封面')
    META.append(row)
    print('   cover.png', row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def main():
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09):
        f()
    cover()
    (HERE / 'figure-metadata.json').write_text(json.dumps(META, indent=1))
    print('wrote', HERE / 'figure-metadata.json', len(META), 'figures')


if __name__ == '__main__':
    main()
