"""New Sagnac illustrations CC BY 4.0; source code CC0-1.0."""
from figure_canvas import *
D=DATA;P=D['parameters']
def plot(c,points,col=BLUE,width=6):
 c.d.line(points,fill=col,width=width,joint='curve');c.bottom=max(c.bottom,max(y for x,y in points))
def circle(c,x,y,r,col=BLUE):
 c.d.ellipse((x-r,y-r,x+r,y+r),outline=col,width=6);c.bottom=max(c.bottom,y+r)
def dot(c,x,y,col=INK,r=12):
 c.d.ellipse((x-r,y-r,x+r,y+r),fill=col);c.bottom=max(c.bottom,y+r)
def ring(c,x,y,r):
 circle(c,x,y,r);c.arrow((x+70,y-r),(x-80,y-r),BLUE);c.arrow((x+70,y+r),(x-80,y+r),ORANGE)
def wave(c,y,phase=0,col=BLUE):
 plot(c,[(90+880*i/240,y-55*math.cos(4*math.pi*i/240-phase)) for i in range(241)],col)
# Model-independent component layouts use screen coordinates only.
c=Canvas('光绕一圈，怎样知道你转了？')
c.text(65,135,'Sagnac效应：比较同一路线的两个方向',40)
ring(c,530,490,220)
c.text(205,200,'反向绕行',44,BLUE);c.text(585,760,'再合到一起',44,ORANGE)
dot(c,530,710);c.arrow((530,730),(530,870));c.text(215,920,'一小段时间差，变成相位差',44)
c.text(215,1010,'相位的变化，告诉我们转动有多快',40)
c.save('00-cover.png','独立封面以环路和会合点提出两方向时间比较')

c=Canvas('先认清光从哪里来、到哪里去')
c.text(65,140,'俯视概念图；蓝棕线略错开便于辨认',40)
# square path: beam splitter lower-left, three mirrors
for a,b in [((260,700),(260,300)),((260,300),(800,300)),((800,300),(800,700)),((800,700),(260,700))]:c.line(a,b,BLUE)
for a,b in [((290,670),(770,670)),((770,670),(770,330)),((770,330),(290,330)),((290,330),(290,670))]:c.line(a,b,ORANGE)
c.arrow((260,540),(260,440));c.arrow((490,300),(610,300));c.arrow((770,530),(770,430),ORANGE);c.arrow((490,670),(610,670),ORANGE)
for x,y in [(260,300),(800,300),(800,700)]:c.d.rectangle((x-22,y-22,x+22,y+22),fill=GREEN)
c.line((225,735),(305,655),INK);c.text(370,745,'分束/合束器',42)
c.arrow((70,700),(225,700),GREEN);c.text(65,590,'入射光',40,GREEN)
c.arrow((280,730),(280,880),GREEN);c.text(370,865,'检测器：读明暗',42,GREEN)
c.text(65,1000,'镜子迫使光闭环；自由空间中的光不会拐弯',40)
c.text(65,1085,'同路反向不是两条独立长短臂',42)
c.save('01-loop.png','识别分束合束、三面镜、两反向路径与探测端')

c=Canvas('不转动时，两束光同时回到B')
c.text(65,135,'理想圆形导路、真空；惯性实验室俯视',40)
ring(c,530,510,230);dot(c,760,510);c.text(790,480,'B',46)
c.text(400,455,'同一半径R',40);c.text(395,540,'路程均为L',40)
c.text(65,835,f"R = {P['radius_m']:g} m；L = {D['circumference_m']:.4f} m",44)
c.text(65,925,f"两束都用 L/c = {D['time_zero_s']*1e9:.4f} ns",44)
c.save('02-rest.png','建立静止基线和固定接收点，定义半径周长与传播时间')

