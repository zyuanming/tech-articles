# 来源与素材记录

核对日期：2026-10-11。原创中文正文由 zyuanming 发布，采用CC BY 4.0；第三方图保留自身许可，不纳入正文授权。

## 事实与实现边界

- scikit-image 0.21官方Contour finding示例：https://scikit-image.org/docs/0.21.x/auto_examples/edges/plot_contours.html 。主要配图目标页；正文唯一信息图完整保留，导航logo与运行按钮不收入文章。示例输入是公式生成的合成场，不是实物照片。
- 同版本find_contours API：https://scikit-image.org/docs/0.21.x/api/skimage.measure.html#skimage.measure.find_contours 。核对线性边插值、对角歧义的高/低充分连通选项、边界和缺失值导致开放轮廓，以及数组坐标。文章只点明0.21的接口，不宣称以后版本相同。
- William E. Lorensen、Harvey E. Cline，Marching Cubes: A High Resolution 3D Surface Construction Algorithm，Computer Graphics 21(4)，1987年7月。原论文：https://www.cs.toronto.edu/~jacobson/seminar/lorenson-and-cline-1987.pdf 。核对三维采样到三角片表面、作者与时间。未把二维方格算法全部归为该论文首次发明。
- Gregory M. Nielson、Bernd Hamann，The Asymptotic Decider: Resolving the Ambiguity in Marching Cubes，IEEE Visualization 1991，pp.83–91。作者目录：https://web.cs.ucdavis.edu/~hamann/pubs91.shtml ；论文：https://people.eecs.berkeley.edu/~jrs/meshpapers/NielsonHamann.pdf 。实际核对扫描第83–85页的歧义面、双线性模型、渐近线交点与连接规则。本文Q表达式按自己的A/B/C/D角顺序展开，不照搬另一套下标。

原论文包含其自身示意与三维结果图，本篇没有开放再分发许可依据，未复制论文图；历史引用仅用于核对原理与时间。本篇是二维机制原创讲解，不是对这些三维论文的逐图翻译或完整再现。

## 原文件与许可

assets/skimage-contours.png：来自 https://scikit-image.org/docs/0.21.x/_images/sphx_glr_plot_contours_001.png ，原文件43347字节，未缩放、未裁切、未重绘；尺寸以文件为准。署名scikit-image team，页面版权2013–2023；项目文件授权为BSD-3-Clause（2009–2022 the scikit-image team）。[官方许可页](https://scikit-image.org/docs/0.21.x/license.html)，[完整许可证副本](originals/SCIKIT-IMAGE-LICENSE.txt)。不得将作者或项目名称用于背书。

## 自设算例与原创图

assets/01-island-question.png至18-changing-level.png共18幅，1200×840，均由examples/generate_figures.py生成（NumPy、Matplotlib，中文Noto Sans CJK）。01是样本色块而非连续地形重建；02–10贯穿九点小岛；11–13为分类与连接机制；14–15对明确双线性公式画零等值线；16、17分别是数据边界和升维概念；18按同一九点表计算三个阈值的折线，不填补窗口外数据。

正文标准库代码实际执行，四线段端点与图一致。a=8,b=-3,c=1,d=-3时，Q=-1，中心0.75，鞍点(11/15,11/15)及其值-1/15均可直接代入复核。主例避开阈值恰等样本；短代码不处理通用歧义、整边等值、缺失值与拼线，已在正文明确。

原创正文CC BY 4.0声明不自动扩展到原创图片或代码。本文使用AI辅助调研与写作；代码生成的教学示意与第三方原始示例图已区分。
