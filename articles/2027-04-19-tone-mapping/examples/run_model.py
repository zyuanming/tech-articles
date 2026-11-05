"""跑全部实验，写出 results.json。所有数字都能由 tone.py 重算。"""

import json
from pathlib import Path

import tone as T

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results.json'

XS = [0.001, 0.01, 0.05, 0.18, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 64.0, 1000.0]
OCTAVES = [0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
SLOPE_XS = [0.01, 0.05, 0.18, 0.5, 1.0, 2.0, 4.0, 8.0]
WHITES = [2.0, 4.0, 8.0, 16.0]


def curve_table():
    """十二个输入值经过四条曲线之后，线性值和 8 位码值各是多少。"""
    rows = []
    for x in XS:
        row = {'x': x}
        for name, f in T.CURVES:
            y = f(x)
            row[name] = y
            row[name + '_code'] = T.code8(y)
        rows.append(row)
    return rows


def octaves():
    """每个「一档曝光」的输入段，在屏幕上占多少个 8 位码值。"""
    out = []
    for i in range(len(OCTAVES) - 1):
        lo, hi = OCTAVES[i], OCTAVES[i + 1]
        row = {'lo': lo, 'hi': hi, 'stop': i - 3}
        for name, f in T.CURVES:
            row[name] = T.codes_in_range(f, lo, hi)
        out.append(row)
    return out


def slopes():
    """对数斜率：输入亮一档，屏幕上亮几档。"""
    out = []
    for x in SLOPE_XS:
        row = {'x': x}
        for name, f in T.CURVES:
            row[name] = T.loglog_slope(f, x)
        out.append(row)
    return out


def white_points():
    """带白点的 Reinhard：白点选在哪里，那里就正好显示成 1.0。"""
    out = []
    for w in WHITES:
        f = lambda x, w=w: T.reinhard_white(x, w)
        # 白点处的输出
        at_white = f(w)
        # 中灰处要抬到多少才回到 0.18（下一条实验用）
        out.append({'white': w, 'at_white': at_white,
                    'mid': f(0.18),
                    'mid_code': T.code8(f(0.18)),
                    'octave_1_8': T.codes_in_range(f, 1.0, 8.0)})
    return out


def midgray():
    """中灰（18% 灰卡）在四条曲线下的落点，以及「要抬多少」才回到中灰。"""
    out = {'x': 0.18, 'rows': []}
    for name, f in T.CURVES:
        y = f(0.18)
        # 二分找 f(x) = 0.18 的 x
        lo, hi = 1e-6, 1000.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if f(mid) < 0.18:
                lo = mid
            else:
                hi = mid
        out['rows'].append({'curve': name, 'y': y, 'code': T.code8(y),
                            'x_for_mid': (lo + hi) / 2,
                            'ratio': (lo + hi) / 2 / 0.18})
    # 曝光（±2 档）对中灰的影响，用 Reinhard 与 ACES 拟合
    expo = []
    for ev in (-1.0, 0.0, 1.0, 2.0, 3.0):
        gain = 2.0 ** ev
        expo.append({'ev': ev, 'gain': gain,
                     'rein': T.reinhard(0.18 * gain),
                     'rein_code': T.code8(T.reinhard(0.18 * gain)),
                     'aces': T.aces_fit(0.18 * gain),
                     'aces_code': T.code8(T.aces_fit(0.18 * gain))})
    out['exposure'] = expo
    return out


def ramps():
    """连续渐变送进曲线：用掉多少码值、最长一段重复多长。"""
    out = []
    for name, f in T.CURVES:
        st = T.ramp_stats(f, 8.0, samples=8192)
        st['curve'] = name
        # 高光那一段单独看：1 到 8 之间有多少码值
        st['octave_1_8'] = T.codes_in_range(f, 1.0, 8.0)
        out.append(st)
    return out


def srgb_reference():
    """sRGB 编码的几个锚点，正文与图都要用。"""
    anchors = [0.0, 0.0031308, 0.01, 0.05, 0.18, 0.214041, 0.5, 0.735, 1.0]
    return [{'v': v, 'enc': T.srgb_encode(v), 'code': T.code8(v)} for v in anchors]


def selfcheck(R):
    rows = {r['x']: r for r in R['table']}
    sl = {r['x']: r for r in R['slopes']}
    oct_ = {r['lo']: r for r in R['octaves']}
    checks = [
        ('sRGB 编解码可逆', all(
            abs(T.srgb_decode(T.srgb_encode(v)) - v) < 1e-12
            for v in (0.001, 0.05, 0.214041, 0.5, 0.9, 1.0))),
        ('sRGB 0.5 电平对应 0.2140 线性', abs(T.srgb_decode(0.5) - 0.214041) < 1e-5),
        ('Reinhard 在 0.18 处给 0.1525', abs(rows[0.18]['Reinhard'] - 0.152542) < 1e-5),
        ('白点 8 的版本在 8.0 处正好给 1.0', abs(T.reinhard_white(8.0, 8.0) - 1.0) < 1e-12),
        ('四条曲线都单调不减', all(
            all(f(XS[i]) <= f(XS[i + 1]) + 1e-12 for i in range(len(XS) - 1))
            for _, f in T.CURVES)),
        ('截断把 1 到 8 压成 1 个码值', oct_[1.0]['截断'] == 1),
        ('Reinhard 在 8 到 16 只剩不到 10 个码值', oct_[8.0]['Reinhard'] < 10),
        ('截断的对数斜率恒为 1', abs(sl[0.18]['截断'] - 1.0) < 1e-6),
        ('Reinhard 在 8 处的对数斜率不到 0.12', sl[8.0]['Reinhard'] < 0.12),
        ('ACES 拟合在 0.18 处给 0.2669', abs(rows[0.18]['ACES 拟合'] - 0.266899) < 1e-4),
        ('ACES 拟合在 1.0 处没有到 1', rows[1.0]['ACES 拟合'] < 0.85),
        ('Reinhard 永不达到 1（1000 处仍小于 1）', rows[1000.0]['Reinhard'] < 1.0),
        ('中灰经 Reinhard 后偏暗，需要抬 20% 以上才回到 0.18',
         [r for r in R['midgray']['rows'] if r['curve'] == 'Reinhard'][0]['ratio'] > 1.2),
        ('渐变进截断后，最长一段重复超过 5000 个采样',
         [r for r in R['ramps'] if r['curve'] == '截断'][0]['longest_run'] > 5000),
    ]
    R['checks'] = [{'name': n, 'ok': bool(ok)} for n, ok in checks]
    R['selfcheck'] = all(ok for _, ok in checks)
    return R


def main():
    R = {
        'meta': {'xs': XS, 'curves': [n for n, _ in T.CURVES],
                 'octaves': OCTAVES, 'whites': WHITES,
                 'srgb': 'IEC 61966-2-1 分段式',
                 'aces': '常用有理拟合，非官方 RRT+ODT（一手出处未取到）'},
        'table': curve_table(),
        'octaves': octaves(),
        'slopes': slopes(),
        'whites': white_points(),
        'midgray': midgray(),
        'ramps': ramps(),
        'srgb': srgb_reference(),
    }
    selfcheck(R)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1) + '\n')
    print('wrote', OUT, OUT.stat().st_size, 'bytes')
    print('selfcheck', R['selfcheck'])
    for c in R['checks']:
        print(('  OK  ' if c['ok'] else '  BAD ') + c['name'])
    return R


if __name__ == '__main__':
    main()
