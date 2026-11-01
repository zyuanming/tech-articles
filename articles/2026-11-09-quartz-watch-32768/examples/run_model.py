#!/usr/bin/env python3
"""Measurements for the quartz-watch article. Writes results.json. MIT."""
from __future__ import annotations

import json
from pathlib import Path

import quartz as Q

HERE = Path(__file__).resolve().parent


def main() -> int:
    div = Q.divider()
    stage_rows = []
    for k, edges in enumerate(div['edges'], start=1):
        stage_rows.append(dict(stage=k, divide=2 ** k, hz=Q.F_CRYSTAL / 2 ** k,
                               edges=edges,
                               period_seconds=2 ** k / Q.F_CRYSTAL))

    # the parabola, sampled
    curve = []
    for t10 in range(-200, 701, 10):
        t = t10 / 10.0
        curve.append(dict(t=t, ppm=Q.ppm_error(t) * 1e6))

    # a month of drift, four ways
    days = 30
    scenarios = [
        ('恒温 25 °C（抛物线顶点）', Q.constant(25.0)),
        ('恒温 35 °C', Q.constant(35.0)),
        ('恒温 5 °C', Q.constant(5.0)),
        ('房间 23 °C，日夜摆 ±3 °C', Q.daily_swing(23.0, 3.0)),
        ('房间 28 °C，日夜摆 ±5 °C', Q.daily_swing(28.0, 5.0)),
    ]
    drift_rows = []
    cumulative = {}
    for name, profile in scenarios:
        per_day = Q.drift_seconds(profile, Q.DAY)
        per_month = Q.drift_seconds(profile, Q.MONTH)
        curve_days = []
        for d in range(days + 1):
            curve_days.append(round(Q.drift_seconds(profile, d * Q.DAY), 3))
        cumulative[name] = curve_days
        drift_rows.append(dict(name=name, per_day=round(per_day, 3),
                               per_month=round(per_month, 3),
                               per_year=round(Q.drift_seconds(profile, 365 * Q.DAY), 1)))

    ladder = Q.ladder()
    budget = Q.budget()
    pw = Q.power()

    # what a 1 s/month target demands, in ppm
    need_ppm = 1.0 / Q.MONTH * 1e6

    out = dict(
        crystal=dict(hz=Q.F_CRYSTAL, stages=Q.STAGES, power_of_two=2 ** Q.STAGES,
                     edges=div['edges'], out_hz=div['out_hz'],
                     high_seconds=div['high_seconds'],
                     cycles_day=Q.cycles_per(Q.DAY),
                     cycles_year=Q.cycles_per(365 * Q.DAY)),
        stages=stage_rows,
        turnover=Q.TURNOVER, quad=Q.QUAD,
        curve=curve,
        drift=drift_rows,
        cumulative=cumulative,
        budget=budget,
        budget_total_ppm=round(sum(b['ppm'] for b in budget), 2),
        budget_total_month=round(sum(b['per_month'] for b in budget), 2),
        ladder=ladder,
        power=pw,
        one_second_per_month_ppm=round(need_ppm, 3),
    )
    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('stages', [(r['stage'], r['hz']) for r in stage_rows][:4], '...',
          stage_rows[-1]['hz'])
    print('drift', [(r['name'], r['per_month']) for r in drift_rows])
    print('budget', [(b['name'], round(b['ppm'], 2), b['per_month'])
                     for b in budget], out['budget_total_month'])
    print('power', pw['total_ua'], 'uA', round(pw['life_years'], 2), 'years')
    print('1 s/month =', out['one_second_per_month_ppm'], 'ppm')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
