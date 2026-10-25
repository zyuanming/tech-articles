"""Original teaching UI; serves actual cms.demo() output. CC0-1.0."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, platform
from cms import demo
PAGE='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Count-Min 真实执行</title><link rel="icon" href="data:,"><style>*{box-sizing:border-box}body{margin:0;background:#f8fafc;color:#142d42;font-family:"Noto Sans CJK SC",sans-serif;font-size:min(3.955vw,42px);line-height:1.5}main{width:1062px;max-width:100%;padding:min(4vw,42px)}h1{font-size:min(4.52vw,48px);margin:0 0 .5em}p{margin:.5em 0}button{font:inherit;background:#176297;color:white;border:0;border-radius:.3em;padding:.3em .6em}table{width:100%;border-collapse:collapse;margin:.5em 0;text-align:center}th,td{border:2px solid #bbcbd6;padding:.15em}.note{color:#166c57}section{border-top:2px solid #bbcbd6;margin-top:.6em}</style><main><h1>Count-Min 真实执行</h1><p>原创教学网页 · 固定映射 · Python</p><p>输入：A B A C A B<br>D A C A B A</p><button id="run">处理事件并查询 A—E</button><div id="result"><p>尚未运行</p></div></main><script>document.querySelector('#run').onclick=async()=>{const d=await(await fetch('/run',{method:'POST'})).json();let rows=d.table.map((r,i)=>`<tr><th>${i+1}</th>${r.map(v=>`<td>${v}</td>`).join('')}</tr>`).join('');let queries=Object.keys(d.exact).map(k=>`<tr><td>${k}</td><td>${d.exact[k]}</td><td>${d.estimates[k]}</td></tr>`).join('');document.querySelector('#result').innerHTML=`<section><p>Python ${d.python} · 共 ${d.total} 次事件</p><p>完整计数表（左侧为行号）</p><table><tr><th>行/列</th><th>0</th><th>1</th><th>2</th><th>3</th></tr>${rows}</table></section><section><table><tr><th>查询键</th><th>精确基线</th><th>CMS估计</th></tr>${queries}</table><p class="note">A：min(${d.candidates.A.join(', ')}) = ${d.estimates.A}<br>E 未出现，也会被碰撞抬高。</p><p>基线只供核对；CMS不保存精确账本。<br>此页不是 Redis 界面。</p></section>`;document.querySelector('#result').dataset.done='true';};</script></html>'''
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path!='/':self.send_error(404);return
  self.reply(PAGE.encode(),'text/html; charset=utf-8')
 def do_POST(self):
  if self.path!='/run':self.send_error(404);return
  d=demo();d['python']=platform.python_version()
  self.reply(json.dumps(d,ensure_ascii=False).encode(),'application/json')
 def reply(self,body,kind):
  self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
if __name__=='__main__':
 server=HTTPServer(('127.0.0.1',0),Handler)
 print(f'Open http://127.0.0.1:{server.server_port}',flush=True)
 server.serve_forever()
