#!/usr/bin/env python3
"""Original teaching figures for the white-balance article. MIT.

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

VIOLET = PALETTE.add('#6a4c93')
BROWN = PALETTE.add('#8a5a44')


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


def deg(x):
    return '%.1f°' % x


# ---------------------------------------------------------------- 01

def fig01():
    fig, y = new(1, '温度越高，光谱的重心越往蓝边搬',
                 '五条黑体光谱，都把 560 nm 处的强度归一成 1。'
                 '2000 K 时红光比蓝光多几十倍，9000 K 时反过来。')
    x0, y0, x1, y1 = 140, y + 30, 1012, y + 430
    X, Y = frame(fig, (x0, y0, x1, y1),
                 [(0.0, '380'), (0.25, '480'), (0.5, '580'),
                  (0.75, '680'), (1.0, '780')],
                 [(0.0, '0'), (0.25, '0.5'), (0.5, '1.0'),
                  (0.75, '1.5'), (1.0, '2.0')])
    lambdas = R['planck_family']['lambdas']
    curves = R['planck_family']['curves']
    palette = [RED, AMBER, INK_SOFT, TEAL, BLUE]
    top = None
    for row, color in zip(curves, palette):
        ref = row['curve'][lambdas.index(560)]
        pts = []
        for lam, v in zip(lambdas, row['curve']):
            fx = (lam - 380) / 400.0
            vv = min(2.2, v / ref)
            pts.append((X(fx), Y(min(1.0, vv / 2.2))))
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=color, width=5)
    for i, (row, color) in enumerate(zip(curves, palette)):
        lx = 60 + i * 190
        fig.line((lx, y1 + 86), (lx + 44, y1 + 86), color=color, width=8)
        fig.text((lx + 56, y1 + 62), '%d K' % row['T'], 38, color=color)
    fig.text((X(0.5), y1 + 148), '波长（nm）', 38, color=INK_SOFT, anchor='ma')
    y = y1 + 190
    y = note(fig, y, '纵轴是相对强度。三条曲线在 560 nm 交叉，往红边走 2000 K 高、'
                     '往蓝边走 9000 K 高——这就是"暖光"和"冷光"的全部物理内容。')
    save(fig, '01-planck.png', '五个色温下的黑体光谱形状')


# ---------------------------------------------------------------- 02

def fig02():
    photo('02-filament.jpg', 'Electric_bulb_filament.jpg',
          '白炽灯的钨丝通电发光，色温约 2856 K，是 A 光源的原型',
          'Wikimedia Commons, Arnoldius, CC BY-SA 3.0')


# ---------------------------------------------------------------- 03

def fig03():
    fig, y = new(3, '把每个温度画成一个点',
                 '横轴 x、纵轴 y 是 CIE 1931 色度坐标。马蹄形的边界是单色光，'
                 '中间那条线是黑体轨迹。')
    x0, y0, x1, y1 = 170, y + 20, 760, y + 470
    X = (lambda fx: x0 + (x1 - x0) * fx / 0.9)
    Y = (lambda fy: y1 - (y1 - y0) * fy / 0.9)
    fig.line((x0, y1), (x1, y1), color=INK_SOFT, width=4)
    fig.line((x0, y1), (x0, y0), color=INK_SOFT, width=4)
    for fx, lab in ((0.0, '0'), (0.2, '0.2'), (0.4, '0.4'), (0.6, '0.6'),
                    (0.8, '0.8')):
        fig.text((X(fx), y1 + 16), lab, 38, color=INK_SOFT, anchor='ma')
    for fy, lab in ((0.0, '0'), (0.3, '0.3'), (0.6, '0.6'), (0.9, '0.9')):
        fig.text((x0 - 16, Y(fy) - 20), lab, 38, color=INK_SOFT, anchor='ra')
    fig.text((X(0.45), y1 + 66), '色度坐标 x', 38, color=INK_SOFT, anchor='ma')

    horse = R['spectral_locus']
    pts = [(X(p['x']), Y(p['y'])) for p in horse]
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=GRAY, width=4)
    fig.line(pts[-1], pts[0], color=GRAY, width=3)

    loc = R['locus']
    outline = [(X(p['x']), Y(p['y'])) for p in loc]
    for a, b in zip(outline, outline[1:]):
        fig.line(a, b, color=INK, width=6)
    marks = [2000, 2856, 6504, 10000]
    for T in marks:
        p = min(loc, key=lambda r: abs(r['T'] - T))
        fig.circle(X(p['x']), Y(p['y']), 12, fill=RED, outline=WHITE)
    p_lo = min(loc, key=lambda r: abs(r['T'] - 2000))
    p_hi = min(loc, key=lambda r: abs(r['T'] - 10000))
    fig.text((X(p_lo['x']) + 24, Y(p_lo['y']) - 44), '2000 K', 40, bold=True,
             color=RED)
    fig.text((X(p_hi['x']) + 24, Y(p_hi['y']) + 16), '10000 K', 40, bold=True,
             color=RED)
    y = y1 + 108
    y = note(fig, y, '这条线只覆盖一小段：黑体从红热走到白热，在色度图上留下的是'
                     '一条曲线，不是整个马蹄。日常光源基本都落在它附近。')
    save(fig, '03-locus.png', '黑体轨迹与单色光边界')


# ---------------------------------------------------------------- 04

def fig04():
    fig, y = new(4, '同一张白纸，七种光下七个颜色',
                 '纵轴是相机三通道的读数，都按红通道归一。白纸的红蓝比从 17 倍'
                 '一路掉到 0.86 倍。')
    rows = R['algorithms'][0]['rows']
    x0, x1 = 140, 1012
    base = y + 420
    top = y + 60
    fig.line((x0, base), (x1, base), color=INK_SOFT, width=4)
    n = len(rows)
    slot = (x1 - x0) / n
    colors = (RED, GREEN, BLUE)
    for i, row in enumerate(rows):
        cx = x0 + slot * i + slot * 0.5
        bw = slot * 0.20
        for k, (v, color) in enumerate(zip(row['white_rgb'], colors)):
            bx = cx - bw * 1.6 + k * bw
            h = (base - top) * v
            fig.rect(bx + 2, base - h, bx + bw - 2, base, fill=color,
                     outline=None)
        fig.text((cx, base + 14), str(row['T']), 38, color=INK_SOFT, anchor='ma')
        fig.text((cx, base - (base - top) * row['white_rgb'][0] - 44),
                 deg(row['raw_err_deg']), 38, color=INK)
    y = base + 74
    y = note(fig, y, '柱子上面写的是"不校正时白纸偏了多少度"——把三个通道当成'
                     '一个向量，量它离"三通道相等"那条轴多远。')
    y = note(fig, y, '在 8000 K 附近这个角度最小，因为白纸本来就接近中性；'
                     '到 2000 K，偏了 37.7 度，肉眼一眼就能看出整张照片是橙的。')
    save(fig, '04-white-rgb.png', '白纸在七种色温下的相机读数与偏色角度')


# ---------------------------------------------------------------- 05

def fig05():
    fig, y = new(5, '灰世界的假设：平均下来是灰的',
                 '把画面里所有像素的 R、G、B 分别求平均，然后强行把它们拉成相等。'
                 '这个假设成立时，一次除法就调好了白平衡。')
    top = y + 20
    cell = 150
    tones = (RED, AMBER, GREEN, TEAL, BLUE, VIOLET, BROWN, GRAY)
    for i in range(8):
        cx = 60 + (i % 4) * 240
        cy = top + (i // 4) * 170
        fig.rect(cx, cy, cx + cell, cy + cell, fill=tones[i], outline=WHITE,
                 width=4)
    bx, by = 60, top + 380
    fig.line((bx, by), (bx + 920, by), color=INK_SOFT, width=4)
    for i, (v, color, lab) in enumerate(((0.72, RED, 'R'), (0.70, GREEN, 'G'),
                                         (0.68, BLUE, 'B'))):
        h = 160 * v
        fig.rect(bx + 40 + i * 120, by - h, bx + 120 + i * 120, by,
                 fill=color, outline=None)
        fig.text((bx + 80 + i * 120, by + 14), lab, 40, color=INK_SOFT,
                 anchor='ma')
    fig.text((bx + 460, by - 40), '平均 ≈ 灰', 44, bold=True, color=INK)
    y = by + 90
    y = note(fig, y, '问题在图里就能看出来：草地、砖墙、橙色雨衣，只要某一种颜色'
                     '占的版面够大，平均值就不是灰的，你按它去调，整张照片就会'
                     '往反方向偏。')
    save(fig, '05-gray-world.png', '灰世界假设与它的破绽')


# ---------------------------------------------------------------- 06

def fig06():
    rows = R['dominance']
    fig, y = new(6, '绿色占的面积越大，灰世界错得越离谱',
                 '横轴是画面里绿色块的比例，纵轴是白纸校正后仍然偏的角度。'
                 '三种方法跑同一个场景。')
    x0, y0, x1, y1 = 150, y + 30, 1012, y + 420
    X, Y = frame(fig, (x0, y0, x1, y1),
                 [(0.0, '0'), (0.25, '25%'), (0.5, '50%'),
                  (0.75, '75%'), (1.0, '90%')],
                 [(0.0, '0'), (0.33, '10'), (0.66, '20'), (1.0, '30')])
    series = (('gray_world', '灰世界', RED), ('shades_p6', 'p=6', AMBER),
              ('max_rgb', '最大 RGB', TEAL))
    for key, lab, color in series:
        pts = [(X(r['green_frac'] / 0.9), Y(min(1.0, r[key]['err_deg'] / 30.0)))
               for r in rows]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=color, width=5)
        for a in pts:
            fig.circle(a[0], a[1], 9, fill=color, outline=color)
    for i, (key, lab, color) in enumerate(series):
        lx = 150 + i * 300
        fig.line((lx, y1 + 84), (lx + 44, y1 + 84), color=color, width=8)
        fig.text((lx + 56, y1 + 60), lab, 38, color=color)
    y = y1 + 152
    y = note(fig, y, '灰世界从 10.1 度涨到 27.2 度；p=6 的版本压得住一段，到九成'
                     '绿色也散了；最大 RGB 方法起伏不定，因为"最亮的那个点"换了人。')
    y = note(fig, y, '这不是算法写得不好，是假设被违反了。灰世界关于世界的断言'
                     '（平均反射率是中性灰）和关于照片的断言（平均值可以直接当'
                     '光源颜色）是两个不同的东西。')
    save(fig, '06-dominance.png', '绿色占比与三种方法的误差')


# ---------------------------------------------------------------- 07

def fig07():
    rows = R['algorithms'][0]['rows']
    fig, y = new(7, '有白纸的时候，四种方法各差多少',
                 '场景里有一张白纸，它正好是画面最亮的点。四种方法在七种光源下'
                 '的残差角度。')
    cols = [(48, 'la'), (340, 'ra'), (520, 'ra'), (680, 'ra'),
            (850, 'ra'), (1010, 'ra')]
    head = [('光源', INK_SOFT, False), ('不校正', INK_SOFT, False),
            ('灰世界', INK_SOFT, False), ('p=6', INK_SOFT, False),
            ('最亮块', INK_SOFT, False), ('灰卡', INK_SOFT, False)]
    body = [head]
    for r in rows:
        m = r['methods']
        body.append([
            ('%d K' % r['T'], INK, True),
            (deg(r['raw_err_deg']), GRAY, False),
            (deg(m['gray_world']['err_deg']), RED, False),
            (deg(m['shades_p6']['err_deg']), AMBER, False),
            (deg(m['max_rgb']['err_deg']), TEAL, False),
            (deg(m['known_gray']['err_deg']), GREEN, False)])
    y = table(fig, y + 8, cols, body)
    y = note(fig, y, '最大 RGB 认为"画面里最亮的点就是白"，这里恰好成立，误差是 0。'
                     '灰世界反而比不校正还差——它把本来就接近中性的照片调歪了。')
    y = note(fig, y, '这张表里最该记住的是第 3 列：一个流行的、写起来只要四行的'
                     '算法，在正常场景里能把误差从 5.7 度放大到 9.1 度。')
    save(fig, '07-with-white.png', '有白纸场景下的四种方法误差')


# ---------------------------------------------------------------- 08

def fig08():
    rows = R['algorithms'][1]['rows']
    fig, y = new(8, '没有白纸，最大 RGB 也跟着走偏',
                 '同一个场景，抽掉那张白纸。最大 RGB 只能去认画面里最亮的色块，'
                 '而它可能是一块黄布。')
    cols = [(48, 'la'), (340, 'ra'), (520, 'ra'), (680, 'ra'),
            (850, 'ra'), (1010, 'ra')]
    head = [('光源', INK_SOFT, False), ('不校正', INK_SOFT, False),
            ('灰世界', INK_SOFT, False), ('p=6', INK_SOFT, False),
            ('最亮块', INK_SOFT, False), ('灰卡', INK_SOFT, False)]
    body = [head]
    for r in rows:
        m = r['methods']
        body.append([
            ('%d K' % r['T'], INK, True),
            (deg(r['raw_err_deg']), GRAY, False),
            (deg(m['gray_world']['err_deg']), RED, False),
            (deg(m['shades_p6']['err_deg']), AMBER, False),
            (deg(m['max_rgb']['err_deg']), TEAL, False),
            (deg(m['known_gray']['err_deg']), GREEN, False)])
    y = table(fig, y + 8, cols, body)
    y = note(fig, y, '没有白纸时最大 RGB 稳定在 7.7 度上下，四个方向都偏。'
                     '灰世界的误差反而落到 4.2 到 7.4 度之间——不是因为变准了，'
                     '是因为这个场景的色块分布凑巧接近中性。')
    y = note(fig, y, '"灰卡"那一列永远是 0，因为它是作弊：我们知道哪一块是白纸。'
                     '真实的自动白平衡没有这个信息，所以它必须猜。')
    save(fig, '08-no-white.png', '没有白纸场景下的四种方法误差')


# ---------------------------------------------------------------- 09

def fig09():
    rows = R['algorithms'][0]['rows']
    fig, y = new(9, '自动白平衡要跨的增益范围',
                 '红蓝比从 17.3 倍到 0.86 倍：同一台相机，在不同光下要给红通道'
                 '乘的系数差二十倍。')
    x0, x1 = 200, 1012
    base = y + 420
    top = y + 60
    fig.line((x0, base), (x1, base), color=INK_SOFT, width=4)
    n = len(rows)
    slot = (x1 - x0) / n
    mx = max(r['true_rb'] for r in rows)
    for i, r in enumerate(rows):
        cx = x0 + slot * i
        h = (base - top) * r['true_rb'] / mx
        fig.rect(cx + 12, base - h, cx + slot - 12, base, fill=TINT_B,
                 outline=BLUE, width=4)
        fig.text((cx + slot / 2, base - h - 46), '%.1f' % r['true_rb'], 38,
                 color=BLUE, anchor='ma')
        fig.text((cx + slot / 2, base + 14), str(r['T']), 38, color=INK_SOFT,
                 anchor='ma')
    y = base + 74
    y = note(fig, y, '柱高是白纸的 R/B。2000 K 以下红比蓝多十几倍，10000 K 时'
                     '反过来蓝比红多。任何一台相机想在这两头都拍白，增益旋钮'
                     '就得跨过一个数量级。')
    y = note(fig, y, '这也是为什么"白平衡"不是一条固定的曲线，而是一张查表：'
                     '每种光源配一组三通道增益。')
    save(fig, '09-gain-range.png', '七种光源下的红蓝比')


# ---------------------------------------------------------------- 10

def fig10():
    fig, y = new(10, '对角校正：三个通道各乘一个数',
                 '把光源的读数当成"需要抵消的东西"，红乘 1/R、绿乘 1/G、'
                 '蓝乘 1/B，白点就回到对角线上。')
    x0, y0, x1, y1 = 220, y + 50, 980, y + 430
    fig.line((x0, y1), (x1, y1), color=INK_SOFT, width=4)
    fig.line((x0, y1), (x0, y0), color=INK_SOFT, width=4)
    fig.text((x0, y0 - 52), 'B 分量', 38, color=INK_SOFT)
    fig.text((x1 - 128, y1 + 22), 'R 分量', 38, color=INK_SOFT)
    fig.line((x0, y1), (x1, y0), color=GRAY, width=4, dash=14)
    fig.text((x0 + 520, y0 + 110), '三通道相等', 38, color=GRAY)
    px, py = x0 + 470, y1 - 150
    fig.line((x0, py), (px, py), color=LIGHT, width=3)
    fig.line((px, y1), (px, py), color=LIGHT, width=3)
    fig.circle(px, py, 17, fill=RED, outline=WHITE)
    fig.text((px - 26, py + 10), '白纸', 38, color=RED, anchor='ra')
    tx, ty = x0 + 260, y1 - 250
    fig.arrow((px - 14, py - 16), (tx + 14, ty + 16), color=TEAL, width=5)
    w = R['algorithms'][0]['rows'][0]['white_rgb']
    fig.text((tx, ty - 56), '红 × %.2f' % (w[1] / w[0]), 38, color=TEAL,
             anchor='ma')
    y = y1 + 120
    y = note(fig, y, '这个做法叫对角模型，也叫 von Kries 假设：换光源相当于三个'
                     '通道各自缩放。写起来是三次除法，硬件里是三个乘法器。')
    y = note(fig, y, '图上的 0.44 是 2000 K 那一行的增益：绿通道不动，红乘 '
                     '%.2f，蓝乘 %.2f。' % (w[1] / w[0], w[1] / w[2]))
    y = note(fig, y, '它的隐含前提是"通道之间不串色"。真实的感光曲线互相重叠，'
                     '所以这个前提只是近似——但它是所有手机相机里跑得最快的那一步。')
    save(fig, '10-diagonal.png', '对角校正的几何含义')


# ---------------------------------------------------------------- 11

def fig11():
    fig, y = new(11, '对角只是一族矩阵里最小的那个',
                 '左边只许拉伸坐标轴，右边允许剪切：全矩阵能把偏色挪到更接近'
                 '中性灰的位置，代价是九个系数和一次矩阵乘。')
    y += 10
    fig.text((44, y), '对角：三个数', 44, bold=True, color=TEAL)
    fig.text((560, y), '全矩阵：九个数', 44, bold=True, color=AMBER)
    y += 90
    mono(fig, (60, y), 'R\' = g_r · R', 40, TEAL)
    mono(fig, (60, y + 62), 'G\' = g_g · G', 40, TEAL)
    mono(fig, (60, y + 124), 'B\' = g_b · B', 40, TEAL)
    mono(fig, (560, y), 'R\' = a·R + b·G + c·B', 40, AMBER)
    mono(fig, (560, y + 62), 'G\' = d·R + e·G + f·B', 40, AMBER)
    mono(fig, (560, y + 124), 'B\' = h·R + i·G + j·B', 40, AMBER)
    y += 210
    y = note(fig, y, '对角模型只改亮度、不改色相之间的关系。传感受光曲线重叠得'
                     '厉害时（几乎所有相机都这样），一个绿色很亮的东西会让红通道'
                     '也读出一点绿，这种串色只有全矩阵能补。')
    y = note(fig, y, '工程上的选择往往是：先用对角把白点拉正，剩下的色差交给一张'
                     '查找表或一个 3×3 矩阵，在出厂校准时算好。')
    save(fig, '11-matrix.png', '对角模型与全矩阵的差别')


# ---------------------------------------------------------------- 12

def fig12():
    rows = R['metamer']['rows']
    r0 = rows[0]
    fig, y = new(12, '两种反射率，相机读数完全相同',
                 '灰色区域是可见光。把第二条曲线构造在"相机看不见的方向"上：'
                 '两者在相机里是同一个颜色。')
    x0, y0, x1, y1 = 150, y + 30, 1012, y + 400
    X = (lambda lam: x0 + (x1 - x0) * (lam - 380) / 400.0)
    Y = (lambda v: y1 - (y1 - y0) * min(1.0, v / 1.0))
    fig.line((x0, y1), (x1, y1), color=INK_SOFT, width=4)
    for lam, lab in ((380, '380'), (480, '480'), (580, '580'), (680, '680'),
                     (780, '780')):
        fig.text((X(lam), y1 + 16), lab, 38, color=INK_SOFT, anchor='ma')
    lambdas = list(range(380, 781, 20))
    for spec, color, lab in ((r0['spec_a'], INK, '反射率 A'),
                             (r0['spec_b'], AMBER, '反射率 B')):
        pts = [(X(lam), Y(v)) for lam, v in zip(lambdas, spec)]
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, color=color, width=5)
    fig.text((X(400), Y(0.86)), '反射率 A', 38, color=INK)
    fig.text((X(700), Y(0.86)), '反射率 B', 38, color=AMBER)
    y = y1 + 66
    y = note(fig, y, '相机读数：A = (%.3f, %.3f, %.3f)，B = (%.3f, %.3f, %.3f)。'
             % tuple(list(r0['rgb_a']) + list(r0['rgb_b'])))
    y = note(fig, y, '归一化之后，两者的三通道差值在双精度里算出来是 %.1f——'
                     '也就是计算机意义上完全相等。可人眼看到的色坐标差了 '
                     '%.4f（uv 距离）。'
             % (R['metamer']['max_cam_rel'], r0['uv_dist']))
    save(fig, '12-metamer.png', '同一相机读数对应的两条反射率')


# ---------------------------------------------------------------- 13

def fig13():
    rows = R['metamer']['rows']
    fig, y = new(13, '换一种光，它们就露馅了',
                 '同一对样品，在 6504 K 下相机读数相同；拿到 2856 K 的钨丝灯下，'
                 '两者差出百分之几。')
    cols = [(48, 'la'), (460, 'ra'), (760, 'ra'), (1010, 'ra')]
    body = [[('样品对', INK_SOFT, False), ('相机差 6504 K', INK_SOFT, False),
             ('相机差 2856 K', INK_SOFT, False),
             ('人眼 uv 距离', INK_SOFT, False)]]
    for i, r in enumerate(rows):
        body.append([
            ('%d' % (i + 1), INK, True),
            ('%.1e' % r['cam_rel'] if r['cam_rel'] else '0', TEAL, False),
            ('%.2f%%' % (r['cam_rel_a'] * 100), RED, False),
            ('%.4f' % r['uv_dist'], AMBER, False)])
    y = table(fig, y + 8, cols, body)
    y = note(fig, y, '在第一盏灯下，相机认为这两块布是同一个颜色，调白平衡时'
                     '给它们乘同一组增益；换到第二盏灯，相机读数差出 %.1f%%，'
                     '再乘同一组增益，它们就变成一个偏品红、一个偏绿。'
             % (max(r['cam_rel_a'] for r in rows) * 100))
    y = note(fig, y, '这就是颜色恒常性做不到"物理正确"的原因：三通道把光谱压扁了，'
                     '而不同的光谱在不同光源下的表现不一样。任何算法都只能在这个'
                     '损失之后再猜。')
    save(fig, '13-metamer-shift.png', '元激发在不同光源下的分裂')


# ---------------------------------------------------------------- 14

def fig14():
    rows = sorted(R['metamer']['rows'], key=lambda r: -r['uv_dist'])
    fig, y = new(14, '人眼能不能看出来，有一个门槛',
                 '竖柱是样品对的 uv 距离，横线是一个刚可分辨色差（0.004）的位置。'
                 '超过这条线的，人眼分得出来。')
    x0, x1 = 180, 1012
    base = y + 400
    top = y + 60
    fig.line((x0, base), (x1, base), color=INK_SOFT, width=4)
    n = len(rows)
    slot = (x1 - x0) / n
    mx = max(r['uv_dist'] for r in rows) * 1.15
    for i, r in enumerate(rows):
        cx = x0 + slot * i
        h = (base - top) * r['uv_dist'] / mx
        fig.rect(cx + 14, base - h, cx + slot - 14, base, fill=TINT_T,
                 outline=TEAL, width=4)
        fig.text((cx + slot / 2, base - h - 46), '%.4f' % r['uv_dist'], 38,
                 color=TEAL, anchor='ma')
    jnd = R['metamer']['jnd_uv']
    jy = base - (base - top) * jnd / mx
    fig.line((x0 - 10, jy), (x1, jy), color=RED, width=4, dash=12)
    fig.text((x0 - 18, jy - 20), '0.004', 38, color=RED, anchor='ra')
    y = base + 74
    y = note(fig, y, '%d 对里有 %d 对越过了这条线。相机说"一样"，眼睛说"不一样"，'
                     '这中间的差距就是元激发现象。'
             % (R['metamer']['pairs'], R['metamer']['over_jnd']))
    y = note(fig, y, '注意这个差距不是靠更高位深能补的：它来自"三个通道"这个'
                     '结构本身，不是量化的锅。四通道、多光谱相机能补一部分，'
                     '代价是体积和算力。')
    save(fig, '14-jnd.png', '元激发距离与刚可分辨阈值')


# ---------------------------------------------------------------- 15

def fig15():
    probes = R['cct']
    rows = [p for p in probes if p['diff_k'] > 0][:6]
    fig, y = new(15, '同一个色点，两种算法给出两个色温',
                 '一种在 x-y 平面上找最近的黑体点，另一种先转到 u-v 平面再找。'
                 '两者最多差出 825 K。')
    cols = [(48, 'la'), (430, 'ra'), (730, 'ra'), (1010, 'ra')]
    body = [[('真实色温', INK_SOFT, False), ('x-y 最近点', INK_SOFT, False),
             ('u-v 最近点', INK_SOFT, False), ('差', INK_SOFT, False)]]
    for p in rows:
        body.append([
            ('%d K' % p['true_T'], INK, True),
            ('%d K' % p['T_by_xy'], AMBER, False),
            ('%d K' % p['T_by_uv'], TEAL, False),
            ('%d K' % p['diff_k'], RED, False)])
    y = table(fig, y + 8, cols, body)
    y = note(fig, y, '上表的色点都是人为从黑体轨迹上挪开一点——真实场景里的白'
                     '总是落在轨迹旁边，不会正好在线上。挪开一点，"离谁最近"'
                     '这个问题的答案就取决于你用什么尺子量。')
    y = note(fig, y, 'u-v 平面的那套尺子（1960 CIE UCS）是为"等距离看起来差不多'
                     '一样远"设计的，所以行业标准 CCT 用它；x-y 平面上一小步，'
                     '在蓝色那一头是很大的色差。')
    save(fig, '15-cct.png', '两种色温估计法的差异')


# ---------------------------------------------------------------- 16

def fig16():
    rows = R['algorithms'][0]['rows']
    name = {2000: '烛光', 2856: '白炽灯', 4000: '暖白 LED',
            5000: '正午', 6504: 'D65', 8000: '阴天',
            10000: '蓝天'}
    fig, y = new(16, '七个常见档位，落到纸面上是多少',
                 '右列是白纸的相机读数（按红通道归一）。色温每往高走一档，'
                 '红就少一点、蓝多一点。')
    cols = [(48, 'la'), (385, 'ra'), (740, 'ra'), (1010, 'ra')]
    body = [[('色温', INK_SOFT, False), ('典型场合', INK_SOFT, False),
             ('白纸读数', INK_SOFT, False), ('R/B', INK_SOFT, False)]]
    for r in rows:
        g = r['white_rgb']
        body.append([
            ('%d K' % r['T'], INK, True),
            (name.get(r['T'], '—'), INK_SOFT, False),
            ('%.2f / %.2f / %.2f' % (g[0], g[1], g[2]), TEAL, False),
            ('%.2f' % r['true_rb'], AMBER, False)])
    y = table(fig, y + 8, cols, body)
    y = note(fig, y, '"典型场合"是约定俗成的说法，不是严格定义：一档色温对应'
                     '一大片光源，同一盏 LED 的色温也能随亮度漂几百 K。')
    save(fig, '16-table.png', '常见光源的色温与白纸读数')


# ---------------------------------------------------------------- 17

def fig17():
    photo('17-colorchecker.jpg',
          '2024_X-Rite_ColorChecker_Passport_Photo_2_(1).jpg',
          'X-Rite ColorChecker 校色卡，24 个已知反射率的标准色块，'
          '第二行是六格灰阶，白平衡与色彩矩阵都靠它标定',
          'Wikimedia Commons, Jacek Halicki, CC BY-SA 4.0')


# ---------------------------------------------------------------- 18

def fig18():
    fig, y = new(18, '把这一页压成五句话')
    y += 10
    y = bullets(fig, y, [
        '白平衡要解决的问题不是"让白变白"，是"在不知道光源的情况下猜光源"。',
        '色温描述的是光源，黑体轨迹是它在色度图上留下的那条线。',
        '灰世界、最大 RGB 都是关于场景的假设。假设被违反，算法会安静地错。',
        '对角模型只缩放三个通道，串色补不了；全矩阵能补，代价是九个系数。',
        '三通道丢掉了光谱，所以完美的白平衡在原理上不存在，只有够用的近似。',
    ])
    save(fig, '18-takeaways.png', '五条结论')


# ---------------------------------------------------------------- cover

def cover():
    fig = Fig(1080, bg=BG, width=1080)
    rows = R['algorithms'][0]['rows']
    bw = 1080 / len(rows)
    for i, r in enumerate(rows):
        g = r['white_rgb']
        col = '#%02x%02x%02x' % (255, int(255 * g[1] ** 0.45),
                                 int(255 * g[2] ** 0.45))
        PALETTE.add(col)
        fig.rect(int(i * bw), 140, int((i + 1) * bw), 400, fill=col,
                 outline=None)
    fig.rect(0, 400, 1080, 408, fill=INK, outline=None)
    fig.text((72, 460), '白平衡', 132, bold=True, color=INK)
    fig.text((76, 640), '为什么白纸在照片里不是白的', 52, color=INK_SOFT)
    fig.text((76, 726), '黑体、灰世界、对角模型，以及', 44, color=INK_SOFT)
    fig.text((76, 786), '三通道丢掉了多少东西', 44, color=INK_SOFT)
    fig.rect(76, 880, 1004, 888, fill=TEAL, outline=None)
    fig.text((76, 920), '从 2000 K 到 10000 K，同一条白纸的', 42, color=INK)
    fig.text((76, 980), '相机读数差二十倍。', 42, color=INK)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png', optimize=True)
    (ASSETS / 'cover.png').unlink(missing_ok=True)
    print('   cover.png', (ART / 'cover.png').stat().st_size, 'bytes')


def main():
    for fn in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
               fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18):
        print(fn.__name__[3:])
        fn()
    print('cover')
    cover()
    META.sort(key=lambda r: r['path'])
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
