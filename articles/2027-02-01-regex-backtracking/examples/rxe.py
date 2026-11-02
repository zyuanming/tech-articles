"""A tiny regular-expression engine with three interchangeable executors.

The point is not to be a useful regex library; it is to make the difference
between backtracking, memoised search and NFA simulation measurable with the
same pattern, the same program and the same step counter.

Supported syntax: literal characters, '.', '\\d', '\\w', '\\s', character
classes ('[a-z0-9_]', '[^ab]'), groups ('(?:...)' and '(...)'), alternation,
'*', '+', '?', the lazy variants ('*?', '+?', '??'), and the anchors '^' / '$'.
Backreferences and lookaround are deliberately absent: the automaton approach
cannot express them.
"""

import re as _re

INSTR = ('char', 'any', 'cls', 'split', 'jmp', 'bol', 'eol', 'match')

CLASSES = {
    'd': lambda c: c.isdigit(),
    'w': lambda c: c.isalnum() or c == '_',
    's': lambda c: c.isspace(),
    'D': lambda c: not c.isdigit(),
    'W': lambda c: not (c.isalnum() or c == '_'),
    'S': lambda c: not c.isspace(),
}


# ----------------------------------------------------------------- parser

class Parser:
    def __init__(self, pattern):
        self.s = pattern
        self.i = 0

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else None

    def take(self):
        c = self.peek()
        self.i += 1
        return c

    def parse(self):
        node = self.alt()
        if self.i != len(self.s):
            raise ValueError('unexpected %r at %d' % (self.peek(), self.i))
        return node

    def alt(self):
        branches = [self.cat()]
        while self.peek() == '|':
            self.take()
            branches.append(self.cat())
        return branches[0] if len(branches) == 1 else ('alt', branches)

    def cat(self):
        items = []
        while self.peek() not in (None, '|', ')'):
            items.append(self.rep())
        if not items:
            return ('empty',)
        return items[0] if len(items) == 1 else ('cat', items)

    def rep(self):
        node = self.atom()
        while True:
            c = self.peek()
            if c in ('*', '+', '?'):
                self.take()
                kind = {'*': 'star', '+': 'plus', '?': 'opt'}[c]
                lazy = False
                if self.peek() in ('?', '+'):
                    lazy = self.take() == '?'
                node = (kind, node, lazy)
            else:
                return node

    def atom(self):
        c = self.take()
        if c == '(':
            if self.s.startswith('?:', self.i):
                self.i += 2
            node = self.alt()
            if self.take() != ')':
                raise ValueError('missing )')
            return node
        if c == '[':
            return self.charclass()
        if c == '.':
            return ('any',)
        if c == '^':
            return ('bol',)
        if c == '$':
            return ('eol',)
        if c == '\\':
            e = self.take()
            if e in CLASSES:
                return ('cls', e)
            return ('char', e)
        if c is None:
            raise ValueError('pattern ends early')
        return ('char', c)

    def charclass(self):
        negate = self.peek() == '^'
        if negate:
            self.take()
        items = []
        while True:
            c = self.take()
            if c is None:
                raise ValueError('unterminated class')
            if c == ']' and items:
                break
            if self.peek() == '-' and self.i + 1 < len(self.s) and self.s[self.i + 1] != ']':
                self.take()
                hi = self.take()
                items.append((c, hi))
            else:
                items.append((c, c))
        return ('range', items, negate)


# ---------------------------------------------------------------- compiler

