"""固定时间步长的模型。

全部用标准库：随机数是 splitmix64，浮点误差用 float64 / struct 模拟 float32。
每个实验都把结果写回 results.json，正文和图只引用那里面的数。
"""

import math
import struct

G = 30.0          # 重力，m/s²（一个偏「游戏手感」的值，不是地球）
INF = float('inf')


class SplitMix64:
    """Steele–Lea–Flood splitmix64，固定种子可复现。"""

    def __init__(self, seed):
        self.s = seed & 0xFFFFFFFFFFFFFFFF

    def next(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)

    def uniform(self, lo, hi):
        return lo + (hi - lo) * (self.next() / 2.0 ** 64)


def f32(x):
    return struct.unpack('f', struct.pack('f', x))[0]


# ---------------------------------------------------------------- 跳跃

def jump(dt, order='v_first', v0=8.0, g=G, tmax=1.2):
    """竖直起跳。order 决定一步里先更新速度还是先更新位置。

    'v_first'：v += g·dt 然后 y += v·dt（半隐式，游戏里最常见）
    'y_first'：y += v·dt 然后 v += g·dt（显式，先动后加速）
    """
    y, v, t = 0.0, v0, 0.0
    apex, t_apex = y, t
    frames = 0
    while t < tmax:
        if order == 'v_first':
            v -= g * dt
            y += v * dt
        else:
            y += v * dt
            v -= g * dt
        t += dt
        frames += 1
        if y > apex:
            apex, t_apex = y, t
        if y < 0 and t > 0.05:
            break
    return dict(dt=dt, apex=apex, t_apex=t_apex, frames=frames,
                analytic=v0 ** 2 / (2 * g), order=order)


# ---------------------------------------------------------------- 每帧插值

def lerp_curve(fps, k=0.1, seconds=1.0, target=1.0):
    """x += (target − x)·k，每帧一次。返回 seconds 秒后的 x。"""
    n = int(round(fps * seconds))
    x = 0.0
    for _ in range(n):
        x += (target - x) * k
    return dict(fps=fps, frames=n, x=x, covered=x / target)


def lerp_exact(k=0.1, fps_ref=60.0):
    """把「每帧 10%」换算成连续时间上的指数速率 λ，以及任意 fps 下等效的每帧系数。"""
    lam = -fps_ref * math.log(1.0 - k)
    return dict(lam=lam,
                half_life=math.log(2) / lam,
                k_144=1.0 - math.exp(-lam / 144.0),
                k_30=1.0 - math.exp(-lam / 30.0))


# ---------------------------------------------------------------- 振子

def spring(dt, seconds=10.0, method='semi', omega=2 * 3.141592653589793,
           x0=1.0, v0=0.0):
    """谐振子 x'' = −ω²x，E = ½v² + ½ω²x²。返回能量相对误差的轨迹。"""
    x, v = x0, v0
    e0 = 0.5 * v0 * v0 + 0.5 * omega * omega * x0 * x0
    n = int(round(seconds / dt))
    max_err = 0.0
    for _ in range(n):
        if method == 'explicit':
            a = -omega * omega * x
            x = x + v * dt
            v = v + a * dt
        elif method == 'semi':
            a = -omega * omega * x
            v = v + a * dt
            x = x + v * dt
        elif method == 'rk4':
            def f(xx, vv):
                return vv, -omega * omega * xx
            k1x, k1v = f(x, v)
            k2x, k2v = f(x + 0.5 * dt * k1x, v + 0.5 * dt * k1v)
            k3x, k3v = f(x + 0.5 * dt * k2x, v + 0.5 * dt * k2v)
            k4x, k4v = f(x + dt * k3x, v + dt * k3v)
            x = x + dt / 6.0 * (k1x + 2 * k2x + 2 * k3x + k4x)
            v = v + dt / 6.0 * (k1v + 2 * k2v + 2 * k3v + k4v)
        e = 0.5 * v * v + 0.5 * omega * omega * x * x
        max_err = max(max_err, abs(e - e0) / e0)
    e = 0.5 * v * v + 0.5 * omega * omega * x * x
    return dict(dt=dt, method=method, steps=n, err_final=(e - e0) / e0,
                err_max=max_err, phase=omega * dt)


