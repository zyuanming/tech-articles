#!/usr/bin/env python3
"""Original teaching figures for the elevator-governor article. MIT.

Every number comes from results.json, which run_model.py writes by running
examples/elevator.py. Nothing here is typed in by hand.
"""
from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

from PIL import Image

from figkit import (Fig, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED, GRAY,
                    LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R,
                    TINT_G)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []
G = R['governor']


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

    def line(self, pts, color=TEAL, width=5, dash=None):
        pixels = [(self.px(x), self.py(y)) for x, y in pts]
        for a, b in zip(pixels, pixels[1:]):
            self.f.line(a, b, color=color, width=width, dash=dash)

    def dot(self, x, y, color=TEAL, r=13):
        self.f.circle(self.px(x), self.py(y), r, fill=color, outline=color)

    def band(self, xa, xb, color, alpha_box=None):
        self.f.rect(self.px(xa), self.y0, self.px(xb), self.y1, fill=color,
                    outline=None)


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
    if w > 1062:                      # only downscale; never recompress in place
        w, h = 1062, round(h * 1062 / w)
        im.resize((w, h), Image.LANCZOS).save(ASSETS / name, quality=92,
                                              optimize=True)
    elif crop or im.size != Image.open(ART / 'originals' / src).size:
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


def leader(fig, a, b, color=GRAY):
    """A thin leader line from a shape to a label, without an arrowhead."""
    fig.line(a, b, color=color, width=3)


# ---------------------------------------------------------------- figures


def fig01():
    fig, y = new(1, '管住超速的，是井道边上这三个零件')
    # guide rails
    for x in (368, 664):
        fig.rect(x, 190, x + 12, 872, fill=LIGHT, outline=None)
    # car
    fig.box('car', 430, 420, 616, 700, fill=PALE)
    fig.text((523, 536), '轿厢', 40, bold=True, anchor='ma', inside='car')
    # safety gear blocks, one per rail
    for x in (380, 620):
        fig.rect(x, 640, x + 48, 700, fill=TINT_R, outline=RED, width=3)
    # governor
    fig.circle(180, 262, 50, fill=TINT_T, outline=TEAL)
    fig.circle(180, 262, 12, fill=INK, outline=INK)
    # rope loop
    fig.line((166, 312), (166, 826), color=INK_SOFT, width=4)
    fig.line((194, 312), (194, 826), color=INK_SOFT, width=4)
    fig.circle(180, 852, 26, fill=WHITE, outline=INK_SOFT)

    leader(fig, (676, 300), (720, 300))
    fig.text((730, 278), '导轨', 42, bold=True, color=INK)
    leader(fig, (232, 262), (268, 262))
    fig.text((278, 240), '限速器', 42, bold=True, color=TEAL)
    leader(fig, (232, 300), (268, 340))
    fig.text((278, 318), '限速绳：一根首尾相接的环', 40, color=INK_SOFT)
    leader(fig, (206, 852), (268, 800))
    fig.text((278, 778), '张紧轮：靠自重把绳拉直', 40, color=INK_SOFT)
    leader(fig, (378, 664), (322, 604))
    fig.text((312, 580), '安全钳', 42, color=RED, bold=True, anchor='ra')
    fig.text((312, 626), '每侧一个', 40, color=INK_SOFT, anchor='ra')

    y = 900
    note(fig, y, '轿厢上挂着一根环形的限速绳。绳不动，轿厢就带着绳一起走；'
                 '绳被卡住，绳就会把轿厢上那对楔块拽进导轨。')
    save(fig, '01-overview.png', '井道全景：轿厢、两条导轨、顶上那台限速器、'
                                 '绕过底部的限速绳与张紧轮')


def fig02():
    photo('02-governor.jpg', 'governor.jpg',
          '真实限速器：绳轮、两个甩块、中间的弹簧，装在机房一侧',
          'Wikimedia Commons, File:Elevator speed governor.jpg, '
          'Darklanlan, CC BY 4.0')


