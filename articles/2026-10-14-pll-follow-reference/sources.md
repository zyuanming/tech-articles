# 资料与视觉素材清单

《芯片里的时钟，怎样追上另一串节拍？》；核对日期2026-10-14。

## 一手技术依据

1. Analog Devices，[MT-086: Fundamentals of Phase Locked Loops (PLLs)](https://www.analog.com/media/en/training-seminars/tutorials/mt-086.pdf)，Rev.0，2008-10。用于核PLL保持固定相位关系、鉴相/受控振荡器/环路、分频反馈与频率合成。旧资料中的发展预测不作为今天事实。原厂图只链接，没有推定公开PDF等于图片开放许可。
2. W. M. Austin，Texas Instruments，[CMOS Phase-Locked-Loop Applications Using the CD54/74HC/HCT4046A and CD54/74HC/HCT7046A](https://www.ti.com/lit/an/scha003b/scha003b.pdf)，SCHA003B，2002-09。第9–11页比较器差异、锁定波形及第31–32页结构说明支撑“锁定不一律零相差”；捕获与保持术语按原定义区分。本文不把一个芯片的范围数值推广至所有PLL。
3. Texas Instruments，[C2000 SPLL_1PH_NOTCH软件PLL说明](https://software-dl.ti.com/C2000/c2000_apps_public_sw/c2000ware_sdk/digitalpowersdk/5_03_00_00/html_guide/group__SPLL__1PH__NOTCH.html)。用于核数字PI与振荡器相位累加的结构。本文用自己的直接圈数误差模型，不复制该电网单相正弦PLL。页面误差传递函数分子s²对应原点两个零点，未照抄正文将其误称two poles的句子。
4. Mike Curtin、Paul O’Brien，[Phase-Locked Loops for High-Frequency Receivers and Transmitters, Part 2](https://www.analog.com/en/resources/analog-dialogue/articles/pll-for-high-frequency-receivers-and-transmitters-2.html)，Analog Dialogue。Closing the Loop与噪声传递公式用于核参考和本振噪声有不同进入路径；不据此声称窄带过滤一切噪声。
5. Analog Devices，[Phase-Locked Loop (PLL) Fundamentals](https://www.analog.com/en/resources/analog-dialogue/articles/phase-locked-loop-pll-fundamentals.html)：环路滤波、响应与低抖动权衡的补充。PI自身高频增益趋向Kp，本文没有把它单独描述成滚降至0的低通；“参考相位跟踪的低通特征”指整个闭环。

历史优先权、发明轶事未搜集到足够一手证据，本文不扩写。正文的1 Hz/0.8 Hz、前三次运算、P-only偏差、除4、扰动以及11 Hz混叠反例来自自己的明确模型与实际程序，不假托为上述原厂的实测数据。

## 两张真实研究图片

完整出处：Tobias T. Braun, Marcel van Delden, Christian Bredendiek, Jan Schoepfel, Stephan Hauptmeier, William Shillue, Thomas Musch, Nils Pohl (2023), “A phase-locked loop with a jitter of 50 fs for astronomy applications”, International Journal of Microwave and Wireless Technologies 15(6), 1012–1020。

- [DOI](https://doi.org/10.1017/S1759078722001386)
- [Cambridge出版社页面](https://www.cambridge.org/core/journals/international-journal-of-microwave-and-wireless-technologies/article/phaselocked-loop-with-a-jitter-of-50-fs-for-astronomy-applications/6AD147A0E98786F85A7C92C1D03DC908)
- [出版社PDF](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/6AD147A0E98786F85A7C92C1D03DC908/S1759078722001386a.pdf/phaselocked_loop_with_a_jitter_of_50_fs_for_astronomy_applications.pdf)
- 版权：© The Author(s), 2023；[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。出版社页面与PDF首页均载明该许可；两图图注和邻近内容未见另行第三方权利例外。

图1：已搭建的本振模块及射频前端。本文文件assets/02-real-pll-module.jpg，对应原件[braun-2023-fig1-pdf-extracted-000.jpg](originals/braun-2023-fig1-pdf-extracted-000.jpg)，375×362。

图3：芯片显微照片，包含VCO、N-Divider、PFD及其他射频区域。本文文件assets/18-real-pll-chip.jpg，对应原件[braun-2023-p4-extracted-000.jpg](originals/braun-2023-p4-extracted-000.jpg)，500×369。

两图均从已成功取得的出版社PDF用pdfimages无损提取内嵌JPEG，正文副本与原件逐字节相同，未裁切、修改画面、翻译图内标签或生成补画。以上尺寸是PDF内嵌资产原生尺寸，不是相机原始照片尺寸。出版社独立高分辨率PNG端点返回403，未继续追取，本文没有冒称采用高分辨率原始PNG。

正文保留作者、年份、原图号、论文链接、许可链接与无改动说明。来源论文的设备是研究实现，不可称已在ngVLA望远镜部署；原作者与出版社不为本文教学程序背书。本文没有移用50 fs数值去宣传自制仿真性能，也不把这套电路当作通用PLL所有部件的完整清单。

## 每图的新理解作用

| 文件 | 职责与来源身份 |
|---|---|
| 01-actual-locking.png | 同一实际计算0–3/24–27秒脉冲，先看边沿逐渐接近，不冒称仪器实测 |
| 02-real-pll-module.jpg | 原论文图1的真实模块照片，明确PLL可制成实际电路 |
| 03-period-frequency.png | 一秒重复次数与一次所需时间，分别定义Hz和周期 |
| 04-same-frequency-phase.png | 同频却保持0.25秒偏移，区分频率和相位 |
| 05-frequency-drift.png | 同序号周期的差距累积，说明频差与相差变化的关系 |
| 06-phase-circle.png | 主例0与0.25圈的进度、方向及误差符号 |
| 07-wrapped-error.png | 0.98到0.02跨零短差，交代包裹误差的选择 |
| 08-loop-structure.png | 真实读图路径贯通比较、控制、相位推进和反馈 |
| 09-first-control-step.png | 主例第0次先更新累计量再定频率，带具体单位 |
| 10-three-checks.png | 真实前三行记录，累计量不重置，改变后相位继续参与下一轮 |
| 11-lock-transient.png | 同一运行的频率和相位误差分开画，不混量纲 |
| 12-p-only-phase-offset.png | P-only与PI实际后期波形，固定相差也可同频 |
| 13-divider-multiplier.png | 同时间窗4个输出周期对应1个反馈周期，解释倍频闭环 |
| 14-tracking-speed.png | 两组明确PI系数追踪同一个频率突变，误差带和计时基准清楚 |
| 15-two-noise-sources.png | 把参考端与本振端扰动入口分开，避免统一噪声结论 |
| 16-noise-tradeoff.png | 两种扰动、快慢环路的实际去均值RMS；组内同刻度、组间明确不同 |
| 17-sampling-alias.png | 每0.1秒看一圈进度会把1与11 Hz混淆，限定模型捕获能力 |
| 18-real-pll-chip.jpg | 原论文图3显微照片，使振荡器/分频器/比较器在真实芯片中可见 |
| cover.png | 独立封面，采用主模型后期波形，不使用真实器件图冒称产品宣传 |

正文18张图中16张为原创解释/计算图、2张为同论文的不同真实图；封面另计。originals副本、同一图中的面板及手机代理都不是新增配图。图数只是清单，不作为解释充分的代替标准。

原创图由[制图代码](examples/build_figures.py)重建；[图像元数据](examples/figure-metadata.json)记录作用与字号。数字来自[预期结果](examples/expected-results.json)与[复现说明](README.md)所列独立模型，参考扰动和本振扰动是规定的正弦输入，不是随机噪声实测谱。

## 权利与AI辅助

- 原创正文、原创解释图、计算曲线/波形与封面：CC BY 4.0。
- 两张研究图片：按Braun等原作者CC BY 4.0单独保留信用、来源和修改说明，不冒称本文原创。
- 原创Python求解与制图脚本：MIT，完整文本见[LICENSE-CODE.txt](LICENSE-CODE.txt)。原厂资料与第三方软件权利仍属于其权利人。
- AI辅助用于一手检索、教学设计、文字起草、程序与制图代码、数字核算和审读。照片来自已核出处，不由AI生成；曲线和波形由实际运行的原创模型产生，并非伪实测、仿历史照片或假设备界面。
