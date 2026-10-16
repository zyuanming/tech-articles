"""Minimal but complete chess rules + search, standard library only. MIT.

Board is a list of 64 one-character strings, index 0 = a8, 63 = h1.
White pieces are upper case, black lower case, '.' empty.
"""
from __future__ import annotations

WHITE, BLACK = 'w', 'b'
FILES = 'abcdefgh'
START = ('rnbqkbnr' 'pppppppp' '........' '........'
         '........' '........' 'PPPPPPPP' 'RNBQKBNR')

KNIGHT_D = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
KING_D = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
BISHOP_D = ((-1, -1), (-1, 1), (1, -1), (1, 1))
ROOK_D = ((-1, 0), (1, 0), (0, -1), (0, 1))


def sq_to_xy(i):
    return i % 8, i // 8          # file 0..7 (a..h), rank 0..7 (8..1)


def xy_to_sq(x, y):
    return y * 8 + x


def name(i):
    x, y = sq_to_xy(i)
    return FILES[x] + str(8 - y)


def parse(text):
    """Accepts the 64-char board string (rank 8 first)."""
    assert len(text) == 64, len(text)
    return list(text)


def from_fen(fen):
    """Parse a FEN string into a Pos (used to load real game positions)."""
    parts = fen.split()
    rows = parts[0].split('/')
    assert len(rows) == 8, fen
    out = []
    for row in rows:
        for ch in row:
            if ch.isdigit():
                out.extend('.' * int(ch))
            else:
                out.append(ch)
    assert len(out) == 64, fen
    turn = parts[1] if len(parts) > 1 else 'w'
    castle = parts[2] if len(parts) > 2 and parts[2] != '-' else ''
    ep = -1
    if len(parts) > 3 and parts[3] != '-':
        x = FILES.index(parts[3][0])
        y = 8 - int(parts[3][1])
        ep = xy_to_sq(x, y)
    return Pos(out, turn, castle, ep)


def is_white(p):
    return p != '.' and p.isupper()


def colour_of(p):
    return WHITE if p.isupper() else BLACK


class Pos:
    __slots__ = ('b', 'turn', 'castle', 'ep')

    def __init__(self, board=START, turn=WHITE, castle='KQkq', ep=-1):
        assert len(board) == 64, f'board must be 64 squares, got {len(board)}'
        self.b = list(board)
        self.turn = turn
        self.castle = castle
        self.ep = ep

    def copy(self):
        return Pos(self.b, self.turn, self.castle, self.ep)

    def key(self):
        return (''.join(self.b), self.turn, self.castle, self.ep)

    def find_king(self, colour):
        target = 'K' if colour == WHITE else 'k'
        return self.b.index(target)


def _ray(pos, i, dirs):
    x0, y0 = sq_to_xy(i)
    for dx, dy in dirs:
        x, y = x0 + dx, y0 + dy
        while 0 <= x < 8 and 0 <= y < 8:
            j = xy_to_sq(x, y)
            p = pos.b[j]
            if p == '.':
                yield j
            else:
                yield j
                break
            x += dx
            y += dy


def attacked(pos, target, by_colour):
    """Is square `target` attacked by `by_colour`?"""
    tx, ty = sq_to_xy(target)
    b = pos.b
    # pawns
    dy = 1 if by_colour == WHITE else -1       # attacker sits one rank "behind"
    pawn = 'P' if by_colour == WHITE else 'p'
    for dx in (-1, 1):
        x, y = tx + dx, ty + dy
        if 0 <= x < 8 and 0 <= y < 8 and b[xy_to_sq(x, y)] == pawn:
            return True
    # knights
    kn = 'N' if by_colour == WHITE else 'n'
    for dx, dy2 in KNIGHT_D:
        x, y = tx + dx, ty + dy2
        if 0 <= x < 8 and 0 <= y < 8 and b[xy_to_sq(x, y)] == kn:
            return True
    # king
    kg = 'K' if by_colour == WHITE else 'k'
    for dx, dy2 in KING_D:
        x, y = tx + dx, ty + dy2
        if 0 <= x < 8 and 0 <= y < 8 and b[xy_to_sq(x, y)] == kg:
            return True
    # sliding
    for dirs, pieces in ((BISHOP_D, 'BQ' if by_colour == WHITE else 'bq'),
                         (ROOK_D, 'RQ' if by_colour == WHITE else 'rq')):
        for dx, dy2 in dirs:
            x, y = tx + dx, ty + dy2
            while 0 <= x < 8 and 0 <= y < 8:
                p = b[xy_to_sq(x, y)]
                if p != '.':
                    if p in pieces:
                        return True
                    break
                x += dx
                y += dy2
    return False


def in_check(pos, colour):
    return attacked(pos, pos.find_king(colour), WHITE if colour == BLACK else BLACK)


