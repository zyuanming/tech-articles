# 2026年10月24日：再往原理里走一步

这批 30 篇原创中文长文从具体问题出发，用可手算的例子、连续图解、反例和可运行的小程序逐步解释原理，共 378 张正文配图。每篇的来源、模型边界和图片许可见随文 `sources.md`。

图片按正文中的独立图片引用计数，不把同图面板算成多张。真实照片与史料保留各自权利，未取得可收录原件的控制矩阵和继电器图仅提供原站查看链接，不计入本地图数。

## 算法：保存什么，忘记什么

| 文章 | 图数 |
| --- | ---: |
| [把字母排成一团，为什么还能原样还原？BWT 的可逆重排](../articles/2026-10-24-bwt-reversible-clustering/read.md) | 13 |
| [有序链表加几层捷径，怎样少走路又容易插入？](../articles/2026-10-24-skip-list-express-lanes/read.md) | 13 |
| [只记一个名字，怎样找出过半的那一个？](../articles/2026-10-24-majority-vote-cancellation/read.md) | 12 |
| [排错一个方案，怎样把所有选择原样放回？Dancing Links](../articles/2026-10-24-dancing-links-exact-cover/read.md) | 12 |
| [不记住每个人，怎样估计到底来了多少人？](../articles/2026-10-24-hyperloglog-distinct-count/read.md) | 14 |

## 图形与游戏：屏幕上的数怎样变成形状

| 文章 | 图数 |
| --- | ---: |
| [明明已经透明，蓝色为什么还会漏出来？把图片边缘的 alpha 算清楚](../articles/2026-10-24-premultiplied-alpha-edges/read.md) | 14 |
| [鼠标指向哪块石头？让射线沿着格子边界走，为什么不会跳过去](../articles/2026-10-24-dda-voxel-traversal/read.md) | 14 |
| [没有画一盏灯，墙角为什么也会变暗？从八条射线理解环境光遮蔽](../articles/2026-10-24-ambient-occlusion-visibility/read.md) | 14 |
| [从格子里长出模型，为什么拐角容易被削掉？Dual Contouring 多问了一个方向](../articles/2026-10-24-dual-contouring-sharp-corners/read.md) | 14 |
| [扩散明明会抹平差别，为什么两种浓度还能长出斑纹？亲手算一步反应扩散](../articles/2026-10-24-reaction-diffusion-patterns/read.md) | 15 |

## 数学与控制：把直觉变成能检查的规则

| 文章 | 图数 |
| --- | ---: |
| [不把每一步都算出来，怎样知道系统最终会稳住？](../articles/2026-10-24-lyapunov-energy-certificate/read.md) | 12 |
| [油门踩到底，什么时候该换成刹车？一次最短时间控制的手算](../articles/2026-10-24-bang-bang-braking-switch/read.md) | 12 |
| [算不出一个准数，能不能保证答案没有跑出这两条边？](../articles/2026-10-24-interval-arithmetic-enclosures/read.md) | 12 |
| [只量三次流量，为什么中间那次要算四份？从面积走进辛普森公式](../articles/2026-10-24-simpson-three-samples/read.md) | 12 |
| [三份读数互相打架，怎样找出最合适的一条直线？把 QR 分解拆成一次投影](../articles/2026-10-24-qr-orthogonal-fitting/read.md) | 12 |

## 系统：并行工作怎样收尾

| 文章 | 图数 |
| --- | ---: |
| [一颗CPU忙到最后，其他CPU在等什么？任务窃取怎样把活重新分开](../articles/2026-10-24-work-stealing-deques/read.md) | 12 |
| [读到了两个正确数字，为什么拼起来却错了？序列锁怎样发现一次“读裂了”](../articles/2026-10-24-seqlock-consistent-copy/read.md) | 12 |
| [一个文件名，怎么借走了服务的权限？从“混淆代理人”理解能力安全](../articles/2026-10-24-capability-authority-paths/read.md) | 12 |
| [电脑模拟十分钟，为什么不必一秒一秒等？离散事件模拟的日历](../articles/2026-10-24-discrete-event-calendar/read.md) | 12 |
| [每台机器都说“我闲着”，为什么任务还没结束？给分布式计算收最后一张回执](../articles/2026-10-24-termination-dependency-tree/read.md) | 12 |

## 技术史：人们怎样重新组织计算

| 文章 | 图数 |
| --- | ---: |
| [想让程序最后得到对的结果，最开始必须满足什么？跟 Dijkstra 倒着想一次](../articles/2026-10-24-dijkstra-weakest-precondition/read.md) | 13 |
| [一条加法指令，谁来按顺序拨动开关？Wilkes 与微程序控制](../articles/2026-10-24-wilkes-microprogram-control/read.md) | 13 |
| [几个开关接在一起，为什么能做逻辑？Shannon 把接线问题变成代数](../articles/2026-10-24-shannon-relay-boolean/read.md) | 13 |
| [源码明明干干净净，运行的程序为什么仍可能变样？Thompson 留下的信任难题](../articles/2026-10-24-thompson-trusting-compiler/read.md) | 13 |
| [先讲清楚，再拼成程序：Knuth 的文学化编程为什么需要两种顺序](../articles/2026-10-24-knuth-literate-programming/read.md) | 13 |

## 仪器与工程：怎样从微弱变化读出信号

| 文章 | 图数 |
| --- | ---: |
| [十八块镜子怎样变成一面镜子：韦布望远镜为什么还要“调相”](../articles/2026-10-24-webb-segments-phase-alignment/read.md) | 12 |
| [把镜子吊起来，为什么反而更稳？LIGO 悬挂系统里的频率选择](../articles/2026-10-24-ligo-pendulum-isolation/read.md) | 11 |
| [太空里的发电机为什么没有转轴？从一对热电材料读懂 RTG](../articles/2026-10-24-rtg-thermoelectric-temperature/read.md) | 11 |
| [声呐怎样“朝一个方向听”：把四条录音错开，再对齐](../articles/2026-10-24-sonar-delay-beamforming/read.md) | 12 |
| [两路线圈怎样告诉电脑：这根轴转到了哪里？](../articles/2026-10-24-resolver-angle-sensing/read.md) | 12 |

原创正文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。原创教学图、代码与第三方素材的具体许可按各篇说明执行；公开可访问不等于允许转载。本文目录不代表微信公众号或其他平台发布状态。
