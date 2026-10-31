#!/usr/bin/env python3
"""Original teaching figures for the Diffie–Hellman article. MIT.

Numbers come from results.json (written by run_model.py, which calls dh.py).
The schematic figures say so on the canvas.
"""
from __future__ import annotations

import json
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

    def line(self, xs, ys, color, width=5, dash=None):
        pts = [(self.px(x), self.py(y)) for x, y in zip(xs, ys)]
        for a, b in zip(pts, pts[1:]):
            self.f.line(a, b, color=color, width=width, dash=dash)

    def bar(self, x, value, width_px, color):
        cx = self.px(x)
        self.f.rect(cx - width_px / 2, self.py(value), cx + width_px / 2,
                    self.py(0), fill=color, outline=None)
        self.f.text((cx, self.py(value) - 52), '%g' % value, 40, color=color,
                    anchor='ma', bold=True, allow_overlap=True)

    def hline(self, y, color=GRAY, dash=14):
        self.f.line((self.x0, self.py(y)), (self.x1, self.py(y)), color=color,
                    width=3, dash=dash)


class Seq:
    """A sequence diagram: actors on lifelines, messages as horizontal arrows.

    Lifelines are drawn a row at a time, so the canvas height follows the
    content instead of being pinned by one long vertical line.
    """

    def __init__(self, fig, actors, y, row=112):
        self.f = fig
        self.y = y
        self.row = row
        self.x = {key: x for key, x, _ in actors}
        self.actors = actors
        self.seg = None
        for key, x, name in actors:
            fig.text((x, y), name, 42, bold=True, anchor='ma')

    def start(self):
        self.y += 86
        self.seg = self.y - 22

    def _advance(self):
        if self.seg is not None and self.y - 22 > self.seg:
            for _key, x, _name in self.actors:
                self.f.line((x, self.seg), (x, self.y - 22), color=LIGHT, width=3)
        self.seg = self.y - 22

    def phase(self, text, color=INK):
        self.y += 44
        self.f.text((44, self.y), text, 40, color=color, bold=True)
        self.y += 84
        self._advance()
        return self.y

    def _arrow(self, xs, xd, color, width, dash=False):
        ax = xs + 14 if xd > xs else xs - 14
        bx = xd - 14 if xd > xs else xd + 14
        self.f.arrow((ax, self.y + 66), (bx, self.y + 66), color=color,
                     width=width, head=15, dash=14 if dash else None)

    def msg(self, src, dst, label, color=TEAL, dash=False, note_text=None):
        xs, xd = self.x[src], self.x[dst]
        self.f.text(((xs + xd) / 2, self.y), label, 40, color=color, anchor='ma')
        self._arrow(xs, xd, color, 5, dash)
        if note_text:
            self.f.text((1018, self.y), note_text, 40, color=GRAY, anchor='ra')
        self.y += self.row
        self._advance()
        return self.y

    def fan(self, src, dsts, label, color=TEAL, note_text=None):
        xs = self.x[src]
        self.f.text((xs, self.y), label, 40, color=color, anchor='ma')
        for dst in dsts:
            self._arrow(xs, self.x[dst], color, 4)
        if note_text:
            self.f.text((1018, self.y), note_text, 40, color=GRAY, anchor='ra')
        self.y += self.row
        self._advance()
        return self.y

    def fan_back(self, dsts, dst, label, color=BLUE, note_text=None):
        xd = self.x[dst]
        self.f.text((xd, self.y), label, 40, color=color, anchor='ma')
        for src in dsts:
            self._arrow(self.x[src], xd, color, 4)
        if note_text:
            self.f.text((1018, self.y), note_text, 40, color=GRAY, anchor='ra')
        self.y += self.row
        self._advance()
        return self.y


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


FIVE = ['A1', 'A2', 'A3', 'A4', 'A5']


def machine(fig, x, y, w, h, name, sub, fill=WHITE, tag=None):
    fig.box(tag or name, x, y, x + w, y + h, fill=fill)
    fig.text((x + 26, y + 22), name, 42, bold=True, inside=tag or name)
    fig.text((x + 26, y + 84), sub, 40, color=INK_SOFT, inside=tag or name)



