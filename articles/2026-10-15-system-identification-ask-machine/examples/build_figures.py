"""Original system-identification diagrams from the attached experiment."""
from pathlib import Path
import argparse,json,math
from PIL import Image,ImageDraw,ImageFont
A=Path(__file__).resolve().parents[1]
P=argparse.ArgumentParser();P.add_argument('--output',type=Path,default=A);args=P.parse_args()
O=args.output; (O/'assets').mkdir(parents=True,exist_ok=True)
R=json.loads((A/'examples/expected-results.json').read_text())
W=1062; BG='#F3F4EB';INK='#163645';BLUE='#246F97';ORANGE='#B65A27';GREEN='#337766';MUTED='#61747B';PALE='#E7EDF0';WHITE='#FFFFFF';RED='#A53C41'
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
def point(d,p,label,col=BLUE,dx=18,dy=-55):
 dot(d,*p,col,12);text(d,p[0]+dx,p[1]+dy,label,40,col)
def triangle(d,pts,col=BLUE,fill='#D8E9EA',names=('A','B','C')):
 d.polygon(pts,fill=fill);d.line(pts+[pts[0]],fill=col,width=6)
 for p,n in zip(pts,names):point(d,p,n,col)
def plot(d,rect,series,xlim,ylim,xticks,yticks,xlab='时间 / 秒',ylab='温差 / °C'):
    x0,y0,x1,y1=rect
    def p(x,y):return x0+(x-xlim[0])/(xlim[1]-xlim[0])*(x1-x0),y1-(y-ylim[0])/(ylim[1]-ylim[0])*(y1-y0)
    for t in yticks:
        yy=p(xlim[0],t)[1];d.line((x0,yy,x1,yy),fill='#D5DFDF',width=3);text(d,x0-65,yy-27,f'{t:g}',36,MUTED,True)
    for t in xticks:
        xx=p(t,ylim[0])[0];d.line((xx,y1,xx,y1+12),fill=INK,width=3);text(d,xx,y1+20,f'{t:g}',36,MUTED,True)
    d.line((x0,y0,x0,y1,x1,y1),fill=INK,width=4)
    text(d,x0,y0-75,ylab,40,BLUE);text(d,(x0+x1)/2,y1+85,xlab,38,BLUE,True)
    for xs,ys,col in series:
        assert all(xlim[0]-1e-12<=x<=xlim[1]+1e-12 and ylim[0]-1e-12<=y<=ylim[1]+1e-12 for x,y in zip(xs,ys)), (current,min(ys),max(ys),ylim)
        pts=[p(x,y) for x,y in zip(xs,ys)];d.line(pts,fill=col,width=6)
    return p

def legend(d,y,entries):
    n=len(entries);width=900/n
    for i,(label,col) in enumerate(entries):
        x=80+i*width;d.line((x,y+29,x+45,y+29),fill=col,width=7);text(d,x+57,y,label,38,col)
