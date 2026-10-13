"""Original ideal harmonic/pulley experiments; not a tide forecast or hardware test."""
from fractions import Fraction as F
from itertools import product
import math,json,random

def height(t,terms,mean=0):
    return mean+sum(a*math.cos(w*t+p) for a,w,p in terms)

def rate(t,terms):
    return sum(-a*w*math.sin(w*t+p) for a,w,p in terms)

def output_for_offsets(offsets,z0=0):
    # offsets positive up; half-height crank motion makes full output contribution.
    return z0+sum(offsets)

def wire_length(ys,z):
    return 2*sum(ys)+z

def bisect_root(f,a,b,steps=70):
    fa,fb=f(a),f(b)
    if fa*fb>0:raise ValueError('root must be bracketed')
    if fa==0:return a
    if fb==0:return b
    for _ in range(steps):
        c=(a+b)/2;fc=f(c)
        if fc==0:return c
        if fa*fc<=0:b=c;fb=fc
        else:a=c;fa=fc
    return (a+b)/2

def check():
    toy=[(1,math.pi/6,0),(.5,math.pi/3,0)]
    table=[{'t':t,'q1':math.cos(math.pi*t/6),'q2':.5*math.cos(math.pi*t/3),'h':height(t,toy,2)} for t in [0,3,4,6,8,9,12]]
    expected=[3.5,1.5,1.25,1.5,1.25,1.5,3.5]
    assert all(abs(r['h']-e)<1e-12 for r,e in zip(table,expected))
    roots=[bisect_root(lambda t:rate(t,toy),a,b) for a,b in [(3,5),(5,7),(7,9)]]
    assert max(abs(a-b) for a,b in zip(roots,[4,6,8]))<1e-12
    for t,kind in [(4,'min'),(6,'max'),(8,'min')]:
        c=height(t,toy,2);left=height(t-.001,toy,2);right=height(t+.001,toy,2)
        assert (c<left and c<right) if kind=='min' else (c>left and c>right)
    count=0
    for values in product([F(i,4) for i in range(-4,5)],repeat=4):
        ys=[F(10)-v/2 for v in values];z=F(10)+sum(values)
        assert wire_length(ys,z)==90
        assert output_for_offsets(values,F(10))==z
        count+=1
    rng=random.Random(30);error=0;derivative_error=0;random_count=0
    for n in range(1,9):
      for k in range(400):
        terms=[(rng.uniform(0,2),rng.uniform(.1,3),rng.uniform(-math.pi,math.pi)) for _ in range(n)]
        t=rng.uniform(-10,10);qs=[a*math.cos(w*t+p) for a,w,p in terms]
        ys=[10-q/2 for q in qs];z=10+sum(qs)
        error=max(error,abs(wire_length(ys,z)-(20*n+10)))
        assert abs(output_for_offsets(qs,2)-height(t,terms,2))<1e-12
        eps=1e-5;numeric=(height(t+eps,terms)-height(t-eps,terms))/(2*eps)
        derivative_error=max(derivative_error,abs(numeric-rate(t,terms)));random_count+=1
    assert error<1e-12 and derivative_error<1e-7
    # Cosine projection equals unit-circle dot product; use independent angle composition.
    projection=0;projection_error=0
    for amplitude in [0,.25,.5,1,2]:
      for base in range(24):
       for phase in range(24):
        b=base*math.pi/12;p=phase*math.pi/12
        projected=amplitude*(math.cos(b)*math.cos(p)-math.sin(b)*math.sin(p))
        projection_error=max(projection_error,abs(projected-amplitude*math.cos(b+p)));projection+=1
    assert projection_error<1e-13
    m_deg=28.9841042;s_deg=30.0;beat_h=360/(s_deg-m_deg)
    # Complex magnitude is compared to a separate triangle formula for two phasors.
    env=0
    for aa in [0,.25,.5,1,2]:
      for bb in [0,.25,.5,1,2]:
       for k in range(145):
        delta=math.tau*k/144
        direct=abs(complex(aa,0)+bb*complex(math.cos(delta),math.sin(delta)))
        formula=math.sqrt(max(0,aa*aa+bb*bb+2*aa*bb*math.cos(delta)))
        assert abs(direct-formula)<1e-7;env+=1
    frames=[]
    for t in range(13):
        q=[a*math.cos(w*t+p) for a,w,p in toy]
        ys=[10-v/2 for v in q];z=10+sum(q)
        assert abs(wire_length(ys,z)-50)<1e-12
        frames.append({'t':t,'angles':[w*t+p for a,w,p in toy],'q':q,'pulley_y':ys,'end_z':z,'h':2+sum(q)})
    return {'hand_table':table,'stationary_roots':roots,'exact_wire_cases':count,'random_harmonic_cases':random_count,'max_wire_float_error':error,'max_central_difference_error':derivative_error,'projection_cases':projection,'max_projection_error':projection_error,'envelope_cases':env,'M2_deg_per_hour':m_deg,'S2_deg_per_hour':s_deg,'M2_period_hours':360/m_deg,'beat_hours':beat_h,'beat_days':beat_h/24,'animation_frames':frames,'limits':'Synthetic ideal geometry; no local tide constants, no weather model, no navigational use, no machine measurement.'}

if __name__=='__main__':print(json.dumps(check(),ensure_ascii=False,indent=2))
