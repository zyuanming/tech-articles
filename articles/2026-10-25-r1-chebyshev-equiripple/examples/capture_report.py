"""Capture the actually served report with default system Chromium. CC0."""
from pathlib import Path
import argparse,json,threading,http.server,functools
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--audit-dir',required=True);args=p.parse_args();out=Path(args.audit_dir);out.mkdir(parents=True,exist_ok=True)
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT/'examples'))
server=http.server.ThreadingHTTPServer(('127.0.0.1',8155),handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
checks={}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium')
  page=browser.new_page(viewport={'width':1062,'height':1800},device_scale_factor=1)
  page.goto('http://127.0.0.1:8155/report.html');page.wait_for_selector('body[data-ready=true]')
  assert page.locator('tbody tr').all_text_contents()==['10.093750.15625','20.125000.12500','30.125000.12500']
  assert '通过' in page.locator('#certificate').inner_text()
  for w in [1062,354]:
   page.set_viewport_size({'width':w,'height':1800})
   result=page.evaluate('''() => ({width:innerWidth,scroll:document.documentElement.scrollWidth,text:[...document.querySelectorAll('h1,h2,p,th,td,small')].map(e=>({text:e.innerText,size:parseFloat(getComputedStyle(e).fontSize),rect:e.getBoundingClientRect().toJSON()}))})''')
   assert result['scroll']<=w
   for t in result['text']:
    r=t['rect'];assert r['x']>=0 and r['x']+r['width']<=w+.1
    assert t['size']>=(40 if w==1062 else 17)
   checks[str(w)]=result
   page.locator('body').screenshot(path=str(ROOT/'assets/14-live-report.png') if w==1062 else str(out/'report-mobile-browser.png'))
  checks['browser']=browser.version;browser.close()
finally:server.shutdown()
(out/'report-browser-check.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
im=Image.open(ROOT/'assets/14-live-report.png');assert im.width==1062;assert im.convert('L').getextrema()[0]<80
mp=ROOT/'examples/figure-metadata.json';meta=json.loads(mp.read_text());meta=[m for m in meta if m['file']!='assets/14-live-report.png']
meta.append(dict(file='assets/14-live-report.png',width=im.width,height=im.height,min_font_px=40,effective_min_font_at_354=13.33,identity='实际默认Chromium本地只读教学报告截图',purpose='显示真实执行交换迭代、精确复核与版本',numeric_geometry='表格数值直接读取results.json，无数量编码图元',checks=['browser-1062-and-354','font-size','text-bounds','actual-readings','document-overflow','actual-dimensions','ink'],manual_checks_required=['glyphs','contrast','overlap']))
mp.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print('Captured real report at 1062 and 354')
