"""Independent cut oracle, exact partition recursion, and sampled checks. CC0-1.0."""
import json, random, platform, math
from pathlib import Path
from itertools import combinations
from fractions import Fraction
from collections import Counter, defaultdict
from functools import lru_cache
from karger import trial, prepare, repeat
ROOT = Path(__file__).parent

def cuts(n, edges):
    # Hold vertex 0 on the left to avoid counting complements twice.
    rows=[]
    for mask in range(1 << (n-1)):
        left={0}|{v for v in range(1,n) if mask & (1 << (v-1))}
        if len(left)==n: continue
        right=set(range(n))-left
        rows.append({'parts':[sorted(left),sorted(right)],
                     'value':sum((u in left)!=(v in left) for u,v in edges)})
    return rows

def distribution(n, edges):
    # Never rewrite edge endpoints: derive all active edges from original
    # membership in a partition. Independent of trial's edge-list updates.
    @lru_cache(None)
    def visit(parts):
        owner={v:i for i,p in enumerate(parts) for v in p}
        pairs=[(owner[u],owner[v]) for u,v in edges if owner[u]!=owner[v]]
        if len(parts)==2: return {parts:Fraction(1)}
        out=defaultdict(Fraction)
        for a,b in pairs:
            merged=tuple(sorted(parts[a]+parts[b]))
            nxt=tuple(sorted([p for i,p in enumerate(parts) if i not in (a,b)]+[merged]))
            for final,p in visit(nxt).items(): out[final]+=p/len(pairs)
        return dict(out)
    return visit(tuple((i,) for i in range(n)))

def certify(n,edges,rng,trials):
    rows=cuts(n,edges);oracle=min(r['value'] for r in rows)
    dist=distribution(n,edges)
    assert sum(dist.values())==1
    lookup={tuple(tuple(p) for p in r['parts']):r['value'] for r in rows}
    for row in rows:
        if row['value']==oracle:
            assert dist.get(tuple(tuple(p) for p in row['parts']),0)>=Fraction(2,n*(n-1))
    for _ in range(trials):
        r=trial(n,edges,rng);key=tuple(tuple(p) for p in r['parts'])
        assert r['value']==lookup[key]>=oracle
    return oracle,dist

k4=list(combinations(range(4),2));rows=cuts(4,k4)
rng=random.Random(20261025);counts=Counter();example={}
for _ in range(10000):
    r=trial(4,k4,rng);counts[r['value']]+=1
    example.setdefault(r['value'],r)
checked=0;counts_by_n={};check_rng=random.Random(20261026)
for n in range(2,6):
    possible=list(combinations(range(n),2));number=0
    for mask in range(1<<len(possible)):
        edges=[e for j,e in enumerate(possible) if mask & (1<<j)]
        try:prepare(n,edges)
        except ValueError:continue
        certify(n,edges,check_rng,8);number+=1
    counts_by_n[n]=number;checked+=number
multis=[(2,[(0,1)]*3+[(0,0)]),(3,[(0,1)]*2+[(1,2)]*3+[(0,2)]),(4,k4+[(0,1)]*2+[(2,2)])]
for n,e in multis:certify(n,e,check_rng,100)
rejected=[]
for n,e in [(1,[]),(3,[(0,1)]),(3,[]),(2,[(0,2)]),(2,[(0,0),(1,1)])]:
    try:trial(n,e,check_rng)
    except ValueError:rejected.append([n,e])
    else:raise AssertionError('invalid input accepted')
dist=distribution(4,k4)
exact_by_value=defaultdict(Fraction)
for parts,p in dist.items():
    left=set(parts[0]);value=sum((u in left)!=(v in left) for u,v in k4)
    exact_by_value[value]+=p
