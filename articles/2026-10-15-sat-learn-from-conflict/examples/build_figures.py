"""Original SAT conflict-learning diagrams from the attached experiment."""
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
def node(d,x,y,ss,col=BLUE,w=250,h=140):box(d,(x-w/2,y-h/2,x+w/2,y+h/2),ss,col,size=42)
def dashed(d,a,b,col=MUTED):
    dx=b[0]-a[0];dy=b[1]-a[1];dist=math.hypot(dx,dy)
    for t in range(0,int(dist),28):d.line((a[0]+dx*t/dist,a[1]+dy*t/dist,a[0]+dx*min(t+15,dist)/dist,a[1]+dy*min(t+15,dist)/dist),fill=col,width=5)
def switch(d,x,y,name,value):
    col=GREEN if value else MUTED
    d.rounded_rectangle((x-110,y-55,x+110,y+55),radius=55,fill=col)
    cx=x+55 if value else x-55;d.ellipse((cx-40,y-40,cx+40,y+40),fill=WHITE)
    text(d,x,y-140,name,50,BLUE,True,True);text(d,x,y+85,'开 / 1' if value else '关 / 0',40,col,True)
#01
im,d=canvas('01','撞墙以后，可以一次跳过一整层',1250)
for y,lab,col in [(240,'第1层：选择 p=1',BLUE),(510,'第2层：选择 z=1',MUTED),(780,'第3层：选择 x=1',ORANGE)]:
    box(d,(110,y,760,y+150),[lab],col,size=44)
arrow(d,[(435,405),(435,490)],MUTED);arrow(d,[(435,675),(435,760)],MUTED)
text(d,435,980,'传播后冲突',48,RED,True)
arrow(d,[(790,850),(970,850),(970,315),(790,315)],GREEN)
text(d,531,1120,'学到原因：p和x不能同时为1',44,GREEN,True)
save(im,'01-conflict-skip-level.png','Actual chosen decision levels and learned backjump skipping unrelated level2')
#02 six switches
im,d=canvas('02','六个开关：每个只回答开或关',1300)
for x,y,name,val in [(220,400,'p',1),(530,400,'x',1),(840,400,'u',1),(220,900,'v',1),(530,900,'z',1),(840,900,'w',0)]:switch(d,x,y,name,val)
text(d,531,1160,'这只是示例组合，接下来还要检查规则',38,RED,True)
save(im,'02-six-boolean-switches.png','Concrete Boolean configuration, explicitly not yet a satisfying assignment')
#03 four clauses
im,d=canvas('03','四条规则，必须同时成立',1480)
for y,cid,formula,meaning,col in [(180,'C1','¬x ∨ u','开x，就必须开u',BLUE),(470,'C2','¬x ∨ v','开x，就必须开v',BLUE),(760,'C3','¬p ∨ ¬u ∨ ¬v','p、u、v不能全开',ORANGE),(1050,'C4','z ∨ w','z、w至少开一个',MUTED)]:
    box(d,(80,y,982,y+235),[cid+'：'+formula,meaning],col,size=44)
text(d,531,1360,'∨：至少一项为真；¬：取反',40,GREEN,True)
save(im,'03-four-clauses.png','Exact four-clause original CNF and plain-language interpretation')
#04 propagation states
im,d=canvas('04','一条子句还剩几个办法能成立？',1440)
for y,formula,meaning,col in [(200,'¬x ∨ u；x=0','¬x为真，已经满足',GREEN),(570,'¬x ∨ u；x=1、u未知','只能令u=1：单位传播',BLUE),(940,'¬x ∨ u；x=1、u=0','两项都为假：冲突',RED)]:
    box(d,(80,y,982,y+250),[formula,meaning],col,size=42)
save(im,'04-clause-states.png','Satisfied, unit and conflicting states of one fixed clause')
#05 actual trail
im,d=canvas('05','决定一次，可能跟出好几个必然结果',1490)
for y,level,contents,col in [(210,1,['主动选 p=1'],BLUE),(490,2,['主动选 z=1'],MUTED),(770,3,['主动选 x=1','C1推出u=1；C2推出v=1'],ORANGE)]:
    text(d,80,y-65,f'第{level}层',42,col);box(d,(80,y,982,y+(220 if level==3 else 150)),contents,col,size=42)
