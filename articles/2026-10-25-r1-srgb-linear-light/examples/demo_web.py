"""Original local teaching UI; CC0-1.0. This is not a photometric measurement."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import json,platform
from srgb import decode,encode,q8
HTML='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><link rel="icon" href="data:,"><title>sRGB计算</title><style>body{margin:0;background:#f8fafc;color:#142d42;font:42px sans-serif}main{padding:42px;box-sizing:border-box;width:1062px;max-width:100%}h1{font-size:52px}button{font:inherit;background:#176297;color:white;border:0;border-radius:14px;padding:16px}p{line-height:1.5}.patch{height:180px;border:2px solid #627487}.num{font-variant-numeric:tabular-nums}@media(max-width:600px){body{font-size:16px}main{padding:14px}h1{font-size:22px}button{padding:10px}.patch{height:70px}}</style><main><h1>sRGB：真实Python计算</h1><p>输入：黑0、白1，权重各0.5</p><button id="run">计算两条路径</button><section id="result" hidden><p id="version"></p><p id="direct"></p><div class="patch" id="patch-direct"></div><p id="linear"></p><div class="patch" id="patch-linear"></div><p class="num" id="values"></p><p>色块是计算出的编码像素。<br>这不是显示器光度测量。</p></section></main><script>window.data=null;document.querySelector('#run').onclick=async()=>{window.data=await(await fetch('/compute')).json();let d=window.data;document.querySelector('#result').hidden=false;document.querySelector('#version').textContent='Python '+d.python;document.querySelector('#direct').textContent='直接平均编码：'+d.direct;document.querySelector('#linear').textContent='线性平均后编码：'+d.linear;for(let k of ['direct','linear'])document.querySelector('#patch-'+k).style.background='rgb('+[d[k],d[k],d[k]].join(',')+')';document.querySelector('#values').innerHTML='S=0.5 → L='+d.decoded.toFixed(6)+'<br>L=0.5 → S='+d.encoded.toFixed(6);};</script>'''
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        if self.path=='/':data=HTML.encode();kind='text/html; charset=utf-8'
        elif self.path=='/compute':data=json.dumps(dict(python=platform.python_version(),direct=q8(.5),linear=q8(encode(.5)),decoded=decode(.5),encoded=encode(.5))).encode();kind='application/json'
        else:self.send_error(404);return
        self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);print(f'http://127.0.0.1:{server.server_port}',flush=True);server.serve_forever()
