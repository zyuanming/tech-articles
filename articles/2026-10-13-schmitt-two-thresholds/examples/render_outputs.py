"""Original teaching display driven by schmitt_lab output; not a commercial UI. MIT."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math
from schmitt_lab import data,run
ROOT=Path(__file__).resolve().parent
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def font(n):return ImageFont.truetype(FONT,n)
def panel(value,on,label,size=(624,210)):
 im=Image.new('RGB',size,'#182c3b');d=ImageDraw.Draw(im);d.rounded_rectangle((8,8,size[0]-8,size[1]-8),16,outline='#69899b',width=2)
 d.text((27,18),label,font=font(28),fill='#dde9e7');d.text((30,77),f'{value:.1f} °C',font=font(42),fill='white');d.text((30,145),'散热：'+('开' if on else '关'),font=font(28),fill='#68e0b4' if on else '#b5c0c8')
 cx,cy=510,108;col='#68e0b4' if on else '#647580';d.ellipse((cx-66,cy-66,cx+66,cy+66),outline=col,width=4)
 for a in [0,120,240]:
  r=math.radians(a);pts=[(cx,cy),(cx+55*math.cos(r),cy+55*math.sin(r)),(cx+27*math.cos(r+.9),cy+27*math.sin(r+.9))];d.polygon(pts,fill=col)
 d.ellipse((cx-10,cy-10,cx+10,cy+10),fill='white');return im
if __name__=='__main__':
 hand,_=data();states=run(hand);out=ROOT/'rendered';out.mkdir(exist_ok=True)
 for i in [2,3,4,5]:
  for name,on in [('single',hand[i]>=28),('hysteresis',states[i])]:panel(hand[i],on,'原创程序显示 · '+name).save(out/f'{name}-{i}.png')
 print('8 data-driven display frames written')
