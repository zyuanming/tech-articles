"""Original illustrations from computed data. Code MIT; images CC BY 4.0."""
from pathlib import Path
import json
from figurekit import Board,BLUE,ORANGE,TEAL,INK,LIGHT
P=Path(__file__).resolve().parent;D=json.loads((P/'results.json').read_text());S=D['samples'];M=[]
COL={'A':'#e5f1fb','B':'#fcebdc','C':'#eeeeee'}
def start(title):b=Board();b.text((40,30),title);return b
def cards(b,s,y,x=50,w=95):
 for i,c in enumerate(s):
  q=(x+i*w,y,x+i*w+80,y+80);b.rect(q,fill=COL.get(c,LIGHT));b.text((q[0]+40,y+40),c,anchor='mm',inside=q)
def save(b,n,p):M.append(b.save(P.parent/'assets'/n,p))
b=start('九张里有六张 A：超过一半');cards(b,S['main']['input'],150);cards(b,'A'*S['main']['counts']['A'],320);b.text((70,450),'A：6     其余：3');save(b,'01-majority.png','真实总量和严格过半条件')
b=start('最多，不等于超过一半');scale=140;threshold=sum(D['mode_counts'].values())/2
for i,(c,n) in enumerate(D['mode_counts'].items()):
 y=150+i*150;b.text((40,y),c);b.rect((150,y,150+n*scale,y+75),fill=BLUE);b.text((830,y),str(n))
b.line([(150+threshold*scale,115),(150+threshold*scale,560)],fill=ORANGE);b.text((670,620),f'门槛 {threshold:g}');save(b,'02-mode.png','同一票数尺度下众数未过半的反例')
b=start('删除异名对，不消灭严格多数')
for k,(left,right) in enumerate([('AAA','BC'),('AAA','BC')]):
 y=170+k*330;cards(b,left,y,x=40);cards(b,right,y,x=530)
 for x in ([40,530] if k==0 else [530,625]):b.line([(x,y),(x+80,y+80)],fill=ORANGE,width=7);b.line([(x+80,y),(x,y+80)],fill=ORANGE,width=7)
 b.text((50,y+145),'删 A 与非 A' if k==0 else '删两个不同的非 A')
save(b,'03-pair-proof.png','两类合法抵消的具体票堆')
b=start('余堆只存：名字 + 数量');cards(b,'AAA',150);b.text((500,175),'A，3');b.arrow((350,190),(460,190));cards(b,'B',350,x=400);b.arrow((440,455),(230,520),fill=ORANGE);cards(b,'AA',560);b.text((500,580),'A，2');save(b,'04-state.png','相同名字的余堆如何缩成常数状态')
for name,tr,title in [('05-trace-start.png',S['main']['trace'][:4],'前四步：归零后再开新堆'),('06-trace-end.png',S['main']['trace'][4:],'后五步：计数记录未配对数')]:
 b=start(title)
 for k,t in enumerate(tr):
  y=150+k*150;b.text((45,y+15),str(t['i']));cards(b,t['input'],y,x=160);b.arrow((300,y+40),(440,y+40));cards(b,(t['candidate'] or '')*t['count'],y,x=490)
  if not t['count']:b.rect((490,y,570,y+80),fill='#eeeeee');b.text((530,y+40),'—',anchor='mm')
  b.text((900,y+15),str(t['count']))
 save(b,name,'逐步输入、余堆、计数的实际轨迹')
b=start('原来六张 A，余堆只剩三张')
for i,pair in enumerate(S['main']['pairs']):
 y=150+i*140;b.rect((40,y-10,270,y+95),fill='#f2f2f2',outline='#777777');cards(b,pair,y,x=60)
cards(b,S['main']['stack'],290,x=560);b.text((60,650),'已配对');b.text((570,650),'未配对');save(b,'07-count-not-frequency.png','频数由已配对与未配对两部分组成')
b=start('没有多数，也会留下一名候选');cards(b,S['counter']['input'],150)
for k,t in enumerate(S['counter']['trace']):
 y=320+k*105;b.text((70,y),f'第{t["i"]}步');b.text((400,y),t['candidate'] or '—');b.text((720,y),str(t['count']))
save(b,'08-counterexample.png','只有一票的C也能成为最终候选')
b=start('第一遍筛选，第二遍数原始票')
for k,key in enumerate(['main','counter']):
 q=S[key];y=170+k*320;b.text((50,y),q['input']);b.text((50,y+100),f'候选 {q["candidate"]}');b.arrow((350,y+135),(500,y+135));b.text((560,y+100),f'实数 {q["actual"]} 次');b.text((550,y+210),'过半' if q['answer'] else '不过半')
save(b,'09-two-passes.png','候选与真实频数验证分开')
b=start('全配完：任何名字至多占一半')
for i,pair in enumerate(['AB','AC','BC']):
 y=160+i*160;b.rect((180,y-10,460,y+100),fill='#f2f2f2',outline='#777777');cards(b,pair,y,x=220)
b.text((580,300),'每对最多');b.text((580,390),'一张 A');save(b,'10-zero.png','异名对的结构证明零余量无严格多数')
b=start('频数相同，候选可以不同')
for i,key in enumerate(['counter','reorder']):
 q=S[key];y=150+i*270;cards(b,q['input'],y);b.text((60,y+130),f'候选 {q["candidate"]}，实际 {q["actual"]} 次')
save(b,'11-order.png','无多数时顺序影响候选却不影响验证结论')
b=start('穷举全部输入，逐一比对精确计数');maximum=max(n for _,n in D['tests']);lens=[]
for n,c in D['tests']:
 y=140+n*105;b.text((35,y),str(n));length=660*c/maximum;b.rect((145,y+10,145+length,y+65),fill=BLUE);b.text((850,y),str(c));lens.append((length,c))
assert sorted(lens)==lens
save(b,'12-verification.png','长度0至9的实际穷举数量')
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n');print('figures',len(M))
