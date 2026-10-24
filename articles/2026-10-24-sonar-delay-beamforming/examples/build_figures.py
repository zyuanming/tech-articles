from pathlib import Path
import math,json,cmath
from figurelib import *
P=Path(__file__).resolve().parent;A=P.parent/'assets';M=[]
ang=[-90+i*.25 for i in range(721)];ts=[i for i in range(301)]
def response(n,d,a):return abs(sum(cmath.exp(2j*math.pi*j*d*(.5-math.sin(math.radians(a)))) for j in range(n)))/n
D={'model':'uniform linear point array, far field, one 2D half-space','c_m_s':1500,'f_Hz':10000,'d_m':.075,'theta_deg':30,'arrival_us':[0,25,50,75],'add_us':[75,50,25,0],'angles_deg':ang,'N4':[response(4,.5,a) for a in ang],'N8':[response(8,.5,a) for a in ang],'grating':[response(4,1,a) for a in ang],'time_us':ts,'raw':[[math.cos(2*math.pi*(t-arr)/100) for t in ts] for arr in [0,25,50,75]],'aligned':[math.cos(2*math.pi*(t-75)/100) for t in ts]}
assert abs(D['N4'][480]-1)<1e-10
(P/'results.json').write_text(json.dumps(D,ensure_ascii=False,indent=2));D=json.loads((P/'results.json').read_text())
def done(b,n,p):M.append(b.save(A/f'{n:02}.png',p))
b=Board('斜着来的波，在阵列上依次到达');
for ox in [30,510]:
 for j in range(4):b.circle(ox+60+j*105,570,12,fill=BLUE)
 for j in range(3):
  if ox==30:b.line([(ox+30,220+j*90),(ox+410,220+j*90)],TEAL)
  else:b.line([(ox+40,400+j*90),(ox+380,200+j*90)],TEAL)
 if ox==30:b.arrow((ox+220,180),(ox+220,500),ORANGE)
 else:b.arrow((ox+80,210),(ox+260,520),ORANGE)
b.text('正面同时到达',60,660);b.text('左先到，右后到',515,660);done(b,1,'平面波到达顺序')
b=Board('间距投影，才是额外声程');a=(220,590);bb=(760,590);foot=(625,356);b.line([a,bb],BLUE);b.line([a,foot],GRAY);b.line([foot,bb],ORANGE,7);b.circle(*a,12,fill=BLUE);b.circle(*bb,12,fill=BLUE);b.line([(220,590),(220,170)],GRAY,3);b.arrow((45,287),(220,590),ORANGE);b.d.arc((120,490,320,690),240,270,fill=ORANGE,width=4);b.text('θ = 30°',240,440);b.text('d = 7.5 cm',350,640);b.text('投影 = 3.75 cm',390,270);b.text('辅助线与传播方向垂直',150,770);done(b,2,'路程差三角几何')
b=Board('同一波峰：A 最先，D 最后');
for i,v in enumerate(D['arrival_us']):
 y=200+i*150;b.text('ABCD'[i],40,y-28);b.line([(170,y),(840,y)],GRAY,2);b.circle(170+8*v,y,13,fill=BLUE);b.text(f'{v} μs',180+8*v,y+20)
b.text('向右：时间增加',310,820);done(b,3,'到达时间表')
b=Board('先到的多等一会儿，全部对齐');
for i,(x,yv) in enumerate(zip(D['arrival_us'],D['add_us'])):
 y=210+i*150;b.text('ABCD'[i],35,y);b.line([(170,y+30),(170+8*x,y+30)],BLUE,16);b.line([(170+8*x,y+30),(770,y+30)],ORANGE,16);b.text(f'{x} + {yv} = 75 μs',220,y+60)
done(b,4,'补偿时间与到达相加')
b=Board('未补偿：每路相差四分之一周');
for i,vals in enumerate(D['raw']):
 y=260+i*250;b.text('ABCD'[i],35,y-40);b.line([(150,y),(870,y)],GRAY,2);b.line([(150+t*2.4,y-60*v) for t,v in zip(D['time_us'],vals)],BLUE)
 b.text('0',150,y+85,anchor='mt');b.text('300 μs',870,y+85,anchor='mt')
b.text('各行振幅：−1 到 +1',180,1260);done(b,5,'四路原始相位错位')
b=Board('对齐后相加，四个波峰一起到');plot(b,[(D['time_us'],D['aligned'],BLUE),(D['time_us'],[4*x for x in D['aligned']],ORANGE)],(0,300),(-4,4),xlabel='时间 / 微秒',ylabel='相对声压');b.text('蓝：一路   橙：四路之和',90,740);done(b,6,'对齐相加')
for n,title,series in [(7,'来波固定 30°，试着朝不同方向听',[(D['angles_deg'],D['N4'],BLUE)]),(8,'更长阵列，对方向误差更敏感',[(D['angles_deg'],D['N4'],BLUE),(D['angles_deg'],D['N8'],TEAL)]),(9,'间距一个波长：出现重复主峰',[(D['angles_deg'],D['grating'],ORANGE)])]:
 b=Board(title);plot(b,series,(-90,90),(0,1),xlabel='假设方向 / 度',ylabel='归一化振幅',ticks=[(-90,'−90'),(-30,'−30'),(30,'30'),(90,'90')]);
 if n==8:b.text('蓝：四元   绿：八元',150,740)
 done(b,n,'方向扫描模型')
b=Board('25 微秒，不总是四分之一周');
for i,f in enumerate([10000,20000]):
 y=260+i*400;b.text(f'{f//1000} kHz',35,y-150);b.line([(130+t*7,y-65*math.cos(2*math.pi*f*t*1e-6)) for t in range(101)],BLUE);b.arrow((130,y+100),(840,y+100),GRAY,2);b.line([(130,y+100),(305,y+100)],ORANGE,10);b.text('25 微秒',135,y+140);b.text('100 微秒',690,y+140)
done(b,10,'宽带时延与固定相移区别')
b=Board('近场要按每条真实距离算延时');
for j in range(4):b.circle(100+j*95,600,12,fill=BLUE);b.circle(560+j*95,600,12,fill=BLUE)
for j in range(3):b.line([(70,270+j*95),(420,270+j*95)],TEAL)
b.circle(700,200,15,fill=ORANGE)
for x in [560,655,750,845]:b.line([(700,200),(x,600)],ORANGE,3)
for r in [180,260,340]:b.d.arc((700-r,200-r,700+r,200+r),40,140,fill=TEAL,width=4)
b.text('远场平面近似',55,700);b.text('近场波面弯曲',520,700);done(b,11,'平面近似的边界')
from PIL import Image
im=Image.open(P.parent/'originals/photos/transducer.jpg');M.append({'file':'../originals/photos/transducer.jpg','width':im.width,'height':im.height,'identity':'NOAA Ocean Exploration 换能器实物照片','min_font_px':'NOT_MEASURED','purpose':'真实船底阵列'})
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2))
