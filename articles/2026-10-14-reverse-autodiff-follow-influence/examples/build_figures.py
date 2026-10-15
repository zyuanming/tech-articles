"""Draw original explanatory diagrams and measured numerical-result plots."""
from pathlib import Path
import argparse,json,math
from PIL import Image,ImageDraw,ImageFont
A=Path(__file__).resolve().parents[1]
P=argparse.ArgumentParser();P.add_argument('--output',type=Path,default=A);args=P.parse_args()
O=args.output; (O/'assets').mkdir(parents=True,exist_ok=True)
R=json.loads((A/'examples/expected-results.json').read_text())
W=1062; BG='#F7F4EA';INK='#163645';BLUE='#246F97';ORANGE='#B65A27';GREEN='#337766';MUTED='#61747B';PALE='#E7EDF0';WHITE='#FFFFFF';RED='#A53C41'
fonts={}; metadata=[]; current=''
def F(n=40,bold=False):
 key=(n,bold)
 if key not in fonts:fonts[key]=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-'+('Bold'if bold else'Regular')+'.ttc',n,index=2)
 return fonts[key]
def text(d,x,y,s,size=40,color=INK,center=False,bold=False):
 assert size>=36
 width=d.textlength(s,font=F(size,bold))
 if center:x-=width/2
 assert x>=18 and x+width<=W-18,(current,s,x,width)
 d.text((x,y),s,font=F(size,bold),fill=color)
def lines(d,x,y,ss,size=40,color=INK,center=False,gap=58):
 for i,s in enumerate(ss):text(d,x,y+i*gap,s,size,color,center)
def canvas(name,title,h=1080):
 global current
 current=name
 im=Image.new('RGB',(W,h),BG);d=ImageDraw.Draw(im)
 d.rounded_rectangle((36,32,1026,125),radius=20,fill=INK)
 text(d,531,47,title,48,WHITE,True,True)
 return im,d
def save(im,name,role):
 im.save(O/'assets'/name)
 metadata.append(dict(file='assets/'+name,width=im.width,height=im.height,min_font_px=36,min_effective_px_at_354=12,role=role,identity='original teaching diagram' if 'curve'not in name and 'error'not in name else'original plot from stated model or recorded experiment'))
def box(d,rect,ss,color=BLUE,fill=WHITE,size=40):
 d.rounded_rectangle(rect,radius=20,fill=fill,outline=color,width=5)
 n=len(ss);cy=(rect[1]+rect[3])/2
 for i,s in enumerate(ss):text(d,(rect[0]+rect[2])/2,cy-n*29+i*58,s,size,color,True)
def arrow(d,pts,color=BLUE,width=7):
 d.line(pts,fill=color,width=width,joint='curve');a,b=pts[-2:];ang=math.atan2(b[1]-a[1],b[0]-a[0]);sz=19
 d.polygon([b,(b[0]-sz*math.cos(ang-.5),b[1]-sz*math.sin(ang-.5)),(b[0]-sz*math.cos(ang+.5),b[1]-sz*math.sin(ang+.5))],fill=color)
def dot(d,x,y,color=BLUE,r=9):d.ellipse((x-r,y-r,x+r,y+r),fill=color)
def graph(name,dual=False):
 im,d=canvas(name,'正向数值  /  反向梯度'if dual else'先按依赖关系，算出每个值',1300)
 nodes={'x':(270,245),'y':(800,245),'u':(650,475),'v':(650,705),'r':(650,935),'L':(650,1165)}
 for a,b in [('x','u'),('y','u'),('u','v'),('v','r'),('r','L')]:
  p=nodes[a];q=nodes[b];arrow(d,[(p[0],p[1]+70),(q[0],q[1]-70)])
 arrow(d,[(270,315),(270,705),(440,705)])
 text(d,75,470,'直接用x',36,BLUE)
 text(d,75,550,'再加一次',36,BLUE)
 labels={'u':'u = x × y','v':'v = u + x','r':'r = v − 10','L':'L = r² / 2'}
 for n,(x,y) in nodes.items():
  val=R['main'][n]['value'];g=R['main'][n]['gradient']
  if dual:ss=[f'{n}: 值 {val:g}',f'梯度 {g:g}']
  else:ss=[labels.get(n,n),f'{val:g}']
  if dual:
   d.rounded_rectangle((x-200,y-75,x+200,y+75),radius=20,fill=WHITE,outline=MUTED,width=5)
   text(d,x,y-58,ss[0],40,BLUE,True)
   text(d,x,y,ss[1],40,ORANGE,True)
  else:box(d,(x-200,y-75,x+200,y+75),ss,BLUE,size=40)
 return im
