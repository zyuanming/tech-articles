"""Actual Chromium desktop/mobile checks for generated Pages output in CI."""
from pathlib import Path
import io, json, math, threading
from PIL import Image, ImageStat
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'qa-artifacts';ART.mkdir(exist_ok=True)
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT/'_site')))
threading.Thread(target=server.serve_forever,daemon=True).start()
url='http://127.0.0.1:'+str(server.server_port)
catalog=json.loads((ROOT/'catalog.json').read_text())
mvcc=next(item for item in catalog if item['id']=='2026-10-11-mvcc-snapshots')
expected_mvcc_images=mvcc['images']
assert expected_mvcc_images > 0
results=[]

def decode_images(page):
 page.locator('img').evaluate_all("imgs => imgs.forEach(i => i.loading = 'eager')")
 page.wait_for_function("Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)")
 page.locator('img').evaluate_all("imgs => Promise.all(imgs.map(i => i.decode()))")

def settle_paint(page):
 page.evaluate("async () => { await document.fonts.ready; await new Promise(requestAnimationFrame); await new Promise(requestAnimationFrame); }")

def figure_screenshot(page, label):
 figure=page.locator('img').nth(8)
 figure.evaluate("img => img.scrollIntoView({block:'center',behavior:'instant'})")
 figure.evaluate("img => img.decode()")
 settle_paint(page)
 box=figure.bounding_box()
 assert box and box['width']>0 and box['height']>0
 screenshot=page.screenshot(path=str(ART/(label+'-mvcc-figure.png')),full_page=False)
 pixels=Image.open(io.BytesIO(screenshot)).convert('RGB')
 bounds=(math.ceil(box['x']),math.ceil(box['y']),math.floor(box['x']+box['width']),math.floor(box['y']+box['height']))
 assert 0<=bounds[0]<bounds[2]<=pixels.width and 0<=bounds[1]<bounds[3]<=pixels.height
 figure_pixels=pixels.crop(bounds)
 variation=max(ImageStat.Stat(figure_pixels).stddev)
 assert variation>8, 'The known colored MVCC figure was captured blank'
 figure_pixels.save(ART/(label+'-mvcc-figure-pixels.png'))
 return round(variation,2)

try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch()
  for label,width,height in [('desktop',1440,1000),('mobile',390,844)]:
   page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(url,wait_until='networkidle')
   assert page.locator('.cards li').count()==97
   page.screenshot(path=str(ART/(label+'-home.png')),full_page=False)
   page.locator('#search').fill(mvcc['title'])
   assert page.locator('.cards li:visible').count()==1
   page.locator('.cards li:visible a').click();page.wait_for_load_state('networkidle')
   assert page.locator('h1').inner_text()==mvcc['title']
   # Eagerly load every image for actual decoded pixels, then verify the layout.
   decode_images(page)
   assert page.locator('img').count()==expected_mvcc_images
   overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth')
   assert not overflow
   settle_paint(page)
   page.screenshot(path=str(ART/(label+'-mvcc-top.png')),full_page=False)
   figure_variation=figure_screenshot(page,label)
   page.go_back();page.wait_for_load_state('networkidle');page.locator('#search').fill('')
   page.locator('#date').select_option('2026-10-11')
   assert page.locator('.cards li:visible').count()==23
   page.reload();page.wait_for_load_state('networkidle')
   assert page.locator('.cards li:visible').count()==97
   page.goto(url+'/articles/2026-10-10-raft-shared-log/source-figures.html',wait_until='networkidle')
   assert page.locator('img').count()==16
   decode_images(page)
   assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
   assert not errors,errors
   results.append({'viewport':label,'width':width,'height':height,'status':'PASS','search':'PASS','date_filter':'PASS','back_reload':'PASS','mvcc_images':{'expected':expected_mvcc_images,'status':'PASS'},'figure_pixels_stddev':figure_variation,'raft_16_images':'PASS','page_errors':errors})
   page.close()
  browser.close()
finally:
 server.shutdown()
 (ART/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
