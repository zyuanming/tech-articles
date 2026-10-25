"""Original deterministic star-identification teaching model. CC0-1.0.
Synthetic pixels and a fictional eight-star catalog; not flight software.
"""
from pathlib import Path
from itertools import combinations,permutations
import json,math
import numpy as np
from scipy.ndimage import label
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
P={'width':1024,'height':768,'cx':512.,'cy':384.,'focal_px':2000.,'background':10.,'minimum_area':3,'angle_tolerance_deg':.005,'validation_radius_px':2.}
patch=np.array([[0,10,0],[5,40,15],[0,20,10]],dtype=float)
raw=np.full((P['height'],P['width']),P['background'])
centres=[(532,374),(632,404),(482,484),(402,314)]
gains=[10,8,6,4]
for (x,y),gain in zip(centres,gains):raw[y-1:y+2,x-1:x+2]+=patch*gain
raw[200,800]=4010 # isolated bright defect; distinct from four synthetic star blobs
net=np.maximum(raw-P['background'],0)
regions,n=label(net>0);blobs=[]
for k in range(1,n+1):
 yy,xx=np.where(regions==k);w=net[yy,xx]
 blobs.append({'area':len(w),'flux':float(w.sum()),'x':float(xx@w/w.sum()),'y':float(yy@w/w.sum()),'accepted':bool(len(w)>=P['minimum_area'])})
blobs.sort(key=lambda b:-b['flux']);spots=sorted([b for b in blobs if b['accepted']],key=lambda b:-b['flux'])
uv=np.array([[b['x'],b['y']] for b in spots])
def unit(x):return np.array(x,dtype=float)/np.linalg.norm(x)
def ray(pt):return unit([(pt[0]-P['cx'])/P['focal_px'],(pt[1]-P['cy'])/P['focal_px'],1])
def angle(a,b):return math.degrees(math.atan2(np.linalg.norm(np.cross(a,b)),np.dot(a,b)))
def rz(deg):
 a=math.radians(deg);c,s=math.cos(a),math.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def ry(deg):
 a=math.radians(deg);c,s=math.cos(a),math.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def rx(deg):
 a=math.radians(deg);c,s=math.cos(a),math.sin(a);return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def frame(a,b):
 e1=unit(a);e2=unit(b-np.dot(e1,b)*e1);e3=np.cross(e1,e2)
 return np.column_stack((e1,e2,e3))
def triad(body,sky):return frame(*sky)@frame(*body).T
rays=np.array([ray(pt) for pt in uv]);R=rz(30)@ry(20)@rx(10);S=rz(100)
true_catalog=(R@rays.T).T
false_catalog=(S@true_catalog.T).T
# The second region shares the first triangle but has a displaced fourth star.
false_catalog[3]=S@R@ray(uv[3]+[60,20])
catalog=np.vstack((true_catalog,false_catalog));names=list('ABCDEFGH')
pairs=list(combinations(range(3),2));sig=sorted(angle(rays[i],rays[j]) for i,j in pairs)
coarse=[];candidates=[]
for ids in combinations(range(len(catalog)),3):
 edges=sorted(angle(catalog[ids[i]],catalog[ids[j]]) for i,j in pairs)
 error=max(abs(a-b) for a,b in zip(sig,edges))
 if error>P['angle_tolerance_deg']:continue
 coarse.append({'stars':''.join(names[i] for i in ids),'sorted_angles_deg':edges,'max_error_deg':error})
 for order in permutations(ids):
  err=max(abs(angle(rays[i],rays[j])-angle(catalog[order[i]],catalog[order[j]])) for i,j in pairs)
  if err>P['angle_tolerance_deg']:continue
  est=triad(rays[:2],catalog[list(order[:2])])
  third_error=angle(est@rays[2],catalog[order[2]])
  if third_error>P['angle_tolerance_deg']:continue
  predictions=[]
  for j in range(len(catalog)):
   if j in order:continue
   body=est.T@catalog[j]
   if body[2]<=0:continue
   px=P['cx']+P['focal_px']*body[0]/body[2];py=P['cy']+P['focal_px']*body[1]/body[2]
   predictions.append({'star':names[j],'xy':[px,py],'residual_px':float(np.linalg.norm(np.array([px,py])-uv[3]))})
  best=min(predictions,key=lambda z:z['residual_px'])
  candidates.append({'mapping':''.join(names[i] for i in order),'R_camera_to_sky':est.tolist(),'third_star_residual_deg':third_error,'fourth_best':best,'accepted':best['residual_px']<=P['validation_radius_px']})
