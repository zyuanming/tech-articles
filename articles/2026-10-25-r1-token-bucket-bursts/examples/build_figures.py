"""Original token bucket diagrams. Code CC0; images CC BY 4.0.
All model-driven lengths, points, states and labels are from results.json.
Coordinates, padding, axis scales and font sizes are layout constants.
"""
from figurekit import *
from fractions import Fraction as F
D=DATA;P=D['parameters'];rows=D['policing'];shaped=D['shaping']
def v(s):return float(F(s))
def num(s):
 x=F(s)
 return str(x.numerator) if x.denominator==1 else f'{float(x):g}'
r=v(P['rate']);B=v(P['capacity'])
def txt(c,y,s,color=INK):c.text(50,y,s,42,color)
def bar(c,y,value,label,color=BLUE,maximum=None):
 maximum=B if maximum is None else maximum
 c.text(50,y,label)
 x=350;w=580;length=v(value)/maximum*w
 c.d.rectangle((x,y+10,x+w,y+58),outline='#b6c4d0',width=3)
 if length:c.d.rectangle((x,y+10,x+length,y+58),fill=color)
 c.bottom=max(c.bottom,y+60)
 assert abs(length/w-v(value)/maximum)<1e-10
 if not hasattr(c,'bar_records'):c.bar_records=[]
 for old_value,old_length,old_maximum in c.bar_records:
  if old_maximum==maximum:
   assert (v(value)-old_value)*(length-old_length)>=0
 c.bar_records.append((v(value),length,maximum))
 return length

def axis(c,y,height=360,xmax=6,ymax=6):
 left,right=140,970;top,bottom=y,y+height
 c.line((left,top),(left,bottom),INK);c.line((left,bottom),(right,bottom),INK)
 def xy(x,z):return (left+float(x)/xmax*(right-left),bottom-float(z)/ymax*height)
 return xy,bottom

def curve(c,pts,xy,color=BLUE,width=6):
 pp=[xy(v(a),v(b)) for a,b in pts]
 for a,b in zip(pp,pp[1:]):c.line(a,b,color)
 for x,y in pp:c.d.ellipse((x-6,y-6,x+6,y+6),fill=color)

def ticks(c,xy,xs,ys):
 for x in xs:
  a,b=xy(x,0);c.text(a-16,b+20,num(str(x)),40)
 for y in ys:
  a,b=xy(0,y);c.text(a-75,b-25,num(str(y)),40)

c=Canvas('令牌桶：让闲下来的额度留下来')
txt(c,130,'每秒新增许可，突发花掉积蓄')
for i,e in enumerate(rows[:2]):
 x=70+i*480;y=250
 c.d.rounded_rectangle((x,y,x+420,y+150),radius=20,fill='#e5eef7')
 c.text(x+35,y+40,f"{e['name']}：{num(e['cost'])} 份额度",48)
c.arrow((280,440),(280,560));c.arrow((760,440),(760,560))
txt(c,600,f"同一时刻放行 {num(str(F(rows[0]['cost'])+F(rows[1]['cost'])))} 份",GREEN)
txt(c,690,f"长期补充：{num(P['rate'])} 份 / 秒")
bar(c,800,P['capacity'],'桶上限',GREEN)
c.save('00-cover.png','独立封面：并置短时额度与长期补充速率')

c=Canvas('两条通路：包往前走，额度被扣掉')
txt(c,125,f"计费规则：{P['bytes_per_credit']} 字节 = 1 份额度")
c.card(50,250,400,100,'数据包 A');c.card(640,250,370,100,'允许 / 拒绝')
c.arrow((470,300),(620,300))
c.card(350,480,430,105,'额度账本 q')
c.arrow((550,460),(550,365));c.text(65,430,'判断够不够',42)
c.arrow((550,720),(550,610));txt(c,760,f"时间经过：以 r={num(P['rate'])} 份/秒补充")
txt(c,850,f"容量 B={num(P['capacity'])} 份；包长 L 用同一单位")
txt(c,940,'桶里存的是许可，数据包不装在桶里。')
c.save('01-two-paths.png','分清数据包路径与虚拟额度账本，统一单位')

c=Canvas('同一时刻：补充量为零，逐个扣款')
for i,e in enumerate(rows[:3]):
 y=130+i*250
 txt(c,y,f"{e['name']}：花 {num(e['cost'])}，此前有 {num(e['before'])}")
 bar(c,y+80,e['after'],f"余 {num(e['after'])}",GREEN if e['allowed'] else ORANGE)
 txt(c,y+160,'放行并扣款' if e['allowed'] else '拒绝；额度保持原值',GREEN if e['allowed'] else ORANGE)
c.save('02-same-time.png','A/B/C三步用同轴库存条逐一展示同刻顺序和不补充')