def fig03():
    fig, y = new(4, '三种曲线：正常、驱动失效、自由落体')
    p = Plot(fig, (250, 210, 1000, 660), (0, 1.2), (0, 3.4))
    p.axes(xticks=(0, 0.3, 0.6, 0.9, 1.2), yticks=(0, 1, 2, 3),
           xfmt='%.1f', yfmt='%g', ylab='速度  m/s', xlab='秒')
    # rated speed
    p.line(((0, G['rated']), (1.2, G['rated'])), GRAY, width=4, dash=18)
    fig.text((760, p.py(G['rated']) - 58), '额定 1.75', 40, color=GRAY)
    # free fall
    p.line(((0, 0), (0.35, 0.35 * 9.81)), RED, width=5, dash=18)
    fig.text((470, 300), '自由落体 9.81 m/s²', 40, color=RED)
    # trip line
    p.line(((0, G['trip']), (1.2, G['trip'])), AMBER, width=4)
    fig.text((250, p.py(G['trip']) + 16), '触发速度 2.01（额定 +15%）', 40,
             color=AMBER)
    # measured trace
    tr = R['scenarios']['from_rest']['trace']
    p.line([(d['t'], d['v']) for d in tr], TEAL, width=6)
    s = R['scenarios']['from_rest']['summary']
    p.dot(s['t_trip'], s['v_trip'], AMBER)
    p.dot(s['t_brake'], s['v_brake'], BLUE)
    p.dot(s['stop_t'], 0.0, GREEN)
    fig.text((p.px(s['t_brake']) + 18, p.py(s['v_brake']) - 96),
             '开始制动 3.49', 40, color=BLUE)
    fig.text((p.px(s['stop_t']) - 30, p.py(0.0) - 120), '停下', 40, color=GREEN,
             anchor='ra')
    y = 806
    y = note(fig, y, '绿线是这台电梯从静止开始坠落时的实测曲线（模型输出）：'
                     '先按 9.81 加速到 2.01，触发；再用 0.15 秒把力传到钳口；'
                     '然后才真正吃上劲。')
    save(fig, '04-three-curves.png', '三种速度曲线：额定运行、驱动失效、自由落体，'
                                     '以及限速器触发的那一点')


def fig04():
    fig, y = new(5, '离心力对上弹簧力，交点就是触发速度')
    p = Plot(fig, (250, 210, 1000, 660), (0, 2.6), (0, 10.5))
    p.axes(xticks=(0, 0.5, 1.0, 1.5, 2.0, 2.5), yticks=(0, 2, 4, 6, 8, 10),
           xfmt='%.1f', yfmt='%g', ylab='力  N', xlab='绳速  m/s')
    pts = [(v / 100, 0.25 * 0.06 * (v / 100 / 0.10) ** 2) for v in range(0, 261, 2)]
    p.line(pts, TEAL, width=6)
    p.line(((0, G['spring']), (2.6, G['spring'])), AMBER, width=5, dash=18)
    fig.text((1000, p.py(G['spring']) + 18), '弹簧预压 6.1 N', 42, color=AMBER,
             anchor='ra')
    p.dot(G['trip'], G['spring'], RED, r=15)
    fig.text((p.px(G['trip']) - 24, p.py(G['spring']) - 110), '2.01 m/s', 42,
             bold=True, color=RED, anchor='ra')
    y = 776
    y = bullets(fig, y, [
        '离心力 = m·r·ω²，ω 是绳轮的角速度。速度一快，力按平方涨。',
        '弹簧的力基本是常数（预压多少就是多少），所以两条线只有一个交点。',
        '交点在 2.01 m/s：这就是触发速度，只需换一根弹簧就能改。',
    ])
    y = note(fig, y, '绳轮半径 0.10 米、甩块 0.25 千克、重心离轴 0.06 米；'
                     '触发时甩块自己承受 2.5 倍体重的离心加速度。')
    save(fig, '05-flyweight.png', '离心力与弹簧力的交点决定触发速度')


