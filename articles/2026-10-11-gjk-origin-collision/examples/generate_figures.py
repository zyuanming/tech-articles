"""Original GJK teaching diagrams. All coordinates are the article's synthetic examples."""
from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parents[1]/'assets';FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
BG='#f6f3eb';INK='#172f3b';BLUE='#247b9b';RED='#c45437';GREEN='#478b65';GOLD='#dcb44a';GRAY='#7c8b8d'
def ft(n=42,bold=False):return ImageFont.truetype(BOLD if bold else FONT,n)
def canvas(title,h=840):
 im=Image.new('RGB',(1200,h),BG);d=ImageDraw.Draw(im);d.text((45,28),title,font=ft(47,True),fill=INK);d.line((45,108,1155,108),fill='#cad2cc',width=3);d.text((45,h-43),'原创几何示意 · 自设坐标 · 非引擎实测',font=ft(25),fill=GRAY);return im,d

def text(d,p,t,n=39,c=INK,anchor=None):d.text(p,t,font=ft(n),fill=c,anchor=anchor)
def arrow(d,a,b,c=RED,w=6):
 d.line((a,b),fill=c,width=w);an=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-19*math.cos(an-.5),b[1]-19*math.sin(an-.5)),(b[0]-19*math.cos(an+.5),b[1]-19*math.sin(an+.5))],fill=c)
def chart(d,lim=(-4,4,-4,4),box=(95,170,785,730)):
 x0,y0,x1,y1=box;lx,hx,ly,hy=lim
 scale=min((x1-x0)/(hx-lx),(y1-y0)/(hy-ly));cx=(x0+x1)/2;cy=(y0+y1)/2
 x0=cx-(hx-lx)*scale/2;x1=cx+(hx-lx)*scale/2;y0=cy-(hy-ly)*scale/2;y1=cy+(hy-ly)*scale/2
 def P(p):return (x0+(p[0]-lx)/(hx-lx)*(x1-x0),y1-(p[1]-ly)/(hy-ly)*(y1-y0))
 for x in range(math.ceil(lx),math.floor(hx)+1):
  a=P((x,ly));b=P((x,hy));d.line((a,b),fill='#d8ded8',width=2)
  if x!=0:text(d,(a[0],y1+12),str(x),28,GRAY,'mt')
 for y in range(math.ceil(ly),math.floor(hy)+1):
  a=P((lx,y));b=P((hx,y));d.line((a,b),fill='#d8ded8',width=2)
  if y!=0:text(d,(x0-15,a[1]),str(y),28,GRAY,'rm')
 if ly<=0<=hy:d.line((P((lx,0)),P((hx,0))),fill=GRAY,width=4)
 if lx<=0<=hx:d.line((P((0,ly)),P((0,hy))),fill=GRAY,width=4)
 return P

def poly(d,P,ps,c,fill=None,w=6):
 if fill:d.polygon([P(x) for x in ps],fill=fill)
 d.line([P(x) for x in ps+[ps[0]]],fill=c,width=w)
def point(d,P,p,c=RED,label=None,offset=(10,-45)):
 x,y=P(p);d.ellipse((x-9,y-9,x+9,y+9),fill=c)
 if label:text(d,(x+offset[0],y+offset[1]),label,35,c)
def save(im,n):im.save(OUT/n)
A=[(1,1),(3,1),(3,3),(1,3)];B=[(2,0),(4,2),(2,4)]
def hull(pts):
 pts=sorted(set(tuple(x) for x in pts))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for p in pts:
  while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 for p in reversed(pts):
  while len(hi)>=2 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
  hi.append(p)
 return lo[:-1]+hi[:-1]
D=hull([(x-u,y-v) for x,y in A for u,v in B]);W=[(1,1),(-3,-1),(1,-3)]
# 01
im,d=canvas('两个形状碰没碰：先固定住这一瞬间');P=chart(d,(-1,5,-1,5),box=(120,170,830,720));poly(d,P,A,BLUE,'#b8d6df');poly(d,P,B,RED,None);text(d,(885,260),'方块 A',45,BLUE);text(d,(885,355),'三角 B',45,RED);text(d,(870,505),'有共同点？',40);save(im,'01-two-shapes.png')
# 02
im,d=canvas('两个点做减法：记录一支相对位移');P=chart(d,(-1,5,-1,4),box=(110,180,820,700));poly(d,P,A,BLUE);poly(d,P,B,RED);arrow(d,P((2,0)),P((3,1)),GREEN);point(d,P,(3,1),BLUE,'a=(3,1)');point(d,P,(2,0),RED,'b=(2,0)',(15,10));text(d,(865,320),'a − b',44,GREEN);text(d,(865,400),'＝(1,1)',44,GREEN);save(im,'02-point-difference.png')
# 03
im,d=canvas('把所有顶点差列出来，围成一个新形状');P=chart(d);poly(d,P,D,GREEN,'#dbe9d4')
for a in A:
 for b in B:point(d,P,(a[0]-b[0],a[1]-b[1]),BLUE)
