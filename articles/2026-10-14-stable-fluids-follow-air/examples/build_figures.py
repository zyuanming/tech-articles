#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original figures from actual solver output. See README for reproduction."""
from pathlib import Path
import argparse,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];A=P/'assets';A.mkdir(exist_ok=True)
ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);args=ap.parse_args()
DATA=Path(args.data);R=json.loads((DATA/'results.json').read_text());Z=np.load(DATA/'frames.npz');F=Z['frames']
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
W=1062;BG='#f6f2e9';INK='#203642';TEAL='#087c80';BLUE='#3379a9';GOLD='#dda73d';RED='#bf593f';GRAY='#66717a';WHITE='#ffffff'
meta=[];im=d=None;smallest=99

def font(s=44,b=False):return ImageFont.truetype(BOLD if b else FONT,s,index=2)
def text(x,y,t,s=44,c=INK,b=False,anchor=None):
 global smallest
 smallest=min(smallest,s);d.text((x,y),str(t),font=font(s,b),fill=c,anchor=anchor)
def line(points,c=INK,w=5):d.line(points,fill=c,width=w)
def box(x,y,w,h,fill='white',stroke=None,r=18):d.rounded_rectangle((x,y,x+w,y+h),r,fill,stroke,width=3)
def arrow(x1,y1,x2,y2,c=TEAL,w=7,tip=19):
 line([(x1,y1),(x2,y2)],c,w);a=math.atan2(y2-y1,x2-x1)
 d.polygon([(x2,y2),(x2-tip*math.cos(a-.5),y2-tip*math.sin(a-.5)),(x2-tip*math.cos(a+.5),y2-tip*math.sin(a+.5))],fill=c)
def dot(x,y,c=TEAL,r=11):d.ellipse((x-r,y-r,x+r,y+r),fill=c)
def new(title,h=950,sub=None):
 global im,d,smallest
 smallest=99;im=Image.new('RGB',(W,h),BG);d=ImageDraw.Draw(im);d.rectangle((0,0,16,h),fill=TEAL)
 text(48,32,title,52,b=True)
 if sub:text(48,111,sub,38,c=GRAY)
def save(name,purpose,kind='original_explanation',evidence='simulate.py small_examples'):
 im.save(A/(name+'.png'));meta.append(dict(file='assets/'+name+'.png',purpose=purpose,kind=kind,evidence=evidence,
 width=W,height=im.height,minimum_font_px=smallest,effective_minimum_at_354px=smallest/3))
def dye_image(a,size):
 # Fixed linear mapping 0..1, no framewise normalization; array row y points upward.
 c=np.stack([15+220*a,25+185*a,40+70*a],axis=-1).clip(0,255).astype('uint8')
 return Image.fromarray(c[::-1]).resize(size,Image.Resampling.NEAREST)
def colorbar(x,y,w=400):
 a=np.tile(np.linspace(0,1,w),(28,1));im.paste(dye_image(a,(w,28)),(x,y));text(x,y+35,'0',38);text(x+w,y+35,'1',38,anchor='rt')
def field(a,x,y,size=450):im.paste(dye_image(a,(size,size)),(x,y))

new('一条染料带，怎样卷成涡？',1340,'同一次二维计算；四幅使用同一亮度标尺')
for k,x,y,label in [(0,48,230,'第 0 步'),(1,562,230,'第 10 步'),(2,48,780,'第 20 步'),(4,562,780,'第 40 步')]:
 text(x,y-59,label,44,b=True);field(F[k,2],x,y)
text(48,1282,'暗 = 少量染料；亮 = 较多染料',40)
save('01-computed-sequence','先看同一染料的四次实际计算状态，建立动画对象','actual_simulation','frames.npz frames 0,1,2,4; n64 dt.04')

new('颜色与箭头，是两份不同的数据',870,'同一时刻：第 20 步；下方看各自的职责')
field(F[2,2],48,205)
box(562,205,450,450,'#edf1ed')
u,v=F[2,:2];n=len(u)
for j in range(4,n,8):
 for i in range(4,n,8):
  xx=562+(i+.5)/n*450;yy=655-(j+.5)/n*450
  ux=(u[j,i]+u[j,(i+1)%n])/2;vy=(v[j,i]+v[(j+1)%n,i])/2
  dot(xx,yy,'#b1bdbb',3);arrow(xx,yy,xx+ux*230,yy-vy*230,TEAL,4,10)
