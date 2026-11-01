#!/usr/bin/env python3
"""Original teaching figures for the 0x5f3759df article. MIT.

Headline numbers come from results.json (written by run_model.py); the dense
curves are sampled by importing the same model, so figure and text can never
drift apart.
"""
from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageFont

from figkit import (Fig, PALETTE, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED,
                    GRAY, LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R,
                    TINT_G)

import rsqrt as M

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []

for c in ('#dfe9f2', '#b9cfe4', '#8fb0d0', '#628cb4', '#3d6390', '#26425f'):
    PALETTE.add(c)
HEAT = ['#dfe9f2', '#b9cfe4', '#8fb0d0', '#628cb4', '#3d6390', '#26425f']

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
            y, a, b = math.log10(y), math.log10(a), math.log10(b)
        return self.y1 - (self.y1 - self.y0) * (y - a) / (b - a)

    def axes(self, xticks=(), yticks=(), xfmt='%g', yfmt='%g', xlab=None):
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


def bin32(hexword):
    return format(int(hexword, 16), '032b')


def bitsplit(fig, x, y, word, size=38, color=INK):
    """Draw a 32-bit word as three coloured runs: sign | exponent | mantissa."""
    s, e, m = word[:1], word[1:9], word[9:]
    cx = x
    for txt, col in ((s, RED), (e, BLUE), (m, TEAL)):
        w = fig.width_of(txt, size)
        fig.rect(cx - 4, y - 8, cx + w + 4, y + size + 8, fill=WHITE, outline=col,
                 width=3)
        fig.text((cx, y), txt, size, color=col)
        cx += w + 18
    return cx


# ---------------------------------------------------------------- figures


def fig01():
    fig, y = new(1, '每个像素都要把法线拉直',
                 '光照公式里的点积只认单位向量。所以每帧都有上百万次 1/√x。')
    # a surface at an angle, with normal, light and eye
    fig.line((90, 700), (980, 560), color=INK, width=6)
    for k in range(18):
        x0 = 100 + k * 50
        fig.line((x0, 700 - k * 7.8), (x0 + 14, 690 - k * 7.8), color=LIGHT,
                 width=3)
    fig.line((300, 660), (420, 430), color=TEAL, width=6)
    fig.arrow((420, 430), (452, 358), color=TEAL, width=6)
    fig.text((300, 392), '法线 n', 42, bold=True, color=TEAL)
    fig.line((820, 240), (700, 470), color=AMBER, width=6)
    fig.arrow((700, 470), (668, 520), color=AMBER, width=6)
    fig.text((830, 216), '光线 l', 42, bold=True, color=AMBER)
    fig.text((96, 250), '亮度 ≈ max(0, n · l)', 44, bold=True)
    fig.text((96, 316), 'n 和 l 都是单位向量时，点积才是余弦', 40, color=INK_SOFT)
    fig.text((700, 700), '表面', 40, color=INK_SOFT)
    fig.line((560, 380), (700, 470), color=GRAY, width=3, dash=14)

    y = 790
    y = note(fig, y, '一个三角形有三个顶点，每个顶点有法线；插值到像素以后，'
                     '长度就不再是 1 了。想让它变回 1，就得除以自己的长度——'
                     '而长度是 √(x²+y²+z²)，也就是要算一次开方、一次除法。')
    y = note(fig, y, '这就是 1999 年那条三行代码想省掉的东西：'
                     '它直接要 1/√x，连 x 都不用先开方。')
    save(fig, '01-overview.png', '光照公式里法线与光线的点积，以及为什么需要单位化')


def fig02():
    photo('02-carmack.jpg', 'John_Carmack_-_QuakeCon_2008_-_02.jpg',
          'John Carmack，QuakeCon 2008',
          'QuakeCon, CC BY 2.0, via Wikimedia Commons')


