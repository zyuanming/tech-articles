#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render original explanatory figures from the accompanying verified data."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, math
P=Path(__file__).resolve().parents[1]; A=P/'assets';A.mkdir(exist_ok=True)
R=json.loads((P/'examples/expected-results.json').read_text())
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
W=1062; BG='#f7f4ec'; INK='#142b35'; TEAL='#077f78'; ORANGE='#c55d23'; PURPLE='#6b56a0'; GRAY='#5c6b70'; BLUE='#e2eef7'; GREEN='#dcefe7'; GOLD='#ffedcd'; RED='#f7dddd'
meta=[]; im=None;d=None;smallest=100

def font(s=44,b=False,mono=False): return ImageFont.truetype(MONO if mono else BOLD if b else FONT,s,index=0 if mono else 2)
def text(x,y,t,s=44,c=INK,b=False,mono=False,anchor=None):
 global smallest
 smallest=min(smallest,s)
 d.text((x,y),str(t),font=font(s,b,mono),fill=c,anchor=anchor)
def box(x,y,w,h,fill='white',stroke=None,r=22):d.rounded_rectangle((x,y,x+w,y+h),r,fill,stroke,width=3)
def line(points,c=INK,w=5):d.line(points,fill=c,width=w)
def arrow(x1,y1,x2,y2,c=TEAL,w=7):
 line([(x1,y1),(x2,y2)],c,w);ang=math.atan2(y2-y1,x2-x1);sz=20
 d.polygon([(x2,y2),(x2-sz*math.cos(ang-.5),y2-sz*math.sin(ang-.5)),(x2-sz*math.cos(ang+.5),y2-sz*math.sin(ang+.5))],fill=c)
def new(title,h=820,kicker=None):
 global im,d,smallest
 smallest=100;im=Image.new('RGB',(W,h),BG);d=ImageDraw.Draw(im)
 d.rectangle((0,0,18,h),fill=TEAL)
 text(52,35,title,54,b=True)
 if kicker:text(52,115,kicker,40,c=GRAY)
def save(name,purpose,evidence,kind='original_diagram'):
 im.save(A/(name+'.png'))
 meta.append({'file':'assets/'+name+'.png','purpose':purpose,'evidence':evidence,'kind':kind,'width':W,'height':im.height,'minimum_font_px':smallest,'effective_minimum_at_354px':smallest/3,'rights':'Original design CC BY 4.0; original example code MIT; factual tool-output excerpts identified in caption.'})
def bytes_row(values,y,high=None,x=76,cw=172):
 for i,v in enumerate(values):
  box(x+i*cw,y,cw-12,115,GOLD if high and i in high else GREEN)
  text(x+i*cw+(cw-12)/2,y+27,v,55,mono=True,anchor='mt')

new('先看见：分开做，最后能接上',840,'下面是本次真实构建与运行结果的排印')
for y,name,label in [(195,'start.s → start.o','汇编成功'),(330,'answer.c → answer.o','编译成功')]:
 box(52,y,958,105,'white');text(78,y+22,name,44,mono=True);text(780,y+26,label,40,c=TEAL)
arrow(531,462,531,525)
box(52,545,958,230,INK);text(84,570,'$ ./normal; echo $?',44,c='white',mono=True);text(84,636,str(R['builds']['normal']['exit_code']),86,c='#8ce0c7',b=True);text(270,670,'42 是退出状态，由 shell 显示',40,c='white')
save('01-observed-result','先给可感知的真实运行结果，解释42是退出状态','reproduce.py: compile/assemble and execute-normal','typeset_actual_result')

new('两份文件先各自完成，再合并',1040)
for x,source,role,obj,col in [(52,'start.s','请 answer 给我一个数','start.o',BLUE),(562,'answer.c','把 42 交回去','answer.o',GREEN)]:
 box(x,165,448,215,col);text(x+30,188,source,50,b=True,mono=True)
 text(x+30,270,role,36)
 arrow(x+224,401,x+224,474)
 box(x,498,448,168,'white',TEAL);text(x+30,518,obj,50,mono=True);text(x+30,587,'机器码 + 必要记录',38)
