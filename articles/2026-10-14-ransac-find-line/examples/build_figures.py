#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original diagrams and recorded numerical results; real photo transformations explicit."""
from pathlib import Path
import argparse,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'assets';A.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--data',required=True);args=p.parse_args();DATA=Path(args.data)
R=json.loads((DATA/'results.json').read_text());Z=np.load(DATA/'photo-data.npz');P=np.array([[r['x'],r['y']]for r in R['points']]);NAMES=list('ABCDEFGHIJKL')
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc';W=1062
BG='#f5f3eb';INK='#223b45';TEAL='#087d82';ORANGE='#c16522';RED='#b74857';BLUE='#367bad';GRAY='#657378';meta=[]
def font(s=42,b=False):return ImageFont.truetype(BOLD if b else FONT,s,index=2)
def text(x,y,t,s=42,c=INK,b=False,anchor=None):
 global smallest
 smallest=min(smallest,s);d.text((x,y),str(t),font=font(s,b),fill=c,anchor=anchor)
def line(pts,c=INK,w=5):d.line(pts,fill=c,width=w)
def dot(x,y,c=TEAL,r=10):d.ellipse((x-r,y-r,x+r,y+r),fill=c)
def arrow(x1,y1,x2,y2,c=TEAL,w=6):
 line([(x1,y1),(x2,y2)],c,w);ang=math.atan2(y2-y1,x2-x1);d.polygon([(x2,y2),(x2-17*math.cos(ang-.5),y2-17*math.sin(ang-.5)),(x2-17*math.cos(ang+.5),y2-17*math.sin(ang+.5))],fill=c)
def new(title,h=1100,sub=None):
 global im,d,smallest
 smallest=99;im=Image.new('RGB',(W,h),BG);d=ImageDraw.Draw(im);d.rectangle((0,0,16,h),fill=TEAL);text(48,30,title,52,b=True)
 if sub:text(48,111,sub,38,c=GRAY)
def save(n,purpose,kind='Original explanatory diagram'):
 im.save(A/(n+'.png'));meta.append(dict(file='assets/'+n+'.png',purpose=purpose,evidence=kind,width=W,height=im.height,minimum_font_px=smallest,effective_minimum_at_354px=smallest/3))
def axes(y=230,h=610,xlim=(-.5,7.5),ylim=(-1,16),xticks=(0,2,4,6),yticks=(0,5,10,15),xlabel='x / 教学单位',ylabel='y / 教学单位'):
 x=142;w=850
 def xy(a,b):return (x+(a-xlim[0])/(xlim[1]-xlim[0])*w,y+h-(b-ylim[0])/(ylim[1]-ylim[0])*h)
 for a in xticks:
  xx=xy(a,0)[0];line([(xx,y),(xx,y+h)],'#d9dfdc',2);text(xx,y+h+14,f'{a:g}',36,anchor='mt')
 for b in yticks:
  yy=xy(0,b)[1];line([(x,yy),(x+w,yy)],'#d9dfdc',2);text(x-17,yy,f'{b:g}',36,anchor='rm')
 line([(x,y),(x,y+h),(x+w,y+h)],GRAY,3);text(x,y-56,ylabel,38,b=True);text(x+w,y+h+60,xlabel,38,anchor='rt')
 return xy,(xlim,ylim)
def model(xy,bounds,ab,col=TEAL,w=6):
 (xl,xh),(yl,yh)=bounds;a,b=ab;xx=[xl,xh]
 if a!=0:xx.extend([(yl-b)/a,(yh-b)/a])
 good=sorted(set(round(v,12)for v in xx if xl-1e-9<=v<=xh+1e-9 and yl-1e-8<=a*v+b<=yh+1e-8))
 if len(good)>=2:line([xy(good[0],a*good[0]+b),xy(good[-1],a*good[-1]+b)],col,w)
def points(xy,mask=None,labels=False,p=P,label_offsets=None):
 offsets={'A':(14,0),'B':(-39,-40),'C':(14,-48),'D':(-40,-47),'E':(14,-10),'F':(15,-6),'G':(-44,-46),'H':(12,-40),'I':(16,-35),'J':(14,-35),'K':(14,0),'L':(14,-5)}
 if label_offsets:offsets.update(label_offsets)
 for i,(x,y)in enumerate(p):
  xx,yy=xy(x,y);dot(xx,yy,GRAY if mask is None else TEAL if mask[i] else RED,11)
  if labels:
   dx,dy=offsets[NAMES[i]];text(xx+dx,yy+dy,NAMES[i],38,b=True)
def legend(y,items):
 for x,(lab,col)in zip([48,560],items):line([(x,y+24),(x+55,y+24)],col,7);text(x+72,y,lab,38,c=col)

