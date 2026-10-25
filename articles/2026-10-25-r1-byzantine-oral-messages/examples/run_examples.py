"""Execute every article example and finite test; outputs CC0-1.0."""
from pathlib import Path
from itertools import product, combinations
from collections import Counter
import json, random, platform
from om import simulate, majority, ATTACK as P, RETREAT as R
ROOT=Path(__file__).resolve().parent
N=['C','A','B','D']
bad_c=simulate(N,1,['C'],strategy=lambda p,t,v: P if t=='A' else R)
good_c=simulate(N,1,['D'],strategy=lambda p,t,v: R if t=='A' else P)
missing=simulate(N,1,['C'],strategy=lambda p,t,v: P if t=='A' else (R if t=='B' else None))
N7=['C','A','B','D','E','F','G']
def deep_strategy(p,t,v):
    if p==('C',): return P if t in ['A','B','E'] else R
    return P if N7.index(t)%2 else R
higher=simulate(N7,2,['C','B'],strategy=deep_strategy)
for s in [bad_c,good_c,missing,higher]:
    assert s['agreement'] and s['validity'] is not False
    s['top']=[x for x in s['reductions'] if len(x['path'])==1]
    s['round_counts']=dict(sorted(Counter(e['round'] for e in s['events']).items()))
    for row in s['top']:
        row['counts']={v:row['vector'].count(v) for v in [P,R]}
# Exhaust all effective ternary choices for one faulty sender, n4 OM1.
tested=0
for command in [P,R]:
    s=simulate(N,1,command=command);assert s['agreement'] and s['validity'];tested+=1
for bad in N:
    skeleton=simulate(N,1)
    slots=[(tuple(e['path']),e['target']) for e in skeleton['events'] if e['sender']==bad]
    for cmd in ([P] if bad=='C' else [P,R]):
        for choices in product([P,R,None],repeat=len(slots)):
            table=dict(zip(slots,choices))
            s=simulate(N,1,[bad],cmd,lambda p,t,v:table[p,t])
            assert s['agreement'] and s['validity'] is not False
            tested+=1
# Each random run has its own explicitly recorded seed, no generator sharing.
seeds=list(range(20261025,20261125));random_cases=[]
for seed in seeds:
    rng=random.Random(seed)
    faulty=rng.sample(N7,2);cmd=rng.choice([P,R])
    skeleton=simulate(N7,2)
    table={(tuple(e['path']),e['target']):rng.choice([P,R,None]) for e in skeleton['events'] if e['sender'] in faulty}
    s=simulate(N7,2,faulty,cmd,lambda p,t,v:table[p,t])
    assert s['agreement'] and s['validity'] is not False
    random_cases.append(dict(seed=seed,faulty=faulty,command=cmd,agreement=s['agreement'],validity=s['validity']))
# Count actual scheduled edges, independently compare a falling-product formula.
growth=[]
for m in range(4):
    n=3*m+1 if m else 2
    s=simulate(['C']+[str(i) for i in range(n-1)],m)
    counts=Counter(e['round'] for e in s['events']);term=1;terms=[]
    for r in range(1,m+2):term*=n-r;terms.append(term)
    assert list(counts.values())==terms and sum(terms)==s['slots']
    growth.append(dict(n=n,m=m,rounds=s['rounds'],by_round=terms,slots=s['slots']))
# n3 OM1 breaks validity even though its tie rule makes this run unanimous.
under=simulate(['C','A','B'],1,['B'],P,lambda p,t,v:R)
assert under['loyal']['A']==R and under['validity'] is False
# Three indistinguishable-world projections, descriptive traces, not a proof by test.
worlds=[dict(name='世界一：C忠诚，B恶意',bad='B',direct={ 'A':P,'B':P},relay={'A':R,'B':P}),
        dict(name='世界二：C恶意',bad='C',direct={'A':P,'B':R},relay={'A':R,'B':P}),
        dict(name='世界三：C忠诚，A恶意',bad='A',direct={'A':R,'B':R},relay={'A':R,'B':P})]
for w in worlds:w['view']={t:[w['direct'][t],w['relay'][t]] for t in ['A','B']}
assert worlds[0]['view']['A']==worlds[1]['view']['A']
assert worlds[1]['view']['B']==worlds[2]['view']['B']
exercise=simulate(N,1,['C'],strategy=lambda p,t,v:P if t!='D' else R)
result=dict(python=platform.python_version(),model='synchronous oral messages; no digital signatures',
 default=R,bad_c=bad_c,good_c=good_c,missing=missing,higher=higher,growth=growth,
 tests=dict(n4_ternary_cases=tested,n7_seeded_cases=len(seeds),seeded_runs=random_cases),
 under=under,worlds=worlds,exercise=exercise)
(ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(f'n4 ternary cases: {tested}; n7 seeded cases: {len(seeds)}; all guaranteed runs passed')
print('growth:',[(r['n'],r['m'],r['slots']) for r in growth])
print('higher loyal:',higher['loyal'])
print('higher top:',higher['top'])
