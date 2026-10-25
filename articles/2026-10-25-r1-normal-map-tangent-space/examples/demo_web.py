"""Original teaching UI, CC0-1.0. Python computes data on every click."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from io import BytesIO
import json,base64,platform
from PIL import Image,PngImagePlugin
from normal_map import unpack,transform,dot,render
HTML='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><link rel="icon" href="data:,"><title>法线换基计算</title><style>body{margin:0;background:#f8fafc;color:#142d42;font:42px sans-serif}main{padding:42px;box-sizing:border-box;width:1062px;max-width:100%}h1{font-size:50px}p{line-height:1.5}button{font:inherit;background:#176297;color:white;padding:16px;border:0;border-radius:14px}.pair{display:flex;gap:36px}.pair div{width:46%}.pair img{width:100%;image-rendering:pixelated}@media(max-width:600px){body{font-size:16px}main{padding:14px}h1{font-size:22px}button{padding:10px}.pair{gap:12px}}</style><main><h1>法线贴图：真实Python计算</h1><p>理想RGB：0.68 / 0.74 / 0.90<br>T=(0,1,0)，B=(-1,0,0)，N=(0,0,1)</p><button id="run">重新计算换基与光照</button><section id="result" hidden><p id="version"></p><p id="values"></p><div class="pair"><div>平坦法线<img id="flat"></div><div>程序法线纹理<img id="mapped"></div></div><p>下方是另一个平面模型的CPU输出。<br>96×96像素；不是游戏或设备实测。</p></section></main><script>window.data=null;document.querySelector('#run').onclick=async()=>{let d=window.data=await(await fetch('/compute')).json();document.querySelector('#result').hidden=false;document.querySelector('#version').textContent='Python '+d.python;document.querySelector('#values').innerHTML='局部 n：'+d.nt.map(x=>x.toFixed(2)).join(' / ')+'<br>世界 n：'+d.nw.map(x=>x.toFixed(2)).join(' / ')+'<br>正确点积 '+d.good.toFixed(2)+'；漏换基 '+d.wrong.toFixed(2);for(let k of ['flat','mapped'])document.querySelector('#'+k).src='data:image/png;base64,'+d.images[k];};</script>'''
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path=='/':data=HTML.encode();kind='text/html; charset=utf-8'
  elif self.path=='/compute':
   nt=unpack((.68,.74,.9));nw=transform(nt,(0,1,0),(-1,0,0),(0,0,1));light=(-.48,.36,.8);images={}
   for mode in ['flat','mapped']:
    pixels,detail=render(mode);im=Image.new('RGB',(detail['size'],detail['size']));im.putdata(pixels);b=BytesIO();info=PngImagePlugin.PngInfo();info.add(b'sRGB',b'\x00');im.save(b,format='PNG',pnginfo=info);images[mode]=base64.b64encode(b.getvalue()).decode()
   data=json.dumps(dict(python=platform.python_version(),nt=nt,nw=nw,good=dot(nw,light),wrong=dot(nt,light),images=images)).encode();kind='application/json'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
if __name__=='__main__':
 s=ThreadingHTTPServer(('127.0.0.1',0),Handler);print(f'http://127.0.0.1:{s.server_port}',flush=True);s.serve_forever()
