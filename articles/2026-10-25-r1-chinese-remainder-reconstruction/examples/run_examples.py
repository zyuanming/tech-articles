"""Generate all numerical material and execute independent CRT checks. CC0."""
from pathlib import Path
from math import gcd, lcm, prod
from itertools import product
import json, random, platform
import sympy
from sympy.ntheory.modular import solve_congruence
from crt_exact import egcd, inverse, coprime_basis, reconstruct, merge, solve, centered

ROOT=Path(__file__).resolve().parent
ms=[3,5,7]; rs=[2,3,2]; M,es=coprime_basis(ms)
x,_=reconstruct(rs,ms)
all_rows=[{'x':v,'residues':[v%m for m in ms]} for v in range(M)]
filters=[[v for v in range(M) if all(v%ms[j]==rs[j] for j in range(i+1))] for i in range(3)]
basis=[]
for m,r,e in zip(ms,rs,es):
 q=M//m;inv=inverse(q,m)
 basis.append({'m':m,'r':r,'q':q,'q_residue':q%m,'inverse':inv,'e':e,'residues':[e%n for n in ms],'weighted':r*e,'weighted_residues':[(r*e)%n for n in ms]})
trace=[];a,mod=rs[0],ms[0]
for b,n in zip(rs[1:],ms[1:]):
 g=gcd(mod,n);t=((b-a)//g*inverse(mod//g,n//g))%(n//g)
 out=merge(a,mod,b,n);trace.append({'a':a,'m':mod,'b':b,'n':n,'g':g,'delta':b-a,'t':t,'x':out[0],'L':out[1]});a,mod=out
non=[]
for b in [6,3]:
 out=merge(2,6,b,8)
 non.append({'a':2,'m':6,'b':b,'n':8,'g':gcd(6,8),'result':out,'row1':[v for v in range(24) if v%6==2],'row2':[v for v in range(24) if v%8==b],'matches':[v for v in range(24) if v%6==2 and v%8==b]})
calc_ms=[5,7,11];A,B,C=7,9,80
channels=[{'m':m,'a':A%m,'b':B%m,'c':C%m,'raw':(A%m)*(B%m)-(C%m),'r':(A*B-C)%m} for m in calc_ms]
calc_x,calc_M=reconstruct([p['r'] for p in channels],calc_ms)
wrong_rs=rs.copy();wrong_rs[1]+=1;wrong_x,_=reconstruct(wrong_rs,ms)
# Exhaustive independent enumeration, not using CRT to establish the answer.
exhaustive=0;has_solution=0
for m in range(1,13):
 for n in range(1,13):
  for a in range(m):
   for b in range(n):
    L=lcm(m,n);expected=[v for v in range(L) if v%m==a and v%n==b]
    actual=merge(a,m,b,n)
    assert actual == ((expected[0],L) if expected else None)
    assert len(expected)<=1
    exhaustive+=1;has_solution+=bool(expected)
rng=random.Random(2026102514);cas_checks=0
for _ in range(1200):
 n=rng.randrange(1,6)
 pairs=[(rng.randrange(-500,501),rng.randrange(2,41)) for _ in range(n)]
 actual=solve(pairs);ref=solve_congruence(*pairs)
 expected=None if ref is None else tuple(map(int,ref))
 assert actual==expected,(pairs,actual,expected)
 cas_checks+=1
# All 105 combinations uniquely mapped; compare basis, merge and brute-force table.
for residues in product(*[range(m) for m in ms]):
 a,P=reconstruct(residues,ms);assert solve(zip(residues,ms))==(a,P)
 assert [v for v in range(P) if [v%m for m in ms]==list(residues)]==[a]
assert len({tuple(row['residues']) for row in all_rows})==M
signed_checks=0
for value in range(-100,101):
 raw,P=reconstruct([value%m for m in calc_ms],calc_ms)
 assert centered(raw,P)==value;signed_checks+=1
assert egcd(35,3)==(1,-1,12)
assert inverse(35,3)==2
assert solve([(5,1),(-7,8)])==(1,8)
assert solve([(1,4),(5,8)])==(5,8)
assert solve([(1,4),(2,4)]) is None
errors=0
for fn,args,kind in [(inverse,(2,6),ValueError),(inverse,(0,1),ValueError),(solve,([],),ValueError),(merge,(0,0,1,2),ValueError),(merge,(1,2,0,-3),ValueError),(merge,(1.0,2,1,3),TypeError),(merge,(True,2,1,3),TypeError),(reconstruct,([1],[2,3]),ValueError),(reconstruct,([1,2],[4,6]),ValueError),(reconstruct,([],[]),ValueError)]:
 try:fn(*args)
 except kind:errors+=1
 else:raise AssertionError((fn.__name__,args))
# An inconsistent valid prefix must not hide an invalid later condition.
prefix = [(0, 2), (1, 2)]
suffix_checks = []
for label, suffix, kind in [
 ('short-pair', (1,), ValueError),
 ('long-pair', (1, 3, 5), ValueError),
 ('noniterable-pair', 5, ValueError),
 ('float-residue', (1.0, 3), TypeError),
 ('bool-residue', (True, 3), TypeError),
 ('float-modulus', (1, 3.0), TypeError),
 ('bool-modulus', (1, True), TypeError),
 ('zero-modulus', (1, 0), ValueError),
 ('negative-modulus', (1, -3), ValueError),
]:
 try:solve(prefix + [suffix])
 except kind:
  errors += 1
  suffix_checks.append({'case': label, 'exception': kind.__name__})
 else:raise AssertionError(('invalid suffix was ignored', label))
assert solve(prefix + [(1, 3)]) is None
assert centered(3,6)==3 and centered(4,6)==-2
assert reconstruct([1,2],[4,9])==(29,36)
assert coprime_basis([4,9])==(36,[9,28])
D={'exercise':{'moduli':[4,9],'residues':[1,2],'basis':[9,28],'sum':65,'x':29,'M':36},'versions':{'python':platform.python_version(),'sympy':sympy.__version__},'main':{'moduli':ms,'residues':rs,'M':M,'x':x,'division':[{'m':m,'q':x//m,'r':x%m} for m in ms],'filters':filters,'basis':basis,'sum':sum(r*e for r,e in zip(rs,es)),'all_rows':all_rows,'trace':trace,'period_points':[x+k*M for k in range(-1,3)],'multiplication_map':[(k,2*k%3) for k in range(3)],'egcd':[1,-1,12]},'signed':{'value':-17,'x':-17%M,'M':M,'lo':-(M//2),'hi':M//2,'same_residues':[(-17)%m for m in ms]},'noncoprime':non,'calculation':{'A':A,'B':B,'C':C,'value':A*B-C,'moduli':calc_ms,'channels':channels,'M':calc_M,'raw':calc_x,'centered':centered(calc_x,calc_M),'B_bound':100,'input_range':{'A':[0,10],'B':[0,10],'C':[0,100]},'ambiguous_pair':[-17,88],'alias_pair':[75,centered(75,M)]},'error':{'correct':rs,'wrong':wrong_rs,'x':x,'wrong_x':wrong_x,'difference':wrong_x-x,'basis_shift':es[1]},'overflow':{'a':200,'b':200,'modulus':251,'true_product':40000,'correct':40000%251,'wrapped8':40000%256,'bad':(40000%256)%251},'verification':{'exhaustive_pairs':exhaustive,'solvable_pairs':has_solution,'cas_checks':cas_checks,'seed':2026102514,'bijection':M,'signed_range_checks':signed_checks,'rejected_inputs':errors,'invalid_suffix_checks':suffix_checks}}
(ROOT/'results.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(D['verification']))
