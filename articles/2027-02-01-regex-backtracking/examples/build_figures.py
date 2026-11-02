#!/usr/bin/env python3
"""正则回溯一文的原创教学插图。MIT。

带数字的图全部读 results.json；图 11 的格子是记忆化引擎真实访问过的
(状态, 位置) 对，图 08 的柱子是 NFA 模拟每步真实的线程数。
"""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageFont

from figkit import (Fig, PALETTE, BG, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED,
                    GRAY, LIGHT, PALE, GREEN, CREAM, TINT_T, TINT_B, TINT_A,
                    TINT_R, TINT_G)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []

MONO_PATH = '/System/Library/Fonts/Menlo.ttc'
_MONO = {}

VIOLET = '#5b4b8a'
BROWN = '#8a5a44'
PALETTE.update({VIOLET, BROWN})


def mono(fig, xy, s, size=38, color=INK, anchor='la'):
    if size not in _MONO:
        _MONO[size] = ImageFont.truetype(MONO_PATH, size, index=0)
    f = _MONO[size]
    bb = fig.d.textbbox(xy, s, font=f, anchor=anchor)
    fig.d.text(xy, s, font=f, fill=color, anchor=anchor)
    fig.labels.append(dict(s=s, size=size, bold=False, bbox=bb, inside=None,
                           anchor=anchor, allow_overlap=False, tag=None,
                           skip_audit=False))
    fig.min_px = min(fig.min_px, size)
    return bb


def new(n, title, sub=None):
    fig = Fig(900)
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


def table(fig, y, cols, rows, size=38, row_h=68, zebra=True):
    for i, row in enumerate(rows):
        if zebra and i % 2 == 1:
            fig.rect(48, y - 12, 1014, y + row_h - 14, fill=PALE, outline=None)
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


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def legend(fig, y, items, x0=52, step=300):
    x = x0
    for color, text in items:
        fig.rect(x, y, x + 30, y + 30, fill=color, outline=None, radius=6)
        fig.text((x + 44, y - 4), text, 38, color=INK)
        x += step
    return y + 46


def card(fig, name, x0, y0, x1, y1, head, lines, accent, size=40, head_size=42):
    fig.box(name, x0, y0, x1, y1, fill=WHITE, outline=accent)
    fig.text((x0 + 24, y0 + 18), head, head_size, bold=True, color=accent,
             inside=name)
    y = y0 + 24 + head_size * 1.9
    for ln in lines:
        y += int(fig.wrap((x0 + 24, y), ln, size, (x1 - x0) - 48, color=INK,
                          inside=name) * size * 1.35) + 8
    return y


# ---------------------------------------------------------------- 图 01

def fig01():
    fig, y = new(1, '同一个模式，两种走法',
                 '模式 ab*c：一个 a，任意多个 b（可以 0 个），最后跟一个 c。'
                 ' 机器有两种做法，差别不在模式，在「同一时刻手上拿着几条路」。')
    cy = y + 120
    bw, bh = 120, 110
    xs = [70, 300, 530, 760]
    for i, x in enumerate(xs):
        name = 's%d' % i
        fig.box(name, x, cy, x + bw, cy + bh,
                fill=TINT_G if i == 3 else WHITE,
                outline=GREEN if i == 3 else INK_SOFT)
        fig.text((x + bw / 2, cy + bh / 2), str(i), 46, bold=True,
                 anchor='mm', inside=name)
        fig.text((x + bw / 2, cy + bh + 16), ['起点', '可停可走', '等 c', '收下'][i],
                 38, color=GRAY, anchor='ma')
    for a, b, lab in ((0, 1, 'a'), (1, 2, 'ε'), (2, 3, 'c')):
        x0, x1 = xs[a] + bw, xs[b]
        fig.arrow((x0 + 6, cy + bh / 2), (x1 - 6, cy + bh / 2), color=INK,
                  width=4, head=14)
        fig.text(((x0 + x1) / 2, cy - 48), lab, 42, anchor='ma', color=TEAL)
    loop_x = xs[1] + bw / 2
    fig.arrow((loop_x - 20, cy - 6), (loop_x - 20, cy - 84), color=TEAL,
              width=4, head=14)
    fig.arrow((loop_x + 20, cy - 84), (loop_x + 20, cy - 6), color=TEAL,
              width=4, head=14)
    fig.text((loop_x, cy - 132), 'b 可以反复吃', 40, anchor='ma', color=TEAL)

    top = cy + bh + 78
    card(fig, 'k1', 48, top, 520, top + 380, '回溯：一次只拿一条路',
         ['先贪心地把 b 吃到不能再吃，再试 c；失败就退回一个 b，'
          '换一种切法。'], RED)
    card(fig, 'k2', 542, top, 1014, top + 380, 'NFA：同时拿所有路',
         ['每读一个字符，把所有活着的状态一起往前推一步；'
          '手里是一小把状态。'], TEAL)
    save(fig, '01-two-ways.png', '回溯与 NFA 两种执行方式的结构差别')


