#!/usr/bin/env python3
"""Original teaching figures for the delta-sigma article. MIT.

Headline numbers come from results.json (run_model.py writes it); dense curves
are sampled from the same model module, so text and figures cannot drift apart.
"""
from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageFont

from figkit import (Fig, PALETTE, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED,
                    GRAY, LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R,
                    TINT_G)

import dsigma as M

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []

MONO_PATH = '/System/Library/Fonts/Menlo.ttc'
_MONO = {}


def mono(fig, xy, s, size=38, color=INK):
    if size not in _MONO:
        _MONO[size] = ImageFont.truetype(MONO_PATH, size, index=0)
    f = _MONO[size]
    bb = fig.d.textbbox(xy, s, font=f, anchor='la')
    fig.d.text(xy, s, font=f, fill=color, anchor='la')
    fig.labels.append(dict(s=s, size=size, bold=False, bbox=bb, inside=None,
                           anchor='la', allow_overlap=False, tag=None,
                           skip_audit=False))
    fig.min_px = min(fig.min_px, size)
    return bb


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

    def px(self, x):
        a, b = self.xlim
        if self.logx:
            x, a, b = math.log10(x), math.log10(a), math.log10(b)
        return self.x0 + (self.x1 - self.x0) * (x - a) / (b - a)

    def py(self, y):
        a, b = self.ylim
        if self.logy:
            y, a, b = math.log10(max(y, 1e-12)), math.log10(a), math.log10(b)
        return self.y1 - (self.y1 - self.y0) * (y - a) / (b - a)

    def axes(self, xticks=(), yticks=(), xfmt='%g', yfmt='%g', xlab=None,
             ylab=None):
        for v in yticks:
            yy = self.py(v)
            self.f.line((self.x0, yy), (self.x1, yy), color=LIGHT, width=2)
            self.f.text((self.x0 - 18, yy - 21), yfmt % v, 40, color=GRAY,
                        anchor='ra')
        for v in xticks:
            xx = self.px(v)
            self.f.line((xx, self.y0), (xx, self.y1), color=LIGHT, width=2)
            self.f.text((xx, self.y1 + 14), xfmt % v, 40, color=GRAY, anchor='ma')
        self.f.line((self.x0, self.y1), (self.x1, self.y1), color=GRAY, width=3)
        self.f.line((self.x0, self.y0), (self.x0, self.y1), color=GRAY, width=3)
        if xlab:
            self.f.text((self.x1, self.y1 + 74), xlab, 40, color=GRAY, anchor='ra')
        if ylab:
            self.f.text((self.x0 - 10, self.y0 - 62), ylab, 40, color=GRAY,
                        anchor='la')

    def line(self, pts, color=TEAL, width=5, dash=None):
        pixels = [(self.px(x), self.py(y)) for x, y in pts]
        for a, b in zip(pixels, pixels[1:]):
            self.f.line(a, b, color=color, width=width, dash=dash)

    def dot(self, x, y, color=TEAL, r=13):
        self.f.circle(self.px(x), self.py(y), r, fill=color, outline=color)


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def photo(name, src, purpose, source, identity='真实照片'):
    im = Image.open(ART / 'originals' / src).convert('RGB')
    w, h = im.size
    if w > 1062:
        h = round(h * 1062 / w)
        im.resize((1062, h), Image.LANCZOS).save(ASSETS / name, quality=92,
                                                 optimize=True)
        w = 1062
    else:
        shutil.copyfile(ART / 'originals' / src, ASSETS / name)
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


def bar(fig, x, y, w, value, top, color, label=None, size=38):
    lo, hi = min(y, top), max(y, top)
    fig.rect(x, lo, x + w, hi, fill=color, outline=None)
    if label:
        fig.text((x + w + 14, min(y, top) + 12), label, size, color=INK)


# ---------------------------------------------------------------- figures


