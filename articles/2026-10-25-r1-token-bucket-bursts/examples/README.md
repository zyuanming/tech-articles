# 复现令牌桶主例

Python 3.12.14，精确算术使用标准库 `fractions.Fraction`；无随机输入。所有时间单位为秒，费用单位为份额度，主例1000字节为1份。原始输入在 `model.py` 的 `INPUT`，`RATE=2`、`CAPACITY=6`；固定窗反例另设容量2，流体近似另设持续速率8，均在输出中标明。

进入本目录后执行：

```sh
PYTHONDONTWRITEBYTECODE=1 \
python run_examples.py
```

运行会更新 `results.json`，输出2401组整数时钟对照检查与57个子区间界检查的数量。`model.py` 中监管按需补充、截顶、判定并扣款；整形是离线FIFO资格时间计算，超大包先移除、无限等候区、零链路传输耗时。不提供线程安全、分布式原子性或生产流控保证。

图形依赖 Pillow、fontTools、Noto Sans CJK 和 DejaVu Sans Mono 字体；真实界面截图还需 Playwright 和 Chromium。本次版本见 [environment.json](environment.json)。

```sh
PYTHONDONTWRITEBYTECODE=1 \
python build_figures.py
PYTHONDONTWRITEBYTECODE=1 \
python render_source.py
```

运行后分别生成14张原创图及1张带完整版权通知的RFC ASCII渲染。数据驱动条长、状态、曲线点来自 `results.json`；布局常量不是实验数据。前两篇允许复用的CC0绘图Canvas经过本篇调用，所有构图与标注均为新作。

启动教学界面：

```sh
PYTHONDONTWRITEBYTECODE=1 \
python demo_web.py
```

程序打印本机回环地址，浏览器打开后点击按钮，会重新执行 Python 模型并显示结果。没有任何数据包被发到外部网络。也可自动点击并截图；审计目录须位于文章目录之外，下列相对位置请按实际目录调整：

```sh
PYTHONDONTWRITEBYTECODE=1 \
python capture_demo.py \
  --evidence-dir ../../../../token-audit
```

桌面截图写到 `assets/15-model-live.png`；实际354宽手机浏览器截图、浏览器版本、文字框及检查证据写入给定外部目录。`figure-metadata.json`记录全部正文图片身份与尺寸；图14中完整英文许可为史料附注小字，原ASCII以37px保留两侧边距（354宽约12.3px），中文解释40px及以上。

代码与原创模型数据（results.json、environment.json、figure-metadata.json）由zyuanming以 [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) 提供。原创图像与截图采用CC BY 4.0。RFC ASCII及许可不在这些授权内，保留Internet Society原权利。源码依赖库和浏览器各自保持其原许可。
