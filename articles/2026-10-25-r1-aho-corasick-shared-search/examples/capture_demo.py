"""Capture an actual browser click and response. Requires Playwright + Chromium.
Code CC0; original interface screenshot CC BY 4.0. No remote requests.
"""
from pathlib import Path
from http.server import HTTPServer
import threading,json
from PIL import Image
from playwright.sync_api import sync_playwright
from demo_web import Handler
ROOT=Path(__file__).resolve().parents[1]
server=HTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1062,'height':1450},device_scale_factor=1)
    page.goto('http://127.0.0.1:'+str(server.server_port))
    assert page.locator('#result').inner_text()=='尚未运行'
    with page.expect_response('**/run') as resp:page.locator('#run').click()
    result=resp.value.json()
    page.wait_for_selector('#result[data-done="true"]')
    page.evaluate('document.fonts.ready')
    assert result['first']==[] and result['second']==[['she',1,4],['he',2,4],['hers',2,6],['his',6,9]]
    assert result['cases']==8001 and result['splits']==10
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
    minimum=page.locator('main *').evaluate_all('(xs)=>Math.min(...xs.map(x=>parseFloat(getComputedStyle(x).fontSize)))')
    assert minimum>=40
    page.locator('main').screenshot(path=str(ROOT/'assets/13-live-demo.png'))
    result.update(browser=browser.version,viewport_width=1062,min_font_px=minimum)
    browser.close()
server.shutdown()
(ROOT/'examples/demo-capture.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'examples/figure-metadata.json';data=json.loads(p.read_text());data=[x for x in data if x['file']!='assets/13-live-demo.png']
w,h=Image.open(ROOT/'assets/13-live-demo.png').size
data.append(dict(file='assets/13-live-demo.png',width=w,height=h,min_font_px=minimum,effective_min_font_at_354=minimum/3,identity='真实本地教学web界面截图；Playwright点击调用Python实时运算',purpose='同时展示双块输入、四输出和实际测试摘要',checks=['real-click','response-assertions','browser-overflow','computed-font-size','actual-dimensions']))
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
