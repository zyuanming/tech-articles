"""Original Karger figures, CC BY 4.0; generator code CC0-1.0.
Canvas validation API adapted from this repository's r1 Quickselect generator (CC0).
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

RED='#b13c37';GRAY='#67798a'
STEPS=DATA['exact']['steps']
FIRST=f"{STEPS['first_safe']}/{STEPS['first_total']}"
NEXT=f"{STEPS['next_safe']}/{STEPS['next_total']}"

def node(c,x,y,label,color=BLUE):
 w=max(110,len(label)*39+30);b=(x-w/2,y-48,x+w/2,y+48)
 c.d.rounded_rectangle(b,20,fill=BG,outline=color,width=5)
 f=ImageFont.truetype(FONT,42);tw=c.d.textlength(label,font=f)
 c.text(x-tw/2,y-32,label,42,color,b);c.bottom=max(c.bottom,y+48)

def curve(c,a,b,offset=0,color=BLUE):
 dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
 mx=(a[0]+b[0])/2-dy/length*offset;my=(a[1]+b[1])/2+dx/length*offset
 pts=[]
 for i in range(41):
  t=i/40;pts.append(((1-t)**2*a[0]+2*(1-t)*t*mx+t*t*b[0],(1-t)**2*a[1]+2*(1-t)*t*my+t*t*b[1]))
 c.d.line(pts,fill=color,width=7);c.bottom=max(c.bottom,max(y for x,y in pts))

def graph(c,positions,edges,red=(),nodes=None):
 counts={}
 for u,v in edges:counts[tuple(sorted((u,v)))]=counts.get(tuple(sorted((u,v))),0)+1
 seen={}
 for u,v in edges:
  key=tuple(sorted((u,v)));i=seen.get(key,0);seen[key]=i+1
  curve(c,positions[key[0]],positions[key[1]],(i-(counts[key]-1)/2)*70,RED if (u,v) in red or (v,u) in red else BLUE)
 for lab,(x,y) in positions.items():node(c,x,y,lab,RED if nodes and lab in nodes else BLUE)

def k4(c,y,left=None):
 pos={'A':(260,y),'B':(802,y),'C':(260,y+350),'D':(802,y+350)}
 edges=[tuple('ABCD'[x] for x in e) for e in DATA['edges']]
 red=[e for e in edges if left and ((e[0] in left)!=(e[1] in left))]
 graph(c,pos,edges,red)

def tri(c,y,protected=False):
 pos={'AB':(230,y),'C':(832,y),'D':(531,y+350)}
 edges=[('AB','C')]*DATA['after_ab']['multiplicities'][0]+[('AB','D')]*DATA['after_ab']['multiplicities'][1]+[('C','D')]*DATA['after_ab']['multiplicities'][2]
 graph(c,pos,edges,[e for e in edges if 'D' in e] if protected else ())

def final(c,y,left,right,n,color):
 for i in range(n):curve(c,(280,y),(782,y),(i-(n-1)/2)*80,color)
 node(c,280,y,left,color);node(c,782,y,right,color)

c=Canvas('Karger：把图缩小，留下最小割')
k4(c,240,left='ABC')
c.text(65,700,'红边连接两侧；目标是让跨边最少',42,RED)
c.arrow((530,800),(530,885))
final(c,1030,'ABC','D',DATA['mincut'],RED)
c.text(65,1180,'合并顶点，保留每条跨边的身份',46)
c.text(65,1270,'一次可能错，多次取最小并量化风险',42)
c.save('00-cover.png','独立封面：原图到两个超节点，保留跨边结构')

c=Canvas('割是分成两组，再数跨边')
c.text(65,140,'A | BCD：红色跨边，蓝色组内边',42)
k4(c,300,left='A')
c.text(65,750,f"跨边 AB、AC、AD：共 {DATA['mincut']} 条",44,RED)
c.text(65,880,'AB | CD：同一张图，改分组',42)
k4(c,1040,left='AB')
c.text(65,1490,f"跨边 AC、AD、BC、BD：共 {max(r['value'] for r in DATA['cuts'])} 条",42,RED)
c.text(65,1600,'线条交叉处不是顶点；圆框才是顶点',40)
c.save('01-cuts.png','两种割在同一K4上显示跨边和组内边，不把平面几何当割')

c=Canvas('收缩 AB：顶点合并，边仍逐条保留')
k4(c,230)
c.text(65,680,'A 与 B 永久同组，记作超节点 AB',42)
c.arrow((531,770),(531,850))
tri(c,1000)
c.text(65,1460,'AC、BC 变成 AB 到 C 的两条平行边',40)
c.text(65,1540,'AD、BD 变成 AB 到 D 的两条平行边',40)
c.text(65,1620,'原来的 AB 变成自环：删除',42,RED)
# a visible loop and its crossout, isolated from label
c.d.ellipse((465,1740,595,1870),outline=GRAY,width=6)
node(c,530,1880,'AB');c.line((450,1730),(610,1835),RED)
c.text(65,2000,'自环两端同组，永远不跨割',42)
c.save('02-contract.png','显式呈现AB收缩后的双边、第三边和被丢弃的自环')

c=Canvas('均匀抽的是边副本，不是端点对')
tri(c,250)
c.text(65,720,'把剩下的每条边各写一张签',44)
for i,name in enumerate(DATA['after_ab']['copies']):
 x=55+i*200;c.card(x,830,180,100,name)
 c.text(x+35,960,f"1/{len(DATA['after_ab']['copies'])}",42)
c.text(65,1090,'AC、BC 两签：都合并 AB 与 C',42)
c.text(65,1180,'AD、BD 两签：都合并 AB 与 D',42)
c.text(65,1270,'CD 一签：合并 C 与 D',42)
c.text(65,1390,'按端点对各抽一签，会改变概率',44,RED)
c.save('03-sampling.png','把多重图五个边副本映射到五张等概率签')

c=Canvas('同一起点，两种结局')
tri(c,230)
c.text(65,690,'下一步选 AC（或 BC）',44,GREEN)
c.arrow((530,785),(530,855),GREEN)
final(c,1000,'ABC','D',DATA['mincut'],GREEN)
c.text(65,1140,f"原图跨边 AD、BD、CD：{DATA['mincut']} 条",42,GREEN)
c.text(65,1280,'回到上图：下一步改选 CD',44,RED)
c.arrow((530,1370),(530,1440),RED)
final(c,1600,'AB','CD',max(r['value'] for r in DATA['cuts']),RED)
c.text(65,1780,'AC、AD、BC、BD：合法，但非最优',42,RED)
c.save('04-branches.png','比较第二步收缩导致的成功与失败，并保留最终多重边')

c=Canvas('盯住一个最小割：ABC | D')
k4(c,230,left='ABC')
c.text(65,680,'红边 AD、BD、CD：危险，不能收缩',42,RED)
c.text(65,770,'蓝边 AB、AC、BC：当前安全',42,BLUE)
c.arrow((530,860),(530,930))
tri(c,1080,True)
c.text(65,1530,'已安全合并 AB：红色跨边一条未少',40,RED)
d=DATA['after_ab']['degrees']
c.text(65,1620,f"数接到各点的边：AB={d[0]}，C={d[1]}，D={d[2]}",42)
c.text(65,1710,f"每条边两头各数一次：共 {sum(d)} = 2 × {sum(DATA['after_ab']['multiplicities'])}",42)
c.text(65,1800,'下一步只有通向 C 的两条蓝边安全',42,BLUE)
c.save('05-survival.png','固定目标割跨边着色，展示条件存活与度数和的双计数')

c=Canvas('存活概率：沿着安全分支相乘')
# branching tree with clear edge labels
node(c,530,210,'K4')
c.arrow((480,260),(280,410),BLUE);c.arrow((580,260),(780,410),RED)
c.text(60,310,f'安全 {FIRST}',42,BLUE);c.text(740,310,f"破坏 {STEPS['first_total']-STEPS['first_safe']}/{STEPS['first_total']}",42,RED)
node(c,280,500,'割仍在',BLUE);node(c,780,500,'割消失',RED)
c.arrow((280,555),(280,730),BLUE);c.text(370,610,f'再安全 {NEXT}',42,BLUE)
node(c,280,820,'ABC|D',GREEN)
c.text(65,950,f"这个割：{FIRST} × {NEXT} = {DATA['exact']['fixed_D']}",46,GREEN)
c.text(65,1060,f"一般保证：{STEPS['first_lower']} × {STEPS['next_lower']} = {DATA['exact']['lower']}",44)
c.text(65,1170,f"K4 任意最小割：{DATA['exact']['by_value']['3']}",48,GREEN)
c.text(65,1280,'目标割存活、任意最优、下界是三回事',40)
c.save('06-probability.png','条件概率树区分固定割成功率、任意最小割成功率与下界')

c=Canvas('实际运行：输出的割再回原图核验')
s=DATA['sample'];c.text(65,140,f"K4，{s['runs']} 次；种子 {s['seed']}",42)
c.text(65,230,'横条共用计数尺度；绿色达到最优',40)
scale=720/s['runs'];lengths=[];values=[]
for i,key in enumerate(['3','4']):
 y=370+i*260;v=s['counts'][key];values.append(v);lengths.append(v*scale)
 c.text(65,y,f"割值 {key}：{v} 次",46,GREEN if key=='3' else RED)
 c.d.rectangle((65,y+90,65+v*scale,y+155),fill=GREEN if key=='3' else RED)
assert sorted(range(2),key=lambda i:values[i])==sorted(range(2),key=lambda i:lengths[i])
c.line((65,875),(785,875),INK);c.text(65,905,'0',40);c.text(725,905,str(s['runs']),40)
c.text(65,1040,'重复取最小：只有每次都失败才失败',42)
c.text(65,1140,f"K4 重复四次，全失败 = {DATA['repeat']['four_k4_failure']}",44)
c.text(65,1250,f"通用下界重复 {DATA['repeat']['T']} 次：",44)
c.text(65,1340,f"失败上界 (5/6)^{DATA['repeat']['T']} = {DATA['repeat']['generic_failure']:.5f}",44)
c.text(65,1450,'后两行是理论计算，不是柱图实测频率',40)
c.save('07-experiment.png','同轴实测输出分布，与重复失败理论数值明确分开')

c=Canvas('把所有有序路径逐条列出')
c.text(65,135,'每行先收缩左侧那条边；再看第二步',40)
c.text(65,215,'绿格割值为最优，红格割值较大',40)
for i,row in enumerate(DATA['path_matrix']):
 y=330+i*190
 c.text(50,y+35,row['first'],44)
 for j,o in enumerate(row['options']):
  x=190+j*168;good=o['value']==DATA['mincut']
  c.card(x,y,148,80,o['second'],fill='#dceee6' if good else '#ffe1df',color=GREEN if good else RED)
  c.text(x+30,y+95,str(o['value']),44,GREEN if good else RED)
c.text(65,1520,'格内上行：第二条原始边；下行：割值',40)
c.text(65,1610,f"{DATA['exact']['successful_leaf_paths']} 个绿格 / {DATA['exact']['leaf_paths']} 条等概率路径 = {DATA['exact']['by_value']['3']}",44,GREEN)
c.save('08-all-paths.png','精确枚举全部三十条K4有序路径，显式找到六个失败分支')

c=Canvas('边列表更新：两项相同也不去重')
c.text(65,135,'A=0，B=1，C=2，D=3；收缩 AB',42)
c.text(65,235,'原端点',42);c.text(405,235,'更新后',42);c.text(785,235,'处理',42)
for i,row in enumerate(DATA['endpoint_map']):
 y=350+i*155;u,v=row['original'];a,b=row['updated'];color=BLUE if row['keep'] else RED
 c.card(65,y,220,85,f'({u}, {v})')
 c.arrow((310,y+45),(390,y+45),color)
 c.card(425,y,220,85,f'({a}, {b})',fill='#e5eef7' if row['keep'] else '#ffe1df',color=color)
 c.text(765,y+10,'保留' if row['keep'] else '自环删',42,color)
c.text(65,1330,'旧列表每项都扫描；新列表逐项追加',42)
c.text(65,1420,'保留副本数，而不只是不同端点对',42)
c.save('09-edge-list.png','把图形收缩转换成实际整数端点列表，显式保留重复项、剔除自环')

(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'figures':len(meta),'all_geometry_checks':'PASS'},ensure_ascii=False))
