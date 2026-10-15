"""Original interval-analysis diagrams from the attached experiment."""
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
def numberline(d,y,lo,hi,limit=10,color=BLUE,label='',x0=145,x1=945):
    def x(v):return x0+(x1-x0)*v/limit
    d.line((x0,y,x1,y),fill=MUTED,width=4)
    for k in range(limit+1):
        d.line((x(k),y-9,x(k),y+9),fill=MUTED,width=3)
        text(d,x(k),y+25,str(k),36,MUTED,True)
    if hi is not None:d.line((x(lo),y,x(hi),y),fill=color,width=14);dot(d,x(hi),y,color,10)
    else:
        d.line((x(lo),y,x1+35,y),fill=color,width=13)
        d.polygon([(x1+65,y),(x1+20,y-24),(x1+20,y+24)],fill=color)
    dot(d,x(lo),y,color,10)
    if label:text(d,80,y-90,label,42,color)
def array(d,y,bad=False):
    for k in range(9):
        x=115+k*92;c=RED if k==8 else BLUE
        d.rectangle((x,y,x+82,y+90),fill=WHITE if k==8 else '#D9EBE9',outline=c,width=4)
        text(d,x+41,y+100,str(k),40,c,True)
    text(d,531,y+185,'长度8：合法下标是0到7',42,BLUE,True)
#01
im,d=canvas('01','八个格子，最后一个叫7',1100)
text(d,531,185,'n = 8：需要清空八个位置',44,BLUE,True)
array(d,310)
text(d,531,650,'红框仅标位置：它不属于数组',40,RED,True)
text(d,531,800,'i < n：停在访问下标8之前',42,GREEN,True)
text(d,531,900,'i <= n：会试着再多走一步',42,RED,True)
save(im,'01-eight-cells.png','Fixed eight-cell array and boundary distinction')
#02 concrete reachable cloud
im,d=canvas('02','许多次运行，汇成一片状态',1250)
text(d,531,170,'每个点都是一组实际的(n,i)',40,BLUE,True)
ox,oy,step=160,990,86
for n in range(9):
 for i in range(9):
  d.ellipse((ox+n*step-4,oy-i*step-4,ox+n*step+4,oy-i*step+4),fill='#CCD6D8')
for r in R['concrete_good']['heads']:dot(d,ox+r['n']*step,oy-r['i']*step,ORANGE,13)
for r in R['concrete_good']['accesses']:dot(d,ox+r['n']*step,oy-r['i']*step,GREEN,13)
arrow(d,[(ox-30,oy+30),(940,oy+30)],INK,4);arrow(d,[(ox-30,oy+30),(ox-30,245)],INK,4)
for k in [0,2,4,6,8]:
 text(d,ox+k*step,oy+45,str(k),36,MUTED,True);text(d,80,oy-k*step-27,str(k),36,MUTED,True)