# visible motion uses deliberately huge beta=.2, exact circular geometry.
for forward,filename,title in [(True,'03-chase.png','顺着转：光要追上前移的B'),(False,'04-meet.png','逆着转：光迎面遇到前移的B')]:
 c=Canvas(title);v=D['visible'];q=v['q_plus' if forward else 'q_minus'];shift=v['receiver_plus' if forward else 'receiver_minus'];cx=530;cy=500;r=225
 c.text(65,135,f"为了看清：另设 v/c = {v['beta']:g}（放大演示）",40)
 circle(c,cx,cy,r,'#b3c4ce');dot(c,cx+r,cy,INK);c.text(805,475,'B起点',40)
 end=2*math.pi*shift;ex=cx+r*math.cos(end);ey=cy-r*math.sin(end);dot(c,ex,ey,GREEN)
 points=[(cx+r*math.cos(end*i/100),cy-r*math.sin(end*i/100)) for i in range(101)];plot(c,points,GREEN,10);c.arrow(points[-9],points[-1],GREEN)
 rr=r+35 if forward else r-35
 optical=[(cx+rr*math.cos((1 if forward else -1)*2*math.pi*q*i/240),cy-rr*math.sin((1 if forward else -1)*2*math.pi*q*i/240)) for i in range(241)]
 plot(c,optical,BLUE if forward else ORANGE,5);c.arrow(optical[-7],optical[-1],BLUE if forward else ORANGE)
 c.text(65,780,'绿：B移动；光路径向错开仅便于辨认',40,GREEN)
 c.text(65,870,('ct+ = L + vt+' if forward else 'ct− = L − vt−'),52,BLUE if forward else ORANGE)
 c.text(65,970,f"光走 {q:.3f} L；B走 {shift:.3f} L",44)
 c.text(65,1060,'光在实验室中仍以c前进',44)
 c.save(filename,'分别展示不同接收事件与移动终点，实际弧角读取JSON可见模型')

c=Canvas('把圆周展开，两条直线给出接收时刻')
c.text(65,140,f"与前两图同一放大模型；v/c = {D['visible']['beta']:g}",40)
v=D['visible'];xp=lambda x:130+(x+1)*450;yp=lambda q:900-q/1.45*600
c.arrow((100,900),(995,900),INK);c.arrow((580,940),(580,230),INK)
# x coordinates displayed [-1,1]; source copies at +/-1 receiver trajectory x=bq.
for x in [-1,0,1]:c.text(xp(x)-20,945,f'{x:g}',40)
c.text(600,225,'q = ct/L',40);c.text(405,1030,'x = 实验室弧长/L',40)
for sign,q,col in [(1,v['q_plus'],BLUE),(-1,v['q_minus'],ORANGE)]:
 start=-sign;end=v['beta']*q;plot(c,[(xp(start),yp(0)),(xp(end),yp(q))],col);dot(c,xp(end),yp(q),col)
plot(c,[(xp(0),yp(0)),(xp(v['beta']*1.4),yp(1.4))],GREEN)
c.text(65,190,'蓝：顺向光',40,BLUE);c.text(65,270,'棕：逆向光',40,ORANGE);c.text(65,350,'绿：B',40,GREEN)
c.text(65,1130,f"交点：q− = {v['q_minus']:.3f}；q+ = {v['q_plus']:.3f}",42)
c.text(65,1215,'±1处是同一发射点的相邻展开副本',40)
c.save('05-spacetime.png','同一坐标系画出光与探测器世界线并解释圆周展开副本')

c=Canvas('极小的延迟，可以是一段可读相位')
c.text(65,140,f"回到教学参数：R={P['radius_m']:g} m、Ω={P['omega_rad_s']:g} rad/s",40)
c.text(65,230,f"单匝 Δt ≈ {D['single_delay_s']:.3g} s",48,BLUE)
c.text(65,320,f"λ0 = {P['wavelength_m']*1e9:.0f} nm；T光 = {D['optical_period_s']*1e15:.3f} fs",42)
wave(c,570,0,BLUE);wave(c,740,D['coil_phase_rad'],ORANGE)
c.text(65,425,'蓝：参考波；棕：延迟波（多匝例）',40)
c.text(65,850,f"{P['turns']}匝：延迟 {D['coil_delay_s']*1e15:.3f} fs",44)
c.text(65,940,f"Δφ = 2π Δt/T光 = {D['coil_phase_rad']:.3f} rad",44)
c.text(65,1030,'横向为同一处的时间；电场振荡仅为示意',40)
c.save('06-phase.png','波形相对相位与实算延迟连接，不把模型波形当真实记录')

c=Canvas('面积相同吗？别只看光走多远')
c.text(65,140,f"两个矩形周长均{D['area_shapes'][0]['perimeter']:g} m；同一比例尺",42)
scale=2000
for i,z in enumerate(D['area_shapes']):
 x=150;y=300+i*560;w=z['width']*scale;h=z['height']*scale
 c.d.rectangle((x,y,x+w,y+h),outline=BLUE,width=7);c.bottom=max(c.bottom,y+h)
 c.text(590 if i==0 else 150,y+(80 if i==0 else 180),f"A = {z['area']:.4f} m²",42)
 c.text(590 if i==0 else 150,y+(170 if i==0 else 270),z['name'],44)
