"""Derive a lightweight reading site from the canonical Markdown articles."""
from __future__ import annotations
import argparse
import html
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit, unquote
import markdown

ROOT = Path(__file__).resolve().parents[1]
CSS = '''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:#252d28;background:#f7f7f2;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.75}a{color:#21664b;text-underline-offset:3px}header,main,footer{max-width:940px;margin:auto;padding:26px 24px}header{border-bottom:1px solid #dce1d8;display:flex;justify-content:space-between;gap:12px;align-items:center}header a{text-decoration:none}header .brand{font-weight:700;letter-spacing:.06em}h1,h2,h3{line-height:1.35;scroll-margin-top:20px}h1{font-size:clamp(28px,4.5vw,44px);margin:22px 0}h2{margin-top:2.2em;font-size:1.45em}p,li{overflow-wrap:anywhere}.intro{font-size:18px;color:#57665a}.eyebrow,.meta{font-size:14px;color:#637466}.article{max-width:820px;background:#fff;border:1px solid #e6e9e0;border-radius:12px;padding:36px 40px;font-size:18px}.article img{display:block;max-width:100%;height:auto;margin:24px auto}.article pre{overflow:auto;background:#eef2eb;padding:20px;border-radius:8px;font-size:14px;line-height:1.6}.article code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.article p code,.article li code{background:#edf2e9;padding:.1em .3em;border-radius:3px}.article table{display:block;max-width:100%;overflow-x:auto;border-collapse:collapse;font-size:16px}.article th,.article td{border:1px solid #dce1d8;padding:8px 12px}.article blockquote{border-left:3px solid #80a992;margin:20px 0;padding:2px 20px;color:#536657}.toc{font-size:15px;background:#f4f7f0;padding:12px 20px;border-radius:8px}.search{display:flex;gap:12px;margin:28px 0}.search input,.search select{font:inherit;padding:12px;border:1px solid #becbbe;border-radius:8px;min-width:0;background:white}.search input{flex:1}.cards{list-style:none;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:16px}.cards li{background:white;border:1px solid #dce1d8;border-radius:10px;padding:22px}.cards h2{font-size:21px;margin:6px 0 14px}.cards a{text-decoration:none}.card-meta{font-size:13px;color:#67766c}.tools{display:flex;flex-wrap:wrap;gap:16px;font-size:14px;margin:22px 0}.notice{border-left:3px solid #b8aa73;background:#fbf8eb;padding:12px 18px;font-size:15px}footer{font-size:13px;color:#607065;border-top:1px solid #dce1d8;margin-top:35px}[hidden]{display:none!important}@media(max-width:620px){header,main,footer{padding:18px 16px}.article{padding:22px 18px;border-radius:0;border-left:0;border-right:0;font-size:17px}.cards{grid-template-columns:1fr}.search{flex-direction:column}.article-page{padding:12px 0}.article h1{font-size:29px}}'''

def shell(title, body, prefix, article=False):
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>'+html.escape(title)+' · 技术文章</title><link rel="stylesheet" href="'+prefix+'site.css"></head><body><header><a class="brand" href="'+prefix+'index.html">技术文章</a><a href="https://github.com/zyuanming/tech-articles">GitHub 存档 ↗</a></header><main'+(' class="article-page"' if article else '')+'>'+body+'</main><footer>原创正文 <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · 第三方图片及引用遵循各自许可。网页为辅助阅读展示。</footer></body></html>'

def render(source, source_path):
    output=markdown.markdown(source,extensions=['extra','toc','sane_lists'],extension_configs={'toc':{'permalink':False}})
    def local_markdown_link(match):
        value=html.unescape(match[1]);ref=urlsplit(value)
        if ref.scheme or ref.netloc or not ref.path.endswith('.md'):
            return match[0]
        target=(source_path.parent/unquote(ref.path)).resolve()
        if not target.is_relative_to(ROOT/'articles') or not target.is_file():
            return match[0]
        from urllib.parse import urlunsplit
        rewritten=urlunsplit(('', '', ref.path[:-3]+'.html', ref.query, ref.fragment))
        return 'href="'+html.escape(rewritten,quote=True)+'"'
    output=re.sub(r'href="([^"]+)"',local_markdown_link,output)
    output=output.replace('<img ', '<img loading="lazy" decoding="async" ')
    return output

