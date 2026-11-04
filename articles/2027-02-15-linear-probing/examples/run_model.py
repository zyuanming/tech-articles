"""跑出这一篇要用的全部数字，写进 results.json。"""
from __future__ import annotations
import json
import probe as P
from math import log

OUT = {}

# ---------------------------------------------------------------- 1. 手算例子
M7 = 7
TOY_KEYS = [1, 8, 15, 2, 9]
t = P.LinearTable(M7)
steps = []
for k in TOY_KEYS:
    pr = t.insert(k)
    steps.append(dict(key=k, home=k % M7, probe=pr,
                      slot=list(t.slot), clusters=t.clusters()))
toy = dict(m=M7, keys=TOY_KEYS, steps=steps,
           alpha=len(TOY_KEYS) / M7,
           fail_knuth=P.knuth_fail(len(TOY_KEYS) / M7),
           succ_knuth=P.knuth_success(len(TOY_KEYS) / M7))

# 删除 8，再查 15
t.delete(8)
ok15, pr15 = t.find(15)
ok8, pr8 = t.find(8)
absent = 22 % M7
ok22, pr22 = t.find(22)
toy.update(del_key=8, after_delete=list(t.slot),
           find15=[ok15, pr15], find8=[ok8, pr8],
           find22=[ok22, pr22], absent_key=22, absent_home=absent)
OUT['toy'] = toy

print('toy slots', toy['after_delete'], 'find15', toy['find15'],
      'find22', toy['find22'])

# ---------------------------------------------------------------- 2. 负载因子曲线
LOAD = [i / 20 for i in range(1, 20)] + [0.96, 0.97, 0.98]
curve = []
M = 4099
KS = P.keys(4000, seed=7)
ABSENT = P.keys(6000, seed=99)[4000:]
for a in LOAD:
    n = int(round(a * M))
    tab = P.LinearTable(M)
    for k in KS[:n]:
        tab.insert(k)
    succ = [tab.find(k)[1] for k in KS[:n]]
    fail = [tab.find(k)[1] for k in ABSENT[:1500]]
    curve.append(dict(alpha=n / M,
                      succ=sum(succ) / len(succ),
                      fail=sum(fail) / len(fail),
                      succ_knuth=P.knuth_success(n / M),
                      fail_knuth=P.knuth_fail(n / M),
                      max_probe=tab.max_probe,
                      max_cluster=max(tab.clusters())))
OUT['curve'] = curve

for r in curve[::4]:
    print('α=%.2f succ=%.2f/%.2f fail=%.2f/%.2f maxcluster=%d' % (
        r['alpha'], r['succ'], r['succ_knuth'], r['fail'],
        r['fail_knuth'], r['max_cluster']))

# ---------------------------------------------------------------- 3. 探测长度分布
DIST = {}
for name, cls in (('linear', P.LinearTable), ('double', P.DoubleHash)):
    n = int(round(0.9 * M))
    tab = cls(M)
    for k in KS[:n]:
        tab.insert(k)
    hist = {}
    for k in KS[:n]:
        p = tab.find(k)[1]
        hist[p] = hist.get(p, 0) + 1
    fails = [tab.find(k)[1] for k in ABSENT[:1500]]
    DIST[name] = dict(hist=[[int(a), b] for a, b in sorted(hist.items())],
                      mean_succ=sum(a * b for a, b in hist.items()) / n,
                      mean_fail=sum(fails) / len(fails),
                      max_succ=max(hist), max_probe=tab.max_probe)
OUT['dist'] = DIST
print('dist linear mean %.2f max %d | double mean %.2f max %d' % (
    DIST['linear']['mean_succ'], DIST['linear']['max_succ'],
    DIST['double']['mean_succ'], DIST['double']['max_succ']))

# ---------------------------------------------------------------- 4. 最长簇与最长探测
BIG = 65537
KBig = P.keys(60000, seed=3)
grow = []
for n in (20000, 30000, 40000, 50000, 55000, 58000):
    line = P.LinearTable(BIG)
    rh = P.RobinHood(BIG)
    for k in KBig[:n]:
        line.insert(k)
        rh.insert(k)
    lp = [line.find(k)[1] for k in KBig[:n]]
    rp = [rh.find(k)[1] for k in KBig[:n]]
    grow.append(dict(n=n, alpha=n / BIG,
                     lin_max_cluster=max(line.clusters()),
                     lin_max_probe=max(lp),
                     lin_mean=sum(lp) / n,
                     rh_max_probe=max(rp),
                     rh_mean=sum(rp) / n,
                     rh_moves=rh.moves))
OUT['grow'] = grow
for r in grow:
    print('n=%d α=%.2f cluster=%d lin_max=%d rh_max=%d' % (
        r['n'], r['alpha'], r['lin_max_cluster'], r['lin_max_probe'],
        r['rh_max_probe']))

