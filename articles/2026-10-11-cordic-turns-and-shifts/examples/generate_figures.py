"""Original teaching graphics, not chip benchmarks or historical schematics."""
from pathlib import Path
import math
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle,Arc
OUT=Path(__file__).resolve().parents[1]/'assets';F=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',size=24)
plt.rcParams.update({'font.family':F.get_name(),'font.size':24,'axes.unicode_minus':False,'figure.facecolor':'#f6f3eb','axes.facecolor':'#f6f3eb'})
BLUE='#247b9b';RED='#c45437';GREEN='#478b65';GOLD='#d1a62d';GRAY='#789095'
def fig(title):
 f,ax=plt.subplots(figsize=(12,8.4),dpi=100);f.suptitle(title,fontproperties=F,fontsize=29,y=.95);f.subplots_adjust(left=.13,right=.94,bottom=.17,top=.83);return f,ax
def save(f,n):f.savefig(OUT/n);plt.close(f)
def arrow(ax,p,q,c=BLUE,lw=4):ax.annotate('',q,p,arrowprops={'arrowstyle':'->','color':c,'lw':lw,'mutation_scale':22})
def axes(ax,lim=(-.15,1.85,-.15,1.65)):
 ax.axhline(0,color=GRAY,lw=2);ax.axvline(0,color=GRAY,lw=2);ax.set_xlim(lim[:2]);ax.set_ylim(lim[2:]);ax.set_aspect('equal');ax.set_xlabel('x');ax.set_ylabel('y');ax.grid(alpha=.15)
def box(ax,x,y,w,h,label,c=BLUE):
 ax.add_patch(Rectangle((x,y),w,h,facecolor=c,alpha=.12,edgecolor=c,lw=3));ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontproperties=F,fontsize=26)
def cordic(n,prescale=True):
 K=math.prod(1/math.sqrt(1+2**(-2*i)) for i in range(n));x,y,z=(K if prescale else 1),0,math.radians(30);rows=[(x,y,z)]
 for i in range(n):
  d=1 if z>=0 else -1;x,y=x-d*y*2**-i,y+d*x*2**-i;z-=d*math.atan(2**-i);rows.append((x,y,z))
 return rows
f,ax=fig('转到30°：坐标就是余弦和正弦');axes(ax,(-.15,1.25,-.15,1.25));t=np.linspace(0,math.pi/2,100);ax.plot(np.cos(t),np.sin(t),c=GRAY,lw=3);c,s=math.cos(math.pi/6),.5;arrow(ax,(0,0),(c,s));ax.plot([c,c,0],[0,s,s],ls='--',c=GOLD,lw=3);ax.text(.15,.15,'30°',fontsize=26);ax.text(.55,-.1,'cos 30°',fontsize=24);ax.text(.02,.55,'sin 30°',fontsize=24);save(f,'01-unit-circle.png')
f,ax=fig('把难函数，交给便宜的基本动作');ax.axis('off');ax.set_xlim(0,10);ax.set_ylim(0,6);box(ax,.2,3.8,2.5,1.2,'状态 x、y、z');box(ax,3.8,3.8,2.5,1.2,'移位与加减');box(ax,7.3,3.8,2.5,1.2,'下一轮状态');arrow(ax,(2.7,4.4),(3.8,4.4));arrow(ax,(6.3,4.4),(7.3,4.4));box(ax,3.8,1,2.5,1.2,'固定角度表',GREEN);arrow(ax,(5.05,2.2),(5.05,3.8),GREEN);ax.text(5,.1,'概念信息流，不是历史机器接线图',ha='center',fontproperties=F,fontsize=23);save(f,'02-hardware-idea.png')
f,ax=fig('旋转两个分量，再把它们相加');axes(ax,(-.55,1.6,-.15,1.5));p=np.array([1,.5]);a=math.pi/6;rx=np.array([math.cos(a),math.sin(a)]);ry=np.array([-.5*math.sin(a),.5*math.cos(a)]);arrow(ax,(0,0),(1,0),GRAY);arrow(ax,(1,0),p,GRAY);arrow(ax,(0,0),rx,BLUE);arrow(ax,rx,rx+ry,GREEN);arrow(ax,(0,0),rx+ry,RED);ax.text(.8,.9,'合成结果',fontproperties=F,fontsize=24,color=RED);save(f,'03-rotation-components.png')
f,ax=fig('角度表：每次减半的是斜率');axes(ax,(-.05,1.4,-.05,1.25))
for slope,c in [(1,RED),(.5,BLUE),(.25,GREEN)]:
 arrow(ax,(0,0),(1,slope),c);ax.text(1.02,slope,f'{math.degrees(math.atan(slope)):.3f}°',fontsize=23,color=c)
