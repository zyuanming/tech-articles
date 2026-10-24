"""Run: python lab.py. Original calculations and image synthesis; no downloaded art."""
from pathlib import Path
import json, platform
import numpy as np
from PIL import Image, ImageFilter
from figurelib import *
P=Path(__file__).resolve().parents[1];A=P/'assets';A.mkdir(exist_ok=True)
def over(f,a,b):return f*a+b*(1-a)
def pm_over(ca,a,cb,b):return ca+cb*(1-a),a+b*(1-a)
R=np.array([1.,0,0]);B=np.array([0.,0,1]);white=np.ones(3)
bad=over((R+B)/2,.5,white);good=over(R,.5,white)
c,a=pm_over(R*.5,.5,B*.5,.5)
vals={'input_red':[1,0,0,1],'input_transparent_blue':[0,0,1,0],'bad_half_white':bad.tolist(),'correct_half_white':good.tolist(),'two_layers_premult':c.tolist(),'two_layers_alpha':a,'two_layers_straight':(c/a).tolist(),'linear_half_srgb':float(srgb(.5)),'low_alpha':1/255,'low_original_red':.4,'low_quantized_pm_red':round(.4)/255,'versions':{'python':platform.python_version(),'numpy':np.__version__}}
# Independent source-over associativity check and explicit order counterexample.
rng=np.random.default_rng(24)
for _ in range(1000):
 col=rng.random((3,3));al=rng.random(3);pm=col*al[:,None]
 ab,aa=pm_over(pm[0],al[0],pm[1],al[1]);left,la=pm_over(ab,aa,pm[2],al[2])
 bc,ba=pm_over(pm[1],al[1],pm[2],al[2]);right,ra=pm_over(pm[0],al[0],bc,ba)
 assert np.allclose(left,right) and np.isclose(la,ra)
assert np.allclose(bad,[.75,.5,.75]) and np.allclose(good,[1,.5,.5])
(P/'examples/results.json').write_text(json.dumps(vals,ensure_ascii=False,indent=2)+'\n');v=json.loads((P/'examples/results.json').read_text());M=[]
def save(f,n,p,id='原创教学示意'):M.append(f.save(A/n,p,id))
def edge_array(pm):
 t=np.linspace(0,1,480);alpha=1-t
 col=np.zeros((480,3));col[:,0]=1
 if not pm:col[:,0]=1-t;col[:,2]=t
 return col*alpha[:,None]+white*(1-alpha[:,None])
def shape(pm,blur=False):
 y,x=np.indices((72,72));alpha=(((x-36)**2+(y-36)**2)<22**2).astype(float)
 color=np.zeros((72,72,3));color[...,0]=alpha;color[...,2]=1-alpha
 layers=np.dstack([color*alpha[...,None] if pm else color,alpha])
 out=[]
 for k in range(4):
  im=Image.fromarray(layers[...,k].astype('float32'),mode='F').resize((360,360),Image.Resampling.BILINEAR)
  if blur:
   im=Image.fromarray(np.uint8(np.asarray(im)*255)).filter(ImageFilter.GaussianBlur(12));out.append(np.asarray(im)/255)
  else:out.append(np.asarray(im))
 a=out[3][...,None];c=np.stack(out[:3],axis=2);return c+(1-a) if pm else c*a+(1-a)
f=Fig('透明边缘：颜色该先乘谁？');f.image(rgbim(shape(False)),(90,110));f.image(rgbim(shape(True)),(510,110));f.text(100,500,'普通分量插值');f.text(520,500,'预乘后插值');f.image(rgbim(shape(False)).crop((270,155,310,195)).resize((240,240),Image.Resampling.NEAREST),(150,580));f.image(rgbim(shape(True)).crop((270,155,310,195)).resize((240,240),Image.Resampling.NEAREST),(570,580));f.text(180,850,'边缘放大');f.text(600,850,'同处放大');save(f,'01-edge.png','真实运行输出展示透明蓝污染红色边缘','原创程序运行结果')
f=Fig('同一个透明点，四个数');f.rect((70,130,390,380),fill='#ff0000');f.text(110,410,'红：α = 1');f.rect((560,130,880,380),fill='#0000ff');f.text(585,410,'蓝：α = 0');f.text(55,490,'RGB 存了蓝，不等于蓝会贡献');save(f,'02-rgba.png','区分RGB储存值与alpha贡献')
f=Fig('一半覆盖 ≠ 同一块半透明玻璃');grid(f,70,140,4,4,80)
for j in range(4):
 for i in range(2):f.rect((70+i*80,140+j*80,150+i*80,220+j*80),fill='#cf3d34',outline=BG)