def phase_track(dt, seconds=4.0, method='semi', omega=2 * 3.141592653589793):
    """把 (x, ω·v) 轨迹取样回传，用来画相图。"""
    x, v = 1.0, 0.0
    pts = [(x, v / omega)]
    n = int(round(seconds / dt))
    for _ in range(n):
        if method == 'explicit':
            a = -omega * omega * x
            x = x + v * dt
            v = v + a * dt
        elif method == 'semi':
            a = -omega * omega * x
            v = v + a * dt
            x = x + v * dt
        else:
            def f(xx, vv):
                return vv, -omega * omega * xx
            k1x, k1v = f(x, v)
            k2x, k2v = f(x + 0.5 * dt * k1x, v + 0.5 * dt * k1v)
            k3x, k3v = f(x + 0.5 * dt * k2x, v + 0.5 * dt * k2v)
            k4x, k4v = f(x + dt * k3x, v + dt * k3v)
            x = x + dt / 6.0 * (k1x + 2 * k2x + 2 * k3x + k4x)
            v = v + dt / 6.0 * (k1v + 2 * k2v + 2 * k3v + k4v)
        pts.append((x, v / omega))
    return pts


# ---------------------------------------------------------------- 累加器

def accumulator(frame_times, fixed=1 / 60.0, max_frame=None):
    """Fix Your Timestep 的累加器：返回每帧跑了几步、剩余、丢了多久。"""
    acc = 0.0
    rows = []
    dropped = 0.0
    for t in frame_times:
        x = t if max_frame is None else min(t, max_frame)
        dropped += (t - x)
        acc += x
        steps = 0
        while acc >= fixed:
            acc -= fixed
            steps += 1
        rows.append(dict(frame=t, steps=steps, acc=acc))
    return dict(rows=rows, dropped=dropped)


def run_accumulator(frame_times, fixed=1 / 60.0, max_frame=None):
    r = accumulator(frame_times, fixed, max_frame)
    steps = sum(row['steps'] for row in r['rows'])
    elapsed = sum(frame_times)
    clamped = sum(min(t, max_frame) if max_frame else t for t in frame_times)
    hist = {}
    for row in r['rows']:
        hist[row['steps']] = hist.get(row['steps'], 0) + 1
    return dict(rows=r['rows'], frames=len(frame_times), steps=steps, elapsed=elapsed,
                simulated=steps * fixed, clamped=clamped,
                dropped=r['dropped'], acc_left=r['rows'][-1]['acc'],
                hist=sorted(hist.items()))


def spiral_run(base_ms, cost_ms, fixed_ms=16.6667, frames=400, max_frame=None,
               seed=5):
    """Fix Your Timestep 的累加器 + 一帧开销 = 基础开销 + 步数 × 每步开销。

    帧时间由上一帧跑了几步决定：步越多越慢，越慢步越多。max_frame 就是
    常见实现里的「一帧最多补多久」闸门。
    """
    rng = SplitMix64(seed)
    acc = 0.0
    t_frame = fixed_ms
    out = []
    for i in range(frames):
        steps = 0
        acc += min(t_frame, max_frame) if max_frame else t_frame
        while acc >= fixed_ms and steps < 5000:
            acc -= fixed_ms
            steps += 1
        t_frame = base_ms * rng.uniform(0.9, 1.1) + steps * cost_ms
        out.append(dict(frame=i, ms=t_frame, steps=steps, acc=acc))
        if t_frame > 5000:      # 已经没法看了，别把机器跑死
            break
    return out


def spiral_stats(rows):
    """最后一次的帧时间、平均步数，以及有没有发散。"""
    ms = [r['ms'] for r in rows]
    steps = [r['steps'] for r in rows]
    return dict(last_ms=ms[-1], max_ms=max(ms), last_steps=steps[-1],
                mean_steps=sum(steps) / len(steps),
                diverged=max(ms) > 200.0)


# ---------------------------------------------------------------- 穿透

