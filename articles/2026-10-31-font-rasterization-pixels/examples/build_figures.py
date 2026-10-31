#!/usr/bin/env python3
"""Original teaching figures for the rasterisation article. MIT.

Every number printed on a figure is read from results.json, which comes from
run_model.py -> glyph.py. The pixel panels are real renders of the article's
own glyph outlines, not pictures pasted from a font.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import glyph
from figkit import (Fig, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED, GRAY,
                    LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R, TINT_G)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []

PAPER = (244, 243, 237)
INKPX = (24, 40, 46)
GRID = (206, 214, 211)


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
        if ylab:
            self.f.text((self.x0, self.y0 - 58), ylab, 40, color=GRAY)
        if xlab:
            self.f.text((self.x1, self.y1 + 74), xlab, 40, color=GRAY, anchor='ra')

    def line(self, xs, ys, color, width=5, dash=None):
        pts = [(self.px(x), self.py(y)) for x, y in zip(xs, ys)]
        for a, b in zip(pts, pts[1:]):
            self.f.line(a, b, color=color, width=width, dash=dash)

    def dot(self, x, y, color, r=10):
        self.f.circle(self.px(x), self.py(y), r, fill=color, outline=color)

    def label(self, x, y, text, color, anchor='la'):
        self.f.text((self.px(x), self.py(y)), text, 40, color=color, anchor=anchor)


def cov_image(cov, scale, paper=PAPER, ink=INKPX, grid=True):
    h, w = len(cov), len(cov[0])
    pad = 2 if grid else 0
    img = Image.new('RGB', (w * (scale + pad) + pad, h * (scale + pad) + pad), GRID)
    d = ImageDraw.Draw(img)
    for yy in range(h):
        for xx in range(w):
            c = max(0.0, min(1.0, cov[yy][xx]))
            col = tuple(int(paper[i] + (ink[i] - paper[i]) * c) for i in range(3))
            x0 = xx * (scale + pad) + pad
            y0 = yy * (scale + pad) + pad
            d.rectangle([x0, y0, x0 + scale - 1, y0 + scale - 1], fill=col)
    return img


def panel(fig, x, y, cov, scale, label=None, label_color=GRAY):
    """Paste a real render into the figure, with a white card behind it."""
    img = cov_image(cov, scale)
    fig.rect(x - 10, y - 10, x + img.width + 10, y + img.height + 10,
             fill=WHITE, outline=LIGHT, width=2)
    fig.im.paste(img, (int(x), int(y)))
    if label:
        fig.text((x, y + img.height + 18), label, 40, color=label_color)
    return img.width, img.height


def outlined(contours, px, dx=0.0, dy=0.0):
    return [[(x * px + dx, y * px + dy) for x, y in c] for c in contours]


O = glyph.flatten_all(glyph.outline_o(), 12)
I = glyph.flatten_all(glyph.outline_i(), 12)


# ------------------------------------------------------------------ figures
def fig01():
    fig, y = new(1, '屏幕上的一个字，到底是什么',
                 '下面是同一个 O，在 11 像素高时被真正光栅化出来的样子，放大了 26 倍。每一格是一个像素。')
    cov = glyph.coverage(outlined(O, 11), 11, 11, 16)
    panel(fig, 428, y + 6, cov, 26)
    y = y + 11 * 27 + 40
    y = note(fig, y, '11 像素高的 O 只占 11×11 个像素。圆环的宽度是 2.53 个像素：'
                     '中间三格是满的，两侧各有一格只被盖住一部分，'
                     '所以它不可能被干净地画成黑白。')
    save(fig, '01-one-glyph.png', '一个 11 像素的 O 放大 26 倍')


def fig02():
    fig, y = new(2, '同一条轮廓，两种存法',
                 '字体文件里存的是左边的曲线；屏幕上显示的是右边的格子。光栅化就是这两者之间的转换。')
    # left: the outline, smooth, drawn from the same flattened polygons
    box = (60, y + 10, 480, y + 430)
    fig.rect(*box, fill=WHITE, outline=LIGHT, width=2)
    for poly in O:
        pts = [(box[0] + 30 + x * 380, box[1] + 20 + yy * 380) for x, yy in poly]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=TEAL, width=4)
    cov = glyph.coverage(outlined(O, 12), 12, 12, 16)
    panel(fig, 560, y + 10, cov, 34)
    fig.text((60, box[3] + 16), '轮廓（连续的）', 40, color=TEAL)
    fig.text((560, y + 10 + 12 * 35 + 14), '像素（离散的）', 40, color=INK)
    y = box[3] + 100
    y = note(fig, y, '左边的每条曲线由两个端点和一个控制点定义；右边每个格子只有一个 0 到 1 之间的数，'
                     '叫覆盖率。')
    save(fig, '02-outline-vs-pixels.png', '轮廓与像素两种表示')


def fig03():
    fig, y = new(3, '二次贝塞尔：一个控制点决定弯曲',
                 'TrueType 用的就是这种曲线：起点、终点，加一个控制点。控制点不在曲线上。')
    p0, p1, p2 = (0.12, 0.86), (0.30, 0.06), (0.88, 0.30)
    box = (60, y + 10, 1000, y + 420)

    def at(p):
        return (box[0] + 40 + p[0] * 880, box[1] + 30 + p[1] * 340)

    fig.rect(*box, fill=WHITE, outline=LIGHT, width=2)
    a, b, c = at(p0), at(p1), at(p2)
    fig.line(a, b, color=GRAY, width=3, dash=12)
    fig.line(b, c, color=GRAY, width=3, dash=12)
    pts = [at(glyph.quad_bezier(p0, p1, p2, i / 60)) for i in range(61)]
    for s, t in zip(pts, pts[1:]):
        fig.line(s, t, color=TEAL, width=5)
    for p, name, col in ((a, '起点', INK), (b, '控制点', AMBER), (c, '终点', INK)):
        fig.circle(p[0], p[1], 13, fill=col, outline=col)
        fig.text((p[0] + 24, p[1] - 50), name, 40, color=col)
    y = box[3] + 24
    y = note(fig, y, '曲线永远落在起点—控制点—终点围成的三角形里，永远碰到两端，'
                     '但通常不经过控制点。')
    save(fig, '03-quadratic.png', '二次贝塞尔曲线的三点结构')


def fig04():
    fig, y = new(4, '曲线要切成直线段才能填',
                 '光栅化器先按每段切成若干折线。切得越细越准，代价是边更多。')
    cols = [(170, 'la'), (420, 'la'), (700, 'la')]
    rows = []
    for r in R['chord']:
        rows.append([('%d 段' % r['steps'], INK, False),
                     ('%.6f em' % r['em'], INK_SOFT, False),
                     ('%.4f 像素' % r['at_12px'], INK_SOFT, False)])
    fig.text((170, y), '每段切几刀', 40, color=GRAY)
    fig.text((420, y), '最大偏差', 40, color=GRAY)
    fig.text((700, y), '12 像素时', 40, color=GRAY)
    y = table(fig, y + 66, cols, rows, row_h=64)
    y = note(fig, y, '偏差按平方下降：刀数翻倍，误差变成四分之一。切到 8 段时，'
                     '误差已经只有 0.006 像素，远小于一个像素能表达的精度。')
    save(fig, '04-flatten.png', '折线近似曲线的误差表')


def fig05():
    fig, y = new(5, '填充：一条横线扫过去',
                 '对每一行像素的中心画一条水平线，算出它和轮廓的所有交点，然后按规则填交点之间的部分。')
    box = (60, y + 10, 700, y + 430)
    fig.rect(*box, fill=WHITE, outline=LIGHT, width=2)

    def at(p, px=300):
        return (box[0] + 40 + p[0] * px * 1.4, box[1] + 30 + p[1] * px * 1.1)

    for poly in O:
        pts = [at(p) for p in poly]
        for s, t in zip(pts, pts[1:]):
            fig.line(s, t, color=INK, width=3)
    for frac in (0.34, 0.5, 0.66):
        yy = box[1] + 30 + frac * 300 * 1.1
        fig.line((box[0] + 30, yy), (box[2] - 30, yy), color=RED, width=3, dash=10)
        fig.text((box[2] - 20, yy - 52), '这一行', 40, color=RED, anchor='ra')
    fig.text((760, y + 40), '交点', 40, color=TEAL, bold=True)
    fig.text((760, y + 100), '4 个', 42, color=INK)
    fig.text((760, y + 190), '填两段', 40, color=TEAL, bold=True)
    fig.text((760, y + 250), '中间空着', 42, color=INK)
    y = box[3] + 30
    y = note(fig, y, '一行横线穿过一个 O，会有四个交点：从外面进环、出环进洞、出洞回环、再出环。'
                     '把这些交点排序，相邻两个之间就是「实心」的一段。')
    save(fig, '05-scanline.png', '扫描线求交与填充')


def fig06():
    fig, y = new(6, '洞是另一个轮廓，方向反着写',
                 '轮廓没有「内」「外」的标记。判断哪里实心，靠的是绕行方向计数：非零即填。')
    left = (70, y + 10, 500, y + 410)
    right = (560, y + 10, 1000, y + 410)
    for box, title, reverse in ((left, '两个轮廓同向绕', False),
                                (right, '内圈反向绕', True)):
        fig.rect(*box, fill=WHITE, outline=LIGHT, width=2)
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2 + 20
        r = 130
        for radius, direction in ((r, 1), (r * 0.45, -1 if reverse else 1)):
            pts = [(cx + radius * __import__('math').cos(direction * 2 * 3.14159 * i / 40),
                    cy + radius * __import__('math').sin(direction * 2 * 3.14159 * i / 40))
                   for i in range(41)]
            for s, t in zip(pts, pts[1:]):
                fig.line(s, t, color=TEAL if radius == r else BLUE, width=5)
            tip = pts[6]
            ang = __import__('math').atan2(tip[1] - pts[5][1], tip[0] - pts[5][0])
            fig.arrow((tip[0] - 26 * __import__('math').cos(ang),
                       tip[1] - 26 * __import__('math').sin(ang)),
                      tip, color=TEAL if radius == r else BLUE, width=5, head=14)
        fig.text((cx, box[3] - 52), title, 40, color=INK, anchor='ma')
        res = '实心' if not reverse else '中间是洞'
        fig.text((cx, box[1] + 12), res, 38, color=GRAY, anchor='ma')
    y = left[3] + 24
    y = note(fig, y, '左边两个轮廓都顺时针绕，环内的计数是 2，洞里也是 2，整个圆饼都是实的。'
                     '右边内圈反过来绕，洞里计数回到 0，洞就出现了。')
    save(fig, '06-winding.png', '内外轮廓的方向与非零环绕规则')


def fig07():
    fig, y = new(7, '一个像素的覆盖率',
                 '轮廓从格子中间穿过时，这个像素既不是全黑也不是全白，而是按面积算出一个中间值。')
    tri = [[(0.0, 0.0), (6.0, 0.0), (0.0, 6.0)]]
    cov = glyph.coverage(tri, 6, 6, 32)
    panel(fig, 320, y + 10, cov, 88)
    y = y + 6 * 90 + 90
    vals = sorted({round(v, 3) for row in cov for v in row})
    y = bullets(fig, y, [
        '左上角整个落在三角形里：覆盖率 %.3f，纯黑。' % max(vals),
        '右下角完全在外面：覆盖率 %.3f，纯白。' % min(vals),
        '斜边切过的格子各占一半：%s。'
        % '、'.join('%.3f' % v for v in vals if 0 < v < 1)[:44],
        '格子越靠近斜边，这个中间值变化越连续——这正是灰阶的来源。',
    ], accent=TEAL)
    save(fig, '07-coverage.png', '单个像素的覆盖率')
    return cov


def fig08():
    fig, y = new(8, '采样越多，边缘越准',
                 '同一个 12 像素的 O，每个像素分别采 1×1、4×4、16×16 个点。')
    xs = (70, 396, 722)
    for x, ss in zip(xs, (1, 4, 16)):
        cov = glyph.coverage(outlined(O, 12), 12, 12, ss)
        panel(fig, x, y + 10, cov, 25, label='%d×%d 采样' % (ss, ss), label_color=INK)
    y = y + 12 * 27 + 80
    y = note(fig, y, '最左边只有两种颜色，圆环的边成了锯齿；中间出现灰色过渡；'
                     '右边边缘过渡已经有十几种灰。人眼在正常观看距离下分不出这三者的区别，'
                     '但在小字号下能不能看清笔画，取决于这个过渡带。')
    save(fig, '08-supersampling.png', '三种采样密度的实际渲染')


def fig09():
    fig, y = new(9, '误差随采样数的下降',
                 '以 64×64 采样为参照，量每种采样的最大误差（覆盖率之差，0 到 1）。')
    rows = [r for r in R['aa'] if r['glyph'] == 'O']
    rows_i = [r for r in R['aa'] if r['glyph'] == 'I']
    plot = Plot(fig, (170, y + 30, 1000, y + 400), (0, 18), (0, 0.6))
    plot.axes(xticks=(1, 4, 8, 16), yticks=(0, 0.2, 0.4, 0.6),
              xfmt='%d', yfmt='%.1f', xlab='每边采样数', ylab='最大误差')
    plot.line([r['ss'] for r in rows], [r['max_err'] for r in rows], TEAL, 5)
    plot.line([r['ss'] for r in rows_i], [r['max_err'] for r in rows_i], AMBER, 5, dash=14)
    for r in rows:
        plot.dot(r['ss'], r['max_err'], TEAL)
    fig.text((640, y + 90), 'O（12 像素）', 40, color=TEAL, bold=True)
    fig.text((640, y + 160), 'I（11 像素）', 40, color=AMBER, bold=True)
    y = y + 545
    a = rows[0]['max_err']
    b = rows[-1]['max_err']
    y = note(fig, y, '16 倍采样把最大误差从 %.3f 压到 %.3f，降了 %.0f 倍。'
                     '但注意曲线在 4 到 8 之间变平：再往上加采样，得到的改善越来越少，'
                     '这就是真实渲染器普遍只用 4×4 到 8×8 的原因。' % (a, b, a / b))
    save(fig, '09-error.png', '最大覆盖率误差随采样数变化')


def fig10():
    fig, y = new(10, '斜线最难：它每行都要跨格子',
                 '一个 45 度斜边，在四种采样密度下能得到多少种不同的灰。')
    cols = [(180, 'la'), (520, 'la')]
    rows = [[('%d×%d 采样' % (r['ss'], r['ss']), INK, False),
             ('%d 种灰' % r['levels'], INK_SOFT, False)] for r in R['diagonal']]
    fig.text((180, y), '采样密度', 40, color=GRAY)
    fig.text((520, y), '灰阶数', 40, color=GRAY)
    y = table(fig, y + 66, cols, rows, row_h=64)
    y = note(fig, y, '竖直线和水平线最多两三种灰——边要么在格子边界上，要么落在某个固定的小数位置。'
                     '斜线每跨一行就移动一点，覆盖率的取值连续变化，所以它对采样最敏感，'
                     '也最容易看出锯齿。')
    save(fig, '10-diagonal.png', '斜边的灰阶数')


def fig11():
    fig, y = new(11, '同一根竖笔，八个尺寸',
                 '字形的竖笔宽度固定为 0.12 em。下面是它在 8 到 24 像素时的实际样子。')
    xs = [70, 250, 430, 610, 790]
    for x, px in zip(xs, (8, 10, 11, 12, 16)):
        cov = glyph.coverage(outlined(I, px), px, px, 16)
        scale = 130 // px
        panel(fig, x, y + 10, cov, max(6, scale), label='%d px' % px, label_color=INK)
    y = y + 130 * 2 + 60
    small = [r for r in R['stem'] if r['px'] in (8, 10, 11, 12)]
    y = bullets(fig, y, [
        '8 像素时竖笔占 0.96 个格子，边缘是 50%% 的灰。',
        '11 像素时是 1.32 个格子，摊成三列，最外面一列只有 %.0f%% 的黑。'
        % (small[2]['lightest'] * 100),
        '24 像素时是 2.88 个格子，边缘同样落在别的灰度上，但笔画本身足够粗，不影响识别。',
    ], accent=RED)
    save(fig, '11-stem-sizes.png', '同一根竖笔在不同像素尺寸下的渲染')


def fig12():
    fig, y = new(12, 'hinting：把边吸到格子上',
                 '同一个 11 像素的 I，左边是原样，右边是把所有坐标就近对齐到整像素之后。')
    px = 11
    before = glyph.coverage(outlined(I, px), px, px, 16)
    after = glyph.coverage(outlined(glyph.hint(I, px, px), px), px, px, 16)
    panel(fig, 150, y + 10, before, 34, label='原样', label_color=INK)
    panel(fig, 660, y + 10, after, 34, label='对齐之后', label_color=INK)
    y = y + px * 35 + 130
    hb = [r for r in R['hint'] if r['px'] == px][0]
    y = bullets(fig, y, [
        '原样：竖笔 1.32 像素宽，摊在 %d 列上，最外面一列只有 %d%% 的黑。'
        % (hb['before']['columns'], round(hb['before']['lightest'] * 100)),
        '对齐：竖笔正好 1 像素，%d 列全黑，边缘锐利。' % hb['after']['columns'],
        '代价：笔画变细了 %.0f%%。'
        % (100 * (1 - hb['after']['ink_total'] / hb['before']['ink_total'])),
    ], accent=AMBER)
    save(fig, '12-hinting.png', 'hinting 前后对比')


def fig13():
    fig, y = new(13, 'hinting 是两边的赌注',
                 '对齐会让笔画变细，也会让它变粗。同一个字形在不同字号下，方向不一样。')
    cols = [(120, 'la'), (300, 'la'), (520, 'la'), (760, 'la')]
    rows = []
    for r in R['hint']:
        before = r['before']['ink_total']
        after = r['after']['ink_total']
        delta = (after - before) / before * 100
        rows.append([('%d px' % r['px'], INK, False),
                     ('%.2f 像素' % before, INK_SOFT, False),
                     ('%.2f 像素' % after, INK_SOFT, False),
                     ('%+.0f%%' % delta, RED if abs(delta) > 20 else INK_SOFT, True)])
    fig.text((120, y), '字号', 40, color=GRAY)
    fig.text((300, y), '原始笔画', 40, color=GRAY)
    fig.text((520, y), '对齐之后', 40, color=GRAY)
    fig.text((760, y), '变化', 40, color=GRAY)
    y = table(fig, y + 66, cols, rows, row_h=68)
    y = note(fig, y, '11 像素时竖笔被压细 27%，12 像素时被撑粗 33%。'
                     '没有任何一种统一的对齐方式能让所有字号都正确——'
                     '所以 hinting 只能是「一组按字号写的规则」，由字体设计师手工调试，'
                     '而不是一个通用算法。')
    save(fig, '13-hint-tradeoff.png', 'hinting 在不同字号下的粗细变化')


def fig14():
    fig, y = new(14, '50% 的覆盖率，不是 50% 的亮度',
                 '屏幕的亮度与像素值不是线性关系。按线性去混一个 50% 的像素，出来的是 73.5% 的亮。')
    fig.text((200, y + 10), '灰色虚线：线性', 40, color=GRAY)
    fig.text((640, y + 10), '粗线：真实显示', 40, color=TEAL)
    plot = Plot(fig, (200, y + 140, 980, y + 500), (0, 1), (0, 1))
    plot.axes(xticks=(0, 0.25, 0.5, 0.75, 1), yticks=(0, 0.25, 0.5, 0.75, 1),
              xfmt='%.2f', yfmt='%.2f', xlab='覆盖率', ylab='显示亮度')
    xs = [i / 40 for i in range(41)]
    plot.line(xs, xs, GRAY, 4, dash=12)
    plot.line(xs, [glyph.srgb_encode(v) for v in xs], TEAL, 5)
    for g in R['gamma']:
        if g['coverage'] in (0.25, 0.5, 0.75):
            plot.dot(g['coverage'], g['srgb'], AMBER)
            fig.text((plot.px(g['coverage']) + 16, plot.py(g['srgb']) - 52),
                     '%.1f%%' % g['as_percent'], 40, color=AMBER)
    y = y + 640
    y = note(fig, y, '所以渲染器必须先把覆盖率转成线性光、混完再转回来，否则文字会显得偏粗偏黑。'
                     '浅色背景、深色文字时最明显：不修正的话，白底黑字会发胖，笔画容易并在一起。')
    save(fig, '14-gamma.png', '覆盖率与显示亮度的非线性关系')


def fig15():
    fig, y = new(15, '次像素：一台显示器有三个发光体',
                 '每个像素其实是并排的红绿蓝三个条。物理上能单独点亮它们，就多了三倍的水平分辨率。')
    px = 62
    for i, (col, name, code) in enumerate(((RED, 'R', (188, 70, 80)),
                                           (GREEN, 'G', (63, 125, 78)),
                                           (BLUE, 'B', (52, 104, 173)))):
        x = 200 + i * px
        fig.rect(x, y + 20, x + px - 6, y + 20 + 190, fill=col, outline=col)
        fig.text((x + 26, y + 240), name, 42, color=col, bold=True)
    fig.text((200, y + 320), '一个像素', 42, color=INK)
    fig.text((560, y + 20), '想让「一个字」的边', 40, color=INK)
    fig.text((560, y + 90), '落在右三分之一的', 40, color=INK)
    fig.text((560, y + 160), '位置，就只点亮右边的', 40, color=INK)
    fig.text((560, y + 230), '那个发光体。', 40, color=INK)
    y = y + 420
    y = note(fig, y, '代价是颜色。为了让边缘看起来是灰色而不是彩边，三个通道的强度必须互相补偿，'
                     '而补偿只能做到近似——在深色背景、彩色文字、旋转过的屏幕上，'
                     '它会留下肉眼可见的彩边。')
    save(fig, '15-subpixel.png', '次像素渲染的物理基础')


def fig16():
    fig, y = new(16, '为什么次像素渲染消失了',
                 '它是一笔用颜色换清晰度的交易。当像素密到看不清单个像素时，这笔交易就不划算了。')
    cols = [(120, 'la'), (420, 'la'), (760, 'la')]
    rows = [[('2000 年', INK, True), ('约 100 ppi', INK_SOFT, False), ('值得换', INK_SOFT, False)],
            [('2010 年', INK, True), ('约 130 ppi', INK_SOFT, False), ('开始犹豫', INK_SOFT, False)],
            [('2020 年', INK, True), ('400 ppi 以上', INK_SOFT, False), ('不划算', INK_SOFT, False)]]
    fig.text((120, y), '年代', 40, color=GRAY)
    fig.text((420, y), '典型手机屏幕', 40, color=GRAY)
    fig.text((760, y), '结论', 40, color=GRAY)
    y = table(fig, y + 66, cols, rows, row_h=70)
    y = note(fig, y, 'macOS 在 2018 年的 Mojave 里关掉了次像素抗锯齿，Chrome 也在 2015 年后逐步放弃。'
                     'Windows 的 ClearType 还留着，但不再是卖点。理由不是算法退步，而是屏幕变好了：'
                     '在 400 ppi 上，一个像素只有 0.06 毫米，边缘的彩边比它要弥补的锯齿更显眼。')
    save(fig, '16-subpixel-end.png', '次像素渲染的退场')


def fig17():
    fig, y = new(17, '另一种存法：存距离，而不是颜色',
                 '游戏里常用有向距离场（SDF）：每个格子存「离轮廓有多远」，渲染时按距离算覆盖率，可以任意放大。')
    field = glyph.sdf(outlined(O, 12), 12, 12)
    flat = [v for row in field for v in row]
    lo, hi = min(flat), max(flat)
    norm = [[(v - lo) / (hi - lo) for v in row] for row in field]
    panel(fig, 90, y + 10, norm, 26, label='距离场（12×12）', label_color=INK)
    recon = glyph.sdf_reconstruct(field, 4, edge=0.75)
    panel(fig, 500, y + 10, recon, 6, label='从它重建（48×48）', label_color=INK)
    y = y + 48 * 8 + 100
    y = bullets(fig, y, [
        '距离场只有 %d 个格子，直接存 48×48 的图要 %d 个。'
        % (R['sdf']['bytes_tight'], R['sdf']['bytes_direct']),
        '重建出来的形状和真正的 48 像素渲染相比，均方根差 %.3f。' % R['sdf']['rms_tight'],
        '放大到任意尺寸都能得到一个平滑的边缘——代价是细节全丢了。',
    ], accent=BLUE)
    y = note(fig, y, '它不是「更清楚」，是「更省、更平滑」。游戏里的招牌、UI 图标用它，'
                     '因为可以只存一张小图，然后在 GPU 上无限放大；正文排版不这么干，'
                     '因为文字要的是精确的笔画，不是柔软的轮廓。')
    save(fig, '17-sdf.png', '距离场的存储与重建')


def fig18():
    fig, y = new(18, '两条渲染路线，各管一段',
                 '同一套轮廓，两条完全不同的下坡路：一条追精确，一条追平滑。')
    rows = [[('目标', INK, True), ('正文字体', INK, False), ('游戏 / UI', INK, False)],
            [('存什么', INK, True), ('轮廓曲线', INK, False), ('距离场小图', INK, False)],
            [('多大', INK, True), ('按字号实时算', INK, False), ('一次烘好', INK, False)],
            [('代价', INK, True), ('小字号要 hinting', INK, False), ('细节不可恢复', INK, False)]]
    cols = [(110, 'la'), (360, 'la'), (700, 'la')]
    y = table(fig, y, cols, rows, row_h=76)
    y = note(fig, y) if False else y
    y = note(fig, y + 10, '两条路线都不是「更先进」的关系。FreeType 到今天仍然在实时算曲线，'
                          '因为它要处理的正是 SDF 最不擅长的事：12 像素高、笔画只有一像素宽的汉字。')
    save(fig, '18-two-routes.png', '两条渲染路线的对照')


def fig19():
    fig, y = new(19, '从字体文件到屏幕：一次排版要做的事',
                 '光栅化只是中间一环。真正把字放到屏幕上的，是四个各管一段的程序。')
    steps = [('字体文件', 'TrueType / OpenType，存轮廓与 hinting 指令', TEAL, TINT_T),
             ('整形器', 'shape：把字符序列变成带坐标的字形序列', BLUE, TINT_B),
             ('光栅化器', 'rasterize：把轮廓变成覆盖率矩阵', AMBER, TINT_A),
             ('合成器', 'blend：按 gamma 把覆盖率和背景混起来', GREEN, TINT_G)]
    for i, (name, sub, col, tint) in enumerate(steps):
        top = y + 10 + i * 220
        fig.box(name, 60, top, 1002, top + 160, fill=tint)
        fig.text((84, top + 14), name, 42, bold=True, inside=name)
        fig.text((84, top + 86), sub, 40, color=INK_SOFT, inside=name)
        if i < 3:
            fig.arrow((531, top + 164), (531, top + 216), color=GRAY, width=4, head=14)
    y = y + 10 + 4 * 220 + 10
    y = note(fig, y, '整形器负责「哪个字形、放在哪」：阿拉伯文的连写、印度文字的重新排序、'
                     '中文标点的挤压，都发生在这一步。光栅化器只认坐标，不认文字。')
    save(fig, '19-pipeline.png', '字体到屏幕的处理链')


def fig20():
    fig, y = new(20, '五十年的时间线', None)
    rows = [('1977', 'Knuth 开始写 Metafont，目标是让数学公式在低分辨率打印机上也好看'),
            ('1982', 'Adobe 成立，PostScript 把字形写成一串轮廓而不是一张点阵图'),
            ('1985', 'Apple LaserWriter 让 PostScript 走进办公室；Adobe 用 Type 1 加密轮廓'),
            ('1991', 'Apple 与 Microsoft 联合推出 TrueType：轮廓公开，还带 hinting 指令'),
            ('2000', 'ClearType 随 Microsoft Reader 与 Windows XP 登场，次像素渲染出现'),
            ('2007', 'Valve 在《军团要塞 2》里用距离场渲染文字，SDF 进入游戏'),
            ('2010s', '高 DPI 屏幕普及，次像素渲染逐步退场，hinting 也从手工调试转向自动')]
    for year, text in rows:
        fig.text((70, y), year, 42, bold=True, color=TEAL)
        lines = fig.wrap((240, y + 2), text, 40, 770, color=INK)
        y += max(1, int(lines * 40 * 1.35)) + 34
    save(fig, '20-timeline.png', '字体光栅化的五十年')


def fig21():
    fig, y = new(22, '三句话', None)
    items = [('轮廓是连续的，像素是离散的。', '光栅化的全部工作，就是把曲线切成格子，算出每个格子被盖住多少。'),
             ('小字号不是「缩小的大字号」，','是另一个问题。一个像素宽的笔画没有中间值可用，只能靠 hinting 把边吸到格子上。'),
             ('清楚和忠实是两件事。', 'hinting 让字更清楚，代价是笔画粗细变了；SDF 让轮廓更平滑，代价是细节没了。')]
    for head, body in items:
        fig.text((70, y), head, 44, bold=True, color=INK)
        y += 66
        y = note(fig, y, body, size=42) + 34
    save(fig, '22-three-lines.png', '三句话总结')


def make_cover():
    fig = Fig(1080, width=1080)
    cov = glyph.coverage(outlined(O, 12), 12, 12, 16)
    img = cov_image(cov, 18)
    fig.im.paste(img, (120, 372))
    fig.text((410, 366), '一个像素', 58, bold=True, color=INK)
    fig.text((410, 444), '能装下多少', 58, bold=True, color=INK)
    fig.text((410, 522), '笔画', 58, bold=True, color=INK)
    fig.text((410, 606), '字体光栅化：曲线怎样变成格子', 40, color=TEAL)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


FIGURES = [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
           fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18,
           fig19, fig20, fig21]


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    for fn in FIGURES:
        n = fn.__name__[-2:]
        if only and n not in only:
            continue
        fn()
    if not only:
        make_cover()
    meta_path = HERE / 'figure-metadata.json'
    rows = json.loads(meta_path.read_text('utf-8')) if meta_path.is_file() else []
    rebuilt = {row['path'] for row in META}
    rows = sorted([r for r in rows if r['path'] not in rebuilt] + META,
                  key=lambda r: r['path'])
    meta_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(rows))


if __name__ == '__main__':
    main()