def fig03():
    fig, y = new(3, '一个 float32 就是 32 个位',
                 '符号 1 位、指数 8 位、尾数 23 位。下面这行就是 x = 4.0 的位。')
    bitsplit(fig, 44, y + 20, bin32(R['examples'][0]['bits']))
    yy = y + 110
    fig.text((44, yy), '↑ 符号', 40, color=RED)
    fig.text((220, yy), '↑ 指数 8 位', 40, color=BLUE)
    fig.text((470, yy), '↑ 尾数 23 位', 40, color=TEAL)

    y = yy + 110
    rows = [
        [('字段', INK, True), ('位', INK, True), ('这一段存什么', INK, True)],
        [('符号', RED, False), ('1 位', INK, False), ('正还是负', INK_SOFT, False)],
        [('指数', BLUE, False), ('8 位', INK, False),
         ('2 的多少次方，偏移 127', INK_SOFT, False)],
        [('尾数', TEAL, False), ('23 位', INK, False),
         ('1.xxx 里小数点后面那截', INK_SOFT, False)],
    ]
    y = table(fig, y, [(60, 'la'), (210, 'la'), (420, 'la')], rows, size=38,
              row_h=76)
    y = note(fig, y, '4.0 = 1.0 × 2²，所以指数段存的是 127 + 2 = 129，'
                     '二进制 10000001；尾数全是 0。拼起来是 0x40800000。')
    y = note(fig, y, '关键的一点：指数段在 23 位的上面。也就是说，'
                     '把这串位当成一个整数看，它的大小顺序和浮点数的大小顺序是一样的——'
                     '这一条后面会变成全部的杠杆。')
    save(fig, '03-float32.png', 'float32 的字段布局，用 x = 4.0 的真实位模式标注')


def fig04():
    e4 = R['examples'][0]
    fig, y = new(4, '第一行：把位当整数移位再相减',
                 '下面每一步都是真实的位，不是示意。')
    rows = [
        [('步骤', INK, True), ('十六进制', INK, True), ('当成浮点数是', INK, True)],
        [('x', INK, False), (e4['bits'], GRAY, False),
         ('%g' % e4['x'], INK, False)],
        [('位数右移 1 位', INK, False), (e4['halves'], GRAY, False),
         ('——', INK_SOFT, False)],
        [('0x5f3759df − 它', INK, False), (e4['approx'], AMBER, False),
         ('%.6f' % e4['y0'], AMBER, False)],
        [('真值 1/√x', INK, False), ('——', INK_SOFT, False),
         ('%.6f' % e4['exact'], TEAL, False)],
    ]
    y = table(fig, y + 10, [(60, 'la'), (430, 'la'), (700, 'la')], rows, size=38,
              row_h=78)
    y = note(fig, y + 10, '一次整数移位、一次整数减法，就已经拿到 0.4831，'
                          '而真值是 0.5。误差 3.4%——对光照来说，这个精度还看不出问题。')
    y = note(fig, y, '接下来两行是修正：把这 3.4% 压到 0.17%，'
                     '再压到 0.00047%。修正用的是三百年前就有的办法。')
    save(fig, '04-three-steps.png', 'x = 4.0 经过移位、相减、得到近似值的三步位运算')


def fig05():
    fig, y = new(5, '右移一位为什么等于指数减半',
                 '因为指数段就压在高位上，右移的时候它被整体往下推。')
    e4 = R['examples'][0]
    b = bin32(e4['bits'])
    half = format(int(e4['halves'], 16), '032b')
    diff = bin32(e4['approx'])
    rows = [
        ('x = %g' % e4['x'], b, GRAY),
        ('>> 1', half, GRAY),
        ('0x5f3759df − 它', diff, AMBER),
    ]
    yy = y + 10
    for label, word, col in rows:
        fig.text((44, yy), label, 38, color=col if col is AMBER else INK)
        mono(fig, (44, yy + 50), '%s %s %s' % (word[:1], word[1:9], word[9:]), 38, col)
        yy += 108
    fig.text((44, yy), '符号 ↑    指数 8 位 ↑             尾数 23 位 ↑', 38,
             color=INK_SOFT)
    yy += 80
    yy = note(fig, yy, '指数段 10000001 是无符号数 129。右移一位，它被推下去一位，'
                       '高位让出来一个 0，于是它变成 01000000 = 64。')
    yy = note(fig, yy, '尾数也被推下去一位，等于把尾数除以 2；常数里的尾数再把它补回来。'
                       '整件事的本质是：**log 域里除以 2 就是开方，加个负号就是取倒数**，'
                       '而这两步在整数上就是移位和减法。')
    save(fig, '05-shift-means.png', '右移一位在位模式上的效果：指数被减半，尾数被推下去一位')


