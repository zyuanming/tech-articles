"""New Catmull–Rom figures; code CC0, figure output CC BY 4.0.
Canvas checks adapted from previous CC0 generator; compositions new.
"""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
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
  self.im=Image.new('RGB',(1062,4000),BG);self.d=ImageDraw.Draw(self.im);self.boxes=[];self.bottom=0;self.geometry=[]
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
  assert all(0<=p[0]<=1062 and 0<=p[1]<=4000 for p in (a,b))
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
  im=self.im.crop((0,0,1062,math.ceil(self.bottom+45)));p=ROOT/'assets'/name;info=PngImagePlugin.PngInfo();info.add(b'sRGB',b'\x00');im.save(p,pnginfo=info)
  assert Image.open(p).size==im.size
  meta.append(dict(file='assets/'+name,width=im.width,height=im.height,min_font_px=min(z[2] for z in self.boxes),effective_min_font_at_354=round(min(z[2] for z in self.boxes)/3,2),identity='原创CPU模型输出或教学示意；执行数值来自 results.json',purpose=purpose,numeric_geometry=self.geometry,checks=['canvas','declared-box','text-overlap','font-size','contrast','glyph-cmap','ink-pixels','actual-dimensions']))
import numpy as np
D=DATA;GRAY='#627487';RED='#a13631';COLORS=[BLUE,GREEN,RED]
def rows(c,y,lines):
 for i,s in enumerate(lines):c.text(55,y+i*72,s,40)
def fmt(v):return '('+', '.join(f'{(0 if abs(x)<1e-12 else x):.6g}' for x in v)+')'
def bounds(points,pad=.15):
 p=np.array(points);lo=p.min(axis=0);hi=p.max(axis=0);span=np.maximum(hi-lo,.5);return [*(lo-pad*span),*(hi+pad*span)]
def plot(c,y,points,curves=(),colors=None,labels=True,box=None,height=560,markers=(),vectors=()):
 # Equal x/y scale. All model coordinates come from results.json.
 p=np.array(points);allp=np.vstack([p]+[np.array(z) for z in curves]);box=box or bounds(allp)
 x0,y0,x1,y1=box;scale=min(860/(x1-x0),(height-70)/(y1-y0));ox=100+(860-(x1-x0)*scale)/2;oy=y+30+(height-70-(y1-y0)*scale)/2
 def tr(v):return (ox+(v[0]-x0)*scale,oy+(y1-v[1])*scale)
 assert abs((tr([1,0])[0]-tr([0,0])[0])-(tr([0,0])[1]-tr([0,1])[1]))<1e-9
 c.geometry.append(dict(kind='equal-aspect-plot',bounds=[float(v) for v in box],pixels_per_unit=float(scale),control_points=p.tolist(),curve_count=len(curves),source='results.json coordinates; affine transform shared for every curve in this panel'))
 c.d.rectangle((65,y,997,y+height),outline='#b7c8d5',width=2)
 # Clipping plot content to the explicitly declared frame.
 layer=Image.new('RGBA',c.im.size,(0,0,0,0));ld=ImageDraw.Draw(layer)
 def poly(q,col,width):ld.line([tr(v) for v in q],fill=col,width=width)
 poly(p,GRAY,3)
 for curve,col in zip(curves,colors or COLORS):poly(curve,col,7)
 for idx,v in enumerate(p):
  x,z=tr(v);ld.ellipse((x-9,z-9,x+9,z+9),fill=INK)
 for q,col in markers:
  for v in q:
   x,z=tr(v);ld.ellipse((x-10,z-10,x+10,z+10),fill=col,outline='white',width=2)
 for start,vec,col in vectors:
  a=tr(start);b=tr(np.array(start)+np.array(vec));ld.line([a,b],fill=col,width=5)
  ang=math.atan2(b[1]-a[1],b[0]-a[0]);ld.polygon([b,(b[0]-18*math.cos(ang-.5),b[1]-18*math.sin(ang-.5)),(b[0]-18*math.cos(ang+.5),b[1]-18*math.sin(ang+.5))],fill=col)
 crop=layer.crop((65,y,998,y+height));c.im.paste(crop,(65,y),crop)
 c.bottom=max(c.bottom,y+height)
 # Labels in reserved margin, not over curve/control points.
 if labels:
  c.text(80,y+height+12,f'x: {x0:.3g} 至 {x1:.3g}',40)
  c.text(550,y+height+12,f'y: {y0:.3g} 至 {y1:.3g}',40)
 return tr
main=D['main'];p=main[0]['points'];whole=D['whole'];hand=D['hand']
c=Canvas('必经点给好了，怎样自动连成曲线？')
plot(c,135,whole['points'],[s['curve'] for s in whole['segments']],colors=[BLUE]*len(whole['segments']),height=500)
rows(c,730,['黑点：指定位置；灰线：直接连线','蓝线：本文程序实际算出的向心曲线','经过点不等于匀速，也不保证避开障碍'])
c.save('00-cover.png','可见路线任务与实际计算轨迹')

