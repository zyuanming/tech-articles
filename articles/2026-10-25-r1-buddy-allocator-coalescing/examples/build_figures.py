"""Generate all new explanatory figures from executed JSON. CC0-1.0."""
import json
from figurekit import Canvas, ROOT, DATA as D, meta, INK

C=D['colors']; TOTAL=D['total']; UNIT=D['unit']

def bar(c,y,blocks,labels=True):
    x0=60; w=936
    lengths=[w*b['size']/TOTAL for b in blocks]
    values=[b['size'] for b in blocks]
    assert sorted(range(len(values)),key=values.__getitem__) == sorted(range(len(lengths)),key=lengths.__getitem__)
    for b in blocks:
        x=x0+w*b['offset']/TOTAL; width=w*b['size']/TOTAL
        c.d.rectangle((x,y,x+width,y+100),fill=C[b['kind']],outline=INK,width=3)
        if b['kind']=='used' and b['request'] < b['size']:
            start=x+width*b['request']/b['size']
            c.d.rectangle((start,y+5,x+width-4,y+95),fill=C['waste'])
        text=b['name']; tw=c.d.textlength(text,font=__import__('PIL').ImageFont.truetype(__import__('figurekit').FONT,42))
        c.text(x+(width-tw)/2,y+18,text,42)
        if labels:c.text(x,y-58,str(b['offset']),40)
    if labels:c.text(x0+w-52,y-58,str(TOTAL),40)
    c.bottom=max(c.bottom,y+100)


def state(c,y,idx,group='main',title=None,table=True):
    s=D[group][idx];c.text(50,y,title or s['title'],44)
    bar(c,y+135,s['blocks'])
    c.text(50,y+255,f"表内空闲 {s['free_bytes']}；最大块 {s['largest']} 字节",42)
    if table:
        lists=s['free_lists']
        for k in range(len(lists)):
            value=', '.join(map(str,lists[k])) or '空'
            c.text(50,y+325+k*65,f"order {k} / {UNIT<<k} 字节：{value}",42)
        return y+615
    return y+345

c=Canvas('Buddy：只与同父伙伴合并')
s=D['fragment'][D['fragment_failed']]
bar(c,180,s['blocks']);c.text(50,320,'两个空闲块相邻，却不是伙伴',46)
c.text(50,395,f"总空闲 {s['free_bytes']} 字节，仍给不出 17 字节",44)
c.arrow((280,485),(280,555));c.arrow((750,485),(750,555))
c.card(60,580,430,110,'左侧父块');c.card(565,580,430,110,'右侧父块')
c.text(50,740,'能否合并，要沿分裂树向上找',44)
c.save('00-cover.png','用相邻但非伙伴反例引出合并规则')

c=Canvas('请求如何变成一个 order？')
round_rows=[D['rounding'][j] for j in [1,3,5]]
for field in ['size','request']:
    values=[r[field] for r in round_rows]
    lengths=[900*v/32 for v in values]
    assert sorted(range(len(values)),key=values.__getitem__) == sorted(range(len(lengths)),key=lengths.__getitem__)
for i,r in enumerate([D['rounding'][j] for j in [1,3,5]]):
 y=120+i*220;c.text(50,y,f"请求 {r['request']} → 块 {r['size']} 字节",44)
 width=900*r['size']/32;used=900*r['request']/32
 c.d.rectangle((60,y+75,60+width,y+145),fill=C['waste'])
 c.d.rectangle((60,y+75,60+used,y+145),fill=C['used'])
 c.text(50,y+155,f"order {r['order']}；块内余 {r['waste']} 字节",40)
 c.bottom=max(c.bottom,y+205)
c.text(50,805,'共用比例尺：整条宽度表示 32 字节',42)
c.save('01-rounding.png','共轴展示请求与保留块、内部碎片')