def fig06():
    fig, y = new(6, '从位里读出的 log₂ 是一条锯齿',
                 '纵轴是 log₂(x)。真实的 log₂ 是那条斜线，'
                 '从位模式里直接读出来的值是那条台阶。')
    p = Plot(fig, (250, y + 20, 1012, y + 540), (0.5, 1.0), (-1.05, 0.05))
    p.axes(xticks=(0.5, 0.6, 0.75, 0.9, 1.0), yticks=(-1.0, -0.5, 0.0),
           xfmt='%g', yfmt='%g', xlab='x')
    xs = [0.5 + i / 200.0 for i in range(201)]
    p.line([(x, M.log2_true(x)) for x in xs], color=GRAY, width=5)
    p.line([(x, M.log2_float_bits(x)) for x in xs], color=TEAL, width=6, dash=14)
    fig.text((p.px(0.505), p.py(-0.42)), '台阶：位 / 2²³ − 127', 38, color=TEAL)
    fig.text((p.px(0.78), p.py(-0.62)), '斜线：真的 log₂(x)', 38, color=GRAY)

    y = p.y1 + 150
    y = note(fig, y, '台阶比斜线低一截，而且低的位置随尾数变化。'
                     '下一张图把这一截单独拿出来看，它是那个常数的全部来历。')
    save(fig, '06-log2-saw.png', '从位模式读出的 log₂ 与真实 log₂ 的对照，呈锯齿状')


def fig07():
    fig, y = new(7, '那截差多少？一条浅弧',
                 '纵轴是 log₂(1+m) − m，m 是尾数。这条弧的形状决定了常数该取多少。')
    p = Plot(fig, (250, y + 20, 1012, y + 520), (0.0, 1.0), (0.0, 0.10))
    p.axes(xticks=(0, 0.25, 0.5, 0.75, 1.0), yticks=(0.0, 0.05, 0.10),
           xfmt='%g', yfmt='%.2f', xlab='尾数 m')
    fit = R['fit']
    p.line([(r['m'], r['diff']) for r in fit], color=TEAL, width=6)
    p.line([(0.0, R['sigma']), (1.0, R['sigma'])], color=AMBER, width=4, dash=16)
    fig.text((p.px(0.03), p.py(0.060)), 'σ = %.4f' % R['sigma'], 38, color=AMBER)
    fig.text((p.px(0.03), p.py(0.014)), '两端是 0，中间鼓到 +0.086', 38, color=TEAL)

    y = p.y1 + 130
    y = note(fig, y, '用一条水平线代替这条弧，最大偏差 ±%.3f——换成相对误差约 3%%，'
                     '正好对上后面那个 3.44%%。' % R['sigma'])
    save(fig, '07-fit-error.png', 'log₂(1+m) 与 m 的差随尾数的变化，以及水平近似线 σ')


def fig08():
    fig, y = new(8, '常数是怎么算出来的',
                 '把两条 log₂ 写法对齐，解出整数。全过程只有乘法和减法。')
    yy = y + 10
    mono(fig, (44, yy), 'log2(x) ≈ bits/2^23 - 127      (读位)', 38)
    mono(fig, (44, yy + 60), 'log2(x) ≈ bits/2^23 - 127 + σ  (加修正)', 38)
    mono(fig, (44, yy + 120), 'log2(1/√x) = -0.5 * log2(x)   (取倒数)', 38)
    yy += 210
    y2 = note(fig, yy, '要让 "-0.5 × 第一式的位" 等于 "第二式的位"，'
                       '就得把常数取成 A × (127 − σ)，其中 A = 1.5 × 2²³。')
    rows = [
        [('量', INK, True), ('值', INK, True)],
        [('A = 1.5 × 2²³', INK, False), ('12582912', GRAY, False)],
        [('σ（拟合出来的）', INK, False), ('%.7f' % R['sigma'], AMBER, False)],
        [('A × (127 − σ)，取整', INK, False),
         ('%d' % R['magic_from_sigma'], TEAL, True)],
        [('就是', INK, False), (R['magic'], INK, True)],
    ]
    y2 = table(fig, y2 + 12, [(60, 'la'), (620, 'la')], rows, size=38, row_h=74)
    y2 = note(fig, y2 + 8, '这里有个漂亮的细节：这条公式算出来正好是原版那个数，'
                           '一位不差。也就是说，1999 年写这行代码的人'
                           '（或者更早想到它的人）确实按这个思路推过。')
    save(fig, '08-derivation.png', '从 log₂ 近似式推出 0x5f3759df 的乘法与取整过程')


