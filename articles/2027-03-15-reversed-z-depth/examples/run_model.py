"""跑一遍深度精度实验，把结果写进 results.json。

    python3 run_model.py

全部确定性，没有随机数。
"""
from __future__ import annotations

import json
import math

import depth as D

NEAR = 0.1
FAR = 1000.0


def steps_table(near_list, far, zs):
    rows = []
    for n in near_list:
        for z in zs:
            rows.append({
                'near': n,
                'far': far,
                'z': z,
                'fixed24': D.eye_grid(z, n, far, D.std_depth, D.q_fixed),
                'f32_std': D.eye_grid(z, n, far, D.std_depth, D.q_float),
                'f32_rev': D.eye_grid(z, n, far, D.rev_depth, D.q_float),
                'formula_std': (2.0 ** -24) * (far - n) * z * z / (far * n),
                'formula_rev': (2.0 ** -24) * z * (1.0 - z / far),
            })
    return rows


def near_sweep(ns, z, far):
    rows = []
    for n in ns:
        rows.append({
            'near': n,
            'z': z,
            'fixed24': D.eye_grid(z, n, far, D.std_depth, D.q_fixed),
            'formula': (2.0 ** -24) * (far - n) * z * z / (far * n),
            'd': D.std_depth(z, n, far),
        })
    return rows


def far_sweep(fars, n, z):
    rows = []
    for f in fars:
        rows.append({
            'far': f,
            'z': z,
            'fixed24': D.eye_grid(z, n, f, D.std_depth, D.q_fixed),
            'formula': (2.0 ** -24) * (f - n) * z * z / (f * n),
        })
    return rows


