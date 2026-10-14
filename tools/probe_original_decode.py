"""One fresh Chromium process, one unchanged original, one decode attempt."""
import hashlib, importlib.metadata, json, os, threading
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa-original-probe'; OUT.mkdir(exist_ok=True)
REL='articles/2026-10-14-jacquard-cards-weave/originals/getty-107VAW-double-jacquard-1851.jpg'
EXPECTED='da39ad71a0746a34262b75587ec8bf20a215cc8c2579b1d20486de972f695089'
data=(ROOT/REL).read_bytes()
report={'playwright':importlib.metadata.version('playwright'),'path':REL,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'decode_attempts':0,'fresh_browser':True}
assert report['sha256']==EXPECTED
for key,path in [('meminfo','/proc/meminfo'),('cgroup_memory_max','/sys/fs/cgroup/memory.max'),('cgroup_memory_current','/sys/fs/cgroup/memory.current')]:
 try:report[key]=Path(path).read_text()
 except OSError as e:report[key]={'unavailable':str(e)}
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
failed=False
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch()
  report['browser_version']=browser.version
  cdp=browser.new_browser_cdp_session()
  for method in ['Browser.getVersion','Browser.getBrowserCommandLine','SystemInfo.getInfo']:
   try:report[method]=cdp.send(method)
   except Exception as e:report[method]={'unavailable':str(e)}
  page=browser.new_page(viewport={'width':1280,'height':900},device_scale_factor=1)
  target=f'http://127.0.0.1:{server.server_port}/{REL}'
  try:
   response=page.request.get(target); report['http_status']=response.status
   assert response.ok
   assert hashlib.sha256(response.body()).hexdigest()==EXPECTED
   page.set_content('<html><body style="margin:0;padding:18px;box-sizing:border-box"><img style="display:block;max-width:100%;height:auto" src="'+target+'"></body></html>',wait_until='networkidle')
   page.wait_for_function('Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)')
   report['before_decode']=page.locator('img').evaluate_all('imgs=>imgs.map(i=>({src:i.currentSrc,complete:i.complete,w:i.naturalWidth,h:i.naturalHeight}))')
   report['decode_attempts']=1
   page.locator('img').evaluate_all('imgs=>Promise.all(imgs.map(i=>i.decode()))')
   report['decode']='PASS'
  except Exception as e:
   failed=True; report['decode']='FAIL';report['error']=str(e)
  try:
   page.screenshot(path=str(OUT/'getty-original.png'))
   report['screenshot']='captured; distinct from decode status'
  except Exception as e:report['screenshot_error']=str(e)
  browser.close()
finally:
 server.shutdown()
 (OUT/'result.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report.get(k) for k in ['browser_version','playwright','sha256','bytes','decode_attempts','decode','error']}))
if failed:raise SystemExit(1)
