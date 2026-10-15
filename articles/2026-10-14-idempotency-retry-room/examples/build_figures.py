#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original teaching diagrams and faithful charts of the actual local SQLite output."""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'assets';A.mkdir(exist_ok=True)
D=json.loads((ROOT/'examples/expected-results.json').read_text())['cases']
# Bind fixed teaching labels to actual output, rather than silently drawing stale numbers.
expected_counts={'unsafe_response_ignored':2,'safe_response_ignored':1,'new_intent_same_parameters':2,'same_key_different_parameters':1,'same_key_different_actor':2,'before_commit':1,'after_commit':1,'effect_first':2,'marker_first':0,'concurrent_same_key':1,'receipt_expired':2,'resource_lifecycle':1}
for name,n in expected_counts.items():assert len(D[name]['final']['rooms'])==n,(name,n)
assert D['safe_response_ignored']['retry']['body']=={'mode':'duo','room_id':'R001'}
assert D['safe_response_ignored']['first_server_result']['body']==D['safe_response_ignored']['retry']['body']
assert D['safe_response_ignored']['retry']['status']==201
assert D['new_intent_same_parameters']['second']['body']['room_id']=='R002'
assert D['same_key_different_parameters']['rejected']=='same actor/key, different parameters'
assert D['concurrent_same_key']['outcomes_sorted_by_replayed']==[dict(status=201,body={'mode':'duo','room_id':'R001'},replayed=False),dict(status=201,body={'mode':'duo','room_id':'R001'},replayed=True)]
assert D['receipt_expired']['retention_ticks']==10 and D['receipt_expired']['retry_tick']==11
assert not D['receipt_expired']['after_purge']['receipts'] and len(D['receipt_expired']['after_purge']['rooms'])==1
assert D['receipt_expired']['late_retry']['body']['room_id']=='R002'
assert D['resource_lifecycle']['final']['rooms'][0]['active'] is False
assert D['resource_lifecycle']['retry']['body']=={'mode':'duo','room_id':'R001'}
W=1062;BG='#f5f3eb';INK='#283e4a';BLUE='#267c94';GREEN='#43805d';RED='#b25158';GOLD='#c28e40';GRAY='#707974';LIGHT='#d4dcd8';WHITE='#ffffff'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc';MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf';meta=[];bounds=[]
def f(s=42,b=False,mono=False):return ImageFont.truetype(MONO if mono else BOLD if b else FONT,s,index=0 if mono else 2)
def tx(x,y,t,s=42,c=INK,b=False,anchor=None,mono=False):
 global smallest;smallest=min(smallest,s);bb=d.textbbox((x,y),str(t),font=f(s,b,mono),anchor=anchor);bounds.append(dict(figure=current,text=str(t),bbox=bb)) if bb[0]<24 or bb[2]>W-24 or bb[1]<0 or bb[3]>im.height else None;d.text((x,y),str(t),font=f(s,b,mono),fill=c,anchor=anchor)
def ln(points,c=INK,w=6):d.line(points,fill=c,width=w)
def arrow(x1,y1,x2,y2,c=BLUE,w=6):
 ln([(x1,y1),(x2,y2)],c,w);q=math.atan2(y2-y1,x2-x1);d.polygon([(x2,y2),(x2-19*math.cos(q-.5),y2-19*math.sin(q-.5)),(x2-19*math.cos(q+.5),y2-19*math.sin(q+.5))],fill=c)
def box(x,y,w,h,fill=WHITE,outline=LIGHT,r=18):d.rounded_rectangle((x,y,x+w,y+h),r,fill=fill,outline=outline,width=3)
def new(title,h,sub):
 global im,d,smallest,current
 current=title
 im=Image.new('RGB',(W,h),BG);d=ImageDraw.Draw(im);smallest=99;d.rectangle((0,0,15,h),fill=BLUE);tx(48,34,title,52,b=True);tx(48,116,sub,38,c=GRAY)
