"""Reproduce examples and finite checks, CC0-1.0."""
from pathlib import Path
from itertools import product
from collections import Counter
from fractions import Fraction
import json, math, platform, random
from cms import CountMin, HASHES, STREAM, demo
ROOT=Path(__file__).resolve().parent
out=demo()
out['configuration']={'width':4,'depth':3,'unit_increment':1,
 'merge_split':6,'noise_threshold':2,'counter_bits':64,'reference_total':1000000}
# General linear table demonstration: deliberately separate from CountMin.add,
# whose teaching API rejects negative increments. Apply signed updates directly.
linear_rows=[[0]*4 for _ in HASHES]
linear_exact=Counter()
def linear_update(key, delta):
 linear_exact[key]+=delta
 for row,h in zip(linear_rows,HASHES):
  row[h(key)]+=delta
 # Independently reconstruct all buckets from the signed frequency vector.
 for j,h in enumerate(HASHES):
  assert linear_rows[j]==[sum(v for k,v in linear_exact.items() if h(k)==col) for col in range(4)]
def linear_snapshot(delta):
 candidates=[row[h('A')] for row,h in zip(linear_rows,HASHES)]
 return {'update_key':'B' if delta else None,'delta':delta,
  'exact':dict(linear_exact),'table':[row[:] for row in linear_rows],
  'A_candidates':candidates,'A_estimate':min(candidates),
  'first_A_bucket':candidates[0],
  'all_frequencies_nonnegative':all(v>=0 for v in linear_exact.values())}
for key in STREAM:linear_update(key,1)
initial=linear_snapshot(0)
linear_update('B',-2);legal_delete=linear_snapshot(-2)
linear_update('B',-4);negative_frequency=linear_snapshot(-4)
assert [x['first_A_bucket'] for x in [initial,legal_delete,negative_frequency]]==[9,7,3]
assert legal_delete['all_frequencies_nonnegative']
assert not negative_frequency['all_frequencies_nonnegative']
assert negative_frequency['A_estimate']<negative_frequency['exact']['A']
out['deletions']={'method':'signed linear table update, not CountMin.add',
 'states':[initial,legal_delete,negative_frequency]}
assert out['exact']==dict(A=6,B=3,C=2,D=1,E=0)
assert out['candidates']['A']==[9,8,7]
# Exhaustively inspect all short streams over the supported alphabet.
checked=0
for n in range(7):
 for stream in product('ABCD',repeat=n):
  s=CountMin(4,HASHES); exact=Counter(stream)
  for k in stream:s.add(k)
  assert all(s.query(k)>=exact[k] for k in 'ABCDE')
  assert all(sum(row)==n for row in s.rows)
  checked+=1
# Every split of the main stream must merge to the same table.
for split in range(len(STREAM)+1):
 a=CountMin(4,HASHES); b=CountMin(4,HASHES)
 for k in STREAM[:split]:a.add(k)
 for k in STREAM[split:]:b.add(k)
 a.merge(b);assert a.rows==out['table'] and a.total==out['total']
a=CountMin(4,HASHES);b=CountMin(4,HASHES)
for k in STREAM[:6]:a.add(k)
for k in STREAM[6:]:b.add(k)
out['merge']={'left':a.rows,'right':b.rows,'sum':out['table']}
# Exact fully random one-row mapping, four keys and four buckets.
hist=Counter()
for cols in product(range(4),repeat=4):
 noise=sum(f for c,f in zip(cols[1:],[out['exact'][k] for k in 'BCD']) if c==cols[0])
 hist[noise]+=1
assert sum(hist.values())==256
# Independent rows: min noise > t iff all row noises > t.
minhist={t:Fraction(sum(v for k,v in hist.items() if k>=t),256)**3-Fraction(sum(v for k,v in hist.items() if k>t),256)**3 for t in range(7)}
assert sum(minhist.values())==1
out['enumeration']={'row_mappings':256,'row_noise_hist':dict(sorted(hist.items())),
 'row_clean':str(Fraction(hist[0],256)), 'three_rows_clean':str(1-(1-Fraction(hist[0],256))**3),
 'min_noise_pmf':{str(k):str(v) for k,v in minhist.items()},
 'one_row_above_2':str(Fraction(sum(v for k,v in hist.items() if k>2),256)),
 'three_rows_above_2':str(Fraction(sum(v for k,v in hist.items() if k>2),256)**3)}
out['sizes']=[]
for eps,delta in [(.01,.001),(.001,.001),(.01,.000001)]:
 w=math.ceil(math.e/eps);d=math.ceil(math.log(1/delta))
 out['sizes'].append(dict(epsilon=eps,delta=delta,width=w,depth=d,counters=w*d,bytes64=w*d*8,error_at_million=eps*1000000))
out['checks']={'exhaustive_streams':checked,'merge_splits':len(STREAM)+1,'python':platform.python_version()}
# Actual repeated fully random hash maps; fixed data, random maps, no adaptive keys.
rng=random.Random(20261025);runs=10000;observed=Counter()
for _ in range(runs):
 noise=[]
 for row in range(3):
  cols=[rng.randrange(4) for _ in range(4)]
  noise.append(sum(f for c,f in zip(cols[1:],[out['exact'][k] for k in 'BCD']) if c==cols[0]))
 observed[min(noise)]+=1
out['experiment']={'runs':runs,'seed':20261025,'min_noise_counts':{str(k):observed[k] for k in range(7)}}
(ROOT/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':out['checks'],'enumeration':out['enumeration'],'experiment':out['experiment'],'sizes':out['sizes']},ensure_ascii=False,indent=2))
