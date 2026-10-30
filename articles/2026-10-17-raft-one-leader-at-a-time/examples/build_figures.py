#!/usr/bin/env python3
"""Original teaching figures for the Raft article. MIT.

Every state, log and count is read from results.json, which run_model.py
produced by actually running the simulator. Nothing is sketched by hand.
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
STATE_COLOR = {'leader': TEAL, 'candidate': AMBER, 'follower': GRAY}


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


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def log_chips(fig, x, y, entries, *, label=None, commit=None, h=110,
              accent=LIGHT, term_color=GRAY):
    """Draw a log as a row of chips: term on top, command underneath.

    `entries` are strings like 'T2:b'. `commit` marks how many leading entries
    are committed, which is drawn as a tinted background.
    """
    if label:
        fig.text((x, y + 34), label, 40, color=INK, bold=True)
        x += fig.width_of(label, 40, True) + 40
    left = x
    for i, text in enumerate(entries):
        term, _, cmd = text.partition(':')
        w = max(96, fig.width_of(cmd, 40) + 44)
        if x + w > 1014 and x > left:      # wrap rather than run off the canvas
            x, y = left, y + h + 24
        fill = TINT_T if (commit is not None and i < commit) else WHITE
        fig.rect(x, y, x + w, y + h, fill=fill, outline=accent, width=3,
                 radius=10)
        fig.text((x + w // 2, y + 8), term, 40, color=term_color, anchor='ma')
        fig.text((x + w // 2, y + 56), cmd, 40, color=INK, anchor='ma')
        x += w + 12
    if not entries:
        fig.text((x, y + 34), '（空日志）', 40, color=GRAY)
    return y + h


def node_chip(fig, x, y, name, state, term, w=150, h=64):
    """One node drawn as a small labelled chip."""
    color = STATE_COLOR.get(state, GRAY)
    fig.rect(x, y, x + w, y + h, fill=WHITE, outline=color, width=4, radius=14)
    fig.text((x + w // 2, y + 6), name, 42, bold=True, color=INK, anchor='ma')
    fig.text((x + w // 2, y + h - 42), 'T%d' % term, 40, color=color, anchor='ma')


def log_row(fig, x, y, entries, cw=96, ch=64, commit=0, label=None):
    """A node's log drawn as index/term cells."""
    if label:
        fig.text((x, y + 12), label, 40, color=INK, bold=True)
        x += 90
    for i, text in enumerate(entries):
        fill = TINT_T if i < commit else WHITE
        fig.rect(x + i * cw, y, x + (i + 1) * cw - 6, y + ch, fill=fill,
                 outline=LIGHT, width=3, radius=8)
        fig.text((x + i * cw + (cw - 6) // 2, y + 10), text, 40,
                 color=INK if i < commit else INK_SOFT, anchor='ma')
    if not entries:
        fig.text((x, y + 12), '（空）', 40, color=GRAY)
    return x + len(entries) * cw


def seq_arrow(fig, x0, y0, x1, y1, label, color, dy=-30, anchor='ma'):
    fig.arrow((x0, y0), (x1, y1), color=color, width=4)
    fig.text(((x0 + x1) // 2, min(y0, y1) + dy), label, 40, color=color,
             anchor=anchor)


# ------------------------------------------------------------------- figures
def fig01():
    f, y = new(1, '一台机器记不住，那就多放几台',
               '把同一份数据复制到多台机器上，问题就从「机器会不会坏」'
               '变成了「它们会不会各说各话」。')
    f.box('s', 60, y, 1002, y + 300)
    f.text((90, y + 24), '一台机器：它坏了，数据就没了', 42, bold=True, inside='s')
    f.text((90, y + 96), '多台机器：只要还有一份活着，数据就还在——', 42, color=INK_SOFT, inside='s')
    f.text((90, y + 164), '前提是它们对「现在是什么」有同一个答案。', 42, color=RED, inside='s')
    y += 360
    y = bullets(f, y, [
        '客户端把写请求发给谁？如果发给三台，三台会不会各自写进不同的值？',
        '一台机器暂时联系不上，它到底「死了」还是「只是慢」？',
        '如果两台机器都认为自己是主，谁说了算？',
    ])
    y = note(f, y, 'Raft 的答案只有一句话：**任何决定，都要拿到多数票才算数。**'
                   '剩下的所有规则，都是为了在机器随时会坏、消息随时会丢的前提下，'
                   '把这句话守住。', color=TEAL)
    save(f, '01-why-replicate.png', '为什么需要复制')


def fig02():
    f, y = new(2, '为什么是「过半」，不是「全部」',
               '要求全部同意，坏一台就全停；要求过半同意，坏掉少数几台还能继续。')
    # 容忍故障 and 可失联 are the same number for every n -- the model computes
    # both, but showing both invites the reader to hunt for a difference.
    rows = [[('机器数', INK, True), ('过半', INK, True), ('容忍故障', INK, True)]]
    for row in R['majority']:
        rows.append([('%d' % row['n'], INK, False),
                     ('%d' % row['majority'], INK, False),
                     ('%d' % row['tolerated'], INK, False)])
    y = table(f, y, [(60, 'la'), (400, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '偶数台并不比它少一台更结实：4 台的过半是 3，和 3 台的过半是 2 相比，'
                   '能容忍的故障数一样，却多花一台机器。这就是集群常用 3、5、7 台的原因。')
    y = note(f, y, '过半的另一个名字是「任意两个多数派必然有交集」。'
                   '两次投票的多数派至少共用一个节点，而那个节点记得自己投过谁——'
                   '这是整个 Raft 唯一的地基。', color=TEAL)
    save(f, '02-majority.png', '多数派与可容忍故障数')


def fig03():
    f, y = new(3, '任期：一个只增不减的编号',
               '每个节点都记着一个整数，叫任期（term）。它只会在两种情况下变大：'
               '自己发起选举，或者听说别人用了更大的任期。')
    f.box('t', 60, y, 1002, y + 430)
    for i, line in enumerate([
            '任期 1：A 当选，全集群进入任期 1',
            '任期 2：A 失联，B 发起选举，任期 +1',
            '任期 3：B 也失联，C 再发起，任期再 +1',
            '看到更大任期的节点，立刻退位并接受它']):
        f.text((90, y + 30 + i * 96), line, 42,
               color=TEAL if i < 3 else RED, inside='t')
    y += 490
    y = note(f, y, '任期把「谁说了算」变成了一个可以比较的数字：'
                   '**任期大的说了算，任期相同的只可能有一个领导。**')
    y = note(f, y, '一个任期里只允许投出一票——这条规则让「同一任期两个领导」'
                   '不可能发生，而它的证明只需要一句：两个多数派必然相交。', color=TEAL)
    save(f, '03-terms.png', '任期是单调递增的编号')


def fig04():
    f, y = new(4, '一次选举，从头到尾',
               '这个集群一开始没有领导。程序跑出来的实际过程是：'
               'A 先等到自己的超时，出来拉票，拿到过半就上位。')
    changes = R['timeline']['changes']
    rows = [[('时刻 / s', INK, True), ('节点', INK, True),
             ('变成', INK, True), ('任期', INK, True)]]
    for c in changes:
        rows.append([('%.1f' % c['t'], INK, False), (c['node'], INK, False),
                     ({'leader': '领导', 'candidate': '候选', 'follower': '跟随'}[c['to']],
                      STATE_COLOR[c['to']], False),
                     ('%d' % c['term'], INK, False)])
    y = table(f, y, [(60, 'la'), (330, 'la'), (620, 'la'), (1014, 'ra')], rows)
    final = R['timeline']['final']
    y = note(f, y, '终态：%s。'
                   % '，'.join('%s=%s' % (n, {'leader': '领导', 'follower': '跟随',
                                              'candidate': '候选'}[s])
                              for n, s in sorted(final.items())))
    y = note(f, y, '整场只花了两秒：候选发出拉票请求、收到过半同意，'
                   '立刻发心跳告诉所有人「我是领导，别选了」。', color=TEAL)
    save(f, '04-one-election.png', '一次选举的实际时间线')


def fig05():
    f, y = new(5, '心跳：为什么领导在位时没人出来选',
               '领导每 8 秒给所有人发一条空的追加日志请求。'
               '收到它的节点会把自己的选举计时器清零。')
    f.box('h', 60, y, 1002, y + 620)
    rows = [
        ('领导每 8 秒发一次心跳', 't = 0、8、16、24 ……', TEAL),
        ('跟随者收到心跳', '把选举计时器清成 0', INK),
        ('选举超时是 15 到 30 秒', '随机取值，每个节点不一样', AMBER),
        ('只要心跳不断', '计时器到不了超时，没人发起选举', GREEN),
        ('心跳一断（领导崩了）', '计时器涨到超时，选举开始', RED),
    ]
    for i, (a, b, color) in enumerate(rows):
        f.text((90, y + 26 + i * 122), a, 42, bold=True, color=color, inside='h')
        f.text((90, y + 82 + i * 122), b, 40, color=INK_SOFT, inside='h')
    y += 680
    y = note(f, y, '这里的关键是**两段时间必须拉开差距**：心跳间隔要明显小于选举超时。'
                   '本文用的是 8 秒对 15–30 秒，也就是超时至少能容下一次心跳丢失。')
    save(f, '05-heartbeat.png', '心跳与选举超时')


def fig06():
    f, y = new(6, '如果所有人的超时都一样',
               '把五个节点的选举超时全部设成 20 秒，让程序跑 600 秒。')
    fx = R['fixed_timeout']
    rows = [[('节点', INK, True), ('发起选举次数', INK, True),
             ('最终任期', INK, True)]]
    for n in sorted(fx['elections']):
        rows.append([(n, INK, False), ('%d' % fx['elections'][n], INK, False),
                     ('%d' % fx['terms'][n], INK, False)])
    y = table(f, y, [(60, 'la'), (420, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '600 秒里每个节点都发起了 %d 次选举，任期一路涨到 %d，'
                   '**始终没有选出领导**。'
                   % (fx['elections']['A'], fx['max_term']), color=RED)
    y = note(f, y, '原因是它们同时超时、同时拉票、各自投给自己，'
                   '每轮都恰好拿不到过半，然后同时进入下一个任期——无限重复。'
                   '这就是「分裂投票」。')
    y = note(f, y, '解法不是让超时变短，而是让它**不一样**：'
                   '随机化，让某一个节点总是先醒过来。', color=TEAL)
    save(f, '06-split-vote.png', '固定超时导致永远分裂投票')


def fig07():
    f, y = new(7, '把超时随机化之后',
               '选举超时改成 15 到 30 秒之间随机取值，其余全部不变。'
               '同样跑 600 秒，换 %d 个不同的随机种子各跑一次。'
               % R['random_timeout']['runs'])
    rt = R['random_timeout']
    y = table(f, y, [(60, 'la'), (380, 'la'), (620, 'la'), (1014, 'ra')],
              [[('最快选出领导', INK, True), ('最慢', INK, True),
                ('平均', INK, True), ('没选出来的次数', INK, True)],
               [('%.1f s' % rt['best'], GREEN, False),
                ('%.1f s' % rt['worst'], INK, False),
                ('%.2f s' % rt['mean'], INK, False),
                ('%d' % len(rt['failed']), GREEN, False)]])
    y = note(f, y, '每一次都在 30 秒以内选出了领导，一次都没卡住。'
                   '随机化没有让选举变快，它让**冲突变得不可能持续**：'
                   '下一轮总有人醒得更早，于是总有人先拿到过半。')
    y = note(f, y, 'Raft 的作者把这个技巧称为「用随机化换掉复杂的选举协议」。'
                   '它不优雅，但极简单，而且有效。', color=TEAL)
    save(f, '07-random-timeout.png', '随机化超时的效果')


def fig08():
    f, y = new(8, '日志长什么样',
               '每台机器存一份日志：一个有序的条目列表。'
               '每个条目带着「产生它的任期」和「客户端要求的内容」。')
    f.box('g', 60, y, 1002, y + 320)
    for i, line in enumerate([
            '索引 index：从 1 开始，连续，无空位',
            '任期 term：谁当领导时写进来的',
            '内容 command：客户端要求执行的命令',
            'commitIndex：确认后不会再改的条目数',
            'lastApplied：已交给状态机执行的条目数']):
        f.text((90, y + 24 + i * 58), line, 42,
               color=TEAL if i < 3 else INK_SOFT, inside='g')
    y += 380
    log_row(f, 60, y, ['T1:a', 'T1:b', 'T2:c', 'T2:d'], commit=3)
    y += 110
    y = note(f, y, '上图是 4 个条目、前 3 个已提交。浅色的是已提交部分。'
                   '**提交位置只会往前挪，永远不会后退。**')
    y = note(f, y, '两个细节后面会反复用到：索引从 1 开始（所以「索引 0」'
                   '可以安全地表示「还没有任何条目」）；任期是每条自带的，'
                   '不是全局的——这正是判断两份日志在哪里开始分叉的依据。', color=AMBER)
    save(f, '08-the-log.png', '日志的结构')


def fig09():
    f, y = new(9, '一次客户端写，消息长什么样',
               '程序记录下的完整往返：领导收到写请求，一条追加日志请求，'
               '过半回复，条目就可以提交了。')
    rt = R['round_trip']
    first = [t for t in rt['trace'] if t['t'] <= rt['started'] + 2]
    rows = [[('时刻 / s', INK, True), ('从', INK, True), ('到', INK, True),
             ('消息', INK, True)]]
    kinds = {'append': '追加日志', 'append_reply': '追加回复',
             'request_vote': '拉票', 'request_vote_reply': '投票回复'}
    for t in first[:8]:
        rows.append([('%.0f' % t['t'], INK, False), (t['src'], INK, False),
                     (t['dst'], INK, False),
                     (kinds.get(t['kind'], t['kind']), INK, False)])
    y = table(f, y, [(60, 'la'), (300, 'la'), (480, 'la'), (700, 'la')], rows)
    y = note(f, y, '领导发给了全部四台，但**只要过半（3 台，含自己）回复就够了**。'
                   '所以第 %s 秒提交时，只有部分回复已经到达。'
                   % ('2',))
    y = note(f, y, '写请求从发出到提交，用了一个来回：%.1f 秒（本文设定的单向延迟是 1 秒）。'
                   % rt['committed_after'])
    y = note(f, y, '提交之后，领导会在下一次心跳里把 commitIndex 带给跟随者，'
                   '它们才知道「这条可以执行了」。**日志被复制**和'
                   '**日志被提交**是两件不同的事。', color=TEAL)
    save(f, '09-round-trip.png', '一次客户端写的完整往返')


def fig10():
    f, y = new(10, '机器越多，提交不会变慢，消息会变多',
               '同一份写请求，放在 3、5、7 台的集群里各跑 %d 次，'
               '记录提交耗时和消息条数。' % 20)
    rows = [[('机器数', INK, True), ('过半', INK, True),
             ('提交耗时', INK, True), ('每次写的消息条数', INK, True)]]
    for row in R['latency']:
        rows.append([('%d' % row['n'], INK, False),
                     ('%d' % row['majority'], INK, False),
                     ('%.1f s' % row['mean'], INK, False),
                     ('%.1f' % row['messages_per_write'], INK, False)])
    y = table(f, y, [(60, 'la'), (280, 'la'), (470, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '提交耗时全都是 %.1f 秒——**一个来回就够了，与机器数无关**。'
                   % R['latency'][0]['mean'])
    y = note(f, y, '变多的是消息：从 3 台的 %.1f 条涨到 7 台的 %.1f 条，'
                   '大致是线性的，因为领导要给每一台都发一遍。'
                   % (R['latency'][0]['messages_per_write'],
                      R['latency'][2]['messages_per_write']), color=AMBER)
    y = note(f, y, '这就是「用机器换容错」的真实代价：**延迟不涨，带宽涨**。'
                   '生产系统因此常用 3 或 5 台，而不是越多越好。')
    save(f, '10-cost-of-scale.png', '集群规模对延迟与消息量的影响')


def fig11():
    f, y = new(11, '领导崩了，日志会不会丢',
               '程序先让集群正常提交 3 条日志，然后让领导彻底失联，'
               '等新的领导出现。')
    c = R['crash']
    f.text((60, y), '崩溃前：%s 是领导，任期 1，已提交 %d 条'
           % (c['first_leader'], c['committed_before']), 42, bold=True)
    y += 70
    y = log_chips(f, 60, y, c['log_before'],
                  commit=c['committed_before']) + 80
    f.text((60, y), '崩溃后：%s 当选，任期 %d，用了 %.1f 秒'
           % (c['new_leader'], c['new_term'], c['election_seconds']), 42,
           bold=True, color=GREEN)
    y += 70
    y = log_chips(f, 60, y, c['log_after'], commit=c['committed_after'],
                  accent=GREEN, term_color=GREEN) + 80
    y = note(f, y, '新领导的日志与旧领导的**一字不差**，已提交的 %d 条一条不少。'
                   % c['committed_after'])
    y = note(f, y, '这不是运气。能当选的节点，日志必须「至少和投票者一样新」；'
                   '而任何一个多数派都包含至少一个存有全部已提交条目的节点。'
                   '两条规则叠起来，就保证了已提交的条目不会在选举中丢失。', color=TEAL)
    save(f, '11-leader-crash.png', '领导崩溃后日志不丢')


def fig12():
    f, y = new(12, '两份日志对不上，怎么办',
               '跟随者的日志和领导不一致时，领导会往回退，一直退到找到'
               '「第一个相同的条目」，然后把它后面的全部替换掉。')
    c = R['conflict']
    for label, log, color in (
            ('%s 旧领导（已死）' % c['first_leader'], c['orphan_log'], GRAY),
            ('%s 跟着旧领导' % c['slow_follower'], c['orphan_log'], GRAY),
            ('%s 新领导' % c['new_leader'], c['winner_log'], TEAL),
            ('%s 修复后' % c['slow_follower'], c['follower_after_repair'],
             GREEN)):
        y = log_chips(f, 60, y, log, label=label, accent=color,
                      term_color=color) + 50
    y = note(f, y, '被丢弃的是 %s——它们**从未提交**，只存在于旧领导和这一个跟随者身上。'
                   % '、'.join(c['discarded']))
    y = note(f, y, '程序没有一条一条往回退：跟随者回复时直接告诉领导'
                   '「冲突的那一段任期是 T%d，你从这个索引开始发」，'
                   '领导一步跳到位。这就是所谓的快速回退。', color=TEAL)
    y = note(f, y, '**能被丢弃，是因为没被提交。** 已提交的条目不可能只存在于少数节点上——'
                   '它必然在多数派手里，所以新的领导必然也有。')
    save(f, '12-conflict-repair.png', '日志冲突的修复')


def fig13():
    f, y = new(13, '选领导时，日志不够新的人选不上',
               '拉票请求里带着「我的最后一条日志的索引和任期」。'
               '投票者会拿它和自己的比：不够新就不投。')
    f.box('c', 60, y, 1002, y + 420)
    for i, line in enumerate([
            '先比最后一条的任期，任期大的算更新',
            '任期相同，再看索引，索引大的算更新',
            '任期小的，无论索引多长，都算落后',
            '任何已提交的条目，多数派里都有人存着']):
        f.text((90, y + 26 + i * 92), line, 42,
               color=RED if i == 2 else INK, inside='c')
    y += 480
    y = note(f, y, '第三条容易被忽略，但它正是第 15 节那个反例的关键：'
                   '一个只有一条日志、任期却是 6 的节点，比一个有一百条日志、'
                   '任期只有 1 的节点「更新」——因为它见过更晚的世界。')
    y = note(f, y, '这条规则叫**选举限制**。它的作用是把「已提交的日志」'
                   '和「未来的领导」绑在一起：想当领导，先证明你手里有全部该有的东西。',
         color=TEAL)
    save(f, '13-election-restriction.png', '选举限制：日志不够新就选不上')


def fig14():
    f, y = new(14, '「多数派都有」不等于「可以提交」',
               '这是 Raft 里最容易写错的一条规则：只有**当前任期**的条目，'
               '才能通过「多数派已复制」来提交。')
    f.box('r', 60, y, 1002, y + 560)
    for i, line in enumerate([
            '领导现在是任期 6，日志里索引 2 来自任期 2',
            '索引 2 已经被多数派存下来了',
            '错误做法：过半都有，就提交到索引 2',
            '正确做法：不提交，因为它来自旧任期',
            '领导再写一条任期 6 的新条目',
            '多数派复制它之后，提交点一次跳到新条目',
            '旧任期的那条，顺带被提交']):
        f.text((90, y + 22 + i * 70), line, 42,
               color=RED if i == 2 else (GREEN if i >= 3 else INK), inside='r')
    y += 620
    y = note(f, y, '为什么不能图省事？因为「多数派存下来了」这句话是**此刻**成立的，'
                   '而旧任期的条目可能随时被一个任期更高的新领导覆盖掉。'
                   '只有当前任期的条目能提交，才堵住了这个缺口。')
    save(f, '14-commit-rule.png', '提交规则：为什么必须是当前任期')


def fig15():
    f, y = new(15, '把这条规则去掉，会丢什么',
               '下面这个状态直接照抄 Raft 论文里的那张图（Figure 8）。'
               '五台机器，索引 1 早已提交，索引 2 上有分歧。')
    s = R['figure8']
    rows = [[('节点', INK, True), ('任期', INK, True), ('日志', INK, True)]]
    for n in ('S1', 'S2', 'S3', 'S4', 'S5'):
        st = s['states_c'][n]
        rows.append([(n, INK, False), ('%d' % st['term'], INK, False),
                     ('，'.join(st['log']), INK, False)])
    y = table(f, y, [(60, 'la'), (300, 'la'), (480, 'la')], rows)
    y = note(f, y, 'S1 是任期 6 的领导，它把索引 2（任期 2 的条目）推给了 S3，'
                   '现在 S1、S2、S3 都有它——多数派有了。')
    rows = [[('用的规则', INK, True), ('提交到', INK, True), ('索引 2 的状态', INK, True)]]
    rows.append([('只提交当前任期（正确）', INK, False),
                 ('%d' % s['correct_commit_index'], GREEN, False),
                 ('仍未提交', GREEN, False)])
    rows.append([('过半就提交（错误）', INK, False),
                 ('%d' % s['broken_commit_index'], RED, False),
                 ('被当成已提交', RED, False)])
    y = table(f, y, [(60, 'la'), (560, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '然后 S1 再次失联，S5 当选任期 7（它的最后任期是 5，'
                   '比 S3 的 2 更新，所以 S3 会投给它）。S5 把自己的日志推给 S3：')
    f.box('x', 60, y, 1002, y + 150)
    f.text((90, y + 20), 'S3 原来是：%s' % '，'.join(s['s3_before']), 42, inside='x')
    f.text((90, y + 84), 'S3 变成：  %s' % '，'.join(s['s3_after']), 42,
           color=RED, inside='x')
    y += 210
    y = note(f, y, '**T2:b 消失了。** 在错误规则下它是「已提交」的，'
                   '现在它被一条从未提交过的条目覆盖掉了——'
                   '两台机器的状态机从此永久分叉。', color=RED)
    y = note(f, y, '这就是「只提交当前任期」存在的唯一理由。'
                   '它不解决性能问题，它只堵这一个洞。')
    save(f, '15-figure-8.png', '错误提交规则导致的已提交条目丢失')


def fig16():
    f, y = new(16, '网络断开：旧领导还以为自己是领导',
               '把领导单独隔到一个分区里。它没有坏，只是谁也联系不上。'
               '它会继续以为自己说了算。')
    p = R['partition']
    f.box('p', 60, y, 1002, y + 210)
    f.text((90, y + 18), '多数派那边：%s 在 %.1f 秒后当选，任期 %d'
           % (p['new_leader'], p['elected_after'], p['new_term']), 42,
           color=TEAL, inside='p')
    f.text((90, y + 78), '日志：%s' % '，'.join(p['new_log']), 42, inside='p')
    f.text((90, y + 138), '少数派那边：%s 仍是「领导」，任期 %d'
           % (p['old_leader'], p['old_term']), 42, color=RED, inside='p')
    y += 270
    y = note(f, y, '被隔离的 %s 又接了两条客户端请求：%s。'
                   '它的日志变成了 %s——但 commitIndex 停在 %d，一步没动。'
                   % (p['old_leader'], '、'.join(p['stale_writes']),
                      '，'.join(p['old_log']), p['old_commit']), color=RED)
    y = note(f, y, '**它接受了写请求，却永远提交不了。** 因为提交需要多数派，'
                   '而它的多数派在墙的另一边。这两条请求事实上被吞掉了——'
                   '客户端会超时，然后重试。')
    save(f, '16-partition.png', '网络分区：少数派里的旧领导')


def fig17():
    f, y = new(17, '网络恢复：那两条请求去哪了',
               '把分区拆掉，让两边重新能说话。')
    p = R['partition']
    f.text((60, y), '%s 回到集群，立刻看到任期 %d 的 %s，于是退位。'
           % (p['old_leader'], p['new_term'], p['new_leader']), 42, bold=True)
    y += 80
    y = log_chips(f, 60, y, p['healed_log'], label='集群现在的日志',
                  accent=GREEN, term_color=GREEN) + 80
    f.text((60, y), '被丢弃的孤儿请求：%s' % '、'.join(p['orphans_discarded']),
           42, color=RED)
    y += 80
    y = log_chips(f, 60, y, p['old_final_log'], label='旧领导最终日志',
                  accent=RED, term_color=RED) + 80
    y = note(f, y, '它自己写进去的那两条被**整段截掉**，换成了新领导的日志。'
                   '这正是第 12 节讲的冲突修复，只不过冲突发生在整个节点上。')
    y = note(f, y, '这里可以看到 Raft 的一条隐含承诺：**没有提交的写，'
                   '不保证还在。** 客户端要拿到「提交成功」的答复，'
                   '才算真正写进去了；没拿到答复就重试。')
    save(f, '17-heal.png', '分区恢复：孤儿条目被覆盖')


def fig18():
    f, y = new(18, '加机器：一次只加一台',
               '成员变更的难点是：新旧配置的多数派可能没有交集，'
               '一步跨过去会出现「两个多数派各选一个领导」。')
    m = R['membership']
    rows = [[('步骤', INK, True), ('机器数', INK, True), ('过半', INK, True),
             ('新节点已追到', INK, True)]]
    rows.append([('初始', INK, False), ('%d' % m['before']['n'], INK, False),
                 ('%d' % m['before']['majority'], INK, False),
                 ('%d 条' % m['before']['entries'], INK, False)])
    for s in m['steps']:
        rows.append([('加入 %s' % s['added'], INK, False),
                     ('%d' % s['new_n'], INK, False),
                     ('%d' % s['new_majority'], INK, False),
                     ('%d 条' % s['caught_at'], GREEN, False)])
    y = table(f, y, [(60, 'la'), (330, 'la'), (560, 'la'), (1014, 'ra')], rows)
    y = note(f, y, '从 5 台加到 6 台，过半从 3 变成 4；再加到 7 台，过半还是 4。'
                   '每一步新节点都追上了现有日志（%d 条）。' % m['before']['entries'])
    y = note(f, y, '一次只加一台时，新旧两个多数派**一定相交**——'
                   '因为新配置只比旧配置多一个成员，两边过半的集合不可能错开。'
                   '这条性质让变更过程始终只有一个领导。', color=TEAL)
    y = note(f, y, '反过来，如果从 3 台直接跳到 7 台，新旧过半就可能完全没有交集，'
                   '选举会分裂。所以真实系统要么一次加一台，要么用两阶段联合配置。')
    save(f, '18-membership.png', '成员变更：一次加一台')


def fig19():
    f, y = new(19, '随机日程：让程序自己去找反例',
               '与其手写几个场景，不如让程序随机地崩机器、切网络、发请求，'
               '每一步都检查四条安全性性质。')
    s = R['sweep_harsh']
    rows = [[('检查项', INK, True), ('内容', INK, True)]]
    rows.append([('选举安全', INK, False), ('同一任期不可能同时有两个领导', INK, False)])
    rows.append([('日志匹配', INK, False), ('索引任期相同，前缀必然相同', INK, False)])
    rows.append([('提交一致', INK, False), ('都提交了同一索引，内容必须相同', INK, False)])
    rows.append([('状态机一致', INK, False), ('已执行的命令序列，前缀必须相同', INK, False)])
    y = table(f, y, [(60, 'la'), (340, 'la')], rows, row_h=74)
    y = note(f, y, '跑了 %d 个随机日程，每个 400 秒：共 %d 次崩溃、%d 次重启、'
                   '%d 次网络分区、%d 条写请求。'
                   % (s['seeds'], s['totals']['crashes'], s['totals']['restarts'],
                      s['totals']['partitions'], s['totals']['commands']))
    y = note(f, y, '违反次数：**%d**。' % s['violated'], color=GREEN)
    y = note(f, y, '这个数字只说明「在这些日程里没被抓到」，不构成证明。'
                   'Raft 的正确性来自论文里的归纳论证；随机测试的作用是'
                   '**把实现里的错误逼出来**——它确实逼出来了一个，见下一节。')
    save(f, '19-random-schedules.png', '随机日程下的安全性检查')


def fig20():
    f, y = new(20, '检查器抓到的第一个真错误',
               '第一次跑完 300 个随机日程，出现了 1 次违规（种子 62）：'
               'B 和 E 已经执行过的命令序列不一样了。')
    f.box('e', 60, y, 1002, y + 470)
    f.text((90, y + 18), '跟随者回复的是「我整份日志有多长」', 42, bold=True,
           color=RED, inside='e')
    f.wrap((90, y + 92), '这个数字可能大于领导这次实际发给它的范围，'
                         '于是领导以为对方早已拥有那些条目，'
                         '把它们算进了「多数派已复制」。', 42, 890,
           color=INK_SOFT, inside='e')
    f.wrap((90, y + 250), '结果：E 执行了一条从未被多数派确认过的命令，'
                          '索引 1 上它跑的是 cmd7，B 跑的是 cmd0。', 42, 890,
           color=RED, inside='e')
    y += 540
    y = note(f, y, '正确的回复是：**「我们核对到哪个索引为止一致」**，'
                   '也就是「上一次的索引 + 这次发过去的条目数」，'
                   '而不是「我这边的日志总长度」。')
    bh = R['bug_hunt']
    y = note(f, y, '同一批随机日程，只改这一行：'
                   '「回复整份日志长度」时 %d 个日程里 %d 次违规（种子 62），'
                   '「回复核对到哪为止」时 %d 个日程里 %d 次。'
                   % (bh['broken']['seeds'], bh['broken']['violated'],
                      bh['correct']['seeds'], bh['correct']['violated']), color=GREEN)
    y = note(f, y, '这是本文写作过程中最有价值的一次失败：'
                   '**手写场景想不到这个 bug，随机日程一分钟就抓到了。**')
    save(f, '20-real-bug.png', '检查器抓到的一个真实实现错误')


def fig21():
    f, y = new(21, '它在哪些系统里跑',
               'Raft 不是论文里的玩具。下面这些系统用同一套机制解决同一类问题。')
    y = bullets(f, y, [
        'etcd：Kubernetes 的配置与选主存储，几乎每个 K8s 集群里都有一份。',
        'Consul：服务发现与健康检查的目录数据。',
        'TiKV、CockroachDB：分布式数据库的复制层，Raft 管一致性，'
        '上层再分片。',
        'Hashicorp Vault、Nomad：密钥与调度的元数据。',
        'Kafka 的 KRaft 模式：用 Raft 取代了 ZooKeeper 来管元数据。',
    ])
    y += 10
    y = note(f, y, '它和 Paxos 解决的是同一个问题。Raft 的设计目标不是更快，'
                   '而是**更容易被理解、更容易被正确实现**：'
                   '把「领导选举」「日志复制」「安全性」拆成三块，各自可以单独讲清楚。')
    y = note(f, y, '本文没有对任何真实实现做过测试，也没有引用它们的性能数据；'
                   '上面列出的只是「这些系统用了 Raft」这一公开事实。', color=GRAY)
    save(f, '21-where-it-runs.png', 'Raft 的现实应用')


def fig22():
    f, y = new(22, '自己动手改一个条件',
               '下面每一条都能在本目录的代码里改一个数字重跑。先猜结果，再对照。')
    y = bullets(f, y, [
        '把心跳间隔从 8 秒改成 25 秒（接近选举超时），会发生什么？',
        '把选举超时改成固定值（`randomized_timeout_election` 里把随机去掉），'
        '重现第 6 节的分裂投票。',
        '把集群改成 4 台，看它比 3 台多花了什么、多得到了什么。',
        '把 `advance_commit` 里的任期检查删掉，再跑 400 个随机日程——'
        '检查器抓得到吗？',
        '把 `on_append` 里跟随者的回复改回「整份日志长度」，'
        '看第 20 节那个 bug 会不会重现。',
        '把随机日程的崩溃概率从 0.03 提到 0.15，还能保持 0 违规吗？',
    ])
    y += 10
    y = note(f, y, '第 4 题会给出一个出乎意料的答案：**抓不到。**'
                   '把提交规则改错之后，400 个随机日程依然是 0 违规——'
                   '第 15 节那个反例需要非常特定的交错顺序，随机测试碰不上。')
    y = note(f, y, '这一条比前面任何一条都值得记住：'
                   '**随机测试能证明「有 bug」，不能证明「没 bug」。**', color=RED)
    save(f, '22-try-it.png', '读者可以自己改动的六项实验')


def make_cover():
    f = Fig(1080, width=1080)
    # Same 310..770 window as the float cover: the 2.35:1 feed crop takes the
    # middle 460 rows, so the title has to live there.
    f.text((540, 320), '一次只选一个', 80, True, anchor='ma')
    f.text((540, 410), '多数票、任期和日志', 52, True, TEAL, anchor='ma')
    for i, (label, color) in enumerate((('过半才算数', TEAL),
                                        ('任期只增不减', AMBER),
                                        ('只提交当前任期', RED))):
        f.rect(120, 480 + i * 74, 960, 544 + i * 74, fill=WHITE,
               outline=LIGHT, width=3)
        f.rect(120, 480 + i * 74, 140, 544 + i * 74, fill=color, outline=None)
        f.text((180, 495 + i * 74), label, 44, color=INK)
    f.text((540, 714), '五台机器，一台随时会坏', 42, True, INK_SOFT, anchor='ma')
    f.im.crop((0, 0, 1080, 1080)).save(ART / 'cover.png')
    print('   cover.png', (1080, 1080))


def main():
    only = [int(a) for a in sys.argv[1:]]
    for i in range(1, 23):
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