text(d,963,1018,'n',40);text(d,80,230,'i',40)
dot(d,150,1140,GREEN,13);text(d,180,1110,'36个访问点',38,GREEN)
dot(d,590,1140,ORANGE,13);text(d,620,1110,'退出前的i=n',38,ORANGE)
save(im,'02-concrete-state-cloud.png','Actual enumeration of all nine allowed inputs; head and access states')
#03
im,d=canvas('03','把散落的值，装进一个区间',1180)
text(d,531,190,'具体集合：{0, 2, 5}',46,BLUE,True)
numberline(d,420,0,5,6,BLUE)
for k in [0,2,5]:dot(d,145+800*k/6,420,ORANGE,18)
text(d,531,560,'区间 [0,5] 还装入了1、3、4',42,ORANGE,True)
numberline(d,800,0,5,6,GREEN)
text(d,531,960,'可以多装；不能漏掉真实可能值',42,GREEN,True)
save(im,'03-set-to-interval.png','Overapproximation of a sparse finite set by an integer interval')
#04
im,d=canvas('04','把每个值加1，区间怎样变？',1160)
numberline(d,340,0,7,9,BLUE,'执行之前：i ∈ [0,7]')
arrow(d,[(531,470),(531,595)],ORANGE)
text(d,700,495,'i = i + 1',42,ORANGE,True)
numberline(d,760,1,8,9,GREEN,'执行之后：i ∈ [1,8]')
text(d,531,965,'只计算两个端点，也覆盖所有整数',40,GREEN,True)
save(im,'04-transfer-add-one.png','Actual interval transformer for one increment')
#05
im,d=canvas('05','两条分支汇合，保留所有来路',1300)
box(d,(80,190,470,350),['分支甲','i = 2'],BLUE)
box(d,(590,190,982,350),['分支乙','i = 6'],ORANGE)
arrow(d,[(275,375),(275,535),(475,650)],BLUE)
arrow(d,[(785,375),(785,535),(585,650)],ORANGE)
numberline(d,800,2,6,8,GREEN,'合并：最小的包含区间 [2,6]')
for k in [2,6]:dot(d,145+800*k/8,800,ORANGE,18)
text(d,531,1010,'3、4、5也被包进来',42,MUTED,True)
text(d,531,1100,'这叫join：收集，不是取交集',42,GREEN,True)
save(im,'05-branch-join.png','Join operation and the precision lost when merging branches')
#06 loop graph
im,d=canvas('06','循环：消息会沿回边再次回来',1470)
box(d,(310,175,800,315),['入口：i = 0'],BLUE)
arrow(d,[(550,330),(550,400)],BLUE)
box(d,(310,415,800,565),['循环头 H','汇合入口与回边'],BLUE)
arrow(d,[(550,580),(550,650)],BLUE)
box(d,(310,665,800,805),['条件 i < n'],ORANGE)
arrow(d,[(550,820),(550,905)],GREEN)
text(d,680,830,'成立',38,GREEN)
box(d,(310,920,800,1090),['访问 a[i]','i = i + 1'],GREEN)
arrow(d,[(550,1110),(550,1250),(130,1250),(130,490),(290,490)],ORANGE)
text(d,190,1320,'回边带回“加1之后”的范围',40,ORANGE)
arrow(d,[(800,735),(930,735),(930,980)],MUTED)
text(d,790,825,'不成立',38,MUTED)
box(d,(835,1000,1020,1160),['退出'],MUTED)
save(im,'06-loop-control-flow.png','Loop entry, guard, body and feedback into one head invariant')
#07 actual interval iterations
im,d=canvas('07','循环头的区间怎样长大？',1420)
text(d,531,170,'实际求解轨迹；上界每轮扩大1',40,BLUE,True)
x0=325;step=70
for k,r in enumerate(R['good']['trace']):
 y=300+k*100;hi=r['head'][1]
 text(d,80,y-25,f'第{k}轮',38,MUTED)
 d.line((x0,y,x0+8*step,y),fill='#D9E0E1',width=20)
 d.line((x0,y,x0+hi*step,y),fill=GREEN if k==8 else BLUE,width=20)
 dot(d,x0,y,BLUE,12);dot(d,x0+hi*step,y,GREEN if k==8 else BLUE,12)
 text(d,951,y-28,str(hi),38,GREEN if k==8 else BLUE,True)
text(d,531,1270,'到 [0,8]：再传一圈，仍是 [0,8]',40,GREEN,True)
save(im,'07-fixpoint-iterations.png','Recorded interval-head iteration through a fixed point')
#08 inductive
im,d=canvas('08','为什么一张区间证书管得住循环？',1350)
box(d,(80,190,982,365),['① 起点在里面','i=0 属于 H=[0,8]'],BLUE)
arrow(d,[(531,385),(531,445)],BLUE)
box(d,(80,465,982,700),['② 经过条件，身体只剩 [0,7]','加1后得到 [1,8]','仍然回到 H 里面'],GREEN)
arrow(d,[(531,720),(531,780)],GREEN)
box(d,(80,800,982,1035),['③ 所有实际访问都在 [0,7]','恰好落在数组合法下标内'],GREEN)
text(d,531,1150,'入口 + 保持 + 安全位置',44,BLUE,True)
save(im,'08-inductive-certificate.png','Three local obligations proving the whole-loop access property')
#09 mutant actual
im,d=canvas('09','把 < 改成 <=，多出来哪个点？',1280)
ox,oy,step=160,990,86
for r in R['concrete_bad']['accesses']:
 dot(d,ox+r['n']*step,oy-r['i']*step,GREEN if r['safe'] else RED,15)
arrow(d,[(ox-30,oy+30),(940,oy+30)],INK,4);arrow(d,[(ox-30,oy+30),(ox-30,245)],INK,4)
for k in [0,2,4,6,8]:
 text(d,ox+k*step,oy+45,str(k),36,MUTED,True);text(d,80,oy-k*step-27,str(k),36,MUTED,True)
text(d,963,1018,'n',40);text(d,80,230,'i',40)
text(d,530,175,'45次访问尝试；1次越界',42,RED,True)
arrow(d,[(620,245),(820,290)],RED)
text(d,525,260,'(8,8)',40,RED)
text(d,531,1135,'抽象范围 [0,8] 碰到了危险下标8',40,RED,True)
save(im,'09-mutated-real-counterexample.png','Actual enumeration of mutated loop with one illegal access')
#10 widening
im,d=canvas('10','上界总在增长，先把围栏放远',1380)
for k,(label,hi,col) in enumerate([('第0轮：[0,0]',0,BLUE),('第1轮：[0,1]',1,BLUE),('第2轮：[0,2]',2,BLUE),('看到上界3：加宽到 [0,+∞]',None,ORANGE)]):
 numberline(d,330+k*240,0,hi,8,col,label)
