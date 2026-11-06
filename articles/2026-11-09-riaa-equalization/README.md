# # 先砍 19 dB，再加回来

黑胶上那条 RIAA 曲线。刻片时低音被砍掉 19 分贝、高音被提起 20 分贝，放音时再原样倒回去。全文围绕一个问题：为什么要先动手脚，而不是直接刻？

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png
```

`run_model.py` 只用标准库；`build_figures.py` 需要 Pillow（3.14.7 / 12.3.0，见 `examples/run-environment.json`）。两个脚本都是确定性的，重跑得到逐字节相同的图。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，18 张图按出现顺序编号 |
| `assets/01..18-*` | 正文用图（1062 px 宽）与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `originals/` | 四张 Commons 原图，未改动 |
| `examples/riaa.py` | 模型：曲线、振幅、槽距、噪声、容差 |
| `examples/run_model.py` | 写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |

## 关于数字

正文里每一个数都来自 `examples/results.json`；图也一样。模型是理想化的：槽距按最大振幅统一定，刻片头行程、唱针接触力学都没有建模。哪些是设定值、哪些是推导值、哪些没算，`sources.md` 和正文最后一节逐条写了。

## 许可

正文与原创插图：CC BY 4.0。
四张 Commons 图片：CC BY-SA 2.0 / CC BY 2.0 / CC0 ×2，见 `sources.md`，不受正文许可覆盖。
代码：MIT，见 `LICENSE-CODE.txt`。
