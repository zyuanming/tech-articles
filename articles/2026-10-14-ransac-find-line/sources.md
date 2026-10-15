# 事实、素材与方法来源

核查日期：2026-10-14。本文自写的是非竖直直线回归的教学实现，使用竖直残差，不冒充历史论文代码或第三方库完整复现。

## 历史书目

- [SRI：Random Sample Consensus: A Paradigm for Model Fitting with Applications to Image Analysis and Automated Cartography](https://www.sri.com/publication/artificial-intelligence-pubs/random-sample-consensus-a-paradigm-for-model-fitting-with-applications-to-image-analysis-and-automated-cartography-2/)。M. A. Fischler、R. C. Bolles；1981；Communications of the ACM 24(6), 381–395。支持正文年份、作者、题名与发表信息。
- 既有原论文获取尝试遇到访问限制；本次没有换站追取，也没有声称读过完整原论文。本文技术步骤由下列官方文档/固定版本源码及独立数学计算核验，不把书目页当作完整算法细节来源。

## 官方技术依据与具体差异

- [scikit-learn 1.7：RANSACRegressor](https://scikit-learn.org/1.7/modules/generated/sklearn.linear_model.RANSACRegressor.html)，配合 [1.7.2源码](https://github.com/scikit-learn/scikit-learn/blob/1.7.2/sklearn/linear_model/_ransac.py)。支持预测y与观察y的绝对残差、阈值一致集、最佳一致集重拟合等回归框架。该库接受残差<=阈值。本文没有直接调用、复制或完全复现该库的估计/停止/同票策略。
- [scikit-image 0.25：ransac与LineModelND](https://scikit-image.org/docs/0.25.x/api/skimage.measure.html#skimage.measure.ransac)，配合 [v0.25.2 fit.py](https://github.com/scikit-image/scikit-image/blob/v0.25.2/skimage/measure/fit.py)。支持最小子集抽样、检查残差、优先最大支持集与最后重拟合的通用流程。LineModelND用正交最短距离，与本文竖直差不同。
- 固定版本 scikit-image 使用残差<阈值；同票时比较全体点的残差平方和；重拟合后保留此前最佳mask。本文用<=、支持集内部平方和破同票，并另算最终mask，因此不称“复现scikit-image”。两套mask在真图127→131的变化实际展示。
- [OpenCV 4.13：USAC](https://docs.opencv.org/4.13.0/de/d3e/tutorial_usac.html)。支持RANSAC类方法需要指定抽样、评分、模型、退化检查及优化组件。正文只介绍基础流程，不把现代USAC的全部策略归属为原始基础版本。

## 本文独立推导与运行

- 两个x不同的点决定y=ax+b；中心化OLS斜率为两种偏离的乘积和除以x偏离平方和，截距使直线通过均值位置。这些是本文重新代入数据计算的数学关系。
- 从有限N点无放回抽两个不同索引，m个已知生成内点时，单轮事件概率为m(m−1)/(N(N−1))。跨轮独立重抽时，K轮至少一次事件概率为1−(1−q)^K。正文8/12例的28/66及所需9轮已穷举核验。
- 常见内点比例的平方w²，在这里不是有限总体无放回抽样的精确值。本文没有把库动态估计的内点率当作已知真值，也没有把抽样事件概率写成模型正确概率。
- 12点原始数据、随机种子、全部轮次、手算候选、阈值对比、真内点对穷举、OLS输出与真照片的全部候选/两张mask保存在[本次结果](examples/expected-results.json)。代码与运行说明见[README](README.md)。
- 教学种子20261074是为方便逐步阅读选定的：第2轮为A、F；不代表随机性能抽样。照片参数在第一次运行前确定，此后保留首次127→131结果；没有手动挑除候选或加假点。

## 真实照片及派生图

[USGS《Bridges》](https://www.usgs.gov/media/images/bridges)，摄影信用Joel M. Galloway / USGS，机构Dakota Water Science Center。页面日期2011-06-23，不另推断精确拍摄时刻。页面说明为USGS人员在Civil Air Patrol飞行中拍摄的密苏里河四桥航拍；由远到近分别为Expressway Bridge、Liberty Memorial Bridge、Burlington Northern SantaFe Railway Bridge、Interstate 94 Grant Marsh Bridge。

单图来源页明确标注Public Domain。采用其公开Original原生文件，3240×4320、5,216,398字节，随文[完整保存](originals/usgs-bridges-DSCN0281.jpg)。不暗示USGS认可文章或算法。

- 图02：原照片完整画面缩放，加本文人工ROI框。不是程序检测结果。
- 图13：缩放后的真实局部裁切，添加扫描列线；下方为该列实际计算的亮度差。
- 图14：缩放后局部裁切，叠加全部159候选、对应分类颜色与拟合线。两面板使用同一照片，不能算作两份独立采集证据。
- 未对照片使用生成式补画、移除物体、改造边缘或构造假截图。数值提点与可视化属于明确标出的图像分析和叠加。

## 解释图与权利

除上述明确标出的真实照片背景，全部坐标图、计算图、概率图与封面由本文原创脚本生成，中文说明与[图像用途清单](examples/figure-metadata.json)配合正文。图01/07/08/09/12/14绘制实际结果；图03/04/05/06/10/11解释同一组可核对输入与规则；图13衔接真实输入与数值。未复制论文图、人物肖像或产品界面。

原创正文与原创解释图采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。USGS原照片保持其Public Domain身份与摄影信用，不因本文许可改变。原创代码采用随文[MIT许可](LICENSE-CODE.txt)。第三方文档只作为链接和依据，没有批量转载。

## AI辅助说明

本文使用AI辅助规划、起草、代码与科学图表制作、来源核查和审读。数值来自随文代码的实际运行；真实照片来自上面的可追溯USGS原件。没有把AI生成内容当作历史照片、原论文图、真实软件截图、仪器测量或作者亲历。公开文件只含正文、素材、复现代码与必要权利说明，不含私有审读过程或未完成的发布状态。
