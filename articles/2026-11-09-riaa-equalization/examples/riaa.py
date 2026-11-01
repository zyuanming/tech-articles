"""RIAA 均衡：为什么刻片时先把低音砍掉 19 dB，放音时再加回来。

只用标准库。所有数字都由 run_model.py 写进 results.json。
"""

import math

# RIAA 的三个时间常数（IEC 60098 / RIAA 1954）
T1 = 3180e-6      # 50.05 Hz
T2 = 318e-6       # 500.5 Hz
T3 = 75e-6        # 2122 Hz

REF_HZ = 1000.0   # 曲线在 1 kHz 归一化为 0 dB
V_REF = 0.05      # 参考振速 5 cm/s（峰值），黑胶调电平常用值
OMEGA_REF = 2 * math.pi * REF_HZ

# LP 的几何
R_OUT = 0.146     # 录音区外半径 146 mm
R_IN = 0.058      # 录音区内半径 58 mm
RPM = 100.0 / 3   # 33⅓ 转/分
GUARD = 2.5       # 沟槽间距 = 2.5 倍最大振幅（留出隔离带）
CONTACT_R = 5e-6  # 唱针与槽壁的接触半径量级，5 µm


def hz(t):
    return 1.0 / (2 * math.pi * t)


def _s(f):
    return 1j * 2 * math.pi * f


def play_h(f):
    """放音曲线：零点在 500 Hz，极点在 50 Hz 与 2122 Hz，1 kHz 归一到 1。"""
    z = _s(f)
    h = (1 + z * T2) / ((1 + z * T1) * (1 + z * T3))
    h0 = (1 + _s(REF_HZ) * T2) / ((1 + _s(REF_HZ) * T1) * (1 + _s(REF_HZ) * T3))
    return h / h0


def rec_h(f):
    """刻片曲线 = 放音曲线的倒数：低音衰减、高音提升。"""
    return 1.0 / play_h(f)


def db(x):
    return 20 * math.log10(abs(x))


def curve(freqs):
    return [dict(f=f, rec=round(db(rec_h(f)), 2), play=round(db(play_h(f)), 2))
            for f in freqs]


def excursion(f, use_riaa=True, v=V_REF):
    """给定振速，沟槽振幅（米）。没均衡时振幅就是 v/(2πf)。"""
    a = v / (2 * math.pi * f)
    return a * abs(rec_h(f)) if use_riaa else a


def corner_freqs():
    return dict(f1=hz(T1), f2=hz(T2), f3=hz(T3))


def span():
    lo = db(play_h(20.0))
    hi = db(play_h(20000.0))
    return dict(at20=round(lo, 2), at20k=round(hi, 2), total=round(lo - hi, 2))


def bass_headroom():
    """低音省下来的振幅：同一振速下，有均衡 / 无均衡的振幅之比。"""
    out = []
    for f in (20, 30, 50, 100, 1000, 10000):
        a = excursion(f, True)
        b = excursion(f, False)
        out.append(dict(f=f, with_riaa_um=round(a * 1e6, 2),
                        flat_um=round(b * 1e6, 2),
                        ratio=round(b / a, 2), saved_db=round(20 * math.log10(b / a), 2)))
    return out


def side_time(pitch_mm):
    """一面 LP 能录多少秒：等间距螺旋，线速度按平均半径算。"""
    band = (R_OUT - R_IN) * 1000.0        # mm
    turns = band / pitch_mm
    r_mid = (R_OUT + R_IN) / 2
    length = 2 * math.pi * r_mid * turns  # m
    speed = 2 * math.pi * r_mid * (RPM / 60.0)
    return dict(pitch_mm=round(pitch_mm, 3), turns=round(turns, 1),
                length_m=round(length, 1), seconds=round(length / speed, 1),
                minutes=round(length / speed / 60, 2))


def playing_time():
    """两种世界的沟槽间距：按整条带子里最大的振幅定间距。

    最大振幅出现在最低频（20 Hz）。有均衡时 43 µm，没有时 398 µm。
    """
    a = max(excursion(f, True) for f in (20.0, 30.0, 50.0, 100.0, 1000.0))
    b = max(excursion(f, False) for f in (20.0, 30.0, 50.0, 100.0, 1000.0))
    p_riaa = a * GUARD * 1000.0
    p_flat = b * GUARD * 1000.0
    return dict(amp_riaa_um=round(a * 1e6, 1), amp_flat_um=round(b * 1e6, 1),
                pitch_riaa_mm=round(p_riaa, 3), pitch_flat_mm=round(p_flat, 3),
                riaa=side_time(p_riaa), flat=side_time(p_flat),
                ratio=round(b / a, 1))


def wavelength(f, v):
    """沟槽上这个频率的一个完整正弦有多少米。v 是线速度。"""
    return v / f


def speeds():
    """三个半径上的线速度（m/s）。"""
    def v(r):
        return 2 * math.pi * r * (RPM / 60.0)
    return dict(outer=round(v(R_OUT), 3), mid=round(v((R_OUT + R_IN) / 2), 3),
                inner=round(v(R_IN), 3))


