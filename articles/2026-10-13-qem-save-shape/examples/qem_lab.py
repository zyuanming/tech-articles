"""Original educational edge-only QEM on an original height field. MIT.
Requires Python 3.12+ and NumPy. Slow, global candidate scan, not a production tool.
"""
from pathlib import Path
import json, math, platform, time
import numpy as np
ROOT = Path(__file__).resolve().parent

def terrain(n=21):
    xy = np.linspace(-1, 1, n)
    vertices = []
    for y in xy:
        for x in xy:
            z = (.68*np.exp(-((x+.38)**2/.085+(y+.12)**2/.17))
                 + .48*np.exp(-((x-.36)**2/.10+(y-.20)**2/.08))
                 + .20*np.exp(-(y-.35*x+.30)**2/.012)*np.exp(-x*x/.65))
            vertices.append([x,y,z])
    faces = []
    for j in range(n-1):
        for i in range(n-1):
            a=j*n+i; b=a+1; c=a+n; d=c+1
            faces += [(a,b,d),(a,d,c)]
    boundary={j*n+i for j in range(n) for i in range(n) if i in (0,n-1) or j in (0,n-1)}
    return np.array(vertices), np.array(faces,dtype=int),boundary

def quadrics(v, faces):
    q=np.zeros((len(v),4,4))
    for a,b,c in faces:
        normal=np.cross(v[b]-v[a],v[c]-v[a]);normal/=np.linalg.norm(normal)
        p=np.append(normal,-normal@v[a]);k=np.outer(p,p)
        for i in (a,b,c): q[i]+=k
    return q

def adjacency(faces):
    incident={};edges={};neighbors={}
    for fi,(a,b,c) in enumerate(faces):
        for v in (a,b,c):incident.setdefault(int(v),set()).add(fi)
        for x,y in ((a,b),(b,c),(c,a)):
            x,y=sorted((int(x),int(y)));edges.setdefault((x,y),[]).append(fi)
            neighbors.setdefault(x,set()).add(y);neighbors.setdefault(y,set()).add(x)
    return incident,edges,neighbors

def legal_position(a,b,p,v,faces,incident):
    for fi in incident[a]|incident[b]:
        ids=faces[fi]
        if a in ids and b in ids:continue  # two incident triangles disappear
        before=v[ids];after=before.copy()
        for j,i in enumerate(ids):
            if i==a or i==b:after[j]=p
        old=np.cross(before[1]-before[0],before[2]-before[0])
        new=np.cross(after[1]-after[0],after[2]-after[0])
        # Positive XY area keeps this special height field single-valued.
        if new[2] <= 1e-10 or old@new <= 1e-12:return False
    return True

def snapshot(v,faces):
    used=np.unique(faces);mapping={int(a):i for i,a in enumerate(used)}
    return {'vertices':v[used].tolist(),'faces':[[mapping[int(a)] for a in f] for f in faces]}

def check_mesh(v,faces,boundary,original):
    incident,edges,_=adjacency(faces)
    assert all(len(fs) in (1,2) for fs in edges.values())
    assert len(incident)-len(edges)+len(faces)==1
    assert set(np.unique([e for e,f in edges.items() if len(f)==1]))==boundary
    assert np.array_equal(v[sorted(boundary)],original[sorted(boundary)])
    areas=np.cross(v[faces[:,1]]-v[faces[:,0]],v[faces[:,2]]-v[faces[:,0]])[:,2]/2
    assert np.all(areas>0) and abs(areas.sum()-4)<1e-9
    assert len(set(tuple(sorted(f)) for f in faces))==len(faces)
    return {'V':len(incident),'E':len(edges),'F':len(faces),'euler':1,'xy_area':float(areas.sum())}

