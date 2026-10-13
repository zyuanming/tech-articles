"""MIT-licensed renderer of actual Box2D-Lite CSV; no physics is computed here.
The pictures are original renderings of logged engine data, not official UI captures.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import csv,math
HERE=Path(__file__).resolve().parent
COLORS=['#617782','#42aac5','#e9a15a','#71be97','#b599d6','#e87982','#8ec3df','#d2c075','#90bda0']
def load(name):
    frames={}
    for row in csv.DictReader((HERE/'engine-output'/f'{name}.csv').open()):
        entry={k:float(v) for k,v in row.items()};frames.setdefault(int(entry['frame']),[]).append(entry)
    return frames

def render(frame,size=(640,400),bounds=(-3,4,-2,2),velocity=False):
    width,height=size;x0,x1,y0,y1=bounds
    scale=min((width-36)/(x1-x0),(height-36)/(y1-y0));ox=(width-scale*(x1-x0))/2;oy=(height-scale*(y1-y0))/2
    def xy(x,y):return (ox+(x-x0)*scale,height-oy-(y-y0)*scale)
    im=Image.new('RGB',size,'#172a38');d=ImageDraw.Draw(im)
    for x in range(math.ceil(x0),math.floor(x1)+1):d.line([xy(x,y0),xy(x,y1)],fill='#29424e',width=1)
    for y in range(math.ceil(y0),math.floor(y1)+1):d.line([xy(x0,y),xy(x1,y)],fill='#29424e',width=1)
    for body in frame:
        px,py,a=body['x'],body['y'],body['angle'];w,h=body['width']/2,body['height']/2;c,s=math.cos(a),math.sin(a)
        corners=[xy(px+c*x-s*y,py+s*x+c*y) for x,y in [(-w,-h),(w,-h),(w,h),(-w,h)]]
        color=COLORS[int(body['body'])%len(COLORS)];d.polygon(corners,fill=color,outline='#f2f6ec',width=2)
        if body['mass']<1e10:
            d.line([xy(px,py),xy(px+c*w*.7,py+s*w*.7)],fill='#172a38',width=3)
            xx,yy=xy(px,py);d.ellipse((xx-3,yy-3,xx+3,yy+3),fill='#f2f6ec')
            if velocity:d.line([xy(px,py),xy(px+body['vx']*.18,py+body['vy']*.18)],fill='#f5f0b5',width=3)
    return im

def run():
    out=HERE/'rendered';out.mkdir(exist_ok=True)
    for name in ['center','offset']:
        frames=load(name)
        for frame in [0,72,192,288]:render(frames[frame]).save(out/f'{name}-{frame:03d}.png')
    for name in ['stack-1-0','stack-1-1','stack-10-0','stack-10-1']:
        frames=load(name)
        for frame in [0,120,300,600]:render(frames[frame],(640,520),(-7,13,-1,9)).save(out/f'{name}-{frame:03d}.png')
    for name in ['slide-0','slide-0.3']:
        frames=load(name)
        for frame in [0,60,120,240]:render(frames[frame],(640,150),(-5,18,-1,2)).save(out/f'{name}-{frame:03d}.png')
if __name__=='__main__':run()
