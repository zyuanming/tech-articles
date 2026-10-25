"""Recompute finite examples, grammar sets, and independent cross-checks. CC0-1.0."""
import itertools
import json
import platform
import re
from pathlib import Path
from parser import parse

HERE = Path(__file__).resolve().parent
G = {
 'S': [['E', 'EOF']],
 'E': [['T', 'R']],
 'R': [['+', 'T', 'R'], ['-', 'T', 'R'], []],
 'T': [['F', 'Q']],
 'Q': [['*', 'F', 'Q'], []],
 'F': [['NUM'], ['(', 'E', ')']]
}


def grammar_sets():
    first = {a: set() for a in G}
    def seq(rhs):
        result = set()
        for x in rhs:
            s = first[x] if x in G else {x}
            result |= s - {'epsilon'}
            if 'epsilon' not in s:
                return result
        return result | {'epsilon'}
    changed = True
    while changed:
        changed = False
        for a, rules in G.items():
            old = first[a].copy()
            for rhs in rules:
                first[a] |= seq(rhs)
            changed |= old != first[a]
    follow = {a: set() for a in G}
    follow['S'] = {'END'}
    changed = True
    while changed:
        changed = False
        for a, rules in G.items():
            for rhs in rules:
                for i, x in enumerate(rhs):
                    if x in G:
                        old = follow[x].copy()
                        tail = seq(rhs[i+1:])
                        follow[x] |= tail - {'epsilon'}
                        if 'epsilon' in tail:
                            follow[x] |= follow[a]
                        changed |= old != follow[x]
    select = {}
    for a, rules in G.items():
        used = set(); select[a] = []
        for rhs in rules:
            s = seq(rhs)
            pick = s - {'epsilon'}
            if 'epsilon' in s:
                pick |= follow[a]
            assert not used & pick, (a, rhs)
            used |= pick
            select[a].append(dict(rhs=rhs, look=sorted(pick)))
    return dict(grammar=G, first={k: sorted(v) for k,v in first.items()},
                follow={k: sorted(v) for k,v in follow.items()}, select=select)


def oracle(s):
    # Independent regex lexer and operator-stack recognizer.
    values, ops = [], []
    need = True
    prec = {'+': 1, '-': 1, '*': 2}
    def reduce():
        op = ops.pop(); b = values.pop(); a = values.pop()
        values.append(a+b if op == '+' else a-b if op == '-' else a*b)
    for c in re.findall(r'1+|[^1]', s):
        if c[0] == '1':
            if not need: return None
            values.append(int(c)); need = False
        elif c == '(':
            if not need: return None
            ops.append(c)
        elif c == ')':
            if need or '(' not in ops: return None
            while ops[-1] != '(': reduce()
            ops.pop(); need = False
        else:
            if need: return None
            while ops and ops[-1] != '(' and prec[ops[-1]] >= prec[c]: reduce()
            ops.append(c); need = True
    if need or '(' in ops: return None
    while ops: reduce()
    return values[0]


def left_recursion_probe():
    events = []
    def bad_expr(depth, index):
        events.append(dict(depth=depth, index=index))
        if depth < 3:
            bad_expr(depth+1, index)
    bad_expr(0, 0)
    return events


def main():
    cases = ['12-3*2-1', '12-(3*2-1)', '(12-3)*2-1', '12-3**2', '12 3', '(12-3', '12@3', '', '-2', ' 12 - 3 * 2 - 1 ', '1+2*3', '2*3*4', '12-6-1', '12-(6-1)', '12+3*2-1']
    runs = {s: parse(s) for s in cases}
    assert [runs[s]['value'] for s in cases[:3]] == [5, 7, 17]
    assert runs['12-3**2']['error']['pos'] == 5
    tested = accepted = 0
    for n in range(6):
        for t in itertools.product('1+-*()', repeat=n):
            s = ''.join(t); r = parse(s); v = oracle(s)
            assert r['ok'] == (v is not None), (s,r,v)
            if r['ok']:
                assert r['value'] == v
                accepted += 1
            tested += 1
    limits = {s: parse(s)['ok'] for s in ['('*32+'1'+')'*32, '('*33+'1'+')'*33, '1'*9, '1'*10, ' '*256, ' '*257]}
    assert list(limits.values()) == [True, False, True, False, False, False]
    result = dict(python=platform.python_version(), runs=runs, sets=grammar_sets(),
                  checks=dict(exhaustive_count=tested, valid_count=accepted, alphabet='1+-*()', max_length=5, limits=limits),
                  left_recursion=left_recursion_probe())
    (HERE/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['checks'],ensure_ascii=False))

if __name__ == '__main__': main()
