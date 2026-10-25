"""Actual local browser execution. Code CC0; screenshot CC BY 4.0."""
from http.server import HTTPServer
import json
from pathlib import Path
import shutil
import threading
from PIL import Image
from playwright.sync_api import sync_playwright
from demo_web import Handler
ROOT = Path(__file__).resolve().parents[1]
server = HTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
checks = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=shutil.which('chromium'))
    page = browser.new_page(viewport={'width': 354, 'height': 900}, device_scale_factor=3)
    page.goto('http://127.0.0.1:' + str(server.server_port))
    with page.expect_response('**/run') as response:
        page.locator('#run').click()
    result = response.value.json()
    page.wait_for_function('window.done === true')
    page.evaluate('document.fonts.ready')
    for width in (354, 1062):
        page.set_viewport_size({'width': width, 'height': 1000})
        for mode in ('LT', 'ET'):
            page.select_option('#mode', mode)
            metrics = page.evaluate('''() => ({width:innerWidth,
                scroll:document.documentElement.scrollWidth,
                minFont:Math.min(...Array.from(document.querySelectorAll('main *'))
                .map(x=>parseFloat(getComputedStyle(x).fontSize)))})''')
            assert metrics['scroll'] <= metrics['width']
            assert metrics['minFont'] >= (14 if width == 354 else 40)
            checks.append(dict(mode=mode, **metrics))
    page.set_viewport_size({'width': 354, 'height': 900})
    page.select_option('#mode', 'ET')
    page.locator('main').screenshot(path=str(ROOT/'assets/14-live-demo.png'))
    capture = dict(browser=browser.version, css_width=354, device_scale_factor=3,
                   identity='真实点击后重新执行本地实验的浏览器截图', checks=checks,
                   experiment_environment=result['environment'],
                   lt_second=result['partial'][0]['second_event'],
                   et_second=result['partial'][1]['second_event'])
    browser.close()
server.shutdown()
(ROOT/'examples/demo-capture.json').write_text(json.dumps(capture, ensure_ascii=False, indent=2)+'\n')
p = ROOT/'examples/figure-metadata.json'
meta = [x for x in json.loads(p.read_text()) if x['file'] != 'assets/14-live-demo.png']
w, h = Image.open(ROOT/'assets/14-live-demo.png').size
meta.append(dict(file='assets/14-live-demo.png', width=w, height=h, min_font_px=42,
                 effective_min_font_at_354=14, identity=capture['identity'],
                 purpose='真实操作本地教学界面，查看运行环境及ET逐步结果',
                 checks=['live-response','mobile-desktop','both-modes','overflow','computed-font-size','actual-size']))
p.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(capture,ensure_ascii=False))
