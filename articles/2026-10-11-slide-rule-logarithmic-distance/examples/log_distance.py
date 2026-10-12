"""Original teaching model. No physical slide rule was measured.
Python 3 standard library; emits a printable SVG and checks ideal geometry.
"""
import math
from pathlib import Path

L = 200.0  # millimetres per decade on the teaching paper scale

def position(x):
    if x <= 0:
        raise ValueError('a logarithmic scale requires a positive number')
    return L * math.log10(x)

def read_at(s):
    return 10 ** (s / L)

def multiply(a, b):
    return read_at(position(a) + position(b))

def printable_svg(path):
    # Both strips have the SAME scale factor. Print at any uniform size.
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="240mm" height="110mm" viewBox="0 0 240 110">',
           '<rect width="240" height="110" fill="white"/>',
           '<g font-family="sans-serif" fill="#243740" stroke="none">',
           '<text x="20" y="10" font-size="4">Paper slide rule: two identical logarithmic scales</text>']
    for label, y in [('C', 35), ('D', 80)]:
        out.append(f'<text x="6" y="{y+2}" font-size="5">{label}</text>')
        out.append(f'<path d="M 20 {y} H 220" stroke="#243740" stroke-width="0.25"/>')
        out.append(f'<rect x="16" y="{y-12}" width="209" height="28" fill="none" stroke="#999" stroke-width="0.15" stroke-dasharray="1 1"/>')
        for n in range(10, 101):
            x = n / 10
            s = 20 + position(x)
            major = n % 10 == 0
            out.append(f'<path d="M {s:.5f} {y} v {-6 if major else -3}" stroke="#243740" stroke-width="0.2"/>')
            if major:
                out.append(f'<text x="{s:.5f}" y="{y+7}" text-anchor="middle" font-size="3.5">{x:g}</text>')
        out.append(f'<text x="20" y="{y+22}" font-size="3">Dashed box: cut outline. Do not stretch one strip independently.</text>')
    out.append('</g></svg>')
    Path(path).write_text('\n'.join(out), encoding='utf-8')

if __name__ == '__main__':
    for x in [1, 2, 2.4, 3.2, 4, 7.68, 8, 10]:
        print(f'x={x:5g}, position={position(x):.6f} mm')
    print('2.4 * 3.2:', multiply(2.4, 3.2))
    print('6 * 4: raw position, wrapped position, scale reading:',
          position(6)+position(4), position(6)+position(4)-L,
          read_at(position(6)+position(4)-L))
    print('7.68 / 3.2:', read_at(position(7.68)-position(3.2)))
    print('single final-position error +0.2mm, relative error:', read_at(.2)-1)
    values = [10 ** (i / 10) for i in range(-30, 31)]
    for a in values:
        for b in values:
            assert math.isclose(multiply(a, b), a*b, rel_tol=1e-12)
            assert math.isclose(read_at(position(a)-position(b)), a/b, rel_tol=1e-12)
    for x in [1, 2, 4, 9, 20, 36, 100]:
        assert math.isclose(read_at(position(x)/2), math.sqrt(x), rel_tol=1e-12)
    print('PASS: 3721 positive pairs, ideal multiply/divide, plus 7 square roots')
    printable_svg(Path(__file__).with_name('paper-slide-rule.svg'))