# 01
im,d=canvas('01','两个旋钮，一个偏差分数',1140)
for x,label,val in [(275,'x',2),(787,'y',3)]:
 text(d,x,165,label,52,BLUE,True,True);d.ellipse((x-130,245,x+130,505),fill=WHITE,outline=BLUE,width=7)
 d.line((x,375,x+85,300),fill=BLUE,width=15);text(d,x,400,str(val),48,BLUE,True)
arrow(d,[(275,530),(275,595),(531,595),(531,650)]);arrow(d,[(787,530),(787,595),(531,595)])
box(d,(120,650,942,780),['先乘：2 × 3 = 6','再加：6 + 2 = 8'])
text(d,531,815,'目标是10；还差 −2',44,ORANGE,True)
box(d,(120,900,942,1040),['偏差分数 L = (−2)² / 2 = 2'],ORANGE)
save(im,'01-two-knobs.png','Concrete invented input-to-output situation')
# 02 plot
im,d=canvas('02','小幅改变，不等于沿直线走',1130)
px=lambda x:140+(x-1.7)/1.2*790;py=lambda y:700-y/5.2*470
for y in [0,2,4]:
 d.line((140,py(y),930,py(y)),fill='#CED9DA',width=2);text(d,65,py(y)-25,str(y),36)
for x in [2,2.5]:text(d,px(x),725,str(x),36,center=True)
text(d,155,165,'L（y固定为3）',40);text(d,955,710,'x',40)
d.line((140,220,140,700),fill=INK,width=4);d.line((140,700,930,700),fill=INK,width=4)
pts=[(px(x),py(.5*(4*x-10)**2))for x in [1.7+i*1.2/200 for i in range(201)]];d.line(pts,fill=BLUE,width=8)
# tangent restricted visible portion
pts=[(px(x),py(2-8*(x-2)))for x in [1.7+i*.5/100 for i in range(101)]];d.line(pts,fill=ORANGE,width=5)
dot(d,px(2),py(2),ORANGE);text(d,560,290,'切线斜率 −8',40,ORANGE);text(d,680,580,'真实曲线',36,BLUE)
box(d,(75,825,987,1050),['x：2 → 2.01','L：2 → 1.9208','平均变化率：−0.0792 / 0.01 = −7.92'],ORANGE,size=36)
save(im,'02-small-change.png','Loss curve and tangent with actual finite perturbation')
save(graph('03'),'03-forward-graph.png','Full original computation DAG with shared x and forward values')
# 04
im,d=canvas('04','每种运算，提供局部变化率',1280)
for y,title,ss in [(180,'加法：c = a + b',['对a：1    对b：1','某一项多一点，和就多同样多']), (530,'乘法：u = x × y',['对x：y = 3    对y：x = 2','局部规则要用另一侧的当前数值']), (880,'半平方：L = r² / 2',['对r：r = −2','从−2走向0，平方分数会下降'])]:
 box(d,(65,y,997,y+290),[title]+ss,size=40)
save(im,'04-local-rules.png','Local derivative rules for three primitive operations')
#05
im,d=canvas('05','从输出的1，沿路径往回传',1230)
for y,name,val in [(220,'L',1),(480,'r',-2),(740,'v',-2),(1000,'u',-2)]:
 box(d,(80,y,450,y+140),[f'{name} 的梯度',str(val)],ORANGE)
for y,label in [(360,'× (−2)：半平方'),(620,'× 1：减去10'),(880,'× 1：加法')]:
 arrow(d,[(265,y),(265,y+120)],ORANGE);text(d,500,y+30,label,40,ORANGE)
