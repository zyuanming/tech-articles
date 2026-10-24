"""Original reproducible teaching figure helper, CC BY 4.0. Pillow only."""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont
W=960
INK='#172c3c'; BLUE='#1765a0'; ORANGE='#bb521d'; TEAL='#087b78'; GRAY='#687784'; BG='#fffdf7'
FONT=next((p for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf'] if Path(p).exists()),None)
if not FONT: raise RuntimeError('Chinese font required')
class Fig:
 def __init__(self,title,h=800):
  self.im=Image.new('RGB',(W,h),BG);self.d=ImageDraw.Draw(self.im);self.boxes=[];self.sizes=[];self.bottom=0
  self.text(45,32,title,48)
 def text(self,x,y,s,size=42,color=INK):
  f=ImageFont.truetype(FONT,size);box=self.d.textbbox((x,y),str(s),font=f)
  assert box[0]>=0 and box[2]<=W and box[1]>=0 and box[3]<=self.im.height,(s,box)
  for old,txt in self.boxes:
   assert min(box[2],old[2])<=max(box[0],old[0]) or min(box[3],old[3])<=max(box[1],old[1]),('overlap',s,txt)
  self.d.text((x,y),str(s),font=f,fill=color);self.boxes.append((box,str(s)));self.sizes.append(size);self.bottom=max(self.bottom,box[3])
  # Per-label non-background pixel evidence; font cmap check is performed below.
  crop=self.im.crop(box);assert sum(p!=(255,253,247) for p in crop.getdata())>5
 def line(self,pts,color=GRAY,width=4):
  self.d.line(pts,fill=color,width=width);self.bottom=max(self.bottom,max(y for x,y in pts))
 def poly(self,pts,color='#dcebf2'):
  self.d.polygon(pts,fill=color);self.bottom=max(self.bottom,max(y for x,y in pts))
 def dot(self,x,y,color=BLUE,r=9):
  self.d.ellipse((x-r,y-r,x+r,y+r),fill=color);self.bottom=max(self.bottom,y+r)
 def arrow(self,a,b,color=BLUE,width=6):
  self.line([a,b],color,width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);l=20
  self.poly([b,(b[0]-l*math.cos(ang-.45),b[1]-l*math.sin(ang-.45)),(b[0]-l*math.cos(ang+.45),b[1]-l*math.sin(ang+.45))],color)
 def rect(self,box,fill='#e7eef2',outline=GRAY):
  self.d.rectangle(box,fill=fill,outline=outline,width=3);self.bottom=max(self.bottom,box[3])
 def save(self,p,purpose):
  from fontTools.ttLib import TTFont
  font=TTFont(FONT,fontNumber=0); cmap=font.getBestCmap()
  for _,s in self.boxes:
   assert all(ord(c) in cmap or c.isspace() for c in s),('missing glyph',s)
  h=min(self.im.height,math.ceil(self.bottom+45));self.im=self.im.crop((0,0,W,h));p=Path(p);p.parent.mkdir(exist_ok=True,parents=True);self.im.save(p)
  # Dark label vs nearly-white background contrast exceeds WCAG 4.5 for all chosen label colors.
  def lum(hex):
   v=[int(hex[i:i+2],16)/255 for i in (1,3,5)];v=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v];return sum(a*b for a,b in zip(v,[.2126,.7152,.0722]))
  for c in [INK,BLUE,ORANGE,TEAL,GRAY]:assert (lum(BG)+.05)/(lum(c)+.05)>4.5
  assert min(self.sizes)>=40
  return dict(file=str(p.name),width=W,height=h,min_font_px=min(self.sizes),effective_at_354=min(self.sizes)*354/W,identity='原创模型计算或教学示意',purpose=purpose,checks=dict(bounds=True,overlap=True,font_cmap=True,pixels=True,contrast=True),labels=[s for _,s in self.boxes])
def chart(title,series,xlim,ylim,xticks,yticks,xlabel,ylabel,fill=None):
 f=Fig(title,860);X=lambda x:150+(x-xlim[0])/(xlim[1]-xlim[0])*720;Y=lambda y:650-(y-ylim[0])/(ylim[1]-ylim[0])*380
 for j,(name,points,color) in enumerate(series):
  f.text(60+j*300,118,name,40,color)
 f.text(50,183,ylabel,40)
 for x,s in xticks:
  f.line([(X(x),260),(X(x),650)],'#dce1e4',2);f.text(X(x)-15,674,s,40)
 for y,s in yticks:
  f.line([(150,Y(y)),(870,Y(y))],'#dce1e4',2);f.text(40,Y(y)-25,s,40)
 f.line([(150,260),(150,650),(870,650)],INK,4)
 if fill:
  points,col=fill;f.poly([(X(x),Y(y)) for x,y in points],col)
 for name,pts,col in series:f.line([(X(x),Y(y)) for x,y in pts],col,6)
 f.text(680,752,xlabel,40)
 return f

def rails(title,rows,limits):
 f=Fig(title,200+len(rows)*150);lo,hi=limits;X=lambda x:210+(x-lo)/(hi-lo)*620
 for j,(label,a,b,col) in enumerate(rows):
  y=180+j*150;f.text(45,y-40,label,40);f.line([(210,y+40),(830,y+40)],GRAY,3);f.line([(X(a),y+40),(X(b),y+40)],col,16);f.dot(X(a),y+40,col);f.dot(X(b),y+40,col)
  f.text(X(a)-20,y+60,f'{a:g}',40,col)
  if abs(X(b)-X(a))>100:f.text(X(b)-20,y+60,f'{b:g}',40,col)
 return f
