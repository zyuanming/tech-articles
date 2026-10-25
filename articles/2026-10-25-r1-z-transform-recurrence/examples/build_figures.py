"""Original Z-transform figures. Code CC0; figures CC BY 4.0.
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
D=DATA;GRAY='#627487';RED='#a13631';PALE='#e4eef6'
def rows(c,y,lines):
 for i,s in enumerate(lines):c.text(55,y+i*70,s,40)
def fmt(v):return f'{v:.6g}'
def chart(c,y,x,series,colors,labels,ylim=None,ticks=None,height=370,title=None,stems=False):
 x=np.array(x,float);series=[np.array(v,float) for v in series]
 lo,hi=(min(min(v) for v in series),max(max(v) for v in series)) if ylim is None else ylim
 if hi==lo:hi=lo+1
 xmin,xmax=float(x.min()),float(x.max());left,right,top,bot=135,965,y+75,y+height
 def tr(a,b):return (left+(a-xmin)/(xmax-xmin)*(right-left),bot-(b-lo)/(hi-lo)*(bot-top))
 c.geometry.append(dict(kind='numeric-shared-axis',xrange=[xmin,xmax],yrange=[float(lo),float(hi)],samples=len(x),source='results.json arrays',labels=labels))
 c.line((left,top),(left,bot),GRAY);c.line((left,bot),(right,bot),GRAY)
 if lo<=0<=hi:c.line(tr(xmin,0),tr(xmax,0),GRAY)
 for val in sorted(set([lo,hi])):
  xx,yy=tr(xmin,val);c.text(15,yy-25,f'{val:.3g}',40)
 for val in (ticks if ticks is not None else [xmin,xmax]):
  xx,yy=tr(val,lo);c.line((xx,bot),(xx,bot+8),GRAY);c.text(xx-15,bot+13,fmt(val),40)
 for i,(vals,col) in enumerate(zip(series,colors)):
  pts=[tr(a,b) for a,b in zip(x,vals)]
  if stems:
   lengths=[abs(tr(xx,v)[1]-tr(xx,0)[1]) for xx,v in zip(x,vals)]
   assert np.array_equal(np.argsort(lengths),np.argsort(abs(vals)))
   for a,b in zip(x,vals):
    px,py=tr(a,b);c.line(tr(a,0),(px,py),col);c.d.ellipse((px-7,py-7,px+7,py+7),fill=col)
  else:c.d.line(pts,fill=col,width=6)
 c.bottom=max(c.bottom,bot+65)
 if title:c.text(55,y,title,42)
 for i,(label,col) in enumerate(zip(labels,colors)):c.text(55,y+height+85+i*60,label,40,col)
 return tr

def plane(c,y,pole=.5,region=None,unit=True,label=''):
 cx,cy,scale=530,y+320,210
 extent=1.55
 def tr(z):return (cx+z[0]*scale,cy-z[1]*scale)
 # Filled ROC clipped to this finite display; boundary is explicitly excluded.
 box=(cx-extent*scale,cy-extent*scale,cx+extent*scale,cy+extent*scale)
 if region=='outside':
  c.d.rectangle(box,fill=PALE);r=abs(pole)*scale;c.d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=BG)
 if region=='inside':
  r=abs(pole)*scale;c.d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=PALE)
 c.line((cx-350,cy),(cx+350,cy),GRAY);c.line((cx,cy+350),(cx,cy-350),GRAY)
 if unit:c.d.ellipse((cx-scale,cy-scale,cx+scale,cy+scale),outline=GREEN,width=4)
 r=abs(pole)*scale;c.d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=BLUE,width=3)
 px,py=tr((pole,0));c.line((px-9,py-9),(px+9,py+9),RED);c.line((px-9,py+9),(px+9,py-9),RED)
 c.d.ellipse((cx-8,cy-8,cx+8,cy+8),outline=INK,width=3)
 c.text(cx+365,cy-25,'实部',40);c.text(cx+15,cy-365,'虚部',40)
 c.text(cx-40,cy+15,'0',40);c.text(px+15,py+20,fmt(pole),40,RED)
 c.text(60,y+720,label,40)
 c.bottom=max(c.bottom,y+785)
 c.geometry.append(dict(kind='equal-aspect-z-plane',pole=pole,unit_radius=1,pixels_per_unit=scale,region=region))
 return tr

n=D['main']['n'];x=D['main']['x'];y=D['main']['y'];a=D['main']['a']
c=Canvas('只响两拍，输出为什么还在继续？')
chart(c,145,n[:10],[x[:10],y[:10]],[GRAY,BLUE],['灰：输入 x[n]','蓝：输出 y[n]'],ylim=(0,3),ticks=[0,3,6,9],height=400)
rows(c,790,[f'每拍：y[n] = {a:g} y[n−1] + x[n]','本文实际计算；横轴为采样序号 n','记忆把旧输入带到后来的时刻'])
c.save('00-cover.png','实际输入输出结果，提出递推记忆问题')

c=Canvas('离散序列：每一拍只放一个数')
chart(c,140,n[:8],[x[:8]],[BLUE],['点的位置是 n，竖线高度是 x[n]'],ylim=(0,2.5),ticks=[0,2,4,7],stems=True)
rows(c,690,['x[0]=1，x[1]=2，之后均为0','两点之间没有指定连续波形','时间若每拍间隔 T 秒，则时刻为 nT'])
c.save('01-samples.png','序号、数值与离散采样身份')

c=Canvas('一格记忆：先读取，再更新')
c.card(55,170,240,100,'当前 x[n]');c.card(450,170,170,100,'相加');c.card(755,170,250,100,'输出 y[n]')
c.arrow((295,220),(435,220));c.arrow((620,220),(740,220))
c.card(730,480,285,110,'存到下一拍');c.card(355,480,240,110,'上一输出');c.card(50,480,245,110,f'乘 {a:g}')
c.arrow((880,285),(880,465),GREEN);c.arrow((715,535),(610,535),GREEN);c.arrow((340,535),(310,535),GREEN)
c.arrow((170,465),(170,365),GREEN);c.arrow((170,365),(530,365),GREEN);c.arrow((530,365),(530,285),GREEN)
rows(c,710,['绿色反馈路径跨过一个采样间隔','没有这一格延迟，就不是同一条递推','实现时可用一个变量保存上一输出'])
c.save('02-memory.png','反馈/单位延迟和状态读写顺序')

c=Canvas('前三拍：旧状态怎样进入新结果')
for i in range(3):
 yy=150+i*250;old=0 if i==0 else y[i-1]
 c.text(55,yy,f'n={i}：读出旧值 {fmt(old)}',44)
 c.card(55,yy+85,270,95,f'{fmt(old)} × {a:g}')
 c.text(350,yy+103,'+',44);c.card(425,yy+85,175,95,fmt(x[i]));c.text(630,yy+103,'=',44);c.card(720,yy+85,285,95,fmt(y[i]),fill='#dcefe8')
rows(c,940,['相加完成后，把结果存成下一拍旧值','例如 n=2，输入已为0，输出仍不为0'])
c.save('03-three-steps.png','逐拍实算和状态覆盖次序')

c=Canvas('给时间贴标签，数值就成了系数')
for i,(value,power) in enumerate(zip(x[:4],['1','z⁻¹','z⁻²','z⁻³'])):
 yy=150+i*145;c.text(55,yy,f'n={i}',44);c.card(245,yy,230,95,fmt(value));c.text(515,yy+18,'×',44);c.card(625,yy,335,95,power)
rows(c,790,['把各拍相加：X(z) = 1 + 2z⁻¹','z 是可选择的复数，不是时间 n','整串序列变成一个关于 z 的函数'])
c.save('04-encoding.png','系数与幂次对应时刻，不是仅换字母')

c=Canvas('晚一拍：每个指数都多一个 −1')
for j,(label,vals) in enumerate([('原序列 x[n]',x[:4]),('延迟 x[n−1]',[0]+x[:3])]):
 yy=155+j*260;c.text(55 if j==0 else 690,yy,label,44)
 for k,v in enumerate(vals):c.card(55+k*250,yy+85,215,95,fmt(v))
 for k in range(4):c.text(100+k*250,yy+185,f'n={k}',40)
c.arrow((160,390),(410,485),GREEN);c.arrow((410,390),(660,485),GREEN)
rows(c,760,['原变换：1 + 2z⁻¹','延迟后：z⁻¹ + 2z⁻²','正好是原式乘 z⁻¹；这里负时刻为0'])
c.save('05-delay.png','系数右移一格与幂次相乘的对应')

c=Canvas('递推变代数：把同一个 Y 收到一边')
lines=['Y(z) = 0.5 z⁻¹Y(z) + X(z)','(1−0.5z⁻¹) Y(z) = X(z)','H(z) = Y(z)/X(z)','H(z) = 1/(1−0.5z⁻¹)']
for i,s in enumerate(lines):
 c.text(60,150+i*175,s,42)
 if i<3:c.arrow((530,225+i*175),(530,290+i*175),GREEN)
rows(c,885,['此处先设 y[−1]=0：零状态响应','H 描述输入→输出的线性规则','初始记忆不为0时，要另加一项'])
c.save('06-algebra.png','移位代入、同类项消元与零状态前提')

c=Canvas('反变换：从幂次读回每一拍')
c.text(55,150,'1/(1−q) = 1 + q + q² + …',42)
c.text(55,240,f'q = {a:g} z⁻¹',44)
for i in range(4):
 yy=360+i*135;c.card(55,yy,270,95,['1','z⁻¹','z⁻²','z⁻³'][i]);c.arrow((350,yy+48),(565,yy+48),GREEN);c.card(610,yy,395,95,f'h[{i}] = {fmt(D["h"][i])}')
rows(c,990,['幂次记录时刻，系数就是冲激响应','无穷级数要收敛：|0.5/z| < 1','所以这个展开要求 |z| > 0.5'])
c.save('07-inverse.png','几何级数展开与系数反演及收敛条件')

c=Canvas('只推一下：冲激响应显示全部记忆')
chart(c,145,n[:9],[D['h'][:9]],[BLUE],['h[n] = 0.5ⁿ，n≥0'],ylim=(0,1),ticks=[0,2,4,8],stems=True)
rows(c,700,['单位冲激：只有 n=0 取1，其余取0','它是离散的一拍输入，不是无限高脉冲','每过一拍，残留值减半'])
c.save('08-impulse.png','单位冲激和实际递推衰减尾迹')

c=Canvas('两个输入，叠出两条错开的尾迹')
for j,(vals,label,col) in enumerate([(D['convolution'][0],'第0拍输入1：1 × h[n]',GREEN),(D['convolution'][1],'第1拍输入2：2 × h[n−1]',ORANGE),(y,'两条相加：y[n]',BLUE)]):
 chart(c,145+j*590,n[:8],[vals[:8]],[col],[label],ylim=(0,3),ticks=[0,3,7],height=350,stems=True)
rows(c,1930,[f'n=2：{fmt(D["convolution"][0][2])} + {fmt(D["convolution"][1][2])} = {fmt(y[2])}','这就是卷积：缩放、延迟，再逐拍相加','三图使用同一纵轴，条高可直接比较'])
c.save('09-convolution.png','两份输入贡献、延迟和实际叠加结果')

c=Canvas('一直输入1，输出趋近2而不是1')
chart(c,145,n,[D['step']['raw'],D['step']['normalized']],[BLUE,GREEN],['蓝：原规则，稳态增益2','绿：输入也乘0.5，稳态增益1'],ylim=(0,2),ticks=[0,5,10,15],height=410)
rows(c,805,['原规则是消退累加，不是归一化平均','若需平均：y[n]=0.5y[n−1]+0.5x[n]','两条都从 y[−1]=0 开始，仍有起步过渡'])
c.save('10-step.png','阶跃响应与未归一化增益的明确区别')

c=Canvas('只从 n=0 相加，会留下边界项')
rows(c,150,['延迟序列：y[−1], y[0], y[1], …','对应权重：1,       z⁻¹,   z⁻², …'])
c.card(55,360,280,105,'y[−1]');c.text(370,385,'+',44);c.card(455,360,550,105,'z⁻¹ × Y₊(z)')
rows(c,570,['单边变换只加 n≥0 的项','y[−1] 不在 Y₊ 所收的原序列里','Y₊ = 0.5Y₊z⁻¹ + X₊ + 0.5y[−1]','双边求和没有同样的固定起点边界'])
c.save('11-boundary.png','单边延迟从实际首项导出初始状态')

c=Canvas('初始值4，会叠上一条自然衰减')
chart(c,145,n[:10],[y[:10],D['initial']['natural'][:10],D['initial']['y'][:10]],[BLUE,GREEN,RED],['蓝：零状态输入响应','绿：初始记忆产生的响应','红：完整输出 = 蓝 + 绿'],ylim=(0,4),ticks=[0,3,6,9],height=430)
rows(c,910,['y[−1]=4；初始项为 4×0.5ⁿ⁺¹',f'n=0：{fmt(y[0])}+{fmt(D["initial"]["natural"][0])}={fmt(D["initial"]["y"][0])}','H 没有变，但只算 HX 会漏掉绿色部分'])
c.save('12-initial.png','零状态/零输入/完整响应的实际分解')

c=Canvas('复数 z：长度与角度一起编码')
c.text(55,140,'示例 z = 2(cos60° + i sin60°)',42)
cx,cy,scale=530,580,150
c.line((cx-370,cy),(cx+370,cy),GRAY);c.line((cx,cy+370),(cx,cy-370),GRAY)
c.d.ellipse((cx-scale,cy-scale,cx+scale,cy+scale),outline=GREEN,width=4)
for value,label,col,offset in [(D['complex']['z'],'z：长度2',ORANGE,(25,-15)),(D['complex']['powers'][1],'z⁻¹：长度1/2',BLUE,(160,60))]:
 end=(cx+value[0]*scale,cy-value[1]*scale);c.arrow((cx,cy),end,col);c.text(end[0]+offset[0],end[1]+offset[1],label,40,col)
c.text(920,cy-20,'实部',40);c.text(cx+20,cy-390,'虚部',40);c.text(cx-45,cy+20,'0',40)
c.geometry.append(dict(kind='equal-aspect-complex-plane',pixels_per_unit=scale,z=D['complex']['z'],inverse=D['complex']['powers'][1],unit_radius=1))
rows(c,1020,['绿色圆半径1；横轴实部，纵轴虚部','i²=−1；倒数的角度与原角度相反','每乘一次 z⁻¹：长度减半、角度减60°','当 |z|=1 时，只旋转，不改变长度'])
c.save('13-complex.png','复平面中实际复数/倒数与单位圆同尺度')

c=Canvas('无穷求和：项是否真的越变越小？')
for i,item in enumerate(D['convergence']):
 yy=150+i*470
 vals=item['terms'][:6];upper=max(vals)
 chart(c,yy,np.arange(6),[vals],[BLUE],[f"|z|={fmt(item['r'])}，公比={fmt(item['ratio'])}"],ylim=(0,upper),ticks=[0,2,5],height=260,stems=True)
rows(c,1640,['图中是 h[n]z⁻ⁿ 的大小，横轴 n','三个面板纵轴不同，不能直接比条高','公比<1可求和；=1不趋零；>1增长'])
c.save('14-convergence.png','级数项的实际收敛/边界/发散数值')

c=Canvas('同一有理式，可以代表另一串数')
bi=D['bilateral']
chart(c,145,bi['n'],[bi['right']],[BLUE],['右侧：n≥0 为 0.5ⁿ'],ylim=(0,1),ticks=[-5,0,7],height=340,stems=True)
chart(c,735,bi['n'],[bi['left']],[RED],['左侧：n<0 为 −0.5ⁿ'],ylim=(-32,0),ticks=[-5,0,7],height=340,stems=True)
rows(c,1310,['两者代数式都是 1/(1−0.5z⁻¹)','右侧要求 |z|>0.5；左侧要求 |z|<0.5','不是同一因果程序换个算法：时间支持变了'])
c.save('15-two-sequences.png','同有理式的右侧/左侧序列和不同支持')

c=Canvas('收敛域也是答案的一部分')
plane(c,140,pole=D['bilateral']['pole'],region='outside',label='上：右侧序列，蓝色区域 |z|>0.5')
plane(c,1050,pole=D['bilateral']['pole'],region='inside',label='下：左侧序列，蓝色区域 |z|<0.5')
rows(c,1970,['圆周 |z|=0.5 均不包含；只画有限窗口','绿单位圆只在上面的收敛域内','原点空心圆是零点，红叉是极点'])
c.save('16-roc.png','两个ROC与单位圆、极点零点的实际几何')

c=Canvas('稳定性：看尾迹能否绝对相加')
for i,item in enumerate(D['stability']):
 chart(c,145+i*500,n,[item['impulse']],[ [BLUE,ORANGE,RED][i] ],[f"a={fmt(item['a'])}：单位冲激输出"],ylim=(0,max(item['impulse'])),ticks=[0,5,10,15],height=300,stems=True)
chart(c,1645,n,[D['stability'][1]['step']],[ORANGE],['a=1：改为每拍输入1，输出持续增长'],ylim=(0,16),ticks=[0,5,10,15],height=330,stems=True)
rows(c,2240,['a=0.5 衰减，绝对和为2','a=1 冲激不衰减；阶跃会持续累加','a=1.1 增长；有限图不代表有界','这三个例子都规定为因果、零初态系统'])
c.save('17-stability.png','衰减/临界/增长冲激与因果BIBO条件')

c=Canvas('沿单位圆走，看不同频率的增益')
f=D['frequency'];omega=np.array(f['omega'])/np.pi
chart(c,145,omega,[f['gain']],[BLUE],['横轴 ω/π；纵轴幅度增益 |H|'],ylim=(0,2),ticks=[0,.5,1],height=420)
rows(c,760,['ω 是每拍旋转的弧度，不是赫兹','ω=0：缓慢/直流，增益2','ω=π：每拍正负交替，增益2/3','若采样率为 Fs，频率 f=ωFs/(2π)'])
c.save('18-frequency.png','由实际复数频响得到幅度随离散频率变化')

c=Canvas('实际输入余弦：核对预测的增益与相位')
for i,item in enumerate(D['sine']):
 k=slice(32,64)
 chart(c,145+i*650,item['n'][k],[item['x'][k],item['y'][k],item['steady'][k]],[GRAY,BLUE,ORANGE],['灰输入／蓝递推／棕理论稳态（重合）'],ylim=(-2,2),ticks=[32,48,63],height=360)
 c.text(60,690+i*650,f"增益 {item['gain']:.4f}；相位 {item['phase']:.4f} rad",40)
rows(c,1480,['上：ω=π/8；下：ω=3π/4','都从零初态开始，只显示 n=32…63','已消退的起步误差不等于完全不存在'])
c.save('19-sinusoids.png','实际时域余弦输出与频域预测交叉核验')

c=Canvas('分块处理：把状态接上，尾巴才不断')
sc=D['scipy']
chart(c,145,n[:10],[y[:10],np.r_[sc['first'],sc['reset']][:10]],[BLUE,RED],['蓝：完整或正确接续，逐项相同','红：第4拍错误重置状态'],ylim=(0,3),ticks=[0,3,4,9],height=410)
rows(c,820,[f"前4拍结束，SciPy状态 zf={fmt(sc['state'][0])}",'继续时把 zf 作为下一块 zi','本例zi储存0.5×上一输出，不是上一输出','API状态含义要按实现核对'])
c.save('20-chunks.png','真实SciPy分块状态与重置错误的输出差异')

# The UI screenshot is created separately by actual Chromium.
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'generated':len(meta),'files':[m['file'] for m in meta]}))
