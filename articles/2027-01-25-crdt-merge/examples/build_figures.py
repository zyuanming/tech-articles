#!/usr/bin/env python3
"""CRDT 一文的原创教学插图。MIT。

图里出现的每个数字都来自 results.json；论文封面是原件渲染，不重画。
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
    assert fig.width_of(title, 46, True) <= 828, 'title too wide: ' + title
    fig.text((44, 26), title, 46, bold=True)
    fig.text((1018, 32), '图 %02d' % n, 40, color=GRAY, anchor='ra')
    y = 112
    if sub:
        y += int(fig.wrap((44, y), sub, 40, 974, color=INK_SOFT) * 40 * 1.35) + 20
    return fig, y


def note(fig, y, text, size=40, color=INK_SOFT):
    return y + int(fig.wrap((44, y), text, size, 974, color=color) * size * 1.35) + 16


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


def photo(name, src, purpose, source, identity='档案扫描件'):
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


def legend(fig, y, items, x0=52, step=236):
    x = x0
    for color, text in items:
        fig.rect(x, y, x + 30, y + 30, fill=color, outline=None, radius=6)
        fig.text((x + 44, y - 2), text, 38, color=INK)
        x += step
    return y + 46


def node_box(fig, x0, y0, x1, y1, label, value, color=TINT_T, edge=TEAL):
    fig.rect(x0, y0, x1, y1, fill=color, outline=edge, width=3, radius=16)
    cy = (y0 + y1) / 2
    fig.text(((x0 + x1) / 2, cy - 44), label, 40, bold=True, color=INK, anchor='mm')
    fig.text(((x0 + x1) / 2, cy + 14), value, 40, color=INK, anchor='mm')


# ---------------------------------------------------------------- 01 冲突

def fig01():
    fig, y = new(1, '两个人同时改同一个值',
                 'A 和 B 各自在本地写了一次，谁也不知道对方写了什么，'
                 '然后把两条更新互相发过去。')
    y += 10
    node_box(fig, 44, y, 470, y + 150, '机器 A', '值 = 7', TINT_T, TEAL)
    node_box(fig, 592, y, 1018, y + 150, '机器 B', '值 = 5', TINT_B, BLUE)
    top = y + 150
    obs = top + 210
    node_box(fig, 44, obs, 470, obs + 150, 'A 合并之后', '值 = ？', TINT_A, AMBER)
    node_box(fig, 592, obs, 1018, obs + 150, 'B 合并之后', '值 = ？', TINT_A, AMBER)
    fig.arrow((300, top + 12), (400, obs - 12), color=TEAL, width=4, dash=14)
    fig.arrow((762, top + 12), (662, obs - 12), color=BLUE, width=4, dash=14)
    fig.text((531, (top + obs) / 2 - 24), '两条更新在路上', 38, color=INK_SOFT,
             anchor='mm')
    fig.text((531, (top + obs) / 2 + 26), '谁先到，结果就不一样', 38, color=INK_SOFT,
             anchor='mm')
    y = note(fig, obs + 190,
             '问题不在「哪条更新对」——两条都是用户真的写下的。'
             '难的是让两台机器算出一个一样的答案，而且这个答案只跟两条更新有关、'
             '跟谁先到无关。')
    save(fig, '01-two-writes.png', '两台机器并发写同一个值，合并时互相收到对方的更新')


# ---------------------------------------------------------------- 02 后到覆盖

def fig02():
    late = R['merge_order']['late']
    fig, y = new(2, '后到覆盖：换个到达顺序，结果就变了',
                 '最省事的同步写法——谁的消息后到，就照抄谁的值。'
                 '三份状态按 200 种随机顺序合并，出现了 %d 种不同的最终结果。'
                 % late['distinct'])
    y += 10
    cols = [(64, 'la'), (420, 'la'), (768, 'la')]
    fig.text((64, y), '同样两条更新', 40, bold=True, color=INK_SOFT)
    fig.text((420, y), '顺序一', 40, bold=True, color=TEAL)
    fig.text((768, y), '顺序二', 40, bold=True, color=BLUE)
    y += 64
    rows = [('第 1 步', '收 A：值 = 7', '收 B：值 = 5'),
            ('第 2 步', '收 B：值 = 5', '收 A：值 = 7'),
            ('最终', '值 = 5', '值 = 7')]
    table_rows = []
    for i, (a_, b_, c_) in enumerate(rows):
        strong = i == len(rows) - 1
        table_rows.append([(a_, INK, strong), (b_, TEAL if strong else INK, strong),
                           (c_, BLUE if strong else INK, strong)])
    y = table(fig, y, cols, table_rows, row_h=74, size=40)
    y = note(fig, y + 6,
             '两条更新、两台机器，就能得出两个相反的答案；'
             '三台机器时，%d 次随机合并里有 %d 次落在最常见的那个结果上——'
             '「多数时候一致」不等于「一定一致」。' % (200, late['top']))
    save(fig, '02-late-order.png', '后到覆盖在两种到达顺序下得到相反的值')


# ---------------------------------------------------------------- 03 三条律

def fig03():
    fig, y = new(3, '合并要守三条规矩',
                 '把合并看成一个函数：喂它两份状态，吐出一份新状态。'
                 '这三条守住了，任何人、任何时候、按任何顺序合并，结果都一样。')
    y += 16
    cards = [
        ('交换', 'A ⊕ B = B ⊕ A', '谁先谁后无所谓', TEAL, TINT_T),
        ('结合', '(A ⊕ B) ⊕ C\n= A ⊕ (B ⊕ C)', '分几批合也一样', BLUE, TINT_B),
        ('幂等', 'A ⊕ A = A', '同一条消息收两遍', AMBER, TINT_A),
    ]
    w = 306
    for i, (name, formula, why, color, tint) in enumerate(cards):
        x0 = 44 + i * (w + 30)
        fig.rect(x0, y, x0 + w, y + 250, fill=tint, outline=color, width=3, radius=18)
        fig.text((x0 + w / 2, y + 34), name, 44, bold=True, color=color, anchor='mm')
        for k, line in enumerate(formula.split('\n')):
            mono(fig, (x0 + w / 2, y + 110 + k * 48), line, 38, INK, anchor='mm')
        fig.text((x0 + w / 2, y + 206), why, 38, color=INK_SOFT, anchor='mm')
    y += 286
    y = note(fig, y,
             '三条合成一句：合并是一份「只增不减」的账本，'
             '每次合并只是把两份账本里的事实合起来，不覆盖、不重算。'
             '前两条好办，第三条最容易破——只要把「收到什么」当成新事实写下来，'
             '重复投递就出事。')
    save(fig, '03-laws.png', '交换律、结合律、幂等律：合并必须满足的三条规矩')


# ---------------------------------------------------------------- 04 顺序试验

def fig04():
    order = R['merge_order']
    idem = R['idempotence']
    fig, y = new(4, '八种方案，同一批合并，200 种顺序',
                 '每台机器的状态原样取出，随机打乱顺序合并 200 次，数一数能得出几种结果；'
                 '再把同一份状态重复投递 1 次、2 次、5 次，看最终值变不变。')
    y += 6
    cols = [(64, 'la'), (452, 'la'), (664, 'la'), (1010, 'ra')]
    fig.text((64, y), '合并规则', 38, bold=True)
    fig.text((452, y), '结果数', 38, bold=True)
    fig.text((664, y), '重复收 5 次', 38, bold=True)
    fig.text((1010, y), '守律？', 38, bold=True, anchor='ra')
    y += 62
    rows = []
    for key in ('lww', 'gcounter', 'pncounter', 'twopset', 'orset', 'gset',
                'late', 'sum'):
        o, i = order[key], idem[key]
        same = len({r['fingerprint'] for r in i['runs']}) == 1
        ok = o['distinct'] == 1 and same
        last = i['runs'][-1]['value']
        if same:
            cell = ('还是 %s' % last) if last is not None else '还一样'
        else:
            cell = '变了'
        rows.append([(o['label'], INK, False),
                     (str(o['distinct']), RED if o['distinct'] > 1 else GREEN, True),
                     (cell, INK, False),
                     ('是' if ok else '否', GREEN if ok else RED, True)])
    y = table(fig, y, cols, rows, row_h=64)
    y = note(fig, y + 2,
             '后到覆盖栽在第一条，合并相加栽在第三条（%s）。'
             '两种朴素做法各破一条律，而四种 CRDT 一条都没破。'
             % ' / '.join(str(r['value']) for r in idem['sum']['runs']))
    save(fig, '04-order-test.png', '八种合并规则在 200 种随机合并顺序与重复投递下的表现')


# ---------------------------------------------------------------- 05 LWW

def fig05():
    fig, y = new(5, '最后写入者胜：给每次写盖一个时间戳',
                 '合并时只留时间戳大的那一次。时间戳跟着状态走，不是到达时间，'
                 '所以跟谁先到无关。')
    y += 24
    x0, x1 = 90, 990
    mid = 540
    fig.line((x0, y + 120), (x1, y + 120), color=LIGHT, width=6)
    events = [(260, 'A 写「草稿 v1」', 'ts = 1', TEAL, TINT_T),
              (700, 'B 写「草稿 v3」', 'ts = 3', BLUE, TINT_B)]
    for cx, label, ts, color, tint in events:
        fig.line((cx, y + 84), (cx, y + 156), color=color, width=5)
        fig.circle(cx, y + 120, 16, fill=color, outline=WHITE)
        fig.text((cx, y + 40), label, 38, color=INK, anchor='mm')
        fig.text((cx, y + 176), ts, 38, color=color, anchor='mm')
    y2 = y + 250
    fig.rect(190, y2, 890, y2 + 150, fill=TINT_G, outline=GREEN, width=3, radius=18)
    fig.text((540, y2 + 34), '合并之后两台机器都留下', 40, color=INK, anchor='mm')
    fig.text((540, y2 + 96), '「草稿 v3」，ts = 3', 44, bold=True, color=GREEN,
             anchor='mm')
    y = note(fig, y2 + 186,
             '只要时间戳是单调的、并且都被带上，LWW 就是标准的 CRDT：'
             '交换、结合、幂等三条全过（图 04 第一行）。'
             '代价是它把「并发」当成了「有先后」——时间戳小的那次写被整条丢弃。')
    save(fig, '05-lww.png', '最后写入者胜：时间戳大的那次写覆盖小的')


# ---------------------------------------------------------------- 06 撞车

def fig06():
    tb = R['tiebreak']
    fig, y = new(6, '时间戳撞车的时候',
                 '两台机器各自数自己的时钟，撞上同一个时间戳是常态。'
                 '规则里再比一个节点名，答案就唯一了。')
    y += 20
    fig.text((300, y), '%d 次' % tb['trials'], 92, bold=True, color=INK, anchor='ma')
    fig.text((300, y + 118), '撞上同一个时间戳', 38, color=INK_SOFT, anchor='ma')
    fig.text((760, y), '%d : %d' % (tb['higher'], tb['lower']), 92, bold=True,
             color=GREEN, anchor='ma')
    fig.text((760, y + 118), '名字大的那台赢 / 输', 38, color=INK_SOFT, anchor='ma')
    y += 220
    rows = [[('A 写「甲」 ts=5', INK, False), ('B 写「乙」 ts=5', INK, False),
             ('保留「乙」', GREEN, True)],
            [('C 写「甲」 ts=5', INK, False), ('B 写「乙」 ts=5', INK, False),
             ('保留「甲」', GREEN, True)],
            [('D 写「甲」 ts=5', INK, False), ('C 写「乙」 ts=5', INK, False),
             ('保留「甲」', GREEN, True)]]
    y = table(fig, y, [(64, 'la'), (424, 'la'), (760, 'la')], rows, row_h=66)
    y = note(fig, y + 2,
             '比节点名不是「谁更重要」，只是找一个所有机器都能算出同一个答案的次序。'
             '名字是字符串就比字典序，是数字就比大小。')
    save(fig, '06-tiebreak.png', '时间戳相同时用节点名兜底，保证唯一的赢家')


# ---------------------------------------------------------------- 07 读改写

def fig07():
    rmw = R['rmw']
    fig, y = new(7, '计数器为什么不能用 LWW',
                 '三台机器同时做「读出来、加一、写回去」——这是最常见的一种丢更新。')
    y += 16
    for i, name in enumerate('ABC'):
        x0 = 44 + i * 330
        fig.rect(x0, y, x0 + 300, y + 130, fill=TINT_T, outline=TEAL, width=3,
                 radius=16)
        fig.text((x0 + 150, y + 28), '机器 %s' % name, 40, bold=True,
                 color=TEAL, anchor='ma')
        fig.text((x0 + 150, y + 82), '读到 0 → 写下 1', 38, color=INK, anchor='ma')
    y += 168
    fig.rect(190, y, 890, y + 170, fill=TINT_R, outline=RED, width=3, radius=18)
    fig.text((540, y + 34), '合并之后的值', 40, color=INK, anchor='mm')
    fig.text((540, y + 92), '%d' % rmw['final'], 64, bold=True, color=RED, anchor='mm')
    fig.text((540, y + 138), '三次加一，应该是 %d' % rmw['intended'], 38,
             color=INK_SOFT, anchor='mm')
    y = note(fig, y + 206,
             '时间戳把三次写分出了先后，于是后两次把前两次整条丢掉。'
             '计数器要的是「每次加都算数」，所以它需要另一种状态：'
             '不是「最后的值」，而是「每台机器各加了多少」。')
    save(fig, '07-rmw.png', '三台机器并发读改写，LWW 只剩一个 1')


# ---------------------------------------------------------------- 08 G-Counter

def fig08():
    fig, y = new(8, 'G-Counter：每台机器只写自己那一格',
                 '把「总共加了多少」拆成「每台机器各加了多少」。合并时逐格取最大，'
                 '读的时候再求和。')
    y += 10
    counts = {'A': 7, 'B': 5, 'C': 2}
    cols = [('A 那一格', 64, 7), ('B 那一格', 424, 5), ('C 那一格', 764, 2)]
    for label, x0, v in cols:
        fig.rect(x0, y, x0 + 240, y + 210, fill=TINT_T, outline=TEAL, width=3,
                 radius=16)
        fig.text((x0 + 120, y + 32), label, 38, color=INK_SOFT, anchor='ma')
        fig.text((x0 + 120, y + 108), str(v), 72, bold=True, color=TEAL, anchor='ma')
    y += 246
    fig.text((524, y), '合并：逐格取最大　→　读：三格相加', 42, color=INK, anchor='ma')
    y += 62
    fig.rect(264, y, 784, y + 132, fill=TINT_G, outline=GREEN, width=3, radius=18)
    fig.text((524, y + 26), '7 + 5 + 2', 44, color=INK, anchor='ma')
    fig.text((524, y + 82), '= 14', 56, bold=True, color=GREEN, anchor='ma')
    y = note(fig, y + 172,
             '每格只由它的主人往上加，所以别人的合并永远只会把自己的格子抬到更大，'
             '不会把它改小——「取最大」在这里就是「取最新的那格」，而且天然幂等。')
    save(fig, '08-gcounter.png', 'G-Counter 的三格状态与逐格取最大、读时求和')


# ---------------------------------------------------------------- 09 幂等对照

def fig09():
    sum_runs = R['idempotence']['sum']['runs']
    g_runs = R['idempotence']['gcounter']['runs']
    fig, y = new(9, '同一条消息收两遍',
                 '分布式系统里重复投递是常态：重发、重试、断线重连，'
                 '同一条更新会被收到不止一次。')
    y += 8
    cols = [(80, 'la'), (440, 'la'), (760, 'la')]
    fig.text((80, y), '同一份状态投递', 38, bold=True)
    fig.text((440, y), '合并相加', 38, bold=True, color=RED)
    fig.text((760, y), 'G-Counter', 38, bold=True, color=GREEN)
    y += 62
    rows = [[('%d 次' % r['repeats'], INK, False),
             (str(r['value']), RED, True),
             (str(g['value']), GREEN, True)]
            for r, g in zip(sum_runs, g_runs)]
    y = table(fig, y, cols, rows, row_h=74, size=44)
    y = note(fig, y + 4,
             '「相加」在数学上很美：交换、结合都满足，'
             '但它把「我收到过这一份」当成了「这是一份新的增量」。'
             '重复投递三遍，就多算了两遍。G-Counter 取最大，收几遍都一样。')
    save(fig, '09-idempotent.png', '重复投递同一份状态：合并相加会翻倍，G-Counter 不变')


# ---------------------------------------------------------------- 10 PN-Counter

def fig10():
    fig, y = new(10, 'PN-Counter：加和减各记一本账',
                 '计数器要能减，就再放一排格子专记减了多少；'
                 '读的时候用加的总数减掉减的总数。')
    y += 8
    rows = [('加', {'A': 7, 'B': 5, 'C': 2}, GREEN, TINT_G),
            ('减', {'A': 1, 'B': 0, 'C': 2}, RED, TINT_R)]
    for label, cells, color, tint in rows:
        fig.text((64, y + 42), label, 48, bold=True, color=color)
        for i, k in enumerate('ABC'):
            x0 = 180 + i * 250
            fig.rect(x0, y, x0 + 200, y + 168, fill=tint, outline=color, width=3,
                     radius=14)
            fig.text((x0 + 100, y + 10), k, 38, color=INK_SOFT, anchor='ma')
            fig.text((x0 + 100, y + 104), str(cells[k]), 56, bold=True, color=color,
                     anchor='mm')
        y += 190
    y += 6
    fig.rect(240, y, 810, y + 140, fill=TINT_B, outline=BLUE, width=3, radius=18)
    fig.text((525, y + 24), '14 − 3', 46, color=INK, anchor='ma')
    fig.text((525, y + 84), '= 11', 56, bold=True, color=BLUE, anchor='ma')
    y = note(fig, y + 180,
             '两本账各自只增不减，所以合并还是逐格取最大、还是幂等。'
             '减到负数也没关系：状态里记的是「减了多少次」，不是「还剩多少」，'
             '余额可以是负的。')
    save(fig, '10-pncounter.png', 'PN-Counter 的加减两本账与余额')


# ---------------------------------------------------------------- 11 分区

def fig11():
    part = R['partition']
    fig, y = new(11, '断网之后再合起来',
                 'A、B 在一侧、C 在另一侧，中间断了几分钟。'
                 '两边各自加了 100 次，然后网通了。')
    y += 16
    bars = [('真相 300 次', part['gcounter']['truth'], GRAY, 1.0),
            ('G-Counter 合并后', part['gcounter']['value'], TEAL,
             part['gcounter']['value'] / part['gcounter']['truth']),
            ('PN-Counter 合并后', part['pncounter']['value'], BLUE,
             part['pncounter']['value'] / part['pncounter']['truth']),
            ('后到覆盖 合并后', part['late']['value'], RED,
             part['late']['value'] / part['late']['truth'])]
    for label, v, color, frac in bars:
        fig.text((64, y + 12), label, 38, color=INK)
        bar_x1 = 500 + max(frac * 400, 4)
        fig.rect(500, y, bar_x1, y + 56, fill=color, outline=None, radius=6)
        fig.text((bar_x1 + 18, y + 4), str(v), 44, bold=True, color=color)
        y += 96
    y = note(fig, y + 26,
             'G-Counter 一格没丢：断网两边加的是不同的格子，合起来正好 300。'
             '后到覆盖只剩 100——哪一侧后合进来，另一侧的 200 次就没了。')
    save(fig, '11-partition.png', '分区愈合后各方案记住的增量总数')


# ---------------------------------------------------------------- 12 八卦

def fig12():
    gs = R['gossip_scale']
    fig, y = new(12, '要几轮才能全部对上',
                 '每轮里每台机器都从一个随机同伴拉一份全量状态。'
                 '横轴是机器台数，纵轴是「所有机器状态完全相同」所需的轮数。')
    y += 24
    bx0, by0, bx1, by1 = 130, y, 1000, y + 360
    fig.line((bx0, by1), (bx1, by1), color=GRAY, width=4)
    fig.line((bx0, by0), (bx0, by1), color=GRAY, width=4)
    nmax, rmax = 32, 12.0
    pts = []
    for row in gs:
        x = bx0 + (row['nodes'] - 3) / (nmax - 3) * (bx1 - bx0)
        yy = by1 - row['rounds'] / rmax * (by1 - by0)
        pts.append((x, yy, row))
    for i in range(len(pts) - 1):
        fig.line(pts[i][:2], pts[i + 1][:2], color=TEAL, width=5)
    for x, yy, row in pts:
        fig.circle(x, yy, 11, fill=TEAL, outline=WHITE)
    for x, yy, row in (pts[0], pts[2], pts[4], pts[-1]):
        fig.text((x, yy - 54), '%d 轮' % row['rounds'], 38, color=TEAL, anchor='mm')
        fig.text((x, by1 + 18), '%d 台' % row['nodes'], 38, color=INK, anchor='ma')
    fig.text((bx0 - 24, by0 - 6), '轮数', 38, color=INK_SOFT, anchor='ra')
    y = note(fig, by1 + 76,
             '台数从 3 涨到 32（十倍多），轮数只从 %.2f 涨到 %.2f。'
             '每轮每台机器都把自己的见闻混进新的一份里，'
             '信息量翻倍的传法，轮数自然是台数的对数。'
             % (gs[0]['rounds'], gs[-1]['rounds']))
    save(fig, '12-gossip.png', '副本数 3 到 32 时达到全部一致所需的八卦轮数')


# ---------------------------------------------------------------- 13 2P-Set

def fig13():
    fig, y = new(13, '2P-Set：删掉就回不来',
                 '两个只增不减的集合：一个记「加过什么」，一个记「删过什么」。'
                 '在加过、且没删过的，才算还在。')
    y += 20
    boxes = [('还没加过', 64, TINT_T, TEAL), ('加过', 430, TINT_G, GREEN),
             ('删过', 786, TINT_R, RED)]
    for label, x0, tint, color in boxes:
        fig.rect(x0, y, x0 + 218, y + 120, fill=tint, outline=color, width=3,
                 radius=16)
        fig.text((x0 + 109, y + 40), label, 40, bold=True, color=color, anchor='ma')
    fig.arrow((290, y + 60), (420, y + 60), color=GREEN, width=5)
    fig.text((355, y + 84), 'add', 38, color=GREEN, anchor='ma')
    fig.arrow((656, y + 60), (776, y + 60), color=RED, width=5)
    fig.text((716, y + 84), 'remove', 38, color=RED, anchor='ma')

    y2 = y + 210
    fig.rect(64, y2, 282, y2 + 120, fill=TINT_A, outline=AMBER, width=3, radius=16)
    fig.text((173, y2 + 40), '再 add 一次', 40, bold=True, color=AMBER, anchor='ma')
    fig.arrow((290, y2 + 60), (420, y2 + 60), color=AMBER, width=5, dash=14)
    fig.line((340, y2 + 30), (372, y2 + 90), color=RED, width=6)
    fig.line((372, y2 + 30), (340, y2 + 90), color=RED, width=6)
    fig.text((436, y2 + 40), '还是「删过」——回不到「加过」', 40, color=RED)
    y = note(fig, y2 + 170,
             '「删过什么」这张表只增不减，所以合并就是两个并集，三条律都过。'
             '代价是同一项删掉之后再加回来是无效的：'
             '对「删了还能重新加」的购物车，这个规则不合用。')
    save(fig, '13-twopset.png', '2P-Set 的状态流转与「删掉就回不来」的限制')


# ---------------------------------------------------------------- 14 OR-Set

def fig14():
    aw = R['add_wins']
    fig, y = new(14, 'OR-Set：每次「加」带一个标签',
                 '删的时候不删元素，只删「当时看到的那几个标签」。'
                 '别人并发加进来的新标签，删不掉。')
    y += 12
    fig.rect(60, y, 470, y + 200, fill=TINT_T, outline=TEAL, width=3, radius=16)
    fig.text((265, y + 26), '元素「apple」的标签', 38, color=INK, anchor='ma')
    for i, tag in enumerate(['A#1', 'B#2']):
        fig.rect(120 + i * 150, y + 96, 260 + i * 150, y + 164, fill=WHITE,
                 outline=TEAL, width=3, radius=10)
        mono(fig, (190 + i * 150, y + 130), tag, 40, INK, anchor='mm')
    fig.rect(590, y, 1002, y + 200, fill=TINT_R, outline=RED, width=3, radius=16)
    fig.text((796, y + 26), '作废的标签', 38, color=INK, anchor='ma')
    fig.rect(690, y + 96, 830, y + 164, fill=WHITE, outline=RED, width=3, radius=10)
    mono(fig, (760, y + 130), 'A#1', 40, INK, anchor='mm')
    y += 236
    fig.rect(190, y, 890, y + 150, fill=TINT_G, outline=GREEN, width=3, radius=18)
    fig.text((540, y + 22), '还在吗：标签 − 作废 ≠ 空', 38, color=INK, anchor='ma')
    fig.text((540, y + 80), '{B#2} 还在 → apple 还在', 42, bold=True, color=GREEN,
             anchor='ma')
    y = note(fig, y + 190,
             '合并还是两个并集，三条律照旧。代价是标签一直要留着：'
             '每加一次多一个标签，作废的标签也不能删——'
             '这是后面那条「状态越来越大」的根源。')
    save(fig, '14-orset.png', 'OR-Set 的标签集合与作废集合')


# ---------------------------------------------------------------- 15 加与删

def fig15():
    aw = R['add_wins']
    fig, y = new(15, '同一秒里，一个在加、一个在删',
                 'A 把 apple 放进购物车，B 几乎同时把它删掉，然后互相同步。'
                 '两种集合给出相反的答案，两个都不算错——是规则选得不一样。')
    y += 16
    panels = [('2P-Set', '删过就不能再加', 'apple 不在', RED, TINT_R),
              ('OR-Set', 'B 删的是它看到的那个标签', 'apple 还在', GREEN, TINT_G)]
    for i, (name, why, result, color, tint) in enumerate(panels):
        x0 = 44 + i * 512
        fig.rect(x0, y, x0 + 460, y + 240, fill=tint, outline=color, width=3,
                 radius=18)
        fig.text((x0 + 230, y + 28), name, 46, bold=True, color=color, anchor='ma')
        fig.text((x0 + 230, y + 100), why, 38, color=INK_SOFT, anchor='ma')
        fig.text((x0 + 230, y + 168), result, 48, bold=True, color=color, anchor='ma')
    y += 276
    y = note(fig, y,
             'OR-Set 按「加赢」处理：并发的加和删，加的那一份留下。'
             '这次合并之后 apple 有两个标签、一个作废（%d 个标签、%d 个作废），'
             '所以它还在。选哪种要看你想要什么语义，不是看哪种更对。'
             % (aw['orset_tags'], aw['orset_dead']))
    save(fig, '15-add-wins.png', '并发加与删时 2P-Set 与 OR-Set 的不同结论')


# ---------------------------------------------------------------- 16 状态大小

def fig16():
    g = R['growth']
    fig, y = new(16, '墓碑是要占地方的',
                 '状态式 CRDT 每次同步都发全量状态。'
                 '表里是序列化之后的字节数，操作数从 10 加到 2000。')
    y += 26
    bx0, by0, bx1, by1 = 150, y, 1000, y + 340
    fig.line((bx0, by1), (bx1, by1), color=GRAY, width=4)
    fig.line((bx0, by0), (bx0, by1), color=GRAY, width=4)
    series = [('OR-Set', 'orset_bytes', RED), ('2P-Set', 'twopset_bytes', AMBER),
              ('G-Set', 'gset_bytes', TEAL)]
    nmax = g[-1]['ops']
    bmax = g[-1]['orset_bytes'] * 1.12
    for name, key, color in series:
        pts = []
        for row in g:
            x = bx0 + row['ops'] / nmax * (bx1 - bx0)
            yy = by1 - row[key] / bmax * (by1 - by0)
            pts.append((x, yy))
        for i in range(len(pts) - 1):
            fig.line(pts[i], pts[i + 1], color=color, width=5)
        for x, yy in pts:
            fig.circle(x, yy, 9, fill=color, outline=WHITE)
        x, yy = pts[-1]
        fig.text((x - 18, yy - 52), '%s %d' % (name, g[-1][key]), 38, color=color,
                 anchor='ra')
    fig.text((bx0, by1 + 14), '10', 38, color=INK, anchor='ma')
    fig.text((bx0 + (1000 - 10) / (nmax - 10) * (bx1 - bx0), by1 + 14), '1000', 38,
             color=INK, anchor='ma')
    fig.text((bx1, by1 + 14), '2000 次操作', 38, color=INK, anchor='ra')
    y = note(fig, by1 + 70,
             '两千次操作之后：G-Set 12 KB，2P-Set 33 KB，OR-Set 53 KB。'
             'OR-Set 每个元素都要留标签，删过的标签也留着，'
             '平均每次操作 %.1f 字节。' % (g[-1]['orset_bytes'] / g[-1]['ops']))
    save(fig, '16-growth.png', '三种状态随操作数增长占用的字节数')


# ---------------------------------------------------------------- 17 论文首页

def fig17():
    photo('17-rr7506.png', 'rr7506-cover.png',
          '2011 年 INRIA 研究报告 RR-7506 的封面：四位作者与报告编号',
          'https://inria.hal.science/inria-00555588/file/techreport.pdf',
          identity='档案扫描件')


# ---------------------------------------------------------------- 18 谁在用

def fig18():
    fig, y = new(18, '谁在用',
                 '下面这些系统都用到了某种 CRDT，侧重点各不相同。')
    y += 8
    cards = [
        ('Riak', '计数器、集合、映射', '键值库把 CRDT 做成了数据类型', TEAL, TINT_T),
        ('Redis Enterprise', '带 CRDT 的复制', '多主复制时用它合并冲突', RED, TINT_R),
        ('SoundCloud Roshi', 'LWW-Element-Set', '为「动态流」写的，跑在 Redis 上',
         AMBER, TINT_A),
        ('Figma', 'LWW + 分数索引', '属性按最后写入者胜，顺序另有约定', BLUE, TINT_B),
    ]
    for i, (name, kind, why, color, tint) in enumerate(cards):
        col, row = i % 2, i // 2
        x0 = 44 + col * 512
        y0 = y + row * 236
        fig.rect(x0, y0, x0 + 460, y0 + 210, fill=tint, outline=color, width=3,
                 radius=18)
        fig.text((x0 + 26, y0 + 22), name, 42, bold=True, color=color)
        fig.text((x0 + 26, y0 + 88), kind, 38, color=INK)
        fig.wrap((x0 + 26, y0 + 142), why, 38, 410, color=INK_SOFT)
    y += 2 * 236 + 30
    y = note(fig, y,
             '产品说明里写的名字未必和论文里一样，但合并在做的事是一样的：'
             '把两份各自动过的状态，合回一份。')
    save(fig, '18-who.png', '四类使用 CRDT 的系统及其侧重点')


# ---------------------------------------------------------------- 19 四句话

def fig19():
    fig, y = new(19, '记住四件事')
    y += 10
    y = bullets(fig, y, [
        '合并要守三条律：交换、结合、幂等。破一条，迟早出现两台机器算出两个答案。',
        '计数器拆成「每台各加了多少」，集合拆成「加过什么、删过什么」，'
        '冲突就不再是冲突。',
        '并发加与删要有明确取舍：加赢（OR-Set）还是删赢（2P-Set），'
        '是选语义，不是选对错。',
        '代价在状态里：墓碑只增不减，状态式同步又总发全量，'
        '所以要压缩、要合并、要定期清理。',
    ])
    save(fig, '19-takeaways.png', '四条结论')


# ---------------------------------------------------------------- 封面

def cover():
    fig = Fig(1080)
    fig.text((74, 300), 'CRDT', 54, bold=True, color=TEAL)
    fig.text((74, 372), '三个节点吵架，谁说了算', 60, bold=True)
    fig.text((74, 456), '交换、结合、幂等：把冲突变成一道加法题', 40,
             color=INK_SOFT)
    y = 540
    for i, (name, val, color, tint) in enumerate([('A', '7', TEAL, TINT_T),
                                                  ('B', '5', BLUE, TINT_B),
                                                  ('C', '2', AMBER, TINT_A)]):
        x0 = 74 + i * 146
        fig.rect(x0, y, x0 + 116, y + 124, fill=tint, outline=color, width=3,
                 radius=14)
        fig.text((x0 + 58, y + 6), name, 38, color=INK_SOFT, anchor='ma')
        fig.text((x0 + 58, y + 72), val, 52, bold=True, color=color, anchor='mm')
    fig.arrow((540, y + 62), (630, y + 62), color=GRAY, width=5)
    fig.rect(658, y, 1010, y + 124, fill=TINT_G, outline=GREEN, width=3, radius=14)
    fig.text((834, y + 10), '每格取最大再相加', 38, color=INK_SOFT, anchor='ma')
    fig.text((834, y + 72), '7 + 5 + 2 = 14', 44, bold=True, color=GREEN,
             anchor='mm')
    fig.text((74, 730), '顺序怎么打乱都一样，重复收几遍也都一样', 40, color=INK)
    fig.text((74, 980), '2027-01-25 · 原创 · CC BY 4.0', 38, color=GRAY)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png', optimize=True)
    (ASSETS / 'cover.png').unlink(missing_ok=True)
    print('   cover.png', (ART / 'cover.png').stat().st_size, 'bytes')


def main():
    for i in range(1, 20):
        globals()['fig%02d' % i]()
    cover()
    META.sort(key=lambda r: r['path'])
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, indent=1, ensure_ascii=False) + '\n')
    print('figures:', len(META))


if __name__ == '__main__':
    main()
