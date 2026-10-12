"""Original exact-arithmetic teaching model, CC BY 4.0.
A frictionless cart, constant acceleration during each 1 s interval.
No hardware, collision, controller stability, or energy-in-joules claim.
Run: python reachability_lab.py [--output results.json]
"""
from fractions import Fraction as F
from itertools import product
import argparse
import json


def step(state, acceleration, dt=F(1)):
    p, v = map(F, state)
    u, dt = F(acceleration), F(dt)
    return (p + v * dt + u * dt * dt / 2, v + u * dt)


def simulate(inputs, initial=(0, 0)):
    states = [tuple(map(F, initial))]
    for u in inputs:
        states.append(step(states[-1], u))
    return states


def two_step_inputs(target, initial=(0, 0)):
    p, v = map(F, target)
    p0, v0 = map(F, initial)
    # Remove uncontrolled drift for two seconds first.
    dp, dv = p - p0 - 2 * v0, v - v0
    return (dp - dv / 2, 3 * dv / 2 - dp)


def within_two_step_bound(target, limit=F(1)):
    return all(abs(u) <= limit for u in two_step_inputs(target))


def mul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def rank(a):
    a = [list(map(F, r)) for r in a]
    row = 0
    for col in range(len(a[0])):
        pivot = next((r for r in range(row, len(a)) if a[r][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        q = a[row][col]
        a[row] = [x / q for x in a[row]]
        for r in range(len(a)):
            if r != row:
                q = a[r][col]
                a[r] = [x - q * y for x, y in zip(a[r], a[row])]
        row += 1
        if row == len(a):
            break
    return row


def controllability(a, b):
    """[B, AB, ..., A^(n-1)B], for constant discrete-time A and B."""
    block = b
    out = [[] for _ in a]
    for _ in a:
        for row, vals in zip(out, block):
            row.extend(vals)
        block = mul(a, block)
    return out


def least_squared_input(n, target):
    """Minimize sum(u_k**2) for this cart, fixed n >= 2, from rest.
    This is a command penalty; it is not automatically physical energy.
    """
    if n < 2:
        raise ValueError('n must be at least two')
    p, v = map(F, target)
    weights = [F(2 * (n - k) - 1, 2) for k in range(n)]
    a, b, c = sum(w * w for w in weights), sum(weights), F(n)
    det = a * c - b * b
    alpha, beta = (c * p - b * v) / det, (a * v - b * p) / det
    return [alpha * w + beta for w in weights]


def squared_input(us):
    return sum(F(u) ** 2 for u in us)


def checks():
    a = [[1, 1], [0, 1]]
    b = [[F(1, 2)], [1]]
    c = controllability(a, b)
    assert c == [[F(1, 2), F(3, 2)], [1, 1]] and rank(c) == 2
    shared_a = [[1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]]
    shared_b = [[F(1, 2)], [1], [F(1, 2)], [1]]
    assert rank(controllability(shared_a, shared_b)) == 2
    targets = 0
    for p, v in product(range(-40, 41), repeat=2):
        target = (F(p, 4), F(v, 4))
        assert simulate(two_step_inputs(target))[-1] == target
        targets += 1
    drift_cases = 0
    for p0, v0, p, v in product(range(-3, 4), repeat=4):
        initial, target = (p0, v0), (p, v)
        assert simulate(two_step_inputs(target, initial), initial)[-1] == target
        drift_cases += 1
    sequences = 0
    for n in range(9):
        for us in product((-1, 0, 1), repeat=n):
            result = simulate(us)[-1]
            # Independent closed-form endpoint, not step-by-step integration.
            expected = (sum(F(2*(n-k)-1, 2)*u for k,u in enumerate(us)), sum(us))
            assert result == expected
            # Two identical carts with the same command remain identical.
            state = [[F(0)], [F(0)], [F(0)], [F(0)]]
            for u in us:
                drift = mul(shared_a, state)
                state = [[r[0] + bi[0]*u] for r,bi in zip(drift,shared_b)]
            assert tuple(r[0] for r in state) == result + result
            sequences += 1
    bound_grid = 0
    for u0, u1 in product(range(-10, 11), repeat=2):
        us = (F(u0, 10), F(u1, 10))
        target = simulate(us)[-1]
        assert within_two_step_bound(target)
        assert two_step_inputs(target) == us
        bound_grid += 1
    extremes = [simulate(us)[-1] for us in product((-1, 1), repeat=2)]
    assert extremes == [(F(-2),F(-2)), (F(-1),F(0)), (F(1),F(0)), (F(2),F(2))]
    four = (F(3,4), F(3,4), F(-3,4), F(-3,4))
    assert simulate(four)[-1] == (3,0) and not within_two_step_bound((3,0))
    # Vertices with v4=0: this restricted enumeration checks the shown bang-bang case.
    resting_vertices = [simulate(us)[-1][0] for us in product((-1,1), repeat=4) if sum(us)==0]
    assert max(resting_vertices) == 4
    least_cases = 0
    for n in range(2, 11):
        for p,v in product(range(-5,6),repeat=2):
            us=least_squared_input(n,(p,v));assert simulate(us)[-1] == (p,v)
            # Null direction (1,-2,1,0,...) has zero endpoint; orthogonality
            # verifies cost increases by its squared length for +/- perturbations.
            if n>=3:
                for t in (-2,-1,1,2):
                    perturbed=[u+t*q for u,q in zip(us,[1,-2,1]+[0]*(n-3))]
                    assert simulate(perturbed)[-1] == (p,v)
                    assert squared_input(perturbed) == squared_input(us)+6*t*t
            least_cases += 1
    gentle = least_squared_input(4,(1,0))
    assert gentle == [F(3,10),F(1,10),F(-1,10),F(-3,10)]
    assert squared_input(gentle) == F(1,5)
    return {
      'model':'exact piecewise-constant acceleration, dt=1 s, no friction; rational arithmetic',
      'target_grid_cases':targets,'nonzero_initial_cases':drift_cases,
      'ternary_sequences_lengths_0_to_8':sequences,'bounded_input_grid_cases':bound_grid,
      'least_squared_fixed_horizon_cases':least_cases,
      'cart_controllability_rank':rank(c),'shared_two_cart_rank_of_four':2,
      'two_second_stop':{'inputs':[1,-1],'states':simulate([1,-1])},
      'three_metre_four_second_stop':{'inputs':four,'states':simulate(four)},
      'four_second_gentle_stop':{'inputs':gentle,'states':simulate(gentle),'squared_command':squared_input(gentle)},
      'two_step_box_corners':extremes,
      'scope':'Exact model checks only; not actuator tests, stability proof, or general constrained-control solver.'}


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output');args=parser.parse_args()
    result=json.dumps(checks(),ensure_ascii=False,indent=2,default=str)+'\n'
    if args.output:
        with open(args.output,'w') as f:f.write(result)
    print(result,end='')