point(d,P,(0,0),RED,'原点 O');text(d,(855,230),'4×3＝12',43);text(d,(855,305),'次顶点配对',40);text(d,(855,450),'取这些点',40);text(d,(855,510),'的凸包',40);save(im,'03-difference-hull.png')
# 04
im,d=canvas('共同点减自己，恰好得到原点');P=chart(d,(-1,5,-1,5),box=(90,180,760,730));poly(d,P,A,BLUE,'#c2dce3');poly(d,P,B,RED);point(d,P,(2.5,1),GREEN,'q=(2.5,1)',(10,-65));text(d,(820,295),'q 在 A 中',41,BLUE);text(d,(820,370),'q 也在 B 中',41,RED);text(d,(820,480),'q − q＝(0,0)',39,GREEN);save(im,'04-common-origin.png')
# 05
im,d=canvas('把碰撞问题，换成“原点在里面吗”');P=chart(d);poly(d,P,D,GREEN,'#dbe9d4');point(d,P,(0,0),RED,'O');text(d,(840,255),'A 与 B 相交',41);arrow(d,(960,340),(960,425),GREEN);arrow(d,(1010,425),(1010,340),GREEN);text(d,(840,435),'A−B 含原点',41);save(im,'05-origin-test.png')
# 06
im,d=canvas('支持点：沿一个方向走得最远的点');P=chart(d,(-1,5,-1,5));poly(d,P,A,BLUE,'#c2dce3');arrow(d,P((0,0)),P((1.2,1.2)),RED);point(d,P,(3,3),GREEN,'(3,3)',(-110,-60));text(d,(845,230),'d＝(1,1)',41);text(d,(845,330),'x＋y 最大',41);text(d,(845,440),'3＋3＝6',41,GREEN);save(im,'06-support-dot.png')
# 07
im,d=canvas('差形状的最右点：A最右，减B最左');P=chart(d,(-1,5,-1,5));poly(d,P,A,BLUE);poly(d,P,B,RED);point(d,P,(3,1),BLUE,'a=(3,1)',(-120,10));point(d,P,(2,0),RED,'b=(2,0)',(-125,20));arrow(d,P((3,4)),P((4.5,4)),GREEN);text(d,(835,250),'d＝(1,0)',40);text(d,(835,370),'a − b＝(1,1)',37);text(d,(835,510),'不用造出',40);text(d,(835,570),'整个 A−B',40);save(im,'07-support-difference.png')
# 08
im,d=canvas('点、线段、三角形：只保存一小把证据');
for x in [170,480,900]:d.ellipse((x-10,430-10,x+10,430+10),fill=BLUE)
d.line((480,430,650,280),fill=BLUE,width=7);d.ellipse((640,270,660,290),fill=BLUE);d.polygon([(860,450),(1060,450),(960,240)],fill='#dbe9d4',outline=GREEN,width=6)
text(d,(125,555),'1个点',43);text(d,(460,555),'2点线段',43);text(d,(850,555),'3点三角形',43);save(im,'08-simplex.png')
# 09–11 fixed axes and exact same example
for n,title,points in [('09-first','第一次查询：先拿到 w1=(1,1)',W[:1]),('10-second','第二次查询：加入 w2=(−3,−1)',W[:2]),('12-third','第三次查询：加入 w3=(1,−3)',W)]:
 im,d=canvas(title);P=chart(d);poly(d,P,D,'#a9b9a9')
 if len(points)==2:d.line([P(p) for p in points],fill=BLUE,width=7)
 if len(points)==3:poly(d,P,points,BLUE,'#d2e4ea')
 for i,p in enumerate(points):point(d,P,p,BLUE,'w'+str(i+1),(8,-55))
 point(d,P,(0,0),RED,'O',(12,6))
 if len(points)==1:arrow(d,P(points[0]),P((0,0)),RED);text(d,(840,290),'下一步：',42);text(d,(840,365),'朝原点找',42)
 if len(points)==2:text(d,(840,265),'还没包住 O',42);text(d,(840,360),'先找线段上',39);text(d,(840,420),'离 O 最近点',39)
 if len(points)==3:text(d,(840,300),'三角形内',45,GREEN);text(d,(840,375),'包含原点',45,GREEN)
 save(im,n+'.png')
