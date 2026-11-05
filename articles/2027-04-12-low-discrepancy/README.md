# 一千个点能有多准

撒点法估面积，误差按 1/√N 缩小——想让误差小十倍，就得扔一百倍的点。这一篇把「点还能更顶用一点吗」这个问题走完：用可以手算的 16 个点起步（van der Corput 序列，二进制位反转），量出随机点、抖动网格、Halton、Halton 平移四种做法的收敛指数（0.49 / 0.69 / 0.78），再讲清它的两个脾气——遇到跳变的被积函数只到 0.78 而不是 1，以及它根本不告诉你自己有多准（N 与 4N 可能给出同一个估计值，8192 个点的答案甚至比 16384 个点更准）。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 2 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 3 秒）
```

两个脚本都是确定性的，重跑得到相同的数字与图（`results.json` 43 051 字节）。只需标准库（画图另需 Pillow）：不用 NumPy，不用 `random` 模块，没有计时。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，9 张图按出现顺序编号 |
| `assets/01..09-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `examples/qmc.py` | 点集生成、积分估计、最大空洞、指数拟合 |
| `examples/run_model.py` | 跑全部实验，写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |
| `examples/figkit.py` | 画图小工具（几何断言、字号换算） |

`qmc.py` 的主要入口：

- `radical_inverse(n, base)` / `van_der_corput(count, base)`：基数反转，1 起编号。
- `halton(count, dims)`：第 j 维用第 j 个素数（2, 3, 5, 7…）。
- `random_points(count, dims, seed)`：64 位线性同余，取高 53 位。
- `stratified(count, seed)`：k×k 抖动网格，count 必须是完全平方数。
- `shifted(points, shift)`：Cranley–Patterson 平移，逐维模 1。
- `estimate_pi_over_4(points)` / `inside(xs)`：被估的积分，只看前两维。
- `max_gap(vals)`：一维最大空洞，含两端。
- `fit_exponent(ns, errs)`：log-log 最小二乘斜率。

## 关于数字

正文里每个数都来自 `examples/results.json`，图也一样。数的是误差、比值、收敛指数与点数，不是耗时。可手算复核的地方：

1. van der Corput 前 8 项：1/2、1/4、3/4、1/8、5/8、3/8、7/8、1/16（二进制位反转）；前 8 项在 8 个 1/8 格里各一个。
2. 标准差：√(0.168536/1024) = 0.012830，实测 0.013812；√(0.168536/16384) = 0.003208，实测 0.003301。
3. 端点斜率：log(9.20e−2/3.30e−3)/log(1024) = 0.48；抖动网格 0.674；Halton 平移 0.769。
4. 重复比值：26/32 = 104/128 = 0.8125；51/64 = 204/256 = 0.796875；806/1024 = 1612/2048 = 3224/4096 = 0.787109375；减去 π/4 = 0.785398163 得 0.027102、0.011477、0.001711。
5. 最大空洞：van der Corput 前 2^k 项严格为 2^−k；随机点 32 组平均是 log n / n 的 1.08 倍（n = 1024、16384）。
6. n = 1024 的误差散布：最小 2.4e−4，最大 3.6e−2，均值 9.87e−3，RMS 1.23e−2。

模型没做的事：没有推导收敛率；没有解释「分子四倍」的机制（只核实它是可重算的事实）；没有实现 Sobol 或 Owen 加扰；没有做高维实验；没有测耗时；没有在真实渲染器里跑过；没有读过 van der Corput 1935 原文。`sources.md` 里逐条写明。

## 许可

正文与图：CC BY 4.0。代码（`examples/` 下所有 `.py`）：见 [LICENSE-CODE.txt](LICENSE-CODE.txt)。
