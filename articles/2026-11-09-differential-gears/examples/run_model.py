#!/usr/bin/env python3
"""Measurements for the differential article. Writes results.json. MIT."""
from __future__ import annotations

import json
from pathlib import Path

import diff as D

HERE = Path(__file__).resolve().parent

V = 50 / 3.6          # 50 km/h
MASS = 1400.0         # kg
TORQUE = 2730.0       # Nm at the axle, first gear, wide open


def main() -> int:
    rows = D.turn_table((5, 10, 15, 25, 50, 200), V)

    ratio_curve = []
    for r10 in range(40, 4010, 10):
        r = r10 / 10.0
        ratio_curve.append(dict(radius=r, ratio=D.gear_ratio(r)))

    path = D.Path([(40, 0.0), (23.6, 1 / 15), (30, 0.0),
                   (12.6, -1 / 8), (40, 0.0)], V)
    trace = path.trace()
    step = max(1, len(trace) // 220)
    slim = [dict(s=round(p['s'], 2), t=round(p['t'], 2),
                 left=round(p['left'], 2), right=round(p['right'], 2),
                 kappa=round(p['kappa'], 5)) for p in trace[::step]]

    cases = [
        ('两轮都在干沥青上', 0.90, 0.90),
        ('一侧湿滑', 0.90, 0.35),
        ('一侧结冰', 0.90, 0.10),
        ('一侧悬空（μ≈0）', 0.90, 0.01),
    ]
    tract = []
    for name, ml, mr in cases:
        t = D.traction(MASS, ml, mr, TORQUE, grade=0.0)
        g = D.traction(MASS, ml, mr, TORQUE, grade=0.10)
        tract.append(dict(name=name, mu_left=ml, mu_right=mr,
                          each=round(t['each'], 0), total=round(t['total'], 0),
                          accel=round(t['accel'], 2),
                          accel_grade=round(g['accel'], 2),
                          climbs=bool(g['climbs']),
                          grade_need=round(g['grade_force'], 0)))

    lsd_rows = []
    for bias in (1.0, 2.0, 2.5, 4.0):
        r = D.lsd(MASS, 0.90, 0.10, TORQUE, bias=bias)
        lsd_rows.append(dict(bias=bias, total=round(r['total'], 0),
                             accel=round(r['accel'], 2)))

    hop = D.hopkins(V, 15.0)

    # a 90 degree corner: how much one tyre would scrub if the axle were welded
    corner = []
    for r in (5, 8, 10, 15, 20):
        a = D.arc(r)
        corner.append(dict(radius=r, quarter_gap=a['gap'] / 4,
                           full_gap=a['gap']))

    out = dict(
        track=D.TRACK, wheel_d=D.WHEEL_D, circumference=D.CIRC,
        speed_kmh=50.0,
        turns=rows,
        ratio_curve=ratio_curve,
        path=dict(length=path.length, points=slim,
                  scrub=path.locked_scrub(),
                  left_m=round(trace[-1]['left_m'], 1),
                  right_m=round(trace[-1]['right_m'], 1),
                  seconds=round(trace[-1]['t'], 1)),
        corners=corner,
        traction=dict(mass=MASS, axle_torque=TORQUE, cases=tract),
        lsd=lsd_rows,
        hopkins=hop,
    )
    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('turn ratio @15 m:', round(rows[2]['ratio'], 3),
          'outer', round(rows[2]['outer_kmh'], 1), 'inner', round(rows[2]['inner_kmh'], 1))
    print('one circle gap:', round(rows[2]['gap_m'], 2), 'm;',
          'rev gap', round(rows[2]['rev_gap'], 2))
    print('path scrub:', {k: round(v, 2) for k, v in out['path']['scrub'].items()},
          'm over', round(path.length, 1), 'm')
    print('traction:', [(c['name'], c['total'], c['accel'], c['climbs'])
                        for c in tract])
    print('lsd:', [(r['bias'], r['total'], r['accel']) for r in lsd_rows])
    print('hopkins:', {k: round(v, 2) for k, v in hop.items()})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