n=4;lower=Fraction(2,n*(n-1));delta=0.01
T=math.ceil(math.log(1/delta)/float(lower))
# Compute the teaching contraction directly from original edge identities.
owner={0:'AB',1:'AB',2:'C',3:'D'}
remaining=[e for e in k4 if owner[e[0]]!=owner[e[1]]]
copies=[''.join('ABCD'[v] for v in e) for e in remaining]
pair_counts=Counter(tuple(sorted((owner[u],owner[v]))) for u,v in remaining)
degrees=Counter(x for u,v in remaining for x in (owner[u],owner[v]))
# Unweighted leaf counts are only used for K4, where each branch has 6 then 5 choices.
def leaves(parts):
    own={v:i for i,g in enumerate(parts) for v in g}
    active=[(own[u],own[v]) for u,v in k4 if own[u]!=own[v]]
    if len(parts)==2:return [len(active)]
    out=[]
    for a,b in active:
        nxt=tuple(sorted([g for i,g in enumerate(parts) if i not in (a,b)]+[tuple(sorted(parts[a]+parts[b]))]))
        out.extend(leaves(nxt))
    return out
leaf_values=leaves(tuple((i,) for i in range(n)))
path_matrix=[]
for u,v in k4:
    groups=[tuple(sorted((u,v)))]+[(x,) for x in range(n) if x not in (u,v)]
    own={x:i for i,g in enumerate(groups) for x in g}
    options=[]
    for a,b in k4:
        if own[a]==own[b]:continue
        merged=set(groups[own[a]])|set(groups[own[b]])
        final=[merged]+[set(g) for i,g in enumerate(groups) if i not in (own[a],own[b])]
        value=sum((x in final[0])!=(y in final[0]) for x,y in k4)
        options.append({'second':''.join('ABCD'[x] for x in (a,b)),'value':value})
    path_matrix.append({'first':''.join('ABCD'[x] for x in (u,v)),'options':options})
assert Counter(o['value'] for r in path_matrix for o in r['options'])==Counter(leaf_values)
endpoint_map=[{'original':list(e),'updated':[0 if v==1 else v for v in e],
               'keep':(0 if e[0]==1 else e[0])!=(0 if e[1]==1 else e[1])} for e in k4]

fixed_left={0,1,2}
safe_first=sum((u in fixed_left)==(v in fixed_left) for u,v in k4)
safe_next=sum((u in fixed_left)==(v in fixed_left) for u,v in remaining)
steps={'first_total':len(k4),'first_safe':safe_first,'next_total':len(remaining),'next_safe':safe_next,
       'first_lower':str(Fraction(n-2,n)),'next_lower':str(Fraction(n-3,n-1))}

data={'python':platform.python_version(),'model':'connected undirected unweighted multigraph; loops removed; disconnected rejected','n':4,'edges':k4,'path_matrix':path_matrix,'endpoint_map':endpoint_map,'cuts':rows,'mincut':min(r['value'] for r in rows),'after_ab':{'groups':['AB','C','D'],'copies':copies,'multiplicities':[pair_counts[('AB','C')],pair_counts[('AB','D')],pair_counts[('C','D')]],'degrees':[degrees[g] for g in ['AB','C','D']]},'sample':{'seed':20261025,'runs':10000,'counts':dict(counts),'examples':example},'exact':{'by_value':{str(v):str(p) for v,p in exact_by_value.items()},'fixed_D':str(dist[((0,1,2),(3,))]),'lower':str(lower),'leaf_paths':len(leaf_values),'successful_leaf_paths':sum(v==min(r['value'] for r in rows) for v in leaf_values),'steps':steps},'repeat':{'T':T,'delta':0.01,'generic_failure':float((1-lower)**T),'exp_bound':math.exp(-float(lower)*T),'k4_failure':float(Fraction(1,5)**T),'four_k4_failure':str(Fraction(1,5)**4),'table':[{'T':t,'generic':float((1-lower)**t),'actual_k4':float(Fraction(1,5)**t)} for t in [1,4,10,28]]},'checks':{'seed':20261026,'all_connected_simple_by_n':counts_by_n,'total_graphs':checked,'random_trials_per_graph':8,'multigraph_cases':len(multis),'multigraph_trials_each':100,'invalid_cases_rejected':len(rejected),'fixed_cut_bound':'all minimum cuts checked by exact Fraction enumeration'},'repeated_example':repeat(4,k4,T,20261027)}
(ROOT/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(data,ensure_ascii=False,indent=2))
