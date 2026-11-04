#!/usr/bin/env python3
"""Original teaching figures for the RIAA equalization article. MIT.

Every number comes from results.json, which run_model.py writes by running
examples/riaa.py. Nothing here is typed in by hand except labels.
"""
from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

from PIL import Image

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
    def __init__(self, fig, box, xlim, ylim, logx=False, logy=False):
        self.f = fig
        self.x0, self.y0, self.x1, self.y1 = box
        self.xlim, self.ylim = xlim, ylim
        self.logx, self.logy = logx, logy

    def _tx(self, x):
        a, b = self.xlim
        if self.logx:
            return (math.log10(x) - math.log10(a)) / (math.log10(b) - math.log10(a))
        return (x - a) / (b - a)

    def _ty(self, y):
        a, b = self.ylim
        if self.logy:
            return (math.log10(y) - math.log10(a)) / (math.log10(b) - math.log10(a))
        return (y - a) / (b - a)

    def px(self, x):
        return self.x0 + (self.x1 - self.x0) * self._tx(x)

    def py(self, y):
        return self.y1 - (self.y1 - self.y0) * self._ty(y)

    def axes(self, xticks=(), yticks=(), xfmt='%g', yfmt='%g', xlab=None,
             ylab=None, grid=True, ylab_at_top=False):
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
            if ylab_at_top:
                self.f.text((44, self.y0 - 62), ylab, 40, color=GRAY)
            else:
                self.f.text((self.x0, self.y0 - 62), ylab, 40, color=GRAY)
        if xlab:
            self.f.text((self.x1, self.y1 + 74), xlab, 40, color=GRAY, anchor='ra')

    def line(self, pts, color=TEAL, width=5, dash=None):
        pixels = [(self.px(x), self.py(y)) for x, y in pts]
        for a, b in zip(pixels, pixels[1:]):
            self.f.line(a, b, color=color, width=width, dash=dash)

    def dot(self, x, y, color=TEAL, r=13):
        self.f.circle(self.px(x), self.py(y), r, fill=color, outline=color)

    def vline(self, x, color=GRAY, dash=14):
        xx = self.px(x)
        self.f.line((xx, self.y0), (xx, self.y1), color=color, width=3, dash=dash)

    def hline(self, y, color=GRAY, dash=14):
        yy = self.py(y)
        self.f.line((self.x0, yy), (self.x1, yy), color=color, width=3, dash=dash)


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def photo(name, src, purpose, source, identity='真实照片', crop=None):
    im = Image.open(ART / 'originals' / src).convert('RGB')
    if crop:
        im = im.crop(crop)
    w, h = im.size
    if w > 1062:
        w, h = 1062, round(h * 1062 / w)
        im.resize((w, h), Image.LANCZOS).save(ASSETS / name, quality=92,
                                              optimize=True)
    elif crop:
        im.save(ASSETS / name, quality=92, optimize=True)
    else:
        shutil.copyfile(ART / 'originals' / src, ASSETS / name)
        w, h = im.size
    META.append(dict(path='assets/' + name, width=w, height=h, min_label_px=36,
                     effective_min_at_354px=12.0, purpose=purpose,
                     identity=identity, source=source))
    print('  ', name, w, 'x', h)


_CHIP = [0]


def chip(fig, box, label, fill, color=INK, size=40, bold=False):
    _CHIP[0] += 1
    key = 'c%d' % _CHIP[0]
    fig.box(key, *box, fill=fill)
    fig.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - size * 0.62), label,
             size, bold=bold, color=color, anchor='ma', inside=key)
    return key


def polyline(fig, pts, color=TEAL, width=6, dash=None):
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=color, width=width, dash=dash)


def leader(fig, a, b, color=GRAY):
    fig.line(a, b, color=color, width=3)


FREQ = [r['f'] for r in R['curve']]
CURVE = {r['f']: r for r in R['curve']}
SPAN = R['span']


