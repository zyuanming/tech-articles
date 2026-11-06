# # 2^53 上再加 1，等于没加

`s += x` 循环一亿次，是最不可能写错的代码，也是最容易静悄悄给出错答案的代码：和到了 2^53 这个量级，1 就等于两个刻度正中间的一点，舍入之后消失。这一篇从两个能心算的例子起步（2^53 加 1 不动；`[1, 1e16, −1e16]` 精确值为 1 而直接相加得 0），再看 Kahan 1965 年那四行怎么把丢掉的那一点单独存起来，Neumaier 1974 年补的是哪一处漏洞，然后量化三件事：百万项调和级数上直接相加差 7.4e−13、补偿求和逐位精确；同一批数只换加法顺序，直接相加的误差差 15 倍；20000 组抵消测试里 Kahan 有 263 组比直接相加还差。最后是它救不了的边界——1e16 + 0.01 在双精度里就是 1e16，换什么算法都一样。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 2 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 3 秒）
```

两个脚本都是确定性的，重跑得到相同的数字与图（`results.json` 6968 字节）。只需标准库（画图另需 Pillow）：全部是 float64 运算，不用 NumPy，也没有计时。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，9 张图按出现顺序编号 |
| `assets/01..09-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `examples/kahan.py` | 五种求和、三种方差、测试数据生成、运算次数计数 |
| `examples/run_model.py` | 跑全部实验，写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |
| `examples/figkit.py` | 画图小工具（几何断言、字号换算） |

`kahan.py` 的主要入口：

- `naive(xs)`：`s += x`，基线。
- `kahan(xs)`：`y = x - c; t = s + y; c = (t - s) - y; s = t`，返回 `s`。
- `neumaier(xs)`：`|s| ≥ |x|` 时 `c += (s - t) + x`，否则 `c += (x - t) + s`，返回 `s + c`。
- `pairwise(xs)`：分治两两相加，长度 ≤ 32 时退回 `naive`。
- `exact(xs)`：`math.fsum`，参照值。
- `variance_onescan` / `variance_twopass` / `variance_welford`：三种方差。
- `ops_per_term()`：静态计数，每个数在内循环里花几次四则运算；不是耗时。
- `lcg(seed)` / `harmonic(n)` / `wide_positive(...)` / `noisy_offset(...)` / `cancel_mix(...)`：确定性测试数据。

## 关于数字

正文里每个数都来自 `examples/results.json`，图也一样。数的是**误差、比例与运算次数**，不是耗时。八处可以手算复核：

1. 2^53 处 ulp = 2^53 × 2^−52 = 2，加 1 是半个 ulp，取偶后不动；加 2 才前进。
2. `[1, 1e16, −1e16]` 的 Kahan 第二行：`t = 1 + 1e16` 舍入到 1e16；`t − s = 1e16 − 1` 也舍入到 1e16（该量级 ulp 是 2），于是 `c = 0`，那个 1 掉了两次。
3. Neumaier 同一行走另一支：`(x − t) + s = (1e16 − 1e16) + 1 = 1`，c 保住。
4. n = 1000 的直接相加误差 1.776e−15 = 2 个 ulp（7.4854 处 ulp = 8.88e−16）；n = 1000000 的 7.354e−13 约 413 个 ulp。
5. 精确率：17249/20000 = 86.245%，18420/20000 = 92.1%，19987/20000 = 99.935%；263/20000 = 1.315%。
6. 一次扫算方差：Σx² ≈ 1e19 处 ulp = 2048，除以 n = 1000 后每次舍入贡献约 2，实测误差 8.97 约 4 个 ulp。
7. 1e16 + 0.01：0.01 < ulp/2 = 1，舍入回 1e16；`math.fsum` 也是 1e16。
8. 一百万个倒数和换四种顺序，直接相加 7.354e−13 / 4.796e−14 / 7.194e−13 / 4.796e−14，Kahan 全为 0。

模型没做的事：没有测耗时；没有实测 `-ffast-math`；没有实现 Shewchuk 的无损变换（只调用 `math.fsum`）；没有做并行归约或 GPU 实验；没有给出误差界推导；没有覆盖 long double、Double-double、浮点异常；没有测 NumPy、C 或 SIMD 实现。`sources.md` 里逐条写明。

## 许可

正文与图：CC BY 4.0。代码（`examples/` 下所有 `.py`）：见 [LICENSE-CODE.txt](LICENSE-CODE.txt)。