c.text(65,1310,'同转速时，面积更大的回路相位差更大',40)
c.save('07-area.png','同周长不同面积的几何反例，边长及面积都由JSON计算')

c=Canvas('一只环，只读转动在法向上的分量')
c.text(65,140,'面积箭头垂直环面；与正向绕行满足右手规则',40)
c.d.ellipse((260,540,800,710),outline=BLUE,width=6);c.bottom=710
c.arrow((530,625),(530,280),BLUE);c.text(570,260,'面积法向',42,BLUE)
c.arrow((530,625),(820,335),ORANGE);c.text(785,250,'Ω',50,ORANGE)
c.d.arc((370,465,690,785),start=270,end=315,fill=INK,width=4);c.text(555,410,'θ',40)
c.text(65,800,'有效面积 = A cosθ',48)
for i,z in enumerate(D['tilts'][:3]):c.text(65,910+i*90,f"θ={z['degrees']:g}° → {P['turns']}匝相位 {z['phase_rad']:.3f} rad",42)
c.text(65,1215,'正转/反转或翻转法向，会改变符号',42)
c.save('08-projection.png','面积法向和角速度投影以及0/60/90度计算，区分转速与倾角')

c=Canvas('增加的是带符号面积，不只是纤长')
c.text(65,140,f"半径{P['radius_m']:g} m的每匝面积相同",44)
cases=D['winding_cases'];assert len({z['forward']+z['reverse'] for z in cases})==1
ordered=sorted(cases,key=lambda z:z['forward'])
assert all(a['forward']*850/(a['forward']+a['reverse']) <= b['forward']*850/(b['forward']+b['reverse']) for a,b in zip(ordered,ordered[1:]))
for j,z in enumerate(cases):
 y=290+j*320;c.text(65,y,f"正绕{z['forward']}匝，反绕{z['reverse']}匝",44)
 total=z['forward']+z['reverse'];sc=850/total
 c.d.rectangle((90,y+100,90+z['forward']*sc,y+160),fill=BLUE)
 if z['reverse']:c.d.rectangle((90+z['forward']*sc,y+100,940,y+160),fill=ORANGE)
 c.text(90,y+180,f"净{z['effective_turns']}匝 → {z['phase_rad']:.3f} rad",42)
c.text(65,1270,'蓝正棕反；同方向面积相加，反方向相减',40)
c.save('09-turns.png','展示同纤长不同绕向的净面积与相位，条长按匝数共轴')

c=Canvas('填入玻璃，不能把c直接替换成c/n')
c.text(65,140,'圆环整体共转；n为共动介质折射率',42)
c.card(100,270,860,110,'介质局部静止系：光速为 ±u，u=c/n')
c.arrow((530,400),(530,490),GREEN)
c.card(100,540,860,110,'实验室：w± = (±u+v)/(1±uv/c²)')
c.text(65,760,'再追运动终点：t+=L/(w+−v)',42)
c.text(65,845,'反向相遇：t−=L/(v−w−)',42)
for j,z in enumerate(D['medium']):c.text(65,965+j*85,f"n={z['index']:g}：Δt={float(z['delay_s']):.3g} s",44)
c.text(65,1260,'延迟差相同；各自传播时间并不相同',42)
c.save('10-medium.png','逐步分开介质局部速度、相对论合成和移动探测器，以高精度数据核n抵消')

for biased,name,title in [(False,'11-cosine.png','单看明暗：正转和反转可能一样'),(True,'12-bias.png','加四分之一周期偏置，才有零点斜率')]:
 c=Canvas(title);xp=lambda p:145+(p+math.pi)/(2*math.pi)*770;yp=lambda z:800-z*440
 c.text(65,140,'归一化检测强度；理想等强、同偏振',40)
 for z in [0,.5,1]:c.line((145,yp(z)),(915,yp(z)),'#b5c3ce');c.text(65,yp(z)-20,f'{z:g}',40)
 plot(c,[(xp(z['phase']),yp(z['biased' if biased else 'bright'])) for z in D['curves']],ORANGE if biased else BLUE)
 for p,label in [(-math.pi,'−π'),(0,'0'),(math.pi,'π')]:c.text(xp(p)-25,850,label,42)
 c.text(330,940,'横轴：Sagnac相位 / rad',42)
 c.text(65,1040,'I/I0 = [1−sin(Δφ)]/2' if biased else 'I/I0 = [1+cos(Δφ)]/2',44)
 c.text(65,1130,'已知偏置+π/2；局部信号有符号' if biased else '关于零点对称；零点斜率也为零',42)
 c.text(65,1220,'实际用调制/解调并管理周期歧义' if biased else '同亮度不唯一确定转速和方向',42)
 c.save(name,'在同一相位强度坐标中分别展示余弦歧义和正交偏置局部线性')

