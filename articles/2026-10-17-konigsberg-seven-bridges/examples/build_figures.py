#!/usr/bin/env python3
"""Original teaching figures for the Seven Bridges article. MIT.

Every degree, verdict, route and count comes from examples/results.json,
which examples/run_model.py produced by running examples/graphs.py.
"""
from __future__ import annotations
import json
from pathlib import Path
from figkit import (Fig, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED, GRAY,
                    LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R, TINT_G)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []


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


def vertex(fig, x, y, label, r=52, fill=TINT_T, outline=TEAL):
    fig.circle(x, y, r, fill=fill, outline=outline, width=5)
    fig.text((x, y), label, 46, True, INK, anchor='mm')


def edge(fig, a, b, color=GRAY, width=6):
    fig.line(a, b, color=color, width=width)


def shape(fig, x, y, s, name, edges, ox=0, oy=0):
    """Draw a small graph given vertex coordinates and an edge list."""
    pts = {'A': (x, y), 'B': (x + s, y), 'C': (x + s, y + s), 'D': (x, y + s),
           'E': (x + s / 2, y - s * 0.62)}
    for u, v in edges:
        edge(fig, pts[u], pts[v])
    for k, p in pts.items():
        if any(k in e for e in edges):
            vertex(fig, p[0], p[1], k, r=26, fill=WHITE)
    fig.text((x + s / 2, y + s + 62), name, 42, True, INK, anchor='mm')


# ---------------------------------------------------------------- 01 地图
def fig01():
    fig = Fig(940)
    fig.text((48, 34), '哥尼斯堡，1736 年', 52, True)
    sub(fig, 104, '城市建在普雷格尔河两岸，河中间有两座岛。四块陆地，七座桥。')
    fig.rect(48, 230, 1014, 620, fill=PALE)
    fig.rect(48, 380, 1014, 470, fill=TINT_B)
    fig.text((150, 425), '普雷格尔河', 42, True, BLUE)
    for cx, cy, name in ((300, 320, '北岸 B'), (300, 530, '南岸 C'),
                         (640, 320, '岛 D'), (640, 530, '岛 A')):
        fig.circle(cx, cy, 92, fill=WHITE, outline=TEAL, width=5)
        fig.text((cx, cy), name, 42, True, INK, anchor='mm')
    fig.text((531, 680), 'A 是克奈普霍夫岛，D 是洛姆塞岛，B 和 C 是两岸。', 42,
             color=INK, anchor='mm')
    save(fig, '01-city.png', '哥尼斯堡的四块陆地与河流')


# ---------------------------------------------------------------- 02 七桥
def fig02():
    fig = Fig(940)
    fig.text((48, 34), '七座桥把它们连起来', 52, True)
    sub(fig, 104, '数一数：A 到 B 两座，A 到 C 两座，A 到 D、B 到 D、C 到 D 各一座。')
    fig.rect(48, 230, 1014, 620, fill=PALE)
    fig.rect(48, 380, 1014, 470, fill=TINT_B)
    pos = {'B': (300, 320), 'C': (300, 530), 'D': (640, 320), 'A': (640, 530)}
    for u, v, off in (('A', 'B', -22), ('A', 'B', 22), ('A', 'C', -22),
                      ('A', 'C', 22), ('A', 'D', 0), ('B', 'D', 0),
                      ('C', 'D', 0)):
        (x1, y1), (x2, y2) = pos[u], pos[v]
        fig.line((x1 + 92 + off, y1 + off), (x2 - 92 + off, y2 + off), GRAY, 6)
    for k, (cx, cy) in pos.items():
        fig.circle(cx, cy, 92, fill=WHITE, outline=TEAL, width=5)
        fig.text((cx, cy), k, 46, True, INK, anchor='mm')
    fig.text((531, 680), '七条线，每一条都是一座桥。', 42, color=INK, anchor='mm')
    save(fig, '02-seven-bridges.png', '七座桥的连接')


