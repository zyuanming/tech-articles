"""New Chebyshev teaching compositions. Code CC0, images CC BY 4.0."""
import json,math
from figure_canvas import Canvas,DATA as D,ROOT,meta,BLUE,GREEN,ORANGE,INK,BG
from PIL import Image
PURPLE='#72389a';RED='#a33243';GRAY='#526473'
X=D['grid'];C=D['curves'];M=D['main']
def fmt(v):return f'{v:g}'
def plot(c,xs,ys,color=BLUE,ylim=(-.3,.3),top=200,bottom=650,xlim=(-1,1),ticks=True):
 left,right=200,962
 px=lambda x:left+(x-xlim[0])/(xlim[1]-xlim[0])*(right-left)
 py=lambda y:bottom-(y-ylim[0])/(ylim[1]-ylim[0])*(bottom-top)
 if ticks:
  c.line((left,top),(left,bottom),GRAY);c.line((left,bottom),(right,bottom),GRAY)
  if ylim[0]<=0<=ylim[1]:c.line((left,py(0)),(right,py(0)),GRAY,True)
  for y in [ylim[0],ylim[1]]:c.text(45,py(y)-26,fmt(y),40,GRAY)
  for x in [xlim[0],(xlim[0]+xlim[1])/2,xlim[1]]:c.text(px(x)-22,bottom+16,fmt(x),40,GRAY)
  c.text(1018,bottom+16,'x',40)
 pts=[(px(x),py(y)) for x,y in zip(xs,ys)]
 assert all(top-1e-8<=p[1]<=bottom+1e-8 for p in pts)
 c.d.line(pts,fill=color,width=6);c.bottom=max(c.bottom,bottom+60)
 c.geometry.append({'x_values':xs if len(xs)<10 else 'results.json curve grid','y_values':ys if len(ys)<10 else 'results.json curve','xlim':xlim,'ylim':ylim,'mapping':[left,right,top,bottom]})
 return px,py
def dots(c,px,py,xs,ys,color=ORANGE):
 for x,y in zip(xs,ys):
  u,v=px(x),py(y);c.d.ellipse((u-10,v-10,u+10,v+10),fill=color)
def save(c,n,p):c.save(n,p)
# Each title and layout newly composed.
c=Canvas('Chebyshev：让最坏误差降下来');c.text(50,115,'五个交错峰，锁住一个最优解',42,GREEN)
px,py=plot(c,X,C['e'],BLUE,(-.15,.15),220,600)
for h in [-M['E'],M['E']]:c.line((200,py(h)),(962,py(h)),ORANGE,True)
dots(c,px,py,M['nodes'],M['peaks']);c.text(90,725,'x⁴ ≈ x² − 1/8',60);c.text(90,820,'在 [−1, 1]，绝对误差不超过 1/8',42)
save(c,'cover.png','独立封面：有界误差带与交错峰')
c=Canvas('同一个 x，比较两条曲线');c.text(50,110,'蓝：目标 x⁴　绿：候选 x²',42)
px,py=plot(c,X,C['f'],BLUE,(-.05,1.05));plot(c,X,C['p0'],GREEN,(-.05,1.05),ticks=False)
z=M['sample']['x']; c.line((px(z),py(z**4)),(px(z),py(z*z)),ORANGE)
c.text(50,765,'竖直差 e = 目标 − 候选',44);c.text(50,835,f"x = {z:g}：e = {M['sample']['f']:g} − {M['sample']['p0']:g}",40);c.text(50,900,f"这里的差是 {M['sample']['error0']:g}",42,ORANGE)
save(c,'01-task.png','在同一横坐标解释函数值与有符号竖直误差')
c=Canvas('先看未经平移的误差');c.text(50,110,'候选 p₀ = x²；蓝线 e₀ = x⁴ − x²',40)
px,py=plot(c,X,C['e0'],BLUE,(-.3,.05));dots(c,px,py,M['nodes'],[v-M['E'] for v in M['peaks']])
c.text(50,765,f"最高 {max(C['e0']):g}；最低 { -M['old_E']:g}",44);c.text(50,840,'把误差整体上移，能缩窄最坏一侧',40)
save(c,'02-unbalanced.png','单侧误差的真实形状和待均衡的上下界')
c=Canvas('平移后，两边同时碰到界');c.text(50,110,'p = x² − 0.125；e = x⁴ − p',40)
px,py=plot(c,X,C['e'],BLUE,(-.15,.15))
for h in [-M['E'],M['E']]:c.line((200,py(h)),(962,py(h)),ORANGE,True)
dots(c,px,py,M['nodes'],M['peaks'])
c.text(50,765,f"最高 +{M['E']:g}；最低 { -M['E']:g}",44);c.text(50,840,'峰值从左到右：＋ − ＋ − ＋',42)
save(c,'03-balanced.png','实际误差曲线的五个等幅交错峰')
c=Canvas('平均误差小，不等于最坏误差小');c.text(50,110,'蓝：最坏优先　紫：平方平均优先',40)
plot(c,X,C['e'],BLUE,(-.16,.25));plot(c,X,C['ls_error'],PURPLE,(-.16,.25),ticks=False)
c.text(50,765,f"蓝线最大绝对误差：{M['E']:g}",42,BLUE);c.text(50,840,f"紫线最大绝对误差：{D['least_squares']['max_error']:.6f}",42,PURPLE)
save(c,'04-objectives.png','同一目标/区间/次数预算下两种误差准则的实跑差异')
c=Canvas('等分角度，投影却不等距');cx,cy,r=531,570,350
pts=[(cx+r*math.cos(i*math.pi/200),cy-r*math.sin(i*math.pi/200)) for i in range(201)]
c.d.line(pts,fill=BLUE,width=6);c.line((cx-r,cy),(cx+r,cy),GRAY)
for i,(th,z,t) in enumerate(zip(D['cosine']['theta'],D['cosine']['x'],D['cosine']['T4'])):
 u,v=cx+r*z,cy-r*math.sin(th);c.line((cx,cy),(u,v),GRAY);c.line((u,v),(u,cy+110),ORANGE,True);c.d.ellipse((u-10,v-10,u+10,v+10),fill=BLUE)
 c.text(u-20,cy+130,str(i),40)
