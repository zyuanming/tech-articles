"""Original local result viewer. Code CC0-1.0."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
def page():
 d=json.loads((ROOT/'examples/results.json').read_text());r=d['render']
 return '''<!doctype html><html lang="zh"><meta charset="utf-8"><title>MIS教学结果查看器</title><style>*{box-sizing:border-box}body{margin:0;background:#f7fafc;color:#163145;font:42px/1.5 sans-serif;padding:42px}h1{font-size:52px;margin:0 0 22px}p{margin:22px 0}select{font:42px sans-serif;max-width:100%;padding:12px}img{width:100%;image-rendering:pixelated;border:2px solid #60778b}.note{font-size:42px}#result{white-space:pre-wrap}button{font-size:42px}</style><h1>MIS：实跑结果查看器</h1><p>Python '''+d['python']+' / NumPy '+d['numpy']+'''</p><p>160×88；2048方向离散模型；每点32项</p><select id="method"><option value="light">只按光分布</option><option value="brdf">只按材质分布</option><option value="balance">balance 16+16</option><option value="power">power 16+16</option></select><p>读取已生成的计算结果，不是实时GPU渲染。</p><img id="render" alt="实际球渲染"><p id="result"></p><script>const stats='''+json.dumps(r['stats'])+r''';function update(){const m=document.querySelector('#method').value;document.querySelector('#render').src='/examples/output/'+m+'.png';const s=stats[m];document.querySelector('#result').textContent='线性RMSE：'+s.rmse.toFixed(6)+'\n解析期望MSE：'+s.expected_mse.toFixed(6)+'\n随机种子：'+s.seed;}document.querySelector('#method').addEventListener('change',update);update()</script></html>'''
class Handler(SimpleHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/':
   b=page().encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(b)
  else:super().do_GET()
 def log_message(self,*args):pass
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8080);a=p.parse_args();ThreadingHTTPServer(('127.0.0.1',a.port),partial(Handler,directory=str(ROOT))).serve_forever()
