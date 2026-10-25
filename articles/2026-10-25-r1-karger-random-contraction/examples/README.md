# 复现本篇数值与原创图

Python 3.12.14 执行结果见 results.json。核算程序只用标准库；绘图使用 Pillow、fontTools 和系统 Noto Sans CJK 字体，找不到中文字体会报错。

在本目录执行：

```bash
PYTHONDONTWRITEBYTECODE=1 python run_examples.py
PYTHONDONTWRITEBYTECODE=1 python build_figures.py
```

`karger.py` 是连通无向无权多重图的教学实现。自环忽略，断连或越界端点拒绝；每个边列表项代表一个副本。`run_examples.py` 另用原图分组枚举割 oracle，再精确枚举所有收缩分支，核验随机实现。运行范围、版本和种子均写入 results.json。测试不是针对大型生产图的性能基准。

`build_figures.py` 从结果文件读取数值；原生宽1062像素，最小文字40像素，校验中文glyph、出界、声明框、文字重叠、字号、对比、文字墨迹和图像实际尺寸。元数据见 figure-metadata.json。生成器的Canvas检查API沿用本仓库r1 Quickselect篇CC0代码；本篇所有图形构成与正文均为新作。

本目录Python源码采用CC0-1.0：https://creativecommons.org/publicdomain/zero/1.0/ 。JSON数值记录采用CC0-1.0；生成的教学图片采用CC BY 4.0，不随代码许可改变。
