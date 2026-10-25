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

## 新增的过程与波动图

`results.json` 的 `scan` 记录主元为 5 时逐项追加后的三组及未读后缀；图09选第1、2、9项后的状态，省略中间动作但保留累计结果。`experiments` 的既有样本最小/最大访问数与均值一起用于图10，`sample_plot` 记录共用轴与种子范围。范围是200个种子的观测极值，不是理论界或置信区间。两张图仍由标准库实验数据生成，不依赖 NumPy。

## 可选：真实 NumPy 教学网页

新增 `demo_web.py` 实时调用 NumPy；不修改原来的标准库 `selection.py`。本篇截图实际使用 Python 3.12.14、**NumPy 2.4.6** 和 `int64` 数组。文档链接指向 NumPy 2.4 系列；不要以其他补丁版本的运行冒充这里的精确输出。当前截图程序有意断言 2.4.6，复现其他版本时应另存并注明结果。

请在仓库外的独立虚拟环境安装额外依赖，避免将依赖文件纳入文章发布目录（标准库选择例子无需这一步）：

```bash
python -m venv "$HOME/quickselect-demo-venv"
DEMO_PY="$HOME/quickselect-demo-venv/bin/python"
"$DEMO_PY" -m pip install \
  numpy==2.4.6 playwright pillow fonttools
```

网页运行只需 NumPy。已有可用的系统 Chromium 与 Noto Sans CJK 字体时，可执行：

```bash
PYTHONDONTWRITEBYTECODE=1 "$DEMO_PY" \
  examples/demo_web.py
```

程序只绑定 `127.0.0.1`，动态选取空闲端口，在终端打印本地地址。打开后点击“运行 NumPy 并核验”。请求实时产生结果，不读取一份预先画好的输出截图。`np.partition` 返回新数组，输入未变；这组短输入的返回数组恰好全部有序，界面明确说明这不是两侧内部总有序的保证。

需要重现公开截图时，可指定仓库外的证据目录：

```bash
PYTHONDONTWRITEBYTECODE=1 "$DEMO_PY" \
  examples/capture_demo.py \
  --evidence-dir "$HOME/quickselect-browser-evidence"
```

`capture_demo.py` 使用 Playwright 默认启动配置和系统 Chromium，可用 `--chromium` 显式指定已安装可执行文件；不修改系统浏览器配置。它自动运行本地服务、实际点击1062/354宽两种视口，保存公开 `assets/11-numpy-live.png`、纯教学调用数据 `numpy-result.json` 和图元数据。实际 URL、端口、浏览器检查记录、真实手机截图只写入指定的外部证据目录；不要把这些记录提交进文章目录。若本机浏览器环境无法正常启动，应停止截图并记录限制，不把静态重画冒充实跑。

截图检查包括响应断言、输入未变、页面身份、控制台错误、横向溢出、文字框相交、计算字号、字体字形与截图区域的对比/墨迹像素。截图展示的是原创教学网页，不是 NumPy 官方UI、终端或公众号预览；两种视口是同一界面的复核，不当成两张独立教学配图。
