"""Local teaching viewer, actual model calls. Code CC0."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
import json
from model import simulate,metrics
HTML='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>积分饱和查看器</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f8fafc;color:#142d42;font:42px/1.5 "Noto Sans CJK SC",sans-serif}main{width:1062px;padding:40px}h1{font-size:48px;margin:0 0 16px}p{margin:16px 0}select{font:40px sans-serif;padding:8px;color:#142d42;background:white}label{display:block;margin:14px 0}.small{font-size:40px}svg{width:982px;height:400px;display:block;background:#eaf1f6}table{width:100%;border-collapse:collapse;font-size:40px}th,td{border-bottom:2px solid #c0ccd7;padding:10px 8px;text-align:left}#state{color:#166c57}</style>
<main><h1>积分饱和：实际计算查看器</h1><p class="small">本文教学模型；不是设备或原厂软件</p>
<label>方法 <select id="method"><option value="none">无抗饱和</option><option value="conditional">条件积分</option><option value="backcalc" selected>回算</option></select></label>
<label>Tt <select id="tt"><option>.2</option><option selected>1</option><option>5</option></select> 秒（仅回算生效）</label>
<label>Kd <select id="kd"><option selected>0</option><option>.5</option></select> （非零时 Tf=0.5秒）</label>
<p>固定 Δt=0.1秒，Kp=2，Ki=0.5</p><p>灰：目标　蓝：温升 y；横轴：秒</p><svg id="plot" viewBox="0 0 982 400"></svg>
<p id="state"></p><table><thead><tr><th>20秒目标下降瞬间</th><th>值</th></tr></thead><tbody id="table"></tbody></table>
<p id="timing"></p><p class="small">模型结果，非设备实测；误差带±0.02<br>保持检查仅到60秒仿真结束</p></main>
<script>
let serial=0;
async function update(){let token=++serial;let method=document.querySelector('#method').value,tt=document.querySelector('#tt').value,kd=document.querySelector('#kd').value;
let d=await(await fetch('/data?method='+method+'&tt='+tt+'&kd='+kd)).json();if(token!==serial)return;window.result=d;
const L=140,R=940,TOP=40,BOT=330,scale=1.6;
function path(arr){return arr.map((v,i)=>(i?'L':'M')+(L+(R-L)*d.series.t[i]/60)+','+(BOT-(BOT-TOP)*v/scale)).join(' ')}
document.querySelector('#plot').innerHTML='<path d="M'+L+' '+TOP+'V'+BOT+'H'+R+'" stroke="#627487" fill="none" stroke-width="3"/><path d="'+path(d.series.r)+'" stroke="#627487" fill="none" stroke-width="5"/><path d="'+path(d.series.y)+'" stroke="#176297" fill="none" stroke-width="6"/><text id="maxlabel" x="'+(L-18)+'" y="55" text-anchor="end" font-size="40">1.6</text><text x="'+(L-18)+'" y="335" text-anchor="end" font-size="40">0</text><text x="'+(L-15)+'" y="385" font-size="40">0</text><text x="920" y="385" font-size="40">60</text>';
let q=d.metrics.at_drop;document.querySelector('#table').innerHTML=['y','P','I','D','v','u'].map(k=>'<tr><td>'+k+'</td><td>'+q[k].toFixed(6)+'</td></tr>').join('');
document.querySelector('#state').textContent='同一模型已执行 '+d.series.t.length+' 个采样点';
function fmt(v){return v===null?'观察窗内未达到':v.toFixed(1)+'秒'}
document.querySelector('#timing').textContent='离开上限：'+fmt(d.metrics.release)+'；进入并保持误差带：'+fmt(d.metrics.settle_02);
}
for(let x of document.querySelectorAll('select'))x.onchange=update;update();
</script></html>'''
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  parsed=urlparse(self.path)
  if parsed.path=='/data':
   q=parse_qs(parsed.query);m=q.get('method',['backcalc'])[0];tt=float(q.get('tt',['1'])[0]);kd=float(q.get('kd',['0'])[0])
   if m not in ['none','conditional','backcalc'] or tt not in [.2,1.,5.] or kd not in [0.,.5]:self.send_error(400);return
   d=simulate(m,Tt=tt,Kd=kd);out=json.dumps(dict(method=m,Tt=tt,Kd=kd,series=d,metrics=metrics(d))).encode();typ='application/json'
  elif parsed.path=='/':out=HTML.encode();typ='text/html; charset=utf-8'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',typ);self.send_header('Content-Length',str(len(out)));self.end_headers();self.wfile.write(out)
if __name__=='__main__':
 print('http://127.0.0.1:8112/',flush=True);ThreadingHTTPServer(('127.0.0.1',8112),Handler).serve_forever()
