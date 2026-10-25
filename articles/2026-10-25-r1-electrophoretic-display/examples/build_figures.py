"""New electrophoretic display illustrations, CC BY 4.0. Code CC0-1.0.
Canvas validation API adapted from the r1 Quickselect generator.
"""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'examples/results.json').read_text())
CANDIDATES=['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc']
FONT=next((p for p in CANDIDATES if Path(p).exists()),None)
if not FONT:raise RuntimeError('Chinese font not found')
CMAP=TTFont(FONT,fontNumber=0).getBestCmap()
BG='#f8fafc'; INK='#142d42'; BLUE='#176297'; GREEN='#166c57'; ORANGE='#9c4d0d'
meta=[]
class Canvas:
 def __init__(self,title):
  self.im=Image.new('RGB',(1062,4000),BG);self.d=ImageDraw.Draw(self.im);self.boxes=[];self.bottom=0
  self.text(50,30,title,48)
 def text(self,x,y,s,size=42,color=INK,box=None):
  assert size>=40
  assert all(ord(c) in CMAP for c in s if not c.isspace()),s
  f=ImageFont.truetype(FONT,size);b=self.d.textbbox((x,y),s,font=f)
  assert b[0]>=0 and b[1]>=0 and b[2]<=1062 and b[3]<=4000,(s,b)
  if box:assert box[0]+5<=b[0] and box[1]+5<=b[1] and b[2]<=box[2]-5 and b[3]<=box[3]-5,(s,b,box)
  for old in self.boxes:
   q=old[0]
   assert min(b[2],q[2])<=max(b[0],q[0]) or min(b[3],q[3])<=max(b[1],q[1]),(s,old[1])
  self.d.text((x,y),s,font=f,fill=color);self.boxes.append((b,s,size));self.bottom=max(self.bottom,b[3])
  px=self.im.crop(b).convert('L');lo,hi=px.getextrema();assert hi-lo>90,(s,lo,hi)
  assert sum(1 for v in px.getdata() if v<180)>len(s)*8,s
 def line(self,a,b,color=BLUE,dashed=False):
  if dashed:
   dx=b[0]-a[0];dy=b[1]-a[1];n=max(1,int(math.hypot(dx,dy)/18))
   for i in range(0,n,2):self.d.line((a[0]+dx*i/n,a[1]+dy*i/n,a[0]+dx*min(i+1,n)/n,a[1]+dy*min(i+1,n)/n),fill=color,width=5)
  else:self.d.line((*a,*b),fill=color,width=5)
  self.bottom=max(self.bottom,a[1],b[1])
 def arrow(self,a,b,color=BLUE,dashed=False):
  self.line(a,b,color,dashed);ang=math.atan2(b[1]-a[1],b[0]-a[0]);pts=[b]
  for delta in [-.55,.55]:pts.append((b[0]-20*math.cos(ang+delta),b[1]-20*math.sin(ang+delta)))
  self.d.polygon(pts,fill=color)
 def card(self,x,y,w,h,s,fill='#e5eef7',color=INK):
  b=(x,y,x+w,y+h);self.d.rounded_rectangle(b,radius=16,fill=fill)
  f=ImageFont.truetype(FONT,42);width=self.d.textlength(s,font=f)
  self.text(x+(w-width)/2,y+(h-60)/2,s,42,color,b);self.bottom=max(self.bottom,y+h)
 def save(self,name,purpose):
  im=self.im.crop((0,0,1062,math.ceil(self.bottom+45)));p=ROOT/'assets'/name;im.save(p)
  assert Image.open(p).size==im.size
  meta.append(dict(file='assets/'+name,width=im.width,height=im.height,min_font_px=min(z[2] for z in self.boxes),effective_min_font_at_354=round(min(z[2] for z in self.boxes)/3,2),identity='原创教学示意；执行数值来自 results.json',purpose=purpose,checks=['canvas','declared-box','text-overlap','font-size','contrast','glyph-cmap','ink-pixels','actual-dimensions']))

