# 来源与许可

## 一、文字参考

1. Wikipedia, *Branch predictor*. 存取方式：`https://en.wikipedia.org/wiki/Branch_predictor?action=raw`（2026-10 抓取，43 637 字节）。用于：静态预测的「向后跳猜跳、向前跳猜不跳」规则与 RISC-V ISA 的相关建议（原文件第 24 行）、Pentium 4 / 4E 接受预测前缀而 Pentium M / Core 2 忽略且此后没有 x86 厂商重新引入（第 26 行）、动态预测器在无缓存信息时回落到静态预测（第 28 行）、初代 Pentium 使用饱和计数器（第 61 行）、两级自适应预测器由 Yeh 与 Patt 于 1991 年提出并被 Pentium MMX 采用（第 81 行）、Pentium MMX / II / III 的 4 位局部历史 + 16 格图案历史表（第 89 行）、gshare 与 gselect 的命名区别（第 98 行）、AMD K8 的双模态 + 全局组合与「选择本身又是双模态」（第 164 行）、Alpha 21464 的最小误判代价 14 拍（第 166 行）、Spectre 的公开时间与手法（第 168 行）。
2. J. P. Shen, M. H. Lipasti, *Modern Processor Design: Fundamentals of Superscalar Processors*, McGraw-Hill, 2005. 经 Wikipedia 第 20 行引用，用于「静态预测只依据指令本身、不看运行历史」这个定义。
3. *The RISC-V Instruction Set Manual, Volume I: Unprivileged Architecture*（2024-04-11 版）。经 Wikipedia 第 24 行引用，用于「RISC-V 建议软件按向后跳 = 跳来优化」这一条。
4. Agner Fog, *The Microarchitecture of Intel, AMD, and VIA CPUs*, 2016-12-01，`https://www.agner.org/optimize/microarchitecture.pdf`（第 26、38 页）。经 Wikipedia 引用，用于 Pentium 4 之后各家对预测前缀的处理。
5. Ars Technica, *The Pentium 4 and the G4e: An Architectural Comparison*, 2001-05-12。经 Wikipedia 第 28 行引用，用于「无缓存信息时回落到静态预测」的两个实例（PowerPC 7450、Pentium 4）。

**没有读过的**：本文没有读任何一份 CPU 厂商的微架构白皮书或指令集手册原文。上列第 2–5 项都是通过 Wikipedia 的引用链得到的，我只核对了 Wikipedia 正文的表述，没有去核对被引文献的页码内容。

## 二、照片（1 张）

| 图 | 文件 | 作者 | 许可 | 原尺寸 |
| --- | --- | --- | --- | --- |
| 图 2 | `Intel_Wolfdale_die_shot_(E8400)_etched_-_29336152187.jpg` | Martijn Boer | **公有领域** | 3341×2350 |

来自 Wikimedia Commons（`File:Intel Wolfdale die shot (E8400) etched - 29336152187.jpg`）。原图保存在 `originals/`，未做裁剪、调色或重压缩；`assets/` 里的版本只在宽度超过 1062 px 时等比缩小一次（Pillow `LANCZOS`，JPEG 质量 92）。

同一次检索还下载了 `File:Intel 286 CPU - Die shot 20100311.jpg`（80286 裸片）作为候选，最后没有用上，**已从 `originals/` 删除**，不随文章发布。

正文里没有第二张照片。关于「哪个年代的 CPU 开始有分支预测」这类硬件史，我只写了 Wikipedia 明写的部分（初代 Pentium 用饱和计数器、Pentium MMX 用两级自适应），没有自己推断 80286 有没有预测机制，所以也就不放一张「它没有」的照片。

## 三、18 张示意图的数字来源

每张图里的数字都来自 `examples/results.json`，没有一个手写。

