# 资料、实验与图片来源

核查日期：2026-10-14。本文的三个整数点、网格、凸包差异、区间过滤器和解释图均为原创教学构造或本次实际程序结果，不是复制原论文的数据。

## 一手来源

1. Jonathan Richard Shewchuk：[Fast Robust Predicates for Computational Geometry](https://www.cs.cmu.edu/~quake/robust.html)。作者页面说明方向/incircle符号接近0时的舍入风险、自适应工作量、精确算术与应用失败的关系；列出1996会议论文、1997期刊长文与原代码。页面明确区分public-domain谓词代码与另有权利的Triangle程序。本篇没有转载网页图、论文图或Triangle程序。
2. Shewchuk：[原始predicates.c](https://www.cs.cmu.edu/afs/cs/project/quake/public/code/predicates.c)，1996-05-18。实际读取原始文件，核orient2d的普通估计、误差界和orient2dadapt回退；文件头声明public domain。本文不复制、编译或运行此代码，没有宣称自行实现了其完整浮点展开算法。引用目的仅为原算法结构核查。
3. [作者的长文摘要与文献记录](https://www.cs.cmu.edu/afs/cs/project/quake/public/papers/robust-arithmetic.abstract)。说明算法对二进制、正确舍入算术的依赖，以及工作量随结果不确定程度调整。本文不把这些保证外推到任何硬件、任意溢出或fast-math设置。
4. [CGAL：Filtered_predicate](https://doc.cgal.org/latest/Kernel_23/classCGAL_1_1Filtered__predicate.html)，核查页面为CGAL 6.2.1。官方示例区分区间过滤与精确谓词，过滤无法确认时调用精确层。本文用原创Python区间+Fraction实例解释这一架构，没有使用或声称测试CGAL。
5. [CGAL：Exact_predicates_inexact_constructions_kernel](https://doc.cgal.org/latest/Kernel_23/classCGAL_1_1Exact__predicates__inexact__constructions__kernel.html)。支持精确几何谓词与一般不精确几何构造的职责区别。没有声称使用此内核就解决整个几何应用的所有错误。
6. [Python：math.nextafter](https://docs.python.org/3/library/math.html#math.nextafter)及[fractions](https://docs.python.org/3/library/fractions.html)。支持按方向寻找相邻浮点数、将float转换为完全相同的有理值。本文运行Python 3.12.14，只使用该版本已有的API，不依赖文档新版新增接口。

## 原创计算与视觉

代码[run_orientation.py](examples/run_orientation.py)生成完整结果；[build_figures.py](examples/build_figures.py)绘制14正文图和封面。公开输入、运行版本、计数及算术范围见[README](README.md)。

- 主例D=1用整数恒等式N²−(N−1)(N+1)独立推导；浮点D=0与循环顺序0/1/1由实际运行核对。
- 凸包图根据同一单调链实现的两组输出绘制。改变的只是方向谓词；显示坐标另作明确线性变换，未冒称原比例或游戏故障截图。
- 961点测试网格和500组固定种子样本保留所有结果。数值分类与有限区间包含关系逐项由Fraction精确参考核对。显示颜色不是置信概率。
- 原文没有被复制进图像目录。涉及Shewchuk的是算法结构，不是人物生平或设备外观主题；没有采用无许可人像、假历史照片或伪造框架界面。

## AI辅助和许可

AI助手协助研究、中文组织、编写原创程序和图像代码，并在本地实际执行、检查输入及结果。AI文字或图本身不是外部事实来源；文章里绘图工具的故事是教学设定，没有冒称作者亲历工程事故。

原创正文、原创图、封面、原创教学数据采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。原创代码采用[MIT](LICENSE-CODE.txt)。外部网页、论文与软件各自保留原权利，不因为被链接而获得本文的许可。Noto字体仅用于渲染，没有随文分发字体文件。
