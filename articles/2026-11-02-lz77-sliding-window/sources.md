# 来源与素材

## 参考

- J. Ziv, A. Lempel, *A Universal Algorithm for Sequential Data Compression*,
  IEEE Transactions on Information Theory, IT-23(3), 1977, pp. 337–343。
  LZ77 的原始论文：本文的"距离 + 长度"、匹配的最短长度、以及"没有窗口限制"
  这一点都以此为准。
- J. Ziv, A. Lempel, *Compression of Individual Sequences via Variable-Rate Coding*,
  IEEE Transactions on Information Theory, IT-24(5), 1978。LZ78。
- T. A. Welch, *A Technique for High-Performance Data Compression*, IEEE Computer,
  17(6), 1984。LZW。
- P. Deutsch, *DEFLATE Compressed Data Format Specification version 1.3*, RFC 1951,
  1996。32768 的窗口、3–258 的匹配长度、以及距离/长度的霍夫曼编码都以此为准。
- J. Gailly, M. Adler, *gzip* 源码与文档（1992 起）。哈希链、懒匹配、块划分的
  工程实现。
- J. Ziv 的 IEEE Medal of Honor（2021）与 A. Lempel 的生平，取自 IEEE 与
  Technion 的公开公告。
- Brotli（RFC 7932, 2016）与 Zstandard（RFC 8878, 2021）的规范，用于时间线。

## 事实核对说明

- 1977 年论文的卷期页码按 IEEE Xplore 的公开记录写。
- "LZ77 原名并非 LZ77"——这个名字是后来为了和 LZ78 区分才叫开的；论文本身
  没有 77 这个编号。本文第 1 节写明了"1977 年那篇论文里没有窗口"。
- LZW 的专利争议（GIF / Unisys）按公开记载写，未核对诉讼文件。
- 时间线里的年份按公开资料表述，不精确到月份。

## 图片

17 张示意图与封面由 `examples/build_figures.py` 生成，属原创教学示意。
所有曲线与柱子的高度都从 `examples/results.json` 读取，没有手写数值。

两张真实肖像：

| 文件 | 内容 | 许可 | 原页 |
| --- | --- | --- | --- |
| `assets/02-lempel.jpg` | Abraham Lempel | CC BY 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:Abraham_Lempel.JPG) |
| `assets/03-ziv.jpg` | Jacob Ziv | 公有领域 | [Commons](https://commons.wikimedia.org/wiki/File:Jacob_Ziv.jpeg) |

处理方式：等比缩放到 620 高、加姓名与出处条。原图分别为 2381×2592 与 917×968。
原件在 `originals/`。

## 语料

`examples/corpus/alice.txt`（102832 字节）来自 Project Gutenberg 电子书 #11，
*Alice's Adventures in Wonderland*（Lewis Carroll, 1865），公有领域。截取第一章，
在段落边界处截断，未做其它改动。

## 缺口

- 没有 Lempel 与 Ziv 的合影，也没有两人在 Technion 的工作照。
- 没有 1977 年论文的扫描页（IEEE 版权，不便转载）。
- 没有 LZW 专利文件、也没有 PKZIP 的早期版本截图。
- 没有真实服务器日志：日志语料是合成模板，规模 24000 字节。

## AI 辅助说明

正文由作者撰写，编码器、测量与绘图代码由作者编写并实际运行。没有使用生成式
图像模型；两张肖像是真实照片，许可与出处如上。
