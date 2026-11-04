# 先拿哪个数当除数

两个方程、两个未知数，一支三位有效数字的账本给出的答案是 (0, 1)。代回第一个方程成立，代回第二个差了整整一倍。题没错，公式没错，错的是第一步选了哪个数当除数。这一篇从这组 4 个字符长的数字出发：先手算一个三位有效数字的例子，再手算一个 3×3 的整数例子，然后回答三个问题——为什么必须换行、为什么换到绝对值最大的那行、以及它为什么救不了病态问题。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 75 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 4 秒）
```

两个脚本都是确定性的，重跑得到逐字节相同的图与数字。`run_model.py` 只用标准库：精确算术用 `fractions.Fraction`，有限位算术自己做「按有效数字舍入」，单精度用 `struct` 打包解包，随机矩阵用 `random.Random(seed)`。

`run_model.py` 里最慢的一段是枚举 4 阶 ±1 矩阵（65 536 个，每个都做一次精确消元），占掉七成时间。不需要那两行数字的话，删掉 `pm1` 那段就回到几秒。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，18 张图按出现顺序编号 |
| `assets/01..18-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `examples/ge.py` | 模型：精确/有限位/单精度三套消元、增长因子、Hilbert 矩阵、条件数 |
| `examples/run_model.py` | 写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |
| `examples/figkit.py` | 画图小工具（几何断言、字号换算） |

## 关于数字

正文里每一个数都来自 `examples/results.json`，图也一样。三处可以手算复核：

1. 三阶例子 `toy`：消元后 `−3x1 − x2 + 2x3 = −11`、`5/3·x2 + 2/3·x3 = 13/3`、`1/5·x3 = −1/5`，回代得 (2, 3, −1)，代回三个方程精确成立。
2. 三位有效数字的例子 `cancel`：真解 1.00010001…，不换行得 (0, 1)，换行得 (1, 1)。
3. 条件数的几何 `sensitivity`：位移 = 扰动 / tan(夹角)，0.001 / tan(0.03°) = 1.90986。

模型没做的事：完全主元、稀疏与分块实现的实测性能、复数、对称正定矩阵的 Cholesky。`dgesv` 那张图是流程示意，不是速度曲线。`sources.md` 里逐条写明哪些是设定值、哪些没算、哪些是文献背景。
