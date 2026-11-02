"""分支预测的几个经典结构，和它们在合成 trace 上的错判率。

只算「猜对没猜对」，不算缓存、不算乱序执行、不算取指带宽。
所有表都是 2 的幂，索引都用低位，这样冲突（别名）才会像真硬件那样发生。
"""
from __future__ import annotations

import random

PCS = {
    'loop': 0x1000,
    'inner': 0x2000,
    'outer': 0x2004,
    'condA': 0x3000,
    'condB': 0x3004,
    'period': 0x4000,
    'switch': 0x5000,
}


# --------------------------------------------------------------- traces

def loop_trace(iters=10, reps=60, pc=PCS['loop']):
    """for i in range(iters)：分支 taken iters 次，最后退出时 not taken。"""
    out = []
    for _ in range(reps):
        for _ in range(iters):
            out.append((pc, True))
        out.append((pc, False))
    return out


def nested_trace(inner=5, outer=8, reps=30):
    """外层循环里套内层循环，两个分支互相影响。"""
    out = []
    for _ in range(reps):
        for o in range(outer):
            for _ in range(inner):
                out.append((PCS['inner'], True))
            out.append((PCS['inner'], False))
            out.append((PCS['outer'], o < outer - 1))
    return out


def random_trace(n=3000, rate=0.5, seed=7, pc=PCS['period']):
    rng = random.Random(seed)
    return [(pc, rng.random() < rate) for _ in range(n)]


def correlated_trace(n=1500, seed=11):
    """两个分支结果一样：A 是随机的，B 跟着 A。单看每个都是 50%。"""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        a = rng.randrange(2) == 0
        out.append((PCS['condA'], a))
        out.append((PCS['condB'], a))
    return out


def period_trace(k=3, n=3000, pc=PCS['period']):
    """周期为 k 的图案：k-1 次 taken，一次 not taken。"""
    return [(pc, (i % k) != k - 1) for i in range(n)]


def switch_trace(cases=8, groups=400, seed=13):
    """switch 派发：每组正好有一个分支 taken。"""
    rng = random.Random(seed)
    out = []
    for _ in range(groups):
        chosen = rng.randrange(cases)
        for i in range(cases):
            out.append((PCS['switch'] + 4 * i, i == chosen))
    return out


# ----------------------------------------------------------- predictors

class StaticNT:
    name = '静态：从不 taken'

    def predict(self, pc):
        return False

    def update(self, pc, taken):
        pass


class StaticT:
    name = '静态：总是 taken'

    def predict(self, pc):
        return True

    def update(self, pc, taken):
        pass


class Bimodal:
    """一位或两位的饱和计数器表，按 PC 的低位索引。"""

    def __init__(self, log_entries=12, bits=2, shift=0):
        self.mask = (1 << log_entries) - 1
        self.shift = shift
        self.bits = bits
        self.max = (1 << bits) - 1
        self.tab = [0] * (1 << log_entries)
        self.name = '%d 位计数器表' % bits

    def predict(self, pc):
        c = self.tab[(pc >> self.shift) & self.mask]
        return c >= (self.max + 1) // 2

    def update(self, pc, taken):
        i = (pc >> self.shift) & self.mask
        c = self.tab[i]
        if taken:
            self.tab[i] = min(self.max, c + 1)
        else:
            self.tab[i] = max(0, c - 1)


class Local2:
    """每个 PC 记住一小段自己的历史，用这段历史去查计数器表。"""

    def __init__(self, log_pcs=10, hist_bits=8, bits=2):
        self.pc_mask = (1 << log_pcs) - 1
        self.hist_bits = hist_bits
        self.hist_mask = (1 << hist_bits) - 1
        self.max = (1 << bits) - 1
        self.hist = [0] * (1 << log_pcs)
        self.tab = [0] * (1 << hist_bits)
        self.history = []          # 便于在外面看它学到了什么
        self.name = '局部历史 %d 位' % hist_bits

    def predict(self, pc):
        i = pc & self.pc_mask
        return self.tab[self.hist[i]] >= (self.max + 1) // 2

    def update(self, pc, taken):
        i = pc & self.pc_mask
        h = self.hist[i]
        c = self.tab[h]
        self.tab[h] = min(self.max, c + 1) if taken else max(0, c - 1)
        self.hist[i] = ((h << 1) | int(taken)) & self.hist_mask


