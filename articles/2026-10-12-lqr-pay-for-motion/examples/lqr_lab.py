#!/usr/bin/env python3
"""Original scalar discrete-time finite-horizon LQR lab, CC BY 4.0.
Python standard library only. Exact Fraction arithmetic; no real actuator tests.
x[k+1] = a*x[k] + b*u[k]. J=sum(q*x[k]**2+r*u[k]**2)+qf*x[N]**2.
Inputs unbounded unless explicitly clipping an illustrative counterexample.
"""
from fractions import Fraction as F
from itertools import product
import json,random,sys

def solve(horizon,a=1,b=1,q=1,r=1,qf=1):
    if not isinstance(horizon,int) or horizon<0:raise ValueError('nonnegative integer horizon required')
    a,b,q,r,qf=map(F,(a,b,q,r,qf))
    if q<0 or qf<0 or r<=0:raise ValueError('q,qf>=0 and r>0 required')
    p=[F(0)]*(horizon+1);g=[F(0)]*horizon;p[-1]=qf
    for k in range(horizon-1,-1,-1):
        den=r+b*b*p[k+1]
        g[k]=b*p[k+1]*a/den
        p[k]=q+a*a*r*p[k+1]/den
    return p,g

def rollout(x0,g,a=1,b=1,q=1,r=1,qf=1, disturbances=None,clip=None):
    a,b,q,r,qf=map(F,(a,b,q,r,qf));x=[F(x0)];u=[];j=F(0)
    disturbances={} if disturbances is None else disturbances
    for k,gain in enumerate(g):
        uk=-gain*x[-1]
        if clip is not None:uk=max(-F(clip),min(F(clip),uk))
        j+=q*x[-1]**2+r*uk**2;u.append(uk)
        x.append(a*x[-1]+b*uk+F(disturbances.get(k,0)))
    j+=qf*x[-1]**2
    return {'x':x,'u':u,'cost':j}

def sequence_cost(x0,controls,a=1,b=1,q=1,r=1,qf=1):
    x=F(x0);j=F(0);a,b,q,r,qf=map(F,(a,b,q,r,qf))
    for u in controls:
        u=F(u);j+=q*x*x+r*u*u;x=a*x+b*u
    return j+qf*x*x

def linear_solve(m,v):
    """Exact dense Gaussian elimination; independent batch objective oracle."""
    n=len(v);c=[[F(x) for x in row]+[F(v[i])] for i,row in enumerate(m)]
    for k in range(n):
        pivot=next(i for i in range(k,n) if c[i][k])
        c[k],c[pivot]=c[pivot],c[k];z=c[k][k];c[k]=[x/z for x in c[k]]
        for i in range(n):
            if i!=k:
                z=c[i][k];c[i]=[x-z*y for x,y in zip(c[i],c[k])]
    return [row[-1] for row in c]

def batch_solution(n,x0,a,b,q,r,qf):
    """Build all states x_i=c_i+row_i*U, then solve H U=-h."""
    a,b,q,r,qf,x0=map(F,(a,b,q,r,qf,x0))
    hess=[[F(0) for _ in range(n)] for _ in range(n)];linear=[F(0)]*n
    for i in range(n):hess[i][i]=r
    for k in range(1,n+1):
        row=[b*a**(k-1-j) if j<k else F(0) for j in range(n)]
        weight=q if k<n else qf;c=a**k*x0
        for i in range(n):
            linear[i]+=weight*c*row[i]
            for j in range(n):hess[i][j]+=weight*row[i]*row[j]
    return linear_solve(hess,[-x for x in linear])

def encode(v):
    if isinstance(v,F):return str(v)
    if isinstance(v,dict):return {k:encode(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)):return [encode(x) for x in v]
    return v

