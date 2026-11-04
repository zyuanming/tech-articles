"""深度缓冲精度的小模型。MIT。

所有量都是解析式加「按格式真实量化」：定点深度按 2^-24 取整，浮点深度用
struct 走一遍 float32。分辨率的求法是对每个距离做一次二分，找「再挪多远，
量化后的深度值才会变」。
"""
from __future__ import annotations

import math
import struct

Q24 = 1.0 / (1 << 24)


def f32(x):
    """把一个 Python float 舍入到 float32。"""
    return struct.unpack('<f', struct.pack('<f', x))[0]


def std_depth(z, near, far):
    """D3D 约定：[0,1]，近平面 → 0，远平面 → 1。"""
    return (far / (far - near)) * (1.0 - near / z)


def rev_depth(z, near, far):
    """反转深度：近平面 → 1，远平面 → 0。"""
    return 1.0 - std_depth(z, near, far)


def gl_depth(z, near, far):
    """OpenGL 默认约定：[−1,1]。"""
    return ((far + near) * z - 2.0 * far * near) / ((far - near) * z)


def q_fixed(v, bits=24):
    """定点格式：均匀网格，步长 2^-bits。"""
    step = 1.0 / (1 << bits)
    return math.floor(v / step + 0.5) * step


def q_float(v):
    return f32(v)


def eye_step(z, near, far, depth, quant, limit=60):
    """在距离 z 处，量化后的深度值还能分开多小的间隔（米）。"""
    base = quant(depth(z, near, far))
    lo, hi = 0.0, z * 0.9
    for _ in range(limit):
        mid = 0.5 * (lo + hi)
        if quant(depth(z + mid, near, far)) != base:
            hi = mid
        else:
            lo = mid
    return hi


def visible(z, sep, near, far, depth, quant):
    """距离 z 处，相隔 sep 米的两个面能不能被深度值分开。"""
    a = quant(depth(z, near, far))
    b = quant(depth(z + sep, near, far))
    return a != b


def log_depths(near, far, count):
    """近平面到远平面之间按对数分布的距离，用于统计相邻点被并成一格的比例。"""
    lo, hi = math.log(near), math.log(far)
    return [math.exp(lo + (hi - lo) * i / (count - 1)) for i in range(count)]


def collapse_count(zs, near, far, depth, quant, decreasing=False):
    """相邻两点量化后相同（indist）与顺序颠倒（swap）的次数。

    `decreasing=True` 用于反转深度：距离越远存的数越小，正常的相邻关系是
    a > b，颠倒才是错的。
    """
    vals = [quant(depth(z, near, far)) for z in zs]
    indist = sum(1 for a, b in zip(vals, vals[1:]) if a == b)
    if decreasing:
        swap = sum(1 for a, b in zip(vals, vals[1:]) if a < b)
    else:
        swap = sum(1 for a, b in zip(vals, vals[1:]) if a > b)
    return indist, swap


def merge_prob(z, sep, near, far, depth, quant):
    """相隔 sep 的两个面在这一距离上被压成同一个深度值的概率。

    间隙比一个格距小的时候，两个面要么正好跨在格边两侧、要么落在同一格里，
    比例就是 1 − sep/格距；间隙比格距大就一定有保证。
    """
    cell = eye_grid(z, near, far, depth, quant)
    return min(1.0, max(0.0, 1.0 - sep / cell))


def z_for_cell(target, near, far, depth, quant, lo=1e-3, hi=None, limit=60):
    """格距长到 target 米时的距离。格距随距离单调增，可以直接二分。"""
    hi = hi or (far * 0.999)
    if eye_grid(lo, near, far, depth, quant) > target:
        return lo
    if eye_grid(hi, near, far, depth, quant) <= target:
        return hi
    a, b = lo, hi
    for _ in range(limit):
        mid = 0.5 * (a + b)
        if eye_grid(mid, near, far, depth, quant) <= target:
            a = mid
        else:
            b = mid
    return a


