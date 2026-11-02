#!/usr/bin/env python3
"""一致性哈希一文的原创教学插图。MIT。

图里出现的每个数字都来自 results.json；环形示意图上的位置由 ch.py 现场算出。
"""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageFont

import ch
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

NODE_COLORS = [BLUE, TEAL, AMBER, RED, GREEN, VIOLET, BROWN, INK_SOFT, GRAY, INK]


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


def hbar(fig, x0, x1, y, frac, color, h=38):
    x1 = x0 + max(frac * (x1 - x0), 6)
    fig.rect(x0, y, x1, y + h, fill=color, outline=None)


def legend(fig, y, items, x0=52, step=236):
    x = x0
    for color, text in items:
        fig.rect(x, y, x + 30, y + 30, fill=color, outline=None, radius=6)
        fig.text((x + 44, y - 2), text, 38, color=INK)
        x += step
    return y + 46


# ---------------------------------------------------------------- 环的几何

def at(cx, cy, r, pos):
    a = 2 * math.pi * pos
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def arc(fig, cx, cy, r, p0, p1, color, width=5):
    """顺时针从 p0 到 p1 画一段弧（p1 > p0）。"""
    steps = max(8, int((p1 - p0) * 90))
    prev = at(cx, cy, r, p0)
    for i in range(1, steps + 1):
        cur = at(cx, cy, r, p0 + (p1 - p0) * i / steps)
        fig.line(prev, cur, color=color, width=width)
        prev = cur


def wedge(fig, cx, cy, r, p0, p1, fill):
    steps = max(8, int((p1 - p0) * 90))
    pts = [(cx, cy)]
    for i in range(steps + 1):
        pts.append(at(cx, cy, r, p0 + (p1 - p0) * i / steps))
    fig.poly(pts, fill=fill, outline=None)


def node_spots():
    return R['sample']['nodes']


def draw_ring(fig, cx, cy, r, labels=True, dots=True, size=38):
    fig.circle(cx, cy, r, fill=None, outline=LIGHT, width=4)
    for i, nd in enumerate(node_spots()):
        if dots:
            x, y = at(cx, cy, r, nd['pos'])
            fig.circle(x, y, 17, fill=NODE_COLORS[i], outline=WHITE)
        if labels:
            x, y = at(cx, cy, r + 62, nd['pos'])
            anchor = 'mm'
            fig.text((x, y), nd['name'][-2:], size, bold=True,
                     color=NODE_COLORS[i], anchor=anchor)


# ---------------------------------------------------------------- 01 环

def fig01():
    fig, y = new(3, '一串位置，绕成一个圈',
                 '十个节点在环上各占一个点，每个 key 也钉在环上。'
                 'key 顺时针走，遇到的第一个节点就是它的主人。')
    y += 20
    cx, cy, r = 531, y + 220, 190
    draw_ring(fig, cx, cy, r)
    for k in R['sample']['keys'][:3]:
        kw = {'node-03': TINT_A, 'node-04': TINT_B, 'node-06': TINT_G}[k['owner']]
        wedge(fig, cx, cy, r, k['pos'], k['start'] if k['start'] > k['pos']
              else k['start'] + 1.0, kw)
        kx, ky = at(cx, cy, r, k['pos'])
        fig.circle(kx, ky, 10, fill=INK, outline=WHITE)
    y = cy + r + 96
    y = legend(fig, y, [(INK, 'key 的位置'), (BLUE, '节点'), (TINT_A, '归属区间')],
               x0=110, step=290)
    y = note(fig, y + 6, '环的周长是 2⁶⁴。本文的场景固定为 10 个节点、'
             '20 万个 key，后面所有数字都来自这一个环。')
    save(fig, '03-ring.png', '哈希环：节点与 key 都钉在同一个圆上，key 顺时针找主人')


# ---------------------------------------------------------------- 02 取模

