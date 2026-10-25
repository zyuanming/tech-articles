"""Original diagrams CC BY 4.0. Code CC0-1.0. Data from experiment.py."""
from pathlib import Path
import json
import math
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'examples/results.json').read_text())
FONT = next((p for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                         '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc'] if Path(p).exists()), None)
if FONT is None:
    raise RuntimeError('Install a Chinese Noto CJK font.')
CMAP = TTFont(FONT, fontNumber=0).getBestCmap()
BG, INK, BLUE, GREEN, ORANGE = '#f7f9fc', '#152f43', '#1b5b8b', '#166552', '#98460d'
META = []


class Figure:
    def __init__(self, title):
        self.im = Image.new('RGB', (1062, 5000), BG)
        self.draw = ImageDraw.Draw(self.im)
        self.boxes = []
        self.bottom = 0
        self.text(48, 28, title, 48)

    def text(self, x, y, s, size=42, color=INK, bounds=None):
        assert size >= 40
        assert all(ord(c) in CMAP for c in s if not c.isspace()), s
        f = ImageFont.truetype(FONT, size)
        box = self.draw.textbbox((x, y), s, font=f)
        assert 0 <= box[0] < box[2] <= 1062 and 0 <= box[1] < box[3] <= 5000, (s, box)
        if bounds:
            assert bounds[0]+8 <= box[0] and box[2] <= bounds[2]-8 and bounds[1]+8 <= box[1] and box[3] <= bounds[3]-8, (s, box, bounds)
        for other, label, _ in self.boxes:
            assert min(box[2], other[2]) <= max(box[0], other[0]) or min(box[3], other[3]) <= max(box[1], other[1]), (s, label)
        self.draw.text((x, y), s, font=f, fill=color)
        pixels = self.im.crop(box).convert('L')
        low, high = pixels.getextrema()
        assert high-low >= 90 and sum(v < 180 for v in pixels.getdata()) > len(s)*8
        self.boxes.append((box, s, size))
        self.bottom = max(self.bottom, box[3])

    def rect(self, box, fill='#e2edf5'):
        self.draw.rounded_rectangle(box, radius=14, fill=fill)
        self.bottom = max(self.bottom, box[3])

    def label(self, x, y, w, text, fill='#e2edf5', color=INK):
        box = (x, y, x+w, y+88)
        self.rect(box, fill)
        f = ImageFont.truetype(FONT, 42)
        width = self.draw.textlength(text, font=f)
        self.text(x+(w-width)/2, y+12, text, color=color, bounds=box)

    def arrow(self, x1, y1, x2, y2, color=BLUE):
        self.draw.line((x1, y1, x2, y2), fill=color, width=5)
        angle = math.atan2(y2-y1, x2-x1)
        self.draw.polygon([(x2, y2)]+[(x2-18*math.cos(angle+d), y2-18*math.sin(angle+d)) for d in (-.5, .5)], fill=color)
        self.bottom = max(self.bottom, y1, y2)

    def bytes(self, x, y, payload, unit=105, color=BLUE):
        for i, c in enumerate(payload):
            self.label(x+i*unit, y, unit-8, c, '#dceaf5', color)
        if not payload:
            self.text(x, y+12, '空', color=ORANGE)

    def save(self, filename, purpose):
        im = self.im.crop((0, 0, 1062, math.ceil(self.bottom+46)))
        path = ROOT/'assets'/filename
        im.save(path)
        assert Image.open(path).size == im.size
        META.append(dict(file='assets/'+filename, width=im.width, height=im.height,
                         min_font_px=min(x[2] for x in self.boxes),
                         effective_min_font_at_354=min(x[2] for x in self.boxes)/3,
                         identity='原创结构示意／本地实验数据图；非内核监控截图', purpose=purpose,
                         checks=['glyph-cmap','canvas-bounds','declared-box','text-overlap','font-size','contrast','ink-pixels','actual-size']))


def show_event(items):
    return '+'.join(items[0]['flags']) if items else '无事件'