# ---------------------------------------------------------------- 图 02

def fig02():
    rows = R['catastrophic']['rows']
    last = rows[-1]
    fig, y = new(2, '(a+)+b 撞上一串 a',
                 '文本是 n 个 a，里面没有 b，所以注定失配。'
                 ' 每加两个字符，回溯的步数就乘 4；纵轴是对数刻度。')
    x0, x1 = 150, 972
    ytop, ybot = y + 40, y + 470
    ylo, yhi = 2.0, 8.0

    def fx(n):
        return x0 + (n - 6) / 14.0 * (x1 - x0)

    def fy(v):
        t = (math.log10(max(v, 1)) - ylo) / (yhi - ylo)
        return ybot - max(0.0, min(t, 1.0)) * (ybot - ytop)

    for e in range(2, 9, 2):
        yy = ybot - (e - ylo) / (yhi - ylo) * (ybot - ytop)
        fig.line((x0, yy), (x1, yy), color=LIGHT, width=2)
        mono(fig, (x0 - 18, yy - 22), '1e%d' % e, 36, color=GRAY, anchor='ra')
    fig.line((x0, ybot), (x1, ybot), color=INK, width=3)
    for n in (6, 10, 14, 18, 20):
        fig.text((fx(n), ybot + 16), str(n), 38, anchor='ma', color=INK_SOFT)
    fig.text((x0, ybot + 68), 'n（文本里 a 的个数）', 38, color=INK_SOFT)

    for key, color in (('backtrack', RED), ('memo', TEAL), ('pike', BLUE)):
        pts = [(fx(r['n']), fy(r[key])) for r in rows]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=color, width=5)
        for p in pts:
            fig.circle(p[0], p[1], 7, fill=color, outline=color)
    fig.text((x1 - 16, ytop + 6), '{:,} 步'.format(last['backtrack']).replace(',', ' '),
             42, bold=True, color=RED, anchor='ra')
    fig.text((x1 - 16, fy(last['pike']) - 30), '%d 步' % last['pike'], 38,
             color=BLUE, anchor='ra')
    leg_y = ybot + 116
    legend(fig, leg_y, [(RED, '回溯'), (TEAL, '记忆化'), (BLUE, 'NFA 模拟')],
           step=310)
    save(fig, '02-catastrophic.png', '(a+)+b 在纯 a 文本上的步数增长')


# ---------------------------------------------------------------- 图 03

