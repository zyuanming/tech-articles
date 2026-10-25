"""Real local Python model interface, CC0-1.0. Not a network benchmark."""
from http.server import BaseHTTPRequestHandler,HTTPServer
from run_examples import run
import json
PAGE='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>令牌桶有理数实跑</title><link rel="icon" href="data:,"><style>*{box-sizing:border-box}body{margin:0;background:#f8fafc;color:#142d42;font-family:"Noto Sans CJK SC",sans-serif;font-size:min(3.955vw,42px);line-height:1.55}main{width:1062px;max-width:100%;padding:min(4vw,42px)}h1{font-size:min(4.52vw,48px);margin:0 0 .5em}p{margin:.5em 0}button{font:inherit;color:white;background:#176297;padding:.35em .6em;border:0;border-radius:.3em}table{width:100%;border-collapse:collapse;margin-top:.6em}th,td{text-align:left;border-bottom:1px solid #bccbd6;padding:.2em}th{font-weight:normal}small{font:inherit}#checks{color:#166c57}</style><main><h1>令牌桶 · 精确有理数模型</h1><p>r=2 份/秒；B=6 份；初始满桶</p><p>输入 A–I；FIFO；超大 G 先移除</p><button id="run">执行 Python 并检查</button><div id="result"><p>尚未运行</p></div></main><script>document.querySelector('#run').onclick=async()=>{const response=await fetch('/run',{method:'POST'});const d=await response.json();const number=s=>{if(s===null)return '超大';const [a,b=1]=s.split('/');return +a/+b};document.querySelector('#result').innerHTML=`<p>Python ${d.python} · fractions.Fraction</p><table><thead><tr><th>包</th><th>到达秒</th><th>费用</th><th>整形秒</th></tr></thead><tbody>${d.shaping.map(x=>`<tr><td>${x.name}</td><td>${number(x.arrival)}</td><td>${number(x.cost)}</td><td>${number(x.departure)}</td></tr>`).join('')}</tbody></table><p>监管接受：${d.policing.filter(x=>x.allowed).map(x=>x.name).join(' ')}</p><p id="checks">${d.checks.exhaustive_sequences} 组独立检查通过<br>${d.checks.intervals} 个区间上界通过</p><p>原创教学程序；没有发送网络流量。</p>`;document.querySelector('#result').dataset.done='true';};</script></html>'''
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path!='/':self.send_error(404);return
  b=PAGE.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_POST(self):
  if self.path!='/run':self.send_error(404);return
  b=json.dumps(run(),ensure_ascii=False).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
if __name__=='__main__':
 server=HTTPServer(('127.0.0.1',0),Handler);print(f'Open http://127.0.0.1:{server.server_port}',flush=True);server.serve_forever()
