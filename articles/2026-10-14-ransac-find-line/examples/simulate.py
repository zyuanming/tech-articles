#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original vertical-residual RANSAC teaching experiments. No network operations."""
from pathlib import Path
import argparse, hashlib, itertools, json, math, platform
import numpy as np
from PIL import Image, __version__ as pillow_version
ROOT=Path(__file__).resolve().parents[1]
POINTS=np.array([[0,1],[1,3.1],[2,4.9],[3,7.1],[4,8.9],[5,11],[6,13.1],[7,14.9],[.5,10],[2.5,0],[4.5,2],[6.5,4]],dtype=float)
NAMES=list('ABCDEFGHIJKL')
def ols(points):
 x,y=points.T;xc=x-x.mean();den=float(xc@xc)
 if den<=0:raise ValueError('OLS needs variation in x')
 a=float(xc@(y-y.mean())/den);return [a,float(y.mean()-a*x.mean())]
def residual(points,ab):return np.abs(points[:,1]-(ab[0]*points[:,0]+ab[1]))
def candidate(points,pair,threshold):
 i,j=map(int,pair);x1,y1=points[i];x2,y2=points[j]
 if x1==x2:return None
 a=float((y2-y1)/(x2-x1));b=float(y1-a*x1);r=residual(points,[a,b]);mask=r<=threshold
 return dict(pair=[i,j],ab=[a,b],count=int(mask.sum()),mask=mask.tolist(),inlier_sse=float(r[mask]@r[mask]))
def ransac(points,threshold,trials,seed):
 rng=np.random.default_rng(seed);best=None;rows=[]
 for k in range(trials):
  c=candidate(points,rng.choice(len(points),2,replace=False),threshold)
  better=c is not None and (best is None or (c['count'],-c['inlier_sse'])>(best['count'],-best['inlier_sse']))
  if better:best=c.copy();best['round']=k+1
  rows.append(dict(round=k+1,candidate=c,best_count=0 if best is None else best['count'],replaced=bool(better)))
 if best is None:raise ValueError('No non-degenerate sample')
 mask=np.array(best['mask']);ab=ols(points[mask]);newmask=residual(points,ab)<=threshold
 return dict(seed=seed,threshold=threshold,trials=trials,rounds=rows,best=best,refit_ab=ab,refit_mask=newmask.tolist(),refit_count=int(newmask.sum()),membership_changed=np.flatnonzero(mask!=newmask).tolist(),all_ols_ab=ols(points))
def photo_points():
 source=ROOT/'originals/usgs-bridges-DSCN0281.jpg'
 im=Image.open(source).convert('RGB').resize((1080,1440),Image.Resampling.LANCZOS)
 gray=np.asarray(im,dtype=float).mean(axis=2)
 xs=np.arange(100,1050,6);gradient=np.abs(gray[881:1001,xs]-gray[879:999,xs]);ys=gradient.argmax(axis=0)+880
 return np.c_[xs,ys].astype(float),np.asarray(im),gradient,gray

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args();out=Path(args.out)
 if out.exists() and any(out.iterdir()):raise SystemExit('Output directory must be empty or absent')
 out.mkdir(parents=True,exist_ok=True)
 main=ransac(POINTS,.25,12,20261074)
 photo,rgb,grad,gray=photo_points();real=ransac(photo,3,100,20261014)
 pairs=list(itertools.combinations(range(12),2));good=[p for p in pairs if p[0]<8 and p[1]<8];q=len(good)/len(pairs);k=math.ceil(math.log(.01)/math.log1p(-q))
 known=[2.,1.];mean_model_error=lambda ab:float(np.mean(((ab[0]-2)*POINTS[:8,0]+ab[1]-1)**2)**.5)
 result=dict(environment=dict(python=platform.python_version(),numpy=np.__version__,pillow=pillow_version),points=[dict(name=n,x=float(x),y=float(y),known_generated_inlier=i<8)for i,(n,(x,y))in enumerate(zip(NAMES,POINTS))],main=main,threshold_counts={str(t):int((residual(POINTS,known)<=t).sum())for t in [.05,.25,8.]},hand_A_F=candidate(POINTS,[0,5],.25),close_C_D=candidate(POINTS,[2,3],.25),probability=dict(all_pairs=len(pairs),true_pairs=len(good),q=q,trials_for_99_percent=k,event_probability_at_9=1-(1-q)**9,event_probability_at_12=1-(1-q)**12,all_true_pairs_with_all_eight_support=sum(candidate(POINTS,p,.25)['mask'][:8]==[True]*8 for p in good)),model_error_over_true_x=dict(all_ols_rms=mean_model_error(main['all_ols_ab']),ransac_refit_rms=mean_model_error(main['refit_ab'])),photo=dict(source_sha256=hashlib.sha256((ROOT/'originals/usgs-bridges-DSCN0281.jpg').read_bytes()).hexdigest(),original_size=[3240,4320],working_size=[1080,1440],roi_xyxy_exclusive=[100,880,1050,1000],column_step=6,points=photo.tolist(),run=real,profile_column=700))
 assert main['best']['count']==8 and main['refit_count']==8 and not main['membership_changed']
 assert len(photo)==159 and real['best']['count']==127 and real['refit_count']==131
 assert result['threshold_counts']=={'0.05':2,'0.25':8,'8.0':11}
 assert k==9 and len(good)==28 and len(pairs)==66
 (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 np.savez_compressed(out/'photo-data.npz',rgb=rgb,gradient=grad,profile_y=np.arange(880,1000),profile_gradient=np.abs(gray[881:1001,700]-gray[879:999,700]))
 (out/'hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(out.iterdir())if p.is_file()},indent=2)+'\n')
 print(json.dumps(dict(main=main['refit_ab'],main_best=main['best'],photo_best=real['best']['count'],photo_refit=real['refit_count'],photo_ab=real['refit_ab'],probability=result['probability'],model_error=result['model_error_over_true_x']),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
