#!/usr/bin/env python3
"""Measurements for the elevator governor article. Writes results.json. MIT."""
from __future__ import annotations

import json
from pathlib import Path

import elevator as E

HERE = Path(__file__).resolve().parent


def main() -> int:
    gov = {
        'rated': E.RATED, 'trip': E.TRIP, 'factor': E.TRIP_FACTOR,
        'sheave_r': E.SHEAVE_R, 'pawl_m': E.PAWL_M, 'pawl_r': E.PAWL_R,
        'spring': E.SPRING, 'trip_check': E.trip_speed(),
        'at_trip': E.governor(E.TRIP),
        'at_rated': E.governor(E.RATED),
        'tolerance': E.governor_tolerance(),
    }

    # two scenarios: drive fails at rated speed, and a free fall from rest
    fast, fast_trace = E.simulate(v0=E.RATED)
    drop, drop_trace = E.simulate(v0=0.0)

    # a slower brake for a high-speed lift is another article; here only 3..12
    stops = E.stop_table(fast['v_brake'], decels=(3, 6, 9, 12))
    clamp = E.clamp_force(fast['v_brake'], 6.0)

    wedges = E.wedge_curve()
    main_wedge = E.wedge(6.0)
    alt = [E.wedge(a) for a in (4.0, 6.0, 8.0, 10.0)]

    out = dict(
        governor=gov,
        scenarios=dict(
            from_rated=dict(summary={k: v for k, v in fast.items()},
                            trace=fast_trace),
            from_rest=dict(summary={k: v for k, v in drop.items()},
                           trace=drop_trace),
        ),
        stops=stops,
        clamp=clamp,
        wedge=dict(main=main_wedge, curve=wedges, alt=alt,
                   critical_alpha=main_wedge['alpha_crit']),
        energy=dict(stop=E.energy(E.CAR_MASS, fast['stop_s']),
                    free_fall=E.energy(E.CAR_MASS, 30.0),
                    speed_30m=(2 * E.G * 30.0) ** 0.5),
        rope=E.rope(fast['v_brake']),
        free_fall_30m=dict(v=(2 * E.G * 30.0) ** 0.5,
                           v_kmh=(2 * E.G * 30.0) ** 0.5 * 3.6,
                           t=(2 * 30.0 / E.G) ** 0.5),
        mass=E.CAR_MASS, blocks=E.BLOCKS, mu=E.MU_RAIL,
    )
    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + '\n')

    print('spring %.2f N, trip %.3f m/s (check %.3f)' % (E.SPRING, E.TRIP, E.trip_speed()))
    print('trip: %.1f rad/s, %.0f rpm, cent a = %.2f g' % (
        gov['at_trip']['omega'], gov['at_trip']['rpm'], gov['at_trip']['a_cent_g']))
    print('tolerance:', [(t['scale'], round(t['trip'], 3)) for t in gov['tolerance']])
    for name, d in (('from rated', fast), ('from rest', drop)):
        print('%-11s trip %.3f s v=%.2f | brake at %.3f s v=%.2f | stop %.3f s %.2f m '
              '| peak %.2f mean %.2f' % (
                  name, d['t_trip'], d['v_trip'], d['t_brake'], d['v_brake'],
                  d['stop_t'], d['stop_s'], d['peak_decel'], d['mean_decel']))
    print('clamp: total %.0f N, per block %.0f N, normal %.0f N' % (
        clamp['total'], clamp['per_block'], clamp['normal']))
    print('stops:', [(s['decel'], round(s['stop'], 2)) for s in stops])
    print('wedge 6deg:', {k: (round(v, 3) if isinstance(v, float) else v)
                          for k, v in main_wedge.items()})
    print('energy stop %.0f J, free-fall 30 m %.0f J, v %.1f m/s' % (
        out['energy']['stop']['potential'], out['energy']['free_fall']['potential'],
        out['free_fall_30m']['v']))
    print('rope:', {k: round(v, 1) for k, v in out['rope'].items()})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
