"""Capture actual browser execution, not a drawn interface. CC0-1.0."""
from pathlib import Path
import argparse,threading,json
from playwright.sync_api import sync_playwright
from demo_web import server
p=argparse.ArgumentParser();p.add_argument('--chromium',required=True);p.add_argument('--evidence',required=True);a=p.parse_args()
out=Path(a.evidence);out.mkdir(parents=True,exist_ok=True);root=Path(__file__).resolve().parents[1]
s=server();threading.Thread(target=s.serve_forever,daemon=True).start();records=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=a.chromium)
  for width in [1062,354]:
   page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1)
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{s.server_port}',wait_until='networkidle');page.locator('#run').click();page.wait_for_function('window.result !== undefined');page.evaluate('document.fonts.ready')
   d=page.evaluate('window.result');assert [x['run_count'] for x in d['phases']]==[4,2,1] and d['total_blocks']==72
   assert not errors and not page.evaluate('document.documentElement.scrollWidth>innerWidth')
   page.screenshot(path=str(root/'assets/14-live-demo.png' if width==1062 else out/'demo-354.png'),full_page=True)
   records.append(dict(width=width,n=d['n'],input_bytes=d['input_bytes'],phases=d['phases'],total_blocks=d['total_blocks'],overflow=False,errors=errors))
  browser.close()
finally:s.shutdown()
(out/'capture-result.json').write_text(json.dumps(records,indent=2)+'\n');print('actual file execution and both browser widths: PASS')
