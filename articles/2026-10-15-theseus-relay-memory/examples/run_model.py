"""Original teaching model, not a relay-level replica. MIT License, 2026 zyuanming.
N,E,S,W=0,1,2,3. row increases south. A move crosses one open cell edge;
a failed attempt returns to the same centre and is logged separately.
"""
from pathlib import Path
import json, csv
from collections import deque
DXY=((-1,0),(0,1),(1,0),(0,-1)); NAMES='NESW'
CELLS={chr(65+i):(i//3,i%3) for i in range(9)}
REVERSE={v:k for k,v in CELLS.items()}
EDGES=['AB','BC','AD','DE','DG','EF','EH','FI','HI','CF']

def neighbour(cell,d):
 r,c=CELLS[cell]; dr,dc=DXY[d]
 return REVERSE.get((r+dr,c+dc))
def edge(a,b):return ''.join(sorted((a,b)))
def direction(a,b):
 delta=tuple(y-x for x,y in zip(CELLS[a],CELLS[b]));return DXY.index(delta)
def simulate(edges,start='A',goal='C',memory=None,mode='explore',threshold=None,max_moves=200):
 """At each entry, explore rotates CCW; skip the back edge only on that
 first proposal. Walls update the local arrow and rotate again, in either
 mode. Goal mode takes the stored arrow first. Count successful moves only.
 On timeout switch strategy, retaining arrows: this is an explicit model
 convention, not a claim about every historical counter/contact timing.
 """
 memory=dict(memory or {c:3 for c in CELLS});events=[];path=[start];pos=start;back=None;moves=0
 while pos!=goal and moves<max_moves:
  if mode=='goal' and threshold is not None and moves>=threshold:
   events.append(dict(kind='switch',move=moves,cell=pos,mode_before='goal',mode_after='explore'))
   mode='explore'
  proposal=memory[pos]
  skipped=False
  if mode=='explore':
   proposal=(proposal-1)%4
   if proposal==back:proposal=(proposal-1)%4;skipped=True
  for attempt in range(4):
   before=memory[pos];memory[pos]=proposal;dest=neighbour(pos,proposal)
   passed=dest is not None and edge(pos,dest) in edges
   events.append(dict(kind='move' if passed else 'wall',move=moves+int(passed),cell=pos,
    direction=NAMES[proposal],old=NAMES[before],new=NAMES[proposal],target=dest,
    mode=mode,skipped_back=skipped if attempt==0 else False))
   if passed:
    assert edge(pos,dest) in edges
    moves+=1;path.append(dest);back=(proposal+2)%4;pos=dest;break
   proposal=(proposal-1)%4
  else:break  # isolated cell: this model returns rather than running forever
 return dict(path=path,moves=moves,walls=sum(e['kind']=='wall' for e in events),reached=pos==goal,
  memory=memory,events=events,mode=mode)

def follow_last(memory,start,goal,edges):
 out=[start];p=start
 while p!=goal:
  assert len(out)<=len(CELLS),'cycle in final arrows'
  q=neighbour(p,memory[p]);assert q is not None and edge(p,q) in edges
  out.append(q);p=q
 return out

def last_exit(walk):
 return {u:direction(u,v) for u,v in zip(walk,walk[1:])}
def shortest(edges,start,goal):
 queue=deque([[start]]);seen={start}
 while queue:
  p=queue.popleft()
  if p[-1]==goal:return p
  for d in range(4):
   q=neighbour(p[-1],d)
   if q and edge(p[-1],q) in edges and q not in seen:seen.add(q);queue.append(p+[q])
 return None

def all_small_walk_tests():
 # Enumerate every walk of lengths 1..8 in a 2x2 square; stop on first D.
 # This checks the general last-exit fact, independently of our search rule.
 adj={'A':['B','C'],'B':['A','D'],'C':['A','D'],'D':['B','C']};total=0
 def check(path):
  nonlocal total
  if path[-1]=='D':
   mem=dict(zip(path,path[1:]));times={u:i for i,u in enumerate(path[:-1])}
   for start in set(path)-{'D'}:
    p=start;seen=set()
    while p!='D':
     assert p not in seen;seen.add(p);q=mem[p]
     if q!='D':assert times[q]>times[p]
     p=q
   total+=1;return
  if len(path)==9:return
  for q in adj[path[-1]]:check(path+[q])
 check(['A']);return total

def main():
 out=Path(__file__).resolve().parent
 first=simulate(EDGES)
 assert first['path']==list('ADGDEHIFC')
 learned=first['memory'];second=simulate(EDGES,memory=learned,mode='goal',threshold=8)
 assert second['path']==list('ADEHIFC') and second['walls']==0
 for c in set(first['path'])-{'C'}:
  assert follow_last(learned,c,'C',EDGES)[-1]=='C'
  assert learned[c]==last_exit(first['path'])[c]
 unfamiliar=simulate(EDGES,start='B',memory=learned,mode='goal',threshold=8)
 changed=[e for e in EDGES if e!='CF']
 stale=simulate(changed,memory=learned,mode='goal',max_moves=24)
 recovered=simulate(changed,memory=learned,mode='goal',threshold=8)
 assert not stale['reached'] and recovered['reached']
 assert sum(e['kind']=='switch' for e in recovered['events'])==1
 assert next(e for e in recovered['events'] if e['kind']=='switch')['move']==8
 # No shortening optimisation is hidden in the model. BFS is a separate yardstick.
 opt=shortest(EDGES,'A','C');assert opt==list('ABC') and second['moves']>len(opt)-1
 tests=all_small_walk_tests()
 # Exhaust all 2^12 undirected wall configurations on the 3x3 grid.
 all_edges=[edge(a,b) for a in CELLS for d in (1,2) if (b:=neighbour(a,d))]
 connected=0;worst=0
 for mask in range(1<<len(all_edges)):
  es=[e for i,e in enumerate(all_edges) if mask>>i&1]
  if shortest(es,'A','C') is None:continue
  trial=simulate(es,max_moves=1000);assert trial['reached'],(mask,trial)
  assert len(follow_last(trial['memory'],'A','C',es))-1<=8
  connected+=1;worst=max(worst,trial['moves'])
 result=dict(model='deterministic event-level teaching model; not historical hardware measurement',
  grid=CELLS,edges=EDGES,changed_edges=changed,initial_memory={c:'W' for c in CELLS},
  first=first,second=second,unfamiliar=unfamiliar,stale=stale,recovered=recovered,
  shortest_path=opt,last_exit_walk_cases=tests,wall_subsets_tested=4096,
  reachable_subsets=connected,max_moves_in_reachable_subsets=worst)
 (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 with (out/'events.csv').open('w',newline='') as f:
  fields=['case','kind','move','cell','direction','old','new','target','mode','skipped_back','mode_before','mode_after']
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for name in ('first','second','unfamiliar','stale','recovered'):
   for e in result[name]['events']:w.writerow(dict(case=name,**e))
 summary={k:{'path':'-'.join(result[k]['path']),'moves':result[k]['moves'],'walls':result[k]['walls'],'reached':result[k]['reached']} for k in ('first','second','unfamiliar','stale','recovered')}
 summary.update({k:result[k] for k in ('last_exit_walk_cases','reachable_subsets','max_moves_in_reachable_subsets')})
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
