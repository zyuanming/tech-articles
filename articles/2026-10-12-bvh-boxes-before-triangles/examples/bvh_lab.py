#!/usr/bin/env python3
"""BVH learning lab. Python 3.10+, standard library only; original code, MIT.
This is a small double-precision teaching model, NOT a watertight production kernel.
All coordinates are dimensionless model units. Ray parameter t need not be distance.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import argparse, copy, json, math, platform, random
from pathlib import Path

Vec = tuple[float, float, float]
def add(a, b): return tuple(x+y for x,y in zip(a,b))
def sub(a, b): return tuple(x-y for x,y in zip(a,b))
def mul(a, s): return tuple(x*s for x in a)
def dot(a, b): return sum(x*y for x,y in zip(a,b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def unit(a): return mul(a, 1/math.sqrt(dot(a,a)))

@dataclass(frozen=True)
class Triangle:
    name: str
    a: Vec
    b: Vec
    c: Vec
    @property
    def center(self): return tuple((self.a[k]+self.b[k]+self.c[k])/3 for k in range(3))
    @property
    def bounds(self):
        return (tuple(min(self.a[k],self.b[k],self.c[k]) for k in range(3)),
                tuple(max(self.a[k],self.b[k],self.c[k]) for k in range(3)))

def union(boxes):
    boxes=list(boxes)
    if not boxes: raise ValueError('An empty group has no finite box in this lab.')
    return (tuple(min(b[0][k] for b in boxes) for k in range(3)),
            tuple(max(b[1][k] for b in boxes) for k in range(3)))

def box_hit(origin, direction, bounds, t_min=0.0, t_max=math.inf):
    """Closed slab intervals, including boundary contact; explicit parallel case."""
    lo, hi = t_min, t_max
    for k in range(3):
        if direction[k] == 0.0:  # includes -0.0; never divide 0 by 0
            if origin[k] < bounds[0][k] or origin[k] > bounds[1][k]:
                return None
            continue
        a = (bounds[0][k] - origin[k]) / direction[k]
        b = (bounds[1][k] - origin[k]) / direction[k]
        lo = max(lo, min(a, b))
        hi = min(hi, max(a, b))
        if lo > hi:
            return None
    return lo, hi

def triangle_hit(o, d, tri, t_min=0.0, t_max=math.inf):
    """Two-sided Moller-Trumbore-style determinant test. No back-face culling.
    Coplanar/near-parallel/degenerate triangles are not reported as point hits.
    EPS is a pedagogical, scale-dependent threshold, not a robustness proof.
    """
    e1, e2 = sub(tri.b,tri.a), sub(tri.c,tri.a)
    p = cross(d,e2); det = dot(e1,p)
    if abs(det) < 1e-12: return None
    v = sub(o,tri.a); u = dot(v,p)/det
    if u < 0.0 or u > 1.0: return None
    q = cross(v,e1); w = dot(d,q)/det
    if w < 0.0 or u+w > 1.0: return None
    t = dot(e2,q)/det
    return t if t_min <= t <= t_max else None

@dataclass
class Node:
    box: tuple
    ids: tuple[int,...] = ()
    children: tuple = ()
    name: str = ''

@dataclass
class Counts:
    boxes: int = 0
    triangles: int = 0
    pruned_after_hit: int = 0
    trace: list = field(default_factory=list)

def build(tris, ids=None, leaf_size=1, mode='longest', label='R'):
    """Median object split. The hand example uses y-first, then x.
    Equal centroid coordinates still split by count (stable ID tie-break).
    Re-sorting at each level makes this reference builder O(N log^2 N).
    """
    if leaf_size < 1: raise ValueError('leaf_size must be positive')
    ids=list(range(len(tris))) if ids is None else list(ids)
    if not ids: return None
    b=union(tris[i].bounds for i in ids)
    if len(ids) <= leaf_size: return Node(b,tuple(ids),(),label)
    spread=[max(tris[i].center[k] for i in ids)-min(tris[i].center[k] for i in ids) for k in range(3)]
    axis=1 if mode=='y_first' and spread[1]>1e-9 else max(range(3),key=lambda k:spread[k])
    ids.sort(key=lambda i:(tris[i].center[axis],tris[i].name))
    mid=len(ids)//2
    return Node(b,(),(build(tris,ids[:mid],leaf_size,mode,label+'0'),build(tris,ids[mid:],leaf_size,mode,label+'1')),label)

def refit(node, tris):
    if node is None: return
    if node.children:
        for c in node.children: refit(c,tris)
        node.box=union(c.box for c in node.children)
    else: node.box=union(tris[i].bounds for i in node.ids)

def validate(node, tris):
    if node is None: return []
    ids=[]
    if node.children:
        for c in node.children: ids.extend(validate(c,tris))
    else: ids=list(node.ids)
    assert node.box==union(tris[i].bounds for i in ids)
    return ids

def better(hit, old):
    return old is None or hit < old  # tuple (t, name): deterministic tie-break

def brute(tris,o,d,t_max=math.inf,any_hit=False):
    c=Counts();best=None
    for tri in tris:
        c.triangles+=1
        t=triangle_hit(o,d,tri,0.0,t_max if best is None else min(t_max,best[0]))
        if t is not None and better((t,tri.name),best):
            best=(t,tri.name)
            if any_hit: return best,c
    return best,c

def traverse(tris, root, o,d, near_first=True, shrink=True, t_max=math.inf,any_hit=False):
    """Each box call is counted once, even if tested for child ordering.
    Cached entries on stack are checked again only against updated best t;
    that comparison is not another box intersection.
    """
    stats=Counts();best=None
    if root is None: return None,stats
    def test(n,limit):
        stats.boxes+=1;v=box_hit(o,d,n.box,0.0,limit)
        stats.trace.append({'kind':'box','node':n.name,'interval':v})
        return v
    interval=test(root,t_max)
    if interval is None:return None,stats
    stack=[(interval[0],root)]
    while stack:
        entry,node=stack.pop()
        limit=min(t_max,best[0]) if shrink and best is not None else t_max
        if entry>limit:
            stats.pruned_after_hit+=1
            stats.trace.append({'kind':'prune','node':node.name,'entry':entry,'best':limit})
            continue
        if node.children:
            todo=[]
            for child in node.children:
                v=test(child,limit)
                if v is not None:todo.append((v[0],child))
            if near_first:todo.sort(key=lambda p:(p[0],p[1].name),reverse=True)
            else:todo.reverse()
            stack.extend(todo)
        else:
            for i in node.ids:
                stats.triangles+=1
                t=triangle_hit(o,d,tris[i],0.0,limit)
                stats.trace.append({'kind':'triangle','name':tris[i].name,'t':t})
                if t is not None and better((t,tris[i].name),best):
                    best=(t,tris[i].name)
                    if any_hit:return best,stats
                    if shrink:limit=best[0]
    return best,stats

def main_scene(nx=3,ny=4):
    result=[]
    for row in range(ny):
        for col in range(nx):
            x,y=3+3*col,4*row
            name=chr(65+len(result)) if nx*ny<=26 else f'T{len(result):05}'
            result.append(Triangle(name,(x,y-.6,-.5),(x,y+.6,-.5),(x+.6,y,.5)))
    return result

def summary(hit,c):
    return dict(hit=hit,boxes=c.boxes,triangles=c.triangles,pruned_after_hit=c.pruned_after_hit)

def same(a,b):
    if a is None or b is None:return a is b
    return a[1]==b[1] and math.isclose(a[0],b[0],rel_tol=1e-10,abs_tol=1e-10)

def plane_oracle(o,d,tr):
    """Independent plane + dot-product barycentric oracle for ordinary cases."""
    e,f=sub(tr.b,tr.a),sub(tr.c,tr.a);n=cross(e,f);den=dot(n,d)
    if abs(den)<1e-12:return None
    t=dot(n,sub(tr.a,o))/den
    if t<0:return None
    p=sub(add(o,mul(d,t)),tr.a)
    ee,ef,ff,pe,pf=dot(e,e),dot(e,f),dot(f,f),dot(p,e),dot(p,f)
    det=ee*ff-ef*ef
    if det<1e-20:return None
    u=(pe*ff-pf*ef)/det;v=(pf*ee-pe*ef)/det
    return t if u>=0 and v>=0 and u+v<=1 else None

def ray_grid():
    return [((0.0,-1.0+i*.125,0.0),(1.0,0.0,0.0)) for i in range(113)]

def total_queries(tris,root,rays):
    b=t=p=0;hits=0
    for o,d in rays:
        hit,c=traverse(tris,root,o,d);ref,_=brute(tris,o,d)
        assert same(hit,ref),(hit,ref,o,d)
        b+=c.boxes;t+=c.triangles;p+=c.pruned_after_hit;hits+=hit is not None
    return dict(rays=len(rays),hits=hits,boxes=b,triangles=t,pruned_after_hit=p)

def tests(output):
    tris=main_scene();root=build(tris,mode='y_first');o=(0,8,0);d=(1,0,0)
    assert sorted(validate(root,tris))==list(range(12))
    rec={'python':platform.python_version(),'seed':20261012,'units':'dimensionless model units','status':'PASS',
         'triangle_count':12,'query_origin':o,'query_direction':d,'scene':[dict(name=t.name,vertices=[t.a,t.b,t.c]) for t in tris]}
    rec['main']={}
    for name,fn in [('brute',lambda:brute(tris,o,d)),('bvh_no_shrink',lambda:traverse(tris,root,o,d,shrink=False)),('bvh_nearest',lambda:traverse(tris,root,o,d))]:
        h,c=fn();assert same(h,(3.3,'G'));rec['main'][name]=summary(h,c);rec['main'][name]['trace']=c.trace
    row_box=union(t.bounds for t in tris[6:9])
    rec['slabs']={'row_box':row_box,'diagonal':box_hit((0,2,0),(1,1,0),row_box),'reverse':box_hit((12,8,0),(-1,0,0),row_box)}
    assert rec['slabs']['diagonal']==(5.4,6.6)
    # Boundary cases have exact, small integer binary values.
    unitbox=((0.,0.,0.),(1.,1.,1.))
    edgecases=[('parallel_inside',(.5,.5,-1),(0.,-0.,1.),(1.,2.)),('parallel_outside',(2,.5,-1),(0,0,1),None),('on_face',(0,.5,-1),(-0.,0,1),(1.,2.)),('inside',(.5,.5,.5),(1,0,0),(0.,.5)),('behind',(2,.5,.5),(1,0,0),None),('corner',(0,-1,.5),(1,1,0),(1.,1.))]
    rec['box_edge_cases']=[]
    for name,ro,rd,want in edgecases:
        got=box_hit(ro,rd,unitbox);assert got==want,(name,got,want)
        rec['box_edge_cases'].append(dict(name=name,result=got))
    # AABB false positive: ray through the upper-right projected corner.
    miss_o=(0,8.5,.4);false_box=box_hit(miss_o,d,tris[6].bounds);false_tri=triangle_hit(miss_o,d,tris[6]);assert false_box is not None and false_tri is None
    rec['false_positive']={'origin':miss_o,'box':false_box,'triangle':false_tri}
    # Bad tree has identical overlapping boxes; a miss forces every leaf test.
    bad=[Triangle(str(i),* (tris[6].a,tris[6].b,tris[6].c)) for i in range(12)]
    h,c=traverse(bad,build(bad),miss_o,d);assert h is None and c.boxes==23 and c.triangles==12
    rec['overlap_miss']=summary(h,c)
    # Any hit versus closest: reversed list encounters distant I before G.
    reversed_tris=list(reversed(tris));rec['any_vs_nearest']={}
    for anyhit in [False,True]:
        h,c=brute(reversed_tris,o,d,any_hit=anyhit);rec['any_vs_nearest'][str(anyhit)]=summary(h,c)
    assert rec['any_vs_nearest']['True']['hit'][1]=='I'
    # Permute which object occupies each fixed geometric location.
    perm=[0,11,3,8,1,10,4,7,2,9,5,6]
    moved=[Triangle(tris[i].name,tris[j].a,tris[j].b,tris[j].c) for i,j in enumerate(perm)]
    refitted=copy.deepcopy(root);refit(refitted,moved);rebuilt=build(moved,mode='y_first')
    assert sorted(validate(refitted,moved))==list(range(12))
    rec['movement']={'permutation_old_id_to_new_position':perm,'initial':total_queries(tris,root,ray_grid()),'refit':total_queries(moved,refitted,ray_grid()),'rebuild':total_queries(moved,rebuilt,ray_grid())}
    # Random traversal agreement tests, both ordering strategies and shrinking.
    rng=random.Random(20261012);hits=0
    for _ in range(20000):
        ro=(rng.uniform(-2,14),rng.uniform(-2,14),rng.uniform(-2,2));rd=unit((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-1,1)))
        truth,_=brute(tris,ro,rd)
        hits+=truth is not None
        for near,shrink in [(True,True),(False,True),(True,False)]:
            got,_=traverse(tris,root,ro,rd,near_first=near,shrink=shrink)
            assert same(got,truth),(ro,rd,truth,got)
    rec['random_traversal']={'rays':20000,'modes':3,'comparisons':60000,'hits':hits,'mismatches':0}
    oracle_comp=0
    for _ in range(10000):
        ro=(rng.uniform(-2,14),rng.uniform(-2,14),rng.uniform(-2,2));rd=unit((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-1,1)))
        tr=rng.choice(tris);a=triangle_hit(ro,rd,tr);b=plane_oracle(ro,rd,tr)
        assert (a is None and b is None) or (a is not None and b is not None and math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-8)),(a,b)
        oracle_comp+=1
    rec['independent_triangle_oracle']={'comparisons':oracle_comp,'mismatches':0,'scope':'ordinary random cases; not a watertightness proof'}
    # Identical geometric depth ties and empty trees are deterministic.
    tie=[Triangle('B',tris[0].a,tris[0].b,tris[0].c),Triangle('A',tris[0].a,tris[0].b,tris[0].c)]
    assert traverse(tie,build(tie),(0,0,0),d)[0][1]=='A'
    assert traverse([],build([]),o,d)[0] is None
    deg=Triangle('deg',(0,0,0),(0,0,0),(0,0,0));assert triangle_hit(o,d,deg) is None
    rec['extra_cases']=['deterministic_tie','empty_tree','degenerate_triangle_no_point_hit']
    rec['scaling']=[]
    for nx,ny in [(3,4),(12,16),(48,64)]:
        scene=main_scene(nx,ny);tree=build(scene)
        rays=[((0,4*(i%ny),0),(1,0,0)) for i in range(256)]
        totals=total_queries(scene,tree,rays);totals.update(N=len(scene),brute_triangle_tests=len(scene)*len(rays))
        rec['scaling'].append(totals)
    output.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in rec.items() if k not in ['scene','main']},ensure_ascii=False,indent=2))
    print('MAIN',json.dumps({k:{kk:vv for kk,vv in v.items() if kk!='trace'} for k,v in rec['main'].items()}))
    return rec

def render(path,width=480,height=400):
    tris=main_scene();root=build(tris,mode='y_first');eye=(-8,7,9);target=(6,6,0)
    f=unit(sub(target,eye));r=unit(cross(f,(0,0,1)));up=cross(r,f)
    pix=bytearray();tri_count=box_count=0
    for j in range(height):
        for i in range(width):
            sx=(2*(i+.5)/width-1)*width/height*.52;sy=(1-2*(j+.5)/height)*.52
            d=unit(add(f,add(mul(r,sx),mul(up,sy))));hit,c=traverse(tris,root,eye,d);tri_count+=c.triangles;box_count+=c.boxes
            if hit:
                tri=next(t for t in tris if t.name==hit[1]);n=unit(cross(sub(tri.b,tri.a),sub(tri.c,tri.a)))
                light=.4+.6*abs(dot(n,unit((-1,-1,2))))
                base=[(44,138,133),(231,145,69),(78,117,163),(166,99,120)][(ord(tri.name)-65)//3]
                rgb=tuple(round(x*light) for x in base)
            else:rgb=(242,239,229)
            pix.extend(rgb)
    path.write_bytes(f'P6\n{width} {height}\n255\n'.encode()+pix)
    return dict(width=width,height=height,primary_rays=width*height,box_tests=box_count,triangle_tests=tri_count,identity='actual output of this teaching CPU ray tracer; no path bounces or real hardware benchmark')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=Path('results.json'));ap.add_argument('--render',type=Path);args=ap.parse_args()
    rec=tests(args.output)
    if args.render:
        rr=render(args.render);print('RENDER',json.dumps(rr));args.render.with_suffix('.json').write_text(json.dumps(rr,indent=2))
