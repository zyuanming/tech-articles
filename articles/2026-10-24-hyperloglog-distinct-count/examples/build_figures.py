"""Original HLL figures; MIT code, CC BY 4.0 rendered images."""
from pathlib import Path
import json
from figurekit import Board,BLUE,ORANGE,TEAL,INK,LIGHT
P=Path(__file__).resolve().parent;D=json.loads((P/'results.json').read_text());M=[]
def start(t):b=Board(height=4000);b.text((40,30),t);return b
def save(b,n,p,identity='原创教学示意'):M.append(b.save(P.parent/'assets'/n,p,identity))
def box(b,x,y,t,w=90,fill=LIGHT):
 q=(x,y,x+w,y+80);b.rect(q,fill=fill);b.text((x+w/2,y+40),str(t),anchor='mm',inside=q)
def bits(b,s,x,y,selected=None):
 for i,c in enumerate(s):box(b,x+i*80,y,c,w=68,fill='#fff0e5' if i==selected else LIGHT)
b=start('访问六次，不同身份只有五个')
for i,r in enumerate(D['toy_trace']):box(b,55+i*150,155,r['id'])
for i,c in enumerate(dict.fromkeys(r['id'] for r in D['toy_trace'])):box(b,55+i*150,370,c)
b.text((50,535),f'访问 {len(D["toy_trace"])} 次；不同身份 {D["toy_unique"]} 个');save(b,'01-distinct.png','重复事件数与集合基数的区别')
b=start('同一身份，每次得到同一位串');b.text((40,130),'身份');b.text((260,130),'前四位');b.text((610,130),'后六位')
for i,r in enumerate(D['toy_trace']):
 y=240+i*105;b.text((70,y),r['id']);b.text((260,y),r['prefix']);b.text((610,y),r['suffix'])
save(b,'02-hash.png','短教学映射中重复身份结果固定')
b=start('至少 k 个前导零：概率逐次减半')
for i,(k,p) in enumerate(D['probabilities']):
 y=150+i*120;b.text((40,y),str(k));b.rect((170,y+10,170+p*1400,y+75),fill=BLUE);b.text((900,y),f'1/{2**k}')
save(b,'03-zero-probability.png','稀有位模式的概率尺度','原创概率计算图')
b=start('前缀选桶，后缀才数前导零');r=D['toy_trace'][0];b.text((60,130),'前四位');b.text((530,130),'后六位');bits(b,r['prefix'],40,240);bits(b,r['suffix'],500,240,selected=r['rank']-1);b.arrow((200,345),(200,470));b.arrow((700,345),(700,470),fill=ORANGE);b.text((75,520),f'桶号 {r["bucket"]}');b.text((600,520),f'ρ = {r["rank"]}');save(b,'04-split.png','桶索引与观测后缀严格分开')
b=start('每次只比较一个桶的最大值')
for x,t in [(40,'身份'),(230,'桶号'),(420,'ρ'),(610,'旧值'),(820,'新值')]:b.text((x,135),t)
for i,r in enumerate(D['toy_trace']):
 y=250+i*110
 for x,v in [(70,r['id']),(270,r['bucket']),(430,r['rank']),(650,r['before']),(860,r['after'])]:b.text((x,y),str(v),fill=ORANGE if x==860 and r['after']!=r['before'] else INK)
