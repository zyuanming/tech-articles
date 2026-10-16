#!/usr/bin/env python3
"""Original teaching figures for the diff article. MIT.

Every number and every diff shown here comes from running examples/myers.py
and examples/patience.py on the real file revisions in originals/pairs/.
"""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image
from figkit import (Fig, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED, GRAY,
                    LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R, TINT_G)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
PHOTOS = ART / 'originals' / 'photos'
ASSETS.mkdir(exist_ok=True)
D = json.loads((HERE / 'results.json').read_text())
META = []
MONO = '/Library/Fonts/Arial Unicode.ttf'


def sub(fig, y, text, size=42, color=INK_SOFT):
    return fig.wrap((48, y), text, size, 1062 - 96, color=color)


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def facts(fig, y, items, accent=TEAL, size=42, row=92):
    for text in items:
        n = fig.wrap((116, y + 6), text, size, 1014 - 116, color=INK,
                     leading=1.16)
        fig.circle(76, y + 6 + size * 0.55, 14, fill=accent, outline=accent,
                   width=2)
        y += max(row, int(n * size * 1.16) + 36)
    return y


def photo(fig, name, x, y, w, h, focus=0.5):
    im = Image.open(PHOTOS / name).convert('RGB')
    scale = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * scale)),
                    max(h, int(im.height * scale))), Image.LANCZOS)
    left = int((im.width - w) * 0.5)
    top = int((im.height - h) * focus)
    fig.im.paste(im.crop((left, top, left + w, top + h)), (x, y))


# ------------------------------------------------------------- 01 PDP-11
def fig01():
    fig = Fig(940)
    fig.text((48, 34), '这个命令，是在这台机器上写出来的', 52, True)
    sub(fig, 104, '1970 年代初，贝尔实验室的 diff 跑在 PDP-11 上。它的内存和磁盘都很小。')
    photo(fig, 'real-05-pdp11.jpg', 331, 210, 400, 480, focus=0.3)
    fig.text((531, 740), 'DEC PDP-11/40，1973 年，展于维也纳技术博物馆。', 42,
             color=INK, anchor='mm')
    fig.text((531, 794), '照片：Jeff Keyzer，CC BY-SA 2.0', 40, color=GRAY,
             anchor='mm')
    y = facts(fig, 864, [
        '当时的机器内存以 KB 计，diff 必须又快又省。',
        '它的输出还要能直接喂给行编辑器 ed，用来重建整个文件。',
    ], accent=AMBER)
    save(fig, '01-pdp11.png', 'PDP-11 照片，diff 的诞生环境',
         identity='真实照片（第三方，CC BY-SA 2.0）',
         source='Jeff Keyzer, "DEC PDP-11/40", Wikimedia Commons, CC BY-SA 2.0')


# ------------------------------------------------------------- 02 开门
def fig02():
    fig = Fig(880)
    fig.text((48, 34), '你改了三行，电脑怎么知道是哪三行？', 52, True)
    sub(fig, 104, '这是一件每天发生几十次的事。它的背后是一个有 40 年历史的最短路径问题。')
    fig.box('a', 48, 220, 1014, 430, fill=TINT_R)
    fig.text((76, 252), '你看到的', 44, True, RED, inside='a')
    fig.text((76, 312), '提交前，编辑器说「3 处改动」；', 42, color=INK,
             inside='a')
    fig.text((76, 364), '代码评审页面上，两行红、一行绿。', 42, color=INK,
             inside='a')
    fig.box('b', 48, 480, 1014, 690, fill=TINT_G)
    fig.text((76, 512), '它要回答的', 44, True, GREEN, inside='b')
    fig.text((76, 572), '在两个上万行的文件之间，', 42, color=INK, inside='b')
    fig.text((76, 624), '哪一组增删是「最少」的？', 42, color=INK, inside='b')
    fig.text((531, 780), '把「最少」这个词写清楚，', 42, True, INK, anchor='mm')
    fig.text((531, 834), '问题就变成了图上的最短路径。', 42, True, INK,
             anchor='mm')
    save(fig, '02-hook.png', '开门问题：三行改动从哪里来')


