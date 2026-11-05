#!/usr/bin/env python3
"""《一千个点能有多准》的全部实验。MIT。

    python3 run_model.py   →  examples/results.json

只用标准库。随机数来自 qmc.lcg，重跑逐字节相同。
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import qmc as Q

HERE = Path(__file__).resolve().parent
SEED = 20270412
NS = [16, 64, 256, 1024, 4096, 16384]
RUNS = 32


def vdc_table():
    vals = Q.van_der_corput(16)
    cells = []
    for k in range(8):
        lo, hi = k / 8.0, (k + 1) / 8.0
        idx = [i + 1 for i, v in enumerate(vals[:8]) if lo <= v < hi]
        cells.append({'cell': [lo, hi], 'index': idx})
    return {'first16': vals, 'first8_cells': cells,
            'one_per_cell': all(len(c['index']) == 1 for c in cells)}


def pi_scan():
    truth = Q.PI_OVER_4
    rows = []
    for n in NS:
        rnd = []
        strat = []
        shift = []
        for r in range(RUNS):
            pts = Q.random_points(n, 2, SEED + 1000 * r + n)
            rnd.append(abs(Q.estimate_pi_over_4(pts) - truth))
            pts = Q.stratified(n, SEED + 2000 * r + n)
            strat.append(abs(Q.estimate_pi_over_4(pts) - truth))
        hp = Q.halton(n, 2)
        halton_err = abs(Q.estimate_pi_over_4(hp) - truth)
        unit = Q.lcg(SEED + 7)
        for r in range(RUNS):
            sh = (unit(), unit())
            shift.append(abs(Q.estimate_pi_over_4(Q.shifted(hp, sh)) - truth))
        row = {'n': n, 'truth': truth,
                     'random_rms': Q.rms(rnd), 'random_max': max(rnd),
                     'stratified_rms': Q.rms(strat), 'stratified_max': max(strat),
                     'halton_err': halton_err,
                     'halton_shift_rms': Q.rms(shift), 'halton_shift_max': max(shift)}
        if n == 1024:
            row['shift_errors'] = shift   # 图 6 直接用这一批，不另抽
        rows.append(row)
    return rows


def convergence(rows):
    keys = [('random_rms', '随机'), ('stratified_rms', '抖动网格'),
            ('halton_shift_rms', 'Halton 平移'), ('halton_err', 'Halton 原样')]
    out = []
    for key, name in keys:
        errs = [r[key] for r in rows]
        out.append({'method': name, 'key': key,
                    'exponent': Q.fit_exponent([r['n'] for r in rows], errs),
                    'err_at_1024': [r[key] for r in rows if r['n'] == 1024][0],
                    'err_at_16384': errs[-1]})
    return out


def error_bars(rows):
    """固定 N = 1024：随机点的误差分布，与 Halton 的一个确定值。

    平移那一行直接复用 pi_scan 里 N = 1024 的那一批，图上和表上是同一组数。
    """
    truth = Q.PI_OVER_4
    n = 1024
    rnd = []
    for r in range(200):
        pts = Q.random_points(n, 2, SEED + 31 * r + 5)
        rnd.append(abs(Q.estimate_pi_over_4(pts) - truth))
    rms = Q.rms(rnd)
    row = [r for r in rows if r['n'] == n][0]
    return {
        'random_errors': rnd,
        'shift_errors': row['shift_errors'],
        'shift_rms': row['halton_shift_rms'],
        'n': n,
        'random_rms': rms, 'random_min': min(rnd), 'random_max': max(rnd),
        'random_over_2rms': sum(1 for e in rnd if e > 2 * rms) / len(rnd),
        'random_mean': sum(rnd) / len(rnd),
        'halton_err': row['halton_err'],
        'halton_over_2rms': row['halton_err'] > 2 * rms,
        'halton_below_rms': row['halton_err'] < rms,
    }


def gap_scan():
    """一维：把 n 个点排开，最大空洞有多宽。

    van der Corput 前 2^k 个点恰好是每条宽 1/2^k 的格子里一个，
    所以最大空洞就是 1/n；随机点的最大空洞约是 log(n)/n。
    """
    rows = []
    for n in NS:
        v = Q.van_der_corput(n)
        vgap = Q.max_gap(v)
        gaps = []
        for r in range(RUNS):
            pts = [x[0] for x in Q.random_points(n, 1, SEED + 3000 * r + n)]
            gaps.append(Q.max_gap(pts))
        rows.append({'n': n, 'vdc_gap': vgap, 'vdc_expected': 1.0 / n,
                     'random_gap_mean': sum(gaps) / len(gaps),
                     'random_gap_max': max(gaps),
                     'log_over_n': math.log(n) / n,
                     'ratio': (sum(gaps) / len(gaps)) / (1.0 / n)})
    return rows


def stuck():
    """点数翻四倍，分子是否也恰好翻四倍？以及标称点数对比值的影响。"""
    rows = []
    for k in range(4, 17):
        n = 1 << k
        c = sum(1 for p in Q.halton(n, 2) if Q.inside(p))
        rows.append({'n': n, 'inside': c, 'fraction': c / n,
                     'err': abs(c / n - Q.PI_OVER_4)})
    quads = []
    for i in range(len(rows) - 2):
        small, large = rows[i], rows[i + 2]
        if large['inside'] == 4 * small['inside']:
            quads.append({'small': small['n'], 'large': large['n'],
                          'inside': small['inside'], 'fraction': small['fraction']})
    seen = {}
    for r in rows:
        seen.setdefault(r['fraction'], []).append(r['n'])
    repeats = [{'fraction': f, 'ns': ns} for f, ns in seen.items() if len(ns) > 1]
    return {'rows': rows, 'quads': quads, 'repeats': repeats}


def main():
    R = {'meta': {'seed': SEED, 'runs': RUNS, 'points': NS,
                  'target': 'π/4 = 0.7853981633974483'},
         'vdc': vdc_table()}
    R['pi'] = pi_scan()
    R['conv'] = convergence(R['pi'])
    R['bars'] = error_bars(R['pi'])
    R['scatter'] = {'random': [list(p) for p in Q.random_points(256, 2, SEED + 13)],
                    'halton': [list(p) for p in Q.halton(256, 2)]}
    R['gaps'] = gap_scan()
    R['stuck'] = stuck()

    v = R['vdc']
    c = {row['key']: row['exponent'] for row in R['conv']}
    b = R['bars']
    s = R['stuck']
    checks = [
        ('前 16 个 van der Corput 值的第 1 个是 0.5', v['first16'][0] == 0.5),
        ('前 8 个点每个 1/8 格里恰好一个', v['one_per_cell']),
        ('随机点的收敛指数接近 0.5', 0.4 < c['random_rms'] < 0.6),
        ('抖动的 Halton 收敛指数明显高于随机',
         c['halton_shift_rms'] > c['random_rms'] + 0.2),
        ('最小的一批点：Halton 误差不到随机的五分之一',
         R['pi'][-1]['halton_shift_rms'] < R['pi'][-1]['random_rms'] / 5),
        ('随机点的误差分布与 RMS 同量级（2×RMS 之外不超过 1/5）',
         b['random_over_2rms'] < 0.2),
        ('N = 1024 时 Halton 原样的误差小于随机 RMS', b['halton_below_rms']),
        ('van der Corput 的最大空洞恰好等于 1/n',
         all(abs(row['vdc_gap'] - row['vdc_expected']) < 1e-12 for row in R['gaps'])),
        ('点数上千之后，随机点的最大空洞是 van der Corput 的六倍以上',
         all(row['ratio'] > 6 for row in R['gaps'] if row['n'] >= 256)),
        ('点数翻四倍而分子恰好翻四倍的对不止一个', len(s['quads']) >= 2),
        ('存在两个不同的点数给出同一个估计值', len(s['repeats']) >= 2),
        ('标称点数涨一倍，误差反而变大：8192 好于 16384',
         [r for r in s['rows'] if r['n'] == 8192][0]['err']
         < [r for r in s['rows'] if r['n'] == 16384][0]['err']),
    ]
    R['checks'] = [{'name': n, 'ok': bool(ok)} for n, ok in checks]
    R['selfcheck'] = all(x['ok'] for x in R['checks'])

    out = HERE / 'results.json'
    out.write_text(json.dumps(R, indent=1, ensure_ascii=False))
    print('wrote', out, out.stat().st_size, 'bytes')
    print('selfcheck', R['selfcheck'])
    for x in R['checks']:
        print('  ', 'OK ' if x['ok'] else 'BAD', x['name'])
    print('\nn     random_rms   strat_rms   halton_err  halton_shift_rms')
    for r in R['pi']:
        print('%6d %11.3e %11.3e %11.3e %11.3e' % (r['n'], r['random_rms'],
              r['stratified_rms'], r['halton_err'], r['halton_shift_rms']))
    print('\nexponents', {row['method']: round(row['exponent'], 3) for row in R['conv']})
    print('bars', {k: b[k] for k in ('random_rms', 'random_min', 'random_max',
                                     'random_over_2rms', 'halton_err', 'halton_over_2rms')})
    print('\ngaps: n  vdc_gap  expected  random_mean  log(n)/n  ratio')
    for r in R['gaps']:
        print('%7d %9.2e %9.2e %11.2e %9.2e %6.1f' % (r['n'], r['vdc_gap'],
              r['vdc_expected'], r['random_gap_mean'], r['log_over_n'], r['ratio']))
    print('\nstuck: n inside fraction err')
    for r in s['rows']:
        print('%7d %6d %.9f %.3e' % (r['n'], r['inside'], r['fraction'], r['err']))
    print('quads', s['quads'])
    print('repeats', s['repeats'])


if __name__ == '__main__':
    main()
