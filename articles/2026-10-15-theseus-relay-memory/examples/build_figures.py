"""Original teaching diagrams. MIT code; rendered originals CC BY 4.0, zyuanming."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json, math
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets';OUT.mkdir(exist_ok=True)
R=json.loads((ROOT/'examples/results.json').read_text());W=1062
BG='#f7f4eb';INK='#193644';MUTED='#50636a';TEAL='#007d83';ORANGE='#b94e22';BLUE='#305fc3';GRAY='#c3cccb';WHITE='#ffffff'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
font=lambda size,b=False:ImageFont.truetype(BOLD if b else FONT,size,index=2)
META=[]
def canvas(title,h=1000,sub=None):
 global im,d,labels
 im=Image.new('RGB',(W,h),BG);d=ImageDraw.Draw(im);labels=[]
 text((54,42),title,48,b=True)
 if sub:text((54,114),sub,38,color=MUTED)
 return im

def text(xy,s,size=40,color=INK,b=False,anchor=None):
 assert size>=38
 box=d.textbbox(xy,str(s),font=font(size,b),anchor=anchor)
 assert min(box[:2])>=0 and box[2]<=W and box[3]<=im.height,(s,box,im.size)
 d.text(xy,str(s),font=font(size,b),fill=color,anchor=anchor);labels.append({'text':str(s),'size':size,'bbox':box})
def lines(x,y,ss,size=40,gap=60,color=INK):
 for i,s in enumerate(ss):text((x,y+i*gap),s,size,color)
def box(x,y,w,h,fill=WHITE,outline=GRAY):d.rounded_rectangle((x,y,x+w,y+h),radius=18,fill=fill,outline=outline,width=3)
def arrow(a,b,color=TEAL,width=8):
 d.line((a,b),fill=color,width=width)
 dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy)
 if not L:return
 ux,uy=dx/L,dy/L
 p=(b[0]-20*ux,b[1]-20*uy)
 d.polygon([b,(p[0]+10*uy,p[1]-10*ux),(p[0]-10*uy,p[1]+10*ux)],fill=color)
def save(name,cover=False):
 p=ROOT/'cover.png' if cover else OUT/name
 im.save(p);META.append({'file':str(p.relative_to(ROOT)),'size':im.size,'minimum_label_px':min(x['size'] for x in labels),'labels':labels})
def maze(x,y,cell=240,edges=None,memory=None,path=None,color=TEAL,unvisited=None,goal='C'):
 edges=R['edges'] if edges is None else edges
 d.rectangle((x,y,x+3*cell,y+3*cell),fill=WHITE,outline=INK,width=7)
 pos={a:(x+(c+.5)*cell,y+(r+.5)*cell) for a,(r,c) in R['grid'].items()}
 for a,(r,c) in R['grid'].items():
  px,py=x+c*cell,y+r*cell
  if unvisited and a in unvisited:d.rectangle((px+6,py+6,px+cell-6,py+cell-6),fill='#e3e8e6')
  if a==goal:d.rectangle((px+8,py+8,px+cell-8,py+cell-8),fill='#d5eee3')
  for dr,dc in ((0,1),(1,0)):
   q=(r+dr,c+dc);b=next((k for k,v in R['grid'].items() if tuple(v)==q),None)
   if b:
    if dc:a1=(px+cell,py);a2=(px+cell,py+cell)
    else:a1=(px,py+cell);a2=(px+cell,py+cell)
    if ''.join(sorted((a,b))) not in edges:d.line((a1,a2),fill=INK,width=9)
    else:
     # Dashed boundary marks the cell coordinates; a gap is traversable.
     vx,vy=a2[0]-a1[0],a2[1]-a1[1]
     for k in (0,.85):d.line((a1[0]+vx*k,a1[1]+vy*k,a1[0]+vx*(k+.15),a1[1]+vy*(k+.15)),fill=GRAY,width=3)
  text((px+18,py+12),a,42,b=True)
  if memory and a!=goal and (not unvisited or a not in unvisited):
   dd=memory[a];dr,dc=((-1,0),(0,1),(1,0),(0,-1))[dd];cx,cy=pos[a]
   arrow((cx-dc*34,cy-dr*34),(cx+dc*45,cy+dr*45))
 if path:
  for a,b in zip(path,path[1:]):
   ax,ay=pos[a];bx,by=pos[b];dx,dy=bx-ax,by-ay;L=math.hypot(dx,dy)
   arrow((ax+dx/L*23,ay+dy/L*23),(bx-dx/L*25,by-dy/L*25),color,10)
  for a in set(path):
   cx,cy=pos[a];d.ellipse((cx-13,cy-13,cx+13,cy+13),fill=color)
 return pos

canvas('老鼠的“记性”，放在哪里？',1040,'依据 1951 年报告的功能关系示意')
# Functional, deliberately not a faux physical replica.
box(60,195,440,480);text((95,222),'可改隔板的 5×5 迷宫',38,b=True)
for r in range(5):
 for c in range(5):d.rectangle((100+c*70,300+r*62,170+c*70,362+r*62),outline=GRAY,width=2)
d.ellipse((237,425,263,451),fill=ORANGE);text((99,617),'触头碰到隔板',38)
box(590,195,412,180);lines(624,224,['两个方向的电机','东西 / 南北'],38)
box(590,445,412,210);lines(624,477,['继电器控制电路','位置、策略、记忆'],38)
arrow((735,432),(735,385));arrow((510,570),(578,570));arrow((578,325),(510,325))
box(60,730,942,220);lines(94,763,['25 格 × 每格 2 个继电器','另有控制、计数等电路；不能只数这 50 个。','示意不代表原机尺寸、布线或具体外观。'],38)
save('01-machine.png')

canvas('一个开关，怎样影响下次动作？',960,'继电器：线圈通电，可改变触点的连接')
for i,on in enumerate((False,True)):
 y=210+i*300;box(70,y,922,245);text((100,y+24),'线圈断电' if not on else '线圈通电',40,b=True)
 d.rectangle((125,y+100,335,y+175),outline=INK,width=4)
 for k in range(7):d.arc((135+k*25,y+100,180+k*25,y+175),90,270,fill=ORANGE,width=5)
 arrow((375,y+138),(505,y+138),GRAY)
 d.line((560,y+150,640,y+150),fill=INK,width=5);d.line((800,y+150,900,y+150),fill=INK,width=5)
 d.ellipse((630,y+140,650,y+160),fill=INK);d.ellipse((790,y+140,810,y+160),fill=INK)
 d.line((640,y+150,800,y+150 if on else y+85),fill=TEAL,width=9)
 text((575,y+185),'触点闭合' if on else '触点断开',38)
lines(90,850,['状态要靠电路保持；断电后未必还能记住。'],38)
save('02-relay.png')

canvas('两个二态量，能表示四个方向',900,'下面只是教学编码，不是原机接线表')
for i,(bits,word,dd) in enumerate((('00','北 N',0),('01','东 E',1),('10','南 S',2),('11','西 W',3))):
 x=70+(i%2)*480;y=210+(i//2)*290;box(x,y,442,250)
 text((x+35,y+30),bits,64,b=True);text((x+190,y+42),word,42)
 dr,dc=((-1,0),(0,1),(1,0),(0,-1))[dd]
 arrow((x+235-dc*42,y+168-dr*42),(x+235+dc*42,y+168+dr*42))
text((82,825),'记的是一个方向，不是四面墙的完整地图。',38)
save('03-two-relays.png')

canvas('把手指放在 A，目标在 C',1120,'3×3 自构教学迷宫；粗黑线是墙')
maze(171,220,240)
lines(110,990,['初始箭头全部设为西；这是我们的实验输入。'],38)
save('04-maze.png')

canvas('探索：先转 90°，再试一步',1130,'逆时针：东 → 北 → 西 → 南 → 东')
rows=[('A：旧记忆 西','转成南，走到 D'),('D：旧记忆 西','转成南，走到 G'),('G：旧记忆 西','南碰墙；东也碰墙'),('G：刚写入 东','再转到北，返回 D'),('D：上次写入 南','这次转到东，走向 E')]
for i,(a,b) in enumerate(rows):
 y=210+i*155;box(65,y,930,135);text((95,y+16),a,40,b=True);text((95,y+72),b,38)
text((80,1020),'每次尝试都更新本格箭头；碰墙不跨格。',38)
save('05-exploration.png')

canvas('第一次走：8 次跨格，6 次碰墙',1200,'下方是程序实际记录的逐步轨迹')
# Legible event timeline, not overlapping paths.
seq=R['first']['path']
for i,a in enumerate(seq):
 x=130+(i%3)*340;y=260+(i//3)*255
 d.ellipse((x-70,y-70,x+70,y+70),fill=WHITE,outline=TEAL,width=6);text((x,y-8),a,54,b=True,anchor='mm');text((x-70,y+85),f'位置 {i}',38)
 if i<8:
  if i%3<2:arrow((x+85,y),(x+245,y))
  # Row wrapping is specified by the numbered positions below, not a false vertical edge.
lines(90,1070,['按“位置 0→8”阅读；换行后从左侧继续。','D 出现两次，最后一次改写会留下来。'],38)
save('06-first-trace.png')

canvas('到达 C 后，留下了这张箭头图',1140,'绿色目标不用再出发；灰色 B 尚未访问')
maze(171,220,240,memory=R['first']['memory'],unvisited={'B'})
lines(100,990,['每格只保留最后一次离开时的方向。','B 仍是初始西向，不能当成已学会的出口。'],38)
save('07-memory.png')

canvas('岔路如何被“最后一次”擦掉？',1120,'只放大 D 这一格的记忆变化')
for y,left,right,caption in [(220,'D → G','D 记住南','进入死胡同'),(500,'G → D','D 仍记南','返回不等于改写 D'),(780,'D → E','D 改记东','再次出发，覆盖旧方向')]:
 box(65,y,930,235);text((100,y+30),left,46,b=True);text((490,y+30),right,42,color=TEAL);text((100,y+135),caption,40)
save('08-overwrite.png')

canvas('第二次：照着箭头走',1150,'A → D → E → H → I → F → C')
maze(171,220,240,path=R['second']['path'])
lines(100,990,['6 次跨格，0 次碰墙。','D→G→D 这段往返消失了。'],40)
save('09-replay.png')

canvas('为什么最后出口不会绕成圈？',1160,'给第一次走过的每次离开，标上序号')
items=[('A',0),('D',3),('E',4),('H',5),('I',6),('F',7)]
for i,(a,t) in enumerate(items):
 x=95+(i%2)*495;y=220+(i//2)*210;box(x,y,400,170);text((x+25,y+25),a,52,b=True);text((x+125,y+35),f'最后 {t}',40)
 if i%2==0:arrow((x+410,y+85),(x+475,y+85))
box(95,900,890,180,fill='#d5eee3');lines(130,927,['沿最终箭头前进，最后离开序号严格变大。','有限个格子里，不能一直变大又回到原处。'],38)
save('10-proof.png')

canvas('记住一条路，不等于找到最短路',1970,'同一个迷宫，两条都合法')
text((150,195),'记住的路：6 次跨格',42,b=True);maze(171,275,240,path=R['second']['path'])
text((150,1060),'更短的路：2 次跨格',42,b=True);maze(171,1140,240,path=R['shortest_path'],color=ORANGE)
text((110,1900),'A→B→C 根本没有进入第一次的经历。',38)
save('11-not-shortest.png')

canvas('把它放在没到过的 B，会怎样？',1150,'这个输入恰好先去 A，再接上已知路线')
maze(171,220,240,path=R['unfamiliar']['path'],color=BLUE)
lines(90,990,['B → A → D → E → H → I → F → C','7 次跨格；这次恰好没有碰墙。'],38)
save('12-unfamiliar.png')

canvas('只堵住 F—C，旧答案就会绕圈',1200,'其他通道不变；仍能从 A→B→C 到目标')
ps=maze(171,220,240,edges=R['changed_edges'],path=['E','H','I','F','E'],color=ORANGE)
d.line((651,460,891,460),fill=ORANGE,width=14)
lines(85,990,['F 的旧箭头撞墙后转向西，进入 E。','E → H → I → F → E，旧路反而困住它。'],38)
save('13-changed-wall.png')

canvas('到第 8 次跨格：切换回探索',1180,'本文 9 格模型的计数；原报告 25 格用 24')
# Actual cumulative path, axis labels fit 354px.
x0=160;y0=250;dx=54;dy=70
for i,a in enumerate('ABCDEFGHI'):
 y=y0+i*dy;d.line((x0,y,940,y),fill=GRAY,width=2);text((90,y-28),a,38)
for n in (0,2,4,6,8,10,12,14):text((x0+n*dx,y0+8*dy+40),str(n),38,anchor='mt')
path=R['recovered']['path']
for i in range(len(path)-1):
 a=(x0+i*dx,y0+(ord(path[i])-65)*dy);b=(x0+(i+1)*dx,y0+(ord(path[i+1])-65)*dy)
 d.line((a,b),fill=BLUE if i<8 else TEAL,width=7)
for i,p in enumerate(path):
 x=x0+i*dx;y=y0+(ord(p)-65)*dy;d.ellipse((x-9,y-9,x+9,y+9),fill=BLUE if i<=8 else TEAL)
x=x0+8*dx;d.line((x,200,x,850),fill=ORANGE,width=4);text((x-85,170),'切换策略',38,color=ORANGE)
lines(100,960,['横轴：累计跨格次数；纵轴：所在格。','蓝线先用旧记忆；绿线探索，最终到 C。','碰墙未跨格，不推进这个实验的横轴。'],38)
save('14-switch-trace.png')

canvas('同一份事件日志，汇总出这些数',1260,'长度单位都是次数；不是原机速度测试')
keys=['first','second','unfamiliar','stale','recovered'];names=['初次探索','原地重跑','从 B 开始','改墙不切换','改墙后切换']
for i,(k,n) in enumerate(zip(keys,names)):
 y=235+i*185;v=R[k];text((75,y),n,40,b=True)
 d.rectangle((390,y,390+v['moves']*20,y+42),fill=TEAL);text((410+v['moves']*20,y-5),str(v['moves']),38)
 if v['walls']:d.rectangle((390,y+70,390+v['walls']*20,y+110),fill=ORANGE)
 text((410+v['walls']*20,y+62),str(v['walls']),38)
text((75,1180),'青色：跨格；橙色：碰墙；24 次那项未到目标。',38)
save('15-results.png')

canvas('一只没有电脑芯片的老鼠',900,'怎样记住迷宫？')
# Independent cover with relay states and a stylized, explicitly graphic mouse.
for r in range(3):
 for c in range(3):
  x=70+c*195;y=250+r*165;box(x,y,170,140,fill=WHITE);arrow((x+42,y+72),(x+125,y+72),TEAL)
box(720,250,270,250);text((770,275),'0    1',48,b=True);text((765,365),'一格记忆',40)
d.ellipse((730,620,930,730),fill=INK);d.ellipse((830,580,880,635),fill=INK);d.ellipse((865,630,878,643),fill=BG);d.arc((900,660,1000,790),-80,110,fill=INK,width=8)
text((715,790),'Theseus',44,b=True);save('cover.png',True)
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(META,ensure_ascii=False,indent=2)+'\n')
print('rendered',len(META),'original figures including cover')