c.text(50,110,'单位半圆；右端 θ=0，逆时针增大',40)
arc=[(cx+120*math.cos(a),cy-120*math.sin(a)) for a in [i*D['cosine']['theta'][1]/50 for i in range(51)]]
c.d.line(arc,fill=RED,width=6);c.arrow(arc[-3],arc[-1],RED);c.text(670,490,'θ',40,RED);c.text(565,585,'半径1',40)
c.text(50,780,'投到横轴：x = cos θ',42)
c.text(50,855,'从右往左 k：0　1　2　3　4',40)
c.text(50,930,'对应 x：1，√2/2，0，−√2/2，−1',40)
c.text(50,1005,'T₄(x) = cos(4θ)：＋1，−1，＋1…',40)
c.geometry.append({'radius':r,'points_from':'results.json cosine.x/theta/T4','note':'angle and projection geometry use computed values'})
save(c,'05-projection.png','半圆角度到横坐标的实际投影，解释峰间距不等')
c=Canvas('不必求反余弦，也能算 T₄');c.text(50,115,'固定 x = 0.5，逐次使用递推',42)
for i,t in enumerate(M['T_at_half']):
 y=215+i*150;c.card(90,y,230,90,'T'+str(i));c.text(415,y+15,f'= {t:g}',48,BLUE)
 if i<4:c.arrow((205,y+95),(205,y+140),GREEN)
c.text(50,1035,'下一项 = 2x × 当前项 − 前一项',42);c.text(50,1110,'例如 T₂ = 2×0.5×0.5 − 1',42);c.text(50,1185,f"所以 T₄(0.5)/8 = {M['sample']['error']:g}",42,ORANGE)
save(c,'06-recurrence.png','同一点从T0、T1到T4的可逐项执行递推')
c=Canvas('先构造误差，再得到近似');c.text(50,115,'同一组 x；各面板共用纵轴范围',40)
for i,(key,label,col) in enumerate([('f','目标 f = x⁴',BLUE),('p','近似 p = x² − 1/8',GREEN),('e','剩余 e = T₄/8',ORANGE)]):
 top=230+i*450;c.text(50,top-75,label,42,col);plot(c,X,C[key],col,(-.2,1),top,top+290)