c=Canvas('折线会拐角；曲线把方向接起来')
plot(c,140,p,[main[0]['curve']],height=500)
rows(c,735,['从 P1=(1, 2) 走到 P2=(4, 3)','P0=(0, 0)、P3=(6, 0) 提供邻域','本图只算中间段；灰色两端不是曲线'])
c.save('01-four-points.png','四点只确定中段，控制多边形与曲线区分')

c=Canvas('切线：把前后两步的斜率平均')
s=main[0]
plot(c,140,p,[s['curve']],vectors=[(p[1],s['m'][0],GREEN),(p[2],s['m'][1],RED)],height=540)
rows(c,775,[f"绿 m1=(P2−P0)/2 = {fmt(s['m'][0])}",f"红 m2=(P3−P1)/2 = {fmt(s['m'][1])}",'箭头表示局部 u 每增加1的瞬时变化','它们是方向和变化率，不是另两个必经点'])
c.save('02-tangents.png','邻点差分确定端点导数，箭头按真实向量比例')

c=Canvas('四个条件，恰好确定一个三次式')
rows(c,150,['横轴 u；下图纵轴是基函数权重','位置：C(0)=P1；C(1)=P2','斜率：C′(0)=m1；C′(1)=m2','先只管 x，四个条件解出四个系数','再用完全同一规则求 y'])
# Basis curves are mathematical definitions evaluated from recorded sample u.
u=np.array(s['u']);basis=[2*u**3-3*u*u+1,u**3-2*u*u+u,-2*u**3+3*u*u,u**3-u*u]
plot(c,570,[[0,0],[1,0]],[np.c_[u,z] for z in basis],colors=[BLUE,GREEN,RED,ORANGE],height=450,box=[-.1,-.2,1.1,1.15])
rows(c,1115,['蓝 h00：起点位置；红 h01：终点位置','绿 h10：起点斜率；棕 h11：终点斜率'])
c.save('03-basis.png','Hermite四条件与真实基函数曲线，负权重可见')

c=Canvas('u=0.5：把四份贡献相加')
labels=['P1 位置','m1 斜率','P2 位置','m2 斜率']
for i,(label,b,term) in enumerate(zip(labels,hand['basis'],hand['terms'])):
 y=150+i*125;c.text(60,y,f'{label} × {b:g}',42);c.text(570,y,fmt(term),42)
rows(c,700,[f"相加：C(0.5) = {fmt(hand['value'])}",'P1/P2 的几何中点是 (2.5, 2.5)','两份斜率贡献把结果向左上方推'])
c.save('04-one-evaluation.png','四份数值贡献逐项核算')

c=Canvas('让 u 前进：位置沿同一曲线移动')
plot(c,140,p,[s['curve']],markers=[(hand['samples'],RED)],height=520)
for i,(u,q) in enumerate(zip(hand['samples_u'],hand['samples'])):c.text(65,760+i*72,f'u={u:g} → {fmt(q)}',40)
c.save('05-trace.png','五个实际插值位置和非等距分布')

c=Canvas('相邻两段共享同一个结点导数')
plot(c,140,whole['points'],[z['curve'] for z in whole['segments']],colors=[BLUE,GREEN,BLUE,GREEN,BLUE],height=480)
j=whole['joins'][1]
rows(c,710,[f"在 P2={fmt(j['point'])} 拼接",f"左段局部导数：{fmt(j['local_left'])}",f"右段局部导数：{fmt(j['local_right'])}",f"各除 Δt 后：{fmt(j['global_left'])}",'两侧全局 t 导数相同；二阶导数未必相同'])
c.save('06-continuity.png','C1共享导数与非均匀局部参数尺度')

c=Canvas('移动一个点，只改变附近四段')
box=bounds(np.vstack([whole['points'],whole['edited']]))
for y,pts,segs,label in [(150,whole['points'],whole['segments'],'原路径'),(760,whole['edited'],whole['newsegments'],'只把第3个点上移1.5')]:
 c.text(60,y,label,42);plot(c,y+80,pts,[z['curve'] for z in segs],colors=[BLUE]*5,box=box,height=440)
rows(c,1370,['两幅坐标与比例完全相同','最右一段不含被改点：输出逐点不变'])
c.save('07-local-edit.png','真实局部编辑与远处未变曲线，同轴对照')

