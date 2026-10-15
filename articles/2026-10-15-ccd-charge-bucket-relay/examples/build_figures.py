#!/usr/bin/env python3
"""Original Chinese explanatory drawings and plots from run_model.py. MIT."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,csv,math
A=Path(__file__).resolve().parents[1];O=A/'assets';O.mkdir(exist_ok=True)
R=json.loads((A/'examples/results.json').read_text());EV=json.loads((A/'examples/readout-events.json').read_text())
BG='#f4f2e9';INK='#183944';WHITE='#ffffff';TEAL='#16817f';BLUE='#326bab';AMBER='#ad690f';RED='#b83e51';GRAY='#687b81';LIGHT='#dbe6e3';PALE='#e4edf6'
F='/usr/share/fonts/opentype/noto/NotoSansCJK-';font=lambda n,b=False:ImageFont.truetype(F+('Bold' if b else 'Regular')+'.ttc',n,index=2)
meta=[]
def start(title,h):
 global im,d,mn
 im=Image.new('RGB',(1062,h),BG);d=ImageDraw.Draw(im);mn=100;txt((48,35),title,48,True)
def txt(p,s,n=40,b=False,c=INK,anchor=None):
 global mn
 mn=min(mn,n);bb=d.textbbox(p,str(s),font=font(n,b),anchor=anchor)
 assert bb[0]>=0 and bb[2]<=1062 and bb[1]>=0 and bb[3]<=im.height,(s,bb,im.size)
 d.text(p,str(s),font=font(n,b),fill=c,anchor=anchor)
def line(a,b,c=GRAY,w=5):d.line([a,b],fill=c,width=w)
def arrow(a,b,c=TEAL,w=7):
 line(a,b,c,w);theta=math.atan2(b[1]-a[1],b[0]-a[0]);r=20
 d.polygon([b,(b[0]-r*math.cos(theta-.5),b[1]-r*math.sin(theta-.5)),(b[0]-r*math.cos(theta+.5),b[1]-r*math.sin(theta+.5))],fill=c)
def box(x,y,w,h,fill=WHITE,outline=LIGHT):d.rounded_rectangle((x,y,x+w,y+h),radius=18,fill=fill,outline=outline,width=3)
def dot(x,y,c=TEAL,r=12):d.ellipse((x-r,y-r,x+r,y+r),fill=c)
def save(name,purpose,identity='原创机制示意；不代表器件尺寸或真实波形'):
 im.save((A if name=='cover.png' else O)/name);meta.append(dict(path=name if name=='cover.png' else 'assets/'+name,width=im.width,height=im.height,min_label_px=mn,effective_min_at_354px=mn/3,purpose=purpose,identity=identity))
def cells(vals,x,y,w=190,h=100,colors=None,unit=1):
 for j,v in enumerate(vals):
  box(x+j*w,y,w-10,h,fill=(colors[j] if colors else WHITE));txt((x+j*w+(w-10)/2,y+h/2),str(v//unit if isinstance(v,int) else v),40,True,anchor='mm')

start('一张照片，经过四种表示',1190)
for y,title,sub,c in [(145,'光子','落到不同位置的光',AMBER),(385,'电荷包','各像素保存的电子数量',TEAL),(625,'模拟电压','输出节点逐包测量',BLUE),(865,'数字','ADC量化后得到数值',INK)]:
 box(65,y,932,165);txt((100,y+25),title,46,True,c);txt((100,y+90),sub,40)
 if y<865:arrow((530,y+173),(530,y+228),c)
txt((531,1115),'CCD搬运电荷；数字通常在后面产生。',40,True,anchor='mm')
save('02-four-representations.png','把CCD的模拟电荷转移和最终数字照片分开')

start('“井”是电子势能低的地方',1080)
box(65,145,930,330);txt((100,170),'剖面示意：栅极隔着绝缘层控场',40,True)
for j,lab in enumerate(['A：低','B：高','C：低']):
 x=125+j*280;box(x,245,250,75,BLUE if j==1 else LIGHT);txt((x+125,282),lab,40,True,WHITE if j==1 else INK,anchor='mm')
d.rectangle((100,340,960,365),fill=AMBER);txt((110,385),'硅中电子可移动，栅极本身不搬家',40)
box(65,530,930,445);txt((100,552),'下图纵向：电子势能，向下更低',40,True)
pts=[(120,685),(360,685),(360,855),(660,855),(660,685),(945,685)]
d.line(pts,fill=BLUE,width=7)
for j in range(6):dot(405+j*42,825,TEAL,13)
arrow((225,755),(225,865),GRAY);txt((100,900),'较正的栅极电压 → 较低的电子势能',39,True)
save('03-potential-well.png','电子势能与栅电压方向不同；势阱不是刻出的空洞')

start('三相接力：电荷前进，栅极不动',1530)
xs=[310+100*j for j in range(7)]
for j,x in enumerate(xs):txt((x,155),'ABC'[j%3],40,True,anchor='mm')
for row,state in enumerate(R['phase_sequence']):
 y=245+row*165;txt((65,y+28),str(row),42,True);active=set(state['active'].replace('+',''));txt((100,y+28),state['active'],38,True)
 pts=[]
 for j,x in enumerate(xs):
  yy=y+85 if 'ABC'[j%3] in active else y+15
  if pts:pts.append((x-49,pts[-1][1]))
  pts.extend([(x-49,yy),(x+49,yy)])
 d.line(pts,fill=BLUE,width=5)
 for off in (0,3):dot(xs[0]+100*(state['packet_center_gate']+off),y+62,TEAL if off==0 else AMBER,17)
txt((531,1445),'两包电荷之间始终留着势垒。',40,True,anchor='mm')
save('04-three-phase-spatial.png','7个时刻显示相邻两包在同一周期内平移；绿色和棕色用于追踪身份')

start('三路时钟，控制整列同相栅极',930)
xx=[225+i*120 for i in range(7)]
for i,x in enumerate(xx):txt((x,155),str(i),40,True,anchor='mm')
for ri,phase in enumerate('ABC'):
 y=285+ri*180;txt((70,y),phase,48,True);txt((130,y-50),'高',38);txt((130,y+40),'低',38)
 vals=[int(phase in s['active']) for s in R['phase_sequence']];pts=[]
 for i,v in enumerate(vals):
  yy=y+60-100*v
  if pts:pts.append((xx[i],pts[-1][1]))
  pts.append((xx[i],yy))
 d.line(pts,fill=[TEAL,BLUE,AMBER][ri],width=8)
 for x,v in zip(xx,vals):dot(x,y+60-100*v,[TEAL,BLUE,AMBER][ri],8)
txt((65,835),'0与6：电压状态相同，电荷位置不同。',40,True)
save('05-phase-clocks.png','用时间视角解释相位重叠以及一个像素周期；折线仅逻辑状态')

start('把十二个像素，排队送往出口',1190)
txt((80,135),'格内数字 × 100电子；总量7800电子',39)
for c in range(4):txt((305+c*190,215),'列'+str(c),38,anchor='mm')
for r,row in enumerate(R['initial_e']):
 y=275+r*160;txt((65,y+55),'行'+str(r),38);cells(row,215,y,190,115,unit=100)
for x in [305,495,685,875]:arrow((x,725),(x,805),TEAL)
cells([0]*4,215,845,190,115,colors=[PALE]*4)
txt((420,1000),'串行寄存器',42,True);arrow((210,902),(100,902),BLUE);txt((65,1075),'整幅下移一行，再把底排向左读空。',40,True)
save('06-array-readout.png','明确3×4主例坐标、7800电子、两个搬运方向和空的串行寄存器')

start('第一行抵达后，怎样逐个读？',1390)
for k in range(4):
 ev=EV[k+2];y=155+k*285
 txt((65,y),'第'+str(k+1)+'次串行移位',42,True)
 cells(ev['serial_e'],225,y+80,190,105)
 arrow((220,y+130),(115,y+130),BLUE)
 txt((65,y+205),'刚读出 '+str(ev['output_e'])+'电子',40,c=BLUE)
txt((531,1320),'读空之后，才能接住下一整行。',40,True,anchor='mm')
save('07-first-row-steps.png','由实际模型前4串行事件显示空位如何逐步补入','实际运行教学模型状态，不是硬件测量')

start('实跑结果：一串数怎样还原成图',1190)
rows=list(csv.DictReader((A/'examples/readout.csv').open()))
left,right,top,bottom=125,985,230,790
for val in [0,400,800,1200]:
 y=bottom-val/1200*(bottom-top);line((left,y),(right,y),LIGHT,3);txt((left-12,y),str(val),38,anchor='rm')
colors=[TEAL,BLUE,AMBER]
for k,r in enumerate(rows):
 x=left+(k+.5)*(right-left)/12;v=int(r['electrons']);y=bottom-v/1200*(bottom-top)
 d.rectangle((x-22,y,x+22,bottom),fill=colors[k//4]);txt((x,835),str(k+1),38,anchor='mm')
txt((65,135),'纵轴：电子数',40);txt((625,895),'横轴：输出样本序号',38)
for y,c,s in [(970,TEAL,'1—4：原行2'),(1035,BLUE,'5—8：原行1'),(1100,AMBER,'9—12：原行0')]:dot(85,y+25,c,13);txt((120,y),s,40,True)
save('08-output-plot.png','直接绘制readout.csv的12个样本，用颜色保存空间行身份','实际运行教学模型输出；横轴不是秒')

start('900个电子，为什么读到550？',1190)
for y,title,sub in [(150,'电荷包：900电子','到达输出检测节点'),(420,'电压变化：|ΔV| = Q / C','电子电荷量×个数，除以节点电容'),(690,'数字码：100 + 900 / 2 = 550','假设偏置100 DN，增益2电子/DN')]:
 box(55,y,952,205);txt((90,y+28),title,43,True);txt((90,y+112),sub,38)
 if y<690:arrow((530,y+213),(530,y+258),BLUE)
txt((65,990),'DN是数字单位；不是电子个数。',42,True)
txt((65,1070),'测量后复位，为下一包重新准备。',40)
save('09-charge-to-number.png','区分电荷、电压、数字码、偏置和转换增益')

start('读出时还在收光，会发生什么？',1250)
for y,title,shield in [(150,'全帧式：同一区域感光和转移',False),(650,'帧转移式：另设遮光存储区',True)]:
 txt((65,y),title,42,True)
 if not shield:
  for j in range(4):box(320,y+90+j*65,330,58,PALE)
  arrow((470,y+110),(470,y+330),BLUE)
  for j in range(3):arrow((140,y+110+j*80),(310,y+150+j*65),AMBER,6)
  txt((70,y+385),'移动中的包，又混入沿途新电荷。',39)
 else:
  box(100,y+95,350,235,PALE);box(590,y+95,350,235,LIGHT)
  txt((275,y+155),'感光区',42,True,anchor='mm');txt((765,y+155),'遮光存储区',40,True,anchor='mm')
  arrow((465,y+245),(570,y+245),BLUE);txt((65,y+385),'先快速搬入，再从暗处慢慢读。',39)
save('10-smear-and-storage.png','区分全帧式与帧转移式；右向箭头只表示区域交接不是实际芯片方向')

start('满阱：装不下的电荷到哪里去？',1080)
txt((65,135),'教学规则：满1000，超出量向下溢出',39)
b=R['bloom']
for k,(title,values) in enumerate([('溢出前',b['input_e']),('溢出后',b['output_e'])]):
 x=140+k*490;txt((x+145,235),title,43,True,anchor='mm')
 for r,v in enumerate(values):
  y=320+r*180;box(x,y,290,145);d.rectangle((x+8,y+137-min(v,1000)/1000*120,x+282,y+137),fill=PALE)
  txt((x+145,y+65),str(v),46,True,RED if v>1000 else INK,anchor='mm')
arrow((455,570),(580,570),AMBER)
txt((65,915),'中间少500，下方多500；总量1700。',40,True)
txt((65,990),'具体溢出方向、防溢出结构因器件而异。',38)
save('11-blooming-model.png','用守恒数值区分饱和和邻近像素污染','原创定向溢出模型；非器件模拟')

start('每步很好，走两千步以后呢？',1130)
rows=list(csv.DictReader((A/'examples/efficiency.csv').open()));left,right,top,bottom=155,980,245,795
for v in [0.8,0.85,0.9,0.95,1.0]:
 y=bottom-(v-.8)/.2*(bottom-top);line((left,y),(right,y),LIGHT,3);txt((left-18,y),f'{v*100:.0f}%',38,anchor='rm')
for n in [0,512,1024,1536,2048]:
 x=left+n/2048*(right-left);txt((x,845),str(n),38,anchor='mm')
for key,c in [('eta_09999',AMBER),('eta_099999',TEAL)]:
 pts=[(left+int(r['transfers'])/2048*(right-left),bottom-(float(r[key])-.8)/.2*(bottom-top)) for r in rows];d.line(pts,fill=c,width=7)
txt((65,135),'纵轴：原包按时留下的比例',40)
txt((470,910),'横轴：像素间转移次数',38)
txt((65,975),'每步99.99% → 2048步81.48%',40,True,AMBER)
txt((65,1045),'每步99.999% → 2048步97.97%',40,True,TEAL)
save('12-transfer-efficiency.png','从同一效率乘法模型输出曲线，不把门相位子步当成像素转移','实际运行恒定效率模型；非厂商标称曲线')

start('电荷晚到，会在后面留下尾巴',1280)
rows=list(csv.DictReader((A/'examples/trail.csv').open()));left,right=145,980
for ytop,key,c,title in [(255,'ideal_e',TEAL,'理想：第4拍读出1000'),(745,'delayed_e',AMBER,'每步搬90%：后面还在到达')]:
 txt((65,ytop-100),title,40,True,c)
 for v in [0,500,1000]:
  y=ytop+280-v/1000*280;line((left,y),(right,y),LIGHT,3);txt((left-15,y),str(v),38,anchor='rm')
 for k,r in enumerate(rows[:10]):
  x=left+(k+.5)*(right-left)/10;v=float(r[key]);y=ytop+280-v/1000*280
  if v:d.rectangle((x-24,y,x+24,ytop+280),fill=c)
  txt((x,ytop+325),str(k+1),38,anchor='mm')
txt((65,1140),'纵轴：平均电子数；横轴：移位拍数',38)
txt((65,1205),'前四个非零值：656.1，262.44，65.61，13.122',38)
save('13-delayed-trail.png','从守恒残留模型画出脉冲尾巴；16拍总输出加芯片残留仍为1000','实际运行夸张残留模型，90%非实际产品参数')

start('CCD与典型CMOS：在哪里测量？',1160)
for y,title,ccd in [(150,'CCD：电荷沿像素链搬走',True),(650,'CMOS有源像素：就近转成信号',False)]:
 txt((65,y),title,42,True)
 for j in range(3):
  x=120+j*295;box(x,y+100,225,135,PALE);txt((x+112,y+165),'电荷',42,True,anchor='mm')
  if ccd and j<2:arrow((x+230,y+165),(x+285,y+165),TEAL)
  if not ccd:
   arrow((x+112,y+240),(x+112,y+300),BLUE);box(x,y+310,225,90);txt((x+112,y+355),'读出电路',38,True,anchor='mm')
 if ccd:arrow((820,y+245),(820,y+300),BLUE);txt((480,y+335),'送往少数输出节点',40,True)
txt((65,1090),'架构不同，不等于谁在任何场景都更好。',39)
save('14-readout-architectures.png','比较模拟电荷长程搬运与典型有源像素局部读出；不暗示每像素各有ADC')

start('一个器件构思，走向成像系统',1220)
items=[('1969','Boyle、Smith','提出CCD器件构思'),('1970','Boyle、Smith','论文描述储存与转移'),('1970','Amelio、Tompsett、Smith','发表器件实验验证'),('随后','Tompsett及团队','推进CCD成像与相机'),('2009','Boyle、Smith','分享诺贝尔物理学奖的一半')]
for i,(date,who,what) in enumerate(items):
 y=150+i*205;box(55,y,952,170);txt((85,y+25),date,43,True,BLUE);txt((280,y+22),who,40,True);txt((280,y+92),what,38)
save('15-history-roles.png','区分器件构思、实验验证和成像工程；不虚构具体会面日期')

start('照片里的电荷接力',1062)
txt((55,125),'CCD：一幅图，怎样走到一个出口',42)
for r in range(4):
 for c in range(5):
  x=155+c*160;y=270+r*140;box(x,y,130,100,PALE)
  for k in range((r+c)%4+1):dot(x+25+k*25,y+55,TEAL,9)
for x in [220,380,540,700,860]:arrow((x,805),(x,865),TEAL)
for c in range(5):box(155+c*160,900,130,80,WHITE)
arrow((145,940),(60,940),BLUE)
save('cover.png','独立封面：二维电荷矩阵汇入一条输出链')
(A/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('wrote',len(meta),'original PNG figures; NASA source photo is unchanged')
