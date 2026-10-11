"""Original explicit-data illustrations; not measured terrain. Python+NumPy+Matplotlib."""
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon,Rectangle
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets';OUT.mkdir(exist_ok=True)
F=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',size=24);plt.rcParams.update({'font.family':F.get_name(),'font.size':24,'axes.unicode_minus':False,'figure.facecolor':'#f6f3eb','axes.facecolor':'#f6f3eb'})
BLUE='#247b9b';RED='#c45437';GREEN='#478b65';GOLD='#dbac37';GRAY='#75878b'
H=np.array([[0,2,0],[2,6,2],[0,2,0]],float)
def fig(title,n=1):
 f,aa=plt.subplots(1,n,figsize=(12,8.4),dpi=100,squeeze=False);f.suptitle(title,fontsize=28,fontproperties=F,y=.96);f.text(.04,.035,'原创数值教学图 · 自设样本 · 非实测地图',fontproperties=F,fontsize=16,color=GRAY);f.subplots_adjust(left=.09,right=.96,bottom=.16,top=.84,wspace=.32);return f,aa.ravel()
def save(f,name):f.savefig(OUT/name);plt.close(f)
def grid(ax,lim=(0,2,0,2),labels=True):
 ax.set_xlim(lim[0]-.15,lim[1]+.15);ax.set_ylim(lim[2]-.15,lim[3]+.15);ax.set_aspect('equal');ax.set_xlabel('x');ax.set_ylabel('y');ax.set_xticks(np.arange(lim[0],lim[1]+.1));ax.set_yticks(np.arange(lim[2],lim[3]+.1));ax.grid(alpha=.2)
def cell(ax,v=(0,2,6,2),lev=3,labels=True):
 ps=np.array([[0,0],[1,0],[1,1],[0,1]]);ax.add_patch(Rectangle((0,0),1,1,fill=False,color=GRAY,lw=3))
 for i,(p,z) in enumerate(zip(ps,v)):
  ax.scatter(*p,s=170,c=RED if z>lev else BLUE,zorder=5)
  if labels:ax.text(p[0]+(-.07 if p[0]==0 else .07),p[1]+(-.12 if p[1]==0 else .07),f'{"ABCD"[i]}：{z:g}',ha='right' if p[0]==0 else 'left',fontsize=22)
 ax.set_xlim(-.4,1.5);ax.set_ylim(-.35,1.35);ax.set_aspect('equal');ax.axis('off')
def march(h,level):
 seg=[]
 for y in range(h.shape[0]-1):
  for x in range(h.shape[1]-1):
   p=np.array([[x,y],[x+1,y],[x+1,y+1],[x,y+1]],float);v=np.array([h[y,x],h[y,x+1],h[y+1,x+1],h[y+1,x]])-level;hit={}
   for e in range(4):
    j=(e+1)%4
    if (v[e]>0)!=(v[j]>0):hit[e]=p[e]+(-v[e]/(v[j]-v[e]))*(p[j]-p[e])
   if len(hit)==2:seg.append(list(hit.values()))
   elif len(hit)==4:
    pairs=[(0,1),(2,3)] if v[0]*v[2]-v[1]*v[3]>0 else [(0,3),(1,2)]
    seg += [[hit[a],hit[b]] for a,b in pairs]
 return np.array(seg)
def segments(ax,h=H,lev=3,color=RED,lw=5):
 for ss in march(h,lev):ax.plot(ss[:,0],ss[:,1],c=color,lw=lw)
def samples(ax,h=H):
 for y in range(h.shape[0]):
  for x in range(h.shape[1]):ax.scatter(x,y,c=RED if h[y,x]>3 else BLUE,s=90,zorder=5);ax.text(x+.06,y+.07,str(int(h[y,x])),fontsize=24)
