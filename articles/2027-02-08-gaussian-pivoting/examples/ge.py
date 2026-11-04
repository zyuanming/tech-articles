"""高斯消元的三个版本：精确分数、有限位浮点、带/不带部分主元。

这个模块只做算术，不做 I/O。所有实验在 run_model.py 里跑。
"""
from __future__ import annotations

import math
from fractions import Fraction as F


# ---------------------------------------------------------------- 精确版本
def solve_frac(A, b, pivot=True):
    """用 Fraction 精确求解，返回 (x, 消元过程, 是否换过行)。"""
    n = len(A)
    M = [[F(x) for x in row] + [F(y)] for row, y in zip(A, b)]
    steps = []
    swaps = 0
    for k in range(n):
        if pivot:
            p = max(range(k, n), key=lambda i: abs(M[i][k]))
        else:
            p = k
        if M[p][k] == 0:
            raise ZeroDivisionError('pivot %d is zero' % k)
        if p != k:
            M[k], M[p] = M[p], M[k]
            swaps += 1
        rows = []
        for i in range(k + 1, n):
            f = M[i][k] / M[k][k]
            rows.append((i, f))
            for j in range(k, n + 1):
                M[i][j] -= f * M[k][j]
        steps.append(dict(k=k, pivot_row=p, pivot=M[k][k],
                          multipliers=[(i, str(f)) for i, f in rows],
                          M=[[str(v) for v in row] for row in M]))
    x = [F(0)] * n
    for i in range(n - 1, -1, -1):
        s = sum(M[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (M[i][n] - s) / M[i][i]
    return x, steps, swaps


def matmul(A, x):
    return [sum(a * v for a, v in zip(row, x)) for row in A]


def inv_frac(A):
    """精确逆矩阵：对每个单位向量解一次。"""
    n = len(A)
    cols = []
    for k in range(n):
        e = [F(1) if i == k else F(0) for i in range(n)]
        x, _, _ = solve_frac(A, e)
        cols.append(x)
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def norm1(M):
    """矩阵的 1-范数：列和的绝对值的最大值。"""
    n = len(M)
    return max(sum(abs(M[i][j]) for i in range(n)) for j in range(n))


def cond1(A):
    Ai = inv_frac(A)
    return float(norm1(A) * norm1(Ai))


def hilbert(n):
    return [[F(1, i + j + 1) for j in range(n)] for i in range(n)]


# ---------------------------------------------------------------- 有限精度版本
def _round(x, digits):
    """把 x 舍入到 digits 位有效数字，模拟手算/短字长的算术。"""
    if x == 0 or not math.isfinite(x):
        return x
    e = math.floor(math.log10(abs(x)))
    q = 10.0 ** (digits - 1 - e)
    return round(x * q) / q


def f32(x):
    """把双精度值舍入成 IEEE-754 单精度。"""
    import struct
    return struct.unpack('f', struct.pack('f', x))[0]


def solve_prec(A, b, digits=None, pivot=True, single=False):
    """digits=None 用双精度；digits 给了就舍入到 digits 位有效数字；
    single=True 时每一步都舍入成 float32。"""
    n = len(A)
    M = [[float(x) for x in row] + [float(y)] for row, y in zip(A, b)]
    if single:
        step = f32
        M = [[f32(v) for v in row] for row in M]
    elif digits is None:
        step = lambda v: v
    else:
        step = lambda v: _round(v, digits)
    swaps = 0
    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(M[i][k])) if pivot else k
        if M[p][k] == 0:
            # 没有主元可换：真实现里这里就返回失败，模型记成 NaN
            return [float('nan')] * n, dict(fail='zero pivot', k=k, swaps=swaps)
        if p != k:
            M[k], M[p] = M[p], M[k]
            swaps += 1
        for i in range(k + 1, n):
            f = step(M[i][k] / M[k][k])
            for j in range(k, n + 1):
                M[i][j] = step(M[i][j] - f * M[k][j])
            M[i][k] = 0.0
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = sum(M[i][j] * x[j] for j in range(i + 1, n))
        x[i] = step((M[i][n] - s) / M[i][i])
    return x, dict(swaps=swaps)


def growth(A, pivot=True):
    """消元过程中出现过的最大元素 / 初始最大元素。"""
    n = len(A)
    M = [[float(x) for x in row] for row in A]
    big = max(abs(v) for row in M for v in row)
    if big == 0:
        return 0.0
    peak = big
    for k in range(n):
        if pivot:
            p = max(range(k, n), key=lambda i: abs(M[i][k]))
            M[k], M[p] = M[p], M[k]
        if M[k][k] == 0:
            return float('inf')
        for i in range(k + 1, n):
            f = M[i][k] / M[k][k]
            for j in range(k, n):
                M[i][j] -= f * M[k][j]
            M[i][k] = 0.0
        peak = max(peak, max(abs(v) for row in M for v in row))
    return peak / big


# ---------------------------------------------------------------- 一些矩阵
def wilkinson(n):
    """Wilkinson 的增长矩阵：下三角全 -1、对角 1、最后一列 1。

    非主元消元时每一步的乘数都是 1，最后一列每步翻倍，元素长到 2^(n-1)。
    """
    A = [[F(0)] * n for _ in range(n)]
    for i in range(n):
        A[i][i] = F(1)
        A[i][n - 1] = F(1)
        for j in range(i):
            A[i][j] = F(-1)
    return A


def rand_int(n, seed, lo=-5, hi=5):
    """[-5,5] 上的随机整数矩阵。种子固定，可复现。"""
    import random
    rng = random.Random(seed)
    return [[F(rng.randint(lo, hi)) for _ in range(n)] for _ in range(n)]


def pm1_singular_count(n):
    """枚举全部 ±1 矩阵，数出恰好奇异的个数。n ≤ 4 才跑得完。"""
    import itertools
    total = sing = 0
    for flat in itertools.product((1, -1), repeat=n * n):
        A = [[F(flat[i * n + j]) for j in range(n)] for i in range(n)]
        total += 1
        try:
            solve_frac(A, [F(0)] * n, pivot=True)
        except ZeroDivisionError:
            sing += 1
    return dict(n=n, total=total, singular=sing, nonsingular=total - sing)


def rand_pm1(n, seed):
    """±1 随机矩阵。用 random.Random(seed) 的 Mersenne Twister，可复现。"""
    import random
    rng = random.Random(seed)
    return [[F(1) if rng.getrandbits(1) else F(-1) for _ in range(n)]
            for _ in range(n)]
