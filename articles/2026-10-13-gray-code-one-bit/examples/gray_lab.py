"""Exact Gray-code checks and an explicitly idealized read-head model.
Run with Python 3.10+, standard library only. Writes results.json beside this file.
This is a numerical teaching model, not an encoder hardware test.
"""
from itertools import product
from pathlib import Path
from fractions import Fraction
import json

def encode(n):
    if not isinstance(n, int) or n < 0:
        raise ValueError('n must be a nonnegative integer')
    return n ^ (n >> 1)

def decode(gray):
    if not isinstance(gray, int) or gray < 0:
        raise ValueError('gray must be a nonnegative integer')
    n = 0
    while gray:
        n ^= gray
        gray >>= 1
    return n

def reflected(width):
    if width < 1:
        raise ValueError('width must be positive')
    words = [0, 1]
    for w in range(2, width + 1):
        words += [(1 << (w - 1)) | x for x in reversed(words)]
    return words

def mixes(old, new, width):
    """Every changed bit may independently be old or new; others stay fixed."""
    changed = [b for b in range(width) if ((old ^ new) >> b) & 1]
    out = set()
    for choices in product((0, 1), repeat=len(changed)):
        word = old
        for b, take_new in zip(changed, choices):
            if take_new:
                word ^= 1 << b
        out.add(word)
    return out

def read_heads(x, offsets, gray=False, width=3):
    """x and offsets in sector-width units; ideal instantaneous bits, no noise."""
    word = 0
    for i, offset in enumerate(offsets):
        sector = (x + offset).__floor__() % (1 << width)
        coded = encode(sector) if gray else sector
        bit = width - 1 - i
        word |= ((coded >> bit) & 1) << bit
    return decode(word) if gray else word

def run():
    per_width = []
    for w in range(1, 13):
        count = 1 << w
        seq = reflected(w)
        assert len(set(seq)) == count
        assert seq == [encode(i) for i in range(count)]
        assert [decode(g) for g in seq] == list(range(count))
        binary_candidates = gray_candidates = binary_others = 0
        by_changes = {}
        for i in range(count):
            j = (i + 1) % count
            difference = (seq[i] ^ seq[j]).bit_count()
            assert difference == 1
            gm = mixes(seq[i], seq[j], w)
            assert {decode(x) for x in gm} == {i, j}
            bm = mixes(i, j, w)
            binary_candidates += len(bm)
            gray_candidates += len(gm)
            binary_others += len(bm - {i, j})
            k = (i ^ j).bit_count()
            by_changes[str(k)] = by_changes.get(str(k), 0) + 1
        assert binary_candidates == (w + 1) * count
        assert gray_candidates == 2 * count
        per_width.append(dict(width=w, positions=count,
             binary_candidates=binary_candidates, gray_candidates=gray_candidates,
             binary_other_candidates=binary_others, binary_edges_by_changed_bits=by_changes))
    assert sorted(mixes(3,4,3)) == list(range(8))
    assert sorted(decode(g) for g in mixes(encode(3),encode(4),3)) == [3,4]
    assert [encode(i) for i in range(8)] == [0,1,3,2,6,7,5,4]
    assert decode(0b101) == 6 and encode(6) == 0b101
    assert decode(0b010) == 3  # arbitrary middle-bit flip from 000 is not corrected
    assert (encode(0) ^ encode(2)).bit_count() == 2
    assert (encode(5) ^ encode(0)).bit_count() == 3
    cycle6 = [0,1,3,2,6,4]
    assert all((a ^ b).bit_count() == 1 for a,b in zip(cycle6,cycle6[1:]+cycle6[:1]))
    offsets = [Fraction(6,100),Fraction(-1,100),Fraction(-5,100)]
    points = [Fraction(t,1000) for t in range(3850,4151)]
    traces = [dict(x=str(x),binary=read_heads(x,offsets),gray=read_heads(x,offsets,True)) for x in points]
    assert [read_heads(Fraction(s),offsets) for s in ['3.90','3.97','4.03','4.10']] == [3,7,5,4]
    assert {r['gray'] for r in traces} == {3,4}
    result = dict(model='ideal bits; offsets in sector-width units; no noise or metastability',
        widths_checked=[1,12],cyclic_edges_checked=sum(x['positions'] for x in per_width),
        binary_mixed_words_checked=sum(x['binary_candidates'] for x in per_width),
        gray_mixed_words_checked=sum(x['gray_candidates'] for x in per_width),
        per_width=per_width, offsets=[str(x) for x in offsets], samples=traces,
        gray_sequence_3=reflected(3),six_cycle=cycle6)
    Path(__file__).with_name('results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('per_width','samples')},ensure_ascii=False,indent=2))
    print('8-bit results:',json.dumps(per_width[7],ensure_ascii=False))
    print('All assertions passed.')
    return result

if __name__ == '__main__':
    run()