arrow(276,696,430,780);arrow(786,696,632,780)
box(260,796,540,165,INK);text(530,820,'链接器 ld',50,c='white',b=True,anchor='mt');text(530,886,'输出可执行文件 normal',38,c='white',anchor='mt')
save('02-separate-files','把汇编/编译与链接分成可见两阶段','start.s, answer.c; GNU as/gcc/ld verified')

new('打开 start.o：它真的是 ELF',1020,'真实文件头字节与 readelf 结果，选取相关部分')
box(52,185,958,170,INK);text(80,205,'7f 45 4c 46 02 01',54,c='#8ce0c7',mono=True);text(80,286,'文件开头 6 字节（十六进制）',40,c='white')
for y,a,b,col in [(400,'ELF64 / X86-64','64 位格式 / 指令体系',BLUE),(535,'.text  14 bytes','保存这份文件的机器指令',GREEN),(670,'.symtab','登记定义和需要的名字',GOLD),(805,'.rela.text','记录尚待处理的补丁',RED)]:
 box(52,y,958,112,col);text(78,y+12,a,44,mono=True);text(78,y+64,b,38)
save('03-elf-object','展示真实目标文件内部身份及必要节','readelf -hW/-SW start.o; independent ELF parser','typeset_actual_fields')

new('同一个名字，一边需要，一边提供',980,'readelf -sW 的 answer 条目：选列、去前导零')
for y,obj,ndx,size,col in [(185,'start.o','UND',0,RED),(528,'answer.o','1',6,GREEN)]:
 box(52,y,958,277,col);text(82,y+20,obj,50,b=True,mono=True)
 text(82,y+104,'Name     Bind     Ndx',40,mono=True);text(82,y+166,f'answer   GLOBAL   {ndx}',40,mono=True)
 text(82,y+222,f'Value = 0     Size = {size}',40,mono=True)
arrow(531,479,531,515)
text(52,854,'上方 UND：这份文件里没有定义',42,c=ORANGE)
text(52,919,'下方 1：定义在第 1 节的偏移 0',42,c=TEAL)
save('04-symbols','避免把UND的0误认为真实地址；两份符号匹配','readelf -sW start.o / answer.o','typeset_actual_fields')

new('call 已经有字节，距离还没填好',900,'objdump -drw start.o 的关键输出，拆行排印')
box(52,185,958,240,INK)
text(80,208,'0: e8 00 00 00 00',48,c='white',mono=True)
text(80,280,'call 5 <_start+0x5>',46,c='#8ce0c7',mono=True)
text(80,350,'1: R_X86_64_PLT32 answer-0x4',44,c='#ffcf83',mono=True)
bytes_row(['e8','00','00','00','00'],495,{1,2,3,4})
text(75,654,'调用操作',40,c=TEAL);text(360,654,'4 字节：有待链接器修补',40,c=ORANGE)
text(52,766,'不要把暂时反汇编出的 “5”',46,b=True)
text(52,828,'当作已经确定的 answer 位置。',46,b=True)
save('05-call-before','给出真正未链接指令及暂时反汇编的陷阱','objdump -drw start.o','typeset_actual_output')

new('偏移要先问：从哪里开始数？',1130)
for y,title,eq,desc,col in [(180,'在 start.o 的 .text 内','0 + 1 = 1','重定位记录里的 Offset',GOLD),(402,'在 start.o 整个文件内','64 + 1 = 65','同一字段在磁盘文件中的位置',BLUE),(624,'在 normal 整个文件内','4096 + 1 = 4097','输出文件的 .text 搬到了别处',GREEN),(846,'在 normal 的虚拟地址空间','0x401000 + 1','得到 0x401001，不是物理地址',RED)]:
 box(52,y,958,195,col);text(80,y+13,title,42,b=True);text(80,y+68,eq,47,mono=True);text(80,y+129,desc,38)
save('06-three-coordinates','区分节内偏移、文件偏移和虚拟地址，禁止混减','readelf sections start.o and normal; independently parsed ELF')

