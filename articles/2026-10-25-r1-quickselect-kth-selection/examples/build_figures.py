"""Original Quickselect figures, CC BY 4.0; generator code CC0-1.0.
Canvas validation API adapted from this repository's r1 Aho-Corasick generator.
All figure compositions below are new.
"""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'examples/results.json').read_text())
CANDIDATES=['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc']
FONT=next((p for p in CANDIDATES if Path(p).exists()),None)
if not FONT:raise RuntimeError('Chinese font not found')
CMAP=TTFont(FONT,fontNumber=0).getBestCmap()
BG='#f8fafc'; INK='#142d42'; BLUE='#176297'; GREEN='#166c57'; ORANGE='#9c4d0d'
meta=[]
class Canvas:
 def __init__(self,title):
  self.im=Image.new('RGB',(1062,4000),BG);self.d=ImageDraw.Draw(self.im);self.boxes=[];self.bottom=0
  self.text(50,30,title,48)
 def text(self,x,y,s,size=42,color=INK,box=None):
  assert size>=40
  assert all(ord(c) in CMAP for c in s if not c.isspace()),s
  f=ImageFont.truetype(FONT,size);b=self.d.textbbox((x,y),s,font=f)
  assert b[0]>=0 and b[1]>=0 and b[2]<=1062 and b[3]<=4000,(s,b)
  if box:assert box[0]+5<=b[0] and box[1]+5<=b[1] and b[2]<=box[2]-5 and b[3]<=box[3]-5,(s,b,box)
  for old in self.boxes:
   q=old[0]
   assert min(b[2],q[2])<=max(b[0],q[0]) or min(b[3],q[3])<=max(b[1],q[1]),(s,old[1])
  self.d.text((x,y),s,font=f,fill=color);self.boxes.append((b,s,size));self.bottom=max(self.bottom,b[3])
  px=self.im.crop(b).convert('L');lo,hi=px.getextrema();assert hi-lo>90,(s,lo,hi)
  assert sum(1 for v in px.getdata() if v<180)>len(s)*8,s
 def line(self,a,b,color=BLUE,dashed=False):
  if dashed:
   dx=b[0]-a[0];dy=b[1]-a[1];n=max(1,int(math.hypot(dx,dy)/18))
   for i in range(0,n,2):self.d.line((a[0]+dx*i/n,a[1]+dy*i/n,a[0]+dx*min(i+1,n)/n,a[1]+dy*min(i+1,n)/n),fill=color,width=5)
  else:self.d.line((*a,*b),fill=color,width=5)
  self.bottom=max(self.bottom,a[1],b[1])
 def arrow(self,a,b,color=BLUE,dashed=False):
  self.line(a,b,color,dashed);ang=math.atan2(b[1]-a[1],b[0]-a[0]);pts=[b]
  for delta in [-.55,.55]:pts.append((b[0]-20*math.cos(ang+delta),b[1]-20*math.sin(ang+delta)))
  self.d.polygon(pts,fill=color)
 def card(self,x,y,w,h,s,fill='#e5eef7',color=INK):
  b=(x,y,x+w,y+h);self.d.rounded_rectangle(b,radius=16,fill=fill)
  f=ImageFont.truetype(FONT,42);width=self.d.textlength(s,font=f)
  self.text(x+(w-width)/2,y+(h-60)/2,s,42,color,b);self.bottom=max(self.bottom,y+h)
 def save(self,name,purpose):
  im=self.im.crop((0,0,1062,math.ceil(self.bottom+45)));p=ROOT/'assets'/name;im.save(p)
  assert Image.open(p).size==im.size
  meta.append(dict(file='assets/'+name,width=im.width,height=im.height,min_font_px=min(z[2] for z in self.boxes),effective_min_font_at_354=round(min(z[2] for z in self.boxes)/3,2),identity='原创教学示意；执行数值来自 results.json',purpose=purpose,checks=['canvas','declared-box','text-overlap','font-size','contrast','glyph-cmap','ink-pixels','actual-dimensions']))