# ---------------------------------------------------------------- figures
import math


def fig01():
    fig, y = new(1, '三个人，一个公开的频道',
                 'Alice 和 Bob 想私下说话，Eve 能听到线路上的一切。')
    fig.box('eve', 352, y + 20, 710, y + 160, fill=TINT_R)
    fig.text((376, y + 44), 'Eve', 42, bold=True, inside='eve')
    fig.text((376, y + 106), '只听，不说', 40, color=RED, inside='eve')
    top = y + 230
    for key, x, name, sub, tint in (('alice', 44, 'Alice', '想发消息', TINT_T),
                                    ('bob', 722, 'Bob', '想收消息', TINT_B)):
        fig.box(key, x, top, x + 296, top + 230, fill=tint)
        fig.text((x + 24, top + 26), name, 42, bold=True, inside=key)
        fig.text((x + 24, top + 94), sub, 40, color=INK_SOFT, inside=key)
        fig.text((x + 24, top + 162), '钥匙：？', 40, color=INK_SOFT, inside=key)
    fig.arrow((340, top + 104), (722, top + 104), color=TEAL, width=5, head=16)
    fig.arrow((722, top + 172), (340, top + 172), color=TEAL, width=5, head=16)
    fig.text((531, top + 52), '明文：p, g, A, B', 40, color=TEAL, anchor='ma')
    fig.text((531, top + 260), 'Eve 全都能抄下来', 40, color=RED, anchor='ma')
    save(fig, '01-three-people.png', '公开频道上的三个人')


def fig02():
    fig, y = new(2, '对称加密只要一把钥匙，问题是怎么给',
                 '同一把钥匙加密、解密。它不能明文发出去，那就先得有一条安全的路。')
    xs = [44, 420, 796]
    for name, x in zip(('明文', '密文', '明文'), xs):
        fig.box('b' + str(x), x, y + 120, x + 222, y + 270, fill=TINT_T)
        fig.text((x + 28, y + 166), name, 42, bold=True, inside='b' + str(x))
    fig.text((266, y + 170), '加密', 40, color=INK_SOFT, anchor='ma')
    fig.text((642, y + 170), '解密', 40, color=INK_SOFT, anchor='ma')
    fig.box('key', 300, y + 340, 762, y + 500, fill=TINT_G)
    fig.text((330, y + 368), '同一把钥匙 K', 42, bold=True, inside='key')
    fig.text((330, y + 432), '加密解密都用它', 40, color=GREEN, inside='key')
    for x in (200, 570, 900):
        fig.arrow((x, y + 340), (x, y + 278), color=GREEN, width=4, head=14)
    note(fig, y + 540, '于是问题变成：Alice 和 Bob 从没见面的两个人，'
                       '怎么在一条人人可听的线路上，商量出一把只有他们知道的钥匙？')
    save(fig, '02-one-key.png', '对称加密的一把钥匙')


def fig03():
    fig, y = new(3, '颜料的比喻：混在一起容易，分开很难',
                 '公开的是黄色。红和蓝各自保密。')
    panel_w, gap = 470, 60
    cells = [(0, 0), (1, 0), (0, 1), (1, 1)]
    colors = [(AMBER, RED), (AMBER, BLUE), (AMBER, BLUE), (AMBER, AMBER)]
    labels = [('① 公开黄 + 我的红', '→ 橙'), ('② 公开黄 + 我的蓝', '→ 绿'),
              ('③ 交换橙和绿', '还是橙 / 绿'), ('④ 各加一点自己的', '→ 同一种土色')]
    for (cx, cy), (c1, c2), (t1, t2) in zip(cells, colors, labels):
        x0 = 44 + cx * (panel_w + gap)
        y0 = y + 20 + cy * 330
        name = 'p%d%d' % (cx, cy)
        fig.box(name, x0, y0, x0 + panel_w, y0 + 290, fill=WHITE)
        fig.circle(x0 + 96, y0 + 84, 52, fill=c1, outline=INK, width=3)
        fig.circle(x0 + 176, y0 + 84, 52, fill=c2, outline=INK, width=3)
        fig.text((x0 + 24, y0 + 156), t1, 40, bold=True, inside=name)
        fig.text((x0 + 24, y0 + 216), t2, 40, color=INK_SOFT, inside=name)
    save(fig, '03-paint.png', '颜料混合的比喻')


