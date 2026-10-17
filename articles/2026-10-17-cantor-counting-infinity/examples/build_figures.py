#!/usr/bin/env python3
"""Original teaching figures for the infinity article. MIT."""
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


def arrow_row(fig, y, left, right, color=TEAL, size=42):
    """A pairing row: left item -> right item, with an arrow between."""
    fig.text((60, y), left, size, color=INK)
    fig.arrow((430, y + 20), (610, y + 20), color, 5, 14)
    fig.text((640, y), right, size, color=INK)


# ---------------------------------------------------------------- 01 旅馆
def fig01():
    fig = Fig(880)
    fig.text((48, 34), '希尔伯特旅馆：有无穷多个房间', 52, True)
    sub(fig, 104, '房间编号 1、2、3、…… 一直数下去，没有最后一间。今天客满。')
    y = 250
    for i in range(8):
        fig.rect(60 + i * 118, y, 60 + i * 118 + 100, y + 150, fill=TINT_B)
        fig.text((60 + i * 118 + 50, y + 46), str(i + 1), 44, True, INK,
                 anchor='mm')
        fig.text((60 + i * 118 + 50, y + 106), '有人', 40, color=INK_SOFT,
                 anchor='mm')
    fig.text((1010, y + 75), '…', 56, True, INK, anchor='mm')
    fig.text((531, y + 220), '每一间都住着人，但后面还有房间——永远有。', 42,
             color=INK, anchor='mm')
    fig.text((531, y + 286), '这就是「无穷」和「很大的数」的区别。', 44, True,
             INK, anchor='mm')
    save(fig, '01-hotel.png', '希尔伯特旅馆的起点')


# ---------------------------------------------------------------- 02 第一夜
def fig02():
    h = R['hotel']
    fig = Fig(880)
    fig.text((48, 34), '第一夜：来了一位新客人', 52, True)
    sub(fig, 104, '客满了。但老板说：请 1 号房的客人搬到 2 号，2 号搬到 3 号，依此类推。')
    y = 250
    fig.text((48, y), '搬之前', 42, True, INK)
    for i, r in enumerate(h['night1_before'][:7]):
        fig.rect(200 + i * 112, y - 26, 200 + i * 112 + 96, y + 26, fill=TINT_B)
        fig.text((200 + i * 112 + 48, y), str(r), 42, color=INK, anchor='mm')
    y += 150
    fig.text((48, y), '搬之后', 42, True, INK)
    for i, r in enumerate(h['night1_after'][:7]):
        fig.rect(200 + i * 112, y - 26, 200 + i * 112 + 96, y + 26, fill=TINT_G)
        fig.text((200 + i * 112 + 48, y), str(r), 42, color=INK, anchor='mm')
    fig.text((1010, y), '…', 48, True, INK, anchor='mm')
    y += 100
    y = facts(fig, y, [
        '每个人都有一个新房间，一个也没落下——因为后面永远还有房间。',
        '空出来的 1 号房，给新客人。',
        '「客满」在无穷旅馆里，不等于「住不下」。',
    ], accent=GREEN)
    save(fig, '02-hotel-one-guest.png', '无穷旅馆的第一夜（程序输出）')


# ---------------------------------------------------------------- 03 第二夜
def fig03():
    h = R['hotel']
    fig = Fig(900)
    fig.text((48, 34), '第二夜：来了一辆无限长的车', 52, True)
    sub(fig, 104, '车上坐着无穷多位客人。老板说：原来的客人，请都搬到「房间号乘 2」。')
    y = 250
    y = facts(fig, y, [
        '原来的 1 号搬到 2 号，2 号搬到 4 号，3 号搬到 6 号……',
        '于是所有奇数号房间都空了出来：1、3、5、7……',
        '无穷多位新客人，一人一间，全都住下。',
    ], accent=BLUE)
    fig.box('odd', 48, y + 10, 1014, y + 180, fill=TINT_A)
    fig.text((76, y + 48), '空出来的房间', 44, True, AMBER, inside='odd')
    fig.text((76, y + 112), '1、3、5、7、9、11 ……（也是无穷多个）', 42,
             color=INK, inside='odd')
    fig.text((531, y + 230), '无穷加上无穷，还是无穷。', 44, True, INK,
             anchor='mm')
    save(fig, '03-hotel-bus.png', '无穷旅馆的第二夜（程序输出）')


