#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original timing diagrams and actual numerical plots; no fake instrument screenshots."""
from pathlib import Path
import argparse,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];A=P/'assets';A.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--data',required=True);args=p.parse_args();DATA=Path(args.data)
R=json.loads((DATA/'results.json').read_text());Z=np.load(DATA/'comparisons.npz')
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
W=1062;BG='#f5f3eb';INK='#243843';TEAL='#087d82';BLUE='#367daf';ORANGE='#c16a26';RED='#b64b56';GRAY='#6a7679';meta=[]
def font(s=42,b=False):return ImageFont.truetype(BOLD if b else FONT,s,index=2)
def text(x,y,t,s=42,c=INK,b=False,anchor=None):
 global smallest
 smallest=min(smallest,s);d.text((x,y),str(t),font=font(s,b),fill=c,anchor=anchor)
def line(points,c=INK,w=5):d.line(points,fill=c,width=w)
def box(x,y,w,h,fill='white',stroke=None,r=18):d.rounded_rectangle((x,y,x+w,y+h),r,fill,stroke,width=3)
def arrow(x1,y1,x2,y2,c=TEAL,w=6,tip=18):
 line([(x1,y1),(x2,y2)],c,w);ang=math.atan2(y2-y1,x2-x1)
 d.polygon([(x2,y2),(x2-tip*math.cos(ang-.5),y2-tip*math.sin(ang-.5)),(x2-tip*math.cos(ang+.5),y2-tip*math.sin(ang+.5))],fill=c)
def dot(x,y,c=TEAL,r=10):d.ellipse((x-r,y-r,x+r,y+r),fill=c)
def new(title,h=1000,sub=None):
 global im,d,smallest
 smallest=99;im=Image.new('RGB',(W,h),BG);d=ImageDraw.Draw(im);d.rectangle((0,0,16,h),fill=TEAL);text(48,32,title,52,b=True)
 if sub:text(48,111,sub,38,c=GRAY)
def save(n,purpose,evidence='Original teaching diagram'):
 im.save(A/(n+'.png'));meta.append(dict(file='assets/'+n+'.png',purpose=purpose,evidence=evidence,width=W,height=im.height,minimum_font_px=smallest,effective_minimum_at_354px=smallest/3))
def interp_output(t,key='main'):
 rows=R[key];return np.interp(t,[a['time'] for a in rows],[a['output_phase']for a in rows])
def pulses(phase,t,x0,y0,width=858,amp=70,col=TEAL):
 vals=(np.mod(phase,1)<.2).astype(float);pts=[(x0+(tt-t[0])/(t[-1]-t[0])*width,y0-aa*amp)for tt,aa in zip(t,vals)];line(pts,col,5)
def time_axis(t0,t1,y,x=145,w=855,step=1):
 line([(x,y),(x+w,y)],GRAY,3)
 for t in np.arange(math.ceil(t0/step)*step,t1+1e-8,step):
  xx=x+(t-t0)/(t1-t0)*w;line([(xx,y),(xx,y+12)],GRAY,3);text(xx,y+17,f'{t:g}',36,anchor='mt')
def chart(x,y,w,h,xlim,ylim,xticks,yticks,curves,xlabel='时间 / 秒',ylabel=None):
 for v in yticks:
  yy=y+h-(v-ylim[0])/(ylim[1]-ylim[0])*h;line([(x,yy),(x+w,yy)],'#d5dddd',2);text(x-15,yy,f'{v:g}',36,c=GRAY,anchor='rm')
 for v in xticks:
  xx=x+(v-xlim[0])/(xlim[1]-xlim[0])*w;line([(xx,y),(xx,y+h)],'#e0e5e1',2);text(xx,y+h+16,f'{v:g}',36,c=GRAY,anchor='mt')
 line([(x,y),(x,y+h),(x+w,y+h)],GRAY,3)
 for xx,yy,col in curves:
  pts=[(x+(a-xlim[0])/(xlim[1]-xlim[0])*w,y+h-(b-ylim[0])/(ylim[1]-ylim[0])*h)for a,b in zip(xx,yy) if xlim[0]-1e-8<=a<=xlim[1]+1e-8]
  if pts:line(pts,col,6)
 if xlabel:text(x+w,y+h+71,xlabel,38,anchor='rt')
 if ylabel:text(x,y-60,ylabel,42,b=True)