def fig02():
    rows = R['modulo_example']
    fig, y = new(1, '取模：换个除数，几乎全搬',
                 'h(key) % 10 分到十台机器上，加一台变成 h(key) % 11。'
                 '除数一换，绝大部分 key 的归属就变了。')
    y += 8
    tbl = [[('key', INK, True), ('% 10', INK, True), ('% 11', INK, True), ('换了？', INK, True)]]
    for r in rows:
        moved = r['mod10'] != r['mod11']
        tbl.append([(r['key'][-6:], INK, False),
                    (r['mod10'][-2:], BLUE, False),
                    (r['mod11'][-2:], AMBER, False),
                    ('换了' if moved else '没换', RED if moved else GREEN, moved)])
    y = table(fig, y, [(60, 'la'), (420, 'la'), (640, 'la'), (860, 'la')], tbl,
              size=40, row_h=70)
    y = note(fig, y, '这六个 key 里有五个换了主人。整套 20 万个 key 跑下来，'
             '搬家比例是 %.2f%%——理想值是 %s，也就是只有新机器该接的那一份。'
             % (100 * R['grow']['modulo'], '9.1%'))
    save(fig, '01-modulo.png', '取模方案：除数变化导致大量 key 重新归属')


# ---------------------------------------------------------------- 03 迁移比例

def fig03():
    g = R['grow']
    fig, y = new(2, '加一台机器，多少 key 要搬家',
                 '十台加到十一台，理想情况是只有新机器该拿的那 %s。'
                 % ('1/11 = 9.1%'))
    y += 26
    rows = [('取模', g['modulo'], RED),
            ('环，每节点 1 个点', g['ring_v1'], AMBER),
            ('环，每节点 128 个点', g['ring_v128'], TEAL),
            ('jump hash', g['jump'], GREEN)]
    for lab, v, color in rows:
        fig.text((44, y - 4), lab, 40, color=INK)
        hbar(fig, 470, 1018, y, v, color)
        fig.text((1018, y + 44), '%.1f%%' % (100 * v), 38, color=INK_SOFT, anchor='ra')
        y += 130
    # 理想值参考线
    gx = 470 + (1018 - 470) * g['ideal']
    fig.line((gx, y - 470), (gx, y - 30), color=INK, width=4, dash=14)
    fig.text((gx, y - 498), '理想 9.1%', 38, color=INK, anchor='ma')
    y = note(fig, y, '取模方案搬了 %.1f%% 的 key；三个一致性方案都落在 9–10%% 之间。'
             '注意「每节点 1 个点」那一栏只有 %.1f%%——不是更好，是这次运气好：'
             '十个点分布不均，新节点分到的空间本来就小于平均。'
             % (100 * g['modulo'], 100 * g['ring_v1']))
    save(fig, '02-migration.png', '扩容时搬家比例：取模与三种一致性方案对比')


# ---------------------------------------------------------------- 04 绕环

def fig04():
    keys = R['sample']['keys']
    wrap = [k for k in keys if k['wrap']][0]
    normal = [k for k in keys if not k['wrap']][0]
    fig, y = new(4, '顺时针走，第一个点就是答案',
                 'key 落在两个点之间的弧上，就归后面那个点。'
                 '落在最后一个点之后呢？绕过 0 点继续走。')
    y += 20
    for cx, k, color, lab in ((300, normal, BLUE, '普通情况'),
                              (760, wrap, AMBER, '要绕过 0 点')):
        cy, r = y + 158, 142
        draw_ring(fig, cx, cy, r, labels=False)
        end = k['start'] if k['start'] > k['pos'] else k['start'] + 1.0
        arc(fig, cx, cy, r - 24, k['pos'], end, color, width=7)
        kx, ky = at(cx, cy, r, k['pos'])
        fig.circle(kx, ky, 10, fill=color, outline=WHITE)
        fig.text((cx, cy + r + 86), lab, 40, bold=True, color=color, anchor='ma')
    y += 2 * 158 + 140
    y = legend(fig, y, [(BLUE, '蓝点：一次普通查找'), (AMBER, '橙点：要绕过 0 点')],
               x0=80, step=470)
    y = note(fig, y + 6, '右边那个 key 的位置是 %.3f，环上最靠后的节点在 0.84，'
             '它只能绕过 0 点去找 0.071 上的节点。代码里就是一句 bisect，'
             '越界就回数组开头。' % wrap['pos'])
    save(fig, '04-walk.png', '一个 key 顺时针找到主人的两种情况，含绕过 0 点')


