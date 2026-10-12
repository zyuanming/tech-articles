"""An original, deliberately small, pure Hindley–Milner teaching interpreter.

Python standard library. Run `python infer_lab.py` for the article examples.
Input is an AST, not OCaml/Python source. No effects, recursion, subtyping,
overloading, or higher-rank types. This program infers types; it does not execute
the supplied expressions. Original example code: CC BY 4.0, like this article.
"""
from dataclasses import dataclass
from itertools import count
import json


@dataclass(frozen=True)
class TVar:
    key: int


@dataclass(frozen=True)
class TCon:
    name: str
    args: tuple = ()


INT, BOOL = TCon('Int'), TCon('Bool')


def arrow(a, b):
    return TCon('->', (a, b))


def pair_type(a, b):
    return TCon('*', (a, b))


def ftv(t):
    if isinstance(t, TVar):
        return {t.key}
    return set().union(*(ftv(a) for a in t.args))


def apply(substitution, t):
    if isinstance(t, TVar):
        return apply(substitution, substitution[t.key]) if t.key in substitution else t
    return TCon(t.name, tuple(apply(substitution, a) for a in t.args))


def compose(newer, older):
    """Result acts as: first older, then newer. Acyclic solved substitutions."""
    result = {v: apply(newer, t) for v, t in older.items()}
    result.update({v: t for v, t in newer.items() if v not in result})
    return result


@dataclass(frozen=True)
class Scheme:
    quantified: frozenset
    body: object


def apply_scheme(s, scheme):
    return Scheme(scheme.quantified,
                  apply({v: t for v, t in s.items() if v not in scheme.quantified},
                        scheme.body))


def apply_env(s, env):
    return {name: apply_scheme(s, scheme) for name, scheme in env.items()}


def env_ftv(env):
    return set().union(*(ftv(sc.body) - sc.quantified for sc in env.values()))


def generalize(env, t):
    return Scheme(frozenset(ftv(t) - env_ftv(env)), t)


class TypeProblem(Exception):
    pass


def pretty(t):
    names = {}
    def go(t, parent=0):
        if isinstance(t, TVar):
            if t.key not in names:
                i = len(names)
                names[t.key] = chr(97 + i) if i < 26 else 'a' + str(i)
            return names[t.key]
        if not t.args:
            return t.name
        a, b = t.args
        if t.name == '->':
            s = go(a, 2) + ' -> ' + go(b, 1)
            return '(' + s + ')' if parent > 1 else s
        return '(' + go(a) + ' * ' + go(b) + ')'
    return go(t)


def raw_type(t):
    if isinstance(t, TVar):
        return 't' + str(t.key)
    if not t.args:
        return t.name
    return '(' + raw_type(t.args[0]) + ' ' + t.name + ' ' + raw_type(t.args[1]) + ')'


def unify(left, right, trace=None):
    if trace is not None:
        trace.append({'left': raw_type(left), 'right': raw_type(right)})
    if left == right:
        return {}
    if isinstance(left, TVar):
        if left.key in ftv(right):
            raise TypeProblem('occurs check: ' + raw_type(left) + ' occurs in ' + raw_type(right))
        return {left.key: right}
    if isinstance(right, TVar):
        return unify(right, left, trace)
    if left.name != right.name or len(left.args) != len(right.args):
        raise TypeProblem('type mismatch: ' + raw_type(left) + ' versus ' + raw_type(right))
    s = {}
    for a, b in zip(left.args, right.args):
        s = compose(unify(apply(s, a), apply(s, b), trace), s)
    return s


# AST constructors keep the example focused on types rather than parsing.
def Var(name): return ('var', name)
def Lit(value):
    if type(value) not in (int, bool):
        raise ValueError('Only Int and Bool literals are in this language')
    return ('lit', value)
def Lam(name, body): return ('lam', name, body)
def App(f, x): return ('app', f, x)
def Let(name, value, body): return ('let', name, value, body)
def Pair(a, b): return ('pair', a, b)


class Infer:
    def __init__(self, start=0):
        self.ids = count(start)
        self.trace = []

    def fresh(self):
        return TVar(next(self.ids))

    def instantiate(self, scheme):
        return apply({v: self.fresh() for v in sorted(scheme.quantified)}, scheme.body)

    def w(self, env, expression):
        tag, *args = expression
        if tag == 'lit':
            return {}, BOOL if type(args[0]) is bool else INT
        if tag == 'var':
            if args[0] not in env:
                raise TypeProblem('unbound name: ' + args[0])
            return {}, self.instantiate(env[args[0]])
        if tag == 'lam':
            name, body = args
            a = self.fresh()
            s, t = self.w({**env, name: Scheme(frozenset(), a)}, body)
            return s, arrow(apply(s, a), t)
        if tag == 'app':
            f, x = args
            s1, tf = self.w(env, f)
            s2, tx = self.w(apply_env(s1, env), x)
            result = self.fresh()
            s3 = unify(apply(s2, tf), arrow(tx, result), self.trace)
            return compose(s3, compose(s2, s1)), apply(s3, result)
        if tag == 'let':
            name, value, body = args
            s1, t = self.w(env, value)
            updated = apply_env(s1, env)
            scheme = generalize(updated, apply(s1, t))
            s2, result = self.w({**updated, name: scheme}, body)
            return compose(s2, s1), result
        if tag == 'pair':
            s1, a = self.w(env, args[0])
            s2, b = self.w(apply_env(s1, env), args[1])
            return compose(s2, s1), pair_type(apply(s2, a), b)
        raise ValueError('unknown AST tag: ' + tag)


def standard_env():
    mono = lambda t: Scheme(frozenset(), t)
    return {'add': mono(arrow(INT, arrow(INT, INT))),
            'not': mono(arrow(BOOL, BOOL))}


def infer(expression):
    engine = Infer()
    s, t = engine.w(standard_env(), expression)
    return apply(s, t)


def examples():
    identity = Lam('x', Var('x'))
    twice = Lam('f', Lam('x', App(Var('f'), App(Var('f'), Var('x')))))
    compose_fn = Lam('f', Lam('g', Lam('x', App(Var('f'), App(Var('g'), Var('x'))))))
    poly = Let('id', identity, Pair(App(Var('id'), Lit(3)), App(Var('id'), Lit(True))))
    shared = Lam('f', Pair(App(Var('f'), Lit(3)), App(Var('f'), Lit(True))))
    captured = Lam('x', Let('k', Lam('y', Var('x')),
                          Pair(App(Var('k'), Lit(3)), App(Var('k'), Lit(True)))))
    bad_capture = Lam('x', Let('k', Lam('y', Var('x')),
        Pair(App(App(Var('add'), App(Var('k'), Lit(3))), Lit(1)),
             App(Var('not'), App(Var('k'), Lit(True))))))
    return {
        'identity': identity, 'twice': twice, 'compose': compose_fn,
        'let_two_types': poly, 'lambda_two_types': shared,
        'captured_result_shared': captured, 'bad_capture': bad_capture,
        'self_application': Lam('x', App(Var('x'), Var('x'))),
        'let_id_id': Let('id', identity, App(Var('id'), Var('id'))),
        'integer_add_bool': App(App(Var('add'), Lit(True)), Lit(1)),
    }


def run_examples():
    results = {}
    for name, e in examples().items():
        try:
            results[name] = {'type': pretty(infer(e))}
        except TypeProblem as error:
            results[name] = {'error': str(error)}
    return results


if __name__ == '__main__':
    print(json.dumps(run_examples(), ensure_ascii=False, indent=2))