new('同一台本地振荡器，逐渐跟上参考',1160,'实际教学仿真；高低变化表示周期脉冲')
for top,(lo,hi,title) in [(210,(0,3,'刚开始：边沿还没有对齐')),(700,(24,27,'后来：边沿接近对齐'))]:
 text(48,top-31,title,44,b=True);t=np.linspace(lo,hi,2001)
 text(48,top+95,'参考',40,c=GRAY);text(48,top+250,'本地',40,c=TEAL)
 pulses(.25+t,t,145,top+135,col=GRAY);pulses(interp_output(t),t,145,top+290,col=TEAL)
 time_axis(lo,hi,top+320)
text(48,1081,'显示的是计算波形，不是示波器实测。',39)
save('01-actual-locking','同一运行的初期与后期边沿，给出可感知的锁定对象','results.json main output phase, piecewise linear interpolation')

new('一秒重复几次，叫频率',1120,'独立示意：两串脉冲，不是主实验的两路输入')
t=np.linspace(0,2,2001)
for y,f,lab in [(445,1,'1 Hz：每秒 1 次'),(895,2,'2 Hz：每秒 2 次')]:
 text(48,y-251,lab,46,b=True);pulses(f*t,t,145,y,width=855,amp=95,col=TEAL if f==1 else BLUE);time_axis(0,2,y+25,step=.5)
 pwidth=855/(2*f);arrow(145,y-110,145+pwidth,y-110,ORANGE,5);text(145+pwidth/2,y-176,'周期 '+('1'if f==1 else'0.5')+' 秒',39,c=ORANGE,anchor='mt')
text(48,1032,'周期是一次要多久；频率是每秒多少次。',39)
save('03-period-frequency','把Hz、周期、时间轴与实际重复次数连在一起')

new('频率相同，也可能一直晚一点',820,'两者都是 1 Hz；下路每个上升沿都晚 0.25 秒')
t=np.linspace(0,3,2401)
for y,ph,lab,col in [(350,t,'参考',GRAY),(560,t-.25,'本地',TEAL)]:
 text(48,y-65,lab,40,c=col);pulses(ph,t,145,y,amp=85,col=col)
for tt in [1,2]:
 x=145+tt/3*855;x2=145+(tt+.25)/3*855
 line([(x,210),(x,610)],'#aeb9ba',3);line([(x2,420),(x2,610)],TEAL,3)
arrow(145+855/3,408,145+1.25/3*855,408,ORANGE,5,13)
text(48,683,'时间差 0.25 秒，占一个周期的 1/4。',40)
time_axis(0,3,601);text(48,755,'这个“走到哪里”的差别，就是相位差。',39)
save('04-same-frequency-phase','同周期固定延迟的边沿，区别频率一致和零相差')

new('频率差一点，早晚就会不断累积',850,'独立示意：开始时同相，之后不作任何反馈校正')
t=np.linspace(0,5,3501)
for y,f,lab,col in [(355,1,'1 Hz',GRAY),(600,.8,'0.8 Hz',TEAL)]:
 text(48,y-67,lab,40,c=col);pulses(f*t,t,145,y,amp=90,col=col)
for k in [1,2,3,4]:
 xr=145+k/5*855;xo=145+(k/.8)/5*855;line([(xr,366),(xo,490)],ORANGE,4)
time_axis(0,5,648)
text(48,757,'橙线连接同序号的周期，间隔越拉越开。',39)
save('05-frequency-drift','累计相差由频差产生；连接同序号周期避免混数')

new('把一圈当作 1，相位就能记成数',1120,'这不是机械钟表；圆只是周期进度的画法')
cx=530;cy=480;rr=230
d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline='#9daaa9',width=5)
for ph,label in [(0,'0 / 1'),(.25,'0.25'),(.5,'0.5'),(.75,'0.75')]:
 x=cx+rr*math.cos(2*math.pi*ph);y=cy-rr*math.sin(2*math.pi*ph);dot(x,y,GRAY,7)
 text(cx+(rr+77)*math.cos(2*math.pi*ph),cy-(rr+65)*math.sin(2*math.pi*ph),label,44,anchor='mm')
