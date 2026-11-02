# 来源与说明

本文的正文数字全部来自 `examples/run_model.py` 跑出的 `examples/results.json`，图由
`examples/build_figures.py` 生成。这里说明每个外部材料的用途、配图身份与模型边界。

## 一、文字参考

| 材料 | 位置 | 用途 |
| --- | --- | --- |
| Wikipedia，*Consistent hashing*（raw 快照，2026-11-02 取） | 第 48 行：虚拟节点（virtual nodes / weight）的定义 | 第九节"给节点名拼序号"与"权重"的说法 |
| 同上 | 第 60–82 行：复杂度表（加/删节点 O(K/N + log N)，查找 O(log N)，并注明 O(log N) 来自节点角度上的二分） | 第十一节"查找是二分，O(log 点数)" |
| 同上 | 第 93–107 行：使用者列表（Couchbase、OpenStack Swift、Dynamo、Cassandra、ScyllaDB、Voldemort、Akka、Riak、Gluster、Akamai、Discord、Chord） | 第十六节"谁在用"四张卡片的取材范围 |
| Karger, Lehman, Leighton, Panigrahy, Levine，*Consistent Hashing and Random Trees*，STOC '97，DOI `10.1145/258533.258660` | Crossref 元数据（标题、会议、年份、五位作者） | 第十五节的出处交代 |
| DeCandia 等，*Dynamo: Amazon's Highly Available Key-value Store*，SOSP 2007，DOI `10.1145/1294261.1294281` | Crossref 元数据（标题、会议、2007-10-14、作者前五位） | 第十六节"Dynamo 用环 + 虚拟节点做分区" |
| Lamping & Veach，*A Fast, Minimal Memory, Consistent Hash Algorithm*，arXiv `1406.2294` | arXiv 摘要页的 `citation_title` / `citation_author`（2014 年 6 月提交） | 第十三、十四节的 jump hash；代码里的乘数 `2862933555777941757` 与 `2^31` 取自该算法 |

说明几点：

- **没有读过 Karger 1997 与 Dynamo 2007 的正文。** 上面两篇只核对了 Crossref 记录的标题、
  会议、年份与作者名单；文中关于"当年动机是网络代理缓存"、"Dynamo 的分区组件用环加虚拟节点"
  这两句，取自 Wikipedia 条目对该论文的转述与论文标题本身，不是逐句读原文得到的。
- **jump hash 的算法细节**（六行代码、乘数、2^31、`key >> 33`）来自 arXiv 摘要页链到的
  技术报告版本；本文的 `examples/ch.py` 是按这份公开描述实现的，行为与之一致（每个桶等概率、
  增删只影响 1/n）。
- **本文不判断"一致性哈希是谁最先提出的"**，也不讨论 1997 年之前 Chord 一系的相近工作。

## 二、照片

| 文件 | 身份 | 来源与许可 | 原始尺寸 → 交付尺寸 |
| --- | --- | --- | --- |
| `assets/17-karger.jpg` | 真实照片（人物肖像） | Wikimedia Commons，`File:David Karger.jpg`，作者 Transclusion，2017-09-15，CC BY 4.0 | 3744×5616 → 1062×1593（按宽 1062 等比缩放，质量 92） |

`originals/David_Karger.jpg` 保留原始下载字节（9,721,867 字节），用于核对与再导出。
正文第二句的"第一作者是 MIT 的 David Karger"与该照片身份对应；本文没有其它人物肖像。

## 三、19 张图逐图对应

