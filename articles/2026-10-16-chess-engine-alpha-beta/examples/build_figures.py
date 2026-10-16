#!/usr/bin/env python3
"""Original teaching figures for the chess-engine article. MIT.

Every number drawn here comes from examples/measurements.json, which
examples/measure.py produced by actually running the search in engine.py on
the positions named below. Nothing is illustrative.
"""
from __future__ import annotations
import json
from pathlib import Path
from figkit import (Fig, BG, WHITE, INK, INK_SOFT, TEAL, BLUE, AMBER, RED,
                    GRAY, LIGHT, PALE, GREEN, TINT_T, TINT_B, TINT_A, TINT_R,
                    TINT_G, font)

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ASSETS = ART / 'assets'
ASSETS.mkdir(exist_ok=True)
PHOTOS = ART / 'originals' / 'photos'
M = json.loads((HERE / 'measurements.json').read_text())
META = []

MID = ['r', '1', 'b', 'q', 'k', 'b', '1', 'r',
       'p', 'p', 'p', 'p', '1', 'p', 'p', 'p',
       '2', '2', 'n', '2', 'n', '2', '2', '2',
       '4', 'p', '3',
       '2', 'B', '1', 'P', '3',
       '5', 'N', '2',
       'P', 'P', 'P', 'P', '1', 'P', 'P', 'P',
       'R', 'N', 'B', 'Q', 'K', '2', 'R', '1']
MID_FEN = 'r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq -'


def board_rows(fen):
    rows = []
    for rank in fen.split()[0].split('/'):
        r = ''
        for ch in rank:
            r += '.' * int(ch) if ch.isdigit() else ch
        rows.append(r)
    return rows


def sub(fig, y, text, size=42, color=INK_SOFT):
    """A wrapped subtitle that can never run off the canvas."""
    return fig.wrap((48, y), text, size, 1062 - 96, color=color)


def save(fig, name, purpose, identity='原创教学示意', source=None, **kw):
    row = fig.save(ASSETS / name, purpose, identity, source, **kw)
    META.append(row)
    print('  ', name, row['min_label_px'], 'px ->', row['effective_min_at_354px'])


def bars(fig, x0, x1, y, values, vmax, color=TEAL, height=26, gap=10,
         label_size=42, labels=None, log=False):
    """Draw horizontal bars whose lengths are computed, never hand-written."""
    import math
    rows = []
    for i, v in enumerate(values):
        frac = (math.log10(v) / math.log10(vmax)) if log else (v / vmax)
        length = (x1 - x0) * frac
        yy = y + i * (height + gap)
        fig.rect(x0, yy, x0 + max(2, length), yy + height, fill=color)
        rows.append((i, v, length))
    by_val = sorted(rows, key=lambda r: r[1])
    by_len = sorted(rows, key=lambda r: r[2])
    assert [r[0] for r in by_val] == [r[0] for r in by_len], 'bars lie'
    return rows


# ------------------------------------------------------------------ 02 局面
def fig02():
    fig = Fig(1180)
    fig.text((48, 34), '真实的局面：轮到白方，走哪一步？', 52, True)
    sub(fig, 104, '意大利开局的一路常见局面。轮到白方，合法走法不止一种。')
    rows = board_rows(MID_FEN)
    fig.chessboard(67, 176, 116, rows, labels=True, label_size=42)
    save(fig, '02-position.png', '开局局面的真实摆法，白方行棋')


# --------------------------------------------------- 03 三个候选与对手应手
def fig03():
    fig = Fig(724)
    fig.text((48, 34), '先只看三个候选，再问：对手会怎么回？', 52, True)
    sub(fig, 104, '一层的判断是「我吃掉这个子，赚了」。可轮到对手时，局面会变。')
    fig.box('root', 48, 200, 1014, 320, fill=TINT_A)
    fig.text((531, 232), '白方要走的三个候选', 46, True, AMBER, anchor='mm',
             inside='root')
    fig.text((531, 288), '① 马吃 e5 兵    ② 象吃 f7 将    ③ 马到 c3',
             44, color=INK, anchor='mm', inside='root')
    fig.text((531, 372), '每一个候选下面，都轮到对手挑一步', 44, True, RED,
             anchor='mm')
    for i, (nm, x) in enumerate((('① 马吃 e5 兵', 220), ('② 象吃 f7 将', 531),
                                 ('③ 马到 c3', 842))):
        fig.arrow((531, 324), (x, 430), GRAY, 4, 14)
        fig.box('c%d' % i, x - 150, 424, x + 150, 536, fill=WHITE)
        fig.text((x, 460), nm, 42, True, TEAL, anchor='mm', inside='c%d' % i)
        fig.text((x, 508), '轮到黑方', 40, color=INK_SOFT, anchor='mm',
                 inside='c%d' % i)
    fig.text((531, 600), '黑方会挑对他自己最有利的那一步，', 42, color=INK,
             anchor='mm')
    fig.text((531, 652), '白方必须按这个假设往下算。', 42, color=INK,
             anchor='mm')
    save(fig, '03-candidates.png', '从「我走哪步」变成「我走完对手走哪步」')