arrow(cx,cy,cx+rr,cy,TEAL,9);arrow(cx,cy,cx,cy-rr,ORANGE,9)
text(48,879,'绿：本地 0 圈；橙：参考 0.25 圈',43,b=True)
text(48,956,'参考领先 0.25 圈，本地要加快去追。',41)
text(48,1032,'转满一圈又回到 0，但总转数可以继续数。',37,c=GRAY)
save('06-phase-circle','引入圈作为相位单位，和参考领先误差符号绑定')

new('只看一圈内的位置，要会跨过零点',980,'同一个周期上的 0.98 与 0.02，其实很近')
cx=531;cy=450;rr=230;d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline='#a7b5b1',width=5)
for ph,col,lab,yoff in [(.98,TEAL,'本地 0.98',100),(.02,ORANGE,'参考 0.02',-120)]:
 x=cx+rr*math.cos(2*math.pi*ph);y=cy-rr*math.sin(2*math.pi*ph);dot(x,y,col,12);line([(x,y),(860,y+yoff)],col,4);text(850,y+yoff,lab,40,c=col,anchor='rt')
text(48,757,'直接相减：0.02 − 0.98 = −0.96',44)
text(48,834,'跨过零点：等价的短差是 +0.04 圈',43,c=ORANGE,b=True)
text(48,908,'本文把误差折回 −0.5 到 0.5 圈之间。',38)
save('07-wrapped-error','具体跨周期例解释wrap误差与测量歧义，而非把负误差一律当后退')

new('比较早晚，再把误差送回去调速',1250,'主例不分频；反馈的是本地相位读数')
box(48,200,440,137,'#e6ece8');text(268,230,'参考相位',46,b=True,anchor='mt')
arrow(268,347,268,415)
box(48,430,440,190,'#d8e9e4');text(268,451,'比较器',47,b=True,anchor='mt');text(268,531,'参考 − 本地',40,anchor='mt')
box(591,320,423,195,'#e6e0d3');text(802,344,'当前 + 累计',44,b=True,anchor='mt');text(802,419,'得到频率修正',40,anchor='mt')
arrow(500,512,575,420,ORANGE);text(510,552,'误差',38,c=ORANGE)
arrow(802,525,802,606)
box(591,620,423,185,'#dce8ef');text(802,642,'受控振荡器',44,b=True,anchor='mt');text(802,710,'快慢由修正量决定',37,anchor='mt')
arrow(802,815,802,893)
box(591,908,423,148,'#e7eee9');text(802,950,'新的本地相位',41,b=True,anchor='mt')
line([(576,982),(266,982),(266,670)],TEAL,7);arrow(266,670,266,636,TEAL,7)
text(48,1090,'输出再回来，下一次继续比较。',44,b=True)
text(48,1170,'这就是锁相环里的“环”。',41)
save('08-loop-structure','可追踪的反馈通路，把鉴相、PI和相位推进接起来')

new('第 0 次检查：把数字真的算一次',1180,'参考 0.25 圈，本地 0 圈，累计修正从 0 开始')
items=[('相位误差','0.25 − 0 = 0.25 圈'),('按当前误差纠偏','1 × 0.25 = 0.25 Hz'),('先更新累计量','0 + 0.5 × 0.1 × 0.25'),('累计量的新值','= 0.0125 Hz'),('决定下一小段频率','0.8 + 0.25 + 0.0125'),('结果','= 1.0625 Hz')]
for i,(a,b) in enumerate(items):
 y=186+i*156;box(48,y,966,136,'#e4ece7' if i%2==0 else 'white');text(73,y+8,a,38,c=GRAY);text(73,y+64,b,46,b=i==5,c=TEAL if i==5 else INK)
save('09-first-control-step','所有数字单位和更新次序落实到同一0.1秒样本','results.json main[0]')