c.text(50,1580,'每一列都满足：f = p + e',44)
save(c,'07-decomposition.png','分离目标/候选/残差，显示T4最高次项抵消后的表示转换')
c=Canvas('若还想更好，修正必须反复变号');c.text(50,115,'d = 新候选 q − 已有候选 p',42)
left,right=160,940;px=lambda z:left+(z+1)/2*(right-left)
c.line((left,380),(right,380),GRAY)
for z,v in zip(M['nodes'],M['peaks']):
 u=px(z);dy=-110 if v>0 else 110;c.arrow((u,380),(u,380+dy),GREEN if v>0 else RED);c.text(u-22,195 if v>0 else 525,'＋' if v>0 else '−',44,GREEN if v>0 else RED)
for a,b in zip(M['nodes'][:-1],M['nodes'][1:]):
 u=px((a+b)/2);c.d.ellipse((u-13,367,u+13,393),fill=ORANGE)
c.text(50,650,'箭头：要降低误差，d 被迫取的符号',40);c.text(50,725,'圆点：四个间隔各须至少一个零点',40);c.text(50,800,'这是符号要求示意，并非某条 d 曲线',40)
c.geometry.append({'nodes':'main.nodes','signs':'main.peaks','zero_positions':'interval midpoints schematic, not actual root locations'})
save(c,'08-proof.png','正负修正需求逼出四个互异根；中点只表示根存在的间隔')
for j in [0,1]:
 t=D['exchange'][j];c=Canvas('交换迭代：'+('参考点相等还不够' if j==0 else '把参考点换成真正的峰'))
 c.text(50,110,f"参考幅度 E = {t['E']:.5f}",42)
 px,py=plot(c,X,t['curve'],BLUE,(-.18,.15))
 for h in [-t['E'],t['E']]:c.line((200,py(h)),(962,py(h)),GRAY,True)
 vals=[z**4-sum(a*z**i for i,a in enumerate(t['coefficients'])) for z in t['reference']]
 dots(c,px,py,t['reference'],vals,GREEN)
 dots(c,px,py,t['extrema'],t['values'],ORANGE)
 c.text(50,765,'绿：参考点　橙：端点与真实驻点',40);c.text(50,840,f"实际最大绝对误差 = {t['max_error']:.5f}",44,ORANGE)
 save(c,f'{9+j:02d}-exchange.png','实跑交换第'+str(j+1)+'轮：参考幅度与全驻点最大值对照')
c=Canvas('粗网格会漏掉真正的谷');c.text(50,110,'纵轴 e = x⁴ − x²；灰虚线是 0',42)
px,py=plot(c,X,C['e0'],BLUE,(-.3,.05));dots(c,px,py,D['coarse']['x'],D['coarse']['e0'],GREEN)
c.text(50,765,f"绿点最大绝对误差：{D['coarse']['sample_max']:g}",42,GREEN);c.text(50,840,f"全区间最大绝对误差：{D['coarse']['true_max']:g}",42,ORANGE)
save(c,'11-grid-trap.png','原候选的五点网格漏掉±1/√2的真正极值')
c=Canvas('离开承诺区间，误差会迅速变大');c.text(50,110,'仍用 p = x² − 1/8；横轴扩大',40)
px,py=plot(c,D['outside']['grid'],D['outside']['curve'],BLUE,(-.2,3),xlim=(-1.5,1.5))
for z in D['domain']:c.line((px(z),200),(px(z),650),ORANGE,True)
c.text(50,765,'橙线之间才是原来的 [−1, 1]',42);c.text(50,840,f"x = 1.5 时，误差 = {D['outside']['e'][-1]:g}",42,ORANGE)
save(c,'12-outside.png','同一多项式在扩大横轴后的实际误差，否定外推保证')
c=Canvas('截掉高次项，并不总是最优');c.text(50,110,'换题：g = T₂ + T₄，只允许常数',40)
px,py=plot(c,X,C['g'],BLUE,(-1.3,2.1));v=D['truncation']['constant'];c.line((200,py(v)),(962,py(v)),GREEN)
c.text(50,765,'蓝线 g；绿线是上下界的中点',40);c.text(50,840,f"截断得到 0：最坏误差 {D['truncation']['raw_error']:g}",42);c.text(50,915,f"改成 {v:g}：最坏误差 {D['truncation']['error']:g}",42,GREEN)
save(c,'13-truncation.png','新函数常数逼近的精确反例，区分Chebyshev截断与真正minimax')
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('Generated',len(meta),'new figures; geometric/font/ink checks passed')
