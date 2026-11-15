#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""四点蝶形、递归 radix-2 FFT 与工作量计数的可复算例子。不联网。"""
from pathlib import Path
import argparse, cmath, json, math, platform


MULTIPLICATIONS = 0
DIGITS = 9


def pair(z, digits=DIGITS):
    """把复数记成 [实部, 虚部]；只去掉浮点末位噪声，不做别的修圆。"""
    return [round(z.real, digits) + 0.0, round(z.imag, digits) + 0.0]


def dft(x):
    """直接照公式算：每个频率位置都遍历全部输入。"""
    n = len(x)
    return [sum(x[t] * cmath.exp(-2j * math.pi * k * t / n) for t in range(n))
            for k in range(n)]


def fft(x):
    """递归 radix-2：按位置奇偶拆成两个小问题，再各乘一次权重拼回来。"""
    global MULTIPLICATIONS
    n = len(x)
    if n == 1:
        return list(x)
    even, odd = fft(x[0::2]), fft(x[1::2])
    z = []
    for k in range(n // 2):
        w = cmath.exp(-2j * math.pi * k / n)
        MULTIPLICATIONS += 1
        z.append(w * odd[k])
    return ([even[k] + z[k] for k in range(n // 2)] +
            [even[k] - z[k] for k in range(n // 2)])


def four_point_walkthrough():
    """正文的四点例子：[1,2,3,4] → 偶 [1,3]、奇 [2,4]。"""
    x = [1.0, 2.0, 3.0, 4.0]
    even, odd = x[0::2], x[1::2]
    e, o = dft(even), dft(odd)
    w1 = cmath.exp(-2j * math.pi * 1 / 4)  # 四点时 k=1 的权重，等于 −i
    stitched = [e[0] + o[0], e[1] + w1 * o[1], e[0] - o[0], e[1] - w1 * o[1]]
    return dict(
        input=x, even=even, odd=odd,
        even_dft=[pair(v) for v in e], odd_dft=[pair(v) for v in o],
        weight_k1=pair(w1), stitched=[pair(v) for v in stitched],
        matches_direct_dft=max(abs(a - b) for a, b in zip(stitched, dft(x))) < 1e-12,
    )


def template_match():
    """正文的两张检查模板与四点数据。"""
    signal = [1.0, 0.0, -1.0, 0.0]
    same = [1.0, 0.0, -1.0, 0.0]
    other = [1.0, -1.0, 1.0, -1.0]
    dot = lambda a, b: sum(p * q for p, q in zip(a, b))
    return dict(signal=signal, matched=same, matched_sum=dot(signal, same),
                alternating=other, alternating_sum=dot(signal, other))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out)
    if out.exists() and any(out.iterdir()):
        raise SystemExit('输出目录须为空或不存在')
    out.mkdir(parents=True, exist_ok=True)

    walk = four_point_walkthrough()
    templates = template_match()

    # 递归实现与直接公式在同一输入上一致；8 点用固定整数输入，便于照抄。
    check_input = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    global MULTIPLICATIONS
    MULTIPLICATIONS = 0
    fast = fft(check_input)
    eight_mult = MULTIPLICATIONS
    slow = dft(check_input)
    max_diff = max(abs(a - b) for a, b in zip(fast, slow))

    work = {}
    for n in (8, 1024):
        layers = int(round(math.log2(n)))
        layers_exact = math.log2(n) == layers
        work[str(n)] = dict(
            direct_products=n * n,
            layers=layers,
            log2_exact=layers_exact,
            butterfly_multiplications_exact=(n // 2) * layers,
            butterfly_additions=n * layers,
            formula_multiplications=int(n / 2 * layers),
        )

    # 用计数过的实现核对 1024 点乘法次数等于 (N/2)×log₂N。
    MULTIPLICATIONS = 0
    fft([float(i) for i in range(1024)])
    counted_1024 = MULTIPLICATIONS

    result = dict(
        environment=dict(python=platform.python_version(), libraries='cmath/json/math/platform'),
        walkthrough=walk,
        templates=templates,
        consistency=dict(input=check_input, max_abs_diff_dft_vs_fft=max_diff,
                         multiplications_for_8_points=eight_mult),
        work=work,
        counted_multiplications_1024=counted_1024,
        output_of_readme_example=[pair(v, 6) for v in fft([1.0, 2.0, 3.0, 4.0])],
    )

    assert walk['matches_direct_dft']
    assert walk['even_dft'] == [[4.0, 0.0], [-2.0, 0.0]]
    assert walk['odd_dft'] == [[6.0, 0.0], [-2.0, 0.0]]
    assert walk['stitched'] == [[10.0, 0.0], [-2.0, 2.0], [-2.0, 0.0], [-2.0, -2.0]]
    assert templates['matched_sum'] == 2 and templates['alternating_sum'] == 0
    assert max_diff < 1e-9
    assert eight_mult == 12 == (8 // 2) * 3
    assert counted_1024 == 5120 == (1024 // 2) * 10
    assert work['1024']['direct_products'] == 1048576
    assert work['1024']['butterfly_additions'] == 10240
    assert result['output_of_readme_example'] == [
        [10.0, 0.0], [-2.0, 2.0], [-2.0, 0.0], [-2.0, -2.0]]

    (out / 'results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'walkthrough': walk['stitched'], 'work': work,
                      'counted_1024': counted_1024}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
