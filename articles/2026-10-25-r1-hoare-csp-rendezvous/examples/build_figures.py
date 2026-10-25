#!/usr/bin/env python3
# CC0-1.0 code; original generated illustrations CC BY 4.0.
import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / 'results.json').read_text())
RUN = DATA['runs']
FONT = Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
assert FONT.exists(), 'Chinese font required'
CMAP = TTFont(str(FONT), fontNumber=0).getBestCmap()
BG, INK, BLUE, LIGHT, GOLD, RED = '#faf7ef', '#192d3b', '#165b70', '#e1efeb', '#f5e1ab', '#8c3038'
META = []


def lum(c):
    a = [int(c[i:i+2], 16)/255 for i in (1, 3, 5)]
    a = [x/12.92 if x <= .04045 else ((x+.055)/1.055)**2.4 for x in a]
    return sum(v*w for v, w in zip(a, [.2126, .7152, .0722]))


class Sheet:
    def __init__(self, name, title, purpose):
        self.name, self.purpose = name, purpose
        self.im = Image.new('RGB', (1062, 6000), BG)
        self.pen = ImageDraw.Draw(self.im)
        self.items, self.last, self.segments = [], 0, []
        self.text(48, 40, title, 52)
        self.line((48, 122, 1014, 122))
    def text(self, x, y, s, size=44, color=INK, box=None, bg=BG):
        assert size >= 40
        assert all(ord(c) in CMAP for c in s), ('missing glyph', s)
        f = ImageFont.truetype(str(FONT), size)
        b = self.pen.textbbox((x, y), s, font=f, anchor='lt')
        assert 28 <= b[0] and b[2] <= 1034 and b[1] >= 0, (self.name, s, b)
        if box:
            assert box[0]+8 <= b[0] and b[2] <= box[2]-8 and box[1]+8 <= b[1] and b[3] <= box[3]-8, (s, b, box)
        for old in self.items:
            a = old['bbox']
            assert not (b[0] < a[2] and b[2] > a[0] and b[1] < a[3] and b[3] > a[1]), (s, old['text'])
        lo, hi = sorted([lum(color), lum(bg)])
        contrast = (hi+.05)/(lo+.05)
        assert contrast >= 4.5
        self.pen.text((x, y), s, fill=color, font=f, anchor='lt')
        ink = sum(1 for p in self.im.crop(b).getdata() if p != tuple(bytes.fromhex(bg[1:])))
        assert ink > size, ('no ink', s)
        self.items.append({'text': s, 'bbox': b, 'font_px': size, 'contrast': contrast, 'ink_pixels': ink, 'box': box})
        self.last = max(self.last, b[3])
    def line(self, points, color=BLUE, width=4):
        self.pen.line(points, fill=color, width=width)
        self.segments.append((points, width))
        self.last = max(self.last, max(points[1::2]))
    def arrow(self, a, b, color=BLUE):
        self.line((*a, *b), color)
        t = math.atan2(b[1]-a[1], b[0]-a[0])
        self.pen.polygon([b, (b[0]-18*math.cos(t-.5), b[1]-18*math.sin(t-.5)),
                          (b[0]-18*math.cos(t+.5), b[1]-18*math.sin(t+.5))], fill=color)
    def box(self, b, fill=LIGHT):
        self.pen.rounded_rectangle(b, 18, fill, BLUE, 3)
        self.last = max(self.last, b[3])
    def save(self, out):
        # Conservative sampled segment-to-text audit; no diagram stroke may cross text.
        for points, width in self.segments:
            x1,y1,x2,y2 = points
            n = max(abs(x2-x1),abs(y2-y1),1)
            for item in self.items:
                a,b,d,e=item['bbox']
                for k in range(int(n)+1):
                    x=x1+(x2-x1)*k/n; y=y1+(y2-y1)*k/n
                    assert not (a-width/2 < x < d+width/2 and b-width/2 < y < e+width/2), (self.name,'line crosses text',item['text'])
        h = int(self.last+48)
        self.im = self.im.crop((0, 0, 1062, h))
        self.im.save(out / (self.name+'.png'))
        assert Image.open(out / (self.name+'.png')).size == (1062, h)
        META.append({'file': 'assets/'+self.name+'.png', 'width': 1062, 'height': h,
                     'minimum_font_px': min(x['font_px'] for x in self.items),
                     'mobile_width': 354, 'identity': '原创教学模型图，来自实际有限状态枚举结果',
                     'license': 'CC-BY-4.0', 'purpose': self.purpose, 'data': 'examples/results.json',
                     'checks': ['glyph-cmap', 'bounds', 'declared-box', 'text-overlap', 'font-size', 'contrast', 'ink', 'dynamic-crop', 'PNG-dimensions'],
                     'geometry': '状态数量/路径/队列格占用/指令位置由JSON计算；坐标为无物理单位的排版常量',
                     'texts': self.items})


def optext(op):
    k = op[0]
    if k == 'send': return f'{op[1]}!{op[2]}'
    if k == 'recv': return f'{op[1]}?{op[2]}'
    if k == 'add': return f'{op[1]} := {op[1]} + {op[2]}'
    if k == 'record': return f'记下 {op[1]}'
    return '内部准备'


