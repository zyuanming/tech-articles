"""Original executable file-sort teaching UI. Code CC0-1.0."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from run_examples import run
from external_sort import KEYS
import json,platform
HTML='''<!doctype html><meta charset="utf-8"><link rel="icon" href="data:,"><title>外部归并真实执行</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f8fafc;color:#142d42;font-family:Arial,"Noto Sans CJK SC",sans-serif;font-size:42px;padding:42px;line-height:1.5}h1{font-size:52px;margin:0 0 20px}button{font:inherit;background:#176297;color:white;border:0;padding:12px 20px;border-radius:12px}table{width:100%;border-collapse:collapse;margin:25px 0}td,th{border:2px solid #b8c9d8;padding:8px;text-align:center}p{margin:24px 0}.result{color:#166c57} @media(max-width:600px){body{font-size:16px;padding:14px}h1{font-size:22px}button{font-size:16px}td,th{padding:4px}}</style>
<h1>外部归并：真实文件执行</h1><p>原创 Python 教学程序<br>每次新建二进制输入与各代文件</p>
<button id="run">生成文件并开始归并</button><div id="out"></div>
<script>document.querySelector('#run').onclick=async()=>{let d=await(await fetch('/run')).json();window.result=d;
let rows=d.phases.map(x=>`<tr><td>${x.phase}</td><td>${x.run_count}</td><td>${x.read_blocks}</td><td>${x.write_blocks}</td></tr>`).join('');
document.querySelector('#out').innerHTML=`<p>Python ${d.python}<br>输入 ${d.n} 条 / ${d.input_bytes} 字节</p><p>每段 6 条 · 每块 2 条 · 三路归并</p><table><tr><th>阶段</th><th>段数</th><th>读块</th><th>写块</th></tr>${rows}</table><p>最终键序列：</p><p class="result">${d.output.map(x=>x[0]).join(' ')}</p><p class="result">逐记录与独立排序基线相同</p><p>输出 ${d.output_bytes} 字节<br>合计 ${d.total_blocks} 次逻辑块传输</p><p>阶段 0 是生成初始段。<br>这是文件程序实跑；不是磁盘测速。<br>Python 总内存并非只有 64 字节。</p>`;};</script>'''
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path=='/':body=HTML.encode();kind='text/html; charset=utf-8'
  elif self.path=='/run':
   d=run(KEYS,trace=True);d.update(n=len(KEYS),python=platform.python_version(),total_blocks=sum(x['read_blocks']+x['write_blocks'] for x in d['phases']))
   body=json.dumps(d).encode();kind='application/json'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
def server():return ThreadingHTTPServer(('127.0.0.1',0),Handler)
if __name__=='__main__':
 s=server();print(f'http://127.0.0.1:{s.server_port}',flush=True);s.serve_forever()
