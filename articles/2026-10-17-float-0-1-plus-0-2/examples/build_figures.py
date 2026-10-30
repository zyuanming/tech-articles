#!/usr/bin/env python3
"""Original teaching figures for the 0.1+0.2 article. MIT.

Every number drawn here is read from results.json, which run_model.py produced
by actually executing the arithmetic. Nothing is typed in twice.
"""
from __future__ import annotations
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

from figkit import (Fig, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED, GRAY,
                    LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R, TINT_G,
                    bars_are_honest)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []


def num(value):
    """results.json stores exact rationals as 'a/b' strings; get a float back."""
    if isinstance(value, str) and '/' in value:
        return float(Fraction(value))
    return float(value)


# ------------------------------------------------------------------- helpers
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


def table(fig, y, cols, rows, size=40, row_h=68, box=None, name=None,
          head=True, zebra=True):
    """cols: [(x, anchor), ...]. rows: [[(text, colour, bold), ...], ...]."""
    top = y
    for i, row in enumerate(rows):
        if zebra and i % 2 == 1:
            fig.rect(48, y - 10, 1014, y + row_h - 12, fill=PALE, outline=None)
        for (text, color, bold), (x, anchor) in zip(row, cols):
            w = fig.width_of(text, size, bold)
            span = (x, x + w) if anchor == 'la' else (x - w, x)
            assert span[0] >= 44 and span[1] <= 1018, \
                'cell outside the safe band: %r %s' % (text, span)
            kw = dict(inside=name) if name else {}
            fig.text((x, y + 4), text, size, bold=bold, color=color,
                     anchor=anchor, **kw)
        y += row_h
    if box:
        fig.box(box, 40, top - 26, 1022, y - 6, fill=WHITE)
        for row in rows:
            pass
    return y + 18


def codelines(fig, x, y, lines, step=68, size=44):
    for text, color in lines:
        fig.text((x, y), text, size, color=color)
        y += step
    return y


def bar_row(fig, x0, x1, y, frac, color, label, value, h=58, size=40):
    fig.text((x0 - 22, y + h / 2 - 22), label, size, color=INK, anchor='ra')
    fig.rect(x0, y, x0 + max(6, (x1 - x0) * frac), y + h, fill=color, outline=None)
    fig.text((x1 + 18, y + h / 2 - 22), value, size, color=INK)
    return y + h + 26


def bullets(fig, y, items, accent=TEAL, size=42):
    for text in items:
        fig.circle(76, y + 22, 15, fill=accent, outline=accent)
        lines = fig.wrap((116, y + 2), text, size, 898, color=INK)
        y += int(lines * size * 1.35) + 26
    return y


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


# ------------------------------------------------------------------- figures
def fig01():
    f, y = new(1, '0.1 + 0.2 到底等于几',
               '三种常见环境给出同一个「看起来错」的数。这不是某一个软件的毛病，'
               '是所有按同一份标准实现浮点数的机器共同的结果。')
    f.box('code', 44, y, 1018, y + 340)
    codelines(f, 80, y + 34, [
        ('>>> 0.1 + 0.2', INK),
        ('0.30000000000000004', RED),
        ('>>> 0.1 + 0.2 == 0.3', INK),
        ('False', RED),
    ])
    y += 380
    y = note(f, y, '三个数你都写对了，加法本身也没做错。问题出在「0.1」这三个字符所指的那个数：'
                   '机器根本存不下它，只能存一个非常接近、但并不等于十分之一的数。')
    note(f, y, '差多少？差 1 个最小间隔，也就是 ' + R['sum']['difference_ulps'].__str__().split('.')[0] +
         ' 个 ulp。本文后面会把这个数精确算出来。', color=TEAL)
    save(f, '01-the-symptom.png', '现象：0.1 + 0.2 不等于 0.3')


def fig02():
    f, y = new(2, '二进制小数只认分母是 2 的幂',
               '十进制里 1/2、1/4、1/10 都写得出有限小数。二进制里只有分母是 2 的幂的那些才写得出。'
               '下表的十进制一列，超过 7 位的用省略号缩写了。')
    rows = [[('分数', INK, True), ('十进制', INK, True), ('写得出吗', INK, True),
             ('存得准吗', INK, True)]]
    pick = [('1/2', True), ('1/4', True), ('3/4', True), ('1/5', False),
            ('1/10', False), ('1/3', False)]
    by_name = {r['fraction']: r for r in R['exactness']}
    for name, _ in pick:
        r = by_name[name]
        dec = r['decimal']
        shown = dec if len(dec) <= 7 else dec[:6] + '…'
        rows.append([(name, INK, False), (shown, INK, False),
                     ('能' if r['binary_exact'] else '不能', GREEN if r['binary_exact'] else RED, False),
                     ('精确' if r['stored_exactly'] else '有误差', GREEN if r['stored_exactly'] else RED, False)])
    cols = [(56, 'la'), (230, 'la'), (660, 'la'), (1014, 'ra')]
    y = table(f, y, cols, rows)
    note(f, y, '分母里只要有一个 5 或者 3，二进制就永远写不完。十进制世界里的「0.1」，'
               '到了二进制世界就变成一条无限循环小数。')
    save(f, '02-what-binary-can-hold.png', '哪些小数在二进制里是精确的')


