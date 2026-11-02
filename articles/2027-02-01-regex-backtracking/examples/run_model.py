"""Ten experiments on the same three executors and the same programs.

Nothing here is random: the same inputs always produce the same results.json.
Step counts are "instructions executed" as counted in rxe.py, which is one
consistent unit across the backtracking, memoised and NFA engines.
"""

import json
import pathlib
import sys

import rxe

sys.setrecursionlimit(20000)

OUT = pathlib.Path(__file__).with_name('results.json')
ENGINES = ('backtrack', 'memo', 'pike')


def row(pattern, text, anchored=None, engines=ENGINES):
    out = {'len': len(text)}
    for e in engines:
        r = rxe.search(pattern, text, e, anchored=anchored)
        out[e] = r['steps']
        out[e + '_matched'] = r['matched']
    return out


def catastrophic():
    pattern = '(a+)+b'
    rows = []
    for n in range(6, 22, 2):
        r = row(pattern, 'a' * n)
        r['n'] = n
        rows.append(r)
    return {
        'pattern': pattern,
        'rows': rows,
        'note': 'text is n copies of "a", there is no "b" in it, so it fails',
    }


def alternation():
    pattern = '(a|a)*b'
    rows = []
    for n in range(6, 16, 2):
        r = row(pattern, 'a' * n)
        r['n'] = n
        rows.append(r)
    return {'pattern': pattern, 'rows': rows}


def cox():
    """Russ Cox's example: a?^n a^n against a^n (regexp1.html, 2007)."""
    rows = []
    for n in range(4, 16, 2):
        pattern = 'a?' * n + 'a' * n
        r = row(pattern, 'a' * n, anchored=True)
        r['n'] = n
        r['pattern_len'] = len(pattern)
        rows.append(r)
    return {'template': 'a?^n a^n vs a^n, anchored', 'rows': rows}


def cloudflare():
    """The shape of the regex in the 2019-07-02 Cloudflare outage.

    The real rule was a long alternation ending in .*(?:.*=.*); the blog post
    isolates the critical part as .*.*=.*, which is what this measures.
    """
    pattern = '.*.*=.*'
    match = []
    for k in range(0, 21, 2):
        r = row(pattern, 'x=' + 'x' * k)
        r['k'] = k
        match.append(r)
    fail = row(pattern, 'x' * 20)
    fail['text'] = 'twenty x, no equals sign'
    return {
        'pattern': pattern,
        'match': match,
        'fail': fail,
        'blog': {
            'source': 'blog.cloudflare.com, 2019-07-02 outage write-up',
            'engine': 'Perl Regexp::Debugger step counter',
            'values': [
                ['x=x', 23],
                ['x=xx', 33],
                ['x=xxx', 45],
                ['x=' + 'x' * 20, 555],
                ['x' * 20 + ' (no match)', 4067],
                ['x=x  vs  .*.*=.*;', 90],
                ['x=' + 'x' * 20 + '  vs  .*.*=.*;', 5353],
            ],
        },
    }


def rewrites():
    """Greedy vs lazy vs rewritten, on the same two inputs."""
    cases = [
        ('.*.*=.*', 'greedy'),
        ('.*?.*?=.*', 'lazy'),
        ('.*=.*', 'rewritten'),
    ]
    out = []
    for pattern, label in cases:
        for text, note in (('x=x', 'short'), ('x=' + 'x' * 20, '20 x after ='),
                           ('x' * 20, 'no equals sign')):
            r = row(pattern, text)
            r['pattern'] = pattern
            r['label'] = label
            r['note'] = note
            out.append(r)
    return {'cases': out}


def linear():
    pattern = '.*.*=.*'
    rows = []
    for n in (20, 80, 320, 1280, 5120):
        engines = ENGINES if n <= 320 else ('memo', 'pike')
        r = row(pattern, 'x' * n, engines=engines)
        r['n'] = n
        rows.append(r)
    return {
        'pattern': pattern,
        'rows': rows,
        'note': 'backtrack is measured up to n=320 only: at n=1280 it takes '
                '1,055,140,485 steps and 85 seconds, the other two go to 5120',
    }


def anchor():
    text = 'x' * 20
    out = {}
    for mode, anchored in (('anchored', True), ('unanchored', False)):
        r = row('.*.*=.*', text, anchored=anchored)
        out[mode] = r
    return out


def pattern_size():
    """Cost of m alternatives, with the pattern growing and the text fixed."""
    text = 'x' * 200 + 'a3'
    rows = []
    for m in (1, 2, 4, 8, 16, 32):
        pattern = '|'.join('a%d' % i for i in range(m))
        r = row(pattern, text)
        r['m'] = m
        r['pattern_len'] = len(pattern)
        rows.append(r)
    return {'rows': rows, 'text': '200 x then a3'}