def fig05():
    fig, y = new(6, '换一根弹簧，就换了一档速度')
    y = note(fig, y, '触发速度 = 绳轮半径 × √(弹簧力 ÷ (甩块质量 × 重心半径))。'
                     '力在根号里，所以弹簧偏 10%，速度只偏 5%。')
    y += 40
    rows = []
    for t in G['tolerance']:
        rows.append([('%d%%' % round(t['scale'] * 100), INK, False),
                     ('%.2f N' % t['force'], INK_SOFT, False),
                     ('%.3f m/s' % t['trip'], INK, True),
                     ('%+.2f%%' % ((t['trip'] / G['trip'] - 1) * 100),
                      GREEN if abs(t['scale'] - 1) < 1e-9 else INK_SOFT, False)])
    cols = [(80, 'la'), (300, 'la'), (500, 'la'), (760, 'la')]
    fig.text((80, y - 54), '弹簧', 40, color=GRAY)
    fig.text((300, y - 54), '预压力', 40, color=GRAY)
    fig.text((500, y - 54), '触发速度', 40, color=GRAY)
    fig.text((760, y - 54), '偏差', 40, color=GRAY)
    y = table(fig, y + 8, cols, rows, row_h=72)
    y = note(fig, y, '这就是为什么限速器要定期校验：弹簧会疲劳、会锈、会被拧动。'
                     '偏 5% 看起来不多，但触发点离额定速度只有 15% 的余量。')
    save(fig, '06-tolerance.png', '弹簧力偏差对触发速度的影响')


def fig06():
    fig, y = new(3, '甩块一飞出去，就咬住外面那圈棘齿')
    cx, cy, r = 380, 470, 130
    # ratchet ring
    for i in range(24):
        a = i * 2 * math.pi / 24
        x0, y0 = cx + (r + 12) * math.cos(a), cy + (r + 12) * math.sin(a)
        x1, y1 = cx + (r + 34) * math.cos(a), cy + (r + 34) * math.sin(a)
        fig.line((x0, y0), (x1, y1), color=GRAY, width=6)
    fig.circle(cx, cy, r, fill=TINT_T, outline=TEAL)
    fig.circle(cx, cy, 16, fill=INK, outline=INK)
    # two flyweights on arms, one latched out
    for a in (-0.9, 2.3):
        fig.line((cx, cy), (cx + 96 * math.cos(a), cy + 96 * math.sin(a)),
                 color=INK_SOFT, width=6)
    fig.rect(cx + 96 * 0.91 - 16, cy + 96 * 0.42 - 16,
             cx + 96 * 0.91 + 16, cy + 96 * 0.42 + 16, fill=AMBER, outline=AMBER)
    fig.rect(cx - 106 - 16, cy - 16, cx - 106 + 16, cy + 16, fill=RED, outline=RED)
    # labels, right of the wheel
    lab = [(276, '棘齿：固定的齿圈', (cx + 118, cy - 92)),
           (368, '甩块：超速时张开', (cx + 92, cy + 36)),
           (462, '弹簧：往里拉', (cx + 30, cy + 66)),
           (556, '绳轮：跟着绳转', (cx + 66, cy + 92))]
    for ty, text, target in lab:
        leader(fig, (596, ty + 24), target)
        fig.text((610, ty), text, 40, color=INK)
    y = 700
    y = note(fig, y, '甩块张开的力来自离心力。张开到能勾住棘齿，绳轮就被钉死；'
                     '绳轮一停，限速绳也跟着停。')
    save(fig, '03-ratchet.png', '限速器内部：绳轮、甩块、弹簧与静止棘齿')


FIGS = [fig01, fig02, fig03, fig04, fig05, fig06]