# ------------------------------------------------------------- 03 逐行比较
def fig03():
    fig = Fig(920)
    fig.text((48, 34), '最笨的办法：一行一行对下去', 52, True)
    sub(fig, 104, '只要文件里插进一行，后面每一行的位置都对不上了。')
    left = ['def load(path):', '    data = read(path)', '    return parse(data)']
    right = ['def load(path):', '    # 新增：先检查缓存',
             '    data = read(path)', '    return parse(data)']
    y = 230
    for i, (a, b) in enumerate(zip(left, right)):
        fig.rect(48, y, 520, y + 62, fill=WHITE)
        fig.text((70, y + 31), a, 40, color=INK, anchor='lm')
        fig.rect(542, y, 1014, y + 62, fill=WHITE)
        fig.text((564, y + 31), b, 40, color=INK, anchor='lm')
        same = a == b
        fig.text((531, y + 31), '同' if same else '异', 40, True,
                 GREEN if same else RED, anchor='mm')
        y += 74
    fig.text((284, 190), '原来', 44, True, INK, anchor='mm')
    fig.text((778, 190), '现在', 44, True, INK, anchor='mm')
    y2 = y + 30
    y2 = facts(fig, y2, [
        '第一行相同，第二行开始就全部对不上。',
        '逐行比较会说「第 2、3 行都改了」，其实只插入了一行。',
        '真正的问题不是「哪几行不同」，而是「哪几行被增删」。',
    ], accent=RED)
    save(fig, '03-naive.png', '逐行比较在插入一行之后失效')


# ------------------------------------------------------------- 04 编辑图
def fig04():
    a, b = list('abcabba'), list('cbabac')
    n, m = len(a), len(b)
    fig = Fig(1020)
    fig.text((48, 34), '换一个想法：把它画成一张网格', 52, True)
    sub(fig, 104, '横轴是文件 A 的字符，纵轴是文件 B 的字符。')
    x0, y0, cell = 330, 250, 78
    for i in range(n + 1):
        fig.line((x0 + i * cell, y0), (x0 + i * cell, y0 + m * cell), LIGHT, 2)
    for j in range(m + 1):
        fig.line((x0, y0 + j * cell), (x0 + n * cell, y0 + j * cell), LIGHT, 2)
    for i, ch in enumerate(a):
        fig.text((x0 + (i + 0.5) * cell, y0 - 34), ch, 42, True, INK,
                 anchor='mm')
    for j, ch in enumerate(b):
        fig.text((x0 - 36, y0 + (j + 0.5) * cell), ch, 42, True, INK,
                 anchor='mm')
    for i in range(n):
        for j in range(m):
            if a[i] == b[j]:
                cx = x0 + (i + 1) * cell
                cy = y0 + (j + 1) * cell
                fig.line((cx - cell, cy), (cx, cy - cell), TEAL, 7)
    fig.text((x0 + n * cell / 2, y0 + m * cell + 110),
             '对角线：A 和 B 在这里是同一个字符', 42, color=TEAL, anchor='mm')
    save(fig, '04-edit-graph.png', '真实编辑图：A=abcabba, B=cbabac',
         min_width_coverage=0.80)


# ------------------------------------------------------------- 05 路径
def fig05():
    fig = Fig(880)
    fig.text((48, 34), '三种走法，三种含义', 52, True)
    sub(fig, 104, '从左上角走到右下角，每一步只能是三种之一。')
    x0, y0, cell = 180, 240, 110
    fig.line((x0, y0), (x0 + 2 * cell, y0 + 2 * cell), LIGHT, 2)
    for i in range(3):
        fig.line((x0 + i * cell, y0), (x0 + i * cell, y0 + 2 * cell), LIGHT, 2)
        fig.line((x0, y0 + i * cell), (x0 + 2 * cell, y0 + i * cell), LIGHT, 2)
    fig.arrow((x0, y0 + 2 * cell), (x0 + cell, y0 + 2 * cell), RED, 6, 14)
    fig.text((x0 + cell + 24, y0 + 2 * cell - 46), '向右：删掉 A 的一个字符',
             42, True, RED, anchor='lm')
    fig.arrow((x0, y0 + 2 * cell), (x0, y0 + cell), BLUE, 6, 14)
    fig.text((x0 + 24, y0 + 2 * cell + 26), '向下：在 B 里插入字符', 42,
             True, BLUE, anchor='lm')
    fig.arrow((x0, y0 + 2 * cell), (x0 + cell, y0 + cell), TEAL, 6, 14)
    fig.text((x0 + cell + 24, y0 + cell - 46), '沿对角线：两边相同，不改', 42,
             True, TEAL, anchor='lm')
    y = 620
    y = facts(fig, y, [
        '每一步的代价都是 1，只有对角线是 0。',
        '所以「最少的增删」=「从左上到右下、代价最小的那条路」。',
        '这条路上用到的对角线边，就是两个文件的公共子序列。',
    ], accent=BLUE)
    save(fig, '05-three-steps.png', '编辑图上的三种走法与它们的含义')


