"""Supplementary original teaching diagrams. Code CC0; images CC BY 4.0."""
from visual_figurekit import *

def row_nodes(c, labels, y, colors=None):
    step=190; x0=55
    for i,s in enumerate(labels):
        x=x0+i*step
        if i:c.arrow((x-step+150,y+45),(x-10,y+45))
        c.card(x,y,150,90,s,fill=(colors or {}).get(s,'#e5eef7'))

c=Canvas('逐词插入：沿旧路走，只补缺少的边')
c.text(50,120,'绿色：本次复用；蓝色：本次新建',40)
for i,r in enumerate(DATA['insertions']):
    y=225+i*300
    c.text(50,y,'插入 '+r['pattern']+'：',44)
    row_nodes(c,['根']+r['path'],y+80,{s:'#dceee6' for s in ['根']+r['shared']})
    c.text(55,y+185,('复用 '+', '.join(r['shared'])+'；' if r['shared'] else '还没有可复用的非根节点；')+'末端登记 '+r['pattern'],40)
c.text(50,1450,'各行仅展开本次路径；其余旧分支保留',40)
c.save('06-insert.png','按四个词的插入顺序区分复用前缀与新增路径')

c=Canvas('广度优先：先浅后深，队首先处理')
c.text(50,130,'层号是路径长度；同层从左向右出队',40)
for i,layer in enumerate(DATA['layers']):
    y=225+i*115
    c.text(50,y,f'深度 {i}',40)
    c.card(260,y-12,740,90,'   '.join(layer))
c.text(50,850,'队列局部：左边取出，右边加入',44)
for j,index in enumerate([0,1,2,3,4]):
    r=DATA['bfs'][index];y=945+j*160
    c.text(50,y,'取出 '+r['pop']+' 后：',40)
    c.text(50,y+65,' | '.join(r['after']) or '空',42,BLUE)
c.text(50,1800,'算 she 前，sh 的退路 h 已经算好',40)
c.save('07-bfs.png','把深度层级与实际FIFO队列连接，说明构建的依赖顺序')

c=Canvas('构建一步：为 she 找失败目标')
r=DATA['build_step']
c.text(50,135,'已知父节点 sh 的失败目标是 h',42)
c.card(90,260,240,90,r['parent']);c.card(730,260,240,90,r['child'])
c.arrow((350,305),(710,305));c.text(480,355,'读 '+r['char'],42,BLUE)
c.arrow((210,370),(210,585),ORANGE,True);c.text(280,475,'已知失败',40,ORANGE)
c.card(90,610,240,90,r['parent_fail']);c.card(730,610,240,90,r['child_fail'])
c.arrow((350,655),(710,655));c.text(450,710,'也读 '+r['char'],42,BLUE)
c.arrow((850,370),(850,585),ORANGE,True);c.text(550,475,'新建失败',40,ORANGE)
c.text(50,850,'从 h 试 e，确实到 he；于是记下',42)
c.text(50,930,'she → he，不会指回 she 自己',42)
c.text(50,1030,'蓝实线：树边；橙虚线：失败指针',40)
c.save('08-build-failure.png','从父节点的已知失败边推导子节点的失败边')

c=Canvas('两种链接，两种动作')
c.text(50,130,'失败：下一字符 r 接不上，主状态改变',40)
c.card(55,245,150,90,'she');c.card(405,245,150,90,'he');c.card(755,245,150,90,'her')
c.arrow((225,290),(385,290),ORANGE,True);c.arrow((575,290),(735,290),BLUE)
c.text(50,365,'she → he 不读字符；he → her 才读 r',40)
c.text(50,505,'输出：读完 e 后，主状态仍停在 she',40)
c.card(60,610,360,90,'主状态 she',fill='#dceee6')
c.text(55,755,'只移动输出游标：',42)
for i,r in enumerate(DATA['output_chain']):
    x=70+i*560;c.card(x,855,250,90,r['state'])
    c.text(x,990,'报告 '+', '.join(r['outputs']),42,GREEN)
c.arrow((350,900),(600,900),GREEN);c.text(370,945,'输出链接',40,GREEN)
c.text(50,1120,'he 之后无输出链接，停止枚举',42)
c.text(50,1200,'这次枚举结束，主状态还是 she',42)
c.text(50,1300,'绿色实线只供报告；不用它驱动扫描',40)
c.save('09-output-link.png','分开失败转移与输出枚举，突出输出游标不修改主状态')

c=Canvas('三次回退：手里的字符始终是同一个')
for j,r in enumerate([r for r in DATA['trace'] if r['fallback']]):
    y=150+j*390
    c.text(50,y,f"位置 {r['i']}，待处理字符 {r['ch']}",44)
    labels=[r['before']]+r['fallback']+[r['state']]
    for k,s in enumerate(labels):
        x=65+k*350;c.card(x,y+100,220,90,s)
        if k:
            c.arrow((x-120,y+145),(x-15,y+145),ORANGE if k<len(labels)-1 else BLUE,k<len(labels)-1)
    c.text(50,y+225,'橙虚线：不消费；蓝实线：消费 '+r['ch'],40)
    c.text(50,y+295,f"输入位置到此才从 {r['i']} 增到 {r['i']+1}",40)
