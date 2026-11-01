"""白平衡的最小模型：黑体辐射、CIE 1931 观察者、一台假相机、几种估白算法。

只用标准库。所有数字都由本文件算出，写进 results.json，正文与图从那里取。
"""

import math

# ---------------------------------------------------------------- 物理常数

H = 6.62607015e-34
C = 2.99792458e8
KB = 1.380649e-23

LAMBDAS = list(range(380, 781, 5))          # 5 nm 采样，81 个点
DLAM = 5.0


def planck(lam_nm, T):
    """黑体光谱辐射（相对值，未乘常数以外的东西）。"""
    lam = lam_nm * 1e-9
    return (2.0 * math.pi * H * C * C / lam ** 5) / (
        math.exp(H * C / (lam * KB * T)) - 1.0)


def planck_curve(T):
    return [planck(l, T) for l in LAMBDAS]


# ------------------------------------------- CIE 1931 配色函数（解析拟合）
# Wyman, Sloan, Shirley 2013 的多瓣高斯拟合，误差在 1% 量级。

def _g(x, mu, s1, s2):
    s = s1 if x < mu else s2
    return math.exp(-0.5 * ((x - mu) / s) ** 2)


def cmf(lam):
    x = (1.056 * _g(lam, 599.8, 37.9, 31.0)
         + 0.362 * _g(lam, 442.0, 16.0, 26.7)
         - 0.065 * _g(lam, 501.1, 20.4, 26.2))
    y = (0.821 * _g(lam, 568.8, 46.9, 40.5)
         + 0.286 * _g(lam, 530.9, 16.3, 31.1))
    z = (1.217 * _g(lam, 437.0, 11.8, 36.0)
         + 0.681 * _g(lam, 459.0, 26.0, 13.8))
    return x, y, z


def xyz_of(sp):
    X = Y = Z = 0.0
    for lam, v in zip(LAMBDAS, sp):
        x, y, z = cmf(lam)
        X += v * x
        Y += v * y
        Z += v * z
    return X * DLAM, Y * DLAM, Z * DLAM


def xy_of(xyz):
    X, Y, Z = xyz
    s = X + Y + Z
    if s <= 0:
        return 0.0, 0.0
    return X / s, Y / s


def uv1960(x, y):
    d = -2.0 * x + 12.0 * y + 3.0
    return 4.0 * x / d, 6.0 * y / d


def uv1960_of_xyz(xyz):
    return uv1960(*xy_of(xyz))


# ---------------------------------------------------------------- 假相机
# 三条高斯感光曲线。真实相机的曲线长得不完全这样，但红绿蓝三个窄峰是共性。

SENSORS = ((600.0, 45.0), (545.0, 40.0), (450.0, 30.0))


def sensor_rgb(sp):
    out = []
    for mu, sd in SENSORS:
        acc = 0.0
        for lam, v in zip(LAMBDAS, sp):
            acc += v * _g(lam, mu, sd, sd)
        out.append(acc * DLAM)
    return tuple(out)


def illum_rgb(T):
    return sensor_rgb(planck_curve(T))


# ------------------------------------------------ 反射率与场景

def flat(level):
    return [level] * len(LAMBDAS)


def bump(center, width, peak, base=0.18):
    """一个高斯反射率峰，用来造"红的东西""绿的东西"。"""
    out = []
    for lam in LAMBDAS:
        v = base + peak * _g(lam, center, width, width)
        out.append(min(0.98, max(0.02, v)))
    return out


def reflectance(seed_center, seed_width, seed_peak, base=0.18):
    return bump(seed_center, seed_width, seed_peak, base)


class Rng:
    def __init__(self, seed):
        s = (1103515245 * seed + 12345) & 0x7FFFFFFF
        self.s = s or 0x9E3779B9

    def next(self):
        s = self.s
        s ^= (s << 13) & 0xFFFFFFFF
        s ^= s >> 17
        s ^= (s << 5) & 0xFFFFFFFF
        self.s = s & 0xFFFFFFFF
        return self.s

    def rand(self):
        return self.next() / 4294967296.0

    def uniform(self, lo, hi):
        return lo + (hi - lo) * self.rand()


def random_reflectance(rng):
    """随机平滑反射率：两三个高斯叠起来，裁到 [0.02, 0.98]。"""
    peaks = []
    for _ in range(rng.next() % 2 + 2):
        peaks.append((rng.uniform(420.0, 660.0), rng.uniform(20.0, 60.0),
                      rng.uniform(0.1, 0.55)))
    out = []
    for lam in LAMBDAS:
        v = rng.uniform(0.05, 0.25)
        for mu, sd, amp in peaks:
            v += amp * _g(lam, mu, sd, sd)
        out.append(min(0.98, max(0.02, v)))
    return out


