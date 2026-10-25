"""Capture the genuinely running local viewer; code CC0-1.0."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
import argparse,threading,json
from playwright.sync_api import sync_playwright
import ui
p=argparse.ArgumentParser();p.add_argument('--chromium',default='/usr/bin/chromium');a=p.parse_args()
s=ThreadingHTTPServer(('127.0.0.1',0),partial(ui.Handler,directory=str(ui.ROOT)));threading.Thread(target=s.serve_forever,daemon=True).start()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=a.chromium)
 page=b.new_page(viewport={'width':1062,'height':1200},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:'+str(s.server_port)+'/',wait_until='networkidle')
 for mode in ['light','brdf','power','balance']:
  page.select_option('#method',mode);page.locator('#render').evaluate('(i)=>i.decode()')
  assert page.locator('#render').get_attribute('src').endswith(mode+'.png')
  assert '线性RMSE' in page.locator('#result').inner_text()
 assert not errors,errors
 assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 page.screenshot(path=str(ui.ROOT/'assets/20-live-ui.png'),full_page=True)
 b.close()
s.shutdown();print('real HTTP viewer: 4 selections, image decode, no overflow PASS')
