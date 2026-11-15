#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""二次 de Casteljau 插值与权重展开的可复算例子。不联网、不绘图。"""
from pathlib import Path
import argparse, json, platform


def lerp(a, b, t):
    """线性插值：t=0 在 a，t=1 在 b。"""
    return (a[0] * (1 - t) + b[0] * t, a[1] * (1 - t) + b[1] * t)


def quadratic_casteljau(p0, p1, p2, t):
    """三层插值：P0P1→A、P1P2→B、AB→C。"""
    a = lerp(p0, p1, t)
    b = lerp(p1, p2, t)
    c = lerp(a, b, t)
    return dict(t=t, a=a, b=b, c=c)


def quadratic_polynomial(p0, p1, p2, t):
    """展开后的权重：C(t)=(1−t)²P₀+2t(1−t)P₁+t²P₂。"""
    w = ((1 - t) ** 2, 2 * t * (1 - t), t ** 2)
    x = w[0] * p0[0] + w[1] * p1[0] + w[2] * p2[0]
    y = w[0] * p0[1] + w[1] * p1[1] + w[2] * p2[1]
    return dict(t=t, weights=w, weight_sum=sum(w), point=(x, y))


def inside_hull(curve, hull):
    """三角形凸包判定：用三条边的同侧符号，不引入第三方库。"""
    def side(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    signs = []
    for x in curve:
        s = [side(hull[i], hull[(i + 1) % 3], x) for i in range(3)]
        negative = any(v < -1e-12 for v in s)
        positive = any(v > 1e-12 for v in s)
        signs.append(not (negative and positive))
    return all(signs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out)
    if out.exists() and any(out.iterdir()):
        raise SystemExit('输出目录须为空或不存在')
    out.mkdir(parents=True, exist_ok=True)

    p0, p1, p2 = (0.0, 0.0), (2.0, 4.0), (6.0, 0.0)
    half = quadratic_casteljau(p0, p1, p2, 0.5)
    poly_half = quadratic_polynomial(p0, p1, p2, 0.5)

    # 同一比例必须三层共用；换一个比例会离开这条曲线。
    mixed = lerp(lerp(p0, p1, 0.5), lerp(p1, p2, 0.5), 0.75)
    same_t_curve = [
        quadratic_casteljau(p0, p1, p2, i / 100)['c'] for i in range(101)
    ]

    # SVG 的 Q 命令：Q 2 4 6 0 与本文三个点同值。
    q_command = dict(command='Q 2 4 6 0', control=p1, end=p2,
                     matches_article_points=(p1 == (2.0, 4.0) and p2 == (6.0, 0.0)))

    result = dict(
        environment=dict(python=platform.python_version(), libraries='仅在标准库内实现'),
        points=dict(p0=p0, p1=p1, p2=p2),
        t_half=dict(
            casteljau=half,
            polynomial=poly_half,
            coordinates_agree=abs(half['c'][0] - poly_half['point'][0]) < 1e-12
            and abs(half['c'][1] - poly_half['point'][1]) < 1e-12,
        ),
        dt_equals_dp=dict(
            note='t 均匀走，弧长不保证均匀：0→0.25 与 0.25→0.5 的弦长比较',
            chord_0_025=((same_t_curve[25][0] - same_t_curve[0][0]) ** 2
                         + (same_t_curve[25][1] - same_t_curve[0][1]) ** 2) ** 0.5,
            chord_025_05=((same_t_curve[50][0] - same_t_curve[25][0]) ** 2
                          + (same_t_curve[50][1] - same_t_curve[25][1]) ** 2) ** 0.5,
        ),
        mixed_ratio=dict(note='第三次换比例就离开同一条曲线', point=mixed,
                         on_curve=abs(mixed[0] - 2.5) < 1e-12 and abs(mixed[1] - 2) < 1e-12),
        hull=dict(curve_samples=len(same_t_curve),
                  all_inside=inside_hull(same_t_curve, (p0, p1, p2))),
        svg=q_command,
    )

    assert half['a'] == (1.0, 2.0) and half['b'] == (4.0, 2.0) and half['c'] == (2.5, 2.0)
    assert poly_half['weights'] == (0.25, 0.5, 0.25) and poly_half['weight_sum'] == 1.0
    assert result['t_half']['coordinates_agree']
    assert result['hull']['all_inside']
    assert not result['mixed_ratio']['on_curve']

    (out / 'results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['t_half'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