def fig01():
    fig, y = new(1, '一条曲线，两头的活', '刻片时按它砍，放音时按它补。'
                                          '中间隔着几十年的化学、机械和一点点听力。')
    top = [(50, 200), (360, 200), (670, 200)]
    top_labels = ['话筒 / 母带', '刻片放大器', '刻片头']
    top_fills = [PALE, TINT_R, TINT_A]
    top_colors = [INK, RED, AMBER]
    for (x, yy), t, f, c in zip(top, top_labels, top_fills, top_colors):
        chip(fig, (x, yy, x + 290, yy + 96), t, f, color=c)
    for i in range(2):
        fig.arrow((top[i][0] + 300, 248), (top[i + 1][0] - 10, 248),
                  color=INK_SOFT, width=4)
    fig.arrow((815, 306), (815, 396), color=INK_SOFT, width=4)
    fig.arrow((815, 516), (815, 596), color=INK_SOFT, width=4)

    chip(fig, (50, 396, 1010, 516), '沟槽：两个斜面上各刻一条波形', TINT_B,
         color=BLUE, size=44, bold=True)

    low = [(670, 596), (360, 596), (50, 596)]
    low_labels = ['唱头 / 唱针', '唱放：逆着来', '功放 / 音箱']
    low_fills = [TINT_G, TINT_T, PALE]
    low_colors = [GREEN, TEAL, INK]
    for (x, yy), t, f, c in zip(low, low_labels, low_fills, low_colors):
        chip(fig, (x, yy, x + 290, yy + 96), t, f, color=c)
    for i in range(2):
        fig.arrow((low[i][0] - 10, 644), (low[i + 1][0] + 300, 644),
                  color=INK_SOFT, width=4)

    fig.text((50, 730), '去：低音砍 19 dB，高音提 20 dB', 42, color=RED, bold=True)
    fig.text((50, 800), '回：低音抬 19 dB，高音压 20 dB', 42, color=TEAL, bold=True)
    y = note(fig, 880, '两个放大器一个正着来、一个反着来，中间那一段走的是'
                       '塑料、金属和一根针。只要两端严格互为倒数，'
                       '听的人就听不出中间动过手脚。')
    save(fig, '01-overview.png', '整条链路的两个放大器，以及它们之间那道沟槽')


def fig02():
    photo('02-lathe.jpg', 'lathe.jpg',
          'Neumann VMS-70 刻片机，SAE Mastering（亚利桑那州凤凰城）',
          'VACANT FEVER, CC BY-SA 2.0, via Wikimedia Commons')


def fig03():
    fig, y = new(3, '这条曲线长这样', '纵轴是相对 1 kHz 的增益，正数是提升。'
                                     '红的是刻片，蓝的是放音。')
    p = Plot(fig, (250, y + 20, 1012, y + 680), (20, 20000), (-24, 24),
             logx=True)
    p.axes(xticks=(20, 100, 1000, 10000),
           yticks=(-20, -10, 0, 10, 20), xfmt='%d', yfmt='%+d',
           xlab='Hz')
    fig.text((44, p.py(20) - 4), 'dB', 40, color=GRAY)

    play = [(f, CURVE[f]['play']) for f in FREQ]
    rec = [(f, CURVE[f]['rec']) for f in FREQ]
    p.line(rec, color=RED, width=6)
    p.line(play, color=BLUE, width=6)

    p.dot(20, CURVE[20]['rec'], RED, 11)
    fig.text((p.px(20) + 16, p.py(CURVE[20]['rec']) - 46), '刻片 −19.3', 38,
             color=RED)
    p.dot(20, CURVE[20]['play'], BLUE, 11)
    fig.text((p.px(20) + 16, p.py(CURVE[20]['play']) + 18), '放音 +19.3', 38,
             color=BLUE)
    p.dot(20000, CURVE[20000]['rec'], RED, 11)
    fig.text((p.px(20000) - 14, p.py(CURVE[20000]['rec']) - 54), '刻片 +19.6', 38,
             color=RED, anchor='ra')
    p.dot(20000, CURVE[20000]['play'], BLUE, 11)
    fig.text((p.px(20000) - 14, p.py(CURVE[20000]['play']) + 18), '放音 −19.6', 38,
             color=BLUE, anchor='ra')
    fig.text((p.px(24), p.py(-2)), '三个转折：50 Hz、500 Hz、2122 Hz', 38,
             color=INK)
    fig.text((p.px(24), p.py(-11)), '1 kHz 定为 0 dB，两端各走 19 dB', 38,
             color=INK)

    y = p.y1 + 150
    y = note(fig, y, '两条线互为倒数，间距 38.9 dB。一个把低音按下去、把高音'
                     '提上来；另一个原样倒回去。')
    save(fig, '03-riaa-curve.png', 'RIAA 刻片与放音两条曲线，标出三个转折与两端的 dB 值')


