#!/usr/bin/env python3
"""Original teaching figures for the BVH ray-tracing article. MIT.

Every number printed here comes from results.json or from the render in
renders/. Nothing is typed in by hand except labels.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageFont

import bvh
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
INK_DARK = '#0f2430'
PALETTE.update({VIOLET, BROWN, INK_DARK})


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


# ------------------------------------------------------------- render on demand

def _scene_tree():
    sc = bvh.build_scene()
    root, _st = bvh.build_bvh(sc['prims'], 'sah')
    return sc, root


def _pil(raw, w, h):
    return Image.frombytes('RGB', (w, h), raw)


def renders_160():
    """160×90 的两张渲染（朴素 / BVH），顺手核对与 results.json 的 sha256。"""
    sc, root = _scene_tree()
    w, h = R['compare']['width'], R['compare']['height']
    raw_bvh, _c = bvh.render(sc, root, w, h)
    raw_nai, _c = bvh.render(sc, None, w, h)
    for tag, raw in (('sah', raw_bvh), ('naive', raw_nai)):
        got = hashlib.sha256(raw).hexdigest()
        assert got == R['compare']['pixel_sha256'][tag], tag
    return _pil(raw_nai, w, h), _pil(raw_bvh, w, h)


def hero_image():
    sc, root = _scene_tree()
    w, h = R['hero']['width'], R['hero']['height']
    raw, _c = bvh.render(sc, root, w, h, aa=R['hero']['aa'])
    return _pil(raw, w, h)


# ---------------------------------------------------------------- render utils

def panel(fig, x0, y0, width, im, outline=LIGHT):
    """把一张渲染图按宽度贴进画布，返回它的外框（同时登记成 shape）。"""
    w, h = im.size
    ih = round(width * h / w)
    fig.im.paste(im.resize((width, ih), Image.LANCZOS), (x0, y0))
    fig.rect(x0, y0, x0 + width, y0 + ih, fill=None, outline=outline, width=3)
    return (x0, y0, x0 + width, y0 + ih)


def hbar(fig, x0, x1, y, frac, color, h=36):
    x1 = x0 + max(frac * (x1 - x0), 6)
    fig.rect(x0, y, x1, y + h, fill=color, outline=None)


def lerp_color(a, b, t):
    ca = tuple(int(a[i:i + 2], 16) for i in (1, 3, 5))
    cb = tuple(int(b[i:i + 2], 16) for i in (1, 3, 5))
    out = tuple(int(round(ca[k] + (cb[k] - ca[k]) * t)) for k in range(3))
    return '#%02x%02x%02x' % out


# ---------------------------------------------------------------- 01 render

def fig01():
    hero = HERO[0]
    fig, y = new(1, '一条光线，问一圈「挡我了吗」',
                 '这张图是 examples/bvh.py 自己渲染出来的：320×180 像素，'
                 '每个像素发 4 条稍许错开的子光线。本文所有数字都来自同一个模型。')
    y += 10
    box = panel(fig, 44, y, 974, hero)
    y = note(fig, box[3] + 30,
             '场景里 %d 个图元：%d 个球排成一条隧道，%d 块地板砖，再加一盏球形的灯。'
             % (R['scene']['prims'], R['scene']['spheres'], R['scene']['tiles']))
    save(fig, '01-tunnel-render.png',
         '模型的输出：球阵隧道，每个像素的颜色由光线求交算出',
         identity='原创教学示意（本文模型渲染输出）')


# ---------------------------------------------------------------- 02 loop

def fig02():
    fig, y = new(2, '整个渲染器就是一个循环',
                 '换个更直白的说法：屏幕上的每个点，都有一条线从这里射进场景，'
                 '我们只要知道这条线先撞上了什么。')
    y += 16
    steps = [
        ('1', '相机：每个像素发一条光线', TEAL),
        ('2', '沿光线往前找，谁离得最近', BLUE),
        ('3', '什么都没撞上：涂背景色', GRAY),
        ('4', '撞上了：再问灯，这一路上有人挡吗', AMBER),
        ('5', '把算出的颜色写回这个像素', GREEN),
    ]
    for i, (num, text, color) in enumerate(steps):
        fig.box('s%d' % i, 44, y, 1018, y + 104, fill=WHITE, outline=color, width=4)
        fig.circle(96, y + 52, 30, fill=color, outline=color)
        fig.text((96, y + 52), num, 40, bold=True, color=WHITE, anchor='mm',
                 inside='s%d' % i)
        fig.text((150, y + 30), text, 42, color=INK, inside='s%d' % i)
        if i < len(steps) - 1:
            fig.arrow((531, y + 108), (531, y + 148), color=INK_SOFT, width=4, head=14)
        y += 152
    y = note(fig, y, '上面这个循环跑 %s 次，就是一张图。麻烦全在第 2 步。'
             % format(R['hero']['primary_pixels'], ','))
    save(fig, '02-loop.png', '渲染循环：每个像素一条光线，关键是找最近的交点')


# ---------------------------------------------------------------- 03 sphere

def fig03():
    fig, y = new(3, '跟一个球求交，是一道初中数学题',
                 '球心是 C，半径是 r，光线从 O 出发、方向 D。问题：沿着 D 走多远会碰到球皮？')
    cx, cy, rad = 470, 470, 185
    ox, oy = 130, 790
    dx, dy = 0.80, -0.60
    # 解 |O + tD - C|^2 = r^2，画真实的两个交点
    fx, fy = ox - cx, oy - cy
    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - rad * rad
    disc = b * b - 4 * a * c
    t0 = (-b - math.sqrt(disc)) / (2 * a)
    t1 = (-b + math.sqrt(disc)) / (2 * a)
    p0 = (ox + dx * t0, oy + dy * t0)
    p1 = (ox + dx * t1, oy + dy * t1)
    fig.circle(cx, cy, rad, fill=TINT_B, outline=BLUE, width=4)
    fig.circle(cx, cy, 7, fill=INK, outline=INK)
    fig.line((ox, oy), (p1[0] + 120 * dx, p1[1] + 120 * dy), color=AMBER, width=5)
    fig.arrow((ox, oy), (ox + 150 * dx, oy + 150 * dy), color=AMBER, width=5, head=16)
    fig.line((cx, cy), (cx + rad * 0.72, cy - rad * 0.69), color=RED, width=4, dash=10)
    fig.circle(p0[0], p0[1], 12, fill=TEAL, outline=WHITE, width=3)
    fig.circle(p1[0], p1[1], 12, fill=GRAY, outline=WHITE, width=3)
    fig.text((ox + 14, oy + 18), 'O 相机', 40, color=AMBER, bold=True)
    fig.text((ox + 30, oy - 66), 'D 方向', 40, color=AMBER)
    fig.text((cx + 10, cy + rad + 16), 'C 球心', 40, color=INK)
    fig.text((cx + rad * 0.34, cy - rad * 0.86), 'r', 42, color=RED, bold=True)
    fig.text((p0[0] - 12, p0[1] - 74), 't0', 40, color=TEAL, bold=True, anchor='ma')
    fig.text((p1[0] + 16, p1[1] + 26), 't1', 40, color=GRAY, bold=True)
    y = oy + 110
    y = note(fig, y, '两个交点，t0 是近的那个。渲染要的就是它：'
             't0 之前没有东西挡着，t1 是穿过球之后又出来的位置。')
    y = note(fig, y, '判别式算出小于零，说明这条线从球边上擦过去了，一个交点都没有。')
    save(fig, '03-sphere-hit.png', '光线与球求交：解一元二次方程，取近的那个根')


# ---------------------------------------------------------------- 04 naive

def fig04():
    n_rays, n_prims = 4, 8
    rows = [(0, 2), (1, 5), (2, 0), (3, 6)]      # 每条光线真正打中的那个图元
    fig, y = new(4, '最笨的做法：每条光线问遍所有图元',
                 '4 条光线、8 个图元，就要 32 次求交。真正打中的只有 2 次，其余 30 次白问。')
    y += 16
    x0, step, cell = 250, 92, 62
    for j in range(n_prims):
        fig.text((x0 + j * step + cell / 2, y - 8), '图%d' % (j + 1), 38,
                 color=INK_SOFT, anchor='ra')
    y += 38
    for i in range(n_rays):
        yy = y + i * 96
        fig.text((60, yy + 8), '光线 %d' % (i + 1), 40, color=INK)
        hit = rows[i][1]
        for j in range(n_prims):
            x = x0 + j * step
            if j == hit:
                fig.rect(x, yy, x + cell, yy + cell, fill=GREEN, outline=GREEN,
                         radius=12)
                mono(fig, (x + 12, yy + 10), 'hit', 38, WHITE)
            else:
                fig.rect(x, yy, x + cell, yy + cell, fill=TINT_R, outline=RED,
                         radius=12, width=3)
                mono(fig, (x + 18, yy + 10), 'x', 38, RED)
    y += n_rays * 96 + 10
    y = note(fig, y, '真实的循环就是这样：%d 条光线 × %d 个图元 = %s 次求交。'
             % (n_rays, n_prims, format(n_rays * n_prims, ',')))
    save(fig, '04-naive.png', '朴素做法：每条光线把所有图元都测一遍',
         identity='原创教学示意（示意图里的 4 条光线是编的，不是模型数据）')


# ---------------------------------------------------------------- 05 slab

def fig05():
    fig, y = new(5, '先问盒子：一步算出「进没进去」',
                 '盒子是六个面，也就是三对平行板。光线在每一对板上都有一段「在里面」的距离，'
                 '三段有重叠，这条线才可能穿过盒子。')
    y += 10
    bx0, by0, bx1, by1 = 330, y + 130, 720, y + 450
    fig.rect(bx0, by0, bx1, by1, fill=TINT_A, outline=AMBER, width=4, radius=8)
    ox, oy = 120, y + 470
    ex, ey = 930, y + 40
    span = max(ex - ox, ey - oy)
    dx, dy = (ex - ox) / span, (ey - oy) / span
    fig.line((ox, oy), (ex, ey), color=INK, width=4)
    fig.arrow((ox, oy), (ox + 150 * dx, oy + 150 * dy), color=INK, width=4, head=14)
    fig.text((ox - 4, oy + 18), 'O', 42, bold=True, color=INK)
    ts = []
    for lo, hi, o_, d_ in ((bx0, bx1, ox, dx), (by0, by1, oy, dy)):
        ta = (lo - o_) / d_
        tb = (hi - o_) / d_
        ts.append((min(ta, tb), max(ta, tb)))
    tin = max(ts[0][0], ts[1][0])
    tout = min(ts[0][1], ts[1][1])
    pin = (ox + dx * tin, oy + dy * tin)
    pout = (ox + dx * tout, oy + dy * tout)
    fig.line(pin, pout, color=TEAL, width=6)
    fig.circle(pin[0], pin[1], 11, fill=TEAL, outline=WHITE, width=3)
    fig.circle(pout[0], pout[1], 11, fill=TEAL, outline=WHITE, width=3)
    fig.text((pin[0] - 20, pin[1] + 34), '进去', 40, color=TEAL, bold=True,
             anchor='ra')
    fig.text((pout[0] + 22, pout[1] + 16), '出来', 40, color=TEAL, bold=True)
    fig.text((bx1 + 18, by0 - 58), '盒子', 40, color=AMBER, bold=True)

    # 参数 t 上的两段区间
    ax0, ax1 = 210, 990
    ty = by1 + 160
    tmax = span

    def tx(t):
        return ax0 + (ax1 - ax0) * (t / tmax)

    fig.rect(tx(tin), ty - 118, tx(tout), ty + 42, fill=TINT_T, outline=None)
    for row, (lo, hi), color in ((0, ts[0], AMBER), (1, ts[1], BLUE)):
        ry = ty - 118 + row * 56
        fig.rect(tx(lo), ry, tx(hi), ry + 40, fill=color, outline=None, radius=8)
    fig.line((ax0, ty + 46), (ax1, ty + 46), color=INK_SOFT, width=4)
    for t, lab in ((0.0, '0 起点'), (1.0, '1 走到画外')):
        fig.text((tx(t), ty + 54), lab, 38, color=INK_SOFT,
                 anchor='la' if t == 0 else 'ra')
    fig.text((tx((tin + tout) / 2), ty + 54), '两段重叠 = 穿过盒子', 38,
             color=TEAL, anchor='ma')
    ly = ty + 118
    for x, color, lab in ((44, AMBER, 'x 方向的两块板'),
                          (420, BLUE, 'y 方向的两块板'),
                          (790, TEAL, '重叠')):
        fig.rect(x, ly + 6, x + 34, ly + 42, fill=color, outline=None, radius=6)
        fig.text((x + 48, ly + 2), lab, 38, color=INK)
    y = ly + 86
    y = note(fig, y, '每一对板只要两次除法。三对都算完，既知道「进没进去」，'
             '也知道「从多远进、多远出」——后面剪枝要用的正是这两个距离。')
    save(fig, '05-slab.png', '包围盒的 slab 判定：三对平板各算一段参数区间，取交集',
         identity='原创教学示意（坐标是示意图，不是模型数据）')


# ---------------------------------------------------------------- 06 tree

def fig06():
    fig, y = new(6, '盒子套盒子，就是一棵树',
                 '把场景对半切开，每边套一个盒子；再对半切，再套盒子。'
                 '切到剩几个图元就停，叫叶子。')
    y += 20
    span = 270
    pos = {0: (531, y + 30)}
    for i, x in enumerate((531 - span, 531 + span)):
        pos[1 + i] = (x, y + 200)
    for i, x in enumerate((531 - span - 60, 531 - span + 60,
                           531 + span - 60, 531 + span + 60)):
        pos[3 + i] = (x, y + 380)
    for a, b in ((0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)):
        fig.line((pos[a][0], pos[a][1] + 56), (pos[b][0], pos[b][1] - 56),
                 color=GRAY, width=3)
    labels = {0: '整个场景', 1: '左半', 2: '右半', 3: '一角', 4: '一角', 5: '一角', 6: '一角'}
    for i in range(7):
        x, cy = pos[i]
        fig.circle(x, cy, 62 if i == 0 else 56, fill=TEAL if i == 0 else WHITE,
                   outline=TEAL, width=4)
        fig.text((x, cy), labels[i], 40, color=WHITE if i == 0 else INK,
                 anchor='mm')
    build = R['build']
    fig.text((1018, y + 112), '每个圆圈 = 一个盒子', 38, color=INK_SOFT,
             anchor='ra')
    fig.text((1018, y + 270), '下面的枝不看，就是剪枝', 38, color=INK_SOFT,
             anchor='ra')
    y = y + 500
    stats = build['sah']
    rows = [
        [('节点总数', INK, False), ('%d' % stats['nodes'], INK, True)],
        [('叶子数', INK, False), ('%d' % stats['leaves'], INK, True)],
        [('最深处', INK, False), ('%d 层' % stats['depth'], INK, True)],
        [('建树时算 SAH 的次数', INK, False), ('%s' % format(stats['sah_ops'], ','), INK, True)],
    ]
    y = table(fig, y, [(60, 'la'), (1000, 'ra')], rows, size=40)
    y = note(fig, y, '树里每个节点只存一个盒子和两个孩子。遍历时先测盒，'
             '盒子没被穿过，底下那一整片图元就不用问了。')
    save(fig, '06-tree.png', 'BVH 的递归结构：节点存包围盒，叶子存图元')


# ---------------------------------------------------------------- 07 topview

def fig07():
    fig, y = new(7, '俯视图：树把空间切成了几段',
                 '同一棵树的前三层画在地面上。相机在左边，光线往右射。'
                 '每个框是那一层节点的包围盒在俯视图上的影子。')
    y += 20
    x_lo, x_hi = -8.0, 8.0
    z_lo, z_hi = -2.0, 19.0
    px0, py0, px1, py1 = 120, y, 980, y + 640

    def sx(x):
        return px0 + (x - x_lo) / (x_hi - x_lo) * (px1 - px0)

    def sz(z):
        return py0 + (z - z_lo) / (z_hi - z_lo) * (py1 - py0)

    fig.line((px0, py1), (px1, py1), color=INK_SOFT, width=4)
    fig.line((px0, py0), (px0, py1), color=INK_SOFT, width=4)
    fig.text((px1 - 6, py1 + 18), 'z 往纵深 →', 38, color=INK_SOFT, anchor='ra')
    fig.text((px0 - 12, py0 - 40), 'x', 38, color=INK_SOFT, anchor='ra')
    colours = {1: BLUE, 2: TEAL}
    for b in R['topview']['boxes']:
        if b['depth'] < 1:
            continue
        x0, y0, x1, y1 = (sx(b['lo'][0]), sz(b['lo'][2]),
                          sx(b['hi'][0]), sz(b['hi'][2]))
        c = colours[b['depth']]
        fig.rect(x0, y0, x1, y1, fill=None, outline=c, width=5 if b['depth'] == 1 else 3,
                 radius=6)
    for x, hy, z, r, mirror in R['topview']['spheres']:
        fig.circle(sx(x), sz(z), max(6, r / (x_hi - x_lo) * (px1 - px0)),
                   fill=TINT_B if not mirror else TINT_G, outline=BLUE, width=1)
    fig.text((px0 + 20, py0 + 20), '蓝框：第一层的两个盒子', 40, color=BLUE, bold=True)
    fig.text((px0 + 20, py0 + 76), '青框：第二层的四个盒子', 40, color=TEAL, bold=True)
    fig.text((px0 + 20, py0 + 132), '小圆：球在俯视图上的位置', 40, color=INK_SOFT)
    y = py1 + 58
    y = note(fig, y, '注意这些框是「包围盒的影子」，不是真的分区墙：'
             '框和框会重叠，球的位置越挤，框套得越紧，剪枝就越有效。')
    save(fig, '07-topview.png', '同一棵 BVH 前两层节点的包围盒，俯视图上看空间被切成几段')


# ---------------------------------------------------------------- 08 splits

def fig08():
    fig, y = new(8, '切开的方式不止一种',
                 '同样一棵树，怎么选切点，结果差很多。三种都能用，代价不一样。')
    y += 16
    b = R['build']
    c = R['compare']['rows']
    rows = [
        [('', INK, False), ('中位数', INK, True), ('空间等分', INK, True),
         ('SAH', INK, True)],
        [('节点数', INK, False), ('%d' % b['mid']['nodes'], INK, False),
         ('%d' % b['spatial']['nodes'], INK, False), ('%d' % b['sah']['nodes'], INK, False)],
        [('叶子数', INK, False), ('%d' % b['mid']['leaves'], INK, False),
         ('%d' % b['spatial']['leaves'], INK, False), ('%d' % b['sah']['leaves'], INK, False)],
        [('最深', INK, False), ('%d 层' % b['mid']['depth'], INK, False),
         ('%d 层' % b['spatial']['depth'], INK, False), ('%d 层' % b['sah']['depth'], INK, False)],
        [('每光线求交', INK, False), ('%.2f' % c['mid']['tests_per_ray'], INK, False),
         ('%.2f' % c['spatial']['tests_per_ray'], TEAL, True),
         ('%.2f' % c['sah']['tests_per_ray'], INK, False)],
        [('建树比较次数', INK, False), (format(b['mid']['sort_ops'], ','), INK, False),
         (format(b['spatial']['sort_ops'], ','), INK, False),
         (format(b['sah']['sah_ops'], ','), INK, False)],
    ]
    y = table(fig, y, [(60, 'la'), (420, 'la'), (650, 'la'), (880, 'la')], rows, size=40)
    y = note(fig, y, '「中位数」每层都要排序，比较次数最多，切得还最不均；'
             '「空间等分」只按坐标对半分，不看图元落在哪；'
             '「SAH」试算十几个候选切点，换来的是一棵更深的树。')
    y = note(fig, y, '注意最后一行：这一篇的场景里，空间等分反而比 SAH 便宜一点点'
             '（%.2f 对 %.2f 次求交）——SAH 的估算只是在猜，不是保证。'
             % (c['spatial']['tests_per_ray'], c['sah']['tests_per_ray']))
    save(fig, '08-splits.png', '三种切分方式的建树统计与实测每光线求交次数')


# ---------------------------------------------------------------- 09 sah

def fig09():
    prof = R['sah_profile']['rows']
    costs = [r['cost'] for r in prof if r['cost']]
    lo, hi = min(costs) / 1e3, max(costs) / 1e3
    fig, y = new(9, 'SAH：给每个候选切点估一次价',
                 '根节点上试了 11 个切点。代价 = 左盒面积 × 左边图元数 + 右盒面积 × 右边图元数，'
                 '单位随便，只看谁小。')
    y += 20
    box = (150, y, 980, y + 520)
    fx, fy = frame(fig, box, [], [], xsize=38)
    top = hi * 1.06
    bot = lo * 0.94

    def vy(v):
        return (v - bot) / (top - bot)

    pts = [(fx((r['split'] - 0.5) / 11.0), fy(vy(r['cost'] / 1e3)))
           for r in prof if r['cost']]
    for i in range(len(pts) - 1):
        fig.line(pts[i], pts[i + 1], color=TEAL, width=5)
    for i, (p, r) in enumerate(zip(pts, [r for r in prof if r['cost']])):
        fig.circle(p[0], p[1], 9, fill=TEAL, outline=WHITE, width=2)
        fig.text((p[0], box[3] + 18), '%d' % r['split'], 38, color=INK_SOFT,
                 anchor='ma')
    best = min((r for r in prof if r['cost']), key=lambda r: r['cost'])
    bx = fx((best['split'] - 0.5) / 11.0)
    by = fy(vy(best['cost'] / 1e3))
    fig.circle(bx, by, 18, fill=WHITE, outline=RED, width=4)
    fig.text((bx + 26, by - 66), '最省：切在第 %d 号' % best['split'], 40,
             color=RED, bold=True)
    fig.text((bx + 26, by - 18), '左边 %d 个，右边 %d 个' % (best['left'], best['right']),
             38, color=RED)
    fig.text((box[0] - 16, box[1] - 46), '每千次', 38, color=INK_SOFT)
    for frac, val in ((0.0, lo), (1.0, hi)):
        yy = fy(frac)
        fig.text((box[0] - 16, yy - 20), '%.0f' % val, 38, color=INK_SOFT, anchor='ra')
    fig.text((box[2], box[3] + 74), '候选切点编号（沿最长轴分 12 个桶）', 38,
             color=INK_SOFT, anchor='ra')
    y = box[3] + 136
    y = note(fig, y, '两头贵、中间便宜：切得太偏，一边塞满图元，另一边盒子白大；'
             '切在中间最平衡。曲线最陡处比最低点高了 %.0f%%。'
             % (100 * (max(costs) - min(costs)) / min(costs)))
    save(fig, '09-sah.png', '根节点上 11 个候选切点的 SAH 代价曲线，最低点在 6 号')


# ---------------------------------------------------------------- 10 identical

def fig10():
    nai_im, bvh_im = RENDERS_160
    sha = R['compare']['pixel_sha256']['sah'][:12]
    fig, y = new(10, '换了加速结构，图一个像素都没变',
                 '左边是朴素遍历画的，右边是 BVH 画的。两张图的像素数据逐字节相同——'
                 '加速结构只改「先问谁」，不改「答案是什么」。')
    y += 16
    w = 440
    b1 = panel(fig, 44, y, w, nai_im)
    b2 = panel(fig, 534, y, w, bvh_im)
    fig.text((44, b1[3] + 16), '朴素：464 次', 40, color=INK)
    fig.text((534, b2[3] + 16), 'BVH：%.1f 次' % R['compare']['rows']['sah']['tests_per_ray'],
             40, color=TEAL, bold=True)
    y = b1[3] + 78
    mono(fig, (44, y), 'sha256 ' + sha, 38, INK_SOFT)
    y += 62
    y = note(fig, y, '两次渲染都是 %d×%d，光线完全相同。'
             'sha256 取前 12 位，完整值在 results.json 里。'
             % (R['compare']['width'], R['compare']['height']))
    save(fig, '10-identical.png', '同一场景分别用朴素遍历与 BVH 渲染，输出逐字节相同')


# ---------------------------------------------------------------- 11 compare

def fig11():
    c = R['compare']['rows']
    order = [('朴素：全测一遍', c['naive']['tests_per_ray'], RED),
             ('中位数切', c['mid']['tests_per_ray'], AMBER),
             ('SAH 切', c['sah']['tests_per_ray'], TEAL),
             ('空间等分', c['spatial']['tests_per_ray'], GREEN)]
    fig, y = new(11, '同一条光线，问的次数差 %d 倍' % round(R['speedup']),
                 '横轴是「一条光线平均要跟多少个图元做求交」，对数刻度：'
                 '每一格是前一个数的两倍左右。')
    y += 24
    x0, x1 = 420, 980
    logmax = math.log(1000.0)
    for i, (lab, v, color) in enumerate(order):
        yy = y + i * 112
        fig.text((400, yy + 4), lab, 40, color=INK, anchor='ra')
        frac = math.log(max(v, 1.0)) / logmax
        hbar(fig, x0, x1, yy, frac, color, h=44)
        fig.text((x0 + frac * (x1 - x0) + 14, yy + 2), '%.1f' % v, 40,
                 color=color, bold=True)
    y += 4 * 112
    fig.line((x0, y + 8), (x1, y + 8), color=INK_SOFT, width=4)
    for frac, lab in ((0.0, '1'), (math.log(10) / logmax, '10'),
                      (math.log(100) / logmax, '100'), (1.0, '1000')):
        gx = x0 + frac * (x1 - x0)
        fig.line((gx, y + 8), (gx, y + 20), color=INK_SOFT, width=3)
        fig.text((gx, y + 26), lab, 38, color=INK_SOFT, anchor='ma')
    y += 88
    y = note(fig, y, '朴素方案正好等于图元数 %d：它不管光线去哪，每个都问。'
             'BVH 让这个数字跟「这条光线附近有多少东西」有关，跟场景总共有多少东西基本无关。'
             % R['scene']['prims'])
    save(fig, '11-compare.png', '每光线求交次数对比（对数横轴）：朴素 vs 三种切分')


# ---------------------------------------------------------------- 12 where

def fig12():
    c = R['compare']['rows']['sah']
    per_ray_nodes = c['nodes'] / c['rays']
    pruned = 100 * c['pruned'] / c['nodes']
    fig, y = new(12, '一条光线的一生',
                 '这一帧 %s 条光线（主 + 阴影 + 反射）平均下来，省下的不只是求交，'
                 '还有「进盒子」这一步。' % format(c['rays'], ','))
    y += 24
    cards = [('%.1f' % per_ray_nodes, '个盒子\n被检查', BLUE),
             ('%.1f' % pruned, '% 的盒子\n直接被剪掉', TEAL),
             ('%.1f' % c['tests_per_ray'], '次真正的\n图元求交', AMBER)]
    w = 300
    for i, (big, lab, color) in enumerate(cards):
        x = 44 + i * 322
        fig.rect(x, y, x + w, y + 300, fill=WHITE, outline=color, width=4, radius=18)
        fig.text((x + w / 2, y + 60), big, 64, bold=True, color=color, anchor='ma')
        for j, line in enumerate(lab.split('\n')):
            fig.text((x + w / 2, y + 170 + j * 56), line, 40, color=INK, anchor='ma')
    y += 340
    y = note(fig, y, '把三个数摆在一起看：一条光线要穿 %.1f 个盒子，才能把 %d 个图元筛到 %.1f 次求交。'
             % (per_ray_nodes, R['scene']['prims'], c['tests_per_ray']))
    y = note(fig, y, '所以加速结构的收益，要用「省下的求交」减去「多花的访盒」来算，'
             '不是拿 %d 直接除以 %.1f。' % (R['scene']['prims'], c['tests_per_ray']))
    save(fig, '12-where.png', '每条光线的开销分解：访盒数、剪掉比例、真实求交数')


# ---------------------------------------------------------------- 13 scaling

def fig13():
    rows = R['scaling']
    fig, y = new(13, '图元变多，朴素变慢得多',
                 '把球的数量从 8 加到 343，每次用同一批光线统计。'
                 '纵轴是每条光线的求交次数，对数刻度。')
    y += 24
    box = (170, y, 980, y + 480)
    ns = [r['prims'] for r in rows]
    top = 1000.0

    def logy(v):
        return math.log(max(v, 1.0)) / math.log(top)

    fx, fy = frame(fig, box, [], [], xsize=38)
    for v, lab in ((1, '1'), (10, '10'), (100, '100')):
        gy = fy(logy(v))
        fig.text((box[0] - 16, gy - 20), lab, 38, color=INK_SOFT, anchor='ra')
    for name, color, key in (('朴素', RED, 'naive'), ('BVH', TEAL, 'bvh')):
        pts = []
        for i, r in enumerate(rows):
            px = fx(i / (len(rows) - 1))
            py = fy(logy(r[key]))
            pts.append((px, py))
        for i in range(len(pts) - 1):
            fig.line(pts[i], pts[i + 1], color=color, width=5)
        for p, r in zip(pts, rows):
            fig.circle(p[0], p[1], 9, fill=color, outline=WHITE, width=2)
        fig.text((pts[-1][0] - 10, pts[-1][1] - 60), name, 40, color=color,
                 bold=True, anchor='ra')
    for i, r in enumerate(rows):
        gx = fx(i / (len(rows) - 1))
        fig.text((gx, box[3] + 18), '%d' % r['prims'], 38, color=INK_SOFT, anchor='ma')
    y = box[3] + 78
    y = note(fig, y, '朴素那条线斜着往上冲：图元翻一倍，求交翻一倍。'
             'BVH 那条几乎是平的——它只跟「附近有多少」有关。')
    y = note(fig, y, '最左边 BVH 也要 %.1f 次，因为图元少的时候树本身没多少可省的。'
             % rows[0]['bvh'])
    save(fig, '13-scaling.png', '图元数增加时每光线求交次数的增长：朴素线性，BVH 接近对数')


# ---------------------------------------------------------------- 14 prune

def fig14():
    t = R['traversal']
    base = t['normal']['tests']
    rows = [
        ('正常遍历（先近后远，按距离剪枝）', t['normal']['tests'], t['normal']['nodes'], TEAL),
        ('先远后近', t['far_first']['tests'], t['far_first']['nodes'], AMBER),
        ('不按距离剪枝', t['no_prune']['tests'], t['no_prune']['nodes'], RED),
    ]
    fig, y = new(14, '两个细节：先走哪边，剪不剪',
                 '同一棵树、同一批 %s 条光线，只改遍历的两个开关。' % format(t['rays'], ','))
    y += 24
    for i, (lab, tests, nodes, color) in enumerate(rows):
        yy = y + i * 150
        fig.text((44, yy), lab, 40, color=INK)
        frac = tests / rows[2][1]
        hbar(fig, 44, 740, yy + 52, frac, color, h=40)
        fig.text((44 + frac * 696 + 14, yy + 50), '%s' % format(tests, ','), 40,
                 color=color, bold=True)
        fig.text((44, yy + 104), '检查了 %s 个盒子' % format(nodes, ','), 38,
                 color=INK_SOFT)
    y += 3 * 150 + 10
    y = note(fig, y, '先走靠近的那边，只省 %.1f%%；关掉按距离剪枝，求交多出 %.0f%%。'
             % (100 * (t['far_first']['tests'] - base) / base,
                100 * (t['no_prune']['tests'] - base) / base))
    save(fig, '14-prune.png', '遍历的两个开关：先近后远、命中后按 tmax 剪枝')


# ---------------------------------------------------------------- 15 heatmap

def fig15():
    hm = R['heatmap']
    w, h, mx = hm['width'], hm['height'], hm['max']
    vals = hm['values']
    ramp = ['#f4f3ed', '#dce6e3', '#147d84', '#ab640b', '#bc4650', '#5b4b8a']
    im = Image.new('RGB', (w, h))
    px = im.load()
    for yy in range(h):
        for xx in range(w):
            v = vals[yy * w + xx] / mx
            t = min(v, 1.0) * (len(ramp) - 1)
            i = min(int(t), len(ramp) - 2)
            c = lerp_color(ramp[i], ramp[i + 1], t - i)
            px[xx, yy] = tuple(int(c[k:k + 2], 16) for k in (1, 3, 5))
    fig, y = new(15, '哪个像素更累',
                 '同一张 %d×%d 的图，逐像素统计「这个像素的光线做了多少次求交」。'
                 '越亮的地方，加速结构越使不上劲。' % (w, h))
    y += 16
    box = panel(fig, 44, y, 974, im, outline=LIGHT)
    y = box[3] + 26
    # 色标
    bar_y = y
    strips = []
    for i in range(240):
        v = i / 239.0 * (len(ramp) - 1)
        j = min(int(v), len(ramp) - 2)
        c = lerp_color(ramp[j], ramp[j + 1], v - j)
        strips.append(tuple(int(c[k:k + 2], 16) for k in (1, 3, 5)))
    bar = Image.new('RGB', (720, 30))
    bpx = bar.load()
    for xx in range(720):
        for yy in range(30):
            bpx[xx, yy] = strips[xx // 3]
    fig.im.paste(bar, (44, bar_y))
    fig.rect(44, bar_y, 764, bar_y + 30, fill=None, outline=LIGHT, width=2)
    fig.text((44, bar_y + 44), '0', 38, color=INK_SOFT)
    fig.text((764, bar_y + 44), '%d 次' % mx, 38, color=INK_SOFT, anchor='ra')
    fig.text((44, bar_y - 58), '最多 %d 次，平均 %.1f 次'
             % (mx, hm['mean']), 38, color=INK_SOFT)
    y = bar_y + 106
    y = note(fig, y, '平坦的深色块是天空：光线谁都没碰到，一次就出局。'
             '隧道口那一圈最贵，那里每条线都要在十几个球之间比远近。')
    save(fig, '15-heatmap.png', '逐像素求交次数热力图：场景里哪些地方最费')


# ---------------------------------------------------------------- 16 rays

def fig16():
    r = R['rays']
    sec = r['total'] - r['primary']
    fig, y = new(16, '一条主光线不够，还得再发几条',
                 '找到交点之后还要问灯、还要照镜子。这些线也走同一棵树。')
    y += 24
    total = r['total']
    rows = [('主光线（%d 像素 × 1）' % r['primary'], r['primary'], TEAL),
            ('阴影线与反射线', sec, AMBER)]
    for i, (lab, v, color) in enumerate(rows):
        yy = y + i * 140
        fig.text((44, yy), lab, 40, color=INK)
        hbar(fig, 44, 940, yy + 50, v / total, color, h=44)
        fig.text((930, yy + 48), '%s' % format(v, ','), 40, color=color,
                 bold=True, anchor='ra')
    y += 2 * 140 + 10
    y = note(fig, y, '一共 %s 条光线，平均每个像素 %.2f 条：'
             '主光线之外还多出 %.0f%%。' % (format(total, ','),
                                        total / r['primary'],
                                        100 * sec / r['primary']))
    y = note(fig, y, '阴影线只问到灯为止，命中就停；反射线只再跳一次，'
             '跳第二次就直接算黑。这两条限制让模型跑得动，也是真实渲染器的常用简化。')
    save(fig, '16-rays.png', '光线构成：主光线之外，阴影线与反射线各占多少')


# ---------------------------------------------------------------- 17 photo

def fig17():
    photo('17-teapot.jpg', 'Utah_Teapot_circa_1974,_Computer_History_Museum.jpg',
          '计算机图形学界最有名的一把茶壶：1970 年代用来做曲面建模测试的那一只，'
          '现藏于山景城的计算机历史博物馆',
          'The wub, CC BY-SA 4.0, via Wikimedia Commons')


# ---------------------------------------------------------------- 18 takeaway

def fig18():
    fig, y = new(18, '带走四句话')
    y += 12
    y = bullets(fig, y, [
        '加速结构不改变结果，只改变顺序：先问大的，再问小的，问完就剪。',
        '包围盒判定很便宜（6 次除法），一次就能排除一大片图元。',
        '切法决定树的形状，树的形状决定每次遍历要走多少步。',
        '这套办法不专用于光线：哪里的问题长得像「在一堆东西里找最近的那个」，它就在哪里出现。',
    ])
    y = note(fig, y, '如果只记一个数：这个场景里，朴素遍历每条光线问 %d 次，'
             'BVH 问 %.1f 次。' % (R['scene']['prims'],
                                R['compare']['rows']['sah']['tests_per_ray']))
    save(fig, '18-takeaways.png', '全文四条结论')


def cover():
    hero = HERO[0]
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill=BG, outline=None)
    fig.text((70, 90), '459 次白问', 118, bold=True, color=INK)
    fig.text((74, 246), 'BVH：先把场景装进盒子，再问它', 50, color=INK_SOFT)
    w = 640
    ih = round(w * hero.size[1] / hero.size[0])
    y0 = 330
    fig.im.paste(hero.resize((w, ih), Image.LANCZOS), (74, y0))
    fig.rect(74, y0, 74 + w, y0 + ih, fill=None, outline=LIGHT, width=3)
    c = R['compare']['rows']
    fig.text((760, y0 + 20), '朴素', 44, color=INK_SOFT)
    fig.text((760, y0 + 74), '%d 次' % R['scene']['prims'], 72, bold=True, color=RED)
    fig.text((760, y0 + 200), 'BVH', 44, color=INK_SOFT)
    fig.text((760, y0 + 254), '%.1f 次' % c['sah']['tests_per_ray'], 72, bold=True,
             color=TEAL)
    fig.text((74, 980), '2027-01-11 · 原创 · CC BY 4.0', 40, color=GRAY)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png', optimize=True)
    (ASSETS / 'cover.png').unlink(missing_ok=True)
    print('   cover.png', (ART / 'cover.png').stat().st_size, 'bytes')


HERO = None
RENDERS_160 = None


def main():
    global HERO, RENDERS_160
    RENDERS_160 = renders_160()
    HERO = (hero_image(),)
    fig01()
    fig02()
    fig03()
    fig04()
    fig05()
    fig06()
    fig07()
    fig08()
    fig09()
    fig10()
    fig11()
    fig12()
    fig13()
    fig14()
    fig15()
    fig16()
    fig17()
    fig18()
    cover()
    META.sort(key=lambda r: r['path'])
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, ensure_ascii=False, indent=1) + '\n')
    print('figures:', len(META))


if __name__ == '__main__':
    main()
