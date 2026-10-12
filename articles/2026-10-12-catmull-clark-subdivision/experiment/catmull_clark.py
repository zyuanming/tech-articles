"""Original educational implementation. Python 3. No third-party dependencies.
Supported: orientable 2-manifold polygon meshes, optional boundary-edge smoothing,
and infinite sharp edges; no semi-sharp/UV/adaptive/OpenSubdiv implementation.
Run: python catmull_clark.py --output results.json
SPDX-License-Identifier: MIT
"""
from collections import defaultdict, Counter
from fractions import Fraction
import argparse, json, math

def add(*ps): return tuple(sum(x) for x in zip(*ps))
def mul(p,s): return tuple(x*s for x in p)
def mean(ps): return mul(add(*ps),Fraction(1,len(ps)))
def edge(a,b): return (min(a,b),max(a,b))

def cube(exact=False):
    vs=[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
    if exact:vs=[tuple(map(Fraction,p)) for p in vs]
    return vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]

def adjacency(vs,faces):
    ef=defaultdict(list); vf=[[] for _ in vs]; ve=[set() for _ in vs]
    for fi,f in enumerate(faces):
        for i,a in enumerate(f):
            b=f[(i+1)%len(f)]; e=edge(a,b);ef[e].append(fi);vf[a].append(fi);ve[a].add(e);ve[b].add(e)
    return ef,vf,ve

def validate(vs,faces,closed=None):
    assert vs and faces
    assert all(len(p)==3 and all(math.isfinite(float(c)) for c in p) for p in vs)
    directed=Counter()
    for f in faces:
        assert len(f)>=3 and len(set(f))==len(f)
        assert all(0<=v<len(vs) for v in f)
        for a,b in zip(f,f[1:]+f[:1]):directed[a,b]+=1
    assert max(directed.values())==1,'duplicate directed edge / inconsistent winding'
    ef,vf,ve=adjacency(vs,faces)
    assert all(len(fs) in (1,2) for fs in ef.values()),'non-manifold edge'
    for e,fs in ef.items():
        if len(fs)==2:assert directed[e[0],e[1]]==directed[e[1],e[0]]==1
    bd=[e for e,fs in ef.items() if len(fs)==1]
    if closed is True:assert not bd
    if closed is False:assert bd
    for v,fs in enumerate(vf):
        assert fs,'isolated vertex'
        # Incident-face graph must be one cycle or one boundary chain.
        nbr={f:set() for f in fs}
        for e in ve[v]:
            if len(ef[e])==2:
                a,b=ef[e];nbr[a].add(b);nbr[b].add(a)
        seen=set();todo=[fs[0]]
        while todo:
            f=todo.pop()
            if f not in seen:seen.add(f);todo.extend(nbr[f]-seen)
        assert len(seen)==len(fs),'bow-tie vertex'
        assert sum(len(ef[e])==1 for e in ve[v]) in (0,2)
    return dict(V=len(vs),E=len(ef),F=len(faces),chi=len(vs)-len(ef)+len(faces),boundary_edges=len(bd),valences=dict(Counter(map(len,ve))))

def refine(vs,faces,creases=frozenset(),linear=False,pin_boundary_corners=False):
    validate(vs,faces)
    ef,vf,ve=adjacency(vs,faces)
    fpoints=[mean([vs[v] for v in f]) for f in faces]
    ordered=sorted(ef);eid={e:len(vs)+i for i,e in enumerate(ordered)}
    fid={i:len(vs)+len(ordered)+i for i in range(len(faces))}
    sharp=set(creases)|{e for e,fs in ef.items() if len(fs)==1}
    vpoints=[]
    for v,p in enumerate(vs):
        se=[e for e in ve[v] if e in sharp]
        if linear or len(se)>=3 or (pin_boundary_corners and len(vf[v])==1):q=p
        elif len(se)==2:
            ns=[vs[e[0] if e[1]==v else e[1]] for e in se]
            q=mul(add(mul(p,6),*ns),Fraction(1,8))
        else:
            n=len(ve[v]);Q=mean([fpoints[f] for f in vf[v]])
            R=mean([mean([vs[a],vs[b]]) for a,b in ve[v]])
            q=mul(add(Q,mul(R,2),mul(p,n-3)),Fraction(1,n))
        vpoints.append(q)
    epoints=[]
    for a,b in ordered:
        e=(a,b)
        epoints.append(mean([vs[a],vs[b]]) if linear or e in sharp else mean([vs[a],vs[b]]+[fpoints[f] for f in ef[e]]))
    outvs=vpoints+epoints+fpoints;outfaces=[]
    for fi,f in enumerate(faces):
        for i,v in enumerate(f):outfaces.append((v,eid[edge(v,f[(i+1)%len(f)])],fid[fi],eid[edge(f[i-1],v)]))
    outsharp=set()
    for a,b in creases:outsharp.update([edge(a,eid[edge(a,b)]),edge(eid[edge(a,b)],b)])
    validate(outvs,outfaces)
    return outvs,outfaces,outsharp,dict(edge_ids=eid,face_ids=fid)

def limit_vertex(vs,faces,v):
    """Independent all-quad interior limit stencil; diagonals are opposite corners."""
    ef,vf,ve=adjacency(vs,faces);n=len(ve[v]);assert n==len(vf[v]) and n>=3
    assert all(len(faces[f])==4 for f in vf[v])
    neighbors=[vs[e[0] if e[1]==v else e[1]] for e in ve[v]]
    opposites=[]
    for fi in vf[v]:
        f=faces[fi];opposites.append(vs[f[(f.index(v)+2)%4]])
    return mul(add(mul(vs[v],n*n),mul(add(*neighbors),4),add(*opposites)),Fraction(1,n*(n+5)))