text(d,531,1150,'传回敏感度，不是恢复原输入',40,ORANGE,True)
save(im,'05-chain-backward.png','Reverse seed and local multiplier chain')
#06
im,d=canvas('06','同一个x，两条路同时起作用',1230)
box(d,(330,180,732,310),['同一个输入 x'],BLUE)
arrow(d,[(410,310),(270,410)]);arrow(d,[(650,310),(792,410)])
box(d,(65,430,500,630),['直接进入v','贡献 −2 × 1','= −2'],ORANGE,size=38)
box(d,(562,430,997,630),['先经过u','贡献 −2 × 3','= −6'],ORANGE,size=38)
arrow(d,[(270,640),(270,755),(420,815)],ORANGE);arrow(d,[(792,640),(792,755),(642,815)],ORANGE)
box(d,(115,825,947,960),['x的梯度 = −2 + (−6) = −8'],ORANGE,size=40)
box(d,(115,1030,947,1165),['y只有乘法一路：−2 × 2 = −4'],GREEN,size=40)
save(im,'06-two-paths.png','Separate derivative paths and accumulation at shared x')
save(graph('07',True),'07-two-ledgers.png','Distinct primal value and reverse gradient at every node')
#08
im,d=canvas('08','先收齐，再继续向前传',1350)
box(d,(340,180,722,330),['z = w + w','z的梯度：1'])
arrow(d,[(380,330),(240,430),(240,560)],ORANGE);arrow(d,[(682,330),(822,430),(822,560)],ORANGE)
text(d,65,455,'第一份1',36,ORANGE);text(d,840,455,'第二份1',36,ORANGE)
arrow(d,[(240,560),(400,610)],ORANGE);arrow(d,[(822,560),(662,610)],ORANGE)
box(d,(210,620,852,790),['w = x × x = 4','w先收齐：1 + 1 = 2'],ORANGE)
arrow(d,[(360,790),(240,940)],ORANGE);arrow(d,[(702,790),(822,940)],ORANGE)
text(d,55,825,'2 × x = 4',36,ORANGE);text(d,790,825,'2 × x = 4',36,ORANGE)
arrow(d,[(240,940),(400,1060)],ORANGE);arrow(d,[(822,940),(662,1060)],ORANGE)
box(d,(170,1080,892,1260),['同一个 x = 2','收到 4 + 4，梯度为8'],GREEN)
save(im,'08-shared-node-order.png','Shared intermediate and duplicate operand slots')
#09
im,d=canvas('09','三种办法，做的事情不同',1270)
for y,title,ss,col in [(180,'符号微分',['变换公式','生成导数的代数表达式'],BLUE),(520,'有限差分',['改输入，再运行','用输出差 ÷ 输入差估计'],ORANGE),(860,'自动微分',['执行局部导数规则','按程序依赖相乘、累加'],GREEN)]:
 box(d,(75,y,987,y+280),[title]+ss,col,size=44)
save(im,'09-three-methods.png','Compare objects and operations used by three differentiation approaches')
#10 plot actual
im,d=canvas('10','h太大或太小，都可能不准',1180)
X0,X1,Y0,Y1=210,950,770,240
px=lambda e:X0+(-e-1)/17*(X1-X0);py=lambda e:Y0-(e+8)/9*(Y0-Y1)
for e in [-8,-6,-4,-2,0]:
 y=py(e);d.line((X0,y,X1,y),fill='#CBD6D7',width=3);text(d,48,y-25,f'10^{e}',36)
for e in [-1,-4,-7,-10,-13,-16,-18]:
 x=px(e);d.line((x,Y0,x,Y0+14),fill=INK,width=3);text(d,x,Y0+25,f'{e}',36,center=True)
d.line((X0,Y1,X0,Y0,X1,Y0),fill=INK,width=4)
text(d,531,165,'|差分估计 − (−8)|',40,center=True)
text(d,531,855,'横轴：log10(h)，往右步长更小',36,center=True)
pts=[]
for r in R['finite_difference']:
 p=(px(math.log10(r['h'])),py(math.log10(r['absolute_error'])));pts.append(p)
d.line(pts,fill=ORANGE,width=7)
for p in pts:dot(d,*p,ORANGE)
box(d,(75,940,987,1110),['实际18次前向差分；双精度浮点','末三点：2 + h 已经舍入为2'],ORANGE,size=38)
save(im,'10-difference-error.png','18 actual forward finite-difference errors, logarithmic axes')
#11
im,d=canvas('11','输入与输出，决定划算的方向',1300)
text(d,531,170,'很多输入 → 一个分数',44,BLUE,True)
for i in range(4):
 x=160+i*245;box(d,(x-65,280,x+65,390),[f'x{i+1}'],BLUE)
 arrow(d,[(x,400),(531,540)],BLUE)
box(d,(330,560,732,680),['L：从这里反传'],ORANGE,size=40)
text(d,531,720,'一次反传，得到各输入的梯度',40,ORANGE,True)
d.line((75,805,987,805),fill='#CBD6D7',width=4)
text(d,531,835,'一个输入 → 很多输出',44,GREEN,True)
box(d,(400,930,662,1040),['输入 x'],GREEN)
for i in range(4):
 x=160+i*245;arrow(d,[(531,1040),(x,1115)],GREEN);box(d,(x-65,1130,x+65,1235),[f'f{i+1}'],GREEN)