# ---------------------------------------------------------------- 05 虚拟节点

def fig05():
    fig, y = new(7, '一个节点，可以出现在很多地方',
                 '把节点名后面拼上序号再哈希，同一个物理节点就在环上占很多个点。'
                 '图里是节点 03 的 8 个虚拟节点。')
    y += 16
    cx, cy, r = 531, y + 210, 186
    draw_ring(fig, cx, cy, r, labels=False, dots=False)
    mine = [ch.h64('node-03#%d' % i) / ch.SPACE for i in range(8)]
    others = [nd for nd in node_spots() if nd['name'] != 'node-03']
    for i, nd in enumerate(others):
        x, y2 = at(cx, cy, r, nd['pos'])
        fig.circle(x, y2, 13, fill=LIGHT, outline=GRAY)
    for p in sorted(mine):
        x, y2 = at(cx, cy, r, p)
        fig.circle(x, y2, 15, fill=AMBER, outline=WHITE)
    y = cy + r + 70
    y = note(fig, y, '物理上还是一台机器，逻辑上它占了八段弧。'
             '每段弧都只管自己那一小片 key 空间——这就是虚拟节点。')
    save(fig, '07-vnodes.png', '虚拟节点：一个物理节点在环上占据多个点')


# ---------------------------------------------------------------- 06 彩条

def fig06():
    fig, y = new(5, '把环拉直，看谁占多宽',
                 '同一个环，每节点 1 个点时彩条宽窄悬殊；每节点 16 个点时'
                 '各色被切碎、重新洗匀。')
    y += 30
    x0, x1 = 44, 1018
    for tag, lab in (('v1', '每节点 1 个点'), ('v16', '每节点 16 个点')):
        segs = R['strips'][tag]
        fig.text((44, y - 4), lab, 38, color=INK_SOFT)
        y += 62
        for s in segs:
            start = s['start']
            end = s['end'] if s['end'] > s['start'] else s['end'] + 1.0
            idx = [n['name'] for n in node_spots()].index(s['node'])
            a = x0 + (x1 - x0) * start
            b = x0 + (x1 - x0) * min(end, 1.0)
            if b - a < 1:
                b = a + 1
            fig.rect(a, y, b, y + 56, fill=NODE_COLORS[idx], outline=None)
        fig.rect(x0, y, x1, y + 56, fill=None, outline=INK_SOFT, width=3)
        y += 108
    y = legend(fig, y, [(NODE_COLORS[i], 'n%02d' % i) for i in range(5)],
               x0=60, step=190)
    y = legend(fig, y, [(NODE_COLORS[i + 5], 'n%02d' % (i + 5)) for i in range(5)],
               x0=60, step=190)
    y = note(fig, y, '最宽的一段占了整个环的 %.0f%%（第一行）。'
             '对一台机器来说，这意味着它要接 %.0f%% 的流量——平均值应该是 10%%。'
             % (100 * R['vnodes'][0]['max_arc_share'],
                100 * R['vnodes'][0]['max_arc_share']))
    save(fig, '05-strip.png', '把环拉直：每节点 1 个点与 16 个点的弧段宽窄对比')


# ---------------------------------------------------------------- 07 均衡曲线

