# 来源、图像身份与复算范围

本文为原创中文教学文章。AI参与资料检索、文字与代码草拟、制图和校读；历史版画未用生成式模型伪造，所有标为实际网格渲染的图均来自附带原创数据和真实Blender运行。作者没有制作实体盒子或实体欧拉器物，不声称硬件亲测。

## 一手资料与支撑边界

1. [Euler Archive / University of the Pacific：E230《Elementa doctrinae solidorum》馆藏记录](https://scholarlycommons.pacific.edu/euler-works/230/)。实际读取目录，支持作者、题名、Written Date 1750、Published Date 1758、原刊卷4页109—140。正文仅据馆藏陈述这些历史元数据。目录英文Content Summary把顶点加面与边数的关系写反，本文以立方体直接验证后不采用该句。全文下载当次正常访问返回403，未绕过限制，也没有把原作正文表述成已核。
2. [Stanford CS164：Topology II, Complexes and Homology，2010-05-17讲义](https://graphics.stanford.edu/courses/cs164-10-spring/Protected/10cs164-05-17.pdf)。公开读取并取得84页原PDF，实际核对PDF第52页的示性数定义与不变性、第53—57页的连通和、把手及边界公式，另参考第20—29页link概念、第31页定向。第56页公式已实际看原页。本文使用连通、紧致、可定向等前提；没有把课件末尾简写成的分类概括无条件推广到有边界对象。讲义仅用于事实与概念核验，没有转载其图、截图或整段文本。
3. [Cornell Mathematics Explorers' Club：Euler Characteristic](https://pi.math.cornell.edu/~mec/Winter2009/Victor/part5.htm)。实际读取，交叉核对合法三角剖分、χ定义、分割不变性、球面与环面示性数。本文主体采用自主绘制的局部记账及平面图剪树路线，不复制该页球面面积证明或原图。
4. [Smithsonian Libraries and Archives：Portrait of Leonhard Euler，SIL-SIL14-E2-07](https://library.si.edu/image-gallery/73170)。实际取得记录HTML及其直接下载原图并看完整像素，核身份、底部刊印行和具体权利字段No Copyright - United States。记录中刻者生年一项有内部矛盾，不采用它。正文年份1789对应版画刊印，不对应Euler论文或人物出生。图像保持原字节，详见[图像来源清单](originals/portrait-manifest.json)与[权利说明](originals/RIGHTS.md)。

历史目录不能替代未核原文；图像记录不能替代内部结构证据。本文没有复用访问受限的论文或Blender文档，也没有绕过相关限制。Blender版本与导入后顶点、边、面数量依据本地实际运行输出，而不是未读到的网页说明。

## 本文实际生成的数据

- [mesh_lab.py](examples/mesh_lab.py)：Python标准库；16个原创索引网格，271项实际运行的计数与局部检查；随机种子20261013。
- [meshes.json](examples/meshes.json)：全部实际顶点位置和面连接；坐标无量纲。
- [results.json](examples/results.json)：V/E/F/χ、连通分量、边界边、边界圈、非流形候选；三阶段矩形接缝独立计数。
- [render_in_blender.py](examples/render_in_blender.py)：Blender4.3.2、Cycles CPU、48采样、seed20261013，真实导入并交叉核对每个模型的原始点/边/多边形面计数。
- [blender-results.json](examples/blender-results.json)：版本、参数、16份实际网格导入计数及原始渲染路径。黑边为独立显示层，不纳入计数；光照、阴影与透视只是显示方式。
- [示例说明](examples/README.md)：准确命令、输出与边界。程序不是工业网格修复器，不验证所有几何自交、重复面或一般可定向性。正文给出的g/b解释依赖已声明表面条件。

## 许可

- 原创正文、原创教学图、原创网格和原创Blender渲染：CC BY 4.0。
- 原创示例代码：MIT，见[完整许可](examples/LICENSE)。
- 欧拉版画：采用馆藏具体No Copyright - United States标记，保留机构与源链接；不重新授权为CC BY或CC0。
- 引用的大学讲义、馆藏网页均只提供来源链接与有限事实说明，不把它们整体收入公开附件。

## 逐图职责与素材身份

封面为原创组合：同一组实际Blender方盒与方环渲染，配原创中文标题及计数；CC BY 4.0。正文共33个图像节点，其中32为原创图解、实际结果或二者组合，1为原样馆藏版画。面板、原始渲染副本、原件备份不另算正文图数。

- [assets/01-three-actual-meshes.png](assets/01-three-actual-meshes.png)：先看见三种实际生成并计数的网格，建立不同洞的悬念。原创，CC BY 4.0。
- [assets/02-point-edge-face.png](assets/02-point-edge-face.png)：同一方盒上逐项高亮三个计数对象。原创，CC BY 4.0。
- [assets/03-indexed-cube.png](assets/03-indexed-cube.png)：透明线框与ID帮助读者不漏背面顶点。原创，CC BY 4.0。
- [assets/04-edge-dedup.png](assets/04-edge-dedup.png)：从两个共边三角形解释按ID而非方向去重。原创，CC BY 4.0。
- [assets/05-cube-account.png](assets/05-cube-account.png)：将实际模型计数与V减E加F绑定。原创，CC BY 4.0。
- [assets/06-add-diagonal.png](assets/06-add-diagonal.png)：局部增边和增面的抵消。原创，CC BY 4.0。
- [assets/07-split-shared-edge.png](assets/07-split-shared-edge.png)：边插点的局部增量并强调相邻面共享新ID。原创，CC BY 4.0。
- [assets/08-face-fan.png](assets/08-face-fan.png)：避免把增加4个新面误算为净增加4面。原创，CC BY 4.0。
- [assets/09-subdivision-results.png](assets/09-subdivision-results.png)：实际Blender三档网格与原始计数揭示细分不改变特征。原创，CC BY 4.0。
- [assets/10-same-connections.png](assets/10-same-connections.png)：真实同连接网格变形，区分位置和拓扑。原创，CC BY 4.0。
- [assets/11-coincident-unjoined.png](assets/11-coincident-unjoined.png)：真实未焊接网格的爆炸视图，不用视觉接触代替ID连接。原创，CC BY 4.0。
- [assets/12-open-box-boundary.png](assets/12-open-box-boundary.png)：实渲染和边界诊断并用解释删面不删仍被使用的边点。原创，CC BY 4.0。
- [assets/13-shell-not-volume.png](assets/13-shell-not-volume.png)：剖面示意澄清有限厚度实物与抽象二维壳的差别。原创，CC BY 4.0。
- [assets/14-planar-cube.png](assets/14-planar-cube.png)：一张无交叉方盒平面图，明确外部区域就是第六面。原创，CC BY 4.0。
- [assets/15-delete-cycle-edge.png](assets/15-delete-cycle-edge.png)：展示删非桥边不拆散图且E和区域数同减。原创，CC BY 4.0。
- [assets/16-prune-tree.png](assets/16-prune-tree.png)：让树V减E等于1不依赖读者预先知道图论。原创，CC BY 4.0。
- [assets/17-square-tunnel.png](assets/17-square-tunnel.png)：实际贯穿方环与16片面的分组计数。原创，CC BY 4.0。
- [assets/18-torus-grid.png](assets/18-torus-grid.png)：低多边形实际环面对象与周期网格计数。原创，CC BY 4.0。
- [assets/19-identify-grid-seams.png](assets/19-identify-grid-seams.png)：矩形到圆筒到环面的接缝方向及三套真实组合计数。原创，CC BY 4.0。
- [assets/20-corners-identified.png](assets/20-corners-identified.png)：接缝局部明确点的识别而不只说把面弯曲。原创，CC BY 4.0。
- [assets/21-opening-versus-handle.png](assets/21-opening-versus-handle.png)：并排比较最容易混淆的两种洞，边界身份直接标明。原创，CC BY 4.0。
- [assets/22-two-handles.png](assets/22-two-handles.png)：真实两洞网格及程序计数，不依赖看不清的抽象双环线条。原创，CC BY 4.0。
- [assets/23-formula-conditions.png](assets/23-formula-conditions.png)：用对象和侧向解释连通、流形与定向的必要条件。原创，CC BY 4.0。
- [assets/24-boundary-components.png](assets/24-boundary-components.png)：用开口圆筒显示两条边界圈，每圈可含许多边。原创，CC BY 4.0。
- [assets/25-disconnected-components.png](assets/25-disconnected-components.png)：实际两个连通分量使单个球面2的范围清楚。原创，CC BY 4.0。
- [assets/26-three-face-edge.png](assets/26-three-face-edge.png)：实际三片共边网格和局部截面解释非流形。原创，CC BY 4.0。
- [assets/27-pinched-vertex-link.png](assets/27-pinched-vertex-link.png)：捏点实际反例说明仅检查边邻面不足，附邻接圈解释。原创，CC BY 4.0。
- [assets/28-same-chi-different-boundary.png](assets/28-same-chi-different-boundary.png)：同χ而不同边界的具体反例限制万能指纹误解。原创，CC BY 4.0。
- [assets/29-euler-1789-smithsonian.jpg](assets/29-euler-1789-smithsonian.jpg)：真实1789年欧拉版画保留色卡与原始刊印行，为人物史料锚点；正文另给中文解释。馆藏原图，第三方权利如上。
- [assets/30-history-timeline.png](assets/30-history-timeline.png)：三个可核日期分开，避免论文和画像混淆。原创，CC BY 4.0。
- [assets/31-edge-set-result.png](assets/31-edge-set-result.png)：实际计数算法的最小输入输出，以几何而非代码截图解释。原创，CC BY 4.0。
- [assets/32-model-check-workflow.png](assets/32-model-check-workflow.png)：真实网格小图串联工程检查顺序，限定计数器的能力。原创，CC BY 4.0。
- [assets/33-triangulated-cube-check.png](assets/33-triangulated-cube-check.png)：实际三角化盒子提供读者可独立复算的收尾。原创，CC BY 4.0。

所有正式教学图关键标签按720像素原图、约354像素正文宽度设计；历史版画的小字保留原貌，正文另给中文识别和时间说明。静态文章不依赖动画或互动。
