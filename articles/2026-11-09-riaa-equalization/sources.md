# 来源

## 事实

**RIAA 曲线的三个时间常数**
- <https://en.wikipedia.org/wiki/RIAA_equalization>（二手）
- 用于：3180 / 318 / 75 微秒三个时间常数，对应 50.05 / 500.5 / 2122 Hz 三个折点；"1 kHz 归零"的归一化方式；以及"两端各约 ±20 dB、总跨度约 40 dB"的数量级。
- **本文没有逐字核对 1954 年的 RIAA 标准文本，也没有读 IEC 60098 原文。** 正文里"1954 年"这个年份、以及"后来标准里加了一条可选的亚声频滚降"这一句，都是公开技术资料里的通行表述。

**曲线管的是振速，不是振幅**
- 同一页的 transfer function 表述：刻片曲线把**振速**按频率加权，沟槽上真正刻出来的**振幅** = 振速 / (2πf)。
- 这一条是本文第四节"把分贝换成毫米"的全部依据。很多介绍文章把两者混着说，导致"低音砍了 19 dB 反而振幅更大"看起来像矛盾。

**45/45 立体声制式**
- <https://en.wikipedia.org/wiki/Gramophone_record>（二手）
- 用于：第七节"V 形槽、左右两个斜面各驮一个声道、1958 年成为标准"。具体年份没有核对原始标准。

**刻片头的行程限制与槽距**
- 同页以及 <https://en.wikipedia.org/wiki/Phonograph_record_cutting>（二手）
- 用于：第五节"振幅超过槽距会撞进隔壁一圈"、"槽距决定一面能录多久"这两条推理，以及第八节"内圈线速度低、波长更短"的几何关系。
- 具体行程数值（几十微米量级）是量级估计，不来自某个型号的规格表。

**唱针接触半径与高频损失**
- <https://en.wikipedia.org/wiki/Phonograph_stylus>（二手）
- 用于：第七节"接触半径在 5 微米量级"、第八节"波长接近接触尺寸时针尖读不到细节"。
- 本文只做了数量级比较，**没有建模接触力学**；针尖形状（圆锥、椭圆、柴田、线接触）之间的差别也没有展开。

## 模型里哪些是设定值

- 时间常数 3180 / 318 / 75 µs、参考频率 1 kHz、参考振速 5 cm/s（峰值）：前三个是 RIAA 定义值，后两个是"常见测试电平"的取法，不是唯一约定。
- 盘片几何：外半径 146 mm、内半径 58 mm、33⅓ 转/分、首尾各留 2.5 mm 保护带。用来算线速度（外 0.51 / 中 0.356 / 内 0.202 m/s）、圈数、沟长。
- 槽距估法：**按整条带子里最大的振幅定统一槽距**，再乘一个固定余量。真刻片机是动态调槽距的，所以模型的时长是上界。
- 唱针接触半径 5 微米（即接触直径 10 微米）：常见量级，用来说明波长与接触尺寸的关系。
- 元件容差：R ±1%、C ±5%（另有一组 1%/1% 对照），抽样 200 次，取整条曲线上偏离理想值的最大绝对值作为"最坏一次"。**这不是元件厂家的实测分布**，均匀分布假设。
- 亚声频：33⅓ 转对应 0.556 Hz；翘曲幅度没有建模，只算了曲线在该频率上的增益（+19.9 dB）。
- 白噪：假设噪声功率谱密度在每个频率上相同，按 10 个倍频程（31.5 Hz–16 kHz）加权求和。真实唱片表面噪声不是严格白噪，低频段会受转盘隆隆声污染。

## 图片

四张照片全部来自 Wikimedia Commons，许可与作者按下表独立保留；正文的 CC BY 4.0 **不覆盖**这四张图。

| 文件 | 原文件 | 作者 | 许可 |
| --- | --- | --- | --- |
| `assets/02-lathe.jpg` | [File:Neumann VMS-70 Cutting Lathe, SAE Mastering, Phoenix, AZ.jpg](https://commons.wikimedia.org/wiki/File:Neumann_VMS-70_Cutting_Lathe,_SAE_Mastering,_Phoenix,_AZ.jpg) | VACANT FEVER | CC BY-SA 2.0 |
| `assets/06-groove.jpg` | [File:LP Record Groove Close-Up (5248017534).jpg](https://commons.wikimedia.org/wiki/File:LP_Record_Groove_Close-Up_(5248017534).jpg) | Piano Piano! | CC BY 2.0 |
| `assets/09-cartridge.jpg` | [File:Ortofon 2M-Black PNP cartridge, stylus gauge, Ortofon Anniversary white book (2).jpg](https://commons.wikimedia.org/wiki/File:Ortofon_2M-Black_PNP_cartridge,_stylus_gauge,_Ortofon_Anniversary_white_book_(2).jpg) | Audiotecna Música | CC0 |
| `assets/14-turntable.jpg` | [File:Technics SL-1200MK5 Direct Drive Turntable System with Ortofon cartridge (2017-01-21 22.33.27 piqsels.com en).jpg](https://commons.wikimedia.org/wiki/File:Technics_SL-1200MK5_Direct_Drive_Turntable_System_with_Ortofon_cartridge_(2017-01-21_22.33.27_piqsels.com_en).jpg) | 未署名（piqsels 上传） | CC0 |

原图完整尺寸保存在 `originals/`：`lathe.jpg`（2288×1712）、`groove.jpg`（1908×1780）、`cartridge.jpg`（2048×1536）、`turntable.jpg`（3000×2308）。`assets/` 里的四份对应文件做过一次等比缩小到 1062 px 宽，没有裁切、没有调色。缩完的大小是 182 KB / 302 KB / 151 KB / 138 KB，都远低于公众号每图 5,000,000 字节的限制。

其余 14 张（`01`、`03`–`05`、`07`、`08`、`10`–`13`、`15`–`18`）是本文原创的示意图与数据图，由 `examples/build_figures.py` 生成，identity 记为「原创教学示意」。封面 `cover.png` 同为原创。

**身份说明**：`02`、`06`、`09`、`14` 是真实照片（刻片机、沟槽特写、唱头、唱盘）；`05`、`07` 是把微米级尺寸按比例画出来的**示意**，不是显微照片，图里注明了比例尺，不能当作实测形貌看。

**缺口**：刻片头的内部结构（线圈、反馈线圈、加热丝）没有找到可自由使用的照片；RIAA 网络的实际电路照片也没有收入，正文第十节只画了方块。唱针针尖在电子显微镜下的照片有公开版本，但多数许可不明，本篇没有采用。

## 代码

`examples/riaa.py`、`examples/run_model.py`、`examples/build_figures.py` 为原创，MIT（见 `LICENSE-CODE.txt`）。`examples/figkit.py` 是本仓库多篇文章共用的绘图工具，同样 MIT。模型只用 Python 标准库（`build_figures.py` 另需 Pillow，见 `run-environment.json`）。
