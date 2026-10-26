"""New piezo inkjet illustrations, CC BY 4.0. Code CC0-1.0.
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
# All coordinates below are layout. Quantitative lengths use JSON values.
def poly(c,pts,color=BLUE,width=7):
 c.d.line(pts,fill=color,width=width,joint='curve');c.bottom=max(c.bottom,max(y for x,y in pts))
def chamber(c,y,expanded=False):
 top=y+(0 if expanded else 20);bottom=y+200-(0 if expanded else 20)
 c.d.rectangle((240,top,810,bottom),fill='#dbedf5',outline=BLUE,width=5)
 c.d.rectangle((300,top-25,730,top),fill='#e6ac6e')
 c.d.rectangle((300,bottom,730,bottom+25),fill='#e6ac6e')
 c.line((100,y+100),(240,y+100),BLUE)
 c.line((810,y+85),(910,y+85),BLUE);c.line((810,y+115),(910,y+115),BLUE)
 c.d.arc((885,y+85,930,y+115),-90,90,fill=BLUE,width=5)
 c.bottom=max(c.bottom,bottom+25)
def drop(c,x,y,r=36):
 c.d.ellipse((x-r,y-r,x+r,y+r),fill='#cce5f2',outline=BLUE,width=5);c.bottom=max(c.bottom,y+r)

c=Canvas('一滴墨水，先听见腔内的波')
c.text(55,130,'电压改变壁面，压力驱动液体',46)
chamber(c,300)
c.text(65,245,'供墨');c.text(370,225,'压电驱动壁',44,ORANGE)
c.text(370,370,'充液腔体',46)
c.text(805,550,'喷嘴',42)
c.arrow((850,610),(850,690));drop(c,850,760,45)
c.text(70,650,'形变');c.arrow((200,690),(310,690));c.text(345,650,'声波')
c.text(70,780,'液柱');c.arrow((200,820),(310,820));c.text(345,780,'断滴')
c.text(65,940,'关键是时序，不只是电压幅度',46,GREEN)
c.save('00-cover.png','独立封面：从驱动壁到喷嘴外液滴的因果链')

c=Canvas('先辨认液体走过的路')
c.text(60,135,'管式喷头的概念剖面；不按比例',40)
c.d.rectangle((70,265,200,555),fill='#dbedf5',outline=BLUE,width=5)
c.text(65,195,'储液器',42)
chamber(c,320)
c.text(330,250,'电极与压电陶瓷',42,ORANGE)
c.text(330,390,'液体腔',46)
c.text(725,615,'喷嘴 / 液面',42)
c.line((895,590),(920,440),INK)
c.text(65,715,'外界空气在右侧；液体尚未滴出',42)
c.text(65,805,'平衡靠压差、曲率和润湿共同维持',42)
c.save('01-structure.png','指认储液器、驱动部位、腔、喷嘴及弯月面')

c=Canvas('容积变化先产生压力扰动')
chamber(c,260,True)
c.text(65,125,'膨胀：壁面外移，先出现负压',44)
c.arrow((480,235),(480,190),ORANGE)
c.arrow((480,485),(480,535),ORANGE)
c.text(65,570,'液体从入口补入，液面也可能回缩',42)
chamber(c,800,False)
c.text(65,665,'回缩：壁面内移，先出现正压',44)
c.arrow((480,745),(480,790),ORANGE)
c.arrow((480,1050),(480,1010),ORANGE)
c.text(65,1100,'这里的正负，相对于静止工作压力',42)
c.text(65,1190,'电压极性与变形方向须看具体喷头',42)
c.save('02-wall-motion.png','同一剖面显示腔体膨胀/回缩及压力符号')

c=Canvas('挤进多少体积，不能都算成液滴')
c.text(65,140,f"教学输入：自由容积减少 {P['stroke_m3']*1e15:.0f} pL",44)
c.text(65,220,'自由：没有液压反作用时的位移',40)
vals=[P['stroke_m3']*1e15,0];scale=850/vals[0]
c.d.rectangle((80,335,80+vals[0]*scale,420),fill='#e6ac6e')
c.text(90,450,'堵住两端：压缩液体 + 撑开壁面',42)
c.text(90,540,f"Δp = ΔV / C = {D['closed_pressure_pa']/1000:.0f} kPa",48,ORANGE)
c.arrow((530,640),(530,720))
c.text(65,765,'打开液路后，增加两条体积去向',44)
c.card(65,865,430,95,'喷嘴流出');c.card(565,865,430,95,'入口倒流 / 补液')
c.text(65,1030,'C × dp/dt = 挤压速率 − 净流出率',40)
c.text(65,1110,'封闭算例只给量级，不给真实波形',42)
c.save('03-volume-account.png','用体积守恒区分封闭压力估算与开放液路的流量')

c=Canvas('反射把一次形变带回驱动区')
c.text(65,135,'储液器近似低声阻抗端；教学路径',40)
x0=145;x1=875
for y in [280,495,710]:c.line((x0,y),(x1,y),'#8299a8')
c.text(65,205,'储液器',40);c.text(710,205,'驱动区',40)
c.arrow((x1,280),(x0,280),BLUE);c.text(300,325,'负压波向左传播',42,BLUE)
c.arrow((x0,495),(x1,495),ORANGE);c.text(300,540,'反射为正压波',42,ORANGE)
c.arrow((x1,710),(985,710),GREEN);c.text(300,755,'回缩正压与返回正压同号',42,GREEN)
c.text(65,875,f"单程 {P['acoustic_length_m']*1000:.0f} mm ÷ {P['sound_speed_m_s']:.0f} m/s",42)
c.text(65,955,f"= {D['acoustic']['one_way_us']:.0f} µs；往返 {D['acoustic']['roundtrip_us']:.0f} µs",48,ORANGE)
c.text(65,1060,'喷嘴、入口和柔性壁都会改变反射',42)
c.save('04-reflection.png','画出负压波去程、变号回程及驱动叠加的位置')

c=Canvas('同一幅度，换时刻就换了叠加')
c.text(65,135,'线性脉冲教学模型；纵轴均为 kPa',40)
x0=170;xspan=800;mint=-4;maxt=52
xp=lambda t:x0+(t-mint)/(maxt-mint)*xspan
for j,(key,title) in enumerate([('matched','回缩配准返回波'),('late','回缩晚到')]):
 top=245+j*650;zero=top+305
 c.text(65,top,title,44,GREEN if j==0 else ORANGE)
 for v in [-10,0,20]:
  yy=zero-v*9;c.line((x0,yy),(970,yy),'#b3c3cf');c.text(55,yy-28,str(v),40)
 for t in [0,20,40]:c.text(xp(t)-20,zero+130,str(t),40)
 c.text(750,zero+200,'时间 / µs',40)
 ck='compression_matched' if j==0 else 'compression_late'
 for k,col in [('reflected','#9f6500'),(ck,'#6b5ba7'),(key,BLUE)]:
  poly(c,[(xp(w['t_us']),zero-w[k]*9) for w in D['acoustic']['wave']],col,7 if k==key else 4)
 peak=D['acoustic']['matched_peak' if j==0 else 'late_peak']
 c.text(600,top+55,f"合成峰值 {peak:.0f}",42,BLUE)
c.text(65,1550,'蓝：合成；棕：反射；紫：回缩产生',40)
c.text(65,1630,'三角脉冲是设定形状，非实测压力',42)
c.save('05-wave-timing.png','共轴对比两种时序，分量相加的峰值由计算产生')

c=Canvas('喷嘴里的一小段液体，怎样加速')
c.text(65,140,'局部近似：圆管截面，流向向右',42)
c.d.rectangle((230,310,820,465),fill='#dbedf5',outline=BLUE,width=5)
c.arrow((70,390),(215,390),GREEN);c.arrow((990,390),(840,390),ORANGE)
c.text(70,230,'上游压力',42,GREEN);c.text(770,530,'毛细压力',42,ORANGE)
c.arrow((670,280),(420,280),ORANGE);c.text(375,200,'黏性阻力',42,ORANGE)
c.text(285,360,'Q：体积流量',44)
c.text(65,650,'M × dQ/dt = p − p毛细 − RQ',42)
c.text(65,750,'压力差先加速；速度大了，阻力变大',42)
c.text(65,850,f"本例毛细量级：{D['capillary_pa']/1000:.0f} kPa",46,ORANGE)
c.text(65,945,'这不是断滴模型：没有计算液面形状',42)
c.save('06-nozzle-forces.png','压力、毛细和黏性相抵后剩余部分造成惯性加速')

c=Canvas('压力保持，流量也不会瞬间到顶')
c.text(65,135,f"设喷嘴上游 {P['drive_pa']/1000:.0f} kPa，持续 {P['duration_s']*1e6:.0f} µs",42)
x0=180;xr=970;yp=lambda q:700-q*190
for q in [0,1,2]:
 c.line((x0,yp(q)),(xr,yp(q)),'#b3c3cf');c.text(65,yp(q)-25,str(q),40)
for t in [0,10,20]:c.text(x0+t/20*(xr-x0)-20,735,str(t),40)
poly(c,[(x0+z['t_us']/20*(xr-x0),yp(z['q_pl_us'])) for z in D['curve']])
c.text(65,195,'流量 / pL每µs',40);c.text(760,795,'时间 / µs',40)
c.text(65,860,'曲线下的面积，才是流出的体积',44)
c.text(65,955,f"末端流量 {D['end']['q_pl_us']:.3f} pL/µs",44,BLUE)
c.text(65,1045,f"累计体积 {D['end']['volume_pl']:.2f} pL",48,GREEN)
c.text(65,1155,'只积分这段正压；尚未判断是否断滴',42)
c.save('07-flow-curve.png','实际解析曲线显示惯性滞后，明确瞬时流量与累计体积')

c=Canvas('液柱断裂，发生在喷嘴外的自由表面')
for j,label in enumerate(['凸出','拉长','缩颈','分离']):
 x=130+j*265;c.text(x-45,145,label,44)
 c.line((x-50,250),(x-50,330));c.line((x+50,250),(x+50,330))
 if j==0:
  c.d.pieslice((x-50,280,x+50,380),0,180,fill='#cce5f2',outline=BLUE,width=4)
 elif j==1:
  c.d.polygon([(x-45,330),(x-22,410),(x-20,510),(x+20,510),(x+22,410),(x+45,330)],fill='#cce5f2')
  drop(c,x,540,42)
 elif j==2:
  c.d.polygon([(x-40,330),(x-6,410),(x-15,510),(x+15,510),(x+6,410),(x+40,330)],fill='#cce5f2')
  drop(c,x,550,45);c.arrow((x-90,410),(x-14,410),ORANGE)
 else:
  c.d.arc((x-40,295,x+40,360),0,180,fill=BLUE,width=5)
  drop(c,x,460,15);drop(c,x,610,45)
c.text(65,735,'细颈可继续变细，主滴与喷嘴分开',42)
c.text(65,825,'剩余细丝可能并入主滴，也可能成小滴',40)
c.text(65,915,'这里画的是机制，不是计算出的轮廓',42)
c.save('08-breakup.png','原创四阶段形状说明颈部与卫星滴；不替代真实过程图')

c=Canvas('同样的压力，黏度改变响应')
c.text(65,135,'其余条件相同；只比较局部流量模型',40)
v=D['viscosity_comparison'];scale=730/max(z['volume_pl'] for z in v)
lengths=[]
for j,z in enumerate(v):
 y=270+j*270;c.text(65,y,f"黏度 {z['mu_mpa_s']:.0f} mPa·s",42)
 length=z['volume_pl']*scale;lengths.append(length)
 c.d.rectangle((85,y+85,85+length,y+145),fill='#8fc5dc')
 c.text(85,y+165,f"{z['volume_pl']:.2f} pL",44,BLUE)
assert sorted(range(len(v)),key=lambda i:v[i]['volume_pl'])==sorted(range(len(v)),key=lambda i:lengths[i])
c.text(65,1145,'条长共用同一体积尺度',42)
c.text(65,1230,'多流出液体 ≠ 卫星更少或打印更好',42)
c.save('09-viscosity.png','共同尺度比较黏度改变；明确此实验不判断断滴质量')

def cap(c,x,base,entry,scale):
 theta=math.radians(entry['angle_deg']);rr=entry['sphere_radius_um']*scale
 cy=base+rr*math.cos(theta)
 pts=[(x+rr*math.sin(-theta+2*theta*i/100),
       cy-rr*math.cos(-theta+2*theta*i/100)) for i in range(101)]
 c.d.polygon(pts,fill='#cce5f2');poly(c,pts,BLUE,5)
 c.line(pts[0],pts[-1],BLUE)

c=Canvas('飞行中的球，不等于纸上的圆点')
drop(c,250,280,D['scales']['equivalent_diameter_um']*2)
c.text(90,410,'飞行中：等效球径',42)
c.text(90,490,f"条件换算 {D['scales']['equivalent_diameter_um']:.2f} µm",42,BLUE)
c.arrow((500,300),(700,300))
cap(c,850,342,D['spherical_caps'][1],4)
c.line((700,342),(1000,342),INK);c.text(700,410,'落到基底',42)
for x,entry in zip([270,790],D['spherical_caps']):
 c.line((x-200,810),(x+200,810),INK)
 cap(c,x,810,entry,6)
 c.text(x-130,855,f"接触角 {entry['angle_deg']}°",42)
 c.text(x-160,935,f"底径 {2*entry['base_radius_um']:.2f} µm",42,BLUE)
c.text(65,1050,'两球冠等体积、同尺度；不是实际印迹',40)
c.text(65,1135,'本例忽略吸收、蒸发、撞击和滞后',42)
c.save('10-deposition.png','同体积球冠实际计算：显示接触角改变基底占地直径')

c=Canvas('电压边沿，对应两次壁面动作')
c.text(65,135,'本例选定：电压升高让腔体扩大',42)
x0=180;span=800;zero=650;scale=10
for v in [0,P['voltage_v']]:
 y=zero-v*scale;c.line((x0,y),(980,y),'#b3c3cf');c.text(65,y-25,f'{v:.0f}',40)
c.text(65,230,'电压 / V',40)
poly(c,[(x0+z['t_us']/40*span,zero-z['voltage_v']*scale) for z in D['voltage']],BLUE)
for t in [0,5,25,40]:c.text(x0+t/40*span-22,680,str(t),40)
c.text(750,755,'时间 / µs',40)
for j,(word,action) in enumerate([('上升边沿','扩腔'),('保持阶段','自由设定保持'),('下降边沿','缩腔')]):
 y=855+j*105;c.text(65,y,word,42,BLUE);c.arrow((360,y+35),(510,y+35));c.text(570,y,action,44,ORANGE)
c.text(65,1220,'保持期间，压力波仍可传播与反射',42)
c.text(65,1300,'这张是电压图，不是压力或液滴速度',42)
c.save('11-voltage-stages.png','将电压上升、保持、下降与选定极性的壁面动作对应')

photo=ROOT/'originals/photos/ipj-bio-assembled.jpg'
with Image.open(photo) as im:
 meta.append(dict(file='originals/photos/ipj-bio-assembled.jpg',
                  width=im.width,height=im.height,min_font_px=None,
                  identity='第三方项目原件：左CAD，右实物照片，原字节未改',
                  purpose='显示实际压电喷头装配和部件关系',
                  checks=['actual-dimensions','original-bytes']))

(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(f'Generated and checked {len(meta)} figures.')
