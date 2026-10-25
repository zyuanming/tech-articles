"""Original COBS diagrams. Code CC0-1.0; output figures CC BY 4.0.
All sequence values, indices, block counts and lengths come from results.json.
Coordinates, spacings, font sizes and palette are layout constants.
"""
from figurekit import Canvas,DATA as D,ROOT,meta,BLUE,GREEN,ORANGE,INK
import json

def hx(v):return f'{v:02X}'
def tape(c,values,y,codes=(),pending=None,indices=False,neutral=False):
    for i,v in enumerate(values):
        x=50+i*95
        fill='#e1edf7' if i in codes else '#e9f1eb'
        color=BLUE if i in codes else GREEN
        if neutral and i not in codes:fill='#e8e9ed';color=INK
        if v==0:fill='#fae6cf';color=ORANGE
        c.card(x,y,84,80,'?' if i==pending else hx(v),fill,color)
        if indices:c.text(x+23,y+90,str(i),40)
    return y+(150 if indices else 110)

def text(c,y,lines,color=INK):
    for line in lines:c.text(50,y,line,42,color);y+=65
    return y

c=Canvas('COBS：把零留给包的边界')
y=text(c,120,['原数据里的零，也必须完整送达'])
y=tape(c,D['payload'],y+15)
c.arrow((530,y),(530,y+65))
y=text(c,y+90,['编码后，正文内不再有 00'])
y=tape(c,D['encoded'],y+15,[x['start'] for x in D['dec_trace']])
y=text(c,y+15,['再加 00，接收端才知道包到此结束'],ORANGE)
c.save('00-cover.png','独立封面：原始零与帧末定界符的不同职责')

c=Canvas('同一条字节流，包界可能不同')
y=text(c,120,['原始连续字节（全部是十六进制）'])
y=tape(c,D['payload'],y+15)
for label,groups in [('可能 A：全部属于同一包',[D['payload']]),('可能 B：拆成两包',[D['payload'][:3],D['payload'][3:]])]:
    y=text(c,y+20,[label]);x=50
    for g in groups:
        w=len(g)*95-10;c.d.rounded_rectangle((x,y,x+w,y+95),radius=15,outline=BLUE,width=5)
        c.text(x+12,y+20,' '.join(map(hx,g)),40,box=(x,y,x+w,y+95));c.bottom=max(c.bottom,y+95);x+=w+25
    y+=135
y=text(c,y,['数据相同；若无协议，无法选定包界'])
c.save('01-ambiguity.png','同一数据两种分包解释，read返回不提供语义边界')

c=Canvas('先按原始零分组，空组也留下')
y=120;cursor=0
for i,g in enumerate(D['input_groups']):
    label='结束后留下的空组' if i==len(D['input_groups'])-1 else '这一组后面有原始零'
    y=text(c,y,[f'组 {i}：'+label])
    if g:y=tape(c,g,y+5)
    else:y=text(c,y+5,['（没有非零数据）'],GREEN)
    cursor+=len(g)
    if i<len(D['input_groups'])-1:
        c.text(660,y-85,f'零在原下标 {cursor}',40,ORANGE);cursor+=1
    y+=30
c.save('02-zero-groups.png','显式保留连续零之间及末零之后的空组')

def snapshot(c,event,y):
    y=text(c,y,[f"读原下标 {event['index']}：{hx(event['value'])}"])
    y=tape(c,event['out'],y+10,codes=event['completed_codes'],pending=event['pointer'],indices=True)
    y=text(c,y,[f"待填位置 p = {event['pointer']}；计数 c = {event['count']}"])
    return y+25

c=Canvas('先留一个位置，再复制非零数据')
y=text(c,120,[f"p 指向待填码字，c 从 {D['enc_trace'][0]['before']['count']} 起数"])
y=snapshot(c,D['enc_trace'][0],y+15)
y=snapshot(c,D['enc_trace'][1],y)
y=text(c,y,['? 是内存占位，不会作为 00 发出去'])
c.save('03-encode-copy.png','第一次复制两个非零字节，显示真实p/c和待回填字节')

