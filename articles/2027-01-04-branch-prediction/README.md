# # 一条 if 值多少拍

一条 `if` 要等几个拍子才知道结果，而 CPU 不愿意等。于是它赌：先按猜的方向把后面的指令搬进流水线，猜错了再扔掉。这篇文章讲这个赌注——为什么非赌不可、怎么赌得更准、赌错一次值多少。

七种预测器（两种静态、一位计数器、两位计数器、局部历史、gshare、锦标赛）在同一批合成 trace 上跑，数字全部来自 `examples/bp.py`，跑一遍不到一秒。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 0.1 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 4 秒）
```

`run_model.py` 只用标准库（随机 trace 生成、七种预测器、扫描与成本模型）。`build_figures.py` 需要 Pillow（3.14.7 / 12.3.0，见 `examples/run-environment.json`）。两个脚本都是确定性的，重跑得到逐字节相同的图。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，19 张图按出现顺序编号 |
| `assets/01..19-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `originals/` | 一张 Commons 原图（Wolfdale 裸片），未改动 |
| `examples/bp.py` | 模型：七条 trace、七种预测器、历史长度阶梯、别名实验、成本模型 |
| `examples/run_model.py` | 写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `examples/figure-metadata.json` |
| `examples/figure-metadata.json` | 每张图的尺寸、字号下限、用途与身份（19 行，按 `path` 排序） |
| `examples/figkit.py` | 画图用的几何引擎（画布宽度、安全边带、字号下限的检查都在这里） |

## 关于数字

正文和图里的每个数字都由 `examples/bp.py` 算出。几个可以手算复核的：

- `loop10` 是「跳 10 次、退出一次」重复 60 轮，共 660 个分支。一位计数器每轮错两次（退出、下一轮第一步），2/11 = 18.2%；两位只错退出那一次，1/11 = 9.1%，实测 9.4% 多出来的部分是开头两次冷启动。
- 别名实验是 64 个结果固定的分支、60 轮，共 3840 个执行。表够大（≥64 格）之后只剩冷启动错误：64 ÷ 3840 = 1.67%，正是曲线尾部停住的位置。
- 成本模型是 `CPI = 0.5 + 0.2 × 错判率 × 15`。错判率 5% 时 CPI = 0.65，也就是每周期 1.54 条；20% 时 CPI = 1.10，每周期 0.91 条，比单发射还慢。完全不猜、每次都等，则是 0.5 + 0.2 × 15 = 3.5，每周期 0.29 条。
- `correlated` 那条 trace 里 A 是真随机的，3000 个分支中 A 占一半，最好也错 750 个 = 25%。gshare 实测 30.5%，离这个下限只差 5.5 个百分点。

一处值得单说的结论：**没有哪个预测器在所有 trace 上都最好**。`switch8` 上「永远猜不跳」错 12.5%，比 gshare 的 14.3% 还好——因为 8 个分支里 7 个不跳，最笨的策略正好是最优策略。

`sources.md` 里写明了文字参考、那张照片的许可、每张图的数字来源、模型的简化假设，以及明确没做的事（没有对接真实硬件、没有给 TAGE 建模、没有目视看图）。
