"""A* 的账本：节点扩展数、路径代价、启发式的强度。

只用标准库。网格是整数坐标，起点 (0,0) 在左上角，y 向下。
"""

from heapq import heappush, heappop
import math

MASK = (1 << 64) - 1
MOVES4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
MOVES8 = MOVES4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


class SplitMix64:
    """Steele–Lea–Flood 的 splitmix64，种子固定即可复现。"""

    def __init__(self, seed):
        self.state = seed & MASK

    def next(self):
        self.state = (self.state + 0x9E3779B97F4A7C15) & MASK
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
        return z ^ (z >> 31)

    def below(self, n):
        return self.next() % n

    def random(self):
        return self.next() / float(1 << 64)


# ---------------------------------------------------------------- 网格

class Grid:
    def __init__(self, width, height, walls=(), cost=None, diagonal=False,
                 diag_cost=None):
        self.w = width
        self.h = height
        self.walls = frozenset(walls)
        self.cost = dict(cost or {})
        self.moves = MOVES8 if diagonal else MOVES4
        self.diagonal = diagonal
        # 斜走的价格。默认 √2（欧氏几何），设成 1 就是「八方向同价」的常见写法
        self.diag_cost = math.sqrt(2.0) if diag_cost is None else diag_cost

    def inside(self, c):
        return 0 <= c[0] < self.w and 0 <= c[1] < self.h

    def blocked(self, c):
        return (not self.inside(c)) or c in self.walls

    def step_cost(self, a, b):
        if a == b:
            return 0
        base = self.diag_cost if (a[0] != b[0] and a[1] != b[1]) else 1.0
        return base * self.cost.get(b, 1.0)

    def neighbors(self, c):
        out = []
        for dx, dy in self.moves:
            n = (c[0] + dx, c[1] + dy)
            if self.blocked(n):
                continue
            if dx and dy:
                # 不允许贴着墙角斜穿
                if self.blocked((c[0] + dx, c[1])) or self.blocked((c[0], c[1] + dy)):
                    continue
            out.append(n)
        return out


# ---------------------------------------------------------------- 启发式

def h_zero(a, b):
    return 0.0


def h_manhattan(a, b):
    return float(abs(a[0] - b[0]) + abs(a[1] - b[1]))


def h_euclid(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def h_chebyshev(a, b):
    return float(max(abs(a[0] - b[0]), abs(a[1] - b[1])))


def h_octile(a, b):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    lo, hi = min(dx, dy), max(dx, dy)
    return (hi - lo) + lo * math.sqrt(2.0)


HEURISTICS = dict(zero=h_zero, manhattan=h_manhattan, euclid=h_euclid,
                  chebyshev=h_chebyshev, octile=h_octile)


# ---------------------------------------------------------------- 搜索

def search(grid, start, goal, h=h_zero, weight=1.0, reopen=True,
           tie_break=False):
    """返回扩展数、生成数、开表峰值、代价、路径。

    reopen=False 时闭表里的节点永不再打开（教科书那条「h 一致就不用重开」的
    优化，去掉一致性前提之后的写法）。tie_break=True 时同 f 值优先挑 h 更小的，
    也就是更靠近目标的先展开。
    """
    g = {start: 0.0}
    parent = {start: None}
    h0 = h(start, goal)
    counter = 1
    heap = [(weight * h0, h0, counter, start)] if tie_break else \
        [(weight * h0, counter, start)]
    closed = set()
    expansions = 0
    generated = 1
    open_max = 1
    reopenings = 0
    trace = []

    while heap:
        item = heappop(heap)
        if len(item) == 4:
            f, hh, _, cur = item
        else:
            f, _, cur = item
        if cur in closed:
            continue
        gs = g[cur]
        closed.add(cur)
        expansions += 1
        trace.append(dict(cell=list(cur), g=round(gs, 4),
                          h=round(h(cur, goal), 4), f=round(f, 4)))
        if cur == goal:
            path = []
            node = cur
            while node is not None:
                path.append(list(node))
                node = parent[node]
            path.reverse()
            return dict(expansions=expansions, generated=generated,
                        open_max=open_max, cost=round(gs, 4), path=path,
                        reopenings=reopenings, trace=trace)
        for n in grid.neighbors(cur):
            if n in closed and not reopen:
                continue
            ng = gs + grid.step_cost(cur, n)
            if ng + 1e-12 < g.get(n, float('inf')):
                g[n] = ng
                parent[n] = cur
                counter += 1
                generated += 1
                if n in closed:
                    closed.discard(n)
                    reopenings += 1
                hh = h(n, goal)
                if tie_break:
                    heappush(heap, (ng + weight * hh, hh, counter, n))
                else:
                    heappush(heap, (ng + weight * hh, counter, n))
                open_max = max(open_max, len(heap))
    return dict(expansions=expansions, generated=generated, open_max=open_max,
                cost=None, path=[], reopenings=reopenings, trace=trace)


def optimal_cost(grid, start, goal):
    return search(grid, start, goal, h_zero)['cost']
