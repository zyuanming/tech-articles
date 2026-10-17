#!/usr/bin/env python3
"""Monty Hall: exact enumeration, closed form, conditioning, simulation.

Standard library only. Writes results.json next to this file. MIT.
"""
from __future__ import annotations
import json
from fractions import Fraction
from itertools import product
from pathlib import Path

from monty import (exact_three_doors, exact_three_doors_ignorant,
                   closed_form, simulate)

HERE = Path(__file__).resolve().parent


def f(x):
    return str(x) if isinstance(x, Fraction) else x


def conditional_by_opened_door(policy, pick=0, n=3):
    """Exact P(win) given which door the host opened, with the pick fixed.

    Weighting matters: with an unbiased host, (car, pick, opened) triples are
    NOT equally likely, because when the player has already picked the car the
    host has two doors to choose from and each gets half the weight.
    """
    joint = {}
    for car in range(n):
        avail = [d for d in range(n) if d != pick and d != car]
        weights = policy(car, pick, avail)
        for opened, w in weights.items():
            joint[(car, opened)] = joint.get((car, opened), Fraction(0)) + \
                Fraction(1, n) * w
    rows = []
    for opened in range(n):
        if opened == pick:
            continue
        total = sum(v for (c, o), v in joint.items() if o == opened)
        if total == 0:
            continue
        stay = sum(v for (c, o), v in joint.items()
                   if o == opened and c == pick)
        rows.append(dict(opened=opened + 1,
                         probability_of_this_opening=f(total),
                         stay_win=f(stay / total),
                         switch_win=f((total - stay) / total)))
    return rows


def random_goat(car, pick, avail):
    return {d: Fraction(1, len(avail)) for d in avail}


def lowest_goat(car, pick, avail):
    return {min(avail): Fraction(1)}


def main():
    out = {}
    stay, switch, total, rows = exact_three_doors()
    out['exact_three_doors'] = dict(
        cases=total, stay_wins=stay, switch_wins=switch,
        stay_rate=f(Fraction(stay, total)), switch_rate=f(Fraction(switch, total)),
        note='主持人知道车在哪，且必须开一只羊')
    out['exact_three_doors_cases'] = rows

    s2, w2, t2 = exact_three_doors_ignorant()
    out['exact_ignorant_host'] = dict(
        cases=t2, stay_wins=s2, switch_wins=w2,
        stay_rate=f(Fraction(s2, t2)), switch_rate=f(Fraction(w2, t2)),
        note='主持人不知道车在哪，随机开一扇，我们只看他没开到车的情形')

    out['closed_form'] = [
        dict(doors=n, host_opens=k,
            stay=f(closed_form(n, k)[0]), switch=f(closed_form(n, k)[1]))
        for n, k in ((3, 1), (4, 2), (10, 8), (100, 98))
    ]

    sims = []
    for label, n, k, knows, trials, seed in (
            ('三扇门，知情主持人', 3, 1, True, 200000, 11),
            ('三扇门，不知情主持人（只看他碰巧没开到车）', 3, 1, False, 200000, 11),
            ('一百扇门，开掉 98 扇，知情', 100, 98, True, 200000, 11),
            ('十扇门，开掉 8 扇，知情', 10, 8, True, 200000, 11)):
        s, w, disc = simulate(n, k, knows, trials, seed)
        kept = trials - disc
        sims.append(dict(label=label, doors=n, host_opens=k, trials=trials,
                         discarded=disc, kept=kept, stay_wins=s, switch_wins=w,
                         stay_rate=f(Fraction(s, kept)),
                         switch_rate=f(Fraction(w, kept)),
                         stay_rate_decimal=round(s / kept, 4),
                         switch_rate_decimal=round(w / kept, 4),
                         seed=seed))
    out['simulations'] = sims

    out['conditioning'] = dict(
        pick=1,
        random_host=conditional_by_opened_door(random_goat),
        lowest_number_host=conditional_by_opened_door(lowest_goat),
        note='玩家的选择固定为 1 号门；两种主持人策略下总体胜率都是 1/3 与 2/3，'
             '但按「他开了哪扇门」分别看就不同了')

    # running estimate, so the article can show the number settling down
    import random
    rng = random.Random(20261017)
    conv = []
    switch_wins = 0
    for i in range(1, 200001):
        car, pick = rng.randrange(3), rng.randrange(3)
        can = [d for d in range(3) if d != pick and d != car]
        opened = rng.choice(can)
        other = [d for d in range(3) if d != pick and d != opened][0]
        switch_wins += (other == car)
        if i in (10, 100, 1000, 10000, 100000, 200000):
            conv.append(dict(trials=i, switch_wins=switch_wins,
                             switch_rate=round(switch_wins / i, 4)))
    out['convergence'] = conv

    out['bayes'] = dict(
        prior_car_behind_pick='1/3',
        prior_car_behind_other='2/3',
        likelihood_host_opens_door3_if_car_behind_pick='1/2',
        likelihood_host_opens_door3_if_car_behind_other='1',
        posterior_car_behind_pick='1/3',
        posterior_car_behind_other='2/3',
        note='以「主持人随机开一只羊」为前提；分子的 1/2 是他有两只羊可选，'
             '另一支的 1 是他没得选')

    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(out, ensure_ascii=False, indent=2)[:1200])


if __name__ == '__main__':
    main()
