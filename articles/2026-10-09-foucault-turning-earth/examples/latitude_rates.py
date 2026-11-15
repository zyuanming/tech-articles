#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""理想小振幅傅科摆进动速率与长摆周期的可复算例子。不联网、不涉及实体实验。"""
from pathlib import Path
import argparse, json, math, platform

SIDEREAL_DAY_S = 86164.0905   # 23 小时 56 分 4.09 秒
EARTH_RATE_DEG_PER_H = 360 / SIDEREAL_DAY_S * 3600
G = 9.81                      # 米/秒²，教学取值


def clock(hours):
    """把小时数写成“若干小时若干分”。"""
    whole = int(hours)
    return dict(hours=hours, hhmm=f'{whole} 小时 {round((hours - whole) * 60):d} 分')


def site(name, latitude, hemisphere):
    rate = EARTH_RATE_DEG_PER_H * abs(math.sin(math.radians(latitude)))
    if rate == 0:
        return dict(name=name, latitude=latitude, hemisphere=hemisphere,
                    sin_abs_latitude=0.0, rate_deg_per_hour=0.0,
                    period_hours=None, period=dict(hours=None, hhmm='不适用（速率恰为零）'))
    period = 360 / rate
    return dict(name=name, latitude=latitude, hemisphere=hemisphere,
                sin_abs_latitude=abs(math.sin(math.radians(latitude))),
                rate_deg_per_hour=round(rate, 2),
                period_hours=round(period, 2),
                period=clock(round(period, 2)))


def pendulum(length_m, g=G):
    """简单摆的小振幅周期：T=2π√(L/g)，质量不出现。"""
    return 2 * math.pi * math.sqrt(length_m / g)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out)
    if out.exists() and any(out.iterdir()):
        raise SystemExit('输出目录须为空或不存在')
    out.mkdir(parents=True, exist_ok=True)

    sites = [
        site('北极', 90, '北'),
        site('巴黎', 49, '北'),
        site('北纬30°', 30, '北'),
        site('赤道', 0, '—'),
        site('悉尼', 34, '南'),
    ]
    paris = next(s for s in sites if s['name'] == '巴黎')
    thirty = next(s for s in sites if s['name'] == '北纬30°')
    sydney = next(s for s in sites if s['name'] == '悉尼')

    result = dict(
        environment=dict(python=platform.python_version(), libraries='math/json'),
        constants=dict(sidereal_day_seconds=SIDEREAL_DAY_S,
                       earth_rate_deg_per_hour=round(EARTH_RATE_DEG_PER_H, 4),
                       g=G),
        note='理想小振幅模型：速率≈自转速率×|sin φ|，不含有限摆幅、椭圆轨道等修正',
        sites=sites,
        pendulum=dict(length_m=67, period_seconds=round(pendulum(67), 2),
                      mass_kg=28,
                      mass_in_period=False,
                      note='28 千克只影响实际装置的干扰与控制，不进入周期公式'),
    )

    assert round(EARTH_RATE_DEG_PER_H, 4) == 15.0411
    assert paris['rate_deg_per_hour'] == 11.35
    assert round(paris['period_hours'], 1) == 31.7
    assert thirty['rate_deg_per_hour'] == 7.52
    assert thirty['period']['hhmm'] == '47 小时 52 分'
    assert sydney['rate_deg_per_hour'] == 8.41
    assert next(s for s in sites if s['name'] == '赤道')['rate_deg_per_hour'] == 0.0
    assert next(s for s in sites if s['name'] == '北极')['rate_deg_per_hour'] == 15.04
    assert 16.0 < result['pendulum']['period_seconds'] < 17.0

    (out / 'results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'earth_rate': round(EARTH_RATE_DEG_PER_H, 4),
                      'sites': [(s['name'], s['rate_deg_per_hour'],
                                 s['period']['hhmm']) for s in sites],
                      'pendulum_67m': result['pendulum']['period_seconds']},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
