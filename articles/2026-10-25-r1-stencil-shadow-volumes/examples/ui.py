"""Read-only local teaching viewer for already computed results; CC0-1.0."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,argparse
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kw):super().__init__(*args,directory=str(ROOT),**kw)
 def do_GET(self):
  if self.path!='/':return super().do_GET()
  d=json.loads((ROOT/'examples/results.json').read_text());r=d['renders']['inside']
  body=f'''<!doctype html><html lang="zh"><meta charset="utf-8"><title>阴影体 CPU 参考模型</title>
<style>body{{margin:0;padding:36px;background:#f8fafc;color:#142d42;font:42px sans-serif;max-width:990px}}h1{{font-size:48px}}h2{{font-size:44px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:30px}}img{{width:100%;image-rendering:pixelated}}p{{line-height:1.6}}select{{font-size:42px}}</style>
<h1>阴影体 CPU 参考模型 v{d['version']}</h1><p>Python {d['python']} · NumPy {d['numpy']}<br>160×128像素；解析求交，不是GPU运行</p>
<label>选择视角 <select id="mode"><option value="inside">相机在阴影体内</option><option value="outside">相机在阴影体外</option><option value="other-light">体外：更换光源</option></select></label>
<div class="grid"><section><h2>闭合 z-fail</h2><img id="good" src="examples/output/inside-zfail.png"></section><section><h2>z-pass 初值0</h2><img id="bad" src="examples/output/inside-zpass.png"></section></div>
<p id="stats">有效点 {r['valid']}；z-fail 错 {r['zfail_errors']}<br>z-pass 错 {r['zpass_errors']}</p>
<p>独立真值：接收点到灯的线段与盒相交。<br>数据从执行后的 results.json 读取。</p>
<script>const data={json.dumps(d['renders'])};document.querySelector('#mode').onchange=e=>{{let k=e.target.value,r=data[k];document.querySelector('#good').src='examples/output/'+k+'-zfail.png';document.querySelector('#bad').src='examples/output/'+k+'-zpass.png';document.querySelector('#stats').innerHTML=`有效点 ${{r.valid}}；z-fail 错 ${{r.zfail_errors}}<br>z-pass 错 ${{r.zpass_errors}}`;}};</script></html>'''.encode()
  self.send_response(200);self.send_header('Content-Type','text/html;charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8080);a=p.parse_args()
 ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