# ---------------------------------------------------------------- 04 一一配对
def fig04():
    fig = Fig(960)
    fig.text((48, 34), '「一样多」到底是什么意思', 52, True)
    sub(fig, 104, '数东西的时候，我们其实在做一件事：一个一个配成对。')
    fig.box('a', 48, 240, 1014, 540, fill=TINT_G)
    fig.text((76, 280), '能配完', 44, True, GREEN, inside='a')
    fig.text((76, 344), '左手 5 个石子，右手 5 个石子。', 42, color=INK,
             inside='a')
    fig.text((76, 398), '一对一对配下去，两边同时用完。', 42, color=INK,
             inside='a')
    fig.text((76, 452), '配得完，就是一样多。', 42, True, GREEN, inside='a')
    fig.box('b', 48, 580, 1014, 870, fill=TINT_R)
    fig.text((76, 620), '配不完', 44, True, RED, inside='b')
    fig.text((76, 684), '左手 5 个，右手 6 个。', 42, color=INK, inside='b')
    fig.text((76, 738), '配到最后，右手还剩一个。', 42, color=INK, inside='b')
    fig.text((76, 792), '配不上对，就是不一样多。', 42, True, RED, inside='b')
    fig.text((531, 930), '对无穷集合，我们把这个办法直接拿来当定义。', 42,
             color=INK, anchor='mm')
    save(fig, '04-pairing.png', '「一样多」的定义：能不能一一配对')


# ---------------------------------------------------------------- 05 偶数
def fig05():
    p = R['pairings'][0]
    fig = Fig(880)
    fig.text((48, 34), '自然数和偶数，一样多', 52, True)
    sub(fig, 104, '这听起来很荒唐：偶数明明只是自然数的一半。看配对。')
    y = 250
    left = list(range(0, 8))
    right = [n * 2 for n in left]
    fig.text((60, y - 50), '自然数', 44, True, INK)
    fig.text((640, y - 50), '偶数', 44, True, INK)
    for i, (a, b) in enumerate(zip(left, right)):
        yy = y + i * 62
        fig.rect(48, yy, 380, yy + 52, fill=TINT_B)
        fig.text((214, yy + 26), str(a), 42, color=INK, anchor='mm')
        fig.rect(620, yy, 952, yy + 52, fill=TINT_T)
        fig.text((786, yy + 26), str(b), 42, color=INK, anchor='mm')
        fig.arrow((392, yy + 26), (608, yy + 26), TEAL, 4, 12)
    y += 8 * 62 + 30
    y = facts(fig, y, [
        '每个自然数都配到一个偶数，每个偶数也都被配到一次。',
        '程序检查了前 %s 个：没有重复，没有遗漏。'
        % f"{p['checked']:,}",
        '所以按「能不能配对」这个定义，它们一样多。',
    ], accent=TEAL)
    save(fig, '05-evens.png', '自然数与偶数的配对（程序校验）')


# ---------------------------------------------------------------- 06 整数
def fig06():
    fig = Fig(900)
    fig.text((48, 34), '自然数和整数，也一样多', 52, True)
    sub(fig, 104, '整数有正有负，看起来比自然数「多一倍」。用之字形走一遍。')
    y = 250
    pairs = [(0, '0'), (1, '−1'), (2, '1'), (3, '−2'), (4, '2'),
             (5, '−3'), (6, '3'), (7, '−4'), (8, '4')]
    for i, (a, b) in enumerate(pairs):
        yy = y + i * 62
        fig.rect(48, yy, 420, yy + 52, fill=TINT_B)
        fig.text((234, yy + 26), '第 %d 个自然数' % a, 40, color=INK,
                 anchor='mm')
        fig.rect(620, yy, 952, yy + 52, fill=TINT_T)
        fig.text((786, yy + 26), b, 42, color=INK, anchor='mm')
        fig.arrow((432, yy + 26), (608, yy + 26), TEAL, 4, 12)
    y += 9 * 62 + 24
    fig.text((531, y), '0、−1、1、−2、2、−3、3、……', 42, color=INK,
             anchor='mm')
    fig.text((531, y + 54), '一路数下去，一个整数也漏不掉。', 42, color=INK,
             anchor='mm')
    save(fig, '06-integers.png', '自然数与整数的之字形配对')


