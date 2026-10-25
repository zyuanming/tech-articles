"""New OM teaching figures; executed JSON drives messages, matrices and geometry.
CC0-1.0 code; generated figures CC BY 4.0.
"""
from figure_canvas import *
D=DATA;RED='#a13631';GRAY='#627487';PALE='#e5eef7'
def rows(c,y,lines,gap=74):
 for i,s in enumerate(lines):c.text(55,y+i*gap,s,40)
def center(c,x,y,s,size=42,col=INK):c.text(x-measure(c.d,s,size)/2,y,s,size,col)
def color(v):return GREEN if v=='进' else ORANGE

def fan(c,s,y=150):
 c.card(370,y,320,100,'C：恶意' if 'C' in s['faulty'] else 'C：忠诚',color=RED if 'C' in s['faulty'] else INK)
 ev=[e for e in s['events'] if e['round']==1]
 for i,e in enumerate(ev):
  xx=190+i*340;c.arrow((530,y+125),(xx,y+300),color(e['value']))
  center(c,xx,y+325,'缺报' if e['raw'] is None else e['raw'],44,color(e['value']))
  c.card(xx-130,y+430,260,100,e['target']+('：恶意' if e['target'] in s['faulty'] else '：忠诚'),color=RED if e['target'] in s['faulty'] else INK)
 c.geometry.append({'kind':'message-fan','events':ev})

def vector_table(c,s,y=260,only_loyal=True):
 rs=[r for r in s['top'] if not only_loyal or r['target'] not in s['faulty']]
 heads=['谁的表']+rs[0]['columns']+['输出'];xs=[135]+[300+i*170 for i in range(3)]+[930]
 for x,h in zip(xs,heads):center(c,x,y,h,40)
 c.line((55,y+85),(1005,y+85),GRAY)
 for k,r in enumerate(rs):
  yy=y+135+k*160;center(c,xs[0],yy,r['target'])
  for j,v in enumerate(r['vector']):
   xx=xs[j+1];is_self=r['target']==r['columns'][j]
   c.card(xx-65,yy-8,130,90,v,fill='#dcebe5' if is_self else PALE,color=color(v))
  center(c,xs[-1],yy,r['value'],42,color(r['value']))
 c.geometry.append({'kind':'ordered-vectors','rows':rs,'own_cell':'green background'})
 return y+135+len(rs)*160

c=Canvas('拜占庭口信：把分裂的命令对齐')
fan(c,D['bad_c'],140)
c.arrow((530,720),(530,800),GRAY)
for i,r in enumerate(D['bad_c']['top']):
 xx=190+i*340;c.card(xx-130,850,260,100,r['target']+'：'+r['value'],color=color(r['value']))
rows(c,1040,['指挥官可以说谎，忠诚者仍须一致','先交换各自听到的，再按相同规则决定'])
c.save('00-cover.png','一次坏指挥官广播造成分裂，口信算法让忠诚接收者统一结果')

c=Canvas('知道谁在说话，不等于转述有凭据')
c.card(60,170,220,100,'C');c.card(420,170,220,100,'A');c.card(780,170,220,100,'B')
c.arrow((300,220),(390,220));c.arrow((660,220),(750,220),ORANGE)
center(c,345,325,'直接送达',40);center(c,705,405,'A转述',40,ORANGE)
rows(c,520,['B能确认：这条转述由A发来','B不能据此确认：C真的说过这个值','A不能冒充C的直接信道','A却可以改写“我从C听到的内容”'])
c.line((55,865),(1005,865),GRAY)
rows(c,920,['本文模型还要求：','发出的消息正确送达；成员名单固定','有共同轮次，截止时可识别缺报','没有任何可转交验证的数字签名'])
c.save('01-channel.png','把直接发送者识别与不可验证转述放在同一具体路径区分')

c=Canvas('第一轮：坏指挥官分别说不同的话')
fan(c,D['bad_c'])
rows(c,850,['绿色“进”是进攻；棕色“退”是退却','箭头表示一条定向消息，不是投票','这一轮结束，A与B、D知道的并不相同'])
c.save('02-bad-first.png','坏C的全部首轮定向发送与三个不同直收值')