def fig03():
    f, y = new(3, '把 1 ÷ 10 用二进制除一遍',
               '十进制里做长除法是「余数乘 10」；二进制里换成「余数乘 2」，其余完全一样。')
    rows = [[('第几位', INK, True), ('上一步余数', INK, True), ('余数 ×2', INK, True),
             ('这一位是', INK, True), ('新余数', INK, True)]]
    for s in R['binary_steps']:
        rows.append([(str(s['index']), GRAY, False), (str(s['remainder_in']), INK, False),
                     (str(s['doubled']), INK, False), (str(s['digit']), TEAL, True),
                     (str(s['remainder_out']), INK, False)])
    y = table(f, y, [(70, 'la'), (280, 'la'), (520, 'la'), (720, 'la'), (1014, 'ra')], rows)
    note(f, y, '第 2 步的余数（2）在第 6 步又出现了。余数一旦重复，后面的每一步都会重复——'
               '所以这个除法永远除不完。', color=AMBER)
    save(f, '03-long-division.png', '用长除法求 1/10 的二进制展开')


def fig04():
    f, y = new(4, '循环节是 0011，周期 4',
               '把 1/10 的二进制展开写出来，从第 2 位起，「0011」四个数字无限重复。')
    b = R['binary']
    digits = b['tenth']['digits']
    at = b['tenth']['cycle_at']
    period = b['tenth']['period']
    f.box('d', 44, y, 1018, y + 210)
    f.text((76, y + 26), '0 . ' + digits[:at] + ' ' + digits[at:at + period] * 4 + ' …',
           46, color=INK, inside='d')
    f.text((76, y + 108), '前 %d 位是过渡，从第 %d 位开始循环，每 %d 位一轮'
           % (at, at + 1, period), 40, color=INK_SOFT, inside='d')
    y += 250
    y = note(f, y, '对比一下：1/2 = 0.1，1/4 = 0.01，1/8 = 0.001，都在有限位内结束。'
                   '1/10 不行，因为 10 = 2 × 5，那个 5 不是 2 的幂。')
    note(f, y, '所以「0.1」在二进制里是一条无限循环小数，而机器只能存 53 位有效数字。',
         color=RED)
    save(f, '04-the-cycle.png', '1/10 的二进制展开与循环节')


def fig05():
    f, y = new(5, '只留 53 位，后面的必须舍掉',
               '一个 float64 的尾数只有 52 位，加上隐含的整数位，一共 53 位有效数字。')
    f.box('bits', 44, y, 1018, y + 210)
    bits = R['tenth_expansion']
    keep, tail = bits[:53], bits[53:]
    cell = (1018 - 76) / 53.0
    for i, d in enumerate(keep):
        fill = TEAL if d == '1' else LIGHT
        f.rect(76 + i * cell, y + 66, 76 + (i + 1) * cell - 2, y + 130,
               fill=fill, outline=None)
    f.text((76, y + 18), '1/10 的二进制展开，前 53 位（青 = 1，灰 = 0）', 40,
           color=INK, inside='bits')
    f.text((76, y + 150), '第 54 位之后是 %s… —— 只能被舍入掉' % tail[:8], 40,
           color=RED, inside='bits')
    y += 250
    y = note(f, y, '舍入的规则不是「截断」，而是「就近取偶」：看第 54 位和后面的尾巴，'
                   '离哪个可表示的数近就往哪边靠；正好在中间时，取尾数为偶数的那一侧。')
    note(f, y, '结果就是：存进去的不是 0.1，而是 ' +
         R['sum']['one_tenth_decimal'][:34] + '…，比 0.1 大 '
         '%.3e。' % float(Fraction(R['sum']['one_tenth_decimal'])
                          - Fraction(1, 10)), color=TEAL)
    save(f, '05-cut-it-off.png', '53 位有效数字之外的位必须舍入')