def make_scene(n_patches, green_frac, seed=20261221):
    """造一个场景：若干随机色块，加上按比例混入的绿色块，末尾放一块白纸。"""
    rng = Rng(seed)
    patches = []
    n_green = int(round(n_patches * green_frac))
    for i in range(n_patches):
        if i < n_green:
            patches.append(('green', bump(550.0, 35.0, 0.55, base=0.10)))
        else:
            patches.append(('random', random_reflectance(rng)))
    patches.append(('white', flat(0.9)))
    return patches


def render(patches, T):
    """场景在某个光源下的相机三通道响应。"""
    e = planck_curve(T)
    out = []
    for kind, refl in patches:
        sp = [r * v for r, v in zip(refl, e)]
        out.append((kind, sensor_rgb(sp)))
    return out


# ---------------------------------------------------------------- 估白算法

def means(rgbs):
    return [sum(c[i] for c in rgbs) / len(rgbs) for i in range(3)]


def gains_from(est):
    m = sum(est) / 3.0
    return [m / max(v, 1e-12) for v in est]


def est_gray_world(rgbs):
    return means(rgbs)


def est_shades_of_gray(rgbs, p=6.0):
    out = []
    for i in range(3):
        acc = sum(c[i] ** p for c in rgbs) / len(rgbs)
        out.append(acc ** (1.0 / p))
    return out


def est_max_rgb(rgbs):
    return [max(c[i] for c in rgbs) for i in range(3)]


def est_known_gray(rgbs, kinds):
    idx = [i for i, k in enumerate(kinds) if k == 'white']
    return list(rgbs[idx[0]])


def angle_deg(a, b):
    na = math.sqrt(sum(v * v for v in a))
    nb = math.sqrt(sum(v * v for v in b))
    if na <= 0 or nb <= 0:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b)) / (na * nb)
    dot = max(-1.0, min(1.0, dot))
    return math.degrees(math.acos(dot))


def white_error(rgbs, kinds, gains):
    """把增益乘到白纸上，看它离中性轴（三通道相等）还差多少度。"""
    idx = [i for i, k in enumerate(kinds) if k == 'white'][0]
    c = [rgbs[idx][i] * gains[i] for i in range(3)]
    return angle_deg(c, [1.0, 1.0, 1.0])


def gain_ratio(gains):
    return max(gains) / min(gains)


# ---------------------------------------------------------------- 参考光源

D65_T = 6504
A_T = 2856
TEST_TS = (2000, 2856, 4000, 5000, 6504, 8000, 10000)


# ---------------------------------------------------------------- 实验

def planck_family():
    """几个色温下的相对光谱，归一化到各自峰值，给图用。"""
    out = []
    for T in (2000, 3000, 4500, 6500, 9000):
        sp = planck_curve(T)
        top = max(sp)
        out.append({'T': T, 'curve': [round(v / top, 6) for v in sp]})
    return {'lambdas': LAMBDAS, 'curves': out}


def locus():
    """黑体轨迹在两套色度坐标里的样子，以及"离谁最近"的两种算法。"""
    rows = []
    for T in range(1500, 20001, 25):
        x, y = xy_of(xyz_of(planck_curve(T)))
        u, v = uv1960(x, y)
        rows.append({'T': T, 'x': round(x, 6), 'y': round(y, 6),
                     'u': round(u, 6), 'v': round(v, 6)})
    return rows


def _nearest(rows, key_u, key_v):
    best = None
    for r in rows:
        d = (r[key_u]) ** 2 + (r[key_v]) ** 2
        if best is None or d < best[0]:
            best = (d, r['T'])
    return best[1]


def cct_compare():
    """同一组色坐标，用 xy 最近点与用 uv 最近点找到的色温差多少。"""
    rows = locus()
    probes = []
    for T in (2200, 2856, 3600, 5000, 6504, 9000, 12000):
        x, y = xy_of(xyz_of(planck_curve(T)))
        for dx, dy in ((0.0, 0.0), (0.012, -0.008), (-0.010, 0.014)):
            px, py = x + dx, y + dy
            u, v = uv1960(px, py)
            best = None
            for r in rows:
                d = (r['x'] - px) ** 2 + (r['y'] - py) ** 2
                if best is None or d < best[0]:
                    best = (d, r['T'])
            t_xy = best[1]
            best = None
            for r in rows:
                d = (r['u'] - u) ** 2 + (r['v'] - v) ** 2
                if best is None or d < best[0]:
                    best = (d, r['T'])
            t_uv = best[1]
            probes.append({'true_T': T, 'x': round(px, 6), 'y': round(py, 6),
                           'T_by_xy': t_xy, 'T_by_uv': t_uv,
                           'diff_k': abs(t_xy - t_uv)})
    return probes


