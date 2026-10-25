"""Figures derive objects, rows and edges from actual evaluator output. CC0."""
import json
from figurekit import Canvas, DATA as D, ROOT, meta, BLUE, GREEN, ORANGE, INK

# All x/y/width/height literals below are layout, not model data.
def lines(c, x, y, rows, color=INK, gap=65):
    for row in rows:
        c.text(x,y,row,42,color);y+=gap
    return y

def save(c,name,purpose):
    c.save(name,purpose)

c=Canvas('一张表，怎样成为程序？')
frames=D['recursive_frames']
for i,frame in enumerate(frames):
    y=140+i*180
    c.card(110,y,660,100,'first '+frame['args'][0])
    if i: c.arrow((440,y-75),(440,y-12))
c.text(100,710,'eval 读表达式 · apply 执行调用',44)
c.text(100,790,'McCarthy 经典求值器的教学模型',42)
save(c,'00-cover.png','独立封面：递归输入逐步缩小')

c=Canvas('表不是一整块字符串')
g=D['structure'];nodes={n['id']:n for n in g['nodes']}
chain=[];nid=g['root']
while nodes[nid]['type']=='pair':
    chain.append(nodes[nid]);nid=nodes[nid]['cdr']
for i,node in enumerate(chain):
    x=90+i*470;y=180
    c.card(x,y,190,100,nodes[node['car']]['value'])
    c.card(x+195,y,180,100,'cdr')
    c.text(x+45,305,'car',42)
    if i<len(chain)-1:c.arrow((x+375,y+50),(x+465,y+50))
    else:
        c.arrow((x+280,y+105),(x+280,y+235))
        c.card(x+190,y+245,190,90,nodes[nid]['value'])
c.text(65,515,'读作 '+D['cons']['result'],46)
c.text(65,590,'car 取左格；cdr 沿右格走',42)
c.text(65,665,'nil 是空表，也是原子',42)
save(c,'01-pairs.png','实际Pair对象遍历出的两格链表和终止符')

c=Canvas('同一棵结构，两种处理方式')
c.text(70,130,'对象：'+D['quoted']['result'],42)
c.arrow((530,215),(280,295));c.arrow((530,215),(795,295))
c.card(60,310,435,90,'quote：原样返回')
c.card(565,310,435,90,'eval：解释执行')
c.text(65,465,'返回可再处理的表',42)
c.text(580,465,'调用 car',42)
c.text(65,540,D['quoted']['result'].split(' (quote')[0],40)
c.text(65,605,'(quote'+D['quoted']['result'].split('(quote')[1],40)
c.text(580,540,'返回 '+D['executed']['result'],46,GREEN)
c.text(65,720,'左边把实际返回值分行显示，未执行 car',42)
save(c,'02-quote.png','quote返回结构与eval解释同一结构的分叉')

c=Canvas('先实际拆一次，再接一次')
for i,key in enumerate(('car','cdr','cons','pair')):
    y=140+i*190
    c.text(65,y,D[key]['source'],44)
    c.arrow((110,y+80),(320,y+80))
    c.text(350,y+45,D[key]['result'],46,GREEN)
c.text(65,920,'(a . b) 的右格是原子 b，并非表尾',42)
save(c,'03-operations.png','运行car/cdr/cons，区分正常表与点对')

c=Canvas('atom 与 eq 问的是不同问题')
for i,key in enumerate(('nil_atom','list_atom','eq_same','eq_different','empty_eq')):
    y=130+i*135
    c.text(60,y,D[key]['source'],42)
    c.card(770,y-5,220,85,D[key]['result'],color=GREEN)
c.text(60,860,'eq 只接收符号原子；表深比较另写',42)
save(c,'04-predicates.png','原子/空表真值和eq定义域的实际计算')