c=Canvas('有源环激光：读两种频率的拍频')
c.text(65,140,'与外部光源的无源光纤环分开理解',42)
ring(c,530,480,210);c.d.rectangle((720,435,760,525),fill=GREEN);c.text(350,185,'腔内增益介质',42,GREEN);c.line((700,230),(740,420),GREEN)
c.text(65,785,'顺向谐振频率f+，逆向f−',44)
c.text(65,875,'合束后的慢明暗振荡：|f+−f−|',42)
c.text(65,965,'理想幅值 ≈ 4A|Ω·n|/(λ0P)',44)
c.text(65,1060,'P为周长；实际拍频还需校正激光动力学',40)
c.save('13-ringlaser.png','主动环腔的增益与频率差，明确不同于一次绕行相位强度读出')

c=Canvas('静止在地面，也随地球一起转')
z=D['rlg'];c.text(65,140,'另一个量级模型：方环，633 nm附近',42)
# Earth normal and rotation axis: angle comes from the executed JSON model.
cx=480;cy=590;r=230;theta=math.radians(z['tilt_degrees'])
circle(c,cx,cy,r,'#95b5c8');c.d.ellipse((cx-r,cy-65,cx+r,cy+65),outline='#95b5c8',width=4)
c.arrow((cx,850),(cx,275),BLUE);c.text(180,260,'地球转轴 Ω地',42,BLUE)
px=cx+r*math.sin(theta);py=cy-r*math.cos(theta)
nx=math.sin(theta);ny=-math.cos(theta);tx=math.cos(theta);ty=math.sin(theta)
c.line((px-120*tx,py-120*ty),(px+120*tx,py+120*ty),GREEN)
c.arrow((px,py),(px+190*nx,py+190*ny),ORANGE)
c.text(760,235,'环面法向',42,ORANGE);c.text(745,455,'环面侧视',40,GREEN)
c.line((px,py),(px,py-175),BLUE,True)
c.d.arc((px-100,py-100,px+100,py+100),start=270,end=270+z['tilt_degrees'],fill=INK,width=4)
c.text(650,280,f"{z['tilt_degrees']:g}°",42)
c.text(70,900,f"Ω地={z['earth_omega_rad_s']:.4g} rad/s",44)
c.text(70,985,f"有效分量：Ω地 cos {z['tilt_degrees']:g}°",44)
c.text(70,1080,f"边长{z['side_m']:g} m，A={z['area_m2']:.2f} m²，P={z['perimeter_m']:g} m",42)
c.text(70,1170,f"λ0={z['wavelength_m']*1e9:g} nm → 理想拍频{z['frequency_hz']:.1f} Hz",44,GREEN)
c.text(70,1270,'环与地球不按尺寸比例；地点与朝向是假设',40)
c.text(70,1355,'非GINGERINO安装地点，也非本文实测',40)
c.text(70,1440,'须区分转动变化、倾角变化和腔长漂移',40)
c.save('14-earth.png','地球轴、假设45度环面法向与有效投影，角度和拍频由JSON计算')

c=Canvas('测到角速度，不等于永远知道朝向')
b=D['bias'];xp=lambda t:150+t/b['points'][-1]['t_s']*750;yp=lambda e:800-e/b['points'][-1]['error_deg']*400
c.text(65,140,f"假设固定零偏 {b['bias_deg_s']:g}°/s；真实转速为0",42)
for y in [0,b['points'][-1]['error_deg']/2,b['points'][-1]['error_deg']]:c.line((150,yp(y)),(900,yp(y)),'#b2c2cd');c.text(65,yp(y)-22,f'{y:g}',40)
plot(c,[(xp(z['t_s']),yp(z['error_deg'])) for z in b['points']],ORANGE)
for t in [0,b['points'][-1]['t_s']/2,b['points'][-1]['t_s']]:c.text(xp(t)-25,855,f'{t:g}',40)
c.text(280,950,'横轴：时间/s；纵轴：角度误差/°',40)
c.text(65,1060,f"积分{b['points'][-1]['t_s']} s → 误差{b['points'][-1]['error_deg']:g}°",48)
c.text(65,1160,'需标定、温度补偿和其他姿态信息约束',40)
c.save('15-drift.png','固定角速度零偏实际积分为随时间增长的角度误差')
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(f'{len(meta)} figures; geometry/glyph/ink checks PASS')