def threshold_distance(sep, near, far, depth, quant, lo=0.01, hi=None, limit=60):
    """相隔 sep 米仍能被分开的最远距离（二分）。"""
    hi = hi or (far * 0.999)
    if not visible(lo, sep, near, far, depth, quant):
        return None
    if visible(hi, sep, near, far, depth, quant):
        return hi
    a, b = lo, hi
    for _ in range(limit):
        mid = 0.5 * (a + b)
        if visible(mid, sep, near, far, depth, quant):
            a = mid
        else:
            b = mid
    return a


# ---------------------------------------------------------------- float32 流水线

def matmul_f32(A, B):
    out = []
    for i in range(4):
        row = []
        for j in range(4):
            acc = 0.0
            for k in range(4):
                acc = f32(acc + f32(A[i][k] * B[k][j]))
            row.append(acc)
        out.append(row)
    return out


def matvec_f32(M, v):
    out = []
    for i in range(4):
        acc = 0.0
        for k in range(4):
            acc = f32(acc + f32(M[i][k] * v[k]))
        out.append(acc)
    return out


def projection(near, far, f=1.0, aspect=1.0, reverse=False):
    """右手系、看向 −z，D3D [0,1] 深度范围的投影矩阵。

    `reverse=True` 给的是反转深度的矩阵：25 角直接算出 1 − d，不用事后减，
    所以精度不会被这次减法吃掉。
    """
    if reverse:
        a = near / (far - near)
        b = far * near / (far - near)
    else:
        a = -far / (far - near)
        b = -far * near / (far - near)
    return [
        [f / aspect, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, a, b],
        [0.0, 0.0, -1.0, 0.0],
    ]


def translate_z(t):
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, t],
        [0.0, 0.0, 0.0, 1.0],
    ]


def clip_depth(clip):
    zc, wc = clip[2], clip[3]
    if wc == 0.0:
        return None
    return f32(zc / wc)


def pipeline_pair(camera_z, near, far, depths, reverse=False):
    """同一条 view + projection，两条算法路径：

    A：先乘成 M = P·V，再拿 M 乘点（4 次点积，元素是复合出来的大数）。
    B：先 V 乘点，再 P 乘结果（投影矩阵保持原样）。
    """
    P = projection(near, far, reverse=reverse)
    V = translate_z(-camera_z)
    M = matmul_f32(P, V)
    out = []
    for zw in depths:
        p = [0.0, 0.0, zw, 1.0]
        a = clip_depth(matvec_f32(M, p))
        b = clip_depth(matvec_f32(P, matvec_f32(V, p)))
        out.append((a, b))
    return out


def order_errors(vals, decreasing=False):
    """(indist, swap)：相邻两项在量化后的深度里合并或颠倒的次数。"""
    indist = sum(1 for a, b in zip(vals, vals[1:]) if a is not None and a == b)
    if decreasing:
        swap = sum(1 for a, b in zip(vals, vals[1:])
                   if a is not None and b is not None and a < b)
    else:
        swap = sum(1 for a, b in zip(vals, vals[1:])
                   if a is not None and b is not None and a > b)
    return indist, swap


def float_cell(v):
    """float32 在 v 处的间距（ULP）。"""
    if v == 0.0:
        return 2.0 ** -24
    _, e = math.frexp(abs(v))
    return 2.0 ** (e - 24)


def cell_at(v, quant):
    return Q24 if quant is q_fixed else float_cell(v)


def eye_grid(z, near, far, depth, quant):
    """在该距离处，量化网格投影到 z 轴上的间距（米）。

    格距取该处深度值的 ULP（定点就是 2^-24），再除以 |dd/dz| —— 导数用中心
    差分在双精度里算，步长是 z 的百万分之一。比「二分找第一次跨格」稳，后者
    量到的是从当前位置到下一个边界的距离，随相位在 0 到一个格距之间乱跳。
    """
    v = depth(z, near, far)
    h = max(abs(z) * 1e-6, 1e-12)
    dv = (depth(z + h, near, far) - depth(z - h, near, far)) / (2.0 * h)
    return cell_at(v, quant) / abs(dv)
