"""采样点怎么来。标准库 only，全部双精度。

点的来源有四类，后面所有实验都只换这一件事：

    random_points   伪随机（线性同余，自己实现，不依赖 random 的版本差异）
    stratified      32×32 抖动网格：每格一个点，位置随机
    van_der_corput  二进制基数反转：0, 1/2, 1/4, 3/4, ...
    halton          多维版，第 j 维用第 j 个素数做基数
    shifted         把一组点整体平移（Cranley–Patterson），用于给确定性序列
                    重新造出误差棒

被估的积分固定：单位正方形里落在四分之一圆内的比例，真值 π/4。
"""

from __future__ import annotations

import math

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
PI_OVER_4 = math.pi / 4.0


def lcg(seed):
    state = seed & 0xFFFFFFFFFFFFFFFF

    def unit():
        nonlocal state
        state = (state * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        return (state >> 11) / float(1 << 53)

    return unit


def radical_inverse(n, base):
    """把 n 在 base 进制下写出来，小数点镜像到左边。n = 1..∞。"""
    inv = 1.0 / base
    f = inv
    r = 0.0
    while n > 0:
        r += (n % base) * f
        n //= base
        f *= inv
    return r


def van_der_corput(count, base=2):
    return [radical_inverse(i, base) for i in range(1, count + 1)]


def halton(count, dims, bases=None):
    """前 count 个点，每维一个基数，取前 dims 个素数。"""
    bases = bases or PRIMES[:dims]
    cols = [van_der_corput(count, b) for b in bases]
    return [tuple(cols[d][i] for d in range(dims)) for i in range(count)]


def random_points(count, dims, seed):
    unit = lcg(seed)
    return [tuple(unit() for _ in range(dims)) for _ in range(count)]


def stratified(count, seed):
    """count 必须是完全平方数：k×k 网格，每格一个随机点。二维。"""
    k = int(round(math.sqrt(count)))
    assert k * k == count, 'stratified 需要完全平方数个点'
    unit = lcg(seed)
    pts = []
    for i in range(k):
        for j in range(k):
            pts.append(((i + unit()) / k, (j + unit()) / k))
    return pts


def shifted(points, shift):
    """Cranley–Patterson 平移：整组点同时加上一个偏移，逐个模 1。"""
    return [tuple((p[d] + shift[d]) % 1.0 for d in range(len(p))) for p in points]


# ---------------------------------------------------------------- 被估的积分

def inside(xs, dims=2):
    """落在前两维的单位四分之一圆内。其余维度只当噪声维度，不进入判定。"""
    return xs[0] * xs[0] + xs[1] * xs[1] <= 1.0


def estimate_pi_over_4(points):
    return sum(1.0 for p in points if inside(p)) / len(points)


def max_gap(vals):
    """一维点集的最大空洞，含两端到 0 和 1 的段。"""
    xs = sorted(vals)
    edges = [0.0] + xs + [1.0]
    return max(b - a for a, b in zip(edges, edges[1:]))


def rms(errors):
    return math.sqrt(sum(e * e for e in errors) / len(errors))


def fit_exponent(ns, errs):
    """log(err) = log(C) − α log(n) 的最小二乘解，返回 α。"""
    xs = [math.log(n) for n in ns]
    ys = [math.log(e) for e in errs]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return -num / den