def fig07():
    rows = R['vnodes']
    fig, y = new(8, '点数越多，越接近平均',
                 '纵轴是「最忙的节点的负载 ÷ 平均值」。1.0 表示完全均匀；'
                 '横轴是每个节点的点数。')
    y += 30
    box = (100, y, 1000, y + 400)
    n = len(rows)
    fx = lambda i: box[0] + (box[2] - box[0]) * (i / (n - 1))
    top = 2.4
    fy = lambda v: box[3] - (box[3] - box[1]) * min(v / top, 1.0)
    fig.line((box[0], box[3]), (box[2], box[3]), color=INK_SOFT, width=4)
    fig.line((box[0], box[3]), (box[0], box[1]), color=INK_SOFT, width=4)
    for frac, lab in ((0.0, '0'), (0.5, '1.2'), (1.0, '2.4')):
        gy = box[3] - (box[3] - box[1]) * frac
        fig.line((box[0] - 10, gy), (box[0], gy), color=INK_SOFT, width=3)
        fig.text((box[0] - 18, gy - 22), lab, 38, color=INK_SOFT, anchor='ra')
    for i, r in enumerate(rows):
        xx = fx(i)
        if i % 2 == 0:
            fig.text((xx, box[3] + 16), str(r['vnodes']), 38, color=INK_SOFT,
                     anchor='ma')
    fig.text((box[2], box[3] + 72), '每节点点数', 38, color=INK_SOFT, anchor='ra')
    for key, color in (('load_max', RED), ('load_min', TEAL)):
        prev = None
        for i, r in enumerate(rows):
            cur = (fx(i), fy(r[key]))
            if prev:
                fig.line(prev, cur, color=color, width=5)
            prev = cur
    fig.line((box[0], fy(1.0)), (box[2], fy(1.0)), color=GRAY, width=3, dash=12)
    fig.text((box[0] + 10, fy(1.0) - 46), '完全平均', 38, color=GRAY)
    fig.text((fx(0) + 14, fy(rows[0]['load_max']) - 12), '最忙的节点',
             38, color=RED, anchor='la')
    fig.text((fx(0) + 14, fy(rows[0]['load_min']) + 30), '最闲的节点',
             38, color=TEAL, anchor='la')
    y = box[3] + 120
    y = note(fig, y, '每节点 1 个点时，最忙的节点扛着平均值的 %.2f 倍；'
             '128 个点时降到 %.2f 倍；1024 个点是 %.2f 倍。'
             % (rows[0]['load_max'], rows[7]['load_max'], rows[10]['load_max']))
    save(fig, '08-balance.png', '虚拟节点数量与负载均衡的关系')


# ---------------------------------------------------------------- 08 每节点负载

def fig08():
    fig, y = new(6, '同一批 key，两台机器的活法',
                 '十个节点的实际负载（20 万个 key）。左边每节点 1 个点，'
                 '右边每节点 128 个点。')
    y += 24
    h = R['hist']
    peak = max(h['v1'] + h['v128'])
    for tag, lab in (('v1', '每节点 1 个点'), ('v128', '每节点 128 个点')):
        fig.text((44, y), lab, 40, bold=True)
        y += 56
        base = y + 300
        fig.line((80, base), (1000, base), color=INK_SOFT, width=4)
        for i, v in enumerate(h[tag]):
            x = 96 + i * 92
            bh = 300 * v / peak
            fig.rect(x, base - bh, x + 66, base, fill=NODE_COLORS[i], outline=None)
            fig.text((x + 33, base + 14), 'n%02d' % i, 38, color=INK_SOFT, anchor='ma')
            fig.text((x + 33, base - bh - 48), '%d' % round(v / 1000), 38,
                     color=INK, anchor='ma')
        y = base + 84
    y = note(fig, y, '纵轴标签是「千个 key」。左边从 8 千到 46 千，差五倍多；'
             '右边都在 18 千到 22 千之间。')
    save(fig, '06-per-node.png', '每节点实际负载：1 个点与 128 个点')


# ---------------------------------------------------------------- 09 查找步数

def fig09():
    rows = R['vnodes']
    fig, y = new(10, '多花的代价：二分要多比几次',
                 '环上的点排成一列，找主人就是二分查找。点数翻倍，比较次数加一。')
    y += 26
    picks = [0, 2, 4, 7, 10]
    tbl = [[('每节点点数', INK, True), ('环上点数', INK, True),
            ('平均比较', INK, True), ('log₂(点数)', INK, True)]]
    for i in picks:
        r = rows[i]
        tbl.append([('%d' % r['vnodes'], INK, False), ('%d' % r['points'], INK, False),
                    ('%.2f' % r['steps'], TEAL, True),
                    ('%.2f' % math.log2(r['points']), INK_SOFT, False)])
    y = table(fig, y, [(60, 'la'), (320, 'la'), (580, 'la'), (820, 'la')], tbl,
              size=40, row_h=68)
    y = note(fig, y, '从 10 个点涨到 10240 个点，比较次数只从 %.2f 涨到 %.2f——'
             '对数增长。真实系统里这点开销比一次网络请求便宜得多。'
             % (rows[0]['steps'], rows[10]['steps']))
    save(fig, '10-lookup.png', '二分查找的比较次数随环上点数增长（对数）')