new('混了干扰点，直线会被拉向哪里？',1050,'同一组 12 点；两条线都来自实际运行')
xy,b=axes();model(xy,b,R['main']['all_ols_ab'],ORANGE);model(xy,b,R['main']['refit_ab'],TEAL);points(xy)
legend(971,[('全部点一起拟合',ORANGE),('先找支持者再拟合',TEAL)])
save('01-fit-comparison','看见全点最小二乘与RANSAC在相同数据上的不同结果','results.json main')

new('真实输入：四座桥的航拍照片',1635,'框中是人工指定的近景桥局部')
photo=Image.fromarray(Z['rgb']).resize((1008,1344),Image.Resampling.LANCZOS);im.paste(photo,(27,185));d=ImageDraw.Draw(im)
sx=1008/1080;sy=1344/1440;box=(27+100*sx,185+880*sy,27+1050*sx,185+1000*sy);d.rectangle(box,outline='#ffd65c',width=8)
text(48,1561,'Joel M. Galloway / USGS · Public Domain',36)
save('02-real-photo-roi','完整真图提供现实对象，并显式标记人为限定的输入区域','USGS original photo resized; rectangle added; original retained')

new('先让一堆点有名字和坐标',1100,'所有点先用同色：程序还不知道谁属于哪条线')
xy,b=axes(h=620);points(xy,labels=True)
text(48,984,'A = (0, 1)：向右 0，向上 1。',42)
text(48,1040,'F = (5, 11)：向右 5，向上 11。',42)
save('03-point-coordinates','坐标轴、单位和点名建立同一12点贯穿例子')

new('平方误差，会放大很离谱的偏离',1080,'都相对候选线 y = 2x + 1 计算')
for top,name,x,obs,pred in [(220,'B',1,3.1,3),(540,'L',6.5,4,14)]:
 text(48,top,f'{name} 点：x = {x:g}，观察到 y = {obs:g}',44,b=True)
 text(48,top+75,f'直线预测 {pred:g}；竖直差 {abs(obs-pred):g}',42)
 text(48,top+151,f'平方后：{abs(obs-pred):g} × {abs(obs-pred):g} = {(obs-pred)**2:g}',46,c=TEAL if name=='B'else RED,b=True)
text(48,900,'100 是 0.01 的 10,000 倍。',48,b=True)
text(48,988,'这解释了“少数远点也可能很有分量”。',40)
save('04-squared-residual','用同组B与L代入平方，解释全点OLS为何可能受远点影响')

new('只拿 A 和 F，先提出一条线',1120,'斜率：每向右 1，平均向上多少')
xy,b=axes(h=570);model(xy,b,[2,1]);points(xy,mask=[i in[0,5]for i in range(12)])
x0,y0=xy(0,1);xf,yf=xy(5,11);arrow(x0,y0,xf,y0,ORANGE);arrow(xf,y0,xf,yf,ORANGE)
text((x0+xf)/2,y0-63,'向右 5',42,c=ORANGE,anchor='mt');text(xf+25,(y0+yf)/2,'向上 10',40,c=ORANGE)
text(48,943,'斜率 a = 10 ÷ 5 = 2',46,b=True)
text(48,1010,'A 在 x=0 时 y=1，所以 b=1。',43)
save('05-two-point-line','在坐标动作上计算斜率和截距；其余红点只表示未被抽中')

new('投票规则：预测值上下各容许 0.25',1320,'这里的误差沿竖直方向量，不是最短距离')
xy,b=axes(y=230,h=540);model(xy,b,[2,1],TEAL)
for off in[-.25,.25]:model(xy,b,[2,1+off],'#9bc7ba',4)
mask=R['hand_A_F']['mask'];points(xy,mask)
legend(897,[('支持点：误差 ≤ 0.25',TEAL),('不支持这条线',RED)])
text(48,998,'把 B 点附近单独放大：',44,b=True)
xx=400;lo=1210;hi=1080;line([(xx,hi),(xx,lo)],TEAL,14)
for val,yy in[(2.75,lo),(3.,(lo+hi)/2),(3.25,hi)]:
 line([(xx-15,yy),(xx+15,yy)],INK,4);text(xx-37,yy,f'{val:g}',38,anchor='rm')
dot(xx,(lo+hi)/2-.1/.5*(lo-hi),ORANGE,12);text(xx+50,1117,'B 的 3.1 落在允许区间内',39)
save('06-threshold-vote','同一候选的所有点分类，并放大B的实际阈值区间')

new('不同的两点，会提出不同的候选',2410,'三幅图使用相同坐标范围；绿色是本轮支持点')
for top,idx,title in[(190,0,'第 1 轮 E、K：2 票'),(920,1,'第 2 轮 A、F：8 票'),(1650,3,'第 4 轮 J、K：3 票')]:
 text(48,top,title,46,b=True);xy,b=axes(y=top+126,h=440);c=R['main']['rounds'][idx]['candidate'];model(xy,b,c['ab']);points(xy,c['mask'])
