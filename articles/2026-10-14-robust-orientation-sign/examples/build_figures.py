"""Original robust-orientation diagrams from the attached experiment."""
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
#01
im,d=canvas('01','换起点，三角形会突然出现吗？',1160)
triangle(d,[(190,540),(780,540),(790,260)])
text(d,531,620,'同一数据；形状仅作示意',38,MUTED,True)
box(d,(70,730,992,880),['普通公式：A → B → C','算出0：以为共线'],RED,size=42)
box(d,(70,930,992,1080),['普通公式：B → C → A','算出1：逆时针'],GREEN,size=42)
save(im,'01-one-triangle-two-answers.png','Same triangle cyclic-order inconsistency; shape explicitly schematic')
#02
im,d=canvas('02','面向B：C在左边，还是右边？',1340)
for y,state,cY,val,col in [(200,'左侧',290,'D = +4',GREEN),(570,'右侧',800,'D = −4',RED),(940,'共线',1110,'D = 0',MUTED)]:
 text(d,70,y,state+'：'+val,44,col)
 a=(170,y+170);b=(900,y+170);c=(530,cY)
 arrow(d,[a,b],BLUE);point(d,a,'A',BLUE,-20,25);point(d,b,'B',BLUE,-20,25);point(d,c,'C',col,20,-55)
 if state!='共线':d.line([a,c,b],fill=col,width=4)
text(d,531,1260,'横轴向右，纵轴向上',40,BLUE,True)
save(im,'02-left-right-collinear.png','Orientation classification with one fixed directed horizontal edge')
#03
im,d=canvas('03','符号保存方向，大小对应面积',1090)
a=(170,670);b=(650,670);c=(410,430);q=(890,430)
d.polygon([a,b,q,c],fill='#DDECE7');d.line([a,b,q,c,a],fill=GREEN,width=5)
d.polygon([a,b,c],fill='#B8D8E2');arrow(d,[a,b],BLUE);arrow(d,[a,c],BLUE);d.line([b,c],fill=BLUE,width=6)
point(d,a,'A = (0,0)',BLUE,-75,35);point(d,b,'B = (4,0)',BLUE,-90,35);point(d,c,'C = (2,1)',BLUE,-85,-75)
text(d,531,210,'D = 4 × 1 − 0 × 2 = 4',46,GREEN,True)
box(d,(70,820,992,1010),['平行四边形面积：4','三角形面积：2；方向为逆时针'],GREEN,size=40)
save(im,'03-signed-area.png','Oriented parallelogram and triangle areas in introductory exact example')
#04
im,d=canvas('04','坐标没丢：两个乘积只差1',1370)
box(d,(75,180,987,440),['N = 2^27 = 134217728','A = (0,0)','B = (N,N−1)，C = (N+1,N)'],BLUE,size=40)
box(d,(75,520,987,750),['N × N','18014398509481984'],BLUE,size=46)
box(d,(75,830,987,1060),['(N−1) × (N+1)','18014398509481983'],ORANGE,size=46)
arrow(d,[(531,1075),(531,1140)],GREEN)
text(d,531,1170,'精确相减：D = 1',50,GREEN,True,True)
text(d,531,1260,'三角形面积是 1 / 2',42,GREEN,True)
save(im,'04-two-products-one-apart.png','Exact integer coordinates and large products')
#05
im,d=canvas('05','细小差别，在相减前就丢了',1150)
text(d,531,175,'令 P = 2^54',46,BLUE,True)
for x,label in [(200,'P−2'),(530,'P−1'),(860,'P')]:
 d.line((x,390,x,430),fill=INK,width=5);text(d,x,450,label,44,center=True)
d.line((170,410,900,410),fill=INK,width=5)
dot(d,200,410,BLUE,15);dot(d,860,410,BLUE,15);dot(d,530,410,ORANGE,13)
text(d,531,260,'P−1：在两个可表示数正中间',38,ORANGE,True)
arrow(d,[(545,360),(850,360)],ORANGE)
text(d,531,555,'就近舍入；中点取偶，落到P',40,ORANGE,True)
box(d,(75,680,987,910),['第一个乘积 → P','第二个乘积 → P','浮点相减：P − P = 0'],RED,size=44)
text(d,531,995,'不是显示隐藏了那个1',42,RED,True)
save(im,'05-rounded-before-subtract.png','Exact products and ties-to-even rounding around 2^54')
#06
im,d=canvas('06','循环换起点：方向本应不变',1210)
for i,(lab,calc,answer) in enumerate([('A → B → C','N² − (N²−1)','0'),('B → C → A','(−N+1) − (−N)','1'),('C → A → B','另一组小差值乘积','1')]):
 y=180+i*300;box(d,(75,y,987,y+250),[lab,calc,'普通浮点结果：'+answer],RED if i==0 else GREEN,size=40)
