"""Kinematics and traction of an open differential. Standard library only. MIT."""
from __future__ import annotations

import math

TRACK = 1.55          # m, distance between the two rear wheels
WHEEL_D = 0.65        # m, rolling diameter
CIRC = math.pi * WHEEL_D


def wheel_speeds(v, radius, track=TRACK):
    """Straight-ahead speed v, steady turn of radius `radius` to the axle centre."""
    outer = v * (radius + track / 2) / radius
    inner = v * (radius - track / 2) / radius
    return dict(inner=inner, outer=outer, ratio=outer / inner,
                carrier=(inner + outer) / 2,
                spider=(outer - inner) / 2)


def arc(radius, track=TRACK):
    """Distances the two wheels cover going once around a circle."""
    outer = 2 * math.pi * (radius + track / 2)
    inner = 2 * math.pi * (radius - track / 2)
    return dict(inner=inner, outer=outer, gap=outer - inner,
                gap_over_track=(outer - inner) / track)


def turn_table(radius_list, v=50 / 3.6):
    rows = []
    for r in radius_list:
        s = wheel_speeds(v, r)
        a = arc(r)
        rows.append(dict(radius=r, inner_kmh=s['inner'] * 3.6,
                         outer_kmh=s['outer'] * 3.6, ratio=s['ratio'],
                         carrier_kmh=s['carrier'] * 3.6,
                         spider_kmh=s['spider'] * 3.6,
                         rev_inner=a['inner'] / CIRC,
                         rev_outer=a['outer'] / CIRC,
                         rev_gap=(a['outer'] - a['inner']) / CIRC,
                         gap_m=a['gap']))
    return rows


class Path:
    """A polyline road: (segment length, curvature) with curvature 1/R.

    Positive curvature turns left. The car drives at a constant speed.
    """

    def __init__(self, segments, v, track=TRACK, wheel_d=WHEEL_D):
        self.segments = segments
        self.v = v
        self.track = track
        self.circ = math.pi * wheel_d
        self.ds = 0.05
        self.samples = []          # (s, kappa)
        s = 0.0
        for length, kappa in segments:
            n = max(1, int(round(length / self.ds)))
            for i in range(n):
                self.samples.append((s, kappa))
                s += self.ds
        self.length = s

    def trace(self):
        """Per-sample: time, wheel speeds, cumulative wheel travel."""
        out = []
        left = right = 0.0
        t = 0.0
        for s, kappa in self.samples:
            # v_left = v (1 +- kappa * track/2)
            vl = self.v * (1 - kappa * self.track / 2)
            vr = self.v * (1 + kappa * self.track / 2)
            left += vl * self.ds / self.v
            right += vr * self.ds / self.v
            t += self.ds / self.v
            out.append(dict(s=s, t=t, left=vl * 3.6, right=vr * 3.6,
                            left_m=left, right_m=right,
                            kappa=kappa))
        return out

    def locked_scrub(self):
        """If the axle were welded, how far the tyres must drag.

        `net` is the signed difference at the end (zero for a route that turns
        equally both ways); `total` is the drag accumulated along the way, which
        is what actually wears the tyres.
        """
        tr = self.trace()
        net = abs(tr[-1]['right_m'] - tr[-1]['left_m'])
        # trace stores km/h; convert back to m/s before integrating
        total = sum(abs(p['right'] - p['left']) / 3.6 for p in tr) * self.ds / self.v
        return dict(net=net, total=total)


def traction(mass, mu_left, mu_right, torque, wheel_d=WHEEL_D, grade=0.0):
    """Open differential: torque is split equally, grip is not.

    Returns the usable tractive force and acceleration for a rear-drive car.
    """
    r = wheel_d / 2
    n_wheel = mass * 9.81 / 2       # per driven wheel, level ground
    demand = torque / 2 / r          # the axle torque is split in two before it arrives
    cap_l = mu_left * n_wheel
    cap_r = mu_right * n_wheel
    # equal split: each wheel can only push as hard as the slipperier one allows
    share = min(demand, cap_l, cap_r)
    total = 2 * share
    grade_force = mass * 9.81 * grade
    return dict(demand_each=demand, cap_left=cap_l, cap_right=cap_r,
                each=share, total=total, grade_force=grade_force,
                accel=(total - grade_force) / mass,
                climbs=total > grade_force)


def lsd(mass, mu_left, mu_right, torque, bias=2.5, wheel_d=WHEEL_D):
    """Clutch-type limited slip: it can send `bias` times more to the gripping side."""
    r = wheel_d / 2
    n_wheel = mass * 9.81 / 2
    demand = torque / 2 / r
    lo, hi = sorted((mu_left, mu_right))
    low_cap, high_cap = lo * n_wheel, hi * n_wheel
    # torque through the slow side, boosted by the bias ratio, capped by grip
    low = min(low_cap, demand)
    high = min(high_cap, demand, low * bias)
    return dict(low=low, high=high, total=low + high,
                accel=(low + high) / mass)


def gear_ratio(radius, track=TRACK):
    return (radius + track / 2) / (radius - track / 2)


def hopkins(v, radius, track=TRACK):
    """The classic one-line construction: put speeds on a vertical axis.

    Carrier speed sits at the midpoint of the two wheel speeds; the spider
    gear turns by half the difference — that is why the differential is
    called an averaging device.
    """
    s = wheel_speeds(v, radius, track)
    return dict(inner=s['inner'], outer=s['outer'], mid=s['carrier'],
                half_gap=s['spider'],
                avg_check=(s['inner'] + s['outer']) / 2 - s['carrier'])