def compile_pattern(pattern):
    """Compile to a program: list of lists, each starting with an opcode."""
    prog = []

    def emit(*ins):
        prog.append(list(ins))
        return len(prog) - 1

    def patch(slots, target):
        for idx, field in slots:
            prog[idx][field] = target

    def gen(node):
        kind = node[0]
        if kind == 'char':
            i = emit('char', node[1], None)
            return i, [(i, 2)]
        if kind == 'any':
            i = emit('any', None)
            return i, [(i, 1)]
        if kind in ('cls', 'range'):
            spec = node[1] if kind == 'cls' else (node[1], node[2])
            i = emit('cls', spec, None)
            return i, [(i, 2)]
        if kind == 'bol':
            i = emit('bol', None)
            return i, [(i, 1)]
        if kind == 'eol':
            i = emit('eol', None)
            return i, [(i, 1)]
        if kind == 'empty':
            i = emit('jmp', None)
            return i, [(i, 1)]
        if kind == 'cat':
            start = None
            dangling = None
            for child in node[1]:
                s, d = gen(child)
                if start is None:
                    start = s
                else:
                    patch(dangling, s)
                dangling = d
            return start, dangling
        if kind == 'alt':
            branches = [gen(child) for child in node[1]]
            starts = [b[0] for b in branches]
            dangling = []
            for b in branches:
                dangling.extend(b[1])
            head = starts[0]
            for s in starts[1:]:
                j = emit('split', head, s)
                head = j
            return head, dangling
        if kind == 'star':
            child, lazy = node[1], node[2]
            sp = emit('split', None, None)
            body, d = gen(child)
            if lazy:
                prog[sp][1] = None
                prog[sp][2] = body
                patch(d, sp)
                return sp, [(sp, 1)]
            prog[sp][1] = body
            patch(d, sp)
            return sp, [(sp, 2)]
        if kind == 'plus':
            child, lazy = node[1], node[2]
            body, d = gen(child)
            sp = emit('split', None, None)
            patch(d, sp)
            if lazy:
                prog[sp][1] = None
                prog[sp][2] = body
                return body, [(sp, 1)]
            prog[sp][1] = body
            return body, [(sp, 2)]
        if kind == 'opt':
            child, lazy = node[1], node[2]
            sp = emit('split', None, None)
            body, d = gen(child)
            if lazy:
                prog[sp][1] = body
                dangling = [(sp, 2)] + d
            else:
                prog[sp][1] = body
                dangling = [(sp, 2)] + d
            return sp, dangling
        raise ValueError('bad node %r' % (kind,))

    if pattern.startswith('^'):
        anchored = True
        pattern = pattern[1:]
    else:
        anchored = False
    start, dangling = gen(Parser(pattern).parse())
    end = emit('match')
    patch(dangling, end)
    return prog, start, anchored


# ------------------------------------------------------------- executors

def _class_hit(spec, ch):
    if isinstance(spec, str):
        return CLASSES[spec](ch)
    items, negate = spec
    ok = False
    for lo, hi in items:
        if lo <= ch <= hi:
            ok = True
            break
    return (not ok) if negate else ok


def run_backtrack(prog, start, text, anchored=False):
    """Plain recursive backtracking. One step per instruction executed."""
    n = len(text)
    steps = 0

    def go(pc, pos):
        nonlocal steps
        while True:
            ins = prog[pc]
            op = ins[0]
            steps += 1
            if op == 'char':
                if pos < n and text[pos] == ins[1]:
                    pc, pos = ins[2], pos + 1
                    continue
                return False
            if op == 'any':
                if pos < n:
                    pc, pos = ins[1], pos + 1
                    continue
                return False
            if op == 'cls':
                if pos < n and _class_hit(ins[1], text[pos]):
                    pc, pos = ins[2], pos + 1
                    continue
                return False
            if op == 'jmp':
                pc = ins[1]
                continue
            if op == 'split':
                if go(ins[1], pos):
                    return True
                pc = ins[2]
                continue
            if op == 'bol':
                if pos == 0:
                    pc = ins[1]
                    continue
                return False
            if op == 'eol':
                if pos == n:
                    pc = ins[1]
                    continue
                return False
            if op == 'match':
                return True
            raise ValueError(op)

    starts = [0] if anchored else range(n + 1)
    for s in starts:
        if go(start, s):
            return True, steps
    return False, steps


