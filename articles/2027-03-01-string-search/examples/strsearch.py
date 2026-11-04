"""字符串搜索的四个算法，全部只依赖标准库。

用到的量：
  comparisons —— 字符比较次数（等于「看了一个字符」的次数）
  windows     —— 尝试过多少个对齐位置
  matches     —— 命中的次数（含重叠）

实现约定：所有函数签名都是 (text, pattern) -> dict，pattern 为空时返回
matches = 0、windows = 0（空模式在正文里单独讨论）。
"""

import bisect

MASK = (1 << 64) - 1


class SplitMix64:
    """Steele–Lea–Flood 的 splitmix64，固定种子可复现。"""

    def __init__(self, seed):
        self.s = seed & MASK

    def next(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & MASK
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
        return z ^ (z >> 31)

    def below(self, n):
        return self.next() % n


def text_corpus():
    """一段自己写的英文，用来当「普通文本」。没有引用任何版权文本。"""
    parts = [
        "A string search routine looks simple until the text gets long. "
        "You put the pattern under the text, compare characters, and slide it "
        "one place to the right when the comparison fails. That is the whole idea, "
        "and it is also where the trouble starts, because sliding by one throws away "
        "everything the failed comparison just told you. ",
        "The pattern itself already contains the answer. If the first four characters "
        "of the pattern are the same as its last four characters, then a partial match "
        "that ends in those four characters can be reused instead of rechecked. "
        "This is the observation behind the failure function, and it turns a "
        "quadratic scan into a linear one. ",
        "Searching backwards gives a different kind of information. When the last "
        "character of the pattern does not appear in the text window at all, the "
        "window can move past that character entirely, which is often further than "
        "a single step. English text has enough distinct letters for this to pay off "
        "handsomely, while a text made of one repeated character gives it nothing. ",
        "The practical lesson is that no single algorithm wins everywhere. "
        "The right choice depends on the alphabet, on the pattern length, and on "
        "whether the input is adversarial. Measuring the three cases separately is "
        "cheaper than arguing about which one is fastest. ",
    ]
    return "".join(parts)


def dna_corpus(n, seed=20270301):
    rng = SplitMix64(seed)
    letters = "ACGT"
    return "".join(letters[rng.below(4)] for _ in range(n))


# ---------------------------------------------------------------- 朴素

def naive_search(text, pattern):
    n, m = len(text), len(pattern)
    comparisons = windows = matches = 0
    positions = []
    trace = []
    if m == 0 or m > n:
        return dict(comparisons=0, windows=0, matches=0, positions=[],
                    trace=[], shifts=[])
    for start in range(n - m + 1):
        windows += 1
        j = 0
        while j < m:
            comparisons += 1
            if text[start + j] != pattern[j]:
                break
            j += 1
        if m <= 64:
            trace.append(dict(start=start, matched=j, fail=(j < m)))
        if j == m:
            matches += 1
            positions.append(start)
    return dict(comparisons=comparisons, windows=windows, matches=matches,
                positions=positions, trace=trace, shifts=[1] * max(0, windows - 1))


# ---------------------------------------------------------------- KMP

def prefix_function(pattern):
    """failure[i] = pattern[:i+1] 的最长真前缀同时也是后缀的长度。"""
    m = len(pattern)
    failure = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and pattern[i] != pattern[k]:
            k = failure[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        failure[i] = k
    return failure


def kmp_search(text, pattern):
    n, m = len(text), len(pattern)
    failure = prefix_function(pattern)
    comparisons = windows = matches = 0
    positions = []
    trace = []
    i = j = 0
    start = 0
    while i < n:
        comparisons += 1
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                matches += 1
                positions.append(i - m)
                if m <= 64:
                    trace.append(dict(start=i - m, matched=m, fail=False))
                windows += 1
                j = failure[m - 1]
        else:
            if m <= 64 and j > 0:
                trace.append(dict(start=i - j, matched=j, fail=True))
            if j == 0:
                i += 1
            else:
                j = failure[j - 1]
            windows += 1
    return dict(comparisons=comparisons, windows=windows, matches=matches,
                positions=positions, trace=trace, failure=failure,
                shifts=[])


# ---------------------------------------------------------------- Boyer–Moore 家族

def last_occurrence(pattern):
    """每个字符出现过的所有下标（升序），坏字符规则要用它找 j 左边最近的一个。"""
    table = {}
    for i, ch in enumerate(pattern):
        table.setdefault(ch, []).append(i)
    return table


def _bad_char_shift(table, ch, j):
    """在位置 j 失配时的坏字符位移。

    只看 pattern[0..j-1] 里有没有 ch：有就把它对到 ch 上，没有就整个跳过这一格。
    """
    occ = bisect.bisect_left(table.get(ch, ()), j) - 1
    if occ < 0:
        return j + 1
    return j - table[ch][occ]


def bmh_search(text, pattern):
    """Boyer–Moore–Horspool：只看窗口最后一个字符建表。"""
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return dict(comparisons=0, windows=0, matches=0, positions=[],
                    trace=[], shifts=[])
    table = {}
    for i in range(m - 1):
        table[pattern[i]] = m - 1 - i
    default = m
    comparisons = windows = matches = 0
    positions = []
    trace = []
    shifts = []
    start = 0
    while start + m <= n:
        windows += 1
        j = m - 1
        while j >= 0:
            comparisons += 1
            if text[start + j] != pattern[j]:
                break
            j -= 1
        if m <= 64:
            trace.append(dict(start=start, matched=m - 1 - j, fail=(j >= 0)))
        if j < 0:
            matches += 1
            positions.append(start)
        step = table.get(text[start + m - 1], default)
        if step <= 0:
            step = 1
        shifts.append(step)
        start += step
    return dict(comparisons=comparisons, windows=windows, matches=matches,
                positions=positions, trace=trace, shifts=shifts, table=table)


def good_suffix_shift(pattern):
    """CLRS 风格的后缀预处理：shift[j] = 在 j 处失配时应右移的距离。"""
    m = len(pattern)
    shift = [0] * (m + 1)
    bpos = [0] * (m + 1)
    i, j = m, m + 1
    bpos[i] = j
    while i > 0:
        while j <= m and pattern[i - 1] != pattern[j - 1]:
            if shift[j] == 0:
                shift[j] = j - i
            j = bpos[j]
        i -= 1
        j -= 1
        bpos[i] = j
    j = bpos[0]
    for i in range(m + 1):
        if shift[i] == 0:
            shift[i] = j
        if i >= j:
            j = bpos[j]
    return shift


def bm_search(text, pattern):
    """完整版 Boyer–Moore：坏字符 + 好后缀。"""
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return dict(comparisons=0, windows=0, matches=0, positions=[],
                    trace=[], shifts=[])
    if m == 1:
        r = naive_search(text, pattern)
        r['shifts'] = [1] * (r['windows'] - 1)
        return r
    gs = good_suffix_shift(pattern)
    table = last_occurrence(pattern)
    comparisons = windows = matches = 0
    positions = []
    trace = []
    shifts = []
    start = 0
    while start + m <= n:
        windows += 1
        j = m - 1
        while j >= 0:
            comparisons += 1
            if text[start + j] != pattern[j]:
                break
            j -= 1
        if m <= 64:
            trace.append(dict(start=start, matched=m - 1 - j, fail=(j >= 0)))
        if j < 0:
            matches += 1
            positions.append(start)
            step = gs[0]
        else:
            step = max(gs[j + 1], _bad_char_shift(table, text[start + j], j))
        if step <= 0:
            step = 1
        shifts.append(step)
        start += step
    return dict(comparisons=comparisons, windows=windows, matches=matches,
                positions=positions, trace=trace, shifts=shifts, table=table,
                good_suffix=gs)


ALGOS = (
    ("naive", naive_search),
    ("kmp", kmp_search),
    ("bmh", bmh_search),
    ("bm", bm_search),
)


def run_all(text, pattern):
    out = {}
    for name, fn in ALGOS:
        r = fn(text, pattern)
        out[name] = dict(comparisons=r["comparisons"], windows=r["windows"],
                         matches=r["matches"], positions=r["positions"])
    return out


# ---------------------------------------------------------------- 自检

def selfcheck(rounds=400, seed=7):
    """随机短串上对比四个算法的命中位置，顺便验证 BM 的位移永不小于 1。"""
    rng = SplitMix64(seed)
    for _ in range(rounds):
        alpha = "ab c"[0:1 + rng.below(3)]
        n = 1 + rng.below(30)
        m = 1 + rng.below(min(6, n))
        text = "".join(alpha[rng.below(len(alpha))] for _ in range(n))
        pattern = "".join(alpha[rng.below(len(alpha))] for _ in range(m))
        base = naive_search(text, pattern)
        for name, fn in ALGOS[1:]:
            r = fn(text, pattern)
            assert r["positions"] == base["positions"], (name, text, pattern,
                                                        r["positions"],
                                                        base["positions"])
            assert r["comparisons"] > 0
            assert all(s >= 1 for s in r["shifts"])
    return True


if __name__ == "__main__":
    print(selfcheck())