text(d,531,1110,'精确数学：三种顺序都是 +1',44,GREEN,True)
save(im,'06-cyclic-inconsistency.png','Recorded cyclic-order determinants versus exact invariance')
#07
im,d=canvas('07','同一凸包程序，删掉了不同的点',1330)
text(d,531,175,'展示坐标：X=x/N',40,BLUE,True)
text(d,531,235,'Y=N×y−(N−1)×x',40,BLUE,True)
for y,title,robust in [(350,'普通谓词：只剩A、C',False),(800,'可靠谓词：保留A、B、C',True)]:
 text(d,531,y,title,44,GREEN if robust else RED,True)
 def display(p):
  xx,yy=map(int,p); n=R['N']
  return (220+(xx/n)*630,y+300-(n*yy-(n-1)*xx)*200)
 pts=[display(p) for p in R['main']['points']]
 selected=[display(p) for p in R['hull']['robust' if robust else 'naive']]
 if robust:triangle(d,selected,GREEN)
 else:
  d.line(selected,fill=RED,width=8)
  point(d,pts[0],'A',RED,-50,15);point(d,pts[2],'C',RED,25,-40)
  point(d,pts[1],'B',MUTED,20,5)
  for dx in [-1,1]:d.line((pts[1][0]-20,pts[1][1]-dx*20,pts[1][0]+20,pts[1][1]+dx*20),fill=RED,width=5)
text(d,531,1240,'变换后看形状；不是原比例',38,MUTED,True)
save(im,'07-hull-loses-vertex.png','Actual two-point versus three-point hull under declared area-preserving display transform')
#08
im,d=canvas('08','固定小阈值，遇上缩放就变了',1240)
for y,title,value,result,col in [(170,'原三角形','D = 2^-40 ≈ 9.09×10^-13','小于 0.000000001 → 共线',RED),(700,'坐标统一乘2^20','D = 1','大于 0.000000001 → 左转',GREEN)]:
 text(d,531,y,title,44,col,True)
 tri=[(200,y+220),(850,y+220),(850,y+100)];triangle(d,tri,col)
 text(d,531,y+280,value,40,col,True);text(d,531,y+355,result,38,col,True)
text(d,531,1160,'形状示意；D随长度尺度的平方改变',38,BLUE,True)
save(im,'08-fixed-epsilon-scale.png','Scale dependence of fixed determinant threshold; shapes schematic')
#09
im,d=canvas('09','区间不跨0，才有把握判号',1240)
for y,title,lo,hi,col in [(250,'整个在右侧：确认正',1,4,GREEN),(570,'整个在左侧：确认负',-4,-1,BLUE),(890,'跨过0：还不能决定',-2,3,ORANGE)]:
 text(d,531,y-80,title,44,col,True)
 d.line((100,y+90,960,y+90),fill=MUTED,width=4)
 zero=531;d.line((zero,y+60,zero,y+120),fill=INK,width=5);text(d,zero,y+130,'0',40,center=True)
 x1=zero+lo*90;x2=zero+hi*90;d.line((x1,y+90,x2,y+90),fill=col,width=20)
 for x in [x1,x2]:d.line((x,y+60,x,y+120),fill=col,width=6)
text(d,531,1160,'跨0表示“不确定”，不表示“共线”',38,ORANGE,True)
save(im,'09-certified-intervals.png','Certified determinant intervals and three filter outcomes')
#10
im,d=canvas('10','每一步都往外包住精确结果',1250)
box(d,(70,180,992,440),['区间相减','最小：左下界 − 右上界','最大：左上界 − 右下界'],BLUE,size=40)
box(d,(70,510,992,750),['区间相乘','检查四个端点乘积','取最小值和最大值'],GREEN,size=40)
arrow(d,[(531,765),(531,850)],ORANGE)
text(d,531,890,'下界 ←    结果范围    → 上界',40,ORANGE,True)
text(d,531,980,'朝两侧相邻浮点数各扩一步',40,ORANGE,True)
text(d,531,1100,'溢出或无法包围：进入精确层',38,RED,True)
save(im,'10-outward-arithmetic.png','Outward interval arithmetic operations and explicit fallback')
#11
im,d=canvas('11','主例：先承认不知道，再补算',1240)
for y,ss,col in [(170,['普通估计 D = 0'],BLUE),(440,['区间约为 [−14, 20]','跨0，不能由此判共线'],ORANGE),(800,['精确分数算出 D = 1','返回正号：左转'],GREEN)]:
 box(d,(85,y,977,y+210),ss,col,size=44)
 if y<800:arrow(d,[(531,y+220),(531,y+260)],col)
