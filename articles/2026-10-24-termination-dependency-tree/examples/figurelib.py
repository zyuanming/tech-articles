"""Original teaching figure helper; MIT, zyuanming, 2026. See sources.md.
Requires Python 3.11+, Pillow. Fonts: Noto Sans CJK installed by OS.
Geometry checks are not semantic peer review.
"""
from pathlib import Path
import math,json
from PIL import Image,ImageDraw,ImageFont,ImageStat
W=1062
INK='#172a3a'; BLUE='#185ea8'; TEAL='#087e83'; ORANGE='#b34716'; GRAY='#607080'
PALE='#e7f0fa'; MINT='#e3f3ef'; WARM='#fff0e2'; LIGHT='#edf0f3'; WHITE='#ffffff'
FONT=next((p for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'] if Path(p).exists()),None)
if not FONT: raise RuntimeError('Noto Sans CJK font required; no silent fallback')
class Fig:
 def __init__(self,title):
  self.im=Image.new('RGB',(W,2400),WHITE);self.d=ImageDraw.Draw(self.im);self.texts=[];self.bottom=0
  self.text(44,30,title,54)
 def text(self,x,y,s,size=46,fill=INK,anchor=None,inside=None):
  assert size>=44
  f=ImageFont.truetype(FONT,size)
  # Compare non-space glyph masks with missing-glyph mask.
  missing=bytes(f.getmask(chr(0x10ffff)))
  for c in s:
   if not c.isspace(): assert bytes(f.getmask(c))!=missing,('missing glyph',c)
  bb=self.d.textbbox((x,y),s,font=f,anchor=anchor)
  assert 0<=bb[0] and bb[2]<=W and 0<=bb[1] and bb[3]<2400,('off canvas',s,bb)
  if inside: assert inside[0]+8<=bb[0] and inside[1]+8<=bb[1] and bb[2]<=inside[2]-8 and bb[3]<=inside[3]-8,('outside box',s,bb,inside)
  for b,old,_ in self.texts:
   assert min(b[2],bb[2])<=max(b[0],bb[0]) or min(b[3],bb[3])<=max(b[1],bb[1]),('text overlap',old,s)
  self.d.text((x,y),s,font=f,fill=fill,anchor=anchor)
  self.texts.append((bb,s,size));self.bottom=max(self.bottom,bb[3])
 def box(self,xy,fill=PALE,outline=BLUE):
  self.d.rounded_rectangle(xy,radius=14,fill=fill,outline=outline,width=3);self.bottom=max(self.bottom,xy[3])
 def node(self,cx,cy,label,w=200,h=94,fill=PALE,outline=BLUE):
  b=(cx-w/2,cy-h/2,cx+w/2,cy+h/2);self.box(b,fill,outline);self.text(cx,cy,label,anchor='mm',inside=b)
 def arrow(self,a,b,color=BLUE,width=6):
  self.d.line([a,b],fill=color,width=width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);l=19
  self.d.polygon([b,(b[0]-l*math.cos(ang-.45),b[1]-l*math.sin(ang-.45)),(b[0]-l*math.cos(ang+.45),b[1]-l*math.sin(ang+.45))],fill=color);self.bottom=max(self.bottom,a[1],b[1])
 def line(self,xy,color=GRAY,width=4):
  self.d.line(xy,fill=color,width=width);self.bottom=max(self.bottom,*[p[1] for p in xy])
 def dot(self,x,y,r=11,color=BLUE):
  self.d.ellipse((x-r,y-r,x+r,y+r),fill=color);self.bottom=max(self.bottom,y+r)
 def table(self,headers,rows,y=130,widths=None):
  widths=widths or [(W-88)/len(headers)]*len(headers);x=44
  for j,h in enumerate(headers):
   self.box((x,y,x+widths[j]-5,y+88),LIGHT,GRAY);self.text(x+widths[j]/2,y+44,str(h),anchor='mm');x+=widths[j]
  for i,row in enumerate(rows):
   x=44;yy=y+100+i*88
   for j,v in enumerate(row):
    self.text(x+widths[j]/2,yy+38,str(v),anchor='mm');x+=widths[j]
   self.line([(44,yy+82),(W-44,yy+82)],LIGHT,2)
 def queue(self,labels,y=180,x=110,color=BLUE):
  n=max(1,len(labels));cw=min(180,840/n)
  for i,t in enumerate(labels): self.node(x+cw*(i+.5),y,str(t),cw-12,100,PALE,color)
  return x,x+cw*n
 def lanes(self,names,events,max_t,y=170,step=2):
  # events: (lane, start,end,label,color)
  x0=180;x1=990;scale=(x1-x0)/max_t
  for i,name in enumerate(names):
   yy=y+i*145;self.text(44,yy+38,name,anchor='lm');self.line([(x0,yy+85),(x1,yy+85)],GRAY,2)
  for lane,a,b,label,col in events:
   yy=y+lane*145;bb=(x0+a*scale,yy,x0+b*scale-3,yy+76);self.box(bb,col,col)
   if label:self.text((bb[0]+bb[2])/2,yy+38,label,44,WHITE,anchor='mm',inside=bb)
  yy=y+len(names)*145
  for t in range(0,max_t+1,step):
   xx=x0+t*scale;self.line([(xx,yy),(xx,yy+12)]);self.text(xx,yy+28,str(t),44,anchor='mt')
 def save(self,path,purpose,identity='原创机制示意'):
  h=math.ceil(self.bottom+42);assert h<2400
  im=self.im.crop((0,0,W,h))
  for bb,s,size in self.texts:
   region=im.crop(bb).convert('L');lo,hi=region.getextrema();assert hi-lo>50,('contrast',s)
   hist=region.histogram();assert sum(hist[:150])>10,('no visible ink',s)
  path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
  return dict(file=path.name,width=W,height=h,min_font_px=min(t[2] for t in self.texts),effective_at_354_px=min(t[2] for t in self.texts)*354/W,purpose=purpose,identity=identity,geometry_checks={'canvas':True,'declared_boxes':True,'text_overlap':True,'font_minimum':True,'contrast_and_pixels':True,'glyph_masks':True})
def emit(base,items):
 meta=[]
 for name,fig,purpose in items:meta.append(fig.save(base/'assets'/name,purpose))
 (base/'examples'/'figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 for m in meta:
  with Image.open(base/'assets'/m['file']) as im:assert im.size==(m['width'],m['height'])
 return meta