D=DATA;P=D['parameters']
V=P['voltage_v']; pulse=P['pulse_s']; crossing=D['crossing_s']
trace_end=max(z['t_s'] for row in D['reset_trace'] for z in row['points'])
# Coordinates, schematic particle counts and conceptual gray swatches are layout.
# Physical input labels and all quantitative geometry read the computed JSON.
def dot(c,x,y,white=False):
 c.d.ellipse((x-24,y-24,x+24,y+24),fill='white' if white else '#172c3c',outline=INK,width=3);c.bottom=max(c.bottom,y+24)
def cell(c,x,y,blacktop=True,w=380):
 c.d.rounded_rectangle((x,y,x+w,y+250),radius=60,fill='#dfeaf0',outline=BLUE,width=4)
 for i in range(5):
  dot(c,x+60+i*(w-120)/4,y+60,not blacktop);dot(c,x+60+i*(w-120)/4,y+190,blacktop)
 c.line((x,y-25),(x+w,y-25),GREEN);c.line((x,y+275),(x+w,y+275),ORANGE)
 c.bottom=max(c.bottom,y+275)
def plot(c,points,color=BLUE,width=6):
 c.d.line(points,fill=color,width=width,joint='curve');c.bottom=max(c.bottom,max(z[1] for z in points))

c=Canvas('一页字，留在颜料的位置里')
c.text(65,135,'电泳显示：用电压搬动带电颜料',44)
cell(c,150,335,True,760)
c.text(65,230,'眼睛看向这一侧',44,GREEN);c.arrow((530,285),(530,325),GREEN)
c.text(65,710,'更新：改变位置');c.arrow((470,748),(610,748));c.text(650,710,'改变明暗')
c.text(65,835,'保持：材料稳定性让图案留下',44)
c.text(65,940,'断电仍可见 ≠ 整台阅读器不耗电',42,ORANGE)
c.save('00-cover.png','封面用颜料前后位置连接电压更新与图像保持')

c=Canvas('看得见，靠光往返一次')
c.d.rectangle((130,510,930,640),fill='#dfeaf0',outline=INK,width=4)
c.text(280,665,'颜料层：反射或吸收',44)
c.arrow((150,190),(390,500),ORANGE);c.text(75,115,'环境光',44,ORANGE)
c.arrow((405,500),(700,200),GREEN);c.text(700,115,'眼睛',44,GREEN)
c.d.ellipse((365,510,445,590),fill='white',outline=INK,width=3)
c.d.ellipse((645,510,725,590),fill=INK)
c.arrow((530,190),(680,500),ORANGE)
c.text(65,790,'白颜料散射较多光；黑颜料吸收更多',42)
c.text(65,880,'暗处需要外界照明或前照灯',44)
c.text(65,970,'前照灯照亮表面，不是像素自己发光',42)
c.save('01-light.png','区分反射式颜料与发光像素，并说明前照明的作用')

c=Canvas('把一个小区域从侧面切开')
c.text(65,135,'上：观看侧；下：电路背板',44)
cell(c,145,350,False,770)
c.text(220,235,'透明公共电极：V上 = 0 V',42,GREEN)
c.text(220,690,'像素电极：V下可正可负',42,ORANGE)
c.text(65,810,'透明液体中：白负、黑正（本文约定）',42)
c.text(65,900,'外壳将颗粒约束在局部，不等于像素边界',40)
c.text(65,990,'示意把颗粒排齐；实物并非整齐双层',42)
c.save('02-section.png','标观看侧、两电极、透明液体、两种粒子与教学极性约定')

c=Canvas('翻转电压，两种颗粒反向移动')
for i,(title,blacktop,sign) in enumerate([(f'V下 = +{V:g} V',True,'正'),(f'V下 = −{V:g} V',False,'负')]):
 x=70+i*520;c.text(x,145,title,42)
 cell(c,x,345,blacktop,400)
 c.arrow((x+80,760 if i==0 else 665),(x+80,665 if i==0 else 760),INK)
 c.arrow((x+310,665 if i==0 else 760),(x+310,760 if i==0 else 665),BLUE)
 c.text(x,800,'黑正',42);c.text(x+255,800,'白负',42,BLUE)
 c.text(x,910,'观看面偏黑' if blacktop else '观看面偏白',42)