PALE=['#dceee6','#fff0df','#e5eef7'];COL=[GREEN,ORANGE,BLUE]
def row(c,values,y,x=65,step=102,highlight=None):
 for i,v in enumerate(values):
  c.card(x+i*step,y,step-10,80,str(v),fill='#ffe1ae' if i==highlight else '#e5eef7')
def nums(values):return '  '.join(map(str,values))
def band(c,values,y,label,color_index):
 c.text(65,y,label,42,COL[color_index])
 row(c,values,y+70)

c=Canvas('Quickselect：只找一个排名')
c.text(65,135,f"目标：第 {DATA['k']} 小",52,ORANGE)
row(c,DATA['input'],245)
c.arrow((530,365),(530,440))
c.text(170,470,'按主元分组，只跟答案那一组',44)
for j,r in enumerate(DATA['main']['rows']):
 y=590+j*160
 c.text(65,y,f"剩 {len(r['a'])} 项",42)
 row(c,r['a'],y-5,330,75)
 if j<len(DATA['main']['rows'])-1:c.arrow((365,y+80),(365,y+140))
c.text(65,1100,f"答案 {DATA['main']['answer']}；其他位置不必排好",48,GREEN)
c.save('00-cover.png','独立封面：原数组与仅保留一侧的候选链')

c=Canvas('第几小：按值排队，每次出现都占位')
c.text(65,140,'输入顺序')
row(c,DATA['input'],215)
c.text(65,355,'排序核验（算法不必做这一步）')
row(c,DATA['sorted'],435,highlight=DATA['index'])
c.text(65,560,'序号从左到右，从第一项开始')
for i in range(len(DATA['input'])):c.text(90+i*102,650,str(i+1),40,ORANGE if i==DATA['index'] else INK)
c.text(65,770,f"第 {DATA['k']} 小 = {DATA['sorted'][DATA['index']]}",48,GREEN)
c.text(65,860,f"Python 对应索引：{DATA['k']} - 1 = {DATA['index']}")
c.save('01-rank.png','把原位置、排序后的序号和零起始索引区分开')

r=DATA['main']['rows'][0]
c=Canvas(f"一次分区：所有数都与主元 {r['p']} 比")
row(c,r['a'],145)
c.text(65,275,'按输入次序扫描；各组内部不排序')
for j,(key,sign) in enumerate([('less','<'),('equal','='),('greater','>')]):
 vals=r[key];y=390+j*230
 band(c,vals,y,f"{sign} {r['p']}：{len(vals)} 项",j)
c.text(65,1110,f"小组内：{nums(r['less'])}，仍然无序")
c.save('02-partition.png','呈现三路分区的实际数组、等值处理和组内无序')

c=Canvas('只保留答案所在组：局部排名会变')
for j,r in enumerate(DATA['main']['rows']):
 y=140+j*430
 c.text(65,y,f"当前 {nums(r['a'])}",42)
 c.text(65,y+80,f"求第 {r['k']} 小；主元 {r['p']}",44,ORANGE)
 for z,(key,label) in enumerate([('less','小于'),('equal','等于'),('greater','大于')]):
  x=65+z*330;c.text(x,y+170,label,40,COL[z])
  c.text(x,y+235,nums(r[key]) or '空',42,COL[z])
 if r['branch']=='greater':s=f"去大于组：{r['k']} - {r['L']} - {r['E']} = {r['next_k']}"
 elif r['branch']=='less':s=f"去小于组：仍找第 {r['next_k']} 小"
 else:s=f"落在等于组：返回 {r['p']}"
 c.text(65,y+325,s,44,GREEN)
c.save('03-shrink.png','完整跟踪三轮候选和进右侧时的排名重编号')

