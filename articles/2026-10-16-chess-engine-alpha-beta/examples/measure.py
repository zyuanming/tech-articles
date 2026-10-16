import sys, time, json
sys.path.insert(0, '/tmp/chess')
from chesslib import from_fen, legal, make, san, Pos, name
from engine import (Stats, minimax, alphabeta, best_move, Zobrist, quiescence,
                    evaluate, side_score)
import random

OUT = {}
START = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -'
MID = 'r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq -'

def timed(fn):
    t = time.time(); v = fn(); return v, time.time() - t

# 1. plain minimax, depth by depth
p = from_fen(MID)
mm = []
for d in range(1, 5):
    st = Stats()
    (v), dt = timed(lambda: minimax(p, d, st))
    mm.append(dict(depth=d, score=v, nodes=st.nodes, leaves=st.leaves,
                   seconds=round(dt, 3)))
    print('minimax', mm[-1], flush=True)
    if dt > 120: break
OUT['minimax_midgame'] = mm

# 2. alpha-beta, with and without ordering
for order in ('none', 'captures', 'shuffle'):
    rows = []
    for d in range(1, 7):
        st = Stats()
        (v), dt = timed(lambda: alphabeta(p, d, -10**9, 10**9, st, order))
        rows.append(dict(depth=d, score=v, nodes=st.nodes, cutoffs=st.cutoffs,
                         seconds=round(dt, 3)))
        print('ab', order, rows[-1], flush=True)
        if dt > 60: break
    OUT['alphabeta_' + order] = rows

# 3. best-move agreement, minimax vs alpha-beta
agree = []
for d in range(1, 5):
    st1 = Stats(); st2 = Stats()
    mv1, sc1, _ = best_move(p, d, order='none')
    mv2, sc2, _ = best_move(p, d, order='captures')
    agree.append(dict(depth=d, minimax_move=san(p, mv1), minimax_score=sc1,
                      alphabeta_move=san(p, mv2), alphabeta_score=sc2,
                      same=(mv1 == mv2)))
    print('agree', agree[-1], flush=True)
OUT['best_move_agreement'] = agree

# 4. transposition table
z = Zobrist()
rows = []
for d in (4, 5, 6):
    st = Stats(); (v), dt = timed(lambda: alphabeta(p, d, -10**9, 10**9, st, 'captures'))
    st2 = Stats(); tt = {}
    (v2), dt2 = timed(lambda: alphabeta(p, d, -10**9, 10**9, st2, 'captures', tt, z))
    rows.append(dict(depth=d, without_tt_nodes=st.nodes, without_tt_s=round(dt, 3),
                     with_tt_nodes=st2.nodes, with_tt_s=round(dt2, 3),
                     tt_probes=st2.tt_probes, tt_hits=st2.tt_hits,
                     tt_entries=len(tt), same_score=(v == v2)))
    print('tt', rows[-1], flush=True)
OUT['transposition'] = rows

# 5. zobrist incremental vs recomputed over a real game line
line = ['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1b5', 'a7a6', 'b5a4', 'g8f6',
        'e1g1', 'f8e7', 'f1e1', 'b7b5', 'a4b3', 'd7d6', 'c2c3', 'e8g8']
pos = Pos()
inc = z.full(pos)
check = []
for tok in line:
    frm = (8 - int(tok[1])) * 8 + 'abcdefgh'.index(tok[0])
    to = (8 - int(tok[3])) * 8 + 'abcdefgh'.index(tok[2])
    mv = None
    for m in legal(pos):
        if m[0] == frm and m[1] == to:
            mv = m; break
    assert mv is not None, tok
    nxt = make(pos, mv)
    inc, matches = z.update(pos, mv, nxt)
    full = z.full(nxt)
    check.append(dict(move=san(pos, mv), incremental=inc, recomputed=full,
                      equal=(inc == full)))
    assert inc == full, (tok, hex(inc), hex(full))
    pos = nxt
OUT['zobrist_incremental'] = dict(steps=len(check),
                                  all_equal=all(c['equal'] for c in check),
                                  first=check[0], last=check[-1],
                                  final_hash=hex(inc))

# 6. collision probe: how many distinct positions share a hash
rng = random.Random(11)
seen = {}
pos = Pos()
for _ in range(4000):
    moves = legal(pos)
    mv = rng.choice(moves)
    pos = make(pos, mv)
    h = z.full(pos)
    seen.setdefault(h, set()).add(''.join(pos.b) + pos.turn)
    if len(legal(pos)) == 0:
        pos = Pos()
OUT['zobrist_collisions'] = dict(positions=sum(len(v) for v in seen.values()),
                                 distinct_hashes=len(seen),
                                 collisions=sum(len(v) - 1 for v in seen.values()))

# 7. horizon effect: depth 4 vs depth 5 on the same position
hz = []
for fen in ['r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq -',
            'rnbqkbnr/ppp2ppp/8/3pp3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -']:
    q = from_fen(fen)
    row = dict(fen=fen)
    for d in (2, 3, 4, 5):
        st = Stats()
        mv, sc, _ = best_move(q, d, order='captures')
        row['d%d' % d] = dict(move=san(q, mv), score=sc, nodes=st.nodes)
    st = Stats()
    mv, sc, _ = best_move(q, 5, order='captures', tt={}, zob=z, quiesce=True)
    row['d5_quiescence'] = dict(move=san(q, mv), score=sc, nodes=st.nodes,
                                qnodes=st.qnodes)
    hz.append(row)
    print('horizon', row, flush=True)
OUT['horizon'] = hz

json.dump(OUT, open('/tmp/chess/measurements.json', 'w'), indent=2, ensure_ascii=False)
print('DONE', flush=True)