c=Canvas('结点间距：给每段分配多少参数')
for k,z in enumerate(main):
 y=160+k*230;c.text(60,y,['均匀 α=0','向心 α=0.5','弦长 α=1'][k],42)
 t=z['knots'];scale=850/main[2]['knots'][-1]
 lengths=np.diff(t)*scale;assert np.array_equal(np.argsort(lengths),np.argsort(z['h']))
 c.geometry.append(dict(kind='knot-axis',alpha=z['alpha'],positions=t,interval_pixels=lengths.tolist(),scale=scale,source='main[k].knots and main[k].h'))
 c.line((90,y+90),(90+scale*t[-1],y+90),COLORS[k])
 for i,v in enumerate(t):
  x=90+v*scale;c.line((x,y+70),(x,y+110),COLORS[k]);c.text(x-25,y+120,f'P{i}',40)
 c.text(420,y,'间距 '+', '.join(f'{v:.3f}' for v in z['h']),40)
rows(c,880,['标号 P0–P3 对应输入点，不是刻度值','上面三轴使用同一参数长度尺度','Δt = 相邻位置距离的 α 次方','结点不是时间戳；单位取决于参数定义'])
c.save('08-knots.png','三种结点分配，数值与轴段长绑定')

c=Canvas('同四点，同坐标，只改参数化')
plot(c,150,p,[z['curve'] for z in main],colors=COLORS,height=600)
rows(c,850,['蓝：均匀；绿：向心；红：弦长','全都经过 P1 和 P2，内部形状不同','不能改了结点，却仍套均匀的1/2差分'])
c.save('09-three-curves.png','三参数曲线真实叠加与共享控制点')

c=Canvas('非均匀：先算每单位 t 的斜率')
z=main[1]
for i,v in enumerate(z['v']):c.text(60,150+i*78,f'第{i+1}条边斜率 = {fmt(v)}',40)
rows(c,440,[f"P1 的 D1 = {fmt(z['D'][0])}",f"本段 Δt = {z['h'][1]:.6f}",f"局部 m1 = Δt×D1 = {fmt(z['m'][0])}",'一段的 u 走满1，t 实际走了 Δt','箭头转换的是参数尺度，不是旋转方向'])
c.save('10-parameter-scale.png','非均匀加权差分和导数尺度实际值')

c=Canvas('另一种算法：逐层做直线插值')
pyr=D['pyramid']
for k,(label,coords) in enumerate([('第一层 A',[*pyr['A']]),('第二层 B',[*pyr['B']]),('第三层 C',[pyr['C']])]):
 y=140+k*305;c.text(60,y,label,44)
 for i,q in enumerate(coords):c.text(85,y+75+i*62,f'{i}: {fmt(q)}',40)
 if k<2:c.arrow((850,y+200),(850,y+280),GREEN)
rows(c,1080,['同一均匀例：t=1.5，对应 u=0.5','第一层有外推，数值会超出相邻点范围','三层结果与 Hermite 计算完全一致'])
c.save('11-pyramid.png','Barry–Goldman层层结果，用实际数值暴露外推')

c=Canvas('转成贝塞尔：把导数换成把手')
z=main[0]
plot(c,140,z['bezier'],[z['curve']],height=520)
for i,q in enumerate(z['bezier']):c.text(60,750+i*75,f'B{i} = {fmt(q)}',40)
rows(c,1080,['B1=P1+m1/3；B2=P2−m2/3','同一条曲线，只是控制方式不同'])
c.save('12-bezier.png','实际Bezier控制多边形与曲线等价转换')

c=Canvas('均匀参数：一个中间段也会回环')
loop=D['loop'];plot(c,150,loop['points'],[z['curve'] for z in loop['curves']],colors=COLORS,height=520)
rows(c,760,[f"新例 P0={fmt(loop['points'][0])}，P1={fmt(loop['points'][1])}",f"P2={fmt(loop['points'][2])}，P3={fmt(loop['points'][3])}",'蓝均匀／绿向心／红弦长，共用坐标','回环很小：下一图放大中段的回环'])
c.save('13-loop-context.png','单段反例完整控制点与三参数同轴真实输出')

c=Canvas('局部放大：同一点被经过两次')
h=loop['hit'];plot(c,150,loop['points'],[loop['curves'][0]['curve']],colors=[BLUE],height=560,box=bounds(loop['loop_bounds'],.25),markers=[([h['point']],RED)])
rows(c,810,[f"u={h['u']:.6f} 与 u={h['v']:.6f}",f"都到达 {fmt(h['point'])}",'红点是解方程得到的交点，不靠目测','只放大同一蓝色曲线，未改控制点'])
c.save('14-loop-zoom.png','均匀段真实双参数交点及注明坐标的局部放大')

c=Canvas('向心不回环，也仍可能越出数值范围')
o=D['overshoot'];plot(c,150,o['points'],[o['curve']],colors=[GREEN],height=560,markers=[([o['peak']],RED)])
rows(c,810,['新例：四点 y 都在0到1之间',f"曲线最高处 y={o['peak'][1]:.6f}",'无段内自交 ≠ 每个坐标都不越界','高度、颜色等有硬边界的值要另设约束'])
c.save('15-overshoot.png','向心参数纵坐标过冲反例与实算极值')