def algorithms():
    """七种光源 × 两种场景 × 四种方法：把白纸调成白还差多少。

    场景 A 里有一张白纸（相机里的"白点"），场景 B 里没有。
    """
    out = []
    for label, has_white, seed in (('with_white', True, 11),
                                   ('no_white', False, 12)):
        patches = make_scene(20, 0.0, seed=seed)
        if not has_white:
            patches = [(k, r) for k, r in patches if k != 'white']
            patches = list(patches) + [('white', flat(0.9))]   # 只为算误差
            # 真白纸留在场景里但不参与估计：估白只看前面的色块
        kinds = [k for k, _ in patches]
        out.append({'scene': label, 'rows': []})
        for T in TEST_TS:
            rendered = render(patches, T)
            rgbs = [c for _, c in rendered]
            if has_white:
                vis = rgbs
            else:
                vis = rgbs[:-1]
            row = {'T': T, 'methods': {}}
            row['raw_err_deg'] = round(
                white_error(rgbs, kinds, [1.0, 1.0, 1.0]), 3)
            for name, est in (('gray_world', est_gray_world(vis)),
                              ('shades_p6', est_shades_of_gray(vis, 6.0)),
                              ('max_rgb', est_max_rgb(vis)),
                              ('known_gray', est_known_gray(rgbs, kinds))):
                g = gains_from(est)
                row['methods'][name] = {
                    'err_deg': round(white_error(rgbs, kinds, g), 3),
                    'gain_ratio': round(gain_ratio(g), 4),
                }
            e = illum_rgb(T)
            row['true_rb'] = round(e[0] / e[2], 4)
            idx = [i for i, k in enumerate(kinds) if k == 'white'][0]
            w = rgbs[idx]
            row['white_rgb'] = [round(v / max(w), 4) for v in w]
            out[-1]['rows'].append(row)
    return out


def dominance():
    """绿色块占比从 0 涨到九成，两种方法分别错到哪里。"""
    out = []
    for frac in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        patches = make_scene(20, frac, seed=11)
        kinds = [k for k, _ in patches]
        rgbs = [c for _, c in render(patches, 6504)]
        vis = rgbs[:-1]
        row = {'green_frac': frac}
        for name, est in (('gray_world', est_gray_world(vis)),
                          ('shades_p6', est_shades_of_gray(vis, 6.0)),
                          ('max_rgb', est_max_rgb(vis))):
            g = gains_from(est)
            row[name] = {'err_deg': round(white_error(rgbs, kinds, g), 3),
                         'gain_ratio': round(gain_ratio(g), 4)}
        out.append(row)
    return out


def _sensor_vecs():
    out = []
    for mu, sd in SENSORS:
        out.append([_g(lam, mu, sd, sd) for lam in LAMBDAS])
    return out


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _null_direction(center, width, T):
    """让相机三通道读数为零的光谱扰动。

    注意要减掉的是"光源 × 感光曲线"这三个方向，不是感光曲线本身：
    相机看到的是反射率乘上光源再乘感光曲线。
    """
    v = [_g(lam, center, width, width) for lam in LAMBDAS]
    e = planck_curve(T)
    basis = []
    for s in _sensor_vecs():
        s = [x * y for x, y in zip(s, e)]
        w = list(s)
        for q in basis:
            c = _dot(w, q)
            w = [w[i] - c * q[i] for i in range(len(w))]
        n = math.sqrt(_dot(w, w))
        basis.append([x / n for x in w])
    for q in basis:
        c = _dot(v, q)
        v = [v[i] - c * q[i] for i in range(len(v))]
    n = math.sqrt(_dot(v, v))
    return [x / n for x in v]