new('一条重定位记录，交代四件事',1120,'readelf -rW start.o：把同一行拆成四张便签')
for y,a,b,c,col in [(185,'Offset = 1','改哪里？','从 .text 起点往后 1 字节',GOLD),(402,'Type = R_X86_64_PLT32','怎样改？','本例是 32 位调用相对位移',BLUE),(619,'Symbol = answer','找谁？','到符号表里找 answer 的定义',GREEN),(836,'Addend = -4','额外加什么？','把补丁位置换算到下一指令',RED)]:
 box(52,y,958,191,col);text(78,y+10,a,43,mono=True);text(78,y+69,b,44,b=True);text(78,y+132,c,38)
save('07-relocation-recipe','重定位数据不是泛泛待办，四字段可操作','readelf -rW start.o; type4 and addend-4','typeset_actual_fields')

new('链接器先安排位置，再补距离',1030,'本次输出 .text 起点选为 0x401000')
box(52,198,958,210,BLUE);text(82,225,'start.o 的 .text',49,b=True);text(82,296,'14 字节',54,c=TEAL);text(500,308,'偏移 0 到 13',42)
box(52,428,958,210,GREEN);text(82,453,'answer.o 的 .text',49,b=True);text(82,528,'6 字节',54,c=TEAL);text(500,538,'偏移 14 到 19',42)
text(52,693,'本次排列没有中间填充。',42,c=GRAY)
box(52,780,958,192,INK);text(82,799,'_start   0x401000',49,c='white',mono=True);text(82,885,'answer   0x40100e',49,c='#8ce0c7',mono=True)
save('08-linked-layout','用实测14+6布局确定两个函数位置','normal ELF symbols / .text; linker input order')

new('真正被改掉的是哪几个字节？',1000)
text(52,156,'链接前：start.o',45,b=True);bytes_row(['e8','00','00','00','00'],234,{1,2,3,4})
arrow(531,377,531,462)
text(52,490,'链接后：normal',45,b=True);bytes_row(R['builds']['normal']['call_bytes'].split(),568,{1,2,3,4})
box(52,747,958,195,INK);text(80,772,'401000: e8 09 00 00 00',44,c='white',mono=True);text(80,850,'call 40100e <answer>',46,c='#8ce0c7',mono=True)
save('09-patched-bytes','把输出二进制的实际变化和反汇编连起来','objdump -drw normal; independent byte diff','typeset_actual_output')

new('距离从“下一条指令”开始算',1050)
# Byte scale at 42 px/cell; 20 cells spans840. Labels not in every cell.
x0=80;cw=45;y=220
for i in range(20):
 col=GOLD if i<5 else BLUE if i<14 else GREEN
 d.rectangle((x0+i*cw,y,x0+(i+1)*cw-3,y+110),fill=col)
 if i in [0,5,14,19]:text(x0+i*cw+cw/2,y+132,i,38,anchor='mt')
text(80,159,'.text 内的字节位置',42)
for i,col in [(0,ORANGE),(5,PURPLE),(14,TEAL)]:line([(x0+i*cw,y-6),(x0+i*cw,y+116)],col,6)
text(52,443,'call 起点：偏移 0',46,c=ORANGE)
text(52,525,'call 长 5 字节，下一指令在 5',46,c=PURPLE)
text(52,607,'answer 起点：偏移 14',46,c=TEAL)
box(52,736,958,244,'white');text(531,763,'14 − 5 = 9',83,b=True,anchor='mt');text(531,884,'因此向前走 9 字节，就到 answer',40,anchor='mt')
save('10-relative-distance','不用大地址也能数清call距离基准','normal: start offset0, next5, answer14')

new('为什么记录上还写了一个 −4？',1110)
bytes_row(['e8','??','??','??','??'],210,{1,2,3,4})
text(75,367,'偏移 0',40);text(255,367,'P：偏移 1',40,c=ORANGE)
text(52,463,'P 是待填四字节字段的开头。',46)
text(52,541,'CPU 从字段后面的第一个字节算。',42)
text(52,595,'它就是下一条指令的位置：P+4。',40)
box(52,652,958,205,INK);text(85,671,'D = S - (P + 4)',49,c='white',mono=True);text(85,758,'     = S + (-4) − P',49,c='#8ce0c7',mono=True)
text(52,916,'S = answer 的最终地址',44,c=TEAL)
text(52,989,'A = −4，是这次记录里的附加数',44,c=ORANGE)
save('11-addend-origin','由CPU下一指令基准推导-4而非死记公式','x86-64 call rel32 encoding and normal ELF relocation')

