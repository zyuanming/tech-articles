"""Local educational viewer, CC0. No external resources or network fetches."""
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.parse import urlparse,parse_qs
from pathlib import Path
import json
import numpy as np
from model import segment,evaluate
ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'results.json').read_text())
HTML='''<!doctype html><meta charset="utf-8"><title>Catmull–Rom 教学查看器</title>
<style>body{margin:0;background:#f8fafc;color:#142d42;font:40px "Noto Sans CJK SC",sans-serif;padding:36px}h1{font-size:48px;margin:0 0 24px}p{margin:18px 0}select,input,button{font:40px sans-serif}svg{width:100%;height:auto;border:2px solid #b7c8d5}label{display:block;margin:16px 0}output{display:block;line-height:1.7}.legend{color:#176297}small{font-size:40px}</style>
<h1>Catmull–Rom 教学查看器</h1><p>Python 实算；原创控制点；非引擎截图</p>
<label>参数化 <select id="alpha"><option value="0">均匀 α=0</option><option value="0.5">向心 α=0.5</option><option value="1">弦长 α=1</option></select></label>
<label>局部 u <input id="u" type="range" min="0" max="1" step="0.01" value="0.5"></label>
<div id="plot"></div><output id="result"></output><p class="legend">灰：控制多边形　蓝：中段　红：当前位置</p>
<small>改参数会改变曲线；移动滑块只改变位置。</small>
<script>
async function update(){let a=document.querySelector('#alpha').value,u=document.querySelector('#u').value;let r=await fetch('/api?alpha='+a+'&u='+u),d=await r.json();let f=q=>[70+q[0]*135,520-q[1]*135];let path=q=>q.map((v,i)=>(i?'L':'M')+f(v).join(',')).join(' ');let q=f(d.value);document.querySelector('#plot').innerHTML='<svg viewBox="0 0 970 580"><path d="'+path(d.points)+'" fill="none" stroke="#627487" stroke-width="3"/><path d="'+path(d.curve)+'" fill="none" stroke="#176297" stroke-width="7"/>'+d.points.map(v=>{let p=f(v);return '<circle cx="'+p[0]+'" cy="'+p[1]+'" r="9" fill="#142d42"/>'}).join('')+'<circle cx="'+q[0]+'" cy="'+q[1]+'" r="13" fill="#a13631"/></svg>';document.querySelector('#result').innerHTML='u = '+d.u.toFixed(2)+'<br>位置 = ('+d.value.map(v=>v.toFixed(4)).join(', ')+')<br>局部速度大小 = '+d.speed.toFixed(4);}
document.querySelectorAll('input,select').forEach(e=>e.addEventListener('input',update));update();
</script>'''
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  url=urlparse(self.path)
  if url.path=='/api':
   q=parse_qs(url.query);alpha=float(q.get('alpha',['0'])[0]);u=float(q.get('u',['.5'])[0])
   if alpha not in [0,.5,1] or not 0<=u<=1:self.send_error(400);return
   p=DATA['main'][0]['points'];s=segment(p,alpha)
   body=json.dumps(dict(points=p,curve=evaluate(s,np.linspace(0,1,401)).tolist(),value=evaluate(s,u).tolist(),u=u,speed=float(np.linalg.norm(evaluate(s,u,1))))).encode();kind='application/json'
  elif url.path=='/':body=HTML.encode();kind='text/html; charset=utf-8'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
if __name__=='__main__':HTTPServer(('127.0.0.1',8110),Handler).serve_forever()
