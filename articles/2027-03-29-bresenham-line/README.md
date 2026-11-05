# 半个像素算谁的

一条斜线在大部分列上只有一个正确像素，但当理想高度正好落在半整数上，两个像素一样近——这种平局不是数值误差，而是真要选一个。这一篇只问「平局怎么办」，量它的三个后果：同一个算法按整数格点量偏差不超过 0.5、按像素中心量能到 1.49；4000 条随机线段里 23% 与四舍五入给出不同像素，而且只差在长度为偶数的那些线上；把端点顺序换一下，三分之一的线段会变——这正是今天 GPU 要写「左上规则」的原因。顺带看圆的平局、Wu 抗锯齿怎么把平局摊成灰度，以及 1962 年 CalComp 绘图仪上的那笔账。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

误差项的推导与历史在库里另有一篇讲透了：[画一条直线，为什么只要加减法？](../2026-10-11-bresenham-error-ledger/read.md)。本篇只在开头留一张手算表当锚，不重推。

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 0.2 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 2 秒）
```

两个脚本都是确定性的，重跑得到相同的数字与图（`results.json` 21 055 字节，md5 `4eb25ec23fcde1fb01c015874e2a4c87`）。只需标准库（画图另需 Pillow）：画线、圆、DDA 对照全是整数或 float64，不用 NumPy，也没有计时。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，10 张图按出现顺序编号 |
| `assets/01..10-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `examples/bres.py` | 画线、误差项轨迹、浮点 DDA 对照、中点圆、Wu 覆盖度 |
| `examples/run_model.py` | 跑全部实验，写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |
| `examples/figkit.py` | 画图小工具（几何断言、字号换算） |

`bres.py` 的主要入口：

- `bresenham(x0, y0, x1, y1)`：第一八分圆的核心循环，外面按轴交换和符号翻转套用。判据是 `d > 0`（平局留在原行）。
- `err_trace(x0, y0, x1, y1)`：同一条线的误差项逐步取值，给正文的手算表用。
- `dda_round(x0, y0, x1, y1)`：浮点参考——每列重算精确高度再四舍五入。注意用的是 Python 的 `round`，平局**取偶**，不是「一律进位」。
- `dev_integer(pts, ...)` / `dev_center(pts, ...)`：两种偏差度量。前者在整数坐标上比，后者在像素中心上比。
- `midpoint_circle(r)` / `circle_round(r)`：中点圆与「每列四舍五入」的圆，用来数像素数和径向误差。
- `wu_coverage(x0, y0, x1, y1)`：Wu 1991 的覆盖度，返回 `{(x, y): 0..255}`。
- `lcg(seed)` / `rand_segments(count, seed)`：确定性随机线段，不依赖 `random` 的实现。

## 关于数字

正文里每个数都来自 `examples/results.json`，图也一样。数的是**像素、偏差与计数**，不是耗时。七处可以手算复核：

1. 手算表：D₀ = 2×4 − 10 = −2；第 1 列 −2 + 8 = 6 > 0，行号加一、D = 6 − 20 + 8 = −6。11 列逐行对得上。
2. 周期 5 列：5 × 2Δy = 40 = 2 × 2Δx，即 Δx/gcd(Δx, Δy)。
3. 判据式 D_k = 2Δx[理想(k+1) − (y_k + 0.5)]：第 1 列 2×10×(0.8−0.5) = 6，第 2 列 2×10×(1.2−1.5) = −6。
4. 平局的条件：2Δy·k ≡ Δx (mod 2Δx) 左边是偶数，Δx 为奇数时无解。手算那条线（Δx = 10、Δy = 4）8k ≡ 10 (mod 20) 无解，所以它和四舍五入完全一致。
5. (0,0)→(4,2)：两个平局在 k = 1 和 k = 3，Bresenham 与四舍五入差在 k = 3 一处；反向画差在两处。
6. 中心度量 1.49 = 0.5（平局）+ 0.5（中心比格点偏半格）+ 0.5 × 65/66。
7. 中点圆 r = 13 的第一八分圆 10 个点，从 (0,13)、d = −12 起，逐步加 2x+1 或 2(x−y)+1。

模型没做的事：没有测耗时、没有量浮点增量版本的误差累积、没有实现其他画线算法（Gupta–Sproull、supercover 等）、没有模拟真实 GPU 光栅化器、没有给出半径更大时比值收敛的解析式。`sources.md` 里逐条写明。

## 许可

正文与图：CC BY 4.0。代码（`examples/` 下所有 `.py`）：见 [LICENSE-CODE.txt](LICENSE-CODE.txt)。