def fig09():
    fig, y = new(9, '第一次近似：3.4% 的锯齿',
                 '误差随 x 呈锯齿状，因为尾数是锯齿状的。')
    p = Plot(fig, (250, y + 20, 1012, y + 520), (0.01, 100), (0.0, 0.04),
             logx=True)
    p.axes(xticks=(0.01, 1, 100), yticks=(0.0, 0.02, 0.04),
           xfmt='%g', yfmt='%.2f', xlab='x（对数轴）')
    scan = R['scan']['e0']
    p.line([(x, e) for x, e in scan], color=RED, width=5)
    fig.text((p.px(0.013), p.py(0.036)), '峰 3.44%', 38, color=RED)
    fig.text((p.px(0.013), p.py(0.004)), '谷接近 0', 38, color=INK_SOFT)

    y = p.y1 + 150
    y = note(fig, y, '每个倍频程里，误差都从接近 0 爬到 3.44%，然后掉回去。'
                     '十四倍频程里重复了十四次——但峰值始终在 3.44%。')
    y = note(fig, y, '3.44% 对光照是可以接受的：它会让亮度差个零点几个百分点，'
                     '肉眼看不出来。真正不能接受的是它被用在别的地方——'
                     '比如物理里累加几百万次。')
    save(fig, '09-first-error.png', '只做位运算第一次近似的相对误差随 x 的变化')


def fig10():
    e4 = R['examples'][0]
    fig, y = new(10, '牛顿的办法：切线落到对的地方',
                 '要解的是 1/y² = x。在 y₀ 处画切线，切线与横线的交点就是 y₁。')
    p = Plot(fig, (290, y + 20, 1012, y + 520), (0.42, 0.62), (0.0, 7.5))
    p.axes(xticks=(0.45, 0.5, 0.55, 0.6), yticks=(0.0, 2.0, 4.0, 6.0),
           xfmt='%g', yfmt='%g', xlab='y')
    ys = [0.42 + i * 0.2 / 200.0 for i in range(201)]
    p.line([(v, 1.0 / (v * v)) for v in ys], color=TEAL, width=6)
    p.line([(0.42, 4.0), (0.62, 4.0)], color=AMBER, width=4)
    fig.text((1010, p.py(5.7)), '目标横线：1/y² = 4', 38, color=AMBER, anchor='ra')
    y0, y1 = e4['y0'], e4['y1']
    g0 = 1.0 / (y0 * y0)
    slope = -2.0 / (y0 ** 3)
    p.line([(y0 - 0.01, g0 - slope * 0.01), (y1 + 0.012, g0 + slope * (y1 + 0.012 - y0))],
           color=RED, width=4, dash=14)
    p.dot(y0, g0, RED, 12)
    p.dot(y1, 4.0, GREEN, 12)
    fig.text((p.px(y0) - 12, p.py(g0) + 22), 'y₀ = %.4f' % y0, 38, color=RED,
             anchor='ra')
    fig.text((p.px(y1) + 12, p.py(4.0) + 28), 'y₁ = %.5f' % y1, 38, color=GREEN)

    y = p.y1 + 150
    y = note(fig, y, '这一步用三百年不变：y ← y × (1.5 − 0.5·x·y²)。'
                     '它把 3.44% 的误差一次压到 0.17%，第二次压到 0.00047%。')
    y = note(fig, y, '为什么这么灵？因为 y₀ 已经很接近真值，'
                     '而牛顿法在根附近的收敛是平方级的——'
                     '误差每迭代一次大致被平方：0.034 → 0.0012 → 1.4e-6。')
    save(fig, '10-newton.png', '牛顿迭代的几何：切线从 y₀ 落到 y₁，横线是目标值')


