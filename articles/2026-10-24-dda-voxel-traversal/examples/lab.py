"""Exact rational grid traversal and independent slab verification. MIT."""
from pathlib import Path
from fractions import Fraction as F
import json,math,platform
import numpy as np
from figurelib import *
P=Path(__file__).resolve().parents[1];A=P/'assets';M=[]
def traverse(o,d,end=F(4)):
 o=list(map(F,o));d=list(map(F,d));cell=[math.floor(x) for x in o];step=[1 if x>0 else -1 if x<0 else 0 for x in d]
 # Negative movement starting exactly on boundary belongs to the immediately entered cell.
 for k in range(len(o)):
  if d[k]<0 and o[k].denominator==1:cell[k]-=1
 delta=[abs(1/x) if x else None for x in d]
 ts=[(F(cell[k]+1 if d[k]>0 else cell[k])-o[k])/d[k] if d[k] else None for k in range(len(o))]
 t=F(0);out=[]
 while t<end:
  n=min([x for x in ts if x is not None]+[end]);out.append({'cell':cell.copy(),'enter':str(t),'exit':str(n),'next':[str(x) if x is not None else 'inf' for x in ts]})
  if n>=end:break
  for k in range(len(o)):
   if ts[k]==n:cell[k]+=step[k];ts[k]+=delta[k]
  t=n
 return out
O=[F(1,5),F(3,10)];D=[F(1),F(3,5)];trace=traverse(O,D)
# Independent cell/line slab intersection; no incremental states shared.
def reference(o,d,end):
 lo=[math.floor(min(o[k],o[k]+end*d[k]))-1 for k in range(2)];hi=[math.ceil(max(o[k],o[k]+end*d[k]))+1 for k in range(2)];out=[]
 for i in range(lo[0],hi[0]):
  for j in range(lo[1],hi[1]):
   enter=F(0);leave=end;ok=True
   for k,c in enumerate([i,j]):
    if d[k]==0:
     if not c<=o[k]<c+1:ok=False
    else:
     x=(F(c)-o[k])/d[k];y=(F(c+1)-o[k])/d[k];enter=max(enter,min(x,y));leave=min(leave,max(x,y))
   if ok and enter<leave:out.append((enter,[i,j]))
 return [c for t,c in sorted(out)]
cases=0
for ox in [F(1,5),F(1),F(-1,3)]:
 for oy in [F(3,10),F(1),F(-2,3)]:
  for dx in [F(-1),F(0),F(1),F(3,5)]:
   for dy in [F(-1),F(0),F(1),F(3,5)]:
    if not(dx or dy):continue
    got=[z['cell'] for z in traverse([ox,oy],[dx,dy])];assert got==reference([ox,oy],[dx,dy],F(4)),(ox,oy,dx,dy,got);cases+=1
v={'origin':list(map(float,O)),'direction':list(map(float,D)),'end':4,'trace':trace,'negative':traverse([F(19,5),F(27,10)],[-F(1),-F(3,5)]),'corner':traverse([F(1,2),F(1,2)],[1,1],F(2)),'three_d':traverse(O+[F(2,5)],D+[F(1,4)]),'checks':cases,'versions':{'python':platform.python_version()}}
(P/'examples/results.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');v=json.loads((P/'examples/results.json').read_text())
def save(f,n,p,id='原创几何示意'):M.append(f.save(A/n,p,id))
def scene(title,active=None,o=None,d=None,tend=4,cell=140,nx=6,ny=4):
 f=Fig(title);o=np.array(v['origin'] if o is None else o);d=np.array(v['direction'] if d is None else d);base=(60,150);bottom=150+ny*cell
 def xy(p):return(base[0]+p[0]*cell,bottom-p[1]*cell)
 for j in range(ny):
  for i in range(nx):f.rect((base[0]+i*cell,bottom-(j+1)*cell,base[0]+(i+1)*cell,bottom-j*cell),fill='#d4e8ef' if active and [i,j] in active else None,outline='#bac5cb',width=2)
 f.arrow(xy(o),xy(o+tend*d),RED,6);f.dot(*xy(o),10,INK)
 for i in range(nx+1):f.text(base[0]+i*cell-15,bottom+18,str(i))
 for j in range(ny+1):f.text(12,bottom-j*cell-18,str(j))
 f.text(915,bottom+85,'x');f.text(15,90,'y');return f,xy,bottom