def save(n,purpose,identity='Original explanatory diagram, not a product screenshot'):
 im.save(A/(n+'.png'));meta.append(dict(file='assets/'+n+'.png',purpose=purpose,identity=identity,width=W,height=im.height,minimum_font_px=smallest,effective_minimum_at_354px=smallest/3))
def room(x,y,label,c=BLUE):
 box(x,y,228,128,outline=c);tx(x+114,y+20,label,46,c,b=True,anchor='mt');tx(x+114,y+79,'双人房',36,anchor='mt')
def chip(x,y,label,c=BLUE,w=225):box(x,y,w,88,outline=c);tx(x+w/2,y+16,label,43,c,b=True,anchor='mt')
def cross(x,y):ln([(x-19,y-19),(x+19,y+19)],RED,9);ln([(x-19,y+19),(x+19,y-19)],RED,9)

new('没有回音，可能发生了不同的事',1530,'横向是两位参与者；每个小图中，时间向下')
for top,title,kind in [(210,'① 请求没到：还没有房间','request_lost'),(820,'② 已经建好：成功回信没到','reply_lost')]:
 tx(48,top,title,46,b=True);tx(250,top+90,'玩家',42,anchor='mt');tx(820,top+90,'服务器',42,anchor='mt')
 ln([(250,top+170),(250,top+475)],LIGHT,4);ln([(820,top+170),(820,top+475)],LIGHT,4)
 if kind=='request_lost':
  arrow(250,top+205,520,top+245);cross(545,top+248);tx(300,top+149,'创建请求',38);tx(694,top+305,'房间数：0',42,c=RED)
 else:
  arrow(250,top+205,820,top+245);tx(365,top+149,'创建请求',38);chip(705,top+285,'R001',GREEN,230);arrow(820,top+405,545,top+445,GREEN);cross(520,top+448);tx(555,top+455,'成功回信',38,c=GREEN)
 tx(48,top+515,'玩家只看到：等了一阵，还没收到成功。',40)
save('01-no-reply-two-worlds','从玩家相同观察区分未执行和已执行两种隐藏状态')

new('直接再创建，数据库里真多了一间',1130,'本地SQLite实际执行；“丢回信”由调用方忽略结果模拟')
for y,lab,result in [(235,'第一次调用',D['unsafe_response_ignored']['first_server_result']),(465,'再次调用',D['unsafe_response_ignored']['retry'])]:
 tx(65,y,lab,44,b=True);arrow(335,y+58,635,y+58);room(715,y-5,result['room_id'])
box(48,730,966,290);tx(78,752,'实际读取 rooms 表',43,b=True);tx(95,845,'房间',38,c=GRAY);tx(360,845,'主人',38,c=GRAY);tx(620,845,'模式',38,c=GRAY)
for j,r in enumerate(D['unsafe_response_ignored']['final']['rooms']):tx(95,903+j*48,r['id'],38,mono=True);tx(360,903+j*48,r['owner'],38,mono=True);tx(620,903+j*48,r['mode'],38,mono=True)
tx(48,1060,'duo 是程序里的“双人房”模式名。',39)
save('02-unsafe-real-rows','真实两次INSERT后的两行数据，不把无回音当没创建','Faithful typesetting of actual SQLite results, not a terminal screenshot')

new('编号回答的是：这是不是同一次意图',1330,'同一玩家 p7；所有箭头都请求创建 duo 房间')
tx(48,223,'同一次创建，重试要带同一编号',44,b=True)
chip(65,321,'K17');chip(65,464,'K17');arrow(315,366,630,423);arrow(315,509,630,423);room(704,360,'R001',GREEN)
tx(68,604,'第一次发出前取编号；重试保留它。',40)
ln([(48,716),(1014,716)],LIGHT,3)
tx(48,777,'确实想再开一间，才是新的意图',44,b=True)
chip(65,883,'K18');arrow(315,927,630,927);room(704,870,'R002')
tx(48,1080,'参数都写“双人房”，也可能是两次愿望。',40)
tx(48,1173,'只比较参数，会把第二间错误地合并掉。',40,c=RED)
save('03-intent-and-retry','重复送达的同次意图与参数相同的新意图区别，建立K17/K18身份')

