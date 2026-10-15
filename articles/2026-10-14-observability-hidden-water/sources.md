# 来源、模型身份与素材权利

正文：[read.md](read.md)。资料核查与计算日期：2026-10-14 UTC。

## 一手资料

### Stephen Boyd、Sanjay Lall：离散可观测性

[Stanford EE263官方讲义：Observability and state estimation](https://ee263.stanford.edu/lectures/observ.pdf)，7页。

第2页明确模型与输入已知、扰动和测量误差另列；第4–5页用有限次输入、输出恢复初态；第6–7页说明不可区分方向与可观测矩阵。用于核对本文的离散、参数已知、同一已知输入、初态可区分性，以及两步观测系数表。PDF元数据时间不被当作课程讲授或初次发表年份。

本文水量规则、具体数字、图的几何布局和Python程序均为新的教学设计，不是该讲义的实物实验或原例复制。讲义没有提供本文图片的开放复用许可；公开包只链接原文，不收录幻灯片截图。

### R. E. Kalman，1960年原文

[Contributions to the Theory of Optimal Control，教师托管重印扫描](https://liberzon.csl.illinois.edu/teaching/kalman_paper.pdf)。Boletín de la Sociedad Matemática Mexicana, Vol.5 (1960), pp.102–119；当前扫描重印页码149–166，不混同原期刊页码。

核对重印首页及158页：原文已明确讨论可控性与可观测性，支持历史段的年份与概念归属。未声称其独创全部状态空间思想，也不把新编双水箱当作原论文装置。重印自身得到的许可不是本文的再传播授权，不复制论文页或公式截图到公开assets。

### R. E. Kalman，1963年原文

[Mathematical Description of Linear Dynamical Systems，Duke教师托管原文](https://people.duke.edu/~hpgavin/SystemID/References/Kalman-JSIAM-1963.pdf)；[DOI与出版者记录](https://doi.org/10.1137/0301010)。J. SIAM Control, Series A, 1(2), 1963, 152–192。

核对首页、原页162–165、169–170：内部状态与输入输出描述、不可区分状态及隐藏方向。1963是发表年，1962收稿/报告与2006线上日期不是发表年的替代。本文具体的“初态与未来离散读数”定义由Stanford讲义核实，不把原文更一般的历史表述未经条件核对直接套过来。

完整41页原件中的相关Fig.2以及邻近Fig.1、3、4已用于私下核查上下文；出版物受SIAM版权约束，公开教师副本不等于开放图片许可。本文只链接，不复印原图或用换色版冒充原创。

### Karl J. Åström、Richard M. Murray：教材入口

[FBSwiki：Output Feedback](https://fbswiki.org/wiki/index.php/Output_Feedback)；[Feedback Systems第二版入口](https://fbswiki.org/wiki/index.php/Feedback_Systems:_An_Introduction_for_Scientists_and_Engineers)。第二版对应第8章，第一版是第7章。

章节摘要用于确认状态估计/输出反馈的题材入口。完整章节PDF本次未成功取得，不能声称核读全章；已核章节首面，但教材版权与wiki页脚许可不能混同，所以不复制该首图。章节摘要存在把“不可达”混入可观测性段落的措辞笔误，本稿没有据此认定不可控等于不可观测。正式离散判据采用已完整核读的Stanford讲义。

## 本篇图像与实际计算

13张原创解释图加1张真实人物照片。封面单独制作，不重复计为正文图。代码、数据、尺寸及重绘方法见[README](README.md)、[figure-metadata.json](examples/figure-metadata.json)。

- 01：固定左/右位置的两组分配与相同总量；透视画法只供读者解释。
- 02：一轮排水、净交换、最终剩余，所有数字按轮初值计算。
- 03：本次实际精确模型计算的左右内部轨迹，折线连接离散记录。
- 04：同一批数据的总量曲线完全重合，另列前三次记录，不人为偏移。
- 05：箱间交换在总量账里相消，说明无限继续读取为何也无用。
- 06：初始状态平面，不是空间地图；同总量的分配构成一条线。
- 07：另一明确标记的已知输入实验，实际输出10、8.4、7.12升。
- 08：新实验只测左箱、不沿用旧总量；右箱不透明，避免把未知答案画出来。
- 09：从收支式到求出右箱初值，明确0.2是代数剩余项，不是额外反向水流。
- 10：同一初始状态平面上，重复约束与唯一交点比较。
- 11：系数表先走通8、2的乘加，再解释两次读数是否提供独立方向。
- 12：新候选P=(8,2)、Q=(8,3)，改变交换比例后的输出差与指定误差范围；两幅尺度不同。
- 13：固定一对误差的精确传播，区分真量、读数、估计；未运行滤波器或统计实验。
- 14：2007年Kalman真实肖像。来源与CC BY-SA 4.0许可见[NOTICE](third-party/NOTICE.md)。

数据由[保存的程序](examples/run_model.py)实际运行，非语言模型预测。图使用Pillow与代码定义的几何/曲线绘制，不使用生成式图像伪造设备或历史照片。

没有合适、许可明确且对应本模型的真实双水箱设备照片。核查到的Quanser Coupled Tanks官方资料是不同的真实装置，版权All rights reserved，访问受限后未继续获取；不冒称本文用了该设备，不用无关水罐照片凑图。本文的实体职责由明确标识的原创模型示意承担，实证职责由可复算的真实代码输出承担。

## 权利与AI辅助

原创正文、原创解释图及原创教学数据：CC BY 4.0。原创计算与制图代码：[MIT](LICENSE-CODE.txt)。Kalman肖像保持独立的CC BY-SA 4.0及机构署名，未裁剪改色，不被正文许可重新授权。其他论文、讲义、教材只提供出处链接，其原有版权保留。

AI参与资料查找、模型讨论、初稿、代码与解释图制作和审读辅助。没有声称作者亲历历史事件、见过Kalman、搭建真实水槽，或测量任何真实设备。参数已知的无噪声可观测性、固定误差反演与实际工程性能分开表述。
