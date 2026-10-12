"""A finite-action MPC teaching model; not a vehicle controller.

P is twice the position, so all arithmetic is exact integer arithmetic.
One beat: p' = p + v + u/2, v' = v + u. u is -1, 0 or 1.
0 <= p <= 8, 0 <= v <= 3. Horizon terminal set: v = 0.
Cost per predicted beat: 4*(p'-8)**2 + v'**2 + u**2.
SPDX-License-Identifier: MIT
"""
from itertools import product
from functools import lru_cache
import json

ACTIONS = (-1, 0, 1)

def step(state, u):
    P, v = state
    return P + 2*v + u, v + u

def allowed(state):
    P, v = state
    return 0 <= P <= 16 and 0 <= v <= 3

def stage(state, u):
    P, v = state
    return (P - 16)**2 + v*v + u*u

def rollout(state, actions, terminal_stop=True):
    if not allowed(state):
        return None
    states = [state]
    cost = 0
    for u in actions:
        if u not in ACTIONS:
            raise ValueError('unknown actuator setting')
        state = step(state, u)
        if not allowed(state):
            return None
        states.append(state)
        cost += stage(state, u)
    if terminal_stop and state[1] != 0:
        return None
    return {'cost': cost, 'actions': list(actions), 'states': states}

def candidates(state, horizon=3, terminal_stop=True):
    if horizon < 1:
        raise ValueError('positive horizon required')
    plans = []
    for actions in product(ACTIONS, repeat=horizon):
        plan = rollout(state, actions, terminal_stop)
        if plan is not None:
            plans.append(plan)
    return sorted(plans, key=lambda x: (x['cost'], x['actions']))

def solve(state, horizon=3, terminal_stop=True):
    plans = candidates(state, horizon, terminal_stop)
    return plans[0] if plans else None

def closed_loop(state, horizon=3, terminal_stop=True, max_beats=12):
    log = []
    for beat in range(max_beats):
        if state == (16, 0):
            return {'status': 'AT_TARGET_STOPPED', 'states_actions_plans': log,
                    'final_state': state}
        plan = solve(state, horizon, terminal_stop)
        if plan is None:
            return {'status': 'INFEASIBLE', 'states_actions_plans': log,
                    'final_state': state}
        u = plan['actions'][0]
        after = step(state, u)
        log.append({'beat': beat, 'state': state, 'plan': plan,
                    'applied': u, 'actual_after': after})
        state = after
    return {'status': 'BEAT_LIMIT', 'states_actions_plans': log,
            'final_state': state}

@lru_cache(None)
def independent_dp(P, v, remaining, terminal_stop):
    """Different search organization: Bellman recursion, no rollout/solve call."""
    if not (0 <= P <= 16 and 0 <= v <= 3):
        return None
    if remaining == 0:
        return (0, ()) if not terminal_stop or v == 0 else None
    choices = []
    for accel in (-1, 0, 1):
        next_v = v + accel
        next_P = P + v + next_v
        child = independent_dp(next_P, next_v, remaining-1, terminal_stop)
        if child is not None:
            cost = (16-next_P)**2 + next_v**2 + accel**2 + child[0]
            choices.append((cost, (accel,) + child[1]))
    return min(choices) if choices else None

def checks():
    comparisons = 0
    for P in range(17):
        for v in range(4):
            for N in range(1, 6):
                for terminal in (False, True):
                    a = solve((P,v), N, terminal)
                    b = independent_dp(P,v,N,terminal)
                    assert (None if a is None else (a['cost'],tuple(a['actions']))) == b
                    comparisons += 1
    shifted = 0
    for P in range(17):
        for v in range(4):
            for plan in candidates((P,v),3,True):
                next_state = tuple(plan['states'][1])
                shifted_actions = plan['actions'][1:] + [0]
                assert rollout(next_state, shifted_actions, True) is not None
                shifted += 1
    opening = candidates((4,2),3,True)  # physical position 2
    assert [(x['actions'],x['cost']) for x in opening] == [([0,-1,-1],112),([-1,0,-1],170),([-1,-1,0],212)]
    greedy = [(u, stage(step((4,2),u),u)) for u in ACTIONS]
    assert greedy == [(-1,83),(0,68),(1,59)]
    nominal = closed_loop((4,2))
    assert [x['applied'] for x in nominal['states_actions_plans']] == [0,0,-1,-1]
    from_rest = closed_loop((0,0))
    assert [x['applied'] for x in from_rest['states_actions_plans']] == [1,1,0,0,-1,-1]
    short = closed_loop((0,0),1,False)
    assert short['status']=='INFEASIBLE' and short['final_state']==(14,2)
    short_two = closed_loop((0,0),2,False)
    assert short_two['status']=='INFEASIBLE' and short_two['final_state']==(9,3)
    stalled = closed_loop((0,0),1,True,4)
    assert stalled['final_state']==(0,0) and all(x['applied']==0 for x in stalled['states_actions_plans'])
    nominal_next = solve((8,2))
    measured_next = solve((10,2))
    assert nominal_next['actions']==[0,-1,-1] and nominal_next['cost']==24
    assert measured_next['actions']==[-1,0,-1] and measured_next['cost']==14
    assert rollout((10,2),nominal_next['actions']) is None
    # Exact stopping travel in twice-position units is v**2.
    for initial_v in range(7):
        P,v=0,initial_v
        for _ in range(initial_v):
            P,v=step((P,v),-1)
        assert (P,v)==(initial_v**2,0)
    return {'status':'AUTHOR_MODEL_CHECKS_PASS',
            'enumeration_vs_independent_dp_cases':comparisons,
            'all_three_step_feasible_tail_shift_cases':shifted,
            'exact_stop_distance_cases':7,
            'opening':opening,'greedy_one_step':greedy,
            'nominal_from_position_2':nominal,'nominal_from_rest':from_rest,
            'horizon1_without_terminal':short,'horizon2_without_terminal':short_two,
            'horizon1_with_terminal':stalled,
            'nominal_next_plan':nominal_next,'measured_next_plan':measured_next,
            'scope':'Exact finite-action toy model. No hardware, solver benchmark or real-vehicle safety claim.'}

if __name__ == '__main__':
    print(json.dumps(checks(),ensure_ascii=False,indent=2))
