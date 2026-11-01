# 一行代码算出 1/√x

1999 年 Quake III 的源码里有三行看不懂的代码：一次整数移位、一次整数减法，就给出平方根倒数的近似值，误差 3.4%。这一篇把那个常数 `0x5f3759df` 拆开，从 float32 的位布局讲到牛顿迭代，说明它为什么长这样，以及今天它还剩下什么。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png
```

两个脚本都是确定性的，重跑得到逐字节相同的图。`run_model.py` 只用标准库；`build_figures.py` 需要 Pillow（3.14.7 / 12.3.0，见 `examples/run-environment.json`）。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，21 张图按出现顺序编号 |
| `assets/01..21-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `originals/` | 四张 Commons 原图，未改动 |
| `examples/rsqrt.py` | 模型：float32 位运算、log₂ 近似、牛顿迭代、误差扫描 |
| `examples/run_model.py` | 写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |

## 关于数字

正文里每一个数都来自 `examples/results.json`；图也一样。模型按 IEEE-754 float32 规范逐步舍入，但没有模拟 x87 的 80 位中间结果。正文里那句"一帧 3 ms 对 55 ms"是量级估计，不是实测——`sources.md` 里写明了哪些是设定值、哪些没算、哪些没验证。

## 许可

正文与原创插图：CC BY 4.0。
四张 Commons 照片：CC BY 2.0 ×2、Public domain、CC BY 3.0，见 `sources.md`，不受正文许可覆盖。
代码：MIT，见 `LICENSE-CODE.txt`。
