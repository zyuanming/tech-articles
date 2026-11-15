#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""显式欧拉误差、毫秒累积器与插值滞后的可复算例子。不联网。"""
from pathlib import Path
import argparse, json, platform

ACCELERATION = 10.0   # 米/秒²
TOTAL_SECONDS = 1.0   # 模拟总时长


def explicit_euler(steps, acceleration=ACCELERATION, total=TOTAL_SECONDS):
    """先按段首速度推进位置，再更新速度。"""
    dt = total / steps
    x, v = 0.0, 0.0
    for _ in range(steps):
        x += v * dt
        v += acceleration * dt
    return dict(steps=steps, dt=dt, position=x, velocity=v)


def accumulator(elapsed_ms, step_ms):
    """记录未被物理消费的时间，够一步就走一步。"""
    pending, rows = 0, []
    for i, elapsed in enumerate(elapsed_ms, 1):
        pending += elapsed
        steps = pending // step_ms
        pending -= steps * step_ms
        rows.append(dict(render=i, elapsed=elapsed, steps=int(steps),
                         simulated_ms_changed=int(steps * step_ms),
                         pending_ms=int(pending)))
    return rows


def interpolation(pending_ms, step_ms, previous_px, current_px, real_ms):
    """用上一状态与当前状态插值，模拟一份始终落后的显示。"""
    alpha = pending_ms / step_ms
    display = (1 - alpha) * previous_px + alpha * current_px
    display_ms = step_ms + alpha * step_ms   # previous 在 10 毫秒，current 在 20 毫秒
    latest_ms = 2 * step_ms
    return dict(alpha=alpha, display_px=display, display_time_ms=display_ms,
                latest_state_ms=latest_ms, real_ms=real_ms,
                display_lag_ms=real_ms - display_ms,
                latest_lag_ms=real_ms - latest_ms)


def article_snippet(elapsed_ms, step_ms):
    """正文那段循环原样执行，返回它会打印的四行。"""
    accumulator_ms = 0
    simulation_ms = 0
    lines = []
    for elapsed in elapsed_ms:
        accumulator_ms += elapsed
        steps = 0
        while accumulator_ms >= step_ms:
            simulation_ms += step_ms
            accumulator_ms -= step_ms
            steps += 1
        lines.append(f'{steps} {simulation_ms} {accumulator_ms}')
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out)
    if out.exists() and any(out.iterdir()):
        raise SystemExit('输出目录须为空或不存在')
    out.mkdir(parents=True, exist_ok=True)

    exact = dict(position=0.5 * ACCELERATION * TOTAL_SECONDS ** 2,
                 velocity=ACCELERATION * TOTAL_SECONDS)
    runs = {n: explicit_euler(n) for n in (1, 2, 10)}

    elapsed = [6, 13, 8, 23]
    step_ms = 10
    rows = accumulator(elapsed, step_ms)
    # 第三次画面更新后：现实 27 毫秒，物理刚算到 20 毫秒，余 7。
    third = rows[2]
    real_ms = sum(elapsed[:3])
    interp = interpolation(third['pending_ms'], step_ms, 1.0, 2.0, real_ms)

    # 螺旋：每步 12 毫秒真实成本，却只代表 10 毫秒模拟时间。
    spiral = dict(cost_ms=12, step_ms=step_ms, debt_ms_per_step=12 - step_ms,
                  steps_per_second_of_reality=3600 // 12)

    result = dict(
        environment=dict(python=platform.python_version(), libraries='仅标准库'),
        setup=dict(acceleration=ACCELERATION, total_seconds=TOTAL_SECONDS),
        exact=exact,
        euler=runs,
        euler_errors={n: round(exact['position'] - r['position'], 12)
                      for n, r in runs.items()},
        error_rule=dict(per_step=round(ACCELERATION * (TOTAL_SECONDS / 10) ** 2 / 2, 12),
                        total_for_ten_steps=round(
                            exact['position'] - runs[10]['position'], 12)),
        accumulator=dict(step_ms=step_ms, elapsed_ms=elapsed, rows=rows,
                         total_elapsed_ms=sum(elapsed),
                         total_steps=sum(r['steps'] for r in rows)),
        interpolation_ms=dict(pending_ms=third['pending_ms'], **interp),
        article_snippet=article_snippet(elapsed, step_ms),
        spiral=spiral,
    )

    assert exact == {'position': 5.0, 'velocity': 10.0}
    assert [round(runs[n]['position'], 12) for n in (1, 2, 10)] == [0.0, 2.5, 4.5]
    assert all(abs(runs[n]['velocity'] - 10.0) < 1e-12 for n in runs)
    assert result['euler_errors'] == {1: 5.0, 2: 2.5, 10: 0.5}
    assert result['error_rule']['per_step'] == 0.05  # dt=0.1 秒时每步漏掉 0.05 米
    assert [(r['steps'], r['pending_ms']) for r in rows] == [(0, 6), (1, 9), (1, 7), (3, 0)]
    assert sum(r['steps'] for r in rows) == 5 and sum(elapsed) == 50
    assert abs(interp['alpha'] - 0.7) < 1e-12 and abs(interp['display_px'] - 1.7) < 1e-12
    assert interp['display_time_ms'] == 17 and interp['latest_state_ms'] == 20
    assert interp['display_lag_ms'] == 10 and interp['latest_lag_ms'] == 7
    assert article_snippet(elapsed, step_ms) == ['0 0 6', '1 10 9', '1 20 7', '3 50 0']
    assert spiral['steps_per_second_of_reality'] == 300

    (out / 'results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'euler': {n: r['position'] for n, r in runs.items()},
                      'accumulator': rows, 'interpolation': interp},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
