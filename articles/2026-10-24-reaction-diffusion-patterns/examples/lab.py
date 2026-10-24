"""Original dimensionless four-neighbor Gray-Scott model; MIT."""
from pathlib import Path
import numpy as np,json,platform
from figurelib import *
P=Path(__file__).resolve().parents[1];A=P/'assets';M=[]
N=128;DU=.16;DV=.08;DT=1.;SEED=24
rng=np.random.default_rng(SEED);U0=np.ones((N,N));V0=np.zeros((N,N));U0[54:74,54:74]=.5+.02*rng.uniform(-1,1,(20,20));V0[54:74,54:74]=.25+.02*rng.uniform(-1,1,(20,20))
def lap(a,boundary='periodic'):
 if boundary=='periodic':return sum(np.roll(a,s,axis=ax) for s,ax in [(1,0),(-1,0),(1,1),(-1,1)])-4*a
 p=np.pad(a,1,mode='edge');return p[:-2,1:-1]+p[2:,1:-1]+p[1:-1,:-2]+p[1:-1,2:]-4*a
def step(u,v,F,k,dt=DT,boundary='periodic'):
 reaction=u*v*v;un=u+dt*(DU*lap(u,boundary)-reaction+F*(1-u));vn=v+dt*(DV*lap(v,boundary)+reaction-(F+k)*v);return un,vn
def run(F=.04,k=.06,steps=6000,boundary='periodic'):
 u=U0.copy();v=V0.copy();sn={0:(u.copy(),v.copy())}
 for t in range(1,steps+1):
  u,v=step(u,v,F,k,boundary=boundary)
  assert np.isfinite(u).all() and np.isfinite(v).all()
  if t in [250,1000,3000,6000]:sn[t]=(u.copy(),v.copy())
 return sn
