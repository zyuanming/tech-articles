"""Local live teaching interface. Code CC0; original interface CC BY 4.0."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import json
from experiment import run

HTML = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>epoll 本地实验</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f7f9fc;color:#152f43;
font-family:"Noto Sans CJK SC",sans-serif;font-size:clamp(14px,3.96vw,42px)}
main{max-width:1062px;padding:1em;margin:auto}h1{font-size:1.35em;margin:0 0 .5em}
p{margin:.5em 0}button,select{font:inherit;padding:.4em;border:2px solid #1b5b8b;
background:white;border-radius:.3em;color:inherit}section{border-top:3px solid #b4cbdc;
margin-top:.8em;padding-top:.6em}strong{color:#166552}#trace p{padding:.25em .5em;
background:#e2edf5;overflow-wrap:anywhere}label{display:block;margin-top:.7em}
</style><main><h1>epoll：通知与读取</h1>
<p>真实 Linux 本地 socketpair 实验</p><p>每次点击重新执行；不是回放</p>
<button id="run">运行实验</button><p id="status">尚未运行</p>
<section id="result" hidden><p id="env"></p><p id="comparison"></p>
<label>查看模式 <select id="mode"><option>ET</option><option>LT</option></select></label>
<div id="trace"></div><p>poll(0) 立即返回；本页不测性能。</p>
</section></main><script>
let data;const $=s=>document.querySelector(s);
function ev(xs){return xs.length?xs[0].flags.join('+'):'无事件'}
function render(){const r=data.partial.find(r=>r.mode===$('#mode').value);
const lines=['写入 '+r.payload,'第一次轮询：'+ev(r.first_event),
'读 2 字节 → '+r.first_read.text,'缓冲还剩 '+r.remaining,
'第二次轮询：'+ev(r.second_event),
'继续读：'+r.drained.map(x=>x.kind==='data'?x.text:x.kind).join(' → ')];
$('#trace').replaceChildren(...lines.map(s=>{const p=document.createElement('p');p.textContent=s;return p}));}
$('#mode').onchange=()=>data&&render();
$('#run').onclick=async()=>{const button=$('#run');button.disabled=true;
try{const res=await fetch('/run',{method:'POST'});if(!res.ok)throw Error('实验失败');
data=await res.json();$('#env').textContent='Linux '+data.environment.observed_kernel_release+' / Python '+data.environment.python;
$('#comparison').textContent='读走 ab 后：LT '+ev(data.partial[0].second_event)+'；ET '+ev(data.partial[1].second_event);
$('#result').hidden=false;render();$('#status').textContent='本次实验完成';window.done=true;
}catch(e){$('#status').textContent=e.message}finally{button.disabled=false}};
</script></html>'''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        if self.path != '/':
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        if self.path != '/run':
            self.send_error(404)
            return
        data = json.dumps(run(), ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8920)
    args = parser.parse_args()
    print('Open http://127.0.0.1:' + str(args.port))
    HTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