lt, et = D['partial']
f=Figure('epoll 提醒了，字节还在原处')
f.text(48,120,'看见“可读”之后，谁来把它读完？',46)
f.label(70,240,920,'通知：B 可以尝试读取')
f.arrow(530,340,530,405)
f.text(70,430,'接收缓冲区',44)
f.bytes(70,515,et['before'],145)
f.text(70,650,'read 才搬走字节；wait 只取事件。',44)
f.save('00-cover.png','独立封面：将通知和字节两个对象并置')

f=Figure('三个对象：端点、兴趣集合、事件')
f.label(70,125,920,'发送端 A：写入 '+et['payload'])
f.arrow(530,220,530,280)
f.text(70,300,'Linux 内核：B 的接收缓冲区')
f.bytes(70,375,et['before'],145)
f.label(70,535,440,'兴趣：B / EPOLLIN')
f.label(550,535,440,'就绪事件：B 可读')
f.arrow(510,579,548,579)
f.text(70,665,'应用先登记兴趣，再等待事件')
f.label(70,750,920,'epoll_wait → 返回 B 和事件标志')
f.text(70,885,'应用另调 read(B)，才能拿到内容')
f.save('01-objects.png','分离socket缓冲区、兴趣集合、返回事件，避免把事件当消息')

f=Figure('等待前后，字节没有减少')
for y,title,payload in [(130,'等待之前',et['before']),(425,'等待返回之后',et['after_wait'])]:
 f.text(70,y,title)
 f.bytes(70,y+80,payload,145)
f.text(70,330,'epoll_wait：返回 '+show_event(et['first_event']),color=GREEN)
f.text(70,640,'两个快照由 MSG_PEEK 观察；不消费数据')
f.save('02-wait.png','真实peek前后比较，说明wait不读取字节')

f=Figure('只读一小段：LT 与 ET 分叉')
f.text(70,120,'左：默认 LT',color=BLUE); f.text(550,120,'右：EPOLLET',color=ORANGE)
for x,r in [(70,lt),(550,et)]:
 f.label(x,205,440,'发送 '+r['payload'])
 f.arrow(x+220,300,x+220,345)
 f.label(x,365,440,show_event(r['first_event']))
 f.arrow(x+220,460,x+220,505)
 f.label(x,525,440,'read → '+r['first_read']['text'])
 f.text(x,655,'仍留 '+r['remaining'])
 f.arrow(x+220,720,x+220,770)
 f.label(x,790,440,show_event(r['second_event']), '#e6f2ec' if r['second_event'] else '#f8e9da')
f.text(70,930,'最后一行：没有新写入时，再 poll(0)')
f.text(70,1005,'空事件列表，不等于接收缓冲区为空。',color=ORANGE)
f.save('03-lt-et.png','同输入同读量的并列操作时序，定位通知差异')

f=Figure('继续读取，直到现在会阻塞')
remaining=et['remaining']; y=130
for item in et['drained']:
 f.text(70,y,'读取前：')
 f.bytes(300,y-8,remaining)
 if item['kind']=='data':
  remaining=remaining[item['bytes']:]
  result='read → '+item['text']+'，剩 '+str(len(remaining))+' 字节'
 else: result='read → EAGAIN；暂停等后续事件'
 f.text(70,y+115,result,color=GREEN if item['kind']=='data' else ORANGE)
 y+=245
f.text(70,y,'此后发送 XY → '+show_event(et['next_event']))
f.save('04-drain.png','将cdef分两次搬出并实际触及EAGAIN，格子数来自数据')

f=Figure('非阻塞 read：结果决定下一步')
f.label(280,130,500,'read(fd, 正数长度)')
f.arrow(530,225,530,280)
rows=[('n > 0','保存这些字节，继续尝试','#dceaf5'),
      ('EAGAIN / EWOULDBLOCK','现在会阻塞，结束本轮','#f8e9da'),
      ('n == 0','流已到 EOF，结束读方向','#e6f2ec'),
      ('EINTR','未读到字节，被信号打断；重试','#e2edf5'),
      ('其他错误','按错误处理，不当成“暂时空”','#f8e9da')]