text(48,682,'染料：这里有多少？',41,b=True)
text(562,682,'速度：往哪儿走？',41,b=True)
text(48,775,'箭头越长，速度越快；位置一一对应',40)
save('03-dye-and-velocity','同一实际状态区分标量浓度与方向速度；中心箭头为边速度平均','actual_simulation','frames.npz frame 2, velocity averaged to centers and sparsely displayed')

new('先选“新位置”，再向后找',1050,'横向 x 向右，纵向 y 向上；长度单位自定')
ox=185;oy=800;sc=265
for i in range(3):
 line([(ox+i*sc,oy),(ox+i*sc,oy-2*sc)],'#d2d9d7',3);line([(ox,oy-i*sc),(ox+2*sc,oy-i*sc)],'#d2d9d7',3)
 text(ox+i*sc,oy+19,i,41,anchor='mt');text(ox-30,oy-i*sc,i,41,anchor='rm')
arrow(ox,oy,ox+660,oy,INK,4);arrow(ox,oy,ox,oy-600,INK,4);text(890,810,'x',45);text(158,165,'y',45)
x=ox+2*sc;y=oy-2*sc;bx=ox+.5*sc;by=oy-.75*sc
dot(x,y,RED,14);dot(bx,by,TEAL,14);arrow(x-17,y+14,bx+18,by-15,TEAL,9)
text(x-15,y-72,'新位置 (2, 2)',43,c=RED,anchor='rt')
text(bx+25,by+24,'旧位置 (0.5, 0.75)',42,c=TEAL)
text(48,906,'退回横向 1.5，退回纵向 1.25',44,b=True)
text(48,980,'因为速度 × 时间步 = 这一步的位移',40)
save('04-backtrace','一条坐标路径走通x−uΔt，目标固定而去旧场取值')

new('落在四个样本之间，就分两次估',1150,'四个角是旧时刻的染料读数，不是坐标')
x0=190;x1=850;yt=250;yb=690;xx=520;yy=yb-.75*(yb-yt)
box(x0,yt,x1-x0,yb-yt,'#e5eeea',TEAL,0)
for x,y,val in [(x0,yb,0),(x1,yb,4),(x0,yt,8),(x1,yt,12)]:
 dot(x,y,TEAL,13);text(x+(30 if x==x0 else -30),y+(25 if y==yt else -75),val,62,b=True,anchor='lt' if x==x0 else 'rt')
line([(xx,yb),(xx,yt)],'#789c9a',5);dot(xx,yb,BLUE);dot(xx,yt,BLUE);dot(xx,yy,RED,15)
text(xx+24,yt+7,'10',47,c=BLUE,b=True);text(xx+24,yb-57,'2',47,c=BLUE,b=True)
text(xx+25,yy+12,'要估的读数',41,c=RED)
text(x0,755,'横向走到一半：',44,b=True)
text(x0,819,'下边 0 与 4 → 2',42);text(x0,879,'上边 8 与 12 → 10',42)
text(48,972,'再从 2 向 10 走四分之三：',43,b=True)
text(48,1032,'2 × 0.25 + 10 × 0.75 = 8',48,c=RED,b=True)
save('05-bilinear-two-stages','同一回溯点先横后纵完成一次可手算双线性插值')

new('“混合旧值”，为何不产生新峰值？',830,'本例四角权重：都不小于 0，加起来等于 1')
xs=[48,169,290,652,1014];colors=['#bcdbdd','#9bc6ca','#6faaa9','#267777']
for i in range(4):
 box(xs[i],210,xs[i+1]-xs[i]-2,170,colors[i],None,0)
 text((xs[i]+xs[i+1])/2,270,['1/8','1/8','3/8','3/8'][i],38,c='white' if i>1 else INK,anchor='mt')