def checks():
    p,g=solve(2);main=rollout(4,g)
    assert p==[F(8,5),F(3,2),F(1)] and g==[F(3,5),F(1,2)]
    assert main=={'x':[F(4),F(8,5),F(4,5)],'u':[F(-12,5),F(-4,5)],'cost':F(128,5)}
    # Diverse finite horizons and dynamics, including uncontrollable b=0.
    ncases=0
    for n,a,b,q,r,qf in product(range(1,6),[-2,0,1,2],[0,F(1,2),1],[0,1,3],[F(1,2),1,4],[0,1,5]):
        p,g=solve(n,a,b,q,r,qf);out=rollout(F(3,2),g,a,b,q,r,qf)
        batch=batch_solution(n,F(3,2),a,b,q,r,qf)
        assert out['u']==batch and out['cost']==p[0]*F(3,2)**2
        assert all(x>=0 for x in p)
        ncases+=1
    # Exact square-completion identity for arbitrary, non-optimal sequences.
    rng=random.Random(196001);identity=0
    for _ in range(3000):
        n=rng.randrange(1,8);a=F(rng.randrange(-4,5),2);b=F(rng.randrange(-4,5),2)
        q=F(rng.randrange(4));r=F(rng.randrange(1,6));qf=F(rng.randrange(4));x=F(rng.randrange(-8,9),2)
        p,g=solve(n,a,b,q,r,qf);u=[F(rng.randrange(-8,9),2) for _ in range(n)];cost=sequence_cost(x,u,a,b,q,r,qf);base=p[0]*x*x;excess=F(0)
        for k,uk in enumerate(u):
            excess+=(r+b*b*p[k+1])*(uk+g[k]*x)**2;x=a*x+b*uk
        assert cost-base==excess and excess>=0;identity+=1
    # Deliberately held-out command grid includes the exact main optimum.
    grid=[F(i,5) for i in range(-25,6)];best=min((sequence_cost(4,[u,v]),u,v) for u,v in product(grid,repeat=2));assert best==(F(128,5),F(-12,5),F(-4,5))
    variants={}
    for r in [F(1,4),F(1),F(4)]:
        p,g=solve(2,r=r);variants[str(r)]={'p':p,'gain':g,**rollout(4,g,r=r)}
    long={}
    for r in [F(1,4),F(1),F(4)]:
        p,g=solve(12,r=r);long[str(r)]={'gain':g,**rollout(4,g,r=r)}
    p,g=solve(2);closed=rollout(4,g,disturbances={0:1});planned=rollout(4,g)
    # Replay precomputed controls after the same +1 disturbance.
    xo=[F(4)];j=F(0)
    for k,u in enumerate(planned['u']):j+=xo[-1]**2+u*u;xo.append(xo[-1]+u+(1 if k==0 else 0))
    j+=xo[-1]**2
    assert closed['x']==[F(4),F(13,5),F(13,10)] and closed['cost']==F(319,10) and j==F(162,5)
    # Merely increasing r does not impose a hard input cap.
    _,wide_gain=solve(2,r=4);wide=rollout(40,wide_gain,r=4);assert abs(wide['u'][0])>1
    clipped=rollout(4,g,clip=1);assert clipped['x']==[F(4),F(3),F(2)]
    # Finite optimality is not a general stability claim when no state is priced.
    _,no_state=solve(5,a=2,q=0,qf=0);unstable=rollout(1,no_state,a=2,q=0,qf=0);assert unstable['x'][-1]==32 and unstable['cost']==0
    # Common positive rescaling leaves gains exactly unchanged.
    scaled=0
    for c in [F(1,100),F(1,3),F(1),F(7),F(100)]:
        pp,gg=solve(9,q=c,r=c,qf=c);basep,baseg=solve(9);assert gg==baseg and pp==[c*x for x in basep];scaled+=1
    return {'status':'PASS_EXACT_MODEL_ONLY','seed':196001,'main':{'p':solve(2)[0],'gain':solve(2)[1],**main},'batch_oracle_cases':ncases,'completion_of_squares_cases':identity,'two_step_command_grid_cases':len(grid)**2,'grid_minimum':best,'weight_variants':variants,'long_horizon_variants':long,'disturbance':{'feedback':closed,'fixed_planned_controls':{'x':xo,'u':planned['u'],'cost':j}},'large_r_not_hard_cap':wide,'clipped_demo':clipped,'finite_optimum_unstable_counterexample':unstable,'common_weight_rescalings':scaled,'environment':'Python standard library Fraction; no physical device or measured energy'}

if __name__=='__main__':
    result=encode(checks());print(json.dumps(result,ensure_ascii=False,indent=2))
