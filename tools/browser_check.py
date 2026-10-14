"""Actual Chromium desktop/mobile checks for generated Pages output in CI."""
from pathlib import Path
import io, json, math, threading, os, html, hashlib
from urllib.parse import quote
from PIL import Image, ImageStat
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
from exploration_scope import exploration_articles, supplementary_visuals
from image_decode_diagnostics import NetworkDiagnostics
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'qa-artifacts';ART.mkdir(exist_ok=True)
server=None
url=os.environ.get('ARTICLE_SITE_BASE_URL','').rstrip('/')
if not url:
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT/'_site')))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 url='http://127.0.0.1:'+str(server.server_port)
catalog=json.loads((ROOT/'catalog.json').read_text())
mvcc=next(item for item in catalog if item['id']=='2026-10-11-mvcc-snapshots')
expected_mvcc_images=mvcc['images']
assert expected_mvcc_images > 0
results=[]

def decode_images(page):
 diagnostics.decode_images()

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
   diagnostics=NetworkDiagnostics(page,url,ART/'network-diagnostics.jsonl',label)
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   diagnostics.goto(url,wait_until='networkidle')
   assert page.locator('.cards li').count()==len(catalog)
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
   assert page.locator('.cards li:visible').count()==sum(a['date']=='2026-10-11' for a in catalog)
   page.reload();page.wait_for_load_state('networkidle')
   assert page.locator('.cards li:visible').count()==len(catalog)
   diagnostics.goto(url+'/articles/2026-10-10-raft-shared-log/source-figures.html',wait_until='networkidle')
   assert page.locator('img').count()==16
   decode_images(page)
   assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
   exploration=[]
   expected_exploration=exploration_articles(catalog)
   for item in expected_exploration:
    response=diagnostics.goto(url+'/'+item['path'].replace('.md','.html'),wait_until='networkidle')
    assert response and response.ok,item['id']
    assert page.locator('h1').inner_text()==item['title']
    decode_images(page)
    assert page.locator('img').count()==item['images'],item['id']
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'),item['id']
    settle_paint(page)
    page.screenshot(path=str(ART/(label+'-'+item['id']+'-top.png')),full_page=False)
    middle=page.locator('img').nth(item['images']//2)
    middle.scroll_into_view_if_needed();settle_paint(page)
    middle.screenshot(path=str(ART/(label+'-'+item['id']+'-figure.png')))
    if item['id']=='2026-10-11-cordic-turns-and-shifts':
     assert '**' in page.locator('pre').all_inner_texts()[0]
    # Published source notes, local experiments and audio must resolve too.
    links=page.locator('a[href]').evaluate_all("nodes => nodes.map(a => a.href)")
    for href in set(links):
     if href.startswith(url+'/articles/'+item['id']+'/'):
      linked=diagnostics.get(href)
      assert linked.ok,(item['id'],href,linked.status)
    supplemental=supplementary_visuals(ROOT,item)
    appendix_results=[]
    for appendix in supplemental['pages']:
     response=diagnostics.goto(url+'/'+quote(appendix['path'].replace('.md','.html'),safe='/'),wait_until='networkidle')
     assert response and response.ok,appendix['path']
     decode_images(page)
     assert page.locator('img').count()==appendix['images'],appendix['path']
     assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'),appendix['path']
     for edge,index in [('first',0),('last',appendix['images']-1)]:
      im=page.locator('img').nth(index);im.scroll_into_view_if_needed();settle_paint(page)
      im.screenshot(path=str(ART/(label+'-'+item['id']+'-appendix-'+edge+'.png')))
     appendix_results.append({'path':appendix['path'],'images':appendix['images'],'decoded':'PASS','overflow':'PASS'})
    # Some notes offer downloadable originals rather than embedding all of them.
    # Inspect these actual public image bytes in an explicitly QA-only layout.
    extras=supplemental['unembedded_images']
    if extras:
     for path in extras:
      response=diagnostics.get(url+'/'+quote(path,safe='/'))
      assert response.ok,(path,response.status)
      assert hashlib.sha256(response.body()).digest()==hashlib.sha256((ROOT/path).read_bytes()).digest(),path
     markup='<html><meta charset="utf-8"><body style="margin:0;padding:18px;box-sizing:border-box;overflow-wrap:anywhere"><p>QA-only original-image layout, not a published article page</p>'
     markup+=''.join('<figure style="margin:0 0 24px"><img style="display:block;max-width:100%;height:auto" src="'+html.escape(url+'/'+quote(path,safe='/'),quote=True)+'"><figcaption>'+html.escape(Path(path).name)+'</figcaption></figure>' for path in extras)
     diagnostics.reset()
     page.set_content(markup+'</body></html>',wait_until='networkidle')
     decode_images(page)
     assert page.locator('img').count()==len(extras)
     assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
     for edge,index in [('first',0),('last',len(extras)-1)]:
      im=page.locator('img').nth(index);im.scroll_into_view_if_needed();settle_paint(page)
      im.screenshot(path=str(ART/(label+'-'+item['id']+'-qa-original-'+edge+'.png')))
    exploration.append({'id':item['id'],'images':item['images'],'decoded':'PASS','overflow':'PASS','local_links':'PASS','source_figure_pages':appendix_results,'unembedded_original_images':{'count':len(extras),'paths':extras,'exact_bytes_and_decode':'PASS','layout_identity':'QA_ONLY_NOT_PUBLISHED_PAGE'}})
   assert [a['id'] for a in exploration]==[a['id'] for a in expected_exploration]
   assert not errors,errors
   results.append({'viewport':label,'width':width,'height':height,'status':'PASS','search':'PASS','date_filter':'PASS','back_reload':'PASS','mvcc_images':{'expected':expected_mvcc_images,'status':'PASS'},'figure_pixels_stddev':figure_variation,'raft_16_images':'PASS','page_errors':errors,'new_exploration_articles':exploration,'base_url':url})
   page.close()
  browser.close()
finally:
 if server:server.shutdown()
 (ART/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')

