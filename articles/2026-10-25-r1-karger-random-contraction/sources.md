# 来源、核算与素材权利

核验日期：2026-10-25。本文是新写的中文教学文章；没有复制论文原图、旧篇正文或第三方照片。

## 一手来源及实际查阅范围

1. David R. Karger、Clifford Stein，作者公开稿 [A New Approach to the Minimum Cut Problem](https://people.csail.mit.edu/karger/Papers/contract.pdf)。所提供PDF首页标1996-08-06，共37页。实际查阅第2节、引理2.1、定理2.2及证明、第2.1节，另核对第3节实现与第4节重复/递归收缩的区别。支持无向多重图收缩、保留平行边而删除自环、割值对应、固定最小割存活概率下界与重复思想。没有声称全文逐页精读；本篇复杂度是对随文Python代码自行分析，不套论文更快实现。
2. MIT OpenCourseWare [Minimum Cuts / Lecture 11](https://ocw.mit.edu/courses/6-854j-advanced-algorithms-fall-2008/7619ba2a27478cf420558710fe826d1f_mincut.pdf)。实际核对讲义开头的割、无权计数与指定s–t割定义。讲义内页标1996-10-22，Lecturer Michel X. Goemans、Scribe Roberto De Prisco；OCW外封为Fall 2008，不把课程发布页年份写成讲义创作年份。其主体是Stoer–Wagner算法，本篇不把它冒称Karger授课稿，也不借其当年性能描述作今日最快算法结论。

作者论文目录URL `https://people.csail.mit.edu/karger/Papers/` 本次工具返回不可访问，未重试绕过，也未使用目录内容；论文PDF本身可直接公开读取。随后尝试将这两份PDF下载为本地原文件时，执行环境网络隧道返回403，已停止该下载动作，没有绕过。浏览工具先前可读取的PDF文本与图注仍可用于定位；页面截图请求只返回引用，未得到可检查像素，因此不声称完成了原PDF逐页视觉检查。没有访问受限素材进入本篇。搜索结果中的百科、论坛和二手教程仅用于定位，不作为事实依据。

## 本篇计算证据

K₄边表、七个割的穷举、固定割1/5与任意最小割4/5的精确概率、抽样8034/1966及重复失败数值均由本篇 examples/run_examples.py 实际产生，记录于 [results.json](examples/results.json)。精确分布使用Fraction；771张连通简单图的每个最小割下界均作精确检查，另测多重边、自环和拒绝输入。理论模型和实验范围在正文交代，实验不是网络实测。

## 逐图来源、作用与许可

下列图片均由本篇 examples/build_figures.py 新生成，作者署名 zyuanming，CC BY 4.0。它们是教学示意或程序结果可视化，不是历史原件、实物照片或软件界面截图。数值读取results.json；画布检查API改编自本库r1 Quickselect篇的CC0生成器，图论结构与构图是本篇新作。

| 文件 | 新增理解作用 | 身份和权利 |
|---|---|---|
| assets/00-cover.png | 从原图到两个超节点的跨边保留；独立封面 | 原创教学示意，CC BY 4.0 |
| assets/01-cuts.png | 同一K₄两种分组的跨边与组内边对照 | 原创教学示意，CC BY 4.0 |
| assets/02-contract.png | AB收缩后双边、自环与端点映射 | 原创教学示意，CC BY 4.0 |
| assets/03-sampling.png | 五个边副本与五张等概率签的一一对应 | 原创教学示意，CC BY 4.0 |
| assets/04-branches.png | 成功与失败完整结局及原图跨边核验 | 原创教学示意，CC BY 4.0 |
| assets/05-survival.png | 固定目标割安全边、危险边和度数双计数 | 原创教学示意，CC BY 4.0 |
| assets/06-probability.png | 条件存活概率树，区分固定割、任意最优与下界 | 原创教学示意，CC BY 4.0 |
| assets/07-experiment.png | 实际单轮计数同轴对比，另列重复失败理论值 | 原创程序结果可视化，CC BY 4.0 |
| assets/08-all-paths.png | 实际精确枚举三十条路径，逐格展示六个失败分支 | 原创程序结果可视化，CC BY 4.0 |
| assets/09-edge-list.png | 六条整数端点边的逐项更新、重复项保留、自环剔除 | 原创教学示意，CC BY 4.0 |

正文与图的许可：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。配套Python源码与JSON记录另采用[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/)。引用论文及讲义的权利归原作者/机构，本篇只链接与中文释义，不把文献纳入本篇开放授权。


## 原文图表的相关范围与采用决定

作者PDF的可检索文本列出Figure 1–8；没有检索到Figure 9或另标Table的项目。这里是已定位图注/算法框的清点，不等于原PDF所有页面的像素核查。

| 原文对象（PDF页序从1起） | 与本文关系及处理 |
|---|---|
| Figure 1，页3，历史算法复杂度表 | 不采用。比较的是论文当年的算法结果，不是本篇教学实现，也不是今日性能排名。 |
| Figure 2，页8，contraction | 核心相关。未取得原图再分发许可，不复制原图；本篇02、03、04、05、09用独立K₄例子展开端点、平行边、自环与存活割。 |
| Figure 3，页8，基本Contract算法框 | 核心相关。不复制版面；本篇用新写代码、逐步收缩及全部路径矩阵解释同一算法规则。 |
| Figure 4，页10，加权Contract算法框 | 未实现的推广；仅链接和说明按权重抽样边界，不放原框以免读者混用输入模型。 |
| Figure 5，页12，矩阵收缩更新算法框 | 与实现区别相关。原稿是矩阵更新，本篇是边列表；09图逐项展示本篇真实表示，避免暗示实现了原稿数据结构。 |
| Figure 6，页13，Recursive Contraction算法框 | Karger–Stein递归版本，超出本篇基本独立重复范围；明确排除，不借其复杂度。 |
| Figure 7，页19，Compact算法框 | 分批收缩/排列的进阶实现，本文未实现；排除。 |
| Figure 8，页23，Iterated-Sampling算法框 | 进阶抽样实现，本文未实现；排除。 |
| MIT讲义Figure 1，页5，mincut algorithm illustration | 来自Stoer–Wagner主体，并非本文的均匀随机收缩；排除。其讲义算法框也属于该不同算法。 |

作者PDF公开可读不等于授予图像再许可，本次未找到适用的开放图像授权，因此仅链接。MIT OCW [使用条款](https://ocw.mit.edu/pages/privacy-and-terms-of-use/)列CC BY-NC-SA 4.0，不能当作本篇CC BY 4.0素材使用；该图同时也不属于本文算法范围。没有拿第三方原图的排版或形状做换字复制。本篇实际结果是自行执行代码产生的JSON与可视化，不是论文实验的转绘。

## AI辅助

本篇由AI助手辅助选定贯穿例、检索一手来源、撰写解释、编写Python核算与绘图程序，并在执行环境实际运行检查和查看生成图片。图片是程序按图结构绘制，没有使用生成式图像模型，也未制作伪历史图片。数值、来源访问范围和许可按实际结果保留；作者自检不等于外部独立审读。