text(48,2337,'票多只表示更受这些点支持，尚不等于真相。',39)
save('07-candidate-comparison','坏样本、主结构和另一条小结构逐轮比较','results.json first, second, fourth candidates')

new('每轮都比较，但只保存目前最好',1080,'竖线是本轮票数；绿线是截至该轮的最多票')
xy,b=axes(y=260,h=545,xlim=(.5,12.5),ylim=(0,9),xticks=(1,2,4,6,8,10,12),yticks=(0,2,4,6,8),xlabel='抽样轮次',ylabel='支持点数量 / 个')
last=None
for row in R['main']['rounds']:
 k=row['round'];cnt=row['candidate']['count'];x,y=xy(k,cnt);line([xy(k,0),(x,y)],ORANGE,15)
 if last:line([last,xy(k,row['best_count'])],TEAL,7)
 last=xy(k,row['best_count']);dot(*last,TEAL,8)
text(48,943,'第 2 轮得到 8 票，后面没有更优的候选。',41)
text(48,1008,'同票时，本文再比较支持集内的平方误差。',39)
save('08-rounds-best','实际12轮本轮分数与保存分数区别','results.json main rounds')

new('选出支持者以后，再一起微调',1080,'纵轴改为“相对 y=2x+1 的偏差”，放大细节')
xy,b=axes(y=260,h=500,xlim=(-.5,7.5),ylim=(-.15,.15),xticks=(0,2,4,6),yticks=(-.1,0,.1),xlabel='x / 教学单位',ylabel='y 偏差 / 教学单位')
model(xy,b,[0,0],ORANGE);ab=R['main']['refit_ab'];model(xy,b,[ab[0]-2,ab[1]-1],TEAL)
for x,y in P[:8]:dot(*xy(x,y-(2*x+1)),GRAY,11)
legend(905,[('A、F 两点候选',ORANGE),('8 点共同重拟合',TEAL)])
text(48,998,'最终 y ≈ 1.992857x + 1.025',45,b=True)
save('09-refit-detail','改用明确的偏差坐标看微调，避免原图上几乎重合的两线假装巨大改善','results.json main refit')

new('阈值变了，谁能投票也会变',2410,'只改阈值；三幅都固定同一条 y=2x+1')
for top,t in[(190,.05),(920,.25),(1650,8.)]:
 m=np.abs(P[:,1]-(2*P[:,0]+1))<=t;text(48,top,f'阈值 {t:g}：{int(m.sum())} 个支持点',46,b=True)
 xy,b=axes(y=top+126,h=440);model(xy,b,[2,1]);points(xy,m)
text(48,2337,'这不是重跑搜索，只是在隔离观察阈值的作用。',38)
save('10-threshold-comparison','固定模型隔离阈值，显示太窄排除噪声点、太宽吞进其他结构')

new('随机，不等于只能凭运气猜一次',1260,'以下知道 8 个生成内点，只因数据是我们造的')
text(48,208,'第一点：12 个里有 8 个生成内点',43,b=True)
for i in range(12):dot(86+i*78,331,TEAL if i<8 else RED,24)
text(48,393,'已抽中一个后，剩下 11 个里有 7 个。',41)
for i in range(11):dot(86+i*78,507,TEAL if i<7 else RED,24)
text(48,587,'两点都抽中：8/12 × 7/11 = 14/33',43,b=True)
text(48,666,'约 42.4%；下一轮从完整 12 点重新抽。',39)
q=R['probability']['q'];xy,b=axes(y=853,h=218,xlim=(0,12),ylim=(0,1),xticks=(0,3,6,9,12),yticks=(0,.5,1),xlabel='独立抽样轮数',ylabel='至少一次抽中全内点对的概率')
line([xy(k,1-(1-q)**k)for k in range(13)],TEAL,6);dot(*xy(9,1-(1-q)**9),ORANGE,12)
text(48,1200,'9 轮约 99.30%；不是“模型正确率”。',40,b=True)
save('11-sampling-probability','无放回一轮中的分母变化与跨轮至少一次事件','results.json probability; exact enumeration of66pairs')

new('两个点都来自主结构，也可能画偏',1110,'C、D 只相隔 1；0.2 的相对抖动改变了斜率')
xy,b=axes(y=240,h=565);model(xy,b,[2,1],GRAY);model(xy,b,R['close_C_D']['ab'],ORANGE);points(xy,R['close_C_D']['mask'],labels=True,label_offsets={'C':(-54,-62),'G':(-44,-70),'H':(-5,20)})
legend(931,[('生成线：y=2x+1',GRAY),('C、D 给出的候选',ORANGE)])
text(48,1012,'(7.1−4.9) ÷ (3−2) = 2.2，而不是 2。',42)
save('12-good-pair-can-fail','用真实已知生成内点反例区分抽到好标签和拟合正确','results.json close_C_D')

