from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math
O=Path(__file__).resolve().parent.parent/'assets'
F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'; B=F.replace('Regular','Bold')
BG='#fffdf7'; INK='#20333d'; BLUE='#267c9c'; GREEN='#45856a'; GOLD='#d39427'; RED='#bf5d51'; MUTED='#607581'
def font(n,b=False):return ImageFont.truetype(B if b else F,n)
def base(title,sub=''):
 im=Image.new('RGB',(1200,840),BG);d=ImageDraw.Draw(im);d.text((55,38),title,font=font(43,True),fill=INK)
 if sub:d.text((55,106),sub,font=font(28),fill=MUTED)
 return im,d
def txt(d,p,t,n=32,c=INK,a=None):d.text(p,t,font=font(n),fill=c,anchor=a)
def arr(d,a,b,c=INK,w=5):
 d.line((*a,*b),fill=c,width=w);ang=math.atan2(b[1]-a[1],b[0]-a[0]);l=18
 d.polygon([b,(b[0]-l*math.cos(ang-.45),b[1]-l*math.sin(ang-.45)),(b[0]-l*math.cos(ang+.45),b[1]-l*math.sin(ang+.45))],fill=c)
def card(d,b,title,value,color=BLUE):
 d.rounded_rectangle(b,24,fill='#edf3f1',outline=color,width=4);txt(d,(b[0]+25,b[1]+18),title,32,color);txt(d,((b[0]+b[2])/2,b[1]+85),str(value),67,color,'mt')
