"""New MIS figures; code CC0, figure output CC BY 4.0.
Canvas checks adapted from previous CC0 generator; compositions new.
"""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
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
  assert all(0<=p[0]<=1062 and 0<=p[1]<=4000 for p in (a,b))
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
  im=self.im.crop((0,0,1062,math.ceil(self.bottom+45)));p=ROOT/'assets'/name;info=PngImagePlugin.PngInfo();info.add(b'sRGB',b'\x00');im.save(p,pnginfo=info)
  assert Image.open(p).size==im.size
  meta.append(dict(file='assets/'+name,width=im.width,height=im.height,min_font_px=min(z[2] for z in self.boxes),effective_min_font_at_354=round(min(z[2] for z in self.boxes)/3,2),identity='原创CPU模型输出或教学示意；执行数值来自 results.json',purpose=purpose,checks=['canvas','declared-box','text-overlap','font-size','contrast','glyph-cmap','ink-pixels','actual-dimensions']))
D=DATA;T=D['toy'];R=D['render'];GRAY='#627487';RED='#a13631';meta=[]

def rows(c,y,lines):
 for i,s in enumerate(lines):c.text(60,y+i*88,s,42)
def panel(c,x,y,key,w=440,crop=None):
 im=Image.open(ROOT/R['outputs'][key]['file'])
 if crop:im=im.crop(crop)
 h=round(w*im.height/im.width);c.im.paste(im.resize((w,h),Image.Resampling.NEAREST),(x,y));c.d.rectangle((x,y,x+w,y+h),outline=GRAY,width=2);c.bottom=max(c.bottom,y+h)
def pair(c,y,a,b,la,lb,crop=None):
 for x,key,label in [(60,a,la),(562,b,lb)]:c.text(x,y,label,40);panel(c,x,y+75,key,crop=crop)
def bar(c,x,y,value,maximum,width=700,color=BLUE):
 length=width*value/maximum;c.d.rectangle((x,y,x+length,y+45),fill=color);c.bottom=max(c.bottom,y+45);return length

def two_bins(c,y,vals,label,maximum=2):
 c.text(60,y,label,42)
 left=190;scale=280;bottom=y+400
 c.line((left,bottom),(left+640,bottom),GRAY)
 for j,v in enumerate(vals):
  x=left+j*320;h=v/maximum*250;c.d.rectangle((x,bottom-h,x+280,bottom),fill=BLUE if j==0 else GREEN)
  c.text(x+30,bottom-h-65,f'{v:g}',42);c.text(x+70,bottom+30,'左半' if j==0 else '右半',40)
 c.bottom=max(c.bottom,bottom+100)

c=Canvas('多重重要性采样：让两种策略互补')
pair(c,160,'light','balance','只按光分布抽32次','MIS各抽16次')
rows(c,560,['同一原创CPU球场景；同一估计项预算','左球较粗糙，右球高光较集中','这是真实计算图，不是原论文截图'])
c.save('00-cover.png','真实球渲染预览，建立有限样本噪声和组合策略的任务')

c=Canvas('要算的量：两块面积加起来')
two_bins(c,150,T['heights'],'高度 f；两半宽度都是0.5')
rows(c,670,[f"左面积={T['widths'][0]:g}×{T['heights'][0]:g}={T['F'][0]:g}",f"右面积={T['widths'][1]:g}×{T['heights'][1]:g}={T['F'][1]:g}",f"目标 I={sum(T['F']):g}；不是两个高度直接相加"])
c.save('01-area.png','从同宽矩形面积引入积分，避免把高度与区域贡献混淆')

c=Canvas('概率密度不是概率：看面积')
two_bins(c,150,T['densities'][0],'A：偏向左半，密度共用同一尺度')
two_bins(c,700,T['densities'][1],'B：偏向右半，密度共用同一尺度')
rows(c,1240,['密度1.8 × 宽0.5 = 概率0.9','密度0.2 × 宽0.5 = 概率0.1','密度可以大于1；总概率仍须等于1'])
c.save('02-density.png','两方案密度高度和区域概率的对应，保持共轴比例')

