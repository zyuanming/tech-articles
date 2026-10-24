from pathlib import Path
import json
from figurelib import *
R=Path(__file__).resolve().parents[1];D=json.loads(Path(__file__).with_name('results.json').read_text());M=[]
def save(b,n,p):M.append(b.save(R/'assets'/n,p))
b=Board('一条ADD，下方还有三个动作');
for y,s in [(140,'程序：ADD 7'),(300,'控制序列：取地址 / 读数 / 相加'),(460,'数据通路：寄存器 / 内存 / 加法器')]:b.box((35,y,805,y+75),s,size=34)
b.arrow((420,215),(420,300));b.arrow((420,375),(420,460));save(b,'01-layers.png','区分机器指令、控制序列与数据通路')
def path(title,a,mar,mdr,highlight=None):
 b=Board(title);b.box((40,140,300,225),f'A = {a}');b.box((520,140,800,225),f'MDR = {mdr}');b.box((40,370,300,455),f'MAR = {mar}');b.box((520,370,800,455),'内存[7] = 5',size=34);b.circle(420,280,55,'加')
 b.arrow((280,225),(370,265),ORANGE if highlight=='add' else GRAY);b.arrow((540,225),(470,265),ORANGE if highlight=='add' else GRAY);b.arrow((370,300),(180,225),ORANGE if highlight=='add' else GRAY)
 b.arrow((300,412),(520,412),ORANGE if highlight=='address' else GRAY);b.arrow((660,370),(660,225),ORANGE if highlight=='read' else GRAY);return b
save(path('加法之前：先认清四个位置',3,0,0),'02-datapath.png','A存累加值，MAR存地址，MDR存读数，内存存操作数')
for i,t in enumerate(D['trace']):
 b=path(f'微步{t["microaddress"]}：{["先把地址7送入MAR","再把数值5读入MDR","最后把3+5写回A"][i]}',t['after']['A'],t['after']['MAR'],t['after']['MDR'],t['op'])
 if i==2:
  b=Board('微步12：3与5相加，8写回A')
  b.box((40,140,340,220),'旧A = 3');b.box((500,140,800,220),'MDR = 5');b.circle(420,330,55,'加');b.arrow((190,220),(380,290));b.arrow((650,220),(460,290));b.arrow((420,385),(420,470));b.box((250,470,590,550),'新A = 8')
 save(b,f'{i+3:02d}-step.png','同一ADD指令的连续状态变化')
b=Board('控制字：这一拍打开哪些开关？');labels=['取地址','读内存','相加'];
for j,label in enumerate(labels):b.text(185+j*210,150,label,34,anchor='mm')
for i,row in enumerate(D['words']):
 y=210+i*100;b.text(30,y+15,str(D['trace'][i]['microaddress']),size=34)
 for j,v in enumerate(row[:3]):b.box((100+j*210,y,270+j*210,y+70),str(v),fill='#d7e8f7' if v else '#f2f4f6',outline=BLUE if v else GRAY)
save(b,'06-control-bits.png','三个独立控制位逐拍激活，不是存储数据的位')
b=Board('一行控制字，还要告诉下一行');
for i,t in enumerate(D['trace']):
 y=140+i*140;b.box((40,y,250,y+75),f'地址{t["microaddress"]}',size=34);b.box((340,y,800,y+75),f'下一址 = {t["next"]}',size=34);b.arrow((250,y+38),(340,y+38));
 if i<2:b.arrow((740,y+75),(150,y+140))
save(b,'07-next.png','微地址与程序地址是两本不同的编号')
b=Board('条件分支：零标志选择下一个地址');b.box((270,140,570,220),'A 是否为0？');b.arrow((320,220),(180,340));b.arrow((520,220),(660,340));b.box((45,340,325,420),'Z=1 → 20',size=34);b.box((515,340,795,420),'Z=0 → 0',size=34);save(b,'08-branch.png','状态标志参与微序列下一址选择')
b=Board('两个输出同时驱动一根总线');b.box((40,140,330,215),'来源A：3');b.box((510,140,800,215),'来源B：5');b.arrow((185,215),(350,340),ORANGE);b.arrow((655,215),(490,340),ORANGE);b.line((180,340,660,340),ORANGE,9);b.text(180,400,'不是自动得到8',40,fill=ORANGE);b.text(110,470,'冲突控制字必须被排除');save(b,'09-conflict.png','独立控制位不能不受约束地任意组合')
b=Board('水平与编码：宽度换来译码工作');b.text(40,135,'独立控制位');
for i,v in enumerate([0,0,1]):b.box((40+i*250,200,230+i*250,270),str(v))
b.text(40,330,'编码字段');b.box((40,395,310,465),'10',size=40);b.arrow((310,430),(450,430));b.box((450,385,800,475),'译码成“相加”',size=34);save(b,'10-encoding.png','三个互斥动作可编码，但需要译码器且丢失任意并行组合')
b=Board('内存中的程序，控制存储中的步骤');b.box((40,140,360,225),'程序地址100',size=34);b.box((40,280,360,365),'ADD 7');b.arrow((200,225),(200,280));b.arrow((360,320),(480,197));
for i,t in enumerate(D['trace']):b.box((480,160+i*130,800,235+i*130),f'微地址{t["microaddress"]}',size=34)
save(b,'11-two-addresses.png','程序计数器与微程序计数器不同层次')
b=Board('改变控制表，不能变出不存在的通路');b.box((40,140,360,225),'已有：加法器');b.box((480,140,800,225),'没有：除法器');b.arrow((200,225),(200,345));b.box((40,345,360,430),'直接加法');b.arrow((640,225),(640,345),ORANGE);b.box((480,345,800,430),'不能一拍除法',34,fill='#fae8de',outline=ORANGE);save(b,'12-limits.png','微程序只调度已有硬件能力，不能无限替代硬件')
Path(__file__).with_name('figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n');print(len(M),'figures verified')
