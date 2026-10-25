"""New CRT explanatory compositions, generated from executed JSON. Code CC0."""
from figure_canvas import *
D=DATA;M=D['main'];GRAY='#627487';RED='#a13631';PALE='#e4eef6'
def rows(c,y,lines,gap=68):
 for i,s in enumerate(lines):c.text(55,y+i*gap,s,40)
def center(c,x,y,s,size=42,color=INK):c.text(x-measure(c.d,s,size)/2,y,s,size,color)
def matrix(c,y,heads,rs,widths):
 xs=[];x=55
 for w in widths:xs.append(x+w/2);x+=w
 for xx,h in zip(xs,heads):center(c,xx,y,h,40)
 c.line((55,y+70),(1005,y+70),GRAY)
 for i,row in enumerate(rs):
  for xx,s in zip(xs,row):center(c,xx,y+100+i*95,str(s),42)
 return y+100+len(rs)*95

def numberline(c,y,lo,hi,marks,lab='整数 x'):
 tx=lambda x:110+(x-lo)/(hi-lo)*840
 c.line((110,y),(950,y),GRAY)
 for val,label,color in marks:
  xx=tx(val);c.line((xx,y-10),(xx,y+10),color);center(c,xx,y+25,label,40,color)
 c.text(55,y+105,lab,40)
 c.geometry.append({'kind':'numberline','range':[lo,hi],'marks':[v for v,_,_ in marks]})
 return tx

c=Canvas('中国剩余定理：把余数合回整数')
c.card(330,140,400,110,f'原数 {M["x"]}')
for i,(m,r) in enumerate(zip(M['moduli'],M['residues'])):
 xx=190+i*340;c.arrow((530,275),(xx,345),GRAY);c.card(xx-140,370,280,105,f'除以 {m}')
 c.card(xx-140,515,280,105,f'余 {r}')
 c.arrow((xx,650),(530,740),BLUE)
c.card(330,770,400,110,f'合回 {M["x"]}')
rows(c,950,[f'必须指定范围：0 ≤ x < {M["M"]}',f'否则 {M["x"]}、{M["x"]+M["M"]}、{M["x"]+2*M["M"]}…余数完全相同','三条小记录，保留了哪些信息？'])
c.save('00-cover.png','原数、三个余数通道与有范围的重建关系')

c=Canvas('除法余数：整组拿走，剩下多少')
for i,r in enumerate(M['division']):
 yy=155+i*310;rows(c,yy,[f'{M["x"]} ÷ {r["m"]}：{r["q"]} 整组，余 {r["r"]}'])
 # Each actual object dot is assigned to a full group or remainder; same 23 objects.
 for j in range(M['x']):
  xx=75+j*40
  col=BLUE if j<r['q']*r['m'] else ORANGE
  c.d.ellipse((xx,yy+100,xx+18,yy+118),fill=col)
 for q in range(r['q']):
  x0=68+q*r['m']*40;x1=x0+r['m']*40-5
  c.d.rounded_rectangle((x0,yy+83,x1,yy+136),radius=10,outline=BLUE,width=3)
 c.text(55,yy+175,f'{M["x"]} = {r["m"]} × {r["q"]} + {r["r"]}',42)
rows(c,1110,['蓝框是完整分组；棕点是余数','每一行都重新分同一批23个对象'])
c.geometry.append({'kind':'division-groups','source':'main.division','objects':M['x']})
c.save('01-division.png','同一整数的三次实际分组和余数含义')