def fig01():
    fig, y = new(1, '一位也能存声音',
                 '不是靠数得细，是靠数得密。')
    x = 44
    for label, col in (('麦克风', TINT_T), ('环路', TINT_B), ('1 bit 流', TINT_A),
                       ('低通', TINT_G), ('耳朵', TINT_R)):
        chip(fig, (x, y + 30, x + 184, y + 150), label, col, size=42)
        if x < 800:
            fig.arrow((x + 190, y + 90), (x + 214, y + 90), color=GRAY, width=4)
        x += 204
    yy = y + 210
    yy += int(fig.wrap((44, yy), '模拟电压 → 每秒钟 282 万次「高了还是低了」'
                                 '→ 一串 0 和 1', 42, 974, color=INK_SOFT)
              * 42 * 1.35) + 20
    mono(fig, (44, yy), ' '.join(str(b) for b in R['tracking']['bits'][:22]))
    yy += 90
    y = note(fig, yy, '这一段是模型里真实跑出来的位流：输入从 0 慢慢爬到 0.85，'
                      '数一下就能看出「1」越来越多——平均值就是信号本身。')
    y = note(fig, y, '看起来什么都没记住：每个样点只有两种答案。'
                     '时间上的密度里，藏着比 1 bit 多得多的信息。')
    save(fig, '01-overview.png', '一位转换器的信号链：用密度而不是幅度表示信号')


def fig02():
    photo('02-cdp101.jpg', 'Sony-101_lettore-CD_Museo_scienza_tecnologia_Milano_08733.jpg',
          'Sony CDP-101，1982 年第一台量产 CD 机',
          'Museo Nazionale Scienza e Tecnologia Leonardo da Vinci, CC BY-SA 4.0, via Wikimedia Commons')


def fig03():
    fig, y = new(3, '把连续的值切成台阶',
                 '同样的输入，1 位只有两级，3 位有八级。')
    for k, (cx, bits, col, title) in enumerate(
            ((60, 1, RED, '1 位'), (560, 3, TEAL, '3 位'))):
        fig.text((cx, y), title, 42, bold=True, color=col)
        box = (cx, y + 60, cx + 420, y + 500)
        p = Plot(fig, box, (-1.25, 1.25), (-1.25, 1.25))
        p.axes(xticks=(), yticks=())
        steps = M.quantiser_steps(bits, 41)
        prev = None
        for q in steps:
            if prev is not None and abs(q['y'] - prev['y']) > 1e-9:
                p.line([(prev['x'], prev['y']), (q['x'], prev['y'])], color=col,
                       width=5)
                p.line([(q['x'], prev['y']), (q['x'], q['y'])], color=col, width=5)
            prev = q
        p.line([(q['x'], q['y']) for q in steps], color=col, width=5)
        fig.text((cx + 300, y + 470), '输入', 38, color=GRAY, anchor='ra')
        fig.text((cx, y + 560), '误差最多半格', 40, color=INK_SOFT)
        if bits == 1:
            fig.text((cx + 40, y + 610), '半格 = 满幅的一半', 40, color=RED)
        else:
            fig.text((cx + 40, y + 610), '半格 = 满幅的 1/16', 40, color=TEAL)

    y = y + 700
    y = note(fig, y, '量化误差听上去像白噪声：它和信号无关，均匀撒在 ±半格之间。'
                     '功率是「格子宽度」的平方除以 12——这条规律后面每一处都要用。')
    save(fig, '03-quantise.png', '1 位与 3 位量化器的台阶与量化误差')


def fig04():
    fig, y = new(4, '位数决定噪声底',
                 '满幅正弦：每多一位，信噪比多 6 dB。')
    p = Plot(fig, (250, y + 30, 1012, y + 520), (0, 25), (0, 155))
    p.axes(xticks=(1, 8, 16, 24), yticks=(0, 50, 100, 150), xlab='bit',
           ylab='dB')
    p.line([(r['bits'], r['snr']) for r in R['pcm']], color=TEAL, width=6)
    for r in (R['pcm'][0], R['pcm'][5]):
        p.dot(r['bits'], r['snr'], color=TEAL, r=15)
        fig.text((p.px(r['bits']) + 24, p.py(r['snr']) - 60),
                 '%d 位 %.0f dB' % (r['bits'], r['snr']), 40, bold=True)
    y = y + 680
    y = note(fig, y, '1 位按这把尺子只有 %.1f dB，也就是噪声只比信号低 8 dB——'
                     '连说话都盖不住。' % R['pcm'][0]['snr'])
    y = note(fig, y, '所以一 位转换器不能靠「数得细」。它换了一条路：'
                     '把样点变密，再把噪声赶到听不见的地方去。')
    save(fig, '04-sqnr.png', '信噪比与量化位数的 6 dB 规律，标出一位的位置')


