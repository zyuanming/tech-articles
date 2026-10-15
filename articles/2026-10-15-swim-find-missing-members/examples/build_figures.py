#!/usr/bin/env python3
"""Original explanatory figures and plots from recorded run outputs. MIT."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,json,math,re
A=Path(__file__).resolve().parents[1];O=A/'assets';O.mkdir(exist_ok=True)
R=json.loads((A/'examples/results.json').read_text());U=json.loads((A/'originals/udp-results.json').read_text());E=list(csv.DictReader((A/'examples/events.csv').open()));G=list(csv.DictReader((A/'examples/gossip-contacts.csv').open()))
BG='#f4f3ed';WHITE='#ffffff';INK='#183440';TEAL='#147d84';BLUE='#3468ad';AMBER='#ab640b';RED='#bc4650';GRAY='#697c82';LIGHT='#dce6e3';PALE='#e8f0f6'
F='/usr/share/fonts/opentype/noto/NotoSansCJK-';font=lambda n,b=False:ImageFont.truetype(F+('Bold' if b else 'Regular')+'.ttc',n,index=2)
meta=[];checks=[]
def start(title,h=1000):
 global im,d,mn
 im=Image.new('RGB',(1062,h),BG);d=ImageDraw.Draw(im);mn=100;txt((48,35),title,48,True)
def txt(pos,s,n=40,b=False,c=INK,anchor=None):
 global mn
 mn=min(mn,n);box=d.textbbox(pos,s,font=font(n,b),anchor=anchor)
 assert box[0]>=0 and box[2]<=1062 and box[1]>=0 and box[3]<=im.height,(s,box,im.size)
 d.text(pos,s,font=font(n,b),fill=c,anchor=anchor)
def line(a,b,c=GRAY,w=5):d.line([a,b],fill=c,width=w)
def arr(a,b,c=TEAL,w=7):
 line(a,b,c,w);t=math.atan2(b[1]-a[1],b[0]-a[0]);r=22;pts=[b,(b[0]-r*math.cos(t-.48),b[1]-r*math.sin(t-.48)),(b[0]-r*math.cos(t+.48),b[1]-r*math.sin(t+.48))];d.polygon(pts,fill=c)
def box(x,y,w,h,fill=WHITE,outline=LIGHT,r=22):d.rounded_rectangle((x,y,x+w,y+h),radius=r,fill=fill,outline=outline,width=3)
def node(x,y,label,c=TEAL,r=49):d.ellipse((x-r,y-r,x+r,y+r),fill=BG,outline=c,width=6);txt((x,y-3),label,48,True,c,anchor='mm')
def save(name,purpose,identity='原创机制示意'):
 p=O/name;im.save(p);meta.append(dict(path='assets/'+name,width=im.width,height=im.height,min_label_px=mn,effective_min_at_354px=mn/3,purpose=purpose,identity=identity))

start('同一句“没回音”，两种真实可能',1050)
for y,title,alive in [(140,'B真的停了',False),(575,'B还在运行，往返不通',True)]:
 box(42,y,978,380);txt((78,y+26),title,44,True);node(170,y+190,'A');node(875,y+190,'B',TEAL if alive else GRAY)
 arr((225,y+165),(795,y+165),BLUE);txt((405,y+100),'还在吗？',40,c=BLUE)
 if alive:
  arr((820,y+225),(300,y+225),RED);txt((440,y+250),'回信没送到',40,c=RED);line((515,y+200),(550,y+240),RED,9);line((550,y+200),(515,y+240),RED,9)
 else:txt((385,y+250),'没有产生回信',40,c=GRAY)
save('01-silence-worlds.png','相同观察不能区分进程停机与消息失败')

start('六个成员，一轮发送量差多少？',1610)
coords=[(531+275*math.cos(-math.pi/2+i*math.pi/3),480+230*math.sin(-math.pi/2+i*math.pi/3)) for i in range(6)]
for off,full in [(0,True),(740,False)]:
 txt((70,130+off),'每人给其余五人发心跳' if full else '每人挑一人：PING + ACK',42,True)
 ps=[(x,y+off) for x,y in coords]
 if full:
  for i,a in enumerate(ps):
   for j,b in enumerate(ps):
    if i<j:line(a,b,LIGHT,6)
 else:
  targets=[2,3,4,5,0,1]
  for i,j in enumerate(targets):
   a,b=ps[i],ps[j];v=(b[0]-a[0],b[1]-a[1]);l=math.hypot(*v);arr((a[0]+50*v[0]/l,a[1]+50*v[1]/l),(b[0]-52*v[0]/l,b[1]-52*v[1]/l),BLUE,5)
 for n,(x,y) in zip('ABCDEF',ps):node(x,y,n)
 txt((531,810 if full else 1550),'30封心跳（线代表双向）' if full else '6封PING + 6封ACK = 12封',40,True,anchor='mm')
save('02-message-networks.png','同样六成员下比较全互联心跳与健康探测；箭头仅PING')

start('成员表，是每个人手里的看法',850)
for y,owner,status,c in [(150,'A','B：怀疑，代号0',AMBER),(470,'E','B：活着，代号0',TEAL)]:
 box(55,y,952,255);node(155,y+120,owner);txt((280,y+48),'本地成员表的一条记录',40);txt((280,y+125),status,46,True,c)
txt((531,790),'两份表可以暂时不同。',42,True,anchor='mm')
save('03-local-views.png','一台机器的判断和整个系统当前视图不同')

def trace(case,name,title,filterfn,height=1080,max_t=180):
 rows=[r for r in E if r['case']==case];start(title,height);xs={'A':215,'C':595,'B':960};top=230;scale=(height-350)/max_t
 for n,x in xs.items():
  if case=='healthy' and n=='C':continue
  txt((x,150),n,46,True,anchor='mm');line((x,195),(x,height-75),LIGHT,5)
 ts=sorted(set(float(r['t_ms']) for r in rows if r['event']=='SEND' and filterfn(r)))
 for t in sorted(set(ts+[max_t])):txt((30,top+t*scale-22),str(int(t)),38,c=GRAY)
 for r in rows:
  if r['event']!='SEND' or not filterfn(r):continue
  pid=r['note'].split(';')[0];dest=next(z for z in rows if z['event'] in ('DROP','RECEIVE') and z['note'].split(';')[0]==pid)
  s,t=float(r['t_ms']),float(dest['t_ms']);a=(xs[r['src']],top+s*scale);b=(xs[r['dst']],top+t*scale);col=RED if dest['event']=='DROP' else (TEAL if 'ACK' in r['kind'] else BLUE);arr(a,b,col,7)
  lab={'PING_REQ':'PING_REQ(B)','ACK_RELAY':'转发 ACK'}.get(r['kind'],r['kind']);label_y=min(a[1],b[1])-52 if r['kind']=='PING_REQ' else (a[1]+b[1])/2-31
  txt(((a[0]+b[0])/2,label_y),lab,38,True,col,anchor='mm')
  if dest['event']=='DROP':line((b[0]-15,b[1]-15),(b[0]+15,b[1]+15),RED,8);line((b[0]-15,b[1]+15),(b[0]+15,b[1]-15),RED,8)
 txt((60,height-60),'时间：虚拟毫秒，向下增加',38,c=GRAY)
 save(name,'从真实执行的离散事件CSV筛选该路径，逐个显示发送和到达时间','实际运行的教学模型事件轨迹；非网络抓包')
trace('healthy','04-direct-trace.png','直接探测：40毫秒收到回信',lambda r:r['src'] in 'AB' and r['dst'] in 'AB',720,40)
trace('indirect','05-indirect-trace.png','借C绕行：D的并行路径未画',lambda r:r['src'] in 'ABC' and r['dst'] in 'ABC',1180,180)

start('B短暂停顿：A的记录怎样变？',1070)
txt((65,125),'B在350毫秒恢复；A尚不知道。',39)
for y,tm,state,c in [(255,'0','活着 · 0',TEAL),(455,'300','怀疑 · 0',AMBER),(655,'520','活着 · 1',TEAL),(855,'900','旧计时器无效',GRAY)]:
 txt((130,y),tm,44,True,anchor='mm');node(320,y,'A',c);box(430,y-64,560,128);txt((710,y),state,45,True,c,anchor='mm')
 if y<855:arr((320,y+60),(320,y+138),GRAY,5)
txt((65,990),'时间：虚拟毫秒；数字是B的代号。',38,c=GRAY)
save('06-suspicion-timeline.png','显示怀疑是过渡状态以及更新代号取消旧怀疑超时','实际教学模型事件：300怀疑、520恢复、900取消')

start('怀疑先到B，反驳再带回来',1340)
steps=[('400 → 420','A → C','PING 搭载：怀疑B，0',AMBER),('440 → 460','C → B','PING 搭载：怀疑B，0',AMBER),('460','B自己更新','代号 0 → 1，声明活着',TEAL),('460 → 480','B → C','ACK 搭载：活着B，1',TEAL),('500 → 520','C → A','PING 搭载：活着B，1',TEAL)]
for i,(tm,route,msg,c) in enumerate(steps):
 y=145+i*225;box(55,y,952,190);txt((85,y+22),tm+' ms',38,c=GRAY);txt((500,y+22),route,42,True,c);txt((85,y+100),msg,42,True)
 if i<4:arr((531,y+192),(531,y+220),c,5)
save('07-refutation-route.png','把传播、本人递增、反驳返回拆成五步','实际执行的教学模型事件；未绘制不改变结论的ACK')

start('迟到的旧消息，不能让记录倒退',1320)
items=[('已经记录：怀疑B，0','又收到：活着B，0','不变：旧“活着”不够新',AMBER),('已经记录：怀疑B，0','又收到：活着B，1','更新：B给出了新一版',TEAL),('已经记录：活着B，1','又收到：怀疑B，0','不变：这次怀疑已过时',TEAL),('已经记录：确认移除B','又收到：普通Alive','原论文中，不能这样复活',RED)]
for i,(a,b,c,col) in enumerate(items):
 y=140+i*285;box(48,y,966,253);txt((78,y+24),a,42,True);txt((78,y+94),b,40,c=GRAY);txt((78,y+164),c,40,True,col)
save('08-message-order.png','版本号、同版本怀疑优先和原论文Confirm终态','原创规则图；前3类由merge测试与乱序枚举核验')

start('同一条更新，怎样传到六个人？',1130)
txt((55,125),'蓝色“知”＝已收到这条更新',40,c=BLUE)
for j,n in enumerate('ABCDEF'):txt((290+j*130,225),n,42,True,anchor='mm')
for i,row in enumerate(R['gossip'][:5]):
 y=350+i*150;txt((55,y),f'第{row["round"]}轮',40,True,anchor='lm')
 for j,n in enumerate('ABCDEF'):
  x=290+j*130;yes=n in row['known'];box(x-48,y-48,96,96,BLUE if yes else WHITE)
  txt((x,y),'知' if yes else '·',42,True,WHITE if yes else GRAY,anchor='mm')
txt((531,1060),'人数：1 → 2 → 4 → 6',42,True,anchor='mm')
save('09-gossip-spread.png','逐轮逐节点展示一次固定种子的传播过程','独立的六成员无丢包ping/ack搭载模型，seed=2301')

start('省下的是每个人的探测工作',1160)
ys=[270,560,850]
for row,y in zip(R['loads'],ys):
 box(55,y-95,952,270);txt((85,y-65),f'{row["n"]}个成员',44,True);txt((85,y+10),'全互联心跳',40,c=GRAY);txt((945,y+10),f'{row["all_to_all_heartbeats"]:,}封',46,True,AMBER,anchor='ra');txt((85,y+90),'健康PING / ACK',40,c=GRAY);txt((945,y+90),f'{row["healthy_ping_ack"]:,}封',46,True,TEAL,anchor='ra')
txt((55,1050),'均按一轮；尚未计入失败时的间接探测。',38)
save('10-message-counts.png','以公式逐项计算6、100、1000成员的消息数','Python整数计算结果，不是吞吐量压测')

start('只问一个，为什么仍常能很快碰到？',1170)
box(55,145,952,235);txt((85,178),'六人中B停止，另外五人各选一人。',39,True);txt((85,255),'每人恰好选中B的概率：1 / 5',42,True,BLUE)
for i,n in enumerate('ACDEF'):
 x=135+i*195;node(x,475,n);txt((x,580),'没选B',38,anchor='mm');txt((x,640),'4 / 5',40,True,anchor='mm')
box(55,745,952,310);txt((85,780),'五人都没选中：(4 / 5)^5 = 0.32768',40);txt((85,865),'至少一人选中：1 − 0.32768',40);txt((85,950),'= 0.67232，也就是约67.2%',44,True,TEAL)
save('11-probe-probability.png','先算全部没选中，再用补集得到至少一人选中概率','作者对明确独立均匀抽样模型的手算与代码核验')

start('真实UDP：这一次运行的事件记录',1370)
txt((55,125),'横轴：实际经过的毫秒',40);xs=lambda t:150+2.7*t
for i,(row,label,col) in enumerate(zip(U['cases'],['正常回信','直达路径被忽略','B忽略所有探测'],[TEAL,BLUE,RED])):
 y=290+i*335;txt((55,y-110),label,43,True,col);line((150,y),(960,y),GRAY,4)
 for t in (0,100,200,300):line((xs(t),y-12),(xs(t),y+12),GRAY,4);txt((xs(t),y+47),str(t),38,anchor='mm')
 ev=[e for e in csv.DictReader((A/'originals/udp-events.csv').open()) if e['case']==row['case'] and e['event']=='SEND']
 for k,e in enumerate(ev):x=xs(float(e['t_ms']));d.ellipse((x-8,y-8-(k%2)*27,x+8,y+8-(k%2)*27),fill=col)
 if row['ack_ms'] is not None:
  x=xs(row['ack_ms']);line((x,y-27),(x,y+17),col,8);txt((55,y+115),f'首个ACK：{row["ack_ms"]:.1f} ms；发送{row["udp_sent"]}包',40,True,col)
 else:txt((55,y+115),f'{row["deadline_ms"]:.1f} ms检查：无ACK；发送5包',40,True,col)
txt((55,1265),'圆点＝sendto日志；每次处理故意等20 ms。',38)
save('12-real-udp-log.png','把实际socket实验的发包时刻和首次ACK画出来','本次真实localhost UDP应用日志；非pcap、非性能测量')

start('换两条路，也可能一起走不通',1060)
for x,n in [(170,'A'),(530,'C'),(890,'D')]:node(x,240,n)
node(531,790,'B',RED);box(55,430,952,150,PALE);txt((531,505),'三条路共享的网络故障',44,True,RED,anchor='mm')
for x in (170,530,890):
 arr((x,295),(x,420),BLUE);line((x,590),(531,725),GRAY,5);line((x-20,380),(x+20,420),RED,9);line((x-20,420),(x+20,380),RED,9)
txt((531,970),'路径数量增加 ≠ 故障彼此独立',43,True,anchor='mm')
save('13-correlated-paths.png','间接探测无法解决共因断网或目标整体停顿')

start('有时，慢的是负责检查的人',960)
node(170,260,'B');node(890,260,'A',AMBER);arr((235,260),(815,260),TEAL);txt((531,200),'回信已经到达',42,True,TEAL,anchor='mm')
box(100,420,862,245);txt((145,455),'A的本地处理队列',44,True);txt((145,545),'繁忙任务 → 繁忙任务 → ACK',40,c=GRAY)
arr((531,675),(531,765),AMBER);txt((531,830),'计时器先到，ACK却还没被处理',42,True,AMBER,anchor='mm')
save('14-slow-observer.png','观察者自身过载可引发误判，衔接Lifeguard')

start('“我不再联系你”不会让你停机',1100)
box(55,150,952,270);txt((95,188),'A的成员表',44,True);txt((95,275),'B：确认移除',46,True,RED);node(850,290,'A')
node(220,620,'B',TEAL);txt((410,590),'B可能仍在另一侧运行',40,True);arr((220,680),(220,865),TEAL)
box(420,800,585,170);txt((710,885),'仍可能写入共享资源',40,True,anchor='mm');arr((280,885),(405,885),RED)
txt((55,1020),'成员状态，不是独占写入权限。',42,True)
save('15-membership-not-authority.png','成员发现与授权/隔离边界可见，不重复讲共识协议')

# Independent cover, not an article figure or historical photo.
start('没有总管点名',760);txt((48,112),'服务器怎样发现谁掉队？',52,True)
positions=[(150,330),(540,300),(900,350),(185,620),(540,585),(905,625)]
for i,j in [(0,1),(1,2),(0,3),(1,4),(2,5),(3,4),(4,5)]:line(positions[i],positions[j],LIGHT,9)
for n,(x,y) in zip('ABCDEF',positions):node(x,y,n,AMBER if n=='B' else TEAL,58)
txt((540,435),'PING？',55,True,BLUE,anchor='mm');txt((540,712),'SWIM · 探测、怀疑与反驳',42,True,anchor='mm');im.save(A/'cover.png')
meta.append(dict(path='cover.png',width=im.width,height=im.height,min_label_px=mn,effective_min_at_354px=mn/3,purpose='独立封面',identity='原创程序绘制；非历史照片或真实设备'))
(A/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(f'Rendered {len(meta)-1} body images and one independent cover. All labels >= {min(x["min_label_px"] for x in meta)} px at 1062px width.')