c=Canvas('cond 只走命中的那条分支')
test=next(e for e in D['safe_cond']['events'] if e['kind']=='test')
c.card(290,130,450,90,'判断 '+test['test']+' = '+test['value'])
c.arrow((390,230),(255,340),GREEN)
c.line((750,230),(860,340),ORANGE,dashed=True)
c.card(65,360,430,90,"执行 (quote ok)",color=GREEN)
c.card(565,360,430,90,"跳过 (car 'a)",color=ORANGE)
c.text(70,515,'实际返回 '+D['safe_cond']['result'],46,GREEN)
c.text(70,600,'若先算所有分支的结果：',42)
err=next(e for e in D['errors'] if e['name']=='eager_branch')
c.text(70,675,err['error'],44,ORANGE)
c.text(70,760,'虚线是不执行的路，不是异常已发生',40)
save(c,'05-cond.png','真分支与被跳过错误分支对照，错误由反例实跑')

c=Canvas('eval 与 apply 接力的接口')
c.card(100,140,860,100,'eval：表达式 + 环境')
c.arrow((535,250),(535,335))
c.card(100,355,860,100,'先求参数值，再交给 apply')
c.arrow((535,465),(535,550))
c.card(100,570,860,100,'apply：函数描述 + 值 + 环境')
c.arrow((260,685),(260,785));c.arrow((790,685),(790,785))
c.card(50,810,445,100,'基本操作：直接返回')
c.card(565,810,445,100,'lambda：绑定参数')
c.arrow((790,925),(790,1015))
c.card(565,1040,445,100,'再 eval 函数体')
c.text(65,1230,'quote、cond 在 eval 内先处理',42)
save(c,'06-eval-apply.png','接口示意：表达式与已算出的值不混用')

c=Canvas('参数值怎样变成变量值')
bind=next(e for e in D['simple']['events'] if e['kind']=='bind')
c.text(65,135,'lambda 的形参        实际参数值',42)
for i,(param,value) in enumerate(zip(bind['params'],bind['values'])):
    y=245+i*150
    c.card(70,y,250,90,param)
    c.arrow((335,y+45),(560,y+45))
    c.card(580,y,420,90,value)
c.text(65,605,'新环境：新绑定排在原环境之前',42)
for i,(k,v) in enumerate(bind['env']):
    c.text(145,700+i*70,k+' → '+v,44)
c.text(65,945,'参数都在调用者环境中先求值',42)
save(c,'07-binding.png','真实bind事件生成参数与环境关联表')

c=Canvas('一次调用：进入与返回值')
calls=D['simple']['calls']
selected=[p for p in calls if (p['kind']=='eval' and p['expr'] in
 ['(quote (a b))','(quote (c))','x','y','(car x)','(cons (car x) y)'])]
for i,p in enumerate(selected):
    y=130+i*135
    c.text(65,y,p['expr'],42)
    c.arrow((530,y+40),(670,y+40))
    c.text(705,y,p['result'],44,GREEN)
c.text(65,130+len(selected)*135,'按进入 eval 的先后列出；右侧为返回值',40)
save(c,'08-call-frames.png','真实eval调用记录：表达式与返回值逐帧配对')

c=Canvas('label 让递归名进入环境')
lab=next(e for e in D['recursive']['events'] if e['kind']=='label')
c.card(100,140,860,100,'first  →  lambda 函数描述')
c.text(65,310,'进入函数体后，查找 first 就能再调用',42)
for i,fr in enumerate(frames):
    binding=next(e for e in D['recursive']['events'] if e['kind']=='bind' and e['parent']==fr['id'])
    y=445+i*190
    c.text(65,y,'本层 x = '+binding['values'][0],44)
    env=binding['env'];c.text(65,y+70,'关联表顺序：'+' / '.join(k for k,v in env),40)
c.text(65,1090,'查找遇到第一个同名绑定就停',42)
save(c,'09-recursive-env.png','由label和bind事件显示名字绑定与新旧x遮蔽')

c=Canvas('递归调用下去，结果逐层回来')
lookup={p['id']:p for p in D['recursive']['calls']}
positions={fr['id']:(125+i*190,150+i*240) for i,fr in enumerate(frames)}
frame_ids=set(positions)
for fr in frames:
    parent=fr['parent']
    while parent is not None and parent not in frame_ids:parent=lookup[parent]['parent']
    x,y=positions[fr['id']]
    if parent is not None:
        px,py=positions[parent]
        c.arrow((px+100,py+105),(x+100,y-12),BLUE)
        c.arrow((x+440,y-15),(px+440,py+105),GREEN)
    c.card(x,y,500,95,'first '+fr['args'][0])
    c.text(x,y+110,'返回 '+fr['result'],42,GREEN)