def fig05():
    fig, y = new(5, '把噪声摊到更宽的带宽',
                 '同样的噪声功率，铺得越宽，每赫兹上就越薄。')
    d0 = R['quant_noise'] / 44100.0
    y0 = y + 60
    for k, (osr, fs, col, label) in enumerate(
            ((1, 44100.0, RED, 'OSR 1'), (64, 2822400.0, TEAL, 'OSR 64'))):
        dens = R['quant_noise'] / fs
        h = 150 if osr == 1 else 150 / 8
        x0 = 120
        ybase = y0 + 300 + k * 240
        fig.rect(x0, ybase, x0 + 780, ybase + h, fill=col, outline=None)
        fig.text((x0, ybase - 46), '%s：%s' % (label, '0–22 kHz' if osr == 1
                                               else '0–1.4 MHz'), 40, bold=True,
                 color=col)
        fig.text((x0 + 790, ybase + h / 2 - 24),
                 '%.1f dB' % (10 * math.log10(dens / d0)), 40, color=col,
                 anchor='ra')
    y = y0 + 700
    y = note(fig, y, '面积是噪声总功率，两种带宽下一样大（%0.3f）。宽度变成 64 倍，'
                     '高度就降到 1/64，也就是 −%.1f dB。' % (R['quant_noise'],
                                                          10 * math.log10(64)))
    y = note(fig, y, '这就是过采样的全部收益：不改变噪声，只把它铺开。'
                     '接下来再把剩下的那层噪声推到高频去。')
    save(fig, '05-oversample.png', '过采样把同样的噪声功率摊到更宽的频带上')


def fig06():
    fig, y = new(6, '过采样换来的信噪比',
                 '每加一倍采样率，一阶 +9 dB，二阶 +15 dB。')
    p = Plot(fig, (250, y + 40, 1012, y + 520), (1, 128), (-10, 110),
             logx=True)
    p.axes(xticks=(1, 4, 16, 64), yticks=(-10, 10, 40, 70, 100), xlab='OSR',
           ylab='dB')
    rows = R['oversample']
    p.line([(r['osr'], r['th1']) for r in rows], color=RED, width=4, dash=18)
    p.line([(r['osr'], r['sim1']) for r in rows], color=RED, width=6)
    p.line([(r['osr'], r['th2']) for r in rows], color=BLUE, width=4, dash=18)
    p.line([(r['osr'], r['sim2']) for r in rows], color=BLUE, width=6)
    fig.text((p.px(20), p.py(100) - 30), '二阶', 42, bold=True, color=BLUE)
    fig.text((p.px(20), p.py(46)), '一阶', 42, bold=True, color=RED)
    fig.text((p.px(1.4), p.py(105)), '实线是模型，虚线是公式', 38, color=GRAY)
    y = y + 630
    y = note(fig, y, 'OSR 64 时一阶模型 %.1f dB、二阶 %.1f dB。'
                     '同样的采样率，二阶多出 %.0f dB。' % (
                         R['sim']['o1'], R['sim']['o2'],
                         R['sim']['o2'] - R['sim']['o1']))
    y = note(fig, y, '公式总是比实测乐观 6–15 dB：它假设量化误差是白的、'
                     '幅度刚好一格，而一 位环路的误差是跟着信号变的。'
                     '差距是真实的，不妨碍趋势。')
    save(fig, '06-osr.png', '信噪比随过采样率上升：一阶每倍频程 9 dB，二阶 15 dB')