text(d,531,1110,'精确的是已存输入的数学关系',40,GREEN,True)
save(im,'11-filter-then-exact.png','Actual conservative interval and exact fallback for main example')
#12 grid
im,d=canvas('12','普通答案错了？还是证据不够？',1930)
for y,title,mode,col in [(230,'普通方向判错：31 / 961','wrong',RED),(1060,'需要精确回退：283 / 961','fallback',ORANGE)]:
 text(d,531,y-60,title,44,col,True)
 left,top,cell=230,y+40,19
 for r in R['grid']:
  flag=r['naive_sign']!=r['exact_sign'] if mode=='wrong' else r['route']=='exact'
  x=left+(r['ix']+15)*cell;yy=top+(15-r['iy'])*cell
  d.rectangle((x,yy,x+cell-1,yy+cell-1),fill=col if flag else'#DBE5E3')
 for val in [-15,0,15]:
  text(d,left+(val+15)*cell+9,top+610,str(val),36,center=True)
  text(d,130,top+(15-val)*cell-15,str(val),36)
 text(d,840,top+600,'Δx步',36)
text(d,531,1850,'横纵各31点；每步2^-25；纵轴向上',38,MUTED,True)
save(im,'12-neighborhood-results.png','Actual 31x31 grid: wrong naive signs versus conservative exact fallbacks')
#13
im,d=canvas('13','回退数量取决于这次输入',1160)
for y,title,total,fallback,col in [(210,'普通散点样本',500,0,GREEN),(640,'特制近共线样本',961,283,ORANGE)]:
 text(d,531,y,title,44,col,True)
 d.rounded_rectangle((100,y+100,962,y+180),20,fill='#D3E6E1')
 if fallback:d.rectangle((100,y+100,100+862*fallback/total,y+180),fill=ORANGE)
 text(d,531,y+230,f'精确回退：{fallback} / {total}',44,col,True)
text(d,531,1030,'固定测试集；不是行业性能比例',40,MUTED,True)
save(im,'13-two-test-populations.png','Actual exact-fallback counts for two different test populations')
#14
im,d=canvas('14','输入已合并，精确计算也找不回',1320)
text(d,531,175,'M = 2^53 = 9007199254740992',40,BLUE,True)
box(d,(75,280,987,530),['原始整数','B = (M,M)','C = (M+1,M)：不同点'],BLUE,size=44)
arrow(d,[(531,550),(531,650)],ORANGE)
text(d,660,580,'转为双精度',38,ORANGE)
box(d,(75,720,987,960),['实际存储','B = (M,M)','C = (M,M)：已经重合'],RED,size=44)
text(d,531,1070,'精确谓词对已存数据返回0',42,RED,True)
text(d,531,1160,'它无法猜回丢掉的那个1',40,MUTED,True)
save(im,'14-input-already-lost.png','Input rounding loss distinguished from arithmetic sign correctness')
#cover
im,d=canvas('cover','一个错误的符号，能删掉什么？',1062)
text(d,531,175,'鲁棒几何谓词',60,GREEN,True,True)
triangle(d,[(220,640),(840,640),(840,330)],BLUE)
text(d,531,735,'0？   +？   −？',58,ORANGE,True)
text(d,531,860,'先判断证据够不够',46,GREEN,True)
text(d,531,940,'不确定时，再提高精度',42,GREEN,True)
im.save(O/'cover.png');metadata.append(dict(file='cover.png',width=1062,height=1062,min_font_px=36,min_effective_px_at_354=12,role='Independent original cover',identity='original teaching illustration'))

for item in metadata:
 if item['file'] in ['assets/06-cyclic-inconsistency.png','assets/07-hull-loses-vertex.png','assets/11-filter-then-exact.png','assets/12-neighborhood-results.png','assets/13-two-test-populations.png']:
  item['identity']='original visualization of attached actual experiment outputs'
(O/'examples').mkdir(exist_ok=True);(O/'examples/figure-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
print('Drew 14 body figures and a separate cover')
