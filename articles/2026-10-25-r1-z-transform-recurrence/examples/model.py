"""Reproducible Z-transform teaching calculations. Code/data: CC0."""
from pathlib import Path
import json, math, platform
import numpy as np
import scipy
from scipy import signal
ROOT=Path(__file__).resolve().parent

def recurrence(x,a=.5,previous=0.,b=1.):
    out=[]
    for value in x:
        previous=a*previous+b*value
        out.append(previous)
    return np.asarray(out)

def pack(z):
    return [float(z.real),float(z.imag)]

def run():
    n=np.arange(16);x=np.zeros(16);x[:2]=[1,2]
    y=recurrence(x);h=.5**n
    terms=np.array([x[k]*np.r_[np.zeros(k),h[:len(n)-k]] for k in range(2)])
    initial=recurrence(x,previous=4);natural=4*.5**(n+1)
    unit=recurrence(np.ones(16));normal=.5*unit
    z=2*np.exp(1j*np.pi/3)
    powers=np.array([z**(-k) for k in range(5)])
    sums=[]
    for r in [1.,.5,.25]:
        terms_r=(.5/r)**np.arange(9)
        sums.append(dict(r=r,ratio=.5/r,terms=terms_r.tolist(),partial=np.cumsum(terms_r).tolist()))
    right_n=np.arange(-5,8);right=np.where(right_n>=0,.5**right_n,0)
    left=np.where(right_n<0,-.5**right_n,0)
    f=np.linspace(0,np.pi,257);response=1/(1-.5*np.exp(-1j*f))
    sine=[]
    for w in [np.pi/8,3*np.pi/4]:
        ns=np.arange(80);inp=np.cos(w*ns);out=recurrence(inp)
        H=1/(1-.5*np.exp(-1j*w));steady=np.real(H*np.exp(1j*w*ns))
        sine.append(dict(omega=float(w),n=ns.tolist(),x=inp.tolist(),y=out.tolist(),steady=steady.tolist(),gain=float(abs(H)),phase=float(np.angle(H)),post32_error=float(max(abs(out[32:]-steady[32:])))))
    cases=[]
    for a in [.5,1.,1.1]:
        cases.append(dict(a=a,impulse=(a**n).tolist(),step=recurrence(np.ones(16),a).tolist()))
    zi=signal.lfiltic([1.],[1.,-.5],[4.])
    scipy_initial,zf=signal.lfilter([1.],[1.,-.5],x,zi=zi)
    p1,state=signal.lfilter([1.],[1.,-.5],x[:4],zi=[0.])
    p2,state2=signal.lfilter([1.],[1.,-.5],x[4:],zi=state)
    reset=signal.lfilter([1.],[1.,-.5],x[4:])
    # Random tests use an independent, explicitly documented generator.
    rng=np.random.default_rng(2026102511);err=0.;conv_err=0.
    for _ in range(240):
        a=float(rng.uniform(-.95,.95));p=float(rng.normal());xx=rng.normal(size=64)
        yy=recurrence(xx,a,p);ref=signal.lfilter([1.],[1.,-a],xx,zi=[a*p])[0]
        err=max(err,float(max(abs(yy-ref))))
        direct=np.convolve(xx,a**np.arange(64))[:64]+p*a**(np.arange(64)+1)
        conv_err=max(conv_err,float(max(abs(yy-direct))))
    checks=[]
    for zz in [1.,2.,1j,.75+.5j]:
        finite=sum(y[k]*zz**(-k) for k in range(16));X=1+2/zz
        infinite=X/(1-.5/zz)
        missing= y[-1]*(.5/zz)*zz**(-15)/(1-.5/zz)
        assert abs(infinite-finite-missing)<1e-12
        # The recurrence summed only through N includes the final boundary.
        identity=X+.5/zz*finite-.5*y[-1]*zz**(-16)
        assert abs(finite-identity)<1e-12
        checks.append(dict(z=pack(complex(zz)),finite=pack(complex(finite)),infinite=pack(complex(infinite)),tail=pack(complex(missing))))
    assert np.allclose(y,terms.sum(axis=0))
    assert np.array_equal(initial,y+natural)
    assert np.array_equal(initial,scipy_initial)
    assert np.array_equal(y,np.r_[p1,p2])
    assert np.allclose(unit,2*(1-.5**(n+1)))
    assert np.allclose(normal,1-.5**(n+1))
    for zz in [.1,.2+.1j]:
        ls=sum(-(.5**(-k))*(zz**k) for k in range(1,100))
        assert abs(ls-1/(1-.5/zz))<1e-12
    data=dict(main=dict(n=n.tolist(),x=x.tolist(),y=y.tolist(),a=.5,previous=0),h=h.tolist(),convolution=terms.tolist(),initial=dict(previous=4,y=initial.tolist(),natural=natural.tolist()),step=dict(raw=unit.tolist(),normalized=normal.tolist()),complex=dict(z=pack(z),r=2.,theta=float(np.pi/3),powers=[pack(v) for v in powers]),convergence=sums,bilateral=dict(n=right_n.tolist(),right=right.tolist(),left=left.tolist(),pole=.5),stability=cases,frequency=dict(omega=f.tolist(),gain=abs(response).tolist(),phase=np.angle(response).tolist()),sine=sine,scipy=dict(zi=zi.tolist(),initial_output=scipy_initial.tolist(),final_state=zf.tolist(),split=4,first=p1.tolist(),state=state.tolist(),continued=p2.tolist(),reset=reset.tolist(),final_state2=state2.tolist()),finite=checks,tests=dict(random_seed=2026102511,random_cases=240,values_per_case=64,scipy_max_error=err,convolution_max_error=conv_err))
    (ROOT/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'reproduction.json').write_text(json.dumps(dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),indent=2)+'\n')
    print(json.dumps(data['tests']))
if __name__=='__main__':run()
