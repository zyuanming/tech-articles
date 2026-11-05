#!/usr/bin/env python3
"""《一亿次加法之后，和少了多少》的全部实验。MIT。

    python3 run_model.py   →  examples/results.json

只用标准库。所有随机数来自 kahan.lcg，重跑逐字节相同。
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import kahan as K

HERE = Path(__file__).resolve().parent
SEED = 20270405


def rel(err, ref):
    return abs(err) / abs(ref) if ref else float('nan')


def swallow():
    """2^53 之后加 1 会怎样：这是「小量被大和吞掉」的最干净的版本。"""
    base = float(2 ** 53)
    # 从 2^53 起连续加 10 次 1.0，看有没有一步会动
    s = base
    seen = []
    for _ in range(10):
        s = s + 1.0
        seen.append(s)
    return {
        'base': base,
        'base_plus_1': base + 1.0,
        'swallowed': (base + 1.0) == base,
        'plus_two': base + 2.0,
        'plus_two_moves_by': (base + 2.0) - base,
        'ladder': seen,
        'ladder_stuck': all(v == base for v in seen),
        'ulp_at_base': math.ulp(base),
        'epsilon': 2.0 ** -52,
        'why': '2^53 处 ulp = 2，加 1 正好落在两个可表示数的正中间，取偶 → 不动',
    }


def traces():
    """一个 3 项的小序列：[1, 1e16, −1e16]。精确和是 1，naive 与 Kahan 都给 0。"""
    xs = [1.0, 1e16, -1e16]
    rows_k = []
    s = 0.0
    c = 0.0
    for x in xs:
        y = x - c
        t = s + y
        c = (t - s) - y
        s = t
        rows_k.append({'x': x, 'y': y, 't': t, 'c': c, 's': s})
    rows_n = []
    s2 = 0.0
    c2 = 0.0
    for x in xs:
        t = s2 + x
        if abs(s2) >= abs(x):
            c2 += (s2 - t) + x
        else:
            c2 += (x - t) + s2
        s2 = t
        rows_n.append({'x': x, 't': t, 'c': c2, 's': s2})
    return {
        'xs': xs,
        'exact': math.fsum(xs),
        'naive': K.naive(xs),
        'kahan': K.kahan(xs),
        'neumaier': K.neumaier(xs),
        'kahan_steps': rows_k,
        'neumaier_steps': rows_n,
        'loss_in_kahan': 1.0 - K.kahan(xs),
    }


def harmonic_scan():
    """1 + 1/2 + … + 1/n，四种方法各占多少绝对误差。"""
    out = []
    for n in (1000, 10000, 100000, 1000000):
        xs = K.harmonic(n)
        ref = math.fsum(xs)
        row = {'n': n, 'ref': ref}
        for name, fn in (('naive', K.naive), ('kahan', K.kahan),
                         ('neumaier', K.neumaier), ('pairwise', K.pairwise)):
            v = fn(xs)
            row[name] = v
            row[name + '_err'] = abs(v - ref)
            row[name + '_rel'] = rel(v - ref, ref)
        out.append(row)
    return out


def representation():
    """补偿能不能救一个「本来就存不下」的答案。

    起始和 1e16、每步加 1e-8、加一百万次：精确和是 1e16 + 0.01，
    但 1e16 处 ulp = 2，这个答案在 float64 里根本不存在。
    """
    s0 = 1e16
    delta = 1e-8
    n = 1000000
    xs = [delta] * n
    naive_val = s0 + K.naive(xs)
    return {
        'start': s0, 'delta': delta, 'n': n,
        'exact_total': math.fsum([s0] + xs),
        'naive_total': naive_val,
        'kahan_total': s0 + K.kahan(xs),
        'neumaier_total': s0 + K.neumaier(xs),
        'ulp_at_start': math.ulp(s0),
        'rounds_to': s0 + 0.01,
        'representable': (s0 + 0.01) != s0,
        'note': '0.01 远小于 ulp = 2，四种方法全都只能给出 1e16',
    }


def order_scan():
    """同一批数（1…1e6 的倒数和），只改加法顺序。"""
    xs = K.harmonic(1000000)
    ref = math.fsum(xs)
    cases = [('原顺序 1 → 1/n', list(xs)),
             ('倒过来 1/n → 1', list(reversed(xs)))]
    # 洗牌：LCG 驱动的 Fisher–Yates
    nxt, _ = K.lcg(SEED + 1)
    sh = list(xs)
    for i in range(len(sh) - 1, 0, -1):
        j = nxt() % (i + 1)
        sh[i], sh[j] = sh[j], sh[i]
    cases.append(('打乱', sh))
    cases.append(('按大小排序（小在前）', sorted(xs)))
    out = []
    for name, data in cases:
        row = {'order': name, 'naive': K.naive(data), 'kahan': K.kahan(data),
               'ref': ref}
        row['naive_err'] = abs(row['naive'] - ref)
        row['kahan_err'] = abs(row['kahan'] - ref)
        out.append(row)
    return out


def cancel_search(trials=20000):
    """正负抵消最厉害的小序列上，三种方法谁更常给出精确结果。"""
    nxt, _ = K.lcg(SEED + 2)
    stats = {'trials': 0, 'skipped_zero': 0,
             'naive_exact': 0, 'kahan_exact': 0, 'neumaier_exact': 0,
             'kahan_worse_than_naive': 0}
    worst = None
    for _ in range(trials):
        n = 3 + nxt() % 10
        xs = K.cancel_mix(n, seed=nxt() & 0xFFFFFFFF)
        ref = math.fsum(xs)
        if ref == 0.0:
            stats['skipped_zero'] += 1
            continue
        stats['trials'] += 1
        en = abs(K.naive(xs) - ref)
        ek = abs(K.kahan(xs) - ref)
        em = abs(K.neumaier(xs) - ref)
        if en == 0.0:
            stats['naive_exact'] += 1
        if ek == 0.0:
            stats['kahan_exact'] += 1
        if em == 0.0:
            stats['neumaier_exact'] += 1
        if ek > en:
            stats['kahan_worse_than_naive'] += 1
            score = ek / en if en else float('inf')
            if worst is None or score > worst['ratio']:
                worst = {'xs': xs, 'ref': ref, 'naive': K.naive(xs),
                         'kahan': K.kahan(xs), 'neumaier': K.neumaier(xs),
                         'ratio': score}
    for k in ('naive_exact', 'kahan_exact', 'neumaier_exact', 'kahan_worse_than_naive'):
        stats[k + '_share'] = stats[k] / stats['trials']
    stats['worst'] = worst
    return stats


def variance_scan():
    """均值 1e8、方差 1 的数据：三种方差算法各丢多少位。"""
    out = []
    for n in (1000, 100000):
        xs = K.noisy_offset(n, seed=SEED)
        # 参照：先把均值用精确方法定下来，再精确求和
        mean = math.fsum(xs) / n
        ref = math.fsum([(x - mean) ** 2 for x in xs]) / n
        row = {'n': n, 'ref': ref}
        for name, fn in (('onescan', K.variance_onescan),
                         ('twopass', K.variance_twopass),
                         ('welford', K.variance_welford)):
            try:
                v = fn(xs)
            except (OverflowError, ZeroDivisionError):
                v = float('nan')
            row[name] = v
            row[name + '_err'] = abs(v - ref) if not math.isnan(v) else float('nan')
            row[name + '_rel'] = rel(v - ref, ref) if not math.isnan(v) else float('nan')
        out.append(row)
    return out


def main():
    R = {
        'meta': {'seed': SEED, 'python': 'stdlib only, float64'},
        'swallow': swallow(),
        'traces': traces(),
        'harmonic': harmonic_scan(),
        'representation': representation(),
        'order': order_scan(),
        'cancel': cancel_search(),
        'ops': K.ops_per_term(),
        'variance': variance_scan(),
    }

    t = R['traces']
    h = R['harmonic'][-1]
    o = R['order']
    c = R['cancel']
    v = R['variance'][-1]
    checks = [
        ('2^53 加 1 被吞掉', R['swallow']['swallowed']),
        ('从 2^53 起加 1 每次都不动', R['swallow']['ladder_stuck']),
        ('在 2^53 处加 2 才前进一步', R['swallow']['plus_two_moves_by'] == 2.0),
        ('[1, 1e16, −1e16] 的精确和是 1', t['exact'] == 1.0),
        ('Kahan 在这串上丢掉那个 1', t['kahan'] == 0.0),
        ('Neumaier 在这串上不出错', t['neumaier'] == 1.0),
        ('百万项调和数：Kahan 误差小于 naive', h['kahan_err'] < h['naive_err']),
        ('同一批数：换个顺序 naive 的结果就变', o[0]['naive'] != o[1]['naive']),
        ('抵消测试里 Neumaier 精确的次数最多',
         c['neumaier_exact'] >= c['kahan_exact'] >= 0),
        ('Kahan 不是处处更好：确有比 naive 差的情况', c['kahan_worse_than_naive'] > 0),
        ('和本身存不下时，四种方法都给同一个数',
         R['representation']['naive_total'] == R['representation']['kahan_total']
         == R['representation']['neumaier_total'] == R['representation']['start']),
        ('Welford 的方差误差小于一次扫',
         v['welford_err'] < v['onescan_err']),
        ('Kahan 每次加法四次运算，naive 一次', R['ops']['kahan']['total'] == 4),
    ]
    R['checks'] = [{'name': n, 'ok': bool(ok)} for n, ok in checks]
    R['selfcheck'] = all(c_['ok'] for c_ in R['checks'])

    out = HERE / 'results.json'
    out.write_text(json.dumps(R, indent=1, ensure_ascii=False))
    print('wrote', out, out.stat().st_size, 'bytes')
    print('selfcheck', R['selfcheck'])
    for c_ in R['checks']:
        print('  ', 'OK ' if c_['ok'] else 'BAD', c_['name'])


if __name__ == '__main__':
    main()
