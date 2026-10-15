#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Single-process teaching model, NOT a distributed execution framework.

Python 3 standard library only. Corpus is fixed whitespace-separated tokens.
`accepted_attempts` illustrates selection of one complete attempt per task;
it does not implement real distributed commit, transport, storage, or retries.
"""
from collections import Counter, defaultdict
from pathlib import Path
import itertools
import json
import random
import sys

HERE = Path(__file__).resolve().parent
ROUTE = {"cat": 0, "dog": 1, "bird": 2, "fish": 2}


def map_record(document, text):
    return [(word, 1) for word in text.split()]


def combine(pairs):
    counts = Counter()
    for word, count in pairs:
        counts[word] += count
    return sorted(counts.items())


def run(corpus, use_combiner=False):
    mapped = {name: map_record(name, text) for name, text in corpus.items()}
    sent = {name: combine(pairs) if use_combiner else pairs
            for name, pairs in mapped.items()}
    partitions = [[] for _ in range(3)]
    for name, pairs in sent.items():
        for word, count in pairs:
            partitions[ROUTE[word]].append((name, word, count))
    grouped = []
    output = {}
    for records in partitions:
        groups = defaultdict(list)
        # A real implementation can use external sorting; this small model
        # keeps all records in memory and sorts by the key explicitly.
        for name, word, count in sorted(records, key=lambda p: p[1]):
            groups[word].append(count)
        grouped.append(dict(groups))
        for word, counts in groups.items():
            output[word] = sum(counts)
    return {"mapped": mapped, "sent": sent, "partitions": partitions,
            "grouped": grouped, "output": dict(sorted(output.items())),
            "input_tokens": sum(len(text.split()) for text in corpus.values()),
            "transferred_pairs": sum(len(p) for p in sent.values()),
            "partition_pairs": [len(p) for p in partitions]}


def accept_first_complete(attempts):
    # Input is an ordered list of (task_id, attempt_id, complete_pairs).
    # This is a pedagogical selection rule, not a production transaction.
    accepted = {}
    for task_id, attempt_id, pairs in attempts:
        if task_id not in accepted:
            accepted[task_id] = (attempt_id, pairs)
    return accepted


def test_all(corpus):
    expected = Counter(w for text in corpus.values() for w in text.split())
    checks = 0
    for order in itertools.permutations(corpus):
        reordered = {name: corpus[name] for name in order}
        for use in (False, True):
            r = run(reordered, use)
            assert r['output'] == expected
            assert sum(r['output'].values()) == r['input_tokens']
            checks += 1
    rng = random.Random(20261013)
    for _ in range(200):
        c = {name: ' '.join(rng.choices(list(ROUTE), k=rng.randrange(0, 40)))
             for name in ('A', 'B', 'C')}
        direct = Counter(w for text in c.values() for w in text.split())
        for use in (False, True):
            r = run(c, use)
            assert r['output'] == direct
            assert sum(r['output'].values()) == r['input_tokens']
            checks += 1
    a = map_record('A', corpus['A'])
    for attempts in ([('A', 'A.0', a), ('A', 'A.1', a)],
                     [('A', 'A.1', a), ('A', 'A.0', a)]):
        accepted = accept_first_complete(attempts)
        assert len(accepted) == 1
        assert sum(v for _, v in accepted['A'][1]) == 4
        checks += 1
    assert run({})['output'] == {}
    checks += 1
    return checks


def main():
    corpus = json.loads((HERE / 'corpus.json').read_text())
    base = run(corpus)
    reduced = run(corpus, True)
    duplicate = dict(corpus, A_retry=corpus['A'])
    hot = dict(corpus, A=corpus['A'] + ' cat' * 100)
    a = map_record('A', corpus['A'])
    selected = accept_first_complete([('A', 'A.0', a), ('A', 'A.1', a)])
    report = {
        'model': 'single-process deterministic teaching model',
        'corpus': corpus, 'base': base, 'combined': reduced,
        'wrong_duplicate_output': run(duplicate)['output'],
        'accepted_A_attempt': selected['A'][0],
        'hotspot': run(hot), 'hotspot_combined': run(hot, True),
        'mean_counterexample': {'A': [4], 'B': [1, 1, 1, 1, 1],
                                'wrong_mean_of_means': 2.5,
                                'correct_sum': 9, 'correct_count': 6,
                                'correct_mean': 1.5},
        'timeline_seconds': {'original_finish': 8, 'backup_start': 3,
                             'backup_duration': 2, 'accepted_finish': 5},
        'test_scenarios_passed': test_all(corpus),
        'random_seed': 20261013,
    }
    (HERE / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    output = '\n'.join([
        'MODEL: single-process teaching model',
        f"INPUT TOKENS: {base['input_tokens']}",
        'RESULT: ' + ' | '.join(f'{w}={n}' for w, n in base['output'].items()),
        f"SHUFFLE PAIRS: {base['transferred_pairs']} -> {reduced['transferred_pairs']}",
        f"RAW PARTITIONS: {base['partition_pairs']}",
        'RETRY: A.0 accepted; A.1 ignored',
        f"HOTSPOT RAW: {run(hot)['partition_pairs']}",
        f"HOTSPOT COMBINED: {run(hot,True)['partition_pairs']}",
        f"TEST SCENARIOS: {report['test_scenarios_passed']} passed",
    ]) + '\n'
    (HERE / 'output.txt').write_text(output)
    print(output, end='')


if __name__ == '__main__':
    main()
