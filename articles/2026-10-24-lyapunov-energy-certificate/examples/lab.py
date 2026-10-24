"""Exact-form teaching oscillator and reproducible figures. CC BY 4.0."""
from pathlib import Path
import math,json
from figure import *
P=Path(__file__).resolve().parent;A=P.parent/'assets';w=math.sqrt(3)/2
def state(t):return math.exp(-t/2)*(math.cos(w*t)+math.sin(w*t)/(2*w)),-math.exp(-t/2)*math.sin(w*t)/w
T=[i/50 for i in range(601)];trace=[dict(t=t,x=state(t)[0],v=state(t)[1],E=sum(q*q for q in state(t))/2) for t in T]
data=dict(model="x'=v, v'=-x-v; dimensionless",initial=[1,0],trace=trace,local=[dict(x=i/100,dV=-(i/100)**2+(i/100)**4) for i in range(-140,141)],euler=[dict(h=i/100,factor=1-i/100+(i/100)**2) for i in range(201)])
assert all(b['E']<=a['E']+1e-14 for a,b in zip(trace,trace[1:]));assert trace[-1]['E']<1e-5
(P/'data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));D=json.loads((P/'data.json').read_text());M=[]
def save(f,n,purpose):M.append(f.save(A/f'{n:02}.png',purpose))
f=Fig('位置和速度一起才是状态',650);f.line([(70,300),(890,300)],GRAY,5);f.rect((70,200,110,300));pts=[(110,250)]+[(120+i*35,225 if i%2==0 else 275) for i in range(12)]+[(545,250)];f.line(pts,BLUE,6);f.rect((545,200,700,300),'#dcebf2');f.dot(575,322,INK,15);f.dot(670,322,INK,15);f.arrow((610,150),(820,150),ORANGE);f.text(710,205,'速度 v',42,ORANGE);f.text(280,380,'弹簧拉回，阻尼耗散',42);f.text(80,480,'位置 x = 1，速度 v = 0',42);save(f,1,'认识弹簧、位置与速度，建立状态对象')
s=[('位置 x',[(r['t'],r['x']) for r in D['trace']],BLUE),('速度 v',[(r['t'],r['v']) for r in D['trace']],ORANGE)]
save(chart('越过原点以后仍会回来',s,(0,12),(-1,1),[(0,'0'),(4,'4'),(8,'8'),(12,'12')],[(-1,'−1'),(0,'0'),(1,'1')],'时间 t','无量纲'),2,'解析模型中位置与速度的变化，不是设备实测')
save(chart('位置起伏，能量却不回涨',[('能量 E',[(r['t'],r['E']) for r in D['trace']],TEAL)],(0,12),(0,.5),[(0,'0'),(4,'4'),(8,'8'),(12,'12')],[(0,'0'),(.25,'0.25'),(.5,'0.5')],'时间 t','E'),3,'同一轨迹的能量单调性')
f=chart('把时间藏进一条状态轨迹',[('有阻尼',[(r['x'],r['v']) for r in D['trace']],BLUE)],(-1.2,1.2),(-1.2,1.2),[(-1,'−1'),(0,'0'),(1,'1')],[(-1,'−1'),(0,'0'),(1,'1')],'位置 x','速度 v');save(f,4,'相平面螺旋表现位置和速度共同收敛')
pts=[(math.cos(i/100),-math.sin(i/100)) for i in range(630)]
save(chart('没有阻尼，就一直绕圈',[('无阻尼',pts,ORANGE)],(-1.2,1.2),(-1.2,1.2),[(-1,'−1'),(0,'0'),(1,'1')],[(-1,'−1'),(0,'0'),(1,'1')],'位置 x','速度 v'),5,'能量恒定的反例：稳定不等于趋于原点')
xx=[i/100 for i in range(-150,151)];save(chart('记账量必须分得清远近',[('x²',[(x,x*x) for x in xx],BLUE),('x',[(x,x) for x in xx],ORANGE)],(-1.5,1.5),(-1.5,2.5),[(-1,'−1'),(0,'0'),(1,'1')],[(-1,'−1'),(0,'0'),(2,'2')],'位置 x','候选量'),6,'正定函数与可能向负无穷下降的量比较')
f=Fig('能量不增，把轨迹圈住',800);cx,cy=480,420
for r,col in [(240,'#e5edf0'),(170,'#cce3e6'),(100,'#abd6d9')]:f.d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=col,outline=TEAL,width=4)
f.bottom=660;f.dot(cx,cy,INK);f.text(75,120,'外圈：E 更大',42);f.text(350,710,'内圈：E 更小',42);f.arrow((700,350),(580,400),BLUE);save(f,7,'能量子水平集给出留在邻域内的几何理由')
save(chart('只在这一段，变化率为负',[('V 的变化率',[(r['x'],r['dV']) for r in D['local']],BLUE)],(-1.4,1.4),(-.3,2),[(-1,'−1'),(0,'0'),(1,'1')],[(0,'0'),(1,'1'),(2,'2')],'位置 x','−x²+x⁴'),8,'局部系统x´=-x+x³的证书仅在绝对值小于1有效')
f=Fig('同一规则，也有不同去向',610);f.line([(100,300),(870,300)],GRAY,4)
for x,label in [(280,'−1'),(480,'0'),(680,'1')]:f.dot(x,300,INK);f.text(x-25,350,label,42)
for a,b in [((230,250),(110,250)),((320,250),(430,250)),((640,250),(530,250)),((730,250),(850,250))]:f.arrow(a,b,BLUE)
f.text(80,450,'圈内回原点，圈外向外走',42);save(f,9,'标明局部吸引域和两个非零平衡点')
save(chart('步长太大，会造出假发散',[('模长平方',[(r['h'],r['factor']) for r in D['euler']],ORANGE)],(0,2),(0,3),[(0,'0'),(1,'1'),(2,'2')],[(0,'0'),(1,'1'),(2,'2'),(3,'3')],'步长 h','1−h+h²'),10,'前向Euler离散特征值模长平方随步长改变')
T=[i/50 for i in range(601)];save(chart('趋近的速度也可能很慢',[('指数衰减',[(t,math.exp(-t)) for t in T],BLUE),('慢衰减',[(t,1/math.sqrt(1+2*t)) for t in T],ORANGE)],(0,12),(0,1),[(0,'0'),(4,'4'),(8,'8'),(12,'12')],[(0,'0'),(.5,'0.5'),(1,'1')],'时间 t','初值均为 1'),11,'x´=-x与x´=-x³不同收敛速度的精确解')
save(chart('一张证书覆盖一片初态',[(f'初值 {a:g}',[(a*r['x'],a*r['v']) for r in D['trace']],col) for a,col in [(.4,TEAL),(.7,ORANGE),(1,BLUE)]],(-1.2,1.2),(-1.2,1.2),[(-1,'−1'),(0,'0'),(1,'1')],[(-1,'−1'),(0,'0'),(1,'1')],'位置 x','速度 v'),12,'有限几条曲线与对所有初态成立的代数证明分开')
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2));print('12 figures; monotone analytic energy checked; no independent review claimed')
