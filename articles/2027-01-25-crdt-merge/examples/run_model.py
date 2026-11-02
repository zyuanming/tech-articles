"""跑出 crdt 一文的全部数字，写到 results.json。

    python3 run_model.py

只用标准库，约 8 秒。
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import crdt as C

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results.json'

TYPES = [
    ('lww', 'LWW 寄存器', lambda node: C.LWW(node)),
    ('gcounter', 'G-Counter', lambda node: C.GCounter(node)),
    ('pncounter', 'PN-Counter', lambda node: C.PNCounter(node)),
    ('twopset', '2P-Set', lambda node: C.TwoPSet()),
    ('orset', 'OR-Set', lambda node: C.ORSet(node)),
    ('gset', 'G-Set', lambda node: C.GSet()),
    ('late', '后到覆盖', lambda node: C.LateValue(node)),
    ('sum', '合并相加', lambda node: C.SumCounter(node)),
]


def fresh(kind, node='A'):
    for k, _, ctor in TYPES:
        if k == kind:
            return ctor(node)
    raise KeyError(kind)


def build_three(kind, seed=11):
    """三台机器各自做一串操作，返回三份状态（互不通信）。"""
    rng = random.Random(seed)
    reps, states = {}, []
    if kind == 'lww':
        a = C.LWW('A'); a.write('草稿 v1')
        b = C.LWW('B'); b.write('草稿 v2')
        c = C.LWW('C'); c.write('草稿 v3')
        return [a.state(), b.state(), c.state()]
    if kind == 'gcounter':
        a = C.GCounter('A'); [a.add() for _ in range(7)]
        b = C.GCounter('B'); [b.add() for _ in range(5)]
        c = C.GCounter('C'); [c.add() for _ in range(2)]
        return [a.state(), b.state(), c.state()]
    if kind == 'pncounter':
        a = C.PNCounter('A'); [a.add() for _ in range(7)]; a.sub()
        b = C.PNCounter('B'); [b.add() for _ in range(5)]
        c = C.PNCounter('C'); [c.add() for _ in range(2)]; c.sub(); c.sub()
        return [a.state(), b.state(), c.state()]
    if kind == 'twopset':
        a = C.TwoPSet(); a.add('apple'); a.add('pear')
        b = C.TwoPSet(); b.add('pear'); b.remove('apple')
        c = C.TwoPSet(); c.add('plum')
        return [a.state(), b.state(), c.state()]
    if kind == 'orset':
        a = C.ORSet('A'); a.add('apple'); a.add('pear')
        b = C.ORSet('B'); b.add('pear'); b.remove('apple')
        c = C.ORSet('C'); c.add('plum')
        return [a.state(), b.state(), c.state()]
    if kind == 'gset':
        a = C.GSet(); a.add('apple'); a.add('pear')
        b = C.GSet(); b.add('pear'); b.add('plum')
        c = C.GSet(); c.add('plum'); c.add('fig')
        return [a.state(), b.state(), c.state()]
    if kind == 'late':
        a = C.LateValue('A', 7)
        b = C.LateValue('B', 5)
        c = C.LateValue('C', 2)
        return [a.state(), b.state(), c.state()]
    if kind == 'sum':
        a = C.SumCounter('A', 7)
        b = C.SumCounter('B', 5)
        c = C.SumCounter('C', 2)
        return [a.state(), b.state(), c.state()]
    raise KeyError(kind)


# ---------------------------------------------------------------- 1. 合并顺序

def merge_shuffled(kind, states, trials=200, seed=3):
    """把同样的三份状态按随机顺序合并，看能得出几种不同的最终结果。"""
    rng = random.Random(seed)
    finals = {}
    for _ in range(trials):
        pool = [json.loads(json.dumps(s)) for s in states]
        rng.shuffle(pool)
        rep = fresh(kind)
        for st in pool:
            rep.merge(st)
        finals[C.fp(rep.state())] = finals.get(C.fp(rep.state()), 0) + 1
    return {'distinct': len(finals), 'top': max(finals.values()),
            'fingerprints': sorted(finals)[:6]}


# ---------------------------------------------------------------- 2. 幂等

def idempotence(kind, states, repeats=(1, 2, 5)):
    out = []
    data = {"v": None, "n": 0}
    for r in repeats:
        rep = fresh(kind)
        for st in states:
            for _ in range(r):
                rep.merge(json.loads(json.dumps(st)))
        st = rep.state()
        out.append({'repeats': r, 'fingerprint': C.fp(st),
                    'value': getattr(rep, 'value', lambda: None)()})
    return out


# ---------------------------------------------------------------- 3. 八卦收敛

def gossip(kind, op_count=300, seed=5, limit=40):
    """三台机器随机两两同步，直到三份状态完全一样；返回用了几轮。"""
    rng = random.Random(seed)
    reps = {n: fresh(kind, n) for n in 'ABC'}
    truth = 0
    for i in range(op_count):
        n = 'ABC'[rng.randrange(3)]
        if kind in ('gcounter', 'pncounter', 'sum'):
            reps[n].add()
            truth += 1
        elif kind == 'late':
            truth += 1
            reps[n].write(truth)
        elif kind in ('twopset', 'orset', 'gset'):
            reps[n].add('item-%d' % i)
        elif kind == 'lww':
            truth += 1
            reps[n].write(truth)
    for r in range(1, limit + 1):
        a, b = rng.sample('ABC', 2)
        reps[a].merge(json.loads(json.dumps(reps[b].state())))
        if len({C.fp(reps[n].state()) for n in 'ABC'}) == 1:
            rep = reps['A']
            val = rep.value() if hasattr(rep, 'value') else rep.load()
            want = truth if kind in ('lww', 'late', 'gcounter',
                                     'pncounter') else op_count
            return {'rounds': r, 'value': val, 'truth': want,
                    'ops': op_count}
    return {'rounds': None, 'ops': op_count}


# ---------------------------------------------------------------- 3b. 副本数与轮数

def gossip_scale(sizes=(3, 4, 6, 8, 12, 16, 24, 32), op_count=100, seeds=4):
    """每轮里，每台机器都从一个随机同伴拉一份全量状态。

    返回：副本数 → 三份状态全部相同所需的轮数（4 个种子取平均）。
    """
    out = []
    for n in sizes:
        got = []
        for sd in range(seeds):
            rng = random.Random(700 + 31 * sd + n)
            names = [chr(ord('A') + i) if i < 26 else 'N%d' % i
                     for i in range(n)]
            reps = {nm: C.GCounter(nm) for nm in names}
            for _ in range(op_count):
                reps[names[rng.randrange(n)]].add()
            rounds = None
            for r in range(1, 400):
                pulls = {nm: names[rng.randrange(n)] for nm in names}
                for nm, src in pulls.items():
                    reps[nm].merge(json.loads(json.dumps(reps[src].state())))
                if len({C.fp(reps[nm].state()) for nm in names}) == 1:
                    rounds = r
                    break
            got.append(rounds)
        out.append({'nodes': n, 'rounds': round(sum(got) / len(got), 2),
                    'log2': round(__import__('math').log2(n), 2)})
    return out


# ---------------------------------------------------------------- 4. 分区愈合

def partition(kind, per_side=100):
    """{A,B} 和 {C} 断开，各自改各自的，然后合起来。"""
    a, b = fresh(kind, 'A'), fresh(kind, 'B')
    c = fresh(kind, 'C')

    def bump(r, i):
        if kind in ('gcounter', 'pncounter', 'sum'):
            r.add()
        else:                        # 后到覆盖：每边各自从自己的值往上加
            r.write((r.value() or 0) + 1)

    for i in range(per_side):
        bump(a, i)
        bump(b, i)
        bump(c, i)
    a.merge(json.loads(json.dumps(b.state())))
    a.merge(json.loads(json.dumps(c.state())))
    return {'value': a.value(), 'truth': per_side * 3}


# ---------------------------------------------------------------- 5. 加与删同时发生

def add_wins():
    """A 在加 apple，B 同时在删 apple，然后互相同步。"""
    a = C.ORSet('A')
    a.add('apple')
    b = C.ORSet('B')
    b.add('apple')
    b.remove('apple')
    a.merge(json.loads(json.dumps(b.state())))
    b.merge(json.loads(json.dumps(a.state())))

    p = C.TwoPSet()
    p.add('apple')
    q = C.TwoPSet()
    q.add('apple')
    q.remove('apple')
    p.merge(json.loads(json.dumps(q.state())))
    q.merge(json.loads(json.dumps(p.state())))
    return {'orset_has': a.has('apple'), 'twopset_has': p.has('apple'),
            'orset_tags': len(a.tags.get('apple', ())),
            'orset_dead': len(a.dead)}


# ---------------------------------------------------------------- 6. 状态大小

def growth(steps=(10, 50, 100, 200, 500, 1000, 2000)):
    gset, twop, ors = C.GSet(), C.TwoPSet(), C.ORSet('A')
    out = []
    done = 0
    for n in steps:
        while done < n:
            done += 1
            elem = 'item-%d' % done
            gset.add(elem) if done % 2 else None
            twop.add(elem)
            if done % 3 == 0:
                twop.remove(elem)
            ors.add(elem)
            if done % 4 == 0:
                ors.remove(elem)
        out.append({'ops': n,
                    'gset_bytes': C.size_of(gset.state()),
                    'twopset_bytes': C.size_of(twop.state()),
                    'orset_bytes': C.size_of(ors.state()),
                    'orset_tags': sum(len(v) for v in ors.tags.values()),
                    'orset_dead': len(ors.dead)})
    return out


# ---------------------------------------------------------------- 7. 时间戳撞车

def tiebreak(trials=200, seed=9):
    """两条写操作时间戳一样，谁赢？"""
    rng = random.Random(seed)
    wins = {'higher': 0, 'lower': 0}
    examples = []
    for _ in range(trials):
        n1, n2 = rng.sample(['A', 'B', 'C', 'D'], 2)
        a = C.LWW(n1); a.st['ts'] = 5; a.st['val'] = '来自 ' + n1
        b = C.LWW(n2); b.st['ts'] = 5; b.st['val'] = '来自 ' + n2
        a.merge(json.loads(json.dumps(b.state())))
        win = a.value()[-1]
        wins['higher' if win == max(n1, n2) else 'lower'] += 1
        if len(examples) < 3:
            examples.append({'pair': [n1, n2], 'winner': win})
    return {'trials': trials, **wins, 'examples': examples}


# ---------------------------------------------------------------- 8. 读改写

def read_modify_write():
    """三台机器同时把计数从 0 改成 1——这是最典型的丢更新。"""
    reps = [C.LWW('A'), C.LWW('B'), C.LWW('C')]
    for i, r in enumerate(reps):
        seen = 0 if i == 0 else 0
        r.write(seen + 1)
    for r in reps[1:]:
        reps[0].merge(json.loads(json.dumps(r.state())))
    return {'final': reps[0].value(), 'intended': 3,
            'concurrent_writes': len(reps)}


def main():
    out = {'setup': {'keys_note': '三台机器 A/B/C，互不通信', 'seed': 3}}

    # 1. 合并顺序
    order = {}
    for kind, label, _ in TYPES:
        states = build_three(kind)
        r = merge_shuffled(kind, states)
        order[kind] = {'label': label, **r,
                       'states': [C.fp(s) for s in states]}
    out['merge_order'] = order

    # 2. 幂等
    idem = {}
    for kind, label, _ in TYPES:
        states = build_three(kind)
        idem[kind] = {'label': label, 'runs': idempotence(kind, states)}
    out['idempotence'] = idem

    # 3. 八卦收敛
    goss = {}
    for kind, label, _ in TYPES:
        goss[kind] = {'label': label, **gossip(kind)}
    out['gossip'] = goss

    # 3b. 副本数与收敛轮数
    out['gossip_scale'] = gossip_scale()

    # 4. 分区愈合
    part = {}
    for kind in ('gcounter', 'pncounter', 'late', 'sum'):
        part[kind] = partition(kind)
    out['partition'] = part

    # 5. 加与删同时发生
    out['add_wins'] = add_wins()

    # 6. 状态大小
    out['growth'] = growth()

    # 7. 时间戳撞车
    out['tiebreak'] = tiebreak()

    # 8. 读改写
    out['rmw'] = read_modify_write()

    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n')
    print('results.json', OUT.stat().st_size, 'bytes')
    for k, v in order.items():
        print('order %-10s distinct=%d' % (k, v['distinct']))
    for k, v in goss.items():
        print('gossip %-10s rounds=%s value=%s truth=%s'
              % (k, v['rounds'], v.get('value'), v.get('truth')))
    for k, v in part.items():
        print('partition %-10s %s / %s' % (k, v['value'], v['truth']))
    print('add_wins', out['add_wins'])
    print('rmw', out['rmw'])
    for row in out['growth']:
        print('growth', row)


if __name__ == '__main__':
    main()
