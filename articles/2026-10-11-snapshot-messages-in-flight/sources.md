# 来源、图像署名与复现实验

核对日期：2026-10-11。原创中文正文由 zyuanming 发布，采用 CC BY 4.0；该声明不自动扩展到图片、代码、第三方素材。本文使用 AI 辅助调研与写作；18幅教学图由代码按自设模型生成，区别于下列两幅 Flink 官方原图。没有虚构作者轶事、网络实测、故障恢复实验或性能基准。

## 一手文献与使用范围

1. K. Mani Chandy、Leslie Lamport，Distributed Snapshots: Determining Global States of Distributed Systems，ACM Transactions on Computer Systems 3(1)，1985年2月，63–75页。[作者提供的原论文](https://lamport.azurewebsites.net/pubs/chandy.pdf)。核对首页归属与出版信息；第2节进程/通道模型；第3节发送/接收标记规则、终止条件与收集记录；第4节快照不必等于原执行中实际出现的某个状态；第5节稳定性质。论文中的图、扫描页均未复制；首页再发表权限限制不能当作全篇开放许可。本稿不是论文翻译，8枚代币、五步调度与独立事件例子均为自设教学展开。
2. Apache Flink，2020-07-06，[Apache Flink 1.11.0 Release Announcement](https://flink.apache.org/2020/07/06/apache-flink-1.11.0-release-announcement/)，明确采用“Unaligned Checkpoints (Beta)”这一节的两幅原图与历史机制说明。核对对齐等待、屏障越过在途记录、持久化在途数据带来较大检查点等取舍。它不是当前版本使用指南，也不能作为本文玩具程序实现了 Flink 的证据。
3. Apache Flink，[From Aligned to Unaligned Checkpoints — Part 1: Checkpoints, Alignment, and Backpressure](https://flink.apache.org/2020/10/15/from-aligned-to-unaligned-checkpoints-part-1-checkpoints-alignment-and-backpressure/)，2020-10-15。作为理解流式处理工程语境的补充链接；未复用其中图像。

## 官方原图：本节两幅完整收齐

本篇工程对照的核心原链接为上列1.11.0发布公告的“Unaligned Checkpoints (Beta)”节，该节两幅正文信息图均保留原文件、原字节。公告的 Data Source API 与 CDC 插图属于其他功能介绍，未纳入本篇；站点导航图标和商标未当作内容插图。

- `assets/flink-aligned.gif`：原图 Fig.1 Aligned Checkpoints，原URL https://flink.apache.org/img/blog/2020-07-06-release-1.11.0/image1.gif ，453×173，8帧，65524字节。保持动画与原尺寸，未重绘英文图例或把放大代理当原图。
- `assets/flink-unaligned.png`：原图 Fig.2 Unaligned Checkpoints，原URL https://flink.apache.org/img/blog/2020-07-06-release-1.11.0/image2.png ，1654×616，127907字节。原始PNG无裁切、无改绘。

两图署名：Apache Flink / Apache Software Foundation。许可依据是上述官方网页对**网站内容本身**的明确 Apache License v2 声明，不是从 Flink 软件代码的许可推断图像权限。网站页脚原署名为：© 2024 Apache Software Foundation。原文件未见另外的第三方归属声明。

许可：[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)。随稿保留[完整许可文件](originals/FLINK-WEB-LICENSE.txt)，其原文件来自 https://raw.githubusercontent.com/apache/flink-web/asf-site/LICENSE 。该网站仓库相应分支未提供根目录 NOTICE 文件（该路径返回404），未虚构一个上游 NOTICE；本段保留已提供的页面署名与来源。Apache Flink、Flink 及其标志为 Apache Software Foundation 的商标或注册商标，使用原图不暗示其对本稿背书。

## 原创图与代码

01–03解释同一组8枚代币的正常、漏算和重复计数；04展示进程与双向通道；05展示一致切面的因果约束；06–10逐步跟踪同一轮快照；11–14解释FIFO边界、记录窗口与每条入通道独立结束；15对齐实时与冻结账本；16为两个无因果依赖事件的合法重排；17为终止判定反例；18区分理论模型与工程补充。18幅PNG均1200×840，中文采用Noto Sans CJK，没有把论文图改绘后冒称原创。

- [完整模拟程序](examples/simulate.py)：Python标准库，两个进程、单轮快照、可靠FIFO队列；实际运行主调度和消息先到的变体，总数均为8。程序没有实现真实网络、线程、持久化、崩溃恢复或多轮快照。
- [原创图生成程序](examples/generate_figures.py)：Python、Pillow；可在具有相同字体的环境运行重画。图片用于解释自设模型，不是设备截图或性能测量。

历史人物是算法归属所必需的说明，不构成人物视觉传记。未采用无适当复用依据的肖像，也未生成假肖像替代。
