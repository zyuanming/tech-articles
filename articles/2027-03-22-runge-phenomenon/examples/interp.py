"""多项式插值：节点分布、Lebesgue 常数、收敛率。

只用标准库。所有求和都用双精度，没有用 NumPy——这里要看的正是「双精度够不够」，
换成任意精度反而把问题藏起来了。
"""
import math

# --------------------------------------------------------------------------
# 被插的函数
# --------------------------------------------------------------------------

def runge(x, a=25.0):
    """Runge 的例子 1/(1 + a x²)，a = 25 时极点在 ±0.2i。"""
    return 1.0 / (1.0 + a * x * x)


def absx(x):
    return abs(x)


# --------------------------------------------------------------------------
# 节点
# --------------------------------------------------------------------------

def equispaced(n, lo=-1.0, hi=1.0):
    """n 个等距节点，含两端。"""
    step = (hi - lo) / (n - 1)
    return [lo + step * i for i in range(n)]


def chebyshev(n, lo=-1.0, hi=1.0):
    """n 个 Chebyshev 节点（第一类零点的降序取反），按从小到大返回。"""
    mid, half = (lo + hi) / 2.0, (hi - lo) / 2.0
    pts = [mid + half * math.cos(math.pi * (2 * i + 1) / (2 * n))
           for i in range(n)]
    return sorted(pts)


def chebyshev_lobatto(n, lo=-1.0, hi=1.0):
    """n 个 Chebyshev–Lobatto 节点，含两端。"""
    mid, half = (lo + hi) / 2.0, (hi - lo) / 2.0
    pts = [mid + half * math.cos(math.pi * i / (n - 1)) for i in range(n)]
    return sorted(pts)


# --------------------------------------------------------------------------
# 重心形式的拉格朗日插值
# --------------------------------------------------------------------------

def bary_weights(nodes):
    """w_i = 1 / prod_{j≠i} (x_i − x_j)。"""
    n = len(nodes)
    w = []
    for i in range(n):
        prod = 1.0
        for j in range(n):
            if j != i:
                prod *= nodes[i] - nodes[j]
        w.append(1.0 / prod)
    return w


def bary_eval(x, nodes, vals, w):
    num = den = 0.0
    for xi, vi, wi in zip(nodes, vals, w):
        d = x - xi
        if d == 0.0:
            return vi
        t = wi / d
        num += t * vi
        den += t
    return num / den


def interpolant(nodes, fn):
    """返回 (x) -> p(x) 的闭包，权重只算一次。"""
    vals = [fn(x) for x in nodes]
    w = bary_weights(nodes)
    return lambda x: bary_eval(x, nodes, vals, w)


# --------------------------------------------------------------------------
# 误差与 Lebesgue 常数
# --------------------------------------------------------------------------

def grid(lo, hi, count):
    step = (hi - lo) / (count - 1)
    return [lo + step * i for i in range(count)]


def sup_error(fn, nodes, count=4001, lo=-1.0, hi=1.0):
    """在稠密网格上取最大误差，同时记下位置。"""
    p = interpolant(nodes, fn)
    best, at = 0.0, lo
    for x in grid(lo, hi, count):
        e = abs(fn(x) - p(x))
        if e > best:
            best, at = e, x
    return best, at


def lebesgue(nodes, count=4001, lo=-1.0, hi=1.0):
    """λ = max_x Σ_i |L_i(x)|，用重心权重算，不需要显式写出 L_i。"""
    w = bary_weights(nodes)
    best, at = 0.0, lo
    for x in grid(lo, hi, count):
        num = den = 0.0
        hit = False
        for xi, wi in zip(nodes, w):
            d = x - xi
            if d == 0.0:
                hit = True
                break
            t = wi / d
            num += abs(t)
            den += t
        if hit:
            continue
        val = num / abs(den)
        if val > best:
            best, at = val, x
    return best, at


def basis_at(nodes, x):
    """在 x 处返回每个 L_i(x)，用于画基函数。"""
    w = bary_weights(nodes)
    num = 0.0
    den = 0.0
    terms = []
    for xi, wi in zip(nodes, w):
        d = x - xi
        if d == 0.0:
            return [1.0 if xi == x else 0.0 for xi in nodes]
        t = wi / d
        terms.append(t)
        num += abs(t)
        den += t
    if den == 0.0:
        return [0.0] * len(nodes)
    return [t / den for t in terms]


# --------------------------------------------------------------------------
# 单项式基：Vandermonde 求解与条件数
# --------------------------------------------------------------------------

def vandermonde(nodes):
    return [[x ** k for k in range(len(nodes))] for x in nodes]


def solve(a, b):
    """高斯消元（列主元），原地改 a、b，返回解。"""
    n = len(a)
    m = [row[:] for row in a]
    v = b[:]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        if m[p][c] == 0.0:
            raise ZeroDivisionError('singular')
        if p != c:
            m[c], m[p] = m[p], m[c]
            v[c], v[p] = v[p], v[c]
        piv = m[c][c]
        for r in range(c + 1, n):
            f = m[r][c] / piv
            if f == 0.0:
                continue
            for k in range(c, n):
                m[r][k] -= f * m[c][k]
            v[r] -= f * v[c]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = v[r] - sum(m[r][k] * x[k] for k in range(r + 1, n))
        x[r] = s / m[r][r]
    return x


def monomial_fit(nodes, fn):
    """用单项式基解出系数，再在稠密网格上看误差。"""
    v = vandermonde(nodes)
    coef = solve(v, [fn(x) for x in nodes])
    return coef


def polyval(coef, x):
    s = 0.0
    for c in reversed(coef):
        s = s * x + c
    return s


# --------------------------------------------------------------------------
# 收敛率：极点的位置决定 ρ
# --------------------------------------------------------------------------

def ellipse_rho(imag, real=0.0):
    """极点 z = real + imag·i 落在哪条 Bernstein 椭圆上，返回 ρ ≥ 1。"""
    z = complex(real, imag)
    s = (z * z - 1.0) ** 0.5
    w = z + s
    return abs(w)


def fit_ratio(ns, errs):
    """对 log(err) 关于 n 做最小二乘，返回每加一个节点误差乘的倍数。"""
    pts = [(n, math.log(e)) for n, e in zip(ns, errs) if e > 0]
    k = len(pts)
    sx = sum(p[0] for p in pts)
    sy = sum(p[1] for p in pts)
    sxx = sum(p[0] ** 2 for p in pts)
    sxy = sum(p[0] * p[1] for p in pts)
    slope = (k * sxy - sx * sy) / (k * sxx - sx * sx)
    return math.exp(slope)


def fit_rho(ns, errs):
    """误差按 ρ 的 −n 次方掉时，反解 ρ。"""
    return 1.0 / fit_ratio(ns, errs)
