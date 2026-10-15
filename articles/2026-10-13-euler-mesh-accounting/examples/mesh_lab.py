"""Original indexed-surface examples and exact combinatorial checks. MIT.
Python 3.11+, standard library. Run: python mesh_lab.py
Only polygon boundary edges are represented; no loose edges or hidden face holes.
"""
from pathlib import Path
from collections import Counter,defaultdict,deque
from math import sin,cos,pi,sqrt
import json,random
HERE=Path(__file__).resolve().parent

def edges(faces):
    return Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]))

def components(adj):
    seen=set();out=[]
    for start in sorted(adj):
        if start in seen:continue
        q=[start];seen.add(start);part=[]
        while q:
            v=q.pop();part.append(v)
            for w in adj[v]:
                if w not in seen:seen.add(w);q.append(w)
        out.append(sorted(part))
    return out

def inspect(mesh):
    vs,fs=mesh['vertices'],mesh['faces'];n=len(vs)
    assert all(len(f)>=3 and len(set(f))==len(f) and all(isinstance(v,int) and 0<=v<n for v in f) for f in fs)
    es=edges(fs);adj={i:set() for i in range(n)}
    for a,b in es:adj[a].add(b);adj[b].add(a)
    boundary=[e for e,c in es.items() if c==1];bad=[e for e,c in es.items() if c>2]
    ba=defaultdict(set)
    for a,b in boundary:ba[a].add(b);ba[b].add(a)
    boundary_loops=len(components(ba)) if all(len(x)==2 for x in ba.values()) else None
    # Vertex link: each incident face joins its predecessor and successor.
    # A surface interior needs one cycle, a boundary vertex one path.
    bad_vertices=[]
    for v in range(n):
        link=defaultdict(set);deg=Counter()
        for f in fs:
            if v in f:
                i=f.index(v);a,b=f[i-1],f[(i+1)%len(f)];link[a].add(b);link[b].add(a);deg[a]+=1;deg[b]+=1
        is_boundary=v in ba
        ok=bool(link) and len(components(link))==1
        if is_boundary:ok=ok and sum(x==1 for x in deg.values())==2 and all(x in (1,2) for x in deg.values())
        else:ok=ok and all(x==2 for x in deg.values())
        if not ok:bad_vertices.append(v)
    return dict(V=n,E=len(es),F=len(fs),chi=n-len(es)+len(fs),components=len(components(adj)),boundary_edges=len(boundary),boundary_loops=boundary_loops,overfull_edges=[list(e) for e in bad],bad_vertex_links=bad_vertices,surface_local_checks_pass=not bad and not bad_vertices)

def cube():
    return dict(vertices=[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])

def subdiv_cube(n):
    c=cube();vs=[];fs=[];lookup={}
    def add(p):
        p=tuple(round(x,10) for x in p)
        if p not in lookup:lookup[p]=len(vs);vs.append(list(p))
        return lookup[p]
    for face in c['faces']:
        a,b,cc,d=[c['vertices'][i] for i in face]
        grid={}
        for j in range(n+1):
            for i in range(n+1):
                u,v=i/n,j/n
                p=[(1-u)*(1-v)*a[k]+u*(1-v)*b[k]+u*v*cc[k]+(1-u)*v*d[k] for k in range(3)]
                grid[i,j]=add(p)
        for j in range(n):
            for i in range(n):fs.append([grid[i,j],grid[i+1,j],grid[i+1,j+1],grid[i,j+1]])
    return dict(vertices=vs,faces=fs)

def unjoined(c,explode=0):
    vs=[];fs=[]
    for f in c['faces']:
        center=[sum(c['vertices'][i][k] for i in f)/len(f) for k in range(3)];ids=[]
        for i in f:ids.append(len(vs));vs.append([c['vertices'][i][k]+explode*center[k] for k in range(3)])
        fs.append(ids)
    return dict(vertices=vs,faces=fs)

