"""Original educational implementation, MIT. Python 3. No third-party algorithm code."""
import itertools,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def transform(s):
 assert s.count('$')==1 and s.endswith('$')
 rows=sorted(s[i:]+s[:i] for i in range(len(s)))
 return ''.join(r[-1] for r in rows),rows

def inverse(last):
 first=sorted(last);count={};lf=[]
 for c in last:
  count[c]=count.get(c,0)+1
  lf.append(first.index(c)+count[c]-1)
 row=last.index('$');back=[];trace=[]
 for _ in last:
  back.append(last[row]);trace.append([row,last[row],lf[row]]);row=lf[row]
 return ''.join(back)[::-1],lf,trace

def table_inverse(last):
 rows=['']*len(last);trace=[]
 for _ in last:
  rows=sorted(c+r for c,r in zip(last,rows));trace.append(rows[:])
 return next(r for r in rows if r.endswith('$')),trace

def mtf(s):
 alphabet=sorted(set(s));codes=[];trace=[]
 for c in s:
  before=alphabet[:];k=alphabet.index(c);codes.append(k);alphabet.pop(k);alphabet.insert(0,c)
  trace.append({'char':c,'before':before,'index':k,'after':alphabet[:]})
 check=[];a=sorted(set(s))
 for k in codes:
  c=a.pop(k);a.insert(0,c);check.append(c)
 assert ''.join(check)==s
 return codes,trace

def main():
 s='BANANA$';last,rows=transform(s);back,lf,walk=inverse(last);slow,steps=table_inverse(last);codes,mt=mtf(last)
 assert back==slow==s
 tests=[]
 for n in range(8):
  count=0
  for chars in itertools.product('ABC',repeat=n):
   q=''.join(chars)+'$';l,_=transform(q)
   assert inverse(l)[0]==q and table_inverse(l)[0]==q
   count+=1
  tests.append([n,count])
 comparison=[]
 for q in ['BANANA$','ABABAB$','ABCD$']:
  l,_=transform(q)
  runs=lambda v:sum(i==0 or v[i]!=v[i-1] for i in range(len(v)))
  comparison.append({'input':q,'output':l,'length':len(q),'runs_before':runs(q),'runs_after':runs(l)})
 d={'input':s,'rotations':[s[i:]+s[:i] for i in range(len(s))],'rows':rows,'last':last,'first':''.join(sorted(last)),'lf':lf,'walk':walk,'backward':''.join(x[1] for x in walk),'inverse':back,'table_steps':steps,'mtf_codes':codes,'mtf':mt,'tests':tests,'total':sum(x[1] for x in tests),'comparison':comparison,'python':sys.version.split()[0]}
 (ROOT/'results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print('PASS',d['total'],'roundtrips; LF and table inverse; MTF inverse')
if __name__=='__main__':main()
