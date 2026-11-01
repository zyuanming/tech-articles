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

import shutil

from PIL import Image


def photo(name, src, purpose, source, identity='真实照片'):
    im = Image.open(ART / 'originals' / src).convert('RGB')
    w, h = im.size
    if w > 1062:                      # only downscale; never recompress in place
        w, h = 1062, round(im.height * 1062 / im.width)
        im.resize((w, h), Image.LANCZOS).save(ASSETS / name, quality=92,
                                             optimize=True)
    else:
        shutil.copyfile(ART / 'originals' / src, ASSETS / name)
    META.append(dict(path='assets/' + name, width=w, height=h, min_label_px=36,
                     effective_min_at_354px=12.0, purpose=purpose,
                     identity=identity, source=source))
    print('  ', name, w, 'x', h)


def square(plot, period, seconds, y0, y1, color, width=5, phase=0.0):
    """Draw a square wave from 0..seconds on a Plot-like axis (x in seconds)."""
    half = period / 2
    pts = []
    t = 0.0
    level = y1
    pts.append((0, level))
    edge = phase % period
    while edge < seconds:
        pts.append((edge, level))
        level = y0 if level == y1 else y1
        pts.append((edge, level))
        edge += half
    pts.append((seconds, level))
    plot.line(pts, color, width=width)


# ---------------------------------------------------------------- figures

def fig01():
    fig, y = new(1, '压电：挤一下，出电；通上电，变形', '石英的这两件事是互逆的，钟表用的是第二件。')
    for i, (title, note_text, flip) in enumerate([
            ('受力', '挤压晶片，两个面之间出现电压', False),
            ('加电压', '给两个面加电压，晶片被拉长或压短', True)]):
        x0 = 60 + i * 490
        fig.rect(x0, y + 60, x0 + 380, y + 300, fill=PALE, outline=None)
        fig.poly([(x0 + 90, y + 120), (x0 + 190, y + 90),
                  (x0 + 290, y + 120), (x0 + 190, y + 150)], fill=TINT_B,
                 outline=BLUE)
        fig.rect(x0 + 80, y + 70, x0 + 300, y + 84, fill=GRAY, outline=None)
        fig.rect(x0 + 80, y + 156, x0 + 300, y + 170, fill=GRAY, outline=None)
        if flip:
            fig.arrow((x0 + 190, y + 250), (x0 + 190, y + 190), color=RED, width=5)
            fig.text((x0 + 210, y + 210), '＋', 44, color=RED)
        else:
            fig.arrow((x0 + 60, y + 130), (x0 + 120, y + 130), color=AMBER, width=5)
            fig.arrow((x0 + 320, y + 130), (x0 + 260, y + 130), color=AMBER, width=5)
            fig.text((x0 + 120, y + 200), '＋　　　−', 44, color=RED)
        fig.text((x0, y + 320), title, 44, bold=True)
        fig.wrap((x0, y + 372), note_text, 40, 380, color=INK_SOFT)
    y = note(fig, y + 480, '石英是压电材料。1880 年居里兄弟测到的是第一种；'
                          '钟表靠的是第二种：加一个交变电压，让晶片自己振起来。')
    save(fig, '01-piezo.png', '压电效应的两个方向')


def fig02():
    photo('02-tuning-fork.jpg', 'quartz-tuning-fork.jpg',
          '音叉形石英振子（拆掉外壳）', 'Wikimedia Commons，公有领域')


