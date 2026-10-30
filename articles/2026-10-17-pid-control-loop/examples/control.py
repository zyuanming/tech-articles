"""A PID controller and the plants this article drives with it.

Standard library only. Every number in the article and in every figure comes
from running these functions; nothing is quoted from a textbook table.
"""
from __future__ import annotations

import math
from collections import deque

# ------------------------------------------------------------------ the plant
class Thermal:
    """A heater warming a box, with a sensor that lags behind.

        dT1/dt = (K * u - (T1 - T_room)) / tau1      the box
        dT2/dt = (T1 - T2) / tau2                    the sensor

    Two lags in series is the smallest model that can ring. With K = 200 and
    a 20 C room the box settles at 220 C at full power, so holding 80 C
    needs u = 0.3.
    `dead` seconds of transport delay sit between the command and the heater.
    """

    def __init__(self, K=200.0, tau1=60.0, tau2=20.0, room=20.0, dead=0.0, dt=0.1,
                 T0=None):
        self.K, self.tau1, self.tau2, self.room = K, tau1, tau2, room
        self.leak = 0.0
        self.T1 = self.T2 = room if T0 is None else T0
        self.dt = dt
        n = max(1, int(round(dead / dt)))
        self.buffer = deque([0.0] * n, maxlen=n)
        self.dead = dead

    def out(self):
        return self.T2

    def step(self, u):
        if len(self.buffer) > 1:
            self.buffer.append(u)
            u = self.buffer[0]
        dt = self.dt
        self.T1 += dt * (self.K * u - (self.T1 - self.room) - self.leak) / self.tau1
        self.T2 += dt * (self.T1 - self.T2) / self.tau2
        return self.T2


class CartPole:
    """The classic balancing problem: nonlinear, unstable, four states.

    theta is measured from upright, so theta = 0 is the goal and the system
    falls away from it on its own.
    """

    def __init__(self, mc=1.0, mp=0.1, length=0.5, g=9.8, dt=0.01):
        self.mc, self.mp, self.l, self.g, self.dt = mc, mp, length, g, dt
        self.x = self.xd = 0.0
        self.th = 0.05          # start 0.05 rad off balance
        self.thd = 0.0

    def out(self):
        return self.x

    def step(self, force):
        dt, g, mc, mp, l = self.dt, self.g, self.mc, self.mp, self.l
        st, ct = math.sin(self.th), math.cos(self.th)
        total = mc + mp
        thdd = (g * st + ct * (-force - mp * l * self.thd ** 2 * st) / total) / \
               (l * (4.0 / 3.0 - mp * ct ** 2 / total))
        xdd = (force + mp * l * (self.thd ** 2 * st - thdd * ct)) / total
        self.x += dt * self.xd
        self.xd += dt * xdd
        self.th += dt * self.thd
        self.thd += dt * thdd
        return self.x, self.th


class Motor:
    """A position servo with a speed limit and a little friction.

    Nonlinear on purpose: the actuator saturates, so a controller that only
    works in the linear region will misbehave here.
    """

    def __init__(self, inertia=1.0, friction=0.6, vmax=2.0, dt=0.01):
        self.J, self.b, self.vmax, self.dt = inertia, friction, vmax, dt
        self.pos = self.vel = 0.0

    def out(self):
        return self.pos

    def step(self, torque):
        torque = max(-1.0, min(1.0, torque))
        self.vel += self.dt * (torque - self.b * self.vel) / self.J
        self.vel = max(-self.vmax, min(self.vmax, self.vel))
        self.pos += self.dt * self.vel
        return self.pos