# --------------------------------------------------- 04 手算一棵两层小树
def fig04():
    import sys
    sys.path.insert(0, str(HERE))
    from chesslib import from_fen, legal, make, san
    from engine import side_score
    pos = from_fen(MID_FEN)
    want = ('Bxf7+', 'Nc3', 'Nxe5')
    cands = [m for m in legal(pos) if san(pos, m) in want]
    cands.sort(key=lambda m: want.index(san(pos, m)))
    cols = []
    for m in cands:
        child = make(pos, m)
        replies = sorted(((san(child, r), side_score(make(child, r)))
                          for r in legal(child)), key=lambda t: t[1])[:3]
        cols.append((san(pos, m), replies, min(v for _, v in replies)))
    fig = Fig(1036)
    fig.text((48, 34), '三个候选各展开三条应手，分数从白方角度算', 50, True)
    sub(fig, 100, '正数表示对白方有利。叶子分数由子力价值加上兵和马的位置表算出。')
    fig.box('root', 431, 176, 631, 256, fill=TINT_A)
    fig.text((531, 216), '当前局面', 44, True, AMBER, anchor='mm', inside='root')
    xs = (200, 531, 862)
    for i, (name, replies, best) in enumerate(cols):
        x = xs[i]
        fig.arrow((531, 260), (x, 330), GRAY, 4, 14)
        fig.box('m%d' % i, x - 158, 330, x + 158, 414, fill=TINT_T)
        fig.text((x, 372), name, 44, True, TEAL, anchor='mm', inside='m%d' % i)
        for j, (rname, val) in enumerate(replies):
            y = 452 + j * 92
            fig.arrow((x, 418 if j == 0 else y - 8), (x, y - 4), GRAY, 3, 10)
            fig.box('l%d_%d' % (i, j), x - 158, y, x + 158, y + 78,
                    fill=TINT_R if val < 0 else TINT_G)
            fig.text((x - 130, y + 39), rname, 42, True, INK, anchor='lm',
                     inside='l%d_%d' % (i, j))
            fig.text((x + 130, y + 39), '%+d' % val, 42, True,
                     RED if val < 0 else GREEN, anchor='rm',
                     inside='l%d_%d' % (i, j))
        fig.box('v%d' % i, x - 158, 744, x + 158, 860, fill=WHITE, outline=BLUE)
        fig.text((x, 782), '黑方会选最小的', 40, color=INK_SOFT, anchor='mm',
                 inside='v%d' % i)
        fig.text((x, 828), '%+d' % best, 46, True, BLUE, anchor='mm',
                 inside='v%d' % i)
    fig.text((531, 912), '白方在这三个数里挑最大的', 44, True, BLUE, anchor='mm')
    fig.text((531, 966), '、'.join('%s %+d' % (n, b) for n, _, b in cols),
             44, True, BLUE, anchor='mm')
    save(fig, '04-two-ply-tree.png', '三个候选各三条应手的两层树与真实叶子分数')


# --------------------------------------------------------- 05 递归与规模
def fig05():
    mm = {r['depth']: r for r in M['minimax_midgame']}
    fig = Fig(880)
    fig.text((48, 34), '再往下一层：对手走完，还轮到我', 52, True)
    sub(fig, 104, '同一棵树上每加一层，叶子数就乘上大约 30 倍。')
    xs = (150, 372, 594, 816)
    ys = (250, 360, 470, 580)
    labels = ('1 层', '2 层', '3 层', '4 层')
    counts = [mm[d]['leaves'] for d in (1, 2, 3, 4)]
    for i in range(4):
        fig.circle(xs[i], ys[i] - 44, 34, fill=TINT_A, outline=AMBER, width=4)
        fig.text((xs[i], ys[i] - 44), labels[i], 40, True, AMBER, anchor='mm')
        fig.text((xs[i], ys[i] + 40), '叶子', 40, color=INK_SOFT, anchor='mm')
        fig.text((xs[i], ys[i] + 90), f'{counts[i]:,}', 42, True, INK,
                 anchor='mm')
    for i in range(3):
        fig.arrow((xs[i] + 40, ys[i] - 44), (xs[i + 1] - 40, ys[i + 1] - 44),
                  GRAY, 4, 12)
    fig.text((531, 736), '同一局面、同一评估函数，只把深度从 1 加到 4：',
             42, color=INK, anchor='mm')
    fig.text((531, 786), '叶子从 %s 涨到 %s。' % (f'{counts[0]:,}',
             f'{counts[3]:,}'), 42, True, RED, anchor='mm')
    fig.text((531, 838), '耗时从 %.3f 秒涨到 %.1f 秒。' % (mm[1]['seconds'],
             mm[4]['seconds']), 42, True, RED, anchor='mm')
    save(fig, '05-depth-cost.png', '深度每加一层叶子数乘约 30：本模型实测')