c=Canvas('第二轮：每人转述自己收到的值')
ev=[e for e in D['bad_c']['events'] if e['round']==2]
for i,sender in enumerate(['A','B','D']):
 yy=155+i*300;es=[e for e in ev if e['sender']==sender]
 c.card(55,yy+55,180,95,sender)
 for j,e in enumerate(es):
  y=yy+j*125;c.arrow((280,y+45),(730,y+45),color(e['value']));c.card(790,y,180,95,e['target'])
  center(c,505,y-5,e['value'],42,color(e['value']))
rows(c,1130,[f'共 {len(ev)} 条消息，C不参加这一轮','本例C已占唯一坏节点，其余人如实转述'])
c.geometry.append({'kind':'all-second-round-events','source':'bad_c.events','events':ev})
c.save('03-bad-relays.png','列全六条有方向的二轮消息，避免把双向转述简成一条线')

c=Canvas('按来源排成表：自己那一格也要算')
rows(c,145,['三列固定按 A、B、D 排列'])
y=vector_table(c,D['bad_c'])
rows(c,y+50,['绿底格：自己第一轮直接收到的值','蓝底格：这一列的人第二轮转述的值','三个接收者得到完全相同的有序向量'])
c.save('04-bad-vectors.png','三个接收者的完整有序向量及自身直收项定位')

c=Canvas('多数规则：数的是表格，不是嗓门')
r=D['bad_c']['top'][0]
for i,v in enumerate(['进','退']):
 yy=220+i*250;c.text(60,yy,v,48,color(v))
 for j in range(r['counts'][v]):c.d.ellipse((260+j*200,yy,365+j*200,yy+105),fill=color(v))
 c.text(760,yy,f'{r["counts"][v]} 票',42,color(v));c.bottom=yy+115
rows(c,800,[f'向量共 {len(r["vector"])} 项；退却占严格多数','严格多数：某值的票数 > 总项数÷2','没有严格多数时，统一输出“退”','缺报也先补“退”，不能各人自行猜测'])
c.geometry.append({'kind':'count-dots','counts':r['counts']})
c.save('05-majority.png','实际向量的计数几何及统一默认值的必要位置')

c=Canvas('换一种坏法：C忠诚，D篡改转述')
fan(c,D['good_c'],145)
rows(c,800,['第一轮：三人直接收到同一个“进”'])
for i,e in enumerate(e for e in D['good_c']['events'] if e['sender']=='D'):
 yy=940+i*180;c.card(55,yy,180,95,'D');c.arrow((270,yy+48),(735,yy+48),RED);c.card(790,yy,180,95,e['target']);center(c,505,yy-5,e['value'],42,RED)
rows(c,1350,['第二轮中A、B仍如实向其他副官说“进”','只把D的两条恶意消息放大在上方'])
c.save('06-good-commander.png','好指挥官首轮一致值与坏副官对不同目标的矛盾转述')

c=Canvas('表格可以不同，正确命令仍占多数')
rows(c,145,['只要求忠诚A、B的结果；D可任意行动'])
y=vector_table(c,D['good_c'])
rows(c,y+60,['A的D列是“退”，B的D列是“进”','两表不同，但A、B两列都是可靠的“进”','所以两人都保留忠诚指挥官的命令','这叫有效性；不是证明D已被识破'])
c.save('07-good-vectors.png','好C坏D时向量不必完全相同但多数仍保留原命令')