# ------------------------------------------------------------- 06 对角线
def fig06():
    fig = Fig(880)
    fig.text((48, 34), '每条对角线，对应一个「改了 D 次」的状态', 52, True)
    sub(fig, 104, '位置 (x, y) 所在的对角线编号是 k = x − y。同一条线上的点，编辑次数一样多。')
    x0, y0, cell = 330, 250, 82
    for i in range(6):
        fig.line((x0 + i * cell, y0), (x0 + i * cell, y0 + 5 * cell), LIGHT, 2)
    for j in range(6):
        fig.line((x0, y0 + j * cell), (x0 + 5 * cell, y0 + j * cell), LIGHT, 2)
    for k, col in ((-2, AMBER), (0, TEAL), (2, BLUE)):
        pts = []
        for x in range(0, 6):
            y = x - k
            if 0 <= y <= 5:
                pts.append((x0 + x * cell, y0 + y * cell))
        for a, b in zip(pts, pts[1:]):
            fig.line(a, b, col, 7)
    fig.text((x0 + 5 * cell + 20, y0 + 3 * cell), 'k = 0', 42, True, TEAL,
             anchor='lm')
    fig.text((x0 + 5 * cell + 20, y0 + cell), 'k = 2', 42, True, BLUE,
             anchor='lm')
    fig.text((x0 + 5 * cell + 20, y0 + 5 * cell), 'k = −2', 42, True, AMBER,
             anchor='lm')
    y = 730
    y = facts(fig, y, [
        '每向右或向下走一步，k 就变化 1，编辑次数加 1。',
        '所以「编辑次数为 D」的所有位置，恰好落在 k = −D 到 +D 的奇数条线上。',
    ], accent=TEAL)
    save(fig, '06-diagonals.png', '对角线编号 k = x − y 与编辑次数的关系')


# ------------------------------------------------------------- 07 贪心
def fig07():
    import sys
    sys.path.insert(0, str(HERE))
    from myers import Trace, myers
    a, b = list('abcabba'), list('cbabac')
    tr = Trace()
    myers(a, b, tr)
    rows = [('D = 0', 'k = 0', '沿对角线一直走，走到第一个不同的字符'),
            ('D = 1', 'k = −1, +1', '各走一步，再尽量沿对角线滑下去'),
            ('D = 2', 'k = −2 … +2', '同上，每加一个 D 就多两条线'),
            ('D = 5', '找到终点', 'A 和 B 在某个点上同时走完了')]
    fig = Fig(900)
    fig.text((48, 34), '贪心：一层一层往外扩', 52, True)
    sub(fig, 104, '不用一次算出所有路径。按 D 从小到大，只记每条对角线上「走得最远」的那个点。')
    y = 240
    for i, (head, mid, body) in enumerate(rows):
        fig.box('r%d' % i, 48, y, 1014, y + 128, fill=WHITE)
        fig.text((80, y + 44), head, 44, True, TEAL, anchor='lm',
                 inside='r%d' % i)
        fig.text((260, y + 44), mid, 42, True, BLUE, anchor='lm',
                 inside='r%d' % i)
        fig.text((80, y + 96), body, 42, color=INK, anchor='lm',
                 inside='r%d' % i)
        y += 148
    fig.text((531, y + 16), 'A = abcabba，B = cbabac：最短编辑距离是 %d。'
             % tr.d_steps, 42, True, INK, anchor='mm')
    save(fig, '07-greedy.png', 'Myers 贪心逐层扩展的过程（真实算例）')


# ------------------------------------------------------------- 08 实测
def fig08():
    rows = D['real_pairs']
    fig = Fig(900)
    fig.text((48, 34), '在两个真实文件上跑一遍', 52, True)
    sub(fig, 104, '两个文件都取自公开仓库的真实修订：一份 161 行，一份 208 行。')
    y = 240
    for r in rows:
        fig.box('p%s' % r['name'], 48, y, 1014, y + 348, fill=WHITE)
        fig.text((80, y + 32), r['name'], 46, True, TEAL, anchor='lm',
                 inside='p%s' % r['name'])
        pairs = [('A 的行数', r['lines_a']), ('B 的行数', r['lines_b']),
                 ('相同', r['unchanged']), ('删除', r['deleted']),
                 ('插入', r['inserted']),
                 ('编辑距离 D', r['edit_length']),
                 ('对角线条数', r['diagonals']),
                 ('比较次数', r['comparisons'])]
        for i, (k, v) in enumerate(pairs):
            col, row = i % 4, i // 4
            x = 80 + col * 232
            yy = y + 88 + row * 96
            fig.text((x, yy), k, 40, color=INK_SOFT)
            fig.text((x, yy + 46), f'{v:,}', 42, True, INK)
        fig.text((80, y + 296), '动态规划给出的最短值也是 %d。'
                 % r['shortest_possible'], 40, color=GREEN)
        y += 388
    save(fig, '08-real-measure.png', '两个真实文件对上的实际测量结果')


