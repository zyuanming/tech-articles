#!/usr/bin/env python3
"""Run every experiment the article quotes and write results.json.

Standard library only. Nothing is hard-coded: the prose and the figures both
read the JSON this produces.
"""
from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

import floats as F

HERE = Path(__file__).resolve().parent


def clean(value):
    """JSON cannot hold Fraction, NaN or Infinity. Make them readable strings."""
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value):
            return 'NaN'
        if math.isinf(value):
            return 'Infinity' if value > 0 else '-Infinity'
        return value
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    return value


def main() -> None:
    n = F.article_numbers()
    out = {
        'sum': {
            'a': 0.1, 'b': 0.2, 'c': 0.3,
            'repr': n['sum_repr'], 'hex': n['sum_hex'], 'three_hex': n['three_hex'],
            'equals': (0.1 + 0.2) == 0.3,
            'difference': n['difference'],
            'difference_ulps': n['difference_ulps'],
            'ulp_of_0_3': F.ulp(0.3),
            'bits_a': F.bitstring(0.1),
            'bits_b': F.bitstring(0.2),
            'bits_sum': F.bitstring(0.1 + 0.2),
            'bits_c': F.bitstring(0.3),
            'exact_sum_decimal': n['exact_sum_decimal'],
            'rounded_decimal': n['rounded_decimal'],
            'three_decimal': n['three_decimal'],
            'one_tenth_decimal': n['one_tenth_exact'],
            'trace': F.addition_trace(0.1, 0.2),
        },
        'binary': {
            'tenth': n['tenth_binary'],
            'quarter': n['one_fourth_binary'],
            'third': n['one_third_binary'],
            'half': F.long_division(1, 2, 20),
            'fifth': F.long_division(1, 5, 20),
            'eighth': F.long_division(1, 8, 20),
        },
        'exactness': F.exactness_table(),
        'powers': F.power_gallery(),
        'layout': {
            'sign_bits': F.SIGN_BITS, 'exponent_bits': F.EXP_BITS,
            'fraction_bits': F.FRAC_BITS, 'bias': F.BIAS,
            'decode_tenth': F.decode(0.1),
            'decode_one': F.decode(1.0),
            'decode_half': F.decode(0.5),
        },
        'spacing': {
            'profile': [dict(value=v['value'], ulp=v['ulp'], exponent=v['exponent'])
                        for v in F.gap_profile(0.5, 4096.0, 9)],
            'neighbours_of_one': F.neighbours(1.0, 3),
            'neighbours_of_tenth': F.neighbours(0.1, 3),
            'ulp_table': [dict(value=v, ulp=F.ulp(v)) for v in
                          (1e-300, 1e-10, 1.0, 1000.0, 1e6, 1e12, 1e16, 1e100)],
        },
        'big_eats_small': {**n['big_eats_small'],
                           'chain': [dict(n=k, value=1e16 + k, changed=1e16 + k != 1e16)
                                     for k in (1, 2, 3, 4, 5)]},
        'cancellation': [
            {'x': c['x'], 'naive': c['naive'], 'stable': c['stable'],
             'reference': c['reference'],
             'relative_error': float(c['relative_error']),
             'relative_error_stable': float(c['relative_error_stable']),
             'good_digits': c['good_digits'],
             'good_digits_stable': c['good_digits_stable']}
            for c in n['cancellation']],
        'quadratic': n['quadratic'],
        'accumulation': {
            'n': n['accumulation']['n'],
            'value': n['accumulation']['value'],
            'truth': n['accumulation']['truth'],
            # The exact total of 100000 copies of fl(0.1) is not a double --
            # it is 10000 + 5.55e-13 -- so record the Fraction itself.
            # float() would round it to 10000.0 and lose the whole point.
            'exact': str(n['accumulation']['exact_fraction']),
            'rows': [dict(name=r['name'], got=r['got'],
                          error=float(r['error']), ulps=float(r['ulps']))
                     for r in n['accumulation']['rows']],
        },
        'mixed': {
            'seed': n['mixed']['seed'], 'count': n['mixed']['count'],
            'exact': str(n['mixed']['exact_fraction']),
            'rows': [dict(name=r['name'], got=r['got'], error=float(r['error']))
                     for r in n['mixed']['rows']],
        },
        'special': F.special_values(),
        'nan': n['nan'],
        'subnormal': n['subnormal'],
        'float32': n['float32_of_tenth'],
        'fast_inverse_sqrt': n['fast_inv'],
        'rounding': F.rounding_demo(),
        'tolerance': n['tolerance'],
        'drift': [dict(n=k, naive=F.sum_naive([0.1] * k), kahan=F.sum_kahan([0.1] * k),
                       truth=k / 10.0)
                  for k in (10, 100, 1000, 10000, 100000)],
        'rounding_tie': F.rounding_tie(),
        'binary_steps': F.long_division_steps(1, 10, 10),
        # The first 60 bits of 1/10's expansion: figure 5 shows the 53 that
        # survive and the tail that gets rounded away.
        'tenth_expansion': ''.join(str(s['digit'])
                                   for s in F.long_division_steps(1, 10, 60)),
        'drift_curve': F.drift_curve(),
        'one_tenth_times': [dict(n=k, value=0.1 * k, exact=k / 10.0,
                                 equal=(0.1 * k) == k / 10.0)
                            for k in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)],
    }
    (HERE / 'results.json').write_text(
        json.dumps(clean(out), ensure_ascii=False, indent=2) + '\n')
    print('0.1 + 0.2 =', repr(0.1 + 0.2))
    print('0.1 + 0.2 == 0.3 ->', (0.1 + 0.2) == 0.3)
    print('difference      =', out['sum']['difference'], 'ulp')
    print('ulp(0.3)        =', out['sum']['ulp_of_0_3'])
    print('0.1 stored as   =', out['sum']['one_tenth_decimal'])
    print('1/10 in binary  = 0.' + out['binary']['tenth']['digits'],
          'cycle at', out['binary']['tenth']['cycle_at'],
          'period', out['binary']['tenth']['period'])
    print('1e16 + 1 == 1e16 ->', out['big_eats_small']['equal'],
          ' ulp(1e16) =', out['big_eats_small']['ulp'])
    for r in out['accumulation']['rows']:
        print('  sum 0.1 x100000 %-14s %r  err %+.3e' % (r['name'], r['got'], r['error']))
    for r in out['mixed']['rows']:
        print('  mixed sum      %-14s err %+.3e' % (r['name'], r['error']))
    for c in out['cancellation']:
        print('  1-cos(%.0e) naive %r (%.2f digits)  stable %r (%.2f digits)'
              % (c['x'], c['naive'], c['good_digits'] or 0, c['stable'],
                 c['good_digits_stable']))
    q = out['quadratic']
    print('  quadratic naive small root %r, stable %r, true 1e-8'
          % (q['naive'][1], q['stable'][1]))
    f = out['fast_inverse_sqrt']
    print('  fast inverse sqrt(0.5):', [repr(v) for v in f['steps']],
          'truth', f['truth'])
    print('  float32(0.1) =', out['float32']['float32'], out['float32']['hex'])
    print('  writes results.json')


if __name__ == '__main__':
    main()