for i,(name,action,fill) in enumerate(rows):
 y=305+i*180
 f.rect((70,y,990,y+145),fill)
 f.text(95,y+8,name,40)
 f.text(95,y+74,action,40)
f.save('05-read-results.png','分开数据、暂时无数据、EOF、EINTR及真实错误，拒绝混淆终止条件')

f=Figure('通知不是给某个读取者保留字节')
s=D['stale']
for y,text in [(135,'A 写入 Z；事件返回 '+show_event(s['event'])),
               (300,'先执行的读取者拿走 '+s['earlier_reader']['text']),
               (465,'稍后再读：'+s['later_reader']['kind'])]:
 f.label(70,y,920,text)
 if y<465:f.arrow(530,y+98,530,y+150)
f.text(70,630,'本实验按顺序模拟两个读取者；没有线程竞速')
f.text(70,705,'即使刚见过可读，实际 read 仍要处理 EAGAIN')
f.save('06-stale.png','真实先读后读实验解释就绪状态可以在处理前变化')

f=Figure('排空一次，不等于得到一条完整消息')
y=130
for i,row in enumerate(D['framing']):
 sent=row['sent'].replace('\n','\\n')
 messages=' / '.join(row['messages']) or '无'
 pending=row['pending'] or '空'
 f.text(70,y,'发送：'+sent,color=BLUE)
 f.text(70,y+80,'本轮读到 EAGAIN')
 f.label(70,y+170,920,'完整消息：'+messages)
 f.label(70,y+280,920,'应用暂存：'+pending,'#f8e9da')
 y+=440
f.text(70,y,'协议规则：换行结束一条；\\n 表示一个字节')
f.save('07-framing.png','三轮实际分段输入与解析输出，展示半条和两条消息')

f=Figure('对端结束写入，尾部数据仍要读')
e=D['eof']
f.text(70,130,'发送 '+e['payload']+'，然后 shutdown(SHUT_WR)')
f.text(70,215,'实际事件：'+show_event(e['event']),40)
y=335
for item in e['reads']:
 text=('读到 '+item['text']+'：'+str(item['bytes'])+' 字节') if item['kind']=='data' else '读到 0：EOF'
 f.label(70,y,920,text,'#e6f2ec' if item['kind']=='EOF' else '#dceaf5')
 if item is not e['reads'][-1]:f.arrow(530,y+100,530,y+145)
 y+=170
f.text(70,y,'EOF ≠ EAGAIN：不会再有此方向的新字节')
f.save('08-eof.png','半关闭时真实尾部EN、D及零返回的顺序')

f=Figure('可写也可能只接纳一部分')
w=D['writing']; first=w['writes'][0]; second=w['writes'][1]
f.text(70,130,'应用待发送：'+str(w['payload_bytes'])+' 字节')
f.text(70,210,'本次首次 send 接纳：'+str(first['accepted'])+' 字节')
x=70; total=920; cut=x+total*first['accepted']/w['payload_bytes']
f.rect((x,315,cut,405),'#bddfcf'); f.rect((cut+3,315,990,405),'#f4d8ba')
f.text(70,450,'绿色：已接纳；橙色：仍在应用队列')
f.text(70,535,'剩余 '+str(first['remaining'])+' 字节，接着 '+second['kind'])
f.arrow(530,625,530,685)
f.label(70,710,920,'对端读走数据 → 再收到 EPOLLOUT')
f.text(70,850,'继续发送剩余部分，累计接纳 '+str(w['received_bytes']))
f.text(70,925,'色段比例共用整段 '+str(w['payload_bytes'])+' 字节',40)
assert abs((cut-x)/total-first['accepted']/w['payload_bytes'])<1e-9
f.save('09-partial-write.png','实测部分写与应用未发送队列，用同比例段长避免虚构大小')

