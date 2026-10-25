"""Local teaching viewer; independent UI and code CC0, screenshots CC BY 4.0."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
import json
import numpy as np
from scipy import signal
from model import recurrence
HTML='''<!doctype html><meta charset="utf-8"><title>递推与 Z 变换实验</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f8fafc;color:#142d42;font:42px/1.5 "Noto Sans CJK SC",sans-serif}main{width:1062px;padding:40px}h1{font-size:48px;margin:0 0 15px}p{margin:15px 0}select{font:40px sans-serif;padding:8px;border:2px solid #627487;background:white;color:#142d42}label{display:inline-block;margin:12px 20px 10px 0}.small{font-size:40px}svg{display:block;width:982px;height:390px;background:#eef3f7}table{width:100%;border-collapse:collapse;font-size:40px}td,th{text-align:left;border-bottom:2px solid #c0ccd7;padding:9px 12px}#status{color:#166c57}</style>
<main><h1>递推与 Z 变换实验</h1><p>y[n] = a y[n−1] + x[n]</p>
<label>系数 a <select id="a"><option>.5</option><option>1</option><option>1.1</option></select></label>
<label>y[−1] <select id="initial"><option>0</option><option>4</option></select></label>
<label>输入 <select id="mode"><option value="main">1, 2, 0, …</option><option value="impulse">一拍冲激</option><option value="step">每拍为1</option></select></label>
<p class="small">灰：输入　蓝：递推输出；横轴 n</p><svg id="plot" viewBox="0 0 982 390"></svg>
<p id="status"></p><p id="state" class="small"></p>
<table><thead><tr><th>n</th><th>x[n]</th><th>递推 y[n]</th><th>SciPy</th></tr></thead><tbody id="table"></tbody></table>
<p class="small">自产教学模型 · SciPy 1.17.0 · 任意数值单位</p></main>
<script>
const ids=['a','initial','mode'];
async function update(){let q=new URLSearchParams(ids.map(id=>[id,document.getElementById(id).value]));let d=await(await fetch('/data?'+q)).json();window.result=d;
let max=Math.max(1,...d.x,...d.y),W=795,H=290,L=140,T=40;let pt=(i,v)=>[L+i/7*W,T+H-v/max*H];
let line=(v,col)=>'<polyline fill="none" stroke="'+col+'" stroke-width="5" points="'+v.map((z,i)=>pt(i,z).join(',')).join(' ')+'"/>';
let dots=d.y.map((v,i)=>{let p=pt(i,v);return '<circle cx="'+p[0]+'" cy="'+p[1]+'" r="7" fill="#176297"/>'}).join('');
document.getElementById('plot').innerHTML='<path id="axes" d="M'+L+' '+T+'V'+(T+H)+'H'+(L+W)+'" stroke="#627487" fill="none" stroke-width="3"/>'+line(d.x,'#627487')+line(d.y,'#176297')+dots+'<text id="maximum" x="'+(L-18)+'" y="55" text-anchor="end" font-size="40">'+max.toFixed(1)+'</text><text x="'+(L-18)+'" y="350" text-anchor="end" font-size="40">0</text><text x="920" y="380" font-size="40">7</text>';
document.getElementById('status').textContent='两实现最大差：'+d.error;
document.getElementById('state').textContent='内部初始 zi = '+d.zi+'；结束 zf = '+d.zf.toFixed(6);
document.getElementById('table').innerHTML=d.y.slice(0,6).map((v,i)=>'<tr><td>'+i+'</td><td>'+d.x[i]+'</td><td>'+v.toFixed(4)+'</td><td>'+d.scipy[i].toFixed(4)+'</td></tr>').join('');}
ids.forEach(id=>document.getElementById(id).onchange=update);update();
</script>'''
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  u=urlparse(self.path)
  if u.path=='/':body=HTML.encode();content='text/html; charset=utf-8'
  elif u.path=='/data':
   q=parse_qs(u.query);a=float(q.get('a',['.5'])[0]);initial=float(q.get('initial',['0'])[0]);mode=q.get('mode',['main'])[0]
   if a not in [.5,1.,1.1] or initial not in [0,4] or mode not in ['main','impulse','step']:
    self.send_error(400);return
   x=np.zeros(8);x[0]=1
   if mode=='main':x[1]=2
   if mode=='step':x[:]=1
   y=recurrence(x,a,initial);zi=signal.lfiltic([1.],[1.,-a],[initial]);ref,zf=signal.lfilter([1.],[1.,-a],x,zi=zi)
   body=json.dumps(dict(x=x.tolist(),y=y.tolist(),scipy=ref.tolist(),a=a,initial=initial,zi=float(zi[0]),zf=float(zf[0]),error=float(max(abs(y-ref))))).encode();content='application/json'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',content);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
if __name__=='__main__':
 print('Teaching viewer: http://127.0.0.1:8111/',flush=True)
 ThreadingHTTPServer(('127.0.0.1',8111),Handler).serve_forever()