def fig04():
    fig, y = new(4, '单向：混起来一秒，分出来没门',
                 '这一步的难度差，就是全部的安全性所在。')
    fig.box('mix', 44, y + 30, 500, y + 200, fill=TINT_T)
    fig.text((70, y + 60), '两种颜料倒进桶里', 42, bold=True, inside='mix')
    fig.text((70, y + 130), '混成一种新颜色', 40, color=INK_SOFT, inside='mix')
    fig.box('sep', 562, y + 30, 1018, y + 200, fill=TINT_R)
    fig.text((588, y + 60), '从一种颜色还原', 42, bold=True, inside='sep')
    fig.text((588, y + 130), '没人知道怎么做', 40, color=RED, inside='sep')
    fig.arrow((300, y + 220), (300, y + 330), color=TEAL, width=6, head=18)
    fig.text((330, y + 252), '容易，一秒', 40, color=TEAL)
    fig.arrow((760, y + 330), (760, y + 220), color=RED, width=4, head=18, dash=18)
    fig.text((560, y + 250), '难到没人做到过', 40, color=RED)
    note(fig, y + 400, '数学版的「混合」是乘方取模：给定 g、a、p，算 g^a mod p 很快；'
                       '给定 g^a mod p，反推 a 慢得多——这是被大量研究检验过的假设，'
                       '不是已被证明的定理。')
    save(fig, '04-one-way.png', '单向函数的难度差')


def fig05():
    fig, y = new(5, '模 23 的时钟：5 的幂绕着表盘走',
                 '每乘一次 5，就顺着表盘往前跳一格。转一圈 22 步走完全部非零余数。')
    cx, cy, r = 531, y + 330, 218
    fig.circle(cx, cy, r + 52, fill=WHITE, outline=LIGHT, width=4)
    table_ = R['table']
    n = len(table_)
    for row in table_:
        k, value = row['k'], row['value']
        ang = -math.pi / 2 + 2 * math.pi * k / n
        px, py = cx + r * math.cos(ang), cy + r * math.sin(ang)
        big = k % 2 == 0
        fig.circle(px, py, 13 if big else 9, fill=TEAL if big else GRAY,
                   outline=TEAL if big else GRAY)
        if big:
            lx = cx + (r + 58) * math.cos(ang)
            ly = cy + (r + 58) * math.sin(ang)
            fig.text((lx, ly - 20), str(value), 40, color=INK, anchor='ma',
                     allow_overlap=True)
    fig.text((cx, cy - 24), 'mod 23', 42, bold=True, anchor='ma')
    fig.text((cx, cy + 32), '22 个非零余数', 40, color=INK_SOFT, anchor='ma')
    note(fig, cy + r + 100, '5 是 23 的原根：它的幂能走遍 1..22 的每一个数。'
                            '图上的数字由 examples/dh.py 算出。')
    save(fig, '05-clock.png', '模 23 的幂循环')


def fig06():
    fig, y = new(6, '把这张表抄下来，后面全靠它',
                 'p = 23, g = 5。右边是 5^k mod 23 的全部 22 个结果。')
    rows = R['table']
    half = (len(rows) + 1) // 2
    for col, chunk in enumerate((rows[:half], rows[half:])):
        x0 = 44 + col * 492
        fig.rect(x0, y + 10, x0 + 470, y + 78, fill=TINT_T, outline=None)
        fig.text((x0 + 20, y + 24), 'k', 40, bold=True)
        fig.text((x0 + 170, y + 24), '5^k mod 23', 40, bold=True)
        yy = y + 96
        for row in chunk:
            fig.text((x0 + 20, yy), str(row['k']), 40, color=INK_SOFT)
            fig.text((x0 + 170, yy), str(row['value']), 40, bold=True)
            yy += 62
        fig.line((x0, yy - 16), (x0 + 470, yy - 16), color=LIGHT, width=3)
    note(fig, y + 790, '注意 k = 0 时的 1 和 k = 11 时的 22：这两头一接，就绕回来了。')
    save(fig, '06-table.png', '5 的幂模 23 的完整表')