# ---------------------------------------------------------------- 07 分数
def fig07():
    r = R['rationals']
    fig = Fig(960)
    fig.text((48, 34), '自然数和分数，还是一样多', 52, True)
    sub(fig, 104, '把「分子」和「分母」当坐标，画成一张网格。')
    x0, y0, cell = 250, 250, 88
    for i in range(1, 7):
        for j in range(1, 7):
            fig.rect(x0 + (i - 1) * cell, y0 + (j - 1) * cell,
                     x0 + i * cell, y0 + j * cell, fill=WHITE, outline=LIGHT,
                     width=2)
            fig.text((x0 + (i - 0.5) * cell, y0 + (j - 0.5) * cell),
                     '%d/%d' % (j, i), 40, color=INK, anchor='mm')
    fig.text((x0 + 3 * cell, y0 - 40), '分母 →', 42, True, INK, anchor='mm')
    fig.text((x0 - 40, y0 + 3 * cell), '分子', 42, True, INK, anchor='rm')
    y = y0 + 6 * cell + 50
    y = facts(fig, y, [
        '沿着对角线一条一条扫过去，每个格子都会被扫到一次。',
        '遇到能约分的（比如 2/2）就跳过——它已经用 1/1 数过了。',
        '这样数下去，每一个正分数都会在某一步被数到。',
    ], accent=BLUE)
    fig.text((531, y + 26), '前几个数是：%s'
             % '、'.join(x['value'] for x in r['first_twelve'][:8]), 42,
             color=INK, anchor='mm')
    save(fig, '07-rationals.png', '用网格对角线数遍所有分数')


# ---------------------------------------------------------------- 08 对角线表
def fig08():
    d = R['diagonal'][0]
    fig = Fig(980)
    fig.text((48, 34), '现在换一个问题：0 到 1 之间的小数呢？', 52, True)
    sub(fig, 104, '假设有人声称：所有 0 到 1 之间的小数，能排成一张有编号的表。')
    y = 250
    fig.text((80, y), '编号', 42, True, INK)
    fig.text((260, y), '这个数的各位数字', 42, True, INK)
    fig.text((1010, y), '对角线上的数字', 42, True, AMBER, anchor='ra')
    y += 56
    for i, e in enumerate(d['escapes']):
        s = e['listed']
        body = s.split('.')[1]
        fig.rect(48, y, 1014, y + 62, fill=WHITE)
        fig.text((110, y + 31), '第 %d 个' % (i + 1), 40, color=INK,
                 anchor='mm')
        fig.text((260, y + 31), body, 40, color=INK, anchor='lm')
        fig.rect(260 + (i) * 26, y + 6, 260 + (i + 1) * 26, y + 56,
                 fill=TINT_A)
        fig.text((1010, y + 31), body[i], 42, True, AMBER, anchor='rm')
        y += 70
    fig.text((531, y + 26), '把对角线上这一串数字取出来：%s'
             % d['diagonal'], 42, True, AMBER, anchor='mm')
    save(fig, '08-diagonal-table.png', '假设的「所有小数」列表与它的对角线')


# ---------------------------------------------------------------- 09 造新数
def fig09():
    d = R['diagonal'][0]
    fig = Fig(920)
    fig.text((48, 34), '每一位都改掉，得到一个不在表里的数', 52, True)
    sub(fig, 104, '规则：第 n 个数在第 n 位是什么，新数在那一位就换成别的。')
    y = 250
    for i, e in enumerate(d['escapes']):
        s = e['listed'].split('.')[1]
        fig.rect(48, y, 1014, y + 62, fill=WHITE)
        fig.text((80, y + 31), '第 %d 个 %s' % (i + 1, s), 40, color=INK,
                 anchor='lm')
        fig.text((1010, y + 31), '第 %d 位：%s → %s'
                 % (i + 1, s[i], d['diagonal'].split('.')[1][i]), 40,
                 True, AMBER, anchor='rm')
        y += 70
    y += 16
    y = facts(fig, y, [
        '新数和第 1 个数在第 1 位不同，和第 2 个数在第 2 位不同……',
        '所以它和第 1 个数不是同一个数，和第 2 个也不是，一个都不是。',
        '程序逐行核对过：它确实和表里每一个数都不同。',
    ], accent=GREEN)
    fig.text((531, y + 26), '新数 = %s' % d['diagonal'], 44, True, GREEN,
             anchor='mm')
    save(fig, '09-new-number.png', '对角线造出的新数逐行核对（程序输出）')


