"""Original exact-arithmetic perspective interpolation experiment. Python 3.12.
Camera looks +Z; image plane Z=1; no clipping, lens distortion, or GPU timing.
Run: python perspective_lab.py
License: CC BY 4.0, same as original explanatory example; no third-party code.
"""
from fractions import Fraction as F
import json


def barycentric(p, tri):
    (x,y)=p
    (x0,y0),(x1,y1),(x2,y2)=tri
    den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
    if den==0:
        raise ValueError('projected triangle is degenerate')
    a=((y1-y2)*(x-x2)+(x2-x1)*(y-y2))/den
    b=((y2-y0)*(x-x2)+(x0-x2)*(y-y2))/den
    return a,b,1-a-b


def correct(weights, attributes, depths):
    if any(z<=0 for z in depths):
        raise ValueError('this simple camera model requires every Z > 0')
    q=sum(w/z for w,z in zip(weights,depths))
    return sum(w*a/z for w,a,z in zip(weights,attributes,depths))/q


def vertices(k=F(3)):
    # Coplanar affine UV map: X=-1+2u, Y=-1+2v, Z=1+k*v.
    return [(-F(1),-F(1),F(1),F(0),F(0)),
            (F(1),-F(1),F(1),F(1),F(0)),
            (F(1),F(1),1+k,F(1),F(1)),
            (-F(1),F(1),1+k,F(0),F(1))]


DIAGONALS=[[(0,1,2),(0,2,3)],[(0,1,3),(1,2,3)]]


def interpolate(p,k=F(3),diagonal=0,perspective=True):
    verts=vertices(k)
    for ids in DIAGONALS[diagonal]:
        t=[verts[i] for i in ids]
        w=barycentric(p,[(x/z,y/z) for x,y,z,u,v in t])
        if min(w)>=0:
            result=[]
            for j in (3,4):
                vals=[v[j] for v in t]
                result.append(correct(w,vals,[v[2] for v in t]) if perspective
                              else sum(a*b for a,b in zip(w,vals)))
            return tuple(result)
    raise ValueError('point outside projected quad')


def ray_plane(p,k=F(3)):
    # Independent geometric oracle: ray=(sx*Z,sy*Z,Z), plane Z=1+k*(Y+1)/2.
    sx,sy=p
    z=(1+k/2)/(1-k*sy/2)
    return (sx*z+1)/2,(sy*z+1)/2


def run():
    edge=[]
    for i in range(101):
        s=F(i,100);t=s/(4-3*s)
        u=correct((1-s,s),(F(0),F(1)),(F(1),F(4)))
        assert u==t and 4*t/(1+3*t)==s
    for s in (F(0),F(1,4),F(1,2),F(3,4),F(1)):
        t=s/(4-3*s);edge.append({'screen':str(s),'u':str(t),'Z':str(1+3*t)})
    cases=0;affine_changed=0;max_difference=F(0)
    for k in (F(0),F(1),F(2),F(3),F(7)):
        for i in range(41):
            for j in range(41):
                u,v=F(i,40),F(j,40);z=1+k*v;p=((2*u-1)/z,(2*v-1)/z)
                assert ray_plane(p,k)==(u,v)
                a=interpolate(p,k,0);b=interpolate(p,k,1)
                assert a==b==(u,v)
                aa=interpolate(p,k,0,False);bb=interpolate(p,k,1,False)
                if k==0:assert aa==bb==(u,v)
                if aa!=bb:affine_changed+=1
                max_difference=max(max_difference,abs(aa[0]-bb[0]),abs(aa[1]-bb[1]))
                cases+=1
    # Screen origin; its ray meets this plane at its UV center.
    p=(F(0),F(0))
    selected={'screen':['0','0'],'oracle':[str(x) for x in ray_plane(p)],
              'perspective_diagonal_0':[str(x) for x in interpolate(p)],
              'perspective_diagonal_1':[str(x) for x in interpolate(p,diagonal=1)],
              'affine_diagonal_0':[str(x) for x in interpolate(p,perspective=False)],
              'affine_diagonal_1':[str(x) for x in interpolate(p,diagonal=1,perspective=False)]}
    # Both affine and corrected values are continuous along each shared diagonal;
    # changing a diagonal may change the INTERIOR mapping, not make a value crack.
    continuity=0
    verts=vertices()
    for ids0,ids1 in DIAGONALS:
        common=sorted(set(ids0)&set(ids1));va,vb=[verts[i] for i in common]
        for i in range(21):
            t=F(i,20);p=tuple((1-t)*va[d]/va[2]+t*vb[d]/vb[2] for d in (0,1))
            values=[]
            for ids in (ids0,ids1):
                tri=[verts[i] for i in ids];weights=barycentric(p,[(x/z,y/z) for x,y,z,u,v in tri])
                values.append(tuple(sum(w*a[j] for w,a in zip(weights,tri)) for j in (3,4)))
            assert values[0]==values[1];continuity+=1
    return {'status':'PASS','edge_cases':101,'quad_exact_oracle_cases':cases,
            'affine_diagonal_changed_cases':affine_changed,'max_affine_diagonal_coordinate_difference':str(max_difference),
            'shared_edge_continuity_cases':continuity,'edge_table':edge,'selected_quad_point':selected,
            'scope':'Exact rational checks in a stated pinhole/planar model, not GPU or game measurements.'}


if __name__=='__main__':
    print(json.dumps(run(),ensure_ascii=False,indent=2))
