"""Original saturation experiments. Code/data CC0; not a physical plant test."""
from pathlib import Path
import json, math, platform
import numpy as np
ROOT=Path(__file__).resolve().parent

def simulate(mode='none',dt=.1,Tt=1.,Kd=0.,end=60.,high=1.5,drop=20.,limits=(0.,1.),low=.4):
    Kp,Ki,tau,Tf=2.,.5,5.,.5
    y=I=d=previous_y=0.
    out={k:[] for k in ['t','r','y','e','P','I','D','v','u','integral_rate','tracking_rate','I_next','blocked']}
    for n in range(round(end/dt)+1):
        t=n*dt;r=high if t<drop else low;e=r-y;P=Kp*e
        # Backward-Euler filtered derivative of measurement (not error).
        d=Tf/(Tf+dt)*d+(y-previous_y)/(Tf+dt)
        D=-Kd*d;v=P+I+D;u=min(limits[1],max(limits[0],v));base=Ki*e
        blocked=(v>=limits[1] and base>0) or (v<=limits[0] and base<0)
        rate=0. if mode=='conditional' and blocked else base
        track=(u-v)/Tt if mode=='backcalc' else 0.
        nextI=I+dt*(rate+track)
        for key,val in zip(out,[t,r,y,e,P,I,D,v,u,rate,track,nextI,bool(blocked and mode=='conditional')]):out[key].append(val)
        previous_y=y;y=u+(y-u)*math.exp(-dt/tau);I=nextI
    return out

def metrics(d):
    t=np.array(d['t']);y=np.array(d['y']);u=np.array(d['u']);ix=np.flatnonzero(t>=20)
    released=next((float(t[k]) for k in ix if u[k]<1.-1e-12),None)
    band=np.abs(y-.4)<=.02
    settle=next((float(t[k]) for k in ix if np.all(band[k:])),None)
    return dict(at_drop={k:d[k][ix[0]] for k in ['t','y','e','P','I','D','v','u','I_next','integral_rate','tracking_rate']},release= released,settle_02=settle,iae_after_drop=float(np.sum(abs(y[ix][:-1]-.4))*(t[1]-t[0])),final_y=float(y[-1]))

def run():
    main={m:simulate(m) for m in ['none','conditional','backcalc']}
    sensitivity={str(T):simulate('backcalc',Tt=T) for T in [.2,1.,5.]}
    pid={m:simulate(m,Kd=.5) for m in main}
    hand={m:{k:v[:3] for k,v in d.items()} for m,d in main.items()}
    directions=[]
    for v,base in [(1.2,.2),(1.2,-.2),(-.2,-.2),(-.2,.2)]:
        stop=(v>=1 and base>0) or (v<=0 and base<0)
        directions.append(dict(v=v,integral_rate=base,blocked=stop,increment=0 if stop else .1*base))
    # Freeze P/e and impose external tracking input u=1: isolated scalar subsystem, not clip(I) feedback.
    stiff=[]
    for T in [.2,.1,.04]:
        I=2.;vals=[]
        for n in range(9):vals.append(I);I+=(.1/T)*(1-I)
        exact=[1+math.exp(-n*.1/T) for n in range(9)]
        stiff.append(dict(Tt=T,dt=.1,factor=1-.1/T,I=vals,continuous=exact))
    derivative=dict(dt=.1,Kd=.5,dr=-1.1,dy=0.,error_kick=.5*(-1.1)/.1,measurement_kick=0.)
    feedforward=dict(vpid=.7,uff=.6,total=1.3,actual=1.,correct_tracking=1.-.6,correct_difference=(1.-.6)-.7,wrong_difference=1.-.7)
    transfer=dict(manual=.6,r=.4,y=.3,Kp=2.,D=0.,P=2*(.4-.3),I_match=.6-2*(.4-.3),v_zero=2*(.4-.3))
    # Scalar independent analytic identity for open-loop constant held command.
    t=np.arange(201)*.1;openloop=1-np.exp(-t/5)
    assert np.max(abs(np.array(main['none']['y'][:201])-openloop))<1e-12
    # Recompute integral states by cumulative recorded rates independently.
    maxI=0.
    for d in [*main.values(),*sensitivity.values(),*pid.values()]:
        assert min(d['u'])>=0 and max(d['u'])<=1
        rate=np.array(d['integral_rate'])+np.array(d['tracking_rate'])
        ref=np.r_[0,.1*np.cumsum(rate[:-1])];maxI=max(maxI,float(max(abs(ref-d['I']))))
        assert np.max(abs(ref-d['I']))<1e-11
        assert all(abs(v-(p+i+de))<1e-12 for v,p,i,de in zip(d['v'],d['P'],d['I'],d['D']))
    # All modes exactly reduce to identical discrete PI while never saturated.
    free=[simulate(m,high=.2,drop=100,end=10) for m in main]
    # Some initial demand may saturate? .2 gives v=.4 and remains interior.
    assert all(all(0<u<1 for u in d['u']) for d in free)
    for d in free[1:]:assert np.array_equal(d['y'],free[0]['y']) and np.array_equal(d['I'],free[0]['I'])
    mirrored={m:simulate(m,high=-1.5,low=-.4,limits=(-1.,0.)) for m in main}
    for m,d in mirrored.items():
        assert min(d['u'])>=-1 and max(d['u'])<=0
        for key in ['y','I','v','u']:assert np.allclose(d[key],-np.array(main[m][key]))
    data=dict(parameters=dict(dt=.1,tau=5.,Kp=2.,Ki=.5,Kd=0.,Tt=1.,Tf=.5,limits=[0.,1.],high=1.5,low=.4,drop=20.,end=60.),main=main,metrics={m:metrics(d) for m,d in main.items()},hand=hand,sensitivity=sensitivity,pid=pid,pid_metrics={m:metrics(d) for m,d in pid.items()},directions=directions,stiff=stiff,derivative=derivative,feedforward=feedforward,transfer=transfer,saturation=dict(v=np.linspace(-1,2,61).tolist(),u=np.clip(np.linspace(-1,2,61),0,1).tolist()),tests=dict(state_cumsum_error=maxI,openloop_exact_error=float(max(abs(np.array(main['none']['y'][:201])-openloop))),sample_count=len(main['none']['t']),unsaturated_modes_equal=True,lower_limit_cases_pass=True))
    (ROOT/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'reproduction.json').write_text(json.dumps(dict(python=platform.python_version(),numpy=np.__version__),indent=2)+'\n')
    print(json.dumps(data['metrics'],ensure_ascii=False))
if __name__=='__main__':run()
