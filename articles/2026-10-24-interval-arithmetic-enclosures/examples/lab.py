"""Exact rational interval examples. Not a floating-point interval package. CC BY 4.0."""
from pathlib import Path
from fractions import Fraction as F
import json,math
from figure import *
P=Path(__file__).resolve().parent;A=P.parent/'assets';M=[]
def add(a,b):return a[0]+b[0],a[1]+b[1]
def sub(a,b):return a[0]-b[1],a[1]-b[0]
def mul(a,b):
 p=[x*y for x in a for y in b];return min(p),max(p)
def sq(a):return (F(0) if a[0]<=0<=a[1] else min(x*x for x in a),max(x*x for x in a))
def div(a,b):
 if b[0]<=0<=b[1]:raise ValueError('denominator interval contains zero')
 return mul(a,(1/b[1],1/b[0]))
x=(F(0),F(1));parts=[]
for n in [1,2,4,8,16]:
 ranges=[mul((F(i,n),F(i+1,n)),sub((F(1),F(1)),(F(i,n),F(i+1,n)))) for i in range(n)]
 parts.append(dict(n=n,bounds=[float(min(r[0] for r in ranges)),float(max(r[1] for r in ranges))]))
D=dict(length=[2,3],width=[4,5],sum=list(add((2,3),(4,5))),area=list(mul((2,3),(4,5))),difference=list(sub((2,3),(2,3))),parts=parts,polynomial=[(i/200,(i/200)*(1-i/200)) for i in range(201)])
assert mul((2,3),(4,5))==(8,15);assert sq((F(-1),F(1)))==(0,1);assert mul((F(-1),F(1)),(F(-1),F(1)))==(-1,1)
# Verify inclusion on a finite grid for the rational primitives (not a general proof).
checks=0
for lo in range(-3,3):
 for hi in range(lo+1,4):
  a=(F(lo),F(hi))
  for lo2 in range(-2,2):
   b=(F(lo2),F(lo2+2))
   for k in range(5):
    u=a[0]+(a[1]-a[0])*F(k,4)
    for l in range(5):
     v=b[0]+(b[1]-b[0])*F(l,4)
     for fn,op in [(add,lambda u,v:u+v),(sub,lambda u,v:u-v),(mul,lambda u,v:u*v)]:
      r=fn(a,b);assert r[0]<=op(u,v)<=r[1];checks+=1
D['grid_assertions']=checks
(P/'data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2));D=json.loads((P/'data.json').read_text())
def save(f,n,s):M.append(f.save(A/f'{n:02}.png',s))
save(rails('读数不是点，而是一段范围',[('长度 / cm',2,3,BLUE),('宽度 / cm',4,5,ORANGE)],(0,6)),1,'两项输入的闭区间含义')
save(rails('相加时，两头各自相加',[('长度',2,3,BLUE),('宽度',4,5,ORANGE),('和',D['sum'][0],D['sum'][1],TEAL)],(0,9)),2,'相加后得到6到8厘米')
f=Fig('面积的四个角都要检查',750);f.text(80,130,'长：2 或 3；宽：4 或 5',42)
for x,y,s in [(160,280,'2 × 4 = 8'),(570,280,'3 × 4 = 12'),(160,480,'2 × 5 = 10'),(570,480,'3 × 5 = 15')]:f.rect((x-25,y-30,x+300,y+80));f.text(x,y,s,40)
save(f,3,'乘法极值来自端点的四种组合')
f=chart('两项输入可以独立变化',[('可行边界',[(2,4),(3,4),(3,5),(2,5),(2,4)],BLUE)],(1.5,3.5),(3.5,5.5),[(2,'2'),(3,'3')],[(4,'4'),(5,'5')],'长度 / cm','宽度 / cm',fill=([(2,4),(3,4),(3,5),(2,5)],'#dcebf2'));save(f,4,'输入集合是矩形，不是概率密度')
save(chart('同一个 x 不能各取各的',[('独立输入',[(2,2),(3,2),(3,3),(2,3),(2,2)],GRAY),('同一输入',[(2,2),(3,3)],BLUE)],(1.8,3.2),(1.8,3.2),[(2,'2'),(3,'3')],[(2,'2'),(3,'3')],'第一处 x','第二处 x'),5,'重复变量只能沿对角线，区间独立代入会扩大集合')
save(rails('平方知道两次是同一个数',[('通用乘法',-1,1,ORANGE),('平方专用',0,1,BLUE)],(-1.3,1.3)),6,'[-1,1]相乘与平方得到不同包围宽度')
save(chart('先保住答案，再谈紧不紧',[('x(1−x)',D['polynomial'],BLUE),('粗上界',[(0,1),(1,1)],ORANGE)],(0,1),(0,1.1),[(0,'0'),(.5,'0.5'),(1,'1')],[(0,'0'),(.5,'0.5'),(1,'1')],'x','函数值'),7,'自然区间延拓给0到1，真实最大值仅1/4')
save(chart('把输入切小，包围就变紧',[('上界',[(r['n'],r['bounds'][1]) for r in D['parts']],ORANGE),('真实最大',[(1,.25),(16,.25)],BLUE)],(1,16),(0,1.1),[(1,'1'),(4,'4'),(8,'8'),(16,'16')],[(0,'0'),(.5,'0.5'),(1,'1')],'分段数','上界'),8,'从一段细分到十六段的实际区间运算')
save(chart('分母跨零，结果不能硬接',[('1/x',[(x,1/x) for x in [-1+i/500 for i in range(450)]],BLUE),('另一支',[(x,1/x) for x in [.1+i/500 for i in range(451)]],ORANGE)],(-1,1),(-11,11),[(-1,'−1'),(0,'0'),(1,'1')],[(-10,'−10'),(0,'0'),(10,'10')],'x','1/x'),9,'跨零除法有断裂且无有限统一上下界')
save(rails('向外舍入，不能四舍五入',[('包住 1/3',.33,.34,BLUE)],(.32,.35)),10,'百分位表示须把精确三分之一夹在0.33与0.34之间')
vals=[('开始',1,2,GRAY),('保留',1,1.5,ORANGE),('再保留',1.375,1.5,BLUE),('更小',1.40625,1.4375,TEAL)]
save(rails('范围收窄，仍保住平方根',vals,(.9,2.1)),11,'对x²−2的带符号端点二分包围')
save(rails('相交的范围，不能硬排队',[('A',1,3,BLUE),('B',2,4,ORANGE),('C',5,6,TEAL)],(0,7)),12,'A与B顺序不确定，但B的所有值都小于C')
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2));print(f'12 figures; {checks} rational-grid inclusion checks')