# ------------------------------------------------------------- the controller
class PID:
    """Position-form PID with the three terms kept separately for plotting.

    anti_windup: 'none' integrates blindly; 'clamp' stops integrating while the
    output is saturated; 'back' bleeds the integral off in proportion to how
    far the output was clipped.
    derivative_on: 'error' differentiates the error (causing derivative kick on
    a setpoint change); 'measurement' differentiates the measurement instead.
    """

    def __init__(self, kp, ki=0.0, kd=0.0, dt=0.1, out_min=None, out_max=None,
                 anti_windup='clamp', derivative_on='error', tau_d=0.0):
        self.kp, self.ki, self.kd, self.dt = kp, ki, kd, dt
        self.out_min, self.out_max = out_min, out_max
        self.anti_windup = anti_windup
        self.derivative_on = derivative_on
        self.tau_d = tau_d
        self.integral = 0.0
        self.prev = None
        self.last = dict(p=0.0, i=0.0, d=0.0, raw=0.0, out=0.0)

    def reset(self):
        self.integral = 0.0
        self.prev = None

    def step(self, setpoint, measurement):
        error = setpoint - measurement
        p = self.kp * error
        self.integral += self.ki * error * self.dt
        if self.prev is None:
            self.prev = measurement if self.derivative_on == 'measurement' else error
        if self.derivative_on == 'measurement':
            d = -self.kd * (measurement - self.prev) / self.dt
        else:
            d = self.kd * (error - self.prev) / self.dt
        self.prev = measurement if self.derivative_on == 'measurement' else error
        if self.tau_d:
            d = d * self.dt / (self.tau_d + self.dt)
        raw = p + self.integral + d
        out = raw
        if self.out_max is not None:
            out = min(out, self.out_max)
        if self.out_min is not None:
            out = max(out, self.out_min)
        if self.anti_windup == 'clamp' and out != raw:
            self.integral -= self.ki * error * self.dt
        elif self.anti_windup == 'back' and out != raw:
            # Bleed the integral off in proportion to how far the output was
            # clipped, over a tracking time constant Tt = 20 s.
            self.integral += (out - raw) * self.dt / 20.0
        self.last = dict(p=p, i=self.integral, d=d, raw=raw, out=out)
        return out


# ------------------------------------------------------------------- the loop
def run(plant, pid, setpoint, t_end, dt=0.1, setpoint_at=None, noise=0.0, seed=1):
    """Drive `plant` with `pid` and record everything that happened.

    The sample at index k is the measurement *before* the k-th control move,
    so the arrays line up in time and the control signal can be plotted
    underneath the response.
    """
    import random
    rng = random.Random(seed)
    pid.dt = dt
    plant.dt = dt
    n = int(round(t_end / dt))
    y, u, p_terms, i_terms, d_terms, sps = [], [], [], [], [], []
    for k in range(n + 1):
        sp = setpoint if setpoint_at is None else setpoint_at(k * dt)
        meas = plant.out()
        if noise:
            meas += rng.gauss(0.0, noise)
        out = pid.step(sp, meas)
        y.append(meas)
        u.append(out)
        p_terms.append(pid.last['p'])
        i_terms.append(pid.last['i'])
        d_terms.append(pid.last['d'])
        sps.append(sp)
        if k < n:
            plant.step(out)
    return dict(t=[k * dt for k in range(n + 1)], y=y, u=u, p=p_terms,
                i=i_terms, d=d_terms, setpoint=setpoint, setpoints=sps)