def signed_volume(vs,faces):
    s=0.0
    for f in faces:
        a=vs[f[0]]
        for i in range(1,len(f)-1):
            b,c=vs[f[i]],vs[f[i+1]]
            s+=float(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    return s

def serialize_mesh(vs,faces):return dict(vertices=[[float(x) for x in p] for p in vs],faces=faces)

def run():
    tests=[];vs,fs=cube(True); v1,f1,_,ids=refine(vs,fs)
    assert v1[6]==(Fraction(5,9),)*3
    assert v1[ids['edge_ids'][(5,6)]]==(Fraction(3,4),0,Fraction(3,4))
    assert v1[ids['face_ids'][1]]==(0,0,1)
    tests.append('cube face, edge, vertex: exact Fraction assertions')
    p_limit=limit_vertex(vs,fs,6); assert p_limit==(Fraction(1,2),)*3
    assert limit_vertex(v1,f1,6)==p_limit
    axis_limit=limit_vertex(v1,f1,ids['face_ids'][1]);assert axis_limit==(0,0,Fraction(68,81))
    tests.append('independent limit stencil: P∞=(1/2)^3; face-axis z=68/81; invariant after refinement')
    # Independent nonsymmetric interior fan. Four quads, center at (0,0,2).
    vv=[(0,0,2),(2,0,0),(0,2,0),(-2,0,0),(0,-2,0),(2,2,4),(-2,2,0),(-2,-2,0),(2,-2,0)]
    ff=[(0,1,5,2),(0,2,6,3),(0,3,7,4),(0,4,8,1)]
    x,_,_,_=refine(vv,ff);assert x[0]==(0,0,Fraction(19,16))
    # Independent stencil 9/16 center + 3/32 cardinal sum + 1/64 diagonal sum.
    direct=add(mul(vv[0],Fraction(9,16)),mul(add(*vv[1:5]),Fraction(3,32)),mul(add(*vv[5:9]),Fraction(1,64)))
    assert x[0]==direct;tests.append('asymmetric regular 4-quad fan: updated z=19/16 via independent 9/16,3/32,1/64 stencil')
    # Affine covariance, unequal box dimensions and translation; values remain exact.
    trans=lambda p:(2*p[0]+3,3*p[1]-7,5*p[2]+2)
    av,_,_,_=refine([trans(p) for p in vs],fs)
    assert all(a==trans(b) for a,b in zip(av,v1));tests.append('exact nonuniform scale and translation covariance')
    # Open the same box by removing its top face.
    of=[f for i,f in enumerate(fs) if i!=1];ov,of1,_,_=refine(vs,of)
    assert ov[6]==(Fraction(3,4),Fraction(3,4),1)
    assert validate(vs,of,False)['boundary_edges']==4 and validate(ov,of1,False)['boundary_edges']==8
    tests.append('open cube: boundary P=(3/4,3/4,1), boundary edges 4→8, chi=1')
    rim={edge(a,b) for a,b in zip(fs[1],fs[1][1:]+fs[1][:1])}
    crv,crf,_,_=refine(vs,fs,rim);assert crv[6]==(Fraction(3,4),Fraction(3,4),1)
    ef,_,_=adjacency(vs,fs);allv,allf,_,_=refine(vs,fs,set(ef));assert allv[6]==vs[6]
    tests.append('infinite top-rim crease: P=(3/4,3/4,1); three incident sharp edges pin cube corner')
    qv=[(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)];qf=[(0,1,2,3)]
    assert refine(qv,qf)[0][2]==(Fraction(3,4),Fraction(3,4),0)
    assert refine(qv,qf,pin_boundary_corners=True)[0][2]==qv[2]
    tests.append('isolated quad: edge-only corner moves; edge-and-corner option pins it')
    # Three invalid inputs must fail: duplicate face, 3-face edge, bow tie.
    bad=[(vs,fs+[fs[0]]), ([(0,0,0),(1,0,0),(0,1,0),(0,-1,0),(0,0,1)],[(0,1,2),(1,0,3),(0,1,4)]), ([(0,0,0),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0)],[(0,1,2),(0,3,4)])]
    for bv,bf in bad:
        try:validate(bv,bf)
        except AssertionError:pass
        else:raise AssertionError('invalid mesh accepted')
    tests.append('rejected duplicate-oriented face, 3-face edge and bow-tie vertex')
    levels=[];vs,fs=cube();vs=[tuple(map(float,p)) for p in vs]
    for level in range(6):
        stats=validate(vs,fs,True);assert stats['chi']==2 and stats['F']==6*4**level
        assert stats['V']==6*4**level+2 and stats['E']==12*4**level
        assert stats['valences'].get(3,0)==8
        assert signed_volume(vs,fs)>0
        levels.append(dict(level=level,**stats,tracked_P=vs[6],volume=signed_volume(vs,fs),min_radius=min(math.sqrt(sum(x*x for x in p)) for p in vs),max_radius=max(math.sqrt(sum(x*x for x in p)) for p in vs)))
        if level<5:vs,fs,_,_=refine(vs,fs)
    tests.append('levels 0–5: oriented closed 2-manifold, vertex fans, Euler=2, V/E/F counts, eight valence-3 vertices, positive volume')
    return dict(status='AUTHOR_SELF_CHECK',implementation='original Python; not OpenSubdiv output',tests=tests,levels=levels,limit=dict(corner=[.5]*3,corner_radius=math.sqrt(3)/2,axis=[0,0,68/81],axis_radius=68/81),independent_example=dict(center_before=[0,0,2],center_after=[0,0,19/16]))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='results.json');a=p.parse_args()
    r=run();open(a.output,'w').write(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False,indent=2))