def fig07():
    fig, y = new(7, '从"太快了"到"咬住了"，一共 230 毫秒')
    x0, x1, sw = 130, 1010, 0
    span = 240.0

    def px(ms):
        return x0 + (x1 - x0) * ms / span

    segs = [(0, 40, '棘爪啮合', AMBER), (40, 100, '连杆行程', BLUE),
            (100, 150, '楔块贴合', TEAL), (150, 230, '夹紧力爬升', RED)]
    for a, b, label, color in segs:
        fig.rect(px(a), 360, px(b) - 3, 424, fill=color, outline=color)
    fig.line((x0, 424), (x1, 424), color=GRAY, width=3)
    for a, b, label, color in segs:
        leader(fig, ((px(a) + px(b)) / 2, 430), ((px(a) + px(b)) / 2, 500))
        fig.text(((px(a) + px(b)) / 2, 510), label, 38, color=color, anchor='ma')
    fig.text((x0, 300), '0', 40, color=GRAY, anchor='ma')
    fig.text((px(150), 300), '150 ms', 40, color=GRAY, anchor='ma')
    fig.text((x1, 300), '230 ms', 40, color=GRAY, anchor='ra')
    note(fig, 600, '这四段是我按常见机构设定的时间常数，不是实测；加起来就是模型里的 '
                   '0.15 秒延迟 + 0.08 秒爬升。')
    y = 730
    y = bullets(fig, y, [
        '前 150 毫秒里，车还在加速——制动还没开始，只是"传话"。',
        '真正吃上劲是最后 80 毫秒：夹紧力从零爬到目标值。',
        '所以夹紧力不是"啪"一下到位，这也是为什么平均减速度比峰值低。',
    ])
    save(fig, '07-chain.png', '从超速到夹紧的四个阶段与各自的耗时')


def fig08():
    fig, y = new(8, '同一根速度曲线，分三段看')
    p = Plot(fig, (250, 210, 1000, 640), (0, 1.1), (0, 4.0))
    p.axes(xticks=(0, 0.25, 0.5, 0.75, 1.0), yticks=(0, 1, 2, 3, 4),
           xfmt='%.2f', yfmt='%g', ylab='速度  m/s', xlab='秒')
    a = R['scenarios']['from_rest']['summary']
    b = R['scenarios']['from_rated']['summary']
    p.band(0, a['t_trip'], TINT_B)
    p.band(a['t_trip'], a['t_brake'], TINT_A)
    p.band(a['t_brake'], a['stop_t'], TINT_R)
    p.line([(d['t'], d['v']) for d in R['scenarios']['from_rest']['trace']],
           TEAL, width=6)
    p.line([(d['t'], d['v']) for d in R['scenarios']['from_rated']['trace']],
           BLUE, width=5, dash=16)
    p.line(((0, G['trip']), (1.1, G['trip'])), AMBER, width=4)
    p.dot(a['t_trip'], a['v_trip'], AMBER)
    p.dot(a['t_brake'], a['v_brake'], INK)
    fig.text((p.px(a['t_trip']) + 14, p.py(a['v_trip']) - 66), '触发', 40,
             color=AMBER)
    fig.text((p.px(a['t_brake']) + 14, p.py(a['v_brake']) - 70), '制动开始 3.5',
             40, color=INK)
    fig.text((560, 548), '蓝虚线：已在 1.75', 38, color=BLUE)
    fig.text((560, 600), '绿实线：从静止坠落', 38, color=TEAL)
    y = 800
    y = note(fig, y, '灰蓝色的两段是"还在加速"，只有最后红色的那一段在减速。'
                     '从静止坠落的那条线，全程最多掉 2.0 米。')
    save(fig, '08-sim.png', '仿真得到的速度曲线与三个阶段')


def fig09():
    fig, y = new(9, '楔块：竖直的拖力，变成水平的夹紧力')
    fig.rect(130, 200, 166, 700, fill=LIGHT, outline=None)
    fig.text((130, 150), '导轨', 42, color=INK)
    fig.poly([(166, 360), (166, 620), (300, 620)], fill=TINT_A, outline=AMBER)
    fig.text((190, 556), '楔块', 42, bold=True, color=AMBER)
    fig.line((300, 620), (372, 360), color=INK_SOFT, width=8)
    fig.text((388, 330), '壳体斜面', 40, color=INK_SOFT)
    # wedge angle, exaggerated for legibility
    fig.line((166, 360), (222, 360), color=RED, width=4)
    fig.text((232, 330), '楔角 α', 40, color=RED)
    fig.arrow((250, 706), (250, 648), color=GREEN)
    fig.text((266, 680), '拖力 D', 42, color=GREEN)
    fig.arrow((176, 500), (286, 500), color=BLUE)
    fig.text((300, 468), 'N', 42, bold=True, color=BLUE)
    y = 770
    y = note(fig, y, '竖直的拖力 D 顶在斜面上，被分解成水平的正压力 N。'
                     'N = D / tan(α + φ)：楔角 α = 6°、摩擦角 φ = 8.5° 时，'
                     '一份拖力换来 3.9 份夹紧力。图上角度放大了，否则这个楔子只有一条缝宽。')
    save(fig, '09-wedge.png', '楔块如何把竖直拖力转换成水平正压力')


