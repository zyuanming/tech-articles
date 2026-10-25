#!/usr/bin/env python3
# Original code and layout: CC0-1.0. Output illustrations: CC BY 4.0.
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
R = json.loads((HERE/'results.json').read_text())
V = R['values']
FONT = Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
MONO = Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
assert FONT.exists() and MONO.exists(), 'Required Chinese and mono fonts missing'
CMAPS = {str(p): TTFont(str(p), fontNumber=0).getBestCmap() for p in [FONT, MONO]}
INK = '#182b3d'
BG = '#f7f4eb'
BLUE = '#12637a'
TEAL = '#dbeee9'
GOLD = '#f4df9b'
RED = '#873f3f'
META = []

def luminance(color):
    x = [int(color[i:i+2],16)/255 for i in (1,3,5)]
    x = [v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in x]
    return .2126*x[0]+.7152*x[1]+.0722*x[2]

class Canvas:
    def __init__(self, name, title, purpose):
        self.name, self.purpose = name, purpose
        self.im = Image.new('RGB',(1062,5000),BG)
        self.d = ImageDraw.Draw(self.im)
        self.texts, self.last = [], 0
        self.text(48,38,title,52)
        self.line((48,120,1014,120), BLUE, 5)
    def text(self,x,y,s,size=44,color=INK,mono=False,box=None,bg=BG):
        p = MONO if mono else FONT
        assert all(ord(c) in CMAPS[str(p)] for c in s), (self.name,s)
        f = ImageFont.truetype(str(p),size)
        b = self.d.textbbox((x,y),s,font=f,anchor='lt')
        assert size>=40 and b[0]>=32 and b[2]<=1030, (self.name,s,b)
        if box:
            assert b[0]>=box[0]+8 and b[1]>=box[1]+8 and b[2]<=box[2]-8 and b[3]<=box[3]-8,(s,b,box)
        for t in self.texts:
            a=t['bbox']
            assert not (b[0]<a[2] and b[2]>a[0] and b[1]<a[3] and b[3]>a[1]),(self.name,s,t['text'])
        l1,l2=sorted([luminance(color),luminance(bg)])
        contrast=(l2+.05)/(l1+.05)
        assert contrast>=4.5,(s,contrast)
        self.d.text((x,y),s,font=f,fill=color,anchor='lt')
        crop=self.im.crop(b)
        assert len(set(crop.getdata()))>1,s
        self.texts.append({'text':s,'bbox':b,'font':str(p),'size':size,'contrast':round(contrast,2)})
        self.last=max(self.last,b[3])
    def rect(self,b,fill=TEAL,outline=BLUE,width=3):
        self.d.rounded_rectangle(b,18,fill,outline,width)
        self.last=max(self.last,b[3])
    def line(self,xy,color=BLUE,width=5):
        self.d.line(xy,fill=color,width=width)
        self.last=max(self.last,max(xy[1::2]))
    def arrow(self,x1,y1,x2,y2,color=BLUE):
        import math
        self.line((x1,y1,x2,y2),color)
        a=math.atan2(y2-y1,x2-x1)
        p=[(x2,y2),(x2-19*math.cos(a-.5),y2-19*math.sin(a-.5)),(x2-19*math.cos(a+.5),y2-19*math.sin(a+.5))]
        self.d.polygon(p,fill=color)
    def code(self,y,s,size=48):
        self.text(60,y,s,size,mono=True)
    def note(self,y,s):
        self.text(60,y,s,42)
    def save(self,out):
        h=int(self.last+48)
        self.im=self.im.crop((0,0,1062,h))
        assert all(t['bbox'][3]<h-20 for t in self.texts)
        self.im.save(out/(self.name+'.png'))
        META.append({'file':'assets/'+self.name+'.png','width':1062,'height':h,
          'minimum_font_px':min(t['size'] for t in self.texts),
          'mobile_width':354,'effective_minimum_px':min(t['size'] for t in self.texts)/3,
          'identity':'原创教学示意；数值来自实际C11程序','license':'CC-BY-4.0',
          'purpose':self.purpose,'text_audit':self.texts,
          'checks':['cmap','bounds','declared-box','text-overlap','font-size','contrast','ink','dynamic-crop'],
          'data':'examples/results.json','geometry':'样本格数/指针目标/比例条由values计算；其余为排版坐标，不表示物理地址'})