def fig07():
    fig, y = new(9, '噪声整形的形状',
                 '输出 = 信号 + (1−z⁻¹)ⁿ 乘上量化误差。')
    p = Plot(fig, (250, y + 40, 1012, y + 500), (0, 0.5), (0, 8))
    p.axes(xticks=(0, 0.1, 0.2, 0.3, 0.4, 0.5),
           yticks=(0, 2, 4, 6, 8), xlab='f / fs', ylab='|NTF|')
    for order, col in ((1, RED), (2, BLUE), (3, TEAL)):
        pts = [(k / 200.0, M.ntf_mag(k / 200.0, order)) for k in range(101)]
        p.line(pts, color=col, width=6)
    xb = 1 / 128.0
    p.line([(xb, 0), (xb, 8)], color=GRAY, width=4, dash=16)
    fig.text((p.px(xb) + 18, p.py(6.6)), '音频带宽', 38, color=GRAY)
    fig.text((p.px(0.02), p.py(2.1)), '一阶', 42, bold=True, color=RED)
    fig.text((p.px(0.20), p.py(4.3)), '二阶', 42, bold=True, color=BLUE)
    fig.text((p.px(0.32), p.py(7.0)), '三阶', 42, bold=True, color=TEAL)
    y = y + 670
    y = note(fig, y, '低频处 |NTF| 很小，噪声被压下去；到了 fs/2 附近它大于 1，'
                     '噪声被放大。整条曲线是守恒的搬运，不是消灭。')
    y = note(fig, y, '阶数越高，低频压得越狠，但高频也被抬得越高，'
                     '而且环路越容易不稳定。这就是设计里的那个取舍。')
    save(fig, '09-ntf.png', '一、二、三阶噪声传递函数的形状与带宽边界')


def fig08():
    fig, y = new(10, '实测的噪声斜率',
                 '把两条曲线各自对齐到 1 kHz，再看它们往上爬多快。')
    p = Plot(fig, (280, y + 40, 1012, y + 500), (100, 1.2e6), (-45, 25),
             logx=True)
    p.axes(xticks=(100, 1000, 10000, 100000),
           yticks=(-40, -20, 0, 20), xlab='Hz', ylab='dB')
    for key, col, lab in (('density1', RED, '一阶 %.1f dB/oct' % R['slope']['o1']),
                          ('density2', BLUE, '二阶 %.1f dB/oct' % R['slope']['o2'])):
        curve = R[key]
        ref = min(curve, key=lambda d: abs(d['f'] - 1000))
        pts = [(d['f'], 10 * math.log10(d['p'] / ref['p'])) for d in curve]
        p.line(pts, color=col, width=6)
    fig.text((p.px(150), p.py(-28)), '一阶：每倍频程 +6 dB', 40, bold=True,
             color=RED)
    fig.text((p.px(150), p.py(-40)), '二阶：每倍频程 +12 dB', 40, bold=True,
             color=BLUE)
    y = y + 610
    y = note(fig, y, '一阶实测 %.1f dB/oct，二阶 %.1f dB/oct，'
                     '和 |1−z⁻¹|ⁿ 的 6 与 12 对得上。' % (R['slope']['o1'],
                                                     R['slope']['o2']))
    y = note(fig, y, '功率谱是 20 dB/十倍频程还是 40 dB/十倍频程，'
                     '决定了同样的采样率下低频能干净多少。')
    save(fig, '10-density.png', '实测噪声密度斜率与理论阶数的对照')


def fig09():
    fig, y = new(7, '环路里只有三样东西',
                 '一个减法、一个累加、一个比较。')
    chip(fig, (60, y + 40, 210, y + 150), '求和', TINT_T, size=40)
    chip(fig, (330, y + 40, 520, y + 150), '积分器', TINT_B, size=40)
    chip(fig, (640, y + 40, 810, y + 150), '比较', TINT_A, size=40)
    fig.arrow((214, y + 95), (326, y + 95), color=INK, width=5)
    fig.arrow((524, y + 95), (636, y + 95), color=INK, width=5)
    fig.arrow((814, y + 95), (1000, y + 95), color=INK, width=5)
    fig.text((44, y + 170), '输入 u', 40, color=INK_SOFT)
    fig.text((860, y + 30), '输出 ±1', 40, color=RED, bold=True)
    # feedback path
    fig.line((920, y + 100), (920, y + 260), color=RED, width=5)
    fig.line((920, y + 260), (135, y + 260), color=RED, width=5)
    fig.line((135, y + 260), (135, y + 154), color=RED, width=5)
    fig.arrow((135, y + 200), (135, y + 156), color=RED, width=5)
    fig.text((300, y + 275), '把刚才那一位减回去', 40, color=RED)
    y = y + 360
    y = note(fig, y, '累加器一直在算「我想要的值」和「我实际给出的值」之间的差。'
                     '差是正的，下一次就给 +1；差是负的，就给 −1。')
    y = note(fig, y, '于是输出在 +1 和 −1 之间来回跳，跳的平均值跟着输入走。'
                     '这不是滤波，是反馈——误差没有被扔掉，被推迟到下一步处理。')
    save(fig, '07-loop.png', '一阶 delta-sigma 环路的三个组成部分与反馈路径')


