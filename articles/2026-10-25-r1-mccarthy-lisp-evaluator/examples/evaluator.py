"""Dynamic association-list teaching evaluator. Code/data: CC0-1.0."""
from dataclasses import dataclass
import re

NIL = 'nil'
T = 't'
PRIMITIVES = {'atom': 1, 'eq': 2, 'car': 1, 'cdr': 1, 'cons': 2}

class LispError(Exception):
    pass

@dataclass(frozen=True, eq=False)
class Pair:
    car: object
    cdr: object

def atom(x):
    return isinstance(x, str)

def pack(items, tail=NIL):
    for item in reversed(items):
        tail = Pair(item, tail)
    return tail

def unpack(x):
    out = []
    while isinstance(x, Pair):
        out.append(x.car)
        x = x.cdr
    if x != NIL:
        raise LispError('expected proper list')
    return out

def show(x):
    if atom(x):
        return x
    parts = []
    while isinstance(x, Pair):
        parts.append(show(x.car))
        x = x.cdr
    if x != NIL:
        parts.extend(['.', show(x)])
    return '(' + ' '.join(parts) + ')'

def parse(source):
    tokens = re.findall(r"[()]|'|[^\s()']+", source.lower())
    pos = 0
    def read():
        nonlocal pos
        if pos >= len(tokens):
            raise LispError('unexpected end')
        token = tokens[pos]
        pos += 1
        if token == "'":
            return pack(['quote', read()])
        if token == '(':
            items = []
            while pos < len(tokens) and tokens[pos] != ')':
                if tokens[pos] == '.':
                    if not items:
                        raise LispError('bad dotted pair')
                    pos += 1
                    tail = read()
                    if pos >= len(tokens) or tokens[pos] != ')':
                        raise LispError('bad dotted tail')
                    pos += 1
                    return pack(items, tail)
                items.append(read())
            if pos >= len(tokens):
                raise LispError('missing closing parenthesis')
            pos += 1
            return pack(items)
        if token in (')', '.'):
            raise LispError('unexpected punctuation')
        if not re.fullmatch(r'[a-z][a-z0-9_-]*', token):
            raise LispError('expected symbol')
        return token
    value = read()
    if pos != len(tokens):
        raise LispError('extra input')
    return value

class Evaluator:
    def __init__(self, limit=2000):
        self.limit = limit
        self.steps = 0
        self.events = []
        self.stack = []
        self.calls = []

    def env_data(self, env):
        return [[k, show(v)] for k, v in env]

    def event(self, kind, **values):
        self.events.append(dict(n=len(self.events), kind=kind,
                                parent=self.stack[-1] if self.stack else None,
                                **values))

    def enter(self, kind, expr, env):
        self.steps += 1
        if self.steps > self.limit:
            raise LispError('step limit')
        ident = len(self.calls)
        self.calls.append(dict(id=ident, parent=self.stack[-1] if self.stack else None,
                               kind=kind, expr=expr, env=self.env_data(env)))
        self.stack.append(ident)
        self.event('enter', call=ident)
        return ident

    def finish(self, ident, value):
        self.calls[ident]['result'] = show(value)
        self.event('return', call=ident, value=show(value))
        self.stack.pop()
        return value

    def lookup(self, name, env):
        for index, (key, value) in enumerate(env):
            if name == key:
                self.event('lookup', name=name, index=index, value=show(value),
                           env=self.env_data(env))
                return value
        raise LispError('unbound: ' + name)

    @staticmethod
    def arity(items, n):
        if len(items) != n:
            raise LispError('arity: expected ' + str(n))

    def eval(self, expr, env=()):
        ident = self.enter('eval', show(expr), env)
        if atom(expr):
            value = expr if expr in (NIL, T) else self.lookup(expr, env)
        else:
            parts = unpack(expr)
            fn, args = parts[0], parts[1:]
            if fn == 'quote':
                self.arity(args, 1)
                value = args[0]
                self.event('quote', value=show(value))
            elif fn == 'cond':
                for index, clause in enumerate(args):
                    pair = unpack(clause)
                    self.arity(pair, 2)
                    test = self.eval(pair[0], env)
                    self.event('test', clause=index, test=show(pair[0]),
                               value=show(test), selected=test != NIL)
                    if test != NIL:
                        value = self.eval(pair[1], env)
                        break
                else:
                    raise LispError('cond: no true clause')
            else:
                values = [self.eval(arg, env) for arg in args]
                self.event('arguments', fn=show(fn), values=[show(v) for v in values])
                value = self.apply(fn, values, env)
        return self.finish(ident, value)

    def apply(self, fn, values, env):
        ident = self.enter('apply', show(fn), env)
        self.calls[ident]['args'] = [show(v) for v in values]
        if atom(fn):
            if fn not in PRIMITIVES:
                value = self.apply(self.lookup(fn, env), values, env)
            else:
                self.arity(values, PRIMITIVES[fn])
                if fn == 'atom':
                    value = T if atom(values[0]) else NIL
                elif fn == 'eq':
                    if not all(atom(v) for v in values):
                        raise LispError('eq: symbols only')
                    value = T if values[0] == values[1] else NIL
                elif fn == 'cons':
                    value = Pair(*values)
                else:
                    if not isinstance(values[0], Pair):
                        raise LispError(fn + ': pair required')
                    value = getattr(values[0], fn)
        else:
            parts = unpack(fn)
            if not parts or parts[0] not in ('lambda', 'label'):
                raise LispError('not a function')
            self.arity(parts, 3)
            if parts[0] == 'label':
                name, body = parts[1:]
                if not atom(name) or name in (NIL, T) or name in PRIMITIVES:
                    raise LispError('bad label name')
                extended = ((name, body),) + tuple(env)
                self.event('label', name=name, value=show(body), env=self.env_data(extended))
                value = self.apply(body, values, extended)
            else:
                params, body = unpack(parts[1]), parts[2]
                if any(not atom(p) or p in (NIL, T) for p in params) or len(set(params)) != len(params):
                    raise LispError('bad parameters')
                self.arity(values, len(params))
                extended = tuple(zip(params, values)) + tuple(env)
                self.event('bind', params=params, values=[show(v) for v in values],
                           env=self.env_data(extended))
                value = self.eval(body, extended)
        return self.finish(ident, value)

def run(source, env=(), limit=2000):
    machine = Evaluator(limit)
    result = machine.eval(parse(source), env)
    return result, machine
