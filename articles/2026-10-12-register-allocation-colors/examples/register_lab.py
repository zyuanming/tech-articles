"""Original educational model; not a production compiler or hardware benchmark."""
from itertools import combinations,product
import json
from pathlib import Path

def graph(n,mask):
 g={i:set() for i in range(n)}
 for bit,(a,b) in enumerate(combinations(range(n),2)):
  if mask>>bit&1:g[a].add(b);g[b].add(a)
 return g

def greedy(g,order,k=None):
 colors={}
 for v in order:
  used={colors[w] for w in g[v] if w in colors};c=next(c for c in range(len(g)+1) if c not in used)
  if k is not None and c>=k:return None
  colors[v]=c
 return colors

def simplify(g,k):
 left=set(g);stack=[]
 while left:
  candidates=[v for v in left if len(g[v]&left)<k]
  if not candidates:return None,stack,sorted(left)
  v=min(candidates);stack.append(v);left.remove(v)
 return greedy(g,reversed(stack),k),stack,[]

def exact(g,k):
 order=sorted(g,key=lambda v:(-len(g[v]),v));c={}
 def go(i):
  if i==len(order):return c.copy()
  v=order[i]
  for color in range(k):
   if all(c.get(w)!=color for w in g[v]):
    c[v]=color;r=go(i+1)
    if r is not None:return r
  c.pop(v,None)
  return None
 return go(0)

def valid(g,c,k):
 return c is not None and set(c)==set(g) and all(0<=a<k for a in c.values()) and all(c[v]!=c[w] for v in g for w in g[v])

# All operands read before the destination write; no fixed hardware registers.
PROGRAM=[('a','input',('x',)),('b','input',('y',)),('c','add',('a','b')),('d','mul',('c','b')),('e','add',('d','c')),(None,'return',('e',))]
def liveness(program):
 after=set();rows=[]
 for dst,op,args in reversed(program):
  uses=set() if op=='input' else set(args)
  before=uses|(after-({dst} if dst else set()))
  rows.append({'dst':dst,'op':op,'uses':sorted(uses),'before':sorted(before),'after':sorted(after)})
  after=before
 return list(reversed(rows))
def interference(program):
 rows=liveness(program);g={dst:set() for dst,op,args in program if dst}
 for row in rows:
  d=row['dst']
  if d:
   for v in set(row['after'])-{d}:g[d].add(v);g[v].add(d)
 return g

def run(x,y,colors=None):
 s={};trace=[]
 def slot(v):return v if colors is None else colors[v]
 for dst,op,args in PROGRAM:
  if op=='input':value={'x':x,'y':y}[args[0]]
  elif op=='return':return s[slot(args[0])],trace
  else:
   a,b=[s[slot(v)] for v in args];value=a+b if op=='add' else a*b
  s[slot(dst)]=value;trace.append({'name':dst,'value':value,'storage':dict(s)})

def spilled(x,y,z):
 # Two actual toy registers; ADD may read one memory source operand.
 # Source b is stored once, then fetched by two later ADD instructions.
 r0=x;r1=y;memory={'slot_b':r1}
 r1=z;r0=r0+memory['slot_b'];r1=r1+memory['slot_b'];r0=r0*r1
 return r0

def main():
 total=success=stuck_colorable=0
 for n in range(1,7):
  for mask in range(1<<(n*(n-1)//2)):
   g=graph(n,mask)
   for k in [1,2,3]:
    c,_,_=simplify(g,k);e=exact(g,k);total+=1
    if c is not None:assert valid(g,c,k) and e is not None;success+=1
    elif e is not None:stuck_colorable+=1
 g=interference(PROGRAM);colors={'a':0,'b':1,'c':0,'d':1,'e':0};assert valid(g,colors,2)
 for x,y in product(range(-10,11),repeat=2):assert run(x,y)[0]==run(x,y,colors)[0]
 cycle={0:{1,3},1:{0,2},2:{1,3},3:{0,2}};assert simplify(cycle,2)[0] is None and valid(cycle,exact(cycle,2),2)
 for x,y,z in product(range(-10,11),repeat=3):assert spilled(x,y,z)==(x+y)*(y+z)
 out={'spill_toy_isa_tests':9261,'spill_x7_y5_z3':spilled(7,5,3),'graph_color_tests':total,'simplify_succeeded':success,'stuck_but_colorable':stuck_colorable,'program_liveness':liveness(PROGRAM),'program_interference':{k:sorted(v) for k,v in g.items()},'program_colors':colors,'program_input_tests':441,'example_x7_y5':run(7,5,colors),'bad_greedy_order':greedy(g,['a','d','b','c','e']),'cycle2colors':exact(cycle,2)}
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
