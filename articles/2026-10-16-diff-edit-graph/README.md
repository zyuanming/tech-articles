# 差分算法：可复算材料

正文：[read.md](read.md)。来源与许可：[sources.md](sources.md)。

这是一份 Myers O(ND) 差异算法的实现，加一份 patience diff，加一份用来校验它们是否真的给出最短脚本的动态规划。它不追求工程性能：没有实现 O(N) 空间的改进版本，也没有覆盖 Git 的 histogram 变体。

## 运行

环境记录见 [run-environment.json](examples/run-environment.json)。全部代码只用 Python 标准库；绘图另需 Pillow 与一款中文字体。

在本篇目录中执行：

```sh
python examples/run_model.py        # 全部实验，写 results.json
python examples/build_figures.py    # 重绘全部正文图与封面
```

首次运行时的原始标准输出保存在 `originals/model-stdout.txt`。

绘图程序会按以下顺序寻找中文字体：

```text
/System/Library/Fonts/Hiragino Sans GB.ttc               （macOS）
/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc   （Linux）
/Library/Fonts/Arial Unicode.ttf
/System/Library/Fonts/STHeiti Medium.ttc
```

找不到任何一款时程序直接报错，不会退回默认字体。

## 算法

`myers.py` 按 1986 年论文实现贪心 O(ND)：

- 编辑图上每个位置的对角线编号是 `k = x − y`。
- 按 `D = 0, 1, 2, …` 逐层扩展，每层只保留 `k = −D, −D+2, …, D` 这些对角线上最远的 `x`。
- 每次从一个 D−1 层的邻居走一步（向右删、向下插），然后沿对角线一直滑到字符不同为止。
- 找到终点后，用逐层保存的状态回溯出编辑脚本。

`patience.py` 换了一个目标：

1. 找出在 A 和 B 里都恰好出现一次的行。
2. 取它们在 B 中位置的最长递增子序列，作为锚点。
3. 锚点之间的空隙交给 Myers。

## 四组实验

1. **正确性校验**：400 组随机小输入上，Myers 的脚本能重建出 B，且编辑长度等于动态规划的最优值；另有 300 组校验 patience。
2. **真实文件**：`originals/pairs/` 下两组公开仓库的真实修订，报告行数、增删数、编辑距离、对角线条数、比较次数，并与动态规划最优值对照。
3. **代价增长**：同一份 161 行文件插入 1/2/4/8/16 处新行；以及"文件和自己比"与"文件和打乱后的自己比"两个极端。
4. **patience 与 Myers 对比**：三组输入上的编辑距离、输出是否相同、比较次数、对角线条数；以及一个四万行文件的耗时对比。

另外穷举了几组小输入上"最短脚本一共有多少条"，用来说明最短不等于唯一。

## 实测得到的两条反直觉结论

- **在三组真实/经典输入上，patience 的输出与 Myers 完全相同**，元素比较次数降到 1/6 到 1/18。但在 20 万组随机小输入上，两者有 11.8% 给出不同的脚本，其中 6.4% 是 patience 的编辑脚本更长——锚点只会收紧解空间，所以它不可能更短。
- **比较次数少不等于跑得快**：四万行、8 处改动的输入上，patience 的比较次数是 0，挂钟时间却比 Myers 长——建索引、排序、求最长递增子序列本身要花时间。

这两条都写在正文里，没有为了叙事把它们藏起来。

## 文件

- [myers.py](examples/myers.py)：贪心 O(ND)、回溯、动态规划 LCS、unified diff 渲染、工作量计数。
- [patience.py](examples/patience.py)：唯一行锚点、最长递增子序列、递归。
- [run_model.py](examples/run_model.py)：全部实验，输出 `results.json`。
- [figkit.py](examples/figkit.py)：绘图工具。每张图在保存前会检查文字是否出画布、是否越出所声明的框、是否互相重叠、字号是否低于下限、文字与背景的对比度是否够读。
- [build_figures.py](examples/build_figures.py)：全部正文图与封面。
- `originals/pairs/`：两组真实文件修订原文（四个 `.py` 文件）。

## 限制

- 本文的实现保存每一层的对角线状态，内存是 O(D²)，没有实现论文里的 O(N) 空间版本。
- 没有实现 Git 的 histogram 变体，也没有实现 Git 实际的 diff 代码。
- 所有耗时都是纯 Python 在本机上的数字，不能与其他语言的实现比较。
- 正文里的"经典教学示例"是构造的 C 代码片段，不是任何论文的原始例子。
- **没有测量可读性。** 正文区分了两件事：patience 会改变答案（有实测数据），它是否让答案更好读（没有测，也不声称）。

## 许可

原创文字、原创图、封面与原创实验数据：CC BY 4.0。原创代码：MIT，完整文本见 [LICENSE-CODE.txt](LICENSE-CODE.txt)。第三方照片保留各自权利，许可与处理说明见 [sources.md](sources.md)。
