"""Original educational diagrams. MIT license; see sources.md."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math,json
W=960
INK='#182b40'; BLUE='#17649c'; ORANGE='#a84716'; TEAL='#08786c'; GRAY='#617080'; LIGHT='#e7eff5'; RED='#ae2440'
FONT=next((p for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf'] if Path(p).exists()),None)
if not FONT: raise RuntimeError('Chinese font is required')
from fontTools.ttLib import TTFont
_CMAP=TTFont(FONT,fontNumber=0).getBestCmap()
class Board:
 def __init__(self,title):
  self.im=Image.new('RGB',(W,3000),'white');self.d=ImageDraw.Draw(self.im);self.texts=[];self.bottom=0
  self.text(title,35,28,44);self.line([(35,102),(925,102)],GRAY,2)
 def text(self,s,x,y,size=42,color=INK,anchor=None,box=None):
  assert size>=42
  assert all(ord(c) in _CMAP or c.isspace() for c in str(s)),('missing glyph',s)
  f=ImageFont.truetype(FONT,size); b=self.d.textbbox((x,y),str(s),font=f,anchor=anchor)
  assert 10<=b[0]<b[2]<=950 and b[1]>=0,(s,b)
  for old in self.texts:
   o=old['box'];assert not (b[0]<o[2] and b[2]>o[0] and b[1]<o[3] and b[3]>o[1]),(s,old['text'])
  if box: assert box[0]<=b[0] and box[1]<=b[1] and b[2]<=box[2] and b[3]<=box[3]
  self.d.text((x,y),str(s),font=f,fill=color,anchor=anchor)
  crop=self.im.crop(b); assert crop.getextrema()[0][0]<240,(s,'blank')
  self.texts.append({'text':str(s),'box':b,'size':size});self.bottom=max(self.bottom,b[3])
 def line(self,pts,color=BLUE,width=5):
  self.d.line(pts,fill=color,width=width);self.bottom=max(self.bottom,max(p[1] for p in pts))
 def arrow(self,a,b,color=BLUE,width=5):
  self.line([a,b],color,width); dx=b[0]-a[0];dy=b[1]-a[1];l=math.hypot(dx,dy);ux=dx/l;uy=dy/l
  self.d.polygon([b,(b[0]-18*ux+9*uy,b[1]-18*uy-9*ux),(b[0]-18*ux-9*uy,b[1]-18*uy+9*ux)],fill=color)
 def rect(self,box,fill=LIGHT,outline=BLUE,width=3):
  self.d.rectangle(box,fill=fill,outline=outline,width=width);self.bottom=max(self.bottom,box[3])
 def poly(self,points,fill=LIGHT,outline=BLUE):
  self.d.polygon(points,fill=fill,outline=outline,width=3);self.bottom=max(self.bottom,max(p[1] for p in points))
 def circle(self,x,y,r,fill=LIGHT,outline=BLUE,width=3):
  self.d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=outline,width=width);self.bottom=max(self.bottom,y+r)
 def save(self,path,purpose,identity='原创教学示意'):
  h=int(self.bottom+35);self.im=self.im.crop((0,0,W,h));path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);self.im.save(path)
  # Geometry and actual pixels: dark label pixels must exist on the white/light ground.
  for t in self.texts:
   b=t['box'];assert b[3]<=h
   p=self.im.crop(b); vals=list(p.convert('L').getdata());assert min(vals)<150 and max(vals)>200 and max(vals)-min(vals)>100
  return {'file':str(path.name),'width':W,'height':h,'min_font_px':min(t['size'] for t in self.texts),'effective_font_at_354px':min(t['size'] for t in self.texts)*354/W,'identity':identity,'purpose':purpose,'geometry_check':'passed','glyph_cmap_check':'passed','text_overlap_check':'passed','canvas_bounds_check':'passed','text_pixel_contrast_check':'passed','text_boxes':self.texts}
def plot(b,series,xlim,ylim,rect=(130,240,890,560),xlabel='时间',ylabel='幅度',ticks=None):
 x0,y0,x1,y1=rect; b.arrow((x0,y1),(x1+10,y1),GRAY,3);b.arrow((x0,y1),(x0,y0-15),GRAY,3)
 def pt(x,y):return x0+(x-xlim[0])/(xlim[1]-xlim[0])*(x1-x0),y1-(y-ylim[0])/(ylim[1]-ylim[0])*(y1-y0)
 for xs,ys,col in series:b.line([pt(x,y) for x,y in zip(xs,ys)],col,5)
 if ylim[0]<0<ylim[1]:b.line([pt(xlim[0],0),pt(xlim[1],0)],GRAY,2)
 b.text(xlabel,x1,y1+85,anchor='rt');b.text(ylabel,35,y0-100)
 for y in [ylim[0],(ylim[0]+ylim[1])/2,ylim[1]]:
  xx,yy=pt(xlim[0],y);b.text(f'{y:g}',xx-15,yy,anchor='rm')
 if ticks is None: ticks=[(v,f'{v:g}') for v in [xlim[0],(xlim[0]+xlim[1])/2,xlim[1]]]
 if ticks:
  for x,label in ticks:xx,yy=pt(x,ylim[0]);b.text(label,xx,yy+23,anchor='mt')
 return pt