c=Canvas('缺报：必须等到约定截止点再补值')
c.line((100,270),(940,270),GRAY);c.arrow((100,270),(940,270),GRAY)
for x,label in [(150,'轮次开始'),(820,'截止点')]:c.line((x,250),(x,290),GRAY);center(c,x+20,335,label,40)
c.card(330,150,340,90,'D尚未收到C')
c.line((820,230),(820,310),RED,True);c.line((820,415),(820,520),RED,True)
rows(c,590,['截止前：不能把“还没来”当作缺报','截止后：本模型把缺报记为“退”'])
e=next(e for e in D['missing']['events'] if e['round']==1 and e['target']=='D')
c.card(80,805,350,100,'C→D：缺报',color=ORANGE);c.arrow((465,855),(575,855),GRAY);c.card(620,805,350,100,'D记录：'+e['value'],color=ORANGE)
rows(c,1010,[f'调度槽 {D["missing"]["slots"]} 个，实际发送 {D["missing"]["sent"]} 条','D下一轮向A、B转述补出的“退”','没有已知时限，这个判断依据就消失了'])
c.save('08-missing.png','把未到、确认缺报与默认退却区分并展示计数口径')

c=Canvas('递归路径：深一层，就少一位参与者')
rows(c,145,['OM(2)：允许最多两个坏节点','这里只展开C→A，再展开A→D这一支'])
c.card(410,350,240,90,'C')
c.arrow((530,460),(530,530),GRAY);c.card(410,550,240,90,'A')
children=[x for x in D['higher']['nodes'] if x not in ['C','A']]
for i,s in enumerate(children):
 xx=130+i*200;c.arrow((530,670),(xx,760),GRAY);c.card(xx-65,790,130,90,s)
leaves=[e for e in D['higher']['events'] if e['path']==['C','A','D']]
# selected D branch displayed again below; the dotted connector marks expansion.
c.arrow((330,905),(530,990),ORANGE,True);c.card(405,1020,250,90,'D的展开',color=ORANGE)
for i,e in enumerate(leaves):
 xx=200+i*220;c.arrow((530,1140),(xx,1230),ORANGE);c.card(xx-70,1260,140,90,e['target'])
rows(c,1450,['虚线只放大同一个D，不是一次发送','第三轮的路径如 C→A→D→E','该消息直接sender是D，E不验证C签名','路径不含重复节点；不会再绕回C或A','深度减到OM(0)：直发后结束，不再转述'])
c.geometry.append({'kind':'selected-recursion-tree','children':children,'leaves':leaves})
c.save('09-recursion-tree.png','实际OM2局部递归树、第三轮叶子与不重访节点边界')

def deep_table(c,path,y=280):
 rs=[r for r in D['higher']['reductions'] if r['path']==path and r['target'] not in D['higher']['faulty']]
 xs=[115,300,430,560,690,820,970]
 heads=['接收者']+rs[0]['columns']+['值']
 for x,h in zip(xs,heads):center(c,x,y,h,40)
 c.line((55,y+80),(1010,y+80),GRAY)
 for i,r in enumerate(rs):
  yy=y+125+i*120
  for j,v in enumerate([r['target']]+r['vector']+[r['value']]):center(c,xs[j],yy,v,42,color(v) if v in ['进','退'] else INK)
 c.geometry.append({'kind':'subproblem-reductions','path':path,'rows':rs})
 return y+125+len(rs)*120
c=Canvas('七人算一次：A这一列怎样被校准')
rows(c,140,['C、B恶意；A忠诚且从C收到“进”','子问题只剩 A、B、D、E、F、G'])
y=deep_table(c,['C','A'],350)
rows(c,y+50,['此表在第三轮结束后计算；只列忠诚者','列B可能说谎，另外四列始终是“进”','每行多数为“进”，填回顶层的A列','A自己的顶层A列仍用第一轮直收值'])
c.save('10-honest-subtree.png','从忠诚子指挥官A的五项向量逐行归约到顶层一列')

c=Canvas('B这一列：坏子指挥官也不能分裂结果')
rows(c,140,['C、B恶意；移除C后，只剩B恶意','B向不同人发出不同值，然后众人互告'])
y=deep_table(c,['C','B'],350)
rows(c,y+45,['各忠诚者看到相同的五项向量','“进”占严格多数，统一填进顶层B列','这不代表B真的忠诚，也不证明它原想说进'])
c.save('11-faulty-subtree.png','坏B子问题靠其余忠诚者交换实现一致的归约结果')