def curve(step, keys=('y', 'u'), max_points=420):
    """Thin a trajectory down for drawing, keeping the first and last sample.

    The extremes are kept as well. A derivative kick is a one-sample spike, and
    uniform thinning drops exactly that -- which would leave a figure claiming
    to show a spike with no spike in it.
    """
    n = len(step['t'])
    stride = max(1, n // max_points)
    idx = list(range(0, n, stride))
    if idx[-1] != n - 1:
        idx.append(n - 1)
    for key in keys:
        series = step[key]
        idx.append(max(range(n), key=series.__getitem__))
        idx.append(min(range(n), key=series.__getitem__))
    idx = sorted(set(idx))
    out = {'t': [round(step['t'][i], 3) for i in idx]}
    for key in keys:
        out[key] = [round(step[key][i], 6) for i in idx]
    return out


def cascade_cartpole(t_end=10.0, dt=0.01, tilt_limit=0.15, goal=0.5,
                     kp_x=0.03, kd_x=0.05, kp_th=70.0, kd_th=6.0, start_tilt=0.05):
    """Balance the pole while the cart tracks a position: PID outside, PD inside.

    The outer loop turns "the cart is 0.5 m short" into "lean the pole by this
    much"; the inner loop turns "the pole is off by this much" into a force.
    The inner loop's output is negated because pushing the cart *towards* the
    lean is what straightens it.
    """
    plant = CartPole(dt=dt)
    plant.th = start_tilt
    outer = PID(kp_x, 0.0, kd_x, dt=dt, out_min=-tilt_limit, out_max=tilt_limit)
    inner = PID(kp_th, 0.0, kd_th, dt=dt)
    n = int(round(t_end / dt))
    ts, xs, ths, forces = [], [], [], []
    for k in range(n + 1):
        x, th = plant.out(), plant.th
        target_angle = outer.step(goal, x)
        force = -inner.step(target_angle, th)
        ts.append(k * dt)
        xs.append(x)
        ths.append(th)
        forces.append(force)
        if abs(th) > 1.2:
            return dict(t=ts, x=xs, th=ths, u=forces, goal=goal,
                        start_tilt=start_tilt, fell=True)
        if k < n:
            plant.step(force)
    return dict(t=ts, x=xs, th=ths, u=forces, goal=goal, start_tilt=start_tilt,
                fell=False)


# ---------------------------------------------------------------- measuring it
def metrics(step):
    """Rise time, overshoot, settling time, steady-state error, control effort."""
    y, t, sp = step['y'], step['t'], step['setpoint']
    y0 = y[0]
    span = sp - y0
    out = dict(y0=y0, setpoint=sp, final=y[-1], peak=max(y), trough=min(y))
    if span == 0:
        # The run started already at the setpoint (a later setpoint change is
        # the thing being measured). Scale by the largest excursion instead of
        # dividing by zero.
        span = max(1e-9, max(abs(v - y0) for v in y))
        out['span_from_excursion'] = True
    tail = y[-max(1, len(y) // 20):]
    out['steady_state_error'] = sp - sum(tail) / len(tail)
    for frac, key in ((0.1, 't10'), (0.9, 't90')):
        out[key] = None
        for ti, yi in zip(t, y):
            if (yi - y0) / span >= frac:
                out[key] = ti
                break
    out['rise_time'] = (None if out['t10'] is None or out['t90'] is None
                        else out['t90'] - out['t10'])
    out['overshoot'] = max(0.0, (out['peak'] - sp) / span * 100.0)
    band = 0.02 * abs(span)
    out['settling_time'] = None
    for i in range(len(y) - 1, -1, -1):
        if abs(y[i] - sp) > band:
            if i + 1 < len(t):
                out['settling_time'] = t[i + 1]
            break
    du = [abs(b - a) for a, b in zip(step['u'], step['u'][1:])]
    out['effort'] = sum(du) / len(du) if du else 0.0
    out['max_u'] = max(step['u'])
    return out


def peaks_of(step, min_gap=20):
    """Indices of the local maxima, measured against the value the loop settles at."""
    y = step['y']
    ref = sum(y[-max(1, len(y) // 10):]) / max(1, len(y) // 10)
    out = []
    for i in range(1, len(y) - 1):
        if y[i] > y[i - 1] and y[i] >= y[i + 1] and y[i] > ref:
            if not out or i - out[-1] > min_gap:
                out.append(i)
    return out, ref


def decay_ratio(step):
    """How much smaller each oscillation is than the one before (1.0 = sustained)."""
    idx, ref = peaks_of(step)
    if len(idx) < 3:
        return None
    amps = [step['y'][i] - ref for i in idx]
    return amps[-1] / amps[-2] if amps[-2] else None


def ultimate_gain(dead, lo=0.002, hi=4.0, K=200.0, sp=80.0, t_end=1200.0, dt=0.1):
    """Find the proportional gain that leaves the loop just oscillating.

    Returns ku = None when even a very large gain still settles: a plant with
    no phase lag beyond 180 degrees has no ultimate gain at all, and inventing
    one would be worse than reporting that.
    """
    def probe(kp):
        plant = Thermal(K=K, dead=dead)
        pid = PID(kp, 0.0, 0.0, out_min=0.0, out_max=1.0)
        step = run(plant, pid, sp, t_end, dt)
        return decay_ratio(step), step

    top, _ = probe(hi)
    if top is None or top < 1.0:
        return dict(ku=None, tu=None, settling_check=top,
                    note='没有极限增益：Kp 一直加到 %g，回路仍然收敛' % hi)
    for _ in range(26):
        mid = (lo + hi) / 2
        r, _ = probe(mid)
        if r is None or r < 1.0:
            lo = mid
        else:
            hi = mid
    ku = (lo + hi) / 2
    _, step = probe(ku)
    idx, _ = peaks_of(step)
    tu = None
    if len(idx) >= 2:
        tu = (idx[-1] - idx[0]) * dt / (len(idx) - 1)
    return dict(ku=ku, tu=tu, note='', settling_check=top)
