"""Real default-Chromium capture and all exposed input combinations. CC0."""
from pathlib import Path
from http.server import ThreadingHTTPServer
import threading,json,itertools
from playwright.sync_api import sync_playwright
from PIL import Image
from ui import Handler
ROOT=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium');page=b.new_page(viewport={'width':1062,'height':1200},device_scale_factor=1)
  page.goto('http://127.0.0.1:'+str(server.server_port),wait_until='networkidle');page.wait_for_function('window.result')
  count=0
  for m,tt,kd in itertools.product(['none','conditional','backcalc'],['.2','1','5'],['0','.5']):
   page.select_option('#method',m);page.select_option('#tt',tt);page.select_option('#kd',kd)
   page.wait_for_function('([m,t,k])=>window.result.method===m && window.result.Tt===t && window.result.Kd===k',arg=[m,float(tt),float(kd)])
   assert page.evaluate('window.result.series.t.length===601')
   assert page.evaluate('window.result.series.u.every(v=>v>=0 && v<=1)')
   assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
   bounds=page.locator('#maxlabel').evaluate('(e)=>{let b=e.getBBox();return {left:b.x,right:b.x+b.width,top:b.y}}')
   assert bounds['left']>=0 and bounds['right']<=125 and bounds['top']>=0
   count+=1
  page.select_option('#method','backcalc');page.select_option('#tt','1');page.select_option('#kd','0');page.wait_for_function('window.result.method==="backcalc" && window.result.Tt===1 && window.result.Kd===0')
  page.evaluate('document.fonts.ready');page.locator('main').screenshot(path=str(ROOT/'assets/22-viewer.png'));version=b.version;b.close()
finally:server.shutdown();server.server_close()
meta=json.loads((ROOT/'examples/figure-metadata.json').read_text());meta=[x for x in meta if x['file']!='assets/22-viewer.png'];im=Image.open(ROOT/'assets/22-viewer.png')
meta.append(dict(file='assets/22-viewer.png',width=im.width,height=im.height,min_font_px=40,effective_min_font_at_354=40/3,identity='自制教学应用默认Chromium实际截图，不是原厂界面或设备实测',purpose='模型实际运行及20秒状态/恢复指标',checks=['real-browser','all18input-combinations','no-overflow','dynamic-label-bounds','actual-dimensions']))
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
r=json.loads((ROOT/'examples/reproduction.json').read_text());r['chromium']=version;(ROOT/'examples/reproduction.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(combinations=count,width=im.width,height=im.height,browser=version)))
