# 来源与说明

## 图片

13 张正文图与 `cover.png` 全部是本文原创的教学示意，由 `examples/build_figures.py` 生成。几何断言写在 `examples/figkit.py` 里：文字不出画布、不互相压、任何字号的文字换算到 354 px 宽的显示宽度后不小于 12 px。没有使用照片、截图或第三方素材，因此不涉及第三方署名与许可。

图里的文本、字节、位移都来自 `examples/results.json`；`build_figures.py` 只负责取值和摆放，不改数。

## 数字

正文和图片里的每个数字都由 `examples/strsearch.py` 算出、`examples/run_model.py` 写进 `examples/results.json`，`examples/build_figures.py` 只从 `results.json` 取值。跑一遍：

```sh
cd examples && python3 run_model.py && python3 build_figures.py
```

纯标准库（画图需要 Pillow），`run_model.py` 约 110 秒，`build_figures.py` 约 3.8 秒。慢的那一段是对抗输入 A：朴素匹配在 n = 64000 时要真比 7.68 亿次。

模型设定：

- **计数的定义**：所有算法都数「字符与字符比了几次」，不数下标算术、表查询、函数调用。朴素、BMH、BM 的「窗口数」是一次对齐尝试；KMP 没有对齐尝试这回事，`results.json` 里它的 `windows` 记的是「失配或命中的次数」，正文里统一叫推进次数，并在第六节的表头写明。
- **语料 1，小例子**：`text = abcabcabd`、`pattern = abcabd`。四个算法的 trace 都写进 `results.json`，正文的 6、1、1、6 与 6、4 直接对应 trace 里的 `matched`。
- **语料 2，英文**：1288 个字符，是本文自己写的一段介绍字符串搜索的英文，不是引文。六个模式：`the`、`character`、`string`、`the quick`、`quicksilver`、`aaa`；前四个命中，后两个不命中。
- **语料 3，DNA**：20000 个字符，字符集 `ACGT`，由 SplitMix64（种子 20270301）生成，不是真实基因组。
- **语料 4，全 a**：8000 个 `a`，模式 `aaaaaaa`（全命中，7994 次）与 `aaaaaaab`（不命中）。
- **对抗输入**：n ∈ {1000, 2000, 4000, 8000, 16000, 32000, 64000}，m = n/4。A 是 `a`×(m−1) + `b`，B 是 `b` + `a`×(m−1)。
- **UTF-8**：32 个字符的文本 `naïve café — 中文也在这里，é 和 e 不是一回事。`，在字符层与字节层各搜一次 `é`（字节 `c3 a9`）；另有一组用非法针 `96 87`（「文」的第 2、3 字节）搜 `中文也在这里`。
- **好后缀表**：模式 `baaaaaaa`（m = 8），按 CLRS 第 32 章的强好后缀定义算 `good_suffix_shift`，结果 `[8,8,1,2,3,4,5,6,7]`。同一模式在下标 0 失配时，坏字符规则给 1 格、好后缀规则给 8 格。
- **BM 的实现**：坏字符规则 + 强好后缀规则，取两者较大值；m = 1 时直接退回朴素；位移小于 1 时按 1 处理。
- **自检**：`selfcheck()` 用 400 组随机短串（固定种子）把四个算法的命中位置互相对拍，任何不一致都会抛异常。`results.json` 里的 `selfcheck: true` 就是这一步。

关键数字的来历：

- **14 / 10 / 7 / 7**：小例子上朴素、KMP、BMH、BM 的比较次数。
- **1445 / 1384 / 551 / 551**：英文里搜 `the` 的比较次数。**1225** 是 KMP 的推进次数，**461** 是 BMH 的窗口数。
- **2.7939 / 3**：BMH 在 `the` 上的平均位移与最大位移。394 次挪满 3 格，除以 461 得 0.855。
- **26542 / 24953 / 5925 / 4530**：DNA 里搜 `CTTATTTT` 的四组比较次数；长度 16 那一行是 **8738 / 6445**（BMH / BM）。
- **187750 → 768016000**：对抗输入 A 上朴素匹配在 n = 1000 与 64000 时的比较次数，符合 3n²/16 的手算式。
- **112001 / 48001**：同一输入上 KMP 与 BMH 的比较次数，n 涨 64 倍它们只涨 64 倍。
- **55958 / 8000**：8000 个 a、模式 `aaaaaaa` 时朴素与 KMP 的比较次数。
- **15993**：同一文本、模式 `aaaaaaab` 时 KMP 的比较次数，2n = 16000 略高一点。
- **9 和 20 / 10 和 38**：`é` 在 32 字符文本里的字符偏移与字节偏移。

