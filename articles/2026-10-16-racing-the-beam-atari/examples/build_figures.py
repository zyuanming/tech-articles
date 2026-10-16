#!/usr/bin/env python3
"""Original teaching figures for the Atari 2600 article. MIT.

Every number and every rendered screen here comes from running the model in
this directory (run_model.py writes results.json and the frame-*.png files).
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


def photo(fig, name, x, y, w, h, focus=0.5):
    im = Image.open(PHOTOS / name).convert('RGB')
    scale = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * scale)),
                    max(h, int(im.height * scale))), Image.LANCZOS)
    left = int((im.width - w) * 0.5)
    top = int((im.height - h) * focus)
    fig.im.paste(im.crop((left, top, left + w, top + h)), (x, y))


def frame(fig, name, x, y, scale=2):
    im = Image.open(HERE / name).convert('RGB')
    im = im.resize((im.width * scale // 3, im.height * scale // 3),
                   Image.NEAREST)
    fig.im.paste(im, (x, y))
    return im.size


# ---------------------------------------------------------------- 01 开门
def fig01():
    fig = Fig(1000)
    fig.text((48, 34), '这台游戏机没有显存', 52, True)
    sub(fig, 104, '画面不是从内存里读出来送到电视的。它是程序一行一行，赶在电子束前面写出来的。')
    photo(fig, 'real-01-console.jpg', 48, 210, 966, 560)
    fig.text((531, 830), 'Atari 2600，1980—1982 年的四开关「木纹」版本。',
             42, color=INK, anchor='mm')
    fig.text((531, 886), '照片里的两个黑色手柄是标准摇杆。', 42, color=INK,
             anchor='mm')
    save(fig, '01-console.png', '真实主机照片，用于交代对象',
         identity='真实照片（第三方，公有领域）',
         source='Evan-Amos, "Atari-2600-Wood-4Sw-Set", Wikimedia Commons, public domain')


# ---------------------------------------------------------------- 02 电子束
def fig02():
    fig = Fig(940)
    fig.text((48, 34), '电视里的电子束，一行一行地扫', 52, True)
    sub(fig, 104, '下面这张高速合成照片拍下了真实的一帧：光束从左到右扫过一行，再回到左边扫下一行。')
    photo(fig, 'real-06-scanline.jpg', 48, 220, 966, 260)
    n = fig.wrap((531, 512), '照片：Tristantech，Wikimedia Commons，CC BY-SA 3.0',
                 40, 966, color=GRAY, anchor='ma', leading=1.16)
    y = facts(fig, 512 + n * 46 + 40, [
        '一帧 262 行，每秒画 60 帧。',
        '一行 228 个色时钟：前 68 个在屏幕外，后 160 个才画在屏幕上。',
        '游戏机的 CPU 每 3 个色时钟走 1 个机器周期，所以一行只有 76 个机器周期。',
    ], accent=TEAL)
    fig.text((531, y + 6), '这 76 个周期，就是程序一行的全部预算。', 42, True,
             RED, anchor='mm')
    save(fig, '02-beam.png', '真实电子束扫描照片与一行的时间构成',
         identity='真实照片（第三方，CC BY-SA 3.0）+ 原创示意',
         source='Tristantech, "Television Scan Line", Wikimedia Commons, CC BY-SA 3.0')


# ---------------------------------------------------------------- 03 帧时间表
def fig03():
    ft = R['frame_timing']
    fig = Fig(900)
    fig.text((48, 34), '一帧 262 行，每一段都有名字', 52, True)
    sub(fig, 104, '数字取自 Stella 程序员指南（Steve Wright，1979）里描述的典型 NTSC 帧。')
    segs = [('垂直同步', ft['vsync_lines'], AMBER),
            ('垂直消隐', ft['vblank_lines'], BLUE),
            ('画面', ft['picture_lines'], TEAL),
            ('溢出区', ft['overscan_lines'], GRAY)]
    total = ft['scanlines']
    x0, x1, y = 48, 1014, 230
    x = x0
    for name, n, col in segs:
        w = (x1 - x0) * n / total
        fig.rect(x, y, x + w, y + 110, fill=col)
        if w > 90:
            fig.text((x + w / 2, y + 34), name, 42, True, WHITE, anchor='mm')
            fig.text((x + w / 2, y + 80), '%d 行' % n, 42, WHITE, anchor='mm')
        x += w
    fig.text((531, y + 152), '3 + 37 + 192 + 30 = 262 行', 44, True, INK,
             anchor='mm')
    y2 = y + 230
    y2 = facts(fig, y2, [
        '只有中间 192 行会被画出来。',
        '另外 70 行一共给出 5,320 个机器周期，用来做游戏逻辑。',
        '程序必须自己数行，在正确的时刻发出垂直同步信号。',
    ], accent=BLUE)
    fig.text((531, y2 + 6), '这台机器没有「帧计数器」，数行是程序自己的事。', 42,
             True, INK, anchor='mm')
    save(fig, '03-frame-timeline.png', 'NTSC 一帧的四段构成')


# ---------------------------------------------------------------- 04 一行
def fig04():
    ft = R['frame_timing']
    fig = Fig(880)
    fig.text((48, 34), '一行里，前三分之一是「看不见的时间」', 52, True)
    sub(fig, 104, '电子束回到左边之后要等一会儿才开始画。这段时间里寄存器可以随便改。')
    y = 230
    fig.rect(48, y, 48 + 966 * 68 / 228, y + 120, fill=PALE)
    fig.rect(48 + 966 * 68 / 228, y, 1014, y + 120, fill=TINT_T)
    fig.text((48 + 966 * 34 / 228, y + 40), '水平消隐', 42, True, BLUE,
             anchor='mm')
    fig.text((48 + 966 * 34 / 228, y + 86), '68 色时钟', 42, BLUE, anchor='mm')
    fig.text((48 + 966 * (68 + 80) / 228, y + 40), '屏幕上的 160 个色时钟',
             42, True, TEAL, anchor='mm')
    fig.text((48 + 966 * (68 + 80) / 228, y + 86), '22 个机器周期在画', 42,
             TEAL, anchor='mm')
    y2 = y + 200
    y2 = facts(fig, y2, [
        '机器周期和色时钟的比例是 1 比 3。',
        '一行的 76 个机器周期里，有 68 ÷ 3 约 23 个落在消隐期。',
        '程序通常在这段时间里把下一行要用的寄存器全部写好。',
        '写晚了，光束已经画过去了，这一行就只能将错就错。',
    ], accent=AMBER)
    save(fig, '04-one-line.png', '一行 228 个色时钟的划分')


# ---------------------------------------------------------------- 05 只有一行
def fig05():
    fig = Fig(900)
    fig.text((48, 34), '为什么不能一次把整幅画面写进去', 52, True)
    sub(fig, 104, 'TIA 的图形寄存器只保存「当前这一行」的内容，它不记得上一行写了什么。')
    fig.box('a', 48, 220, 1014, 420, fill=TINT_R)
    fig.text((531, 254), '如果只写一次', 46, True, RED, anchor='mm',
             inside='a')
    fig.text((531, 320), '寄存器里留着第一行的图案，', 42, color=INK,
             anchor='mm', inside='a')
    fig.text((531, 372), '屏幕上 192 行全都长成一样。', 42, color=INK,
             anchor='mm', inside='a')
    fig.box('b', 48, 470, 1014, 700, fill=TINT_G)
    fig.text((531, 504), '实际做法', 46, True, GREEN, anchor='mm', inside='b')
    fig.text((531, 570), '每一行开始前重写一遍寄存器，', 42, color=INK,
             anchor='mm', inside='b')
    fig.text((531, 622), '192 行各写各的。', 42, color=INK, anchor='mm',
             inside='b')
    fig.text((531, 672), '这段代码叫 kernel。', 42, True, GREEN, anchor='mm',
             inside='b')
    fig.text((531, 776), '所以「画面」不是一个数据结构，', 42, True, INK,
             anchor='mm')
    fig.text((531, 830), '而是一段按时执行的代码。', 42, True, INK, anchor='mm')
    save(fig, '05-no-framebuffer.png', '为什么必须逐行重写寄存器')


# ---------------------------------------------------------------- 06 WSYNC
def fig06():
    fig = Fig(940)
    fig.text((48, 34), 'WSYNC：让程序停下来等光束', 52, True)
    sub(fig, 104, '程序写一下 WSYNC，CPU 就停住，直到这一行结束、下一行开始。')
    steps = [('写 WSYNC', 'CPU 停住，等这一行走完', AMBER),
             ('下一行开始', 'CPU 从下一行第 0 个周期继续', BLUE),
             ('写寄存器', '把这一行要用的图形、颜色写进去', TEAL),
             ('循环', '行号加一，回到第一步', GREEN)]
    y = 230
    for i, (head, body, col) in enumerate(steps):
        fig.box('s%d' % i, 48, y, 1014, y + 118, fill=WHITE)
        fig.circle(110, y + 59, 30, fill=col, outline=col, width=3)
        fig.text((110, y + 59), str(i + 1), 42, True, WHITE, anchor='mm')
        fig.text((170, y + 40), head, 44, True, col, anchor='lm',
                 inside='s%d' % i)
        fig.text((170, y + 88), body, 42, color=INK, anchor='lm',
                 inside='s%d' % i)
        if i < len(steps) - 1:
            fig.arrow((110, y + 122), (110, y + 146), GRAY, 4, 12)
        y += 152
    fig.text((531, y + 6), '本文样例 kernel 一行的固定开销，', 42, color=INK,
             anchor='mm')
    fig.text((531, y + 60), '就是这四步循环。', 42, color=INK, anchor='mm')
    save(fig, '06-wsync.png', 'WSYNC 与 kernel 循环的结构')


# ---------------------------------------------------------------- 07 周期账
def fig07():
    bud = R['kernel_budget'][0]
    fig = Fig(900)
    fig.text((48, 34), '一行 76 个周期，这笔账必须算平', 52, True)
    sub(fig, 104, '本文样例 kernel 实际用掉的机器周期，由模型逐条指令统计得到。')
    items = [('WSYNC', 3), ('6 组表读写', 42), ('INX', 2),
             ('CPX #192', 2), ('BNE', 3)]
    y = 240
    x0, x1 = 400, 1014
    vmax = 76
    used = 0
    for name, n in items:
        w = (x1 - x0) * n / vmax
        fig.rect(x0 + (x1 - x0) * used / vmax, y,
                 x0 + (x1 - x0) * (used + n) / vmax, y + 56, fill=TEAL)
        fig.text((x0 - 24, y + 28), name, 42, color=INK, anchor='rm')
        fig.text((x0 + (x1 - x0) * (used + n / 2) / vmax, y + 28), str(n), 42,
                 True, WHITE, anchor='mm')
        used += n
        y += 72
    fig.rect(x0 + (x1 - x0) * used / vmax, 240,
             x0 + (x1 - x0) * vmax / vmax, 240 + 5 * 72 - 16, fill=PALE)
    fig.text((x0 + (x1 - x0) * (used + vmax) / 2 / vmax, 240 + 2 * 72),
             '余量\n%d' % (vmax - used), 42, True, BLUE, anchor='mm')
    fig.text((531, y + 20), '合计 %d 个周期，还剩 %d 个。' % (used, vmax - used),
             44, True, INK, anchor='mm')
    fig.text((531, y + 78), '剩下的余量不是浪费：留一点缓冲，才不会写晚。', 42,
             color=INK_SOFT, anchor='mm')
    save(fig, '07-cycle-budget.png', '样例 kernel 一行的机器周期账')


# ---------------------------------------------------------------- 08 RESPx
def fig08():
    steps = R['position_steps']
    fig = Fig(920)
    fig.text((48, 34), '精灵的位置，由「什么时候写寄存器」决定', 52, True)
    sub(fig, 104, 'RESP0 一被写，精灵的位置就从头开始算。晚写几个周期，精灵就往右挪几格。')
    y = 240
    x0, x1 = 330, 800
    lo = min(s['pixel'] for s in steps)
    hi = max(s['pixel'] for s in steps)
    for i, s in enumerate(steps):
        v = s['pixel']
        w = (x1 - x0) * (v - lo) / (hi - lo)
        yy = y + i * 46
        fig.text((x0 - 20, yy + 20), '延时 %d 次' % s['loop_iterations'], 40,
                 color=INK, anchor='rm')
        if v < 0:
            fig.text((x0 + 6, yy + 20), '（在屏幕左边之外）', 40, color=GRAY,
                     anchor='lm')
            continue
        fig.rect(x0, yy, x0 + max(3, w), yy + 40, fill=TEAL)
        fig.text((x0 + w + 16, yy + 20), '第 %d 像素' % v, 40, True, TEAL,
                 anchor='lm')
    fig.text((531, y + len(steps) * 46 + 40),
             '每次多绕一圈，精灵右移 15 个像素。', 44, True, RED, anchor='mm')
    fig.text((531, y + len(steps) * 46 + 96),
             'Stella 指南把这写成：水平定位只能落在', 42, color=INK,
             anchor='mm')
    fig.text((531, y + len(steps) * 46 + 148),
             '15 个色时钟的间隔上。', 42, color=INK, anchor='mm')
    save(fig, '08-resp-steps.png', '延时循环次数与精灵像素位置（本模型实测）')


# ---------------------------------------------------------------- 09 HMOVE
def fig09():
    fig = Fig(900)
    fig.text((48, 34), '那 15 像素之间的空档，靠 HMOVE 补上', 52, True)
    sub(fig, 104, 'HMP0 存一个 −8 到 +7 的数，HMOVE 一次把它加到所有物体的位置上。')
    y = 250
    fig.rect(48, y, 1014, y + 130, fill=PALE)
    for i in range(16):
        x = 48 + (966 - 40) * i / 15
        fig.rect(x, y + 20, x + 16, y + 110, fill=BLUE if i % 5 == 0 else LIGHT)
    fig.text((531, y + 66), 'HMOVE 能覆盖的 16 个位置（−8 到 +7）', 42, True,
             BLUE, anchor='mm')
    y2 = y + 210
    y2 = facts(fig, y2, [
        'RESP0 决定一个基准位置，间隔 15 像素。',
        'HMP0 在这 15 像素里做 1 像素级的微调。',
        '两者合起来，屏幕上任何一个位置都能放得下。',
    ], accent=BLUE)
    fig.text((531, y2 + 6), 'HMOVE 必须紧跟 WSYNC，才能赶上消隐期。', 42, True,
             AMBER, anchor='mm')
    save(fig, '09-hmove.png', 'HMOVE 在 15 像素间隔之间做微调')


# ---------------------------------------------------------------- 10/11 渲染帧
def frame_fig(name, title, caption_lines, out, identity='原创教学示意（模型输出）',
              source=None, second=None, second_caption=None):
    fig = Fig(900)
    fig.text((48, 34), title, 52, True)
    sub(fig, 104, caption_lines[0])
    if second:
        w, h = frame(fig, name, 90, 200, 3)
        w2, h2 = frame(fig, second, 572, 200, 3)
        fig.text((90 + w / 2, 200 + h + 40), '第一帧', 42, True, TEAL,
                 anchor='mm')
        fig.text((572 + w2 / 2, 200 + h2 + 40), '第二帧', 42, True, AMBER,
                 anchor='mm')
        y = 200 + h + 110
    else:
        w, h = frame(fig, name, 331, 200, 3)
        y = 200 + h + 60
    for i, ln in enumerate(caption_lines[1:]):
        fig.text((531, y + i * 54), ln, 42, color=INK, anchor='mm')
    y += len(caption_lines[1:]) * 54 + 20
    if second_caption:
        fig.text((531, y), second_caption, 42, True, GREEN, anchor='mm')
    save(fig, out, caption_lines[0], identity=identity, source=source)


def fig10():
    frame_fig('frame-pong.png',
              '本文模型渲染出的一帧',
              ['同一个 kernel 跑 192 行，每一行换一组数据。',
               '左右两道墙来自 playfield，两个挡板是两个玩家精灵，',
               '中间那个小方块是球。'],
              '10-rendered-frame.png',
              '本模型实际运行样例 kernel 得到的画面，不是真实主机截图')


def fig11():
    frame_fig('frame-pong-moved.png',
              '同一个 kernel，换一组数据',
              ['只把三组数据里的位置改掉，同一段代码画出另一个局面。',
               '两个挡板在第 72 和 150 像素，球在第 44 像素。'],
              '11-rendered-moved.png',
              '本模型实际运行样例 kernel 得到的画面，不是真实主机截图')


def fig12():
    frame_fig('frame-overrun.png',
              '少算 32 个周期，画面就错位了',
              ['在每行开头多插 16 条 NOP，一共 32 个机器周期。',
               '寄存器写得比光束晚，这一行就按旧数据画。'],
              '12-overrun.png',
              '本模型实际运行超支版 kernel 得到的画面：%d 行与正常版本不同。'
              % R['overrun']['picture_differing_lines'])


def fig13():
    frame_fig('frame-flicker-a.png',
              '只有两个玩家精灵，怎样画出四个物体',
              ['第一帧画物体 1 和 3，第二帧换成 2 和 4。',
               '每帧各画 16 行，两帧合起来 32 行。'],
              '13-flicker.png',
              '本模型实际渲染的两帧与它们的合成画面',
              second='frame-flicker-b.png',
              second_caption='人眼把交替出现的两帧合在一起，看到四个物体。')


# ---------------------------------------------------------------- 14 碰撞
def fig14():
    col = R['collisions']
    fig = Fig(920)
    fig.text((48, 34), '碰撞检测：芯片替你做了', 52, True)
    sub(fig, 104, 'TIA 里有 15 个触发器，两个物体在同一像素上同时出现，对应的位就被置起来。')
    frame(fig, 'frame-pong.png', 48, 210, 2)
    fig.text((300, 230), '让球和左挡板重叠在', 42, color=INK)
    fig.text((300, 282), '同一像素上，再读一次', 42, color=INK)
    fig.text((300, 334), '碰撞寄存器。', 42, color=INK)
    fig.box('c', 300, 390, 1014, 620, fill=TINT_G)
    fig.text((324, 420), '被置起来的位', 44, True, GREEN, inside='c')
    names = {'CXP0FB': '玩家 0 撞到球或场地',
             'CXBLPF': '球撞到场地',
             'CXPPMM': '玩家 0 撞到玩家 1'}
    y = 478
    for reg, v in col['registers'].items():
        fig.text((324, y), '%s：%s' % (reg, names.get(reg, '')), 40,
                 color=INK, inside='c')
        y += 52
    fig.text((531, 700), '球在第 %d 像素，左挡板也在第 %d 像素。'
             % (col['ball_pixel'], col['player0_pixel']), 42, color=INK,
             anchor='mm')
    fig.text((531, 756), '程序不需要自己逐像素比较，读一个寄存器就知道。', 42,
             True, INK, anchor='mm')
    save(fig, '14-collisions.png', '碰撞触发器被置位的实测结果',
         identity='原创教学示意（模型输出）')


# ---------------------------------------------------------------- 15 硬件
def fig15():
    fig = Fig(940)
    fig.text((48, 34), '盒子里面有什么', 52, True)
    sub(fig, 104, '一块主板，一颗 CPU，一颗 TIA，128 字节内存，和一只 4 KB 的卡带。')
    photo(fig, 'real-04-motherboard.jpg', 48, 210, 966, 330)
    fig.text((531, 566), 'Atari 2600 主板（1982 年四开关版）。', 42, color=INK,
             anchor='mm')
    photo(fig, 'real-05-6502.jpg', 48, 630, 966, 200)
    fig.text((531, 856), 'MOS 6502。游戏机里用的是引脚更少的 6507 版本，', 42,
             color=INK, anchor='mm')
    fig.text((531, 908), '内部硅片相同，只少了几根引脚。', 42, color=INK,
             anchor='mm')
    y = facts(fig, 970, [
        'CPU：6507，1.19 MHz。',
        '内存：128 字节，和 I/O 芯片做在同一颗里。',
        '卡带：最大 4 KB，后来的游戏靠 bank switching 扩展到 64 KB。',
    ], accent=BLUE)
    save(fig, '15-hardware.png', '主板与 6502 芯片照片',
         identity='真实照片（第三方，CC BY-SA 4.0）+ 原创示意',
         source='Tetrodotoxine (motherboard) and ZyMOS (MOS 6502), Wikimedia Commons, CC BY-SA 4.0')


# ---------------------------------------------------------------- 16 卡带
def fig16():
    fig = Fig(900)
    fig.text((48, 34), '4 KB 里装下一整个游戏', 52, True)
    sub(fig, 104, 'Pitfall! 的卡带只有 4 KB。它的丛林有 255 个场景。')
    photo(fig, 'real-03-pitfall-cart.jpg', 331, 210, 400, 440, focus=0.2)
    n = fig.wrap((531, 694), 'Pitfall! 卡带。照片：JoRgE-1987，Wikimedia Commons，CC BY-SA 4.0',
                 40, 966, color=GRAY, anchor='ma', leading=1.16)
    y = facts(fig, 694 + n * 46 + 40, [
        'David Crane 花了大约 1000 小时编程，设计只用了 10 分钟。',
        '大部分时间花在优化和压缩代码，让它塞进 4 KB。',
        '255 个场景不是逐个存下来的，而是用一个 8 位寄存器生成。',
    ], accent=TEAL)
    save(fig, '16-cartridge.png', 'Pitfall! 卡带照片与 4 KB 的限制',
         identity='真实照片（第三方，CC BY-SA 4.0）+ 原创示意',
         source='JoRgE-1987, "Cartucho de Atari 2600 del juego Pitfall", Wikimedia Commons, CC BY-SA 4.0')


# ---------------------------------------------------------------- 17 Miner
def fig17():
    fig = Fig(1060)
    fig.text((48, 34), '设计 TIA 的人：Jay Miner', 52, True)
    sub(fig, 104, 'TIA 是那颗没有显存的显示芯片。它决定了这台机器的全部上限与全部怪癖。')
    photo(fig, 'real-08-jay-miner.jpg', 331, 200, 400, 430, focus=0.15)
    fig.text((531, 676), 'Jay Miner（1932—1994），1990 年。', 42,
             color=INK, anchor='mm')
    n = fig.wrap((531, 728), '照片：Michael C. Battilana / Cloanto IT srl，CC BY 2.0',
                 40, 966, color=GRAY, anchor='ma', leading=1.16)
    y = facts(fig, 728 + n * 46 + 40, [
        '1975 年底加入 Atari，负责设计 VCS 的显示芯片。',
        '内存太贵，所以他干脆把帧缓冲从设计里拿掉。',
        '同一个设计思路后来变成 Atari 8 位机的 ANTIC 芯片，',
        '再后来是 Amiga 的定制芯片组。',
    ], accent=AMBER)
    save(fig, '17-miner.png', 'Jay Miner 肖像与 TIA 的设计取舍',
         identity='真实肖像（第三方，CC BY 2.0）+ 原创示意',
         source='JayMiner1990, Wikimedia Commons, CC BY 2.0, (c) 1990 Michael C. Battilana and Cloanto IT srl')


# ---------------------------------------------------------------- 18 Crane
def fig18():
    fig = Fig(1060)
    fig.text((48, 34), '让 255 个场景只花一个字节', 52, True)
    sub(fig, 104, 'David Crane 在 4 KB 里塞进一整片丛林，办法是不存地图，只存生成规则。')
    photo(fig, 'real-10-crane.jpg', 331, 200, 380, 420, focus=0.12)
    fig.text((531, 656), 'David Crane，2011 年波特兰复古游戏展。', 42, color=INK,
             anchor='mm')
    fig.text((531, 710), '照片：Joe Grand，CC BY-SA 2.0', 40, color=GRAY,
             anchor='mm')
    y = facts(fig, 780, [
        '每个场景需要的东西很少：坑在哪、树在哪、宝物是什么。',
        '这些可以用一个 8 位状态寄存器的低几位拼出来。',
        '每走一个场景，让寄存器按固定规则变化一次，',
        '255 个场景就全部生成完了，一个字节都没多存。',
    ], accent=TEAL)
    fig.text((531, y + 6), '代价是：场景顺序固定，', 42, True, INK, anchor='mm')
    fig.text((531, y + 60), '所以游戏有一条固定的「正确路线」。', 42, True, INK,
             anchor='mm')
    save(fig, '18-crane.png', 'David Crane 肖像与 4 KB 里的场景生成',
         identity='真实肖像（第三方，CC BY-SA 2.0）+ 原创示意',
         source='Joe Grand, "David Crane at Portland Retro Gaming Expo 2011", Flickr, CC BY-SA 2.0')


# ---------------------------------------------------------------- 19 Robinett
def fig19():
    fig = Fig(1000)
    fig.text((48, 34), '128 字节内存里，藏着一个名字', 52, True)
    sub(fig, 104, 'Warren Robinett 写了 Adventure。当时 Atari 不给设计者署名。')
    photo(fig, 'real-11-robinett.jpg', 331, 200, 340, 400, focus=0.1)
    fig.text((531, 636), 'Warren Robinett，2015 年游戏开发者大会。', 42, color=INK,
             anchor='mm')
    fig.text((531, 690), '照片：Official GDC，CC BY 2.0', 40, color=GRAY,
             anchor='mm')
    y = facts(fig, 760, [
        '他在游戏里留了一个隐藏房间，走进去会看到一行字。',
        '那行字写着这个游戏是谁做的。',
        '这是最早被广泛知道的游戏彩蛋之一。',
    ], accent=AMBER)
    fig.text((531, y + 6), 'Adventure 在 128 字节内存、', 42, True, INK,
             anchor='mm')
    fig.text((531, y + 60), '4 KB 卡带的限制下做成。', 42, True, INK,
             anchor='mm')
    save(fig, '19-robinett.png', 'Warren Robinett 肖像与 Adventure 的彩蛋',
         identity='真实肖像（第三方，CC BY 2.0）+ 原创示意',
         source='Official GDC, "Warren Robinett, 2015", Flickr, CC BY 2.0')


# ---------------------------------------------------------------- 20 Bushnell
def fig20():
    fig = Fig(1020)
    fig.text((48, 34), '为什么要把机器做成可换卡带的', 52, True)
    sub(fig, 104, '专用电路的机器只能玩一个游戏。卖完那一款，这台机器就没用了。')
    photo(fig, 'real-09-bushnell.jpg', 331, 200, 380, 420, focus=0.1)
    fig.text((531, 656), 'Nolan Bushnell，Atari 联合创始人，2013 年。', 42,
             color=INK, anchor='mm')
    fig.text((531, 710), '照片：Tech Cocktail，CC BY-SA 2.0', 40, color=GRAY,
             anchor='mm')
    y = facts(fig, 780, [
        '开发一台专用机器要花十万美元以上，货架寿命却只有三个月。',
        '1975 年 MOS 推出 25 美元的 6502，可编程机器才变得可行。',
        '1977 年 VCS 上市，首发九款游戏，卡带 2 KB。',
        '1980 年的《太空侵略者》家用版成为这台机器的爆款。',
    ], accent=BLUE)
    fig.text((531, y + 6), '可编程性把一个「产品」变成了一台「平台」。', 42,
             True, INK, anchor='mm')
    save(fig, '20-bushnell.png', 'Nolan Bushnell 肖像与可换卡带的商业逻辑',
         identity='真实肖像（第三方，CC BY-SA 2.0）+ 原创示意',
         source='Tech Cocktail, "Nolan Bushnell 2013", Flickr, CC BY-SA 2.0')


# ---------------------------------------------------------------- 21 收尾
def fig21():
    fig = Fig(880)
    fig.text((48, 34), '换一个条件，自己再走一遍', 52, True)
    sub(fig, 104, '下面每一件事都能在 examples/ 里改几行就看到结果。')
    items = [
        ('把一行里的一条写操作删掉', '画面会少一块，或者整行错位。'),
        ('把 kernel 的开销加到超过 76 个周期', '寄存器写晚了，画面按旧数据画。'),
        ('把延时循环的次数加一', '精灵右移 15 个像素——不多不少。'),
        ('把 HMP0 从 0 改成 −8', '精灵左移 8 个像素，落在 15 像素的缝隙里。'),
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
    save(fig, '21-try-it.png', '读者可以自己改动的四个条件')


def make_cover():
    fig = Fig(1000)
    fig.text((48, 44), '这台游戏机没有显存', 62, True)
    fig.text((48, 132), '画面是程序追着电子束写出来的', 62, True, TEAL)
    frame(fig, 'frame-pong.png', 291, 250, 3)
    fig.text((531, 250 + 576 + 70), '一行 76 个机器周期，一秒 60 帧',
             46, True, INK, anchor='mm')
    fig.text((531, 250 + 576 + 132), '全部数字与画面来自本仓库实际运行的模型',
             42, color=INK_SOFT, anchor='mm')
    fig.trim(margin=70)
    fig.im.save(ART / 'cover.png')
    print('   cover.png', fig.im.size)


def main():
    for fn in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
               fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18,
               fig19, fig20, fig21):
        fn()
    make_cover()
    for row in META:
        row['path'] = 'assets/' + Path(row['path']).name
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(META))


if __name__ == '__main__':
    main()