c=Canvas('从一整块，分到需要的大小')
y=state(c,110,0,table=False)
y=state(c,y+30,1,table=False)
y=state(c,y+30,2,table=False)
c.text(50,y+10,'橙色：暂取的左块；绿色：已入空闲表',40)
c.text(50,y+75,'上方刻度都是相对基址的字节偏移',40)
c.save('02-split.png','真实事件逐层展示64→32→16的分裂')

c=Canvas('分完 A，空闲表留下什么？')
y=state(c,110,3)
c.text(50,y,'蓝色为占用；粉色为块内未用部分',40)
c.text(50,y+70,'空闲表只列块起点，不逐字节列举',40)
c.save('03-free-lists.png','A分配后每阶空闲表与地址条对应')

c=Canvas('继续分配 B，再分配 C')
y=state(c,110,4,table=False)
y=state(c,y+35,5,table=False)
s=D['main'][5]
c.text(50,y+10,f"三次请求合计 {sum(b['request'] for b in s['blocks'])} 字节",44)
c.text(50,y+80,f"保留整块合计 {sum(b['size'] for b in s['blocks'])}；块内余 {s['internal']}",44)
c.save('04-allocated.png','不同请求占用全部arena以及内部碎片累计')

x=D['xor'];c=Canvas('XOR 翻转的是哪一位？')
for i,(label,val) in enumerate([('当前偏移',x['offset']),('块大小',x['size']),('伙伴偏移',x['partner'])]):
 c.text(60,130+i*125,f'{label}  {val:06b}  = {val}',48)
c.line((60,350),(990,350))
c.text(60,550,'同一父块内：左半 ↔ 右半',48)
c.text(60,635,f"{x['offset']} XOR {x['size']} = {x['partner']}",48)
c.text(60,730,'低位不变；只改变属于哪一半',44)
c.save('05-xor.png','二进制逐位说明固定伙伴为何能用XOR求得')

x=D['xor_bad'];c=Canvas('非零基址：先减，再 XOR，再加')
c.text(50,125,f"基址 {x['base']:#x}，块大小 {x['size']} 字节",44)
c.text(50,210,f"地址 {x['address']:#x} → 偏移 {x['offset']}",44)
c.card(60,325,930,100,f"正确：{x['base']:#x} + ({x['offset']} XOR {x['size']})")
c.text(70,450,f"得到伙伴地址 {x['correct']:#x}",48)
c.card(60,560,930,100,f"错误：{x['address']:#x} XOR {x['size']}",fill='#f3c5c0')
c.text(70,685,f"得到 {x['wrong']:#x}，不是同父伙伴",46)
c.text(50,785,'绝对地址对齐条件满足时才可简化',42)
c.save('06-base.png','同一非零arena在order0处的绝对地址XOR反例')

c=Canvas('释放 A：伙伴 B 还在使用')
y=state(c,110,6,table=False)
y=state(c,y+35,7)
c.text(50,y,'算到伙伴，只得到候选；仍须查状态',40)
c.save('07-free-a.png','释放后不满足空闲条件，不能合并')

c=Canvas('释放 B：先合到 32 字节')
y=state(c,110,8,table=False)
y=state(c,y+35,9,table=False)
y=state(c,y+35,10,table=False)
c.text(50,y,'先从 order 1 删伙伴，再升为 order 2',40)
c.text(50,y+65,'下一层伙伴是 C：仍占用，因此停下',40)
c.save('08-free-b.png','B释放与A合并，检查下一层后停止')

c=Canvas('释放 C：回到整块 64 字节')
y=state(c,110,11,table=False)
y=state(c,y+35,12,table=False)
y=state(c,y+35,13)
c.save('09-free-c.png','最后一次释放逐层恢复根块与空闲表')

c=Canvas('同一棵树：向下分裂，向上合并')
# Node width is geometric interval size; labels show half-open intervals.
nodes={(0,TOTAL)}
for event in D['main']:
    detail=event.get('detail')
    if detail and 'left' in detail:
        child_size=UNIT << detail['order']
        nodes.update([(detail['left'],child_size),(detail['right'],child_size)])
