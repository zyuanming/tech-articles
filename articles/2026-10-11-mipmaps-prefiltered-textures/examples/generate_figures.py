"""Original teaching figures; no third-party image is modified. Python 3, Pillow, NumPy."""
from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
OUT=Path(__file__).resolve().parents[1]/'assets'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
BG='#f6f3eb';INK='#172f3b';BLUE='#247b9b';RED='#c45437';GREEN='#478b65';GOLD='#dcb44a';GRAY='#7c8b8d'
def font(n=42,bold=False):return ImageFont.truetype(BOLD if bold else FONT,n)
def canvas(title,h=780):
 im=Image.new('RGB',(1200,h),BG);d=ImageDraw.Draw(im);d.text((55,36),title,font=font(49,True),fill=INK);d.line((55,113,1145,113),fill='#cbd3cb',width=3);d.text((55,h-48),'原创教学示意 · 自设数据',font=font(27),fill=GRAY);return im,d
def text(d,xy,t,size=42,color=INK,anchor=None):d.text(xy,t,font=font(size),fill=color,anchor=anchor)
def arr(d,a,b,color=RED,w=6):
 d.line((a,b),fill=color,width=w);ang=math.atan2(b[1]-a[1],b[0]-a[0]);q=[b,(b[0]-22*math.cos(ang-.5),b[1]-22*math.sin(ang-.5)),(b[0]-22*math.cos(ang+.5),b[1]-22*math.sin(ang+.5))];d.polygon(q,fill=color)
def grid(d,x,y,n,cell,values=None,labels=False):
 for j in range(n):
  for i in range(n):
   v=(i+j)%2 if values is None else values[j][i];c=int(40+195*v);d.rectangle((x+i*cell,y+j*cell,x+(i+1)*cell,y+(j+1)*cell),fill=(c,c,c),outline=BG,width=2)
   if labels:text(d,(x+(i+.5)*cell,y+(j+.5)*cell),f'{v:g}',34,'white' if v<.5 else INK,'mm')
def save(im,name):im.save(OUT/name)
def panel(im,d,ar,box,title):
 ar=np.clip(ar*255,0,255).astype('uint8');p=Image.fromarray(ar).convert('RGB');p=p.resize((box[2]-box[0],box[3]-box[1]),Image.Resampling.NEAREST);im.paste(p,box[:2]);text(d,((box[0]+box[2])/2,box[3]+24),title,38,anchor='mt')
