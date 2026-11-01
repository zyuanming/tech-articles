# 来源

## 事实与数字

**压电效应（1880，居里兄弟）**
- <https://en.wikipedia.org/wiki/Piezoelectricity>（二手；1880 年居里兄弟的原始论文是法文期刊文章，本次未读原文）
- 用于：第二节"挤压产生电荷、加电压产生形变"的表述。

**石英钟（1927，Bell 实验室）**
- <https://en.wikipedia.org/wiki/Quartz_clock>（二手）
- 用于：第十二节的时间线与"第一台石英钟有整个机柜那么大"。原文给的精度数字口径不一，本文只写"比最好的摆钟准一个数量级"，没有引用具体数值。

**晶振、Q 值与 32768 Hz**
- <https://en.wikipedia.org/wiki/Crystal_oscillator>（二手）
- 用于：等效电路 RLC + C₀ 的形式、Q 的定义、32.768 kHz 作为表晶标准的通行说法。文中的 Q ≈ 50000、a ≈ −0.035 ppm/°C²、±20 ppm 出厂公差是**常见量级**，不是从某一款器件的规格书抄来的；具体型号的实测值会不同。

**石英危机**
- <https://en.wikipedia.org/wiki/Quartz_crisis>（二手）
- 用于：第六节"瑞士制表业就业从约 9 万降到约 3 万"。这是广泛引用的数字，本文没有找到当年的原始统计口径，因此正文与审读记录都标注了这一点。

**秒的定义与铯钟**
- <https://en.wikipedia.org/wiki/Caesium_standard>（二手）
- 用于：第七节精度阶梯里铯束钟的量级（10⁻⁶ ppm 级）。

## 图片

三张真实照片，全部来自 Wikimedia Commons，许可与作者按下表独立保留；正文与图片的 CC BY 4.0 **不覆盖**这三张照片。

| 文件 | 原文件 | 作者 / 机构 | 许可 |
| --- | --- | --- | --- |
| `assets/02-tuning-fork.jpg` | [File:Inside QuartzCrystal-Tuningfork.jpg](https://commons.wikimedia.org/wiki/File:Inside_QuartzCrystal-Tuningfork.jpg) | Chribbe76（own work） | 公有领域 |
| `assets/08-astron-watch.jpg` | [File:Seiko Astron.jpg](https://commons.wikimedia.org/wiki/File:Seiko_Astron.jpg) | Deutsches Uhrenmuseum | CC BY-SA 4.0 |
| `assets/09-movement.jpg` | [File:Seiko 35A.jpg](https://commons.wikimedia.org/wiki/File:Seiko_35A.jpg) | Museumsfoto / Deutsches Uhrenmuseum | CC BY 3.0 de |

原图完整尺寸保存在 `originals/`：`quartz-tuning-fork.jpg`（640×759）、`seiko-astron-1969.jpg`（1200×1563）、`seiko-35a.jpg`（456×456）。`assets/` 里的是同一批字节，只在宽度超过 1062 px 时做过一次等比缩小（Astron 一张），没有裁切、没有调色。

其余 16 张图（`01`、`03`–`07`、`10`–`19`）是本文原创的示意图与数据图，由 `examples/build_figures.py` 生成，identity 记为「原创教学示意」。封面 `cover.png` 同为原创。

**肖像缺口**：本篇不涉及人物肖像。1969 年的设计者、精工的技术负责人没有可自由使用的照片，正文因此只提机芯型号与年份，不做人物特写。

## 代码

`examples/quartz.py`、`examples/run_model.py`、`examples/build_figures.py` 为原创，MIT（见 `LICENSE-CODE.txt`）。`examples/figkit.py` 是本仓库多篇文章共用的绘图工具，同样 MIT。没有第三方依赖，Python 标准库即可运行（`build_figures.py` 另需 Pillow，见 `run-environment.json`）。