c=Canvas('怎样抽到左或右：先抽0到1的数')
for i,(label,p,choices) in enumerate(zip(['A','B'],T['probabilities'],T['choices'])):
 y=170+i*450;c.text(60,y,f'{label}：累计概率分界 {p[0]:g}',42)
 x=100;w=850;c.d.rectangle((x,y+100,x+w*p[0],y+165),fill=BLUE);c.d.rectangle((x+w*p[0],y+100,x+w,y+165),fill=GREEN)
 c.text(85,y+190,'0',40);c.text(940,y+190,'1',40)
 for u in T['uniforms']:c.line((x+w*u,y+80),(x+w*u,y+175),RED)
 c.text(60,y+280,'同组u → '+''.join('左' if k==0 else '右' for k in choices),42)
rows(c,1110,['红线u：'+', '.join(f'{u:g}' for u in T['uniforms']),'这里只示范选区域；区间内再均匀抽点'])
c.save('03-sampling.png','累计概率分段与同一组随机数的实际区域选择')

c=Canvas('少抽到一次，就要让它代表更多')
for j in range(2):
 y=180+j*420;p=T['probabilities'][0][j];value=T['F'][j]/p
 c.text(60,y,('A抽左半' if j==0 else 'A抽右半')+f'：概率 {p:g}',42)
 bar(c,180,y+100,value,10,700,BLUE if j==0 else ORANGE)
 c.text(180,y+180,f'一次估计 F/P = {value:.6g}',42)
rows(c,1050,['两条共用0到10的长度尺度','稀少的右半样本会贡献10，形成亮点','按概率加权平均仍为2；单次未必接近2'])
c.save('04-tail.png','同轴显示稀有样本的大贡献，解释无偏与噪声并存')

c=Canvas('各抽一次：四种结果都算一遍')
for x,label in [(60,'A/B'),(300,'概率'),(520,'简单平均'),(800,'balance')]:c.text(x,150,label,40)
for i,r in enumerate(T['outcomes']):
 y=270+i*145
 for x,s in [(60,('左' if r['A']==0 else '右')+'/'+('左' if r['B']==0 else '右')),(300,f"{r['probability']:.2f}"),(530,f"{r['naive']:.3f}"),(835,f"{r['balance']:.0f}")]:c.text(x,y,s,42)
rows(c,970,['简单平均没有偏，但仍可能跳到10','本例balance四种结果都为2','这是互补恰好完美的特例，不是通则'])
c.save('05-outcomes.png','穷尽双样本四事件及概率，比较天真平均与MIS而非只展示好运一次')

c=Canvas('在同一个位置，比两种生成概率')
for j in range(2):
 y=170+j*520;c.text(60,y,'样本落在'+('左半' if j==0 else '右半'),42)
 for i,label in enumerate(['A','B']):
  val=T['modes']['balance']['weights'][i][j];c.text(65,y+100+i*130,label,42);bar(c,170,y+110+i*130,val,1,650,BLUE if i==0 else GREEN);c.text(850,y+95+i*130,f'{val:g}',42)
 c.text(60,y+380,'加权后每个已抽样项恰好贡献1',42)
rows(c,1300,['不能拿A样本处的概率去比B另一个点','无论谁生成x，都在同一个x求两种概率'])
c.save('06-pointwise.png','权重随位置变化，明确交叉求概率而非比较不同样本点')

c=Canvas('不重复计数：每块贡献分完为止')
for j in range(2):
 y=180+j*330;c.text(60,y,'左半F=1' if j==0 else '右半F=1',42)
 x=200;w=700;a=T['modes']['balance']['weights'][0][j];c.d.rectangle((x,y+90,x+w*a,y+165),fill=BLUE);c.d.rectangle((x+w*a,y+90,x+w,y+165),fill=GREEN)
 c.text(200,y+200,f'A期望份额{a:g} + B份额{1-a:g} = 1',40)