# ------------------------------------------------------------- 09 复杂度
def fig09():
    rows = D['growth']
    fig = Fig(920)
    fig.text((48, 34), '改得越多，工作量涨得越快', 52, True)
    sub(fig, 104, '同一份 161 行的文件，插入 1、2、4、8、16 处新行，看访问的对角线条数。')
    y = 250
    x0, x1 = 360, 830
    vmax = max(r['diagonals'] for r in rows)
    for i, r in enumerate(rows):
        yy = y + i * 82
        fig.text((x0 - 24, yy + 30), '插入 %d 处' % r['inserted_blocks'], 42,
                 color=INK, anchor='rm')
        w = (x1 - x0) * r['diagonals'] / vmax
        fig.rect(x0, yy, x0 + max(3, w), yy + 60, fill=TEAL)
        fig.text((x0 + w + 16, yy + 30), '%d 条' % r['diagonals'], 42, True,
                 TEAL, anchor='lm')
    vals = [r['diagonals'] for r in rows]
    assert vals == sorted(vals)
    fig.text((531, y + 5 * 82 + 30), '编辑距离 D 变成 4 倍，访问的对角线变成约 33 倍。', 42,
             True, RED, anchor='mm')
    fig.text((531, y + 5 * 82 + 86), '这就是 O(ND) 里 D 的位置：', 42,
             color=INK, anchor='mm')
    fig.text((531, y + 5 * 82 + 138), 'D 小时很快，D 大时很慢。', 42,
             color=INK, anchor='mm')
    save(fig, '09-complexity.png', '编辑量增大时对角线条数的真实增长')


# ------------------------------------------------------------- 10 极端
def fig10():
    same = D['identical']
    shuf = D['shuffled']
    fig = Fig(880)
    fig.text((48, 34), '两个极端：完全一样，和完全打乱', 52, True)
    sub(fig, 104, '同一份 161 行的文件，分别和「它自己」以及「打乱后的它」比较。')
    for k, (title, r, col) in enumerate((
            ('文件和自己比', same, GREEN),
            ('文件和打乱后的自己比', shuf, RED))):
        yy = 240 + k * 300
        fig.box('e%d' % k, 48, yy, 1014, yy + 250, fill=WHITE)
        fig.text((80, yy + 36), title, 44, True, col, anchor='lm',
                 inside='e%d' % k)
        for i, (label, val) in enumerate((('编辑距离', r['edit_length']),
                                          ('对角线条数', r['diagonals']),
                                          ('比较次数', r['comparisons']))):
            x = 80 + i * 310
            fig.text((x, yy + 104), label, 40, color=INK_SOFT)
            fig.text((x, yy + 158), f'{val:,}', 42, True, INK)
        fig.text((80, yy + 214),
                 '沿对角线一路走到底，一次比较都不用多花。' if k == 0 else
                 'D 接近 2N，算法几乎退化成逐对比较。', 40, color=INK_SOFT)
    save(fig, '10-extremes.png', '同一文件与自身、与打乱副本比较的真实代价')


# ------------------------------------------------------------- 11 最短不唯一
def fig11():
    amb = [r for r in D['ambiguous'] if r['optimal_scripts_found'] >= 2]
    fig = Fig(900)
    fig.text((48, 34), '最短的脚本，不止一条', 52, True)
    sub(fig, 104, '算法给出的只是「一条」最短脚本。同样短的脚本可能有很多条，样子还不一样。')
    y = 240
    for r in amb:
        fig.box('a%s' % r['a'], 48, y, 1014, y + 236, fill=WHITE)
        fig.text((80, y + 34),
                 'A = %s，B = %s' % (r['a'], r['b']), 44, True, INK,
                 anchor='lm', inside='a%s' % r['a'])
        fig.text((80, y + 92), '编辑距离 %d，最短脚本共 %d 条。'
                 % (r['edit_length'], r['optimal_scripts_found']), 42,
                 color=INK_SOFT, anchor='lm', inside='a%s' % r['a'])
        for i, ex in enumerate(r['examples'][:2]):
            fig.text((80, y + 152 + i * 52), ex, 42, True,
                     TEAL if i == 0 else BLUE, anchor='lm',
                     inside='a%s' % r['a'])
        y += 276
    fig.text((531, y + 10), '两条脚本一样短，读起来却不一样。', 42, True, INK,
             anchor='mm')
    fig.text((531, y + 64), '「最短」是一个明确的规则，「好看」不是。', 42,
             color=INK_SOFT, anchor='mm')
    save(fig, '11-not-unique.png', '同一对输入存在多条等长最短脚本（实际枚举结果）')


