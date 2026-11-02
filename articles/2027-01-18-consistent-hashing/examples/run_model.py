#!/usr/bin/env python3
"""跑出 numbers.json 里的所有数字。只用标准库。"""

import json
import os
import sys

import ch

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = 200_000
N0, N1 = 10, 11


def main():
    out = {}
    keys = ch.make_keys(KEYS)
    nodes = ch.node_names(N0)
    nodes11 = ch.node_names(N1)
    nodes9 = ch.node_names(N0 - 1)

    out['setup'] = {'keys': len(keys), 'nodes': N0, 'space': '2^64'}

    # ---------------- 1. 扩容：加一台机器，多少 key 要搬家 ----------------
    mod10, mod11 = ch.Modulo(nodes), ch.Modulo(nodes11)
    jump10 = lambda k: 'bucket-%02d' % ch.jump_owner(k, N0)
    jump11 = lambda k: 'bucket-%02d' % ch.jump_owner(k, N1)
    ring1, ring1b = ch.Ring(nodes, 1), ch.Ring(nodes11, 1)
    ring128, ring128b = ch.Ring(nodes, 128), ch.Ring(nodes11, 128)
    ring_pt1 = ch.Ring(nodes, 1, tag='v2:')
    ring_pt1b = ch.Ring(nodes11, 1, tag='v2:')

    grow = {
        'modulo': ch.moved_fraction(mod10.owner, mod11.owner, keys),
        'ring_v1': ch.moved_fraction(ring1.owner, ring1b.owner, keys),
        'ring_v128': ch.moved_fraction(ring128.owner, ring128b.owner, keys),
        'jump': ch.moved_fraction(jump10, jump11, keys),
        'ring_v1_other_hash': ch.moved_fraction(ring_pt1.owner, ring_pt1b.owner, keys),
    }
    out['grow'] = grow
    out['grow']['ideal'] = 1.0 / N1

    # ---------------- 2. 缩容 / 一台机器挂掉 ----------------
    mod9 = ch.Modulo(nodes9)
    ring128_9 = ch.Ring(nodes9, 128)
    shrink = {
        'modulo': ch.moved_fraction(mod10.owner, mod9.owner, keys),
        'ring_v128': ch.moved_fraction(ring128.owner, ring128_9.owner, keys),
        'jump': ch.moved_fraction(
            jump10, lambda k: 'bucket-%02d' % ch.jump_owner(k, N0 - 1), keys),
    }
    out['shrink'] = shrink
    out['shrink']['ideal'] = 1.0 / N0

    # ---------------- 3. 虚拟节点数与负载均衡 ----------------
    rows = []
    for v in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024):
        r = ch.Ring(nodes, v)
        counts = r.load(keys)
        rr = ch.ratios(counts)
        arcs = r.arcs()
        arc_len = [e - s for s, e, _ in arcs]
        # 每节点弧长总和（这才是"节点分到的空间"）
        per_node_arc = {n: 0 for n in nodes}
        for s, e, nd in arcs:
            per_node_arc[nd] += e - s
        rr_arc = ch.ratios(per_node_arc)
        steps = [r.owner_steps(k)[1] for k in keys[:20000]]
        rows.append({'vnodes': v, 'points': len(r.points),
                     'load_max': rr['max'], 'load_min': rr['min'],
                     'load_stdev': rr['stdev'],
                     'arc_max': rr_arc['max'], 'arc_min': rr_arc['min'],
                     'max_arc_share': max(arc_len) / sum(arc_len),
                     'steps': ch.mean(steps),
                     'lookup_ms': None})
        print('v=%-5d points=%-6d load max/mean=%.3f min/mean=%.3f stdev=%.3f steps=%.2f'
              % (v, len(r.points), rr['max'], rr['min'], rr['stdev'], ch.mean(steps)))
    out['vnodes'] = rows

    # ---------------- 4. 两种虚拟节点数的每节点负载 ----------------
    hist = {}
    for v in (1, 128):
        r = ch.Ring(nodes, v)
        counts = r.load(keys)
        hist['v%d' % v] = [counts[n] for n in nodes]
    out['hist'] = hist

    # ---------------- 5. 环上的弧段（画彩条用） ----------------
    strips = {}
    for v in (1, 16):
        r = ch.Ring(nodes, v)
        strips['v%d' % v] = [{'start': s / ch.SPACE, 'end': (e - ch.SPACE if e > ch.SPACE else e) / ch.SPACE,
                              'node': n} for s, e, n in r.arcs()]
    out['strips'] = strips

    # ---------------- 6. jump hash 的循环次数 ----------------
    jrows = []
    for n in (2, 4, 8, 16, 32, 64, 128, 256, 1024, 4096):
        steps = [ch.jump_owner(k, n, count=True)[1] for k in keys[:20000]]
        jrows.append({'n': n, 'steps': ch.mean(steps), 'ln_n': __import__('math').log(n)})
    out['jump_steps'] = jrows

    # jump 的负载均衡（n = 10）
    jc = {}
    for k in keys:
        jc[ch.jump_owner(k, N0)] = jc.get(ch.jump_owner(k, N0), 0) + 1
    jr = ch.ratios(jc)
    out['jump_load'] = {'max': jr['max'], 'min': jr['min'], 'stdev': jr['stdev'],
                        'counts': [jc[i] for i in range(N0)]}

    # ---------------- 7. 一个具体的 key 走一圈 ----------------
    sample = []
    r = ch.Ring(nodes, 1)
    picked = keys[:5]
    # 再找一个位置落在最后一个节点之后的 key：它要绕过 0 点才算找到主人
    top = max(pos for pos, _ in r.points)
    for k in keys:
        if ch.h64(k) > top:
            picked.append(k)
            break
    for k in picked:
        p = ch.h64(k)
        i = __import__('bisect').bisect_left(r.pos, p)
        nxt = r.points[i % len(r.points)]
        sample.append({'key': k, 'pos': p / ch.SPACE,
                       'owner': nxt[1], 'start': nxt[0] / ch.SPACE,
                       'wrap': i == len(r.points)})
    out['sample'] = {'nodes': [{'name': n, 'pos': ch.h64('%s#0' % n) / ch.SPACE}
                               for n in nodes],
                     'keys': sample}

    # ---------------- 8. 取模方案的具体例子 ----------------
    rows = []
    for k in keys[:6]:
        h = ch.h64(k)
        rows.append({'key': k, 'mod10': nodes[h % N0], 'mod11': nodes11[h % N1],
                     'ring': ring1.owner(k)})
    out['modulo_example'] = rows

    # ---------------- 9. jump hash 的一个完整轨迹 ----------------
    trace_key, trace_steps = None, []
    for k in keys[:20000]:
        st = []
        b, j, cur = -1, 0, ch.h64(k)
        while j < N0:
            b = j
            cur = (cur * 2862933555777941757 + 1) & ch.MASK
            j = int((b + 1) * (float(1 << 31) / float((cur >> 33) + 1)))
            st.append({'b': b, 'j': j})
        if len(st) == 6:
            trace_key, trace_steps = k, st
            break
    out['jump_trace'] = {'key': trace_key, 'steps': trace_steps}

    # ---------------- 10. 三种方案的固定开销 ----------------
    out['cost'] = {'modulo_points': N0,
                   'ring_v1_points': N0,
                   'ring_v128_points': N0 * 128,
                   'jump_points': 0}

    with open(os.path.join(HERE, 'results.json'), 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write('\n')
    print('results.json', os.path.getsize(os.path.join(HERE, 'results.json')), 'bytes')
    print('grow: modulo %.4f  ring_v1 %.4f  ring_v128 %.4f  jump %.4f  ideal %.4f'
          % (grow['modulo'], grow['ring_v1'], grow['ring_v128'], grow['jump'],
             grow['ideal']))


if __name__ == '__main__':
    sys.exit(main())