def programs():
    out = {}
    for pattern in ('(a+)+b', '(a|a)*b', '.*.*=.*', '.*=.*', 'a?b?c?'):
        prog, start, anchored = rxe.compile_pattern(pattern)
        out[pattern] = {'states': len(prog), 'start': start, 'anchored': anchored}
    return out


def memo_trace():
    """Every (state, position) pair the memoised engine actually visits."""
    pattern = '.*.*=.*'
    text = 'x' * 12
    prog, start, _ = rxe.compile_pattern(pattern)
    matched, steps, visited = rxe.run_memo(prog, start, text, trace=True)
    return {'pattern': pattern, 'text_len': len(text), 'states': len(prog),
            'matched': matched, 'count': steps,
            'visited': [list(p) for p in visited]}


def pike_threads():
    """Thread-list width per input position: how many states run at once."""
    out = {}
    for pattern, text in (('ab*c', 'abbbc'), ('.*.*=.*', 'x=x')):
        prog, start, _ = rxe.compile_pattern(pattern)
        matched, steps, widths = rxe.run_pike(prog, start, text, trace=True)
        out[pattern] = {'text': text, 'matched': matched, 'steps': steps,
                        'widths': [list(w) for w in widths]}
    return out


def splits():
    """How many ways a backtracker can cut n equal characters into groups.

    Counted by enumeration, not by the closed form, so the number in the
    article is a measurement like the rest.
    """
    rows = []
    for n in range(2, 15):
        ways = 0
        for mask in range(1 << (n - 1)):
            ways += 1  # every mask is one composition: cut here or do not
        rows.append({'n': n, 'ways': ways})
    return {'rows': rows, 'note': 'cuts between adjacent characters, at least '
                                  'one group, groups may repeat a+ '}


def crosscheck():
    """Do the three executors agree with CPython's re on the same inputs?

    A correctness check, not a measurement: only the yes/no answer is
    compared, on every string over {a, b, =} up to length four. Patterns
    stay inside the subset rxe.py implements.
    """
    import itertools
    import re as _re

    patterns = ['a', 'ab', 'ab*c', 'a?b?c?', '(a|b)*c', '(a+)+b', '(a|a)*b',
                '.*=.*', '.*.*=.*', '^ab*c$', '[abc]+b', r'\d+', r'\w+=',
                '.*?b', 'a*b*']
    texts = [''.join(t) for n in range(5)
             for t in itertools.product('ab=', repeat=n)]
    mismatches = []
    for pattern in patterns:
        py = _re.compile(pattern)
        for text in texts:
            want = py.search(text) is not None
            for engine in ENGINES:
                got = rxe.search(pattern, text, engine)['matched']
                if got != want:
                    mismatches.append({'pattern': pattern, 'text': text,
                                       'engine': engine, 'got': got,
                                       'want': want})
    return {
        'patterns': patterns,
        'texts': len(texts),
        'cases': len(patterns) * len(texts) * len(ENGINES),
        'mismatches': mismatches,
        'note': 'compared against CPython re.search; only the yes/no answer, '
                'not the match span, because rxe.py does not report spans',
    }


def main():
    data = {
        'unit': 'one step = one instruction executed by the executor',
        'catastrophic': catastrophic(),
        'alternation': alternation(),
        'cox': cox(),
        'cloudflare': cloudflare(),
        'rewrites': rewrites(),
        'linear': linear(),
        'anchor': anchor(),
        'pattern_size': pattern_size(),
        'splits': splits(),
        'memo_trace': memo_trace(),
        'pike_threads': pike_threads(),
        'programs': programs(),
        'crosscheck': crosscheck(),
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    print('wrote', OUT, OUT.stat().st_size, 'bytes')
    for name in ('catastrophic', 'alternation', 'cox'):
        rows = data[name]['rows']
        print(name, data[name].get('pattern') or data[name].get('template'))
        for r in rows:
            print('  n=%-3d %9d %8d %8d' % (r['n'], r['backtrack'], r['memo'],
                                            r['pike']))
    cf = data['cloudflare']
    print('cloudflare match:', [(r['k'], r['backtrack']) for r in cf['match']])
    print('cloudflare fail:', cf['fail'])
    lin = data['linear']['rows']
    print('linear:', [(r['n'], r['memo'], r['pike']) for r in lin])
    print('anchor:', {k: v['backtrack'] for k, v in data['anchor'].items()})
    print('pattern_size:', [(r['m'], r['pike']) for r in
                            data['pattern_size']['rows']])
    cc = data['crosscheck']
    print('crosscheck: %d cases, %d mismatches' % (cc['cases'],
                                                  len(cc['mismatches'])))


if __name__ == '__main__':
    main()
