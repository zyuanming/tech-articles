#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original weaving/selection diagrams; historical image transforms recorded separately."""
from pathlib import Path
import json,math,shutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'assets';A.mkdir(exist_ok=True);O=ROOT/'originals';M=json.loads((ROOT/'examples/model-cards.json').read_text())
W=1062;BG='#f5f1e7';INK='#293c44';TEAL='#16788c';GOLD='#c98a39';RED='#ae5060';GRAY='#6e7775';LIGHT='#d5dad5';PAPER='#e0c89a'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc';meta=[]
def font(s=42,b=False):return ImageFont.truetype(BOLD if b else FONT,s,index=2)
def text(x,y,t,s=42,c=INK,b=False,anchor=None):
 global smallest
 smallest=min(smallest,s);d.text((x,y),str(t),font=font(s,b),fill=c,anchor=anchor)
def line(pts,c=INK,w=6):d.line(pts,fill=c,width=w)
def arrow(x1,y1,x2,y2,c=TEAL,w=6):
 line([(x1,y1),(x2,y2)],c,w);an=math.atan2(y2-y1,x2-x1);d.polygon([(x2,y2),(x2-18*math.cos(an-.5),y2-18*math.sin(an-.5)),(x2-18*math.cos(an+.5),y2-18*math.sin(an+.5))],fill=c)
def dot(x,y,c=TEAL,r=15):d.ellipse((x-r,y-r,x+r,y+r),fill=c)
def new(title,h=1100,sub=None):
 global im,d,smallest
 smallest=99;im=Image.new('RGB',(W,h),BG);d=ImageDraw.Draw(im);d.rectangle((0,0,16,h),fill=TEAL);text(48,31,title,52,b=True)
 if sub:text(48,112,sub,38,c=GRAY)
def save(n,purpose,identity='Original explanatory diagram; not a loom measurement'):
 im.save(A/(n+'.png'));meta.append(dict(file='assets/'+n+'.png',purpose=purpose,identity=identity,width=W,height=im.height,minimum_font_px=smallest,effective_minimum_at_354px=smallest/3))
def photo(name,source,width=1062,crop=None,purpose='',identity='Real museum image; no generative retouching'):
 src=Image.open(O/source).convert('RGB');original_size=src.size
 if crop:src=src.crop(crop)
 if width!=src.width:src=src.resize((width,round(src.height*width/src.width)),Image.Resampling.LANCZOS)
 
 if source.startswith('posselt-') and crop is None and width==original_size[0]:shutil.copyfile(O/source,A/(name+'.jpg'))
 else:src.save(A/(name+'.jpg'),quality=94,subsampling=0)
 meta.append(dict(file='assets/'+name+'.jpg',purpose=purpose,identity=identity,source='originals/'+source,source_size=original_size,crop_xyxy=crop,width=src.width,height=src.height))
def paste_history(name,x,y,maxw,maxh):
 global d
 src=Image.open(O/name).convert('RGB');k=min(maxw/src.width,maxh/src.height);src=src.resize((round(src.width*k),round(src.height*k)),Image.Resampling.LANCZOS);im.paste(src,(int(x+(maxw-src.width)/2),int(y)));d=ImageDraw.Draw(im)
def weave(cards,x,y,cell=95,labels=True):
 # Cell means one warp/weft crossing, not a colored pixel painted onto cloth.
 n=len(cards);w=8*cell;h=n*cell
 for j in range(8):
  xx=x+(j+.5)*cell;line([(xx,y),(xx,y+h)],TEAL,round(cell*.40))
 for i,card in enumerate(cards):
  yy=y+(i+.5)*cell;line([(x,yy),(x+w,yy)],GOLD,round(cell*.40))
  for j,b in enumerate(card):
   if b=='1':
    xx=x+(j+.5)*cell;line([(xx,yy-cell*.40),(xx,yy+cell*.40)],TEAL,round(cell*.40))
 if labels:
  for j in range(8):text(x+(j+.5)*cell,y-65,j+1,38,anchor='mt')
  for i in range(n):text(x-20,y+(i+.5)*cell,str(i+1),38,anchor='rm')

def card(bits,x,y,cell=105,number=True):
 d.rounded_rectangle((x,y,x+8*cell,y+150),radius=12,fill=PAPER,outline=GRAY,width=3)
 for j,b in enumerate(bits):
  xx=x+(j+.5)*cell
  if b=='1':dot(xx,y+75,BG,23);d.ellipse((xx-23,y+52,xx+23,y+98),outline=GRAY,width=3)
  else:d.ellipse((xx-23,y+52,xx+23,y+98),outline='#bba778',width=2)
  if number:text(xx,y-59,j+1,38,anchor='mt')

