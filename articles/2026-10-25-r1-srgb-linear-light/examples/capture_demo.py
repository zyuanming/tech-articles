"""Capture actual local calculation; add sRGB identity without changing pixels. CC0."""
from pathlib import Path
import argparse,json,threading
from http.server import ThreadingHTTPServer
from PIL import Image,PngImagePlugin
from playwright.sync_api import sync_playwright
from demo_web import Handler
P=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--chromium',required=True);p.add_argument('--evidence',required=True);a=p.parse_args();out=Path(a.evidence);out.mkdir(parents=True,exist_ok=True)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=a.chromium)
 for width in [1062,354]:
  page=b.new_page(viewport={'width':width,'height':900},device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}',wait_until='networkidle');page.click('#run');page.wait_for_function('window.data!==null');page.evaluate('document.fonts.ready')
  d=page.evaluate('window.data');assert d['direct']==128 and d['linear']==188;assert not errors;assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  dest=P/'assets/15-live-demo.png' if width==1062 else out/'demo-354.png';page.screenshot(path=str(dest),full_page=True)
  im=Image.open(dest);pixels=im.tobytes();info=PngImagePlugin.PngInfo();info.add(b'sRGB',b'\x00');im.save(dest,pnginfo=info);assert Image.open(dest).tobytes()==pixels
  samples={}
  for key in ['direct','linear']:
   box=page.locator('#patch-'+key).bounding_box();xy=(int(box['x']+box['width']/2),int(box['y']+box['height']/2));color=Image.open(dest).convert('RGB').getpixel(xy);assert color==(d[key],)*3;samples[key]=color
  rows.append(dict(width=width,data=d,sampled_pixels=samples,no_overflow=True,page_errors=errors,browser=b.version));page.close()
 b.close()
server.shutdown();(out/'capture-result.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print('actual browser checks PASS')