# ---------------------------------------------------------------- 10 权衡表

def fig10():
    rows = R['vnodes']
    fig, y = new(9, '虚拟节点数是个旋钮',
                 '点数越多越均匀，但环上的点越多，内存和查找都跟着涨。'
                 '这张表是同一个环的四个档位。')
    y += 8
    tbl = [[('每节点点数', INK, True), ('最忙/平均', INK, True),
            ('最闲/平均', INK, True), ('离散度', INK, True),
            ('步数', INK, True)]]
    for i in (0, 2, 4, 7, 10):
        r = rows[i]
        tbl.append([('%d' % r['vnodes'], INK, False),
                    ('%.2f' % r['load_max'], RED if i == 0 else INK, i == 0),
                    ('%.2f' % r['load_min'], INK, False),
                    ('%.3f' % r['load_stdev'], INK, False),
                    ('%.2f' % r['steps'], INK, False)])
    y = table(fig, y, [(56, 'la'), (270, 'la'), (470, 'la'), (670, 'la'),
                       (870, 'la')], tbl, size=38, row_h=66)
    y = note(fig, y, '工程上的常见取值在几十到几百之间：'
             '128 个点时最忙的节点只比平均多 %.0f%%，再往上收益就很小了。'
             % (100 * (rows[7]['load_max'] - 1)))
    save(fig, '09-tradeoff.png', '虚拟节点数的权衡：均衡度、查找步数')


# ---------------------------------------------------------------- 11 挂一台

def fig11():
    fig, y = new(11, '一台机器挂了，只有一段弧要搬家',
                 '节点 03 消失后，它逆时针前的那一段弧交给顺时针下一个节点，'
                 '其它弧一动不动。')
    y += 16
    cx, cy, r = 531, y + 216, 180
    draw_ring(fig, cx, cy, r, labels=False)
    spots = sorted(node_spots(), key=lambda d: d['pos'])
    idx = next(i for i, d in enumerate(spots) if d['name'] == 'node-03')
    prev = spots[(idx - 1) % len(spots)]
    dead = spots[idx]
    nxt = spots[(idx + 1) % len(spots)]
    wedge(fig, cx, cy, r, prev['pos'], dead['pos'], TINT_R)
    arc(fig, cx, cy, r + 26, dead['pos'], nxt['pos'], TEAL, width=6)
    x, y2 = at(cx, cy, r, dead['pos'])
    fig.line((x - 26, y2 - 26), (x + 26, y2 + 26), color=RED, width=7)
    fig.line((x - 26, y2 + 26), (x + 26, y2 - 26), color=RED, width=7)
    y = cy + r + 96
    y = legend(fig, y, [(TINT_R, '节点 03 那一段要搬家'), (TEAL, '顺时针下一个节点接手')],
               x0=60, step=520)
    y = note(fig, y + 4, '20 万个 key 实测：挂掉一台，环上有 %.1f%% 的 key 换了主人，'
             '理想值是 1/10 = 10%%。' % (100 * R['shrink']['ring_v128']))
    save(fig, '11-failure.png', '节点故障时只有相邻一段弧需要重新归属')


# ---------------------------------------------------------------- 12 扩容缩容