def fig07():
    fig, y = new(7, '一次完整的交换，数字小到能手算',
                 'p = 23, g = 5。Alice 的秘密是 6，Bob 的秘密是 15。')
    d = R['demo']
    s = Seq(fig, [('alice', 190, 'Alice'), ('eve', 531, '线路'), ('bob', 872, 'Bob')], y + 10)
    s.start()
    s.phase('公开参数 p = 23，g = 5，谁都能看', color=INK_SOFT)
    s.msg('alice', 'bob', 'A = 8', note_text='Alice 藏着 a = 6')
    s.msg('bob', 'alice', 'B = 19', color=BLUE, note_text='Bob 藏着 b = 15')
    s.phase('各自把对方的数，抬到自己的秘密次方', color=INK_SOFT)
    s.msg('alice', 'bob', 's = 19^6 mod 23 = 2', note_text='只用 a = 6')
    s.msg('bob', 'alice', 's = 8^15 mod 23 = 2', color=BLUE, note_text='只用 b = 15')
    note(fig, s.y + 16, '两个人算出来都是 %d。线路上出现过的数字只有 23、5、8、19。'
                        % d['s_alice'])
    save(fig, '07-exchange.png', '一次手算的密钥交换')


def fig08():
    fig, y = new(8, '为什么两边一定相等',
                 '因为乘法能换顺序：(g^a)^b 和 (g^b)^a 都只是 g 乘了自己 ab 次。')
    c = R['commute'][0]
    rows = [[('Alice 算', TEAL, True),
             ('(%d^%d)^%d mod 23' % (c['g'], c['a'], c['b']), INK, False),
             ('= %d' % c['left'], TEAL, True)],
            [('同一个指数', INK_SOFT, True),
             ('%d^(%d×%d) mod 23' % (c['g'], c['a'], c['b']), INK, False),
             ('= %d' % c['left'], TEAL, True)],
            [('Bob 算', BLUE, True),
             ('(%d^%d)^%d mod 23' % (c['g'], c['b'], c['a']), INK, False),
             ('= %d' % c['right'], BLUE, True)]]
    y = table(fig, y + 20, [(44, 'la'), (300, 'la'), (860, 'la')], rows, row_h=90)
    note(fig, y, 'a 和 b 都是别人的秘密，但谁也不需要知道对方那个。'
                 '交换的不是钥匙本身，是「让钥匙自己长成一样」这件事。')
    save(fig, '08-commute.png', '交换律让两边得到同一个数')


def fig09():
    fig, y = new(9, 'Eve 手里有什么', '她听见了四个数，然后只能猜。')
    rows = [[('p = 23', INK, True), ('公开的模数', INK_SOFT, False)],
            [('g = 5', INK, True), ('公开的底数', INK_SOFT, False)],
            [('A = 8', INK, True), ('Alice 发的', INK_SOFT, False)],
            [('B = 19', INK, True), ('Bob 发的', INK_SOFT, False)],
            [('a = ?', RED, True), ('要解 5^a ≡ 8', RED, False)],
            [('b = ?', RED, True), ('要解 5^b ≡ 19', RED, False)]]
    y = table(fig, y + 20, [(44, 'la'), (300, 'la')], rows, row_h=78)
    y = note(fig, y, '在 23 这个规模上，Eve 一个一个试就行。换成 2048 位，'
                     '这条路的长度会变得离谱。')
    bullets(fig, y, ['5^1 = 5，5^2 = 2，5^3 = 10……试到 5^6 = 8',
                     '试一次一个乘法，23 的规模最多试 22 次',
                     '问题从来不是「有没有解」，而是「要试多少次」'])
    save(fig, '09-eve-sees.png', '窃听者看到的信息')