def main():
    out = {
        'meta': {
            'near': NEAR,
            'far': FAR,
            'depth_formats': {
                'fixed24': '定点，2^-24 均匀网格（24 位深度缓冲）',
                'f32_std': 'float32，标准 [0,1] 映射',
                'f32_rev': 'float32，反转映射（近平面 1，远平面 0）',
            },
            'q24': D.Q24,
        },
    }

    # 1. d(z) 与 s(z) 曲线，给图 01 / 07 用
    zs = D.log_depths(NEAR, FAR, 61)
    out['curve'] = [{'z': z,
                     'd_std': D.std_depth(z, NEAR, FAR),
                     'd_rev': D.rev_depth(z, NEAR, FAR),
                     'gl': D.gl_depth(z, NEAR, FAR)} for z in zs]

    # 2. 六个距离的深度值（手算表）
    out['depth_values'] = [{'z': z,
                            'd_std': D.std_depth(z, NEAR, FAR),
                            'd_rev': D.rev_depth(z, NEAR, FAR),
                            'share': D.std_depth(z, NEAR, FAR)} for z in
                           (0.1, 1.0, 10.0, 100.0, 500.0, 1000.0)]

    # 3. 分辨率表：near = 0.1，六个距离，三种格式
    out['steps'] = steps_table([NEAR], FAR, [1.0, 10.0, 100.0, 250.0, 500.0, 900.0])

    # 3b. near 三档 × 三个距离（避开 z = near 的退化点）
    out['near_steps'] = steps_table([0.1, 1.0, 10.0], FAR, [20.0, 100.0, 500.0])

    # 3c. 三条 near 的完整曲线，给 log-log 图用
    out['step_curves'] = []
    for n in (0.1, 1.0, 10.0):
        out['step_curves'].append({
            'near': n,
            'rows': [{'z': z, 'step': D.eye_grid(z, n, FAR, D.std_depth, D.q_fixed)}
                     for z in D.log_depths(n * 2.0, FAR * 0.95, 25)],
        })

    # 3d. 反转深度的曲线（float32），给对比图用
    out['rev_curve'] = [{'z': z, 'step': D.eye_grid(z, NEAR, FAR, D.rev_depth, D.q_float)}
                        for z in D.log_depths(1.0, FAR * 0.999, 30)]

    # 4. near 扫描（z = 500）
    out['near_sweep'] = near_sweep([0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0],
                                   500.0, FAR)

    # 5. far 扫描（z = 500，near = 0.1）
    out['far_sweep'] = far_sweep([600.0, 1000.0, 2000.0, 10000.0, 100000.0, 1e6], NEAR, 500.0)

    # 6. 两万个对数分布的距离，被压成同一格的对数
    zs = D.log_depths(NEAR, FAR, 20000)
    out['collapse'] = {
        'count': len(zs),
        'fixed24': dict(zip(('indist', 'swap'),
                            D.collapse_count(zs, NEAR, FAR, D.std_depth, D.q_fixed))),
        'f32_std': dict(zip(('indist', 'swap'),
                            D.collapse_count(zs, NEAR, FAR, D.std_depth, D.q_float))),
        'f32_rev': dict(zip(('indist', 'swap'),
                            D.collapse_count(zs, NEAR, FAR, D.rev_depth, D.q_float,
                                             decreasing=True))),
    }

    # 6b. 第一批被压成同一格的点出现在哪里
    vals = [D.q_fixed(D.std_depth(z, NEAR, FAR)) for z in zs]
    merged = [zs[i + 1] for i in range(len(zs) - 1) if vals[i] == vals[i + 1]]
    out['collapse']['merged_z'] = {
        'count': len(merged),
        'first': merged[0] if merged else None,
        'last': merged[-1] if merged else None,
        'median': merged[len(merged) // 2] if merged else None,
    }

    # 7. 相隔 sep 米的面，在什么距离上开始被压成同一个深度值
    def cell_thresholds(near, sep):
        return {
            'z_guarantee': D.z_for_cell(sep * 1.0, near, FAR, D.std_depth, D.q_fixed),
            'z_half': D.z_for_cell(sep * 2.0, near, FAR, D.std_depth, D.q_fixed),
            'z_all': D.z_for_cell(sep * 10.0, near, FAR, D.std_depth, D.q_fixed),
        }

    out['threshold'] = [dict(sep=sep, near=NEAR, **cell_thresholds(NEAR, sep))
                        for sep in (0.001, 0.01, 0.1, 1.0)]
    out['threshold_near'] = [dict(sep=0.01, near=n, **cell_thresholds(n, 0.01))
                             for n in (0.1, 1.0, 10.0)]
    out['merge_curves'] = [
        {'sep': sep,
         'rows': [{'z': z, 'p': D.merge_prob(z, sep, NEAR, FAR, D.std_depth, D.q_fixed)}
                  for z in D.log_depths(NEAR * 5, FAR * 0.999, 25)]}
        for sep in (0.001, 0.01, 0.1, 1.0)
    ]

    # 7b. 反转深度不单调：扫一遍找最差的距离
    scan = []
    for z in D.log_depths(max(NEAR * 10, 1.0), FAR * 0.999, 40):
        scan.append({'z': z, 'step': D.eye_grid(z, NEAR, FAR, D.rev_depth, D.q_float)})
    worst = max(scan, key=lambda r: r['step'])
    out['rev_worst'] = {'scan': scan, 'z': worst['z'], 'step': worst['step']}

    # 8. 「事后 1 − d」的坑：同样一批点，矩阵直接算 vs 算完再做减法
    zs = [-(100.0 + i * 0.001) for i in range(1000)]
    std = [p[1] for p in D.pipeline_pair(0.0, NEAR, 10000.0, zs)]
    trap = [None if v is None else D.f32(1.0 - v) for v in std]
    rev = [p[1] for p in D.pipeline_pair(0.0, NEAR, 10000.0, zs, reverse=True)]
    out['subtract_after'] = {
        'count': len(zs),
        'z0': 100.0,
        'far': 10000.0,
        'separation': 0.001,
        'trap': dict(zip(('indist', 'swap'), D.order_errors(trap, decreasing=True))),
        'matrix': dict(zip(('indist', 'swap'), D.order_errors(rev, decreasing=True))),
        'trap_mask': [int(a is not None and b is not None and a == b)
                      for a, b in zip(trap, trap[1:])],
        'matrix_mask': [int(a is not None and b is not None and a == b)
                        for a, b in zip(rev, rev[1:])],
    }

    # 9. 预乘 view·projection 与分开乘
    out['premultiply'] = {}
    for name, rev in (('standard', False), ('reversed', True)):
        rows = []
        for sep in (0.5, 0.2, 0.05):
            # 世界坐标取负号，让第 i 个点的距离随 i 增大
            zs = [-(i * sep) for i in range(1000)]
            pairs = D.pipeline_pair(1000.0, NEAR, 10000.0, zs, reverse=rev)
            a = [p[0] for p in pairs]
            b = [p[1] for p in pairs]
            rows.append({
                'sep': sep,
                'premultiplied': dict(zip(('indist', 'swap'),
                                          D.order_errors(a, decreasing=rev))),
                'separate': dict(zip(('indist', 'swap'),
                                     D.order_errors(b, decreasing=rev))),
            })
        out['premultiply'][name] = {'camera_z': 1000.0, 'far': 10000.0, 'rows': rows}

    # 自检
    ok = True
    ok &= abs(D.std_depth(NEAR, NEAR, FAR)) < 1e-12
    ok &= abs(D.std_depth(FAR, NEAR, FAR) - 1.0) < 1e-12
    ok &= abs(D.rev_depth(NEAR, NEAR, FAR) - 1.0) < 1e-12
    ok &= abs(D.rev_depth(FAR, NEAR, FAR)) < 1e-12
    # 标准映射的 float32 分辨率与定点在六个点上应当完全相同
    for row in out['steps']:
        if row['near'] == NEAR:
            ok &= abs(row['fixed24'] - row['f32_std']) <= row['fixed24'] * 1e-6
    out['selfcheck'] = bool(ok)

    with open('results.json', 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write('\n')

    print('near=%.2f far=%.0f' % (NEAR, FAR))
    for row in out['steps']:
        print('n=%-5.2f z=%-6.1f fixed24=%.4g f32std=%.4g f32rev=%.4g' %
              (row['near'], row['z'], row['fixed24'], row['f32_std'], row['f32_rev']))
    print('collapse', out['collapse'])
    for row in out['threshold']:
        print('threshold sep=%.3g 保证分开到 %.1f 米 / 一半 %.1f 米 / 全并 %.1f 米' %
              (row['sep'], row['z_guarantee'], row['z_half'], row['z_all']))
    print('subtract_after trap=%s matrix=%s count=%d' %
          (out['subtract_after']['trap'], out['subtract_after']['matrix'],
           out['subtract_after']['count']))
    print('selfcheck', out['selfcheck'])


if __name__ == '__main__':
    main()