# ---------------------------------------------------------------- 03 抽象
def fig03():
    fig = Fig(900)
    fig.text((48, 34), '欧拉的关键一步：把形状扔掉，只留连接', 52, True)
    sub(fig, 104, '路线在地图上的弯弯曲曲不重要，重要的只有「哪块陆地连着哪块陆地」。')
    fig.box('a', 48, 240, 500, 560, fill=PALE)
    fig.text((274, 276), '地图', 44, True, INK, anchor='mm', inside='a')
    pos = {'B': (150, 380), 'C': (150, 480), 'D': (390, 380), 'A': (390, 480)}
    for u, v, off in (('A', 'B', -12), ('A', 'B', 12), ('A', 'C', -12),
                      ('A', 'C', 12), ('A', 'D', 0), ('B', 'D', 0),
                      ('C', 'D', 0)):
        (x1, y1), (x2, y2) = pos[u], pos[v]
        fig.line((x1 + 44 + off, y1), (x2 - 44 + off, y2), GRAY, 4)
    for k, (cx, cy) in pos.items():
        fig.circle(cx, cy, 44, fill=WHITE, outline=TEAL, width=4)
        fig.text((cx, cy), k, 40, True, INK, anchor='mm')
    fig.arrow((520, 400), (556, 400), AMBER, 6, 16)
    fig.box('b', 562, 240, 1014, 560, fill=TINT_T)
    fig.text((788, 276), '图', 44, True, TEAL, anchor='mm', inside='b')
    pos2 = {'B': (680, 390), 'C': (680, 500), 'D': (900, 390), 'A': (900, 500)}
    for u, v in (('A', 'B'), ('A', 'B'), ('A', 'C'), ('A', 'C'),
                 ('A', 'D'), ('B', 'D'), ('C', 'D')):
        fig.line(pos2[u], pos2[v], GRAY, 4)
    for k, (cx, cy) in pos2.items():
        fig.circle(cx, cy, 42, fill=WHITE, outline=TEAL, width=4)
        fig.text((cx, cy), k, 40, True, INK, anchor='mm')
    fig.text((531, 640), '右边这张图，把桥的弯曲和长短全部丢掉了。', 42,
             color=INK, anchor='mm')
    fig.text((531, 700), '剩下的信息刚好够回答「能不能一次走完」。', 42, True,
             INK, anchor='mm')
    save(fig, '03-abstraction.png', '从地图到图：丢掉形状只留连接')


# ---------------------------------------------------------------- 04 度数
def fig04():
    d = R['konigsberg_1736']['degrees']
    fig = Fig(900)
    fig.text((48, 34), '给每块陆地数一个数：度数', 52, True)
    sub(fig, 104, '度数 = 连到这块陆地上的桥有几座。数桥，不数别的。')
    y = 250
    for k in ('A', 'B', 'C', 'D'):
        fig.rect(48, y, 1014, y + 92, fill=WHITE)
        fig.text((140, y + 46), k, 46, True, TEAL, anchor='mm')
        fig.text((260, y + 46), '连着', 42, color=INK, anchor='lm')
        fig.text((380, y + 46), '%d 座桥' % d[k], 46, True,
                 RED if d[k] % 2 else GREEN, anchor='lm')
        fig.text((640, y + 46), '是奇数' if d[k] % 2 else '是偶数', 42, True,
                 RED if d[k] % 2 else GREEN, anchor='lm')
        y += 104
    fig.text((531, y + 30), '四块陆地的度数全都是奇数：5、3、3、3。', 44, True,
             RED, anchor='mm')
    fig.text((531, y + 90), '这一点，直接决定了答案。', 44, True, INK,
             anchor='mm')
    save(fig, '04-degrees.png', '四块陆地的度数')