def build(output: Path):
    output=output.resolve()
    if output==ROOT or ROOT.is_relative_to(output):raise ValueError('Output must not replace the repository')
    if output.exists() and any(output.iterdir()):raise ValueError('Output must be empty')
    output.mkdir(parents=True,exist_ok=True)
    catalog=json.loads((ROOT/'catalog.json').read_text())
    bypath={a['path']:a for a in catalog}
    for source in (ROOT/'articles').rglob('*'):
        if source.is_symlink():raise ValueError('Symlinks are not published')
        if not source.is_file():continue
        target=output/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
        # Preserve original bytes and dimensions; HTML is a derived sibling.
        shutil.copyfile(source,target)
        if source.suffix=='.md':
            rel=source.relative_to(ROOT).as_posix();entry=bypath.get(rel);text=source.read_text()
            title=next((l[2:] for l in text.splitlines() if l.startswith('# ')),source.stem)
            prefix=os.path.relpath(output,target.parent).replace(os.sep,'/')+'/'
            tools='<div class="tools"><a href="'+source.name+'">Markdown 原文</a><a href="sources.html">图片与来源</a></div>' if entry else ''
            note=''
            if entry and entry.get('status')=='archived_trial':note='<p class="notice">归档试稿 · 写于'+entry['date']+'。版本信息按当时资料保存，示例及实测边界见正文。</p>'
            versions=''
            if entry and entry.get('related_versions'):versions='<p class="meta">同题其他版本：'+ ' · '.join('<a href="../'+v+'/read.html">'+html.escape(next(a['title'] for a in catalog if a['id']==v))+'</a>' for v in entry['related_versions'])+'</p>'
            target.with_suffix('.html').write_text(shell(title,'<article class="article">'+note+tools+render(text,source)+versions+tools+'</article>',prefix,True))
    items=[]
    for a in sorted(catalog,key=lambda a:(a['date'],a['id']),reverse=True):
        items.append('<li data-title="'+html.escape(a['title'].lower(),quote=True)+'" data-date="'+a['date']+'"><div class="card-meta">'+a['date']+(' · 归档试稿' if a['status']=='archived_trial' else '')+'</div><h2><a href="'+a['path'].replace('.md','.html')+'">'+html.escape(a['title'])+'</a></h2><div class="card-meta">'+str(a['images'])+' 幅正文配图'+(' · 有同题版本' if a['related_versions'] else '')+'</div></li>')
    dates=sorted({a['date'] for a in catalog},reverse=True)
    body='<div class="eyebrow">观察 · 理解 · 探索</div><h1>把技术讲清楚，<br>把好奇心留下来。</h1><p class="intro">技术与科学文章的公开阅读存档。每篇保留正文、图片来源与必要的原始素材。</p><p class="meta">'+str(len(catalog))+' 份文章版本 · 微信公众号为主发布渠道 · 同题不同成稿保留关联</p><div class="search"><input id="search" aria-label="搜索标题" type="search" placeholder="搜索文章标题…"><select id="date" aria-label="归档日期"><option value="">全部日期</option>'+''.join('<option>'+d+'</option>' for d in dates)+'</select></div><p id="count" class="meta" aria-live="polite"></p><ul class="cards">'+''.join(items)+'</ul><script src="search.js" defer></script>'
    (output/'index.html').write_text(shell('公开文章存档',body,''));(output/'site.css').write_text(CSS)
    (output/'search.js').write_text("const q=document.querySelector('#search'),d=document.querySelector('#date'),items=[...document.querySelectorAll('.cards li')],c=document.querySelector('#count');function filter(){let n=0;for(const x of items){x.hidden=!(x.dataset.title.includes(q.value.trim().toLowerCase())&&(!d.value||x.dataset.date===d.value));if(!x.hidden)n++}c.textContent='显示 '+n+' 篇';}q.addEventListener('input',filter);d.addEventListener('change',filter);filter();")
    (output/'.nojekyll').touch()
    return {'articles':len(catalog),'files':sum(p.is_file() for p in output.rglob('*'))}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'_site');args=ap.parse_args();print(json.dumps(build(args.output)))
