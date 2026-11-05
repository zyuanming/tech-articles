"""算出 read.md 里用到的每个数，写进 results.json。

python3 run_model.py
"""

import json
import math
import pathlib

import bres

HERE = pathlib.Path(__file__).resolve().parent


def main():
    out = {}

    out['meta'] = {
        'algorithm': 'Bresenham 1965（直线） / Bresenham 1977（中点圆）',
        'arithmetic': '整数加减与比较；DDA 对照用 float64',
        'seed': 20270329,
        'segments': 4000,
    }

    # ---------------------------------------------------------------- 手算
    x0, y0, x1, y1 = 0, 0, 10, 4
    trace = bres.err_trace(x0, y0, x1, y1)
    px = bres.bresenham(x0, y0, x1, y1)
    out['hand'] = {
        'from': [x0, y0], 'to': [x1, y1],
        'dx': x1 - x0, 'dy': y1 - y0,
        'd0': 2 * (y1 - y0) - (x1 - x0),
        'steps': [[k, d, mark] for (k, d, mark) in trace],
        'pixels': px,
        'ideal_at': [[k, y0 + k * (y1 - y0) / float(x1 - x0)] for k in range(x1 - x0 + 1)],
    }

    # ------------------------------------------------- 与浮点 DDA 的逐像素对照
    segs = bres.rand_segments(4000)
    diff_segs = 0
    diff_pixels = 0
    tie_diff = 0
    examples = []
    bucket = {}
    for (ax, ay, bx, by) in segs:
        b = bres.bresenham(ax, ay, bx, by)
        d = bres.dda_round(ax, ay, bx, by)
        major = max(abs(bx - ax), abs(by - ay))
        bucket.setdefault(major, [0, 0])
        bucket[major][0] += 1
        if set(b) != set(d):
            diff_segs += 1
            delta = len(set(b) ^ set(d)) // 2
            diff_pixels += delta
            bucket[major][1] += 1
            # 两个像素集合的差，是不是各自都恰好落在理想线的半整数上
            on_half = True
            for (qx, qy) in sorted(set(b) ^ set(d)):
                if abs(bx - ax) >= abs(by - ay):
                    v = ay + (qx - ax) * (by - ay) / float(bx - ax)
                    if abs(abs(v - int(math.floor(v))) - 0.5) > 1e-9:
                        on_half = False
                else:
                    v = ax + (qy - ay) * (bx - ax) / float(by - ay)
                    if abs(abs(v - int(math.floor(v))) - 0.5) > 1e-9:
                        on_half = False
            if on_half:
                tie_diff += 1
            if len(examples) < 5 and delta == 1:
                examples.append({'seg': [ax, ay, bx, by],
                                 'bresenham_only': sorted(set(b) - set(d)),
                                 'dda_only': sorted(set(d) - set(b)),
                                 'major': major})
    out['compare'] = {
        'segments': len(segs),
        'differing_segments': diff_segs,
        'differing_share': diff_segs / float(len(segs)),
        'differing_pixels_total': diff_pixels,
        'differing_on_exact_half': tie_diff,
        'examples': examples,
        'by_major': sorted([{'major': k, 'n': v[0], 'diff': v[1]}
                            for k, v in bucket.items()], key=lambda r: r['major']),
        'odd_major_diffs': sum(v[1] for k, v in bucket.items() if k % 2 == 1),
        'even_major_diffs': sum(v[1] for k, v in bucket.items() if k % 2 == 0),
        'even_major_segments': sum(v[0] for k, v in bucket.items() if k % 2 == 0),
    }

    # ------------------------------------------------------------ 偏离多远
    worst_int = 0.0
    worst_int_seg = None
    worst_cen = 0.0
    worst_cen_seg = None
    hist = [0] * 12
    for (ax, ay, bx, by) in segs:
        pts = bres.bresenham(ax, ay, bx, by)
        a = bres.dev_integer(pts, ax, ay, bx, by)
        b = bres.dev_center(pts, ax, ay, bx, by)
        if a > worst_int:
            worst_int, worst_int_seg = a, [ax, ay, bx, by]
        if b > worst_cen:
            worst_cen, worst_cen_seg = b, [ax, ay, bx, by]
        hist[min(11, int(b * 20))] += 1
    out['deviation'] = {
        'integer_max': worst_int, 'integer_max_seg': worst_int_seg,
        'center_max': worst_cen, 'center_max_seg': worst_cen_seg,
        'center_hist': [{'bin': i / 20.0, 'n': hist[i]} for i in range(12)],
    }

    # ------------------------------------------------------- 斜率扫描
    scan = []
    for k in range(0, 65):
        seg = (0, 0, 64, k)
        pts = bres.bresenham(*seg)
        scan.append({'k': k, 'slope': k / 64.0,
                     'integer': bres.dev_integer(pts, *seg),
                     'center': bres.dev_center(pts, *seg)})
    out['slope_scan'] = scan

    # 反向画：同一条线换方向画，像素集合是否一样
    same = 0
    rev_delta = {}
    revs = bres.rand_segments(600, seed=7)
    for (ax, ay, bx, by) in revs:
        a = set(bres.bresenham(ax, ay, bx, by))
        b = set(bres.bresenham(bx, by, ax, ay))
        if a == b:
            same += 1
        else:
            delta = len(a ^ b) // 2
            rev_delta[delta] = rev_delta.get(delta, 0) + 1
    out['reverse'] = {'tested': len(revs), 'identical': same,
                      'differ_share': 1 - same / float(len(revs)),
                      'by_delta': sorted([{'delta': k, 'n': v}
                                          for k, v in rev_delta.items()],
                                         key=lambda r: r['delta'])}

    # -------------------------------------------------------------- 中点圆
    rows = []
    for r in range(3, 65):
        mid = bres.midpoint_circle(r)
        ref = bres.circle_round(r)
        radial = [abs(math.hypot(x, y) - r) for (x, y) in mid]
        rows.append({
            'r': r,
            'pixels': len(mid),
            'circumference': 2 * math.pi * r,
            'ratio': len(mid) / (2 * math.pi * r),
            'max_radial_error': max(radial),
            'mean_radial_error': sum(radial) / len(radial),
            'vs_round_diff': len(set(mid) ^ set(ref)) // 2,
        })
    out['circle'] = rows

    r = 13
    octant = []
    x, y = 0, r
    d = 1 - r
    while x <= y:
        octant.append([x, y])
        x += 1
        if d < 0:
            d += 2 * x + 1
        else:
            y -= 1
            d += 2 * (x - y) + 1
    out['octant'] = {'r': r, 'first': octant, 'total': len(bres.midpoint_circle(r)),
                     'inside_radius': len([p for p in bres.midpoint_circle(r)]),
                     'arc_share': len(octant) / float(len(bres.midpoint_circle(r)))}

    # -------------------------------------------------------- 运算次数（静态）
    out['ops'] = [dict(bres.ops_breakdown(0, 0, n, int(n * 0.37)), length=n)
                  for n in (10, 100, 1000, 10000)]

    # ------------------------------------------------------------ 抗锯齿
    wx0, wy0, wx1, wy1 = 0, 0, 12, 5
    cov = bres.wu_coverage(wx0, wy0, wx1, wy1)
    out['wu'] = {
        'seg': [wx0, wy0, wx1, wy1],
        'pixels': [[pt[0], pt[1], c] for pt, c in sorted(cov)],
        'bresenham': bres.bresenham(wx0, wy0, wx1, wy1),
        'levels_nonzero': len({c for _, c in cov if c}),
    }

    # ---------------------------------------------------------------- 自检
    checks = []
    checks.append(('10x4 的线段有 11 个像素', len(out['hand']['pixels']) == 11))
    checks.append(('D 的首值是 2dy-dx', out['hand']['d0'] == 2 * 4 - 10))
    checks.append(('整数坐标下的偏差不超过半个像素',
                   out['deviation']['integer_max'] <= 0.5 + 1e-12))
    checks.append(('奇长度主轴从不与四舍五入分歧',
                   out['compare']['odd_major_diffs'] == 0))
    checks.append(('反方向画大部分相同但确有差异',
                   0.6 < out['reverse']['identical'] / float(out['reverse']['tested']) < 0.75))
    checks.append(('像素中心度量比整数度量更大',
                   out['deviation']['center_max'] > out['deviation']['integer_max']))
    checks.append(('中点圆的径向误差小于 1', max(
        r['max_radial_error'] for r in out['circle']) < 1.0))
    checks.append(('第一八分圆占全圆的八分之一左右',
                   0.10 < out['octant']['arc_share'] < 0.16))
    out['selfcheck'] = all(v for _, v in checks)
    out['checks'] = [{'what': w, 'ok': bool(v)} for w, v in checks]

    path = HERE / 'results.json'
    path.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
    print('wrote', path, path.stat().st_size, 'bytes')
    print('selfcheck', out['selfcheck'])
    for w, v in checks:
        if not v:
            print('  FAIL', w)


if __name__ == '__main__':
    main()