photo('01-real-woven-portrait','met-222531-DP109795.jpg',purpose='真实1839丝织肖像作为问题起点；画面内的卡片和机器是织成的图像，不是实物照片')
new('布，不是把两组线摆在一起',1120,'蓝色经线沿布长方向；金色纬线横过布幅')
weave((M['plain_cards']*3),180,280,88)
text(48,932,'交叉处谁盖住谁，决定这一小处露出哪组线。',40)
text(48,1010,'图为交织关系示意；没有模拟丝线粗细与光泽。',38)
save('02-weave-crossings','先识别经纬两方向与交点上下关系，建立蓝经金纬约定')

new('抬起一部分经线，梭子就有路可走',1390,'上图沿经线方向看；圆点表示经线的截面')
for j in range(8):
 xx=155+j*106;text(xx,219,j+1,40,anchor='mt');line([(xx,292),(xx,646)],LIGHT,2);dot(xx,337 if j%2==0 else 629,TEAL,21)
arrow(95,490,970,490,GOLD,8)
d.polygon([(360,490),(404,457),(576,457),(620,490),(576,523),(404,523)],fill='#edc990',outline=GOLD)
d.ellipse((455,470,525,510),outline=GOLD,width=5);text(660,529,'梭子携带纬线',40,c=GOLD)
text(48,704,'上下两层之间的通道，叫梭口。',44,b=True)
text(48,827,'换成俯视：这一纬穿过去以后',44,b=True)
weave([M['plain_cards'][0]],120,999,105,labels=True)
text(48,1211,'1、3、5、7号经线在这一纬上面。',42,b=True)
text(48,1289,'只是观察方向改变，仍然是同 8 根经线。',38)
save('03-shed-and-pick','端视梭口与俯视同一纬对应，解释提升选择的实际用途')

photo('04-real-double-loom','getty-107VAW-double-jacquard-1851.jpg',crop=(500,1700,5150,7520),purpose='1851双式提花织机真实照片，显示高位控制机构、悬垂绳束、下方织机及卡链')
new('一张卡，先记下这次抬哪些线',1170,'教学缩减：把 8 个控制位展开成一排')
card(M['plain_cards'][0],111,302)
text(48,520,'有孔记 1；没孔记 0。这里只是今天的记法。',39)
for j,b in enumerate(M['plain_cards'][0]):
 xx=163.5+j*105;text(xx,621,b,51,b=True,anchor='mt');arrow(xx,715,xx,806,TEAL if b=='1'else GRAY);dot(xx,852 if b=='1'else 985,TEAL if b=='1'else GRAY,22)
text(48,1065,'抬起：1、3、5、7；留低：2、4、6、8。',43,b=True)
save('05-card-eight-choices','单次8位教学卡与经线身份对应，孔只是选择信息')
photo('06-historical-needle-hooks','posselt-1888-i_014a.jpg',width=393,identity='Public-domain historical technical illustration, native-size verbatim copy',purpose='Posselt1888原图VII：横针、竖钩、上部提升刀与右侧弹簧的真实历史结构图')

# All positions below follow the primary cross-section: card/needle tips left, springs right.
def read_case(top,hole):
 shift=0 if hole else 60;mid=top+275;hx=480+shift;col=TEAL if hole else RED
 text(48,top,'有孔：针进入，钩仍对准刀'if hole else'没孔：针被顶回，钩偏离刀',44,b=True,c=col)
 # A card section at the right face of a recess. Thickness and deflection exaggerated.
 d.rectangle((175,top+145,260,top+439),fill='#bfbcb2')
 d.rectangle((243,top+145,260,top+439),fill=PAPER)
 if hole:d.rectangle((175,mid-22,262,mid+22),fill=BG)
 # Lower hook bends elastically; only its upper region is displaced by the needle eye.
 line([(480,top+510),(hx,mid),(hx,top+90),(hx-40,top+90),(hx-40,top+119)],col,12)
 d.rectangle((454,top+137,470,top+166),fill=GOLD)
 text(200,top+91,'提升刀',37,c=GOLD)
 arrow(337,top+151,443,top+151,GOLD,3)
 # Horizontal needle with an eye surrounding the hook wire.
 line([(200+shift,mid),(hx-18,mid)],INK,7);d.ellipse((hx-18,mid-18,hx+18,mid+18),outline=INK,width=6);line([(hx+18,mid),(840+shift,mid)],INK,7)
 pts=[(840+shift,mid)]
 for k in range(17):pts.append((840+shift+(960-840-shift)*(k+1)/18,mid+(15 if k%2 else-15)))
 pts.append((960,mid));line(pts,GRAY,4);line([(970,mid-50),(970,mid+50)],GRAY,8)
 text(627,mid-78,'横针',40,b=True);text(825,mid+51,'弹簧',38,c=GRAY)
 text(66,top+480,'卡筒与卡片',36);text(530,top+484,'竖钩下端',36,c=col)
 if not hole:arrow(627,mid+93,754,mid+93,RED,5);text(620,mid+121,'被推向右',36,c=RED)
