#!/usr/bin/env python3
"""Run every measurement the article quotes, write results.json. MIT."""
from __future__ import annotations

import json
from pathlib import Path

import lz

HERE = Path(__file__).resolve().parent


def walkthrough(text: str):
    """Token-by-token trace of one short string, for the figure that decodes it."""
    data = text.encode()
    toks = lz.compress(data, window=64)
    out = bytearray()
    steps = []
    for tok in toks:
        if tok[0] == 'lit':
            src = 'literal %r' % chr(tok[1])
            out.append(tok[1])
            steps.append(dict(kind='lit', text=chr(tok[1]), pos=len(out) - 1,
                              now=out.decode('utf-8', 'replace')))
        else:
            _, dist, length = tok
            start = len(out) - dist
            piece = bytes(out[start:start + length])
            for i in range(length):
                out.append(out[start + i])
            steps.append(dict(kind='match', dist=dist, length=length,
                              piece=piece.decode('utf-8', 'replace'),
                              now=out.decode('utf-8', 'replace')))
    assert out == data
    return steps


def main() -> int:
    alice = (HERE / 'corpus' / 'alice.txt').read_bytes()
    log = lz.make_log(24000)
    rnd = lz.random_bytes(24000)
    corpus = {'Alice (英文散文)': alice,
              '访问日志 (合成)': log,
              '随机字节 (合成)': rnd}

    out = dict(
        corpus_size=len(alice),
        window_curve=lz.window_curve(alice),
        corpora=lz.measure(corpus),
        stats=lz.match_stats(alice),
        lazy=lz.lazy_compare(alice),
        runs=lz.run_length_demo(),
        repeat=lz.repeat_demo(),
        walk=walkthrough('the cat sat on the mat, the cat sat'),
        worst=lz.measure({'随机 24000 字节': rnd})[0],
        deflate_bits=len(json.dumps({}, indent=1)),
    )
    out.pop('deflate_bits')
    (HERE / 'results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + '\n', 'utf-8')

    print('corpus %d bytes (%s)' % (len(alice), 'corpus/alice.txt'))
    print('window -> ratio:',
          ', '.join('%d:%.3f' % (r['window'], r['ratio'])
                    for r in out['window_curve']))
    for r in out['corpora']:
        print('  %-18s %6d B  H=%.2f  lz77 %.3f  deflate %.3f'
              % (r['name'], r['size'], r['entropy'], r['lz77'], r['deflate']))
    s = out['stats']
    print('matches %d / tokens %d, coverage %.1f%%, mean len %.1f, mean dist %.0f'
          % (s['matches'], s['tokens'], 100 * s['coverage'], s['mean_length'],
             s['mean_distance']))
    print('lazy:', out['lazy'])
    print('runs:', out['runs'])
    print('repeat:', out['repeat'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
