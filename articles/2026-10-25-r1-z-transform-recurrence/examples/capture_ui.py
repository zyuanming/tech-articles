"""Capture actual local teaching UI using installed default Chromium. CC0."""
from pathlib import Path
from http.server import ThreadingHTTPServer
import threading,json
from playwright.sync_api import sync_playwright
from PIL import Image
import PIL,fontTools
from ui import Handler
ROOT=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium')
  page=browser.new_page(viewport={'width':1062,'height':1200},device_scale_factor=1)
  page.goto('http://127.0.0.1:'+str(server.server_port),wait_until='networkidle')
  page.wait_for_function('window.result && window.result.y[1]===2.5')
  # Every allowed input state must leave the numeric y-label clear of the axis.
  for coefficient in ['.5','1','1.1']:
   for initial in ['0','4']:
    for mode in ['main','impulse','step']:
     page.evaluate("""async ([a,i,m])=>{
       document.getElementById('a').value=a;
       document.getElementById('initial').value=i;
       document.getElementById('mode').value=m;
       await update();await document.fonts.ready;
     }""",[coefficient,initial,mode])
     bounds=page.evaluate("""()=>{
       const b=document.getElementById('maximum').getBBox();
       const a=document.getElementById('axes').getBBox();
       return {left:b.x,right:b.x+b.width,axis:a.x,top:b.y};
     }""")
     assert bounds['left']>=0 and bounds['top']>=0
     assert bounds['right']<=bounds['axis']-15,bounds
     assert page.evaluate('window.result.error')==0
  page.evaluate("""async()=>{
    document.getElementById('initial').value='0';
    document.getElementById('a').value='.5';
    document.getElementById('mode').value='main';
    await update();
  }""")
  assert page.evaluate('window.result.y[1]')==2.5
  page.evaluate('document.fonts.ready');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  page.locator('main').screenshot(path=str(ROOT/'assets/21-viewer.png'))
  version=browser.version;browser.close()
finally:server.shutdown();server.server_close()
meta=json.loads((ROOT/'examples/figure-metadata.json').read_text());meta=[x for x in meta if x['file']!='assets/21-viewer.png']
im=Image.open(ROOT/'assets/21-viewer.png')
meta.append(dict(file='assets/21-viewer.png',width=im.width,height=im.height,min_font_px=40,effective_min_font_at_354=40/3,identity='自制教学应用实际Chromium截图；非官方SciPy界面或设备实测',purpose='实际递推/SciPy对照与内部初态展示',checks=['real-browser','interactive-inputs','default-browser-settings','no-horizontal-overflow','actual-dimensions']))
(ROOT/'examples/figure-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
r=json.loads((ROOT/'examples/reproduction.json').read_text());r['chromium']=version;r['pillow']=PIL.__version__;r['fontTools']=fontTools.__version__;(ROOT/'examples/reproduction.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'screenshot':'assets/21-viewer.png','width':im.width,'height':im.height,'browser':version}))
