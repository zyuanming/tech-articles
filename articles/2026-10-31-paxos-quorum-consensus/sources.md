# 来源与素材

## 一手文献

- Leslie Lamport, *The Part-Time Parliament*, ACM Transactions on Computer Systems 16(2),
  May 1998, pp. 133–169. DOI: [10.1145/279227.279229](https://doi.org/10.1145/279227.279229)。
  本文关于两阶段协议、承诺语义、编号顺序的表述以此文为准。（卷期页经 Crossref 元数据核对。）
- Leslie Lamport, *Paxos Made Simple*, ACM SIGACT News 32(4), Dec. 2001, pp. 51–58。
  文中「取编号最大的已接受值」这一简化表述主要依据此文。
- Leslie Lamport, *The Part-Time Parliament*, DEC Systems Research Center 技术报告, 1990。
  这是 1998 年正式发表前的流通版本。
- Tushar Chandra, Robert Griesemer, Joshua Redstone, *Paxos Made Live: An Engineering
  Perspective*, PODC 2007。第 21 节关于磁盘损坏、成员变更、快照的经验来自此文。

## 事实核对说明

- 图灵奖年份（2013）、LaTeX 的作者身份、帕克索斯岛的地理位置与面积（约 25.3 km²，
  主镇盖奥斯）来自公开百科条目。
- 「论文曾被搁置、审稿人未看出价值」的说法在二手叙述中广泛流传，本文按「流传的说法」
  措辞，未当作已核实的一手事实。
- 副本数 2 : 2 : 1 的跨机房分配、奇数台部署属于工程惯例，不是 Paxos 论文的规定。

## 图片

24 张示意图由 `examples/build_figures.py` 生成，属原创教学示意。图内的消息编号、
时间、统计量读自 `examples/results.json`；第 15 节（活锁）是构造的调度，图内已标注
「构造的调度」，不冒充模拟输出。

两张照片：

| 文件 | 内容 | 作者 | 许可 | 原页 |
| --- | --- | --- | --- | --- |
| `assets/25-leslie-lamport.jpg` | Leslie Lamport 肖像 | Leslie Lamport | Copyrighted free use | [File:Leslie Lamport.jpg](https://commons.wikimedia.org/wiki/File:Leslie_Lamport.jpg) |
| `assets/24-paxos-island.jpg` | 帕克索斯岛全景 | Arxoland | CC BY-SA 4.0 | [File:Paxos island, Greece.JPG](https://commons.wikimedia.org/wiki/File:Paxos_island,_Greece.JPG) |

两张照片只做了等比缩放、裁切（岛景裁掉上下留白）与加注署名条，未修改画面内容。
原图保存在 `originals/`，未做任何处理。

## AI 辅助说明

正文由作者撰写，绘图代码、模拟器与数据由作者编写并实际运行。没有任何图是绘图模型生成的，
没有使用生成式图像。第 15 节的示意图由代码绘制，但消息序列是人工构造的教学调度，
这一点在图内、README 与本节均已注明。
