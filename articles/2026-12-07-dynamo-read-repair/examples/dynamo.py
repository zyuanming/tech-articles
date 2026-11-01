"""Dynamo 式最终一致性的玩具模型。

只用标准库。所有随机性来自固定种子的 xorshift32，逐字节可复现。

模型里的东西：
  - 一致性哈希环，每个物理节点 32 个虚拟节点
  - 偏好列表（preference list）取前 N 个副本
  - 法定人数读写（R 个响应，W 个确认），协调者不固定，读写各自随机挑副本
  - 读修复：读到多个版本时，把最新的写回落后的副本
  - 松散法定人数 + 暗示移交（hinted handoff）：副本挂了，先写到别的活节点，等它回来再补
  - 反熵：Merkle 树对比，只走哈希不相同的子树

模型里故意没有的东西：向量时钟的冲突（假设单写者，版本就是一个递增序号）、
gossip 传播、跨机房的网络延迟、真正的磁盘故障。这些在 sources.md 里写明。
"""

N_NODES = 8
VNODES = 32
N_REPLICAS = 3
N_KEYS = 120
KEY_FMT = 'k%05d'


class Rng:
    """xorshift32。种子先过一次 LCG，避免小种子开头全零。"""

    def __init__(self, seed):
        s = (1103515245 * (seed & 0x7FFFFFFF) + 12345) & 0x7FFFFFFF
        self.s = s or 0x2545F491

    def next(self):
        s = self.s
        s ^= (s << 13) & 0xFFFFFFFF
        s ^= s >> 17
        s ^= (s << 5) & 0xFFFFFFFF
        self.s = s & 0xFFFFFFFF
        return self.s

    def rand(self):
        return self.next() / 4294967296.0

    def randrange(self, lo, hi=None):
        if hi is None:
            lo, hi = 0, lo
        return lo + self.next() % (hi - lo)

    def choice(self, seq):
        return seq[self.next() % len(seq)]

    def sample(self, seq, k):
        """从 seq 里随机挑 k 个不同的元素（k 不超过长度）。"""
        pool = list(seq)
        out = []
        for _ in range(min(k, len(pool))):
            j = self.next() % len(pool)
            out.append(pool.pop(j))
        return out


def fnv1a(text):
    h = 0x811C9DC5
    for ch in text.encode('utf-8'):
        h ^= ch
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


class Node:
    def __init__(self, name):
        self.name = name
        self.data = {}      # key -> (seq, value)
        self.hints = []     # [(key, seq, value, target)]
        self.up = True
        self.stores = 0


class Ring:
    def __init__(self, nodes, vnodes=VNODES):
        self.nodes = {n.name: n for n in nodes}
        self.tokens = []
        for n in nodes:
            for v in range(vnodes):
                self.tokens.append((fnv1a('%s#%d' % (n.name, v)), n.name))
        self.tokens.sort()

    def preference(self, key, n=N_REPLICAS):
        h = fnv1a(key)
        idx = 0
        for i, (tok, _) in enumerate(self.tokens):
            if tok >= h:
                idx = i
                break
        out, seen, i = [], set(), idx
        while len(out) < n:
            name = self.tokens[i][1]
            if name not in seen:
                seen.add(name)
                out.append(name)
            i = (i + 1) % len(self.tokens)
        return out


