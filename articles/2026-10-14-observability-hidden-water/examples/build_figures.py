#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original explanatory vector-like drawings and plots of the saved exact tank model.
Pillow rasterizes code-defined geometry; no generated or simulated photographs.
"""
from pathlib import Path
from fractions import Fraction as F
from PIL import Image,ImageDraw,ImageFont
import json,math
ROOT=Path(__file__).resolve().parents[1];AS=ROOT/'assets';AS.mkdir(exist_ok=True)
R=json.loads((ROOT/'examples/expected-results.json').read_text());T=R['zero_input_trajectories'];U=R['known_input_demo']['trajectories'];N=R['noise_examples']
assert T['A'][1]['left']['fraction']=='29/5' and T['A'][1]['right']['fraction']=='11/5'
for i in range(9):assert T['A'][i]['sum']==T['B'][i]['sum']==T['C'][i]['sum']
assert [n['inferred_right']['fraction'] for n in N]==['83/50','-79/50']
W=1062;BG='#f6f3ea';INK='#233e4a';BLUE='#207a99';GOLD='#b47b26';TEAL='#32816a';RED='#b45359';GRAY='#6c7778';GRID='#d6ddd8';WHITE='#ffffff'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
meta=[];overflow=[]
def font(n=42,b=False):return ImageFont.truetype(BOLD if b else FONT,n,index=2)
def tx(x,y,text,n=42,c=INK,b=False,anchor=None):
 global minimum
 minimum=min(minimum,n);t=str(text);bb=d.textbbox((x,y),t,font=font(n,b),anchor=anchor)
 if bb[0]<20 or bb[2]>W-20 or bb[1]<0 or bb[3]>im.height:overflow.append(dict(figure=current,text=t,bbox=bb))
 d.text((x,y),t,font=font(n,b),fill=c,anchor=anchor)
def line(ps,c=INK,w=5):d.line(ps,fill=c,width=w,joint='curve')
def arrow(x,y,xx,yy,c=BLUE,w=6):
 line([(x,y),(xx,yy)],c,w);a=math.atan2(yy-y,xx-x);d.polygon([(xx,yy),(xx-19*math.cos(a-.5),yy-19*math.sin(a-.5)),(xx-19*math.cos(a+.5),yy-19*math.sin(a+.5))],fill=c)
def box(x,y,w,h,c=WHITE,outline=GRID):d.rounded_rectangle((x,y,x+w,y+h),radius=17,fill=c,outline=outline,width=3)
def new(title,h,sub):
 global im,d,minimum,current
 im=Image.new('RGB',(W,h),BG);d=ImageDraw.Draw(im);minimum=100;current=title
 d.rectangle((0,0,13,h),fill=BLUE);tx(48,32,title,51,b=True);tx(48,116,sub,37,c=GRAY)
def save(name,purpose,identity='Original teaching diagram, not an apparatus photograph'):
 im.save(AS/(name+'.png'));meta.append(dict(file='assets/'+name+'.png',purpose=purpose,identity=identity,width=W,height=im.height,minimum_font_px=minimum,effective_minimum_at_354px=minimum/3))
def tank(x,y,v,c=BLUE,w=180,h=230,unknown=False):
 # Outer box represents a 10 L capacity, all fills proportional to this scale.
 d.rectangle((x,y,x+w,y+h),fill='#e8edeb',outline=INK,width=4)
 if unknown:tx(x+w/2,y+h/2,'?',74,c=GRAY,b=True,anchor='mm')
 else:
  hh=h*float(v)/10;d.rectangle((x+4,y+h-hh,x+w-4,y+h-4),fill=c);tx(x+w/2,y+h+20,f'{float(v):g} 升',43,c=c,b=True,anchor='mt')
 line([(x-5,y),(x+w+5,y)],INK,6)
def dashed(ps,c=GOLD,w=6,dash=18,gap=12):
 for (x1,y1),(x2,y2) in zip(ps,ps[1:]):
  length=math.hypot(x2-x1,y2-y1)
  if not length:continue
  q=0
  while q<length:
   end=min(q+dash,length);line([(x1+(x2-x1)*q/length,y1+(y2-y1)*q/length),(x1+(x2-x1)*end/length,y1+(y2-y1)*end/length)],c,w);q+=dash+gap

def axes(x,y,w,h,xmin,xmax,ymin,ymax,xticks,yticks,xlabel,ylabel):
 def p(a,b):return(x+w*(a-xmin)/(xmax-xmin),y+h-h*(b-ymin)/(ymax-ymin))
 for a in xticks:
  xx,yy=p(a,ymin);line([(xx,y),(xx,y+h)],GRID,2);tx(xx,y+h+15,f'{a:g}',36,anchor='mt')
 for b in yticks:
  xx,yy=p(xmin,b);line([(x,yy),(x+w,yy)],GRID,2);tx(x-18,yy,f'{b:g}',36,anchor='rm')
 line([(x,y),(x,y+h),(x+w,y+h)],INK,4);tx(x,y-67,ylabel,38,b=True);tx(x+w/2,y+h+76,xlabel,38,anchor='mt');return p

def curve(p,rows,key,c=BLUE,isdash=False,width=6):
 points=[p(z['time_s'],z[key]['litres'])for z in rows]
 if isdash:dashed(points,c,width)
 else:line(points,c,width)
 for xx,yy in points:d.ellipse((xx-7,yy-7,xx+7,yy+7),fill=BG,outline=c,width=3)

def legend(y):
 line([(80,y+27),(160,y+27)],BLUE,7);tx(180,y,'实验 A',38,c=BLUE)
 dashed([(490,y+27),(570,y+27)],GOLD,7);tx(590,y,'实验 B',38,c=GOLD)

new('相同读数，两种内部情况',1130,'箱子位置固定；每箱容量10升。透视仅供解释')
for y,label,vals,c in [(245,'A',(8,2),BLUE),(695,'B',(2,8),GOLD)]:
 tx(50,y+75,label,60,c,b=True);tx(230,y-60,'左箱',40,anchor='mt');tx(490,y-60,'右箱',40,anchor='mt')
 tank(140,y,vals[0],c);tank(400,y,vals[1],c);arrow(615,y+105,722,y+105,c)
 box(748,y+15,255,180,outline=c);tx(875,y+32,'只报总量',38,anchor='mt');tx(875,y+95,'10 升',57,c,b=True,anchor='mt')
save('01-same-reading','让读者看到固定左右身份的两种分配为何给相同总量')

new('一轮记账：从（8，2）开始',1400,'所有变化都按轮初水量计算，再一起更新')
tx(270,215,'左箱',44,b=True,anchor='mt');tx(790,215,'右箱',44,b=True,anchor='mt')
tank(180,300,8,w=180,h=270);tank(700,300,2,w=180,h=270)
arrow(385,430,675,430);tx(530,325,'转移 0.6 升',41,c=BLUE,b=True,anchor='mt');tx(530,484,'(8 − 2) × 10%',36,anchor='mt')
arrow(270,666,270,815,GRAY);arrow(790,666,790,815,GRAY)
tx(270,845,'排出 1.6 升',42,c=GRAY,anchor='mt');tx(790,845,'排出 0.4 升',42,c=GRAY,anchor='mt')
tx(270,915,'8 × 20%',38,anchor='mt');tx(790,915,'2 × 20%',38,anchor='mt')
box(48,1055,966,255);tx(80,1080,'剩下多少？',43,b=True);tx(80,1160,'左：8 − 1.6 − 0.6 = 5.8 升',43,c=BLUE);tx(80,1230,'右：2 − 0.4 + 0.6 = 2.2 升',43,c=BLUE)
save('02-first-step-budget','给出同步排水与净交换的方向、单位和完整手算')

new('内部状态：两次实验并不相同',1510,'实际教学模型计算；0至8秒，每秒一个记录')
legend(205)
for y,key,lab in [(390,'left','左箱水量（升）'),(975,'right','右箱水量（升）')]:
 p=axes(145,y,810,365,0,8,0,10,[0,2,4,6,8],[0,5,10],'时间（秒）',lab)
 curve(p,T['A'],key,BLUE);curve(p,T['B'],key,GOLD,True)
save('03-internal-trajectories','分别画左右内部轨迹，在同一时刻对比A和B','Plot of the saved exact rational model, connecting discrete samples only')

new('可见输出：两条曲线完全重合',1360,'蓝色宽线与金色虚线使用同一坐标，没有错位')
legend(205);p=axes(145,390,810,410,0,8,0,10,[0,2,4,6,8],[0,5,10],'时间（秒）','两箱总水量（升）')
curve(p,T['A'],'sum',BLUE,width=13);curve(p,T['B'],'sum',GOLD,True,width=5)
box(48,975,966,290)
for x,t in [(90,'时间（秒）'),(390,'A 总量'),(700,'B 总量')]:tx(x,990,t,38,b=True)
for n in range(3):
 y=1060+66*n
 for x,t in [(120,str(n)),(415,f"{T['A'][n]['sum']['litres']:g} 升"),(725,f"{T['B'][n]['sum']['litres']:g} 升")]:tx(x,y,t,39)
save('04-output-overlap','用忠实重合曲线和小表证明数据相同而非显示器停住','Plot and table of saved rational results; no artificial offsets')

new('总量账：内部转移相互抵消',1260,'以第一轮为例；箱间交换没有把水送出系统')
for y,lab,expression,c in [(235,'左箱','8 − 1.6 − 0.6',BLUE),(465,'右箱','2 − 0.4 + 0.6',TEAL)]:
 box(48,y,966,170);tx(80,y+18,lab,41,c,b=True);tx(525,y+72,expression,55,c,anchor='mt')
# Explicit visual pairing of equal magnitude opposite signs, no false extra flow.
line([(848,380),(977,380),(977,600),(848,600)],RED,5);tx(80,700,'−0.6 与 +0.6 相加为0',47,c=RED,b=True)
arrow(531,800,531,875,GRAY);box(48,920,966,250)
tx(531,950,'总量：10 − 2 = 8 升',49,b=True,anchor='mt');tx(531,1045,'下一轮总量 = 本轮总量 × 0.8',42,c=TEAL,b=True,anchor='mt')
save('05-transfer-cancels','把原始收支相加，解释总量规律对所有轮都成立')

new('一条线，藏着许多种分配',1130,'坐标表示初始水量；不是水箱的空间位置')
p=axes(150,340,765,570,0,10,0,10,[0,2,5,8,10],[0,2,5,8,10],'初始左箱水量（升）','初始右箱水量（升）')
line([p(0,10),p(10,0)],TEAL,8)
for x,y,lab,c,dx,dy in [(8,2,'A (8, 2)',BLUE,0,-110),(2,8,'B (2, 8)',GOLD,20,-62),(5,5,'C (5, 5)',TEAL,-175,25)]:
 xx,yy=p(x,y);d.ellipse((xx-11,yy-11,xx+11,yy+11),fill=c);tx(xx+dx,yy+dy,lab,39,c,b=True)
# A short direction arrow parallel to the line, separate from point labels.
a=p(2.2,6.6);b=p(4,4.8);arrow(*a,*b,GRAY);tx(720,340,'左 +1',38,c=GRAY);tx(720,405,'右 −1',38,c=GRAY)
tx(531,1040,'沿这条线：初始总量始终是10升',41,c=TEAL,b=True,anchor='mt')
save('06-hidden-direction','展示状态平面里的不可区分分配与相消方向')

new('相同已知加水，仍然分不出来',1260,'每轮末尾加水；A、B都收到同一套指令')
for x,t,v in [(270,'左箱','+0.3 升'),(790,'右箱','+0.1 升')]:
 tx(x,220,t,43,b=True,anchor='mt');arrow(x,310,x,420,TEAL);tx(x,455,v,49,c=TEAL,b=True,anchor='mt')
box(48,585,966,345)
for x,t in [(80,'时间（秒）'),(390,'A 总量'),(700,'B 总量')]:tx(x,605,t,38,b=True)
for n in range(3):
 y=685+75*n
 for x,t in [(120,str(n)),(405,f"{U['A'][n]['sum']['litres']:g} 升"),(715,f"{U['B'][n]['sum']['litres']:g} 升")]:tx(x,y,t,42)
tx(531,1000,'下一轮总量',45,b=True,anchor='mt');tx(531,1080,'= 本轮总量 × 0.8 + 0.3 + 0.1',43,c=TEAL,anchor='mt')
save('07-known-input','说明同输入指两次实验的指令相同，并显示实际输出仍相同','Original diagram plus saved model values with known input')

new('新实验：这回只看左箱',1370,'取消加水；不提供旧实验的总量10升')
tx(260,225,'可测左箱',44,c=BLUE,b=True,anchor='mt');tx(795,225,'未知右箱',44,c=GRAY,b=True,anchor='mt')
tank(170,330,8,BLUE,w=180,h=265);tank(705,330,0,unknown=True,w=180,h=265)
arrow(665,455,395,455,GRAY);tx(531,355,'仍会交换水',36,c=GRAY,anchor='mt')
# Arrow is explicitly non-directional influence below: replace arrowhead with double arrow.
arrow(395,455,665,455,GRAY)
box(48,800,966,300);tx(80,825,'观察者手里只有：',43,b=True)
tx(95,920,'0 秒：左箱 8 升',47,c=BLUE);tx(95,1005,'1 秒：左箱 5.8 升',47,c=BLUE)
tx(48,1170,'右箱起点叫 r；现在还没有把答案告诉他。',39);tx(48,1245,'双向连线表示可交换，不表示本轮流向。',37,c=GRAY)
save('08-left-only-sensor','明确新测量实验的信息集，用不透明右箱避免泄露未知量')

new('从左箱的变化，找回右箱初值',1390,'只用两次左箱读数，间隔一轮；不借用总量')
for y,num,title,eq in [(235,'①','列出左箱这一轮的收支','5.8 = 8 − 1.6 − 0.1 × (8 − r)'),(545,'②','合并已经知道的部分','5.8 = 5.6 + 0.1 × r'),(855,'③','先减5.6，再除以0.1','r = (5.8 − 5.6) ÷ 0.1 = 2 升')]:
 box(48,y,966,220);tx(80,y+22,num+' '+title,43,b=True);tx(531,y+111,eq,40,c=BLUE,anchor='mt')
 if y<855:arrow(531,y+232,531,y+293,GRAY)
tx(48,1150,'中间的0.2是代数剩余项，不是反向水流。',39,c=RED);tx(48,1230,'核回：8 − 1.6 − 0.6 = 5.8 升。',42)
save('09-recover-right','不跳步展示收支展开、减已知项、除系数的操作')

new('两次记录，是否带来两条线索？',1900,'两张图的横纵轴，都表示初始左右水量')
for y,kind in [(425,'sum'),(1210,'left')]:
 if kind=='sum':
  tx(48,215,'总量读数：10 升、8 升',44,b=True);tx(48,288,'两条约束其实都说：初始合计10',39,c=GRAY)
 else:
  tx(48,1000,'左箱读数：8 升、5.8 升',44,b=True);tx(48,1073,'两条不同约束，只在（8，2）相交',39,c=GRAY)
 p=axes(150,y,765,430,0,10,0,10,[0,5,8,10],[0,2,5,10],'初始左箱（升）','初始右箱（升）')
 if kind=='sum':
  line([p(0,10),p(10,0)],BLUE,12);dashed([p(0,10),p(10,0)],GOLD,5)
 else:
  line([p(8,0),p(8,10)],BLUE,7);line([p(48/7,10),p(58/7,0)],GOLD,7)
  xx,yy=p(8,2);d.ellipse((xx-11,yy-11,xx+11,yy+11),fill=RED);tx(xx-190,yy+20,'(8, 2)',40,c=RED,b=True)
tx(48,1820,'蓝色：第0次读数；金色：第1次读数。',39)
save('10-two-constraints','初态平面中重合约束与唯一交点对照，避免时间坐标混淆')

new('系数表：把两条水量账放整齐',1770,'列对应本轮左、右；行对应下一轮左、右')
# Coefficients remain large and aligned; no compact math font subscripts.
tx(500,225,'本轮左',40,b=True,anchor='mt');tx(790,225,'本轮右',40,b=True,anchor='mt')
for y,lab,a,b in [(325,'下一轮左',0.7,0.1),(445,'下一轮右',0.1,0.7)]:
 tx(70,y,lab,41,b=True);tx(500,y,str(a),52,c=BLUE,anchor='mt');tx(790,y,str(b),52,c=BLUE,anchor='mt')
box(48,590,966,130);tx(531,620,'第一行：0.7 × 8 + 0.1 × 2 = 5.8',42,c=BLUE,anchor='mt')
tx(48,805,'再问：两次读数怎样依赖初始水量？',43,b=True)
for y,lab,r0,r1,note,c in [(925,'量总量','1          1','0.8        0.8','第二行 = 第一行 × 0.8',GRAY),(1330,'量左箱','1          0','0.7        0.1','第二行带来了右箱信息',TEAL)]:
 box(48,y,966,340);tx(80,y+15,lab,43,c,b=True);tx(100,y+100,'第0次',38);tx(100,y+175,'第1次',38)
 tx(550,y+20,'初始左',36,c,anchor='mt');tx(800,y+20,'初始右',36,c,anchor='mt')
 for yy,row in [(y+92,r0.split()),(y+167,r1.split())]:
  tx(550,yy,row[0],46,c,anchor='mt');tx(800,yy,row[1],46,c,anchor='mt')
 tx(531,y+260,note,40,c,anchor='mt')
save('11-observation-matrix','同一数例演示一行系数的乘加，再比较两行是否重复')

new('交换变弱，右箱传来的痕迹变小',1460,'新候选：P (8, 2)；Q (8, 3)。左箱起点都为8')
for top,i,range_ in [(260,0,(5.75,5.95)),(865,1,(6.30,6.39))]:
 n=N[i];g=n['coupling'];vals=[v['litres']for v in n['new_comparison']['second_readings']];a,b=range_;x0,x1=180,950
 def px(v):return x0+(v-a)/(b-a)*(x1-x0)
 tx(48,top,('交换10%' if i==0 else '交换1%')+'：第二次左箱读数',44,b=True)
 tx(48,top+80,('自身系数0.7' if i==0 else '自身系数0.79'),39,c=GRAY)
 for j,(val,label,c) in enumerate(zip(vals,['P','Q'],[BLUE,GOLD])):
  yy=top+210+j*130;line([(px(val-.02),yy),(px(val+.02),yy)],c,13);d.ellipse((px(val)-10,yy-10,px(val)+10,yy+10),fill=INK)
  tx(65,yy,label,43,c,b=True,anchor='lm');tx(px(val),yy-65,f'{val:g}',39,c,b=True,anchor='mt')
 yy=top+420;line([(x0,yy),(x1,yy)],INK,3)
 ticks=[5.75,5.85,5.95] if i==0 else [6.30,6.34,6.39]
 for tick in ticks:
  xx=px(tick);line([(xx,yy-8),(xx,yy+8)],INK,3);tx(xx,yy+18,f'{tick:g}',36,anchor='mt')
 tx(531,top+500,f"读数差 {n['new_comparison']['separation']['litres']:g} 升",42,b=True,anchor='mt')
# These x ranges deliberately differ; written twice to make the scale change visible.
tx(48,1405,'横轴单位升；两图尺度不同。粗线是 ±0.02升。',37,c=GRAY)
save('12-weak-coupling','更换候选对并用带误差范围的点图展示弱交换信息的缩小','Deterministic model outputs and specified error bounds, not sensor measurements')

new('同样的测量偏差，估计能差多远？',1550,'真初态始终（8，2）；第一次 +0.02，第二次 −0.02升')
for top,i in [(240,0),(830,1)]:
 n=N[i];c=BLUE if i==0 else RED;box(48,top,966,490,outline=c)
 tx(80,top+20,'交换'+('10%'if i==0 else'1%'),47,c,b=True)
 tx(80,top+115,'真实左量：8 → '+f"{n['true_left1']['litres']:g} 升",42)
 tx(80,top+195,'读成左量：8.02 → '+f"{n['measured_left1']['litres']:g} 升",42)
 tx(80,top+285,'直接套式推算右箱起点：',39)
 tx(531,top+355,f"{n['inferred_right']['litres']:g} 升",66,c,b=True,anchor='mt')
tx(48,1385,'右箱实际仍是2升。负的是估计，不是水。',41,c=RED,b=True);tx(48,1470,'这是固定一对误差的算例，没有运行滤波器。',38,c=GRAY)
save('13-noise-amplification','把真值、带误差读数、估计结果分开，解释非物理负估计','Exact deterministic error propagation using saved rational results')

new('看得很准，仍可能看不全',1140,'两箱的秘密，藏在没有进入读数的差别里')
for y,vals,c in [(270,(8,2),BLUE),(710,(2,8),GOLD)]:
 tank(150,y,vals[0],c,w=180,h=220);tank(430,y,vals[1],c,w=180,h=220)
 arrow(655,y+110,755,y+110,c);box(780,y+20,220,180,outline=c);tx(890,y+50,'合计',42,anchor='mt');tx(890,y+110,'10 升',55,c,b=True,anchor='mt')
im.save(ROOT/'cover.png');meta.append(dict(file='cover.png',purpose='两种内部状态汇向同一个读数，概括核心问题',identity='Original cover illustration',width=W,height=im.height,minimum_font_px=minimum,effective_minimum_at_354px=minimum/3))
# The genuine photograph is deliberately not decoded/re-encoded by this builder.
photo=Image.open(AS/'14-kalman-eth-original.jpg');photo.load();assert photo.size==(3168,2112)
meta.append(dict(file='assets/14-kalman-eth-original.jpg',purpose='介绍1960/1963原论文作者，明确照片拍于2007年',identity='Unmodified genuine ETH portrait, CC BY-SA 4.0, not model equipment',width=photo.width,height=photo.height,minimum_font_px=None))
assert not overflow,overflow
assert all(m['minimum_font_px'] is None or m['minimum_font_px']>=36 for m in meta)
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('13 original body diagrams + original cover rendered; unchanged genuine portrait checked; bounds PASS')