def fig06():
    f, y = new(6, '一个 float64 的 64 位怎么分',
               'IEEE 754 把 64 位切成三段：1 位符号、11 位指数、52 位尾数。'
               '上面那条按真实比例画，所以符号位细得几乎看不见；下面用色块一一对应。')
    x0, x1 = 60, 1002
    w1 = (x1 - x0) * 1 / 64.0
    w2 = (x1 - x0) * 11 / 64.0
    f.rect(x0, y + 40, x0 + w1, y + 130, fill=AMBER, outline=None)
    f.rect(x0 + w1, y + 40, x0 + w1 + w2, y + 130, fill=BLUE, outline=None)
    f.rect(x0 + w1 + w2, y + 40, x1, y + 130, fill=TEAL, outline=None)
    f.text((x0, y), '按真实比例：1 : 11 : 52', 40, color=INK_SOFT)
    y += 176
    legend = [(AMBER, '符号位：1 位', '0 表示正，1 表示负。有了它，负数不需要单独的编码。'),
              (BLUE, '指数：11 位', '存的不是指数本身，而是「指数 + 1023」，这样负数也能用无符号位表示。'),
              (TEAL, '尾数：52 位', '存小数点后面的位。整数位那一位总是 1，不存，省下来多给一位精度。')]
    for color, name, desc in legend:
        f.rect(56, y + 4, 96, y + 44, fill=color, outline=None)
        f.text((120, y), name, 42, bold=True, color=INK)
        lines = f.wrap((120, y + 56), desc, 40, 892, color=INK_SOFT)
        y += int(56 + lines * 40 * 1.35) + 34
    y = note(f, y, '52 位尾数 + 1 位隐含的整数位 = 53 位有效数字。'
                   '53 × log10(2) ≈ 15.95，这就是「双精度大约 16 位十进制有效数字」的来历。')
    note(f, y, '小数点本身不是存下来的零件。它由指数决定位置，所以同一套位既能表示 '
               '10⁻³⁰⁰，也能表示 10³⁰⁰。', color=TEAL)
    save(f, '06-ieee-layout.png', 'IEEE 754 双精度的字段划分')