def fig10():
    fig, y = new(8, '前 40 个样点在干什么',
                 '上升的输入、来回摆的积分器、越来越密的 1。')
    T = R['tracking']
    n = len(T['bits'])
    p = Plot(fig, (200, y + 40, 1012, y + 330), (0, n - 1), (-1.6, 1.6))
    p.axes(xticks=(0, 10, 20, 30, 39), yticks=(-1, 0, 1))
    p.line([(i, v) for i, v in enumerate(T['state'])], color=BLUE, width=5)
    p.line([(i, v) for i, v in enumerate(T['runavg'])], color=TEAL, width=6)
    fig.text((p.px(6), p.py(1.35)), '积分器状态', 38, color=BLUE)
    fig.text((p.px(24), p.py(0.02)), '位流的累计平均', 38, color=TEAL)
    yy = y + 380
    for i, b in enumerate(T['bits']):
        xx = 200 + i * 20.5
        col = INK if b else WHITE
        fig.rect(xx, yy, xx + 14, yy + 44, fill=col, outline=GRAY, width=2)
    fig.text((44, yy + 6), '输出位', 38, color=GRAY)
    yy += 80
    fig.text((44, yy + 6), '输入', 38, color=GRAY)
    for i, v in enumerate(T['inp'][:n]):
        xx = 200 + i * 20.5
        h = int(abs(v) * 90) + 2
        fig.rect(xx, yy + 40 - h if v > 0 else yy + 40, xx + 14,
                 yy + 40, fill=TINT_A, outline=None)
    y = yy + 110
    y = note(fig, y, '输入往上走，「1」的比例就变大。黑格越来越密，平均数跟上了输入——'
                     '这就是那位小数点的藏身之处。')
    save(fig, '08-tracking.png', '一阶环路前 40 个样点：输入、积分器状态与输出位')


def fig11():
    fig, y = new(11, '安静的时候它在唱歌',
                 '输入几乎为零，环路也会锁在一个固定频率上。')
    rows = [[('直流输入', INK, True), ('不加抖动', INK, True),
             ('加抖动', INK, True)]]
    seen = {}
    for r in R['dc_tones']:
        seen.setdefault(r['amp'], []).append(r)
    for amp, pair in sorted(seen.items()):
        a, b = pair[0], pair[1]
        rows.append([('%.4f' % amp, INK, False),
                     ('%.1fk/%.0f dB' % (a['f_hz'] / 1e3, a['level_db']),
                      RED, False),
                     ('%.1fk/%.0f dB' % (b['f_hz'] / 1e3, b['level_db']),
                      TEAL, False)])
    y = table(fig, y, [(60, 'la'), (300, 'la'), (660, 'la')], rows, size=38,
              row_h=76)
    y = note(fig, y, '第一行是很小的直流偏置，带内最大杂散 −66 dB，比信号还高——'
                     '这就是「鸟叫」，专业名叫 idle tone。')
    y = note(fig, y, '0.001 那行最典型：−60 dB，几乎和信号一样响。'
                     '加 1 位抖动以后，它被铺成噪声底，代价是整体噪声高了几 dB。')
    save(fig, '11-dither.png', '直流输入下的空闲音：抖动前后带内最大杂散对比')