#01
im,d=canvas('01','稳稳停在2，冷却却各不相同',1350)
text(d,531,185,'昨天：输入1，温差始终为2°C',40,BLUE,True)
series=[]
for row,col in zip(R['steady']['candidates'],[ORANGE,BLUE,GREEN]):series.append((list(range(9)),row['cooling'],col))
plot(d,(170,410,950,920),series,(0,8),(0,2),[0,2,4,6,8],[0,1,2])
text(d,531,275,'现在关掉输入；各模型开始分道扬镳',40,BLUE,True)
legend(d,1100,[('a=0.5',ORANGE),('a=0.8',BLUE),('a=0.9',GREEN)])
text(d,531,1210,'三组参数都符合昨天的稳态数据',40,MUTED,True)
save(im,'01-same-steady-different-cooling.png','Actual noiseless predictions of three steady-state-equivalent models')
#02 device sketch
im,d=canvas('02','给虚拟加热盒一个输入，记录输出',1320)
d.rounded_rectangle((280,320,820,850),radius=45,fill=WHITE,outline=INK,width=7)
text(d,550,360,'虚拟加热盒',48,BLUE,True)
d.line([(360,680),(400,610),(440,680),(480,610),(520,680),(560,610),(600,680)],fill=ORANGE,width=12)
text(d,490,730,'加热功率 u',42,ORANGE,True)
d.ellipse((690,650,755,715),fill=RED);d.rounded_rectangle((709,460,735,690),radius=12,outline=RED,width=7);d.line((722,550,722,685),fill=RED,width=10)
arrow(d,[(80,600),(250,600)],ORANGE);text(d,60,500,'输入',40,ORANGE)
arrow(d,[(845,600),(990,600)],BLUE);text(d,850,500,'输出 y',40,BLUE)
for x in [380,540,700]:arrow(d,[(x,300),(x,210)],MUTED)
text(d,531,950,'y：比环境温度高多少（°C）',42,BLUE,True)
text(d,531,1040,'u：0到1的归一化功率',42,ORANGE,True)
text(d,531,1150,'原创模型示意；没有真实设备测量',38,MUTED,True)
save(im,'02-input-output-box.png','Explicitly hypothetical heater model with normalized input and temperature-deviation output')
#03 time alignment
im,d=canvas('03','输入在哪一秒生效？先把表对齐',1260)
for j,(t,y,u) in enumerate([(0,'0','1'),(1,'0.4','1'),(2,'0.72','1')]):
    yy=230+j*280;box(d,(80,yy,982,yy+180),[f'时刻 k={t}：y={y}°C',f'随后这一秒：u={u}'],BLUE,size=44)
    if j<2:arrow(d,[(531,yy+195),(531,yy+255)],ORANGE)
text(d,531,1130,'第k行：用 y[k]、u[k] 预测 y[k+1]',38,GREEN,True)
save(im,'03-sample-alignment.png','Noiseless first samples and one-step input-output alignment')
#04 contributions
im,d=canvas('04','下一秒：保留一点，再加进一点',1330)
text(d,531,190,'y[k+1] = a × y[k] + b × u[k]',44,BLUE,True)
for yy,old,add,total,label in [(440,0,.4,.4,'第一秒：0 + 0.4 = 0.4'),(880,.32,.4,.72,'第二秒：0.32 + 0.4 = 0.72')]:
    x=160;scale=1000
    if old:d.rectangle((x,yy,x+old*scale,yy+115),fill=BLUE)
    d.rectangle((x+old*scale,yy,x+(old+add)*scale,yy+115),fill=ORANGE)
    text(d,531,yy-90,label,42,BLUE,True)
    text(d,531,yy+155,f'得到 {total}°C',42,GREEN,True)
