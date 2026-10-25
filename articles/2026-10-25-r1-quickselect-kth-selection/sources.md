# 来源、事实范围与素材权利

核验日期：2026-10-25。正文是面向初学者的独立解释，不是论文译文。本文的数组、逐轮主元路径、图形构图、代码和有限范围计数实验均为本篇制作；自设整数没有真实设备测量的身份。

## 已访问并用于核验的来源

1. **Carnegie Mellon University，15-451/651，Lecture 1: Introduction and Linear-time Selection（2023-01-17 修订）**  
   https://www.cs.cmu.edu/~15451-s23/lectures/lec01-selection.pdf  
   实际打开了可提取文本的九页讲义，重点核对第 3 节：选择只继续一侧、右侧序号扣除、随机主元和期望线性。它是课程讲义，不是最初发表论文；该节先假设互异元素。本文三路分区、重复值编号论证、访问计数口径和全部小例另行展开；不把讲义的比较次数常数直接当作本代码耗时。无原文长段引用，无讲义图像转载。

2. **Manuel Blum, Robert W. Floyd, Vaughan Pratt, Ronald L. Rivest, Robert E. Tarjan，*Time Bounds for Selection*，Journal of Computer and System Sciences 7，448–461（1973）**  
   作者公开的原论文 PDF：https://people.csail.mit.edu/rivest/pubs/BFPRT73.pdf  
   DOI：https://doi.org/10.1016/S0022-0000(73)80033-9  
   实际打开并核对首页摘要、引言和第 2 节 PICK 算法及线性保证。支撑的正文事实仅为“存在确定性最坏线性选择算法”；不声称本文实现了 PICK，不复述优化版全部证明，也不把文中的历史转述作为本文独立考证的历史事实。未转载其图、公式排版或扫描页面。

3. **NumPy 2.4 官方文档，`numpy.partition`**  
   https://numpy.org/doc/2.4/reference/generated/numpy.partition.html  
   实际打开并核对 Parameters、返回值、Notes 和 Examples。支撑零起始 `kth`、指定位置的排序值、两侧内部顺序未定义、返回副本，以及该版文档给 `introselect` 列出的最坏 O(n) 保证。本文没有运行 NumPy，也不由这个文档推断所有语言库的选择算法实现。文档说明中的“相等值位置”不作严格一侧的独占承诺；实际示例也允许相等值出现在两侧。本文自己的三路分区则显式集中全部等值项。

## 检索但不能据此声称全文已读

- Hoare 的 *Algorithm 65: Find*，ACM DOI https://dl.acm.org/doi/10.1145/366622.366647 ：打开工具返回 403；未绕过，没有基于全文做历史叙述或实现复刻。
- Princeton 教材网页 https://algs4.cs.princeton.edu/23quicksort/ ：打开返回 403，未作为正文事实来源。
- Hoare 的 *Proof of a Program: FIND* 教学存档 https://web.eecs.umich.edu/~weimerw/2017-590/reading/HoareFind.pdf ：打开返回 502，未据搜索摘要声称读到全文。
- 搜索出现的百科、博客和问答仅作检索线索，未作为技术事实依据。未下载、复制受限原图。

## 本文复算与事实边界

- `examples/selection.py` 的教学函数采用三个新列表，非原地交换。值域约定为 Python 整数；类型检查刻意拒绝布尔、浮点和 NaN。复杂度以元素比较为单位成本，列表追加取摊还常数成本。
- 主线输入 `[8,3,7,3,9,1,6,3,5]`，k=6；指定主元 5、7、6，访问项数为 9+4+1=14，答案 6。排序核验行保留所有重复出现。
- 所有长度 1..7、值域 {-1,0,1} 的数组及其全部合法排名，共 21,324 次核对；另有 500 组随机输入与错误输入检查。执行环境 Python 3.12.14；详细范围随 `results.json` 给出。
- 16 项工作量对照：理想指定主元的分区访问共 27 次；连续最小主元共 136 次。理想路径的主元由排序构造，图和正文都明确排除该排序成本，不能冒称整套算法只做了这些工作。
- 随机实验输入为 0..n-1，n 为 64、128、256、512、1024，k=n//2；每种长度使用种子 0..199。统计对象是分区访问项数，不是时间、精确比较次数或生产库性能。均值不是理论保证。
- 保存全部中间状态的 `trace` 是教学插桩；它与只保留当前状态的正式函数具有不同的历史存储开销，不能混用空间结论。
- 没有对库性能作实测、没有发布到公众号、没有用图像制造真实设备或历史材料的身份。

## 原创图清单与权利

全部图由 `examples/build_figures.py` 生成，模型数值读自 `examples/results.json`。制图基础 Canvas API 参考本库 r1 Aho–Corasick 篇的 CC0 代码，本篇全部图形构图、图中文字与数据为新制，没有复制该篇 PNG。图中的实际对象是数组、排名、执行结果与算法工作量，本题不需要用设备照片或人物图代替它们。

| 文件 | 新增理解作用 | 身份与许可 |
|---|---|---|
| `assets/00-cover.png` | 独立封面：候选列表收缩但目标值保持 | 原创教学示意，CC BY 4.0 |
| `assets/01-rank.png` | 分清输入位置、排序序号和零起始索引 | 原创教学示意，CC BY 4.0 |
| `assets/02-partition.png` | 看见三组内容与组内无序 | 原创模型输出示意，CC BY 4.0 |
| `assets/03-shrink.png` | 逐轮跟踪局部排名和右侧扣除 | 原创模型输出示意，CC BY 4.0 |
| `assets/04-duplicates.png` | 等值段占多个名次与全相等反例 | 原创模型输出示意，CC BY 4.0 |
| `assets/05-memory.png` | 看见新列表与当前列表并存的空间成本 | 原创实现示意，CC BY 4.0 |
| `assets/06-work.png` | 共尺度逐轮扫描条展示两种累计增长 | 原创模型输出图，CC BY 4.0 |
| `assets/07-random-pivot.png` | 用名次集合解释好主元的概率 | 原创数学示意，CC BY 4.0 |
| `assets/08-topk.png` | 阈值不等于精确名单，重复项需要补足规则 | 原创模型输出示意，CC BY 4.0 |

图宽 1062 像素，关键字号不低于 40 像素；按 354 像素宽显示的有效最小字号为 13.33 像素。准确尺寸、用途与程序检查项在 `examples/figure-metadata.json`。程序的几何与像素检查不代替独立内容审读。

## AI 辅助、署名与许可

本篇实际使用 Codex AI 辅助完成研究检索、结构设计、中文草拟、代码与原创图脚本编写、数值复算和作者自检。没有把 AI 生成描述冒称作者现场采访、亲历历史或真实设备测量。未声称受限全文已经读到，未由作者冒充独立审读者给出审读通过结论。

本仓库由 zyuanming 发布。本文原创正文、原创图与原创示意数据采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；建议署名为“zyuanming，tech-articles，《只想知道第六小，为什么要把所有数排好？Quickselect 的分区选择》”，附原文与许可链接，改编时标注改动。`examples/*.py` 原创教学代码采用 [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)。第三方论文、文档、字体软件与商标不因引用而获得本篇再授权；本篇不分发第三方论文或字体文件。
