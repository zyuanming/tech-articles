"""Original MIS finite-sum teaching experiment. Code/data CC0-1.0.
The direction grid is the model: its complete sum is not a continuous-integral truth.
"""
from pathlib import Path
from itertools import product
import json,math,hashlib,platform
import numpy as np
from PIL import Image,PngImagePlugin
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'examples/output'

def weights(ps,ns,beta=1):
 ps=np.asarray(ps,float);ns=np.asarray(ns,float)
 q=(ns[:,None]*ps)**beta;den=q.sum(axis=0)
 return np.divide(q,den,out=np.zeros_like(q),where=den>0)

def exact(F,ps,ns,beta=1,constant=False):
 F=np.asarray(F,float);ps=np.asarray(ps,float);ns=np.asarray(ns,int)
 assert np.all(ns>0) and np.all(ps>=0) and np.allclose(ps.sum(axis=1),1)
 assert np.all((ps.sum(axis=0)>0)|(F==0)), 'uncovered contribution'
 w=np.full_like(ps,1/len(ps)) if constant else weights(ps,ns,beta)
 assert np.allclose(w.sum(axis=0)[F!=0],1)
 assert not np.any((ps==0)&(w*F!=0)), 'nonzero weight outside support'
 terms=np.divide(w*F,ps,out=np.zeros_like(ps),where=ps>0)
 means=np.sum(ps*terms,axis=1)
 variance=float(np.sum((np.sum(ps*terms**2,axis=1)-means**2)/ns))
 return dict(mean=float(means.sum()),variance=max(0.,variance),weights=w.tolist(),terms=terms.tolist())

def toy():
 F=[1.,1.];ps=[[.9,.1],[.1,.9]]
 modes={k:exact(F,ps,[1,1],beta=b,constant=c) for k,b,c in [('naive',1,True),('balance',1,False),('power',2,False)]}
 outcomes=[]
 for a,b in product(range(2),repeat=2):
  outcomes.append(dict(A=a,B=b,probability=ps[0][a]*ps[1][b],**{k:v['terms'][0][a]+v['terms'][1][b] for k,v in modes.items()}))
 for k,m in modes.items():
  mean=sum(r['probability']*r[k] for r in outcomes);var=sum(r['probability']*(r[k]-mean)**2 for r in outcomes)
  assert abs(mean-2)<1e-12 and abs(var-m['variance'])<1e-12
 perfect={k:exact([9,1],p,n,beta=b) for k,p,n,b in [('A_only',[ps[0]],[2],1),('balance',ps,[1,1],1),('power',ps,[1,1],2)]}
 split_ps=[[1,0],[0,1]];hole_ps=[[1,0],[1,0]]
 split=exact(F,split_ps,[1,1]);uncovered=False
 try:exact(F,hole_ps,[1,1])
 except AssertionError:uncovered=True
 assert uncovered
 tests=0
 for f0,f1,a,b in product([0.,1.,3.],[0.,1.,4.],[.1,.3,.7,.9],[.1,.4,.6,.9]):
  for ns in [[1,1],[3,1],[1,4]]:
   for beta in [1,2]:
    d=exact([f0,f1],[[a,1-a],[b,1-b]],ns,beta)
    assert abs(d['mean']-(f0+f1))<1e-10;tests+=1
 widths=np.array([.5,.5]);area_density=1.;distance=2.;light_cosine=.5;other_density=.25
 solid=area_density*distance**2/light_cosine
 wrong=sum(exact(F,[p],[1])['mean'] for p in ps)
 assert solid==8 and wrong==4
 uniforms=[.05,.2,.88,.95];choices=[[int(np.searchsorted(np.cumsum(p),u,side='right')) for u in uniforms] for p in ps]
 return dict(F=F,probabilities=ps,widths=widths.tolist(),heights=(np.array(F)/widths).tolist(),densities=(np.array(ps)/widths).tolist(),uniforms=uniforms,choices=choices,modes=modes,outcomes=outcomes,unequal=exact(F,ps,[3,1]),perfect=perfect,support_split=split,support_probabilities=dict(split=split_ps,hole=hole_ps),uncovered_rejected=uncovered,tests=tests,wrong_sum_expectation=wrong,measure=dict(area_density=area_density,distance=distance,light_cosine=light_cosine,solid_angle_density=solid,other_density=other_density,balance_weight=solid/(solid+other_density),P=[0,0],L=[distance*math.sqrt(1-light_cosine**2),distance*light_cosine]))