rows(c,940,['蓝色A、绿色B；长度表示期望份额','每个位置wA+wB=1，合起来才是原量',f"不加权直接相加：期望={T['wrong_sum_expectation']:g}"])
c.save('07-unbiased.png','用每个区域期望分摊说明权重和为1与重复计数错误')

c=Canvas('抽样数不相等，权重也要知道')
rows(c,160,['A抽3次，B抽1次；看的是 n×P'])
for j in range(2):
 y=320+j*340;pA=T['probabilities'][0][j];pB=T['probabilities'][1][j]
 c.text(60,y,'左半' if j==0 else '右半',42)
 c.text(230,y,f'3×{pA:g} 对 1×{pB:g}',42)
 c.text(60,y+110,f"wA={T['unequal']['weights'][0][j]:.6f}",42)
 c.text(550,y+110,f"wB={T['unequal']['weights'][1][j]:.6f}",42)
rows(c,1080,['A三项先平均，B一项单独算，再相加','最终不要再除以总样本数4','n既影响权重，也影响每组的平均'])
c.save('08-counts.png','3比1样本预算的实际权重与组内平均，防漏n或多除一次')

c=Canvas('power平方更偏向大概率，但不总更好')
for y,key,label in [(170,'balance','balance'),(490,'power','power，β=2')]:
 c.text(60,y,label,42)
 for i,l in enumerate(['A','B']):
  w=T['modes'][key]['weights'][i][0];c.text(60,y+85+i*95,l,40);bar(c,150,y+95+i*95,w,1,650,BLUE if i==0 else GREEN);c.text(830,y+80+i*95,f'{w:.3f}',40)
rows(c,920,[f"本例balance方差={T['modes']['balance']['variance']:.6f}",f"本例power方差={T['modes']['power']['variance']:.6f}",'平方压低小概率项；也改变两者如何抵消'])
c.save('09-power.png','同点实际balance/power权重及精确反例，阻止绝对最优误解')

c=Canvas('已有完美策略时，混入另一种会变差')
rows(c,160,['换目标：左贡献9，右贡献1，总量10','A仍按0.9/0.1抽样，每次都返回10'])
vals=[T['perfect'][k]['variance'] for k in ['A_only','balance','power']];lengths=[]
for i,(name,v) in enumerate(zip(['只用A两次','balance各1次','power各1次'],vals)):
 y=430+i*200;c.text(60,y,name,42);lengths.append(bar(c,330,y+80,v,max(vals),560));c.text(700,y,f'{v:.4f}',42)
assert sorted(range(3),key=lambda i:vals[i])==sorted(range(3),key=lambda i:lengths[i])
rows(c,1110,['条长是方差，共用尺度；总样本都为2','零方差的A，不能靠混合变得比零更小'])
c.save('10-perfect.png','第二个确切反例：一策略精确匹配目标时MIS增加方差')

c=Canvas('一个方案可漏区，两者一起不能漏')
for y,title,key in [(170,'互补覆盖：A只左，B只右','split'),(650,'共同空洞：A只左，B也只左','hole')]:
 a,b=T['support_probabilities'][key]
 c.text(60,y,title,42)
 for i,(label,v) in enumerate([('A',a),('B',b)]):
  c.text(90,y+110+i*130,label,42)
  for j,k in enumerate(v):c.card(250+j*340,y+85+i*130,290,100,'可抽' if k else '概率0',fill='#d5eadd' if k else '#efe0dc')
rows(c,1160,['上：w在不支持处取0，仍能算全两块','下：右半永远不会出现，目标会漏掉','样本再多也补不了共同概率为0的区域'])
c.save('11-support.png','两种支持集合逐格对照，明确联合覆盖条件')

