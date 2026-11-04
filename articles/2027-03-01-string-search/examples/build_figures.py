#!/usr/bin/env python3
"""字符串搜索一文的原创教学插图。MIT。

所有带数字的图都读 results.json，画图时不另算一遍。
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import ImageFont

from figkit import (Fig, PALETTE, BG, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER,
                    RED, GRAY, LIGHT, PALE, GREEN, CREAM, TINT_T, TINT_B,
                    TINT_A, TINT_R, TINT_G)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []

MONO_PATH = '/System/Library/Fonts/Menlo.ttc'
_MONO = {}
VIOLET = '#5b4b8a'
PALETTE.add(VIOLET)

ALGO_COLOR = dict(naive=RED, kmp=TEAL, bmh=AMBER, bm=BLUE)
ALGO_NAME = dict(naive='朴素', kmp='KMP', bmh='BMH', bm='BM')


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


def mono_width(fig, s, size=38):
    if size not in _MONO:
        _MONO[size] = ImageFont.truetype(MONO_PATH, size, index=0)
    return fig.d.textlength(s, font=_MONO[size])


def new(n, title, sub=None):
    fig = Fig(900)
    fig.text((44, 26), title, 46, bold=True)
    fig.text((1018, 32), '图 %02d' % n, 40, color=GRAY, anchor='ra')
    y = 112
    if sub:
        y += int(fig.wrap((44, y), sub, 40, 974, color=INK_SOFT) * 40 * 1.35) + 20
    return fig, y


def note(fig, y, text, size=40, color=INK_SOFT):
    return y + int(fig.wrap((44, y), text, size, 974, color=color) * size * 1.35) + 16


def bullets(fig, y, items, accent=TEAL, size=40):
    for text in items:
        fig.circle(76, y + 20, 14, fill=accent, outline=accent)
        y += int(fig.wrap((114, y), text, size, 900, color=INK) * size * 1.35) + 24
    return y


def table(fig, y, cols, rows, size=38, row_h=70, zebra=True):
    for i, row in enumerate(rows):
        if zebra and i % 2 == 1:
            fig.rect(48, y - 14, 1014, y + row_h - 16, fill=PALE, outline=None)
        for (text, color, bold), (x, anchor) in zip(row, cols):
            if not text:
                continue
            w = fig.width_of(text, size, bold)
            span = (x, x + w) if anchor == 'la' else (x - w, x)
            assert span[0] >= 44 and span[1] <= 1020, 'cell out of band: %r' % (text,)
            fig.text((x, y + 2), text, size, bold=bold, color=color, anchor=anchor)
        y += row_h
    return y + 14


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def legend(fig, y, items, x0=52, step=250):
    x = x0
    for color, text in items:
        fig.rect(x, y + 4, x + 30, y + 34, fill=color, outline=None, radius=6)
        fig.text((x + 44, y - 2), text, 38, color=INK)
        x += step
    return y + 52


def axes(fig, x0, y0, x1, y1, xr, yr, xticks, yticks, xlabel, ylabel,
         xtick_labels=None, ytick_labels=None):
    def px(v):
        return x0 + (v - xr[0]) / (xr[1] - xr[0]) * (x1 - x0)

    def py(v):
        return y1 - (v - yr[0]) / (yr[1] - yr[0]) * (y1 - y0)

    for t in yticks:
        fig.line((x0, py(t)), (x1, py(t)), color=LIGHT, width=2)
    for t in xticks:
        fig.line((px(t), y0), (px(t), y1), color=LIGHT, width=2)
    fig.line((x0, y1), (x1, y1), color=INK, width=3)
    fig.line((x0, y0), (x0, y1), color=INK, width=3)
    labels = xtick_labels or [str(t) for t in xticks]
    for t, lab in zip(xticks, labels):
        fig.text((px(t), y1 + 14), lab, 38, color=INK_SOFT, anchor='ma')
    ylabs = ytick_labels or [str(t) for t in yticks]
    for t, lab in zip(yticks, ylabs):
        fig.text((x0 - 16, py(t) - 22), lab, 38, color=INK_SOFT, anchor='ra')
    fig.text((x1, y1 + 62), xlabel, 38, color=INK_SOFT, anchor='ra')
    fig.text((x0 - 16, y0 - 52), ylabel, 38, color=INK_SOFT, anchor='la')
    return px, py


def series(fig, pts, color, width=5, dash=None):
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=color, width=width, dash=dash)


def cn_num(v):
    if v >= 1e8:
        return '%.2f 亿' % (v / 1e8)
    if v >= 1e4:
        return '%.1f 万' % (v / 1e4)
    return '%d' % v


def cell(fig, x, y, w, h, ch, fill=WHITE, border=LIGHT, color=INK, size=40):
    fig.rect(x, y, x + w, y + h, fill=fill, outline=border, width=3, radius=4)
    mono(fig, (x + w / 2, y + h / 2 - size * 0.62), ch, size, color=color, anchor='ma')


def hbar(fig, x, y, vmax, value, color, wmax=520, h=26):
    w = max(4.0, wmax * value / vmax)
    fig.rect(x, y, x + w, y + h, fill=color, outline=None, radius=4)
    return x + w


# ---------------------------------------------------------------- 图 01

def fig01():
    d = R['demo']
    text, pat = d['text'], d['pattern']
    fig, y = new(1, '朴素匹配：失败一次，只往右挪一格',
                 'text = abcabcabd，pattern = abcabd。每个窗口都从模式最左边开始，'
                 '一个字符一个字符地比。')
    cw, ch = 60, 56
    x0 = 214
    for tr in d['naive']['trace']:
        start, matched, fail = tr['start'], tr['matched'], tr['fail']
        for i, c0 in enumerate(text):
            cell(fig, x0 + i * cw, y, cw, ch, c0, PALE, LIGHT, INK_SOFT)
        for j, c0 in enumerate(pat):
            if j < matched:
                fill, bd, col = TINT_T, TEAL, TEAL
            elif j == matched and fail:
                fill, bd, col = TINT_R, RED, RED
            else:
                fill, bd, col = WHITE, LIGHT, INK_SOFT
            cell(fig, x0 + (start + j) * cw, y + ch + 10, cw, ch, c0, fill, bd, col)
        cost = matched + (1 if fail else 0)
        fig.text((770, y + ch + 22), '比 %d 次' % cost, 40, color=INK)
        if fail:
            fig.text((770, y + ch + 70), '第 %d 个字符不同' % (matched + 1), 38,
                     color=RED)
        else:
            fig.text((770, y + ch + 70), '整段命中', 38, color=TEAL)
        y += 2 * ch + 10 + 78
    save(fig, '01-naive-align.png', '朴素匹配的四个窗口')


# ---------------------------------------------------------------- 图 02

def fig02():
    d = R['demo']
    pat, f = d['pattern'], d['prefix']
    fig, y = new(2, '前缀函数：模式记住对上的尾巴',
                 'pattern = abcabd。failure[i] 是 pattern[0..i] 的最长真前缀，'
                 '同时也是它的后缀的长度。')
    cw, ch = 84, 66
    x0 = 236
    fig.text((44, y + 22), '字符', 38, color=INK_SOFT)
    for i, c0 in enumerate(pat):
        cell(fig, x0 + i * cw, y, cw, ch, c0, WHITE, LIGHT, INK)
    y2 = y + ch + 10
    fig.text((44, y2 + 22), 'failure', 38, color=INK_SOFT)
    for i, v in enumerate(f):
        fill = TINT_A if v else PALE
        cell(fig, x0 + i * cw, y2, cw, ch, str(v), fill,
             AMBER if v else LIGHT, AMBER if v else INK_SOFT)
    y3 = y2 + ch + 30
    # 失配时跳到的位置：failure[4] = 2
    y3 += int(fig.wrap((44, y3),
                       '在最后一个 d 上失配时，已经匹配的 abcab 里，尾巴 ab 正好等于开头 ab，'
                       '这 2 个字符不用重比。', 40, 974, color=INK) * 40 * 1.35) + 20
    y4 = y3
    cw2, ch2 = 62, 54
    for i, c0 in enumerate('abcab'):
        fill = TINT_T if i >= 3 else PALE
        cell(fig, 210 + i * cw2, y4, cw2, ch2, c0, fill, TEAL if i >= 3 else LIGHT,
             TEAL if i >= 3 else INK_SOFT)
    fig.text((210 + 5 * cw2 + 16, y4 + 8), '已匹配 5 个', 38, color=INK_SOFT)
    fig.arrow((300, y4 + ch2 + 14), (300, y4 + ch2 + 84), TEAL, 5)
    fig.text((330, y4 + ch2 + 30), '把这两格对齐，下一轮从第 3 个字符继续', 38, color=TEAL)
    y5 = y4 + ch2 + 120
    for i, c0 in enumerate(pat):
        fill = TINT_T if i < 2 else WHITE
        cell(fig, 210 + i * cw2, y5, cw2, ch2, c0, fill, TEAL if i < 2 else LIGHT,
             TEAL if i < 2 else INK_SOFT)
    fig.text((210 + 6 * cw2 + 16, y5 + 8), '模式开头也是 ab', 38, color=INK_SOFT)
    save(fig, '02-prefix-table.png', '前缀函数表与跳转')


# ---------------------------------------------------------------- 图 03

def fig03():
    d = R['demo']
    fig, y = new(3, '同一个例子：4 个窗口 vs 2 个窗口',
                 '横轴是模式的起点。朴素把 0、1、2、3 全试了一遍；KMP 从 0 直接挪到 3；'
                 'BMH 也从 0 挪到 3。')
    xa, xb = 240, 900

    def px(s):
        return xa + s / 3.0 * (xb - xa)

    yh = y + 16
    fig.line((xa, yh), (xb, yh), color=INK, width=3)
    for s in range(4):
        fig.line((px(s), yh - 10), (px(s), yh + 10), color=INK, width=3)
        fig.text((px(s), yh + 16), str(s), 38, color=INK_SOFT, anchor='ma')
    fig.text((xb + 26, yh - 6), '起点', 38, color=INK_SOFT)
    lanes = [
        ('朴素', [t['start'] for t in d['naive']['trace']],
         ['6', '1', '1', '6'], RED, d['naive']['comparisons']),
        # KMP 第二段只比 4 次：abcab 尾巴 ab 已经对上，接着只比 c a b d
        ('KMP', [t['start'] for t in d['kmp']['trace']], ['6', '4'], TEAL,
         d['kmp']['comparisons']),
        ('BMH', [t['start'] for t in d['bmh']['trace']], ['1', '6'], AMBER,
         d['bmh']['comparisons']),
    ]
    ys = [yh + 150, yh + 330, yh + 510]
    for s in range(4):
        fig.line((px(s), yh + 40), (px(s), ys[-1]), color=LIGHT, width=2)
    for (name, starts, costs, color, total), ly in zip(lanes, ys):
        fig.text((44, ly - 22), name, 40, bold=True, color=color)
        fig.line((xa, ly), (xb, ly), color=INK_SOFT, width=3)
        for s, cost in zip(starts, costs):
            fig.circle(px(s), ly, 17, fill=color, outline=color)
            fig.text((px(s), ly + 30), cost, 38, color=color, anchor='ma')
        if len(starts) == 2:
            a, b = px(starts[0]), px(starts[1])
            top = ly - 84
            fig.line((a, ly - 24), (a, top), color=color, width=4)
            fig.line((a, top), (b, top), color=color, width=4)
            fig.arrow((b, top), (b, ly - 26), color, 5)
            fig.text(((a + b) / 2, top - 46), '挪 3 格', 38, color=color,
                     anchor='ma')
        fig.text((xb + 44, ly - 22), '%d 次' % total, 40, color=color)
    note(fig, ys[-1] + 74, '圆圈下面的数字是这个窗口比了几次。朴素第四个窗口就命中了，'
                           '但它必须先白试前三个。')
    save(fig, '03-tried-starts.png', '三种算法试过的起点')


# ---------------------------------------------------------------- 图 04

def fig04():
    d = R['demo']
    pat, text = d['pattern'], d['text']
    fig, y = new(4, 'BMH：先看窗口的最后一个字符',
                 '模式 abcabd 建一张表：某个字符在模式里最后一次出现在下标 i，'
                 '就让窗口挪 5−i 格；模式里没有的字符，整段跳过去。')
    cards = [('a', '挪 2 格', '下标 3'), ('b', '挪 1 格', '下标 4'),
             ('c', '挪 3 格', '下标 2'), ('其它', '挪 6 格', '模式里没有')]
    cw = 232
    for i, (ch, shift, why) in enumerate(cards):
        x = 52 + i * (cw + 12)
        fill = TINT_A if ch == 'c' else WHITE
        bd = AMBER if ch == 'c' else LIGHT
        fig.rect(x, y, x + cw, y + 168, fill=fill, outline=bd, width=3, radius=8)
        mono(fig, (x + 24, y + 20), ch, 44, color=INK)
        fig.text((x + 24, y + 84), shift, 40, color=INK)
        fig.text((x + 24, y + 130), why, 38, color=INK_SOFT)
    y2 = y + 210
    cwid, chh = 58, 52
    x0 = 214
    for start, label in ((0, '窗口 0：从右往左比，第 1 次就不同'), (3, '窗口 3：整段命中')):
        fig.text((x0, y2 - 44), label, 38, color=INK)
        for i, c0 in enumerate(text):
            cell(fig, x0 + i * cwid, y2, cwid, chh, c0, PALE, LIGHT, INK_SOFT)
        ok = 1 if start == 0 else 6
        for j, c0 in enumerate(pat):
            if start == 0 and j == 5:
                fill, bd, col = TINT_R, RED, RED
            elif start == 3:
                fill, bd, col = TINT_T, TEAL, TEAL
            else:
                fill, bd, col = WHITE, LIGHT, INK_SOFT
            cell(fig, x0 + (start + j) * cwid, y2 + chh + 8, cwid, chh, c0,
                 fill, bd, col)
        fig.text((x0 + 9 * cwid + 18, y2 + chh + 14), '比 %d 次' % ok, 38, color=INK)
        y2 += 2 * chh + 8 + 96
    save(fig, '04-bmh-table.png', 'BMH 的坏字符表与两个窗口')


# ---------------------------------------------------------------- 图 05 / 06

def bar_block(fig, y, label, pattern, row, vmax, wmax=460):
    fig.text((44, y), label, 38, color=INK_SOFT)
    mono(fig, (44, y + 34), pattern, 38, color=INK)
    yy = y
    for algo in ('naive', 'kmp', 'bmh', 'bm'):
        v = row[algo]['comparisons']
        x1 = hbar(fig, 470, yy, vmax, v, ALGO_COLOR[algo], wmax, 24)
        fig.text((x1 + 12, yy - 2), str(v), 38, color=ALGO_COLOR[algo])
        yy += 30
    return y + 140


def fig05():
    d = R['english']
    fig, y = new(5, '英文上：省掉的是一整段窗口',
                 '%d 个字符的英文。柱长是比较次数，每一组是同一个模式。' % d['length'])
    y = legend(fig, y, [(ALGO_COLOR[a], ALGO_NAME[a]) for a in
                        ('naive', 'kmp', 'bmh', 'bm')], step=180)
    vmax = max(r[a]['comparisons'] for r in d['rows'] for a in ALGO_COLOR)
    for r in d['rows']:
        y = bar_block(fig, y + 6, '长度 %d，%s' % (r['m'], '命中' if r['kind'] == 'hit'
                                                else '不在文本里'), r['pattern'],
                      r, vmax)
    save(fig, '05-english-bars.png', '英文文本上的比较次数')


def fig06():
    d = R['dna']
    fig, y = new(7, 'DNA 上：字母只有四种，好后缀补上缺口',
                 '%d 个字符、只有 4 种字母。坏字符表挪不远，BM 靠好后缀继续省。'
                 % d['length'])
    y = legend(fig, y, [(ALGO_COLOR[a], ALGO_NAME[a]) for a in
                        ('naive', 'kmp', 'bmh', 'bm')], step=180)
    vmax = max(r[a]['comparisons'] for r in d['rows'] for a in ALGO_COLOR)
    for r in d['rows']:
        y = bar_block(fig, y + 6, '长度 %d，%s' % (r['m'], '命中' if r['kind'] == 'hit'
                                                else '不在文本里'), r['pattern'],
                      r, vmax, wmax=380)
    save(fig, '07-dna-bars.png', 'DNA 文本上的比较次数')


# ---------------------------------------------------------------- 图 07

def fig07():
    d = R['shift_hist']
    fig, y = new(6, 'BMH 在英文上：十次里有八次半一次挪满',
                 '模式 the，%d 个字符的英文，一共 %d 个窗口。横轴是一次挪了几格，'
                 '纵轴是次数。' % (1288, d['windows']))
    counts = dict(d['counts'])
    x0, y0, x1, y1 = 220, y + 60, 940, y + 420
    peak = max(counts.values())

    def py(v):
        return y1 - v / (peak * 1.12) * (y1 - y0)

    fig.line((x0, y1), (x1, y1), color=INK, width=3)
    fig.line((x0, y0), (x0, y1), color=INK, width=3)
    for t in (0, 100, 200, 300, 400):
        fig.line((x0, py(t)), (x1, py(t)), color=LIGHT, width=2)
        fig.text((x0 - 16, py(t) - 22), str(t), 38, color=INK_SOFT, anchor='ra')
    slot = (x1 - x0) / 3
    for i, k in enumerate((1, 2, 3)):
        v = counts.get(k, 0)
        cx = x0 + slot * (i + 0.5)
        w = 150
        fig.rect(cx - w / 2, py(v), cx + w / 2, y1, fill=TINT_A, outline=AMBER,
                 width=3, radius=6)
        fig.text((cx, py(v) - 44), str(v), 40, color=AMBER, anchor='ma')
        fig.text((cx, y1 + 14), '%d 格' % k, 38, color=INK_SOFT, anchor='ma')
    note(fig, y1 + 76, '平均每次挪 %.2f 格，所以只用 %d 个窗口就把 %d 个字符的文本走完。'
         % (d['mean_shift'], d['windows'], 1288))
    save(fig, '06-shift-hist.png', 'BMH 的位移分布')


# ---------------------------------------------------------------- 图 08 / 09

def adv_figure(n, key, title, sub, highlight):
    d = R[key]['rows']
    fig, y = new(n, title, sub)
    y = legend(fig, y, [(ALGO_COLOR[a], ALGO_NAME[a]) for a in
                        ('naive', 'kmp', 'bmh', 'bm')], step=180)
    x0, y0, x1, y1 = 230, y + 40, 950, y + 440
    lo, hi = 2.5, 9.2

    def px(nn):
        return x0 + (math.log10(nn) - 3.0) / (math.log10(64000) - 3.0) * (x1 - x0)

    def py(v):
        return y1 - (math.log10(v) - lo) / (hi - lo) * (y1 - y0)

    fig.line((x0, y1), (x1, y1), color=INK, width=3)
    fig.line((x0, y0), (x0, y1), color=INK, width=3)
    ylabs = {3: '1000', 5: '10 万', 7: '1000 万', 9: '10 亿'}
    for t, lab in ylabs.items():
        fig.line((x0, py(10 ** t)), (x1, py(10 ** t)), color=LIGHT, width=2)
        fig.text((x0 - 16, py(10 ** t) - 22), lab, 38, color=INK_SOFT, anchor='ra')
    for nn in (1000, 8000, 64000):
        fig.line((px(nn), y0), (px(nn), y1), color=LIGHT, width=2)
        fig.text((px(nn), y1 + 14), str(nn), 38, color=INK_SOFT, anchor='ma')
    fig.text((x1, y1 + 62), '文本长度 n', 38, color=INK_SOFT, anchor='ra')
    fig.text((x0 - 16, y0 - 52), '比较次数', 38, color=INK_SOFT, anchor='la')
    for algo in ('naive', 'kmp', 'bmh', 'bm'):
        pts = [(px(r['n']), py(max(1, r[algo]['comparisons']))) for r in d]
        series(fig, pts, ALGO_COLOR[algo], 6 if algo == highlight else 4,
               None if algo == highlight else 10)
        fig.circle(pts[-1][0], pts[-1][1], 11 if algo == highlight else 8,
                   fill=ALGO_COLOR[algo], outline=ALGO_COLOR[algo])
    return fig, y1


def fig08():
    d = R['adversarial_a']['rows']
    fig, y1 = adv_figure(
        9, 'adversarial_a', '对抗输入 A：朴素匹配塌成二次',
        "text 是 n 个 a，pattern 是 (m−1) 个 a 加一个 b，m = n/4。"
        "每一格都要先比完 m−1 个 a 才知道不对。", 'naive')
    note(fig, y1 + 132, 'n 从 1000 涨到 64000（64 倍），朴素从 %s 次涨到 %s 次（约 4 千倍，'
                        '也就是 64 的平方）；另外三条只涨了 64 倍左右。'
         % (cn_num(d[0]['naive']['comparisons']),
            cn_num(d[-1]['naive']['comparisons'])))
    save(fig, '09-adversarial-a.png', '朴素匹配的二次退化')


def fig09():
    d = R['adversarial_b']['rows']
    fig, y1 = adv_figure(
        10, 'adversarial_b', '对抗输入 B：换成 BMH 塌成二次',
        "text 还是 n 个 a，pattern 换成 b 加 (m−1) 个 a。这次朴素一眼就看穿，"
        "BMH 却每格比完 m−1 个 a 才挪一步。", 'bmh')
    note(fig, y1 + 132, '同一批输入，胜者和败者换了位置：BMH 从 %s 次涨到 %s 次，'
                        '朴素反而是 %s 到 %s 次。BM 靠好后缀规则只挪 %d 个窗口。'
         % (cn_num(d[0]['bmh']['comparisons']), cn_num(d[-1]['bmh']['comparisons']),
            cn_num(d[0]['naive']['comparisons']), cn_num(d[-1]['naive']['comparisons']),
            d[-1]['bm']['windows']))
    save(fig, '10-adversarial-b.png', 'BMH 的二次退化')


# ---------------------------------------------------------------- 图 10

def fig10():
    d = R['goodsuffix']
    pat = d['pattern']
    m = d['m']
    fig, y = new(11, '好后缀说挪 8 格，坏字符只说 1 格',
                 'pattern = baaaaaaa，text 全是 a。从右边比过去，7 个 a 都对上，'
                 '第 8 次比到最左边的 b 才失配。')
    cw, ch = 74, 60
    x0 = 210
    for i in range(m):
        cell(fig, x0 + i * cw, y, cw, ch, 'a', PALE, LIGHT, INK_SOFT)
    for j, c0 in enumerate(pat):
        if j == 0:
            fill, bd, col = TINT_R, RED, RED
        else:
            fill, bd, col = TINT_T, TEAL, TEAL
        cell(fig, x0 + j * cw, y + ch + 10, cw, ch, c0, fill, bd, col)
    fig.text((x0, y + 2 * ch + 30), '已经匹配了 7 个 a，失配点在模式下标 0', 38,
             color=INK_SOFT)
    y2 = y + 2 * ch + 96
    cards = [('坏字符规则', '挪 %d 格' % d['bad_char_at_0'],
              'a 只在模式的下标 1..7 出现，规则给出的位移是负数', AMBER),
             ('好后缀规则', '挪 %d 格' % d['good_suffix_at_0'],
              '对上的 7 个 a 再出现时，前面紧挨着的还是 b', TEAL)]
    for i, (name, big, why, color) in enumerate(cards):
        x = 52 + i * 500
        fig.rect(x, y2, x + 470, y2 + 300, fill=WHITE, outline=color, width=4,
                 radius=10)
        fig.text((x + 24, y2 + 22), name, 40, bold=True, color=color)
        fig.text((x + 24, y2 + 82), big, 44, color=color)
        fig.wrap((x + 24, y2 + 152), why, 38, 424, color=INK_SOFT)
    note(fig, y2 + 328, '坏字符规则最小只挪 1 格；好后缀规则发现这 7 个 a 在模式里再出现时'
                        '前面还是 b，等于把刚失败的局面前移一格重演，于是整段跳过。'
                        'Boyer–Moore 取两者较大的，窗口数从 %d 降到 %d。'
         % (R['adversarial_b']['rows'][-1]['bmh']['windows'],
            R['adversarial_b']['rows'][-1]['bm']['windows']))
    save(fig, '11-good-suffix.png', '好后缀规则与坏字符规则的对比')


# ---------------------------------------------------------------- 图 11

def fig11():
    rows = R['perwindow']
    fig, y = new(8, '两个数字，两个含义',
                 '比较次数 = 推进次数 × 每次平均比几个字符。'
                 '对朴素和 BM 家族，推进次数就是窗口数；KMP 那一列记的是失配或命中的次数。'
                 'BM 家族省的是第一个数字。')
    cols = [(44, 'la'), (430, 'ra'), (640, 'ra'), (850, 'ra'), (1010, 'ra')]
    names = dict(english='英文', dna='DNA', runs='全是 a')
    head = [[('语料 / 算法', INK, True), ('推进次数', INK, True),
             ('比较次数', INK, True), ('每次平均', INK, True), ('', INK, True)]]
    table(fig, y, cols, head, row_h=58)
    y += 58
    body = []
    for r in rows:
        for algo in ('naive', 'kmp', 'bmh', 'bm'):
            body.append([('%s / %s' % (names[r['corpus']], ALGO_NAME[algo]),
                          ALGO_COLOR[algo], False),
                         ('%d' % r[algo]['windows'], INK, False),
                         ('%d' % r[algo]['comparisons'], INK, False),
                         ('%.2f' % r[algo]['per_window'], INK, False),
                         ('', INK, False)])
    table(fig, y, cols, body, row_h=52)
    note(fig, y + 52 * len(body) + 10,
         '英文和 DNA 上每次只比 1.1 到 1.4 个字符，谁都没占便宜；'
         '差别全在第一列。全是 a 的文本上，朴素一次要比 8 个字符，'
         'BMH 和 BM 只比 1 个。')
    save(fig, '08-two-numbers.png', '窗口数与每窗口比较次数')


# ---------------------------------------------------------------- 图 12

def fig12():
    d = R['utf8']
    bad = R['utf8_invalid']
    fig, y = new(12, '字节层搜索，字符层偏移',
                 '「é」在 UTF-8 里是两个字节。按字节找，命中次数一样，'
                 '但偏移量是按字节算的。')
    cw, ch = 80, 58
    lab_w = 252
    fig.text((44, y + 14), '字符', 38, color=INK_SOFT)
    chars = ['c', 'a', 'f', 'é']
    for i, c0 in enumerate(chars):
        fill = TINT_B if i == 3 else WHITE
        cell(fig, lab_w + i * cw, y, cw, ch, c0, fill, BLUE if i == 3 else LIGHT,
             BLUE if i == 3 else INK)
    fig.text((lab_w + 4 * cw + 14, y + 10), '4 个字符', 38, color=INK_SOFT)
    y2 = y + ch + 10
    fig.text((44, y2 + 14), 'UTF-8 字节', 38, color=INK_SOFT)
    for i, b in enumerate(['63', '61', '66', 'c3', 'a9']):
        fill = TINT_B if i in (3, 4) else PALE
        bd = BLUE if i in (3, 4) else LIGHT
        cell(fig, lab_w + i * cw, y2, cw, ch, b, fill, bd, BLUE if i in (3, 4) else INK_SOFT)
    fig.text((lab_w + 5 * cw + 14, y2 + 10), '5 个字节', 38, color=INK_SOFT)
    y3 = y2 + ch + 24
    fig.text((lab_w, y3), '字符偏移 9 和 20  ←→  字节偏移 10 和 38', 40, color=INK)
    note(fig, y3 + 62,
         '同一份文本，%d 个字符里「é」出现 %d 次；按字节搜也正好 %d 次，'
         '没有多也没有少。' % (len(d['text']), d['char_matches'], d['byte_matches']))
    y4 = y3 + 190
    fig.rect(52, y4, 1010, y4 + 200, fill=CREAM, outline=AMBER, width=3, radius=10)
    fig.text((76, y4 + 18), '针自己必须是合法 UTF-8', 40, bold=True, color=AMBER)
    fig.wrap((76, y4 + 74),
             '拿「中文也在这里」的第 4、5 个字节（%s）当针，按字节搜会在偏移 %d 处'
             '报告命中——那是第二个字的一半。字符层不存在这个位置。'
             % (bad['needle_hex'], bad['byte_positions'][0]), 38, 890, color=INK)
    save(fig, '12-utf8-bytes.png', 'UTF-8 下的字节搜索与字符偏移')


# ---------------------------------------------------------------- 图 13

def fig13():
    fig, y = new(13, '三句话')
    bullets(fig, y + 10, [
        '朴素匹配的问题不在「比得慢」，而在「每次失败都从零开始」。'
        'KMP 把「已经对上的尾巴」记成前缀函数，BM 家族把「最后一个字符」'
        '和「已经对上的后缀」记成位移表。',
        'KMP 的最坏情况是线性的，但在英文和 DNA 上它赢不了朴素多少，'
        '因为真正省时间的是「一个窗口挪好几格」。要稳定就选 KMP，要快就选 BM 家族。',
        '没有全局最优：对 n 个 a 加一个 b，朴素塌成二次；换成 b 加 n−1 个 a，'
        'BMH 塌成二次。写死一个算法之前，先想清楚输入是谁给的。',
    ], accent=TEAL)
    save(fig, '13-takeaways.png', '三句话')


def cover():
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill=BG, outline=None)
    fig.rect(0, 0, 1080, 12, fill=TEAL, outline=None)
    fig.text((80, 130), '一次失败', 104, bold=True)
    fig.text((80, 260), '不必从零开始', 104, bold=True)
    fig.text((80, 420), '从朴素匹配到 KMP、BMH 与 Boyer–Moore', 42, color=INK_SOFT)
    mono(fig, (80, 520), 'text = abcabcabd', 40, color=TEAL)
    mono(fig, (80, 580), 'pattern = abcabd', 40, color=TEAL)
    fig.text((80, 680), '朴素：4 个窗口、14 次比较', 42, color=INK)
    fig.text((80, 750), 'KMP：10 次比较；BMH：7 次比较、2 个窗口', 42, color=INK)
    fig.text((80, 850), '英文 1288 个字符：BMH 只用 461 个窗口', 42, color=INK)
    fig.text((80, 920), '对抗输入下谁都会塌成二次', 48, color=RED)
    fig.text((80, 1000), '2027-03-01', 40, color=GRAY)
    fig.trim(margin=60)
    fig.im = fig.im.crop((0, 0, 1080, 1080))
    fig.im.save(ART / 'cover.png')
    print('   cover.png', (ART / 'cover.png').stat().st_size, 'bytes')


def main():
    for fn in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig11, fig08,
               fig09, fig10, fig12, fig13):
        print(fn.__name__)
        fn()
    META.sort(key=lambda r: r['path'])
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, indent=1, ensure_ascii=False))
    print('wrote', HERE / 'figure-metadata.json', len(META), 'figures')
    cover()


if __name__ == '__main__':
    main()
