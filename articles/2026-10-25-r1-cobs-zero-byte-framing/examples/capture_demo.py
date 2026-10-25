"""Real browser checks and teaching screenshot. CC0-1.0."""
from pathlib import Path
from http.server import HTTPServer
import argparse,json,shutil,threading
from PIL import Image
from playwright.sync_api import sync_playwright
from fontTools.ttLib import TTFont
from demo_web import Handler,state
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--evidence-dir',type=Path,required=True);a=p.parse_args();a.evidence_dir.mkdir(parents=True,exist_ok=True)
cmap=TTFont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',fontNumber=0).getBestCmap()
server=HTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();evidence=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=shutil.which('chromium'))
  for width in [1062,354]:
   page=browser.new_page(viewport={'width':width,'height':1100},device_scale_factor=1);errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('console',lambda m:errors.append(m.text) if m.type in ['error','warning'] else None)
   page.on('response',lambda r:errors.append(str(r.status)) if r.status>=400 else None)
   url=f'http://127.0.0.1:{server.server_port}/';page.goto(url)
   assert page.url==url and page.title()=='COBS 分段接收实验'
   page.wait_for_selector('body[data-step="0"]')
   for step in range(1,6):
    with page.expect_response('**/run?step=*') as response:page.locator('#next').click()
    d=response.value.json();assert d==state(step)
    page.wait_for_selector(f'body[data-step="{step}"]')
    assert page.locator('#buffer').inner_text()==d['buffer']
    assert page.locator('#packets p').all_inner_texts()==(d['packets'] or ['尚无完整包'])
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
    if step==4:
     page.evaluate('document.fonts.ready')
     boxes=page.locator('h1,p,button').evaluate_all('els=>els.map(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {x:r.x,y:r.y,w:r.width,h:r.height,font:parseFloat(s.fontSize),text:e.innerText}})')
     for i,b in enumerate(boxes):
      assert b['x']>=0 and b['x']+b['w']<=width+.1
      assert b['font']>=(40 if width==1062 else 13)
      assert all(ord(ch) in cmap for ch in b['text'] if not ch.isspace())
      for q in boxes[i+1:]:assert min(b['x']+b['w'],q['x']+q['w'])<=max(b['x'],q['x'])+.1 or min(b['y']+b['h'],q['y']+q['h'])<=max(b['y'],q['y'])+.1
     dest=a.evidence_dir/f'viewer-{width}.png';page.locator('main').screenshot(path=str(dest));im=Image.open(dest).convert('L')
     for b in boxes:
      crop=im.crop((b['x'],b['y'],b['x']+b['w'],b['y']+b['h']));lo,hi=crop.getextrema();assert hi-lo>90
      assert sum(x<180 for x in crop.getdata())>=len(b['text'])*2
     if width==1062:shutil.copyfile(dest,ROOT/'assets/15-live-viewer.png')
   assert page.locator('#next').is_disabled()
   page.locator('#reset').click();page.wait_for_selector('body[data-step="0"]')
   assert page.locator('#packets').inner_text()=='尚无完整包'
   assert not errors
   evidence.append(dict(viewport_width=width,browser=browser.version,url=url,title=page.title(),steps_tested=list(range(6)),reset=True,errors=errors,boxes=boxes));page.close()
  browser.close()
finally:server.shutdown()
path=ROOT/'examples/figure-metadata.json';m=json.loads(path.read_text());m=[e for e in m if e['file']!='assets/15-live-viewer.png'];im=Image.open(ROOT/'assets/15-live-viewer.png')
m.append(dict(file='assets/15-live-viewer.png',width=im.width,height=im.height,min_font_px=42,effective_min_font_at_354=14,identity='原创教学HTTP界面真实Chromium截图；点击执行Python字节接收模型',purpose='第四次read跨越包界，交出主例同时保留下一包01',checks=['real-click','actual-Python-response','page-identity','no-console-errors','desktop-mobile-overflow','text-overlap','glyph-cmap','font-size','contrast','ink-pixels','actual-dimensions']))
path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
(a.evidence_dir/'browser-checks.json').write_text(json.dumps(dict(browser_path='Browser plugin not available; installed Playwright',flow='local viewer -> next chunk five times -> payload only at delimiter -> reset',checks=evidence),ensure_ascii=False,indent=2)+'\n')
print('Real Chromium desktop/mobile clicks, responses, screenshot and reset checked')
