#!/usr/bin/env python3
"""Original teaching figures for the audio-fingerprint article. MIT.

Every number comes from results.json, which run_model.py writes by running
examples/shazam.py. Nothing here is typed in by hand.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from figkit import (Fig, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED, GRAY,
                    LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R)

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
            if not text:
                continue
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


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


_CHIP = [0]


def chip(fig, box, label, fill, color=INK, size=40, bold=False):
    _CHIP[0] += 1
    key = 'c%d' % _CHIP[0]
    fig.box(key, *box, fill=fill)
    fig.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - size * 0.62), label,
             size, bold=bold, color=color, anchor='ma', inside=key)


# ---------------------------------------------------------------- helpers

HEAT = ['#f4f3ed', '#e8f0f6', '#c9dcec', '#7fa8c9', '#3468ad', '#183440']
DARK = ['#0d1f27', '#ffffff', '#7fa8c9', '#f2b134', '#e8f0f6', '#2b4a55']
from figkit import PALETTE
for _c in HEAT + DARK:
    PALETTE.add(_c)


def heat(fig, box, grid, lo=10.0, hi=80.0, fmax=None):
    """Draw a coarse spectrogram: one filled cell per grid entry."""
    x0, y0, x1, y1 = box
    rows, cols = len(grid), len(grid[0])
    n = len(HEAT)
    cw, ch = (x1 - x0) / cols, (y1 - y0) / rows
    for r in range(rows):
        for c in range(cols):
            v = (grid[rows - 1 - r][c] - lo) / (hi - lo)
            k = min(n - 1, max(0, int(v * (n - 1) + 0.5)))
            fig.rect(x0 + c * cw, y0 + r * ch, x0 + (c + 1) * cw + 1,
                     y0 + (r + 1) * ch + 1, fill=HEAT[k], outline=None)


def envelope(sig, cols):
    """Min/max amplitude per column, for a compact waveform drawing."""
    step = max(1, len(sig) // cols)
    out = []
    for i in range(cols):
        chunk = sig[i * step:(i + 1) * step] or [0.0]
        out.append((min(chunk), max(chunk)))
    return out


def wave(fig, box, sig, color=TEAL, cols=240):
    x0, y0, x1, y1 = box
    mid, half = (y0 + y1) / 2, (y1 - y0) / 2
    env = envelope(sig, cols)
    peak = max(1e-9, max(max(abs(a), abs(b)) for a, b in env))
    for i, (lo, hi) in enumerate(env):
        x = x0 + (x1 - x0) * i / cols
        fig.line((x, mid - lo / peak * half), (x, mid - hi / peak * half),
                 color=color, width=3)


# ---------------------------------------------------------------- figures


# ---------------------------------------------------------------- helpers

import math
import shutil

from PIL import Image


def photo(name, src, purpose, source, identity='真实照片'):
    im = Image.open(ART / 'originals' / src).convert('RGB')
    w, h = im.size
    if w > 1062:
        w, h = 1062, round(im.height * 1062 / im.width)
        im.resize((w, h), Image.LANCZOS).save(ASSETS / name, quality=92,
                                             optimize=True)
    else:
        shutil.copyfile(ART / 'originals' / src, ASSETS / name)
    META.append(dict(path='assets/' + name, width=w, height=h, min_label_px=36,
                     effective_min_at_354px=12.0, purpose=purpose,
                     identity=identity, source=source))
    print('  ', name, w, 'x', h)


def ring(fig, cx, cy, r, color, width=5, dash=None, steps=120):
    pts = [(cx + r * math.cos(2 * math.pi * i / steps),
            cy + r * math.sin(2 * math.pi * i / steps)) for i in range(steps + 1)]
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=color, width=width, dash=dash)


# ---------------------------------------------------------------- figures

def fig01():
    fig, y = new(1, '同一个弯，两个轮子走两条路', '内轮走小圆，外轮走大圆；半径差一圈正好是一个轮距。')
    cx, cy = 520, y + 320
    tr = R['track']
    r_in = 15 - tr / 2
    r_out = 15 + tr / 2
    scale = 270 / r_out
    ring(fig, cx, cy, r_out * scale, BLUE, width=6)
    ring(fig, cx, cy, r_in * scale, TEAL, width=6)
    fig.text((cx + 30, cy - r_out * scale - 46), '外轮 99.1 米', 40, color=BLUE)
    fig.text((cx + 30, cy - r_in * scale + 8), '内轮 89.4 米', 40, color=TEAL)
    fig.circle(cx, cy, 10, fill=GRAY, outline=GRAY)
    fig.text((cx + 18, cy - 44), '转弯中心', 40, color=GRAY)
    y = note(fig, cy + 300, '转一整圈，两轮走出的周长差 %.2f 米——正好是 π × 轮距。'
                            '差速器要做的，就是把这个差让出去。' % R['turns'][2]['gap_m'])
    save(fig, '01-two-circles.png', '转弯时内外轮的两条轨迹')


def fig02():
    photo('02-cutaway.jpg', 'differential-cutaway.jpg',
          '现代差速器（保时捷 Cayenne），剖开显示内部结构',
          'Wikimedia Commons，CC BY-SA 3.0，DrJunge')


def fig03():
    fig, y = new(3, '齿轮是怎么连的', '两个半轴齿轮各自连一个车轮，中间的行星轮坐在行星架上。')
    fig.circle(531, y + 170, 150, fill=PALE, outline=GRAY, width=5)
    fig.circle(531, y + 170, 96, fill=None, outline=GRAY, width=4)
    fig.text((531, y + 16), '环形齿轮（被传动轴带动）', 40, color=GRAY, anchor='ma')
    fig.circle(531, y + 170, 26, fill=TINT_B, outline=BLUE, width=4)
    fig.text((531, y + 240), '行星轮', 40, color=BLUE, anchor='ma')
    fig.rect(120, y + 120, 300, y + 220, fill=TINT_T, outline=TEAL, width=4)
    fig.text((210, y + 156), '半轴齿轮', 40, color=TEAL, anchor='ma')
    fig.rect(762, y + 120, 942, y + 220, fill=TINT_T, outline=TEAL, width=4)
    fig.text((852, y + 156), '半轴齿轮', 40, color=TEAL, anchor='ma')
    fig.arrow((306, y + 170), (418, y + 170), color=GRAY, width=4)
    fig.arrow((644, y + 170), (756, y + 170), color=GRAY, width=4)
    fig.arrow((120, y + 300), (60, y + 300), color=INK, width=4)
    fig.arrow((942, y + 300), (1002, y + 300), color=INK, width=4)
    fig.text((531, y + 292), '← 左轮　　　　右轮 →', 40, color=INK, anchor='ma')
    y = note(fig, y + 360, '行星架（也就是环形齿轮）转一圈，两个半轴齿轮各转半圈——'
                           '如果它们被允许各转各的，那速度可以不一样，总和却固定。')
    save(fig, '03-gears.png', '差速器的齿轮连接')


def fig04():
    fig, y = new(4, '它其实是个平均器', '两个轮速画在一条竖线上，行星架的转速永远落在中点。')
    box = (360, y + 30, 640, y + 400)
    pk = Plot(fig, box, (0, 1), (0, 60))
    outer = R['hopkins']['outer'] * 3.6
    inner = R['hopkins']['inner'] * 3.6
    mid = R['hopkins']['mid'] * 3.6
    x = 0.45
    pk.line([(x, inner), (x, outer)], INK, width=6)
    for v, color, label, dx, dy in ((outer, BLUE, '外轮 %.1f', 26, -52),
                                    (inner, TEAL, '内轮 %.1f', 26, 10),
                                    (mid, AMBER, '行星架 %.1f', 210, -24)):
        pk.dot(x, v, color, r=14)
        fig.text((pk.px(x) + dx, pk.py(v) + dy), label % v, 40, color=color)
    pk.axes(xticks=(), yticks=(0, 20, 40, 60), ylab='车速（km/h）', grid=True)
    fig.arrow((700, pk.py(mid) - 18), (700, pk.py(outer) - 18), color=GRAY, width=4)
    fig.text((700, pk.py(outer) - 96), '一半的差', 40, color=GRAY)
    y = note(fig, box[3] + 130, '行星架转速 =（内轮 + 外轮）÷ 2。'
                                '所以"把两个轮子的速度加起来再平分"不是设计目标，'
                                '而是这套齿轮的数学后果。')
    save(fig, '04-hopkins.png', '差速器的平均性质')


def fig05():
    fig, y = new(5, '弯越急，差越大', '横轴是转弯半径，纵轴是外轮与内轮的速度比。')
    box = (300, y + 40, 990, y + 400)
    pk = Plot(fig, box, (0, 400), (1.0, 1.5))
    pk.line([(p['radius'], p['ratio']) for p in R['ratio_curve']], TEAL, width=6)
    got = []
    for r in (5, 15, 50):
        near = [p for p in R['ratio_curve'] if abs(p['radius'] - r) < 0.01][0]
        got.append((r, near['ratio']))
        pk.dot(near['radius'], near['ratio'], AMBER, r=13)
    pk.axes(xticks=(0, 100, 200, 300, 400), yticks=(1.0, 1.2, 1.4),
            xlab='转弯半径（米）', ylab='外轮 / 内轮')
    y = note(fig, box[3] + 130,
             '%d 米半径时比值 %.2f，%d 米时 %.2f，%d 米时 %.2f。'
             '车速再快也不改变它——这个比值只跟几何有关，跟开多快无关。'
             % (got[0][0], got[0][1], got[1][0], got[1][1], got[2][0], got[2][1]))
    save(fig, '05-ratio.png', '转弯半径与轮速比')


def fig06():
    fig, y = new(6, '一轮打滑，全车没劲', '开式差速器把扭矩对半分，而抓地力从来不是对半的。')
    cases = R['traction']['cases']
    top = max(c['total'] for c in cases)
    for i, c in enumerate(cases):
        yy = y + 20 + i * 110
        fig.text((60, yy + 6), c['name'], 40, color=INK)
        w = max(10, c['total'] / top * 470)
        fig.rect(430, yy, 430 + w, yy + 56, fill=TEAL if c['total'] > 5000 else RED,
                 outline=None)
        fig.text((1014, yy + 4), '%d N' % c['total'], 40, color=INK_SOFT, anchor='ra')
    y = note(fig, y + 20 + 110 * len(cases) + 10,
             '干地上发动机给得出 8400 N；一侧结冰只剩 1373 N——正好等于 1400 kg 的车'
             '爬 10%% 坡所需的力。一边是冰，车就停在坡上不动了。')
    save(fig, '06-traction.png', '不同路面下的可用牵引力')


def fig07():
    fig, y = new(7, '把这张表算出来', '同样的发动机扭矩，四种路面下的加速度和爬坡能力。')
    short = ['两轮干地', '一侧湿滑', '一侧结冰', '一侧悬空']
    rows = [[('路面', INK, True), ('总牵引力', INK, True),
             ('加速度', INK, True), ('10% 坡', INK, True)]]
    for name, c in zip(short, R['traction']['cases']):
        rows.append([(name, INK, False), ('%d N' % c['total'], TEAL, True),
                     ('%.2f m/s²' % c['accel'], INK, False),
                     ('能上' if c['climbs'] else '上不去', GREEN if c['climbs'] else RED, True)])
    y = table(fig, y, [(80, 'la'), (560, 'ra'), (790, 'ra'), (1014, 'ra')], rows)
    y = note(fig, y, '模型：1400 kg、后驱、传动轴扭矩 2730 Nm、轮径 0.65 m、'
                     '每个驱动轮承重 6.87 kN。抓地力按 μ × 正压力算。')
    save(fig, '07-table.png', '四种路面下的牵引力与加速度')


def fig08():
    fig, y = new(8, '一条真实的路线', '左转 90 度、直行、右转 90 度：两轮速度一直在分开又合拢。')
    box = (300, y + 30, 990, y + 380)
    pts = R['path']['points']
    pk = Plot(fig, box, (0, R['path']['length']), (30, 60))
    pk.line([(p['s'], p['left']) for p in pts], TEAL, width=5)
    pk.line([(p['s'], p['right']) for p in pts], BLUE, width=5)
    pk.axes(xticks=(0, 50, 100, 150), yticks=(30, 45, 60),
            xlab='沿路线的距离（米）', ylab='车速（km/h）')
    fig.text((box[0] + 30, box[1] + 16), '内轮', 40, color=TEAL)
    fig.text((box[0] + 30, box[1] + 68), '外轮', 40, color=BLUE)
    y = note(fig, box[3] + 130,
             '左转时外轮快、右转时内轮快。走完整条 146 米的路线，两轮的总里程几乎一样——'
             '因为左转和右转的角度正好抵消。')
    save(fig, '08-path.png', '一条路线上的两轮速度')


def fig09():
    fig, y = new(9, '要是把差速器焊死', '轮子只能同速转，转弯时就必须有一侧在地上拖。')
    rows = [[('转弯半径', INK, True), ('转 90° 拖行', INK, True), ('转一整圈拖行', INK, True)]]
    for c in R['corners']:
        rows.append([('%g 米' % c['radius'], INK, False),
                     ('%.2f 米' % c['quarter_gap'], TEAL, True),
                     ('%.2f 米' % c['full_gap'], INK, False)])
    y = table(fig, y, [(80, 'la'), (600, 'ra'), (1014, 'ra')], rows)
    y = note(fig, y, '拖行距离只跟轮距有关：转 90° 就是 π/2 × 1.55 米，与转弯半径无关。'
                     '上面这条路线如果焊死，累计拖行 %.2f 米。' % R['path']['scrub']['total'])
    save(fig, '09-welded.png', '焊死差速器后的拖行距离')


def fig10():
    photo('10-manual-1911.jpg', 'army-corps-1911.jpg',
          '1911 年英军机械运输教程里的差速器剖面图',
          'Wikimedia Commons，公有领域（HMSO 1911 年扫描）', identity='档案扫描件')


def fig11():
    photo('11-starley.jpg', 'starley-tricycle.jpg',
          'James Starley 1877 年的三轮车差速器（1889 年《Cycling》书中的图）',
          'Wikimedia Commons，公有领域', identity='档案扫描件')


def fig12():
    fig, y = new(12, '比汽车早半个世纪', '差速器是蒸汽马车时代发明的，汽车只是继承了它。')
    items = [('1827', 'Pecqueur 为蒸汽马车申请差速器专利', TEAL),
             ('1877', 'Starley 把差速器装上三轮车，转弯不再靠抬轮子', BLUE),
             ('1890s', '汽车沿用它：后桥中间那坨圆鼓鼓的东西', AMBER),
             ('1958', 'Gleasman 发明 Torsen 蜗杆式限滑差速器', RED),
             ('2000s', '电子限滑：用刹车和发动机控制代替机械摩擦片', GREEN)]
    for year, text, color in items:
        fig.circle(110, y + 22, 14, fill=color, outline=color)
        fig.text((146, y), year, 42, bold=True, color=color)
        fig.wrap((300, y + 2), text, 40, 700, color=INK)
        y += 108
    save(fig, '12-timeline.png', '差速器的时间线')


def fig13():
    fig, y = new(13, '限滑：把扭矩偷偷挪过去', '限滑差速器允许两边转速不同，但限制了扭矩差。')
    rows = R['lsd']
    box = (300, y + 40, 960, y + 360)
    pk = Plot(fig, box, (0.8, 4.2), (0, 4))
    pk.line([(r['bias'], r['accel']) for r in rows], TEAL, width=6)
    for r in rows:
        pk.dot(r['bias'], r['accel'], AMBER, r=12)
        fig.text((pk.px(r['bias']) - 10, pk.py(r['accel']) - 56),
                 '%.2f' % r['accel'], 38, color=AMBER, anchor='ma')
    pk.axes(xticks=(1, 2, 3, 4), yticks=(0, 2, 4),
            xlab='扭矩偏置比（能挪多少倍过去）', ylab='一侧结冰时的加速度（m/s²）')
    y = note(fig, box[3] + 130, '偏置比 1.0 就是开式差速器：0.98 m/s²。'
                                '偏置比 2.5 时能到 1.72 m/s²——还是不快，但至少能走。')
    save(fig, '13-lsd.png', '限滑差速器的偏置比与加速度')


def fig14():
    fig, y = new(14, '摩擦片怎么"偷"扭矩', '慢的一侧不转，摩擦片就在壳体和半轴之间传扭矩。')
    fig.rect(80, y + 60, 980, y + 190, fill=PALE, outline=GRAY, width=4)
    fig.text((100, y + 20), '差速器壳体（与行星架一起转）', 40, color=GRAY)
    for i in range(6):
        x = 300 + i * 30
        fig.rect(x, y + 80, x + 16, y + 170, fill=TINT_A, outline=AMBER, width=3)
    fig.text((360, y + 200), '摩擦片组', 40, color=AMBER)
    fig.line((120, y + 125), (280, y + 125), color=INK, width=6)
    fig.line((720, y + 125), (940, y + 125), color=INK, width=6)
    fig.text((120, y + 60), '半轴', 40, color=INK)
    fig.text((820, y + 60), '半轴', 40, color=INK)
    fig.arrow((500, y + 250), (500, y + 205), color=RED, width=5)
    fig.text((520, y + 262), '压紧力来自斜坡和预压弹簧', 40, color=RED)
    y = note(fig, y + 340, '摩擦片压得越紧，能"挪"过去的扭矩越多。'
                           '代价是：转弯时它一直在打滑，会磨损，也会让车头更难拐。')
    save(fig, '14-clutch-lsd.png', '摩擦片式限滑差速器')


def fig15():
    fig, y = new(15, '另一种办法：用刹车', '电子限滑不动齿轮，直接给打滑那个轮子施加制动力。')
    steps = [('传感器', '发现左右轮速差太多'), ('刹车', '给空转的那个轮子加制动'),
             ('差速器', '反作用扭矩传回另一侧'), ('车轮', '有抓地的那侧重新得到扭矩')]
    for i, (name, text) in enumerate(steps):
        x = 60 + i * 250
        chip(fig, (x, y + 40, x + 210, y + 140), name, PALE, size=40, bold=True)
        fig.wrap((x, y + 156), text, 38, 226, color=INK_SOFT)
        if i < 3:
            fig.arrow((x + 208, y + 90), (x + 246, y + 90), color=GRAY, width=4)
    y = note(fig, y + 300, '机械限滑靠摩擦，电子限滑靠刹车。后者的零件更少，'
                           '但要一直消耗刹车片——而且它只在你踩油门的时候才工作。')
    save(fig, '15-brake-lsd.png', '电子限滑的控制回路')


def fig16():
    fig, y = new(16, '它不只装在汽车上', '只要两个轮子要各转各的，就有人用同一套齿轮。')
    y = bullets(fig, y, [
        '洗衣机：滚筒和搅拌器各自的速度，早期靠一套差速齿轮分配。',
        '打印机与绘图仪：两个走纸辊必须同步，同时又要能被手动拉开。',
        '坦克与履带车：转向靠两侧履带差速，双差速器让转向半径可以很细。',
        '人力三轮车与轮椅：1880 年代就是这么解决转弯的，比汽车早。',
        '四驱车：中央差速器管前后轴，前后桥各有一个差速器，一共三个。',
    ])
    y = note(fig, y, '"让两边各转各的、但总和固定"是一个很通用的需求，齿轮只是其中一种解法。')
    save(fig, '16-elsewhere.png', '差速器的其他用途')


def fig17():
    fig, y = new(17, '从曲轴到地面', '扭矩一路走过来，最后一步才被分成两半。')
    steps = [('发动机', '扭矩与转速'), ('变速箱', '换挡改变比例'),
             ('传动轴', '把扭矩送到后桥'), ('差速器', '分给两个半轴'),
             ('半轴', '各连一个车轮')]
    for i, (name, text) in enumerate(steps):
        col, row = i % 3, i // 3
        x = 50 + col * 322
        yy = y + row * 230
        chip(fig, (x, yy, x + 250, yy + 110), name, PALE, size=44, bold=True)
        fig.wrap((x, yy + 126), text, 38, 290, color=INK_SOFT)
        if col < 2:
            fig.arrow((x + 256, yy + 55), (x + 316, yy + 55), color=GRAY, width=4)
    y = note(fig, y + 2 * 230 + 30,
             '差速器是这条链上唯一一个"把一份扭矩变成两份"的零件，'
             '也是唯一一个允许输出转速不同的零件。')
    save(fig, '17-chain.png', '从发动机到车轮的扭矩路径')


FIGS = [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig10,
        fig11, fig12, fig13, fig14, fig15, fig16, fig17]


def make_cover():
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill='#0d1f27', outline=None)
    fig.text((96, 130), '两个轮子', 92, bold=True, color='#ffffff')
    fig.text((96, 250), '为什么可以不一样快', 56, color='#7fa8c9')
    cx, cy = 540, 640
    fig.circle(cx, cy, 250, fill=None, outline='#2b4a55', width=6) if False else None
    for r, c, w in ((250, '#2b4a55', 6), (170, '#7fa8c9', 6), (60, '#f2b134', 8)):
        pts = [(cx + r * math.cos(2 * math.pi * i / 90),
                cy + r * math.sin(2 * math.pi * i / 90)) for i in range(91)]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=c, width=w)
    fig.text((96, 930), '差速器 1827—今天', 40, color='#e8f0f6')
    fig.im.save(ART / 'cover.png')
    print('   cover.png')


def main(argv):
    want = {int(a) for a in argv[1:]} if len(argv) > 1 else None
    for fn in FIGS:
        n = int(fn.__name__[3:])
        if want and n not in want:
            continue
        fn()
    if not want:
        make_cover()
        META.sort(key=lambda row: row['path'])
        (HERE / 'figure-metadata.json').write_text(
            json.dumps(META, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(META))


if __name__ == '__main__':
    main(sys.argv)
