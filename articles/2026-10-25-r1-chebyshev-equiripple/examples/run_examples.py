"""Exact certificates and a bounded exchange example. Original code/data CC0."""
from pathlib import Path
import json, math, platform
import numpy as np
import sympy as s
x=s.symbols('x'); f=x**4; p=x*x-s.Rational(1,8); e=s.expand(f-p)
T=[s.Integer(1),x]
for n in range(1,12):T.append(s.expand(2*x*T[-1]-T[-2]))
assert all(s.expand(t-s.chebyshevt(n,x))==0 for n,t in enumerate(T))
assert e==T[4]/8
nodes=[-s.Integer(1),-s.sqrt(2)/2,s.Integer(0),s.sqrt(2)/2,s.Integer(1)]
peaks=[s.simplify(e.subs(x,z)) for z in nodes]
assert peaks==[s.Rational(1,8)*(-1)**i for i in range(5)]
assert s.factor(s.diff(e,x))==2*x*(2*x*x-1)
# Establish the complete range algebraically: e=(x²−1/2)²−1/8.
assert s.expand(e-((x*x-s.Rational(1,2))**2-s.Rational(1,8)))==0
# Exact extrema of both residual polynomials on the closed interval.
e0=s.expand(f-x*x)
e0crit=[s.Integer(-1),s.Integer(1)]+s.solve(s.diff(e0,x),x)
ecrit=[s.Integer(-1),s.Integer(1)]+s.solve(s.diff(e,x),x)
assert all(z.is_real and -1<=z<=1 for z in e0crit+ecrit)
old_E=max(abs(e0.subs(x,z)) for z in e0crit)
main_E=max(abs(e.subs(x,z)) for z in ecrit)
assert old_E==s.Rational(1,4) and main_E==s.Rational(1,8)
coarse_x=[-1,-.5,0,.5,1]
coarse_e0=[float(e0.subs(x,z)) for z in coarse_x]
coarse_max=max(abs(v) for v in coarse_e0)
# Continuous, unweighted least squares: normal equations on [-1,1].
a,b=s.symbols('a b'); normal=[s.integrate((f-a*x*x-b)*v,(x,-1,1)) for v in [1,x*x]]
sol=s.solve(normal,[a,b]);ls=s.expand(sol[a]*x*x+sol[b]);lse=f-ls
crit=[-1,1]+s.solve(s.diff(lse,x),x)
lsmax=max(abs(lse.subs(x,z)) for z in crit)
mse=lambda q:s.integrate((f-q)**2,(x,-1,1))/2
# Actual numerical exchange for this quartic only; all derivative roots available.
ref=np.array([-1.,-.5,0,.5,1.]); trace=[]
xx=np.linspace(-1,1,801)
for k in range(3):
 A=np.column_stack([ref**j for j in range(4)]+[(-1.)**np.arange(5)])
 coef=np.linalg.solve(A,ref**4);a0,a1,a2,a3,E=coef
 roots=np.roots([4,-3*a3,-2*a2,-a1])
 extrema=np.array(sorted([-1.,1.]+[float(r.real) for r in roots if abs(r.imag)<1e-12 and -1<r.real<1]))
 residual=lambda z:z**4-np.polynomial.polynomial.polyval(z,coef[:4])
 vals=residual(extrema)
 trace.append(dict(round=k,reference=ref.tolist(),coefficients=coef[:4].tolist(),E=float(E),extrema=extrema.tolist(),values=vals.tolist(),max_error=float(max(abs(vals))),curve=residual(xx).tolist()))
 assert len(extrema)==5 and all(vals[i]*vals[i+1]<0 for i in range(4))
 ref=extrema
assert np.max(np.abs(np.array(trace[-1]['coefficients'])-[-.125,0,1,0]))<1e-12
assert abs(trace[-1]['max_error']-.125)<1e-12
# Truncation counterexample, new function and new degree budget.
g=s.expand(T[2]+T[4]);gcrit=[-1,1]+s.solve(s.diff(g,x),x)
gmin=min(g.subs(x,z) for z in gcrit);gmax=max(g.subs(x,z) for z in gcrit)
gc=(gmin+gmax)/2;gE=(gmax-gmin)/2
graw=max(abs(gmin),abs(gmax))
assert graw.is_Integer
assert (gmin,gmax,gc,gE)==(-s.Rational(9,8),2,s.Rational(7,16),s.Rational(25,16))
sample_x=s.Rational(1,2)
exercise_shift=s.Rational(1,100)
flt=lambda a:float(a)
curve=lambda q:[float(q.subs(x,float(z))) for z in xx]
D={'versions':{'python':platform.python_version(),'numpy':np.__version__,'sympy':s.__version__},'domain':[-1,1],'degree_budget':3,'grid':xx.tolist(),'curves':{'f':curve(f),'p0':curve(x*x),'p':curve(p),'e0':curve(f-x*x),'e':curve(e),'T4':curve(T[4]),'ls_error':curve(lse),'g':curve(g),'g_centered':curve(g-gc)},'main':{'p':str(p),'error':str(e),'E':float(main_E),'old_E':float(old_E),'nodes':[float(z) for z in nodes],'node_exact':[str(z) for z in nodes],'peaks':list(map(float,peaks)),'sample':{'x':float(sample_x),'f':float(f.subs(x,sample_x)),'p':float(p.subs(x,sample_x)),'error':float(e.subs(x,sample_x))},'T_polynomials':[str(z) for z in T[:5]],'T_at_half':[float(z.subs(x,s.Rational(1,2))) for z in T[:5]]},'least_squares':{'polynomial':str(ls),'max_error':float(lsmax),'max_exact':str(lsmax),'mse':float(mse(ls)),'mse_exact':str(mse(ls)),'minimax_mse':float(mse(p)),'minimax_mse_exact':str(mse(p))},'exchange':trace,'cosine':{'theta':[i*math.pi/4 for i in range(5)],'x':[math.cos(i*math.pi/4) for i in range(5)],'T4':[math.cos(i*math.pi) for i in range(5)]},'coarse':{'x':coarse_x,'e0':coarse_e0,'sample_max':coarse_max,'true_max':float(old_E)},'outside':{'x':[1,1.25,1.5],'e':[float(e.subs(x,z)) for z in [1,1.25,1.5]],'grid':np.linspace(-1.5,1.5,601).tolist(),'curve':[float(e.subs(x,z)) for z in np.linspace(-1.5,1.5,601)]},'truncation':{'g':str(g),'min':float(gmin),'max':float(gmax),'constant':float(gc),'error':float(gE),'raw_error':int(graw),'extrema':[float(z) for z in sorted(gcrit)]},'verification':{'exact_recurrences':len(T),'alternating_extrema':len(nodes),'exchange_rounds':len(trace),'grid_points':len(xx),'grid_is_proof':False,'symbolic_identity':True,'no_randomness':True}}
D['main']['sample']['p0']=float((x*x).subs(x,sample_x))
D['main']['sample']['error0']=float(e0.subs(x,sample_x))
D['exercise']={'shift':float(exercise_shift),'positive_peak':float(main_E-exercise_shift),'negative_peak':float(-main_E-exercise_shift)}
D['mapping']={'interval':[2,6],'input':5,'mapped_x':(2*5-2-6)/(6-2)}
Path(__file__).with_name('results.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:D[k] for k in ['versions','least_squares','verification']},ensure_ascii=False))
for t in trace:print('round',t['round'],'E',t['E'],'actual max',t['max_error'])