legend(d,1180,[('旧温差留下的',BLUE),('本秒新增加的',ORANGE)])
save(im,'04-retain-and-add.png','Two noiseless steps decomposed into retained temperature and new input')
#05 parameter intersection
im,d=canvas('05','两条不同的信息，钉住两个参数',1300)
p=plot(d,(170,370,950,950),[],(0,1),(0,1),[0,.5,1],[0,.5,1],'参数 a（每秒保留比例）','参数 b / °C')
d.line([p(0,.4),p(1,.4)],fill=ORANGE,width=7);d.line([p(0,.72),p(1,.32)],fill=BLUE,width=7)
x,y=p(.8,.4);dot(d,x,y,GREEN,17);text(d,620,490,'(0.8,0.4)',40,GREEN)
text(d,531,190,'第一秒：b=0.4',44,ORANGE,True)
text(d,531,250,'第二秒：0.4a+b=0.72',44,BLUE,True)
text(d,531,1150,'相交的位置：a=0.8，b=0.4',42,GREEN,True)
save(im,'05-two-equations.png','Parameter-plane intersection of the first two noiseless observations')
#06 noise residual one scene
im,d=canvas('06','有扰动时，不会每条等式都严丝合缝',1330)
text(d,531,185,'y[k+1] = a y[k] + b u[k] + w[k]',42,BLUE,True)
xs=list(range(31));y=R['train']['y'][:31];pred=[y[0]]+R['train_metrics']['one_step'][:30]
plot(d,(170,400,950,900),[(xs,y,BLUE),(xs,pred,ORANGE)],(0,30),(-.1,2),[0,10,20,30],[0,1,2])
legend(d,1080,[('模型生成记录',BLUE),('拟合后一步预测',ORANGE)])
text(d,531,1190,'曲线之间的小差，叫预测残差',40,GREEN,True)
save(im,'06-noisy-observations.png','First 30 training transitions and actual fitted one-step predictions')
#07 loss plane
im,d=canvas('07','让全部残差的平方和尽量小',1390)
x0,y0,x1,y1=210,380,930,1100;amin,amax=.65,.95;bmin,bmax=.25,.55;N=72
u=R['train']['u'];ys=R['train']['y'];loss=[]
for j in range(N):
    row=[];bb=bmax-(j+.5)*(bmax-bmin)/N
    for i in range(N):
        aa=amin+(i+.5)*(amax-amin)/N;row.append(sum((z-aa*y-bb*v)**2 for y,v,z in zip(ys[:-1],u,ys[1:]))/len(u))
    loss.append(row)
lo=min(map(min,loss));hi=max(map(max,loss))
for j in range(N):
 for i in range(N):
    q=(math.log(loss[j][i])-math.log(lo))/(math.log(hi)-math.log(lo));c=tuple(round(a+(b-a)*q)for a,b in zip((38,111,151),(242,232,190)));d.rectangle((x0+i*10,y0+j*10,x0+(i+1)*10,y0+(j+1)*10),fill=c)