# 11 local closest direction, zoom preserves numerical positions
im,d=canvas('线段的最近点，告诉我们下一步朝哪找');P=chart(d,(-1.2,1.2,-.6,1),box=(110,200,790,700));d.line((P((-1.2,-.1)),P((1,1))),fill=BLUE,width=6);point(d,P,(-.2,.4),GREEN,'q=(−0.2,0.4)',(-210,-70));point(d,P,(0,0),RED,'O',(15,8));arrow(d,P((-.2,.4)),P((0,0)),RED);text(d,(830,235),'放大局部',38,GRAY);text(d,(830,365),'d＝−q',44);text(d,(830,450),'＝(0.2,−0.4)',38);save(im,'11-closest-direction.png')
# 13 barycentric
im,d=canvas('三个正权重，把原点夹在里面');P=chart(d);poly(d,P,W,BLUE,'#d2e4ea');
for w,label,off in zip(W,['w1：5/8','w2：1/4','w3：1/8'],[(10,-58),(5,-60),(12,10)]):point(d,P,w,BLUE,label,off)
point(d,P,(0,0),RED,'O',(15,10));text(d,(845,275),'权重都 ≥ 0',39);text(d,(845,365),'相加等于 1',39);text(d,(845,485),'加权结果',39);text(d,(845,545),'恰为 (0,0)',39);save(im,'13-barycentric.png')
# 14 recover witness
im,d=canvas('同一组权重，也能找回原形状上的点');P=chart(d,(-1,5,-1,5));poly(d,P,A,BLUE,'#c2dce3');poly(d,P,B,RED);point(d,P,(2.5,1),GREEN,'共同点',(0,-62));text(d,(850,240),'A侧加权',40,BLUE);text(d,(850,310),'＝(2.5,1)',40);text(d,(850,430),'B侧加权',40,RED);text(d,(850,500),'＝(2.5,1)',40);save(im,'14-witness-points.png')
# 15 separation
im,d=canvas('连最右边都在原点左侧，就可以停了');P=chart(d,(-10,2,-4,4),box=(105,190,920,730));shift=[(x-5,y) for x,y in D];poly(d,P,shift,BLUE,'#c2dce3');point(d,P,(0,0),RED,'O');d.line((P((-4,-4)),P((-4,4))),fill=GREEN,width=6);arrow(d,P((-2,2)),P((1,2)),RED);text(d,(465,135),'所有 x ≤ −4 < 0',40,GREEN);save(im,'15-separating-plane.png')
# 16 distance
im,d=canvas('距离版本，还要知道最近有多近');P=chart(d,(-1,10,-1,5),box=(90,180,1140,700));bb=[(x+5,y) for x,y in B];poly(d,P,A,BLUE,'#c2dce3');poly(d,P,bb,RED);d.line((P((3,2)),P((7,2))),fill=GREEN,width=8);point(d,P,(3,2),GREEN);point(d,P,(7,2),GREEN);text(d,P((5,2.8)),'距离＝4',44,GREEN,'mm');save(im,'16-distance.png')
# 17 concavity
im,d=canvas('凹洞会被凸包填平：这不是碰撞算法的承诺');P=chart(d,(-1,6,-1,6));u=[(0,0),(5,0),(5,5),(4,5),(4,1),(1,1),(1,5),(0,5)];poly(d,P,u,BLUE,'#c2dce3');q=P((2.5,3));d.ellipse((q[0]-35,q[1]-35,q[0]+35,q[1]+35),fill=RED);d.line((P((0,5)),P((5,5))),fill=GOLD,width=8);text(d,(830,290),'小球在凹洞里',38);text(d,(830,395),'外侧支持点',38);text(d,(830,455),'看不见这个洞',38);save(im,'17-concave-hull.png')
# 18 degeneracy
im,d=canvas('碰到边界：数学的零，计算机的难题');
for x,gap,lbl in [(90,0,'恰好接触'),(655,12,'极小间隙（放大示意）')]:
 d.rectangle((x,260,x+220,540),fill='#b8d6df',outline=BLUE,width=5);d.rectangle((x+220+gap,260,x+440+gap,540),outline=RED,width=6);text(d,(x,610),lbl,36)
text(d,(145,170),'容差、重复支持点、迭代上限，都要有明确定义',37);save(im,'18-degenerate.png')
print('Generated 18 original GJK figures; difference hull',D)
