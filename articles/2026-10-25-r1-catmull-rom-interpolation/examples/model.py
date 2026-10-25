"""Catmull–Rom CPU teaching model. Code/data CC0. Requires NumPy."""
from pathlib import Path
import json
import numpy as np
ROOT=Path(__file__).resolve().parent

def knots(p,alpha):
    p=np.asarray(p,float)
    d=np.linalg.norm(np.diff(p,axis=0),axis=1)
    if alpha!=0 and np.any(d<=0):
        raise ValueError('nonuniform knots require distinct adjacent points')
    return np.r_[0,np.cumsum(np.ones(len(d)) if alpha==0 else d**alpha)]

def segment(p,alpha=0):
    p=np.asarray(p,float);t=knots(p,alpha);h=np.diff(t)
    v=np.diff(p,axis=0)/h[:,None]
    d1=(h[1]*v[0]+h[0]*v[1])/(h[0]+h[1])
    d2=(h[2]*v[1]+h[1]*v[2])/(h[1]+h[2])
    m1=h[1]*d1;m2=h[1]*d2
    a=2*p[1]-2*p[2]+m1+m2
    b=-3*p[1]+3*p[2]-2*m1-m2
    return dict(points=p,alpha=alpha,knots=t,h=h,v=v,D=np.array([d1,d2]),m=np.array([m1,m2]),coef=np.array([a,b,m1,p[1]]),bezier=np.array([p[1],p[1]+m1/3,p[2]-m2/3,p[2]]))

def evaluate(s,u,derivative=0):
    u=np.asarray(u)[...,None];a,b,c,d=s['coef']
    if derivative==1:return (3*a*u+2*b)*u+c
    if derivative==2:return 6*a*u+2*b
    return ((a*u+b)*u+c)*u+d

def pyramid(p,alpha,u):
    p=np.asarray(p,float);t=knots(p,alpha);x=t[1]+u*(t[2]-t[1])
    def blend(a,b,i,j):return ((t[j]-x)*a+(x-t[i])*b)/(t[j]-t[i])
    A=np.array([blend(p[i],p[i+1],i,i+1) for i in range(3)])
    B=np.array([blend(A[i],A[i+1],i,i+2) for i in range(2)])
    return dict(t=x,A=A,B=B,C=blend(B[0],B[1],1,2))

def pack(p,alpha):
    s=segment(p,alpha);s['u']=np.linspace(0,1,401);s['curve']=evaluate(s,s['u']);return s

def chain(p,alpha=.5):
    p=np.asarray(p,float);ext=np.vstack([2*p[0]-p[1],p,2*p[-1]-p[-2]])
    return [pack(ext[i:i+4],alpha) for i in range(len(p)-1)]

def crossing(s):
    a,b,c,_=s['coef'];mat=np.column_stack([a,b])
    if abs(np.linalg.det(mat))<1e-10:return None
    z,total=np.linalg.solve(mat,-c);product=total*total-z
    discr=total*total-4*product
    if discr<=0:return None
    u=(total-np.sqrt(discr))/2;v=(total+np.sqrt(discr))/2
    if 0<u<v<1:return dict(u=u,v=v,point=evaluate(s,u),error=np.linalg.norm(evaluate(s,u)-evaluate(s,v)))