def torus(n=8,m=6):
    vs=[];fs=[]
    for i in range(n):
        a=2*pi*i/n
        for j in range(m):
            b=2*pi*j/m;vs.append([(1.7+.6*cos(b))*cos(a),(1.7+.6*cos(b))*sin(a),.6*sin(b)])
    idx=lambda i,j:(i%n)*m+j%m
    for i in range(n):
        for j in range(m):fs.append([idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1)])
    return dict(vertices=vs,faces=fs)

def square_ring():
    # Outer and inner square loops, two height levels; all 16 faces are disks.
    outer=[[-2,-2],[2,-2],[2,2],[-2,2]];inner=[[-.8,-.8],[.8,-.8],[.8,.8],[-.8,.8]]
    vs=[[x,y,z] for z in [-.55,.55] for loop in [outer,inner] for x,y in loop];fs=[]
    for i in range(4):
        j=(i+1)%4
        fs += [[i,j,j+8,i+8],[i+4,i+12,j+12,j+4],[i+8,j+8,j+12,i+12],[j,i,i+4,j+4]]
    return dict(vertices=vs,faces=fs)

def two_holes():
    # Extrude a 5x3 square-cell plate with two separated missing interior cells.
    cells={(i,j) for i in range(5) for j in range(3)}-{(1,1),(3,1)};vs=[];fs=[];lookup={}
    def v(x,y,z):
        key=(x,y,z)
        if key not in lookup:lookup[key]=len(vs);vs.append([x-2.5,y-1.5,z])
        return lookup[key]
    for x,y in sorted(cells):
        loop=[(x,y),(x+1,y),(x+1,y+1),(x,y+1)]
        fs.append([v(a,b,.45) for a,b in loop]);fs.append([v(a,b,-.45) for a,b in loop[::-1]])
        for (a,b),(c,d),(dx,dy) in zip(loop,loop[1:]+loop[:1],[(0,-1),(1,0),(0,1),(-1,0)]):
            if (x+dx,y+dy) not in cells:fs.append([v(a,b,-.45),v(c,d,-.45),v(c,d,.45),v(a,b,.45)])
    return dict(vertices=vs,faces=fs)

def join_meshes(a,b,offset=(4,0,0)):
    n=len(a['vertices']);return dict(vertices=a['vertices']+[[p[k]+offset[k] for k in range(3)] for p in b['vertices']],faces=a['faces']+[[v+n for v in f] for f in b['faces']])

def split_face(mesh,fi):
    vs=[p[:] for p in mesh['vertices']];fs=[f[:] for f in mesh['faces']];f=fs.pop(fi);i=len(vs);vs.append([sum(vs[v][k] for v in f)/len(f) for k in range(3)])
    fs.extend([[a,b,i] for a,b in zip(f,f[1:]+f[:1])]);return dict(vertices=vs,faces=fs)

def split_edge(mesh,edge):
    a,b=edge;vs=[p[:] for p in mesh['vertices']];i=len(vs);vs.append([(x+y)/2 for x,y in zip(vs[a],vs[b])]);fs=[]
    for f in mesh['faces']:
        new=[]
        for x,y in zip(f,f[1:]+f[:1]):
            new.append(x)
            if {x,y}=={a,b}:new.append(i)
        fs.append(new)
    return dict(vertices=vs,faces=fs)