c=Canvas('先统一单位，才能把密度相加')
m=T['measure'];P=(180,760);L=(P[0]+300*m['L'][0],P[1]-300*m['L'][1]);c.line(P,L,BLUE);c.line((L[0]-130,L[1]),(L[0]+130,L[1]),ORANGE);c.arrow(L,(L[0],L[1]+170),ORANGE)
c.text(110,800,'接收点P',42);c.text(600,350,'光源面小片',42);c.text(740,670,'面法线',40);c.text(270,570,'距离2m',42)
c.d.arc((L[0]-100,L[1]-100,L[0]+100,L[1]+100),90,90+math.degrees(math.acos(m["light_cosine"])),fill=ORANGE,width=6)
c.text(500,670,f'θ={math.degrees(math.acos(m["light_cosine"])):.0f}°',40,ORANGE)
rows(c,980,['面积密度 pA=1 /m²；cosθ=0.5',f"换成方向密度：1×2²/0.5={m['solid_angle_density']:g} /sr",'再与另一方案的0.25 /sr比较',f"balance权重={m['balance_weight']:.6f}"])
c.save('12-measure.png','真实几何距离与面法线示意，面积密度转立体角密度后才可组合')

c=Canvas('实际场景：两个球，共享一片亮环境')
panel(c,80,150,'reference',900)
c.text(110,700,'左：指数6',42);c.text(620,700,'右：指数180',42)
panel(c,200,820,'environment',660)
rows(c,1250,[f"方向表32×64={R['direction_count']}格，等立体角",f"亮斑占{R['bright_cells']}格；其余仍有背景光",'表横轴方位角；纵轴z，不是照片纬度','球：完整离散求和参考；非连续积分真值'])
c.save('13-scene.png','实际球及环境方向表，明确材质、光、离散模型参考身份')

c=Canvas('固定32个估计项：四种实算结果')
pair(c,160,'light','brdf','光分布32次','材质分布32次')
pair(c,590,'balance','power','balance 16+16','power 16+16')
rows(c,1020,['统一颜色、色调映射和sRGB编码','同样样本数不等于同样运行时间','随机种子各自固定，没有挑图改变结论'])
c.save('14-renders.png','四种策略的完整真实计算结果，同预算同显示条件')

c=Canvas('同一局部放大：保留原采样格子')
box=R['zoom_box'];pair(c,160,'light','brdf','光分布','材质分布',box)
pair(c,770,'balance','power','balance','power',box)
rows(c,1390,[f'原图裁取框：{tuple(box)}','左闭右开像素范围，四图完全相同','最近邻放大不增加原始160×88的细节'])
c.save('15-zoom.png','同一高光局部的实际噪声放大，避免缩略图掩盖差别')

c=Canvas('误差在变色之前计算')
pair(c,160,'light-error','brdf-error','光分布误差','材质分布误差')
pair(c,590,'balance-error','power-error','balance误差','power误差')
rows(c,1020,['颜色表示绝对线性误差：蓝0 → 红≥0.5','同一个误差尺度；红色超过0.5会饱和','统计使用未裁剪误差，不从显示图反推'])
c.save('16-error.png','真实线性误差图与固定饱和显示范围，区分图像和统计')

c=Canvas('一张较好看的图，不等于期望更好')
vals=[R['stats'][k]['expected_mse'] for k in ['light','brdf','balance','power']];lengths=[]
for i,(key,label,v) in enumerate(zip(['light','brdf','balance','power'],['光分布','材质分布','balance','power'],vals)):
 y=180+i*240;c.text(60,y,label,42);c.text(540,y,f'期望MSE {v:.6f}',40);lengths.append(bar(c,90,y+85,v,max(vals),850));c.text(90,y+150,f"本次RMSE {R['stats'][key]['rmse']:.6f}",40)
assert sorted(range(4),key=lambda i:vals[i])==sorted(range(4),key=lambda i:lengths[i])
rows(c,1210,['power这次RMSE更低，期望MSE却略高','比较算法要看重复实验或解析方差',f"条长仅对应期望MSE；{R['valid_pixels']}点平均"])
c.save('17-statistics.png','解析期望误差与单种子误差并列，防止挑一次结果概括优劣')

