"""Three-reading least squares, exact coefficients and double-precision checks. CC BY 4.0."""
from pathlib import Path
from fractions import Fraction as F
import math,json
import numpy as np
from figure import *
P=Path(__file__).resolve().parent;AOUT=P.parent/'assets';M=[]
A=np.array([[1.,0.],[1.,1.],[1.,2.]]);b=np.array([1.,2.,2.]);q1=A[:,0]/math.sqrt(3);q2=np.array([-1.,0.,1.])/math.sqrt(2);Q=np.column_stack([q1,q2]);R=np.array([[math.sqrt(3),math.sqrt(3)],[0,math.sqrt(2)]]);coef=np.linalg.solve(R,Q.T@b);fit=A@coef;res=b-fit
assert np.allclose(Q.T@Q,np.eye(2));assert np.allclose(Q@R,A);assert np.allclose(coef,[7/6,1/2]);assert np.allclose(A.T@res,0);assert abs(res@res-1/6)<1e-14
near=[dict(e=e,kappa=float(np.linalg.cond(np.array([[1.,1.],[0,e]])))) for e in [1,.1,.01,.001]]
D=dict(t=[0,1,2],b=b.tolist(),Q=Q.tolist(),R=R.tolist(),coef=coef.tolist(),fit=fit.tolist(),res=res.tolist(),sse=float(res@res),near=near,orthogonality_error=float(np.linalg.norm(Q.T@Q-np.eye(2))))
(P/'data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2));D=json.loads((P/'data.json').read_text())
def save(f,n,s):M.append(f.save(AOUT/f'{n:02}.png',s))
f=chart('三份读数，不能全在一条直线',[('读数连线',list(zip(D['t'],D['b'])),GRAY)],(0,2),(.5,2.5),[(0,'0'),(1,'1'),(2,'2')],[(1,'1'),(2,'2')],'时间 t','读数 b')
for x,y in zip(D['t'],D['b']):f.dot(150+360*x,650-(y-.5)/2*380,BLUE,12)
save(f,1,'三个输入点彼此不共线')
f=Fig('常数列与时间列分别贡献',820);f.text(70,130,'第几次       常数列       时间列',42)
for i in range(3):f.text(110,250+i*130,str(i+1),46);f.text(420,250+i*130,'1',46,BLUE);f.text(740,250+i*130,str(i),46,ORANGE)
save(f,2,'模型c+mt拆成两列输入基底')
save(chart('先在二维练一次投影',[('原箭头',[(0,0),(0,2)],ORANGE),('已知方向',[(0,0),(1.7,1.7)],BLUE),('投影残差',[(1,1),(0,2)],TEAL)],(-1,3.926315789473684),(-.3,2.3),[(0,'0'),(1,'1'),(2,'2')],[(0,'0'),(1,'1'),(2,'2')],'第一分量','第二分量'),3,'独立二维例：投影(1,1)和残余(-1,1)')
f=Fig('把第二列中重复的部分拿走',850);f.text(60,130,'原时间列    减去投影    剩余',42)
for i,(a,b,c) in enumerate([(0,1,-1),(1,1,0),(2,1,1)]):f.text(150,260+i*135,str(a),46,ORANGE);f.text(470,260+i*135,str(b),46,BLUE);f.text(780,260+i*135,str(c),46,TEAL)
save(f,4,'三分量主例的逐项正交化')
f=chart('新方向与旧方向互相垂直',[('常数列 a1',[(0,1),(2,1)],BLUE),('残余 u2',[(0,-1),(1,0),(2,1)],TEAL)],(0,2),(-1.3,1.3),[(0,'1'),(1,'2'),(2,'3')],[(-1,'−1'),(0,'0'),(1,'1')],'分量编号','分量值');save(f,5,'分量图不是三维方向夹角，点积1×(-1)+1×0+1×1=0')
f=Fig('Q 的两列都归一化到长度一',810);f.text(75,130,'分量        第一列        第二列',42)
for i,(a,b) in enumerate([('1/√3','−1/√2'),('1/√3','0'),('1/√3','1/√2')]):f.text(110,260+i*135,str(i+1),46);f.text(340,260+i*135,a,44,BLUE);f.text(670,260+i*135,b,44,TEAL)
save(f,6,'Q矩阵各分量的确切含义')
f=Fig('R 记录旧方向怎样重新拼出',680);f.text(120,135,'第一列 a1      第二列 a2',42);f.text(80,280,'q1',42,BLUE);f.text(350,280,'√3',46);f.text(680,280,'√3',46);f.text(80,440,'q2',42,TEAL);f.text(350,440,'0',46);f.text(680,440,'√2',46);save(f,7,'R的上三角结构由先后构造顺序形成')
f=chart('最小平方误差的直线',[('模型拟合',[(0,7/6),(2,13/6)],BLUE),('原读数',list(zip(D['t'],D['b'])),GRAY)],(0,2),(.5,2.5),[(0,'0'),(1,'1'),(2,'2')],[(1,'1'),(2,'2')],'时间 t','读数')
for x,y,z in zip(D['t'],D['b'],D['fit']):
 f.line([(150+360*x,650-(y-.5)/2*380),(150+360*x,650-(z-.5)/2*380)],ORANGE,8)
save(f,8,'系数7/6与1/2产生拟合线与竖直残差')
f=Fig('点积的正负贡献恰好抵消',900)
f.text(65,125,'所有贡献均以 1/6 为单位',40)
for row,(name,vals,col) in enumerate([('常数列',[-1,2,-1],BLUE),('时间列',[0,2,-2],TEAL)]):
 y=360+row*340;f.text(55,y-150,name,42,col);f.line([(210,y),(850,y)],GRAY,3)
 for i,val in enumerate(vals):
  x=260+i*220
  if val:f.rect((x,min(y,y-val*45),x+90,max(y,y-val*45)),col,col)
  f.text(x+10,y+110,str(val),42,col)
save(f,9,'点积贡献用共同尺度画成正负条，分别相加为零')

ms=[i/100 for i in range(-50,151)];save(chart('偏离答案，就会增加平方误差',[('固定 c=7/6',[(m,sum((bi-(7/6+m*t))**2 for bi,t in zip(D['b'],D['t']))) for m in ms],BLUE)],(-.5,1.5),(0,5.3),[(-.5,'−0.5'),(.5,'0.5'),(1.5,'1.5')],[(0,'0'),(2,'2'),(5,'5')],'斜率 m','平方误差和'),10,'目标函数的一条切片最低处在m=1/2')
save(chart('两列几乎同向，系数就敏感',[('条件数',[(i,math.log10(r['kappa'])) for i,r in enumerate(D['near'])],ORANGE)],(0,3),(0,3.5),[(0,'1'),(1,'0.1'),(2,'0.01'),(3,'0.001')],[(0,'0'),(1,'1'),(2,'2'),(3,'3')],'ε','log10 条件数'),11,'近共线矩阵的实际双精度条件数，横轴按列出的epsilon等距排布')
save(chart('镜面反射也能消掉一个分量',[('原向量',[(0,0),(3,4)],ORANGE),('反射后',[(0,0),(5,0)],BLUE),('镜面方向',[(0,0),(5,2.5)],GRAY)],(-1.5,7.973684210526315),(-.3,4.7),[(0,'0'),(3,'3'),(5,'5')],[(0,'0'),(2,'2'),(4,'4')],'第一分量','第二分量'),12,'独立二维Householder例(3,4)反射成(5,0)，轴显示比例相同')
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2));print('12 figures; QR reconstruction, orthogonality, least-squares residual checked; NumPy',np.__version__)
