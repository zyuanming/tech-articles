#!/usr/bin/env python3
"""CC0-1.0. A finite teaching transition system, not a CSP interpreter."""
import argparse
import copy
import json
import platform
from collections import deque
from pathlib import Path


def send(peer, value):
    return ['send', peer, value]


def recv(peer, var):
    return ['recv', peer, var]


def scenarios():
    pipeline = {
        'P': [send('M', 2), send('M', 5)],
        'M': [recv('P', 'x'), ['add', 'x', 10], send('C', 'x'),
              recv('P', 'x'), ['add', 'x', 10], send('C', 'x')],
        'C': [recv('M', 'y'), ['record', 'y'],
              recv('M', 'y'), ['record', 'y']],
    }
    pair = {'A': [send('B', 2), recv('B', 'y')],
            'B': [send('A', 5), recv('A', 'x')]}
    fixed = copy.deepcopy(pair)
    fixed['B'].reverse()
    burst = {'A': [send('B', 2), send('B', 3), recv('B', 'y'), recv('B', 'y')],
             'B': [send('A', 5), send('A', 6), recv('A', 'x'), recv('A', 'x')]}
    arrival = {'P': [send('M', 2)],
               'M': [['prepare'], recv('P', 'x')]}
    return [('arrival', arrival, 0), ('pipeline', pipeline, 0),
            ('deadlock', pair, 0), ('reordered', fixed, 0),
            ('buffered', pair, 1), ('burst', burst, 1)]


def initial(program):
    channels = sorted({p + '>' + op[1] for p, ops in program.items()
                       for op in ops if op[0] == 'send'})
    return {'pc': {p: 0 for p in program},
            'local': {p: {} for p in program},
            'output': {p: [] for p in program},
            'queues': {c: [] for c in channels}}


def current(program, state, p):
    i = state['pc'][p]
    return program[p][i] if i < len(program[p]) else ['done']


def transitions(program, state, capacity):
    moves = []
    for p in program:
        op = current(program, state, p)
        k = op[0]
        if k in ('prepare', 'add', 'record'):
            s = copy.deepcopy(state)
            s['pc'][p] += 1
            if k == 'add':
                before = s['local'][p][op[1]]
                s['local'][p][op[1]] += op[2]
                detail = f'{p}: {before}+{op[2]}={s["local"][p][op[1]]}'
            elif k == 'record':
                value = s['local'][p][op[1]]
                s['output'][p].append(value)
                detail = f'{p}: record {value}'
            else:
                detail = f'{p}: prepare'
            moves.append(({'kind': k, 'actors': [p], 'label': detail}, s))
        elif k == 'send':
            q, expr = op[1:]
            value = state['local'][p][expr] if isinstance(expr, str) else expr
            channel = p + '>' + q
            if capacity == 0:
                peer = current(program, state, q)
                if peer[0] != 'recv' or peer[1] != p:
                    continue
                s = copy.deepcopy(state)
                s['pc'][p] += 1
                s['pc'][q] += 1
                s['local'][q][peer[2]] = value
                event = {'kind': 'rendezvous', 'actors': [p, q],
                         'value': value, 'label': f'{p}>{q}: {value}'}
                moves.append((event, s))
            elif len(state['queues'][channel]) < capacity:
                s = copy.deepcopy(state)
                s['queues'][channel].append(value)
                s['pc'][p] += 1
                event = {'kind': 'enqueue', 'actors': [p],
                         'value': value, 'label': f'{p}>{q}: put {value}'}
                moves.append((event, s))
        elif k == 'recv' and capacity > 0:
            q, var = op[1:]
            channel = q + '>' + p
            if state['queues'][channel]:
                s = copy.deepcopy(state)
                value = s['queues'][channel].pop(0)
                s['local'][p][var] = value
                s['pc'][p] += 1
                event = {'kind': 'dequeue', 'actors': [p],
                         'value': value, 'label': f'{q}>{p}: take {value}'}
                moves.append((event, s))
    return moves


def key(state):
    return json.dumps(state, sort_keys=True)


def explore(name, program, capacity):
    start = initial(program)
    states, edges, seen = [start], [], {key(start): 0}
    todo, parents = deque([0]), {}
    while todo:
        i = todo.popleft()
        for event, s in transitions(program, states[i], capacity):
            code = key(s)
            if code not in seen:
                seen[code] = len(states)
                states.append(s)
                parents[seen[code]] = (i, event)
                todo.append(seen[code])
            j = seen[code]
            edges.append({'from': i, 'to': j, **event})
            changed = [p for p in program if s['pc'][p] != states[i]['pc'][p]]
            assert set(changed) == set(event['actors'])
            assert len(changed) == (2 if event['kind'] == 'rendezvous' else 1)
            assert all(len(q) <= capacity for q in s['queues'].values())
    ends = [i for i, s in enumerate(states)
            if all(s['pc'][p] == len(program[p]) for p in program)]
    outgoing = {e['from'] for e in edges}
    dead = [i for i in range(len(states)) if i not in outgoing and i not in ends]
    target = dead[0] if dead else ends[0]
    trace = []
    while target != 0:
        prev, event = parents[target]
        trace.append({'from': prev, 'to': target, **event})
        target = prev
    trace.reverse()
    return {'name': name, 'capacity': capacity, 'program': program,
            'states': states, 'edges': edges, 'complete': ends, 'deadlocks': dead,
            'trace': trace, 'state_count': len(states), 'edge_count': len(edges)}


def run():
    runs = {n: explore(n, p, c) for n, p, c in scenarios()}
    p = runs['pipeline']
    assert not p['deadlocks']
    assert all(p['states'][i]['output']['C'] == [12, 15] for i in p['complete'])
    comm = [e['value'] for e in p['trace'] if e['kind'] == 'rendezvous']
    assert comm == [2, 12, 5, 15]
    assert runs['deadlock']['deadlocks'] == [0]
    assert not runs['reordered']['deadlocks']
    assert not runs['buffered']['deadlocks']
    assert runs['burst']['deadlocks'] and not runs['burst']['complete']
    d = runs['burst']['states'][runs['burst']['deadlocks'][0]]
    assert d['queues'] == {'A>B': [2], 'B>A': [5]}
    assert d['pc'] == {'A': 1, 'B': 1}
    return {'model': 'Finite Rendezvous Lab 1.0', 'python': platform.python_version(),
            'randomness': 'none: exhaustive finite graph', 'inputs': [2, 5],
            'increment': 10, 'runs': runs,
            'checks': ['all reachable states explored', 'paired PC advancement',
                       'capacity invariant', 'pipeline outputs on every complete state',
                       'deadlock and repair witnesses', 'burst full-queue witness']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path(__file__).with_name('results.json'))
    args = parser.parse_args()
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(result['model'], 'Python', result['python'])
    for n, r in result['runs'].items():
        print(n, r['state_count'], 'states;', r['edge_count'], 'edges;',
              len(r['deadlocks']), 'deadlock;', len(r['complete']), 'complete')
