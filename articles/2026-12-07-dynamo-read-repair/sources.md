# 来源与素材

## 一、参考文献

- Giuseppe DeCandia, Deniz Hastorun, Madan Jampani, Gunavardhan Kakulapati, Avinash Lakshman, Alex Pilchin, Swaminathan Sivasubramanian, Peter Vosshall, Werner Vogels. *Dynamo: Amazon's Highly Available Key-value Store*. SOSP 2007. DOI [10.1145/1294261.1294281](https://doi.org/10.1145/1294261.1294281)；作者版 PDF：<https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf>。
  本文用到的内容：N/R/W 与 R+W>N 的法定人数表述、虚拟节点与偏好列表、向量时钟与兄弟版本、暗示移交、Merkle 树反熵、购物车合并的动机。
- David Karger, Eric Lehman, Tom Leighton, Matthew Levine, Daniel Lewin, Rina Panigrahy. *Consistent Hashing and Random Trees: Distributed Caching Protocols for Relieving Hot Spots on the World Wide Web*. STOC 1997. DOI [10.1145/258533.258660](https://doi.org/10.1145/258533.258660)。
  本文第二节的一致性哈希与其"节点加入只搬一段弧"的性质来自这里。
- Avinash Lakshman, Prashant Malik. *Cassandra: A Decentralized Structured Storage System*. LADIS 2009. <https://www.cs.cornell.edu/projects/ladis2009/papers/lakshman-ladis2009.pdf>。
  第十六节"Cassandra 用时间戳做最后写入者赢、不产生兄弟版本"的依据。
- Amazon Web Services. *DynamoDB 读一致性*（Read consistency）. <https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html>。
  第十六节"DynamoDB 把最终一致读和强一致读做成两个选项"的依据。

## 二、照片

两张都是 Wikimedia Commons 上的原图，未做重压缩以外的处理（宽度大于 1062 px 时等比缩到 1062 px）。原文件另存于 `originals/`。

| 图 | 文件 | 原图尺寸 | 许可 | 作者 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 02 | `02-rack.jpg` | 2860 × 4304 | CC0（公有领域贡献） | Flickr 用户上传至 Commons | <https://commons.wikimedia.org/wiki/File:Rear_of_rack_at_NERSC_data_center_-_closeup.jpg> |
| 14 | `14-hdd.jpg` | 2428 × 2116 | Public domain | Zzubnik | <https://commons.wikimedia.org/wiki/File:Open_hard-drive.jpg> |

CC0 与公有领域素材不要求署名，这里仍按素材规则保留作者与来源。许可只覆盖照片本身，不覆盖本文正文与示意图。

## 三、原创示意图

16 张（01、03–13、15–18）由 `examples/build_figures.py` 用 `figkit.py` 绘制，身份一律为**原创教学示意**，不是现场照片、不是设备实拍，也不能当作真实系统截图引用。

图内的每个数字都来自 `examples/results.json`，由 `examples/dynamo.py` 真实跑出：

| 图 | 数字来源 | 对应字段 |
| --- | --- | --- |
| 01 | 示意 | 无数字（三个副本的版本号是示意，不是运行结果） |
| 03 | 真实环 | `dynamo.Ring` 按 `N_NODES=8`、`VNODES=32` 建出的 256 个刻度点，键 `k00000` 的偏好列表 |
| 04 | 集合论示意 | 无数字 |
| 05 | 抽样 | `results.json → quorum`（5 组 R/W × 3 种故障率 × 20000 次抽样） |
| 06 | 运行 | `results.json → runs[*].stale_rate` |
| 07 | 运行 | `results.json → trace.twins`（D 方案，4000 步） |
| 08 | 示意 | 版本号 7 / 5 是示意 |
| 09 | 运行 | `results.json → runs[C/D/E].twins` 与 `ops_to_converge` |
| 10 | 示意 | 无数字 |
| 11 | 运行 | `runs[D/F].counters.hints_played / hints_dropped / stale_rate` |
| 12 | 运行 | `runs[A/B/C/D].ages` |
| 13 | 计算 | `results.json → merkle1 / merkle10 / merkle_sweep` |
| 15 | 示意 | 向量时钟示意，模型未实现并发分支（见下） |
| 16 | 抽样 + 运行 | `quorum[1].p_fail20` 与 R=1/2/3 的往返次数 |
| 17 | 史料 | 年份来自参考文献与公开发布时间 |
| 18 | 结论 | 无数字 |

## 四、模型设定

`examples/dynamo.py` 的参数（`results.json → config`）：

| 参数 | 值 | 说明 |
| --- | --- | --- |
| 节点数 | 8 | 每个节点 32 个虚拟节点，环上 256 个刻度 |
| 副本数 N | 3 | 偏好列表长度 |
| 键数 | 120 | 键名 `k%05d`，按 `i × 9973` 取值以在环上散开 |
| 操作数 | 4000 | 前 3000 步允许写，第 3000 步之后只读 |
| 故障 | 每步 2% | 第 2000 步停止制造新故障；每次故障持续 60–260 步 |
| 写/读比 | 55% / 45% | 用同一个随机数决定 |
| 种子 | 20261207 | xorshift32，逐字节可复现 |

## 五、明确没做

- **没有实现向量时钟的分支合并**。模型里每个键只用单调递增的序号表示新旧，`read()` 取接触到的副本里最大的序号。第五节到第十五节的所有数字都基于这个简化；第十五节的兄弟版本是概念示意，不是跑出来的结果。
- **没有跨机房延迟**。所有副本被当成同延迟，故障只有"在线/离线"两种状态，没有慢节点、没有超时抖动。
- **没有磁盘故障与数据损坏**。副本之间的差异只来自"写没落到"和"被更新的写覆盖"，不来自介质错误。
- **没有成员变更与 gossip**。节点集合在运行期间固定，故障是人为开关，不涉及真实的成员协议。
- **反熵的哈希树是原地递归，不是持久化的 Merkle 树**。每次同步都重算两边子树哈希，`results.json → merkle*` 的交换次数是"多少个哈希被比较"的计数，不是字节量。
- **单次运行、单个种子**。第七节到第十二节的场景之间只差修复策略，用的是同一个种子，但没有做多次重复取均值；百分比差异在 1 个百分点以内的不要当结论。
- **没有目视检查渲染结果**。图由 `figkit.verify()` 的几何闸门（字形不出画布、不与别的标签重叠、最小字号、安全边距）与像素审计把守，但"看起来好不好"没有被人工确认。