# 01: Same procedural texture, actual computed sampling comparison.
N=512;yy,xx=np.mgrid[0:N,0:N];base=((xx//8+yy//8)%2)*.75+.12
pyr=[base]
while pyr[-1].shape[0]>1:
 a=pyr[-1];pyr.append((a[::2,::2]+a[1::2,::2]+a[::2,1::2]+a[1::2,1::2])/4)
h,w=360,300;Y,X=np.mgrid[0:h,0:w];z=1.7/(.10+Y/h);u=.5+(X/w-.5)*z*.48;v=z*.43
rho=np.maximum(np.hypot(*np.gradient(u*N)),np.hypot(*np.gradient(v*N)));lod=np.clip(np.log2(np.maximum(rho,1)),0,len(pyr)-1)
def bilinear(a,u,v):
 n=a.shape[0];x=u*n-.5;y=v*n-.5;ix=np.floor(x).astype(int);iy=np.floor(y).astype(int);fx=x-ix;fy=y-iy
 return ((1-fx)*(1-fy)*a[iy%n,ix%n]+fx*(1-fy)*a[iy%n,(ix+1)%n]+(1-fx)*fy*a[(iy+1)%n,ix%n]+fx*fy*a[(iy+1)%n,(ix+1)%n])
nearest=base[np.floor(v*N).astype(int)%N,np.floor(u*N).astype(int)%N];bi=bilinear(base,u,v);mi=np.zeros_like(u)
lo=np.floor(lod).astype(int);hi=np.minimum(lo+1,len(pyr)-1);frac=lod-lo
for k,a in enumerate(pyr):mi+=bilinear(a,u,v)*((lo==k)*(1-frac)+(hi==k)*frac)
im,d=canvas('同一块棋盘：细节太密，会变出假花纹',820)
for a,b,t in [(nearest,(50,160,390,650),'只取一个点'),(bi,(430,160,770,650),'只做双线性'),(mi,(810,160,1150,650),'Mipmap＋混层')]:panel(im,d,a,b,t)
save(im,'01-filter-comparison.png')
# 02
im,d=canvas('纹素和像素：两张网格，不是一回事')
grid(d,70,190,8,53);d.rectangle((200,296,359,455),outline=RED,width=9);arr(d,(520,370),(690,370));d.rectangle((760,290,990,520),fill='#81998c',outline=INK,width=5)
text(d,(70,650),'纹理中的 3×3 区域',40);text(d,(730,570),'屏幕上的 1 格',40);save(im,'02-texel-pixel.png')
# 03
im,d=canvas('隔两格取一个点，偏一点就变了')
for row,phase in enumerate([0,1]):
 y=185+row*245
 for i in range(12):d.rectangle((70+i*87,y,70+(i+1)*87,y+120),fill=INK if i%2==0 else '#ffffff',outline='#bcc6c4',width=2)
 for i in range(phase,12,2):d.ellipse((95+i*87,y+43,127+i*87,y+75),fill=RED)
 text(d,(70,y+144),'落在黑格 → 全黑' if phase==0 else '平移一格 → 全白',42)
save(im,'03-phase-alias.png')
# 04
im,d=canvas('一个大脚印，不能只听四个邻居的意见')
grid(d,65,180,10,48);d.rectangle((160,275,450,565),outline=RED,width=9);d.rectangle((255,370,354,469),outline=GOLD,width=10)
text(d,(630,260),'红框：这一像素',43,color=RED);text(d,(630,320),'真正覆盖的区域',43,color=RED);text(d,(630,440),'黄框：双线性',43,color='#9d7620');text(d,(630,500),'访问的四个纹素',43,color='#9d7620');save(im,'04-four-neighbors.png')
# 05
im,d=canvas('先求平均，再缩小：一块黑白变成灰')
grid(d,100,230,4,105);arr(d,(585,430),(740,430));grid(d,810,325,2,100,[[.5,.5],[.5,.5]])
text(d,(100,165),'4×4：每块都是 0 或 1',39);text(d,(790,570),'2×2：都是 0.5',39);save(im,'05-average.png')
# 06
im,d=canvas('不是每一小块都该变成同一种灰')
a=[[0,0,1,1],[0,1,1,1],[0,0,0,1],[1,0,0,1]];grid(d,80,230,4,105,a,True);arr(d,(550,440),(700,440));b=[[.25,1],[.25,.5]];grid(d,755,300,2,160,b,True);text(d,(755,660),'每格汇总左边 2×2',37);save(im,'06-hand-average.png')
# 07
im,d=canvas('每往上一层，长和宽都减半',840)
for x,y,n,cell,lbl in [(60,220,8,56,'8×8'),(540,220,4,56,'4×4'),(820,220,2,56,'2×2'),(1010,220,1,56,'1×1')]:
 vals=None if n==8 else np.full((n,n),.5);grid(d,x,y,n,cell,vals);text(d,(x,y+n*cell+28),lbl,42)
text(d,(530,555),'64＋16＋4＋1',50);text(d,(530,625),'＝85 个纹素',50);save(im,'07-pyramid.png')
# 08
im,d=canvas('额外成本不是再存一整张大图')
length=980;x=100;y=240
for val,col in [(64,BLUE),(16,GREEN),(4,GOLD),(1,RED)]:
 end=x+length*val/85;d.rectangle((x,y,end,y+140),fill=col);x=end
text(d,(100,440),'原图：64',48,color=BLUE);text(d,(100,525),'额外：16＋4＋1＝21',48,color=GREEN);text(d,(100,610),'这条小链：额外 21/64 ≈ 32.8%',43);save(im,'08-memory.png')
# 09
im,d=canvas('同样一格屏幕，倾斜后罩住更多纹理')
for x,wide,high,lbl in [(60,140,140,'近似正看'),(660,420,90,'斜着看')]:
 grid(d,x,230,8,56,np.full((8,8),.77));cx=x+224;cy=455;d.ellipse((cx-wide/2,cy-high/2,cx+wide/2,cy+high/2),outline=RED,width=9);text(d,(x,160),lbl,46)
save(im,'09-footprints.png')
# 10
im,d=canvas('ρ：一像素跨过多少个原始纹素？',830)
for j,(r,l) in enumerate([(1,0),(2,1),(4,2),(8,3)]):
 y=180+j*125;text(d,(80,y),f'ρ＝{r}',46);d.rectangle((340,y,340+90*r,y+55),fill=BLUE);text(d,(80,y+60),f'第 {l} 层',34,color=GREEN)
text(d,(340,690),'每翻一倍，就向上走一层',40);save(im,'10-level-choice.png')
# 11
im,d=canvas('缩小比例在变，选层不必突然跳')
text(d,(140,130),'层级 ↑',34);d.line((120,570,1090,570),fill=INK,width=4);d.line((120,570,120,180),fill=INK,width=4)
for i in range(4):
 x=160+i*230;y=520-i*90;d.line((x,y,x+210,y),fill=RED,width=10)
 if i<3:d.line((x+210,y,x+210,y-90),fill=RED,width=4)
d.line((160,520,1080,160),fill=BLUE,width=8);text(d,(165,630),'连续缩小 →',44);text(d,(450,210),'整层切换',42,color=RED);text(d,(640,360),'相邻层混合',42,color=BLUE);save(im,'11-level-transition.png')
# 12
im,d=canvas('λ＝2.25：两层各说多少话？')
d.rectangle((80,220,370,500),fill='#666666');d.rectangle((830,220,1120,500),fill='#999999');d.rectangle((470,320,730,570),fill='#737373');arr(d,(370,390),(458,425));arr(d,(820,390),(742,425));text(d,(95,550),'第2层：0.4',40);text(d,(815,550),'第3层：0.6',40);text(d,(80,165),'75%',45);text(d,(925,165),'25%',45);text(d,(295,665),'0.75×0.4＋0.25×0.6＝0.45',40);save(im,'12-trilinear.png')
# 13
im,d=canvas('长条脚印，为什么会被“方形平均”抹糊？')
grid(d,70,200,10,50,np.full((10,10),.85));d.ellipse((90,390,550,500),outline=RED,width=10);d.rectangle((90,215,550,675),outline=BLUE,width=7)
text(d,(640,235),'红：真正要汇总的',42,color=RED);text(d,(640,295),'狭长区域',42,color=RED);text(d,(640,420),'蓝：按长边选层',42,color=BLUE);text(d,(640,480),'连短边也抹宽了',42,color=BLUE);save(im,'13-anisotropic-footprint.png')
# 14
im,d=canvas('沿长方向多取几次，短方向少模糊')
grid(d,80,210,10,50,np.full((10,10),.85));d.ellipse((100,400,560,510),outline=RED,width=8)
for x in [150,240,330,420,510]:d.ellipse((x-46,410,x+46,502),outline=BLUE,width=5)
text(d,(665,310),'多次较窄的采样',44);text(d,(665,400),'覆盖一条长脚印',44);text(d,(665,530),'示意，不规定硬件',36,color=GRAY);text(d,(665,580),'必须这样布点',36,color=GRAY);save(im,'14-anisotropic-samples.png')
# 15
im,d=canvas('颜色数字不是光量：平均前先认清编码')
for x,c,label in [(90,0,'黑：0'),(430,255,'白：1'),(820,188,'平均光量')]:
 d.rectangle((x,220,x+270,490),fill=(c,c,c),outline=GRAY,width=3);text(d,(x,540),label,43)
text(d,(70,640),'在线性光里平均 0.5 → sRGB编码约 0.735',40);save(im,'15-linear-light.png')
# 16
im,d=canvas('颜色之外：透明度也有自己的问题')
for x,vals,lbl in [(100,[[1,0],[0,0]],'4格中有1格不透明'),(800,[[.25]],'平均后：0.25')]:
 n=len(vals);cell=300/n
 for j in range(n):
  for i in range(n):
   a=vals[j][i];col=(int(246*(1-a)+71*a),int(243*(1-a)+139*a),int(235*(1-a)+101*a));d.rectangle((x+i*cell,240+j*cell,x+(i+1)*cell,240+(j+1)*cell),fill=col,outline=GRAY,width=4)
 text(d,(x,585),lbl,38)
arr(d,(510,390),(720,390));text(d,(130,670),'若阈值是 0.5，小叶片会在这一层消失',41);save(im,'16-alpha-coverage.png')
# 17
im,d=canvas('图集的邻居，可能不是游戏里的邻居')
d.rectangle((100,240,560,570),fill=BLUE);d.rectangle((560,240,1020,570),fill=GOLD);d.rectangle((480,330,640,490),outline=RED,width=10);text(d,(100,620),'蓝色岛屿',46,color=BLUE);text(d,(760,620),'黄色沙漠',46,color='#957118');text(d,(230,160),'缩小滤波跨过图集边界 → 颜色串门',41);save(im,'17-atlas-bleeding.png')
# 18
im,d=canvas('同一个实验：把取样起点平移一下',880)
for row,phase in enumerate([0,1]):
 y=200+row*190
 for i in range(12):
  val=(2*i+phase)%2;d.rectangle((100+i*80,y,180+i*80,y+95),fill='white' if val else INK,outline=GRAY,width=2)
 text(d,(100,y+115),f'只取点，起点＝{phase}',38)
for i in range(12):d.rectangle((100+i*80,605,180+i*80,690),fill='#bcbcbc',outline=BG,width=2)
text(d,(100,145),'黑白交替条纹，每两格输出一次',40);text(d,(100,718),'先平均相邻两格：始终为 0.5',40);save(im,'18-experiment.png')
print('Generated 18 original figures')
