"""Capture a real button click, using an already installed Chromium. CC0-1.0."""
from pathlib import Path
import argparse, threading, json
from http.server import HTTPServer
from playwright.sync_api import sync_playwright
from demo_web import Handler
p=argparse.ArgumentParser();p.add_argument('--chromium',required=True);p.add_argument('--evidence',required=True)
a=p.parse_args();root=Path(__file__).resolve().parents[1];dest=Path(a.evidence);dest.mkdir(parents=True,exist_ok=True)
server=HTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium)
 results=[]
 for width in [1062,354]:
  page=browser.new_page(viewport={'width':width,'height':2200},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}')
  with page.expect_response('**/run') as response:page.locator('#run').click()
  data=response.value.json();page.locator('#result[data-done="true"]').wait_for()
  assert data['estimates']['A']==7 and data['exact']['E']==0 and data['table']==[[9,0,2,1],[1,8,3,0],[0,0,7,5]]
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth') and not errors
  file=root/'assets/13-live-demo.png' if width==1062 else dest/'demo-354.png'
  page.locator('main').screenshot(path=str(file))
  results.append({'width':width,'actual_data':data,'pageerrors':errors,'overflow':False})
  page.close()
 browser.close()
server.shutdown();(dest/'capture-result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print('actual button execution and browser capture passed at 1062 and 354')
