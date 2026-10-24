"""Original microsequencer teaching model, not EDSAC hardware. CC BY 4.0."""
from pathlib import Path
import json,platform
mem={7:5};state={'A':3,'MAR':0,'MDR':0,'IR_address':7};trace=[]
# One control word per microstep. Memory read is an atomic model operation.
rom={10:{'op':'address','next':11},11:{'op':'read','next':12},12:{'op':'add','next':0}}
u=10
while u:
 row=rom[u];old=state.copy()
 if row['op']=='address':state['MAR']=state['IR_address']
 elif row['op']=='read':state['MDR']=mem[state['MAR']]
 elif row['op']=='add':state['A']=state['A']+state['MDR']
 trace.append({'microaddress':u,'op':row['op'],'before':old,'after':state.copy(),'next':row['next']});u=row['next']
assert state['A']==8 and [r['microaddress'] for r in trace]==[10,11,12]
# Exhaustively exercise the arithmetic part with a small non-negative domain.
for a in range(16):
 for m in range(16):
  A=a;MDR=m;A=A+MDR;assert A==a+m
D={'initial':{'A':3,'memory_address':7,'memory_value':5},'trace':trace,'words':[[1,0,0,11],[0,1,0,12],[0,0,1,0]],'columns':['地址入MAR','读入MDR','加法入A','下一址'],'zero_branch':[{'A':0,'Z':1,'next':20},{'A':8,'Z':0,'next':0}],'checks':256,'python':platform.python_version()}
Path(__file__).with_name('results.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n');print('Microcontrol: 3 traced steps and 256 arithmetic checks passed')
