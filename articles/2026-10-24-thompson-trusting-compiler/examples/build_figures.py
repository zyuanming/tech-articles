from pathlib import Path
import json
from figurelib import *
R=Path(__file__).resolve().parents[1];D=json.loads(Path(__file__).with_name('results.json').read_text());M=[]
def save(b,n,p):M.append(b.save(R/'assets'/n,p))
def flow(title,labels):
 b=Board(title)
 for i,s in enumerate(labels):
  y=140+i*135;b.box((100,y,740,y+75),s,34)
  if i:b.arrow((420,y-60),(420,y))
 return b
save(flow('源文件不能自己变成执行文件',['源文件：给人阅读','编译器：正在运行的工具','产物：给机器执行']),'01-three-things.png','区分源码、工具和产物三种对象')
b=Board('同一份输入，两个工具给不同结果');
for x,lab,out,col in [(40,'普通转换器',D['normal']['text'],BLUE),(460,'带标记转换器',D['marked']['text'],ORANGE)]:
 b.box((x,140,x+340,215),'HELLO');b.arrow((x+170,215),(x+170,300),col);b.box((x,300,x+340,375),lab,34,outline=col);b.arrow((x+170,375),(x+170,460),col);b.box((x,460,x+340,535),out,40,outline=col)
save(b,'02-output.png','无害星号模型直接展示源码与产物不一致')
b=Board('看同一行：改变只发生在产物');b.text(40,140,'输入');b.text(40,250,'普通产物');b.text(40,360,'异常产物');
for i,s in enumerate(['HELLO','HELLO','HELLO*']):
 for j,ch in enumerate(s):b.box((260+j*85,130+i*110,330+j*85,205+i*110),ch,40,outline=ORANGE if ch=='*' else BLUE,fill='#fae8de' if ch=='*' else LIGHT)
save(b,'03-diff.png','逐字符对照无害标记，不将图伪装成软件截图')
save(flow('编译器自己，也来自一条构建链',['编译器源码 S','旧编译器 T 处理 S','新编译器 C']),'04-bootstrap.png','工具源码与工具可执行体不同，构建需要已有工具')
b=Board('两个检查位置，承担不同的结果');b.box((250,130,590,205),'输入是什么？');
for x,s,out in [(40,'普通应用','产物附加 *'),(460,'编译器源码','产物保留标记规则')]:
 b.arrow((420,205),(x+170,315));b.box((x,315,x+340,390),s);b.arrow((x+170,390),(x+170,480));b.box((x,480,x+340,555),out,32)
save(b,'05-two-cases.png','概念状态机区分应用改写与工具规则传递')
b=Board('源文件相同，不表示工具状态相同');
for i,g in enumerate(D['generations']):
 y=140+i*100;b.text(30,y+10,f'第{g["generation"]}代');b.box((190,y,420,y+65),'同一源码',34);b.box((520,y,800,y+65),g['output'],38,outline=ORANGE);b.arrow((420,y+32),(520,y+32),ORANGE)
save(b,'06-generations.png','四代相同源码配上保留标记的工具会重复异常结果')
b=Board('重复构建：两份相同也可能一起错');b.box((250,130,590,205),'同一异常工具');
for x in [40,460]:
 b.arrow((420,205),(x+170,315));b.box((x,315,x+340,390),'HELLO*',40,outline=ORANGE)
b.text(230,455,'相等 ≠ 符合源码',40);save(b,'07-repeat.png','确定性和正确性是不同性质')
b=Board('签名证明来历，不证明计算含义');b.box((180,140,660,230),'带 * 的产物',40,outline=ORANGE);b.d.ellipse((545,175,745,375),outline=TEAL,width=5);b.text(645,275,'签名',36,anchor='mm');b.text(100,430,'仍要检查：它符合源文件吗？',36);save(b,'08-signature.png','真实性验证不能替代源码产物对应验证')
save(flow('独立工具先建立另一份编译器',['编译器源码 S','独立可信工具 T','中间编译器 I']),'09-ddc-first.png','DDC第一阶段得到实现相同源码含义的工具，字节可不同')
save(flow('再让中间编译器编译同一份源码',['同一份编译器源码 S','中间编译器 I','参考产物 R']),'10-ddc-second.png','第二阶段使用待检源码所规定的生成规则')
b=Board('最后比较的是谁和谁？');b.box((40,140,380,220),'参考产物 R');b.box((460,140,800,220),'待检产物 C');b.arrow((210,220),(350,340));b.arrow((630,220),(490,340));b.box((200,340,640,425),'逐字节比较',40);b.text(95,480,'不是比较独立工具T与C',36);save(b,'11-compare.png','精确指出DDC比较对象，避免误认为不同编译器需相同机器码')
b=Board('对应关系与程序安全，是两道问题');b.box((40,140,800,225),'① 这个产物是否对应这份源码？',36);b.arrow((420,225),(420,320));b.box((40,320,800,405),'② 这份源码的行为是否可接受？',36);b.text(70,470,'通过①，仍然必须回答②',36);save(b,'12-boundary.png','DDC不把恶意或错误源码自动变成安全程序')
Path(__file__).with_name('figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n');print(len(M),'figures verified')