new('除了房间，还要记住这次创建的回执',1390,'这是同一数据库里的两张表；仅服务“创建房间”')
box(48,230,966,275);tx(78,256,'rooms：实际创建的房间',44,b=True)
for x,t in [(90,'房间号'),(375,'主人'),(670,'模式')]:tx(x,344,t,38,c=GRAY)
for x,t in [(90,'R001'),(375,'p7'),(670,'duo')]:tx(x,415,t,44,mono=True)
arrow(531,535,531,627,GREEN)
box(48,660,966,476);tx(78,688,'receipts：按意图查回原结果',44,b=True)
for y,t in [(785,'玩家：p7      编号：K17'),(863,'原参数：mode = duo'),(941,'原成功结果：room_id = R001'),(1019,'保存的成功状态码：201')]:tx(90,y,t,40)
tx(48,1190,'查找范围是“玩家 + 编号”，不是全世界共用。',39)
tx(48,1265,'201 是本例保存的首次创建成功状态。',39)
save('04-room-and-receipt','展示实际资源与意图回执字段，区别房间号和操作键')

new('把“建房”和“记回执”放进同一笔事务',1580,'本例用SQLite：BEGIN IMMEDIATE先取得写事务')
# Main path intentionally vertical and wide; duplicate branch visibly leaves early.
for y,t in [(225,'① 取得写事务'),(385,'② 按 p7 + K17 查回执'),(705,'③ 没找到：创建 R001'),(865,'④ 保存参数与成功结果'),(1025,'⑤ 一起提交')]:
 box(65,y,885,109);tx(507,y+28,t,42,b=True,anchor='mt')
for y1,y2 in [(334,385),(814,865),(974,1025)]:arrow(507,y1+7,507,y2-8)
arrow(507,494,507,691);tx(552,541,'没找到',38)
box(65,539,337,108,outline=GREEN);tx(233,561,'找到了：复用',38,c=GREEN,b=True,anchor='mt');arrow(185,494,185,534,GREEN)
# Bracket means atomic database boundary, not command simultaneously executed.
ln([(982,222),(1002,222),(1002,1135),(982,1135)],GREEN,6)
arrow(507,1143,507,1224,GREEN);tx(507,1266,'提交后，才把成功回给玩家',43,c=GREEN,b=True,anchor='mt')
tx(48,1396,'事务使两项修改一起留下，或都不留下。',40)
tx(48,1473,'复用前仍核对参数；已有回执分支不再建房。',39)
save('05-one-transaction','把首次执行和重放分支走通，明确记录与副作用一起提交的边界')

new('同一编号重发，复用的就是这份结果',1280,'以下为实际SQLite运行结果的中文排版，不是产品界面')
for y,lab,res in [(225,'首次：创建',D['safe_response_ignored']['first_server_result']),(578,'重试：复用',D['safe_response_ignored']['retry'])]:
 box(48,y,966,283,outline=GREEN if res['replayed'] else BLUE);tx(78,y+23,lab,45,b=True);tx(90,y+105,'p7 + K17 → '+res['body']['room_id'],44,mono=True);tx(90,y+187,'status = 201; mode = duo',38,mono=True)
tx(48,979,'最终 rooms 表：1 行；receipts 表：1 行。',42,b=True)
tx(48,1074,'请求执行了查找，但没有再执行一次建房。',40)
tx(48,1154,'重试标记只在实验日志里，不属于保存的正文。',38)
save('06-safe-real-result','实际重试所得状态码与结果一致，区分处理请求与重复副作用','Faithful typesetting of actual SQLite results, not an HTTP capture or terminal screenshot')