## 文献与源码

算法出处，按 DOI 核过卷期页码：

- Knuth, Morris, Pratt, *Fast Pattern Matching in Strings*, SIAM Journal on Computing 6(2):323–350, 1977，DOI `10.1137/0206024`。
- Boyer, Moore, *A fast string searching algorithm*, Communications of the ACM 20(10):762–772, 1977，DOI `10.1145/359842.359859`。
- Horspool, *Practical fast searching in strings*, Software: Practice and Experience 10(6):501–506, 1980，DOI `10.1002/spe.4380100608`。BMH 就是这篇。
- Crochemore, Perrin, *Two-way string-matching*, Journal of the ACM 38(3):650–674, 1991，DOI `10.1145/116825.116845`。
- Cole, *Tight bounds on the complexity of the Boyer–Moore string matching algorithm*, SIAM Journal on Computing 23(5):1075–1091, 1994，DOI `10.1137/s0097539791195543`。正文里「线性性的证明后来被重做过」指的是这条线。
- Guibas, Odlyzko, *On improving the worst case running time of the Boyer–Moore string matching algorithm*, Communications of the ACM 22(9):505–508, 1979，DOI `10.1145/359146.359148`。
- Cormen, Leiserson, Rivest, Stein,《算法导论》第 32 章，好后缀表的定义与预处理按这一章的写法实现。
- RFC 3629（UTF-8 的字节结构：ASCII 单字节、`C2`–`F4` 前导字节、`80`–`BF` 续字节）。

源码，本次抓取后逐行读过：

- glibc `string/strstr.c`（抓取时 HEAD 版本）。分支顺序是：针长 1 走 `strchr`；2、3 走把 2/3 个字符打包成整数的特判；4 到 256 走改良 Horspool，源码注释原文是「Small needles up to size 3 use a dedicated linear search. Longer needles up to size 256 use a novel modified Horspool algorithm.」「By limiting the needle length to 256, the shift table can be reduced to 8 bits per entry」；超过 256 走 `two_way_long_needle`。正文第九节的那张表就是从这段注释和对应分支整理的。
- Rust `library/core/src/str/pattern.rs`。`TwoWaySearcher` 的注释写明出处「Crochemore, M., Perrin, D., 1991, Two-way string-matching, Journal of the ACM 38(3):651-675」，并指向 Crochemore 与 Rytter 的《Text Algorithms》第 13 章第 323 页的 Algorithm CP。注意：注释里的页码 651–675 与 Crossref 记录 650–674 差一页，本文按 Crossref 的 650–674 写。

## 明确没有做的事

- **没有计时**。全文没有任何毫秒数。比较次数少不等于墙钟快——真实实现被 SIMD、缓存、分支预测主导，Python 模型给不出这个答案。
- **没有测 libc 或标准库的速度**。第九节只描述源码里的分支与注释，没有跑 `strstr` 的基准。
- **没有覆盖多字节编码**。只有 UTF-8；GBK、UTF-16、Shift-JIS 的字节结构与边界问题都没碰。
- **没有做归一化实验**。`é` 的两种写法（U+00E9 与 `e` + U+0301）只在正文里作为提醒出现，没有实际搜索对比。
- **没有证明 2n 上界**。正文给的是「每次比较要么推进 i、要么回退 j」的直观论证，加上模型里 15993 这个实测数。
- **KMP 的「窗口数」不是窗口数**。见上文「计数的定义」，这是本文口径里唯一需要读者记住的换算。

## AI 辅助说明

正文与代码由 AI 助手（Claude）在同一轮会话里写出来，审读也是同一个助手做的，独立性有限。所有数字都能用 `run_model.py` 重跑得到；所有源码引用都是实际抓下来读过的，抓不到、读不出正文的来源没有引用。
