# 来源与素材记录

核对日期2026-10-11。原创中文正文由zyuanming发布，采用CC BY 4.0；该声明不自动扩展到原创图片、代码或第三方素材。

## 一手来源与范围

- Jack E. Volder，The CORDIC Trigonometric Computing Technique，IRE Transactions on Electronic Computers EC-8(3)，1959年9月，330–334。原文：https://www.ece.ucdavis.edu/~vojin/CLASSES/EPFL/Papers/3-Volder_CORDIC.pdf 。实际读取扫描首页与旋转推导页；作者、机载实时计算目标、三移位寄存器与三加减器据原文。未使用未经一手核实的飞机型号、个人轶事或历史性能倍数。
- David S. Cochran，Algorithms and Accuracy in the HP-35，Hewlett-Packard Journal，1972年6月，10–11页。HP官方原文：https://www.hp.com/hpinfo/abouthp/histnfacts/museum/personalsystems/0023/other/0023hpjournal03.pdf 。实际读取两页，核对算法选择、十进制尺度、重复减角及计数；不把其方法等同本文固定轮数二进制程序。
- HP官方历史展页：https://www.hp.com/hpinfo/abouthp/histnfacts/museum/personalsystems/0023/index.html ，用于核对1972年设备背景。正文未复述销量、引语和市场调研故事。
- STMicroelectronics AN5325，How to use the CORDIC to perform mathematical functions on STM32 MCUs，实际核对版本Rev 8（June 2026）：https://www.st.com/resource/en/application_note/an5325-how-to-use-the-cordic-to-perform-mathematical-functions-on-stm32-mcus-stmicroelectronics.pdf 。用于说明真实外设的输入缩放、参数范围、位宽与迭代精度是具体接口合同；不是本文实验的平台。本篇未引用该文速度基准或整套支持芯片名单。

本文数学推导采用自设30°例子、i从0开始的二进制圆周旋转、固定N轮、每步d取±1。G_N专指放大，K_N专指倒数补偿。短代码是浮点教学程序，只演示30°，不是无乘法指令的定点实现，不含全角域归约。误差曲线由本文代码实际计算。

## 原图与历史设备的处理

本篇为多来源原创机制讲解，不是历史论文或ST应用说明的逐节翻译。历史扫描文献与厂商应用说明中的接线、误差、性能图未获得本稿开放再分发依据，因此只链接原文，不复制为本篇插图。本文概念电路不是原机接线图，数值图不是厂商实测。

Seth Morabito的《HP 35 Calculator》2007年设备照片，原页面https://commons.wikimedia.org/wiki/File:HP_35_Calculator.jpg 明示[CC BY 2.0](https://creativecommons.org/licenses/by/2.0/)，2027×2283像素，原件1519457字节。本稿未取得本地原文件，故只提供原站查看链接，不用截图、缩略图或生成图片冒充原件。没有将元数据授权与其他博物馆的图片授权混为一谈。

Volder与Cochran只承担必要历史归属，没有采用复用依据未核实的肖像，未以生成真人像替代。

## 原创图

18幅1200×840 PNG均由examples/generate_figures.py生成（Python、NumPy、Matplotlib、Noto Sans CJK）。01–04是坐标旋转与特殊斜率；05是非负整数移位；06–08用正文精确坐标表示前三轮；09用实际浮点计算残差；10为确定的放大因子乘积；11预补偿；12角度常数；13同步状态更新；14固定小数位量化概念；15实算不同轮数正弦误差；16象限归约；17为(3,4)向量的几何目标示意，不冒称运行了向量模式硬件；18是两种进制尺度的机制对照。

本文使用AI辅助调研与写作；教学图由代码按明确坐标和实验生成，原理示意、实际数值计算与历史事实已区分。
