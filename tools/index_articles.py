"""Refresh the catalog after deliberate edits to canonical Markdown files."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re
import markdown
ROOT=Path(__file__).resolve().parents[1]

class _ImageCounter(HTMLParser):
    def __init__(self):
        super().__init__();self.count=0
    def handle_starttag(self,tag,attrs):
        if tag == "img":self.count+=1

def rendered_image_count(text):
    """Use the same Markdown extensions as the reading-site renderer."""
    parser=_ImageCounter()
    parser.feed(markdown.markdown(text,extensions=["extra","toc","sane_lists"]))
    parser.close()
    return parser.count

def refresh(root=ROOT):
    old={a['id']:a for a in json.loads((root/'catalog.json').read_text())} if (root/'catalog.json').exists() else {}
    rows=[]
    for p in sorted((root/'articles').glob('*/read.md')):
        ident=p.parent.name
        if not re.match(r'^\d{4}-\d{2}-\d{2}-.+',ident):raise ValueError('Expected date-slug article ID: '+ident)
        text=p.read_text();r=dict(old.get(ident,{}));r.update(id=ident,title=next(l[2:].strip() for l in text.splitlines() if l.startswith('# ')),date=ident[:10],path=p.relative_to(root).as_posix(),public_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),images=rendered_image_count(text))
        r.setdefault('status','archived_article');r.setdefault('related_versions',[]);rows.append(r)
    (root/'catalog.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    assets=[]
    for p in sorted((root/'articles').rglob('*')):
        # __pycache__ is gitignored, so a fresh clone has none of it. Recording
        # those .pyc files here would make validate_content.py fail on clone --
        # it reads every manifest path back from disk.
        if '__pycache__' in p.parts:
            continue
        if p.is_file() and p.suffix!='.md':
            b=p.read_bytes();assets.append({'path':p.relative_to(root).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    (root/'assets-manifest.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
    return {'articles':len(rows),'assets':len(assets)}

if __name__=="__main__":print(json.dumps(refresh()))

