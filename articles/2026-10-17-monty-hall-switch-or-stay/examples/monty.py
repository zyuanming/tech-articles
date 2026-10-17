"""Monty Hall: exact enumeration, closed form, and simulation. Standard library only. MIT.

Three separate ways to get the same answer, so the article can show that they
agree instead of asking the reader to trust one of them.
"""
from __future__ import annotations
import random
from fractions import Fraction
from itertools import product


def exact_three_doors():
    """Enumerate all 3 x 3 cases with a host who knows where the car is.

    Returns (stay_wins, switch_wins, total) as exact counts.
    """
    stay = switch = 0
    rows = []
    for car, pick in product(range(3), repeat=2):
        # the host must open a door that is neither the player's nor the car's
        can_open = [d for d in range(3) if d != pick and d != car]
        opened = can_open[0]                     # any choice gives the same counts
        other = [d for d in range(3) if d != pick and d != opened][0]
        s = (pick == car)
        w = (other == car)
        stay += s
        switch += w
        rows.append(dict(car=car, pick=pick, host_opens=opened,
                         switch_to=other, stay_wins=s, switch_wins=w))
    return stay, switch, len(rows), rows


def exact_three_doors_ignorant():
    """Same, but the host opens a door at random and it happens to be a goat.

    We only count the trials that survive: the host must not reveal the car.
    """
    stay = switch = total = 0
    for car, pick in product(range(3), repeat=2):
        for opened in range(3):
            if opened == pick or opened == car:
                continue                     # not a legal reveal in this variant
            other = [d for d in range(3) if d != pick and d != opened][0]
            total += 1
            stay += (pick == car)
            switch += (other == car)
    return stay, switch, total


def closed_form(n_doors, n_open):
    """With n doors, the host opens n_open goat doors, then offers the switch.

    P(win by staying)  = 1/n
    P(win by switching to one specific remaining door)
                       = (n-1) / (n * (n-1-n_open))
    """
    stay = Fraction(1, n_doors)
    remaining = n_doors - 1 - n_open
    if remaining <= 0:
        return stay, None
    switch = Fraction(n_doors - 1, n_doors * remaining)
    return stay, switch


def simulate(n_doors, n_open, host_knows, trials, seed):
    """Monte Carlo. Returns counts for stay and switch, plus discarded trials."""
    rng = random.Random(seed)
    stay = switch = discarded = 0
    for _ in range(trials):
        car = rng.randrange(n_doors)
        pick = rng.randrange(n_doors)
        closed = [d for d in range(n_doors) if d != pick and d != car]
        if host_knows:
            opened = rng.sample(closed, n_open)
        else:
            pool = [d for d in range(n_doors) if d != pick]
            opened = rng.sample(pool, n_open)
            if car in opened:
                discarded += 1          # the host blundered and showed the car
                continue
        remaining = [d for d in range(n_doors) if d != pick and d not in opened]
        stay += (pick == car)
        switch += (car in remaining)
    return stay, switch, discarded