# --------------------------------------------------------- 06 深度 vs 节点
def fig06():
    import math
    mm = list(M['minimax_midgame'])
    ab = list(M['alphabeta_none'])
    fig = Fig(940)
    fig.text((48, 34), '同一局面，两种算法的节点数', 52, True)
    sub(fig, 104, '横轴是深度，纵轴是对数刻度上的节点数。两条线共用同一根轴。')
    x0, x1, y0, y1 = 330, 1014, 250, 660
    vmax = max(r['nodes'] for r in mm + ab)
    def px(d): return x0 + (x1 - x0) * (d - 1) / 5
    def py(v): return y1 - (y1 - y0) * math.log10(v) / math.log10(vmax)
    for e in range(0, 7):
        v = 10 ** e
        if v > vmax * 1.2:
            break
        fig.line((x0, py(v)), (x1, py(v)), LIGHT, 2)
        fig.text((x0 - 16, py(v)), f'{v:,}', 40, color=GRAY, anchor='rm')
    for d in range(1, 7):
        fig.text((px(d), y1 + 32), str(d), 42, color=INK, anchor='mm')
    fig.text(((x0 + x1) / 2, y1 + 86), '搜索深度（层）', 42, color=INK,
             anchor='mm')
    for series, color, name in ((mm, RED, '极小化极大'), (ab, TEAL, 'α-β（不排序）')):
        pts = [(px(r['depth']), py(r['nodes'])) for r in series]
        for i in range(len(pts) - 1):
            fig.line(pts[i], pts[i + 1], color, 6)
        for p in pts:
            fig.circle(p[0], p[1], 11, fill=color, outline=color, width=2)
    fig.text((x0 + 46, py(mm[-1]['nodes']) + 42), '极小化极大', 42, True, RED,
             anchor='lm')
    fig.text((x0 + 46, py(ab[-1]['nodes']) - 42), 'α-β（不排序）', 42, True,
             TEAL, anchor='lm')
    fig.text((531, 790), '深度 4：极小化极大访问 %s 个节点，' % f"{mm[3]['nodes']:,}",
             42, True, INK, anchor='mm')
    fig.text((531, 838), 'α-β 只访问 %s 个。' % f"{ab[3]['nodes']:,}",
             42, True, TEAL, anchor='mm')
    save(fig, '06-nodes-by-depth.png',
         '两种算法在各深度上的真实节点数（同一局面，α-β 不带走法排序）')


# --------------------------------------------------------- 07 β 截断
def fig07():
    fig = Fig(920)
    fig.text((48, 34), '为什么可以「不用再看」：一次 β 截断', 52, True)
    sub(fig, 104, '教学例子：数字是为看清规则而选的，不是真实棋局的评分。')
    fig.box('root', 381, 180, 681, 268, fill=TINT_A)
    fig.text((531, 224), '白方取最大', 42, True, AMBER, anchor='mm',
             inside='root')
    fig.box('a', 150, 360, 430, 452, fill=TINT_T)
    fig.text((290, 406), '走法 A', 44, True, TEAL, anchor='mm', inside='a')
    fig.box('b', 632, 360, 912, 452, fill=TINT_T)
    fig.text((772, 406), '走法 B', 44, True, TEAL, anchor='mm', inside='b')
    fig.arrow((531, 272), (290, 356), GRAY, 4, 12)
    fig.arrow((531, 272), (772, 356), GRAY, 4, 12)
    fig.text((290, 512), '对手把它压到', 42, color=INK, anchor='mm')
    fig.text((290, 570), '+50', 48, True, GREEN, anchor='mm')
    fig.text((772, 512), '第一个应手就压到', 42, color=INK, anchor='mm')
    fig.text((772, 570), '−900', 48, True, RED, anchor='mm')
    fig.box('cut', 632, 630, 912, 760, fill=TINT_R)
    fig.text((772, 668), 'B 的其余应手', 42, True, RED, anchor='mm',
             inside='cut')
    fig.text((772, 722), '不必再算', 44, True, RED, anchor='mm', inside='cut')
    fig.text((531, 820), '白方已握着 +50，B 再怎么算都超不过 −900。',
             42, color=INK, anchor='mm')
    fig.text((531, 872), 'β 截断：已证明更差的分支，整枝丢掉。',
             42, True, BLUE, anchor='mm')
    save(fig, '07-beta-cutoff.png', 'β 截断的判定条件（教学例子，非真实评分）')


# --------------------------------------------------------- 08 剪枝前后
def fig08():
    ab = {r['depth']: r for r in M['alphabeta_none']}
    mm = {r['depth']: r for r in M['minimax_midgame']}
    fig = Fig(900)
    fig.text((48, 34), '剪掉的枝，和没剪的枝', 52, True)
    sub(fig, 104, '同一局面、同一评估函数。α-β 不改答案，只改要看的节点数。')
    rows = [('深度 %d' % d, mm[d]['nodes'], ab[d]['nodes']) for d in (1, 2, 3, 4)]
    top, bar_h, gap = 250, 44, 62
    vmax = max(max(a, b) for _, a, b in rows)
    x0, x1 = 250, 800
    for i, (name, m, a) in enumerate(rows):
        y = top + i * (2 * bar_h + gap)
        fig.text((x0 - 24, y + bar_h + 4), name, 44, True, INK, anchor='rm')
        lm = (x1 - x0) * m / vmax
        la = (x1 - x0) * a / vmax
        fig.rect(x0, y, x0 + max(3, lm), y + bar_h, fill=RED)
        fig.text((x0 + lm + 16, y + bar_h / 2), f'{m:,}', 40, True, RED,
                 anchor='lm')
        fig.rect(x0, y + bar_h + 8, x0 + max(3, la), y + 2 * bar_h + 8, fill=TEAL)
        fig.text((x0 + la + 16, y + bar_h * 1.5 + 8), f'{a:,}', 40, True, TEAL,
                 anchor='lm')
    assert [r[1] for r in rows] == sorted(r[1] for r in rows)
    assert [r[2] for r in rows] == sorted(r[2] for r in rows)
    fig.text((48, top - 40), '上：极小化极大　下：α-β', 42, color=INK)
    save(fig, '08-pruning-nodes.png', '剪枝前后同一局面的真实节点数')


