"""Original figures, CC BY 4.0; generator code CC0-1.0."""
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

c=Canvas('Aho–Corasick 多模式匹配')
c.text(50,135,'许多关键词，共享一次向前阅读',48)
for i,p in enumerate(DATA['patterns']):c.card(65+i*245,245,200,95,p)
c.arrow((530,365),(530,430))
c.card(220,455,620,100,'共享前缀 + 保留后缀')
c.arrow((530,580),(530,645))
c.card(220,670,620,95,DATA['text'])
c.text(100,820,'找出全部重叠命中，文本不回头')
c.save('00-cover.png','独立封面：呈现词表、共享机器与文本的关系')

c=Canvas('字典树：从左向右，每条边添一字')
pos={'根':(80,390),'h':(290,250),'he':(500,165),'her':(710,165),'hers':(920,165),'hi':(500,335),'his':(710,335),'s':(290,560),'sh':(500,560),'she':(710,560)}
for s,(x,y) in pos.items():
 if s=='根':continue
 p=s[:-1] or '根';px,py=pos[p];c.arrow((px+68,py),(x-68,y))
for s,(x,y) in pos.items():c.card(x-65,y-45,130,90,s,fill=GREEN if s in DATA['patterns'] else '#e5eef7',color='white' if s in DATA['patterns'] else INK)
c.text(65,675,'深色：完整词；浅色：仍可继续的前缀')
c.text(65,750,'框内是路径全名；根代表空串')
c.save('01-trie.png','呈现共享前缀、终止节点与继续延伸的区别')

c=Canvas('失败指针：保留最长可用真后缀')
c.text(65,130,'she 的候选后缀：he、e、空串')
c.card(80,240,250,90,'she');c.card(650,240,250,90,'he',fill='#dceee6')
c.arrow((350,285),(625,285),ORANGE,True)
c.text(350,350,'失败：不读新字符',40,ORANGE)
c.text(65,460,'he 能接 r，于是进入 her')
c.card(80,560,250,90,'he');c.card(650,560,250,90,'her')
c.arrow((350,605),(625,605));c.text(470,650,'读 r',42,BLUE)
c.text(65,760,'另一条退路：sh 的可用后缀是 h')
c.card(80,860,250,90,'sh');c.card(650,860,250,90,'h',fill='#dceee6')
c.arrow((350,905),(625,905),ORANGE,True)
c.text(65,1020,'橙色虚线保留后缀；蓝色实线读字符')
c.save('02-failure.png','展示失配时状态缩短与继续消费同一字符')

c=Canvas('真实运行：每行消费一个字符')
c.text(65,140,'位置 / 字符');c.text(420,140,'到达状态');c.text(735,140,'新输出')
for j,row in enumerate(DATA['trace']):
 y=240+j*100
 if row['fallback']:c.d.rounded_rectangle((40,y-5,1020,y+80),radius=10,fill='#fff0df')
 c.text(65,y,f"{row['i']} / {row['ch']}");c.text(440,y,row['state']);c.text(735,y,', '.join(h[0] for h in row['hits']) or '无')
c.text(65,1180,'橙色行：先走失败指针，再读本字符')
c.save('03-trace.png','从模型输出逐字符核对状态、失败发生点及匹配结果')

c=Canvas('输出区间：右端不包含在匹配内')
x0=125;step=95
for i,ch in enumerate(DATA['text']):
 x=x0+i*step;c.d.rectangle((x,170,x+step,255),outline=BLUE,width=3);c.text(x+30,180,ch)
for i in range(len(DATA['text'])+1):c.text(x0+i*step-12,280,str(i),40)
for j,(p,a,b) in enumerate(DATA['hits']):
 y=390+j*155;c.d.rounded_rectangle((x0+a*step,y,x0+b*step,y+70),radius=10,fill='#dceee6' if j%2 else '#e5eef7')
 c.text(x0+a*step+12,y+5,p)
 c.text(65,y+80,f'{p}  [{a},{b})',40)
c.text(65,1060,'字符格、端点与彩带共用横向尺度')
c.save('04-overlap.png','把同尾输出与重叠输出落实到准确半开区间')

c=Canvas('流式处理：块结束，记忆不断')
split=3
c.card(180,150,700,100,'第一块：'+DATA['text'][:split]);c.arrow((530,280),(530,350))
c.card(180,380,700,100,'保留状态：'+DATA['trace'][split-1]['state'],fill='#dceee6')
c.text(180,525,f'全局已读字符数：{split}')
c.arrow((530,620),(530,690));c.card(180,720,700,100,'第二块：'+DATA['text'][split:])
c.text(90,880,'首个 e 继续走：sh 到 she')
c.text(90,960,'立即输出 she 与 he，位置沿用全局')
c.save('05-stream.png','说明块间保留状态与绝对偏移，避免跨块关键词丢失')
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'figures':len(meta),'all_geometry_checks':'PASS'},ensure_ascii=False))
