"""Original serial, completed-transaction MESI teaching model. Not a CPU benchmark.

Only stable states, unbounded caches, coherent ordinary memory, no prefetch,
store buffers, transient messages, race scheduling, NUMA, or clock time.
Each cell occupies one aligned eight-byte range; each operation completes before
next. A store supplies a value; it is not a simulated atomic read-modify-write.
Original code: CC BY 4.0, zyuanming / tech-articles.
"""
from collections import Counter
from dataclasses import dataclass
from itertools import product
import json
import random

@dataclass
class Entry:
    state: str
    data: dict

class Machine:
    def __init__(self, addresses, cores=2, line_size=64):
        assert cores > 0 and line_size >= 8 and line_size % 8 == 0
        assert all(a >= 0 and a % 8 == 0 for a in addresses.values())
        assert len(set(addresses.values())) == len(addresses)
        self.addresses = dict(addresses)
        self.line_size = line_size
        self.mem = {}
        for name, addr in addresses.items():
            self.mem.setdefault(addr // line_size, {})[name] = 0
        self.cache = [{} for _ in range(cores)]
        self.stats = Counter()
        self.reference = {name: 0 for name in addresses}

    def line(self, name):
        return self.addresses[name] // self.line_size

    def entry(self, core, line):
        return self.cache[core].setdefault(line, Entry('I', {}))

    def holders(self, core, line):
        return [(i, c[line]) for i, c in enumerate(self.cache)
                if i != core and line in c and c[line].state != 'I']

    def read(self, core, name):
        line = self.line(name)
        e = self.entry(core, line)
        if e.state == 'I':
            self.stats['read_requests'] += 1
            self.stats['fills'] += 1
            others = self.holders(core, line)
            e.data = dict(others[0][1].data if others else self.mem[line])
            for _, other in others:
                if other.state == 'M':
                    self.mem[line] = dict(other.data)
                    self.stats['writebacks'] += 1
                other.state = 'S'
            e.state = 'S' if others else 'E'
        result = e.data[name]
        assert result == self.reference[name]
        self.check()
        return result

    def store(self, core, name, value):
        line = self.line(name)
        e = self.entry(core, line)
        if e.state not in ('M', 'E'):
            self.stats['write_requests'] += 1
            others = self.holders(core, line)
            if e.state == 'I':
                self.stats['fills'] += 1
                # A dirty owner can pass the latest line directly to new owner.
                # Main memory need not be updated on this M -> I transfer.
                e.data = dict(others[0][1].data if others else self.mem[line])
            for _, other in others:
                other.state = 'I'
                self.stats['invalidations'] += 1
        else:
            self.stats['silent_stores'] += 1
        e.state = 'M'
        e.data[name] = value
        self.reference[name] = value
        self.stats['stores'] += 1
        self.check()

    def evict(self, core, name):
        line = self.line(name)
        e = self.entry(core, line)
        if e.state == 'M':
            self.mem[line] = dict(e.data)
            self.stats['writebacks'] += 1
        e.state = 'I'
        # No broadcast: a sole remaining S is allowed to stay S.
        self.check()

    def check(self):
        for line, memory in self.mem.items():
            holders = [c[line] for c in self.cache
                       if line in c and c[line].state != 'I']
            exclusive = [e for e in holders if e.state in ('M', 'E')]
            assert not exclusive or len(holders) == 1
            for e in holders:
                assert e.state in ('M', 'E', 'S')
                assert e.data == {k: self.reference[k] for k in memory}
            if not any(e.state == 'M' for e in holders):
                assert memory == {k: self.reference[k] for k in memory}

    def snapshot(self):
        return {'caches': [{str(k): {'state': e.state, 'data': dict(e.data)}
                            for k, e in c.items()} for c in self.cache],
                'memory': {str(k): dict(v) for k, v in self.mem.items()},
                'stats': dict(self.stats)}

def run_stores(order, separated=False, trace=False):
    m = Machine({'x': 1024, 'y': 1088 if separated else 1032})
    counts = [0, 0]
    states = []
    for core in order:
        counts[core] += 1
        m.store(core, 'xy'[core], counts[core])
        if trace:
            states.append({'core': core, 'value': counts[core], **m.snapshot()})
    return m, states

def run_checks():
    demo = {}
    for label, order, split in [('alternating', [0,1]*4, False),
                               ('batched', [0]*4+[1]*4, False),
                               ('separated', [0,1]*4, True)]:
        m, trace = run_stores(order, split, True)
        demo[label] = {'stats': dict(m.stats), 'trace': trace}
    assert demo['alternating']['stats']['write_requests'] == 8
    assert demo['alternating']['stats']['invalidations'] == 7
    assert demo['batched']['stats']['write_requests'] == 2
    assert demo['batched']['stats']['invalidations'] == 1
    assert demo['separated']['stats']['write_requests'] == 2
    assert demo['separated']['stats'].get('invalidations', 0) == 0
    # Every binary writer order length 0..12: one request per run, invalidation
    # at every writer switch. First cold request invalidates nobody.
    schedules = 0
    for n in range(13):
        for order in product(range(2), repeat=n):
            m, _ = run_stores(order)
            switches = sum(a != b for a, b in zip(order, order[1:]))
            assert m.stats['write_requests'] == (1+switches if n else 0)
            assert m.stats['invalidations'] == switches
            schedules += 1
    # Small exhaustive operation sequences (two values, both variables,
    # reads and silent evictions); includes E->M and S->M without peer.
    alphabet = [(c, op, name, v) for c in range(2) for name in 'xy'
                for op, v in [('R', None), ('W', 0), ('W', 1), ('E', None)]]
    sequences = 0
    for seq in product(alphabet, repeat=4):
        m = Machine({'x':1024, 'y':1032})
        for c, op, name, v in seq:
            if op == 'R': m.read(c, name)
            elif op == 'W': m.store(c, name, v)
            else: m.evict(c, name)
        sequences += 1
    rng = random.Random(1984348)
    events = 0
    for trial in range(100):
        m = Machine({'a':0, 'b':8, 'c':64, 'd':72}, cores=4)
        for step in range(1000):
            c, name, op = rng.randrange(4), rng.choice('abcd'), rng.randrange(3)
            if op == 0: m.read(c, name)
            elif op == 1: m.store(c, name, rng.randrange(-1000,1001))
            else: m.evict(c, name)
            events += 1
    r = Machine({'x':1024, 'y':1032})
    for c in [0,1]*4: r.read(c, 'xy'[c])
    assert r.stats['read_requests'] == 2 and r.stats['invalidations'] == 0
    rw = Machine({'x':1024, 'y':1032})
    for i in range(1,5):
        rw.store(0, 'x', i)
        assert rw.read(1, 'y') == 0
    # 64-byte records, hot offsets tail 56 and next record head 0.
    alignment = []
    for base in range(0,64,8):
        a,b = base+56,base+64
        alignment.append({'base':base, 'hot_addresses':[a,b],
                          'same_line':a//64 == b//64})
    assert [z['same_line'] for z in alignment] == [False]+[True]*7
    return {'status':'PASS', 'seed':1984348, 'writer_schedules':schedules,
            'four_event_sequences':sequences, 'random_events':events,
            'demo':demo, 'read_only_stats':dict(r.stats),
            'write_read_stats':dict(rw.stats), 'alignment':alignment,
            'scope':'Finite serial stable-state model checks; not hardware timing, not transient protocol proof.'}

if __name__ == '__main__':
    print(json.dumps(run_checks(), indent=2))