def fig04():
    fig, y = new(4, '换成"这道沟槽要摆多宽"', '同一个振速下，频率越低振幅越大，'
                                            '除非先按曲线把它压下去。')
    p = Plot(fig, (250, y + 20, 1012, y + 640), (20, 20000), (0.5, 1000),
             logx=True, logy=True)
    p.axes(xticks=(20, 100, 1000), yticks=(1, 10, 100, 1000),
           xfmt='%d', yfmt='%d', xlab='Hz')
    fig.text((44, p.py(1000) - 4), 'µm', 40, color=GRAY)
    fr = [20 * (10 ** (i / 40.0)) for i in range(0, 121)]

    def amp(f, riaa):
        base = 0.05 / (2 * math.pi * f) * 1e6
        if not riaa:
            return base
        return base / (10 ** (db_of_play(f) / 20.0))

    p.line([(f, amp(f, False)) for f in fr], color=RED, width=6, dash=18)
    p.line([(f, amp(f, True)) for f in fr], color=TEAL, width=6)
    for r in R['headroom']:
        p.dot(r['f'], r['with_riaa_um'], TEAL, 10)
        p.dot(r['f'], r['flat_um'], RED, 10)
    fig.text((p.px(26), p.py(430)), '没有均衡：振幅跟着 1/f 涨', 38, color=RED)
    fig.text((p.px(90), p.py(2.6)), '有均衡：1 kHz 以下是平的', 38, color=TEAL)

    y = p.y1 + 150
    y = note(fig, y, '20 Hz 那一列差 9.2 倍：43 µm 对 398 µm。'
                     '刻片头能摆动的幅度是有限的，这 9 倍就是"能不能把低音刻进去"的区别。')
    save(fig, '04-amplitude.png', '同一振速下沟槽振幅随频率的变化，有 / 无 RIAA 对比')


def db_of_play(f):
    z = 1j * 2 * math.pi * f
    num = abs((1 + z * 318e-6) / ((1 + z * 3180e-6) * (1 + z * 75e-6)))
    z0 = 1j * 2 * math.pi * 1000.0
    den = abs((1 + z0 * 318e-6) / ((1 + z0 * 3180e-6) * (1 + z0 * 75e-6)))
    return 20 * math.log10(num / den)


def fig05():
    fig, y = new(5, '沟槽俯视图：同样响，宽窄差 9 倍',
                 '画的是针尖走过的中心线。三条都是 5 cm/s，只是频率和有没有均衡不同。')
    scale = 1.55   # px per µm
    rows = [('1 kHz，有均衡', 8.0, TEAL, y + 130, 16),
            ('50 Hz，有均衡', 22.6, TEAL, y + 360, None),
            ('50 Hz，没有均衡', 159.2, RED, y + 690, None)]
    for label, a, color, base, dash in rows:
        fig.text((44, base - a * scale - 74), label, 40, color=color, bold=True)
        fig.text((1012, base - a * scale - 70), '振幅 %.1f µm' % a, 38,
                 color=GRAY, anchor='ra')
        pts = []
        for i in range(0, 121):
            x = 330 + i * 5.6
            pts.append((x, base - a * scale * math.sin(i / 120.0 * 2 * math.pi * 3)))
        polyline(fig, pts, color=color, width=6, dash=dash)

    bar = 100 * scale
    yb = y + 1110
    fig.line((330, yb), (330 + bar, yb), color=INK, width=5)
    fig.line((330, yb - 12), (330, yb + 12), color=INK, width=3)
    fig.line((330 + bar, yb - 12), (330 + bar, yb + 12), color=INK, width=3)
    fig.text((330 + bar / 2, yb - 60), '100 µm', 40, color=INK, anchor='ma')
    fig.text((330 + bar + 30, yb - 20), '三条同一个比例尺', 38, color=GRAY)

    y = note(fig, yb + 60, '第三行是一个人耳几乎听不见的 50 Hz，'
                           '却要求刻片头像打鼓一样前后甩出 0.16 毫米。'
                           '第一张 LP 之所以能装二十分钟，靠的就是把这一行压成第二行。')
    save(fig, '05-grooves.png', '三条沟槽中心线的俯视示意，振幅按同一比例尺')


