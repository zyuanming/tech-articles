"""Original ideal wheel-and-disc teaching calculations; no hardware tests."""
from fractions import Fraction as F
from itertools import product
from math import exp,cos,sin,pi
import json

def segmented(offsets,angles,wheel_radius):
    if wheel_radius<=0:raise ValueError('positive wheel radius required')
    return sum((r*t/wheel_radius for r,t in zip(offsets,angles)),F(0))

def euler(a,y0,end,n):
    h=end/n;y=y0
    for _ in range(n):y+=h*a*y
    return y

def rk4(a,y0,end,n):
    h=end/n;y=y0
    for _ in range(n):
        k1=a*y;k2=a*(y+h*k1/2);k3=a*(y+h*k2/2);k4=a*(y+h*k3)
        y+=h*(k1+2*k2+2*k3+k4)/6
    return y

def oscillator(u0,v0,end,n):
    h=end/n;u,v=u0,v0
    for _ in range(n):
        k1=(v,-u);k2=(v+h*k1[1]/2,-u-h*k1[0]/2)
        k3=(v+h*k2[1]/2,-u-h*k2[0]/2);k4=(v+h*k3[1],-u-h*k3[0])
        u+=h*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6
        v+=h*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6
    return u,v

def run():
    exact=0
    for offsets in product([F(i,2) for i in range(-3,4)],repeat=3):
        for rw in [F(1,2),F(1),F(2)]:
            for scale in [F(1,4),F(1,2),F(1),F(2)]:
                angles=[scale,2*scale,scale];got=segmented(offsets,angles,rw)
                assert got==scale*(offsets[0]+2*offsets[1]+offsets[2])/rw
                splitr=[r for r in offsets for _ in [0,1]];splitt=[t/2 for t in angles for _ in [0,1]]
                assert segmented(splitr,splitt,rw)==got
                assert segmented(offsets,[-t for t in angles],rw)==-got
                exact+=1
    ramp=0
    for end in [F(i,4) for i in range(1,13)]:
        for n in [1,2,3,5,10,20,40]:
            h=end/n;got=sum(((k*h+(k+1)*h)/2*h for k in range(n)),F(0))
            assert got==end*end/2;ramp+=1
    convergence=[]
    for n in [10,20,40,80]:
        y=euler(1,.5,1,n);z=rk4(1,.5,1,n);convergence.append(dict(n=n,euler=y,rk4=z,exact=.5*exp(1),euler_error=y-.5*exp(1),rk4_error=z-.5*exp(1)))
    trials=0;maxerr=0
    for a in [i/4 for i in range(-8,9)]:
        for y0 in [i/4 for i in range(-3,4)]:
            for end in [.25,.5,1]:
                got=rk4(a,y0,end,200);err=abs(got-y0*exp(a*end));maxerr=max(maxerr,err)
                assert err<1e-8;trials+=1
    osc=0;omax=0
    for u0 in [i/3 for i in range(-3,4)]:
        for v0 in [i/3 for i in range(-3,4)]:
            u,v=oscillator(u0,v0,2*pi,1000)
            err=max(abs(u-(u0*cos(2*pi)+v0*sin(2*pi))),abs(v-(-u0*sin(2*pi)+v0*cos(2*pi))))
            assert err<1e-9;omax=max(omax,err);osc+=1
    frames=[]
    for k in range(9):
        x=k/8;y=.5*exp(x)
        frames.append(dict(x=x,y=y,disc_angle=x,output_angle=y-.5,offset=y))
    # Physical scale consistency: theta=alpha*x, phi=beta*y, rho=gamma*y.
    scales=0
    for alpha,beta,rw,a in product([F(1,2),F(1),F(2)],[F(1),F(2),F(4)],[F(1,2),F(1),F(2)],[-2,-1,0,1,2]):
        gamma=F(a)*beta*rw/alpha
        assert alpha*gamma/(beta*rw)==a;scales+=1
    return dict(model='ideal rho*dtheta=rw*dphi; normalized feedback yprime=a*y',piecewise_exact_cases=exact,ramp_exact_cases=ramp,convergence=convergence,rk4_analytic_cases=trials,max_rk4_error=maxerr,oscillator_cases=osc,max_oscillator_error=omax,scale_identities=scales,animation_frames=frames,main_piecewise=dict(offsets=[2,0,-1],disc_angles=[.5,1,.5],wheel_radius=1,total=.5),limitations='No real disc friction, torque, transient dynamics or machinery measured. RK4/Euler only approximate ideal equations; they are not the operations of an analog machine.')
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