def fig12():
    fig, y = new(12, '二阶的稳定边界',
                 '输入越大信噪比越好，直到环路开始打嗝。')
    p = Plot(fig, (250, y + 40, 1012, y + 490), (-42, 0), (0, 80))
    p.axes(xticks=(-40, -30, -20, -10, 0), yticks=(0, 20, 40, 60, 80),
           xlab='dBFS', ylab='dB')
    rows = R['amp']
    p.line([(r['db'], r['o1']) for r in rows], color=RED, width=6)
    p.line([(r['db'], r['o2']) for r in rows], color=BLUE, width=6)
    fig.text((p.px(-38), p.py(30)), '一阶', 42, bold=True, color=RED)
    fig.text((p.px(-20), p.py(63)), '二阶', 42, bold=True, color=BLUE)
    y = y + 600
    half = [r for r in rows if r['amp'] == 0.5][0]
    top = [r for r in rows if r['amp'] == 0.9][0]
    y = note(fig, y, '二阶在 −6 dBFS 到顶 %.1f dB，此时第二个积分器峰值 %.1f；'
                     '再往上推到 −0.9 dBFS，峰值冲到 %.1f，信噪比掉回 %.0f dB。'
                     % (half['o2'], half['peak2'], top['peak2'], top['o2']))
    y = note(fig, y, '所以二阶调制器的输入要留 3–6 dB 余量。一阶不会过载，'
                     '但它的天花板低得多——两个缺点换一个优点，这是模拟电路里最常见的买卖。')
    save(fig, '12-stability.png', '一阶与二阶环路的信噪比随输入电平变化')


def fig13():
    fig, y = new(13, '还得把速率降回来',
                 '输出是 2.8 MHz 的 0/1，最后的数字信号是 44.1 kHz。')
    yy = y + 40
    xs = [60, 300, 540, 780]
    for i, st in enumerate(R['decimation']):
        cx = xs[i]
        chip(fig, (cx, yy, cx + 200, yy + 150), '÷%d' % st['factor'],
             (TINT_B, TINT_T, TINT_G)[i], size=44)
        fig.text((cx, yy + 170), st['kind'], 38, color=INK_SOFT)
        fig.text((cx, yy + 220), '%.0f kHz' % (st['rate'] / 1e3), 40, bold=True)
        if i < 3:
            fig.arrow((cx + 206, yy + 75), (xs[i + 1] - 6, yy + 75), color=GRAY,
                      width=4)
    fig.text((44, yy - 40), '2.82 MHz', 40, color=GRAY)
    y = yy + 300
    y = note(fig, y, '每一级都先低通再丢样点：不先滤掉高频噪声就抽取，'
                     '被折叠回来的噪声会直接落进音频带里，前功尽弃。')
    y = note(fig, y, '第一级降得最多、对精度要求最低，适合 CIC；'
                     '后面几级降到 2 倍、再降到 1 倍，用半带滤波器，'
                     '系数一半是零，能省一半乘法。')
    save(fig, '13-decimation.png', '三级抽取链：2.82 MHz 一路降到 44.1 kHz')


def fig14():
    photo('14-tda1541.jpg', 'DAC_Philips_TDA1541A_S1.jpg',
          'Philips TDA1541A：16 位多比特 DAC，1980 年代 CD 机里的另一条路',
          'Cjp24, CC BY-SA 3.0, via Wikimedia Commons')


def fig15():
    photo('15-cd472-board.jpg', 'Philips_CD472_-_main_board-8122.jpg',
          'Philips CD472 主板：中间那块 28 脚芯片就是 TDA1541',
          'Raimond Spekking, CC BY-SA 4.0, via Wikimedia Commons')


def fig16():
    fig, y = new(16, '一位并不省数据',
                 '同样的音频，一位流的比特数比 CD 多。')
    rows = [[('方案', INK, True), ('Mbit/s', INK, True), ('说明', INK, True)]]
    short = {'CD 原始 PCM': '16 bit 单声道', '1 bit，OSR 64': '2.8224 Mbit/s',
             'DSD64': '同一串数', '1 bit，OSR 128': 'DSD128',
             '4 bit，OSR 64': '多级调制器'}
    for b in R['bits']:
        rows.append([(b['name'], INK, False),
                     ('%.2f' % (b['rate'] / 1e6), TEAL, False),
                     (short[b['name']], INK_SOFT, False)])
    y = table(fig, y, [(60, 'la'), (420, 'la'), (660, 'la')], rows, size=38,
              row_h=76)
    y = note(fig, y, 'DSD64 和「1 bit，OSR 64」是同一串数：2.8224 Mbit/s，'
                     '是 CD 原始数据率的 4 倍。')
    y = note(fig, y, '一位的好处不在带宽，在两个地方：DAC 只要两个电平，'
                     '做得很线性；环路本身简单，可以跑得很高。')
    save(fig, '16-bitbudget.png', '几种存储方式的比特率对照')


