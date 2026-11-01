# 数到 32768：石英表为什么用这个古怪的频率

秒针一秒跳一格，里面那块石英片每秒振动 32768 次。这个数字是 2¹⁵——除以 2 十五次正好是 1。本篇从压电效应讲到十五级分频，从 1969 年的第一块石英表讲到一个月的误差是怎么凑出来的。

- 正文：[read.md](read.md)
- 来源与图片许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 封面：`cover.png`

## 复现

```bash
cd examples
python3 run_model.py       # 生成 results.json（标准库，无依赖）
python3 build_figures.py   # 生成 19 张图与封面（需要 Pillow）
```

`run_model.py` 约 1 秒跑完；`build_figures.py` 约 20 秒。两者都是确定性的，重跑得到的 `results.json` 与全部图片字节相同。环境见 [examples/run-environment.json](examples/run-environment.json)。

## 结构

```
read.md                     正文（19 张图）
cover.png                   1080×1080 封面
assets/01..19-*             正文配图（16 张原创示意 + 3 张 Wikimedia 照片）
originals/                  三张照片的原文件
examples/quartz.py          模型：分频链、温度抛物线、误差预算、功耗
examples/run_model.py       跑模型，写 results.json
examples/build_figures.py   画图，写 figure-metadata.json
examples/figkit.py          共用绘图工具
sources.md                  事实来源与图片许可
review.md                   审读记录（含没有做的事）
```

## 关于数字

正文里每一个由模型算出来的数都在 `examples/results.json` 里，包括分频链每一级的频率、抛物线采样、五个月的累计误差曲线、误差预算表、精度阶梯、功耗与电池寿命。参数（a = −0.035 ppm/°C²、顶点 25 °C、调校残差 5 ppm、老化 2 ppm、1 µA、20 mAh）是我按常见量级设定的，不是某一款手表的实测值——正文最后一节写明了这一点。

历史年份、数量、价格来自 `sources.md` 列出的来源；"瑞士制表业就业从 9 万降到 3 万"是广泛引用的数字，没有原始统计。

## 许可

- 正文与原创图片：CC BY 4.0
- `examples/` 下的代码：MIT（见 [LICENSE-CODE.txt](LICENSE-CODE.txt)）
- `assets/02-tuning-fork.jpg`、`assets/08-astron-watch.jpg`、`assets/09-movement.jpg`：各自的公有领域 / CC BY-SA 4.0 / CC BY 3.0 de，不适用上面的 CC BY 4.0，署名见 [sources.md](sources.md)