f.rect((560,140,880,460),fill='#e9aaa4');f.text(70,500,'左半完全遮挡');f.text(550,500,'整块部分透过');save(f,'03-coverage.png','提醒alpha压缩后丢失子像素空间布局')
f=Fig('红色在上，蓝色在下');f.rect((80,150,880,310),fill='#0000ff');f.rect((80,150,480,310),fill='#ff0000');f.text(90,350,'红贡献 0.5');f.text(540,350,'蓝剩下 0.5');f.rect((280,440,680,620),fill=tuple(np.uint8(srgb([.5,0,.5])*255)));f.text(280,660,'RGB = (0.5, 0, 0.5)');save(f,'04-over.png','用贡献面积解释source-over加权')
f=Fig('背景也透明时，要保留结果 α');f.rect((80,145,880,300),fill='#e8e3da');f.rect((80,145,480,300),fill='#ff0000');f.rect((480,145,680,300),fill='#0000ff');f.text(80,340,'红 0.5');f.text(410,340,'蓝 0.25');f.text(700,340,'空 0.25');f.text(70,435,f"α = {v['two_layers_alpha']}");f.text(70,515,'预乘 RGB = (0.5, 0, 0.25)');save(f,'05-two-alpha.png','显示两透明层合成后未覆盖部分')
for pm,n,title in [(False,'06-wrong-filter.png','先平均普通 RGB：蓝色漏出来'),(True,'07-right-filter.png','先乘 α 再平均：透明蓝贡献为零')]:
 f=Fig(title);arr=np.tile(edge_array(pm)[None,:,:],(180,1,1));f.image(rgbim(arr).resize((840,220)),(60,140));f.text(65,405,'不透明红');f.text(660,405,'完全透明');f.text(100,495,('中点：(0.75, 0.5, 0.75)' if not pm else '中点：(1, 0.5, 0.5)'));save(f,n,'连续插值真实结果及中点读数','原创程序运行结果')
f=Fig('模糊会扩大错误颜色的影响范围');f.image(rgbim(shape(False,True)),(90,130));f.image(rgbim(shape(True,True)),(510,130));f.text(100,520,'先混 RGB');f.text(520,520,'先混贡献');save(f,'08-blur.png','同一圆形同一滤波器下对照结果','原创程序运行结果')
def circles(order):
 y,x=np.indices((340,400));out=checker(340,400);colors=[R,B,np.array([0.,1,0])];centers=[(150,130),(240,130),(195,220)]
 for k in order:
  cx,cy=centers[k];al=(((x-cx)**2+(y-cy)**2)<90**2)*.6;out=over(colors[k],al[...,None],out)
 return out
def grouped_circles(left_group):
 y,x=np.indices((340,400));colors=[R,B,np.array([0.,1,0])];centers=[(150,130),(240,130),(195,220)];layers=[]
 for color,(cx,cy) in zip(colors,centers):
  a=((((x-cx)**2+(y-cy)**2)<90**2)*.6)[...,None];layers.append((color*a,a))
 if left_group:
  ab,aa=pm_over(*layers[0],*layers[1]);c,a=pm_over(ab,aa,*layers[2])
 else:
  bc,ba=pm_over(*layers[1],*layers[2]);c,a=pm_over(*layers[0],bc,ba)
 return c+checker(340,400)*(1-a)
left_image=grouped_circles(True);right_image=grouped_circles(False);assert np.allclose(left_image,right_image)
f=Fig('次序不变，括号可以换');f.image(rgbim(left_image),(50,120));f.image(rgbim(right_image),(510,120));f.text(70,495,'(红 over 蓝)');f.text(75,550,'再 over 绿');f.text(520,495,'红 over');f.text(520,550,'(蓝 over 绿)');save(f,'09-associate.png','两种分组合成保留同一遮挡次序','原创程序运行结果')
f=Fig('换了前后，颜色就变了');f.image(rgbim(circles([2,1,0])),(50,120));f.image(rgbim(circles([2,0,1])),(510,120));f.text(90,500,'红在蓝前');f.text(550,500,'蓝在红前');save(f,'10-order.png','展示source-over非交换','原创程序运行结果')
f=Fig('光量平均，不等于显示编码平均');f.rect((80,150,440,390),fill=(128,128,128));k=round(v['linear_half_srgb']*255);f.rect((520,150,880,390),fill=(k,k,k));f.text(80,430,'编码 0.500');f.text(520,430,f'编码 {v["linear_half_srgb"]:.3f}');f.text(80,520,'左：直接平均编码');f.text(80,585,'右：平均光量后再编码');save(f,'11-linear.png','实际灰度对照区分编码空间与线性光','原创程序运行结果')
f=Fig('低 α 遇到整数存储：信息会丢');f.text(65,140,'原红色：0.4');f.text(65,220,'α = 1 / 255');f.text(65,300,'预乘后：0.4 / 255');f.arrow((200,390),(200,480));f.text(65,525,'8 位取整：0 / 255');f.text(65,605,'再除 α，也找不回 0.4');save(f,'12-precision.png','极低alpha下量化反例，明确8位条件')
f=Fig('已经乘过，再乘一次会变暗');t=np.linspace(0,1,800)
for j,power in enumerate([1,2]):
 arr=np.tile((R*t[:,None]**power)[None,:,:],(140,1,1));f.image(rgbim(arr),(80,140+j*250));f.text(80,300+j*250,'贡献 = α' if power==1 else '贡献 = α × α')
save(f,'13-double.png','黑底红渐变演示双重乘alpha','原创程序运行结果')
f=Fig('合成是渐变，裁剪是另一个决定');a=np.linspace(0,1,800);bg=np.ones((800,3))*.2
for j,clip in enumerate([False,True]):
 aa=(a>=.5).astype(float) if clip else a;arr=np.tile(over(R,aa[:,None],bg)[None,:,:],(140,1,1));f.image(rgbim(arr),(80,140+j*250));f.text(80,300+j*250,'按 α 连续合成' if not clip else 'α ≥ 0.5 才保留')
save(f,'14-cutout.png','区分透明合成与alpha测试','原创程序运行结果')
finish(M,P);print(json.dumps({'figures':len(M),'calculations':v,'associativity_trials':1000},ensure_ascii=False))