def metamer():
    """同一台相机、同一个光源，两种反射率给出一样的 RGB，人眼却看得出差别。

    做法不是碰运气搜索，而是直接构造：把光谱空间的扰动投影到相机三个
    通道的零空间里，那个方向上相机彻底看不见。
    """
    s = planck_curve(6504)
    rows = []
    for seed in (7, 21, 42):
        rng = Rng(seed)
        a = random_reflectance(rng)
        for center, width in ((470.0, 12.0), (540.0, 10.0), (610.0, 14.0),
                              (430.0, 9.0), (660.0, 16.0)):
            d = _null_direction(center, width, 6504)
            t_hi, t_lo = 1e9, 1e9
            for i in range(len(a)):
                if d[i] > 1e-9:
                    t_hi = min(t_hi, (0.98 - a[i]) / d[i])
                elif d[i] < -1e-9:
                    t_lo = min(t_lo, (a[i] - 0.02) / (-d[i]))
            t = 0.8 * min(t_hi, t_lo)
            if t <= 0 or t > 1e6:
                continue
            b = [a[i] + t * d[i] for i in range(len(a))]
            ra = sensor_rgb([x * v for x, v in zip(a, s)])
            rb = sensor_rgb([x * v for x, v in zip(b, s)])
            rel = max(abs(ra[i] - rb[i]) / max(ra[i], rb[i]) for i in range(3))
            xa = xy_of(xyz_of([x * v for x, v in zip(a, s)]))
            xb = xy_of(xyz_of([x * v for x, v in zip(b, s)]))
            ua, ub = uv1960(*xa), uv1960(*xb)
            duv = math.sqrt((ua[0] - ub[0]) ** 2 + (ua[1] - ub[1]) ** 2)
            dlab = math.sqrt(((xa[0] - xb[0]) * 100) ** 2
                             + ((xa[1] - xb[1]) * 100) ** 2)
            ra2 = sensor_rgb([x * v for x, v in zip(a, planck_curve(2856))])
            rb2 = sensor_rgb([x * v for x, v in zip(b, planck_curve(2856))])
            rel2 = max(abs(ra2[i] - rb2[i]) / max(ra2[i], rb2[i])
                       for i in range(3))
            rows.append({'seed': seed, 'center_nm': center,
                         'cam_rel': round(rel, 9),
                         'cam_rel_a': round(rel2, 6),
                         'uv_dist': round(duv, 6),
                         'xy_dist_x100': round(dlab, 4),
                         'x_a': round(xa[0], 5), 'y_a': round(xa[1], 5),
                         'x_b': round(xb[0], 5), 'y_b': round(xb[1], 5),
                         'spec_a': [round(v, 4) for v in a[::4]],
                         'spec_b': [round(v, 4) for v in b[::4]],
                         'rgb_a': [round(v / max(ra), 6) for v in ra],
                         'rgb_b': [round(v / max(rb), 6) for v in rb]})
    rows.sort(key=lambda r: -r['uv_dist'])
    return {'jnd_uv': 0.004, 'pairs': len(rows),
            'max_cam_rel': max(r['cam_rel'] for r in rows),
            'max_cam_rel_a': max(r['cam_rel_a'] for r in rows),
            'max_uv_dist': rows[0]['uv_dist'],
            'over_jnd': sum(1 for r in rows if r['uv_dist'] > 0.004),
            'rows': rows[:6]}


def sensor_cross():
    """换一套感光曲线，灰世界估出来的增益会变多少。

    说明"灰世界"不是物理定律，是关于场景的假设。
    """
    global SENSORS
    base = SENSORS
    patches = make_scene(20, 0.0, seed=11)
    kinds = [k for k, _ in patches]
    rows = []
    for name, sens in (('标准', ((600.0, 45.0), (545.0, 40.0), (450.0, 30.0))),
                       ('窄带', ((605.0, 25.0), (540.0, 22.0), (455.0, 18.0))),
                       ('宽带重叠', ((610.0, 70.0), (550.0, 65.0), (460.0, 60.0)))):
        SENSORS = sens
        rgbs = [c for _, c in render(patches, 6504)]
        g = gains_from(est_gray_world(rgbs))
        rows.append({'sensor': name,
                     'err_deg': round(white_error(rgbs, kinds, g), 3),
                     'gain_ratio': round(gain_ratio(g), 4)})
    SENSORS = base
    return rows


def spectral_locus():
    """单色光的色坐标，画出来就是那条马蹄形边界。"""
    out = []
    for i, lam in enumerate(LAMBDAS):
        sp = [0.0] * len(LAMBDAS)
        sp[i] = 1.0
        x, y = xy_of(xyz_of(sp))
        out.append({'nm': lam, 'x': round(x, 5), 'y': round(y, 5)})
    return out


def build():
    return {
        'config': {
            'lambdas': [LAMBDAS[0], LAMBDAS[-1], DLAM],
            'patches': 21,
            'd65': D65_T,
            'illuminant_a': A_T,
            'test_ts': list(TEST_TS),
            'spec_step_nm': 20,
            'seed': 20261221,
        },
        'planck_family': planck_family(),
        'locus': [r for r in locus() if r['T'] % 100 == 0],
        'spectral_locus': spectral_locus(),
        'cct': cct_compare(),
        'algorithms': algorithms(),
        'dominance': dominance(),
        'metamer': metamer(),
    }


if __name__ == '__main__':
    import json
    print(json.dumps(build(), ensure_ascii=False)[:1200])
