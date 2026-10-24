"""Deterministic, single-threaded scheduling model, not a concurrent deque.
Original code: MIT, copyright 2026 zyuanming; see sources.md.
Run: python model.py; output is synthetic time units, not benchmarks.
"""
from collections import deque
from pathlib import Path
import json
COST={'S':1,'L':1,'R':1,'A':4,'B':4,'C':1,'D':1,'J':1}
CHILDREN={'S':['R','L'],'L':['A','B'],'R':['C','D']}
def run(steal):
 q=[deque(['S']),deque()];running=[None,None];done=set();log=[];moves=[];t=0;joined=False
 while 'J' not in done:
  for w in range(2):
   if running[w] is None:
    if q[w]: task=q[w].pop()
    elif steal and q[1-w]:
     task=q[1-w].popleft();moves.append({'time':t,'from':1-w,'to':w,'task':task})
    else:continue
    running[w]=[task,COST[task]];log.append([w,t,t+COST[task],task])
  assert any(running),'deadlock'
  t+=1
  for w in range(2):
   if running[w] is None:continue
   running[w][1]-=1
   if running[w][1]==0:
    task=running[w][0];running[w]=None;done.add(task)
    if task=='S':q[0].append('L');q[1].append('R') # initial split identical in both policies
    else:q[w].extend(CHILDREN.get(task,[]))
  if {'A','B','C','D'}<=done and not joined:q[0].append('J');joined=True
 return {'duration':t,'tasks':log,'steals':moves}
def main():
 a=run(False);b=run(True)
 work=sum(COST.values());span=COST['S']+max(COST['L']+max(COST['A'],COST['B']),COST['R']+max(COST['C'],COST['D']))+COST['J']
 assert (work,span,a['duration'],b['duration'])==(14,7,11,9)
 for r in [a,b]:
  assert sorted(x[3] for x in r['tasks'])==sorted(COST)
  assert sum(z-y for _,y,z,_ in r['tasks'])==work
  assert r['duration']>=max(work/2,span)
 d={'per_task_overhead':1,'costs':COST,'work':work,'span':span,'static':a,'stealing':b,'lower_bound_2':max(work/2,span),'grain':[[g,round(g/(g+1),4)] for g in [1,2,4,8,16]]}
 Path(__file__).with_name('results.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,ensure_ascii=False))
if __name__=='__main__':main()
