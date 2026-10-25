"""Original Count-Min figures, CC BY 4.0; generator code CC0-1.0.
Canvas validation API adapted from this repository's r1 Karger generator (CC0).
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

from fractions import Fraction
RED='#b13c37'; GRAY='#67798a'
CFG=DATA['configuration']
ENUM=DATA['enumeration']
NOISES=sorted(map(int,ENUM['row_noise_hist']))

assert CFG['width']==4 and CFG['depth']==3 and CFG['merge_split']==6
assert CFG['reference_total']==1000000 and DATA['experiment']['runs']==10000
assert DATA['experiment']['min_noise_counts'][str(max(NOISES))]==0
assert DATA['mapping']['A'][0]==DATA['mapping']['B'][0]==0
assert DATA['mapping']['A']==DATA['mapping']['E']
assert DATA['stream'][:3]==['A','B','A']
assert len(DATA['stream'])-CFG['merge_split']==6
assert len(DATA['table'])==CFG['depth'] and len(DATA['table'][0])==CFG['width']

def check_bar_order(values, scale):
 lengths=[v*scale for v in values]
 assert all((a<b)==(x<y) and (a==b)==(x==y) for a,x in zip(values,lengths) for b,y in zip(values,lengths))

check_bar_order([DATA['exact'][k] for k in 'ABCD'],100)
check_bar_order([DATA['exact'][k] for k in 'BCD'],100)
check_bar_order(list(DATA['enumeration']['row_noise_hist'].values()),600/max(DATA['enumeration']['row_noise_hist'].values()))

def table(c,rows,y,selected=None):
 for j in range(CFG['width']):c.text(275+j*180,y,str(j),40)
 for i,row in enumerate(rows):
  c.text(55,y+85+i*115,f'第{i+1}行',42)
  for j,v in enumerate(row):c.card(230+j*180,y+75+i*115,150,90,str(v),fill='#ffe1ae' if selected and selected[i]==j else '#e5eef7')

def tokens(c,vals,y):
 for i,v in enumerate(vals):c.card(55+i*80,y,70,90,str(v))

c=Canvas('Count-Min：用碰撞换取小表')
c.text(60,140,'收到事件，只给每行一个格子加数',42)
table(c,DATA['table'],240,DATA['mapping']['A'])
c.text(60,740,'查询 A：沿同一套映射读三个格子',42)
for i,v in enumerate(DATA['candidates']['A']):
 c.card(100+330*i,850,200,100,str(v),fill='#ffe1ae');c.arrow((200+330*i,970),(530,1080))
c.card(370,1110,320,110,f"最小值 {DATA['estimates']['A']}",fill='#dceee6')
c.text(60,1300,f"真实 A 有 {DATA['exact']['A']} 次；小表允许向上误差",42)
c.save('00-cover.png','封面：事件计数表与三路取最小的整体结构')

c=Canvas('先保留一份能逐个核对的账本')
c.text(60,140,'事件从左到右；下行接着上行',42)
tokens(c,DATA['stream'][:CFG['merge_split']],250);tokens(c,DATA['stream'][CFG['merge_split']:],400)
c.text(60,570,'精确账本需要保存键名和它的次数',42)
for i,k in enumerate('ABCD'):
 c.text(70,700+i*140,k,46);c.d.rectangle((170,710+i*140,170+DATA['exact'][k]*100,765+i*140),fill=BLUE)
 c.text(810,700+i*140,str(DATA['exact'][k]),46)
c.text(60,1300,f"总事件数 N = {DATA['total']}；横条每格长度代表一次",40)
c.save('01-stream.png','显示完整输入顺序与精确频率基线，同轴条形按实际次数绘制')

c=Canvas('哈希：给每个键规定桶编号')
c.text(60,140,'列号从零起；这张表是教学映射',42)
for j,label in enumerate(['键',*[f'第{i+1}行' for i in range(CFG['depth'])]]):c.text(70+245*j,260,label,42)
for i,k in enumerate('ABCDE'):
 for j,v in enumerate([k,*DATA['mapping'][k]]):c.card(55+245*j,365+i*130,205,90,str(v),fill='#ffe1ae' if k in 'AE' else '#e5eef7')
c.text(60,1100,'同一行可碰撞，换一行分组可以不同',40)
c.text(60,1190,'A 与 E 在所有行相同：刻意保留反例',40,RED)
c.save('02-hashes.png','完整公布五个键的三行映射，使每个图内读数可追踪')

c=Canvas('前三个事件：加哪几个格子？')
for step in range(3):
 y=140+step*640;k=DATA['stream'][step]
 c.text(60,y,f'事件 {step+1}：{k}，橙格刚加了 {CFG["unit_increment"]}',44)
 table(c,DATA['states'][step],y+95,DATA['mapping'][k])
c.text(60,2100,'第二次 A 回到原来的三个格子',42)
c.text(60,2180,'第一行 A、B 共用桶零，已混在一起',40,RED)
c.save('03-updates.png','逐次A/B/A更新的三个完整状态，标明碰撞第一次发生的位置')

c=Canvas('全部事件完成，再查询 A')
table(c,DATA['table'],150,DATA['mapping']['A'])
c.text(60,680,f"A 的列号依次是 {'、'.join(map(str,DATA['mapping']['A']))}",44)
c.text(60,780,'读数来自橙格，不是每行所有格取最小',40)
for i,v in enumerate(DATA['candidates']['A']):c.card(65,920+i*150,900,100,f'第 {i+1} 行：{v}',fill='#ffe1ae')
c.text(60,1430,f"min({', '.join(map(str,DATA['candidates']['A']))}) = {DATA['estimates']['A']}",48,GREEN)
c.text(60,1540,f"每行计数和都是 {sum(DATA['table'][0])}；全表和为 {sum(map(sum,DATA['table']))}",40)
c.save('04-query.png','查询路径与完整计数表，区别目标桶最小和全行最小')

c=Canvas('每个读数 = 自己 + 混进来的别人')
for i,(other,key) in enumerate([(DATA['exact'][key],key) for key in 'BCD']):
 y=180+i*280;c.text(60,y,f'第 {i+1} 行：A 与 {key} 同桶',44)
 base=65;unit=100;blue_end=base+DATA['exact']['A']*unit
 c.d.rectangle((base,y+100,blue_end,y+180),fill=BLUE);c.d.rectangle((blue_end,y+100,blue_end+other*unit,y+180),fill=ORANGE)
 c.text(65,y+200,f"自己 {DATA['exact']['A']} + {key} 的 {other} = {DATA['candidates']['A'][i]}",42)
c.text(60,1100,'蓝色段相同；橙色段都是非负污染',40)
c.text(60,1200,'取最小：选污染最少的一行',44,GREEN)
c.text(60,1300,'不做平均，也不能从桶里辨认各个键',40)
c.save('05-noise.png','同轴堆积条分解每行目标频率与碰撞噪声，展示上偏理由')

c=Canvas('没出现过，也可能查出非零次数')
c.card(70,180,900,100,'A 和 E 的路径完全相同',fill='#ffe1ae')
for i,k in enumerate('AE'):
 y=370+i*350;c.text(70,y,f"查询 {k}：{'、'.join(map(str,DATA['candidates'][k]))}",44)
 c.text(70,y+100,f"估计 {DATA['estimates'][k]}，真实 {DATA['exact'][k]}",46,RED if k=='E' else INK)
c.text(60,1100,'把流中全部 A 改成 E，计数表也不变',40)
c.text(60,1200,'因此：表本身不能找回键名列表',42,RED)
c.text(60,1300,'查询得零能判定没出现；非零不能反推',40)
c.save('06-absent.png','未出现键假阳性与两种不同输入同表的不可恢复反例')

c=Canvas('两个采集点：相同配置才能逐格相加')
for i,(label,key) in enumerate([('前六个事件','left'),('后六个事件','right'),('相加后 = 完整流','sum')]):
 y=140+i*650;c.text(60,y,label,44);table(c,DATA['merge'][key],y+90)
c.text(60,2160,'相同行数、列数、键编码和哈希函数',40)
c.text(60,2250,'只合并普通加法更新；每个格子独立相加',40)
c.save('07-merge.png','两段真实事件的完整表逐格合并，展示线性性质的具体输入输出')

c=Canvas('换随机映射，噪声有多大？')
c.text(60,140,'只研究一行：四个键各选四个桶',42)
c.text(60,235,'这次不使用前面的固定映射',42,RED)
c.text(60,330,f"共有 {' × '.join([str(CFG['width'])]*len('ABCD'))} = {ENUM['row_mappings']} 种等可能表",40)
hist=DATA['enumeration']['row_noise_hist'];scale=600/max(DATA['enumeration']['row_noise_hist'].values())
for i in NOISES:
 y=490+i*130;v=hist[str(i)];c.text(60,y,f'噪声 {i}',40);c.d.rectangle((250,y+10,250+v*scale,y+65),fill=BLUE);c.text(900,y,str(v),40)
c.text(60,1460,'横条是映射数；所有条共用尺度',40)
c.text(60,1550,'干净一行：其他三个键都避开 A',42)
c.text(60,1640,f"{' × '.join([f"({CFG['width']-1}/{CFG['width']})"]*len('BCD'))} = {ENUM['row_clean']}",42,GREEN)
c.save('08-one-row.png','精确枚举全随机单行哈希的噪声分布，展示概率来自初始化')

c=Canvas('最小值仍然太大：必须每行都太大')
c.text(60,140,f"沿用上一图的随机实验，阈值设为 {CFG['noise_threshold']}",40)
c.text(60,240,f"单行噪声 > {CFG['noise_threshold']}：{DATA['enumeration']['one_row_above_2']}",44)
for i in range(CFG['depth']):
 c.card(70,390+i*190,900,100,f"第 {i+1} 行噪声 > {CFG['noise_threshold']}",fill='#ffe1df',color=RED)
 if i<2:c.text(470,510+i*190,'且',42)
c.text(60,1050,'三行独立选映射，才可以相乘',42)
c.text(60,1150,f"({ENUM['one_row_above_2']}){str(CFG['depth']).translate(str.maketrans('0123456789','⁰¹²³⁴⁵⁶⁷⁸⁹'))} = {ENUM['three_rows_above_2']}",44,RED)
c.text(60,1260,f"约 {float(Fraction(ENUM['three_rows_above_2']))*100:.2f}%；不是单行概率的三倍",42)
c.text(60,1370,'把同一行复制三遍，不增加可信度',42)
c.save('09-depth.png','阈值失败事件的交集与独立乘法，区分独立行与复制行')

c=Canvas('宽度管误差；深度管失败概率')
for i,s in enumerate(DATA['sizes']):
 y=150+i*420;c.text(60,y,f"误差比例 {s['epsilon']}，失败概率 {s['delta']:g}",40)
 c.text(60,y+100,f"{s['width']} 列 × {s['depth']} 行 = {s['counters']} 个计数器",42)
 c.text(60,y+200,f"仅按 {CFG['counter_bits']} 位计数器：{s['bytes64']} 字节",40)
 c.text(60,y+290,f"N = 一百万时，加性误差界 {int(s['error_at_million'])}",40)
c.text(60,1490,'不是每个键自己的次数乘误差比例',42,RED)
c.text(60,1600,'字节数不含哈希、元数据、运行时对象',40)
c.save('10-sizing.png','三种精度参数的真实取整尺寸与百万流量误差规模')

deletes=DATA['deletions']['states']
def deletion_label(index):
 state=deletes[index]
 return f"A={state['exact']['A']}，B={state['exact']['B']}：桶值 {state['first_A_bucket']}"

c=Canvas('能不能减数：看真实频率是否非负')
c.text(60,145,'回到原来的固定映射，第 1 行 A、B 同桶',40)
c.card(70,280,900,110,'原来 '+deletion_label(0),fill='#e5eef7')
c.arrow((530,410),(530,485));c.text(60,460,f"B 减 {-deletes[1]['delta']}",42)
c.card(70,540,900,110,deletion_label(1)+'，仍不低估',fill='#dceee6')
c.arrow((530,690),(530,765));c.text(60,740,f"B 再减 {-deletes[2]['delta']}",42)
c.card(70,820,900,110,deletion_label(2)+'，低于 A',fill='#ffe1df',color=RED)
c.text(60,1080,'真实频率出现负数，非负污染前提消失',40,RED)
c.text(60,1190,'桶值非负，不代表每个键的频率非负',42)
c.text(60,1300,'附带代码只接受非负增量：是实现限制',40)
c.save('11-deletions.png','区分合法非负频率删减与负频率低估，反驳所有删减都不行')

c=Canvas('真正运行一万次，与精确概率对照')
c.text(60,140,f"随机种子 {DATA['experiment']['seed']}；每次重选三行",40)
c.text(60,230,f"输入频率固定为 {'、'.join(k+str(DATA['exact'][k]) for k in 'ABCD')}",42)
c.text(60,340,'最小噪声       实际次数       理论比例',40)
for i in NOISES:
 y=480+i*135;v=DATA['experiment']['min_noise_counts'][str(i)];p=float(Fraction(DATA['enumeration']['min_noise_pmf'][str(i)]))
 c.text(90,y,str(i),44);c.text(410,y,str(v),44);c.text(710,y,f'{p*100:.4f}%',40)
c.text(60,1490,'有限实跑不会精确等于概率',42)
c.text(60,1600,f"最坏噪声 {max(NOISES)} 没抽到，概率仍非零",42,RED)
c.save('12-experiment.png','全部七个误差值的真实试验频率与精确枚举概率逐项对照')
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(f'{len(meta)} figures passed geometry, glyph and pixel checks')
live=ROOT/'assets/13-live-demo.png'
if live.exists():
 with Image.open(live) as im:
  meta.append(dict(file='assets/13-live-demo.png',width=im.width,height=im.height,min_font_px=42,effective_min_font_at_354=14,identity='原创教学网页真实运行截图；实际点击调用Python',purpose='显示真实执行后的表和A至E查询；不是Redis界面',checks=['actual-browser-click','returned-json','browser-overflow','desktop-and-mobile']))
 (ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
