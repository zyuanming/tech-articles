"""Capture a real NumPy call in a local teaching UI. Code CC0-1.0.
Requires optional NumPy, Playwright, Pillow, fontTools, Noto CJK and Chromium.
Logs/browser details remain in the private --evidence-dir, never the public JSON.
"""
from pathlib import Path
from http.server import HTTPServer
import argparse, json, shutil, threading
from PIL import Image
from playwright.sync_api import sync_playwright
from fontTools.ttLib import TTFont
from demo_web import Handler
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--evidence-dir',type=Path,required=True)
    parser.add_argument('--chromium',default=shutil.which('chromium'))
    args=parser.parse_args()
    if not args.chromium:raise RuntimeError('Chromium executable required')
    args.evidence_dir.mkdir(parents=True,exist_ok=True)
    font=next((p for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc'] if Path(p).exists()),None)
    if not font:raise RuntimeError('Noto CJK font required')
    cmap=TTFont(font,fontNumber=0).getBestCmap()
    server=HTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    evidence=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=args.chromium)
            for width in [1062,354]:
                page=browser.new_page(viewport={'width':width,'height':1000},device_scale_factor=1)
                errors=[];failed_responses=[]
                page.on('response',lambda response:failed_responses.append(dict(url=response.url,status=response.status)) if response.status>=400 else None)
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.on('console',lambda msg:errors.append(msg.text) if msg.type=='error' else None)
                url=f'http://127.0.0.1:{server.server_port}'
                page.goto(url);assert page.title()=='NumPy partition 教学实跑'
                assert page.locator('#result').inner_text()=='尚未运行'
                with page.expect_response('**/run') as response:page.locator('#run').click()
                result=response.value.json();page.wait_for_selector('#result[data-done="true"]');page.evaluate('document.fonts.ready')
                assert result['numpy']=='2.4.6',result['numpy']
                assert result['selected']==6 and result['kth']==5 and result['input_unchanged']
                assert result['output']==[1,3,3,3,5,6,7,8,9]
                if errors or failed_responses:
                    (args.evidence_dir/f'failed-responses-{width}.json').write_text(json.dumps(dict(errors=errors,responses=failed_responses),ensure_ascii=False,indent=2)+'\n')
                assert not errors and not failed_responses,(errors,failed_responses)
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                text=page.locator('main').inner_text();assert all(ord(ch) in cmap for ch in text if not ch.isspace())
                boxes=page.locator('h1,p,button,.cell').evaluate_all('els=>els.map(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {x:r.x,y:r.y,w:r.width,h:r.height,text:e.innerText,font:parseFloat(s.fontSize),color:s.color,background:s.backgroundColor}})')
                minimum=min(b['font'] for b in boxes);assert minimum>=40 if width==1062 else minimum>=12
                for i,b in enumerate(boxes):
                    assert b['x']>=0 and b['x']+b['w']<=width+.1 and b['w']>0
                    for q in boxes[i+1:]:
                        assert min(b['x']+b['w'],q['x']+q['w'])<=max(b['x'],q['x'])+.1 or min(b['y']+b['h'],q['y']+q['h'])<=max(b['y'],q['y'])+.1,(b,q)
                destination=ROOT/'assets/11-numpy-live.png' if width==1062 else args.evidence_dir/'11-numpy-mobile-browser.png'
                page.locator('main').screenshot(path=str(destination))
                im=Image.open(destination).convert('L')
                for b in boxes:
                    region=im.crop((int(b['x']),int(b['y']),int(b['x']+b['w']),int(b['y']+b['h'])))
                    low,high=region.getextrema();assert high-low>90
                    assert sum(v<180 for v in region.getdata())>=len(b['text'])*2
                evidence.append(dict(url=url,width=width,browser=browser.version,min_font=minimum,errors=errors,boxes=boxes))
                if width==1062:
                    (ROOT/'examples/numpy-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
                    figure_min=minimum
                page.close()
            browser.close()
    finally:server.shutdown()
    metadata_path=ROOT/'examples/figure-metadata.json'
    meta=[r for r in json.loads(metadata_path.read_text()) if r['file']!='assets/11-numpy-live.png']
    w,h=Image.open(ROOT/'assets/11-numpy-live.png').size
    meta.append(dict(file='assets/11-numpy-live.png',width=w,height=h,min_font_px=figure_min,effective_min_font_at_354=figure_min/3,identity='真实本地原创教学网页截图；点击后实际执行NumPy 2.4.6',purpose='显示同一输入的真实分区结果、指定位置、版本和输入未变',checks=['real-click','response-assertions','browser-overflow','computed-font-size','text-box-overlap','glyph-cmap','contrast','ink-pixels','actual-dimensions']))
    metadata_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    (args.evidence_dir/'browser-checks.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    print('Real NumPy UI: desktop and mobile checks PASS')

if __name__=='__main__':main()
