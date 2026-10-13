# 来源、事实边界与逐图权利

文章：《把词频统计分给一百台机器，最难的是哪一步？》

资料核查日期：2026-10-13。署名发布者：zyuanming。

## 一手与官方来源

### S1：原始论文

Jeffrey Dean、Sanjay Ghemawat，*MapReduce: Simplified Data Processing on Large Clusters*，OSDI 2004，会议页面所列页码137–150。

- [Google Research论文页](https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/)
- [官网提供的完整PDF](https://storage.googleapis.com/gweb-research2023-media/pubtools/4449.pdf)

核查的是Google页面链接的13页PDF，该PDF内部页码1–13，与会议页面的页码范围不是同一种编号。本文#page链接使用PDF页序。

支持范围：

- §2及§2.1：输入记录、map产生中间键值对、同键分组、reduce；词频作为示例。
- §3.1、§3.2：输入切分、任务安排、按分区写中间文件、reduce取中间数据和排序、master维护状态与位置、多份最终输出。
- §3.3：worker失败后重执行，完成map的本地结果失联，完成reduce写全局文件系统；原实现master失败中止；确定性条件下的顺序等价语义；临时文件、map完成消息、reduce原子重命名。
- §3.4、§3.5：数据局部性，任务数与机器数分开及细粒度的成本。
- §3.6：慢任务与备用执行。
- §4.1–4.3：分区、分区内部键序、可选局部合并。
- §4.5：外部副作用应由应用处理其原子性和幂等性，不能把输出文件保证扩成任意外部动作保证。

原件图像盘点：Figure 1执行总览与本文核心直接相关；Figure 2是grep吞吐曲线，Figure 3是排序在正常、关闭备用任务及故障情况下的曲线，Figure 4是作业数历史变化；Table 1为2004年8月作业统计。本文链接完整官方原件，不复制这些图表：未在论文页/PDF找到适用于这些图版的开放再分发许可。正文20幅新图是独立语料、独立布局和原创实现，不是原图临摹；教学时间线尤其不能当作Figure 3的重绘或实测证据。

### S2：Apache Hadoop官方实现说明

[MapReduce Tutorial](https://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html)。本次页面显示Apache Hadoop 3.3.5、Last Published 2023-03-15。stable路径可能变化，此处记录实际读取到的页面版本，不宣称它就是2026年的最新发行版。

支持范围：词频示例、Mapper/Reducer/Partitioner职责、局部combiner、shuffle取相关分区，以及shuffle与sort可以重叠的说明。正文没有声称Google 2004实现等于Hadoop架构，也没有复制其Java程序或把本地Python模型称为Hadoop运行。

### S3：计算机历史博物馆馆藏记录

[Google server assembly](https://www.computerhistory.org/revolution/the-web/20/391/2074)，Object ID 102662167，Date Introduced 1999，Manufacturer Google，Gift of Google, Inc.。

支持范围：早期Google机架作为真实对象的身份和普通PC协作背景。馆藏页自己的Mark Richards照片受独立版权保护，本文未复制该照片。正文使用S4中另一位摄影者公开许可的照片。照片拍摄年份不等于设备引入年份；照片所示早期设备不被当作2004年论文集群实照。

## 第三方照片

### S4：Google's First Server Rack.jpg

- [文件与完整权利说明页](https://commons.wikimedia.org/wiki/File:Google%27s_First_Server_Rack.jpg)
- [摄影者原始Flickr页面](https://www.flickr.com/photos/94599716@N06/16938946811/)
- [原始JPEG](https://upload.wikimedia.org/wikipedia/commons/b/b2/Google%27s_First_Server_Rack.jpg)
- 署名：Photographing Travis（文件页列出的摄影者名；结构化元数据为Travis Wise）。
- 拍摄日期：2012-08-12；此日期不是上传日期，也不是机架制造年份。
- 许可：[Creative Commons Attribution 2.0 Generic](https://creativecommons.org/licenses/by/2.0/)，完整法律文本随附于licenses/CC-BY-2.0.html。
- 文件：assets/google-rack-original.jpg；1536×2048像素，649268字节；原始JPEG未裁切、未调色、未压缩重存。网页或文章阅读器的等比例显示缩放不改变保存的原件。
- SHA-256：0b4f0f8c3d3fd6419942cdce516d1ad4aa7d4768a12ffeaa88d076dedc444e1f。
- 理解作用：让读者先看见多层真实电脑板卡和线缆，理解集群不是共享一块无边界内存的抽象大盒子。
- 本文与摄影者、Google、博物馆之间无背书关系。照片仍按CC BY 2.0使用，不转授为CC BY 4.0。

## 原创教学图逐项说明

以下作品由zyuanming发布，使用CC BY 4.0，法律文本见licenses/CC-BY-4.0.html。图的数学对象与机制参考S1、S2；具体语料、视觉布局、程序、配色和教学表达为本篇原创。不是历史截图或实拍，不采用图像生成模型伪造历史材料。

| 正文图号 | 文件 | 新增的理解作用 |
|---|---|---|
| 图1 | assets/02-baseline.png | 可数格子建立cat5、dog3、bird2、fish2基准 |
| 图3 | assets/01-corpus.png | 展示完整十二词输入及A/B/C身份 |
| 图4 | assets/03-map-one.png | 一条输入产生四对，重复cat必须保留 |
| 图5 | assets/04-mapped-all.png | 完整列出三任务的十二份贡献 |
| 图6 | assets/05-route.png | 同键同分区，不同键可以同分区 |
| 图7 | assets/06-shuffle-cat.png | 跨来源收齐cat的五份贡献 |
| 图8 | assets/07-group-within-partition.png | 同一分区内仍要区分bird与fish键组 |
| 图9 | assets/08-reduce-cat.png | cat按来源相加2+1+2=5 |
| 图10 | assets/09-output-files.png | 多份输出不等于全局有序的单文件 |
| 图11 | assets/10-control-data.png | 区分调度控制消息与中间数据路径 |
| 图12 | assets/11-task-machine.png | 任务是工作包，机器可顺序处理多包 |
| 图13 | assets/20-data-locality.png | 本地读输入与后续网络shuffle并不矛盾 |
| 图14 | assets/12-worker-failure.png | 本地中间结果失联后依靠可读输入重算 |
| 图15 | assets/13-duplicate-attempt.png | 两次执行不能贡献两次，并算出错误结果 |
| 图16 | assets/14-commit-boundary.png | 临时文件到完整输出的提交，外部副作用边界 |
| 图17 | assets/15-straggler.png | 备用尝试如何缩短尾部等待；纯教学时间 |
| 图18 | assets/16-hot-key.png | 相同刻度对比原5/3/4与热点105/3/4条数 |
| 图19 | assets/17-combiner.png | 十二对变九对，数值总和仍为十二 |
| 图20 | assets/18-mean-counterexample.png | 平均值摘要丢条数会算错，需保留和与数量 |
| 图21 | assets/19-program-result.png | 实际本地运行数据的可读排版；不是终端截图 |
| 独立封面 | cover.png | 两份cat贡献跨原位置汇集的视觉引子 |

正文图2是上一节S4列明的独立第三方照片。所有PNG教学图由examples/build_figures.py生成；图像职责和像素尺寸亦可查examples/figure-metadata.json。

## 数值与实验范围

- 输入为本篇人工构造；所有词频、重复合并错误、热点条数和局部小计来自examples/wordcount.py。
- 完整输入与结果：examples/corpus.json、examples/results.json、examples/output.txt。
- 检验情景415个；随机语料使用固定种子20261013；不是统计显著性试验，也不是性能基准。
- 时间线0/3/5/8秒为明示模型设定；没有采集网络吞吐、真实故障恢复耗时或百台机器跑分。
- 平均值反例使用精确整数总和9、条数6，其正确平均值1.5。它是附加的摘要设计反例，不是把词频的主例中途改成平均词长。
- 12→9仅是中间键值对条数，正文不据此声称通信字节精确减少25%。
- 局部合并在教学模型中每个map恰好进行一次；该固定安排不是对所有生产框架调度次数的承诺。
- “只采用一次完整尝试”在本地程序中是字典选择模型，不是分布式原子提交协议的实现或验证。

## AI辅助与原创性说明

本文使用OpenAI的AI助手辅助一手资料检索、结构组织、中文写作、Python代码、程序化教学图和复算检查。没有人类亲访机房、亲测百台集群或与论文作者对话的经历主张。机架照片来自真实摄影者的原文件；未生成或改造为伪历史照片。

正文、原创图、封面和人工语料为CC BY 4.0；两个Python脚本为MIT许可，完整条款见licenses/MIT.txt。第三方论文、照片、商标及来源站点内容不随正文自动获得新授权。除开放许可照片和许可文本外，未将第三方论文原件、源站页面或图版作为本文附件重分发。
