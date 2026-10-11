"""Offline fail-closed checks for article IDs, frozen bytes and local links."""
from pathlib import Path
import hashlib
import json
import re
from urllib.parse import urlsplit, unquote
ROOT=Path(__file__).resolve().parents[1]

def validate():
    articles=json.loads((ROOT/'catalog.json').read_text())
    if len({a['id'] for a in articles})!=len(articles):raise ValueError('Duplicate article ID')
    for a in articles:
        p=(ROOT/a['path']).resolve()
        if not p.is_relative_to(ROOT/'articles'):raise ValueError('Article outside archive')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=a['public_sha256']:raise ValueError('Article hash mismatch: '+a['id'])
    local_links=0
    for p in (ROOT/'articles').rglob('*'):
        if p.is_symlink():raise ValueError('Symlink refused: '+str(p))
        if p.is_file() and p.suffix=='.md':
            text=p.read_text()
            if re.search(r'(?im)^.*(?:editor-review\.json|reviewer_report\.json|wechat_state\.json|/workspace/|/tmp/|sk-proj-[A-Za-z0-9]).*$',text):raise ValueError('Private artifact marker: '+str(p))
            for url in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
                ref=urlsplit(url.split(' "')[0]);name=unquote(ref.path)
                if ref.scheme or ref.netloc or not name:continue
                dest=(p.parent/name).resolve()
                if not dest.is_relative_to(ROOT) or not dest.is_file():raise ValueError('Broken/local escape link: '+str(p)+' -> '+url)
                local_links+=1
    manifest=ROOT/'assets-manifest.json'
    if manifest.exists():
        for a in json.loads(manifest.read_text()):
            p=ROOT/a['path'];b=p.read_bytes()
            if len(b)!=a['bytes'] or hashlib.sha256(b).hexdigest()!=a['sha256']:raise ValueError('Asset changed: '+a['path'])
    return {'articles':len(articles),'local_links':local_links,'result':'PASS'}
if __name__=='__main__':print(json.dumps(validate()))