new('只插入 16 字节，补丁就变了',1060,'同一份 start.o 和 answer.o，没有重新编译')
for y,title,parts,ans,disp in [(180,'原排列',[(0,14,BLUE),(14,6,GREEN)],14,9),(510,'插入 16 个 nop 字节',[(0,14,BLUE),(14,16,GOLD),(30,6,GREEN)],30,25)]:
 text(52,y,title,46,b=True);xx=52;total=36
 for _,n,col in parts:
  ww=958*n/total;box(xx,y+85,ww-8,105,col,r=9);text(xx+ww/2,y+105,str(n),46,anchor='mt');xx+=ww
 text(52,y+220,f'目标偏移 {ans} − 下一指令偏移 5 = {disp}',40)
box(52,868,958,140,INK);text(85,890,'e8 19 00 00 00',55,c='#8ce0c7',mono=True);text(650,914,'0x19 = 25',40,c='white',mono=True)
save('12-padding-experiment','只改布局真实重链接，证明编译器原先不知道距离','padded actual ELF / displacement25 / nop16','actual_experiment_diagram')

new('如果 answer 排在前面呢？',1080,'同样输入，链接顺序改为 answer.o、start.o')
box(52,178,315,140,GREEN);text(209,201,'answer',48,mono=True,anchor='mt');text(209,259,'6 字节',38,anchor='mt')
box(382,178,628,140,BLUE);text(696,201,'_start',48,mono=True,anchor='mt');text(696,259,'14 字节',38,anchor='mt')
arrow(677,405,90,405,ORANGE);text(52,460,'下一指令偏移 11 → 目标偏移 0',44)
box(52,568,958,150,'white');text(531,589,'0 − 11 = −11',74,b=True,anchor='mt')
box(52,772,958,225,INK);text(82,793,'e8 f5 ff ff ff',58,c='#8ce0c7',mono=True);text(82,885,'32 位有符号位移：−11',44,c='white');text(82,944,'回验：11 + (−11) = 0',40,c='white')
save('13-negative-displacement','用实测倒排解释负位移和补码字节','reversed ELF call bytes f5ffffff / target401000 / next40100b','actual_experiment_diagram')

new('整块搬家，内部距离为什么不变？',1040,'两次是分别重新链接、分别运行的静态文件')
for y,start,target in [(183,'0x401005','0x40100e'),(510,'0x501005','0x50100e')]:
 box(52,y,958,240,'white');text(82,y+15,'下一指令',40,c=PURPLE);text(610,y+15,'answer',40,c=TEAL)
 text(82,y+80,start,44,mono=True);text(610,y+80,target,44,mono=True)
 arrow(270,y+180,762,y+180);text(525,y+128,'+9',47,c=TEAL,anchor='mt')
text(52,814,'两端都加 0x100000，相减时抵消。',43)
text(52,897,'这证明片段的相对距离不变；',43,c=ORANGE)
text(52,967,'并没有证明整个 normal 是 PIE。',43,c=ORANGE)
save('14-shifted-distance','验证相对距离平移不变并明确不是运行期PIE试验','normal / shifted separately linked and exit42','actual_experiment_diagram')

new('第一种失败：名字没有找到定义',960,'故意只把 start.o 交给静态链接器')
box(52,175,390,160,BLUE);text(247,193,'start.o',51,mono=True,anchor='mt');text(247,275,'需要 answer',40,anchor='mt')
arrow(468,255,601,255);box(628,175,382,160,RED);text(819,191,'缺席',64,c=ORANGE,b=True,anchor='mt');text(819,277,'answer.o',40,mono=True,anchor='mt')
box(52,428,958,255,INK);text(82,451,'(.text+0x1):',47,c='white',mono=True);text(82,524,'undefined reference',46,c='#ffb6a3',mono=True);text(82,597,"to `answer'",47,c='#ffb6a3',mono=True)
text(52,738,'真实错误选取关键部分、换行排印。',40,c=GRAY)
text(52,823,'start.o 能生成；最终静态链接失败。',43,b=True)
text(52,897,'缺的是定义，不是需要重做算术。',43)
save('15-missing-symbol','真实失败帮助区分汇编/编译成功与链接成功','link-missing.stderr exit1','typeset_actual_error')

