# 出处、事实范围与素材权利

核对日期：2026-10-12。本文是一篇独立编写的学习教程。原理说明、12个三角形的坐标、手算、实验数据与全部28张正文配图均为本篇制作；没有把论文的原图改色后称为原创。

## 一手与作者资料

### 1. Rubin 与 Whitted，1980

Steven M. Rubin and Turner Whitted, “A 3-Dimensional Representation for Fast Rendering of Complex Scenes,” Computer Graphics 14(3), pp.110–116, 1980. DOI: 10.1145/965105.807479。

- [作者 Steven M. Rubin 上传的论文全文与图记录](https://www.researchgate.net/publication/215506194_A_3-dimensional_representation_for_fast_rendering_of_complex_scenes)
- 支持范围：作者、年份、题名；层次包围体表示、可旋转平行六面体、终端表示不同于本篇三角形叶子；原文的层次编辑器与构建/显示成本讨论
- 原文 Introduction 已讨论 Clark、MAGI 与 Reddy/Rubin 等相关前史，所以本文不作“1980年首次发明一切BVH”的断言
- 论文和原图仍有版权。原文第一页区分非商业复制与重新发表，本文没有收录其图或整份PDF，也没有把它们置于CC BY 4.0之下
- 人物不使用AI生成的历史肖像；本文时间线只是原创文字与几何排版

### 2. Wald、Boulos、Shirley，2007

Ingo Wald, Solomon Boulos, Peter Shirley, “Ray Tracing Deformable Scenes Using Dynamic Bounding Volume Hierarchies,” ACM Transactions on Graphics 26(1), 2007. DOI: 10.1145/1189762.1206075。

- [作者机构记录，含原论文与演示入口](https://www.sci.utah.edu/~wald/Publications/2007/#BVH)
- 支持范围：可变形场景中的动态BVH，保持树拓扑并更新包围盒，论文还结合成组射线遍历等技术
- 本篇refit置换实验为另行设计的12对象模型，不复现论文模型、时序或性能数值
- 作者页的真实渲染样例可从原入口查看；未核实公开再分发许可，不转载其图片、影片
- 本次取得作者目录页并核对论文记录；不声称已取得或逐页阅读该论文PDF的本地原件

### 3. Wald，2007，快速构建

Ingo Wald, “On Fast Construction of SAH-based Bounding Volume Hierarchies,” IEEE Symposium on Interactive Ray Tracing, 2007. DOI: 10.1109/RT.2007.4342588。

- [作者提供的原论文](https://www.sci.utah.edu/~wald/Publications/2007///FastBuild/download//fastbuild.pdf)
- 支持范围：SAH构建与快速候选划分思路；正文的10×10×1表面积例子是另设的心算模型
- 不复制论文图表，不移用论文性能数据

### 4. Karras，2012

Tero Karras, “Maximizing Parallelism in the Construction of BVHs, Octrees, and k-d Trees,” High Performance Graphics 2012。

- [NVIDIA Research 论文记录](https://research.nvidia.com/publication/2012-06_maximizing-parallelism-construction-bvhs-octrees-and-k-d-trees)
- [原论文PDF](https://research.nvidia.com/sites/default/files/pubs/2012-06_Maximizing-Parallelism-in/karras2012hpg_paper.pdf)
- [作者的机构介绍](https://research.nvidia.com/person/tero-karras)
- 支持范围：逐层建树在树顶的并行性局限；通过二进制基数树构建BVH的路线；Morton排序、重复键与并行构建讨论
- 本文未实现该论文算法，也不引述其GPU性能数字。图28的4×4 Morton编号由本篇独立计算
- 原论文为Eurographics版权作品，记录页给予特定个人/课堂复制条件，不等于开放再发表许可；本篇不转载原图。机构肖像未找到可供本篇再分发的明确开放许可，未使用

### 5. PBRT 第四版

Matt Pharr, Wenzel Jakob, Greg Humphreys, Physically Based Rendering: From Theory to Implementation, 4th edition, §7.3。

- [Bounding Volume Hierarchies](https://pbr-book.org/4ed/Primitives_and_Intersection_Acceleration/Bounding_Volume_Hierarchies)
- [进一步阅读](https://pbr-book.org/4ed/Primitives_and_Intersection_Acceleration/Further_Reading)
- 支持范围：基本BVH的对象划分与空间划分区别、叶子/父盒概念、SAH和进一步研究入口
- 本文不把程序仓库的代码许可扩展到图书图片。网页可读不代表获得再发表图片的许可，本文没有转载该书图片
- 本次直接获取该正文页返回403后即停止对应路径；没有换地址或绕过限制取得原件

### 6. Ray Tracing: The Next Week

Peter Shirley, Trevor David Black, Steve Hollasch, Ray Tracing: The Next Week, v4.0.2, 2025-04-25，Bounding Volume Hierarchies 一章。

- [书籍正文](https://raytracing.github.io/books/RayTracingTheNextWeek.html#boundingvolumehierarchies)
- [官方系列首页与CC0说明](https://raytracing.github.io/)
- [本地保存的官方完整CC0文本](assets/source/rt-COPYING.txt)
- 支持范围：从包围体直觉走到slab区间、盒合并和BVH的可学习实现；本文并未逐行移植其C++代码，闭区间、零方向与重复测试计数由本篇明确约定
- 该书的BVH节包含4张相关正文信息图：fig-2.01-bvol-hierarchy.jpg、fig-2.02-2d-aabb.jpg、fig-2.03-ray-slab.jpg、fig-2.04-ray-slab-interval.jpg
- 官方首页明确将书籍按CC0提供，不只是给代码授权。该章4幅原图已全部收录于[官方原图附册](source-figures.md)，保留官方原URL的JPEG字节与原尺寸，未裁剪、压缩或改色；与正文28幅原创图明确区分

## 本篇配图逐项说明

以下28个文件均为本篇原创，许可CC BY 4.0，建议署名“zyuanming，本文教学图”。没有第三方照片、商标或嵌入式第三方图像。图1的内部图像是实验程序的实际输出，外层标题为本篇制作；其余为几何示意、计算账目或数据可视化。

1. assets/01-actual-render.png：12对象CPU射线渲染；无光线多次反弹
2. assets/02-twelve-triangles.png：固定主场景的x-y投影与编号
3. assets/03-safe-rejection.png：包含关系保证整组拒绝
4. assets/04-box-is-not-hit.png：G的y-z投影，展示盒相交不蕴含三角形相交
5. assets/05-minmax-box.png：G的坐标与AABB
6. assets/06-tree-map.png：主树分组与局部展开
7. assets/07-object-space.png：对象划分/空间划分概念对照，非历史游戏截图
8. assets/08-ray-parameter.png：参数射线位置变化示意
9. assets/09-slabs-space.png：slab交叠结构示意，非等比例坐标图
10. assets/10-interval-overlap.png：主例变体射线的区间交集
11. assets/11-parallel-zero.png：零方向分量分支
12. assets/12-interval-boundaries.png：反向、盒内起点、角接触边界
13. assets/13-traversal-ledger.png：普通遍历实际计数
14. assets/14-nearest-pruning.png：最近命中剪枝
15. assets/15-any-versus-closest.png：两种查询的不同停止条件
16. assets/16-median-builder.png：主树的y优先中位数分组
17. assets/17-overlapping-bad-case.png：完全重叠盒的落空坏例
18. assets/18-surface-area.png：独立SAH心算模型的长方体表面积
19. assets/19-sah-ledger.png：独立SAH心算模型的估计成本
20. assets/20-leaf-size.png：主射线叶容量实验实际计数
21. assets/21-scaling-counts.png：规则网格规模实验实际计数
22. assets/22-refit-overlap.png：固定置换前后两组对象的范围
23. assets/23-refit-counts.png：refit/重建查询实际计数
24. assets/24-total-cost.png：明确虚构成本单位的代数比较，不是计时
25. assets/25-dont-shrink-box.png：内缩边界漏交风险夸张示意
26. assets/26-history.png：依据一手资料排版的原创历史节点图
27. assets/27-morton-order.png：独立计算的二维位交错次序
28. assets/28-checks-and-limits.png：实际运行验证的范围和限制

正文图号按阅读顺序排列，所以文件28在正文是图26，文件26、27分别在正文是图27、28。所有正文图为静态PNG，无GIF动画。

## 实验与代码事实边界

- [完整程序](examples/bvh_lab.py)和[说明](examples/README.md)，仅依赖Python标准库，MIT许可
- 坐标是人为设计的无量纲模型单位。程序实际执行了求交、遍历、重建/refit、独立算法核对；没有伪造本机耗时、GPU测试、厂商性能或平台发布结果
- 同一个主几何例子贯穿包围盒、区间手算、树、最近命中与移动置换。独立SAH长方体与抽象成本例子在正文均明确切换场景
- 三角形测试是双面行列式测试，阈值1e-12；普通浮点演示，不是watertight内核或任意尺度鲁棒性证明
- 不实现空间切分BVH、SAH构建、并行Morton构建或硬件光追；对应图与段落只解释思路和进一步阅读

## AI辅助说明

本篇使用AI协助资料检索、中文讲解、原创教学程序、几何图生成与自检。历史段落依据上列一手论文和作者记录；实验数字来自实际运行。AI输出不作为历史证据。正文28幅原创图由确定性绘图/实验代码生成；原图附册另保留4幅官方CC0图的原字节，没有生成假历史照片。

原创正文与原创图采用CC BY 4.0；代码采用MIT；官方CC0图片与许可文本按其原身份保留。其他第三方资料及其原图不随本篇获得重新授权。