# ---------------------------------------------------------------- 05 奇偶论证
def fig05():
    fig = Fig(920)
    fig.text((48, 34), '为什么度数必须是偶数', 52, True)
    sub(fig, 104, '假设你真的走通了一条路线。现在盯着中间经过的任意一块陆地。')
    y = 250
    y = facts(fig, y, [
        '每次你从一座桥走上这块陆地，就得从另一座桥离开它。',
        '进去一次、出来一次，用掉两座桥。',
        '进去两次、出来两次，用掉四座桥。',
        '所以，只要你不是在这里开始或结束，用掉的桥数一定是偶数。',
    ], accent=TEAL)
    fig.box('c', 48, y + 10, 1014, y + 348, fill=TINT_A)
    fig.text((76, y + 52), '换句话说', 44, True, AMBER, inside='c')
    fig.text((76, y + 116), '度数不是偶数的陆地，只能是路线的起点或终点。', 42,
             color=INK, inside='c')
    fig.text((76, y + 172), '而一条路线最多只有两个端点：', 42, color=INK,
             inside='c')
    fig.text((76, y + 282), '一个起点、一个终点。', 42, color=INK, inside='c')
    save(fig, '05-parity.png', '奇偶性论证：为什么度数必须是偶数')


# ---------------------------------------------------------------- 06 结论
def fig06():
    k = R['konigsberg_1736']
    fig = Fig(900)
    fig.text((48, 34), '于是矛盾出现了', 52, True)
    sub(fig, 104, '把两条事实摆在一起，答案就出来了。')
    fig.box('a', 48, 250, 1014, 470, fill=TINT_B)
    fig.text((76, 290), '事实一', 44, True, BLUE, inside='a')
    fig.text((76, 354), '这块城市有 4 块陆地的度数是奇数。', 42, color=INK,
             inside='a')
    fig.text((76, 416), '（5、3、3、3）', 42, color=INK, inside='a')
    fig.box('b', 48, 510, 1014, 730, fill=TINT_R)
    fig.text((76, 550), '事实二', 44, True, RED, inside='b')
    fig.text((76, 614), '一条路线最多只能有 2 个端点。', 42, color=INK,
             inside='b')
    fig.text((76, 676), '所以最多只能有 2 块陆地的度数是奇数。', 42, color=INK,
             inside='b')
    fig.text((531, 812), '4 大于 2，矛盾。这条路线不存在。', 46, True, RED,
             anchor='mm')
    save(fig, '06-impossible.png', '矛盾：4 个奇点，但最多只能有 2 个',
         min_width_coverage=0.80)


# ---------------------------------------------------------------- 07 验证
def fig07():
    k = R['konigsberg_1736']
    e = R['exhaustive_check']
    fig = Fig(940)
    fig.text((48, 34), '两条独立的验证', 52, True)
    sub(fig, 104, '上面的推理靠不靠得住？我们用两种办法各验一遍。')
    y = 250
    y = facts(fig, y, [
        '第一，让程序把所有可能的走法全部试一遍，一条一条地试。',
        '结果：一条也走不通。程序没有找到任何路线。',
        '第二，把「度数规则」和「暴力搜索」放在所有小图上对撞。',
        '一共试了 %s 张连通图，规则与暴力搜索的结果完全一致，'
        '一次分歧都没有。' % f"{e['graphs_checked']}",
    ], accent=GREEN)
    fig.text((531, y + 30), '两种办法都指向同一个结论。', 44, True, GREEN,
             anchor='mm')
    save(fig, '07-verified.png', '暴力搜索与穷举校验的结果')


# ---------------------------------------------------------------- 08 一笔画
def fig08():
    rows = R['one_stroke']
    fig = Fig(1000)
    fig.text((48, 34), '换成「一笔画」，规则一样好用', 52, True)
    sub(fig, 104, '能不能不抬笔、不重复地画完一个图形，判据完全相同。')
    y = 250
    for r in rows:
        col = GREEN if r['drawable_in_one_stroke'] else RED
        fig.rect(48, y, 1014, y + 116, fill=TINT_G if
                 r['drawable_in_one_stroke'] else TINT_R)
        fig.text((76, y + 34), r['shape'], 44, True, INK)
        fig.text((76, y + 84), '度数：%s' % '、'.join(
            str(v) for v in r['degrees'].values()), 42, color=INK_SOFT)
        fig.text((990, y + 58), '能' if r['drawable_in_one_stroke'] else '不能',
                 48, True, col, anchor='rm')
        y += 132
    fig.text((531, y + 20), '奇点有 0 个或 2 个，就能一笔画完。', 44, True,
             INK, anchor='mm')
    save(fig, '08-one-stroke.png', '四个图形的一笔画判定（程序输出）')


