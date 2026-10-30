# 0.1 + 0.2 为什么不等于 0.3：可复算材料

正文：[read.md](read.md)。来源与许可：[sources.md](sources.md)。

这篇文章里的每一个数——位模式、精确差值、长除法的每一位、每次求和的误差——都由本目录的代码**实际算出来**，不是从别处抄的。

## 运行

环境记录见 [run-environment.json](examples/run-environment.json)。**全部代码只用 Python 标准库**，不需要安装任何东西（绘图另需 Pillow 与一款中文字体）。

在本篇目录中执行：

```sh
python examples/run_model.py        # 全部实验，写 results.json
python examples/build_figures.py    # 重绘全部正文图与封面
```

首次运行时的原始标准输出保存在 `originals/model-stdout.txt`。

## 三个关键机制

### 1. 位模式是算出来的，不是写死的

`floats.py` 用 `struct.pack('<d', x)` 取一个 float 的 64 位，再用 `format` 把符号、指数、尾数三段切出来。所以 `0x3FB999999999999A` 这样的值不会写错——它本来就不是写进去的。

### 2. 精确值用有理数，不用浮点

"0.1 实际存的是多少"这个问题不能用浮点回答（那正是问题本身）。`Fraction(0.1)` 给出精确的 3602879701896397/36028797018963968，所有差值都在有理数域里算，最后才转成十进制字符串。

### 3. 结论互相印证

- `0.1 + 0.2` 与 `0.3` 相差正好 1 个 ulp —— 由 `Fraction` 相减得到；
- 这个差**恰好**是两者中点 —— 由 `(exact(lower) + exact(upper)) / 2` 与精确和比较得到；
- 取偶数规则选中上邻 —— 由 `bits(0.3) & 1 == 1` 与 `bits(next) & 1 == 0` 得到。

三条独立计算指向同一个结论，才写进正文。

## 复现时容易踩的两个坑

- **不要用浮点去验证浮点。** 想知道"存进去的是什么"，必须用 `Fraction` 或十进制字符串展开。
- **十进制字面量本身就是一次舍入。** 写 `Fraction(0.1)` 得到的是**机器里的 0.1**，不是 1/10。要精确的十分之一得写 `Fraction(1, 10)`。本文需要区分这两者时都会明确写出来。

## 文件

- `examples/floats.py` —— 全部机制：位模式、长除法、ulp、精确加法、求和、抵消、特殊值、快平方根倒数。
- `examples/run_model.py` —— 跑实验，写 `results.json`。
- `examples/build_figures.py` —— 画图；图里的数字从 `results.json` 读。
- `examples/figkit.py` —— 自检式绘图工具，见[技术图的生产与自检](../../docs/figure-production-2026-10-16.md)。
