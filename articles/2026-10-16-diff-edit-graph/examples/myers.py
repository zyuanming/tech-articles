"""Myers' O(ND) difference algorithm, written from the 1986 paper. MIT.

The edit graph, the D-paths and the greedy snake are all implemented exactly
as described in:

    Eugene W. Myers, "An O(ND) Difference Algorithm and Its Variations",
    Algorithmica 1(2):251-266, 1986.

Two extra pieces live here so the article can check its own claims:
  * `lcs_dp` -- a textbook dynamic-programming LCS, used to confirm that the
    greedy algorithm really does return a shortest edit script;
  * `unified` -- turn an edit script into the familiar unified diff text.
"""
from __future__ import annotations


class Trace:
    """Counters so the article can quote real work, not estimates."""

    def __init__(self):
        self.d_steps = 0          # how many D values the outer loop ran
        self.diagonals = 0        # how many (D, k) cells were visited
        self.snake_pixels = 0     # how many diagonal edges were consumed
        self.comparisons = 0      # how many element comparisons were made


def _eq(a, b, tr):
    tr.comparisons += 1
    return a == b


def lcs_dp(a, b):
    """Textbook O(NM) longest common subsequence length, for verification."""
    n, m = len(a), len(b)
    prev = [0] * (m + 1)
    for i in range(n - 1, -1, -1):
        cur = [0] * (m + 1)
        for j in range(m - 1, -1, -1):
            if a[i] == b[j]:
                cur[j] = prev[j + 1] + 1
            else:
                cur[j] = prev[j] if prev[j] >= cur[j + 1] else cur[j + 1]
        prev = cur
    return prev[0]


def shortest_edit_length(a, b):
    """D = N + M - 2L, the length of a shortest edit script."""
    return len(a) + len(b) - 2 * lcs_dp(a, b)


def myers(a, b, trace=None):
    """Greedy O(ND) shortest edit script.

    Returns a list of ('=', i, j) / ('-', i, None) / ('+', None, j) tuples.
    """
    tr = trace or Trace()
    n, m = len(a), len(b)
    max_d = n + m
    offset = max_d
    v = [0] * (2 * max_d + 2)
    history = []
    for d in range(max_d + 1):
        tr.d_steps += 1
        history.append(list(v))
        for k in range(-d, d + 1, 2):
            tr.diagonals += 1
            if k == -d or (k != d and v[offset + k - 1] < v[offset + k + 1]):
                x = v[offset + k + 1]          # step down: insert b[y]
            else:
                x = v[offset + k - 1] + 1      # step right: delete a[x]
            y = x - k
            while x < n and y < m and _eq(a[x], b[y], tr):
                x += 1
                y += 1
                tr.snake_pixels += 1
            v[offset + k] = x
            if x >= n and y >= m:
                return _backtrack(a, b, history, d, offset, trace or tr)
    raise AssertionError('unreachable')


def _backtrack(a, b, history, d_final, offset, tr):
    """Walk the recorded D-paths backwards to recover the edit script."""
    n, m = len(a), len(b)
    x, y = n, m
    script = []
    for d in range(d_final, 0, -1):
        v = history[d]
        k = x - y
        if k == -d or (k != d and v[offset + k - 1] < v[offset + k + 1]):
            prev_k = k + 1
        else:
            prev_k = k - 1
        prev_x = v[offset + prev_k]
        prev_y = prev_x - prev_k
        while x > prev_x and y > prev_y:
            script.append(('=', x - 1, y - 1))
            x -= 1
            y -= 1
        if d > 0:
            if x == prev_x:
                script.append(('+', None, y - 1))
                y -= 1
            else:
                script.append(('-', x - 1, None))
                x -= 1
    while x > 0 and y > 0:
        script.append(('=', x - 1, y - 1))
        x -= 1
        y -= 1
    while x > 0:
        script.append(('-', x - 1, None))
        x -= 1
    while y > 0:
        script.append(('+', None, y - 1))
        y -= 1
    script.reverse()
    return script


def apply_script(a, b, script):
    """Rebuild b from a plus the script -- a check that the script is honest."""
    out = []
    for op, i, j in script:
        if op == '=':
            assert a[i] == b[j], (i, j)
            out.append(a[i])
        elif op == '-':
            assert a[i] not in (None,)
        else:
            out.append(b[j])
    return out


def counts(script):
    return (sum(1 for s in script if s[0] == '='),
            sum(1 for s in script if s[0] == '-'),
            sum(1 for s in script if s[0] == '+'))


def unified(a, b, script, name_a='a', name_b='b', context=3):
    """Render an edit script as unified diff text."""
    lines = []
    ops = []
    for op, i, j in script:
        if op == '=':
            ops.append((' ', a[i]))
        elif op == '-':
            ops.append(('-', a[i]))
        else:
            ops.append(('+', b[j]))
    changed = [n for n, (t, _) in enumerate(ops) if t != ' ']
    if not changed:
        return ''
    groups = []
    start = changed[0]
    last = changed[0]
    for n in changed[1:]:
        if n - last > 2 * context:
            groups.append((start, last))
            start = n
        last = n
    groups.append((start, last))
    lines.append('--- %s' % name_a)
    lines.append('+++ %s' % name_b)
    for lo, hi in groups:
        s = max(0, lo - context)
        e = min(len(ops), hi + context + 1)
        old_count = sum(1 for t, _ in ops[s:e] if t in ' -')
        new_count = sum(1 for t, _ in ops[s:e] if t in ' +')
        old_start = sum(1 for t, _ in ops[:s] if t in ' -') + 1
        new_start = sum(1 for t, _ in ops[:s] if t in ' +') + 1
        lines.append('@@ -%d,%d +%d,%d @@' % (old_start, old_count,
                                              new_start, new_count))
        for t, text in ops[s:e]:
            lines.append(t + text)
    return '\n'.join(lines)