c.text(65,1040,'电场从高电势指向低电势',44,GREEN)
c.text(65,1130,'正粒子顺电场；负粒子逆电场',44)
c.save('03-polarity.png','同一观看方向并列两种电压，明确粒子方向由符号决定')

c=Canvas('从电压，算到一段位移')
c.text(65,140,f"教学间距 d = {P['gap_m']*1e6:.0f} µm",44)
c.text(65,225,f"电压差 = {P['voltage_v']:.0f} V；E = {D['field_v_m']/1000:.0f} kV/m",44)
c.text(65,310,f"设迁移率 µ = {P['mobility_m2_v_s']/1e-10:g}e−10 m²/(V·s)",42)
c.text(65,405,f"v = µE = {D['speed_um_s']:.0f} µm/s",50,GREEN)
y=620
c.line((110,y),(950,y),INK)
for t in [crossing*i/3 for i in range(4)]:
 x=110+t/D['crossing_s']*840;c.line((x,y-20),(x,y+20),INK)
 c.text(x-25,y+65,f'{t:.1f}',40)
 c.text(x-25,y-100,f'{t*D["speed_um_s"]:.0f}',40,BLUE)
c.text(65,760,'下轴：时间 / s；上轴：位移 / µm',40)
c.text(65,865,f"{P['pulse_s']:.2f} s脉冲 → {D['pulse_displacement_um']:.0f} µm",48,ORANGE)
c.text(65,970,'仅匀场漂移量级；不是商用屏刷新时间',42)
c.save('04-drift.png','共轴时间尺把迁移率、电场、速度、位移依次算通')

c=Canvas('胶囊是容器，像素是可控区域')
c.text(65,140,'俯视概念图：背板划成独立电极',42)
for row in range(2):
 for col in range(3):
  x=130+col*270;y=280+row*250
  c.d.rectangle((x,y,x+250,y+230),outline=ORANGE,width=6)
  for dx,dy in [(65,65),(170,75),(115,175)]:
   c.d.ellipse((x+dx-47,y+dy-47,x+dx+47,y+dy+47),fill='#e4edf0',outline=BLUE,width=3)
  c.d.rectangle((x+8,y+190,x+35,y+217),fill=GREEN)
c.bottom=780
c.text(65,845,'橙框：像素电极；蓝圈：微胶囊',42)
c.text(65,930,'绿块：薄膜晶体管，负责选通像素',42)
c.text(65,1020,'同一像素可覆盖多颗胶囊；并非一一对应',40)
c.text(65,1110,'行选通、列给电压，把一幅图分配到各处',40)
c.save('05-pixels.png','区分材料容器和矩阵寻址，不把每胶囊等同像素')

c=Canvas('相同短脉冲，保留不同的过去')
c.text(65,135,'p = 代表性黑粒子高度 ÷ 间距',42)
c.text(65,215,'0是底部，1是观看面；p不是灰度',42)
for j,h in enumerate(D['history']):
 y=390+j*300;c.line((160,y),(930,y),'#a9bbc5')
 for val,label,col,dy in [(h['start'],'起点',ORANGE,-100),(h['end'],'终点',GREEN,60)]:
  x=160+770*val;dot(c,x,y);c.text(max(65,min(800,x-40)),y+dy,f'{label} {val:.1f}',40,col)
 c.arrow((160+770*h['start'],y-45),(160+770*h['end'],y-45),BLUE)
c.text(65,940,f"两处都加 +{V:g} V、{pulse:.2f} s，位移上限{D['pulse_displacement_um']/(P['gap_m']*1e6):.1f}d",40)
c.text(65,1030,'初态不同 → 终态不同：只写目标不够',42)
c.text(65,1120,'裁剪到0～1的教学模型，不预测真实残影',40)
c.save('06-history.png','两行相同位移尺度展示状态历史对终点的影响')

