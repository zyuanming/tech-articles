"""Independent teaching model, not a native memory allocator. CC0-1.0."""
from pathlib import Path
import argparse
import json
import random


class Buddy:
    def __init__(self, total=64, unit=8, base=0x1008):
        if any(type(v) is not int for v in (total, unit, base)):
            raise ValueError('integer configuration required')
        if unit <= 0 or unit & (unit - 1):
            raise ValueError('unit must be a power of two')
        if total < unit or total & (total - 1):
            raise ValueError('total must be a power of two >= unit')
        if base < 0 or base % unit:
            raise ValueError('base must be nonnegative and unit aligned')
        self.total, self.unit, self.base = total, unit, base
        self.top = (total // unit).bit_length() - 1
        self.free = [dict() for _ in range(self.top + 1)]
        self.free[self.top][0] = None
        self.used = {}
        self.events = []
        self.record('初始整块空闲')

    def size(self, order):
        return self.unit << order

    def order_for(self, request):
        if type(request) is not int or request <= 0:
            raise ValueError('request must be a positive integer')
        units = (request + self.unit - 1) // self.unit
        return (units - 1).bit_length()

    def record(self, title, pending=None, detail=None):
        blocks = []
        for order, table in enumerate(self.free):
            blocks.extend(dict(offset=o, size=self.size(order),
                               order=order, kind='free', name='空闲')
                          for o in table)
        blocks.extend(dict(offset=v['offset'], size=self.size(v['order']),
                           order=v['order'], kind='used', name=name,
                           request=v['request'])
                      for name, v in self.used.items())
        if pending:
            o, k = pending
            blocks.append(dict(offset=o, size=self.size(k), order=k,
                               kind='pending', name='处理中'))
        blocks.sort(key=lambda b: b['offset'])
        cursor = 0
        for b in blocks:
            assert b['offset'] == cursor
            assert b['offset'] % b['size'] == 0
            cursor += b['size']
        assert cursor == self.total
        free_bytes = sum(b['size'] for b in blocks if b['kind'] == 'free')
        largest = max((b['size'] for b in blocks if b['kind'] == 'free'), default=0)
        internal = sum(b['size'] - b['request'] for b in blocks if b['kind'] == 'used')
        self.events.append(dict(title=title, blocks=blocks,
            free_lists=[sorted(t) for t in self.free], free_bytes=free_bytes,
            largest=largest, internal=internal, detail=detail))

    def alloc(self, name, request):
        if not isinstance(name, str) or not name or name in self.used:
            raise ValueError('unique nonempty name required')
        target = self.order_for(request)
        order = target
        while order <= self.top and not self.free[order]:
            order += 1
        if order > self.top:
            self.record(f'{name} 请求 {request} 字节失败', detail={'target': target})
            return None
        offset, _ = self.free[order].popitem()
        while order > target:
            order -= 1
            right = offset + self.size(order)
            self.free[order][right] = None
            self.record('对半分裂', (offset, order),
                        dict(left=offset, right=right, order=order))
        self.used[name] = dict(offset=offset, order=target, request=request)
        self.record(f'分配 {name}：请求 {request} 字节')
        self.check_canonical()
        return self.base + offset

    def release(self, name):
        if name not in self.used:
            raise ValueError('unknown or already released allocation')
        item = self.used.pop(name)
        offset, order = item['offset'], item['order']
        self.record(f'释放 {name}，检查伙伴', (offset, order))
        while order < self.top:
            other = offset ^ self.size(order)
            if other not in self.free[order]:
                break
            del self.free[order][other]
            old_order = order
            offset = min(offset, other)
            order += 1
            self.record('同阶伙伴合并', (offset, order),
                        dict(buddy=other, old_order=old_order, order=order))
        self.free[order][offset] = None
        self.record(f'{name} 释放完成')
        self.check_canonical()

    def check_canonical(self):
        for order, table in enumerate(self.free[:-1]):
            for offset in table:
                assert offset ^ self.size(order) not in table


def scenarios():
    main = Buddy()
    for name, size in [('A', 13), ('B', 9), ('C', 17)]:
        main.alloc(name, size)
    for name in ['A', 'B', 'C']:
        main.release(name)
    alternate = Buddy()
    for name, size in [('A',13),('B',9),('C',17)]:
        alternate.alloc(name,size)
    for name in ['C','A','B']:
        alternate.release(name)
    assert alternate.free[alternate.top] == {0:None}
    assert sum(e['title'] == '同阶伙伴合并' for e in alternate.events) == 2
    frag = Buddy()
    for name in ['P', 'Q', 'R', 'S']:
        frag.alloc(name, 16)
    frag.release('Q')
    frag.release('R')
    before = len(frag.events) - 1
    assert frag.alloc('T', 17) is None
    failed = len(frag.events) - 1
    frag.release('P')
    frag.release('S')
    frag.alloc('T', 17)
    b = 0x1008
    offset, size = 16, 16
    xor = dict(base=b, offset=offset, size=size, address=b+offset,
               partner=offset ^ size, correct=b+(offset ^ size),
               wrong=(b+offset)^size)
    # At size 8, base 0x1008 shifts the binary partition boundaries.
    xor_bad = dict(base=b, offset=8, size=8, address=b+8,
                   correct=b+(8^8), wrong=(b+8)^8)
    assert xor_bad['correct'] != xor_bad['wrong']
    arenas = [Buddy(32,8,0x2000), Buddy(32,8,0x2020)]
    arena_data = [dict(base=a.base,total=a.total,free=a.events[-1]['free_bytes'],
                       accepted=a.alloc('large',48) is not None) for a in arenas]
    rounding = [dict(request=r, order=main.order_for(r),
                     size=main.size(main.order_for(r))) for r in [1,8,9,13,16,17,32,33,64]]
    for r in rounding:r['waste']=r['size']-r['request']
    return dict(model='buddy-teaching-1.0', base=main.base,total=main.total,
        unit=main.unit,top=main.top,rounding=rounding,main=main.events,
        fragment=frag.events,fragment_before=before,fragment_failed=failed,
        xor=xor,xor_bad=xor_bad,arenas=arena_data,alternate=alternate.events,
        colors=dict(free='#d7eee2',used='#dbe9fa',pending='#ffdfab',
                    waste='#f3c5c0',ink='#142d42'))


def test():
    # Independent occupied-cell oracle checks successful allocations and frees.
    rng = random.Random(19019)
    b = Buddy(256,8,0x1010)
    occupied = [None] * b.total
    live = {}
    success = failures = 0
    for step in range(2000):
        if live and rng.random() < 0.48:
            name = rng.choice(list(live))
            o, size = live.pop(name)
            b.release(name)
            for i in range(o,o+size):
                assert occupied[i] == name
                occupied[i] = None
        else:
            request = rng.randint(1,95)
            name = f'N{step}'
            target = b.size(b.order_for(request))
            possible = any(all(x is None for x in occupied[o:o+target])
                           for o in range(0,b.total-target+1,target))
            result = b.alloc(name,request)
            assert (result is not None) == possible
            if result is None:failures += 1
            else:
                o = result-b.base
                assert all(x is None for x in occupied[o:o+target])
                occupied[o:o+target] = [name]*target
                live[name] = (o,target)
                success += 1
        b.check_canonical()
    for name in list(live):b.release(name)
    assert b.free[b.top] == {0:None}
    for invalid in [0,-1,True,1.5]:
        try:b.alloc('bad',invalid)
        except ValueError:pass
        else:raise AssertionError(invalid)
    b.alloc('once',8)
    b.release('once')
    try:b.release('once')
    except ValueError:pass
    else:raise AssertionError('actual double free')
    try:b.release('missing')
    except ValueError:pass
    else:raise AssertionError('double-free protection')
    return dict(seed=19019,operations=2000,allocations=success,failures=failures,
                oracle='per-byte occupied cells, aligned target windows')


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=Path(__file__).with_name('results.json'))
    args=p.parse_args()
    data=scenarios()
    data['tests']=test()
    args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(data['tests'],ensure_ascii=False))
