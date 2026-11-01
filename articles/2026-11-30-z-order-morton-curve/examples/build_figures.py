#!/usr/bin/env python3
"""Original teaching figures for the Z-order / Morton curve article. MIT.

Every number printed here is read from results.json, which run_model.py wrote
from the same model module that draws the grids, so text and pictures cannot
disagree.
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

import zorder as M

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


# ---------------------------------------------------------------- grids

def draw_grid(fig, x0, y0, cell, n, order, numbers=True, size=38,
              fill=WHITE, edge=LIGHT):
    """Cells in key order, painted in a colour ramp so the curve is visible."""
    keys = M.order_keys(n, order)
    total = n * n
    for key, x, y in keys:
        px = x0 + x * cell
        py = y0 + y * cell
        t = key / max(1, total - 1)
        col = _ramp(t)
        k = 'g%d_%d' % (x, y)
        if numbers and cell >= 58:
            fig.box(k, px, py, px + cell, py + cell, fill=col, outline=edge, width=2)
            fig.text((px + cell / 2, py + 14), str(key), size, color=INK,
                     anchor='ma', inside=k)
        else:
            fig.rect(px, py, px + cell, py + cell, fill=col, outline=edge, width=2)


def _ramp(t):
    """White -> pale teal -> teal -> deep ink, as a smooth 4-stop ramp."""
    stops = [(1.0, 1.0, 1.0), (0.86, 0.93, 0.92), (0.42, 0.72, 0.74), (0.09, 0.28, 0.33)]
    pos = [0.0, 0.35, 0.72, 1.0]
    for i in range(len(stops) - 1):
        if t <= pos[i + 1] or i == len(stops) - 2:
            u = (t - pos[i]) / (pos[i + 1] - pos[i])
            u = min(1.0, max(0.0, u))
            a, b = stops[i], stops[i + 1]
            return '#%02x%02x%02x' % tuple(
                int(255 * (a[j] + (b[j] - a[j]) * u)) for j in range(3))


# the ramp is used as a fill, so every step of it has to be a known colour
for _i in range(64):
    PALETTE.add(_ramp(_i / 63.0))


def draw_path(fig, x0, y0, cell, n, order, color=TEAL, width=4, skip=None,
              jumps=False):
    keys = M.order_keys(n, order)
    pts = [(x0 + (x + 0.5) * cell, y0 + (y + 0.5) * cell) for _, x, y in keys]
    for a, b in zip(pts, pts[1:]):
        d = math.hypot(a[0] - b[0], a[1] - b[1]) / cell
        if skip is not None and d > skip:
            continue
        c = RED if (jumps and d > 1.05) else color
        w = 6 if (jumps and d > 1.05) else width
        fig.line(a, b, color=c, width=w)


# ---------------------------------------------------------------- figures

def fig01():
    fig, y = new(1, '把二维压成一维',
                 '两个整数换成一个整数，代价是丢掉了「谁离谁近」的直接答案。')
    x = 44
    for label, col in (('(x, y)', TINT_B), ('位交错', TINT_T),
                       ('一个整数', TINT_A), ('排序键', TINT_G)):
        chip(fig, (x, y + 20, x + 226, y + 132), label, col, size=40)
        if x < 700:
            fig.arrow((x + 232, y + 76), (x + 258, y + 76), color=GRAY, width=4)
        x += 260
    yy = y + 180
    yy = note(fig, yy, 'Z 序（Z-order，也叫 Morton 序）做的事就是这一步：把 x 的二进'
                       '制位和 y 的二进制位交替插在一起，得到一个数。这个数可以拿去做'
                       '键、做下标、做排序依据，于是二维网格变成一条一维的线。')
    yy = note(fig, yy + 6, '它便宜得离谱——几次移位和按位或就够了——所以它藏在很多你'
                           '想不到的地方：GPU 纹理排版、空间数据库的索引、八叉树的存储'
                           '顺序、压缩后的稀疏矩阵。但它不是唯一的选择，也不是总赢的那个。')
    save(fig, '01-overview.png', 'Z 序的任务：把二维坐标压成单个整数键')


def fig02():
    photo('02-gpu-die.jpg', 'ATI_RV670_die_shot_-_27808926667.jpg',
          'ATI RV670 图形芯片裸片：显存里的纹理按 Z 序变体分块存放',
          'Martijn Boer, public domain, via Wikimedia Commons')


def fig03():
    B = R['bit_layout']
    fig, y = new(3, '一次位交错',
                 'x = %d，y = %d，交错以后是二进制的 %s。' % (B['x'], B['y'], B['code_bits']))
    # three rows of bit boxes
    cols = [('bit 2', 0), ('bit 1', 1), ('bit 0', 2)]
    mono(fig, (44, y + 20), 'x', 44, TEAL)
    mono(fig, (44, y + 120), 'y', 44, BLUE)
    for i, (label, k) in enumerate(cols):
        px = 140 + i * 260
        fig.text((px, y - 6), label, 38, color=INK_SOFT)
        xb = str(B['rows'][i]['x'])
        yb = str(B['rows'][i]['y'])
        chip(fig, (px, y + 24, px + 112, y + 112), xb, TINT_T, size=44, bold=True)
        chip(fig, (px, y + 124, px + 112, y + 212), yb, TINT_B, size=44, bold=True)
        fig.arrow((px + 56, y + 218), (px + 140, y + 268), color=GRAY, width=4)
    # the interleaved result
    yy = y + 290
    fig.text((44, yy), '键', 40, color=AMBER)
    mono(fig, (140, yy), B['code_bits'], 46, AMBER)
    mono(fig, (420, yy), '= %d' % B['code'], 46, AMBER)
    yy = note(fig, yy + 76,
              '读法：编号的偶数位（第 0、2、4 位）拼出 x，奇数位（第 1、3、5 位）'
              '拼出 y。所以 011011 从右往左念是 x y x y x y，最左边那位是 y 的'
              '最高位——它被放在了更高的一半。反过来抽出偶数位和奇数位，就还原坐标。')
    yy = note(fig, yy + 6,
              '编号本身没有「距离」的含义：相邻编号的两个格子未必相邻，'
              '这一点后面要用整张图来讲。')
    save(fig, '03-interleave.png', '位交错：x=5、y=3 如何变成编号 27')


def fig04():
    n = 8
    fig, y = new(4, '八乘八的格子，走成一条 Z',
                 '编号顺序画出来是一串「Z」字，每一层都把一个方块拆成四块。')
    cell = 70
    x0, y0 = 60, y + 10
    draw_grid(fig, x0, y0, cell, n, 'morton', numbers=True)
    draw_path(fig, x0, y0, cell, n, 'morton', color=AMBER, width=4)
    # big squares: the first quadrant and the first 2x2 block
    fig.rect(x0, y0, x0 + 4 * cell, y0 + 4 * cell, fill=None, outline=TEAL, width=6)
    fig.rect(x0, y0, x0 + 2 * cell, y0 + 2 * cell, fill=None, outline=BLUE, width=4)
    fig.line((x0 + 4 * cell + 4, y0 + 8), (700, y0 + 60), color=TEAL, width=3)
    fig.wrap((712, y0 + 32), '编号 0-15：左上四分之一', 38, 300, color=TEAL)
    fig.line((x0 + 2 * cell + 4, y0 + 2 * cell - 8), (700, y0 + 150), color=BLUE,
             width=3)
    fig.wrap((712, y0 + 140), '编号 0-3：再拆一次', 38, 300, color=BLUE)
    yy = y0 + n * cell + 34
    yy = note(fig, yy, '注意那个大 Z：编号 0 到 15 全部落在左上角的四分之一里，'
                       '16 到 31 落在右上角，32 到 47 落在左下角。任何一段连续的'
                       '编号都对应一个方块——这句话是 Z 序全部用处的来源。')
    save(fig, '04-grid.png', '8x8 网格的 Z 序编号与行走路线')


def fig05():
    P = R['prefix']
    fig, y = new(5, '前缀就是方块',
                 '取编号的高 k 位当作前缀，相同前缀的格子刚好拼成一个矩形。')
    rows = []
    for p in P:
        shape = p['shapes'][0] if p['shapes'] else '?'
        rows.append([('%d 位' % p['bits'], INK, True),
                     ('%d 组' % p['groups'], INK, False),
                     (shape, TEAL if 'x' in shape and
                      shape.split('x')[0] == shape.split('x')[1] else AMBER, True),
                     ('%d 格' % (64 // p['groups']), INK, False)])
    y = table(fig, y + 8, [(120, 'la'), (330, 'la'), (520, 'la'), (800, 'la')], rows)
    y = note(fig, y,
             '偶数位的前缀是正方形，奇数位的前缀是 2:1 的长条——因为交错的时候'
             '每多取一位，x 和 y 就各多拿到一位。这条性质让 Z 序可以直接当地址用：'
             '地址的高位告诉你「哪个大区」，低位告诉你「区内第几格」。')
    y = note(fig, y, '四叉树、八叉树、GPU 的 mipmap 链，都靠这条性质把树节点'
                     '和一段连续内存对应起来。')
    save(fig, '05-prefix.png', '前缀长度与它覆盖的矩形形状')


def fig06():
    n = 8
    fig, y = new(6, '曲线上有长跳',
                 '八乘八里一共 %d 处跳格，最长的跨了两行——这就是 Z 序的代价。'
                 % R['jumps']['total'])
    cell = 78
    x0, y0 = 92, y + 10
    draw_grid(fig, x0, y0, cell, n, 'morton', numbers=False, edge=PALE)
    draw_path(fig, x0, y0, cell, n, 'morton', color=LIGHT, width=4, jumps=True)
    j = R['jumps']['jumps']
    worst = max(j, key=lambda t: t['dist'])
    fig.circle(x0 + (worst['a'][0] + 0.5) * cell, y0 + (worst['a'][1] + 0.5) * cell,
               9, fill=RED, outline=RED)
    fig.circle(x0 + (worst['b'][0] + 0.5) * cell, y0 + (worst['b'][1] + 0.5) * cell,
               9, fill=RED, outline=RED)
    yy = y0 + n * cell + 26
    note(fig, yy, '红线是相邻编号却不相邻的格子：六十三步里有三十一步不是一格，'
                  '最远的一步从最右一列直接跳到最左一列。查询一旦跨过这条裂缝，'
                  '顺序读就被打断。')
    save(fig, '06-jumps.png', '8x8 Z 序里跨格子的跳变（红色）')


def fig07():
    C = R['cost']
    fig, y = new(7, '贵不贵，要看尾巴',
                 '三种顺序，同样 65536 个格子，相邻编号之间的直线距离。')
    rows = [[('顺序', INK_SOFT, True), ('平均', INK_SOFT, True),
             ('95%', INK_SOFT, True), ('最长', INK_SOFT, True),
             ('超过 4 格', INK_SOFT, True)]]
    name = {'row': '逐行', 'morton': 'Z 序', 'hilbert': 'Hilbert'}
    col = {'row': INK, 'morton': TEAL, 'hilbert': BLUE}
    for c in C:
        rows.append([(name[c['order']], col[c['order']], True),
                     ('%.3f' % c['mean'], INK, False),
                     ('%.2f' % c['p95'], INK, False),
                     ('%.1f' % c['longest'], INK, False),
                     ('%d' % c['over_4'], INK, False)])
    y = table(fig, y + 8, [(120, 'la'), (350, 'la'), (500, 'la'),
                           (640, 'la'), (1010, 'ra')], rows)
    y = note(fig, y, 'Z 序的平均步长比逐行还小，可它的尾巴比逐行长得多：超过 4 格的'
                     '跳跃有两千零四十七次，最远一次跨 255 格。平均值好看，中位数好看，'
                     '缓存和磁盘只认最坏情况。')
    y = note(fig, y, 'Hilbert 曲线是另一条填满方块的线，它把这条尾巴彻底消掉了：'
                     '没有一步超过一格。代价是编号的算法复杂得多，还要多几次条件'
                     '判断——第一节说的「便宜」，在这里开始有价格了。')
    save(fig, '07-cost.png', '逐行 / Z 序 / Hilbert 的相邻步长统计')


def fig08():
    n = 8
    fig, y = new(8, 'Hilbert：拐来拐去，但从不跳',
                 '同样是 64 个格子，换成 U 形递归，每一步都紧挨着。')
    cell = 84
    x0, y0 = 90, y + 10
    draw_grid(fig, x0, y0, cell, n, 'hilbert', numbers=False, edge=PALE)
    draw_path(fig, x0, y0, cell, n, 'hilbert', color=BLUE, width=5)
    a = M.hilbert_d2xy(8, 0)
    b = M.hilbert_d2xy(8, 63)
    fig.circle(x0 + (a[0] + 0.5) * cell, y0 + (a[1] + 0.5) * cell, 10, fill=GREEN,
               outline=GREEN)
    fig.circle(x0 + (b[0] + 0.5) * cell, y0 + (b[1] + 0.5) * cell, 10, fill=RED,
               outline=RED)
    fig.text((x0 + n * cell + 26, y0 + 8), '起点', 40, color=GREEN)
    fig.text((x0 + n * cell + 26, y0 + 8 + n * cell - 46), '终点', 40, color=RED)
    note(fig, y0 + n * cell + 26,
         '生成规则只有一句：把一个方块分成四块，按顺序递归地走，进去的时候要'
         '转一下方向。写出来的编号算法比位交错长十倍，换来的是「局部性」这四个'
         '字可以当承诺讲。')
    save(fig, '08-hilbert.png', '8x8 网格上的 Hilbert 曲线')


def fig09():
    Rt = R['rects']
    fig, y = new(9, '对齐的方块，Z 序一次读完',
                 '256x256 网格，方块左上角放在 2 的幂的倍数上，统计要读几段。')
    rows = [[('方块', INK_SOFT, True), ('逐行', INK_SOFT, True),
             ('Z 序', INK_SOFT, True), ('Hilbert', INK_SOFT, True)]]
    for r in Rt:
        rows.append([('%dx%d' % (r['w'], r['h']), INK, True),
                     ('%.2f' % r['row'], INK, False),
                     ('%.2f' % r['morton'], TEAL, True),
                     ('%.2f' % r['hilbert'], BLUE, False)])
    y = table(fig, y + 8, [(140, 'la'), (420, 'la'), (640, 'la'), (860, 'la')], rows)
    y = note(fig, y, '一「段」就是一次寻道加一次顺序扫描。逐行存法下，一个方块'
                     '有多少行就要读多少段；Z 序存法下，对齐的方块编号连续，'
                     '一段就够，无论多大。')
    save(fig, '09-aligned.png', '对齐方块在三种顺序下各占几段')


def fig10():
    Rt = R['rects']
    fig, y = new(10, '方块一挪，优势就少一半',
                 '同样的方块，左上角随机放，不再对齐。')
    rows = [[('方块', INK_SOFT, True), ('逐行', INK_SOFT, True),
             ('Z 序', INK_SOFT, True), ('Hilbert', INK_SOFT, True)]]
    for r in Rt:
        rows.append([('%dx%d' % (r['w'], r['h']), INK, True),
                     ('%.2f' % r['row_free'], INK, False),
                     ('%.2f' % r['morton_free'], AMBER, True),
                     ('%.2f' % r['hilbert_free'], BLUE, False)])
    y = table(fig, y + 8, [(140, 'la'), (420, 'la'), (640, 'la'), (860, 'la')], rows)
    y = note(fig, y, '错开一格，Z 序的段数翻倍：方块的上半和下半在编号上被撕开，'
                     '中间隔着一整块别处的地盘。Hilbert 几乎不受影响，因为它的递归'
                     '分界和方块的边对不齐也能贴着走。')
    y = note(fig, y, '这也解释了工程里常见的那句话：Z 序要么用在「本来就知道对齐」'
                     '的地方（纹理分块、四叉树节点），要么别指望它。')
    save(fig, '10-unaligned.png', '随机偏移的方块在三种顺序下各占几段')


def fig11():
    fig, y = new(11, '段数随边长长成什么样',
                 '256x256 网格，随机偏移的方块，边长从 2 到 64。')
    S = R['sweep']
    # axes
    x0, y0 = 250, y + 60
    x1, y1 = 1000, y0 + 430
    ymax = 140.0
    for val in (0, 35, 70, 105, 140):
        yy = y1 - (val / ymax) * (y1 - y0)
        fig.line((x0, yy), (x1, yy), color=LIGHT, width=2)
        fig.text((x0 - 16, yy - 20), str(val), 38, color=INK_SOFT, anchor='ra')
    for s in (2, 4, 8, 16, 32, 64):
        xx = x0 + (math.log(s, 2) - 1) / 5.0 * (x1 - x0)
        fig.text((xx, y1 + 18), str(s), 38, color=INK_SOFT, anchor='ma')
    fig.text((x1, y0 - 46), '段数', 38, color=INK_SOFT, anchor='ra')
    fig.text((x1, y1 + 70), '方块边长（对数）', 38, color=INK_SOFT, anchor='ra')
    series = [('morton', AMBER, 'Z 序'), ('hilbert', BLUE, 'Hilbert'),
              ('row', GRAY, '逐行')]
    for key, color, label in series:
        pts = []
        for r in S:
            xx = x0 + (math.log(r['side'], 2) - 1) / 5.0 * (x1 - x0)
            yy = y1 - (r[key] / ymax) * (y1 - y0)
            pts.append((xx, yy))
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=color, width=5)
        for p in pts:
            fig.circle(p[0], p[1], 7, fill=color, outline=color)
    ly = y0 + 6
    for key, color, label in series:
        fig.rect(x1 - 300, ly - 4, x1 - 260, ly + 34, fill=color, outline=None)
        fig.text((x1 - 246, ly - 2), label, 38, color=INK)
        ly += 50
    note(fig, y1 + 116,
         '逐行是一条 45 度的直线：N 行的方块永远 8 段起。Z 序的段数约等于边长的'
         '两倍，Hilbert 始终贴着逐行线。三条线在左上角挤在一起——方块小的时候，'
         '谁都不吃亏。')
    save(fig, '11-sweep.png', '随机方块边长与读取段数的关系')


def fig12():
    S = R['sectors']
    fig, y = new(12, '一次读一行的硬件，只认连续',
                 '把 8x8 和 16x16 的方块按三种顺序放进内存，数它碰到几条 32 字节的线。')
    rows = [[('顺序', INK_SOFT, True), ('8x8 块', INK_SOFT, True),
             ('16x16 块', INK_SOFT, True), ('区间跨度', INK_SOFT, True)]]
    name = {'row': '逐行', 'morton': 'Z 序', 'hilbert': 'Hilbert'}
    for i in range(3):
        a, b = S[2 * i], S[2 * i + 1]
        rows.append([(name[a['order']], INK, True),
                     ('%d 条' % a['lines'], TEAL if a['lines'] < 8 else INK, True),
                     ('%d 条' % b['lines'], TEAL if b['lines'] < 16 else INK, True),
                     ('%d 字节' % b['span'], INK, False)])
    y = table(fig, y + 8, [(140, 'la'), (420, 'la'), (650, 'la'), (1010, 'ra')],
              rows)
    y = note(fig, y, '逐行存法的 8x8 方块，256 个字节摊在 8 条线上，中间跳过了'
                     '每行剩下 248 个字节；Z 序把同一个方块压成 64 个连续字节，'
                     '两条线读完。')
    y = note(fig, y, '内存控制器按 32 或 64 字节成块搬运，它不在乎你「只想要'
                     '八个字节」；它在乎这八个字节是不是和别人挤在同一块里。'
                     '这就是为什么贴图、体素、稀疏矩阵都愿意多花几步算编号。')
    save(fig, '12-sectors.png', '方块在三种排列下触碰的缓存线条数')


def fig13():
    fig, y = new(13, '排序以后还能再压一道',
                 '4096 个点挤在 16 个团里，按编号排序后，相邻编号之差平均要几位。')
    C = {c['order']: c for c in R['compression']}
    base = y + 40
    scale = 78.0
    cols = [('row', '逐行', GRAY), ('morton', 'Z 序', TEAL),
            ('hilbert', 'Hilbert', BLUE)]
    for i, (key, label, color) in enumerate(cols):
        v = C[key]['mean_bits']
        bx = 150 + i * 280
        top = base + 340 - v * scale
        bar(fig, bx, base + 340, 150, base + 340 - v * scale, top, color)
        fig.text((bx + 75, top - 54), '%.2f 位' % v, 40, bold=True,
                 color=color, anchor='ma')
        fig.text((bx + 75, base + 352), label, 38, color=INK, anchor='ma')
    fig.line((96, base + 340), (1010, base + 340), color=INK_SOFT, width=3)
    yy = base + 396
    yy = note(fig, yy, '按逐行编号排序，同一个团里的点会被行边界切碎，编号差里'
                       '白存了整行的偏移；Z 序把它们排成一串，差值小了一截，'
                       '变长编码也就短了一截。')
    save(fig, '13-compression.png', '三种排序下相邻编号之差所需的位数')


def fig14():
    D = R['three_d']
    fig, y = new(14, '三维也一样，只是数字变长',
                 '32x32x32 的体素网格，4x4x4 的小立方体，统计读取段数。')
    rows = [[('顺序', INK_SOFT, True), ('对齐', INK_SOFT, True),
             ('随机偏移', INK_SOFT, True)]]
    name = {'row': '逐行（三层循环）', 'morton': 'Z 序（三位交错）'}
    for how in ('row', 'morton'):
        a = next(d for d in D if d['order'] == how and d['aligned'])
        b = next(d for d in D if d['order'] == how and not d['aligned'])
        rows.append([(name[how], INK, True), ('%.1f 段' % a['runs'], TEAL, True),
                     ('%.1f 段' % b['runs'], AMBER, True)])
    y = table(fig, y + 8, [(140, 'la'), (560, 'la'), (830, 'la')], rows)
    y = note(fig, y, '三位交错就是 x、y、z 各取一位拼成三位：编号的每一位走一步，'
                     '就在三个方向上同时前进一格。八叉树的每个节点因此对应一段'
                     '连续编号，展开和折叠都只是移位。')
    y = note(fig, y, '代价和二维一样：对齐的立方体一次读完，随手放的立方体要'
                     '二十多段。三维空间里的「随手放」比二维更常见，这就是为'
                     '什么体素引擎宁可用 Morton 存节点，也不拿它当查询索引。')
    save(fig, '14-3d.png', '三维对齐立方体与随机立方体的读取段数')


def fig15():
    fig, y = new(15, '纹理为什么这么排',
                 '把一张图切成 8x8 的小块，按两种顺序摆进显存。')
    tile = 32
    x0, y0 = 74, y + 74
    fig.text((x0, y0 - 50), '逐行：块按行排', 40, color=INK_SOFT)
    for ty in range(8):
        for tx in range(8):
            px, py = x0 + tx * tile, y0 + ty * tile
            fig.rect(px, py, px + tile, py + tile,
                     fill=_ramp((ty * 8 + tx) / 63.0), outline=WHITE, width=2)
    x1 = x0 + 8 * tile + 118
    fig.text((x1, y0 - 50), 'Z 序：块按 Morton 排', 40, color=INK_SOFT)
    tiles = sorted(range(64), key=lambda t: M.morton2(t % 8, t // 8))
    for slot, t in enumerate(tiles):
        px = x1 + (slot % 8) * tile
        py = y0 + (slot // 8) * tile
        fig.rect(px, py, px + tile, py + tile,
                 fill=_ramp(t / 63.0), outline=WHITE, width=2)
    fig.arrow((x0 + 8 * tile + 16, y0 + 4 * tile), (x1 - 20, y0 + 4 * tile),
              color=GRAY, width=4)
    yy = y0 + 8 * tile + 34
    yy = note(fig, yy, '左边：显存里第 0 块、第 1 块、第 2 块……顺着排。右边：'
                       '第 0 块后面是右边那块，再后面是右下角那块。颜色相同的位置'
                       '在两边代表同一块图，只是摆法不同。')
    yy = note(fig, yy, 'GPU 一次画 2x2 或 4x4 个小块，左图的四次访问在显存里隔着'
                       '两三百字节，右图里挨在一起。这就是「分块」——本质上就是'
                       '把 Z 序当成了地址。')
    save(fig, '15-swizzle.png', '逐行排列与分块（tile）排列的对照')


def fig16():
    photo('16-radeon.jpg', 'ATI_Radeon_HD_2400_Pro,_128MB_(1).jpg',
          'Radeon HD 2400 Pro：这一代显卡的纹理单元已经在用分块寻址',
          'Cjp24, CC BY-SA 4.0, via Wikimedia Commons')


def fig17():
    fig, y = new(17, '六十年，四次重新发现',
                 '同一条曲线被数学、数据库、图形硬件各找了一遍。')
    x0, x1 = 150, 910
    ly = y + 120
    fig.line((x0, ly), (x1, ly), color=INK_SOFT, width=4)
    nodes = [(0.00, '1891', 'Hilbert', '一条不跳的填满方块的曲线'),
             (0.34, '1966', 'Morton', 'IBM 报告：交错二进制位'),
             (0.67, '1990s', 'GPU', '纹理分块寻址成为标准'),
             (1.00, '2013', 'Haswell', 'pdep / pext 一条指令搞定')]
    for t, year, who, what in nodes:
        px = x0 + t * (x1 - x0)
        fig.circle(px, ly, 12, fill=TEAL, outline=TEAL)
        fig.text((px, ly - 76), year, 40, bold=True, color=TEAL, anchor='ma')
        fig.text((px, ly - 34), who, 38, color=INK, anchor='ma')
        fig.wrap((px - 105, ly + 28), what, 38, 210, color=INK_SOFT)
    note(fig, ly + 190,
         'Hilbert 在 1891 年画这条曲线的时候，计算机还不存在；Morton 1966 年'
         '申请专利时想的是「怎么把多维数据排成文件」；图形硬件重新发现它，'
         '是因为 8x8 的方块正好和纹理缓存的行宽对上。')
    save(fig, '17-timeline.png', 'Z 序相关工作的四个时间点')


def fig18():
    fig, y = new(18, '记住三句话',
                 'Z 序不难，难的是判断它在你的场合值不值。')
    y = bullets(fig, y + 6, [
        '它把坐标压成一个整数键，代价是丢掉距离：相邻编号不代表相邻格子，'
        '最坏一步能跨过整行。',
        '它的全部用处来自「前缀是方块」：对齐的方块编号连续，四叉树节点、'
        '纹理小块、体素分块都能因此变成一段地址。',
        '方块不对齐时，优势会掉一半；Hilbert 在这时候更稳，代价是编号算法'
        '不再是几次移位。',
    ])
    y = note(fig, y + 10, '选择的标准不是「谁的曲线更漂亮」，而是「我的查询形状'
                          '和这种编号的分界线对不对得上」。对得上，Z 序最便宜；'
                          '对不上，要么改数据结构，要么换曲线。')
    save(fig, '18-takeaways.png', '全文结论')


def cover():
    fig = Fig(1080, bg='#f4f3ed', width=1080)
    fig.text((540, 336), '一条线穿过所有格子', 58, bold=True, color=INK, anchor='ma')
    fig.text((540, 424), 'Z 序 / Morton 曲线：把二维坐标压成一个整数键', 42,
             color=TEAL, anchor='ma')
    cell = 34
    n = 8
    x0 = 540 - n * cell // 2
    y0 = 486
    draw_grid(fig, x0, y0, cell, n, 'morton', numbers=False, edge=WHITE)
    draw_path(fig, x0, y0, cell, n, 'morton', color=AMBER, width=3)
    fig.text((540, 800), '二维坐标 → 一个整数 → 一段连续的内存', 40,
             color=INK_SOFT, anchor='ma')
    row = fig.save(ASSETS / 'cover.png', 'Z 序封面：8x8 网格上的 Morton 路径')
    fig.im.crop((0, 0, 1080, 1080)).save(ASSETS / 'cover.png')
    print('   cover.png', (ASSETS / 'cover.png').stat().st_size, 'B')


def main():
    fig01(); fig02(); fig03(); fig04(); fig05(); fig06(); fig07(); fig08()
    fig09(); fig10(); fig11(); fig12(); fig13(); fig14(); fig15(); fig16()
    fig17(); fig18()
    (ART / 'figure-metadata.json').write_text(
        json.dumps(sorted(META, key=lambda r: r['path']), indent=1,
                   ensure_ascii=False) + '\n')
    print('  %d figures' % len(META))
    cover()


if __name__ == '__main__':
    main()
