"""Original CPU oriented-intersection teaching model. Code CC0-1.0.
Not a GPU rasterizer: one analytic ray per pixel, no MSAA or hardware timings.
"""
from pathlib import Path
import json, math, hashlib, platform
import numpy as np
from PIL import Image, PngImagePlugin
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'examples/output'
EPS=1e-7
LIGHT=np.array([-3.,-4.,6.])
LO=np.array([-.65,-.65,0.]); HI=np.array([.65,.65,1.6])

def unit(a):
 a=np.asarray(a,dtype=float)
 return a/np.linalg.norm(a,axis=-1,keepdims=True)

def cube():
 v=np.array([[x,y,z] for z in [0,1.6] for y in [-.65,.65] for x in [-.65,.65]])
 quads=[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]]
 f=[t for a,b,c,d in quads for t in [(a,b,c),(a,c,d)]]
 return v,np.array(f)

def adjacency(f):
 e={}
 for i,tri in enumerate(f):
  for a,b in zip(tri,np.roll(tri,-1)):
   e.setdefault(tuple(sorted((int(a),int(b)))),[]).append((i,int(a),int(b)))
 for uses in e.values():
  assert len(uses)==2,uses
  assert uses[0][1:]==uses[1][1:][::-1],uses
 return e

def volume(v,f,light=LIGHT,k=20.):
 adjacency(f)
 normal=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
 dots=np.sum(normal*(light-v[f[:,0]]),axis=1)
 facing=dots>0
 far=light+k*(v-light); vv=np.concatenate([v,far]); n=len(v)
 front=[tuple(t) for t in f[facing]]
 back=[tuple((t+n)[::-1]) for t in f[facing]]
 sides=[]; sil=[]
 for uses in adjacency(f).values():
  if facing[uses[0][0]]!=facing[uses[1][0]]:
   i,a,b=next(q for q in uses if facing[q[0]])
   sil.append((a,b))
   sides.extend([(b,a,a+n),(b,a+n,b+n)])
 vf=np.array(front+back+sides)
 adjacency(vf)
 return vv,vf,dict(dots=dots.tolist(),light_facing=facing.tolist(),silhouette=sil,front_count=len(front),back_count=len(back),side_count=len(sides),k=k)

def triangle_hits(origin,directions,v,f):
 """Return t and entry(+1)/exit(-1) for all ray/triangle pairs."""
 ts=[]; signs=[]
 for tri in f:
  a,b,c=v[tri];e1=b-a;e2=c-a
  h=np.cross(directions,e2); det=h@e1
  safe=np.abs(det)>1e-12; inv=np.divide(1.,det,out=np.zeros_like(det),where=safe)
  s=origin-a; u=(h@s)*inv; q=np.cross(s,e1);w=(directions@q)*inv;t=np.dot(e2,q)*inv
  hit=safe&(u>=-1e-10)&(w>=-1e-10)&(u+w<=1+1e-10)
  ts.append(np.where(hit,t,np.inf));signs.append(np.where(det>0,1,-1))
 return np.array(ts),np.array(signs)

def slab_shadow(points,light=LIGHT):
 """Independent light-segment/AABB reference; endpoints excluded."""
 d=light-points
 with np.errstate(divide='ignore',invalid='ignore'):
  aa=(LO-points)/d; bb=(HI-points)/d
 lo=np.minimum(aa,bb);hi=np.maximum(aa,bb)
 parallel=np.abs(d)<1e-14
 outside=parallel&((points<LO)|(points>HI))
 lo=np.where(parallel,-np.inf,lo);hi=np.where(parallel,np.inf,hi)
 t0=np.maximum(np.max(lo,axis=1),1e-6)
 t1=np.minimum(np.min(hi,axis=1),1-1e-6)
 return (t0<t1)&~np.any(outside,axis=1)

def rays(camera,target,w=160,h=128):
 fw=unit(np.array(target)-camera);rt=unit(np.cross(fw,[0,0,1.]));up=np.cross(rt,fw)
 # Pixel centers; vertical FOV 50 degrees. Coordinate y down in image.
 xx,yy=np.meshgrid((np.arange(w)+.5-w/2)/(h/2),(h/2-np.arange(h)-.5)/(h/2))
 return unit(fw+math.tan(math.radians(25))*(xx[...,None]*rt+yy[...,None]*up)).reshape(-1,3)