def make_models():
    c=cube();tri=dict(vertices=c['vertices'],faces=[t for f in c['faces'] for t in [[f[0],f[1],f[2]],[f[0],f[2],f[3]]]])
    sphere=subdiv_cube(4);sphere['vertices']=[[1.45*x/sqrt(sum(y*y for y in p)) for x in p] for p in sphere['vertices']]
    opening=dict(vertices=c['vertices'],faces=[f for i,f in enumerate(c['faces']) if i!=1])
    tetra=dict(vertices=[[0,0,0],[1,0,1],[0,1,1],[-.6,-.6,1]],faces=[[0,2,1],[0,1,3],[0,3,2],[1,2,3]])
    pinch=join_meshes(tetra,dict(vertices=[[p[0],p[1],-p[2]] for p in tetra['vertices']],faces=tetra['faces']),offset=(0,0,0))
    pinch['faces']=[[0 if v==4 else (v-1 if v>4 else v) for v in f] for f in pinch['faces']];pinch['vertices'].pop(4)
    triple=dict(vertices=[[0,0,-1],[0,0,1],[1,0,0],[-.5,.866,0],[-.5,-.866,0]],faces=[[0,1,2],[1,0,3],[0,1,4]])
    return dict(cube=c,triangulated=tri,subdivide2=subdiv_cube(2),subdivide4=subdiv_cube(4),round_shell=sphere,unjoined=unjoined(c),exploded=unjoined(c,.35),open_box=opening,split_edge=split_edge(c,(0,1)),split_face=split_face(c,1),square_ring=square_ring(),torus=torus(),two_holes=two_holes(),two_cubes=join_meshes(c,c),pinch=pinch,triple_edge=triple)

def glued_grid(n=8,m=6,wrap_x=False,wrap_y=False):
    nx=n if wrap_x else n+1; ny=m if wrap_y else m+1
    idx=lambda i,j:(i%nx)*ny+j%ny
    return dict(vertices=[[i,j,0] for i in range(nx) for j in range(ny)],faces=[[idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1)] for i in range(n) for j in range(m)])

def test():
    tests=0
    for n in range(1,9):
        r=inspect(subdiv_cube(n));assert (r['V'],r['E'],r['F'],r['chi'])==(6*n*n+2,12*n*n,6*n*n,2);assert r['surface_local_checks_pass'];tests+=1
    for n in range(3,13):
        for m in range(3,13):
            r=inspect(torus(n,m));assert (r['V'],r['E'],r['F'],r['chi'])==(n*m,2*n*m,n*m,0);assert r['surface_local_checks_pass'];tests+=1
    rng=random.Random(20261013);c=cube()
    for _ in range(150):
        c=split_face(c,rng.randrange(len(c['faces']))) if rng.random()<.5 else split_edge(c,rng.choice(sorted(edges(c['faces']))))
        r=inspect(c);assert r['chi']==2 and r['surface_local_checks_pass'];tests+=1
    models=make_models();expected={'cube':(8,12,6,2),'triangulated':(8,18,12,2),'unjoined':(24,24,6,6),'open_box':(8,12,5,1),'square_ring':(16,32,16,0),'torus':(48,96,48,0),'two_cubes':(16,24,12,4),'two_holes':(48,100,50,-2),'pinch':(7,12,8,3),'triple_edge':(5,7,3,1)}
    for name,t in expected.items():
        r=inspect(models[name]);assert tuple(r[k] for k in ['V','E','F','chi'])==t,(name,r);tests+=1
    assert inspect(models['pinch'])['bad_vertex_links']==[0]
    assert len(inspect(models['triple_edge'])['overfull_edges'])==1
    for wx,wy,t in [(False,False,(63,110,48,1)),(True,False,(56,104,48,0)),(True,True,(48,96,48,0))]:
        r=inspect(glued_grid(wrap_x=wx,wrap_y=wy));assert tuple(r[k] for k in ['V','E','F','chi'])==t;tests+=1
    return tests

if __name__=='__main__':
    models=make_models();results={'tests_passed':test(),'seed':20261013,'scope':'Indexed polygon surfaces. Local manifold checks are not a geometric self-intersection test or a complete classifier.','models':{k:inspect(v) for k,v in models.items()},'grid_identification':{name:inspect(glued_grid(wrap_x=x,wrap_y=y)) for name,x,y in [('patch',False,False),('cylinder',True,False),('torus',True,True)]}}
    (HERE/'meshes.json').write_text(json.dumps(models,ensure_ascii=False,indent=2)+'\n');(HERE/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print(json.dumps(results,ensure_ascii=False,indent=2))