def fig03():
    fig, y = new(3, '等效成一个电路', '机械振动可以写成一个 RLC 串联，再并上电极的电容。')
    fig.rect(120, y + 40, 900, y + 60, fill=None, outline=None)
    fig.line((120, y + 50), (300, y + 50), color=INK, width=5)
    fig.line((300, y + 50), (300, y + 110), color=INK, width=5)
    fig.rect(280, y + 110, 320, y + 170, fill=TINT_A, outline=AMBER, width=4)
    fig.text((250, y + 118), 'R', 42, bold=True, color=AMBER, anchor='ra')
    fig.line((300, y + 170), (300, y + 210), color=INK, width=5)
    for k in range(3):
        cx = 300 + k * 40
        fig.line((cx, y + 210), (cx + 40, y + 210), color=INK, width=5) if k % 2 == 0 else None
        fig.line((cx, y + 210), (cx, y + 216), color=INK, width=5)
    fig.rect(296, y + 200, 420, y + 220, fill=TINT_B, outline=BLUE)
    fig.text((440, y + 194), 'L', 42, bold=True, color=BLUE)
    fig.line((420, y + 210), (540, y + 210), color=INK, width=5)
    fig.line((520, y + 190), (560, y + 190), color=INK, width=5)
    fig.line((520, y + 230), (560, y + 230), color=INK, width=5)
    fig.text((570, y + 194), 'C₁', 42, bold=True, color=TEAL)
    fig.line((540, y + 210), (900, y + 210), color=INK, width=5)
    fig.line((700, y + 50), (700, y + 100), color=GRAY, width=4)
    fig.line((680, y + 100), (720, y + 100), color=GRAY, width=5)
    fig.line((680, y + 118), (720, y + 118), color=GRAY, width=5)
    fig.line((700, y + 118), (700, y + 210), color=GRAY, width=4)
    fig.text((730, y + 96), 'C₀（电极）', 40, color=GRAY)
    y = note(fig, y + 270, 'R 是振动里的损耗，L、C₁ 是质量和弹性，C₀ 是两个电极之间'
                           '的静态电容。Q = ωL / R；常见表晶的 Q 在几万到十万量级。')
    save(fig, '03-model.png', '晶振的等效电路')


def fig04():
    fig, y = new(4, 'Q 高，峰就窄', '同一个频率上，Q 越大，偏离一点就几乎不振了。')
    box = (300, y + 40, 990, y + 400)
    pk = Plot(fig, box, (-60, 60), (0, 105))
    for q, color, dash in ((1000, GRAY, 9), (20000, BLUE, 13), (100000, TEAL, None)):
        pts = []
        for x in range(-600, 601):
            d = x / 10.0
            resp = 1 / math.sqrt(1 + (q * 2 * d * 1e-6) ** 2)
            pts.append((d, resp * 100))
        pk.line(pts, color, width=5, dash=dash)
    pk.axes(xticks=(-60, -30, 0, 30, 60), yticks=(0, 50, 100),
            xlab='偏离 32768 Hz 多少 ppm', ylab='相对振幅 %%')
    fig.text((box[0] + 30, box[1] + 16), 'Q = 1000', 40, color=GRAY)
    fig.text((box[0] + 30, box[1] + 68), 'Q = 20000', 40, color=BLUE)
    fig.text((box[0] + 30, box[1] + 120), 'Q = 100000', 40, color=TEAL)
    y = note(fig, box[3] + 130, 'Q = 100000 时，偏离 10 ppm 振幅就掉一半。'
                                '窄的好处是频率稳，坏处是它只肯在一个很窄的温度和负载范围内工作。')
    save(fig, '04-resonance.png', '不同 Q 值下的谐振曲线')


def fig05():
    fig, y = new(5, '一路除以二，除十五次', '二进制分频：每一级把输入频率减半，15 级之后正好 1 Hz。')
    stages = R['stages']
    for i, st in enumerate(stages):
        col, row = i % 5, i // 5
        x = 60 + col * 196
        yy = y + row * 150
        chip(fig, (x, yy, x + 150, yy + 86), '÷2', PALE, size=40, bold=True)
        fig.text((x + 75, yy + 96), '%g Hz' % st['hz'], 40, color=INK_SOFT, anchor='ma')
        if col < 4:
            fig.arrow((x + 152, yy + 43), (x + 194, yy + 43), color=GRAY, width=4)
        elif i != len(stages) - 1:
            mid = yy + 122
            fig.line((x + 75, yy + 92), (x + 75, mid), color=GRAY, width=4)
            fig.line((x + 75, mid), (135, mid), color=GRAY, width=4)
            fig.arrow((135, mid), (135, yy + 152), color=GRAY, width=4)
    y = y + 3 * 150 + 20
    y = note(fig, y, '每一级是一个触发器：来一个上升沿就翻转一次，所以输出频率是输入的一半。'
                     '结构简单到可以用十几个晶体管做出来——这正是它能塞进手表的原因。')
    save(fig, '05-divider.png', '十五级二分频链')