def fig10():
    fig, y = new(10, '实测：两种攻击的步数差几个数量级',
                 '同一批随机素数，先用穷举、再用大步小步法，数它们的模乘次数。')
    cost = R['cost']
    box = (180, y + 90, 1004, y + 620)
    p = Plot(fig, box, (14, 30), (1.5, 8.2))
    p.axes(xticks=[16, 20, 24, 28], yticks=[2, 3, 4, 5, 6, 7],
           xfmt='%d 位', yfmt='10^%g', ylab='模乘次数（对数）')
    xs = [row['bits'] for row in cost]
    p.line(xs, [math.log10(row['brute_steps']) for row in cost], RED, width=6)
    p.line(xs, [math.log10(row['bsgs_steps']) for row in cost], TEAL, width=6)
    for row in cost:
        for value, color in ((row['brute_steps'], RED), (row['bsgs_steps'], TEAL)):
            px, py = p.px(row['bits']), p.py(math.log10(value))
            fig.circle(px, py, 11, fill=color, outline=color)
    for i, (name, color) in enumerate((('穷举：一个一个试', RED), ('大步小步：开平方', TEAL))):
        x = 180 + i * 420
        fig.rect(x, y + 700, x + 30, y + 732, fill=color, outline=None)
        fig.text((x + 46, y + 692), name, 40, color=color)
    note(fig, y + 780, '位数每加 4 位，穷举的代价乘 16；大步小步只乘 4。'
                       '28 位时穷举要 3000 万次、1.5 秒，大步小步 1.7 万次、1.8 毫秒。')
    save(fig, '10-attack-cost.png', '穷举与大步小步法的实测步数')


def fig11():
    fig, y = new(11, '把位数往上加，代价跟得上吗',
                 '下表是算的：开平方后的尝试次数，以及按每秒十亿次估算要算多久。')
    rows = []
    for e in R['estimate']:
        exp = int(round(e['log10_steps']))
        yexp = e['log10_years']
        if yexp < -4:
            human = '一瞬间'
        elif yexp < 0:
            human = '几秒'
        elif yexp < 2:
            human = '几分钟到几小时'
        elif yexp < 5:
            human = '几天到几年'
        else:
            human = '10^%d 年' % int(round(yexp))
        rows.append([('%d 位' % e['bits'], INK, True),
                     ('10^%d 次' % exp, TEAL, True),
                     (human, INK_SOFT, False)])
    y = table(fig, y + 10, [(44, 'la'), (300, 'la'), (640, 'la')], rows, row_h=78)
    note(fig, y, '2048 位那一行：开平方要 10^1024 次尝试。宇宙的年龄约 10^17 秒。'
                 '这就是为什么现在的密钥是 2048 位起步，而不是 128 位。')
    save(fig, '11-bit-length.png', '密钥长度与破解代价（估算）')


def fig12():
    fig, y = new(12, '真实的那个素数长这样',
                 'RFC 3526 第 3 节的 2048 位 MODP 组，互联网上真的在用它。')
    meta = R['real']
    head = meta['p_hex_head']
    yy = y + 20
    for i in range(0, len(head), 32):
        fig.text((44, yy), head[i:i + 32], 40, color=INK)
        yy += 56
    fig.text((44, yy + 6), '……', 40, color=GRAY)
    yy += 72
    tail = meta['p_hex_tail']
    fig.text((44, yy), tail[:32], 40, color=INK)
    fig.text((44, yy + 56), tail[32:], 40, color=INK)
    yy += 140
    fig.box('len', 44, yy, 1018, yy + 230, fill=TINT_T)
    fig.text((70, yy + 22), '%d 个十六进制字符' % meta['p_hex_len'], 42,
             bold=True, inside='len')
    fig.text((70, yy + 96), '= %d 位二进制 = %d 位十进制' % (meta['p_bits'], meta['p_digits']),
             40, color=INK_SOFT, inside='len')
    fig.text((70, yy + 162), '生成器 g = 2，所有人共用这个 p', 40,
             color=INK_SOFT, inside='len')
    save(fig, '12-prime.png', 'RFC 3526 的 2048 位素数')