c.text(50,1370,'回退只换记忆；不回读、不丢掉手中字符',40)
c.save('10-fallback-steps.png','展开原轨迹的全部三次失败回退，标清同字符只消费一次')

c=Canvas('深度账本：先上升，才有余量下降')
c.text(50,130,'输入仍是 ushershis；深度 = 路径长度',40)
x0=110;dx=65;y0=690;dy=100
for d in range(5):
    y=y0-d*dy;c.line((100,y),(970,y),'#cbd5e1');c.text(40,y-27,str(d),40)
for i,(a,b) in enumerate(zip(DATA['events'],DATA['events'][1:])):
    c.arrow((x0+i*dx,y0-a['depth']*dy),(x0+(i+1)*dx,y0-b['depth']*dy),ORANGE if b['kind']=='fail' else BLUE,b['kind']=='fail')
for i,e in enumerate(DATA['events']):
    x=x0+i*dx;y=y0-e['depth']*dy;c.d.ellipse((x-7,y-7,x+7,y+7),fill=INK)
    c.text(x-12,750,'' if e['kind']=='start' else ('退' if e['kind']=='fail' else e['label']),40,ORANGE if e['kind']=='fail' else BLUE) if i else None
c.text(50,860,'横向依次是动作；橙色下降不读字符',40)
c.text(50,955,f"上升共 {DATA['rises']} 层；下降共 {DATA['drops']} 层；末深度 {DATA['events'][-1]['depth']}",42)
c.text(50,1040,f"失败跳转 {DATA['fail_count']} 次 ≤ 下降 {DATA['drops']} 层 ≤ 上升 {DATA['rises']} 层",40)
c.text(50,1140,'每读一个字符至多上升一层；',42)
c.text(50,1210,'每次失败至少下降一层，深度不为负。',42)
c.save('11-depth.png','用同一执行轨迹画消费上升与失败下降，连接摊还计数')

c=Canvas('换个输入：四个字符也能有九个输出')
dense=DATA['dense'];c.text(50,130,'词表：'+', '.join(dense['patterns'])+'；文本：'+dense['text'],42)
x0=300;step=150
for i,ch in enumerate(dense['text']):
    c.card(x0+i*step,245,145,90,ch)
for i in range(len(dense['text'])+1):c.text(x0+i*step-10,350,str(i),40)
for j,(p,a,b) in enumerate(dense['hits']):
    y=445+j*105;c.text(50,y,p,40)
    c.d.rounded_rectangle((x0+a*step,y,x0+b*step,y+60),radius=10,fill='#dceee6')
    c.text(x0+a*step+15,y,f'[{a},{b})',40)
c.text(50,1450,'每条带是一项输出；长度按区间比例画',40)
c.text(50,1530,'，'.join(p+' 有 '+str(sum(h[0]==p for h in dense['hits']))+' 项' for p in dense['patterns']),40)
c.text(50,1610,f"合计 {len(dense['hits'])} 项，扫描成本不能省去输出量 z",40)
c.save('12-output-count.png','用九条同尺度区间显示输出量不能被输入长度取代')

c=Canvas('一个字符，也可能连续退两次')
r=DATA['multi']
c.text(50,130,'变体：原文本末尾追加 x，成为',42)
c.text(50,205,DATA['text']+r['ch'],48,BLUE)
c.text(50,325,f"位置 {r['i']}，待处理的仍是 {r['ch']}",42)
for i,label in enumerate([r['before']]+r['fallback']):
    x=60+i*350;c.card(x,445,220,90,label)
    if i:c.arrow((x-115,490),(x-15,490),ORANGE,True)
c.text(50,600,'两条橙虚线都不消费 x',42,ORANGE)
c.text(50,710,'根也没有 x 出边：留在根，消费 x',40)
c.text(50,795,f"此时位置才从 {r['i']} 增到 {r['i']+1}",42)
c.text(50,905,'一次读字符可以多次回退；',42)
c.text(50,980,'总工作量要对整段扫描合起来计。',42)
c.save('14-multi-failure.png','在显式变体中显示同一字符连续两次失败，到根后才消费')

path=ROOT/'examples/figure-metadata.json'
old=json.loads(path.read_text()); old=[m for m in old if m['file'].split('/')[-1][:2] in ['00','01','02','03','04','05'] or int(m['file'].split('/')[-1][:2]) in [13,15,16]]
for m in meta:m['identity']='原创教学示意；数值来自 visual-results.json'
path.write_text(json.dumps(old+meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'added':len(meta),'geometry':'PASS'},ensure_ascii=False))
