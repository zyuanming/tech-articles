"""Keep the completed ten-article regression and include published continuations."""
LEGACY_COLLECTION = 'student-exploration-2026-10-11'
SERIES_COLLECTION = 'student-exploration-series-2026-10-11'

def exploration_articles(catalog):
    legacy = [a for a in catalog if a.get('collection') == LEGACY_COLLECTION]
    if len(legacy) != 10:
        raise ValueError('The completed ten-article regression must remain intact')
    selected = [a for a in catalog if a.get('collection') in
                (LEGACY_COLLECTION, SERIES_COLLECTION)]
    # This batch is added incrementally: test every published item, not thirty
    # merely planned manuscripts, and never replace the existing ten checks.
    if len(selected) == len(legacy):
        raise ValueError('No published continuation article found')
    ids = [a['id'] for a in selected]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate exploration article IDs')
    return selected
