"""Original finite-difference figures, CC BY 4.0; generator code CC0-1.0.
Canvas validation API adapted from this repository's r1 Quickselect (originally Aho-Corasick) generator.
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


def cells(c,vals,y,labels=False):
 for j,v in enumerate(vals):
  x=60+j*250
  if labels:c.text(x+30,y,['数值','一阶差','二阶差','三阶差'][j],40)
  c.card(x,y+(65 if labels else 0),230,80,str(v),fill=['#dceee6','#e5eef7','#fff0df','#e7e1f5'][j])

def finish(c,name,purpose):c.save(name,purpose)

c=Canvas('Babbage 差分机：把乘法移出循环')
c.text(60,145,'一张数表，一套固定的加法',52)
c.text(60,255,'y(n) = '+DATA['polynomial'],54,BLUE)
cells(c,DATA['initial'],375,True)
c.arrow((530,550),(530,640))
cells(c,DATA['states'][1],690)
c.text(60,840,'每格加右邻的旧值；最右保持',46,GREEN)
c.text(60,935,'离散数值教学模型，非机械复原',40)
finish(c,'00-cover.png','封面：展示从多项式到固定状态递推的中心问题')

c=Canvas('起步：先把几个数真正算出来')
for i,r in enumerate(DATA['direct']):
 y=140+i*190
 c.text(60,y,f"n = {r['n']}：{r['n']} × {r['n']} × {r['n']} = {r['cube']}",46)
 c.text(100,y+85,f"{r['cube']} + {r['linear']} + {r['constant']} = {r['value']}",48,GREEN)
finish(c,'01-direct.png','展开初值乘算，避免差分表输入凭空出现')

c=Canvas('差分：下一项减这一项，写在这一行')
heads=['n','y','一阶差','二阶差','三阶差']
xs=[55,200,400,620,840]
for x,h in zip(xs,heads):c.text(x,135,h,40)
for i in range(7):
 y=220+i*105
 c.text(xs[0],y,str(DATA['n'][i]),42)
 for j in range(4):
  v=DATA['columns'][j][i]
  if j==3:c.d.rounded_rectangle((xs[j+1]-12,y-5,1012,y+70),radius=10,fill='#e7e1f5')
  c.text(xs[j+1],y,str(v),46)
c.text(55,1020,f"例如：{DATA['values'][2]} − {DATA['values'][1]} = {DATA['columns'][1][1]}，写在 n = {DATA['n'][1]} 行",42)
c.text(55,1110,'紫列恒定；右列是左列相邻两项之差',40)
finish(c,'02-table.png','明确前向差分的行位置，显示完整可续算状态')

c=Canvas('一次推进：先低阶，再高阶')
for j,h in enumerate(['数值','一阶差','二阶差','三阶差']):c.text(90+j*250,125,h,40)
for i,state in enumerate(DATA['stages']):
 y=215+i*235
 label='起始：所有格都在 n = 0' if i==0 else f"写回第 {i} 格：用右邻尚未更新的值"
 c.text(60,y,label,40)
 cells(c,state,y+75)
 if i<3:c.arrow((530,y+170),(530,y+220))
c.text(60,1200,'最后一行是 n = 1 的完整新状态',44,GREEN)
finish(c,'03-update.png','逐写回状态说明为什么旧右邻仍可用')

c=Canvas('同样初值，反向写回会算错')
cells(c,DATA['initial'],145,True)
for i,state in enumerate(DATA['wrong_stages'][1:]):
 y=400+i*155
 cells(c,state,y)
 c.text(60,y+85,['先把三阶差加进二阶差','再把新的二阶差加进一阶差','最后把新的一阶差加进数值'][i],40,ORANGE)
c.text(60,935,f"错误首项 {DATA['wrong_stages'][-1][0]} ≠ 正确 {DATA['states'][1][0]}",48,ORANGE)
c.text(60,1030,'错在取错时刻，不是加法本身出错',44)
finish(c,'04-order.png','反例展示混用新旧值造成第一步错误')

c=Canvas('把一个整数展开成多个数位')
r=DATA['states'][4]
for j,value in enumerate(r):
 x=160+j*220
 c.text(x,140,['数值','一阶差','二阶差','三阶差'][j],40)
 digits=list(f'{value:03d}')
 for i,digit in enumerate(digits):c.card(x+20,230+i*120,110,85,digit,fill=['#dceee6','#e5eef7','#fff0df','#e7e1f5'][j])
 c.text(x+20,640,str(value),44)
for i,l in enumerate(['百位','十位','个位']):c.text(45,240+i*120,l,40)
c.text(60,790,'每一列保存一个完整整数',46)
c.text(60,885,'每一个有色小格只保存一个数位',44)
c.text(60,1070,'教学存储图；不画真实齿轮、轴与传动',40)
finish(c,'05-registers.png','把数学状态格与十进制各数位分开，明确非实机布局')

r=DATA['carry'];c=Canvas(f"一次加法：{r['a']:03d} + {r['b']:03d}")
for i,e in enumerate(r['events']):
 y=150+i*265
 c.text(60,y,['个位','十位','百位'][i],46,BLUE)
 c.text(250,y,f"{e['a']} + {e['b']} + {e['incoming']} = {e['total']}",48)
 c.text(250,y+85,f"写 {e['digit']}，向高位进 {e['outgoing']}",46,GREEN)
 if i<2:c.arrow((130,y+85),(130,y+220))
c.text(60,1010,f"读回三位：{r['value']:03d}",52,GREEN)
c.text(60,1105,'数学进位轨迹；不是历史装置的动作时序',40)
finish(c,'06-carry.png','从同一多项式73+63分解实际计算得到的逐位进位')

c=Canvas('把最高差分多设一，误差会积累')
xs=[60,210,440,700]
for x,h in zip(xs,['n','正确值','错误值','误差']):c.text(x,145,h,42)
for i,s in enumerate(DATA['bad_states']):
 y=235+i*90
 for x,v in zip(xs,[i,DATA['values'][i],s[0],DATA['errors'][i]]):c.text(x,y,str(v),44,ORANGE if x==700 else INK)
c.text(60,1010,'前三项看似正确，不能证明后面也正确',44)
finish(c,'07-errors.png','展示初值误差逐阶向左传播，不宣称有限测试证明')

r=DATA['overflow'];c=Canvas('有限位宽：数学正确，容器仍可能装不下')
c.text(60,145,f"本例 n = 9 的三位数：{r['a']:03d}",46)
c.text(60,245,f"再加一阶差：{r['b']:03d}",46)
c.text(60,365,f"完整整数结果：{r['a']+r['b']}",52,GREEN)
for i,d in enumerate(f"{r['a']+r['b']:04d}"):
 c.card(60+i*245,500,220,115,d,fill='#ffd8c9' if i==0 else '#e5eef7')
c.text(60,690,'橙格超出本教学容器的三个数位',44,ORANGE)
c.text(60,790,f"只留低三位，会变成 {r['value']:03d}",48,ORANGE)
c.text(60,900,'这里的三位截断仅为反例，非原机规则',40)
finish(c,'08-overflow.png','可见被截掉的高位；区别整数递推与有限容器')

c=Canvas('步长变了，初值也必须重算')
for j,(label,table) in enumerate([('每次 n 加 1',DATA['columns']),('每次 n 加 2',DATA['step2'])]):
 y=150+j*310;c.text(60,y,label,48)
 cells(c,[d[0] for d in table[:4]],y+100,True)
c.text(60,840,'同一多项式，不同采样间隔',46)
c.text(60,940,'阶数仍相同，最高差分不再相同',44)
finish(c,'09-step.png','同一多项式改变步长后，初始状态和三阶差都改变')

c=Canvas('边界：不是所有数列都会差到常数')
xs=[60,280,530,780]
for x,h in zip(xs,['2 的 n 次方','一阶差','二阶差','三阶差']):c.text(x,145,h,40)
for i in range(4):
 for j in range(4):c.text(xs[j],245+i*120,str(DATA['nonpoly'][j][i]),48)
c.text(60,800,'各列仍在翻倍；三阶差没有固定下来',44)
c.text(60,910,'有限阶差分机不能这样精确续完整数列',40)
finish(c,'10-boundary.png','指数数列对照说明恒定高阶差分的适用范围')

(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(f'{len(meta)} figures; geometry, glyph, ink, contrast, dimensions checked.')
