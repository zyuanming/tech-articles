# 来源、图像身份与复算范围

本文面向从零理解光学测转动的读者。叙述、逐步推导与16幅教学图为原创；这些教学图中的波形、几何和读数均是明确参数下的模型。2026-10-26 另补 ROMY 论文的真实装置照片与实测拍频图，身份分别说明，不能混称为本文亲测。

## 一手来源支持什么

1. [Guido Rizzi、Matteo Luca Ruggiero，A direct kinematical derivation of the relativistic Sagnac effect for light or matter beams，2003](https://arxiv.org/pdf/gr-qc/0306128)。支持圆环的惯性系交会、相对论速度合成、局部共动系与固有时间差。本文用独立代数展开讲解，不复制论文插图。已核读相关推导的解析文字，未取得原 PDF 图像像素，未将后部未读范围当作全文核验。
2. [Amos Ori、Joseph E. Avron，A Generalized Sagnac-Wang-Fizeau formula，2016，v2](https://arxiv.org/html/1601.01448v2)。支持低速线积分、面积向量、整体共转介质中折射率抵消的条件，以及伸缩、流动介质为何属于不同问题。实际阅读了导论与相关推导窗口；没有把全文或所有原图像素说成已核。本文没有复制其四幅原图。
3. [GINGERINO 研究团队，2017 年实验论文，arXiv:1702.02789v1](https://arxiv.org/html/1702.02789v1)。支持真实环激光系统、合束与单方向光强读出、背向散射修正和地面旋转测量用途。已读该版本完整解析正文及九幅图注；未取得原图像素。其 arXiv 展示不自动授予本文复制装置照片的权利，因此没有转载。
4. [GINGERINO 团队，2024 年双输出与噪声分析研究](https://www.frontiersin.org/journals/quantum-science-and-technology/articles/10.3389/frqst.2024.1363409/full)。支持原始拍频与校正后 Sagnac 频率的区分、双输出和激光动力学问题。已核相关正文窗口和版权段落。图1为装置布局示意，图2为噪声分析结果；未取得两图原像素，不把布局示意当作实物照片。

5. [Heiner Igel, Karl Ulrich Schreiber, André Gebauer, Felix Bernauer, Sven Egdorf, Andrea Simonelli, Chin-Jen Lin, Joachim Wassermann, Stefanie Donner, Céline Hadziioannou, Shihao Yuan, Andreas Brotzer, Jan Kodet, Toshiro Tanimoto, Urs Hugentobler & Jon-Paul R. Wells（2021），ROMY: a multicomponent ring laser for geodesy and geophysics](https://doi.org/10.1093/gji/ggaa614)，*Geophysical Journal International* **225**(1), 684–698，DOI: 10.1093/gji/ggaa614，Advance Access 2021-01-05。本次核读出版版 PDF 的摘要、装置说明及图2、图4周围正文和原图像素；支持 ROMY 地点、四个约12 m边长量级的三角形环布局（设计边长12 m，实际顶部环周长略小）及图示装置部件、水平环实测553.55 Hz拍频和24 bit/5 kHz采样条件。未将其全部地震观测结论作为本文已复算事实。

各来源只支撑上述限定事实。正文的 R=0.1 m、1550 nm、1000 匝是自设教学算例；另一组 3.6 m 方环、632.8 nm、45°法向夹角也是量级模型，不重建 GINGERINO 的真实地点、纬度或安装朝向。0.01°/s 的零偏是假设输入，不是某设备性能。

## 原创图逐项说明

|文件|解释义务与数据来源|
|---|---|
|00-cover.png|封面提出同环反向比较，非装置照片|
|01-loop.png|分束器、三面镜、两反向闭环与检测端；错开线仅为辨认|
|02-rest.png|静止基线与 L/c，用实际算例 JSON|
|03-chase.png|顺向追赶；另设 v/c=0.2 的放大演示，弧角来自 JSON|
|04-meet.png|逆向迎面交会；同一放大模型，不同接收事件|
|05-spacetime.png|展开圆周与两条光轨迹、B 世界线；交点由模型计算|
|06-phase.png|延迟与光周期比例；多匝波形读取实际相位，非实测|
|07-area.png|同周长异面积，边长共用实际比例尺|
|08-projection.png|面积法向与角速度夹角；0/60/90°数值逐一计算|
|09-turns.png|同纤长不同绕向，条长按真实匝数共轴，净面积相减|
|10-medium.png|局部介质速度、实验室速度合成、交会计算三个步骤|
|11-cosine.png|无偏置端口的偶对称与零斜率，实际计算301点|
|12-bias.png|正交偏置只在局部提供带符号读出，仍有周期歧义|
|13-ringlaser.png|腔内增益、反向振荡及拍频；概念结构而非设备照片|
|14-earth.png|地球转轴与假设45°环法向投影，角度及频率来自 JSON|
|15-drift.png|假设固定零偏的积分误差，实际逐秒计算|

上述16幅原创 PNG 为 1062 px 宽，关键字最小 40 px；画布随内容裁剪。图形程序检查字体字形、文字重叠、框内外边界、墨迹、对比与尺寸。数值标签及定量图形从 `examples/results.json` 读取；屏幕布局位置不代表物理尺度。作者还逐图检查原尺寸及 354 px 静态缩小代理，代理不是浏览器截图，也不能替代真实手机排版验证。

## 真实素材的核查范围与历史限制

真实硬件和实际干涉效果有独立的解释价值，不能用上述原创图冒充。已查的一手候选包括 [2020 年 GINGER 研究综述](https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2020.00049/full) 的 GP2 原型、GINGERINO 装配照片，以及 [2025 年等离激元非互易性实验](https://arxiv.org/html/2506.08815v1) 图1的 Sagnac 布局与实际干涉图。前者相关图注和文章版权说明可读，后者明确显示 CC BY-SA 4.0，但此前均未取得可使用的原图文件。因此本稿没有转载这些候选图，也没有生成假实拍替代。

2025 年实验测的是材料引起的非互易性，不能把其干涉图标成旋转陀螺测量。2017 年论文的可见照片亦不因公众可访问而自动获得转载授权。源码仓库的代码许可不能泛化到第三方照片或模板内素材。此前的 STOP / HOLD 原因是关键真实装置／实际效果图缺失；“已有16幅原创图”不能消除该缺口。2026-10-26 改以合法取得的 ROMY 出版版图2与图4补齐这两类证据；此前未取得素材的记录仍保留，不回写成当时已核。这里不声称原来源全部像素、完整 HTML 素材列表或未读取的段落已经检查。

## 许可与制作说明

中文正文、说明文档与 `assets/` 中16幅原创 PNG 按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 提供，署名为 zyuanming/tech-articles，链接本篇并说明修改。`examples/` 中 Python 程序、计算输出 `results.json` 和图形元数据按 [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) 提供；其中 `README.md` 仍属于 CC BY 4.0 文档。画布验证 API 沿用本仓库本批 Quickselect／电泳显示文章已按 CC0 提供的工具基础，本篇构图、模型和数据另写。新增的第三方图按下面逐图授权与署名使用；本库原创许可不替代其原作者权利。

本稿使用 AI 辅助检索、中文写作、推导检查和 Python 绘图，实际执行程序核算数值。程序验证的是所声明模型的计算一致性，不是对真实仪器性能的测试。图形不是图像生成模型合成的实验照片。事实、素材完整性与图义仍须独立审读。

## ROMY 第三方图：署名、许可与处理

出版版首页标明 © The Author(s) 2021，Published by Oxford University Press on behalf of the Royal Astronomical Society，并采用 [Creative Commons Attribution 4.0 International（CC BY 4.0）](https://creativecommons.org/licenses/by/4.0/)（[完整许可条款](https://creativecommons.org/licenses/by/4.0/legalcode)）。使用时须保留原作者与来源、许可链接并说明修改。图2摄影署名如下；图注和本次核读范围未见这两图另列排除复用条款，但这不等于独立审计了全部摄影权利链。

|仓库文件|原图定位、原始尺寸与署名|处理及解释用途|
|---|---|---|
|`originals/photos/romy-2021-figure2.jpg`|论文图2，印刷页687（PDF第4页），2343×1596；论文作者 Igel et al.；摄影(a) Fa. Wadle，(b)–(d) J. Igel|从PDF抽取嵌入JPEG原字节，未缩放、未裁剪、未重绘；展示施工与实际部件；中文图注为翻译说明|
|`assets/16-romy-measured-beat.png`|论文图4，印刷页688（PDF第5页），1984×1253；论文作者 Igel et al.，未另列摄影署名|从PDF无损抽取灰度图为PNG，未缩放、未裁剪、未改动曲线；解释水平环实际电压信号及采样；中文读图与周期换算为新增说明|

两图均沿用上述 CC BY 4.0。源出版版PDF的 SHA-256 为 `114a4b44595b83f2fded42b85735a39e5d43a073b198717be6610c6d0a1715d0`。只转载与本文解释直接相关的图2、图4；不把图3结构示意冒充实物。原图保留英文标记和坐标，正文另以可缩放文字解释 a–d、秒、伏、采样点和关键读数；没有用生成模型替代原像素，没有把页面渲染图冒充原嵌入图。

补材使用 AI 辅助中文说明、来源整理及一致性检查；论文实测由原研究团队完成。本次没有复测 ROMY、没有取得原始采样数据，也不把 553.55 Hz 和自设方环的约293.3 Hz作为同一条件下的对照实验。

原图注（保留原编号与摄影署名）：

> Figure 2. ROMY construction and final installation: (a) Drone view of the excavated volume, the concrete hull and the top-up construction of the tetrahedral structure (photo: Fa. Wadle). (b) Examples of laser light generation at the centre of the horizontal side tubes. (c) Setup of the rigid bottom plate with the corners of the three inclined ring lasers. (d) View down the central shaft to the tip of the tetrahedron shown in (c). [(b)–(d) photos: J. Igel].

> Figure 4. Example of the time-domain signal obtained from the horizontal ring. The Sagnac beat note of 553.55 Hz is sampled by 24 bit digitizer at 5 kHz sampling rate.
