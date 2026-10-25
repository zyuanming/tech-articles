"""Run the two upstream real images with an explicitly patched compatibility copy.
Original wrapper CC0-1.0. ESA tetra3 / test images retain upstream Apache-2.0.
Requires a local checkout at the pinned commit, never downloads data.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,sys,tempfile,logging
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);args=parser.parse_args()
source=args.source.resolve()
source_sha256={'tetra3/tetra3.py': '0d201443159ac27b61b899a7a814f223e7023bdead67bf32f01240079465aba1', 'tetra3/data/default_database.npz': '4fad84d8d7d922e240abbb557dd6329ed94468c76657eebd4a3d9d042ab0f412', 'LICENSE.txt': '098bcc8a868371332df729fe1221933ae307a6256455fafd39d5c189d0502486', 'README.rst': 'e7526e5082116b19f902d9fb4decd3e8f051de4781022bc1a847c1a70a8b1e99'}
for name,sha in source_sha256.items():
 assert hashlib.sha256((source/name).read_bytes()).hexdigest()==sha, 'Source/database is not the pinned version'
expected={'2019-07-29T204726_Alt40_Azi-135_Try1.tiff':'f5d6c27ac7e8e2114fbeb45196380703e138031819714db7e39f3e101b32b557','2019-07-29T204726_Alt60_Azi-135_Try1.tiff':'f288f6e1fb3a1299626956e3d44740c0260348c65dd9296ac8e07bb27524a5e9'}
with tempfile.TemporaryDirectory(prefix='tetra3-compat-') as temporary:
 runtime=Path(temporary)/'tetra3';shutil.copytree(source/'tetra3',runtime)
 p=runtime/'tetra3.py';s=p.read_text();assert s.count('np.math.factorial')==2
 # The only upstream changes: add math import, replace removed NumPy alias.
 p.write_text(s.replace('import csv\n','import csv\nimport math\n').replace('np.math.factorial','math.factorial'))
 sys.path.insert(0,temporary)
 import tetra3
 t3=tetra3.Tetra3();t3._logger.setLevel(logging.ERROR)
 records=[]
 for name,sha in expected.items():
  inp=source/'examples/data'/name;assert hashlib.sha256(inp.read_bytes()).hexdigest()==sha
  im=Image.open(inp);arr=np.asarray(im,dtype=float);tag='alt40' if 'Alt40' in name else 'alt60'
  solution,images=t3.solve_from_image(im,distortion=[-.2,.1],return_matches=False,return_visual=True,return_images=True,solve_timeout=30000)
  assert solution['Matches'] is not None,'No solution; inspect extraction/calibration.'
  # Display derivative only: full-frame linear percentile stretch, no spatial edits.
  lo,hi=np.percentile(arr,[1,99.9]);display=np.rint(np.clip((arr-lo)/(hi-lo),0,1)*255).astype(np.uint8)
  Image.fromarray(display).save(ROOT/'assets'/('real-'+tag+'-display.png'))
  solution['visual'].save(ROOT/'assets'/('real-'+tag+'-matches.png'))
  if tag=='alt40':
   images['final_centroids'].save(ROOT/'assets'/'real-alt40-centroids.png')
   removed=np.asarray(images['removed_background'])
   mask=np.asarray(images['binary_mask'])
   np.savez_compressed(ROOT/'examples'/'real-alt40-stages.npz',removed_background=removed,binary_mask=mask)
   limits=np.percentile(removed,[1,99.9])
   stage_info={'identity':'Exact returned stage arrays; no pixel editing','shape':list(removed.shape),'removed_dtype':str(removed.dtype),'mask_dtype':str(mask.dtype),'background':'local_mean','filtsize':25,'sigma_mode':'global_root_square','sigma':2,'binary_open':True,'threshold':float(2*np.sqrt(np.mean(removed**2))),'display_percentiles':[1,99.9],'display_limits':[float(x) for x in limits],'mask_true_pixels':int(mask.sum()),'crop_xyxy':[236,278,276,318],'crop_scale':12,'crop_mask_true_pixels':int(mask[278:318,236:276].sum())}
   (ROOT/'examples'/'real-alt40-stages.json').write_text(json.dumps(stage_info,indent=2)+'\n')
  keep=['RA','Dec','Roll','FOV','distortion','RMSE','Matches','epoch_equinox','epoch_proper_motion']
  row={k:(solution[k].item() if hasattr(solution[k],'item') else solution[k]) for k in keep}
  row.update(input=name,input_sha256=sha,display_percentiles=[1,99.9],display_limits=[float(lo),float(hi)])
  records.append(row)
 (ROOT/'examples/real-results.json').write_text(json.dumps({'upstream_commit':'f9fa2eb9a32a5efc529e2d86f0b59f35b1e9028d','identity':'Local execution on upstream real test images, not new observations or attitude ground truth','compatibility':'np.math.factorial replaced by math.factorial in temporary copy; math import added','parameters':{'distortion':[-.2,.1],'solve_timeout_ms':30000,'return_visual':True,'return_images':True},'database':'bundled default_database.npz, hip_main; not redistributed','rows':records},indent=2)+'\n')
print('Two real inputs solved; display derivatives and finite solution summaries written.')