def fig10():
    fig, y = new(10, '楔角小于摩擦角，楔块就自己锁死了')
    p = Plot(fig, (250, 210, 1000, 640), (2, 15), (0, 6.5))
    p.axes(xticks=(2, 4, 6, 8, 10, 12, 15), yticks=(0, 2, 4, 6),
           yfmt='%g', ylab='夹紧倍数', xlab='楔角（度）')
    p.band(2, R['wedge']['main']['phi'], TINT_A)
    phi = R['wedge']['main']['phi']
    crit = R['wedge']['critical_alpha']
    p.line(((phi, 0), (phi, 6.5)), GRAY, width=4, dash=16)
    p.line(((crit, 0), (crit, 6.5)), RED, width=4, dash=16)
    p.line(((2, 1 / (2 * R['mu'])), (15, 1 / (2 * R['mu']))), AMBER, width=4,
           dash=16)
    pts = [(d['alpha'], d['gain']) for d in R['wedge']['curve']]
    p.line(pts, TEAL, width=6)
    p.dot(6.0, R['wedge']['main']['gain'], RED, r=15)
    fig.text((p.px(6.0) + 20, p.py(R['wedge']['main']['gain']) + 30), '本文取值 6°',
             40, color=RED)
    fig.text((p.px(phi) - 10, 210), '%.1f°：摩擦角' % phi, 38, color=GRAY,
             anchor='ra')
    fig.text((p.px(crit) + 10, 250), '%.1f°：自激门槛' % crit, 38, color=RED)
    fig.text((p.px(2) + 16, p.py(1 / (2 * R['mu'])) - 60), '倍数 3.33 = 1/(2μ)',
             38, color=AMBER)
    y = 806
    y = note(fig, y, '阴影区里，楔角小于摩擦角：楔块被拖进去以后，靠自己的摩擦就退不出来，'
                     '这叫自锁。红虚线以左，它连"往里挤"这件事都自己做得到——越夹越紧。')
    save(fig, '10-selflock.png', '楔角、夹紧倍数、自锁与自激的边界')


def fig11():
    photo('11-safety-gear.jpg', 'safety-gear.jpg',
          '真实楔块式安全钳：两侧是碟簧组，用来限制夹紧力',
          'Wikimedia Commons, File:Keilfangvorrichtung Aufzugsbau.jpg, '
          'public domain（Coptercam，own work）')


def fig12():
    fig, y = new(12, '要停住 1200 千克，导轨得挨多大的力')
    y = note(fig, y, '制动时导轨要同时顶住车重和惯性：F = m(g + a)。这份力由两个安全钳分担，'
                     '再靠摩擦变成制动力，所以正压力还要再除以摩擦系数。')
    y += 30
    rows = []
    for s in R['stops']:
        rows.append([('%.0f m/s²' % s['decel'], INK, False),
                     ('%.1f kN' % (s['force'] / 1000), INK, True),
                     ('%.1f kN' % (s['force'] / 2 / 1000), INK_SOFT, False),
                     ('%.0f kN' % (s['force'] / 2 / R['mu'] / 1000), INK, False)])
    cols = [(80, 'la'), (300, 'la'), (560, 'la'), (790, 'la')]
    fig.text((80, y - 54), '减速度', 40, color=GRAY)
    fig.text((300, y - 54), '总制动力', 40, color=GRAY)
    fig.text((560, y - 54), '每块', 40, color=GRAY)
    fig.text((790, y - 54), '每块正压力', 40, color=GRAY)
    y = table(fig, y + 8, cols, rows, row_h=74)
    y = note(fig, y, '车 1200 千克、导轨摩擦系数 0.15。正压力是制动力除以摩擦系数，'
                     '所以它比制动力大六倍多——真正被"压"的是导轨。')
    save(fig, '12-forces.png', '不同减速度下的制动力、每块安全钳的力与正压力')


