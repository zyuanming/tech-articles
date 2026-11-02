"""CRDT 模型：五种合并规则，外加两种「看起来也行」的朴素做法。

只用标准库。所有状态都是可 JSON 序列化的普通结构，方便比较和算指纹。
"""

from __future__ import annotations

import hashlib
import json


def fp(state):
    """状态的指纹：同样的内容得到同样的短串。"""
    return hashlib.sha1(json.dumps(state, sort_keys=True).encode()).hexdigest()[:12]


# ---------------------------------------------------------------- 最后写入者胜

class LWW:
    """时间戳大的赢；时间戳一样就比节点名，保证谁都算出同一个答案。"""

    kind = 'lww'

    def __init__(self, node, ts=0, val=None):
        self.st = {'ts': ts, 'node': node, 'val': val}

    def write(self, v):
        self.st = {'ts': self.st['ts'] + 1, 'node': self.st['node'], 'val': v}
        return dict(self.st)

    def merge(self, other):
        if (other['ts'], other['node']) > (self.st['ts'], self.st['node']):
            self.st = dict(other)
        return self.st

    def state(self):
        return dict(self.st)

    def value(self):
        return self.st['val']


# ---------------------------------------------------------------- 加法计数器

class GCounter:
    """每个节点只写自己那一格，合并时逐格取最大，读的时候求和。"""

    kind = 'gcounter'

    def __init__(self, node, cells=None):
        self.node = node
        self.cells = dict(cells or {})

    def add(self, k=1):
        self.cells[self.node] = self.cells.get(self.node, 0) + k
        return dict(self.cells)

    def merge(self, other):
        for n, v in other.items():
            self.cells[n] = max(self.cells.get(n, 0), v)
        return dict(self.cells)

    def state(self):
        return dict(self.cells)

    def value(self):
        return sum(self.cells.values())


class PNCounter:
    """两个 GCounter：一个记加，一个记减。"""

    kind = 'pncounter'

    def __init__(self, node):
        self.node = node
        self.pos = GCounter(node)
        self.neg = GCounter(node)

    def add(self):
        return {'pos': self.pos.add(1), 'neg': dict(self.neg.cells)}

    def sub(self):
        return {'pos': dict(self.pos.cells), 'neg': self.neg.add(1)}

    def merge(self, other):
        self.pos.merge(other['pos'])
        self.neg.merge(other['neg'])
        return {'pos': dict(self.pos.cells), 'neg': dict(self.neg.cells)}

    def state(self):
        return {'pos': dict(self.pos.cells), 'neg': dict(self.neg.cells)}

    def value(self):
        return self.pos.value() - self.neg.value()


# ---------------------------------------------------------------- 集合

class TwoPSet:
    """加进去、删下去，各记一份；一旦删掉就不能再加回来。"""

    kind = 'twopset'

    def __init__(self, added=(), removed=()):
        self.added = set(added)
        self.removed = set(removed)

    def add(self, e):
        self.added.add(e)
        return self.state()

    def remove(self, e):
        self.removed.add(e)
        return self.state()

    def state(self):
        return {'added': sorted(self.added), 'removed': sorted(self.removed)}

    def merge(self, other):
        self.added |= set(other['added'])
        self.removed |= set(other['removed'])
        return self.state()

    def has(self, e):
        return e in self.added and e not in self.removed

    def load(self):
        return sum(1 for e in self.added if self.has(e))


class ORSet:
    """每个「加」带一个唯一标签，删的时候只是把当时的标签作废。"""

    kind = 'orset'

    def __init__(self, node):
        self.node = node
        self.seq = 0
        self.tags = {}
        self.dead = set()

    def add(self, e):
        self.seq += 1
        tag = '%s#%d' % (self.node, self.seq)
        self.tags.setdefault(e, set()).add(tag)
        return self.state()

    def remove(self, e):
        for t in self.tags.get(e, ()):
            self.dead.add(t)
        return self.state()

    def state(self):
        return {'tags': {k: sorted(v) for k, v in sorted(self.tags.items())},
                'dead': sorted(self.dead)}

    def merge(self, other):
        for e, ts in other['tags'].items():
            self.tags.setdefault(e, set()).update(ts)
        self.dead |= set(other['dead'])
        return self.state()

    def has(self, e):
        return bool(set(self.tags.get(e, ())) - self.dead)

    def load(self):
        return sum(1 for e in self.tags if self.has(e))


class GSet:
    """只加不删：合并就是并集，最简单的一种。"""

    kind = 'gset'

    def __init__(self, items=()):
        self.items = set(items)

    def add(self, e):
        self.items.add(e)
        return sorted(self.items)

    def merge(self, other):
        self.items |= set(other)
        return sorted(self.items)

    def state(self):
        return sorted(self.items)

    def load(self):
        return len(self.items)


# ---------------------------------------------------------------- 两个朴素做法

class LateValue:
    """后到覆盖：谁的消息后到，就照抄谁的值。

    这是最符合直觉的「同步」写法，也是大多数手工同步脚本的样子。
    """

    kind = 'late'

    def __init__(self, node, val=None):
        self.val = val
        self.node = node

    def write(self, v):
        self.val = v
        return {'val': self.val}

    def merge(self, other):
        self.val = other['val']
        return {'val': self.val}

    def state(self):
        return {'val': self.val}

    def value(self):
        return self.val


class SumCounter:
    """合并时把对方的数加到自己身上。听起来合理，但重复消息会重复计数。"""

    kind = 'sum'

    def __init__(self, node, n=0):
        self.n = n
        self.node = node

    def add(self, k=1):
        self.n += k
        return {'n': self.n}

    def merge(self, other):
        self.n = self.n + other['n']
        return {'n': self.n}

    def state(self):
        return {'n': self.n}

    def value(self):
        return self.n


# ---------------------------------------------------------------- 小工具

def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)


def size_of(state):
    """状态序列化之后有多少字节——用来量「墓碑」的代价。"""
    return len(json.dumps(state, sort_keys=True).encode())
