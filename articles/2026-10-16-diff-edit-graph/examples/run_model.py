#!/usr/bin/env python3
"""Experiments for the diff article. Standard library only. MIT."""
from __future__ import annotations
import json
import random
import time
from pathlib import Path

from myers import (Trace, myers, shortest_edit_length, counts, unified,
                   apply_script, lcs_dp)
from patience import patience_flat

HERE = Path(__file__).resolve().parent
PAIRS = HERE.parent / 'originals' / 'pairs'
OUT = HERE / 'results.json'


def read(name):
    return (PAIRS / name).read_text().splitlines()


def verify_random(trials=400, seed=5):
    rng = random.Random(seed)
    for _ in range(trials):
        a = [rng.randint(0, 3) for _ in range(rng.randint(0, 7))]
        b = [rng.randint(0, 3) for _ in range(rng.randint(0, 7))]
        sc = myers(a, b)
        assert apply_script(a, b, sc) == list(b)
        eq, dl, il = counts(sc)
        assert dl + il == shortest_edit_length(a, b), (a, b)
    return dict(trials=trials, seed=seed,
                claim='脚本能重建 b，且编辑长度等于动态规划最优值')


FROBNITZ_BEFORE = """#include <stdio.h>

// Frobs foo heartily
int frobnitz(int foo)
{
    int i;
    for(i = 0; i < 10; i++)
    {
        printf("Your answer is: ");
        printf("%d\\n", foo);
    }
}

int fact(int n)
{
    if(n > 1)
    {
        return fact(n-1) * n;
    }
    return 1;
}

int main(int argc, char **argv)
{
    frobnitz(fact(10));
}""".split('\n')

FROBNITZ_AFTER = """#include <stdio.h>

int fib(int n)
{
    if(n > 2)
    {
        return fib(n-1) + fib(n-2);
    }
    return 1;
}

// Frobs foo heartily
int frobnitz(int foo)
{
    int i;
    for(i = 0; i < 10; i++)
    {
        printf("Your answer is: ");
        printf("%d\\n", foo);
    }
}

int main(int argc, char **argv)
{
    frobnitz(fib(10));
}""".split('\n')


def count_optimal_scripts(a, b):
    """How many distinct shortest edit scripts exist for this pair?"""
    from functools import lru_cache
    n, m = len(a), len(b)
    D = shortest_edit_length(a, b)

    @lru_cache(maxsize=None)
    def lcs(i, j):
        if i == n or j == m:
            return 0
        if a[i] == b[j]:
            return 1 + lcs(i + 1, j + 1)
        return max(lcs(i + 1, j), lcs(i, j + 1))

    count = [0]
    samples = []

    def walk(i, j, length, path):
        if length > D or count[0] > 200000:
            return
        if i == n and j == m:
            if length == D:
                count[0] += 1
                if len(samples) < 3:
                    samples.append(tuple(path))
            return
        if i < n and j < m and a[i] == b[j] and 1 + lcs(i + 1, j + 1) == lcs(i, j):
            walk(i + 1, j + 1, length, path + [('=', i, j)])
        if i < n and lcs(i + 1, j) == lcs(i, j):
            walk(i + 1, j, length + 1, path + [('-', i, None)])
        if j < m and lcs(i, j + 1) == lcs(i, j):
            walk(i, j + 1, length + 1, path + [('+', None, j)])

    walk(0, 0, 0, [])
    return D, count[0], samples


def summarize(a, b, script, tr, seconds):
    eq, dl, il = counts(script)
    return dict(lines_a=len(a), lines_b=len(b), unchanged=eq, deleted=dl,
                inserted=il, edit_length=dl + il,
                shortest_possible=shortest_edit_length(a, b),
                d_steps=tr.d_steps, diagonals=tr.diagonals,
                snake_pixels=tr.snake_pixels, comparisons=tr.comparisons,
                seconds=round(seconds, 4))