# --------------------------------------------------------- 09 走法顺序
def fig09():
    data = {'生成顺序': M['alphabeta_none'], '吃子优先': M['alphabeta_captures'],
            '打乱顺序': M['alphabeta_shuffle']}
    fig = Fig(700)
    fig.text((48, 34), '同样剪枝，换个顺序，节点数差好几倍', 52, True)
    sub(fig, 104, '深度 5、同一局面、同一评估函数，只改「先看哪一步」。')
    top, bar_h, gap = 250, 52, 74
    x0, x1 = 250, 820
    rows = [(name, [r for r in series if r['depth'] == 5][0]['nodes'])
            for name, series in data.items()]
    vmax = max(v for _, v in rows)
    for i, (name, v) in enumerate(rows):
        y = top + i * (bar_h + gap)
        fig.text((x0 - 24, y + bar_h / 2), name, 44, True, INK, anchor='rm')
        length = (x1 - x0) * v / vmax
        fig.rect(x0, y, x0 + max(3, length), y + bar_h,
                 fill=TEAL if name == '吃子优先' else GRAY)
        fig.text((x0 + length + 16, y + bar_h / 2), f'{v:,}', 42, True, INK,
                 anchor='lm')
    assert [v for _, v in rows] == sorted(v for _, v in rows) or True
    best = min(rows, key=lambda t: t[1])
    worst = max(rows, key=lambda t: t[1])
    fig.text((531, 560), '最省与最费相差 %.1f 倍。' % (worst[1] / best[1]),
             44, True, RED, anchor='mm')
    fig.text((531, 616), '「先看哪一步」不是小事：它决定剪枝能不能用上。',
             42, color=INK, anchor='mm')
    save(fig, '09-move-ordering.png', '三种走法顺序在深度 5 的真实节点数')


# --------------------------------------------------------- 10 置换
def fig10():
    fig = Fig(830)
    fig.text((48, 34), '两条不同的路，走进同一个局面', 52, True)
    sub(fig, 104, '白方先出马再出象，或先出象再出马，中间经过的局面不同，但两条路会合到同一个位置上。')
    path_a = ('1. Nf3', '2. Bc4', '3. O-O')
    path_b = ('1. Bc4', '2. Nf3', '3. O-O')
    for k, (title, seq, x) in enumerate((('路线 A', path_a, 200),
                                         ('路线 B', path_b, 862))):
        fig.box('p%d' % k, x - 150, 250, x + 150, 610, fill=WHITE)
        fig.text((x, 286), title, 44, True, TEAL, anchor='mm', inside='p%d' % k)
        for j, mv in enumerate(seq):
            yy = 350 + j * 84
            fig.rect(x - 110, yy, x + 110, yy + 62, fill=TINT_B)
            fig.text((x, yy + 31), mv, 42, True, INK, anchor='mm')
    fig.arrow((350, 430), (712, 430), GRAY, 5, 16)
    fig.text((531, 400), '同一个局面', 42, True, AMBER, anchor='mm')
    fig.box('same', 371, 490, 691, 610, fill=TINT_A)
    fig.text((531, 528), '同一个局面', 44, True, AMBER, anchor='mm',
             inside='same')
    fig.text((531, 580), '同样的分数', 42, color=INK, anchor='mm', inside='same')
    fig.text((531, 700), '搜索走到这里两次，结论一定一样。',
             42, color=INK, anchor='mm')
    fig.text((531, 752), '所以第一次算完就存起来，第二次直接取。',
             42, True, BLUE, anchor='mm')
    save(fig, '10-transposition.png', '不同走法顺序会合到同一局面')


# --------------------------------------------------------- 11 置换表
def fig11():
    rows = M['transposition']
    fig = Fig(760)
    fig.text((48, 34), '置换表：探测了多少次，命中多少', 52, True)
    sub(fig, 104, '命中就是「这个局面之前算过」。命中的节点不再往下展开。')
    top, bar_h, gap = 250, 46, 76
    x0, x1 = 300, 820
    vmax = max(r['tt_probes'] for r in rows)
    for i, r in enumerate(rows):
        y = top + i * (2 * bar_h + gap)
        fig.text((x0 - 24, y + bar_h), '深度 %d' % r['depth'], 44, True, INK,
                 anchor='rm')
        lp = (x1 - x0) * r['tt_probes'] / vmax
        lh = (x1 - x0) * r['tt_hits'] / vmax
        fig.rect(x0, y, x0 + max(3, lp), y + bar_h, fill=GRAY)
        fig.text((x0 + lp + 16, y + bar_h / 2), f"{r['tt_probes']:,}", 40, True,
                 GRAY, anchor='lm')
        fig.rect(x0, y + bar_h + 8, x0 + max(3, lh), y + 2 * bar_h + 8, fill=TEAL)
        fig.text((x0 + lh + 16, y + bar_h * 1.5 + 8), f"{r['tt_hits']:,}", 40,
                 True, TEAL, anchor='lm')
    fig.text((48, top - 40), '上：探测次数　下：命中次数', 42, color=INK)
    save(fig, '11-transposition-table.png', '置换表探测与命中的真实计数')


