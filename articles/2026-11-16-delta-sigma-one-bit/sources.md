# 来源与说明

## 图片

四张实物照片全部来自 Wikimedia Commons，下载的是原始文件，只在宽度超过 1062 px 时按比例缩到 1062 宽（`examples/build_figures.py` 里的 `photo()` 只缩放，宽度已经小于 1062 的直接复制字节）。未裁切。

| 文件 | 原始尺寸 | 作者 | 许可 | 原始页面 |
| --- | --- | --- | --- | --- |
| `02-cdp101.jpg` | 1280×853 | Museo Nazionale Scienza e Tecnologia Leonardo da Vinci 藏（Sony 制造） | CC BY-SA 4.0 | <https://commons.wikimedia.org/wiki/File:Sony-101_lettore-CD_Museo_scienza_tecnologia_Milano_08733.jpg> |
| `14-tda1541.jpg` | 2560×1920 | Cjp24 | CC BY-SA 3.0 | <https://commons.wikimedia.org/wiki/File:DAC_Philips_TDA1541A_S1.jpg> |
| `15-cd472-board.jpg` | 5777×4102 | Raimond Spekking | CC BY-SA 4.0 | <https://commons.wikimedia.org/wiki/File:Philips_CD472_-_main_board-8122.jpg> |
| `17-korg.jpg` | 3872×2592 | Brandon Daniel | CC BY-SA 2.0 | <https://commons.wikimedia.org/wiki/File:KORG_MR-2000S_1-Bit_Studio_Recorder.jpg> |

其余 15 张（`01`、`03`–`13`、`16`、`18`、`19` 和 `cover.png`）是本文原创的教学示意，由 `examples/build_figures.py` 生成，不是照片，也不代表任何真实芯片的版图或实测波形。

照片的身份只有一条：它拍的那个东西。`02-cdp101.jpg` 是博物馆里的 Sony CDP-101，不是本文测试过的机器；`14-tda1541.jpg` 是一颗 TDA1541A S1（单皇冠）芯片，本文没有声称任何具体型号的唱机用的是这一颗；`15-cd472-board.jpg` 是一台 Philips CD472 的主板，本文只用它说明「一颗 DAC 周围要围多少东西」，没有把它当成音质证据；`17-korg.jpg` 是一台 KORG MR-2000S 录音机，本文没有声称它是 DSD 录音的唯一或最早实现。

## 数字

正文和图片里的每个数字都由 `examples/dsigma.py` 算出、`examples/run_model.py` 写进 `examples/results.json`，`examples/build_figures.py` 只从 `results.json` 取值（`|NTF|` 曲线和量化台阶另外 import 同一个模块计算）。跑一遍：

```sh
cd examples && python3 run_model.py && python3 build_figures.py
```

纯标准库，不需要安装任何东西（画图需要 Pillow）。耗时约 10 秒，主要是几万点的自写 FFT。

`results.json` 开头的 `bw / fs0 / nfft / kbin / dither` 就是这几条设定，下面把它们的含义写清楚：

- **信号带宽 22 050 Hz，基准采样率 44 100 Hz。** 过采样率 OSR 就是「实际采样率 ÷（2 × 22 050）」，所以 OSR 64 对应 2.8224 MHz，和 DSD64 同一个数。
- **FFT 长度 32 768，信号落在第 16 个 bin。** 取整 bin 是为了避免频谱泄漏：信号频率 16 × 2.8224 MHz / 32 768 = 1378 Hz，正好在 bin 上。OSR 64 时带内前 256 个 bin 参与统计。
- **SNR 的定义是「信号 bin 的功率」除以「除所有谐波 ±3 bin 以外的带内 bin 功率之和」。** 把谐波算进去的那个指标叫 SINAD，模型里单独输出（`sim.o1_sinad` = 42.3 dB）。
- **抖动幅度 1.0，单位是一位量化器的 1 LSB。** 一位量化器的输出是 ±1，所以 1 LSB 就是 2.0 的台阶高度；`DITHER = 1.0` 表示三角抖动的半宽等于半个台阶。不加抖动时，直流输入会让环路锁成周期图案，测出来的 SNR 会虚高 30 dB 以上，所以正文的 SNR 一律带抖动。
- **随机数用自写的 LCG**（`1103515245 * s + 12345`，取低 31 位），保证换机器重跑逐字节一致。没有用 `random` 模块，因为它不保证跨版本给出同一串数。
- **二阶环路的两个积分器都取上一步的输出**，没有用 `bits[-2]` 这类更早的项——早期版本犯过这个错，二阶的 SNR 会掉到一阶的水平。

