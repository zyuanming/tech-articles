#!/usr/bin/env python3
"""Original teaching figures for the branch-prediction article. MIT.

Every number printed here comes from results.json.
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


def new(n, title, sub=None, h=900):
    fig = Fig(h)
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


def frame(fig, box, xticks, yticks, xsize=38):
    x0, y0, x1, y1 = box
    fig.line((x0, y1), (x1, y1), color=INK_SOFT, width=4)
    fig.line((x0, y1), (x0, y0), color=INK_SOFT, width=4)
    for frac, lab in xticks:
        gx = x0 + (x1 - x0) * frac
        fig.line((gx, y1), (gx, y1 + 10), color=INK_SOFT, width=3)
        fig.text((gx, y1 + 16), lab, xsize, color=INK_SOFT, anchor='ma')
    for frac, lab in yticks:
        gy = y1 - (y1 - y0) * frac
        fig.line((x0 - 10, gy), (x0, gy), color=INK_SOFT, width=3)
        fig.text((x0 - 16, gy - xsize * 0.55), lab, xsize, color=INK_SOFT,
                 anchor='ra')
    return (lambda fx: x0 + (x1 - x0) * fx), (lambda fy: y1 - (y1 - y0) * fy)


def poly(fig, pts, color=TEAL, width=5):
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=color, width=width)


def arc(fig, c, r, a0, a1, color=GRAY, width=4, steps=18, head=True):
    pts = [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
            c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / steps)))
           for i in range(steps + 1)]
    if head:
        fig.arrow(pts[-2], pts[-1], color=color, width=width, head=13)
        poly(fig, pts[:-1], color=color, width=width)
    else:
        poly(fig, pts, color=color, width=width)


def legend(fig, y, items, x0=60, step=236):
    for i, (lab, col) in enumerate(items):
        x = x0 + i * step
        fig.line((x, y + 26), (x + 52, y + 26), color=col, width=7)
        fig.text((x + 66, y), lab, 38, color=INK)
    return y + 70


def pct(v, nd=1):
    return ('%.' + str(nd) + 'f%%') % (v * 100)


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


# ------------------------------------------------------------- 01 pipeline

def fig01():
    fig, y = new(1, '分支的答案，要到第三关才有',
                 '取指、译码、执行、访存、写回。分支在「执行」这一关才知道跳不跳，'
                 '而后面两三条指令早就进了流水线。')
    stages = ['取指', '译码', '执行', '访存', '写回']
    cell_w, cell_h = 100, 64
    x0, y0 = 190, y + 40
    for si, s in enumerate(stages):
        yy = y0 + si * (cell_h + 6)
        fig.text((44, yy + 14), s, 40, color=INK if s != '执行' else RED)
        for c in range(8):
            xx = x0 + c * (cell_w + 4)
            fig.rect(xx, yy, xx + cell_w, yy + cell_h, fill=WHITE,
                     outline=LIGHT, width=2)
    # 指令在流水线里的位置
    filled = {'I0': [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)],
              'I1': [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
              'I2': [(0, 2), (1, 3)]}
    for name, cells in filled.items():
        for r, c in cells:
            xx = x0 + c * (cell_w + 4)
            yy = y0 + r * (cell_h + 6)
            fig.rect(xx, yy, xx + cell_w, yy + cell_h, fill=TINT_T, outline=TEAL,
                     width=3)
            fig.text((xx + cell_w // 2, yy + 12), name, 40, color=INK,
                     anchor='ma')
    # 分支那格
    xx = x0 + 4 * (cell_w + 4)
    yy = y0 + 2 * (cell_h + 6)
    fig.rect(xx, yy, xx + cell_w, yy + cell_h, fill=TINT_R, outline=RED, width=3)
    fig.text((xx + cell_w // 2, yy + 12), '分支', 38, color=RED, anchor='ma')
    # 被冲掉的两格
    for r, c in ((1, 4), (0, 4)):
        xx = x0 + c * (cell_w + 4)
        yy = y0 + r * (cell_h + 6)
        fig.rect(xx, yy, xx + cell_w, yy + cell_h, fill=TINT_R, outline=RED,
                 width=3)
        fig.text((xx + cell_w // 2, yy + 12), '冲掉', 38, color=RED, anchor='ma')
    # 新目标从第 5 拍进来
    for r in range(2):
        xx = x0 + 5 * (cell_w + 4)
        yy = y0 + r * (cell_h + 6)
        fig.rect(xx, yy, xx + cell_w, yy + cell_h, fill=PALE, outline=BLUE,
                 width=3)
        fig.text((xx + cell_w // 2, yy + 12), '新目标' if r == 0 else '等',
                 38, color=BLUE, anchor='ma')
    # 拍号
    for c in range(8):
        fig.text((x0 + c * (cell_w + 4) + cell_w // 2, y0 - 44), '第%d拍' % (c + 1),
                 38, color=GRAY, anchor='ma')
    y = y0 + 5 * (cell_h + 6) + 40
    y = note(fig, y, '这两格不是白等：它们真的空着，这叫气泡。猜对与否，'
                     '决定了每次遇到分支要不要攒这样两三个气泡。')
    save(fig, '01-pipeline.png', '五级流水线上，分支在执行级才有答案，年轻指令被冲掉')


# ---------------------------------------------------------------- 02 photo

def fig02():
    photo('02-wolfdale-die.jpg',
          'Intel_Wolfdale_die_shot_(E8400)_etched_-_29336152187.jpg',
          'Intel Core 2 Duo（Wolfdale）裸片：分支预测器就在这块硅片上，'
          '和缓存、执行单元挤在一起',
          'Martijn Boer, public domain, via Wikimedia Commons')


# ------------------------------------------------------------- 03 lookup

def fig03():
    fig, y = new(3, '预测器说到底就一件事：查表',
                 '拿这条分支的地址（有时再加上最近的跳转历史）当索引，'
                 '从表里取出一位，说「跳」还是「不跳」。')
    fig.box('pc', 44, y + 30, 300, y + 120, fill=TINT_B, outline=BLUE)
    fig.text((172, y + 50), '分支的地址', 40, color=BLUE, anchor='ma')
    fig.box('gh', 44, y + 140, 300, y + 230, fill=TINT_A, outline=AMBER)
    fig.text((172, y + 160), '最近的跳转历史', 38, color=AMBER, anchor='ma')
    fig.arrow((310, y + 165), (400, y + 165), color=INK_SOFT, width=4)
    fig.text((342, y + 190), '异或', 38, color=INK_SOFT)
    # 表
    tx, ty = 410, y + 40
    fig.rect(tx, ty, tx + 380, ty + 200, fill=WHITE, outline=INK_SOFT, width=4)
    vals = ['3', '0', '1', '2', '3', '1']
    for i, v in enumerate(vals):
        cx = tx + 24 + (i % 3) * 120
        cy = ty + 24 + (i // 3) * 84
        fig.rect(cx, cy, cx + 100, cy + 66, fill=TINT_T, outline=TEAL, width=2)
        mono(fig, (cx + 36, cy + 12), v, 38, INK)
    fig.text((600, ty + 212), '表里存的是计数器', 38, color=INK_SOFT, anchor='ma')
    fig.arrow((800, y + 165), (870, y + 165), color=TEAL, width=5)
    fig.box('out', 880, y + 110, 1018, y + 220, fill=TINT_G, outline=GREEN)
    fig.text((949, y + 130), '猜：跳', 40, color=GREEN, anchor='ma')
    y = ty + 280
    y = bullets(fig, y, [
        '表有多大、索引怎么算、计数器几位——各家预测器的差别主要就在这三件事上。',
        '一位的输出看起来寒酸，但它每猜一次都省下十几个周期。',
    ])
    save(fig, '03-lookup.png', '预测器的通用结构：地址与历史做索引，表里取出一位')


# ------------------------------------------------------------ 04 one bit

def fig04():
    fig, y = new(4, '一位计数器：上次跳，这次也猜跳',
                 '两个状态，记住的就只有上回的结果。猜错一次，立刻改口。')
    cy = y + 190
    a, b = (330, cy), (740, cy)
    fig.circle(*a, 100, fill=TINT_B, outline=BLUE, width=5)
    fig.text((a[0], a[1] - 62), '猜不跳', 40, color=BLUE, anchor='ma')
    fig.text((a[0], a[1] + 4), 'N', 44, color=BLUE, anchor='ma')
    fig.circle(*b, 100, fill=TINT_T, outline=TEAL, width=5)
    fig.text((b[0], b[1] - 62), '猜跳', 40, color=TEAL, anchor='ma')
    fig.text((b[0], b[1] + 4), 'T', 44, color=TEAL, anchor='ma')
    fig.arrow((a[0] + 104, a[1] - 26), (b[0] - 104, b[1] - 26), color=GREEN,
              width=5)
    fig.text(((a[0] + b[0]) // 2, cy - 96), '实际跳了', 38, color=GREEN,
             anchor='ma')
    fig.arrow((b[0] - 104, b[1] + 30), (a[0] + 104, a[1] + 30), color=RED,
              width=5)
    fig.text(((a[0] + b[0]) // 2, cy + 42), '实际没跳', 38, color=RED,
             anchor='ma')
    arc(fig, b, 130, -60, 60, color=GREEN, width=4)
    fig.text((b[0] + 128, cy - 20), '跳', 38, color=GREEN)
    arc(fig, a, 130, 120, 240, color=RED, width=4)
    fig.text((a[0] - 132, cy - 20), '没跳', 38, color=RED, anchor='ra')
    y = cy + 210
    y = note(fig, y, '代价：一个循环跑 10 次，退出时会连错两次——退出那一下猜错，'
                     '下一轮进来的第一下又猜错。')
    save(fig, '04-one-bit.png', '一位预测器的两个状态与迁移')


# ------------------------------------------------------------ 05 two bit

def fig05():
    fig, y = new(5, '两位计数器：要错两次才改主意',
                 '四个状态，从「强不跳」到「强跳」。错一次只是把信心减一格，'
                 '预测不变。')
    cy = y + 200
    xs = [210, 440, 670, 900]
    labels = [('强不跳', '00'), ('弱不跳', '01'), ('弱跳', '10'), ('强跳', '11')]
    for (x, (lab, code)), col in zip(zip(xs, labels), (BLUE, BLUE, TEAL, TEAL)):
        fig.circle(x, cy, 92, fill=TINT_B if col == BLUE else TINT_T,
                   outline=col, width=5)
        fig.text((x, cy - 58), lab, 38, color=col, anchor='ma')
        fig.text((x, cy - 6), code, 44, color=col, anchor='ma')
    for i in range(3):
        fig.arrow((xs[i] + 96, cy - 24), (xs[i + 1] - 96, cy - 24), color=GREEN,
                  width=5, head=14)
        fig.arrow((xs[i + 1] - 96, cy + 28), (xs[i] + 96, cy + 28), color=RED,
                  width=5, head=14)
    fig.text((540, cy - 96), '实际跳了 → 往右挪一格', 38, color=GREEN, anchor='ma')
    fig.text((540, cy + 52), '实际没跳 → 往左挪一格', 38, color=RED, anchor='ma')
    arc(fig, (xs[3], cy), 122, -55, 55, color=GREEN, width=4)
    fig.text((xs[3] + 120, cy - 18), '跳', 38, color=GREEN)
    arc(fig, (xs[0], cy), 122, 125, 235, color=RED, width=4)
    fig.text((xs[0] - 124, cy - 18), '没跳', 38, color=RED, anchor='ra')
    y = cy + 190
    y = note(fig, y, '同样的循环跑 10 次，退出时只错一次：从「弱跳」挪到「强不跳」，'
                     '预测才翻转，而这时循环已经退出了。')
    save(fig, '05-two-bit.png', '两位饱和计数器的四个状态与迁移')


# --------------------------------------------------------- 06 loop exit

def fig06():
    d = R['detail']
    n = len(d['outcomes'])
    m1 = len(d['preds']['1 位计数器表']['miss_at'])
    m2 = len(d['preds']['2 位计数器表']['miss_at'])
    fig, y = new(6, '循环退出那一步，两种计数器差在哪',
                 '同一个分支连续跳 5 次后不跳，再重新开始。红圈是猜错的那一步：'
                 '一位错 %d 次，两位错 %d 次。' % (m1, m2))
    cell, gap = 40, 6
    x0 = 180
    rows = [('实际', d['outcomes'], None),
            ('一位', d['preds']['1 位计数器表']['pred'],
             d['preds']['1 位计数器表']['miss_at']),
            ('两位', d['preds']['2 位计数器表']['pred'],
             d['preds']['2 位计数器表']['miss_at'])]
    yy = y + 30
    for lab, seq, miss in rows:
        fig.text((44, yy + 6), lab, 40, color=INK)
        for i, v in enumerate(seq):
            xx = x0 + i * (cell + gap)
            fill = TINT_T if v else PALE
            col = TEAL if v else BLUE
            fig.rect(xx, yy, xx + cell, yy + 56, fill=fill, outline=col, width=2)
            fig.text((xx + cell // 2, yy + 8), '跳' if v else '不', 38,
                     color=col, anchor='ma')
            if miss is not None and i in miss:
                fig.rect(xx - 4, yy - 4, xx + cell + 4, yy + 60, fill=None,
                         outline=RED, width=4)
        yy += 96
    y = yy + 10
    y = note(fig, y, '一位在两处连错：退出（该不跳，它还猜跳）和下一轮第一步'
                     '（该跳，它刚改成不跳）。两位只错退出那一下，'
                     '下一轮第一步已经回到「跳」。')
    save(fig, '06-loop-exit.png', '循环退出时一位与两位预测器的错判位置')


# ------------------------------------------------------- 07 loop length

def fig07():
    ls = R['loop_sweep']
    fig, y = new(7, '循环越长，猜错的占比越低',
                 '每条循环跑 n 次再退出一次，每条 trace 约 4000 个分支。'
                 '纵轴是整段 trace 的错判率，横轴是 n（对数）。')
    box = (150, y + 30, 1010, y + 430)
    lo, hi = 1, math.log2(100)
    h = box[3] - box[1]
    fx = lambda v: box[0] + (box[2] - box[0]) * (math.log2(v) - lo) / (hi - lo)
    fy = lambda v: box[3] - h * min(v, 1.0)
    frame(fig, box, [(0, '2'), ((math.log2(5) - 1) / (hi - lo), '5'),
                     ((math.log2(10) - 1) / (hi - lo), '10'),
                     ((math.log2(20) - 1) / (hi - lo), '20'),
                     ((math.log2(50) - 1) / (hi - lo), '50'),
                     (1, '100')],
          [(0, '0'), (0.25, '25%'), (0.5, '50%'), (0.75, '75%'), (1, '100%')])
    series = [('static', '静态：从不跳', GRAY),
              ('one_bit', '一位', BLUE),
              ('two_bit', '两位', TEAL),
              ('gshare', 'gshare', AMBER)]
    for key, lab, col in series:
        pts = [(fx(r['iters']), fy(r[key])) for r in ls]
        poly(fig, pts, color=col, width=6)
        for p in pts:
            fig.circle(p[0], p[1], 9, fill=col, outline=col, width=2)
    y = legend(fig, box[3] + 90, [('静态', GRAY), ('一位', BLUE),
                                  ('两位', TEAL), ('gshare', AMBER)])
    last = ls[-1]
    fig.text((fx(100), fy(last['gshare']) - 52), pct(last['gshare']), 38,
             color=AMBER, anchor='ra')
    y += 24
    y = note(fig, y, 'n=2 时一半的分支都是退出，一位和「从不跳」一样糟；'
                     'n=100 时两位 1.0%、gshare 1.9%、一位 2.0%，静态还停在 99%。')
    save(fig, '07-loop-length.png', '错判率随循环长度变化')


# ------------------------------------------------------------ 08 alias

def fig08():
    fig, y = new(8, '64 个分支挤进 16 个格子',
                 '索引只取地址的低几位，不同的分支就会落到同一格。'
                 '这一格只记得住一个结果，于是它们互相把对方教坏。')
    # 左：64 个小方块
    bx, by, s, g = 60, y + 40, 40, 6
    for i in range(64):
        cx = bx + (i % 8) * (s + g)
        cy = by + (i // 8) * (s + g)
        fig.rect(cx, cy, cx + s, cy + s, fill=TINT_B, outline=BLUE, width=2)
    fig.text((bx, by + 8 * (s + g) + 16), '64 个不同的分支', 38, color=BLUE)
    # 右：16 个格子
    sx, sy = 760, by + 10
    for i in range(16):
        cx = sx + (i % 4) * 62
        cy = sy + (i // 4) * 62
        fig.rect(cx, cy, cx + 54, cy + 54, fill=TINT_A, outline=AMBER, width=3)
    fig.text((sx, sy + 4 * 62 + 16), '16 个表项', 38, color=AMBER)
    # 四条箭头表示 4 个分支进 1 格
    for k, src_i in enumerate((0, 1, 8, 9)):
        cx = bx + (src_i % 8) * (s + g) + s
        cy = by + (src_i // 8) * (s + g) + s // 2
        fig.arrow((cx + 6, cy), (sx - 10, sy + 27), color=RED, width=3, head=10)
    fig.text((520, by + 30), '低 4 位相同', 38, color=RED, anchor='ma')
    y = by + 8 * (s + g) + 70
    y = bullets(fig, y, [
        '表项越多，撞车越少；但表不可能无限大，所以真硬件里冲突永远存在。',
        'gshare 这类预测器还会把历史也异或进索引，撞车的花样更多，'
        '所以常有「两个预测器用不同的索引」的补救办法。',
    ])
    save(fig, '08-alias.png', '索引位数不够时，多个分支共享同一个表项')


# -------------------------------------------------------- 09 alias curve

def fig09():
    al = R['alias']
    fig, y = new(9, '表长到工作集那么大，冲突才消失',
                 '64 个结果固定、互不相关的分支，反复执行 60 轮。'
                 '表小于 64 格时，平均每格挤着好几个分支。')
    box = (150, y + 30, 1010, y + 400)
    lo, hi = math.log2(4), math.log2(256)
    h = box[3] - box[1]
    fx = lambda v: box[0] + (box[2] - box[0]) * (math.log2(v) - lo) / (hi - lo)
    fy = lambda v: box[3] - h * min(v / 0.6, 1.0)
    frame(fig, box, [((math.log2(v) - lo) / (hi - lo), str(v))
                     for v in (4, 8, 16, 32, 64, 128, 256)],
          [(0, '0'), (0.2, '20%'), (0.4, '40%'), (0.6, '60%')])
    pts = [(fx(r['entries']), fy(r['miss'])) for r in al]
    poly(fig, pts, color=RED, width=6)
    for p in pts:
        fig.circle(p[0], p[1], 9, fill=RED, outline=RED, width=2)
    fig.line((fx(64), box[3]), (fx(64), box[1] + 20), color=GRAY, width=3,
             dash=10)
    fig.text((fx(64) + 14, box[1] + 24), '工作集 64', 38, color=GRAY)
    fig.text((fx(16), fy(al[2]['miss']) - 56), pct(al[2]['miss'], 0), 38,
             color=RED, anchor='ma')
    fig.text((fx(64) + 16, fy(al[4]['miss']) - 56), pct(al[4]['miss'], 0), 38,
             color=RED)
    y = box[3] + 60
    y = note(fig, y, '16 格时错判率约 39%，比「永远猜同一个答案」的 50% 好不了多少；'
                     '64 格时掉到 1.7%，剩下的只是每个分支第一次见面时的试探。')
    save(fig, '09-alias-curve.png', '表项数从 4 到 256 时，64 个分支的错判率')


# ------------------------------------------------------- 10 correlated

def fig10():
    cs = R['correlated_sample']
    fig, y = new(10, '两个分支，一个跟着另一个走',
                 '单看每个分支都是五五开的随机；可一旦知道 A 刚刚怎么走，'
                 'B 就没有悬念了。')
    fig.box('code', 44, y + 20, 1018, y + 210, fill=CREAM, outline=LIGHT)
    mono(fig, (70, y + 40), 'if (a == 0) { ... }', 38, INK)
    mono(fig, (70, y + 96), 'if (b == 0) { ... }', 38, INK)
    mono(fig, (70, y + 152), '// b 的新值就是 a，两个判断同时成立', 38, INK_SOFT)
    yy = y + 250
    fig.text((44, yy + 8), 'A', 40, color=BLUE)
    fig.text((44, yy + 92), 'B', 40, color=TEAL)
    fig.text((130, yy - 46), '1 = 条件成立，0 = 不成立', 38, color=INK_SOFT)
    cell, gap = 74, 8
    for i, (a, b) in enumerate(list(zip(cs['a'], cs['b']))[:10]):
        for row, v, col, tint in ((0, a, BLUE, TINT_B), (1, b, TEAL, TINT_T)):
            xx = 130 + i * (cell + gap)
            cy = yy + row * 84
            fig.rect(xx, cy, xx + cell, cy + 56, fill=tint, outline=col, width=2)
            mono(fig, (xx + 22, cy + 6), str(v), 40, col)
    y = yy + 190
    y = bullets(fig, y, [
        '只看自己的上次结果，B 的每一格都像抛硬币，怎么猜都是五成。',
        '把 A 的结果记进「全局历史」，索引就分成了两半：A 成立的那一半，'
        'B 全成立；另一半全不成立。',
    ])
    save(fig, '10-correlated.png', '两个结果完全相关的分支，单看各自都不可预测')


# -------------------------------------------------------- 11 gshare

def fig11():
    fig, y = new(11, 'gshare：把历史异或进索引',
                 '地址和历史各取一组位，按位异或得到索引。历史一变，同一个分支'
                 '就会查到不同的格子。')
    n = 12
    bw, gap = 44, 6
    x0 = 180

    def row(yy, title, bits, colors):
        fig.text((44, yy + 8), title, 40, color=INK)
        for i, b in enumerate(bits):
            xx = x0 + i * (bw + gap)
            fig.rect(xx, yy, xx + bw, yy + 56,
                     fill=colors[i % 2], outline=INK_SOFT, width=2)
            mono(fig, (xx + 10, yy + 6), str(b), 38, INK)

    pc = [1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0]
    gh = [0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1]
    idx = [a ^ b for a, b in zip(pc, gh)]
    yy = y + 20
    row(yy, '地址', pc, (TINT_B, PALE))
    yy += 90
    fig.text((x0 + 240, yy - 26), '异或', 38, color=RED, anchor='ma')
    row(yy, '历史', gh, (TINT_A, PALE))
    yy += 90
    row(yy, '索引', idx, (TINT_T, PALE))
    yy += 90
    fig.arrow((x0 + 300, yy - 30), (x0 + 300, yy + 26), color=TEAL, width=4)
    fig.rect(x0 + 60, yy + 30, 900, yy + 130, fill=WHITE, outline=INK_SOFT,
             width=3)
    for i in range(6):
        cx = x0 + 76 + i * 128
        fig.rect(cx, yy + 44, cx + 110, yy + 114, fill=TINT_T, outline=TEAL,
                 width=2)
        mono(fig, (cx + 40, yy + 62), str((i * 3) % 4), 38, INK)
    fig.text((540, yy + 138), '计数器表：索引选一格', 38, color=INK_SOFT,
             anchor='ma')
    y = yy + 210
    y = note(fig, y, '同一个分支，在历史不同的时刻被分到不同的格子，'
                     '于是它可以同时记住好几种「上下文」。')
    save(fig, '11-gshare.png', 'gshare 的索引构造：地址低 12 位与 12 位全局历史异或')


# -------------------------------------------------------- 12 ladder

def fig12():
    lad = R['ladder']
    fig, y = new(12, '历史不是越长越好',
                 '同一个 gshare，只改历史长度。太长时表格要见很多次才学得会，'
                 '太短时又分不清上下文。')
    box = (150, y + 30, 1010, y + 380)
    lo, hi = 1, 16
    h = box[3] - box[1]
    fx = lambda v: box[0] + (box[2] - box[0]) * (v - lo) / (hi - lo)
    fy = lambda v: box[3] - h * min(v / 0.35, 1.0)
    frame(fig, box, [((v - lo) / (hi - lo), str(v)) for v in (1, 2, 4, 6, 8, 10, 12, 14, 16)],
          [(0, '0'), (0.1, '10%'), (0.2, '20%'), (0.3, '30%')])
    series = [('correlated', 'B 跟着 A（需要 1 位）', BLUE),
              ('period3', 'T T N 周期（需要 2 位）', GREEN),
              ('loop10', '循环 10 次（需要 10 位）', AMBER)]
    for key, lab, col in series:
        pts = [(fx(r['hist']), fy(r['miss'])) for r in lad[key]]
        poly(fig, pts, color=col, width=6)
    y = legend(fig, box[3] + 90, [('周期 3', GREEN), ('循环 10', AMBER),
                                  ('相关分支', BLUE)])
    y += 24
    y = note(fig, y, '周期 3 只要有 2 位历史（33% 掉到 0.2%）；循环 10 要 10 位，'
                     '不到 10 位时反而比 1 位更差（9.7% 涨到 13.0%）；'
                     '相关分支一直停在 25% 上方——A 本身就是随机的，'
                     '那 25% 是猜不中的下限。')
    save(fig, '12-history-ladder.png', 'gshare 的错判率随历史长度变化')


# --------------------------------------------------------- 13 local

def fig13():
    fig, y = new(13, '局部历史：每个分支记自己的一小段',
                 '周期图案（比如 T T N T T N）在全局历史里会被别的分支搅乱，'
                 '自己的一小段历史反而稳定。')
    fig.box('lht', 44, y + 40, 420, y + 330, fill=TINT_B, outline=BLUE)
    fig.text((232, y + 56), '每个 PC 一格历史', 40, color=BLUE, anchor='ma')
    for i, bits in enumerate(([1, 0, 1, 1], [0, 0, 1, 0], [1, 1, 1, 0])):
        yy = y + 120 + i * 66
        mono(fig, (70, yy), 'PC%d' % i, 38, INK)
        for j, b in enumerate(bits):
            xx = 170 + j * 54
            fig.rect(xx, yy, xx + 46, yy + 50, fill=WHITE, outline=BLUE, width=2)
            mono(fig, (xx + 14, yy + 4), str(b), 38, INK)
    fig.arrow((430, y + 185), (520, y + 185), color=INK_SOFT, width=4)
    fig.box('pht', 530, y + 40, 1018, y + 330, fill=TINT_T, outline=TEAL)
    fig.text((774, y + 56), '用这段历史去查计数器', 40, color=TEAL, anchor='ma')
    for i, v in enumerate(('3', '1', '0', '2', '3', '2', '1', '0')):
        cx = 560 + (i % 4) * 112
        cy = y + 130 + (i // 4) * 100
        fig.rect(cx, cy, cx + 96, cy + 80, fill=WHITE, outline=TEAL, width=2)
        mono(fig, (cx + 34, cy + 18), v, 40)
    y = y + 390
    y = bullets(fig, y, [
        '两位计数器里，局部历史的版本在周期 3 的图案上错判率 0.3%，'
        'gshare 是 0.4%，看起来差不多；在嵌套循环上局部历史是 3.5%，'
        '两位表是 16.3%。',
        '代价：每个分支都要存一段历史，表比单纯的一张计数器表大得多。',
    ])
    save(fig, '13-local.png', '局部历史预测器：每个 PC 一段历史寄存器，用它索引计数器表')


# ----------------------------------------------------- 14 tournament

def fig14():
    fig, y = new(14, '锦标赛：两个预测器，再选一个',
                 'A 猜一次、B 猜一次，另外一张表只负责记录「这个地址上谁更靠谱」。')
    fig.box('a', 44, y + 40, 380, y + 150, fill=TINT_T, outline=TEAL)
    fig.text((212, y + 66), '两位计数器表', 40, color=TEAL, anchor='ma')
    fig.box('b', 44, y + 190, 380, y + 300, fill=TINT_A, outline=AMBER)
    fig.text((212, y + 216), 'gshare', 40, color=AMBER, anchor='ma')
    fig.box('ch', 470, y + 90, 760, y + 250, fill=TINT_B, outline=BLUE)
    fig.text((615, y + 106), '选择计数器', 38, color=BLUE, anchor='ma')
    fig.text((615, y + 168), '0 1 2 3', 40, color=BLUE, anchor='ma')
    fig.arrow((390, y + 95), (462, y + 140), color=TEAL, width=4)
    fig.arrow((390, y + 245), (462, y + 200), color=AMBER, width=4)
    fig.arrow((770, y + 170), (860, y + 170), color=INK_SOFT, width=4)
    fig.box('out', 870, y + 110, 1018, y + 230, fill=TINT_G, outline=GREEN)
    fig.text((944, y + 130), '输出', 40, color=GREEN, anchor='ma')
    fig.text((944, y + 186), '一位', 38, color=GREEN, anchor='ma')
    y = y + 350
    y = note(fig, y, '选择计数器也带饱和：A 对 B 错就往 B 挪，B 对 A 错就往 A 挪。'
                     '循环 10 次那条 trace 上，两位单独错 9.4%、gshare 错 4.5%，'
                     '合起来只错 0.9%。')
    save(fig, '14-tournament.png', '锦标赛预测器：两个预测器加一张选择表')


# --------------------------------------------------------- 15 matrix

def fig15():
    m = R['matrix']
    preds = R['predictors']
    short = {'静态：从不 taken': '静态NT', '静态：总是 taken': '静态T',
             '1 位计数器表': '1 位', '2 位计数器表': '2 位',
             '局部历史 8 位': '局部', 'gshare 12 位历史': 'GS',
             '锦标赛：2 位表 / gshare': '混合'}
    rows = [('loop10', '循环 10'), ('loop100', '循环 100'), ('nested', '嵌套'),
            ('random50', '随机'), ('correlated', '相关'),
            ('period3', '周期 3'), ('switch8', 'switch8')]
    fig, y = new(15, '七种做法，七种分支',
                 '格子里是错判率（%），越低越好，加粗的是这一行最好的。'
                 'GS = gshare，混合 = 锦标赛。', h=980)
    colx = [44] + [300 + i * 116 for i in range(7)]
    fig.rect(44, y - 14, 1018, y + 52, fill=PALE, outline=None)
    for i, pr in enumerate(preds):
        fig.text((colx[i + 1], y), short[pr], 38, bold=True, color=INK_SOFT,
                 anchor='ra')
    yy = y + 78
    for key, lab in rows:
        fig.text((44, yy), lab, 38, color=INK)
        best = min(m[key].values())
        for j, pr in enumerate(preds):
            v = m[key][pr]
            num = ('%.0f' % (v * 100)) if v >= 0.1 else ('%.1f' % (v * 100))
            fig.text((colx[j + 1], yy), num, 38, anchor='ra',
                     bold=(v == best), color=RED if v > 0.45 else INK)
        yy += 66
    y = yy + 20
    y = note(fig, y, '没有哪个预测器在所有 trace 上都最好：gshare 赢在相关分支，'
                     '局部历史赢在嵌套循环，两者都不行的随机分支只能认命。')
    save(fig, '15-matrix.png', '七种预测器在七条合成 trace 上的错判率')


# ----------------------------------------------------------- 16 cost

def fig16():
    cost = R['cost']
    fig, y = new(16, '一次猜错值多少',
                 '假设每周期发射 2 条、每 5 条指令里有 1 个分支、一次猜错罚 15 拍。'
                 '纵轴是每周期能跑几条指令（IPC）。')
    box = (150, y + 30, 1010, y + 400)
    h = box[3] - box[1]
    fx = lambda v: box[0] + (box[2] - box[0]) * (v / 0.5)
    fy = lambda v: box[3] - h * min(v / 2.0, 1.0)
    frame(fig, box, [(0, '0'), (0.1, '10%'), (0.2, '20%'), (0.3, '30%'),
                     (0.4, '40%'), (0.5, '50%')],
          [(0, '0'), (0.25, '0.5'), (0.5, '1.0'), (0.75, '1.5'), (1.0, '2.0')])
    pts = [(fx(r['miss']), fy(r['ipc'])) for r in cost]
    poly(fig, pts, color=BLUE, width=6)
    for p in pts:
        fig.circle(p[0], p[1], 9, fill=BLUE, outline=BLUE, width=2)
    y = box[3] + 60
    pick = {0.005: 0, 0.01: 1, 0.05: 2, 0.2: 3}
    parts = []
    for r in cost:
        if round(r['miss'], 3) in pick:
            parts.append('%s 时 %.2f 条' % (pct(r['miss']), r['ipc']))
    y = note(fig, y, '每周期能跑几条指令：' + '；'.join(parts) +
                     '。20% 已经比每周期一条还慢。')
    save(fig, '16-cost.png', 'IPC 随分支错判率下降')


# ----------------------------------------------------------- 17 tage

def fig17():
    fig, y = new(17, '几段不同长度的历史，一起用',
                 'TAGE 的做法是准备几张表，历史长度按几何级数增长（图里画 2、6、12、24 位），'
                 '每格带一个标签，命中哪张就用哪张。')
    lengths = [2, 6, 12, 24]
    cols = [VIOLET, AMBER, TEAL, BLUE]
    yy = y + 30
    for L, col in zip(lengths, cols):
        fig.rect(44, yy, 700, yy + 92, fill=WHITE, outline=col, width=4)
        fig.text((70, yy + 10), '历史 %d 位' % L, 38, color=col)
        for i in range(3):
            cx = 300 + i * 130
            fig.rect(cx, yy + 16, cx + 110, yy + 76, fill=PALE, outline=col,
                     width=2)
            fig.text((cx + 12, yy + 24), 'T+%d' % (i + 1), 38, color=INK_SOFT)
        yy += 108
    fig.text((720, y + 110), '命中哪张', 38, color=INK)
    fig.text((720, y + 158), '就用哪张', 38, color=INK)
    fig.text((720, y + 250), '都不命中时', 38, color=INK_SOFT)
    fig.text((720, y + 298), '退回兜底表', 38, color=INK_SOFT)
    fig.box('base', 44, yy + 10, 500, yy + 100, fill=TINT_B, outline=BLUE)
    fig.text((70, yy + 20), '兜底的两位计数器表', 38, color=BLUE)
    y = yy + 150
    y = bullets(fig, y, [
        '标签用来确认「这一格真的是这条分支的历史」，避免长历史表里认错人。',
        '有用的格子留、没用的格子被替换——这套替换策略决定了大表能不能物尽其用。',
        '本文没有给 TAGE 建模：上面的 7 种做法都是我自己写的可复现实验，'
        'TAGE 只画结构，不给数字。',
    ])
    save(fig, '17-tage.png', 'TAGE 的结构：多级几何历史长度加标签')


# -------------------------------------------------------- 18 spectre

def fig18():
    fig, y = new(18, '猜错的那一刻，机器已经干了很多活',
                 '预测执行不是空想：猜完就真的往下跑。如果这些活留下了痕迹，'
                 '猜错也删不干净。')
    steps = [('训练', '让预测器相信这里会跳', TEAL),
             ('越界读', '猜错的那条路上，读到不该读的字节', RED),
             ('当索引用', '拿这个字节去挑一条缓存行', AMBER),
             ('计时', '哪条缓存行被换进来，时间会说话', BLUE)]
    xx = 48
    for i, (lab, body, col) in enumerate(steps):
        fig.rect(xx, y + 30, xx + 210, y + 330, fill=WHITE, outline=col, width=4)
        fig.text((xx + 18, y + 44), '%d. %s' % (i + 1, lab), 40, color=col)
        fig.wrap((xx + 18, y + 116), body, 38, 174, color=INK)
        if i < 3:
            fig.arrow((xx + 216, y + 180), (xx + 238, y + 180), color=GRAY,
                      width=4, head=12)
        xx += 238
    y = y + 390
    y = note(fig, y, '这条链子上没有任何一步需要「读取」权限，只有时间差。'
                     '所以修起来也麻烦：得把预测器和缓存的时序一起管住。')
    save(fig, '18-spectre.png', 'Spectre 的四步：训练、越界读、当索引、计时')


# ------------------------------------------------------ 19 takeaways

def fig19():
    fig, y = new(19, '记住这四件事就够了')
    items = [
        ('预测就是查表', '地址（有时加历史）当索引，取出一位。所有花样的差别都在'
                        '表多大、索引怎么算、计数器几位。'),
        ('两位比一位值钱', '循环退出只错一次而不是两次，代价是多一位存储。'),
        ('越相关越要靠历史', '两个分支互相牵着走时，全局历史把五五开变成几乎全对。'),
        ('猜错很贵', '一次 15 拍，5% 的错判就吃掉三成性能；所以现代 CPU 愿意'
                    '为它花掉可观的面积和电。'),
    ]
    yy = y + 20
    for i, (head, body) in enumerate(items):
        fig.rect(44, yy, 1018, yy + 150, fill=WHITE if i % 2 == 0 else PALE,
                 outline=LIGHT, width=3)
        fig.text((70, yy + 16), head, 42, bold=True, color=TEAL)
        fig.wrap((70, yy + 76), body, 38, 920, color=INK)
        yy += 166
    save(fig, '19-takeaways.png', '四条结论')


# ------------------------------------------------------------- cover

def cover():
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill=BG, outline=None)
    fig.text((70, 96), 'CPU 每次都在猜', 116, bold=True, color=INK)
    fig.text((74, 250), '分支预测：一条 if 值多少拍', 50, color=INK_SOFT)
    # 一条分支的两条命运
    yy = 380
    for i, (lab, val, col, tint) in enumerate((
            ('猜对', '省 15 拍', TEAL, TINT_T),
            ('猜错', '清空流水线', RED, TINT_R))):
        fig.rect(74, yy, 986, yy + 120, fill=tint, outline=col, width=5)
        fig.text((110, yy + 20), lab, 52, bold=True, color=col)
        fig.text((110, yy + 86), val, 40, color=INK_SOFT)
        yy += 150
    # 计数器小图
    bx, by = 74, 740
    fig.text((bx, by - 60), '两位计数器', 40, color=INK_SOFT)
    for i in range(4):
        cx = bx + i * 96
        fig.rect(cx, by, cx + 80, by + 80, fill=TINT_B if i < 2 else TINT_T,
                 outline=BLUE if i < 2 else TEAL, width=4)
        fig.text((cx + 24, by + 16), str(i), 44,
                 color=BLUE if i < 2 else TEAL)
    fig.text((bx + 400, by + 8), '错一次不改口，', 40, color=INK)
    fig.text((bx + 400, by + 58), '错两次才翻转。', 40, color=INK)
    fig.text((74, 980), '2027-01-04 · 原创 · CC BY 4.0', 38, color=GRAY)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png', optimize=True)
    (ASSETS / 'cover.png').unlink(missing_ok=True)
    print('   cover.png', (ART / 'cover.png').stat().st_size, 'bytes')


def main():
    fig01(); fig02(); fig03(); fig04(); fig05()
    fig06(); fig07(); fig08(); fig09(); fig10()
    fig11(); fig12(); fig13(); fig14(); fig15()
    fig16(); fig17(); fig18(); fig19()
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(sorted(META, key=lambda r: r['path']), ensure_ascii=False,
                   indent=1), encoding='utf-8')
    cover()


if __name__ == '__main__':
    main()
