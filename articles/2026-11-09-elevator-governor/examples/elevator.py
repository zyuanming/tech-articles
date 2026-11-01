"""Overspeed governor + safety gear for a traction elevator. Standard library only. MIT.

The model is deliberately small: a centrifugal governor, a reaction delay, and a
friction brake on the guide rails. Every number in the article comes from here.
"""
from __future__ import annotations

import math

G = 9.81

# --- the elevator -----------------------------------------------------------
RATED = 1.75          # m/s, nominal speed (about 6 people, low rise)
TRIP_FACTOR = 1.15    # governors trip at >= 115% of rated speed
CAR_MASS = 1200.0     # kg, car + half load
BLOCKS = 2            # one safety gear per guide rail

# --- the governor -----------------------------------------------------------
SHEAVE_R = 0.10       # m, governor rope sheave radius
PAWL_M = 0.25         # kg, one flyweight
PAWL_R = 0.06         # m, flyweight centre of mass from the axis

TRIP = RATED * TRIP_FACTOR


def spring_force(v_trip=TRIP):
    """Preload that makes the flyweights reach the ratchet at `v_trip`."""
    omega = v_trip / SHEAVE_R
    return PAWL_M * PAWL_R * omega ** 2


SPRING = spring_force()


def trip_speed(force=SPRING):
    return SHEAVE_R * math.sqrt(force / (PAWL_M * PAWL_R))


def governor(v):
    omega = v / SHEAVE_R
    fc = PAWL_M * PAWL_R * omega ** 2
    return dict(v=v, omega=omega, rpm=omega * 60 / (2 * math.pi),
                fc=fc, a_cent=omega ** 2 * PAWL_R,
                a_cent_g=omega ** 2 * PAWL_R / G,
                ratio=fc / SPRING)


def governor_tolerance(scales=(0.90, 0.95, 1.00, 1.05, 1.10)):
    return [dict(scale=s, force=SPRING * s, trip=trip_speed(SPRING * s),
                 ppm=(trip_speed(SPRING * s) / TRIP - 1) * 1e6 / 1e6)
            for s in scales]


# --- the reaction chain -----------------------------------------------------
DELAY = 0.15          # s, ratchet + linkage + wedge take-up, after the trip point
RAMP = 0.08           # s, clamp force build-up


def simulate(v0=0.0, brake=6.0, delay=DELAY, ramp=RAMP, dt=2e-4):
    """Fall from `v0`, trip the governor, then brake at `brake` m/s^2 (average).

    Phase 1: free fall until the flyweights reach the trip speed.
    Phase 2: the reaction chain, still accelerating at g.
    Phase 3: clamp force ramps in; deceleration = F/m - g.
    """
    m = CAR_MASS
    target = brake * m + m * G       # force that yields `brake` m/s^2 net
    v, s, t = v0, 0.0, 0.0
    trace = []
    peak = 0.0
    phase = 1
    while v > 0 or t == 0:
        if phase == 1 and t > 0 and v >= TRIP:
            phase = 2
            t_trip, v_trip, s_trip = t, v, s
            t_delay_end = t + delay
        if phase == 1 or (phase == 2 and t < t_delay_end):
            a = G
        else:
            if phase == 2:
                phase = 3
                t_brake, v_brake, s_brake = t, v, s
            k = min(1.0, (t - t_brake) / ramp) if ramp > 0 else 1.0
            f = target * k
            a = G - f / m          # positive v is downward; a<0 is braking
            peak = max(peak, f / m - G)
        v += a * dt
        s += v * dt
        t += dt
        if len(trace) % 50 == 0:
            trace.append(dict(t=round(t, 3), v=round(v, 3), s=round(s, 3),
                              a=round(a, 2)))
        if v <= 0:
            break
    out = dict(v0=v0, brake=brake, delay=delay, ramp=ramp,
               t_trip=t_trip, v_trip=v_trip, s_trip=s_trip,
               t_brake=t_brake, v_brake=v_brake, s_brake=s_brake,
               stop_t=t, stop_s=s, peak_decel=peak,
               mean_decel=(v_brake ** 2) / (2 * (s - s_brake)),
               force=target, per_block=target / BLOCKS,
               force_g=target / (m * G))
    return out, trace


# --- the wedge --------------------------------------------------------------
MU_RAIL = 0.15


def wedge(alpha_deg=6.0, mu=MU_RAIL):
    """A wedge driven up between the rail and its housing.

    Driving it in takes `N tan(a + phi)`; pulling it back out takes
    `N tan(a - phi)`, which vanishes when the wedge angle equals the friction
    angle — that is why a safety gear does not let go.
    """
    phi = math.degrees(math.atan(mu))
    a = math.radians(alpha_deg)
    p = math.atan(mu)
    return dict(alpha=alpha_deg, mu=mu, phi=phi,
                self_locking=alpha_deg <= phi,
                gain=1 / math.tan(a + p) if a + p < math.pi / 2 else 0.0,
                pull_out=(1 / math.tan(a - p)) if a > p else None,
                # self-energising: the drag the wedge itself creates is enough
                # to keep clamping, i.e. 2*mu*N >= N*tan(a+phi)
                self_energising=math.tan(a + p) < 2 * mu,
                alpha_crit=math.degrees(math.atan(2 * mu)) - phi)


def wedge_curve(lo=2, hi=15, step=0.5):
    rows = []
    k = lo
    while k <= hi + 1e-9:
        w = wedge(k)
        rows.append(dict(alpha=round(k, 2), gain=round(w['gain'], 3),
                         self_locking=w['self_locking'],
                         self_energising=w['self_energising'],
                         need=round(math.tan(math.radians(k) + math.atan(MU_RAIL)), 4)))
        k += step
    return rows


# --- forces and distance ----------------------------------------------------
def clamp_force(v, decel, mass=CAR_MASS, mu=MU_RAIL, blocks=BLOCKS):
    f = mass * (G + decel)
    per = f / blocks
    return dict(total=f, per_block=per, normal=per / mu,
                normal_total=f / mu, stop=v ** 2 / (2 * decel),
                time=v / decel)


def stop_table(v, decels=(3, 6, 9, 12)):
    return [dict(decel=d, stop=v ** 2 / (2 * d), time=v / d,
                 force=CAR_MASS * (G + d)) for d in decels]


def energy(mass, drop):
    return dict(potential=mass * G * drop,
                per_kg=mass * G * drop / mass,
                steel_dt=mass * G * drop / (40 * 470))   # 40 kg of steel, 470 J/(kg K)


def rope(v, metres=20.0, kg_per_m=0.25, dt=0.05, tensioner_kg=40.0):
    m = 2 * metres * kg_per_m
    return dict(mass=m, tension=tensioner_kg * G / 2,
                jerk=m * v / dt, jerk_g=m * v / dt / (m * G))