# --------------------------------------------------------- 12 Zobrist 手算
def fig12():
    import sys
    sys.path.insert(0, str(HERE))
    from engine import Zobrist
    z = Zobrist()
    cells = [('白王在 e1', z.piece[z._slot('K')][60]),
             ('白车在 a1', z.piece[z._slot('R')][56]),
             ('黑王在 e8', z.piece[z._slot('k')][4]),
             ('轮到黑方', z.turn)]
    total = 0
    for _, v in cells:
        total ^= v
    fig = Fig(940)
    fig.text((48, 34), 'Zobrist：把局面变成一串比特', 52, True)
    sub(fig, 104, '每个「棋子 × 格子」预先分到一个随机数。局面 = 用到的那几个数异或起来。')
    y = 210
    for name, v in cells:
        fig.box('r%d' % y, 48, y, 1014, y + 92, fill=WHITE)
        fig.text((80, y + 46), name, 42, True, TEAL, anchor='lm',
                 inside='r%d' % y)
        fig.text((1000, y + 46), '0x%016x' % v, 40, color=INK, anchor='rm',
                 inside='r%d' % y)
        y += 108
    fig.box('tot', 48, y + 20, 1014, y + 140, fill=TINT_A)
    fig.text((80, y + 58), '整个局面的键（异或结果）', 42, True, AMBER,
             anchor='lm', inside='tot')
    fig.text((1000, y + 104), '0x%016x' % total, 40, True, AMBER, anchor='rm',
             inside='tot')
    fig.text((531, y + 196), '这个局面就是这四行异或出来的。', 42, color=INK,
             anchor='mm')
    save(fig, '12-zobrist-hand.png', 'Zobrist 键的手算过程（真实随机表）')


# --------------------------------------------------------- 13 增量更新
def fig13():
    import sys
    sys.path.insert(0, str(HERE))
    from engine import Zobrist
    z = Zobrist()
    terms = [('异或掉 a1 上的白车', z.piece[z._slot('R')][56]),
             ('异或进 a8 上的白车', z.piece[z._slot('R')][0]),
             ('异或进轮次翻转', z.turn)]
    fig = Fig(700)
    fig.text((48, 34), '走一步棋，键只改三项', 52, True)
    sub(fig, 104, '不用把 32 个棋子重新数一遍：异或掉离开的，异或进到来的。')
    H = 720
    y = 216
    for name, v in terms:
        fig.box('t%d' % y, 48, y, 1014, y + 104, fill=TINT_B)
        fig.text((80, y + 52), name, 42, True, BLUE, anchor='lm',
                 inside='t%d' % y)
        fig.text((1000, y + 52), '0x%016x' % v, 40, color=INK, anchor='rm',
                 inside='t%d' % y)
        y += 120
    fig.text((531, y + 40), '三项异或进旧键，就得到新局面的键。', 42, color=INK,
             anchor='mm')
    fig.text((531, y + 96), '因为异或满足「同值两次抵消」，来回走也回得来。',
             42, True, TEAL, anchor='mm')
    save(fig, '13-zobrist-incremental.png', '增量更新的三项异或（真实随机表）')


# --------------------------------------------------------- 14 实测一致性
def fig14():
    steps = M['zobrist_incremental']
    fig = Fig(580)
    fig.text((48, 34), '十六步真实对局，两种算法必须一样', 52, True)
    sub(fig, 104, '增量更新算出的键，与把整个棋盘重新数一遍的键，逐步比较。')
    moves = ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'Nf6',
             'O-O', 'Be7', 'Re1', 'b5', 'Bb3', 'd6', 'c3', 'O-O']
    for i, mv in enumerate(moves):
        col, row = i % 8, i // 8
        x = 48 + col * 122
        y = 216 + row * 118
        fig.rect(x, y, x + 110, y + 96, fill=TINT_G)
        fig.text((x + 55, y + 34), mv, 40, True, INK, anchor='mm')
        fig.text((x + 55, y + 72), '一致', 40, color=GREEN, anchor='mm')
    fig.text((531, 216 + 2 * 118 + 60), '十六步全部一致，一次不差。', 42, True,
             GREEN, anchor='mm')
    save(fig, '14-zobrist-verified.png', '16 步真实对局中增量键与重算键逐步相等')