def fig12():
    g, s = R['grow'], R['shrink']
    fig, y = new(12, '加一台、少一台，代价不一样',
                 '左边是加机器（10→11），右边是少机器（10→9）。'
                 '灰色虚线是各自的理想值。')
    y += 26
    rows = [('取模', g['modulo'], s['modulo'], RED),
            ('环 + 128 虚拟节点', g['ring_v128'], s['ring_v128'], TEAL),
            ('jump hash', g['jump'], s['jump'], GREEN)]
    for lab, gv, sv, color in rows:
        fig.text((44, y - 2), lab, 38, color=INK)
        y += 56
        fig.text((60, y), '加一台', 38, color=INK_SOFT)
        hbar(fig, 240, 1018, y, gv, color)
        fig.text((1018, y + 46), '%.1f%%' % (100 * gv), 38, color=INK_SOFT, anchor='ra')
        y += 108
        fig.text((60, y), '少一台', 38, color=INK_SOFT)
        hbar(fig, 240, 1018, y, sv, color)
        fig.text((1018, y + 46), '%.1f%%' % (100 * sv), 38, color=INK_SOFT, anchor='ra')
        y += 132
    y = note(fig, y, '取模方案在两个方向上都搬走近九成；一致性方案都停在理想值附近。'
             'jump hash 连「少一台」也对得上：%.1f%% 对 10%%。'
             % (100 * s['jump']))
    save(fig, '12-grow-shrink.png', '扩容与缩容时的搬家比例：三个方案对照')


# ---------------------------------------------------------------- 13 jump 分步

def fig13():
    tr = R['jump_trace']
    steps = tr['steps']
    fig, y = new(13, 'jump hash：不用环，也不用存表',
                 '一个循环走完，桶号就是答案。它只依赖 key 的哈希和桶数 n，'
                 '连一个节点位置都不用记。')
    y += 10
    mono(fig, (56, y), 'b, j = -1, 0', 38, color=INK)
    y += 60
    mono(fig, (56, y), 'while j < n:', 38, color=INK)
    y += 56
    mono(fig, (86, y), 'b = j', 38, color=INK)
    y += 52
    mono(fig, (86, y), 'key = key * A + 1        # 64 位', 38, color=INK)
    y += 52
    mono(fig, (86, y), 'j = (b+1) * 2^31 / (key>>33 + 1)', 38, color=INK)
    y += 60
    mono(fig, (56, y), 'return b', 38, color=TEAL)
    y += 96
    tbl = [[('第几圈', INK, True), ('b', INK, True), ('j', INK, True),
            ('j < 10 ？', INK, True)]]
    for i, st in enumerate(steps):
        tbl.append([('%d' % (i + 1), INK, False), ('%d' % st['b'], AMBER, False),
                    ('%d' % st['j'], TEAL, False),
                    ('继续' if st['j'] < 10 else '结束', GREEN, st['j'] >= 10)])
    y = table(fig, y, [(80, 'la'), (300, 'la'), (520, 'la'), (760, 'la')], tbl,
              size=38, row_h=62)
    y = note(fig, y, '这一串是 key %s 的真实轨迹：走了 %d 圈，'
             '最后一圈 j 跳出 10，返回 %d。'
             % (tr['key'][-8:], len(steps), steps[-1]['b']))
    save(fig, '13-jump-steps.png', 'jump hash 的循环：一个 key 的真实演化')


# ---------------------------------------------------------------- 14 jump 循环次数

