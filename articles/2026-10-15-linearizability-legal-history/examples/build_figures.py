#!/usr/bin/env python3
"""Original instructional drawings and data-derived figures; requires Pillow."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import argparse,json,math
ROOT=Path(__file__).resolve().parent.parent
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
BG='#F5F3EA'; INK='#17333D'; BLUE='#236B8E'; GREEN='#23785A'; RED='#AD413F'; GOLD='#AD7022'; LIGHT='#E2E8E7'
W=1062
meta=[]
def font(n=40,bold=False):return ImageFont.truetype(BOLD if bold else FONT,n,index=2)
def text(x,y,s,n=40,fill=INK,bold=False):d.text((x,y),s,font=font(n,bold),fill=fill)
def canvas(title,h=720):
 global im,d
 im=Image.new('RGB',(W,h),BG);d=ImageDraw.Draw(im)
 size=48
 while d.textlength(title,font=font(size,True))>978:size-=1
 assert size>=36
 text(42,28,title,size,bold=True);d.line((42,104,1020,104),fill=INK,width=3)
def box(x,y,w,h,label,color=BLUE):
 d.rounded_rectangle((x,y,x+w,y+h),radius=18,fill=color);f=font(42,True);bb=d.textbbox((0,0),label,font=f);d.text((x+(w-bb[2])/2,y+(h-bb[3])/2-4),label,font=f,fill='white')
def arrow(x1,y1,x2,y2,color=INK,width=6):
 d.line((x1,y1,x2,y2),fill=color,width=width);a=math.atan2(y2-y1,x2-x1);s=20
 pts=[(x2,y2),(x2-s*math.cos(a-.5),y2-s*math.sin(a-.5)),(x2-s*math.cos(a+.5),y2-s*math.sin(a+.5))];d.polygon(pts,fill=color)
def save(name,role):
 im.save(out/name);meta.append({'file':name,'width':W,'height':im.height,'minimum_text_px':36,'effective_minimum_at_354px':12,'role':role})
def timeline(title,ops,foot,name,points=None,pending=False):
 canvas(title,700)
 left,right=220,970
 def xx(v):return left+(v-1)*(right-left)/5
 for k in range(1,7):
  x=xx(k);d.line((x,155,x,535),fill='#D3DAD7',width=2);text(x-12,545,str(k),36)
 for j,(label,start,end,color) in enumerate(ops):
  y=205+j*135;text(42,y-30,label,42,bold=True)
  a,b=xx(start),xx(end if end is not None else 6)
  d.line((a,y,b,y),fill=color,width=14);d.ellipse((a-10,y-10,a+10,y+10),fill=color)
  if end is not None:d.line((b,y-22,b,y+22),fill=color,width=7)
  else:arrow(b-42,y,b,y,color)
  if points and j in points:
   x=xx(points[j]);d.ellipse((x-15,y-15,x+15,y+15),fill=GOLD,outline='white',width=4)
 text(42,605,foot,40)
 save(name,'原创调用—返回区间示意；横轴为事件序号，非持续时间')
p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
results=json.loads((ROOT/'examples/expected-results.json').read_text())
canvas('先规定：这块牌只有一个格子',770)
box(380,155,300,170,'当前值：0',INK)
box(45,420,410,100,'写入 1 → 确认',BLUE);box(607,420,410,100,'读取 → 返回格内值',GREEN)
arrow(250,420,425,325,BLUE);arrow(650,325,805,420,GREEN)
text(75,575,'写入后：格子从 0 变成 1',44)
text(75,640,'读取只看值，不把值取走',44)
save('01-register.png','把对象、状态和两种操作分开，建立顺序规格')
canvas('一个请求有两个外部可见端点',700)
text(55,155,'调用：发出“写 1”',44);text(570,155,'返回：收到确认',44)
arrow(180,220,180,295,BLUE);arrow(875,220,875,295,GREEN)
d.line((180,325,875,325),fill=BLUE,width=18)
d.line((180,290,180,360),fill=BLUE,width=8);d.line((875,290,875,360),fill=GREEN,width=8)
text(180,410,'这段区间内：可能正在等待或执行',42)
text(180,490,'仅凭端点，看不到内部哪刻改了值',40)
arrow(180,590,875,590);text(385,610,'真实先后 →',40)
save('02-interval.png','区分调用、返回和不可直接观察的内部生效时刻')
timeline('先读 0，后读 1：可以解释',[('写1',1,6,BLUE),('A→0',2,3,GREEN),('B→1',4,5,GREEN)],'一种摆法：A → 写1 → B','03-legal.png',{0:3.5,1:2.5,2:4.5})
timeline('先读 1，后读 0：这次不行',[('写1',1,6,BLUE),('A→1',2,3,RED),('B→0',4,5,RED)],'只有一次写1，没有任何写0','04-illegal.png')
canvas('三条必须成立的箭头，绕成了圈',870)
box(380,160,300,100,'写1',BLUE);box(680,495,300,100,'A读到1',RED);box(75,495,300,100,'B读到0',RED)
arrow(650,280,805,465,BLUE);arrow(660,545,395,545,INK);arrow(240,470,410,280,GREEN)
text(840,325,'要先写',40,BLUE);text(432,580,'A先返回',38);text(425,630,'B才调用',38)
text(45,325,'要还没写',40,GREEN)
text(68,750,'写1 → A → B → 写1：无法排成直线',40,bold=True)
save('05-cycle.png','将读值约束与真实先后拼成矛盾环，给出不可行证据')
timeline('最小的过期读反例',[('写1',1,2,BLUE),('A→0',4,5,RED)],'写入已确认，随后开始的读却返回0','06-stale.png')
canvas('选一个端点排序，会误杀合法历史',960)
def small(y,label,ops,caption):
 text(44,y,label,44,bold=True)
 for j,(s,a,b,col) in enumerate(ops):
  yy=y+105+j*105;text(55,yy-26,s,40);x1=280+(a-1)*210;x2=280+(b-1)*210;d.line((x1,yy,x2,yy),fill=col,width=13);d.line((x1,yy-18,x1,yy+18),fill=col,width=5);d.line((x2,yy-18,x2,yy+18),fill=col,width=5)
 text(55,y+275,caption,38)
small(140,'按调用排序？',[('读→1',1,4,GREEN),('写1',2,3,BLUE)],'读先调用，但可在写入之后才取值')
small(545,'按返回排序？',[('写1',1,4,BLUE),('读→1',2,3,GREEN)],'读先返回，但写入可已生效、尚未确认')
save('07-endpoint-sorting.png','两个不同嵌套历史分别反驳调用排序和返回排序')
canvas('尝试下一步：先后关系和读值都要过关',1060)
box(350,145,360,90,'初始状态 0',INK)
box(35,370,300,90,'先 A→0',GREEN);box(380,370,300,90,'先 写1',BLUE);box(725,370,300,90,'先 B→1',RED)
arrow(450,245,180,350,GREEN);arrow(530,245,530,350,BLUE);arrow(610,245,870,350,RED)
text(47,485,'可继续',40,GREEN);text(385,485,'此后A要读0',38,RED);text(730,485,'A必须先于B',38,RED)
box(35,660,300,90,'再 写1',BLUE);arrow(185,470,185,640,BLUE)
box(35,865,300,90,'再 B→1',GREEN);arrow(185,760,185,845,GREEN)
text(400,690,'找到一条合法路线即可',42)
text(400,770,'不是要求所有排列都对',40)
text(400,850,'例：图3的同一组操作',38)
save('08-search.png','展示枚举分支及剪枝理由，而不是把搜索藏进黑箱')
canvas('程序真的跑过：原始事件记录的重绘',1220)
for k,(name,title) in enumerate([('locked_register','共享格子：A读0，B读1'),('injected_stale_read','故意旧缓存：A读1，B读0')]):
 y=145+k*500;text(45,y,title,44,bold=True)
 rows=results['threaded_runs'][name]['events'];base=rows[0]['elapsed_ns']
 text(50,y+68,'序号  操作与事件       相对首事件(ns)',36)
 for i,e in enumerate(rows):
  label=('调用写1' if e['id']=='W' else '调用读') if e['event']=='call' else '返回'+str(e['value'])
  text(50,y+125+i*54,f"{e['index']}   {e['id']} {label}",38)
  text(700,y+125+i*54,str(e['elapsed_ns']-base),38)
text(45,1160,'固定调度的本机线程；不是网络服务压测',38)
save('09-runtime-evidence.png','从本次CSV实际事件与单调时钟读数重绘，供读者对照原始日志')
canvas('有界枚举：检查这360份小历史',790)
box(60,160,420,110,'90种端点先后',BLUE);box(580,160,420,110,'4组读取结果',GOLD)
text(507,190,'×',46,bold=True)
text(65,320,'每组：一次写1、两次读，初值0',42)
counts=results['exhaustive'];total=360;x=65;y=430;wid=930;good=wid*counts['linearizable']/total
d.rectangle((x,y,x+good,y+105),fill=GREEN);d.rectangle((x+good,y,x+wid,y+105),fill=RED)
text(95,455,'246 可解释',44,'white',True);text(735,455,'114 不行',42,'white',True)
text(65,605,'两种检查方法：0次判定分歧',44)
text(65,685,'这不是对任意程序的正确性证明',40)
save('10-enumeration.png','以实际枚举结果展示有限测试范围与两种算法交叉核对')
canvas('没有返回的写：不能一律删掉',850)
box(48,150,965,100,'初值0；写1已调用，还没有返回',INK)
box(55,360,430,100,'读到1',GREEN);box(580,360,430,100,'读到0',GOLD)
arrow(310,270,270,340,GREEN);arrow(750,270,790,340,GOLD)
text(60,510,'需要保留待定写',42,GREEN);text(585,510,'可以暂不纳入写',42,GOLD)
text(60,590,'补上确认，再排：',40);text(585,590,'先只解释已完成读',38)
text(60,670,'写1 → 读1',44,bold=True);text(585,670,'也可排：读0 → 写1',38)
text(55,765,'“补返回”只是数学解释，不是真的替服务回复',36)
save('11-pending.png','待定写保留或删除的不同必要性；解释扩展历史不是网络重试')
timeline('尚未调用的写，不能救过去的读',[('A→1',1,2,RED),('写1',4,None,BLUE)],'读已结束，写才开始：不能把写搬到过去','12-no-future.png',pending=True)
canvas('一次读和一次写，不会自动合成一次操作',800)
box(50,170,390,90,'甲读0',BLUE);box(620,170,390,90,'乙读0',GREEN)
arrow(245,275,245,360,BLUE);arrow(815,275,815,360,GREEN)
box(50,390,390,90,'甲写1',BLUE);box(620,390,390,90,'乙写1',GREEN)
arrow(245,495,430,590,BLUE);arrow(815,495,630,590,GREEN)
box(330,620,400,100,'最终仍然是1',INK)
text(45,745,'每次读写都可合法；两次“加1”却没有合成2',36)
save('13-composition-limit.png','通过丢失更新说明单次操作线性一致不等于复合业务步骤原子')
canvas('这些并发操作',1062)
text(50,135,'能排成一条合法队伍吗？',58,bold=True)
for j,(label,a,b,col) in enumerate([('写1',1,6,BLUE),('读0',2,3,GREEN),('读1',4,5,GOLD)]):
 y=360+j*150;text(60,y-28,label,48,bold=True);x1=280+115*(a-1);x2=280+115*(b-1);d.line((x1,y,x2,y),fill=col,width=20);d.ellipse((x1-12,y-12,x1+12,y+12),fill=col);d.line((x2,y-25,x2,y+25),fill=col,width=8)
text(65,835,'线性一致性：为重叠的请求',48)
text(65,905,'找一个符合规则的先后解释',48)
save('cover.png','独立原创封面，不计入正文图数')
(out/'figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
