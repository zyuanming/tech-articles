"""跑出 results.json 与几张渲染图。只用标准库。

输出的每个数都是确定的：没有计时、没有随机种子以外的不确定来源。
成本用「求交测试次数」度量，不用秒——秒会随机器变，测试次数不会。
"""

import hashlib
import json
import math
import os
import random

import bvh

HERE = os.path.dirname(os.path.abspath(__file__))


def scene_serialisable(sc):
    """把场景压成画图要用的几个数组（俯视图用）。"""
    spheres = []
    for p in sc['prims']:
        if p.kind == 'sphere':
            spheres.append([p.c[0], p.c[1], p.c[2], p.r, 1 if p.mirror > 0 else 0])
    return spheres


def tree_boxes(root, depth_limit):
    """把前几层节点的包围盒导出来（俯视图画 x-z 投影）。"""
    out = []

    def walk(node, depth):
        if depth > depth_limit:
            return
        out.append({'depth': depth, 'lo': list(node.lo), 'hi': list(node.hi),
                    'leaf': node.items is not None})
        if node.left is not None:
            walk(node.left, depth + 1)
            walk(node.right, depth + 1)

    walk(root, 0)
    return out


def sample_rays(sc, w, h):
    b = bvh.basis(sc)
    rays = []
    for y in range(h):
        for x in range(w):
            rays.append(bvh.ray_dir(sc, x + 0.5, y + 0.5, w, h, b))
    return rays


def count_tests(sc, accel, rays):
    total = 0
    for d in rays:
        if accel is None:
            n = 0
            for p in sc['prims']:
                n += 1
                p.hit(sc['eye'], d, 1e9)
            total += n
        else:
            _h, tests, _nodes, _p = bvh.hit_bvh(accel, sc['eye'], d, 1e9)
            total += tests
    return total


def traversal_experiment(sc, root, rays):
    """三个变体的节点/求交计数：正常遍历、先远后近、关掉按距离剪枝。"""
    out = {}
    for name, kw in (('normal', {}), ('far_first', {'near_first': False}),
                     ('no_prune', {'prune': False})):
        tests = nodes = 0
        for d in rays:
            _h, t, n, _p = bvh.hit_bvh(root, sc['eye'], d, 1e9, **kw)
            tests += t
            nodes += n
        out[name] = {'tests': tests, 'nodes': nodes}
    return out


def sah_profile(prims, buckets=12):
    """根节点上，12 个候选分割点各自的 SAH 代价（左面积×左数 + 右面积×右数）。"""
    bounds = [p.bounds() for p in prims]
    cen = [bvh.centroid(p) for p in prims]
    lo = [min(b[0][i] for b in bounds) for i in range(3)]
    hi = [max(b[1][i] for b in bounds) for i in range(3)]
    extent = [hi[i] - lo[i] for i in range(3)]
    axis = extent.index(max(extent))
    clo = min(c[axis] for c in cen)
    chi = max(c[axis] for c in cen)
    scale = buckets / (chi - clo)
    bnd = [None] * buckets
    cnt = [0] * buckets
    for i in range(len(prims)):
        bi = min(buckets - 1, int((cen[i][axis] - clo) * scale))
        cnt[bi] += 1
        bnd[bi] = bounds[i] if bnd[bi] is None else bvh.union(bnd[bi], bounds[i])
    pre = [None] * buckets
    acc = None
    for i in range(buckets):
        if bnd[i] is not None:
            acc = bnd[i] if acc is None else bvh.union(acc, bnd[i])
        pre[i] = acc
    suf = [None] * buckets
    acc = None
    for i in range(buckets - 1, -1, -1):
        if bnd[i] is not None:
            acc = bnd[i] if acc is None else bvh.union(acc, bnd[i])
        suf[i] = acc
    rows = []
    nleft = 0
    for i in range(buckets - 1):
        nleft += cnt[i]
        if nleft == 0 or len(prims) - nleft == 0:
            rows.append({'split': i + 1, 'left': nleft, 'right': len(prims) - nleft,
                         'cost': None})
            continue
        cost = (bvh.surface_area(*pre[i]) * nleft
                + bvh.surface_area(*suf[i + 1]) * (len(prims) - nleft))
        rows.append({'split': i + 1, 'left': nleft, 'right': len(prims) - nleft,
                     'cost': cost})
    return {'axis': axis, 'rows': rows}