for v in [.65,.8,.95]:text(d,x0+(v-amin)/(amax-amin)*720,1130,str(v),36,MUTED,True)
for v in [.25,.4,.55]:text(d,130,y1-(v-bmin)/(bmax-bmin)*720-25,str(v),36,MUTED,True)
text(d,531,200,'深蓝更小，浅色更大；颜色是对数尺度',38,BLUE,True)
text(d,80,290,'b / °C',40,BLUE);text(d,531,1210,'a：每秒保留比例',40,BLUE,True)
a,b=R['fit']['a'],R['fit']['b'];xx=x0+(a-amin)/(amax-amin)*720;yy=y1-(b-bmin)/(bmax-bmin)*720
d.line((xx-20,yy,xx+20,yy),fill=WHITE,width=7);d.line((xx,yy-20,xx,yy+20),fill=WHITE,width=7)
text(d,531,1290,f'白十字：a≈{a:.4f}，b≈{b:.4f}',40,GREEN,True)
save(im,'07-squared-error-landscape.png','Actual training mean-square-loss surface, log color scale, and fitted parameter point')
#08 steady rank collapse
im,d=canvas('08','一万次相同读数，也可能只有一条信息',1320)
p=plot(d,(170,400,950,950),[],(0,1),(0,2),[0,.5,1],[0,1,2],'参数 a','参数 b / °C')
d.line([p(0,2),p(1,0)],fill=BLUE,width=8)
for row,col in zip(R['steady']['candidates'],[ORANGE,BLUE,GREEN]):dot(d,*p(row['a'],row['b']),col,17)
text(d,531,185,'每次都读到：u=1，y=2',44,BLUE,True)
text(d,531,260,'只能得到 2a + b = 2',48,GREEN,True)
text(d,531,1145,'整条线都符合；缺的是区分它们的变化',38,ORANGE,True)
save(im,'08-steady-ambiguity.png','One steady relation leaves a line of parameter candidates')
#09 full train two panes
im,d=canvas('09','输入有变化，输出的记忆才显出来',1640)
u=R['train']['u'];ys=R['train']['y'];xs=list(range(120))
stepx=[];stepy=[]
for k,v in enumerate(u):stepx.extend([k,k+1]);stepy.extend([v,v])
plot(d,(170,350,950,650),[(stepx,stepy,ORANGE)],(0,120),(0,1),[0,40,80,120],[0,1],ylab='输入 u（0或1）')
plot(d,(170,1060,950,1400),[(list(range(121)),ys,BLUE)],(0,120),(-.1,2.2),[0,40,80,120],[0,1,2])
text(d,531,180,'训练：120个1秒区间；每5秒可换输入',38,BLUE,True)
text(d,531,1550,'输出没有立刻跟着开关跳到终点',40,GREEN,True)
save(im,'09-training-input-output.png','Actual normalized training input and simulated noisy output on aligned time axes')
#10 independent validation
im,d=canvas('10','换一段新输入，再让模型独自作答',1960)
y=R['validation']['y'];v=R['validation_metrics'];xs=list(range(81))
vu=R['validation']['u'];sx=[];sy=[]
for k,uk in enumerate(vu):sx.extend([k,k+1]);sy.extend([uk,uk])
plot(d,(170,350,950,620),[(sx,sy,ORANGE)],(0,80),(0,1),[0,20,40,60,80],[0,.5,1],ylab='验证输入 u')
plot(d,(170,1040,950,1550),[(xs,y,BLUE),(xs,v['free_run'],GREEN),(list(range(1,81)),v['static'],ORANGE)],(0,80),(-.1,2.2),[0,20,40,60,80],[0,1,2])
text(d,531,190,'80秒独立验证；不再调整a、b',42,BLUE,True)
legend(d,1730,[('记录',BLUE),('动态模型',GREEN),('静态模型',ORANGE)])
text(d,531,1830,f"自由运行误差 {v['free_run_rmse']:.4f}°C",40,GREEN,True)
text(d,531,1890,f"静态误差 {v['static_rmse']:.4f}°C",40,ORANGE,True)
save(im,'10-heldout-simulation.png','Heldout noisy output versus autonomous dynamic and fitted static models')
#11 distinction
im,d=canvas('11','预测下一秒，和独自跑完整段',1400)
box(d,(80,190,982,345),['一步预测','每次拿实际 y[k] 作起点'],BLUE,size=44)
for k in range(3):
 x=100+k*320;box(d,(x,420,x+250,560),[f'y[{k}]'],BLUE);arrow(d,[(x+125,575),(x+125,650)],BLUE);box(d,(x,670,x+250,810),[f'预测{k+1}'],GREEN,size=38)