new('孔不抬线：它先决定针能不能穿过',1580,'简化侧视；针横向选钩，钩才准备向上移动')
text(48,171,'灰块是卡筒局部；右缘米黄色薄层是卡片。',37,c=GRAY)
read_case(247,True);read_case(896,False)
text(48,1500,'纸厚、间距与偏移均夸大；不是按尺寸复刻。',38)
save('07-hole-or-solid','按同一方向展示孔让针通行、实部推针并让钩错开提升刀')

new('刀架上升，只带走已经对准的钩',1270,'提升初段的快照；卡筒正在向外退开')
for xx,selected,title in[(320,True,'此前有孔'),(756,False,'此前没孔')]:
 text(xx,214,title,45,b=True,anchor='mt',c=TEAL if selected else GRAY)
 knife=352;hy=knife-6 if selected else 480;bottom=780 if selected else 914
 stem=xx+26+(0 if selected else 60)
 line([(stem,bottom),(stem,hy),(stem-49,hy),(stem-49,hy+35)],TEAL if selected else GRAY,13)
 d.rectangle((xx-6,knife,xx+17,knife+35),fill=GOLD)
 arrow(xx+120,knife+120,xx+120,knife-12,GOLD,6)
 line([(stem,bottom),(stem,bottom+70)],TEAL,5)
text(48,1060,'灰钩仍被推偏，留在低处；本图不展开复位。',39)
text(48,1145,'卡筒退离与刀架上升会重叠，不是逐件停顿。',38)
save('08-lift-selected-hooks','抓取位置与刀架上升后的因果；明确退卡和上升并非严格串行')

new('钩抬起来以后，经线为什么也会动？',1160,'只放大 1 条通道：钩 → 绳 → 综眼 → 经线')
line([(462,264),(462,211),(411,211),(411,246)],INK,12)
line([(462,264),(462,485)],GRAY,7);text(565,308,'连接绳',43);arrow(550,350,479,350,GRAY,3)
d.ellipse((432,482,492,606),outline=INK,width=8)
line([(145,666),(462,546),(910,666)],TEAL,13)
line([(462,606),(462,817)],GRAY,6);d.rounded_rectangle((442,817,482,996),radius=10,fill=GRAY)
text(580,468,'经线穿过小孔',42,b=True,c=TEAL);text(580,528,'这个孔叫综眼',40)
arrow(553,551,500,549,TEAL,3);text(550,844,'下方配重',42);text(550,905,'维持向下拉力',38,c=GRAY)
arrow(273,481,273,335,TEAL,8);text(48,1046,'向上拉绳，综眼升高，经线也被托起来。',42,b=True)
save('09-hook-to-thread','经线经过综眼而非系死在钩上，配重和连接绳的作用')

new('真实卡筒有平面；卡片串成一条链',1040,'1888 年技术书中的原图，下面保留原结构')
text(48,213,'原图 IX：四棱卡筒',43,b=True);paste_history('posselt-1888-i_016.jpg',60,294,945,220)
text(48,594,'原图 XV：相连卡片（省略了图案孔）',42,b=True);paste_history('posselt-1888-i_018a.jpg',160,687,740,260)
text(48,969,'大定位孔、串卡孔和选择针孔不是同一种用途。',37)
save('10-cylinder-and-chain','原书实证四棱承卡面和串卡；原图XV没有画图案孔','Public-domain Posselt1888 Figs IX,XV; resized and paired with Chinese labels')

new('先退离针尖，再换到下一面',1490,'四面卡筒的简化端视；实际连杆动作会重叠')
text(48,171,'端视只标一个通行孔，省略实际针孔阵列。',37,c=GRAY)
for top,num,cx,labels,title in[(250,1,365,['B','A','D','C'],'① 当前卡 A 对着针'),(635,2,225,['B','A','D','C'],'② 退开，针尖不再插着卡'),(1020,3,225,['C','B','A','D'],'③ 转 1/4 圈，B 成为下一张')]:
 text(48,top,title,44,b=True);cy=top+200;r=92
 d.rectangle((cx-r,cy-r,cx+r,cy+r),fill=PAPER,outline=GRAY,width=5)
 d.rectangle((cx+r-31,cy-14,cx+r+3,cy+14),fill=BG)
 for lab,(dx,dy)in zip(labels,[(0,-55),(55,-25),(0,55),(-55,0)]):text(cx+dx,cy+dy,lab,40,b=True,anchor='mm')
 line([(430,cy),(939,cy)],INK,7);text(695,cy+48,'针尖在左端',37,c=GRAY)
 if num==2:arrow(380,cy+103,260,cy+103,TEAL,7)
 if num==3:
  d.arc((cx-r-48,cy-r-48,cx+r+48,cy+r+48),250,345,fill=TEAL,width=6);arrow(cx+r+46,cy-35,cx+r+35,cy+2,TEAL,5)