r=DATA['duplicate']['rows'][0]
c=Canvas('相等的值，占的是一段排名')
row(c,DATA['sorted'],150)
start=r['L'];end=start+r['E']
c.line((65+start*102,265),(65+end*102-10,265),ORANGE)
c.text(65,320,f"主元 {r['p']}；较小 {r['L']} 项，相等 {r['E']} 项")
c.text(65,410,f"第 {start+1} 至 {end} 小，都等于 {r['p']}",48,ORANGE)
c.text(65,550,'全相等输入：一次分区就可以结束')
row(c,DATA['all_equal']['rows'][0]['a'],635)
c.text(65,765,f"相等组收下 {len(DATA['all_equal']['rows'][0]['a'])} 项",44,GREEN)
c.text(65,855,'若仅移走一个主元，重复值仍留在下一轮')
c.save('04-duplicates.png','显示等值排名区间与只剔除一个主元的退化原因')

r=DATA['main']['rows'][0]
c=Canvas('这份教学代码：用额外列表换清楚')
c.text(65,140,'扫描时，当前列表仍然存在')
row(c,r['a'],220)
c.arrow((520,340),(520,405))
for j,key in enumerate(['less','equal','greater']):
 y=450+j*170
 c.text(65,y,{'less':'less','equal':'equal','greater':'greater'}[key],42,COL[j]);row(c,r[key],y,300,105)
c.text(65,1000,f"新列表共 {r['L']} + {r['E']} + {len(r['greater'])} = {len(r['a'])} 项")
c.text(65,1100,'循环进入下一轮，只继续处理选中的列表')
c.text(65,1190,'峰值额外空间 O(n)，不是原地分区')
c.save('05-memory.png','可见的输入与输出列表共存，约束实现的空间承诺')

c=Canvas('扫描工作量：每条横条是一轮')
c.text(65,135,'另换输入：连续整数，目标为最大值',40)
n=len(DATA['costs']['worst']['rows'][0]['a'])
c.text(65,210,f"两边都从 {n} 项开始；条长共用一根尺度",40)
scale=380/n
for j,(key,title) in enumerate([('balanced','理想主元'),('worst','总选最小值')]):
 x=65+j*520;c.text(x,305,title,42,COL[j])
 vals=[len(r['a']) for r in DATA['costs'][key]['rows']]
 lengths=[]
 for i,v in enumerate(vals):
  y=400+i*70;length=v*scale;lengths.append(length)
  c.d.rectangle((x,y,x+length,y+45),fill=PALE[j]);c.text(x+length+8,y-6,str(v),40)
 assert sorted(range(len(vals)),key=lambda i:vals[i])==sorted(range(len(vals)),key=lambda i:lengths[i])
 c.text(x,1580,f"累计 {sum(vals)} 次访问",42,COL[j])
c.text(65,1690,'这里只数分区访问；不是秒数或完整选主元成本',40)
c.save('06-work.png','同尺度逐轮工作条，揭示几何收缩与逐项剥离的面积差')

c=Canvas('随机主元：不必恰好选中间那个')
g=DATA['good_pivots'];half=g['n']//2
c.text(65,140,f"以 {g['n']} 个互异元素的排序名次为例")
for j in range(2):
 for i,r in enumerate(g['ranks'][j*half:(j+1)*half]):
  x=65+i*122;y=250+j*160
  c.card(x,y,110,85,str(r),fill='#dceee6' if r in g['good'] else '#e5eef7')
c.text(65,620,f"绿色：第 {g['good'][0]} 至 {g['good'][-1]} 名，共 {len(g['good'])} 个",44,GREEN)
c.text(65,715,f"抽中绿色的概率：{len(g['good'])}/{g['n']} = {len(g['good'])//math.gcd(len(g['good']),g['n'])}/{g['n']//math.gcd(len(g['good']),g['n'])}")
c.text(65,815,f"抽中绿色后，任一侧最多 {g['max_side']} 项")
c.text(65,915,'蓝色也可能成功；绿色提供保守保证')
c.save('07-random-pivot.png','按排序名次标出好主元集合，解释概率而非保证次次对半')

