#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read only the explicit CMU subject16 ASF/AMC conventions used in this article.
Column vectors; XYZ rotation application is Rz @ Ry @ Rx.
All output points are bone endpoints, not raw optical marker positions.
"""
from pathlib import Path
import math,re,json,sys
import numpy as np
SCALE=(1/.45)*2.54/100

def rot(axis,degree):
 a=math.radians(degree);c=math.cos(a);s=math.sin(a)
 return np.array({'x':[[1,0,0],[0,c,-s],[0,s,c]],'y':[[c,0,s],[0,1,0],[-s,0,c]],'z':[[c,-s,0],[s,c,0],[0,0,1]]}[axis],float)

def rotation(values,order):
 m=np.eye(3)
 for axis,v in zip(order.lower(),values):m=rot(axis,v)@m
 return m

def parse_asf(path):
 text=Path(path).read_text();sections={}
 for part in text.split(':')[1:]:
  lines=[s.strip()for s in part.splitlines()if s.strip()];sections[lines[0].split()[0]]=lines[1:]
 units={s.split()[0]:s.split()[1:]for s in sections['units']};assert units['angle']==['deg'];assert units['length']==['0.45']
 root={s.split()[0]:s.split()[1:]for s in sections['root']}
 assert root['order']==['TX','TY','TZ','RX','RY','RZ'] and root['axis']==['XYZ']
 assert all(float(x)==0 for x in root['position']+root['orientation'])
 blocks=re.findall(r'\bbegin\b(.*?)\bend\b','\n'.join(sections['bonedata']),re.S);bones={}
 for block in blocks:
  fields={p[0]:p[1:]for line in block.splitlines()if(p:=line.split())}
  name=fields['name'][0];axis=[float(v)for v in fields['axis'][:3]];order=fields['axis'][3];assert order=='XYZ'
  dof=fields.get('dof',[]);assert all(v in ['rx','ry','rz']for v in dof)
  bones[name]=dict(direction=np.array(list(map(float,fields['direction']))),length=float(fields['length'][0])*SCALE,axis=axis,dof=dof,C=rotation(axis,order))
 children={};parents={}
 for line in sections['hierarchy']:
  parts=line.split()
  if parts[0]in ['begin','end']:continue
  children[parts[0]]=parts[1:]
  for child in parts[1:]:assert child not in parents;parents[child]=parts[0]
 order=[]
 def walk(name):
  for child in children.get(name,[]):order.append(child);walk(child)
 walk('root');assert set(order)==set(bones) and len(order)==30
 return dict(bones=bones,order=order,parents=parents,names=['root']+order)

def parse_amc(path,skel):
 lines=Path(path).read_text().splitlines();assert ':DEGREES'in lines and ':FULLY-SPECIFIED'in lines
 records=[];current=None;frame_ids=[]
 for line in lines:
  line=line.strip()
  if not line or line[0]in '#:':continue
  p=line.split()
  if len(p)==1:
   frame_ids.append(int(p[0]));current={};records.append(current)
  else:
   assert current is not None and p[0]not in current;current[p[0]]=list(map(float,p[1:]))
 assert frame_ids==list(range(1,len(records)+1))
 names=skel['names'];name_index={n:i for i,n in enumerate(names)};positions=[];root_rotations=[];length_errors=[]
 required={'root',*[name for name,b in skel['bones'].items()if b['dof']]}
 for record in records:
  assert set(record)==required
  root=record['root'];assert len(root)==6
  # Root translations are world-coordinate values, separate from the 3 orientation channels.
  p={'root':np.array(root[:3])*SCALE};r={'root':rotation(root[3:],'XYZ')};root_rotations.append(r['root'])
  for name in skel['order']:
   b=skel['bones'][name];channels=record.get(name,[]);assert len(channels)==len(b['dof'])
   M=rotation(channels,''.join(x[1]for x in b['dof']));parent=skel['parents'][name]
   r[name]=r[parent]@b['C']@M@b['C'].T
   p[name]=p[parent]+r[name]@(b['direction']*b['length'])
   length_errors.append(abs(np.linalg.norm(p[name]-p[parent])-np.linalg.norm(b['direction'])*b['length']))
  positions.append([p[n]for n in names])
 positions=np.asarray(positions);root_rotations=np.asarray(root_rotations)
 assert np.max(length_errors)<1e-12
 assert np.isfinite(positions).all()
 return dict(names=names,positions=positions,root_rotations=root_rotations,frame_count=len(records),max_bone_length_error=float(np.max(length_errors)))

def ground_basis(root_rotation):
 forward=root_rotation@np.array([0.,0.,1.]);forward[1]=0;norm=np.linalg.norm(forward);assert norm>1e-5;forward/=norm
 right=np.cross(forward,np.array([0.,1.,0.]))
 return right,forward

def features(clip,horizon=60):
 pos=clip['positions'];root=pos[:,0];toe_index=clip['names'].index('ltoes');rows=[]
 for i in range(len(pos)-horizon):
  right,forward=ground_basis(clip['root_rotations'][i]);toe=pos[i,toe_index]-root[i];future=root[i+horizon]-root[i]
  rows.append([float(toe@forward),float(future@right),float(future@forward)])
 return np.asarray(rows)

if __name__=='__main__':
 source=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=False,parents=True)
 sk=parse_asf(source/'16.asf');stats={}
 for name in ['16_15','16_17','16_19']:
  clip=parse_amc(source/(name+'.amc'),sk);feat=features(clip)
  np.savez_compressed(out/(name+'.npz'),positions=clip['positions'],root_rotations=clip['root_rotations'],features=feat,names=np.array(clip['names']))
  stats[name]=dict(frame_count=clip['frame_count'],eligible_frames=len(feat),min_xyz=clip['positions'].min(axis=(0,1)).tolist(),max_xyz=clip['positions'].max(axis=(0,1)).tolist(),root_start=clip['positions'][0,0].tolist(),root_end=clip['positions'][-1,0].tolist(),left_toe_y_range=clip['positions'][:,clip['names'].index('ltoes'),1].min().item(),max_bone_length_error=clip['max_bone_length_error'],first_features=feat[0].tolist())
 (out/'parse-summary.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats,indent=2))
