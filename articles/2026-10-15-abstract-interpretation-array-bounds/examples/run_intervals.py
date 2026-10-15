"""Original, bounded teaching model. Not a Python/C source-code analyzer."""
from dataclasses import dataclass
from pathlib import Path
import argparse,csv,json,math,platform
INF=math.inf
@dataclass(frozen=True)
class I:
    lo: int | float
    hi: int | float
    def contains(self,x): return self.lo <= x <= self.hi
    def join(self,b): return I(min(self.lo,b.lo),max(self.hi,b.hi))
    def add(self,b): return I(self.lo+b.lo,self.hi+b.hi)
    def cap(self,hi): return None if self.lo>min(self.hi,hi) else I(self.lo,min(self.hi,hi))
    def widen(self,b): return I(-INF if b.lo<self.lo else self.lo, INF if b.hi>self.hi else self.hi)
    def data(self): return [('-inf' if x==-INF else 'inf' if x==INF else x) for x in (self.lo,self.hi)]
ENTRY=I(0,0)
def body(head,n_max=8,inclusive=False): return head.cap(n_max if inclusive else n_max-1)
def transfer(head,n_max=8,inclusive=False):
    b=body(head,n_max,inclusive)
    return ENTRY if b is None else ENTRY.join(b.add(I(1,1)))
def trace(n_max=8,inclusive=False,widen_after=None):
    h=ENTRY;rows=[]
    for iteration in range(100):
        b=body(h,n_max,inclusive);f=transfer(h,n_max,inclusive)
        nxt=h.widen(f) if widen_after is not None and iteration>=widen_after else f
        rows.append(dict(iteration=iteration,head=h.data(),body=None if b is None else b.data(),transfer=f.data(),next=nxt.data(),stable=nxt==h))
        if nxt==h:return rows,h
        h=nxt
    raise AssertionError('Teaching analysis did not converge')
def concrete(inclusive=False,n_max=8):
    rows=[];heads=[]
    for n in range(n_max+1):
        i=0
        while True:
            heads.append(dict(n=n,i=i))
            if not (i<=n if inclusive else i<n):break
            rows.append(dict(n=n,i=i,safe=0<=i<8));i+=1
    return rows,heads

def main(out):
    out.mkdir(parents=True,exist_ok=False)
    good,gh=trace();bad,bh=trace(inclusive=True);wide,wh=trace(widen_after=2)
    narrow1=transfer(wh);narrow2=transfer(narrow1)
    gr,gheads=concrete();br,bheads=concrete(True)
    assert gh==I(0,8) and body(gh)==I(0,7)
    assert bh==I(0,9) and body(bh,inclusive=True)==I(0,8)
    assert wh==I(0,INF) and body(wh)==I(0,7) and narrow1==narrow2==I(0,8)
    assert len(gr)==36 and all(r['safe'] for r in gr)
    assert len(br)==45 and [r for r in br if not r['safe']]==[dict(n=8,i=8,safe=False)]
    assert all(gh.contains(r['i']) for r in gheads)
    assert all(body(gh).contains(r['i']) for r in gr)
    assert transfer(gh)==gh and transfer(wh).hi<=wh.hi
    pairs=[(0,1),(1,0)];box=[(x,y) for x in range(2) for y in range(2)]
    assert {x+y for x,y in pairs}=={1} and {x+y for x,y in box}=={0,1,2}
    # Exhaustive finite validation of local transfer rules, separate from analysis.
    intervals=[I(a,b) for a in range(-3,4) for b in range(a,4)]
    add_cases=join_cases=guard_cases=0
    for a in intervals:
        for b in intervals:
            for x in range(a.lo,a.hi+1):
                for y in range(b.lo,b.hi+1):
                    assert a.add(b).contains(x+y);add_cases+=1
                    assert a.join(b).contains(x) and a.join(b).contains(y);join_cases+=1
                    capped=a.cap(b.hi-1)
                    if x<y: assert capped is not None and capped.contains(x)
                    guard_cases+=1
    # Each bounded-loop precondition, checked against exact executions.
    loop_checks=[]
    for limit in range(33):
        for incl in (False,True):
            tr,h=trace(limit,incl);rows,heads=concrete(incl,limit)
            assert all(h.contains(r['i']) for r in heads)
            b=body(h,limit,incl)
            assert all(b is not None and b.contains(r['i']) for r in rows)
            loop_checks.append(dict(n_max=limit,inclusive=incl,head=h.data(),body=None if b is None else b.data(),accesses=len(rows)))
    result=dict(model='Unbounded mathematical integers; array length8; no alias/concurrency/overflow; n constant integer in [0,8]',python=platform.python_version(),concrete_good=dict(heads=gheads,accesses=gr),concrete_bad=dict(heads=bheads,accesses=br),good=dict(trace=good,head=gh.data(),body=body(gh).data(),accesses=len(gr),head_visits=len(gheads)),bad=dict(trace=bad,head=bh.data(),body=body(bh,inclusive=True).data(),accesses=len(br),violations=[r for r in br if not r['safe']]),widen=dict(trace=wide,head=wh.data(),body=body(wh).data(),narrow=[narrow1.data(),narrow2.data()]),correlation=dict(concrete_pairs=pairs,abstract_box=box,actual_sums=[1],interval_sum=[0,2],spurious_unsafe_pairs=[[1,1]]),rule_checks=dict(intervals=len(intervals),add_concrete_pairs=add_cases,join_concrete_pairs=join_cases,guard_concrete_pairs=guard_cases,bounded_loops=len(loop_checks)),loop_checks=loop_checks)
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (out/'concrete-visits.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['variant','n','i','safe']);w.writeheader()
        for v,rs in [('i<n',gr),('i<=n',br)]:
            for row in rs:w.writerow(dict(variant=v,**row))
    summary=f"GOOD: head={gh.data()}, body={body(gh).data()}, accesses={len(gr)}, violations=0\nBAD: head={bh.data()}, body={body(bh,inclusive=True).data()}, accesses={len(br)}, violations=1 at n=8,i=8\nWIDEN: head={wh.data()}, body={body(wh).data()}, narrowed={narrow1.data()}\nCORRELATION: actual sum=1; interval sum=[0,2]; false alarm at 2\nRULE CHECKS: {json.dumps(result['rule_checks'],sort_keys=True)}\n"
    (out/'stdout.txt').write_text(summary);print(summary,end='')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);main(p.parse_args().output)
