"""Original article diagram helper. MIT license. Geometry checks are not editorial review."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops
from fontTools.ttLib import TTFont
import math, json
FONT_CANDIDATES=['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc']
FONT=next((p for p in FONT_CANDIDATES if Path(p).exists()),None)
if not FONT: raise RuntimeError('A real Chinese font is required')
CMAP=TTFont(FONT,fontNumber=0).getBestCmap()
INK='#17324a'; BLUE='#2268a2'; ORANGE='#ad4d16'; TEAL='#14736d'; LIGHT='#eaf2f8'; BG='#ffffff'
def luminance(color):
 c=Image.new('RGB',(1,1),color).getpixel((0,0))
 v=[x/255 for x in c];v=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v]
 return sum(a*b for a,b in zip(v,[.2126,.7152,.0722]))
class Board:
 def __init__(self,width=1062,height=3000,min_font=50):
  self.im=Image.new('RGB',(width,height),BG);self.d=ImageDraw.Draw(self.im);self.w=width;self.h=height;self.minimum=min_font;self.last=0;self.labels=[];self.boxes={}
 def extent(self,b):
  self.last=max(self.last,b[3])
  if b[0]<0 or b[1]<0 or b[2]>self.w or b[3]>self.h: raise ValueError(('shape outside canvas',b))
 def line(self,points,fill=BLUE,width=5):
  self.d.line(points,fill=fill,width=width);self.extent((min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)))
 def arrow(self,a,b,fill=BLUE,width=5):
  self.line([a,b],fill,width);angle=math.atan2(b[1]-a[1],b[0]-a[0]);r=18
  self.d.polygon([b,(b[0]-r*math.cos(angle-.5),b[1]-r*math.sin(angle-.5)),(b[0]-r*math.cos(angle+.5),b[1]-r*math.sin(angle+.5))],fill=fill)
 def rect(self,b,fill=LIGHT,outline=BLUE,width=3,name=None):
  self.extent(b);self.d.rectangle(b,fill=fill,outline=outline,width=width)
  if name:self.boxes[name]=b
 def ellipse(self,b,fill=LIGHT,outline=BLUE,width=3):
  self.extent(b);self.d.ellipse(b,fill=fill,outline=outline,width=width)
 def polygon(self,points,fill=LIGHT,outline=BLUE,width=3):
  self.extent((min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)))
  self.d.polygon(points,fill=fill);self.d.line(points+[points[0]],fill=outline,width=width)
 def text(self,xy,value,size=50,fill=INK,anchor='lt',inside=None,bg=BG):
  value=str(value)
  if size<self.minimum:raise ValueError(('font too small',value,size))
  missing=[c for c in value if not c.isspace() and ord(c) not in CMAP]
  if missing:raise ValueError(('missing glyph',missing))
  font=ImageFont.truetype(FONT,size);b=self.d.textbbox(xy,value,font=font,anchor=anchor)
  self.extent(b)
  if inside:
   q=self.boxes[inside] if isinstance(inside,str) else inside
   if not(q[0]+5<=b[0] and q[1]+5<=b[1] and b[2]<=q[2]-5 and b[3]<=q[3]-5):raise ValueError(('outside declared box',value,b,q))
  for old in self.labels:
   a=old['bbox']
   if min(a[2],b[2])>max(a[0],b[0]) and min(a[3],b[3])>max(a[1],b[1]):raise ValueError(('overlapping labels',value,old['text']))
  lum=sorted([luminance(fill),luminance(bg)])
  if (lum[1]+.05)/(lum[0]+.05)<4.5:raise ValueError(('low contrast',value))
  self.d.text(xy,value,font=font,fill=fill,anchor=anchor)
  if value.strip():
   mask=Image.new('L',(max(1,math.ceil(b[2]-b[0]+4)),max(1,math.ceil(b[3]-b[1]+4))),0);md=ImageDraw.Draw(mask)
   md.text((xy[0]-b[0]+2,xy[1]-b[1]+2),value,font=font,fill=255,anchor=anchor)
   if sum(1 for p in mask.getdata() if p)>10: pass
   else:raise ValueError(('empty text pixels',value))
  self.labels.append({'text':value,'bbox':b,'font_px':size})
 def save(self,path,purpose,identity='原创教学示意',preview=None):
  height=math.ceil(self.last+36);im=self.im.crop((0,0,self.w,height));path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
  minfont=min((x['font_px'] for x in self.labels),default=None)
  result={'file':path.name,'width':self.w,'height':height,'minimum_font_px':minfont,'effective_font_at_354':round(minfont*354/self.w,2) if minfont else None,'purpose':purpose,'identity':identity,'geometry_and_glyph_checks':'passed','text_boxes':self.labels}
  assert Image.open(path).size==(self.w,height)
  if preview:im.resize((354,round(height*354/self.w)),Image.Resampling.LANCZOS).save(preview)
  return result
