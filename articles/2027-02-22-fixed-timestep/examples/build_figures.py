#!/usr/bin/env python3
"""固定时间步长一文的原创教学插图。MIT。

所有带数字的图都读 results.json，不在画图时另算一遍。
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
PALETTE.update({VIOLET})


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


def legend(fig, y, items, x0=52, step=300):
    x = x0
    for color, text in items:
        fig.rect(x, y + 4, x + 30, y + 34, fill=color, outline=None, radius=6)
        fig.text((x + 44, y - 2), text, 38, color=INK)
        x += step
    return y + 52


def axes(fig, x0, y0, x1, y1, xr, yr, xticks, yticks, xlabel, ylabel):
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
    for t in xticks:
        fig.text((px(t), y1 + 14), str(t), 38, color=INK_SOFT, anchor='ma')
    for t in yticks:
        fig.text((x0 - 16, py(t) - 22), str(t), 38, color=INK_SOFT, anchor='ra')
    fig.text((x1, y1 + 62), xlabel, 38, color=INK_SOFT, anchor='ra')
    fig.text((x0 - 16, y0 - 52), ylabel, 38, color=INK_SOFT, anchor='la')
    return px, py


def series(fig, pts, color, width=5, dash=None):
    for a, b in zip(pts, pts[1:]):
        fig.line(a, b, color=color, width=width, dash=dash)


# ---------------------------------------------------------------- 图 01

def fig01():
    fig, y = new(1, '一帧一帧地跳',
                 '60 fps、起跳速度 8 m/s、重力 30 m/s²。灰线是连续解，'
                 '圆点是每帧算出来的位置。')
    x0, y0, x1, y1 = 190, y + 70, 980, 640
    px, py = axes(fig, x0, y0, x1, y1, (0.0, 0.36), (0.0, 1.2),
                  (0.0, 0.1, 0.2, 0.3), (0.0, 0.4, 0.8, 1.2), '秒', '高度 m')
    v0, g = R['jump']['v0'], R['jump']['g']
    cont = []
    for i in range(0, 361):
        tt = i / 1000.0
        yy_ = v0 * tt - 0.5 * g * tt * tt
        if yy_ < -0.05:
            break
        cont.append((px(tt), py(yy_)))
    series(fig, cont, GRAY, 4)
    for row in R['jump']['trace']:
        if row['y'] < -0.02 or row['t'] > 0.36:
            continue
        fig.circle(px(row['t']), py(row['y']), 9, fill=TEAL, outline=WHITE, width=2)
    fig.line((x0, py(1.0667)), (x1, py(1.0667)), color=BLUE, width=3, dash=12)
    fig.text((x1 - 8, py(1.0667) - 44), '连续解 1.067 m', 38, color=BLUE, anchor='ra')
    fig.text((px(0.25) + 16, py(0.99)), '半隐式 1.000 m', 38, color=TEAL)
    yy = note(fig, y1 + 100,
              '每一帧都做同样两步：先把速度减去 g·dt，再用新速度推进一步位置。'
              '整步的位移都算在「已经加速过」的速度上，所以点永远落在抛物线下方 g·t·dt/2 处，'
              '最高点矮了 v0·dt/2 = 6.7 cm。')
    save(fig, '01-jump-trace.png', '跳跃的离散采样与连续解')


# ---------------------------------------------------------------- 图 02

def fig02():
    fig, y = new(2, '帧率一改，跳跃高度就变',
                 '纵轴是最高点与连续解的差（%）。两条线是两种积分顺序，'
                 '横轴是帧率。')
    rows = R['jump']['rows']
    v_first = [r for r in rows if r['order'] == 'v_first']
    y_first = [r for r in rows if r['order'] == 'y_first']
    an = R['jump']['analytic']
    x0, y0, x1, y1 = 190, y + 70, 960, 560
    px, py = axes(fig, x0, y0, x1, y1, (0.0, 4.2), (-16.0, 16.0),
                  (0, 1, 2, 3, 4), (-16, -8, 0, 8, 16), '每秒帧数的对数 log10(fps)', '误差 %')
    for dt, sign, col in ((1, 1, BLUE), (1, -1, TEAL)):
        pts = [(px(math.log10(1 / r['dt'])), py(sign * abs(r['apex'] - an) / an * 100))
               for r in (v_first if sign < 0 else y_first)]
        series(fig, sorted(pts), col, 5)
        for p in pts:
            fig.circle(p[0], p[1], 8, fill=col, outline=WHITE, width=2)
    fig.line((x0, py(0)), (x1, py(0)), color=INK, width=3)
    fig.text((x1 - 10, py(13)), '先动位置', 38, color=BLUE, anchor='ra')
    fig.text((x1 - 10, py(-13)), '先加速度', 38, color=TEAL, anchor='ra')
    yy = note(fig, y1 + 110,
              '两个方向的误差都正好是 ±v0·dt/2 除以最高点：24 fps 差 15%，60 fps 差 6.25%，'
              '240 fps 差 1.56%。同一个起跳速度，30 fps 的玩家比 240 fps 的玩家矮 11%——'
              '这不是玩法设计，是积分器的半步偏移。')
    save(fig, '02-apex-vs-fps.png', '跳跃最高点误差随帧率变化')


# ---------------------------------------------------------------- 图 03

def fig03():
    fig, y = new(12, '每帧靠 10% 的插值',
                 '镜头每帧朝目标走剩余距离的 10%。目标在第 0 帧从 0 跳到 1，'
                 '横轴是时间，纵轴是剩下的距离。')
    x0, y0, x1, y1 = 200, y + 70, 950, 520
    px, py = axes(fig, x0, y0, x1, y1, (0.0, 0.5), (0.0, 1.0),
                  (0, 0.1, 0.2, 0.3, 0.4, 0.5), (0, 0.25, 0.5, 0.75, 1.0),
                  '秒', '已经走完的比例')
    for fps, col in ((30, RED), (60, TEAL), (144, BLUE)):
        pts = [(px(p['t']), py(p['x'])) for p in R['lerp']['tracks'][str(fps)]]
        series(fig, pts, col, 5)
    fig.line((x0, py(1.0)), (x1, py(1.0)), color=GRAY, width=3, dash=12)
    fig.text((x1 - 10, py(1.0) + 14), '目标', 38, color=GRAY, anchor='ra')
    legend(fig, y1 + 96, [(RED, '30 fps'), (TEAL, '60 fps'), (BLUE, '144 fps')], step=260)
    yy = note(fig, y1 + 160,
              '一秒之后：24 fps 还差 8.0%，30 fps 差 4.2%，60 fps 差 0.18%，'
              '144 fps 只剩千万分之三。同一条代码，不同的帧率，'
              '摄像机的「跟手程度」是三个东西。')
    save(fig, '12-lerp.png', '每帧插值对帧率的依赖')


# ---------------------------------------------------------------- 图 04

def fig04():
    fig, y = new(8, '三种积分器的能量账',
                 '谐振子 x″ = −ω²x，ω·dt = 0.105（1 Hz、60 fps），一共跑 10 秒，图只画前 6 秒。'
                 '纵轴是 |E/E₀ − 1|，对数轴。')
    x0, y0, x1, y1 = 210, y + 70, 950, 560
    px, py = axes(fig, x0, y0, x1, y1, (0.0, 6.0), (-6.0, 3.0),
                  (0, 2, 4, 6), (-6, -3, 0, 3), '秒', 'log10 |E/E₀ − 1|')
    for key, col in (('explicit', RED), ('semi', TEAL), ('rk4', BLUE)):
        d = R['energy'][key]
        pts = []
        for t, e in zip(d['t'], d['e']):
            v = abs(e - 1.0)
            lv = math.log10(v) if v > 0 else -6.0
            pts.append((px(t), py(max(-6.0, min(3.0, lv)))))
        series(fig, pts, col, 5)
    fig.text((px(3.3), py(2.4)), '显式欧拉', 38, color=RED)
    fig.text((px(3.3), py(-1.4)), '半隐式', 38, color=TEAL)
    fig.text((px(3.3), py(-3.8)), 'RK4', 38, color=BLUE)
    yy = note(fig, y1 + 100,
              '显式欧拉每一步都把能量乘上 1 + (ω·dt)²，600 步之后放大 694 倍——10 秒就炸了。'
              '半隐式（先加速、再移动）不让能量单向漂移，只在 ±5% 之间来回；RK4 每步更准，'
              '但会一点点往下掉。')
    save(fig, '08-energy.png', '三种积分器的能量偏差')


# ---------------------------------------------------------------- 图 05

def fig05():
    fig, y = new(9, '同一个振子，三种轨迹',
                 '横轴是位置，纵轴是速度除以 ω。初始状态在 (1, 0)，跑 4 秒。')
    cx, cy, rad = 600, 430, 200
    fig.circle(cx, cy, rad, outline=LIGHT, width=3)
    fig.line((cx - rad - 50, cy), (cx + rad + 50, cy), color=LIGHT, width=2)
    fig.line((cx, cy - rad - 30), (cx, cy + rad + 30), color=LIGHT, width=2)
    fig.text((cx + rad + 30, cy + 12), 'x', 38, color=INK_SOFT)
    fig.text((cx - 16, cy - rad - 44), 'ω·v', 38, color=INK_SOFT, anchor='ra')
    for key, col in (('explicit', RED), ('semi', TEAL), ('rk4', BLUE)):
        pts = [(cx + 190 * p[0], cy - 190 * p[1]) for p in R['phase']['rows'][key]
               if abs(p[0]) < 1.35 and abs(p[1]) < 1.35]
        series(fig, pts, col, 4)
    legend(fig, cy + rad + 60, [(RED, '显式欧拉'), (TEAL, '半隐式'), (BLUE, 'RK4')],
           step=250)
    yy = note(fig, cy + rad + 120,
              '能量守恒的振子应该跑出一个闭合圆。显式欧拉绕着圈往外爬，'
              '半隐式贴住圆周（相位略慢，半径不动），RK4 稍微往里收。')
    save(fig, '09-phase.png', '三种积分器的相图')


# ---------------------------------------------------------------- 图 06

def fig06():
    fig, y = new(3, '累加器：这一帧该跑几步',
                 '固定步长 1/60 秒。每根柱子是一帧：柱高就是这一帧补跑的步数，'
                 '横轴是帧序号。帧时间在 10–28 ms 之间随机抖动。')
    x0, y0, x1, y1 = 190, 340, 950, 590
    rows = R['accum']['plain']['rows']
    px, py = axes(fig, x0, y0, x1, y1, (0, len(rows)), (0, 3),
                  (0, 30, 60, 90, 120), (0, 1, 2, 3), '帧序号', '这一帧跑的步数')
    bw = (x1 - x0) / len(rows) - 3
    for i, r in enumerate(rows):
        x = x0 + i * ((x1 - x0) / len(rows))
        c = TEAL if r['steps'] == 1 else (AMBER if r['steps'] == 2 else LIGHT)
        fig.rect(x, py(r['steps']), x + bw, py(0), fill=c, outline=None)
    a = R['accum']['plain']
    legend(fig, y1 + 76, [(TEAL, '1 步'), (AMBER, '2 步'), (LIGHT, '0 步')], step=220)
    yy = note(fig, y1 + 136,
              '{} 帧里 7 帧一步没跑、86 帧跑一步、27 帧跑两步；总共 {} 步 = {:.4f} 秒，'
              '墙上过了 {:.4f} 秒，差的 {:.1f} 毫秒留在累加器里。'.format(
                  a['frames'], a['steps'], a['simulated'], a['elapsed'],
                  a['acc_left'] * 1000))
    save(fig, '03-accumulator.png', '累加器每帧的步数')


# ---------------------------------------------------------------- 图 07

def fig07():
    fig, y = new(4, '一次 500 毫秒的卡顿',
                 '同一个抖动序列，第 40 帧卡了半秒。上面照实补帧，'
                 '下面加了「一帧最多补 250 毫秒」的闸门。')
    x0, x1 = 190, 950
    rows_a = R['accum']['hitch']['rows']
    rows_b = R['accum']['hitch_clamped']['rows']
    for k, (rows, title, col) in enumerate(((rows_a, '不设闸门', TEAL),
                                            (rows_b, '闸门 250 ms', BLUE))):
        base = 430 + k * 240
        fig.text((48, base - 44), title, 40, bold=True, color=col)
        fig.line((x0, base), (x1, base), color=INK, width=2)
        fig.text((x1, base + 14), '第 0–60 帧', 38, color=INK_SOFT, anchor='ra')
        for i, r in enumerate(rows[:60]):
            h = min(150, r['steps'] * 5)
            xx = x0 + i * ((x1 - x0) / 60)
            fig.rect(xx, base - h, xx + 10, base,
                     fill=col if r['steps'] else LIGHT, outline=None)
    yy = note(fig, 750,
              '第 40 帧：上面补跑 30 步（0.5 秒），下面只补 15 步，剩下 250 毫秒丢掉。')
    save(fig, '04-hitch.png', '卡顿帧的补帧与闸门')


# ---------------------------------------------------------------- 图 08

def fig08():
    fig, y = new(5, '越慢越要补，越补越慢',
                 '一帧的开销 = 20 ms 基础开销 + 步数 × 每步开销。'
                 '每步开销逼近 16.67 ms 时，帧时间没有上限。')
    x0, y0, x1, y1 = 210, 360, 950, 590

    def px(v):
        return x0 + v / 20.0 * (x1 - x0)

    def py(v):
        v = min(600.0, max(16.67, v))
        lv = math.log10(v) - math.log10(16.67)
        return y1 - lv / (math.log10(600.0) - math.log10(16.67)) * (y1 - y0)

    fig.rect(px(16.6667), y0, x1, y1, fill=TINT_R, outline=None)
    for c in (20, 100, 600):
        fig.line((x0, py(c)), (x1, py(c)), color=LIGHT, width=2)
        fig.text((x0 - 16, py(c) - 22), '{}'.format(c), 38, color=INK_SOFT, anchor='ra')
    fig.line((px(16.6667), y0), (px(16.6667), y1), color=RED, width=3)
    fig.text((x1 - 10, y1 - 56), '无解', 38, color=RED, anchor='ra')
    pts = []
    for s in R['spiral']:
        if s['predicted'] is None or s['last_ms'] > 600:
            continue
        pts.append((px(s['cost']), py(s['last_ms'])))
        fig.circle(px(s['cost']), py(s['last_ms']), 9, fill=TEAL, outline=WHITE, width=2)
    series(fig, pts, TEAL, 4)
    fig.line((x0, y1), (x1, y1), color=INK, width=3)
    fig.line((x0, y0), (x0, y1), color=INK, width=3)
    for c in (0, 4, 8, 12, 16):
        fig.text((px(c), y1 + 14), str(c), 38, color=INK_SOFT, anchor='ma')
    fig.text((x1, y1 + 62), '每步开销 ms', 38, color=INK_SOFT, anchor='ra')
    fig.text((x0 - 16, y0 - 52), '稳态帧时间 ms（对数）', 38, color=INK_SOFT)
    yy = note(fig, y1 + 120,
              '稳态帧时间 = 基础开销 ÷ (1 − 每步开销 ÷ dt)。每步 10 ms 时稳定在 50 ms，'
              '15 ms 时 200 ms，16 ms 时 500 ms，到了 16.67 ms 就没有稳态了：'
              '补得越多、跑得越慢，这就是死亡螺旋。')
    save(fig, '05-spiral.png', '补帧与每步开销的稳态关系')


# ---------------------------------------------------------------- 图 09

def fig09():
    fig, y = new(6, '薄墙是躲得过去的',
                 '子弹速度换来每步位移，墙厚 0.1 m。柱子是实测穿透率，'
                 '折线是 1 − 墙厚 ÷ 每步位移。')
    rows = R['tunnel']['rows']
    x0, y0, x1, y1 = 210, y + 70, 950, 540
    px, py = axes(fig, x0, y0, x1, y1, (0, 6.2), (0.0, 1.0),
                  (0, 1, 2, 3, 4, 5, 6), (0, 0.25, 0.5, 0.75, 1.0),
                  'log10(速度 m/s)', '整个跳过墙的比例')
    for i, r in enumerate(rows):
        xx = px(math.log10(r['speed']))
        fig.rect(xx - 26, py(r['rate']), xx + 26, py(0), fill=TINT_T, outline=TEAL)
    pts = [(px(math.log10(r['speed'])), py(r['closed_form'])) for r in rows]
    series(fig, pts, RED, 5, dash=14)
    for p in pts:
        fig.circle(p[0], p[1], 7, fill=RED, outline=WHITE, width=2)
    for r in rows:
        if r['speed'] in (10, 40, 160):
            fig.text((px(math.log10(r['speed'])), py(r['rate']) - 16),
                     '{:.0f}%'.format(r['rate'] * 100), 38, color=TEAL, anchor='ma')
    yy = note(fig, y1 + 130,
              '40 m/s 的子弹每步走 0.67 m，墙只有 0.1 m：84% 的情形采样点直接从墙的一侧'
              '跳到另一侧，碰撞检测一次都没触发。实测与闭式曲线吻合，'
              '因为中靶只取决于墙心离采样点多远，与墙本身无关。')
    save(fig, '06-tunnel.png', '穿透率随速度变化')


# ---------------------------------------------------------------- 图 10

def fig10():
    fig, y = new(7, '要几刀才切得动',
                 '把一个大步切成 n 个小步，每个小步的位移不超过墙厚，'
                 '离散采样就不会整块跳过。')
    cols = [(44, 'la'), (350, 'la'), (600, 'la'), (1014, 'ra')]
    y = table(fig, y + 30, cols, [
        [('速度 m/s', INK_SOFT, True), ('每步位移 m', INK_SOFT, True),
         ('需要的子步', INK_SOFT, True), ('每小步 m', INK_SOFT, True)],
        [('10', INK, False), ('0.167', INK, False), ('2', TEAL, True), ('0.083', INK, False)],
        [('20', INK, False), ('0.333', INK, False), ('4', TEAL, True), ('0.083', INK, False)],
        [('40', INK, False), ('0.667', INK, False), ('7', TEAL, True), ('0.095', INK, False)],
        [('80', INK, False), ('1.333', INK, False), ('14', TEAL, True), ('0.095', INK, False)],
        [('160', INK, False), ('2.667', INK, False), ('27', TEAL, True), ('0.099', INK, False)],
    ])
    yy = note(fig, y + 40,
              '子步数是 ⌈速度 × dt ÷ 墙厚⌉，代价是每帧的物理步数线性上涨——'
              '160 m/s 的子弹要 27 步。这也是为什么快速物体通常改用「扫掠」：'
              '一步就从上一个位置射到下一个位置，中间那段也参与判定。')
    save(fig, '07-substep.png', '不同速度需要的子步数')


# ---------------------------------------------------------------- 图 11

def fig11():
    fig, y = new(10, '时间本身也会漂',
                 '把 1/60 秒一帧一帧累加起来的误差，对数纵轴。'
                 '左边两柱是 60 帧，右边是一小时。')
    x0, y0, x1, y1 = 240, 350, 950, 600
    items = [('float64\n60 帧', 1.3e-15, TEAL, '1.3e−15 秒'),
             ('float32\n60 帧', 3.5e-7, AMBER, '3.5e−7 秒'),
             ('float32\n一小时', 2.79, RED, '2.79 秒')]

    def py(v):
        lv = math.log10(max(1e-16, v))
        return y1 - (lv + 16) / 17.0 * (y1 - y0)

    for e in (0, -4, -8, -12, -16):
        fig.line((x0, py(10.0 ** e)), (x1, py(10.0 ** e)), color=LIGHT, width=2)
        fig.text((x0 - 16, py(10.0 ** e) - 22), '1e%d' % e, 38, color=INK_SOFT, anchor='ra')
    fig.line((x0, y1), (x1, y1), color=INK, width=3)
    fig.line((x0, y0), (x0, y1), color=INK, width=3)
    for i, (name, v, col, label) in enumerate(items):
        cx = x0 + 120 + i * 270
        fig.rect(cx - 60, py(v), cx + 60, py(1e-16), fill=col, outline=None)
        fig.text((cx, py(1e-16) - 46), label, 38, color=col, anchor='ma')
        for j, line in enumerate(name.split('\n')):
            fig.text((cx, y1 + 20 + j * 48), line, 38, color=INK, anchor='ma')
    yy = note(fig, y1 + 150,
              'float32 只有 24 位有效位：累加到 1800 秒时一步 0.0167 秒只值 136 个 ulp，'
              '舍掉的零头方向一致，一小时就少了 2.79 秒。另外 (1 + 1e16) − 1e16 在 float64 '
              '里等于 0，而 1 + (1e16 − 1e16) 等于 1——加法不满足结合律。')
    save(fig, '10-float.png', '时间累加的浮点误差')


# ---------------------------------------------------------------- 图 12

def fig12():
    fig, y = new(11, '差一点点，越差越远',
                 '双摆，初始角度只差 1e-9 弧度（float32 的一个末位）。'
                 '纵轴是两个解在状态空间里的距离，对数轴。')
    rows = R['chaos']['rows']
    x0, y0, x1, y1 = 210, y + 70, 950, 530
    px, py = axes(fig, x0, y0, x1, y1, (0.0, 20.0), (-9.0, 1.0),
                  (0, 5, 10, 15, 20), (-9, -6, -3, 0), '秒', 'log10(两个解的距离)')
    pts = [(px(r['t']), py(max(-9.0, r['log10']))) for r in rows]
    series(fig, pts, TEAL, 5)
    fig.line((x0, py(0.0)), (x1, py(0.0)), color=RED, width=3, dash=12)
    fig.text((x0 + 10, py(0.0) + 12), '距离 1 弧度：已经完全对不上', 38, color=RED)
    fig.text((px(10.0) + 12, py(-4.9) - 30), '10 秒：1.2e−5', 38, color=INK_SOFT)
    yy = note(fig, y1 + 130,
              '1e-9 的差别在前 5 秒几乎看不出来，10 秒后是十万分之一，20 秒后两个摆已经'
              '指向完全不同的方向。所以「固定 dt + 同一个浮点库」也不足以保证回放一致：'
              '编译器的 FMA、x87 的 80 位中间结果、不同 CPU 的数学函数都能制造 1e-9。')
    save(fig, '11-chaos.png', '双摆对初值的敏感')


# ---------------------------------------------------------------- 图 13

def fig13():
    fig, y = new(13, '三句话')
    y = bullets(fig, y + 40, [
        '物理要按固定步长走：先累加真实时间，再以 dt = 1/60 为单位一格一格地推进。'
        '帧率只影响画面，不影响模拟的结果。',
        '固定步长的代价是补帧：一帧可能要跑 0、1、2 步，快的时候还要插值。'
        '必须给它一个上限，否则一次卡顿会把自己拖进死亡螺旋。',
        '「固定 dt」不等于「可复现」：浮点加法不满足结合律，编译器和 CPU 的一点差别'
        '会在几十秒后放大成完全不同的世界。要复现就存输入，或者干脆存状态。',
    ], accent=TEAL)
    save(fig, '13-takeaways.png', '三句话')


def cover():
    fig = Fig(1080, width=1080)
    fig.rect(0, 0, 1080, 1080, fill=BG, outline=None)
    fig.rect(0, 0, 1080, 12, fill=TEAL, outline=None)
    fig.text((80, 150), '一秒', 100, bold=True)
    fig.text((80, 280), '就是六十步', 100, bold=True)
    fig.text((80, 430), '固定时间步长：帧率不应该改掉物理', 44, color=INK_SOFT)
    mono(fig, (80, 530), 'dt = 1/60 s', 42, color=TEAL)
    fig.text((80, 620), '60 fps 起跳的最高点：决算 1.000 m，连续解 1.067 m', 42, color=INK)
    fig.text((80, 690), '30 fps：0.933 m，矮了 12.5%', 42, color=INK)
    fig.text((80, 790), '每步开销 16 ms 时，稳态帧时间 500 ms', 42, color=INK)
    fig.text((80, 880), '这就是死亡螺旋', 86, color=RED)
    fig.text((80, 990), '2027-02-22', 40, color=GRAY)
    fig.trim(margin=60)
    fig.im = fig.im.crop((0, 0, 1080, 1080))
    fig.im.save(ART / 'cover.png')
    print('   cover.png', (ART / 'cover.png').stat().st_size, 'bytes')


def main():
    for fn in (fig01, fig02, fig06, fig07, fig08, fig09, fig10, fig04, fig05,
               fig11, fig12, fig03, fig13):
        print(fn.__name__)
        fn()
    META.sort(key=lambda r: r['path'])
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, indent=1, ensure_ascii=False))
    print('wrote', HERE / 'figure-metadata.json', len(META), 'figures')
    cover()


if __name__ == '__main__':
    main()
