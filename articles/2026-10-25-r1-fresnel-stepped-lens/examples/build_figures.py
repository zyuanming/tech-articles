"""New content CC BY 4.0; generator CC0-1.0. Run trace.py first."""
import math, json
from figure_canvas import Canvas, DATA as D, ROOT, BLUE, GREEN, ORANGE, INK, meta
Q=D['rays'][4]; F=D['model']['f']
C=['#176297','#166c57','#9c4d0d','#7d3c86','#a62d49']
def poly(c,points,fill='#d4e8f2'):
 c.d.polygon(points,fill=fill);c.d.line(points+[points[0]],fill=BLUE,width=4);c.bottom=max(c.bottom,max(y for x,y in points))
def plot(c,top=180,bottom=600,xmax=240,ymax=60):
 def pos(z,r):return (150+z/xmax*800,(top+bottom)/2-r/ymax*(bottom-top)/2)
 c.line(pos(-20,0),pos(xmax,0),'#7a8791',True)
 c.text(50,bottom+20,'光轴 z →',40)
 return pos
def ray(c,ps,color=ORANGE):
 for a,b in zip(ps,ps[1:]):c.line(a,b,color)
 c.arrow(ps[-2],ps[-1],color)
def save(c,name,purpose):c.save(name,purpose)

c=Canvas('Fresnel：把厚度让给方向')
P=plot(c,180,680)
for j,r in enumerate([-50,-30,-10,10,30,50]):
 c.line(P(0,r-4),P(0,r+4),BLUE)
 ray(c,[P(-20,r),P(0,r),P(D['model']['f'],0)],C[j%5])
c.line(P(0,-55),P(0,55),BLUE)
c.text(50,770,'一圈斜面，负责一束光的去向',44)
c.text(50,840,'原创薄元件模型｜实物另看来源',40)
save(c,'00-cover.png','独立封面：各高度光线向同一焦点转向')

c=Canvas('先分环，再移近：方向没有旋转')
# Conceptual radial cut: r to right, optical z down. Preserve each slope.
for i,label in enumerate(['连续曲面：各处有各处的斜率','切成环带：保留每段内部的曲率','削去多余材料，曲面段移到共同基底']):
 y=150+i*410;c.text(50,y,label,42)
 for j,segment in enumerate(D['conceptual_segments']):
  gap=7 if i==1 else 0
  x=150+j*(145+gap);width=145
  shift=segment[0]['sag'] if i==2 else 0
  floor=80 if i==2 else 230
  top=[(x+(q['r']-segment[0]['r'])*width,y+100+(q['sag']-shift)*6) for q in segment]
  pts=top+[(x+width,y+100+floor),(x,y+100+floor)]
  poly(c,pts)
  if i==1:c.line((x,y+90),(x,y+335),ORANGE,True)
  if i==2:c.arrow((x+60,y+300),(x+60,y+215),GREEN)
 c.text(50,y+345,'半径向右，光轴向下；移位不旋转',40)
c.text(50,1420,'绿箭头：平移；尺寸和坡度不按比例',40)
save(c,'01-steps.png','连续面分区、分离、平移的三步概念图；不表示实际光程不变')

c=Canvas('折射看法线，不看剩下多少玻璃')
# local tangent normal diagram: z to right; radial +r up.
a=math.radians(D['rays'][4]['alpha_deg']);b=math.radians(D['rays'][4]['beta_deg']);t=b-a
O=(530,440)
poly(c,[(150,180),(O[0]+150*math.sin(a),O[1]-150*math.cos(a)),(O[0]-150*math.sin(a),O[1]+150*math.cos(a)),(150,700)])
ray(c,[(180,440),O,(930,440+400*math.tan(t))],ORANGE)
c.line((O[0]-250*math.cos(a),O[1]+250*math.sin(a)),(O[0]+280*math.cos(a),O[1]-280*math.sin(a)),GREEN,True)
c.text(80,105,f"内部光沿 +z；上半孔径 r = {Q['r']} mm",40)
c.text(650,230,'法线向外倾',40,GREEN)
c.line(O,(980,440),'#7a8791',True)
c.text(925,370,'+z',40)
for radius,start,end,color in [(115,-math.degrees(a),0,GREEN),(175,0,math.degrees(t),ORANGE),(245,-math.degrees(a),math.degrees(t),'#7d3c86')]:
 c.d.arc((O[0]-radius,O[1]-radius,O[0]+radius,O[1]+radius),start,end,fill=color,width=5)