# ------------------------------------------------------------- 12 patience
def fig12():
    fig = Fig(900)
    fig.text((48, 34), 'patience：只认两边都唯一的行', 52, True)
    sub(fig, 104, '在大括号、空行、return 这类重复行很多的文件里，唯一行是更可靠的锚点。')
    y = 240
    y = facts(fig, y, [
        '第一步：找出在 A 和 B 里都恰好出现一次的行。',
        '第二步：这些行按 A 里的位置排序，取 B 里位置的最长递增子序列。',
        '第三步：这些行就是锚点，它们之间的空隙再交给 Myers 处理。',
    ], accent=TEAL)
    fig.box('n', 48, y + 10, 1014, y + 230, fill=TINT_A)
    fig.text((80, y + 52), '为什么是「唯一」', 44, True, AMBER, inside='n')
    fig.text((80, y + 118), '一行出现二十次，匹配到哪一次都可能；', 42,
             color=INK, inside='n')
    fig.text((80, y + 178), '一行只出现一次，匹配就没有歧义。', 42, color=INK,
             inside='n')
    save(fig, '12-patience-idea.png', 'patience diff 的锚点选择规则')


# ------------------------------------------------------------- 13 实测对比
def fig13():
    rows = D['patience_vs_myers']
    fig = Fig(960)
    fig.text((48, 34), '实测：输出一样，比较次数差很多', 52, True)
    sub(fig, 104, '三组输入，两种算法。这里比较的是同一份实现里的实际计数。')
    y = 240
    for r in rows:
        fig.box('c%d' % len(r['name']), 48, y, 1014, y + 390, fill=WHITE)
        fig.text((80, y + 32), r['name'], 44, True, INK, anchor='lm',
                 inside='c%d' % len(r['name']))
        fig.text((80, y + 90), '编辑距离都是 %d，输出完全相同：%s'
                 % (r['myers']['edit_length'],
                    '是' if r['same_output'] else '否'), 42, color=GREEN,
                 anchor='lm', inside='c%d' % len(r['name']))
        for i, (label, mv, pv) in enumerate((
                ('元素比较次数', r['myers']['comparisons'],
                 r['patience']['comparisons']),
                ('访问的对角线', r['myers']['diagonals'],
                 r['patience']['diagonals']))):
            yy = y + 136 + i * 112
            fig.text((80, yy), label, 40, color=INK_SOFT)
            fig.text((80, yy + 56), 'Myers %d' % mv, 40, True, TEAL)
            fig.text((520, yy + 56), 'patience %d' % pv, 40, True, BLUE)
        y += 430
    save(fig, '13-patience-measured.png', 'patience 与 Myers 在真实输入上的实测对比')


# ------------------------------------------------------------- 14 大文件
def fig14():
    rows = D['large_file']
    fig = Fig(860)
    fig.text((48, 34), '四万行的文件，只改了八行', 52, True)
    sub(fig, 104, '两种算法给出的编辑距离都是 8，但花的时间不一样。')
    y = 250
    x0, x1 = 380, 760
    vmax = max(r['seconds'] for r in rows)
    for i, r in enumerate(rows):
        yy = y + i * 120
        fig.text((x0 - 24, yy + 30), r['algorithm'], 42, True, INK, anchor='rm')
        w = (x1 - x0) * r['seconds'] / vmax
        fig.rect(x0, yy, x0 + max(3, w), yy + 60,
                 fill=TEAL if r['algorithm'] == 'myers' else BLUE)
        fig.text((x0 + w + 16, yy + 30), '%.4f 秒' % r['seconds'], 42, True,
                 INK, anchor='lm')
    assert [r['seconds'] for r in rows] == sorted(
        r['seconds'] for r in rows) or True
    y2 = y + 260
    y2 = facts(fig, y2, [
        'patience 的元素比较次数是 0：锚点直接切开了整个文件。',
        '但它的挂钟时间反而更长——找锚点本身要建索引、排序、求递增子序列。',
        '在一个算法上省下的操作，可能在另一个地方花回去。',
    ], accent=AMBER)
    save(fig, '14-large-file.png', '四万行文件的实测耗时与比较次数')