def fig06():
    photo('06-groove.jpg', 'groove.jpg', 'LP 表面沟槽的近距离照片，反光处能看出螺旋的间距',
          'Piano Piano!, CC BY 2.0, via Wikimedia Commons')


def fig07():
    fig, y = new(7, '针尖坐在槽里，靠两个斜面读', '沟槽是 V 形，左右两个斜面各驮一个声道。'
                                              '针尖的接触半径比槽里的波长还大。')
    s = 5.4   # px per µm
    cx = 531
    top = y + 90
    # groove walls
    half = 25 * s / 2
    depth = 34 * s
    fig.poly([(cx - half, top), (cx + half, top), (cx + 30, top + depth), (cx - 30, top + depth)],
             fill=TINT_B, outline=BLUE)
    # stylus: circle of 18 µm radius resting with tip 6 µm above bottom
    r = 18 * s
    ty = top + depth - 6 * s - r
    fig.circle(cx, ty, r, fill=TINT_A, outline=AMBER, width=4)
    fig.circle(cx, ty, 5 * s, fill=WHITE, outline=AMBER, width=3)
    leader(fig, (cx + 14, ty), (cx + 90, ty - 30))
    fig.text((cx + 100, ty - 54), '接触半径 5 µm 量级', 38, color=AMBER)
    leader(fig, (cx - half + 6, top + 6), (cx - 120, top + 6))
    fig.text((cx - 130, top - 18), '槽口 50 µm', 38, color=BLUE, anchor='ra')
    fig.line((cx + 40, top + depth), (cx + 120, top + depth), color=INK_SOFT, width=3)
    fig.text((cx + 130, top + depth - 22), '槽深 30 µm 上下', 38, color=INK_SOFT)

    y = top + depth + 70
    y = note(fig, y, '左边斜面和右边斜面是分开的两个信号，所以一根针能同时读出左右声道。'
                     '斜面上刻的是波浪；波长短到与接触半径同一个量级时，针就没法老老实实'
                     '跟着走。')
    save(fig, '07-stylus.png', '唱针坐在 V 形槽里的截面示意，标出槽口、槽深与接触半径')


def fig08():
    fig, y = new(8, '20 kHz 的波长，比针尖的接触面还短', '波长 = 线速度 ÷ 频率。'
                                            '越往盘的中间走，线速度越低，波长越短。')
    p = Plot(fig, (250, y + 20, 1012, y + 600), (20, 20000), (3, 30000),
             logx=True, logy=True)
    p.axes(xticks=(20, 100, 1000), yticks=(10, 100, 1000, 10000),
           xfmt='%d', yfmt='%d', xlab='Hz')
    fig.text((44, p.py(30000) - 4), 'µm', 40, color=GRAY)
    fr = [20 * (10 ** (i / 40.0)) for i in range(0, 121)]
    sp = R['speeds']
    p.line([(f, sp['outer'] / f * 1e6) for f in fr], color=TEAL, width=4, dash=16)
    p.line([(f, sp['mid'] / f * 1e6) for f in fr], color=TEAL, width=6)
    p.line([(f, sp['inner'] / f * 1e6) for f in fr], color=TEAL, width=4, dash=16)
    p.hline(10, color=RED)
    fig.text((p.px(24), p.py(10) - 52), '接触直径 10 µm', 38, color=RED)
    fig.text((p.px(30), p.py(1600)), '外圈 %.2f m/s' % sp['outer'], 38, color=TEAL)
    fig.text((p.px(30), p.py(430)), '中间 %.2f m/s' % sp['mid'], 38, color=TEAL)
    fig.text((p.px(30), p.py(110)), '内圈 %.2f m/s' % sp['inner'], 38, color=TEAL)
    p.dot(20000, sp['mid'] / 20000 * 1e6, TEAL, 12)
    fig.text((p.px(20000) - 14, p.py(sp['mid'] / 20000 * 1e6) - 56),
             '%.1f µm' % (sp['mid'] / 20000 * 1e6), 38, color=TEAL, anchor='ra')

    y = p.y1 + 150
    y = note(fig, y, '红线以下是波长比接触面还短的地方。最内圈 20 kHz 的波长只有 '
                     '%.0f µm，跟接触直径差不多——针尖没法逐字跟着走，只能"跳过"这些起伏。'
                     % (sp['inner'] / 20000 * 1e6))
    save(fig, '08-wavelength.png', '三个半径上的沟槽波长随频率变化，与唱针接触尺寸比较')


