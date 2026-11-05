"""求和的几种做法。标准库 only，全部双精度。

所有函数都接受一个可迭代对象，按顺序逐个加入。故意不排序、不缓存——
x 的先后就是实验变量。

    naive(xs)        最直白的 s += x
    kahan(xs)        Kahan 1965 的补偿求和
    neumaier(xs)     Neumaier 1974 的改进（|x| > |s| 时换一种记法）
    pairwise(xs)     分治两两相加
    exact(xs)        math.fsum（Shewchuk 的精确累加），当参照物用

    invariance      同方差的两种算法：一次扫与 Welford
    ops_per_term     静态计数：每个数要花几次四则运算，不测时间
"""

from __future__ import annotations

import math


def naive(xs):
    s = 0.0
    for x in xs:
        s += x
    return s


def kahan(xs):
    """Kahan（1965）：把「加的时候丢掉的那一点」单独存起来，下一步再补回去。"""
    s = 0.0
    c = 0.0
    for x in xs:
        y = x - c
        t = s + y
        c = (t - s) - y
        s = t
    return s


def neumaier(xs):
    """Neumaier（1974）：当 |x| 比 |s| 大时，Kahan 的那一步会算错方向，换一种记法。"""
    s = 0.0
    c = 0.0
    for x in xs:
        t = s + x
        if abs(s) >= abs(x):
            c += (s - t) + x
        else:
            c += (x - t) + s
        s = t
    return s + c


def pairwise(xs):
    if len(xs) <= 32:
        return naive(xs)
    mid = len(xs) // 2
    return pairwise(xs[:mid]) + pairwise(xs[mid:])


def exact(xs):
    return math.fsum(xs)


# ---------------------------------------------------------------- 方差

def variance_onescan(xs):
    """一次扫：E[x²] − (E[x])²。教科书上最常见，也最容易在偏移大的数据上崩。"""
    n = len(xs)
    s1 = naive(xs)
    s2 = naive([x * x for x in xs])
    return s2 / n - (s1 / n) ** 2


def variance_twopass(xs):
    """两遍：先求均值，再求和 (x − mean)²。"""
    n = len(xs)
    mean = exact(xs) / n
    return exact([(x - mean) ** 2 for x in xs]) / n


def variance_welford(xs):
    """Welford（1962）：每来一个数就更新均值与离差，不用第二次遍历，也不减两个大数。"""
    n = 0
    mean = 0.0
    m2 = 0.0
    for x in xs:
        n += 1
        d = x - mean
        mean += d / n
        m2 += d * (x - mean)
    return m2 / n


# ---------------------------------------------------------------- 计数

OPS = {
    'naive': {'add': 1, 'sub': 0, 'mul': 0, 'branch': 0},
    'kahan': {'add': 1, 'sub': 3, 'mul': 0, 'branch': 0},
    'neumaier': {'add': 2, 'sub': 2, 'mul': 0, 'branch': 1},
    'pairwise': {'add': 1, 'sub': 0, 'mul': 0, 'branch': 0},
}


def ops_per_term():
    """每个数在内循环里要花几次四则运算（静态计数，不是耗时）。

    naive：s += x，一次加法。
    Kahan：y = x − c（减）、t = s + y（加）、c = (t − s) − y（两次减）→ 一加三减。
    Neumaier：t = s + x（加）、比较一次、c += (s − t) + x 或 (x − t) + s（两次加减）→ 两加两减一次分支。
    pairwise：总数是 n − 1 次加法，摊到每个数约一次加，但要递归调用。
    """
    return {k: dict(v, total=v['add'] + v['sub'] + v['mul'] + v['branch'])
            for k, v in OPS.items()}


# ---------------------------------------------------------------- 测试数据

def lcg(seed):
    state = seed & 0xFFFFFFFFFFFFFFFF

    def nxt():
        nonlocal state
        state = (state * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        return state

    def unit():
        return (nxt() >> 11) / float(1 << 53)

    return nxt, unit


def harmonic(n):
    return [1.0 / k for k in range(1, n + 1)]


def wide_positive(n, seed=20270405, lo=-8.0, hi=8.0):
    """量级跨 16 个数量级的正数：模拟「大数和小数混在一起」。"""
    _, unit = lcg(seed)
    return [10.0 ** (lo + (hi - lo) * unit()) for _ in range(n)]


def noisy_offset(n, offset=1e8, seed=20270405):
    """均值 1e8、标准差 1 的数据：方差只有 1，但两个大数相减会丢掉几乎全部有效位。"""
    _, unit = lcg(seed)
    out = []
    for _ in range(n):
        u1 = max(unit(), 1e-12)
        u2 = unit()
        g = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        out.append(offset + g)
    return out


def cancel_mix(n, seed=20270405, lo=-30.0, hi=30.0):
    """符号随机、量级随机的一小串数：求和时正负抵消最厉害，最容易看出误差。"""
    _, unit = lcg(seed)
    out = []
    for _ in range(n):
        mag = 10.0 ** (lo + (hi - lo) * unit())
        out.append(mag if unit() < 0.5 else -mag)
    return out