for y,s in [(442,'0 × 1/8 + 4 × 1/8'),(509,'+ 8 × 3/8 + 12 × 3/8 = 8')]:text(55,y,s,47,b=True)
line([(80,685),(950,685)],INK,5);dot(80,685,TEAL);dot(950,685,TEAL);dot(80+870*8/12,685,RED,15)
text(80,720,'最小 0',39,anchor='mt');text(80+870*8/12,720,'得到 8',39,c=RED,anchor='mt');text(950,720,'最大 12',39,anchor='mt')
save('06-convex-weights','把有界性的理由变成具体权重与数轴，不冒称完整流体无条件准确')

new('同一条染料带，更新规则不同',1160,'一格宽 1；每步向右移动 1.5 格；首尾相接')
E=R['small']['cfl']['explicit'];S=R['small']['cfl']['semi_lagrangian']
def bars(vals,y,title):
 text(48,y,title,42,b=True);x0=78;yb=y+195;cw=72;scale=60
 line([(x0,yb),(x0+12*cw,yb)],GRAY,3)
 for i,a in enumerate(vals):
  xx=x0+i*cw;col=RED if a<0 or a>1 else TEAL
  d.rectangle((xx,min(yb,yb-a*scale),xx+cw-7,max(yb,yb-a*scale)+1),fill=col)
  if abs(a)>1e-12:text(xx+cw/2,yb-a*scale+(-48 if a>=0 else 5),f'{a:g}',37,c=col,anchor='mt')
 text(950,yb,'0',37,anchor='lt')
bars(E[0],183,'共同初态：3 格有染料，读数都是 1')
bars(E[1],468,'显式上风一步：产生 −0.5 和 1.5')
bars(S[1],826,'回溯插值一步：仍在 0 到 1 之间')
save('07-explicit-vs-backtrace','具体C=1.5反例说明所选显式上风更新的负权重，不泛化所有显式法')

new('物理扩散：两格一起解“新值”',1040,'独立小模型：封闭两格，初值 0 和 12')
for x,val,c in [(85,0,'#e1ede8'),(555,12,'#448e8e')]:
 box(x,203,420,165,c);text(x+210,239,val,74,c=INK if val==0 else 'white',b=True,anchor='mt')
arrow(770,409,295,409,TEAL,7,22)
text(531,438,'净交换：从右边高值到左边低值',38,c=TEAL,anchor='mt')
text(48,534,'新左 = 0 + (新右 − 新左)',43)
text(48,598,'新右 = 12 + (新左 − 新右)',43)
text(48,693,'相加：新左 + 新右 = 12',43,b=True)
for x,val in [(85,4),(555,8)]:
 box(x,820,420,160,'#b8d9cf' if val==4 else '#76b4a7');text(x+210,851,val,76,b=True,anchor='mt')
save('08-implicit-diffusion','先解释隐式用未知新值同时求解，和单纯运输数值糊化区分')

new('空气不能在固定格子里凭空积多',840,'同一格：左边流入 3，右边流出 1')
box(338,236,370,350,'#d8e7e2',TEAL)
arrow(80,410,320,410,BLUE,24,38);arrow(720,410,930,410,RED,10,25)
text(190,295,'流入 3',44,c=BLUE,anchor='mt');text(830,295,'流出 1',44,c=RED,anchor='mt')
text(525,348,'每单位时间',42,anchor='mt');text(525,418,'多留下 2',50,b=True,anchor='mt')
text(48,677,'定容、定密度时，这样不能持续。',44,b=True)
text(48,745,'要一起调整邻格共享的边界流动。',42)
save('09-volume-balance','用固定容积的具体失衡引出不可压缩约束而非只给div符号')

