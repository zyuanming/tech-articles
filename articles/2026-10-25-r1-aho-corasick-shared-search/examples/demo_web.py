"""Local teaching interface, CC0-1.0. Run: python demo_web.py"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from itertools import product
import json, platform
from ac import Matcher, naive

PAGE='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AC 教学运行界面</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f8fafc;color:#142d42;font:42px/1.5 "Noto Sans CJK SC",sans-serif}main{padding:42px;width:1062px;max-width:100%}h1{font-size:50px;margin:0 0 20px}p{margin:18px 0}button{font:inherit;color:white;background:#176297;border:0;border-radius:14px;padding:15px 28px;margin:20px 0}section{border-top:3px solid #bbcbd6;padding:14px 0}#status{color:#166c57}td{padding:4px 60px 4px 0}code{font:inherit}</style>
<main><h1>Aho–Corasick 教学运行界面</h1><p>Python 标准库 · 本地实时计算</p><p>词表：he / she / his / hers</p><p>第一块：ush　第二块：ershis</p><button id="run">运行匹配与核验</button><div id="result"><p>尚未运行</p></div></main>
<script>document.querySelector('#run').onclick=async()=>{const b=document.querySelector('#run');b.disabled=true;const r=await fetch('/run',{method:'POST'});const d=await r.json();document.querySelector('#result').innerHTML=`<section><p>Python ${d.python}</p><p>第一块：${d.first.length} 个命中 · 状态 ${d.middle}</p><p>第二块：${d.second.length} 个命中</p><table><tr><td>词</td><td>区间 [起点, 终点)</td></tr>${d.second.map(h=>`<tr><td>${h[0]}</td><td>[${h[1]}, ${h[2]})</td></tr>`).join('')}</table></section><section id="status"><p>通过：朴素基准与四个输出一致</p><p>通过：全部 ${d.splits} 种双块切法</p><p>通过：${d.cases} 组二进制小输入</p></section>`;b.disabled=false;document.querySelector('#result').dataset.done='true';}</script></html>'''

def run():
    patterns=['he','she','his','hers'];text='ushershis'
    m=Matcher(patterns); first=m.feed('ush')[0];middle=m.label[m.state]
    second=m.feed('ershis')[0];assert sorted(first+second)==naive(patterns,text)
    for k in range(len(text)+1):
        s=Matcher(patterns);assert s.feed(text[:k])[0]+s.feed(text[k:])[0]==first+second
    pool=['a','b','aa','ab','ba','bb'];cases=0
    for bits in range(1,1<<len(pool)):
        ps=[p for j,p in enumerate(pool) if bits>>j&1]
        for n in range(7):
            for chars in product('ab',repeat=n):
                t=''.join(chars);assert sorted(Matcher(ps).feed(t)[0])==naive(ps,t);cases+=1
    return dict(python=platform.python_version(),first=first,middle=middle,second=second,splits=len(text)+1,cases=cases)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        if self.path!='/':self.send_error(404);return
        body=PAGE.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_POST(self):
        if self.path!='/run':self.send_error(404);return
        body=json.dumps(run(),ensure_ascii=False).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)

if __name__=='__main__':
    print('Open http://127.0.0.1:8765 and click the run button.')
    HTTPServer(('127.0.0.1',8765),Handler).serve_forever()
