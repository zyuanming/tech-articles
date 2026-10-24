"""Enumerate atomic abstract actions, NOT a C/C++ memory-model implementation.
Original code MIT; see sources.md. No threads, pointers or hardware fences.
"""
from itertools import combinations
from pathlib import Path
import json
def interleavings(a,b):
 for places in combinations(range(len(a)+len(b)),len(a)):
  p=set(places);aa=iter(a);bb=iter(b)
  yield [next(aa) if i in p else next(bb) for i in range(len(a)+len(b))]
def seq_run(order):
 x,y,s=10,20,0;read={};trace=[]
 for op in order:
  if op=='Wbegin':s+=1
  elif op=='Wx':x=11
  elif op=='Wy':y=22
  elif op=='Wend':s+=1
  elif op=='Rbegin':read['begin']=s
  elif op=='Rx':read['x']=x
  elif op=='Ry':read['y']=y
  elif op=='Rend':read['end']=s
  trace.append([op,s,x,y])
 accepted=read['begin']%2==0 and read['begin']==read['end']
 return {'order':order,'read':read,'accepted':accepted,'trace':trace}
def main():
 runs=[seq_run(o) for o in interleavings(['Wbegin','Wx','Wy','Wend'],['Rbegin','Rx','Ry','Rend'])]
 ok=[r for r in runs if r['accepted']]
 assert all((r['read']['x'],r['read']['y']) in [(10,20),(11,22)] for r in ok)
 naive=[]
 for order in interleavings(['Wx','Wy'],['Rx','Ry']):
  x,y=10,20;r={}
  for op in order:
   if op=='Wx':x=11
   if op=='Wy':y=22
   if op=='Rx':r['x']=x
   if op=='Ry':r['y']=y
  naive.append({'order':order,'pair':[r['x'],r['y']]})
 bad=[r for r in naive if r['pair'] not in [[10,20],[11,22]]]
 trace=seq_run(['Rbegin','Rx','Wbegin','Wx','Wy','Wend','Ry','Rend'])
 assert trace['read']=={'begin':0,'x':10,'y':22,'end':2} and not trace['accepted']
 writer_demo=[];ws=0;wx,wy=10,20
 ws+=1;writer_demo.append(['甲开始',ws,f'{wx},{wy}'])
 ws+=1;writer_demo.append(['乙开始',ws,f'{wx},{wy}'])
 wx=11;writer_demo.append(['甲改x',ws,f'{wx},{wy}'])
 writer_demo.append(['读者核验',ws,'错误接纳'])
 assert ws%2==0 and wy!=2*wx
 wraps=[];s=0
 for k in range(2):
  s=(s+1)%4;s=(s+1)%4;wraps.append(s)
 assert s==0
 d={'writer_demo':writer_demo,'total':len(runs),'accepted':len(ok),'rejected':len(runs)-len(ok),'accepted_pairs':sorted(set((r['read']['x'],r['read']['y']) for r in ok)),'naive_total':len(naive),'naive_bad':len(bad),'bad_orders':bad,'collision':trace,'all_interleavings':runs,'wrap_counts':wraps,'two_writers_bad_pair':[11,20]}
 Path(__file__).with_name('results.json').write_text(json.dumps(d,indent=2)+'\n')
 print({k:d[k] for k in ['total','accepted','rejected','accepted_pairs','naive_total','naive_bad','wrap_counts']})
if __name__=='__main__':main()
