"""Original CPU/NumPy demonstration; one primary sample/pixel, no path tracing.
CC BY 4.0, zyuanming. Rebuilds figures 01 and 22; no third-party scene assets.
"""
from pathlib import Path
import json, sys
import numpy as np
from PIL import Image

W,H = 960,720
EPS, BUDGET, TMAX = 0.001,256,30.0

def field(p):
    sphere=np.linalg.norm(p-np.array([-1.25,-0.1,0.0]),axis=-1)-1.0
    q=np.abs(p-np.array([1.25,-0.25,0.1]))-np.array([.8,.85,.8])
    box=np.linalg.norm(np.maximum(q,0),axis=-1)+np.minimum(np.max(q,axis=-1),0)
    t=p-np.array([0.,1.7,0.])
    torus=np.sqrt((np.linalg.norm(t[..., [0,2]],axis=-1)-.72)**2+t[...,1]**2)-.22
    floor=p[...,1]+1.1
    all_d=np.stack([sphere,box,torus,floor],axis=-1)
    return np.min(all_d,axis=-1),np.argmin(all_d,axis=-1)

def main(out):
    out=Path(out);out.mkdir(exist_ok=True,parents=True)
    cam=np.array([5.,3.5,7.]);target=np.array([0.,.5,0.])
    fw=target-cam;fw/=np.linalg.norm(fw)
    right=np.cross(fw,[0.,1.,0.]);right/=np.linalg.norm(right)
    up=np.cross(right,fw)
    x=(np.arange(W)+.5-W/2)/(H/2)
    y=(H/2-np.arange(H)-.5)/(H/2)
    X,Y=np.meshgrid(x,y)
    dirs=fw+(.58*X[...,None])*right+(.58*Y[...,None])*up
    dirs/=np.linalg.norm(dirs,axis=-1,keepdims=True)
    dirs=dirs.reshape(-1,3)
    n=len(dirs); t=np.zeros(n); counts=np.zeros(n,dtype=int)
    active=np.ones(n,dtype=bool);hit=np.zeros(n,dtype=bool)
    for i in range(BUDGET):
        idx=np.flatnonzero(active)
        if not len(idx):break
        d,_=field(cam+t[idx,None]*dirs[idx]);counts[idx]+=1
        good=d<=EPS;hit[idx[good]]=True;active[idx[good]]=False
        step=idx[~good];t[step]+=d[~good]
        active[t>TMAX]=False
    p=cam+t[hit,None]*dirs[hit]
    _,m=field(p)
    normal=np.empty_like(p);h=.0002
    for k in range(3):
        e=np.eye(3)[k]*h
        normal[:,k]=(field(p+e)[0]-field(p-e)[0])/(2*h)
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    light=np.array([-3.,7.,4.]);l=light-p;dist=np.linalg.norm(l,axis=-1);l/=dist[:,None]
    # Separate shadow rays; epsilon and 128-sample shadow cap differ from primary.
    s=np.full(len(p),.004);blocked=np.zeros(len(p),bool);live=np.ones(len(p),bool)
    for _ in range(128):
        idx=np.flatnonzero(live)
        if not len(idx):break
        sd,_=field(p[idx]+normal[idx]*.003+s[idx,None]*l[idx])
        b=sd<.001;blocked[idx[b]]=True;live[idx[b]]=False
        advance=idx[~b];s[advance]+=sd[~b]*.8
        live[s>=dist]=False
    palette=np.array([[.1,.52,.65],[.96,.49,.18],[.8,.23,.3],[.74,.79,.73]])
    material=palette[m]
    floor=m==3
    check=((np.floor(p[:,0])+np.floor(p[:,2])).astype(int)%2)==0
    material[floor&check]*=.88
    diffuse=np.maximum(np.sum(normal*l,axis=-1),0)*(~blocked)
    rgb=np.tile(np.array([.035,.075,.13]),(n,1))
    rgb[hit]=material*(.23+.77*diffuse[:,None])
    # Mild display gamma only; this is not an energy-accurate light solution.
    rgb=np.clip(rgb,0,1)**(1/2.2)
    Image.fromarray(np.uint8(rgb.reshape(H,W,3)*255)).save(out/'01-rendered-scene.png')
    # Absolute evaluation-count colors; black is range clear, magenta is budget.
    bins=np.digitize(counts,[8,16,32,64])
    colors=np.array([[.20,.66,.62],[.49,.75,.39],[.94,.80,.30],[.96,.49,.22],[.70,.16,.19]])
    heat=colors[bins];heat[~hit]=[.1,.16,.22];heat[active]=[1,0,1]
    Image.fromarray(np.uint8(heat.reshape(H,W,3)*255)).save(out/'22-render-step-counts.png')
    report={'python':sys.version.split()[0], 'numpy':np.__version__, 'width':W,'height':H,
            'primary_epsilon':EPS,'primary_budget':BUDGET,'primary_tmax':TMAX,
            'primary_samples_per_pixel':1,'near_pixels':int(hit.sum()),
            'range_clear_pixels':int((~hit&~active).sum()),'budget_pixels':int(active.sum()),
            'primary_distance_queries':int(counts.sum()),'max_queries':int(counts.max()),
            'shadow_budget':128,'shadow_unresolved_pixels':int(live.sum()),
            'note':'CPU vectorized calculation, not a GPU benchmark; unresolved shadows treated as unoccluded.'}
    print(json.dumps(report,indent=2));return report

if __name__=='__main__':
    main(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/'assets')