box(d,(80,1130,982,1350),['C3要求p、u、v不能全开','现在三者全是1：冲突'],RED,size=42)
save(im,'05-assignment-trail.png','Actual deterministic decision and implication trail with recorded reasons')
#06 implication graph
im,d=canvas('06','把“为什么被迫这样选”画成图',1450)
node(d,530,300,['x=1 @3'],ORANGE)
node(d,250,620,['u=1 @3'],ORANGE);node(d,810,620,['v=1 @3'],ORANGE)
node(d,250,1010,['p=1 @1'],BLUE);node(d,810,1010,['冲突 C3'],RED)
arrow(d,[(440,385),(280,530)],ORANGE);arrow(d,[(620,385),(780,530)],ORANGE)
text(d,230,410,'C1',40,ORANGE);text(d,820,410,'C2',40,ORANGE)
arrow(d,[(300,710),(710,930)],RED);arrow(d,[(810,710),(810,920)],RED);arrow(d,[(395,1010),(660,1010)],BLUE)
box(d,(80,1200,982,1360),['z=1 @2没有通向这次冲突的边'],MUTED,size=40)
save(im,'06-implication-graph.png','Actual reason graph; level2 z has no causal path to this conflict')
#07 first resolution
im,d=canvas('07','先追问：v=1是从哪里来的？',1420)
box(d,(80,190,982,420),['冲突规则C3','¬p ∨ ¬u ∨ ¬v'],RED,size=48)
box(d,(80,500,982,730),['v的理由C2','¬x ∨ v'],BLUE,size=48)
arrow(d,[(125,755),(125,860)],GREEN)
text(d,600,785,'消去v与¬v',42,GREEN,True)
box(d,(80,900,982,1130),['得到新的必然规则','¬p ∨ ¬u ∨ ¬x'],GREEN,size=48)
text(d,531,1240,'p、u、x若全真，两条原规则会夹出矛盾',36,MUTED,True)
save(im,'07-resolve-v.png','First recorded resolution pivot v replaces implication by its reason')
#08 second resolution
im,d=canvas('08','再追问：u=1又是从哪里来的？',1420)
box(d,(80,190,982,420),['上一步结果','¬p ∨ ¬u ∨ ¬x'],GREEN,size=48)
box(d,(80,500,982,730),['u的理由C1','¬x ∨ u'],BLUE,size=48)
arrow(d,[(125,755),(125,860)],GREEN)
text(d,590,785,'消去u与¬u；重复的¬x只留一次',38,GREEN,True)
box(d,(80,900,982,1130),['学到C5','¬p ∨ ¬x'],GREEN,size=54)
text(d,531,1240,'无论z、w怎样选，p和x不能同时为1',40,MUTED,True)
save(im,'08-resolve-u-learn.png','Second recorded resolution produces the learned clause not-p OR not-x')
#09 resolution reason independent truth
im,d=canvas('09','消去一个变量，为什么不会凭空造规则？',1380)
text(d,531,185,'两条规则：(A ∨ v) 与 (B ∨ ¬v)',44,BLUE,True)
box(d,(80,350,982,570),['假设A和B都为假','第一条逼v为真'],BLUE,size=44)
box(d,(80,650,982,870),['同一个假设下','第二条逼v为假'],ORANGE,size=44)
arrow(d,[(531,895),(531,970)],RED)
box(d,(80,1000,982,1220),['矛盾！所以A与B至少一个为真','得到 A ∨ B'],GREEN,size=44)
save(im,'09-resolution-soundness.png','General resolution entailment argument without relying on exhaustive test counts')
#10 cut and UIP
im,d=canvas('10','当前层的两条路，都经过x',1470)
node(d,250,360,['x=1 @3'],ORANGE);node(d,810,360,['u=1 @3'],ORANGE)
node(d,810,720,['v=1 @3'],ORANGE);node(d,250,1100,['p=1 @1'],BLUE);node(d,810,1100,['冲突'],RED)
arrow(d,[(400,360),(660,360)],ORANGE);arrow(d,[(330,450),(720,630)],ORANGE)
arrow(d,[(950,430),(990,430),(990,1020),(950,1050)],RED);arrow(d,[(810,810),(810,1010)],RED);arrow(d,[(400,1100),(660,1100)],BLUE)
dashed(d,(530,190),(530,1250),GREEN);text(d,531,1300,'切口左边只留下p与x',44,GREEN,True)
save(im,'10-current-level-cut.png','Cut of actual implication graph with x as first UIP and earlier p retained')
#11 backjump
im,d=canvas('11','回到第1层，新规则立刻开始工作',1470)
for y,lab,col in [(210,'保留：p=1 @1',BLUE),(450,'撤回：z=1 @2',MUTED),(690,'撤回：x、u、v @3',MUTED)]:box(d,(80,y,982,y+160),[lab],col,size=46)
arrow(d,[(531,875),(531,960)],GREEN)
box(d,(80,990,982,1240),['C5：¬p ∨ ¬x','p仍为1，因此必须x=0 @1'],GREEN,size=44)
text(d,531,1340,'x=0这次是被推出的，不是又猜一次',38,GREEN,True)
save(im,'11-backjump-and-assert.png','Actual state after backjump and immediate unit assertion at level1')
#12 truth mosaic
im,d=canvas('12','学到规则前后，24个真解一个不少',1450)
import csv
rows=list(csv.DictReader((A/'examples/truth-table.csv').open()))
for i,r in enumerate(rows):
 x=170+(i%8)*90;y=300+(i//8)*90
 col=GREEN if int(r['original']) else RED if not int(r['learned']) else '#9AA9AC'
 d.rectangle((x,y,x+80,y+80),fill=col);text(d,x+40,y+10,f'{i:02}',36,WHITE,True)
for y,lab,col in [(1100,'绿色24格：原来是解，现在仍是解',GREEN),(1190,'红色16格：被新规则排除，原本就不是解',RED),(1280,'灰色24格：仍由其他原规则排除',MUTED)]:
 d.rectangle((80,y+10,115,y+45),fill=col);text(d,145,y,lab,36,col)
text(d,531,180,'64个完整赋值；编号对应附表',40,BLUE,True)
save(im,'12-truth-table-preserved.png','Every one of 64 exhaustive assignments, colored by old solutions and learned rejection')
#13 generalized pruning
im,d=canvas('13','同一条规则，可以挡住两条来路',1460)
node(d,530,280,['p=1'],BLUE)
node(d,240,570,['z=0'],MUTED);node(d,820,570,['z=1'],MUTED)
arrow(d,[(420,360),(260,480)],MUTED);arrow(d,[(640,360),(800,480)],MUTED)
node(d,240,930,['x=1','必冲突'],RED,h=200);node(d,820,930,['x=1','必冲突'],RED,h=200)
arrow(d,[(240,660),(240,810)],RED);arrow(d,[(820,660),(820,810)],RED)
box(d,(80,1150,982,1380),['C5在p=1时就推出x=0','不用等到分别选择z=0或z=1再撞墙'],GREEN,size=40)
save(im,'13-block-both-branches.png','Learned clause applies independently of z, illustrated without runtime speedup claims')
#14 satisfying witness
im,d=canvas('14','冲突一条路，不代表整道题无解',1430)
w=R['witness']
for x,y,n in [(220,400,'p'),(530,400,'x'),(840,400,'u'),(220,850,'v'),(530,850,'z'),(840,850,'w')]:switch(d,x,y,n,w[n])
box(d,(80,1120,982,1320),['C1、C2、C3、C4：全部满足','这是程序实际核验的一份完整解'],GREEN,size=40)
save(im,'14-satisfying-assignment.png','Actual satisfying complete assignment after the conflict lesson')
# cover
im,d=canvas('cover','一次失败，写成一条不会忘的理由',1062)
text(d,531,200,'SAT 冲突学习',62,BLUE,True,True)
node(d,250,470,['p=1'],BLUE);node(d,810,470,['x=1'],ORANGE)
arrow(d,[(300,560),(440,700)],RED);arrow(d,[(760,560),(620,700)],RED)
box(d,(180,730,882,940),['不能同时成立','学到：¬p ∨ ¬x'],GREEN,size=46)
im.save(O/'cover.png');metadata.append(dict(file='cover.png',width=W,height=1062,min_font_px=42,min_effective_px_at_354=14,role='Separate original learned-clause cover',identity='original teaching illustration'))
(O/'examples').mkdir(exist_ok=True);(O/'examples/figure-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
print('Drew 14 body figures and separate cover')
