from pathlib import Path
import math,json,cmath
from figurelib import *
P=Path(__file__).resolve().parent;A=P.parent/'assets';M=[]
def H(f,z=.1):r=f;return (1+2j*z*r)/(1-r*r+2j*z*r)
def H2(f):q=1+2j*.1*f;return q*q/((2*q-f*f)*(q-f*f)-q*q)
fs=[.02+i*.01 for i in range(999)]
D={'model':'base-driven linear mass-spring-damper; two-stage uses coupled equations','m_kg':1,'k_N_m':(2*math.pi)**2,'b_Ns_m':.4*math.pi,'f0_Hz':1,'zeta':.1,'f':fs,'T':[abs(H(f)) for f in fs],'T_damped':[abs(H(f,.5)) for f in fs],'logT':[math.log10(abs(H(f))) for f in fs],'logT2':[math.log10(abs(H2(f))) for f in fs],'time':{}}
for f in [.2,1,5]:
 ts=[i/(200*f) for i in range(601)];D['time'][str(f)]={'t':ts,'input':[math.cos(2*math.pi*f*t) for t in ts],'output':[(H(f)*cmath.exp(2j*math.pi*f*t)).real for t in ts],'ratio':abs(H(f))}
(P/'results.json').write_text(json.dumps(D,ensure_ascii=False,indent=2));D=json.loads((P/'results.json').read_text())
def done(b,n,p):M.append(b.save(A/f'{n:02}.png',p))
def mass(b,x,y):b.rect((x-60,y-35,x+60,y+35));
def spring(b,x,y1,y2):
 pts=[(x,y1)]+[(x+(-1 if i%2 else 1)*22,y1+(y2-y1)*(i+1)/10) for i in range(8)]+[(x,y2)];b.line(pts)
b=Board('同一地面，两种连接');
for x in [250,710]:b.rect((x-150,180,x+150,215),fill=GRAY,outline=GRAY);mass(b,x,470);b.arrow((x-60,150),(x+100,150),ORANGE)
b.line([(250,215),(250,435)],GRAY,14);spring(b,710,215,435);b.text('刚性固定',150,670);b.text('柔性悬挂',605,670);done(b,1,'连接方式对比')
b=Board('支撑输入 y，质量块输出 x');b.rect((130,190,830,230));b.text('支撑 y',370,120);spring(b,350,230,490);b.line([(650,230),(650,330)]);b.rect((610,330,690,405),fill='white');b.line([(650,405),(650,490)]);b.rect((250,490,750,590));b.text('质量 m；位置 x',300,610);b.arrow((300,730),(650,730));b.text('水平向右为正',300,770);b.text('弹簧 k',180,350);b.text('阻尼 b',710,350);done(b,2,'模型和坐标定义')
for n,f,lim,title in [(3,.2,1.2,'慢慢移动：几乎跟着支撑走'),(5,1,6,'共振区：输出可以比输入更大'),(6,5,1.2,'快速输入：质量块来不及跟随')]:
 b=Board(title);d=D['time'][str(f)];plot(b,[(d['t'],d['input'],GRAY),(d['t'],d['output'],BLUE)],(0,d['t'][-1]),(-lim,lim),xlabel='时间 / s',ylabel='位移 / 输入振幅');b.text('灰：支撑    蓝：质量块',100,740);done(b,n,'稳态时间序列：'+str(f)+'Hz')
b=Board('频率决定隔振还是放大');mask=[i for i,x in enumerate(D['f']) if x<=5];plot(b,[([D['f'][i] for i in mask],[D['T'][i] for i in mask],BLUE),([0,5],[1,1],GRAY)],(0,5),(0,6),xlabel='频率比 r = f/f0',ylabel='输出 / 输入振幅');done(b,4,'单级传递曲线')
b=Board('阻尼：压峰值，也增加高频通路');plot(b,[(D['f'],D['T'],BLUE),(D['f'],D['T_damped'],ORANGE)],(0,10),(0,6),xlabel='频率比 r',ylabel='输出 / 输入振幅');b.text('蓝：0.1     橙：0.5',170,740);sel=[i for i,f in enumerate(D['f']) if f>=2];plot(b,[([D['f'][i] for i in sel],[D['T'][i] for i in sel],BLUE),([D['f'][i] for i in sel],[D['T_damped'][i] for i in sel],ORANGE)],(2,10),(0,.6),rect=(130,1000,890,1320),xlabel='频率比 r',ylabel='高频局部放大');done(b,7,'阻尼强弱比较')
b=Board('四级主链：下级也会反作用于上级');b.rect((280,170,680,210));
for i in range(4):
 y=300+i*150;spring(b,480,210 if i==0 else 300+(i-1)*150+35,y-(65 if i==3 else 35))
 if i<3:mass(b,480,y)
 else:b.circle(480,y,65)
 b.text(f'第 {i+1} 级',680,y-30)
b.text('底端：测试镜',290,850);done(b,8,'多级悬挂主链')
b=Board('两级必须联立求解');plot(b,[(D['f'],D['logT'],BLUE),(D['f'],D['logT2'],TEAL)],(0,10),(-4,2),xlabel='频率 / Hz',ylabel='振幅比的 log10');b.text('蓝：单级    绿：两级',130,740);done(b,9,'两级耦合频响')
b=Board('悬挂只处理特定的扰动路径');b.text('地面',60,190);b.text('悬挂',390,190);b.text('镜子',740,190);b.arrow((170,225),(360,225));b.arrow((500,225),(715,225));b.text('材料热运动',110,420,color=ORANGE);b.arrow((400,450),(760,300),ORANGE);b.text('其他非支撑路径',100,620,color=TEAL);b.arrow((480,640),(820,300),TEAL);done(b,10,'限制与其他扰动')
from PIL import Image
im=Image.open(P.parent/'originals/photos/suspension.jpg');M.append({'file':'../originals/photos/suspension.jpg','width':im.width,'height':im.height,'identity':'Caltech/MIT/LIGO Laboratory 真实悬挂照片','min_font_px':'NOT_MEASURED','purpose':'实际多级悬挂与光学元件'})
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2))