def srgb(x):
 return np.where(x<=.0031308,12.92*x,1.055*x**(1/2.4)-.055)

def save(name,rgb):
 p=OUT/(name+'.png');info=PngImagePlugin.PngInfo();info.add(b'sRGB',b'\x00')
 Image.fromarray(rgb.astype('uint8'),'RGB').save(p,pnginfo=info)
 return dict(file=str(p.relative_to(ROOT)),size=list(Image.open(p).size),sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def render(name,camera,target,light=LIGHT):
 w,h=160,128;camera=np.array(camera,float);d=rays(camera,target,w,h);v,f=cube();vv,vf,geom=volume(v,f,light)
 t,s=triangle_hits(camera,d,v,f);t=np.where(t>.05,t,np.inf)
 idx=np.argmin(t,axis=0);depth=t[idx,np.arange(len(d))]
 norm=unit(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]))[idx]
 floor=np.divide(-camera[2],d[:,2],out=np.full(len(d),np.inf),where=np.abs(d[:,2])>1e-12)
 floorpoint=camera+np.where(np.isfinite(floor),floor,0)[:,None]*d
 floor=np.where((floor>.05)&(np.abs(floorpoint[:,0])<12)&(np.abs(floorpoint[:,1])<12),floor,np.inf)
 isfloor=floor<depth;depth=np.minimum(depth,floor);norm[isfloor]=[0,0,1]
 valid=np.isfinite(depth);p=camera+np.where(valid,depth,0)[:,None]*d
 vt,vs=triangle_hits(camera,d,vv,vf)
 # Duplicated intersections at exact triangulation seams are not allowed silently.
 ordered=np.sort(np.where(vt>.05,vt,np.inf),axis=0)
 with np.errstate(invalid="ignore"):
  gaps=np.diff(ordered,axis=0)
 finite=np.isfinite(ordered[1:])
 duplicate=np.any((np.abs(np.where(finite,gaps,1))<EPS)&finite,axis=0)
 assert not np.any(duplicate&valid),'sample ray hit shared triangle seam'
 before=(vt>.05)&(vt<depth-EPS)&valid
 behind=(vt>=depth-EPS)&np.isfinite(vt)&valid
 zp=np.sum(vs*before,axis=0);zf=np.sum(-vs*behind,axis=0)
 front=geom['front_count'];back=geom['back_count']
 nofar=behind.copy();nofar[front:front+back]=False
 badfar=np.sum(-vs*nofar,axis=0)
 true=slab_shadow(p,light)&valid
 assert np.all((zf[valid]!=0)==true[valid]),name
 assert np.all((zf[valid]>=0)&(zf[valid]<=1))
 ld=unit(light-p);diff=np.maximum(np.sum(norm*ld,axis=1),0)
 checker=((np.floor(p[:,0])+np.floor(p[:,1]))%2)
 albedo=np.tile([.38,.53,.66],(len(d),1));albedo[isfloor]=(.55+.12*checker[isfloor])[:,None]
 def shade(mask):
  linear=albedo*(.13+.87*diff*(~mask))[:,None];rgb=np.rint(np.clip(srgb(linear),0,1)*255).astype('uint8');rgb[~valid]=[227,237,246];return rgb.reshape(h,w,3)
 outputs={}
 for key,mask in [('unshadowed',np.zeros(len(d),bool)),('zfail',zf!=0),('zpass',zp!=0),('no-far-cap',badfar!=0),('truth',true)]:outputs[name+'-'+key]=save(name+'-'+key,shade(mask))
 # Depth is ray distance, not projected hardware depth; interval fixed [0,18].
 gray=np.rint(255*(1-np.clip(np.where(valid,depth,18)/18,0,1))).astype('uint8');gray[~valid]=0
 outputs[name+'-depth']=save(name+'-depth',np.repeat(gray[:,None],3,axis=1).reshape(h,w,3))
 for key,cnt in [('count',zf),('zpass-count',zp)]:
  col=np.tile([235,241,246],(len(d),1));col[cnt>0]=[38,105,151];col[cnt<0]=[183,75,39];col[~valid]=[227,237,246]
  outputs[name+'-'+key]=save(name+'-'+key,col.reshape(h,w,3))
 error=(zp!=0)!=true;ec=np.tile([235,241,246],(len(d),1));ec[error&valid]=[184,45,49]
 outputs[name+'-error']=save(name+'-error',ec.reshape(h,w,3))
 return dict(camera=camera.tolist(),target=target,light=light.tolist(),width=w,height=h,valid=int(valid.sum()),shadow=int(true.sum()),zfail_errors=int(np.sum(((zf!=0)!=true)&valid)),zpass_errors=int(np.sum(error&valid)),missing_far_errors=int(np.sum(((badfar!=0)!=true)&valid)),zpass_counts={str(x):int(np.sum((zp==x)&valid)) for x in np.unique(zp[valid])},camera_inside=bool(slab_shadow(camera[None,:],light)[0]),geometry=geom),outputs

