"""Why a quartz watch counts to 32768. Standard library only. MIT."""
from __future__ import annotations

import math

F_CRYSTAL = 32768          # Hz, the classic watch crystal
STAGES = 15                # 32768 = 2 ** 15
DAY = 86400.0
MONTH = 30 * DAY

# A tuning-fork crystal cut (the common +-0.035 ppm/degC^2 parabola).
TURNOVER = 25.0            # degC, where the parabola has its top
QUAD = -0.035              # ppm per degC^2


def divider(stages=STAGES, seconds=2.0):
    """Ripple counter: stage k toggles every 2**k input cycles.

    Returns the number of rising edges seen at each stage over `seconds`, plus
    the width of the final output's high phase.
    """
    total = int(F_CRYSTAL * seconds)
    edges = [total >> k for k in range(1, stages + 1)]
    return dict(total=total, edges=edges,
                out_hz=F_CRYSTAL / 2 ** stages,
                high_seconds=2 ** stages / F_CRYSTAL / 2)


def ppm_error(temp_c, quadrature=QUAD, turnover=TURNOVER):
    """Fractional frequency error of the resonator at a given temperature."""
    return quadrature * (temp_c - turnover) ** 2 * 1e-6


def drift_seconds(profile, seconds=MONTH, quadrature=QUAD, turnover=TURNOVER):
    """Integrate the frequency error over a temperature profile.

    `profile` maps a time in seconds (0..seconds) to a temperature. The integral
    is a midpoint sum; the profile is smooth so 2000 steps is plenty.
    """
    steps = 2000
    dt = seconds / steps
    total = 0.0
    for i in range(steps):
        t = (i + 0.5) * dt
        total += ppm_error(profile(t), quadrature, turnover) * dt
    return total


def daily_swing(mean_c, amplitude_c, period=DAY):
    """A room that warms up in the afternoon and cools at night."""
    return lambda t: mean_c + amplitude_c * math.sin(2 * math.pi * t / period)


def constant(temp_c):
    return lambda t: temp_c


def ladder():
    """Accuracy of various timekeepers, in ppm, plus what that means per month."""
    rows = [
        ('机械表（日差 10 秒）', 10.0 / DAY * 1e6, '当天误差'),
        ('音叉晶振，未调校（±20 ppm）', 20.0, '出厂公差'),
        ('音叉晶振，调校后（±5 ppm）', 5.0, '常见手表标称'),
        ('TCXO（±2 ppm）', 2.0, '手机里的普通温补'),
        ('MCXO（±0.5 ppm）', 0.5, '微控制器补偿'),
        ('OCXO（±0.01 ppm）', 0.01, '恒温槽，插电设备'),
        ('铷钟（±0.0005 ppm）', 0.0005, '基站、实验室'),
        ('铯束钟（±0.000001 ppm）', 1e-6, '定义「秒」的东西'),
    ]
    out = []
    for name, ppm, note in rows:
        out.append(dict(name=name, ppm=ppm, per_day=ppm * 1e-6 * DAY,
                        per_month=ppm * 1e-6 * MONTH, note=note))
    return out


def budget(trim_ppm=5.0, aging_ppm=2.0, swing=(23.0, 3.0)):
    """Where a watch's monthly error actually comes from."""
    mean, amp = swing
    # the parabola is symmetric, so a swing costs (T-T0)^2 in the mean
    temp_ppm = abs(QUAD) * ((mean - TURNOVER) ** 2 + amp ** 2 / 2)
    rows = [('出厂调校残差', trim_ppm), ('温度（抛物线 + 日夜摆动）', temp_ppm),
            ('晶振老化（第一年）', aging_ppm)]
    return [dict(name=n, ppm=p, per_month=p * 1e-6 * MONTH) for n, p in rows]


def power(voltage=1.5, osc_ua=0.6, divider_ua=0.3, motor_ua=0.1,
          capacity_mah=20.0):
    total_ua = osc_ua + divider_ua + motor_ua
    hours = capacity_mah * 1000.0 / total_ua      # mAh / uA -> hours
    return dict(voltage=voltage, osc_ua=osc_ua, divider_ua=divider_ua,
                motor_ua=motor_ua, total_ua=total_ua,
                watts=total_ua * 1e-6 * voltage,
                capacity_mah=capacity_mah, hours=hours,
                life_years=hours / 24 / 365)


def cycles_per(seconds=DAY):
    return F_CRYSTAL * seconds
