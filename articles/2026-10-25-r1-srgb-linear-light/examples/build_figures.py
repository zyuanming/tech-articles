"""Original sRGB scientific figures, CC BY 4.0; generator code CC0-1.0.
Canvas validation API adapted from this repository's r1 Count-Min generator (CC0).
All figure compositions below are new.
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
  meta.append(dict(file='assets/'+name,width=im.width,height=im.height,min_font_px=min(z[2] for z in self.boxes),effective_min_font_at_354=round(min(z[2] for z in self.boxes)/3,2),identity='原创教学示意；执行数值来自 results.json',purpose=purpose,checks=['canvas','declared-box','text-overlap','font-size','contrast','glyph-cmap','ink-pixels','actual-dimensions']))
M=DATA['main']
assert M['S_half']==.5 and len(DATA['curve'])==1001
assert len(DATA['image']['source'])==48 and DATA['image']['factor']==4
assert len(DATA['image']['small']['linear'])==12
assert DATA['edge']['weights']==[.25,.5,.25]
assert [z['a'] for z in DATA['alpha']]==[.25,.5,.75]
assert len(DATA['gradients']['direct'])==256
assert len(DATA['reference_gradients']['premult'])==257
GRAY='#627487'; RED='#a13631'
def swatch(c,y,rgb,label,h=150):
 c.text(60,y,label,42);c.d.rectangle((60,y+75,1000,y+75+h),fill=tuple(rgb),outline=GRAY,width=3);c.bottom=max(c.bottom,y+75+h)
def strip(c,y,values,label,height=150):
 c.text(60,y,label,42)
 im=Image.new('RGB',(len(values),1));im.putdata([tuple(v) if isinstance(v,list) else (v,v,v) for v in values]);c.im.paste(im.resize((942,height),Image.Resampling.NEAREST),(60,y+80));c.d.rectangle((60,y+80,1001,y+79+height),outline=GRAY,width=2);c.bottom=max(c.bottom,y+80+height)
def square(c,x,y,rows,size):
 im=Image.new('RGB',(len(rows[0]),len(rows)));im.putdata([(v,v,v) for row in rows for v in row]);c.im.paste(im.resize((size,size),Image.Resampling.NEAREST),(x,y));c.d.rectangle((x,y,x+size-1,y+size-1),outline=GRAY,width=2);c.bottom=max(c.bottom,y+size)
def curve(c,y,limit):
 left=150;right=940;top=y;bottom=y+630
 c.line((left,top),(left,bottom),GRAY);c.line((left,bottom),(right,bottom),GRAY)
 points=[z for z in DATA['curve'] if z['S']<=limit]
 scaleL=1 if limit==1 else .008;xy=[(left+z['S']/limit*(right-left),bottom-z['L']/scaleL*(bottom-top)) for z in points]
 c.d.line(xy,fill=BLUE,width=7)
 for s in [0,limit/2,limit]:
  x=left+s/limit*(right-left);c.line((x,bottom),(x,bottom+12),GRAY);c.text(x-25,bottom+25,f'{s:g}',40)
 for v in [0,scaleL/2,scaleL]:
  yy=bottom-v/scaleL*(bottom-top);c.text(15,yy-15,f'{v:.3f}',40)
 c.text(700,bottom+100,'横轴：编码 S',40);c.text(160,top-75,'纵轴：线性分量 L',40)
 c.bottom=max(c.bottom,bottom+160)

c=Canvas('同样“黑白各半”，为什么不同？')
swatch(c,150,[M['code_direct']]*3,f"直接平均编码：{M['code_direct']}",240)
swatch(c,590,[M['code_linear']]*3,f"先在线性光中平均：{M['code_linear']}",240)
c.text(60,1030,'两块是实际计算的 sRGB 像素',42)
c.text(60,1120,'看见差别，不等于测量了屏幕亮度',40)
c.save('00-cover.png','封面：实际128/188色块先呈现可见差异')

c=Canvas('一个像素值，可能是哪一种量？')
c.text(60,150,'三通道相等时得到中性灰',42)
for j,s in enumerate(['8位编码','S = 编码/255','线性分量 L']):c.text(50+335*j,260,s,40)
for i,z in enumerate(DATA['samples']):
 y=365+i*125
 for j,s in enumerate([str(z['code']),f"{z['S']:.6f}",f"{z['L']:.6f}"]):c.card(45+j*335,y,305,85,s)
c.text(60,1190,'编码等步长，线性光量并不等步长',40)
c.save('01-values.png','区分8位整数、归一化编码S和线性分量L')

c=Canvas('解码曲线：不是一条对角直线')
curve(c,250,1)
c.text(60,1110,'暗部放大：仍使用精确分段函数',42)
curve(c,1350,.08)
c.text(60,2190,'暗端是直线段，其后接幂函数段',40)
c.save('02-curve.png','同一解码曲线全域和暗部局部放大，轴范围明确')

c=Canvas('完整走一遍黑白等权混合')
c.card(55,160,450,110,'黑 S=0 → L=0')
c.card(555,160,450,110,'白 S=1 → L=1')
c.arrow((280,300),(450,460));c.arrow((780,300),(610,460))
for y,label in [(500,'线性平均：(0+1)/2 = 0.5'),(750,f"再编码：S = {M['S_from_L_half']:.6f}"),(1000,f"乘255后四舍五入 → {M['code_linear']}")]:c.card(65,y,930,100,label)
for y in [630,880]:c.arrow((530,y),(530,y+80))
c.text(60,1180,f"量化后再解码 L≈{M['L_from_188']:.6f}",42)
c.text(60,1270,'它接近0.5，但不是精确0.5',40)
c.save('03-steps.png','黑白两输入分别解码后汇合，再编码量化的完整数据链')

c=Canvas('两条渐变：等距的是哪一个量？')
strip(c,160,DATA['gradients']['direct'],'编码 S 等步长',200)
strip(c,570,DATA['gradients']['linear'],'线性分量 L 等步长，再编码',200)
c.text(60,990,'每条256列；放大只复制像素',42)
c.text(60,1080,'线性光等距 ≠ 主观感觉等距',42)
c.save('04-gradients.png','真实数值渐变对比，并区分物理线性与感知均匀')

c=Canvas('缩小棋盘：一个像素代表一片面积')
checker=[row[:DATA['image']['factor']] for row in DATA['image']['source'][:DATA['image']['factor']]]
square(c,330,160,checker,400)
c.text(60,620,'原区域黑白各占一半，等权平均',42)
for i,(v,s) in enumerate([(M['code_direct'],'直接平均编码'),(M['code_linear'],'平均线性光')]):
 c.text(60,770+i*280,f'{s} → {v}',42);c.d.rectangle((60,850+i*280,1000,1000+i*280),fill=(v,v,v),outline=GRAY,width=2);c.bottom=1000+i*280
c.save('05-downsample.png','棋盘面积平均的真实输出，对照源区域与两种缩小结果')

c=Canvas('模糊边缘：同一组权重也会算错')
strip(c,150,[int(v*255) for v in DATA['edge']['input']],'输入：黑白阶跃',120)
strip(c,460,DATA['edge']['encoded_codes'],'权重1/4、1/2、1/4作用于编码',120)
strip(c,770,DATA['edge']['linear_codes'],'同一权重作用于线性光，再编码',120)
ix=len(DATA['edge']['input'])//2
c.text(60,1100,f"边界左：{DATA['edge']['encoded_codes'][ix-1]} 对 {DATA['edge']['linear_codes'][ix-1]}",42)
c.text(60,1190,f"边界右：{DATA['edge']['encoded_codes'][ix]} 对 {DATA['edge']['linear_codes'][ix]}",42)
c.text(60,1280,'仅示范三点滤波，不冒称真实镜头',40)
c.save('06-blur.png','实际三点滤波结果与边界像素，展示暗边来源')

c=Canvas('彩色也逐通道算：红与绿各半')
for y,rgb,s in [(150,[255,0,0],'输入一：红 (255,0,0)'),(440,[0,255,0],'输入二：绿 (0,255,0)'),(730,DATA['redgreen']['encoded'],'直接平均编码'),(1020,DATA['redgreen']['linear'],'线性混合后编码')]:swatch(c,y,rgb,s+' '+(str(tuple(rgb)) if y>=700 else ''),130)
c.text(60,1330,'RGB单通道值不是总亮度Y',42)
c.save('07-colors.png','红绿混合实际色块，说明每个颜色通道都需正确表示')

c=Canvas('Alpha 是权重，不是另一个颜色')
c.text(60,145,'白色前景覆盖黑底，按给定alpha合成',40)
for i,z in enumerate(DATA['alpha']):
 y=260+i*330;c.text(60,y,f"alpha = {z['a']:.2f}",44)
 for x,key,label in [(60,'direct_code','直接用编码'),(550,'linear_code','在线性光中')]:
  v=z[key];c.d.rectangle((x,y+80,x+430,y+225),fill=(v,v,v),outline=GRAY,width=2);c.text(x,y+245,f'{label}：{v}',40)
c.text(60,1300,'alpha=0.5保持0.5，不先做sRGB解码',40)
c.save('08-alpha.png','多个透明权重实际合成，分开颜色曲线与alpha本身')

c=Canvas('透明像素里的蓝色，别混进红边')
c.text(60,150,'端点：不透明红 → 完全透明蓝',42)
c.text(60,240,'此图统一在线性RGB中插值，再叠白底',40)
strip(c,360,DATA['premult']['bad'],'直接插值RGB与alpha：隐藏蓝色混入',150)
strip(c,720,DATA['premult']['good'],'先预乘RGB×alpha，再插值',150)
c.text(60,1090,f"中点坏结果：{tuple(DATA['premult']['mid_bad'])}",42)
c.text(60,1180,f"中点预乘后：{tuple(DATA['premult']['mid_good'])}",42)
c.text(60,1270,'预乘与线性光是两件都要确认的事',40)
c.save('09-premult.png','同一线性空间下分离预乘问题，真实透明边缘效果')

c=Canvas('为何不把8位文件直接存成线性？')
c.text(60,150,'同一暗部范围：L从0到0.02',42)
strip(c,280,DATA['dark']['linear8'],f"先量化线性8位：仅{DATA['dark']['linear_levels']}种输出",200)
strip(c,690,DATA['dark']['srgb8'],f"先sRGB编码再量化：{DATA['dark']['srgb_levels']}种输出",200)
c.text(60,1100,'放大后复制原像素；暗部本来就暗',40)
c.text(60,1190,'浮点线性工作区与8位存储用途不同',40)
c.save('10-quantization.png','同一暗部输入的两种8位量化实际条带和唯一值计数')

c=Canvas('先判断这张纹理存的是什么')
for y,label in [(170,'颜色贴图：sRGB编码 → 解码'),(370,'线性工作区：混合、滤波、光照'),(570,'输出：编码一次 → 标注sRGB')]:c.card(65,y,930,110,label)
for y in [290,490]:c.arrow((530,y),(530,y+60))
c.text(60,820,'数值贴图：粗糙度、法线、深度等',42)
c.text(60,920,'按数据定义读取，不自动套颜色曲线',42)
c.text(60,1050,f"数据0.5若误解码，会变{M['L_from_S_half']:.6f}",42,RED)
c.save('11-workflow.png','颜色与非颜色数据两条路径，防止对全部纹理统一gamma处理')

c=Canvas('工作区L=0.5，输出环节错在哪里？')
for i,(key,label) in enumerate([('no_encode','漏掉编码'),('code_linear','正确编码一次'),('double_encode','重复编码两次')]):
 v=M[key];swatch(c,150+i*350,[v]*3,f'{label}：8位值{v}',170)
c.text(60,1250,'两端0和1不变，不能只用纯黑白排错',40)
c.save('12-output-errors.png','漏编码和重复编码的真实中灰对比')

c=Canvas('“大约gamma 2.2”不是精确sRGB')
for j,s in enumerate(['编码 S','精确解码 L','S的2.2次方']):c.text(55+j*330,170,s,40)
for i,z in enumerate(DATA['approx']['samples']):
 for j,s in enumerate([f"{z['S']:.2f}",f"{z['exact']:.6f}",f"{z['power22']:.6f}"]):c.card(50+j*330,280+i*145,295,95,s)
c.text(60,950,'1001点抽样的最大绝对差：',42)
c.text(60,1040,f"{DATA['approx']['max_error']:.6f}，出现在S≈{DATA['approx']['at_S']:.3f}",42)
c.text(60,1150,'这只是该采样网格结果，不是连续极值证明',40)
c.save('13-approximation.png','实际比较近似幂函数误差，尤其暗部差异')

c=Canvas('实际二维图像：4×4面积缩小')
c.text(60,145,'原创48×48测试图：棋盘与斜边',42)
square(c,290,245,DATA['image']['source'],480)
c.text(60,795,'各4×4区域变为一个像素，输出12×12',40)
for x,key,label in [(60,'encoded','编码平均'),(560,'linear','线性平均')]:
 c.text(x,920,label,42);square(c,x,1010,DATA['image']['small'][key],420)
c.text(60,1510,'展示放大均用最近邻，不添新过渡色',40)
c.save('14-image-result.png','真正执行二维区域缩小，保留源图与两种全部输出像素')

c=Canvas('W3C示例条件：预乘与不预乘')
c.text(60,150,'红 → 透明黑 → 蓝，叠在白底',42)
c.text(60,240,'插值与叠白底都用编码sRGB，区别于图09',40)
strip(c,370,DATA['reference_gradients']['premult'],'按预乘值插值',170)
strip(c,760,DATA['reference_gradients']['straight'],'若错误地插值未预乘值',170)
c.text(60,1150,'依据规范文字条件重新计算，非原SVG',40)
c.text(60,1240,'W3C版权及完整许可见来源附页',40)
c.save('16-source-gradient.png','许可下复算W3C13.4两个相关渐变条件；不是原图或原页面截图')
meta[-1]['identity']='依据W3C CSS Color4文字条件的重计算与新排版；非原SVG'
# Actual browser screenshot is made by capture_demo.py before final metadata pass.
live=ROOT/'assets/15-live-demo.png'
if live.exists():
 im=Image.open(live);assert im.width==1062
 meta.append(dict(file='assets/15-live-demo.png',width=im.width,height=im.height,min_font_px=42,effective_min_font_at_354=14,identity='原创Python教学网页真实浏览器执行截图；非显示器光度测量',purpose='实际点击计算与返回数据，核PNG编码身份',checks=['browser-click','returned-data','no-overflow','sRGB-chunk','actual-dimensions']))
for z in meta:
 im=Image.open(ROOT/z['file']);assert im.size==(z['width'],z['height']);assert im.info.get('srgb')==0
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('figures checked:',len(meta))