# ---------------------------------------------------------------- 10 迭代
def fig10():
    rounds = R['diagonal']
    fig = Fig(900)
    fig.text((48, 34), '「那就把它加进表里不就行了？」', 52, True)
    sub(fig, 104, '可以。加进去之后，同一套办法立刻造出另一个新数。')
    y = 250
    for r in rounds:
        fig.rect(48, y, 1014, y + 116, fill=TINT_G if r['differs_from_all']
                 else TINT_R)
        fig.text((76, y + 34), '第 %d 轮：表里有 %d 个数'
                 % (r['round'], r['how_many_listed']), 44, True, INK)
        fig.text((76, y + 84), '造出的新数：%s' % r['diagonal'], 42,
                 color=INK_SOFT)
        fig.text((1010, y + 58), '逃出全部', 44, True, GREEN, anchor='rm')
        y += 132
    fig.text((531, y + 20), '加一个，逃一个；加一百个，还是逃一个。', 44, True,
             INK, anchor='mm')
    save(fig, '10-iteration.png', '加进去再构造一次，仍然逃出（程序输出）')


# ---------------------------------------------------------------- 11 为什么
def fig11():
    fig = Fig(1000)
    fig.text((48, 34), '为什么新数里不能出现 0 和 9', 52, True)
    sub(fig, 104, '这不是技术细节，是一个真实的坑。')
    fig.box('a', 48, 240, 1014, 590, fill=TINT_R)
    fig.text((76, 280), '同一个数，可以有两种写法', 44, True, RED, inside='a')
    fig.text((76, 348), '0.4999999…… 和 0.5000000……', 42, color=INK,
             inside='a')
    fig.text((76, 402), '是同一个数。', 42, color=INK, inside='a')
    fig.text((76, 470), '如果新数里全是 9，就可能和表里某个数', 42, color=INK,
             inside='a')
    fig.text((76, 524), '写法不同但数值相同，那就没逃出去。', 42, color=INK,
             inside='a')
    fig.box('b', 48, 630, 1014, 880, fill=TINT_G)
    fig.text((76, 670), '回避办法', 44, True, GREEN, inside='b')
    fig.text((76, 738), '新数的每一位只从 1 到 8 里挑。', 42, color=INK,
             inside='b')
    fig.text((76, 792), '这样它永远不会有 9 或 0 的尾巴，写法唯一。', 42,
             color=INK, inside='b')
    fig.text((531, 950), '本文的程序就是这么做的。', 42, color=INK, anchor='mm')
    save(fig, '11-no-nines.png', '为什么对角线要避开 0 和 9',
         min_width_coverage=0.80)


# ---------------------------------------------------------------- 12 结论
def fig12():
    fig = Fig(1000)
    fig.text((48, 34), '于是结论出来了', 52, True)
    sub(fig, 104, '把两件事放在一起。')
    fig.box('a', 48, 240, 1014, 540, fill=TINT_B)
    fig.text((76, 280), '假设', 44, True, BLUE, inside='a')
    fig.text((76, 348), '所有 0 到 1 之间的小数，', 42, color=INK, inside='a')
    fig.text((76, 402), '能排成一张有编号的表。', 42, color=INK, inside='a')
    fig.text((76, 470), '每一行一个数，一行不漏。', 42, color=INK, inside='a')
    fig.box('b', 48, 580, 1014, 880, fill=TINT_R)
    fig.text((76, 620), '但是', 44, True, RED, inside='b')
    fig.text((76, 688), '对角线造出的那个数，', 42, color=INK, inside='b')
    fig.text((76, 742), '不在这张表的任何一行里。', 42, color=INK, inside='b')
    fig.text((76, 810), '它是个小数，却没有编号。', 42, color=INK, inside='b')
    fig.text((531, 950), '矛盾。所以这种表根本不存在。', 46, True, RED,
             anchor='mm')
    fig.text((531, 1016), '结论：0 到 1 之间的小数，比自然数多。', 44, True,
             INK, anchor='mm')
    save(fig, '12-conclusion.png', '对角线论证的结论',
         min_width_coverage=0.80)


