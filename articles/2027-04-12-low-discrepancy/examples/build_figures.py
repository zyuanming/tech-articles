#!/usr/bin/env python3
"""《一千个点能有多准》的原创插图。MIT。

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


def fmt(x, digits=2):
    if x == 0:
        return '0'
    if abs(x) < 1e-3 or abs(x) >= 1e5:
        mant, exp = ('%.*e' % (digits - 1, x)).split('e')
        return '%se%s' % (mant, minus(int(exp)))
    return ('%.' + str(digits) + 'g') % x


# ---------------------------------------------------------------- 图 01

def fig01():
    v = R['vdc']
    fig, y = new(1, '把整数反过来写，就得到一串均匀的点',
                 'van der Corput：把 n 的二进制位翻转放到小数点右边')
    x0, x1 = 250, 950
    axis_y = y + 150
    for i in range(9):
        x = x0 + (x1 - x0) * (i / 8.0)
        fig.line((x, axis_y - 18), (x, axis_y + 18), color=INK, width=3)
        fig.text((x, axis_y + 28), ('0' if i == 0 else '%d/8' % i), 38,
                 color=INK_SOFT, anchor='ma')
    for j, (count, label, color) in enumerate(((8, '前 8 个', TEAL),
                                              (4, '前 4 个', BLUE),
                                              (2, '前 2 个', AMBER))):
        yy = axis_y + 140 + j * 96
        fig.text((44, yy - 20), label, 38, color=color, bold=True)
        for val in v['first16'][:count]:
            fig.circle(x0 + (x1 - x0) * val, yy, 14, fill=color, outline=color)
    y = axis_y + 140 + 3 * 96 + 40
    y = note(fig, y, 'n = 1、2、3、4… 的二进制是 1、10、11、100…；把位序倒过来放到小数点右边，'
                     '得到 0.1、0.01、0.11、0.001…，也就是 1/2、1/4、3/4、1/8。')
    y = note(fig, y, '这串值的脾气：每加一个点，它都落在当前最大的那个空洞正中间。'
                     '所以前 2^k 个点恰好是每条宽 1/2^k 的格子里一个，一个不多、一个不少。')
    save(fig, '01-vdc.png', 'van der Corput 序列前 8 个点的位置与嵌套结构')


# ---------------------------------------------------------------- 图 02

def fig02():
    fig, y = new(2, '256 个点，一眼分开',
                 '同一个单位正方形，同样多的点；左随机，右 Halton（基数 2 与 3）')
    pts_r = R['scatter']['random']
    pts_h = R['scatter']['halton']
    size = 380
    top = y + 20
    for k, (pts, label, color) in enumerate(((pts_r, '随机', RED),
                                            (pts_h, 'Halton', TEAL))):
        ox = 90 + k * 470
        fig.rect(ox, top, ox + size, top + size, fill=WHITE, outline=LIGHT, width=3)
        for px_, py_ in pts:
            cx = ox + px_ * size
            cy = top + size - py_ * size
            fig.circle(cx, cy, 4, fill=color, outline=color)
        fig.text((ox, top + size + 16), label, 40, color=color, bold=True)
    y = top + size + 80
    y = note(fig, y, '左边有空白的大洞，也有黏在一起的小团；右边几乎找不到比它更大的空洞，'
                     '也找不到三个点挤成一堆的地方。')
    y = note(fig, y, '这不是「更随机」，是「更均匀」——两种做法都在逼近同一个积分，'
                     '区别在于「点没落在哪里」这件事：低差异序列的答案里几乎不存在「整块区域没采过」。')
    save(fig, '02-scatter.png', '256 个随机点与 256 个 Halton 点的分布对比')


# ---------------------------------------------------------------- 图 03

def fig04():
    fig, y = new(4, '估 π 的误差：四条曲线，两种斜率',
                 '被积函数是「点是否落在四分之一圆内」，真值 π/4 = 0.78539816；纵轴是误差')
    rows = R['pi']
    ns = [r['n'] for r in rows]
    px, py = axes(fig, 200, y + 40, 880, y + 470, (16, 16384), (1e-5, 1e-1),
                  ns, [1e-5, 1e-4, 1e-3, 1e-2, 1e-1],
                  '点数 N', '',
                  xtick_labels=['16', '64', '256', '1e3', '1e4', '1.6e4', ''],
                  ytick_labels=['1e−5', '1e−4', '1e−3', '1e−2', '1e−1'],
                  xlog=True, ylog=True)
    ref = [(px(16), py(0.06)), (px(16384), py(0.06 / 32))]
    fig.line(ref[0], ref[1], color=GRAY, width=3)
    fig.line((252, y + 336), (382, y + 367), color=GRAY, width=3)
    fig.text((396, y + 326), '1/√N 的斜率', 38, color=GRAY)
    series(fig, [(px(r['n']), py(r['random_rms'])) for r in rows], RED)
    series(fig, [(px(r['n']), py(r['stratified_rms'])) for r in rows], AMBER)
    series(fig, [(px(r['n']), py(r['halton_shift_rms'])) for r in rows], BLUE)
    series(fig, [(px(r['n']), py(r['halton_err'])) for r in rows], TEAL, fill=False)
    legend = [('随机（32 组种子的 RMS）', RED, True),
              ('抖动网格', AMBER, True),
              ('Halton 平移', BLUE, True),
              ('Halton 原样', TEAL, False)]
    ly = y + 56
    for lab, col, filled in legend:
        fig.line((522, ly + 18), (566, ly + 18), color=col, width=5)
        if filled:
            fig.circle(544, ly + 18, 9, fill=col, outline=col)
        else:
            fig.circle(544, ly + 18, 9, fill=WHITE, outline=col, width=4)
        fig.text((580, ly), lab, 38, color=col)
        ly += 52
    y = y + 620
    y = note(fig, y, '两轴都取对数，所以斜率就是收敛速度。红色几乎贴着 1/√N 的灰线走。')
    y = note(fig, y, '青色那条不是直线：它在几个 N 上给出同一个值，所以既不上也不下——'
                     '第 6 张图专门看这件事。')
    save(fig, '04-error-vs-n.png', '四种采样方式估计 π/4 的误差随点数变化')


# ---------------------------------------------------------------- 图 04

def fig05():
    c = {row['key']: row for row in R['conv']}
    fig, y = new(5, '拟合出来的收敛指数：0.49 和 0.78',
                 '斜率取自上一张图的直线段；指数大 0.5 就是「同样点数误差小一个量级」')
    y0 = y + 110
    h = 300
    items = [('随机', c['random_rms']['exponent'], RED),
             ('抖动网格', c['stratified_rms']['exponent'], AMBER),
             ('Halton 平移', c['halton_shift_rms']['exponent'], BLUE)]
    x0, x1 = 320, 960
    for i, (lab, val, col) in enumerate(items):
        yy = y0 + i * 100
        fig.text((x0 - 24, yy - 20), lab, 40, color=col, anchor='ra')
        w = (x1 - x0) * (val / 1.0)
        fig.rect(x0, yy - 8, x0 + w, yy + 40, fill=col, outline=None, radius=4)
        fig.text((x0 + w + 20, yy - 2), '%.2f' % val, 40, color=INK)
    y = y0 + h
    y = note(fig, y, '随机是 0.49，也就是教科书上的 1/√N；低差异的两条在 0.69 和 0.78。'
                     '这不是 1——如果被积函数是光滑的，低差异序列能做到 1 附近；'
                     '这里被积函数在圆周上从 0 直接跳到 1，跳变把 1 拉回到 3/4 左右。')
    y = note(fig, y, 'Halton 原样那条（青）不在这里：它在 N = 64 与 256 上给出完全相同的误差，'
                     '在 1024 与 4096 上也相同，拟合一条直线没有意义。')
    save(fig, '05-exponent.png', '三种采样方式的拟合收敛指数')


# ---------------------------------------------------------------- 图 05

def fig06():
    s_ = R['stuck']
    fig, y = new(6, '翻四倍不动，翻两倍更差',
                 'Halton 前 N 个点里落在四分之一圆内的个数，以及估计值 k/N')
    cols = [(70, 'la'), (360, 'ra'), (680, 'ra'), (970, 'ra')]
    rep = {}
    for g in s_['repeats']:
        for n in g['ns']:
            rep[n] = g['fraction']
    rows = [[('点数 N', INK_SOFT, False), ('落在圆内', INK_SOFT, False),
             ('估计值 k/N', INK_SOFT, False), ('误差', INK_SOFT, False)]]
    for r in s_['rows']:
        if r['n'] < 32 or r['n'] > 16384:
            continue
        dup = rep.get(r['n']) == r['fraction']
        col = RED if dup else INK
        rows.append([(str(r['n']), col, dup),
                     (str(r['inside']), col, dup),
                     ('%.9f' % r['fraction'], col, dup),
                     (fmt(r['err']), col, dup)])
    y = table(fig, y, cols, rows, row_h=62)
    y += 16
    y = note(fig, y, '红色是「这个比值之前已经出现过」：32 与 128 都是 13/16，64 与 256 都是 51/64，'
                     '1024、2048、4096 都是 0.787109375。点数涨四倍，误差一位不动。')
    y = note(fig, y, '更难看的是 8192 与 16384 这两行：多一倍的点，误差从 8.57e−4 涨到 1.28e−3。'
                     '标称点数多了，答案却更远——这就是「没有误差棒」的后果。')
    save(fig, '06-stuck.png', 'Halton 在若干点数上给出相同估计值，且标称点数与误差不同向')


def fig07():
    b = R['bars']
    fig, y = new(7, '散布，和一个孤零零的数',
                 'N = 1024；横轴是「估计值减真值」的绝对值')
    x0, x1 = 300, 960
    top = y + 70
    vmax = max(max(b['random_errors']), max(b['shift_errors'])) * 1.05
    rows = [('随机 200 次', b['random_errors'], RED),
            ('Halton 平移 32 次', b['shift_errors'], BLUE)]
    for j, (lab, vals, col) in enumerate(rows):
        yy = top + j * 120
        fig.text((44, yy - 20), lab, 38, color=col)
        for i, v in enumerate(vals):
            xx = x0 + (x1 - x0) * v / vmax
            jit = ((i * 37) % 21 - 10) * 1.7
            fig.circle(xx, yy + jit, 6, fill=col, outline=col)
    yy = top + 260
    fig.text((44, yy - 20), 'Halton 原样', 38, color=TEAL)
    hx = x0 + (x1 - x0) * b['halton_err'] / vmax
    fig.line((hx, yy - 30), (hx, yy + 30), color=TEAL, width=5)
    fig.text((hx + 18, yy - 62), '一次，没有散布', 38, color=TEAL)
    rmsx = x0 + (x1 - x0) * b['random_rms'] / vmax
    fig.line((rmsx, top - 40), (rmsx, yy + 40), color=INK, width=3)
    fig.text((rmsx + 12, top - 76), '随机 RMS', 38, color=INK)
    fig.line((x0, yy + 66), (x1, yy + 66), color=INK, width=3)
    for tv in (0.0, 0.01, 0.02, 0.03):
        xx = x0 + (x1 - x0) * tv / vmax
        fig.line((xx, yy + 66), (xx, yy + 84), color=INK, width=3)
        fig.text((xx, yy + 92), ('0' if tv == 0 else '%.2f' % tv), 38,
                 color=INK_SOFT, anchor='ma')
    y = yy + 170
    y = note(fig, y, '随机的 200 次里，最小的误差 2.4e−4，最大的 3.6e−2；'
                     'Halton 那一个数是 1.7e−3，落在散布的中间偏左。')
    y = note(fig, y, '把 Halton 整组点平移一个随机偏移（Cranley–Patterson 平移），'
                     '散布就回来了：32 次平移的 RMS 是 3.0e−3，和随机同一量级，'
                     '但它仍然没有大洞，所以系综里的典型误差更小。')
    save(fig, '07-errorbars.png', '随机点与 Halton 的误差分布对比')


# ---------------------------------------------------------------- 图 03

def fig03():
    g = R['gaps']
    fig, y = new(3, '一维版本更清楚：最大空洞',
                 'n 个点落在 0 到 1 之间，最宽的空白有多宽')
    ns = [r['n'] for r in g]
    px, py = axes(fig, 200, y + 40, 900, y + 450, (16, 16384), (4e-5, 4e-1),
                  ns, [1e-4, 1e-2, 1e-1],
                  '点数 n', '最大空洞',
                  xtick_labels=['16', '64', '256', '1e3', '1e4', '1.6e4', ''],
                  ytick_labels=['1e−4', '1e−2', '1e−1'],
                  xlog=True, ylog=True)
    series(fig, [(px(r['n']), py(r['vdc_gap'])) for r in g], TEAL)
    series(fig, [(px(r['n']), py(r['random_gap_mean'])) for r in g], RED)
    series(fig, [(px(r['n']), py(r['log_over_n'])) for r in g], GRAY, fill=False)
    legend = [('van der Corput，正好 1/n', TEAL),
              ('随机点，32 次平均', RED),
              ('log n / n', GRAY)]
    ly = y + 316
    for lab, col in legend:
        fig.line((420, ly + 18), (470, ly + 18), color=col, width=5)
        fig.circle(445, ly + 18, 9, fill=col, outline=col)
        fig.text((486, ly), lab, 38, color=col)
        ly += 54
    y = y + 600
    y = note(fig, y, '青色那条严格等于 1/n：每个新点都插进当前最大的空洞，空洞因此一路减半。')
    y = note(fig, y, '红色的随机点按 log n / n 走——点数翻四倍，空洞只降到约六成。'
                     '这就是为什么「多采几个点」在随机采样里换不来同等的确定性。')
    save(fig, '03-gap.png', 'van der Corput 与随机点在一维上的最大空洞')


# ---------------------------------------------------------------- 图 08

def fig08():
    fig, y = new(8, '什么时候值得换',
                 '先看你需不需要误差棒，再看被积函数光不光滑')
    cols = [(70, 'la'), (372, 'la'), (1010, 'ra')]
    rows = [[('情形', INK_SOFT, False), ('做法', INK_SOFT, False), ('效果', INK_SOFT, False)],
            [('要误差棒', INK, False), ('随机点', INK, False), ('最省事', GRAY, False)],
            [('函数光滑', INK, False), ('Halton / Sobol', TEAL, False), ('快一个量级', GRAY, False)],
            [('边界有跳变', INK, False), ('仍有人用', AMBER, False), ('只快一点', GRAY, False)],
            [('要并行', INK, False), ('随机化平移', TEAL, False), ('一步搞定', GRAY, False)],
            [('维度上百', INK, False), ('优势消失', RED, False), ('得换思路', GRAY, False)],
            [('能随时停', INK, False), ('随机或分层', INK, False), ('可以随时停', GRAY, False)]]
    y = table(fig, y + 10, cols, rows, row_h=76)
    y += 24
    y = note(fig, y, '最后一行最容易被忽略：低差异序列是「按顺序的好」——前 1000 个点很好用，'
                     '不代表只取前 100 个就好。要能提前收工，就得靠随机化把顺序本身变成随机变量。')
    y = note(fig, y, '高维度那一行也不是玄学：Halton 的第 100 维用第 100 个素数做基数，'
                     '点会被摆成很细很长的条纹，投影到任意两维都不再均匀。')
    save(fig, '08-decide.png', '按情形选择采样方式的对照表')


# ---------------------------------------------------------------- 图 09

def fig09():
    fig, y = new(9, '三句话')
    items = [
        '随机点的误差按 1/√N 缩小：百万个点的误差只有一千个点的三十分之一。'
        '这不是实现问题，是概率本身的上限。',
        '低差异序列把点摆在「下一步落进最大空洞」的位置，误差按 0.7 到 0.8 次幂缩小；'
        '被积函数一跳变，速度就从 1 掉到 3/4 附近。',
        '代价是确定性：它不告诉你自己有多准，还可能连续几个点数给出同一个估计值。'
        '把整组点随机平移一次，误差棒就回来了。',
    ]
    y = bullets(fig, y + 20, items, accent=BLUE, size=40)
    save(fig, '09-takeaways.png', '三条结论')


# ---------------------------------------------------------------- 封面

def cover():
    fig = Fig(1080, width=1080)
    fig.text((60, 150), '一千个点', 104, bold=True)
    fig.text((60, 280), '能有多准', 104, bold=True)
    fig.text((60, 470), '随机采样按 1/√N 收敛；把点摆在最大空洞里，', 40, color=INK_SOFT)
    fig.text((60, 528), '同样的点数能准一个量级', 40, color=INK_SOFT)
    rows = [('N = 1024', '随机 RMS 1.4e−2，Halton 1.7e−3'),
            ('拟合指数', '随机 0.49，低差异 0.78'),
            ('N = 64 与 256', 'Halton 给出同一个估计值')]
    y = 660
    for a, b in rows:
        fig.rect(60, y - 10, 76, y + 26, fill=TEAL, outline=None, radius=4)
        fig.text((96, y - 8), a, 40, bold=True, color=INK)
        fig.text((96 + fig.width_of(a, 40, True) + 28, y - 8), b, 38, color=INK_SOFT)
        y += 82
    fig.text((1020, 993), '2027-04-12', 38, color=GRAY, anchor='ra')
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
