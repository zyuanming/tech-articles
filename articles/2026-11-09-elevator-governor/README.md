# 电梯怎么知道自己太快了

限速器、限速绳、安全钳：一台电梯在钢丝绳失效以后，怎么用纯机械的方式把自己钉在导轨上。全文围绕一个 2.01 m/s 的触发点，把离心力、弹簧、楔块自锁和 230 毫秒的反应链拆开算一遍。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png
```

`run_model.py` 只用标准库；`build_figures.py` 需要 Pillow（3.14.7 / 12.3.0，见 `examples/run-environment.json`）。两张脚本都是确定性的，重跑得到逐字节相同的图。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，18 张图按出现顺序编号 |
| `assets/01..18-*` | 正文用图（1062 px 宽）与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `originals/` | 四张 Commons 原图，未改动 |
| `examples/elevator.py` | 模型：限速器、仿真、楔块、能量 |
| `examples/run_model.py` | 写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |

## 关于数字

正文里每一个数都来自 `examples/results.json`；图也一样。参数是"常见电梯的量级"，不是某一款产品的实测数据，也不是规范值。哪些是设定值、哪些是推导值，`sources.md` 里逐条写了。

## 许可

正文与原创插图：CC BY 4.0。
四张 Commons 图片：各自的许可（CC BY 4.0 / 公有领域 ×3），见 `sources.md`，不受正文许可覆盖。
代码：MIT，见 `LICENSE-CODE.txt`。
