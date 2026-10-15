#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original explanatory diagrams and explicitly attributed CMU-data skeleton renders."""
from pathlib import Path
import argparse,json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
W=1062;BG='#f5f2e9';WHITE='#fffdfa';INK='#243e49';MUTED='#5c7074';BLUE='#267b9c';ORANGE='#bc762d';GREEN='#32816b';RED='#bd5348';GOLD='#b69c35';GRID='#d1dcd6';PALE='#e6ede6'
F=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n,index=2)
def text(d,xy,t,size=38,color=INK,b=False):d.text(xy,t,font=F(size,b),fill=color)
def center(d,xy,t,size=38,color=INK,b=False):d.text(xy,t,font=F(size,b),fill=color,anchor='mm')
def arrow(d,a,b,color=INK,width=6,head=16):
 d.line([a,b],fill=color,width=width);v=np.array(b,dtype=float)-a;n=np.linalg.norm(v)
 if n<1:return
 v/=n;p=np.array([-v[1],v[0]]);q=np.array(b);d.polygon([tuple(q),tuple(q-head*v+head*.5*p),tuple(q-head*v-head*.5*p)],fill=color)
def box(d,xy,color=WHITE,outline=None):d.rounded_rectangle(xy,radius=22,fill=color,outline=outline,width=3)
def cross(d,p,color=RED,r=12):
 x,y=p;d.line((x-r,y-r,x+r,y+r),fill=color,width=5);d.line((x-r,y+r,x+r,y-r),fill=color,width=5)
def dot(d,p,color=BLUE,r=10):x,y=p;d.ellipse((x-r,y-r,x+r,y+r),fill=color)
def canvas(title,subtitle,h=1250):
 im=Image.new('RGB',(W,h),BG);d=ImageDraw.Draw(im);text(d,(45,30),title,49,b=True);text(d,(45,105),subtitle,36,MUTED);return im,d
def footer(d,h,t):text(d,(45,h-72),t,36,MUTED)
def save(im,name,out):im.save(out/name,optimize=False)
cam=np.array([3.,2.3,5.]);target=np.array([0.,.8,0.]);vf=target-cam;vf/=np.linalg.norm(vf);vr=np.cross(vf,[0,1,0]);vr/=np.linalg.norm(vr);vu=np.cross(vr,vf)
def screen(p,cx,cy,s):return(cx+s*np.dot(p,vr),cy-s*np.dot(p,vu))
def pose(d,positions,cx,cy,s,D,color=None,width=10):
 p=np.array(positions);idx={n:i for i,n in enumerate(D['names'])};segs=[]
 for name,parent in D['parents'].items():
  if name.endswith(('fingers','thumb')):continue
  a=p[idx[parent]];b=p[idx[name]];segs.append((float(np.dot((a+b)/2,vf)),name,a,b))
 for dep,name,a,b in sorted(segs,reverse=True):
  left=name.startswith('l') and name not in ('lowerback','lowerneck');right=name.startswith('r') and name!='root'
  c=color or (ORANGE if left else BLUE if right else INK)
  u=screen(a,cx,cy,s);v=screen(b,cx,cy,s);d.line([u,v],fill=c,width=width);r=width*.55;dot(d,v,c,r)
 head=screen(p[idx['head']],cx,cy,s);dot(d,head,color or INK,s*.09)
def floor(d,cx,cy,s,extent=.8):
 for a in np.arange(-extent,extent+.001,.2):
  for b in [0,1]:
   p=[a,0,-extent]if b==0 else[-extent,0,a];q=[a,0,extent]if b==0 else[extent,0,a];d.line([screen(p,cx,cy,s),screen(q,cx,cy,s)],fill=GRID,width=2)
def plane(d,ox,oy,scale=300,xmax=.85,zmax=1.12,labels=True):
 arrow(d,(ox-scale*xmax,oy),(ox+scale*xmax,oy),MUTED,4,13);arrow(d,(ox,oy+35),(ox,oy-scale*zmax),MUTED,4,13)
 if labels:text(d,(ox+scale*xmax-50,oy+15),'右+',36,MUTED);text(d,(ox+12,oy-scale*zmax-12),'前+',36,MUTED)
 return lambda x,z:(ox+scale*x,oy-scale*z)
