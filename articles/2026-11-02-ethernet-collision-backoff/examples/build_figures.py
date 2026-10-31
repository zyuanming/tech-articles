#!/usr/bin/env python3
"""Original teaching figures for the Ethernet article. MIT.

Every curve here reads from results.json, which run_model.py wrote by running
examples/net.py. No number is typed into the drawing code.
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

    def line(self, pts, color, width=5, dash=None):
        pixels = [(self.px(x), self.py(y)) for x, y in pts]
        for a, b in zip(pixels, pixels[1:]):
            self.f.line(a, b, color=color, width=width, dash=dash)

    def dot(self, x, y, color, r=13):
        self.f.circle(self.px(x), self.py(y), r, fill=color, outline=color)

    def bar(self, x, value, width_px, color, label=None):
        cx = self.px(x)
        self.f.rect(cx - width_px / 2, self.py(value), cx + width_px / 2,
                    self.py(0), fill=color, outline=None)
        if label:
            self.f.text((cx, self.py(value) - 52), label, 40, color=color,
                        anchor='ma', bold=True, allow_overlap=True)

    def hline(self, y, color=GRAY, dash=14):
        self.f.line((self.x0, self.py(y)), (self.x1, self.py(y)), color=color,
                    width=3, dash=dash)


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


# ---------------------------------------------------------------- figures

def fig01():
    f, y = new(1, '所有人共用一根线',
               '1973 年的以太网就是一根同轴电缆，从这头通到那头，'
               '中间挂着一串机器。谁说话，所有人都听得见。')
    top = y + 40
    f.line((110, top + 120), (952, top + 120), color=INK, width=10)
    f.rect(72, top + 88, 110, top + 152, fill=AMBER, outline=AMBER)
    f.text((91, top + 190), '终结器', 40, color=AMBER, anchor='ma')
    f.rect(952, top + 88, 990, top + 152, fill=AMBER, outline=AMBER)
    f.text((971, top + 190), '终结器', 40, color=AMBER, anchor='ma')
    for i, name in enumerate(['A', 'B', 'C', 'D']):
        x = 220 + i * 210
        f.line((x, top + 120), (x, top + 210), color=INK, width=5)
        f.circle(x, top + 122, 12, fill=INK, outline=INK)
        f.box(name, x - 74, top + 210, x + 74, top + 366, fill=WHITE)
        f.text((x, top + 244), name, 42, bold=True, inside=name, anchor='ma')
        f.text((x, top + 306), '机器', 40, color=INK_SOFT, inside=name,
               anchor='ma')
    y = top + 430
    y = note(f, y, '电缆是共享的：A 发出的电信号沿着铜线往两边跑，'
                   'B、C、D 都会收到。这就是「广播信道」。')
    y = note(f, y, '共享带来一个直接后果：如果 A 和 C 同时开口，'
                   '两根信号会在线上叠在一起，谁都听不清。')
    save(f, '01-one-wire.png', '共享总线：一根电缆串起所有机器')


def fig04():
    f, y = new(4, '同时开口，两个帧一起报废',
               '把时间横着画出来：A 从 0.2 开始说，C 在 0.9 开口，'
               '两段话重叠的地方就是冲突。')
    top = y + 40
    x0, x1 = 300, 990
    scale = (x1 - x0) / 2.4

    def tx(t):
        return x0 + t * scale

    spans = [('A', 0.2, 1.2, TINT_B), ('C', 0.9, 1.9, TINT_A)]
    for name, start, end, fill in spans:
        lane = top if name == 'A' else top + 150
        f.text((70, lane + 40), name, 42, bold=True)
        f.line((x0, lane + 60), (x1, lane + 60), color=LIGHT, width=3)
        f.rect(tx(start), lane + 10, tx(end), lane + 110,
               fill=fill, outline=None)
        f.text(((tx(start) + tx(end)) / 2, lane + 24), '一个帧', 40, color=INK,
               anchor='ma', allow_overlap=True)
        f.text((tx(start), lane - 34), '%g' % start, 40, color=GRAY)
        f.text((tx(end), lane - 34), '%g' % end, 40, color=GRAY, anchor='ma')
    f.rect(tx(0.9), top + 10, tx(1.2), top + 260, fill=TINT_R, outline=None)
    f.text((tx(1.05), top + 118), '重叠', 40, color=RED, anchor='ma', bold=True,
           allow_overlap=True)
    f.text((tx(1.05), top + 170), '0.3', 40, color=RED, anchor='ma', bold=True,
           allow_overlap=True)
    y = top + 330
    y = note(f, y, '两个帧重叠，两个都失败，谁也没传成。'
                   'ALOHA 的规则是「想发就发」，所以这种重叠是常态。')
    save(f, '04-collision.png', '两个帧在共享信道上重叠')


def fig05():
    f, y = new(5, '要撞上，邻居得离得多近',
               '问一个更精确的问题：一个帧要成功，前后各要留多宽的空白？')
    top = y + 40
    x0, w = 190, 260
    f.rect(x0 + w, top + 130, x0 + 2 * w, top + 250, fill=TINT_B, outline=BLUE,
           width=3)
    f.text((int(x0 + 1.5 * w), top + 160), '我的帧', 42, bold=True, color=INK,
           anchor='ma', allow_overlap=True)
    f.text((int(x0 + 1.5 * w), top + 214), '长 1 格', 40, color=INK_SOFT,
           anchor='ma', allow_overlap=True)
    f.rect(x0, top + 130, x0 + 3 * w, top + 250, fill=None, outline=RED, width=4)
    f.text((x0, top + 74), '危险区：前后各一格，共 2 格', 40, color=RED)
    f.text((x0 - 24, top + 172), '早 1 格', 40, color=INK_SOFT, anchor='ra')
    f.text((x0, top + 282), '别人在这 2 格里的任何时刻开口，都会撞上', 40,
           color=INK_SOFT)
    y = top + 360
    y = note(f, y, '一个帧占 1 格，可它会被「前一格开始的帧」和「后一格开始的帧」'
                   '各撞一次，所以脆弱窗口是 2 格，不是 1 格。')
    save(f, '05-vulnerable-window.png', '纯 ALOHA 的两帧脆弱窗口')


def fig06():
    f, y = new(6, '纯 ALOHA 最好也只能到 18.4%',
               '横轴是想发的总量，纵轴是真正传成的比例。'
               '点是从模拟里数出来的，线是 G·e^(-2G)。')
    top = y + 20
    p = Plot(f, (240, top + 40, 990, top + 480), (0, 1.9), (0, 0.26))
    p.axes(xticks=(0, 0.5, 1.0, 1.5), yticks=(0, 0.1, 0.2),
           xfmt='%g', yfmt='%g', ylab='成功率', xlab='想发的量 / 信道容量')
    pts = [(r['g'], r['theory']) for r in R['aloha']]
    p.line(pts, color=TEAL, width=5)
    for r in R['aloha']:
        p.dot(r['g'], r['measured'], color=TEAL, r=11)
    p.hline(R['ceiling']['aloha'], color=AMBER)
    f.text((p.px(0.06), p.py(R['ceiling']['aloha']) - 56),
           '天花板 18.4%', 40, color=AMBER, bold=True)
    y = top + 610
    y = note(f, y, '最优点在「想发的量 = 容量的一半」附近：发得再少是浪费，'
                   '发得再多就是互相撞。18.4% 这个数等于 1/(2e)。')
    save(f, '06-aloha-ceiling.png', '纯 ALOHA 吞吐曲线（实测点与理论线）')


def fig07():
    f, y = new(7, '把时间切成槽，窗口砍一半',
               '如果所有人只在整点开口，就不会有「半个帧叠上去」这种浪费。')
    top = y + 40
    x0, w = 200, 210
    for i in range(5):
        f.line((x0 + i * w, top + 100), (x0 + i * w, top + 320), color=GRAY,
               width=2, dash=10)
    f.text((x0, top + 340), '虚线是槽边界', 40, color=GRAY)
    f.rect(x0 + w, top + 130, x0 + 2 * w, top + 250, fill=TINT_B, outline=BLUE,
           width=3)
    f.text((x0 + int(1.5 * w), top + 160), '我的帧', 42, bold=True, color=INK,
           anchor='ma', allow_overlap=True)
    f.text((x0 + int(1.5 * w), top + 214), '整格', 40, color=INK_SOFT,
           anchor='ma', allow_overlap=True)
    f.rect(x0, top + 130, x0 + 3 * w, top + 250, fill=None, outline=RED, width=4)
    f.text((x0, top + 70), '危险区：前后各半格，共 1 格', 40, color=RED)
    y = top + 400
    y = note(f, y, '脆弱窗口从 2 格缩到 1 格，天花板就从 1/(2e) 涨到 1/e：'
                   '18.4% 变成 36.8%。只是加了一条「对齐」的规矩，翻了一倍。')
    save(f, '07-slotted.png', '分槽 ALOHA 把脆弱窗口缩到 1 格')


def fig08():
    f, y = new(8, '对齐一条边界，效率翻倍',
               '两条曲线同一个横轴。青色是纯 ALOHA，蓝色是分槽 ALOHA，'
               '点仍是模拟实测。')
    top = y + 20
    p = Plot(f, (240, top + 40, 990, top + 470), (0, 1.9), (0, 0.42))
    p.axes(xticks=(0, 0.5, 1.0, 1.5), yticks=(0, 0.2, 0.4),
           ylab='成功率', xlab='想发的量 / 信道容量')
    p.line([(r['g'], r['theory']) for r in R['slotted']], color=BLUE, width=5)
    for r in R['slotted']:
        p.dot(r['g'], r['measured'], color=BLUE, r=11)
    p.line([(r['g'], r['theory']) for r in R['aloha']], color=TEAL, width=5)
    for r in R['aloha']:
        p.dot(r['g'], r['measured'], color=TEAL, r=11)
    f.text((p.px(1.05), p.py(0.39)), '分槽 36.8%', 40, color=BLUE, bold=True)
    f.text((p.px(0.62), p.py(0.235)), '纯 ALOHA 18.4%', 40, color=TEAL, bold=True)
    y = top + 610
    y = note(f, y, '这两个数字不是估计，是从模拟里数出来的：'
                   '分槽那条线在「想发的量 = 容量」时正好是 1/e。')
    save(f, '08-two-curves.png', '纯 ALOHA 与分槽 ALOHA 的实测对照')


def fig09():
    f, y = new(9, '先听，再开口',
               'ALOHA 的问题是它不看信道。加一条规矩：'
               '开口之前先听一下，有人正在说就等。')
    top = y + 20
    x0, scale = 300, 300
    for i, (name, start, end, color) in enumerate(
            [('A 先说', 0.0, 1.0, TINT_B), ('B 想发', 0.3, 2.0, TINT_A)]):
        lane = top + 40 + i * 170
        f.text((60, lane + 40), name, 42, bold=True)
        f.line((x0, lane + 60), (x0 + 5 * scale, lane + 60), color=LIGHT, width=3)
        f.rect(x0 + start * scale, lane + 10, x0 + end * scale, lane + 110,
               fill=color, outline=None)
        f.text((x0 + (start + end) / 2 * scale, lane + 24), '占用信道', 40,
               color=INK, anchor='ma', allow_overlap=True)
        if i == 1:
            f.line((x0 + 0.3 * scale, lane + 130), (x0 + 1.0 * scale, lane + 130),
                   color=RED, width=4)
            f.text((x0 + 0.65 * scale, lane + 140), '听见忙，等着', 40,
                   color=RED, anchor='ma')
    y = top + 420
    y = note(f, y, 'B 听到线上有人，就把自己的帧压住，等 A 说完再发。'
                   '这一步不需要任何协调——听就行了。')
    y = note(f, y, '代价是：B 在等的这段时间里，信道对 B 是「浪费」的。'
                   '低负载时这不算什么，高负载时所有人都想发，听也只能听出「忙」。')
    save(f, '09-listen-first.png', '载波侦听：先听再说')


def fig10():
    f, y = new(10, '撞了之后，各自等一个随机数',
               '冲突已经发生，两边都得重发。如果都立刻重发，就会再撞一次，'
               '永远撞下去。')
    top = y + 20
    x0, scale = 250, 220
    lanes = [('A', top + 30), ('B', top + 150)]
    for name, lane in lanes:
        f.text((70, lane + 40), name, 42, bold=True)
        f.line((x0, lane + 60), (x0 + 4.2 * scale, lane + 60), color=LIGHT, width=3)
    f.rect(x0, top + 40, x0 + scale, top + 140, fill=TINT_R, outline=None)
    f.rect(x0, top + 160, x0 + scale, top + 260, fill=TINT_R, outline=None)
    f.text((x0 + scale / 2, top + 76), '撞了', 42, color=RED, bold=True,
           anchor='ma', allow_overlap=True)
    f.text((x0 + scale / 2, top + 196), '撞了', 42, color=RED, bold=True,
           anchor='ma', allow_overlap=True)
    for name, lane, wait, label in (('A', top + 30, 1.6, '抽到 3 格'),
                                    ('B', top + 150, 2.4, '抽到 7 格')):
        f.line((x0 + wait * scale, lane + 130), (x0 + wait * scale, lane + 60),
               color=GRAY, width=3, dash=10)
        f.text((x0 + wait * scale, lane + 140), label, 40, color=GRAY, anchor='ma')
    f.rect(x0 + 1.6 * scale, top + 40, x0 + 2.6 * scale, top + 140,
           fill=TINT_G, outline=None)
    f.text((x0 + 2.1 * scale, top + 76), '重发成功', 40, color=GREEN,
           anchor='ma', allow_overlap=True)
    f.rect(x0 + 2.6 * scale, top + 160, x0 + 3.6 * scale, top + 260,
           fill=TINT_G, outline=None)
    f.text((x0 + 3.1 * scale, top + 196), '重发成功', 40, color=GREEN,
           anchor='ma', allow_overlap=True)
    y = top + 340
    y = note(f, y, '两个人从各自的窗口里抽一个格数，抽到最小的先发，'
                   '另一个再等下一轮。抽签把「同时」变成了「先后」。')
    save(f, '10-backoff-draw.png', '冲突后各自抽一个随机等待格数')


def fig11():
    f, y = new(11, '窗口一次翻一倍',
               '第 k 次冲突之后，从 0 到 2^k - 1 里抽。人越多，窗口越大。')
    top = y + 20
    cols = [(60, 'la'), (400, 'la'), (700, 'la')]
    rows = [[('冲突次数 k', GRAY, True), ('窗口（格）', GRAY, True),
             ('最大等待', GRAY, True)]]
    for r in R['windows']:
        rows.append([('%d' % r['k'], INK, False),
                     ('%d' % r['window'], TEAL, False),
                     ('%g ms' % r['worst_ms'], INK_SOFT, False)])
    y = table(f, top, cols, rows, size=40, row_h=62)
    y = note(f, y, '一格是 51.2 微秒（10 Mbit/s 的时隙）。'
                   'k 到 10 就不再涨了，最大等待 52 毫秒——'
                   '这个上限是为了让最坏情况有界。')
    save(f, '11-window-table.png', '二进制指数退避的窗口大小')


def fig12():
    f, y = new(12, '人数翻倍，只多撞一次',
               '让 n 台机器同时抢线，数它们平均要撞几次才有人赢。'
               '每一次都是独立的模拟。')
    top = y + 20
    p = Plot(f, (240, top + 40, 990, top + 470), (0, 70), (0, 7))
    p.axes(xticks=(0, 16, 32, 48, 64), yticks=(0, 2, 4, 6),
           ylab='平均冲突次数', xlab='同时想发的机器数')
    pts = [(r['stations'], r['mean']) for r in R['backoff']]
    p.line(pts, color=TEAL, width=5)
    for r in R['backoff']:
        p.dot(r['stations'], r['mean'], color=TEAL, r=11)
    f.text((p.px(2), p.py(1.1)), '每翻一倍，多撞约 1 次', 40, color=TEAL,
           bold=True)
    y = top + 610
    y = note(f, y, '曲线长得像对数：2 → 4 → 8 → … → 64，'
                   '每翻一倍大约多撞一次。这就是「指数」窗口在做的事——'
                   '把冲突的代价压成对数，而不是让它跟着人数线性上涨。')
    save(f, '12-backoff-growth.png', '指数退避：冲突次数随人数对数增长')


def fig13():
    f, y = new(13, '窗口写死，就会撞死',
               '同一份模拟，把窗口固定住：要么永远 2 格，'
               '要么永远等于人数。')
    top = y + 20
    p = Plot(f, (240, top + 40, 990, top + 460), (0, 70), (0, 13))
    p.axes(xticks=(0, 16, 32, 48, 64), yticks=(0, 4, 8, 12),
           ylab='平均冲突次数', xlab='机器数')
    fixed2 = [(c['stations'], c['mean']) for c in R['controls'] if c['kind'] == 'fixed2']
    fixedn = [(c['stations'], c['mean']) for c in R['controls'] if c['kind'] == 'fixedn']
    binary = [(r['stations'], r['mean']) for r in R['backoff']]
    p.line(fixed2, color=RED, width=5)
    for c in R['controls']:
        if c['kind'] == 'fixed2':
            p.dot(c['stations'], c['mean'], color=RED, r=11)
    p.line(fixedn, color=BLUE, width=5, dash=14)
    p.line(binary, color=TEAL, width=5)
    f.text((p.px(4), p.py(11.4)), '窗口固定 2 格：撞不到头', 40, color=RED,
           bold=True)
    f.text((p.px(20), p.py(1.5)), '窗口 = 人数：几乎不撞', 40, color=BLUE)
    f.text((p.px(38), p.py(6.4)), '指数窗口', 40, color=TEAL)
    y = top + 590
    y = note(f, y, '固定 2 格时，8 台机器就撞满了我给的 12 次上限——'
                   '再往上没有意义，它是发散的。')
    y = note(f, y, '而「窗口 = 人数」看起来更好，代价是你得先知道人数，'
                   '并且所有人都得同意这个数。真实的网络里，机器会随时上下线。', color=BLUE)
    save(f, '13-fixed-window.png', '固定窗口与指数窗口的对照')


def fig14():
    f, y = new(14, '两个杠杆：撞得少，撞得便宜',
               '同样 32 台机器、同样平均 4.9 次冲突。'
               '区别只在一次冲突浪费多少时间。')
    top = y + 40
    for i, row in enumerate(R['levers']):
        lane = top + i * 210
        f.text((70, lane + 60), row['name'], 42, bold=True)
        f.rect(70, lane + 100, 70 + int(900 * row['efficiency']), lane + 190,
               fill=TEAL if i == 0 else GREEN, outline=None)
        f.text((84 + int(900 * row['efficiency']), lane + 118),
               '%.1f%%' % (100 * row['efficiency']), 42, bold=True,
               color=TEAL if i == 0 else GREEN)
        f.text((70, lane + 202), '一次冲突浪费 %g 个帧时间' % row['cost'], 40,
               color=INK_SOFT)
    y = top + 500
    y = note(f, y, 'ALOHA：撞了等于两个帧全废，代价 1.0。'
                   'CSMA/CD：撞了马上闭嘴，只浪费来回传播那一点点，代价 0.05。')
    y = note(f, y, '17% 和 80% 的差别不来自「更聪明」，'
                   '来自把一个昂贵的失败换成了一个便宜的失败。', color=GREEN)
    save(f, '14-two-levers.png', '有效吞吐：更少的碰撞与更便宜的碰撞')


def fig15():
    f, y = new(15, '为什么最小帧是 64 字节',
               '要能「边说边听」，帧就必须还在发送时，'
               '对方的碰撞信号已经传回自己耳朵里。')
    top = y + 20
    f.line((120, top + 120), (940, top + 120), color=INK, width=8)
    f.circle(120, top + 120, 16, fill=BLUE, outline=BLUE)
    f.circle(940, top + 120, 16, fill=AMBER, outline=AMBER)
    f.text((120, top + 160), 'A 发', 40, color=BLUE, anchor='ma')
    f.text((940, top + 160), 'B 也发', 40, color=AMBER, anchor='ma')
    f.text((530, top + 60), '最远 2500 米，来回 25 微秒', 40, color=INK_SOFT,
           anchor='ma')
    y = top + 240
    rows = [[('10 Mbit/s', INK, False), ('51.2 µs', TEAL, False),
             ('64 字节', TEAL, True)]]
    y = table(f, y, [(60, 'la'), (330, 'la'), (700, 'la')],
              [[('速率', GRAY, True), ('512 bit 的时隙', GRAY, True),
                ('最小帧长', GRAY, True)]] + rows, size=40, row_h=70)
    y = note(f, y, '512 bit 的时隙是被「最远距离 + 四个中继器 + 收发器延迟」'
                   '定出来的，规格书把它取成 512 bit 整。'
                   '于是最小帧 = 512 bit = 64 字节。')
    save(f, '15-min-frame.png', '64 字节最小帧的来历')


def fig16():
    f, y = new(16, '速度乘十，网线就得缩短十倍',
               '时隙固定是 512 bit，速率越高，这段时间越短。'
               '电信号的传播速度却不会变。')
    top = y + 20
    cols = [(60, 'la'), (330, 'la'), (620, 'la')]
    rows = [[('速率', GRAY, True), ('时隙', GRAY, True),
             ('半双工时的最远距离', GRAY, True)]]
    for r in R['speeds']:
        label = ('%g Gbit/s' % (r['mbps'] / 1000) if r['mbps'] >= 1000
                 else '%g Mbit/s' % r['mbps'])
        rows.append([(label, INK, False),
                     ('%g µs' % r['slot_us'], TEAL, False),
                     ('%g 米' % r['span_m'], INK_SOFT, False)])
    y = table(f, y, cols, rows, size=40, row_h=66)
    y = note(f, y, '每提升十倍速率，半双工能拉的距离就缩到十分之一。'
                   '这是「64 字节帧 + 撞了要能听见」的算术上限，'
                   '不是网线的物理极限。')
    y = note(f, y, '标准没有接受这个结果：百兆改成全双工（不再碰撞检测），'
                   '距离由信号质量决定，是 100 米；千兆在半双工时'
                   '把时隙接长到 512 字节（载波扩展），到全双工再取消。', color=BLUE)
    save(f, '16-speed-vs-reach.png', '速率、时隙与合法网段长度')


def fig17():
    f, y = new(17, '一帧长什么样',
               '以太网的帧头只有 14 字节，加上 4 字节校验。'
               '下面是各字段，宽度按大致比例画。')
    top = y + 40
    fields = [('前导码', '7 B', 80, GRAY), ('SFD', '1 B', 70, GRAY),
              ('目的地址', '6 B', 150, BLUE), ('源地址', '6 B', 150, TEAL),
              ('类型', '2 B', 90, AMBER), ('载荷', '46–1500 B', 320, GREEN),
              ('FCS', '4 B', 90, RED)]
    x = 50
    for name, size, span, color in fields:
        f.rect(x, top, x + span, top + 120, fill=WHITE, outline=color, width=3)
        f.text((x + span // 2, top + 18), name, 40, color=color, anchor='ma',
               allow_overlap=True)
        f.text((x + span // 2, top + 70), size, 40, color=INK_SOFT, anchor='ma',
               allow_overlap=True)
        x += span
    y = top + 170
    y = note(f, y, '前 8 字节让收方的时钟对齐，接着 6 字节是收件人、6 字节是发件人、'
                   '2 字节说明载荷是什么类型，最后 4 字节是 CRC 校验。')
    y = note(f, y, '这套字段在今天的交换机里几乎原封不动，'
                   '只是速率从 2.94 Mbit/s 涨到了一万倍。')
    save(f, '17-frame-format.png', '以太网帧的字段与字节数')


def fig18():
    f, y = new(18, '发小包不划算',
               '帧头一共 22 字节（含前导码与校验），'
               '载荷越小，这部分开销占比越高。')
    top = y + 20
    cols = [(60, 'la'), (360, 'la'), (700, 'la')]
    rows = [[('载荷', GRAY, True), ('整帧', GRAY, True), ('载荷占比', GRAY, True)]]
    for r in R['overhead']:
        rows.append([('%d B' % r['payload'], INK, False),
                     ('%d B' % r['frame'], TEAL, False),
                     ('%.1f%%' % (100 * r['efficiency']), INK_SOFT, False)])
    y = table(f, y, cols, rows, size=40, row_h=60)
    y = note(f, y, '一条 18 字节的确认包，真正的信息只占四分之一。'
                   '这也是为什么高负载网络里，小包比例的上升会让有效带宽掉得比想象中快。')
    save(f, '18-small-packets.png', '帧头开销与载荷大小')


def fig20():
    f, y = new(20, '从一根线，到一个星',
               '交换机的出现让「共享」这个词失效了：'
               '每个端口是一个独立的碰撞域。')
    top = y + 30
    f.line((90, top + 60), (470, top + 60), color=INK, width=8)
    for i in range(3):
        x = 150 + i * 140
        f.line((x, top + 60), (x, top + 110), color=INK, width=4)
        f.rect(x - 46, top + 110, x + 46, top + 180, fill=WHITE, outline=GRAY)
        f.text((x, top + 128), '机器', 40, color=INK_SOFT, anchor='ma')
    f.text((90, top + 250), '总线：所有机器一个碰撞域', 40, color=RED)
    f.line((540, top + 130), (700, top + 130), color=GRAY, width=4, dash=12)
    f.text((620, top + 60), '换成交换机', 40, color=GRAY, anchor='ma')
    f.rect(700, top + 30, 840, top + 230, fill=TINT_B, outline=BLUE, width=4)
    f.text((770, top + 110), '交换机', 42, bold=True, color=BLUE, anchor='ma',
           allow_overlap=True)
    for i in range(3):
        yy = top + 60 + i * 70
        f.line((840, yy), (935, yy), color=BLUE, width=4)
        f.rect(935, yy - 24, 1000, yy + 24, fill=WHITE, outline=GRAY)
    f.text((1018, top + 250), '每个口只有一台机器', 40, color=GREEN,
           anchor='ra')
    y = top + 320
    y = note(f, y, '全双工之后，收发走两对线，也不需要再听别人——'
                   '碰撞检测整套机制被协议「降级」成了可选项。')
    y = note(f, y, '于是以太网赢下的不是「共享」，而是「不需要协调也能用」：'
                   '先来后到由交换机排队，而不是靠所有人抽签。')
    save(f, '20-switch.png', '从共享总线到交换式以太网')


def fig21():
    f, y = new(21, '五十年，一条线',
               '以太网没有换过名字，也没有换过帧格式，'
               '换的只是速率和介质。')
    top = y + 30
    f.line((90, top + 120), (990, top + 120), color=INK, width=4)
    dots = [(140, '1973', '梅特卡夫写下备忘录', TEAL),
            (350, '1980', 'DEC/Intel/Xerox 联合规范', TEAL),
            (560, '1983', 'IEEE 802.3 标准', AMBER),
            (760, '1990', '双绞线 + 集线器', AMBER),
            (950, '1999', '千兆到桌面', GREEN)]
    for x, year, text, color in dots:
        f.circle(x, top + 120, 15, fill=color, outline=color)
        f.text((x, top + 40), year, 42, bold=True, color=color, anchor='ma')
        f.wrap((x, top + 160), text, 40, 200, color=INK_SOFT, anchor='ma')
    y = top + 380
    y = note(f, y, '1973 年那份备忘录里，梅特卡夫把这条总线叫作「以太」——'
                   '借用的是当时物理学里假设存在、用来传播光的介质。名字留下来了，'
                   '假设早就被推翻了。')
    save(f, '21-timeline.png', '以太网五十年')


def fig22():
    f, y = new(22, '三句话', '如果只记三件事，记这三件。')
    top = y + 40
    items = [('共享信道里，沉默也是协议的一部分。',
              '你不说话的时候，别人才说得成。'),
             ('冲突不可怕，冲突很贵才可怕。',
              '先听后说让冲突变少，边说边听让冲突变便宜。'),
             ('退避要随机，窗口要会涨。',
              '随机把两个人错开，翻倍让一群人也能错开。')]
    for i, (head, sub) in enumerate(items):
        lane = top + i * 220
        tag = 'b%d' % i
        f.box(tag, 60, lane, 1002, lane + 176,
              fill=TINT_T if i % 2 == 0 else WHITE)
        f.text((92, lane + 26), head, 42, bold=True, inside=tag)
        f.text((92, lane + 100), sub, 40, color=INK_SOFT, inside=tag)
    save(f, '22-three-lines.png', '三句话总结')


def make_cover():
    fig = Fig(1080, width=1080)
    fig.text((96, 96), '一根线上', 84, bold=True, color=INK)
    fig.text((96, 200), '怎么同时说话', 84, bold=True, color=INK)
    fig.text((96, 320), '以太网：撞了以后，各自等一个随机数', 42, color=TEAL)
    top = 460
    fig.line((110, top), (970, top), color=INK, width=10)
    for i, name in enumerate(['A', 'B', 'C', 'D']):
        x = 190 + i * 230
        fig.line((x, top), (x, top + 80), color=INK, width=5)
        fig.circle(x, top, 13, fill=INK, outline=INK)
        box = 'n%d' % i
        fig.box(box, x - 70, top + 80, x + 70, top + 220, fill=WHITE)
        fig.text((x, top + 110), name, 44, bold=True, inside=box, anchor='ma')
        fig.text((x, top + 172), '机器', 38, color=INK_SOFT, inside=box,
                 anchor='ma')
    fig.text((96, 760), 'ALOHA 18.4%   ·   分槽 36.8%   ·   CSMA/CD 80%', 44,
             color=INK)
    fig.text((96, 850), '从一根同轴电缆讲起', 40, color=INK_SOFT)
    fig.text((96, 930), 'tech-articles · 2026-11-02', 38, color=GRAY)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


FIGS = [fig01, fig04, fig05, fig06, fig07, fig08, fig09, fig10, fig11, fig12,
        fig13, fig14, fig15, fig16, fig17, fig18, fig20, fig21, fig22]


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
