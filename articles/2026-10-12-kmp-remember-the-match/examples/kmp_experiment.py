"""Original verification model: code-point exact search, no normalization."""
import itertools,json
from pathlib import Path

def prefix(p):
 pi=[0]*len(p)
 for i in range(1,len(p)):
  j=pi[i-1]
  while j and p[i]!=p[j]:j=pi[j-1]
  if p[i]==p[j]:j+=1
  pi[i]=j
 return pi

def scan(t,p,trace=False):
 if not p:return list(range(len(t)+1)),0,[]
 pi=prefix(p);j=0;out=[];steps=[];comparisons=0
 for i,c in enumerate(t):
  while True:
   comparisons+=1
   if trace:steps.append({'text_i':i,'text':c,'pattern_j':j,'pattern':p[j],'equal':c==p[j]})
   if c==p[j]:
    j+=1
    if j==len(p):out.append(i-len(p)+1);j=pi[j-1]
    break
   if not j:break
   j=pi[j-1]
 return out,comparisons,steps

class StreamMatcher:
 """Exact code-point matcher for a nonempty pattern, across arbitrary chunks."""
 def __init__(self, pattern):
  if not pattern:raise ValueError('stream example requires a nonempty pattern')
  self.pattern=pattern;self.pi=prefix(pattern);self.matched=0;self.consumed=0
 def feed(self, chunk):
  hits=[]
  for char in chunk:
   while self.matched and char!=self.pattern[self.matched]:
    self.matched=self.pi[self.matched-1]
   if char==self.pattern[self.matched]:self.matched+=1
   self.consumed+=1
   if self.matched==len(self.pattern):
    hits.append(self.consumed-len(self.pattern));self.matched=self.pi[self.matched-1]
  return hits

def naive(t,p):
 count=0;out=[]
 for i in range(len(t)-len(p)+1):
  for j,c in enumerate(p):
   count+=1
   if t[i+j]!=c:break
  else:out.append(i)
 return out,count

def words(max_n):
 return [''.join(p) for n in range(max_n+1) for p in itertools.product('AB',repeat=n)]

if __name__=='__main__':
 tests=0
 for t in words(9):
  for p in words(6):
   a,c,_=scan(t,p);b,_=naive(t,p);assert a==b,(t,p,a,b);tests+=1
   if p:assert c<=2*len(t)
 examples=[]
 for t,p in [('ABABABACABA','ABABACA'),('AAAAA','AAA'),('A'*40,'AAAAB'),('甲乙甲乙甲','甲乙甲'),('','A'),('abc',''),('AAAAAC','AAAAAB'),('ABABCABABCAB','ABABCAB')]:
  a,c,tr=scan(t,p,True);b,d=naive(t,p);examples.append({'text':t,'pattern':p,'pi':prefix(p),'matches':a,'search_comparisons_kmp':c,'search_comparisons_naive':d,'trace':tr})
 chunk_tests=0
 for split1 in range(12):
  for split2 in range(split1,12):
   t='ABABABACABA';engine=StreamMatcher('ABABACA');hits=[]
   for part in [t[:split1],t[split1:split2],t[split2:]]:hits.extend(engine.feed(part))
   assert hits==[2];chunk_tests+=1
 result={'stream_three_chunk_partitions':chunk_tests,'status':'PASS','exhaustive_binary_pairs':tests,'text_lengths':'0..9','pattern_lengths':'0..6','empty_pattern_policy':'all n+1 boundaries','units':'Python Unicode code points; exact equality; no normalization/case folding/grapheme segmentation','comparison_count':'search phase only, preprocessing not included','examples':examples}
 Path(__file__).with_name('actual-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('PASS',tests,'pairs; search comparison bound <=2n for nonempty patterns')
 for x in examples:print(x['text'],x['pattern'],x['matches'],x['search_comparisons_kmp'],x['search_comparisons_naive'])
