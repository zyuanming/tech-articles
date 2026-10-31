#!/usr/bin/env python3
"""Original teaching figures for the Paxos article. MIT.

Message diagrams are drawn from results.json, which run_model.py produced by
running examples/paxos.py. The one figure that is a hand-built schedule (the
livelock) says so on the canvas and in sources.md.
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

PREPARE, PROMISE, ACCEPT, ACCEPTED = TEAL, BLUE, AMBER, GREEN
ROLE_COLOR = {'prepare': PREPARE, 'promise': PROMISE, 'reject': RED,
              'accept': ACCEPT, 'accepted': ACCEPTED}


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
             ylab=None):
        for v in yticks:
            yy = self.py(v)
            self.f.line((self.x0, yy), (self.x1, yy), color=LIGHT, width=2)
            self.f.text((self.x0 - 18, yy - 21), yfmt % v, 40, color=GRAY,
                        anchor='ra')
        for v in xticks:
            xx = self.px(v)
            self.f.line((xx, self.y0), (xx, self.y1), color=LIGHT, width=2)
            self.f.text((xx, self.y1 + 14), xfmt % v, 40, color=GRAY, anchor='ma')
        self.f.line((self.x0, self.y1), (self.x1, self.y1), color=GRAY, width=3)
        self.f.line((self.x0, self.y0), (self.x0, self.y1), color=GRAY, width=3)
        if ylab:
            self.f.text((self.x0, self.y0 - 58), ylab, 40, color=GRAY)
        if xlab:
            self.f.text((self.x1, self.y1 + 74), xlab, 40, color=GRAY, anchor='ra')

    def line(self, xs, ys, color, width=5, dash=None):
        pts = [(self.px(x), self.py(y)) for x, y in zip(xs, ys)]
        for a, b in zip(pts, pts[1:]):
            self.f.line(a, b, color=color, width=width, dash=dash)

    def bar(self, x, value, width_px, color):
        cx = self.px(x)
        self.f.rect(cx - width_px / 2, self.py(value), cx + width_px / 2,
                    self.py(0), fill=color, outline=None)
        self.f.text((cx, self.py(value) - 52), '%g' % value, 40, color=color,
                    anchor='ma', bold=True, allow_overlap=True)

    def hline(self, y, color=GRAY, dash=14):
        self.f.line((self.x0, self.py(y)), (self.x1, self.py(y)), color=color,
                    width=3, dash=dash)


class Seq:
    """A sequence diagram: actors on lifelines, messages as horizontal arrows.

    Lifelines are drawn a row at a time, so the canvas height follows the
    content instead of being pinned by one long vertical line.
    """

    def __init__(self, fig, actors, y, row=112):
        self.f = fig
        self.y = y
        self.row = row
        self.x = {key: x for key, x, _ in actors}
        self.actors = actors
        self.seg = None
        for key, x, name in actors:
            fig.text((x, y), name, 42, bold=True, anchor='ma')

    def start(self):
        self.y += 86
        self.seg = self.y - 22

    def _advance(self):
        if self.seg is not None and self.y - 22 > self.seg:
            for _key, x, _name in self.actors:
                self.f.line((x, self.seg), (x, self.y - 22), color=LIGHT, width=3)
        self.seg = self.y - 22

    def phase(self, text, color=INK):
        self.y += 44
        self.f.text((44, self.y), text, 40, color=color, bold=True)
        self.y += 84
        self._advance()
        return self.y

    def _arrow(self, xs, xd, color, width, dash=False):
        ax = xs + 14 if xd > xs else xs - 14
        bx = xd - 14 if xd > xs else xd + 14
        self.f.arrow((ax, self.y + 66), (bx, self.y + 66), color=color,
                     width=width, head=15, dash=14 if dash else None)

    def msg(self, src, dst, label, color=TEAL, dash=False, note_text=None):
        xs, xd = self.x[src], self.x[dst]
        self.f.text(((xs + xd) / 2, self.y), label, 40, color=color, anchor='ma')
        self._arrow(xs, xd, color, 5, dash)
        if note_text:
            self.f.text((1018, self.y), note_text, 40, color=GRAY, anchor='ra')
        self.y += self.row
        self._advance()
        return self.y

    def fan(self, src, dsts, label, color=TEAL, note_text=None):
        xs = self.x[src]
        self.f.text((xs, self.y), label, 40, color=color, anchor='ma')
        for dst in dsts:
            self._arrow(xs, self.x[dst], color, 4)
        if note_text:
            self.f.text((1018, self.y), note_text, 40, color=GRAY, anchor='ra')
        self.y += self.row
        self._advance()
        return self.y

    def fan_back(self, dsts, dst, label, color=BLUE, note_text=None):
        xd = self.x[dst]
        self.f.text((xd, self.y), label, 40, color=color, anchor='ma')
        for src in dsts:
            self._arrow(self.x[src], xd, color, 4)
        if note_text:
            self.f.text((1018, self.y), note_text, 40, color=GRAY, anchor='ra')
        self.y += self.row
        self._advance()
        return self.y


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    row['path'] = 'assets/' + name
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


FIVE = ['A1', 'A2', 'A3', 'A4', 'A5']


def machine(fig, x, y, w, h, name, sub, fill=WHITE, tag=None):
    fig.box(tag or name, x, y, x + w, y + h, fill=fill)
    fig.text((x + 26, y + 22), name, 42, bold=True, inside=tag or name)
    fig.text((x + 26, y + 84), sub, 40, color=INK_SOFT, inside=tag or name)


# ---------------------------------------------------------------- figures
def fig01():
    f, y = new(1, '五份副本，要写同一个值',
               '复制让系统在机器坏掉时还能活，代价是：同一件事现在有五个地方可以改。'
               '只要不是五台机器同时看到同一个顺序，它们就会慢慢变成两个系统。')
    machine(f, 60, y, 360, 150, '客户端', '写一个值，比如 X')
    for i, name in enumerate(FIVE):
        machine(f, 520, y + i * 170, 480, 140, name, '一份副本 + 一个磁盘')
        f.arrow((432, y + 75), (508, y + i * 170 + 70), color=GRAY, width=4)
    y += 5 * 170 + 20
    y = note(f, y, '每台机器都能单独响应写请求，网络随时可能把消息延迟、重排或丢掉。'
                   '于是问题变成：在只看得到部分回复的情况下，怎样保证「五台机器里不会有'
                   '两台对同一个位置给出不同的值」。')
    y = note(f, y, 'Paxos 是在 1990 年给出的一个答案。它不是算法竞赛里的技巧，'
                   '而是一条很具体的推理：任何两个多数派一定会重叠。',
             color=TEAL)
    save(f, '01-five-replicas.png', '五份副本必须对同一个值达成一致')


def fig02():
    f, y = new(2, '网络不是一根管道',
               '同一时刻发出的两条消息，到达顺序可以反过来；慢一点的那条，'
               '可能永远不来了。下面三种情况在真实机房里每天都在发生。')
    rows = [('正常', '先发先到', TEAL), ('延迟', '第二条先到', AMBER),
            ('丢包', '第一条不见了', RED)]
    for i, (label, sub, color) in enumerate(rows):
        top = y + i * 300
        f.text((44, top), label, 42, bold=True, color=color)
        f.text((44, top + 56), sub, 40, color=INK_SOFT)
        f.line((330, top + 30), (330, top + 200), color=INK, width=4)
        f.line((820, top + 30), (820, top + 200), color=INK, width=4)
        f.text((330, top - 8), 'P', 40, bold=True, anchor='ma')
        f.text((820, top - 8), 'A', 40, bold=True, anchor='ma')
        if label == '正常':
            f.arrow((344, top + 60), (806, top + 60), color=TEAL, width=4)
            f.arrow((344, top + 140), (806, top + 140), color=TEAL, width=4)
            f.text((880, top + 44), '1 → 2', 40, color=GRAY)
        elif label == '延迟':
            f.arrow((344, top + 60), (806, top + 60), color=AMBER, width=4)
            f.arrow((344, top + 140), (806, top + 140), color=AMBER, width=4)
            f.text((880, top + 44), '2 先到', 40, color=GRAY)
        else:
            f.arrow((344, top + 60), (620, top + 60), color=RED, width=4,
                    dash=14)
            f.text((640, top + 34), '?', 40, color=RED)
            f.arrow((344, top + 140), (806, top + 140), color=RED, width=4)
            f.text((880, top + 124), '只有 2', 40, color=GRAY)
    y += 3 * 300 + 10
    y = note(f, y, '所以「等所有回复到齐再决定」是不行的：一台机器挂了，你就永远等不到。'
                   '只能靠「够多了就行」——多数派。')
    save(f, '02-network-reorders.png', '消息会延迟、重排、丢失')


def fig03():
    f, y = new(4, '各自投票，会投出两个结果',
               '最直接的办法：谁先来就听谁的，五台机器各记各的。'
               '问题是三台机器就是一个多数派，而五台机器里有两个三台。')
    def row(title, group, value, color, top):
        f.text((44, top), title, 42, bold=True, color=color)
        for i, name in enumerate(FIVE):
            x = 300 + i * 145
            hit = name in group
            f.box(name + title, x, top + 60, x + 128, top + 210,
                  fill=TINT_T if hit and color == TEAL else
                  (TINT_R if hit else WHITE),
                  outline=color if hit else LIGHT)
            f.text((x + 64, top + 80), name, 40, anchor='ma',
                   inside=name + title)
            f.text((x + 64, top + 142), value if hit else '—', 42, anchor='ma',
                   color=color if hit else GRAY, inside=name + title, bold=hit)
        return top + 268
    y = row('客户 A 先到：{A1 A2 A3} 收到 X', {'A1', 'A2', 'A3'}, 'X', TEAL, y)
    y = row('客户 B 稍后：{A3 A4 A5} 收到 Y', {'A3', 'A4', 'A5'}, 'Y', RED, y)
    y = note(f, y, 'A3 两个都收下了。现在任何两个读者去问多数派，都可能得到不同的答案：'
                   '问 {A1 A2 A3} 得到 X，问 {A3 A4 A5} 得到 Y，而两边都「合法」。',
             color=RED)
    save(f, '04-two-majorities.png', '朴素投票会选出两个互相矛盾的值')


def fig04():
    f, y = new(3, '两个多数派一定重叠',
               '五个位置里挑三个，剩下的只有两个。第二个三票组想完全不碰第一个，'
               '需要三个空位，可空位只有两个——所以它必然踩到第一个里的某一台。')
    f.text((44, y), '第一个多数派 {A1 A2 A3}', 42, bold=True, color=TEAL)
    for i, name in enumerate(FIVE):
        x = 300 + i * 145
        f.box('s1' + name, x, y + 60, x + 120, y + 170,
              fill=TINT_T if name in ('A1', 'A2', 'A3') else WHITE)
        f.text((x + 60, y + 96), name, 40, anchor='ma', inside='s1' + name)
    y += 240
    f.text((44, y), '第二个多数派 {A3 A4 A5}', 42, bold=True, color=RED)
    for i, name in enumerate(FIVE):
        x = 300 + i * 145
        f.box('s2' + name, x, y + 60, x + 120, y + 170,
              fill=TINT_R if name in ('A3', 'A4', 'A5') else WHITE)
        f.text((x + 60, y + 96), name, 40, anchor='ma', inside='s2' + name)
    f.circle(300 + 2 * 145 + 60, y + 115, 96, outline=AMBER, width=6)
    f.text((300 + 2 * 145 + 60, y + 230), '重叠', 40, color=AMBER, anchor='ma')
    y += 320
    y = note(f, y, '一般地，N 台机器里，任何两个 (N/2 + 1) 台的集合至少重叠一台：'
                   '两者大小相加超过 N，抽屉原理。')
    y = note(f, y, '这一台重叠的机器，就是全部安全性的来源。它见过什么，'
                   '下一个提案者就必须知道什么——Paxos 的两个阶段，'
                   '做的事就是「先问它，再决定」。', color=TEAL)
    save(f, '03-quorums-intersect.png', '任意两个多数派必然相交')


def fig05():
    f, y = new(5, '三个角色，一台机器可以全干',
               'Paxos 里没有「主节点」这个身份。只有三种动作：提议、表态、学习。')
    machine(f, 44, y, 280, 170, '提议者', '挑编号和值')
    machine(f, 368, y, 320, 170, '接受者 × 5', '记住两件事', fill=TINT_B)
    machine(f, 732, y, 286, 170, '学习者', '转告结果')
    f.arrow((330, y + 85), (356, y + 85), color=AMBER, width=5)
    f.arrow((694, y + 85), (720, y + 85), color=GREEN, width=5)
    y += 230
    y = bullets(f, y, [
        '提议者：提出「编号 n，值 v」。编号必须比它之前用过的都大。',
        '接受者：对每个编号回一句「我承诺」或「我拒绝」，然后记住自己说过的话。',
        '学习者：谁都可以当。它只需要把多数派接受的值记下来，转发出去。',
        '一台机器常常同时扮演三个角色，这也是 Paxos 难读的原因之一。',
    ])
    y = note(f, y, '注意「接受者」是唯一需要把状态写到磁盘上的角色。'
                   '提议者忘了自己提过什么，最多是重来一次；'
                   '接受者忘了自己承诺过什么，安全性就没了。', color=RED)
    save(f, '05-three-roles.png', '提议者、接受者、学习者三种角色')


def fig06():
    f, y = new(6, '编号就是时间',
               'Paxos 不用时钟，也不用「第几轮」。每个提案自带一个编号，'
               '编号大就代表更新。同一个编号可以有多个提议者，'
               '那就再比提议者的名字，得到全序。')
    f.line((80, y + 90), (990, y + 90), color=INK, width=4)
    for i, (x, label, sub, color) in enumerate([
            (200, '1 · P1', '旧', GRAY), (400, '3 · P1', '', TEAL),
            (600, '3 · P2', '同号，名字大的赢', AMBER),
            (800, '7 · P1', '新', GREEN)]):
        f.circle(x, y + 90, 16, fill=color, outline=color)
        f.text((x, y + 40), label, 40, color=color, anchor='ma', bold=True)
        if sub:
            f.text((x, y + 126), sub, 40, color=INK_SOFT, anchor='ma')
    y += 260
    y = note(f, y, '「更大的编号」这句话里没有任何物理时间。两台机器的钟差几个小时都无所谓，'
                   '只要编号本身是个全序，并且每个提议者的编号严格递增。')
    y = note(f, y, '代价是：如果两个提议者同时抬价，编号会越抬越高，谁也提交不了。'
                   '这一点后面单独讲。', color=AMBER)
    save(f, '06-ballot-order.png', '用编号给提案排全序')


def fig07():
    f, y = new(7, '第一阶段的全部内容',
               '提议者先问，接受者先答。这一问一答只解决一件事：'
               '「有没有人已经接受过什么，而我必须尊重？」')
    actors = [('P1', 150, 'P1'), ('A1', 380, 'A1'), ('A2', 540, 'A2'),
              ('A3', 700, 'A3'), ('A4', 860, 'A4')]
    s = Seq(f, actors, y + 20)
    s.start()
    s.fan('P1', ['A1', 'A2', 'A3', 'A4'], 'prepare(n)', PREPARE)
    s.fan_back(['A1', 'A2', 'A3', 'A4'], 'P1', 'promise(n)', PROMISE)
    y = s.y + 40
    y = note(f, y, '「承诺」的具体含义：我不再接受任何编号小于 n 的提案。'
                   '已经接受过的旧提案，原样告诉你。')
    y = note(f, y, '图中的 A5 没有出现，因为这四次回复就够多数派了。'
                   '多数派不是「所有人」，少一台照样往下走。', color=TEAL)
    save(f, '07-phase-one.png', '第一阶段：问，然后拿到承诺')


def fig08():
    f, y = new(8, '承诺是一条时间线，不是一句话',
               '接受者对每个编号只说一次「承诺」，然后划掉所有比它小的编号。'
               '划掉的部分，之后无论谁来说情都不再接受。')
    y += 20
    f.text((44, y), '收到 prepare(5) 之前', 40, bold=True, color=INK_SOFT)
    for i in range(9):
        x = 330 + i * 74
        f.rect(x, y + 54, x + 64, y + 118, fill=WHITE, outline=LIGHT, width=3)
        f.text((x + 32, y + 66), str(i + 1), 40, color=INK, anchor='ma')
    y += 190
    f.text((44, y), '答完 promise(5) 之后', 40, bold=True, color=TEAL)
    for i in range(9):
        x = 330 + i * 74
        banned = i + 1 < 5
        f.rect(x, y + 54, x + 64, y + 118,
               fill=TINT_R if banned else TINT_G, outline=LIGHT, width=3)
        f.text((x + 32, y + 66), str(i + 1), 40, anchor='ma',
               color=RED if banned else GREEN)
        if banned:
            f.line((x + 12, y + 112), (x + 52, y + 60), color=RED, width=4)
    f.text((330, y + 150), '永远拒绝 1–4', 40, color=RED)
    f.text((700, y + 150), '仍然接受 5 及以上', 40, color=GREEN)
    y += 230
    y = note(f, y, '注意 5 本身仍然接受。承诺的是「比 n 小」，不是「比 n 小或相等」。'
                   '这一格之差，决定了同一个编号能不能被重复提交（后面 Multi-Paxos 会用到）。')
    save(f, '08-promise-blocks-older.png', '承诺会永久封锁更小的编号')


def fig09():
    f, y = new(9, '第二阶段：把值钉下去',
               '拿着承诺，提议者把值发给多数派。多数派接受了，这个值就叫「选定」——'
               '不需要等所有人，也不需要再确认一次。')
    actors = [('P1', 150, 'P1'), ('A1', 380, 'A1'), ('A2', 540, 'A2'),
              ('A3', 700, 'A3'), ('A4', 860, 'A4')]
    s = Seq(f, actors, y + 20)
    s.start()
    s.fan('P1', ['A1', 'A2', 'A3', 'A4'], 'accept(n, X)', ACCEPT)
    s.fan_back(['A1', 'A2', 'A3', 'A4'], 'P1', 'accepted(n, X)', ACCEPTED)
    y = s.y + 40
    y = note(f, y, '选定（chosen）是一个只增不减的状态：一旦多数派接受了 X，'
                   '后面任何编号的提案，只要还遵守规则，就只能继续提 X。')
    save(f, '09-phase-two.png', '第二阶段：把值写到多数派')


def fig10():
    f, y = new(10, '第二阶段到底提交哪个值',
               '这是 Paxos 唯一一处「看起来像作弊」的地方：提议者带着自己的值进来，'
               '却不一定要提自己的值。规则只有一条——如果有人报过值，'
               '就选编号最大的那个。')
    f.text((44, y), '第一阶段的回复', 42, bold=True)
    rows = [[('A1', INK, False), ('—', GRAY, False)],
            [('A2', INK, False), ('3 · X', AMBER, False)],
            [('A3', INK, False), ('5 · Z', AMBER, False)],
            [('A4', INK, False), ('—', GRAY, False)]]
    top = y + 60
    for i, row in enumerate(rows):
        yy = top + i * 66
        f.rect(48, yy - 8, 620, yy + 52, fill=PALE if i % 2 else WHITE,
               outline=None)
        f.text((70, yy), row[0][0], 40)
        f.text((300, yy), row[1][0], 40, color=row[1][1])
    f.text((70, top + 4 * 66 + 6), '结论：编号最大的是 5 · Z，所以提交 Z',
           40, bold=True, color=TEAL)
    y = top + 4 * 66 + 92
    f.rect(48, y, 1014, y + 190, fill=TINT_A, outline=LIGHT, radius=16)
    f.text((80, y + 24), '如果四个人都说「没见过」', 40, bold=True, color=AMBER)
    f.text((80, y + 90), '提议者才可以提自己带来的值。', 40, color=INK)
    f.text((80, y + 144), '这叫「自由提案」，只在系统还空着的时候发生。', 40,
           color=INK_SOFT)
    y += 240
    y = note(f, y, '为什么非要「编号最大」而不是「随便挑一个见过的」？'
                   '因为编号最大的那个，是最近一次多数派可能已经选定的值。'
                   '挑一个更旧的，等于把已经被选定的结果悄悄换掉。', color=RED)
    save(f, '10-value-selection.png', '第二阶段提交哪个值：取编号最大的已接受值')


def fig11():
    f, y = new(12, '跑一遍：一次真实的往返',
               '下面是 examples/run_model.py 实际跑出来的消息，时间来自事件队列，'
               '不是画的。五台接受者、一个提议者，编号 1。')
    rows = [r for r in R['happy']['trace'] if r['dir'] == 'send']
    actors = [('P1', 150, 'P1')] + [(a, 380 + i * 155, a) for i, a in enumerate(FIVE)]
    s = Seq(f, actors, y + 10)
    s.start()
    for r in rows:
        color = ROLE_COLOR[r['kind']]
        if r['src'] == 'P1':
            s.fan('P1', FIVE, '%s(%d)' % (r['kind'], r['ballot']), color,
                  note_text='t=%d' % r['t'])
        else:
            s.fan_back(FIVE, 'P1', r['kind'], color, note_text='')
    y = s.y + 30
    h = R['happy']
    y = note(f, y, '四个阶段，二十条消息，全部落在 1 秒以内（这里的「秒」是模拟时钟）。'
                   '真实系统里最贵的是最后一步：接受者要先把 (n, X) 写到磁盘，'
                   '才能回 accepted。')
    y = note(f, y, '最终每台机器的状态：' + '，'.join(
        '%s promised=%s accepted=%s' % (row['acceptor'], row['promised'],
                                        row['accepted_value'])
        for row in h['state'][:3]) + '，其余相同。')
    save(f, '12-real-trace.png', '一次真实运行的完整消息往返')


def fig12():
    f, y = new(13, '竞争：后来的人会捡起前人的值',
               'P1 用编号 1 提出 X 并成功。稍后 P2 用编号 2 提出 Y，'
               '但它第一阶段的回复里带着 X——于是它放弃 Y，改提 X。')
    actors = [('P1', 170, 'P1'), ('P2', 300, 'P2'),
              ('A1', 470, 'A1'), ('A2', 610, 'A2'), ('A3', 750, 'A3'),
              ('A4', 890, 'A4')]
    s = Seq(f, actors, y + 10, row=100)
    s.start()
    s.phase('第一轮：P1 用编号 1 提交 X', TEAL)
    s.fan('P1', ['A1', 'A2', 'A3'], 'prepare(1)', PREPARE)
    s.fan_back(['A1', 'A2', 'A3'], 'P1', 'promise(1) · 空', PROMISE)
    s.fan('P1', ['A1', 'A2', 'A3'], 'accept(1, X)', ACCEPT)
    s.fan_back(['A1', 'A2', 'A3'], 'P1', 'accepted(1, X)', ACCEPTED)
    s.phase('X 已被 {A1 A2 A3} 选定', GREEN)
    s.phase('第二轮：P2 用编号 2 提交 Y', AMBER)
    s.fan('P2', ['A2', 'A3', 'A4'], 'prepare(2)', PREPARE)
    s.fan_back(['A2', 'A3', 'A4'], 'P2', 'promise(2) · 带回 (1, X)', PROMISE)
    s.fan('P2', ['A2', 'A3', 'A4'], 'accept(2, X)', ACCEPT)
    s.fan_back(['A2', 'A3', 'A4'], 'P2', 'accepted(2, X)', ACCEPTED)
    y = s.y + 30
    y = note(f, y, 'P2 的日志里写着：'
                   + '；'.join(R['race']['proposers'][1]['log']) + '。')
    y = note(f, y, '这就是「两个多数派必然重叠」的用处：P2 的 {A2 A3 A4} 与 P1 的 '
                   '{A1 A2 A3} 在 A2、A3 处重叠，而那两台机器记得 X。'
                   '重叠的那一台没有投票权，它只是把「已经发生的事」告诉了后来者。',
             color=TEAL)
    save(f, '13-race-adopts.png', '竞争时，后到的提案者沿用已选定的值')


def fig13():
    f, y = new(14, '把那条规则去掉会怎样',
               '同一个场景，只删掉「取编号最大的已接受值」这一行代码。'
               'P2 照样拿到承诺，然后照样提它自己的 Y。')
    f.text((44, y), '遵守规则（真实运行）', 42, bold=True, color=TEAL)
    rows = [('第一轮', 'X 被 {A1 A2 A3} 接受', 'X', TEAL),
            ('第二轮', 'P2 的第一阶段看到 X', 'X', TEAL)]
    yy = y + 60
    for i, (a, b, c, color) in enumerate(rows):
        f.text((60, yy + i * 64), a, 40, color=INK)
        f.text((200, yy + i * 64), b, 40, color=INK_SOFT)
        f.text((900, yy + i * 64), c, 40, color=color, bold=True)
    y = yy + 150
    f.text((44, y), '不遵守（同一份代码，honour=False）', 42, bold=True, color=RED)
    rows = [('第一轮', 'X 被 {A1 A2 A3} 接受', 'X', TEAL),
            ('第二轮', 'P2 的第一阶段看到 X，忽略', 'Y', RED)]
    yy = y + 60
    for i, (a, b, c, color) in enumerate(rows):
        f.text((60, yy + i * 64), a, 40, color=INK)
        f.text((200, yy + i * 64), b, 40, color=INK_SOFT)
        f.text((900, yy + i * 64), c, 40, color=color, bold=True)
    y = yy + 150
    y = note(f, y, '删掉这一行之后，X 和 Y 各自拿到一个多数派。'
                   '系统里同时存在两个「被选定」的值，而且两边都能拿出多数派证明。',
             color=RED)
    y = note(f, y, '这就是 Paxos 全部的「魔法」：新提案必须继承旧结果。'
                   '规则不是为了公平，也不是为了性能，是因为不继承就会丢数据。')
    save(f, '14-without-the-rule.png', '去掉继承规则会选出两个值')


def fig14():
    f, y = new(15, '哪个变量必须落盘',
               '接受者的内存里只有两个字段。但崩溃重启之后，它们必须还在，'
               '否则它会答应一个自己早就拒绝过的编号。')
    rows = [[('promised', INK, True), ('见过的最大编号', INK_SOFT, False),
             ('必须落盘', RED, True)],
            [('accepted', INK, True), ('(编号, 值) 这一对', INK_SOFT, False),
             ('必须落盘', RED, True)],
            [('提案者的 value', INK, True), ('它想提的值', INK_SOFT, False),
             ('丢了重来', GRAY, False)]]
    y = table(f, y, [(70, 'la'), (420, 'la'), (790, 'la')], rows)
    y = note(f, y, '顺序也有讲究：先把 promised 写进日志（fsync），再回复 promise。'
                   '如果先回复再写盘，机器在中间挂掉，重启后它会忘记自己的承诺，'
                   '然后接受一个更小的编号——这正是反例图里的那种事故。')
    y = note(f, y, '真实系统会把这一步做成一条日志记录，和业务日志一起复制，'
                   '于是「承诺」本身也变成了一条可以恢复的事实。', color=TEAL)
    save(f, '15-what-must-hit-disk.png', '接受者必须持久化的两个字段')


def fig15():
    f, y = new(16, '活锁：两个人都很有礼貌',
               '编号只增不减，所以谁后说话谁赢。两个人轮流后说话，就谁也赢不了。'
               '这张图画的是一个构造出来的调度，不是模拟的输出。')
    actors = [('P1', 240, 'P1'), ('P2', 780, 'P2')]
    s = Seq(f, actors, y + 10, row=112)
    s.start()
    s.msg('P1', 'P2', 'prepare(1)', PREPARE)
    s.phase('P1 拿到承诺，正要提交，这时 P2 开口了')
    s.msg('P2', 'P1', 'prepare(2)', AMBER)
    s.phase('编号 2 让 P1 的承诺失效，accept(1, X) 被拒绝')
    s.msg('P1', 'P2', 'prepare(3)', PREPARE)
    s.phase('编号 3 又让 P2 的 accept(2, Y) 被拒绝')
    s.msg('P2', 'P1', 'prepare(4)', AMBER)
    s.phase('如此往复，编号越抬越高，谁也没提交成')
    y = s.y + 20
    y = note(f, y, '两个人都没错：每次被拒绝就抬价再来，是标准做法。'
                   '但在「谁编号大谁说了算」的系统里，这种礼貌会互相打断。', color=AMBER)
    y = note(f, y, 'Paxos 只保证安全性（不会选出两个值），不保证活性（一定会选出值）。'
                   '工程上的补丁是随机化：被拒绝之后等一个随机的时间再抬价，'
                   '让两个人错开。')
    save(f, '16-livelock.png', '活锁：互相抬价的提议者',
         identity='原创教学示意（构造的调度）')


def fig16():
    f, y = new(17, '抢的人越多，编号涨得越快',
               '同一份模拟，改同时竞争的提议者数量，每次跑 60 遍取平均。'
               '纵轴是「最后用到的最大编号」。')
    rows = R['contention']
    top = y + 30
    p = Plot(f, (230, top + 20, 990, top + 520), (0.4, 6.6), (0, 14))
    p.axes(xticks=(), yticks=(0, 4, 8, 12), yfmt='%g', ylab='最大编号')
    for row in rows:
        p.bar(row['k'], row['mean'], 92,
              TEAL if row['k'] < 3 else (AMBER if row['k'] < 5 else RED))
        f.text((p.px(row['k']), top + 560), 'k=%d' % row['k'], 40,
               color=INK, anchor='ma')
    y = top + 640
    y = note(f, y, '一个人提，编号停在 1。两个人抢，平均要争到 4.4；'
                   '六个人抢，要到 12。这就是为什么真实的 Paxos 实现要选一个 leader'
                   '（下一张图），而不是让所有机器都随时可以提案。')
    y = note(f, y, '另外一件在这次模拟里反复出现的事：最后胜出的是编号最大的提议者'
                   '带来的值。这不是巧合，是「后来者继承前者」规则的直接后果。',
             color=TEAL)
    save(f, '17-contention-cost.png', '竞争人数与所需编号数量（实测）')


def fig17():
    f, y = new(18, 'Multi-Paxos：把第一阶段省掉',
               '如果只有一个人提案，第一阶段就白跑了。于是先选一个 leader，'
               '让它一次性做完第一阶段，之后每一轮只需要第二阶段。')
    actors = [('L', 170, 'leader'), ('A1', 430, 'A1'), ('A2', 620, 'A2'),
              ('A3', 810, 'A3')]
    s = Seq(f, actors, y + 10, row=96)
    s.start()
    s.phase('选主之后，做一次第一阶段（编号 10）', TEAL)
    s.fan('L', ['A1', 'A2', 'A3'], 'prepare(10)', PREPARE)
    s.fan_back(['A1', 'A2', 'A3'], 'L', 'promise(10)', PROMISE)
    s.phase('此后每一轮只走第二阶段', AMBER)
    for i, value in enumerate(['X', 'Y', 'Z']):
        s.fan('L', ['A1', 'A2', 'A3'], 'accept(10, %s)' % value, ACCEPT)
        s.fan_back(['A1', 'A2', 'A3'], 'L', 'accepted', ACCEPTED)
    y = s.y + 30
    y = note(f, y, '编号 10 被反复使用，靠的是「承诺的是比 10 小」这条细节：'
                   '接受者对 10 不会翻脸，只有更大的编号才会让它改口。')
    y = note(f, y, '省掉第一阶段之后，一轮从四条消息腿变成两条，'
                   '吞吐量翻倍。代价是：leader 挂了，要重新选，重新做第一阶段。', color=TEAL)
    save(f, '18-multi-paxos.png', 'Multi-Paxos 用一次第一阶段服务很多轮')


def fig18():
    f, y = new(19, '日志有空洞，也得先填上',
               '真实的 Paxos 存的是日志：第 1 条、第 2 条……每条是一次独立的共识。'
               '它们可以并行提案，于是完成顺序是乱的。')
    slots = ['1', '2', '3', '4', '5', '6', '7', '8']
    values = ['X', None, 'Z', 'W', None, 'V', 'U', None]
    top = y + 20
    for i, (slot, value) in enumerate(zip(slots, values)):
        x = 60 + i * 120
        fill = TINT_G if value else TINT_R
        f.box('slot' + slot, x, top, x + 104, top + 150, fill=fill)
        f.text((x + 52, top + 18), '#' + slot, 40, color=INK_SOFT, anchor='ma',
               inside='slot' + slot)
        f.text((x + 52, top + 82), value or '空', 42, bold=True, anchor='ma',
               color=INK if value else RED, inside='slot' + slot)
    f.text((60, top + 176), '已选定', 40, color=GREEN)
    f.text((540, top + 176), '还在协商 / 提案者挂了', 40, color=RED)
    y = top + 250
    y = note(f, y, '应用不能先执行 #3 再回头执行 #2——那样两台机器的状态就分叉了。'
                   '所以已经选定的前缀才算数：读日志的一方只能读到第一个空洞之前。')
    y = note(f, y, '空洞本身也是要共识的内容：新 leader 上台后，'
                   '必须先把空洞填成「空操作」，才能继续往后写。', color=TEAL)
    save(f, '19-log-holes.png', '日志并行提交会产生空洞')


def fig19():
    f, y = new(20, '为什么是奇数台',
               '多数派的大小和可容忍的故障数，都是 N 的函数。'
               '纵轴是「还能挂几台」，数据由 results.json 里的公式算出。')
    rows = R['tolerance']
    top = y + 30
    p = Plot(f, (230, top + 20, 990, top + 480), (0, 10), (0, 5))
    p.axes(xticks=(), yticks=(0, 1, 2, 3, 4), yfmt='%g', ylab='可挂数量')
    for row in rows:
        color = TEAL if row['n'] % 2 else GRAY
        p.bar(row['n'], row['tolerated'], 74, color)
        f.text((p.px(row['n']), top + 520), str(row['n']), 40, color=INK,
               anchor='ma')
    f.text((610, top + 578), 'N（台）', 40, color=GRAY)
    y = top + 660
    y = note(f, y, 'N=4 和 N=3 都只能挂 1 台，可 N=4 多花了一台机器的钱。'
                   'N=6 和 N=5 都只能挂 2 台。所以部署几乎总是奇数台。'
                   '（青色是奇数，灰色是偶数。）')
    y = note(f, y, '跨机房时还有另一条约束：多数派必须能在一个机房整体掉线后仍然凑齐，'
                   '于是 3 个机房通常按 2 : 2 : 1 分配副本，而不是平均分。', color=TEAL)
    save(f, '20-odd-numbers.png', '副本数、多数派与可容忍故障数')


def fig20():
    f, y = new(21, '和 Raft 比，差在哪',
               '两套协议解决同一个问题，安全性的核心是同一条：多数派 + 继承。'
               '差别主要在「怎么组织讨论」。')
    rows = [[('项目', INK, True), ('Paxos', TEAL, True), ('Raft', BLUE, True)],
            [('基本单位', INK, False), ('单次决议', INK_SOFT, False),
             ('一条日志', INK_SOFT, False)],
            [('谁在说话', INK, False), ('任何提议者', INK_SOFT, False),
             ('选出的 leader', INK_SOFT, False)],
            [('阶段', INK, False), ('prepare / accept', INK_SOFT, False),
             ('选举 / 复制', INK_SOFT, False)],
            [('日志空洞', INK, False), ('允许，要补洞', INK_SOFT, False),
             ('不允许', INK_SOFT, False)],
            [('活性', INK, False), ('leader 或随机化', INK_SOFT, False),
             ('选举超时', INK_SOFT, False)],
            [('读起来', INK, False), ('难', RED, False), ('相对容易', GREEN, False)]]
    y = table(f, y, [(70, 'la'), (380, 'la'), (720, 'la')], rows, row_h=74)
    y = note(f, y, 'Raft 常被描述成「可理解的 Paxos」，它的贡献不是更快，'
                   '而是把「选主 + 日志 + 成员变更」写成了可以直接实现的说明书。')
    save(f, '21-paxos-vs-raft.png', 'Paxos 与 Raft 的对照')


def fig21():
    f, y = new(22, '它在哪些系统里',
               'Paxos 很少以「Paxos」的名字出现在用户面前，但很多系统的元数据'
               '都是它（或它的变体）在守着。')
    items = [('Chubby', 'Google 的锁服务，GFS 用它选主', TINT_B),
             ('Spanner', '跨机房的副本组', TINT_T),
             ('ZooKeeper', 'ZAB 协议，选主与配置', TINT_A),
             ('etcd / Consul', 'Raft，思想同源', TINT_G)]
    top = y + 10
    for i, (name, sub, tint) in enumerate(items):
        x = 60 + (i % 2) * 490
        yy = top + (i // 2) * 210
        f.box('u%d' % i, x, yy, x + 450, yy + 200, fill=tint)
        f.text((x + 26, yy + 20), name, 42, bold=True, inside='u%d' % i)
        f.wrap((x + 26, yy + 86), sub, 40, 386, color=INK_SOFT,
               inside='u%d' % i)
    y = top + 490
    y = note(f, y, '共同点：它们守护的数据量都不大，但「不能错」。'
                   '一个 1 KB 的配置错一次，整个集群就会按错的地图走。')
    y = note(f, y, '也正因为如此，Paxos 的性能上限通常不是瓶颈——'
                   '每秒钟几次写，换来的是十年不出一次分叉。', color=TEAL)
    save(f, '22-where-it-runs.png', '使用 Paxos 或其变体的系统')


def fig22():
    f, y = new(23, '一份被当成玩笑的论文',
               'Paxos 的故事比算法本身还长：写好、被拒、搁置、再发表，前后十一年。')
    top = y + 20
    f.line((90, top + 120), (990, top + 120), color=INK, width=4)
    dots = [(140, '1988', '写出论文', TEAL),
            (390, '1990', 'SRC 报告', TEAL),
            (650, '1998', 'ACM TOCS 发表', AMBER),
            (900, '2001', 'Paxos Made Simple', GREEN)]
    for x, year, text, color in dots:
        f.circle(x, top + 120, 15, fill=color, outline=color)
        f.text((x, top + 40), year, 42, bold=True, color=color, anchor='ma')
        f.wrap((x, top + 160), text.replace('\n', ''), 40, 210, color=INK_SOFT,
               anchor='ma')
    y = top + 340
    y = note(f, y, '论文用希腊小岛 Paxos 上的议会做比喻：议员们上午来、下午走，'
                   '记不住上次通过了什么，只好靠一套繁琐的规矩保证法案不被重复通过。'
                   '审稿人觉得这是个玩笑，编辑也没看出它是分布式共识的完整解。')
    y = note(f, y, '十一年后，Lamport 又写了一篇六页的 Paxos Made Simple，'
                   '开头第一句是：「Paxos 很简单。」')
    save(f, '23-timeline.png', 'Paxos 从写作到被理解的时间线')


def fig23():
    f, y = new(11, '两阶段的信息量',
               '把两个阶段并排看，会发现它们问的是同一件事的两个方向：'
               '「过去有没有人做过决定」和「现在能不能定下来」。')
    left = [('1a', 'prepare(n)', '问：有没有人接受过比我更旧的？', TEAL),
            ('1b', 'promise(n)', '答：我承诺，并附上我已经接受的值', BLUE)]
    right = [('2a', 'accept(n, v)', '问：把这个值记下来行不行？', AMBER),
             ('2b', 'accepted(n, v)', '答：记下了，多数派都记下就算选定', GREEN)]
    top = y + 10
    for i, (tag, name, desc, color) in enumerate(left):
        yy = top + i * 215
        f.box('l%d' % i, 44, yy, 500, yy + 190, fill=WHITE)
        f.text((70, yy + 16), tag, 42, bold=True, color=color, inside='l%d' % i)
        f.text((150, yy + 16), name, 40, bold=True, inside='l%d' % i)
        f.wrap((70, yy + 84), desc, 40, 396, color=INK_SOFT, inside='l%d' % i)
    for i, (tag, name, desc, color) in enumerate(right):
        yy = top + i * 215
        f.box('r%d' % i, 558, yy, 1014, yy + 190, fill=WHITE)
        f.text((584, yy + 16), tag, 42, bold=True, color=color, inside='r%d' % i)
        f.text((664, yy + 16), name, 40, bold=True, inside='r%d' % i)
        f.wrap((584, yy + 84), desc, 40, 396, color=INK_SOFT, inside='r%d' % i)
    y = top + 2 * 215 + 20
    y = note(f, y, '第一阶段管「过去」，第二阶段管「现在」。'
                   '过去的信息只影响第二阶段提交什么值，不改变第二阶段的形式——'
                   '这也是 Multi-Paxos 能把它折叠掉的原因。')
    save(f, '11-two-phases.png', '两个阶段各自回答的问题')


def fig24():
    f, y = new(26, '回到那个问题',
               '五个副本、一个客户端、一个会丢包的网。Paxos 的答案是三条规矩，'
               '每条都不长。')
    y = bullets(f, y, [
        '任何决定，必须由多数派接受（quorum）。',
        '任何新提案，必须先问出「已经接受过的最大编号值」，并继承它。',
        '任何承诺，必须先落到磁盘，再开口回答。',
    ], accent=TEAL)
    y = note(f, y, '三条规矩合起来，保证了一件很朴素的事：如果某个值已经被选定，'
                   '那么之后每一个多数派里，都至少有一台机器记得它，'
                   '而每个新提案者都必须先听到它。')
    y = note(f, y, '这就是为什么 Paxos 慢。它把「先问一句」变成了协议的一部分：'
                   '不先问，就可能覆盖别人已经做成的事。', color=AMBER)
    save(f, '26-three-rules.png', 'Paxos 的三条规矩')


def make_cover():
    f = Fig(1080, width=1080)
    f.text((540, 322), '一座小岛上的议会', 66, True, anchor='ma')
    f.text((540, 400), '三台机器怎样对同一个值达成一致', 48, True, anchor='ma')
    f.text((540, 462), 'Paxos：先问过去，再决定现在', 48, True, TEAL, anchor='ma')
    for i, (label, color) in enumerate((('prepare', TEAL), ('promise', BLUE),
                                        ('accept', AMBER), ('accepted', GREEN))):
        y0 = 512 + i * 64
        f.rect(160, y0, 920, y0 + 58, fill=WHITE, outline=LIGHT, width=3)
        f.rect(160, y0, 182, y0 + 58, fill=color, outline=None)
        f.text((214, y0 + 10), label, 40, color=INK)
    f.text((540, 782), '多数派必然相交 —— 剩下的都是推论', 40, True, INK_SOFT,
           anchor='ma')
    f.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


def main():
    only = [int(a) for a in sys.argv[1:]]
    figs = [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
            fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18,
            fig19, fig20, fig21, fig22, fig23, fig24]
    failed = {}
    for i, fn in enumerate(figs, start=1):
        if only and i not in only:
            continue
        try:
            fn()
        except Exception as exc:  # keep going so one bad figure does not hide the rest
            failed[i] = str(exc).splitlines()[:4]
            print('FAIL fig%02d' % i)
            for line in failed[i]:
                print('     ', line)
    if not only:
        make_cover()
    for row in META:
        row['path'] = 'assets/' + Path(row['path']).name
    meta_path = HERE / 'figure-metadata.json'
    rows = META
    if only and meta_path.is_file():
        rebuilt = {row['path'] for row in META}
        kept = [r for r in json.loads(meta_path.read_text('utf-8'))
                if r['path'] not in rebuilt]
        rows = sorted(kept + META, key=lambda r: r['path'])
    meta_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(rows))
    if failed:
        print('failed:', sorted(failed))


if __name__ == '__main__':
    main()
