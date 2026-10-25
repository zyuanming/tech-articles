"""Original external merge figures, CC BY 4.0; generator code CC0-1.0.
Canvas validation API adapted from this repository's r1 Count-Min generator (CC0).
All figure compositions below are new.
"""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'examples/results.json').read_text())
CANDIDATES=['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc']
FONT=next((p for p in CANDIDATES if Path(p).exists()),None)
if not FONT:raise RuntimeError('Chinese font not found')
CMAP=TTFont(FONT,fontNumber=0).getBestCmap()
BG='#f8fafc'; INK='#142d42'; BLUE='#176297'; GREEN='#166c57'; ORANGE='#9c4d0d'
meta=[]
class Canvas:
 def __init__(self,title):
  self.im=Image.new('RGB',(1062,4000),BG);self.d=ImageDraw.Draw(self.im);self.boxes=[];self.bottom=0
  self.text(50,30,title,48)
 def text(self,x,y,s,size=42,color=INK,box=None):
  assert size>=40
  assert all(ord(c) in CMAP for c in s if not c.isspace()),s
  f=ImageFont.truetype(FONT,size);b=self.d.textbbox((x,y),s,font=f)
  assert b[0]>=0 and b[1]>=0 and b[2]<=1062 and b[3]<=4000,(s,b)
  if box:assert box[0]+5<=b[0] and box[1]+5<=b[1] and b[2]<=box[2]-5 and b[3]<=box[3]-5,(s,b,box)
  for old in self.boxes:
   q=old[0]
   assert min(b[2],q[2])<=max(b[0],q[0]) or min(b[3],q[3])<=max(b[1],q[1]),(s,old[1])
  self.d.text((x,y),s,font=f,fill=color);self.boxes.append((b,s,size));self.bottom=max(self.bottom,b[3])
  px=self.im.crop(b).convert('L');lo,hi=px.getextrema();assert hi-lo>90,(s,lo,hi)
  assert sum(1 for v in px.getdata() if v<180)>len(s)*8,s
 def line(self,a,b,color=BLUE,dashed=False):
  if dashed:
   dx=b[0]-a[0];dy=b[1]-a[1];n=max(1,int(math.hypot(dx,dy)/18))
   for i in range(0,n,2):self.d.line((a[0]+dx*i/n,a[1]+dy*i/n,a[0]+dx*min(i+1,n)/n,a[1]+dy*min(i+1,n)/n),fill=color,width=5)
  else:self.d.line((*a,*b),fill=color,width=5)
  self.bottom=max(self.bottom,a[1],b[1])
 def arrow(self,a,b,color=BLUE,dashed=False):
  self.line(a,b,color,dashed);ang=math.atan2(b[1]-a[1],b[0]-a[0]);pts=[b]
  for delta in [-.55,.55]:pts.append((b[0]-20*math.cos(ang+delta),b[1]-20*math.sin(ang+delta)))
  self.d.polygon(pts,fill=color)
 def card(self,x,y,w,h,s,fill='#e5eef7',color=INK):
  b=(x,y,x+w,y+h);self.d.rounded_rectangle(b,radius=16,fill=fill)
  f=ImageFont.truetype(FONT,42);width=self.d.textlength(s,font=f)
  self.text(x+(w-width)/2,y+(h-60)/2,s,42,color,b);self.bottom=max(self.bottom,y+h)
 def save(self,name,purpose):
  im=self.im.crop((0,0,1062,math.ceil(self.bottom+45)));p=ROOT/'assets'/name;im.save(p)
  assert Image.open(p).size==im.size
  meta.append(dict(file='assets/'+name,width=im.width,height=im.height,min_font_px=min(z[2] for z in self.boxes),effective_min_font_at_354=round(min(z[2] for z in self.boxes)/3,2),identity='原创教学示意；执行数值来自 results.json',purpose=purpose,checks=['canvas','declared-box','text-overlap','font-size','contrast','glyph-cmap','ink-pixels','actual-dimensions']))

RED='#ae3e38';GRAY='#667887';CFG=DATA['config'];RUNS=DATA['initial'];MERGE=DATA['merges'][0]
B=CFG['block_records'];N=len(DATA['keys']);C=CFG['chunk_records'];K=CFG['fan_in'];S=CFG['record_bytes']
assert (N,B,C,K,S)==(24,2,6,3,8)
assert len(RUNS)==4 and len(DATA["partial"]["output"])==5
assert [p["fan"] for p in DATA["fan_comparison"]]==[2,3,4]
assert all(p["buffer_blocks"]==p["fan"]+1 for p in DATA["fan_comparison"])
def nums(c,values,y,step=145,x=60,selected=None):
 for j,v in enumerate(values):c.card(x+j*step,y,step-15,90,str(v),fill='#ffe0b5' if selected==j else '#e5eef7')
