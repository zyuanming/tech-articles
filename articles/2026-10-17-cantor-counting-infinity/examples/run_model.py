#!/usr/bin/env python3
"""Counting infinity: pairings, the diagonal argument, and the hotel.

Standard library only. Writes results.json next to this file. MIT.
"""
from __future__ import annotations
import json
from fractions import Fraction
from pathlib import Path

from infinity import (naturals_evens, naturals_integers, integers_naturals,
                      cantor_pair, naturals_pairs, rationals_enumeration,
                      diagonal_rounds, power_set_sizes, binary_strings,
                      pad_decimal)

HERE = Path(__file__).resolve().parent
N = 1000


def check_pairing(name, f, inverse=None, limit=N):
    """Verify a claimed pairing on a finite range: no collisions, and (if an
    inverse is given) the round trip comes back to where it started."""
    images = [f(i) for i in range(limit)]
    row = dict(name=name, checked=limit, distinct=len(set(images)),
               injective=len(set(images)) == limit,
               first_ten=images[:10])
    if inverse is not None:
        row['round_trip_ok'] = all(inverse(f(i)) == i for i in range(limit))
    return row


def hilbert_hotel(rooms=12):
    """Three nights at the hotel with infinitely many rooms."""
    occupied = list(range(1, rooms + 1))

    shifted = [r + 1 for r in occupied]
    new_guest_room = 1

    doubled = [r * 2 for r in occupied]
    odd_rooms_free = [r for r in range(1, 2 * rooms + 1, 2)]

    return dict(
        rooms_shown=rooms,
        night1_before=occupied,
        night1_after=shifted,
        night1_new_guest=1,
        night1_everyone_still_has_a_room=len(set(shifted)) == rooms,
        night2_before=occupied,
        night2_after=doubled,
        night2_free_rooms_for_new_guests=odd_rooms_free,
        night2_everyone_still_has_a_room=len(set(doubled)) == rooms,
        note='这里只显示前若干间房；旅店的「无穷」是这些规律的极限')


def subsets_of(items):
    out = [[]]
    for x in items:
        out += [s + [x] for s in out]
    return out


def main():
    out = {}

    out['pairings'] = [
        check_pairing('自然数 ↔ 偶数：n 对应 2n', naturals_evens),
        check_pairing('自然数 ↔ 整数：之字形', naturals_integers,
                      inverse=integers_naturals),
    ]

    # the grid walk: every (a, b) pair of naturals gets its own number
    grid = [cantor_pair(a, b) for a in range(40) for b in range(40)]
    out['pairs'] = dict(
        name='自然数 ↔ 自然数对',
        checked=len(grid), distinct=len(set(grid)),
        injective=len(set(grid)) == len(grid),
        round_trip_ok=all(naturals_pairs(n) ==
                          (a, b) for a in range(40) for b in range(40)
                          for n in [cantor_pair(a, b)]),
        note='把 (分子, 分母) 两两配成一个编号，就得到有理数的枚举')

    rats = rationals_enumeration(60)
    out['rationals'] = dict(
        checked=len(rats),
        first_twelve=[dict(index=i, value=str(f)) for i, f in rats[:12]],
        all_distinct=len({f for _, f in rats}) == len(rats),
        note='按对角线走 (分子, 分母) 网格，跳过可约分的，就一个不漏地数到所有正有理数')

    # the diagonal
    start = ['0.123456789012', '0.234567890123', '0.345678901234',
             '0.456789012345', '0.567890123456']
    out['diagonal'] = diagonal_rounds(start, rounds=3, width=14)

    out['power_set'] = power_set_sizes(10)

    # binary strings vs subsets: same thing, counted two ways
    checks = []
    for n in range(0, 8):
        strings = binary_strings(n)
        subsets = subsets_of(list(range(n)))
        checks.append(dict(n=n, binary_strings=len(strings),
                           subsets=len(subsets),
                           agree=len(strings) == len(subsets)))
    out['strings_vs_subsets'] = checks

    out['hotel'] = hilbert_hotel()

    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(out, ensure_ascii=False, indent=2)[:900])


if __name__ == '__main__':
    main()
