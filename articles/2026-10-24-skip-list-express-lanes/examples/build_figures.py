"""Independent diagrams. MIT code, CC BY 4.0 rendered figures."""
from pathlib import Path
import json
from figurekit import Board,BLUE,ORANGE,TEAL,INK,LIGHT
P=Path(__file__).resolve().parent;D=json.loads((P/'results.json').read_text());M=[]
def start(t):b=Board();b.text((40,30),t);return b
def save(b,n,p,identity='原创教学示意'):M.append(b.save(P.parent/'assets'/n,p,identity))
def towers(b,nodes,y=180,highlights=(),route=()):
 levels=max(h for k,h in nodes);keys=[None]+[k for k,h in nodes];pos={k:60+i*880/(len(keys)-1) for i,k in enumerate(keys)};ht={None:levels,**dict(nodes)}
 for level in range(levels,0,-1):
  yy=y+(levels-level)*180;b.text((40,yy-65),str(level)+'层')
  active=[k for k in keys if ht[k]>=level]
  for a,c in zip(active,active[1:]):b.arrow((pos[a]+78,yy+40),(pos[c]-4,yy+40))
  b.arrow((pos[active[-1]]+78,yy+40),(1045,yy+40))
  for k in active:
   q=(pos[k],yy,pos[k]+78,yy+80);b.rect(q,fill='#fff0e5' if (k,level) in highlights else LIGHT,outline=ORANGE if (k,level) in highlights else BLUE);b.text((pos[k]+39,yy+40),'头' if k is None else str(k),anchor='mm',inside=q)
 for a,la,c,lc in route:
  ya=y+(levels-la)*180;yc=y+(levels-lc)*180
  if la==lc:b.arrow((pos[a]+78,ya+100),(pos[c],yc+100),fill=ORANGE,width=9)
  else:b.arrow((pos[a]+39,ya+90),(pos[c]+39,yc-8),fill=ORANGE,width=9)
 return pos
b=start('完整底层，上层只留部分节点');towers(b,D['original'],route=[(None,3,9,3),(9,3,34,3)]);save(b,'01-lane.png','高层稀疏捷径与底层完整序列')
b=start('一个节点，保存多层下一站');towers(b,D['original'],highlights=[(9,1),(9,2),(9,3)]);b.text((40,820),'9 的下一站：15 / 21 / 34');save(b,'02-towers.png','同一节点多个前向指针的具体去向')
b=start('找 28：最高层先走到 9');towers(b,D['original'],highlights=[(34,3)],route=[(None,3,9,3),(9,3,9,2)]);b.text((40,820),'34 ≥ 28，所以在 9 下降');save(b,'03-search-high.png','最高层不越过目标的比较与下降')
b=start('找 28：第 2 层到 21，再下降');towers(b,D['original'],highlights=[(28,1)],route=[(9,2,21,2),(21,2,21,1)]);b.text((40,820),'底层下一站 28：相等，找到');save(b,'04-search-low.png','低层路径与最终相等检查')
b=start('插入 25：把各层前驱记下来');towers(b,D['original'],highlights=[(k,i+1) for i,k in enumerate(D['insert_predecessors'])]);b.text((40,820),'第 1 / 2 / 3 层：21 / 21 / 9');save(b,'05-predecessors.png','搜索得到的update前驱数组')
b=start('先接住旧下一站，再改前驱')
for i in range(3):
 y=170+i*290
 for x,k in [(70,21),(480,25),(890,28)]:
  if i==0 and k==25:continue
  q=(x,y,x+100,y+90);b.rect(q,fill=LIGHT);b.text((x+50,y+45),str(k),anchor='mm',inside=q)
 if i==0:b.arrow((170,y+45),(880,y+45),fill='#7b8b96')
 if i==1:b.line([(170,y+45),(220,y+45),(220,y-40),(850,y-40),(850,y+45)],fill='#7b8b96');b.arrow((850,y+45),(880,y+45),fill='#7b8b96')
 if i>=1:b.arrow((580,y+45),(880,y+45),fill=ORANGE)
 if i==2:b.arrow((170,y+45),(470,y+45),fill=ORANGE)
 b.text((40,y+165),['原来：21 → 28','先做：25 → 28','再做：21 → 25'][i])
save(b,'06-splice.png','局部插入两次指针赋值的先后顺序')
b=start('25 高 2 层：只接入这两层');towers(b,D['inserted'],highlights=[(25,1),(25,2)]);save(b,'07-inserted.png','插入后完整结构保持原有上层链接')
b=start('删除 21：前驱绕到 25');towers(b,D['deleted'],highlights=[(15,1),(9,2),(25,1),(25,2)]);save(b,'08-deleted.png','不同层的前驱正确绕过被删节点')
b=start('遇到反面停止，正面再升一层')
for i,(coins,h) in enumerate(D['coin_examples']):
 x=50+i*250;b.text((x,150),coins)
 for j in range(h):
  q=(x,650-j*100,x+150,735-j*100);b.rect(q,fill=LIGHT);b.text((x+75,692-j*100),str(j+1),anchor='mm',inside=q)
 b.text((x,810),f'高 {h}')
save(b,'09-coin.png','独立抽高度的四种可能轨迹')
b=start('128 个节点，各层数量的期望')
for i,v in enumerate(D['expected_layers']):
 y=150+i*110;b.text((40,y),str(i+1));b.rect((160,y+10,160+v/128*650,y+65),fill=BLUE);b.text((870,y),f'{v:g}')
save(b,'10-level-expectation.png','几何衰减的期望数量非实测整齐分层','原创概率模型计算图')
b=start('坏运气：所有节点都只高 1 层');towers(b,[[k,1] for k,h in D['original']]);b.text((50,430),'没有上层，找 42 仍要顺着走');save(b,'11-bad-luck.png','全矮节点给出最坏退化反例')
b=start('平均前向指针数：不是总字节数')
for i,(p,n) in enumerate(D['pointer_expectations']):
 y=180+i*250;b.text((50,y),f'p = {p:g}');b.rect((350,y,350+n*250,y+80),fill=BLUE);b.text((400,y+125),f'{n:.3f}')
save(b,'12-space.png','统一尺度比较不同升层概率的期望指针预算','原创概率模型计算图')
b=start('实际平均检查次数：不测运行时间');maxv=30
for i,r in enumerate(D['costs']):
 x=100+i*240;y=600-r['mean']/maxv*500;b.rect((x,y,x+130,600),fill=BLUE);b.text((x+65,y-55),f'{r["mean"]:.2f}',anchor='mt');b.text((x+65,645),str(r['n']),anchor='mt')
b.line([(60,600),(1020,600)],fill=INK);b.text((45,750),'键数 n：64 / 256 / 1024 / 4096');save(b,'13-costs.png','固定实验四种规模的平均链接检查次数','教学程序实际运行统计')
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n');print('figures',len(M))
