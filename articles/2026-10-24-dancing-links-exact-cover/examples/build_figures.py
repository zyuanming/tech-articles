"""Original exact-cover visualizations. MIT code / CC BY 4.0 figures."""
from pathlib import Path
import json
from figurekit import Board,BLUE,ORANGE,TEAL,INK,LIGHT
P=Path(__file__).resolve().parent;D=json.loads((P/'results.json').read_text());ROWS=D['rows'];M=[]
def start(t):b=Board();b.text((40,30),t);return b
def save(b,n,p):M.append(b.save(P.parent/'assets'/n,p))
def box(b,x,y,t,fill=LIGHT,w=100):
 q=(x,y,x+w,y+80);b.rect(q,fill=fill);b.text((x+w/2,y+40),t,anchor='mm',inside=q)
def matrix(b,select=None,covered=(),cross=()):
 for j,c in enumerate(D['columns']):box(b,210+j*125,135,str(c),fill='#fff0e5' if c in covered else LIGHT)
 for i,(name,cs) in enumerate(ROWS.items()):
  y=245+i*105;b.text((55,y+15),name)
  conflict=select is not None and name!=select and bool(set(cs)&set(ROWS[select]))
  for j,c in enumerate(D['columns']):
   x=210+j*125;fill='#e6e6e6' if conflict else ('#fff0e5' if name==select else '#ffffff');box(b,x,y,str(int(c in cs)),fill)
   if (name,c) in cross:b.line([(x+5,y+5),(x+95,y+75)],fill=ORANGE,width=6);b.line([(x+5,y+75),(x+95,y+5)],fill=ORANGE,width=6)
b=start('从七种包里，凑齐编号 1—6')
for i,(name,cs) in enumerate(ROWS.items()):
 y=150+i*110;b.text((65,y+15),name)
 for j,c in enumerate(cs):box(b,320+j*180,y,str(c))
save(b,'01-packages.png','每种候选包对应哪两项需求')
b=start('每列的 1，最后恰好选中一个');matrix(b);save(b,'02-matrix.png','完整0/1精确覆盖模型')
b=start('选 G：1、4 已满足，冲突行退出');matrix(b,select='G',covered=[1,4]);save(b,'03-choose-g.png','一次选行如何排除重复覆盖')
b=start('需求 2 还在，却没有候选')
for i,(col,names) in enumerate(D['forced']['G'].items()):
 x=60+i*250;box(b,x,160,col,fill='#fff0e5' if not names else LIGHT,w=150)
 for j,name in enumerate(names):box(b,x,310+j*130,name,w=150)
 if not names:b.rect((x,310,x+150,550),fill='#fff0e5',outline=ORANGE);b.text((x+75,425),'空',anchor='mm')
save(b,'04-empty-column.png','未满足空列提供失败证据')
b=start('选 A，再选 D，最后选 E')
for i,state in enumerate(D['chain']):
 y=170+i*250;b.text((50,y),f'选 {state["chosen"]}')
 for j,col in enumerate(state['visible']):box(b,330+j*150,y,col)
 if not state['visible']:b.text((330,y),'全部满足')
 if i<2:b.arrow((150,y+110),(150,y+210),fill=ORANGE)
save(b,'05-solution.png','一条成功分支的剩余需求逐次缩小')
b=start('摘下 x，只改左右两侧的链接')
for y in [180,520]:
 box(b,60,y,'L');box(b,870,y,'R')
box(b,465,180,'x');box(b,465,790,'x',fill='#eeeeee')
for a,c in [(160,455),(565,860)]:b.arrow((a,210),(c,210));b.arrow((c,245),(a,245))
b.arrow((160,550),(860,550),fill=ORANGE);b.arrow((860,585),(160,585),fill=ORANGE)
b.arrow((465,830),(110,615),fill='#777777');b.arrow((565,830),(920,615),fill='#777777');save(b,'06-unlink.png','节点退出可见链但保留旧邻居')
b=start('恢复 x：用它保留下来的地址')
for x,t in [(60,'L'),(465,'x'),(870,'R')]:box(b,x,220,t)
b.arrow((160,245),(455,245),fill=ORANGE);b.arrow((870,280),(575,280),fill=ORANGE)
b.arrow((465,280),(170,280),fill='#777777');b.arrow((565,245),(860,245),fill='#777777');b.text((60,470),'两侧重新接回原位置');save(b,'07-relink.png','恢复修改两侧指针而非重建节点')
b=start('横着找同包，竖着找同编号');xs={c:210+(c-1)*125 for c in D['columns']};ys={name:250+i*110 for i,name in enumerate(ROWS)}
for c in D['columns']:
 x=xs[c];b.text((x+40,135),str(c),anchor='mt');names=[r for r,cs in ROWS.items() if c in cs];last=200
 for name in names:b.arrow((x+40,last),(x+40,ys[name]-8));last=ys[name]+80
for name,cs in ROWS.items():
 y=ys[name];b.text((55,y+15),name)
 for a,c in zip(cs,cs[1:]):b.arrow((xs[a]+80,y+40),(xs[c]-8,y+40),fill=ORANGE)
 for c in cs:box(b,xs[c],y,'1',w=80)
save(b,'08-sparse.png','14个非零节点组成行列两种链接')
b=start('cover(1)：只摘同行的其他节点');matrix(b,covered=[1],cross=[('A',2),('B',3),('G',4)]);save(b,'09-cover.png','第1列候选保留而其他列的相应节点退出')
b=start('先做的最后撤销，后做的先撤销')
for x,t in [(70,'覆盖'),(640,'恢复')]:b.text((x,150),t)
for i,(left,right) in enumerate([(1,4),(4,1)]):
 y=280+i*220;box(b,80,y,str(left),w=230);box(b,660,y,str(right),w=230)
 if i==0:b.arrow((195,y+110),(195,y+195));b.arrow((775,y+110),(775,y+195),fill=ORANGE)
save(b,'10-reverse-order.png','覆盖列1/4与恢复4/1的相反顺序')
b=start('先选候选最少的需求列')
for i,(col,names) in enumerate(D['initial_visible'].items()):
 y=150+i*120;b.text((40,y),col);length=len(names)*200;b.rect((170,y+10,170+length,y+75),fill=ORANGE if col=='2' else BLUE);b.text((870,y),str(len(names)))
save(b,'11-small-column.png','候选数量启发式及并列时列序规则')
b=start('两组精确答案；搜索后完整恢复')
for i,sol in enumerate(D['solutions']):
 y=160+i*230;b.text((50,y),' + '.join(sol))
 numbers=sorted(c for r in sol for c in ROWS[r])
 for j,c in enumerate(numbers):box(b,50+j*155,y+90,str(c))
b.text((50,710),f'主例：{D["base_subsets"]} 种选法对照')
b.text((50,810),f'随机：{D["random_matrices"]} 张小矩阵对照')
b.text((50,910),f'主例：{D["node_count"]} 节点字段全部还原')
save(b,'12-verification.png','实际解集完整覆盖和恢复检查范围')
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n');print('figures',len(M))
