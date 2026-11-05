"""色调映射用到的最小工具集：只有标准库。

单位约定：
    场景亮度 x 是相对值（1.0 = 刚好能直接显示的白色）
    曲线输出 y 是 0..1 的显示值
    sRGB 编码把 y 变成显示器要的电平，再乘 255 得到 8 位码值
"""


# ----------------------------------------------------------------- sRGB 编解码

def srgb_decode(c):
    """sRGB 电平（0..1）→ 线性光量。IEC 61966-2-1 的分段式。"""
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def srgb_encode(v):
    """线性光量（0..1）→ sRGB 电平（0..1）。"""
    v = min(max(v, 0.0), 1.0)
    if v <= 0.0031308:
        return v * 12.92
    return 1.055 * v ** (1.0 / 2.4) - 0.055


def code8(v):
    """线性光量 → 8 位码值。四舍五入，不在本文件里做抖动。"""
    return int(round(srgb_encode(v) * 255))


# ------------------------------------------------------------------- 四条曲线

def clamp01(x):
    """什么都不做：超过 1 就截断。基线，用来显示「不映射」的代价。"""
    return min(max(x, 0.0), 1.0)


def reinhard(x):
    """Reinhard 2002 的最简式 y = x / (1 + x)。"""
    return clamp01(x / (1.0 + x))


def reinhard_white(x, white):
    """带白点版本：让指定的 white 正好映射到 1。

    y = x * (1 + x / white^2) / (1 + x)
    """
    y = x * (1.0 + x / (white * white)) / (1.0 + x)
    return clamp01(y)


def aces_fit(x):
    """ACES 影调曲线的有理拟合：引擎里常见的一条近似，不是官方 RRT+ODT。

    本稿没有取到这个拟合的一手出处，只当它是「一条常用的近似曲线」用。

    y = x (2.51 x + 0.03) / (x (2.43 x + 0.59) + 0.14)
    """
    num = x * (2.51 * x + 0.03)
    den = x * (2.43 * x + 0.59) + 0.14
    return clamp01(num / den)


CURVES = [
    ('截断', clamp01),
    ('Reinhard', reinhard),
    ('白点 8', lambda x: reinhard_white(x, 8.0)),
    ('ACES 拟合', aces_fit),
]


# ------------------------------------------------------------------ 度量工具

def loglog_slope(f, x, h=1e-4):
    """曲线在 x 处的对数斜率：输入变一个 stop，输出变几个 stop。

    1 表示对比度原样保留，0.2 表示只剩两成。
    """
    y0 = f(x * (1.0 - h))
    y1 = f(x * (1.0 + h))
    if y0 <= 0.0 or y1 <= 0.0:
        return 0.0
    import math
    return (math.log(y1) - math.log(y0)) / (math.log(x * (1.0 + h)) - math.log(x * (1.0 - h)))


def codes_in_range(f, lo, hi, samples=4000):
    """[lo, hi] 这段输入里，屏幕上出现多少个不同的 8 位码值。"""
    seen = set()
    for i in range(samples):
        x = lo + (hi - lo) * i / (samples - 1)
        seen.add(code8(f(x)))
    return len(seen)


def ramp_stats(f, hi, samples=8192):
    """把 [0, hi] 的连续渐变送进曲线，看输出码值用掉几个、最长一段重复多长。

    重复越长，屏幕上就会出现越宽的「色带」。
    """
    prev = None
    used = 0
    runs = []
    run = 0
    for i in range(samples):
        x = hi * i / (samples - 1)
        c = code8(f(x))
        if c != prev:
            used += 1
            if run:
                runs.append(run)
            run = 0
            prev = c
        else:
            run += 1
    if run:
        runs.append(run)
    return {'codes': used, 'longest_run': max(runs) if runs else 0,
            'samples_per_code': samples / max(used, 1)}