def interval_count(p,start=0,end=10,include_front=True,include_back=True):
 events=[(2,1),(6,-1)];events=[q for q in events if (q[0]!=2 or include_front) and (q[0]!=6 or include_back)]
 return dict(p=p,start=start,end=end,events=events,zpass=sum(s for t,s in events if start<t<p),zfail=sum(-s for t,s in events if p<=t<end),truth=int(2<p<6))

def main():
 OUT.mkdir(exist_ok=True)
 v,f=cube();vv,vf,geom=volume(v,f)
 cases={key:interval_count(**args) for key,args in {'before':{'p':1},'inside':{'p':4},'after':{'p':8},'eye_inside':{'p':4,'start':3},'near_cut':{'p':8,'start':3},'far_cut':{'p':4,'end':5},'no_front':{'p':1,'include_front':False},'no_back':{'p':4,'include_back':False}}.items()}
 wrap=[0];sat=[0]
 for delta in [-1,1]:wrap.append((wrap[-1]+delta)%256);sat.append(min(255,max(0,sat[-1]+delta)))
 overlap=[sum(a<p<b for a,b in [(2,6),(3,7)]) for p in [1,2.5,4,6.5,8]]
 # Exhaustive discrete interval tests: starts outside; end past both events.
 tests=0
 for a in range(1,9):
  for b in range(a+1,11):
   for p2 in range(1,22,2):
    p=p2/2;inside=a<p<b
    zp=sum(s for t,s in [(a,1),(b,-1)] if 0<t<p)
    zf=sum(-s for t,s in [(a,1),(b,-1)] if p<=t<12)
    assert (zp!=0)==inside and(zf!=0)==inside;tests+=1
 render_results={};outputs={}
 for name,cam,target in [('outside',[5,-7,5],[0,0,.6]),('inside',[.8,1.1,.6],[0,-1,.3])]:
  r,o=render(name,cam,target);render_results[name]=r;outputs.update(o)
 r,o=render('other-light',[5,-7,5],[0,0,.6],np.array([4.,-2.,5.]));render_results['other-light']=r;outputs.update(o)
 # Named point for the two distinct geometric paths in figure 01.
 point=np.array([1.,1.,0.]);camera=np.array([5.,-7.,5.]);delta=LIGHT-point
 near=np.minimum((LO-point)/delta,(HI-point)/delta);far=np.maximum((LO-point)/delta,(HI-point)/delta)
 enter=float(max(0,np.max(near)));leave=float(min(1,np.min(far)))
 assert enter<leave and slab_shadow(point[None,:],LIGHT)[0]
 assert not slab_shadow(point[None,:],camera)[0]
 block=point+enter*delta
 demo=dict(P=point.tolist(),C=camera.tolist(),L=LIGHT.tolist(),B=block.tolist(),light_enter=enter,light_leave=leave,eye_blocked=False,light_blocked=True)
 data=dict(ray_demo=demo,version='1.0',python=platform.python_version(),numpy=np.__version__,units='arbitrary scene units',bounds=[LO.tolist(),HI.tolist()],light=LIGHT.tolist(),vertices=v.tolist(),faces=f.tolist(),volume_vertices=vv.tolist(),volume_faces=vf.tolist(),geometry=geom,illustration_far=(LIGHT+2*(v-LIGHT)).tolist(),intervals=cases,wrap=wrap,saturate=sat,overlap=dict(intervals=[[2,6],[3,7]],points=[1,2.5,4,6.5,8],counts=overlap),wrap_256=256%256,interval_tests=tests,renders=render_results,outputs=outputs)
 (ROOT/'examples/results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:{q:v[q] for q in ['valid','shadow','zfail_errors','zpass_errors','missing_far_errors','camera_inside']} for k,v in render_results.items()},indent=2))
if __name__=='__main__':main()
