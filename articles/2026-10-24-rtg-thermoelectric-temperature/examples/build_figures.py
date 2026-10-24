from pathlib import Path
import math,json
from figurelib import *
P=Path(__file__).resolve().parent;A=P.parent/'assets';M=[]
D={'model':'synthetic constant-coefficient thermoelectric circuit','S_V_K':0.0004,'deltaT_K':200,'pairs':100,'internal_ohm':4,'heat_input_assumed_W':100}
D['single_V']=D['S_V_K']*D['deltaT_K'];D['open_V']=D['single_V']*D['pairs'];D['loads_ohm']=[i/10 for i in range(201)];D['power_W']=[D['open_V']**2*r/(4+r)**2 for r in D['loads_ohm']];D['dT_curve']=[i*10 for i in range(21)];D['V_curve']=[D['S_V_K']*x for x in D['dT_curve']];D['cold_K']=[300+i for i in range(101)];D['cool_V']=[100*D['S_V_K']*(500-t) for t in D['cold_K']]
(P/'results.json').write_text(json.dumps(D,ensure_ascii=False,indent=2));D=json.loads((P/'results.json').read_text())
def done(b,n,p):M.append(b.save(A/f'{n:02}.png',p))
b=Board('热源和散热端，缺一不可');b.rect((70,180,250,330),fill='#ffe8d8',outline=ORANGE);b.text('热源',95,220);b.rect((390,180,600,330));b.text('转换材料',400,220);b.rect((740,180,915,330));b.text('冷端',775,220);b.arrow((255,250),(380,250),ORANGE);b.arrow((610,250),(730,250),ORANGE);b.arrow((495,335),(495,465));b.text('电能 → 负载',350,490);done(b,1,'区分热流与电输出')
b=Board('开路：有电压，没有持续电流');b.rect((100,200,850,370));b.text('热端',100,130,color=ORANGE);b.text('冷端',750,130,color=BLUE);b.arrow((240,240),(710,240),ORANGE);b.text('扩散趋势',340,185);b.arrow((710,330),(240,330),BLUE);b.text('电场作用抵消',310,380);done(b,2,'开路电压的作用平衡示意')
b=Board('一对材料：热并排走，电接续走');b.rect((200,170,760,220),fill='#ffe8d8',outline=ORANGE);b.text('共同热面',350,110);b.rect((250,220,370,470),fill='#e7eff5');b.rect((590,220,710,470),fill='#e2f4ef',outline=TEAL);b.text('材料甲',65,300);b.text('材料乙',740,300);b.line([(310,470),(310,600),(160,600)]);b.line([(650,470),(650,600),(800,600)]);b.text('两个冷端输出',280,650);b.arrow((400,270),(400,430),ORANGE);b.arrow((550,270),(550,430),ORANGE);done(b,3,'热通路与电连接方向')
b=Board('常系数模型：温差乘以系数');plot(b,[(D['dT_curve'],D['V_curve'],BLUE)],(0,200),(0,.08),xlabel='温差 / K',ylabel='开路电压 / V');done(b,4,'可手算电压斜率')
b=Board('电串联：沿连接方向累计电压');
for i,v in enumerate([.08,.16,.24]):
 x=95+i*290;b.rect((x,200,x+210,350));b.text(f'{v:.2f} V',x+25,245)
 if i<2:b.arrow((x+215,275),(x+275,275))
b.text('每一对仍跨过同样的温差',130,430);done(b,5,'串联累计电压非串联温差')
b=Board('带负载时，要扣掉内部压降');b.line([(170,230),(760,230),(760,520),(170,520),(170,230)]);b.circle(170,365,60,fill='white');b.text('8 V',110,575);b.rect((300,190,490,270),fill='white');b.text('内阻 4 Ω',295,115);b.rect((690,310,830,440),fill='white');b.text('负载',660,575);b.text('4 Ω',700,630);b.arrow((360,520),(520,520));b.text('1 A',380,570);done(b,6,'闭合电路的串联分压')
b=Board('电压高，不等于输出功率大');plot(b,[(D['loads_ohm'],D['power_W'],BLUE)],(0,20),(0,4),xlabel='负载 / Ω',ylabel='负载功率 / W',ticks=[(0,'0'),(4,'4'),(12,'12'),(20,'20')]);done(b,7,'固定温差负载匹配曲线')
b=Board('另加热输入假设：稳态能量账');
for y,val,col,label in [(210,100,ORANGE,'输入 100 W'),(360,4,BLUE,'电输出 4 W'),(510,96,GRAY,'排热 96 W')]:
 b.text(label,50,y-70);b.rect((50,y,50+8*val,y+50),fill=col,outline=col)
assert 800>768>32;done(b,8,'同尺度热电功率分流')
b=Board('真空中的散热面靠辐射排热');b.rect((340,180,620,550),fill='#d9e2ea');
for y in [230,340,450]:
 b.rect((180,y,780,y+25));b.arrow((180,y+12),(80,y-35),ORANGE);b.arrow((780,y+12),(880,y-35),ORANGE)
b.text('鳍片增加有效辐射面积',160,620);done(b,9,'散热鳍片的作用')
b=Board('热端不变，冷端升温也会掉电压');plot(b,[(D['cold_K'],D['cool_V'],BLUE)],(300,400),(0,8),xlabel='冷端温度 / K',ylabel='开路电压 / V');done(b,10,'冷端温度影响温差')
from PIL import Image
f=P.parent/'originals/photos/rtg.jpg';im=Image.open(f);M.append({'file':'../originals/photos/rtg.jpg','width':im.width,'height':im.height,'identity':'NASA/JPL-Caltech 实物照片，已有许可素材副本','min_font_px':'NOT_MEASURED','purpose':'真实RTG散热鳍片'})
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2))