def fig11():
    fig, y = new(11, '迭代两次，误差掉到百万分之五',
                 '纵轴是对数刻度的相对误差，三条线是同一条曲线的三个版本。')
    p = Plot(fig, (250, y + 20, 1012, y + 560), (0.01, 100), (1e-8, 0.2),
             logx=True, logy=True)
    p.axes(xticks=(0.01, 1, 100), yticks=(1e-8, 1e-5, 1e-2),
           xfmt='%g', yfmt='%.0e', xlab='x（对数轴）')
    for key, col, lab in (('e0', RED, '0 次'), ('e1', AMBER, '1 次'),
                          ('e2', TEAL, '2 次')):
        p.line([(x, max(e, 2e-8)) for x, e in R['scan'][key]], color=col, width=5)
    fig.text((p.px(0.012), p.py(0.13)), '0 次：峰 3.4%', 38, color=RED)
    fig.text((p.px(0.012), p.py(1.2e-3)), '1 次：峰 0.18%', 38, color=AMBER)
    fig.text((p.px(0.012), p.py(1.6e-5)), '2 次：峰 4.7e-6', 38, color=TEAL)

    y = p.y1 + 150
    y = note(fig, y, '注意每次迭代的效果：误差的峰值大约是不迭代时的平方除以某个常数。'
                     '这就是为什么两行代码就够了——第三行只能把误差再压三个数量级，'
                     '而 float32 自己只有七位有效数字。')
    save(fig, '11-iterations.png', '迭代 0 / 1 / 2 次后的相对误差，对数坐标')


def fig12():
    fig, y = new(12, '把误差铺成一张地图',
                 '横轴是尾数（从左到右 1.0→2.0），纵轴是指数。'
                 '每一格是一次迭代后的相对误差，颜色越深误差越大。')
    heat = R['heat']
    x0, y0 = 130, y + 40
    cw, ch = 18, 30
    for e, row in enumerate(heat):
        for k, val in enumerate(row['err_pct']):
            lvl = min(5, int(val / 0.0005))
            fig.rect(x0 + k * cw, y0 + e * ch, x0 + (k + 1) * cw - 1,
                     y0 + (e + 1) * ch - 1, fill=HEAT[lvl], outline=None)
    fig.text((44, y0 + 4), '大', 38, color=GRAY)
    fig.text((44, y0 + 14 * ch - 44), '小', 38, color=GRAY)
    fig.text((x0, y0 + 14 * ch + 16), '尾数（每格 1/47）→', 38, color=GRAY)
    fig.text((44, y0 - 54), '指数', 38, color=GRAY)
    fig.text((1010, y0 - 54), '误差越大颜色越深', 38, color=GRAY, anchor='ra')

    y = y0 + 14 * ch + 90
    y = note(fig, y, '同一行里误差随尾数变化（锯齿），不同行之间几乎一样（'
                     '因为指数每加一，相对误差不变）。这就是为什么'
                     '"3.44%" 一个数字就能概括整条曲线。')
    save(fig, '12-error-map.png', '指数 × 尾数网格上的一次迭代后相对误差热图')


def fig13():
    fig, y = new(13, '就是这三行', '原文在 q_math.c 里，注释比代码长。')
    lines = [
        ('float Q_rsqrt( float number ) {', INK),
        ('    i  = * ( long * ) &number;', INK),
        ('    i  = 0x5f3759df - ( i >> 1 );', AMBER),
        ('    y  = * ( float * ) &i;', INK),
        ('}', INK),
    ]
    yy = y + 14
    fig.rect(44, yy - 10, 1018, yy + len(lines) * 62 + 10, fill=WHITE,
             outline=LIGHT, width=3)
    for text, col in lines:
        mono(fig, (70, yy), text, 38, col)
        yy += 62
    yy += 44
    y2 = bullets(fig, yy, [
        '第一行：把这块内存当整数读——同样是 4 个字节，换一种解释',
        '第二行：右移一位再被常数减，这就是全部的秘密（橙色那行）',
        '第三行：把整数再解释回浮点，交出去',
    ])
    y2 = note(fig, y2, '原版在第三行之后还有两行牛顿迭代（y 和 x2 那几句），'
                       '这里为了看清主干省掉了。')
    save(fig, '13-three-lines.png', 'Quake III 快速平方根倒数的五行主干代码，等宽排版')