c=Canvas('先统一起点，再写相同目标')
c.text(65,135,f'同一裁剪模型；先−{V:g} V，再+{V:g} V',40)
xp=lambda t:165+t/trace_end*780;yp=lambda p:760-p*450
for p in [0,.5,1]:c.line((165,yp(p)),(945,yp(p)),'#b1c3ce');c.text(65,yp(p)-25,f'{p:g}',40)
for t in [0,crossing,trace_end]:c.text(xp(t)-25,810,f'{t:g}',40)
for row,col in zip(D['reset_trace'],[ORANGE,BLUE]):plot(c,[(xp(z['t_s']),yp(z['p'])) for z in row['points']],col,7)
c.text(700,890,'时间 / s',40)
c.text(65,990,f"0～{crossing:.2f} s：两条轨迹都到p = {D['reset'][0]['erased']:g}",42)
c.text(65,1080,f"再写{pulse:.2f} s：两条都到p = {D['reset'][0]['written']:.1f}",42)
c.text(65,1170,'真实驱动还须处理迟滞、等待和材料状态',40)
c.save('07-reset.png','用同一坐标与实际轨迹显示重置消除教学模型的初态差')

c=Canvas('波形是一段时间表，不是一个电压')
c.text(65,140,'示意工序；不作为任何屏的驱动参数',42)
ys=[325,600,875]
labels=['擦除旧图','往返激活','写入目标']
for y,label in zip(ys,labels):c.text(65,y-100,label,46);c.line((365,y),(950,y),'#b5c5ce')
plot(c,[(365,325),(400,325),(400,400),(900,400),(900,325),(950,325)],BLUE)
plot(c,[(365,600),(390,600),(390,525),(520,525),(520,675),(650,675),(650,525),(780,525),(780,675),(910,675),(910,600),(950,600)],ORANGE)
plot(c,[(365,875),(400,875),(400,800),(700,800),(700,875),(950,875)],GREEN)
c.text(65,1025,'中线为0 V，上方正电压，下方负电压',40)
c.text(65,1110,'颜料往返使表面明暗变化，可能看见闪烁',40)
c.text(65,1200,'快更新、残影、闪烁之间需要针对屏幕调校',40)
c.save('08-waveform.png','分开擦除激活写入三职责，解释可见闪烁来自光学往返')

c=Canvas('灰度有两条不同的路')
c.text(65,145,'单像素：控制颜料分布，改变反射',42)
for i in range(5):
 shade=int(245-i*45);c.d.rectangle((90+i*185,260,245+i*185,425),fill=(shade,shade,shade),outline=INK,width=3)
