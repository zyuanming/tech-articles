"""Original teaching implementation; CC0-1.0. Python 3, Unicode code points."""
from collections import deque
from itertools import product
import json
from pathlib import Path

class Matcher:
    def __init__(self, patterns):
        self.patterns = list(patterns)
        if any(not p for p in self.patterns):
            raise ValueError('empty patterns are excluded')
        self.child = [{}]; self.fail = [0]; self.end = [[]]
        self.link = [0]; self.label = ['']
        for pid, pattern in enumerate(self.patterns):
            v = 0
            for ch in pattern:
                if ch not in self.child[v]:
                    self.child[v][ch] = len(self.child)
                    self.child.append({}); self.fail.append(0)
                    self.end.append([]); self.link.append(0)
                    self.label.append(self.label[v] + ch)
                v = self.child[v][ch]
            self.end[v].append(pid)
        queue = deque(self.child[0].values())
        while queue:
            v = queue.popleft()
            for ch, u in self.child[v].items():
                queue.append(u)
                f = self.fail[v]
                while f and ch not in self.child[f]:
                    f = self.fail[f]
                self.fail[u] = self.child[f].get(ch, 0)
                t = self.fail[u]
                self.link[u] = t if self.end[t] else self.link[t]
        self.state = 0; self.offset = 0

    def feed(self, text):
        found = []; trace = []
        for ch in text:
            before = self.state; fallback = []
            while self.state and ch not in self.child[self.state]:
                self.state = self.fail[self.state]
                fallback.append(self.label[self.state] or '根')
            self.state = self.child[self.state].get(ch, 0)
            stop = self.offset + 1; here = []; v = self.state
            while v:
                for pid in self.end[v]:
                    hit = [self.patterns[pid], stop-len(self.patterns[pid]), stop]
                    here.append(hit); found.append(hit)
                v = self.link[v]
            trace.append(dict(i=self.offset,ch=ch,before=self.label[before] or '根',
                              fallback=fallback,state=self.label[self.state] or '根',hits=here))
            self.offset += 1
        return found, trace

def naive(patterns, text):
    return sorted([p,i,i+len(p)] for p in patterns for i in range(len(text)) if text.startswith(p,i))

def experiment():
    patterns = ['he','she','his','hers']; text = 'ushershis'
    ac = Matcher(patterns); hits, trace = ac.feed(text)
    assert sorted(hits) == naive(patterns,text)
    for k in range(len(text)+1):
        s = Matcher(patterns)
        assert s.feed(text[:k])[0]+s.feed(text[k:])[0] == hits
    cases = 0
    pool = ['a','b','aa','ab','ba','bb']
    for bits in range(1,1<<len(pool)):
        ps = [p for j,p in enumerate(pool) if bits>>j&1]
        for n in range(7):
            for chars in product('ab',repeat=n):
                t = ''.join(chars)
                assert sorted(Matcher(ps).feed(t)[0]) == naive(ps,t)
                cases += 1
    assert sorted(Matcher(['a','a']).feed('aa')[0]) == naive(['a','a'],'aa')
    assert Matcher([]).feed('abc')[0] == []
    assert Matcher(['墨水','水']).feed('电泳墨水')[0] == [['墨水',2,4],['水',3,4]]
    try: Matcher([''])
    except ValueError: pass
    else: raise AssertionError('empty pattern accepted')
    data=dict(patterns=patterns,text=text,hits=hits,trace=trace,
              nodes=[dict(label=ac.label[v] or '根',fail=ac.label[ac.fail[v]] or '根',
                          end=ac.end[v]) for v in range(len(ac.child))],
              cases=cases,split_tests=len(text)+1)
    Path(__file__).with_name('results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(data,ensure_ascii=False))

if __name__ == '__main__': experiment()
