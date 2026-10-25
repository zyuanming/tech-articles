"""Original normal-map scientific figures, CC BY 4.0; generator code CC0-1.0.
Canvas validation API adapted from this repository's r1 sRGB generator (CC0).
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
  meta.append(dict(file='assets/'+name,width=im.width,height=im.height,min_font_px=min(z[2] for z in self.boxes),effective_min_font_at_354=round(min(z[2] for z in self.boxes)/3,2),identity='原创教学示意；执行数值来自 results.json',purpose=purpose,checks=['canvas','declared-box','text-overlap','font-size','contrast','glyph-cmap','ink-pixels','actual-dimensions']))
import shutil
M=DATA['main'];F=M['frame']; Q=DATA['mirror'];GRAY='#627487'; RED='#a13631'
def vec(v,n=2):return '('+', '.join(f'{(0 if abs(x)<1e-12 else x):.{n}f}' for x in v)+')'
def panel(c,x,y,key,size=420):
 p=ROOT/DATA['outputs'][key]['file'];im=Image.open(p);assert list(im.size)==DATA['outputs'][key]['size']
 c.im.paste(im.resize((size,size),Image.Resampling.NEAREST),(x,y));c.d.rectangle((x,y,x+size,y+size),outline=GRAY,width=2);c.bottom=max(c.bottom,y+size)
def pair(c,y,a,b,la,lb):
 for x,key,label in [(60,a,la),(570,b,lb)]:c.text(x,y,label,40);panel(c,x,y+85,key)
def rows(c,start,labels):
 for i,s in enumerate(labels):c.text(60,start+i*90,s,42)
def project(v,o=(570,580),s=270):return (o[0]+s*(v[0]-.5*v[1]),o[1]-s*(v[2]+.45*v[1]))
c=Canvas('几何不变，光照细节可以改变')
pair(c,160,'flat','mapped','同一平面：平坦法线','同一平面：法线纹理')
rows(c,770,['原创CPU计算；正交相机朝向平面','96×96实际输出，最近邻放大','没有新增顶点，也没有抬高表面'])
c.save('00-cover.png','同几何同光源的实际渲染；建立改变光照而非几何的核心问题')

c=Canvas('法线：告诉光照“这里朝向哪边”')
o=(510,650);c.line((110,650),(920,650),GRAY);c.arrow(o,(510,300),GREEN);c.text(550,285,'N：面向外',42)
c.arrow(o,(270,400),ORANGE);c.text(95,310,'L：朝向灯',42)
c.text(120,720,'向量 = 方向 + 长度；单位向量长度1',40)
rows(c,850,['点积：对应分量相乘，再相加','单位向量点积 = 两方向夹角的余弦','光照：同向1，垂直0，背向取0'])
c.save('01-normal.png','真实几何表面的法线与向光方向；定义向量、单位长度和点积')

c=Canvas('紫蓝色纹理：三个通道存三个分量')
panel(c,290,160,'normal-map',480)
im=Image.open(ROOT/DATA['outputs']['normal-map']['file']);xy=DATA['render_details']['mapped']['samples'][0]['pixel'];rgb=im.getpixel(tuple(xy))
rows(c,720,[f'真实数据纹理：{im.width}×{im.height}像素',f'像素 {tuple(xy)}：RGB = {rgb}','读取字节÷255，再做2c−1','图中颜色仅是数据的可视预览'])
c.save('02-texture.png','原始程序纹理全部像素与一个真实像素字节；预览不替代输入数据')

c=Canvas('先解包：理想值与8位值分开')
rows(c,160,[f"理想RGB = {vec(M['rgb'])}",'逐通道：2c−1',f"局部 n = {vec(M['nt'])}",'长度平方：0.36²+0.48²+0.8² = 1'])
rows(c,600,[f"8位四舍五入：{tuple(M['codes'])}",'除255，解包，再归一化',f"得到 {vec(M['quant_nt'],4)}",'128/128/255 也不是精确平坦'])
c.save('03-unpack.png','逐通道解包完整例与实际8位量化后的不同向量')

c=Canvas('局部三根轴，不是世界三根轴')
o=project((0,0,0))
for k,col,lab in [('T',BLUE,'T 沿u增加'),('B',ORANGE,'B 沿v增加'),('N',GREEN,'N 面向外')]:
 end=project(F[k]);c.arrow(o,end,col)
for y,k in [(850,'T'),(940,'B'),(1030,'N')]:c.text(60,y,f'{k} = {vec(F[k],0)}',42)
c.text(590,180,'N',48,GREEN);c.text(350,385,'T',48,BLUE);c.text(180,575,'B',48,ORANGE)
c.text(60,740,'轴名属于局部；坐标值属于世界',42)
c.save('04-frame.png','主例TBN箭头在同一斜投影中，各轴世界坐标明确')

c=Canvas('换基，就是把三段方向加起来')
parts=[tuple(M['nt'][i]*x for x in F[k]) for i,k in enumerate(['T','B','N'])];acc=(0,0,0);o=(700,1000)
for p,col in zip(parts,[BLUE,ORANGE,GREEN]):
 nxt=tuple(a+b for a,b in zip(acc,p));c.arrow(project(acc,o,400),project(nxt,o,400),col);acc=nxt
c.arrow(project((0,0,0),o,400),project(acc,o,400),RED,True)
rows(c,160,[f"0.36T = {vec(parts[0])}",f"0.48B = {vec(parts[1])}",f"0.80N = {vec(parts[2])}"])
rows(c,1150,[f"相加：世界 n = {vec(M['nw'])}",'虚线为合向量；结果已是单位长度'])
c.save('05-basis.png','依次首尾相加的换基箭头由JSON分量驱动；保留中间三项')

c=Canvas('方向在同一空间，才可以点积')
rows(c,160,[f"世界光方向 L = {vec(M['light'])}",f"正确世界 n = {vec(M['nw'])}",f"若错把局部 n 当世界：{vec(M['nt'])}"])
for y,value,label,col in [(520,M['good_dot'],'正确',GREEN),(750,M['wrong_dot'],'漏换基',RED)]:
 c.text(60,y,f'{label}：n·L = {value:.2f}',42);c.d.rectangle((60,y+90,60+900*value,y+180),fill=col);c.bottom=y+180
c.text(60,1030,'两条共轴，条长按点积值线性绘制',40)
c.save('06-light.png','同一世界光方向的正确1/错误.64点积，条长从实跑JSON计算')

c=Canvas('UV三角形如何决定切线方向？')
# Each vertex position comes from executed triangle data, under fixed display projections.
for offset,coords,kind in [((130,430),M['uv'],'UV'),((780,480),M['positions'],'P')]:
 pts=[(offset[0]+160*v[0],offset[1]-110*v[1]) for v in coords]
 c.d.polygon(pts,outline=BLUE,width=5)
 for i,(x,y) in enumerate(pts):c.d.ellipse((x-7,y-7,x+7,y+7),fill=BLUE);c.text(x-65 if i==2 else x+25 if kind=='P' and i==1 else x-25,y-70 if i==2 else y+20,f'{kind}{i}',40)
c.text(100,150,'UV平面',44);c.text(620,150,'世界XY平面',44)
rows(c,570,['UV边：(1,0) 与 (0,1)',f"位置边：{vec(F['edges'][0],0)}、{vec(F['edges'][1],0)}",f"原始 ∂P/∂u = {vec(F['rawT'],0)}",f"归一化 T = {vec(F['T'],0)}",f"原始 ∂P/∂v = {vec(F['rawB'],0)}",'UV共线时行列式为0，无法唯一求解'])
c.save('07-triangle.png','对应三角形/边/导数/单位切线，明确长度2不能直接当单位基')

c=Canvas('方片转90°：纹理与坐标轴一起转')
pair(c,160,'rotated-correct','rotated-wrong','正确：旋转T与B','错误：局部值当世界')
rows(c,770,['固定相机；方片绕世界Z轴旋转90°','屏幕点先逆旋转，找到原UV像素','正方形此时外轮廓恰好不变'])
c.save('08-rotation.png','实际正交投影逆UV采样+旋转TBN，与漏换基结果比较')

c=Canvas('镜像UV：不能丢掉手性符号w')
rows(c,160,[f"原来 w={F['w']}，B={vec(F['B'],0)}",f"镜像 w={Q['frame']['w']}，B={vec(Q['frame']['B'],0)}",'glTF：B = w × cross(N,T)',f"同一方向的镜像局部 n={vec(Q['nt'])}"])
for x,frame,label in [(310,F,'原UV'),(800,Q['frame'],'镜像UV')]:
 o=(x,800);c.arrow(o,(x,620),BLUE);c.arrow(o,(x+170*frame['B'][0],800),ORANGE);c.text(x-100,900,label,42)
rows(c,1050,[f"正确世界 n={vec(Q['correct'])}",f"漏w后世界 n={vec(Q['wrong'])}",f"漏w点积：{Q['wrong_dot']:.4f}"])
c.save('09-mirror.png','保持同一世界方向的镜像局部分量+B手性变换，非仅标签描述')

c=Canvas('绿色通道的符号，不是图像上下翻转')
pair(c,160,'mapped','green-flip','约定匹配','只反转ny')
rows(c,770,['反转绿色：G → 1−G，即ny → −ny','图像上下翻转：换了采样像素位置','两种操作不同，先核生产端约定'])
c.save('10-green.png','实际翻转法线分量的光照后果，区分采样位置与方向')

c=Canvas('插值后恢复单位长度；强度改倾斜')
z=DATA['filter'];rows(c,160,[f"两方向 {vec(z['a'],1)} 与 {vec(z['b'],1)}",f"均值 {vec(z['mean'],1)}，长度 {z['length']:.1f}",f"归一化后 {vec(z['normalized'],1)}"])
for i,q in enumerate(DATA['scales']):
 c.text(60,550+i*100,f"scale={q['scale']:g} → n={vec(q['n'],3)}",40)
c.text(60,1060,'先缩放x/y，再对整个向量归一化',42)
c.save('11-filter-scale.png','可核滤波缩短例和四个normalScale结果，避免把长度误当强度')

c=Canvas('法线是数据：不要套sRGB颜色解码')
pair(c,160,'mapped','gamma-wrong','按字节读取数据','错误：先sRGB解码')
rows(c,770,['理想平坦RGB=(0.5,0.5,1)',f"误解码后方向≈{vec(DATA['gamma_wrong_flat'],3)}",'最终光照图仍可编码为sRGB显示'])
c.save('12-data.png','真实错误色彩处理渲染，与理想平坦法线错误倾斜数值')

c=Canvas('换灯会改变明暗；轮廓始终没长高')
pair(c,160,'mapped','other-light','灯在右上方','灯改到左上方')
rows(c,770,['两个实际输出仍是同一个平面','侧面轮廓示意：所有顶点的z都为0'])
c.line((90,1080),(970,1080),GRAY)
texture=Image.open(ROOT/DATA['outputs']['normal-map']['file'])
for i in range(10):
 rgb=texture.getpixel((i*9,32));n=[2*v/255-1 for v in rgb];c.arrow((100+i*90,1080),(100+i*90+90*n[0],1080-90*n[2]),BLUE)
c.text(60,1170,'箭头是方向，不是表面的新增高度',42)
c.save('13-limits.png','同模型换灯真实效果以及平面侧视，分离法线箭头与轮廓高度')

c=Canvas('从制作到显示：对齐六个环节')
for i,s in enumerate(['UV与几何 → 确定切线基','烘焙/生成 → 编码局部方向','采样RGB → 按数值解包','用匹配TBN → 换到光照空间','归一化 → 计算照明','显示颜色 → sRGB编码一次']):
 y=150+i*190;c.card(60,y,940,110,s)
 if i<5:c.arrow((530,y+120),(530,y+170))
c.text(60,1350,'本例只含漫反射与常量项，不是PBR',40)
c.save('14-pipeline.png','生产与运行阶段边界清晰的完整路径，标注教学渲染范围')

src=ROOT/'originals/photos/CompareNormal-original.jpg';dst=ROOT/'assets/16-official-compare.jpg';shutil.copyfile(src,dst);im=Image.open(dst)
meta.append(dict(file='assets/16-official-compare.jpg',width=im.width,height=im.height,min_font_px=None,effective_min_font_at_354=None,identity='Khronos CompareNormal官方Babylon.js Sandbox截图原件；CC0并附商标条款',purpose='真实工具中法线纹理开启/省略的可见效果参照；保持原上下文',checks=['byte-identical-to-original','actual-dimensions']))
live=ROOT/'assets/15-live-demo.png'
if live.exists():
 im=Image.open(live);meta.append(dict(file='assets/15-live-demo.png',width=im.width,height=im.height,min_font_px=42,effective_min_font_at_354=14,identity='原创Python网页真实执行截图',purpose='可点击重算的主例与CPU渲染',checks=['browser-click','returned-data','no-overflow']))
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('figures checked:',len(meta))
