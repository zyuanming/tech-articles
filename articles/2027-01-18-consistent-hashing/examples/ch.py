"""一致性哈希的三个方案：取模、带虚拟节点的哈希环、jump hash。

只用标准库。所有"位置"都是 64 位无符号整数，环的周长就是 2^64。
"""

import bisect
import hashlib
import math
import random

SPACE = 1 << 64
MASK = SPACE - 1


def h64(s):
    """把任意字符串钉到环上的一个点：取 sha1 的前 8 字节。"""
    return int.from_bytes(hashlib.sha1(s.encode()).digest()[:8], 'big')


def make_keys(n, seed=7):
    rnd = random.Random(seed)
    return ['key:%06d:%08d' % (i, rnd.randrange(10 ** 8)) for i in range(n)]


def node_names(n, prefix='node'):
    return ['%s-%02d' % (prefix, i) for i in range(n)]


# ---------------------------------------------------------------- 取模

class Modulo:
    """最朴素的做法：h(key) % N。节点一变，N 就变了。"""

    def __init__(self, nodes):
        self.nodes = list(nodes)

    def owner(self, k):
        return self.nodes[h64(k) % len(self.nodes)]

    def points(self):
        return len(self.nodes)


# ---------------------------------------------------------------- 哈希环

class Ring:
    """每个节点在环上占若干个点；key 顺时针找到的第一个点就是它的主人。

    vnodes=1 时每个节点一个点；vnodes=128 时每个节点 128 个点（虚拟节点）。
    """

    def __init__(self, nodes, vnodes=1, tag=''):
        self.nodes = list(nodes)
        self.vnodes = vnodes
        self.points = sorted((h64('%s%s#%d' % (tag, n, i)), n)
                             for n in nodes for i in range(vnodes))
        self.pos = [p for p, _ in self.points]

    def owner(self, k):
        i = bisect.bisect_left(self.pos, h64(k))
        return self.points[i % len(self.points)][1]

    def owner_steps(self, k):
        """手写二分，顺便数比较次数（bisect 不会告诉你它比了几次）。"""
        target = h64(k)
        lo, hi, steps = 0, len(self.pos), 0
        while lo < hi:
            mid = (lo + hi) // 2
            steps += 1
            if self.pos[mid] < target:
                lo = mid + 1
            else:
                hi = mid
        return self.points[lo % len(self.points)][1], steps

    def arcs(self):
        """顺时针每一段弧：(起点, 终点, 节点)，终点已经处理过绕环。"""
        out = []
        m = len(self.points)
        for i, (p, nd) in enumerate(self.points):
            nxt = self.points[(i + 1) % m][0]
            out.append((p, nxt if nxt > p else nxt + SPACE, nd))
        return out

    def load(self, keys):
        c = {n: 0 for n in self.nodes}
        for k in keys:
            c[self.owner(k)] += 1
        return c


# ---------------------------------------------------------------- jump hash

def jump_owner(k, n, count=False):
    """Lamping 与 Veach 的 jump consistent hash：返回 [0, n) 里的一个桶号。"""
    key = h64(k)
    b, j, steps = -1, 0, 0
    while j < n:
        b = j
        key = (key * 2862933555777941757 + 1) & MASK
        j = int((b + 1) * (float(1 << 31) / float((key >> 33) + 1)))
        steps += 1
    return (b, steps) if count else b


# ---------------------------------------------------------------- 统计小工具

def mean(xs):
    return sum(xs) / len(xs)


def stdev(xs):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def moved_fraction(owner_a, owner_b, keys):
    """从方案 a 换到方案 b，有多大比例的 key 换了归属。"""
    diff = sum(1 for k in keys if owner_a(k) != owner_b(k))
    return diff / len(keys)


def ratios(counts):
    vals = [counts[n] for n in sorted(counts)]
    m = mean(vals)
    return {'max': max(vals) / m, 'min': min(vals) / m, 'stdev': stdev(vals) / m}
