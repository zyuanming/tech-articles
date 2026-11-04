"""跑出 results.json。只依赖标准库。"""

import json
import os

import strsearch as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results.json")


def brief(r):
    return dict(comparisons=r["comparisons"], windows=r["windows"],
                matches=r["matches"], positions=r["positions"])


def demo():
    text = "abcabcabd"
    pattern = "abcabd"
    d = dict(text=text, pattern=pattern,
             prefix=S.prefix_function(pattern))
    for name, fn in S.ALGOS:
        r = fn(text, pattern)
        d[name] = dict(brief(r), trace=r["trace"], shifts=r.get("shifts") or [])
    d["bmh_table"] = {k: v for k, v in S.bmh_search(text, pattern)["table"].items()}
    return d


ENGLISH_PATTERNS = [
    ("the", "hit"),
    ("character", "hit"),
    ("string", "hit"),
    ("the quick", "hit"),
    ("quicksilver", "miss"),
    ("aaa", "miss"),
]

DNA_SHORT = 8
DNA_LONG = 16


def english():
    text = S.text_corpus()
    rows = []
    for pattern, kind in ENGLISH_PATTERNS:
        r = S.run_all(text, pattern)
        rows.append(dict(pattern=pattern, kind=kind, m=len(pattern), **r))
    return dict(length=len(text), rows=rows)


def dna():
    text = S.dna_corpus(20000)
    pats = [
        (text[5000:5000 + DNA_SHORT], "hit"),
        (text[12000:12000 + DNA_SHORT], "hit"),
        (text[5000:5000 + DNA_LONG], "hit"),
        ("ACGTACGT", "miss"),
        ("GGGGGGGG", "miss"),
    ]
    rows = []
    for pattern, kind in pats:
        r = S.run_all(text, pattern)
        rows.append(dict(pattern=pattern, kind=kind, m=len(pattern), **r))
    return dict(length=len(text), rows=rows)


def adversarial_a(note):
    """pattern = 'a'*(m-1) + 'b'，text 全是 a：朴素每格比 m 次。"""
    rows = []
    for n in (1000, 2000, 4000, 8000, 16000, 32000, 64000):
        m = max(2, n // 4)
        text = "a" * n
        pattern = "a" * (m - 1) + "b"
        r = S.run_all(text, pattern)
        rows.append(dict(n=n, m=m, note=note, **r))
    return dict(rows=rows)


def adversarial_b(note):
    """pattern = 'b' + 'a'*(m-1)，text 全是 a：BMH 每格比 m 次且只挪一步。"""
    rows = []
    for n in (1000, 2000, 4000, 8000, 16000, 32000, 64000):
        m = max(2, n // 4)
        text = "a" * n
        pattern = "b" + "a" * (m - 1)
        r = S.run_all(text, pattern)
        rows.append(dict(n=n, m=m, note=note, **r))
    return dict(rows=rows)


def shift_hist():
    text = S.text_corpus()
    pattern = "the"
    r = S.bmh_search(text, pattern)
    hist = {}
    for s in r["shifts"]:
        hist[s] = hist.get(s, 0) + 1
    total = sum(d * c for d, c in hist.items())
    return dict(pattern=pattern, counts=sorted(hist.items()),
                windows=r["windows"], comparisons=r["comparisons"],
                mean_shift=total / max(1, r["windows"]),
                max_shift=max(hist) if hist else 0)


def overlap():
    text = "aaaaa"
    pattern = "aa"
    r = S.run_all(text, pattern)
    return dict(text=text, pattern=pattern,
                matches=r["naive"]["matches"],
                positions=r["naive"]["positions"],
                naive=r["naive"], kmp=r["kmp"], bmh=r["bmh"], bm=r["bm"])


def runs_matches():
    """全是一段重复字符的文本：模式全命中时，KMP 每格只比一个字符。"""
    text = "a" * 8000
    rows = []
    for pattern in ("aaaaaaa", "aaaaaaab"):
        r = S.run_all(text, pattern)
        for algo in r:
            r[algo]['positions'] = r[algo]['positions'][:3]
        rows.append(dict(pattern=pattern, n=len(text), **r))
    return dict(rows=rows)


def perwindow():
    en = S.text_corpus()
    dna = S.dna_corpus(20000)
    runs = "a" * 8000
    cases = [
        ("english", en, "the"),
        ("dna", dna, "ACGTACGT"),
        ("runs", runs, "aaaaaaab"),
    ]
    rows = []
    for name, text, pattern in cases:
        r = S.run_all(text, pattern)
        row = dict(corpus=name, pattern=pattern, n=len(text))
        for algo in ("naive", "kmp", "bmh", "bm"):
            row[algo] = dict(
                comparisons=r[algo]["comparisons"],
                windows=r[algo]["windows"],
                per_window=r[algo]["comparisons"] / max(1, r[algo]["windows"]),
            )
        rows.append(row)
    return rows


def utf8():
    text = "naïve café — 中文也在这里，é 和 e 不是一回事。"
    needle = "é"
    raw = text.encode("utf-8")
    nb = needle.encode("utf-8")
    r = S.bmh_search(raw.decode("latin-1"), nb.decode("latin-1"))
    char_positions = [i for i in range(len(text)) if text.startswith(needle, i)]
    return dict(text=text, needle=needle, text_bytes=len(raw), needle_bytes=len(nb),
                byte_matches=r["matches"], byte_positions=r["positions"],
                char_matches=len(char_positions), char_positions=char_positions)


def goodsuffix():
    """BM 在对抗 B 上靠的正是好后缀：坏字符只说挪 1 格，好后缀说挪 8 格。"""
    pattern = "b" + "a" * 7
    table = S.last_occurrence(pattern)
    gs = S.good_suffix_shift(pattern)
    return dict(pattern=pattern, m=len(pattern), good_suffix=gs,
                bad_char_at_0=S._bad_char_shift(table, "a", 0),
                good_suffix_at_0=gs[1],
                occurrence_a=[i for i, c in enumerate(pattern) if c == "a"])


def utf8_invalid():
    """半个汉字当针：字节层能命中，字符层不存在这样的位置。"""
    text = "中文也在这里"
    raw = text.encode("utf-8")
    needle = raw[4:6]          # 第二个「文」的第 2、3 个字节
    latin = raw.decode("latin-1")
    r = S.bmh_search(latin, needle.decode("latin-1"))
    return dict(text=text, text_bytes=len(raw), needle_hex=needle.hex(" "),
                byte_positions=r["positions"], byte_matches=r["matches"],
                char_positions=[],
                note="这个针不是合法 UTF-8，字符层没有任何位置能放它")


def main():
    data = dict(
        demo=demo(),
        english=english(),
        dna=dna(),
        adversarial_a=adversarial_a("pattern = 'a'*(m-1)+'b', text = 'a'*n"),
        adversarial_b=adversarial_b("pattern = 'b'+'a'*(m-1), text = 'a'*n"),
        shift_hist=shift_hist(),
        overlap=overlap(),
        perwindow=perwindow(),
        runs_matches=runs_matches(),
        goodsuffix=goodsuffix(),
        utf8=utf8(),
        utf8_invalid=utf8_invalid(),
        selfcheck=S.selfcheck(),
    )
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("wrote", os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