c=Canvas('回到顶层：先合每列，再合整行')
s=D['higher'];rs=[r for r in s['top'] if r['target'] not in s['faulty']]
xs=[110]+[270+i*105 for i in range(6)]+[960]
heads=['谁的表']+rs[0]['columns']+['输出']
for x,h in zip(xs,heads):center(c,x,190,h,40)
c.line((55,275),(1005,275),GRAY)
for i,r in enumerate(rs):
 yy=330+i*125
 for j,v in enumerate([r['target']]+r['vector']+[r['value']]):center(c,xs[j],yy,v,42,color(v) if v in ['进','退'] else INK)
rows(c,1080,[f'进 {rs[0]["counts"]["进"]} 项，退 {rs[0]["counts"]["退"]} 项：没有严格多数','全体忠诚者按共同默认值选择“退”','坏C时，保证是结果一致，不是还原真心话'])
c.geometry.append({'kind':'top-level-matrix','source':'higher.top','rows':rs})
c.save('12-top-reduction.png','五位忠诚者的顶层全向量及实际平票默认输出')

c=Canvas('消息数：轮次少，转述树仍然膨胀')
mx=max(r['slots'] for r in D['growth']);scale=680/mx
for i,r in enumerate(D['growth']):
 yy=190+i*250;c.text(55,yy,f'n={r["n"]}，m={r["m"]}',42)
 width=r['slots']*scale;c.d.rectangle((280,yy+85,280+width,yy+150),fill=BLUE)
 c.text(55,yy+90,str(r['slots']),42);c.bottom=yy+160
c.line((280,1140),(960,1140),GRAY)
center(c,280,1170,'0',40);center(c,940,1170,str(mx),40)
rows(c,1300,['同一横轴：单次指挥官广播的消息槽数','短条确实很短；左侧数字给出精确值','不合并消息、不计字节、缺报也算预期槽'])
lengths=[r['slots']*scale for r in D['growth']];assert lengths==sorted(lengths)
c.geometry.append({'kind':'shared-axis-bars','source':'growth.slots','scale':scale,'lengths':lengths})
c.save('13-growth.png','用实际计数共轴展示固定参数递归展开的增长，避免各行独立缩放')

c=Canvas('三个人：同一份所见，可能来自不同真相')
for i,w in enumerate(D['worlds']):
 yy=160+i*570;c.text(55,yy,w['name'],44)
 c.card(440,yy+90,180,90,'C')
 for j,t in enumerate(['A','B']):
  xx=270+j*520;c.arrow((530,yy+205),(xx,yy+285),color(w['direct'][t]));c.card(xx-90,yy+315,180,90,t)
  center(c,xx,yy+145,'C直发：'+w['direct'][t],40)
  center(c,xx,yy+440,('听B转述：' if t=='A' else '听A转述：')+w['relay'][t],40)
rows(c,1910,['看A：世界一、二都是“直进、转退”','看B：世界二、三都是“直退、转进”','世界二的忠诚A、B被逼向相反结果'])
c.geometry.append({'kind':'indistinguishable-world-projections','source':'worlds'})
c.save('14-three-worlds.png','三个世界并置，显露两个忠诚者各自无法区分的局部观察')

c=Canvas('为什么两类坏法，需要两条保证')
c.card(55,170,950,100,'C忠诚：每个忠诚副官保留C的值')
rows(c,350,['好副官形成足够多的可靠列','即使坏列随接收者变化，多数仍是C的值'])
c.line((55,595),(1005,595),GRAY)
c.card(55,665,950,100,'C恶意：剩余坏节点预算少一个')
rows(c,845,['递归让每个来源列在忠诚者之间一致','整行相同，确定的多数/默认规则给出同值','证明需要区分这两类，不能混成一次投票'])
c.save('15-guarantees.png','把一般正确性论证的两种分支和各自理由明确分开')
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('Generated',len(meta),'figures; geometry/glyph/ink/metadata checks passed')