def cells(c, values, y, x=66, w=290, h=100, prefix=None):
    for i,v in enumerate(values):
        b=(x+i*w,y,x+(i+1)*w-10,y+h)
        c.rect(b, GOLD if i==1 else TEAL)
        c.text(x+i*w+35,y+22,str(v),50,box=b,bg=GOLD if i==1 else TEAL)
        if prefix is not None: c.text(x+i*w+35,y+h+14,f'{prefix}[{i}]',40,mono=True)


def build(out):
    out.mkdir(parents=True,exist_ok=True)
    n=V['sample_count']
    c=Canvas('00-cover','C 声明：名字外面是什么？','独立封面：以括号引出指针与数组的组合')
    c.code(170,f'int *p[{n}];',64)
    c.text(70,280,'先是一排指针',48)
    c.line((70,365,990,365),BLUE,3)
    c.code(410,f'int (*p)[{n}];',64)
    c.text(70,520,'先是指向整排的指针',48)
    c.rect((66,620,996,760),TEAL)
    c.text(95,655,'从怎样使用，读回怎样声明',46,box=(66,620,996,760),bg=TEAL)
    c.save(out)

    c=Canvas('01-object','先找到要读的那个值','定义数组、下标、元素地址与解引用')
    c.code(165,f'int samples[{n}] = {{'+','.join(map(str,V['samples']))+'};',44)
    cells(c,V['samples'],280,prefix='s')
    c.note(455,'图中 s 代表 samples；下标从 0 开始')
    c.rect((66,560,436,660),GOLD)
    c.text(95,585,'p：元素地址',44,box=(66,560,436,660),bg=GOLD)
    c.arrow(465,610,790,610)
    c.text(820,585,str(V['samples'][0]),50)
    c.code(730,'int *p = &samples[0];',46)
    c.code(815,f'*p = {V["samples"][0]}    p[1] = {V["p_next_value"]}',46)
    c.note(915,'箭头表示指向关系，不是额外复制值')
    c.save(out)

    c=Canvas('02-build','反过来：由取样动作构造声明','从整行指针的使用逐步回推声明')
    stages=[('row','先拿到指向一整行的指针'),('(*row)','解引用，得到整行'),('(*row)[1]',f'再取下标 1，读到 {V["row_second"]}')]
    for i,(a,b) in enumerate(stages):
        y=170+i*210
        c.code(y,a,60)
        c.note(y+80,b)
        if i<len(stages)-1:c.arrow(905,y+120,905,y+190)
    c.line((60,790,1000,790),BLUE,3)
    c.code(845,f'int (*row)[{n}];',58)
    c.note(945,'把使用中的下标换成声明中的长度')
    c.note(1015,'星号与括号的结构留下，前面写 int')
    c.save(out)

    c=Canvas('03-binding','同一组符号，两棵结合结构','比较下标先结合与括号强制先解引用')
    for i,(expr,top,bottom) in enumerate([('int *links[3];','links → 数组','每个元素 → 指针 → int'),('int (*row)[3];','row → 指针','所指对象 → 数组 → int')]):
        y=170+i*430
        c.code(y,expr,58)
        c.rect((100,y+105,965,y+205),TEAL)
        c.text(125,y+130,top,46,box=(100,y+105,965,y+205),bg=TEAL)
        c.arrow(532,y+215,532,y+265)
        c.text(125,y+290,bottom,46)
    c.note(1050,'[]、调用 () 比前缀 * 结合更紧')
    c.note(1120,'分组括号把 (*row) 先包成一个整体')
    c.save(out)

    c=Canvas('04-links','指针数组：每格可以指向不同位置','实际links重排同一批样本的访问顺序')
    c.code(165,f'int *links[{n}];',56)
    # Side by side columns; each arrow has an isolated route between labels.
    c.text(70,265,'指针格',46);c.text(700,265,'samples',46,mono=True)
    ys=[390+i*200 for i in range(n)]
    for i,y in enumerate(ys):
        c.rect((60,y-15,370,y+90),GOLD)
        c.text(82,y+8,f'links[{i}]',42,mono=True,box=(60,y-15,370,y+90),bg=GOLD)
        c.rect((695,y-15,1000,y+90),TEAL)
        c.text(723,y+8,f'[{i}] {V["samples"][i]}',46,mono=True,box=(695,y-15,1000,y+90),bg=TEAL)
    for i,target in enumerate(V['links_indices']):
        c.arrow(385,ys[i]+37,680,ys[target]+37)
    c.code(1035,f'*links[0] = {V["links_values"][0]}',52)
    c.note(1135,'左列存地址；右列才存采样整数')
    c.save(out)

    c=Canvas('05-row','数组指针：一个指针，指向整行','指针变量与所指数组大小分开')
    c.code(165,f'int (*row)[{n}] = &samples;',44)
    c.rect((65,285,995,430),GOLD)
    c.text(100,320,f'row 指针本身：{V["row_pointer_bytes"]} 字节',46,box=(65,285,995,430),bg=GOLD)
    c.arrow(532,445,532,540)
    c.rect((50,560,1010,805),TEAL)
    cells(c,V['samples'],600,x=70)
    c.text(90,735,f'*row 整行：{V["row_bytes"]} 字节',44,box=(50,560,1010,805),bg=TEAL)
    c.code(865,f'(*row)[1] = {V["row_second"]}',54)
    c.note(965,'字节数为本次 Linux x86_64 实测')
    c.note(1035,'格子等宽表示同类元素，不表示地址值')
    c.save(out)

    c=Canvas('06-steps','加一，究竟跨过多大对象？','同一数组中两种指针的合法步进及目标')
    c.note(150,'二维 grid：两行，每行三个 int')
    vals=[v for row in V['grid'] for v in row]
    x0=66; unit=150
    for i,v in enumerate(vals):
        c.rect((x0+i*unit,300,x0+(i+1)*unit-6,405),GOLD if i==1 else TEAL)
        c.text(x0+i*unit+30,325,str(v),46,bg=GOLD if i==1 else TEAL)
    c.text(75,220,'第 0 行',42);c.text(525,220,'第 1 行',42)
    pixels_per_byte=unit/V['int_bytes']
    lengths=[V['element_step_bytes']*pixels_per_byte,V['rows_step_bytes']*pixels_per_byte]
    assert lengths[0]<lengths[1]
    c.arrow(x0,465,x0+lengths[0],465)
    c.text(65,510,f'element：一步 {V["element_step_bytes"]} 字节',44)
    c.arrow(x0,650,x0+lengths[1],650)
    c.text(65,700,f'rows：一步 {V["rows_step_bytes"]} 字节',44)
    c.note(810,f'从起点加一：分别到 {V["element_next_value"]} 与下一行')
    c.note(880,f'下一行的首个整数为 {V["rows_next_first"]}')
    c.code(975,'element = grid[0];',42)
    c.code(1045,'rows = grid;',42)
    c.note(1130,'长度共用字节比例；不越出各自数组')
    c.save(out)

    c=Canvas('07-functions','函数返回指针；指针指向函数','明确函数与函数指针两条不同使用链')
    c.code(165,'int *pick(int i);',52)
    c.text(65,265,'pick(1)：先调用函数',44)
    c.arrow(100,335,100,390)
    c.text(65,425,'得到 samples[1] 的地址',44)
    c.arrow(100,495,100,550)
    c.text(65,585,f'*pick(1)：沿地址读到 {V["pick_value"]}',44)
    c.line((60,685,1000,685),BLUE,3)
    c.code(745,'int (*value)(int);',52)
    c.text(65,845,'value：先拿到函数指针',44)
    c.arrow(100,915,100,970)
    c.text(65,1005,'(*value)(1)：调用所指函数',44)
    c.arrow(100,1075,100,1130)
    c.text(65,1165,f'返回 int；此例得到 {V["value_pointer_result"]}',44)
    c.save(out)

    c=Canvas('07b-reader-type','从 reader 向外：四层类型','复杂声明的类型组合层次，与调用执行链区分')
    c.code(165,'int *(*reader)(int);',48)
    layers=[('reader','这个名字代表一个指针'),('(*reader)','所指的是接收 int 的函数'),('(*reader)(int)','该函数返回一个指针'),('int','返回指针的目标是整数')]
    for i,(a,b) in enumerate(layers):
        y=300+i*230
        c.rect((60,y,1000,y+170),TEAL)
        c.text(85,y+22,a,48,mono=True,box=(60,y,1000,y+170),bg=TEAL)
        c.text(85,y+100,b,42,box=(60,y,1000,y+170),bg=TEAL)
        if i<len(layers)-1:c.arrow(940,y+180,940,y+218)
    c.note(1250,'这些是声明片段，不是运行次序')
    c.save(out)

    c=Canvas('08-reader','把两种能力接起来：reader','函数指针返回数据指针的实际调用过程')
    c.code(165,'int *(*reader)(int);',48)
    c.code(245,'reader = pick;',48)
    steps=[('reader','选中 pick 函数'),('(*reader)(1)','调用它，传入下标 1'),('samples + 1','返回采样元素的地址'),('*(*reader)(1)',f'解引用，结果 {V["reader_value"]}')]
    for i,(a,b) in enumerate(steps):
        y=365+i*210
        c.rect((60,y,1000,y+165),GOLD if i==3 else TEAL)
        c.text(85,y+20,a,48,mono=True,box=(60,y,1000,y+165),bg=GOLD if i==3 else TEAL)
        c.text(85,y+95,b,42,box=(60,y,1000,y+165),bg=GOLD if i==3 else TEAL)
        if i<len(steps)-1:c.arrow(945,y+175,945,y+200)
    c.save(out)

    c=Canvas('09-sizes','sizeof：问的是哪一个对象？','共轴实测尺寸比较，避免把数组等同指针')
    rows=[('samples 整个数组',V['array_bytes']),('p 指针变量',V['pointer_bytes']),('links 指针数组',V['links_bytes']),('*row 所指整行',V['row_bytes']),('参数 a 调整后',V['param_bytes'])]
    maxv=max(v for _,v in rows); scale=850/maxv
    lengths=[]
    for i,(label,v) in enumerate(rows):
        y=175+i*185
        c.text(65,y,f'{label}：{v} B',44)
        length=v*scale;lengths.append(length)
        c.rect((65,y+70,65+length,y+120),TEAL)
    assert sorted(range(len(rows)),key=lambda i:rows[i][1])==sorted(range(len(rows)),key=lambda i:lengths[i])
    c.note(1140,'B 表示字节；各条从同一起点量起')
    c.note(1210,'仅报告本次 GCC / x86_64 结果')
    c.save(out)

    c=Canvas('10-parameters','参数调整：只调整最外一层','区分数组表达式转换与参数声明调整并保留行宽')
    c.text(60,165,'在 param_size 调用中，只转换实参',42)
    c.code(245,'samples',48)
    c.arrow(130,315,130,370)
    c.code(405,'&samples[0]',48)
    c.line((60,505,1000,505),BLUE,3)
    c.text(60,565,'函数参数声明：数组写法调整为指针',42)
    c.code(650,'int a[3]  →  int *a',44)
    c.code(750,'int a[2][3]',48)
    c.arrow(130,820,130,875)
    c.code(910,'int (*a)[3]',48)
    c.note(1020,'外层调整后，内层仍是一行三个 int')
    c.note(1090,f'所以 sizeof *a 仍为 {V["grid_param_row_bytes"]} 字节')
    c.save(out)

    c=Canvas('11-typedef','typedef：给已经形成的类型命名','给复杂类型起名并展示限定符附着层级')
    c.code(170,'typedef int Row[3];',46)
    c.code(255,'Row *row;',46)
    c.text(65,335,'Row 是整行；row 指向整行',44)
    c.line((60,430,1000,430),BLUE,3)
    c.code(485,'typedef int *Reader(int);',44)
    c.code(570,'Reader *reader;',46)
    c.text(65,650,'Reader 是函数类型；reader 是指针',42)
    c.line((60,745,1000,745),BLUE,3)
    c.code(800,'typedef int *IntPtr;',46)
    c.code(885,'const IntPtr p = samples;',44)
    c.rect((60,980,1000,1140),GOLD)
    c.text(85,1005,'固定的是指针 p；目标仍可改',44,box=(60,980,1000,1140),bg=GOLD)
    c.text(85,1070,f'*p = {V["const_pointer_write"]} 合法；p = p+1 被拒',42,box=(60,980,1000,1140),bg=GOLD)
    c.save(out)
    return META

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); meta=build(a.out)
    (a.out/'figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    print(f'Built and checked {len(meta)} original figures')