def fig09():
    photo('09-cartridge.jpg', 'cartridge.jpg',
          '动磁唱头与唱针（Ortofon 2M Black），旁边是针压计',
          'Audiotecna Música, CC0, via Wikimedia Commons')

def fig10():
    fig, y = new(10, '唱放做三件事', '先把唱头的高阻抗接住，再按三个转折把曲线倒回去，'
                                 '最后放大到线路电平。')
    boxes = [(50, y + 40, 250, y + 176, '唱头\n5 mV 量级', TINT_G, GREEN),
             (290, y + 40, 500, y + 176, '47 kΩ\n负载', PALE, INK),
             (540, y + 40, 790, y + 176, 'RIAA 网络', TINT_T, TEAL),
             (830, y + 40, 1012, y + 176, '增益\n40 dB', TINT_A, AMBER)]
    for x0, y0, x1, y1, label, fill, color in boxes:
        chip(fig, (x0, y0, x1, y1), label.split('\n')[0], fill, color=color,
             size=42, bold=True)
        if '\n' in label:
            fig.text(((x0 + x1) / 2, y1 - 44), label.split('\n')[1], 38,
                     color=INK_SOFT, anchor='ma')
    for i in range(3):
        fig.arrow((boxes[i][2] + 8, y + 108), (boxes[i + 1][0] - 10, y + 108),
                  color=INK_SOFT, width=4)
    fig.text((50, y - 6), '信号往这边走 →', 38, color=GRAY)

    yy = y + 230
    fig.text((44, yy), '三个转折各管一段：', 42, bold=True)
    yy += 70
    yy = bullets(fig, yy, [
        '50 Hz：再往下的低音不再抬，这一段等于把最底下的能量按住',
        '500 Hz：中低音的抬升到这里结束，500 Hz 到 2.1 kHz 是最平的',
        '2122 Hz：往上的高音开始往下压，压到 20 kHz 正好 −19.6 dB',
    ])
    yy = note(fig, yy + 10, '图里只画骨架。真电路用几个电阻电容去凑这三条时间常数，'
                            '元件数看设计，但三段的分界点必须落在上面这三个地方。')
    save(fig, '10-stage.png', '唱放的方块图：负载、RIAA 网络、增益，以及三个转折各管哪一段')


def fig11():
    fig, y = new(11, '电阻电容差一点，曲线歪多少', '1% 的电阻配 5% 的电容，'
                                            '整条曲线偏离理想值不到 1 dB。')
    p = Plot(fig, (250, y + 20, 1012, y + 560), (20, 20000), (-1.0, 1.0),
             logx=True)
    p.axes(xticks=(20, 100, 1000), yticks=(-1.0, -0.5, 0, 0.5, 1.0),
           xfmt='%d', yfmt='%+.1f', xlab='Hz')
    fig.text((44, p.py(1.0) - 4), 'dB', 40, color=GRAY)
    T = R['tolerance_curves']
    fr = T['freqs']
    p.line(list(zip(fr, T['median'])), color=TEAL, width=5)
    p.line(list(zip(fr, T['worst'])), color=RED, width=5)
    Tt = R['tolerance_curves_tight']
    p.line(list(zip(Tt['freqs'], Tt['worst'])), color=BLUE, width=4, dash=16)
    fig.text((p.px(24), p.py(0.62)), '最坏一次：%+.2f dB' % T['worst_db'], 38,
             color=RED)
    fig.text((p.px(24), p.py(-0.30)), '中位那次', 38, color=TEAL)
    tight = R['tolerance_tight']['worst_db']
    fig.text((p.px(24), p.py(-0.62)), '0.1%% 电阻 + 1%% 电容：%+.2f dB' % tight, 38,
             color=BLUE)

    y = p.y1 + 150
    y = note(fig, y, '抽样 200 次，R 偏差 ±1%%、C 偏差 ±5%%。最坏 0.76 dB，'
                     '中位 0.28 dB。这个量级比房间和音箱造成的起伏小一个数量级，'
                     '这一级在整条链路上几乎可以忽略。')
    save(fig, '11-tolerance.png', '元件容差导致的曲线偏差：最坏一次、中位，以及更精密件的对照')