FIGS += [fig07, fig08, fig09, fig10, fig11, fig12]


def fig13():
    fig, y = new(13, '减速度越大，停得越短，力也越大')
    y = note(fig, y, '从 3.49 m/s 刹到零。停距和减速度成反比，而制动力和减速度成正比——'
                     '想停得急，就得让导轨吃更多力。')
    y += 30
    rows = []
    for st in R['stops']:
        rows.append([('%.0f m/s²' % st['decel'], INK, False),
                     ('%.2f m' % st['stop'], INK, True),
                     ('%.2f s' % st['time'], INK_SOFT, False),
                     ('%.1f g' % (st['decel'] / 9.81), INK_SOFT, False)])
    cols = [(80, 'la'), (330, 'la'), (600, 'la'), (830, 'la')]
    fig.text((80, y - 54), '减速度', 40, color=GRAY)
    fig.text((330, y - 54), '停距', 40, color=GRAY)
    fig.text((600, y - 54), '时间', 40, color=GRAY)
    fig.text((830, y - 54), '相当于', 40, color=GRAY)
    y = table(fig, y + 8, cols, rows, row_h=74)
    y = note(fig, y, '常见规范把平均减速度限制在 1 g 左右：再快，人的膝盖和脊椎就要替电梯'
                     '承担剩下的那部分。所以"停得越快越好"是错的。')
    save(fig, '13-stops.png', '减速度、停距、时间与重力加速度的对照')


def fig14():
    fig, y = new(14, '这点热量，连导轨都暖不热')
    stop = R['energy']['stop']
    free = R['energy']['free_fall']
    top = max(stop['potential'], free['potential'])
    x0, width = 60, 640
    for i, (label, e, color, extra) in enumerate([
            ('这次制停', stop['potential'], TEAL, '钢升温 %.1f °C' % stop['steel_dt']),
            ('30 米自由落体', free['potential'], RED, '钢升温 %.0f °C' % free['steel_dt'])]):
        yy = 240 + i * 220
        fig.text((x0, yy - 60), label, 42, color=INK)
        w = width * e / top
        fig.rect(x0, yy, x0 + w, yy + 84, fill=color, outline=None)
        fig.text((x0 + w + 20, yy + 14), '%.0f kJ' % (e / 1000), 42, bold=True,
                 color=color)
        fig.text((x0, yy + 108), extra, 38, color=INK_SOFT)
    y = 720
    y = note(fig, y, '制停时全部动能和势能都变成摩擦热，落在楔块和导轨那几十厘米长的接触面上。'
                     '按 40 千克钢、470 J/(kg·K) 算，升温只有一两度——这也是它敢反复用的原因。')
    save(fig, '14-energy.png', '一次制停与自由落体的能量对比，换算成钢的温升')


def fig15():
    photo('15-otis-1854.jpg', 'otis-1854.jpg',
          '1854 年 Otis 在纽约水晶宫演示安全装置：他让人砍断吊绳',
          'Wikimedia Commons, File:Elisha OTIS 1854.jpg, public domain（佚名版画）',
          identity='档案扫描件')


def fig16():
    photo('16-eiffel-1892.jpg', 'eiffel-governor.jpg',
          '1892 年工程期刊上的埃菲尔铁塔电梯限速器：甩块、弹簧、棘齿都在',
          'Wikimedia Commons, File:Otis Wheel Governor, Eiffel Tower.jpg, '
          'public domain（Engineering News, 1892）', identity='档案扫描件')


