"""New shadow-volume figures; code CC0, figure output CC BY 4.0.
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
GRAY='#627487';RED='#a13631';D=DATA;R=D['renders'];I=D['intervals']
def rows(c,y,ss):
 for i,s in enumerate(ss):c.text(60,y+90*i,s,42)
def panel(c,x,y,key,w=440):
 im=Image.open(ROOT/D['outputs'][key]['file']);h=round(w*im.height/im.width)
 c.im.paste(im.resize((w,h),Image.Resampling.NEAREST),(x,y));c.d.rectangle((x,y,x+w,y+h),outline=GRAY,width=2);c.bottom=max(c.bottom,y+h)
def pair(c,y,a,b,la,lb):
 for x,key,label in [(60,a,la),(562,b,lb)]:c.text(x,y,label,40);panel(c,x,y+80,key)
def interval(c,y,q,mode,label):
 # All horizontal distances derive from the same 0..10 model coordinate axis.
 x=lambda t:80+88*t
 c.text(60,y,label,42);y+=170
 a,b=[z[0] for z in I['inside']['events']]
 c.d.rectangle((x(a),y-24,x(b),y+24),fill='#cadde8')
 c.arrow((x(0),y),(x(10),y),GRAY)
 for t,s in q['events']:
  c.line((x(t),y-50),(x(t),y+50),GREEN if s==1 else ORANGE)
  c.text(x(t)-22,y+60,str(t),40)
 c.d.ellipse((x(q['p'])-11,y-11,x(q['p'])+11,y+11),fill=RED)
 c.text(x(q['p'])-20,y-70,'P',44,RED)
 if q['start']>0:
  c.line((x(q['start']),y-55),(x(q['start']),y+55),RED);c.text(60,y+150,f"计数起点={q['start']}；P={q['p']}",42)
 else:c.text(60,y+150,f"P={q['p']}；区间边界2和6",42)
 c.text(60,y+240,f"{mode}={q[mode]}；正确体内标记={q['truth']}",42)
 c.bottom=max(c.bottom,y+310)
def proj(v,origin=(550,650),scale=150):
 return (origin[0]+scale*(v[0]-.65*v[1]),origin[1]-scale*(v[2]+.28*v[0]+.28*v[1]))
def poly(c,points,fill,outline=GRAY):
 c.d.polygon(points,fill=fill,outline=outline,width=4);c.bottom=max(c.bottom,max(p[1] for p in points))
def wire(c,verts,faces,origin,scale,color=GRAY):
 seen=set()
 for f in faces:
  for a,b in zip(f,f[1:]+f[:1]):
   key=tuple(sorted((a,b)))
   if key not in seen:c.line(proj(verts[a],origin,scale),proj(verts[b],origin,scale),color);seen.add(key)

c=Canvas('模板阴影体：用穿越次数找出阴影')
# Independent cover with full rendered image, not reused as an interior panel.
panel(c,81,150,'outside-zfail',900)
rows(c,960,['原创CPU参考渲染：盒子、平面、点光','每个像素只问：这个可见点在体内吗？'])
c.save('00-cover.png','真实执行的完整阴影渲染，建立技术对象与用途')

c=Canvas('两条线：眼睛找表面，灯判断遮挡')
q=D['ray_demo']
def demo_project(v):return (300+90*(v[0]-.25*v[1]),700-90*(v[2]+.1*v[0]+.1*v[1]))
# Explicit oblique projection of actual 3D model coordinates. Camera path is clear in 3D.
for tri in D['faces']:
 poly(c,[demo_project(D['vertices'][k]) for k in tri],'#c8d4df')
e,p,l,b=[demo_project(q[k]) for k in ['C','P','L','B']]
c.arrow(e,p,BLUE);c.arrow(p,b,ORANGE);c.arrow(b,l,ORANGE,True)
for pos,col in [(e,BLUE),(p,RED),(l,ORANGE),(b,INK)]:
 c.d.ellipse((pos[0]-11,pos[1]-11,pos[0]+11,pos[1]+11),fill=col)
c.text(750,180,'相机 C',44,BLUE);c.text(60,130,'点光 L',44,ORANGE)
c.text(60,650,'交点 B',44);c.line((220,680),b,GRAY)
c.text(500,770,'接收点 P',44,RED);c.line((480,780),p,GRAY)
rows(c,920,['蓝色眼线：C → P，先见地板上的P','橙色检查线：P → L，在B碰到盒子','虚线是被阻挡后的检查线，不是透光'])
rows(c,1260,[f"P={tuple(q['P'])}；C={tuple(q['C'])}",f"L={tuple(q['L'])}",f"B=({q['B'][0]:g}, {q['B'][1]:g}, {q['B'][2]:g})",'同三维场景坐标的斜投影示意'])
c.save('01-scene.png','JSON绑定同一P、相机C、灯L与实算遮挡B，眼线无阻挡而灯线有阻挡')

c=Canvas('同一画面，还存深度与模板')
pair(c,160,'outside-depth','outside-count','射线距离：近白远黑','模板：浅色0，蓝色1')
r=R['outside'];rows(c,680,[f"有效表面像素：{r['valid']}；阴影：{r['shadow']}",'深度图范围0至18场景单位','这里画的是距离，不是硬件投影深度'])
c.save('02-buffers.png','实际深度图和模板计数图，配色/范围/有效像素明确')

c=Canvas('z-pass：只数P之前的进入与退出')
for y,key,lab in [(150,'before','先遇P，再遇体：不加不减'),(700,'inside','先进入，再遇P：加1'),(1250,'after','进入又退出，再遇P：加1减1')]:interval(c,y,I[key],'zpass',lab)
c.save('03-zpass.png','三个接收点完整穿越步骤，共用区间与比例轴')

c=Canvas('相机在体内：初值0已经错了')
interval(c,150,I['eye_inside'],'zpass','相机移到3，进入事件在身后')
rows(c,740,['起点实际上已经在一个阴影体中','但清零后到P之间没有新事件','结果0被误读为“无阴影”'])
c.save('04-eye-inside.png','同一轴上的相机进入体内反例，初值失效')

c=Canvas('眼睛在外，近裁剪仍可能切掉入口')
interval(c,150,I['near_cut'],'zpass','眼睛仍在0，实际可绘范围从3起')
rows(c,740,['t=2的进入面被裁掉，只剩t=6退出','结果−1仍为非零：把亮处判成暗处','安全条件涉及近裁剪面，不能只查眼睛'])
c.save('05-near-clip.png','近裁剪丢入口而眼睛在外的独立反例')

c=Canvas('z-fail：改数P之后，规则反过来')
for y,key,lab in [(150,'before','P后有进入和退出：减1加1'),(700,'inside','P后只有退出：加1'),(1250,'after','P后没有边界：仍为0')]:interval(c,y,I[key],'zfail',lab)
c.save('06-zfail.png','相同三点的后半视线计数，从闭合末端0倒推体内')

c=Canvas('闭合不可省：两种漏盖，两种误判')
interval(c,150,I['no_front'],'zfail','漏入口：亮处P=1被误判为1')
interval(c,700,I['no_back'],'zfail','漏出口：暗处P=4被误判为0')
rows(c,1300,[f"若远裁剪在{I['far_cut']['end']}：也丢掉t=6出口",'z-fail=0，并不能凭名字自动鲁棒'])
c.save('07-caps.png','漏前盖/漏后盖及远裁剪的确定反例')

c=Canvas('找轮廓前，先看面是否朝向灯')
v=D['vertices'];f=D['faces'];g=D['geometry']
for j in [0,6,8,2,4,10]:
 face=f[j];quad=list(dict.fromkeys(f[j]+f[j+1]));pts=[proj(v[k],(530,650),170) for k in quad]
 # Actual triangles avoid wrong quad vertex ordering.
 for tri in [f[j],f[j+1]]:poly(c,[proj(v[k],(530,650),170) for k in tri],'#a6d5c0' if g['light_facing'][j] else '#dae1e8')
c.text(60,160,'绿：朝灯；灰：背灯；不是朝相机',42)
c.text(60,250,'透明拓扑投影：显示被挡住的面与边',42)
rows(c,850,['取一个点V，外法线N','比较 N·(L−V) 的正负',f"上面N=(0,0,1)，灯比盒顶高{D['light'][2]-D['bounds'][1][2]:g}",f"所以单位法线点积为{D['light'][2]-D['bounds'][1][2]:g}，朝向灯"])
c.save('08-light-facing.png','盒子实际三角网格的光源朝向分类，区分两个参考方向')

c=Canvas('轮廓边：两侧面朝灯状态不同')
wire(c,v,f,(530,620),210,GRAY)
for a,b in g['silhouette']:c.line(proj(v[a],(530,620),210),proj(v[b],(530,620),210),RED)
rows(c,900,[f"红色：{len(g['silhouette'])}条轮廓边",'灰色：其他边；线框包含隐藏边','每条边都查两个相邻面的朝灯布尔值','两值不同才挤出，不按屏幕外轮廓猜'])
c.save('09-silhouette.png','从实际邻接数组选出的6条灯光轮廓边，内部对角线不误挤出')

c=Canvas('沿灯到顶点的方向拉长，再封口')
vv=v+D['illustration_far'];origin=(350,650);scale=85
# Draw far, side, then near with semitransparent-like solid palette; wire preserves topology.
for tri in D['volume_faces'][g['front_count']:g['front_count']+g['back_count']]:poly(c,[proj(vv[k],origin,scale) for k in tri],'#f1cd9a')
for tri in D['volume_faces'][g['front_count']+g['back_count']:]:poly(c,[proj(vv[k],origin,scale) for k in tri],'#dae6f0')
for tri in D['volume_faces'][:g['front_count']]:poly(c,[proj(vv[k],origin,scale) for k in tri],'#a6d5c0')
wire(c,vv,D['volume_faces'],origin,scale,GRAY)
rows(c,150,['绿色前盖；橙色后盖；浅蓝侧面','此结构图k=2；实际渲染用k=20'])
c.text(650,390,'后盖单独显示',40,ORANGE)
for tri in D['volume_faces'][g['front_count']:g['front_count']+g['back_count']]:poly(c,[proj(vv[k],(800,650),75) for k in tri],'#f1cd9a')
rows(c,1200,['V远 = L + k(V−L)',f"前盖{g['front_count']}、后盖{g['back_count']}个三角形",f"{len(g['silhouette'])}条边形成{g['side_count']}个侧面三角形",'有限k只在接收点没有超出末端时适用'])
c.save('10-extrusion.png','同实际构造的k=2可视化，k与实际20明确区分，三部分闭合')

c=Canvas('同一条共边，两面必须反向走')
# Topological diagram, no physical lengths claimed.
poly(c,[(200,400),(800,400),(500,180)],'#a6d5c0')
poly(c,[(200,400),(800,400),(800,750),(200,750)],'#dae6f0')
c.arrow((290,365),(700,365),GREEN);c.arrow((700,460),(290,460),BLUE)
c.text(100,280,'前盖',42);c.text(400,610,'侧面',42)
rows(c,900,['前盖边 a→b；侧面边 b→a','一致的外向绕序才能配对进入与退出','模型检查：每边恰有两面，且方向相反'])
c.save('11-winding.png','共享边有向绕序的局部放大，避免生成体面方向失衡')

c=Canvas('进入阴影体后：实际错误会反转')
pair(c,150,'inside-zfail','inside-zpass','正确z-fail','错误z-pass初值0')
pair(c,680,'inside-count','inside-error','正确模板：蓝色1','红色：与独立真值不符')
r=R['inside'];rows(c,1210,[f"相机={tuple(r['camera'])}",f"有效点{r['valid']}；错误z-pass有{r['zpass_errors']}点不符",f"闭合z-fail有{r['zfail_errors']}点不符",'相机确实在阴影体内；场景几何没换'])
c.save('12-render-inside.png','同三维场景相机进入阴影体的实际正确/错误/计数/误差四联图')

c=Canvas('漏后盖：换一盏灯就暴露问题')
pair(c,150,'other-light-zfail','other-light-no-far-cap','完整闭合体','故意不计后盖')
r=R['other-light'];rows(c,680,[f"此处改灯为{tuple(r['light'])}",f"有效点{r['valid']}；漏盖后{r['missing_far_errors']}点不符",'原灯位置漏后盖恰未错，不代表可删','小样例通过，不能代替闭合条件'])
c.save('13-missing-cap-render.png','实际另一个灯位置暴露漏后盖错误，避免只用恰巧通过场景')

c=Canvas('模板要可逆：饱和加减会丢历史')
for y,label,vals,col in [(180,'环绕：先减1，再加1',D['wrap'],GREEN),(430,'饱和：先减1，再加1',D['saturate'],RED)]:
 c.text(60,y,label,42)
 for i,val in enumerate(vals):c.card(70+i*340,y+90,260,100,str(val),color=col)
rows(c,760,[f"8位环绕里，256个体重叠也变{D['wrap_256']}",'所以WRAP修复可逆性，不保证永不溢出'])
o=D['overlap'];c.text(60,1040,'两个体重叠：计数可以为2',42)
for i,(a,b) in enumerate(o['intervals']):
 y=1150+150*i;c.text(60,y,f"体{'AB'[i]}：({a},{b})",42)
 c.d.rectangle((100+110*a,y+70,100+110*b,y+110),fill=BLUE if i==0 else GREEN)
 c.bottom=max(c.bottom,y+110)
for i,(p,n) in enumerate(zip(o['points'],o['counts'])):c.text(60,1510+90*i,f'位置 {p:g} → 重叠数 {n}',42)
c.save('14-wrap.png','实算环绕与饱和顺序反例以及重叠数，明确8位整周期风险')

c=Canvas('每盏灯都有自己的阴影判断')
pair(c,150,'outside-count','other-light-count','灯A的模板','灯B的模板')
rows(c,680,['先画环境项并保存最近表面深度','灯A：清模板 → 计数 → 只给0处加光','灯B：再清模板 → 计数 → 只给0处加光','不要让灯A的阴影禁止灯B照亮该点'])
c.save('15-multiple-lights.png','两个实际灯位置不同模板，与逐灯独立重建/加光流程相联系')

c=Canvas('这次验证了什么，没有验证什么')
rows(c,160,[f"区间穷举：{D['interval_tests']}个非边界接收点例"])
for i,(key,label) in enumerate([('outside','体外相机'),('inside','体内相机'),('other-light','更换光源')]):
 rr=R[key];c.text(60,310+i*140,f"{label}：{rr['valid']}点，z-fail错{rr['zfail_errors']}",42)
rows(c,850,['独立真值：P到灯的线段与盒相交','计数路径：眼线与体三角形求交','没有模拟GPU覆盖规则、MSAA或速度','高面数×多灯×大覆盖，仍可能很贵'])
c.save('16-verification.png','两个独立几何问题的交叉验证规模与未验证范围')
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('validated',len(meta),'figures')
ui=ROOT/'assets/17-live-ui.png'
if ui.exists():
 im=Image.open(ui);meta.append(dict(file='assets/17-live-ui.png',width=im.width,height=im.height,min_font_px=42,effective_min_font_at_354=14,identity='实际Chromium HTTP教学查看器截图；原始模型图最近邻显示',purpose='实际程序版本、输入视角、结果与误差可见；真实切换三种数据后截图',checks=['browser-image-decode','browser-no-overflow','computed-font-size','actual-dimensions','real-select-interaction']))
 (ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
