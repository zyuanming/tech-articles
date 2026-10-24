"""Small original figure helper; code MIT, drawn illustrations CC BY 4.0."""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W=960
BG='#f7f4ec'; INK='#183044'; BLUE='#186c9c'; RED='#ba4534'; GREEN='#167861'; GRAY='#65717a'
FONT=next((p for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'] if Path(p).exists()),None)
if FONT is None: raise RuntimeError('Install Noto Sans CJK: Chinese font unavailable')
class Fig:
 def __init__(self,title):
  self.im=Image.new('RGB',(W,4000),BG);self.d=ImageDraw.Draw(self.im);self.boxes=[];self.texts=[];self.bottom=0;self.title=title
  self.text(36,25,title,46)
 def mark(self,b): self.bottom=max(self.bottom,b[3])
 def text(self,x,y,s,size=42,color=INK,anchor='lt',inside=None):
  f=ImageFont.truetype(FONT,size);b=self.d.textbbox((x,y),str(s),font=f,anchor=anchor)
  assert b[0]>=0 and b[2]<=W and b[1]>=0 and b[3]<=4000,('out of canvas',s,b)
  if inside: assert b[0]>=inside[0]+4 and b[1]>=inside[1]+4 and b[2]<=inside[2]-4 and b[3]<=inside[3]-4,('outside box',s)
  for q in self.texts:
   a=q['bbox']; assert min(b[2],a[2])<=max(b[0],a[0]) or min(b[3],a[3])<=max(b[1],a[1]),('text overlap',s,q['text'])
  assert size>=40
  for ch in str(s):
   if not ch.isspace():
    assert f.getmask(ch).getbbox() is not None,('empty glyph',ch)
  self.d.text((x,y),str(s),font=f,fill=color,anchor=anchor)
  self.texts.append({'text':str(s),'bbox':b,'size':size,'inside':inside});self.mark(b)
 def rect(self,b,fill=None,outline=INK,width=3):self.d.rectangle(b,fill=fill,outline=outline,width=width);self.mark(b)
 def line(self,pts,color=INK,width=5):self.d.line(pts,fill=color,width=width);self.mark((0,0,0,max(p[1] for p in pts)))
 def dot(self,x,y,r=9,color=RED):self.d.ellipse((x-r,y-r,x+r,y+r),fill=color);self.mark((0,0,0,y+r))
 def arrow(self,a,b,color=INK,width=5):
  self.line([a,b],color,width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);L=17
  self.d.polygon([b,(b[0]-L*math.cos(ang-.5),b[1]-L*math.sin(ang-.5)),(b[0]-L*math.cos(ang+.5),b[1]-L*math.sin(ang+.5))],fill=color)
 def image(self,im,xy,size=None):
  if isinstance(im,np.ndarray):im=Image.fromarray(np.uint8(np.clip(im,0,1)*255+.5))
  if size:im=im.resize(size,Image.Resampling.NEAREST)
  self.im.paste(im,xy);self.mark((xy[0],xy[1],xy[0]+im.width,xy[1]+im.height))
 def save(self,path,purpose,identity='原创教学示意'):
  H=math.ceil(self.bottom+30);im=self.im.crop((0,0,W,H));im.save(path)
  # Bounding boxes and actual non-background pixels are checked for every text.
  for t in self.texts:
   b=t['bbox'];a=np.asarray(im.crop(b));assert a.size and np.ptp(a.astype(float),axis=(0,1)).max()>35,('invisible text',t['text'])
  return {'file':'assets/'+Path(path).name,'width':W,'height':H,'minimum_font_px':min(t['size'] for t in self.texts),'effective_at_354px':round(min(t['size'] for t in self.texts)*354/W,2),'purpose':purpose,'identity':identity,'checks':{'canvas':True,'declared_boxes':True,'text_overlap':False,'font_floor':True,'pixel_contrast':True,'nonempty_glyphs':True}}
def srgb(x):
 x=np.asarray(x);return np.where(x<=.0031308,12.92*x,1.055*np.maximum(x,0)**(1/2.4)-.055)
def rgbim(x):return Image.fromarray(np.uint8(np.clip(srgb(x),0,1)*255+.5))
def checker(h,w):
 y,x=np.indices((h,w));v=np.where((x//24+y//24)%2==0,.85,.6);return np.repeat(v[...,None],3,axis=2)
def grid(f,x,y,nx,ny,cell=90,fill=None):
 for j in range(ny):
  for i in range(nx):f.rect((x+i*cell,y+j*cell,x+(i+1)*cell,y+(j+1)*cell),fill=fill,outline='#b9c4ca',width=2)
def finish(meta,folder):
 (folder/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
