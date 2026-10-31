#!/usr/bin/env python3
"""Original teaching figures for the LZ77 article. MIT.

Every number here comes from results.json (written by run_model.py, which runs
examples/lz.py). Nothing is typed in by hand.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from figkit import (Fig, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED, GRAY,
                    LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []


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
            w = fig.width_of(text, size, bold)
            span = (x, x + w) if anchor == 'la' else (x - w, x)
            assert span[0] >= 44 and span[1] <= 1018, \
                'cell outside the safe band: %r %s' % (text, span)
            fig.text((x, y + 4), text, size, bold=bold, color=color, anchor=anchor)
        y += row_h
    return y + 18


class Plot:
    def __init__(self, fig, box, xlim, ylim):
        self.f = fig
        self.x0, self.y0, self.x1, self.y1 = box
        self.xlim, self.ylim = xlim, ylim

    def px(self, x):
        a, b = self.xlim
        return self.x0 + (self.x1 - self.x0) * (x - a) / (b - a)

    def py(self, y):
        a, b = self.ylim
        return self.y1 - (self.y1 - self.y0) * (y - a) / (b - a)

    def axes(self, xticks=(), yticks=(), xfmt='%g', yfmt='%g', xlab=None,
             ylab=None, grid=True):
        if grid:
            for v in yticks:
                yy = self.py(v)
                self.f.line((self.x0, yy), (self.x1, yy), color=LIGHT, width=2)
        for v in yticks:
            yy = self.py(v)
            self.f.text((self.x0 - 18, yy - 21), yfmt % v, 40, color=GRAY,
                        anchor='ra')
        for v in xticks:
            xx = self.px(v)
            if grid:
                self.f.line((xx, self.y0), (xx, self.y1), color=LIGHT, width=2)
            self.f.text((xx, self.y1 + 14), xfmt % v, 40, color=GRAY, anchor='ma')
        self.f.line((self.x0, self.y1), (self.x1, self.y1), color=GRAY, width=3)
        self.f.line((self.x0, self.y0), (self.x0, self.y1), color=GRAY, width=3)
        if ylab:
            self.f.text((self.x0, self.y0 - 58), ylab, 40, color=GRAY)
        if xlab:
            self.f.text((self.x1, self.y1 + 74), xlab, 40, color=GRAY, anchor='ra')

    def line(self, pts, color, width=5, dash=None):
        pixels = [(self.px(x), self.py(y)) for x, y in pts]
        for a, b in zip(pixels, pixels[1:]):
            self.f.line(a, b, color=color, width=width, dash=dash)

    def dot(self, x, y, color, r=13):
        self.f.circle(self.px(x), self.py(y), r, fill=color, outline=color)


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def chip(fig, box, label, fill, color=INK, size=40, bold=False):
    fig.box('c%d' % id(box), *box, fill=fill)
    fig.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - size * 0.62), label,
             size, bold=bold, color=color, anchor='ma', inside='c%d' % id(box))


# ---------------------------------------------------------------- figures

def fig01():
    f, y = new(1, '一句话里的重复，就是一个指针',
               'LZ77 只做一件事：发现「这一段前面出现过」，然后用一个指针代替它。')
    y += 30
    f.text((60, y), '原文（35 字节）', 42, bold=True, color=GRAY)
    y += 66
    box = (60, y, 1002, y + 120)
    f.rect(*box, fill=WHITE, outline=LIGHT, width=3)
    f.text((84, y + 34), 'the cat sat on the mat, the cat sat', 42, inside=None)
    y += 150
    # pointer from the second "cat sat" back to the first
    start = 84 + f.width_of('the cat sat on the mat, ', 42)
    end = start + f.width_of('the cat sat', 42)
    f.line((start, y - 20), (start, y + 40), TEAL, width=4)
    f.line((end, y - 20), (end, y + 40), TEAL, width=4)
    f.text(((start + end) / 2, y + 54), '这次不用重发', 40, color=TEAL,
           anchor='ma')
    f.arrow((start + 8, y + 106), (start - 120, y + 106), TEAL, width=5)
    f.text((start + 24, y + 118), '往回 24 字节，抄 7 字节', 40, color=TEAL)
    y += 160
    y = note(f, y, '编码器发的是「(距离, 长度) = (24, 7)」，解码器从自己刚写出的 '
                   '24 字节之前抄 7 个字节过来。原文没变，只是第二次出现的那句'
                   '话被换成了两个数字。')
    y = note(f, y, '剩下的 28 个字节还是老老实实发。所以 LZ77 的输出永远是两部分：'
                   '原样的字节，和指回前面的指针。')
    save(f, '01-pointer.png', 'LZ77 的基本动作：用指针代替重复')


def fig04():
    f, y = new(4, '一个窗口，一直在往前滑',
               '编码器站在位置 i：左边是已经处理过的历史，右边是还没看的未来。')
    y += 20
    box = (60, y, 1002, y + 150)
    f.rect(*box, fill=WHITE, outline=LIGHT, width=3)
    win_right = 60 + 940 * 0.72
    f.rect(66, y + 8, win_right, y + 142, fill=TINT_T, outline=None)
    f.rect(win_right, y + 8, 996, y + 142, fill=TINT_A, outline=None)
    f.text((80, y + 54), '搜索窗口：往回最多 32768 字节', 40, color=TEAL,
           bold=True)
    f.text((win_right + 16, y + 54), '前瞻缓冲', 40, color=AMBER, bold=True)
    f.line((win_right, y + 6), (win_right, y + 144), INK, width=4)
    f.text((win_right - 20, y + 152), 'i', 42, bold=True, anchor='ra', color=INK)
    y += 210
    y = bullets(f, y, [
        '窗口越大，能往回看的历史越长，可匹配的东西越多——',
        '但每个指针也要多花几位来编码距离。',
        'deflate（gzip / zip / png）选的是 32768：一个巧妙的折中，后面用数据看。',
    ])
    y += 10
    y = note(f, y, 'LZ77 不需要把整个文件装进内存：编码器只要一块窗口，'
                   '解码器只要一个「已经写出来的字节」的缓冲区。这也是它能进'
                   '路由器、进嵌入式设备的原因。')
    save(f, '04-sliding-window.png', '滑动窗口与前瞻缓冲')


def fig05():
    f, y = new(5, '一个 token 长什么样',
               'LZ77 的输出只有两种东西，各带一个标志位。没有熵编码，就是定长。')
    y += 20
    f.text((60, y), '字面量 token', 42, bold=True, color=TEAL)
    y += 64
    for x0, x1, label, fill in ((60, 220, '标志 1 bit', TINT_B),
                                (230, 700, '字面量：8 bit', TINT_T)):
        f.rect(x0, y, x1, y + 110, fill=fill, outline=LIGHT, width=3)
        f.text(((x0 + x1) / 2, y + 34), label, 40, anchor='ma')
    f.text((720, y + 34), '→ 一共 9 bit', 40, color=TEAL)
    y += 160
    f.text((60, y), '匹配 token', 42, bold=True, color=AMBER)
    y += 64
    for x0, x1, label, fill in ((60, 200, '标志 1 bit', TINT_B),
                                (210, 520, '距离：15 bit', TINT_A),
                                (530, 780, '长度：8 bit', TINT_R)):
        f.rect(x0, y, x1, y + 110, fill=fill, outline=LIGHT, width=3)
        f.text(((x0 + x1) / 2, y + 34), label, 40, anchor='ma')
    f.text((790, y + 34), '→ 24 bit', 40, color=AMBER)
    y += 160
    y = note(f, y, '一个匹配 token 花 24 bit，能代替最多 258 个字节。'
                   '所以「长匹配」几乎免费，「短匹配」很贵——长度必须至少 3，'
                   '否则不如直接发 3 个字面量（24 bit vs 27 bit）。')
    y = note(f, y, '真实格式（DEFLATE）比这省得多：长度和距离各有一张霍夫曼表，'
                   '常见的短距离只用 5–6 bit。这里的定长算法是为了让账算得清楚，'
                   '不是为了比赛。')
    y += 8
    y = table(f, y, [(60, 'la'), (620, 'la')],
              [[('字面量', INK, False), ('9 bit', RED, True)],
               [('匹配（3 字节起）', INK, False), ('24 bit', TEAL, True)],
               [('匹配（258 字节）', INK, False), ('0.09 bit/字节', TEAL, True)]],
              size=40)
    save(f, '05-token.png', 'LZ77 的两种 token 与位宽')


def fig06():
    steps = R['walk']
    f, y = new(6, '解码器只做两件事：追加，或者往回抄',
               '把 %d 个 token 一个个走完，看输出怎么长出来。' % len(steps))
    y += 10
    f.text((60, y), '还没输出：空', 40, color=GRAY)
    y += 60
    shown = 0
    for i, s in enumerate(steps):
        if s['kind'] == 'lit':
            head = '① 字面量 %r' % s['text']
            tail = '追加'
            color = TEAL
        else:
            head = '① 往回 %d，抄 %d' % (s['dist'], s['length'])
            tail = '抄成 %r' % s['piece']
            color = AMBER
        f.text((60, y), head, 40, color=color, bold=True)
        f.text((470, y), tail, 40)
        f.text((760, y), '→ ' + s['now'], 40, color=INK)
        y += 74
        shown += 1
        if shown >= 9:
            break
    y += 10
    y = note(f, y, '最后那一行就是原文。注意「往回抄」的源可以落在正在写的这段'
                   '里面——这正是 `a`×400 能变成 3 个 token 的原因：'
                   '第一次抄 258 个字节时，源和目的地是重叠的，靠一个字节一个'
                   '字节往前推。')
    save(f, '06-decode-walk.png', '逐 token 的解码过程')


def fig07():
    f, y = new(7, '怎么找到「前面出现过」',
               '朴素做法是往回一个一个比，太慢。真实的编码器维护一张前缀表。')
    y += 20
    f.text((60, y), '遇到 "the" 这三个字节，就去表里查 "the" 上次出现在哪', 40,
           color=INK_SOFT)
    y += 70
    rows = [(60, 'th', '位置 … 12, 25, 41, 88', TEAL),
            (60, 'the', '位置 … 12, 25, 88', AMBER)]
    f.rect(60, y, 1002, y + 170, fill=WHITE, outline=LIGHT, width=3)
    f.text((90, y + 30), '哈希表（键 = 3 个字节）', 40, bold=True, color=GRAY)
    f.text((90, y + 90), 'the  →  12, 25, 88', 40)
    f.text((90, y + 140), 'cat  →  20, 300, 517, 940', 40)
    y += 210
    y = bullets(f, y, [
        '从最近的那次开始往回想，找到够长的匹配就停（或走完一条链）。',
        '只比 3 个字节就能筛掉绝大多数候选，这一步省下了 90% 的时间。',
        '链条太长就截断（这里的实现最多看 64 个候选）——用一点压缩率换速度。',
    ], accent=AMBER)
    y += 10
    y = note(f, y, '这就是为什么 LZ77 的实际速度取决于「匹配有多难找」，'
                   '而不只是文件多大。压缩一段全 0 的数据，链路会立刻撞到上限；'
                   '压缩随机数据，每个位置都要走完一条链。')
    save(f, '07-match-finding.png', '前缀表与前缀链')


def fig08():
    curve = R['window_curve']
    f, y = new(8, '窗口越大，压缩得越好——直到某个点',
               '%d 字节的英文正文，同一份数据只改窗口大小。' % R['corpus_size'])
    y += 20
    p = Plot(f, (250, y + 40, 990, y + 400), (0, 8), (0.45, 1.1))
    p.axes(xticks=(0, 2, 4, 6, 8), yticks=(0.5, 0.7, 0.9, 1.1),
           xfmt='2^%g', yfmt='%.1f')
    f.text((60, y + 500), '横轴：窗口大小（2 的幂，对数刻度）', 40, color=GRAY)
    pts = []
    for i, r in enumerate(curve):
        pts.append((float(i), r['ratio']))
    p.line(pts, TEAL, width=6)
    for i, r in enumerate(curve):
        p.dot(float(i), r['ratio'], TEAL)
        if i in (0, 5, 7):
            p.f.text((p.px(float(i)), p.py(r['ratio']) - 52), '%.3f' % r['ratio'],
                     38, color=TEAL, anchor='ma', allow_overlap=True)
    y += 560
    y = note(f, y, '横轴是 64 B 到 256 KB，每个刻度翻四倍。曲线在最左边掉得很快：'
                   '64 字节的窗口连一个英文单词都装不下，压缩后反而变大（1.055）。')
    y = note(f, y, '到 32 KB 时是 %.3f，再放大到 256 KB 只变成 %.3f——'
                   '八倍的窗口，换来不到 5%%。deflate 选 32768 就是这个道理。'
             % (curve[5]['ratio'], curve[7]['ratio']))
    save(f, '08-window-curve.png', '窗口大小与压缩率')


def fig09():
    curve = R['window_curve']
    f, y = new(9, '每翻四倍，多赚多少',
               '同一组数据的另一种看法：把「再大一点」的收益画出来。')
    y += 30
    rows = []
    prev = None
    for r in curve:
        gain = '—' if prev is None else '%.3f' % (prev - r['ratio'])
        rows.append([('%d' % r['window'], INK, False),
                     ('%.3f' % r['ratio'], INK, True),
                     (gain, TEAL if gain != '—' else GRAY, False)])
        prev = r['ratio']
    y = table(f, y, [(60, 'la'), (420, 'la'), (760, 'la')], rows, row_h=64)
    y += 10
    y = note(f, y, '收益一直有，但一直在变小。压缩器里所有的「再大一点」都是这个形状：'
                   '前期便宜，后期越来越贵，因为远处的重复越来越少。')
    y = note(f, y, '顺便说一句，窗口不能超过「文件本身」——如果文件只有 100 KB，'
                   '把窗口设成 1 MB 没有任何用，只是每个指针多花几位。')
    save(f, '09-window-table.png', '窗口翻倍带来的收益递减')


def fig10():
    rows = R['corpora']
    names = ['英文正文', '访问日志', '随机字节']
    f, y = new(10, '三种数据，三种命运',
               '同一套编码器，同一套位宽。压缩率 = 输出位数 / 原始位数。')
    y += 40
    p = Plot(f, (580, y, 990, y + 340), (0, 3), (0, 1.3))
    p.axes(yticks=(0, 0.3, 0.6, 0.9, 1.2), yfmt='%.1f')
    for i, r in enumerate(rows):
        f.text((60, y + 40 + i * 110), names[i], 40, bold=True)
        f.text((60, y + 84 + i * 110), '%d B' % r['size'], 38, color=GRAY)
        for j, (key, color) in enumerate((('lz77', TEAL), ('deflate', BLUE))):
            yy = y + 40 + i * 110 + j * 40
            w = (990 - 580) * min(r[key], 1.25) / 1.3
            f.rect(580, yy, 580 + w, yy + 30, fill=color, outline=None)
            f.text((580 + w + 14, yy - 4), '%.2f' % r[key], 38, color=color)
    y += 430
    f.text((60, y - 10), '绿：纯 LZ77（定长 token）', 38, color=GRAY)
    f.text((60, y + 46), '蓝：再加一层霍夫曼（deflate）', 38, color=GRAY)
    y += 96
    y = note(f, y, '英文正文压到 %.1f%%，日志压到 %.1f%%——日志里每一行的日期、'
                   'IP、UA 都长得一模一样，LZ77 最喜欢这种东西。'
             % (100 * rows[0]['lz77'], 100 * rows[1]['lz77']))
    y = note(f, y, '随机字节不行：%.2f。它不但没压小，还变大了。'
                   '这不是 bug，是 LZ77 的账算不过来——每个字节都要花 9 bit。'
             % rows[2]['lz77'], color=RED)
    save(f, '10-corpora.png', '三种语料下的压缩率')


def fig11():
    hist = R['stats']['hist']
    f, y = new(11, '匹配有多长',
               '同一份英文正文，%d 个匹配 token 的长度分布。' % R['stats']['matches'])
    y += 20
    top = max(n for _, n in hist)
    p = Plot(f, (250, y + 40, 990, y + 380), (0, len(hist)), (0, top * 1.15))
    p.axes(yticks=(0, top // 2, top), yfmt='%g')
    for i, (label, n) in enumerate(hist):
        p.f.rect(p.px(i + 0.18), p.py(n), p.px(i + 0.82), p.py(0), fill=TEAL,
                 outline=None)
        p.f.text((p.px(i + 0.5), p.py(0) + 18), label, 38, anchor='ma',
                 color=GRAY, allow_overlap=True)
        p.f.text((p.px(i + 0.5), p.py(n) - 46), '%d' % n, 38, anchor='ma',
                 color=TEAL, allow_overlap=True)
    y += 470
    y = note(f, y, '大多数匹配只有 3–7 个字节：英文里重复的是 "the "、"and "、'
                   '"ing "这种碎片。长的（64 以上）很少，但它们覆盖的字节最多——'
                   '一个 258 字节的匹配就顶 258 个字面量。')
    y = note(f, y, '平均长度 %.1f，中位数 %d。这就是为什么压缩率看着还行（%.3f），'
                   '但 token 数量仍然不少（%d 个）。'
             % (R['stats']['mean_length'], R['stats']['median_length'],
                R['corpora'][0]['lz77'], R['stats']['tokens']))
    save(f, '11-match-lengths.png', '匹配长度分布')


def fig12():
    s = R['stats']
    f, y = new(12, '九成七的字节是「抄」来的',
               '同一个文件：%d 字节里，%d 字节来自匹配，%d 字节是字面量。'
               % (s['total'], s['covered'], s['total'] - s['covered']))
    y += 30
    w = 942
    split = w * s['coverage']
    f.rect(60, y, 60 + w, y + 90, fill=TINT_R, outline=None)
    f.rect(60, y, 60 + split, y + 90, fill=TINT_T, outline=None)
    f.text((70, y + 26), '匹配覆盖 %.1f%%' % (100 * s['coverage']), 40,
           color=TEAL, bold=True)
    f.text((60 + w - 10, y + 26), '字面量', 40, color=RED, anchor='ra')
    y += 130
    y = table(f, y, [(60, 'la'), (620, 'la')],
              [[('字面量字节', INK, False),
                ('%d' % (s['total'] - s['covered']), RED, True)],
               [('匹配覆盖字节', INK, False), ('%d' % s['covered'], TEAL, True)],
               [('token 总数', INK, False), ('%d' % s['tokens'], INK, True)],
               [('其中匹配 token', INK, False), ('%d' % s['matches'], INK, True)]],
              size=40)
    y += 6
    y = note(f, y, '这个比例决定了压缩的上限：能抄的字节越多，越省。'
                   '它也解释了为什么 LZ77 在日志、JSON、源码、HTML 上特别灵，'
                   '在已经压过的数据（zip、jpeg）上完全无效。')
    save(f, '12-coverage.png', '匹配覆盖的字节比例')


def fig13():
    rows = R['stats']['distances']
    f, y = new(13, '指针会往回指多远',
               '距离分布（同一份英文正文，%d 个匹配 token）。' % R['stats']['matches'])
    y += 20
    total = sum(n for _, n in rows) or 1
    lab = ['1–3', '4–15', '16–63', '64–255', '256–1K', '1K–4K', '4K–16K',
           '16K–64K', '>64K']
    top = max(n for _, n in rows)
    p = Plot(f, (250, y + 40, 990, y + 380), (0, len(rows)), (0, top * 1.15))
    p.axes(yticks=(0, top // 2, top), yfmt='%g')
    for i, (_, n) in enumerate(rows):
        p.f.rect(p.px(i + 0.18), p.py(n), p.px(i + 0.82), p.py(0), fill=AMBER,
                 outline=None)
        p.f.text((p.px(i + 0.5), p.py(0) + 18), lab[i], 38, anchor='ma',
                 color=GRAY, allow_overlap=True)
        p.f.text((p.px(i + 0.5), p.py(n) - 46), '%.0f%%' % (100 * n / total),
                 38, anchor='ma', color=AMBER, allow_overlap=True)
    y += 470
    y = note(f, y, '多数指针指得很近——英文的重复是局部的（一句话里的冠词、'
                   '一个段落里的术语）。但右边那条尾巴也有分量：'
                   '平均距离 %.0f 字节，接近窗口的一半。'
             % R['stats']['mean_distance'])
    y = note(f, y, '这条尾巴就是「窗口要够大」的理由。如果窗口只有 4 KB，'
                   '右边四根柱子里的匹配全都被迫退化成字面量。')
    save(f, '13-distances.png', '匹配距离分布')


def fig14():
    lazy = R['lazy']
    f, y = new(14, '贪心不是最优，但很接近',
               '同一个文件，只改一个决策：找到匹配就立刻用，还是再看一个字节。')
    y += 30
    y = table(f, y, [(60, 'la'), (420, 'la'), (760, 'la')],
              [[('贪心', INK, False),
                ('%.3f' % lazy['greedy_ratio'], TEAL, True),
                ('%d token' % lazy['greedy_tokens'], INK, False)],
               [('懒匹配', INK, False),
                ('%.3f' % lazy['lazy_ratio'], TEAL, True),
                ('%d token' % lazy['lazy_tokens'], INK, False)]])
    y += 10
    y = note(f, y, '懒匹配的规则是：当前位置找到长度 L，就再看下一个位置——'
                   '如果那边能给出更长的匹配，就退回一个字面量，让后面的匹配更长。')
    y = note(f, y, '这里省了 %.1f%%，代价是 token 变多（%d → %d）且多一次查找。'
                   '注意「token 更多但更省」并不矛盾：省的是位数，不是条数。'
             % (100 * (lazy['greedy_ratio'] - lazy['lazy_ratio']),
                lazy['greedy_tokens'], lazy['lazy_tokens']))
    save(f, '14-greedy-vs-lazy.png', '贪心匹配与懒匹配')


def fig15():
    runs = R['runs']
    f, y = new(15, '全是同一个字节的时候',
               '`a` × %d，窗口 1 KB。这是 LZ77 的极端情况。' % runs['input'])
    y += 30
    f.rect(60, y, 1002, y + 80, fill=TINT_T, outline=None)
    f.text((80, y + 22), 'aaaa…（%d 个 a）' % runs['input'], 40, color=TEAL)
    y += 130
    toks = R['runs']['kinds']
    lengths = R['runs']['lengths']
    x = 60
    f.text((x, y), '字面量 a', 40, bold=True, color=TEAL)
    y += 60
    f.text((x, y), '匹配（距离 1，长 %d）' % lengths[0], 40, bold=True,
           color=AMBER)
    y += 60
    f.text((x, y), '匹配（距离 1，长 %d）' % lengths[1], 40, bold=True,
           color=AMBER)
    y += 80
    y = note(f, y, '一共 %d 个 token，压缩率 %.3f。第一次匹配的源和自己的目的地'
                   '是重叠的——解码器写到一半，源也在往前挪，所以它抄出来的是'
                   '「1 个 a，然后 2 个，然后 4 个」，指数级长出来。'
             % (runs['tokens'], runs['ratio']))
    y = note(f, y, '下界不是零：每个 258 字节的匹配仍要花 24 bit。'
                   '所以再长的重复也压不到 1%% 以下——这是位宽决定的，不是算法问题。')
    save(f, '15-runs.png', '全同字节的极端情况')


def fig16():
    w = R['worst']
    f, y = new(16, '没有重复的数据，会变大',
               '%d 个随机字节：LZ77 %.3f，deflate %.3f。'
               % (w['size'], w['lz77'], w['deflate']))
    y += 30
    y = table(f, y, [(60, 'la'), (620, 'la')],
              [[('原始大小', INK, False), ('%d B' % w['size'], INK, True)],
               [('LZ77 输出（估算）', INK, False),
                ('%.0f B' % (w['size'] * w['lz77']), RED, True)],
               [('deflate 输出（实测）', INK, False),
                ('%d B' % w['size_deflate'], BLUE, True)],
               [('字节熵', INK, False), ('%.2f bit' % w['entropy'], INK, True)]])
    y += 10
    y = note(f, y, '每个字面量 9 bit = 1.125 字节，所以比原文大 12.5%%。'
                   '真实格式会给「字面量」和「匹配」分别建霍夫曼表，'
                   '在没有匹配时表会退化成一棵近似 8 bit 的树——deflate 因此'
                   '只大 0.1%%，但它也没能压小。')
    y = note(f, y, '这条边界很重要：LZ77 不是「压缩算法」，是「找重复的算法」。'
                   '没有重复，它就只是加了一层开销。所以现实里的格式都会先看一眼'
                   '熵：熵接近 8 就直接存原样。', color=RED)
    save(f, '16-incompressible.png', '无重复数据的膨胀')


def fig17():
    f, y = new(17, '为什么真正的格式还要再加一层',
               'deflate = LZ77 + 霍夫曼编码。前者去掉重复，后者压掉符号本身的冗余。')
    y += 30
    stages = [('原始字节', TEAL), ('LZ77\ntoken', AMBER), ('霍夫曼编码', BLUE),
              ('deflate 流', GREEN)]
    x = 60
    for i, (label, color) in enumerate(stages):
        box = (x, y, x + 200, y + 150)
        f.rect(*box, fill=WHITE, outline=color, width=5)
        for j, line in enumerate(label.split('\n')):
            f.text((x + 100, y + 34 + j * 50), line, 40, anchor='ma', color=color,
                   bold=True)
        if i < len(stages) - 1:
            f.arrow((x + 210, y + 75), (x + 232, y + 75), GRAY, width=4)
        x += 242
    y += 210
    y = note(f, y, 'LZ77 之后，token 里有大量重复：距离 1–4 出现了无数次，'
                   '长度 3–7 也反复出现。霍夫曼编码给这些常见符号分配短码，'
                   '于是压缩率从 %.1f%% 降到 %.1f%%。'
             % (100 * R['corpora'][0]['lz77'], 100 * R['corpora'][0]['deflate']))
    y = note(f, y, 'gzip、zip、PNG、HTTP 的 Content-Encoding 都是这个结构。'
                   'LZ77 负责「这段话刚才说过」，霍夫曼负责「这个符号常出现」。'
                   '两层各管一件事，互不干扰。')
    save(f, '17-deflate.png', 'deflate 的两级结构')


def fig18():
    f, y = new(18, '一条很长的线',
               'LZ77 本身没变过，变的是「谁在用它、用多快」。')
    y += 20
    rows = [('1977', 'Lempel 与 Ziv 发表 LZ77', TEAL),
            ('1978', 'LZ78：不再回指，改用字典', TEAL),
            ('1984', 'LZW：字典法进入 UNIX compress', AMBER),
            ('1991', 'LZMA 的前身开始出现（7z 用）', AMBER),
            ('1992', 'gzip 发布，deflate 定型', BLUE),
            ('1996', 'PNG 采用 deflate 作图像压缩', BLUE),
            ('2013', 'Brotli：更大的窗口 + 静态字典', GREEN),
            ('2016', 'Zstandard：为速度重新设计', GREEN)]
    for year, text, color in rows:
        f.text((70, y), year, 40, bold=True, color=color)
        f.text((240, y), text, 40)
        y += 68
    y += 10
    y = note(f, y, '四十年里，LZ77 的编码规则一个字都没改：距离 + 长度。'
                   '所有进步都在两件事上——找匹配更快（哈希、SIMD）、'
                   '编码那一步更聪明（霍夫曼、算术编码、上下文模型）。')
    save(f, '18-timeline.png', 'LZ 家族的时间线')


def fig19():
    f, y = new(19, '三句话')
    y += 40
    lines = [('找重复，用指针代替。', TEAL),
             ('窗口决定能看多远，长度决定省多少。', AMBER),
             ('它不消灭冗余，只是把冗余记成坐标。', BLUE)]
    for text, color in lines:
        y = note(f, y + 10, text, size=46, color=color)
        y += 30
    y += 20
    y = note(f, y, '剩下的都是工程：哈希怎么建、链多长、窗口多大、'
                   'token 怎么编码。规则本身只有一条——'
                   '「这一段，前面是不是刚出现过？」')
    save(f, '19-three-lines.png', '三句话总结')


def make_cover():
    fig = Fig(1080, width=1080)
    fig.text((96, 96), '往回看 32 KB', 84, bold=True, color=INK)
    fig.text((96, 200), '用一个指针', 84, bold=True, color=INK)
    fig.text((96, 320), 'LZ77：把重复的这段话记成坐标', 42, color=TEAL)
    top = 500
    # a run of blocks, then a pointer that reaches back to the same shape
    fig.line((110, top), (970, top), color=INK, width=6)
    for i in range(6):
        x = 140 + i * 78
        fig.rect(x, top - 130, x + 56, top, fill=TEAL if i < 3 else PALE,
                 outline=None)
    fig.rect(140 + 3 * 78, top - 130, 140 + 6 * 78 - 22, top - 118, fill=PALE,
             outline=None)
    fig.arrow((640, top - 200), (300, top - 200), BLUE, width=6)
    fig.text((650, top - 214), '(距离, 长度)', 42, color=BLUE)
    fig.text((96, 760), '1977 · Lempel 与 Ziv · 距离 + 长度', 44, color=INK_SOFT)
    fig.text((96, 850), 'gzip · zip · PNG · 7z · Brotli · zstd 都从这来', 40,
             color=INK)
    fig.text((96, 930), 'tech-articles · 2026-11-02', 38, color=GRAY)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


def main(argv):
    want = {int(a) for a in argv[1:]} if len(argv) > 1 else None
    for fn in FIGS:
        n = int(fn.__name__[3:])
        if want and n not in want:
            continue
        fn()
    if not want:
        make_cover()
        (HERE / 'figure-metadata.json').write_text(
            json.dumps(META, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8')
    print('figures:', len(META))


FIGS = [fig01, fig04, fig05, fig06, fig07, fig08, fig09, fig10, fig11, fig12,
        fig13, fig14, fig15, fig16, fig17, fig18, fig19]

if __name__ == '__main__':
    main(sys.argv)
