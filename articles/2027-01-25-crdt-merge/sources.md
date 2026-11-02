# 来源与说明

本文的正文数字全部来自 `examples/run_model.py` 跑出的 `examples/results.json`，图由
`examples/build_figures.py` 生成。这里说明每个外部材料的用途、配图身份与模型边界。

## 一、文字参考

| 材料 | 位置 | 用途 |
| --- | --- | --- |
| Shapiro, Preguiça, Baquero, Zawirski，*A comprehensive study of Convergent and Commutative Replicated Data Types*，INRIA 研究报告 RR-7506，2011-01-13，HAL `inria-00555588` | HAL API 元数据（标题、四位作者、`docType=REPORT`、2011-01-13、PDF 文件名）；PDF 封面页与第 1 页摘要 | 第十七节的出处交代；"收敛型""半格（semilattice）"这两个说法在正文中的用法 |
| 同上，会议版 *Conflict-Free Replicated Data Types*，SSS 2011（第 13 届自稳定、安全与分布式系统研讨会），HAL `hal-00932836` | Wikipedia 条目参考文献表（标题、会议名、年份） | 第十七节"会议版标题去掉了 comprehensive study"一句 |
| Wikipedia，*Conflict-free replicated data type*（raw 快照，30,957 字节，2026-11-02 取） | 第 8 行：2011 年由四人正式定义；第 117 行：OR-Set 的标签与墓碑机制、以及"用版本向量代替墓碑"的优化 | 第十四节的标签/作废说法，第十六节"墓碑为什么不能随便删" |
| 同上 | 第 133–135 行：Redis Enterprise 的 CRDT 复制、SoundCloud 的 Roshi（LWW-Element-Set）、Riak（含《英雄联盟》聊天与 bet365 两处引用） | 第十八节四张卡片的取材范围 |
| 同上 | 第 144 行：Figma 的多人协作按属性用 LWW，图层顺序用分数索引、并发插入由服务端兜底 | 第十八节 Figma 那张卡片 |

说明几点：

- **没有读过 RR-7506 的正文。** 我读了封面页与第 1 页摘要（PDF 里第 4 页），并用关键词在全文里
  数过出现次数（`semilattice` 18 次、`convergent` 5 次、`2P-Set` 28 次、`OR-Set` 6 次）。
  文中"报告把状态式归到收敛型、要求合并是并半格上的操作"这两句，依据是标题、摘要与关键词分布，
  **不是逐节读原文得到的**；具体定义请以报告为准。
- 报告正文标的是 **47 页**，PDF 文件有 51 页（多了 HAL 封面页与两页扉页/尾页）。
- **第十八节的四条系统事实全部是二手的**，来自 Wikipedia 条目正文及其引注，我没有去读 Riak 文档、
  Redis 官方博客、SoundCloud 的 Roshi 仓库或 Figma 的两篇工程博客原文。文中保留了条目里给的
  数字（750 万同时在线、每秒 1.1 万条消息），并在正文里写明出处是条目，不是我核过的原始材料。
- **本文不判断"哪种 CRDT 更好"**，也不讨论操作式、增量状态式、序列 CRDT（Yjs、Automerge 那一支）
  的内部结构；第十九节说清楚了这份模型没有覆盖它们。

## 二、档案材料

| 文件 | 身份 | 来源与许可 | 原始尺寸 → 交付尺寸 |
| --- | --- | --- | --- |
| `assets/17-rr7506.png` | 档案扫描件（研究报告封面，PDF 直出渲染） | HAL 开放获取，`https://inria.hal.science/inria-00555588/file/techreport.pdf`，2011-01-13 提交；HAL 记录未标注具体许可，本文仅作引用、未改写封面内容 | 1580×2265 → 1062×1522（按宽 1062 等比缩放，质量 92） |

`originals/rr7506.pdf` 保留原始下载字节（1,014,719 字节），`originals/rr7506-cover.png`
是从 PDF 第 2 页按 200 dpi 渲染、按墨迹包围盒裁掉页边得到的中间文件（1,580×2,265）。
封面上的作者、机构、报告编号都是原件内容，没有重画或补字。

## 三、19 张图逐图对应

