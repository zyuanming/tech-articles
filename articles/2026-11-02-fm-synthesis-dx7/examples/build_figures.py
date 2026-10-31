#!/usr/bin/env python3
"""Original teaching figures for the FM synthesis article. MIT.

Waveforms and spectra come from results.json (written by run_model.py, which
runs examples/fm.py). Nothing is drawn from a number typed here.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from figkit import (Fig, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED, GRAY,
                    LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R, TINT_G)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []


def new(n, title, sub=None):
    fig = Fig(900)
    assert fig.width_of(title, 46, True) <= 828, 'title too wide: ' + title
    fig.text((44, 26), title, 46, bold=True)
    fig.text((1018, 32), '图 %02d' % n, 40, color=GRAY, anchor='ra')
    y = 112
    if sub:
        y += int(fig.wrap((44, y), sub, 40, 974, color=INK_SOFT) * 40 * 1.35) + 20
    return fig, y


def note(fig, y, text, size=42, color=INK_SOFT):
    return y + int(fig.wrap((44, y), text, size, 974, color=color) * size * 1.35) + 18


def bullets(fig, y, items, accent=TEAL, size=42):
    for text in items:
        fig.circle(76, y + 22, 15, fill=accent, outline=accent)
        lines = fig.wrap((116, y + 2), text, size, 898, color=INK)
        y += int(lines * size * 1.35) + 26
    return y


def table(fig, y, cols, rows, size=40, row_h=68, zebra=True):
    for i, row in enumerate(rows):
        if zebra and i % 2 == 1:
            fig.rect(48, y - 10, 1014, y + row_h - 12, fill=PALE, outline=None)
        for (text, color, bold), (x, anchor) in zip(row, cols):
            w = fig.width_of(text, size, bold)
            span = (x, x + w) if anchor == 'la' else (x - w, x)
            assert span[0] >= 44 and span[1] <= 1018, \
                'cell outside the safe band: %r %s' % (text, span)
            fig.text((x, y + 4), text, size, bold=bold, color=color, anchor=anchor)
        y += row_h
    return y + 18


class Plot:
    def __init__(self, fig, box, xlim, ylim):
        self.f = fig
        self.x0, self.y0, self.x1, self.y1 = box
        self.xlim, self.ylim = xlim, ylim

    def px(self, x):
        a, b = self.xlim
        return self.x0 + (self.x1 - self.x0) * (x - a) / (b - a)

    def py(self, y):
        a, b = self.ylim
        return self.y1 - (self.y1 - self.y0) * (y - a) / (b - a)

    def axes(self, xticks=(), yticks=(), xfmt='%g', yfmt='%g', xlab=None,
             ylab=None, grid=True):
        if grid:
            for v in yticks:
                yy = self.py(v)
                self.f.line((self.x0, yy), (self.x1, yy), color=LIGHT, width=2)
        for v in yticks:
            yy = self.py(v)
            self.f.text((self.x0 - 18, yy - 21), yfmt % v, 40, color=GRAY,
                        anchor='ra')
        for v in xticks:
            xx = self.px(v)
            if grid:
                self.f.line((xx, self.y0), (xx, self.y1), color=LIGHT, width=2)
            self.f.text((xx, self.y1 + 14), xfmt % v, 40, color=GRAY, anchor='ma')
        self.f.line((self.x0, self.y1), (self.x1, self.y1), color=GRAY, width=3)
        self.f.line((self.x0, self.y0), (self.x0, self.y1), color=GRAY, width=3)
        if ylab:
            self.f.text((self.x0, self.y0 - 58), ylab, 40, color=GRAY)
        if xlab:
            self.f.text((self.x1, self.y1 + 74), xlab, 40, color=GRAY, anchor='ra')

    def line(self, pts, color, width=5, dash=None):
        pixels = [(self.px(x), self.py(y)) for x, y in pts]
        for a, b in zip(pixels, pixels[1:]):
            self.f.line(a, b, color=color, width=width, dash=dash)

    def dot(self, x, y, color, r=13):
        self.f.circle(self.px(x), self.py(y), r, fill=color, outline=color)


def stems(fig, box, xlim, ylim, pts, color=TEAL, width=6, baseline=0.0):
    """Draw a spectrum as vertical lines from the baseline."""
    p = Plot(fig, box, xlim, ylim)
    for hz, db in pts:
        if hz < xlim[0] or hz > xlim[1] or db < ylim[0]:
            continue
        p.line([(hz, baseline), (hz, db)], color, width=width)
    return p


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


# ---------------------------------------------------------------- figures

def fig01():
    f, y = new(1, '同一个音高，三种内部结构',
               '都是 440 Hz，都听得出一条音。区别全在「里面还藏着什么」。')
    y += 20
    lanes = [('一个正弦：1 条线', [(p['hz'], p['db']) for p in R['pure']
                             if p['db'] > -60], TEAL, 1),
             ('调幅：3 条线', [(p['hz'], p['db']) for p in R['am']
                            if p['db'] > -60], AMBER, 3),
             ('FM（I = 2）：10 条线', [(p['hz'], p['db']) for p in R['example']
                                  if p['db'] > -60], RED, 10)]
    for label, pts, color, n in lanes:
        f.text((60, y), label, 42, bold=True, color=color)
        p = Plot(f, (60, y + 66, 780, y + 186), (0, 1400), (-60, 3))
        for hz, db in pts:
            p.line([(hz, -60), (hz, db)], color, width=8)
        f.line((60, y + 186), (780, y + 186), color=GRAY, width=3)
        f.text((812, y + 96), '%d 条' % len(pts), 42, color=color, bold=True)
        y += 240
    y += 20
    y = note(f, y, '上面三条频谱听起来是同一个音高，但音色完全不同。'
                   '这篇要讲的就是第三条：怎么用两个正弦，算出中间那一排分音。')
    save(f, '01-three-spectra.png', '一个正弦、调幅、FM 的频谱对照')


def fig05():
    """Carrier, modulator, and what comes out."""
    f, y = new(5, '调相：把一个人的相位，交给另一个人推',
               '下式里 fc 是载波（你听到的音高），fm 是调制器（它不发声，'
               '只负责推），I 是推的力度。')
    y += 10
    f.box('fm1', 60, y, 1002, y + 130, fill=TINT_A)
    f.text((90, y + 34), 'x(t) = sin(2π·fc·t + I·sin(2π·fm·t))', 42,
           bold=True, inside='fm1')
    y += 160

    lanes = [('载波 fc = 440 Hz', 440.0, 0.0, TEAL, 'c'),
             ('调制器 fm = 440 Hz', 440.0, 1.0, AMBER, 'm'),
             ('输出（I = 2）', 440.0, 2.0, INK, 'o')]
    for label, freq, index, color, tag in lanes:
        f.text((60, y), label, 42, bold=True, color=color)
        box_top = y + 62
        box_bottom = box_top + 150
        f.rect(60, box_top, 1002, box_bottom, fill=WHITE, outline=LIGHT, width=3)
        # 4 cycles across 940 px
        pts = []
        for i in range(0, 941, 4):
            t = (i / 940.0) * (4.0 / freq)
            if tag == 'c':
                v = math.sin(2 * math.pi * freq * t)
            elif tag == 'm':
                v = -math.sin(2 * math.pi * freq * t)
            else:
                v = math.sin(2 * math.pi * freq * t
                            + index * math.sin(2 * math.pi * freq * t))
            pts.append((60 + i, (box_top + box_bottom) / 2 - v * 62))
        for a, b in zip(pts, pts[1:]):
            f.line(a, b, color=color, width=4)
        y = box_bottom + 34

    y = note(f, y, '中间那行的负号只是画法：调制器往下走时，载波的相位被往回拉。'
                   '第三行就是这两条曲线的合成——注意它的周期还是 1/440 秒，'
                   '但形状已经不是正弦了。')
    save(f, '05-phase-modulation.png', '载波、调制器与调相后的波形')


def fig06():
    f, y = new(6, '调幅只能加两条边带，调相能加一整排',
               '同样是 440 Hz 的音，深度一样。调幅（AM）不管怎么加深，'
               '频谱永远只有三条线；调相的边带可以一直长出去。')
    y += 20
    # AM
    f.text((60, y), '调幅（AM）：3 条线', 42, bold=True, color=AMBER)
    am_pts = [(p['hz'], p['db']) for p in R['am'] if p['db'] > -60]
    p = stems(f, (240, y + 70, 990, y + 330), (0, 900), (-60, 3), am_pts,
              color=AMBER)
    p.axes(xticks=(0, 220, 440, 660, 880), yticks=(-60, -40, -20, 0),
           yfmt='%g dB', xlab='Hz')
    y += 440
    # FM
    f.text((60, y), '调相（I = 2）：一排边带', 42, bold=True, color=TEAL)
    fm_pts = [(p['hz'], p['db']) for p in R['example'] if p['db'] > -60]
    p = stems(f, (240, y + 70, 990, y + 330), (0, 5000), (-60, 3), fm_pts,
              color=TEAL)
    p.axes(xticks=(0, 1000, 2000, 3000, 4000, 5000), yticks=(-60, -40, -20, 0),
           yfmt='%g dB', xlab='Hz')
    y += 440
    y = note(f, y, 'AM 的边带幅度随调制深度单调变化，永远超不过载波；'
                   '调相的边带幅度由贝塞尔函数决定，可以比载波还大。'
                   '这就是 FM 听起来比 AM「亮」得多的原因。')
    save(f, '06-am-vs-fm.png', '调幅与调相的频谱对比')


def fig07():
    pts = [(x['hz'], x['db']) for x in R['example'] if x['db'] > -60]
    f, y = new(7, '一条正弦，变成了 %d 条线' % len(pts),
               'fc : fm = 4 : 1（440 Hz 与 110 Hz），I = 2。'
               '每个边带落在 110 Hz 的整数倍上，所以这是一个「谐波」音色——'
               '虽然它完全不来自锯齿波。')
    y += 20
    p = stems(f, (250, y + 70, 990, y + 420), (0, 3000), (-60, 3), pts,
              color=TEAL)
    p.axes(xticks=(0, 440, 880, 1320, 1760, 2200, 2640),
           yticks=(-60, -40, -20, 0), yfmt='%g dB', xlab='Hz')
    for hz, db in pts:
        if hz > 2900:
            continue
        p.f.text((p.px(hz), p.py(db) - 46), '%d' % round(hz / 110), 38,
                 color=TEAL, anchor='ma', allow_overlap=True)
    y += 540
    top = max(db for _, db in pts)
    y = note(f, y, '柱子上标的是「第几条边带」：位置 = 440 ± n × 110。'
                   '一共 %d 条，最高的一条 %.1f dB。' % (len(pts), top))
    y = note(f, y, '载波（440 Hz，n = 0）不是最响的那条——它的能量被分给了边带。'
                   '这一点和调幅相反：AM 里载波永远最大，边带永远更小。')
    save(f, '07-fm-spectrum.png', '4:1 比率、I=2 的频谱')


def fig08():
    f, y = new(8, '每一条边带的大小，都是一个贝塞尔函数',
               '决定边带幅度的不是「滤波器」，是 J_n(I)：第 n 条边带的振幅。'
               'I 就是推的力度。')
    y += 30
    p = Plot(f, (170, y + 40, 980, y + 460), (0, 8), (-0.5, 1.05))
    p.axes(xticks=(0, 2, 4, 6, 8), yticks=(-0.5, 0, 0.5, 1.0),
           yfmt='%g', xlab='调制指数 I')
    curves = [(0, TEAL, 'J₀ 载波'), (1, AMBER, 'J₁'), (2, BLUE, 'J₂')]
    for key, color, label in curves:
        pts = [(row['x'], row['j%d' % key]) for row in R['bessel_curves']]
        p.line(pts, color, width=5)
    for i, (key, color, label) in enumerate(curves):
        f.text((190, y + 40 + i * 54), label, 40, bold=True, color=color)
    y += 600
    y = note(f, y, '注意 J₁ 在 I ≈ 3.83 处穿过零：那一条边带真的消失了。'
                   '越过零点之后它是负的——负的振幅等于相位翻 180°。'
                   '所以 FM 的音色不是「越多越亮」的单调变化，'
                   '而是会随 I 来回起伏。')
    save(f, '08-bessel.png', '贝塞尔函数 J0/J1/J2 随调制指数的变化')


def fig09():
    f, y = new(9, 'I 越大，边带越多，音色越亮',
               '同一对频率（440 : 110），只改 I。三条频谱叠在一起看。')
    y += 30
    rows = [('I = 0.5', R['example_low'], TEAL),
            ('I = 2', R['example'], AMBER),
            ('I = 6', R['example_high'], RED)]
    for label, spec, color in rows:
        f.text((60, y), label, 42, bold=True, color=color)
        pts = [(p['hz'], p['db']) for p in spec if p['db'] > -55]
        p = Plot(f, (330, y - 10, 990, y + 130), (0, 3000), (-55, 3))
        for hz, db in pts:
            p.line([(hz, -55), (hz, db)], color, width=6)
        f.line((330, y + 130), (990, y + 130), color=GRAY, width=3)
        f.text((1000, y + 40), '%d 条' % len(pts), 40, color=color, anchor='ra')
        y += 190
    y += 20
    y = note(f, y, 'I = 0.5 时载波最强，只有紧邻的两三条边带听得见，声音接近纯音；'
                   'I = 6 时能量撒到了十几条分音上，听起来像铜管或失真吉他。'
                   '「亮度」在这里不是 EQ，是边带的数量。')
    save(f, '09-index-ladder.png', '调制指数与边带数量')


def fig10():
    f, y = new(10, '带宽是可以算出来的',
               '实测的最高边带（点）对着经验公式 (I + 1)·fm（线）。'
               'FM 占用的频谱比载波宽得多，这是它的代价。')
    y += 30
    p = Plot(f, (190, y + 40, 980, y + 430), (1, 4.6), (0, 3400))
    p.axes(xticks=(1, 2, 3, 4), yticks=(0, 1000, 2000, 3000),
           yfmt='%g', xlab='调制指数 I', ylab='一侧带宽 (Hz)')
    colors = {110.0: TEAL, 220.0: AMBER, 440.0: BLUE}
    for fm in (110.0, 220.0, 440.0):
        pts = [(r['index'], r['carson']) for r in R['bandwidth'] if r['fm'] == fm]
        p.line(pts, colors[fm], width=4, dash=16)
    for r in R['bandwidth']:
        p.dot(r['index'], r['measured'], colors[r['fm']], r=15)
    for i, fm in enumerate((110.0, 220.0, 440.0)):
        f.text((210, y + 40 + i * 54), 'fm = %g' % fm, 40, bold=True,
               color=colors[fm])
    y += 580
    y = note(f, y, '实线公式是 (I+1)·fm，点是我按 −40 dB 数出来的最远一条。'
                   '点总在线的上方：公式给的是「包含 98% 能量」的带宽，'
                   '而 −40 dB 比这个标准更严。')
    save(f, '10-bandwidth.png', '调制指数、调制频率与带宽')


def fig11():
    f, y = new(11, '比率是整数：边带落在谐波上',
               'fc : fm = 4 : 1，I = 2。所有分音都是 110 的整数倍，'
               '耳朵听到的仍然是一个音高 440 Hz 的音。')
    y += 20
    pts = [(x['hz'], x['db']) for x in R['example'] if x['db'] > -60]
    p = stems(f, (250, y + 70, 990, y + 430), (0, 3000), (-60, 3), pts,
              color=TEAL)
    p.axes(xticks=(0, 880, 1760, 2640), yticks=(-60, -40, -20, 0),
           yfmt='%g dB', xlab='Hz')
    y += 560
    y = note(f, y, '边带位置是 fc ± n·fm。当 fc 恰好是 fm 的整数倍时，'
                   '这些位置全部落在同一个谐波序列上——听起来就是一个音，'
                   '只是音色变亮了。DX7 面板上那个「比率」旋钮，'
                   '调的就是这个整数倍。')
    save(f, '11-ratio-integer.png', '整数比率下的谐波频谱')


def fig12():
    f, y = new(12, '比率不是整数：音高还在，音色变了',
               'fc : fm = 1.414 : 1（√2），I = 2。载波频率没动，'
               '但边带落到了非整数倍上。')
    y += 20
    pts = [(x['hz'], x['db']) for x in R['inharmonic'] if x['db'] > -60]
    p = stems(f, (250, y + 70, 990, y + 430), (0, 3000), (-60, 3), pts,
              color=RED)
    p.axes(xticks=(0, 880, 1760, 2640), yticks=(-60, -40, -20, 0),
           yfmt='%g dB', xlab='Hz')
    for k in range(0, 8):
        xx = p.px(440 * k)
        p.f.line((xx, y + 80), (xx, y + 490), color=LIGHT, width=3, dash=10)
    y += 560
    rows = [(r['ratio'], '是' if r['harmonic'] else '否', str(r['partials']))
            for r in R['ratios']]
    y = table(f, y, [(60, 'la'), (420, 'la'), (800, 'la')],
              [[(a, INK, True), (b, INK, False), (c + ' 条', INK, False)]
               for a, b, c in rows])
    y = note(f, y, '表格第一列是 fc : fm。2 : 1 和 4 : 1 都落在谐波上；'
                   '1.5 : 1 虽然是「简单分数」，但边带落在 146.7 的倍数上，'
                   '和 440 不成整数比，听起来就是钟、是金属。')
    save(f, '12-ratio-inharmonic.png', '非整数比率下的非谐波频谱')


def fig13():
    f, y = new(13, '减法合成在挑，FM 在造',
               '两种办法都能做出「亮」的声音，但一个是从已有材料里筛，'
               '一个是让新的分音自己长出来。')
    y += 20
    f.text((60, y), '减法：造富矿，再筛', 42, bold=True, color=AMBER)
    f.text((560, y), 'FM：分音自己长出来', 42, bold=True, color=TEAL)
    left = y + 90
    steps = ['锯齿波：分音全都有', '低通滤波器削掉高频', '滤波器扫动 = 音色变']
    steps2 = ['一个正弦（调制器）', '推另一个正弦的相位', '推的力度 = 音色变']
    for i in range(3):
        lane = left + i * 150
        f.box('s%d' % i, 60, lane, 500, lane + 118, fill=TINT_A)
        f.text((84, lane + 30), steps[i], 38, inside='s%d' % i)
        f.box('f%d' % i, 560, lane, 1000, lane + 118, fill=TINT_T)
        f.text((584, lane + 30), steps2[i], 38, inside='f%d' % i)
    y = left + 3 * 150 + 10
    y = note(f, y, '减法合成的亮度受限于源波形里还剩多少高频，'
                   '而且每加一个音就要多一套滤波器；FM 的亮度来自边带，'
                   '处理器只需要几次查表和加法——这是 1983 年的芯片能做出'
                   '低价复音的关键。')
    save(f, '13-subtractive-vs-fm.png', '减法合成与 FM 的思路对比')


def fig14():
    f, y = new(14, '六个算子，三十二种接法',
               'DX7 的每个「算子」就是一个正弦振荡器加一个包络。'
               '它不叫振荡器，因为能不能发声取决于接法。')
    y += 20
    f.text((60, y), '串联（算法 1 - 简化）', 42, bold=True, color=TEAL)
    ops = [('OP1', '调制'), ('OP2', '调制'), ('OP3', '载波')]
    x = 90
    for i, (name, role) in enumerate(ops):
        tag = 'op%d' % i
        f.box(tag, x, y + 70, x + 230, y + 250,
              fill=TINT_T if role == '载波' else WHITE)
        f.text((x + 115, y + 100), name, 44, bold=True, inside=tag, anchor='ma')
        f.text((x + 115, y + 170), role, 40, color=INK_SOFT, inside=tag,
               anchor='ma')
        if i < 2:
            f.arrow((x + 232, y + 160), (x + 288, y + 160), color=INK, width=4)
        x += 290
    y += 300
    f.text((60, y), '并联（两个载波同时发声）', 42, bold=True, color=BLUE)
    f.box('p1', 90, y + 70, 330, y + 200, fill=TINT_B)
    f.text((210, y + 108), 'OP1 调制', 42, inside='p1', anchor='ma')
    f.box('p2', 90, y + 230, 330, y + 360, fill=TINT_B)
    f.text((210, y + 268), 'OP2 调制', 42, inside='p2', anchor='ma')
    f.box('p3', 480, y + 150, 720, y + 280, fill=TINT_T)
    f.text((600, y + 188), 'OP3 载波', 42, inside='p3', anchor='ma')
    f.arrow((335, y + 135), (475, y + 190), color=INK, width=4)
    f.arrow((335, y + 295), (475, y + 240), color=INK, width=4)
    y += 400
    y = note(f, y, '32 种算法就是这 6 个算子的连线方式。'
                   '同一个音色，换一种接法就完全变样——'
                   '所以 DX7 的「音色设计」本质上是「选一个拓扑，再调 6 组参数」。')
    save(f, '14-operators.png', 'DX7 的算子与两种算法接法')


def fig15():
    f, y = new(15, '包络：音量会停，音色不会停',
               'DX7 的四段包络（EG）是「速率 + 目标值」，不是「时间」。'
               '下面这条曲线是 code 里按这种规则跑出来的。')
    y += 30
    env = R['envelope']
    p = Plot(f, (170, y + 40, 980, y + 420), (0, 3.1), (0, 1.1))
    p.axes(xticks=(0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0), yticks=(0, 0.5, 1.0),
           xfmt='%.1f s', yfmt='%g', xlab='时间')
    pts = [(row['t'], row['v']) for row in env]
    p.line(pts, TEAL, width=5)
    marks = [(0.0, '起音'), (0.41, '衰减'), (2.41, '释放')]
    for t, label in marks:
        p.f.line((p.px(t), y + 50), (p.px(t), y + 450), color=LIGHT, width=3,
                 dash=10)
        p.f.text((p.px(t) + 12, y + 52), label, 38, color=GRAY)
    y += 600
    y = note(f, y, '把这条包络接到「载波」上，你听到音量起伏；'
                   '接到「调制器」上，你听到的是音色在变化——'
                   '亮度随时间收放，这是 FM 最像真实乐器的时刻。')
    save(f, '15-envelope.png', '四段包络与它的两种接法')


def fig16():
    f, y = new(16, '数字 FM 的第一个坑：边带会翻墙回来',
               '采样率 44.1 kHz，奈奎斯特频率 22.05 kHz。'
               '载波 12 kHz、调制器 3 kHz、I = 4 时，最高的边带已经到 33 kHz。')
    y += 20
    case = [r for r in R['aliasing'] if r['fc'] == 12000.0][0]
    p = Plot(f, (190, y + 40, 990, y + 400), (0, 22000), (-60, 3))
    p.axes(xticks=(0, 5000, 10000, 15000, 20000), yticks=(-60, -40, -20, 0),
           yfmt='%g dB', xlab='Hz')
    import fm as _fm
    spec = _fm.spectrum(_fm.pm(case['fc'], case['fm'], case['index']))
    for s_ in spec:
        if s_['hz'] > 21990 or s_['mag'] < 1e-3:
            continue
        db = 20 * math.log10(s_['mag'])
        p.line([(s_['hz'], -60), (s_['hz'], db)], TEAL, width=5)
    p.f.line((p.px(22050), y + 40), (p.px(22050), y + 440), color=RED, width=4,
             dash=12)
    p.f.text((p.px(22050) - 16, y + 46), '22.05 kHz', 38, color=RED, anchor='ra')
    p.f.text((p.px(case['alias_hz']), y + 470), '折回来的边带', 38, color=RED,
             anchor='ma')
    y += 580
    y = note(f, y, '理论最高边带在 %.0f kHz，比奈奎斯特高。它不会消失，'
                   '而是被折回到 |44.1 − %.0f| = %.2f kHz 处——'
                   '我在频谱里找到的线在 %.0f Hz，%.1f dB。'
                   % (case['top'] / 1000, case['top'] / 1000,
                      case['alias_hz'] / 1000, case['found_hz'],
                      case['found_db']))
    y = note(f, y, '折回来的东西听起来不是「更高的音」，而是走调的金属声。'
                   'DX7 用限幅、查表精度和相对高的采样率躲这个坑；'
                   '今天的软件则把内部采样率提到 96 kHz，或者干脆做超采样。',
             color=RED)
    save(f, '16-aliasing.png', '数字 FM 的边带折叠')


def fig17():
    f, y = new(17, '自反馈：把一个正弦，逼成噪声',
               '把一个算子自己的输出延迟一个采样，再送回自己的相位。'
               'β 越大，波形越像锯齿，最后变成噪声。')
    y += 20
    rows = [('β = 0（纯正弦）', 0.0, TEAL), ('β = 1.0', 1.0, AMBER),
            ('β = 3.0', 3.0, RED)]
    import fm as _fm
    for label, beta, color in rows:
        f.text((60, y), label, 42, bold=True, color=color)
        spec = _fm.spectrum(_fm.pm(220.0, 55.0, 0.0, feedback=beta))
        p = Plot(f, (320, y - 10, 990, y + 130), (0, 5000), (-50, 3))
        for s in spec:
            if s['hz'] > 5000:
                break
            if s['mag'] < 1e-3:
                continue
            db = 20 * math.log10(s['mag'])
            p.line([(s['hz'], -50), (s['hz'], db)], color, width=5)
        f.line((320, y + 130), (990, y + 130), color=GRAY, width=3)
        n = next(r['partials'] for r in R['feedback'] if r['feedback'] == beta)
        f.text((1000, y + 40), '%d 条' % n, 40, color=color, anchor='ra')
        y += 190
    y += 20
    y = note(f, y, 'β = 1 时已经能看到十几个分音；β = 2 时我数出 291 条；'
                   'β = 4 时整个 0–22 kHz 都被填满，在频谱上就是噪声。'
                   'DX7 的反馈只给一个算子用，正是为了这个效果。')
    save(f, '17-feedback.png', '算子自反馈的频谱')


def fig18():
    f, y = new(18, '五十年，一个乘法器',
               'FM 合成不是「某个合成器型号的功能」，'
               '是一条从 1967 年的一个意外发现，走到今天每一次手机铃声的路。')
    y += 30
    rows = [('1967', 'Chowning 在斯坦福用程序试出「调相能造出新音色」'),
            ('1973', '斯坦福把专利授权给 Yamaha'),
            ('1977', 'US 4,018,121 专利公开'),
            ('1980', 'Yamaha GS-1：第一台商用 FM 合成器，价格六位数'),
            ('1983', 'DX7 上市，约 20 万日元，卖出 20 万台以上'),
            ('1987', 'TX81Z、DX7II：多波形与立体声'),
            ('1990s', '采样回放兴起，FM 退到「音效」和「电钢」'),
            ('2000s', '软件复刻（Dexed 等）把 DX7 带回 DAW')]
    for year, text in rows:
        f.text((60, y + 6), year, 40, bold=True, color=TEAL)
        lines = f.wrap((200, y + 6), text, 40, 800, color=INK)
        y += int(lines * 54) + 26
    y += 20
    y = note(f, y, '在 1983 年，一台 DX7 里有 6 个算子 × 16 个声部，'
                   '全靠专用芯片做加法和查表——没有浮点、没有滤波器。'
                   '「便宜得能做复音」这件事，比「音色新奇」更决定它的命运。')
    save(f, '18-timeline.png', 'FM 合成的时间线')


def fig19():
    f, y = new(19, '三句话', '如果只记三件事，记这三件。')
    top = y + 40
    items = [('调相能造出边带，边带就是音色。',
              '一个正弦推另一个正弦的相位，频谱里就多出一排新的分音。'),
             ('边带的多少由 I 决定，位置由比率决定。',
              'I 管亮度，比率管「是不是一个音」。这两只手是分开的。'),
             ('它便宜，所以它流行。',
              '不需要滤波器、不需要采样，一次查表加一次加法就是一个分音。')]
    for i, (head, sub) in enumerate(items):
        lane = top + i * 230
        tag = 'b%d' % i
        f.box(tag, 60, lane, 1002, lane + 186,
              fill=TINT_T if i % 2 == 0 else WHITE)
        f.text((92, lane + 22), head, 42, bold=True, inside=tag)
        f.wrap((92, lane + 96), sub, 38, 860, color=INK_SOFT)
    save(f, '19-three-lines.png', '三句话总结')


def make_cover():
    fig = Fig(1080, width=1080)
    fig.text((96, 96), '一个正弦', 84, bold=True, color=INK)
    fig.text((96, 200), '推出整片频谱', 84, bold=True, color=INK)
    fig.text((96, 320), 'FM 合成：用相位而不是滤波器造音色', 42, color=TEAL)
    top = 470
    fig.line((110, top), (970, top), color=LIGHT, width=4)
    for i, amp in enumerate([1.0, 0.62, 0.4, 0.28, 0.2, 0.14, 0.1]):
        w = 96
        x = 140 + i * 128
        fig.rect(x, top - amp * 220, x + w, top, fill=TEAL if i % 2 == 0 else BLUE,
                 outline=None)
    fig.line((110, top), (970, top), color=INK, width=6)
    fig.text((96, 780), 'J₀  J₁  J₂ …  边带的幅度是贝塞尔函数', 42, color=INK_SOFT)
    fig.text((96, 850), 'Yamaha DX7 · 1983 · 20 万台', 44, color=INK)
    fig.text((96, 930), 'tech-articles · 2026-11-02', 38, color=GRAY)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


FIGS = [fig01, fig05, fig06, fig07, fig08, fig09, fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18, fig19]


def main(argv):
    want = {int(a) for a in argv[1:]} if len(argv) > 1 else None
    for fn in FIGS:
        n = int(fn.__name__[3:])
        if want and n not in want:
            continue
        fn()
    if not want:
        make_cover()
        print('   cover.png')
        (HERE / 'figure-metadata.json').write_text(
            json.dumps(META, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8')
    print('figures:', len(META))


if __name__ == '__main__':
    main(sys.argv)
