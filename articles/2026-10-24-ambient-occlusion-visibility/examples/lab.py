"""Original ambient visibility ray tracer, sphere and infinite ground; MIT."""
from pathlib import Path
import numpy as np,json,math,platform
from figurelib import *
P=Path(__file__).resolve().parents[1];A=P/'assets';M=[]
R=.8;CENTER=np.array([0.,0.,.8]);EPS=1e-5
rng=np.random.default_rng(24);uv=rng.random((128,2));rr=np.sqrt(uv[:,0]);ph=2*np.pi*uv[:,1];SAMPLES=np.c_[rr*np.cos(ph),rr*np.sin(ph),np.sqrt(1-uv[:,0])]
def sphere_t(o,d,c=CENTER):
 oc=o-c;b=np.sum(oc*d,axis=-1);cc=np.sum(oc*oc,axis=-1)-R*R;disc=b*b-cc;root=np.sqrt(np.maximum(disc,0));t=-b-root;t2=-b+root;t=np.where(t>EPS,t,t2);return np.where((disc>=0)&(t>EPS),t,np.inf)
def scene_t(o,d,c=CENTER):
 ts=sphere_t(o,d,c);tg=np.divide(-o[...,2],d[...,2],out=np.full_like(ts,np.inf),where=np.abs(d[...,2])>1e-12);tg=np.where(tg>EPS,tg,np.inf);return np.minimum(ts,tg)
def visible(points,normals,ns=128,limit=4,c=CENTER):
 norm=np.asarray(normals);helper=np.tile([0.,0.,1.],norm.shape[:-1]+(1,));helper[np.abs(norm[...,2])>.9]=[1.,0.,0.];t=np.cross(helper,norm);t/=np.linalg.norm(t,axis=-1)[...,None];b=np.cross(norm,t);o=points+EPS*4*norm;total=np.zeros(points.shape[:-1]);flags=[]
 for s in SAMPLES[:ns]:
  d=s[0]*t+s[1]*b+s[2]*norm;ok=scene_t(o,d,c)>limit;total+=ok
  if total.ndim==0:flags.append(bool(ok))
 return total/ns,flags
# Primary camera rays.
H,W0=150,180;y,x=np.indices((H,W0));eye=np.array([3.,-5.,3.]);target=np.array([0.,0.,.6]);forward=target-eye;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward);d=forward+((x-W0/2)/(W0/2)*.65)[...,None]*right+((H/2-y)/(W0/2)*.65)[...,None]*up;d/=np.linalg.norm(d,axis=-1)[...,None]
def render(ns=128,limit=4,lift=0):
 c=CENTER+[0,0,lift];o=np.broadcast_to(eye,d.shape);ts=sphere_t(o,d,c);tg=np.divide(-eye[2],d[...,2],out=np.full((H,W0),np.inf),where=d[...,2]<0);valid=np.isfinite(np.minimum(ts,tg));tp=np.minimum(ts,tg);pts=o+d*np.where(valid,tp,0)[...,None];sphere=ts<tg;norm=np.zeros_like(pts);norm[...,2]=1;norm[sphere]=(pts[sphere]-c)/R;ao=np.ones((H,W0));ao[valid]=visible(pts[valid],norm[valid],ns,limit,c)[0];base=np.full((H,W0,3),.72);base[sphere]=[.32,.54,.66];base[~valid]=[.92,.94,.96];out=base*ao[...,None];out[~valid]=base[~valid];return out,base,ao
rendered={}
for name,args in [('main',{}),('short',{'limit':.35}),('long',{'limit':8}),('few',{'ns':8}),('lift',{'lift':.35})]:rendered[name]=render(**args)
point=np.array([1.,0.,0.]);normal=np.array([0.,0.,1.]);av,flags=visible(point,normal,8,4);xs=np.linspace(.82,2.5,21);profile=visible(np.c_[xs,np.zeros_like(xs),np.zeros_like(xs)],np.tile(normal,(len(xs),1)),128,4)[0]
v={'radius':R,'center':CENTER.tolist(),'seed':24,'eight_point':point.tolist(),'eight_directions_local':SAMPLES[:8].tolist(),'eight_visible':flags,'eight_accessibility':float(av),'epsilon':EPS,'profile_x':xs.tolist(),'profile_A':profile.tolist(),'render_pixels':[W0,H],'samples':128,'max_distance':4,'versions':{'python':platform.python_version(),'numpy':np.__version__}}
assert all(0<=z<=1 for z in profile)
assert np.isclose(visible(np.array([100.,0.,0.]),normal,128,4)[0],1)
assert all(np.all(rendered['short'][2]>=rendered['long'][2]-1e-12) for _ in [0])
(P/'examples/results.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');v=json.loads((P/'examples/results.json').read_text())
def save(f,n,p,id='原创教学示意'):M.append(f.save(A/n,p,id))
def pair(title,left,right,labels,n,p):
 f=Fig(title);f.image(rgbim(left).resize((420,350)),(40,140));f.image(rgbim(right).resize((420,350)),(500,140));f.text(50,530,labels[0]);f.text(510,530,labels[1]);save(f,n,p,'原创射线程序运行结果')
pair('同一个球，只改变环境可见性',rendered['main'][1],rendered['main'][0],['均匀底色','底色 × A'],'01-render.png','实际场景基线与AO输出')
f=Fig('表面上方：能收到来光的半球');f.line([(70,670),(890,670)],INK,7);f.d.arc((160,350,800,990),180,360,fill=BLUE,width=5);f.arrow((480,670),(480,270),GREEN,7)
for th in np.linspace(.15,np.pi-.15,9):f.arrow((480,670),(480+310*np.cos(th),670-310*np.sin(th)),BLUE,3)
f.text(520,250,'法线');f.text(80,730,'下方被表面自身挡住');save(f,'02-hemisphere.png','半球的二维切面和法线方向')
f=Fig('八个方向：蓝通，红被挡');f.d.ellipse((250,140,710,600),outline=GRAY,width=4);f.mark((0,0,0,600))
for i,(s,ok) in enumerate(zip(SAMPLES[:8],flags)):
 x=480+210*s[0];y=370-210*s[1];f.dot(x,y,18,BLUE if ok else RED)
