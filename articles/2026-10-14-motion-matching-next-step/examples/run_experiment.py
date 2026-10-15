#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Four invented candidates and a separate, real CMU-data nearest-neighbor query.
Not a production controller, foot-lock solver, or full inertialization implementation.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,csv,hashlib,json,math,platform
import numpy as np
from parse_cmu import parse_asf,parse_amc,features,ground_basis,rotation,SCALE
FPS=120;HORIZON=60;NAMES=['16_15','16_17','16_19'];SCALES=np.array([.25,1.,1.])

def toy():
 q=[F('0.2'),F('-.6'),F('.8')];scale=[F('.25'),F(1),F(1)]
 vals={'A':['.2','0','1'],'B':['-.2','-.6','.8'],'C':['.1','-.5','.85'],'D':['.2','.6','.8']};rows=[]
 for name,ss in vals.items():
  f=list(map(F,ss));delta=[(v-w)/s for v,w,s in zip(f,q,scale)];terms=[d*d for d in delta]
  rows.append(dict(id=name,features=[float(v)for v in f],normalized_differences=[float(v)for v in delta],squared_terms=[float(v)for v in terms],cost_fraction=str(sum(terms)),cost=float(sum(terms)),trajectory_weight_200_cost=float(terms[0]+200*sum(terms[1:])),incorrect_cm_cost=float((100*(f[0]-q[0])/scale[0])**2+sum(terms[1:])),correct_cm_cost=float(((100*f[0]-100*q[0])/25)**2+sum(terms[1:]))))
 assert [r['cost_fraction']for r in rows]==['2/5','64/25','69/400','36/25']
 assert min(rows,key=lambda r:r['cost'])['id']=='C'
 assert min(rows,key=lambda r:r['trajectory_weight_200_cost'])['id']=='B'
 assert min(rows,key=lambda r:r['incorrect_cm_cost'])['id']=='A'
 assert all(r['cost']==r['correct_cm_cost']for r in rows)
 right_query=[F('.2'),F('.6'),F('.8')]
 right_costs={n:float(sum(((F(v)-qv)/sc)**2 for v,qv,sc in zip(vs,right_query,scale))) for n,vs in vals.items()}
 assert right_costs=={'A':.4,'B':4.,'C':1.3725,'D':0.}
 no_left=[r for r in rows if r['id']in['A','D']];assert min(no_left,key=lambda r:r['cost'])['id']=='A'
 return dict(identity='Invented four-frame teaching feature table; not sampled CMU values',query=[float(v)for v in q],scales=[float(v)for v in scale],rows=rows,winner='C',weight_200_winner='B',incorrect_cm_winner='A',correct_cm_winner='C',missing_left_candidates_winner='A',right_query_costs=right_costs,right_query_winner='D',winner_future_position_error_m=math.sqrt(.1**2+.05**2))

def smooth_offset(t):
 # A scalar position/velocity-offset illustration; no joint rotation or collision solver.
 T=.2;d0=.1;dv=-.2
 if t<0:return d0+dv*t
 if t>=T:return 0.
 s=t/T;return d0*(2*s**3-3*s*s+1)+T*dv*(s**3-2*s*s+s)

def transition():
 rows=[]
 for i in range(-10,41):
  t=i/100;old=.2-.3*t;new=.1-.1*t
  rows.append(dict(time_s=t,old_continuation_m=old,new_continuation_m=new,hard_cut_m=old if t<0 else new,smooth_m=old if t<0 else new+smooth_offset(t)))
 eps=1e-6;d0=(smooth_offset(eps)-smooth_offset(0))/eps;dT=(smooth_offset(.2)-smooth_offset(.2-eps))/eps
 assert abs(smooth_offset(0)-.1)<1e-14 and smooth_offset(.2)==0
 assert abs(d0+.2)<1e-5 and abs(dT)<1e-5
 return dict(identity='Separate invented scalar transition, not captured motion and not a full inertializer',old_at_zero_m=.2,new_at_zero_m=.1,old_velocity_m_s=-.3,new_velocity_m_s=-.1,transition_time_s=.2,offset_initial_m=.1,offset_initial_velocity_m_s=-.2,rows=rows)

def aligned(clip,index,start):
 base=clip['positions'][start,0].copy();base[1]=0
 right,forward=ground_basis(clip['root_rotations'][start]);p=clip['positions'][index]-base
 return np.stack([p@right,p[:,1],p@forward],axis=1)