# question
f,a=fig('高度数字，可以变成一条海岸线',2)
for ax in a:ax.imshow(H,origin='lower',extent=(-.5,2.5,-.5,2.5),cmap='terrain',vmin=0,vmax=6,interpolation='nearest');ax.axis('off')
a[0].set_title('九个高度样本',fontproperties=F);a[1].set_title('海平面＝3',fontproperties=F);segments(a[1],color='#732b70',lw=6);save(f,'01-island-question.png')
f,a=fig('九个位置，九个高度');grid(a[0]);samples(a[0]);save(f,'02-nine-samples.png')
f,a=fig('两端相同，中间并不唯一');x=np.linspace(0,1,300);a[0].plot(x,2+4*x,c=BLUE,lw=5,label='本文选择：线性插值');a[0].plot(x,2+4*x+2*np.sin(np.pi*x),c=RED,lw=4,ls='--',label='另一条符合两端的曲线');a[0].scatter([0,1],[2,6],s=120,c='black');a[0].set_xlabel('沿边的位置');a[0].set_ylabel('高度');a[0].legend(prop=F,fontsize=20);save(f,'03-interpolation-assumption.png')
f,a=fig('放大左下角：只看四个样本');cell(a[0]);a[0].text(.5,.5,'目标高度＝3',ha='center',fontproperties=F,fontsize=27);save(f,'04-one-cell.png')
f,a=fig('一端低、一端高：这条边跨过阈值');cell(a[0]);a[0].plot([1,1],[0,1],c=GOLD,lw=10);a[0].plot([0,1],[1,1],c=GOLD,lw=10);a[0].text(.4,.4,'黄色边要找交点',ha='center',fontproperties=F,fontsize=24);save(f,'05-crossing-edges.png')
f,a=fig('从2走向6：高度3在四分之一处');ax=a[0];ax.plot([0,1],[2,6],lw=5,c=BLUE);ax.axhline(3,c=GOLD,lw=3,ls='--');ax.plot([.25,.25],[1.5,3],c=RED,lw=3,ls='--');ax.scatter(.25,3,s=180,c=RED);ax.text(.29,2.6,'t＝0.25',fontsize=26,c=RED);ax.set_xlim(-.05,1.05);ax.set_ylim(1.5,6.5);ax.set_xlabel('从B到C的比例');ax.set_ylabel('高度');save(f,'06-edge-quarter.png')
f,a=fig('连接两个插值点，得到本格线段');cell(a[0]);a[0].plot([1,.25],[.25,1],c=RED,lw=6);a[0].scatter([1,.25],[.25,1],c=GOLD,s=150,zorder=6);a[0].text(1.05,.24,'(1,0.25)',fontsize=21);a[0].text(.15,1.17,'(0.25,1)',fontsize=21);save(f,'07-first-segment.png')
f,a=fig('每个格子交出一段，再拼到一起');grid(a[0]);samples(a[0]);
for i,ss in enumerate(march(H,3)):a[0].plot(ss[:,0],ss[:,1],c=[BLUE,RED,GREEN,GOLD][i],lw=7)
save(f,'08-four-cells.png')
f,a=fig('四段闭合：中央陆地被围住');grid(a[0]);a[0].add_patch(Polygon([[.25,1],[1,.25],[1.75,1],[1,1.75]],facecolor='#b9d9ab',edgecolor=GREEN,lw=5));a[0].text(1,1,'陆地',ha='center',fontproperties=F,fontsize=27);a[0].text(.3,.25,'水',fontproperties=F,fontsize=27,color=BLUE);save(f,'09-closed-coast.png')
f,a=fig('公共边只需要一个身份');ax=a[0]
for x in (0,1):ax.add_patch(Rectangle((x,0),1,1,fill=False,color=GRAY,lw=3))
ax.plot([1,1],[0,1],c=GOLD,lw=8);ax.scatter(1,.4,s=150,c=RED,zorder=5);ax.plot([.1,1,1.9],[.8,.4,.7],c=BLUE,lw=5);ax.text(.5,.2,'左格',ha='center',fontproperties=F);ax.text(1.5,.2,'右格',ha='center',fontproperties=F);ax.text(1,1.16,'同一条竖边 → 同一个交点',ha='center',fontproperties=F,fontsize=24);ax.set_xlim(-.2,2.2);ax.set_ylim(-.1,1.4);ax.set_aspect('equal');ax.axis('off');save(f,'10-shared-edge.png')
f=plt.figure(figsize=(12,8.4),dpi=100);f.suptitle('四个常见类别：先理解，再查表',fontproperties=F,fontsize=28);f.text(.04,.035,'原创分类示意 · 红点高于阈值，蓝点低于阈值',fontproperties=F,fontsize=16,color=GRAY)
for i,v in enumerate([(-1,-1,-1,-1),(-1,-1,1,-1),(-1,1,1,-1),(1,1,1,-1)]):
 ax=f.add_subplot(2,2,i+1);cell(ax,v,0,False);hh=np.array([[v[0],v[1]],[v[3],v[2]]]);segments(ax,hh,0);ax.set_title(['全低','一个高','相邻两个高','三个高'][i],fontproperties=F,fontsize=23)
