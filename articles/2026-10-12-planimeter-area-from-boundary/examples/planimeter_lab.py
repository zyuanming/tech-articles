"""Original ideal midpoint-wheel model; no physical instrument measurements."""
from math import hypot,sqrt,pi,cos,sin
from fractions import Fraction
import json

def joint(p,R=5.0,L=3.0):
    x,y=p; d=hypot(x,y)
    if not abs(R-L)<d<R+L:raise ValueError('outside nonsingular reachable annulus')
    a=(R*R-L*L+d*d)/(2*d); h=sqrt(R*R-a*a)
    return ((a*x-h*y)/d,(a*y+h*x)/d)

def pose(p,R=5.0,L=3.0):
    q=joint(p,R,L); m=((p[0]+q[0])/2,(p[1]+q[1])/2)
    e=((p[0]-q[0])/L,(p[1]-q[1])/L)
    return q,m,(-e[1],e[0])

def wheel(path,N,R=5.0,L=3.0):
    # Mid-time wheel normal dotted with displacement of its center.
    total=0.0
    for k in range(N):
        _,m0,_=pose(path(k/N),R,L); _,m1,_=pose(path((k+1)/N),R,L)
        _,_,n=pose(path((k+.5)/N),R,L)
        total+=n[0]*(m1[0]-m0[0])+n[1]*(m1[1]-m0[1])
    return total

def circle(cx,cy,r,reverse=False):
    return lambda t:(cx+r*cos((-1 if reverse else 1)*2*pi*t),cy+r*sin((-1 if reverse else 1)*2*pi*t))

def polygon_path(points):
    def p(t):
        i=min(int(t*len(points)),len(points)-1);u=t*len(points)-i
        a=points[i];b=points[(i+1)%len(points)]
        return (a[0]+u*(b[0]-a[0]),a[1]+u*(b[1]-a[1]))
    return p

def signed_area(p):
    return sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1]))/2

def xdy(p):
    return sum((a[0]+b[0])*(b[1]-a[1])/2 for a,b in zip(p,p[1:]+p[:1]))

def run():
    cases=[('outside_circle',circle(5,0,1),pi,0),('outside_rectangle',polygon_path([(4,-1),(6,-1),(6,1),(4,1)]),4,0),('inside_circle',circle(0,0,6),36*pi,25*pi),('neutral_circle',circle(0,0,5),25*pi,25*pi),('reverse_circle',circle(5,0,1,True),-pi,0)]
    result={}
    for name,path,area,correction in cases:
        rows=[]
        for N in [100,400,1600,6400]:
            w=wheel(path,N); estimate=3*w+correction
            rows.append(dict(N=N,w=w,estimated_area=estimate,target=area,error=estimate-area))
        assert abs(rows[-1]['error'])<.000006
        result[name]=rows
    count=0;maxerr=0.0
    # 49 translated rectangles, all inside the non-singular reach region.
    for ix in range(7):
        for iy in range(7):
            cx=4.5+ix/6;cy=-.5+iy/6
            p=[(cx-.3,cy-.2),(cx+.3,cy-.2),(cx+.3,cy+.2),(cx-.3,cy+.2)]
            got=3*wheel(polygon_path(p),800);err=abs(got-.24)
            assert err<1e-7;maxerr=max(maxerr,err);count+=1
    # Exact finite identities for arbitrary closed integer polygonal walks;
    # self-crossings count algebraic signed area, not geometric union area.
    import random
    rng=random.Random(20261012);npoly=0
    for n in range(3,13):
        for _ in range(100):
            p=[(Fraction(rng.randrange(-20,21)),Fraction(rng.randrange(-20,21))) for j in range(n)]
            a=signed_area(p);assert a==xdy(p)
            assert signed_area(p[::-1])==-a
            shifted=[(x+17,y-9) for x,y in p];assert signed_area(shifted)==a
            scaled=[(3*x,3*y) for x,y in p];assert signed_area(scaled)==9*a
            npoly+=1
    poses=[]
    for k in range(12):
        t=k/12;p=circle(5,0,1)(t);q,m,n=pose(p)
        assert abs(hypot(*q)-5)<1e-12 and abs(hypot(p[0]-q[0],p[1]-q[1])-3)<1e-12
        poses.append(dict(t=t,p=p,q=q,m=m,n=n))
    return dict(model='ideal two arms R=5,L=3, wheel at midpoint, continuous positive joint branch',cases=result,translated_rectangles=count,max_rectangle_error=maxerr,exact_polygon_walks=npoly,animation_poses=poses)
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