c.text(75,730,f"α = {Q['alpha_deg']:.3f}°（内部光到法线）",40,GREEN)
c.text(75,795,f"β = {Q['beta_deg']:.3f}°（法线到出射光）",40,'#7d3c86')
c.text(75,860,f"向轴偏转 θ = β − α = {Q['theta_deg']:.3f}°",40,ORANGE)
c.text(75,940,'橙：光线　绿虚线：法线',40)
save(c,'02-snell.png','同一r40光线的入射角、出射角与向轴偏转角')

c=Canvas('同一焦点，需要逐圈变陡')
P=plot(c,190,630)
for i,row in enumerate(D['rays'][1:]):
 r=row['r'];ray(c,[P(-20,r),P(0,r),P(D['model']['f'],0)],C[i])
 c.d.ellipse((P(0,r)[0]-6,P(0,r)[1]-6,P(0,r)[0]+6,P(0,r)[1]+6),fill=C[i])
c.text(50,740,'所有出射点暂压在 z = 0 参考面',40)
c.text(50,810,'r / mm       所需法线角 α',42)
for i,row in enumerate(D['rays'][1:]):c.text(80,880+65*i,f"{row['r']:2}                 {row['alpha_deg']:.3f}°",40,C[i])
c.text(50,1240,f'焦点 (z, r) = ({F:g}, 0) mm',42)
save(c,'03-rays.png','半径越大所需转向越大；逐半径实际Snell计算')

c=Canvas('同角度，不等于同一个落点')
P=plot(c,200,650,xmax=230,ymax=50)
r=40;dz=D['translation']['delta_z'];err=D['translation']['delta_hit']
# shift exaggerated, explicit in caption
ray(c,[P(0,r),P(F,0)],BLUE)
ray(c,[P(20,r),P(F+20,0)],ORANGE)
c.line(P(F,-18),P(F,45),GREEN,True)
c.text(610,150,f'z={F:g} mm 焦面',40,GREEN)
c.text(50,740,'蓝：原出射点　橙：沿轴移过',40)
c.text(50,810,'两线平行，穿过焦面的地方不同',40)
c.text(50,880,f'实际平移 {dz:g} mm → 偏移 {err:.3f} mm',40)
c.text(50,950,'图把平移放大，便于辨认',40)
save(c,'04-translation.png','反例：保留局部法线仅保方向，轴向位置改变仍会改变截点')

c=Canvas('球面切薄，也不会自动消除球差')
P=plot(c,200,650)
for i,row in enumerate(D['sphere']):ray(c,[P(-20,row['r']),P(0,row['r']),P(row['focus'],0)],C[i])
c.text(50,740,f"球面半径 {D['model']['sphere_radius']:g} mm，仍用 n = {D['model']['n']}",40)
for i,row in enumerate(D['sphere']):c.text(50,815+i*70,f"r = {row['r']:2} mm → 交轴 z = {row['focus']:.2f} mm",40,C[i])
c.text(50,1050,'仍压在同一参考面；非厚球面追迹',40)
save(c,'05-sphere.png','另一个明确曲面模型：同近轴焦距不保证边缘焦点相同')

c=Canvas('一圈只用一个斜率：落点就有范围')
# 10mm annulus 30 to40, midpoint35
zone=D['pitches'][0]['zones'][3]
for j,q in enumerate(zone['rays'][::5]):
 a0=(150,600-(q['r']-zone['low'])*25);end=(900,600-q['hit']*25)
 ray(c,[a0,end],C[j])
