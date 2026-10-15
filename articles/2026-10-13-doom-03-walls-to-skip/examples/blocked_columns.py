"""A teaching-only screen-column ledger, not Doom's solidsegs implementation.

All public ranges here INCLUDE both ends, e.g. (80, 239).
No game, external package, network, pixel rendering or vertical opening tests.
MIT license: ../licenses/Example-Code-MIT.txt
"""

def visible_columns(candidate, blocked_ranges, width=320):
    first, last = candidate
    if not (0 <= first <= last < width):
        raise ValueError('candidate must be within the numbered screen columns')
    blocked = set()
    for lo, hi in blocked_ranges:
        if not (0 <= lo <= hi < width):
            raise ValueError('blocked range must be within the screen')
        blocked.update(range(lo, hi + 1))
    result = []
    for column in range(first, last + 1):
        if column not in blocked:
            if result and result[-1][1] == column - 1:
                result[-1] = (result[-1][0], column)
            else:
                result.append((column, column))
    return result

if __name__ == '__main__':
    blocked = [(80, 239)]
    for candidate in [(100, 219), (40, 279)]:
        print('Candidate', candidate, 'remaining:', visible_columns(candidate, blocked))
    assert visible_columns((100, 219), blocked) == []
    assert visible_columns((40, 279), blocked) == [(40, 79), (240, 279)]
    assert visible_columns((80, 239), []) == [(80, 239)]
    assert visible_columns((0, 319), [(0, 319)]) == []
    print('These are horizontal bookkeeping examples, not measured game savings.')