| 图 | 文件 | 身份 | 数据来源 |
| --- | --- | --- | --- |
| 1 | `01-modulo.png` | 原创教学示意 | `results.json` → `modulo_example`（六个真实 key 的 `% 10` 与 `% 11`） |
| 2 | `02-migration.png` | 原创教学示意 | `grow`（modulo 0.9093 / ring_v128 0.0964 / jump 0.0914 / ideal 0.0909） |
| 3 | `03-ring.png` | 原创教学示意 | `sample`（10 个节点位置 + 3 个 key 的位置与归属） |
| 4 | `04-walk.png` | 原创教学示意 | `sample.keys`（普通情况与 `wrap: true` 的那一个） |
| 5 | `05-strip.png` | 原创教学示意 | `strips.v1` / `strips.v16`（环上每段弧的起止比例） |
| 6 | `06-per-node.png` | 原创教学示意 | `hist.v1` / `hist.v128`（每节点 key 计数） |
| 7 | `07-vnodes.png` | 原创教学示意 | 环上位置现场算：`h64('node-03#i')`，i = 0..7 |
| 8 | `08-balance.png` | 原创教学示意 | `vnodes`（每节点点数 → `load_max` / `load_min`） |
| 9 | `09-tradeoff.png` | 原创教学示意 | `vnodes`（四个档位的均衡指标与 `steps`） |
| 10 | `10-lookup.png` | 原创教学示意 | `vnodes`（`points` → `steps`） |
| 11 | `11-failure.png` | 原创教学示意 | 环上位置现场算；数字取 `shrink.ring_v128` |
| 12 | `12-grow-shrink.png` | 原创教学示意 | `grow` / `shrink` |
| 13 | `13-jump-steps.png` | 原创教学示意 | `jump_trace`（一个 key 的 b、j 演化） |
| 14 | `14-jump-loop.png` | 原创教学示意 | `jump_steps`（n → 平均循环圈数） |
| 15 | `15-jump-load.png` | 原创教学示意 | `jump_load.counts`（十个桶的 key 数） |
| 16 | `16-compare.png` | 原创教学示意 | `grow` / `shrink` / `vnodes` / `jump_load` |
| 17 | `17-karger.jpg` | 真实照片 | 见上一节 |
| 18 | `18-who.png` | 原创教学示意 | 无数据；系统名单来自 Wikipedia 条目的"使用者"列表 |
| 19 | `19-takeaways.png` | 原创教学示意 | 无数据；四条结论复述正文中的实测值 |

图 18 是纯文字卡片，没有数字，因此不受 `results.json` 约束；它列出的四个系统都能在
Wikipedia 条目的使用者列表里找到对应条目。

## 四、模型做了什么，没做什么

`examples/ch.py` 里只有三个类/函数值得看：

- `Modulo.owner` —— `h64(key) % len(nodes)`。
- `Ring.owner` —— 在排好序的节点位置里 `bisect_left`，越界回到开头。
- `jump_owner` —— 六行循环，乘数 `2862933555777941757`、取低 64 位、`key >> 33`。

`run_model.py` 跑十组实验：扩容搬家比例、缩容搬家比例、虚拟节点数 1..1024 的均衡与查找步数、
两种配置的每节点负载直方图、环上的弧段、jump 的循环圈数、jump 的桶分布、一个 key 的 jump 轨迹。
全部只用 `hashlib` / `bisect` / `math` / `random`，没有第三方依赖，跑一遍约 6 秒。

口径的限定：

- **只算"归属"和"比较次数"，不测时间。** 文中所有"步数"是二分比较次数（jump 是循环圈数），
  不是微秒。
- **没有网络、没有副本、没有数据搬迁过程。** 一个 key 只有一个主人；真实系统里一份数据存三份。
- **哈希是 sha1 前 8 字节**，不是生产里常用的 murmur3/xxhash。换哈希函数会让具体数字抖动，
  但"取模搬 1−1/(N+1)"这个结论不变。
- **20 万个 key 是我选的样本量。** 小样本下 5.72% / 10.17% 这种数字会大幅抖动。

可以手算复核的几条：

1. 扩容理论值 = 1 − 1/11 = 9.0909%；取模理论值 = 10/11 = 90.909%。
2. 20 万 key ÷ 10 节点 = 每节点平均 2 万个；`hist.v1` 的均值确实是 20000。
3. 1280 个点的二分比较次数量级 = log₂1280 ≈ 10.32，实测均值 10.39（含边界情形）。
4. jump 的循环圈数应接近 ln n 量级：ln 4096 = 8.32，实测 8.87。
5. 10240 个点 = 10 节点 × 1024 虚拟节点；log₂10240 ≈ 13.32，实测 13.40。

## 五、审读范围

本文按四步流程成稿：正文、配图、来源并行准备，成稿后做了一次独立审读，并做了一次
本地正文/图片/完整性检查。审读记录了改动与理由，见 `review.md`。

**`VISUAL_REVIEW_NOT_RUN`**：成稿环境不支持读取图片，19 张图只做了程序化检查
（`figkit` 的越界、重叠、字号、对比度审计与安全区断言），没有人工目视确认。
读者若发现图上文字压线、彩条颜色难辨或照片裁切不当，请指出。