def fig13():
    fig, y = new(13, '中间人：一个人谈两场，谁也不知情',
                 'Mallory 对 Alice 扮 Bob，对 Bob 扮 Alice。')
    top = y + 30
    for key, x, name, tint in (('alice', 44, 'Alice', TINT_T),
                               ('mal', 400, 'Mallory', TINT_R),
                               ('bob', 756, 'Bob', TINT_B)):
        fig.box(key, x, top, x + 262, top + 170, fill=tint)
        fig.text((x + 24, top + 26), name, 42, bold=True, inside=key)
    fig.arrow((306, top + 70), (400, top + 70), color=TEAL, width=5, head=16)
    fig.arrow((662, top + 124), (756, top + 124), color=TEAL, width=5, head=16)
    fig.text((318, top + 10), 'A1', 40, color=TEAL)
    fig.text((678, top + 60), 'B2', 40, color=TEAL)
    mid = top + 230
    for key, x, w, title_, body, tint in (
            ('k1', 44, 470, 'Alice 以为', '和 Bob 共享 s1', TINT_A),
            ('k2', 548, 470, 'Bob 以为', '和 Alice 共享 s2', TINT_G)):
        fig.box(key, x, mid, x + w, mid + 180, fill=tint)
        fig.text((x + 24, mid + 26), title_, 42, bold=True, inside=key)
        fig.text((x + 24, mid + 96), body, 40, color=INK_SOFT, inside=key)
    note(fig, mid + 210, '两场交换各自都合法。两个人都算出了「同样的」密钥——'
                         '只是不是和对方同一个。协议本身没有出错。')
    save(fig, '13-man-in-the-middle.png', '中间人攻击')


def fig14():
    fig, y = new(14, 'Mallory 的两把钥匙，数字对得上',
                 '同一个 p = 23、g = 5，两个不同的秘密指数。')
    m = R['mitm']
    a1, a2 = m['alice'], m['bob']
    rows = [[('Alice ↔ Mallory', INK, True),
             ('a = %d，m1 = %d' % (a1['a'], a1['b']), INK_SOFT, False),
             ('s = %d' % a1['s_alice'], TEAL, True)],
            [('Mallory ↔ Bob', INK, True),
             ('m2 = %d，b = %d' % (a2['a'], a2['b']), INK_SOFT, False),
             ('s = %d' % a2['s_bob'], TEAL, True)],
            ]
    y = table(fig, y + 20, [(44, 'la'), (400, 'la'), (800, 'la')], rows, row_h=86)
    y = note(fig, y, 'm1 和 m2 是两个独立的值：给 Alice 的公钥用 m1 算，给 Bob 的用 m2 算。'
                     '两人都以为自己得到了同一个密钥，其实不是。')
    bullets(fig, y, ['两个 s 不相等，但没有任何一方能看出来',
                     'Mallory 两个都知道，转发时各用一把'], accent=RED)
    save(fig, '14-two-keys.png', '中间人手里的两把钥匙')


def fig15():
    fig, y = new(15, '要挡住中间人，得先知道对面是谁',
                 '把名字和公钥用签名绑在一起，中间人就换不掉公钥。')
    top = y + 30
    fig.box('cert', 44, top, 640, top + 300, fill=WHITE)
    fig.text((70, top + 18), '证书', 42, bold=True, inside='cert')
    for i, (name, value) in enumerate((('域名', 'example.com'),
                                      ('公钥', 'B = 19'),
                                      ('签发者', 'CA 的签名'),
                                      ('有效期', '2026 → 2027'))):
        fig.text((70, top + 82 + i * 54), name, 40, color=INK_SOFT, inside='cert')
        fig.text((230, top + 82 + i * 54), value, 40, inside='cert')
    fig.box('verify', 686, top + 40, 1018, top + 260, fill=TINT_G)
    fig.text((710, top + 62), '浏览器验证', 42, bold=True, inside='verify')
    fig.text((710, top + 130), '签名对得上', 40, color=GREEN, inside='verify')
    fig.text((710, top + 190), '才继续握手', 40, color=GREEN, inside='verify')
    fig.arrow((650, top + 150), (680, top + 150), color=GREEN, width=5, head=16)
    note(fig, top + 340, 'Diffie–Hellman 解决的是「有人在听」，不是「对面是谁」。'
                         '换掉公钥的人，看起来和真的一模一样。')
    save(fig, '15-certificate.png', '证书把名字和公钥绑起来')


