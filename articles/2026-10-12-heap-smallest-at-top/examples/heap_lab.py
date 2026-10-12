"""Small binary min-heap experiments, original educational implementation.
Only the Python standard library is needed. Keys must have a consistent total
order (integers/tuples in this lab); NaN and externally mutable keys are excluded.
Run: python heap_lab.py --out results.json
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import heapq
import itertools
import json
import math
import platform
import random


class MinHeap:
    """Array-backed min-heap; counters count key comparisons and swaps only."""
    def __init__(self, values=(), *, build=True):
        self.a = list(values)
        self.comparisons = 0
        self.swaps = 0
        self.trace = []
        if build:
            self.heapify()

    def less(self, x, y):
        self.comparisons += 1
        return x < y

    def swap(self, i, j):
        self.a[i], self.a[j] = self.a[j], self.a[i]
        self.swaps += 1
        self.trace.append({'swap': [i, j], 'array': self.a.copy()})

    def up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if not self.less(self.a[i], self.a[parent]):
                break
            self.swap(i, parent)
            i = parent

    def down(self, i):
        n = len(self.a)
        while 2 * i + 1 < n:
            child = 2 * i + 1
            right = child + 1
            if right < n and self.less(self.a[right], self.a[child]):
                child = right
            if not self.less(self.a[child], self.a[i]):
                break
            self.swap(i, child)
            i = child

    def push(self, value):
        self.a.append(value)
        self.up(len(self.a) - 1)

    def peek(self):
        if not self.a:
            raise IndexError('peek from empty heap')
        return self.a[0]

    def pop(self):
        if not self.a:
            raise IndexError('pop from empty heap')
        answer = self.a[0]
        last = self.a.pop()
        if self.a:
            self.a[0] = last
            self.down(0)
        return answer

    def heapify(self):
        start = len(self.a) // 2 - 1
        for i in range(start, -1, -1):
            self.down(i)

    def valid(self):
        # Testing comparisons deliberately do not alter instrumented counters.
        return all(not self.a[i] < self.a[(i - 1) // 2]
                   for i in range(1, len(self.a)))

    def drain(self):
        return [self.pop() for _ in range(len(self.a))]


class IndexedHeap:
    """ID -> current index must be updated on EVERY exchange.
    Uses unique integer IDs as deterministic tie-breakers, not FIFO arrival order.
    Dictionary access has expected/amortized O(1) cost, not worst-case guaranteed.
    """
    def __init__(self):
        self.a = []
        self.pos = {}

    def swap(self, i, j):
        self.a[i], self.a[j] = self.a[j], self.a[i]
        self.pos[self.a[i][1]] = i
        self.pos[self.a[j][1]] = j

    def up(self, i):
        while i and self.a[i] < self.a[(i - 1) // 2]:
            p = (i - 1) // 2
            self.swap(i, p)
            i = p

    def down(self, i):
        n = len(self.a)
        while 2 * i + 1 < n:
            c = 2 * i + 1
            if c + 1 < n and self.a[c + 1] < self.a[c]:
                c += 1
            if not self.a[c] < self.a[i]:
                break
            self.swap(i, c)
            i = c

    def fix(self, i):
        if i and self.a[i] < self.a[(i - 1) // 2]:
            self.up(i)
        else:
            self.down(i)

    def put(self, ident, priority):
        if ident in self.pos:
            i = self.pos[ident]
            self.a[i] = (priority, ident)
            self.fix(i)
        else:
            self.pos[ident] = len(self.a)
            self.a.append((priority, ident))
            self.up(len(self.a) - 1)

    def remove(self, ident):
        i = self.pos.pop(ident)
        old = self.a[i]
        last = self.a.pop()
        if i < len(self.a):
            self.a[i] = last
            self.pos[last[1]] = i
            self.fix(i)
        return old

    def pop(self):
        if not self.a:
            raise IndexError('pop from empty indexed heap')
        return self.remove(self.a[0][1])

    def valid(self):
        return (len(self.a) == len(self.pos)
                and all(self.pos[item[1]] == i for i, item in enumerate(self.a))
                and all(self.a[(i - 1) // 2] <= self.a[i]
                        for i in range(1, len(self.a))))


class LazyQueue:
    """Replacement gets a NEW arrival order; physical heap includes old versions."""
    def __init__(self):
        self.a = []
        self.live = {}
        self.serial = itertools.count()
        self.skipped = 0

    def put(self, ident, priority):
        serial = next(self.serial)
        self.live[ident] = (priority, serial)
        heapq.heappush(self.a, (priority, serial, ident))

    def remove(self, ident):
        del self.live[ident]

    def pop(self):
        while self.a:
            priority, serial, ident = heapq.heappop(self.a)
            if self.live.get(ident) == (priority, serial):
                del self.live[ident]
                return priority, ident
            self.skipped += 1
        raise IndexError('pop from empty lazy queue')

    def rebuild(self):
        self.a = [(p, s, ident) for ident, (p, s) in self.live.items()]
        heapq.heapify(self.a)


@dataclass
class PriorityOnly:
    priority: int
    name: str

    def __lt__(self, other):
        return self.priority < other.priority


def main_example():
    original = [12, 4, 9, 7, 15, 6, 3]
    h = MinHeap(original, build=False)
    builds = []
    for i in range(len(h.a) // 2 - 1, -1, -1):
        start = len(h.trace)
        h.down(i)
        builds.append({'index': i, 'array': h.a.copy(),
                       'swaps': h.trace[start:]})
    built = h.a.copy()
    counts = {'comparisons': h.comparisons, 'swaps': h.swaps}
    h.trace = []
    h.push(2)
    pushed, push_trace = h.a.copy(), h.trace.copy()
    h.trace = []
    value = h.pop()
    after_pop, pop_trace = h.a.copy(), h.trace.copy()
    return {'input': original, 'heapify_steps': builds, 'built': built,
            'build_counts': counts, 'pushed': pushed, 'push_trace': push_trace,
            'popped': value, 'after_pop': after_pop, 'pop_trace': pop_trace,
            'remaining_output': h.drain()}


def event_simulation():
    # Absolute integer seconds; equal times use arrival order. No wall-clock waits.
    entries = [(12, '开门'), (4, '脚步'), (9, '陷阱'), (7, '敌人'),
               (15, '烟雾'), (6, '落石'), (3, '宝箱')]
    q, serial = [], itertools.count()
    now = 0
    def schedule(t, name):
        if t < now:
            raise ValueError('cannot schedule in the simulated past')
        heapq.heappush(q, (t, next(serial), name))
    for t, name in entries:
        schedule(t, name)
    log = []
    while q:
        now, _, name = heapq.heappop(q)
        log.append([now, name])
        if name == '宝箱':
            schedule(5, '闪光')
        if name == '脚步':
            schedule(6, '回声')
    try:
        schedule(1, '过去的事件')
        raise AssertionError('past event was accepted')
    except ValueError:
        pass
    return {'events': log, 'past_event_rejected': True,
            'time_unit': 'integer simulated seconds; not real-time measurement'}


def run_tests():
    boundary = [[], [5], [2, 1], [1, 2], [3, 1, 2], [2, 2, 2],
                [0, -2, -2, 8, 1, 7], list(range(50)), list(range(49, -1, -1))]
    for data in boundary:
        h = MinHeap(data)
        assert h.valid() and h.drain() == sorted(data)
    for action in ('peek', 'pop'):
        try:
            getattr(MinHeap(), action)()
            raise AssertionError('empty operation was accepted')
        except IndexError:
            pass
    # All distinct permutations up through length 7, checking after every pop.
    exhaustive = 0
    for n in range(8):
        for data in itertools.permutations(range(n)):
            h = MinHeap(data)
            assert h.valid()
            for expected in range(n):
                assert h.pop() == expected and h.valid()
            exhaustive += 1
    # Duplicate-containing vectors also enumerate n<=6, values -1,0,1.
    duplicate_vectors = 0
    for n in range(7):
        for data in itertools.product((-1, 0, 1), repeat=n):
            h = MinHeap(data)
            assert h.valid() and h.drain() == sorted(data)
            duplicate_vectors += 1
    mixed = 0
    for seed in range(20):
        rng = random.Random(1964000 + seed)
        h, reference = MinHeap(), []
        for _ in range(2000):
            if not reference or rng.random() < .54:
                x = rng.randrange(-100, 101)
                h.push(x)
                heapq.heappush(reference, x)
            else:
                assert h.pop() == heapq.heappop(reference)
            assert h.valid() and len(h.a) == len(reference)
            if reference:
                assert h.peek() == reference[0]
            h.trace.clear()  # traces are for the tiny teaching examples only
            mixed += 1
    indexed = 0
    for seed in range(10):
        rng = random.Random(245000 + seed)
        h, ref = IndexedHeap(), {}
        for _ in range(2000):
            action = rng.random()
            if not ref or action < .65:
                ident, p = rng.randrange(100), rng.randrange(-30, 31)
                h.put(ident, p)
                ref[ident] = p
            elif action < .85:
                ident = rng.choice(list(ref))
                assert h.remove(ident) == (ref.pop(ident), ident)
            else:
                expect = min((p, ident) for ident, p in ref.items())
                assert h.pop() == expect
                del ref[expect[1]]
            assert h.valid() and len(ref) == len(h.a)
            assert sorted(h.a) == sorted((p, ident) for ident, p in ref.items())
            indexed += 1
    q = LazyQueue()
    q.put('A', 9); q.put('B', 4); q.put('A', 2); q.remove('B')
    assert q.pop() == (2, 'A')
    try:
        q.pop()
        raise AssertionError('empty lazy queue was accepted')
    except IndexError:
        pass
    assert q.skipped == 2
    q = LazyQueue()
    for p in range(500, 0, -1):
        q.put('A', p)
    lazy_before = [len(q.live), len(q.a)]
    q.rebuild()
    lazy_after = [len(q.live), len(q.a)]
    assert lazy_before == [1, 500] and lazy_after == [1, 1]
    # Priority-only equality does NOT preserve insertion order.
    h = MinHeap()
    for name in 'ABC':
        h.push(PriorityOnly(4, name))
    unstable = [x.name for x in h.drain()]
    assert unstable == ['A', 'C', 'B']
    h = MinHeap()
    for serial, name in enumerate('ABC'):
        h.push((4, serial, name))
    stable = [x[2] for x in h.drain()]
    assert stable == ['A', 'B', 'C']
    # Noncomparable payloads never need to compare when counters are unique.
    h = MinHeap([(4, 0, {}), (4, 1, {})])
    assert len(h.drain()) == 2
    main = main_example()
    assert main['built'] == [3, 4, 6, 7, 15, 12, 9]
    assert main['pushed'] == [2, 3, 6, 4, 15, 12, 9, 7]
    assert main['popped'] == 2 and main['after_pop'] == main['built']
    assert main['remaining_output'] == [3, 4, 6, 7, 9, 12, 15]
    # Sum of node heights by literal descendants equals floor-series.
    height_checks = 0
    for n in range(1025):
        literal = 0
        for i in range(n):
            j = i
            while 2 * j + 1 < n:
                j = 2 * j + 1
                literal += 1
        geometric = sum(n // (2 ** k) for k in range(1, n.bit_length() + 1))
        assert literal == geometric and (n == 0 or geometric < n)
        height_checks += 1
    counts = []
    for n in [7, 31, 127, 1023]:
        data = list(range(n, 0, -1))
        repeated = MinHeap()
        for x in data:
            repeated.push(x)
        bulk = MinHeap(data)
        counts.append({'n': n, 'repeated_push_comparisons': repeated.comparisons,
                       'bottom_up_comparisons': bulk.comparisons,
                       'repeated_push_swaps': repeated.swaps,
                       'bottom_up_swaps': bulk.swaps})
        assert repeated.valid() and bulk.valid()
        assert bulk.comparisons < 2 * n
    return {'python': platform.python_version(), 'status': 'PASS',
            'input_policy': 'consistent total ordering, tested on integers and tuples; NaN excluded',
            'boundary_vectors': len(boundary), 'empty_operations_checked': 2,
            'exhaustive_permutations_n_0_to_7': exhaustive,
            'duplicate_vectors_n_0_to_6_alphabet_minus1_0_1': duplicate_vectors,
            'mixed_push_pop_operations': mixed,
            'mixed_seeds': '1964000..1964019; 2000 operations per seed',
            'indexed_update_delete_operations': indexed,
            'indexed_seeds': '245000..245009; 2000 operations per seed',
            'height_budget_shapes_n_0_to_1024': height_checks,
            'unstable_equal_priorities': unstable, 'with_unique_counter': stable,
            'lazy_queue_before_rebuild_live_physical': lazy_before,
            'lazy_queue_after_rebuild_live_physical': lazy_after,
            'descending_input_key_comparisons': counts,
            'main_example': main, 'event_simulation': event_simulation(),
            'measurement_scope': 'key comparison counts only; not timing or production benchmark'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out')
    args = parser.parse_args()
    result = run_tests()
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        from pathlib import Path
        Path(args.out).write_text(text, encoding='utf8')
    print(text)
