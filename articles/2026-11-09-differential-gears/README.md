# 两个轮子，为什么可以不一样快

转弯时外轮画大圆、内轮画小圆，一圈差出的长度正好是 π × 轮距。本篇从这一个事实出发：为什么必须允许两个后轮转速不同，齿轮是怎么在"分开"的同时还把动力送过去的，以及为什么这么聪明的装置一遇到冰面就当场失效。

- 正文：[read.md](read.md)
- 来源与图片许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 封面：`cover.png`

## 复现

```bash
cd examples
python3 run_model.py       # 生成 results.json（标准库，无依赖）
python3 build_figures.py   # 生成 17 张图与封面（需要 Pillow）
```

`run_model.py` 约 1 秒跑完；`build_figures.py` 约 5 秒。两者都是确定性的，重跑得到的 `results.json` 与全部图片字节相同。环境见 [examples/run-environment.json](examples/run-environment.json)。

## 结构

```
read.md                     正文（17 张图）
cover.png                   1080×1080 封面
assets/01..17-*             正文配图（14 张原创示意 + 3 张 Wikimedia 照片/扫描件）
originals/                  三张照片的原文件
examples/diff.py            模型：轮速关系、拖行距离、牵引力、限滑偏置
examples/run_model.py       跑模型，写 results.json
examples/build_figures.py   画图，写 figure-metadata.json
examples/figkit.py          共用绘图工具
sources.md                  事实来源与图片许可
review.md                   审读记录（含没有做的事）
```

## 关于数字

正文里每一个由模型算出来的数都在 `examples/results.json` 里：轮速比随半径的曲线、一圈的周长差、一条路线的两轮速度轨迹、焊死后的拖行距离、四种路面下的牵引力与加速度、限滑偏置比的效果、行星架的平均关系。参数（轮距 1.55 m、轮径 0.65 m、整车 1400 kg、传动轴扭矩 2730 Nm、μ = 0.01/0.10/0.35/0.90）是按常见量级设定的，不是某一款车的实测值——正文最后一节写明了这一点。

历史年份（1827 / 1877 / 1911 / 1958）来自 `sources.md` 列出的二手资料，原始专利没有读到。

## 许可

- 正文与原创图片：CC BY 4.0
- `examples/` 下的代码：MIT（见 [LICENSE-CODE.txt](LICENSE-CODE.txt)）
- `assets/02-cutaway.jpg`：CC BY-SA 3.0（DrJunge），不适用上面的 CC BY 4.0
- `assets/10-manual-1911.jpg`、`assets/11-starley.jpg`：公有领域
- 三张照片的署名与出处见 [sources.md](sources.md)