text(d,531,900,'每一步都被实际记录重新拉回',40,BLUE,True)
box(d,(80,1000,982,1190),['自由运行','初值 → 预测1 → 预测2 → 预测3'],ORANGE,size=40)
text(d,531,1270,'后续状态由模型自己的上一步提供',38,ORANGE,True)
save(im,'11-prediction-versus-simulation.png','Different information feeds for one-step prediction and free-run simulation')
#12 residual traces
im,d=canvas('12','看剩下的误差，有没有没学会的规律',1550)
v=R['validation_metrics'];xs=list(range(1,81))
plot(d,(170,350,950,710),[(xs,v['residuals'],GREEN)],(0,80),(-1.5,1.5),[0,40,80],[-1,0,1],ylab='动态模型残差 / °C')
plot(d,(170,1050,950,1410),[(xs,v['static_residuals'],ORANGE)],(0,80),(-1.5,1.5),[0,40,80],[-1,0,1],ylab='静态模型残差 / °C')
text(d,531,180,'两面板使用相同纵轴；残差=记录−预测',38,BLUE,True)
save(im,'12-residual-time-patterns.png','Actual heldout one-step residual traces on equal vertical scales')
#13 Monte Carlo
im,d=canvas('13','换一份扰动，参数也会轻轻移动',1370)
rows=R['repeats'];av=[r['a']for r in rows];bv=[r['b']for r in rows];amin=min(av)-.003;amax=max(av)+.003;bmin=min(bv)-.003;bmax=max(bv)+.003
p=plot(d,(180,390,950,990),[],(amin,amax),(bmin,bmax),[round(amin+.005,2),.8,round(amax-.005,2)],[round(bmin+.005,2),.4,round(bmax-.005,2)],'估计的 a','估计的 b / °C')
for row in rows:dot(d,*p(row['a'],row['b']),BLUE,7)
x,y=p(.8,.4);d.line((x-20,y,x+20,y),fill=RED,width=7);d.line((x,y-20,x,y+20),fill=RED,width=7)
text(d,531,185,'相同输入，100份独立模型扰动',42,BLUE,True)
legend(d,1160,[('100次估计',BLUE),('生成参数',RED)])
text(d,531,1260,'散点是本次重复试验，不是置信区间',38,MUTED,True)
save(im,'13-noise-repeat-parameters.png','Actual 100-seed repeated estimates under identical input and noise law')
#14 residual lag
im,d=canvas('14','相邻残差，还像在互相接力吗？',1330)
p=plot(d,(170,380,950,1000),[],(0,9),(-.5,1),[1,2,4,6,8],[-.5,0,.5,1],'滞后 / 采样步','样本残差自相关')
for k,(x,y) in enumerate(zip(v['residual_autocorrelation'],v['static_residual_autocorrelation']),1):
 for offset,value,col in [(-.12,x,GREEN),(.12,y,ORANGE)]:
    xx,yy=p(k+offset,value);zero=p(k+offset,0)[1];d.line((xx,zero,xx,yy),fill=col,width=17)
legend(d,1150,[('动态模型',GREEN),('静态模型',ORANGE)])
text(d,531,1240,'有限样本不要求恰好为0；此图未作显著性检验',36,MUTED,True)
save(im,'14-residual-lag-correlation.png','Actual demeaned sample residual autocorrelations at lags1..8, no significance bands')
#15 extrapolation
im,d=canvas('15','训练范围之外，另一种机器也说得通',1430)
e=R['extrapolation'];xs=list(range(21))
plot(d,(170,410,950,1000),[(xs,e['linear_y'],BLUE),(xs,e['saturated_y'],ORANGE)],(0,20),(0,4),[0,5,10,15,20],[0,2,4])
text(d,531,190,'新输入u=2：已经超过训练的0到1',40,RED,True)
legend(d,1180,[('线性继续增加',BLUE),('功率在1饱和',ORANGE)])
text(d,531,1290,'两种无扰动模型在训练范围内完全相同',38,MUTED,True)
text(d,531,1350,'原数据不能替你决定范围外哪种才是真实',38,RED,True)
save(im,'15-out-of-range-ambiguity.png','Two synthetic models identical on training input range diverge under out-of-range input')
#cover
im,d=canvas('cover','问机器一个好问题，比多记几行更重要',1062)
text(d,531,200,'系统辨识',68,BLUE,True,True)
box(d,(80,350,370,530),['改变输入'],ORANGE,size=42);box(d,(670,350,982,530),['观察输出'],BLUE,size=42)
arrow(d,[(395,440),(640,440)],GREEN)
for j,h in enumerate([35,95,170,220,255,280]):
 x=200+j*120;d.rectangle((x,860-h,x+70,860),fill=BLUE)
text(d,531,930,'从成对记录，寻找能经受新实验的模型',38,GREEN,True)
im.save(O/'cover.png');metadata.append(dict(file='cover.png',width=W,height=1062,min_font_px=38,min_effective_px_at_354=38/3,role='Separate original system-identification cover',identity='original illustration'))
(O/'examples').mkdir(exist_ok=True);(O/'examples/figure-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
print('Drew 15 body figures and a separate cover')