f=Figure('输出队列决定什么时候继续写')
f.label(70,130,920,'应用有待发数据：尝试非阻塞 send')
f.arrow(290,230,290,295);f.arrow(770,230,770,295)
f.label(70,320,440,'若写入 n > 0','#e6f2ec')
f.label(550,320,440,'若 EAGAIN','#f8e9da')
f.text(70,460,'移除队首 n 字节',40)
f.text(550,460,'保留全部待发余量',40)
f.text(70,545,'队列非空：继续尝试',40)
f.text(550,545,'关注 EPOLLOUT',40)
f.text(70,630,'队列空：取消 OUT',40)
f.text(550,630,'通知到来后再重试',40)
f.text(70,770,'EINTR 重试；其他错误另行处理',40)
f.text(70,855,'新数据入队时主动安排发送',40)
f.text(70,940,'本文采用按需关注策略；ET 另有正确策略',40)
f.save('10-output-policy.png','发送结果分支：部分写推进、EAGAIN保留、空队列撤销及异常边界')

f=Figure('有预算可以让路，但不能忘记')
q=D['fairness']; f.text(70,130,'两个读端 A/B；每轮最多 '+str(q['budget_bytes'])+' 字节')
f.text(70,215,'先按名称入队；这不是内核顺序保证',40)
f.text(70,330,'本轮队列',40);f.text(425,330,'读取结果',40);f.text(760,330,'轮后队列',40)
for i,row in enumerate(q['trace']):
 y=420+i*120
 f.rect((55,y-5,1007,y+90),'#e8eff5' if i%2==0 else '#f0f4f8')
 f.text(70,y,' → '.join(row['before']),40)
 out=row['read'].get('text') or row['read']['kind']
 f.text(425,y,row['endpoint']+': '+out,40)
 f.text(760,y,' → '.join(row['after']) or '空',40)
f.text(70,420+len(q['trace'])*120+40,'本例遇 EAGAIN 移出；预算用完放回队尾',40)
f.text(70,420+len(q['trace'])*120+120,'EOF 或错误则转入相应处理',40)
f.save('11-fairness.png','真实轮转读取序列，显现B及时获得服务与A继续排空')

f=Figure('ONESHOT 是另一扇需要重开的门')
o=D['oneshot']
f.text(70,130,'本实验：LT + EPOLLONESHOT；没有 EPOLLET',40)
steps=[('发送 ab，第一次等待',show_event(o['first'])),
       ('读到 EAGAIN，再发送 cd',show_event(o['disabled'])),
       ('epoll.modify 重新启用后等待',show_event(o['rearmed']))]
for i,(label,out) in enumerate(steps):
 y=260+i*270
 f.text(70,y,label,40)
 f.label(70,y+80,920,out, '#f8e9da' if out=='无事件' else '#e6f2ec')
 if i<2:f.arrow(530,y+180,530,y+230)
f.text(70,1090,'处理完如何 rearm，由应用负责协调',40)
f.save('12-oneshot.png','不用ET仍能演示ONESHOT暂停与MOD重装，防止把二者等同')

f=Figure('未读完时，新活动也可能再通知')
n=D['new_activity']
f.text(70,130,'ET：先发送 abcdef，读走 '+n['read']['text'])
f.text(70,220,'没有新活动时：'+show_event(n['quiet']))
f.bytes(70,315,n['before'],145)
f.arrow(530,425,530,480)
f.text(70,500,'此时再发送 '+n['added']+'，并没有先排空')
f.bytes(70,590,n['after'],145)
f.label(70,765,920,'本次再轮询：'+show_event(n['active']),'#e6f2ec')
f.text(70,925,'不能把 ET 说成“非空期间只通知一次”',40)
f.save('13-new-activity.png','独立实跑未排空时新增字节的通知，约束布尔边沿误读')

(ROOT/'examples/figure-metadata.json').write_text(json.dumps(META,ensure_ascii=False,indent=2)+'\n')
print('Generated',len(META),'figures; geometry/glyph/pixel checks passed.')