c=Canvas('实现顺序：一个样本，两种概率')
for i,line in enumerate(['按当前策略生成一个位置x','在同一个x求 f、pA、pB','用nA pA与nB pB计算权重','加上 w×f/p当前','各策略组内平均，最后相加']):
 y=160+i*210;c.card(95,y,870,120,line);
 if i<4:c.arrow((530,y+130),(530,y+195),GRAY)
rows(c,1300,['p不是“这个样本看起来亮不亮”','它描述生成这个位置的概率密度'])
c.save('18-flow.png','逐样本实际执行顺序，标明交叉求PDF和最后的平均层级')

c=Canvas('随机选一种策略：另一个合法模型')
c.card(350,170,360,100,'先抛硬币选A/B')
c.arrow((430,285),(260,400),BLUE);c.arrow((630,285),(800,400),GREEN)
c.card(80,420,360,110,'一半概率选A');c.card(620,420,360,110,'一半概率选B')
c.arrow((260,545),(530,690),BLUE);c.arrow((800,545),(530,690),GREEN)
c.card(180,710,720,110,'q(x)=0.5pA(x)+0.5pB(x)')
rows(c,950,['一次只抽一个位置，返回 f(x)/q(x)','固定各抽一次：各组平均，再把贡献相加','两者都可无偏，但策略样本数波动不同'])
c.save('19-mixture.png','单样本混合路径与固定多样本模型分清，避免混用系数')

c=Canvas('来光亮锥与材质瓣，不一定指向同一处')
g=D['geometry'];P=(520,850);radius=500
pt=lambda angle,r: (P[0]+r*math.cos(math.radians(angle)),P[1]-r*math.sin(math.radians(angle)))
lo=g['light_center_degrees']-g['light_half_angle_degrees'];hi=g['light_center_degrees']+g['light_half_angle_degrees']
c.d.polygon([P]+[pt(t,radius) for t in range(int(lo),int(hi)+1)],fill='#f3e0be')
for m,col in [('6',GREEN),('180',BLUE)]:
 pts=[pt(a,400*v) for a,v in zip(g['angles_degrees'],g['relative_kernels'][m])];c.d.line(pts,fill=col,width=6)
tangent=g['normal_degrees']-90;c.line(pt(tangent,-360),pt(tangent,360),GRAY)
for vec,col in [(g['normal'],GREEN),(g['outgoing'],GRAY),(g['reflection'],BLUE),(g['incoming'],ORANGE)]:c.arrow(P,(P[0]+radius*vec[0],P[1]-radius*vec[1]),col)
c.text(60,160,f"亮锥{g['light_center_degrees']}°±{g['light_half_angle_degrees']}°",42,ORANGE);c.text(340,250,'镜头方向wo',42);c.text(70,330,'来光wi',42,ORANGE);c.text(765,380,'法线N',42,GREEN);c.text(810,620,f"R={g['reflection_degrees']:.0f}°",40,BLUE);c.text(470,900,'表面点P',42)
rows(c,1060,['另选二维截面：N70°、wo90°、wi110°','绿色：宽瓣m=6；蓝色：窄瓣m=180','曲线半径：材质×余弦，各自归一到峰值','方向箭头从P指向外，不代表光子行进'])
c.save('21-directions.png','独立截面的真实向量反射运算和两种材质瓣，补全光照方向关系')

# Preserve a separately captured genuine browser figure in metadata.
ui=ROOT/'assets/20-live-ui.png'
if ui.exists():
 im=Image.open(ui);meta.append(dict(file='assets/20-live-ui.png',width=im.width,height=im.height,min_font_px=42,effective_min_font_at_354=14,identity='真实本地HTTP查看器截图，读实跑JSON',purpose='现场切换四种结果，显示实际方法/预算/误差',checks=['real-browser','decode','interaction','no-overflow']))
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('validated',len(meta),'figures')