c.text(65,1000,'蓝：调用；绿：返回；边来自真实调用栈',40)
c.text(65,1080,'最后一层 atom 为真，不再执行 car',42)
save(c,'10-recursion-tree.png','从真实调用parent链压缩出的递归树及返回值')

c=Canvas('这里查的是调用时的环境')
lookup_event=next(e for e in D['dynamic']['events'] if e['kind']=='lookup' and e['name']=='x')
for i,(key,val) in enumerate(lookup_event['env']):
    label=key+' → '+ ('lambda () x' if val.startswith('(lambda') else val)
    y=150+i*140
    c.card(170,y,790,90,label,color=GREEN if i==lookup_event['index'] else INK)
    if i==lookup_event['index']: c.arrow((55,y+45),(155,y+45),GREEN)
c.text(65,670,'第一个 x 命中：'+D['dynamic']['result'],44,GREEN)
c.text(65,755,'f 只有函数描述，没有保存定义环境',42)
c.text(65,840,'因此它不是现代词法闭包',42)
save(c,'11-dynamic.png','实际lookup事件揭示调用时遮蔽与未捕获环境')

c=Canvas('哪些输入会被明确拒绝？')
for i,name in enumerate(('unbound','car_nil','deep_eq','arity','no_clause','loop')):
    e=next(e for e in D['errors'] if e['name']==name);y=140+i*145
    title={'unbound':'未绑定变量','car_nil':'拆空表','deep_eq':'用 eq 深比较','arity':'参数个数错','no_clause':'没有真分支','loop':'不缩小的递归'}[name]
    c.text(65,y,title,42)
    c.text(380,y,e['error'],40,ORANGE)
c.text(65,1090,'步数上限是实验保护，不是终止性证明',42)
save(c,'12-errors.png','真实错误分类与有限步数边界')
c=Canvas('嵌套表：左格也能指向一张表')
g=D['nested_structure'];ns={n['id']:n for n in g['nodes']}
outer=ns[g['root']];inner=ns[outer['car']]
outer_tail=ns[outer['cdr']];inner_tail=ns[inner['cdr']]
positions={outer['id']:(65,180),outer_tail['id']:(580,180),
           inner['id']:(65,560),inner_tail['id']:(580,560)}
for node in (outer,outer_tail,inner,inner_tail):
    x,y=positions[node['id']];left=ns[node['car']];right=ns[node['cdr']]
    c.card(x,y,180,95,left.get('value','car'))
    c.card(x+185,y,180,95,'cdr')
    if right['type']=='pair':
        tx,ty=positions[right['id']];c.arrow((x+370,y+45),(tx-12,ty+45))
    else:
        c.arrow((x+280,y+105),(x+280,y+185))
        c.card(x+190,y+200,175,80,right['value'])
    if left['type']=='pair':
        tx,ty=positions[left['id']];c.arrow((x+90,y+105),(tx+90,ty-15))
c.text(220,440,'car 进入内层 (a b)',42)
c.text(65,930,'外层：先是子表，再是原子 c',42)
c.text(65,1010,'内层：a、b；两条 cdr 链各以 nil 终止',40)
save(c,'14-nested-pairs.png','实际嵌套Pair结构：外层car到子表、两条cdr链')
from PIL import Image
screenshot=ROOT/'assets/13-live-evaluator.png'
if screenshot.exists():
    with Image.open(screenshot) as im:
        meta.append(dict(file='assets/13-live-evaluator.png',width=im.width,height=im.height,
            min_font_px=42,effective_min_font_at_354=14,
            identity='自制Python教学程序真实Chromium截图',
            purpose='运行主例并展示真实参数绑定',
            checks=['actual-http-execution','actual-dimensions','desktop-and-mobile-visual']))
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('saved',len(meta),'figures')
