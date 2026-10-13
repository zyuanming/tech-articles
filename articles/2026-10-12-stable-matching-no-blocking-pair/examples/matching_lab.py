# SPDX-License-Identifier: MIT
"""Original finite two-sided matching experiments; strict complete rankings only."""
import itertools,json,random
from collections import deque
from pathlib import Path

def ranks(preferences):
 return [{candidate:place for place,candidate in enumerate(row)} for row in preferences]

def deferred(left,right,lifo=False):
 n=len(left);rank=ranks(right);next_choice=[0]*n;held=[None]*n;free=deque(range(n));trace=[]
 while free:
  p=free.pop() if lifo else free.popleft();q=left[p][next_choice[p]];next_choice[p]+=1;old=held[q]
  if old is None or rank[q][p]<rank[q][old]:
   held[q]=p;rejected=old
  else:rejected=p
  if rejected is not None:free.append(rejected)
  trace.append({'proposer':p,'receiver':q,'previous':old,'held':held[q],'rejected':rejected,'state':held[:]})
 result=[None]*n
 for q,p in enumerate(held):result[p]=q
 return tuple(result),trace

def blocking(left,right,matching):
 inv={q:p for p,q in enumerate(matching)};rl=ranks(left);rr=ranks(right)
 return [(p,q) for p in range(len(left)) for q in range(len(right)) if rl[p][q]<rl[p][matching[p]] and rr[q][p]<rr[q][inv[q]]]

def stable_all(left,right):
 return [m for m in itertools.permutations(range(len(left))) if not blocking(left,right,m)]

def check_profile(left,right):
 n=len(left);m,t=deferred(left,right);s=stable_all(left,right)
 assert m in s and len(t)<=n*n
 assert len({(x['proposer'],x['receiver']) for x in t})==len(t)
 assert deferred(left,right,True)[0]==m
 rr=ranks(right);rl=ranks(left);last=[None]*n
 for x in t:
  q=x['receiver'];p=x['held']
  if last[q] is not None:assert rr[q][p]<=rr[q][last[q]]
  last[q]=p
 for other in s:
  assert all(rl[p][m[p]]<=rl[p][other[p]] for p in range(n))
 reverse,tr=deferred(right,left);mr=tuple(reverse.index(p) for p in range(n));assert mr in s
 for other in s:
  assert all(rr[q][reverse[q]]<=rr[q][other.index(q)] for q in range(n))
 # Independent rejection claim: no rejected pair occurs in any enumerated stable outcome.
 for x in t:
  p=x['rejected'];q=x['receiver']
  if p is not None:assert all(v[p]!=q for v in s)
 return len(s),len(t)

def run():
 counts={};profiles=0;stable_count=0;hist={};maxproposals=0
 for n in [1,2,3]:
  perms=list(itertools.permutations(range(n)));k=0
  for profile in itertools.product(perms,repeat=2*n):
   s,t=check_profile(profile[:n],profile[n:]);profiles+=1;k+=1;stable_count+=s;maxproposals=max(maxproposals,t)
   if n==3:hist[str(s)]=hist.get(str(s),0)+1
  counts[str(n)]=k
 rng=random.Random(1962)
 for _ in range(1000):
  p=[rng.sample(range(4),4) for _ in range(8)];check_profile(p[:4],p[4:])
 main_left=[[0,1,2],[0,1,2],[1,0,2]];main_right=[[1,2,0],[0,1,2],[0,1,2]]
 match,trace=deferred(main_left,main_right);assert match==(1,0,2) and len(trace)==6
 initial=(0,2,1);bad=blocking(main_left,main_right,initial);assert (1,0) in bad
 side_left=[[0,1],[1,0]];side_right=[[1,0],[0,1]]
 both=stable_all(side_left,side_right);assert both==[(0,1),(1,0)]
 return {'all_profiles_by_n':counts,'total_complete_profiles':profiles,'enumerated_stable_outcomes':stable_count,'n3_stable_count_histogram':hist,'max_proposals_n_le_3':maxproposals,'random_n4_profiles':1000,'random_seed':1962,'main_left':main_left,'main_right':main_right,'main_initial_unstable':initial,'initial_blocking_pairs':bad,'main_result':match,'main_trace':trace,'side_choice_example':{'left':side_left,'right':side_right,'stable':both},'scope':'strict complete equal-size lists; no ties, incomplete lists, capacities, couples or truthful-reporting proof'}

if __name__=='__main__':
 print(json.dumps(run(),indent=2))
