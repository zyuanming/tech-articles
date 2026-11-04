#!/usr/bin/env python3
"""主元一文的全部实验，输出 results.json。只依赖标准库。"""
from __future__ import annotations

import json
import math
from fractions import Fraction as F
from pathlib import Path

import ge

HERE = Path(__file__).resolve().parent
OUT = {}


def s(v):
    """分数转可读字符串。"""
    v = F(v)
    if v.denominator == 1:
        return str(v.numerator)
    return '%d/%d' % (v.numerator, v.denominator)


def fnum(v):
    """分数转 float，给画图用。"""
    return float(v)


# ---------------------------------------------------------------- 1. 三阶例子
A3 = [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]]
b3 = [8, -11, -3]
x3, steps3, swaps3 = ge.solve_frac(A3, b3)
OUT['toy'] = dict(
    A=[[s(v) for v in row] for row in A3],
    b=[s(v) for v in b3],
    x=[s(v) for v in x3],
    swaps=swaps3,
    steps=[dict(k=st['k'], pivot_row=st['pivot_row'], pivot=s(st['pivot']),
                multipliers=[[i, m] for i, m in st['multipliers']],
                M=st['M']) for st in steps3],
    check=[s(v) for v in ge.matmul([[F(v) for v in row] for row in A3], x3)],
)

# ---------------------------------------------------------------- 2. 主元为零
Z = [[0, 1, 1], [1, 1, 1], [1, -1, 1]]
zb = [3, 4, 2]
zx, zsteps, zswaps = ge.solve_frac(Z, zb, pivot=True)
try:
    ge.solve_frac(Z, zb, pivot=False)
    crashed = False
except ZeroDivisionError as exc:
    crashed = True
    msg = str(exc)
OUT['zero'] = dict(
    A=[[s(v) for v in row] for row in Z],
    b=[s(v) for v in zb],
    x=[s(v) for v in zx],
    no_pivot_crashes=crashed,
    no_pivot_message=msg if crashed else None,
    swaps_with_pivot=zswaps,
    steps=[dict(k=st['k'], pivot_row=st['pivot_row'], pivot=s(st['pivot']),
                multipliers=[[i, m] for i, m in st['multipliers']]) for st in zsteps],
)

# ---------------------------------------------------------------- 3. 小主元
# 0.0001 x1 + x2 = 1 ; x1 + x2 = 2，三位有效数字手算
C = [[0.0001, 1.0], [1.0, 1.0]]
cb = [1.0, 2.0]
xc_exact, _, _ = ge.solve_frac(
    [[F(1, 10000), F(1)], [F(1), F(1)]], [F(1), F(2)])
x_no, info_no = ge.solve_prec(C, cb, digits=3, pivot=False)
x_yes, info_yes = ge.solve_prec(C, cb, digits=3, pivot=True)
x_f64_no, _ = ge.solve_prec(C, cb, digits=None, pivot=False)
x_f64_yes, _ = ge.solve_prec(C, cb, digits=None, pivot=True)
OUT['cancel'] = dict(
    A=C, b=cb,
    exact=[fnum(v) for v in xc_exact],
    digits3_no_pivot=x_no,
    digits3_partial=x_yes,
    digits3_no_pivot_error=max(abs(a - fnum(b)) for a, b in zip(x_no, xc_exact)),
    digits3_partial_error=max(abs(a - fnum(b)) for a, b in zip(x_yes, xc_exact)),
    f64_no_pivot=x_f64_no,
    f64_partial=x_f64_yes,
)

# ---------------------------------------------------------------- 3b. 单精度扫描
sweep = []
for e in (-1, -2, -3, -4, -5, -6, -7):
    p = 10.0 ** e
    A = [[p, 1.0], [1.0, 1.0]]
    b = [1.0 + p, 2.0]
    xs, _ = ge.solve_prec(A, b, single=True, pivot=False)
    xp, _ = ge.solve_prec(A, b, single=True, pivot=True)
    sweep.append(dict(p=p, cond=1.0 / p,
                      err_no_pivot=abs(xs[0] - 1.0),
                      err_partial=abs(xp[0] - 1.0),
                      x_no_pivot=xs[0], x_partial=xp[0]))
OUT['sweep'] = sweep

# ---------------------------------------------------------------- 4. 增长因子
wil = []
for n in (5, 10, 15, 20, 25, 30):
    A = ge.wilkinson(n)
    wil.append(dict(n=n, no_pivot=ge.growth(A, pivot=False),
                    partial=ge.growth(A, pivot=True)))
OUT['wilkinson'] = wil

