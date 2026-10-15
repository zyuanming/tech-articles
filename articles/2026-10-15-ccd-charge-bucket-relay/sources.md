# 来源、图像与适用范围

核查日期：2026-10-15。正文的3×4输入、守恒账本、恒定效率比较及残留脉冲实验均为本篇原创教学设计；结果由随文代码实际运行产生。没有相机实测、物理实验室记录或NASA像素原始数据。

## 历史与机制的一手来源

1. W. S. Boyle、G. E. Smith，1970，*Charge Coupled Semiconductor Devices*，Bell System Technical Journal 49(4)，587–593。[出版页与DOI](https://doi.org/10.1002/j.1538-7305.1970.tb01790.x)。支持储存、转移、检测电荷的器件构想及论文已提出成像应用。另核对[原论文扫描件](https://vtda.org/pubs/BSTJ/vol49-1970/articles/bstj49-4-587.pdf)，此链接是第三方存档载体，证据是原文而非存档者的解释。原文使用n型基底/空穴等说明；本文采用常见电子收集方向作教学，不称它是原论文器件的逐项复刻。
2. G. F. Amelio、M. F. Tompsett、G. E. Smith，1970，*Experimental Verification of the Charge Coupled Device Concept*，同刊49(4)，593–600。[出版页与DOI](https://doi.org/10.1002/j.1538-7305.1970.tb01791.x)。支持实际器件实验验证的作者与年份。本文不把早期测试值当成现代器件参数。
3. [Nokia Bell Labs：2009 Nobel Prize in Physics](https://www.nokia.com/bell-labs/about/awards/2009-nobel-prize-physics/)。支持Boyle/Smith的器件工作及Tompsett团队的成像应用贡献。机构回顾不等于当年实验原始记录；原站部分文字有排版重复，未复制。
4. [Nobel Prize：2009年物理学奖官方记录](https://www.nobelprize.org/prizes/physics/2009/summary/)。支持获奖者及奖项份额；[Boyle访谈入口](https://www.nobelprize.org/prizes/physics/2009/boyle/interview/)可了解其回忆，本文没有把回忆写成虚构对白。不同机构资料对1969年构思会面的具体月份叙述不一，本文只使用共同确认的年份，不裁定具体日子。
5. [Teledyne e2v：How a Charge Coupled Device (CCD) Image Sensor Works](https://www.teledyne-e2v.com/en-us/Solutions_/Documents/2020-01-22_e2v_how-a-charge-coupled-device-works_web.pdf)。支持埋沟道、栅极、列隔离、并行/串行转移、模拟电荷与后端数字化、量子效率。本文没有采用其“典型器件”性能值作为统一规格。另参考[50 Years of the CCD](https://www.teledyne-e2v.com/en-us/Services_/Documents/The%20Ultimate%20CCD%20Fab/50thAnniversaryoftheCCDDevice.pdf)核对历史资料范围，未复用宣传图片或未来任务预测。
6. [Nikon MicroscopyU：Introduction to Charge-Coupled Devices](https://www.microscopyu.com/digital-imaging/introduction-to-charge-coupled-devices-ccds)。重点核对三相栅极、交叠时序、相邻包隔离、二维到串行读出。本文三相7时刻、数字矩阵及图形布局为独立教学设计。原站对市场常见程度和典型速度的概括具有年代性，本文不将其当成2026年市场统计。
7. [Hamamatsu：CCD image sensors技术资料](https://www.hamamatsu.com/content/dam/hamamatsu-photonics/sites/documents/99_SALES_LIBRARY/ssd/ccd_kmpd9002e.pdf)，39页。重点为1-1结构类型、1-2两相转移、1-3输出节点、2-1转换系数、2-5满阱、2-7转移效率和滞后、2-8/2-9暗电流及噪声。两相结构不能直接当作三相结构，本文相应区分。恒定η幂次模型与定向溢出规则不是厂商算法。
8. [Hamamatsu：Image sensors product selection](https://hub.hamamatsu.com/us/en/technical-notes/image-sensors/image-sensors-product-selection.html)，2017技术说明。支持全帧式读出、快门/照明配合与smear的关系；不作为具体相机选购建议。
9. [Hamamatsu：Advances in CMOS image sensors](https://hub.hamamatsu.com/us/en/technical-notes/image-sensors/advances-in-cmos-image-sensors.html)，2015技术说明。支持典型CCD与CMOS有源像素的信号读出/集成方式差异；不外推“CMOS每像素一个ADC”或绝对画质排序。
10. [STScI：ACS WFC CCD Detector Charge Transfer Efficiency](https://hst-docs.stsci.edu/acsdhb/chapter-4-acs-data-processing-considerations/4-6-wfc-ccd-detector-charge-transfer-efficiency-cte)。支持辐射损伤、陷阱与转移问题。[WFC3：The Nature of CTE Losses](https://hst-docs.stsci.edu/wfc3dhb/chapter-6-wfc3-uvis-charge-transfer-efficiency-cte/6-3-the-nature-of-cte-losses)支持暂时俘获与迟释放；[STIS成像说明](https://www.stsci.edu/hst/instrumentation/stis/observing-strategies/imaging)支持饱和电荷沿列溢出的实际仪器注意事项。本文0.9残留比例只是人为放大，不等于这几台仪器的性能或校正模型。
11. [NASA：哈勃设计](https://science.nasa.gov/mission/hubble/observatory/design/)及[高级巡天相机ACS](https://science.nasa.gov/mission/hubble/observatory/design/advanced-camera-for-surveys/)。支持照片身份及实际CCD应用。本文未把ACS所有通道都称为CCD。

## 第三方图像及原件范围

唯一在本篇公开复用的第三方图片是 `assets/01-nasa-acs-detector.webp`。

- 来源：[NASA图片文件](https://science.nasa.gov/wp-content/uploads/2023/05/hubble-acs-jpg.webp?w=1227)，[身份页](https://science.nasa.gov/mission/hubble/observatory/design/)。原站署名NASA，内容为工作人员手持ACS探测器组件。
- 保存的是原站直接提供的1227×1535像素WebP文件，原字节未改。不是最高分辨率原摄文件，也不是截屏或生成图。下载后的SHA256为`6bb42ab8a6da25bbdf7e38eedcf4a9f3d73eaf943d2d5b99fdf364c806c58933`。
- 依据[NASA Images and Media Usage Guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/)用于事实性教育说明，并标示NASA来源；不表示NASA或照片中人物认可本文。该素材不纳入本文作者的CC BY再授权。NASA明确指出其网站上另有第三方受保护内容，不能把该一般规则外推到所有图片。

其余相关原件已逐项盘点，但未获得可再发布许可者仅提供原站链接：

- Boyle/Smith原论文共3张编号图：图1能带/储存条件，图2三相MIS转移（含a、b、c三个面板），图3电荷量与器件参数关系。扫描件包含完整587—593页及下一篇实验验证论文的起始部分；不能据此声称已收齐后者全文。本文不转载这些原图。
- Nikon正文共有10个编号SVG：1显微成像相机、2 MOS结构、3像素结构、4格式、5接力类比、6三相时钟、7三类架构、8微透镜、9合并像素、10光谱响应。正文信息图整体盘点；导航/品牌标识及重复推荐不算相关教学图。原SVG保留其权利，未加入本篇公开文件。
- Hamamatsu完整39页技术PDF可查看全部图；与本文核心直接相关的图包括1-1至1-8的结构/转移/输出，2-9/2-10的效率及滞后。其他关于TDI、驱动布线、器件封装及特定型号参数的图不作为本文展开对象，不伪称它们都是本篇配图。
- Teledyne资料中有关器件照片、历史记录、剖面、阵列和转移的原图未公开复用；访问渠道可读文本，但本次原PDF文件取得受限，未规避限制。本文没有用虚构的历史照片替代。
- Bell Labs及Nobel历史人物/实验影像保留原站链接，不复制到公开包，不生成仿历史照片。

## 原创图与程序

`assets/02-*.png`至`assets/15-*.png`及`cover.png`由本篇Python程序化绘制；14张正文原创图+1张独立封面。加上NASA照片，正文15张图。图07、08、11、12、13引用实际执行的模型输出；其他图为机制或历史贡献示意。相位曲线是逻辑状态，不是示波器记录；势阱是电子势能示意，不是芯片的实际剖面深度。

完整重现入口：[README.md](README.md)。模型原始数据、所有断言与输入位于examples；首次运行输出位于originals。

## AI辅助与许可

本篇使用OpenAI AI助手完成资料检索与对照、中文撰写、原创Python代码、模型运行、原创程序化图形及排版检查。没有声称由作者亲自操作CCD硬件或访问实验室。NASA实物照片来自真实原站文件，不是AI生成；没有生成任何伪历史照片。AI输出仍可能有误，本文提供原始来源与可执行规则供读者核查。

原创文字、原创教学图：Creative Commons Attribution 4.0 International（[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）。引用时标注本文标题、来源与改动。原创代码：MIT（[完整许可](LICENSE-CODE.txt)）。原始教学数据可随原创材料按CC BY 4.0使用。第三方照片、论文、品牌标识及链接资料各自保留权利，不因本文许可而被统一再授权。