| 图 | 文件 | 身份 | 数据来源 |
| --- | --- | --- | --- |
| 1 | `01-two-writes.png` | 原创教学示意 | 无数据；对应 `results.json` 里 A=7、B=5 这组状态 |
| 2 | `02-late-order.png` | 原创教学示意 | `merge_order.late`（`distinct` = 3，`top` = 79） |
| 3 | `03-laws.png` | 原创教学示意 | 无数据；三条律的定义 |
| 4 | `04-order-test.png` | 原创教学示意 | `merge_order`（八种规则的 `distinct`）与 `idempotence`（1/2/5 次投递的最终值） |
| 5 | `05-lww.png` | 原创教学示意 | 无数据；LWW 的两条写与合并结果 |
| 6 | `06-tiebreak.png` | 原创教学示意 | `tiebreak`（`trials` 200、`higher` 200、`lower` 0、三组 `examples`） |
| 7 | `07-rmw.png` | 原创教学示意 | `rmw`（`final` 1、`intended` 3） |
| 8 | `08-gcounter.png` | 原创教学示意 | `merge_order.gcounter` 的起点状态（7 / 5 / 2 → 14） |
| 9 | `09-idempotent.png` | 原创教学示意 | `idempotence.sum` 与 `idempotence.gcounter`（14/28/70 与 14/14/14） |
| 10 | `10-pncounter.png` | 原创教学示意 | `merge_order.pncounter` 的起点状态（加 7/5/2、减 1/0/2 → 11） |
| 11 | `11-partition.png` | 原创教学示意 | `partition`（gcounter 300、pncounter 300、late 100，`truth` 300） |
| 12 | `12-gossip.png` | 原创教学示意 | `gossip_scale`（3–32 台的轮数 3.75–10.25） |
| 13 | `13-twopset.png` | 原创教学示意 | 无数据；2P-Set 的判据 `added − removed` |
| 14 | `14-orset.png` | 原创教学示意 | `add_wins`（`orset_tags` 2、`orset_dead` 1） |
| 15 | `15-add-wins.png` | 原创教学示意 | `add_wins`（`orset_has` true、`twopset_has` false） |
| 16 | `16-growth.png` | 原创教学示意 | `growth`（七个档位的三种字节数） |
| 17 | `17-rr7506.png` | 档案扫描件 | 见上一节 |
| 18 | `18-who.png` | 原创教学示意 | 无数据；四个系统的名单与描述来自 Wikipedia 条目 |
| 19 | `19-takeaways.png` | 原创教学示意 | 无数据；四条结论复述正文中的实测值 |

图 12 的横轴是机器台数、纵轴是轮数，曲线只有 8 个点，值全部来自 `gossip_scale` 里
每个规模 4 个随机种子的平均；图上标了 3、6、12、32 四个点，中间的点没有标数字，
是因为标签会互相压住（38 px 的下限不允许再缩小字号）。

图 18 是纯文字卡片，没有数字，因此不受 `results.json` 约束；它只写条目里确有的系统，
没有把"某产品大概也用了 CRDT"这类猜测写进图里。

## 四、模型做了什么

`examples/crdt.py`（256 行）是五种 CRDT 加两种朴素做法的最小实现，`examples/run_model.py`
（349 行）跑九组实验，约 1 秒，输出 `results.json`（7 KB 上下）：

1. `merge_order`：三台机器各自做一串操作，取出三份状态，随机打乱顺序合并 200 次，
   数能得出几种不同的最终结果。
2. `idempotence`：同一份状态投递 1 / 2 / 5 次，看最终值。
3. `gossip`：三台机器、300 次操作，随机两两交换全量状态，看几轮后三份状态完全相同，
   以及收敛时的值对不对。
4. `gossip_scale`：机器台数 3、4、6、8、12、16、24、32，每轮每台机器都拉一份全量状态，
   量需要的轮数（每个规模 4 个种子取平均）。
5. `partition`：`{A,B}` 与 `{C}` 断开，各加 100 次，然后合并，看记住多少。
6. `add_wins`：A 加 apple、B 同时删 apple，合并后看两种集合的结论。
7. `growth`：操作数 10 到 2000，量三种状态的序列化字节数。
8. `tiebreak`：200 次时间戳相同的写，看谁赢。
9. `rmw`：三台机器并发读改写计数器，看最后剩几。

所有随机数都带固定种子，同一台机器上重跑，`results.json` 逐字节相同。

## 五、模型没做什么

- 只有状态式 CRDT。操作式（只发"我加了一次"）与增量状态式（只发变化的那一小块）一行没写。
- 没有向量时钟，也没有因果关系的判定。图 12 量的只是"状态何时完全相同"，不是"谁见过谁"。
- 没有真网络：没有丢包、乱序、延迟分布、分区检测、成员变更。所谓"八卦"就是每轮随机拉一份状态。
- 没有跨机器时钟漂移的模拟。LWW 的 `ts` 是各机器自己的计数器，撞车靠节点名兜底；
  真实系统里还有混合逻辑时钟、HLC 之类的东西，本文没碰。
- 没有测并发度、吞吐、GC 停顿。图 16 的字节数是 `json.dumps` 之后的长度，用来比相对大小，
  不是任何真实序列化格式的体积。
- 第 18 节的系统清单是二手的，见第一节的说明。

## 六、几条可以手算复核的

1. G-Counter 的三格 7 / 5 / 2，合并后仍是 7 / 5 / 2，`value()` = 14。
2. 同一份三格状态投递 5 次，`max` 之后还是 7 / 5 / 2，值还是 14；而"合并相加"会得到 70。
3. PN-Counter 的余额：加 7+5+2 = 14，减 1+0+2 = 3，14 − 3 = 11。
4. 分区测试两侧各加 100 次：`{A,B}` 两格各 100、`{C}` 一格 100，合并后 300。
5. OR-Set 的 apple：标签 `{A#1, B#2}`、作废 `{A#1}`，差集 `{B#2}` 非空，所以还在。

## 七、审读状态

**VISUAL_REVIEW_NOT_RUN**：本次成稿的模型不能读图。19 张图只通过了 `figkit` 的机器检查
（元素不出画布、标签不重叠、字号不低于 38 px、无杂色、墨迹对比度），
**没有人眼看过渲染结果**。图的排版是否好读、有没有视觉上的挤压或空洞，需要人工复核。