class Gshare:
    """全局历史寄存器和 PC 异或，再查计数器表。"""

    def __init__(self, log_entries=12, hist_bits=12, bits=2):
        self.mask = (1 << log_entries) - 1
        self.hist_bits = hist_bits
        self.hist_mask = (1 << hist_bits) - 1
        self.max = (1 << bits) - 1
        self.tab = [0] * (1 << log_entries)
        self.ghr = 0
        self.name = 'gshare %d 位历史' % hist_bits

    def _idx(self):
        return (self.ghr ^ (self.pc >> 2)) & self.mask

    def predict(self, pc):
        self.pc = pc
        return self.tab[self._idx()] >= (self.max + 1) // 2

    def update(self, pc, taken):
        self.pc = pc
        i = self._idx()
        c = self.tab[i]
        self.tab[i] = min(self.max, c + 1) if taken else max(0, c - 1)
        self.ghr = ((self.ghr << 1) | int(taken)) & self.hist_mask


class Tournament:
    """两个预测器各猜一次，用一个选择计数器决定听谁的。"""

    def __init__(self, a, b, log_entries=12):
        self.a, self.b = a, b
        self.mask = (1 << log_entries) - 1
        self.choice = [1] * (1 << log_entries)   # 1 = 听 b
        self.name = '锦标赛：2 位表 / gshare'

    def predict(self, pc):
        self.pa = self.a.predict(pc)
        self.pb = self.b.predict(pc)
        self.pick_b = self.choice[pc & self.mask] >= 2
        return self.pb if self.pick_b else self.pa

    def update(self, pc, taken):
        i = pc & self.mask
        a_ok = self.pa == taken
        b_ok = self.pb == taken
        if b_ok and not a_ok:
            self.choice[i] = min(3, self.choice[i] + 1)
        elif a_ok and not b_ok:
            self.choice[i] = max(0, self.choice[i] - 1)
        self.a.update(pc, taken)
        self.b.update(pc, taken)


# ---------------------------------------------------------------- run

def run(trace, pred):
    misses = 0
    for pc, taken in trace:
        if pred.predict(pc) != taken:
            misses += 1
        pred.update(pc, taken)
    return misses


def rate(trace, pred):
    return run(trace, pred) / len(trace)


