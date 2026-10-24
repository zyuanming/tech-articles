"""CC BY 4.0. An educational two-output format; NOT compatible with WEB/CWEB.
Supports one definition per name, whole-line references, inherited indentation.
Does not implement lexical parsing, indexing, multi-definition chunks or macros.
"""
from pathlib import Path
import html,re
HEADER=re.compile(r'^<<(.+)>>=$')
REF=re.compile(r'^( *)<<(.+)>>$')
def parse(text):
    parts=[];chunks={};lines=text.splitlines();i=0
    while i<len(lines):
        match=HEADER.fullmatch(lines[i])
        if not match:
            parts.append(('text',lines[i]));i+=1;continue
        name=match.group(1);i+=1;body=[]
        while i<len(lines) and lines[i]!='@':body.append(lines[i]);i+=1
        if i==len(lines):raise ValueError('未结束片段: '+name)
        if name in chunks:raise ValueError('重复定义: '+name)
        chunks[name]=body;parts.append(('chunk',(name,body)));i+=1
    return parts,chunks

def tangle(chunks,root='主程序'):
    def expand(name,stack):
        if name not in chunks:raise ValueError('缺少片段: '+name)
        if name in stack:raise ValueError('循环引用: '+' → '.join(stack+[name]))
        out=[]
        for line in chunks[name]:
            m=REF.fullmatch(line)
            if m:out.extend(m.group(1)+s for s in expand(m.group(2),stack+[name]))
            else:out.append(line)
        return out
    return '\n'.join(expand(root,[]))+'\n'

def weave(parts):
    out=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>只把正数加起来</title>',
         '<style>body{max-width:760px;margin:32px auto;padding:0 24px;font-family:"Noto Sans CJK SC",sans-serif;font-size:32px;line-height:1.6;color:#163047;background:#fff}h1{font-size:42px}h2{font-size:36px}pre{font-size:32px;line-height:1.5;background:#e9f2fa;padding:20px;white-space:pre-wrap}code{font-family:monospace}.name{color:#1763a6;font-weight:bold}</style>']
    for kind,value in parts:
        if kind=='chunk':
            name,body=value;out.append('<div class="name">片段：'+html.escape(name)+'</div><pre><code>'+html.escape('\n'.join(body))+'</code></pre>')
        elif value.startswith('# '):out.append('<h1>'+html.escape(value[2:])+'</h1>')
        elif value.startswith('## '):out.append('<h2>'+html.escape(value[3:])+'</h2>')
        elif value:out.append('<p>'+html.escape(value)+'</p>')
    return '\n'.join(out)+'</html>\n'
if __name__=='__main__':
    base=Path(__file__).resolve().parent
    parts,chunks=parse((base/'positive.lit').read_text())
    (base/'generated.py').write_text(tangle(chunks))
    (base/'generated.html').write_text(weave(parts))
    print('wrote generated.py and generated.html from positive.lit')