def tunnel_rate(speed, thickness=0.1, dt=1 / 60.0, trials=200, seed=11):
    """墙随机摆在一个步长的区间里，看离散采样有没有整个跳过它。

    采样点只在每步末尾取一次，位置是 x_k = k·step。墙是 [c − t/2, c + t/2]。
    """
    rng = SplitMix64(seed)
    step = speed * dt
    missed = 0
    for _ in range(trials):
        c = rng.uniform(0.0, 5.0)
        lo, hi = c - thickness / 2, c + thickness / 2
        x = 0.0
        hit = False
        for _ in range(1000):
            x += step
            if lo <= x <= hi:
                hit = True
                break
            if x > hi:
                break
        if not hit:
            missed += 1
    return dict(speed=speed, step=step, trials=trials, missed=missed,
                rate=missed / trials, thickness=thickness)


def tunnel_substep(speed, thickness=0.1, dt=1 / 60.0):
    step = speed * dt
    n = 1
    while step / n > thickness:
        n += 1
    return dict(speed=speed, step=step, substeps=n, per_step=step / n)


# ---------------------------------------------------------------- 浮点

def float_drift(n=60, dt=1 / 60.0):
    s64 = 0.0
    s32 = 0.0
    dt32 = f32(dt)
    for _ in range(n):
        s64 += dt
        s32 = f32(s32 + dt32)
    return dict(n=n, dt=dt, dt32=dt32, sum64=s64, err64=s64 - n * dt,
                sum32=s32, err32=s32 - n * dt32,
                mul64=n * dt, diff_mul=(s64 - n * dt))


def float_hour(fps=60, seconds=3600):
    dt = f32(1.0 / fps)
    s = 0.0
    for _ in range(fps * seconds):
        s = f32(s + dt)
    return dict(fps=fps, seconds=seconds, dt32=dt, sum32=s,
                err32=s - fps * seconds * dt, exact=fps * seconds * dt)


def sum_order():
    """同一批数换个顺序加，结果不一样。"""
    a = (1.0 + 1e16) - 1e16          # 1.0 先被大数吃掉
    b = 1.0 + (1e16 - 1e16)          # 先相消，再 +1
    return dict(left=a, right=b, equal=(a == b))


# ---------------------------------------------------------------- 双摆

def pendulum(theta1=2.1, theta2=2.1, w1=0.0, w2=0.0, dt=1e-3, seconds=20.0,
             m=1.0, l=1.0, g=9.81):
    """双摆，RK4。返回每隔 0.05 秒的 (t, theta1, theta2)。"""
    s = [theta1, theta2, w1, w2]

    def deriv(s):
        t1, t2, p1, p2 = s
        d = t1 - t2
        den = 2 * m * l * l * (1 + math.sin(d) ** 2 / 2)
        a1 = (-g * (2 * m) * math.sin(t1) - m * g * math.sin(t1 - 2 * t2)
              - 2 * math.sin(d) * m * (p2 * p2 * l + p1 * p1 * l * math.cos(d))) / (l * den)
        a2 = (2 * math.sin(d) * (p1 * p1 * l * m + g * m * math.cos(t1)
              + p2 * p2 * l * m * math.cos(d))) / (l * den)
        return [p1, p2, a1, a2]

    out = []
    n = int(round(seconds / dt))
    every = int(round(0.05 / dt))
    for i in range(n + 1):
        if i % every == 0:
            out.append((i * dt, s[0], s[1]))
        k1 = deriv(s)
        k2 = deriv([s[j] + 0.5 * dt * k1[j] for j in range(4)])
        k3 = deriv([s[j] + 0.5 * dt * k2[j] for j in range(4)])
        k4 = deriv([s[j] + dt * k3[j] for j in range(4)])
        s = [s[j] + dt / 6.0 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j])
             for j in range(4)]
    return out


def chaos(dt=1e-3, seconds=20.0, eps=1e-9):
    a = pendulum(2.1, 2.1, dt=dt, seconds=seconds)
    b = pendulum(2.1 + eps, 2.1, dt=dt, seconds=seconds)
    rows = []
    for (t, t1, t2), (_, u1, u2) in zip(a, b):
        d = ((t1 - u1) ** 2 + (t2 - u2) ** 2) ** 0.5
        rows.append(dict(t=t, sep=d, log10=(math.log10(d) if d > 0 else -16)))
    return rows
