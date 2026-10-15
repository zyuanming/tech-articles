"""Original diagrams for EDSAC sound memory article, CC BY 4.0.
Requires Pillow and NotoSansCJK fonts. Does not alter historical photographs.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math,json
P=Path(__file__).resolve().parents[1]; A=P/'assets'
D=json.loads((P/'examples/results.json').read_text())
REG='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
BG='#f7f5ee'; INK='#163345'; MUTED='#536778'; BLUE='#1c6c9c'; TEAL='#007d75'; ORANGE='#c45824'; PALE='#d6e8e7'; LINE='#b7c6ca'; YELLOW='#efc95f'
W=720

def font(n=30,b=False):return ImageFont.truetype(BOLD if b else REG,n,index=2)
def canvas(h,title,subtitle=None):
 im=Image.new('RGB',(W,h),BG);d=ImageDraw.Draw(im)
 d.rectangle((0,0,W,12),fill=TEAL);d.text((32,34),title,font=font(36,True),fill=INK)
 if subtitle:d.text((32,93),subtitle,font=font(27),fill=MUTED)
 return im,d

def text(d,xy,s,n=30,c=INK,b=False):d.text(xy,s,font=font(n,b),fill=c)
def center(d,xy,s,n=30,c=INK,b=False):
 f=font(n,b);bb=d.textbbox((0,0),s,font=f);d.text((xy[0]-(bb[2]-bb[0])/2,xy[1]-(bb[3]-bb[1])/2-bb[1]),s,font=f,fill=c)
def box(d,rect,fill='white',outline=LINE):d.rounded_rectangle(rect,radius=16,fill=fill,outline=outline,width=2)
def arrow(d,xy,fill=TEAL,w=5):
 d.line(xy,fill=fill,width=w);x,y=xy[-1];u,v=xy[-2];a=math.atan2(y-v,x-u)
 d.polygon([(x,y),(x-15*math.cos(a-.45),y-15*math.sin(a-.45)),(x-15*math.cos(a+.45),y-15*math.sin(a+.45))],fill=fill)
def save(im,name):im.save(P/name if name=='cover.png' else A/name)
def slots(d,bits,y,x=48,step=78,h=72,labels=False,color=TEAL):
 for i,b in enumerate(bits):
  xx=x+i*step;box(d,(xx,y,xx+step-7,y+h),color if b else 'white',color)
  center(d,(xx+(step-7)/2,y+h/2),str(b),34,'white' if b else INK,True)
  if labels:center(d,(xx+(step-7)/2,y+h+26),str(i),25,MUTED)

def pulse(d,bits,y,x=48,step=78,amp=70,color=TEAL):
 pts=[(x,y)]
 for i,b in enumerate(bits):
  xx=x+i*step;pts.extend([(xx+12,y),(xx+12,y-amp*b),(xx+step/2,y-amp*b),(xx+step/2,y),(xx+step,y)])
 d.line(pts,fill=color,width=5)

# 1
im,d=canvas(650,'让一串0和1排队经过','同一小例：10110010')
slots(d,D['bits'],160,labels=True)
text(d,(48,286),'时隙编号：0 到 7',27,MUTED)
pulse(d,D['bits'],445)
for i in range(9):
 x=48+i*78;d.line((x,343,x,470),fill=LINE,width=1)
 if i%2==0:center(d,(x,503),str(i*2),27)
text(d,(490,550),'时间 / 微秒',27)
text(d,(48,580),'1：有一小包脉冲    0：该时隙留空',28)
save(im,'01-bits-and-slots.png')
# 2
im,d=canvas(950,'同一份信息，换三次外衣','电信号 → 声波 → 电信号')
for y,title,desc in [(154,'① 发射端石英晶体','电脉冲使晶体产生微小形变'),(414,'② 水银中的声波','机械振动沿液体传播'),(674,'③ 接收端石英晶体','到达的振动转回电信号')]:
 box(d,(35,y,685,y+195));text(d,(58,y+18),title,32,b=True);text(d,(58,y+65),desc,28)
 if y==154:
  pulse(d,[1,0,1],y+162,x=75,step=110,amp=45);d.rectangle((500,y+112,615,y+163),fill=YELLOW);text(d,(490,y+115),'石英',27)
 elif y==414:
  d.rounded_rectangle((70,y+115,650,y+169),radius=22,fill='#d6dde2')
  for x in [125,155,185,360,390,420,450]:d.line((x,y+125,x,y+159),fill=TEAL,width=5)
  arrow(d,[(500,y+140),(630,y+140)])
 else:pulse(d,[1,0,1],y+164,x=130,step=145,amp=46)
 if y<674:arrow(d,[(360,y+204),(360,y+250)])
save(im,'02-electric-sound-electric.png')
# 3
im,d=canvas(850,'传播要花时间，这就是“延迟”','先看一个声波包，不画全部比特')
for j,(label,px) in enumerate([('刚进入',145),('走到中间',360),('到达接收端',585)]):
 y=160+j*180;text(d,(45,y),label,29,b=True)
 d.rounded_rectangle((50,y+63,660,y+133),radius=25,fill='#d6dde2')
 for dx in [-16,-8,0,8,16]:d.line((px+dx,y+76,px+dx,y+120),fill=TEAL,width=4)
 arrow(d,[(px+30,y+98),(min(px+75,652),y+98)])
box(d,(38,730,682,812),PALE,PALE);center(d,(360,770),'传播时间 = 路程 ÷ 声速',33,b=True)
save(im,'03-propagation-delay.png')
# 4
im,d=canvas(1070,'单向走完，再用电路送回起点','声波本身不需要在管内折返')
box(d,(75,156,645,300),PALE,TEAL);center(d,(360,196),'水银延迟线',33,b=True)
text(d,(105,246),'发射端',28);text(d,(495,246),'接收端',28);arrow(d,[(224,264),(479,264)])
arrow(d,[(590,305),(590,359)])
box(d,(360,371,680,482));center(d,(520,407),'接收、放大、检波',28,b=True);center(d,(520,446),'把声波包读成电信号',25)
arrow(d,[(520,487),(520,542)])
box(d,(360,554,680,681));center(d,(520,591),'判定并重新定时',29,b=True);center(d,(520,640),'跟着时钟重造脉冲',26)
box(d,(37,554,306,681),'#fff2cf',YELLOW);center(d,(171,593),'时钟',30,b=True);center(d,(171,640),'给出时隙节拍',27)
arrow(d,[(311,617),(352,617)],ORANGE)
arrow(d,[(520,686),(520,742)])
box(d,(360,754,680,875));center(d,(520,795),'选择回送的内容',29,b=True);center(d,(520,841),'保留旧位 / 换成新位',26)
arrow(d,[(360,815),(18,815),(18,330),(128,330),(128,312)])
text(d,(44,442),'电反馈',29,TEAL,True);text(d,(42,480),'回到发射端',27)
box(d,(39,938,681,1020),PALE,PALE);center(d,(360,978),'读出时可分出一路，循环仍继续',29,b=True)
save(im,'04-regeneration-loop.png')
# 5
im,d=canvas(900,'复制形状，不如重新作一次判断','教学数值；不是原机测得的电压')
values=D['regeneration']['received']
text(d,(38,154),'收到的强弱已经不整齐',30,b=True)
x0=70; step=76;base=416
for i,v in enumerate(values):
 x=x0+i*step;d.rectangle((x,base-v*190,x+43,base),fill=TEAL)
 center(d,(x+21,base+33),str(D['bits'][i]),29)
y=base-.5*190
for x in range(50,685,20):d.line((x,y,x+10,y),fill=ORANGE,width=3)
text(d,(51,213),'判断门槛',27,ORANGE)
arrow(d,[(360,490),(360,551)])
text(d,(38,577),'过门槛记1，否则记0',29,b=True)
slots(d,D['bits'],646,step=78)
box(d,(38,772,682,856),'#fff2e8',ORANGE);center(d,(360,813),'若原来的1弱到门槛下，就会判错',27,ORANGE,True)
save(im,'05-regenerate-not-amplify.png')
# 6
im,d=canvas(930,'比特在动，顺序不变','每过2微秒，下一位来到读口')
for j,k in enumerate([0,1,2,7,8]):
 y=153+j*143;row=D['bits'][k%8:]+D['bits'][:k%8]
 text(d,(40,y),f't = {k*2} 微秒',27,b=True)
 slots(d,row,y+49,x=40,step=80,h=58)
 d.rectangle((38,y+47,116,y+110),outline=ORANGE,width=4)
text(d,(40,872),'橙框：这一刻正在读出的位',28,ORANGE)
save(im,'06-time-ring.png')
# 7
im,d=canvas(830,'地址要回答两个问题','选哪根管？再等管里的哪一段？')
for row,(name,bits) in enumerate([('0号管：A、B',D['bits']),('1号管：C、D',[0,1,0,1,1,1,0,0])]):
 y=156+row*245;text(d,(42,y),name,31,b=True);slots(d,bits,y+67,step=78)
 text(d,(125,y+159),'第0个字',27);text(d,(438,y+159),'第1个字',27)
box(d,(35,660,685,789),PALE,TEAL);center(d,(360,698),'找B：先选0号管，再等第1个字',29,b=True);center(d,(360,751),'这里每字只有4位，是缩小的教学模型',25)
save(im,'07-tank-and-time-address.png')
# 8
im,d=canvas(1040,'同样读B，等待却不同','B的开头在8、24、40……微秒出现')
for row,(req,start,end) in enumerate([(3,8,16),(9,24,32)]):
 y=170+row*370;text(d,(40,y),f'请求时刻：{req} 微秒',31,b=True)
 x=lambda t:52+t*18.5
 base=y+151;d.line((52,base,652,base),fill=LINE,width=3)
 # wait and transfer separated vertically for legibility
 d.rectangle((x(req),base-68,x(start),base-42),fill=ORANGE)
 d.rectangle((x(start),base-31,x(end),base-5),fill=TEAL)
 for v in sorted(set([0,req,start,end])):
  d.line((x(v),base-6,x(v),base+14),fill=INK,width=2);center(d,(x(v),base+43),str(v),26)
 text(d,(42,y+230),f'等 {start-req} 微秒；再用8微秒收齐B',28)
text(d,(45,915),'橙色：等开头    绿色：接收整个字',28)
text(d,(45,967),'理想模型：忽略控制延迟与建立时间',26,MUTED)
save(im,'08-wait-for-word.png')
# 9
im,d=canvas(915,'改写：只替换B经过的四个时隙','A仍照常回送，不需要先清空整根管')
text(d,(40,153),'这一圈读到： A = 1011   B = 0010',29,b=True)
slots(d,D['bits'],219)
arrow(d,[(360,320),(360,380)])
text(d,(40,413),'A的四位原样回送；B改送0101',29,b=True)
slots(d,[1,0,1,1,0,1,0,1],483)
for i in range(4,8):d.rectangle((47+i*78,482,120+i*78,558),outline=ORANGE,width=4)
text(d,(40,626),'下一圈读到： A = 1011   B = 0101',29,b=True)
box(d,(40,733,680,862),PALE,TEAL);center(d,(360,775),'改写发生在“回送”的选择点',30,b=True);center(d,(360,824),'到下一圈，新内容才走到同一个读口',26)
save(im,'09-overwrite-one-word.png')
# 10
im,d=canvas(1040,'17、18、35、36各在数什么？','把“时间位置”和“有效位”分开')
text(d,(35,155),'一个短字：占18个时隙',31,b=True)
box(d,(38,220,567,305),PALE,TEAL);center(d,(302,262),'17位有效数据（含符号位）',28,b=True)
box(d,(579,220,682,305),'#e2e4e5');center(d,(631,261),'空隙',27)
text(d,(35,365),'两个独立短字：17 + 17 = 34位',30,b=True)
for x in [38,370]:
 box(d,(x,432,x+238,515),PALE,TEAL);center(d,(x+119,474),'17位',31,b=True)
 box(d,(x+248,432,x+310,515),'#e2e4e5');center(d,(x+279,474),'空',26)
text(d,(35,577),'当成一个长字：可用中间的1位',29,b=True)
box(d,(38,645,571,731),PALE,TEAL);center(d,(306,688),'17 + 1 + 17 = 35位',33,b=True)
box(d,(582,645,682,731),'#e2e4e5');center(d,(632,687),'空隙',27)
text(d,(38,783),'总时长仍是36个时隙',30,b=True)
text(d,(38,839),'中间多用的那一位叫“夹心位”。',27)
text(d,(38,886),'图按容量分组，不表示串行高低位次序。',25,MUTED)
text(d,(38,937),'长字是一个数，并非两个短数相加。',27)
save(im,'10-short-and-long-words.png')
# 11
im,d=canvas(1050,'容量要带上建设阶段','“第一天能运行”不等于“全机已装满”')
rows=[('1949年5月6日','日志：第一组4根长管在运行','4 × 32 = 128个短字位置'),('第一组完整配置','16根长管；每根32个短字','16 × 32 = 512个短字位置'),('第二组在1952年启用','两组共32根长管','32 × 32 = 1024个短字位置')]
for i,(date,desc,num) in enumerate(rows):
 y=157+i*275;box(d,(35,y,685,y+225),'white');text(d,(61,y+24),date,32,TEAL,True);text(d,(61,y+84),desc,28);text(d,(61,y+144),num,29,b=True)
text(d,(39,999),'首行容量由日志根数与每管容量推算。',25,MUTED)
save(im,'11-capacity-stages.png')
# 12
im,d=canvas(825,'“到达”和“开门”必须对上','时钟按时开门，声波却受传播条件影响')
for row,(label,shift) in enumerate([('原先：脉冲落在时间窗内',0),('传播时延改变后：可能错过',66)]):
 y=169+row*277;text(d,(38,y),label,29,b=True)
 for i in range(4):
  x=90+i*150;d.rectangle((x-25,y+84,x+25,y+181),fill='#d9e1e5')
  d.line((x+shift,y+176,x+shift,y+109),fill=TEAL if row==0 else ORANGE,width=9)
  d.ellipse((x+shift-8,y+100,x+shift+8,y+116),fill=TEAL if row==0 else ORANGE)
text(d,(42,755),'灰：时钟窗口   竖线：脉冲到达',28)
save(im,'12-temperature-and-timing.png')
# 13
im,d=canvas(960,'回送一次，不等于任由回声反弹','短管里的反射可能制造多余信号')
for j,(label,direction) in enumerate([('① 正常声波：从发射端到接收端',1),('② 一部分在端部反射回来',-1),('③ 再反射，延迟到达接收端',1)]):
 y=165+j*213;text(d,(38,y),label,27,b=True);d.rounded_rectangle((48,y+75,668,y+137),radius=25,fill='#d6dde2')
 arrow(d,[(100 if direction>0 else 610,y+106),(610 if direction>0 else 100,y+106)],TEAL if j==0 else ORANGE,6)
box(d,(39,830,681,918),'#fff2e8',ORANGE);center(d,(360,873),'这些多余回声，不是有意重建的数据',27,ORANGE,True)
save(im,'13-reflection-is-not-feedback.png')
# 14
im,d=canvas(810,'同样叫存储，取数方式可以不同','区别在于怎样到达目标数据')
text(d,(40,156),'延迟线：先选管，再等时隙',31,b=True)
for i,s in enumerate(['A','B','C','D']):
 box(d,(48+i*158,222,182+i*158,300),TEAL if s=='C' else 'white');center(d,(115+i*158,260),s,33,'white' if s=='C' else INK,True)
arrow(d,[(70,359),(650,359)]);center(d,(360,410),'顺着固定次序经过同一个读口',29)
text(d,(40,485),'可直接选单元的存储：译码定位',29,b=True)
for i,s in enumerate(['A','B','C','D']):
 box(d,(48+i*158,555,182+i*158,633),TEAL if s=='C' else 'white');center(d,(115+i*158,594),s,33,'white' if s=='C' else INK,True)
arrow(d,[(432,725),(432,643)],ORANGE);text(d,(48,730),'地址C',29,ORANGE,True)
save(im,'14-access-comparison.png')
# independent cover
im,d=canvas(960,'计算机的记忆','曾经是一串在水银里奔跑的声音')
text(d,(43,168),'EDSAC  /  超声延迟线',32,TEAL,True)
d.rounded_rectangle((39,330,681,505),radius=40,fill='#cdd5d9',outline=LINE,width=3)
for i,b in enumerate(D['bits']):
 if b:
  x=82+i*76
  for dx in [-12,-6,0,6,12]:d.line((x+dx,366,x+dx,469),fill=TEAL,width=4)
arrow(d,[(585,547),(585,688),(120,688),(120,532)],ORANGE,8)
text(d,(253,626),'读出 · 整形 · 回送',29,ORANGE,True)
text(d,(44,802),'数据一直在走，记忆却能留下。',32,b=True)
text(d,(45,870),'从一根实物管子，走进时间里的地址。',26,MUTED)
save(im,'cover.png')
print('15 original PNG diagrams / cover generated')