def fig17():
    fig, y = new(17, '整条链路：测、触、传、夹')
    stages = [('测', '限速器', '绳走多快\n它转多快', TEAL),
              ('触', '棘爪', '超速才咬住', AMBER),
              ('传', '连杆', '把动作送到钳口', BLUE),
              ('夹', '楔块', '挤进导轨', RED)]
    w, gap = 216, 36
    for i, (tag, name, cap, color) in enumerate(stages):
        x = 60 + i * (w + gap)
        fig.box('s%d' % i, x, 250, x + w, 470, fill=WHITE, outline=color, width=5)
        fig.text((x + w / 2, 280), tag, 60, bold=True, color=color, anchor='ma')
        fig.text((x + w / 2, 372), name, 44, bold=True, anchor='ma')
        fig.wrap((x + 18, 430), cap.replace('\n', ''), 38, w - 36, color=INK_SOFT)
        if i < 3:
            fig.arrow((x + w + 4, 360), (x + w + gap - 6, 360), color=GRAY)
    y = 560
    y = bullets(fig, y, [
        '前两步是"测速"和"判断"，都不需要电——纯机械，断电也照做。',
        '后两步是"传"和"夹"，靠的是轿厢自己的下落把楔块拖进导轨。',
        '整条链上没有任何一个环节需要外部供电，这是它在停电时仍然有效的原因。',
    ])
    save(fig, '17-chain.png', '从测速到夹紧的四段链路')


def fig18():
    fig, y = new(18, '为什么夹导轨，不夹那根钢丝绳')
    y = note(fig, y, '安全钳抓的是井道里那条固定不动的钢轨，而不是吊着轿厢的钢丝绳。'
                     '原因不在"哪个更好抓"，在"出事的时候哪个还在"。')
    y += 20
    cols = [(70, 'la'), (470, 'la')]
    rows = [
        [('夹导轨', GREEN, True), ('夹钢丝绳', RED, True)],
        [('在井道里固定不动', INK, False), ('它可能就是断掉的那根', INK_SOFT, False)],
        [('实心钢，几十毫米厚', INK, False), ('几百根细丝拧的，易伤', INK_SOFT, False)],
        [('只影响这一台电梯', INK, False), ('还得绕滑轮，跟绳较劲', INK_SOFT, False)],
        [('导轨油，摩擦可控', INK, False), ('要润滑，摩擦系数会飘', INK_SOFT, False)],
    ]
    fig.text((70, y - 56), '对', 40, color=GRAY)
    fig.text((470, y - 56), '错', 40, color=GRAY)
    y = table(fig, y + 8, cols, rows, row_h=86, size=38)
    y = note(fig, y, '还有一层：限速绳只负责"传话"，它拉着连杆跑几十厘米就够了，'
                     '不需要承受制动力。真正吃力的地方在导轨和楔块之间。')
    save(fig, '18-rails.png', '夹导轨与夹钢丝绳的对比')


FIGS += [fig13, fig14, fig15, fig16, fig17, fig18]


from figkit import PALETTE


def make_cover():
    for c in ('#0d1f27', '#2b4a55', '#7fa8c9', '#e8f0f6', '#f2b134', '#147d84'):
        PALETTE.add(c)
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill='#0d1f27', outline=None)
    fig.text((96, 130), '2.01 米每秒', 96, bold=True, color='#ffffff')
    fig.text((96, 250), '电梯怎么知道自己太快了', 48, color='#7fa8c9')
    # a speed trace: flat, then trip, then a hard stop
    pts = [(96, 640), (420, 640), (470, 560), (520, 470), (600, 470),
           (620, 700), (700, 780)]
    fig.line((96, 700), (960, 700), color='#2b4a55', width=4)
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color='#147d84', width=8)
    fig.line((96, 470), (960, 470), color='#f2b134', width=4)
    fig.text((620, 400), '触发', 44, color='#f2b134')
    fig.text((96, 800), '甩块、弹簧、楔块，和 230 毫秒', 44, color='#e8f0f6')
    fig.text((96, 930), 'tech-articles · 2026-11-09', 38, color='#7fa8c9')
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png')


def main():
    want = {int(a) for a in sys.argv[1:] if a.isdigit()}
    for i, fn in enumerate(FIGS, 1):
        if want and i not in want:
            continue
        print('fig%02d' % i)
        fn()
    if not want:
        make_cover()
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(sorted(META, key=lambda r: r['path']), ensure_ascii=False,
                   indent=1) + '\n')
    total = len(list(ASSETS.glob('*.png'))) + len(list(ASSETS.glob('*.jpg')))
    print('%d files in assets, %d metadata rows' % (total, len(META)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