def main():
    out = {}

    sc = bvh.build_scene()
    out['scene'] = {
        'prims': len(sc['prims']),
        'spheres': sum(1 for p in sc['prims'] if p.kind == 'sphere'),
        'tiles': sum(1 for p in sc['prims'] if p.kind == 'plane'),
        'mirror_prims': sum(1 for p in sc['prims'] if p.mirror > 0),
    }

    builds = {}
    trees = {}
    for mode in ('mid', 'spatial', 'sah'):
        root, st = bvh.build_bvh(sc['prims'], mode)
        trees[mode] = root
        builds[mode] = {k: st[k] for k in ('nodes', 'leaves', 'depth', 'sort_ops', 'sah_ops')}
    out['build'] = builds
    out['sah_profile'] = sah_profile(sc['prims'])

    # ---- 同分辨率下「测试次数」的对比 ----
    W, H = 160, 90
    cmp_rows = {}
    for mode in ('mid', 'spatial', 'sah'):
        _rgb, c = bvh.render(sc, trees[mode], W, H)
        cmp_rows[mode] = {'tests': c['tests'], 'rays': c['rays'], 'nodes': c['nodes'],
                          'pruned': c['pruned'], 'tests_per_ray': c['tests'] / c['rays']}
    _rgb, c = bvh.render(sc, None, W, H)
    cmp_rows['naive'] = {'tests': c['tests'], 'rays': c['rays'], 'nodes': 0,
                         'pruned': 0, 'tests_per_ray': c['tests'] / c['rays']}
    assert cmp_rows['naive']['tests'] == cmp_rows['naive']['rays'] * len(sc['prims']), \
        '朴素遍历的测试次数应当正好是 光线数 × 图元数'
    sha = {}
    for mode in ('sah', 'naive'):
        raw = bvh.render(sc, trees[mode] if mode == 'sah' else None, W, H)[0]
        sha[mode] = hashlib.sha256(raw).hexdigest()
    out['compare'] = {'width': W, 'height': H, 'rows': cmp_rows,
                      'pixel_sha256': sha,
                      'identical': sha['sah'] == sha['naive']}
    out['speedup'] = cmp_rows['naive']['tests'] / cmp_rows['sah']['tests']

    # ---- 每像素测试次数（热力图） ----
    HW, HH = 160, 90
    heat = []
    rays = sample_rays(sc, HW, HH)
    for d in rays:
        _h, tests, _n, _p = bvh.hit_bvh(trees['sah'], sc['eye'], d, 1e9)
        heat.append(tests)
    out['heatmap'] = {'width': HW, 'height': HH, 'max': max(heat),
                      'mean': sum(heat) / len(heat), 'values': heat}

    # ---- 图元数增加时，每条光线的测试次数 ----
    rows = []
    for per_side in (2, 3, 4, 5, 6, 7):
        n = per_side ** 3
        s2 = bvh.build_scene(n_spheres=n)
        r2, _st = bvh.build_bvh(s2['prims'], 'sah')
        rs = sample_rays(s2, 72, 40)
        tb = count_tests(s2, r2, rs) / len(rs)
        tn = count_tests(s2, None, rs) / len(rs)
        rows.append({'spheres': n, 'prims': len(s2['prims']),
                     'bvh': tb, 'naive': tn, 'ratio': tn / tb})
    out['scaling'] = rows

    # ---- 遍历顺序 ----
    rs = sample_rays(sc, 80, 45)
    trav = traversal_experiment(sc, trees['sah'], rs)
    trav['rays'] = len(rs)
    out['traversal'] = trav

    # ---- 光线构成 ----
    b = bvh.basis(sc)
    counters = {'tests': 0, 'rays': 0, 'nodes': 0, 'pruned': 0}
    prim_rays = 0
    for y in range(90):
        for x in range(160):
            d = bvh.ray_dir(sc, x + 0.5, y + 0.5, 160, 90, b)
            prim_rays += 1
            bvh.trace(sc, trees['sah'], sc['eye'], d, 0, counters)
    out['rays'] = {'primary': prim_rays, 'total': counters['rays'],
                   'secondary_per_primary': (counters['rays'] - prim_rays) / prim_rays}

    # ---- 地板：一整块无限平面 vs 144 块砖（同一批光线） ----
    rooms = {}
    for tag in ('tiles', 'infinite'):
        s3 = bvh.build_scene(floor=tag)
        r3, st3 = bvh.build_bvh(s3['prims'], 'sah')
        rs3 = sample_rays(s3, 80, 45)
        tb3 = count_tests(s3, r3, rs3) / len(rs3)
        tn3 = count_tests(s3, None, rs3) / len(rs3)
        rooms[tag] = {'prims': len(s3['prims']), 'bvh': tb3, 'naive': tn3,
                      'ratio': tn3 / tb3, 'nodes': st3['nodes'],
                      'root_lo': list(r3.lo), 'root_hi': list(r3.hi),
                      'rays': len(rs3)}
    out['floor'] = rooms

    # ---- 俯视图与树的盒子 ----
    out['topview'] = {'spheres': scene_serialisable(sc),
                      'boxes': tree_boxes(trees['sah'], 2)}

    # ---- 正式出图的两张渲染（不参与统计，只给正文用） ----
    _rgb, c_hero = bvh.render(sc, trees['sah'], 320, 180, aa=2)
    out['hero'] = {'width': 320, 'height': 180, 'aa': 2,
                   'primary_pixels': 320 * 180, 'rays': c_hero['rays'],
                   'tests': c_hero['tests'],
                   'naive_tests': c_hero['rays'] * len(sc['prims'])}

    with open(os.path.join(HERE, 'results.json'), 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write('\n')
    print('results.json', os.path.getsize(os.path.join(HERE, 'results.json')), 'bytes')
    print('speedup %.1fx, tests/ray bvh %.1f naive %.1f' % (
        out['speedup'], cmp_rows['sah']['tests_per_ray'], cmp_rows['naive']['tests_per_ray']))


if __name__ == '__main__':
    main()
