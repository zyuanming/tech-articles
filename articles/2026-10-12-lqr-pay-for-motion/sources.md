# 一手来源、照片权利与实验范围

本文是原创中文讲解，AI辅助用于检索、组织、确定性示意绘制和代码实现。历史与公式依据下列一手材料；数值来自实际运行。没有虚构对白、亲历或真实设备测试。原创正文、教学图和示例代码采用CC BY 4.0；ETH照片单独采用其实际CC BY-SA 4.0许可，不被整稿许可覆盖。

## 1. Kalman原论文与历史取舍

R. E. Kalman，**Contributions to the Theory of Optimal Control**，*Boletín de la Sociedad Matemática Mexicana*5，1960，pp102–119。[原论文重印扫描，Illinois课程托管](https://liberzon.csl.illinois.edu/teaching/kalman_paper.pdf)。实际重印首页为149页，引用原始页码102–119；本文不采用部分目录误写的102–109。

- 原首页：目标是线性控制系统的二次积分优化，并非声称此前无人研究控制或优化。
- 重印158–160页，第6节：线性二次调节问题、最小代价二次型、Riccati方程、最优反馈，以及不能无条件假定最优系统必稳定的提醒。已查看这些原生页面，不以有OCR错误的扫描提取文字替代公式核查。
- 此原文以连续时间理论为主；本文两步离散标量例是独立设计与推导，不声称复现其全部定理或原实验。
- 没有复制扫描页、原文图表或整份PDF到公开文章包。原页未给本稿开放再发布授权，可在原链接查阅。

R. E. Kalman，*This Week’s Citation Classic*，文字署于1978-06-22，刊于1979-08-06。[作者本人一页回顾](https://garfield.library.upenn.edu/classics1979/A1979HE37100001.pdf)。已实际看完整原页。正文仅采用其把状态描述、结构概念、二次优化与稳定性组合在一起的回顾，不把个人生活细节改编为戏剧场景，也不把回顾发表年份误当原论文年份。

## 2. 固定课程版本的形式化核验

Stephen Boyd，Stanford EE363，**Winter2008–09**，[归档课程目录](https://ee363.stanford.edu/archive/lectures.html)。

- [Lecture1: Linear quadratic regulator: Discrete-time finite horizon](https://ee363.stanford.edu/archive/lectures/dlqr.pdf)，32页。主要核读1–7、11–17、20–23、28页的成本定义、有限时域、价值函数、动态规划、Riccati与反馈结构；第21–23页另外看原生渲染以免文本提取损伤矩阵符号。
- 课件把负号包含在Kt里；本文定义正的主例gain，把负号另写为u=−gain×x。不能不看约定就直接对比增益符号。
- [Lecture3: Infinite horizon linear quadratic regulator](https://ee363.stanford.edu/archive/lectures/dlqr-ss.pdf)，11页。核对有限/无限时域区别与闭环条件，本文不直接复制有限时域结论为一般无限时域稳定保证。
- 本文从x_next=x+u、x0=4出发的两步手算、扰动与权重实验独立设计，不沿用课件的两状态20步数值实验。q=0、a=2的不稳定反例与Lecture3第11页同型，本文将其运行展开为五步，正文已给出处。黄金比例固定点是本文这组标量参数的代数结果，不是一般LQR常数。

课件是可读的一手教学材料，但本次未见适用于图表的开放再发表许可，因此只保留原文链接。与本文有关的原视觉位于Lecture1的第8/10页（取舍图）、18/19页（路径说明）、25–27页（两状态实验轨迹与增益），均未复制、未换色冒充原创。本稿用自己的模型和布局解释对应概念；其他页的文字或公式不被制作成密集截图。

## 3. 真实人物照片

`assets/05-kalman-eth-original.jpg`：**ETH-BIB-Kalman, Rudolf E. (1930–2016)-HK_04-01925**。

- [机构照片的Commons文件页](https://commons.wikimedia.org/wiki/File:ETH-BIB-Kalman,_Rudolf_E._%281930-2016%29-HK_04-01925.jpg)
- [机构DOI来源](https://doi.org/10.3932/ethz-a-000672660)
- 署名：ETH-Bibliothek Zürich，Bildarchiv / Fotograf: Unbekannt / HK_04-01925。
- 档案日期2007-12-27。正文明确不将它当成1960年的现场。
- 许可[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)，[完整法律文本URI](https://creativecommons.org/licenses/by-sa/4.0/legalcode.en)。照片未修改；原始JPEG为3168×2112、1053924字节，SHA-1为6780f427b832b96c66f0f1232b2e3adf1a9d1755。文件中的机构IPTC保留。
- 本稿复用此前已合法取得、署名与许可已核的同一原字节。具体通知见[third-party/NOTICE.md](third-party/NOTICE.md)。需要改编该照片时须遵守同许可适用条件；本文原创许可不更改这项要求。无担保、不暗示ETH、摄影者或被摄者背书。

## 4. 原创视觉职责

共26项正文视觉：24张原创PNG、一张原机构照片、一个原创13帧GIF。没有生成假历史照片或用QA缩略代理交付。

01–04：一步三选择、状态与指令单位、两类账单、成本最低点。

05–07：真实人物；可达/最优/稳定区分；两步成本发生的时间位置。

08–11：最后一步配方、最小剩余成本表、退回第一步、完整数值核账。

12–15：软终点与硬条件、按当前状态生成指令、中途扰动、反馈依赖的信息。

16–19：标量Riccati递推、倒算/正走的方向、三个权重的实际轨迹、拆开两项未加权成本比较。

20–23：软惩罚不能限幅、裁切后轨迹、最优不自动稳定反例、特定参数下的黄金比例固定点。

24–26：正文代码实际输出、独立数值核验范围、12步三权重的13帧实际状态。动画只显示离散时刻，不插值成未经定义的动力学。

每图承担一个可见步骤或边界；原图及最终全部实际动画帧、封面和手机比例代理需进入独立审读。静态手机代理不冒称公众号或浏览器验收。

## 5. 代码与数字的实际范围

[lqr_lab.py](examples/lqr_lab.py)、[实验说明](examples/README.md)。标准库Fraction精确有理数，实际Python3.12.14。

1620组递推/批量消元对照、3000组配方余量恒等式、961组两步动作网格、5组权重同比缩放，以及扰动、软/硬区别、有限最优而不稳定反例均实际通过。正文短Python也单独执行；没有把模型分数说成真实能耗。

所示例子不含多状态矩阵求解、受约束优化器、估计器或真实执行器。有限测试不能替代一般定理。数字和边界对应本稿明确的模型，不能不经工程设计直接用于真实设备。