assert len(coarse)==2 and len(candidates)==2 and sum(c['accepted'] for c in candidates)==1
winner=next(c for c in candidates if c['accepted']);assert winner['mapping']=='ABC' and winner['fourth_best']['star']=='D'
Rfound=np.array(winner['R_camera_to_sky']);assert np.max(abs(Rfound-R))<1e-12
assert np.max(abs(Rfound.T@Rfound-np.eye(3)))<1e-12 and abs(np.linalg.det(Rfound)-1)<1e-12
assert np.max(abs(uv-(np.array(centres)+.2)))<1e-12
# Quantify selected independent limitations without pretending they model a device.
error_angle_deg=math.degrees(math.atan(.1/P['focal_px']))
condition=[{'separation_deg':a,'inverse_sine':1/math.sin(math.radians(a))} for a in [5,1,.1]]
wrong_f=1600.;wrong_ray=unit([(uv[1,0]-P['cx'])/wrong_f,(uv[1,1]-P['cy'])/wrong_f,1])
permutation_checks=[{'mapping':''.join(names[k] for k in order),'max_edge_error_deg':max(abs(angle(rays[i],rays[j])-angle(catalog[order[i]],catalog[order[j]])) for i,j in pairs)} for order in permutations(range(3))]
new_camera=rz(20)@ry(5)
second_rays=(new_camera.T@rays.T).T
second_pixels=[[P['cx']+P['focal_px']*b[0]/b[2],P['cy']+P['focal_px']*b[1]/b[2]] for b in second_rays]
assert max(abs(angle(rays[i],rays[j])-angle(second_rays[i],second_rays[j])) for i,j in pairs)<1e-10
roll_angle=math.radians(60);off=np.array([120.,0.]);roll_matrix=np.array([[math.cos(roll_angle),-math.sin(roll_angle)],[math.sin(roll_angle),math.cos(roll_angle)]])
result={'roll_demo':{'angle_deg':60,'offset_before':off.tolist(),'offset_after':(roll_matrix@off).tolist()},'permutation_checks':permutation_checks,'second_camera_pixels':second_pixels,'parameters':P,'patch_weights':patch.tolist(),'first_patch_weights':(patch*gains[0]).tolist(),'first_patch_x':list(range(centres[0][0]-1,centres[0][0]+2)),'first_patch_y':list(range(centres[0][1]-1,centres[0][1]+2)),'patch_weight_sum':float(patch.sum()),'patch_local_centroid_xy':[float((patch.sum(axis=0)*np.arange(3)).sum()/patch.sum()),float((patch.sum(axis=1)*np.arange(3)).sum()/patch.sum())],'blobs':blobs,'centroids_xy':uv.tolist(),'camera_rays':rays.tolist(),'catalog_names':names,'catalog_unit_vectors':catalog.tolist(),'triangle_sorted_angles_deg':sig,'all_pair_angles_deg':[{ 'pair':str(i+1)+str(j+1),'degrees':angle(rays[i],rays[j])} for i,j in combinations(range(4),2)],'coarse_candidates':coarse,'candidates':candidates,'camera_frame':frame(*rays[:2]).tolist(),'sky_frame':frame(*true_catalog[:2]).tolist(),'rotation_camera_to_sky':Rfound.tolist(),'boresight_sky':(Rfound@np.array([0,0,1])).tolist(),'synthetic_input_rotation_order':'Rz(30) @ Ry(20) @ Rx(10), rightmost first, column vectors','fov_horizontal_deg':math.degrees(2*math.atan(P['width']/(2*P['focal_px']))),'centroid_error_example':{'pixels':.1,'angle_arcsec':error_angle_deg*3600},'conditioning':condition,'wrong_focal_example':{'wrong_focal_px':wrong_f,'star2_ray_error_deg':angle(rays[1],wrong_ray)},'assertions':'centroids, two candidates, one fourth-star survivor, orthogonal proper rotation and recovered synthetic truth passed'}
(ROOT/'examples/results.json').write_text(json.dumps(result,indent=2)+'\n')
# Actual model image, explicit linear display mapping, not a camera photograph.
Image.fromarray(np.rint(raw).astype(np.uint16)).save(ROOT/'examples/synthetic-sensor.tiff')
print('Synthetic extraction, catalog search, verification and TRIAD checks passed.')