def build():
    traces = {
        'loop10': dict(trace=loop_trace(10, 60), note='循环 10 次，退出一次'),
        'loop100': dict(trace=loop_trace(100, 12), note='循环 100 次，退出一次'),
        'nested': dict(trace=nested_trace(), note='内层 5 次套在外层 8 次里'),
        'random50': dict(trace=random_trace(), note='每个分支各 50%，互不相关'),
        'correlated': dict(trace=correlated_trace(), note='B 总是跟着 A 走'),
        'period3': dict(trace=period_trace(3), note='T T N 周期重复'),
        'switch8': dict(trace=switch_trace(), note='8 路 switch，每组一个 taken'),
    }

    def fresh():
        return [
            StaticNT(),
            StaticT(),
            Bimodal(12, 1),
            Bimodal(12, 2),
            Local2(),
            Gshare(12, 12),
            Tournament(Bimodal(12, 2), Gshare(12, 12)),
        ]

    matrix = {}
    for name, t in traces.items():
        preds = fresh()
        matrix[name] = {}
        for p in preds:
            matrix[name][p.name] = round(rate(t['trace'], p), 5)

    # 全局历史长度的影响
    ladder = {}
    for name in ('correlated', 'period3', 'loop10'):
        tr = traces[name]['trace']
        ladder[name] = []
        for h in (1, 2, 3, 4, 6, 8, 10, 12, 14, 16):
            ladder[name].append(dict(hist=h,
                                     miss=round(rate(tr, Gshare(12, h)), 5)))

    # 表太小会自己打自己：64 个结果固定的分支，表从 4 格长到 256 格
    rng = random.Random(23)
    bits = [rng.randrange(2) for _ in range(64)]
    tr = []
    for _ in range(60):
        for i, b in enumerate(bits):
            tr.append((0x6000 + 4 * i, bool(b)))
    alias = []
    for log in range(2, 9):
        alias.append(dict(log_entries=log,
                          entries=1 << log,
                          working_set=64,
                          per_slot=64 // (1 << log),
                          miss=round(rate(tr, Bimodal(log, 2, shift=2)), 5)))

    # 循环长度的扫描
    loop_sweep = []
    for iters in (2, 3, 5, 10, 20, 50, 100):
        reps = max(20, 4000 // (iters + 1))
        tr2 = loop_trace(iters, reps)
        loop_sweep.append(dict(iters=iters,
                               static=round(rate(tr2, StaticNT()), 5),
                               one_bit=round(rate(tr2, Bimodal(12, 1)), 5),
                               two_bit=round(rate(tr2, Bimodal(12, 2)), 5),
                               gshare=round(rate(tr2, Gshare(12, 12)), 5)))

    # 出错要付多少周期
    width = 2.0            # 每周期最多发射 2 条
    branch_density = 0.2   # 每 5 条指令有 1 个分支
    penalty = 15           # 误判代价，周期
    base_cpi = 1.0 / width
    cost = []
    for m in (0.0, 0.005, 0.01, 0.03, 0.05, 0.10, 0.20, 0.50):
        cpi = base_cpi + branch_density * m * penalty
        cost.append(dict(miss=m, cpi=round(cpi, 3), ipc=round(1 / cpi, 3),
                         slowdown_vs_perfect=round(cpi / base_cpi, 3)))
    stall_all = base_cpi + branch_density * penalty

    # 循环退出时，每个预测器到底在哪几步猜错（图 6 用）
    tr3 = loop_trace(5, 3)
    detail = dict(
        outcomes=[int(t) for _, t in tr3],
        preds={},
    )
    for pr in (Bimodal(12, 1), Bimodal(12, 2)):
        seq, miss_at = [], []
        for i, (pc, taken) in enumerate(tr3):
            prd = pr.predict(pc)
            seq.append(int(prd))
            if prd != taken:
                miss_at.append(i)
            pr.update(pc, taken)
        detail['preds'][pr.name] = dict(pred=seq, miss_at=miss_at)

    # 两个相关分支的前 12 轮
    rng2 = random.Random(11)
    a_bits, b_bits = [], []
    for _ in range(12):
        a = rng2.randrange(2) == 0
        a_bits.append(int(a))
        b_bits.append(int(a))
    correlated_sample = dict(a=a_bits, b=b_bits)

    return dict(
        detail=detail,
        correlated_sample=correlated_sample,
        config=dict(width=width, branch_density=branch_density,
                    penalty=penalty, base_cpi=base_cpi,
                    entries=4096, local_hist_bits=8, gshare_hist_bits=12),
        traces={k: dict(length=len(v['trace']),
                        taken=round(sum(1 for _, t in v['trace'] if t) /
                                    len(v['trace']), 4),
                        note=v['note']) for k, v in traces.items()},
        predictors=[p.name for p in fresh()],
        matrix=matrix,
        ladder=ladder,
        alias=alias,
        loop_sweep=loop_sweep,
        cost=cost,
        stall_all_cpi=round(stall_all, 3),
        stall_all_ipc=round(1 / stall_all, 3),
    )


if __name__ == '__main__':
    import json
    print(json.dumps(build(), ensure_ascii=False, indent=1))