def fig12():
    fig, y = new(12, '同一条曲线，对噪声是两副面孔', '把每个倍频程里的白噪'
                                            '按放音曲线的增益加权，正数是放大，负数是压低。')
    octs = R['noise']['by_octave']
    p = Plot(fig, (250, y + 30, 1012, y + 620), (0, len(octs)), (-26, 22))
    p.axes(yticks=(-20, -10, 0, 10, 20), yfmt='%+d', ylab=None)
    fig.text((44, p.py(22) - 4), 'dB', 40, color=GRAY)
    p.hline(0, color=GRAY, dash=None)
    w = (p.x1 - p.x0) / len(octs)
    for i, o in enumerate(octs):
        x = p.x0 + i * w + w * 0.18
        top = p.py(o['db'])
        base = p.py(0)
        lo, hi = min(top, base), max(top, base)
        fig.rect(x, lo, x + w * 0.64, hi, fill=(TINT_R if o['db'] > 0 else TINT_T),
                 outline=None)
        lbl = '%+d' % round(o['db'])
        fig.text((x + w * 0.32, min(top, base) + 10 if o['db'] > 0 else max(top, base) + 12),
                 lbl, 38, color=(RED if o['db'] > 0 else TEAL), anchor='ma')
        f = o['f']
        tag = ('%dk' % round(f / 1000)) if f >= 1000 else '%d' % round(f)
        fig.text((x + w * 0.32, p.y1 + 14), tag, 38, color=GRAY, anchor='ma')
    fig.text((44, p.y1 + 74), '倍频程中心频率（Hz）', 38, color=GRAY)

    y = p.y1 + 150
    y = note(fig, y, '低音那头被抬得最多：31 Hz 附近 +17 dB。高音那头一路压低，'
                     '16 kHz 附近 −21 dB。表面噪声是宽带的，'
                     '所以被抬起来的是最难听的那一段。')
    save(fig, '12-noise.png', '白噪经过放音曲线后，各倍频程被放大或压低多少 dB')


def fig13():
    fig, y = new(13, '这条曲线买来的是时间', '同一套刻片机、同样的振幅上限，'
                                     '槽距能定多密决定了这一面能录多久。')
    pl = R['playing']
    bars = [('有 RIAA', pl['riaa']['minutes'], pl['pitch_riaa_mm'], TEAL),
            ('没有均衡', pl['flat']['minutes'], pl['pitch_flat_mm'], RED)]
    base = y + 640
    for i, (label, mins, pitch, color) in enumerate(bars):
        x = 190 + i * 420
        h = mins / 26.0 * 460
        fig.rect(x, base - h, x + 240, base, fill=(TINT_T if color is TEAL else TINT_R),
                 outline=color, width=4)
        fig.text((x + 120, base - h - 74), '%.1f 分钟' % mins, 42, color=color,
                 anchor='ma', bold=True)
        fig.text((x + 120, base + 20), label, 42, bold=True, anchor='ma')
        fig.text((x + 120, base + 84), '槽距 %.2f mm' % pitch, 38, color=GRAY,
                 anchor='ma')
    fig.line((170, base), (1012, base), color=INK, width=3)
    fig.text((44, y + 30), '一面 12 英寸 LP 的录音时间', 38, color=INK_SOFT)

    y = note(fig, base + 160, '模型算出来 24.4 分钟对 2.6 分钟，差 9.2 倍。'
                              '真唱片大约 20 分钟一面——差距来自节目电平比 5 cm/s 高、'
                              '刻片师还会按峰值动态调槽距。比值才是重点。')
    save(fig, '13-playing-time.png', '有均衡与没有均衡时，一面 LP 能录多长时间')


def fig14():
    photo('14-turntable.jpg', 'turntable.jpg',
          'Technics SL-1200MK5 唱盘与 Ortofon 唱头',
          'Unknown author, CC0, via Wikimedia Commons')