| 图 | 内容 | 数据来源（`results.json` 的键） |
| --- | --- | --- |
| 1 | 五级流水线的气泡 | 无数字；结构示意，气泡数按教科书五级流水线画 |
| 3 | 预测器的通用结构 | 无数字；计数器值 `3 0 1 2 3 1` 是示意，不代表某个具体表 |
| 4 | 一位计数器状态机 | 无数字；两个状态与迁移规则来自 `Bimodal(bits=1)` |
| 5 | 两位计数器状态机 | 无数字；四个状态与饱和规则来自 `Bimodal(bits=2)` |
| 6 | 循环退出的逐步对错 | `detail.outcomes`、`detail.preds[*].pred`、`detail.preds[*].miss_at`（`loop_trace(5, 3)`，18 步） |
| 7 | 错判率随循环长度 | `loop_sweep[*].iters / static / one_bit / two_bit / gshare` |
| 8 | 64 个分支挤 16 格 | `alias[*].per_slot`（`entries` 与 `working_set` 的比值） |
| 9 | 表项数 vs 错判率 | `alias[*].entries / per_slot / miss` |
| 10 | 两个相关分支 | `correlated_sample.a / b`（12 轮，图里画前 10 轮） |
| 11 | gshare 的索引构造 | 无数字；12 位地址 / 历史 / 异或结果的示例向量，索引 = 逐位异或（对应 `Gshare._idx()`） |
| 12 | 历史长度阶梯 | `ladder.correlated / period3 / loop10[*].hist / miss` |
| 13 | 局部历史结构 | 无数字；结构与 `Local2(log_pcs=10, hist_bits=8)` 一致；文中引用的错判率来自 `matrix` |
| 14 | 锦标赛结构 | 无数字；结构与 `Tournament` 一致；文中引用的错判率来自 `matrix` |
| 15 | 七种预测器 × 七条 trace | `matrix[<trace>][<predictor>]` |
| 16 | 错判率 vs IPC | `cost[*].miss / cpi / ipc / slowdown_vs_perfect`、`config.width / branch_density / penalty / base_cpi` |
| 17 | TAGE 结构 | 无数字；只画结构，**正文明确指出没有给 TAGE 建模** |
| 18 | Spectre 的四步 | 无数字；流程依据 Wikipedia 第 168 行的描述 |
| 19 | 四条结论 | 汇总，无新数字 |

## 四、模型做了什么、没做什么

**做的**：七种预测器（两种静态、一位、两位、局部历史 8 位、gshare 12 位、锦标赛）在七条合成 trace 上的错判率；gshare 的历史长度阶梯；表大小与别名；循环长度扫描；一个把错判率换成 CPI / IPC 的成本模型。

**没做的**：

- **没有对接真实硬件。** 没有读任何 CPU 的性能计数器，没有在真实 CPU 上验证过预测准确率。所有数字都是自己写的模拟器算出来的。
- **没有给 TAGE 建模。** 试过一版简化实现，在合成 trace 上不稳定（同一份代码在 `period3` 上击败局部历史、在 `loop10` 上又输给它，换一个分配策略结果就翻过来），最后整段删除，正文只画结构不给数字。
- **trace 是合成的。** 七条 trace 都由 `bp.py` 生成，不是真实程序的指令流。真实程序的分支里有大量相关性和局部结构，本模型的绝对值不能直接外推。
- **没有模拟乱序执行、取指带宽、BTB（分支目标缓存）。** 模型只算「猜对没猜对」，猜对之后的取指地址、目标地址缓存全部省略。真实 CPU 的误判代价取决于流水线深度、是否要重新取指、BTB 是否命中，本文统一取 15 拍。
- **没有做 Spectre 的复现。** 第 18 节只描述公开的机制，没有在本模型里实现任何缓存侧信道。
- **没有目视看过任何一张图。** 当前模型不能读图。19 张图都通过了 `figkit` 的几何闸门，但观感与视觉误导没有检查，记为 `VISUAL_REVIEW_NOT_RUN`。
