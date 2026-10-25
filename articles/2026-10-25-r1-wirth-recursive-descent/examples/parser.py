"""Original educational recursive descent parser. CC0-1.0."""
import json
import sys
from functools import wraps

MAX_CHARS = 256
MAX_NEST = 32

class ParseError(Exception):
    def __init__(self, stage, pos, expected, found):
        self.info = dict(stage=stage, pos=pos, expected=expected, found=found)
        super().__init__(str(self.info))


def tokenize(source):
    if len(source) > MAX_CHARS:
        raise ParseError('limit', MAX_CHARS, '最多256字符', '输入过长')
    tokens, digits = [], []
    i = 0
    while i < len(source):
        ch = source[i]
        if ch in ' \t\r\n':
            i += 1
            continue
        start = i
        if '0' <= ch <= '9':
            value = 0
            while i < len(source) and '0' <= source[i] <= '9':
                if i - start >= 9:
                    raise ParseError('limit', i, '最多9位整数', source[i])
                old = value
                value = 10 * value + int(source[i])
                digits.append(dict(pos=i, digit=int(source[i]), before=old, after=value))
                i += 1
            kind = 'NUM'
        elif ch in '+-*()':
            kind, value = ch, None
            i += 1
        else:
            raise ParseError('lex', i, '数字、+ - * ( ) 或空白', ch)
        tokens.append(dict(kind=kind, value=value, text=source[start:i], start=start, end=i))
    tokens.append(dict(kind='EOF', value=None, text='', start=i, end=i))
    return tokens, digits


def traced(fn):
    @wraps(fn)
    def call(self):
        self.stack.append(fn.__name__)
        self.event('enter', fn.__name__)
        node = fn(self)
        self.event('return', fn.__name__, node)
        self.stack.pop()
        return node
    return call


class Parser:
    def __init__(self, tokens):
        self.tokens, self.i = tokens, 0
        self.nodes, self.events, self.stack = [], [], []
        self.nest = 0

    def peek(self):
        return self.tokens[self.i]['kind']

    def event(self, action, detail, node=None):
        self.events.append(dict(step=len(self.events), action=action, detail=detail,
                                index=self.i, look=self.peek(), stack=self.stack.copy(), node=node))

    def take(self, kind):
        t = self.tokens[self.i]
        if t['kind'] != kind:
            raise ParseError('syntax', t['start'], kind, t['kind'])
        self.event('consume', t['text'] or 'EOF')
        if kind != 'EOF':
            self.i += 1
        return t

    def node(self, op, left=None, right=None, value=None):
        n = len(self.nodes)
        self.nodes.append(dict(id=n, op=op, left=left, right=right, value=value))
        self.event('build', op, n)
        return n

    @traced
    def expr(self):
        left = self.term()
        while self.peek() in ('+', '-'):
            op = self.take(self.peek())['kind']
            right = self.term()
            left = self.node(op, left, right)
        return left

    @traced
    def term(self):
        left = self.factor()
        while self.peek() == '*':
            self.take('*')
            right = self.factor()
            left = self.node('*', left, right)
        return left

    @traced
    def factor(self):
        if self.peek() == 'NUM':
            t = self.take('NUM')
            return self.node('NUM', value=t['value'])
        if self.peek() == '(':
            if self.nest >= MAX_NEST:
                t = self.tokens[self.i]
                raise ParseError('limit', t['start'], '最多32层括号', '(')
            self.take('(')
            self.nest += 1
            result = self.expr()
            self.take(')')
            self.nest -= 1
            return result
        t = self.tokens[self.i]
        raise ParseError('syntax', t['start'], 'NUM 或 (', t['kind'])


def evaluate(nodes):
    """Nodes are appended after their children, so evaluate without recursion."""
    values = []
    for n in nodes:
        if n['op'] == 'NUM':
            v = n['value']
        else:
            a, b = values[n['left']], values[n['right']]
            v = a + b if n['op'] == '+' else a - b if n['op'] == '-' else a * b
        values.append(v)
    return values


def parse(source):
    out = dict(source=source, ok=False, tokens=[], digits=[], nodes=[], events=[])
    p = None
    try:
        out['tokens'], out['digits'] = tokenize(source)
        p = Parser(out['tokens'])
        root = p.expr()
        p.take('EOF')
        values = evaluate(p.nodes)
        out.update(ok=True, root=root, values=values, value=values[root])
    except ParseError as e:
        out['error'] = e.info
    finally:
        if p:
            out.update(nodes=p.nodes, events=p.events)
    return out


if __name__ == '__main__':
    print(json.dumps(parse(sys.argv[1] if len(sys.argv) > 1 else '12-3*2-1'), ensure_ascii=False, indent=2))