c.line((900,260),(900,760),'#7d3c86')
c.text(600,180,f'z={F:g} mm 焦面',40,'#7d3c86')
c.text(50,110,'同槽三条光线平行，图为局部展开',40)
c.text(50,820,f"环带 {zone['low']:g}～{zone['high']:g} mm，以中点设计",40)
c.text(50,890,'实际焦面残差 = r − 环带中点',40)
for j,q in enumerate(zone['rays'][::5]):c.text(60,970+j*65,f"r = {q['r']:g} mm → 残差 {q['hit']:+.1f} mm",40,C[j])
save(c,'06-zone.png','一条平斜面内光束不能全交一点；残差由实跑算出')

c=Canvas('槽距变小：几何散布随之变窄')
maxhit=max(q['max_abs_hit'] for q in D['pitches']);scale=350/maxhit
for i,q in enumerate(D['pitches']):
 y=190+i*260;v=q['max_abs_hit'];c.text(50,y,f"槽距 {q['pitch']:g} mm，最大偏离 {v:g} mm",42)
 c.line((530-maxhit*scale,y+130),(530+maxhit*scale,y+130),'#7a8791')
 c.line((530-v*scale,y+130),(530+v*scale,y+130),C[i])
 for x in [530-v*scale,530+v*scale]:c.line((x,y+100),(x,y+160),C[i])
 c.line((530,y+90),(530,y+170),INK)
 c.text(150,y+175,f'−{maxhit:g}',40);c.text(518,y+175,'0',40);c.text(840,y+175,f'+{maxhit:g} mm',40)
assert all(abs(x['max_abs_hit']-x['pitch']/2)<1e-10 for x in D['pitches'])
c.text(50,1020,'只计单色几何分段，不含衍射和槽壁',40)
save(c,'07-pitch.png','共轴绘出不同槽距产生的焦面径向几何残差范围')

c=Canvas('更密，也意味着更多槽缘')
for i,q in enumerate(D['pitches']):
 y=190+i*240;p=q['pitch'];frac=q['dead_fraction'];c.text(50,y,f"槽距 {p:g} mm；假设槽缘宽 {D['model']['dead_width']:g} mm",40)
 poly(c,[(100,y+100),(900,y+100),(900,y+150),(100,y+150)],'#d4e8f2')
 c.d.rectangle((100,y+100,100+800*frac,y+150),fill=ORANGE)
 c.text(50,y+165,f'局部径向坏区比例 ≈ {frac*100:g}%',40,ORANGE)
c.text(50,970,'仅假设性占比，非圆孔径总功率损失',40)
c.text(50,1040,'真实槽缘有圆角、壁斜度、遮挡和散射',40)
save(c,'08-edges.png','槽缘宽度固定时的局部占比反例，非实机效率')

c=Canvas('折射率改变，原来的坡度不再合适')
P=plot(c,200,650,xmax=225,ymax=50)
for i,q in enumerate(D['colors']):ray(c,[P(0,40),P(q['focus'],0)],['#a62d49',GREEN,BLUE][i])
c.text(50,740,f"同一斜面：α = {Q['alpha_deg']:.3f}°；r = {Q['r']} mm",40)
for i,q in enumerate(D['colors']):c.text(50,815+i*75,f"n = {q['n']:.2f} → 交轴 {q['focus']:.2f} mm",40,['#a62d49',GREEN,BLUE][i])
c.text(50,1080,'折射率为教学假设；不是某种塑料曲线',40)
save(c,'09-dispersion.png','固定斜面、改变n的实际重算，分清材料色散与阶梯')

c=Canvas('薄了以后，两个表面仍会反光')
vals=[]
for i,q in enumerate(D['loss']):
 y=190+i*230;v=q['two_surface_transmit'];vals.append(v)
 c.text(50,y,f"r = {q['r']:g} mm：两面直透 {100*v:.2f}%",42)
 c.d.rectangle((110,y+105,910,y+160),fill='#d8dce1')
 c.d.rectangle((110,y+105,110+800*v,y+160),fill=BLUE)
 c.bottom=max(c.bottom,y+160)
c.text(50,930,'横条统一：0% 至 100%',40)
c.text(50,1000,'未镀膜、无吸收、非偏振、只算首程',40)
c.text(50,1070,'未加入槽壁、表面粗糙度与接收孔径',40)
assert sorted(range(3),key=lambda i:vals[i])==sorted(range(3),key=lambda i:800*vals[i])
save(c,'10-loss.png','用实际界面Fresnel反射公式核双表面首程透过率')

