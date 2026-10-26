# 事实、图像与许可

> **公开状态：待补真实素材稿，整体仍为 HOLD。** 2026-10-26 先公开现有稿件，不代表真实素材缺口已解除或独评已正式通过。尚缺可合法复用的真实液滴形成、颈缩断裂或稳定单滴过程，以及实际沉积印迹。已有装配照片不能证明这些效果；未确认使用权的液滴样本未收录，断滴示意与模型曲线不是实拍或自由表面仿真。

本文为全新中文解释与教学推导。正文及assets目录中的原创PNG由zyuanming发布，采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；Python代码与原创计算JSON采用[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/)。第三方材料独立标注，不受上述原创内容许可覆盖。

## 一手事实来源

- [MicroFab：Ink Jet Microdispenser](https://www.microfab.com/support/a-basic-ink-jet-setup/ink-jet-microdispenser)。已读完整解析正文，支撑管式压电器件、极性与变形、负压波向两端传播、供液端反射、液面移动与频闪观察。厂商图没有查到开放复用许可，未复制其照片、过程帧或结构图；原创图只说明自行设计的教学对象。
- [MicroFab：Drive Electronics](https://www.microfab.com/support/a-basic-ink-jet-setup/drive-electronics)。已读完整解析正文，支撑单极、双极、多段驱动以及时序和观测的角色。不将特定型号的电压限制或默认参数推广到其他设备；未复制其波形图或软件界面。
- [Herman Wijshoff，Drop formation mechanisms in piezo-acoustic inkjet，2007](https://briefs.techconnect.org/wp-content/volumes/Nanotech2007v3/pdf/696.pdf)。已读4页完整解析文字与图注，支撑声阻抗反射、实际观测与模拟的区别、尾部断裂与卫星类型、补液和喷嘴板润湿。未取得原版图像像素，未复制论文的实拍或Flow3D模拟图。正文数值没有使用论文中的设备参数。
- [CentroEPiaggio / IPJ-Bio项目](https://github.com/CentroEPiaggio/IPJ-Bio)。已读README与完整根许可、核对项目文件，并查看原装配图。用于设备构造的真实例证，不独立核验README提到的细胞存活实验，不作医疗结论。
- [Cavaleiro de Ferreira等，Development of an Inkjet Setup for Printing and Monitoring Microdroplets，2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9694169/)。实际已读解析文本第0—376行对应的内容，涵盖方法、结果、图1—9与表1—2的文字；补充材料只定位到清单，没有读取原文件。它使用落地滴图像进行监测，不能当作断滴高速序列。本篇未采用它的图像或实验数值；原图访问受到浏览器检查限制，未取得像素。

正文中的纳米位移、1µL腔体、30pL自由行程、顺应性、10mm声学距离、30µm喷嘴及液体参数全部是教学设定。封闭压力、脉冲叠加和局部流量是三个边界条件不同的计算；图与数值不声称设备测量、自由表面仿真或商业喷头拟合。几何、守恒、牛顿第二定律、圆管层流近似和无量纲换算由本文自行展开并复算。

## 逐图身份与作用

| 文件 | 理解作用 | 身份与许可 |
|---|---|---|
| assets/00-cover.png | 建立电压、壁面、压力波与液滴链条 | 全新原创示意，CC BY 4.0 |
| assets/01-structure.png | 辨认储液器、腔、驱动层、喷嘴与液面 | 全新原创概念剖面，CC BY 4.0 |
| assets/02-wall-motion.png | 比较扩腔和回缩，不固定所有器件极性 | 全新原创示意，CC BY 4.0 |
| assets/03-volume-account.png | 区分封闭压力极限与开放液路流量 | 原创示意与设定参数计算，CC BY 4.0 |
| assets/04-reflection.png | 呈现波的往返方向与时间 | 原创声学近似示意，CC BY 4.0 |
| assets/05-wave-timing.png | 共轴显示配准/错开的叠加差异 | 实际计算的线性脉冲模型，CC BY 4.0 |
| assets/06-nozzle-forces.png | 解释惯性、阻力与毛细的压力预算 | 原创集中参数示意，CC BY 4.0 |
| assets/07-flow-curve.png | 区别瞬时流量与时间积分体积 | 实际解析模型输出，CC BY 4.0 |
| assets/08-breakup.png | 指认液柱、细颈、主滴与可能的卫星 | 原创定性形状，非模拟，CC BY 4.0 |
| assets/09-viscosity.png | 同尺度比较只改变黏度的体积响应 | 实际解析模型输出，CC BY 4.0 |
| assets/10-deposition.png | 区分飞行球径与落地铺展 | 原创球冠计算，两球冠等体积同尺度，CC BY 4.0 |
| assets/11-voltage-stages.png | 对应电压边沿与壁面动作 | 全新原创波形示意，CC BY 4.0 |
| originals/photos/ipj-bio-assembled.jpg | 辨认真实项目的部件与装配 | 第三方CAD及实物合图，GNU GPL v2，见下 |

## IPJ-Bio原件通知

来源：CentroEPiaggio / IPJ-Bio项目，原路径[Mechanics/assembled.jpg](https://github.com/CentroEPiaggio/IPJ-Bio/blob/33806b218e556edcab5219b16a0e871598955aed/Mechanics/assembled.jpg)，固定提交`33806b218e556edcab5219b16a0e871598955aed`，取得日期2026-10-25。

本库[原件](originals/photos/ipj-bio-assembled.jpg)保留3397×1902像素和原始3,740,538字节，未裁切、未添加标注、未重编码。左a是CAD分解，右b是实物照片；不将整幅称为实拍，也不将CAD重绘称为真实设备内部照片。SHA256为：

5d3e9f186515a482d53fc84ca3c9d23f49d8dbee61602ff71ddcb4686fef9fbd

按该第一方项目根目录GNU GPL Version 2许可，以项目文档原文件身份再分发；保留[完整许可](originals/ipj-bio/GPL-2.0.txt)与[原README](originals/ipj-bio/README.upstream.txt)。这不是作者逐图另发的CC授权，也未查明单独摄影者。判断依据是项目自述的设计制造范围、文件所在Mechanics目录、根许可适用全项目及未见相反的逐图版权通知；不是把任何代码仓库许可外推给第三方转载照片。

上游同时提供机械STL及电路源文档，可从[固定版本目录](https://github.com/CentroEPiaggio/IPJ-Bio/tree/33806b218e556edcab5219b16a0e871598955aed)取得；不声称存在未公开的JPEG可编辑合成文件。另一张项目电路PNG已登记但未转载：本文不讲电路设计，真实装配与原创驱动机制已承担本篇相关职责。

## 尚未补齐的真实效果

本稿保留了装配实物，尚未取得可在本库复用的真实液滴过程和落地效果。MicroFab过程帧未查到开放许可；2022论文图页未取得像素。另查[Hashemi等2025预印本](https://arxiv.org/html/2501.13801v1)，已读完整解析正文，论文图文件访问受限；已取得的作者样本另受数据许可约束，具体版本未核实，未转载。原创断滴示意与模型曲线不能替代这些实证。

## AI辅助与验证范围

本篇中文组织、代码、计算、图形与来源核对使用AI辅助。公式和数值实际运行，图的字号、包围盒、字形、对比与比例经过程序检查，并实际查看原图与手机比例静态代理。没有实际连接喷头、测量压力或拍摄液滴。照片为来源作者记录。静态代理不是平台截图，程序检查也不是独立审读结论。