new('只把顺序换一换，堵不住中间的缝',1470,'下面故意把两件事拆成两个独立提交')
for top,title,left,right,outcome in [(215,'先建房，后记回执','房间提交','回执提交','中断后重试：没回执，又建了R002。'),(820,'先留记号，后建房','记号提交','房间提交','中断后重试：见记号跳过，结果0间。')]:
 tx(48,top,title,46,b=True);chip(65,top+125,left,BLUE,330);chip(665,top+125,right,GRAY,330);arrow(410,top+168,647,top+168,GRAY);cross(531,top+168);tx(531,top+245,'进程在这里终止',39,c=RED,anchor='mt');tx(48,top+359,outcome,39);tx(48,top+438,'第一笔提交成功，不代表第二笔已经完成。',38)
save('07-two-bad-orders','用实际两个非原子终止案例说明资源先/记号先都有失配窗口')

new('同一笔事务，提交前后是两种恢复结果',1490,'真实子进程终止实验；不是断电、设备故障或真实丢包')
for top,title,bef,after in [(220,'① 插入房间后，提交前终止',D['before_commit']['before_retry'],D['before_commit']['final']),(825,'② 已提交，函数返回前终止',D['after_commit']['before_retry'],D['after_commit']['final'])]:
 tx(48,top,title,44,b=True)
 box(48,top+115,430,230);box(584,top+115,430,230,outline=GREEN)
 tx(263,top+136,'重新连接后',39,anchor='mt');tx(799,top+136,'同K17重试后',39,anchor='mt')
 for x,state in [(80,bef),(616,after)]:tx(x,top+218,'房间 '+str(len(state['rooms']))+' / 回执 '+str(len(state['receipts'])),39)
 arrow(488,top+230,572,top+230,GREEN)
 tx(48,top+410,'重试会首次完成这次创建。' if top==220 else '重试读取已存结果，不再新建。',41,c=GREEN,b=True)
 tx(48,top+492,'子进程 exit = '+str(86 if top==220 else 87)+'；结果由实际数据库表读取。',37)
save('08-process-exit-real','真实进程退出前后再连接的0/0或1/1记录，与重试之后1/1区分','Faithful chart of actual child-process exit and SQLite row counts; not a power-loss experiment')

new('同时到达，也不能各自认领“第一次”',1350,'两个线程各用一个SQLite连接；谁先取得写事务不固定')
chip(65,230,'请求 A',BLUE,300);chip(697,230,'请求 B',GOLD,300)
tx(215,357,'p7 + K17',38,anchor='mt',mono=True);tx(847,357,'p7 + K17',38,anchor='mt',mono=True)
arrow(215,438,410,580);arrow(847,438,651,580,GOLD)
box(185,615,692,152,outline=GREEN);tx(531,650,'数据库：此时只放行一个写者',40,b=True,anchor='mt');tx(531,712,'另一个等待；不是同时先查再写',36,anchor='mt')
arrow(531,780,531,873,GREEN)
box(48,905,966,229);tx(78,931,'实际输出（按是否复用排序）',41,b=True);tx(90,1004,'一次 created → R001',39);tx(90,1064,'一次 replayed → R001',39)
tx(48,1204,'1间房、1份回执；并未固定A一定先赢。',40)
save('09-concurrent-callers','两个连接同键竞争与串行写事务的实际结果，不暗示SELECT自身可防重','Original concurrency diagram plus faithful summary of actual two-thread SQLite results')

new('同一个编号，不能偷偷换成另一件事',1190,'服务器先比较保存的参数，再决定是否复用')
box(48,225,966,240,outline=BLUE);tx(78,252,'已有回执',43,b=True);tx(90,339,'p7 + K17; mode = duo',39,mono=True)
box(48,535,966,240,outline=RED);tx(78,562,'新的来信',43,b=True);tx(90,649,'p7 + K17; mode = squad',39,mono=True)
cross(531,495)
tx(48,858,'duo = 双人；squad = 小队。意图参数变了。',39)
tx(48,950,'本例拒绝：不返回错误的旧房，也不新建。',40,c=RED,b=True)
tx(48,1047,'实际数据库仍然只有R001这一间duo房。',39)
save('10-key-parameter-conflict','具体同键异参冲突与拒绝结果，避免幂等变为静默错配')