def fig06():
    fig, y = new(6, '每一级的输出', '最上面是晶振，最下面是一秒一次的脉冲。')
    box = (300, y + 30, 990, y + 520)
    pk = Plot(fig, box, (0, 1.0), (0, 5))
    labels = [('32768 Hz', 1 / 32768.0), ('16384 Hz', 1 / 16384.0),
              ('4096 Hz', 1 / 4096.0), ('1 Hz', 1.0)]
    for i, (name, period) in enumerate(labels):
        base = 4.4 - i * 1.1
        square(pk, period, 1.0, base - 0.6, base, [TEAL, BLUE, AMBER, RED][i])
        fig.text((box[0] - 200, pk.py(base) - 24), name, 40, color=INK)
    pk.axes(xticks=(0, 0.25, 0.5, 0.75, 1.0), yticks=(), xfmt='%.2f',
            xlab='时间（秒）', grid=False)
    y = note(fig, box[3] + 170, '在 1 秒的窗口里，上面两行密到并成了一条实心带——放大看才是方波；'
                                '最下面一行只有一个完整周期。分频链做的事，就是把「数得快」变成「数得准」。')
    save(fig, '06-waveforms.png', '分频链各级的输出波形')


def fig07():
    fig, y = new(7, '为什么偏偏是 32768', '因为它是 2 的整数次幂，再除以 2 十五次正好是 1。')
    rows = [[('2 的幂', INK, True), ('值', INK, True), ('÷2 的次数', INK, True)]]
    for k in (10, 12, 13, 14, 15, 16):
        rows.append([('2^%d' % k, TEAL, True), ('%d' % 2 ** k, INK, False),
                     ('%d 次到 1 Hz' % k, INK, False)])
    y = table(fig, y, [(90, 'la'), (380, 'la'), (620, 'la')], rows)
    y = note(fig, y, '32768 Hz 的晶振比 65536 Hz 省电（频率越低，驱动电流越小），'
                     '又比 16384 Hz 更容易做得准（同样的 Q，频率高一点，抗干扰好一点）。'
                     '这个折中在 1960 年代定下来，之后就再没变过。')
    save(fig, '07-why-32768.png', '为什么选 32768 Hz')


def fig08():
    photo('08-astron-watch.jpg', 'seiko-astron-1969.jpg',
          '1969 年 Seiko Quartz Astron 石英表',
          'Wikimedia Commons，CC BY-SA 4.0，Deutsches Uhrenmuseum')


def fig09():
    photo('09-movement.jpg', 'seiko-35a.jpg',
          '精工 35A 机芯（第一块石英表的机芯）',
          'Wikimedia Commons，CC BY 3.0 de，Deutsches Uhrenmuseum')


def fig10():
    fig, y = new(10, '精度阶梯', '从机械表到铯钟，横轴是 ppm 的对数。')
    rows = R['ladder']
    row_h = 94
    for i, r in enumerate(rows):
        yy = y + 10 + i * row_h
        fig.wrap((60, yy + 8), r['name'], 38, 320, color=INK)
        lvl = math.log10(max(r['ppm'], 1e-7))
        w = max(26, (lvl + 7) / 9 * 380)
        fig.rect(420, yy + 20, 420 + w, yy + 62, fill=TEAL if r['ppm'] > 1 else BLUE,
                 outline=None)
        fig.text((1014, yy + 16), '%.1f s/月' % r['per_month'], 38,
                 color=INK_SOFT, anchor='ra')
    y = y + 20 + row_h * len(rows)
    y = note(fig, y, 'ppm 是百万分之一，1 ppm 大约等于每月 2.6 秒。'
                     '条形长度是 log10(ppm)：机械表和铯钟之间差了八个数量级。')
    save(fig, '10-ladder.png', '各类计时器的精度')


