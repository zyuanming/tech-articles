"""Independent sequential skip list model, MIT. Counts link inspections, not time."""
from pathlib import Path
import random,json,sys,statistics
P=Path(__file__).resolve().parent
class Node:
 def __init__(self,key,height):self.key=key;self.next=[None]*height
class Skip:
 def __init__(self,maximum=16):self.head=Node(None,maximum);self.level=1
 def predecessors(self,key):
  x=self.head;update=[self.head]*len(self.head.next);trace=[];checks=0
  for layer in range(self.level-1,-1,-1):
   while True:
    y=x.next[layer];checks+=1
    trace.append({'layer':layer+1,'from':x.key,'next':y.key if y else None,'move':bool(y and y.key<key)})
    if y is None or y.key>=key:break
    x=y
   update[layer]=x
  return update,trace,checks
 def find(self,key):
  u,t,c=self.predecessors(key);x=u[0].next[0]
  return bool(x and x.key==key),t,c+1
 def insert(self,key,height):
  assert 1<=height<=len(self.head.next)
  u,_,_=self.predecessors(key)
  if u[0].next[0] and u[0].next[0].key==key:return False
  n=Node(key,height)
  for layer in range(height):n.next[layer]=u[layer].next[layer];u[layer].next[layer]=n
  self.level=max(self.level,height);return True
 def delete(self,key):
  u,_,_=self.predecessors(key);n=u[0].next[0]
  if not n or n.key!=key:return False
  for layer in range(len(n.next)):u[layer].next[layer]=n.next[layer]
  while self.level>1 and self.head.next[self.level-1] is None:self.level-=1
  return True
 def snapshot(self):
  r=[];x=self.head.next[0]
  while x:r.append([x.key,len(x.next)]);x=x.next[0]
  return r
 def validate(self):
  nodes=self.snapshot();keys=[k for k,h in nodes];assert keys==sorted(set(keys))
  for layer in range(self.level):
   expect=[k for k,h in nodes if h>layer];actual=[];x=self.head.next[layer]
   while x:actual.append(x.key);x=x.next[layer]
   assert actual==expect
  return True

def height(rng,p=.5,maximum=16):
 h=1
 while h<maximum and rng.random()<p:h+=1
 return h

def main():
 original=list(zip([4,9,15,21,28,34,42],[1,3,1,2,1,3,1]));s=Skip()
 for k,h in original:s.insert(k,h)
 found,trace,_=s.find(28);assert found
 u,_,_=s.predecessors(25);pred=[x.key for x in u[:s.level]]
 s.insert(25,2);inserted=s.snapshot();s.validate();s.delete(21);deleted=s.snapshot();s.validate()
 rng=random.Random(20261024);q=Skip();truth=set();operations=0
 for _ in range(5000):
  key=rng.randrange(300)
  if rng.random()<.6:q.insert(key,height(rng));truth.add(key)
  else:q.delete(key);truth.discard(key)
  q.validate()
  assert [k for k,h in q.snapshot()]==sorted(truth)
  for target in [key,rng.randrange(300)]:assert q.find(target)[0]==(target in truth)
  operations+=1
 costs=[]
 for n in [64,256,1024,4096]:
  values=[]
  for trial in range(16):
   r=random.Random(20261024+n*31+trial);z=Skip()
   for key in range(n):z.insert(key,height(r))
   for _ in range(256):values.append(z.find(r.randrange(n))[2])
  costs.append({'n':n,'mean':statistics.mean(values),'min':min(values),'max':max(values),'queries':len(values)})
 d={'original':original,'target':28,'trace':trace,'insert_key':25,'insert_height':2,'insert_predecessors':pred,'inserted':inserted,'deleted_key':21,'deleted':deleted,'coin_examples':[['反',1],['正反',2],['正正反',3],['正正正反',4]],'expected_layers':[128*.5**i for i in range(8)],'pointer_expectations':[[.5,2],[.25,4/3]],'costs':costs,'operations_checked':operations,'seed':20261024,'python':sys.version.split()[0]}
 (P/'results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print('PASS',operations,'mixed operations with invariants;',costs)
if __name__=='__main__':main()
