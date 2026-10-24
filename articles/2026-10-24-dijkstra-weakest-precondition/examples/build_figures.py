from pathlib import Path
import json
from figurelib import *
R=Path(__file__).resolve().parents[1];D=json.loads(Path(__file__).with_name('results.json').read_text());M=[]
def save(b,n,p):M.append(b.save(R/'assets'/n,p,'原创推导或模型输出'))
def chain(title,ls,reverse=False):
 b=Board(title)
 for i,s in enumerate(ls):
  y=140+i*135;b.box((120,y,720,y+75),s,36)
  if i:
   b.arrow((420,y),(420,y-60),ORANGE) if reverse else b.arrow((420,y-60),(420,y))
 return b
save(chain('先说清楚：结束时要满足什么',['起点：x = ?','执行：x先乘2，再加1','目标：结束的x ≥ 11']),'01-target.png','分开输入、程序与末状态要求')
b=Board('沿着一次运行向前看');
for i,r in enumerate(D['samples'][:4]):
 y=145+i*100
 for j,v in enumerate([r['x'],r['doubled'],r['result']]):b.box((40+j*280,y,230+j*280,y+65),str(v),40,outline=TEAL if j==2 and r['accept'] else BLUE)
 b.arrow((230,y+32),(320,y+32));b.arrow((510,y+32),(600,y+32))
b.text(40,570,'列顺序：起点 / 乘2后 / 加1后',34);save(b,'02-forward.png','相邻输入4和5跨越成功门槛')
save(chain('倒推：在加1之前，需要什么？',['加1之前：x ≥ 10','操作：x := x + 1','加1之后：x ≥ 11'],True),'03-back-one.png','从输出条件替换出输入条件')
save(chain('再倒推一层：乘2之前呢？',['最初：x ≥ 5','乘2之后：x ≥ 10','加1之后：x ≥ 11'],True),'04-back-two.png','倒推条件的顺序与执行顺序相反')
b=Board('条件越弱，允许的起点越多');b.d.rectangle((60,140,780,490),outline=BLUE,width=4);b.text(90,165,'x ≥ 5');b.d.rectangle((320,270,740,450),outline=ORANGE,width=4);b.text(380,330,'x ≥ 100',40);b.bottom=490;save(b,'05-weakness.png','集合包含说明弱条件不等于更不可靠')
b=Board('最弱的理由：门内都成功，门外都失败');y=160
for r in D['samples']:
 col=TEAL if r['accept'] else ORANGE;b.circle(95,y+35,35,str(r['x']),fill='#e8f2ed' if r['accept'] else '#fae8de',outline=col);b.arrow((145,y+35),(350,y+35),col);b.box((370,y,750,y+70),f'结束 {r["result"]}',40,outline=col);y+=110
save(b,'06-boundary.png','具体边界例与一般不等式证明相互对照')
b=Board('不是求反函数：平方有两边入口');x0,y0=90,430;W,H=660,270;b.line((x0,140,x0,y0,x0+W,y0),INK,3)
pts=[]
for r in D['square']:
 x=x0+(r['x']+5)/10*W;y=y0-r['value']/25*H;pts.append((x,y));b.circle(x,y,7,fill=TEAL if r['ok'] else ORANGE)
for a,c in zip(pts,pts[1:]):b.line((*a,*c),BLUE,3)
for x in [-5,-3,0,3,5]:b.text(x0+(x+5)/10*W,475,str(x),34,anchor='mm')
b.text(28,y0-9/25*H,'9',32,anchor='lm');b.text(28,160,'25',32,anchor='lm');b.text(100,105,'纵轴：平方后的值',32);b.line((x0,y0-9/25*H,x0+W,y0-9/25*H),ORANGE,3);b.text(90,545,'目标 x² ≥ 9：x ≤ −3 或 x ≥ 3',34);save(b,'07-square.png','后置条件的原像可以是不连续集合')
b=Board('赋值清零，会抹掉输入差异');
for i,x in enumerate([-3,0,7]):b.circle(130,170+i*125,40,str(x));b.arrow((175,170+i*125),(595,295))
b.circle(660,295,55,'0');b.text(60,540,'目标 x=0：所有起点都可以',34);save(b,'08-erase.png','多对一操作仍可倒推条件，无需恢复唯一旧值')
b=Board('有分支时，沿每条真实路径检查');b.box((250,140,590,215),'原x ≥ 0？');
for x,label,action in [(40,'是','y := x'),(460,'否','y := −x')]:
 b.arrow((420,215),(x+170,325));b.box((x,325,x+340,400),label+'：'+action,34);b.arrow((x+170,400),(420,510))
b.box((250,510,590,585),'y ≥ 0');save(b,'09-branch.png','条件分别限制进入各分支的状态')
b=Board('可以任意选时，两种选择都要过关');b.box((260,140,580,215),'允许两种选择');
for x,s in [(40,'x := x + 1'),(460,'x := x − 1')]:b.arrow((420,215),(x+170,315));b.box((x,315,x+340,390),s,34)
b.text(65,470,'要保证结束x ≥ 0，起点需x ≥ 1',34);save(b,'10-all-choices.png','保证全部许可选择成功不同于存在一条成功路')
b=Board('循环：每次少一个，最终走到零');t=D['loops'][5]
for i,x in enumerate(t):
 y=150+i*95;b.box((300,y,540,y+60),str(x),40)
 if i:b.arrow((420,y-35),(420,y))
save(b,'11-loop.png','非负整数严格减少同时给出保持性与终止理由')
b=Board('方向写反：不变式还在，却停不下来');
for i,x in enumerate([1,2,3,4]):
 y=150+i*105;b.box((300,y,540,y+65),str(x),40,outline=ORANGE)
 if i:b.arrow((420,y-40),(420,y),ORANGE)
b.text(90,620,'x始终非负，但x>0一直成立',34);save(b,'12-nontermination.png','部分正确性不能代替必定终止')
Path(__file__).with_name('figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n');print(len(M),'figures verified')
