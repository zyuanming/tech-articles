from figurelib import *
ROOT=Path(__file__).resolve().parents[1];a=math.radians(30);ref=[1,0,-1,0];s=[math.sin(a)*x for x in ref];c=[math.cos(a)*x for x in ref]
data={'angle_deg':30,'reference':ref,'sine_samples':s,'cosine_samples':c,'S':sum(x*y for x,y in zip(s,ref))/2,'C':sum(x*y for x,y in zip(c,ref))/2}
data['time_cycles']=[i/200 for i in range(401)]
data['carrier']=[math.cos(2*math.pi*t) for t in data['time_cycles']]
data['S_voltage']=[data['S']*v for v in data['carrier']]
data['S_opposite']=[-v for v in data['S_voltage']]
data['trajectory']=[{'C':math.cos(i*math.pi/180),'S':math.sin(i*math.pi/180),'S_mismatch':2/3*math.sin(i*math.pi/180)} for i in range(361)]
data['recovered_deg']=math.degrees(math.atan2(data['S'],data['C']));(ROOT/'examples/results.json').write_text(json.dumps(data,indent=2));D=json.loads((ROOT/'examples/results.json').read_text());meta=[]
def save(b,n,p):meta.append(b.save(ROOT/'assets'/f'{n:02}.png',p))
b=Board('角度是一根轴的方向');b.circle(470,410,200,fill='white');b.arrow((470,410),(780,410),GRAY);b.arrow((470,410),(470+200*math.cos(a),410-200*math.sin(a)),BLUE,9);b.text('0°',805,385);b.text('30°',650,250);b.circle(470,410,20,fill=INK);b.text('从右方起，逆时针为正',80,690);save(b,1,'建立角度零位和正方向')
b=Board('圆上的位置，拆成横向和竖向');b.circle(450,440,230,fill='white');x=450+230*math.cos(a);y=440-230*math.sin(a);b.arrow((450,440),(x,y));b.line([(450,440),(x,440)],TEAL,7);b.line([(x,440),(x,y)],ORANGE,7);b.text('C = 0.866',380,600);b.text('S = 0.5',650,450);b.text('半径 = 1',120,170);save(b,2,'30度的正交投影与归一化幅度')
b=Board('只看一条投影，分不清两处')
for x0,deg in [(255,30),(705,150)]:
 aa=math.radians(deg);b.circle(x0,390,160,fill='white');b.arrow((x0,390),(x0+160*math.cos(aa),390-160*math.sin(aa)));b.line([(x0-160,310),(x0+160,310)],ORANGE,3);b.text(f'{deg}°',x0,610,anchor='mt')
b.text('两处的 S 都是 0.5',190,730);save(b,3,'一条正弦幅度不能唯一确定全周角度')
b=Board('正交方向，给出不同的耦合');b.circle(475,430,220,fill='white');b.rect((240,400,710,460),fill='#d9f0eb',outline=TEAL);b.rect((445,195,505,665),fill='#f8e9df',outline=ORANGE);b.arrow((475,430),(665,320),BLUE,12);b.text('余弦方向',160,720,color=TEAL);b.text('正弦方向',600,720,color=ORANGE);b.text('转子方向',520,140);save(b,4,'线圈有效磁轴正交的概念模型，不是绕组施工图')
b=Board('轴没转，电压也在来回振荡');ts=D['time_cycles'];plot(b,[(ts,D['carrier'],GRAY),(ts,D['S_voltage'],ORANGE)],(0,2),(-1,1),xlabel='励磁周期',ylabel='归一化电压');b.text('灰：励磁　橙：30°的S路',45,750);save(b,5,'分清载波快振荡与轴角度缓慢变化')
b=Board('四个时刻，保留同一个参考')
for j,(name,vals) in enumerate([('参考',ref),('S路',s),('C路',c)]):
 y=180+j*150;b.text(name,40,y)
 for i,v in enumerate(vals):b.text(f'{v:.3g}',310+i*170,y,anchor='mt')
b.text('两路都乘上排，再求和',60,690);save(b,6,'同励磁参考用于两路同步解调')
b=Board('倒转半圈，幅度的符号会翻转');ts=D['time_cycles'];plot(b,[(ts,D['S_voltage'],BLUE),(ts,D['S_opposite'],ORANGE)],(0,2),(-1,1),xlabel='励磁周期',ylabel='S路电压');b.text('蓝：30°　橙：210°',50,750);save(b,7,'负系数表现为与励磁反相而非负的峰峰值')
b=Board('先看正负，再确定角度')
b.line([(120,430),(840,430)],GRAY);b.line([(480,160),(480,700)],GRAY)
for txt,x,y in [('C− S+',130,210),('C+ S+',570,210),('C− S−',130,560),('C+ S−',570,560)]:b.text(txt,x,y)
b.text('横轴 C；竖轴 S',150,790);save(b,8,'四象限的符号组合')
b=Board('一起放大，不改变指向');b.line([(160,600),(850,600)],GRAY);b.line([(160,600),(160,150)],GRAY)
for scale,col in [(1.6,ORANGE),(1,BLUE)]:b.arrow((160,600),(160+360*scale*D['C'],600-360*scale*D['S']),col,8)
b.text('S / C 不变',460,730);save(b,9,'相同通道增益与角度比值关系')
b=Board('两路放大量不同，圆会变成椭圆');pts=D['trajectory'];b.line([(480+240*t['C'],420-240*t['S']) for t in pts],GRAY);b.line([(480+240*t['C'],420-240*t['S_mismatch']) for t in pts],ORANGE);b.text('灰：理想　橙：S路偏小',90,760);save(b,10,'增益不匹配对整圈轨迹的影响')
b=Board('跨过零位，不代表倒转一整圈');b.circle(480,430,230,fill='white')
for deg,col in [(355,ORANGE),(5,BLUE)]:
 aa=math.radians(deg);b.arrow((480,430),(480+230*math.cos(aa),430-230*math.sin(aa)),col,7)
b.text('355° → 5°',75,160);b.text('短变化是 +10°',150,760);save(b,11,'角度包裹与跨零差值')
from PIL import Image
im=Image.open(ROOT/'assets/apollo-radar.png');meta.append({'file':'apollo-radar.png','width':im.width,'height':im.height,'identity':'NASA-S-69-3788 历史接口图单页渲染','min_font_px':'NOT_MEASURED','purpose':'交会雷达天线角度与数字接口实证'})
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));assert abs(D['recovered_deg']-30)<1e-10;print(len(meta),D['recovered_deg'])