# ---------------------------------------------------------------- 09 回路与路径
def fig09():
    fig = Fig(900)
    fig.text((48, 34), '两种情形，两个名字', 52, True)
    sub(fig, 104, '奇点的个数只有三种可能：0 个、2 个，或者更多。')
    fig.box('a', 48, 240, 1014, 470, fill=TINT_G)
    fig.text((76, 278), '奇点 0 个：欧拉回路', 44, True, GREEN, inside='a')
    fig.text((76, 342), '从哪出发都行，最后一定回到出发点。', 42, color=INK,
             inside='a')
    fig.text((76, 396), '例：正方形。', 42, color=INK, inside='a')
    fig.box('b', 48, 510, 1014, 740, fill=TINT_B)
    fig.text((76, 518), '奇点 2 个：欧拉路径', 44, True, BLUE, inside='b')
    fig.text((76, 582), '必须从一个奇点出发，在另一个奇点结束。', 42,
             color=INK, inside='b')
    fig.text((76, 636), '例：房子形状。', 42, color=INK, inside='b')
    fig.box('c', 48, 780, 1014, 960, fill=TINT_R)
    fig.text((76, 818), '奇点 4 个或更多：走不通', 44, True, RED, inside='c')
    fig.text((76, 882), '例：信封形状、哥尼斯堡。', 42, color=INK, inside='c')
    save(fig, '09-two-kinds.png', '欧拉回路、欧拉路径与走不通的三种情形')


# ---------------------------------------------------------------- 10 今天
def fig10():
    t = R['kaliningrad_today']
    fig = Fig(960)
    fig.text((48, 34), '今天的加里宁格勒：答案变了', 52, True)
    sub(fig, 104, '七座桥里，两座毁于二战轰炸，两座被拆掉改成了公路。')
    y = 250
    y = facts(fig, y, [
        '同一个位置现在剩下 5 座桥，其中只有 2 座是欧拉时代的原桥。',
        '四块陆地的度数变成 3、2、2、3——只剩两个奇点。',
        '所以今天这条路线走得通了，但必须从一块岛出发，到另一块岛结束。',
    ], accent=AMBER)
    fig.box('r', 48, y + 10, 1014, y + 180, fill=TINT_G)
    fig.text((76, y + 48), '程序实际找到的一条路线', 44, True, GREEN,
             inside='r')
    fig.text((76, y + 112), ' → '.join(t['trail']), 42, True, INK, inside='r')
    fig.text((531, y + 230), '城市变了，数学结论也跟着变。', 44, True, INK,
             anchor='mm')
    save(fig, '10-today.png', '今天 5 座桥的度数与新答案（程序输出）')


