"""Independent 64-bit HLL teaching model, MIT. Not HLL++, not a product codec."""
from pathlib import Path
import hashlib,json,math,statistics,sys
P=Path(__file__).resolve().parent

def rank(word,bits):
 assert 0<=word<(1<<bits)
 return bits-word.bit_length()+1

def registers(items,p=10,salt=0):
 assert 4<=p<=16
 M=[0]*(1<<p);q=64-p;mask=(1<<q)-1
 for item in items:
  word=int.from_bytes(hashlib.sha256(f'{salt}:{item}'.encode('ascii')).digest()[:8],'big')
  bucket=word>>q;r=rank(word&mask,q);M[bucket]=max(M[bucket],r)
 return M

def alpha(m):
 assert m>=16 and m&(m-1)==0
 return {16:.673,32:.697,64:.709}.get(m,.7213/(1+1.079/m))
def estimate(M):
 m=len(M);raw=alpha(m)*m*m/sum(2.0**(-r) for r in M);empty=M.count(0)
 return m*math.log(m/empty) if raw<=2.5*m and empty else raw

def main():
 toy=[('A','0101','001010'),('B','0101','100101'),('C','1010','000100'),('A','0101','001010'),('D','0101','000010'),('E','0010','010011')]
 tm=[0]*16;trace=[]
 for name,pre,suffix in toy:
  j=int(pre,2);r=rank(int(suffix,2),len(suffix));old=tm[j];tm[j]=max(old,r)
  trace.append({'id':name,'prefix':pre,'suffix':suffix,'bucket':j,'rank':r,'before':old,'after':tm[j]})
 manual=[1,2,2,3]*4;sum_inverse=sum(2**(-r) for r in manual);manual_raw=alpha(16)*16**2/sum_inverse
 assert abs(manual_raw-38.28622222222222)<1e-10
 base=registers(range(1000));duplicate=registers(list(range(1000))*5);assert base==duplicate
 left=registers(range(15000));right=registers(range(10000,25000));merged=list(map(max,left,right));union=registers(range(25000));assert merged==union
 trials=[]
 for p in [8,10]:
  m=1<<p;errs=[]
  for salt in range(32):
   estimate_n=estimate(registers(range(20000),p,salt));errs.append((estimate_n-20000)/20000)
  trials.append({'p':p,'m':m,'n':20000,'relative_errors':errs,'mean':statistics.mean(errs),'std':statistics.stdev(errs),'min':min(errs),'max':max(errs),'asymptotic_reference':1.04/math.sqrt(m)})
 data={'toy_trace':trace,'toy_registers':tm,'toy_unique':len(set(x[0] for x in toy)),'manual_registers':manual,'manual_denominator':sum_inverse,'manual_raw':manual_raw,'alpha16':alpha(16),'empty_raw':alpha(16)*16,'empty_corrected':estimate([0]*16),'small_examples':[[v,16*math.log(16/v)] for v in [16,15,8]],'probabilities':[[k,2.0**-k] for k in range(1,7)],'harmonic_example':{'values':[2,4,4,128],'arithmetic':(2+4+4+128)/4,'harmonic':4/(1/2+1/4+1/4+1/128)},'merged_estimate':estimate(merged),'left_estimate':estimate(left),'right_estimate':estimate(right),'union_true':25000,'merge_vector_excerpt':[left[:8],right[:8],merged[:8]],'duplicate_exact_state':True,'trials':trials,'typical_errors':[[m,1.04/math.sqrt(m)] for m in [64,256,1024,4096]],'python':sys.version.split()[0]}
 (P/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('PASS duplicate invariance and exact register union; manual',manual_raw)
 for t in trials:print('m',t['m'],'mean',t['mean'],'std',t['std'],'range',t['min'],t['max'])
 print('union',data['merged_estimate'],'left+right',data['left_estimate']+data['right_estimate'])
if __name__=='__main__':main()
