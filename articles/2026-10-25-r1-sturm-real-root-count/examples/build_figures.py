"""Original Sturm real-root counting figures. Code CC0; figures CC BY 4.0.
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
  meta.append(dict(file='assets/'+name,width=im.width,height=im.height,min_font_px=min(z[2] for z in self.boxes),effective_min_font_at_354=round(min(z[2] for z in self.boxes)/3,2),identity='原创精确有理数算法图或教学示意；执行数值来自 results.json',purpose=purpose,numeric_geometry=self.geometry,checks=['canvas','declared-box','text-overlap','font-size','contrast','glyph-cmap','ink-pixels','actual-dimensions']))
from fractions import Fraction as F
D=DATA;M=D['main'];GRAY='#627487';RED='#a13631';PALE='#e4eef6'
def rows(c,y,lines):
 for i,s in enumerate(lines):c.text(55,y+i*70,s,40)
def fmt(v):return f'{v:.3g}'
def chart(c,y,data,colors,labels,ylim=None,ticks=None,height=360):
 xs=data['x'];ss=data['ys'];lo,hi=ylim or (min(map(min,ss)),max(map(max,ss)))
 left,right,top,bot=170,940,y+55,y+height;xmin,xmax=min(xs),max(xs)
 tr=lambda a,b:(left+(a-xmin)/(xmax-xmin)*(right-left),bot-(b-lo)/(hi-lo)*(bot-top))
 c.line((left,top),(left,bot),GRAY);c.line((left,bot),(right,bot),GRAY)
 for v in [lo,hi]:
  label=fmt(v);c.text(left-25-measure(c.d,label,40),tr(xmin,v)[1]-25,label,40)
 for v in (ticks or [xmin,xmax]):
  xx=tr(v,lo)[0];label=fmt(v);c.text(xx-measure(c.d,label,40)/2,bot+12,label,40)
 if lo<0<hi:c.line(tr(xmin,0),tr(xmax,0),GRAY,True)
 for vals,col in zip(ss,colors):c.d.line([tr(x,v) for x,v in zip(xs,vals)],fill=col,width=6)
 c.bottom=max(c.bottom,bot)
 for i,s in enumerate(labels):c.text(55,bot+90+i*62,s,40,colors[i] if i<len(colors) else INK)
 c.geometry.append({'kind':'numeric-curves','source':'results.json','xrange':[xmin,xmax],'yrange':[lo,hi],'samples':len(xs),'labels':labels})
 return bot+90+len(labels)*62

def sign(s):return '+' if s>0 else ('−' if s<0 else '0')
def signrow(c,y,label,record):
 c.text(55,y,label,42)
 for i,v in enumerate(record['signs']):c.text(280+i*140,y,sign(v),48,GRAY if v==0 else (BLUE if v>0 else RED))
 c.text(915,y,str(record['v']),44,GREEN)

def interval(c,y,a,b,count,xmin=-2,xmax=2):
 # All lengths follow the exact numeric endpoints using a shared horizontal axis.
 tx=lambda v:130+(float(F(v))-xmin)/(xmax-xmin)*800
 left,right=tx(a),tx(b)
 c.line((left,y),(right,y),BLUE)
 c.d.ellipse((left-11,y-11,left+11,y+11),fill=BG,outline=BLUE,width=5)
 c.d.ellipse((right-11,y-11,right+11,y+11),fill=BLUE)
 c.geometry.append({'kind':'half-open-interval','a':a,'b':b,'xrange':[xmin,xmax],'pixel_bounds':[left,right],'count':count})

c=Canvas('Sturm：先数清根，再逼近根')
y=chart(c,120,M['plot'],[BLUE],['上图：p=x³−x；横轴 x，纵轴 p'],ylim=(-6,6),ticks=[-2,-1,0,1,2],height=350)
y=chart(c,y+20,{'x':M['v_plot']['x'],'ys':[M['v_plot']['v']]},[GREEN],['下图：同一 x 上的符号变化数 V(x)'],ylim=(0,3),ticks=[-2,-1,0,1,2],height=310)
rows(c,y+25,['每越过一个不同实根，V 减少 1',f'从 −2 到 2：{M["rows"][0]["v"]}−{M["rows"][-1]["v"]}={M["rows"][0]["v"]-M["rows"][-1]["v"]} 个根','曲线与阶梯由本文程序实际生成'])
c.save('00-cover.png','把根的位置与单调下降的变化数对齐')

c=Canvas('端点同号，区间里仍可能有根')
r=D['repeated'];y=chart(c,140,r['touch_plot'],[BLUE],['q=(x−1)²(x+2)；横轴 x，纵轴 q'],ylim=(0,1),ticks=[.5,1,1.5],height=400)
rows(c,y+45,[f'q(1/2)={r["samples"][0]["y"]}>0',f'q(3/2)={r["samples"][1]["y"]}>0','但 x=1 是二重根：只接触横轴','采样两点看不到这个零点'])
c.save('01-touch.png','明确偶重根的接触形状和采样漏根')

c=Canvas('导数告诉我们：穿过根时朝哪边走')
y=chart(c,140,M['tangent_plot'],[BLUE,ORANGE],['蓝：p=x³−x','棕：x=1 处切线 y=2(x−1)'],ticks=[.75,1,1.25],height=380)
rows(c,y+45,['横轴 x；纵轴函数值',f'p′=3x²−1；p′(1)={M["root_steps"][1]["values"][1]}>0','在根的近旁，p 从负变正','切线只解释局部方向，并非全局替代'])
c.save('02-derivative.png','简单根处的局部斜率及导数的计数作用')

c=Canvas('第一次长除法：为什么余数前要加负号？')
a=M['division'][0];quot=a['quotient'][1];rem=a['remainder'][1]
rows(c,145,['被除式：x³−x','除式：3x²−1',f'首项相除：x³ ÷ 3x² = ({quot})x','乘回去：x³−(1/3)x'])
c.line((55,455),(1000,455),GRAY)
rows(c,490,['相减：(x³−x)−(x³−x/3)',f'普通余数：({rem})x','取相反数：S₂=(2/3)x'])
c.card(55,745,950,110,'S₀ = 商 × S₁ − S₂')
rows(c,900,['余数链保留这个减号','它保证中间项为零时，左右两项异号'])
c.save('03-division.png','完整执行首项相除、乘回、相减及负余数')

c=Canvas('继续除：次数下降，链就会结束')
rows(c,145,['(3x²−1) ÷ ((2/3)x)',f'商为 ({M["division"][1]["quotient"][1]})x',f'普通余数为 {M["division"][1]["remainder"][0]}，所以 S₃=1','再以常数1作除式，余数为0，停止'])
for i,(lab,polynomial) in enumerate(zip(['S₀=x³−x','S₁=3x²−1','S₂=(2/3)x','S₃=1'],M['chain'])):
 degree=len(polynomial)-1
 yy=480+i*155;c.text(65,yy,lab,44)
 if degree:c.d.rectangle((500,yy+8,500+degree*125,yy+55),fill=BLUE)
 c.text(920,yy,str(degree),42)
rows(c,1130,['右侧共轴条长表示多项式次数','零余数不加入链；只保存非零项'])
c.geometry.append({'kind':'degree-bars','values':[len(p)-1 for p in M['chain']],'pixels_per_degree':125})
c.save('04-chain.png','第二次除法、停止条件与完整链的次数')

c=Canvas('逐行代入：先删零，再数相邻变号')
c.text(55,140,'x',42)
for i,s in enumerate(['S₀','S₁','S₂','S₃']):c.text(265+i*140,140,s,42)
c.text(905,140,'V',42)
for i,r in enumerate(M['rows']):signrow(c,240+100*i,r['x'],r)
rows(c,1010,['x=0：0，−，0，+ → −，+','删掉零后，只发生 1 次变号','V(−2)−V(2)=3−0=3'])
c.save('05-sign-table.png','端点及根点的完整符号表与删零规则')

c=Canvas('中间项过零，变化数为什么不动？')
y=chart(c,120,M['middle_plot'],[BLUE,ORANGE,GREEN],['蓝 S₀；棕 S₁；绿 S₂','横轴 x；纵轴各链项值'],ylim=(-.5,.5),ticks=[.5,.6],height=340)
rows(c,y+30,['S₁ 在 1/√3≈0.577 处为零','该点 S₀=−S₂，左右邻项异号','跨过它：−，−，+ → −，+，+','这两个三项窗口都只有 1 次变号','零点当下：−，0，+ → −，+'])
c.save('06-middle-zero.png','以实际三条曲线解释中间项过零不增减变化数')

c=Canvas('原多项式过根，变化数恰好少一个')
rows(c,145,['看 x=1 的附近：S₁ 始终为正','导数正：S₀ 从负走到正','因此首对符号：−，+ → +，+'])
c.text(55,405,'x',42)
for i,s in enumerate(['S₀','S₁','S₂','S₃']):c.text(265+i*140,405,s,42)
c.text(905,405,'V',42)
for i,r in enumerate(M['root_steps']):signrow(c,505+i*100,r['x'],r)
rows(c,870,['根处先删掉 S₀=0，取到右侧计数','导数负时：+，− → −，−','同样恰好少 1 次变号'])
c.save('07-root-drop.png','主算例根左右及恰在根上的完整符号变化')

c=Canvas('端点是根：同一对数，四种区间')
for i,(ends,n) in enumerate(M['counts'].items()):
 yy=170+i*210;c.text(55,yy,f'{ends[0]}−1, 1{ends[1]}：{n} 个不同根',44)
 # Draw exact geometric endpoints and filled/open root markers.
 c.line((220,yy+90),(820,yy+90),GRAY)
 for root_value in M['roots']:
  x=int(root_value)
  xx=220+(x+1)*300;included=(x> -1 or ends[0]=='[') and (x<1 or ends[1]==']')
  c.d.ellipse((xx-14,yy+76,xx+14,yy+104),fill=BLUE if included else BG,outline=BLUE,width=4)
  c.text(xx-18,yy+112,str(x),40)
 c.geometry.append({'kind':'endpoint-inclusion','convention':ends,'count':n,'roots':[-1,0,1]})
rows(c,1110,['实心计入，空心排除','本文默认 (a,b]：左开右闭','V(a)−V(b) 直接给出这个默认值'])
c.save('08-endpoints.png','根端点的四种区间约定避免无声多算少算')

c=Canvas('二分时，位于中点的根只属于左支')
# First two complete levels, endpoints are data from the executed tree.
levels={}
for n in M['tree']:
 depth=0;t=n
 while t['parent'] is not None:depth+=1;t=M['tree'][t['parent']]
 if depth<=2:levels.setdefault(depth,[]).append(n)
positions={}
for depth,nodes in levels.items():
 nodes=sorted(nodes,key=lambda t:F(t['a']));w=950/len(nodes)
 for j,n in enumerate(nodes):positions[n['id']]=(55+(j+.5)*w,170+depth*260)
for depth,nodes in levels.items():
 for n in nodes:
  xx,yy=positions[n['id']]
  if n['parent'] in positions:
   px,py=positions[n['parent']];c.arrow((px,py+140),(xx,yy-15),GRAY)
for depth,nodes in levels.items():
 for n in nodes:
  xx,yy=positions[n['id']];label=f'({n["a"]},{n["b"]}]';width=measure(c.d,label,40)
  c.text(xx-width/2,yy,label,40);s=f'{n["count"]} 根';c.text(xx-measure(c.d,s,42)/2,yy+75,s,42,GREEN if n['count'] else GRAY)
rows(c,1030,['第一刀 m=0：2 根 + 1 根 = 3 根','零点0计入 (−2,0]，不计入 (0,2]','图展示前两层；空区间停止','有根区间继续切分到目标宽度'])
c.geometry.append({'kind':'executed-isolation-tree','node_ids':list(positions),'source':'results.json'})
c.save('09-tree.png','执行树的前两层与中点根的唯一归属')

c=Canvas('隔离结果：每个窄区间恰有一根')
for i,(a,b) in enumerate(M['isolation']):
 yy=180+i*240;c.text(55,yy,f'({a}, {b}]：宽度 {F(b)-F(a)}，1 根',42);interval(c,yy+115,a,b,1)
c.line((130,910),(930,910),GRAY)
for x in [-2,-1,0,1,2]:
 xx=130+(x+2)*200;c.line((xx,902),(xx,918),GRAY);c.text(xx-20,930,str(x),40)
rows(c,1050,['横向位置共用 x 轴；左空右实','宽度小，不表示根就是区间中点','本例根可因式分解直接得到','一般多项式也能得到有证明的包围区间'])
c.save('10-isolates.png','实际隔离输出与统一坐标下的半开小区间')

r=D['repeated']
c=Canvas('重根先去重复：保留位置，丢弃重数')
y=chart(c,130,r['plot'],[BLUE,ORANGE],['蓝：q=(x−1)²(x+2)','棕：平方自由部分 (x−1)(x+2)'],ticks=[-3,-2,0,1,2],height=370)
rows(c,y+35,['横轴 x；纵轴多项式值','gcd(q,q′)=x−1','除去公因式后，根位置仍是 −2 和 1',f'不同实根：{r["count"]} 个；按重数合计：3','本文计数接口返回不同位置的个数'])
c.save('11-squarefree.png','重复因子移除前后的实际形状与根位置')

c=Canvas('不能把链中的 −1 随手变成 +1')
y=chart(c,120,D['bad_normalization']['plot'],[BLUE],['p=x²+1，横轴 x；纵轴 p'],ylim=(0,5),ticks=[-2,0,2],height=300)
q=D['bad_normalization'];rows(c,y+30,['正确链：[x²+1，2x，−1]',f'V(−2)={q["correct"][0]["v"]}，V(2)={q["correct"][1]["v"]} → 0 根','误改尾项为 +1：',f'V(−2)={q["wrong"][0]["v"]}，V(2)={q["wrong"][1]["v"]} → 假报 2 根','各项乘正数不改符号；乘负数会改变'])
c.save('12-wrong-scale.png','无实根反例揭示任意负缩放破坏Sturm性质')

c=Canvas('输入先舍入，精确算法也数不回丢掉的根')
r=D['rounding'];y=chart(c,120,{'x':r['scaled_x'],'ys':[r['exact_y'],r['rounded_y']]},[BLUE,ORANGE],['蓝：精确系数；棕：常数先舍入','横轴 u=(x−1)/10⁻¹⁰','纵轴函数值 / 10⁻²⁰','灰虚线：0'],ylim=(-1,4),ticks=[-2,-1,0,1,2],height=360)
rows(c,y+35,['精确：x²−2x+(1−10⁻²⁰)','舍入：x²−2x+1',f'在 (0,2] 内：{r["exact_count"]} 根变成 {r["rounded_count"]} 根','此图放大极窄邻域，不能当原坐标','Fraction 要从精确整数/字符串建立'])
c.save('13-rounding.png','输入系数舍入改变根数的真实可复算反例')

c=Canvas('不是只会处理已知整数根')
z=D['irrational_isolation'];a,b=F(z['a']),F(z['b']);rows(c,145,['另一个输入：x²−2，在 (0,2] 内',f'隔离得到：({z["a"]}, {z["b"]}]',f'宽度 {z["width"]}，恰有 1 个根'])
left,right=150,930;scale=(right-left)/(float(b-a)*2)
tx=lambda v:left+(float(v)-float(a-(b-a)/2))*scale
c.line((left,515),(right,515),GRAY)
for val,label in [(a,z['a']),(b,z['b'])]:
 xx=tx(val);c.line((xx,490),(xx,540),BLUE);c.text(xx-measure(c.d,label,40)/2,565,label,40)
# Root position is illustrative floating sqrt, not used by the isolator.
xx=tx(math.sqrt(2));c.d.ellipse((xx-10,505,xx+10,525),fill=GREEN);c.text(470,435,'√2',44,GREEN)
rows(c,690,[f'左端平方 = {z["a_squared"]} < 2',f'右端平方 = {z["b_squared"]} > 2','严格证据来自有理数符号，不靠绘图','图中 √2 标记仅用浮点近似定位'])
c.geometry.append({'kind':'rational-isolation','a':str(a),'b':str(b),'width':str(b-a),'sqrt_marker':'illustrative float only'})
c.save('14-irrational.png','无理根的精确有理包围区间及独立平方核算')

(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(f'{len(meta)} original diagrams generated; all geometry/font/ink checks passed')