def fig16():
    fig, y = new(16, '前向保密：每次见面都换一把新钥匙',
                 '长期密钥只用来签名，真正的会话密钥用完就丢。')
    top = y + 30
    fig.box('static', 44, top, 500, top + 300, fill=TINT_R)
    fig.text((70, top + 22), '用长期密钥交换', 42, bold=True, inside='static')
    for i, text in enumerate(['私钥一旦泄露', '以前录下的流量', '都能事后解开']):
        fig.text((70, top + 96 + i * 62), text, 40, color=RED, inside='static')
    fig.box('ephemeral', 562, top, 1018, top + 300, fill=TINT_G)
    fig.text((588, top + 22), '每次连接临时生成', 42, bold=True, inside='ephemeral')
    for i, text in enumerate(['用完就丢', '泄露只影响当前连接', '旧流量仍然安全']):
        fig.text((588, top + 96 + i * 62), text, 40, color=GREEN, inside='ephemeral')
    note(fig, top + 340, '代价是每次多几次签名和验证。TLS 1.3 干脆删掉了'
                         '「用长期密钥交换」这条路，只留临时的（EC）DHE。')
    save(fig, '16-forward-secrecy.png', '前向保密')


def fig17():
    fig, y = new(17, 'TLS 1.3 的握手，压缩成四行',
                 '示意：省略证书链、会话恢复与证书验证。')
    s = Seq(fig, [('client', 190, '客户端'), ('net', 531, '网络'), ('server', 872, '服务器')], y + 10)
    s.start()
    s.phase('一个往返之内完成密钥协商', color=INK_SOFT)
    s.msg('client', 'server', 'ClientHello + key_share', note_text='临时公钥 A')
    s.msg('server', 'client', 'ServerHello + key_share', color=BLUE, note_text='临时公钥 B')
    s.phase('两边各自算出会话密钥，全程没有传输它', color=INK_SOFT)
    s.msg('client', 'server', 'Finished（已加密）', color=GREEN, note_text='用会话密钥')
    s.msg('server', 'client', 'Finished（已加密）', color=GREEN, note_text='握手完成')
    note(fig, s.y + 16, '实际部署里 ECDHE 是默认选项：同样的强度，密钥短得多，算得也快。')
    save(fig, '17-tls13.png', 'TLS 1.3 握手示意')


def fig18():
    fig, y = new(18, '椭圆曲线版：点也能加起来',
                 'y² = x³ + 7 mod 17 上的 17 个点，外加一个无穷远点。'
                 '交换只是把「乘方」换成「加点」。')
    e = R['ecdh']
    size, left, top = 54, 60, y + 10
    span = size * 17
    fig.rect(left, top, left + span, top + span, fill=WHITE, outline=LIGHT, width=3)
    pts = {tuple(p) for p in e['points']}
    marks = {tuple(e['g']): ('g', TEAL), tuple(e['A']): ('5g', BLUE),
             tuple(e['B']): ('7g', AMBER), tuple(e['s1']): ('6g', GREEN)}
    for gx in range(18):
        for gy in range(18):
            px = left + gx * size
            py = top + span - gy * size
            if (gx, gy) in pts:
                name, color = marks.get((gx, gy), (None, GRAY))
                fig.circle(px, py, 14 if name else 6, fill=color, outline=color)
                if name:
                    anchor = 'ra' if gx > 11 else 'la'
                    fig.text((px + (-20 if anchor == 'ra' else 20), py - 28),
                             name, 40, color=color, anchor=anchor, allow_overlap=True)
            elif gx % 4 == 0 and gy % 4 == 0:
                fig.circle(px, py, 4, fill=LIGHT, outline=LIGHT)
    fig.text((left, top + span + 16), 'x = 0 … 17', 40, color=GRAY)
    fig.text((1018, top + span + 16), '17 个点，群阶 18', 40, color=GRAY, anchor='ra')
    note(fig, top + span + 80, '真实曲线用 256 位的素数域，点多到没法画。'
                               '规则完全一样：(a·g)·b = (b·g)·a。')
    save(fig, '18-elliptic-curve.png', '小椭圆曲线上的点与交换')