def fourgrid(title,sub,flows,pots=None,h=1060):
 new(title,h,sub);cx=[285,775];cy=[355,795]
 for k,name in enumerate('ABCD'):
  x=cx[k%2];y=cy[k//2];box(x-190,y-160,380,320,'#e1ece6',TEAL)
  text(x,y-126,name,57,b=True,anchor='mt')
  if pots is not None:text(x,y+28,'q = '+str(pots[k]),47,c=BLUE,anchor='mt')
 # positive arrows right/down; signed labels stand beside arrows
 for val,x1,y1,x2,y2,lx,ly in [(flows[0],500,355,560,355,530,278),(flows[1],500,795,560,795,530,718),(flows[2],285,535,285,595,365,557),(flows[3],775,535,775,595,855,557)]:
  if val>=0:arrow(x1,y1,x2,y2,RED,7,17)
  else:arrow(x2,y2,x1,y1,TEAL,7,17)
  text(lx,ly,abs(val),43,c=RED if val>=0 else TEAL,anchor='mt')
 return cx,cy
fourgrid('四条共享边，必须同时照顾四格','外墙不漏；箭头数 = 每单位时间的流量',[3,1,0,0])
text(48,979,'初始：上边向右 3，下边向右 1',43)
save('10-four-cells-before','把约束耦合具体化；四格外墙封闭，与主实验周期边界明确区分')

fourgrid('给四格四个数，只用相邻差值','四个数来自同一组出入平衡关系',[3,1,0,0],[0,2.5,.5,2],1110)
text(48,973,'上边差值：2.5 − 0 = 2.5',43,b=True)
text(48,1040,'原来 3，减去 2.5，剩下 0.5',42,c=RED)
save('11-four-cell-potentials','一次代入说明压力样校正势如何改变共享边；不是把q当真实Pa')

fourgrid('校正后：流动仍在，挤压消失','每格一条流入 0.5，一条流出 0.5',[.5,-.5,-.5,.5],None,1110)
text(48,970,'顺时针环流保留下来。',46,b=True)
text(48,1040,'每格净流出 = 0，不等于速度 = 0。',40)
save('12-four-cells-after','直接沿闭环复核四格守恒，避免把投影解释成停止流动')

new('真实计算中：数存在什么地方？',1050,'MAC 网格局部；示意仅展示 2×2 个格子')
x0=225;y0=230;sz=310
for i in range(3):
 line([(x0+i*sz,y0),(x0+i*sz,y0+2*sz)],GRAY,4);line([(x0,y0+i*sz),(x0+2*sz,y0+i*sz)],GRAY,4)
for j in range(2):
 for i in range(2):
  dot(x0+(i+.5)*sz,y0+(j+.5)*sz,GOLD,22)
for j in range(2):
 for i in range(3):
  x=x0+i*sz;y=y0+(j+.5)*sz;arrow(x-38,y,x+38,y,BLUE,9,18)
for j in range(3):
 for i in range(2):
  x=x0+(i+.5)*sz;y=y0+j*sz;arrow(x,y+38,x,y-38,RED,9,18)
text(48,904,'金点：染料与 q；蓝箭：横向速度',40)
text(48,970,'红箭：纵向速度；每条边只存一份',40)
save('13-mac-storage','明确现代原创教学实现的交错采样位置及共享数据','original_implementation_diagram','simulate.py sample/divergence/gradient')

new('运输速度之后，做一次整体校正',1150,'本次第 1 步；两幅共用同一净流出颜色范围')
before=Z['div_before'];after=Z['div_after'];mx=float(abs(before).max())
def heat(a):
 t=np.clip(a/mx,-1,1);col=np.ones((*a.shape,3))*245
 for k,c in enumerate([190,80,55]):col[:,:,k]=np.where(t>0,245+(c-245)*t,col[:,:,k])
 for k,c in enumerate([38,111,165]):col[:,:,k]=np.where(t<0,245+(c-245)*(-t),col[:,:,k])
 return Image.fromarray(col[::-1].astype('uint8')).resize((450,450),Image.Resampling.NEAREST)
for x,key,title in [(48,'before','校正前'),(562,'after','校正后')]:
 text(x,181,title,45,b=True);im.paste(heat(Z['div_'+key]),(x,246))
 u=Z['u_'+key];v=Z['v_'+key];n=len(u)
 for j in range(4,n,8):
  for i in range(4,n,8):
   xx=x+(i+.5)/n*450;yy=696-(j+.5)/n*450
   ux=(u[j,i]+u[j,(i+1)%n])/2;vy=(v[j,i]+v[(j+1)%n,i])/2
   arrow(xx,yy,xx+ux*200,yy-vy*200,INK,3,9)
text(48,756,'红：净流出；蓝：净流入；白：接近 0',39)
text(48,831,'箭头仍在转，红蓝失衡已经消失。',43,b=True)
text(48,941,'净流出均方根：0.1423',43)
text(48,1006,'校正后约 0.0000000000000012',40)
text(48,1071,'数值近零受浮点舍入影响，不写成严格 0',36,c=GRAY)
save('14-projection-measured','实际第一步相同尺度热图及箭头证明投影去散度不抹平所有流动','actual_simulation','frames.npz div_before/div_after/u_before etc; results.json first_step')

new('一帧不是只把染料搬一次',1210,'本次程序实际步骤；主实验关闭力、黏性和扩散')
steps=[('速度被外力推动','本次：无持续外力'),('速度因黏性平滑','本次：黏性设为 0'),('第一次投影','统一满足各格出入平衡'),('速度搬运速度，再投影','回溯采样后重新校正'),('新速度搬运染料','回溯 + 双线性插值')]
for k,(a,b) in enumerate(steps):
 y=180+k*201;box(64,y,934,154,'#dfebe4' if k>=2 else '#ecebe3')
 text(90,y+12,str(k+1),52,b=True,c=TEAL);text(172,y+15,a,43,b=True);text(172,y+80,b,38,c=GRAY)
 if k<4:arrow(530,y+160,530,y+192,TEAL,5,13)
save('15-one-step','对应实际程序的速度与染料时序，解释两次投影而非抽象列术语','original_implementation_diagram','simulate.py run')

new('没有物理扩散，也会越来越糊',1060,'同一运行：黏性 = 0，染料扩散系数 = 0')
for k,x,lab in [(0,48,'第 0 步'),(12,562,'第 120 步')]:
 text(x,180,lab,43,b=True);field(F[k,2],x,250)
text(48,764,'峰值：0.9904 → 0.3443',46,b=True)
text(48,840,'染料读数总和：167.507 → 149.093',41)
text(48,922,'两幅颜色范围相同，没有逐帧自动提亮。',39)
text(48,982,'糊化与总量变化是数值方法的代价。',41,c=RED)
save('16-dissipation-measured','实际闭环结果区别物理扩散与插值耗散，并实证染料总和非严格守恒','actual_simulation','results.json stats0/stats120; frames0/12')

new('步子更小，未必让这张图更锐利',1240,'只换成恒速的一维平移；总共移动 16 格')
T=R['small']['translation'];x0=95;ww=850
for k,(key,lab) in enumerate([('1.0','16 次：每次 1 格'),('0.5','32 次：每次 0.5 格'),('0.25','64 次：每次 0.25 格')]):
 y=245+k*300;text(48,y-55,lab,42,b=True);line([(x0,y+155),(x0+ww,y+155)],GRAY,3)
 pts=[(x0+i/(63)*ww,y+155-140*a)for i,a in enumerate(T['variants'][key]['values'])]
 exact=[(x0+i/63*ww,y+155-140*a)for i,a in enumerate(T['exact'])]
 line(exact,'#b7bfbb',6);line(pts,TEAL,6)
 text(x0-22,y+155,'0',36,anchor='rm');text(x0-22,y+15,'1',36,anchor='rm')
text(48,1140,'灰线：精确平移；绿线：反复线性插值',40)
save('17-repeated-interpolation','同终点平移可重算反例，防止把减小dt当作消除一切糊化的万能结论')

# Independent cover: actual field crop plus concise title, never a historical/game photo.
new('让一团烟',1062);text(48,103,'跟着空气卷起来',59,b=True)
im.paste(dye_image(F[2,2],(960,960)).crop((0,155,960,805)),(50,310));text(48,219,'Stable Fluids 的回溯与校正',43,c=TEAL)
im.save(P/'cover.png')
meta.append(dict(file='cover.png',purpose='独立封面：实际原创计算的第20步，不是NASA照片或历史截图',kind='actual_simulation_cover',width=W,height=1062,minimum_font_px=43,effective_minimum_at_354px=43/3))
(P/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('Rendered',len(meta),'original images; NASA photograph handled separately')