for i,ok in enumerate(flags):f.dot(85+110*i,675,20,BLUE if ok else RED);f.text(70+110*i,720,str(i+1),40)
f.text(85,805,f"A = {sum(flags)} / 8 = {float(av):.3f}");save(f,'03-eight.png','八个真实余弦采样方向投影到单位圆及遮挡结果','原创程序运行结果')
f=Fig('斜着来的同一束光，摊得更开');f.line([(70,620),(950,620)],INK,7)
for x in [180,220,260]:f.arrow((x,200),(x,610),BLUE,6)
for k in range(3):
 x=520+20*k;y=470-34.641016*k;f.arrow((x,y),(x+(610-y)*math.sqrt(3),610),RED,6)
f.text(100,690,'正对表面');f.text(550,690,'斜对表面');save(f,'04-cosine.png','余弦权重的投影直觉')
pair('只看近邻，还是把远处也计入？',rendered['short'][0],rendered['long'][0],['最大距离 0.35','最大距离 8'],'05-distance.png','同一采样方向不同遮蔽距离的实际对照')
pair('球离地后，接触区域改变',rendered['main'][0],rendered['lift'][0],['球底高度 0','球底高度 0.35'],'06-lift.png','实际几何抬升改变遮蔽')
pair('增加方向样本，离散噪点减轻',rendered['few'][0],rendered['main'][0],['每点 8 条','每点 128 条'],'07-samples.png','同一序列前缀的采样数对照')
f=Fig('起点略偏离表面，避免打中自己');f.line([(70,620),(880,620)],INK,7);f.dot(380,620,12,RED);f.dot(380,520,12,BLUE);f.arrow((380,520),(700,240),BLUE);f.arrow((340,605),(340,530),GREEN);f.text(70,700,'偏移在此被夸大画出');f.text(70,770,'过大的偏移会漏掉近处遮挡');save(f,'08-offset.png','自相交与偏移量风险示意')
f=Fig('同样可见一半，灯在哪边很重要');f.line([(70,650),(890,650)],INK,7);f.rect((460,220,520,650),fill=GRAY);f.dot(280,650,10);f.d.ellipse((80,200,190,310),fill='#e7af37');f.d.ellipse((720,200,830,310),fill='#e7af37');f.arrow((140,320),(280,630),BLUE);f.line([(720,320),(520,470)],RED,6);f.text(70,720,'左侧灯可达');f.text(580,720,'右侧灯被挡');save(f,'09-light-direction.png','单个可见比例不能保存环境亮度方向')
f=Fig('屏幕看不到的，也可能挡环境光');f.rect((200,180,720,610),outline=BLUE,width=5);f.rect((710,240,860,440),fill=GRAY);f.dot(660,530,14);f.arrow((660,530),(760,350),RED);f.text(70,680,'蓝框：屏幕保存的信息范围');f.text(70,750,'框外几何不在这张深度图里');save(f,'10-screen.png','屏幕空间方法的可见信息限制')
f=Fig('换了表面朝向，半球也要转');f.line([(100,650),(450,650)],INK,7);f.line([(600,200),(600,650)],INK,7);f.arrow((270,650),(270,320),GREEN,7);f.arrow((600,430),(880,430),GREEN,7);f.text(70,720,'地面：向上');f.text(550,720,'墙面：向侧面');save(f,'11-normal.png','局部法线控制采样半球朝向')
f=Fig('同一处遮挡，不要无意扣两次');val=.5;f.rect((100,160,430,410),fill=tuple(np.uint8(srgb([val]*3)*255)));f.rect((530,160,860,410),fill=tuple(np.uint8(srgb([val*val]*3)*255)));f.text(120,460,'A = 0.5');f.text(540,460,'A × A = 0.25');f.text(70,560,'已烘焙的暗处，再乘 AO 会更暗');save(f,'12-double.png','两次遮蔽乘法的数值反例')
f=Fig('红墙反射来的红光，不在 A 里面');f.rect((120,170,230,640),fill='#c64c3b');f.rect((230,570,860,640),fill='#e8e1d5');f.arrow((180,370),(450,560),RED,8);f.dot(450,570,12,BLUE);f.text(70,720,'AO 只问挡没挡，不追这次反弹');save(f,'13-bounce.png','AO遗漏颜色串染的机制示意')
f=Fig('离球越远：本场景的可达率剖面');x0,y0=110,650;f.arrow((x0,y0),(900,y0));f.arrow((x0,y0),(x0,150));pts=[(x0+(x-.8)/1.8*740,y0-a*460) for x,a in zip(v['profile_x'],v['profile_A'])];f.line(pts,BLUE,6)
for val in [0,.5,1]:f.text(15,y0-val*460-15,str(val),40)
for val in [1,1.5,2,2.5]:f.text(x0+(val-.8)/1.8*740-20,690,str(val),40)
f.text(300,775,'地面 x 坐标；球心 x = 0');save(f,'14-profile.png','128方向计算得到的地面可达率剖面','原创程序运行结果')
finish(M,P);print(json.dumps({'figures':len(M),'eight_visible':flags,'A':float(av),'render_pixels':v['render_pixels']},ensure_ascii=False))