def fig19():
    fig, y = new(19, '五十年，一条时间线',
                 '其中有二十年，最好的版本是一个不能说的秘密。')
    items = [(1976, 'Diffie 与 Hellman 发表公钥交换', TEAL),
             (1977, 'Rivest、Shamir、Adleman 给出 RSA', BLUE),
             (1997, 'GCHQ 解密档案：1969–1975 年就做过', AMBER),
             (2006, 'TLS 把临时密钥交换写进标准', TEAL),
             (2013, 'Snowden 文件让前向保密成为默认', RED),
             (2018, 'TLS 1.3 只保留临时的（EC）DHE', GREEN)]
    xline = 176
    yy = y + 40
    fig.line((xline, yy), (xline, yy + 6 * 118), color=LIGHT, width=6)
    for year, text, color in items:
        fig.circle(xline, yy + 40, 13, fill=color, outline=color)
        fig.text((44, yy + 12), str(year), 42, bold=True, color=color)
        fig.text((236, yy + 8), text, 40, color=INK)
        yy += 118
    note(fig, yy + 10, '1976 年那篇论文只有五页，标题是《New Directions in Cryptography》。'
                       '它提出的不是算法，是一类新问题。')
    save(fig, '19-timeline.png', '公钥交换的五十年')


def fig20():
    fig, y = new(21, '一句话总结', '把前面所有内容压成三行。')
    bullets(fig, y + 40, ['公开的数字可以很多，秘密的指数只能自己知道。',
                          '两边算出的密钥相同，因为乘方可以换顺序。',
                          '它防的是窃听，不防冒充：身份要靠签名和证书另补。'], size=44)
    save(fig, '21-three-lines.png', '三句话总结')


def make_cover():
    f = Fig(1080, width=1080)
    f.text((540, 300), '两个人，一个公开频道', 76, True, anchor='ma')
    f.text((540, 396), '怎样商量出一把别人猜不到的钥匙', 48, True, anchor='ma')
    f.text((540, 464), 'Diffie–Hellman 密钥交换', 48, True, TEAL, anchor='ma')
    f.circle(300, 600, 54, fill=AMBER, outline=INK, width=4)
    f.circle(410, 600, 54, fill=RED, outline=INK, width=4)
    f.text((355, 680), '混合', 40, color=INK_SOFT, anchor='ma')
    f.circle(680, 600, 54, fill=AMBER, outline=INK, width=4)
    f.circle(790, 600, 54, fill=BLUE, outline=INK, width=4)
    f.text((735, 680), '再混', 40, color=INK_SOFT, anchor='ma')
    f.text((540, 760), '公开的数字，私密的指数', 40, True, INK_SOFT, anchor='ma')
    f.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


def main():
    only = sys.argv[1:]
    failed = {}
    for i in range(1, 21):
        name = 'fig%02d' % i
        fn = globals().get(name)
        if fn is None:
            continue
        if only and name not in only:
            continue
        try:
            fn()
        except Exception as exc:
            failed[name] = str(exc)[:300]
            print('FAIL', name, exc)
    if not only or 'cover' in only:
        try:
            make_cover()
        except Exception as exc:
            failed['cover'] = str(exc)[:300]
            print('FAIL cover', exc)
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(sorted(META, key=lambda r: r['path']), ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(META))
    if failed:
        print('failed:', sorted(failed))


if __name__ == '__main__':
    main()