ax.text(.15,1.12,'tan α：1、1/2、1/4',fontsize=26);save(f,'04-special-angles.png')
f,ax=fig('二进制移位：12 → 6 → 3');ax.axis('off');ax.set_xlim(0,10);ax.set_ylim(0,6)
for j,(bits,num) in enumerate([('1 1 0 0','12'),('0 1 1 0','6'),('0 0 1 1','3')]):
 ax.text(2,5-j*1.8,bits,fontsize=39,family='DejaVu Sans Mono');ax.text(7,5-j*1.8,'＝'+num,fontsize=32)
 if j<2:ax.text(4,4.25-j*1.8,'右移一位',fontproperties=F,fontsize=24,color=RED)
save(f,'05-binary-shift.png')
rows=cordic(12,False)
for j,name,title in [(1,'06-step-one.png','第一步：45°，超过目标30°'),(2,'07-step-two.png','第二步：回到约18.435°'),(3,'08-step-three.png','第三步：补到约32.471°')]:
 f,ax=fig(title);axes(ax);arrow(ax,(0,0),rows[j-1][:2],GRAY);arrow(ax,(0,0),rows[j][:2],BLUE);ax.plot([0,1.7*math.cos(math.pi/6)],[0,1.7*.5],ls='--',c=RED,lw=3);ax.text(.12,1.4,'红虚线：目标方向',fontproperties=F,fontsize=23,color=RED);ax.text(.6,1.18,f'新坐标 ({rows[j][0]:g}, {rows[j][1]:g})',fontsize=24);save(f,name)
f,ax=fig('残差会来回摆，不是每一步都更小');ax.plot(range(13),[math.degrees(r[2]) for r in rows],'-o',c=BLUE,lw=3);ax.axhline(0,c=RED,ls='--');ax.set_xlabel('已完成轮数');ax.set_ylabel('目标减已转角度（度）');save(f,'09-residual-zigzag.png')
f,ax=fig('固定轮数，固定放大倍数');g=[math.prod(math.sqrt(1+2**(-2*i)) for i in range(n)) for n in range(13)];ax.plot(range(13),g,'-o',c=BLUE,lw=3);ax.axhline(g[-1],c=RED,ls='--');ax.set_xlabel('轮数 N');ax.set_ylabel('总长度放大 G_N');ax.text(4,1.5,'逐渐接近 1.64676',fontproperties=F,fontsize=25);save(f,'10-gain.png')
f,ax=fig('先缩短，再让固定放大补回来');axes(ax,(-.15,1.35,-.15,1.25));K=math.prod(1/math.sqrt(1+2**(-2*i)) for i in range(20));arrow(ax,(0,0),(K,0),GREEN);arrow(ax,(0,0),cordic(20)[-1][:2],BLUE);t=np.linspace(0,math.pi/2,100);ax.plot(np.cos(t),np.sin(t),c=GRAY);ax.text(.12,.13,'起点长度约0.60725',fontproperties=F,fontsize=22,color=GREEN);ax.text(.22,.85,'最终长度约1',fontproperties=F,fontsize=26,color=BLUE);save(f,'11-prescale.png')
f,ax=fig('固定表项：不用随输入重新求角度');ax.axis('off');ax.set_xlim(0,10);ax.set_ylim(0,6)
for i in range(4):
 ax.text(1,5-i*1.3,f'i＝{i}',fontsize=29);ax.text(3,5-i*1.3,f'atan(1/{2**i})',fontsize=28);ax.text(6.5,5-i*1.3,f'{math.degrees(math.atan(2**-i)):.3f}°',fontsize=28,color=BLUE)