def unit(a):
 a=np.asarray(a,float);return a/np.linalg.norm(a,axis=-1,keepdims=True)

def sphere_data():
 W,H=160,88
 xx,yy=np.meshgrid((np.arange(W)+.5-W/2)/36,(H/2-np.arange(H)-.5)/36)
 valid=np.zeros((H,W),bool);norm=np.zeros((H,W,3));exponent=np.zeros((H,W));color=np.zeros((H,W,3))
 for cx,m,c in [(-1.12,6,[.65,.8,1.]),(1.12,180,[1.,.65,.35])]:
  x=xx-cx;y=yy;r2=x*x+y*y;mask=r2<.91**2
  n=np.stack([x/.91,y/.91,np.sqrt(np.maximum(0,.91**2-r2))/.91],axis=-1)
  valid|=mask;norm[mask]=n[mask];exponent[mask]=m;color[mask]=c
 nz,nphi=32,64;z,phi=np.meshgrid(-1+(np.arange(nz)+.5)*2/nz,(np.arange(nphi)+.5)*2*np.pi/nphi,indexing='ij')
 directions=np.stack([np.sqrt(1-z*z)*np.cos(phi),np.sqrt(1-z*z)*np.sin(phi),z],axis=-1).reshape(-1,3)
 light=unit([-.45,.55,1.]);dot=directions@light;Le=.08+12*(dot>math.cos(math.radians(13)))
 return dict(width=W,height=H,mask=valid,normals=norm[valid],exponents=exponent[valid],colors=color[valid],directions=directions,Le=Le,light=light)

def pixel_terms(n,m,directions,Le):
 cos=np.maximum(directions@n,0)
 reflection=2*n[2]*n-np.array([0.,0.,1.])
 brdf=.15/np.pi+.85*(m+2)/(2*np.pi)*np.maximum(directions@reflection,0)**m
 kernel=brdf*cos; F=Le*kernel*(4*np.pi/len(Le))
 pL=Le/Le.sum();pB=kernel/kernel.sum()
 return F,np.array([pL,pB])

def draw(p,n,rng):
 c=np.cumsum(p);c[-1]=1.;return np.searchsorted(c,rng.random(n),side='right')

def estimate(F,ps,mode,rng,N=32):
 if mode=='light':return float(np.mean(F[ids:=draw(ps[0],N,rng)]/ps[0,ids]))
 if mode=='brdf':return float(np.mean(F[ids:=draw(ps[1],N,rng)]/ps[1,ids]))
 n=N//2;w=weights(ps,[n,n],1 if mode=='balance' else 2)
 return float(sum(np.mean(w[i,ids:=draw(ps[i],n,rng)]*F[ids]/ps[i,ids]) for i in range(2)))

def rgb(values,mask,colors):
 linear=values[:,None]*colors
 mapped=linear/(1+linear)
 s=np.where(mapped<=.0031308,12.92*mapped,1.055*mapped**(1/2.4)-.055)
 a=np.zeros((*mask.shape,3),dtype=np.uint8);a[:]=[21,30,43];a[mask]=np.rint(np.clip(s,0,1)*255).astype('uint8');return a