# ---------------------------------------------------------------- 13 幂集
def fig13():
    rows = R['power_set']
    fig = Fig(920)
    fig.text((48, 34), '还有更一般的说法：子集总比元素多', 52, True)
    sub(fig, 104, '一个集合的所有子集，组成它的「幂集」。幂集一定比原集合大。')
    y = 250
    fig.text((220, y - 26), '集合大小 n', 42, True, INK, anchor='mm')
    fig.text((580, y - 26), '子集个数 2ⁿ', 42, True, INK, anchor='mm')
    fig.text((900, y - 26), '比 n 大吗', 42, True, INK, anchor='mm')
    for r in rows[:8]:
        fig.rect(48, y, 1014, y + 62, fill=WHITE)
        fig.text((220, y + 31), str(r['size']), 42, color=INK, anchor='mm')
        fig.text((580, y + 31), str(r['subsets']), 42, color=INK, anchor='mm')
        fig.text((900, y + 31), '是' if r['bigger'] else '否', 42, True, GREEN,
                 anchor='mm')
        y += 70
    fig.text((531, y + 26), 'n 变大时，2ⁿ 把 n 越甩越远。', 42, color=INK,
             anchor='mm')
    save(fig, '13-power-set.png', '子集个数总是超过元素个数（程序输出）')


# ---------------------------------------------------------------- 14 二进制
def fig14():
    rows = R['strings_vs_subsets']
    fig = Fig(900)
    fig.text((48, 34), '换个说法：二进制串', 52, True)
    sub(fig, 104, '长度为 n 的 0/1 串，正好可以表示 n 个东西的每一种「选或不选」。')
    y = 250
    y = facts(fig, y, [
        '串的第 k 位是 1，就表示「第 k 个东西被选进来了」。',
        '所以「长度为 n 的二进制串」和「n 个东西的子集」是一回事。',
        '程序对 n = 0 到 7 逐个核对：两种数法得到的个数完全相同。',
    ], accent=TEAL)
    fig.text((531, y + 26), '2ⁿ 个子集，也可以看成 2ⁿ 个二进制串。', 42,
             color=INK, anchor='mm')
    save(fig, '14-binary.png', '二进制串与子集是同一件事（程序核对）')


# ---------------------------------------------------------------- 15 两种无穷
def fig15():
    fig = Fig(920)
    fig.text((48, 34), '无穷也有大小之分', 52, True)
    sub(fig, 104, '这是康托尔最惊人的发现：无穷不是一个，而是很多个。')
    fig.box('a', 48, 240, 1014, 560, fill=TINT_G)
    fig.text((76, 278), '可数无穷', 46, True, GREEN, inside='a')
    fig.text((76, 346), '能排成一张有编号的表：', 42, color=INK, inside='a')
    fig.text((76, 400), '第 1 个、第 2 个、第 3 个……', 42, color=INK,
             inside='a')
    fig.text((76, 452), '自然数、偶数、整数、分数，都属于这一类。', 42,
             color=INK, inside='a')
    fig.text((76, 504), '它们全都「一样多」。', 42, True, GREEN, inside='a')
    fig.box('b', 48, 600, 1014, 880, fill=TINT_R)
    fig.text((76, 638), '不可数无穷', 46, True, RED, inside='b')
    fig.text((76, 706), '排不成这样的表。无论怎么排，总有数漏在外面。', 42,
             color=INK, inside='b')
    fig.text((76, 760), '0 到 1 之间的小数、实数，都属于这一类。', 42,
             color=INK, inside='b')
    fig.text((76, 824), '它们比可数无穷「更多」。', 42, True, RED, inside='b')
    save(fig, '15-two-infinities.png', '可数无穷与不可数无穷')


