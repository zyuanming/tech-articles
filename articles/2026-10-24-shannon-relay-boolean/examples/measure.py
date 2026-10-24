"""CC BY 4.0. Ideal contact logic; no electrical simulation or measurement."""
from itertools import product
from pathlib import Path
import json
rows=[]
for a,b,c in product([0,1],repeat=3):
 left=(a and b) or (a and c);right=a and (b or c)
 assert left==right
 rows.append(dict(a=a,b=b,c=c,ab=a and b,ac=a and c,F=int(left),G=int(right)))
pairs=[]
for a,b in product([0,1],repeat=2):
 assert not(a or b)==((not a) and (not b))
 assert (a or (a and b))==bool(a)
 pairs.append(dict(a=a,b=b,AND=a and b,OR=a or b,XOR=int(a!=b),NOT_OR=int(not(a or b))))
# Arbitrary teaching time units, not milliseconds or a measured relay.
# A command changes at t=2; old complementary contact opens at3, new closes at5.
trace=[dict(t=t,command=int(t>=2),new=int(t>=5),old=int(t<3),output=int(t>=5 or t<3)) for t in range(8)]
d=dict(rows=rows,pairs=pairs,contacts_before=4,contacts_after=3,trace=trace,trace_units='arbitrary teaching units; not measured')
Path(__file__).with_name('results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('PASS: 8 equivalent states; 4 pair states; illustrative non-simultaneous contacts')