def fig03():
    rows = R['splits']['rows']
    fig, y = new(3, '回溯在试什么：把一串 a 切成几段',
                 '模式 (a+)+b 里，前面那串 a 可以切成任意多段，每段至少一个 a。'
                 ' 回溯要把这些切法一条条试完。')
    cy = y + 30
    cells = 5
    cw = 84
    x = 70
    for i in range(cells):
        fig.box('c%d' % i, x, cy, x + cw, cy + cw, fill=WHITE, outline=INK_SOFT,
                radius=12)
        mono(fig, (x + cw / 2, cy + cw / 2 - 26), 'a', 46, anchor='ma')
        if i < cells - 1:
            fig.line((x + cw + 6, cy + cw / 2), (x + cw + 40, cy + cw / 2),
                     color=GRAY, width=3, dash=8)
            fig.text((x + cw + 23, cy - 46), '切?', 38, color=AMBER, anchor='ma')
            x += cw + 46
        else:
            x += cw + 46
    fig.text((70, cy + cw + 64), '4 个空隙，每个「切」或「不切」', 42, color=INK)
    fig.text((70, cy + cw + 124), '切法 = 2 的 4 次方 = 16 种', 42, bold=True,
             color=TEAL)

    ty = cy + cw + 200
    pairs = []
    for i in range(len(rows) // 2):
        a = rows[i]
        b = rows[i + len(rows) // 2] if i + len(rows) // 2 < len(rows) else None
        pairs.append([(str(a['n']), INK, False), ('{:,}'.format(a['ways']).replace(',', ' '), TEAL, False),
                      (str(b['n']), INK, False) if b else ('', INK, False),
                      ('{:,}'.format(b['ways']).replace(',', ' ') if b else '', TEAL, False)])
    cols = [(70, 'la'), (270, 'la'), (600, 'la'), (800, 'la')]
    table(fig, ty, cols, pairs, row_h=74)
    fig.text((70, ty + 74 * len(pairs) + 6), 'n（要切的一串 a 有多长）与切法数',
             40, color=INK_SOFT)
    save(fig, '03-splits.png', '把一串 a 切成若干段的切法数')


# ---------------------------------------------------------------- 图 04

def fig04():
    rows = [r for r in R['catastrophic']['rows'] if r['n'] in (8, 12, 16, 20)]
    fig, y = new(4, '同一批输入，三种做法的步数',
                 '步数的单位是「执行了一条指令」，三种做法用同一把尺子量。')
    body = []
    for r in rows:
        body.append([('n = %d' % r['n'], INK, False),
                     ('{:,}'.format(r['backtrack']).replace(',', ' '), RED, True),
                     ('{:,}'.format(r['memo']).replace(',', ' '), TEAL, False),
                     ('{:,}'.format(r['pike']).replace(',', ' '), BLUE, False)])
    cols = [(70, 'la'), (300, 'la'), (640, 'la'), (880, 'la')]
    y = table(fig, y + 10, cols, body, row_h=86)
    fig.text((70, y - 30), '回溯', 40, color=RED, bold=True)
    fig.text((300, y - 30), '回溯 + 记忆化', 40, color=TEAL, bold=True)
    fig.text((640, y - 30), 'NFA 模拟', 40, color=BLUE, bold=True)
    y = note(fig, y + 40, 'n 从 8 到 20，回溯的步数从 2 519 涨到 10 485 671，'
                          '涨了四千倍；另外两条线几乎没动。')
    y = note(fig, y, '最后一行三个数字放在一张图上，纵轴得取对数才装得下。')
    note(fig, y + 10, '每加两个 a，回溯步数乘 4：2519 → 40903 是 16.2 倍，跨两步。',
         color=INK_SOFT)
    save(fig, '04-steps-table.png', '三种做法在 n=8/12/16/20 上的步数')


# ---------------------------------------------------------------- 图 05

def fig05():
    rows = R['cloudflare']['match']
    fig, y = new(5, 'Cloudflare 那条正则的关键片段：.*.*=.*',
                 '文本是 x= 后面跟 k 个 x。每多给一个 x，贪婪的第一个 .* 就多退一次，'
                 '第二个 .* 就多扫一遍。')
    x0, x1 = 150, 960
    ytop, ybot = y + 40, y + 420
    vmax = 900

    def fx(k):
        return x0 + k / 20.0 * (x1 - x0)

    def fy(v):
        return ybot - min(v / vmax, 1.0) * (ybot - ytop)

    for v in (0, 300, 600, 900):
        yy = fy(v)
        fig.line((x0, yy), (x1, yy), color=LIGHT, width=2)
        mono(fig, (x0 - 18, yy - 22), str(v), 36, color=GRAY, anchor='ra')
    fig.line((x0, ybot), (x1, ybot), color=INK, width=3)
    pts = [(fx(r['k']), fy(r['backtrack'])) for r in rows]
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=AMBER, width=5)
    for p in pts:
        fig.circle(p[0], p[1], 7, fill=AMBER, outline=AMBER)
    fig.text((x1 - 10, fy(rows[-1]['backtrack']) - 40), '848 步',
             42, bold=True, color=AMBER, anchor='ra')
    fig.text((x0 + 8, fy(rows[0]['backtrack']) - 44), '18 步', 40,
             color=AMBER, anchor='la')
    for k in (0, 5, 10, 15, 20):
        fig.text((fx(k), ybot + 16), str(k), 38, anchor='ma', color=INK_SOFT)
    fig.text((x0, ybot + 68), 'k（等号后面 x 的个数）', 38, color=INK_SOFT)
    y = note(fig, ybot + 130,
             '实际事故里的那条规则比这长得多，这个片段只是把代价最贵的一截单独拎出来。')
    y = note(fig, y, '换一个引擎、换一个步数计数器，绝对值会不同，形状不会：'
                     '外层退一步，内层就重扫一遍，平方是结构决定的。')
    save(fig, '05-cloudflare.png', '.*.*=.* 在 x= 加 k 个 x 上的步数')


# ---------------------------------------------------------------- 图 06

def fig06():
    cf = R['cloudflare']
    fig, y = new(6, '同样的模式，失败比成功更贵',
                 '成功时引擎在第一个能凑出来的位置就停手；失败时它得把所有切法试完。')
    top = y + 10
    ok = cf['match'][-1]
    card(fig, 'a', 48, top, 520, top + 460, '找到了',
         ['输入：x= 后跟 20 个 x',
          '回溯：{n} 步'.format(n='{:,}'.format(ok['backtrack']).replace(',', ' ')),
          '记忆化：{n} 步'.format(n=ok['memo']),
          'NFA：{n} 步'.format(n=ok['pike'])], GREEN, size=42)
    bad = cf['fail']
    card(fig, 'b', 542, top, 1014, top + 460, '没找到',
         ['输入：20 个 x，没有等号',
          '回溯：{n} 步'.format(n='{:,}'.format(bad['backtrack']).replace(',', ' ')),
          '记忆化：{n} 步'.format(n=bad['memo']),
          'NFA：{n} 步'.format(n=bad['pike'])], RED, size=42)
    y = note(fig, top + 510, '两次都只是 20 个字符。回溯在失败那一次多花了 '
                             '6.8 倍的步数，因为成功可以提前收工，失败不行。')
    y = note(fig, y, '这也解释了事故里为什么是「每个请求都变慢」而不是「偶尔一个请求很慢」：'
                     '畸形输入越多，越容易走到最贵的那条路。')
    save(fig, '06-fail-vs-match.png', '同一模式成功与失败的步数差')


# ---------------------------------------------------------------- 图 07

def fig07():
    cases = R['rewrites']['cases']
    def get(label, note_):
        for c in cases:
            if c['label'] == label and c['note'] == note_:
                return c['backtrack']
        raise KeyError(label, note_)

    fig, y = new(7, '同一件事，三种写法',
                 '文本相同，只改模式。数字是回溯的步数。')
    body = [
        [('.*.*=.*', INK, True), (str(get('greedy', 'short')), INK, False),
         (str(get('greedy', '20 x after =')), AMBER, True),
         ('{:,}'.format(get('greedy', 'no equals sign')).replace(',', ' '), RED, True)],
        [('.*?.*?=.*', INK, True), (str(get('lazy', 'short')), INK, False),
         (str(get('lazy', '20 x after =')), TEAL, True),
         ('{:,}'.format(get('lazy', 'no equals sign')).replace(',', ' '), RED, True)],
        [('.*=.*', INK, True), (str(get('rewritten', 'short')), INK, False),
         (str(get('rewritten', '20 x after =')), TEAL, True),
         (str(get('rewritten', 'no equals sign')), TEAL, True)],
    ]
    cols = [(64, 'la'), (250, 'la'), (470, 'la'), (720, 'la')]
    fig.text((64, y), '模式', 38, color=INK_SOFT, bold=True)
    fig.text((250, y), 'x=x', 38, color=INK_SOFT, bold=True)
    fig.text((470, y), 'x= + 20 个 x', 38, color=INK_SOFT, bold=True)
    fig.text((720, y), '20 个 x，无等号', 38, color=INK_SOFT, bold=True)
    y = table(fig, y + 62, cols, body, row_h=92)
    y = note(fig, y + 10, '惰性量词在能提前收工的输入上省一半（31 → 11 步），'
                          '但在注定失败的输入上一分钱都省不下来（5775 → 5775）。')
    y = note(fig, y, '真正省事的是把两个 .* 改成一个：848 → 111，5775 → 693。')
    y = note(fig, y, '为什么少一个 .* 就便宜这么多：多一个 .* 就是多一层「切成两段」的自由，'
                     '而每一层都要把所有切法试一遍。')
    save(fig, '07-rewrites.png', '贪婪、惰性与改写后的步数对比')


# ---------------------------------------------------------------- 图 08

def fig08():
    tr = R['pike_threads']['ab*c']
    fig, y = new(8, 'NFA 每读一个字符，手里同时有几个状态',
                 '模式 ab*c，文本 abbbc。柱子是每一步线程表里活着的状态数。')
    text = tr['text']
    widths = tr['widths']
    x0 = 120
    step = 168
    base = y + 420
    top = y + 60
    for i, (pos, w) in enumerate(widths):
        h = min(w / 3.0, 1.0) * (base - top)
        x = x0 + i * step
        fig.rect(x, base - max(h, 8), x + 96, base, fill=TINT_T if w == 1 else TINT_B,
                 outline=TEAL if w == 1 else BLUE, radius=10)
        fig.text((x + 48, base - max(h, 8) - 44), str(w), 44, bold=True,
                 color=TEAL if w == 1 else BLUE, anchor='ma')
        mono(fig, (x + 48, base + 16), text[i] if i < len(text) else '—', 44,
             anchor='ma', color=INK)
        fig.text((x + 48, base + 76), '位置 %d' % pos, 38, color=GRAY, anchor='ma')
    fig.line((x0 - 20, base), (x0 + 5 * step, base), color=INK, width=3)
    y = note(fig, base + 130, '位置 0 刚起步，只有一个状态；读到第一个 b 之后，'
                              '「继续吃 b」和「准备收尾」同时挂着，线程表变宽。')
    y = note(fig, y, '回溯在同一时刻只有一条路，所以它不占这张表；'
                     '它把「同时」变成了「一个个试」。')
    save(fig, '08-pike-threads.png', 'NFA 模拟每一步的线程数')


# ---------------------------------------------------------------- 图 09

def fig09():
    rows = R['linear']['rows']
    fig, y = new(9, '把文本拉长一百倍，线性做法只慢一百倍',
                 '模式固定为 .*.*=.*，文本是 n 个 x，没有等号，注定失配。'
                 ' 回溯在这个规模上已经跑不完，只测到 n = 320。')
    body = []
    for r in rows:
        body.append([(str(r['n']), INK, False),
                     ('{:,}'.format(r['memo']).replace(',', ' '), TEAL, False),
                     ('{:,}'.format(r['pike']).replace(',', ' '), BLUE, False),
                     ('%.2f' % (r['memo'] / r['n']), GRAY, False),
                     ('%.2f' % (r['pike'] / r['n']), GRAY, False),
                     ('{:,}'.format(r['backtrack']).replace(',', ' ')
                      if 'backtrack' in r else '跑不完', RED, False)])
    cols = [(64, 'la'), (200, 'la'), (380, 'la'), (530, 'la'), (660, 'la'), (780, 'la')]
    fig.text((64, y), 'n', 38, color=INK_SOFT, bold=True)
    fig.text((200, y), '记忆化', 38, color=INK_SOFT, bold=True)
    fig.text((380, y), 'NFA', 38, color=INK_SOFT, bold=True)
    fig.text((530, y), '每字符', 38, color=INK_SOFT, bold=True)
    fig.text((660, y), '每字符', 38, color=INK_SOFT, bold=True)
    fig.text((780, y), '回溯', 38, color=INK_SOFT, bold=True)
    y = table(fig, y + 62, cols, body, row_h=80)
    y = note(fig, y + 6, '两列「每字符」从 5.25 和 8.25 慢慢收敛到 5.00 和 8.00：'
                         '长度翻 256 倍，单位成本基本不变，这才叫线性。')
    y = note(fig, y, '回溯那列：n = 1280 时要 1 055 140 485 步、85 秒，'
                     '所以这张表里干脆没测——它已经不属于「能测」的范围。')
    save(fig, '09-linear.png', '记忆化与 NFA 的步数随长度线性增长')


# ---------------------------------------------------------------- 图 10

def fig10():
    a = R['anchor']
    fig, y = new(10, '锚不锚定，差不差一个数量级',
                 '同一个模式、同样 20 个 x 的文本：^ 开头意味着只试一个起点，'
                 '不锚定就得把 21 个起点都试一遍。')
    base = y + 380
    rows = [('锚定在开头', a['anchored']['backtrack'], TEAL),
            ('不锚定，每个位置都试', a['unanchored']['backtrack'], RED)]
    ytop = y + 30
    for i, (lab, v, color) in enumerate(rows):
        yy = ytop + i * 130
        fig.text((70, yy + 4), lab, 42, color=INK)
        w = min(v / 6000.0, 1.0) * 720
        fig.rect(70, yy + 62, 70 + max(w, 8), yy + 122, fill=color, outline=None,
                 radius=10)
        fig.text((70 + max(w, 8) + 20, yy + 66), '{:,}'.format(v).replace(',', ' '),
                 42, bold=True, color=color)
    y = note(fig, ytop + 300,
             '多出来的部分是 21 个起点各自重跑一遍。回溯的代价按「起点数」乘上去，'
             'NFA 不用：它每读一个字符顺手把新起点加进线程表，'
             '所以两种情况下都是 165 步。')
    save(fig, '10-anchor.png', '锚定与不锚定的步数比较')


# ---------------------------------------------------------------- 图 11

def fig11():
    tr = R['memo_trace']
    visited = {(p, q) for p, q in tr['visited']}
    states, tlen = tr['states'], tr['text_len']
    fig, y = new(11, '记忆化记住了哪些格子',
                 '模式 .*.*=.* 编译成 %d 个状态，文本是 %d 个 x。'
                 ' 每个格子是「某个状态站在某个位置」，涂色的是真正访问过的 %d 个。'
                 % (states, tlen, tr['count']))
    x0, y0 = 96, y + 40
    cw, ch = 62, 58
    for pc in range(states):
        for pos in range(tlen + 1):
            hit = (pc, pos) in visited
            fig.rect(x0 + pos * cw, y0 + pc * ch,
                     x0 + pos * cw + cw - 6, y0 + pc * ch + ch - 6,
                     fill=TINT_B if hit else WHITE,
                     outline=BLUE if hit else LIGHT, width=2, radius=6)
    for pc in range(states):
        mono(fig, (x0 - 18, y0 + pc * ch + 8), 's%d' % pc, 38, color=GRAY,
             anchor='ra')
    for pos in (0, tlen // 2, tlen):
        fig.text((x0 + pos * cw + 24, y0 + states * ch + 14), str(pos), 38,
                 color=GRAY, anchor='ma')
    fig.text((x0 + (tlen + 1) * cw / 2, y0 + states * ch + 70), '文本里的位置',
             38, color=INK_SOFT, anchor='ma')
    grid_bottom = y0 + states * ch
    y = note(fig, grid_bottom + 130,
             '没有记忆化时，同一个格子会被不同的路径反复踩到；'
             '记住「我来过这里并且失败了」，第二次就直接跳过。')
    y = note(fig, y, '代价是这张表本身：格子数是状态数乘长度，%d × %d。'
                     % (states, tlen + 1))
    save(fig, '11-memo-grid.png', '记忆化引擎访问过的状态-位置格子')


# ---------------------------------------------------------------- 图 12

def fig12():
    rows = R['pattern_size']['rows']
    fig, y = new(12, '备选分支变多，NFA 的账单只是跟着变长',
                 '模式是 m 个 a0|a1|… 备选，文本固定 200 个 x 再加 a3，'
                 ' 所以匹配落在最后。')
    ytop = y + 20
    vmax = max(r['pike'] for r in rows)
    for i, r in enumerate(rows):
        yy = ytop + i * 96
        fig.text((70, yy + 8), 'm = %d' % r['m'], 40, color=INK)
        w = min(r['pike'] / vmax, 1.0) * 560
        fig.rect(280, yy, 280 + max(w, 8), yy + 58, fill=TINT_B, outline=BLUE,
                 radius=10)
        fig.text((286 + max(w, 8), yy + 6), '{:,}'.format(r['pike']).replace(',', ' '),
                 40, bold=True, color=BLUE)
        w2 = min(r['backtrack'] / vmax, 1.0) * 560
        fig.rect(280, yy + 60, 280 + max(w2, 8), yy + 74, fill=TINT_R, outline=None,
                 radius=4)
    fig.text((70, ytop + len(rows) * 96 + 4), '细条是回溯：这一组输入里它没占便宜，'
                                              '因为备选都短。',
             38, color=INK_SOFT)
    leg_y = ytop + len(rows) * 96 + 60
    legend(fig, leg_y, [(BLUE, 'NFA 步数'), (RED, '回溯步数')], x0=280, step=300)
    y = note(fig, leg_y + 60,
             'm 从 1 到 32，NFA 步数从 %d 涨到 %d：涨的就是「状态数」这一项，'
             % (rows[0]['pike'], rows[-1]['pike']))
    y = note(fig, y, '长度那一项没动，因为文本没变。')
    save(fig, '12-pattern-size.png', '备选分支数与 NFA 步数')


# ---------------------------------------------------------------- 图 13

def fig13():
    fig, y = new(13, '三种做法的账本',
                 '没有哪种做法全面更好，差别在「worst case 花多少」和「能表达什么」。')
    top = y + 10
    cols = [
        ('回溯', RED, ['最坏 2 的 n 次方', '内存：递归同样深',
                       '能写反向引用']),
        ('回溯 + 记忆化', TEAL, ['最坏 状态数 × 长度', '内存：要存一张表',
                                 '丢捕获与优先级']),
        ('NFA 模拟', BLUE, ['最坏 状态数 × 长度', '内存：只存状态',
                            '反向引用做不了']),
    ]
    w = (1014 - 48 - 2 * 16) / 3
    for i, (head, color, lines) in enumerate(cols):
        x0 = 48 + i * (w + 16)
        card(fig, 'c%d' % i, x0, top, x0 + w, top + 470, head, lines, color, size=38)
    y = note(fig, top + 520, '表里的「状态数」就是模式编译出来的小程序长度，'
                             '对 .*.*=.* 是 8。')
    y = note(fig, y, '反向引用（\\1）让语言不再是正则语言，'
                     '所以它和线性时间这两个好处不能同时拿。')
    save(fig, '13-ledger.png', '三种做法的代价与能力对照')


# ---------------------------------------------------------------- 图 14

def fig14():
    fig, y = new(14, '这条路走了五十年',
                 'Thompson 1968 年的做法今天还在用，只是当年要手写汇编。')
    top = y + 40
    items = [
        ('1968', 'Thompson', 'CACM 11(6): 419–422 一篇论文', TEAL),
        ('2007', 'Cox', '同一套做法重新讲一遍，配可跑的实现', BLUE),
        ('2010s', 'RE2 · Go · Rust', '把线性引擎做成默认', GREEN),
    ]
    w = (1014 - 48 - 2 * 24) / 3
    for i, (year, who, what, color) in enumerate(items):
        x0 = 48 + i * (w + 24)
        name = 'b%d' % i
        fig.box(name, x0, top, x0 + w, top + 340, fill=WHITE, outline=color)
        fig.text((x0 + 20, top + 18), year, 44, bold=True, color=color, inside=name)
        y2 = top + 88
        y2 += int(fig.wrap((x0 + 20, y2), who, 38, w - 40, bold=True, color=INK,
                           inside=name) * 38 * 1.35) + 12
        fig.wrap((x0 + 20, y2), what, 38, w - 40, color=INK_SOFT, inside=name)
        if i < 2:
            fig.arrow((x0 + w + 4, top + 160), (x0 + w + 20, top + 160),
                      color=GRAY, width=4, head=12)
    y = note(fig, top + 390, '中间那一步很关键：算法早就有了，'
                             '但主流语言选择的还是回溯，因为回溯好写好改。')
    y = note(fig, y, '代价是用户输入一旦能左右模式匹配的路径，'
                     '程序的时间就不再由自己控制。')
    save(fig, '14-lineage.png', '线性正则引擎的五十年谱系')


# ---------------------------------------------------------------- 图 15

def fig15():
    src = ART / 'originals' / 'ken-thompson-dennis-ritchie-1973.jpg'
    im = Image.open(src).convert('RGB')
    w, h = im.size
    fig = Fig(900)
    fig.text((44, 26), '1968 年那篇论文的作者', 46, bold=True)
    fig.text((1018, 32), '图 15', 40, color=GRAY, anchor='ra')
    y0 = 128
    fx0 = 60
    fig.rect(fx0 - 10, y0 - 10, fx0 + w + 10, y0 + h + 10, fill=WHITE,
             outline=LIGHT, width=3)
    fig.im.paste(im, (fx0, y0))
    cap = y0 + h + 30
    n = fig.wrap((fx0, cap), 'Ken Thompson（左）与 Dennis Ritchie（右），1973 年',
                 38, 300, color=INK)
    fig.wrap((fx0, cap + n * 38 * 1.35 + 16),
             '公有领域，来源 Jargon File / Wikimedia Commons', 38, 300, color=GRAY)
    tx = 420
    tw = 1018 - tx
    fig.text((tx, y0 - 4), '1968', 46, bold=True, color=TEAL)
    y = y0 + 66
    y += int(fig.wrap((tx, y), 'Thompson 在 CACM 11 卷 6 期发表《Regular expression '
                               'search algorithm》，把正则匹配做成一次线性扫描。',
                      38, tw, color=INK) * 38 * 1.35) + 16
    y += int(fig.wrap((tx, y), '同一时期他给 ed 写了正则搜索，后来演化成 grep。',
                      38, tw, color=INK_SOFT) * 38 * 1.35) + 16
    fig.wrap((tx, y), '照片原尺寸 %d × %d，未放大。' % (w, h), 38, tw, color=GRAY)
    save(fig, '15-thompson.png', 'Ken Thompson 与 Dennis Ritchie 的 1973 年照片',
         identity='档案照片', source='https://commons.wikimedia.org/wiki/File:'
                                    'Ken_Thompson_and_Dennis_Ritchie--1973.jpg')


# ---------------------------------------------------------------- 图 16

def fig16():
    fig, y = new(16, '今天的引擎各走哪条路',
                 '同一门语言里也可能两种都有；这里说的是各自主文档写明的默认实现。')
    body = [
        [('Go  regexp', INK, True), ('NFA 模拟', BLUE, False), ('线性', GREEN, True)],
        [('Rust  regex', INK, True), ('NFA 模拟', BLUE, False), ('O(m·n)', GREEN, True)],
        [('Python  re', INK, True), ('回溯', RED, False), ('指数', RED, True)],
        [('Java  Pattern', INK, True), ('回溯', RED, False), ('指数', RED, True)],
        [('Perl · PHP · Ruby', INK, True), ('回溯', RED, False), ('指数', RED, True)],
    ]
    cols = [(64, 'la'), (470, 'la'), (790, 'la')]
    fig.text((64, y), '引擎', 38, color=INK_SOFT, bold=True)
    fig.text((470, y), '做法', 38, color=INK_SOFT, bold=True)
    fig.text((790, y), '最坏情况', 38, color=INK_SOFT, bold=True)
    y = table(fig, y + 62, cols, body, row_h=88)
    y = note(fig, y + 6, 'Go 的文档把「线性」写成了保证，Rust 写的是 O(m·n) 并提醒'
                          'm 会随模式变大；Python 从 3.11 起支持原子组和占有量词，'
                          '但引擎还是回溯。')
    y = note(fig, y, '最后一行那份名单来自 Cox 2007 的标题：他点名的就是这几个。')
    save(fig, '16-engines.png', '主流正则引擎的实现与最坏情况')


# ---------------------------------------------------------------- 图 17

def fig17():
    fig, y = new(17, '2019 年 7 月 2 日，27 分钟',
                 '一条 WAF 规则的改动，把全球每个 PoP 的 CPU 打满。'
                 ' 时间取自 Cloudflare 事后复盘，UTC。')
    top = y + 40
    axis_y = top + 150
    events = [
        ('13:42', '规则上线', AMBER),
        ('13:45', '告警', RED),
        ('14:00', '定位 WAF', AMBER),
        ('14:02', '提议关停', TEAL),
        ('14:07', '执行关停', TEAL),
        ('14:09', '恢复', GREEN),
    ]
    x0, x1 = 96, 972
    fig.line((x0, axis_y), (x1, axis_y), color=INK, width=4)
    step = (x1 - x0) / (len(events) - 1)
    for i, (t, what, color) in enumerate(events):
        x = x0 + i * step
        fig.circle(x, axis_y, 14, fill=color, outline=color)
        fig.text((x, axis_y - 62), t, 42, bold=True, color=color, anchor='ma')
        yy = axis_y + 46 if i % 2 == 0 else axis_y + 130
        fig.line((x, axis_y + (20 if i % 2 == 0 else -20)), (x, yy), color=LIGHT,
                 width=3)
        fig.text((x, yy), what, 40, bold=True, color=INK,
                 anchor='ma' if i < len(events) - 1 else 'ra')
    y = bullets(fig, axis_y + 210, [
        '13:42 一条 XSS 检测规则经自动流程上线，变更单也是自动开的。',
        '13:45 WAF 自检失败，全球流量掉到 20%。',
        '14:00 CPU 数据与 strace 一起把矛头指向 WAF。',
        '14:07 执行全局关停，14:09 流量与 CPU 回到正常。',
    ], accent=AMBER, size=40)
    y = note(fig, y + 10, '复盘里最扎人的一句是：想关掉 WAF，得先登录内部系统，'
                          '而那个系统正跑在 Cloudflare 上。')
    y = note(fig, y, '一条正则只是引信；真正让事故拖长的是「救火的路也要经过火场」。')
    save(fig, '17-timeline.png', 'Cloudflare 2019 年 7 月 2 日事故时间线')


# ---------------------------------------------------------------- 图 18

def fig18():
    fig, y = new(18, '事故规则里最贵的一小段',
                 '原始规则是一长串 XSS 特征，尾巴上挂着这一截。'
                 ' 关键不是整条式子，是里面的 .*(?:.*=.*)。')
    lines = [
        r'(?:(?:"|\'|\]|\}|\\|\d|(?:nan|infinity',
        r'   |true|false|null|undefined|symbol|math)',
        r'   |`|-|\+)+[)]*;?((?:\s|-|~|!|{}|\|\||',
        r'   \+)*.*(?:.*=.*)))',
    ]
    f = ImageFont.truetype(MONO_PATH, 38, index=0)
    x0 = 52
    y += 16
    for i, ln in enumerate(lines):
        mono(fig, (x0, y + i * 56), ln, 38)
    tail = lines[-1]
    lead = tail.index('.*(?:')
    bx0 = x0 + f.getlength(tail[:lead])
    bx1 = x0 + f.getlength(tail)
    ly = y + (len(lines) - 1) * 56
    fig.rect(bx0 - 10, ly - 12, bx1 + 10, ly + 50, fill=None, outline=RED,
             width=4, radius=8)
    fig.text((x0, ly + 76), '红框里那一段，化简后就是 .*.*=.*', 40, color=RED)

    yy = ly + 168
    steps = [
        '第一个 .* 贪婪：一口气吞掉整串 x=x。',
        '后面还有东西要匹配，只好退回一个字符再试。',
        '第二个 .* 每次都从头扫剩下的部分。',
        '两件事叠起来：外层退 n 次，内层扫 n 次。',
    ]
    for s_ in steps:
        fig.circle(80, yy + 22, 12, fill=RED, outline=RED)
        fig.text((116, yy), s_, 40, color=INK)
        yy += 66
    yy = note(fig, yy + 10, '写成通式：外层每退一步，内层就要重扫一遍剩下的文本，'
                            '于是步数按长度平方涨。')
    mono(fig, (x0, yy + 10), '.*.*=.*   →   .*=.*', 40, color=TEAL)
    yy = note(fig, yy + 86, '少一个 .* 就少一层切分，代价从平方降到线性——'
                            '这才是这段正则的正经修法。')
    save(fig, '18-regex-shape.png', '事故正则的关键片段与其代价')


# ---------------------------------------------------------------- 图 19

def fig19():
    fig, y = new(19, '所以，遇到慢正则怎么办',
                 '四条能立刻用上的做法，按「先做什么」排序。')
    y = bullets(fig, y + 10, [
        '先量：把可疑模式拿到最坏输入上跑一遍，看步数是不是随长度爆炸。',
        '再改模式：能合并的量词就合并，.*.* 写成 .*，嵌套量词尽量拆平。',
        '换引擎：不可信输入交给线性引擎（Go regexp、Rust regex、RE2）。',
        '兜底：给匹配设时间预算或先截断输入，别让一次匹配决定整个请求的生死。',
    ], accent=TEAL)
    y = note(fig, y + 20, '一条实用判据：如果模式来自用户，输入也来自用户，'
                          '那就别让回溯引擎碰它。')
    save(fig, '19-takeaways.png', '四条可执行的做法')


# ---------------------------------------------------------------- 封面

def cover():
    cf = R['cloudflare']
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill=BG, outline=None)
    fig.text((70, 64), '一条正则', 100, bold=True, color=INK)
    fig.text((70, 182), '怎么把 CPU 吃光', 100, bold=True, color=INK)
    fig.text((74, 300), '回溯、NFA，与 2019 年那 27 分钟', 44, color=INK_SOFT)
    mono(fig, (74, 400), '.*.*=.*', 84, color=RED)
    fig.text((74, 540), '在 20 个 x 上，回溯引擎走了', 42, color=INK)
    fig.text((74, 606), '{:,} 步'.format(cf['fail']['backtrack']),
             90, bold=True, color=RED)
    fig.text((74, 740), '换成同时推进的 NFA：{} 步'.format(cf['fail']['pike']),
             42, color=TEAL)
    fig.text((74, 960), '2027-02-01 · 原创 · CC BY 4.0', 40, color=GRAY)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png', optimize=True)
    (ASSETS / 'cover.png').unlink(missing_ok=True)
    print('   cover.png', (ART / 'cover.png').stat().st_size, 'bytes')


def main():
    for i in range(1, 20):
        globals()['fig%02d' % i]()
    META.sort(key=lambda r: r['path'])
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, indent=1, ensure_ascii=False) + '\n')
    print('figures:', len(META))
    cover()


if __name__ == '__main__':
    main()