def png(name,pixels):
 info=PngImagePlugin.PngInfo();info.add(b'sRGB',b'\x00');p=OUT/(name+'.png');Image.fromarray(pixels.astype('uint8'),'RGB').save(p,pnginfo=info)
 return dict(file=str(p.relative_to(ROOT)),width=pixels.shape[1],height=pixels.shape[0],sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def render():
 g=sphere_data();M=int(g['mask'].sum());methods=['light','brdf','balance','power'];seeds={m:2026102500+i for i,m in enumerate(methods)}
 rngs={m:np.random.default_rng(seeds[m]) for m in methods};values={m:np.zeros(M) for m in methods};ref=np.zeros(M);variances={m:np.zeros(M) for m in methods}
 selected=None
 for j,(n,e) in enumerate(zip(g['normals'],g['exponents'])):
  F,ps=pixel_terms(n,e,g['directions'],g['Le']);ref[j]=F.sum()
  assert abs(ps.sum(axis=1)-1).max()<1e-12 and np.all((ps.sum(axis=0)>0)|(F==0))
  for mode in methods:
   values[mode][j]=estimate(F,ps,mode,rngs[mode])
   if mode in ['light','brdf']:
    i=methods.index(mode);variance=exact(F,[ps[i]],[32])['variance']
   else:variance=exact(F,ps,[16,16],2 if mode=='power' else 1)['variance']
   variances[mode][j]=variance
  if j==M//2:selected=dict(index=j,normal=n.tolist(),exponent=float(e),F=F.tolist(),probabilities=ps.tolist(),reference=float(ref[j]))
 outputs={'reference':png('reference',rgb(ref,g['mask'],g['colors']))};stats={}
 for mode in methods:
  outputs[mode]=png(mode,rgb(values[mode],g['mask'],g['colors']))
  err=np.abs(values[mode]-ref);shown=np.clip(err/.5,0,1)
  a=np.zeros((*g['mask'].shape,3),dtype=np.uint8);a[:]=[21,30,43];a[g['mask']]=np.rint(np.column_stack([shown,np.zeros(M),1-shown])*255).astype('uint8');outputs[mode+'-error']=png(mode+'-error',a)
  stats[mode]=dict(seed=seeds[mode],samples=32,rmse=float(np.sqrt(np.mean((values[mode]-ref)**2))),expected_mse=float(np.mean(variances[mode])),mean_signed_error=float(np.mean(values[mode]-ref)),max_abs_error=float(err.max()))
 # Environment grid is an equal-area z/phi table, not a latitude-longitude photo.
 env=g['Le'].reshape(32,64);gray=env/(1+env);outputs['environment']=png('environment',np.repeat(np.rint(gray*255).astype('uint8')[...,None],3,axis=2))
 payload=dict(reference=ref.tolist(),estimates={k:v.tolist() for k,v in values.items()},variances={k:v.tolist() for k,v in variances.items()},normals=g['normals'].tolist(),exponents=g['exponents'].tolist(),mask=g['mask'].astype(int).tolist(),colors=g['colors'].tolist())
 (ROOT/'examples/render-values.json').write_text(json.dumps(payload,separators=(',',':'))+'\n')
 # Independent seeds per method for a fixed-pixel repeated-trial check.
 trial={};F=np.array(selected['F']);ps=np.array(selected['probabilities'])
 for i,mode in enumerate(methods):
  seed=2026102600+i;rng=np.random.default_rng(seed);v=np.array([estimate(F,ps,mode,rng) for _ in range(4000)])
  theory=variances[mode][M//2];trial[mode]=dict(seed=seed,trials=len(v),mean=float(v.mean()),variance=float(v.var()),theoretical_variance=float(theory),reference=selected['reference'])
 return dict(width=g['width'],height=g['height'],valid_pixels=M,direction_count=len(g['Le']),grid=[32,64],bright_cells=int((g['Le']>.08).sum()),light_direction=g['light'].tolist(),light_half_angle_degrees=13,background_radiance=.08,bright_extra_radiance=12,exponents=[6,180],samples_total=32,mis_samples=[16,16],zoom_box=[98,14,140,54],stats=stats,trial=trial,selected=selected,outputs=outputs,seeds_consumption='Separate PCG64 seed per method; valid pixels row-major; A samples then B samples within pixel for MIS.')

def geometry_case():
 deg=math.pi/180;N=np.array([math.cos(70*deg),math.sin(70*deg)]);wo=np.array([0.,1.]);reflection=2*(N@wo)*N-wo
 angles=np.linspace(0,math.pi,181);directions=np.column_stack([np.cos(angles),np.sin(angles)])
 kernels={}
 for m in [6,180]:
  kernel=(.15/math.pi+.85*(m+2)/(2*math.pi)*np.maximum(directions@reflection,0)**m)*np.maximum(directions@N,0)
  kernels[str(m)]=(kernel/kernel.max()).tolist()
 return dict(normal=N.tolist(),outgoing=wo.tolist(),reflection=reflection.tolist(),incoming=[math.cos(110*deg),math.sin(110*deg)],angles_degrees=(angles/deg).tolist(),relative_kernels=kernels,light_center_degrees=120,light_half_angle_degrees=13,normal_degrees=70,reflection_degrees=math.degrees(math.atan2(reflection[1],reflection[0])),identity='separate 2D direction slice, not a rendered sphere pixel or normalized solid-angle PDF')

def main():
 OUT.mkdir(exist_ok=True);data=dict(version='1.0',python=platform.python_version(),numpy=np.__version__,toy=toy(),render=render(),geometry=geometry_case())
 (ROOT/'examples/results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'toy':data['toy']['modes'],'render':data['render']['stats'],'pixels':data['render']['valid_pixels']},indent=2))
if __name__=='__main__':main()