new('照片中的点，怎样自动提取出来？',1210,'先缩小到 1080×1440，再处理人工框定的局部')
raw=Image.fromarray(Z['rgb']).crop((100,880,1050,1000)).resize((950,120),Image.Resampling.NEAREST);im.paste(raw,(56,223));d=ImageDraw.Draw(im)
xx=56+700-100;line([(xx,208),(xx,358)],ORANGE,5);text(48,397,'橙线：工作图第 x=700 列',42,b=True)
text(48,465,'逐行比较“下一行亮度 − 上一行亮度”的大小。',38)
xy,b=axes(y=641,h=340,xlim=(880,999),ylim=(0,120),xticks=(880,920,960,999),yticks=(0,50,100),xlabel='这一列的 y / 像素，往下增大',ylabel='相邻上下行亮度差的绝对值')
g=Z['profile_gradient'];ys=Z['profile_y'];line([xy(float(y),float(v))for y,v in zip(ys,g)],BLUE,5);k=int(g.argmax());dot(*xy(ys[k],g[k]),ORANGE,13)
text(48,1131,f'最大变化在 y={ys[k]}；这列就交出点 (700, {ys[k]})。',40,b=True)
save('13-photo-edge-points','真实局部、单列灰度差剖面与坐标输出，解释图像到点的转换','Original photo crop, recorded photo-data.npz gradient profile')

new('159 个候选点，找到一条局部影像边缘',1930,'下面全是同一张真实照片的工作分辨率局部')
points_real=np.array(R['photo']['points']);run=R['photo']['run'];crop=(75,840,1070,1030);base=Image.fromarray(Z['rgb']).crop(crop);xoff,yoff=crop[:2]
for top,mask,key,title in[(230,run['best']['mask'],'best','重拟合前：127 点组成最佳支持集'),(680,run['refit_mask'],'final','用这 127 点重拟合，再分类得到 131 点')]:
 text(48,top-61,title,40,b=True);im.paste(base,(33,top));d=ImageDraw.Draw(im)
 ab=run['best']['ab']if key=='best'else run['refit_ab']
 for (x,y),m in zip(points_real,mask):
  color='#21ffcf'if m else'#ff3265';dot(33+x-xoff,top+y-yoff,color,4)
 line([(33+100-xoff,top+ab[0]*100+ab[1]-yoff),(33+1049-xoff,top+ab[0]*1049+ab[1]-yoff)],'#ffe466',3)
 text(48,top+231,'绿点支持；红点不支持；黄线是该次模型。',38)
text(48,1045,'同一局部放大 5 倍：x=170..265，y=912..945',38,b=True)
zoom=Image.fromarray(Z['rgb']).crop((170,912,266,946)).resize((480,170),Image.Resampling.NEAREST)
for left,mask,ab,label in [(33,run['best']['mask'],run['best']['ab'],'重拟合前'),(549,run['refit_mask'],run['refit_ab'],'重拟合后')]:
 text(left,1135,label,41,b=True);im.paste(zoom,(left,1210));d=ImageDraw.Draw(im)
 line([(left,1210+(ab[0]*170+ab[1]-912)*5),(left+475,1210+(ab[0]*265+ab[1]-912)*5)],'#ffe466',4)
 for (x,y),m in zip(points_real,mask):
  if 170<=x<266 and 912<=y<946:dot(left+(x-170)*5,1210+(y-912)*5,'#21ffcf'if m else'#ff3265',8)
text(48,1415,'x=184 的点：绿→红；x=208 的点：红→绿。',38)
text(48,1500,'全部重分类：5 点加入，1 点离开。',45,b=True)
text(48,1579,'像素坐标：x 向右，y 向下。',42)
text(48,1658,'最终 y ≈ −0.00296047x + 929.746775',40,b=True)
text(48,1752,'只是局部影像边缘；没有给这些点标注真值。',38)
text(48,1840,'照片：Joel M. Galloway / USGS · Public Domain',36)
save('14-photo-fit-result','真实候选全部保留，两次mask分别展示，重分类成员不是悄悄变化','results.json photo run; original photo crop and overlays')

new('混进干扰点之后',720,'RANSAC：先找支持者，再一起拟合')
xy,b=axes(y=235,h=330);model(xy,b,R['main']['all_ols_ab'],ORANGE);model(xy,b,R['main']['refit_ab']);points(xy)
im.save(ROOT/'cover.png')
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('body figures',len(meta),'cover',1)