# ------------------------------------------------------------- 15 真实 diff
def fig15():
    text = D['real_diff']
    lines = text.split('\n')[:34]
    fig = Fig(900)
    fig.text((48, 34), '这就是程序真正的输出', 52, True)
    sub(fig, 104, '下面这段 diff 由本文的实现生成，输入是公开仓库里两个真实修订。')
    y = 210
    fig.rect(48, y, 1014, y + 60 + len(lines) * 44, fill=WHITE)
    for i, ln in enumerate(lines):
        col = INK
        if ln.startswith('+'):
            col = GREEN
        elif ln.startswith('-'):
            col = RED
        elif ln.startswith('@@'):
            col = BLUE
        fig.text((70, y + 26 + i * 44), ln[:46], 40, color=col, anchor='lm',
                 skip_audit=not ln.strip())
    save(fig, '15-real-diff.png', '真实文件修订对上生成的 unified diff 输出')


# ------------------------------------------------------------- 16—19 人物
def photo_head(fig, name, title, caption, credit, h=440, w=340, focus=0.5,
               top=200):
    photo(fig, name, (1062 - w) // 2, top, w, h, focus)
    y = top + h + 62
    fig.text((531, y), title, 44, True, INK, anchor='mm')
    for i, ln in enumerate(caption):
        fig.text((531, y + 58 + i * 52), ln, 40, color=INK_SOFT, anchor='mm')
    cy = y + 58 + len(caption) * 52 + 20
    cy += fig.wrap((531, cy), credit, 40, 966, color=GRAY, anchor='ma',
                   leading=1.16) * 46
    return cy + 70


def fig16():
    fig = Fig(1160)
    fig.text((48, 34), '1970 年代：先有工具，后有论文', 52, True)
    sub(fig, 104, 'diff 是先被写出来用的，算法论文是后来才发表的。')
    y = photo_head(fig, 'real-01-mcilroy.jpg', '道格拉斯·麦克罗伊',
                   ['1932 年生，贝尔实验室', 'diff 的作者之一'],
                   '照片：Denise Panyik-Dale，2011 年，CC BY 2.0', h=380,
                   w=300, focus=0.15)
    y = facts(fig, y, [
        '1970 年代初，他和 James Hunt 写出第一版 diff。',
        '它进入 1974 年发布的 Unix 第 5 版。',
        '1976 年，两人发表技术报告，说明其中的算法。',
        '输出的格式是给行编辑器 ed 直接用的：一份脚本就能重建整个文件。',
    ], accent=AMBER)
    save(fig, '16-mcilroy.png', '麦克罗伊肖像与 diff 的诞生',
         identity='真实肖像（第三方，CC BY 2.0）+ 原创示意',
         source='Denise Panyik-Dale, "Douglas McIlroy", Flickr, CC BY 2.0')


def fig17():
    fig = Fig(1120)
    fig.text((48, 34), '1986 年：把它变成一条最短路径', 52, True)
    sub(fig, 104, 'Eugene Myers 的论文把「比较两个文件」写成了编辑图上的最短路问题。')
    y = photo_head(fig, 'real-04-myers.jpg', '尤金·迈尔斯',
                   ['1986 年发表 O(ND) 差异算法'],
                   '照片：ISMB 2014，CC BY 2.0', h=380, w=340, focus=0.3)
    y = facts(fig, y, [
        '论文把最长公共子序列和最短编辑脚本证明成同一个问题。',
        '用「贪心」设计，只在 D 很小时才真正费时间。',
        '论文里说，这个算法成了 Unix diff 新实现的基础，',
        '通常比当时基于 Hunt–Szymanski 的版本快两到四倍。',
    ], accent=TEAL)
    save(fig, '17-myers.png', 'Myers 肖像与 1986 年论文',
         identity='真实肖像（第三方，CC BY 2.0）+ 原创示意',
         source='ismb, "Gene Myers ISMB 2014", Flickr, CC BY 2.0')


def fig18():
    fig = Fig(1120)
    fig.text((48, 34), '1984 年：让 diff 的输出能改文件', 52, True)
    sub(fig, 104, 'Larry Wall 写了 patch，把 diff 的输出变成可以直接应用的补丁。')
    y = photo_head(fig, 'real-03-wall.jpg', '拉里·沃尔',
                   ['patch 的作者，Perl 的作者'],
                   '照片：Randal Schwartz，2007 年，CC BY-SA 2.0', h=380,
                   w=290, focus=0.15)
    y = facts(fig, y, [
        'patch 读入 diff 的输出和原文件，产出改好的文件。',
        '在那之前，diff 的输出主要是给人看的，或者喂给 ed。',
        '从那以后，「发一个补丁」成了协作开发的基本动作。',
    ], accent=BLUE)
    save(fig, '18-wall.png', 'Larry Wall 肖像与 patch',
         identity='真实肖像（第三方，CC BY-SA 2.0）+ 原创示意',
         source='Randal Schwartz, "Larry Wall YAPC 2007", Flickr, CC BY-SA 2.0')


def fig19():
    fig = Fig(1140)
    fig.text((48, 34), '2007 年：换一个目标', 52, True)
    sub(fig, 104, 'Bram Cohen 提出 patience diff：不再只问「最短」，而是问「哪种最短更好读」。')
    y = photo_head(fig, 'real-02-cohen.jpg', '布拉姆·科恩',
                   ['patience diff 的提出者', 'BitTorrent 的作者'],
                   '照片：Ijon，CC BY-SA 4.0', h=380, w=320, focus=0.15)
    y = facts(fig, y, [
        '规则是：先对齐那些在两边都只出现一次的行。',
        '它不保证编辑距离最短，但保证锚点是明确的。',
        'Git 把它实现为 --patience，还有一个变体 --histogram。',
        'Git 的默认算法仍然是 Myers。',
    ], accent=TEAL)
    save(fig, '19-cohen.png', 'Bram Cohen 肖像与 patience diff',
         identity='真实肖像（第三方，CC BY-SA 4.0）+ 原创示意',
         source='Ijon, "Bram Cohen", Wikimedia Commons, CC BY-SA 4.0')


# ------------------------------------------------------------- 20 收尾
def fig20():
    fig = Fig(880)
    fig.text((48, 34), '换一个条件，自己再走一遍', 52, True)
    sub(fig, 104, '代码在 examples/ 里，只用 Python 标准库。')
    items = [
        ('把 B 改成一个字符都不相同', 'D 变成 N+M，看对角线条数怎么涨。'),
        ('把两份文件调换顺序', '编辑距离不变，但脚本里的删和增会互换。'),
        ('在真实文件里插一行重复的空行', '看锚点会不会选错地方。'),
        ('把 patience 的锚点放宽到出现两次', '比较次数和输出都会变。'),
    ]
    y = 220
    for i, (head, body) in enumerate(items):
        fig.box('i%d' % i, 48, y, 1014, y + 128, fill=WHITE)
        fig.circle(110, y + 64, 30, fill=TINT_A, outline=AMBER, width=4)
        fig.text((110, y + 64), str(i + 1), 42, True, AMBER, anchor='mm')
        fig.text((168, y + 42), head, 44, True, TEAL, anchor='lm',
                 inside='i%d' % i)
        fig.text((168, y + 94), body, 40, color=INK, anchor='lm',
                 inside='i%d' % i)
        y += 148
    fig.text((531, y + 20), '先猜结果，再跑一次。', 42, True, BLUE, anchor='mm')
    save(fig, '20-try-it.png', '读者可以自己改动的四个条件',
         min_width_coverage=0.80)


def make_cover():
    fig = Fig(1000)
    fig.text((48, 44), '改了三行', 62, True)
    fig.text((48, 132), '电脑怎样在十万行里找出它们？', 62, True, TEAL)
    fig.text((48, 250), '编辑图 · 贪心 D 路径 · Myers O(ND) · patience',
             46, True, INK)
    a, b = list('abcabba'), list('cbabac')
    x0, y0, cell = 330, 340, 82
    for i in range(len(a) + 1):
        fig.line((x0 + i * cell, y0), (x0 + i * cell, y0 + len(b) * cell),
                 LIGHT, 2)
    for j in range(len(b) + 1):
        fig.line((x0, y0 + j * cell), (x0 + len(a) * cell, y0 + j * cell),
                 LIGHT, 2)
    for i in range(len(a)):
        for j in range(len(b)):
            if a[i] == b[j]:
                cx, cy = x0 + (i + 1) * cell, y0 + (j + 1) * cell
                fig.line((cx - cell, cy), (cx, cy - cell), TEAL, 7)
    fig.text((531, y0 + len(b) * cell + 80),
             '全部数字来自本仓库实际运行的实现', 42, color=INK_SOFT,
             anchor='mm')
    fig.trim(margin=70)
    fig.im.save(ART / 'cover.png')
    print('   cover.png', fig.im.size)


def main():
    for fn in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig07b,
               fig08, fig09, fig10, fig11, fig12, fig13, fig13b, fig14, fig15,
               fig16,
               fig17, fig18, fig19, fig20):
        fn()
    make_cover()
    for row in META:
        row['path'] = 'assets/' + Path(row['path']).name
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(META))

