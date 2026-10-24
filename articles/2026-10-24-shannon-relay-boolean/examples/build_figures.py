from pathlib import Path
import json
from figurelib import *
R=Path(__file__).resolve().parents[1];D=json.loads(Path(__file__).with_name('results.json').read_text());M=[]
def save(b,n,p):M.append(b.save(R/'assets'/n,p))
def sw(b,x,y,name,on=False,col=BLUE):
 b.line((x-65,y,x-30,y),col,4);b.line((x+35,y,x+65,y),col,4)
 b.circle(x-30,y,5,fill=col,outline=col);b.circle(x+35,y,5,fill=col,outline=col)
 b.line((x-30,y,x+35,y if on else y-35),col,5);b.text(x,y-75,name,36,anchor='mm')
def net(b,y,factored=False,a=True,bb=False,c=True):
 # Two-terminal network only; external lamp/source explicitly shown separately.
 left,right=90,750;top,bot=y,y+160
 if not factored:
  b.line((left,top,left,bot),GRAY,4);b.line((right,top,right,bot),GRAY,4)
  for yy,v,label in [(top,bb,'b'),(bot,c,'c')]:
   b.line((left,yy,255,yy),BLUE,4);sw(b,320,yy,'a',a);b.line((385,yy,515,yy),BLUE,4);sw(b,580,yy,label,v);b.line((645,yy,right,yy),BLUE,4)
 else:
  mid=400;b.line((left,y+80,185,y+80),BLUE,4);sw(b,250,y+80,'a',a);b.line((315,y+80,mid,y+80),BLUE,4)
  b.line((mid,top,mid,bot),BLUE,4);b.line((right,top,right,bot),BLUE,4)
  for yy,v,label in [(top,bb,'b'),(bot,c,'c')]:b.line((mid,yy,515,yy),BLUE,4);sw(b,580,yy,label,v);b.line((645,yy,right,yy),BLUE,4)
 b.circle(left,y+80,7,fill=INK,outline=INK);b.circle(right,y+80,7,fill=INK,outline=INK)
 b.text(left,y+235,'P',36,anchor='mm');b.text(right,y+235,'Q',36,anchor='mm');b.bottom=max(b.bottom,y+260)
b=Board('先看整条回路：有缺口，灯不亮');b.line((150,170,680,170,680,440,150,440,150,310),BLUE,5);b.line((150,170,150,270),BLUE,5)
b.line((110,270,190,270),INK,6);b.line((125,310,175,310),INK,6);b.text(40,350,'电池',34);b.d.rectangle((340,140,470,200),fill='white');sw(b,405,170,'开关',False)
b.circle(680,310,46,fill='#f2f2f2');b.line((650,280,710,340),GRAY,4);b.line((650,340,710,280),GRAY,4);b.text(480,490,'理想模型：开路 / 闭路',32);save(b,'01-loop.png','把开关网络放回电源与负载回路')
for state in [0,1]:
 b=Board('继电器：'+('线圈未通电，触点分开' if not state else '线圈通电，机械推动闭合'))
 b.box((65,170,330,330),None,fill='#fff5e7',outline=ORANGE)
 for x in range(95,305,32):b.d.arc((x,195,x+34,305),-90,90,fill=ORANGE,width=5)
 b.text(195,370,'线圈',36,anchor='mm');b.text(60,460,'控制回路的电流产生磁作用',34)
 b.arrow((350,245),(495,245),ORANGE);b.text(425,320,'机械联动',32,anchor='mm')
 sw(b,665,245,'常开触点',bool(state));b.text(520,390,'被控制回路',34)
 b.text(60,540,'两边没有画成同一根导线',34);save(b,f'0{2+state}-relay-{state}.png','区分控制电流、机械作用与触点导通状态')
b=Board('串联：每一个缺口都得接上');
for i,r in enumerate(D['pairs']):
 y=185+i*145;b.line((80,y,200,y),BLUE,4);sw(b,265,y,'a='+str(r['a']),bool(r['a']));b.line((330,y,430,y),BLUE,4);sw(b,495,y,'b='+str(r['b']),bool(r['b']));b.line((560,y,625,y),BLUE,4);b.box((650,y-40,790,y+35),str(r['AND']),40,outline=TEAL if r['AND'] else ORANGE)
