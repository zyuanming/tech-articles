# 运行本文的小型 Lisp 求值器

需要 Python 3.12 或更新版本。先进入本目录；以下命令的输出是本篇实验数据，不是历史机器日志。

```sh
PYTHONDONTWRITEBYTECODE=1 \
python experiment.py
```

它会生成 `results.json`：16 个成功例、9 个预期错误例、5 个解析打印往返检查，以及完整调用/环境事件。输入没有随机数。错误例包括强制计算危险分支、未绑定名字、eq 的非原子输入、未捕获自由变量和不终止递归。预算上限只用于停止实验。

查看真实本地教学界面：

```sh
PYTHONDONTWRITEBYTECODE=1 \
python server.py
```

打开 `http://127.0.0.1:8121`，点击“运行表达式”。页面真的调用同目录的 Python 解释器，返回值和参数绑定由每次输入重新计算。服务只监听本机地址，按 Ctrl-C 停止；它是教学开发服务器，不是生产服务。

可以直接修改页面中的表达式。支持符号、点对、正常表、单引号缩写，五个基本操作 atom/eq/car/cdr/cons，quote/cond，以及函数位置上的 lambda/label。t 和 nil 自求值，空表归一为 nil；其他符号从环境查找。参数从左到右求值，形参绑定前置。自由变量使用调用时环境；不保存词法闭包。

重新生成示意图另需 Pillow 与 fonttools，并安装 Noto Sans CJK 字体。绘图脚本缺中文字体时会报错，不回退到缺字字体。

```sh
python -m pip install \
  Pillow fonttools
PYTHONDONTWRITEBYTECODE=1 \
python build_figures.py
```

`build_figures.py` 生成 00—12 和 14 号图；13 号图是使用 Chromium 实际打开本地应用、运行默认程序后的截图，不能由图形生成器伪造。示意图元数据由生成器写出；截图元数据由截图工具核实后登记。

数据结构和环境只用有限、无环对象；不支持循环配对、数值、赋值、宏、全局 DEFUN、任意函数位置求值或完整现代 Lisp。本文把错误定义为明确异常；这不是对早期硬件系统所有边界行为的模拟。大型/深层输入可能先遇到宿主 Python 的递归上限。

代码、HTML 和 JSON 数据采用 CC0-1.0。生成的原创图片采用 CC BY 4.0。完整来源与差异说明见[来源](../sources.md)。
