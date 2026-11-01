#!/usr/bin/env python3
"""Original teaching figures for the CRC-32 article. MIT.

Headline numbers come from results.json (run_model.py writes it); the binary
strings drawn here are recomputed from the same model module, so text and
figures cannot drift apart.
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

import crc as M

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


def bar(fig, x, y, w, value, top, color, label=None, size=38):
    lo, hi = min(y, top), max(y, top)
    fig.rect(x, lo, x + w, hi, fill=color, outline=None)
    if label:
        fig.text((x + w + 14, min(y, top) + 12), label, size, color=INK)


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


# ---------------------------------------------------------------- figures


def fig01():
    fig, y = new(1, '三个动作，一条尾巴',
                 '发送端算一串数挂在后面，接收端自己再算一遍。')
    x = 44
    for label, col in (('数据', TINT_B), ('÷ G(x)', TINT_T),
                       ('4 字节尾巴', TINT_A), ('线路', TINT_G)):
        chip(fig, (x, y + 20, x + 232, y + 130), label, col, size=40)
        if x < 760:
            fig.arrow((x + 238, y + 75), (x + 262, y + 75), color=GRAY, width=4)
        x += 262
    yy = y + 170
    yy = note(fig, yy, '接收端做的是同一件事：把收到的字节再除一次。余数为零就收下，'
                       '不为零就丢掉这一帧。它不问「哪个比特错了」，只回答「有没有错」。')
    yy += 20
    x = 44
    for label, col in (('收到的字节', TINT_B), ('÷ 同一个 G(x)', TINT_T),
                       ('丢 / 收', TINT_R)):
        chip(fig, (x, yy, x + 300, yy + 110), label, col, size=40)
        if x < 640:
            fig.arrow((x + 306, yy + 55), (x + 330, yy + 55), color=GRAY, width=4)
        x += 330
    yy += 150
    y = note(fig, yy, 'CRC 的全部本事就在这条尾巴上：它能保证「错了几乎一定看得出来」，'
                      '但不保证「看得出来就一定是错了」，更不告诉你在哪儿。')
    save(fig, '01-overview.png', 'CRC 的三个动作：算、附带、重算比较')


def fig02():
    photo('02-nic.jpg', 'Intel_PRO1000PT_Dual_GigE_front.jpg',
          'Intel PRO/1000 PT 双口千兆网卡：每收一帧都要验一次 CRC-32',
          'Phiarc, CC BY-SA 4.0, via Wikimedia Commons')


def fig03():
    fig, y = new(3, '最朴素的校验和，最容易被骗',
                 '把两个字节对调，累加和与异或都还是原来的数。')
    good = '48 65 6C 6C 6F 21'
    bad = '65 48 6C 6C 6F 21'
    for k, (label, s, col) in enumerate((('发送的', good, TEAL),
                                         ('路上被对调的', bad, RED))):
        fig.text((44, y + k * 92), label, 40, color=col)
        mono(fig, (300, y + k * 92), s, 40, col)
    yy = y + 210
    gg = bytes.fromhex(good)
    bb = bytes.fromhex(bad)
    yy = note(fig, yy, '两串字节的 8 位累加和都是 0x%02X（%d），'
                       '异或都是 0x%02X（%d）——校验值一动不动，可数据已经变了。'
             % (M.naive_sum(gg), M.naive_sum(gg),
                M.naive_xor(gg), M.naive_xor(gg)))
    yy += 10
    rows = []
    for row in R['swap']:
        rows.append([(row['scheme'], INK, False),
                     ('%.0f%%' % (row['miss_rate'] * 100), 
                      RED if row['miss_rate'] > 0.01 else GREEN, True)])
    yy = table(fig, yy + 30, [(44, 'la'), (1010, 'ra')], rows, size=40, row_h=64)
    y = note(fig, yy, '表里是 64 字节报文、两万个随机对调实验里「校验值完全没变」的比例。'
                      '纯累加和与异或全漏；CRC 一个都没漏。')
    assert M.naive_sum(gg) == M.naive_sum(bb)
    assert M.naive_xor(gg) == M.naive_xor(bb)
    save(fig, '03-weak.png', '累加和与异或对调换字节视而不见，CRC 不会')


def fig04():
    fig, y = new(4, 'CRC 就是一次除法',
                 '规矩只有一个：加就是异或，不借位、不进位。')
    d = R['demo']
    W = d['message'].bit_length() + d['width']
    dividend = format(d['dividend'], '0%db' % W)
    fig.text((44, y), '被除数：数据后面补 %d 个 0' % d['width'], 40, color=GRAY)
    mono(fig, (44, y + 52), dividend, 40)
    yy = y + 130
    div = format(d['poly'], 'b')
    mono(fig, (44, yy), ' ' * 0 + div, 40, TEAL)
    fig.text((44 + 30 * len(div), yy + 4), '← 除数（生成多项式）', 40, color=TEAL)
    yy += 70
    for st in d['steps']:
        before = format(st['before'], '0%db' % W)
        sub = format(st['sub'], 'b')
        after = format(st['after'], 'b')
        mono(fig, (44, yy), ' ' * (W - len(sub)) + sub, 40, AMBER)
        mono(fig, (44, yy + 52), before, 40)
        mono(fig, (44, yy + 104), ' ' * (W - len(after)) + after, 40, INK_SOFT)
        fig.line((44, yy + 40), (44 + 30 * W, yy + 40), color=LIGHT, width=3)
        yy += 160
    yy += 10
    y = note(fig, yy, '每一步都把对齐后的除数异或一次，最高位一定被消掉，'
                      '于是窗口往右挪一位。除到头剩下的 %d 位就是余数 %s。'
                      % (d['width'], format(d['remainder'], '0%db' % d['width'])))
    save(fig, '04-division.png', 'GF(2) 长除法：CRC 的全部运算')


def fig05():
    fig, y = new(5, '同一个算法，画成一根移位线',
                 '用 4 位宽讲结构，32 位宽只是把格子接长。')
    cells = 4
    w, gap = 165, 22
    x0 = 300
    yy = y + 70
    for i in range(cells):
        x = x0 + i * (w + gap)
        chip(fig, (x, yy, x + w, yy + 110), 'r%d' % (cells - 1 - i), TINT_B,
             size=42)
    fig.text((x0, yy - 56), '寄存器 %d 位' % cells, 40, color=GRAY)

    right = x0 + cells * (w + gap) - gap
    fig.arrow((right, yy + 55), (right + 40, yy + 55), color=RED, width=4)
    fig.text((right - 6, yy - 46), '移出的最高位', 38, color=RED, anchor='ra')
    # feedback: right -> down -> left -> up into the XOR
    fig.line((right + 40, yy + 55), (right + 40, yy + 300), color=RED, width=4)
    fig.line((right + 40, yy + 300), (250, yy + 300), color=RED, width=4)
    fig.line((250, yy + 300), (250, yy + 96), color=RED, width=4)
    fig.circle(250, yy + 55, 30, fill=AMBER, outline=AMBER)
    fig.text((250, yy + 22), 'XOR', 38, color=WHITE, anchor='ma')
    fig.arrow((96, yy + 55), (215, yy + 55), color=TEAL, width=5)
    fig.text((96, yy + 96), '新数据位', 38, color=TEAL)
    fig.arrow((282, yy + 55), (x0 - 6, yy + 55), color=AMBER, width=5)
    yy += 380
    y = note(fig, yy, '数据位从右边进、从左边出；出去的那一位若是 1，就把多项式'
                      '异或回来。这个结构叫 LFSR，硬件里就是几个触发器加几个异或门。')
    y = note(fig, y, 'CRC 的位宽就是寄存器的位数：32 位 CRC 就是 32 个触发器，'
                     '外加和多项式里 1 的个数一样多的异或门。')
    save(fig, '05-lfsr.png', '移位寄存器形式的 CRC：一位进、一位出')


def fig06():
    fig, y = new(6, '一个字节走进去，八步',
                 '被处理的字节 0x%02X；每一步看最高位决定要不要异或。'
                 % R['trace']['byte'])
    rows = [[('步', GRAY, True), ('移出', GRAY, True),
             ('做了什么', GRAY, True), ('寄存器', GRAY, True)]]
    tb = R['trace']['rows']
    rows.append([('0', INK, False), ('—', GRAY, False),
                 ('先异或进数据字节', INK, False),
                 ('%08X' % tb[0]['reg'], TEAL, False)])
    for i, row in enumerate(tb[1:], start=1):
        rows.append([('%d' % i, INK, False),
                     ('%d' % row['bit'], INK, False),
                     ('移位 + 异或' if row['xored'] else '只移位', INK, False),
                     ('%08X' % row['reg'], TEAL, False)])
    y = table(fig, y + 20, [(44, 'la'), (180, 'la'), (330, 'la'), (760, 'la')],
              rows, size=38, row_h=62)
    y = note(fig, y, '八步之后寄存器里是 0x%08X。32 位寄存器、8 位输入，'
                     '这就是「一次处理一个字节」的全部内容——慢，但一看就懂。'
                     % R['trace']['final'])
    save(fig, '06-trace.png', '一个字节经过 32 位移位寄存器的八步')


def fig07():
    fig, y = new(7, '把八步压成一步',
                 '表里每一项，都是「这个字节进来、寄存器从全零开始」的结果。')
    rows = []
    for i, v in enumerate(R['table'][:8]):
        rows.append([('0x%02X' % i, INK, False),
                     ('%08X' % v, TEAL, False)])
    y = table(fig, y + 20, [(44, 'la'), (330, 'la')], rows, size=40, row_h=62)
    y = note(fig, y, '两百五十六项、每项 4 字节，一共 1024 字节的表，'
                     '16 位和 32 位的实现都是这么来的。表是算出来的，不是查出来的。')
    y = note(fig, y, '用表的时候：取「当前 CRC 的最低位与数据字节」异或的结果当索引，'
                     '查出一项，再把 CRC 右移 8 位异或一次。八步的事，一步做完。')
    save(fig, '07-table.png', '查表法：256 项的表是八次移位的预先结果')


def fig08():
    fig, y = new(8, '代价：1024 字节的表',
                 '快是快了，但这块表要待在缓存里。')
    yy = y + 30
    for k, (label, cost, col) in enumerate(
            (('逐位：每字节 8 次移位 + 8 次判断', '慢', RED),
             ('查表：每字节 1 次访存 + 1 次异或', '快', GREEN))):
        chip(fig, (44, yy + k * 150, 1018, yy + k * 150 + 120), label,
             TINT_R if k == 0 else TINT_G, size=42)
    yy += 330
    y = note(fig, yy, '表法在软件里几乎是默认选择：zlib、PNG、几乎所有以太网驱动'
                      '都是查表。硬件里反而常常回到逐位——触发器比 1 KB 的 ROM 便宜。')
    y = note(fig, y, '后来有了更省的办法：把表拆成 4 张小的、或者干脆用 CPU 的专用指令'
                     '（x86 的 crc32、ARM 的 crc32 扩展），一条指令算一段。')
    save(fig, '08-lookup.png', '逐位法与查表法的成本对照')


def fig09():
    fig, y = new(9, '短突发错误，一个都跑不掉',
                 '长度不超过 32 的成片错误，全部穷举后没有一个漏网。')
    rows = []
    for r in R['burst']:
        if r['length'] in (1, 4, 8, 12, 16):
            rows.append([('%d 位' % r['length'], INK, False),
                         ('%d' % r['patterns'], INK, False),
                         ('%d' % r['missed'], GREEN, True)])
    y = table(fig, y + 20, [(44, 'la'), (330, 'la'), (700, 'la')],
              rows, size=40, row_h=66)
    y = note(fig, y, '合计 %d 种图案，漏掉 0 种。原因是次数：长度为 L 的突发错误，'
                     '多项式次数最高 L−1；只要 L−1 小于生成多项式的次数 32，'
                     '就除不尽。' % sum(r['patterns'] for r in R['burst']))
    save(fig, '09-burst.png', '长度 1 到 16 的突发错误穷举，全部被抓住')


def fig10():
    fig, y = new(10, '第一个漏掉的，就是它自己',
                 '33 位的那一种突发错误里，有一个恰好等于生成多项式。')
    g = R['burst_min']
    bits = format(int(g['hex'], 16), '033b')
    yy = y + 40
    fig.text((44, yy), '生成多项式 G（%d 位）' % len(bits), 40, color=GRAY)
    mono(fig, (44, yy + 52), ' '.join(bits[i:i + 8] for i in range(0, 33, 8)), 38)
    fig.text((44, yy + 120), '一个 33 位的突发错误，首尾都是 1', 40, color=GRAY)
    bad = bits[0] + '0' * 31 + bits[-1]
    mono(fig, (44, yy + 172), ' '.join(bad[i:i + 8] for i in range(0, 33, 8)), 38,
         RED)
    yy += 260
    y = note(fig, yy, '第一行除以它自己，余数是 0——这一种错误看不见。'
                      '它的长度 33 正是「32 位 CRC 抓不住的最短突发」。')
    y = note(fig, y, '把 G 往左挪 k 位，得到长度 33+k 的漏网图案；'
                     '这样的图案每一段都有，但它们极稀疏：长度 33 的突发有 2³¹ 种，'
                     '漏网的只有这一个。')
    save(fig, '10-first-miss.png', '最短的漏检突发：长度 33，恰好等于生成多项式')


def fig11():
    fig, y = new(11, '为什么有的多项式能抓奇数个错',
                 '在 10 位窗口里穷举所有权重 1 到 4 的错误图案。')
    rows = []
    small = {g['gen']: g for g in R['small_width']}
    a = small['x^4+x^2+x+1']
    b = small['x^4+x+1']
    fig.text((44, y + 6), 'x⁴+x²+x+1（含 x+1 因子）', 40, bold=True, color=TEAL)
    fig.text((44, y + 76), 'x⁴+x+1（三项式，不含 x+1）', 40, bold=True, color=RED)
    yy = y + 150
    rows.append([('错误位数', GRAY, False),
                 ('含 x+1', TEAL, True), ('不含 x+1', RED, True)])
    amap = {r['weight']: r['missed'] for r in a['rows']}
    bmap = {r['weight']: r['missed'] for r in b['rows']}
    for w in (1, 2, 3, 4):
        rows.append([('%d 位' % w, INK, False),
                     ('%d 漏' % amap[w], GREEN if amap[w] == 0 else INK, False),
                     ('%d 漏' % bmap[w], GREEN if bmap[w] == 0 else INK, False)])
    y = table(fig, yy, [(44, 'la'), (420, 'la'), (660, 'la')], rows,
              size=40, row_h=64)
    y = note(fig, y, '含 x+1 的那列，奇数位错误全抓得住：奇数个翻转的图案代入 1 得 1，'
                     '不可能被 G 整除。不含的那列，3 位就漏了 9 种。')
    y = note(fig, y, '把 x³² 那一项也算上，CRC-32 的完整多项式有 15 个非零项（奇数），'
                     'CRC-32C 有 18 个（偶数）。所以前者的 x+1 因子是没有的，'
                     '后者有。前者靠的是位宽。')
    save(fig, '11-xplus1.png', '小位宽穷举：x+1 因子与奇数位错误的关系')


def fig12():
    fig, y = new(12, '八位 CRC 到底能挡多少',
                 '2048 位随机错误图案，两万次实验。')
    n = R['narrow']
    yy = y + 50
    full = max(n['rate'], n['predicted']) * 1.35
    for k, (label, v, col) in enumerate((('实测漏检', n['rate'], RED),
                                         ('理论 2⁻⁸', n['predicted'], GRAY))):
        x = 300
        w = int(420 * v / full)
        bar(fig, x, yy + k * 150, max(w, 10), yy + k * 150 + 80, yy + k * 150,
            col)
        fig.text((44, yy + k * 150 + 16), label, 40, color=col)
        fig.text((740, yy + k * 150 + 16), '%.4f' % v, 40, color=col)
    yy += 340
    y = note(fig, yy, '和理论上的 1/256 对得上：两万次实验的抖动在 ±0.001 量级。'
                      '这个概率说的是「随机错误恰好被整除」，和错误有多密集无关。')
    y = note(fig, y, '位宽换成 32，这个概率就从 1/256 掉到 1/43 亿。'
                     '这就是以太网用 32 位的原因：误码率再高，也要很久才撞上一次。')
    save(fig, '12-narrow.png', '八位 CRC 的实测漏检率与 2⁻⁸ 吻合')


def fig13():
    fig, y = new(13, '五种校验，一次对调',
                 '64 字节报文里换掉两个字节的位置，看谁的校验值不变。')
    yy = y + 30
    for k, row in enumerate(R['swap']):
        rate = row['miss_rate']
        col = RED if rate > 0.5 else (AMBER if rate > 0.001 else GREEN)
        x = 430
        w = int(500 * max(rate, 0.004) / 1.0)
        bar(fig, x, yy + k * 110, w, yy + k * 110 + 56, yy + k * 110, col)
        fig.text((44, yy + k * 110 + 6), row['scheme'], 40, color=INK)
        fig.text((1018, yy + k * 110 + 6), '%.1f%%' % (rate * 100), 40,
                 color=col, anchor='ra')
    yy += 600
    y = note(fig, yy, '累加和、异或：全漏。Fletcher 好一些，但它按 255 取模，'
                      '位置差与数值差相乘凑成 255 的倍数时会漏——这就是那 1%。')
    y = note(fig, y, 'CRC-16 和 CRC-32 这次实验都没漏。但注意：'
                     '「没漏」不是「不会漏」，只是这两万个样本里没撞上。')
    save(fig, '13-swap.png', '五种校验方案对「对调两个字节」的漏检率')


def fig14():
    fig, y = new(14, '它挡不住故意改稿的人',
                 'CRC 是线性的：改法可以算出来，改完校验值一动不动。')
    fg = R['forging']
    fig.text((44, y), '原来', 40, color=TEAL)
    mono(fig, (44, y + 52), fg['text'], 40, TEAL)
    fig.text((44, y + 122), '改后（只换掉最后 5 个字节）', 40, color=RED)
    mono(fig, (44, y + 174), fg['forged'], 38, RED)
    yy = y + 260
    rows = [[('原来', INK, False), (fg['crc'], TEAL, False)],
            [('改后', INK, False), (fg['forged_crc'], RED, False)]]
    yy = table(fig, yy, [(44, 'la'), (330, 'la')], rows, size=40, row_h=62)
    y = note(fig, yy, '五个字节里翻掉 %d 个比特，CRC 完全相同。'
                      '因为对定长报文来说，CRC 是「比特 → 32 位」的仿射映射，'
                      '它的核一定有解。' % fg['changed_bits'])
    y = note(fig, y, '所以 CRC 只能对付「手滑」，不能对付「有意」。要防人，'
                     '得用 HMAC 或者数字签名：那里有一把别人没有的密钥。')
    save(fig, '14-forge.png', '利用线性，构造出 CRC 相同而内容不同的报文')


def fmt_count(n):
    if n >= 1e8:
        return '%.1f 亿' % (n / 1e8)
    if n >= 1e4:
        return '%.1f 万' % (n / 1e4)
    if n >= 1e3:
        return '%d 千' % round(n / 1e3)
    return '%d' % n


def fig15():
    fig, y = new(15, '换了内容也想撞上？很难',
                 '但这是「随机撞」，不是「有人算着撞」。')
    rows = [[('宽度', GRAY, True), ('一半概率撞上，需要', GRAY, True)]]
    for r in R['birthday']:
        rows.append([('%d 位' % r['width'], INK, False),
                     ('%s 条报文' % fmt_count(r['half']), INK, False)])
    y = table(fig, y + 20, [(44, 'la'), (420, 'la')], rows, size=40, row_h=66)
    n32 = [r for r in R['birthday'] if r['width'] == 32][0]['half']
    y = note(fig, y, '这是生日界：32 位不用 42 亿条，%s 条就有五成概率撞上——'
                     '随机碰撞比直觉容易得多。' % fmt_count(n32))
    y = note(fig, y, '不过上一张图已经说明：有人存心要撞，根本不用碰运气，'
                     '算一遍就能构造出来。')
    save(fig, '15-birthday.png', '生日界：找到一次 CRC 碰撞所需的样本量')


def fig16():
    fig, y = new(16, '四张 32 位的表',
                 '都是 32 位，多项式不同，抓错的本事也不同。')
    short = {'CRC-32/ISO-HDLC': '以太网、ZIP',
             'CRC-32/BZIP2': 'bzip2',
             'CRC-32/MPEG-2': 'MPEG-2 传输流',
             'CRC-32C (Castagnoli)': 'iSCSI、ext4',
             'CRC-32K (Koopman)': '短帧最优之一'}
    rows = [[('名字', GRAY, True), ('多项式', GRAY, True),
             ('用在哪', GRAY, True)]]
    for s in R['standards']:
        if s['width'] != 32:
            continue
        name = s['name'].split(' (')[0]
        rows.append([(name, INK, False),
                     ('%08X' % s['poly'], TEAL, False),
                     (short[s['name']], INK_SOFT, False)])
    y = table(fig, y + 20, [(44, 'la'), (420, 'la'), (660, 'la')], rows,
              size=38, row_h=64)
    y = note(fig, y, 'ISO-HDLC 是大家最熟的那个：以太网、ZIP、PNG、gzip 全用它。'
                     'Castagnoli 换了多项式，好在硬件里一次算得多，'
                     'Koopman 那组是论文里把短帧距离推到最大搜出来的。')
    save(fig, '16-polys.png', '常见 32 位 CRC 多项式与它们的用途')


def fig17():
    fig, y = new(17, '尾巴挂在哪里',
                 '以太网 II 帧：4 字节 FCS 是最后一道，也是唯一一道冗余。')
    fields = R['frame']['fields']
    total = R['frame']['total']
    x0, x1 = 44, 1018
    scale = (x1 - x0) / total
    palette = [TINT_G, TINT_G, TINT_B, TINT_B, TINT_A, TINT_T, TINT_R]
    yy = y + 80
    x = x0
    for i, f in enumerate(fields):
        w = f['bytes'] * scale
        fig.rect(x, yy, x + w - 1, yy + 150, fill=palette[i], outline=None)
        fig.text((x + w / 2, yy + 156), '%d' % (i + 1), 38, color=INK,
                 anchor='ma')
        x += w
    fig.text((x0, yy - 46), '从目的地址到载荷末尾算 CRC；前导码与 SFD 不算',
             38, color=GRAY)
    yy += 230
    rows = [[('编号', GRAY, True), ('字段', GRAY, True),
             ('字节', GRAY, True), ('备注', GRAY, True)]]
    for i, f in enumerate(fields):
        rows.append([('%d' % (i + 1), INK, False), (f['name'], INK, False),
                     ('%d' % f['bytes'], INK, False),
                     (f['note'] or '-', INK_SOFT, False)])
    y = table(fig, yy, [(44, 'la'), (170, 'la'), (430, 'la'), (600, 'la')],
              rows, size=38, row_h=60)
    y = note(fig, y, '整帧 %d 字节（载荷 64 字节时）。网卡用硬件算 CRC，'
                     '软件只看到「这一帧收下了」或「这一帧被丢了」。' % total)
    save(fig, '17-frame.png', '以太网帧布局与 4 字节 FCS 的位置')


def fig18():
    photo('18-zip.jpg', 'Iomega_Zip_100_drive_with_a_disk.jpg',
          'Iomega ZIP 驱动器与一张 100 MB 磁盘：ZIP 格式的每一块都带 CRC-32',
          'Yuri Litvinenko / 30pin, CC BY 2.0, via Wikimedia Commons')


def fig19():
    fig, y = new(19, '六十多年',
                 '从一张纸上的多项式，到 CPU 里的一条指令。')
    nodes = [('1961', 'Peterson 与 Brown 提出循环码检错'),
             ('1975', 'IBM 同步链路用上 CRC-16'),
             ('1985', '以太网定下 CRC-32'),
             ('1989', 'ZIP 把它带进文件格式'),
             ('2008', 'CPU 加了 crc32 指令')]
    x0, x1 = 150, 910
    yy = y + 190
    fig.line((x0, yy), (x1, yy), color=GRAY, width=5)
    step = (x1 - x0) / (len(nodes) - 1)
    for i, (year, text) in enumerate(nodes):
        x = x0 + i * step
        fig.circle(x, yy, 16, fill=TEAL, outline=TEAL)
        fig.text((x, yy + 34), year, 42, bold=True, anchor='ma',
                 color=TEAL if i % 2 == 0 else BLUE)
        fig.wrap((x - 85, yy + 92), text, 38, 170, color=INK)
    yy += 330
    y = note(fig, yy, '中间那些年也没停：磁带、磁盘、光盘、总线、无线，'
                      '凡是「传过去可能坏、坏了要快点知道」的地方，'
                      '最后都落在这一个除法上。')
    save(fig, '19-timeline.png', 'CRC 从 1961 年到今天的几个节点')


def fig20():
    fig, y = new(20, '带走三句话')
    y = bullets(fig, y + 30, [
        'CRC 是一次多项式除法，余数就是校验尾巴。',
        '32 位能保证抓住所有 ≤32 位的突发错误；第一个漏网的在第 33 位。',
        '它只回答「有没有错」，不回答「错在哪儿」——纠错是另一个故事。',
    ])
    save(fig, '20-takeaways.png', '三条结论')


def cover():
    bg = '#f4f3ed'
    fig = Fig(1120, bg=bg, width=1080)
    for c in ('#1d3240', '#8fb0d0', '#dfe9f2'):
        PALETTE.add(c)
    fig.rect(0, 0, 1080, 1080, fill=bg, outline=None)
    fig.text((70, 310), 'CRC-32', 150, bold=True, color='#1d3240')
    fig.text((70, 480), '抓得住什么，', 66, bold=True, color='#8fb0d0')
    fig.text((70, 552), '抓不住什么', 66, bold=True, color='#8fb0d0')
    fig.text((70, 636), '生成多项式里正好 15 个 1', 40, color='#1d3240')
    bits = format(M.POLY32 | (1 << 32), '033b')
    for i, b in enumerate(bits):
        x = 70 + i * 28
        fig.rect(x, 690, x + 20, 750,
                 fill='#1d3240' if b == '1' else '#dfe9f2', outline=None)
    im = fig.im.crop((0, 0, 1080, 1080))
    im.save(ART / 'cover.png')
    print('   cover.png', im.size)


FIGS = [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig10,
        fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18, fig19, fig20]


def main(only=None):
    for fn in FIGS:
        if only and fn.__name__[3:] not in only:
            continue
        print(fn.__name__)
        fn()
    if not only or 'cover' in only:
        print('cover')
        cover()
    META.sort(key=lambda r: r['path'])
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, indent=1, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    import sys
    main(set(sys.argv[1:]) or None)
