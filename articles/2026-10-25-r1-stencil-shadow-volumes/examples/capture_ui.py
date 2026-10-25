"""Optional real Chromium capture of the local viewer. Code CC0-1.0."""
from pathlib import Path
import argparse,subprocess,sys,time,urllib.request
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--chromium',required=True);p.add_argument('--port',type=int,default=8879);a=p.parse_args()
 server=subprocess.Popen([sys.executable,str(ROOT/'examples/ui.py'),'--port',str(a.port)])
 try:
  url=f'http://127.0.0.1:{a.port}/'
  for _ in range(100):
   try:
    urllib.request.urlopen(url,timeout=1).close();break
   except ConnectionError:time.sleep(.05)
   except urllib.error.URLError:time.sleep(.05)
  else:raise RuntimeError('local viewer not ready')
  with sync_playwright() as p:
   b=p.chromium.launch(executable_path=a.chromium)
   page=b.new_page(viewport={'width':1062,'height':1200},device_scale_factor=1)
   page.goto(url,wait_until='networkidle')
   assert page.locator('#stats').inner_text()=='有效点 18392；z-fail 错 0\nz-pass 错 18392'
   assert page.locator('body').evaluate('e=>getComputedStyle(e).fontSize')=='42px'
   page.select_option('#mode','outside');assert '15286' in page.locator('#stats').inner_text()
   page.select_option('#mode','other-light');assert 'z-pass 错 0' in page.locator('#stats').inner_text()
   page.select_option('#mode','inside');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   page.screenshot(path=str(ROOT/'assets/17-live-ui.png'),full_page=True)
   b.close()
 finally:server.terminate();server.wait(timeout=10)
if __name__=='__main__':main()
