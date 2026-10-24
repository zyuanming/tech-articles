from pathlib import Path
import json
from figurelib import *
R=Path(__file__).resolve().parents[1];D=json.loads(Path(__file__).with_name('results.json').read_text());M=[]
def save(b,n,p):M.append(b.save(R/'assets'/n,p))
b=Board('一个输入，两份用途不同的输出');b.box((190,140,650,230),'positive.lit');
for x,label,target in [(35,'tangle：展开片段','generated.py'),(445,'weave：保留讲解','generated.html')]:
 b.arrow((420,230),(x+180,350));b.box((x,350,x+360,430),label,32);b.arrow((x+180,430),(x+180,550));b.box((x,550,x+360,630),target,32)
save(b,'01-two-outputs.png','同一份源面向执行者与读者产生两种派生物')
b=Board('先弄清这个程序到底要做什么');
for i,r in enumerate(D['trace']):
 y=150+i*115;b.circle(105,y+30,35,str(r['value']));b.arrow((150,y+30),(300,y+30));b.box((320,y-10,760,y+70),f'累计 {r["before"]} → {r["after"]}',36,outline=TEAL if r['value']>0 else GRAY)
b.text(60,660,'只加正数：3 + 5 = '+D['stdout'].strip(),38);save(b,'02-values.png','同一贯穿输入逐步执行，零与负数不改变累积值')
b=Board('讲解顺序，不必等于展开后的顺序');b.text(60,135,'文章中',36);b.text(500,135,'程序中',36)
for i,(a,c) in enumerate(zip(['主程序','扫描','函数定义','初值'],['函数头','初值','扫描','调用'])):
 y=210+i*115;b.box((40,y,340,y+70),a,36);b.box((500,y,800,y+70),c,36)
b.text(60,730,'连接两种顺序的是命名引用',36);save(b,'03-orders.png','空间两列不是同一顺序，仅对照不同的组织目的')
b=Board('引用一个名字，就请求展开它');b.box((70,140,770,230),'<<函数定义>>',40);b.arrow((420,230),(420,330));
for i,s in enumerate(['def sum_positive(values):','    <<初值>>','    <<扫描>>','    return total']):b.text(60,350+i*65,s,34)
save(b,'04-reference.png','把名字的使用处与定义体一一对应')
b=Board('依赖图：先回答里面还有哪些名字');b.box((250,140,590,220),'主程序');b.arrow((420,220),(420,315));b.box((250,315,590,395),'函数定义');
for x,n in [(40,'初值'),(470,'扫描')]:b.arrow((420,395),(x+165,520));b.box((x,520,x+330,600),n)
save(b,'05-dependencies.png','递归展开沿有向依赖边继续，最终到无引用片段')
b=Board('第一步展开：主程序看见函数外壳');lines=['def sum_positive(values):','    <<初值>>','    <<扫描>>','    return total','values = [3, -2, 5, 0]','print(sum_positive(values))']
for i,s in enumerate(lines):b.text(40,145+i*75,s,34)
save(b,'06-first-expand.png','一次展开后仍有两个未解析的片段引用')
b=Board('第二步展开：每个名字都有了正文');
for i,s in enumerate(D['expanded_lines']):b.text(35,140+i*70,s,32)
save(b,'07-expanded.png','实际生成Python文件的完整行序与缩进')
b=Board('缩进要相加，不能只做文字粘贴');b.text(50,145,'引用行已有：4个空格',36);b.text(50,235,'片段内if已有：4个空格',36);b.arrow((420,310),(420,400));b.box((70,400,770,490),'展开后if前：8个空格',38);b.text(60,550,'其内累加行：4 + 8 = 12个空格',34);save(b,'08-indent.png','同一递归展开还要携带外层缩进上下文')
b=Board('名字写错：停下来，别默默丢掉');b.box((70,140,770,220),'引用 <<不存在>>');b.arrow((420,220),(420,340),ORANGE);b.box((70,340,770,430),D['errors']['missing'],36,fill='#fff1e7',outline=ORANGE);save(b,'09-missing.png','实际解析器把未定义引用作为错误输出')
b=Board('引用绕回自己：检查当前展开栈');b.box((70,140,340,220),'主程序');b.box((500,140,770,220),'A');b.arrow((340,175),(500,175));b.arrow((500,205),(340,205),ORANGE);b.text(55,335,D['errors']['cycle'],34);b.text(55,435,'重复使用允许；本次调用链循环不行',34);save(b,'10-cycle.png','当前递归路径发现循环，不误禁正常重复引用')
b=Board('讲得清楚，也可能写错一个符号');b.box((40,140,800,225),'正确：total += value',38);b.box((40,310,800,395),'错误：total = value',38,fill='#fff1e7',outline=ORANGE);b.text(80,490,'相同输入：[3, −2, 5, 0]',36);b.text(80,590,f'正确输出：8     错误输出：{D["broken_result"]}',38);save(b,'11-test.png','实际执行错误变体，说明解释与测试职责不同')
b=Board('派生文件改了，下次生成会覆盖');b.box((80,140,760,220),'修改positive.lit');b.arrow((420,220),(420,330));b.box((80,330,760,410),'重新生成程序和文档');b.arrow((420,410),(420,520));b.box((80,520,760,600),'再运行检查和测试');save(b,'12-workflow.png','明确权威源与派生产物的维护路径')
Path(__file__).with_name('figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n');print(len(M),'figures verified')