new('同一过程继续检查，别重置累计量',830,'真实运行记录；这里只显示四舍五入后的读数')
cols=[112,338,583,856]
for x,t in zip(cols,['时间 / 秒','误差 / 圈','累计 / Hz','频率 / Hz']):text(x,211,t,37,b=True,anchor='mt')
for j,row in enumerate(R['main'][:3]):
 y=330+j*133;box(48,y-10,966,108,'#e4ece7'if j%2==0 else'white')
 vals=[f"{row['time']:.1f}",f"{row['error']:.5f}",f"{row['integral_after']:.5f}",f"{row['frequency']:.5f}"]
 for x,val in zip(cols,vals):text(x,y+16,val,40,anchor='mt')
text(48,739,'每行频率，作用于紧接着的 0.1 秒。',41)
save('10-three-checks','实际前三行不把误差瞬间消失；累计项逐步积累','results.json main[0:3]')

new('追上以后，频率和相差都趋于稳定',1300,'同一次主运行；灰线是目标，绿线是本地结果')
rows=R['main'];tt=np.array([q['time']for q in rows]);ff=np.array([q['frequency']for q in rows]);ee=np.array([q['error']for q in rows])
chart(160,230,840,310,(0,30),(.78,1.14),[0,10,20,30],[.8,1.,1.1],[(tt,ff,TEAL),(tt,np.ones_like(tt),GRAY)],ylabel='输出频率 / Hz')
chart(160,830,840,300,(0,30),(-.035,.27),[0,10,20,30],[0,.1,.25],[(tt,ee,TEAL),(tt,np.zeros_like(tt),GRAY)],ylabel='参考减本地的相差 / 圈')
text(48,1230,'本地原本自由频率 0.8 Hz，最后接近 1 Hz。',37)
save('11-lock-transient','分开画频率和相位误差，使锁定和初期调整可观察','results.json main')

new('同频锁定，可以还差一个固定相位',1250,'主模型后期对比：只看当前误差，或再加累计项')
t=np.linspace(24,27,2501)
for top,key,lab in [(240,'ponly','只用当前误差：持续落后 0.2 圈'),(745,'main','当前 + 累计：相差趋近 0')]:
 text(48,top-55,lab,42,b=True);pulses(.25+t,t,145,top+125,col=GRAY);pulses(interp_output(t,key),t,145,top+280,col=TEAL)
 text(48,top+50,'参考',37,c=GRAY);text(48,top+210,'本地',37,c=TEAL);time_axis(24,27,top+315)
text(48,1172,'两种情况的输出频率都已接近 1 Hz。',39)
save('12-p-only-phase-offset','P与PI相位波形实证固定相差与锁定不冲突','results.json ponly/main phase24..27')

new('输出除以 4 再比较，会发生什么？',1100,'独立稳态示意：所有波形共用一条时间轴')
t=np.linspace(0,2,4001)
for y,f,lab,col in [(370,4,'输出 4 Hz',TEAL),(665,1,'除 4 反馈',BLUE),(905,1,'参考 1 Hz',GRAY)]:
 text(48,y-(195 if f==4 else 148),lab,43,b=True,c=col);pulses(f*t,t,145,y,amp=85,col=col)
for k in range(4):text(145+(k+.5)/8*855,246,str(k+1),37,c=TEAL,anchor='mt')
arrow(500,405,500,490,ORANGE);text(570,424,'4 个周期 → 1 个周期',38,c=ORANGE)
time_axis(0,2,952,step=.5)
save('13-divider-multiplier','数同一时间窗周期数，把反馈除N推到输出N倍而不称脉冲被凭空复制')

new('追得快，还是改得慢？',1070,'另一次实验：第 30 秒，参考从 1 变成 1.2 Hz')
t=Z['tracking_fast_time'];rf=Z['tracking_fast_reference_frequency']
chart(160,260,840,515,(28,58),(.98,1.24),[30,40,50],[1,1.1,1.2],[(t,rf,GRAY),(t,Z['tracking_fast_frequency'],BLUE),(t,Z['tracking_slow_frequency'],ORANGE)],ylabel='输出频率 / Hz')
text(48,901,'蓝：快环路；橙：慢环路；灰：参考',39)
text(48,971,'进入并保持 ±0.01 Hz：约 4.12 / 20.72 秒',37)
save('14-tracking-speed','相同参考频率变化下的两组增益响应和明确误差带','comparisons.npz tracking; results.json tests')