f,xy,b=scene('射线经过哪些格子？',[s['cell'] for s in trace]);f.rect((xy([3,2])[0],xy([3,2])[1],xy([4,1])[0],xy([4,1])[1]),fill=None,outline=GREEN,width=7);save(f,'01-route.png','按事件计算得到的实际访问格序列','原创程序运行结果')
f,xy,b=scene('固定步长会跨过短短一段格子')
for t in np.arange(0,4.1,1.3):f.dot(*xy(np.array(v['origin'])+t*np.array(v['direction'])),13,BLUE)
f.rect((xy([1,1])[0],xy([1,1])[1],xy([2,0])[0],xy([2,0])[1]),outline=GREEN,width=7);save(f,'02-fixed-step.png','固定参数步长1.3漏掉射线短暂经过的格(1,0)')
f,xy,b=scene('t 是行程参数，不一定是米')
for t in [0,1,2,3]:
 p=xy(np.array(v['origin'])+t*np.array(v['direction']));f.dot(*p,10,BLUE);f.text(p[0]+5,p[1]-62,f't={t}')
save(f,'03-parameter.png','参数增量与坐标位移对应')
for idx,n,title in [(0,'04-first-x.png','先碰 x = 1 的竖边'),(1,'05-first-y.png','再碰 y = 1 的横边')]:
 s=trace[idx];f,xy,b=scene(title,[s['cell']],tend=float(F(s['exit'])),cell=260,nx=3,ny=2);f.text(65,b+90,'t = '+s['exit']);save(f,n,'连续两次边界事件的计算状态')
f=Fig('两张时间表，只更新刚跨过的轴')
for j,s in enumerate(trace[:5]):
 y=140+j*110;f.text(45,y,str(tuple(s['cell'])));f.text(280,y,'x: '+s['next'][0]);f.text(610,y,'y: '+s['next'][1])
save(f,'06-ledger.png','实际精确分数状态表，便于核对增量更新','原创程序运行结果')
f,xy,b=scene('向左走：下一条边在当前格左侧',[s['cell'] for s in v['negative']],o=[3.8,2.7],d=[-1,-.6],tend=3.7);save(f,'07-negative.png','负向射线及对应访问格')
f,xy,b=scene('某个方向为零，就不跨它的边',[[i,1] for i in range(5)],o=[.2,1.5],d=[1,0]);f.text(65,b+90,'y 的下一次事件：∞');save(f,'08-zero.png','零分量不做除零，事件设为无穷')
f,xy,b=scene('恰好碰角：同时跨过两条边',[[0,0],[1,1],[2,2]],o=[.5,.5],d=[1,1],tend=2.5);f.dot(*xy([1,1]),17,GREEN);save(f,'09-corner.png','正长度遍历约定跳过只触及角点的邻格')
f=Fig('从网格外来，先找进入盒子的时刻');f.rect((250,170,830,620),fill='#e4edf0');f.arrow((60,540),(900,280),RED);f.dot(250,481,13,GREEN);f.text(60,660,'起点在外');f.text(380,660,'入口：再初始化格号');save(f,'10-entry.png','包围盒裁剪与网格初始化顺序示意')
f=Fig('三维只是多一张 z 时间表')
def iso(p):x,y,z=p;return(480+70*(x-y),620-35*(x+y)-70*z)
for j,s in enumerate(v['three_d']):
 x,y,z=s['cell'];corners=[iso([x+u,y+w,z+h]) for u,w,h in [(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]]
 for i,k in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:f.line([corners[i],corners[k]],BLUE,3)
f.arrow(iso([.2,.3,.4]),iso([4.2,2.7,1.4]),RED,7);f.text(60,700,'每次比较：tX、tY、tZ');save(f,'11-three-d.png','实际三维访问立方格投影','原创程序运行结果')
f=Fig('进入一个格，不等于击中里面的物体');grid(f,140,150,3,2,210);f.d.ellipse((390,190,530,330),fill='#479484');f.arrow((80,490),(870,350),RED,6);f.text(80,650,'射线穿过中格，绕开圆形物体');save(f,'12-candidate.png','网格候选与物体精确交点的区别')
f=Fig('格宽改变，跨格所需 t 也改变');f.rect((100,180,850,470));f.line([(350,180),(350,470)],BLUE);f.line([(600,180),(600,470)],BLUE);f.arrow((130,400),(800,280),RED);f.text(100,540,'格宽 h：Δt = h / |d|');f.text(100,620,'本文单位格：h = 1');save(f,'13-cell-size.png','一般格宽对跨轴时间增量的作用')
f=Fig('检查不是只看一条漂亮路径');f.text(70,150,f"精确分数用例：{v['checks']}");f.text(70,235,'正向 / 负向 / 零分量');f.text(70,320,'边界起点 / 对角同时跨轴');f.arrow((220,420),(220,510));f.text(70,565,'逐格独立求交，核对相同格序');save(f,'14-tests.png','实验范围与独立验证方法概览','原创实验说明')
finish(M,P);print(json.dumps(v,ensure_ascii=False))
