# # 一位 DAC：把声音存进密度里

1990 年代的 CD 机上印着「1 bit」，而 CD 的规格是 16 bit。这一篇解释那个标签为什么不是营销话术：一位量化精度极低，但把它跑快 64 倍、再用一个反馈环把误差推到高频去，就能得到比 CD 更好的信噪比。从量化台阶、过采样、噪声整形讲到抽取滤波、空闲音、抖动和真实的芯片。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png
```

两个脚本都是确定性的，重跑得到逐字节相同的图。`run_model.py` 只用标准库（自写 radix-2 FFT 与自写 LCG）；`build_figures.py` 需要 Pillow（3.14.7 / 12.3.0，见 `examples/run-environment.json`）。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，19 张图按出现顺序编号 |
| `assets/01..19-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `originals/` | 四张 Commons 原图，未改动 |
| `examples/dsigma.py` | 模型：量化器、一/二阶环路、FFT、SNR/SINAD、抖动、抽取 |
| `examples/run_model.py` | 写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |

## 关于数字

正文里每一个数都来自 `examples/results.json`；图也一样。模型是行为级的：理想积分器、理想比较器，没有电路噪声，没有开关电容的非理想性。所以模型给出的 45.0 / 69.3 dB 比教科书公式低 12–16 dB，而这个差距本身也是正文的一部分——`sources.md` 里写明了哪些是设定值、哪些没算、哪些没验证。
