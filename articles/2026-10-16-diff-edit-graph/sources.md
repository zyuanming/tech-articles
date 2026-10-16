# 来源、图像身份与 AI 辅助说明

核查日期：2026-10-16。正文为面向学生的原创机制讲解。文中全部编辑距离、对角线条数、比较次数、耗时与 diff 输出，均由本文作者实际运行本仓库的实现在真实文件修订上得到；经典教学示例是本文构造的 C 代码片段，不是任何论文的原始数据。

## 一手来源及支持范围

1. Eugene W. Myers，*An O(ND) Difference Algorithm and Its Variations*，Algorithmica 1(2):251–266，1986。本文的编辑图、D 路径、贪心与 snake、回溯、O(ND) 复杂度，以及"基本 O(ND) 算法成为 Unix diff 新实现的基础、通常比当时基于 Hunt–Szymanski 的版本快两到四倍"这一表述，均出自该论文。论文同时说明：当 D 很大时（例如两个完全不同的文件），Hunt–Szymanski 的方法更优——正文第 7 节如实引用了这一点，没有把它说成 Myers 全面更优。
2. J. W. Hunt、M. D. McIlroy，*An Algorithm for Differential File Comparison*，Bell Laboratories Computing Science Technical Report #41。本文核对的是扫描并 OCR 整理的公开版本，报告本身标注 1976 年 7 月；Myers 1986 年论文的参考文献把它引作 1975 年。正文同时给出这两个年份，没有单方面选一个当定论。报告的摘要支持"diff 报告两个文件的差异、表示为最小的行改动列表""在典型输入上时间与空间开销大致随文件长度之和变化""核心算法求解最长公共子序列问题"等表述。
3. J. W. Hunt、T. G. Szymanski，*A Fast Algorithm for Computing Longest Common Subsequences*，Communications of the ACM 20(5):350–353，1977。用于把 Hunt–Szymanski 算法与 1976 年的 Hunt–McIlroy 报告区分开。**《diff》条目把两者混为一谈，本文没有沿用那个说法**，而是按 Myers 论文参考文献 [10]、[11] 的两条独立条目表述。
4. `diff` 由 Douglas McIlroy 与 James Hunt 在 1970 年代初为 Unix 开发、随 1974 年 Unix 第 5 版发布、输出为 ed 可用的编辑脚本、McIlroy 关于"不写后处理器而是让 diff 直接生成 ed 语法"的说明，出自 [diff 条目](https://en.wikipedia.org/wiki/Diff)所引的原始资料与 McIlroy 本人的回忆。正文把这段明确标为当事人回忆。
5. Larry Wall 1984 年发布 `patch`（在 mod.sources 与 net.sources 新闻组发布源码），出自 diff 条目。正文只陈述他与 patch 的关系，未展开其生平。
6. Bram Cohen 提出了 patience diff。**本文没有核对到其原始博文**（`bramcohen.livejournal.com/73318.html` 在核查时返回 403，Wayback 存档页也没有正文），因此正文不复述其博文措辞，**也不给它标注年份**。
7. Git 对 patience diff 的实现：提交 `92b7de93fb`，Johannes Schindelin，2009-01-07，标题 "Implement the patience diff algorithm"。提交信息支持正文引用的全部三点：该算法"不先追求最小化 +/- 行数，而是尽量保住唯一的行"；"先确定在两个文件中都唯一的行，再取出保持（相对两个文件的）顺序的最长序列"；"其余行递归处理，在 patience 因没有共同唯一行而失败时以 Myers 算法兜底"。另见提交 `34292bddb8`（2009-01-07）"Introduce the diff option '--patience'"。**正文据此把 Git 的实现时间写成 2009 年 1 月**，而不是把它与 Cohen 提出该想法的时间混为一谈。
8. **Git 的默认算法是 Myers**，出自 Git 官方文档 `Documentation/diff-algorithm-option.adoc`：`default` / `myers` 条目写明 "The basic greedy diff algorithm. Currently, this is the default."；同文件把 `histogram` 描述为 "extends the patience algorithm to support low-occurrence common elements"。

## 本文实际运行的实现

`examples/run_model.py` 只用 Python 标准库；绘图另需 Pillow。环境记录见 `examples/run-environment.json`。

- **`myers.py`**：按论文实现的贪心 O(ND) 算法，带逐层记录与回溯；另含一个教科书式动态规划最长公共子序列，用来独立校验"脚本确实最短"。
- **`patience.py`**：唯一行锚点 + 最长递增子序列 + 锚点间隙交给 Myers。
- **输入**：`originals/pairs/` 下两组真实文件修订，取自公开仓库的历史提交（`integrity.py` 与 `source_rights.py` 各前后两版）。

### 校验

- 400 组随机小输入（种子 5）：Myers 的脚本能重建出 B，且编辑长度等于动态规划的最优值。
- 300 组随机小输入（种子 9）：patience 的脚本能重建出 B。
- 两组真实文件对：编辑长度分别等于动态规划最优值 13 与 5。
- 20 万组随机小输入（字母表 4 个符号、长度 3—10、种子 2）：两种算法有 23,525 组（11.8%）给出不同的脚本，其中 12,829 组（6.4%）patience 的公共子序列更短，0 组更长。**"0 组更长"是结构性结论**：锚点只会收紧解空间。

### 明确没有做到的事

- **没有测量"可读性"。** 正文把两件事分开：patience 会改变答案（有实测数据），它是否让答案更好读（没有测）。那需要人工阅读大量真实 diff，本文没有做。
- **没有实现 O(N) 空间的改进版本。** 本文的实现保存每一层的对角线状态，内存是 O(D²)。
- **没有做性能工程。** 所有耗时都是纯 Python 在本机上的数字，不能与其他语言的实现比较。
- **经典教学示例是构造的。** `frobnitz`/`fact` → `fib` 那段 C 代码是本文按 patience diff 常见教学场景写的，不是任何论文的原始例子。图 13 与正文均已标明。
- **没有覆盖 Git 的 histogram 变体**，也没有实现 Git 实际的 diff 代码。

## 原件图片盘点与使用边界

本文正文没有复制任何论文的原始图表。Myers 1986 年论文的 Figure 1（编辑图）与本文图 4 讲的是同一个例子，但图 4 是本文用程序重绘的，不是论文原图的复制。

正文使用 5 张第三方真实照片，全部来自 Wikimedia Commons：

| 文件 | 内容 | 作者 | 许可 |
|---|---|---|---|
| originals/photos/real-01-mcilroy.jpg | Douglas McIlroy，2011 年 | Denise Panyik-Dale | CC BY 2.0 |
| originals/photos/real-02-cohen.jpg | Bram Cohen | Ijon | CC BY-SA 4.0 |
| originals/photos/real-03-wall.jpg | Larry Wall，2007 年 | Randal Schwartz | CC BY-SA 2.0 |
| originals/photos/real-04-myers.jpg | Eugene Myers，ISMB 2014 | ismb | CC BY 2.0 |
| originals/photos/real-05-pdp11.jpg | DEC PDP-11/40，1973 年 | Jeff Keyzer | CC BY-SA 2.0 |

处理说明：

- 全部照片均未超过公众号每图 5,000,000 字节的限制，未做压缩。
- McIlroy 照片原文件 407 × 564、Larry Wall 照片 411 × 578，都是该文件的原始尺寸；本文未放大后称其为高清。
- 全部照片只做等比缩放与居中裁切以适配版面，没有改动人物、设备或背景。人物肖像的拍摄年代各不相同（McIlroy 2011 年、Myers 2014 年、Wall 2007 年），图注均写明拍摄场合，未暗示它们来自所讲述的历史现场。
- 未使用任何生成模型制造的人像或伪历史照片。

**第三方 CC BY-SA 素材范围**：Bram Cohen 照片（CC BY-SA 4.0）、Larry Wall 照片与 PDP-11 照片（CC BY-SA 2.0）采用 CC BY-SA 许可。相应图片保留各自注明版本的 CC BY-SA 许可；如对这些图作改编，须按该许可要求分享，保留作者、来源、许可链接及修改说明。本文对它们的处理是等比缩放与居中裁切。文章集合不据此把其他独立作品统一改为 CC BY-SA。

## 原创视觉及证据身份

- 图 03—14：原创机制示意与实测图表。图 08、09、10、13、14 的数字全部来自 `examples/results.json`。
- 图 04、05、06、07：按 Myers 论文的编辑图形式由本仓库程序重绘，示例序列 `abcabba` / `cbabac` 取自论文。
- 图 15：**本文实现实际输出的 unified diff 文本**，输入是公开仓库里两个真实修订；为适配版面按 46 个字符截断显示，完整输出见 `examples/results.json` 的 `real_diff` 字段。
- 图 16—19：第三方真实照片与原创文字说明的合成图；合成只做版面排布，没有改动照片内容。
- 图 01：第三方真实照片，未叠加任何图形或文字说明。
- 图 11、12、20：原创机制示意。
- cover.png：本文独立设计的封面，不计入正文图。

详细尺寸、最小字号与身份见 [figure-metadata.json](examples/figure-metadata.json)。全部原创图由可复现的 Python/Pillow 程序绘制，字号下限 40 设计像素（1062 像素宽画布，按 354 像素显示宽度折算约 13.3 像素）。

## AI 辅助的真实范围

本文由 Anthropic 的 Claude 在用户授权的技术科普文章任务中辅助研究、构思、撰写中文、编写并执行差分算法、制作程序图、核查数值并修订。算法的正确性用独立实现的动态规划逐例校验，全部测量结果实际运行并保存在 `examples/results.json` 与 `originals/model-stdout.txt`。AI 生成的文字、代码与图本身不作为外部事实证据；历史段落中的年份、作者与论文以公开一手来源核对，未能核到原文的部分（Bram Cohen 原始博文正文）已在正文与本文件中说明。本文没有假装作者参与过 diff 的早期开发或接触过任何当事人。

原创正文、原创图、封面与原创实验数据采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名可注明本篇题名及文章发布者；原创代码采用 [MIT](LICENSE-CODE.txt)。第三方照片的权利保留于各自权利人，不包含在上述授权中。
