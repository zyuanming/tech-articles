# 来源、图像与可复现实验

原创中文正文由zyuanming发布，采用CC BY 4.0。该许可不自动覆盖照片、原论文、代码或其他素材。本文使用AI辅助研究与写作；除一张有独立署名和许可的实物照片外，教学图及动画按明确坐标、公式与实验结果编程生成，不是设备实测或历史录像。

## 一手事实与范围

1. J. E. Bresenham, “Algorithm for computer control of a digital plotter”, IBM Systems Journal 4(1), 25–30 (1965), DOI 10.1147/sj.41.0025。[公开扫描件](https://www.cse.iitb.ac.in/~paragc/files/bresenham_line.pdf)。支持八方向网格模型、整数增量判别、八象限处理，以及第29页的333个core locations和约1.5毫秒这一特定历史报告。第30页说明论文基于1963年8月30日的会议报告，并列出先行工作和致谢。已读六页；本文代码是独立教学实现，不是原Autocoder程序。
2. Paul E. Black, NIST Dictionary of Algorithms and Data Structures，[Bresenham’s algorithm](https://xlinux.nist.gov/dads/HTML/bresenham.html)，条目修改日期2020-12-14。页面收录Bresenham于2001年提供的回忆，支持1962年夏已使用、IBM1401/1407/CalComp这一组合，以及1963会议、1965刊发的区分。回忆不冒充同时代日志。条目还指向其1987年“Ambiguities in incremental line rastering”；本文仅据NIST确认该文存在，不宣称读过其全部内容。
3. [Computer History Museum 1401项目的Bresenham资料页](https://ibm1401.computerhistory.org/BresenhamLineDraw.html)用于交叉定位原始扫描与作者通信。网页混有恢复者讨论、联系信息及与本题无关的图像；本稿不收录私人联系方式，不采用无关画像，不将恢复者推测当作者原话。正文历史主线依照上面两项。

## 1965论文信息图覆盖

原论文不是本库原创，也未在该扫描件中核到开放复用许可，因此不把整页扫描或图版改标为CC再发布。读者可从原件逐页核对；本稿以不同的自设坐标和中文教学图解释全部五项图示职责，不冒称这些新图是原图：

- 原Figure 1，八种移动，第25页（PDF第1页）：本文03-eight-moves。
- 原Figure 2，曲线由线段拼接，第25页：本文22-curve-before-line。
- 原Figure 3，离散移动与理想线段，第26页：本文01、09、11。
- 原Figure 4，候选点和误差几何，第27页：本文05、06、07、12。
- 原Figure 5，八区域坐标方向，第29页：本文13、14、18。

这是原件访问与教学覆盖说明，不是原论文图像复用授权。

## 真实设备照片

assets/calcomp-565-original.jpg：Ryan Somma，[Calcomp 565 drum plotter](https://commons.wikimedia.org/wiki/File:Calcomp_565_drum_plotter.jpg)，[Flickr原发布页](https://www.flickr.com/photos/14405058@N08/3242804326)，CC BY-SA 2.0，许可链接：https://creativecommons.org/licenses/by-sa/2.0/ 。

采用Commons原文件3072×2048，2,573,390字节，未裁切、未改色、未放大。原文件SHA-1 a6573625a217ecd93b5dd3f560f1795a3a3caace 与文件页结构化数据一致。仅网页/CSS显示尺寸可缩放，仓库保存原字节。照片日期未知，EXIF的1980年日期已被文件页标为无效；约1966指文件页对展品的描述，不是摄影日期，也不代表Bresenham最早使用的那台机器。

02-plotter-mechanism是新绘制的机构概念图，没有修改此照片；尺寸、材质、细节不是复原结论。照片不纳入正文CC BY 4.0。本页保留作者、原文件页、许可和未改动说明。

## 人物肖像的核查与未采用范围

已主动检索Bresenham肖像，并核对[IT History Society人物页](https://ithistory.org/honoree/jack-elton-bresenham)及其[使用条款](https://ithistory.org/terms)。该页有肖像，但图片署名处为“Unknown”，未给出可覆盖本公开仓库再分发的开放许可；条款中的在校学生无偿学习用途并不自动适用于本稿。因此仅链接原站，不下载或再发布这张肖像。[Wikidata Q92833](https://www.wikidata.org/wiki/Q92833)当次核查未列image声明，Commons检索也未找到身份和许可均可核的本人肖像；这不等于断言任何地方都没有。本文以实物照片、原始论文出处及中文机制图承担历史与技术的视觉解释，不生成仿真人像。

## 24幅正文图与实验身份

共24幅正文图：1幅第三方实物照片、22幅原创静态教学图、1幅原创12帧动画。不是将同一图机械裁成许多张。

01理想线与格点；02机构；03动作集合；04候选步骤；05前两列距离；06中点；07整数判别量；08两种递推；09实际12状态动画；10纵向误差界；11只守终点的反例；12垂距与纵向误差关系；13主轴交换；14八方向；15边界输入；16平局；17未统一方向的歧义；18规范化；19代表格与穿过格的差别；20简化灰度权重示意（不是面积覆盖实测）；21端点取整改变几何；22上游折线近似；23读者手算。

例子采用数学坐标y向上。屏幕API可能y向下，移植时必须统一坐标。09动画可用静态帧理解，不依赖声音。23的练习与正文答案一致。

[完整实验](examples/line_experiment.py)只用Python 3标准库，输出判别账本并检查6561组格点端点。Fraction参照直接按最近整数定义重算，不使用相同的误差递推。验证范围包含正反方向、点、水平、竖直、陡线与负坐标；不是性能跑分、GPU测试或硬件实测。

算法合同：整数中心格点；含两个端点；每主轴位置一个代表点；统一方向解决平局；反向输入产生相反输出次序。并未包含裁剪、任意线宽、亚像素端点、抗锯齿、全部相交格枚举或机械运动规划。
