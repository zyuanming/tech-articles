# 可复算说明

正文里每个数字都从这里来：折线误差、覆盖率误差、竖笔在八个字号下的墨量、
hinting 前后的粗细变化、gamma 表、距离场重建的误差。

## 跑一遍

```sh
python3 examples/run_model.py       # 全部测量 -> examples/results.json
python3 examples/build_figures.py   # 21 张正文图 + cover.png
python3 examples/photos.py          # 两张照片的版式（需要 originals/）
```

要求：Python 3.10+，绘图需要 Pillow。除 Pillow 外只用标准库。

单独重画某张图：`python3 examples/build_figures.py 07`。

## 文件

| 文件 | 作用 |
| --- | --- |
| `examples/glyph.py` | 光栅化器：贝塞尔、折线化、扫描线填充、覆盖率、hinting、距离场 |
| `examples/run_model.py` | 跑全部测量，写 `results.json` |
| `examples/figkit.py` | 画图工具（MIT），自带字号与越界自检 |
| `examples/build_figures.py` | 21 张示意图与封面 |
| `examples/photos.py` | 照片合成与署名 |
| `examples/results.json` | 全部测量结果 |
| `originals/` | 两张 Wikimedia 原图，未经修改 |

## 字形是编出来的，不是从字体里取的

`O` 是 8 段二次贝塞尔拼的圆环，`I` 是三个矩形。坐标写在 `glyph.py` 里，
单位是 em（字高为 1），y 轴向下。

这样做的好处是每一步都能看清：你能看到控制点在哪、折线切了几刀、覆盖率怎么算。
代价是它们不是真字体：真实的汉字有十几条轮廓、笔画交叉、极窄的缝隙，
hinting 也不是「就近对齐」这么简单。

## 四件要说清楚的事

1. 覆盖率用的是 N×N 超采样，不是解析面积积分。FreeType 用解析/半解析方法，
   更快更准，但数学目标相同。
2. hinting 只实现了「就近对齐」这一种策略。真实的 TrueType hinting 是一段字节码，
   可以按字号判断、移动单个点、改笔画宽度。
3. gamma 表用的是 sRGB 标准曲线，没有考虑具体屏幕校准。真实系统还要处理
   「stem darkening」这类知觉补偿。
4. 距离场那一节比较的是「12×12 距离场放大到 48×48」和「真正的 48×48 渲染」。
   两者本来就不同——这正是要说的事：SDF 是平滑的近似，不是更清楚的原文。

## 许可

代码 MIT，见 `../LICENSE-CODE.txt`。正文与图 CC BY 4.0。照片许可见 `sources.md`。