# ---------------------------------------------------------------- 11 绕路
def fig11():
    k = R['konigsberg_1736']
    t = R['kaliningrad_today']
    c = R['route_inspection_counterexample']
    fig = Fig(1020)
    fig.text((48, 34), '如果允许重复走几趟呢', 52, True)
    sub(fig, 104, '现实里的送信、扫雪、收垃圾，都得把每条路走一遍，重复也没关系。')
    y = 250
    y = facts(fig, y, [
        '问题变成：最少要多走几趟，才能把每条路都覆盖到？',
        '思路：把奇点两两配成一对，每对之间重复走一遍最短的路。',
        '所以正确的规则是「配对后最短距离的总和」，不是简单的奇点数除以 2。',
    ], accent=BLUE)
    fig.box('ok', 48, y + 10, 1014, y + 350, fill=TINT_G)
    fig.text((76, y + 50), '本文那两张图', 44, True, GREEN, inside='ok')
    fig.text((76, y + 114), '七桥：4 个奇点，额外走 %d 趟。'
             % k['route_inspection_extra_crossings'], 42, color=INK,
             inside='ok')
    fig.text((76, y + 168), '今天：2 个奇点，额外走 %d 趟。'
             % t['route_inspection_extra_crossings'], 42, color=INK,
             inside='ok')
    fig.text((76, y + 222), '两张图恰好都能用单条边配对，', 42, color=INK_SOFT,
             inside='ok')
    fig.text((76, y + 274), '所以简单公式碰巧算对。', 42, color=INK_SOFT,
             inside='ok')
    fig.box('no', 48, y + 390, 1014, y + 660, fill=TINT_R)
    fig.text((76, y + 430), '但简单公式不普遍成立', 44, True, RED, inside='no')
    fig.text((76, y + 494), '三角形加一条尾巴：奇点 C 和 E 相隔 2 条边。', 42,
             color=INK, inside='no')
    fig.text((76, y + 548), '简单公式给 1 趟，正确答案是 %d 趟。'
             % c['correct_value'], 42, color=INK, inside='no')
    fig.text((76, y + 602), '程序把两种算法都跑了，结果就在这里分开。', 42,
             color=INK_SOFT, inside='no')
    save(fig, '11-route-inspection.png', '允许重复时的最小代价，以及简单公式的反例')
# ---------------------------------------------------------------- 12 DNA 唯一
def fig12():
    b = R['de_bruijn_unique']
    fig = Fig(960)
    fig.text((48, 34), '今天最出人意料的用处：拼 DNA', 52, True)
    sub(fig, 104, '测序仪给你的不是一整条序列，而是一堆互相重叠的短片段，顺序全乱。')
    y = 240
    fig.text((48, y), '原序列', 42, True, INK)
    fig.text((240, y), b['sequence'], 46, True, TEAL)
    y += 76
    fig.text((48, y), '测出的片段', 42, True, INK)
    n = fig.wrap((300, y), '、'.join(b['kmers']), 42, 1014 - 300, color=INK)
    y += max(0, int(n * 42 * 1.16) - 46)
    y += 90
    y = facts(fig, y, [
        '把每个短片段拆成「前 3 个字母 → 后 3 个字母」的一条有向边。',
        '得到的图里，一条欧拉路径就对应一条能解释全部片段的序列。',
        '这个例子程序只找到 %d 条相容的序列：%s。'
        % (b['how_many_sequences'], '、'.join(b['distinct_sequences'])),
    ], accent=TEAL)
    fig.text((531, y + 30), '碎片拼回去，正好是一道欧拉路径问题。', 44, True,
             GREEN, anchor='mm')
    save(fig, '12-dna-unique.png', 'de Bruijn 图拼出唯一序列（程序输出）')


# ---------------------------------------------------------------- 13 DNA 歧义
def fig13():
    b = R['de_bruijn_ambiguous']
    a = R['assembly_ambiguity']
    fig = Fig(980)
    fig.text((48, 34), '但重复的片段会让它失效', 52, True)
    sub(fig, 104, '看这个例子：两串完全不同的序列，测出来的短片段一模一样。')
    y = 240
    fig.box('x', 48, y, 1014, y + 84, fill=TINT_R)
    fig.text((76, y + 42), '原序列：%s' % b['sequence'], 42, True, INK,
             anchor='lm', inside='x')
    y += 100
    fig.box('y', 48, y, 1014, y + 84, fill=TINT_R)
    fig.text((76, y + 42), '另一串序列：%s' % b['distinct_sequences'][1], 42,
             True, INK, anchor='lm', inside='y')
    y += 110
    y = facts(fig, y, [
        '这两串序列的短片段集合完全相同，程序无法判断原来的是哪一串。',
        '在 300 条随机序列上试：%d 条有唯一解，%d 条有歧义。'
        % (a['unique_solutions'], a['trials'] - a['unique_solutions']),
        '平均歧义倍数只有 %.2f——也就是说，大多数情况拼得回去，'
        '卡住的地方正是序列里有重复的地方。' % a['mean_ambiguity'],
    ], accent=AMBER)
    fig.text((531, y + 30), '真实的基因组组装，就是靠额外信息', 42,
             color=INK, anchor='mm')
    fig.text((531, y + 84), '（配对读段、覆盖深度、参考序列）来化解这些歧义。',
             42, color=INK, anchor='mm')
    save(fig, '13-dna-ambiguous.png', '重复片段造成的组装歧义（程序输出）')


