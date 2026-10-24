"""Finite, reliable, asynchronous termination-detector teaching model.
Parent/ack variant inspired by Dijkstra-Scholten; not EWD684 cornet code.
All states are in memory. Exhaustively explores this fixed 3-task input only.
Original code MIT; see sources.md.
"""
from pathlib import Path
from copy import deepcopy
import json
NAMES=['R','A','B']
def initial():
 s={'nodes':{n:{'parent':None,'queue':[],'out':[]} for n in NAMES},'flight':[],'sent':0,'completed':0,'acks':0}
 send(s,'R','A','a');send(s,'R','B','b');return s
def send(s,src,dst,task):
 s['sent']+=1;mid=s['sent'];s['nodes'][src]['out'].append(mid);s['flight'].append(['work',src,dst,mid,task])
def release(s,n):
 v=s['nodes'][n]
 if n!='R' and not v['queue'] and not v['out'] and v['parent'] is not None:
  src,mid=v['parent'];s['flight'].append(['ack',n,src,mid,'']);v['parent']=None
def moves(s):
 return [('deliver',i) for i in range(len(s['flight']))]+[('run',n) for n in NAMES if s['nodes'][n]['queue']]
def step(s,move):
 s=deepcopy(s);kind,k=move
 if kind=='deliver':
  typ,src,dst,mid,task=s['flight'].pop(k);v=s['nodes'][dst]
  if typ=='work':
   engaged=dst=='R' or v['parent'] is not None
   if engaged:s['flight'].append(['ack',dst,src,mid,''])
   else:
    assert not v['queue'] and not v['out'];v['parent']=[src,mid]
   v['queue'].append(task)
  else:
   assert mid in v['out'];v['out'].remove(mid);s['acks']+=1;release(s,dst)
 else:
  v=s['nodes'][k];task=v['queue'].pop(0);s['completed']+=1
  if task=='a':send(s,'A','B','c')
  release(s,k)
 check(s);return s

def detected(s):return not s['nodes']['R']['queue'] and not s['nodes']['R']['out']
def check(s):
 assert sum(len(v['out']) for v in s['nodes'].values())==s['sent']-s['acks']
 for n,v in s['nodes'].items():
  assert len(set(v['out']))==len(v['out'])
  if n!='R' and (v['queue'] or v['out']):assert v['parent'] is not None
  seen={n};cur=n
  while cur!='R' and s['nodes'][cur]['parent'] is not None:
   cur=s['nodes'][cur]['parent'][0];assert cur not in seen;seen.add(cur)
 if detected(s):
  assert all(not v['queue'] and not v['out'] and v['parent'] is None for v in s['nodes'].values())
  assert not s['flight'] and s['completed']==3

def key(s):
 t=deepcopy(s);t['flight'].sort()
 for v in t['nodes'].values():v['out'].sort()
 return json.dumps(t,sort_keys=True)
def explore():
 seen=set();todo=[initial()];ends=0;max_debt=0
 while todo:
  s=todo.pop();k=key(s)
  if k in seen:continue
  seen.add(k);check(s);max_debt=max(max_debt,sum(len(v['out']) for v in s['nodes'].values()));ms=moves(s)
  if not ms:assert detected(s);ends+=1
  todo.extend(step(s,m) for m in ms)
 return {'states':len(seen),'terminal_states':ends,'max_outstanding':max_debt,'false_positive':0}
def example():
 s=initial();trace=[deepcopy(s)];labels=['R发送两件工作后空闲']
 def act(m,label):
  nonlocal s
  s=step(s,m);trace.append(deepcopy(s));labels.append(label)
 def deliver(typ,mid,label):
  i=next(i for i,m in enumerate(s['flight']) if m[0]==typ and m[3]==mid);act(('deliver',i),label)
 deliver('work',1,'A接收首次工作')
 deliver('work',2,'B接收首次工作')
 act(('run','A'),'A完成并向B派生工作')
 deliver('work',3,'B已挂在树上，回追加回执')
 deliver('ack',3,'A收到追加回执，回父回执')
 deliver('ack',1,'R收到A回执，仍等B')
 act(('run','B'),'B完成第一件，仍有一件')
 act(('run','B'),'B完成第二件，回父回执')
 deliver('ack',2,'R收到最后回执，检测结束')
 assert detected(s)
 return labels,trace
if __name__=='__main__':
 labels,trace=example();single=0;single_rows=[['发送前',single]];single+=1;single_rows.extend([['工作已发出',single],['对方收到',single]]);single-=1;single_rows.append(['回执收到',single]);d={'single_debt':single_rows,'exploration':explore(),'labels':labels,'trace':trace,'debt_rows':[[i]+[len(s['nodes'][n]['out']) for n in NAMES] for i,s in enumerate(trace)]}
 Path(__file__).with_name('results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(d['exploration']);print(d['debt_rows'])