# ---------------------------------------------------------------- 16 历史
def fig16():
    fig = Fig(940)
    fig.text((48, 34), '这个结论当年几乎没人愿意接受', 52, True)
    sub(fig, 104, '康托尔 1874 年证明了这个结果，1891 年给出了对角线这个更漂亮的证法。')
    y = 240
    y = facts(fig, y, [
        '他的老师克罗内克强烈反对，认为这套东西根本不是数学。',
        '两件事的关系说法不一：有人归因于同行敌意，也有人认为是双相障碍。',
        '康托尔从 1884 年起长期陷入抑郁。',
        '希尔伯特后来这样评价：没有人能把我们从康托尔创造的乐园里赶出去。',
        '今天，「可数」与「不可数」是数学专业的基础内容之一。',
    ], accent=AMBER)
    fig.text((531, y + 26), '一个正确的结论，也可能要等一代人才被接受。', 44,
             True, INK, anchor='mm')
    save(fig, '16-history.png', '康托尔的结论与当年的反对')


# ---------------------------------------------------------------- 17 图灵
def fig17():
    fig = Fig(1020)
    fig.text((48, 34), '同一套对角线，两种用法', 52, True)
    sub(fig, 104, '图灵 1936 年处理「停机问题」时，用的正是这个形状的论证。')
    fig.box('a', 48, 240, 1014, 540, fill=TINT_B)
    fig.text((76, 280), '康托尔的做法', 44, True, BLUE, inside='a')
    fig.text((76, 348), '假设所有小数排成一张表，', 42, color=INK, inside='a')
    fig.text((76, 402), '然后造出一个不在表里的数。', 42, color=INK, inside='a')
    fig.text((76, 470), '结论：这张表不存在。', 42, True, BLUE, inside='a')
    fig.box('b', 48, 600, 1014, 900, fill=TINT_T)
    fig.text((76, 640), '图灵的做法', 44, True, TEAL, inside='b')
    fig.text((76, 708), '假设所有程序排成一张表，', 42, color=INK, inside='b')
    fig.text((76, 762), '然后造出一个行为不同的程序。', 42, color=INK,
             inside='b')
    fig.text((76, 830), '结论：这样一张表也不存在。', 42, True, TEAL,
             inside='b')
    fig.text((531, 970), '同一个手法，一个用来数无穷，', 42, True, INK,
             anchor='mm')
    fig.text((531, 1024), '一个用来划出计算的边界。', 42, True, INK,
             anchor='mm')
    save(fig, '17-turing.png', '对角线论证与停机问题是同一个形状')


# ---------------------------------------------------------------- 18 收尾
def fig18():
    fig = Fig(880)
    fig.text((48, 34), '自己动手改一个条件', 52, True)
    sub(fig, 104, '这一篇也只需要一支笔和一张纸。')
    items = [
        ('自己配一次自然数和偶数', '写出前十个配对，看有没有重复或遗漏。'),
        ('把对角线改成「每位加 1」', '为什么不能简单加 1？想想 9 会变成什么。'),
        ('数一数 3 个东西有几个子集', '动手列出来，再和 2³ 对一下。'),
        ('想一个「比实数还多」的东西', '提示：实数的所有子集更大。'),
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
    fig.text((531, y + 20), '先猜结果，再动手验。', 42, True, BLUE, anchor='mm')
    save(fig, '18-try-it.png', '读者可以自己改动的四个条件',
         min_width_coverage=0.80)


def make_cover():
    fig = Fig(1080, width=1080)
    fig.text((540, 226), '无穷也有大小', 60, True, anchor='ma')
    fig.text((540, 302), '康托尔用一条对角线，分开了两种无穷', 46, True, TEAL,
             anchor='ma')
    rows = ['0.12345678', '0.23456781', '0.34567812', '0.45678123']
    for i, s in enumerate(rows):
        fig.text((300, 400 + i * 62), s, 44, color=INK)
        fig.rect(300 + i * 26, 400 + i * 62 - 6, 300 + (i + 1) * 26,
                 400 + i * 62 + 44, fill=TINT_A)
    fig.text((760, 420), '← 对角线', 44, True, AMBER)
    fig.text((760, 500), '0.2468…', 46, True, GREEN)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


def main():
    for fn in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
               fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18):
        fn()
    make_cover()
    for row in META:
        row['path'] = 'assets/' + Path(row['path']).name
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(META))


if __name__ == '__main__':
    main()
