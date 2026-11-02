"""光线追踪的最小实现：一个球阵场景、三种加速结构，以及可以数出来的代价。

只算「这条光线要跟多少个图元做求交」和「建树做了多少次比较」，不算 SIMD、
不算 GPU、不算打包遍历。所有图元都是球或平面，求交公式精确，没有近似。
"""

import math
import random

# ---------- 向量 ----------


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def norm(a):
    n = math.sqrt(dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


def reflect(d, n):
    return sub(d, mul(n, 2.0 * dot(d, n)))


# ---------- 图元 ----------


class Sphere:
    """球：求交只要解一个一元二次方程。"""

    kind = 'sphere'

    def __init__(self, c, r, albedo, mirror=0.0):
        self.c = c
        self.r = r
        self.albedo = albedo
        self.mirror = mirror

    def bounds(self):
        r = self.r
        return (sub(self.c, (r, r, r)), add(self.c, (r, r, r)))

    def hit(self, o, d, tmax):
        oc = sub(o, self.c)
        b = dot(oc, d)
        c = dot(oc, oc) - self.r * self.r
        disc = b * b - c
        if disc < 0.0:
            return None
        s = math.sqrt(disc)
        t = -b - s
        if t <= 1e-4:
            t = -b + s
            if t <= 1e-4:
                return None
        if t >= tmax:
            return None
        p = add(o, mul(d, t))
        return t, norm(sub(p, self.c)), self, 1 + 3 + 1   # 大致浮点运算次数，只用于说明量级

    def normal(self, p):
        return norm(sub(p, self.c))


class Plane:
    """无限平面：求交是一次除法。用来当地板和天花板。"""

    kind = 'plane'

    def __init__(self, n, d, albedo, mirror=0.0, half=None, center=(0.0, 0.0, 0.0)):
        self.n = norm(n)
        self.d = d
        self.albedo = albedo
        self.mirror = mirror
        self.half = half
        self.center = center

    def bounds(self):
        if self.half is None:
            big = 1e6
            return ((-big, -big, -big), (big, big, big))
        hx, hz = self.half
        cx, cz = self.center[0], self.center[2]
        y = self.center[1]
        return ((cx - hx, y - 0.05, cz - hz), (cx + hx, y + 0.05, cz + hz))

    def hit(self, o, d, tmax):
        den = dot(self.n, d)
        if abs(den) < 1e-9:
            return None
        t = (self.d - dot(self.n, o)) / den
        if t <= 1e-4 or t >= tmax:
            return None
        p = add(o, mul(d, t))
        if self.half is not None:
            hx, hz = self.half
            if abs(p[0] - self.center[0]) > hx or abs(p[2] - self.center[2]) > hz:
                return None
        return t, self.n, self, 1 + 2

    def normal(self, p):
        return self.n


# ---------- 包围盒 ----------


def slab(o, d, lo, hi):
    """光线与轴对齐包围盒求交：三对平板，取交。返回进入参数 t0 或 None。

    d 的某个分量为 0 时要单独处理（否则除零），这是最容易写错的地方。
    """
    t0 = 0.0
    t1 = float('inf')
    for i in range(3):
        di = d[i]
        oi = o[i]
        if abs(di) < 1e-12:
            if oi < lo[i] or oi > hi[i]:
                return None
            continue
        inv = 1.0 / di
        a = (lo[i] - oi) * inv
        b = (hi[i] - oi) * inv
        if a > b:
            a, b = b, a
        if a > t0:
            t0 = a
        if b < t1:
            t1 = b
        if t0 > t1:
            return None
    return t0


def surface_area(lo, hi):
    dx = hi[0] - lo[0]
    dy = hi[1] - lo[1]
    dz = hi[2] - lo[2]
    return 2.0 * (dx * dy + dy * dz + dz * dx)


def union(a, b):
    return (
        (min(a[0][0], b[0][0]), min(a[0][1], b[0][1]), min(a[0][2], b[0][2])),
        (max(a[1][0], b[1][0]), max(a[1][1], b[1][1]), max(a[1][2], b[1][2])),
    )


# ---------- 场景 ----------


def build_scene(n_spheres=320, seed=5, floor='tiles'):
    """一个「球阵隧道」：球围成一圈圈的环，沿着视线往纵深排开。

    相机站在隧道口往里看，下面是反光地板，上面是天花板。灯的功率大、
    位置偏左上，球在地面和彼此身上投下长影子。
    """
    rnd = random.Random(seed)
    prims = []
    # 地板不是一整块「无限大的平面」，而是 12×12 块小方砖。原因见正文：
    # 一块无限大的平面会让它的包围盒盖住整个场景，盒子就白套了。
    n_tile = 12
    step = 1.2
    if floor == 'infinite':
        # 反例：一整块「无限大」的平面。数学上它和下面的砖地等价，
        # 但它的包围盒是一百万单位见方，会把整棵 BVH 的第一层废掉。
        prims.append(Plane((0, 1, 0), 0.0, (0.70, 0.72, 0.77), mirror=0.22))
    else:
        for ix in range(n_tile):
            for iz in range(n_tile):
                cx = (ix - (n_tile - 1) / 2.0) * step
                cz = 6.0 + (iz - (n_tile - 1) / 2.0) * step
                dark = (ix + iz) % 2 == 0
                alb = (0.66, 0.68, 0.74) if dark else (0.74, 0.76, 0.80)
                prims.append(Plane((0, 1, 0), 0.0, alb, mirror=0.22,
                                   half=(step / 2.0, step / 2.0),
                                   center=(cx, 0.0, cz)))
    per_ring = 18
    cy, rad = 2.95, 2.55
    placed = 0
    iz = 0
    while placed < n_spheres:
        for k in range(per_ring):
            if placed >= n_spheres:
                break
            ang = 2.0 * math.pi * k / per_ring + 0.16 * iz
            r = rnd.uniform(0.42, 0.62)
            x = rad * math.cos(ang) + rnd.uniform(-0.12, 0.12)
            y = cy + rad * math.sin(ang) + rnd.uniform(-0.12, 0.12)
            z = 3.0 + iz * 0.86 + rnd.uniform(-0.10, 0.10)
            hue = 0.5 + 0.5 * math.sin(1.7 * k + 0.9 * iz)
            albedo = (0.26 + 0.60 * hue,
                      0.38 + 0.34 * (1.0 - hue),
                      0.46 + 0.34 * (1.0 - 0.5 * hue))
            mirror = 0.85 if (k + 2 * iz) % 9 == 0 else 0.0
            prims.append(Sphere((x, y, z), r, albedo, mirror))
            placed += 1
        iz += 1
    light = Sphere((-0.9, 3.9, 1.1), 0.34, (1.0, 0.96, 0.88))
    return {'prims': prims, 'light': light, 'eye': (0.0, 2.95, -2.1),
            'target': (0.0, 3.0, 6.0), 'up': (0.0, 1.0, 0.0), 'fov': 62.0,
            'sky': ((0.04, 0.05, 0.08), (0.15, 0.19, 0.30))}


# ---------- 逐个求交（没有加速结构） ----------


def hit_all(prims, o, d, tmax):
    best = None
    tests = 0
    for p in prims:
        tests += 1
        h = p.hit(o, d, tmax)
        if h is not None and h[0] < tmax:
            tmax = h[0]
            best = h
    return best, tests


# ---------- BVH ----------


class Node:
    __slots__ = ('lo', 'hi', 'left', 'right', 'items', 'axis')

    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi
        self.left = None
        self.right = None
        self.items = None
        self.axis = -1


def centroid(p):
    lo, hi = p.bounds()
    return ((lo[0] + hi[0]) * 0.5, (lo[1] + hi[1]) * 0.5, (lo[2] + hi[2]) * 0.5)


def build_bvh(prims, mode='sah', leaf_size=4, buckets=12):
    """三种切法：mid（按质心中位数对半）、spatial（空间等分）、sah（分桶代价最小）。"""
    stats = {'mode': mode, 'nodes': 0, 'leaves': 0, 'depth': 0,
             'sort_ops': 0, 'sah_ops': 0, 'items': len(prims)}
    bounds = [p.bounds() for p in prims]
    cen = [centroid(p) for p in prims]
    idx = list(range(len(prims)))

    def make(start, end, depth):
        lo = list(bounds[idx[start]][0])
        hi = list(bounds[idx[start]][1])
        for k in range(start + 1, end):
            b = bounds[idx[k]]
            for i in range(3):
                if b[0][i] < lo[i]:
                    lo[i] = b[0][i]
                if b[1][i] > hi[i]:
                    hi[i] = b[1][i]
        node = Node(tuple(lo), tuple(hi))
        stats['nodes'] += 1
        if depth > stats['depth']:
            stats['depth'] = depth
        n = end - start
        if n <= leaf_size:
            node.items = [prims[i] for i in idx[start:end]]
            stats['leaves'] += 1
            return node

        extent = [hi[i] - lo[i] for i in range(3)]
        axis = extent.index(max(extent))
        node.axis = axis
        mid = None

        if mode == 'mid':
            idx[start:end] = sorted(idx[start:end], key=lambda i: cen[i][axis])
            stats['sort_ops'] += int(n * math.log2(n)) if n > 1 else 0
            mid = (start + end) // 2
        elif mode == 'spatial':
            split = (lo[axis] + hi[axis]) * 0.5
            a = [i for i in idx[start:end] if cen[i][axis] < split]
            b = [i for i in idx[start:end] if cen[i][axis] >= split]
            stats['sort_ops'] += n
            if a and b:
                idx[start:end] = a + b
                mid = start + len(a)
            else:
                mid = (start + end) // 2
        if mode == 'sah':
            clo = min(cen[i][axis] for i in idx[start:end])
            chi = max(cen[i][axis] for i in idx[start:end])
            if chi - clo < 1e-9:
                mid = (start + end) // 2
            else:
                scale = buckets / (chi - clo)
                bnd = [None] * buckets
                cnt = [0] * buckets
                for k in range(start, end):
                    i = idx[k]
                    b = bounds[i]
                    bi = min(buckets - 1, int((cen[i][axis] - clo) * scale))
                    cnt[bi] += 1
                    bnd[bi] = b if bnd[bi] is None else union(bnd[bi], b)
                # 前缀盒 / 后缀盒：各扫一遍，O(buckets)
                pre = [None] * buckets
                acc = None
                for i in range(buckets):
                    if bnd[i] is not None:
                        acc = bnd[i] if acc is None else union(acc, bnd[i])
                    pre[i] = acc
                suf = [None] * buckets
                acc = None
                for i in range(buckets - 1, -1, -1):
                    if bnd[i] is not None:
                        acc = bnd[i] if acc is None else union(acc, bnd[i])
                    suf[i] = acc
                best = None
                best_cost = None
                nleft = 0
                for i in range(buckets - 1):
                    nleft += cnt[i]
                    stats['sah_ops'] += 1
                    if nleft == 0 or n - nleft == 0:
                        continue
                    lb = pre[i]
                    rb = suf[i + 1]
                    if lb is None or rb is None:
                        continue
                    cost = surface_area(*lb) * nleft + surface_area(*rb) * (n - nleft)
                    if best_cost is None or cost < best_cost:
                        best_cost = cost
                        best = i + 1
                if best is None:
                    mid = (start + end) // 2
                else:
                    split = clo + (chi - clo) * (best / buckets)
                    a = [i for i in idx[start:end] if cen[i][axis] < split]
                    b = [i for i in idx[start:end] if cen[i][axis] >= split]
                    if not a or not b:
                        mid = (start + end) // 2
                    else:
                        idx[start:end] = a + b
                        mid = start + len(a)
        node.left = make(start, mid, depth + 1)
        node.right = make(mid, end, depth + 1)
        return node

    root = make(0, len(idx), 0)
    return root, stats


def hit_bvh(root, o, d, tmax, near_first=True, prune=True):
    """遍历：先测盒，再进子树。

    已经命中过东西之后，tmax 会变小；进入参数比 tmax 还远的盒子直接跳过——
    这一步叫「按距离剪枝」，省下来的不是求交，是整棵子树。
    """
    best = None
    tests = 0
    nodes = 0
    pruned = 0
    stack = [root]
    while stack:
        node = stack.pop()
        nodes += 1
        t0 = slab(o, d, node.lo, node.hi)
        if t0 is None or (prune and t0 >= tmax):
            pruned += 1
            continue
        if node.items is not None:
            for p in node.items:
                tests += 1
                h = p.hit(o, d, tmax)
                if h is not None and h[0] < tmax:
                    tmax = h[0]
                    best = h
            continue
        if near_first and node.axis >= 0 and abs(d[node.axis]) > 1e-12:
            tl = slab(o, d, node.left.lo, node.left.hi)
            tr = slab(o, d, node.right.lo, node.right.hi)
            # 远的先压栈、近的后压：后进先出，于是先走近的那一侧
            if tl is not None and (tr is None or tl <= tr):
                stack.append(node.right)
                stack.append(node.left)
            else:
                stack.append(node.left)
                stack.append(node.right)
        else:
            stack.append(node.right)
            stack.append(node.left)
    return best, tests, nodes, pruned


# ---------- 渲染 ----------


def sky_color(scene, d):
    t = 0.5 * (d[1] + 1.0)
    a, b = scene['sky']
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def trace(scene, accel, o, d, depth, counters):
    """Whitted 风格：一次漫反射阴影 + 最多一次镜面反射。"""
    if depth > 1:
        return (0.0, 0.0, 0.0)
    counters['rays'] += 1
    if accel is None:
        h, tests = hit_all(scene['prims'], o, d, 1e9)
        counters['tests'] += tests
    else:
        h, tests, nodes, pruned = hit_bvh(accel, o, d, 1e9)
        counters['tests'] += tests
        counters['nodes'] += nodes
        counters['pruned'] += pruned
    if h is None:
        return sky_color(scene, d)
    t, n, prim, _ops = h
    p = add(o, mul(d, t))
    if dot(n, d) > 0.0:
        n = mul(n, -1.0)
    alb = prim.albedo
    light = scene['light']
    to_l = sub(light.c, p)
    dist = math.sqrt(dot(to_l, to_l))
    ldir = mul(to_l, 1.0 / dist)
    lam = dot(n, ldir)
    shade = (0.10, 0.11, 0.14)
    if lam > 0.0:
        so = add(p, mul(n, 1e-3))
        counters['rays'] += 1
        if accel is None:
            sh, st = hit_all(scene['prims'], so, ldir, dist)
            counters['tests'] += st
        else:
            sh, st, sn, sp = hit_bvh(accel, so, ldir, dist)
            counters['tests'] += st
            counters['nodes'] += sn
            counters['pruned'] += sp
        if sh is None:
            k = lam * 1.2 / (1.0 + 0.05 * dist * dist)
            shade = (shade[0] + alb[0] * k, shade[1] + alb[1] * k, shade[2] + alb[2] * k)
    if prim.mirror > 0.0:
        r = reflect(d, n)
        ro = add(p, mul(n, 1e-3))
        c = trace(scene, accel, ro, r, depth + 1, counters)
        m = prim.mirror
        shade = (shade[0] * (1 - m) + c[0] * m,
                 shade[1] * (1 - m) + c[1] * m,
                 shade[2] * (1 - m) + c[2] * m)
    return shade


def basis(scene):
    eye = scene['eye']
    fwd = norm(sub(scene['target'], eye))
    right = norm(cross(fwd, scene['up']))
    up = norm(cross(right, fwd))
    return fwd, right, up


def ray_dir(scene, fx, fy, w, h, b):
    fwd, right, up = b
    scale = math.tan(math.radians(scene['fov']) * 0.5)
    aspect = w / h
    sx = (2.0 * fx / w - 1.0) * scale * aspect
    sy = (1.0 - 2.0 * fy / h) * scale
    return norm(add(add(fwd, mul(right, sx)), mul(up, sy)))


def gamma(v):
    if v <= 0.0:
        return 0
    if v >= 1.0:
        return 255
    return int(255.0 * (v ** (1.0 / 2.2)) + 0.5)


def render(scene, accel, w, h, aa=1, counters=None):
    '''返回 (rgb 字节, 统计)。aa=2 表示每个像素 2x2 超采样。'''
    if counters is None:
        counters = {'tests': 0, 'rays': 0, 'nodes': 0, 'pruned': 0}
    b = basis(scene)
    eye = scene['eye']
    px = bytearray()
    inv = 1.0 / (aa * aa)
    for y in range(h):
        for x in range(w):
            acc = [0.0, 0.0, 0.0]
            for sy in range(aa):
                for sx in range(aa):
                    d = ray_dir(scene, x + (sx + 0.5) / aa, y + (sy + 0.5) / aa, w, h, b)
                    c = trace(scene, accel, eye, d, 0, counters)
                    acc[0] += c[0]
                    acc[1] += c[1]
                    acc[2] += c[2]
            px.append(gamma(acc[0] * inv))
            px.append(gamma(acc[1] * inv))
            px.append(gamma(acc[2] * inv))
    return bytes(px), counters


def write_ppm(path, w, h, rgb):
    with open(path, 'wb') as f:
        f.write(('P6\n%d %d\n255\n' % (w, h)).encode('ascii'))
        f.write(rgb)