f.subplots_adjust(top=.85,bottom=.1,hspace=.15);save(f,'11-ordinary-cases.png')
f,a=fig('四个交点，可能连接成两种不同答案',2)
for ax in a:cell(ax,(1,-1,1,-1),0,False)
for ss in [((.5,0),(0,.5)),((1,.5),(.5,1))]:a[0].plot(*np.array(ss).T,c=GREEN,lw=5)
for ss in [((.5,0),(1,.5)),((.5,1),(0,.5))]:a[1].plot(*np.array(ss).T,c=GREEN,lw=5)
a[0].set_title('高值两角分开',fontproperties=F);a[1].set_title('高值两角连通',fontproperties=F);save(f,'12-ambiguous-pairings.png')
f,a=fig('双线性：先横向，再纵向');ax=a[0];cell(ax,(8,-3,1,-3),0);ax.annotate('',(.65,0),(0,0),arrowprops={'arrowstyle':'->','color':GREEN,'lw':4});ax.annotate('',(.65,1),(0,1),arrowprops={'arrowstyle':'->','color':GREEN,'lw':4});ax.annotate('',(.65,.55),(.65,0),arrowprops={'arrowstyle':'->','color':GOLD,'lw':4});ax.scatter(.65,.55,c=RED,s=120);ax.text(.12,.45,'再纵向\n混合',fontproperties=F,fontsize=25);save(f,'13-bilinear-steps.png')
x=np.linspace(0,1,501);X,Y=np.meshgrid(x,x);Z=8-11*X-11*Y+15*X*Y
for name,title,saddle in [('14-center-trap.png','中心高于0，仍不代表两片高地相连',False),('15-saddle-location.png','真正的低鞍部，不在几何中心',True)]:
 f,a=fig(title);ax=a[0];ax.contourf(X,Y,Z,levels=[-4,0,9],colors=['#cee1ea','#d0e3b8']);ax.contour(X,Y,Z,levels=[0],colors=GREEN,linewidths=4);ax.scatter(.5,.5,c=RED,s=110);ax.text(.51,.45,'中心：0.75',fontsize=22);ax.set_aspect('equal');ax.set_xlabel('x');ax.set_ylabel('y')
 if saddle:ax.scatter(11/15,11/15,c='black',s=110);ax.text(.27,.86,'鞍点：(11/15,11/15)\n值＝−1/15',fontproperties=F,fontsize=22)
 else:ax.text(.04,.05,'高值8',fontproperties=F,fontsize=20);ax.text(.82,.93,'高值1',fontproperties=F,fontsize=20) # labels replaced below
 save(f,name)
f,a=fig('走出数据窗口：轮廓可以是开放的');ax=a[0];xx=np.linspace(-1,1,101);X,Y=np.meshgrid(xx,xx);ax.imshow(X+Y,extent=(-1,1,-1,1),origin='lower',cmap='Blues');ax.plot([-1,1],[1,-1],c=RED,lw=6);ax.scatter([-1,1],[1,-1],c=GOLD,s=140);ax.set_xlabel('x');ax.set_ylabel('y');ax.text(-.8,-.7,'窗口外没有数据',fontproperties=F,fontsize=23,color=BLUE);save(f,'16-open-boundary.png')
f,a=fig('同一种局部思路：二维线段，三维面片',2);ax=a[0];cell(ax,(-1,-1,1,-1),0,False);ax.plot([.5,1],[1,.5],c=RED,lw=6);ax.set_title('二维方格',fontproperties=F)
ax=a[1];front=np.array([[0,0],[1,0],[1,1],[0,1],[0,0]]);back=front+np.array([.4,.35]);ax.plot(*front.T,c=GRAY,lw=3);ax.plot(*back.T,c=GRAY,lw=3)
for u,v in zip(front[:4],back[:4]):ax.plot(*np.array([u,v]).T,c=GRAY,lw=3)
ax.add_patch(Polygon([[1,.5],[.5,1],[1.2,1.175]],facecolor='#b9d9ab',edgecolor=GREEN,lw=4));ax.set_xlim(-.3,1.7);ax.set_ylim(-.2,1.6);ax.set_aspect('equal');ax.axis('off');ax.set_title('三维立方体（概念示意）',fontproperties=F,fontsize=24);save(f,'17-square-cube.png')
f,a=fig('同一份高度样本，只改变海平面');grid(a[0]);
for lev,c in [(1,BLUE),(3,GREEN),(4,RED)]:
 segments(a[0],H,lev,c,5);a[0].plot([],[],color=c,lw=5,label=f'高度 {lev}')
a[0].legend(prop=F,loc='upper right');save(f,'18-changing-level.png')
print('18 original figures generated; segments at level 3:',march(H,3).tolist())