save(b,'04-series.png','四种状态逐个沿导线走，右框为导通值')
b=Board('并联：上路或下路，通一条就行');b.line((150,190,150,390),BLUE,4);b.line((650,190,650,390),BLUE,4)
for yy,n,v in [(190,'a=0',False),(390,'b=1',True)]:b.line((150,yy,335,yy),BLUE,4);sw(b,400,yy,n,v);b.line((465,yy,650,yy),BLUE,4)
b.arrow((150,290),(150,375),TEAL);b.arrow((170,390),(310,390),TEAL);b.text(100,510,'下路闭合：整体导通值为1',36);save(b,'05-parallel.png','分支结构与至少一条完整路径的含义')
b=Board('先按两项许可，画出四个触点');net(b,210);b.text(110,540,'上路：a且b    下路：a且c',34);b.text(110,610,'同名a：两个触点，受同一信号控制',32);save(b,'06-before.png','同一输入重复出现，不等于同一个实体触点')
b=Board('把共同许可移到分岔前');net(b,210,True);b.text(80,540,'先过a，再从b、c两条路中选一条',34);b.text(80,615,f'触点：{D["contacts_before"]}个 → {D["contacts_after"]}个',40);save(b,'07-after.png','分配律在同一电路对象上的几何意义')
b=Board('八种输入，两个网络逐行对账');heads=['a','b','c','旧F','新G']
for j,h in enumerate(heads):b.text(90+j*155,140,h,36,anchor='mm')
for i,r in enumerate(D['rows']):
 y=220+i*76
 for j,k in enumerate(['a','b','c','F','G']):b.text(90+j*155,y,str(r[k]),40,fill=TEAL if j>=3 and r[k] else INK,anchor='mm')
 b.line((45,y+37,790,y+37),'#d8e2ea',2)
save(b,'08-table.png','穷举八态验证两个表达式而非只挑一个成功输入')
b=Board('改错连接方式，就改变了要求');b.text(60,145,'输入：a=1，b=0',40);b.text(60,235,'a且b：必须两个都满足 → 0',36);b.text(60,325,'a或b：至少一个满足   → 1',36);b.box((55,425,785,510),'有这一行不同，就不能说等价',34,fill='#fff1e7',outline=ORANGE);save(b,'09-counterexample.png','一个反例足以否决错误简化')
b=Board('“非”来自相反的稳定触点状态');
for i,a in enumerate([0,1]):
 y=210+i*260;b.text(60,y-75,f'控制a={a}',36);sw(b,335,y,'常开',bool(a));sw(b,635,y,'常闭',not a);b.text(255,y+75,str(a),40);b.text(555,y+75,str(1-a),40)
save(b,'10-complement.png','常开常闭按线圈未激励的正常位置命名')
b=Board('恰好一个满足：两条互斥的路');
for y,names,states in [(210,['a','非b'],[True,True]),(410,['非a','b'],[False,False])]:
 b.line((100,y,255,y),BLUE,4);sw(b,320,y,names[0],states[0]);b.line((385,y,495,y),BLUE,4);sw(b,560,y,names[1],states[1]);b.line((625,y,740,y),BLUE,4)
b.line((100,210,100,410),BLUE,4);b.line((740,210,740,410),BLUE,4);b.text(70,520,'此刻a=1、b=0：只有上路导通',34);b.text(70,595,'两者都为1时，两条路都不通',34);save(b,'11-xor.png','从自然语言恰好一个反向合成接线')
b=Board('稳态恒为1，过渡中仍可能断开');
for j,(key,label) in enumerate([('command','命令a'),('new','常开路'),('old','常闭路'),('output','两路并联')]):
 y=170+j*150;b.text(30,y,label,34);pts=[]
 for i,r in enumerate(D['trace']):
  x=240+i*75;yy=y+65-r[key]*60
  if pts:pts.append((x,pts[-1][1]))
  pts.append((x,yy))
 for p,q in zip(pts,pts[1:]):b.line((*p,*q),ORANGE if key=='output' else BLUE,5)
 b.text(200,y+5,'1',32);b.text(200,y+70,'0',32)
for t in range(8):b.text(240+t*75,805,str(t),32,anchor='mm')
b.text(65,875,'横轴：教学时间单位，并非实测毫秒',32);save(b,'12-delay.png','不同接点切换时刻展示稳态逻辑模型的边界')
Path(__file__).with_name('figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n');print(len(M),'figures verified')
