"""Refresh the catalog after deliberate edits to canonical Markdown files."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
old={a['id']:a for a in json.loads((ROOT/'catalog.json').read_text())} if (ROOT/'catalog.json').exists() else {}
rows=[]
for p in sorted((ROOT/'articles').glob('*/read.md')):
    ident=p.parent.name
    if not re.match(r'^\d{4}-\d{2}-\d{2}-.+',ident):raise ValueError('Expected date-slug article ID: '+ident)
    text=p.read_text();r=dict(old.get(ident,{}));r.update(id=ident,title=next(l[2:].strip() for l in text.splitlines() if l.startswith('# ')),date=ident[:10],path=p.relative_to(ROOT).as_posix(),public_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),images=len(re.findall(r'!\[[^\]]*\]\([^)]+\)',text)))
    r.setdefault('status','archived_article');r.setdefault('related_versions',[]);rows.append(r)
(ROOT/'catalog.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
assets=[]
for p in sorted((ROOT/'articles').rglob('*')):
    if p.is_file() and p.suffix!='.md':
        b=p.read_bytes();assets.append({'path':p.relative_to(ROOT).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(ROOT/'assets-manifest.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'articles':len(rows),'assets':len(assets)}))