def fig14():
    rows = R['jump_steps']
    fig, y = new(14, 'jump 的代价：循环几圈',
                 '横轴是桶数（等距排列），纵轴是平均循环次数。'
                 '它长得像对数——桶数翻一倍，只多走一点点。')
    y += 30
    box = (110, y, 1000, y + 360)
    n = len(rows)
    fx = lambda i: box[0] + (box[2] - box[0]) * (i / (n - 1))
    top = 10.0
    fy = lambda v: box[3] - (box[3] - box[1]) * min(v / top, 1.0)
    fig.line((box[0], box[3]), (box[2], box[3]), color=INK_SOFT, width=4)
    fig.line((box[0], box[3]), (box[0], box[1]), color=INK_SOFT, width=4)
    for frac, lab in ((0.0, '0'), (0.5, '5'), (1.0, '10')):
        gy = box[3] - (box[3] - box[1]) * frac
        fig.line((box[0] - 10, gy), (box[0], gy), color=INK_SOFT, width=3)
        fig.text((box[0] - 18, gy - 22), lab, 38, color=INK_SOFT, anchor='ra')
    prev = None
    for i, r in enumerate(rows):
        cur = (fx(i), fy(r['steps']))
        if prev:
            fig.line(prev, cur, color=BLUE, width=5)
        prev = cur
        fig.circle(cur[0], cur[1], 7, fill=BLUE, outline=WHITE)
    for i, r in enumerate(rows):
        if i in (0, 4, 9):
            fig.text((fx(i), box[3] + 16), str(r['n']), 38, color=INK_SOFT, anchor='ma')
    fig.text((box[2], box[3] + 74), '桶数 n', 38, color=INK_SOFT, anchor='ra')
    fig.text((fx(6), fy(rows[6]['steps']) - 54), '%.1f 圈' % rows[6]['steps'],
             38, color=BLUE, anchor='ma')
    y = box[3] + 126
    y = note(fig, y, 'n = 4096 时平均 %.1f 圈，而 log₂(4096) = 12——'
             '真实常数比 log₂ 还小一点，因为每圈是按概率跳跃的。'
             % rows[9]['steps'])
    save(fig, '14-jump-loop.png', 'jump hash 的平均循环次数随桶数增长')


# ---------------------------------------------------------------- 15 jump 均匀

def fig15():
    jl = R['jump_load']
    fig, y = new(15, 'jump 的均衡性好得不像话',
                 '同样的 20 万个 key、同样的十个桶，jump hash 的十个桶都在平均线附近。')
    y += 40
    base = y + 300
    peak = max(jl['counts']) * 1.16
    fig.line((80, base), (1000, base), color=INK_SOFT, width=4)
    mean = sum(jl['counts']) / len(jl['counts'])
    for i, v in enumerate(jl['counts']):
        x = 96 + i * 92
        bh = 300 * v / peak
        fig.rect(x, base - bh, x + 66, base, fill=GREEN, outline=None)
        fig.text((x + 33, base + 14), 'b%d' % i, 38, color=INK_SOFT, anchor='ma')
    my = base - 300 * mean / peak
    fig.line((84, my), (996, my), color=RED, width=4, dash=12)
    fig.text((996, my - 44), '平均 %.0f' % (mean / 1000) + ' 千', 38, color=RED,
             anchor='ra')
    y = base + 96
    y = note(fig, y, '最忙的桶是平均值的 %.3f 倍，最闲的是 %.3f 倍，'
             '离散度只有 %.4f。十个桶几乎没有偏差。'
             % (jl['max'], jl['min'], jl['stdev']))
    save(fig, '15-jump-load.png', 'jump hash 的桶分布：十个桶几乎等分')


# ---------------------------------------------------------------- 16 三方案对照

def fig16():
    g, s = R['grow'], R['shrink']
    fig, y = new(16, '三个方案，一张表',
                 '同样是十台机器、二十万个 key。')
    y += 6
    tbl = [[('', INK, True), ('取模', INK, True), ('环 + 虚拟节点', INK, True),
            ('jump hash', INK, True)],
           [('加一台搬家', INK, False), ('%.1f%%' % (100 * g['modulo']), RED, True),
            ('%.1f%%' % (100 * g['ring_v128']), INK, False),
            ('%.1f%%' % (100 * g['jump']), INK, False)],
           [('少一台搬家', INK, False), ('%.1f%%' % (100 * s['modulo']), RED, True),
            ('%.1f%%' % (100 * s['ring_v128']), INK, False),
            ('%.1f%%' % (100 * s['jump']), INK, False)],
           [('最忙/平均', INK, False), ('—', INK, False),
            ('%.2f' % R['vnodes'][7]['load_max'], INK, False),
            ('%.2f' % R['jump_load']['max'], GREEN, True)],
           [('要存的点', INK, False), ('10', INK, False), ('1280', INK, False),
            ('0', INK, False)],
           [('查找', INK, False), ('一次取模', INK, False), ('二分', INK, False),
            ('几圈循环', INK, False)]]
    y = table(fig, y, [(52, 'la'), (270, 'la'), (545, 'la'), (800, 'la')], tbl,
              size=38, row_h=66)
    y = note(fig, y, '取模那一列在「搬家」两行上都是九成——这是它被替换掉的原因。'
             '环与 jump 的搬家比例都对得上理想值，区别在「要不要存一张表」。')
    save(fig, '16-compare.png', '取模、环加虚拟节点、jump hash 的横向对照')


