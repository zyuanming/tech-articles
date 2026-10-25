"""Generate all exact values and figure samples. Original code/data CC0."""
import json, random, sys
from pathlib import Path
from fractions import Fraction as F
import sympy as sp
from sturm_exact import (poly, derivative, evaluate, divide, multiply, gcd,
                         squarefree, chain, signs, variations, count, isolate)
ROOT=Path(__file__).resolve().parent
p=poly([0,-1,0,1]); q=poly([2,-3,0,1]); s=chain(p)
serialize=lambda p:[str(c) for c in p]

def record(seq, x):
 return dict(x=str(x),values=[str(evaluate(a,x)) for a in seq],
             signs=signs(seq,x),v=variations(seq,x))

def sample(polys,a,b,n=401):
 xs=[F(a)+(F(b)-F(a))*i/(n-1) for i in range(n)]
 return dict(x=[float(x) for x in xs],ys=[[float(evaluate(p,x)) for x in xs] for p in polys])

leaves,tree=isolate(p,-2,2)
wrong=chain(poly([1,0,1])); flipped=wrong[:-1]+[poly(-v for v in wrong[-1])]
tiny=F(1,10**20); close=poly([1-tiny,-2,1]); rounded=poly([F(float(1-tiny)),-2,1])
# Fraction(float(...)) here deliberately models the rounded coefficient.
# The public exact API does not accept the float directly.
D={
 'identity':'Exact rational teaching model; plot samples alone use float coordinates',
 'versions':{'python':sys.version.split()[0],'sympy':sp.__version__},
 'main':{'coefficients':serialize(p),'chain':[serialize(a) for a in s],
         'rows':[record(s,F(x)) for x in ['-2','-1','-1/2','0','1/2','1','2']],
         'counts':{e:count(p,-1,1,e) for e in ['(]','[]','()','[)']},
         'division':[{'dividend':serialize(s[i]),'divisor':serialize(s[i+1]),
                      'quotient':serialize(divide(s[i],s[i+1])[0]),
                      'remainder':serialize(divide(s[i],s[i+1])[1])} for i in range(2)],
         'plot':sample([p],-2,2),
         'roots':['-1','0','1'],
         'v_plot':{'x':[-2,-1,-1,0,0,1,1,2],
                   'v':[variations(s,F(x)) for x in ['-2','-2','-1','-1','0','0','1','2']]},
         'root_steps':[record(s,F(x)) for x in ['9/10','1','11/10']],
         'middle_steps':[record(s,F(x)) for x in ['1/2','3/5']],
         'middle_plot':sample(s[:3],F(1,2),F(3,5)),
         'tangent_plot':sample([p,poly([-2,2])],F(3,4),F(5,4)),
         'isolation':[[str(a),str(b)] for a,b in leaves], 'tree':tree},
 'repeated':{'coefficients':serialize(q),'gcd':serialize(gcd(q,derivative(q))),
             'squarefree':serialize(squarefree(q)),'chain':[serialize(a) for a in chain(q)],
             'count':count(q,-3,2),'plot':sample([q,squarefree(q)],-3,2),
             'touch_plot':sample([q],F(1,2),F(3,2)),
             'samples':[dict(x=str(x),y=str(evaluate(q,x))) for x in [F(1,2),F(3,2)]]},
 'bad_normalization':{'chain':[serialize(a) for a in wrong],
                      'correct':[record(wrong,F(x)) for x in [-2,2]],
                      'wrong':[record(flipped,F(x)) for x in [-2,2]],
                      'plot':sample([poly([1,0,1])],-2,2)},
 'rounding':{'epsilon':str(tiny),'exact_coefficients':serialize(close),
             'rounded_coefficients':serialize(rounded),
             'exact_count':count(close,0,2),'rounded_count':count(rounded,0,2),
             'exact_at_one':str(evaluate(close,1)),
             'rounded_at_one':str(evaluate(rounded,1)),
             'root_offset':str(F(1,10**10)),
             'scaled_x':[float(F(-2)+F(i,100)) for i in range(401)],
             'exact_y':[float((F(-2)+F(i,100))**2-1) for i in range(401)],
             'rounded_y':[float((F(-2)+F(i,100))**2) for i in range(401)]}}

# Factor-generated oracle independent of Sturm: roots and multiplicities known.
rng=random.Random(2026102513); checks=0; cases=80
pool=[F(i,2) for i in range(-6,7)]
for _ in range(cases):
 roots=rng.sample(pool,rng.randint(1,5)); f=poly([rng.choice([-3,-1,1,2])])
 for r in roots:
  for _ in range(rng.randint(1,3)):
   f=multiply(f,poly([-r,1]))
 for _ in range(10):
  a,b=sorted(rng.sample(pool+[F(-4),F(4)],2))
  for e in ['(]','[]','()','[)']:
   expected=sum((r>=a if e[0]=='[' else r>a) and (r<=b if e[1]==']' else r<b) for r in roots)
   assert count(f,a,b,e)==expected,(f,a,b,e,expected)
   checks+=1
# Independent CAS checks on irreducible and repeated-root polynomials.
x=sp.Symbol('x'); cas=[]
for coeff,a,b in [(p,-2,2),(q,-3,2),(poly([1,0,1]),-2,2),
                   (poly([-2,0,1]),0,2),(poly([-1,-1,0,0,0,1]),-2,2),
                   (close,0,2)]:
 expr=sum(sp.Rational(c.numerator,c.denominator)*x**i for i,c in enumerate(coeff))
 ours=count(coeff,a,b,'[]'); official=int(sp.Poly(expr,x).count_roots(a,b))
 assert ours==official
 ours_chain=chain(coeff); official_chain=sp.sturm(expr,x)
 assert len(ours_chain)==len(official_chain)
 for z,t in zip(ours_chain,official_chain):
  zexpr=sum(sp.Rational(c.numerator,c.denominator)*x**i for i,c in enumerate(z))
  assert sp.expand(zexpr-t)==0
 cas.append(dict(polynomial=str(expr),a=a,b=b,ours=ours,sympy=official))
# exact irrational root isolation (not relying on known rational factors).
sqrt_leaves,_=isolate(poly([-2,0,1]),0,2,F(1,64))
lo,hi=sqrt_leaves[0];assert lo*lo<2<hi*hi and hi-lo<=F(1,64)
D['irrational_isolation']={'a':str(lo),'b':str(hi),'width':str(hi-lo),
                         'a_squared':str(lo*lo),'b_squared':str(hi*hi)}
assert count([7],-1,1)==0
for f in [[],[0],[0,0]]:
 try: chain(f)
 except ValueError: pass
 else: raise AssertionError('zero polynomial accepted')
for args in [(p,1,1),(p,2,-2)]:
 try: count(*args)
 except ValueError: pass
 else: raise AssertionError('invalid interval accepted')
try: poly([0.1,1])
except TypeError: pass
else: raise AssertionError('float accepted')
# Every node split preserves root counts, including midpoint roots.
for node in tree:
 children=[t for t in tree if t['parent']==node['id']]
 if children: assert sum(t['count'] for t in children)==node['count']
D['verification']={'factor_seed':2026102513,'factor_cases':cases,
                   'endpoint_comparisons':checks,'cas_cases':cas,
                   'boundary_tests':'zero/constant/reversed/equal/float and split additivity passed'}
(ROOT/'results.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'factor_comparisons':checks,'cas_cases':len(cas),
                  'main_chain':D['main']['chain'],'main_intervals':D['main']['isolation'],
                  'sqrt2':D['irrational_isolation'],'rounding':[count(close,0,2),count(rounded,0,2)]},ensure_ascii=False,indent=2))
