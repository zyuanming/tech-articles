"""Capture real browser clicks and Python responses. CC0-1.0."""
from pathlib import Path
from http.server import HTTPServer
import argparse,json,shutil,threading
from PIL import Image
from playwright.sync_api import sync_playwright
from fontTools.ttLib import TTFont
from demo_web import Handler
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--evidence-dir',type=Path,required=True);args=p.parse_args();args.evidence_dir.mkdir(parents=True,exist_ok=True)
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';assert Path(font).exists();cmap=TTFont(font,fontNumber=0).getBestCmap()
server=HTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();evidence=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=shutil.which('chromium'))
  for width in [1062,354]:
   page=browser.new_page(viewport={'width':width,'height':1100},device_scale_factor=1);errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('response',lambda r:errors.append(str(r.status)) if r.status>=400 else None)
   page.goto(f'http://127.0.0.1:{server.server_port}')
   assert page.locator('#result').inner_text()=='尚未运行'
   with page.expect_response('**/run') as response:page.locator('#run').click()
   d=response.value.json();page.wait_for_selector('#result[data-done="true"]');page.evaluate('document.fonts.ready')
   expected=json.loads((ROOT/'examples/results.json').read_text());assert d==expected
   assert not errors
   assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
   boxes=page.locator('h1,p,button,th,td').evaluate_all('els=>els.map(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {x:r.x,y:r.y,w:r.width,h:r.height,font:parseFloat(s.fontSize),text:e.innerText}})')
   for i,b in enumerate(boxes):
    assert b['x']>=0 and b['x']+b['w']<=width+.1
    assert b['font']>=(40 if width==1062 else 13)
    assert all(ord(ch) in cmap for ch in b['text'] if not ch.isspace())
    for q in boxes[i+1:]:assert min(b['x']+b['w'],q['x']+q['w'])<=max(b['x'],q['x'])+.1 or min(b['y']+b['h'],q['y']+q['h'])<=max(b['y'],q['y'])+.1,(b,q)
   dest=ROOT/'assets/15-model-live.png' if width==1062 else args.evidence_dir/'model-mobile-browser.png'
   page.locator('main').screenshot(path=str(dest));im=Image.open(dest).convert('L')
   for b in boxes:
    crop=im.crop((b['x'],b['y'],b['x']+b['w'],b['y']+b['h']));low,high=crop.getextrema();assert high-low>90
    assert sum(x<180 for x in crop.getdata())>=len(b['text'])*2
   evidence.append(dict(width=width,browser=browser.version,boxes=boxes,errors=errors));page.close()
  browser.close()
finally:server.shutdown()
path=ROOT/'examples/figure-metadata.json';m=json.loads(path.read_text());m=[e for e in m if e['file']!='assets/15-model-live.png'];im=Image.open(ROOT/'assets/15-model-live.png')
m.append(dict(file='assets/15-model-live.png',width=im.width,height=im.height,min_font_px=42,effective_min_font_at_354=14,identity='本地原创教学网页真实Chromium截图；点击后执行Python Fraction模型',purpose='展示真实可复现输入输出与独立检查，不是tc或网络设备实测',checks=['real-click','response-equals-results','browser-overflow','text-overlap','glyph-cmap','font-size','contrast','ink-pixels']))
path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(args.evidence_dir/'browser-checks.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n');print('Desktop/mobile real browser model checked')