class Cluster:
    def __init__(self, seed=20261207, n_ops=4000, chaos=0.02, chaos_len=(60, 260),
                 R=2, W=2, hints=True, repair=True, antientropy=0, hint_ttl=None,
                 chaos_stop_frac=0.5, write_stop_frac=0.75):
        self.rng = Rng(seed)
        self.members = [Node('n%d' % i) for i in range(N_NODES)]
        self.nodes = {n.name: n for n in self.members}
        self.ring = Ring(self.members)
        self.n_ops = n_ops
        self.chaos = chaos
        self.chaos_len = chaos_len
        self.R, self.W = R, W
        self.use_hints = hints
        self.use_repair = repair
        self.antientropy = antientropy
        self.seq = {}
        self.clock = 0
        self.next_seq = 1
        self.counters = dict(writes=0, reads=0, stale_reads=0, repairs=0,
                             hints_stored=0, hints_played=0, ae_runs=0,
                             ae_keys_fixed=0, ae_hashes=0, ae_naive=0,
                             write_short=0, misses=0, no_live=0)
        self.twins = []
        self.down_until = {}
        self.hint_ttl = hint_ttl
        self.hints_dropped = 0
        self.chaos_stop = int(n_ops * chaos_stop_frac)
        self.quiet_from = int(n_ops * write_stop_frac)

    # ---- 基础 ----
    def _pref(self, key):
        return [self.nodes[name] for name in self.ring.preference(key)]

    def global_max(self, key):
        return self.seq.get(key, 0)

    def divergence(self):
        total = 0
        for key, top in self.seq.items():
            for node in self._pref(key):
                rec = node.data.get(key)
                if rec is None or rec[0] != top:
                    total += 1
        return total

    # ---- 故障 ----
    def _tick_failures(self):
        rng = self.rng
        if rng.rand() < self.chaos:
            cand = [n for n in self.members if n.up]
            if cand:
                node = rng.choice(cand)
                node.up = False
                self.down_until[node.name] = self.clock + rng.randrange(*self.chaos_len)
        for name, until in list(self.down_until.items()):
            if self.clock >= until:
                node = self.nodes[name]
                if not node.up:
                    node.up = True
                    self._replay_hints(node)
                del self.down_until[name]

    def _replay_hints(self, node):
        for other in self.members:
            keep = []
            for key, seq, value, target, born in other.hints:
                if target == node.name:
                    node.data[key] = (seq, value)
                    self.counters['hints_played'] += 1
                else:
                    keep.append((key, seq, value, target, born))
            other.hints = keep

    def _expire_hints(self):
        if not self.hint_ttl:
            return
        for other in self.members:
            keep = []
            for hint in other.hints:
                if self.clock - hint[4] > self.hint_ttl:
                    self.hints_dropped += 1
                else:
                    keep.append(hint)
            other.hints = keep

    # ---- 写 ----
    def write(self, key):
        rng = self.rng
        self.clock += 1
        self.counters['writes'] += 1
        live = [n for n in self._pref(key) if n.up]
        seq = self.next_seq
        self.next_seq += 1
        self.seq[key] = seq
        value = 'v%d' % seq
        targets = rng.sample(live, self.W)
        for node in targets:
            node.data[key] = (seq, value)
            node.stores += 1
        if len(targets) < self.W:
            self.counters['write_short'] += 1
        pref = self._pref(key)[:N_REPLICAS]
        if self.use_hints:
            missing = [n for n in pref if n not in targets]
            others = [n for n in self.members if n.up and n not in pref]
            for target in missing:
                if not others:
                    break
                holder = others[rng.next() % len(others)]
                holder.hints.append((key, seq, value, target.name, self.clock))
                self.counters['hints_stored'] += 1
        return len(targets) >= self.W

    def lost_keys(self):
        """最新版本在所有节点（含待发暗示）里都找不到的键。"""
        lost = []
        for key, top in self.seq.items():
            if top == 0:
                continue
            found = False
            for node in self.members:
                rec = node.data.get(key)
                if rec and rec[0] == top:
                    found = True
                    break
                for hint in node.hints:
                    if hint[0] == key and hint[1] == top:
                        found = True
                        break
                if found:
                    break
            if not found:
                lost.append(key)
        return lost

    # ---- 读 ----
    def read(self, key):
        rng = self.rng
        self.clock += 1
        self.counters['reads'] += 1
        live = [n for n in self._pref(key) if n.up]
        contact = rng.sample(live, self.R)
        if not contact:
            # 这个键的三个副本全挂着：什么也读不到，既不算陈旧也不算命中
            self.counters['no_live'] += 1
            return None
        best = None
        for node in contact:
            rec = node.data.get(key)
            if rec is None:
                continue
            if best is None or rec[0] > best[0]:
                best = rec
        top = self.global_max(key)
        if top == 0:
            self.counters['misses'] += 1        # 这个键还没人写过，返回空
        elif best is None or best[0] != top:
            self.counters['stale_reads'] += 1
        if self.use_repair and best is not None:
            for node in contact:
                rec = node.data.get(key)
                if rec is None or rec[0] < best[0]:
                    node.data[key] = best
                    self.counters['repairs'] += 1
        return None if best is None else best[1]

    # ---- 反熵 ----
    def _node_hash(self, node, keys, lo, hi):
        acc = [node.name, str(lo), str(hi)]
        for i in range(lo, hi):
            k = keys[i]
            rec = node.data.get(k)
            acc.append('%s=%d' % (k, rec[0] if rec else 0))
        return fnv1a('|'.join(acc))

    def _merkle_sync(self, a, b, keys, fanout=16):
        hashes, fixed, naive = 0, 0, 0
        stack = [(0, len(keys))]
        while stack:
            lo, hi = stack.pop()
            hashes += 2
            if self._node_hash(a, keys, lo, hi) == self._node_hash(b, keys, lo, hi):
                continue
            if hi - lo == 1:
                k = keys[lo]
                ra = a.data.get(k, (0, None))
                rb = b.data.get(k, (0, None))
                top = max(ra[0], rb[0])
                if top:
                    a.data[k] = (top, 'v%d' % top)
                    b.data[k] = (top, 'v%d' % top)
                    fixed += 1
                continue
            step = max(1, (hi - lo + fanout - 1) // fanout)
            for s in range(lo, hi, step):
                stack.append((s, min(hi, s + step)))
        naive = 2 * len(keys)
        return hashes, fixed, naive

    def anti_entropy(self):
        rng = self.rng
        self.counters['ae_runs'] += 1
        up = [n for n in self.members if n.up]
        if len(up) < 2:
            return
        a, b = rng.sample(up, 2)
        keys = sorted(self.seq)
        hashes, fixed, naive = self._merkle_sync(a, b, keys)
        self.counters['ae_hashes'] += hashes
        self.counters['ae_naive'] += naive
        self.counters['ae_keys_fixed'] += fixed

    # ---- 主循环 ----
    def run(self):
        rng = self.rng
        keys = [KEY_FMT % (i * 9973) for i in range(N_KEYS)]
        for _ in range(self.n_ops):
            if self.clock < self.chaos_stop:
                self._tick_failures()
            else:
                for node in self.members:
                    if not node.up:
                        node.up = True
                        self._replay_hints(node)
            self._expire_hints()
            key = keys[rng.next() % len(keys)]
            if self.clock < self.quiet_from and rng.rand() < 0.55:
                self.write(key)
            else:
                self.read(key)
            if self.antientropy and self.clock % self.antientropy == 0:
                self.anti_entropy()
            self.twins.append(self.divergence())
        return self


def quorum_conflict(N, R, W, fail_prob, trials=20000, seed=7):
    """读不到最新写的概率：随机挑 R 个读副本、W 个写副本，看两个集合是否相交。"""
    rng = Rng(seed)
    stale, ok = 0, 0
    for _ in range(trials):
        up = [i for i in range(N) if rng.rand() >= fail_prob]
        if len(up) < max(R, W):
            continue
        ok += 1
        wset = set(rng.sample(up, W))
        rset = set(rng.sample(up, R))
        if not (wset & rset):
            stale += 1
    return (stale / ok) if ok else 0.0


def quorum_table(trials=20000):
    rows = []
    for R, W in ((1, 1), (1, 3), (2, 2), (2, 3), (3, 3)):
        rows.append(dict(R=R, W=W, safe=R + W > N_REPLICAS,
                         p_nofail=quorum_conflict(N_REPLICAS, R, W, 0.0, trials),
                         p_fail20=quorum_conflict(N_REPLICAS, R, W, 0.2, trials),
                         p_fail40=quorum_conflict(N_REPLICAS, R, W, 0.4, trials)))
    return rows


def merkle_cost(n_keys=4096, fanout=16, diverged=1, seed=11):
    """两棵哈希树只有一个（或 k 个）叶子不同，要交换多少个哈希；对照是一把梭。"""
    rng = Rng(seed)
    bad = set()
    while len(bad) < diverged:
        bad.add(rng.next() % n_keys)
    hashes, depth = 0, 0
    stack = [(0, n_keys, 0)]
    while stack:
        lo, hi, d = stack.pop()
        hashes += 2
        depth = max(depth, d)
        if not any(lo <= k < hi for k in bad):
            continue
        if hi - lo == 1:
            continue
        step = max(1, (hi - lo + fanout - 1) // fanout)
        for s in range(lo, hi, step):
            stack.append((s, min(hi, s + step), d + 1))
    return dict(keys=n_keys, fanout=fanout, diverged=diverged,
                hashes=hashes, naive=2 * n_keys, depth=depth,
                ratio=(2 * n_keys) / hashes)


def ages(c):
    """每个副本落后最新版本几个版本：0 / 1 / 2 / 3+。"""
    hist = [0, 0, 0, 0]
    for key, top in c.seq.items():
        for node in c._pref(key):
            rec = node.data.get(key)
            d = top - (rec[0] if rec else 0)
            hist[min(d, 3)] += 1
    return hist


def sample_replicas(c, n=4):
    out = []
    names = sorted(c.seq)
    step = max(1, len(names) // n)
    for key in names[::step][:n]:
        row = dict(key=key, top=c.global_max(key), replicas=[])
        for node in c._pref(key):
            rec = node.data.get(key)
            row['replicas'].append(dict(node=node.name, seq=rec[0] if rec else 0))
        out.append(row)
    return out


def scenario(name, **kw):
    c = Cluster(**kw).run()
    c.counters['hints_dropped'] = c.hints_dropped
    lost = c.lost_keys()
    return dict(name=name, R=c.R, W=c.W, hints=c.use_hints, repair=c.use_repair,
                antientropy=c.antientropy, hint_ttl=c.hint_ttl,
                counters=c.counters, final_divergence=c.divergence(), twins=c.twins,
                lost_keys=lost, ages=ages(c), sample=sample_replicas(c),
                hits=(c.counters['reads'] - c.counters['misses']
                      - c.counters['no_live']),
                stale_rate=(c.counters['stale_reads'] / (c.counters['reads']
                             - c.counters['misses'] - c.counters['no_live'])
                            if c.counters['reads'] > c.counters['misses']
                            + c.counters['no_live'] else 0.0),
                quiet_from=c.quiet_from, chaos_stop=c.chaos_stop)


def ops_to_converge(scn):
    tw = scn['twins']
    start = scn['quiet_from']
    for i in range(start, len(tw)):
        if tw[i] == 0:
            return i - start
    return None


def build():
    out = {}
    out['config'] = dict(nodes=N_NODES, vnodes=VNODES, replicas=N_REPLICAS,
                         keys=N_KEYS, ops=4000, seed=20261207, chaos=0.02)
    runs = [
        scenario('A 单副本，无修复', R=1, W=1, hints=False, repair=False),
        scenario('B 法定人数，无修复', R=2, W=2, hints=False, repair=False),
        scenario('C 读修复', R=2, W=2, hints=False, repair=True),
        scenario('D 暗示移交 + 读修复', R=2, W=2, hints=True, repair=True),
        scenario('E 暗示移交 + 反熵', R=2, W=2, hints=True, repair=True, antientropy=100),
        scenario('F 暗示超时被丢', R=2, W=2, hints=True, repair=True, hint_ttl=60),
        scenario('G 严格法定人数', R=3, W=3, hints=False, repair=False),
    ]
    for r in runs:
        r['ops_to_converge'] = ops_to_converge(r)
        r['twins'] = r['twins'][::25]
    out['runs'] = runs
    out['quorum'] = quorum_table()
    out['merkle1'] = merkle_cost(diverged=1)
    out['merkle10'] = merkle_cost(diverged=10)
    out['merkle_small'] = merkle_cost(n_keys=256, diverged=1)
    out['merkle_sweep'] = [merkle_cost(n_keys=n, diverged=1)
                           for n in (64, 120, 256, 1024, 4096)]

    # 一次典型运行的操作级轨迹（D 方案）
    c = Cluster(R=2, W=2, hints=True, repair=True).run()
    out['trace'] = dict(twins=c.twins, counters=c.counters,
                        quiet_from=c.quiet_from, chaos_stop=c.chaos_stop,
                        n_ops=c.n_ops)
    # 只留读修复、不用暗示的一条轨迹，用来说明“旧副本要等被读到才修好”
    c2 = Cluster(R=2, W=2, hints=False, repair=True).run()
    out['trace_nohint'] = dict(twins=c2.twins, quiet_from=c2.quiet_from,
                               chaos_stop=c2.chaos_stop, n_ops=c2.n_ops)
    return out


if __name__ == '__main__':
    import json
    print(json.dumps(build(), indent=1, ensure_ascii=False))
