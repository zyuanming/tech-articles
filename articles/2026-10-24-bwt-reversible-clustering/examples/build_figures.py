"""Original teaching figures, MIT code; generated images CC BY 4.0."""
from pathlib import Path
import json
from figurekit import Board,BLUE,ORANGE,TEAL,INK,LIGHT
P=Path(__file__).resolve().parent;D=json.loads((P/'results.json').read_text());OUT=P.parent/'assets';META=[]
COL={'A':'#e5f1fb','N':'#fcebdc','B':'#e0f2ee','$':'#eeeeee'}
def board(title):
 b=Board();b.text((40,30),title);return b

def row(b,s,y,x=210,w=90,mark=None):
 for j,c in enumerate(s):
  q=(x+j*w,y,x+(j+1)*w-8,y+72);b.rect(q,fill=COL.get(c,LIGHT),outline=TEAL if mark==j else BLUE,name=f'{x}-{y}-{j}')
  b.text(((q[0]+q[2])/2,y+36),c,anchor='mm',inside=q)

def save(b,name,purpose):META.append(b.save(OUT/name,purpose))
b=board('普通排序：顺序找不回来')
for y,s in [(140,'BANANA'),(250,'ANANAB')]:
 b.text((45,y),s);b.arrow((390,y+30),(565,y+30));b.text((620,y),'AAABNN')
b.line([(40,350),(1020,350)],fill='#aabaca');b.text((40,390),'BWT：保留可逆的次序关系')
b.text((40,500),D['input']);b.arrow((400,530),(560,530));b.text((600,500),D['last']);save(b,'01-order.png','区分普通排序碰撞与BWT可逆重排')
b=board('同一个环，换七个起点')
for i,s in enumerate(D['rotations']):b.text((55,150+i*95),str(i));row(b,s,135+i*95,mark=0)
save(b,'02-rotations.png','逐行列出完整旋转避免凭空出现矩阵')
b=board('字典顺序排列旋转行');b.text((230,120),'F');b.text((775,120),'L')
for i,s in enumerate(D['rows']):b.text((55,215+i*95),str(i));row(b,s,200+i*95)
save(b,'03-sorted.png','排序表的每一行及首尾列位置')
b=board('只保存 L，也能重建 F');b.text((210,135),'L');b.text((740,135),'F')
for i,(l,f) in enumerate(zip(D['last'],D['first'])):
 b.text((65,240+i*90),str(i));row(b,l,225+i*90,x=205);row(b,f,225+i*90,x=735)
b.arrow((380,500),(620,500));b.text((400,410),'排序');save(b,'04-two-columns.png','字符多重集合不变与首列可恢复')
b=board('同字符，第几次就认第几次');seen={};left=[];right=[]
for c in D['last']:seen[c]=seen.get(c,0)+1;left.append(c+str(seen[c]))
seen={}
for c in D['first']:seen[c]=seen.get(c,0)+1;right.append(c+str(seen[c]))
for i,(l,f) in enumerate(zip(left,right)):
 y=160+i*100;b.text((55,y),str(i));b.text((170,y),l);b.text((790,y),f);b.text((950,y),str(i))
for i,j in enumerate(D['lf']):b.arrow((295,190+i*100),(730,190+j*100),fill=TEAL if D['last'][i]=='A' else '#ad4d16')
save(b,'05-stable-match.png','出现次序构成一对一映射')
b=board('相同末字母搬到头，次序不变')
for k,i in enumerate([1,2]):
 y=150+k*300;b.text((30,y+15),str(i));b.text((30,y+165),str(D['lf'][i]));row(b,D['rows'][i],y,x=120);b.arrow((900,y+35),(900,y+140),fill=ORANGE);row(b,D['rows'][D['lf'][i]],y+150,x=120,mark=0)
save(b,'06-predecessor.png','同字符组稳定性与LF的一次旋转对应')
b=board('沿路标倒着取字');b.text((55,125),'当前行');b.text((385,125),'取字');b.text((775,125),'下一行')
for k,(i,c,j) in enumerate(D['walk']):
 y=230+k*95;b.text((140,y),str(i));b.text((430,y),c);b.arrow((560,y+25),(725,y+25));b.text((860,y),str(j))
save(b,'07-inverse-walk.png','完整七步LF逆变换轨迹')
b=board('倒着读完，再反转位置');row(b,D['backward'],170,x=100)
for i in range(len(D['input'])):b.line([(140+i*90,250),(140+(6-i)*90,430)],fill='#b3c1cc',width=3)
row(b,D['inverse'],440,x=100);b.text((100,570),'恢复 BANANA$');save(b,'08-roundtrip.png','逆读与反转的位置对应')
b=board('前插 L，再排序：列逐轮长出')
for k in range(3):
 x=50+k*340;b.text((x,130),f'第{k+1}轮')
 for j,s in enumerate(D['table_steps'][k]):b.text((x,235+j*83),s)
save(b,'09-table-rebuild.png','前三轮慢逆变换的实际字符串')
b=board('MTF：输出位置，再移到最前')
for i,t in enumerate(D['mtf'][:3]):
 y=140+i*240;b.text((50,y),f'读 {t["char"]}');row(b,t['before'],y+80,x=250,w=95,mark=t['index']);b.text((690,y),f'输出 {t["index"]}');b.arrow((250+t['index']*95+35,y+160),(285,y+195),fill=ORANGE)
save(b,'10-mtf.png','动态列表位置使连续重复转为零')
b=board('长度不变；重复也不是保证')
for i,c in enumerate(D['comparison']):
 y=160+i*240;b.text((40,y),c['input']);b.arrow((420,y+30),(560,y+30));b.text((610,y),c['output']);b.text((60,y+105),f'段数 {c["runs_before"]} → {c["runs_after"]}')
save(b,'11-noncompression.png','算例及无重复反例区分重排与压缩')
b=board('分块以后，各块各自成环')
b.text((50,130),'一整块');row(b,'BANANA',230,x=170);b.rect((150,210,730,325),fill=None,outline=TEAL)
b.text((50,430),'分两块');row(b,'BAN',530,x=170);row(b,'ANA',530,x=620);b.line([(540,480),(540,680)],fill=ORANGE);b.text((430,720),'边界')
save(b,'12-blocks.png','分块改变循环邻接范围')
b=board('穷举往返：长度 0—7，全部通过');maxv=max(n for _,n in D['tests']);lengths=[]
for i,n in D['tests']:
 y=150+i*110;b.text((45,y),str(i));v=700*n/maxv;b.rect((160,y+10,160+v,y+65),fill=BLUE);b.text((885,y),str(n));lengths.append((v,n))
assert sorted(lengths)==lengths
save(b,'13-verification.png','各长度测试数量共用尺度的真实运行结果')
(P/'figure-metadata.json').write_text(json.dumps(META,ensure_ascii=False,indent=2)+'\n');print('figures',len(META))
