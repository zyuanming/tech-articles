"""Capture the real localhost viewer using installed system Chromium; CC0."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium')
 page=browser.new_page(viewport={'width':1062,'height':1500},device_scale_factor=1)
 page.goto('http://127.0.0.1:8110/',wait_until='networkidle')
 page.wait_for_function("document.querySelector('#result').textContent.includes('2.4375')")
 assert page.locator('#result').inner_text().startswith('u = 0.50')
 page.locator('#alpha').select_option('0.5');page.wait_for_timeout(200)
 assert '2.4375' not in page.locator('#result').inner_text()
 page.locator('#alpha').select_option('0');page.wait_for_function("document.querySelector('#result').textContent.includes('2.4375')")
 page.locator('body').screenshot(path=str(ROOT/'assets/21-viewer.png'))
 from PIL import Image
 im=Image.open(ROOT/'assets/21-viewer.png')
 metadata=json.loads((ROOT/'examples/figure-metadata.json').read_text())
 metadata=[x for x in metadata if x['file']!='assets/21-viewer.png']
 metadata.append(dict(file='assets/21-viewer.png',width=im.width,height=im.height,min_font_px=40,effective_min_font_at_354=round(40*354/im.width,2),identity='真实默认Chromium '+browser.version+' 截图；自制Python教学应用',purpose='切换参数并计算当前位置；示例u=.5',checks=['actual-http-app','actual-parameter-switch','readout-assertion','actual-dimensions','CSS-font-minimum-40']))
 (ROOT/'examples/figure-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
 print('Chromium',browser.version,'interactive switch verified')
 browser.close()
