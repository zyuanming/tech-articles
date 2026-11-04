"""跑出 results.json。所有图和正文只引用这里的数。"""

import json
from pathlib import Path

import timestep as T

HERE = Path(__file__).resolve().parent
OUT = {}

# ---------------------------------------------------------------- 1 跳跃
jump = []
for order in ('v_first', 'y_first'):
    for dt in (1 / 24, 1 / 30, 1 / 60, 1 / 120, 1 / 144, 1 / 240, 1 / 1000):
        jump.append(T.jump(dt, order))
OUT['jump'] = dict(rows=jump, analytic=jump[0]['analytic'], v0=8.0, g=T.G)

# 每一帧的位置也都留下来，画「一帧一帧跳」
trace = []
dt = 1 / 60
y, v, t = 0.0, 8.0, 0.0
for i in range(34):
    v -= T.G * dt
    y += v * dt
    t += dt
    trace.append(dict(t=t, y=y, v=v))
OUT['jump']['trace'] = trace

# ---------------------------------------------------------------- 2 每帧插值
lerp = [T.lerp_curve(fps) for fps in (24, 30, 45, 60, 90, 120, 144, 240)]
OUT['lerp'] = dict(rows=lerp, exact=T.lerp_exact(k=0.1, fps_ref=60.0), k=0.1)

# 跟踪一段：目标从 0 跳到 1，看三种帧率下 0.5 秒内的轨迹
tracks = {}
for fps in (30, 60, 144):
    x, xs = 0.0, []
    for i in range(int(fps * 0.5) + 1):
        xs.append(dict(t=i / fps, x=x))
        x += (1.0 - x) * 0.1
    tracks[fps] = xs
OUT['lerp']['tracks'] = tracks

# ---------------------------------------------------------------- 3 振子
spring = []
for method in ('explicit', 'semi', 'rk4'):
    for dt in (1 / 30, 1 / 60, 1 / 120, 1 / 240, 1 / 1000):
        spring.append(T.spring(dt, method=method))
OUT['spring'] = dict(rows=spring, omega=6.283185307179586, seconds=10.0)

# 能量轨迹（不是只要终值）：每 0.05 秒采一次
import math  # noqa: E402

energy = {}
for method in ('explicit', 'semi', 'rk4'):
    dt = 1 / 60
    x, v = 1.0, 0.0
    w = 2 * math.pi
    e0 = 0.5 * w * w
    xs, ys = [], []
    n = int(6.0 / dt)
    for i in range(n + 1):
        if i % 3 == 0:
            e = 0.5 * v * v + 0.5 * w * w * x * x
            xs.append(i * dt)
            ys.append(e / e0)
        if method == 'explicit':
            a = -w * w * x
            x, v = x + v * dt, v + a * dt
        elif method == 'semi':
            a = -w * w * x
            v = v + a * dt
            x = x + v * dt
        else:
            def f(xx, vv):
                return vv, -w * w * xx
            k1x, k1v = f(x, v)
            k2x, k2v = f(x + 0.5 * dt * k1x, v + 0.5 * dt * k1v)
            k3x, k3v = f(x + 0.5 * dt * k2x, v + 0.5 * dt * k2v)
            k4x, k4v = f(x + dt * k3x, v + dt * k3v)
            x = x + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            v = v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
    energy[method] = dict(t=xs, e=ys)
OUT['energy'] = energy

# 相图：ω·dt ≈ 0.105（60 fps、1 Hz）
phase = {}
for method in ('explicit', 'semi', 'rk4'):
    phase[method] = T.phase_track(1 / 60, seconds=4.0, method=method)
OUT['phase'] = dict(rows=phase, phase_angle=2 * math.pi / 60)

# ---------------------------------------------------------------- 4 累加器
rng = T.SplitMix64(7)
jitter = []
for _ in range(120):
    jitter.append(rng.uniform(0.010, 0.028))
acc_plain = T.run_accumulator(jitter)
acc_clamped = T.run_accumulator(jitter, max_frame=0.25)
# 一次 500 ms 的卡顿
hitch = jitter[:]
hitch[40] = 0.5
acc_hitch = T.run_accumulator(hitch)
acc_hitch_clamped = T.run_accumulator(hitch, max_frame=0.25)
OUT['accum'] = dict(fixed=1 / 60, plain=acc_plain, clamped=acc_clamped,
                    hitch=acc_hitch, hitch_clamped=acc_hitch_clamped,
                    frames=jitter, hitch_at=40)

# 每帧步数的直方图（给图 05 用）
OUT['accum']['steps_plain'] = [row['steps'] for row in acc_plain['rows']]
OUT['accum']['steps_clamped'] = [row['steps'] for row in acc_clamped['rows']]

# ---------------------------------------------------------------- 5 螺旋
spiral = []
for cost in (2, 5, 8, 10, 12, 15, 16, 18, 25):
    rows = T.spiral_run(20.0, float(cost))
    st = T.spiral_stats(rows)
    st['cost'] = cost
    st['base'] = 20.0
    st['predicted'] = (20.0 / (1 - cost / 16.6667)) if cost < 16.6667 else None
    st['trace'] = [r['ms'] for r in rows[:120]]
    spiral.append(st)
OUT['spiral'] = spiral
OUT['spiral_gated'] = T.spiral_stats(T.spiral_run(20.0, 25.0, max_frame=250.0))

# ---------------------------------------------------------------- 6 穿透
tunnel = []
for speed in (2, 5, 10, 20, 40, 80, 160):
    row = T.tunnel_rate(speed)
    row['closed_form'] = max(0.0, 1 - row['thickness'] / row['step'])
    tunnel.append(row)
OUT['tunnel'] = dict(rows=tunnel, substeps=[T.tunnel_substep(v) for v in (10, 20, 40, 80, 160)],
                     dt=1 / 60, thickness=0.1)

# ---------------------------------------------------------------- 7 浮点
OUT['floats'] = dict(drift=T.float_drift(), hour=T.float_hour(),
                     hour32=T.float_hour(fps=60, seconds=3600),
                     order=T.sum_order())

# ---------------------------------------------------------------- 8 双摆
OUT['chaos'] = dict(rows=T.chaos(dt=1e-3, seconds=20.0, eps=1e-9), eps=1e-9,
                    dt=1e-3, theta=2.1)

( HERE / 'results.json').write_text(json.dumps(OUT, indent=1, ensure_ascii=False))
print('wrote', (HERE / 'results.json').stat().st_size, 'bytes')
