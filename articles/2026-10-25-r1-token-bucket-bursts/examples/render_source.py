"""CC0 rendering code; RFC ASCII and notice retain Internet Society rights."""
from figurekit import *
import textwrap
source=(ROOT/'originals/rfc3290-figure4.txt').read_text()
mono='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
assert Path(mono).exists()
c=Canvas('原文中的 meter：判断，不等于处置')
c.text(50,120,'RFC 3290 图 4 · 原 ASCII 转录',40)
lines=source.split('unmetered',1)[1].split('Full Copyright Statement',1)[0]
lines=('unmetered'+lines).strip().splitlines()
# Original ASCII uses 37px with side margins; Chinese labels remain >=40px.
font=ImageFont.truetype(mono,37);cmap=TTFont(mono).getBestCmap()
y=230
for line in lines:
 if line.strip():
  assert all(ord(ch) in cmap for ch in line)
  box=c.d.textbbox((40,y),line,font=font);assert box[2]<=1062,(line,box)
  for old,*_ in c.boxes:
   assert min(box[2],old[2])<=max(box[0],old[0]) or min(box[3],old[3])<=max(box[1],old[1])
  c.d.text((40,y),line,font=font,fill=INK)
  pixel=c.im.crop(box).convert('L');lo,hi=pixel.getextrema();assert hi-lo>90
  assert sum(x<180 for x in pixel.getdata())>=len(line.strip())*8
  c.boxes.append((box,line,37));c.bottom=max(c.bottom,box[3])
 y+=65
c.text(50,y+35,'原图有三种合规程度；本文只用两种。',42)
c.text(50,y+115,'meter 后再接放行、丢弃或排队动作。',42)
c.text(50,y+195,'以下保留原文完整版权和许可通知。',40)
# Original legal text is an evidence attachment, not mobile teaching labels.
notice=source.split('Full Copyright Statement',1)[1].strip()
y+=300
f=ImageFont.truetype(mono,22)
for para in notice.split('\n\n'):
 for line in textwrap.wrap(' '.join(para.split()),width=76):
  assert all(ord(ch) in cmap for ch in line)
  box=c.d.textbbox((25,y),line,font=f);assert box[0]>=0 and box[2]<=1062 and box[3]<=4000
  for old,*_ in c.boxes:
   assert min(box[2],old[2])<=max(box[0],old[0]) or min(box[3],old[3])<=max(box[1],old[1])
  c.d.text((25,y),line,font=f,fill=INK)
  pixel=c.im.crop(box).convert('L');lo,hi=pixel.getextrema();assert hi-lo>90
  assert sum(x<180 for x in pixel.getdata())>=len(line.strip())*3
  c.boxes.append((box,line,22));y+=32
 y+=20
c.bottom=max(c.bottom,y)
c.save('14-rfc-meter.png','保留相关原始ASCII图及完整许可，说明测量结果与后续动作分开')
entry=meta[0];entry.update(identity='RFC3290 Fig4 ASCII转录渲染，非原站截图；Internet Society (2002)',min_font_px=22,effective_min_font_at_354=round(22/3,2),source_diagram_min_font_px=37,teaching_labels_min_font_px=40,exception='底部完整原许可通知22px，为史料附件；原ASCII37px保留左右边距（354宽约12.3px）；中文解释40px及以上')
# Preserve full original notice in PNG textual metadata as well.
from PIL.PngImagePlugin import PngInfo
info=PngInfo();info.add_text('Copyright and permission',notice)
p=ROOT/entry['file'];im=Image.open(p);im.save(p,pnginfo=info)
path=ROOT/'examples/figure-metadata.json';old=json.loads(path.read_text());old=[m for m in old if m['file']!=entry['file']]
path.write_text(json.dumps(old+[entry],ensure_ascii=False,indent=2)+'\n')
print('Source ASCII preserved with complete copyright statement')
