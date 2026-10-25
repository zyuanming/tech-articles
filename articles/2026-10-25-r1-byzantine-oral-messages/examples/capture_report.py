"""Real localhost teaching report capture. CC0 code; screenshot CC BY 4.0."""
from pathlib import Path
import argparse,json
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8166/report.html');p.add_argument('--audit-dir',required=True);a=p.parse_args()
out=Path(a.audit_dir);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium')
 page=browser.new_page(viewport={'width':1062,'height':1600},device_scale_factor=1)
 page.goto(a.url);page.wait_for_selector('body[data-ready=true]')
 assert page.locator('#exhaust').inner_text()=='四人三值穷举：83 组'
 assert page.locator('#random').inner_text()=='七人独立种子检验：100 组'
 assert page.locator('#counts').inner_text()=='各轮槽数：6 + 30 + 120 = 156'
 assert page.locator('tbody tr').all_text_contents()==['坏CA退 B退 D退9','坏DA进 B进9','C缺报A退 B退 D退9']
 checks={}
 for w in [1062,354]:
  page.set_viewport_size({'width':w,'height':1600})
  checks[str(w)]=page.evaluate('''() => ({width:innerWidth,scroll:document.documentElement.scrollWidth,text:[...document.querySelectorAll('h1,h2,p,td,th,small')].map(e=>({text:e.innerText,size:parseFloat(getComputedStyle(e).fontSize),rect:e.getBoundingClientRect().toJSON()}))})''')
  assert checks[str(w)]['scroll']<=w
  for t in checks[str(w)]['text']:
   r=t['rect'];assert r['x']>=0 and r['x']+r['width']<=w+0.1
   assert t['size']>=(40 if w==1062 else 18)
  page.locator('body').screenshot(path=str(ROOT/'assets/16-live-report.png') if w==1062 else str(out/'report-mobile-browser.png'))
 (out/'report-browser-check.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
 browser.close()
im=Image.open(ROOT/'assets/16-live-report.png');assert im.width==1062
meta_path=ROOT/'examples/figure-metadata.json';meta=json.loads(meta_path.read_text());meta=[m for m in meta if m['file']!='assets/16-live-report.png']
meta.append(dict(file='assets/16-live-report.png',width=im.width,height=im.height,min_font_px=40,effective_min_font_at_354=13.33,identity='默认Chromium实际执行报告截图，原创教学程序，非真实网络实测',purpose='实际主例输出、消息计数、有限测试与越界失败证据',checks=['browser-widths-1062-354','text-bounds','font-size','actual-output','image-dimensions'],numeric_geometry='DOM结果直接读取results.json'))
meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('Real report captured and output assertions passed')
