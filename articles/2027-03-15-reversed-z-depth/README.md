# # 深度缓冲只记得住 48 厘米

near = 0.1 米、far = 1000 米、24 位深度缓冲，900 米处一格有 48 厘米宽。这一篇从这个数字往回拆：深度值存的到底是什么（1/z 的一次重映射），为什么精度按距离平方衰减、为什么远平面几乎不参与、为什么 float32 的标准映射和 24 位定点逐位相同，把深度反过来存之后 900 米处的 48 厘米为什么变成 7.4 微米，以及「算完再减 1」和「预乘 view·projection」这两种常见写法各会吃掉多少。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 0.21 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 3.5 秒）
```

两个脚本都是确定性的，重跑得到相同的数字与图（`results.json` 46716 字节，md5 `512a7b9be288b603523494249d6b5bf4`）。只需标准库（画图另需 Pillow）：float32 舍入用 `struct.pack('<f', …)`，不依赖 NumPy，也不依赖平台的浮点格式——定点量化就是 `round(v * 2**24) / 2**24`。

`build_figures.py <N>` 可以只重画第 N 张，但那样会把 `examples/figure-metadata.json` 截断成一张，正式出图请整跑。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，12 张图按出现顺序编号 |
| `assets/01..12-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `examples/depth.py` | 深度映射、量化、格距、可见性、float32 矩阵流水线 |
| `examples/run_model.py` | 跑全部实验，写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |
| `examples/figkit.py` | 画图小工具（几何断言、字号换算） |

`depth.py` 的主要入口：

- `std_depth(z, n, f)` / `rev_depth(z, n, f)` / `gl_depth(z, n, f)`：标准 [0,1] 映射、它的 1 − d、以及 OpenGL 的 [−1,1] 版本。
- `q_fixed(v, bits=24)` / `q_float(v)`：把深度值量化成 24 位定点、float32。
- `eye_grid(z, n, f, depth, quant)`：该距离处的格距（米）。取该处深度值的 ULP（定点是 2 的 −24 次方）除以 |dd/dz|，导数用中心差分在双精度里算。
- `eye_step(z, …)`：从当前位置到下一个格边界的距离。它随相位在 0 到一个格距之间乱跳，只用来抽检 `eye_grid`。
- `merge_prob(z, sep, …)`：相隔 `sep` 的两个面在此距离处被压成同一个深度值的比例。
- `projection(n, f, reverse=True)` / `translate_z(t)` / `pipeline_pair(…)`：float32 的投影与视图矩阵，以及「预乘」与「分开乘」两条流水线的对比。

## 关于数字

正文里每个数都来自 `examples/results.json`，图也一样。数的是**深度值的格距、合并比例与顺序误差**，不是帧率或耗时。八处可以手算复核：

1. 映射本身：`d = f/(f−n) · (1 − n/z)`，n = 0.1、f = 1000 时系数是 1000/999.9 = 1.0001。z = 1 给 `1.0001 × 0.9 = 0.90009`，z = 500 给 `1.0001 × 0.9998 = 0.9999`，与 `depth_values` 一致。
2. 格距公式：Δz = 2 的 −24 次方 × (f−n)z²/(n·f) = 5.9605e-8 × 9.999 × z² = 5.96e-7·z²。z = 900 给 0.4828 米，`steps` 里是 0.48275。
3. float32 与定点的重合：float32 在 [0.5, 1) 里的间距是 2 的 −24 次方 = 5.9605e-8，与 24 位定点的格距是同一个数。`steps` 六行里 `fixed24` 与 `f32_std` 完全相同。
4. 远平面无关：`far_sweep` 六组（600 到 100 万米）落在 0.148987 到 0.149012 之间，因为因子 (f−n)/(n·f) 在 f 大时趋近 1/n。
5. 近平面线性：`near_sweep` 里 near 每乘 10，500 米处的格距除 10（0.05 → 298 毫米，0.5 → 29.8，5 → 2.97）。斜率 −1 的双对数直线。
6. 1 厘米的界限：5.96e-7·z² = 0.01 → z² ≈ 16778 → z ≈ 129.5 米，`threshold` 的 `z_guarantee` 是 129.53；`z_half`（格距涨到两倍间隙）是 183.19，正好是 129.53 × √2。
7. 开口那两堵墙：900 米处格距 0.48275 米，30 厘米的间隙有 `1 − 0.3/0.48275 = 0.3786` 的比例落在同一格，`merge_prob(900, 0.3, …)` 给 0.3786。
8. 反转的锯齿：反转存的值 s ≈ 0.1/z，float32 在 s 处的 ULP 每跨一个 2 的幂就翻倍，而 s 的斜率按 1/z² 变小，于是格距被拉成锯齿、包络仍按 z 增长。`steps` 里 900 米处 7.366e-6 米，`rev_worst` 的齿峰在 587 米、25.09 微米。

模型没做的事：没在真实 GPU 上跑、没测带宽与填充率、没做 MSAA 与深度压缩、没碰多层深度（layered depth）、没在引擎里验证、没分析阴影贴图与对数深度缓冲。所有「能不能分开」都是「两个深度值量化后是否相等」，不含视口变换、光栅化与逐样本解析。`sources.md` 里逐条写明哪些是文献、哪些是读了网页、哪些没做。

## 许可

正文与图：CC BY 4.0。代码（`examples/` 下所有 `.py`）：见 [LICENSE-CODE.txt](LICENSE-CODE.txt)。
