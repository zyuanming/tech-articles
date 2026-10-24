"""Finite checks of independently derived integer predicates. CC BY 4.0."""
from pathlib import Path
import json,platform
rows=[]
for x in range(-20,21):
 result=2*x+1;assert (result>=11)==(x>=5)
 assert (x*x>=9)==(x<=-3 or x>=3)
 y=x if x>=0 else -x;assert y>=0
 rows.append({'x':x,'doubled':2*x,'result':result,'accept':result>=11})
traces=[]
for start in range(8):
 x=start;t=[x]
 while x>0:x-=1;t.append(x)
 assert x==0 and len(t)-1==start
 traces.append(t)
D={'rows':rows,'samples':[r for r in rows if r['x'] in [3,4,5,6,7]],'loops':traces,'square':[{'x':x,'value':x*x,'ok':x*x>=9} for x in range(-5,6)],'checks':len(rows),'python':platform.python_version()}
Path(__file__).with_name('results.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n');print('WP: 41 inputs, square preimages, absolute values, 8 terminating loop traces passed')
