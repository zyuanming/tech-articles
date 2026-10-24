"""Original majority-vote teaching implementation, MIT."""
from pathlib import Path
from collections import Counter
import itertools,json,sys
P=Path(__file__).resolve().parent

def scan(items):
 candidate=None;count=0;trace=[];pairs=[];stack=[]
 for i,x in enumerate(items):
  if count==0:candidate,count=x,1;stack=[x]
  elif x==candidate:count+=1;stack.append(x)
  else:count-=1;pairs.append([stack.pop(),x])
  trace.append({'i':i+1,'input':x,'candidate':candidate if count else None,'count':count})
 assert count==len(stack) and all(a!=b for a,b in pairs)
 return candidate,count,trace,pairs,stack

def majority(items):
 candidate,count,*_=scan(items)
 if count==0:return None
 actual=sum(x==candidate for x in items)
 return candidate if 2*actual>len(items) else None

def main():
 samples={}
 for key,s in {'main':'ABACAABAA','counter':'AABBC','reorder':'ABCAB','zero':'AB','exercise':'ABCABCA'}.items():
  c,n,t,p,r=scan(s);samples[key]={'input':s,'candidate':c,'remaining':n,'trace':t,'pairs':p,'stack':r,'actual':s.count(c) if c else 0,'answer':majority(s),'counts':dict(Counter(s))}
 tests=[]
 for n in range(10):
  count=0
  for s in itertools.product('ABC',repeat=n):
   freq=Counter(s);answer=next((k for k,v in freq.items() if 2*v>n),None)
   assert majority(s)==answer
   if answer is not None:assert scan(s)[0]==answer
   count+=1
  tests.append([n,count])
 d={'samples':samples,'tests':tests,'total':sum(v for _,v in tests),'mode_counts':{'A':4,'B':3,'C':2},'python':sys.version.split()[0]}
 (P/'results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print('PASS',d['total'],'exact comparisons and majority-candidate invariants')
if __name__=='__main__':main()