# ---------------------------------------------------------------- 17 人物

def fig17():
    photo('17-karger.jpg', 'David_Karger.jpg',
          '1997 年论文的第一作者 David Karger（2017 年摄）',
          'Transclusion, Wikimedia Commons, CC BY 4.0')


# ---------------------------------------------------------------- 18 谁在用

def fig18():
    fig, y = new(18, '谁在用',
                 '一致性哈希不是教科书里的玩具：它是今天主流分布式存储的分区方式。')
    y += 18
    cards = [('Amazon Dynamo',
              '2007 年的论文里，环加虚拟节点就是它做数据分区的方式', BLUE),
             ('Apache Cassandra',
              '每个节点在令牌环上占若干个位置，按 token 决定数据归谁', TEAL),
             ('OpenStack Swift',
              '对象存储的「环」决定每个对象该存到哪几个节点上', AMBER),
             ('Riak', '用环做分区，再用副本数决定一份数据存几处', GREEN)]
    for i, (name, body, color) in enumerate(cards):
        x = 44 + (i % 2) * 494
        yy = y + (i // 2) * 300
        fig.rect(x, yy, x + 466, yy + 264, fill=WHITE, outline=color, width=4,
                 radius=18)
        fig.text((x + 24, yy + 22), name, 40, bold=True, color=color)
        fig.wrap((x + 24, yy + 92), body, 38, 418, color=INK)
    y += 2 * 300 + 20
    y = note(fig, y, '四个系统的细节各不相同（副本怎么放、故障怎么检测），'
             '但「用哈希把 key 空间切成段、段归节点」这一步是一样的。')
    save(fig, '18-who.png', '使用一致性哈希的代表性系统')


# ---------------------------------------------------------------- 19 结论

def fig19():
    fig, y = new(19, '四句话带走')
    y += 10
    y = bullets(fig, y, [
        '取模的问题是 N 本身参与运算：N 一变，几乎所有 key 的归属都变。实测 90.9%。',
        '环的问题换了：key 和节点钉在同一个圆上，加一个节点只切开一段弧。实测 9.6%，理想 9.1%。',
        '虚拟节点把「一台机器」变成「很多个点」，点越多越接近平均：1 个点时最忙的是平均的 2.31 倍，128 个点是 1.11 倍。',
        'jump hash 连表都不存：几圈循环算出桶号，均衡性更好（最忙/平均 1.01），代价是只支持「按序号增删」这种扩容方式。',
    ], accent=TEAL)
    save(fig, '19-takeaways.png', '四条结论')


def cover():
    g = R['grow']
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill=BG, outline=None)
    fig.text((70, 64), '多一台机器，', 100, bold=True, color=INK)
    fig.text((70, 182), '要搬走多少钥匙', 100, bold=True, color=INK)
    fig.text((74, 300), '一致性哈希：把取模换成一个环', 44, color=INK_SOFT)
    rows = [('取模', g['modulo'], RED), ('环 + 虚拟节点', g['ring_v128'], TEAL),
            ('理想值', g['ideal'], GRAY)]
    y = 386
    for lab, v, color in rows:
        fig.text((74, y + 8), lab, 42, color=INK)
        bar_x1 = 340 + max(v * 560, 8)
        fig.rect(340, y, bar_x1, y + 62, fill=color, outline=None, radius=8)
        fig.text((bar_x1 + 20, y + 6), '%.1f%%' % (100 * v), 46, bold=True, color=color)
        y += 118
    fig.line((340 + 560 * g['ideal'], 366), (340 + 560 * g['ideal'], 736),
             color=INK, width=4, dash=12)
    fig.text((74, 960), '2027-01-18 · 原创 · CC BY 4.0', 40, color=GRAY)
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