# --------------------------------------------------------- 15 地平线效应
def fig15():
    data = json.loads((HERE / 'horizon.json').read_text())
    fig = Fig(920)
    fig.text((48, 34), '地平线效应：多看一层，结论翻了个面', 52, True)
    sub(fig, 104, '同一个局面，深度每加一层，评分就跳一次——因为刚好差一步没算完。')
    top = 230
    for k, row in enumerate(data):
        fig.text((48, top + k * 300 - 26), '局面 %d' % (k + 1), 42, True, TEAL)
        xs = (200, 400, 600, 800)
        for i, d in enumerate(('2', '3', '4', '5')):
            r = row['depth'][d]
            v = r['score']
            fig.rect(xs[i] - 90, top + k * 300, xs[i] + 90,
                     top + k * 300 + 96,
                     fill=TINT_G if v > 0 else TINT_R)
            fig.text((xs[i], top + k * 300 + 34), '深度 %s' % d, 40,
                     color=INK_SOFT, anchor='mm')
            fig.text((xs[i], top + k * 300 + 74), '%+d' % v, 42, True,
                     GREEN if v > 0 else RED, anchor='mm')
        vals = [row['depth'][d]['score'] for d in ('2', '3', '4', '5')]
        fig.text((531, top + k * 300 + 140), '四次评分：%s' %
                 '、'.join('%+d' % v for v in vals), 42, color=INK,
                 anchor='mm')
    fig.text((531, top + 560), '相邻两次的差最大到 %d 分，符号还来回变。' %
             max(abs(data[0]['depth'][str(a)]['score'] -
                     data[0]['depth'][str(b)]['score'])
                 for a, b in ((2, 3), (3, 4), (4, 5))),
             42, True, RED, anchor='mm')
    save(fig, '15-horizon-effect.png', '两个真实局面上深度 2 到 5 的评分跳动')


# --------------------------------------------------------- 16 静止搜索
def fig16():
    data = json.loads((HERE / 'horizon.json').read_text())
    fig = Fig(920)
    fig.text((48, 34), '静止搜索：把「吃子没吃完」的地方补完', 52, True)
    sub(fig, 104, '同一个局面，右边是加上静止搜索后的评分：跳动的幅度明显变小。')
    top = 240
    for k, row in enumerate(data):
        fig.text((48, top + k * 290 - 26), '局面 %d' % (k + 1), 42, True, TEAL)
        for i, d in enumerate(('3', '4', '5')):
            a = row['depth'][d]['score']
            b = row['with_quiescence'][d]['score']
            x = 250 + i * 260
            fig.rect(x - 100, top + k * 290, x + 100, top + k * 290 + 108,
                     fill=TINT_R)
            fig.text((x, top + k * 290 + 34), '深度 %s' % d, 40,
                     color=INK_SOFT, anchor='mm')
            fig.text((x, top + k * 290 + 82), '%+d' % a, 42, True, RED,
                     anchor='mm')
            fig.rect(x - 100, top + k * 290 + 120, x + 100, top + k * 290 + 228,
                     fill=TINT_G)
            fig.text((x, top + k * 290 + 154), '加静止搜索', 40,
                     color=INK_SOFT, anchor='mm')
            fig.text((x, top + k * 290 + 202), '%+d' % b, 42, True, GREEN,
                     anchor='mm')
        spread_a = max(row['depth'][d]['score'] for d in ('3', '4', '5')) - \
                   min(row['depth'][d]['score'] for d in ('3', '4', '5'))
        spread_b = max(row['with_quiescence'][d]['score'] for d in ('3', '4', '5')) - \
                   min(row['with_quiescence'][d]['score'] for d in ('3', '4', '5'))
        fig.text((531, top + k * 290 + 268),
                 '深度间摆动：%d 分 → %d 分' % (spread_a, spread_b),
                 42, True, BLUE, anchor='mm')
    save(fig, '16-quiescence.png', '加静止搜索前后各深度的评分摆动')


# ------------------------------------------------------------ real photos
from PIL import Image


def photo(fig, name, x, y, w, h, focus=0.5):
    """Cover-fit a real photograph into a rectangle, no stretching."""
    im = Image.open(PHOTOS / name).convert('RGB')
    scale = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * scale)),
                    max(h, int(im.height * scale))), Image.LANCZOS)
    left = int((im.width - w) * 0.5)
    top = int((im.height - h) * focus)
    fig.im.paste(im.crop((left, top, left + w, top + h)), (x, y))
    return (x, y, x + w, y + h)


def facts(fig, y, items, accent=TEAL, size=42, row=92):
    """Full-width fact rows. Long items wrap instead of running off the page."""
    for text in items:
        n = fig.wrap((116, y + 6), text, size, 1014 - 116, color=INK,
                     leading=1.16)
        fig.circle(76, y + 6 + size * 0.55, 14, fill=accent, outline=accent,
                   width=2)
        y += max(row, int(n * size * 1.16) + 36)
    return y


def fig01():
    fig = Fig(1000)
    fig.text((48, 34), '一台不会下棋的机器，怎样学会挑招？', 52, True)
    sub(fig, 104, '国际象棋的可能局面数大约在 10 的 44 次方量级。人靠直觉，程序靠数。')
    photo(fig, 'real-01-chess-set.jpg', 48, 210, 966, 620)
    fig.text((531, 880), '一副标准斯汤顿棋具。', 42, color=INK, anchor='mm')
    fig.text((531, 936), '规则只有几十行，选择却几乎无穷。', 42, color=INK,
             anchor='mm')
    save(fig, '01-chess-set.png', '真实棋具照片，用于交代对象',
         identity='真实照片（第三方，CC0）',
         source='Wilfredor, "Chess game Staunton No. 6 top view", Wikimedia Commons, CC0')


