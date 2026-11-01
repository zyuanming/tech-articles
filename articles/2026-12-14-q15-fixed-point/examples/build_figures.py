#!/usr/bin/env python3
"""Original teaching figures for the Q15 fixed-point article. MIT.

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


def pct(x, digits=1):
    return ('%.' + str(digits) + 'f%%') % (x * 100)


def lsb(x, digits=1):
    return ('%.' + str(digits) + 'f') % x


# ---------------------------------------------------------------- 01

def fig01():
    fig, y = new(1, '小数点焊死在符号位后面',
                 '最高位是符号位，权重 −1；往下十五位依次是 1/2、1/4……一直到 '
                 '1/32768。')
    cell, gap = 58, 2
    x0 = 50
    top = y + 56
    for i in range(16):
        idx = 15 - i
        x = x0 + i * (cell + gap)
        fill = TINT_R if idx == 15 else WHITE
        fig.rect(x, top, x + cell, top + 76, fill=fill, outline=GRAY)
        fig.text((x + cell / 2, top - 48), str(idx), 38, color=INK_SOFT, anchor='ma')

    raw = 22528
    bits = format(raw, '016b')
    top2 = top + 150
    fig.text((x0, top2 - 52), '例：0.6875 存成 %d' % raw, 40, color=INK)
    for i, ch in enumerate(bits):
        x = x0 + i * (cell + gap)
        on = ch == '1'
        fig.rect(x, top2, x + cell, top2 + 76,
                 fill=TINT_T if on else BG, outline=GRAY)
        fig.text((x + cell / 2, top2 + 18), ch, 40, bold=on,
                 color=TEAL if on else GRAY, anchor='ma')

    top3 = top2 + 130
    fig.text((x0, top3), '0.6875 = 1/2 + 1/8 + 1/16', 40, color=INK)
    fig.text((x0, top3 + 62), '22528  = 16384 + 4096 + 2048', 40, color=TEAL)
    y = note(fig, top3 + 140,
             '整张图里没有“小数点”这个东西：存下来的只有 22528 这个整数，'
             '解码的人自己知道它要除以 32768。这就是 Q15 的全部约定。')
    save(fig, '01-bits.png', 'Q15 的位权与一个具体数值的拆解')


# ---------------------------------------------------------------- 02

def fig02():
    fig, y = new(2, '两个相邻的数之间有多宽',
                 '把 0.3 附近的数轴放大：可表示的点只有那些，真值落在两点中间。')
    rows = {round(r['value'], 3): r for r in R['representation']['rows']}
    target = 0.3
    base = 9830
    pts = [(base - 1, (base - 1) / 32768), (base, base / 32768),
           (base + 1, (base + 1) / 32768), (base + 2, (base + 2) / 32768)]
    x0, x1 = 190, 1012
    y0, y1 = y + 60, y + 300
    fig.line((x0, y1), (x1, y1), color=INK, width=5)
    lo = pts[0][1] - 0.000005
    hi = pts[-1][1] + 0.000005

    def fx(v):
        return x0 + (x1 - x0) * (v - lo) / (hi - lo)

    for raw, v in pts:
        px = fx(v)
        fig.line((px, y1 - 16), (px, y1 + 16), color=TEAL, width=6)
        fig.text((px, y1 + 40), '%d' % raw, 38, color=TEAL, anchor='ma')
    tx = fx(target)
    fig.line((tx, y1 - 90), (tx, y1 - 20), color=RED, width=5, dash=10)
    fig.text((tx + 14, y1 - 140), '真值 0.3', 40, color=RED)
    fig.text((fx(pts[1][1]), y1 - 90), '存成 0.29998779', 38, color=INK_SOFT,
             anchor='ra')
    y = y1 + 130
    r = rows[0.3]
    y = note(fig, y, '一格的值是 1/32768 ≈ 0.0000305。0.3 落在 9830 和 9831 之间，'
                     '按四舍五入存成 9830，误差 %.2f 个格——比半格小。' % r['err_lsb'])
    y = note(fig, y, '误差是相对量：同一个 0.0000305，对 0.3 来说是十万分之三，'
                     '对 0.001 来说就是百分之三。定点数小信号吃亏，原因就在这里。')
    save(fig, '02-grid.png', 'Q15 的量化格与 0.3 的存储误差')


# ---------------------------------------------------------------- 03

def fig03():
    fig, y = new(3, '16 位定点与 4 位定点',
                 '上：Q15 量化后的正弦。下：同样一条正弦，只留 4 位。')
    st = R['staircase']
    n = st['n']
    xs = list(range(n))
    top_panel = y + 20
    panels = [(st['q15'], 'Q15', TEAL, 'Q15 的台阶在屏幕上根本看不见'),
              (st['q3'], 'Q3', AMBER, '4 位的台阶一眼就看得见')]
    for k, (vals, name, color, label) in enumerate(panels):
        base = top_panel + k * 300
        x0, x1 = 120, 1012
        y0, y1 = base + 40, base + 220
        fig.line((x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2), color=LIGHT, width=3)
        prev = None
        for i, v in enumerate(vals):
            px = x0 + (x1 - x0) * i / (n - 1)
            py = (y0 + y1) / 2 - (y1 - y0) / 2 * v
            if prev:
                fig.line(prev, (px, py), color=color, width=4)
            prev = (px, py)
        fig.text((x0, base + 4), label, 38, color=color)
    y = top_panel + 620
    y = note(fig, y, 'Q15 的格子是 1/32768，画在这块 220 像素高的图里，一个格子'
                     '不到百分之一像素，所以看起来是光滑的。Q3 的格子是 1/8，'
                     '一下就露出来了。')
    y = note(fig, y, '定点数不是“不精确”，它的误差有确定的上界：半个格。'
                     '真正难受的是这个上界不随数值大小变化。')
    save(fig, '03-staircase.png', 'Q15 与 4 位定点量化同一条正弦的对比')


# ---------------------------------------------------------------- 04

def fig04():
    fig, y = new(4, '一次乘法要还的债',
                 '两个 Q15 相乘，结果是 30 位小数；往回到 15 位时，多出来的位'
                 '怎么处理，有三种做法。')
    m = R['mul']
    a, b = m['a_raw'], m['b_raw']
    lines = [('存下来的两个操作数', '%d 和 %d' % (a, b), INK),
             ('相乘（整数）', '%d' % (a * b), TEAL),
             ('按 Q15 解释', '%.4f' % m['product_exact'], TEAL),
             ('这一步要还的债', '小数点后有 30 位，只留 15 位', AMBER)]
    for label, value, color in lines:
        fig.text((48, y + 8), label, 40, color=INK_SOFT)
        fig.text((430, y + 8), value, 40, bold=True, color=color)
        y += 66
    y += 12
    y = note(fig, y, '真值 0.0100002 落在 327 和 328 之间：327.72。三种舍入给出'
                     '三个不同的整数，误差分别是 −0.72、+0.28、+0.28 个格。')
    stats = m['stats']
    y = table(fig, y + 6,
              [(48, 'la'), (700, 'ra'), (1010, 'ra')],
              [[('做法', INK_SOFT, False), ('平均误差', INK_SOFT, False),
                ('单次最大误差', INK_SOFT, False)],
               [('截断：直接 >> 15', INK, True),
                ('%.4f 格' % stats['trunc']['mean_err_lsb'], AMBER, False),
                ('%.4f 格' % stats['trunc']['max_abs_err_lsb'], AMBER, False)],
               [('四舍五入：先加半个格', INK, True),
                ('+%.4f 格' % stats['round']['mean_err_lsb'], GREEN, False),
                ('%.1f 格' % stats['round']['max_abs_err_lsb'], GREEN, False)],
               [('五取偶：看余数再进位', INK, True),
                ('+%.5f 格' % stats['rne']['mean_err_lsb'], GREEN, False),
                ('%.1f 格' % stats['rne']['max_abs_err_lsb'], GREEN, False)]])
    y = note(fig, y, '截断永远朝下取整：正数变小、负数变更小，误差全落在'
                     ' −1 到 0 之间，平均值 −0.4966 格。另外两种把误差摊到'
                     ' ±0.5 格，平均值几乎为 0。')
    save(fig, '04-mul-modes.png', 'Q15 乘法的三种舍入做法与实测误差')


# ---------------------------------------------------------------- 05

def fig05():
    fig, y = new(5, '两万次乘法，误差落在哪里',
                 '横轴是误差（单位：格），纵轴是按比例缩放的次数。'
                 '三种做法各 20000 次。')
    st = R['mul']['stats']
    x0, x1 = 250, 1012
    bars = [('trunc', '截断', AMBER), ('round', '四舍五入', TEAL),
            ('rne', '五取偶', BLUE)]
    for k, (mode, name, color) in enumerate(bars):
        base = y + 30 + k * 260
        y0, y1 = base + 30, base + 190
        fig.line((x0, y1), (x1, y1), color=INK_SOFT, width=4)
        buckets = st[mode]['buckets']
        mx = max(buckets)
        bw = (x1 - x0) / 22
        for i, c in enumerate(buckets):
            if not c:
                continue
            h = (y1 - y0) * c / mx
            cx = x0 + i * bw
            fig.rect(cx + 1, y1 - h, cx + bw - 2, y1, fill=color, outline=None)
        fig.text((x0, base - 26), name, 40, bold=True, color=color)
        fig.text((x1, base - 26), '%s 格' % lsb(st[mode]['mean_err_lsb'], 3),
                 38, color=INK_SOFT, anchor='ra')
    bw = (x1 - x0) / 22
    axis = y + 30 + 3 * 260
    for v, lab in ((-1.0, '−1.0'), (-0.5, '−0.5'), (0.0, '0'), (0.5, '0.5')):
        gx = x0 + (v + 1.1) / 0.1 * bw
        fig.line((gx, axis - 12), (gx, axis - 34), color=INK_SOFT, width=3)
        fig.text((gx, axis + 4), lab, 38, color=INK_SOFT, anchor='ma')
    y = y + 30 + 3 * 260 + 60
    y = note(fig, y, '截断的分布整个偏在 0 左边，最远到 −1 格；另外两种被压在'
                     ' ±0.5 格里，形状也对称。')
    y = note(fig, y, '这条偏置不会自己消失。同一个乘法做四千次，误差就攒成'
                     ' 0.085 的绝对误差——下一张图。')
    save(fig, '05-mul-error.png', '三种舍入做法的误差分布')


# ---------------------------------------------------------------- 06

def fig06():
    fig, y = new(6, '偏置是怎么攒起来的',
                 '0.1 × 0.1 连做 4096 次，真值 40.96。三个数是同一次实验的结果。')
    drift = R['mul']['drift']
    x0, x1 = 250, 1012
    base = y + 300
    top = y + 60
    items = [('真值', drift['trunc']['true'], GRAY),
             ('截断', drift['trunc']['sum_q15'], AMBER),
             ('四舍五入', drift['round']['sum_q15'], TEAL),
             ('五取偶', drift['rne']['sum_q15'], BLUE)]
    for i, (name, v, color) in enumerate(items):
        cx = x0 + 60 + i * 190
        h = (base - top) * v / 42
        fig.rect(cx, base - h, cx + 130, base, fill=color, outline=None)
        fig.text((cx + 65, base - h - 44), lsb(v, 3), 38, color=color, anchor='ma')
        fig.text((cx + 65, base + 18), name, 38, color=INK, anchor='ma')
    fig.line((x0, base), (x1, base), color=INK, width=4)
    fig.line((x0, base - (base - top) * 40.96 / 42), (x1, base - (base - top) * 40.96 / 42),
             color=RED, width=4, dash=12)
    y = base + 90
    y = note(fig, y, '截断少了 %s（%.0f 个格），四舍五入多了 0.04（%.0f 个格）。'
             % (lsb(drift['trunc']['err'], 3), drift['trunc']['err'] * 32768,
                drift['round']['err'] * 32768))
    y = note(fig, y, '做一次乘法看不出差别。做四百万次，这 0.085 就是可以听见的'
                     '直流偏移。反过来，如果误差正负相消（输入是零均值的随机信号），'
                     '四舍五入的偏置几乎不累积——但截断的偏置仍在。')
    save(fig, '06-drift.png', '4096 次乘法后偏置的累积')


# ---------------------------------------------------------------- 07

def fig07():
    fig, y = new(7, '溢出之后，两个不同的世界',
                 'Q15 只放得下 [−1, 1)。加出界了，是截住，还是绕回去？')
    x0, x1 = 120, 1012
    yy = y + 150
    fig.line((x0, yy), (x1, yy), color=INK, width=5)
    for v, lab in ((-1.0, '−1'), (0.0, '0'), (1.0, '+1')):
        px = x0 + (x1 - x0) * (v + 1) / 2
        fig.line((px, yy - 14), (px, yy + 14), color=INK, width=4)
        fig.text((px, yy + 30), lab, 38, color=INK_SOFT, anchor='ma')
    px = x0 + (x1 - x0) * (0.9 + 1) / 2
    fig.circle(px, yy, 12, fill=TEAL, outline=TEAL)
    fig.text((px - 24, yy - 70), '0.9', 40, color=TEAL, anchor='ra')
    # 饱和
    fig.line((x1 - 34, yy - 120), (x1 - 34, yy - 30), color=GREEN, width=5)
    fig.text((x1 - 44, yy - 170), '截住：0.99997', 38, color=GREEN, anchor='ra')
    # 回绕
    fig.line((x1 - 4, yy - 120), (x0 + 4, yy + 120), color=AMBER, width=4, dash=14)
    fig.text((x0, yy + 150), '绕回去：−0.600', 38, color=AMBER)
    y = yy + 230
    rows = []
    for r in R['overflow']['rows']:
        rows.append([('%.2f + %.2f' % (r['a'], r['b']), INK, True),
                     ('%.4f' % r['sum_true'], INK, False),
                     ('%.4f' % r['sat'], GREEN, False),
                     ('%.4f' % r['wrap'], AMBER, False)])
    y = table(fig, y,
              [(48, 'la'), (420, 'la'), (700, 'la'), (1010, 'ra')],
              [[('算式', INK_SOFT, False), ('真值', INK_SOFT, False),
                ('饱和', INK_SOFT, False), ('回绕', INK_SOFT, False)]] + rows)
    y = note(fig, y, '回绕不只是“变小”：符号会翻。正的 1.9 变成负的 −0.11，'
                     '在音频里就是一声爆响，在控制回路里就是反向输出。'
                     '所以语音、音频、飞控的定点代码里，加法几乎都带饱和。')
    save(fig, '07-saturate.png', '定点加法溢出时饱和与回绕的两种结果')


# ---------------------------------------------------------------- 08

def fig08():
    fig, y = new(8, '乘加要用更宽的累加器',
                 '两个 16 位数相乘，结果要 31 位；把它们加 256 次，要 39 位。')
    acc = R['accumulator']
    x0 = 120
    unit = (1012 - x0) / 42
    bars = [('一个乘积', R['overflow']['product_bits'], BLUE, '16 位 × 16 位'),
            ('int32 的上限', 31, RED, '再高就装不下'),
            ('256 项之和', acc['need_bits'], AMBER, '最坏情况')]
    for k, (label, bits, color, note_) in enumerate(bars):
        top = y + 40 + k * 190
        fig.text((44, top - 34), '%s：%d 位' % (label, bits), 40, bold=True,
                 color=color)
        fig.rect(x0, top, x0 + unit * 42, top + 90, fill=PALE, outline=GRAY)
        w = unit * bits
        fig.rect(x0, top, x0 + w, top + 90, fill=color, outline=None)
        fig.text((x0, top + 104), note_, 38, color=INK_SOFT)
    y = y + 40 + 3 * 190 + 20
    y = note(fig, y, '最坏情况是 256 项全是 (−1) × (−1)：%d，恰好 %d 位。'
             % (acc['worst_sum'], acc['need_bits']))
    y = note(fig, y, '实测里 200 次随机乘加有 %d 次把 int32 撑爆——不是罕见情况。'
                     '所以 16 位输入的乘加器后面跟的一定是 32 位或 40 位累加器，'
                     '不是 16 位。' % acc['overflow32_runs'])
    save(fig, '08-acc-bits.png', '乘法的位数需求与 int32 溢出')


# ---------------------------------------------------------------- 09

def fig09():
    fig, y = new(9, '系数存不住，滤波器就没了',
                 '一阶低通 y += a(x − y)，a 由截止频率决定。a 被量化到 1/32768 '
                 '的格子上。')
    co = R['coef']
    rows = []
    for r in co['rows']:
        if r['a_raw'] == 0:
            rows.append([('%.1f Hz' % r['cutoff'], INK, True),
                         ('%d' % r['a_raw'], RED, True),
                         ('0', RED, True),
                         ('整条滤掉', RED, False)])
        else:
            rel = r['rel_err']
            rows.append([('%.1f Hz' % r['cutoff'], INK, True),
                         ('%d' % r['a_raw'], TEAL, False),
                         ('%.4f' % r['a_q15'], INK, False),
                         ('%+.2f%%' % (rel * 100) if rel is not None else '—',
                          GREEN if abs(rel) < 0.01 else AMBER, False)])
    y = table(fig, y + 6,
              [(48, 'la'), (300, 'la'), (520, 'la'), (1010, 'ra')],
              [[('想要', INK_SOFT, False), ('a 的整数', INK_SOFT, False),
                ('实际存的 a', INK_SOFT, False), ('实际截止', INK_SOFT, False)]] + rows)
    y = note(fig, y, '最小的正系数是 1/32768，对应截止 %.2f Hz。比它更低的'
                     '截止频率在 Q15 里根本没有系数可写：a 变成 0，滤波器'
                     '只剩一条 y 不动。' % co['f_floor'])
    y = note(fig, y, '采样率 %.0f Hz 下，20 Hz 以下就已经只剩一百来个可选的 a。'
                     '这不是精度不够，是可选的档位本来就那么几个。' % co['fs'])
    save(fig, '09-coef.png', '低通系数在 Q15 里的可表示值与截止频率偏移')


# ---------------------------------------------------------------- 10

def fig10():
    fig, y = new(10, '靠近单位圆，极点迈不动步',
                 '二阶谐振器的极点半径只由 b1 决定：r = √(−b1)。b1 一格一格地'
                 '变，r 不是。')
    rows = []
    vals = []
    for i in range(6):
        raw = -32763 - i
        r = math.sqrt(-raw / 32768)
        t60 = (6.907755278982137 / (-math.log(r) * 48000)) if r < 1 else float('inf')
        vals.append((raw, r, t60))
        rows.append([('%d' % raw, INK, True), ('%.7f' % r, TEAL, False),
                     (('%.2f 秒' % t60) if t60 != float('inf') else '无穷大',
                      RED if t60 == float('inf') else (AMBER if t60 > 3 else INK),
                      False)])
    y = table(fig, y + 10,
              [(48, 'la'), (400, 'la'), (1010, 'ra')],
              [[('b1 的整数', INK_SOFT, False), ('极点半径 r', INK_SOFT, False),
                ('衰减到 −60 dB 的时间', INK_SOFT, False)]] + rows)
    a, b = vals[2], vals[3]
    y = note(fig, y, '一格 b1 换来的是 T60 从 %.2f 秒跳到 %.2f 秒——在音频里'
                     '就是从“短促的敲击”跳到“拖得很长”。' % (a[2], b[2]))
    y = note(fig, y, '再往下一格就是 b1 = −32768，r 正好等于 1：极点站在单位圆上，'
                     'T60 变成无穷大。想要 20 秒的衰减，Q15 给不了，它只给 %.2f 秒'
                     '和无穷大两个选项。' % vals[4][2])
    save(fig, '10-pole.png', '极点半径在 Q15 系数下的离散取值')


# ---------------------------------------------------------------- 11

def fig11():
    fig, y = new(11, '衰减到最后，它不肯归零',
                 '输入一个脉冲后归零，看单极点低通的尾巴。纵轴是余量（格），'
                 '横轴是采样点。')
    lc = R['limit_cycle']
    x0, x1 = 200, 1012
    y0, y1 = y + 40, y + 340
    fig.line((x0, y1), (x1, y1), color=INK_SOFT, width=4)
    fig.line((x0, y1), (x0, y0), color=INK_SOFT, width=4)
    for frac, lab in ((0.0, '0'), (0.5, '200'), (1.0, '400')):
        gx = x0 + (x1 - x0) * frac
        fig.text((gx, y1 + 16), lab, 38, color=INK_SOFT, anchor='ma')
    nmax = 0.5
    for frac, lab in ((0.0, '0'), (0.5, '0.25'), (1.0, '0.5')):
        gy = y1 - (y1 - y0) * frac
        fig.text((x0 - 16, gy - 21), lab, 38, color=INK_SOFT, anchor='ra')
    for mode, name, color in (('trunc', '截断', AMBER), ('round', '四舍五入', TEAL)):
        curve = lc[mode]['curve']
        prev = None
        for i, v in enumerate(curve):
            px = x0 + (x1 - x0) * i / (len(curve) - 1)
            py = y1 - (y1 - y0) * max(0.0, v) / nmax
            if prev and (abs(v) > 0.0002 or abs(prev[1] - py) > 0.5):
                fig.line(prev, (px, py), color=color, width=4)
            prev = (px, py)
    fig.text((x0 + 40, y1 - 60), '四舍五入停在 10 格不动', 38, color=TEAL)
    fig.text((x0 + 40, y1 - 130), '截断继续掉到 0，但整体偏低', 38, color=AMBER)
    y = y1 + 80
    y = note(fig, y, 'a = %.2f 时，一格的修正量最多是 a × 1 = %.2f 格。当余量小于'
                     '这个数，舍入后就是 0：尾巴卡在 10 格，永远不动。' % (lc['a'],
                                                                     lc['a']))
    y = note(fig, y, '这个死区的宽度是 1/a ≈ %.0f 格。截断用“朝下取整”绕过了它，'
                     '代价是整条曲线多了一个负偏置。两个毛病，选一个。'
             % lc['deadband_lsb'])
    save(fig, '11-deadband.png', '定点单极点滤波器的死区与偏置')


# ---------------------------------------------------------------- 12

def fig12():
    fig, y = new(12, '误差曲线长什么样',
                 '500 Hz 采样的低通输出减去浮点参考，单位是格。'
                 '纵轴正负对称。')
    fl = R['filter']
    x0, x1 = 210, 1012
    y0, y1 = y + 50, y + 350
    mid = (y0 + y1) / 2
    span = 16.0
    fig.line((x0, y1), (x1, y1), color=INK_SOFT, width=4)
    for frac, lab in ((0.0, '0'), (0.5, '1 秒'), (1.0, '2 秒')):
        gx = x0 + (x1 - x0) * frac
        fig.text((gx, y1 + 16), lab, 38, color=INK_SOFT, anchor='ma')
    for v in (-15, 0, 15):
        gy = mid - (y1 - y0) / 2 * v / span
        fig.text((x0 - 16, gy - 21), str(v), 38, color=INK_SOFT, anchor='ra')
        fig.line((x0 - 8, gy), (x0, gy), color=INK_SOFT, width=3)
    for mode, name, color in (('trunc', '截断', AMBER), ('round', '四舍五入', TEAL)):
        wave = fl['q15_waves'][mode]
        fw = fl['float_wave']
        prof = [(wave[i] - fw[i]) * 32768 for i in range(len(fw))]
        prev = None
        for i, v in enumerate(prof):
            px = x0 + (x1 - x0) * i / (len(prof) - 1)
            py = mid - (y1 - y0) / 2 * max(-span, min(span, v)) / span
            if prev:
                fig.line(prev, (px, py), color=color, width=4)
            prev = (px, py)
    fig.text((x1, y0 - 10), '截断：平均 −%.1f 格' % abs(fl['runs']['trunc']['rms_err_lsb']),
             38, color=AMBER, anchor='ra')
    fig.text((x1, y0 + 46), '四舍五入：平均 ±%.1f 格' % fl['runs']['round']['rms_err_lsb'],
             38, color=TEAL, anchor='ra')
    y = y1 + 90
    y = note(fig, y, '截断的误差整条压在零线下面，因为它每次都在朝下取整；'
                     '四舍五入的在零线上下小幅摆动。')
    y = note(fig, y, '反馈把偏置放大了：单次乘法平均 −0.5 格，进了环路之后'
                     '输出误差的均方根到了 %.1f 格，信噪比从 %.1f dB 掉到 %.1f dB。'
             % (fl['runs']['trunc']['rms_err_lsb'], fl['runs']['round']['snr_db'],
                fl['runs']['trunc']['snr_db']))
    save(fig, '12-filter-err.png', '定点低通与浮点参考的误差曲线')


# ---------------------------------------------------------------- 13

def fig13():
    fig, y = new(13, '三种写法，三个信噪比',
                 '同样一条输入、同一个 a，只换乘法的舍入方式。'
                 '信噪比按误差功率相对浮点参考算。')
    runs = R['filter']['runs']
    x0, x1 = 260, 1012
    base = y + 500
    top = y + 60
    scale = 76.0
    bars = [('trunc', '截断', AMBER), ('round', '四舍五入', TEAL),
            ('rne', '五取偶', BLUE)]
    for i, (mode, name, color) in enumerate(bars):
        cx = x0 + 40 + i * 240
        v = runs[mode]['snr_db']
        h = (base - top) * v / scale
        fig.rect(cx, base - h, cx + 150, base, fill=color, outline=None)
        fig.text((cx + 75, base - h - 44), '%.1f dB' % v, 38, color=color,
                 anchor='ma')
        fig.text((cx + 75, base + 18), name, 38, color=INK, anchor='ma')
        fig.text((cx + 75, base + 62), '误差 %.1f 格' % runs[mode]['rms_err_lsb'],
                 38, color=INK_SOFT, anchor='ma')
    fig.line((x0, base), (x1, base), color=INK, width=4)
    y = base + 140
    y = note(fig, y, '同一个算法，只把 `>> 15` 换成 `(x + 16384) >> 15`，'
                     '信噪比多了 18 dB。这 18 dB 不是靠更宽的位数，'
                     '是靠把偏置消掉。')
    y = note(fig, y, '代价是每次乘法多一条加法。在老 DSP 上这条加法是要算成本的，'
                     '所以你会看到“精度不够就换 24 位芯片”和“加一条舍入指令”'
                     '两种流派。')
    save(fig, '13-filter-snr.png', '三种舍入方式下端到端信噪比')


# ---------------------------------------------------------------- 14

def fig14():
    fig, y = new(14, '正弦表：1024 个点够不够',
                 '查表法算 sin。上：直接取最近的一个表项。下：在两个表项之间'
                 '做线性插值。')
    st = R['sin_table']
    panels = (('最近点', st['curve_near'], AMBER, '最大 %.1f 格' % st['max_err_lsb']),
              ('线性插值', st['curve_lerp'], TEAL, '最大 %.1f 格' % st['max_err_lerp_lsb']))
    for k, (name, curve, color, label) in enumerate(panels):
        base = y + 20 + k * 300
        x0, x1 = 140, 1012
        y0, y1 = base + 50, base + 210
        mid = (y0 + y1) / 2
        fig.line((x0, mid), (x1, mid), color=INK_SOFT, width=3)
        prev = None
        rng = max(abs(v) for v in curve) or 1
        for i, v in enumerate(curve):
            px = x0 + (x1 - x0) * i / (len(curve) - 1)
            py = mid - (y1 - y0) / 2 * v / rng
            if prev:
                fig.line(prev, (px, py), color=color, width=4)
            prev = (px, py)
        fig.text((44, base + 20), name, 40, bold=True, color=color)
        fig.text((1012, base + 20), label, 38, color=color, anchor='ra')
    y = y + 20 + 2 * 300 + 40
    y = note(fig, y, '1024 项的表，相位一步是 2π/1024 ≈ 0.00614 弧度，'
                     '对应的正弦误差上界是 %.1f 格。插值之后误差降到一格——'
                     '也就是存储误差本身。' % st['max_err_lsb'])
    y = note(fig, y, '这张表占 %d 字节。用 %d 字节换掉一次泰勒展开或者一次'
                     '浮点乘加，这就是 90 年代合成器和示波器里的常规做法。'
             % (st['table_bytes'], st['table_bytes']))
    save(fig, '14-sin-lut.png', '正弦查表的误差：最近点与线性插值')


# ---------------------------------------------------------------- 15

def fig15():
    fig, y = new(15, '位数每加一，信噪比加约 6 dB',
                 '满幅正弦量化后的信噪比。斜线是 6.02N + 1.76 的理论值，'
                 '点是本文实测。')
    rows = R['sqnr']
    x0, x1 = 230, 1000
    y0, y1 = y + 60, y + 420
    lo, hi = 40.0, 155.0
    fx, fy = frame(fig, (x0, y0, x1, y1),
                   [(0.0, '8 位'), (0.5, '16 位'), (1.0, '24 位')],
                   [(0.0, '50'), (0.5, '100'), (1.0, '150')])

    def X(bits):
        return fx((bits - 8) / 16.0)

    def Y(db):
        return fy((db - lo) / (hi - lo))

    fig.line((X(8), Y(rows[0]['theory'])), (X(24), Y(rows[-1]['theory'])),
             color=GRAY, width=4, dash=12)
    prev = None
    for r in rows:
        px, py = X(r['bits']), Y(r['measured'])
        if prev:
            fig.line(prev, (px, py), color=TEAL, width=4)
        prev = (px, py)
        fig.circle(px, py, 11, fill=TEAL, outline=TEAL)
    for k, r in enumerate(rows[:1] + rows[3:4] + rows[-1:]):
        px = X(r['bits'])
        last = r is rows[-1]
        fig.text((px - 18 if last else px + 18, Y(r['measured']) - 46),
                 '%.1f' % r['measured'], 38, color=TEAL,
                 anchor='ra' if last else 'la')
    y = y1 + 90
    y = note(fig, y, '8 位 49.1 dB、16 位 98.1 dB、24 位 145.9 dB。'
                     '这条斜线是音频行业里“一位六个 dB”说法的来源。')
    y = note(fig, y, 'Q15 的 1 格相对于满幅是 %.1f dB，所以它的理想信噪比'
                     '就是 98 dB 左右——跟 CD 的 16 位是同一个数。' % R['representation']['lsb_db'])
    save(fig, '15-sqnr.png', '量化位数与实测信噪比')


# ---------------------------------------------------------------- 16

def fig16():
    fig, y = new(16, '同一个滤波器，换字长',
                 '一阶低通、同一系数，把整条数据通路换成不同位宽的定点，'
                 '跟浮点比信噪比。')
    rows = R['word_sweep']
    x0, x1 = 250, 1012
    base = y + 460
    top = y + 60
    scale = 180.0
    for i, r in enumerate(rows):
        cx = x0 + i * 150
        h = (base - top) * r['snr_db'] / scale
        color = TEAL if r['bits'] in (16, 24) else BLUE
        fig.rect(cx, base - h, cx + 110, base, fill=color, outline=None)
        fig.text((cx + 55, base - h - 44), '%.0f' % r['snr_db'], 38, color=color,
                 anchor='ma')
        fig.text((cx + 55, base + 18), '%d 位' % r['bits'], 38, color=INK,
                 anchor='ma')
    fig.line((x0, base), (x1, base), color=INK, width=4)
    y = base + 80
    y = note(fig, y, '16 位 66.9 dB，24 位 119.9 dB。差的 53 dB 差不多是'
                     '八位乘以每位的 6 dB——所以 24 位定点 DSP 不是“更贵一点”，'
                     '是多了整整 53 dB 的动态余量。')
    y = note(fig, y, '注意这里没有换成浮点。同一个算法、同一份代码结构，只是'
                     '把一个常量改成 2 的幂。这就是为什么 90 年代的音频 DSP 都'
                     '标着“24 位定点”。')
    save(fig, '16-word-sweep.png', '定点字长与端到端信噪比')


# ---------------------------------------------------------------- 17

def fig17():
    photo('17-dsp56000.jpg', 'KL_Motorola_DSP_XSP56001ZL.jpg',
          '摩托罗拉 DSP56001：24 位定点的音频/通信 DSP，1980 年代后期的典型产品',
          'Wikimedia Commons, Konstantin Lanzet, CC BY-SA 3.0')


# ---------------------------------------------------------------- 18

def fig18():
    fig, y = new(18, '把这一页压成五句话')
    y = bullets(fig, y + 10, [
        'Q15 是一个整数加一个约定：除以 32768。小数点不在内存里，在写代码的人脑子里。',
        '一格的误差在 0.3 上是十万分之三，在 0.001 上是百分之三——相对误差随信号变小而变坏。',
        '乘法有三种舍入：截断便宜但偏 −0.5 格，进了反馈环路就是 18 dB 信噪比。',
        '系数和状态共用这几个格子：截止 0.1 Hz 的系数直接归零，20 秒的衰减直接变无穷。',
        '所以定点设计的第一件事不是写代码，是算清楚动态范围、累加器宽度和舍入方式。',
    ])
    y = note(fig, y + 10, '这五条里，只有第一条是数学，其余四条都是工程选择。'
                          '定点数的麻烦从来不在“表示不了”，在“表示得了，但你得知道'
                          '它表示成了什么”。')
    save(fig, '18-takeaways.png', '全文结论')


# ---------------------------------------------------------------- cover

def cover():
    fig = Fig(1080, width=1080)
    fig.text((72, 96), '一个 16 位小数', 58, color=INK_SOFT)
    fig.text((72, 176), '能装下多少', 96, bold=True)
    fig.text((72, 292), '误差', 96, bold=True, color=TEAL)
    fig.text((72, 400), 'Q15 的表示、乘法、溢出与滤波器', 44, color=INK)
    # 阶梯正弦
    x0, x1 = 72, 1008
    mid = 720
    amp = 120
    n = 96
    prev = None
    for i in range(n):
        v = math.sin(2 * math.pi * 1.5 * i / n)
        px = x0 + (x1 - x0) * i / (n - 1)
        py = mid - amp * v
        if prev:
            fig.line((prev[0], prev[1]), (px, prev[1]), color=TEAL, width=5)
            fig.line((px, prev[1]), (px, py), color=TEAL, width=5)
        prev = (px, py)
    fig.line((x0, mid + amp + 40), (x1, mid + amp + 40), color=LIGHT, width=3)
    fig.text((x0, mid + amp + 60), '1 格 = 1/32768 = −90.3 dBFS', 40, color=INK_SOFT)
    fig.text((1008, mid - amp - 96), '格子在屏幕上看不见', 40, color=TEAL,
             anchor='ra')
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png', quality=92, optimize=True)
    p = ASSETS / 'cover.png'
    if p.exists():
        p.unlink()
    print('   cover.png', (ART / 'cover.png').stat().st_size, 'bytes')


# ---------------------------------------------------------------- main

def main():
    for fn in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
               fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18):
        print(fn.__name__)
        fn()
    META.sort(key=lambda r: r['path'])
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, indent=1, ensure_ascii=False) + '\n')
    cover()


if __name__ == '__main__':
    main()