def values(records):return [r[0] for r in records]
def runrows(c,records,y,prefix=''):
 for q in range(0,len(records),6):nums(c,values(records[q:q+6]),y+(q//6)*115)
 return y+math.ceil(len(records)/6)*115

c=Canvas('外部归并：让大文件分批走过内存')
for i,r in enumerate(RUNS):
 c.text(60,150+i*140,f'R{i}',42);nums(c,values(r['sorted']),145+i*140,step=135,x=175)
c.text(60,755,f'{len(RUNS)} 个有序段，不等于整文件有序',42)
c.arrow((530,850),(530,950));c.card(230,980,600,100,'逐次选择各段当前最小值')
c.arrow((530,1110),(530,1200));c.card(230,1220,600,100,f'最终得到 {N} 条全局有序记录',fill='#dceee6')
c.save('00-cover.png','封面展示初始有序段与全局归并目标')

c=Canvas('先分清记录、块、文件和内存')
c.text(60,150,f'一条记录：键 {S//2} 字节 + 原序号 {S//2} 字节',42)
c.card(75,250,420,100,'键：用于大小比较');c.card(565,250,420,100,'原序号：区分同键')
c.text(60,420,f'一块 = {B} 条 = {B*S} 字节（教学值）',44)
nums(c,[f'{DATA["keys"][j]}:{j}' for j in range(B)],540,step=300,x=225)
c.text(60,700,f'整个文件 = {N} 条 = {DATA["input_bytes"]} 字节',44)
for i in range(N//B):c.card(60+(i%6)*155,810+(i//6)*125,135,90,f'块{i}')
c.text(60,1110,f'工作数据缓冲：{CFG["data_buffer_blocks"]} 块，共 {CFG["data_buffer_blocks"]*B*S} 字节',42)
c.text(60,1200,'此预算不含 Python 对象、堆和文件元数据',40,RED)
c.save('01-units.png','用同一文件解释8字节记录、16字节块和数据缓冲预算')

c=Canvas('生成初始段：连续取一批，在内存排好')
for i,r in enumerate(RUNS):
 y=150+i*330;c.text(60,y,f'R{i}：原文件连续 {len(r["input"])} 条',42);nums(c,values(r['input']),y+75)
 c.text(60,y+185,'排好',40);nums(c,values(r['sorted']),y+180,step=135,x=180)
c.text(60,1520,f'每次只排 {C} 条，依次写出 {len(RUNS)} 个文件',42)
c.save('02-runs.png','完整输入四批与各自排序结果，显示阶段内部排序而非全量内存排序')

c=Canvas('为什么不能把四个文件直接接起来？')
nums(c,values(RUNS[0]['sorted']),160);nums(c,values(RUNS[1]['sorted']),330)
a,b=DATA['concat_boundary'];c.text(60,520,f'拼接边界：R0 的末尾 {a}，接 R1 的开头 {b}',42)
c.card(150,650,260,110,str(a),fill='#ffe0b5');c.card(650,650,260,110,str(b),fill='#ffe0b5');c.arrow((440,705),(610,705),RED)
c.text(60,870,f'{a} > {b}：段内有序，边界仍会倒退',44,RED)
c.text(60,980,'需要重新交织各段，而不是重命名后串接',40)
c.save('03-concat.png','反例证明各run内部有序不意味着拼接后有序')

c=Canvas('同一预算，在两个阶段分配不同职责')
for i in range(CFG['data_buffer_blocks']):
 c.card(60+245*i,200,220,110,'待排序' if i<CFG['data_buffer_blocks']-1 else 'I/O缓冲',fill='#dceee6' if i<3 else '#ffe0b5')
c.text(60,365,f'生成段：{C} 条工作区 + {B} 条传输缓冲',44)
for i in range(CFG['data_buffer_blocks']):c.card(60+245*i,570,220,110,f'输入R{i}' if i<K else '输出',fill='#e5eef7' if i<K else '#ffe0b5')
c.text(60,740,f'归并：{K} 个输入块 + {CFG["data_buffer_blocks"]-K} 个输出块',44)
c.text(60,865,f'每块 {B} 条，数据槽总数仍是 {CFG["data_buffer_blocks"]*B}',42)
c.text(60,970,'各段只在头部块里取数，用完才补下一块',40)
c.text(60,1060,'真实实现还要另留堆、指针和库缓冲空间',40,RED)
c.save('04-memory.png','统一四块预算展示生成段和三路归并阶段的空间分工')

c=Canvas('只比较各段的头：前六次选择')
headers=['步','R0头','R1头','R2头','输出']
for i,h in enumerate(headers):c.text(65+i*190,160,h,42)
for step,s in enumerate(MERGE['steps'][:6]):
 heads={x['run']:x['record'][0] for x in s['heap_before']};row=[step+1,*[heads.get(i,'—') for i in range(K)],s['chosen'][0]]
 for j,v in enumerate(row):c.card(55+j*190,255+step*120,165,90,str(v),fill='#ffe0b5' if j==4 else '#e5eef7')
c.text(60,1060,'每次只推进被选中的那一段，其余头不动',40)
c.text(60,1150,'同键时再比较原序号，保持原先先后',40)
c.save('05-heads.png','完整列出前六步候选头和值，解释正确性不依赖扫描整段')

c=Canvas('输入块用完了，怎样继续？')
r=RUNS[2]['sorted'];c.text(60,150,'第一组三路归并中的 R2',44)
for j in range(0,len(r),B):
 y=270+(j//B)*230;nums(c,values(r[j:j+B]),y,step=200,x=100);c.text(560,y+20,'当前块' if j==0 else '后续磁盘块',42)
c.text(60,1040,f'先输出 {r[0][0]}，该块还剩 {r[1][0]}',42)
c.text(60,1130,f'再输出 {r[1][0]} 后，下一块带来 {r[2][0]}、{r[3][0]}',42)
c.text(60,1220,'块空：补下一块；整段结束：移出候选堆',40)
c.save('06-refill.png','区分输入缓冲耗尽与整个有序段结束')

c=Canvas('输出也按块攒起来，再写回文件')
writes=[e for e in MERGE['events'] if e['kind']=='write']
for i,e in enumerate(writes[:3]):
 y=170+i*200;nums(c,values(e['records']),y,step=175,x=70);c.arrow((465,y+45),(650,y+45));c.card(710,y,280,90,f'写块 {i+1}')
pw=[e for e in DATA['partial']['merges'][0]['events'] if e['kind']=='write']
c.text(60,840,'另一个五条记录的尾块例子',44)
nums(c,values(pw[-1]['records']),960,step=175,x=70);c.text(350,980,f'最后仅 {len(pw[-1]["records"])} 条，也要写出',42)
c.text(60,1160,'等不到满块就结束，会丢掉最后几条记录',40,RED)
c.text(60,1250,'计数把非空尾块算一块，字节数按实际长度',40)
c.save('07-flush.png','前三个实际输出块及独立五记录用例的非满尾块')

c=Canvas('小根堆：让最小的头留在最上方')
s0=MERGE['steps'][0];s1=MERGE['steps'][1]
for offset,state,label in [(0,s0['heap_before'],'输出前'),(560,s0['heap_after'],'推进来源段后')]:
 c.text(60,140+offset,label,44)
 coords=[(470,250+offset),(190,440+offset),(750,440+offset)]
 for i,(rec,x) in enumerate(zip(state,coords)):
  if i:c.line((530,340+offset),(x[0]+60,x[1]))
  c.card(x[0],x[1],140,90,str(rec['record'][0]),fill='#ffe0b5' if i==0 else '#e5eef7');c.text(x[0],x[1]+110,f'R{rec["run"]}',40)
c.text(60,1350,'父节点不大于孩子；左右孩子无需互相有序',40)
c.text(60,1440,'只维护各段一个候选，不把整段装进堆',40)
c.save('08-heap.png','实际heap前后状态显示候选更新和堆序而非全排序')

c=Canvas('有序段太多，就分组做下一趟')
for i,r in enumerate(RUNS):c.card(60+i*245,170,220,100,f'R{i}：{len(r["sorted"])}条')
for i in range(K):c.arrow((170+i*245,300),(330,430))
c.arrow((905,300),(820,430));c.card(100,470,460,100,f'G0：{len(DATA["merges"][0]["records"])}条');c.card(670,470,340,100,f'G1：{len(DATA["merges"][1]["records"])}条')
c.text(60,660,'第一趟：孤单 R3 也复制到新代文件',40)
c.arrow((330,780),(530,910));c.arrow((840,780),(530,910));c.card(280,950,500,100,f'第二趟：最终 {N} 条')
c.text(60,1160,'本实现保留每代文件，便于逐一核对',40)
c.text(60,1250,'可优化：沿用孤段，或安全回收已消费文件',40)
c.save('09-passes.png','展示4→2→1完整谱系并显式说明孤段复制策略')

c=Canvas('把每一趟的读写账摊开')
for j,h in enumerate(['阶段','读块','写块','总字节']):c.text(65+j*245,160,h,42)
for i,p in enumerate(DATA['phases']):
 for j,v in enumerate([f'生成段' if i==0 else f'归并{i}',p['read_blocks'],p['write_blocks'],p['read_bytes']+p['write_bytes']]):c.card(55+j*245,270+i*140,220,100,str(v))
c.text(60,800,f'总块传输 = {DATA["total_blocks"]}；逻辑字节 = {DATA["logical_bytes"]}',44)
c.text(60,910,'输入生成、结果校验的额外读写不在表内',40)
c.text(60,1010,'不是系统调用数，不是物理扇区数',42,RED)
c.text(60,1100,'缓存、预读、合并写回会改变底层 I/O',40)
c.save('10-io.png','实际分阶段非空块与字节计数，明确计量边界')

c=Canvas('多一路，是否真的少一趟？')
for j,h in enumerate(['路数','归并缓冲','归并趟','总传输']):c.text(65+j*245,150,h,42)
for i,p in enumerate(DATA['fan_comparison']):
 for j,v in enumerate([p['fan'],p['buffer_blocks'],p['passes'],p['blocks']]):c.card(55+j*245,260+i*145,220,100,str(v))
maxv=max(p['blocks'] for p in DATA['fan_comparison']);unit=700/maxv
c.text(60,720,'块传输次数（蓝条共用尺度）',42)
c.line((230,870),(930,870))
for tick in range(4):
 value=maxv*tick/3;x=230+value*unit;c.text(x-20,795,str(round(value)),40);c.line((x,850),(x,885))
for i,p in enumerate(DATA['fan_comparison']):
 y=930+i*125;c.text(60,y,f'{p["fan"]}路',42);c.d.rectangle((230,y+15,230+p['blocks']*unit,y+65),fill=BLUE)
vs=[p['blocks'] for p in DATA['fan_comparison']];ls=[v*unit for v in vs]
assert all((a<b)==(x<y) and (a==b)==(x==y) for a,x in zip(vs,ls) for b,y in zip(vs,ls))
c.text(60,1390,'四路要五个数据缓冲块，不能偷用原预算',40,RED)
c.text(60,1480,'趟数按阈值下降，不随内存连续成比例',40)
c.save('11-fanin.png','同一文件二/三/四路实跑，展示增加内存才跨过一趟阈值')

c=Canvas('键相同，怎样不打乱原有先后？')
keys=sorted(set(r[0] for r in DATA['stable']))
for i,key in enumerate(keys):
 rows=[r for r in DATA['stable'] if r[0]==key];y=170+i*155;c.text(60,y+15,f'键 {key}',42)
 nums(c,[f'{r[0]}:{r[1]}' for r in rows],y,step=230,x=250)
c.text(60,1050,'冒号右边是原输入序号，从零开始',42)
c.text(60,1140,'比较 (键, 原序号)：同键记录保持原先先后',40)
c.text(60,1230,'只有键相同，不意味着记录内容可任意交换',40)
c.save('12-stability.png','实际输出重复键的序号，解释复合比较带来的稳定性')

c=Canvas('较大文件也实际分段，再从文件归并')
L=DATA['large'];c.text(60,160,f'{L["n"]} 条记录，文件 {L["input_bytes"]} 字节',44)
c.text(60,270,f'每段 {L["chunk"]} 条；每块 {L["block"]} 条；{L["fan"]} 路',42)
for i,p in enumerate(L['phases']):
 y=440+i*230;c.card(60,y,280,100,f'{p["run_count"]} 段');c.text(410,y+10,f'读 {p["read_blocks"]} / 写 {p["write_blocks"]} 块',42)
 if i<len(L['phases'])-1:c.arrow((200,y+120),(200,y+210))
c.text(60,1210,'输出与独立全量排序基线逐记录一致',42)
c.text(60,1320,'基线只用于校验，不是外部排序内部步骤',40)
c.text(60,1430,'数据很小且有缓存；本图不是磁盘性能测试',40,RED)
c.save('13-file-run.png','真实10000记录文件排序的run数量及逻辑块读写结果')

p=ROOT/'assets/14-live-demo.png'
if p.exists():
 im=Image.open(p);meta.append(dict(file='assets/14-live-demo.png',width=im.width,height=im.height,min_font_px=42,effective_min_font_at_354=14,identity='原创教学网页真实浏览器执行截图',purpose='实际创建二进制临时文件并运行外部归并，展示文件尺寸/趟数/结果',checks=['actual-browser','button-execution','returned-json','viewport-overflow']))
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'figures':len(meta),'checks':'PASS'},ensure_ascii=False))