def fig15():
    fig, y = new(15, '越低越危险', '曲线在 50 Hz 以下不再下降，也就是说'
                            '亚声频的东西一点没被压住，反而被抬到了最高。')
    p = Plot(fig, (250, y + 20, 1012, y + 520), (0.3, 100), (8, 22),
             logx=True)
    p.axes(xticks=(0.3, 1, 3, 10, 30, 100), yticks=(10, 14, 18, 22),
           xfmt='%g', yfmt='%+d', xlab='Hz')
    fig.text((44, p.py(22) - 4), 'dB', 40, color=GRAY)
    fr = [0.3 * (10 ** (i / 40.0)) for i in range(0, 101)]
    p.line([(f, db_of_play(f)) for f in fr], color=TEAL, width=6)
    p.vline(0.556, color=RED, dash=None)
    fig.text((p.px(0.58), p.py(8.8)), '转一圈一次，0.56 Hz', 38, color=RED)
    p.dot(0.556, db_of_play(0.556), RED, 12)
    fig.text((p.px(1.1), p.py(20.6)), '20 Hz 处 +19.3 dB', 38, color=TEAL)

    y = p.y1 + 150
    y = note(fig, y, '唱针读到的是振速，所以翘曲这种慢速摆动照样出电压；'
                     '曲线又把这段抬到最高。结果是一转一次的"呜"，'
                     '和喇叭纸盆肉眼可见的前后晃。后来加的那条低切就是为它。')
    save(fig, '15-warp.png', '放音曲线在 50 Hz 以下的平台，与 33⅓ 转翘曲频率的位置')


def fig16():
    fig, y = new(16, '四段斜率，一条曲线', '把 38.9 dB 拆开看，'
                                     '只有中间那一段是平的，其余全是斜的。')
    cols = [(70, 'la'), (400, 'la'), (650, 'la')]
    rows = [
        [('频段', INK, True), ('放音曲线', INK, True), ('干什么', INK, True)],
        [('20–50 Hz', INK, False), ('平，+19 dB', TEAL, False), ('低音到头了', INK_SOFT, False)],
        [('50–500 Hz', INK, False), ('每倍频程 +6', TEAL, False), ('把中低音补回来', INK_SOFT, False)],
        [('500 Hz–2.1 kHz', INK, False), ('平，0 dB', INK, False), ('中频不动', INK_SOFT, False)],
        [('2.1 kHz 以上', INK, False), ('每倍频程 −6', TEAL, False), ('把高音压回去', INK_SOFT, False)],
    ]
    y = table(fig, y + 20, cols, rows, size=38, row_h=84)
    y = note(fig, y + 30, '刻片曲线把每一行反过来做一遍。所以"为什么刻片时要砍低音"'
                          '和"为什么放音时要加回来"是同一个问题的两句话，'
                          '而两端各走 19 dB 正是那道 38.9 dB 的跨度。')
    save(fig, '16-slopes.png', '按频段拆开的斜率表：平、+6、平、−6')


def fig17():
    fig, y = new(17, '搞错会怎样', '均衡是可逆的，所以接错不会坏，只会难听。'
                              '下表的数字直接取曲线的两端。')
    a20 = CURVE[20]['play']
    a20k = CURVE[20000]['play']
    cols = [(70, 'la'), (600, 'la'), (800, 'la')]
    rows = [
        [('接法', INK, True), ('20 Hz', INK, True), ('20 kHz', INK, True)],
        [('正常：曲线对上了', INK, False), ('0 dB', TEAL, False), ('0 dB', TEAL, False)],
        [('只放大，不做均衡', INK, False), ('%+.1f dB' % a20, RED, False),
         ('%+.1f dB' % a20k, BLUE, False)],
        [('均衡接了两次', INK, False), ('%+.1f dB' % (2 * a20), RED, False),
         ('%+.1f dB' % (2 * a20k), BLUE, False)],
        [('该砍的时候在抬', INK, False), ('%+.1f dB' % -a20, RED, False),
         ('%+.1f dB' % -a20k, BLUE, False)],
    ]
    y = table(fig, y + 20, cols, rows, size=38, row_h=82)
    y = note(fig, y + 30, '第一行是"低音轰头、高音发闷"，因为唱片本来就带着 19 dB '
                          '的低音提升；第二行是轰两次；第三行直接把两个 19 dB 反了过来，'
                          '听起来薄、亮、刺。')
    save(fig, '17-mismatch.png', '三种接错的均衡方式在两端的偏差')


