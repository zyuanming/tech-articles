"""Execute UI, verify returned values, capture real Chromium pixels; CC0-1.0."""
from pathlib import Path
import subprocess,sys,json
from playwright.sync_api import sync_playwright
from PIL import Image,PngImagePlugin
ROOT=Path(__file__).resolve().parents[1]
p=subprocess.Popen([sys.executable,str(ROOT/'examples/demo_web.py')],stdout=subprocess.PIPE,text=True)
try:
 url=p.stdout.readline().strip()
 with sync_playwright() as w:
  browser=w.chromium.launch(executable_path='/usr/bin/chromium');page=browser.new_page(viewport={'width':1062,'height':900},device_scale_factor=1)
  page.goto(url);page.locator('#run').click();page.wait_for_function('window.data!==null');page.locator('#mapped').wait_for();page.wait_for_function("document.querySelector('#mapped').complete")
  d=page.evaluate('window.data');assert abs(d['good']-1)<1e-12 and abs(d['wrong']-.64)<1e-12
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  out=ROOT/'assets/15-live-demo.png';page.screenshot(path=str(out),full_page=True)
  im=Image.open(out).convert('RGB');info=PngImagePlugin.PngInfo();info.add(b'sRGB',b'\x00');im.save(out,pnginfo=info)
  page.set_viewport_size({'width':354,'height':800});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  browser.close()
 print('real browser click, values, desktop/mobile overflow: PASS')
finally:p.terminate();p.wait(timeout=10)