def run_memo(prog, start, text, anchored=False, trace=False):
    """Backtracking with a global "this state already failed" set."""
    n = len(text)
    steps = 0
    seen = set()
    visited = []
    stack = [(start, s) for s in ([0] if anchored else range(n + 1))]
    stack.reverse()
    while stack:
        pc, pos = stack.pop()
        if (pc, pos) in seen:
            continue
        seen.add((pc, pos))
        visited.append((pc, pos))
        steps += 1
        ins = prog[pc]
        op = ins[0]
        if op == 'char':
            if pos < n and text[pos] == ins[1]:
                stack.append((ins[2], pos + 1))
        elif op == 'any':
            if pos < n:
                stack.append((ins[1], pos + 1))
        elif op == 'cls':
            if pos < n and _class_hit(ins[1], text[pos]):
                stack.append((ins[2], pos + 1))
        elif op == 'jmp':
            stack.append((ins[1], pos))
        elif op == 'split':
            stack.append((ins[2], pos))
            stack.append((ins[1], pos))
        elif op == 'bol':
            if pos == 0:
                stack.append((ins[1], pos))
        elif op == 'eol':
            if pos == n:
                stack.append((ins[1], pos))
        elif op == 'match':
            return (True, steps, visited) if trace else (True, steps)
        else:
            raise ValueError(op)
    return (False, steps, visited) if trace else (False, steps)


def run_pike(prog, start, text, anchored=False, trace=False):
    """Thompson NFA simulation: each state is in a list at most once per position."""
    n = len(text)
    steps = 0

    def add(threads, seen, pc, pos):
        """Epsilon closure. Dedup is per list, so a state appears once."""
        nonlocal steps
        stack = [pc]
        while stack:
            pc = stack.pop()
            if pc in seen:
                continue
            seen.add(pc)
            steps += 1
            ins = prog[pc]
            op = ins[0]
            if op == 'jmp':
                stack.append(ins[1])
            elif op == 'split':
                stack.append(ins[2])
                stack.append(ins[1])
            elif op == 'bol':
                if pos == 0:
                    stack.append(ins[1])
            elif op == 'eol':
                if pos == n:
                    stack.append(ins[1])
            elif op == 'match':
                return True
            else:
                threads.append(pc)
        return False

    widths = []
    clist, cseen = [], set()
    for pos in range(n + 1):
        if not (anchored and pos > 0):
            if add(clist, cseen, start, pos):
                return (True, steps, widths) if trace else (True, steps)
        if trace:
            widths.append((pos, len(clist)))
        if pos == n:
            break
        ch = text[pos]
        nlist, nseen = [], set()
        for pc in clist:
            ins = prog[pc]
            op = ins[0]
            steps += 1
            if op == 'char':
                if ch == ins[1] and add(nlist, nseen, ins[2], pos + 1):
                    return (True, steps, widths) if trace else (True, steps)
            elif op == 'any':
                if add(nlist, nseen, ins[1], pos + 1):
                    return (True, steps, widths) if trace else (True, steps)
            elif op == 'cls':
                if _class_hit(ins[1], ch) and add(nlist, nseen, ins[2], pos + 1):
                    return (True, steps, widths) if trace else (True, steps)
        clist, cseen = nlist, nseen
        if not clist and anchored:
            break
    return (False, steps, widths) if trace else (False, steps)


ENGINES = {
    'backtrack': run_backtrack,
    'memo': run_memo,
    'pike': run_pike,
}


def search(pattern, text, engine='backtrack', anchored=None):
    prog, start, auto = compile_pattern(pattern)
    if anchored is None:
        anchored = auto
    matched, steps = ENGINES[engine](prog, start, text, anchored)
    return {'matched': matched, 'steps': steps}


def prog_size(pattern):
    prog, _, _ = compile_pattern(pattern)
    return len(prog)


def python_steps(pattern, text, anchored=False):
    """Reference: how many characters CPython's re scans per match attempt."""
    rx = _re.compile(pattern)
    m = rx.search(text) if not anchored else (rx.match(text) and True)
    return bool(m)