c=Canvas('等了多久，就补多少：先补再判断')
for i,e in enumerate(rows[3:6]):
 y=130+i*250
 txt(c,y,f"{e['name']} 到达 {num(e['time'])} 秒；费用 {num(e['cost'])}")
 txt(c,y+75,f"{num(e['old'])} + {num(P['rate'])} × {num(e['elapsed'])} = {num(e['before'])} 份")
 bar(c,y+150,e['after'],('放行余 ' if e['allowed'] else '拒绝余 ')+num(e['after']),GREEN if e['allowed'] else ORANGE)
c.save('03-refill-steps.png','D/E/F逐步补充与拒绝不扣费，用同一时序算出每个前后值')

c=Canvas('完整监管轨迹：斜线补充，竖线扣款')
txt(c,125,'纵轴：额度 q；横轴：秒')
xy,bottom=axis(c,230,xmax=6,ymax=B)
ticks(c,xy,[0,2,4,6],[0,2,4,6])
pts=[('0',P['initial'])]
for e in rows:pts.extend([(e['time'],e['before']),(e['time'],e['after'])])
curve(c,pts,xy)
txt(c,bottom+110,'放行：'+ ' '.join(e['name'] for e in rows if e['allowed']),GREEN)
txt(c,bottom+190,'拒绝：'+ ' '.join(e['name'] for e in rows if not e['allowed']),ORANGE)
txt(c,bottom+270,'同刻 A、B 的竖降位于同一横坐标。')
c.save('04-token-trace.png','实际模型所有事件的额度折线与接受名单对照')

c=Canvas('空闲可以存额度，但不能无限存')
txt(c,125,'另从空桶开始，整个区间没有数据包')
xy,bottom=axis(c,230,height=400,xmax=6,ymax=12)
ticks(c,xy,[0,3,6],[0,6,12])
curve(c,[(p['time'],p['uncapped']) for p in D['idle']],xy,ORANGE)
curve(c,[(p['time'],p['credit']) for p in D['idle']],xy,GREEN)
txt(c,bottom+110,'橙线：若不截顶的累计新增量',ORANGE)
txt(c,bottom+190,f"绿线：实际库存，{num(str(F(P['capacity'])/F(P['rate'])))} 秒后封顶",GREEN)
txt(c,bottom+270,'横轴：秒；纵轴：份额度')
c.save('05-idle-cap.png','无消费空闲曲线显示达上限后继续等待不会额外积存')

c=Canvas('任意一段时间：钱只能从两处来')
w=D['windows'][2]
txt(c,125,f"窗口长 {num(w['duration'])} 秒，起点最多存 {num(w['burst'])} 份")
maximum=v(w['bound']);a=bar(c,260,w['burst'],'起点 '+num(w['burst'])+' 份',BLUE,maximum)
b=bar(c,370,w['refill'],'新增 '+num(w['refill'])+' 份',GREEN,maximum)
z=bar(c,480,w['bound'],'上限 '+num(w['bound'])+' 份',INK,maximum)
assert abs(a+b-z)<1e-8
c.text(50,640,'放行量 ≤ B + r × 窗口时长',44)
txt(c,740,'拒绝不算放行；满桶溢出的额度不能用。')
c.save('06-window-budget.png','共同长度单位可加的两来源预算；推导任意区间界')

c=Canvas('时间看得越长，初始积蓄越不显眼')
txt(c,125,'区间平均上界 = r + B / 时长')
for i,w in enumerate(D['windows'][1:]):
 y=240+i*140
 bar(c,y,w['mean'],f"{num(w['duration'])} 秒",BLUE,max(v(q['mean']) for q in D['windows'][1:]))
 c.text(760,y+65,num(w['mean'])+' 份/秒',40)
txt(c,850,f"长期趋近 {num(P['rate'])}；短窗口允许高于它。")
c.save('07-long-average.png','不同时间尺度共轴比较平均上界，区分长期与短窗')

c=Canvas('突发多久用完？另看连续流体近似')
pk=D['peak'];txt(c,125,f"满桶 {num(P['capacity'])}，连续流量 {num(pk['rate'])} 份/秒")
txt(c,205,f"补充 {num(P['rate'])}；净消耗 {num(str(F(pk['rate'])-F(P['rate'])))} 份/秒")
xy,bottom=axis(c,310,height=330,xmax=1,ymax=B)
ticks(c,xy,[0,0.5,1],[0,3,6]);curve(c,[(p['time'],p['credit']) for p in pk['curve']],xy)
txt(c,bottom+110,f"耗尽需 {num(pk['duration'])} 秒；共通过 {num(pk['amount'])} 份")
txt(c,bottom+190,'横轴：秒；纵轴：额度；不是逐包轨迹。')
c.save('08-fluid-burst.png','流体近似下B/(p-r)耗尽时间，显式不同于原子扣包')

