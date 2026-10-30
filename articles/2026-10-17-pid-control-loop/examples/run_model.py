#!/usr/bin/env python3
"""Run every experiment the PID article quotes and write results.json.

Standard library only. The prose and the figures both read this file.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import control as C

HERE = Path(__file__).resolve().parent
SP = 80.0


def tidy(step, keys=('y', 'u'), n=420):
    return C.curve(step, keys, n)


def brief(m):
    return {k: (round(v, 6) if isinstance(v, float) else v) for k, v in m.items()}


def trial(kp, ki=0.0, kd=0.0, *, dead=0.0, t=800.0, dt=0.1, T0=None, sp=SP,
          aw='clamp', don='error', noise=0.0, leak_at=None, leak=0.0,
          setpoint_at=None, seed=1, umax=1.0, umin=0.0):
    plant = C.Thermal(dead=dead, T0=T0)
    pid = C.PID(kp, ki, kd, out_min=umin, out_max=umax,
                anti_windup=aw, derivative_on=don)
    if leak_at is not None:
        original = plant.step

        def stepped(u, _o=original, _p=plant, _t=[0.0]):
            out = _o(u)
            _t[0] += dt
            if _t[0] >= leak_at:
                _p.leak = leak
            return out
        plant.step = stepped
    step = C.run(plant, pid, sp, t, dt, setpoint_at=setpoint_at, noise=noise,
                 seed=seed)
    return step, C.metrics(step)


def main() -> None:
    out = {'setpoint': SP, 'room': 20.0}

    # ---- on/off control: what a thermostat with no proportional band does
    class OnOff:
        def __init__(self, sp):
            self.sp = sp
            self.on = False
            self.last = dict(p=0.0, i=0.0, d=0.0, raw=0.0, out=0.0)

        def step(self, sp, meas):
            if meas < sp:
                self.on = True
            else:
                self.on = False
            self.last = dict(p=0.0, i=0.0, d=0.0, raw=float(self.on),
                             out=float(self.on))
            return float(self.on)

    plant = C.Thermal()
    step = C.run(plant, OnOff(SP), SP, 800.0, 0.1)
    out['onoff'] = dict(metrics=brief(C.metrics(step)), curve=tidy(step))

    # ---- proportional only
    out['p_only'] = []
    for kp in (0.002, 0.008, 0.02, 0.06, 0.15):
        step, m = trial(kp)
        out['p_only'].append(dict(kp=kp, metrics=brief(m), curve=tidy(step)))

    # ---- one knob at a time around a fixed operating point
    out['ki_sweep'] = []
    for ki in (0.0, 5e-5, 1e-4, 2e-4, 4e-4):
        step, m = trial(0.06, ki)
        out['ki_sweep'].append(dict(ki=ki, metrics=brief(m), curve=tidy(step)))
    out['kd_sweep'] = []
    for kd in (0.0, 0.25, 0.5, 1.0, 2.0):
        step, m = trial(0.06, 0.0, kd)
        out['kd_sweep'].append(dict(kd=kd, metrics=brief(m), curve=tidy(step)))

    # ---- the four controllers side by side
    tunings = [('只有 P', 0.06, 0.0, 0.0), ('P 加 D', 0.06, 0.0, 0.5),
               ('P 加 I', 0.06, 2e-4, 0.0), ('PID', 0.06, 4e-4, 1.0)]
    out['tunings'] = []
    for name, kp, ki, kd in tunings:
        step, m = trial(kp, ki, kd)
        # Keep the three terms as well as the total: section 12 draws the
        # decomposition, and a figure that claims to show it must have the
        # numbers to do so.
        out['tunings'].append(dict(name=name, kp=kp, ki=ki, kd=kd,
                                   metrics=brief(m),
                                   curve=tidy(step, ('y', 'u', 'p', 'i', 'd'))))

    # ---- integral windup
    out['windup'] = []
    for aw in ('none', 'clamp', 'back'):
        step, m = trial(0.05, 2e-4, 0.0, aw=aw, t=1000.0)
        out['windup'].append(dict(mode=aw, metrics=brief(m), curve=tidy(step)))

    # ---- derivative kick: move the setpoint, not the plant
    out['kick'] = []
    for don in ('error', 'measurement'):
        step, m = trial(0.06, 4e-4, 1.0, T0=SP, don=don, t=400.0,
                        setpoint_at=lambda t: 80.0 if t < 200.0 else 90.0)
        out['kick'].append(dict(mode=don, metrics=brief(m), curve=tidy(step)))

    # ---- dead time: the thing that actually makes loops hard
    out['dead_time'] = []
    for dead in (0.0, 10.0, 25.0, 40.0, 60.0):
        step, m = trial(0.02, 5e-5, 0.05, dead=dead, t=1500.0)
        out['dead_time'].append(dict(dead=dead, metrics=brief(m), curve=tidy(step)))

    # Detuning the same family against the worst delay in the table above.
    # "You cannot tune your way out of delay" is too strong: lowering the gain
    # does stop the overshoot -- it just stops everything else too.
    out['dead_time_detune'] = []
    for factor in (1.0, 0.5, 0.25, 0.125, 0.0625):
        step, m = trial(0.02 * factor, 5e-5 * factor, 0.05 * factor,
                        dead=60.0, t=1500.0)
        out['dead_time_detune'].append(dict(factor=factor, metrics=brief(m),
                                            curve=tidy(step)))

    # ---- Ziegler-Nichols, measured rather than looked up
    zn0 = C.ultimate_gain(0.0)
    zn = C.ultimate_gain(15.0)
    entry = dict(no_delay=dict(ku=zn0['ku'], tu=zn0['tu'], note=zn0['note']),
                 with_delay=dict(ku=zn['ku'], tu=zn['tu'], note=zn['note']))
    if zn['ku']:
        ku, tu = zn['ku'], zn['tu']
        table = [('P', 0.5 * ku, 0.0, 0.0), ('PI', 0.45 * ku, 0.45 * ku / (tu / 1.2), 0.0),
                 ('PID', 0.6 * ku, 0.6 * ku / (0.5 * tu), 0.6 * ku * 0.125 * tu)]
        entry['tunings'] = []
        for name, kp, ki, kd in table:
            step, m = trial(kp, ki, kd, dead=15.0, t=1500.0)
            entry['tunings'].append(dict(name=name, kp=kp, ki=ki, kd=kd,
                                         metrics=brief(m), curve=tidy(step)))
    out['zn'] = entry

    # ---- sample time
    out['sample_time'] = []
    for dt in (0.1, 1.0, 5.0, 15.0, 30.0):
        step, m = trial(0.06, 4e-4, 1.0, dt=dt, t=800.0)
        out['sample_time'].append(dict(dt=dt, metrics=brief(m), curve=tidy(step)))

    # ---- measurement noise: what the D term really costs you
    out['noise'] = []
    for kd in (0.0, 1.0, 4.0):
        step, m = trial(0.06, 4e-4, kd, noise=0.4, t=600.0, seed=7)
        swings = [abs(b - a) for a, b in zip(step['u'], step['u'][1:])]
        out['noise'].append(dict(kd=kd, metrics=brief(m), curve=tidy(step),
                                 mean_u_swing=sum(swings) / len(swings),
                                 max_u_swing=max(swings)))

    # ---- disturbance rejection at steady state
    out['disturbance'] = []
    for name, kp, ki, kd in (('只有 P', 0.06, 0.0, 0.0), ('PI', 0.06, 4e-4, 0.0),
                             ('PID', 0.06, 4e-4, 1.0)):
        step, m = trial(kp, ki, kd, T0=SP, t=800.0, leak_at=300.0, leak=20.0)
        after = [y for t, y in zip(step['t'], step['y']) if t >= 300.0]
        out['disturbance'].append(dict(
            name=name, kp=kp, ki=ki, kd=kd, curve=tidy(step),
            dip=SP - min(after), final=after[-1],
            recovered_at=next((t for t, y in zip(step['t'], step['y'])
                               if t > 300.0 and abs(y - SP) < 0.2), None)))

    # ---- actuator saturation
    out['saturation'] = []
    for umax in (0.2, 0.5, 1.0):
        step, m = trial(0.06, 4e-4, 1.0, umax=umax, t=1200.0)
        out['saturation'].append(dict(umax=umax, metrics=brief(m), curve=tidy(step)))

    # ---- the same three ideas on a system that does not sit still
    cp = C.cascade_cartpole()
    idx = list(range(0, len(cp['t']), max(1, len(cp['t']) // 420)))
    out['cartpole'] = dict(
        fell=cp['fell'], goal=cp['goal'], start_tilt=cp['start_tilt'],
        max_abs_angle=max(abs(v) for v in cp['th']),
        max_force=max(abs(v) for v in cp['u']),
        final_x=cp['x'][-1],
        t=[round(cp['t'][i], 3) for i in idx],
        x=[round(cp['x'][i], 5) for i in idx],
        th=[round(cp['th'][i], 6) for i in idx],
        u=[round(cp['u'][i], 4) for i in idx])

    # ---- what happens with no controller at all: how fast does it fall?
    free = C.CartPole(1.0, 0.2, 0.5, 9.81, 0.01)
    free.th = 0.05
    tf, thf = 0.0, free.th
    while tf < 20.0:
        free.step(0.0)
        tf += 0.01
        thf = free.th
        if abs(free.th) > 0.5:
            break
    out['cartpole_free'] = dict(start_tilt=0.05, fell_at=round(tf, 2),
                                threshold=0.5, angle_then=round(thf, 4))

    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + '\n')

    print('on/off      overshoot %.2f%%  ess %.3f' % (
        out['onoff']['metrics']['overshoot'], out['onoff']['metrics']['steady_state_error']))
    for row in out['p_only']:
        m = row['metrics']
        print('  P  kp=%-6g rise %-7s overshoot %6.2f%%  offset %7.3f' % (
            row['kp'], m['rise_time'], m['overshoot'], m['steady_state_error']))
    for row in out['tunings']:
        m = row['metrics']
        print('  %-8s rise %-7s overshoot %6.2f%%  offset %7.3f  settle %s' % (
            row['name'], m['rise_time'], m['overshoot'],
            m['steady_state_error'], m['settling_time']))
    for row in out['windup']:
        m = row['metrics']
        print('  windup=%-6s overshoot %6.2f%%  settle %-8s' % (
            row['mode'], m['overshoot'], m['settling_time']))
    print('  ZN no delay:', out['zn']['no_delay']['note'])
    print('  ZN dead=15: ku=%.3f tu=%.1f' % (zn['ku'], zn['tu']))
    for row in out['zn']['tunings']:
        print('    %-4s overshoot %6.2f%%  offset %7.3f' % (
            row['name'], row['metrics']['overshoot'],
            row['metrics']['steady_state_error']))
    for row in out['dead_time']:
        print('  dead=%-5g overshoot %6.2f%%  settle %s' % (
            row['dead'], row['metrics']['overshoot'], row['metrics']['settling_time']))
    for row in out['noise']:
        print('  noise kd=%-4g mean |du| %.4f' % (row['kd'], row['mean_u_swing']))
    for row in out['disturbance']:
        print('  disturbance %-8s dip %.2f  final %.3f  recovered %s' % (
            row['name'], row['dip'], row['final'], row['recovered_at']))
    print('  cart-pole free: |theta| > 0.5 rad at t=%.2f s (start %.2f rad)' % (
        out['cartpole_free']['fell_at'], out['cartpole_free']['start_tilt']))
    print('  cart-pole: fell=%s max|theta|=%.4f rad  final x=%.4f m  max|F|=%.2f N' % (
        out['cartpole']['fell'], out['cartpole']['max_abs_angle'],
        out['cartpole']['final_x'], out['cartpole']['max_force']))
    print('  writes results.json')


if __name__ == '__main__':
    main()