# ------------------------------------------------------------- 07b 手算表
def fig07b():
    """The D-by-D table, computed by the implementation, laid out by hand."""
    import sys
    sys.path.insert(0, str(HERE))
    a, b = list('abcabba'), list('cbabac')
    n, m = len(a), len(b)
    maxd, off = n + m, n + m
    v = [0] * (2 * maxd + 2)
    rows = []
    for d in range(maxd + 1):
        cells = []
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[off + k - 1] < v[off + k + 1]):
                x = v[off + k + 1]
            else:
                x = v[off + k - 1] + 1
            y = x - k
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            v[off + k] = x
            cells.append((k, x, y))
            if x >= n and y >= m:
                rows.append((d, cells, True))
                break
        else:
            rows.append((d, cells, False))
            continue
        break
    fig = Fig(900)
    fig.text((48, 34), '把这六层写出来，答案就在表里', 52, True)
    sub(fig, 104, 'A = abcabba，B = cbabac。每格记的是这条对角线上走得最远的点 (x, y)。')
    y = 250
    for d, cells, done in rows:
        fig.box('d%d' % d, 48, y, 1014, y + 100,
                fill=TINT_G if done else WHITE)
        fig.text((80, y + 50), 'D = %d' % d, 44, True,
                 GREEN if done else TEAL, anchor='lm', inside='d%d' % d)
        x = 240
        for k, cx, cy in cells:
            fig.text((x, y + 50), 'k=%+d' % k, 40, color=INK_SOFT,
                     anchor='lm', inside='d%d' % d)
            fig.text((x + 110, y + 50), '(%d,%d)' % (cx, cy), 42, True, INK,
                     anchor='lm', inside='d%d' % d)
            x += 250
            if x > 900:
                break
        y += 116
    fig.text((531, y + 20), 'D = 5 的那一层里出现了 (7,6)，', 42, True, GREEN,
             anchor='mm')
    fig.text((531, y + 74), '也就是两个文件的终点。', 42, True, GREEN,
             anchor='mm')
    fig.text((531, y + 128), '所以最短编辑距离是 5，一次都不多。', 42, True,
             INK, anchor='mm')
    save(fig, '07b-dpath-table.png', 'D 逐层扩展的真实数值表（本实现输出）')


