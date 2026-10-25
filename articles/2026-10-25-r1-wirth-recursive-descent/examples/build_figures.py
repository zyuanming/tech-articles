"""Original diagrams from parser results. Code CC0; figures CC BY 4.0."""
import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
HERE=Path(__file__).resolve().parent
DATA=json.loads((HERE/'results.json').read_text())
RUN=DATA['runs']; MAIN=RUN['12-3*2-1']
FONT=next((Path(p) for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf'] if Path(p).exists()),None)
assert FONT, 'Chinese font required'
CMAP=TTFont(str(FONT),fontNumber=0).getBestCmap()
BG='#faf7ef';INK='#192d3b';BLUE='#165b70';PALE='#e1efeb';GOLD='#f5e1ab';RED='#8c3038'
META=[]

def luminance(h):
 c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
 c=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c]
 return sum(a*b for a,b in zip(c,[.2126,.7152,.0722]))

class Canvas:
 def __init__(self,name,title,purpose):
  self.name,self.purpose=name,purpose
  self.im=Image.new('RGB',(1062,6000),BG);self.d=ImageDraw.Draw(self.im)
  self.texts=[];self.lines=[];self.bottom=0
  self.text(48,40,title,52);self.line(48,122,1014,122)
 def text(self,x,y,s,size=44,color=INK,box=None,bg=BG):
  assert size>=40
  assert all(ord(c) in CMAP for c in s),(s,'missing glyph')
  f=ImageFont.truetype(str(FONT),size)
  b=self.d.textbbox((x,y),s,font=f,anchor='lt')
  assert b[0]>=28 and b[2]<=1034 and b[1]>=0,(self.name,s,b)
  if box: assert b[0]>=box[0]+8 and b[2]<=box[2]-8 and b[1]>=box[1]+8 and b[3]<=box[3]-8,(s,b,box)
  for t in self.texts:
   a=t['bbox'];assert not(b[0]<a[2] and b[2]>a[0] and b[1]<a[3] and b[3]>a[1]),(self.name,s,t['text'])
  lo,hi=sorted([luminance(color),luminance(bg)]);contrast=(hi+.05)/(lo+.05);assert contrast>=4.5
  self.d.text((x,y),s,font=f,fill=color,anchor='lt')
  ink=sum(p!=tuple(bytes.fromhex(bg[1:])) for p in self.im.crop(b).getdata());assert ink>size
  self.texts.append(dict(text=s,bbox=b,font_px=size,contrast=contrast,ink_pixels=ink,box=box))
  self.bottom=max(self.bottom,b[3])
 def line(self,x1,y1,x2,y2,color=BLUE,width=4):
  self.d.line((x1,y1,x2,y2),fill=color,width=width);self.lines.append((x1,y1,x2,y2,width));self.bottom=max(self.bottom,y1,y2)
 def arrow(self,x1,y1,x2,y2):
  self.line(x1,y1,x2,y2);a=math.atan2(y2-y1,x2-x1)
  self.d.polygon([(x2,y2),(x2-17*math.cos(a-.5),y2-17*math.sin(a-.5)),(x2-17*math.cos(a+.5),y2-17*math.sin(a+.5))],fill=BLUE)
 def box(self,b,fill=PALE):
  self.d.rounded_rectangle(b,16,fill,BLUE,3);self.bottom=max(self.bottom,b[3])
 def save(self,out):
  for x1,y1,x2,y2,w in self.lines:
   steps=max(abs(x2-x1),abs(y2-y1),1)
   for t in self.texts:
    a,b,c,d=t['bbox']
    for i in range(int(steps)+1):
     x=x1+(x2-x1)*i/steps;y=y1+(y2-y1)*i/steps
     assert not(a-w/2<x<c+w/2 and b-w/2<y<d+w/2),(self.name,'line-text collision',t['text'])
  h=int(self.bottom+48);self.im=self.im.crop((0,0,1062,h));p=out/(self.name+'.png');self.im.save(p)
  assert Image.open(p).size==(1062,h)
  META.append(dict(file='assets/'+p.name,width=1062,height=h,minimum_font_px=min(t['font_px'] for t in self.texts),identity='原创机制图；数值与树来自实跑JSON',license='CC-BY-4.0',purpose=self.purpose,data='examples/results.json',geometry='节点/边/步骤取自JSON；坐标和字号为版式常量，无数量轴',checks=['cmap','text-bounds','declared-box','text-overlap','font-minimum','contrast','ink','line-text','dynamic-crop','PNG-size'],texts=self.texts))

def tree(c,r,root,y=220):
 nodes=r['nodes'];leaves=[];depths={}
 def collect(k,depth):
  depths[k]=depth
  if nodes[k]['op']=='NUM':leaves.append(k)
  else:collect(nodes[k]['left'],depth+1);collect(nodes[k]['right'],depth+1)
 collect(root,0);coords={}
 for i,k in enumerate(leaves):coords[k]=(160+742*i/max(1,len(leaves)-1),y+depths[k]*175)
 def place(k):
  if k not in coords:
   a,b=nodes[k]['left'],nodes[k]['right'];place(a);place(b)
   coords[k]=((coords[a][0]+coords[b][0])/2,y+depths[k]*175)
 place(root)
 for k,(x,yy) in coords.items():
  n=nodes[k]
  if n['op']!='NUM':
   for child in [n['left'],n['right']]:
    xx,y2=coords[child];dist=math.hypot(xx-x,y2-yy);dx=(xx-x)/dist;dy=(y2-yy)/dist
    c.line(x+dx*51,yy+dy*51,xx-dx*51,y2-dy*51)
 for k,(x,yy) in coords.items():
  n=nodes[k];label=str(n['value']) if n['op']=='NUM' else n['op']
  c.d.ellipse((x-50,yy-50,x+50,yy+50),fill=GOLD if n['op']!='NUM' else PALE,outline=BLUE,width=3)
  f=ImageFont.truetype(str(FONT),48);w=c.d.textlength(label,font=f)
  c.text(x-w/2,yy-24,label,48,bg=GOLD if n['op']!='NUM' else PALE)
  c.bottom=max(c.bottom,yy+50)
 return max(yy for x,yy in coords.values())+110


def main(out):
 out.mkdir(parents=True,exist_ok=True)
 c=Canvas('00-cover','一行算式，怎样长成一棵树？','独立封面：把输入与分层的运算依赖联系起来')
 c.text(80,175,MAIN['source'],70);end=tree(c,MAIN,MAIN['root'],380)
 c.text(70,end,'Wirth 与递归下降',56);c.text(70,end+85,'把文法写成会互相调用的函数',44);c.save(out)
 c=Canvas('01-tokens','字符位置与 token 不是一回事','显示多位数字合并、半开区间与EOF位置')
 for i,ch in enumerate(MAIN['source']):
  x=70+i*115;c.text(x,180,ch,56);c.text(x,265,str(i),40)
 c.text(70,345,'上行是字符；下行是从零起的位置',42)
 for i,t in enumerate(MAIN['tokens']):
  x=55+(i%4)*252;y=440+(i//4)*210;b=(x,y,x+238,y+175);c.box(b)
  label=t['text'] or t['kind'];c.text(x+20,y+20,label,48,box=b,bg=PALE)
  c.text(x+20,y+100,f'{t["start"]} → {t["end"]}',40,box=b,bg=PALE)
 c.text(65,900,'区间含起点、不含终点；EOF 不占字符',40);c.save(out)
 c=Canvas('02-number','读到第二位，为什么不是第二个数？','逐位十进制累积和遇非数字结束')
 for j,d in enumerate(MAIN['digits'][:2]):
  y=190+j*230;c.text(65,y,f'读字符 {d["digit"]}（位置 {d["pos"]}）',48)
  c.text(90,y+90,f'{d["before"]} × 10 + {d["digit"]} = {d["after"]}',64)
 c.text(65,690,'接下来是 −：数字结束，减号留下',44)
 c.text(65,780,f'交出一个 NUM，值为 {MAIN["tokens"][0]["value"]}',48);c.save(out)
 c=Canvas('03-grammar','每一层只接自己负责的运算','把文法层级、循环与括号递归关系合成源码结构图')
 rows=[('expr()', 'term 后接若干 + 或 − 与 term'),('term()','factor 后接若干 * 与 factor'),('factor()','NUM，或 ( expr )')]
 for i,(a,b) in enumerate(rows):
  y=180+i*240;box=(125,y,960,y+170);c.box(box);c.text(160,y+20,a,52,box=box,bg=PALE);c.text(160,y+100,b,40,box=box,bg=PALE)
  if i<2:c.arrow(530,y+175,530,y+230)
 c.line(120,745,65,745);c.line(65,745,65,265);c.arrow(65,265,120,265)
 c.text(125,920,'左侧回边：括号内部重新调用 expr',42)
 c.text(125,1000,'纵向箭头：按层调用；不是求值顺序',40);c.save(out)
 c=Canvas('04-trace','先进入，再带着子树返回','从实际调用事件展示初段识别12与交回减号')
 chosen=[0,1,2,3,5,6,7,8]
 action={'enter':'进入','return':'返回','consume':'吃掉'}
 for row,i in enumerate(chosen):
  e=MAIN['events'][i];y=180+row*115;x=70+(len(e['stack'])-1)*65
  c.text(x,y,f'{e["step"]}  {action[e["action"]]} {e["detail"]}',44)
  c.text(700,y,f'游标 {e["index"]}',42)
 c.text(65,1160,'缩进表示调用深度；游标只在吃掉后前移',40)
 c.text(65,1240,'term 看见 − 就返回，交给 expr 处理',42);c.save(out)
 builds=[e for e in MAIN['events'] if e['action']=='build' and e['detail']!='NUM']
 for i,e in enumerate(builds):
  n=MAIN['nodes'][e['node']];c=Canvas(f'0{i+5}-build',f'第 {i+1} 次运算节点构建：{n["op"]}','保留实际AST逐次构建，解释优先级与左折叠')
  c.text(65,170,f'事件 {e["step"]}；当前 token：{e["look"]}',44)
  end=tree(c,MAIN,e['node'],340)
  c.text(65,end,f'这棵子树求值为 {MAIN["values"][e["node"]]}',48)
  labels=['term 先构建乘法子树，再整棵交回','expr 把原来的 left 放到新节点左边','再次使用整个 left；形成左结合']
  c.text(65,end+85,labels[i],42);c.save(out)
 r=RUN['12-(3*2-1)'];c=Canvas('08-parentheses','括号让 factor 再进入一次 expr','对照括号如何改变AST归属与结果')
 c.text(65,180,r['source'],64);end=tree(c,r,r['root'],350)
 c.text(65,end,f'内树求值：{r["values"][r["nodes"][r["root"]]["right"]]}；整式：{r["value"]}',48)
 c.text(65,end+85,'括号影响树形，但不单独成为运算节点',42);c.save(out)
 c=Canvas('09-choice','看一个 token，怎样选路？','将FIRST选择、循环退出与非法输入区分')
 for i,(look,result) in enumerate([('NUM','factor：读一个整数'),('(','factor：读括号中的 expr'),('*','term：继续读一个 factor'),('+ 或 −','term：返回给 expr'),(') 或 EOF','expr：停止循环并返回')]):
  y=180+i*140;c.text(65,y,look,48);c.arrow(310,y+28,410,y+28);c.text(440,y,result,40)
 c.text(65,940,'以上选择都发生在对应的文法位置',42)
 c.text(65,1025,'例如 factor 开头遇到 *，必须报错',42);c.save(out)
 c=Canvas('10-first-follow','能开头，和能跟在后面，是两件事','由固定点计算结果展示FIRST/FOLLOW与空尾部选择')
 for i,k in enumerate(['E','T','F']):
  y=180+i*220;c.text(65,y,{'E':'E / expr','T':'T / term','F':'F / factor'}[k],50)
  first='  '.join(DATA['sets']['first'][k]);follow='  '.join(DATA['sets']['follow'][k])
  c.text(65,y+78,'FIRST: '+first,42);c.text(65,y+145,'FOLLOW: '+follow,42)
 c.text(65,910,'R 是加减尾部： + T R | − T R | ε',40)
 c.text(65,990,'ε 不吃字符；只在 ) 或 EOF 时选择',42)
 c.text(65,1070,'EOF 是输入结束标记；ε 是空串',42);c.save(out)
 c=Canvas('11-left-recursion','还没吃字符，就又调用自己','有界错误探针与改写文法并列说明左递归风险')
 c.text(65,180,'错误直译：E → E − T | T',48)
 for i,e in enumerate(DATA['left_recursion']):
  y=280+i*105;x=65+i*90;c.text(x,y,f'E 深度 {e["depth"]}，游标 {e["index"]}',44)
 c.text(65,750,'仅演示前四次进入；主动截断探针',40)
 c.text(65,850,'改写：E → T { − T }',50)
 c.text(65,945,'先读 T，再循环：left = (− left T)',42)
 c.text(65,1030,'消除左递归后，仍要检查选择冲突',42);c.save(out)
 c=Canvas('12-error-map','程序拒绝的，是哪个位置？','区分词法、缺操作数、尾部残留和缺右括号')
 for i,s in enumerate(['12@3','12-3**2','12 3','(12-3']):
  r=RUN[s];e=r['error'];y=180+i*230;c.text(65,y,s,58)
  c.text(65,y+95,f'位置 {e["pos"]}：遇到 {e["found"]}',44,color=RED)
  c.text(65,y+160,'期待 '+e['expected'],40)
 c.text(65,1130,'位置从零起算；EOF 定位在文本末尾',42);c.save(out)
 # Screenshots were captured from live browser; retain identity if present.
 for name,purpose in [('13-live-result','Python实际解析成功：token与依创建顺序的运算节点'),('14-live-error','Python实际错误：位置5的第二个乘号')]:
  p=out/(name+'.png')
  if p.exists():
   w,h=Image.open(p).size;META.append(dict(file='assets/'+p.name,width=w,height=h,minimum_font_px=40,identity='真实Chromium截图；原创教学程序v1；Python3.12.14',license='CC-BY-4.0',purpose=purpose,data='实际HTTP POST /parse返回',checks=['live-browser','PNG-size','desktop-mobile-layout'],geometry='浏览器真实渲染；不由绘图脚本重建'))
 (HERE/'figure-metadata.json').write_text(json.dumps(META,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=HERE.parent/'assets');main(p.parse_args().out)
