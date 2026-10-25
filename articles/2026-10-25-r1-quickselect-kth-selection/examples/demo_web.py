"""Original local teaching web interface, CC0-1.0; NumPy is an optional dependency."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json, platform
import numpy as np

ROOT = Path(__file__).resolve().parent

def run():
    data = json.loads((ROOT / 'results.json').read_text())
    a = np.array(data['input'], dtype=np.int64)
    before = a.copy()
    kth = data['index']
    p = np.partition(a, kth)
    selected = int(p[kth])
    left_ok = bool(np.all(p[:kth] <= p[kth]))
    right_ok = bool(np.all(p[kth+1:] >= p[kth]))
    unchanged = bool(np.array_equal(a, before))
    assert selected == sorted(data['input'])[kth]
    assert left_ok and right_ok and unchanged
    return dict(python=platform.python_version(), numpy=np.__version__, dtype=str(a.dtype),
                input=before.tolist(), kth=kth, rank=kth+1, output=p.tolist(),
                selected=selected, input_after=a.tolist(), input_unchanged=unchanged,
                left_ok=left_ok, right_ok=right_ok,
                output_sorted=bool(np.all(p[:-1] <= p[1:])))

PAGE='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NumPy partition 教学实跑</title><link rel="icon" href="data:,">
<style>*{box-sizing:border-box}body{margin:0;background:#f8fafc;color:#142d42;font-family:"Noto Sans CJK SC",sans-serif;font-size:min(3.955vw,42px);line-height:1.5}main{width:1062px;max-width:100%;padding:min(4vw,42px)}h1{font-size:min(4.52vw,48px);margin:0 0 .4em}p{margin:.45em 0}button{font:inherit;color:white;background:#176297;border:0;border-radius:.3em;padding:.3em .6em;margin:.35em 0}section{border-top:2px solid #bbcbd6;padding:.3em 0}.array{display:grid;grid-template-columns:repeat(9,1fr);gap:.15em;margin:.4em 0 .7em}.cell{text-align:center;background:#e5eef7;border-radius:.2em;padding:.1em}.chosen{background:#ffe1ae;color:#723200;border:2px solid #9c4d0d}#status{color:#166c57}.note{border-top:2px solid #bbcbd6;margin-top:.4em;padding-top:.35em}code{font:inherit}</style>
<main><h1>NumPy partition 真实运行</h1><p>原创教学网页 · 按钮调用本地 Python</p><p id="input"></p><div id="original" class="array"></div><p id="request"></p><button id="run">运行 NumPy 并核验</button><div id="result"><p>尚未运行</p></div></main>
<script>
const setup=__SETUP__;
const cells=(a,k=-1)=>a.map((v,i)=>`<span class="cell ${i===k?'chosen':''}">${v}</span>`).join('');
document.querySelector('#input').textContent='输入数组（int64）';
document.querySelector('#original').innerHTML=cells(setup.input);
document.querySelector('#request').textContent=`kth = ${setup.kth}（从零编号）· 找第 ${setup.kth+1} 小`;
document.querySelector('#run').onclick=async()=>{
 const button=document.querySelector('#run');button.disabled=true;
 const response=await fetch('/run',{method:'POST'});const d=await response.json();
 document.querySelector('#result').innerHTML=`<section><p>NumPy ${d.numpy} · Python ${d.python}</p><p>实际返回数组 p；橙框是索引 ${d.kth}</p><div class="array">${cells(d.output,d.kth)}</div><p>p[${d.kth}] = ${d.selected}：第 ${d.rank} 小</p></section><section id="status"><p>原数组未改动：${d.input_unchanged?'是':'否'}</p><p>左右分区条件：${d.left_ok&&d.right_ok?'通过':'未通过'}</p></section><p class="note">${d.output_sorted?'本次输出恰好全部有序。':'本次输出并未全部有序。'}<br>接口只保证分区，两侧内部不保证排序。</p>`;
 document.querySelector('#result').dataset.done='true';button.disabled=false;
};</script></html>'''

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass
    def do_GET(self):
        if self.path!='/':
            self.send_error(404);return
        data=json.loads((ROOT/'results.json').read_text())
        setup=dict(input=data['input'],kth=data['index'])
        body=PAGE.replace('__SETUP__',json.dumps(setup)).encode()
        self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_POST(self):
        if self.path!='/run':
            self.send_error(404);return
        body=json.dumps(run(),ensure_ascii=False).encode()
        self.send_response(200);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)

if __name__=='__main__':
    server=HTTPServer(('127.0.0.1',0),Handler)
    print(f'Open http://127.0.0.1:{server.server_port} and click the run button.',flush=True)
    server.serve_forever()
