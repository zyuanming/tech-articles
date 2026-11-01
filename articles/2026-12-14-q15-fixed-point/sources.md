# 来源与素材

## 一、参考文献

- Randy Yates. *Fixed-Point Arithmetic: An Introduction*. 2007–2013（多次修订的数字信号处理讲义）。用到的内容：Q 格式的记法（Q15 = 1 位符号 + 15 位小数）、乘法的定标规则、舍入与截断的差别。本文的记法与它一致。
- Motorola. *DSP56000/DSP56001 Digital Signal Processor User's Manual*. 1990。用到的内容：定点 DSP 的数据通路宽度与累加器宽度分开设计这一事实（24 位数据、56 位累加器），以及饱和指令在指令集里的位置。本文没有逐页核对指令编码，只用了手册层面的架构描述。
- Alan V. Oppenheim, Ronald W. Schafer. *Discrete-Time Signal Processing*. 第 3 版, 2010, §4.8。用到的内容：量化噪声功率 Δ²/12 与满幅正弦的 6.02N + 1.76 dB 公式，也就是第十三节那条斜线。
- L. B. Jackson. *An Analysis of Limit Cycles due to Multiplication Rounding in Recursive Digital Filters*. Proc. 7th Allerton Conf. on Circuit and System Theory, 1969。用到的内容：递归滤波器在乘法舍入之下会产生小振幅的极限环（本文第十节的"死区"，是这个问题在一阶低通上的具体形态）。本文没有实现论文里的完整分析，只做了单点数值实验。
- ARM. *CMSIS-DSP 文档*，`q15_t` 与 `arm_float_to_q15`。<https://arm-software.github.io/CMSIS-DSP/main/group__q15.html>。用到的内容：一个占主流的 Q15 实现约定。要注意 CMSIS 把 1.0 定标到 `0x7FFF`（32767），而本文为了算术整齐把满幅取成 32768；两者差一格，不影响任何结论，但混用两套代码时会出现一格的对不上。

## 二、照片

一张，Wikimedia Commons 原图。宽度大于 1062 px，按比例缩到 1062 px 存放；原文件另存于 `originals/`。

| 图 | 文件 | 原图尺寸 | 许可 | 作者 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 17 | `17-dsp56000.jpg` | 2341 × 1456 | CC BY-SA 3.0 | Konstantin Lanzet | <https://commons.wikimedia.org/wiki/File:KL_Motorola_DSP_XSP56001ZL.jpg> |

许可只覆盖照片本身，不覆盖本文正文与示意图。照片里的芯片型号按 Commons 文件描述为 DSP56001（XSP56001ZL，评估/工程样品封装）；本文没有独立核对丝印。

## 三、原创示意图

17 张（01–16、18）由 `examples/build_figures.py` 用 `figkit.py` 绘制，身份一律为**原创教学示意**：不是照片、不是示波器截图、不是硬件实测波形。图里的每个数字都来自 `examples/results.json`。

| 图 | 内容 | 数字来源（`results.json` 字段） |
| --- | --- | --- |
| 01 | 16 位的位权与 0.6875 的拆解 | 算术示意（0.6875 × 32768 = 22528） |
| 02 | 0.3 附近的量化格 | `representation.rows[2]`（9830、误差 0.4 格） |
| 03 | Q15 与 4 位定点的正弦 | `staircase`（96 点，含 Q15 与 Q3 两条） |
| 04 | 两个 0.1 相乘的三种落位 | `mul.a_raw`、`mul.b_raw`、`mul.product_exact`、`mul.stats` |
| 05 | 三种舍入的误差分布 | `mul.stats[*].buckets`（20000 次抽样） |
| 06 | 4096 次乘法的偏置累积 | `mul.drift` |
| 07 | 饱和与回绕 | `overflow.rows` |
| 08 | 乘积 31 位、和 39 位 | `overflow.product_bits`、`accumulator.need_bits`、`accumulator.overflow32_runs` |
| 09 | 系数被量化后的截止频率 | `coef.rows`、`coef.f_floor` |
| 10 | 极点半径与 T60 | `poles.rows`（图内按 b1 = −32763…−32768 重算，公式同 `poles`） |
| 11 | 死区里的尾巴 | `limit_cycle.trunc.curve`、`limit_cycle.round.curve` |
| 12 | 与浮点参考的误差曲线 | `filter.q15_waves`、`filter.float_wave` |
| 13 | 三种舍入的端到端信噪比 | `filter.runs[*].snr_db`、`rms_err_lsb` |
| 14 | 正弦表的误差曲线 | `sin_table.curve_near`、`sin_table.curve_lerp`、`max_err_lsb` |
| 15 | 位数与信噪比 | `sqnr`（实测 `measured` 与理论 `theory`） |
| 16 | 换字长 | `word_sweep` |
| 18 | 五条结论 | 无数字 |

## 四、模型设定

`examples/q15.py` 的参数（写死在模块常量里，`results.json → config` 也记了一份）：

| 参数 | 值 | 说明 |
| --- | --- | --- |
| 小数位数 | 15 | Q15，满幅 32768 |
| 采样率 | 48000 Hz | 只影响截止频率与 T60 的换算 |
| 随机乘法抽样 | 20000 对 | xorshift32，种子 7 |
| 偏置累积 | 4096 次 | 固定乘 3277 × 3277 |
| 累加器实验 | 200 组 × 256 项 | 随机 16 位操作数，其中有 50% 的机会抽到满幅 |
| 死区实验 | a = 0.05，4000 步 | 一个脉冲，其余输入为 0 |
| 端到端滤波 | 2000 点，a = 0.02 | 220 / 3000 / 9000 Hz 三个正弦叠加 |
| 正弦表 | 1024 项 | 误差在 800 个相位点上取最大值 |
| 字长扫描 | 16 / 20 / 24 / 28 / 32 位 | 同一个滤波器，只改定标 |

## 五、明确没做的

- **没有在真实 DSP 或 MCU 上跑。** 所有结果来自 Python 整数模型，它精确复现 Q15 的整数运算，但不会复现流水线、饱和指令的时序、编译器是否把 `(a*b)>>15` 优化成一条指令这类事。
- **累加器只分析到 32 位。** 39 位那个结论是位数计算，没有真的用 39 位寄存器跑一遍。
- **死区只测了一个 a（0.05）**，没有做参数扫描，也没有测二阶滤波器的极限环。"死区宽度约 1/a 格"是从单点结果推的，不是扫出来的。
- **正弦表只测了 1024 项**，没有扫表长与误差的关系，也没有测更高阶的插值。
- **图 17 的芯片信息来自 Commons 文件描述与公开资料**，没有查原始数据手册内页确认封装与年份。
- **没有做浮点对照之外的第三方参考。** 端到端误差是相对 Python 双精度算的同一条滤波器，不是相对硬件。
- **图片未目视检查**，构建者当前的模型不能读图；机械校验（文字越界、重叠、字号下限、画布覆盖）通过，视觉效果未看。
