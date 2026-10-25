"""New teaching illustrations 00–14: CC BY 4.0. Code CC0-1.0.
Figures 15–16 derive from ESA tetra3 output and retains Apache-2.0 notices.
Canvas validation API adapted from the r1 Quickselect generator.
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

D=DATA;P=D['parameters']
# Layout coordinates/counts are schematic. Quantitative labels and geometry read D.
def spot(c,x,y,label='',color=BLUE,r=10):
 c.d.ellipse((x-r,y-r,x+r,y+r),fill=color);c.bottom=max(c.bottom,y+r)
 if label:c.text(x+18,y-25,label,40,color)
def vec(c,a,b,label,color=BLUE):
 c.arrow(a,b,color);c.text(b[0]+15,b[1]-15,label,40,color)
def triangle(c,xy,names,color=BLUE):
 for i,j in [(0,1),(1,2),(2,0)]:c.line(xy[i],xy[j],color)
 for pt,name in zip(xy,names):spot(c,*pt,name,color)
def projection_plot(c,pts,x,y,w,h,names,color=BLUE):
 c.d.rectangle((x,y,x+w,y+h),outline='#9fb3c0',width=3)
 for index,(pt,name) in enumerate(zip(pts,names)):
  xx=x+pt[0]/P['width']*w;yy=y+pt[1]/P['height']*h
  spot(c,xx,yy,color=color)
  dx,dy=([(-40,-60),(18,-25),(-35,25)][index] if len(pts)==3 else (18,-25))
  c.text(xx+dx,yy+dy,name,40,color)
 c.bottom=max(c.bottom,y+h)

c=Canvas('亮点没有名字，相机怎样认方向？')
xy=[(160,360),(420,300),(270,580),(720,490)]
triangle(c,xy[:3],['1','2','3']);spot(c,*xy[3],'4',GREEN)
c.arrow((570,340),(850,200),ORANGE);c.text(630,120,'星表中的方向',42,ORANGE)
c.text(65,720,'先认出：这些点是哪几颗星',44)
c.text(65,825,'再计算：相机的三根轴朝向哪里',44)
c.text(65,940,'图案识别 + 姿态；不等于测出宇宙位置',40)
c.save('00-cover.png','从无名亮点到恒星身份与相机姿态的任务封面')

c=Canvas('只知道看向哪，不等于姿态全知道')
c.text(65,145,'几何例：中心星不动，离轴星随滚转改变位置',40)
for i,offset in enumerate([D['roll_demo']['offset_before'],D['roll_demo']['offset_after']]):
 x=65+i*520;y=300;c.d.rectangle((x,y,x+420,y+420),outline=BLUE,width=4)
 centre=(x+210,y+210);spot(c,*centre,color=GREEN)
 c.text(centre[0]-145,centre[1]+25,'中心',40,GREEN)
 off=(centre[0]+offset[0],centre[1]+offset[1]);spot(c,*off,color=ORANGE)
 c.text(off[0]-70,off[1]-75 if i==0 else off[1]+25,'另一星',40,ORANGE)
 c.line(centre,off,ORANGE,True)
 c.text(x,780,'滚转前' if i==0 else f"相对转动{D['roll_demo']['angle_deg']}°",42)
c.text(65,910,'中心同一颗星，只约束光轴指向',42)
c.text(65,1010,'另一颗已知方向，才能约束画面怎样转',42)
c.save('01-attitude.png','两幅成像框中中心星不动而离轴星转动，体现单星剩余滚转自由度')

c=Canvas('一个星斑，不只占一个像素')
c.text(65,130,'1号星：扣除背景后的数字权重',42)
weights=D['first_patch_weights'];maximum=max(map(max,weights))
for row in range(3):
 for col in range(3):
  x=210+col*210;y=300+row*180;v=weights[row][col];shade=int(245-v/maximum*70)
  c.d.rectangle((x,y,x+190,y+160),fill=(shade,shade,shade),outline=BLUE,width=3)
  c.text(x+45,y+45,f'{v:.0f}',44)
for i,x in enumerate(D['first_patch_x']):c.text(235+i*210,225,str(x),40)
for i,y in enumerate(D['first_patch_y']):c.text(75,345+i*180,str(y),40)
c.text(65,920,f"总权重 {sum(map(sum,weights)):.0f}；质心 ({D['centroids_xy'][0][0]:.1f}, {D['centroids_xy'][0][1]:.1f})",42,GREEN)
c.text(65,1015,'右边与下边多一点光，中心便偏一点',42)
c.text(65,1110,'合成数字例；不是恒星表面或相机实拍',42)
c.save('02-centroid.png','3×3实际权重解释亚像素质心；横列x纵行y')

c=Canvas('先找亮团，再拒绝明显的假点')
c.text(65,135,f"本篇合成图：背景固定为{P['background']:g}，净值大于0",40)
projection_plot(c,D['centroids_xy'],70,300,900,675,['1','2','3','4'],GREEN)
for b in D['blobs']:
 if not b['accepted']:
  x=70+b['x']/P['width']*900;y=300+b['y']/P['height']*675
  spot(c,x,y,'假点',ORANGE,16)
  c.text(65,1090,f"最亮孤点：面积{b['area']}，被面积门槛拒绝",42,ORANGE)
c.text(65,1010,f"框是{P['width']}×{P['height']}；点标记放大以便看清",40)
c.text(65,1180,f"保留面积≥{P['minimum_area']}的连通团，按总权重排序",42)
c.text(65,1270,'真实阈值需考虑噪声；面积不能识破所有伪星',40)
c.save('03-extraction.png','同一合成输入四星和孤点坐标，说明亮度排序之前须筛选')

c=Canvas('用一个虚拟像平面，读出视线斜率')
o=(150,700);plane_x=570
c.arrow(o,(950,700),GREEN);c.text(800,745,'相机 +z',42,GREEN)
c.line((plane_x,245),(plane_x,810),BLUE);c.text(460,140,'前方虚拟像平面',42,BLUE)
c.arrow(o,(910,285),ORANGE);spot(c,plane_x,470,'星点',ORANGE)
c.line((150,870),(570,870),INK);c.text(255,915,'距离 f',44)
c.text(70,620,'光心',42)
c.text(65,1040,'横偏移 ÷ f = 横向分量 ÷ 光轴方向分量',40)
c.text(65,1135,'真实传感器在镜头后；这里移到前面作图',40)
c.save('04-pinhole.png','虚拟像平面相似三角形解释像素偏移为何除焦距')

c=Canvas('先换坐标，再把向量缩到单位长度')
c.text(65,130,f"主点 ({P['cx']:g}, {P['cy']:g})；f = {P['focal_px']:g} 像素",42)
x0,y0=200,650;c.arrow((x0,y0),(900,y0),BLUE);c.arrow((x0,270),(x0,760),GREEN)
c.text(720,710,'相机 +x',42,BLUE);c.text(235,250,'相机 +y（向下）',42,GREEN)
pt=D['centroids_xy'][0];scale=25;end=(x0+(pt[0]-P['cx'])*scale,y0-(P['cy']-pt[1])*scale)
spot(c,*end,'1',ORANGE);c.line((end[0],y0),end,ORANGE,True);c.line((x0,end[1]),end,ORANGE,True)
c.text(450,550,f"右移 {pt[0]-P['cx']:.1f}",42);c.text(235,325,f"上移 {P['cy']-pt[1]:.1f}",42)
c.text(65,830,'图像v与相机y均向下；z朝前构成右手系',40)
b=D['camera_rays'][0]
c.text(65,930,f"归一化后 b1 = ({b[0]:.5f}, {b[1]:.5f},",40)
c.text(595,1000,f"{b[2]:.5f})",40)
c.text(65,1100,'长度为1，留下方向，舍去任意倍数',42)
c.save('05-rays.png','同一星点偏移、相机坐标约定和单位视线坐标')

c=Canvas('比较星间夹角，不拿像素距离硬比')
pts=D['centroids_xy'][:3];xy=[(200+(p[0]-450)*3,280+(p[1]-350)*3) for p in pts]

for i,j in [(0,1),(1,2),(2,0)]:c.line(xy[i],xy[j],BLUE)
for i,(x,y) in enumerate(xy):
 spot(c,x,y,color=BLUE);c.text(x-50,y-70 if i!=2 else y+25,str(i+1),40,BLUE)
c.text(65,800,'连接线仅帮助认点对；不是天空里的实体线',40)
for i,row in enumerate(D['all_pair_angles_deg']):
 if row['pair'] in ['12','13','23']:c.text(90,910+['12','13','23'].index(row['pair'])*85,f"{row['pair'][0]}—{row['pair'][1]}：{row['degrees']:.4f}°",44)
c.text(520,910,'θ = arccos(bi·bj)',40,GREEN)
c.text(520,1010,'两条单位视线的夹角',40)
c.save('06-angles.png','三对角距数值与标号逐一对应；连接像素只定位')

c=Canvas('相机转了，三颗星之间的角没有变')
projection_plot(c,D['centroids_xy'][:3],45,300,460,345,['1','2','3'])
projection_plot(c,D['second_camera_pixels'][:3],555,300,460,345,['1','2','3'],ORANGE)
c.text(70,170,'原相机坐标',42,BLUE);c.text(580,170,'转动后的坐标',42,ORANGE)
c.text(65,730,'两框同样像素尺度；投影位置和形状会变',40)
c.text(65,835,'但两条视线的内积保持：',44)
c.text(170,935,'(R bi)·(R bj) = bi·bj',44,GREEN)
c.text(65,1045,'这里比较刚体旋转；姿态还要排除镜像',42)
c.text(65,1135,'镜头畸变或错误焦距会破坏这套比较',42)
c.save('07-invariant.png','实际改变相机方向后的投影对照解释球面角距不变量')

c=Canvas('三条边像指纹，但指纹也可能撞上')
for i,row in enumerate(D['coarse_candidates']):
 x=65+i*520;col=BLUE if i==0 else ORANGE
 c.text(x,150,'候选 '+row['stars'],44,col)
 points=[(x+55,340),(x+345,340),(x+145,570)]
 for a,b in [(0,1),(1,2),(2,0)]:c.line(points[a],points[b],col)
 for j,pt in enumerate(points):
  spot(c,*pt,color=col);c.text(pt[0]-20,pt[1]-65 if j!=2 else pt[1]+30,row['stars'][j],42,col)
 for j,v in enumerate(row['sorted_angles_deg']):c.text(x+40,740+j*85,f'{v:.4f}°',42)
c.text(65,1070,'上图只画身份关系，不按角度或像素比例',40)
c.text(65,1160,'两处同形三角是刻意设置的虚构星表歧义',40)
c.text(65,1250,'相同三边给出候选，不能直接宣布认星成功',40)
c.save('08-candidates.png','两套具体顶点关系与相同角距签名，展示不同身份可产生歧义')

c=Canvas('边长排序，不会自动告诉你点的名字')
c.text(65,130,'按1、2、3的顺序尝试A、B、C的排列',40)
for i,row in enumerate(D['permutation_checks']):
 y=260+i*115;c.text(80,y,row['mapping'],44,GREEN if i==0 else ORANGE)
 c.text(300,y,f"最大边角误差 {row['max_edge_error_deg']:.4f}°",42)
c.text(65,1030,f"本例门槛 {P['angle_tolerance_deg']:.3f}°，只留下ABC",42)
c.text(65,1125,'这是3!种对应的实际计算，不靠亮度当星名',40)
c.save('09-permutations.png','逐个排列核对有标签角距，找回无序签名丢掉的对应关系')

c=Canvas('把第四颗星投回照片，再问一次')
obs=D['centroids_xy'][3];false=D['candidates'][1]['fourth_best']['xy'];origin=(170,420);scale=9
spot(c,*origin,color=GREEN,r=12);c.text(origin[0]-70,origin[1]-90,'观测4 / 预测D',40,GREEN)
c.d.ellipse((origin[0]-P['validation_radius_px']*scale,origin[1]-P['validation_radius_px']*scale,origin[0]+P['validation_radius_px']*scale,origin[1]+P['validation_radius_px']*scale),outline=GREEN,width=4)
fp=(origin[0]+(false[0]-obs[0])*scale,origin[1]+(false[1]-obs[1])*scale)
spot(c,*fp,'预测H',ORANGE,12);c.line(origin,fp,ORANGE,True)
c.text(65,220,'局部像平面：u向右、v向下，两轴同尺度',40)
c.text(65,790,f"ABC→D：残差约0；EFG→H：{D['candidates'][1]['fourth_best']['residual_px']:.2f}像素",40)
c.text(65,890,f"绿色小圈：{P['validation_radius_px']:g}像素接受半径（教学选值）",42)
c.text(65,990,'同一个旋转必须解释额外的星，不能只解释三点',40)
c.text(65,1090,'已用于生成候选的点，不算独立验证证据',42)
c.save('10-validation.png','同像素尺度显示第四星残差0和63.25及真实2像素门槛')

c=Canvas('两条方向，怎样拼成一套坐标轴')
o=(150,700);b=(700,330);foot=(700,700)
a=(o[0]+math.hypot(b[0]-o[0],b[1]-o[1]),o[1])
c.arrow(o,a,BLUE);c.text(800,745,'e1',44,BLUE)
c.arrow(o,b,ORANGE);c.text(720,300,'b2',44,ORANGE)
c.line(b,foot,GREEN,True);c.arrow(foot,b,GREEN)
c.text(730,490,'剩下的',40,GREEN);c.text(730,550,'垂直部分',40,GREEN)
c.text(65,150,'先沿第一颗星，再找第二颗星“横出去”的部分',40)
c.text(65,865,'e1 = b1',44)
c.text(65,950,'q = b2 − (b1·b2) b1',44)
c.text(65,1035,'e2 = q / |q|；e3 = e1 × e2',44)
c.text(65,1135,'图中夹角为说明而放大；e3由右手规则确定',40)
c.save('11-frame.png','投影减法构造第二正交轴，再由叉积补右手第三轴')

c=Canvas('保持分量，换一套基底重组方向')
c.text(110,150,'相机基底 B',42)
c.text(650,150,'天空基底 S',42)
projection=((.9,-.6,0),(-.2,-.3,-.9));cols=[BLUE,ORANGE,GREEN]
for centre,matrix,prefix in [((265,520),D['camera_frame'],'e'),((800,520),D['sky_frame'],'s')]:
 for j,col in enumerate(cols):
  vector=[matrix[k][j] for k in range(3)]
  dx=sum(a*b for a,b in zip(projection[0],vector))*190
  dy=sum(a*b for a,b in zip(projection[1],vector))*190
  end=(centre[0]+dx,centre[1]+dy);c.arrow(centre,end,col)
  if prefix=='s' and j==1:c.text(end[0]+35,end[1]-15,'s2',42,col)
  else:c.text(end[0]-25,end[1]-70 if j!=2 else end[1]+20,prefix+str(j+1),42,col)
c.text(65,740,'两图用同一斜投影；投影长度不是三维长度',40)
c.text(65,830,'先用B^T求分量，再用S把同样分量放回天空',40)
c.text(220,940,'r = S B^T b；R = S B^T',48)
b=D['boresight_sky']
c.text(65,1060,'把相机光轴 (0,0,1) 代进去：',42)
c.text(100,1150,f"r = ({b[0]:.5f}, {b[1]:.5f}, {b[2]:.5f})",42,GREEN)
c.text(65,1250,'两套轴来自本例B、S的同一投影',40)
c.save('12-rotation.png','实际两基底同投影并标三轴，先分解后重组算出相机光轴')

c=Canvas('两颗星挤得太近，横向信息就太少')
rows=D['conditioning'];scale=780/max(z['inverse_sine'] for z in rows)
values=[z['inverse_sine'] for z in rows];lengths=[v*scale for v in values]
assert sorted(range(len(values)),key=values.__getitem__)==sorted(range(len(lengths)),key=lengths.__getitem__)
for i,z in enumerate(rows):
 y=200+i*280;c.text(65,y,f"夹角 {z['separation_deg']:g}°",44)
 c.d.rectangle((110,y+100,110+z['inverse_sine']*scale,y+165),fill=BLUE)
 c.text(110,y+190,f"1 / sin θ = {z['inverse_sine']:.1f}",40)
c.text(65,1130,'同尺比较归一化的放大因子，不是完整误差界',40)
c.text(65,1225,'垂直分量越短，噪声越容易改变其方向',42)
c.save('13-conditioning.png','由1/sin角距共轴展示两星过近的数值敏感性')

c=Canvas('同一个像点，错误焦距会给错方向')
e=D['centroid_error_example'];bad=D['wrong_focal_example'];u=D['centroids_xy'][1][0]-P['cx'];v=D['centroids_xy'][1][1]-P['cy'];rho=math.hypot(u,v)
o=(120,660);sx=.38;sy=2.5
c.arrow(o,(980,660),INK);c.text(800,710,'光轴方向',40)
for f,col,name in [(P['focal_px'],BLUE,'正确f'),(bad['wrong_focal_px'],ORANGE,'错误f')]:
 x=o[0]+f*sx;y=o[1]-rho*sy;c.line((x,300),(x,660),col);c.arrow(o,(x,y),col)
 label_x=x-85 if f==P['focal_px'] else x-190
 c.text(label_x,160,name,40,col);c.text(label_x,225,f'{f:g}像素',40,col)
c.text(65,830,'同样径向偏移，较小f给出更大的视线偏角',40)
c.text(65,925,f"2号星的实际角差：{bad['star2_ray_error_deg']:.4f}°",46,ORANGE)
c.text(65,1030,'侧视斜率示意：横纵方向不同缩放，角度不按比例',40)
c.text(65,1130,f"近轴{e['pixels']:g}像素约{e['angle_arcsec']:.2f}角秒，只是另一测量例",40)
c.text(65,1230,'精确质心与准确标定是两件事',44)
c.save('14-calibration.png','同一星点径向偏移在两个焦距平面上的方向差，明确非角度比例图')

# A faithful crop from the actual returned software canvas, nearest-neighbor enlarged.
c=Canvas('放大软件结果，分清“点”和“圈”')
c.text(65,135,'Alt40实际返回图：截取x=150～470、y=210～390',40)
source=Image.open(ROOT/'assets/real-alt40-matches.png').convert('RGB')
crop=source.crop((150,210,470,390)).resize((960,540),Image.Resampling.NEAREST)
c.im.paste(crop,(51,270));c.bottom=810
c.text(65,885,'原像素最近邻放大3倍；未移动或补画标记',40)
c.text(65,985,'白点：提取位置；绿圈：匹配的星表投影',40)
c.text(65,1080,'红圈：未匹配的星表投影，不等于一个假像素',40)
c.text(65,1175,'橙标记/绿小点：粗估与最终校正的位置',40)
c.save('15-real-detail.png','软件原返回画布保真局部放大并配中文图例，派生图依上游Apache2')
meta[-1]['identity']='ESA tetra3实际软件返回图的标明裁剪/3倍最近邻放大；中文讲解新加，整体按上游Apache2保留通知'

# These arrays are the real solver return, not a hand-built detection model.
import numpy as np
st=json.loads((ROOT/'examples/real-alt40-stages.json').read_text())
with np.load(ROOT/'examples/real-alt40-stages.npz') as stages:
 removed=stages['removed_background'];mask=stages['binary_mask']
lo,hi=st['display_limits']
removed_display=Image.fromarray(np.rint(np.clip((removed-lo)/(hi-lo),0,1)*255).astype('uint8')).convert('RGB')
mask_display=Image.fromarray(mask.astype('uint8')*255).convert('RGB')
c=Canvas('实测星场：扣背景，再留下亮团')
c.text(45,135,'Alt40原返回数组；同一帧、同一区域',42)
c.text(45,235,'去掉局部均值背景',40,BLUE)
c.text(565,235,'阈值 + 开运算',40,GREEN)
box=st['crop_xyxy'];panel_w=480;panel_h=round(panel_w*removed.shape[0]/removed.shape[1])
for x,im in [(30,removed_display),(552,mask_display)]:
 c.im.paste(im.resize((panel_w,panel_h),Image.Resampling.NEAREST),(x,330))
 coords=(x+box[0]/removed.shape[1]*panel_w,330+box[1]/removed.shape[0]*panel_h,x+box[2]/removed.shape[1]*panel_w,330+box[3]/removed.shape[0]*panel_h)
 c.d.rectangle(coords,outline='#ffae42',width=3)
c.bottom=330+panel_h
c.text(45,735,'上排为全幅缩览；橙框只标出下方放大区',40)
c.text(45,825,f"局部 x=[{box[0]},{box[2]})，y=[{box[1]},{box[3]})",40)
crop_size=((box[2]-box[0])*st['crop_scale'],(box[3]-box[1])*st['crop_scale'])
assert crop_size==(480,480)
for x,im in [(30,removed_display),(552,mask_display)]:
 c.im.paste(im.crop(tuple(box)).resize(crop_size,Image.Resampling.NEAREST),(x,945))
c.bottom=945+crop_size[1]
c.text(45,1470,f"同一区域最近邻放大{st['crop_scale']}倍，未改像素位置",40)
c.text(45,1560,f"右侧白色：开运算后保留的{st['crop_mask_true_pixels']}个像素",40,GREEN)
c.text(45,1650,f"左侧灰度按{st['display_percentiles'][0]:g}%～{st['display_percentiles'][1]:g}%分位线性显示",40)
c.text(45,1740,'右侧白=真、黑=假；不表示星的真实颜色',40)
c.text(45,1830,'亮斑周围的暗环是处理结果，不是天空结构',40)
c.save('16-real-extraction-stages.png','同一实测输入去背景与阈值/开运算真实阶段全幅及保真局部，呈现从背景隆起到离散像素团的变化')
meta[-1]['identity']='ESA tetra3实际返回数组的明示显示映射/缩览/最近邻局部；Apache2派生，不是手绘像素'

for f in sorted((ROOT/'assets').glob('real-*.png')):
 with Image.open(f) as im:meta.append({'file':str(f.relative_to(ROOT)),'width':im.width,'height':im.height,'min_font_px':None,'identity':'ESA tetra3真实测试输入的明示显示派生或软件实际返回图，非原创摄影','purpose':'真实星场/提取结果/匹配结果；图注解释其身份'})
for f in sorted((ROOT/'originals/photos').glob('*.tiff')):
 with Image.open(f) as im:meta.append({'file':str(f.relative_to(ROOT)),'width':im.width,'height':im.height,'min_font_px':None,'identity':'ESA tetra3项目原TIFF，未改字节；正文链接下载','purpose':'保留可验证原测试图'})
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('15 new illustrations and two real-output composites plus real-image outputs documented; geometry checks passed.')