def pcs(s):
    return '  '.join(f'{k}{v}' for k, v in s['pc'].items())


def title_event(e):
    if e['kind'] == 'rendezvous': return f'{e["actors"][0]} → {e["actors"][1]}  交接 {e["value"]}'
    if e['kind'] == 'add': return e['label']
    if e['kind'] == 'record': return e['label'].replace('record', '记下')
    return e['label']


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    p = RUN['pipeline']; vals = DATA['inputs']
    c = Sheet('00-cover', '发送已经开始，为什么还没完成？', '独立封面：把会合表示为两边共同跨过的门槛')
    c.text(70, 180, 'P 准备发送', 50); c.text(650, 180, 'M 准备接收', 50)
    for x in (210, 830): c.line((x, 290, x, 650), BLUE, 7)
    c.box((370, 345, 690, 485), GOLD)
    c.text(420, 385, f'值 {vals[0]}', 60, box=(370,345,690,485), bg=GOLD)
    c.arrow((220,415),(355,415)); c.arrow((705,415),(820,415))
    c.text(65, 715, '一次会合：传值，同时推进双方', 50)
    c.text(65, 810, 'Hoare CSP 的同步通信', 44)
    c.save(out)

    c = Sheet('01-program', '把任务拆成三个顺序进程', '列出贯穿例的每条本地指令与数据流')
    names = list(p['program'])
    for col, name in enumerate(names):
        x = 48 + col*326
        c.box((x, 175, x+310, 860))
        c.text(x+24, 200, name, 56, box=(x,175,x+310,860), bg=LIGHT)
        for row, op in enumerate(p['program'][name]):
            c.text(x+20, 310+row*82, optext(op), 40, box=(x,175,x+310,860), bg=LIGHT)
    c.text(70, 915, f'P 产出 {vals}；M 每次加 {DATA["increment"]}', 44)
    end = p['states'][p['complete'][0]]['output']['C']
    c.text(70, 995, f'C 最终按顺序记下 {end}', 44)
    c.text(70, 1080, '! 是发送；? 是接收；竖排是本地顺序', 40)
    c.save(out)

    a = RUN['arrival']
    c = Sheet('02-arrival', '先到的一方，要停在哪里？', '由实际三状态解释先到等待、另一方准备及同时推进')
    for i, s in enumerate(a['states']):
        y = 180+i*260
        c.text(65, y, f'状态 {i}：'+pcs(s), 46)
        left = optext(a['program']['P'][s['pc']['P']]) if s['pc']['P'] < len(a['program']['P']) else 'P 已完成'
        right = optext(a['program']['M'][s['pc']['M']]) if s['pc']['M'] < len(a['program']['M']) else f'M 得到 x={s["local"]["M"]["x"]}'
        c.box((65,y+80,450,y+170), GOLD); c.box((610,y+80,995,y+170))
        c.text(90,y+100,left,44,box=(65,y+80,450,y+170),bg=GOLD)
        c.text(635,y+100,right,44,box=(610,y+80,995,y+170),bg=LIGHT)
        if i < len(a['trace']):
            e=a['trace'][i]
            c.text(80,y+195,'只推进 M 的准备' if e['kind']=='prepare' else '传值；P、M 一起越过通信',40)
    c.text(65, 980, '数字表示已完成指令数，不表示秒数', 42)
    c.save(out)

    c = Sheet('03-trace', '流水线的一条完整执行轨迹', '逐事件保存值传递与局部计算，不能只呈现最终输出')
    c.text(55,170,'动作完成后',42); c.text(685,170,'指令位置',42)
    for i,e in enumerate(p['trace']):
        y=255+i*115
        c.text(55,y,f'{i+1}. '+title_event(e),42)
        c.text(685,y,pcs(p['states'][e['to']]),42)
        c.line((55,y+76,1005,y+76), '#becbc8',2)
    c.text(55,255+len(p['trace'])*115,'! 与 ? 配成一次事件，不是两次转移',40)
    c.save(out)

    branch = next(s for s in range(len(p['states'])) if len([e for e in p['edges'] if e['from']==s])==2)
    es=[e for e in p['edges'] if e['from']==branch]
    ends=[{e['to'] for e in p['edges'] if e['from']==first['to']} for first in es]
    join=next(iter(ends[0]&ends[1]))
    c = Sheet('04-order', '局部顺序，并不等于全局唯一顺序', '真实可达图中的菱形：内部记录与下一次会合可交换')
    coords={branch:(315,170), es[0]['to']:(60,520),es[1]['to']:(590,520),join:(315,900)}
    for e in [*es,*[e for e in p['edges'] if e['from'] in [x['to'] for x in es] and e['to']==join]]:
        x,y=coords[e['from']]; xx,yy=coords[e['to']]
        c.arrow((x+210,y+150),(xx+210,yy-10))
    for sid,(x,y) in coords.items():
        box=(x,y,x+410,y+145);c.box(box)
        c.text(x+22,y+20,f'状态 {sid}',42,box=box,bg=LIGHT)
        c.text(x+22,y+82,pcs(p['states'][sid]),42,box=box,bg=LIGHT)
    c.text(65,340,title_event(es[0]),40)
    c.text(650,340,title_event(es[1]),40)
    for i,first in enumerate(es):
        second=next(e for e in p['edges'] if e['from']==first['to'] and e['to']==join)
        c.text(65 if i==0 else 650,820,title_event(second),40)
    c.text(60,1110,'两条路线都可到达下方同一状态',44)
    c.text(60,1190,'非确定 ≠ 各占一半，也不保证公平',42)
    c.save(out)

    c = Sheet('05-deadlock', '两个发送者，凑不成一次会合', '原程序初始死锁及改序后真实两次会合')
    d=RUN['deadlock']; f=RUN['reordered']
    for col,name in enumerate(d['program']):
        x=70+col*520
        c.text(x,180,name+' 当前',50)
        c.box((x,265,x+400,365),GOLD)
        c.text(x+25,290,optext(d['program'][name][0]),48,box=(x,265,x+400,365),bg=GOLD)
        c.text(x,430,'后面才有 '+optext(d['program'][name][1]),42)
    c.text(65,550,f'可达状态 {d["state_count"]}；可执行转移 {d["edge_count"]}',46,color=RED)
    c.line((60,650,1005,650))
    c.text(65,700,'修复：B 改成先收后发',48)
    for i,e in enumerate(f['trace']):
        c.text(75,820+i*110,title_event(e),48)
        c.text(700,820+i*110,pcs(f['states'][e['to']]),42)
    c.text(65,1090,'改变协议顺序，比催促调度更有用',42)
    c.save(out)

    b=RUN['buffered']; ids=[0]+[e['to'] for e in b['trace']]
    c=Sheet('06-buffer','一格缓冲：发送完成的含义改变了','实际入队与出队分开，显示每条有向通道的占用')
    c.text(45,175,'动作 / 状态',42);c.text(500,175,'A → B',42);c.text(795,175,'B → A',42)
    for i,sid in enumerate(ids):
        y=275+i*190;s=b['states'][sid]
        label='开始' if i==0 else b['trace'][i-1]['label']
        c.text(45,y,label,40);c.text(45,y+65,pcs(s),40)
        for j,ch in enumerate(s['queues']):
            x=500+j*295;box=(x,y-5,x+215,y+110);fill=GOLD if s['queues'][ch] else LIGHT
            c.box(box,fill)
            c.text(x+35,y+25,str(s['queues'][ch][0]) if s['queues'][ch] else '空',48,box=box,bg=fill)
    c.text(45,275+len(ids)*190,'put = 入队；take = 出队；一格一个值',40)
    c.save(out)

    b=RUN['burst']; s=b['states'][b['deadlocks'][0]]
    c=Sheet('07-burst','一格缓冲，也会被协议填死','从两次真实入队抵达双满队列死锁，保留尚未执行的接收')
    for i,e in enumerate(b['trace']): c.text(65,180+i*85,e['label'],46)
    y=435
    for j,(ch,q) in enumerate(s['queues'].items()):
        x=70+j*510;box=(x,y,x+400,y+140);c.box(box,GOLD)
        c.text(x+30,y+30,ch+' = '+str(q),44,box=box,bg=GOLD)
    for j,name in enumerate(b['program']):
        x=70+j*510;i=s['pc'][name]
        c.text(x,650,name+' 当前 '+optext(b['program'][name][i]),44,color=RED)
        c.text(x,750,'接收仍排在后面',42)
    c.text(65,890,f'容量 {b["capacity"]}，两个方向都已满',46)
    c.text(65,980,f'穷举 {b["state_count"]} 个状态，发现 {len(b["deadlocks"])} 个死锁',42)
    c.save(out)
    c=Sheet('10-matching','不是任意一发一收都能配对','从流水线真实初始状态辨认互指名称与尚未就绪的下游通信')
    s=p['states'][0]
    for i,name in enumerate(p['program']):
        y=180+i*230;box=(65,y,995,y+140);c.box(box)
        c.text(95,y+35,name+' 当前：'+optext(p['program'][name][s['pc'][name]]),50,box=box,bg=LIGHT)
        if i<2:
            c.arrow((900,y+150),(900,y+210),BLUE if i==0 else RED)
            if i==1:c.line((878,y+175,922,y+175),RED,7)
            c.text(95,y+166,'P 与 M：互相指定，整数可接收' if i==0 else 'M 与 C：M 当前尚未向 C 发送',40)
    c.text(65,940,'C 已经等着，也不能提前拿到结果',44)
    c.save(out)
    old=HERE/'figure-metadata.json'
    if old.exists():
        META.extend(x for x in json.loads(old.read_text()) if x.get('identity','').startswith('真实浏览器'))
    (out.parent/'examples'/'figure-metadata.json').parent.mkdir(parents=True,exist_ok=True)
    (out.parent/'examples'/'figure-metadata.json').write_text(json.dumps(META,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=HERE.parent/'assets')
    main(ap.parse_args().out)