c=Canvas('要最小几项，阈值还不等于名单')
t=DATA['topk']
c.text(65,140,f"同一组数（排序核验），取最小 {t['k']} 项",40)
row(c,DATA['sorted'],225)
c.text(65,365,f"先找第 {t['k']} 小，阈值 = {t['threshold']}",44,ORANGE)
band(c,t['below'],480,'严格小于阈值：全部保留',0)
band(c,t['equal'],710,f"等于阈值：只还需要 {t['needed']} 项",1)
c.text(65,965,f"直接取 <= {t['threshold']}，会拿到 {len(t['below'])+len(t['equal'])} 项")
c.text(65,1060,'并列项选谁，需另定规则；展示有序还要排序')
c.save('08-topk.png','把重复值边界转化为top-k的精确数量与并列选择问题')

c=Canvas('分区不是瞬间搬完：逐项扫描')
c.text(65,135,'橙格：正在读取；右侧蓝格：尚未读取',40)
c.text(65,210,'左侧格子已处理；下方是本步追加后的组',40)
for j,index in enumerate([0,1,len(DATA['scan'])-1]):
 st=DATA['scan'][index];y=330+j*510
 c.text(65,y,f"读第 {index+1} 项：{st['value']} 进入"+{'less':'小于组','equal':'等于组','greater':'大于组'}[st['group']],44,ORANGE)
 row(c,DATA['input'],y+85,highlight=index)
 for z,(key,label) in enumerate([('less','小于'),('equal','等于'),('greater','大于')]):
  x=65+z*330;c.text(x,y+215,label,40,COL[z]);c.text(x,y+280,nums(st[key]) or '空',42,COL[z])
 c.text(65,y+370,f"尚未读取：{nums(st['unread']) if st['unread'] else '无'}",40)
 if j==1:c.text(65,y+445,'中间若干步略去；下段已累计其处理结果',40)
c.save('09-scan-steps.png','用真实逐项追加快照连接输入、当前读数、未读后缀和三个输出组')

c=Canvas('随机执行：样本范围比均值更宽')
c.text(65,135,'线：样本最小至最大；圆点：样本均值',40)
c.text(65,210,f"每种长度 {DATA['experiments'][0]['trials']} 次；种子 {DATA['sample_plot']['seed_start']} 至 {DATA['sample_plot']['seed_end']}",40)
c.text(65,285,'共用横轴：分区访问项数，不是时间',40)
x0=180;span=760;axismax=DATA['sample_plot']['axis_max']
c.line((x0,390),(x0+span,390),INK)
for v in DATA['sample_plot']['ticks']:
 x=x0+span*v/axismax;c.line((x,380),(x,405),INK);c.text(x-24,420,str(v),40)
lengths=[];ranges=[]
for j,r in enumerate(DATA['experiments']):
 y=535+j*220
 c.text(65,y,f"n = {r['n']}",42)
 low=x0+span*r['min_visits']/axismax;hi=x0+span*r['max_visits']/axismax;mu=x0+span*r['mean_visits']/axismax
 c.line((low,y+95),(hi,y+95),BLUE)
 c.line((low,y+80),(low,y+110),BLUE);c.line((hi,y+80),(hi,y+110),BLUE)
 c.d.ellipse((mu-9,y+86,mu+9,y+104),fill=ORANGE)
 c.text(65,y+135,f"范围 {r['min_visits']}–{r['max_visits']}；均值 {r['mean_visits']:.3f}",40)
 lengths.append(hi-low);ranges.append(r['max_visits']-r['min_visits'])
assert sorted(range(len(ranges)),key=lambda i:ranges[i])==sorted(range(len(lengths)),key=lambda i:lengths[i])
c.text(65,1685,'有限种子的观测极值，不是理论最坏界',40)
c.text(65,1760,'目标为下中位值；也不是置信区间',40)
c.save('10-sample-range.png','把既有实验的样本极值与均值共尺度展示，避免平均值被读成单次保证')

# Keep independently captured browser figure metadata when regenerating diagrams.
meta_path=ROOT/'examples/figure-metadata.json'
if meta_path.exists():
 meta.extend(row for row in json.loads(meta_path.read_text()) if row['file']=='assets/11-numpy-live.png')
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'figures':len(meta),'all_geometry_checks':'PASS'},ensure_ascii=False))