c=Canvas('遇到零：把计数填回前面的空位')
e=D['enc_trace'][2]
y=text(c,120,[f"读到原下标 {e['index']} 的 00",f"把 {e['before']['count']} 写到输出下标 {e['before']['pointer']}"])
y=snapshot(c,e,y+10)
y=text(c,y,['原始 00 不复制；开下一块的占位',f"{hx(e['before']['count'])} 的值是 {e['before']['count']}：含码字，跨过这一块"])
c.save('04-encode-zero.png','第一次回填03并为下块预留位置')

c=Canvas('连续两个零，中间就是一个空块')
y=snapshot(c,D['enc_trace'][4],120)
y=snapshot(c,D['enc_trace'][5],y)
y=text(c,y,['空块没有数据，码字仍是 01','它跨到紧邻的下一个码字'])
c.save('05-encode-double-zero.png','先封闭33所在块，再由连续零封闭零数据块')

c=Canvas('最后是零，还要封好最后的空块')
y=snapshot(c,D['enc_trace'][7],120)
y=text(c,y,['输入结束：把当前计数填回 ?'])
y=tape(c,D['encoded'],y+15,[x['start'] for x in D['dec_trace']],indices=True)
y=text(c,y,['最后的 01 让前一块知道：还有块','因此前一块的原始末零能够恢复'])
c.save('06-encode-end.png','原末零后的待填位置必须最终填01')

c=Canvas('沿着码字跳：不能随便挑一个字节')
y=120
for t in D['dec_trace']:
    y=text(c,y,[f"下标 {t['start']}，码字 {hx(t['code'])}（值 {t['code']}）"])
    c.card(50,y,150,80,hx(t['code']),'#e1edf7',BLUE)
    for j,b in enumerate(t['copied']):c.card(230+j*100,y,84,80,hx(b),'#e9f1eb',GREEN)
    c.arrow((540,y+40),(720,y+40))
    c.text(750,y+12,f"到 {t['next']}",42)
    y+=110
y=text(c,y,[f"{len(D['encoded'])} 是编码长度；到这里就停止",'下标与计数用十进制，格内用十六进制'])
c.save('07-code-chain.png','全部5个码字位置的跳跃链及终点')

for name,title,steps in [('08-decode-first.png','解码前两块：复制，然后补零',D['dec_trace'][:2]),('09-decode-last.png','空块与末块：是否补零看后面',D['dec_trace'][2:])]:
    c=Canvas(title);y=120
    for t in steps:
        y=text(c,y,[f"码字 {hx(t['code'])}：复制 {t['count']} 字节",'后面还有块：补一个 00' if t['add_zero'] else '已到编码末尾：不补 00'])
        y=tape(c,t['out'],y+10)
        y+=25
    c.save(name,'逐块显示已恢复前缀，补零条件来自解码trace')

c=Canvas('FF 作为码字：复制满块，不补零')
b=D['boundaries'][1];y=120
y=text(c,y,[f"输入：{b['n']} 个非零字节（均为 55）"])
c.card(50,y,110,90,hx(b['plain_codes'][0]),'#e1edf7',BLUE)
w=b['plain_blocks'][0]*3
c.d.rectangle((180,y,180+w,y+90),fill='#d7e9df');c.bottom=max(c.bottom,y+90)
c.text(210,y+18,f"{b['plain_blocks'][0]} 个 55",42,GREEN,box=(180,y,180+w,y+90))
y+=125
y=text(c,y,['长条省略展开，不是单个字节格',f"{hx(b['plain_codes'][0])} 的十进制值是 {b['plain_codes'][0]}",f"{b['plain_codes'][0]} − 1 = {b['plain_blocks'][0]} 个数据字节",'此块之后不隐含一个 00'])
y+=20
y=text(c,y,['同一个 FF，也可以是普通数据：'])
y=tape(c,D['tiny'][-1]['encoded'],y+10,[0])
y=text(c,y,['02 是码字；紧随的 FF 是数据'])
c.save('10-full-block.png','254个数据位置与FF码字语义，以及数据FF的反例')

