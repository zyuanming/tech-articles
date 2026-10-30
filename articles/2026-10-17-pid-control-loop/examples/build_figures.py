#!/usr/bin/env python3
"""Original teaching figures for the PID article. MIT.

Every curve is read from results.json, which run_model.py produced by actually
simulating the loop. Nothing is sketched by hand.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

from figkit import (Fig, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED, GRAY,
                    LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R, TINT_G)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
META = []
SP = R['setpoint']


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


def table(fig, y, cols, rows, size=40, row_h=68, head=True, zebra=True):
    for i, row in enumerate(rows):
        if zebra and i % 2 == 1:
            fig.rect(48, y - 10, 1014, y + row_h - 12, fill=PALE, outline=None)
        for (text, color, bold), (x, anchor) in zip(row, cols):
            w = fig.width_of(text, size, bold)
            span = (x, x + w) if anchor == 'la' else (x - w, x)
            assert span[0] >= 44 and span[1] <= 1018, \
                'cell outside the safe band: %r %s' % (text, span)
            fig.text((x, y + 4), text, size, bold=bold, color=color,
                     anchor=anchor)
        y += row_h
    return y + 18


class Plot:
    """A tiny linear-axes plotter with the label sizes this series needs."""

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
             ylab=None):
        for v in yticks:
            yy = self.py(v)
            self.f.line((self.x0, yy), (self.x1, yy), color=LIGHT, width=2)
            self.f.text((self.x0 - 18, yy - 21), yfmt % v, 40, color=GRAY,
                        anchor='ra')
        for v in xticks:
            xx = self.px(v)
            self.f.line((xx, self.y0), (xx, self.y1), color=LIGHT, width=2)
            self.f.text((xx, self.y1 + 14), xfmt % v, 40, color=GRAY,
                        anchor='ma')
        self.f.line((self.x0, self.y1), (self.x1, self.y1), color=GRAY, width=3)
        self.f.line((self.x0, self.y0), (self.x0, self.y1), color=GRAY, width=3)
        if ylab:
            self.f.text((self.x0, self.y0 - 58), ylab, 40, color=GRAY)
        if xlab:
            self.f.text((self.x1, self.y1 + 74), xlab, 40, color=GRAY,
                        anchor='ra')

    def line(self, xs, ys, color, width=5, dash=None):
        pts = [(self.px(x), self.py(y)) for x, y in zip(xs, ys)]
        for a, b in zip(pts, pts[1:]):
            self.f.line(a, b, color=color, width=width, dash=dash)

    def hline(self, y, color=GRAY, dash=14):
        self.f.line((self.x0, self.py(y)), (self.x1, self.py(y)), color=color,
                    width=3, dash=dash)

    def label(self, x, y, text, color, anchor='la', bold=False):
        self.f.text((self.px(x), self.py(y)), text, 40, color=color,
                    anchor=anchor, bold=bold)


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def single(fig, y, title, ylim, yticks, xmax, xticks, ylab='温度 / °C',
           xfmt='%g', height=400):
    """One panel with a title above it, returning the y to carry on from."""
    f = fig
    f.text((44, y), title, 42, bold=True, color=INK)
    y0 = y + 130
    p = Plot(f, (212, y0, 1000, y0 + height), (0, xmax), ylim)
    p.axes(xticks=xticks, yticks=yticks, yfmt='%g', ylab=ylab, xfmt=xfmt,
           xlab='时间 / s')
    return y0 + height + 130, p


def key_row(fig, items, right=1000, y=0, sample=56, gap=34, size=40):
    """A horizontal key for a plot: a colour sample followed by its label."""
    widths = [sample + 16 + fig.width_of(text, size) for _, text in items]
    x = right - (sum(widths) + gap * (len(items) - 1))
    for (color, text), w in zip(items, widths):
        fig.line((x, y + 22), (x + sample, y + 22), color=color, width=6)
        fig.text((x + sample + 16, y), text, size, color=INK)
        x += w + gap


def response(fig, y, curve, title, ylim=(20, 100), yticks=(20, 40, 60, 80, 100),
             xmax=800, xticks=(0, 200, 400, 600, 800), show_u=True,
             xfmt='%g', colors=None, extra=()):
    """Two stacked panels: the temperature, and the control signal under it."""
    f = fig
    f.text((44, y), title, 42, bold=True, color=INK)
    ty0 = y + 130
    ty1 = ty0 + 300
    top = Plot(f, (212, ty0, 1000, ty1), (0, xmax), ylim)
    top.axes(xticks=(), yticks=yticks, yfmt='%g', ylab='温度 / °C')
    by0 = ty1 + 112
    by1 = by0 + 220
    bot = Plot(f, (212, by0, 1000, by1), (0, xmax), (0, 1.05))
    bot.axes(xticks=xticks, yticks=(0, 0.5, 1.0), yfmt='%g', ylab='加热功率',
             xfmt=xfmt, xlab='时间 / s')
    for xs, ys, color, width in extra:
        top.line(xs, ys, color, width)
    top.hline(SP, color=GRAY, dash=16)
    top.line(curve['t'], curve['y'], colors or TEAL, 5)
    if show_u:
        bot.line(curve['t'], curve['u'], colors or AMBER, 4)
    return by1 + 130, top, bot


# ------------------------------------------------------------------- figures
def fig01():
    f, y = new(1, '闭环比开环多了什么',
               '开环控制是「按经验给一个值」，闭环控制是「先看结果，再改动作」。'
               '自动控制的全部秘密就在那条从输出回到输入的线上。')
    stages = [
        ('设定值', '希望达到的温度：80 °C'),
        ('比较', '误差 e = 设定值 − 测量值'),
        ('控制器', 'u = Kp·e + Ki·∫e dt + Kd·de/dt'),
        ('执行器', '把 u 变成 0 到 1 之间的加热功率'),
        ('被控对象', '炉子：两级滞后，见下一节'),
        ('输出', '传感器读到的温度 T₂'),
    ]
    x0, x1 = 60, 900
    for i, (name, desc) in enumerate(stages):
        h = 150
        fill = TINT_T if i == 2 else WHITE
        f.box('s%d' % i, x0, y, x1, y + h, fill=fill)
        f.text((88, y + 22), name, 42, bold=True, color=INK, inside='s%d' % i)
        f.text((88, y + 84), desc, 40, color=INK_SOFT, inside='s%d' % i)
        if i < len(stages) - 1:
            f.arrow((480, y + h + 8), (480, y + h + 52), color=GRAY, width=4)
        y += h + 60
    top = y - 60 - 150
    f.line((900, y - 210 + 75), (960, y - 210 + 75), color=TEAL, width=4)
    f.line((960, y - 210 + 75), (960, 150 + 60 + 75), color=TEAL, width=4)
    f.arrow((960, 150 + 60 + 75), (900, 150 + 60 + 75), color=TEAL, width=4)
    f.text((930, top - 4), '反馈', 40, color=TEAL, anchor='ma')
    y += 20
    y = note(f, y, 'PID 就是「控制器」那个方块。它只做一件事：把误差变成执行器的动作。'
                   '三个字母对应三种利用误差的方式——现在差多少、过去累计差了多少、'
                   '误差正在往哪边变。')
    y = note(f, y, '反馈那一条线是整个系统的关键。把它剪断，剩下的部分就是开环：'
               '设定值给出去，没人回头看结果。', color=TEAL)
    save(f, '01-open-vs-closed.png', '开环与闭环控制的差别')


def fig02():
    f, y = new(2, '最原始的办法：只有开和关',
               '恒温器就是这样的：低于设定值就全功率加热，到了就关掉。'
               '它不需要任何参数，但它一定会来回震荡。')
    m = R['onoff']['metrics']
    y, top, bot = response(f, y, R['onoff']['curve'], '开关控制的响应',
                           ylim=(20, 100))
    top.label(20, 92, '超调 %.1f%%' % m['overshoot'], RED)
    y = note(f, y, '因为加热器只有「全开」和「全关」两档，温度只能绕着设定值来回过冲。'
                   '要让它稳下来，就得让动作随着误差的大小连续变化——这就是 P。')
    save(f, '02-on-off.png', '开关控制为什么必然震荡')


def fig03():
    f, y = new(3, '先造一个能跑的炉子',
               '后面所有实验都作用在同一个模型上。它足够简单，能算；'
               '也足够真实，会震荡、会饱和、会受延迟影响。')
    f.box('eq', 60, y, 1002, y + 320)
    f.text((90, y + 24), 'dT₁/dt = (K·u − (T₁ − T_room)) / τ₁', 42, color=INK, inside='eq')
    f.text((90, y + 92), 'dT₂/dt = (T₁ − T₂) / τ₂', 42, color=INK, inside='eq')
    f.text((90, y + 176), 'K = 200，τ₁ = 60 s，τ₂ = 20 s', 42,
           color=INK_SOFT, inside='eq')
    f.text((90, y + 240), 'T_room = 20 °C，u 限制在 0 到 1 之间', 42,
           color=INK_SOFT, inside='eq')
    y += 380
    y = bullets(f, y, [
        'T₁ 是加热元件的温度，T₂ 是传感器读到的温度。两级滞后串在一起，'
        '这是能产生震荡的最小模型。',
        'u = 1 时炉子最终到 220 °C。要稳在 80 °C，稳态功率是 0.3。',
        '第二级滞后就是现实中「传感器比炉子慢」的那部分，它会让控制器看到的是旧消息。',
    ])
    save(f, '03-the-plant.png', '本文使用的加热模型')


def fig04():
    f, y = new(4, '只有 P：差得越多，加得越猛',
               '比例控制把误差乘以一个系数当作输出。系数越大反应越快，'
               '但无论多大，都消不掉最后那点偏差。')
    y, p = single(f, y, 'Kp 从 0.002 加到 0.15', (20, 100),
                  (20, 40, 60, 80, 100), 800, (0, 200, 400, 600, 800))
    p.hline(SP, color=GRAY, dash=16)
    shades = (LIGHT, GRAY, BLUE, AMBER, RED)
    for row, color in zip(R['p_only'], shades):
        p.line(row['curve']['t'], row['curve']['y'], color, 4)
    y = note(f, y, '曲线从浅到深对应 Kp = 0.002、0.008、0.02、0.06、0.15。'
                   'Kp 越大上升越快，但每条曲线都停在设定值下面。')
    y = note(f, y, '最后那点偏差叫稳态误差：Kp = 0.002 时是 42.9 °C，'
                   'Kp = 0.15 时还有 1.9 °C。它不会自己消失。', color=RED)
    save(f, '04-p-only.png', '比例控制：越快越接近，但总差一点')


def fig05():
    f, y = new(5, '稳态误差是从哪来的',
               '比例控制的输出正比于误差。可要让炉子稳在 80 °C，'
               '输出必须恰好是它该有的那个值。这两个要求会互相打架。')
    f.box('d', 60, y, 1002, y + 470)
    for i, line in enumerate([
            '稳态：控制器输出不再变化，u = Kp · e',
            '稳态：炉子也必须自洽，T2 = 20 + 200 · u',
            '而 e = SP - T2。三式联立，消去 u 和 T2：',
            'T2 = (20 + 200·Kp·SP) / (1 + 200·Kp)',
            'e = (SP - 20) / (1 + 200·Kp)',
            '所以 e = 60 / (1 + 200·Kp)']):
        f.text((90, y + 24 + i * 74), line, 42,
               color=RED if i >= 4 else INK, inside='d')
    y += 530
    rows = [[('Kp', INK, True), ('实测稳态误差', INK, True), ('公式预测', INK, True),
             ('上升时间', INK, True), ('超调', INK, True)]]
    for row in R['p_only']:
        m = row['metrics']
        rows.append([('%g' % row['kp'], INK, False),
                     ('%.4f °C' % m['steady_state_error'], RED, False),
                     ('%.4f' % (60.0 / (1 + 200.0 * row['kp'])), GRAY, False),
                     ('%s' % (m['rise_time'] if m['rise_time'] else '—'), INK, False),
                     ('%.1f%%' % m['overshoot'], INK, False)])
    y = table(f, y, [(60, 'la'), (250, 'la'), (540, 'la'), (740, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '最后一行的 60 就是设定值减室温（80 − 20）。'
                   '第三列是纯代数算出来的，第二列是模拟跑出来的：五行全部吻合到小数点后四位，'
                   '说明在这个模型里稳态误差确实只由 Kp 决定。')
    y = note(f, y, '顺带一个结论：只要 Kp 有限，误差就不为 0。想让 e 变小，'
               '只能让 Kp 趋于无穷——而那正是下一节要付出的代价。', color=RED)
    save(f, '05-steady-state-error.png', '比例控制的稳态误差公式与实测')


def fig06():
    f, y = new(6, 'Kp 太大的代价：开始晃',
               '把 Kp 一路加大，误差是变小了，但回路开始出现超调和振荡。'
               '快到一定程度，快本身就是问题。')
    rows = [[('Kp', INK, True), ('上升时间 / s', INK, True), ('超调', INK, True),
             ('峰値 / °C', INK, True)]]
    for row in R['p_only']:
        m = row['metrics']
        rows.append([('%g' % row['kp'], INK, False),
                     ('%s' % (m['rise_time'] if m['rise_time'] else '—'), INK, False),
                     ('%.1f%%' % m['overshoot'], RED if m['overshoot'] > 5 else INK, False),
                     ('%.1f' % m['peak'], INK, False)])
    y = table(f, y, [(60, 'la'), (330, 'la'), (620, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '上升时间从「根本没到」一路降到 27.6 s 就停住了——'
                   '再加大 Kp 也不会更快，因为加热功率已经顶到 1。')
    y = note(f, y, '超调却一直在涨：0% → 0% → 0% → 10.9% → 17.6%。'
               '这就是 P 控制的两难：要快就得大 Kp，要大 Kp 就得接受晃。', color=RED)
    save(f, '06-p-too-large.png', 'Kp 过大带来的超调')


def fig07():
    f, y = new(7, '加上 I：把历史账也算进去',
               '积分项累加过去的误差。只要还有偏差，它就一直往同一个方向加，'
               '直到偏差被抹平为止。')
    y, top, bot = response(f, y, R['tunings'][2]['curve'],
                           'P 加 I：误差归零，代价是超调', ylim=(20, 100))
    top.label(430, 96, '超调 %.1f%%' % R['tunings'][2]['metrics']['overshoot'], RED)
    y = note(f, y, '稳态误差从 4.6 °C 降到 0.48 °C，最终几乎为零。'
                   '代价是温度冲过了头：超调 %.1f%%，而且要多花几分钟才稳下来。'
             % R['tunings'][2]['metrics']['overshoot'])
    y = note(f, y, '原因在于积分项在升温过程中一直累积。等温度到了设定值，'
               '积分项里还存着「欠账」，于是继续加热，就冲过去了。', color=AMBER)
    save(f, '07-add-integral.png', '积分项消除稳态误差')


def fig08():
    f, y = new(8, '积分给得越多，冲得越远',
               'Ki 决定积分项累积的快慢。Ki 越大，误差抹平得越快，超调也越大。')
    y, p = single(f, y, 'Ki 从 0 加到 0.0004（Kp 固定为 0.06）', (20, 100),
                  (20, 40, 60, 80, 100), 800, (0, 200, 400, 600, 800))
    p.hline(SP, color=GRAY, dash=16)
    shades = (GRAY, LIGHT, TEAL, AMBER, RED)
    for row, color in zip(R['ki_sweep'], shades):
        p.line(row['curve']['t'], row['curve']['y'], color, 4)
    rows = [[('Ki', INK, True), ('稳态误差 / °C', INK, True), ('超调', INK, True),
             ('稳定时间 / s', INK, True)]]
    for row in R['ki_sweep']:
        m = row['metrics']
        rows.append([('%g' % row['ki'], INK, False),
                     ('%+.3f' % m['steady_state_error'], INK, False),
                     ('%.1f%%' % m['overshoot'], RED if m['overshoot'] > 10 else INK, False),
                     ('%s' % (m['settling_time'] if m['settling_time'] else '没稳下来'), INK, False)])
    y = table(f, y, [(60, 'la'), (300, 'la'), (620, 'la'), (1014, 'ra')], rows)
    y = note(f, y, 'Ki = 0 那一行就是纯 P：误差 4.6 °C，永不消失。'
               'Ki = 0.0004 时误差归零，但超调涨到 11.4%。')
    save(f, '08-ki-sweep.png', '积分增益对超调的影响')


def fig09():
    f, y = new(9, '再加上 D：看误差正在往哪边变',
               '微分项对误差的变化率起作用。误差在快速缩小的时候，'
               '它会主动把输出往下压——相当于提前松油门。')
    y, p = single(f, y, 'Kd 从 0 加到 2（Kp = 0.06，Ki = 0）', (20, 100),
                  (20, 40, 60, 80, 100), 800, (0, 200, 400, 600, 800))
    p.hline(SP, color=GRAY, dash=16)
    shades = (RED, AMBER, TEAL, BLUE, GRAY)
    for row, color in zip(R['kd_sweep'], shades):
        p.line(row['curve']['t'], row['curve']['y'], color, 4)
    rows = [[('Kd', INK, True), ('上升时间 / s', INK, True), ('超调', INK, True),
             ('稳态误差 / °C', INK, True)]]
    for row in R['kd_sweep']:
        m = row['metrics']
        rows.append([('%g' % row['kd'], INK, False),
                     ('%s' % (m['rise_time'] if m['rise_time'] else '—'), INK, False),
                     ('%.1f%%' % m['overshoot'], GREEN if m['overshoot'] < 0.01 else INK, False),
                     ('%.2f' % m['steady_state_error'], INK, False)])
    y = table(f, y, [(60, 'la'), (300, 'la'), (620, 'la'), (1014, 'ra')], rows)
    y = note(f, y, 'Kd 从 0 加到 0.5，超调就从 10.9% 掉到 0，上升时间只慢了 6 s。'
               '这就是 D 的作用：把「快」和「不冲过头」分开调。')
    y = note(f, y, '但稳态误差一点没变（都是 4.62 °C）——D 只看变化，'
               '对「一直差着的那一点」无能为力。', color=AMBER)
    save(f, '09-kd-sweep.png', '微分项压制超调')


def fig10():
    f, y = new(10, '四种组合摆在一起',
               '同一个炉子，同一个设定值，只换控制器的三项。'
               '每种组合缺什么，一眼就能看出来。')
    rows = [[('控制器', INK, True), ('上升时间 / s', INK, True), ('超调', INK, True),
             ('稳态误差 / °C', INK, True)]]
    for row in R['tunings']:
        m = row['metrics']
        rows.append([(row['name'], INK, False),
                     ('%s' % (m['rise_time'] if m['rise_time'] else '—'), INK, False),
                     ('%.2f%%' % m['overshoot'], INK, False),
                     ('%+.3f' % m['steady_state_error'],
                      GREEN if abs(m['steady_state_error']) < 0.05 else RED, False)])
    y = table(f, y, [(60, 'la'), (330, 'la'), (620, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '只有 P：有 4.6 °C 的偏差，还有 10.9% 的超调。')
    y = note(f, y, 'P 加 D：超调被压到 0，但偏差还是 4.6 °C。')
    y = note(f, y, 'P 加 I：偏差基本归零，但超调没解决。')
    y = note(f, y, 'PID：偏差 0.005 °C，超调 0.77%。三项各管一件事，'
               '这就是为什么它被用了上百年还没被换掉。', color=TEAL)
    save(f, '10-four-tunings.png', 'P、PD、PI、PID 的指标对比')


def fig11():
    f, y = new(11, '写进程序里长什么样',
               '计算机里没有「连续」，只有一帧一帧地算。'
               '把三项写成每一帧执行的代码，就是所谓的位置式 PID。')
    f.box('c', 60, y, 1002, y + 480)
    lines = [
        'error = setpoint - measured',
        'integral += error * dt',
        'derivative = (error - prev_error) / dt',
        'output = kp*error + ki*integral',
        '       + kd*derivative',
        'prev_error = error',
    ]
    yy = y + 30
    for s in lines:
        f.text((90, yy), s, 42, color=TEAL if 'output' in s else INK, inside='c')
        yy += 62
    y += 520
    y = note(f, y, '三行状态里藏着一个关键点：integral 会一直累加，永不遗忘。'
                   '它让误差归零，也是超调和积分饱和的根源。')
    y = note(f, y, '还有一个容易忽略的地方：derivative 用的是「这一帧减上一帧」。'
               '采样越快，同样的温度变化算出来的导数越大——第 15 节会看到它的后果。',
         color=AMBER)
    save(f, '11-discrete-form.png', '位置式 PID 的离散实现')


def fig12():
    f, y = new(12, '三项各自出了多少力',
               '把 PID 的三个分量单独画出来，就能看清谁在什么时候说话。')
    row = R['tunings'][3]
    c = row['curve']
    y, top = single(f, y, '温度响应（Kp = 0.06，Ki = 0.0004，Kd = 1）',
                    (20, 100), (20, 40, 60, 80, 100), 800, (0, 200, 400, 600, 800))
    top.hline(SP, color=GRAY, dash=16)
    top.line(c['t'], c['y'], TEAL, 5)
    f.text((44, y), '三项各自的值，以及它们相加后的输出', 42, bold=True, color=INK)
    key_row(f, [(BLUE, 'P 项'), (GREEN, 'I 项'), (RED, 'D 项'), (INK, '总输出 u')],
            right=1000, y=y + 58)
    y0 = y + 178
    p = Plot(f, (212, y0, 1000, y0 + 440), (0, 800), (-2.0, 4.0))
    p.axes(xticks=(0, 200, 400, 600, 800), yticks=(-2, -1, 0, 1, 2, 3, 4),
           yfmt='%g', ylab='项的值', xlab='时间 / s')
    p.hline(0, color=GRAY, dash=16)
    p.line(c['t'], c['p'], BLUE, 4)
    p.line(c['t'], c['i'], GREEN, 4)
    p.line(c['t'], c['d'], RED, 4)
    p.line(c['t'], c['u'], INK, 5)
    y = y0 + 440 + 130
    y = note(f, y, '黑线是三项之和，也就是控制器想要给出的功率。它一开始是 3.6，'
                   '远超执行器上限 1，所以前 15 秒真正送进炉子的只有 1——'
                   '这段时间黑线被压在 1 上，跟三项之和不再相等。')
    y = bullets(f, y, [
        'P 项（蓝）从 3.6 起步——误差 60 度乘以 Kp = 0.06——误差一小就退回零。',
        'I 项（绿）慢慢爬升，最后一个人扛下全部稳态输出（约 0.3），'
        '此时 P 和 D 都是零。',
        'D 项（红）在升温最快的时候给出 −1.7 左右，把输出往下拉，'
        '这就是它压制超调的方式；温度一稳，它也回到零。',
    ])
    save(f, '12-three-terms.png', 'PID 三项在时间上的分工')


def fig13():
    f, y = new(13, '积分饱和：账记多了，就还不清',
               '如果执行器已经满功率，误差还在，积分项仍然继续累积。'
               '等温度到了设定值，账上已经存了一大笔，只能靠反向超调来还。')
    rows = [[('反饱和处理', INK, True), ('超调', INK, True), ('稳定时间 / s', INK, True)]]
    for row in R['windup']:
        m = row['metrics']
        name = {'none': '不做处理', 'clamp': '饱和时停止积分', 'back': '按超出量回退积分'}[row['mode']]
        rows.append([(name, INK, False), ('%.2f%%' % m['overshoot'], INK, False),
                     ('%s' % (m['settling_time'] if m['settling_time'] else '没稳下来'), INK, False)])
    y = table(f, y, [(60, 'la'), (620, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '同一组参数、同一个炉子，只改「饱和时积分项怎么办」：'
                   '超调从 17.0% 降到 9.2%，再降到 0%。')
    y = note(f, y, '代价是变慢：回退积分的方式把上升时间从 28 s 拖到 308 s。'
               '反饱和不是免费的，它是拿速度换稳定。', color=AMBER)
    save(f, '13-windup.png', '积分饱和与三种处理方式')


def fig14():
    f, y = new(14, '微分踢：换设定值时输出会跳一下',
               '误差 = 设定值 − 测量值。设定值突然变了，误差也跟着跳，'
               '微分项算出的是一个巨大的瞬时值。')
    y, p = single(f, y, '在 t = 200 s 把设定值从 80 °C 调到 90 °C', (0, 2.2),
                  (0, 0.5, 1, 1.5, 2), 400, (0, 100, 200, 300, 400),
                  ylab='加热功率')
    for row, color in zip(R['kick'], (RED, TEAL)):
        p.line(row['curve']['t'], row['curve']['u'], color, 4)
    # `overshoot` is meaningless here: the run starts at the setpoint and the
    # setpoint then moves, so the metric falls back to a full-span excursion
    # and reports 100% for both modes. Quote the peak output instead.
    for row, color in zip(R['kick'], (RED, TEAL)):
        name = '对误差求导' if row['mode'] == 'error' else '对测量值求导'
        y = note(f, y, '%s：峰值输出 %.3f（上限 1.000）' % (name, row['metrics']['max_u']),
                 color=color)
    y = note(f, y, '红线的尖峰就是「微分踢」：一次设定值变化被微分项当成了无穷大的变化率，'
                   '一个采样点就顶到了上限。改成对测量值求导，同样的信息还在，尖峰没有了。')
    save(f, '14-derivative-kick.png', '微分踢与两种求导对象')


def fig15():
    f, y = new(15, '采样太慢，等于蒙着眼睛开车',
               '控制器每隔 dt 秒才看一次温度。两次之间发生了什么，它完全不知道。')
    y, p = single(f, y, '同一组 PID 参数，只改采样周期', (20, 110),
                  (20, 40, 60, 80, 100), 800, (0, 200, 400, 600, 800))
    p.hline(SP, color=GRAY, dash=16)
    shades = (TEAL, GREEN, BLUE, AMBER, RED)
    for row, color in zip(R['sample_time'], shades):
        p.line(row['curve']['t'], row['curve']['y'], color, 4)
    rows = [[('采样周期 / s', INK, True), ('上升时间 / s', INK, True),
             ('超调', INK, True), ('稳定时间 / s', INK, True)]]
    for row in R['sample_time']:
        m = row['metrics']
        rows.append([('%g' % row['dt'], INK, False),
                     ('%s' % (m['rise_time'] if m['rise_time'] else '—'), INK, False),
                     ('%.2f%%' % m['overshoot'], RED if m['overshoot'] > 5 else INK, False),
                     ('%s' % (m['settling_time'] if m['settling_time'] else '没稳下来'), INK, False)])
    y = table(f, y, [(60, 'la'), (330, 'la'), (620, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '采样周期从 0.1 s 拉到 30 s，参数一个字没改，'
               '回路却从「稳稳的」变成「来回荡」。')
    y = note(f, y, '经验规则：采样周期应当明显小于系统最快的时间常数。'
               '本文的炉子最快时间常数是 20 s，采样取到它的四分之一（5 s）仍然安全；'
               '接近这个时间常数本身（15 s）才开始失稳。', color=TEAL)
    save(f, '15-sample-time.png', '采样周期对控制质量的影响')


def fig16():
    f, y = new(16, '延迟：PID 真正打不过的对手',
               '延迟意味着控制器此刻的动作，要过一会儿才被炉子看到。'
               '它拿着过期信息做决定，越用力越容易过冲。')
    y, p = single(f, y, '同一组 PID 参数，只改纯延迟时间', (20, 160),
                  (20, 60, 100, 140), 1500, (0, 300, 600, 900, 1200, 1500))
    p.hline(SP, color=GRAY, dash=16)
    shades = (TEAL, GREEN, BLUE, AMBER, RED)
    for row, color in zip(R['dead_time'], shades):
        p.line(row['curve']['t'], row['curve']['y'], color, 4)
    rows = [[('延迟 / s', INK, True), ('超调', INK, True), ('峰值 / °C', INK, True),
             ('稳定时间/s', INK, True)]]
    for row in R['dead_time']:
        m = row['metrics']
        rows.append([('%g' % row['dead'], INK, False),
                     ('%.1f%%' % m['overshoot'], RED if m['overshoot'] > 20 else INK, False),
                     ('%.1f' % m['peak'], INK, False),
                     ('%s' % (m['settling_time'] if m['settling_time'] else '没稳下来'), INK, False)])
    y = table(f, y, [(60, 'la'), (330, 'la'), (520, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '延迟从 0 加到 60 s，超调从 0% 涨到 122%，峰值冲到 153 °C。'
               '参数完全没变——变的是「控制器对现在的了解有多旧」。')
    # The obvious next move is to turn the gain down. It works, and that is
    # the trap: the overshoot disappears because the whole loop slows down.
    y, p = single(f, y, '延迟 60 s 不变，把同一组参数整体调小', (20, 160),
                  (20, 60, 100, 140), 1500, (0, 300, 600, 900, 1200, 1500))
    p.hline(SP, color=GRAY, dash=16)
    for row, color in zip(R['dead_time_detune'], shades):
        p.line(row['curve']['t'], row['curve']['y'], color, 4)
    key_row(f, [(c, '%g×' % r['factor'])
                for r, c in zip(R['dead_time_detune'], shades)],
            right=1000, y=y, sample=28, gap=16)
    y += 100
    rows = [[('增益', INK, True), ('超调', INK, True), ('上升时间', INK, True),
             ('最终温度', INK, True)]]
    for row in R['dead_time_detune']:
        m = row['metrics']
        rows.append([('×%g' % row['factor'], INK, False),
                     ('%.1f%%' % m['overshoot'], RED if m['overshoot'] > 20 else INK, False),
                     ('%s' % ('%.0f' % m['rise_time'] if m['rise_time'] else '到不了'),
                      INK, False),
                     ('%.1f' % row['curve']['y'][-1], INK, False)])
    y = table(f, y, [(60, 'la'), (330, 'la'), (640, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '增益减半，超调从 122% 掉到 50%；减到四分之一，超调真的归零——'
               '但上升时间从 27.6 s 涨到 1087 s，慢了近四十倍，最终还只停在 76.2 °C。'
               '再往下减，温度在 1500 s 内根本到不了 80 °C。', color=TEAL)
    y = note(f, y, '延迟拿走的不是「稳定」，是「又快又稳」这个组合：'
               '调小增益能让回路重新稳住，代价是整个回路跟着一起慢下来。')
    save(f, '16-dead-time.png', '纯延迟如何毁掉一组好参数')


def fig17():
    f, y = new(17, '让系统自己说出该用多大参数',
               '1942 年提出的整定法：先把 I 和 D 关掉，把 Kp 加到系统刚好等幅振荡，'
               '记下这个增益和振荡周期，再按表换算。')
    zn = R['zn']
    y = bullets(f, y, [
        '第一步：只用 P，从小到大加 Kp，直到响应不再衰减。这个值叫极限增益 Ku。',
        '第二步：量出等幅振荡的周期 Tu。',
        '第三步：按固定比例换算出 Kp、Ki、Kd。',
    ])
    y += 10
    rows = [[('延迟 / s', INK, True), ('极限增益 Ku', INK, True),
             ('周期 Tu / s', INK, True), ('结论', INK, True)]]
    rows.append([('0', INK, False), ('—', GRAY, False), ('—', GRAY, False),
                 ('没有极限增益', RED, False)])
    rows.append([('15', INK, False), ('%.3f' % zn['with_delay']['ku'], INK, False),
                 ('%.1f' % zn['with_delay']['tu'], INK, False),
                 ('可以整定', GREEN, False)])
    y = table(f, y, [(60, 'la'), (320, 'la'), (640, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '第一行是本文程序跑出来的：没有延迟时，Kp 一直加到 4，'
                   '回路仍然收敛——因为二级滞后系统的相位滞后永远到不了 180°。'
                   '这种情况下「极限增益」根本不存在，硬套公式会得到一个假数。')
    if zn.get('tunings'):
        rows = [[('按表整定', INK, True), ('超调', INK, True), ('稳态误差 / °C', INK, True)]]
        for row in zn['tunings']:
            rows.append([(row['name'], INK, False),
                         ('%.1f%%' % row['metrics']['overshoot'], RED, False),
                         ('%+.2f' % row['metrics']['steady_state_error'], INK, False)])
        y = table(f, y, [(60, 'la'), (620, 'la'), (1014, 'ra')], rows)
        y = note(f, y, '延迟 15 s 的那一组：按 ZN 表整定出来，超调 26% 到 60%。'
                       '这不是算错了，是 ZN 本来就偏激进——它追求的是「快速回到设定值」，'
                       '而不是「不冲过头」。', color=AMBER)
    save(f, '17-ziegler-nichols.png', 'Ziegler-Nichols 整定法的实测结果')


def fig18():
    f, y = new(18, 'D 项的代价：它放大了噪声',
               '微分项算的是「这一帧减上一帧」。传感器读数里的随机跳动，'
               '会被它按同样的比例放大成执行器的抖动。')
    rows = [[('Kd', INK, True), ('平均变化', INK, True),
             ('最大变化', INK, True), ('超调', INK, True)]]
    for row in R['noise']:
        rows.append([('%g' % row['kd'], INK, False),
                     ('%.4f' % row['mean_u_swing'], INK, False),
                     ('%.3f' % row['max_u_swing'], INK, False),
                     ('%.2f%%' % row['metrics']['overshoot'], INK, False)])
    y = table(f, y, [(60, 'la'), (320, 'la'), (620, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '传感器噪声标准差 0.4 °C。Kd 从 0 加到 1，'
                   '执行器每次动作的平均幅度从 0.024 涨到 0.62——放大 25 倍。')
    y = note(f, y, '现实中执行器有寿命，电机有磨损。所以工程上的 D 项通常要配一个低通滤波'
               '（本文代码里的 tau_d 参数就是干这个的），或者干脆不用 D。', color=AMBER)
    save(f, '18-noise.png', '微分项对测量噪声的放大')


def fig19():
    f, y = new(19, '扰动来了，谁先扛住',
               '设定值没变，是外部条件变了：t = 300 s 时炉门被打开，'
               '多了一份持续的热损失。')
    y, p = single(f, y, '同样的三种控制器，面对同一个扰动', (68, 84),
                  (70, 75, 80), 800, (0, 200, 400, 600, 800))
    p.hline(SP, color=GRAY, dash=16)
    for row, color in zip(R['disturbance'], (RED, AMBER, TEAL)):
        p.line(row['curve']['t'], row['curve']['y'], color, 4)
    rows = [[('控制器', INK, True), ('最大跌落', INK, True),
             ('最终温度', INK, True), ('恢复时间', INK, True)]]
    for row in R['disturbance']:
        rows.append([(row['name'], INK, False), ('%.2f' % row['dip'], INK, False),
                     ('%.2f' % row['final'],
                      RED if abs(row['final'] - SP) > 0.5 else GREEN, False),
                     ('%.1f' % row['recovered_at'] if row['recovered_at']
                      else '没恢复', INK, False)])
    y = table(f, y, [(60, 'la'), (300, 'la'), (600, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '只有 P 的控制器的最终温度是 73.85 °C——它永远回不到设定值，'
               '因为它没有「记账」的能力，而扰动是持续的。')
    save(f, '19-disturbance.png', '三种控制器对持续扰动的反应')


def fig20():
    f, y = new(20, '执行器顶到头的时候',
               '加热功率最大是 1。设定值定得太高，控制器无论怎么算都到不了，'
               '积分项就会一直往上爬。')
    rows = [[('功率上限', INK, True), ('最终温度', INK, True),
             ('稳态误差', INK, True), ('能达到吗', INK, True)]]
    for row in R['saturation']:
        m = row['metrics']
        ok = abs(m['steady_state_error']) < 0.5
        rows.append([('%.1f' % row['umax'], INK, False),
                     ('%.2f' % m['final'], INK, False),
                     ('%+.3f' % m['steady_state_error'], RED if not ok else GREEN, False),
                     ('能' if ok else '不能', GREEN if ok else RED, False)])
    y = table(f, y, [(60, 'la'), (300, 'la'), (600, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '功率上限 0.2 时，炉子最高只能到 60 °C，离设定值 80 °C 差 20 °C。'
                   '控制器再聪明也变不出功率。')
    y = note(f, y, '这时候积分项会一直累积（除非开了反饱和），一旦上限被抬高，'
               '它会突然把积压的账一次性放出来——这是现场调试里最常见的「一改参数就冲」。',
         color=AMBER)
    save(f, '20-saturation.png', '执行器饱和下的稳态误差')


def fig21():
    f, y = new(21, '同一套想法，用在会倒的东西上',
               '小车上的倒立摆：杆子会倒，小车只能左右推。它不稳定、非线性，'
               '但两个 PID 串起来就能让它站起来。')
    cp = R['cartpole']
    y, p = single(f, y, '外环管位置，内环管角度', (-0.1, 0.6),
                  (0, 0.25, 0.5), 10, (0, 2, 4, 6, 8, 10), ylab='小车位置 / m')
    p.hline(cp['goal'], color=GRAY, dash=16)
    p.line(cp['t'], cp['x'], TEAL, 5)
    rows = [[('量', INK, True), ('结果', INK, True), ('说明', INK, True)]]
    rows.append([('初始倾角', INK, False), ('%.3f rad' % cp['start_tilt'], INK, False),
                 ('一放手就会倒', INK, False)])
    rows.append([('最大倾角', INK, False), ('%.4f rad' % cp['max_abs_angle'], INK, False),
                 ('没超过初始值', INK, False)])
    rows.append([('最终位置', INK, False), ('%.4f m' % cp['final_x'], INK, False),
                 ('目标 0.5 m', INK, False)])
    rows.append([('最大推力', INK, False), ('%.2f N' % cp['max_force'], INK, False),
                 ('没有用蛮力', INK, False)])
    y = table(f, y, [(60, 'la'), (330, 'la'), (700, 'la')], rows)
    y = note(f, y, '内环的控制器输出要取负号：杆子往右倒，就得把车往右推。'
                   '外环的输出是「该倾斜多少度」，它被限幅在 ±0.15 rad——'
                   '不让外环为了追位置而把杆子甩倒。')
    y = note(f, y, '这两个细节（取负号、限幅）都不是 PID 公式里的东西，'
               '而是把公式接到真实系统上时必须自己补的。', color=TEAL)
    save(f, '21-cartpole.png', '串级 PID 控制倒立摆')


def fig22():
    f, y = new(22, '它在哪些地方真的在跑',
               'PID 不是实验室里的玩具。下面这些设备里，跑的都是同一套三项相加的逻辑。')
    y = bullets(f, y, [
        '恒温箱、热水器、3D 打印机的热床——温度环，最常见的一阶加滞后对象。',
        '汽车定速巡航和无人机的姿态环——后者通常用串级 PID，和倒立摆一个套路。',
        '硬盘磁头定位、光刻机的工件台——高速高精度位置环。',
        '电厂锅炉、化工反应釜——分布式控制系统里的绝大多数回路仍然是 PID。',
        '游戏里的相机跟随、角色转向平滑——用的也是同一套公式，只是 dt 是一帧。',
    ])
    y += 10
    y = note(f, y, '一项行业调查曾估计，工业控制回路里超过九成仍然是 PID 或它的变体。'
                   '本文没有核对这份调查的原始数据，因此正文只说「绝大多数」，不给具体比例。')
    y = note(f, y, '它长盛不衰的原因很简单：三个参数、可以手调、不依赖精确模型，'
               '而且在大多数对象上确实够用。', color=TEAL)
    save(f, '22-where-it-runs.png', 'PID 的现实应用')


def fig23():
    f, y = new(23, '一百年前，它是在船上被发明出来的',
               'PID 的第一次系统描述出现在 1922 年，作者是俄裔美国工程师'
               '尼古拉斯·米诺尔斯基，对象是军舰的舵机。')
    y = bullets(f, y, [
        '船很大，舵转过去以后，船要过很久才转向——这就是纯延迟。',
        '只按角度偏差打舵，船会来回摆；米诺尔斯基加入了「偏差的积分」和'
        '「偏差的变化率」两项。',
        '他 1922 年发表的论文给出了三项并列的控制器形式，'
        '这是目前公认的 PID 最早的系统性描述。',
    ])
    y += 10
    y = note(f, y, '后来这套方法被 Sperry 等公司用于船舶自动驾驶仪，'
                   '再进入化工、冶金、航空，最后进入每一台带温度控制的电器。')
    y = note(f, y, '正文没有引用论文原文，只陈述其公开的年份、作者与对象；'
               '更细的历史考证见文末来源说明。', color=GRAY)
    save(f, '23-history.png', 'PID 的起源：1922 年的船舶舵机')


def fig24():
    f, y = new(24, '自己动手改一个条件',
               '下面每一行都能在本目录的代码里改一个数字重跑。先猜结果，再对照。')
    y = bullets(f, y, [
        '把 Ki 设成 0.01（比本文大 25 倍），看温度会冲到哪里。',
        '把 Kd 设成 20，再看一次——超调是变小还是变大？',
        '把采样周期改成 60 s，比炉子的时间常数还长，会怎样？',
        '把 anti_windup 从 clamp 改成 none，超调变化多少？',
        '把 tau_d 设成 5 s，再跑第 18 节的噪声实验，看执行器抖动降了多少。',
        '把倒立摆的初始倾角从 0.05 改成 0.3 rad，PID 还能救回来吗？',
    ])
    y += 10
    y = note(f, y, '第 6 题值得认真试：同一个控制器，初始偏差一大就失效了。'
                   '这不代表 PID 不好，而是说明任何控制器的能力都有边界。')
    save(f, '24-try-it.png', '读者可以自己改动的六项实验', min_width_coverage=0.80)


def make_cover():
    """The 1080 square, and the band a 2.35:1 centre crop would keep.

    WeChat's list thumbnail crops the master to 2.35:1 from the middle --
    y from 310 to 770. Anything that has to be read in the feed lives there.
    """
    f = Fig(1080, width=1080)
    # The cover carries the article's own headline. A cover with a different
    # headline than the article is a promise the article never makes good on.
    f.text((540, 322), '为什么炉子总是差那一点点？', 64, True, anchor='ma')
    f.text((540, 394), 'PID 控制器怎样学会自己找目标', 56, True, anchor='ma')
    f.text((540, 460), '三个旋钮：P、I、D 各管一件事', 48, True, TEAL, anchor='ma')
    for i, (label, color) in enumerate((('P 现在差多少', RED),
                                        ('I 过去差了多少', AMBER),
                                        ('D 正在往哪变', TEAL))):
        y0 = 508 + i * 66
        f.rect(120, y0, 960, y0 + 64, fill=WHITE, outline=LIGHT, width=3)
        f.rect(120, y0, 140, y0 + 64, fill=color, outline=None)
        f.text((180, y0 + 13), label, 40, color=INK)
    f.text((540, 716), '一个炉子、一台倒立摆，和一百年前的船舵', 40, True,
           INK_SOFT, anchor='ma')
    f.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


def main():
    only = [int(a) for a in sys.argv[1:]]
    for i in range(1, 25):
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