text(48,1410,'再靠近针板，开始下一次选择；链不止四张。',39)
save('11-advance-cards','侧面读卡、退出针尖后分度，卡筒四面不等于只容四张卡')

photo('12-real-card-chain','getty-107VAW-double-jacquard-1851.jpg',crop=(3050,2750,4700,4500),purpose='同一1851真实照片右侧卡链局部；与书中卡链示意对照，不把织物中画出的卡当实物')
new('四张卡，四次引纬；接着再循环',1500,'列是 8 根经线；行是引纬时间，按上到下排列')
for i,bits in enumerate(M['twill_cards']):
 text(70,218+i*99,f'{i+1}',40,b=True);text(154,218+i*99,bits,48,b=True,c=TEAL)
 text(655,225+i*99,'抬起 '+','.join(str(j+1)for j,b in enumerate(bits)if b=='1'),36)
text(48,662,'把同 4 张卡重复两轮，得到下面的交织关系：',39)
weave(M['twill_cards']*2,233,806,75,labels=True)
text(48,1437,'交点的蓝色带逐行移动，形成这块小斜纹。',39)
save('13-four-cards-weave','8位卡序列逐纬映射到交织，四张卡重复两次形成8纬')

new('一只钩，也能带动多个重复位置',1440,'左为 1888 年原图 XXV；右为只画一钩的简化')
paste_history('posselt-1888-i_024.jpg',42,247,411,705)
line([(734,350),(734,289),(695,289),(695,322)],INK,10);line([(734,350),(734,495)],GRAY,6)
for xx,lab in[(570,'I'),(751,'II'),(932,'III')]:
 line([(734,495),(xx,705)],GRAY,5);d.ellipse((xx-18,705,xx+18,787),outline=GRAY,width=6)
 line([(xx-50,807),(xx,746),(xx+48,807)],TEAL,7);text(xx,865,lab,42,b=True,anchor='mt')
text(530,998,'同一位置，跨布幅重复三份。',37)
text(48,1140,'钩一动，这三处一起动；它们不能独立选。',42,b=True)
text(48,1225,'这里已换成“三重复穿综”例子，',39)
text(48,1296,'不是前面 8 根线模型多出了隐藏的独立指令。',38)
save('14-one-hook-repeats','连接映射决定一钩多线及重复图案的代价','Posselt1888 FigXXV resized plus original one-hook three-repeat sketch')

new('卡能执行，不等于布一定织得牢',1160,'下面让 8 根经线连续 6 纬全部抬起')
weave(['11111111']*6,180,275,88)
text(48,934,'每处都是蓝经线在上，金纬线从下面经过。',40)
text(48,1004,'两组线没有在这些交点轮流上下交织。',40)
text(48,1071,'真实设计还要处理组织、浮长、密度与张力。',37)
save('15-float-limit','全1卡串可以选线却不能自动保证交织结构，限制像素类比')

new('从画一片叶子，到安排真正的交织',1640,'1888 年原书的设计过程；都是历史插图，不是照片')
for x,y,name,lab in[(48,250,'i_115','89：叶形草图'),(561,250,'i_115a','90：方格轮廓'),(48,901,'i_115b','91：加入组织点'),(561,901,'i_116','92：织物效果示意')]:
 text(x,y-67,lab,39,b=True);paste_history('posselt-1888-'+name+'.jpg',x,y,450,500)
text(48,1517,'“画出外形”之后，还要决定纱线如何交错。',40)
save('16-historic-design-stages','原书四阶段区分外轮廓、组织设计与效果；未冒称实物照片','Public-domain Posselt1888 Appendix Figs89–92, resized and arranged; original files retained')

# Same textile, closer view. This is neither an additional textile nor a generated texture.
photo('17-real-weave-detail','met-222531-DP109795.jpg',crop=(925,770,1845,1690),purpose='开篇同一1839织物的局部细看；不补出原件没有的纱线细节')
new('打孔卡，怎样让织机织出花纹？',780,'把“抬哪几根线”的顺序，放进一串可更换的卡')
card(M['twill_cards'][0],111,252,number=False);weave(M['twill_cards'],252,482,70,labels=False)
im.save(ROOT/'cover.png')
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('Body figures:',len(meta),'cover:1')