main=run();alts=[run(.022,.051),run(.06,.062)]
# A local hand-computable step, using the same reaction terms as the solver.
u=.5;v=.25;F=.04;k=.06;react=u*v*v;feed=F*(1-u);remove=(F+k)*v;lapv=4*.2-4*v;un=u-react+feed;vn=v+DV*lapv+react-remove
assert np.isclose(un,.48875) and np.isclose(vn,.24025)
# Diffusion-only conservation and positivity counterexample.
a=np.zeros((5,5));a[2,2]=1;safe=a+DU*lap(a);unsafe=a+2*DU*lap(a);assert np.isclose(safe.sum(),a.sum()) and np.isclose(unsafe.sum(),a.sum());assert unsafe.min()<0
constu=np.ones((6,6));constv=np.zeros((6,6));cu,cv=step(constu,constv,.04,.06);assert np.array_equal(cu,constu) and np.array_equal(cv,constv)
# Show why old/new buffers must be distinct: left-to-right in-place diffusion changes the map.
b=np.array([0.,1.,0.,0.]);syn=b+.2*(np.roll(b,1)+np.roll(b,-1)-2*b);inp=b.copy()
for i in range(4):inp[i]+=.2*(inp[(i-1)%4]+inp[(i+1)%4]-2*inp[i])
data={'N':N,'DU':DU,'DV':DV,'dt':DT,'seed':SEED,'F':.04,'k':.06,'snapshot_steps':list(main.keys()),'time_stats':{str(t):{'Umin':float(u.min()),'Umax':float(u.max()),'Vmin':float(v.min()),'Vmax':float(v.max()),'Vmean':float(v.mean())} for t,(u,v) in main.items()},'hand':{'U':.5,'V':.25,'neighbor_U':.5,'neighbor_V':.2,'reaction':react,'feed':feed,'removal':remove,'lapV':lapv,'U_new':un,'V_new':vn},'diffusion_safe':safe.tolist(),'diffusion_unsafe':unsafe.tolist(),'sync':syn.tolist(),'inplace':inp.tolist(),'alternative_parameters':[[.022,.051],[.06,.062]],'versions':{'python':platform.python_version(),'numpy':np.__version__}}
(P/'examples/results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
# Store only mathematical final states, not transient research cache.
np.savez_compressed(P/'examples/final-fields.npz',U=main[6000][0],V=main[6000][1]);data=json.loads((P/'examples/results.json').read_text())
def color(a,maxv=.5):
 t=np.clip(a/maxv,0,1);return np.stack([.06+.86*t,.15+.58*t,.27-.12*t],axis=-1)
def save(f,n,p,id='原创教学示意'):M.append(f.save(A/n,p,id))
def fieldfig(title,ar,n,p,maxv=.5):
 f=Fig(title);f.image(color(ar,maxv),(180,130),(600,600));f.image(color(np.linspace(0,maxv,600)[None,:],maxv),(180,780),(600,36));f.text(170,840,'0');f.text(720,840,str(maxv));save(f,n,p,'原创数值模拟输出')
fieldfig('一块种子，怎样长出斑纹？',main[6000][1],'01-pattern.png','6000步V浓度真实输出，固定色标')
f=Fig('每个格，存两种浓度')
for x,label,val,col in [(100,'U',.5,BLUE),(550,'V',.25,RED)]:
 f.rect((x,150,x+300,500));f.rect((x+4,500-val*600,x+296,496),fill=col,outline=None);f.text(x+80,540,f'{label} = {val}')
save(f,'02-two-fields.png','单格两种浓度，用容器高度解释数值')
f=Fig('一次局部反应：U 变少，V 变多');f.text(70,150,'U + 2V → 3V');f.text(70,250,'反应速率 U × V²');f.text(70,350,f"0.5 × 0.25² = {data['hand']['reaction']}");f.arrow((220,460),(220,560),BLUE);f.arrow((690,560),(690,460),RED);f.text(70,630,'U 减去这一份');f.text(530,630,'V 加上这一份');save(f,'03-reaction.png','反应项配对变化及实际手算数值')
f=Fig('扩散：邻居与自己的差，合起来');vals=[(.5,0,0),(.5,1,0),(.5,-1,0),(.5,0,1),(.5,0,-1)]
for dx,dy,val in [(0,0,.25),(1,0,.2),(-1,0,.2),(0,1,.2),(0,-1,.2)]:
 x=350+dx*210;y=350+dy*210;f.rect((x,y,x+170,y+150),fill='#e5eceb');f.text(x+35,y+45,str(val))
f.text(50,820,'V 的邻居总和 − 4V = −0.2');save(f,'04-laplacian.png','四邻域差分与中心V浓度')
f=Fig('把同一小步的三笔账相加');h=data['hand'];rows=[('U：反应',-h['reaction']),('U：补给',h['feed']),('V：扩散',DV*h['lapV']),('V：反应',h['reaction']),('V：移出',-h['removal'])]
for j,(label,num) in enumerate(rows):
 y=135+j*100;f.text(60,y,label);x=580;f.line([(x,y),(x,y+55)],GRAY,2);end=x+num/.04*250;f.rect((min(x,end),y+10,max(x,end),y+45),fill=BLUE if num>=0 else RED,outline=None)
f.text(60,700,f"U 新 = {h['U_new']}");f.text(490,700,f"V 新 = {h['V_new']}");save(f,'05-step.png','同一尺度有符号增量条及一步结果')
f=Fig('先算完新一帧，再替换旧一帧')
for j,(name,arr) in enumerate([('旧值',[0,1,0,0]),('同步',data['sync']),('原地',data['inplace'])]):
 y=150+j*180;f.text(45,y+25,name)
 for i,val in enumerate(arr):
  x=230+i*175;f.rect((x,y,x+160,y+110),fill='#e1ebee');f.text(x+12,y+35,f'{val:.3f}',40)
save(f,'06-sync.png','一维扩散对照，原地更新改变实际规则','原创程序运行结果')
for t,num in [(0,7),(250,8),(1000,9),(3000,10)]:fieldfig(f'同一场：第 {t} 步',main[t][1],f'{num:02d}-time-{t}.png',f'时间序列第{t}步V浓度，色标不变')
f=Fig('同一初始种子，改补给与移出参数')
for j,(params,arr) in enumerate(zip(data['alternative_parameters'],alts)):
 f.image(color(arr[6000][1]),(180,130+j*760),(600,600));f.text(120,760+j*760,f'F = {params[0]}；k = {params[1]}')
save(f,'11-parameters.png','两组参数6000步实际结果，固定色标','原创数值模拟输出')
f=Fig('周期边界：左边和右边是邻居');grid(f,100,180,4,2,180);f.arrow((115,310),(800,310),RED,6);f.arrow((800,430),(115,430),BLUE,6);f.text(70,650,'跨出一侧，从对侧接回来');save(f,'12-boundary.png','边界条件示意，不是额外反应规则')
f=Fig('步子太大，扩散能算出负浓度')
for j,(name,arr) in enumerate([('Δt = 1',safe),('Δt = 2',unsafe)]):
 ox=90+j*460;f.text(ox,140,name)
 for i,k in [(2,2),(1,2),(3,2),(2,1),(2,3)]:
  x=ox+(i-1)*115;y=250+(k-1)*115;f.rect((x,y,x+110,y+110),fill='#e4ebed');f.text(x+6,y+35,f'{arr[k,i]:.2f}',40)
save(f,'13-timestep.png','纯扩散单脉冲在两步长下的实际结果','原创程序运行结果')
f=Fig('完全没有种子，V = 0 会一直是 0');f.image(color(np.zeros((128,128))),(180,150),(600,400));f.text(80,610,'U = 1：补给项为零');f.text(80,690,'V = 0：反应与移出也为零');save(f,'14-no-seed.png','均匀平衡态的真实计算与解释','原创程序运行结果')
f=Fig('同一时刻，两张图不一定互补');f.image(color(main[6000][0],1),(40,150),(420,420));f.image(color(main[6000][1],1),(500,150),(420,420));f.text(70,620,'U：色标 0 到 1');f.text(520,620,'V：色标 0 到 1');save(f,'15-two-maps.png','同一时刻U和V在同一色标的实际对照','原创数值模拟输出')
finish(M,P);print(json.dumps({'figures':len(M),'hand':data['hand'],'stats':data['time_stats'],'sync':data['sync'],'inplace':data['inplace']},ensure_ascii=False))