text(d,531,1255,'+∞ 表示没有有限上界，不是一个值',38,ORANGE,True)
save(im,'10-widening.png','Delayed widening from the recorded sequence to an unbounded interval')
#11 narrowing
im,d=canvas('11','区间放宽后，条件仍能帮忙',1420)
numberline(d,325,0,None,9,ORANGE,'循环头：[0,+∞]')
text(d,531,495,'i < n 且 n ≤ 8',44,GREEN,True)
numberline(d,710,0,7,9,GREEN,'访问位置：[0,7]，仍可证明安全')
text(d,531,900,'加1，再与入口0合并',42,BLUE,True)
numberline(d,1120,0,8,9,BLUE,'本例重新收窄：[0,8]')
save(im,'11-guard-and-narrowing.png','Guard recovers the finite access bound even after widening')
#12 correlation plane
im,d=canvas('12','两个真状态，怎么变出了假状态？',1320)
ox,oy,sz=270,880,510
rectangle=(ox,oy-sz,ox+sz,oy);d.rectangle(rectangle,fill='#DCE9E9',outline=ORANGE,width=5)
arrow(d,[(ox-50,oy+40),(935,oy+40)],INK,4);arrow(d,[(ox-50,oy+40),(ox-50,260)],INK,4)
for x,y in R['correlation']['concrete_pairs']:
 dot(d,ox+x*sz,oy-y*sz,GREEN,19)
for x,y in [(0,0),(1,1)]:
 px,py=ox+x*sz,oy-y*sz;d.line((px-17,py-17,px+17,py+17),fill=RED,width=7);d.line((px-17,py+17,px+17,py-17),fill=RED,width=7)
text(d,ox-15,oy+75,'0',40);text(d,ox+sz,oy+75,'1',40,center=True);text(d,160,oy-sz-30,'1',40);text(d,945,920,'x',40);text(d,195,250,'y',40)
text(d,531,175,'真实：(0,1) 或 (1,0)',44,GREEN,True)
text(d,830,300,'(1,1)',38,RED,True)
text(d,531,1080,'独立区间：[0,1] × [0,1]',42,ORANGE,True)
text(d,531,1170,'红叉没有真的发生，却被盒子装进来',38,RED,True)
save(im,'12-lost-correlation.png','Exact reachable pairs versus product interval and spurious corners')
#13 precision fix
im,d=canvas('13','留住“二者相加总是1”',1280)
ox,oy,sz=280,840,500
arrow(d,[(ox-50,oy+40),(940,oy+40)],INK,4);arrow(d,[(ox-50,oy+40),(ox-50,260)],INK,4)
d.line((ox,oy-sz,ox+sz,oy),fill=BLUE,width=8)
for x,y in [(0,1),(1,0)]:dot(d,ox+x*sz,oy-y*sz,GREEN,19)
text(d,531,185,'关系：x + y = 1',46,BLUE,True)
text(d,ox,oy+75,'0',40,center=True);text(d,ox+sz,oy+75,'1',40,center=True);text(d,165,oy-sz-25,'1',40);text(d,950,880,'x',40);text(d,190,245,'y',40)
text(d,531,1010,'或者保留两条分支，不急着合并',40,GREEN,True)
text(d,531,1110,'得到 j = 1；长度2的数组可安全访问',38,GREEN,True)
save(im,'13-restore-relation.png','Relational equality or disjunctive states eliminate the false alarm')
#14 proof vs uncertainty
im,d=canvas('14','围栏碰到危险区，结论还差一步',1350)
for y,hi,label,col in [(420,7,'范围完全留在合法区：已证明',GREEN),(950,8,'范围碰到下标8：发出警报',ORANGE)]:
 d.rounded_rectangle((790,y-75,995,y+110),radius=15,fill='#F3D7D7')
 numberline(d,y,0,hi,9,col,label,x0=145,x1=945)
 text(d,915,y-155,'危险区',38,RED,True)
text(d,531,1150,'警报可能来自真越界，也可能是假状态',38,RED,True)
save(im,'14-proof-versus-alarm.png','Safe overapproximation versus one intersecting the error region')
# separate cover
im,d=canvas('cover','不运行程序，先给下标画围栏',1062)
text(d,531,200,'抽象解释',66,BLUE,True,True)
for k in range(8):
 x=139+100*k;d.rectangle((x,400,x+85,510),fill='#D8EBE5',outline=GREEN,width=4);text(d,x+42,535,str(k),44,GREEN,True)
d.rounded_rectangle((105,365,962,625),radius=28,outline=GREEN,width=8)
arrow(d,[(531,670),(531,755)],BLUE)
text(d,531,790,'许多条执行路径',46,BLUE,True)
text(d,531,875,'一份包含它们的范围证明',46,GREEN,True)
im.save(O/'cover.png');metadata.append(dict(file='cover.png',width=W,height=1062,min_font_px=44,min_effective_px_at_354=44/3,role='Separate original cover with actual eight-element index layout',identity='original teaching illustration'))
(O/'examples').mkdir(exist_ok=True);(O/'examples/figure-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
print('Drew 14 body figures and a separate cover')
