#!/usr/bin/env python3
"""Original teaching figures for the USB-C Power Delivery article. MIT.

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


def fmt_v(v):
    return ('%.3f V' % v) if v < 2.5 else ('%.1f V' % v)


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


# ---------------------------------------------------------------- 01 photo

def fig01():
    photo('01-plug.jpg', 'USB_Type-C_plug_20170626_crop.jpg',
          'USB-C 插头实物：一个扁平的椭圆口，正反都能插',
          'Santeri Viinamäki, CC BY-SA 4.0, via Wikimedia Commons')


# ---------------------------------------------------------------- 02 CC 电路

def fig02():
    fig, y = new(2, '一根 CC 线上只有两个电阻',
                 '供电端放一个恒流源，设备端放一个 5.1 kΩ 的电阻。'
                 '电压是这两个东西算出来的，没有芯片参与。')
    top = y + 20
    fig.box('dfp', 44, top, 300, top + 230, fill=TINT_B, outline=BLUE)
    fig.text((172, top + 24), '充电器（供电端）', 40, color=BLUE, anchor='ma')
    fig.text((172, top + 96), 'CC 脚上挂一个', 38, color=INK, anchor='ma')
    fig.text((172, top + 154), '80 - 330 µA 的', 38, color=INK, anchor='ma')
    fig.text((172, top + 204), '恒流源', 38, color=INK, anchor='ma')
    fig.box('ufp', 762, top, 1018, top + 230, fill=TINT_G, outline=GREEN)
    fig.text((890, top + 24), '设备（受电端）', 40, color=GREEN, anchor='ma')
    fig.text((890, top + 96), 'CC 脚上挂一个', 38, color=INK, anchor='ma')
    fig.text((890, top + 154), '5.1 kΩ 电阻', 38, color=INK, anchor='ma')
    fig.text((890, top + 204), '到地', 38, color=INK, anchor='ma')

    yline = top + 300
    fig.line((172, top + 230), (172, yline), color=INK, width=5)
    fig.line((172, yline), (890, yline), color=INK, width=6)
    fig.line((890, yline), (890, top + 230), color=INK, width=5)
    fig.text((531, yline - 76), 'CC 线', 40, color=INK, anchor='ma')
    fig.rect(500, yline - 14, 562, yline + 14, fill=BG, outline=None)
    fig.text((531, yline - 34), 'I', 38, color=TEAL, anchor='ma')
    fig.arrow((600, yline), (664, yline), color=TEAL, head=14)
    fig.text((531, yline + 34), 'I × 5.1 kΩ = 0.41 / 0.92 / 1.68 V', 40,
             color=TEAL, anchor='ma')

    yy = yline + 120
    yy = bullets(fig, yy, [
        '电阻没有「档位」：同一个 5.1 kΩ，电压只由供电端那个电流决定。',
        '所以识别是模拟的、单向的、几毫秒就能完成的。',
        '真正的合同要等后面的数字报文，那是另一条路。',
    ])
    save(fig, '02-cc-circuit.png',
         'CC 引脚上的恒流源与下拉电阻，以及它产生的电压')


# ---------------------------------------------------------------- 03 阈值

def fig03():
    d = R['cc']
    fig, y = new(3, '电压落在哪个区间，就报几安',
                 '三个区间的边界由规范钉死；电阻 ±10% 的误差不会把任何一档算错。')
    x0, x1 = 96, 1006
    yb = y + 300
    lo, hi = 0.0, 2.6
    X = lambda v: x0 + (x1 - x0) * (v - lo) / (hi - lo)
    fig.line((x0, yb), (x1, yb), color=INK_SOFT, width=4)
    for k in range(0, 6):
        v = k * 0.5
        fig.line((X(v), yb), (X(v), yb + 10), color=INK_SOFT, width=3)
        fig.text((X(v), yb + 16), '%.1f' % v, 38, color=INK_SOFT, anchor='ma')
    fig.text((X(1.3), yb + 70), 'CC 上的电压 / V', 40, color=INK_SOFT, anchor='ma')

    amps = ['0.5 A', '1.5 A', '3 A']
    for i, b in enumerate(d['bands']):
        bx0, bx1 = X(b['lo']), X(b['hi'])
        fig.rect(bx0, yb - 96, bx1, yb - 12, fill=(TINT_T, TINT_B, TINT_A)[i],
                 outline=None)
        fig.text(((bx0 + bx1) / 2, yb - 84), amps[i], 40, color=INK, anchor='ma')

    for i, r in enumerate(d['rows']):
        cx = X(r['v_cc'])
        fig.rect(cx - 3, yb - 150, cx + 3, yb - 96, fill=(TEAL, BLUE, VIOLET)[i],
                 outline=None)
        fig.circle(cx, yb - 150, 14, fill=(TEAL, BLUE, VIOLET)[i],
                   outline=(TEAL, BLUE, VIOLET)[i])
        fig.text((cx, yb - 206), fmt_v(r['v_cc']), 40,
                 color=(TEAL, BLUE, VIOLET)[i], anchor='ma')
    y2 = yb + 120
    y2 = note(fig, y2, '点的高度只是让三档分开画；实测最窄的一侧余量是 '
              '%.3f V（默认档到上边界）。' % min(min(r['margin_lo'], r['margin_hi'])
                                            for r in d['rows']))
    y2 = bullets(fig, y2, [
        '同一档位在 ±10% 的电阻与 ±10% 的电流源下，算出的电压仍然落回同一条区间。',
        '边界之间留了这么宽的缝，就是为了让一个几分钱的电阻也能被可靠地认出来。',
    ])
    save(fig, '03-cc-levels.png',
         '三档 Rp 在 5.1 kΩ 上产生的 CC 电压，与三个合法区间')


# ---------------------------------------------------------------- 04 方向

def fig04():
    d = R['flip']
    fig, y = new(4, '插反了也没关系：看哪一脚被拉低',
                 '插头里只有一根 CC 线通到底，另一根变成给线缆供电的 VCONN。'
                 '所以两个方向都只剩一个下拉电阻。')
    for i, c in enumerate(d['cases']):
        top = y + 20 + i * 300
        fig.box('dfp%d' % i, 44, top, 300, top + 220, fill=TINT_B, outline=BLUE)
        fig.text((172, top + 22), '充电器', 40, color=BLUE, anchor='ma')
        fig.text((172, top + 88), '两脚都上拉', 38, color=INK, anchor='ma')
        fig.text((172, top + 140), '到 3.3 V', 38, color=INK, anchor='ma')
        fig.box('ufp%d' % i, 762, top, 1018, top + 220, fill=TINT_G, outline=GREEN)
        fig.text((890, top + 22), '设备', 40, color=GREEN, anchor='ma')
        fig.text((890, top + 88), '哪一脚有', 38, color=INK, anchor='ma')
        fig.text((890, top + 140), '5.1 kΩ', 38, color=INK, anchor='ma')
        fig.text((44, top - 44), c['label'], 40, bold=True, color=INK)
        for k, pin in enumerate(('CC1', 'CC2')):
            yy = top + 70 + k * 76
            rd = c['pins'][pin] == 'Rd'
            col = TEAL if rd else GRAY
            fig.line((300, yy), (762, yy), color=col,
                     width=6, dash=None if rd else 10)
            fig.text((330, yy - 52), pin + ('' if rd else ' 浮空'), 40, color=INK)
            v = c['v_cc1'] if pin == 'CC1' else c['v_cc2']
            fig.text((700, yy - 52), fmt_v(v), 40, color=col, anchor='ra')
        fig.text((700, top + 186), '低的那一脚 = %s' % c['low_pin'], 38,
                 color=TEAL, anchor='ra')
    y = y + 640
    y = note(fig, y, '方向是从「哪一脚低」推出来的，不是从数据里读出来的。'
             '数据线要等方向定了才知道怎么走。')
    save(fig, '04-flip.png',
         '正插与反插两种情形下，哪一脚被拉低以及供电端的读数')


# ---------------------------------------------------------------- 05 BMC

def fig05():
    b = R['bmc']
    fig, y = new(5, 'BMC：跳变本身就是时钟',
                 '接收端不需要单独的时钟线，跳变本身就是时钟。')
    x0, x1 = 96, 1006
    nbits = len(b['bits'])
    hi, lo_y = y + 100, y + 250
    step = (x1 - x0) / nbits
    wave = b['wave']
    per = b['ui_samples']
    pts = []
    for i, lvl in enumerate(wave):
        gx = x0 + (i + 0.5) * (x1 - x0) / len(wave)
        pts.append((gx, hi if lvl else lo_y))
    for a, c in zip(pts, pts[1:]):
        fig.line(a, c, color=TEAL, width=5)
    for i in range(nbits + 1):
        gx = x0 + i * step
        fig.line((gx, lo_y - 40), (gx, lo_y + 44), color=LIGHT, width=3)
    for i, bit in enumerate(b['bits']):
        cx = x0 + (i + 0.5) * step
        fig.text((cx, lo_y + 78), str(bit), 42, bold=True,
                 color=TEAL if bit else GRAY, anchor='ma')
        fig.text((cx, lo_y + 140), '%d' % b['edges_per_bit'][i], 38,
                 color=INK_SOFT, anchor='ma')
        # sample points at 1/4 and 3/4 of the cell, drawn at the level they read
        for frac in (0.25, 0.75):
            sx = x0 + (i + frac) * step
            idx = min(len(wave) - 1, int((i + frac) * per))
            sy = (hi if wave[idx] else lo_y) - 32
            fig.circle(sx, sy, 9, fill=AMBER, outline=AMBER)
    fig.text((x0, hi - 44), '每个格子的边界必有一次跳变', 40, color=INK)
    fig.text((x0 + 2 * step, hi - 100), '两点的值不同 → 这一位是 1', 40,
             color=AMBER)
    fig.text((84, lo_y + 78), '位', 38, color=INK_SOFT, anchor='ra')
    fig.text((84, lo_y + 140), '跳变', 38, color=INK_SOFT, anchor='ra')
    y2 = lo_y + 210
    y2 = note(fig, y2, '黄点是接收端在一个格子内采的两个样。'
              '0 的两点一样，1 的两点必须不同——判据只有这一句。')
    save(fig, '05-bmc.png',
         '比特 1 0 1 1 0 0 1 0 的 BMC 波形、跳变次数与两个采样点')


# ---------------------------------------------------------------- 06 窗口

def fig06():
    b = R['bmc']
    fig, y = new(6, '采样点偏多少就全错',
                 '上半：固定的采样相位；下半：接收端自己的时钟快了或慢了。'
                 '两条曲线的起点都由「半个格子」决定。')
    x0, x1 = 150, 1000
    yb = y + 210
    fig.text((44, y + 4), 'A  采样点偏了', 40, bold=True, color=BLUE)
    X = lambda p: x0 + (x1 - x0) * p / 0.6
    Y = lambda e: yb - 150 * (e / 176.0)
    fig.line((x0, yb), (x1, yb), color=INK_SOFT, width=4)
    fig.line((x0, yb), (x0, yb - 160), color=INK_SOFT, width=4)
    for k in range(7):
        p = k / 10.0
        fig.line((X(p), yb), (X(p), yb + 10), color=INK_SOFT, width=3)
        fig.text((X(p), yb + 16), '%.1f' % p, 38, color=INK_SOFT, anchor='ma')
    fig.text((X(0.3), yb + 70), '采样相位偏差 / 个比特', 40, color=INK_SOFT,
             anchor='ma')
    pts = [(X(s['offset_ui']), Y(s['errors'])) for s in b['sweep']]
    for a, c in zip(pts, pts[1:]):
        fig.line(a, c, color=BLUE, width=5)
    fig.line((X(0.25), yb - 160), (X(0.25), yb), color=RED, width=4, dash=10)
    fig.text((X(0.25) + 14, y + 66), '0.25 格：半格', 38, color=RED)
    fig.text((X(0.24) - 16, Y(95) - 56), '一帧错 %d 位'
             % b['first_bad']['errors'], 38, color=BLUE, anchor='ra')

    y2 = yb + 160
    fig.text((44, y2), 'B  时钟快了或慢了', 40, bold=True, color=VIOLET)
    yb2 = y2 + 250
    fig.line((x0, yb2), (x1, yb2), color=INK_SOFT, width=4)
    fig.line((x0, yb2), (x0, yb2 - 160), color=INK_SOFT, width=4)
    X2 = lambda p: x0 + (x1 - x0) * p / 5000.0
    maxerr = max(s['errors'] for s in b['fsweep'])
    Y2 = lambda e: yb2 - 150 * (e / max(maxerr, 1))
    for k in range(0, 6):
        p = k * 1000
        fig.line((X2(p), yb2), (X2(p), yb2 + 10), color=INK_SOFT, width=3)
        fig.text((X2(p), yb2 + 16), '%d' % p, 38, color=INK_SOFT, anchor='ma')
    fig.text((X2(2500), yb2 + 70), '两端时钟差 / ppm', 40, color=INK_SOFT,
             anchor='ma')
    pts = [(X2(s['ppm']), Y2(s['errors'])) for s in b['fsweep']]
    for a, c in zip(pts, pts[1:]):
        fig.line(a, c, color=VIOLET, width=5)
    fx = X2(b['first_freq']['ppm'])
    fig.line((fx, yb2 - 160), (fx, yb2), color=RED, width=4, dash=10)
    fig.text((fx + 16, y2 + 62), '%d ppm' % b['first_freq']['ppm'], 38, color=RED)
    y3 = yb2 + 150
    y3 = note(fig, y3, '半格是硬边界：相位差 0.24 格时一个比特都不错，'
              '0.25 格就有 %d 位读错。'
              % b['first_bad']['errors'])
    y3 = note(fig, y3, '时钟差也一样，只是要攒：%d 位攒到半格需要 %d ppm。'
              '实测第一个错出现在 %d ppm（错 %d 位）。'
              % (b['payload_bits'], b['limit_ppm'], b['first_freq']['ppm'],
                 b['first_freq']['errors']))
    y3 = note(fig, y3, '曲线到 %d 位就不再涨——漂移超过一格后，采样点滑进了'
              '下一个格子，错的位换了一批，总数落在同一水平。'
              % max(s['errors'] for s in b['fsweep']))
    save(fig, '06-window.png',
         '比特错误数随采样相位偏差、随时钟频率差的实测曲线')


# ---------------------------------------------------------------- 07 帧

def fig07():
    m = R['frame']
    m = m['message']
    fig, y = new(7, '一帧只有 22 个字节',
                 '4 档电压的 Source_Capabilities：2 字节头 + 16 字节内容 + 4 字节 CRC。')
    x0, x1 = 48, 1014
    total = m['bits']
    parts = [('头 %d 位' % (2 * 8), 16, TINT_B, BLUE),
             ('%d 个 PDO，每个 32 位' % m['ndo'], 128, TINT_T, TEAL),
             ('CRC %d 位' % 32, 32, TINT_A, AMBER)]
    gx = x0
    for label, bits, fill, line in parts:
        w = (x1 - x0) * bits / total
        fig.rect(int(gx), y + 40, int(gx + w), y + 200, fill=fill, outline=line,
                 width=3)
        fig.text((gx + w / 2, y + 96), label, 40, color=line, anchor='ma')
        fig.text((gx + w / 2, y + 156), '%d 位' % bits, 38, color=INK_SOFT,
                 anchor='ma')
        gx += w
    y2 = y + 250
    y2 = bullets(fig, y2, [
        '加上 CRC 一共 %d 字节，正好 %d 位。' % (m['frame_len'], total),
        '发之前每个 4 位换成 5 位：%d × 5/4 = %d 位。'
        % (total, R['frame']['fourb5b_bits']),
        '再用 BMC 调制，每位 64 个采样点：%d 个采样点。'
        % R['frame']['bmc_samples'],
        'CRC-32 在这条 %d 字节的帧上算出 0x%s；把 176 位里任意一位翻过来，'
        '%d 次全部被抓到。'
        % (m['frame_len'], m['crc_hex'], R['frame']['single_bit_caught']),
    ])
    save(fig, '07-frame.png',
         'Source_Capabilities 帧的字段长度，以及 4b5b、BMC 之后的位数')


# ---------------------------------------------------------------- 08 游程

def fig08():
    d = R['fourb5b']
    fig, y = new(8, '4b5b 把连零掐短了',
                 '同一批随机负载，编码前后最长的一段相同比特各有多长；'
                 '再拿最坏的全零负载对照。')
    rows = [('随机 6 字节，不编码', d['raw_mean'], d['raw_max'], GRAY),
            ('随机 6 字节，4b5b', d['c5_mean'], d['c5_max'], TEAL),
            ('全零 6 字节，不编码', 0, d['zero_raw'], RED),
            ('全零 6 字节，4b5b', 0, d['zero_c5'], BLUE)]
    x0 = 420
    scale = 470 / d['zero_raw']
    yy = y + 10
    for label, mean, mx, col in rows:
        fig.text((44, yy + 6), label, 40, color=INK)
        w = max(6, mx * scale)
        fig.rect(x0, yy, int(x0 + w), yy + 52, fill=col, outline=col)
        fig.text((x0 + w + 14, yy + 4), '%d 位' % mx, 40, color=col)
        yy += 92
    fig.rect(x0, y + 10, x0 + 2, yy - 20, fill=INK_SOFT, outline=None)
    y2 = yy + 40
    y2 = note(fig, y2, '横条长度就是最长的一段相同比特。全零负载在编码前是 48 位——'
              '线路会一直贴在同一个电平上。')
    y2 = bullets(fig, y2, [
        '编码后最坏情况是 %d 位，随机负载的平均最长段从 %.1f 位降到 %.1f 位。'
        % (d['c5_max'], d['raw_mean'], d['c5_mean']),
        '每个 5 位码里 1 的个数只在 %d 到 %d 之间，所以任何字节都不会变成'
        '全零或全一；全零负载编码后 1 的比例是 %.0f%%。'
        % (d['ones_per_symbol_min'], d['ones_per_symbol_max'],
           100 * d['ones_c5']),
    ])
    save(fig, '08-runlength.png',
         '编码前后最长相同比特段的实测对比，以及全零负载的对照')


# ---------------------------------------------------------------- 09 头

def fig09():
    f = R['frame']['message']['header_fields']
    fig, y = new(9, '16 个比特里塞了三件事',
                 '消息类型、带几个对象、这是第几次发——'
                 '剩下的位留给供电端/受电端角色和规范版本。')
    rows = [
        [('扩展标志', INK, False), ('15', INK_SOFT, False), ('%d' % f['ext'], INK, True)],
        [('对象个数', INK, False), ('14 - 12', INK_SOFT, False), ('%d' % f['ndo'], INK, True)],
        [('消息序号', INK, False), ('11 - 9', INK_SOFT, False), ('%d' % f['msg_id'], INK, True)],
        [('电源角色', INK, False), ('8', INK_SOFT, False), ('0 = 供电端', INK, True)],
        [('规范版本', INK, False), ('7 - 6', INK_SOFT, False), ('%d' % f['rev'], INK, True)],
        [('数据角色', INK, False), ('5', INK_SOFT, False), ('0 = 主机', INK, True)],
        [('消息类型', INK, False), ('4 - 0', INK_SOFT, False),
         ('%d（供电能力）' % f['type'], INK, True)],
    ]
    y = table(fig, y + 20, [(48, 'la'), (420, 'la'), (700, 'la')], rows)
    y = note(fig, y, '整条头是 0x%04X。接收端先读这 16 位，'
             '才知道后面的字节该按几个 32 位对象去切。'
             % R['frame']['message']['header'])
    save(fig, '09-header.png',
         '一条 Source_Capabilities 消息的 16 位头逐字段解码')


# ---------------------------------------------------------------- 10 PDO

def fig10():
    p = R['frame']['message']
    mv, ma = 20000, 3250
    fig, y = new(10, '一个 PDO 就是两个十位数',
                 '电压除以 50 mV，电流除以 10 mA，各自放进 10 位里。'
                 '剩下的 12 位是旗标。')
    x0, x1 = 48, 1014
    groups = [('12 位旗标', 12, TINT_A, AMBER),
              ('电压 10 位', 10, TINT_B, BLUE),
              ('电流 10 位', 10, TINT_T, TEAL)]
    gx = x0
    for label, bits, fill, line in groups:
        w = (x1 - x0) * bits / 32
        fig.rect(int(gx), y + 30, int(gx + w), y + 170, fill=fill, outline=line,
                 width=3)
        fig.text((gx + w / 2, y + 76), label, 40, color=line, anchor='ma')
        gx += w
    y2 = y + 230
    y2 = bullets(fig, y2, [
        '%d mV ÷ 50 mV = %d → 写成 10 位是 0x%03X。' % (mv, mv // 50, mv // 50),
        '%d mA ÷ 10 mA = %d → 0x%03X。' % (ma, ma // 10, ma // 10),
        '这一档电源是 %d V / %.2f A，也就是 %.1f W。'
        % (mv // 1000, ma / 1000, mv * ma / 1e6),
        '共用 32 位，所以一条消息里最多塞 7 档电压（头里那三位对象计数不够用 8）。',
    ])
    y2 = note(fig, y2, '分辨率是定死的：电压只能报 50 mV 的整数倍，'
              '电流只能报 10 mA 的整数倍。')
    save(fig, '10-pdo.png',
         '固定电压 PDO 的 32 位字段划分，以及 20 V / 3.25 A 的编码')


# ---------------------------------------------------------------- 11 时序

def fig11():
    t = R['trace']
    fig, y = new(11, '从插上到 20 V：先谈话，再升压',
                 '先等 %d ms 去抖，三条报文 %d ms 谈完，再用 %d ms 把电压爬上去。'
                 % (round(t['tcc_debounce'] * 1000),
                    round((t['events'][3]['t'] - t['events'][1]['t']) * 1000),
                    t['ramp_ms_5_to_20']))
    x0, x1 = 130, 1000
    yb = y + 330
    X = lambda ms: x0 + (x1 - x0) * ms / 400.0
    Y = lambda v: yb - (yb - (y + 60)) * v / 22.0
    fig.line((x0, yb), (x1, yb), color=INK_SOFT, width=4)
    fig.line((x0, yb), (x0, y + 60), color=INK_SOFT, width=4)
    for k in range(0, 5):
        ms = k * 100
        fig.line((X(ms), yb), (X(ms), yb + 10), color=INK_SOFT, width=3)
        fig.text((X(ms) if k else X(ms) + 24, yb + 16), '%d' % ms, 38,
                 color=INK_SOFT, anchor='ma')
    fig.text((X(200), yb + 70), '时间 / ms', 40, color=INK_SOFT, anchor='ma')
    for k, v in ((5.0, '5 V'), (20.0, '20 V')):
        fig.text((x0 - 16, Y(k) - 20), v, 38, color=INK_SOFT, anchor='ra')

    pts = [(X(v['t'] * 1000), Y(v['mv'] / 1000.0)) for v in t['vbus']]
    pts += [(X(320), Y(20)), (X(346), Y(9))]
    for a, c in zip(pts, pts[1:]):
        fig.line(a, c, color=TEAL, width=6)
    # annotations
    fig.line((X(150), Y(5)), (X(150), y + 40), color=BLUE, width=3, dash=8)
    fig.text((X(150) - 18, y + 6), '三条报文，%d ms'
             % round((t['events'][3]['t'] - t['events'][1]['t']) * 1000),
             38, color=BLUE, anchor='ra')
    fig.line((X(312), Y(20)), (X(312), y + 90), color=AMBER, width=3, dash=8)
    fig.text((X(312) - 18, y + 56), 'PS_RDY：%d ms' % round(t['attach_to_ready'] * 1000),
             38, color=AMBER, anchor='ra')
    fig.line((X(346), Y(9)), (X(346), y + 150), color=VIOLET, width=3, dash=8)
    fig.text((X(346) - 18, y + 116), '改约 PPS 9 V', 38, color=VIOLET, anchor='ra')
    y2 = yb + 110
    y2 = note(fig, y2, 'Accept 只是「我同意」，PS_RDY 才代表电压真的到了。'
              '这中间电源要按自己的速率把 5 V 抬到 20 V。')
    save(fig, '11-trace.png',
         '插上之后 0 - 350 ms 内 Vbus 的变化与三次握手的位置')


# ---------------------------------------------------------------- 12 规则表

def fig12():
    d = R['rules']
    fig, y = new(12, '功率不是想给多少就给多少',
                 '每一档功率都绑死一个电压和一个电流上限；超过 100 W 还要换线。')
    rows = [[('上限', INK_SOFT, False), ('电压', INK_SOFT, False),
             ('电流', INK_SOFT, False), ('线缆要求', INK_SOFT, False)]]
    for r in d['rules']:
        rows.append([('%d W' % r['max_w'], INK, True),
                     ('%d V' % r['v'], INK, False),
                     ('%.0f A' % r['a'], INK, False),
                     (r['cable'], INK_SOFT, False)])
    y = table(fig, y + 10, [(48, 'la'), (300, 'la'), (470, 'la'), (1010, 'ra')], rows)
    y = note(fig, y, '想让 100 W 从 5 V 出去，得 20 A——没有任何 USB-C 线缆允许。'
             '功率上去只能靠抬电压：20 V 时只要 5 A。')
    y = note(fig, y, '240 W 是 48 V × 5 A。直流 60 V 常被当作人体安全上限，'
             '48 V 离它只剩 12 V，所以 EPR 的插针、触点间隙和绝缘都重新做过。')
    save(fig, '12-rules.png',
         'USB PD 的功率档位、电压电流上限与对应的线缆要求')


# ---------------------------------------------------------------- 13 照片

def fig13():
    photo('13-cable.jpg', 'USB-C_cable_2017_A.jpg',
          '一根两端都是 USB-C 的线缆：两端插头一样，方向也一样',
          'Fructibus, CC0, via Wikimedia Commons')


# ---------------------------------------------------------------- 14 e-marker

def fig14():
    d = R['emarker']
    fig, y = new(14, '线缆自己会报身份',
                 '线里那枚 e-marker 芯片通过同一根 CC 线回答问题：'
                 '我能过几安、几伏、支不支持 EPR。')
    rows = [[('线缆', INK_SOFT, False), ('电流上限', INK_SOFT, False),
             ('电压上限', INK_SOFT, False), ('最高功率', INK_SOFT, False)]]
    for c in (d['cases'][0], d['cases'][2], d['cases'][5]):
        cap = c['max_a'] * c['max_v']
        rows.append([(c['cable'], INK, True),
                     ('%.0f A' % c['max_a'], INK, False),
                     ('%.0f V' % c['max_v'], INK, False),
                     ('%.0f W' % cap, INK, True)])
    y = table(fig, y + 10, [(48, 'la'), (520, 'la'), (700, 'la'), (1010, 'ra')], rows)
    y = note(fig, y, '同一个 100 W 的充电器，插到一根没有 e-marker 的线上，'
             '只能按 20 V × 3 A = %.0f W 走。' % d['lost_100w']['fallback_w'])
    y = bullets(fig, y, [
        '电流上限靠线芯粗细，也靠插头触点能扛多少热。',
        '电压上限靠绝缘和针距，所以 EPR 的 48 V 必须整根线重新认证。',
        '没有 e-marker 不等于坏线，只是上限回到 3 A / 20 V。',
    ])
    save(fig, '14-emarker.png',
         '三种线缆的身份、电流与电压上限，以及由此决定的最高功率')


# ---------------------------------------------------------------- 15 线损

def fig15():
    d = R['loss']
    rows = [r for r in d['rows'] if r['watts'] == 100]
    fig, y = new(15, '同样的 100 W，电压越高线越轻松',
                 '线阻按 %.2f Ω 计（来回两段）。电流降到四分之一，'
                 '损耗降到十六分之一。' % d['r_cable'])
    x0 = 430
    scale = 470 / 40.0
    yy = y + 10
    for r in rows:
        fig.text((44, yy + 6), '%d V  /  %.1f A' % (r['v'], r['a']), 40, color=INK)
        w = max(6, r['loss_w'] * scale)
        col = RED if r['loss_w'] > 5 else (AMBER if r['loss_w'] > 1 else TEAL)
        fig.rect(x0, yy, int(x0 + w), yy + 54, fill=col, outline=col)
        fig.text((x0 + w + 16, yy + 6), '%.1f W' % r['loss_w'], 40, color=col)
        yy += 100
    fig.rect(x0, y + 10, x0 + 2, yy - 26, fill=INK_SOFT, outline=None)
    y2 = yy + 40
    y2 = note(fig, y2, '横条长度就是线上烧掉的功率。5 V 送 100 W 要 20 A，'
              '光在线里就烧掉 40 W——而且这个电流没有任何 USB-C 线缆允许。')
    y2 = note(fig, y2, '20 V 时 5 A，损耗 2.5 W；48 V 时 2.1 A，损耗 0.4 W。'
              '240 W 在 48 V 下是 5 A，线损 2.5 W，占 1%。')
    save(fig, '15-loss.png',
         '同样 100 W 在 5 - 48 V 各档电压下的线缆损耗与电流')


# ---------------------------------------------------------------- 16 PPS

def fig16():
    d = R['pps']
    fig, y = new(16, 'PPS：把电压调成连续的',
                 '固定档位只有 5 / 9 / 15 / 20 V；PPS 允许 3.3 - 21 V 之间'
                 '以 20 mV 为步长要一个点。')
    rows = [[('目标电压', INK_SOFT, False), ('步数', INK_SOFT, False),
             ('实际设定', INK_SOFT, False), ('误差', INK_SOFT, False)]]
    for r in d['rows']:
        rows.append([('%.3f V' % r['target'], INK, False),
                     ('%d' % r['steps'], INK, False),
                     ('%.3f V' % r['set'], INK, True),
                     ('%.1f mV' % r['err_mv'], INK_SOFT, False)])
    y = table(fig, y + 10, [(48, 'la'), (420, 'la'), (660, 'la'), (1010, 'ra')], rows)
    y = note(fig, y, '总共 %.0f 个电压台阶（%.1f - %.1f V，每级 %.0f mV），'
             '电流每级 %.0f mA。半个台阶就是 %.0f mV 的极限误差。'
             % (d['v_steps'], d['v_lo'], d['v_hi'], d['step_mv'] * 1000,
                d['i_step_ma'], d['max_err_mv']))
    # cable drop compensation
    y += 10
    fig.text((44, y), '线阻还要吃掉一点电压', 42, bold=True, color=INK)
    y += 74
    x0 = 300
    for i, r in enumerate(d['drop']):
        yy = y + i * 96
        fig.text((44, yy + 6), '%.0f V / %.1f A' % (r['setpoint'], r['amps']), 40,
                 color=INK)
        fig.rect(x0, yy, x0 + 260, yy + 48, fill=TINT_G, outline=None)
        fig.text((x0 + 14, yy + 4), '设备端 %.2f V' % r['device_v'], 38,
                 color=GREEN)
        fig.rect(x0 + 280, yy, x0 + 280 + 260, yy + 48,
                 fill=TINT_T, outline=None)
        fig.text((x0 + 294, yy + 4), '设定 %.2f V' % r['comp_setpoint'], 38,
                 color=TEAL)
        fig.text((x0 + 560, yy + 4), '%d 步' % r['comp_steps'], 38,
                 color=INK_SOFT)
    y = y + 3 * 96 + 26
    y = note(fig, y, '充电器只能管自己端子上的电压。'
              'PPS 让它把设定点抬高一个「线阻 × 电流」，设备端正好拿到目标值。')
    save(fig, '16-pps.png',
         'PPS 的 20 mV 步长、量化误差，以及补偿线阻需要的步数')


# ---------------------------------------------------------------- 17 照片

def fig17():
    photo('17-port.jpg', 'USB-C_connector_on_a_laptop.jpg',
          '笔记本电脑侧面的 USB-C 母座：上下两排触点，正反都能对上',
          'Logant547, CC BY 4.0, via Wikimedia Commons')


# ---------------------------------------------------------------- 18 结论

def fig18():
    fig, y = new(18, '五句话', None)
    y = bullets(fig, y + 10, [
        'CC 上的模拟电压只回答「有没有设备、要几安」；'
        '真正的电压电流合同是数字报文谈出来的。',
        'BMC 把时钟藏进跳变里，4b5b 把连零掐短——'
        '两根线、22 字节，就能改一次电压。',
        '功率上限由「电压 × 电流」卡死，而电流受线缆和触点限制，'
        '所以每一次涨功率都是涨电压。',
        '线缆会自己报身份。没有 e-marker 就只给你 3 A / 20 V，'
        '这是协议层面的保护，不是厂商偷懒。',
        '48 V 离 60 V 的安全上限只剩 12 V。再往上不是做不到，'
        '是要换一套绝缘、触点和认证。',
    ], size=40)
    save(fig, '18-takeaways.png', '全文五个结论')


# ---------------------------------------------------------------- cover

def cover():
    fig = Fig(1080, bg=BG, width=1080)
    # a stylised connector silhouette
    fig.rect(80, 120, 1000, 300, fill=TINT_B, outline=BLUE, width=6, radius=90)
    fig.rect(150, 170, 930, 250, fill=WHITE, outline=LIGHT, width=4, radius=40)
    for i in range(12):
        fig.rect(200 + i * 60, 196, 220 + i * 60, 224, fill=INK_SOFT, outline=None)
    fig.text((80, 330), 'CC 两脚 + 电源四对', 40, color=INK_SOFT)

    steps = [(5, '5 V'), (9, '9 V'), (15, '15 V'), (20, '20 V')]
    bx = 80
    for i, (v, lab) in enumerate(steps):
        h = 40 + v * 6
        fig.rect(bx, 940 - h, bx + 96, 940, fill=(TINT_T, TINT_B, TINT_A, TINT_G)[i],
                 outline=None)
        fig.text((bx + 48, 940 - h - 52), lab, 38, color=INK, anchor='ma')
        bx += 112
    fig.text((560, 560), '3 A 上限', 40, color=RED)
    fig.text((560, 620), '线缆决定电流', 40, color=INK_SOFT)
    fig.text((560, 720), '电压决定功率', 40, color=TEAL)
    fig.text((560, 800), '48 V × 5 A = 240 W', 42, bold=True, color=INK)

    fig.text((80, 380), 'USB-C 供电', 116, bold=True, color=INK)
    fig.text((84, 520), '两根线怎么谈出 240 W', 48, color=INK_SOFT)
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
