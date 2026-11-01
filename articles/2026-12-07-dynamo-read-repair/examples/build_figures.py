#!/usr/bin/env python3
"""Original teaching figures for the Dynamo read-repair article. MIT.

Every number printed here is read from results.json, which run_model.py wrote
from the same model module that also draws the ring, so text and pictures
cannot disagree.
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

import dynamo as M

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []
RUNS = {r['name'].split()[0]: r for r in R['runs']}

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


def table(fig, y, cols, rows, size=40, row_h=70, zebra=True):
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


def pct(x, digits=1):
    return ('%.' + str(digits) + 'f%%') % (x * 100)


# ---------------------------------------------------------------- 01

def fig01():
    fig, y = new(1, '三个副本，一个落后',
                 '写请求只要两个副本点头就算成功。第三个副本没被访问，'
                 '它就一直停在旧版本，直到有人去读它，或者后台去比对。')
    top = y + 30

    chip(fig, (60, top + 90, 246, top + 190), '客户端', TINT_B, size=40)
    chip(fig, (300, top + 90, 526, top + 190), '协调者', TINT_T, size=40)

    boxes = []
    for i, (ver, col, tint) in enumerate((('v7', TEAL, TINT_T),
                                          ('v7', TEAL, TINT_T),
                                          ('v5', RED, TINT_R))):
        by = top + 20 + i * 110
        b = (620, by, 880, by + 84)
        chip(fig, b, '副本 %s' % 'ABC'[i], tint, size=40)
        boxes.append(b)
    for i, (ver, col) in enumerate((('v7', TEAL), ('v7', TEAL), ('v5', RED))):
        by = top + 20 + i * 110
        fig.text((1006, by + 20), ver, 42, bold=True, color=col, anchor='ra')

    mid = (top + 20 + 3 * 110) / 2
    fig.arrow((246, mid + 6), (300, mid + 6), color=INK, width=5)
    fig.arrow((526, mid - 10), (620, top + 62), color=TEAL, width=5)
    fig.arrow((526, mid - 10), (620, top + 172), color=TEAL, width=5)
    fig.arrow((526, mid - 10), (620, top + 282), color=GRAY, width=4, dash=10)
    fig.text((552, top + 292), '没访问', 40, color=GRAY)

    y = top + 3 * 110 + 60
    y = note(fig, y, '第三次写没有落在这里：协调者只等两个副本应答就返回了。'
                     '于是 A、B 是 v7，C 是 v5。数据没丢，但同一个键在两个地方'
                     '同时存在两个版本——这就是“最终一致”里“最终”两个字的位置。')
    save(fig, '01-overview.png', '三个副本中有一个落后一个版本')


# ---------------------------------------------------------------- 02

def fig02():
    photo('02-rack.jpg', 'Rear_of_rack_at_NERSC_data_center_-_closeup.jpg',
          '机柜背面的网线与服务器',
          'https://commons.wikimedia.org/wiki/File:Rear_of_rack_at_NERSC_data_center_-_closeup.jpg')


# ---------------------------------------------------------------- 03

def fig03():
    fig, y = new(3, '键落在环上，右边三台是它的副本',
                 '一致性哈希把键和节点放在同一个圆上：从键的位置顺时针走，'
                 '碰到的前三台机器就是它的副本。')
    cx, cy, rad = 531, y + 300, 232
    nodes = [M.Node('n%d' % i) for i in range(8)]
    ring = M.Ring(nodes)
    key = 'k00000'
    pref = ring.preference(key)
    # 节点按各自第一个 token 的角度排到固定的 8 个槽位，避免标签打架
    first = {}
    for tok, name in ring.tokens:
        first.setdefault(name, tok)
    order = sorted(first, key=lambda n: first[n])
    slot = {name: i * (360 / len(order)) for i, name in enumerate(order)}

    for i in range(256):
        tok = ring.tokens[i][0]
        ang = tok / 4294967296.0 * 2 * math.pi - math.pi / 2
        px = cx + rad * math.cos(ang)
        py = cy + rad * math.sin(ang)
        name = ring.tokens[i][1]
        col = TEAL if name in pref else LIGHT
        fig.circle(px, py, 5 if name in pref else 4, fill=col, outline=col, width=1)

    for i, name in enumerate(order):
        ang = slot[name] / 180 * math.pi - math.pi / 2
        lx = cx + (rad + 62) * math.cos(ang)
        ly = cy + (rad + 62) * math.sin(ang)
        hot = name in pref
        anchor = 'ma'
        fig.text((lx, ly - 24), name, 42, bold=hot, anchor=anchor,
                 color=TEAL if hot else INK_SOFT)
        if hot:
            fig.circle(cx + rad * math.cos(ang), cy + rad * math.sin(ang), 15,
                       fill=None, outline=RED, width=5)

    kh = M.fnv1a(key)
    ang = kh / 4294967296.0 * 2 * math.pi - math.pi / 2
    fig.arrow((cx + (rad - 96) * math.cos(ang), cy + (rad - 96) * math.sin(ang)),
              (cx + (rad - 18) * math.cos(ang), cy + (rad - 18) * math.sin(ang)),
              color=AMBER, width=5)
    fig.text((cx - 210, cy - 26), '键 k00000', 42, bold=True, color=AMBER)

    legend_y = cy + rad + 110
    for i, name in enumerate(pref):
        bx = 90 + i * 300
        chip(fig, (bx, legend_y, bx + 260, legend_y + 78),
             '第 %d 副本 %s' % (i + 1, name), TINT_T, size=40)
    fig.text((44, legend_y + 92),
             '环上 8 台机器各占 32 个虚拟节点，共 256 个刻度点。',
             40, color=INK_SOFT)
    save(fig, '03-ring.png', '一致性哈希环与一个键的三个副本')


# ---------------------------------------------------------------- 04

def fig04():
    fig, y = new(4, '读集和写集必须相交',
                 '三个副本，写要落到 W 个，读要问 R 个。只要 R + W 大于副本数，'
                 '两个集合就一定碰面——至少有一个读到的副本见过这次写。')
    y += 20
    for panel, (rw, ok) in enumerate((((2, 2), True), ((1, 1), False))):
        Rq, Wq = rw
        base = y + panel * 330
        label = 'R=2，W=2：相交' if ok else 'R=1，W=1：可能不相交'
        fig.text((44, base), label, 42, bold=True,
                 color=TEAL if ok else RED)
        wy = base + 76
        sets = [(set(range(Wq)), '写集 W=%d' % Wq, TEAL, TINT_T, wy),
                (set(range(Rq)) if ok else {2}, '读集 R=%d' % Rq, BLUE, TINT_B,
                 wy + 96)]
        for cells, name, col, tint, by in sets:
            fig.text((44, by + 4), name, 40, color=col)
            for i in range(3):
                bx = 300 + i * 240
                hot = i in cells
                k = 'p%d_%d_%d' % (panel, i, by)
                fig.box(k, bx, by, bx + 200, by + 74,
                        fill=tint if hot else WHITE,
                        outline=col if hot else LIGHT, width=4 if hot else 3)
                fig.text((bx + 100, by + 14), '副本 %s' % 'ABC'[i], 40,
                         color=INK, anchor='ma', inside=k)
        if ok:
            bx = wy + 96 + 92
            fig.line((302, bx), (738, bx), color=GREEN, width=4)
            fig.line((302, bx - 10), (302, bx + 10), color=GREEN, width=4)
            fig.line((738, bx - 10), (738, bx + 10), color=GREEN, width=4)
            fig.text((302, bx + 12), '两个集合在这里相交', 38, color=GREEN)
    y = y + 2 * 330 + 30
    y = note(fig, y, 'R + W = 4 > 3，两个集合不可能错开。这是“读到的值至少有一份'
                     '是新的”的全部理由——它保证的是集合相交，不是保证写成功，'
                     '也不是保证读到的就是唯一的最新值（并发写会产生兄弟版本）。')
    save(fig, '04-quorum.png', '法定人数读写集的相交关系')


# ---------------------------------------------------------------- 05

def fig05():
    fig, y = new(5, '相交的概率：算出来的',
                 '假设三副本里每个都以固定概率挂掉，随机挑 R 个读、W 个写，'
                 '两万次抽样里读不到最新写的比例。')
    rows = []
    for q in R['quorum']:
        rows.append([
            ('%d / %d' % (q['R'], q['W']), INK, False),
            (pct(q['p_nofail']), RED if q['p_nofail'] > 0.01 else GREEN, False),
            (pct(q['p_fail20']), RED if q['p_fail20'] > 0.01 else GREEN, False),
            (pct(q['p_fail40']), RED if q['p_fail40'] > 0.01 else GREEN, False),
            ('是' if q['safe'] else '否', TEAL if q['safe'] else RED, True),
        ])
    cols = [(60, 'la'), (300, 'la'), (480, 'la'), (660, 'la'), (1010, 'ra')]
    hy = y + 4
    for text, x, anchor in (('R / W', 60, 'la'), ('无故障', 300, 'la'),
                            ('20% 挂', 480, 'la'), ('40% 挂', 660, 'la'),
                            ('相交保证', 1010, 'ra')):
        fig.text((x, hy), text, 40, bold=True, color=INK_SOFT, anchor=anchor)
    fig.line((48, hy + 56), (1014, hy + 56), color=LIGHT, width=3)
    y = table(fig, hy + 70, cols, rows)
    y = note(fig, y, 'R=1、W=1 这一行是反面教材：三副本里各写各的，六成以上的读'
                     '会撞上旧值。R+W>3 的四行在抽样里全部是 0——不是因为运气，'
                     '是因为集合论。故障率再高也不改变这个结论，只改变还能不能'
                     '凑够 R 个和 W 个副本。')
    save(fig, '05-quorum-table.png', '法定人数相交概率表')


# ---------------------------------------------------------------- 06

def fig06():
    fig, y = new(6, '七种策略，四百次故障',
                 '同一套 8 节点、每台 32 个虚拟节点，每步 2% 概率挂掉一台。'
                 '每条横条是“读到旧值的比例”。')
    y += 30
    names = [r['name'] for r in R['runs']]
    top = 0.65
    bw = 400
    bar_h = 52
    for i, r in enumerate(R['runs']):
        by = y + i * 92
        letter = r['name'].split()[0]
        fig.text((44, by + 6), letter, 42, bold=True, color=INK)
        fig.text((96, by + 6), r['name'][2:], 40, color=INK_SOFT)
        v = r['stale_rate']
        w = max(6, int(bw * v / top))
        col = RED if v > 0.2 else AMBER if v > 0.05 else GREEN
        fig.rect(420, by, 420 + w, by + bar_h, fill=col, outline=None)
        fig.text((432 + w, by + 4), pct(v, 1), 40, bold=True, color=INK,
                 allow_overlap=(w < 40))
    y = y + len(R['runs']) * 92 + 10
    y = note(fig, y, 'A 是“只写一份”的基线；G 是相反的极端：写要三份全点头。'
                     'G 的比例不算低，因为写经常凑不齐三份，只落了一部分；'
                     '但只要三份都在，读到的就是当前值，所以它结束时没有落后副本。'
                     'B 到 F 的差别全是“谁来修”的差别。')
    save(fig, '06-stale-bars.png', '七种策略的旧值读取比例')


# ---------------------------------------------------------------- 07

def fig07():
    fig, y = new(7, '一次运行里的落后副本数',
                 '写入一直持续到第 3000 步，之后只读不写。故障窗口在左半边，'
                 '右边是恢复期。')
    tw = R['trace']['twins']
    n = len(tw)
    top = 60
    x0, x1 = 250, 1012
    yy0, yy1 = y + 60, y + 470
    fig.line((x0, yy1), (x1, yy1), color=INK_SOFT, width=4)
    fig.line((x0, yy1), (x0, yy0), color=INK_SOFT, width=4)
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        gx = x0 + (x1 - x0) * frac
        fig.text((gx, yy1 + 16), '%d' % round(frac * n), 38, color=INK_SOFT,
                 anchor='ma')
        fig.line((gx, yy1), (gx, yy1 + 10), color=INK_SOFT, width=3)
    for val in (0, 20, 40, 60):
        gy = yy1 - (yy1 - yy0) * val / top
        fig.text((x0 - 16, gy - 22), str(val), 38, color=INK_SOFT, anchor='ra')
        fig.line((x0 - 10, gy), (x0, gy), color=INK_SOFT, width=3)
    for marker, lab in ((int(R['trace']['chaos_stop'] / n * (x1 - x0)) + x0, '停止故障'),
                        (int(R['trace']['quiet_from'] / n * (x1 - x0)) + x0, '停止写入')):
        fig.line((marker, yy0), (marker, yy1), color=AMBER, width=4, dash=12)
        fig.text((marker + 12, yy0 + 6), lab, 38, color=AMBER)
    prev = None
    for i, v in enumerate(tw):
        px = x0 + (x1 - x0) * i / (n - 1)
        py = yy1 - (yy1 - yy0) * min(v, top) / top
        if prev:
            fig.line(prev, (px, py), color=TEAL, width=4)
        prev = (px, py)
    y = yy1 + 70
    y = note(fig, y, '锯齿是正常的：一次写只覆盖两个副本，落后数就先涨；读碰到旧副本'
                     '就顺手修好，数字再掉。停止写入之后它单调下降——剩下的事'
                     '全部由修复机制完成。')
    save(fig, '07-trace.png', '一次运行中落后副本数随时间的变化')


# ---------------------------------------------------------------- 08

def fig_conv():
    fig, y = new(9, '停止写入以后，多久才干净',
                 '横轴是写入停止之后的读操作次数，纵轴仍然是落后副本数。'
                 '三条线只差“用什么修”。')
    x0, x1 = 250, 1012
    yy0, yy1 = y + 70, y + 460
    top = 240
    fig.line((x0, yy1), (x1, yy1), color=INK_SOFT, width=4)
    fig.line((x0, yy1), (x0, yy0), color=INK_SOFT, width=4)
    for val in (0, 80, 160, 240):
        gy = yy1 - (yy1 - yy0) * val / top
        fig.text((x0 - 16, gy - 22), str(val), 38, color=INK_SOFT, anchor='ra')
    styles = [('C', TEAL, 4, None), ('D', BLUE, 4, None), ('E', AMBER, 5, 14)]
    labels = []
    for letter, col, width, dash in styles:
        r = RUNS[letter]
        qf = r['quiet_from']
        tw = r['twins']
        step = max(1, len(tw) // 160)
        pts = []
        for i in range(0, len(tw), step):
            op = i * (4000 / len(tw))
            if op < qf:
                continue
            px = x0 + (x1 - x0) * (op - qf) / (4000 - qf)
            py = yy1 - (yy1 - yy0) * min(tw[i], top) / top
            pts.append((px, py))
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=col, width=width, dash=dash)
        labels.append((letter, r, col, pts))
    yy = y + 40
    for letter, r, col, pts in labels:
        conv = r['ops_to_converge']
        txt = '%s：%s 次读之后归零' % (letter, conv if conv is not None else '从不')
        fig.text((560, yy), txt, 40, color=col)
        fig.rect(520, yy + 10, 540, yy + 30, fill=col, outline=None)
        yy += 64
    y = yy1 + 60
    y = note(fig, y, '读修复（C）只能修“被读到的那几个副本”，所以它要等旧副本'
                     '轮流出现在读集里。反熵（E）不问读写，自己定期比对，'
                     '所以它最快。这个顺序跟直觉相反：最“主动”的机制最慢，'
                     '因为它依赖运气；后台扫描最“笨”，但它不看运气。')
    save(fig, '09-converge.png', '停止写入后三种修复策略的收敛速度')


# ---------------------------------------------------------------- 09

def fig_repair():
    fig, y = new(8, '读的时候顺手把旧值改掉',
                 '协调者不是把三个副本的回答拼起来给用户，它挑最新的那个返回，'
                 '同时把旧副本改成这个版本。用户根本没感觉到这次写。')
    cols = [('客户端', 120), ('协调者', 380), ('副本 A', 660), ('副本 B', 900)]
    for name, cx in cols:
        chip(fig, (cx - 90, y + 10, cx + 90, y + 88), name, TINT_T, size=40)
        fig.line((cx, y + 88), (cx, y + 520), color=LIGHT, width=3, dash=10)

    msgs = [
        (120, 380, '读 key', 150, TEAL),
        (380, 660, '版本 7', 230, INK_SOFT),
        (380, 900, '版本 5', 300, RED),
        (380, 120, '返回 7', 372, TEAL),
        (380, 900, '写 7', 446, GREEN),
    ]
    for x_from, x_to, label, my, col in msgs:
        fig.arrow((x_from + (20 if x_to > x_from else -20), y + my),
                  (x_to - (20 if x_to > x_from else -20), y + my),
                  color=col, width=5)
        mid = (x_from + x_to) / 2
        fig.text((mid, y + my - 54), label, 40, color=col, anchor='ma')

    y = y + 560
    y = note(fig, y, '副本 B 上这一改，是“读修复”。它不需要用户重试，也不需要'
                     '后台任务，代价是这次读的延迟从两次往返变成两次往返加一次'
                     '异步写。如果 B 当时正好挂了，这次修复就没发生——旧值继续'
                     '留在那里，等下一次有人读它。')
    save(fig, '08-repair-flow.png', '读修复的消息流程')


# ---------------------------------------------------------------- 10

def fig10():
    fig, y = new(10, '副本挂了，写先寄存在别人家里',
                 '被选中的副本不在线，协调者不会干等：它把这次写交给环上另一台'
                 '机器，附一张便条“等 n3 回来交给它”。')
    y += 20
    rows = [
        ('① 写 k 到达', 'n3', '目标副本不在线', TINT_R, RED),
        ('② 转存', 'n6', '多出一条便条：(k, v7)', TINT_A, AMBER),
        ('③ n3 恢复', 'n3', '可以接收数据了', TINT_T, TEAL),
        ('④ 回放', 'n6 → n3', '便条清空，副本补齐', TINT_G, GREEN),
    ]
    for i, (label, box, detail, tint, col) in enumerate(rows):
        by = y + i * 150
        fig.text((44, by + 18), label, 42, bold=True, color=col)
        k = 'h%d' % i
        fig.box(k, 300, by, 540, by + 84, fill=tint, outline=col, width=4)
        fig.text((420, by + 14), box, 40, anchor='ma', inside=k, color=INK)
        fig.text((576, by + 18), detail, 40, color=INK_SOFT)
    y = y + 4 * 150 + 20
    y = note(fig, y, '这就是“松散法定人数”：写的总算还是 W 份，只是第三份'
                     '暂时住在一个不属于这个键的节点上。可用性没有丢，代价是'
                     '这份数据在回放之前不能算“到位”。')
    save(fig, '10-hints.png', '暗示移交的四个步骤')


# ---------------------------------------------------------------- 11

def fig11():
    fig, y = new(11, '便条会过期，过期就没了',
                 '暗示不能无限期留着，默认过一段时间就丢。丢掉的不是数据，是'
                 '“第三份副本”——但恢复就得多走一段路。')
    y += 24
    d, f = RUNS['D'], RUNS['F']
    rows = [
        ('D 不过期', d, TEAL),
        ('F 会过期', f, RED),
    ]
    for i, (label, r, col) in enumerate(rows):
        by = y + i * 170
        fig.text((44, by), label, 42, bold=True, color=col)
        played = r['counters']['hints_played']
        dropped = r['counters']['hints_dropped']
        total = max(played + dropped, 1)
        pw = int(620 * played / total)
        fig.rect(300, by + 10, 300 + pw, by + 74, fill=col, outline=None)
        fig.rect(300 + pw, by + 10, 920, by + 74, fill=GRAY, outline=None)
        if pw > 150:
            fig.text((310, by + 18), '回放 %d' % played, 38, color=WHITE)
        fig.text((44, by + 100), '丢掉 %d 条暗示，旧值读 %.1f%%' %
                 (dropped, r['stale_rate'] * 100), 40, color=INK_SOFT)
    y = y + 2 * 170 + 20
    y = note(fig, y, '两条都收敛了，所以“丢暗示”在这个规模下不是数据丢失，是'
                     '把活儿推给了读修复和反熵。真正会丢数据的情形更苛刻：'
                     '那唯一持有最新版的副本也挂了，而它的暗示恰好过期。')
    save(fig, '11-hint-ttl.png', '暗示回放与丢掉的对比')


# ---------------------------------------------------------------- 12

def fig_merkle():
    m1, m10 = R['merkle1'], R['merkle10']
    fig, y = new(13, '别把所有键拿来比：先比根',
                 '反熵靠哈希树。根一样，整棵子树跳过；不一样才往下钻。'
                 '一个键不一致，只需要交换 %d 个哈希。' % m1['hashes'])
    y += 16
    levels = [('全部键', m1['keys'], '根哈希不同，往下钻', TEAL, TINT_T),
              ('16 个桶', 16, '只有这一个桶不同', AMBER, TINT_A),
              ('桶内 16 页', 16, '只有这一页不同', AMBER, TINT_A),
              ('单个键', 1, '只剩一个叶子', RED, TINT_R)]
    prev = None
    for i, (label, count, detail, col, tint) in enumerate(levels):
        by = y + i * 122
        k = 'lv%d' % i
        fig.box(k, 44, by, 470, by + 86, fill=tint, outline=col, width=4)
        fig.text((60, by + 16), '%s：%d' % (label, count), 40, color=INK,
                 inside=k)
        fig.text((520, by + 16), detail, 40, color=col)
        if prev:
            fig.arrow((257, prev), (257, by), color=GRAY, width=4)
        prev = by + 86
    y = y + 4 * 122 + 10
    small = R['merkle_sweep'][0]
    y = note(fig, y, '4096 个键：一把梭要交换 %d 个哈希，走树只要 %d 个；'
                     '十个键不一致时 %d 个。树上每一层都是整块跳过，'
                     '所以代价跟“有多少不一致”成正比，而不是跟“一共有多少键”'
                     '成正比。' % (m1['naive'], m1['hashes'], m10['hashes']))
    y = note(fig, y, '键很少的时候不划算：%d 个键走树要 %d 个哈希，一把梭才 %d 个。'
                     '树的层数是白送的固定开销，键多到几百以上才开始赚。'
                     % (small['keys'], small['hashes'], small['naive']))
    save(fig, '13-merkle.png', 'Merkle 树对比的代价')


# ---------------------------------------------------------------- 13

def fig_ages():
    fig, y = new(12, '每个副本落后几个版本',
                 '把结束时的全部副本摊开：完全跟上最新版本的、落后一个的、'
                 '落后两个的、落后三个以上的。')
    y += 20
    letters = ['A', 'B', 'C', 'D']
    cols = [TEAL, AMBER, RED, GRAY]
    names = ['跟得上', '落后 1', '落后 2', '落后 3+']
    total = 360
    for gi, letter in enumerate(letters):
        r = RUNS[letter]
        by = y + gi * 130
        fig.text((44, by + 20), letter, 42, bold=True)
        x = 130
        for i, v in enumerate(r['ages']):
            w = max(4, int(760 * v / total))
            fig.rect(x, by, x + w, by + 76, fill=cols[i], outline=None)
            if w > 90:
                fig.text((x + 12, by + 12), str(v), 38, color=WHITE)
            x += w
    ly = y + 4 * 130 + 10
    x = 130
    for i, nm in enumerate(names):
        fig.rect(x, ly, x + 26, ly + 26, fill=cols[i], outline=None)
        fig.text((x + 36, ly - 12), nm, 38, color=INK_SOFT)
        x += 220
    y = ly + 70
    y = note(fig, y, 'A 有一大半副本落后三个版本以上——因为只写一份，另外两份'
                     '永远没人管。B 有一百多个落后到底：W=2 加上没有人修，'
                     '落后者只能靠运气。C、D 全部跟上，但 C 要等几百次读。')
    save(fig, '12-ages.png', '各方案结束时副本落后的版本数分布')


# ---------------------------------------------------------------- 14

def fig14():
    photo('14-hdd.jpg', 'Open_hard-drive.jpg', '拆开的机械硬盘',
          'https://commons.wikimedia.org/wiki/File:Open_hard-drive.jpg')


# ---------------------------------------------------------------- 15

def fig15():
    fig, y = new(15, '两个客户端同时写，得到两个版本',
                 '版本不是时间戳，是一个计数器向量。两个写各改了一处，'
                 '谁也管不到谁，于是两个版本都留着，交给读的人去合并。')
    y += 20
    k1 = 'cl1'
    fig.box(k1, 44, y, 470, y + 130, fill=TINT_B)
    fig.text((60, y + 12), '客户端 1', 40, bold=True, inside=k1, color=INK)
    fig.text((60, y + 70), '写 x=1，版本 (1,0)', 40, color=INK_SOFT, inside=k1)
    k2 = 'cl2'
    fig.box(k2, 512, y, 938, y + 130, fill=TINT_A)
    fig.text((528, y + 12), '客户端 2', 40, bold=True, inside=k2, color=INK)
    fig.text((528, y + 70), '写 y=2，版本 (0,1)', 40, color=INK_SOFT, inside=k2)

    reps = [('副本 A', '版本 (1,0)', 44, 330, TEAL, TINT_T),
            ('副本 B', '版本 (1,1)', 384, 670, AMBER, TINT_A),
            ('副本 C', '版本 (0,1)', 724, 1010, BLUE, TINT_B)]
    ry = y + 250
    for name, ver, x0, x1, col, tint in reps:
        k = 'rp' + name
        fig.box(k, x0, ry, x1, ry + 86, fill=tint, outline=col, width=4)
        fig.text(((x0 + x1) / 2, ry + 14), name, 40, anchor='ma', inside=k,
                 color=INK)
        fig.text(((x0 + x1) / 2, ry + 106), ver, 40, color=col, anchor='ma')
    fig.line((257, y + 130), (187, ry), color=TEAL, width=4, dash=10)
    fig.line((257, y + 130), (527, ry), color=TEAL, width=4, dash=10)
    fig.line((725, y + 130), (527, ry), color=AMBER, width=4, dash=10)
    fig.line((725, y + 130), (867, ry), color=AMBER, width=4, dash=10)
    y = ry + 190
    y = note(fig, y, '读的时候拿到 A 的 (1,0) 和 C 的 (0,1)：两个都不比对方新，'
                     '于是两个都返回，让应用自己合并。这叫兄弟版本。'
                     '“最后写入者赢”能把它压成一个，代价是悄悄丢掉另一个写。')
    save(fig, '15-vector-clock.png', '并发写产生的两个版本')


# ---------------------------------------------------------------- 16

def fig16():
    fig, y = new(16, 'R 越大越准，也越慢',
                 'R 是一次读要等的副本数。等得越多，撞上旧值的机会越小，'
                 '但延迟从“一次往返”变成“三次往返里最慢的那个”。')
    y += 24
    q = {x['R']: x for x in R['quorum'] if x['W'] == 2 or x['R'] == x['W']}
    rows = [
        ('R=1', 1, pct(q[1]['p_fail20']), '最短', RED),
        ('R=2', 2, '0.0%', '两倍往返', TEAL),
        ('R=3', 3, '0.0%', '三倍往返', BLUE),
    ]
    for i, (name, trips, stale, lat, col) in enumerate(rows):
        by = y + i * 130
        fig.text((44, by + 20), name, 44, bold=True, color=col)
        for t in range(trips):
            fig.rect(180 + t * 42, by + 16, 180 + t * 42 + 32, by + 72,
                     fill=col, outline=None)
        fig.text((340, by + 20), '旧值 %s' % stale, 40, color=INK)
        fig.text((640, by + 20), lat, 40, color=INK_SOFT)
    y = y + 3 * 130 + 10
    y = note(fig, y, '表格里的旧值比例是“20% 副本挂掉”时的抽样结果。R=1 时五成'
                     '以上的读会撞上旧值；R=2 起就是 0——但这里有个前提：写真的'
                     '落到了 W 个副本上。挂得太多、W 凑不齐的时候，保证就失效，'
                     '这正是松散法定人数要解决的问题。')
    save(fig, '16-latency.png', 'R 与延迟、旧值比例的权衡')


# ---------------------------------------------------------------- 17

def fig17():
    fig, y = new(17, '从一篇内部论文到默认选项',
                 '这些机制没有一个是 Dynamo 发明的，它的贡献是把它们摆进同一个'
                 '系统，并且证明在商品化硬件上够用。')
    y += 20
    nodes = [('2007', 'Dynamo 论文', 'SOSP，亚马逊内部系统的设计记录'),
             ('2008', 'Cassandra', '开源，分区与副本照搬，冲突判定换成时间戳'),
             ('2009', 'Riak', '把冲突交给应用自己合并'),
             ('2012', 'DynamoDB', '托管服务，冲突被藏起来')]
    top = y + 40
    fig.line((110, top), (110, top + 3 * 150 + 40), color=LIGHT, width=5)
    for i, (year, name, desc) in enumerate(nodes):
        by = top + i * 150
        fig.circle(110, by + 44, 15, fill=TEAL, outline=TEAL)
        fig.text((150, by + 2), year, 42, bold=True, color=TEAL)
        fig.text((300, by + 2), name, 42, bold=True, color=INK)
        fig.text((150, by + 66), desc, 40, color=INK_SOFT)
    y = top + 3 * 150 + 150
    y = note(fig, y, '十年之后，这些东西变成了默认选项：几乎每个云数据库都提供'
                     '“可调一致性”，背后就是 R、W、N 三个旋钮和几套修复机制。')
    save(fig, '17-timeline.png', 'Dynamo 与后续系统的时间线')


# ---------------------------------------------------------------- 18

def fig18():
    fig, y = new(18, '记住这三句')
    y += 26
    y = bullets(fig, y, [
        'R + W > N 保证读集和写集相交，所以只要写真的落到了 W 个副本，'
        '读就不会漏掉最新版本。它保证的是集合，不是成功。',
        'W 小于 N 意味着永远有副本落后。让它收敛的只有三样东西：读修复、'
        '暗示回放、反熵。少了它们，“最终一致”就是“永远不一致”。',
        '修复要花钱：读修复加一次写，暗示要占别人的磁盘，反熵要定期交换'
        '哈希。这些钱换来的是可用性——机器挂了，写还能成功。',
    ])
    y += 10
    y = note(fig, y, '反过来用也成立：如果不能接受读到旧值，就把 R 调大或者'
                     '要求写入走一个真正的共识协议；如果只是想让监控图表好看，'
                     'R=1 也许就够了。', color=INK_SOFT)
    save(fig, '18-takeaways.png', '全文结论')


# ---------------------------------------------------------------- cover

def cover():
    fig = Fig(1080, bg=BG, width=1080)
    fig.text((60, 150), '三个副本，', 84, bold=True, color=INK)
    fig.text((60, 258), '一个落后', 84, bold=True, color=INK)
    fig.text((60, 400), '法定人数、读修复', 44, color=INK_SOFT)
    fig.text((60, 462), '与暗示移交', 44, color=INK_SOFT)

    for i, (ver, col, tint) in enumerate((('v7', TEAL, TINT_T),
                                          ('v7', TEAL, TINT_T),
                                          ('v5', RED, TINT_R))):
        by = 150 + i * 120
        k = 'cv%d' % i
        fig.box(k, 760, by, 1020, by + 92, fill=tint, outline=col, width=5)
        fig.text((890, by + 18), ver, 44, bold=True, color=col, anchor='ma',
                 inside=k)

    fig.text((1020, 560), '最终一致', 42, color=TEAL, anchor='ra')

    cx, cy, rad = 540, 760, 150
    for i in range(120):
        ang = i / 120 * 2 * math.pi
        px, py = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
        fig.circle(px, py, 4, fill=LIGHT, outline=LIGHT, width=1)
    for ang, col, tint in ((-math.pi / 2, TEAL, TINT_T), (0.6, TEAL, TINT_T),
                           (2.4, RED, TINT_R)):
        px, py = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
        fig.circle(px, py, 40, fill=tint, outline=col, width=6)
    fig.text((60, 930), 'tech-articles', 42, color=GRAY)

    row = fig.save(ASSETS / 'cover.png', '封面：三个副本，一个落后')
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    (ASSETS / 'cover.png').unlink()
    print('   cover.png', (ART / 'cover.png').stat().st_size, 'B')


# ---------------------------------------------------------------- main

def main():
    fig01()
    fig02()
    fig03()
    fig04()
    fig05()
    fig06()
    fig07()
    fig_repair()
    fig_conv()
    fig10()
    fig11()
    fig_ages()
    fig_merkle()
    fig14()
    fig15()
    fig16()
    fig17()
    fig18()
    cover()
    META.sort(key=lambda r: r['path'])
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, indent=1, ensure_ascii=False) + '\n')
    print('  %d figures' % len(META))


if __name__ == '__main__':
    main()
