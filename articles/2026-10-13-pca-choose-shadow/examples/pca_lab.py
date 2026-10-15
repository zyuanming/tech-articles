"""PCA teaching calculations; Python + NumPy + Pillow. No network calls.
Run: python pca_lab.py --out results
Input files are ../originals/iris.data and usgs-iris-versicolor.jpg.
The photo threshold is a selected-pixel example, not botanical recognition.
"""
from pathlib import Path
import argparse,json,math,hashlib,sys
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
TOY=np.array([[8.,19.],[9.,18.],[11.,22.],[12.,21.]])

def pca(x):
 x=np.asarray(x,dtype=float)
 if x.ndim!=2 or len(x)<2 or not np.isfinite(x).all():raise ValueError('finite 2D table, at least 2 rows required')
 mean=x.mean(0);xc=x-mean
 u,s,vt=np.linalg.svd(xc,full_matrices=False)
 # A reproducible display convention only; eigenvector signs have no physical meaning.
 for v in vt:
  if v[np.argmax(np.abs(v))]<0:v*=-1
 return mean,vt,s*s/len(x)

def reconstruction(x,k):
 m,v,e=pca(x);z=(x-m)@v[:k].T;return m+z@v[:k]
def measure(x,angle):
 u=np.array([math.cos(math.radians(angle)),math.sin(math.radians(angle))]);c=x-x.mean(0);z=c@u;rec=z[:,None]*u
 return {'angle_deg':angle,'direction':u.tolist(),'scores':z.tolist(),'projected_variance':float(np.mean(z*z)),'mean_squared_residual':float(np.mean(np.sum((c-rec)**2,axis=1))),'reconstructed':(rec+x.mean(0)).tolist()}
def pack(x):
 m,v,e=pca(x);return {'mean':m.tolist(),'directions':v.tolist(),'variance_population':e.tolist(),'ratios':(e/e.sum()).tolist() if e.sum() else [0.]*len(e),'points':np.asarray(x).tolist()}
def load_iris():
 rows=[s.split(',') for s in (HERE.parent/'originals/iris.data').read_text().splitlines() if s.strip()]
 return np.array([[float(a) for a in r[:4]] for r in rows]),[r[4] for r in rows]
def arrow(d,a,b,color,width=5):
 d.line([a,b],fill=color,width=width);angle=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-16*math.cos(angle-.45),b[1]-16*math.sin(angle-.45)),(b[0]-16*math.cos(angle+.45),b[1]-16*math.sin(angle+.45))],fill=color)
def photo_run(out):
 src=Image.open(HERE.parent/'originals/usgs-iris-versicolor.jpg').convert('RGB');src.thumbnail((900,900),Image.Resampling.LANCZOS);src.save(out/'photo-resized.png')
 rgb=np.array(src);info={}
 for threshold in [45,180]:
  mask=np.max(rgb,axis=2)>threshold;yy,xx=np.nonzero(mask);points=np.column_stack([xx,yy]);m,v,e=pca(points)
  im=Image.fromarray(np.repeat((mask*255).astype('uint8')[:,:,None],3,axis=2));im.save(out/f'photo-mask-{threshold}.png')
  overlay=src.copy();d=ImageDraw.Draw(overlay)
  for k,color in [(0,'#18dc83'),(1,'#f5a943')]:
   delta=v[k]*math.sqrt(e[k])*2; a=m-delta;b=m+delta;d.line([tuple(a),tuple(b)],fill=color,width=6)
  d.ellipse((m[0]-7,m[1]-7,m[0]+7,m[1]+7),fill='white');overlay.save(out/f'photo-axes-{threshold}.png')
  info[str(threshold)]={'selected_pixels':len(points),'mean_xy_pixels':m.tolist(),'principal_directions_image_y_down':v.tolist(),'variance_population_pixel_squared':e.tolist(),'long_axis_angle_deg_mod180':float(math.degrees(math.atan2(v[0,1],v[0,0]))%180)}
 info['working_image_size']=list(src.size);info['original_size']=list(Image.open(HERE.parent/'originals/usgs-iris-versicolor.jpg').size);return info

def run_tests():
 rng=np.random.default_rng(20261013);n=0
 for i in range(200):
  x=rng.normal(size=(30,2))@rng.normal(size=(2,2));m,v,e=pca(x);c=x-m
  assert np.allclose(v@v.T,np.eye(2),atol=1e-12)
  assert np.allclose(reconstruction(x,2),x,atol=1e-11)
  assert abs(np.mean(np.sum(c*c,axis=1))-e.sum())<1e-10
  assert abs(np.mean(np.sum((x-reconstruction(x,1))**2,axis=1))-e[1])<1e-10
  z=c@v[0];assert np.allclose(z[:,None]*v[0],(-z)[:,None]*(-v[0]))
  shift=np.array([100.,-40.]);assert np.allclose(reconstruction(x+shift,1)-shift,reconstruction(x,1),atol=1e-10)
  n+=6
 for i in range(40):
  x=rng.normal(size=(15,2))@rng.normal(size=(2,2));_,_,e=pca(x)
  for angle in np.linspace(0,180,361):assert measure(x,float(angle))['projected_variance']<=e[0]+1e-10
  n+=361
 for a,expect in [(0,2.5),(45,4.5),(-45,.5)]:assert abs(measure(TOY,a)['projected_variance']-expect)<1e-12;n+=1
 assert np.allclose(pca(TOY)[2],[4.5,.5]);n+=1
 assert np.allclose(reconstruction(TOY,1),[[8.5,18.5],[8.5,18.5],[11.5,21.5],[11.5,21.5]]);n+=1
 return {'seed':20261013,'assertions':n,'scope':'finite synthetic 2D inputs; not proof of universal robustness'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=HERE/'results');args=ap.parse_args();out=args.out;out.mkdir(parents=True,exist_ok=True)
 iris,labels=load_iris();assert iris.shape==(150,4)
 m,v,e=pca(iris);recs={str(k):{'mean_squared_residual_cm2':float(np.mean(np.sum((iris-reconstruction(iris,k))**2,axis=1))),'first_row_reconstructed_cm':reconstruction(iris,k)[0].tolist()} for k in [1,2,3,4]}
 centered=TOY-TOY.mean(0);scaled=centered*np.array([1,10]);standard=scaled/scaled.std(0)
 result={'versions':{'python':sys.version.split()[0],'numpy':np.__version__,'pillow':Image.__version__},'toy':pack(TOY),'angles':[measure(TOY,a) for a in [0,45,-45]],'toy_covariance_population':(centered.T@centered/len(TOY)).tolist(),'scaled_y10':pack(scaled),'standardized_after_scale':pack(standard),'outlier':pack(np.vstack([centered,[0,12]])),'iris':{'input_sha256':hashlib.sha256((HERE.parent/'originals/iris.data').read_bytes()).hexdigest(),'shape':list(iris.shape),'feature_order':['sepal length','sepal width','petal length','petal width'],'units':'cm; no standardization','fit_all_150_rows':True,'labels_not_used_in_fit':True,'known_source_discrepancies':'UCI iris.names reports row35 and row38 differences from Fisher; original iris.data retained unchanged',**pack(iris),'scores_2d':((iris-m)@v[:2].T).tolist(),'labels':labels,'reconstruction':recs},'photo':photo_run(out),'tests':run_tests()}
 (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'toy_variance':result['toy']['variance_population'],'iris_ratios':result['iris']['ratios'],'iris_reconstruction':recs,'photo':result['photo'],'tests':result['tests']},indent=2))
if __name__=='__main__':main()