def main(art,out):
 out.mkdir(parents=True,exist_ok=True);D=json.loads((art/'examples/render-samples.json').read_text());R=json.loads((art/'examples/expected-results.json').read_text());toy=R['toy'];real=R['real'];current=D['comparison']['current'][0]['positions'];selected=D['comparison']['selected'][0]['positions']
 # 01 Real input pose, distinct manually drawn intention.
 im,d=canvas('这一帧，还迈着原来的步子','真实动捕骨架 + 另外添加的玩家意图',1320)
 floor(d,620,900,395);pose(d,current,620,900,395,D)
 text(d,(70,190),'16_15 · 第113帧',40,b=True)
 text(d,(70,260),'身体左侧',38,ORANGE);text(d,(70,315),'身体右侧',38,BLUE)
 a=screen([0,0,0],620,900,395);b=screen([-.7,0,.65],620,900,395);arrow(d,a,b,GREEN,14,30)
 box(d,(50,1030,1012,1210),PALE);text(d,(80,1050),'输入：接下来想往左前方走',43,GREEN,True);text(d,(80,1120),'问题：哪一帧能接住这个变化？',39)
 footer(d,1320,'CMU数据重绘；箭头不是原始采集标记。');save(im,'01-input-pose.png',out)
 #02 real keyframes plus sequence identity.
 im,d=canvas('选中一帧，也选中它的后续','同一真实左转片段；姿势分别移到展示格中央',1430)
 rows=D['whole_clips']['16_17'];chosen=[rows[0],next(r for r in rows if r['source_frame']==261),rows[-1]]
 for i,row in enumerate(chosen):
  p=np.array(row['positions']);p-=np.array([p[0,0],0,p[0,2]]);x=200+i*330
  pose(d,p,x,760,270,D);center(d,(x,850),f"第{row['source_frame']}帧",39,b=True)
 box(d,(45,960,1017,1310),WHITE);text(d,(75,985),'候选可以在片段中间',42,b=True)
 for i,label in enumerate(['…','k','k+1','k+2','…']):
  x=125+i*200;box(d,(x-60,1080,x+65,1185),PALE if i!=1 else '#d4e9dd');center(d,(x,1132),label,41)
  if i<4:arrow(d,(x+73,1132),(x+125,1132),MUTED,4)
 text(d,(75,1220),'取回第k帧 → 沿原时间顺序继续播放',39)
 footer(d,1430,'上方是CMU 16_17；下方k只是帧号示意。');save(im,'02-frames-and-continuation.png',out)
 #03 artificial local coordinates.
 im,d=canvas('把意图记成三个数','人工手算例；距离单位：米',1320)
 p=plane(d,600,790,460,xmax=.78,zmax=1.12);q=p(-.6,.8);arrow(d,p(0,0),q,GREEN,9,24);cross(d,q,GREEN,15)
 dot(d,p(0,.2),ORANGE,13);text(d,(630,675),'脚尖前方0.20',37,ORANGE);text(d,(70,330),'目标：左0.60 / 前0.80',38,GREEN)
 d.line([q,p(-.6,0)],fill=GREEN,width=3);d.line([q,p(0,.8)],fill=GREEN,width=3)
 text(d,(300,820),'−0.60',38,GREEN);text(d,(620,410),'0.80',38,GREEN);text(d,(480,900),'原点：脚下参考点',38)
 box(d,(45,1010,1017,1215),WHITE);text(d,(75,1030),'查询 =（0.20，−0.60，0.80）',44,b=True);text(d,(75,1110),'当前脚尖        期望未来地面位置',37)
 footer(d,1320,'脚尖位置与整个人未来位置，是两种量。');save(im,'03-local-coordinates.png',out)
 #04 Four candidates in independent panels.
 im,d=canvas('四帧，各写一张三项索引卡','人工数据；× 查询目标，● 候选的未来地面点',1600)
 for i,r in enumerate(toy['rows']):
  x=45+(i%2)*500;y=190+(i//2)*650;box(d,(x,y,x+472,y+615),WHITE);text(d,(x+25,y+18),r['id'],53,b=True)
  text(d,(x+100,y+24),f"脚尖 {r['features'][0]:.2f} 米",37,ORANGE)
  # Separate scalar ruler, not a body silhouette.
  yy=y+125;d.line((x+50,yy,x+420,yy),fill=GRID,width=4);center(d,(x+235,yy+38),'0',36,MUTED);dot(d,(x+235+r['features'][0]*650,yy),ORANGE,11)
  p=plane(d,x+245,y+500,225,xmax=.8,zmax=1.12);cross(d,p(-.6,.8),GREEN,12);dot(d,p(*r['features'][1:]),BLUE,12)
  text(d,(x+25,y+545),f"未来 ({r['features'][1]:.2f}, {r['features'][2]:.2f})",36)
 footer(d,1600,'每格用自己的起点和朝向；轴约定相同。');save(im,'04-four-candidates.png',out)
 #05 Normalization arithmetic.
 im,d=canvas('候选C：差值 → 除尺度 → 平方','三项都先用各自的尺子衡量',1370)
 lines=[('脚尖前后','(0.10 − 0.20) ÷ 0.25','−0.4 → 0.16',ORANGE),('未来左右','(−0.50 − (−0.60)) ÷ 1','0.1 → 0.01',BLUE),('未来前后','(0.85 − 0.80) ÷ 1','0.05 → 0.0025',GREEN)]
 for i,(label,formula,value,c) in enumerate(lines):
  y=190+i*290;box(d,(45,y,1017,y+255),WHITE);text(d,(75,y+18),label,42,c,True);text(d,(75,y+85),formula,43);text(d,(75,y+155),value,43,c,True)
 box(d,(45,1080,1017,1240),'#d4e9dd');center(d,(531,1160),'总分 0.16 + 0.01 + 0.0025 = 0.1725',40,b=True)
 footer(d,1370,'分数没有长度单位，也不是概率。');save(im,'05-scales-cost.png',out)
 #06 true lengths same scale.
 im,d=canvas('C不是单项冠军，却是总分最低','四帧同一把代价刻度；色块长度来自实际计算',1270)
 for j,(c,l) in enumerate([(ORANGE,'脚尖'),(BLUE,'未来左右'),(GREEN,'未来前后')]):dot(d,(75+j*325,205),c,12);text(d,(100+j*325,178),l,37)
 for i,r in enumerate(sorted(toy['rows'],key=lambda x:x['cost'])):
  y=330+i*175;text(d,(55,y),r['id'],50,b=True);x=150
  for term,c in zip(r['squared_terms'],[ORANGE,BLUE,GREEN]):
   w=term*270
   if w>0:d.rectangle((x,y+15,x+w,y+80),fill=c)
   x+=w
  text(d,(max(310,x+20),y+15),f"{r['cost']:.4f}".rstrip('0').rstrip('.'),42,b=True)
 for v in [0,1,2,3]:
  x=150+v*270;d.line((x,1060,x,1074),fill=MUTED,width=3);center(d,(x,1110),str(v),36,MUTED)
 d.line((150,1060,960,1060),fill=MUTED,width=3)
 footer(d,1270,'C的绿色项很短；精确数值见正文逐项算式。');save(im,'06-ranking.png',out)
 #07 conceptual pipeline.
 im,d=canvas('索引负责找，完整记录负责播放','结构示意；不是说三个数字可以生成全身',1330)
 panels=[('① 比较特征','脚尖 + 未来轨迹','选出片段身份与帧号',PALE),('② 用身份取回完整记录','根位置、各关节姿势等','不是只取回三项特征',WHITE),('③ 读取同一片段后续帧','k → k+1 → k+2 → …','后续动作保留原时间顺序','#d4e9dd')]
 for i,(a,b,c,col)in enumerate(panels):
  y=190+i*340;box(d,(70,y,992,y+270),col);text(d,(100,y+25),a,44,b=True);text(d,(100,y+105),b,40);text(d,(100,y+180),c,38,MUTED)
  if i<2:arrow(d,(531,y+280),(531,y+325),MUTED,6,17)
 footer(d,1330,'真实实验会取回完整骨架；手算表仅教检索。');save(im,'07-lookup-and-play.png',out)
 #08 world transform exact simple example coordinate rotations.
 im,d=canvas('搬到别处、转个方向，动作关系不变','人工坐标示意；绿色点相对自身仍是左0.5、前0.85',1350)
 text(d,(65,200),'橙箭头：自身前方',36,ORANGE);text(d,(550,200),'蓝箭头：自身右方',36,BLUE)
 for i,ang in enumerate([0,55]):
  ox=285+i*490;oy=620;theta=math.radians(ang)
  def world(x,z):return(ox+260*(x*math.cos(theta)-z*math.sin(theta)),oy-260*(x*math.sin(theta)+z*math.cos(theta)))
  arrow(d,world(0,0),world(.8,0),BLUE,5);arrow(d,world(0,0),world(0,1.15),ORANGE,5);dot(d,world(-.5,.85),GREEN,14);arrow(d,world(0,0),world(-.5,.85),GREEN,6)
  text(d,(ox-110,730),'自身原点',37);text(d,(ox-145,820),'局部值相同',40,GREEN,True)
 box(d,(45,950,1017,1210),WHITE);text(d,(75,975),'比较：先用各自的参考点与朝向',40,b=True);text(d,(75,1050),'播放：再把选中段映射到角色当前位置',38);text(d,(75,1120),'保留后续相对移动，不逐帧归零',38)
 footer(d,1350,'上图只是换坐标；不是任意姿势都保持特征。');save(im,'08-align-coordinates.png',out)
 #09 scalar transition calculated true axes.
 im,d=canvas('选帧之后，还要处理切换','另一组人工标量例；位置：米，时间：秒',1360)
 for i,(c,label)in enumerate([(MUTED,'旧动作延续'),(RED,'直接切换'),(GREEN,'短时补偿')]):dot(d,(70+i*330,207),c,12);text(d,(95+i*330,180),label,36)
 x0,y0=160,900;sx=1600;sy=2350
 xy=lambda t,p:(x0+(t+.1)*sx,y0-(p-.04)*sy)
 for p in [.05,.1,.15,.2,.25]:
  y=xy(0,p)[1];d.line((x0,y,960,y),fill=GRID,width=2);text(d,(45,y-25),f'{p:.2f}',36)
 for t in [-.1,0,.1,.2,.3,.4]:
  x=xy(t,0)[0];d.line((x,xy(0,.25)[1],x,y0),fill=GRID,width=2);center(d,(x,945),f'{t:.1f}',36)
 rows=R['scalar_transition']['rows']
 d.line([xy(r['time_s'],r['old_continuation_m'])for r in rows],fill=MUTED,width=4)
 before=[xy(r['time_s'],r['old_continuation_m'])for r in rows if r['time_s']<=0];after=[xy(r['time_s'],r['new_continuation_m'])for r in rows if r['time_s']>=0]
 d.line(before,fill=RED,width=7);d.line([xy(0,.2),xy(0,.1)],fill=RED,width=7);d.line(after,fill=RED,width=7)
 d.line([xy(r['time_s'],r['smooth_m'])for r in rows],fill=GREEN,width=7)
 text(d,(220,1005),'t=0 切换',37,RED);text(d,(610,1005),'t=0.2 补偿归零',37,GREEN)
 box(d,(45,1090,1017,1235),WHITE);text(d,(75,1105),'旧：0.20米，−0.30米/秒',38);text(d,(75,1165),'新：0.10米，−0.10米/秒',38)
 footer(d,1360,'只演示一个坐标；未用于后面的真实骨架动画。');save(im,'09-transition-curve.png',out)
 #10 precise weights + units separate cases.
 im,d=canvas('偏好可改，单位不能偷偷改偏好','人工四候选；下表只抽出B、C展示权重翻转',1470)
 box(d,(45,180,1017,650),WHITE);text(d,(75,200),'轨迹项乘权重 λ',44,b=True)
 for y,label,b,c in [(300,'λ = 1','B：2.56','C：0.1725 ✓'),(430,'λ = 200','B：2.56 ✓','C：2.66')]:text(d,(75,y),label,40);text(d,(385,y),b,40);text(d,(700,y),c,40,GREEN)
 text(d,(75,545),'λ=200只是放大现象的反例。',38,MUTED)
 box(d,(45,710,1017,1300),WHITE);text(d,(75,730),'把脚尖改用厘米时',43,b=True)
 text(d,(75,820),'C的脚尖差：−10厘米',40)
 text(d,(75,900),'错：还除以0.25 → 平方1600',40,RED)
 text(d,(75,980),'对：改除以25 → 平方0.16',40,GREEN)
 text(d,(75,1080),'单位错配：A误胜；尺度一起改：C仍胜。',37)
 text(d,(75,1170),'其余两项保持用米及原尺度。',37,MUTED)
 footer(d,1470,'λ乘的是平方后的代价，不是先乘特征向量。');save(im,'10-weights-and-units.png',out)
 #11 missing coverage.
 im,d=canvas('库里没有，就只能选“不太像的”','人工例：移除B、C，只留下A和D',1260)
 p=plane(d,531,830,450,xmax=.9,zmax=1.2);cross(d,p(-.6,.8),GREEN,16);text(d,(55,385),'想去这里',38,GREEN)
 for id,x,z,c in [('A',0,1,BLUE),('D',.6,.8,ORANGE)]:
  arrow(d,p(0,0),p(x,z),c,6);dot(d,p(x,z),c,14);text(d,(p(x,z)[0]+20,p(x,z)[1]-25),id,48,c,True)
 box(d,(45,960,1017,1140),WHITE);text(d,(75,980),'A：0.40 < D：1.44 → 选A',43,b=True);text(d,(75,1055),'它最近，但仍然在直走。',40)
 footer(d,1260,'基本检索不会凭空生成库里不存在的左转。');save(im,'11-missing-coverage.png',out)
 #12 True root trajectories, equal scale across panels based actual max values.
 im,d=canvas('真实小库：1399帧 → 1219个候选','CMU subject16；路径统一起点与初始朝向',1600)
 colors=[BLUE,GREEN,ORANGE];labels=['16_15 直行','16_17 左转','16_19 右转'];rootidx=D['names'].index('root')
 allpts=[np.array([r['positions'][rootidx]for r in D['whole_clips'][n]])[:,[0,2]]for n in ['16_15','16_17','16_19']]
 maxx=max(abs(p[:,0]).max()for p in allpts);maxz=max(p[:,1].max()for p in allpts);scale=min(125/maxx,510/maxz)
 for i,(n,label,c,pts)in enumerate(zip(['16_15','16_17','16_19'],labels,colors,allpts)):
  x=205+i*330;y=840;center(d,(x,220),label,36,c,True)
  arrow(d,(x-140,y),(x+140,y),MUTED,3,11);arrow(d,(x,y+20),(x,y-560),MUTED,3,11)
  q=[(x+a*scale,y-b*scale)for a,b in pts];d.line(q,fill=c,width=7);dot(d,q[0],INK,9);cross(d,q[-1],c,10)
  text(d,(x+105,y+15),'右',36,MUTED);text(d,(x+12,y-550),'前',36,MUTED)
  center(d,(x,910),f"{real['frame_counts'][n]} → {real['eligible_counts'][n]}",36)
 # Actual shared scale bar, not arbitrary trajectory axes.
 d.line((65,995,65+scale,995),fill=INK,width=6);text(d,(65,1020),'1米（三格同尺度）',36)
 box(d,(45,1110,1017,1435),WHITE);text(d,(75,1130),'120 Hz × 0.5秒 = 往后看60帧',42,b=True)
 text(d,(75,1210),'每段末尾60帧：未来窗口不完整',39)
 d.rectangle((100,1305,740,1350),fill=GREEN);d.rectangle((740,1305,960,1350),fill=RED)
 text(d,(100,1360),'可查候选',36,GREEN);text(d,(735,1360),'排除片尾',36,RED)
 footer(d,1600,'下方时间条仅示意分区；上方路径来自源数据。');save(im,'12-real-library.png',out)
 #13 Real measured query with numeric identity.
 im,d=canvas('真实查询：选到16_17第244帧','与前面人工四候选分开；当前是16_15第113帧',1440)
 labels=['左脚尖前后','未来右向','未来前向'];q=real['query']['features'];b=real['winner']['features'];text(d,(65,195),'特征 / 米',38,b=True);text(d,(410,195),'当前查询',38,b=True);text(d,(725,195),'最佳候选',38,b=True)
 for i,label in enumerate(labels):
  y=300+i*150;box(d,(45,y-20,1017,y+95),WHITE);text(d,(65,y),label,39);text(d,(400,y),f'{q[i]:.6f}',40);text(d,(715,y),f'{b[i]:.6f}',40,GREEN)
 box(d,(45,800,1017,1270),'#d4e9dd');text(d,(75,830),'全扫描：1219个候选',43,b=True);text(d,(75,925),'最小代价：0.00086628',43,b=True);text(d,(75,1020),'未来地面点误差：2.73厘米',41);text(d,(75,1120),'仍有偏差，不是“完全命中”。',40)
 footer(d,1440,'这是一次离线查询；不代表完整游戏控制器。');save(im,'13-real-query.png',out)
 #14 Real animation. Two aligned segments each hold fixed initial frame transform.
 frames=[]
 for i in range(16):
  im,d=canvas('同一起点，接着播放各自半秒','真实CMU数据重绘；没有混合、锁脚或碰撞',1200)
  for col,(label,n,c) in enumerate([('current','16_15',BLUE),('selected','16_17',GREEN)]):
   row=D['comparison'][label][i];x=280+col*500;text(d,(55+col*500,190),'原直行'if col==0 else'选中片段',40,c,True)
   floor(d,x,880,315,extent=.6);pose(d,row['positions'],x,880,315,D)
   center(d,(x,985),f"{n} · 帧{row['source_frame']}",36)
  center(d,(531,1070),f"源时间 +{i/30:.3f}秒 / 0.500秒",38,b=True)
  footer(d,1200,'30帧/秒显示采样；首尾另加停顿。');frames.append(im)
 # GIF uses a fixed palette across every frame; no unpredictable per-frame colors.
 palette=frames[0].quantize(colors=128,method=Image.Quantize.MEDIANCUT)
 qframes=[f.quantize(palette=palette,dither=Image.Dither.NONE)for f in frames]
 # GIF duration in 10ms ticks; internal intervals 30/30/40ms, source time explicitly labeled.
 durations=[800]+[30 if i%3!=0 else 40 for i in range(1,15)]+[1000]
 qframes[0].save(out/'14-real-playback.gif',save_all=True,append_images=qframes[1:],loop=0,duration=durations,optimize=False,disposal=2)
 #15 True 3D jump current versus selected, with projected connection.
 im,d=canvas('脚尖一项近，不等于全身接得上','真实对齐起点；两种颜色分别代表两个完整姿势',1460)
 text(d,(65,185),'原当前帧',38,BLUE);text(d,(555,185),'选中帧',38,ORANGE)
 floor(d,560,980,420);pose(d,current,560,980,420,D,color=BLUE,width=11);pose(d,selected,560,980,420,D,color=ORANGE,width=7)
 idx=D['names'].index('rfemur');a=screen(np.array(current)[idx],560,980,420);b=screen(np.array(selected)[idx],560,980,420)
 d.line([a,b],fill=RED,width=7);dot(d,a,RED,13);dot(d,b,RED,13)
 arrow(d,(800,845),((a[0]+b[0])/2+20,(a[1]+b[1])/2),RED,4,13);text(d,(810,820),'右膝',38,RED)
 box(d,(45,1100,1017,1325),WHITE);text(d,(75,1120),'左脚尖前后项：差2.76毫米',40);text(d,(75,1200),'右膝三维端点：差16.24厘米',42,RED,True)
 footer(d,1460,'数字来自三维计算，不是测量图上的像素。');save(im,'15-remaining-jump.png',out)
 #Cover: original conceptual graphic, not a derivative skeleton.
 im,d=canvas('下一步，选哪一帧？','Motion Matching · 从四个候选到真实动作库',800)
 for i,(id,col)in enumerate([('A',BLUE),('B',ORANGE),('C',GREEN),('D',MUTED)]):
  x=65+i*250;box(d,(x,260,x+215,490),WHITE,col);center(d,(x+107,355),id,80,col,True);center(d,(x+107,445),'候选帧',36)
 arrow(d,(120,620),(670,620),GREEN,12,26);text(d,(720,585),'选C',60,GREEN,True)
 footer(d,800,'姿势接近 + 未来路径接近 → 取回完整后续');save(im,'cover.png',out.parent)
 meta=[]
 for p in sorted(out.glob('*')):
  if p.suffix.lower()not in('.png','.gif'):continue
  obj=Image.open(p);count=getattr(obj,'n_frames',1)
  for i in range(count):obj.seek(i);obj.load()
  meta.append(dict(file=p.name,width=obj.width,height=obj.height,frames=count,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),identity='CMU-data derived original render under CMU terms'if p.name[:2]in['01','02','12','13','14','15']else'Original explanatory diagram with invented teaching data'))
 (out.parent/'figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'body_images':len(meta),'animated_frames':16,'minimum_font_px_at_1062':36,'gif_note':'Source sampling30Hz; GIF playback timing quantized to10ms and endpoint holds'},ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--article',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();main(a.article.resolve(),a.output.resolve())
