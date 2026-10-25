"""Capture our real, read-only local report; code CC0, screenshot CC BY 4.0.
Run from this directory after: python -m http.server 8133 --bind 127.0.0.1
Requires installed Chromium and Playwright. No browser security overrides.
"""
from pathlib import Path
import argparse,json
from PIL import Image
from fontTools.ttLib import TTFont
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8133/report.html');p.add_argument('--audit-dir',required=True);args=p.parse_args()
out=Path(args.audit_dir);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium')
 page=browser.new_page(viewport={'width':1062,'height':1600},device_scale_factor=1)
 page.goto(args.url);page.wait_for_selector('body[data-ready=true]')
 assert page.locator('#checks').inner_text()=='3200 次一致'
 assert page.locator('tbody tr').count()==3
 assert page.locator('tbody tr').all_text_contents()==['x³−x；[−2,2]33','x³−3x+2；[−3,2]22','x²+1；[−2,2]00']
 result={}
 for w in [1062,354]:
  page.set_viewport_size({'width':w,'height':1600})
  result[str(w)]=page.evaluate('''() => ({width:innerWidth, scroll:document.documentElement.scrollWidth, text:Array.from(document.querySelectorAll('h1,h2,p,th,td,small')).map(e=>({text:e.innerText,size:parseFloat(getComputedStyle(e).fontSize),rect:e.getBoundingClientRect().toJSON()}))})''')
  assert result[str(w)]['scroll']<=w
  for t in result[str(w)]['text']:
   r=t['rect'];assert r['x']>=0 and r['x']+r['width']<=w+0.1
  assert min(t['size'] for t in result[str(w)]['text']) >= (40 if w==1062 else 17)
  page.locator('body').screenshot(path=str(ROOT/'assets/15-live-report.png') if w==1062 else str(out/'report-mobile-browser.png'))
 (out/'report-browser-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 browser.close()
font=next(p for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc'] if Path(p).exists())
cmap=TTFont(font,fontNumber=0).getBestCmap()
for t in result['1062']['text']:
 for ch in t['text']:assert ch.isspace() or ord(ch) in cmap, ch
im=Image.open(ROOT/'assets/15-live-report.png')
assert im.width==1062
assert im.convert('L').getextrema()[0]<80
meta_path=ROOT/'examples/figure-metadata.json'
meta=json.loads(meta_path.read_text());meta=[m for m in meta if m['file']!='assets/15-live-report.png']
meta.append({'file':'assets/15-live-report.png','width':im.width,'height':im.height,'min_font_px':40,'effective_min_font_at_354':13.33,'identity':'默认Chromium localhost真实只读教学报告截图，不是SymPy官方界面','purpose':'实际执行的Fraction/SymPy对照与隔离结果','numeric_geometry':'报告读数直接读取results.json；无数量编码条形','checks':['browser-1062-and-354','document-overflow','text-bounds','font-size','glyph-cmap','PNG-ink','actual-dimensions','actual-output-readings'],'manual_checks_required':['contrast','text-overlap','phone-scale-glyphs']})
meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('Real localhost report captured at 1062 and 354; readings and overflow checked')
