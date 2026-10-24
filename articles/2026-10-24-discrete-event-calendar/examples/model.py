"""A single-server, non-preemptive FCFS discrete event simulation.
Integer simulated minutes; no wall-clock sleeping or physical printer.
Original code MIT; see sources.md.
"""
from heapq import heappush,heappop
from itertools import count
from collections import deque
from pathlib import Path
import json
JOBS={'A':(0,4),'B':(1,2),'C':(4,1),'D':(8,2)}
def run(departure_first=True):
 events=[];serial=count();waiting=deque();busy=None;trace=[];service=[];waits={};area=0;previous=0
 def schedule(t,kind,name):
  rank=(0 if kind=='完成' else 1) if departure_first else (1 if kind=='完成' else 0)
  heappush(events,(t,rank,next(serial),kind,name))
 def start(t,name):
  nonlocal busy
  busy=name;waits[name]=t-JOBS[name][0];end=t+JOBS[name][1];service.append([name,t,end]);schedule(end,'完成',name)
 for name,(arr,_) in JOBS.items():schedule(arr,'到达',name)
 while events:
  t,priority,eid,kind,name=heappop(events);assert t>=previous
  area+=len(waiting)*(t-previous);previous=t
  if kind=='到达':
   if busy is None:start(t,name)
   else:waiting.append(name)
  else:
   assert busy==name;busy=None
   if waiting:start(t,waiting.popleft())
  trace.append({'t':t,'kind':kind,'job':name,'busy':busy,'queue':list(waiting),'calendar':[[x[0],x[3],x[4]] for x in sorted(events)]})
 assert busy is None and not waiting
 return {'trace':trace,'service':service,'waits':waits,'queue_area':area,'finish':previous,'busy_time':sum(JOBS[n][1] for n in JOBS),'events':len(trace)}
def main():
 d=run();a=run(False);assert d['service']==a['service'];assert d['waits']=={'A':0,'B':3,'C':2,'D':0};assert d['queue_area']==sum(d['waits'].values())==5
 assert (d['finish'],d['busy_time'],d['events'])==(10,9,8)
 d['jobs']=JOBS;d['mean_wait']=sum(d['waits'].values())/len(JOBS);d['arrival_first_trace']=a['trace'];pending=[];current=1;heappush(pending,(2,current));current+=1;heappush(pending,(5,current));cancel_trace=[]
 while pending:
  moment,token=heappop(pending);cancel_trace.append([moment,token,'有效处理' if token==current else '过期忽略'])
 d['cancel_trace']=cancel_trace
 assert cancel_trace==[[2,1,'过期忽略'],[5,2,'有效处理']]
 # Equal-time counterexample: timeout cancels only a still-waiting job.
 def tie(order):
  state='等待'
  for op in order:
   if op=='取走' and state=='等待':state='服务'
   if op=='超时' and state=='等待':state='取消'
  return state
 d['tie_test']=[['先取走',tie(['取走','超时'])],['先超时',tie(['超时','取走'])]]
 assert d['tie_test']==[['先取走','服务'],['先超时','取消']]
 Path(__file__).with_name('results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print({k:d[k] for k in ['service','waits','queue_area','finish','events','mean_wait','tie_test']})
if __name__=='__main__':main()
