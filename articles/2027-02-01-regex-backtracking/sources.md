# 来源与核对

这篇正文里的每个数字都来自 `examples/results.json`，它由 `examples/run_model.py` 调用 `examples/rxe.py` 现跑得出。下面先列文字与图片来源，再逐图说明数字出自哪一组实验。

## 文字参考

| 内容 | 出处 | 核对方式 |
|---|---|---|
| 2019-07-02 事故的时间线、80% 流量损失、27 分钟、事故规则的原文 | Cloudflare Blog,《Details of the Cloudflare outage on July 2, 2019》,2019-07-02,<https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/> | 抓取正文后核对:13:42 部署、13:45 首个告警、14:00 定位 WAF、14:07 全局关停、14:09 恢复；原文写明 "we had lost 80% of our traffic" 与 "went down for 27 minutes"；规则原文逐字符对照 |
| 回溯与 NFA 的对照、`a?` 那组经典例子、主流语言的选择 | Russ Cox,《Regular Expression Matching Can Be Simple And Fast (but is slow in Java, Perl, PHP, Python, Ruby, ...)》,2007-01,<https://swtch.com/~rsc/regexp/regexp1.html> | 抓取全文，确认标题、时间与文中对反向引用的论证 |
| Thompson 的线性算法 | K. Thompson,《Programming Techniques: Regular expression search algorithm》,CACM 11(6): 419–422,1968-06,DOI `10.1145/363347.363387` | Crossref 按 DOI 查询，核对刊名、卷期、页码与日期 |
| Go 的线性保证 | Go 官方文档，`regexp` 包，<https://pkg.go.dev/regexp> | 原句为 "The regexp implementation provided by this package is guaranteed to run in time linear in the size of the input." |
| Rust 的 O(m·n) 与「不支持环视与反向引用」 | Rust `regex` crate 文档，<https://docs.rs/regex/latest/regex/> | 原句为 "all regex searches in this crate have worst case O(m * n) time complexity"；同页写明 lacks look-around and backreferences，并提醒 m 不可忽略 |
| Python 3.11 起支持原子组与占有量词 | 本机 Python 3.14.7 实测 `re.compile(r'(?>a+)b')` 与 `re.compile(r'a*+b')` 均通过 | 直接验证，不是引用；正文只写「支持」不写具体版本号之外的行为 |

一条排除记录：我曾误以为 Thompson 那篇论文的 DOI 是 `10.1145/362851.362887`,Crossref 查询显示那是 Matula 的《In-and-out conversions》(CACM 11(1): 47–50, 1968-01)，与本文无关，已弃用。

## 图片

| 图 | 身份 | 来源 |
|---|---|---|
| 图 15 | 真实照片(档案照) | Wikimedia Commons,`File:Ken Thompson and Dennis Ritchie--1973.jpg`，公有领域，原始来源为 Jargon File。文件 310×201,19590 字节，未缩放未重压缩 |
| 图 01—图 14、图 16—图 19，以及封面 | 原创教学示意 | 由 `examples/build_figures.py` 用 `figkit.py` 绘制，不含第三方素材 |

图 15 是本文唯一的第三方图片。选它而不是 2019 年那批 CC BY-SA 的照片，理由很实际：公有领域没有署名与传播条件的负担，而且它和 Unix 那段历史直接相关。图注里的「公有领域」不是「署名了就等于可以随便用」的替代品，它是这张图本身的版权状态。

## 每张图里的数字从哪来

