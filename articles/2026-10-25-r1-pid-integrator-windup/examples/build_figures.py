"""Original PID integrator-windup figures. Code CC0; figures CC BY 4.0.
Canvas checks reuse the repository CC0 helper, all compositions/data new.
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
SYMBOL='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SCMAP=TTFont(SYMBOL).getBestCmap()
def runs(s,size):
 out=[]
 for ch in s:
  path=FONT if ch.isspace() or ord(ch) in CMAP else SYMBOL
  assert ch.isspace() or ord(ch) in (CMAP if path==FONT else SCMAP),ch
  if out and out[-1][0]==path:out[-1]=(path,out[-1][1]+ch)
  else:out.append((path,ch))
 return [(ImageFont.truetype(path,size),txt) for path,txt in out]
def luminance(col):
 rgb=[int(col[i:i+2],16)/255 for i in (1,3,5)]
 lin=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
 return sum(a*b for a,b in zip(lin,[.2126,.7152,.0722]))
def contrast(a,b):
 l1,l2=sorted([luminance(a),luminance(b)])
 return (l2+.05)/(l1+.05)
def measure(draw,s,size):return sum(draw.textlength(txt,font=f) for f,txt in runs(s,size))
BG='#f8fafc'; INK='#142d42'; BLUE='#176297'; GREEN='#166c57'; ORANGE='#9c4d0d'
meta=[]
class Canvas:
 def __init__(self,title):
  self.im=Image.new('RGB',(1062,4000),BG);self.d=ImageDraw.Draw(self.im);self.boxes=[];self.bottom=0;self.geometry=[]
  self.text(50,30,title,48)
 def text(self,x,y,s,size=42,color=INK,box=None):
  assert size>=40
  assert contrast(color,BG)>=4.5,(color,contrast(color,BG))
  parts=runs(s,size);cur=x;bounds=[]
  for f,txt in parts:
   bb=self.d.textbbox((cur,y+size),txt,font=f,anchor='ls');bounds.append(bb);cur+=self.d.textlength(txt,font=f)
  b=(min(q[0] for q in bounds),min(q[1] for q in bounds),max(q[2] for q in bounds),max(q[3] for q in bounds))
  assert b[0]>=0 and b[1]>=0 and b[2]<=1062 and b[3]<=4000,(s,b)
  if box:assert box[0]+5<=b[0] and box[1]+5<=b[1] and b[2]<=box[2]-5 and b[3]<=box[3]-5,(s,b,box)
  for old in self.boxes:
   q=old[0]
   assert min(b[2],q[2])<=max(b[0],q[0]) or min(b[3],q[3])<=max(b[1],q[1]),(s,old[1])
  cur=x
  for f,txt in parts:
   self.d.text((cur,y+size),txt,font=f,fill=color,anchor='ls');cur+=self.d.textlength(txt,font=f)
  self.boxes.append((b,s,size));self.bottom=max(self.bottom,b[3])
  px=self.im.crop(b).convert('L');lo,hi=px.getextrema();assert hi-lo>90,(s,lo,hi)
  assert sum(1 for v in px.get_flattened_data() if v<180)>len(s)*8,s
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
  assert contrast(color,fill)>=4.5
  b=(x,y,x+w,y+h);self.d.rounded_rectangle(b,radius=16,fill=fill)
  width=measure(self.d,s,42)
  self.text(x+(w-width)/2,y+(h-60)/2,s,42,color,b);self.bottom=max(self.bottom,y+h)
 def save(self,name,purpose):
  im=self.im.crop((0,0,1062,math.ceil(self.bottom+45)));p=ROOT/'assets'/name;info=PngImagePlugin.PngInfo();info.add(b'sRGB',b'\x00');im.save(p,pnginfo=info)
  assert Image.open(p).size==im.size
  meta.append(dict(file='assets/'+name,width=im.width,height=im.height,min_font_px=min(z[2] for z in self.boxes),effective_min_font_at_354=round(min(z[2] for z in self.boxes)/3,2),identity='原创CPU模型输出或教学示意；执行数值来自 results.json',purpose=purpose,numeric_geometry=self.geometry,checks=['canvas','declared-box','text-overlap','font-size','contrast','glyph-cmap','ink-pixels','actual-dimensions']))
import numpy as np
D=DATA;GRAY='#627487';RED='#a13631';PALE='#e4eef6';M=D['main'];Q=D['parameters']
def rows(c,y,lines):
 for i,s in enumerate(lines):c.text(55,y+i*70,s,40)
def fmt(v):return f'{v:.5g}'
def chart(c,y,x,series,colors,labels,ylim=None,height=360,title=None,ticks=None):
 x=np.asarray(x,float);series=[np.asarray(s,float) for s in series];lo,hi=ylim if ylim else (min(v.min() for v in series),max(v.max() for v in series))
 if hi==lo:hi=lo+1
 left,right,top,bot=155,955,y+80,y+height;xmin,xmax=x.min(),x.max()
 def tr(a,b):return (left+(a-xmin)/(xmax-xmin)*(right-left),bot-(b-lo)/(hi-lo)*(bot-top))
 c.line((left,top),(left,bot),GRAY);c.line((left,bot),(right,bot),GRAY)
 for val in [lo,hi]:
  yy=tr(xmin,val)[1];s=f'{val:.3g}';c.text(left-20-measure(c.d,s,40),yy-25,s,40)
 for val in (ticks or [float(xmin),float(xmax)]):
  px=tr(val,lo)[0];c.line((px,bot),(px,bot+8),GRAY);c.text(px-15,bot+15,fmt(val),40)
 if lo<0<hi:c.line(tr(xmin,0),tr(xmax,0),GRAY,True)
 for arr,col in zip(series,colors):
  c.d.line([tr(a,b) for a,b in zip(x,arr)],fill=col,width=6)
 for i,(s,col) in enumerate(zip(labels,colors)):c.text(55,bot+85+i*60,s,40,col)
 if title:c.text(55,y,title,42)
 c.geometry.append(dict(kind='shared-numeric-axis',xrange=[float(xmin),float(xmax)],yrange=[float(lo),float(hi)],labels=labels,source='results.json',samples=len(x)))
 return bot+85+len(labels)*60

t=M['none']['t'];colors=[RED,GREEN,BLUE];names=['无抗饱和','条件积分','回算 Tt=1s']
c=Canvas('目标已降低，为什么仍在全力加热？')
y=chart(c,150,t,[M['none']['r']]+[M[m]['y'] for m in M],[GRAY]+colors,['灰：目标 r']+names,ylim=(0,1.6),ticks=[0,20,40,60],height=460)
rows(c,y+60,['同一教学对象、同一组 PI 参数','纵轴：归一化温升；横轴：秒','执行器满功率只能维持 y=1','本文实际计算，不是设备实测'])
c.save('00-cover.png','三策略的实际响应与可达范围')

c=Canvas('闭环里，命令与实际功率隔着一道限幅')
for xx,yy,w,s in [(55,160,270,'目标 r'),(425,160,230,'误差 e'),(55,440,270,'PID 控制器'),(425,440,230,'限幅'),(745,440,260,'被控对象')]:c.card(xx,yy,w,110,s)
c.arrow((325,215),(410,215));c.arrow((540,285),(540,340));c.arrow((540,340),(190,340));c.arrow((190,340),(190,425))
c.arrow((325,495),(410,495));c.text(343,405,'v',42,BLUE)
c.arrow((655,495),(730,495));c.text(675,405,'u',42,GREEN)
c.arrow((880,565),(880,700));c.arrow((880,700),(40,700));c.arrow((40,700),(40,300));c.arrow((40,300),(430,300));c.arrow((430,300),(430,285));c.text(490,640,'测量 y，反馈相减',40)
rows(c,800,['e=r−y；v 是未限幅的请求','u 才真正施加到对象上','控制器应知道 v 与 u 不一致'])
c.save('01-loop.png','执行器/对象/反馈身份与两个不同控制量')

c=Canvas('执行器到顶后，再大的请求也只有满功率')
y=chart(c,150,D['saturation']['v'],[D['saturation']['u']],[BLUE],['横轴 v；纵轴 u=clip(v,0,1)'],ylim=(-.1,1.1),ticks=[-1,0,1,2],height=440)
rows(c,y+70,['v<0 时，实际 u=0','0≤v≤1 时，u=v','v>1 时，实际 u=1','这叫幅值饱和，不是浮点数溢出'])
c.save('02-saturation.png','真实限幅曲线与非线性区域')

c=Canvas('P、I、D：三个量最后都成为控制请求')
for i,(label,detail,col) in enumerate([('P：看现在的偏差','P=Kp e',BLUE),('I：保存过去的误差积累','I下一步=I+Ki e Δt',GREEN),('D：看测量变化的快慢','D≈−Kd Δy/Δt',ORANGE)]):
 yy=155+i*230;c.text(55,yy,label,44,col);c.card(80,yy+80,900,100,detail)
rows(c,925,['合起来：v=P+I+D','D 常需滤波；对误差微分会受目标跳变冲击','主对比先取 D=0，明确使用 PI'])
c.save('03-pid-terms.png','PID三作用和PI实验范围')

c=Canvas('积分状态记的是：误差 × 持续时间')
steps=D['hand']['none'];c.text(55,155,f'Ki={Q["Ki"]:g}，Δt={Q["dt"]:g}s，初始 I=0',42)
for i in range(3):
 yy=260+i*200;c.text(55,yy,f'第 {i} 拍：e={steps["e"][i]:.5f}',42)
 c.text(55,yy+65,f'ΔI=Ki e Δt={steps["I_next"][i]-steps["I"][i]:.6f}',42,GREEN)
 c.text(55,yy+125,f'I：{steps["I"][i]:.6f} → {steps["I_next"][i]:.6f}',42)
rows(c,940,['积分 I 与输出命令同单位','Ki 的单位是“命令 / 偏差 / 秒”','累计不是在发现饱和时自动归零'])
c.save('04-integral-steps.png','连续三拍累积误差的真实增量')

c=Canvas('这台教学对象：满功率也只能趋近 1')
openy=M['none']['y'][:201];y=chart(c,150,t[:201],[openy,[1]*201,[1.5]*201],[BLUE,GREEN,RED],['蓝：从0开始，恒定满功率','绿：可达稳态上限 y=1','红：目标 r=1.5'],ylim=(0,1.6),ticks=[0,10,20],height=440,title='纵轴 y / r；横轴时间（秒）')
rows(c,y+65,['归一化温升 y，不是直接摄氏温度','对象：dy/dt=(u−y)/5','时间常数 5s；当前无延迟、噪声、扰动','抗饱和不能增大执行器的物理能力'])
c.save('05-plant.png','模型对象、时间常数与不可达目标')

c=Canvas('每一拍顺序固定，避免偷偷多算一次积分')
labels=['1 读 y、r，计算 e=r−y','2 用旧 I 计算 v=P+I+D','3 限幅得到实际 u','4 用当前 e、v、u 更新 I下一步','5 用 u 推进对象，进入下一拍']
for i,s in enumerate(labels):
 yy=155+i*170;c.card(55,yy,950,105,s)
 if i<4:c.arrow((530,yy+115),(530,yy+155),GREEN)
rows(c,1090,['对象在采样间隔内保持 u 不变','精确更新：y下一步=u+(y−u)exp(−Δt/5)','控制器积分采用显式 Euler 更新'])
c.save('06-order.png','控制计算与状态更新的明确次序')

c=Canvas('请求越积越高，实际功率早已不动')
y=chart(c,145,t[:201],[M['none'][k][:201] for k in ['v','u','I']],[RED,GREEN,BLUE],['红：未限幅请求 v','绿：实际功率 u','蓝：积分状态 I'],ylim=(0,9),ticks=[0,10,20],height=440,title='纵轴 v / u / I；横轴时间（秒）')
rows(c,y+60,[f'20s降目标前：I≈{M["none"]["I"][200]:.3f}','目标1.5持续不可达，误差仍为正','u已到1，v增加不会再多加热','只把输出截到1，并没有处理内部 I'])
c.save('07-windup.png','控制命令与实际动作分离及积分积累')

c=Canvas('20 秒目标下降，P 已反向，I 还很大')
for i,m in enumerate(M):
 q=D['metrics'][m]['at_drop'];yy=150+i*260;c.text(55,yy,names[i],44,colors[i]);c.text(55,yy+70,f'P={q["P"]:.3f}，I={q["I"]:.3f}',42)
 c.text(55,yy+135,f'v={q["v"]:.3f} → u={q["u"]:.3f}',42)
rows(c,1020,['此刻三者 y 相同，e 已经为负','普通积分：负 P 抵不过正 I','另外两者立即退出上限，但尚未达到目标'])
c.save('08-drop-state.png','同一降目标时刻的P/I/v/u数值分解')

c=Canvas('条件积分：只阻止“越推越饱和”的方向')
for i,q in enumerate(D['directions']):
 yy=155+i*300;c.text(55,yy,f'v={q["v"]:g}，Ki e={q["integral_rate"]:g}',42)
 col=RED if q['blocked'] else GREEN
 c.text(625,yy,'停止积分' if q['blocked'] else '允许积分',42,col)
 c.d.rectangle((250,yy+80,750,yy+130),fill='#dcefe8')
 c.line((140,yy+105),(940,yy+105),GRAY)
 for val in [0,1]:
  xp=250+500*val;c.line((xp,yy+80),(xp,yy+130),GRAY);c.text(xp-12,yy+145,str(val),40)
 xp=250+500*q['v'];c.d.ellipse((xp-9,yy+96,xp+9,yy+114),fill=col)
 c.arrow((xp,yy+105),(xp+(80 if q['integral_rate']>0 else -80),yy+105),col)
 c.text(420,yy+145,'可用区间',40,GREEN)
 c.geometry.append(dict(kind='conditional-direction',v=q['v'],integral_rate=q['integral_rate'],point_x=xp,scale=500,arrow='direction only; not increment magnitude'))
rows(c,1430,['点是未限幅 v，箭头只表示积分方向','箭头长度不代表这0.1秒的实际增量','区外向外推：停；向内返回：允许','允许积分也不保证一拍就回到区间内'])
c.save('09-conditional.png','上下限四种积分方向的规则与反例')

c=Canvas('条件积分会保存旧 I，不是把它清零')
y=chart(c,150,t,[M['conditional']['I'],M['none']['I']],[GREEN,RED],['绿：条件积分 I','红：普通积分 I'],ylim=(-.1,8),ticks=[0,20,40,60],height=430,title='纵轴 I；横轴秒；灰虚线 I=0')
rows(c,y+70,['本例初始 I=0，上限且误差正时保持0','目标下降后先处于下限，负增量也暂停','一旦允许的方向出现，积分继续更新','采样式规则仍可能跨过边界；不是精确投影'])
c.save('10-conditional-state.png','冻结积分状态的实际曲线及恢复条件')

c=Canvas('回算：让实际执行量纠正内部记忆')
c.card(55,160,250,105,'Ki e');c.card(420,160,220,105,'相加');c.card(755,160,250,105,'按时间累积')
c.arrow((305,212),(405,212));c.arrow((640,212),(740,212));c.text(657,95,'变化率',40);c.arrow((880,280),(880,355),BLUE);c.text(830,365,'状态 I',40)
c.card(150,460,300,110,'实际 u − 请求 v');c.card(650,460,280,110,'除以 Tt')
c.arrow((450,515),(635,515),GREEN);c.arrow((790,445),(790,350),GREEN);c.arrow((790,350),(530,350),GREEN);c.arrow((530,350),(530,280),GREEN)
rows(c,700,['I变化率 = Ki e + (u−v)/Tt','上饱和时 u−v<0，向下拉积分','下饱和时 u−v>0，向上拉积分','未饱和时 u=v，回算项自然为0'])
c.save('11-backcalc-loop.png','回算反馈路径、符号和时间常数')

c=Canvas('回算的第一拍：积分可以先变成负数')
q=D['hand']['backcalc'];rows(c,155,[f'r={q["r"][0]:g}，y={q["y"][0]:g}，e={q["e"][0]:g}',f'P={q["P"][0]:g}，I={q["I"][0]:g} → v={q["v"][0]:g}',f'限幅后 u={q["u"][0]:g}',f'误差贡献 Ki e={q["integral_rate"][0]:g}/s',f'回算贡献 (u−v)/Tt={q["tracking_rate"][0]:g}/s',f'ΔI={Q["dt"]:g}×({q["integral_rate"][0]:g}{q["tracking_rate"][0]:+g})',f'I下一步={q["I_next"][0]:g}'])
rows(c,760,['负 I 在这里抵消过大的比例请求','不是把实际加热功率变成负数','实际 u 仍严格限制在 0 与 1 之间'])
c.save('12-backcalc-step.png','回算第一拍逐项代入及负积分的含义')

c=Canvas('三种策略，真正施加的功率怎样变化？')
y=chart(c,150,t,[M[m]['u'] for m in M],colors,names,ylim=(-.1,1.1),ticks=[0,20,40,60],height=430,title='纵轴 u；横轴秒；灰虚线 u=0')
rows(c,y+70,[f'普通积分到 {D["metrics"]["none"]["release"]:.1f}s 才低于1',f'距20s目标下降仍延迟 {D["metrics"]["none"]["release"]-20:.1f}s','条件积分与回算在20s立即退出上限','离开限幅不等于输出已回到目标'])
c.save('13-controls.png','三方法实际执行量与饱和退出时间')

c=Canvas('三种内部记忆：长期不可达时差异最明显')
y=chart(c,150,t,[M[m]['I'] for m in M],colors,names,ylim=(-1,8),ticks=[0,20,40,60],height=430,title='纵轴 I；横轴秒；灰虚线 I=0')
rows(c,y+70,['回算不一定使 v 与 u 严格相等','若误差持续为正，平衡时仍可能 v>u','Ki e 与负的回算项可以互相抵消','最终可达稳态需要 I≈0.4 提供维持功率'])
c.save('14-integral-compare.png','内部积分状态、回算平衡与稳态非零I')

c=Canvas('回到目标附近：只比较同一明确指标')
values=[D['metrics'][m]['settle_02']-20 for m in M];maxv=max(values);scale=690/maxv
for i,(v,lab,col) in enumerate(zip(values,names,colors)):
 yy=170+i*205;c.text(55,yy,lab,42,col);c.d.rectangle((55,yy+75,55+v*scale,yy+135),fill=col);c.text(790,yy+75,f'{v:.1f}s',40)
assert np.array_equal(np.argsort(values),np.argsort(np.array(values)*scale))
c.geometry.append(dict(kind='common-scale-bar',values=values,pixels_per_second=scale))
rows(c,850,['从20s起计，首次进入 ±0.02 后','直到本次60s仿真结束都保持在范围内','这不是对无限未来或真实设备的证明','也不是所有参数下的固定优劣排名'])
c.save('15-recovery.png','同一误差带与观察窗定义的恢复时间')

c=Canvas('回算时间 Tt 改变，恢复形状也会改变')
y=chart(c,150,t,[D['sensitivity'][s]['y'] for s in ['0.2','1.0','5.0']]+[M['none']['r']],[ORANGE,BLUE,GREEN,GRAY],['Tt=0.2s','Tt=1s','Tt=5s','灰：目标'],ylim=(0,1.6),ticks=[0,20,40,60],height=420,title='纵轴 y / r；横轴时间（秒）')
rows(c,y+70,['其他参数、输入和采样间隔保持一致','更快追踪不等于所有指标都更好','Tt 是内部修正速度，不是对象时间常数'])
c.save('16-time-constant.png','同一模型不同回算时间的真实响应')

c=Canvas('回算过快：离散更新本身也可能振荡')
s=D['stiff'];xx=list(range(9));y=chart(c,150,xx,[q['I'] for q in s],[GREEN,BLUE,RED],[f'Tt={q["Tt"]:g}s；因子 {q["factor"]:g}' for q in s],ylim=(-18,28),ticks=[0,4,8],height=430,title='纵轴 I；横轴更新次数 n，Δt=0.1s')
rows(c,y+70,['独立标量试验：外部固定 u=1、P=0、e=0','I下一步=I+(Δt/Tt)(1−I)，初始 I=2','误差每步乘 (1−Δt/Tt)','此更新收敛需 0<Δt/Tt<2','灰虚线为 I=0；这里只是跟踪子系统','收敛条件不能当作完整闭环保证'])
c.save('17-discrete-limit.png','明确隔离的Euler回算稳定性反例')

c=Canvas('D 不会自动修好已经积累的积分')
y=chart(c,150,t,[D['pid'][m]['y'] for m in M],colors,names,ylim=(0,1.1),ticks=[0,20,40,60],height=420,title='纵轴 y；横轴时间（秒）')
rows(c,y+70,['补充实验：Kd=0.5、微分滤波 Tf=0.5s','D 对测量 y 微分，主实验其他条件不变','三种方法仍保留不同的饱和恢复过程','它不是所有 PID 参数和对象的结论'])
c.save('18-pid-check.png','带滤波D的独立补充仿真，明确PI范围')

c=Canvas('目标跳变：对误差微分会多出一脚冲击')
q=D['derivative'];rows(c,155,[f'独立一拍：Δr={q["dr"]:g}，Δy={q["dy"]:g}',f'Δt={q["dt"]:g}s，Kd={q["Kd"]:g}',f'对误差：Kd(Δr−Δy)/Δt={q["error_kick"]:g}',f'对测量：−Kd Δy/Δt={q["measurement_kick"]:g}'])
c.card(55,510,950,110,'D测量：不直接响应目标的瞬间跳变')
rows(c,720,['这是未滤波差分的单拍对照','实际微分常需低通滤波抑制测量噪声','滤波 D 还有自己的状态；抗积分饱和','不等于已处理所有动态与速率限制'])
c.save('19-derivative.png','微分突跳的具体数值与测量微分区别')

c=Canvas('加了前馈后，反馈哪个“实际量”？')
q=D['feedforward'];rows(c,155,[f'PID请求={q["vpid"]:g}，前馈={q["uff"]:g}',f'总请求={q["total"]:g} → 执行器实际={q["actual"]:g}',f'留给PID的实际份额={q["actual"]:g}−{q["uff"]:g}={q["correct_tracking"]:g}',f'正确差值={q["correct_difference"]:g}；直接用总量则为{q["wrong_difference"]:g}'])
rows(c,600,['两种接法连修正方向都相反','真实执行量须换回与 PID 命令相同的量纲','不能把温度 y 直接当成加热功率 u 回算','这里是静态相加例，不含执行器自身动态'])
c.save('20-tracking-point.png','前馈情况下的跟踪点与符号反例')

c=Canvas('手动切自动：先让内部状态接上当前输出')
q=D['transfer'];rows(c,155,[f'当前手动 u={q["manual"]:g}',f'r={q["r"]:g}，y={q["y"]:g} → P={q["P"]:.1f}；D=0',f'若把 I 清零，自动请求仅 {q["v_zero"]:.1f}',f'令 I=u手动−P−D={q["I_match"]:.1f}',f'此刻 v=P+I+D={q["manual"]:g}，接上原命令'])
rows(c,690,['这是“无突跳切换”的代数初始化示例','后续响应仍受控制参数和对象决定','不能把“退出饱和就清零 I”作为通用规则'])
c.save('21-transfer.png','非零积分的实际作用与手动自动状态衔接')

c=Canvas('归一化热收支：加进去的，减去散掉的')
c.card(310,230,450,220,'储存的热量 → 温升 y',fill='#f3e5d7')
c.arrow((70,340),(295,340),GREEN);c.text(65,220,'加热 u',42,GREEN)
c.arrow((775,340),(990,340),RED);c.text(805,220,'散热 y',42,RED)
rows(c,560,['净流入 = 加热 − 散热 = u−y',f'热惯性使 {Q["tau"]:g} dy/dt = u−y','这里把满功率下的稳态温升归一化为1','u=y 时热收支平衡，温升不再改变','忽略温度相关材料特性和热传导延迟'])
c.save('23-thermal-balance.png','热收支解释一阶归一化模型，不冒充真实结构')

c=Canvas('误差的面积：三个采样间隔怎样累起来')
left,right,top,bot=155,955,220,620;dt=Q['dt'];errs=D['hand']['none']['e'];scale=(bot-top)/1.6
for k,e in enumerate(errs):
 x0=left+(right-left)*k/3;x1=left+(right-left)*(k+1)/3
 c.d.rectangle((x0,bot-e*scale,x1-3,bot),fill=PALE,outline=GREEN,width=4)
 c.text(x0+30,bot-e*scale+35,f'{e:.3f}',40,GREEN)
c.line((left,top),(left,bot),GRAY);c.line((left,bot),(right,bot),GRAY)
for k in range(4):c.text(left+(right-left)*k/3-15,bot+20,f'{k*dt:.1f}',40)
c.text(55,145,'纵轴误差 e；横轴时间（秒）',42)
rows(c,750,[f'每块宽度 Δt={dt:g}s，高度取该拍误差',f'总面积≈{sum(errs)*dt:.6f} 偏差·秒',f'乘 Ki={Q["Ki"]:g}，三拍累积 I={D["hand"]["none"]["I_next"][-1]:.6f}','矩形是显式 Euler 采样近似，不是假称连续积分'])
c.geometry.append(dict(kind='sampled-error-area',heights=errs,width_seconds=dt,pixels_per_error=scale))
c.save('24-integral-area.png','误差乘时间的矩形面积与积分状态的对应')

(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('Generated',len(meta),'figures')
