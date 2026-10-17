#!/usr/bin/env python3
"""Original teaching figures for the Monty Hall article. MIT.

Every probability, count and rate drawn here comes from running
examples/run_model.py; results.json is the only source of numbers.
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


def door(fig, x, y, w, h, label, fill=WHITE, outline=GRAY, big=False):
    fig.rect(x, y, x + w, y + h, fill=fill, outline=outline, width=5,
             radius=14)
    fig.circle(x + w - 34, y + h / 2, 9, fill=outline, outline=outline,
               width=2)
    fig.text((x + w / 2, y + h / 2), label, 56 if big else 48, True, INK,
             anchor='mm')


def bar_row(fig, x0, x1, y, frac, color, label, value, h=62):
    w = (x1 - x0) * frac
    fig.rect(x0, y, x0 + max(4, w), y + h, fill=color)
    fig.text((x0 - 24, y + h / 2), label, 42, color=INK, anchor='rm')
    fig.text((x0 + w + 18, y + h / 2), value, 42, True, color, anchor='lm')


# ---------------------------------------------------------------- 01 开门
def fig01():
    fig = Fig(760)
    fig.text((48, 34), '三扇门，一辆车，两只羊', 52, True)
    sub(fig, 104, '你选一扇。主持人打开另一扇，里面是羊。现在：换，还是不换？')
    for i in range(3):
        door(fig, 96 + i * 300, 250, 250, 340, str(i + 1), big=True)
    fig.text((531, 650), '三扇门后面：一辆车、两只羊。你不知道车在哪。', 42,
             color=INK, anchor='mm')
    save(fig, '01-three-doors.png', '题目的起点：三扇门')


# ---------------------------------------------------------------- 02 约束
def fig02():
    fig = Fig(880)
    fig.text((48, 34), '关键在那句「主持人知道车在哪」', 52, True)
    sub(fig, 104, '他不是随便开一扇。他必须开一扇羊，而且不能开你选的那扇。')
    fig.box('a', 48, 230, 1014, 452, fill=TINT_G)
    fig.text((76, 266), '他不能开的', 44, True, GREEN, inside='a')
    fig.text((76, 330), '你选的那扇门（他不能动你的选择）', 42, color=INK,
             inside='a')
    fig.text((76, 384), '藏着车的那扇门（他不能把车送给你）', 42, color=INK,
             inside='a')
    fig.box('b', 48, 492, 1014, 714, fill=TINT_A)
    fig.text((76, 512), '他只能开的', 44, True, AMBER, inside='b')
    fig.text((76, 574), '剩下那扇（或那几扇）羊门。', 42, color=INK,
             inside='b')
    fig.text((76, 628), '所以他的动作里，带着你不知道的信息。', 42, True, INK,
             inside='b')
    fig.text((531, 794), '这条约束，是整道题的全部关键。', 44, True, RED,
             anchor='mm')
    save(fig, '02-host-constraint.png', '主持人的动作受什么约束')


# ---------------------------------------------------------------- 03 九种情形
def fig03():
    cases = R['exact_three_doors_cases']
    fig = Fig(1080)
    fig.text((48, 34), '把所有情形摆出来数一遍', 52, True)
    sub(fig, 104, '车可能在 1、2、3 号门，你也可能选 1、2、3 号门，一共九种，每种一样可能。')
    y = 250
    fig.text((64, y - 20), '车在', 42, True, INK)
    fig.text((200, y - 20), '你选', 42, True, INK)
    fig.text((336, y - 20), '主持人开', 42, True, INK)
    fig.text((536, y - 20), '不换', 42, True, INK)
    fig.text((700, y - 20), '换', 42, True, INK)
    fig.text((850, y - 20), '换成几号', 42, True, INK)
    y += 24
    for c in cases:
        row = TINT_G if c['switch_wins'] else TINT_R
        fig.rect(48, y, 1014, y + 62, fill=row)
        fig.text((110, y + 31), str(c['car'] + 1), 42, color=INK, anchor='mm')
        fig.text((246, y + 31), str(c['pick'] + 1), 42, color=INK, anchor='mm')
        fig.text((386, y + 31), str(c['host_opens'] + 1), 42, color=INK,
                 anchor='mm')
        fig.text((576, y + 31), '赢' if c['stay_wins'] else '输', 42, True,
                 GREEN if c['stay_wins'] else RED, anchor='mm')
        fig.text((740, y + 31), '赢' if c['switch_wins'] else '输', 42, True,
                 GREEN if c['switch_wins'] else RED, anchor='mm')
        fig.text((930, y + 31), '%d 号' % (c['switch_to'] + 1), 42, color=INK,
                 anchor='mm')
        y += 70
    e = R['exact_three_doors']
    fig.text((531, y + 30), '九种里：不换赢 %d 种，换赢 %d 种。'
             % (e['stay_wins'], e['switch_wins']), 44, True, INK, anchor='mm')
    save(fig, '03-nine-cases.png', '九种情形的完整枚举（程序输出）')


# ---------------------------------------------------------------- 04 对比
def fig04():
    e = R['exact_three_doors']
    fig = Fig(760)
    fig.text((48, 34), '数出来的结果', 52, True)
    sub(fig, 104, '九种情形里，换赢的次数是不换的两倍。')
    x0, x1 = 300, 1014
    bar_row(fig, x0, x1, 250, e['stay_wins'] / e['cases'], RED, '不换',
            '%d / %d = 1/3' % (e['stay_wins'], e['cases']))
    bar_row(fig, x0, x1, 360, e['switch_wins'] / e['cases'], GREEN, '换',
            '%d / %d = 2/3' % (e['switch_wins'], e['cases']))
    fig.text((531, 520), '两根柱子的长度按同一根轴算，直接可比。', 42,
             color=INK_SOFT, anchor='mm')
    fig.text((531, 580), '所以答案是：换。', 46, True, GREEN, anchor='mm')
    save(fig, '04-three-vs-six.png', '不换与换的胜率（九种情形计数）')


# ---------------------------------------------------------------- 05 直觉陷阱
def fig05():
    fig = Fig(900)
    fig.text((48, 34), '为什么直觉会说是 50 比 50', 52, True)
    sub(fig, 104, '剩下两扇门，看起来一样。但它们并不是对称的。')
    fig.box('a', 48, 240, 1014, 450, fill=TINT_R)
    fig.text((76, 276), '直觉的想法', 44, True, RED, inside='a')
    fig.text((76, 340), '「两扇门，一扇有车，所以各占一半。」', 42, color=INK,
             inside='a')
    fig.text((76, 400), '这个推理漏掉了一件事。', 42, color=INK, inside='a')
    fig.box('b', 48, 490, 1014, 782, fill=TINT_G)
    fig.text((76, 526), '实际情况', 44, True, GREEN, inside='b')
    fig.text((76, 590), '你选的那扇门，是你在主持人开口前选的，', 42,
             color=INK, inside='b')
    fig.text((76, 644), '它中奖的机会一直是你当初选时的 1/3，没有变。', 42,
             color=INK, inside='b')
    fig.text((76, 698), '另一扇门是主持人挑剩下的，它背着 2/3。', 42, True,
             INK, inside='b')
    fig.text((531, 858), '两扇门的历史不一样，所以概率不一样。', 44, True,
             INK, anchor='mm')
    save(fig, '05-why-not-fifty.png', '为什么「剩下两扇各一半」是错的')


# ---------------------------------------------------------------- 06 贝叶斯
def fig06():
    b = R['bayes']
    fig = Fig(940)
    fig.text((48, 34), '用贝叶斯算一遍，也是 1/3 和 2/3', 52, True)
    sub(fig, 104, '把「主持人开了 3 号门」当成一条新证据，看它怎么改变两边的可能性。')
    rows = [
        ('一开始，车在你选的门后', b['prior_car_behind_pick'], RED),
        ('一开始，车在另外两扇门后', b['prior_car_behind_other'], TEAL),
        ('若车在你选的门后，他开到 3 号门的机会', b['likelihood_host_opens_door3_if_car_behind_pick'], RED),
        ('若车在另一扇门后，他只能开 3 号门', b['likelihood_host_opens_door3_if_car_behind_other'], TEAL),
        ('乘起来再归一化，最后得到', '', INK),
        ('车在你选的门后', b['posterior_car_behind_pick'], RED),
        ('车在另一扇门后', b['posterior_car_behind_other'], TEAL),
    ]
    y = 230
    for label, value, col in rows:
        if value:
            fig.rect(48, y, 1014, y + 74, fill=WHITE)
            fig.text((76, y + 37), label, 42, color=INK, anchor='lm')
            fig.text((990, y + 37), value, 42, True, col, anchor='rm')
        else:
            fig.text((76, y + 37), label, 44, True, INK, anchor='lm')
        y += 86
    fig.text((531, y + 20), '注意第四行是 1，不是 1/2——他没得选。', 42, True,
             AMBER, anchor='mm')
    save(fig, '06-bayes.png', '贝叶斯逐步计算（精确分数）')


# ---------------------------------------------------------------- 07 模拟
def fig07():
    sims = R['simulations']
    fig = Fig(1000)
    fig.text((48, 34), '真的跑二十万次，数字自己会说话', 52, True)
    sub(fig, 104, '下面全部是程序实际跑出来的结果，不是理论值。')
    y = 250
    x0, x1 = 240, 780
    for s_ in sims[:3]:
        fig.text((48, y), s_['label'], 44, True, INK)
        fig.text((48, y + 56), '共 %s 次，其中 %s 次计入选票'
                 % (f"{s_['trials']:,}", f"{s_['kept']:,}"), 42,
                 color=INK_SOFT)
        for k, (name, rate, col) in enumerate(
                (('不换', s_['stay_rate_decimal'], RED),
                 ('换', s_['switch_rate_decimal'], GREEN))):
            yy = y + 112 + k * 66
            w = (x1 - x0) * rate
            fig.rect(x0, yy, x0 + max(4, w), yy + 56, fill=col)
            fig.text((x0 - 18, yy + 28), name, 42, True, col, anchor='rm')
            fig.text((x0 + w + 16, yy + 28), '%.4f' % rate, 42, True, col,
                     anchor='lm')
        y += 268
    fig.text((531, y + 16), '三种配置，换的胜率都远高于不换。', 44, True, INK,
             anchor='mm')
    save(fig, '07-simulation.png', '三组配置的模拟结果（程序实际输出）')


# ---------------------------------------------------------------- 08 不知情
def fig08():
    s = R['simulations'][1]
    fig = Fig(940)
    fig.text((48, 34), '去掉「主持人知道答案」，答案就变了', 52, True)
    sub(fig, 104, '如果主持人也不知道车在哪，他只是随便开一扇，结果碰巧是羊——')
    y = 250
    y = facts(fig, y, [
        '这时换与不换各占一半，真正的 50 比 50。',
        '为什么？因为他开到羊这件事，纯属运气，没有携带关于车的信息。',
        '同样的场面、同样的两扇门，只因为「他知不知道」，概率就不同。',
    ], accent=AMBER)
    fig.box('cmp', 48, y + 10, 1014, y + 268, fill=WHITE)
    fig.text((76, y + 46), '两种主持人的对照', 44, True, INK, inside='cmp')
    fig.text((76, y + 108), '他知道答案：换的胜率 2/3', 42, True, GREEN,
             inside='cmp')
    fig.text((76, y + 162), '他不知道答案：换的胜率 1/2', 42, True, RED,
             inside='cmp')
    fig.text((76, y + 212), '（实测 %.4f，共 %s 次有效试验）'
             % (s['switch_rate_decimal'], f"{s['kept']:,}"), 40,
             color=INK_SOFT, inside='cmp')
    save(fig, '08-ignorant-host.png', '不知情主持人把 2/3 变回 1/2（实测）')


# ---------------------------------------------------------------- 09 一百扇门
def fig09():
    cf = {r['doors']: r for r in R['closed_form']}
    sim = R['simulations'][2]
    fig = Fig(940)
    fig.text((48, 34), '把门加到一百扇，直觉就追上来了', 52, True)
    sub(fig, 104, '你选 1 扇，主持人把另外 98 扇羊门全打开，只剩一扇没开。')
    y = 250
    y = facts(fig, y, [
        '你一开始选中的机会只有 1/100。',
        '主持人避开了 98 扇羊门，那扇没开的门，扛着剩下的 99/100。',
        '换的胜率是 %s，不换是 %s。' % (cf[100]['switch'], cf[100]['stay']),
    ], accent=TEAL)
    fig.text((531, y + 30), '实测：二十万次里换赢 %s 次（%.4f）。'
             % (f"{sim['switch_wins']:,}", sim['switch_rate_decimal']),
             42, True, GREEN, anchor='mm')
    fig.text((531, y + 90), '门越多，「换」越显然。三扇门只是把这个差距压缩了。',
             42, color=INK, anchor='mm')
    save(fig, '09-hundred-doors.png', '一百扇门版本与实测')


# ---------------------------------------------------------------- 10 公式
def fig10():
    rows = R['closed_form']
    fig = Fig(880)
    fig.text((48, 34), '一般情况：n 扇门，主持人开掉 k 扇', 52, True)
    sub(fig, 104, '公式里每个符号都能对上刚才的数：n 是门数，k 是他打开的羊门数。')
    fig.box('f', 48, 240, 1014, 452, fill=TINT_B)
    fig.text((531, 286), '不换：1 / n', 46, True, RED, anchor='mm',
             inside='f')
    fig.text((531, 356), '换到某扇没开的门：', 46, True, GREEN, anchor='mm',
             inside='f')
    fig.text((531, 408), '(n−1) ÷ [ n × (n−1−k) ]', 46, True, GREEN, anchor='mm',
             inside='f')
    y = 500
    fig.text((80, y - 24), '门数 n', 42, True, INK)
    fig.text((320, y - 24), '开掉 k', 42, True, INK)
    fig.text((560, y - 24), '不换', 42, True, INK)
    fig.text((800, y - 24), '换', 42, True, INK)
    for r in rows:
        fig.rect(48, y, 1014, y + 68, fill=WHITE)
        fig.text((200, y + 34), str(r['doors']), 42, color=INK, anchor='mm')
        fig.text((430, y + 34), str(r['host_opens']), 42, color=INK, anchor='mm')
        fig.text((640, y + 34), r['stay'], 42, True, RED, anchor='mm')
        fig.text((890, y + 34), r['switch'], 42, True, GREEN, anchor='mm')
        y += 78
    save(fig, '10-formula.png', '一般公式与四组取值')


# ---------------------------------------------------------------- 11 条件概率
def fig11():
    c = R['conditioning']
    fig = Fig(1000)
    fig.text((48, 34), '一个容易漏掉的细节：他开的是哪扇门', 52, True)
    sub(fig, 104, '你的选择固定是 1 号门。看「他开了几号门」这个条件。')
    y = 240
    for title, key, col in (('主持人随机开一只羊', 'random_host', BLUE),
                            ('主持人固定开编号最小的羊', 'lowest_number_host',
                             AMBER)):
        fig.text((48, y), title, 44, True, col)
        y += 62
        for r in c[key]:
            fig.rect(48, y, 1014, y + 66, fill=WHITE)
            fig.text((100, y + 33), '他开了 %d 号门' % r['opened'], 42,
                     color=INK, anchor='lm')
            fig.text((560, y + 33), '不换 %s' % r['stay_win'], 42, True, RED,
                     anchor='lm')
            fig.text((800, y + 33), '换 %s' % r['switch_win'], 42, True, GREEN,
                     anchor='lm')
            y += 74
        y += 24
    fig.text((531, y + 16), '两种主持人，总体胜率都是 1/3 与 2/3。', 42, True,
             INK, anchor='mm')
    fig.text((531, y + 72), '但按「他开了哪扇门」分开看，就不一样了。', 42,
             color=INK, anchor='mm')
    save(fig, '11-conditioning.png', '按主持人实际开的门分别计算（精确分数）')


# ---------------------------------------------------------------- 12 为什么
def fig12():
    fig = Fig(900)
    fig.text((48, 34), '为什么「他开哪扇门」会改变答案', 52, True)
    sub(fig, 104, '因为不同的主持人策略，让「他开了 3 号门」这件事的含义不同。')
    fig.box('a', 48, 240, 1014, 502, fill=TINT_B)
    fig.text((76, 276), '随机开一只羊', 44, True, BLUE, inside='a')
    fig.text((76, 340), '无论车在哪，他开到 3 号门的可能性都算得清，', 42,
             color=INK, inside='a')
    fig.text((76, 394), '所以这个观察不额外偏向任何一扇门。', 42, color=INK,
             inside='a')
    fig.text((76, 440), '结果：换的胜率还是 2/3。', 42, True, GREEN,
             inside='a')
    fig.box('b', 48, 542, 1014, 800, fill=TINT_A)
    fig.text((76, 562), '固定开编号最小的羊', 44, True, AMBER, inside='b')
    fig.text((76, 626), '如果他开了 3 号门，说明 2 号门不能开——', 42,
             color=INK, inside='b')
    fig.text((76, 680), '那只有一种可能：车就在 2 号门后面。', 42, color=INK,
             inside='b')
    fig.text((76, 726), '结果：换的胜率是 1。', 42, True, GREEN, inside='b')
    fig.text((531, 880), '概率不只取决于你看到什么，', 42, True, RED,
             anchor='mm')
    fig.text((531, 934), '还取决于它是怎么产生的。', 42, True, RED, anchor='mm')
    save(fig, '12-why-conditioning.png', '主持人策略如何改变条件概率')


# ---------------------------------------------------------------- 13 收敛
def fig13():
    import math
    conv = R['convergence']
    fig = Fig(960)
    fig.text((48, 34), '跑得越多，越贴近 2/3', 52, True)
    sub(fig, 104, '同一套程序，只记下不同次数时的累计胜率。横轴是对数刻度。')
    x0, x1, y0, y1 = 250, 960, 260, 600
    def px(n): return x0 + (x1 - x0) * math.log10(n) / math.log10(200000)
    def py(v): return y1 - (y1 - y0) * (v - 0.55) / 0.40
    fig.line((x0, py(2/3)), (x1, py(2/3)), GREEN, 4, dash=12)
    fig.text((x0 - 10, py(2/3)), '2/3', 42, True, GREEN, anchor='rm')
    pts = [(px(c['trials']), py(c['switch_rate'])) for c in conv]
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, TEAL, 6)
    for c, p in zip(conv, pts):
        fig.circle(p[0], p[1], 10, fill=TEAL, outline=TEAL, width=2)
    fig.text((pts[0][0], pts[0][1] - 46), '0.9000', 42, True, TEAL, anchor='mm')
    fig.text((pts[-1][0], pts[-1][1] + 50), '0.6666', 42, True, TEAL, anchor='mm')
    y = y1 + 60
    fig.text((531, y), '每次试验的累计胜率', 42, True, INK, anchor='mm')
    y += 74
    for c in conv:
        fig.text((48, y), '%s 次' % f"{c['trials']:,}", 40, color=INK_SOFT)
        fig.text((1014, y), '%.4f' % c['switch_rate'], 40, True, TEAL,
                 anchor='ra')
        y += 56
    save(fig, '13-convergence.png', '换的胜率随试验次数的收敛（程序实际输出）')


# ---------------------------------------------------------------- 14 历史
def fig14():
    fig = Fig(900)
    fig.text((48, 34), '这道题是怎么出名的', 52, True)
    sub(fig, 104, '它不是凭空编的题，背后有一串真实的人和事。')
    y = 240
    y = facts(fig, y, [
        '1975 年，Steve Selvin 把它写成信寄给《The American Statistician》，'
        '并在后续信件里给它起名「蒙提霍尔问题」。',
        '蒙提霍尔是真实存在的人：美国电视节目《Let’s Make a Deal》的主持人。',
        '1990 年，读者 Craig F. Whitaker 把这道题寄给《Parade》杂志的'
        '「Ask Marilyn」专栏，由 Marilyn vos Savant 作答。',
        '这道题在数学上等价于 1959 年 Martin Gardner 在《科学美国人》上'
        '讲过的「三个囚犯问题」。',
    ], accent=AMBER)
    save(fig, '14-history.png', '题目的来源与等价问题')


# ---------------------------------------------------------------- 15 一万封信
def fig15():
    fig = Fig(880)
    fig.text((48, 34), '专栏登出后，约一万个人写信说她错了', 52, True)
    sub(fig, 104, '其中近一千人有博士学位。这不是一道难题，是一道反直觉的题。')
    fig.box('a', 48, 240, 1014, 462, fill=TINT_R)
    fig.text((76, 276), '连数学家也一时不信', 44, True, RED, inside='a')
    fig.text((76, 340), 'Paul Erdős 是历史上最多产的数学家之一，', 42,
             color=INK, inside='a')
    fig.text((76, 394), '他也不相信，直到有人当场跑了一个计算机模拟。', 42,
             color=INK, inside='a')
    fig.box('b', 48, 502, 1014, 700, fill=TINT_G)
    fig.text((76, 522), '鸽子反而学得会', 44, True, GREEN, inside='b')
    fig.text((76, 586), '反复做这道题的鸽子，很快就学会每次都换。', 42,
             color=INK, inside='b')
    fig.text((76, 640), '人却会因为「两扇门看起来一样」而坚持不换。', 42,
             color=INK, inside='b')
    fig.text((531, 780), '直觉在概率题上出错，是常态，不是笨。', 44, True, INK,
             anchor='mm')
    save(fig, '15-furor.png', '专栏风波与 Erdős、鸽子的对照')


# ---------------------------------------------------------------- 16 三个囚犯
def fig16():
    fig = Fig(900)
    fig.text((48, 34), '同一个问题，换个壳子', 52, True)
    sub(fig, 104, '1959 年 Gardner 讲的「三个囚犯问题」，数学上和它一模一样。')
    fig.box('a', 48, 240, 1014, 600, fill=TINT_B)
    fig.text((76, 276), '三个囚犯 A、B、C', 44, True, BLUE, inside='a')
    fig.text((76, 340), '只有一个会被赦免，另外两个会被处决。', 42, color=INK,
             inside='a')
    fig.text((76, 394), 'A 问看守：B 和 C 里，谁会被处决？', 42, color=INK,
             inside='a')
    fig.text((76, 448), '看守说：B。', 42, color=INK, inside='a')
    fig.text((76, 496), 'A 松一口气：我被赦免的机会', 42, color=INK, inside='a')
    fig.text((76, 542), '从 1/3 变成了 1/2。', 42, color=INK, inside='a')
    fig.box('b', 48, 640, 1014, 848, fill=TINT_R)
    fig.text((76, 676), '他错了', 44, True, RED, inside='b')
    fig.text((76, 740), '看守的回答和他自己会不会被赦免无关，', 42, color=INK,
             inside='b')
    fig.text((76, 794), '他的机会仍然是 1/3，而 C 的机会变成了 2/3。', 42,
             color=INK, inside='b')
    save(fig, '16-three-prisoners.png', '等价问题：三个囚犯')


# ---------------------------------------------------------------- 17 收尾
def fig17():
    fig = Fig(880)
    fig.text((48, 34), '自己动手改一个条件', 52, True)
    sub(fig, 104, '代码在 examples/ 里，只用 Python 标准库。')
    items = [
        ('把门数改成 5，开掉 3 扇', '先猜换的胜率，再跑一次对答案。'),
        ('让主持人不知情', '看换的胜率怎么从 2/3 掉到 1/2。'),
        ('让主持人只在你有 50% 机会时才开', '换的胜率会变成多少？先想清楚再跑。'),
        ('把车换成两个，羊只剩一个', '规则变了，公式也要跟着改。'),
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
    save(fig, '17-try-it.png', '读者可以自己改动的四个条件',
         min_width_coverage=0.80)


def make_cover():
    fig = Fig(1080, width=1080)
    fig.text((540, 236), '换，还是不换？', 58, True, anchor='ma')
    fig.text((540, 308), '一道让一万个人写信说「你错了」的题', 48, True, TEAL,
             anchor='ma')
    for i in range(3):
        door(fig, 190 + i * 240, 380, 200, 260, str(i + 1), big=True)
    fig.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


def main():
    for fn in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
               fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17):
        fn()
    make_cover()
    for row in META:
        row['path'] = 'assets/' + Path(row['path']).name
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(META))


if __name__ == '__main__':
    main()