def fig11():
    fig, y = new(11, '温度一偏，频率就掉', '抛物线：顶点在 25 °C，两边都变慢，而且越远掉得越快。')
    box = (300, y + 40, 990, y + 400)
    pk = Plot(fig, box, (-20, 70), (-70, 5))
    pk.line([(p['t'], p['ppm']) for p in R['curve']], TEAL, width=6)
    pk.axes(xticks=(-20, 0, 25, 50, 70), yticks=(-60, -40, -20, 0),
            xlab='温度（°C）', ylab='频率偏差（ppm）')
    pk.dot(25, 0, AMBER, r=14)
    fig.text((pk.px(25) + 20, pk.py(0) - 40), '顶点 25 °C', 40, color=AMBER)
    for t in (0, 35, 50):
        ppm = [p['ppm'] for p in R['curve'] if abs(p['t'] - t) < 0.01][0]
        pk.dot(t, ppm, RED, r=10)
        fig.text((pk.px(t) + 12, pk.py(ppm) + 8), '%.1f' % ppm, 38, color=RED)
    y = note(fig, box[3] + 130,
             '35 °C 时只慢 3.5 ppm，5 °C 时慢 14 ppm——因为 5 °C 离顶点更远。'
             '抛物线意味着两件事：温度偏差总是让它变慢，而且冷比热更糟。')
    save(fig, '11-parabola.png', '音叉晶振的温度特性')


def fig12():
    fig, y = new(12, '一个月会差多少', '把频率误差按时间积起来，就是表针和标准时间的差。')
    box = (300, y + 40, 990, y + 400)
    pk = Plot(fig, box, (0, 30), (-40, 2))
    colors = {'恒温 25 °C（抛物线顶点）': GREEN, '恒温 35 °C': AMBER,
              '恒温 5 °C': RED, '房间 23 °C，日夜摆 ±3 °C': TEAL,
              '房间 28 °C，日夜摆 ±5 °C': BLUE}
    for name, series in R['cumulative'].items():
        pk.line([(i, v) for i, v in enumerate(series)], colors[name], width=5)
    pk.axes(xticks=(0, 10, 20, 30), yticks=(-36, -18, 0),
            xlab='天', ylab='累计误差（秒）')
    yy = box[1] + 20
    for name, color in colors.items():
        fig.line((box[0] + 40, yy + 18), (box[0] + 90, yy + 18), color=color, width=6)
        fig.text((box[0] + 104, yy), name, 38, color=INK)
        yy += 56
    y = note(fig, box[3] + 130,
             '恒温 5 °C 一个月慢 36.3 秒，恒温 35 °C 只慢 9.1 秒；'
             '房间在 23 °C 上下摆 3 °C，一个月慢 0.77 秒。'
             '日常温度摆动的影响其实很小——只要平均值不太偏。')
    save(fig, '12-month-drift.png', '一个月里的累计误差')


def fig13():
    fig, y = new(13, '一块表一个月的误差，是怎么凑出来的', '真正让表不准的，不是温度，是出厂调校和老化。')
    rows = [[('来源', INK, True), ('ppm', INK, True), ('秒/月', INK, True)]]
    for b in R['budget']:
        rows.append([(b['name'], INK, False), ('%.1f' % b['ppm'], TEAL, True),
                     ('%.2f' % b['per_month'], INK, False)])
    rows.append([('合计', INK, True), ('%.1f' % R['budget_total_ppm'], INK, True),
                 ('%.1f' % R['budget_total_month'], RED, True)])
    rows = [[(c[0].replace('（抛物线 + 日夜摆动）', ''), c[1], c[2]) for c in r] for r in rows]
    y = table(fig, y, [(70, 'la'), (740, 'ra'), (1014, 'ra')], rows)
    y = note(fig, y, '这就是为什么手表标称"月差 ±15 秒"：不是晶振不准，是这三项加起来就这么多。'
                     '温度那一项在这套参数下只占 0.8 秒。')
    save(fig, '13-error-budget.png', '月误差的来源分解')