def fig14():
    photo('14-pentium3.jpg', 'Intel_Pentium_III_Coppermine_die.jpg',
          'Intel Pentium III (Coppermine) 芯片裸片',
          'Lp, public domain, via Wikimedia Commons')


def fig15():
    photo('15-quakecon.jpg', 'Quake_III_Arena_Duel_Finals_-_QuakeCon_2003_-_01.jpg',
          'QuakeCon 2003 的 Quake III Arena 决赛现场',
          'QuakeCon, CC BY 2.0, via Wikimedia Commons')


def fig16():
    fig, y = new(16, '三个常数，三种「最好」',
                 '目标函数不同，最优的那个整数就不同。')
    rows = [[('常数', INK, True), ('σ', INK, True), ('0 次', INK, True),
             ('1 次', INK, True)]]
    for r in R['table']:
        rows.append([(r['name'], INK, False), ('%.4f' % r['sigma'], GRAY, False),
                     ('%.4f' % (r['e0'] * 100), RED, False),
                     ('%.6f' % (r['e1'] * 100), TEAL, True)])
    y = table(fig, y + 10, [(60, 'la'), (430, 'la'), (600, 'la'), (800, 'la')],
              rows, size=38, row_h=76)
    y = note(fig, y + 10, '单位都是百分比。第三行那个常数是按 log₂ 拟合挑的，'
                          '它的第一次近似最准（3.42%），但加上牛顿迭代以后反而最差。'
                          '原版那个数不是这么挑的——它是冲着"迭代之后"去的。')
    y = note(fig, y, '在原版前后 300 个整数里再搜一遍，最好的是 %s，'
                     '比原版好 %.5f 个百分点。也就是说，原版已经在最优点附近两个整数以内。'
              % (R['sweep']['magic'], (R['table'][0]['e1'] - R['sweep']['err']) * 100))
    save(fig, '16-magics.png', '三个魔数常数对应的 σ 与迭代前后的最坏误差')


def fig17():
    fig, y = new(17, '拿几个具体数字试一遍',
                 'x 是任意正数；y₀ 是纯位运算的结果，y₁、y₂ 是迭代一次、两次。')
    rows = [[('x', INK, True), ('y₀', INK, True), ('y₁', AMBER, True),
             ('y₂', TEAL, True), ('1/√x', INK, True)]]
    for e in R['examples']:
        rows.append([('%g' % e['x'], INK, False), ('%.4f' % e['y0'], GRAY, False),
                     ('%.4f' % e['y1'], AMBER, False),
                     ('%.6f' % e['y2'], TEAL, False),
                     ('%.6f' % e['exact'], INK, True)])
    y = table(fig, y + 10, [(56, 'la'), (240, 'la'), (420, 'la'), (600, 'la'),
                            (806, 'la')], rows, size=38, row_h=74)
    y = note(fig, y + 10, '注意 x = 1 那一行：真值是 1，第一次近似是 0.9662。'
                          '位运算在这里最不准，因为它只是在指数上做减法，'
                          '尾数的细节全靠常数里的那点偏移。')
    save(fig, '17-examples.png', '六个具体输入的近似值、两次迭代结果与真值对照')


def fig18():
    fig, y = new(18, '这条代码的来历更有意思',
                 '没有人知道它最初是谁写的。能查到的是它怎么传开的。')
    rows = [
        [('时间', INK, True), ('发生了什么', INK, True)],
        [('1990 年代', INK, False), ('同一种位技巧在图形圈里流传', INK_SOFT, False)],
        [('1999', AMBER, False), ('随 Quake III Arena 发布，注释很粗', INK_SOFT, False)],
        [('2002', INK, False), ('有人在论坛上把它拆开讲了一遍', INK_SOFT, False)],
        [('2003', INK, False), ('Lomont 写报告，顺手搜出更好的常数', INK_SOFT, False)],
        [('2005', INK, False), ('id 以 GPL 公开源码，代码传遍全网', INK_SOFT, False)],
    ]
    y = table(fig, y + 10, [(60, 'la'), (300, 'la')], rows, size=38, row_h=78)
    y = note(fig, y + 10, '常见的说法把它归给某一个人，但公开讨论里至少有三位'
                          '在 1999 年之前就见过或写过类似的东西（SGI、Ardent 的老同事之间）。'
                          '所以本文只说"它随 Quake III 传开"，不说"它被谁发明"。')
    save(fig, '18-timeline.png', '这条技巧从 1990 年代流传到 2005 年开源的时间线')