levels=[]
for size in sorted({size for _,size in nodes},reverse=True):
    levels.append(sorted((off,s) for off,s in nodes if s==size))
for depth,level in enumerate(levels):
 y=150+depth*230
 for off,size in level:
  center=60+936*(off+size/2)/TOTAL
  width=936*size/TOTAL-16
  if depth:
   parent_size=size*2;po=(off//parent_size)*parent_size
   pc=60+936*(po+parent_size/2)/TOTAL
   c.line((pc,y-130),(center,y-15))
  c.card(center-width/2,y,width,95,f'{off}–{off+size}')
c.text(50,825,'区间右端不含：0–16 表示 [0,16)',40)
c.text(50,900,'合并顺序：两个 16 → 32；两个 32 → 64',40)
c.text(50,975,'未画的子节点没有被本次请求拆开',40)
c.save('10-tree.png','真实贯穿例子的分裂树显示兄弟与共同父块')

c=Canvas('连续空闲，也未必是合法大块')
y=state(c,110,7,'fragment',table=False,title='先分配四个 16 字节块')
y=state(c,y+35,D['fragment_failed'],'fragment',table=False)
c.text(50,y,'Q 的伙伴是 P；R 的伙伴是 S',44)
c.text(50,y+75,'[16,48) 虽连续，却跨过两个父块',42)
c.text(50,y+145,'32 字节块只能从偏移 0 或 32 开始',42)
c.save('11-fragment.png','相邻同大小空闲块不具有同父关系的失败反例')

c=Canvas('同样的请求，释放布局决定结果')
y=state(c,110,D['fragment_failed'],'fragment',table=False)
y=state(c,y+35,19,'fragment',table=False)
y=state(c,y+35,21,'fragment',table=False)
c.text(50,y,'本模型没有移动活块：等 P、S 也释放',40)
c.save('12-recovery.png','失败状态到全部释放再申请成功的实跑对照')

c=Canvas('两个 arena 不能凑成一个块')
for i,a in enumerate(D['arenas']):
 y=130+i*230
 c.text(50,y,f"arena {i+1}：{a['base']:#x}–{a['base']+a['total']:#x}",44)
 c.card(60,y+80,936*a['total']/TOTAL,100,f"空闲 {a['free']} 字节",fill=C['free'])
c.text(50,650,f"总空闲 {sum(a['free'] for a in D['arenas'])} 字节",46)
assert not any(a['accepted'] for a in D['arenas'])
c.text(50,735,'请求 48 字节：两个 arena 都失败',44)
c.text(50,820,'相邻地址不能抹去管理边界',44)
c.save('13-arenas.png','独立管理域不会因地址相邻而跨界合并')

c=Canvas('管理数据不等于用户的载荷')
c.card(60,140,930,105,'模拟载荷：一段 64 字节地址空间',fill=C['used'])
c.arrow((530,270),(530,350))
c.card(60,385,930,105,'used：名称 → 偏移、order、请求量')
c.card(60,535,930,105,'free[order]：可用块起点集合',fill=C['free'])
c.text(50,725,'本程序：管理表在 Python 对象里',44)
c.text(50,800,'生产实现：可用外置表或块头等方案',42)
c.text(50,875,'这些对象的内存成本不算进 64 字节',42)
c.save('14-metadata.png','区分模型容量、分配记录、空闲表和语言对象开销')
screenshot=ROOT/'assets/15-viewer.png'
if screenshot.exists():
    from PIL import Image
    im=Image.open(screenshot)
    meta.append(dict(file='assets/15-viewer.png',width=im.width,height=im.height,
        min_font_px=42,effective_min_font_at_354=14,
        identity='实际Chromium原创HTTP教学界面截图；354 CSS px，deviceScaleFactor=3',
        purpose='显示实跑JSON的失败状态、区间表与各阶空闲表',
        checks=['all-events-mobile-overflow','desktop-overflow','browser-errors','actual-dimensions']))
for entry in meta:
    entry['license']='CC-BY-4.0'
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(f'{len(meta)} original figures checked')