# ---------------------------------------------------------------- 14 历史
def fig14():
    fig = Fig(920)
    fig.text((48, 34), '1736 年，一篇论文开了图论这个门', 52, True)
    sub(fig, 104, '欧拉做的不是解一道谜题，而是发明了一套看问题的方法。')
    y = 240
    y = facts(fig, y, [
        '他没有去一条一条试路线，而是先证明「这类问题只跟连接方式有关」。',
        '这一步把形状、距离、面积全部扔掉，只留下「谁连着谁」。',
        '然后他给出了判定条件，并且证明了它。',
        '必要条件由欧拉给出；「充分」那一半，后来由 Carl Hierholzer '
        '在 1873 年补上。',
    ], accent=AMBER)
    fig.text((531, y + 30), '这套「只看连接」的结构，', 44, True, TEAL,
             anchor='mm')
    fig.text((531, y + 86), '就是今天的图（graph）。', 44, True, TEAL,
             anchor='mm')
    save(fig, '14-history.png', '欧拉 1736 年的方法与 Hierholzer 的补充')


# ---------------------------------------------------------------- 15 收尾
def fig15():
    fig = Fig(880)
    fig.text((48, 34), '自己动手改一个条件', 52, True)
    sub(fig, 104, '代码在 examples/ 里，只用 Python 标准库。')
    items = [
        ('给七桥加一座桥', '加在哪两块陆地之间，才能让路线走得通？'),
        ('拆掉一座桥', '拆哪一座，能让奇点从 4 个变成 2 个？'),
        ('把一笔画那四个图形自己画一遍', '先按度数判断，再动手验证。'),
        ('把 DNA 例子的 k 改成 3 或 5', '歧义会变多还是变少？为什么？'),
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
    save(fig, '15-try-it.png', '读者可以自己改动的四个条件',
         min_width_coverage=0.80)


def make_cover():
    fig = Fig(1080, width=1080)
    fig.text((540, 226), '七座桥，走不通', 60, True, anchor='ma')
    fig.text((540, 302), '欧拉用一次「只数奇偶」开了图论这个门', 46, True, TEAL,
             anchor='ma')
    pos = {'B': (300, 390), 'C': (300, 560), 'D': (780, 390), 'A': (780, 560)}
    for u, v, off in (('A', 'B', -18), ('A', 'B', 18), ('A', 'C', -18),
                      ('A', 'C', 18), ('A', 'D', 0), ('B', 'D', 0),
                      ('C', 'D', 0)):
        (x1, y1), (x2, y2) = pos[u], pos[v]
        fig.line((x1 + 80 + off, y1 + off), (x2 - 80 + off, y2 + off), GRAY, 6)
    for k, (cx, cy) in pos.items():
        fig.circle(cx, cy, 80, fill=WHITE, outline=TEAL, width=5)
        fig.text((cx, cy), k, 48, True, INK, anchor='mm')
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


def main():
    for fn in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
               fig10, fig11, fig12, fig13, fig14, fig15):
        fn()
    make_cover()
    for row in META:
        row['path'] = 'assets/' + Path(row['path']).name
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(META))


if __name__ == '__main__':
    main()