new('第二种失败：同名强定义来了两份',940,'故意把 answer.o 在链接命令里写两遍')
for x in [52,562]:
 box(x,178,448,208,GREEN);text(x+224,200,'answer.o',49,mono=True,anchor='mt');text(x+224,282,'定义 answer',44,anchor='mt')
arrow(276,413,438,500);arrow(786,413,625,500)
box(52,535,958,190,INK);text(82,560,'multiple definition',48,c='#ffb6a3',mono=True);text(82,641,"of `answer'",48,c='#ffb6a3',mono=True)
text(52,786,'普通强全局定义不能这样重复。',46,b=True)
text(52,863,'这是本例；弱符号等另有选择规则。',42,c=GRAY)
save('16-duplicate-symbol','用真实重复定义反例说明名字匹配还要遵守规则','link-duplicate.stderr exit1','typeset_actual_error')

new('普通 C 调用，也留下同样的线索',1180,'补充实验：caller.c 单独用 gcc -c 编译')
box(52,179,958,280,INK)
for yy,s in [(202,'int answer(void);'),(275,'int caller(void) {'),(348,'  return answer() + 1;'),(404,'}')]:text(82,yy,s,42,c='white',mono=True)
arrow(531,483,531,552)
box(52,578,958,306,BLUE);text(82,596,'caller.o：真实 objdump 选行',41,b=True)
text(82,678,'4: e8 00 00 00 00',46,mono=True);text(82,752,'5: R_X86_64_PLT32',44,mono=True);text(82,820,'answer-0x4',44,mono=True)
text(52,948,'call 在偏移 4，补丁字段在偏移 5。',43)
text(52,1034,'“声明它存在”不等于“提供它的代码”。',42)
text(52,1102,'具体字节由编译选项和版本共同决定。',40,c=GRAY)
save('17-c-compiler-evidence','从透明汇编入口桥接到真实C编译调用','caller.c; objdump -drw caller.o, original code MIT','typeset_actual_code_output')

new('三个问题，发生在不同层次',1190)
items=[(170,'构建时：静态链接器','在哪里安排代码、哪些字段要修补？','本例：answer 已接好，输出 normal',BLUE),(486,'加载时：系统与动态链接器','把程序和所需共享库装入进程。','若留下动态重定位，再按其规则处理。',GREEN),(802,'执行时：CPU 与操作系统','程序访问的虚拟地址对应什么物理页？','这是地址翻译，不是本文的符号匹配。',GOLD)]
for y,title,l1,l2,col in items:
 box(52,y,958,250,col);text(80,y+18,title,44,b=True);text(80,y+103,l1,39);text(80,y+170,l2,38)
 if y<800:arrow(531,y+261,531,y+300)
text(52,1101,'本例无动态解释器；动态流程只作边界示意。',38,c=GRAY)
save('18-link-load-execute','分开静态链接、动态链接与虚拟内存职责','ELF program loading/dynamic linking gABI; normal has no PT_INTERP','original_boundary_diagram')

# Independent article cover, not a body figure.
new('代码分开编译',880)
text(52,120,'函数地址，最后是谁填上的？',56,b=True)
text(52,237,'从真实 ELF 字节里，找到链接器的工作',41,c=GRAY)
box(52,352,958,162,INK);text(531,386,'e8 00 00 00 00',75,c='white',mono=True,anchor='mt')
arrow(531,541,531,618,ORANGE)
box(52,646,958,162,TEAL);text(531,680,'e8 09 00 00 00',75,c='white',mono=True,anchor='mt')
im.save(P/'cover.png')
meta.append({'file':'cover.png','purpose':'独立封面以实际call补丁前后作为视觉中心','evidence':'normal byte patch','kind':'original_cover','width':W,'height':880,'minimum_font_px':smallest,'effective_minimum_at_354px':smallest/3,'rights':'Original CC BY 4.0'})
(P/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('Rendered',len(meta)-1,'body figures and one cover.')
