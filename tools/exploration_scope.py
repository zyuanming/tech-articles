"""Keep the completed ten-article regression and include published continuations."""
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
LEGACY_COLLECTION = 'student-exploration-2026-10-11'
SERIES_COLLECTION = 'student-exploration-series-2026-10-11'
DOOM_COLLECTION = 'doom-from-zero'

def exploration_articles(catalog):
    legacy = [a for a in catalog if a.get('collection') == LEGACY_COLLECTION]
    if len(legacy) != 10:
        raise ValueError('The completed ten-article regression must remain intact')
    selected = [a for a in catalog if a.get('collection') in
                (LEGACY_COLLECTION, SERIES_COLLECTION, DOOM_COLLECTION)]
    # This batch is added incrementally: test every published item, not thirty
    # merely planned manuscripts, and never replace the existing ten checks.
    if len(selected) == len(legacy):
        raise ValueError('No published continuation article found')
    ids = [a['id'] for a in selected]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate exploration article IDs')
    return selected

def supplementary_visuals(root, item):
    """Discover only canonical same-article public files, never external sources."""
    root = Path(root).resolve()
    ident = item['id']
    if not re.fullmatch(r'[A-Za-z0-9_-]+', ident):
        raise ValueError('Unsafe article ID')
    expected = 'articles/' + ident + '/read.md'
    if item['path'] != expected:
        raise ValueError('Noncanonical article path')
    directory = (root / 'articles' / ident).resolve()
    directory.relative_to(root / 'articles')
    body = directory / 'read.md'
    def image_refs(path, require_local=False):
        refs = set()
        for raw in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc:
                if require_local:
                    raise ValueError('Appendix must use local public images')
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            target.relative_to(directory)
            refs.add(target)
        return refs
    used = image_refs(body)
    appendix = directory / 'source-figures.md'
    pages = []
    if appendix.is_file():
        appendix.resolve().relative_to(directory)
        refs = image_refs(appendix, require_local=True)
        if not refs:
            raise ValueError('Source figure appendix has no local images')
        pages.append({'path': appendix.relative_to(root).as_posix(),
                      'images': len(re.findall(r'!\[[^\]]*\]\([^)]+\)', appendix.read_text()))})
        used.update(refs)
    extras = []
    for path in sorted(directory.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in {'.png','.jpg','.jpeg','.gif','.svg','.webp'}:
            continue
        path.resolve().relative_to(directory)
        if path.resolve() not in used:
            extras.append(path.relative_to(root).as_posix())
    return {'pages': pages, 'unembedded_images': extras}