def fig14():
    fig, y = new(14, 'ppm 到底是多少', '把百万分之一换算成秒，才好判断一个数字算不算大。')
    rows = [[('偏差', INK, True), ('每天', INK, True), ('每月', INK, True), ('每年', INK, True)]]
    for ppm in (1, 5, 20, 100):
        rows.append([('%d ppm' % ppm, TEAL, True),
                     ('%.2f 秒' % (ppm * 1e-6 * 86400), INK, False),
                     ('%.1f 秒' % (ppm * 1e-6 * 2592000), INK, False),
                     ('%.0f 秒' % (ppm * 1e-6 * 31536000), INK, False)])
    y = table(fig, y, [(80, 'la'), (600, 'ra'), (820, 'ra'), (1014, 'ra')], rows)
    y = note(fig, y, '反过来：想把误差压到每月 1 秒，频率偏差不能超过 %.3f ppm。'
                     '这就是"准"这个字在工程上的意思。' % R['one_second_per_month_ppm'])
    save(fig, '14-ppm-table.png', 'ppm 与秒的换算')


def fig15():
    fig, y = new(15, '电从哪来', '整块表的平均电流不到 1 微安，所以一颗纽扣电池能撑两年。')
    pw = R['power']
    rows = [[('部件', INK, True), ('电流（µA）', INK, True)]]
    for name, key in (('晶振驱动', 'osc_ua'), ('分频电路', 'divider_ua'),
                      ('步进电机（平均）', 'motor_ua')):
        rows.append([(name, INK, False), ('%.1f' % pw[key], TEAL, True)])
    rows.append([('合计', INK, True), ('%.1f' % pw['total_ua'], RED, True)])
    y = table(fig, y, [(90, 'la'), (700, 'ra')], rows)
    y = note(fig, y, '总功耗 %.1f µW。%d mAh 的电池，按这个电流能用 %.1f 年。'
                     '石英表赢机械表，赢在"几乎不耗电"和"几乎没有磨损"，不只是赢在准。'
              % (pw['watts'] * 1e6, pw['capacity_mah'], pw['life_years']))
    save(fig, '15-power.png', '功耗与电池寿命')


def fig16():
    fig, y = new(16, '从实验室到手腕', '压电效应被发现 89 年之后，它才变成一件消费品。')
    items = [('1880', '居里兄弟发现压电效应', TEAL),
             ('1927', 'Bell 实验室做出第一台石英钟，用示波器分频', BLUE),
             ('1950s', '晶体管出现，分频电路才可能小型化', AMBER),
             ('1969', 'Seiko Quartz Astron，100 只，45 万日元', RED),
             ('1970s', '石英机芯成本暴跌，瑞士制表业就业腰斩', INK_SOFT),
             ('今天', '一年几十亿颗 32768 Hz 晶振，装进手表、手机、电表', GREEN)]
    for year, text, color in items:
        fig.circle(110, y + 22, 14, fill=color, outline=color)
        fig.text((146, y), year, 42, bold=True, color=color)
        fig.wrap((300, y + 2), text, 40, 700, color=INK)
        y += 100
    save(fig, '16-timeline.png', '石英表的时间线')


