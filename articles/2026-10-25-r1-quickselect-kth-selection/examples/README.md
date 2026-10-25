# Quickselect 的可复算教学材料

Python 3.12.14；绘图另需 Pillow 与 fontTools，以及 Noto Sans CJK 中文字体。正文算法只依赖 Python 标准库。代码采用 CC0-1.0，生成的原创教学图采用 CC BY 4.0。

在本文目录执行：

```bash
PYTHONDONTWRITEBYTECODE=1 python examples/run_examples.py
PYTHONDONTWRITEBYTECODE=1 python examples/build_figures.py
```

- `selection.py`：正式教学函数 `quickselect` 与指定主元的 `trace`。前者循环分配新列表，期望时间 O(n)、最坏 O(n²)、峰值额外空间 O(n)，不修改输入；仅接受整数，比较视作单位成本。后者为教学保存所有轮次快照，不能据它的内存用量声称前者也保留全部历史；最坏快照总量可达 O(n²)。
- `run_examples.py`：穷举重复值输入、边界检查、固定种子测试，以及指定/随机主元的访问次数实验。实验计数是分区处理的项数，不是比较次数、秒数或全部操作次数。
- `results.json`：实际执行的数组、轨迹、工作量与验证范围，图中的模型数字均从这里读取。
- `build_figures.py`：本篇新图组成与字体/边界/声明框/重叠/字号/对比度/墨迹像素检查。Canvas 基础 API 参考同库 r1 Aho–Corasick 篇的 CC0 代码，没有复用该篇图像或图中结构。
- `figure-metadata.json`：每图用途、尺寸、身份、最小字号和检查项。

主线指定主元为 5、7、6，候选长度为 9、4、1。理想主元实验用排序选取主元，仅用于展示分区工作形状，其排序成本没有算入访问数。随机实验对每个 n 使用种子 0..199；输入为 0..n-1，k=n//2。它们是有限范围的模型输出，不是理论证明或生产性能基准。