c=Canvas('把光路倒过来：焦点也能送出平行光')
for k in range(2):
 P=plot(c,200+600*k,580+600*k)
 for i,r in enumerate([-40,-20,20,40]):
  ps=[P(-20,r),P(0,r),P(F,0)]
  ray(c,ps if k==0 else ps[::-1],C[i])
 c.text(50,710+600*k,'平行光 → 焦点' if k==0 else '焦点小光源 → 平行光',44)
c.text(50,1400,'可逆的是同一条理想路径；灯丝有面积',40)
save(c,'11-reverse.png','同一路径的聚光与准直互逆，灯塔目标与聚光相连')

c=Canvas('收进一个孔，与看清一幅图不同')
# paraxial image geometry with same f; scaled horizontal distances
u=D['finite_object']['u'];v=D['finite_object']['v'];m=D['finite_object']['magnification']
left,center=80,760;right=center+(center-left)*v/u;axis=420;obj=160;img=obj*abs(m)
c.line((50,axis),(1010,axis),'#7a8791',True)
c.arrow((left,axis),(left,axis-obj),GREEN)
c.arrow((right,axis),(right,axis+img),ORANGE)
c.line((center,180),(center,650),BLUE)
ray(c,[(left,axis-obj),(center,axis-obj),(right,axis+img)],ORANGE)
ray(c,[(left,axis-obj),(center,axis),(right,axis+img)],GREEN)
c.text(50,720,f'物距 {u:g} mm → 像距 {v:g} mm',42)
c.text(50,790,f"近轴放大率 {m:g}；{D['finite_object']['source_width']:g} mm 对应 {D['finite_object']['paraxial_image_width']:g} mm",40)
c.text(50,860,'不同物点必须各自落在不同像点',40)
c.text(50,930,'几何图纵向放大；薄透镜近轴近似',40)
save(c,'12-imaging.png','有限物距例子解释成像需要点到点对应，不只是总收光')

c=Canvas('正面是一圈，切开才看见工作面')
selected=D['pitches'][0]['zones'][3]
center=(530,425);scale=5;outer=selected['high']*scale;inner=selected['low']*scale
c.d.ellipse((center[0]-outer,center[1]-outer,center[0]+outer,center[1]+outer),fill='#d4e8f2')
c.d.ellipse((center[0]-inner,center[1]-inner,center[0]+inner,center[1]+inner),fill='#f8fafc')
for zone in D['pitches'][0]['zones']:
 radius=zone['high']*scale
 c.d.ellipse((center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius),outline=BLUE,width=4)
c.line(center,(center[0]+D['model']['radius']*scale,center[1]),ORANGE)
c.text(50,110,'正面：同心环带；橙线为径向截线',40)
c.text(50,730,f"蓝底选中 {selected['low']:g}～{selected['high']:g} mm 那一圈",40)
c.text(50,820,'局部截面：两条固定斜率工作面',40)
for j,zone in enumerate(D['pitches'][0]['zones'][3:5]):
 x=210+j*300;depth=zone['depth']*28
 c.line((x,930),(x+300,930+depth),BLUE)
 c.line((x+300,930+depth),(x+300,930),ORANGE)
c.text(50,1140,'蓝斜线：工作面　橙竖线：槽壁',40)
c.text(50,1210,'径向与槽高分别缩放，不是加工图',40)
save(c,'13-ring-section.png','同心环正面与局部工作面/槽壁截面的身份对应')

# Photographs are unmodified, separate GPL source files; never rasterized here.
from PIL import Image
for path in sorted((ROOT/'originals/photos').glob('*.jpg')):
 im=Image.open(path)
 meta.append(dict(file=str(path.relative_to(ROOT)),width=im.width,height=im.height,min_font_px=None,identity='June Glasses 第一方项目原照片；GPL v3；字节未修改',purpose='实物、装配或相机记录的光学效果，详见图注',checks=['original-bytes-kept','actual-dimensions'],font_exception='原照片内固有内容，不是原创教学标注'))

(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('Wrote',len(meta),'figures')
