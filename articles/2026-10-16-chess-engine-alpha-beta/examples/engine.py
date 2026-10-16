"""Search layer: minimax, alpha-beta, move ordering, Zobrist + TT, quiescence."""
from __future__ import annotations
import random
from chesslib import (Pos, from_fen, legal, make, in_check, colour_of, sq_to_xy,
                      xy_to_sq, WHITE, BLACK, name)

VALUE = {'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000}

# A small centre-favouring table for pawns and knights, written as 8 ranks.
PST = {
    'p': [0, 0, 0, 0, 0, 0, 0, 0,
          50, 50, 50, 50, 50, 50, 50, 50,
          10, 10, 20, 30, 30, 20, 10, 10,
          5, 5, 10, 25, 25, 10, 5, 5,
          0, 0, 0, 20, 20, 0, 0, 0,
          5, -5, -10, 0, 0, -10, -5, 5,
          5, 10, 10, -20, -20, 10, 10, 5,
          0, 0, 0, 0, 0, 0, 0, 0],
    'n': [-50, -40, -30, -30, -30, -30, -40, -50,
          -40, -20, 0, 0, 0, 0, -20, -40,
          -30, 0, 10, 15, 15, 10, 0, -30,
          -30, 5, 15, 20, 20, 15, 5, -30,
          -30, 0, 15, 20, 20, 15, 0, -30,
          -30, 5, 10, 15, 15, 10, 5, -30,
          -40, -20, 0, 5, 5, 0, -20, -40,
          -50, -40, -30, -30, -30, -30, -40, -50],
}


def evaluate(pos):
    """Static score in centipawns, positive = good for White."""
    score = 0
    for i, p in enumerate(pos.b):
        if p == '.':
            continue
        low = p.lower()
        v = VALUE[low]
        if low in PST:
            table = PST[low]
            v += table[i] if p.isupper() else table[63 - i]
        score += v if p.isupper() else -v
    return score


def side_score(pos):
    """Score from the side-to-move's point of view (negamax convention)."""
    s = evaluate(pos)
    return s if pos.turn == WHITE else -s


# ------------------------------------------------------------------ Zobrist
class Zobrist:
    def __init__(self, seed=20261016):
        rng = random.Random(seed)
        self.piece = [[rng.getrandbits(64) for _ in range(64)] for _ in range(12)]
        self.turn = rng.getrandbits(64)
        self.castle = {c: rng.getrandbits(64) for c in 'KQkq'}
        self.ep = [rng.getrandbits(64) for _ in range(64)]

    def _slot(self, p):
        idx = 'pnbrqk'.index(p.lower())
        return idx if p.isupper() else idx + 6

    def full(self, pos):
        h = 0
        for i, p in enumerate(pos.b):
            if p != '.':
                h ^= self.piece[self._slot(p)][i]
        if pos.turn == BLACK:
            h ^= self.turn
        for c in pos.castle:
            h ^= self.castle[c]
        if pos.ep >= 0:
            h ^= self.ep[pos.ep]
        return h

    def update(self, pos, mv, child):
        """Incremental hash: XOR out what left, XOR in what arrived."""
        h = self.full(pos)
        frm, to, promo = mv
        p = pos.b[frm]
        if promo == 'castle':
            child_hash = self.full(child)
            return child_hash, child_hash != h
        h ^= self.piece[self._slot(p)][frm]
        h ^= self.piece[self._slot(p)][to]
        captured = pos.b[to]
        if promo == 'ep':
            cap_sq = to + (8 if pos.turn == WHITE else -8)
            h ^= self.piece[self._slot(pos.b[cap_sq])][cap_sq]
        elif captured != '.':
            h ^= self.piece[self._slot(captured)][to]
        if promo:
            np_ = promo.upper() if pos.turn == WHITE else promo
            h ^= self.piece[self._slot(np_)][to]
        if pos.ep >= 0:
            h ^= self.ep[pos.ep]
        if child.ep >= 0:
            h ^= self.ep[child.ep]
        for c in set(pos.castle) | set(child.castle):
            if (c in pos.castle) != (c in child.castle):
                h ^= self.castle[c]
        h ^= self.turn
        return h, h == self.full(child)


# ------------------------------------------------------------------- search
class Stats:
    def __init__(self):
        self.nodes = 0
        self.leaves = 0
        self.cutoffs = 0
        self.tt_hits = 0
        self.tt_probes = 0
        self.qnodes = 0


def order_moves(pos, moves, mode, tt_move=None):
    if mode == 'none':
        return moves
    scored = []
    for mv in moves:
        s = 0
        if tt_move is not None and mv == tt_move:
            s += 10 ** 6
        victim = pos.b[mv[1]]
        if victim != '.' or mv[2] == 'ep':
            attacker = pos.b[mv[0]]
            s += 10 * VALUE[victim.lower() if victim != '.' else 'p'] \
                 - VALUE[attacker.lower()]
        if mv[2] and mv[2] not in ('ep', 'castle'):
            s += VALUE[mv[2]]
        scored.append((s, mv))
    if mode == 'captures':
        scored.sort(key=lambda t: -t[0])
    elif mode == 'shuffle':
        scored.sort(key=lambda t: -t[0])
        random.Random(7).shuffle(scored)
    return [mv for _, mv in scored]


def minimax(pos, depth, st):
    """Plain minimax: every leaf is visited, no pruning at all."""
    st.nodes += 1
    moves = legal(pos)
    if depth == 0 or not moves:
        st.leaves += 1
        if not moves:
            return -100000 + depth if in_check(pos, pos.turn) else 0
        return side_score(pos)
    best = -10 ** 9
    for mv in moves:
        v = -minimax(make(pos, mv), depth - 1, st)
        if v > best:
            best = v
    return best


def alphabeta(pos, depth, alpha, beta, st, order='none', tt=None, zob=None,
              quiesce=False):
    st.nodes += 1
    key = None
    tt_move = None
    if tt is not None:
        key = zob.full(pos)
        st.tt_probes += 1
        hit = tt.get(key)
        if hit is not None and hit[1] >= depth:
            st.tt_hits += 1
            return hit[0]
        if hit is not None:
            tt_move = hit[2]
    moves = legal(pos)
    if not moves:
        st.leaves += 1
        return -100000 + depth if in_check(pos, pos.turn) else 0
    if depth == 0:
        if quiesce:
            return quiescence(pos, alpha, beta, st)
        st.leaves += 1
        return side_score(pos)
    moves = order_moves(pos, moves, order, tt_move)
    best, best_mv = -10 ** 9, moves[0]
    for mv in moves:
        v = -alphabeta(make(pos, mv), depth - 1, -beta, -alpha, st, order,
                       tt, zob, quiesce)
        if v > best:
            best, best_mv = v, mv
        if best > alpha:
            alpha = best
        if alpha >= beta:
            st.cutoffs += 1
            break
    if tt is not None:
        tt[key] = (best, depth, best_mv)
    return best


def quiescence(pos, alpha, beta, st):
    st.qnodes += 1
    stand = side_score(pos)
    if stand >= beta:
        return beta
    if stand > alpha:
        alpha = stand
    caps = [m for m in legal(pos) if pos.b[m[1]] != '.' or m[2] == 'ep']
    caps = order_moves(pos, caps, 'captures')
    for mv in caps:
        v = -quiescence(make(pos, mv), -beta, -alpha, st)
        if v >= beta:
            return beta
        if v > alpha:
            alpha = v
    return alpha


def best_move(pos, depth, **kw):
    """Return (move, score, stats) for the side to move."""
    st = Stats()
    alpha, beta = -10 ** 9, 10 ** 9
    best, best_mv = -10 ** 9, None
    moves = order_moves(pos, legal(pos), kw.get('order', 'none'))
    for mv in moves:
        v = -alphabeta(make(pos, mv), depth - 1, -beta, -alpha, st,
                       kw.get('order', 'none'), kw.get('tt'), kw.get('zob'),
                       kw.get('quiesce', False))
        if v > best:
            best, best_mv = v, mv
        if best > alpha:
            alpha = best
    return best_mv, best, st
