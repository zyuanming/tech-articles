"""Bounded-acceleration teaching model, exact segment equations. CC BY 4.0."""
from pathlib import Path
import json,math
from figure import *
P=Path(__file__).resolve().parent;A=P.parent/'assets';M=[]
def segment(t,switch=2):
 if t<=switch:return .5*t*t,t,1
 z=t-switch;return .5*switch**2+switch*z-.5*z*z,switch-z,-1
T=[i/100 for i in range(401)];rows=[dict(t=t,x=segment(t)[0],v=segment(t)[1],u=segment(t)[2]) for t in T]
D=dict(a=1,L=4,T=4,switch=2,trace=rows,brake=[dict(v=i/50,d=(i/50)**2/2) for i in range(151)],delayed=dict(switch=2.1,stop=2.1**2,time=4.2))
assert segment(4)==(4,0,-1);assert abs(D['delayed']['stop']-4.41)<1e-12
(P/'data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2));D=json.loads((P/'data.json').read_text())
def save(f,n,s):M.append(f.save(A/f'{n:02}.png',s))
f=Fig('四米外，要停住而非路过',700);f.line([(100,310),(860,310)],GRAY,5)
for x,label,col in [(120,'起点 0 m',BLUE),(470,'切换 2 m',ORANGE),(820,'终点 4 m',TEAL)]:
 f.rect((x-45,245,x+45,305),'#dcebf2');f.dot(x-25,318,INK,10);f.dot(x+25,318,INK,10);f.text(x-65 if x>200 else 60,370,label,40,col)
f.text(80,130,'从静止出发，最终也静止',42);f.arrow((210,220),(360,220),BLUE);f.arrow((710,220),(560,220),ORANGE);save(f,1,'明确起点/终点位置和加减速两段')
save(chart('速度图的面积就是位移',[('速度 v',[(r['t'],r['v']) for r in D['trace']],BLUE)],(0,4),(0,2.3),[(0,'0'),(2,'2'),(4,'4')],[(0,'0'),(1,'1'),(2,'2')],'时间 / s','速度 / m/s',fill=([(0,0),(2,2),(4,0)],'#dcebf2')),2,'4秒三角形面积为4米')
save(chart('前半越来越快，后半减速',[('位置 x',[(r['t'],r['x']) for r in D['trace']],BLUE)],(0,4),(0,4.3),[(0,'0'),(2,'2'),(4,'4')],[(0,'0'),(2,'2'),(4,'4')],'时间 / s','位置 / m'),3,'同一行程位置曲线变化')
save(chart('加速度在中途换一次符号',[('加速度',[(0,1),(2,1),(2,-1),(4,-1)],ORANGE)],(0,4),(-1.3,1.3),[(0,'0'),(2,'2'),(4,'4')],[(-1,'−1'),(0,'0'),(1,'1')],'时间 / s','加速度 / m/s²'),4,'理想瞬时切换输入，不代表现实电机能瞬变')
save(chart('从每秒两米刹到零',[('刹车速度',[(0,2),(2,0)],ORANGE)],(0,2),(0,2.3),[(0,'0'),(1,'1'),(2,'2')],[(0,'0'),(1,'1'),(2,'2')],'时间 / s','速度 / m/s',fill=([(0,0),(0,2),(2,0)],'#f4dfd4')),5,'刹车距离由速度三角形得到')
save(chart('刹车线把位置与速度连起',[('刹停曲线',[(4-r['d'],r['v']) for r in D['brake']],TEAL)],(-.5,4.5),(0,3),[(0,'0'),(2,'2'),(4,'4')],[(0,'0'),(1,'1'),(2,'2'),(3,'3')],'位置 / m','速度 / m/s'),6,'v正向时恰好停在4米的状态曲线')
save(chart('早刹停不够，晚刹就过头',[(name,[(i/100,segment(i/100,s)[1]) for i in range(round(200*s)+1)],col) for name,s,col in [('早 1.5s',1.5,TEAL),('准 2s',2,BLUE),('晚 2.5s',2.5,ORANGE)]],(0,5),(0,3),[(0,'0'),(2,'2'),(4,'4')],[(0,'0'),(1,'1'),(2,'2'),(3,'3')],'时间 / s','速度 / m/s'),7,'改变切换时刻同时改变停止位置')
save(chart('任何合法速度都在屋顶下',[('起点限制',[(0,0),(4,4)],BLUE),('终点限制',[(0,4),(4,0)],ORANGE)],(0,4),(0,4),[(0,'0'),(2,'2'),(4,'4')],[(0,'0'),(2,'2'),(4,'4')],'时间 / s','速度上界',fill=([(0,0),(2,2),(4,0)],'#dcebf2')),8,'两端加速度限制形成速度包络并证明时间下界')
save(chart('再加限速，会多出巡航段',[('上限 1 m/s',[(0,0),(1,1),(4,1),(5,0)],BLUE)],(0,5),(0,1.3),[(0,'0'),(1,'1'),(4,'4'),(5,'5')],[(0,'0'),(1,'1')],'时间 / s','速度 / m/s',fill=([(0,0),(1,1),(4,1),(5,0)],'#dcebf2')),9,'限制速度后最优形状改为梯形')
pts=[(i/100,math.cos(math.pi*(i/100)/4)) for i in range(401)]
save(chart('平滑动作是另一项约束',[('瞬时切换',[(0,1),(2,1),(2,-1),(4,-1)],ORANGE),('平滑示意',pts,BLUE)],(0,4),(-1.2,1.2),[(0,'0'),(2,'2'),(4,'4')],[(-1,'−1'),(0,'0'),(1,'1')],'时间 / s','加速度 / m/s²'),10,'明确平滑曲线未被声明为同一行程最优解')
rows2=[dict(t=i/100,x=segment(i/100,2.1)[0]) for i in range(421)]
save(chart('切换晚一点，终点就变了',[('准时',[(r['t'],r['x']) for r in D['trace']],BLUE),('晚 0.1s',[(r['t'],r['x']) for r in rows2],ORANGE)],(0,4.2),(0,4.6),[(0,'0'),(2,'2'),(4,'4')],[(0,'0'),(2,'2'),(4,'4')],'时间 / s','位置 / m'),11,'事件延迟0.1秒使完全刹停位置变4.41米')
pts=[(i/100,3-(i/100)) for i in range(301)]
save(chart('已经过快，最强刹车也会越过',[('从 x=3 起',[(3+3*t-.5*t*t,3-t) for t in [i/100 for i in range(301)]],ORANGE)],(2.5,8),(0,3),[(3,'3'),(4,'4'),(6,'6'),(8,'8')],[(0,'0'),(1,'1'),(2,'2'),(3,'3')],'位置 / m','速度 / m/s'),12,'起点改为位置3速度3时刹停在7.5米，不能立即回到目标')
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2));print('12 figures; endpoint 4 m, 0 m/s; delayed stop 4.41 m checked')