c.bottom=425;c.text(65,470,'这些色块只表意，不是实测响应曲线',40)
c.text(65,580,'多个黑白像素：用空间比例混合观感',42)
for j,z in enumerate(D['dither']):
 x=90+j*185
 for i,b in enumerate(z['cells']):
  xx=x+(i%4)*38;yy=710+(i//4)*38;c.d.rectangle((xx,yy,xx+35,yy+35),fill=INK if b else 'white',outline='#a1adb5')
 c.text(x,915,f"{z['black_count']}/16",40)
c.text(65,1030,'上：同一像素灰度；下：黑白像素空间抖动',40)
c.text(65,1120,'下图按行填黑便于计数，不是高质量抖动算法',40)
c.save('09-grayscale.png','区分单像素反射灰度与多个二值像素的面积比例')

c=Canvas('保持图像，与整机功耗分开算')
c.text(65,140,f"假设额外更新{P['refresh_energy_j']*1000:g} mJ，基线{P['sleep_power_w']*1e6:g} µW",42)
c.text(65,220,f"观察{P['observation_s']/3600:g}小时；不含前照灯、无线和处理器忙碌",40)
vals=[z['total_j'] for z in D['energy']];scale=750/max(vals)
for i,z in enumerate(D['energy']):
 y=350+i*250;c.text(65,y,f"每小时 {z['updates']} 次更新",42)
 c.d.rectangle((85,y+85,85+z['update_j']*scale,y+145),fill=BLUE)
 c.d.rectangle((85+z['update_j']*scale,y+85,85+z['total_j']*scale,y+145),fill=ORANGE)
 c.text(85,y+160,f"总能量 {z['total_j']:.3f} J",40)
assert all((vals[i]<vals[j]) == (vals[i]*scale<vals[j]*scale) for i in range(len(vals)) for j in range(len(vals)))
c.text(65,1160,'蓝：更新；棕：固定基线项（同一比例尺）',40)
c.text(65,1245,'少量更新时基线项可能占大头；小条并非零',40)
c.save('10-energy.png','使用同一比例尺与假设数据比较更新次数对能量的作用')

c=Canvas('彩色不是把黑白电压多分几档')
c.text(65,140,'路线一：黑白颜料 + 彩色滤片',44)
for i,col in enumerate(['#bf5555','#6ba46b','#648ac2']):
 x=165+i*245;c.d.rectangle((x,270,x+200,320),fill=col);c.d.rectangle((x,380,x+200,470),fill='white',outline=INK,width=3);c.arrow((x+100,215),(x+100,260),ORANGE)
c.text(65,525,'入射与返回光受滤片选择，亮度需权衡',42)
c.text(65,655,'路线二：同一区域放入多种彩色颜料',44)
c.d.rounded_rectangle((150,795,930,1050),radius=50,fill='#e3ebed',outline=BLUE,width=4)
for i,col in enumerate(['white','#c64b4b','#e0b449',INK]):
 for j in range(3):
  x=240+i*190;y=850+j*65;c.d.ellipse((x-22,y-22,x+22,y+22),fill=col,outline=INK,width=2)
c.bottom=1050
c.text(65,1110,'不同颗粒的电荷/迁移响应需要专用波形',42)
c.text(65,1200,'两路线都只画结构，不冒充具体产品配方',42)
c.save('11-color.png','并列滤色片路线与多颜料路线，不以RGB发光像素解释所有彩色电泳屏')

c=Canvas('零伏秒，不保证回到原来的状态')
c.text(65,140,f'同一裁剪模型：+{V:g} V与−{V:g} V各{crossing:.2f} s',40)
for i,p in enumerate(D['zero_volt_seconds']['states']):
 x=150+i*330;c.line((x,360),(x,760),'#9eb1bd');dot(c,x,760-p*400)
 c.text(x-70,830,f'p = {p:.1f}',42)
c.text(65,245,'起点');c.text(390,245,'正脉冲后');c.text(720,245,'负脉冲后')
c.text(65,955,'电压×时长相消，但到边界后不能继续前进',40)
c.text(65,1040,'返程失去原先的起点信息，终态发生变化',40)
c.text(65,1125,'真实DC平衡用于控制偏置，不能单独保证图像',40)
c.save('12-balance.png','反例展示电压时间积分为零与位置回原处不是一回事')

c=Canvas('移动快慢变了，同一脉冲就不够')
c.text(65,140,'只改变假定迁移率；不是温度实测曲线',42)
vals=[z['crossing_s'] for z in D['mobility_comparison']];scale=780/max(vals)
for i,z in enumerate(D['mobility_comparison']):
 y=330+i*330;c.text(65,y,f"µ = {z['mobility'] / 1e-10:g}e−10 m²/(V·s)",42)
 c.d.rectangle((100,y+100,100+z['crossing_s']*scale,y+180),fill=BLUE if i==0 else ORANGE)
 c.text(100,y+210,f"走完间距：{z['crossing_s']:.2f} s",42)
assert vals[0]*scale<vals[1]*scale
c.text(65,1080,'真实温度会改变响应，控制器需对应波形',42)
c.text(65,1170,'具体补偿数据来自面板标定，不能套本图',42)
c.save('13-mobility.png','共轴迁移率反例解释为何速度和驱动时间需要标定')

for f in sorted((ROOT/'originals/photos').glob('*')):
 with Image.open(f) as im:meta.append({'file':str(f.relative_to(ROOT)),'width':im.width,'height':im.height,'identity':'第三方项目文档实拍原件；不改像素','purpose':'真实设备或可见显示结果','min_font_px':None})
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(f'{len(meta)} images documented; all generated geometry checks passed.')