def note(d,t,y=730,n=31,c=INK):txt(d,(600,y),t,n,c,'mt')
def save(im,n):im.save(O/n)
def coins(d,x,y,n,c=GOLD):
 for k in range(n):
  xx=x+(k%5)*55;yy=y+(k//5)*60;d.ellipse((xx,yy,xx+38,yy+38),fill=c);txt(d,(xx+19,yy+19),'1',24,'white','mm')
# 1
im,d=base('8 枚代币，从来没有凭空消失','先认识同一组例子：P 与 Q 可以互相发消息')
card(d,(90,210,480,560),'P 手中',5);card(d,(720,210,1110,560),'Q 手中',3,GREEN);coins(d,145,440,5);coins(d,835,440,3);arr(d,(495,300),(705,300));arr(d,(705,470),(495,470));txt(d,(600,320),'P → Q',28,a='mt');txt(d,(600,490),'Q → P',28,a='mt');note(d,'机器里的 + 路上的 = 8',650,44);save(im,'01-eight-tokens.png')
# 2
im,d=base('为什么两张照片只加出 6？','P 拍得早，Q 已经扣掉了转出的 2 枚')
card(d,(80,215,410,510),'P 的照片',5);card(d,(790,215,1120,510),'Q 的照片',1,GREEN);d.rounded_rectangle((450,270,750,450),20,fill='#f8e9c9',outline=GOLD,width=4);txt(d,(600,305),'路上：2',45,GOLD,'mt');txt(d,(600,375),'被漏掉了',30,GOLD,'mt');note(d,'只算本地照片：5 + 1 = 6',590,44);note(d,'补上通道里的消息，才是完整系统',685,34);save(im,'02-missing-two.png')
#3
im,d=base('为什么另一种拼法竟加出 10？','同一笔转移，被两张照片算了两遍')
card(d,(95,210,505,505),'Q 发送前',3,GREEN);card(d,(695,210,1105,505),'P 接收后',7);arr(d,(520,350),(680,350),GOLD);note(d,'3 + 7 = 10',565,60,RED);note(d,'收到的结果进了照片，发送的原因却被切掉',685,33);save(im,'03-double-count.png')
#4
im,d=base('全局状态，还包括两条通道','通道有方向；每条保存“已发出、尚未接收”的序列')
card(d,(70,295,350,575),'P 本地',5);card(d,(850,295,1130,575),'Q 本地',1,GREEN)
arr(d,(370,315),(830,315),BLUE);txt(d,(600,230),'P → Q：空',38,BLUE,'mt');arr(d,(830,545),(370,545),GOLD);txt(d,(600,565),'Q → P：[2]',38,GOLD,'mt');d.rounded_rectangle((520,440,680,520),15,fill='#f8e9c9');txt(d,(600,480),'m：2',34,GOLD,'mm');note(d,'本地状态 + 每条通道的状态',720,39);save(im,'04-whole-state.png')
#5 separate causal rule panels
im,d=base('收到消息，不能没有发送','实心圆：已纳入照片；空心圆：尚未纳入')
for y,c,label,sendinc in [(270,GREEN,'合法：发送已算入，接收未算入',True),(515,RED,'不合法：接收已算入，发送未算入',False)]:
 arr(d,(240,y),(955,y),c);d.ellipse((210,y-20,250,y+20),fill=c if sendinc else BG,outline=c,width=4);d.ellipse((950,y-20,990,y+20),fill=BG if sendinc else c,outline=c,width=4);txt(d,(230,y-80),'发送',30,a='mt');txt(d,(970,y-80),'接收',30,a='mt');txt(d,(600,y+55),label,33,c,'mt')
note(d,'合法情形中的消息，要留在通道照片里',742,33);save(im,'05-consistent-cut.png')
# 6-10 state progression; identical coordinates aid tracking
steps=[('先发业务消息，快照尚未开始',5,1,None,None,'[ m：2 ]','未记录', 'Q 扣掉 2；P 还没收到','06-send-message.png'),('P 先拍照，再发出标记',5,1,5,None,'[ m：2 ]','窗口打开','P → Q 的标记正在传播','07-record-p.png'),('Q 收到首个标记，也拍一张',5,1,5,1,'[ m：2 , 标记 ]','窗口仍开','Q → P：先 m，后标记','08-record-q.png'),('P 收到业务消息，保存两种状态',7,1,5,1,'[ 标记 ]','已记录 [2]','实时余额更新，冻结余额不变','09-record-transit.png'),('标记到 P，记录窗口关闭',7,1,5,1,'[ ]','最终记录 [2]','P→Q 为空；两条入通道均已完成','10-close-window.png')]
for title,p,q,sp,sq,queue,log,caption,name in steps:
 im,d=base(title,caption)
 card(d,(60,200,405,460),'P 实时',p);card(d,(795,200,1140,460),'Q 实时',q,GREEN)
 txt(d,(232,490),'快照：'+('未拍' if sp is None else str(sp)),34,BLUE,'mt');txt(d,(967,490),'快照：'+('未拍' if sq is None else str(sq)),34,GREEN,'mt')
 arr(d,(765,295),(435,295),GOLD);txt(d,(600,335),'Q → P',32,GOLD,'mt');d.rounded_rectangle((250,570,950,655),18,fill='#f8e9c9',outline=GOLD,width=2);txt(d,(600,611),'实时队列 '+queue,32,INK,'mm');note(d,'通道快照：'+log,696,35,GOLD);save(im,name)
#11
im,d=base('标记像队列中的一条分界线','只保证同一条通道内不超车，不保证不同通道同速')
for x,label,col in [(90,'旧消息',BLUE),(335,'旧消息',BLUE),(580,'标记',RED),(825,'新消息',GREEN)]:
 d.rounded_rectangle((x,290,x+205,475),18,fill=col);txt(d,(x+102,355),label,38,'white','mt')
arr(d,(110,580),(1070,580));txt(d,(600,625),'发送顺序 = 接收顺序',42,a='mt');note(d,'发送者：先拍照 → 插入标记 → 再发新消息',740,31);save(im,'11-fifo-boundary.png')
#12
im,d=base('接收者只补记这一个窗口','本地照片之前的消息，已经反映在本地状态里')
d.rectangle((325,270,890,480),fill='#f8e9c9');arr(d,(95,485),(1100,485));
for x,label,col in [(325,'我拍照',BLUE),(890,'标记到达',RED)]:d.line((x,225,x,560),fill=col,width=5);txt(d,(x,580),label,36,col,'mt')
for x in [480,630,765]:d.ellipse((x-16,345,x+16,377),fill=GOLD)
txt(d,(610,285),'窗口里的业务消息',35,GOLD,'mt');note(d,'纳入通道记录；标记到达后停止补记',710,36);save(im,'12-recording-window.png')
#13
im,d=base('同一轮快照：收到标记时怎么办？')
d.rounded_rectangle((345,165,855,265),18,fill='#e9eef0');txt(d,(600,215),'我记录过本地状态吗？',35,a='mm')
arr(d,(430,275),(270,360),BLUE);arr(d,(770,275),(930,360),GREEN);txt(d,(325,300),'没有',29,BLUE);txt(d,(855,300),'有了',29,GREEN)
for b,col,lines in [((70,385,565,670),BLUE,['保存本地状态','该入通道记为空','各出通道发送标记']),((635,385,1130,670),GREEN,['本地照片保持不变','结束这条入通道的记录','其他入通道继续等待'])]:
 d.rounded_rectangle(b,22,fill='#edf3f1',outline=col,width=3)
 for k,t in enumerate(lines):txt(d,(b[0]+30,b[1]+35+75*k),t,31,col)
note(d,'一次本地记录，多条独立的入通道记录',741,32);save(im,'13-marker-rules.png')
#14
im,d=base('B 的标记，不能替 C 关门','示意：接收者 A 已记录本地状态，有两条输入')
card(d,(800,315,1110,620),'A 已拍照','保持',BLUE)
for y,name,col,last in [(270,'B',GREEN,'标记已到：关闭 B→A'),(530,'C',GOLD,'标记未到：继续 C→A')]:
 d.ellipse((90,y-70,240,y+80),fill=col);txt(d,(165,y+5),name,55,'white','mm');arr(d,(270,y),(760,410 if name=='B' else 530),col);txt(d,(450,y+105),last,30,col,'mt')
save(im,'14-each-channel.png')
#15
im,d=base('同样是 8，两本账描述不同边界','蓝绿色是进程余额，金色是通道里的业务消息')
for y,title,vals in [(225,'实时现场',[7,1,0]),(475,'冻结快照',[5,1,2])]:
 txt(d,(60,y+40),title,35)
 for i,v in enumerate(vals):
  x=280+i*245;col=[BLUE,GREEN,GOLD][i];d.rounded_rectangle((x,y,x+180,y+145),18,fill=col);txt(d,(x+90,y+67),str(v),60,'white','mm')
  if i<2:txt(d,(x+212,y+70),'+',35,a='mm')
 txt(d,(1060,y+70),'= 8',45,a='mm')
for x,t in [(370,'P'),(615,'Q'),(860,'在途')]:txt(d,(x,680),t,35,a='mt')
save(im,'15-final-ledger.png')
#16
im,d=base('合法的组合，未必在原顺序中出现过','自设例子：P 与 Q 独立把自己的 0 变成 1，没有通信')
for y,title,states,col in [(265,'实际顺序',['(0,0)','(1,0)','(1,1)'],BLUE),(535,'交换独立事件',['(0,0)','(0,1)','(1,1)'],GREEN)]:
 txt(d,(75,y-75),title,33,col)
 for i,s in enumerate(states):
  x=130+i*365;d.rounded_rectangle((x,y,x+230,y+105),18,fill='#edf3f1',outline=col,width=3);txt(d,(x+115,y+52),s,44,col,'mm')
  if i<2:arr(d,(x+250,y+50),(x+340,y+50),col)
note(d,'(0,1) 没有违反因果关系，仍是合法图景',742,33);save(im,'16-equivalent-order.png')
#17
im,d=base('大家都不忙，计算就结束了吗？','前提：这一阶段不会再从外界注入新工作')
for x,t in [(100,'P 空闲'),(790,'Q 空闲')]:
 d.rounded_rectangle((x,245,x+310,475),22,fill='#edf3f1',outline=BLUE,width=3);txt(d,(x+155,332),t,39,BLUE,'mt')
arr(d,(425,350),(775,350),GOLD);d.rounded_rectangle((470,270,730,420),16,fill='#f8e9c9');txt(d,(600,308),'工作消息',35,GOLD,'mt');txt(d,(600,360),'还在路上',28,GOLD,'mt');note(d,'尚未结束：消息到达后会唤醒工作者',580,38,RED);note(d,'要检查本地状态，也要检查通道状态',695,34);save(im,'17-termination.png')
#18
im,d=base('把理论边界，带回真实工程','本文单轮模型没有自动解决右侧的问题')
for x,title,col,lines in [(60,'基础算法依赖',BLUE,['可靠、有序的逻辑通道','所有参与者能够被触达','标记最终得到处理']),(650,'工程上还要处理',RED,['失败、超时与可靠保存','多轮快照的身份与隔离','各处记录的收集与恢复'])]:
 d.rounded_rectangle((x,200,x+485,690),22,fill='#edf3f1',outline=col,width=3);txt(d,(x+35,232),title,38,col)
 for j,t in enumerate(lines):txt(d,(x+30,340+j*100),t,29)
save(im,'18-engineering-boundary.png')