def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def run(source,out):
 out.mkdir(exist_ok=False,parents=True);sk=parse_asf(source/'16.asf');clips={n:parse_amc(source/(n+'.amc'),sk)for n in NAMES};fs={n:features(c,HORIZON)for n,c in clips.items()}
 assert [clips[n]['frame_count']for n in NAMES]==[471,518,410]
 assert sum(len(fs[n])for n in NAMES)==1219
 # Fixed original AMC frame113, not picked afresh by the nearest-neighbor search.
 source_name='16_15';current=112;query=np.array([fs[source_name][current,0],-.05,.35])
 ranked=[]
 for n in NAMES:
  costs=(((fs[n]-query)/SCALES)**2).sum(axis=1)
  for i,(f,cost)in enumerate(zip(fs[n],costs)):
   terms=((f-query)/SCALES)**2
   ranked.append(dict(clip=n,frame=i+1,features=f.tolist(),squared_terms=terms.tolist(),cost=float(cost)))
 ranked.sort(key=lambda x:(x['cost'],x['clip'],x['frame']));best=ranked[0];assert(best['clip'],best['frame'])==('16_17',244)
 perclip=[next(r for r in ranked if r['clip']==n)for n in NAMES]
 # Rigid world transform invariant: rotate all world points/frames and translate them.
 transform=rotation([0,73,0],'XYZ');translation=np.array([8.,3.,-5.]);max_error=0
 for n,c in clips.items():
  changed=dict(c,positions=c['positions']@transform.T+translation,root_rotations=np.einsum('ij,njk->nik',transform,c['root_rotations']))
  err=float(np.max(abs(features(changed,HORIZON)-fs[n])));max_error=max(max_error,err);assert err<1e-12
 # Do not hide pose differences beyond the one feature: report all-point displacement.
 b=best['frame']-1;oldpose=aligned(clips[source_name],current,current);newpose=aligned(clips[best['clip']],b,b);dist=np.linalg.norm(oldpose-newpose,axis=1);imax=int(dist.argmax())
 evidence=[]
 for name in ['16.asf',*[n+'.amc'for n in NAMES]]:
  buf=(source/name).read_bytes();evidence.append(dict(file=name,bytes=len(buf),sha256=hashlib.sha256(buf).hexdigest()))
 result=dict(environment=dict(python=platform.python_version(),numpy=np.__version__),source_identity='CMU Graphics Lab motion capture ASF/AMC, subject16. FK-derived joint endpoints, not raw camera markers or game screenshots.',units=dict(length_m_per_cmu_unit=SCALE,sample_rate_hz=FPS,future_seconds=.5,future_frame_offset=HORIZON),model_scope='One exhaustive query using three features, no live game, no network, no foot lock, no transition applied to CMU playback',files=evidence,toy=toy(),scalar_transition=transition(),real=dict(frame_counts={n:clips[n]['frame_count']for n in NAMES},eligible_counts={n:len(fs[n])for n in NAMES},total_candidates=len(ranked),query=dict(current_clip=source_name,current_frame=current+1,features=query.tolist(),scales_m=SCALES.tolist(),desired_trajectory_point_is_user_chosen=True,root_identity='unsmoothed ground projection of source hip root; forward from root rotation projected on ground; not Holden simulation-bone preprocessing'),winner=best,best_per_clip=perclip,top20=ranked[:20],current_frame_feature=fs[source_name][current].tolist(),current_frame_cost=float((((fs[source_name][current]-query)/SCALES)**2).sum()),winner_root_target_error_m=float(np.linalg.norm(np.array(best['features'][1:])-query[1:])),winner_left_toe_forward_jump_m=best['features'][0]-query[0],maximum_all_joint_initial_jump_m=float(dist[imax]),maximum_jump_joint=clips[source_name]['names'][imax],rigid_transform_max_feature_error_m=max_error,max_bone_length_error_m=max(c['max_bone_length_error']for c in clips.values())))
 dump(out/'results.json',result)
 with(out/'features.csv').open('w',newline='')as f:
  w=csv.writer(f);w.writerow(['clip','source_frame_1based','left_toe_forward_m','future_right_m','future_forward_m','query_cost'])
  for n in NAMES:
   for i,row in enumerate(fs[n]):w.writerow([n,i+1,*[format(v,'.12g')for v in row],format(float((((row-query)/SCALES)**2).sum()),'.12g')])
 # 30fps display samples only. Calculation and ranking above use all120Hz source frames.
 render=dict(identity='Display samples rounded to 6 decimals; full precision used for scores and checks',names=sk['names'],parents=sk['parents'],whole_clips={},comparison={})
 for n,c in clips.items():
  ids=list(range(0,c['frame_count'],4))
  if ids[-1]!=c['frame_count']-1:ids.append(c['frame_count']-1)
  render['whole_clips'][n]=[dict(source_frame=i+1,time_s=i/FPS,positions=aligned(c,i,0).round(6).tolist())for i in ids]
 for label,n,start in [('current',source_name,current),('selected',best['clip'],b)]:
  render['comparison'][label]=[dict(source_frame=start+j+1,elapsed_s=j/FPS,positions=aligned(clips[n],start+j,start).round(6).tolist())for j in range(0,HORIZON+1,4)]
 dump(out/'render-samples.json',render)
 console='\n'.join(['One offline query; no production motion controller',f'Python {platform.python_version()}; NumPy {np.__version__}','CMU original frames: 471 + 518 + 410 = 1399','Eligible with60 future frames: 411 + 458 + 350 = 1219','Invented four-candidate winner: C; cost0.1725','Real query current: 16_15 frame113',f'Real winner: {best["clip"]} frame{best["frame"]}; cost {best["cost"]:.12f}',f'Future-point error: {result["real"]["winner_root_target_error_m"]:.9f} m',f'Left toe forward jump: {result["real"]["winner_left_toe_forward_jump_m"]:.9f} m',f'Maximum aligned joint jump: {dist[imax]:.9f} m ({clips[source_name]["names"][imax]})',f'Rigid-transform feature error: {max_error:.3g} m','No foot-lock, collision, blend, or new-query processing applied to CMU segment','All checks PASS'])+'\n'
 (out/'stdout.txt').write_text(console);print(console,end='')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.source.resolve(),a.output.resolve())
