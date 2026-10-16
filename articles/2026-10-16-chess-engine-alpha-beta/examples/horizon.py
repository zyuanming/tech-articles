#!/usr/bin/env python3
"""Horizon effect and quiescence search, measured on two real positions.

Writes horizon.json next to this file. Standard library only. MIT.
"""
from __future__ import annotations
import json
import time
from pathlib import Path

from chesslib import from_fen, san
from engine import best_move

HERE = Path(__file__).resolve().parent

POSITIONS = [
    'r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq -',
    'rnbqkbnr/ppp2ppp/8/3pp3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -',
]


def run():
    out = []
    for fen in POSITIONS:
        pos = from_fen(fen)
        row = {'fen': fen, 'depth': {}, 'with_quiescence': {}}
        for d in (2, 3, 4, 5):
            t = time.time()
            mv, score, st = best_move(pos, d, order='captures')
            row['depth'][str(d)] = dict(move=san(pos, mv), score=score,
                                        nodes=st.nodes,
                                        seconds=round(time.time() - t, 3))
            print(fen[:24], 'depth', d, row['depth'][str(d)], flush=True)
        for d in (3, 4, 5):
            t = time.time()
            mv, score, st = best_move(pos, d, order='captures', quiesce=True)
            row['with_quiescence'][str(d)] = dict(
                move=san(pos, mv), score=score, nodes=st.nodes,
                qnodes=st.qnodes, seconds=round(time.time() - t, 3))
            print(fen[:24], 'depth', d, 'quiescence',
                  row['with_quiescence'][str(d)], flush=True)
        out.append(row)
    (HERE / 'horizon.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print('wrote horizon.json')


if __name__ == '__main__':
    run()