def serial(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    raise TypeError(type(x).__name__)

def run():
    p=np.array([[0,0],[1,2],[4,3],[6,0]],float)
    main=[pack(p,a) for a in [0,.5,1]];s=main[0]
    u=.5;basis=np.array([2*u**3-3*u*u+1,u**3-2*u*u+u,-2*u**3+3*u*u,u**3-u*u])
    terms=basis[:,None]*np.array([p[1],s['m'][0],p[2],s['m'][1]])
    rng=np.random.default_rng(20261025);loop=None;trials=0
    while loop is None:
        q=rng.integers(-10,11,size=(4,2)).astype(float);trials+=1
        if np.any(np.linalg.norm(np.diff(q,axis=0),axis=1)==0):continue
        candidate=pack(q,0);hit=crossing(candidate)
        if hit:
            va=evaluate(candidate,hit['u'],1);vb=evaluate(candidate,hit['v'],1)
            angle=np.degrees(np.arccos(np.clip(np.dot(va,vb)/np.linalg.norm(va)/np.linalg.norm(vb),-1,1)))
            size=np.ptp(evaluate(candidate,np.linspace(hit['u'],hit['v'],101)),axis=0)
        if hit and hit['v']-hit['u']>.3 and min(size)>.12 and 25<angle<155:
            loop=dict(points=q,curves=[candidate,pack(q,.5),pack(q,1)],hit=hit,seed=20261025,trials=trials,selection="integer coordinates -10..10; parameter gap>0.3, loop width and height>0.12, crossing tangent angle 25..155 degrees",loop_bounds=np.array([evaluate(candidate,np.linspace(hit['u'],hit['v'],101)).min(axis=0),evaluate(candidate,np.linspace(hit['u'],hit['v'],101)).max(axis=0)]))
    top=np.array([[0,0],[1,1],[2,1],[3,0]],float);overshoot=pack(top,.5);overshoot['peak']=evaluate(overshoot,.5)
    whole=np.array([[0,0],[1,2],[4,3],[6,0],[8,2],[10,1]],float)
    edited=whole.copy();edited[2]+=[0,1.5]
    segments=chain(whole);newsegments=chain(edited)
    joins=[]
    for i in range(len(segments)-1):
        left,right=segments[i:i+2]
        joins.append(dict(point=whole[i+1],local_left=left['m'][1],local_right=right['m'][0],global_left=left['D'][1],global_right=right['D'][0],h=[left['h'][1],right['h'][1]],second_left=evaluate(left,1,2)/left['h'][1]**2,second_right=evaluate(right,0,2)/right['h'][1]**2))
    bow=np.array([[-3,-2],[-2,-1],[2,1],[-2,1],[2,-1],[3,-2]],float);bowsegments=chain(bow)
    left,right=bowsegments[1],bowsegments[3];uv=np.array([.5,.5])
    for _ in range(12):
        delta=np.linalg.solve(np.column_stack([evaluate(left,uv[0],1),-evaluate(right,uv[1],1)]),evaluate(left,uv[0])-evaluate(right,uv[1]));uv-=delta
    globalhit=dict(u=uv,point=evaluate(left,uv[0]),error=np.linalg.norm(evaluate(left,uv[0])-evaluate(right,uv[1])))
    dense=np.linspace(0,1,4001);xy=evaluate(s,dense);arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(xy,axis=0),axis=1))]
    uniform_u=np.linspace(0,1,11);arc_u=np.interp(np.linspace(0,arc[-1],11),arc,dense)
    markers=[evaluate(s,uniform_u),evaluate(s,arc_u)];steps=[np.linalg.norm(np.diff(m,axis=0),axis=1) for m in markers]
    reverse=pack([[0,0],[1,0],[0,0],[-1,1]],.5)
    duplicate_rejected=False
    try:segment([[0,0],[0,0],[1,1],[2,0]],.5)
    except ValueError:duplicate_rejected=True
    errors=[];derivative_errors=[];bezier_errors=[]
    test_rng=np.random.default_rng(71025)
    for alpha in [0,.5,1]:
        for _ in range(60):
            q=test_rng.normal(size=(4,2));ss=segment(q,alpha)
            for x in [.0,.17,.5,.83,1.]:
                errors.append(np.linalg.norm(evaluate(ss,x)-pyramid(q,alpha,x)['C']))
                bz=ss['bezier'];bezier_errors.append(np.linalg.norm(evaluate(ss,x)-((1-x)**3*bz[0]+3*(1-x)**2*x*bz[1]+3*(1-x)*x*x*bz[2]+x**3*bz[3])))
            x=.37;e=1e-6
            derivative_errors.append(np.linalg.norm((evaluate(ss,x+e)-evaluate(ss,x-e))/(2*e)-evaluate(ss,x,1)))
            assert np.allclose(evaluate(ss,0),q[1]) and np.allclose(evaluate(ss,1),q[2])
    tests=dict(independent_seed=71025,segments=180,evaluations=900,max_pyramid_error=max(errors),max_bezier_error=max(bezier_errors),max_derivative_error=max(derivative_errors),max_join_error=max(np.linalg.norm(j['global_left']-j['global_right']) for j in joins),duplicate_rejected=duplicate_rejected,reverse_endpoint_speed=np.linalg.norm(reverse['D'][0]))
    assert tests['max_pyramid_error']<1e-10 and tests['max_bezier_error']<1e-10 and tests['max_derivative_error']<1e-7
    assert tests['max_join_error']<1e-12 and duplicate_rejected and tests['reverse_endpoint_speed']==0
    assert loop['hit']['error']<1e-10 and globalhit['error']<1e-10 and np.all((uv>0)&(uv<1))
    assert np.allclose(segments[-1]['curve'],newsegments[-1]['curve'])
    assert abs(evaluate(overshoot,.5,1)[1])<1e-12 and evaluate(overshoot,.5,2)[1]<0
    assert np.allclose(evaluate(s,.5),[2.4375,2.8125]) and overshoot['peak'][1]>1
    result=dict(main=main,hand=dict(u=u,basis=basis,terms=terms,value=terms.sum(axis=0),samples_u=np.linspace(0,1,5),samples=evaluate(s,np.linspace(0,1,5))),pyramid=pyramid(p,0,.5),loop=loop,overshoot=overshoot,whole=dict(points=whole,edited=edited,segments=segments,newsegments=newsegments,joins=joins),global_cross=dict(points=bow,segments=bowsegments,hit=globalhit),speed=dict(uniform_u=uniform_u,arc_u=arc_u,markers=markers,steps=steps,arc_approx=arc[-1],dense_samples=len(dense)),reverse=reverse,tests=tests)
    (ROOT/'results.json').write_text(json.dumps(result,default=serial,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(hand=result['hand']['value'],loop_points=loop['points'],loop_hit=loop['hit'],global_hit=globalhit,overshoot=overshoot['peak'],tests=tests),default=serial,indent=2))
if __name__=='__main__':run()