save(f,'12-angle-table.png')
f,ax=fig('两个新值，都必须读取同一份旧状态');ax.axis('off');ax.set_xlim(0,10);ax.set_ylim(0,6);box(ax,.3,2.2,2.5,1.5,'旧x、旧y');box(ax,6,3.7,3.5,1.2,'新x＝旧x−d·旧y·h');box(ax,6,.8,3.5,1.2,'新y＝旧y＋d·旧x·h',GREEN);arrow(ax,(2.8,3),(6,4.3));arrow(ax,(2.8,3),(6,1.4),GREEN);ax.text(3.5,.1,'h＝2的负i次方',fontproperties=F,fontsize=23);save(f,'13-state-update.png')
f,ax=fig('8位小数：只能落在1/256的刻度上');ax.set_xlim(.490,.510);ax.set_ylim(-.5,.9);ax.axhline(0,c=GRAY)
for n in range(126,131):ax.plot([n/256,n/256],[-.1,.1],c=BLUE,lw=3);ax.text(n/256,-.25,f'{n}/256',ha='center',fontsize=22)
ax.scatter(.5012,.55,c=RED,s=120);arrow(ax,(.5012,.52),(.5,.04),RED);ax.text(.5012,.7,'连续值示例',ha='center',fontproperties=F,fontsize=25);ax.axis('off');save(f,'14-quantization.png')
f,ax=fig('实际教学计算：轮数与正弦误差');ns=range(1,25);err=[abs(cordic(n)[-1][1]-.5) for n in ns];ax.semilogy(ns,err,'-o',c=BLUE,lw=3);ax.set_xlabel('轮数 N');ax.set_ylabel('sin 30°绝对误差（对数）');ax.grid(alpha=.15);save(f,'15-error-iterations.png')
f,ax=fig('120°＝90°＋30°：交换坐标并改符号');axes(ax,(-1.1,1.1,-.2,1.2));t=np.linspace(0,math.pi,150);ax.plot(np.cos(t),np.sin(t),c=GRAY);arrow(ax,(0,0),(.8660254,.5),BLUE);arrow(ax,(0,0),(-.5,.8660254),RED);ax.text(.55,.7,'(c,s)',fontsize=26,color=BLUE);ax.text(-1,.95,'(−s,c)',fontsize=26,color=RED);save(f,'16-quadrant.png')
f,ax=fig('向量模式：给定坐标，反求方向与长度');axes(ax,(-.3,5.5,-.3,5.1));arrow(ax,(0,0),(3,4),BLUE);ax.plot([3,3,0],[0,4,4],c=GOLD,ls='--',lw=3);ax.text(1.05,2.5,'长度5',fontproperties=F,fontsize=28,color=BLUE);ax.text(1.3,.25,'方向约53.130°',fontproperties=F,fontsize=24);ax.text(3.2,4.2,'(3,4)',fontsize=26);save(f,'17-vectoring.png')
f,ax=fig('同一种思想，不同的进制与控制细节');ax.axis('off');ax.set_xlim(0,10);ax.set_ylim(0,6);box(ax,.3,2,4.3,2.7,'本文二进制教学版\n1、1/2、1/4…\n每轮选择正转或反转',BLUE);box(ax,5.3,2,4.3,2.7,'HP-35文献中的尺度\n1、0.1、0.01…\n重复减角与计数',GREEN);ax.text(5,.8,'不能把教学循环当作历史固件',ha='center',fontproperties=F,fontsize=28,color=RED);save(f,'18-two-radices.png')
print('Generated18 CORDIC figures')