save(im,'11-which-direction.png','Many-to-one reverse mode versus one-to-many forward mode')
#12
im,d=canvas('12','记住中间量，或者以后重算',1190)
text(d,531,175,'全部保存：反传时直接取用',42,BLUE,True)
for i in range(5):
 x=140+i*195;box(d,(x-70,290,x+70,420),[str(i)],BLUE);d.rounded_rectangle((x-57,450,x+57,515),15,fill=BLUE)
 if i<4:arrow(d,[(x+75,355),(x+120,355)],BLUE,width=4)
text(d,531,565,'蓝色块：保留的中间信息',38,BLUE,True)
d.line((75,660,987,660),fill='#CBD6D7',width=4)
text(d,531,700,'只存检查点：缺的段落重新算',42,GREEN,True)
for i in range(5):
 x=140+i*195;box(d,(x-70,800,x+70,930),[str(i)],GREEN)
 if i in [0,2,4]:d.rounded_rectangle((x-57,960,x+57,1025),15,fill=GREEN)
 if i<4:arrow(d,[(x+75,865),(x+120,865)],ORANGE,width=4)
text(d,531,1090,'示意：减少保存，增加计算',40,GREEN,True)
save(im,'12-remember-or-recompute.png','Conceptual retention and checkpoint recomputation, no memory benchmark')
#13
im,d=canvas('13','沿本次分支求导，不会抹平尖角',1170)
px=lambda x:531+x*150;py=lambda y:755-y*150
for a,b in [((-2.5,0),(2.5,0)),((0,-.2),(0,3))]:d.line((*[c for p in [a,b] for c in (px(p[0]),py(p[1]))],),fill=INK,width=4)
d.line([(px(-2.5),py(2.5)),(px(0),py(0)),(px(2.5),py(2.5))],fill=BLUE,width=9)
for x in [-2,0,2]:text(d,px(x),790,str(x),40,center=True)
text(d,150,180,'f(x) = |x|',48,BLUE)
text(d,110,290,'左侧斜率 −1',38,ORANGE);text(d,680,290,'右侧斜率 +1',38,GREEN)
dot(d,px(0),py(0),RED,12)
box(d,(75,910,987,1090),['x = 0：普通导数不存在','框架约定值 ≠ 证明可导'],RED,size=42)
save(im,'13-branch-and-corner.png','Absolute-value branches and mathematically nondifferentiable corner')
#14
im,d=canvas('14','方向对了，步子也可能迈太大',1240)
px=lambda x:160+(x-1.5)/2.5*790;py=lambda y:770-y/20*500
for y in [0,2,6,10,18]:
 d.line((160,py(y),950,py(y)),fill='#CBD6D7',width=2);text(d,70,py(y)-25,str(y),36)
for x in [2,2.5,3.6]:text(d,px(x),795,str(x),36,center=True)
d.line((160,270,160,770,950,770),fill=INK,width=4)
xs=[1.5+i*2.5/250 for i in range(251)];d.line([(px(x),py(.5*(4*x-10)**2))for x in xs],fill=BLUE,width=8)
for x,col in [(2,INK),(2.08,GREEN),(3.6,ORANGE)]:dot(d,px(x),py(.5*(4*x-10)**2),col,12)
arrow(d,[(px(2),py(2)-30),(px(3.6),py(9.68)-30)],ORANGE)
text(d,170,170,'L，固定y=3；起点x=2',40)
text(d,955,790,'x',36)
box(d,(75,920,987,1035),['小步：x = 2.08，L = 1.4112'],GREEN,size=40)
box(d,(75,1085,987,1200),['大步：x = 3.6，L = 9.68'],ORANGE,size=40)
save(im,'14-gradient-is-not-optimizer.png','Actual loss after two step sizes, fixed y')
# cover separate from body
im,d=canvas('cover','程序怎样倒着计算影响？',1062)
text(d,531,170,'反向自动微分',64,ORANGE,True,True)
box(d,(90,330,400,490),['输入 x','输入 y'],BLUE)
box(d,(660,330,972,490),['最终分数 L'],BLUE)
arrow(d,[(420,375),(640,375)],BLUE);text(d,531,430,'正向算值',36,BLUE,True)
arrow(d,[(640,620),(420,620)],ORANGE);text(d,531,670,'反向传梯度',40,ORANGE,True)
box(d,(100,790,962,980),['一条路径：相乘','多条路径：相加'],ORANGE,size=48)
im.save(O/'cover.png');metadata.append(dict(file='cover.png',width=1062,height=1062,min_font_px=36,min_effective_px_at_354=12,role='Separate original cover',identity='original explanatory illustration'))
(O/'examples').mkdir(exist_ok=True)
(O/'examples/figure-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
print(f'Drew {len(metadata)-1} body images and separate cover')