c=Canvas('满块结尾：两种输出，相同原数据')
y=120
for b in D['boundaries']:
    y=text(c,y,[f"输入 {b['n']} 个非零字节"])
    c.text(50,y,'常规版本',42,BLUE);c.text(450,y,'末满块优化',42,GREEN);y+=65
    c.text(50,y,'码：'+' '.join(map(hx,b['plain_codes'])),42)
    c.text(450,y,'码：'+' '.join(map(hx,b['compact_codes'])),42);y+=65
    c.text(50,y,f"共 {b['plain']} 字节",42)
    c.text(450,y,f"共 {b['compact']} 字节",42);y+=100
y=text(c,y,['只在最后完整 FF 块后省去空码 01','这里只列码字；数据原样夹在块内','长度均未计帧末 00'])
c.save('11-boundary-conventions.png','253/254/255/508输入长度下的真实两约定码字与长度')

c=Canvas('满块后有原始零，不能当作满块结尾')
z=D['after_full_zero'];y=text(c,120,[f"输入：{z['blocks'][0]} 个 55，再一个 00",f"共 {z['n']} 字节；输出共 {z['encoded_length']} 字节"])
for i,(code,n) in enumerate(zip(z['codes'],z['blocks'])):
    y=text(c,y+20,[f"块 {i}：码字 {hx(code)}，复制 {n} 字节"])
    action='此块不补零' if code==255 else ('后面有块，补原始零' if i<len(z['codes'])-1 else '最后空块，不补零')
    y=text(c,y,[action],BLUE if code==255 else ORANGE)
c.save('12-full-then-zero.png','FF后真实末零需要01 01，不能错误删掉')

c=Canvas('空数据不是一个孤零零的定界符')
y=120
for t in D['tiny'][:4]:
    label=' '.join(map(hx,t['input'])) or '空 payload'
    y=text(c,y,['输入：'+label])
    y=tape(c,t['wire'],y+10,t['codes']);y+=20
y=text(c,y,['橙色 00 是外加定界符','裸 00 留下空片段；本接收器忽略它'])
c.save('13-empty-payload.png','空payload/单零/连零/无零的线缆序列区分')

c=Canvas('read 的分段，可以切在任何位置')
y=120
for i,t in enumerate(D['chunks']):
    y=text(c,y,[f"第 {i+1} 次收到："])
    y=tape(c,t['chunk'],y+5,neutral=True)
    label='待收：'+' '.join(map(hx,t['buffer'])) if t['buffer'] else '待收缓冲为空'
    y=text(c,y,[label,f"本次交出 {len(t['emitted'])} 个包"])
    y+=25
y=text(c,y,['灰色：收到但未解码；橙色：定界零'])
c.save('14-receive-chunks.png','任意read分段，第四次跨包且留下下包前缀')

c=Canvas('字节改错了，仍可能是合法的 COBS')
y=120
for e in D['errors'][:2]:
    y=text(c,y,[f"数据位翻转：{hx(D['encoded'][1])} 变成 {hx(e['input'][1])}" if e['name']=='data_flip' else f"码字改成 {hx(e['input'][0])}，索要太多字节"])
    y=tape(c,e['input'],y+10,e['codes'],neutral=not e['accepted'])
    if e['accepted']:
        y=text(c,y,['解码器接受，但数据已经错了'],ORANGE);y=tape(c,e['output'],y+5)
    else:y=text(c,y,['拒绝：码字指到当前帧之外'],ORANGE)
    y+=30
c.save('16-errors.png','实跑显示可检出的长度错误和不可检出的数据错误')

c=Canvas('丢了一个定界符，两个包会粘住')
y=text(c,120,['主例后接空 payload；删除中间 00'])
v=D['lost_delimiter']['chunk'];cut=v.index(0)
y=tape(c,v[:cut],y+15,D['lost_delimiter']['first_codes'])
y=text(c,y,['这段仍能解码，但末尾多出一个零'])
y=tape(c,D['lost_delimiter']['packets'][0],y+10)
y=text(c,y,['后一个完整无错帧仍能恢复：'])
y=tape(c,D['lost_delimiter']['packets'][-1],y+10)
y=text(c,y,['恢复后继包的边界，不是救回受损包'])
c.save('17-resync.png','真实丢定界符反例：拼接合法但payload错，后继66恢复')

(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(f'Generated {len(meta)} diagrams; geometry/glyph/ink checks passed')