c=Canvas('同一批包：拒绝，或排队等到够付')
txt(c,125,'每行：圆点为到达，线末为整形放行')
left,right=245,940;xmax=max(v(e['departure']) for e in shaped if e['departure'])
for i,(e,s) in enumerate(zip(rows,shaped)):
 y=250+i*85
 c.text(50,y-28,e['name'],42)
 x=left+v(e['time'])/xmax*(right-left)
 if s['departure'] is not None:
  z=left+v(s['departure'])/xmax*(right-left)
  c.arrow((x,y),(z,y),BLUE) if z>x else None
  c.d.ellipse((z-8,y-8,z+8,y+8),fill=BLUE)
 else:c.text(350,y-28,'超大包移除',40,ORANGE)
 c.d.ellipse((x-8,y-8,x+8,y+8),outline=INK,width=3)
 c.text(105,y-28,'收' if e['allowed'] else '拒',40,GREEN if e['allowed'] else ORANGE)
for t in [0,2,4,7]:c.text(left+t/xmax*(right-left)-15,1030,str(t),40)
txt(c,1120,'横轴：秒；左栏“收/拒”是监管结果')
txt(c,1200,'整形采用 FIFO、无限等候区、零传输时长。')
c.save('09-police-shape.png','同一输入两种动作的实际到达至放行时间线，标超大包')

c=Canvas('F 的等待：先等前包，再等自己的额度')
s=shaped[5];prev=shaped[4]
txt(c,125,f"F 到达 {num(s['arrival'])} 秒，费用 {num(s['cost'])} 份")
txt(c,230,f"E 在 {num(prev['departure'])} 秒放行，F 才轮到队首")
left=100;unit=540/(v(s['departure'])-v(s['arrival']));y=430
cut=left+(v(s['head'])-v(s['arrival']))*unit;end=left+(v(s['departure'])-v(s['arrival']))*unit
c.d.rectangle((left,y,cut,y+65),fill=ORANGE);c.d.rectangle((cut,y,end,y+65),fill=BLUE)
for x,t in [(left,s['arrival']),(cut,s['head']),(end,s['departure'])]:c.text(x-10,y+85,num(t),40)
txt(c,630,'橙段：前方包还没放行',ORANGE)
txt(c,710,'蓝段：轮到自己后继续攒额度',BLUE)
txt(c,810,f"总等待 {num(s['wait'])} 秒；自身补充只需 {num(s['extra'])} 秒")
c.save('10-fifo-wait.png','F实际等候分为队前等待与队首缺额等待，长度从结果计算')

c=Canvas('有两种“现在发不了”，不要混淆')
e=rows[6];bar(c,150,e['before'],'G 可用',GREEN,maximum=v(e['cost']))
bar(c,270,e['cost'],'G 费用',ORANGE,maximum=v(e['cost']))
txt(c,410,f"{num(e['cost'])} > 桶上限 {num(P['capacity'])}：永远攒不够",ORANGE)
txt(c,550,'再看 A：费用没有超过容量')
for i,key in enumerate(['full','empty']):
 e=D['initial_comparison'][key][0]
 bar(c,650+i*130,e['before'],'满初值' if key=='full' else '空初值',GREEN)
txt(c,950,f"空桶的 A 可等 {num(D['initial_comparison']['empty_wait'])} 秒再发")
c.save('11-size-initial.png','费用超过B与初始余额不足的不同后果，初值同轴比较')

c=Canvas('固定整秒清零：边界两侧会挤在一起')
f=D['fixed'];txt(c,125,'另一个例子：每请求花 1；r=2，B=2')
for i,(t,label) in enumerate([('0.99','上一秒末'),('1.01','下一秒初')]):
 x=80+i*500;c.text(x,250,label,42);c.text(x,330,t+' 秒',42)
 for k in range(sum(1 for e in f['input'] if e[1]==t)):c.card(x+k*180,430,150,100,'请求')
c.line((531,225),(531,580),ORANGE)
txt(c,650,f"固定窗放行 {f['window_count']} 个；相距 {num(f['gap'])} 秒")
txt(c,740,f"令牌桶只放行 {f['token_count']} 个",GREEN)
txt(c,830,f"第二批前仅新生 {num(f['token_rows'][2]['before'])} 份额度")
c.save('12-fixed-window.png','固定窗跨边界四请求反例，和明确另设B2的桶比较')

c=Canvas('账算对了，同时读写仍会超卖')
ra=D['race'];txt(c,125,f"同一桶只剩 {num(ra['initial'])}；X、Y 各需 {num(ra['cost'])}")
c.text(100,230,'X',48);c.text(670,230,'Y',48)
for y,word in [(340,'读到 '+num(ra['reads'][0])),(520,'决定放行' if ra['decisions'][0] else '拒绝'),(700,'写回 '+num(ra['writes'][0]))]:
 c.card(60,y,350,100,word);c.card(620,y,350,100,word)
 if y<700:c.arrow((235,y+110),(235,y+165));c.arrow((795,y+110),(795,y+165))
txt(c,890,f"错误地放行 {ra['unsafe_allowed']} 个；合法串行只收 {ra['serial_allowed']} 个")
txt(c,980,'补充、判断、扣款须是同一个原子操作。')
c.save('13-atomicity.png','两个调用读同一余额的具体交错，指出原子边界')

(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(f'Generated {len(meta)} figures; geometry, glyphs, pixels checked')