new('回执被忘掉以后，旧编号也可能再建房',1480,'教学保留期10个时间单位；不是任何产品的时间标准')
for y,t in [(225,'t = 0：K17创建R001，回执留下'),(615,'t = 11：删除旧回执，R001仍在'),(1005,'t = 11：迟到K17到达，又创建R002')]:tx(48,y,t,41,b=True)
room(65,315,'R001');chip(650,335,'K17 → R001',GREEN,345)
arrow(531,475,531,563,GRAY)
room(65,705,'R001');box(650,725,345,90,outline=RED);tx(822,744,'回执已删除',40,c=RED,anchor='mt')
arrow(531,865,531,953,GRAY)
room(65,1095,'R001');room(390,1095,'R002');chip(665,1115,'K17 → R002',BLUE,345)
tx(48,1335,'实际最终：2间房、1份新回执。保护有保留边界。',38)
save('11-retention-boundary','实际清理回执后迟到重试的反例，图区分仍存在的原资源与已遗忘的意图')

new('旧创建结果，不保证房间此刻还开着',1120,'另一个独立实验：建好以后，主动把房间关闭')
box(48,230,966,239);tx(78,256,'当前资源',44,b=True);tx(90,351,'R001：active = false（已关闭）',38)
box(48,557,966,239,outline=GREEN);tx(78,583,'重试K17时，仍读取原创建回执',42,b=True);tx(90,678,'room_id = R001; mode = duo',38,mono=True)
tx(48,891,'回执回答“当时创建了什么”。',42,b=True)
tx(48,981,'房间现在能否加入，须另外查询当前状态。',39)
save('12-resource-lifecycle','实际关闭房间后重放原结果，区分操作历史与当前资源生命周期','Faithful chart of actual closed-resource and replayed-receipt experiment')

new('一个数据库的事务，包不住所有外部动作',1280,'本篇只保护框内的两种数据库修改')
box(48,225,966,485,outline=GREEN);tx(78,255,'同一SQLite数据库的事务范围',44,c=GREEN,b=True);chip(110,390,'房间',BLUE,330);chip(620,390,'回执',GREEN,330);ln([(465,435),(595,435)],GREEN,8);tx(531,586,'一起提交，或都不提交',44,b=True,anchor='mt')
arrow(531,733,531,856,GOLD)
box(185,888,692,150,outline=GOLD);tx(531,924,'邮件、另一个服务、真实设备',41,b=True,anchor='mt');tx(531,987,'没有自动加入这笔数据库事务',37,anchor='mt')
tx(48,1120,'把外部调用写在BEGIN/COMMIT之间也不够。',38)
save('13-external-effect-boundary','把本地原子边界与外部副作用隔开，不承诺全系统exactly-once')

new('下一次没回音时，先别丢掉这次意图',1260,'请求可以重发；用户真正要的是同一次创建结果')
for y,t,col in [(225,'发出前：保存玩家、K17和原参数',BLUE),(470,'未确认：保留K17，按接口规则重试/查询',GOLD),(715,'确认结果：得到R001，再查当前房间状态',GREEN),(960,'真想另开一间：明确开始新意图K18',BLUE)]:
 box(48,y,966,149,outline=col);tx(531,y+45,t,38,c=col,b=True,anchor='mt')
 if y<960:arrow(531,y+165,531,y+218,col)
save('14-client-intent-lifecycle','把用户动作与意图生命周期收拢，超时不自动换编号')
new('点了“创建房间”却没回音，',780,'再点一次安全吗？')
chip(75,282,'K17',BLUE,250);chip(75,457,'K17',BLUE,250);arrow(350,326,630,414);arrow(350,501,630,414);room(718,350,'R001',GREEN)
tx(48,666,'同一次意图，找回同一个结果。',46,b=True)
im.save(ROOT/'cover.png')
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
assert not bounds, bounds
print('body figures',len(meta),'text outside safe page',len(bounds))
