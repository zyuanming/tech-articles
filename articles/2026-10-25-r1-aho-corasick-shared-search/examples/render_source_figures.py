"""Code CC0. Third-party ASCII diagrams and rendered images retain MIT.
Source: Andrew Gallant, aho-corasick 1.1.5 DESIGN.md Basics.
See ../originals/LICENSE-MIT.txt. Text transcribed from accessible GitHub view.
"""
from visual_figurekit import *
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
assert Path(MONO).exists()
mono=ImageFont.truetype(MONO,40)
mono_cmap=TTFont(MONO).getBestCmap()
for n,source,title,lines in [
 (15,'design-trie.txt','原文 ASCII 树：换用 abcd / cef', ['S0 是根；字母标在边上。','S4* 对应 abcd；S7* 对应 cef。']),
 (16,'design-failure.txt','原文 ASCII 图：补上 S3 到 S5', ['S3 对应 abc，S5 对应 c。','中间折线连接 S3 与 S5，方向是','从 S3 退到 S5；不重新读 c。'])]:
    c=Canvas(title)
    c.text(50,125,'现代实现方文档重排渲染，非原站截图',40)
    text=(ROOT/'originals'/source).read_text()
    for j,line in enumerate(text.splitlines()):
        x=60;y=245+j*75
        assert all(ord(ch) in mono_cmap for ch in line)
        box=c.d.textbbox((x,y),line,font=mono)
        assert box[2]<1062
        for b,*_ in c.boxes:assert min(box[3],b[3])<=max(box[1],b[1]) or min(box[2],b[2])<=max(box[0],b[0])
        c.d.text((x,y),line,font=mono,fill=INK)
        px=c.im.crop(box).convert('L');lo,hi=px.getextrema();assert hi-lo>90
        assert sum(v<180 for v in px.getdata())>len(line.strip())*8
        c.boxes.append((box,line,40));c.bottom=max(c.bottom,box[3])
    y=c.bottom+80
    for line in lines:c.text(50,y,line,42);y+=80
    c.text(50,y+20,'Andrew Gallant · aho-corasick 1.1.5',40)
    c.text(50,y+100,'MIT；完整许可见原图对照附页',40)
    c.save(f'{n}-source-'+('trie' if n==15 else 'failure')+'.png','保存原文ASCII结构、状态编号与终止标记，并加中文读图说明')
p=ROOT/'examples/figure-metadata.json';data=json.loads(p.read_text());data=[x for x in data if x['file'] not in [m['file'] for m in meta]]
for m in meta:m['identity']='第三方MIT ASCII图文本重排渲染；非原站截图；Andrew Gallant，1.1.5'
p.write_text(json.dumps(data+meta,ensure_ascii=False,indent=2)+'\n')
print('Two MIT source diagrams rendered; geometry and pixels PASS')
