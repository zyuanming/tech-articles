"""Recompute examples, exhaustive checks and deterministic experiments. CC0-1.0."""
from itertools import product
from pathlib import Path
import json, platform, random, statistics
from selection import quickselect, trace
ROOT = Path(__file__).resolve().parent
A = [8, 3, 7, 3, 9, 1, 6, 3, 5]
K = 6
main = trace(A, K, lambda a, r: [5, 7, 6][r])
assert main['answer'] == sorted(A)[K-1] == 6
checks = 0
for n in range(1, 8):
    for a in product([-1, 0, 1], repeat=n):
        for k in range(1, n+1):
            assert quickselect(a, k, random.Random(checks)) == sorted(a)[k-1]
            checks += 1
for a in [[], [1]]:
    for k in [0, -1, len(a)+1, 1.2, True]:
        try: quickselect(a, k)
        except ValueError: pass
        else: raise AssertionError((a, k))
for a in [[float('nan')], [1.0], [True]]:
    try: quickselect(a, 1)
    except TypeError: pass
    else: raise AssertionError(a)
rng=random.Random(20261025)
for j in range(500):
    a=[rng.randrange(-100,101) for _ in range(rng.randrange(1,100))]
    original=a.copy(); k=rng.randrange(1,len(a)+1)
    assert quickselect(a,k,rng)==sorted(a)[k-1] and a==original
for m in range(1, 257):
    average=sum(max(r-1,m-r) for r in range(1,m+1))/m
    formula=3*m/4-0.5-(1/(4*m) if m%2 else 0)
    assert abs(average-formula)<1e-12 and average<=3*m/4
assert [max(r-1,4-r) for r in range(1,5)] == [3,2,2,3]
n=16
costs={name:trace(list(range(1,n+1)),n,pick) for name,pick in [
    ('balanced',lambda a,r:sorted(a)[len(a)//2]),('worst',lambda a,r:min(a))]}
experiments=[]
for n in [64,128,256,512,1024]:
    visits=[]
    for seed in range(200):
        rng=random.Random(seed)
        visits.append(trace(list(range(n)),n//2,lambda a,r:rng.choice(a))['visits'])
    experiments.append(dict(n=n, trials=len(visits),mean_visits=statistics.mean(visits),
                            ratio=statistics.mean(visits)/n,min_visits=min(visits),max_visits=max(visits)))
data=dict(input=A,k=K,index=K-1,sorted=sorted(A),main=main,
          duplicate=trace(A,4,lambda a,r:3),all_equal=trace([3]*9,6,lambda a,r:3),
          costs=costs,experiments=experiments,
          good_pivots=dict(n=16,ranks=list(range(1,17)),good=list(range(5,13)),max_side=11),
          topk=dict(k=3,threshold=3,below=[1],equal=[3,3,3],needed=2),
          validation=dict(exhaustive_cases=checks,random_cases=500,python=platform.python_version(),seed=20261025))
(ROOT/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(answer=main['answer'],visits=main['visits'],validation=data['validation'],experiments=experiments),ensure_ascii=False))
