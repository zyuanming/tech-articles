from pathlib import Path
import math,json
from figurelib import *
P=Path(__file__).resolve().parent;A=P.parent/'assets';M=[]
t=[i/200 for i in range(401)];delta=[i/200 for i in range(251)];u=[-2+i/100 for i in range(401)]
def sinc(x):return 1 if abs(x)<1e-10 else math.sin(math.pi*x)/(math.pi*x)
D={'model':'two equal coherent fields, normal reflection; separate 1D two-aperture Fraunhofer model','wavelength_um':2,'time_cycles':t,'wave':[math.sin(2*math.pi*x) for x in t],'delta_um':delta,'I2':[2+2*math.cos(4*math.pi*x/2) for x in delta],'I25':[2+2*math.cos(4*math.pi*x/2.5) for x in delta],'u':u,'psf0':[4*sinc(x)**2*math.cos(math.pi*1.5*x)**2 for x in u],'psfpi':[4*sinc(x)**2*math.sin(math.pi*1.5*x)**2 for x in u]}
(P/'results.json').write_text(json.dumps(D,ensure_ascii=False,indent=2));D=json.loads((P/'results.json').read_text())
def done(b,n,p):M.append(b.save(A/f'{n:02}.png',p))
b=Board('十八段围成主镜，中心留有开口');R=65
for q in range(-2,3):
 for r in range(-2,3):
  if (q,r)==(0,0) or max(abs(q),abs(r),abs(q+r))>2:continue
  x=480+1.5*R*q;y=460+math.sqrt(3)*R*(r+q/2);pts=[(x+R*math.cos(i*math.pi/3),y+R*math.sin(i*math.pi/3)) for i in range(6)];b.poly(pts,fill='#f6df92',outline=ORANGE)
b.text('布局示意，非尺寸图',235,800);done(b,1,'镜片分段与中央开口')
b=Board('方向有偏差：同一颗星出现两个像');b.line([(800,130),(800,620)],GRAY,8)
for y,outy,col in [(300,200,BLUE),(550,350,TEAL)]:
 incidence=math.atan2(170,250);out=math.atan2(outy-y,500);tangent=(incidence+out)/2
 dx=65*math.cos(tangent);dy=65*math.sin(tangent);b.line([(300-dx,y-dy),(300+dx,y+dy)],col,9)
 b.arrow((50,y-170),(300,y),ORANGE);b.arrow((300,y),(800,outy),col);b.circle(800,outy,12,fill=col)
b.text('镜片',200,680);b.text('探测面',680,680);done(b,2,'相同入射方向与不同镜面反射方向')
b=Board('先加电场，再算强度');
for off,sgn,label in [(0,1,'同相：振幅加倍'),(500,-1,'反相：振幅抵消')]:
 plot(b,[(D['time_cycles'],D['wave'],ORANGE),(D['time_cycles'],[sgn*v for v in D['wave']],TEAL),(D['time_cycles'],[(1+sgn)*v for v in D['wave']],BLUE)],(0,2),(-2,2),rect=(130,260+off,890,490+off),xlabel='周期进度',ylabel=label)
done(b,3,'相长相消的连续波形')
b=Board('多走一个波长，多转一整圈');plot(b,[([0,.5,1],[0,180,360],BLUE)],(0,1),(0,360),xlabel='光程差 / 波长',ylabel='相位差 / 度');done(b,4,'光程到相位的线性转换')
b=Board('镜子后退，去和回都增加路程');b.line([(550,170),(550,550)],GRAY,6);b.line([(750,170),(750,550)],BLUE,10);b.arrow((150,270),(740,270),ORANGE);b.arrow((740,440),(150,440),ORANGE);b.text('原位置',450,600);b.text('新位置',700,600);b.text('增加 δ',560,195);b.text('再加 δ',560,470);done(b,5,'反射位移双程系数')
b=Board('倾斜与平移是两件事');b.line([(160,250),(160,550)],GRAY,5);b.line([(120,250),(220,550)],BLUE,10);b.line([(660,250),(660,550)],GRAY,5);b.line([(780,250),(780,550)],TEAL,10);b.arrow((670,410),(765,410),TEAL);b.text('改变方向',100,640);b.text('保持方向',610,640);done(b,6,'区分倾斜和活塞')
b=Board('四分之一拍：用勾股定理相加');b.arrow((280,600),(680,600),ORANGE);b.arrow((680,600),(680,200),TEAL);b.arrow((280,600),(680,200),BLUE);b.text('1',420,650);b.text('1',730,380);b.text('√2',340,350,color=BLUE);b.text('强度 = (√2)² = 2',220,770);done(b,7,'相位箭头与强度')
b=Board('中心亮度随镜片位移周期变化');plot(b,[(D['delta_um'],D['I2'],BLUE)],(0,1.25),(0,4),xlabel='镜片后退 / 微米',ylabel='归一化强度',ticks=[(0,'0'),(.5,'0.5'),(1,'1')]);done(b,8,'光程相位和中心强度')
b=Board('中心变暗，能量分到其他方向');plot(b,[(D['u'],D['psf0'],BLUE),(D['u'],D['psfpi'],ORANGE)],(-2,2),(0,4),xlabel='方向坐标 u',ylabel='归一化强度');b.text('蓝：同相   橙：半拍错位',95,740);done(b,9,'两孔径远场分布非Webb真实PSF')
b=Board('增加一种颜色，减少单色歧义');plot(b,[(D['delta_um'],D['I2'],BLUE),(D['delta_um'],D['I25'],TEAL)],(0,1.25),(0,4),xlabel='镜片后退 / 微米',ylabel='归一化强度',ticks=[(0,'0'),(.5,'0.5'),(1,'1')]);b.text('蓝：2 微米   绿：2.5 微米',90,740);done(b,10,'两波长约束')
b=Board('让隐藏误差显露在不同观测中');b.text('同一个未知镜面状态',220,150);b.arrow((480,220),(250,340));b.arrow((480,220),(710,340));b.rect((80,350,420,480));b.rect((540,350,880,480));b.text('已知离焦甲',100,390);b.text('已知离焦乙',560,390);b.arrow((250,490),(250,610));b.arrow((710,490),(710,610));b.text('预测 ↔ 观测',90,640);b.text('预测 ↔ 观测',550,640);b.text('共同约束镜面误差',240,790);done(b,11,'已知多样性辅助相位恢复')
from PIL import Image
im=Image.open(P.parent/'originals/photos/webb-test.jpeg');M.append({'file':'../originals/photos/webb-test.jpeg','width':im.width,'height':im.height,'identity':'NASA/Chris Gunn CC BY2.0 实物照片','min_font_px':'NOT_MEASURED','purpose':'真实Webb分段镜与地面测试'})
(P/'figure-metadata.json').write_text(json.dumps(M,ensure_ascii=False,indent=2))