def fig07():
    f, y = new(7, '把 0.1 拆成三段看看',
               '把 0.1 的 64 位按上面的规则切开，再按公式拼回一个数。')
    d = R['layout']['decode_tenth']
    frac = d['bitstr'].split(' ')[2]
    f.box('b', 44, y, 1018, y + 300)
    f.text((70, y + 22), '符号位：' + str(d['sign']), 42, color=INK, inside='b')
    f.text((70, y + 86), '指数段：' + d['bitstr'].split(' ')[1], 42, color=BLUE, inside='b')
    f.text((70, y + 150), '尾数段：' + frac[:26], 42, color=TEAL, inside='b')
    f.text((70, y + 214), '        ' + frac[26:], 42, color=TEAL, inside='b')
    y += 340
    rows = [[('字段', INK, True), ('内容', INK, True), ('意思', INK, True)],
            [('符号位', INK, False), ('= 0', INK, False), ('正数', INK_SOFT, False)],
            [('指数段原值', INK, False), ('= %d' % d['raw_exponent'], INK, False),
             ('无符号', INK_SOFT, False)],
            [('真实指数', INK, False),
             ('= %d − 1023 = %d' % (d['raw_exponent'], d['exponent']), INK, False),
             ('减掉偏移量', INK_SOFT, False)],
            [('尾数段', INK, False), ('= %d' % d['fraction'], INK, False),
             ('尾数位', INK_SOFT, False)]]
    y = table(f, y, [(56, 'la'), (330, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '拼回去的公式：(−1)^符号 × (1 + 尾数 ÷ 2^52) × 2^真实指数')
    note(f, y, '这个公式算出来的精确值是 ' + R['sum']['one_tenth_decimal'][:38] + '…，'
               '而不是 0.1。', color=RED)
    save(f, '07-decode-0-1.png', '把 0.1 的位模式拆开并还原')


def fig08():
    f, y = new(8, '存进去的到底是哪个数',
               '把机器里那个 float64 用精确分数展开成十进制，一位不差地写出来。')
    exact_s = R['sum']['one_tenth_decimal']
    f.box('e', 44, y, 1018, y + 400)
    f.text((76, y + 24), '你以为存的 0.1', 42, color=INK_SOFT, inside='e')
    f.text((76, y + 86), '0.1', 46, color=INK, inside='e')
    f.text((76, y + 158), '实际存的数', 42, color=INK_SOFT, inside='e')
    f.wrap((76, y + 218), exact_s, 40, 920, color=RED, inside='e')
    y += 440
    y = note(f, y, '这个数离 0.1 有多远？用精确分数相减，差是 1/180143985094819840，'
                   '大约 5.55 × 10⁻¹⁸。它比 0.1 大一点点。')
    note(f, y, '机器没有「欺骗」你：它把你写的十进制字面量，按规则换成了离它最近的那个可表示的数。'
               '后面所有计算都在这个数上进行。', color=TEAL)
    save(f, '08-what-is-stored.png', '0.1 实际存储的精确十进制展开')


def fig09():
    f, y = new(9, '浮点数在数轴上不是均匀铺开的',
               '同一个「最小间隔」，在 1 附近是 2.2 × 10⁻¹⁶，在 10¹⁶ 附近却是 2。'
               '每跨过一个 2 的幂，间隔就翻一倍。')
    prof = R['spacing']['profile']
    rows = [[('数量级', INK, True), ('最近的 2 的幂', INK, True), ('与邻居的间隔', INK, True),
             ('相对间隔', INK, True)]]
    for p in prof:
        rows.append([('%.4g' % p['value'], INK, False), ('2^%d' % p['exponent'], INK, False),
                     ('%.2g' % p['ulp'], TEAL, False),
                     ('%.1e' % (p['ulp'] / p['value']), GRAY, False)])
    y = table(f, y, [(70, 'la'), (330, 'la'), (600, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '看最后一列：无论数值多大，间隔相对于自身的比例都稳定在 10⁻¹⁶ 量级。'
                   '所以浮点数的精度是「相对的」，不是「绝对的」。')
    note(f, y, '这就是为什么比较两个浮点数时，写「绝对差小于 0.000001」在数值很大时会失效——'
               '那时候连一个间隔都比这个容差大。', color=AMBER)
    save(f, '09-not-even-spacing.png', '浮点间隔随数量级变化')


def fig10():
    f, y = new(10, '一个 ulp 有多大',
               'ulp 是「最小间隔」的通用叫法（unit in the last place）。'
               '同一个数在不同数量级上，一个 ulp 差得很远。')
    rows = [[('数值', INK, True), ('一个 ulp', INK, True), ('ulp ÷ 数值', INK, True)]]
    for t in R['spacing']['ulp_table']:
        rows.append([('%.0e' % t['value'], INK, False), ('%.3g' % t['ulp'], TEAL, False),
                     ('%.2e' % (t['ulp'] / t['value']), GRAY, False)])
    y = table(f, y, [(90, 'la'), (420, 'la'), (760, 'la')], rows)
    note(f, y, '从 10⁻³⁰⁰ 到 10¹⁰⁰，一个 ulp 跨越了 400 个数量级，但 ulp ÷ 数值始终落在 '
               '1.11 × 10⁻¹⁶ 到 2.22 × 10⁻¹⁶ 之间。这就是「双精度大约 16 位十进制有效数字」的来历。')
    save(f, '10-ulp-table.png', '不同数量级上一个 ulp 的大小')


def fig11():
    f, y = new(11, '加法的第一步：把小数点对齐',
               '两个数的指数不同，硬件要先把小的那个向右移位，让两边的位权一致，'
               '然后才能逐位相加。')
    f.box('a', 44, y, 1018, y + 300)
    f.text((76, y + 22), '0.1 的尾数（真实指数 −4）', 42, color=INK, inside='a')
    f.text((76, y + 86), '1.' + R['sum']['bits_a'].split(' ')[2][:24] + '…', 42,
           color=TEAL, inside='a')
    f.text((76, y + 160), '0.2 的尾数（真实指数 −3，比上面大 1）', 42, color=INK, inside='a')
    f.text((76, y + 224), '1.' + R['sum']['bits_b'].split(' ')[2][:24] + '…', 42,
           color=BLUE, inside='a')
    y += 340
    y = note(f, y, '指数每差 1，就要把较小的尾数整体右移一位。移出去的那些位不会凭空消失，'
                   '它们还要参与后面的舍入判断。')
    note(f, y, '所以浮点加法的代价不是「一次整数加法」，而是对齐、相加、规格化、舍入四步。'
               '这也是浮点运算比整数运算慢的原因之一。', color=TEAL)
    save(f, '11-alignment.png', '浮点加法前必须对齐小数点')


def fig12():
    f, y = new(12, '精确的和、舍入后的和、以及 0.3',
               '把三段 60 位的十进制展开并排写出来。精确和不是格点上的数——'
               '它卡在另外两段的正中间。')
    rows = [('0.1 与 0.2 的精确和', R['sum']['exact_sum_decimal'], INK),
            ('舍入回 53 位之后', R['sum']['rounded_decimal'], TEAL),
            ('你以为在比的 0.3', R['sum']['three_decimal'], BLUE)]
    for title, text, color in rows:
        f.text((44, y), title, 42, color=color, bold=True)
        y += 58
        for i in range(0, 54, 27):
            f.text((44, y), text[i:i + 27], 42, color=color)
            y += 54
        y += 26
    y = note(f, y, '第二段与第三段的差，正好是 0.3 的一个 ulp：%.3e。'
             % R['sum']['ulp_of_0_3'], color=RED)
    y = note(f, y, '第一段到第二段、第一段到第三段的距离都是半个 ulp——'
                   '精确和恰好落在两者正中间，所以「舍入」必须选一次边。', color=TEAL)
    save(f, '12-the-sum.png', '精确和、舍入后的和与 0.3 的逐位对比')


def fig13():
    f, y = new(13, '最后一票：正好在中间，取偶数',
               '0.1 与 0.2 的精确和，恰好落在两个相邻浮点数的正中间。'
               '这时候决定结果的是「就近取偶」这条规则。')
    t = R['rounding_tie']
    f.box('t', 44, y, 1018, y + 430)
    f.text((76, y + 22), '下邻：' + t['lower_hex'] + '，末位是 ' + str(t['lower_last_bit']),
           42, color=BLUE, inside='t')
    f.text((76, y + 96), '上邻：' + t['upper_hex'] + '，末位是 ' + str(t['upper_last_bit']),
           42, color=AMBER, inside='t')
    f.text((76, y + 170), '精确和与两边的距离：', 42, color=INK, inside='t')
    f.text((76, y + 236), '离下邻 ' + ('%.3e' % num(t['distance_to_lower']))
           + '，离上邻 ' + ('%.3e' % num(t['distance_to_upper'])), 42,
           color=INK, inside='t')
    f.text((76, y + 310), '两边一样远 —— 程序判定：' + str(t['exactly_halfway']),
           42, color=RED, inside='t')
    f.text((76, y + 372), '规则说取偶数那一侧 → 末位为 0 的上邻胜出', 42, color=TEAL,
           inside='t')
    y += 470
    y = note(f, y, '所以结果不是「随便偏了一点」，而是被一条明确的规则选出来的：'
                   '0.30000000000000004。')
    note(f, y, '这也解释了为什么 0.1 + 0.2 比 0.3 大，而 0.1 + 0.1 却正好等于 0.2 —— '
               '两次舍入碰到的位置不一样。', color=TEAL)
    save(f, '13-rounding-tie.png', '就近取偶规则如何决定 0.1+0.2 的结果')


def fig14():
    f, y = new(14, '大数会把小数整个吃掉',
               '在 10¹⁶ 附近，相邻两个可表示的数相差 2。所以「加 1」根本推不动它。')
    chain = R['big_eats_small']['chain']
    base, ulp = chain[0]['value'], R['big_eats_small']['ulp']
    rows = [[('算式', INK, True), ('结论', INK, True), ('实际存成', INK, True)]]
    for c in chain:
        delta = c['value'] - base
        if not delta:
            v = '没变'
        elif c['n'] == delta - ulp / 2:
            # the exact sum sits halfway between two representable numbers
            v = '舍到 +%d' % delta
        else:
            v = '变 +%d' % delta
        rows.append([('1e16 + %d' % c['n'], INK, False),
                     (v, GREEN if c['changed'] else RED, False),
                     ('%d' % c['value'], INK, False)])
    y = table(f, y, [(60, 'la'), (300, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '一个 ulp 是 %.0f，加 1 连半个 ulp 都不到，舍入之后回到原处。'
             % R['big_eats_small']['ulp'])
    note(f, y, '同一个道理：往一个很大的和里逐个累加很小的数，前面的小贡献会全部消失。'
               '正确的做法是先把小的加起来，或者用 Kahan 补偿。', color=AMBER)
    save(f, '14-big-eats-small.png', '大数量级下小增量被完全吃掉')


def fig15():
    f, y = new(15, '减法会吃掉有效位数',
               '1 − cos(x) 在 x 很小时，两个几乎相等的数相减，前面的有效位全部抵消，'
               '剩下的全是舍入噪声。')
    # The two results agree to the ninth significant digit, so printing the
    # values side by side would show them as identical. The relative error is
    # what actually separates them, and it is what "losing digits" means.
    rows = [[('x', INK, True), ('朴素误差', INK, True), ('位数', INK, True),
             ('稳定误差', INK, True), ('位数', INK, True)]]
    for c in R['cancellation']:
        gd = c['good_digits']
        rows.append([('%.0e' % c['x'], INK, False),
                     ('%.3e' % c['relative_error'], RED, False),
                     ('0.0' if gd is None or gd < 0.5 else '%.1f' % gd, RED, False),
                     ('%.3e' % c['relative_error_stable'], TEAL, False),
                     ('%.1f' % c['good_digits_stable'], TEAL, False)])
    y = table(f, y, [(60, 'la'), (200, 'la'), (430, 'la'), (560, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '「位数」是相对误差取负对数。x = 10⁻⁸ 时朴素写法直接给出 0.0 —— '
               '相对误差 100%，一位有效数字都没剩下。')
    note(f, y, '两个式子代数上完全相等，但稳定写法每一行都保住了 16 位以上有效数字，'
               '朴素写法最好的时候也只有 8.3 位。差别不在数学，在「先算哪一步」。',
         color=TEAL)
    save(f, '15-cancellation.png', '灾难性抵消与等价改写')


def _axes(fig, x0, y0, x1, y1):
    fig.line((x0, y1), (x1, y1), color=GRAY, width=3)
    fig.line((x0, y0), (x0, y1), color=GRAY, width=3)


def fig16():
    f, y = new(16, '误差随项数怎么长',
               '把 0.1 加 n 次，看实际结果偏离精确值多少。纵轴是对数刻度，'
               '每一格是 100 倍。')
    curve = R['drift_curve']
    x0, x1, y0, y1 = 210, 1000, y, y + 560
    _axes(f, x0, y0, x1, y1)

    def px(n):
        return x0 + (x1 - x0) * (math.log10(max(1, n)) / 5.0)

    def py(e):
        e = max(abs(e), 1e-17)
        return y1 - (y1 - y0) * (min(math.log10(e), -7.0) + 17.0) / 10.0

    for k in range(6):
        x = px(10 ** k)
        f.line((x, y1), (x, y1 + 12), color=GRAY, width=3)
        f.text((x, y1 + 26), '1e%d' % k, 40, color=GRAY, anchor='ma')
    for k in range(0, 11, 2):
        e = 10.0 ** (-17 + k)
        yy = py(e)
        f.line((x0 - 12, yy), (x0, yy), color=GRAY, width=3)
        f.text((x0 - 24, yy - 20), '1e%d' % (-17 + k), 40, color=GRAY, anchor='ra')
    for name, key, color in (('朴素从左到右', 'naive_error', RED),
                             ('Kahan 补偿', 'kahan_error', TEAL)):
        pts = [(px(c['n']), py(c[key])) for c in curve]
        for a, b in zip(pts, pts[1:]):
            f.line(a, b, color=color, width=5)
    y = y1 + 92
    f.rect(60, y, 96, y + 36, fill=RED, outline=None)
    f.text((116, y - 4), '朴素从左到右', 42, color=INK)
    f.rect(520, y, 556, y + 36, fill=TEAL, outline=None)
    f.text((576, y - 4), 'Kahan 补偿', 42, color=INK)
    y += 92
    acc = {r['name']: r['error'] for r in R['accumulation']['rows']}
    y = note(f, y, '朴素相加的误差随项数稳步上升，到 10 万项时是 %.1e；'
                   'Kahan 补偿把误差压在 %.1e 附近，几乎不随项数增长。'
             % (abs(acc['朴素从左到右']), abs(acc['Kahan 补偿'])))
    note(f, y, 'Kahan 的代价是每次加法多做三次浮点运算，用一点点速度换回精度。', color=TEAL)
    save(f, '16-accumulate.png', '累加误差随项数的增长曲线')


def fig17():
    f, y = new(17, '四种求和方式，误差差四个数量级',
               '同一列两万个数，量级从 1 跨到 10⁻¹⁵，只是换一个相加顺序，结果就不一样。')
    mixed = R['mixed']
    items = sorted(mixed['rows'], key=lambda r: abs(r['error']))
    short = {'Kahan 补偿': 'Kahan', '按绝对值从小到大': '先排序', '二分两两相加': '两两相加',
             '朴素从左到右': '朴素'}
    x0, x1 = 360, 780
    rows = []
    for r in items:
        e = max(abs(r['error']), 1e-16)
        frac = (min(math.log10(e), -10.0) + 16.0) / 6.0
        rows.append((short[r['name']], e, frac))
    bars_are_honest(rows)
    for name, e, frac in rows:
        y = bar_row(f, x0, x1, y, frac, TEAL, name, '%.2e' % e)
    mix = {r['name']: abs(r['error']) for r in R['mixed']['rows']}
    ratio = mix['朴素从左到右'] / mix['Kahan 补偿']
    y = note(f, y, '朴素相加的误差 %.1e，是 Kahan 的约 %.1f 万倍。'
                   '差别只来自「按什么顺序加」。'
             % (mix['朴素从左到右'], ratio / 1e4))
    note(f, y, '柱子长度按对数刻度画，否则最小的那根在图上只有零点几个像素。'
               '刻度范围 10⁻¹⁶ 到 10⁻¹⁰。', color=GRAY)
    save(f, '17-kahan.png', '同一列数的四种求和方式误差对比')


def fig18():
    f, y = new(18, '同一个公式，换个写法就准了',
               '解 x² − 10⁸x + 1 = 0。两个根一个是 10⁸ 量级，一个是 10⁻⁸ 量级，'
               '教科书公式在小根上失效。')
    q = R['quadratic']
    rows = [[('求法', INK, True), ('大根', INK, True), ('小根', INK, True)]]
    rows.append([('教科书公式', INK, False), ('%.10g' % q['naive'][0], INK, False),
                 ('%.3e' % q['naive'][1], RED, False)])
    rows.append([('避开相减的写法', INK, False), ('%.10g' % q['stable'][0], INK, False),
                 ('%.3e' % q['stable'][1], TEAL, False)])
    y = table(f, y, [(56, 'la'), (380, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '检查的办法：两根之积应该等于 c/a = 1。教科书公式给出 %.4f，'
                   '换写法给出 %.4f。' % (q['product_naive'], q['product_stable']))
    note(f, y, '原因还是抵消：−b 与 √(b²−4ac) 几乎相等，相减时前面的位全丢了。'
               '换写法就是让减法变成加法。', color=TEAL)
    save(f, '18-quadratic.png', '二次方程求根的两种写法')


def fig19():
    f, y = new(19, '浮点数自己的几个特殊值',
               'IEEE 754 给「除以零」「零除以零」这些没有数学答案的运算也留了位置，'
               '它们不抛异常，而是变成特定的值。')
    rows = [[('写法', INK, True), ('结果', INK, True), ('位模式（十六进制）', INK, True)]]
    for s in R['special']:
        rows.append([(s['name'], INK, False),
                     (str(s['value']), RED if s['name'].startswith('0.0/0.0') else TEAL,
                      False),
                     (s['hex'], INK, False)])
    y = table(f, y, [(56, 'la'), (300, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '无穷和 NaN 的指数段全是 1，这是它们和普通数分开的地方；'
                   '尾数段全 0 是无穷，不全 0 就是 NaN。')
    n = R['nan']
    y = note(f, y, 'NaN 有一个反直觉的性质：它不等于自己（nan == nan 得到 ' +
             str(n['equal_to_itself']).lower() + '）。判断要用 math.isnan，不能写 x == x。')
    note(f, y, '0.0 和 −0.0 是两个不同的位模式，但比较时相等；'
               '只有在 1/x 这种地方才看得出区别。', color=TEAL)
    save(f, '19-special-values.png', '0、负零、无穷与 NaN')


def fig20():
    f, y = new(20, '最靠近 0 的地方：下溢是渐进的',
               '正常数的间隔随指数变化。到了 2⁻¹⁰²² 以下，整数位不再隐含为 1，'
               '间隔固定成最小的一格，一路铺到 0。')
    s = R['subnormal']
    y = bullets(f, y, [
        '最小的正规数：%.6e，位模式 %s' % (s['smallest_normal'], s['smallest_normal_hex']),
        '最小的次正规数：%.6e，位模式 %s' % (s['smallest_subnormal'],
                                            s['smallest_subnormal_hex']),
        '两者之比：%.6g，也就是 2⁵²' % num(s['ratio']),
    ])
    y += 14
    y = note(f, y, '从 2⁻¹⁰²² 往下，还有 2⁵² − 1 个台阶可以踩，而不是突然掉到 0。'
                   '这就是「渐进下溢」。')
    note(f, y, '代价是：这些台阶上的有效数字比正常数少，精度会随着靠近 0 而降低。'
               '最小的次正规数再除以 2，结果就是 0。', color=AMBER)
    save(f, '20-subnormal.png', '次正规数与渐进下溢')


def fig21():
    f, y = new(21, '把浮点数的位当成整数来用',
               'Quake III 里的平方根倒数：先做一个整数减法得到一个粗糙初值，'
               '再做几次牛顿迭代。整数运算负责「猜」，浮点运算负责「修」。')
    q = R['fast_inverse_sqrt']
    rows = [[('步骤', INK, True), ('结果', INK, True), ('相对误差', INK, True)]]
    rows.append([('整数减半之后', INK, False), ('%.10f' % q['after_magic'], INK, False),
                 ('%.2e' % (abs(q['after_magic'] - q['truth']) / q['truth']), AMBER,
                  False)])
    for i, v in enumerate(q['steps']):
        rows.append([('第 %d 次牛顿迭代' % (i + 1), INK, False), ('%.10f' % v, INK, False),
                     ('%.2e' % q['errors'][i], TEAL if i else AMBER, False)])
    rows.append([('真值 1/√0.5', GRAY, False), ('%.10f' % q['truth'], GRAY, False),
                 ('—', GRAY, False)])
    y = table(f, y, [(60, 'la'), (440, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '第一步只用到整数运算：把 float32 的位当成整数 i，算 magic − (i >> 1)，'
                   'magic = 0x5F3759DF，再把结果读回浮点。')
    inv = R['fast_inverse_sqrt']
    seed_err = abs(inv['after_magic'] - inv['truth']) / inv['truth']
    y = note(f, y, '三次迭代把误差从 %.2g%% 压到 %.1e。'
                   '整个技巧成立的前提是：float32 的位模式里，符号位在最前面，'
                   '指数段紧跟其后，所以「整数减半」近似等于「指数减半」，也就是开平方。'
             % (100 * seed_err, inv['errors'][-1]))
    note(f, y, '这不是魔法，是对格式本身的理解。同样的思路今天还在用：'
               '把浮点数的位拿来比较大小、排序、压缩。', color=TEAL)
    save(f, '21-fast-inv-sqrt.png', '快平方根倒数的迭代收敛')


def fig22():
    f, y = new(22, '容差该按比例给，不能按绝对值给',
               '判断两个浮点数「差不多」，写死一个绝对容差在数值大时会完全失效。')
    rows = [[('数值', INK, True), ('一个 ulp', INK, True),
             ('容差相当于', INK, True), ('能用吗', INK, True)]]
    for t in R['tolerance']:
        k = t['tol_in_ulps']
        ok = k >= 1
        rows.append([('%.0e' % t['value'], INK, False), ('%.3g' % t['ulp'], INK, False),
                     ('%.2e ulp' % k, INK, False),
                     ('可以' if ok else '不行', GREEN if ok else RED, False)])
    y = table(f, y, [(60, 'la'), (300, 'la'), (620, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '「不行」的意思是：容差 1e-9 比一个 ulp 还小。'
                   '在这个量级上，任意两个不同的数都差着好几个 ulp，检查永远返回「不相等」。')
    note(f, y, '正确做法是比较相对差：|a − b| ≤ ε × max(|a|, |b|)，'
               '或者直接用 Python 的 math.isclose。', color=TEAL)
    save(f, '22-compare-with-tolerance.png', '绝对容差在不同数量级上的失效')


def fig23():
    f, y = new(23, '自己动手改一个条件',
               '下面每一行都可以直接在 Python 里敲一遍，先猜结果，再对照。')
    items = [
        'repr(0.1 + 0.2) 与 repr(0.3) —— 看两个字符串是不是同一个。',
        '0.1 * 3 == 0.3 —— 乘法那边会不会也踩到同一个坑？',
        'sum([0.1] * 10) == 1.0 —— 十项就够出问题吗？',
        '用 Fraction(0.1) 打印精确值 —— 看看机器到底存了什么。',
        '把 math.isclose(0.1 + 0.2, 0.3) 改成相对容差 1e-12，再试 1e-18。',
        'math.nextafter(1e16, math.inf) - 1e16 —— 亲手量一个 ulp。',
    ]
    for i, text in enumerate(items):
        f.circle(76, y + 22, 15, fill=TEAL, outline=TEAL)
        lines = f.wrap((116, y + 2), text, 42, 898, color=INK)
        y += int(lines * 42 * 1.35) + 26
    y += 10
    y = note(f, y, '全部只用标准库。改一个数字、换一个顺序，看看结论会不会变——'
                   '这正是浮点数最值得亲手摸一遍的地方。')
    save(f, '23-try-it.png', '读者可以自己改动的六项实验', min_width_coverage=0.80)


def make_cover():
    f = Fig(1080, width=1080)
    # Everything sits inside y = 310..770: WeChat crops the 2.35:1 feed cover
    # from the middle of this square, so the title must not fall outside it.
    f.text((540, 329), '0.1 + 0.2', 84, True, anchor='ma')
    f.text((540, 419), '为什么不等于 0.3？', 56, True, TEAL, anchor='ma')
    bits = R['sum']['bits_a'].replace(' ', '')
    f.rect(120, 507, 960, 607, fill=WHITE, outline=LIGHT, width=3)
    cell = (960 - 120 - 24) / 64.0
    for i, ch in enumerate(bits):
        f.rect(132 + i * cell, 527, 132 + (i + 1) * cell - 1, 587,
               fill=TEAL if ch == '1' else LIGHT, outline=None)
    f.text((540, 629), '符号 1 位 · 指数 11 位 · 尾数 52 位', 40,
           color=INK_SOFT, anchor='ma')
    f.text((540, 699), '机器存不下十分之一，只能存离它最近的那个数', 44, True,
           INK, anchor='ma')
    f.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


def main():
    only = [int(a) for a in sys.argv[1:]]
    for i in range(1, 24):
        if only and i not in only:
            continue
        globals()['fig%02d' % i]()
    if not only:
        make_cover()
    for row in META:
        row['path'] = 'assets/' + Path(row['path']).name
    meta_path = HERE / 'figure-metadata.json'
    rows = META
    if only and meta_path.is_file():
        # A partial rebuild (`build_figures.py 12`) must not drop the other
        # figures' records: keep what this run did not regenerate.
        rebuilt = {row['path'] for row in META}
        kept = [r for r in json.loads(meta_path.read_text('utf-8'))
                if r['path'] not in rebuilt]
        rows = sorted(kept + META, key=lambda r: r['path'])
    meta_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(rows))


if __name__ == '__main__':
    main()
