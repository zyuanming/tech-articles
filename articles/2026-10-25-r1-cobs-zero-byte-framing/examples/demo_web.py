"""Local teaching viewer; real Python model behind each click. CC0-1.0."""
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.parse import urlsplit,parse_qs
import json
from model import encode,Receiver,hexbytes

def state(step):
    p=bytes.fromhex('11 22 00 33 00 00 44 00')
    stream=encode(p)[0]+b'\0'+encode(b'')[0]+b'\0'
    sizes=[2,3,1,5,1];r=Receiver();pos=0;last=None
    for size in sizes[:step]:
        last=r.feed(stream[pos:pos+size]);pos+=size
    return dict(step=step,total=len(sizes),chunk=hexbytes(last['chunk']) if last else '尚未送入',
                buffer=hexbytes(r.buffer) or '空',
                packets=[hexbytes(x) or '空 payload' for x in r.packets],
                emitted=len(last['emitted']) if last else 0)

HTML='''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>COBS 分段接收实验</title><style>
*{box-sizing:border-box}body{margin:0;background:#f8fafc;color:#142d42;
font-family:"Noto Sans CJK SC",sans-serif;font-size:clamp(14px,4vw,42px)}
main{padding:clamp(16px,4.7vw,50px);max-width:1062px;margin:auto}
h1{font-size:1.14em;margin:0 0 .7em}p{margin:.55em 0}
button{font:inherit;padding:.3em .6em;border:2px solid #176297;
background:#e1edf7;color:#142d42;border-radius:10px;margin:.2em .4em .5em 0}
.value{padding:.35em;background:#e9f1eb;overflow-wrap:anywhere}
.label{color:#176297}.note{border-top:2px solid #ccd8e0;padding-top:.6em}
</style><main><h1>COBS 分段接收实验</h1>
<p>本文 Python 模型 · 字节用十六进制</p>
<button id="next">送入下一片段</button><button id="reset">重置</button>
<p id="step" class="label"></p><p>本次收到</p><p id="chunk" class="value"></p>
<p>等待后续字节的缓冲</p><p id="buffer" class="value"></p>
<p id="emitted" class="label"></p><p>累计交出的 payload</p>
<div id="packets"></div><p class="note">分段由实验指定；未连接真实串口。</p>
</main><script>
let step=0;
async function draw(){let d=await(await fetch('/run?step='+step)).json();
document.querySelector('#step').textContent='片段 '+d.step+' / '+d.total;
for(let k of ['chunk','buffer'])document.querySelector('#'+k).textContent=d[k];
document.querySelector('#emitted').textContent='本次交出 '+d.emitted+' 个包';
document.querySelector('#packets').replaceChildren(...(d.packets.length?d.packets:['尚无完整包']).map(x=>{let p=document.createElement('p');p.className='value';p.textContent=x;return p}));
document.querySelector('#next').disabled=step>=d.total;
document.body.dataset.step=step;
}
document.querySelector('#next').onclick=()=>{step++;draw()};
document.querySelector('#reset').onclick=()=>{step=0;draw()};draw();
</script></html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        u=urlsplit(self.path)
        if u.path=='/run':
            try:
                n=int(parse_qs(u.query).get('step',['0'])[0])
                if not 0<=n<=5:raise ValueError()
            except ValueError:self.send_error(400);return
            body=json.dumps(state(n),ensure_ascii=False).encode();kind='application/json'
        elif u.path=='/':body=HTML.encode();kind='text/html; charset=utf-8'
        elif u.path=='/favicon.ico':self.send_response(204);self.end_headers();return
        else:self.send_error(404);return
        self.send_response(200);self.send_header('Content-Type',kind);self.end_headers();self.wfile.write(body)
    def log_message(self,*a):pass

if __name__=='__main__':
    print('Open http://127.0.0.1:8018')
    HTTPServer(('127.0.0.1',8018),Handler).serve_forever()
