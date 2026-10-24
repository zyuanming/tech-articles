# 来源与许可

## 事实与机制

- Michael Burrows、David J. Wheeler，*A Block-sorting Lossless Data Compression Algorithm*，Digital Systems Research Center Research Report 124，1994-05-10。[原报告的大学保存副本](https://www.eecs.harvard.edu/~michaelm/CS222/burrows-wheeler.pdf)。支持分块排序变换、逆变换和后续编码的原始出处。本文不是原报告翻译；BANANA$、稳定匹配的逐步说明、逐列重建及反例为独立教学构造。本文以唯一最小结束标记固定旋转起点，未实现原报告或现成压缩器的完整文件格式。
- 本文的正确性解释由循环旋转、字典顺序、同字稳定次序直接推出；有限实验见 `examples/verify.py` 和 `results.json`，不是压缩器性能测试。没有引用或重印原论文图、表、原文长段落；原链接供读者查阅。

## 图片逐项说明

所有图片均由本篇 `examples/build_figures.py` 独立绘制，作者为本仓库文章创作团队，采用 CC BY 4.0。没有第三方照片、人物肖像、软件界面或实验装置照片；矩阵和图形是明确标注的教学示意，不是历史原稿。

| 文件 | 内容与新增理解作用 | 数据与改动 |
|---|---|---|
| assets/01-order.png | 普通排序碰撞与可逆重排的差异 | 自拟字符串，原创 |
| assets/02-rotations.png | 七个旋转起点及完整字符排列 | results.json，原创 |
| assets/03-sorted.png | 排序矩阵与首尾列 | results.json，原创 |
| assets/04-two-columns.png | 从L重建F | results.json，原创 |
| assets/05-stable-match.png | 相同字符按出现次序认领 | results.json，原创 |
| assets/06-predecessor.png | 移尾到头保持同组相对次序 | results.json，原创 |
| assets/07-inverse-walk.png | 七步LF逆读 | results.json，原创 |
| assets/08-roundtrip.png | 倒读结果反转后还原 | results.json，原创 |
| assets/09-table-rebuild.png | 朴素逐列重建前三轮 | results.json，原创 |
| assets/10-mtf.png | 动态列表的前三次位置编码 | results.json，原创 |
| assets/11-noncompression.png | 无重复输入的反例 | results.json，原创 |
| assets/12-blocks.png | 分块改变循环邻接范围 | 自拟边界示意，原创 |
| assets/13-verification.png | 穷举范围与实际通过数 | results.json，原创 |

原创正文和上述原创图片采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名 zyuanming / tech-articles，转载须保留原链接并注明修改。一手文献本身、其图表及相关商标不因此获得再授权。

`examples/` 下独立编写的 Python 代码采用 MIT，完整许可见 `examples/LICENSE`。复现：Python 3 执行 `python examples/verify.py`；绘图另需 Pillow、fontTools 和 Noto Sans CJK 字体，再执行 `python examples/build_figures.py`。输入、测试范围及运行版本记录在结果文件，未计真实压缩文件的字节开销。

AI辅助：本文的研究梳理、中文起草、代码和教学图由 AI 辅助完成；数学小例与程序输出实际核对。未虚构访谈、亲历或历史照片。
