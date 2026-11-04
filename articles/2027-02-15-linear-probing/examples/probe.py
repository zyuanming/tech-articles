"""线性探测的开地址哈希表：插入、查找、删除，以及三种探测策略的对照。

只用标准库。随机数是 splitmix64，种子固定，可复现。
"""
from __future__ import annotations

M64 = (1 << 64) - 1


class SplitMix64:
    """Steele–Lea–Flood 的 splitmix64。分布均匀、状态只有 64 位。"""

    def __init__(self, seed):
        self.s = seed & M64

    def next(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & M64
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
        return z ^ (z >> 31)


def keys(n, seed=1):
    """n 个互不相同的 64 位键。"""
    rng = SplitMix64(seed)
    out = []
    while len(out) < n:
        k = rng.next()
        if k not in out:            # 50 万键以内的重号极少，仍然要排掉
            out.append(k)
    return out


EMPTY, TOMB = -1, -2


class LinearTable:
    """线性探测。槽位三态：空、墓碑、占用。"""

    def __init__(self, m):
        self.m = m
        self.slot = [EMPTY] * m
        self.occ = 0          # 占用数
        self.tomb = 0         # 墓碑数
        self.max_probe = 0

    def _home(self, k):
        return k % self.m

    def insert(self, k):
        i = self._home(k)
        probe = 1
        while self.slot[i] not in (EMPTY, TOMB):
            if self.slot[i] == k:
                return probe
            i = (i + 1) % self.m
            probe += 1
        self.slot[i] = k
        self.occ += 1
        self.max_probe = max(self.max_probe, probe)
        return probe

    def find(self, k):
        """返回 (是否找到, 探测次数)。找不到也要走完整条链才算数。"""
        i = self._home(k)
        probe = 1
        while True:
            v = self.slot[i]
            if v == EMPTY:
                return False, probe
            if v == k:
                return True, probe
            i = (i + 1) % self.m
            probe += 1
            if probe > self.m:
                return False, probe

    def delete(self, k):
        ok, probe = self.find(k)
        if not ok:
            return False, probe
        i = self._home(k)
        while self.slot[i] != k:
            i = (i + 1) % self.m
        self.slot[i] = TOMB
        self.occ -= 1
        self.tomb += 1
        return True, probe

    def clusters(self):
        """连续非空槽位的长度列表（空槽打断）。墓碑不算断。"""
        out, run = [], 0
        for v in self.slot:
            if v != EMPTY:
                run += 1
            elif run:
                out.append(run)
                run = 0
        if run:
            out.append(run)
        return out


class RobinHood(LinearTable):
    """Robin Hood：谁的探测距离短就给谁让位。槽里存 (键, 起点)。"""

    def __init__(self, m):
        super().__init__(m)
        self.item = [None] * m          # (key, home)
        self.moves = 0                  # 发生了几次让位

    def _dist(self, home, i):
        return (i - home) % self.m

    def insert(self, k):
        home = self._home(k)
        i, dist = home, 0
        cur = (k, home)
        probe = 1
        while True:
            v = self.item[i]
            if v is None:
                self.item[i] = cur
                self.occ += 1
                self.max_probe = max(self.max_probe, probe)
                return probe
            if v[0] == k:
                return probe
            if self._dist(v[1], i) < dist:
                # 来人比占位者更「冤」，交换，带着被踢走的人继续往前
                self.item[i], cur = cur, v
                self.moves += 1
                dist = self._dist(cur[1], i)
            i = (i + 1) % self.m
            dist += 1
            probe += 1

    def clusters(self):
        out, run = [], 0
        for v in self.item:
            if v is not None:
                run += 1
            elif run:
                out.append(run)
                run = 0
        if run:
            out.append(run)
        return out

    def find(self, k):
        home = self._home(k)
        i, dist = home, 0
        probe = 1
        while True:
            v = self.item[i]
            if v is None:
                return False, probe
            if v[0] == k:
                return True, probe
            if self._dist(v[1], i) < dist:
                # 占位者比「如果 k 在这里该有的距离」还近，k 不可能在后面
                return False, probe
            i = (i + 1) % self.m
            dist += 1
            probe += 1
            if probe > self.m:
                return False, probe


class DoubleHash:
    """双散列：步长随键变，打散主聚集。m 取素数。"""

    def __init__(self, m):
        self.m = m
        self.slot = [EMPTY] * m
        self.occ = 0
        self.max_probe = 0

    def _step(self, k):
        return 1 + (k // self.m) % (self.m - 1)

    def insert(self, k):
        i = k % self.m
        s = self._step(k)
        probe = 1
        while self.slot[i] != EMPTY:
            if self.slot[i] == k:
                return probe
            i = (i + s) % self.m
            probe += 1
        self.slot[i] = k
        self.occ += 1
        self.max_probe = max(self.max_probe, probe)
        return probe

    def find(self, k):
        i = k % self.m
        s = self._step(k)
        probe = 1
        while True:
            v = self.slot[i]
            if v == EMPTY:
                return False, probe
            if v == k:
                return True, probe
            i = (i + s) % self.m
            probe += 1
            if probe > self.m:
                return False, probe


def knuth_success(alpha):
    """Knuth 1963：线性探测，平均成功探测次数（每条链等概率被查到）。"""
    return 0.5 * (1.0 + 1.0 / (1.0 - alpha))


def knuth_fail(alpha):
    """Knuth 1963：平均失败探测次数。"""
    return 0.5 * (1.0 + 1.0 / (1.0 - alpha) ** 2)
