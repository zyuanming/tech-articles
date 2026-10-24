"""Independent Algorithm X / dancing-links model, MIT. Not Knuth's source code."""
from pathlib import Path
import itertools,json,random,sys
P=Path(__file__).resolve().parent
ROWS={'A':[1,2],'B':[1,3],'C':[2,4],'D':[3,5],'E':[4,6],'F':[5,6],'G':[1,4]}
class Node:
 def __init__(self,label,row=None):
  self.label=label;self.row=row;self.L=self.R=self.U=self.D=self;self.C=self;self.size=0
class DLX:
 def __init__(self,columns,rows):
  self.root=Node('root');self.columns={};self.row_node={};self.nodes=[self.root];self.work=0
  for col in columns:
   c=Node(str(col));self.columns[col]=c;self.nodes.append(c);self.link_before(self.root,c,'L','R')
  for name,cols in rows.items():
   first=None
   for col in cols:
    n=Node(name+':'+str(col),name);n.C=self.columns[col];self.nodes.append(n)
    self.link_before(n.C,n,'U','D');n.C.size+=1
    if first:self.link_before(first,n,'L','R')
    else:first=n
   self.row_node[name]=first
 @staticmethod
 def link_before(target,node,prev,nxt):
  setattr(node,prev,getattr(target,prev));setattr(node,nxt,target)
  setattr(getattr(target,prev),nxt,node);setattr(target,prev,node)
 def cover(self,c):
  c.R.L=c.L;c.L.R=c.R;i=c.D
  while i!=c:
   j=i.R
   while j!=i:
    j.D.U=j.U;j.U.D=j.D;j.C.size-=1;self.work+=1;j=j.R
   i=i.D
 def uncover(self,c):
  i=c.U
  while i!=c:
   j=i.L
   while j!=i:
    j.C.size+=1;j.D.U=j;j.U.D=j;j=j.L
   i=i.U
  c.R.L=c;c.L.R=c
 def signature(self):
  return [(n.label,n.L.label,n.R.label,n.U.label,n.D.label,n.C.label,n.size) for n in self.nodes]
 def visible(self):
  result={};c=self.root.R
  while c!=self.root:
   result[c.label]=[];n=c.D
   while n!=c:result[c.label].append(n.row);n=n.D
   c=c.R
  return result
 def solve(self):
  ans=[]
  def visit(chosen):
   if self.root.R==self.root:ans.append(tuple(chosen));return
   c=self.root.R;j=c.R
   while j!=self.root:
    if j.size<c.size:c=j
    j=j.R
   self.cover(c);r=c.D
   while r!=c:
    j=r.R
    while j!=r:self.cover(j.C);j=j.R
    visit(chosen+[r.row]);j=r.L
    while j!=r:self.uncover(j.C);j=j.L
    r=r.D
   self.uncover(c)
  before=self.signature();visit([]);assert self.signature()==before;return sorted(tuple(sorted(a)) for a in ans)
 def force(self,row):
  n=self.row_node[row];covered=[];j=n
  while True:
   self.cover(j.C);covered.append(j.C);j=j.R
   if j==n:break
  return covered

def brute(columns,rows):
 ans=[];names=list(rows)
 for bits in itertools.product([0,1],repeat=len(names)):
  selected=[name for name,b in zip(names,bits) if b];flat=[x for name in selected for x in rows[name]]
  if sorted(flat)==sorted(columns):ans.append(tuple(sorted(selected)))
 return sorted(ans)

def main():
 dlx=DLX(range(1,7),ROWS);original=dlx.signature();forced={}
 for name in ['G','A','B']:
  covered=dlx.force(name);forced[name]=dlx.visible()
  for c in reversed(covered):dlx.uncover(c)
  assert dlx.signature()==original
 sol=dlx.solve();assert sol==brute(range(1,7),ROWS)==[('A','D','E'),('B','C','F')]
 assert forced['G']['2']==[]
 chain=DLX(range(1,7),ROWS);chain_states=[]
 for r in ['A','D','E']:
  chain.force(r);chain_states.append({'chosen':r,'visible':chain.visible()})
 first=DLX(range(1,7),ROWS);first.cover(first.columns[1]);covered_one=first.visible()
 random_checks=0;rng=random.Random(20261024)
 for trial in range(200):
  rows={chr(65+i):[c for c in range(1,5) if rng.random()<.5] for i in range(7)}
  rows={r:cs for r,cs in rows.items() if cs}
  x=DLX(range(1,5),rows);assert x.solve()==brute(range(1,5),rows);random_checks+=1
 data={'chain':chain_states,'covered_one':covered_one,'rows':ROWS,'columns':list(range(1,7)),'solutions':sol,'forced':forced,'initial_visible':DLX(range(1,7),ROWS).visible(),'node_count':len(dlx.nodes),'nonzero_count':sum(map(len,ROWS.values())),'base_subsets':2**len(ROWS),'random_matrices':random_checks,'random_columns':4,'maximum_rows':7,'seed':20261024,'restored_all_node_fields':True,'python':sys.version.split()[0]}
 (P/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('PASS 128 base subsets; 200 random matrices vs brute force; all link fields restored')
if __name__=='__main__':main()
