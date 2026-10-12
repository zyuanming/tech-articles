"""Executable author checks, not a proof of Algorithm W or an independent review.

Cross-checks infer_lab.py against a separate mutable-graph implementation,
enumerates a finite set of closed lambda terms, and uses deterministic random
ASTs including let, shadowing, pairs, Int and Bool. Standard library only.
"""
import json
import random
from functools import lru_cache
import infer_lab as w


class Cell:
    def __init__(self):
        self.link = None


class GraphError(Exception):
    pass


def prune(t):
    if isinstance(t, Cell) and t.link is not None:
        t.link = prune(t.link)
        return t.link
    return t


def free(t):
    t = prune(t)
    if isinstance(t, Cell):
        return {t}
    return set().union(*(free(a) for a in t[1:]))


def merge(a, b):
    work = [(a, b)]
    while work:
        a, b = map(prune, work.pop())
        if a is b:
            continue
        if isinstance(a, Cell):
            if a in free(b):
                raise GraphError('cycle')
            a.link = b
        elif isinstance(b, Cell):
            work.append((b, a))
        elif a[0] != b[0] or len(a) != len(b):
            raise GraphError('constructor clash')
        else:
            work.extend(zip(a[1:], b[1:]))


def clone(scheme):
    qs, body = scheme
    fresh = {v: Cell() for v in qs}
    def go(t):
        t = prune(t)
        if isinstance(t, Cell):
            return fresh.get(t, t)
        return (t[0], *(go(a) for a in t[1:]))
    return go(body)


def graph_infer(e):
    def walk(e, env):
        tag, *a = e
        if tag == 'lit':
            return ('Bool',) if type(a[0]) is bool else ('Int',)
        if tag == 'var':
            if a[0] not in env:
                raise GraphError('unbound')
            return clone(env[a[0]])
        if tag == 'lam':
            t = Cell()
            return ('->', t, walk(a[1], {**env, a[0]: (set(), t)}))
        if tag == 'app':
            f = walk(a[0], env)
            x = walk(a[1], env)
            result = Cell()
            merge(f, ('->', x, result))
            return result
        if tag == 'pair':
            left = walk(a[0], env)
            right = walk(a[1], env)
            return ('*', left, right)
        if tag == 'let':
            name, value, body = a
            t = walk(value, env)
            outside = set().union(*(free(v) - qs for qs, v in env.values()))
            return walk(body, {**env, name: (free(t) - outside, t)})
        raise ValueError(tag)
    env = {'add': (set(), ('->', ('Int',), ('->', ('Int',), ('Int',)))),
           'not': (set(), ('->', ('Bool',), ('Bool',)))}
    t = walk(e, env)
    def convert(t):
        t = prune(t)
        if isinstance(t, Cell):
            return w.TVar(id(t))
        return w.TCon(t[0], tuple(convert(a) for a in t[1:]))
    return w.pretty(convert(t))


def outcome(e):
    try:
        return w.pretty(w.infer(e))
    except w.TypeProblem:
        return None


def crosscheck(e):
    first = outcome(e)
    try:
        second = graph_infer(e)
    except GraphError:
        second = None
    assert first == second, (e, first, second)
    return first is not None


@lru_cache(None)
def lambda_terms(size, depth):
    result = []
    if size == 1:
        return tuple(w.Var('v' + str(i)) for i in range(depth))
    if size >= 2:
        result.extend(w.Lam('v' + str(depth), b) for b in lambda_terms(size - 1, depth + 1))
    for n in range(1, size - 1):
        result.extend(w.App(a, b) for a in lambda_terms(n, depth)
                      for b in lambda_terms(size - 1 - n, depth))
    return tuple(result)


def random_ast(rng, depth, names):
    leaves = [w.Lit(3), w.Lit(True), w.Var('add'), w.Var('not')]
    leaves.extend(w.Var(n) for n in names)
    if depth == 0 or rng.random() < .30:
        return rng.choice(leaves)
    kind = rng.randrange(4)
    name = rng.choice(['x', 'y', 'z'])  # deliberately includes name shadowing
    if kind == 0:
        return w.Lam(name, random_ast(rng, depth - 1, names + [name]))
    if kind == 1:
        return w.Let(name, random_ast(rng, depth - 1, names),
                     random_ast(rng, depth - 1, names + [name]))
    ctor = w.App if kind == 2 else w.Pair
    return ctor(random_ast(rng, depth - 1, names), random_ast(rng, depth - 1, names))


def run():
    expected = {
        'identity': 'a -> a', 'twice': '(a -> a) -> a -> a',
        'compose': '(a -> b) -> (c -> a) -> c -> b',
        'let_two_types': '(Int * Bool)', 'lambda_two_types': None,
        'captured_result_shared': 'a -> (a * a)', 'bad_capture': None,
        'self_application': None, 'let_id_id': 'a -> a', 'integer_add_bool': None,
    }
    for name, e in w.examples().items():
        assert outcome(e) == expected[name], name
        crosscheck(e)
    enumerated = accepted = 0
    for size in range(1, 10):
        for e in lambda_terms(size, 0):
            accepted += crosscheck(e)
            enumerated += 1
    rng = random.Random(20261012)
    random_accepted = 0
    for _ in range(20000):
        random_accepted += crosscheck(random_ast(rng, 6, []))
    # Fresh instances must differ, but repeated variables within each must agree.
    engine = w.Infer(100)
    scheme = w.Scheme(frozenset({0}), w.arrow(w.TVar(0), w.TVar(0)))
    a, b = engine.instantiate(scheme), engine.instantiate(scheme)
    assert a.args[0] == a.args[1] and b.args[0] == b.args[1] and a != b
    env = {'x': w.Scheme(frozenset(), w.TVar(10))}
    general = w.generalize(env, w.arrow(w.TVar(11), w.TVar(10)))
    assert general.quantified == frozenset({11})
    assert w.apply(w.compose({1: w.INT}, {0: w.TVar(1)}), w.TVar(0)) == w.INT
    engine = w.Infer()
    engine.w(w.standard_env(), w.examples()['twice'])
    return {'status': 'PASS', 'seed': 20261012, 'named_examples': expected,
            'closed_lambda_terms_size_1_to_9': enumerated,
            'closed_lambda_terms_accepted': accepted,
            'random_asts_depth_at_most_6': 20000, 'random_asts_accepted': random_accepted,
            'extra_structural_checks': 3, 'twice_unification_trace': engine.trace,
            'scope': 'Finite tests and author-created second implementation; not a general proof.'}


if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False, indent=2))
