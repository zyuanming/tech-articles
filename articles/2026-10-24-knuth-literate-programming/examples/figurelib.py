"""Original figure primitives, CC BY 4.0. No downloaded graphics."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math,json
FONT=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
if not FONT.exists(): raise RuntimeError('Chinese font missing')
INK='#163047'; BLUE='#1763a6'; ORANGE='#b54812'; TEAL='#087b78'; GRAY='#65727d'; BG='#ffffff'; LIGHT='#e9f2fa'
COLORS=[BLUE,TEAL,ORANGE,'#7452a1','#556b2f']
class Board:
 def __init__(self,title,w=840):
  self.w=w; self.im=Image.new('RGB',(w,4000),BG); self.d=ImageDraw.Draw(self.im); self.items=[]; self.bottom=0; self.fonts=[]
  self.text(32,25,title,40); self.line((32,91,w-32,91),BLUE,3)
 def text(self,x,y,s,size=36,fill=INK,anchor='la',inside=None):
  s=str(s); f=ImageFont.truetype(str(FONT),size)
  for ch in set(s)-set(' \n'):
   assert f.getmask(ch).getbbox(),f'empty glyph {ch!r}'
  bb=self.d.textbbox((x,y),s,font=f,anchor=anchor)
  assert bb[0]>=0 and bb[2]<=self.w and bb[1]>=0 and bb[3]<4000, (s,bb)
  if inside:
   assert bb[0]>=inside[0]+4 and bb[2]<=inside[2]-4 and bb[1]>=inside[1]+4 and bb[3]<=inside[3]-4,(s,bb,inside)
  for old,ss in self.items:
   assert bb[2]<=old[0] or bb[0]>=old[2] or bb[3]<=old[1] or bb[1]>=old[3],('text overlap',s,ss,bb,old)
  self.d.text((x,y),s,font=f,fill=fill,anchor=anchor)
  self.items.append((bb,s)); self.fonts.append(size); self.bottom=max(self.bottom,bb[3])
 def box(self,rect,label=None,size=36,fill=LIGHT,outline=BLUE):
  assert 0<=rect[0]<rect[2]<=self.w and 0<=rect[1]<rect[3]<4000,('box bounds',rect)
  self.d.rounded_rectangle(rect,12,fill=fill,outline=outline,width=3); self.bottom=max(self.bottom,rect[3])
  if label is not None:self.text((rect[0]+rect[2])/2,(rect[1]+rect[3])/2,label,size,anchor='mm',inside=rect)
 def line(self,xy,fill=GRAY,width=4):
  self.d.line(xy,fill=fill,width=width); self.bottom=max(self.bottom,max(xy[1::2]))
 def arrow(self,start,end,fill=BLUE,width=5):
  self.line((*start,*end),fill,width); a=math.atan2(end[1]-start[1],end[0]-start[0]); r=14
  p=[end,(end[0]-r*math.cos(a-.5),end[1]-r*math.sin(a-.5)),(end[0]-r*math.cos(a+.5),end[1]-r*math.sin(a+.5))]
  self.d.polygon(p,fill=fill)
 def circle(self,x,y,r,label=None,fill=LIGHT,outline=BLUE):
  self.d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=outline,width=3); self.bottom=max(self.bottom,y+r)
  if label:self.text(x,y,label,36,anchor='mm')
 def save(self,p,purpose,identity='原创教学示意'):
  p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);h=math.ceil(self.bottom+30);self.im=self.im.crop((0,0,self.w,h));self.im.save(p)
  for bb,s in self.items:
   region=self.im.crop(bb).convert('L'); lo,hi=region.getextrema();assert hi-lo>=45,('contrast',s)
   assert sum(1 for v in region.getdata() if v<180)>5,('pixels',s)
  return {'file':str(p.name),'width':self.w,'height':h,'min_font_px':min(self.fonts),'effective_font_at_354':round(min(self.fonts)*354/self.w,2),'identity':identity,'purpose':purpose,'geometry_and_pixel_checks':True}
def rows(title,items,cols=None):
 b=Board(title); y=125
 for i,(label,value) in enumerate(items):
  b.text(35,y,label);b.box((350,y-4,800,y+57),str(value),fill='#eef5f9');y+=90
 return b