def simplify(method,targets=(400,160)):
    v,faces,boundary=terrain();original=v.copy();q=quadrics(v,faces)
    outputs={str(len(faces)):snapshot(v,faces)};trace=[];metrics={};start=time.perf_counter();rounds=0
    while len(faces)>min(targets):
        incident,edges,neighbors=adjacency(faces);best=None
        for (a,b),shared in sorted(edges.items()):
            if a in boundary or b in boundary or len(shared)!=2:continue
            opposite=set(int(i) for fi in shared for i in faces[fi])-{a,b}
            if neighbors[a]&neighbors[b] != opposite:continue # link condition
            if method=='shortest':
                options=[('midpoint',(v[a]+v[b])/2)];qsum=None
                length=float(np.sum((v[a]-v[b])**2))
            else:
                qsum=q[a]+q[b];options=[('endpoint-a',v[a]),('endpoint-b',v[b]),('midpoint',(v[a]+v[b])/2)]
                matrix=qsum[:3,:3]
                if np.linalg.cond(matrix)<1e10:
                    options.append(('solve',np.linalg.solve(matrix,-qsum[:3,3])))
            for kind,p in options:
                h=np.append(p,1);cost=length if method=='shortest' else max(0.,float(h@qsum@h))
                key=(cost,a,b,kind)
                if best is not None and key>=best[0]:continue
                if legal_position(a,b,p,v,faces,incident):best=(key,p.copy())
        if best is None:raise RuntimeError(f'No legal edge remains at {len(faces)} faces')
        key,p=best;cost,a,b,kind=key
        if rounds<3 or len(faces) in (402,162):
            trace.append({'before_faces':len(faces),'edge':[a,b],'cost':cost,'kind':kind,'old_a':v[a].tolist(),'old_b':v[b].tolist(),'new':p.tolist()})
        v[a]=p;q[a]+=q[b] # preserve old planes; do not recompute from changed triangles
        faces=faces.copy();faces[faces==b]=a
        faces=faces[np.array([len(set(f))==3 for f in faces])]
        rounds+=1
        if len(faces) in targets:
            metrics[str(len(faces))]=check_mesh(v,faces,boundary,original)
            outputs[str(len(faces))]=snapshot(v,faces)
    return {'method':method,'snapshots':outputs,'checks':metrics,'trace':trace,'collapses':rounds,'elapsed_seconds':time.perf_counter()-start}

def sample_height(mesh,points):
    v=np.array(mesh['vertices']);faces=np.array(mesh['faces']);answer=np.full(len(points),np.nan)
    for ids in faces:
        t=v[ids];a,b,c=t[:,:2];matrix=np.column_stack((b-a,c-a));uv=np.linalg.solve(matrix,(points-a).T).T
        mask=(uv[:,0]>=-1e-10)&(uv[:,1]>=-1e-10)&(uv.sum(axis=1)<=1+1e-10)
        answer[mask]=t[0,2]+uv[mask,0]*(t[1,2]-t[0,2])+uv[mask,1]*(t[2,2]-t[0,2])
    assert np.isfinite(answer).all()
    return answer

def run():
    # Direct checks for the compact representation and singular fallback example.
    planes=np.array([[1,0,0,0],[1,0,0,-2],[0,1,0,-1],[0,0,1,-3]],float)
    q=planes.T@planes;h=np.array([1,1,3,1.]);assert abs(h@q@h-2)<1e-12
    assert np.allclose(np.linalg.solve(q[:3,:3],-q[:3,3]),[1,1,3])
    rng=np.random.default_rng(20261013)
    for _ in range(1000):
        h=np.append(rng.normal(size=3),1);assert np.isclose(h@q@h,np.sum((planes@h)**2))
    assert np.linalg.matrix_rank(np.outer([0,0,1,0],[0,0,1,0])[:3,:3])==1
    results={'python':platform.python_version(),'numpy':np.__version__,'coordinate_unit':'dimensionless','grid':21,'original_vertices':441,'original_faces':800,'locked_boundary_vertices':80,'matrix_identity_random_tests':1000}
    points=np.array([(x,y) for y in np.linspace(-1,1,81) for x in np.linspace(-1,1,81)])
    for method in ('qem','shortest'):
        item=simplify(method);reference=sample_height(item['snapshots']['800'],points)
        item['height_error']={};item['height_maps']={}
        for size in ('400','160'):
            err=sample_height(item['snapshots'][size],points)-reference
            item['height_error'][size]={'samples':len(points),'rmse':float(np.sqrt(np.mean(err**2))),'max_abs':float(abs(err).max())}
            item['height_maps'][size]=err.reshape(81,81).tolist()
        results[method]=item
        print(method,item['elapsed_seconds'],item['height_error'],flush=True)
    (ROOT/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    for method in ('qem','shortest'):
        for count,mesh in results[method]['snapshots'].items():
            if method=='shortest' and count=='800':continue
            text=['# Original procedural terrain; coordinates dimensionless']
            text+=['v '+' '.join(f'{a:.12g}' for a in p) for p in mesh['vertices']]
            text+=['f '+' '.join(str(a+1) for a in f) for f in mesh['faces']]
            (ROOT/f'{method}-{count}.obj').write_text('\n'.join(text)+'\n')
    return results
if __name__=='__main__':run()
