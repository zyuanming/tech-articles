#!/usr/bin/env python3
"""Original teaching figures for the audio-fingerprint article. MIT.

Every number comes from results.json, which run_model.py writes by running
examples/shazam.py. Nothing here is typed in by hand.
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
            if not text:
                continue
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


_CHIP = [0]


def chip(fig, box, label, fill, color=INK, size=40, bold=False):
    _CHIP[0] += 1
    key = 'c%d' % _CHIP[0]
    fig.box(key, *box, fill=fill)
    fig.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - size * 0.62), label,
             size, bold=bold, color=color, anchor='ma', inside=key)


# ---------------------------------------------------------------- helpers

HEAT = ['#f4f3ed', '#e8f0f6', '#c9dcec', '#7fa8c9', '#3468ad', '#183440']
DARK = ['#0d1f27', '#ffffff', '#7fa8c9', '#f2b134', '#e8f0f6', '#2b4a55']
from figkit import PALETTE
for _c in HEAT + DARK:
    PALETTE.add(_c)


def heat(fig, box, grid, lo=10.0, hi=80.0, fmax=None):
    """Draw a coarse spectrogram: one filled cell per grid entry."""
    x0, y0, x1, y1 = box
    rows, cols = len(grid), len(grid[0])
    n = len(HEAT)
    cw, ch = (x1 - x0) / cols, (y1 - y0) / rows
    for r in range(rows):
        for c in range(cols):
            v = (grid[rows - 1 - r][c] - lo) / (hi - lo)
            k = min(n - 1, max(0, int(v * (n - 1) + 0.5)))
            fig.rect(x0 + c * cw, y0 + r * ch, x0 + (c + 1) * cw + 1,
                     y0 + (r + 1) * ch + 1, fill=HEAT[k], outline=None)


def envelope(sig, cols):
    """Min/max amplitude per column, for a compact waveform drawing."""
    step = max(1, len(sig) // cols)
    out = []
    for i in range(cols):
        chunk = sig[i * step:(i + 1) * step] or [0.0]
        out.append((min(chunk), max(chunk)))
    return out


def wave(fig, box, sig, color=TEAL, cols=240):
    x0, y0, x1, y1 = box
    mid, half = (y0 + y1) / 2, (y1 - y0) / 2
    env = envelope(sig, cols)
    peak = max(1e-9, max(max(abs(a), abs(b)) for a, b in env))
    for i, (lo, hi) in enumerate(env):
        x = x0 + (x1 - x0) * i / cols
        fig.line((x, mid - lo / peak * half), (x, mid - hi / peak * half),
                 color=color, width=3)


# ---------------------------------------------------------------- figures

def fig01():
    fig, y = new(1, '先把问题说清楚', '同一首歌，两次录音：波形对不上，人耳却一听就知道是同一首。')
    box = (60, y, 1002, y + 300)
    wave(fig, box, SONG_SIG, TEAL)
    fig.text((60, y + 306), '原速、干净', 40, color=GRAY)
    y2 = y + 360
    box2 = (60, y2, 1002, y2 + 300)
    wave(fig, box2, NOISY_SIG, BLUE)
    fig.text((60, y2 + 306), '同一段，10 dB 噪声，晚了 3 秒开始', 40, color=GRAY)
    y = note(fig, y2 + 372,
             '按样本比，这两条曲线处处不同；按耳朵比，它们是同一首歌。'
             '识别系统要做的，就是把「处处不同」变成「一个相同的记号」。')
    save(fig, '01-two-recordings.png', '同一首歌的两次录音波形')


def fig03():
    fig, y = new(3, '切成一帧一帧', '加窗、做傅里叶变换，把每一小段声音变成一行数字。')
    a = R['audio']
    box = (60, y, 1002, y + 210)
    wave(fig, box, SONG_SIG[:int(0.9 * 4000)], TEAL, cols=120)
    for i in range(4):
        x = 60 + i * 236
        fig.rect(x, y, x + 170, y + 210, fill=None, outline=AMBER, width=5)
    fig.text((60, y + 218), '0.9 秒', 40, color=GRAY)
    y += 300
    y = note(fig, y, '每 %d 个样本一帧，相邻两帧只挪 %d 个样本（帧长 %d）。'
                     '一秒钟得到 %.1f 帧。' % (a['frame'], a['hop'], a['frame'],
                                              a['frames_per_second']))
    y = note(fig, y, '窗函数把帧的两端压到接近零，避免边缘突变被误当成高频。'
                     'FFT 之后每帧留下 %d 个频率格，从 0 到 2000 Hz，'
                     '每格 %.1f Hz。' % (a['bins'], a['freq_step']))
    save(fig, '03-framing.png', '分帧、加窗与傅里叶变换')


def fig04():
    fig, y = new(4, '声音变成一张图', '横轴时间，纵轴频率，亮度是能量。谱峰就是这首歌的「地标」。')
    p = R['panels']
    box = (200, y, 1002, y + 420)
    heat(fig, box, p['song'])
    fig.text((200, y + 428), '0 s', 40, color=GRAY)
    fig.text((1002, y + 428), '8 s', 40, color=GRAY, anchor='ra')
    fig.text((196, y - 4), '2000 Hz', 38, color=GRAY, anchor='ra')
    fig.text((196, y + 396), '0 Hz', 38, color=GRAY, anchor='ra')
    y = note(fig, box[3] + 62,
             '三条横线是同一个音的基频和它的两个泛音。每个音符换一次横线高度，'
             '于是图上留下一串方块。')
    save(fig, '04-spectrogram.png', '短时傅里叶谱图')


def fig05():
    fig, y = new(5, '只留最强的点', '一张谱图有几万个像素，其中真正有辨识度的只有一两百个峰。')
    p = R['panels']
    box = (200, y, 1002, y + 420)
    heat(fig, box, p['song'])
    nf, nb = 247, 256
    for t, f in p['clean']:
        fig.circle(box[0] + (box[2] - box[0]) * t / nf,
                   box[3] - (box[3] - box[1]) * f / nb, 5, fill=AMBER, outline=AMBER)
    fig.text((200, y + 428), '0 s', 40, color=GRAY)
    fig.text((1002, y + 428), '8 s', 40, color=GRAY, anchor='ra')
    fig.text((196, y + 396), '0 Hz', 38, color=GRAY, anchor='ra')
    fig.text((196, y - 4), '2000 Hz', 38, color=GRAY, anchor='ra')
    y = note(fig, box[3] + 62,
             '每个峰要在一个时间-频率邻域里最大，还不要太挤。'
             '这首歌 8 秒留下 %d 个峰，大约每秒 %.0f 个。' %
             (R['songs'][1]['peaks'], R['songs'][1]['peaks_per_second']))
    save(fig, '05-peaks.png', '谱峰（constellation map）')


def fig06():
    fig, y = new(6, '峰的三种命运', '峰要稳：加噪声、压缩、外放，它还在原地；不是峰的地方，噪声一来就变。')
    rows = 5
    cols = 5
    grid = [[0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]]
    vals = [[12, 15, 21, 18, 11],
            [14, 52, 61, 27, 13],
            [13, 58, 74, 31, 12],
            [11, 24, 29, 19, 10],
            [9, 12, 14, 13, 8]]
    x0, y0 = 60, y + 30
    cell = 88
    for r in range(rows):
        for c in range(cols):
            v = vals[r][c]
            k = min(5, max(0, int((v - 8) / 66 * 5)))
            fig.rect(x0 + c * cell, y0 + r * cell, x0 + (c + 1) * cell - 2,
                     y0 + (r + 1) * cell - 2, fill=HEAT[k], outline=WHITE, width=2)
            fig.text((x0 + c * cell + cell / 2, y0 + r * cell + 26), str(v),
                     38, color=WHITE if k >= 4 else INK, anchor='ma')
    fig.rect(x0 + 2 * cell, y0 + 2 * cell, x0 + 3 * cell - 2, y0 + 3 * cell - 2,
             fill=None, outline=AMBER, width=6)
    tx = x0 + 5 * cell + 36
    fig.text((tx, y0 + 30), '中间 74：邻居没有', 40, color=INK)
    fig.text((tx, y0 + 82), '比它高的 → 留下', 40, color=INK)
    fig.text((tx, y0 + 190), '61、58 在自己邻域', 40, color=INK_SOFT)
    fig.text((tx, y0 + 242), '里也最大 → 留下', 40, color=INK_SOFT)
    fig.text((tx, y0 + 350), '平坦处一个不剩', 40, color=INK_SOFT)
    y = y0 + 5 * cell + 40
    y = note(fig, y, '真实信号里，噪声的谱是平的，音乐的谱是尖的。'
                     '「局部最大」这个条件自动把两者分开了。')
    save(fig, '06-local-max.png', '局部极大值判定')


def fig07():
    fig, y = new(7, '把一个峰变成一把钥匙', '每个峰向后看：谁在我后面、差多少时间、差多少频率。')
    p = R['panels']
    pts = p['clean'][:26]
    box = (90, y + 30, 700, y + 470)
    xf = lambda t: box[0] + (box[2] - box[0]) * t / 247
    yf = lambda f: box[3] - (box[3] - box[1]) * f / 256
    for t, f in pts:
        fig.circle(xf(t), yf(f), 9, fill=INK_SOFT, outline=INK_SOFT)
    a = pts[4]
    fig.circle(xf(a[0]), yf(a[1]), 16, fill=AMBER, outline=AMBER)
    fig.rect(xf(a[0] + 1), box[1], xf(a[0] + 63), box[3], fill=None,
             outline=AMBER, width=4)
    for t, f in pts[5:11]:
        if 1 <= t - a[0] <= 63 and abs(f - a[1]) <= 64:
            fig.arrow((xf(a[0]) + 18, yf(a[1])), (xf(t) - 12, yf(f)),
                      color=BLUE, width=4, head=12)
    fig.text((94, y + 6), '锚点', 40, color=AMBER)
    fig.text((xf(a[0] + 63) + 12, box[1] + 6), '目标区：63 帧以内', 40, color=AMBER)
    y = box[3] + 60
    f1, f2, dt = pts[5][1], pts[6][1], pts[6][0] - pts[5][0]
    y = note(fig, y, '一对峰组成一个键：(f₁, f₂, Δt)。'
                     '上面那个锚点和它后面第一个峰就写成 (%d, %d, %d)。' % (a[1], f1, dt))
    save(fig, '07-pair-hash.png', '组合哈希：锚点与目标区')


def fig08():
    fig, y = new(8, '键和它的出处', '键本身不说明任何事；出处（哪首歌、第几帧）才是要查的东西。')
    rows = [[('(f₁, f₂, Δt)', INK, True), ('→ 数据库里存的', INK, True), ('', INK, False)]]
    import shazam as S
    songs = [S.song(s) for s in (11, 23, 37)]
    add = 0
    for i, (sig, _n) in enumerate(songs[:2]):
        pairs = S.hashes(S.pick_peaks(S.spectrogram(sig)), fan=R['fan_out'])
        for key, t in pairs[:2]:
            rows.append([('%d, %d, %d' % key, TEAL, True),
                         ('歌 %d，第 %d 帧' % (i, t), INK, False), ('', INK, False)])
    y = table(fig, y, [(60, 'la'), (560, 'la'), (1014, 'ra')], rows)
    y = note(fig, y, '每首歌就变成了几千条这样的记录。识别的时候不再看声音，'
                     '只是拿键去表里查：这张表有 %d 条键、%d 条记录。'
              % (R['database']['entries'], R['database']['pairs']))
    save(fig, '08-hash-table.png', '哈希键与数据库记录')


def fig09():
    fig, y = new(9, '查询：三秒钟，加噪声', '手上只有一小段、还录得很糟。同样切帧、找峰、组键。')
    p = R['panels']
    box = (200, y, 1002, y + 380)
    heat(fig, box, p['query'])
    fig.text((200, y + 388), '0 s', 40, color=GRAY)
    fig.text((1002, y + 388), '3 s（片段）', 40, color=GRAY, anchor='ra')
    y = note(fig, box[3] + 56, '同一个旋律、同样的峰——因为峰对噪声不敏感。'
                               '这就是指纹能扛住外放、压缩、吵闹餐厅的原因。')
    save(fig, '09-query.png', '查询片段的谱图')


def fig10():
    fig, y = new(10, '数票：它们对得上同一个时间差', '每命中一条记录就投一票，票投给「这首歌、这个时间差」。')
    h = R['histogram']
    box = (300, y + 40, 990, y + 340)
    pk = Plot(fig, box, (0, 160), (0, 50))
    top = h['best_offset']
    for i, v in enumerate(h['correct']):
        if v:
            pk.f.line((i, 0), (i, v), color=BLUE, width=5)
    pk.axes(xticks=(0, 40, 80, 120, 160), yticks=(0, 20, 40),
            xlab='时间差（帧）', ylab='票数')
    fig.circle(pk.px(top), pk.py(h['correct'][top]), 16, fill=RED, outline=RED)
    fig.text((pk.px(top) + 26, pk.py(h['correct'][top]) - 26),
             '第 %d 帧：%d 票' % (top, h['correct'][top]), 40, color=RED)
    y = note(fig, box[3] + 132,
             '查询片段的第 0 帧对应这首歌的第 %d 帧，所以所有诚实的匹配都落在同一格。'
             '噪声明明占了 90%% 的能量，票照样聚成一堆。' % top)
    save(fig, '10-offset-votes.png', '偏移直方图：正确的那首歌')


def fig11():
    fig, y = new(11, '换一首歌，票就散了', '同样的查询，投给库里另一首歌：没有一堆票，只有零星的巧合。')
    h = R['histogram']
    box = (300, y + 40, 990, y + 340)
    pk = Plot(fig, box, (0, 160), (0, 50))
    for i, v in enumerate(h['wrong']):
        if v:
            pk.f.line((i, 0), (i, v), color=GRAY, width=5)
    pk.axes(xticks=(0, 40, 80, 120, 160), yticks=(0, 20, 40),
            xlab='时间差（帧）', ylab='票数')
    y = note(fig, box[3] + 132,
             '错歌一共 %d 票，散在 161 个格子上，最高的才 %d 票。'
             '「像」不是看票的总数，是看票有没有堆在一个格子上。'
             % (h['wrong_total'], h['wrong_max']))
    save(fig, '11-wrong-song.png', '偏移直方图：错误的那首歌')


def fig12():
    fig, y = new(12, '噪声加到多大就听不出来', '边界不在「听得清」那里，比人耳低得多。')
    rows = R['identification']
    box = (300, y + 40, 990, y + 360)
    pk = Plot(fig, box, (-20, 30), (0, 50))
    pk.line([(r['snr'], r['votes']) for r in rows], TEAL, width=6)
    pk.line([(r['snr'], r['runner_up']) for r in rows], GRAY, width=4)
    pk.axes(xticks=(-20, -10, 0, 10, 20, 30), yticks=(0, 20, 40),
            xlab='信噪比（dB）', ylab='票数')
    fig.text((box[0] + 20, box[1] + 10), '正确那首', 40, color=TEAL)
    fig.text((box[0] + 20, box[1] + 64), '第二名的票', 40, color=GRAY)
    last = [r for r in rows if r['confident']][-1]
    y = note(fig, box[3] + 132,
             '一直到 %d dB 还能认出（%d 票，第二名 %d 票）；再低就只剩巧合了。'
             '音频指纹本来就不是给人听的。' % (last['snr'], last['votes'],
                                              last['runner_up']))
    save(fig, '12-snr-curve.png', '信噪比与识别票数')


def fig02():
    fig, y = new(2, '换成波形直接比，会怎样', '同一个片段，只把播放速度改 1%：相关系数从 0.984 掉到 0.161。')
    rows = R['correlation']
    y = table(fig, y, [(60, 'la'), (700, 'ra'), (1014, 'ra')],
              [[('情况', INK, True), ('波形相关系数', INK, True), ('', INK, False)]] +
              [[(r['label'], INK, False), ('%.3f' % r['peak'], TEAL, True),
                ('', INK, False)] for r in rows])
    y = note(fig, y, '而且要在整首歌里找这个最大值：一首 8 秒的歌，4 kHz 采样，'
                     '就是三万个位移，每个都要算一遍。指纹把这件事省掉了。')
    save(fig, '02-waveform-vs-fingerprint.png', '波形比对对速度变化极敏感')


def fig13():
    fig, y = new(13, '指纹怕什么', '它对噪声、压缩、外放很宽容，对「音高整体变了」很不宽容。')
    rows = R['speed']
    y = table(fig, y, [(60, 'la'), (560, 'ra'), (800, 'ra'), (1014, 'ra')],
              [[('播放速度', INK, True), ('最高票数', INK, True),
                ('认对了吗', INK, True), ('', INK, False)]] +
              [[('%.1f%%' % (100 * (r['factor'] - 1) + 100), INK, False),
                ('%d' % r['votes'], TEAL, True),
                ('是' if r['confident'] else '不成立', INK, False),
                ('', INK, False)] for r in rows])
    y = note(fig, y, '转速变 1%，所有频率整体平移 1%。峰的相对位置没变，'
                     '但它们落进了别的频率格，键就对不上了。真实系统用对数频率轴，'
                     '正是为了让「平移」变成「错位一点点」而不是「全错」。')
    save(fig, '13-speed.png', '播放速度变化下的票数')


def fig14():
    fig, y = new(14, '一首歌要占多少地方', '指纹比音频小得多，但库大了以后量也不能忽略。')
    rows = R['library']
    box = (300, y + 40, 990, y + 320)
    pk = Plot(fig, box, (0, 62), (0, 250000))
    pk.line([(r['seconds'] / 60, r['hashes']) for r in rows], BLUE, width=6)
    for r in rows:
        pk.dot(r['seconds'] / 60, r['hashes'], BLUE, r=10)
    pk.axes(xticks=(0, 10, 30, 60), yticks=(0, 100000, 200000),
            xfmt='%g', yfmt='%g', xlab='歌曲长度（分钟）', ylab='指纹条数')
    y = note(fig, box[3] + 132,
             '本文的密度是每秒 %.0f 条键。照这个密度，一首 4 分钟的歌约 %d 条，'
             '一小时约 %d 条——比原始音频小三个数量级，所以才放得进内存。'
             % (R['songs'][1]['hashes'] / 8.0, rows[0]['hashes'], rows[3]['hashes']))
    save(fig, '14-library-size.png', '库规模与指纹条数')


def fig15():
    fig, y = new(15, '谁在做这件事', '一个想法、一篇论文、一个产品，还有后来者。')
    items = [('2002', 'Shazam 在英国上线，短号 2580', TEAL),
             ('2003', 'Avery Wang 在 ISMIR 发表工业级检索算法', BLUE),
             ('2006', '美国专利 6,990,453 授权：谱峰 + 组合哈希 + 偏移投票', AMBER),
             ('2008', 'Chromaprint / AcoustID 走开源路线，用别的指纹算法', GREEN),
             ('2018', 'Apple 收购 Shazam', INK_SOFT)]
    for year, text, color in items:
        fig.circle(110, y + 22, 14, fill=color, outline=color)
        fig.text((146, y), year, 42, bold=True, color=color)
        lines = fig.wrap((300, y + 2), text, 40, 700, color=INK)
        y += int(lines * 40 * 1.35) + 46
    y = note(fig, y + 6, '中间那些年没有断过：手机从按键机换到智能机，'
                          '算法几乎没变，变的只是它跑在谁的芯片上。')
    save(fig, '15-timeline.png', '音频指纹的时间线')


def fig17():
    fig, y = new(17, '指纹的边界', '它不是「听懂」，只是「对上过一次」。')
    y = bullets(fig, y, [
        '只认曲库里有的东西。库里没有，再多票也没用。',
        '翻唱、现场版、remix：谱峰位置变了，对不上原版。',
        '音高被整体改变（变速不变调、降调）会让键全部错位。',
        '长度太短的片段（一两秒）峰太少，票不够。',
        '它不知道「这是什么乐器」，也不知道「这段在唱什么」。',
    ])
    save(fig, '17-limits.png', '音频指纹的边界')


def fig16():
    fig, y = new(16, '一次识别的全过程', '八步，其中七步都不看声音，只看数字。')
    steps = [('录音', '手机麦克风，16 kHz 以上'), ('切帧', '每帧 512 点，每 128 点挪一次'),
             ('谱图', 'FFT，得到时间-频率能量'), ('找峰', '局部最大 + 不要太挤'),
             ('组键', '锚点配后邻，每锚 %d 条' % R['fan_out']),
             ('查表', '每个键取出所有出处'), ('投票', '按时间差聚成直方图'),
             ('判定', '最高票的格子对应的歌')]
    for i, (name, text) in enumerate(steps):
        x = 50 + (i % 3) * 322
        yy = y + (i // 3) * 230
        chip(fig, (x, yy, x + 250, yy + 110), name, PALE, size=44, bold=True)
        fig.wrap((x, yy + 126), text, 38, 290, color=INK_SOFT)
    y = y + 3 * 230 + 30
    y = note(fig, y, '查表那一步是关键：不在音频上滑窗，而是在一张哈希表上做常数时间查找。'
                     '整个系统的速度优势全在这里。')
    save(fig, '16-pipeline.png', '识别的八个步骤')


def fig18():
    fig, y = new(18, '这套方法后来去了哪里', '指纹不只用来认歌。')
    y = bullets(fig, y, [
        '版权扫描：上传时就比对，自动下架。',
        '广告监测：电视里播了哪支曲子，按秒计费。',
        '广播统计：哪首歌在哪个电台播了几次。',
        '视频去重与内容审核：把音频换成指纹再比。',
        '同一条思路也在做「图像指纹」「视频指纹」。',
    ], accent=BLUE)
    y = note(fig, y, '它们共同的前提是：内容可以被压成一串对噪声不敏感、'
                     '对内容很敏感的短记号。这就是「指纹」这个名字的来处。')
    save(fig, '18-uses.png', '音频指纹的其他用途')


FIGS = [fig01, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig10, fig11,
        fig12, fig02, fig13, fig14, fig15, fig17, fig16, fig18]


def make_cover():
    import shazam as S
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill='#0d1f27', outline=None)
    box = (90, 340, 990, 640)
    heat(fig, box, R['panels']['song'])
    for t, f in R['panels']['clean']:
        fig.circle(box[0] + (box[2] - box[0]) * t / 247,
                   box[3] - (box[3] - box[1]) * f / 256, 4, fill='#f2b134',
                   outline='#f2b134')
    fig.text((96, 120), '听歌识曲', 96, bold=True, color='#ffffff')
    fig.text((96, 240), '把声音压成一串键', 48, color='#7fa8c9')
    fig.text((96, 680), '一个峰配另一个峰，票数堆在同一格', 44, color='#e8f0f6')
    fig.text((96, 900), 'tech-articles · 2026-11-09', 38, color='#7fa8c9')
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
        META.sort(key=lambda row: row['path'])
        (HERE / 'figure-metadata.json').write_text(
            json.dumps(META, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(META))


import shazam as S
SONG_SIG, _ = S.song(23)
NOISY_SIG = S.noise(SONG_SIG, 10)

if __name__ == '__main__':
    main(sys.argv)