def tracing(v=0.356):
    out = []
    for f in (100, 1000, 2000, 5000, 10000, 15000, 20000):
        lam = wavelength(f, v)
        out.append(dict(f=f, lam_um=round(lam * 1e6, 1),
                        ratio=round(lam / (2 * CONTACT_R), 2)))
    return out


def noise_gain(lo=20.0, hi=20000.0, n=4000):
    """白噪经过放音曲线后的总功率相对平坦（dB）。噪声密度是常数，所以按 df 积。"""
    step = (math.log(hi) - math.log(lo)) / n
    tot = 0.0
    for i in range(n):
        f = math.exp(math.log(lo) + (i + 0.5) * step)
        tot += abs(play_h(f)) ** 2 * f * step      # Δf = f·Δlnf
    flat = hi - lo
    return round(10 * math.log10(tot / flat), 2)


def noise_by_octave():
    out = []
    f = 31.5
    while f < 20000:
        g = noise_gain(f, f * 2, n=400)
        out.append(dict(f=round(f, 1), db=g))
        f *= 2
    return out


def tolerance(trials=200, r_tol=0.01, c_tol=0.05, seed=7):
    """元件容差把三个角频率推歪以后，曲线偏离理想值多少 dB。

    角频率 f_i = 1/(2πRC)，R 偏差 ±r_tol、C 偏差 ±c_tol，一阶近似下
    f_i 的偏差近似为 r + c 的叠加；这里用确定性伪随机抽样看最坏情况。
    """
    x = seed
    worst = 0.0
    over = []
    freqs = [20 * (10 ** (i / 24.0)) for i in range(0, 73)]   # 20 Hz → 20 kHz，每 1/8 倍频程
    for _ in range(trials):
        dr = []
        for _ in range(3):
            x = (1103515245 * x + 12345) % (2 ** 31)
            r = r_tol * (2 * (x / 2 ** 31) - 1)
            x = (1103515245 * x + 12345) % (2 ** 31)
            c = c_tol * (2 * (x / 2 ** 31) - 1)
            dr.append(1 + r + c)
        m = 0.0
        for f in freqs:
            z = 1j * 2 * math.pi * f
            h = (1 + z * T2 / dr[1]) / ((1 + z * T1 / dr[0]) * (1 + z * T3 / dr[2]))
            h0 = (1 + 2j * math.pi * REF_HZ * T2 / dr[1]) / (
                (1 + 2j * math.pi * REF_HZ * T1 / dr[0]) *
                (1 + 2j * math.pi * REF_HZ * T3 / dr[2]))
            m = max(m, abs(db((h / h0) / play_h(f))))
        over.append(m)
        worst = max(worst, m)
    over.sort()
    return dict(trials=trials, r_tol=r_tol, c_tol=c_tol,
                worst_db=round(worst, 2),
                p50_db=round(over[len(over) // 2], 2),
                p95_db=round(over[int(len(over) * 0.95)], 2))


def tolerance_curves(r_tol=0.01, c_tol=0.05, trials=200, seed=7):
    """和 tolerance() 同一套抽样，但把"最坏那次"和"中位那次"的整条偏差曲线留下。"""
    x = seed
    freqs = [20 * (10 ** (i / 24.0)) for i in range(0, 73)]
    rows = []
    for _ in range(trials):
        dr = []
        for _ in range(3):
            x = (1103515245 * x + 12345) % (2 ** 31)
            r = r_tol * (2 * (x / 2 ** 31) - 1)
            x = (1103515245 * x + 12345) % (2 ** 31)
            c = c_tol * (2 * (x / 2 ** 31) - 1)
            dr.append(1 + r + c)
        curve, m = [], 0.0
        for f in freqs:
            z = 1j * 2 * math.pi * f
            h = (1 + z * T2 / dr[1]) / ((1 + z * T1 / dr[0]) * (1 + z * T3 / dr[2]))
            h0 = (1 + 2j * math.pi * REF_HZ * T2 / dr[1]) / (
                (1 + 2j * math.pi * REF_HZ * T1 / dr[0]) *
                (1 + 2j * math.pi * REF_HZ * T3 / dr[2]))
            d = db((h / h0) / play_h(f))
            curve.append(round(d, 3))
            m = max(m, abs(d))
        rows.append((m, curve))
    rows.sort(key=lambda t: t[0])
    return dict(freqs=[round(f, 1) for f in freqs],
                worst=rows[-1][1], median=rows[len(rows) // 2][1],
                worst_db=round(rows[-1][0], 2))


def warp():
    """33⅓ 转每转一次的翘曲 = 0.556 Hz。振速相同的话，它比 1 kHz 响多少 dB。"""
    f = RPM / 60.0
    return dict(hz=round(f, 3), db=round(db(play_h(f)), 2))


def loudness_note(v=V_REF):
    """5 cm/s 在 1 kHz 是多少振幅；同一电平在 50 Hz 是多少。"""
    return dict(v_ref_cm_s=v * 100,
                amp_1k_um=round(excursion(1000.0, True) * 1e6, 2),
                amp_50_um=round(excursion(50.0, True) * 1e6, 2),
                amp_30_um=round(excursion(30.0, True) * 1e6, 2))