# ---------------------------------------------------------------- 5. 墓碑
M5 = 4099
tomb = []
for cycle in range(3):
    KS5 = P.keys(4000, seed=500 + cycle)
    ABS5 = P.keys(2000, seed=900 + cycle)
    tab = P.LinearTable(M5)
    n0 = int(0.85 * M5)
    for k in KS5[:n0]:
        tab.insert(k)
    before = sum(tab.find(k)[1] for k in ABS5[:1200]) / 1200
    succ_before = sum(tab.find(k)[1] for k in KS5[:n0]) / n0
    for k in KS5[:1200]:
        tab.delete(k)
    after = sum(tab.find(k)[1] for k in ABS5[:1200]) / 1200
    alive = KS5[1200:n0]
    succ_after = sum(tab.find(k)[1] for k in alive) / len(alive)
    fresh = P.LinearTable(M5)
    for k in alive:
        fresh.insert(k)
    f = sum(fresh.find(k)[1] for k in ABS5[:1200]) / 1200
    tomb.append(dict(cycle=cycle, occ=tab.occ, tombs=tab.tomb,
                     fill=(tab.occ + tab.tomb) / M5,
                     fail_before=before, fail_after=after, fail_fresh=f,
                     succ_before=succ_before, succ_after=succ_after,
                     succ_fresh=sum(fresh.find(k)[1] for k in alive) / len(alive)))
OUT['tomb'] = tomb
for r in tomb:
    print('tomb occ=%d tombs=%d fill=%.2f fail %.2f -> %.2f (fresh %.2f)' % (
        r['occ'], r['tombs'], r['fill'], r['fail_before'], r['fail_after'],
        r['fail_fresh']))

# ---------------------------------------------------------------- 5b. 格子图
def cluster_ids(tab):
    """把表摊成圆环：0 = 空，正整数 = 簇编号。"""
    m = tab.m
    out = [0] * m
    cid = 0
    i = 0
    if all(v != P.EMPTY for v in tab.slot):
        return [1] * m
    while tab.slot[i] != P.EMPTY:
        i = (i + 1) % m
    seen = 0
    while seen < m:
        i = (i + 1) % m
        if tab.slot[i] == P.EMPTY:
            continue
        cid += 1
        while tab.slot[i] != P.EMPTY and seen < m:
            out[i] = cid
            seen += 1
            i = (i + 1) % m
    return out


grid = []
for a, s in ((0.5, 11), (0.9, 12)):
    m = 64
    tab = P.LinearTable(m)
    for k in P.keys(4000, seed=s)[:int(a * m)]:
        tab.insert(k)
    ids = cluster_ids(tab)
    cl = tab.clusters()
    grid.append(dict(alpha=a, m=m, ids=ids, clusters=cl,
                     longest=max(cl), n=tab.occ))
OUT['grid'] = grid
for g in grid:
    print('grid α=%.1f clusters=%s' % (g['alpha'], g['clusters']))

# ---------------------------------------------------------------- 5c. Robin Hood 演示
m = 11
rh = P.RobinHood(m)
trace = []
for k in (8, 9, 19, 30):
    pr = rh.insert(k)
    trace.append(dict(key=k, home=k % m, probe=pr,
                      items=[[i, v[0], (i - v[1]) % m] for i, v in
                             enumerate(rh.item) if v is not None],
                      moves=rh.moves))
OUT['rhdemo'] = dict(m=m, trace=trace)
for s in trace:
    print('rh', s['key'], s['items'], 'moves', s['moves'])

# ---------------------------------------------------------------- 5d. 大表复核
FM = 65537
FN = int(0.98 * FM)
FK = P.keys(FN + 2000, seed=21)
ft = P.LinearTable(FM)
for k in FK[:FN]:
    ft.insert(k)
ff = [ft.find(k)[1] for k in FK[FN:]]
finite = dict(m=FM, n=FN, alpha=FN / FM, keys_absent=len(ff),
              fail=sum(ff) / len(ff), fail_formula=P.knuth_fail(FN / FM),
              succ=sum(ft.find(k)[1] for k in FK[:FN]) / FN,
              succ_formula=P.knuth_success(FN / FM),
              max_cluster=max(ft.clusters()),
              small=[dict(m=r['alpha'] and 4099, alpha=r['alpha'],
                          fail=r['fail'], formula=r['fail_knuth'])
                     for r in []])
finite['small'] = [dict(m=4099, alpha=c['alpha'], fail=c['fail'],
                        fail_formula=c['fail_knuth'])
                   for c in curve if c['alpha'] > 0.94]
OUT['finite'] = finite
print('finite m=%d α=%.2f fail %.1f formula %.1f maxcluster %d' % (
    FM, finite['alpha'], finite['fail'], finite['fail_formula'],
    finite['max_cluster']))

# ---------------------------------------------------------------- 6. 一张表
tabrow = []
for a in (0.5, 0.75, 0.9, 0.95):
    tabrow.append(dict(alpha=a,
                       lin=0.5 * (1 + 1 / (1 - a)),
                       lin_fail=0.5 * (1 + 1 / (1 - a) ** 2),
                       dbl=-log(1 - a) / a,
                       chain=1 + a / 2,
                       chain_fail=a))
OUT['formula'] = tabrow

(HERE := __import__('os').path.dirname(__file__))
with open(HERE + '/results.json', 'w') as f:
    json.dump(OUT, f, indent=1, ensure_ascii=False)
print('wrote results.json', len(json.dumps(OUT)), 'bytes')