new('噪声从哪里进来，结论就可能相反',1080,'下面把两种扰动分开实验，不混成一个“抖动”')
for y,title,label,fill in [(218,'实验 A：参考端被扰动','给参考相位加小幅快摆动','#e5e0cf'),(625,'实验 B：本地振荡器被扰动','给自由频率加小幅慢摆动','#dce9eb')]:
 box(48,y,966,310,fill);text(83,y+22,title,46,b=True)
 text(83,y+95,label,39)
 box(83,y+172,330,91,'white');text(248,y+190,'参考 → 比较',38,anchor='mt')
 arrow(425,y+218,601,y+218,TEAL);box(620,y+172,350,91,'white');text(795,y+190,'本地振荡器',38,anchor='mt')
 if y<300:arrow(246,y+151,246,y+174,ORANGE,7,13)
 else:arrow(795,y+151,795,y+174,ORANGE,7,13)
text(48,1001,'橙色小箭头标出扰动加入的位置。',41)
save('15-two-noise-sources','先把参考端与本振内的噪声加入位置分开，避免窄带全能误解')

new('同样两种环路，噪声结果会对调',1370,'纵轴：输出相位波动的均方根，单位是圈')
nr=R['tests']['noise_rms_cycles']
for top,source,title,ymax in [(300,'reference_phase','A：参考相位受到扰动',.01),(900,'local_frequency','B：本振自由频率受到扰动',.06)]:
 text(48,top-110,title,43,b=True)
 x=205;w=700;h=285
 for val in [0,ymax/2,ymax]:
  yy=top+h-val/ymax*h;line([(x,yy),(x+w,yy)],'#d0d8d4',2);text(x-15,yy,f'{val:g}',36,anchor='rm')
 for bx,speed,col,lab in [(340,'fast',BLUE,'快环路'),(730,'slow',ORANGE,'慢环路')]:
  v=nr[source][speed];yy=top+h-v/ymax*h;box(bx-95,yy,190,top+h-yy,col,None,0)
  text(bx,yy-56,f'{v:.5f}',40,c=col,b=True,anchor='mt');text(bx,top+h+24,lab,40,anchor='mt')
text(48,1304,'注意：A、B 两组纵轴范围不同，各组内相同。',36,c=GRAY)
save('16-noise-tradeoff','同一快慢环路对两种明确扰动的计算RMS，标清不同纵轴','results.json tests.noise_rms_cycles; 100<=t<125')

new('只在采样点合拍，未必真的同频',1210,'反例仅针对本文简化鉴相器，不代表所有 PLL')
t=np.linspace(0,1,4401)
for top,f,lab,col in [(300,1,'参考：每秒 1 圈',GRAY),(780,11,'本地：每秒 11 圈',TEAL)]:
 text(48,top-61,lab,45,b=True)
 vals=np.mod(f*t,1)
 chart(160,top,840,235,(0,1),(0,1),[0,.5,1],[0,1],[(t,vals,col)],xlabel='时间 / 秒')
 for ts in np.arange(0,1.00001,.1):dot(160+ts*840,top+235-(ts%1)*235,RED,9)
text(48,1128,'红点每 0.1 秒查一次，两路圈内读数相同。',38)
save('17-sampling-alias','具体1Hz/11Hz采样混叠揭示短相差测量不能担保任意捕获','results.json alias, all measured error near0')

new('让芯片里的时钟',1062);text(48,117,'追上参考节拍',62,b=True);text(48,232,'锁相环：比较、纠偏，再比较',40,c=TEAL)
t=np.linspace(24,27,2201)
box(48,359,966,562,'#e2ebe6')
pulses(.25+t,t,102,560,width=858,amp=100,col=GRAY);pulses(interp_output(t),t,102,800,width=858,amp=100,col=TEAL)
text(78,395,'参考',40,c=GRAY);text(78,639,'本地',40,c=TEAL)
im.save(P/'cover.png');meta.append(dict(file='cover.png',purpose='独立封面：主实验锁定后真实计算波形',evidence='results.json main24..27',width=W,height=1062,minimum_font_px=40,effective_minimum_at_354px=40/3))
(P/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print('rendered',len(meta),'original images including cover')