c=Canvas('每段没回环，全路径仍能交叉')
g=D['global_cross'];plot(c,150,g['points'],[z['curve'] for z in g['segments']],colors=[GREEN]*5,height=570,markers=[([g['hit']['point']],RED)])
rows(c,820,['全部使用向心参数，红点来自不同段',f"交点约 {fmt(g['hit']['point'])}",'单段内部保证，不替代全路径碰撞检查','非相邻段是否相交，需要额外检验'])
c.save('16-global-crossing.png','向心全路径非相邻段真实交点')

c=Canvas('端点缺邻居：明确选择边界规则')
first=whole['segments'][0];plot(c,150,first['points'],[first['curve']],height=500)
rows(c,740,[f"虚拟前点 = 2P首−P次 = {fmt(first['points'][0])}",'它只用来算切线，不加入必经点序列','直接重复端点会令非均匀 Δt=0','非均匀时拒绝相邻重复点，避免除零'])
c.save('17-endpoints.png','外推虚拟端点与首段的真实构造')

c=Canvas('曲线光滑，不代表按参数走就匀速')
speed=D['speed'];box=bounds(np.vstack([p,s['curve']]))
for k in range(2):
 y=150+k*610;c.text(60,y,['u 每次等增0.1','查弧长表：近似等路程'][k],42)
 plot(c,y+80,p,[s['curve']],height=430,box=box,markers=[(speed['markers'][k],RED)])
rows(c,1370,[f"等 u 相邻距离 {min(speed['steps'][0]):.4f} 至 {max(speed['steps'][0]):.4f}",f"弧长表后 {min(speed['steps'][1]):.4f} 至 {max(speed['steps'][1]):.4f}",'同一曲线、同一比例；点间直线距仅作诊断'])
c.save('18-speed.png','真实等参数与近似等弧长标记比较')

c=Canvas('反向共线：结点处可以瞬时停住')
z=D['reverse'];plot(c,150,z['points'],[z['curve']],colors=[GREEN],height=500)
rows(c,740,['P0=(0,0)，P1=(1,0)，P2=(0,0)',f"向心 D1={fmt(z['D'][0])}",'相邻点没有重复，但来回方向完全相反','单段内部定理不排除端点零导数'])
c.save('19-zero-speed.png','反向共线结点零导数的退化边界')
c=Canvas('递归构造：直线可以延伸到点外')
q=np.array(pyr['A']);r=np.array(pyr['B']);end=np.array(pyr['C']);box=bounds(np.vstack([p,q,r,end]))
for k,(label,control,result) in enumerate([('第一层：三条直线 → A',p,q),('第二层：连接相邻 A → B',q,r),('第三层：B → C（局部放大）',r,[end])]):
 y=150+k*670;c.text(60,y,label,42)
 curves=[control]
 if k==0:curves += [[control[0],result[0]],[result[2],control[3]]]
 thisbox=box if k<2 else bounds(np.vstack([control,result]),.8)
 tr=plot(c,y+75,control,curves,colors=[GRAY]*len(curves),height=500,box=thisbox,markers=[(result,RED)])
 names=[['P0','P1','P2','P3'],['A0','A1','A2'],['B0','B1']][k]
 offsets=[ [(-85,0),(-85,-12),(24,-18),(25,0)], [(-100,-25),(-25,30),(20,-60)], [(-110,12),(25,-55)] ][k]
 for value,name,(dx,dy) in zip(control,names,offsets):
  xx,yy=tr(value);c.text(xx+dx,yy+dy,name,40)
 offsets=[[(15,-67),(-25,20),(20,-60)],[(-115,10),(25,-40)],[(20,20)]][k]
 names=[['A0','A1','A2'],['B0','B1'],['C']][k]
 for value,name,(dx,dy) in zip(result,names,offsets):
  xx,yy=tr(value);c.text(xx+dx,yy+dy,name,40,RED)
rows(c,2220,['红点是每层结果；前两层坐标比例相同','A0越过P1；A2在P2之前：都是外推','第三层单独放大，坐标范围写在图下'])
c.save('20-recursion-geometry.png','递归每层编号位置、外推几何和第三层明确局部放大')

c=Canvas('同一短段放大：三种参数的形状')
curves=[z['curve'] for z in loop['curves']]
plot(c,150,loop['points'],curves,colors=COLORS,height=620,box=bounds(np.vstack(curves),.18))
rows(c,880,['蓝：均匀；绿：向心；红：弦长','三条都是上方全景的原曲线，只放大视野','它们仍共享同一对起终点和坐标比例'])
c.save('22-parameter-closeup.png','同一个不均匀点集三参数化的中段共同局部放大')

(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('figures',len(meta))