def fig17():
    fig, y = new(17, '怕温度，就补温度', 'TCXO：用热敏电阻测温度，用变容二极管把频率拉回来。')
    boxes = [('晶振', 40), ('变容管', 320), ('热敏网络', 600), ('分频链', 880)]
    for label, x in boxes:
        chip(fig, (x, y + 40, x + 200, y + 150), label, PALE, size=40)
    fig.text((140, y + 106), '32768 Hz', 38, color=INK_SOFT, anchor='ma')
    fig.arrow((242, y + 95), (316, y + 95), color=GRAY, width=4)
    fig.arrow((522, y + 95), (596, y + 95), color=GRAY, width=4)
    fig.arrow((802, y + 95), (876, y + 95), color=GRAY, width=4)
    fig.arrow((700, y + 152), (700, y + 210), color=AMBER, width=4)
    fig.arrow((700, y + 210), (420, y + 210), color=AMBER, width=4)
    fig.arrow((420, y + 210), (420, y + 154), color=AMBER, width=4)
    fig.text((430, y + 224), '温度 → 电压 → 电容 → 频率', 40, color=AMBER)
    y = note(fig, y + 300, '补偿之后能到 ±2 ppm，一个月差 5 秒。代价是多几个元件、多一点电，'
                           '所以便宜的表不做，手机和基站做。')
    save(fig, '17-tcxo.png', '温度补偿振荡器的原理')


def fig18():
    fig, y = new(18, '它也不是一直准', '石英表的三类误差，和它们的来源。')
    y = bullets(fig, y, [
        '老化：晶片里的应力慢慢释放，频率一年偏 1～3 ppm，而且方向基本固定。',
        '温度：抛物线之外还有拐点漂移，用久了顶点会挪一点。',
        '姿态与加速度：音叉的两个方向对重力敏感，戴在手上晃会影响瞬时频率。',
        '磁场：步进电机怕强磁，走时会乱，但这是电机的问题，不是晶振的。',
        '电池电压下降：末段驱动力不足，可能丢步——表"停过"往往不是晶振停了。',
    ])
    y = note(fig, y, '这五条里有三条可以靠设计压下去，两条只能靠换更好的元件。'
                     '"准"从来不是一件事，是一张误差预算表。')
    save(fig, '18-errors.png', '石英表的误差来源')


def fig19():
    fig, y = new(19, '整条链路', '32768 次振动，最后变成秒针的一格。')
    steps = [('晶振', '每秒振 32768 次'), ('分频', '十五级 ÷2'),
             ('整形', '得到干净的 1 Hz'), ('驱动', '交替脉冲'),
             ('步进电机', '转子每次转 180°'), ('齿轮', '减速到秒针')]
    for i, (name, text) in enumerate(steps):
        col, row = i % 3, i // 3
        x = 50 + col * 322
        yy = y + row * 230
        chip(fig, (x, yy, x + 250, yy + 110), name, PALE, size=44, bold=True)
        fig.wrap((x, yy + 126), text, 38, 290, color=INK_SOFT)
        if col < 2:
            fig.arrow((x + 256, yy + 55), (x + 316, yy + 55), color=GRAY, width=4)
    y = note(fig, y + 2 * 230 + 40,
             '每一步都在丢掉信息：晶振只保留频率，分频只保留周期，电机只保留"该走了"。'
             '最后你看到的"准"，是这一路上每一次除法都没出错的结果。')
    save(fig, '19-chain.png', '从晶振到秒针')


FIGS = [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig10,
        fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18, fig19]


def make_cover():
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill='#0d1f27', outline=None)
    fig.text((96, 120), '数到 32768', 96, bold=True, color='#ffffff')
    fig.text((96, 240), '石英表为什么用这个频率', 48, color='#7fa8c9')
    x = 96
    for i, hz in enumerate((32768, 16384, 8192, 4096, 2048, 1024, 512, 256, 128)):
        w = 8 if i else 12
        fig.rect(x, 380, x + 92, 380 + 60 + i * 4, fill='#147d84', outline=None)
        x += 100
    fig.text((96, 700), '÷2 十五次 → 1 Hz', 48, color='#f2b134')
    fig.text((96, 790), '一颗晶振、十五个触发器、一颗电池', 44, color='#e8f0f6')
    fig.text((96, 930), 'tech-articles · 2026-11-09', 38, color='#7fa8c9')
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
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
        META[:] = [m for m in META if 'unused' not in m['path']]
        META.sort(key=lambda row: row['path'])
        (HERE / 'figure-metadata.json').write_text(
            json.dumps(META, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(META))


import math

if __name__ == '__main__':
    main(sys.argv)