关键数字的来历：

- **56.8 dB / 85.2 dB**：一阶、二阶在 OSR 64、一位满幅正弦下的教科书估计。式子是 `6.02n + 1.76 − 10·log₁₀(π^{2L}/(2L+1)) + 10(2L+1)·log₁₀(OSR)`，L 是阶数。一阶：7.8 − 5.2 + 54.1；二阶：7.8 − 12.9 + 90.3。
- **45.0 dB / 69.3 dB**：同一条件下的模型输出（带 1 位三角抖动）。差距 11.8 dB 和 15.9 dB，`sources.md` 的这一节和正文都把这当成「公式乐观」的例子，不是模型错误。
- **5.9 / 10.3 dB/oct**：`slope_db_per_octave()` 取噪声密度曲线从第 4 个点到倒数第 4 个点做两点拟合。端点附近有信号谐波和直流，所以掐掉不用。理论值是 6 和 12。
- **14.1 kHz / −60 dB**：输入 0.001 的直流、不加抖动时，带内（0–22.05 kHz）最大的那根非信号谱线。加 1 位抖动后同一位置的峰值是 −63.5 dB。
- **1/3**（`quant_noise`）：一位量化器（输出 ±1，台阶 2）的量化噪声功率 2²/12。
- **比特率表**：CD 705 600 bit/s = 44 100 × 16（单声道）；一位流 2 822 400 bit/s；四倍 11 289 600。

## 明确没有做的事

- **没有实测任何真实芯片。** 全文的数字来自行为级模型：理想积分器、理想比较器、一位量化器，没有运放有限增益、没有电容失配、没有时钟抖动、没有热噪声。真实芯片的 SNR 通常比模型低 3–10 dB，`sources.md` 不假装模型等于硬件。
- **没有 SPICE 仿真。** 环路是离散时间差分方程，连连续时间开关电容的电荷注入都没建模。
- **没有做听感测试。** 「−60 dB 的空闲音在安静段落里明确可闻」是基于音量量级的判断，不是本文的盲听结果。
- **没有推翻公式。** 理论式子是教科书里的标准结果，本文只是把它和模型放在同一张图上。
- **没有证明「1 bit 比多比特好听」。** 正文只说两条路线的成本结构不同，没有对音质下结论——这类结论需要受控听测，本文没做。
- **没有逐条核对芯片规格书。** TDA1541A 的引脚数、DEM 结构、SAA7350/TDA1547 的组合年份来自公开资料的常见说法，本文没有对照原始数据手册逐一确认。
- **没有目视检查图片。** 见 `review.md`。

## 引用与延伸

- H. Inose, Y. Yasuda, *A unity bit coding method by negative feedback*, Proc. IEEE 51(11), 1963（1962 年在日本发表日文版）。
- S. Park, *Principles of Sigma-Delta Modulation for Analog-to-Digital Converters*, Motorola APRI8/D, 1990。噪声整形公式与稳定性讨论的常见入门材料。
- R. Schreier, G. C. Temes, *Understanding Delta-Sigma Data Converters*, Wiley, 2005。高阶环路的稳定性与 NTF 设计。
- 本文的推导、公式与图全部重算，没有复制上述材料里的数字或图。