rnd = []
for n in (10, 20, 40, 80, 160, 320):
    gs_no, gs_yes, dead, dead_p = [], [], 0, 0
    for seed in range(1, 21):
        A = ge.rand_int(n, seed)
        g = ge.growth(A, pivot=False)
        if not math.isfinite(g):
            dead += 1
        else:
            gs_no.append(g)
        h = ge.growth(A, pivot=True)
        if not math.isfinite(h):
            dead_p += 1
        else:
            gs_yes.append(h)
    gs_no.sort()
    gs_yes.sort()
    rnd.append(dict(n=n, seeds=20, dead_no_pivot=dead, dead_partial=dead_p,
                    no_pivot_median=gs_no[len(gs_no) // 2] if gs_no else None,
                    no_pivot_max=max(gs_no) if gs_no else None,
                    partial_median=gs_yes[len(gs_yes) // 2],
                    partial_max=max(gs_yes)))
OUT['random_growth'] = rnd

# ±1 矩阵常常恰好奇异：枚举所有 3 阶与 4 阶
OUT['pm1'] = [ge.pm1_singular_count(3), ge.pm1_singular_count(4)]

# ---------------------------------------------------------------- 5. Hilbert
hil = []
for n in (4, 6, 8, 10, 12):
    H = ge.hilbert(n)
    ones = [F(1)] * n
    rhs = ge.matmul(H, ones)
    cond = ge.cond1(H)
    xf, _ = ge.solve_prec([[float(v) for v in row] for row in H],
                          [float(v) for v in rhs], digits=None, pivot=True)
    err = max(abs(v - 1.0) for v in xf)
    # 残差：把解代回原方程，看「方程满足得多好」
    Hf = [[float(v) for v in row] for row in H]
    bf = [float(v) for v in rhs]
    res = [sum(a * v for a, v in zip(row, xf)) - t for row, t in zip(Hf, bf)]
    rel_res = max(abs(v) for v in res) / max(abs(v) for v in bf)
    hil.append(dict(n=n, cond=cond, fwd_err=err, rel_residual=rel_res))
OUT['hilbert'] = hil

# ---------------------------------------------------------------- 5a. 二维几何
G = [[F(1), F(1)], [F(2), F(-1)]]
gb = [F(4), F(2)]
gx, _, _ = ge.solve_frac(G, gb)
OUT['geom'] = dict(A=[[s(v) for v in row] for row in G], b=[s(v) for v in gb],
                   x=[s(v) for v in gx])

# 消掉 x：eq2 - 2*eq1，第二条线变成水平线 y = 2
after = [F(2) - 2 * F(4), F(-1) - 2 * F(1)]
OUT['geom']['after_elim'] = dict(coefficients=[s(v) for v in after],
                                 line='-3y = -6', y=2.0)

# ---------------------------------------------------------------- 5a2. 夹角与灵敏度
# 两条线在 (1,0) 相交，第二条的斜率 m = tan(theta)；右端项扰动 eps 时，
# 交点的位移是 eps / m。
sens = []
for deg in (90, 45, 10, 3, 1, 0.3, 0.1, 0.03):
    m = math.tan(math.radians(deg))
    sens.append(dict(deg=deg, slope=m, shift_1e6=1e-6 / m,
                     shift_1e3=1e-3 / m))
OUT['sensitivity'] = sens

# ---------------------------------------------------------------- 5b. 二维
F2 = [[F(0), F(1)], [F(1), F(1)]]
f2b = [F(1), F(2)]
fx, _, _ = ge.solve_frac(F2, f2b, pivot=True)
fx_no, _, _ = ge.solve_frac([[F(1), F(1)], [F(0), F(1)]], [F(2), F(1)])
OUT['flat'] = dict(A=[[s(v) for v in row] for row in F2], b=[s(v) for v in f2b],
                   x=[s(v) for v in fx], x_swapped=[s(v) for v in fx_no])

# ---------------------------------------------------------------- 6. 代价
cost = []
for n in (10, 100, 1000, 10000):
    mult = n ** 3 / 3 - n / 3
    adds = n ** 3 / 3 - n ** 2 / 2 + n / 6
    cmps = n * (n - 1) / 2
    cost.append(dict(n=n, mult=mult, add=adds, cmp=cmps,
                     total=mult + adds + cmps,
                     pivot_share=cmps / (mult + adds + cmps)))
OUT['cost'] = cost

# ---------------------------------------------------------------- 7. 舍入与残差
# Hilbert n=10 上部分主元消元的向前误差 vs 残差：说明「解错了」和「方程没满足」

(HERE / 'results.json').write_text(json.dumps(OUT, ensure_ascii=False, indent=1) + '\n')
print(OUT['toy']['x'], OUT['toy']['check'])
print('zero:', OUT['zero']['x'], OUT['zero']['no_pivot_crashes'])
print('cancel:', OUT['cancel']['exact'], OUT['cancel']['digits3_no_pivot'],
      OUT['cancel']['digits3_partial'])
print('f64:', OUT['cancel']['f64_no_pivot'], OUT['cancel']['f64_partial'])
print('wilkinson:', [(r['n'], round(r['no_pivot'], 1), round(r['partial'], 2))
                     for r in wil])
for r in rnd:
    print('random n=%d dead both %d/%d no_pivot med=%s partial med=%.2f max=%.2f' % (
        r['n'], r['dead_no_pivot'], r['dead_partial'], r['no_pivot_median'],
        r['partial_median'], r['partial_max']))
for r in hil:
    print('hilbert n=%d cond=%.3g fwd=%.3g res=%.3g' % (
        r['n'], r['cond'], r['fwd_err'], r['rel_residual']))
for r in OUT['sweep']:
    print('sweep p=%.0e cond=%.0e err_no=%.3g err_pivot=%.3g' % (
        r['p'], r['cond'], r['err_no_pivot'], r['err_partial']))
for r in cost:
    print('cost n=%d total=%.3g pivot_share=%.4f' % (
        r['n'], r['total'], r['pivot_share']))