def _pseudo(pos):
    """Pseudo-legal moves as (from, to, promo)."""
    b, me = pos.b, pos.turn
    mine = (lambda p: p.isupper()) if me == WHITE else (lambda p: p.islower())
    out = []
    for i, p in enumerate(b):
        if p == '.' or not mine(p):
            continue
        x, y = sq_to_xy(i)
        low = p.lower()
        if low == 'p':
            fwd = -1 if me == WHITE else 1
            start_rank = 6 if me == WHITE else 1
            promo_rank = 0 if me == WHITE else 7
            ny = y + fwd
            if 0 <= ny < 8 and b[xy_to_sq(x, ny)] == '.':
                j = xy_to_sq(x, ny)
                if ny == promo_rank:
                    for pr in 'qrbn':
                        out.append((i, j, pr))
                else:
                    out.append((i, j, ''))
                    if y == start_rank and b[xy_to_sq(x, y + 2 * fwd)] == '.':
                        out.append((i, xy_to_sq(x, y + 2 * fwd), ''))
            for dx in (-1, 1):
                nx = x + dx
                if not (0 <= nx < 8 and 0 <= ny < 8):
                    continue
                j = xy_to_sq(nx, ny)
                t = b[j]
                if t != '.' and not mine(t):
                    if ny == promo_rank:
                        for pr in 'qrbn':
                            out.append((i, j, pr))
                    else:
                        out.append((i, j, ''))
                elif t == '.' and j == pos.ep:
                    out.append((i, j, 'ep'))
        elif low == 'n':
            for dx, dy2 in KNIGHT_D:
                nx, ny = x + dx, y + dy2
                if 0 <= nx < 8 and 0 <= ny < 8:
                    j = xy_to_sq(nx, ny)
                    if b[j] == '.' or not mine(b[j]):
                        out.append((i, j, ''))
        elif low == 'k':
            for dx, dy2 in KING_D:
                nx, ny = x + dx, y + dy2
                if 0 <= nx < 8 and 0 <= ny < 8:
                    j = xy_to_sq(nx, ny)
                    if b[j] == '.' or not mine(b[j]):
                        out.append((i, j, ''))
        else:
            dirs = (BISHOP_D if low == 'b' else ROOK_D if low == 'r'
                    else BISHOP_D + ROOK_D)
            for j in _ray(pos, i, dirs):
                if b[j] == '.' or not mine(b[j]):
                    out.append((i, j, ''))
    return out


def _castles(pos):
    b, me = pos.b, pos.turn
    out = []
    if me == WHITE:
        home, rights, rook = 60, ('K', 'Q'), 'R'
        enemy = BLACK
    else:
        home, rights, rook = 4, ('k', 'q'), 'r'
        enemy = WHITE
    if b[home] != ('K' if me == WHITE else 'k') or in_check(pos, me):
        return out
    if rights[0] in pos.castle and b[home + 3] == rook and b[home + 1] == '.' \
            and b[home + 2] == '.':
        if not attacked(pos, home + 1, enemy) and not attacked(pos, home + 2, enemy):
            out.append((home, home + 2, 'castle'))
    if rights[1] in pos.castle and b[home - 4] == rook and b[home - 1] == '.' \
            and b[home - 2] == '.' and b[home - 3] == '.':
        if not attacked(pos, home - 1, enemy) and not attacked(pos, home - 2, enemy):
            out.append((home, home - 2, 'castle'))
    return out


def make(pos, mv):
    """Apply a legal move; returns a new Pos."""
    frm, to, promo = mv
    n = pos.copy()
    b = n.b
    me = n.turn
    p = b[frm]
    low = p.lower()
    n.ep = -1
    if promo == 'ep':
        b[to] = p
        b[frm] = '.'
        b[to + (8 if me == WHITE else -8)] = '.'
    elif promo == 'castle':
        b[to] = p
        b[frm] = '.'
        if to > frm:
            b[to - 1] = b[frm + 3]
            b[frm + 3] = '.'
        else:
            b[to + 1] = b[frm - 4]
            b[frm - 4] = '.'
    else:
        b[to] = (promo.upper() if me == WHITE else promo.lower()) if promo else p
        b[frm] = '.'
        if low == 'p' and abs(to - frm) == 16:
            n.ep = (frm + to) // 2
    if low == 'k':
        n.castle = n.castle.replace('K' if me == WHITE else 'k', '')
    for sq, ch in ((56, 'Q'), (63, 'K'), (0, 'q'), (7, 'k')):
        if frm == sq or to == sq:
            n.castle = n.castle.replace(ch, '')
    n.turn = BLACK if me == WHITE else WHITE
    return n


def legal(pos):
    me = pos.turn
    out = []
    for mv in _pseudo(pos) + _castles(pos):
        if mv[2] == 'castle':
            out.append(mv)
            continue
        nxt = make(pos, mv)
        if not in_check(nxt, me):
            out.append(mv)
    return out


def perft(pos, depth):
    if depth == 0:
        return 1
    n = 0
    for mv in legal(pos):
        n += perft(make(pos, mv), depth - 1)
    return n


def san(pos, mv):
    frm, to, promo = mv
    if promo == 'castle':
        return 'O-O' if to > frm else 'O-O-O'
    p = pos.b[frm]
    cap = pos.b[to] != '.' or promo == 'ep'
    body = ('' if p.lower() == 'p' else p.upper())
    if p.lower() == 'p' and cap:
        body = FILES[sq_to_xy(frm)[0]]
    text = body + ('x' if cap else '') + name(to)
    if promo and promo != 'ep':
        text += '=' + promo.upper()
    nxt = make(pos, mv)
    if in_check(nxt, nxt.turn):
        text += '#' if not legal(nxt) else '+'
    return text