| 图 | `results.json` 里的键 | 图里画的是什么 |
|---|---|---|
| 01 | 无(结构图) | `ab*c` 的四个状态与 ε 边 |
| 02 | `catastrophic.rows` | n=6…20 的三种步数，纵轴对数 |
| 03 | `splits.rows` | n=2…14 的切法数 2^(n−1) |
| 04 | `catastrophic.rows` | n=8/12/16/20 三种步数 |
| 05 | `cloudflare.match` | k=0…20 的回溯步数 |
| 06 | `cloudflare.match[−1]`、`cloudflare.fail` | 成功与失败的步数 |
| 07 | `rewrites.cases` | 三种模式 × 三种输入 |
| 08 | `pike_threads['ab*c'].widths` | 每步线程表宽度 |
| 09 | `linear.rows` | n=20…5120 的步数与每字符步数 |
| 10 | `anchor.anchored`、`anchor.unanchored` | 锚定与否的步数 |
| 11 | `memo_trace.visited`、`.states`、`.text_len` | 访问过的 (状态， 位置) 格子 |
| 12 | `pattern_size.rows` | m=1…32 的步数 |
| 13 | `programs` 的五个状态数 | 三种做法的代价与能力(文字部分来自 Cox 2007 与两份引擎文档) |
| 14 | 无(时间线) | 1968 / 2007 / 2010s 三段 |
| 15 | 无 | 1973 年照片 |
| 16 | 无(对照表) | 五个引擎的实现与最坏情况(来自各自文档) |
| 17 | 无(时间线) | 事故时间线(来自 Cloudflare 复盘) |
| 18 | `programs['.*.*=.*']` = 8 个状态 | 事故规则节选与代价 |
| 19 | 无(清单) | 四条做法 |

## 模型做了什么

`examples/rxe.py` 是一个 430 行的正则引擎(编译逻辑、三个执行器、一个步数计数器)，刻意只做一件事：把同一个模式编译成同一份指令表，再用三个执行器跑它，并且**用同一个步数计数器**计量。实验是 `examples/run_model.py` 里的十组：九组测量，一组正确性对拍。

1. `catastrophic` —— `(a+)+b` 对纯 `a` 文本，n=6…20。
2. `alternation` —— `(a|a)*b` 对纯 `a` 文本，n=6…14。
3. `cox` —— n 个 `a?` 接 n 个 `a` 对 n 个 `a`，锚定。
4. `cloudflare` —— `.*.*=.*` 对 `x=` 加 k 个 `x`，以及只有 `x` 的失配输入。
5. `rewrites` —— 贪婪、惰性、改写三种模式 × 三种输入。
6. `linear` —— `.*.*=.*` 对 n 个 `x`，n 到 5 120；回溯只测到 320。
7. `anchor` —— 同一输入下锚定与不锚定。
8. `pattern_size` —— m 个备选分支 × 200 个 `x` 加 `a3`。
9. `splits`、`memo_trace`、`pike_threads` —— 三个小实验：切法枚举、记忆化访问的格子、NFA 每步线程宽度。
10. `crosscheck` —— 15 个模式 × 121 个短文本({a, b, =} 上长度 0–4 的全部串)× 3 个执行器，与 CPython `re.search` 的「匹配 / 不匹配」逐个比对，5 445 次全部一致。只比布尔结果，不比匹配区间，因为 `rxe.py` 不报告区间。

## 模型没做什么

- 不支持反向引用与环视。这是有意的：自动机方案表达不了，正文把这个限制本身当作论点。
- 不支持 Unicode 字符类、位置断言、命名组。`\d \w \s` 与 `\D \W \S` 按 ASCII 处理。
- 没有做真实引擎的优化：没有字面量前缀加速、没有 DFA 缓存、没有惰性 DFA、没有 SIMD。
- 步数是「执行了几条指令」，不是 CPU 周期，也不是纳秒。跨语言、跨实现的绝对速度不能拿这篇的数字换算。
- `linear` 组的回溯只到 n=320。n=1 280 需要 1 055 140 485 步、85 秒，已超出这张表想表达的规模，所以停在这里并写在 `note` 里。

## 可以手算复核的三处

1. `(a+)+b` 在 n 个 `a` 上的步数 = `5·2^(n+1) − 4n − 9`。n=6:640−33=607;n=20:10 485 760−89=10 485 671。n=6…20 的十五个点全部吻合。
2. `(a|a)*b` 的步数 = `5·2^(n+2) − 5n − 15`。n=6:1 280−45=1 235;n=14:327 680−85=327 595。
3. 切法数 = `2^(n−1)`:n=14 时 8 192，与 `splits` 的最后一个点一致。

## 没有做的检查

`VISUAL_REVIEW_NOT_RUN`。这篇成稿的环境里没有可用的图像审阅能力，十九张图与封面只经过 `figkit` 的自动校验(元素不出画布、文字不重叠、字号不低于 38px、颜色必须在调色板里、像素对比度)，没有经过人眼或视觉模型的实际看图。图里有没有「道理都对但读起来别扭」的排版问题，这一轮无法回答。
