# 国际象棋搜索：可复算材料

正文：[read.md](read.md)。来源与许可：[sources.md](sources.md)。

这是一套完整的国际象棋走法生成与搜索程序，以及正文全部数字的测量脚本。它不是引擎，没有开局库、残局库、迭代加深、空着剪枝或任何硬件加速，也没有针对棋力调过参。它的用途是让正文里每一个节点数、每一个评分、每一步历史说法都能被重新跑出来。

## 运行

环境记录见 [run-environment.json](examples/run-environment.json)。数值程序只用 Python 标准库；绘图另需 Pillow 与一款中文字体。

在本篇目录中执行：

```sh
python examples/measure.py          # 走法生成校验 + 搜索测量（约 20 分钟）
python examples/horizon.py          # 地平线与静止搜索（约 2 分钟）
python examples/build_figures.py    # 重绘全部正文图与封面
```

`measure.py` 会把结果写到 `examples/measurements.json`，`horizon.py` 写到 `examples/horizon.json`。首次制作时的原始标准输出保存在 `originals/model-stdout.txt`。

绘图程序会按以下顺序寻找中文字体：

```text
/System/Library/Fonts/Hiragino Sans GB.ttc        （macOS）
/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc   （Linux）
/Library/Fonts/Arial Unicode.ttf
/System/Library/Fonts/STHeiti Medium.ttc
```

找不到任何一款时程序会直接报错，不会退回默认字体。棋子符号单独从 Arial Unicode MS 或 Apple Symbols 取，程序会先检查该字体是否真的有这些字形（`glyph_available()`）。

## 五个范围明确的实验

### 1. 走法生成正确性（perft）

用公开的标准测试局面校验走法生成器，包括王车易位、吃过路兵、升变、被将时不能易位等规则。

| 局面 | perft(1) | perft(2) | perft(3) | perft(4) |
|---|---|---|---|---|
| 初始局面 | 20 | 400 | 8,902 | 197,281 |
| Kiwipete | 48 | 2,039 | 97,862 | — |
| 残局局面 3 | 14 | 191 | 2,812 | 43,238 |

全部与公开基准值一致。这是本文唯一与外部已知数值直接比对的实验。

### 2. 极小化极大与 α-β 的节点数

同一局面 `r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq -`，同一评估函数（子力价值 + 兵/马位置表），深度 1—6。同时记录两者选出的走法与分数，用来验证"剪枝不改变答案"。

### 3. 走法顺序

三种排序在同一深度下的节点数：生成顺序（`order='none'`）、MVV-LVA 吃子优先（`order='captures'`）、同分打乱（`order='shuffle'`）。

### 4. 置换表与 Zobrist

深度 4—6 在有表与无表下的节点数、探测数、命中数。另外用 16 步真实着法序列逐步比较增量键与重算键，并用 4,000 步随机走子得到的 3,045 个局面检查碰撞。

碰撞检查**不是**碰撞概率的证明。64 位空间里的碰撞概率极低但不为零；本文的模型假设不碰撞，这个假设只在本文的实验范围内成立。

### 5. 地平线与静止搜索

两个真实局面上深度 2—5 的评分，以及加静止搜索后同一深度的评分与节点数。静止搜索只展开吃子走法，不展开非吃子走法，因此不会无限递归。

## 文件

- [chesslib.py](examples/chesslib.py)：棋盘表示、走法生成、合法性判定、FEN 解析、SAN 记谱、perft。
- [engine.py](examples/engine.py)：评估函数、极小化极大、α-β、走法排序、Zobrist、置换表、静止搜索。
- [measure.py](examples/measure.py)：实验 1—4，输出 `measurements.json`。
- [horizon.py](examples/horizon.py)：实验 5，输出 `horizon.json`。
- [figkit.py](examples/figkit.py)：绘图工具。每张图在保存前会检查文字是否出画布、是否越出所声明的框、是否互相重叠、字号是否低于下限、文字与背景的对比度是否够读。
- [build_figures.py](examples/build_figures.py)：全部正文图与封面。

## 限制

程序没有实现迭代加深、空着剪枝、主变例搜索、杀手走法、历史启发、开局库、残局库、多线程或任何硬件加速，评估函数也没有调过参。正文所有"秒数"都是这套纯 Python 实现在本文机器上的耗时，不能外推为其他实现或深蓝的性能。

`horizon.json` 中深度 5 的静止搜索要跑半分钟以上，`measure.py` 全量运行约 20 分钟，其中极小化极大深度 4 一项就占 3 分钟。

## 许可

原创文字、原创图与原创实验数据：CC BY 4.0。原创代码：MIT，完整文本见 [LICENSE-CODE.txt](LICENSE-CODE.txt)。第三方照片、论文与外链资料保留各自权利，不因本篇许可而变成 CC BY 材料；第三方照片的许可与处理说明见 [sources.md](sources.md)。