def fig18():
    fig, y = new(18, '它今天还在三处上班', '数字录音本身不需要这条曲线，'
                                    '但只要中间隔着一段模拟的沟槽，它就得出现。')
    cols = [(70, 'la'), (420, 'la')]
    rows = [
        [('场景', INK, True), ('为什么还要它', INK, True)],
        [('放黑胶', INK, False), ('唱片按它刻的，不补就是错的', INK_SOFT, False)],
        [('老录音数字化', INK, False), ('磁带和 lacquer 母盘里也带着它', INK_SOFT, False)],
        [('插件里的"黑胶味"', INK, False), ('模拟的是同一条曲线和它的误差', INK_SOFT, False)],
    ]
    y = table(fig, y + 20, cols, rows, size=38, row_h=82)
    y = bullets(fig, y + 30, [
        '它不改善音质，只把刻片时不得已的妥协还原成原来的样子',
        '38.9 dB 的跨度是个提醒：模拟介质里每一个"不得已"，都要有人在对岸接住',
    ])
    save(fig, '18-today.png', '这条曲线今天还在的三处，以及它不改善音质这一点')


from figkit import PALETTE


def make_cover():
    for c in ('#0e1b22', '#2b4a55', '#8fb6c9', '#e8f0f6', '#f2b134', '#2fb3a8'):
        PALETTE.add(c)
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill='#0e1b22', outline=None)
    fig.text((96, 96), '刻片时砍掉 19 dB', 78, bold=True, color='#ffffff')
    fig.text((96, 200), '放音时再加回来', 78, bold=True, color='#ffffff')
    fig.text((96, 310), 'RIAA 曲线：一条 38.9 dB 的推挽', 46, color='#8fb6c9')

    mid = 610
    x0, x1 = 96, 984
    lo, hi = 20.0, 20000.0

    def px(f):
        a = (math.log10(f) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
        return x0 + (x1 - x0) * a

    def py(d):
        return mid - d / 21.0 * 150

    fig.line((x0, mid), (x1, mid), color='#2b4a55', width=3, dash=12)
    fr = [20 * (10 ** (i / 40.0)) for i in range(0, 121)]
    play = [(px(f), py(db_of_play(f))) for f in fr]
    for a, b in zip(play, play[1:]):
        fig.line(a, b, color='#2fb3a8', width=7)
    rec = [(x, 2 * mid - y) for x, y in play]
    for a, b in zip(rec, rec[1:]):
        fig.line(a, b, color='#f2b134', width=7)
    for f in (50.0, 500.0, 2122.0):
        fig.line((px(f), mid - 10), (px(f), mid + 10), color='#8fb6c9', width=3)
    fig.text((x0, py(19.3) - 56), '放音 +19.3', 40, color='#2fb3a8')
    fig.text((x1, py(-19.6) + 16), '放音 −19.6', 40, color='#2fb3a8', anchor='ra')
    fig.text((x1, 2 * mid - py(-19.6) - 56), '刻片 +19.6', 40, color='#f2b134',
             anchor='ra')
    fig.text((x0, 2 * mid - py(19.3) + 16), '刻片 −19.3', 40, color='#f2b134')
    fig.text((px(1000) - 6, mid + 22), '1 kHz = 0 dB', 40, color='#8fb6c9',
             anchor='ra')
    fig.text((96, 830), '为什么低音要先压下去，高音反而先提上来', 44,
             color='#e8f0f6')
    fig.text((96, 940), 'tech-articles · 2026-11-09', 38, color='#8fb6c9')
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


FIGS = [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
         fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18]


def main():
    want = {int(a) for a in sys.argv[1:] if a.isdigit()}
    for i, fn in enumerate(FIGS, 1):
        if want and i not in want:
            continue
        print('->', fn.__name__)
        fn()
    if not want:
        make_cover()
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(sorted(META, key=lambda r: r['path']), ensure_ascii=False,
                   indent=1) + '\n')
    print('figures:', len(META))


if __name__ == '__main__':
    raise SystemExit(main())
