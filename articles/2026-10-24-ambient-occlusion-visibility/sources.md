# 来源与素材说明

本文由AI辅助研究、写作、程序实现和制图，程序已实际运行。正文、图和数据由zyuanming发布，CC BY4.0；原创代码MIT。没有第三方图像、游戏资产或人物照片。

## 实际读取的一手技术材料

- Matt Pharr、Simon Green，[GPU Gems Chapter17: Ambient Occlusion](https://developer.nvidia.com/gpugems/gpugems/part-iii-materials/chapter-17-ambient-occlusion)：环境可达性、半球查询、预计算及平均未遮挡方向的含义。章节的基本计数使用均匀半球方向；本文明确改用余弦分布，不能混同二者估计量。未照译章节，未采用历史人物故事。
- PBRT原作者著作，[Sampling Multidimensional Functions，A.5.3](https://pbr-book.org/4ed/Sampling_Algorithms/Sampling_Multidimensional_Functions#Cosine-WeightedHemisphereSampling)：余弦半球分布及均匀圆盘投影思想，实际读取相关段落。本文代码使用极坐标圆盘变换，不复制书中同心圆实现。

本文的球/地面场景、8方向实例、128方向图像、距离与高度比较及数值反例均为原创自设计算。原理以明确简化模型解释，不是对任一现行引擎默认参数或版本的实测。

上述材料原图没有明确逐图公开复制依据，本篇不归档。算法输入、输出、半球、方向信息丢失等关键视觉由原创程序与几何示意覆盖；没有用生成图片冒充真实软件界面。模型本身是数学场景，实际运行的结果是该模型的实证，不是现实光学实验。

## 配图职责与身份

原链接均为 [lab.py](examples/lab.py)及[results.json](examples/results.json)。所有14图署名zyuanming、CC BY4.0，没有第三方变更。图01兼入口图。具体像素尺寸、字号和计算自检见[figure-metadata.json](examples/figure-metadata.json)。

|文件|作用|
|---|---|
|01-render|真实射线计算：均匀底色与AO对照|
|02-hemisphere|半球二维切面示意，不作3D计数|
|03-eight|八个实际方向及命中结果|
|04-cosine|等截面束的投影解释|
|05-distance|同一方向序列、不同最大距离的实际输出|
|06-lift|同一场景球抬高的实际输出|
|07-samples|8与128样本的实际输出|
|08-offset|自相交偏移示意，偏移刻意夸大|
|09-light-direction|方向亮度信息丢失反例|
|10-screen|屏幕空间信息缺失示意|
|11-normal|表面朝向与采样半球|
|12-double|重复乘可达率的真实灰度对比|
|13-bounce|AO不计算墙面反弹的路径示意|
|14-profile|相同方向计算的地面剖面|

图像统一在线性颜色计算后转sRGB显示；图中大场景为180×150原始计算结果放大，不声称额外真实细节。全部射线只与一个球和无限地面求交，不含网格加速、SSAO、GPU或完整路径追踪。字体只用于位图渲染，不分发字体。