c=Canvas('先筛一遍：候选数怎样越来越少')
rows(c,145,[f'范围 0…{M["M"]-1}；先满足除3余2','以下按数值从左到右、从上到下'])
for i,v in enumerate(M['filters'][0]):
 xx=65+(i%7)*140;yy=320+(i//7)*110
 accepted=v in M['filters'][1]
 c.card(xx,yy,125,85,str(v),fill='#dcebe5' if accepted else PALE,color=GREEN if accepted else INK)
rows(c,930,['绿格：继续满足除5余3的7个数'])
for i,v in enumerate(M['filters'][1]):
 xx=65+i*140;c.card(xx,1040,125,85,str(v),fill='#f3e5d8' if v==M['x'] else PALE,color=ORANGE if v==M['x'] else INK)
rows(c,1190,[f'再要求除7余2，只剩 {M["x"]}','格子顺序是候选列表，不是等距数轴'])
c.geometry.append({'kind':'candidate-filter','source':'main.filters','stage_counts':list(map(len,M['filters']))})
c.save('02-sieve.png','列全首轮35个候选及后两次真实筛选')

c=Canvas('同余：两数相差整整几个周期')
ps=M['period_points'];tx=numberline(c,270,ps[0]-10,ps[-1]+10,[(v,str(v),BLUE) for v in ps])
for a,b in zip(ps,ps[1:]):
 c.arrow((tx(a),215),(tx(b),215),GREEN);center(c,(tx(a)+tx(b))/2,145,f'+{M["M"]}',40,GREEN)
rows(c,460,[f'共同周期 {M["M"]} = 3×5×7',f'{ps[2]}−{ps[1]}={M["M"]}，被三个模数整除','余数都为 (2, 3, 2)','x ≡ a (mod m) 的意思：','x−a 是 m 的整数倍','并不是 x 在普通整数里等于 a'])
c.save('03-period.png','同余类的真实等距数轴与共同周期')

c=Canvas('先让另外两条条件看不见它')
b=M['basis'][0]
rows(c,145,[f'先取另外两个模的乘积：{b["q"]}=5×7'])
matrix(c,280,['待放入数','模3','模5','模7'],[[b['q']]+[b['q']%m for m in M['moduli']],[b['e']]+b['residues']],[350,200,200,200])
c.arrow((535,670),(535,760),GREEN)
rows(c,820,[f'{b["q"]} 已经让模5、模7都读到0',f'但模3读到 {b["q_residue"]}；乘 {b["inverse"]} 后读到1',f'得到 {b["e"]}：只给模3通道增加1','乘整数不会破坏已为0的两条条件'])
c.save('04-isolate-channel.png','隔离其他模通道，再把目标通道的余数校准成1')

c=Canvas('模逆不是倒数：乘完只要余1')
rows(c,145,['目标：2 × t ≡ 1 (mod 3)','逐一试模3中的三种余数：'])
matrix(c,310,['t','2×t','除3的余数'],[[k,2*k,r] for k,r in M['multiplication_map']],[300,325,325])
rows(c,800,['t=2 时，2×2=4，除3余1','所以2在模3下的逆元是2','它不是普通分数 1/2','互素时，乘法把各余数重新排列','若有公因子，可能永远到不了余1'])
c.save('05-inverse.png','完整小余数乘法表说明模逆与普通倒数区别')

c=Canvas('不靠遍历：把余数除法倒着代回去')
rows(c,145,['35 = 11×3 + 2',' 3 =  1×2 + 1',' 2 =  2×1 + 0'])
c.line((55,395),(1005,395),GRAY)
rows(c,440,['最后一个非零余数：gcd(35,3)=1','往回代：','1 = 3−2','  = 3−(35−11×3)','  = 12×3−35'])
c.card(55,845,950,110,'−35 ≡ 1 (mod 3)')
rows(c,1015,[f'−1 与 {M["basis"][0]["inverse"]} 模3相同，所以可取 t=2','扩展欧几里得记录这种线性组合','一般：s a + t m = 1','所以：s a ≡ 1 (mod m)'])
c.save('06-euclid-backsub.png','一次完整欧几里得除法和回代建立模逆')

c=Canvas('三个选择基：每行只打开一个通道')
matrix(c,155,['选择基','模3','模5','模7'],[[b['e']]+b['residues'] for b in M['basis']],[350,200,200,200])
for i,b in enumerate(M['basis']):
 yy=700+i*150
 c.card(55,yy,340,95,f'{b["q"]} × {b["inverse"]} = {b["e"]}')
 c.arrow((430,yy+45),(580,yy+45),GRAY)
 c.text(625,yy+20,f'目标模 {b["m"]}',42)
rows(c,1210,['一列看到1，其余两列看到0','这是余数意义下的选择，不是普通乘法的0'])
c.save('07-basis.png','完整选择基矩阵和各自乘积来源')

c=Canvas('给每条通道填上所需余数，再相加')
matrix(c,155,['加权项','模3','模5','模7'],[[f'{b["r"]}×{b["e"]}={b["weighted"]}']+b['weighted_residues'] for b in M['basis']],[350,200,200,200])
S=M['sum'];total_res=[S%m for m in M['moduli']]
c.line((55,635),(1005,635),GRAY)
matrix(c,690,['总和','模3','模5','模7'],[[S]+total_res],[350,200,200,200])
rows(c,1010,['每个目标余数只由对应的一项贡献','其他两项在该模下都是0','因此加法不会把已设好的条件搅乱'])
c.save('08-weighted.png','逐通道核实加权贡献与总和满足全部条件')

c=Canvas('总和233，为什么能减成23？')
S=M['sum'];period=M['M'];x=M['x'];segments=[period,period,x];unit=900/S;start=70
for i,v in enumerate(segments):
 end=start+v*unit;c.d.rectangle((start,230,end,330),fill=[BLUE,GREEN,ORANGE][i]);center(c,(start+end)/2,365,str(v),42);start=end
c.bottom=440
rows(c,490,[f'{S} = 2×{period} + {x}',f'每减一个 {period}，三条余数都不变',f'取除以 {period} 的余数：得到 {x}',f'它是 0 ≤ x < {period} 中的代表','图中每段长度使用同一数值比例'])
c.geometry.append({'kind':'shared-scale-sum','segments':segments,'pixels_per_unit':unit})
c.save('09-normalize.png','共轴长度把总和拆成完整周期与最小非负代表')

c=Canvas('唯一的是一个周期里的代表')
rows(c,145,['假设 x 和 y 都满足同一组余数','那么差 d=x−y：'])
for i,m in enumerate(M['moduli']):
 xx=190+i*340;c.card(xx-140,340,280,100,f'{m} 整除 d');c.arrow((xx,475),(530,595),GRAY)
c.card(250,630,560,110,f'{M["M"]} 整除 d')
rows(c,820,['这一步需要模数两两互素','否则不能直接把除数相乘',f'若 x、y 都在 0…{M["M"]-1} 中',f'则 |d|<{M["M"]}，只能是 d=0','于是 x=y；周期之外仍有无穷多解'])
c.save('10-uniqueness.png','从相同余数到差为共同周期倍数的证明结构')

c=Canvas('105种余数组合，恰好对应105个整数')
rows(c,140,['每层固定模3余数；行是模5余数','列是模7余数；格内是重建整数'])
y=320
for a in range(3):
 c.text(55,y,f'模3余数 = {a}',42);y+=80
 for col in range(7):center(c,275+col*112,y,str(col),40)
 c.text(55,y,'模7→',40);y+=75
 for b in range(5):
  c.text(105,y+15,str(b),42)
  for cc in range(7):
   value=next(row['x'] for row in M['all_rows'] if row['residues']==[a,b,cc])
   xx=220+cc*112;c.card(xx,y,105,78,str(value),fill='#f3e5d8' if value==M['x'] else PALE,color=ORANGE if value==M['x'] else INK)
  y+=90
 y+=70
rows(c,y,[f'棕格 (2,3,2) 对应 {M["x"]}','整张表由程序枚举，不是随机抽样','实际查过：每个0…104恰好出现一次'])
c.geometry.append({'kind':'exhaustive-bijection','source':'main.all_rows','items':len(M['all_rows'])})
c.save('11-bijection.png','所有105余数组合的完整可视化检验，非缩略抽样')

c=Canvas('允许负数时，必须先约定代表范围')
s=D['signed'];numberline(c,240,0,104,[(0,'0',GRAY),(52,'52',GRAY),(s['x'],str(s['x']),ORANGE),(104,'104',GRAY)],'上：非负代表 0…104')
numberline(c,590,-52,52,[(-52,'−52',GRAY),(s['value'],str(s['value']),BLUE),(0,'0',GRAY),(52,'52',GRAY)],'下：对称代表 −52…52')
rows(c,800,[f'{s["x"]}−{s["M"]}={s["value"]}',f'两者余数都为 {tuple(s["same_residues"])}','两根数轴的零点和范围不同','对称范围内选 −17，不是余数变了','没有范围信息，就不能判断哪个是原数'])
c.save('12-centered.png','非负与对称代表的不同区间及相同余数')

c=Canvas('模数不互素，也可能有解')
n=D['noncoprime'][0]
rows(c,145,[f'x 除 {n["m"]} 余 {n["a"]}；除 {n["n"]} 余 {n["b"]}','检查一个最小公倍数周期：0…23'])
for i,v in enumerate(range(24)):
 xx=65+(i%6)*158;yy=340+(i//6)*140
 match=v in n['matches'];c.card(xx,yy,140,95,str(v),fill='#f3e5d8' if match else PALE,color=ORANGE if match else INK)
 if v in n['row1']:c.d.rectangle((xx+10,yy+104,xx+60,yy+115),fill=BLUE)
 if v in n['row2']:c.d.rectangle((xx+80,yy+104,xx+130,yy+115),fill=GREEN)
rows(c,1000,['格下蓝条：满足模6；绿条：满足模8',f'唯一重合 {n["result"][0]}；每 {n["result"][1]} 个整数重复','共同因子2要求两边余数奇偶一致','6与8不互素，但2与6同为偶数'])
c.geometry.append({'kind':'noncoprime-candidate-grid','source':'noncoprime[0]'})
c.save('13-compatible.png','非互素相容系统的完整一个周期候选交集')

c=Canvas('同一条公共信息，不能一边偶一边奇')
n=D['noncoprime'][1]
rows(c,145,[f'x ≡ {n["a"]} (mod {n["m"]}) → x 必为偶数',f'x ≡ {n["b"]} (mod {n["n"]}) → x 必为奇数','下面只列 0…23 的候选'])
for i,vals in enumerate([n['row1'],n['row2']]):
 yy=350+i*250
 for j,v in enumerate(vals):c.card(80+j*220,yy,180,100,str(v),fill=PALE,color=BLUE if i==0 else GREEN)
rows(c,920,['同一个整数无法同时为偶数和奇数','gcd(6,8)=2，但 3−2=1 不被2整除','这是无解，不是搜索还不够久','一般条件：gcd(m,n) 必须整除 b−a'])
c.save('14-incompatible.png','非互素冲突是共同因子上的信息矛盾')

c=Canvas('逐条合并：保留旧条件，只试新方向')
state=[(M['residues'][0],M['moduli'][0])]+[(t['x'],t['L']) for t in M['trace']]
for i,(a,m) in enumerate(state):
 yy=155+i*380;c.card(100,yy,850,100,f'x ≡ {a} (mod {m})')
 if i<len(M['trace']):
  t=M['trace'][i];c.arrow((530,yy+125),(530,yy+215),GRAY)
  center(c,530,yy+240,f'加上模 {t["n"]} 条件；选 t={t["t"]}',40)
rows(c,1340,['每次把全部已处理条件压成一条','新候选写作 x=a+m t','所以怎样改变 t，都不会弄坏旧条件'])
c.save('15-merge-trace.png','贯穿例从2mod3到8mod15再到23mod105的实际合并')

c=Canvas('一般合并：先约掉共同因子')
n=D['noncoprime'][0]
rows(c,145,['已知 x=2+6t，要求 x≡6 (mod8)','代入：6t ≡ 4 (mod8)','gcd(6,8)=2；两边和模一起除2','得到：3t ≡ 2 (mod4)','3的模4逆元是3：t≡6≡2 (mod4)'])
c.card(55,555,950,110,f'x = 2+6×2 = {n["result"][0]}')
rows(c,730,['t 每增加4，x 增加6×4=24',f'因此新周期是 {n["result"][1]}，不是6×8=48','一般：g=gcd(m,n)，先检查 g | (b−a)','再解 (m/g)t ≡ (b−a)/g (mod n/g)','约掉g后，两边的模与系数已互素'])
c.save('16-general-merge.png','非互素合并的一次完整约化、模逆及最小周期')

c=Canvas('小模数通道内，也能先做加减乘')
f=D['calculation'];rows(c,145,[f'另一个计算：{f["A"]}×{f["B"]}−{f["C"]} = {f["value"]}','这次换成模5、7、11，周期385'])
for i,r in enumerate(f['channels']):
 yy=340+i*220;c.card(55,yy,220,100,f'模{r["m"]}')
 c.text(330,yy+8,f'{r["a"]}×{r["b"]}−{r["c"]} = {r["raw"]}',42)
 c.text(330,yy+100,f'归一化余数：{r["r"]}',42,GREEN)
rows(c,1080,[f'余数组合 {tuple(r["r"] for r in f["channels"])}',f'重建非负代表 {f["raw"]}；减{f["M"]}得{f["centered"]}','整数加减乘与取余相容','普通除法没有同样的无条件规则'])
c.save('17-modular-calculation.png','实际整数表达式在三个小模通道的计算与重建')

c=Canvas('先有大小界，重建才知道该选谁')
f=D['calculation'];rows(c,145,['已知 0≤A,B≤10；0≤C≤100','那么 −100≤A×B−C≤100','可能结果跨度200；新周期385足够大'])
numberline(c,500,-200,200,[(-100,'−100',BLUE),(0,'0',GRAY),(100,'100',BLUE)],'已知结果范围：两端都包括')
rows(c,730,[f'M={f["M"]}>2×{f["B_bound"]}，两个候选不可能都落入',f'若只用105：{f["ambiguous_pair"][0]} 和 {f["ambiguous_pair"][1]} 都在界内','且二者模3、5、7的余数完全相同','多跑几次并不能补回缺失的范围信息',f'例：75会被对称解码成 {f["alias_pair"][1]}，不能保证正确'])
c.save('18-bound.png','有符号重建的事前界与模数积不足的实际混淆')

c=Canvas('一个余数错1，整数可能跳很远')
e=D['error'];matrix(c,155,['情况','模3','模5','模7'],[['正确']+e['correct'],['模5错1']+e['wrong']],[350,200,200,200])
numberline(c,650,0,60,[(e['x'],str(e['x']),BLUE),(e['wrong_x'],str(e['wrong_x']),ORANGE)],'重建整数；横向距离按数值绘制')
rows(c,875,[f'结果从 {e["x"]} 跳到 {e["wrong_x"]}，差 {e["difference"]}',f'模5的选择基正是 {e["basis_shift"]}','两组都是合法余数组合，CRT都能满足','重新核对输入余数，也发现不了输入已错','纠错要额外冗余与错误模型，不能凭空得到'])
c.save('19-bad-residue.png','输入错误沿选择基传播，区分一致重建与错误检测')

c=Canvas('余数很小，不代表中间乘积不会溢出')
o=D['overflow'];rows(c,145,[f'希望计算 {o["a"]}×{o["b"]} mod {o["modulus"]}'])
c.card(55,295,950,100,f'精确乘积 {o["true_product"]} → 正确余数 {o["correct"]}')
c.arrow((530,435),(530,510),RED)
c.card(55,545,950,100,f'若模拟8位无符号回绕：变成 {o["wrapped8"]}')
rows(c,715,[f'再除以{o["modulus"]}，得到{o["bad"]}，已经错了','这是Python显式模拟的模256回绕','不是声称Python整数自己会这样溢出','工程实现要用足够宽整数或安全模乘','构造模数积与加权和时也要检查位宽'])
c.save('20-overflow.png','实际可复算的定宽中间值回绕与错误模结果')

(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'figures':len(meta),'checks':'PASS'}))