def fig17():
    photo('17-korg.jpg', 'KORG_MR-2000S_1-Bit_Studio_Recorder.jpg',
          'KORG MR-2000S：把 1 bit / 5.6 MHz 直接录成文件的录音机',
          'Brandon Daniel, CC BY-SA 2.0, via Wikimedia Commons')


def fig18():
    fig, y = new(18, '这条路走了六十年',
                 '从一篇苏联论文，到手机里的麦克风。')
    yy = y + 120
    fig.line((70, yy), (1000, yy), color=GRAY, width=5)
    nodes = ((110, '1962', 'Inose 与\nYasuda 提出\ndelta-sigma'),
             (330, '1982', 'CD 上市，\n16 位 PCM\n成为标准'),
             (560, '1990s', '一位 DAC\n进入平价\nCD 机'),
             (790, '2000s', 'MEMS 麦克风\n与手机音频\n普及'))
    for x, year, text in nodes:
        fig.circle(x, yy, 16, fill=TEAL, outline=TEAL)
        fig.text((x, yy - 90), year, 42, bold=True, color=TEAL, anchor='ma')
        fig.wrap((x - 100, yy + 34), text.replace('\n', ' '), 38, 210,
                 color=INK)
    y = yy + 300
    y = note(fig, y, 'delta-sigma 不是为音频发明的，早期用在仪表和语音编码里；'
                     'CD 把它带进了消费电子。')
    y = note(fig, y, '今天它在你手机的话筒、助听器、体重秤的 ADC 里，'
                     '也在每一块音频 codec 里——一块芯片里可能同时有十几个环路。')
    save(fig, '18-history.png', 'delta-sigma 从 1962 年到今天的时间线')


def fig19():
    fig, y = new(19, '带走三句话')
    y = bullets(fig, y + 10, [
        '一位不是低精度，是另一种坐标：把幅度换成密度，把误差换成频率。',
        '过采样把噪声摊开，噪声整形把它推到听不见的地方，抽取滤波再把高频扔掉。',
        '一阶一 位在 OSR 64 只有 %.0f dB，二阶能到 %.0f dB——'
        '位数不由「一位」决定，由环路阶数和采样率决定。'
        % (R['sim']['o1'], R['sim']['o2']),
    ])
    save(fig, '19-takeaways.png', '三条结论')


def cover():
    fig = Fig(1120)
    bg = '#101d26'
    for c in (bg, '#e8f0f6', '#8fb0d0', '#dfe9f2', '#1d3240'):
        PALETTE.add(c)
    fig.rect(0, 0, 1062, 4000, fill=bg, outline=None)
    # everything important stays inside y = 310..770, the band a 2.35:1
    # timeline crop keeps
    fig.text((70, 330), '一位', 150, bold=True, color='#e8f0f6')
    fig.text((70, 500), '也能存声音', 88, bold=True, color='#8fb0d0')
    bits = R['first_bits']
    for i, b in enumerate(bits):
        y0 = 630
        fig.rect(70 + i * 20, y0, 70 + i * 20 + 13, y0 + 86,
                 fill='#dfe9f2' if b else '#1d3240', outline=None)
    fig.text((70, 724), '2822400 次/秒的「高了还是低了」', 40, color='#8fb0d0')
    im = fig.im.crop((0, 0, 1080, 1080))
    im.save(ART / 'cover.png')
    print('   cover.png', im.size)


FIGS = [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig10,
        fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18, fig19]


def main(argv):
    want = set(argv[1:])
    for fn in FIGS:
        num = fn.__name__[3:]
        if want and num not in want:
            continue
        print('->', fn.__name__)
        fn()
    if not want or 'cover' in want:
        cover()
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(sorted(META, key=lambda r: r['path']), indent=1,
                   ensure_ascii=False) + '\n')


if __name__ == '__main__':
    import sys
    main(sys.argv)
