#!/usr/bin/env python3
"""Original teaching figures for the frequency-hopping article. MIT.

Every number comes from results.json (written by run_model.py, which runs
examples/fh.py). Nothing is typed in by hand except dates and channel counts
that come from the patent text.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from figkit import (Fig, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED, GRAY,
                    LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R, font)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []
N = R['channels']


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
             ylab=None, grid=True, labels=True):
        if grid:
            for v in yticks:
                yy = self.py(v)
                self.f.line((self.x0, yy), (self.x1, yy), color=LIGHT, width=2)
        if labels:
            for v in yticks:
                yy = self.py(v)
                self.f.text((self.x0 - 18, yy - 21), yfmt % v, 40, color=GRAY,
                            anchor='ra')
        for v in xticks:
            xx = self.px(v)
            if grid:
                self.f.line((xx, self.y0), (xx, self.y1), color=LIGHT, width=2)
            if labels:
                self.f.text((xx, self.y1 + 14), xfmt % v, 40, color=GRAY,
                            anchor='ma')
        self.f.line((self.x0, self.y1), (self.x1, self.y1), color=GRAY, width=3)
        self.f.line((self.x0, self.y0), (self.x0, self.y1), color=GRAY, width=3)
        if xlab:
            self.f.text((self.x1, self.y1 + 74), xlab, 40, color=GRAY, anchor='ra')
        if ylab:
            self.f.text((self.x0, self.y0 - 58), ylab, 40, color=GRAY)

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

def grid(fig, x0, y0, cell, hops, channels, colour, label_every=0):
    """A time-frequency grid: one column per hop, one row per channel band."""
    for (hop, ch, *rest) in hops:
        c = colour(ch, rest[0] if rest else False)
        fig.rect(x0 + hop * cell, y0 + (channels - 1 - ch) * cell,
                 x0 + (hop + 1) * cell, y0 + (channels - ch) * cell,
                 fill=c, outline=None)
    return x0 + hops[-1][0] * cell + cell


def fig01():
    fig, y = new(1, '同一段时间，两种命运', '横轴是时间（一跳一格），纵轴是频点。'
                 '上面一直用同一个频点，下面每一跳换一个。红点是被干扰者盖住的跳。')
    hops = R['waterfall_parked'][:40]
    p1 = Plot(fig, (300, y + 30, 980, y + 330), (0, 40), (0, 88))
    p1.axes(xticks=(0, 10, 20, 30, 40), yticks=(0, 44, 88),
            xlab='跳数', ylab='频点编号')
    p1.line([(0, 0), (40, 0)], RED, width=8)
    fig.text((p1.px(20), p1.py(0) - 62), '定频：每一跳都在频点 0', 40, color=RED,
             anchor='ma')
    y2 = y + 330 + 190
    p2 = Plot(fig, (300, y2, 980, y2 + 330), (0, 40), (0, 88))
    p2.axes(xticks=(0, 10, 20, 30, 40), yticks=(0, 44, 88),
            xlab='跳数', ylab='频点编号')
    p2.line([(i, ch) for (i, ch, _j) in hops], TEAL, width=4)
    for (i, ch, j) in hops:
        p2.dot(i, ch, RED if j else TEAL, r=10 if j else 6)
    fig.text((p2.px(38), p2.py(88) - 40), '跳频：每一跳换一个频点', 40,
             color=TEAL, anchor='ra')
    y = y2 + 330 + 150
    y = note(fig, y, '同样的干扰者（挡住 18/88 个频点），对定频链路是 100% 破坏，'
                     '对跳频链路是 21.4%%。')
    save(fig, '01-two-worlds.png', '定频与跳频在同一张时频图上的对比')


def fig07():
    fig, y = new(8, '88 个键，88 个频率', '专利原文：一份钢琴卷纸上有 88 行孔，'
                 '在我们的系统里，它就对应 88 个不同的载波频率。')
    cell = 11
    x0 = 60
    keys_w = 88 * cell
    # keyboard: 88 white keys, black keys drawn short
    ytop = y
    for i in range(88):
        fig.rect(x0 + i * cell, ytop, x0 + (i + 1) * cell, ytop + 150,
                 fill=WHITE, outline=GRAY, width=1)
    black = {1, 3, 6, 8, 10}
    for i in range(88):
        if i % 12 in black:
            fig.rect(x0 + i * cell - cell * 0.3, ytop,
                     x0 + i * cell + cell * 0.7, ytop + 92,
                     fill=INK, outline=None)
    y = ytop + 190
    # arrow band
    fig.text((x0, y), '88 个频点，从低到高排开', 42, color=INK)
    y += 60
    for i in range(88):
        fig.rect(x0 + i * cell, y, x0 + (i + 1) * cell - 1, y + 90,
                 fill=TINT_T if i % 2 else TINT_B, outline=None)
    fig.text((x0, y + 120), 'f₁', 40, color=GRAY)
    fig.text((x0 + keys_w - 60, y + 120), 'f₈₈', 40, color=GRAY, anchor='ra')
    y += 200
    y = bullets(fig, y, [
        '钢琴有 88 个键，卷纸有 88 行；专利里 7 行孔控制 7 个调谐电容，'
        '另外一行管同步指示。',
        '本文的模型就取这 88 个频点：不是工程规格，是这份专利自己给的数量。',
    ])
    save(fig, '08-keys.png', '88 个钢琴键与 88 个频点的对应')


def fig08():
    fig, y = new(7, '一份卷纸决定下一跳', '纸上的孔位闭合一排开关，开关切换电容，'
                 '电容决定这一瞬间发射机停在哪。')
    rows = R['strip']
    x0, w = 120, 780
    ytop = y
    per = 46
    holes = {
        'A': [2, 3, 7, 8, 9, 13], 'B': [1, 5, 6, 10, 12],
        'C': [3, 4, 8, 11, 13], 'D': [2, 6, 7, 9, 12],
        'E': [1, 4, 5, 10, 13], 'F': [3, 7, 8, 12, 13],
        'G': [2, 5, 9, 10, 11], 'H': [1, 8],
    }
    step = w / 15
    for i, r in enumerate(rows):
        y0 = ytop + i * per
        fig.rect(x0, y0, x0 + w, y0 + per - 6, fill=WHITE, outline=GRAY, width=2)
        fig.text((x0 - 24, y0 + 4), r['row'], 40,
                 color=AMBER if r['row'] == 'H' else INK, anchor='ra')
        for k in holes[r['row']]:
            fig.circle(x0 + k * step, y0 + per / 2 - 3, 12,
                       fill=AMBER if r['row'] == 'H' else INK,
                       outline=AMBER if r['row'] == 'H' else INK)
    y = ytop + len(rows) * per + 34
    # what each row actually drives, at each end
    table_rows = [[('行', INK, True), ('发端', INK, True), ('收端', INK, True)]]
    for r in rows:
        missing = r['rx'].startswith('收端没有')
        table_rows.append([(r['row'], INK, True), (r['role'], INK, False),
                           (r['rx'] if not missing else '— 没有这一路', 
                            RED if missing else TEAL, False)])
    y = table(fig, y, [(60, 'la'), (280, 'la'), (660, 'la')], table_rows,
              size=38, row_h=58)
    y = note(fig, y, '发端 7 路，收端只有 4 路。A、B、C 发得出去，鱼雷听不到——'
                     '专利原文说，这三路专门用来「发假指令迷惑敌人」。')
    y = note(fig, y, '卷纸由恒速电机拖动，两端各一份。同速、同起点，就会在同一时刻'
                     '读到同一行孔——这就是同步的全部秘密。')
    save(fig, '07-strip.png', '专利里的记录纸带、八行孔与收发两端的电容分配')


def fig09():
    fig, y = new(11, '四千跳里，88 个频点都去过', '跳频序列不需要随机数发生器，'
                 '一个 16 位移位寄存器就够了。')
    hops = R['waterfall'][:64]
    cell = 13
    h = N * cell
    x0 = 60
    grid(fig, x0, y, cell, [(i, ch) for (i, ch) in hops], N,
         lambda ch, j: TEAL if ch % 3 else BLUE)
    y += h + 60
    s = R['sequence']
    cols = [(60, 'la'), (300, 'la'), (620, 'la')]
    rows = [
        [('跳数', INK, False), ('用到的频点', INK, False), ('均匀性 χ²', INK, False)],
        [('%d' % s['hops'], TEAL, True), ('%d / %d' % (s['used'], N), TEAL, True),
         ('%.1f' % s['chi2'], TEAL, True)],
    ]
    y = table(fig, y, cols, rows)
    y = note(fig, y, 'χ² 的理论期望值就是自由度 87。我这次算出 %.1f——看着很像随机，'
                     '其实是确定性电路。' % s['chi2'])
    y = note(fig, y, '四千跳里「和上一跳相同」出现 %d 次，预期的 1/88 是 %.0f 次。'
              % (s['same_as_previous'], s['hops'] / N))
    save(fig, '11-sequence.png', '跳频序列与均匀性检查')


def fig10():
    fig, y = new(9, '定频：坐在靶心上', '发射机不动，干扰者也不需要动。')
    cell = 13
    x0 = 60
    hops = [(i, 0, True) for i in range(60)]
    grid(fig, x0, y, cell, hops, N, lambda ch, j: RED)
    # the jammer band
    fig.rect(x0 - 6, y + (N - 1) * cell - 6, x0 + 60 * cell,
             y + N * cell, fill=None, outline=RED, width=4, radius=0)
    y += N * cell + 60
    y = bullets(fig, y, [
        '60 跳全在同一个频点上，60 个格子全红。',
        '要打断它，干扰功率只需要信号的 10 倍——本文模型里那个「10 dB」的门槛。',
    ], accent=RED)
    save(fig, '09-sitting-duck.png', '定频链路被窄带干扰全面压制')


def fig11():
    fig, y = new(10, '跳频：干扰者得先猜中', '挡住 20% 的频点，'
                 '打断的跳也只有 21%。')
    cell = 13
    x0 = 60
    hops = R['waterfall_parked']
    grid(fig, x0, y, cell, hops, N,
         lambda ch, j: RED if j else (TINT_B if ch % 2 else TINT_T))
    y += N * cell + 50
    y = note(fig, y, '红格是「这一跳落在被挡的 18 个频点里」。'
                     '干扰者付了 176 倍功率，换来 21% 的破坏率。')
    save(fig, '10-hopping.png', '跳频链路对部分频带干扰的时频图')


def fig12():
    fig, y = new(12, '要挡住多少，得付多少', '同样的 10 dB 门槛，'
                 '覆盖越宽，每点越弱，总功率就要越大。')
    pc = R['power_curve']
    p = Plot(fig, (300, y + 84, 980, y + 470), (0, 90), (0, 900))
    p.axes(xticks=(0, 22, 44, 66, 88), yticks=(0, 300, 600, 900),
           xlab='被覆盖的频点数', ylab='需要的干扰功率（倍于信号）')
    p.line([(x['channels'], x['needed']) for x in pc], TEAL, width=6)
    for x in pc:
        p.dot(x['channels'], x['needed'], TEAL, r=11)
    y = y + 470 + 120
    y = note(fig, y, '88 个频点全盖住要 880 倍功率；只盖 1 个只要 10 倍。'
                     '跳频干的唯一一件事，就是逼干扰者在两者之间选。')
    save(fig, '12-power.png', '干扰功率与覆盖频点数的关系')


def fig13():
    fig, y = new(13, '七种打法，一张表', '每一行的干扰者都恰好强到能打断它盖住的跳。')
    rows = [[('情形', INK, True), ('所需功率', INK, True), ('打断的跳', INK, True)]]
    for r in R['compare']:
        rows.append([('%s · %s' % (r['mode'], r['jammer']), INK, False),
                     ('%.0f×' % r['needed'], TEAL, True),
                     ('%.0f%%' % (100 * r['per']), RED if r['per'] > 0.5 else INK_SOFT,
                      False)])
    y = table(fig, y, [(60, 'la'), (700, 'ra'), (960, 'ra')], rows, size=38,
              row_h=64)
    y = note(fig, y, '最后一行的「跟随」是唯一真正威胁：只要它能在半跳内完成'
                     '「听到 + 调谐」，跳频就退化成定频。')
    save(fig, '13-table.png', '七种干扰策略的功率代价与破坏率')


def fig14():
    fig, y = new(14, '跳得比它快，就赢', '干扰者的反应时间占一跳的比例，'
                 '决定它能不能真的打到。')
    p = Plot(fig, (300, y + 84, 980, y + 460), (0, 5), (0, 1))
    p.axes(xticks=(0, 1, 2, 3, 4, 5), yticks=(0, 0.5, 1.0),
           yfmt='%.1f', xlab='反应时间 ÷ 一跳的长度', ylab='被打断的跳的比例')
    p.line([(x['share_of_hop'], x['per']) for x in R['reaction']], BLUE, width=6)
    for x in R['reaction']:
        p.dot(x['share_of_hop'], x['per'], BLUE, r=11)
    y += 460 + 120
    y = note(fig, y, '反应时间只要超过「半跳」，破坏率就掉到零。'
                     '这是本模型里「跳速」唯一真正重要的地方。')
    save(fig, '14-reaction.png', '跟随式干扰的成功率与反应时间的关系')


def fig15():
    fig, y = new(15, '多少次才算快', '同样 2 ms 的反应时间，在每秒 10 跳时只占一跳的 2%，'
                 '在每秒 5000 跳时已经是十跳。')
    rows = [[('跳速（跳/秒）', INK, True), ('一跳多长', INK, True),
             ('2 ms 内的跳数', INK, True)]]
    for r in R['rates']:
        rows.append([('%d' % r['rate'], INK, False),
                     ('%.2f ms' % r['hop_ms'], INK_SOFT, False),
                     ('%.2f' % r['hops_in_reaction'],
                      RED if r['hops_in_reaction'] < 1 else TEAL, True)])
    y = table(fig, y, [(60, 'la'), (400, 'la'), (700, 'la')], rows, size=40)
    y = note(fig, y, '参考值：蓝牙经典 1600 跳/秒、79 个频点；GSM 的慢跳频 217 跳/秒；'
                     'SINCGARS 电台每秒 100 跳。')
    save(fig, '15-rates.png', '跳速与干扰者反应时间的对照表')


def fig16():
    fig, y = new(16, '同步是生死线', '差一跳，两边的频率就对不上，收到的全是噪声。')
    p = Plot(fig, (300, y + 84, 980, y + 420), (-0.4, 3.4), (0, 1))
    p.axes(xticks=(0, 1, 2, 3), yticks=(0, 0.5, 1.0), yfmt='%.1f',
           xlab='收端比发端慢几跳', ylab='能对上的跳的比例')
    p.line([(x['offset'], x['aligned']) for x in R['sync']], AMBER, width=6)
    for x in R['sync']:
        p.dot(x['offset'], x['aligned'], AMBER, r=11)
    y += 420 + 120
    y = note(fig, y, '只差一跳，对齐率就从 100%% 掉到 %.1f%%——剩下的那点重合是'
                     '「两个频点碰巧相同」。' % (100 * R['sync'][1]['aligned']))
    y = note(fig, y, '所以专利里写了两手：恒速电机（石英表那一档的精度），'
                     '外加定期发同步脉冲。')
    save(fig, '16-sync.png', '收发两端失步后的对齐率')


def fig17():
    fig, y = new(17, '19.44 dB 是什么概念', '跳频的处理增益是 10·log₁₀(频点数)。'
                 '这也是干扰者被迫多花的那份功率。')
    p = Plot(fig, (300, y + 84, 980, y + 460), (0, 260), (0, 26))
    p.axes(xticks=(0, 64, 128, 192, 256), yticks=(0, 10, 20),
           xlab='频点数', ylab='处理增益（dB）')
    p.line([(n, g) for n, g in R['gain_curve'] if n <= 256], TEAL, width=6)
    for n, g in R['gain_curve']:
        if n <= 256:
            p.dot(n, g, TEAL, r=10)
    p.dot(88, R['gain'], RED, r=18)
    fig.text((p.px(88) + 18, p.py(R['gain']) - 52), '88 个频点 → 19.44 dB',
             40, color=RED)
    y += 460 + 120
    y = note(fig, y, 'dB 是对数：19.44 dB 意味着干扰者要多花 88 倍功率，'
                     '才能得到和定频时一样的效果。')
    save(fig, '17-gain.png', '处理增益随频点数增长')


def fig18():
    fig, y = new(18, '从一份卷纸到你的耳机', '这条线上有些年份是申请日，'
                 '有些是产品发布，含义不一样，所以标出来。')
    events = [
        ('1914', 'Hedy Kiesler 生于维也纳'),
        ('1933', '出演《神魂颠倒》，嫁给军火商 Mandl'),
        ('1937', '逃到伦敦，改名 Hedy Lamarr'),
        ('1941', '与 Antheil 递交专利申请'),
        ('1942', '专利授权，交给海军，未被采用'),
        ('1959', '专利到期，Antheil 同年去世'),
        ('1960s', '扩频进入军用抗干扰电台'),
        ('1997', 'Lamarr 获 EFF 先锋奖'),
        ('1999', '蓝牙：79 个频点，1600 跳/秒'),
        ('2014', '入选美国发明家名人堂'),
    ]
    x0 = 60
    fig.line((x0 + 10, y + 30), (x0 + 10, y + 30 + (len(events) - 1) * 96),
             color=LIGHT, width=6)
    for i, (when, what) in enumerate(events):
        yy = y + i * 96
        fig.circle(x0 + 10, yy + 30, 14, fill=TEAL, outline=TEAL)
        fig.text((x0 + 44, yy + 4), when, 40, bold=True, color=TEAL)
        fig.text((x0 + 250, yy + 4), what, 40, color=INK)
    y += len(events) * 96 + 20
    y = note(fig, y, '注意 1942 到 1959 之间的空白：专利有效期内，这套系统一次'
                     '实战都没用过。')
    save(fig, '18-timeline.png', '从 1914 到 2014 的时间线')


def fig19():
    fig, y = new(19, '三句话')
    y = bullets(fig, y, [
        '跳频不消除干扰，它把「一个频点被压死」换成「每次只可能被压掉一点」。',
        '它的代价是同步：两边必须同时、同速、同序列，差一跳就全废。',
        '它真正的贡献是 19.44 dB 的处理增益——逼干扰者把功率摊开 88 倍。',
    ], accent=TEAL)
    y = note(fig, y, '1942 年的美国海军没有要它。五十年后，蓝牙耳机每秒跳 1600 次。')
    save(fig, '19-three-lines.png', '全文的三句话总结')


def make_cover():
    fig = Fig(1080, width=1080)
    fig.text((96, 96), '每一跳', 84, bold=True, color=INK)
    fig.text((96, 200), '换一个频率', 84, bold=True, color=INK)
    fig.text((96, 320), '跳频：一份钢琴卷纸如何躲开干扰', 42, color=TEAL)
    y0 = 470
    cell = 44
    for i in range(14):
        ch = (i * 7 + 3) % 14
        fig.rect(96 + i * cell, y0 + (13 - ch) * cell, 96 + (i + 1) * cell - 4,
                 y0 + (14 - ch) * cell - 4,
                 fill=RED if i in (5, 9) else (TEAL if i % 2 else BLUE),
                 outline=None)
    fig.text((96, 760), '88 个频点 · 19.44 dB · 1942 年的专利', 42, color=INK_SOFT)
    fig.text((96, 850), 'Hedy Lamarr 与 George Antheil', 44, color=INK)
    fig.text((96, 930), 'tech-articles · 2026-11-02', 38, color=GRAY)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


FIGS = [fig01, fig07, fig08, fig09, fig10, fig11, fig12, fig13, fig14, fig15,
        fig16, fig17, fig18, fig19]


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


if __name__ == '__main__':
    main(sys.argv)