save(b,'05-update.png','六条输入的具体寄存器变化')
b=start('16 桶：0 表示尚未命中')
for i,v in enumerate(D['toy_registers']):
 x=55+(i%8)*120;y=210+(i//8)*250;b.text((x+40,y-70),str(i),anchor='mt');box(b,x,y,v,w=88,fill='#fff0e5' if v else LIGHT)
save(b,'06-registers.png','最终寄存器向量与索引对照')
b=start('大离群值，怎样影响两种平均')
for i,v in enumerate(D['harmonic_example']['values']):
 y=150+i*130;b.text((40,y),str(i+1));b.rect((170,y+10,170+v*5.5,y+75),fill=BLUE);b.text((900,y),str(v))
b.text((50,760),f'普通平均：{D["harmonic_example"]["arithmetic"]:.3f}');b.text((50,865),f'调和平均：{D["harmonic_example"]["harmonic"]:.3f}');save(b,'07-harmonic.png','同一输入的两种平均行为比较','原创数值计算图')
b=start('指定 16 个寄存器，手算一次')
for i in range(4):
 for j,v in enumerate(D['manual_registers'][i*4:i*4+4]):box(b,250+j*140,150+i*110,v)
b.text((40,680),f'倒数和：4 × 1.125 = {D["manual_denominator"]:g}')
b.text((40,790),f'E = 0.673 × 256 ÷ {D["manual_denominator"]:g}');b.text((40,900),f'估计：{D["manual_raw"]:.3f}');save(b,'08-estimate.png','完整代入调和估计公式','原创数值计算图')
b=start('空集合，原始公式却不是零')
for i in range(16):box(b,55+(i%8)*120,160+(i//8)*120,0,w=88)
b.text((50,500),f'原始公式：{D["empty_raw"]:.3f}');b.text((50,620),f'空桶修正：{D["empty_corrected"]:g}');save(b,'09-empty.png','空状态揭示小范围估计偏差','原创数值计算图')
b=start('空桶 V 越少，估计通常越大')
for i,(v,e) in enumerate(D['small_examples']):
 y=170+i*250;b.text((40,y),f'V = {v}')
 for j in range(16):b.rect((360+j*40,y,390+j*40,y+70),fill='#ffffff' if j<v else BLUE)
 b.text((40,y+120),f'估计 {e:.3f}')
save(b,'10-linear-counting.png','空桶数与线性计数公式的关系','原创概率模型计算图')
b=start('合并：同一位置取较大值')
for i,(name,values) in enumerate(zip(['甲：前八桶','乙：前八桶','合并：前八桶'],D['merge_vector_excerpt'])):
 y=150+i*260;b.text((50,y),name)
 for j,v in enumerate(values):box(b,55+j*120,y+90,v,w=88,fill='#fff0e5' if i==2 else LIGHT)
save(b,'11-merge.png','实际兼容摘要逐桶max等于直接并集状态','教学程序实际运行结果')
b=start('同样记着 5，删除后却不同')
for x,values,remaining in [(80,[3,5],3),(650,[5],0)]:
 for i,v in enumerate(values):box(b,x+i*140,180,v)
 b.arrow((x+50,290),(x+50,400));box(b,x,450,max(values));b.text((x,610),'删掉 5');b.text((x,730),f'应回到 {remaining}')
save(b,'12-deletion.png','最大值丢失次大值所以不可一般删除')
b=start('32 次实验，两种桶数，同一误差轴')
for panel,t in enumerate(D['trials']):
 y0=200+panel*700;b.text((50,y0-90),f'm = {t["m"]}')
 for e in [-20,0,20]:
  yy=y0+200-e*10;b.line([(180,yy),(990,yy)],fill='#acbdcb' if e else INK,width=3);b.text((35,yy-30),f'{e}%')
 for i,e in enumerate(t['relative_errors']):
  x=180+i*810/31;y=y0+200-e*1000;b.ellipse((x-8,y-8,x+8,y+8),fill=ORANGE if e>0 else BLUE,outline=ORANGE if e>0 else BLUE)
 for i in [0,7,15,23,31]:b.text((180+i*810/31,y0+440),str(i+1),anchor='mt')
b.text((50,1500),'横轴：试验序号；纵轴：相对误差')
save(b,'13-errors.png','两组独立盐值实验的实际误差分布','教学程序实际运行统计')
b=start('桶数每增四倍，典型尺度约减半');points=[]
for i,(m,e) in enumerate(D['typical_errors']):
 x=150+i*250;y=650-e*100/15*450;points.append((x,y));b.text((x,y-65),f'{e*100:g}%',anchor='mt');b.text((x,730),str(m),anchor='mt')
b.line(points,fill=BLUE,width=6)
for x,y in points:b.ellipse((x-9,y-9,x+9,y+9),fill=BLUE)
b.line([(100,650),(980,650)],fill=INK);b.text((50,850),'横向一步：桶数 × 4');b.text((50,950),'数值来自 1.04 / √m')
save(b,'14-budget.png','桶数与理论常用相对标准误差尺度','原创概率模型计算图')
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n');print('figures',len(M))