def fig19():
    photo('19-sgi-indy.jpg', 'SGI_Indy_(1).jpg',
          'SGI Indy 工作站（1993），90 年代图形工作站的一台典型机器',
          'Peter Wallén, CC BY 3.0, via Wikimedia Commons')


def fig20():
    fig, y = new(20, '今天它换了个地方继续跑',
                 '现在没人手写这三行了——指令集直接给了一条。')
    rows = [
        [('平台', INK, True), ('一条指令做到', INK, True)],
        [('x86 SSE', INK, False), ('rsqrtss：一条指令，精度约 12 位', INK_SOFT, False)],
        [('ARM NEON', INK, False), ('vrsqrte：一条指令，精度约 8 位', INK_SOFT, False)],
        [('GPU', INK, False), ('rsqrt 近似指令，精度由厂商定', INK_SOFT, False)],
        [('C / C++', INK, False), ('1.0f / sqrtf(x) 由编译器决定用哪条', INK_SOFT, False)],
    ]
    y = table(fig, y + 10, [(60, 'la'), (330, 'la')], rows, size=38, row_h=78)
    y = note(fig, y + 10, '这些指令的精度和这条技巧差不多（十位左右有效数字），'
                          '所以它们同样是"够用就行"的产物，也同样的快。'
                          '硬件的做法是直接查表再迭代，思路一模一样。')
    save(fig, '20-today.png', '今天各平台上的平方根倒数指令对照')


def fig21():
    fig, y = new(21, '这件事能带走的三句话',
                 '不是"位运算很酷"，而是三个更耐用的想法。')
    y = bullets(fig, y + 10, [
        '同一个 32 位，可以是整数也可以是浮点。换个解释，就换了一套算术。',
        '一个函数不够准，可以用另一个函数去修它——修比算便宜得多。',
        '常数不是魔法，是某个近似目标下的最优解；换目标，它就变了。',
    ])
    y = note(fig, y + 10, '第三条最实用：看到别人代码里一个说不清的常数，'
                          '先问"它让什么误差最小"。答案往往就写在注释外面。')
    save(fig, '21-takeaways.png', '三条可以带走的想法')


def make_cover():
    for c in ('#101d26', '#27414f', '#7fa8c9', '#e8f0f6', '#f2b134', '#2fb3a8'):
        PALETTE.add(c)
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill='#101d26', outline=None)
    fig.text((96, 96), '一行代码', 76, bold=True, color='#ffffff')
    fig.text((96, 196), '算出 1/√x', 76, bold=True, color='#ffffff')
    fig.text((96, 306), '0x5f3759df 到底在干什么', 44, color='#7fa8c9')

    # the saw: relative error over two octaves
    x0, x1, mid = 96, 984, 560
    fig.line((x0, mid), (x1, mid), color='#27414f', width=3, dash=12)
    pts = []
    n = 160
    for k in range(n):
        x = 0.5 * (4.0 ** (k / (n - 1.0)))
        e = M.rel_err(x, M.fast_inv_sqrt(x, 1))
        pts.append((x0 + (x1 - x0) * k / (n - 1.0), mid - e / 0.0018 * 150))
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color='#2fb3a8', width=6)
    fig.text((x0, mid - 210), '迭代一次后的相对误差', 42, color='#2fb3a8')
    fig.text((x1, mid + 22), '0.18% 的峰，每倍频程一次', 40, color='#7fa8c9',
             anchor='ra')
    fig.text((96, 830), '一条位运算、一次减法、两次迭代', 44, color='#e8f0f6')
    fig.text((96, 940), 'tech-articles · 2026-11-16', 38, color='#7fa8c9')
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


FIGS = [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig10,
        fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18, fig19, fig20,
        fig21]


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


if __name__ == '__main__':
    main()
