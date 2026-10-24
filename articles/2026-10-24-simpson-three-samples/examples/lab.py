"""Original quadrature examples; all exact polynomial checks use Fraction. CC BY 4.0."""
from pathlib import Path
from fractions import Fraction as F
import math,json
from figure import *
P=Path(__file__).resolve().parent;A=P.parent/'assets';M=[]
def simpson(fn,a,b,n):
 if n<=0 or n%2:raise ValueError('positive even number of panels required')
 h=(b-a)/n
 return h/3*(fn(a)+fn(b)+sum((4 if i%2 else 2)*fn(a+i*h) for i in range(1,n)))
T=[i/100 for i in range(201)];f=lambda x:1+x*x
D=dict(main=[(t,f(t)) for t in T],exact=str(F(14,3)),simpson=str(simpson(lambda x:1+x*x,F(0),F(2),2)),x4=[dict(n=n,estimate=str(simpson(lambda x:x**4,F(0),F(2),n)),error=str(simpson(lambda x:x**4,F(0),F(2),n)-F(32,5))) for n in [2,4,8,16]],hidden=[(t,math.sin(2*math.pi*t)**2) for t in [i/400 for i in range(801)]])
assert D['simpson']==D['exact']
for k in range(4):assert simpson(lambda x:x**k,F(-1),F(1),2)==F(0) if k%2 else simpson(lambda x:x**k,F(-1),F(1),2)==F(2,k+1)
assert F(D['x4'][0]['error'])/F(D['x4'][1]['error'])==16
(P/'data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2));D=json.loads((P/'data.json').read_text())
def save(f,n,s):M.append(f.save(A/f'{n:02}.png',s))
save(chart('流量曲线下面，藏着总水量',[('流量',D['main'],BLUE)],(0,2),(0,5.5),[(0,'0'),(1,'1'),(2,'2')],[(0,'0'),(2,'2'),(5,'5')],'时间 / s','流量 / L/s',fill=([(0,0)]+D['main']+[(2,0)],'#dcebf2')),1,'流量与体积的面积关系')
pts=[(0,1),(.5,1),(.5,1.25),(1,1.25),(1,2),(1.5,2),(1.5,3.25),(2,3.25)]
save(chart('左端矩形遗漏了上面的水',[('真实流量',D['main'],BLUE),('矩形顶',pts,ORANGE)],(0,2),(0,5.5),[(0,'0'),(1,'1'),(2,'2')],[(0,'0'),(2,'2'),(5,'5')],'时间 / s','流量 / L/s'),2,'矩形近似偏低的可见空隙')
save(chart('两点连直线，又多算一块',[('真实曲线',D['main'],BLUE),('端点直线',[(0,1),(2,5)],ORANGE)],(0,2),(0,5.5),[(0,'0'),(1,'1'),(2,'2')],[(0,'0'),(2,'2'),(5,'5')],'时间 / s','流量 / L/s'),3,'单个梯形面积6升而真实14/3升')
f=chart('中间多问一次，看见弯曲',[('穿过三点',D['main'],BLUE)],(0,2),(0,5.5),[(0,'0'),(1,'1'),(2,'2')],[(0,'0'),(2,'2'),(5,'5')],'时间 / s','流量 / L/s')
for x in [0,1,2]:f.dot(150+x*360,650-float(1+x*x)/5.5*380,ORANGE,12)
save(f,4,'三个等距采样点确定二次插值曲线')
X=[-1+i/100 for i in range(201)];save(chart('检查三种最简单的形状',[('常数 1',[(x,1) for x in X],TEAL),('直线 z',[(x,x) for x in X],ORANGE),('平方 z²',[(x,x*x) for x in X],BLUE)],(-1,1),(-1.2,1.3),[(-1,'−1'),(0,'0'),(1,'1')],[(-1,'−1'),(0,'0'),(1,'1')],'新坐标 z','函数值'),5,'用常数、一次与二次决定权重')
f=Fig('同一份高度，中间算四份',660)
for x,v,label,col in [(180,1,'左',BLUE),(450,4,'中',ORANGE),(720,1,'右',BLUE)]:
 f.rect((x,480-v*75,x+120,480),col,col);f.text(x+25,500,label,42);f.text(x+40,480-v*75-70,str(v),42,col)
f.text(80,120,'权重 1 : 4 : 1',46);save(f,6,'权重柱长共用每份75像素的比例')
save(chart('三次项的两半正好抵消',[('z³',[(x,x**3) for x in X],BLUE)],(-1,1),(-1.2,1.2),[(-1,'−1'),(0,'0'),(1,'1')],[(-1,'−1'),(0,'0'),(1,'1')],'坐标 z','有符号高度'),7,'对称积分使三次多项式也能精确')
xx=[i/100 for i in range(201)];save(chart('四次曲线已经不再精确',[('x⁴',[(x,x**4) for x in xx],BLUE),('三点抛物线',[(x,7*x*x-6*x) for x in xx],ORANGE)],(0,2),(-2,17),[(0,'0'),(1,'1'),(2,'2')],[(0,'0'),(8,'8'),(16,'16')],'x','函数值'),8,'插值抛物线甚至局部为负，不能当作真实函数')
save(chart('步距减半，误差缩到十六分一',[('log10误差',[(r['n'],math.log10(float(F(r['error'])))) for r in D['x4']],BLUE)],(2,16),(-4.5,0),[(2,'2'),(4,'4'),(8,'8'),(16,'16')],[(-4,'−4'),(-2,'−2'),(0,'0')],'小段数 n','误差对数'),9,'同一x4积分的真实误差，纵轴为对数')
save(chart('五个零读数，也可能漏掉波峰',[('真实函数',D['hidden'],BLUE),('采样判断',[(0,0),(2,0)],ORANGE)],(0,2),(0,1.15),[(0,'0'),(.5,'0.5'),(1,'1'),(2,'2')],[(0,'0'),(.5,'0.5'),(1,'1')],'x','sin²(2πx)'),10,'两层Simpson恰好漏采的反例')
f=Fig('不等距采样，不能照搬权重',640);f.line([(100,300),(860,300)],GRAY,5)
for x,s,col in [(100,'0',BLUE),(290,'0.5',ORANGE),(860,'2',BLUE)]:f.dot(x,300,col,12);f.text(x-20,345,s,42,col)
f.text(80,130,'三点仍在，左右间隔不同',42);f.text(100,450,'0.5',42);f.text(560,450,'1.5',42);save(f,11,'非等距节点不能套标准1:4:1')
f=chart('把额外采样放在变化快处',[('窄峰示意',[(x,math.exp(-80*(x-1.25)**2)) for x in xx],BLUE)],(0,2),(0,1.1),[(0,'0'),(1,'1'),(2,'2')],[(0,'0'),(.5,'0.5'),(1,'1')],'x','函数值')
for x in [0,.5,1,1.125,1.25,1.375,1.5,2]:f.line([(150+360*x,650),(150+360*x,620)],ORANGE,5)
save(f,12,'自适应的采样位置示意，不冒称已实现可靠积分器')
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2));print('12 figures; exact rational polynomial degrees 0..3 and x4 error ratio checked')