def main():
    out = {}
    out['random_verification'] = verify_random()

    # 1. the real file pairs
    pairs = []
    for name, fa, fb in (('integrity.py', 'integrity-before.py',
                          'integrity-after.py'),
                         ('source_rights.py', 'source_rights-before.py',
                          'source_rights-after.py')):
        a, b = read(fa), read(fb)
        tr = Trace()
        t = time.time()
        sc = myers(a, b, tr)
        dt = time.time() - t
        assert apply_script(a, b, sc) == list(b)
        row = summarize(a, b, sc, tr, dt)
        row['name'] = name
        row['optimal'] = row['edit_length'] == row['shortest_possible']
        pairs.append(row)
        print(name, row, flush=True)
    out['real_pairs'] = pairs

    # 2. how the work grows with the size of the change
    growth = []
    base = read('integrity-before.py')
    for k in (1, 2, 4, 8, 16):
        a = list(base)
        b = list(base)
        for t in range(k):
            pos = 20 + t * 9
            if pos < len(b):
                b.insert(pos, '# inserted line %d' % t)
        tr = Trace()
        t0 = time.time()
        sc = myers(a, b, tr)
        dt = time.time() - t0
        row = summarize(a, b, sc, tr, dt)
        row['inserted_blocks'] = k
        growth.append(row)
        print('growth', k, row, flush=True)
    out['growth'] = growth

    # 3. the same file against itself, and against a shuffled copy
    a = read('integrity-before.py')
    b = list(a)
    tr = Trace(); t0 = time.time(); sc = myers(a, b, tr); dt = time.time() - t0
    out['identical'] = summarize(a, b, sc, tr, dt)
    rng = random.Random(3)
    shuffled = list(a)
    rng.shuffle(shuffled)
    tr = Trace(); t0 = time.time(); sc = myers(a, shuffled, tr); dt = time.time() - t0
    out['shuffled'] = summarize(a, shuffled, sc, tr, dt)

    # 4. shortest is not the same as unique
    amb = []
    for a, b in ((list('aaa'), list('bbb')), (list('abab'), list('baba')),
                 (list('abcab'), list('cabca'))):
        D, n, samples = count_optimal_scripts(a, b)
        amb.append(dict(
            a=''.join(a), b=''.join(b), edit_length=D,
            optimal_scripts_found=n,
            myers_choice=' '.join(
                '%s%s' % (op, a[i] if i is not None else b[j])
                for op, i, j in myers(a, b)),
            examples=[' '.join('%s%s' % (op, a[i] if i is not None else b[j])
                               for op, i, j in sc) for sc in samples]))
    out['ambiguous'] = amb

    # 5. patience vs Myers, measured rather than assumed
    cmp_rows = []
    for name, a, b in (('经典教学示例 frobnitz/fact → fib', FROBNITZ_BEFORE,
                        FROBNITZ_AFTER),
                       ('integrity.py 两版', read('integrity-before.py'),
                        read('integrity-after.py')),
                       ('source_rights.py 两版',
                        read('source_rights-before.py'),
                        read('source_rights-after.py'))):
        tr_m = Trace(); t0 = time.time(); sc_m = myers(a, b, tr_m)
        dt_m = time.time() - t0
        tr_p = Trace(); t0 = time.time(); sc_p = patience_flat(a, b, tr_p)
        dt_p = time.time() - t0
        assert apply_script(a, b, sc_p) == list(b)
        cmp_rows.append(dict(
            name=name, lines=len(a),
            myers=summarize(a, b, sc_m, tr_m, dt_m),
            patience=summarize(a, b, sc_p, tr_p, dt_p),
            same_output=(sc_m == sc_p)))
    out['patience_vs_myers'] = cmp_rows

    # 6. a large file with few edits
    big = ['line %06d of the file' % i for i in range(40000)]
    big_after = list(big)
    for k in range(8):
        big_after.insert(5000 * k + 100, '# a newly added line %d' % k)
    big_rows = []
    for name, fn in (('myers', myers), ('patience', patience_flat)):
        tr = Trace(); t0 = time.time(); sc = fn(big, big_after, tr)
        big_rows.append(dict(algorithm=name, lines=len(big),
                             seconds=round(time.time() - t0, 4),
                             diagonals=tr.diagonals,
                             comparisons=tr.comparisons,
                             edit_length=counts(sc)[1] + counts(sc)[2]))
    out['large_file'] = big_rows

    # 7. how often patience and Myers disagree at all
    rng = random.Random(2)
    trials = 200000
    different = 0
    patience_longer = 0
    shorter_lcs = 0
    for _ in range(trials):
        a = [rng.choice('abcd') for _ in range(rng.randint(3, 10))]
        b = [rng.choice('abcd') for _ in range(rng.randint(3, 10))]
        sm = myers(a, b)
        sp = patience_flat(a, b)
        if sm == sp:
            continue
        different += 1
        cm, cp = counts(sm), counts(sp)
        if cm[0] > cp[0]:
            shorter_lcs += 1
        if cm[0] < cp[0]:
            patience_longer += 1
    out['random_disagreement'] = dict(
        trials=trials, alphabet=4, lengths='3..10', seed=2,
        different_scripts=different,
        different_fraction=round(different / trials, 4),
        patience_lcs_shorter=shorter_lcs,
        patience_lcs_longer=patience_longer,
        note='锚点只会收紧解空间，所以 patience 的公共子序列不可能比 Myers 更长')
    print('disagreement', out['random_disagreement'], flush=True)

    # 8. the classic example, both outputs, side by side
    sc_m = myers(FROBNITZ_BEFORE, FROBNITZ_AFTER)
    sc_p = patience_flat(FROBNITZ_BEFORE, FROBNITZ_AFTER)
    out['classic'] = dict(
        before=FROBNITZ_BEFORE, after=FROBNITZ_AFTER,
        myers_diff=unified(FROBNITZ_BEFORE, FROBNITZ_AFTER, sc_m,
                           'before.c', 'after.c', context=1),
        patience_diff=unified(FROBNITZ_BEFORE, FROBNITZ_AFTER, sc_p,
                              'before.c', 'after.c', context=1),
        same=(sc_m == sc_p))

    # 9. the real diff of the smallest real pair, as actual output
    a, b = read('source_rights-before.py'), read('source_rights-after.py')
    sc = myers(a, b)
    out['real_diff'] = unified(a, b, sc, 'source_rights.py (前一版)',
                               'source_rights.py (后一版)', context=2)

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print('wrote', OUT.name)


if __name__ == '__main__':
    main()