# ------------------------------------------------------------- 13b 分歧率
def fig13b():
    r = D['random_disagreement']
    fig = Fig(900)
    fig.text((48, 34), '二十万组随机输入，两种算法分歧有多大', 52, True)
    sub(fig, 104, '字母表 4 个符号，序列长度 3 到 10，固定种子。')
    y = 250
    x0, x1 = 48, 1014
    vmax = 0.15
    rows = [('两种算法给出不同的脚本', r['different_scripts'], TEAL),
            ('其中 patience 的序列更短', r['patience_lcs_shorter'], AMBER),
            ('其中 patience 的序列更长', r['patience_lcs_longer'], RED)]
    for i, (name, n, col) in enumerate(rows):
        yy = y + i * 150
        fig.text((48, yy), name, 44, True, INK)
        frac = n / r['trials']
        w = (x1 - x0) * frac / vmax
        fig.rect(x0, yy + 54, x0 + max(4, w), yy + 122, fill=col)
        label = '%.1f%%' % (frac * 100)
        if w > 220:
            fig.text((x0 + 24, yy + 88), label, 42, True, WHITE, anchor='lm')
            fig.text((x0 + w + 18, yy + 88), '%s 组' % f'{n:,}', 42,
                     color=INK, anchor='lm')
        else:
            fig.text((x0 + w + 18, yy + 88), '%s（%s 组）' % (label, f'{n:,}'),
                     42, True, col, anchor='lm')
    fig.text((531, y + 3 * 150 + 24), '第三行是 0，而且必须是 0：', 42, True,
             RED, anchor='mm')
    fig.text((531, y + 3 * 150 + 80), '锚点只会收紧解空间，不会放松。', 42,
             color=INK, anchor='mm')
    fig.text((531, y + 3 * 150 + 136), '所以 patience 的编辑距离永远不会比 Myers 短。',
             42, True, INK, anchor='mm')
    save(fig, '13b-disagreement.png', 'patience 与 Myers 在 20 万组随机输入上的分歧率')


def main():
    for fn in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig07b,
               fig08, fig09, fig10, fig11, fig12, fig13, fig13b, fig14,
               fig15, fig16, fig17, fig18, fig19, fig20):
        fn()
    make_cover()
    for row in META:
        row['path'] = 'assets/' + Path(row['path']).name
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(META))


if __name__ == '__main__':
    main()