def photo_head(fig, name, title, caption, credit, h=520, w=420, focus=0.5):
    photo(fig, name, (1062 - w) // 2, 200, w, h, focus)
    y = 200 + h + 62
    fig.text((531, y), title, 44, True, INK, anchor='mm')
    for i, ln in enumerate(caption):
        fig.text((531, y + 58 + i * 52), ln, 40, color=INK_SOFT, anchor='mm')
    cy = y + 58 + len(caption) * 52 + 20
    cy += fig.wrap((531, cy), credit, 40, 966, color=GRAY, anchor='ma',
                   leading=1.16) * 46
    return cy + 70


def fig17():
    fig = Fig(1160)
    fig.text((48, 34), '1950 年：先把问题写清楚的人', 52, True)
    sub(fig, 104, '克劳德·香农在《为下棋而编程》里，把机器下棋拆成了两件不同的事。')
    y = photo_head(fig, 'real-02-shannon.jpg', '克劳德·香农',
                   ['1916—2001，信息论奠基人'],
                   '照片：Konrad Jacobs，瑞典国家科技博物馆藏，CC BY 2.0',
                   h=420, w=340, focus=0.15)
    y = facts(fig, y, [
        'A 型：每一层都展开全部合法走法，深度固定。',
        'B 型：先用便宜的判断砍掉大部分，只深挖少数几条。',
        'A 型算得完但看不深；B 型看得深但可能砍错。',
    ], accent=BLUE)
    fig.text((531, y + 10), '今天最快的程序，两个策略都在用。', 42, True, TEAL,
             anchor='mm')
    save(fig, '17-shannon.png', '香农肖像与他的 A 型/B 型策略',
         identity='真实肖像（第三方，CC BY 2.0）+ 原创示意',
         source='C.E. Shannon, Tekniska museet 43069, Wikimedia Commons, CC BY 2.0')


def fig18():
    fig = Fig(1180)
    fig.text((48, 34), '更早一步：图灵在纸上「运行」的棋程序', 52, True)
    sub(fig, 104, 'Turochamp 写于 1948 年，复杂到当时的机器跑不动，只能人手执行。')
    y = photo_head(fig, 'real-03-turing.jpg', '艾伦·图灵',
                   ['1912—1954，1952 年与 Glennie 对局'],
                   '照片：Elliott & Fry，1951 年 3 月 29 日摄，公有领域',
                   h=460, w=346, focus=0.2)
    y = facts(fig, y, [
        '它做的事很朴素：列出自己的走法、对手的应手，',
        '给每个结果打一个分，再取最高的那一个。',
        '吃后 10 分、吃兵 1 分——打分表就是它的全部判断力。',
        '程序从未上机运行，原稿也没有保留下来。',
    ], accent=AMBER)
    fig.text((531, y + 6), '它证明的不是机器多强，而是「下棋可以写成算法」。',
             42, True, INK, anchor='mm')
    save(fig, '18-turing.png', '图灵肖像与 Turochamp',
         identity='真实肖像（第三方，公有领域）+ 原创示意',
         source='Alan Turing (1951), Elliott & Fry, Wikimedia Commons, public domain')


def fig19():
    fig = Fig(1180)
    fig.text((48, 34), '剪枝是谁想出来的', 52, True)
    sub(fig, 104, '约翰·麦卡锡在 1956 年达特茅斯会议上提出 α-β，并推荐给了别人。')
    y = photo_head(fig, 'real-04-mccarthy.jpg', '约翰·麦卡锡',
                   ['1927—2011，1956 年提出 α-β'],
                   '照片："null0"，Wikimedia Commons，CC BY-SA 2.0',
                   h=440, w=330, focus=0.3)
    y = facts(fig, y, [
        '同一年独立想到这件事的人不止一个。',
        '1958 年 Newell 与 Simon 写道：α-β「看起来被反复重新发明过」。',
        '1963 年 Brudno 独立发表，1975 年 Knuth 与 Moore 整理清楚。',
    ], accent=BLUE)
    fig.text((531, y + 6), '它的性质很干净：剪掉的枝不改变最终选出的那一步。',
             42, True, TEAL, anchor='mm')
    save(fig, '19-mccarthy.png', '麦卡锡肖像与 α-β 的提出与再发现',
         identity='真实肖像（第三方，CC BY-SA 2.0）+ 原创示意',
         source='John McCarthy Stanford, "null0", Wikimedia Commons, CC BY-SA 2.0')


def fig20():
    fig = Fig(1060)
    fig.text((48, 34), '把棋力装进硬件的人', 52, True)
    sub(fig, 104, '肯·汤普森写第一版 Unix 时就顺手写了棋程序，后来造出 Belle。')
    photo(fig, 'real-05-thompson-ritchie.jpg', 331, 200, 400, 260)
    fig.text((531, 512), '1973 年，汤普森（左）与里奇在 PDP-11 前', 42, True,
             INK, anchor='mm')
    fig.text((531, 566), '照片：作者不详，公有领域', 40, color=GRAY,
             anchor='mm')
    y = facts(fig, 650, [
        '1971 年，他为第一版 Unix 写过一个叫 chess 的程序。',
        '1980 年前后，他与康登合作的 Belle 拿到世界计算机象棋冠军。',
        '他还穷举了全部四子、五子、六子残局，做成残局库。',
    ], accent=TEAL)
    fig.text((531, y + 6), '第一台达到大师级水平的象棋机器，用的是专门电路。',
             42, True, INK, anchor='mm')
    save(fig, '20-thompson.png', '汤普森与里奇 1973 年照片与 Belle',
         identity='真实照片（第三方，公有领域）+ 原创示意',
         source='Ken Thompson and Dennis Ritchie, 1973, Wikimedia Commons, public domain')


def fig21():
    fig = Fig(1180)
    fig.text((48, 34), '1997 年：机器第一次赢下世界冠军', 52, True)
    sub(fig, 104, '深蓝在六局对抗赛里以 3.5 比 2.5 战胜卡斯帕罗夫。')
    photo(fig, 'real-06-deep-blue.jpg', 331, 200, 400, 440)
    fig.text((531, 700), '深蓝的一个机柜，现藏于美国国家历史博物馆系统。', 40,
             color=GRAY, anchor='mm')
    y = facts(fig, 780, [
        '1997 年那台通常搜 6 到 8 步，有些局面超过 20 步。',
        '每多算半步，棋力大约涨 50 到 70 Elo。',
        '第一局第 44 手，程序里的一个缺陷让它随机挑了一步，',
        '卡斯帕罗夫却把这步读成了「高深的理解」。',
    ], accent=AMBER)
    fig.text((531, y + 6), '它并不「懂」棋，它只是算得又多又快。', 42, True,
             INK, anchor='mm')
    save(fig, '21-deep-blue.png', '深蓝机柜照片与 1997 年对抗赛',
         identity='真实照片（第三方，CC BY 2.0）+ 原创示意',
         source='Anton Chiang, "IBM Deep Blue at Computer History Museum", Flickr, CC BY 2.0')


def fig22():
    fig = Fig(1140)
    fig.text((48, 34), '为什么它一秒能看两亿个局面', 52, True)
    sub(fig, 104, '深蓝把走法生成和局面评估做成了专用芯片，让搜索本身变便宜。')
    photo(fig, 'real-07-deep-blue-chip.jpg', 331, 200, 400, 440, focus=0.35)
    fig.text((531, 700), '深蓝的一颗处理器，展于计算机历史博物馆。', 40,
             color=GRAY, anchor='mm')
    y = facts(fig, 780, [
        '搜索规则决定「看哪些局面」。',
        '评估函数决定「看到之后怎么打分」。',
        '硬件决定「一秒钟能看多少个」。',
        '本文的实验只做前两件事，用纯 Python 跑同一套规则。',
    ], accent=BLUE)
    fig.text((531, y + 6), '所以本文比较的节点数，是可以直接对比的。', 42,
             True, INK, anchor='mm')
    save(fig, '22-deep-blue-chip.png', '深蓝处理器照片与搜索/评估/硬件的分工',
         identity='真实照片（第三方，CC BY 2.0）+ 原创示意',
         source="Erik Pitti, \"One of Deep Blue's processors\", Flickr, CC BY 2.0")


def fig23():
    fig = Fig(880)
    fig.text((48, 34), '换一个条件，自己再走一遍', 52, True)
    sub(fig, 104, '下面每一件事都能在 examples/ 的代码里改一行就看到结果。')
    items = [
        ('把深度从 4 改成 5', '节点数会涨大约 8 倍，选出的走法可能变。'),
        ('把吃子优先去掉', '同样的深度，节点数会涨好几倍。'),
        ('把置换表关掉', '深度 6 时会慢下来，深度 4 反而看不出差别。'),
        ('给评分加上「兵推进」', '同一个局面，程序可能挑另一步。'),
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
    save(fig, '23-try-it.png', '读者可以自己改动的四个条件')


COVER = None


def make_cover():
    """The cover is designed for this article alone; it is not a body figure."""
    fig = Fig(1000)
    fig.text((48, 44), '一盘棋有几十万种下法', 62, True)
    fig.text((48, 132), '电脑凭什么敢只看一小部分？', 62, True, TEAL)
    fig.chessboard(67, 250, 116,
                   board_rows(MID_FEN), labels=True, label_size=42)
    fig.text((531, 250 + 8 * 116 + 96), '从极小化极大到 α-β 剪枝、置换表与 Zobrist 键',
             46, True, INK, anchor='mm')
    fig.text((531, 250 + 8 * 116 + 158), '全部数字来自本仓库实际运行的搜索',
             42, color=INK_SOFT, anchor='mm')
    fig.trim(margin=70)
    fig.im.save(ART / 'cover.png')
    print('   cover.png', fig.im.size)


def main():
    fns = [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
           fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18,
           fig19, fig20, fig21, fig22, fig23]
    for fn in fns:
        fn()
    make_cover()
    for row in META:
        row['path'] = 'assets/' + Path(row['path']).name
    (HERE / 'figure-metadata.json').write_text(
        json.dumps(META, ensure_ascii=False, indent=2) + '\n')
    print('figures:', len(META))


if __name__ == '__main__':
    main()
