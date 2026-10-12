# 出处、实验与图像权利

核对日期：2026-10-12。本文的原创正文、原创教学图为CC BY 4.0；第三方照片按其各自许可保留，不能因与本文一起发布而被重新许可。

## 一手资料及支撑范围

1. E. Catmull、J. Clark，Recursively generated B-spline surfaces on arbitrary topological meshes，Computer-Aided Design 10(6)，1978年11月，350–355。DOI：[10.1016/0010-4485(78)90110-0](https://doi.org/10.1016/0010-4485(78)90110-0)；[大学课程托管的原论文扫描](https://people.eecs.berkeley.edu/~sequin/CS284/PAPERS/CatmullClark_SDSurf.pdf)。已逐页视觉核对6页。350页：作者、机构、原始动机及没有给出特殊点连续性证明的限制；351–352页：三类规则、Q/R定义、连接方式；352–354页：特殊点、实例、反例及当时的限制；354–355页：另一种双二次方案，本文不把它混入Catmull–Clark主线。扫描首面标©1978 IPC Business Press，未发现开放图片再利用授权，所有图版只链接不复制。
2. Pixar OpenSubdiv v3_6_0，[Subdivision Surfaces官方文档源](https://github.com/PixarAnimationStudios/OpenSubdiv/blob/v3_6_0/documentation/subdivision_surfaces.rst)。固定Git树对象7d0ab5530feef693ac0a920585b5c663b80773b3。用于术语、规则区域/特殊点、控制笼与极限表面、细分与tessellation区别、边界模式、半锐折痕范围。该文档源自身有Modified Apache 2.0文件头；不能由此自动断言外链的每幅图也以该许可发布。本文只对事实进行独立解释，不复制其图版。
3. 同版本[catmarkScheme.h](https://github.com/PixarAnimationStudios/OpenSubdiv/blob/v3_6_0/opensubdiv/sdc/catmarkScheme.h)。assignSmoothMaskForVertex用于核对更新权重；assignCreaseMaskForVertex用于核对3/4、1/8、1/8；assignSmoothLimitMask用于核对全四边形内部顶点的极限权重。本文Python为从数学公式独立编写，没有复制C++源码；实验未运行OpenSubdiv。
4. 同版本[crease.h](https://github.com/PixarAnimationStudios/OpenSubdiv/blob/v3_6_0/opensubdiv/sdc/crease.h)，用于核查无限锐度与锐度传播是附加规则，不把半锐折痕偷换成“固定一排顶点”。
5. 同版本[Modeling Tips](https://github.com/PixarAnimationStudios/OpenSubdiv/blob/v3_6_0/documentation/mod_notes.rst)，用于支撑线圈、特殊点与形状控制的简短讨论。未引入文档中的旧GPU价数上限作为2026年硬件事实。
6. Tony DeRose、Michael Kass、Tien Truong，Subdivision surfaces in character animation，SIGGRAPH 1998，85–94。[ACM正式出版记录及摘要](https://doi.org/10.1145/280814.280826)。本文仅根据摘要说明作品应用与生产环境的关系，不声称完成全文核读，也不复用电影画面。官方PDF在网页阅读工具中因体积过大无法读取，未改换通道绕过该工具限制。
7. [Pixar《Geri’s Game》官方作品页](https://www.pixar.com/geris-game)，交叉核验作品确实存在且为1997年作品。正文未扩写无关剧情和奖项，官方剧照未取得开放复用依据。
8. 两位人物照片的Commons原文件页是图像署名与授权的直接发布记录，不拿百科人物介绍代替研究史一手证据。

## 具体数值与图像对应

- 所有主例来自同一控制笼：各轴取−1、+1的8顶点，6四边形，棱长2，无单位。完整顶点与面绕序见[初始网格](experiment/cube-level-0.json)。另外提供[第一轮精确分数网格](experiment/cube-level-1.json)、[第二轮精确分数网格](experiment/cube-level-2.json)。
- 算法、拓扑验证和独立数值测试：[catmull_clark.py](experiment/catmull_clark.py)。Python标准库即可运行；没有随机数，无seed适用项。精确断言用fractions.Fraction；完整0–5轮遍历用双精度浮点。
- [results.json](experiment/results.json)保留全部运行结果。对称例之外，另建4四边形不对称高度测试，中心新z=19/16；使用展开权重独立核算。其四位直接邻点、四位对角点和高度在代码及正文公开。
- 网格验证：每面顶点不重复；共享边方向相反；每边只接1或2面；每个顶点的面邻域连通；边界顶点恰有2边界边；检查全0–5轮闭合、Euler=2、V/E/F计数、价数和正有向体积；另检测开口和3类坏输入。Euler计数不是唯一正确性依据。
- 体积仅针对有限网格：每个四边形以固定第一顶点作扇形三角化，使用有向四面体体积求和。非共面四边形的三角化会影响有限多面体几何，正文明确限定，不声称这是极限曲面精确体积。
- 渲染采用本次原创CPU正交投影、三角形z-buffer、固定光照；前几轮叠加真实可见网格边。只有17-not-sphere.png额外使用顶点法线插值辅助观察；其几何仍为第5轮有限网格。开口容器双面显示，无厚度。
- 与OpenSubdiv的关系是“公式与固定版本官方规则相互核对”，不是其回归测试通过、不是商业软件截图，也不代表真实引擎性能实测。

## 正文图像完整清单

| 文件 | 教学职责 | 来源、权利与改动 |
| --- | --- | --- |
| originals/01-ed-catmull.jpg | 真实作者Ed Catmull | Steve Jurvetson，2014-04-30；[Commons](https://commons.wikimedia.org/wiki/File:Ed_Catmull,_ETL_2014.jpg)，原发布[Flickr](https://www.flickr.com/photos/jurvetson/13891687919/)；[CC BY 2.0](https://creativecommons.org/licenses/by/2.0/)，3050×3011，原字节，未改动 |
| originals/02-james-clark.jpg | 真实合作者Jim Clark | Knnkanda；[Commons](https://commons.wikimedia.org/wiki/File:James_H._Clark.jpg)；[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)，500×465，原字节，未改动；不推断原页日期等于照片事件日期 |
| assets/03-cube-levels.png | 同尺度0/1/2/4轮实际网格 | 本次原创，CC BY 4.0 |
| assets/04-control-cube.png | 固定输入、坐标与P | 本次原创，CC BY 4.0 |
| assets/05-connectivity.png | 面点—边点—角点后继怎样连接 | 本次原创拓扑示意，CC BY 4.0；故意不表示真实空间位置 |
| assets/06-face-point.png | 顶面四个点的平均 | 本次原创，CC BY 4.0 |
| assets/07-edge-point.png | 普通边中点与新边点的区别 | 本次原创y=0截面示意，CC BY 4.0 |
| assets/08-vertex-rule.png | Q、R、n=3代入公式 | 本次原创，CC BY 4.0 |
| assets/09-first-round.png | 第一轮三类顶点与26/24计数 | 本次原创实际网格，CC BY 4.0 |
| assets/10-two-rules.png | 同拓扑下只加密/光滑更新反例 | 本次原创实际网格，CC BY 4.0 |
| assets/11-subdivision.gif | 0–5轮6帧真实有限网格 | 本次原创，CC BY 4.0；每帧1.3秒，无中间形变插值 |
| assets/12-extraordinary.png | 价数4与3的连接性质 | 本次原创拓扑示意，CC BY 4.0 |
| assets/13-boundary.png | 同一盒子删顶面后的边界规则 | 本次原创实际网格，CC BY 4.0 |
| assets/14-crease.png | 闭合盒子三种无限硬折痕分配 | 本次原创实际网格，CC BY 4.0 |
| assets/15-boundary-corners.png | 单张正方形的角固定选项 | 本次原创独立边界反例，CC BY 4.0 |
| assets/16-limit.png | 有限轮坐标与极限分开 | 本次原创数据图，CC BY 4.0 |
| assets/17-not-sphere.png | 两条极限半径不同 | 本次原创计算与显示，CC BY 4.0 |
| assets/18-independent-stencil.png | 非对称九点权重独立复算 | 本次原创，CC BY 4.0 |

两张照片的法律文本分别为[CC BY 2.0 legalcode](https://creativecommons.org/licenses/by/2.0/legalcode)和[CC BY-SA 3.0 legalcode](https://creativecommons.org/licenses/by-sa/3.0/legalcode)。照片在本文作为独立素材收录，不把CC BY-SA照片改为CC BY 4.0。署名不表示摄影者或被摄者认可本文。

## 核心来源的正文图片盘点

该盘点覆盖1978原论文全部编号图，以及上述两个v3_6_0官方文档中实际出现的全部唯一图片引用。未将导航、品牌页眉、社交图标算作教学图。没有因为图多就截取少量然后称“已收齐原件”。

### 1978论文：11幅编号图

| 原图 | 内容 | 处理 |
| --- | --- | --- |
| 图1，350页 | 规则双三次B样条控制网格和细分点 | 相关；未见开放图版许可，只链接。本文以不同具体立方体自建规则说明 |
| 图2a–d，352页 | 非矩形拓扑的连续细分 | 相关；四个子图全部在盘点范围，不复制 |
| 图3，352页 | 从四面体得到的历史着色曲面 | 相关历史结果；不复制。本文不把自己的立方体渲染冒称此结果 |
| 图4，353页 | 初始四面体及生成线框 | 相关历史结果；不复制 |
| 图5，353页 | 非规则点网格及线框例 | 相关；不复制 |
| 图6，354页 | 图5对应闭合着色物体 | 相关；不复制 |
| 图7，354页 | z=xy鞍形的初始顶视网格 | 相关反例；不复制 |
| 图8，354页 | 鞍形一轮后的网格 | 相关反例；不复制 |
| 图9，354页 | 鞍形多轮后的网格 | 相关反例；不复制 |
| 图10，354页 | 鞍形着色结果 | 相关反例；不复制，正文说明作者承认限制 |
| 图11，355页 | 双二次B样条方案 | 已查看；属于另一个方案，不在本文主线；同样不复制 |

355页下方另有Benson绘图与Summagraphics数字化设备广告，不是本论文实验设备说明，也不是细分算法信息图，排除。本文没有找到可证实“此算法当年在这台具体机器上运行”的开放设备图，因此没有拿年代相近设备充当原机。

### OpenSubdiv官方文档

文档中的图片可以公开查看；代码/文档源许可未被本文外推为图片许可。没有独立查到各图片适用的开放授权，因此以下图像均只链接原固定版本，不收进文章素材，不克隆原构图。许多图还涉及动画角色或生产资产，尤其不能用一个开源代码许可证概括。

完整65项文件名、对应章节和相关性见[原图盘点](source-image-inventory.json)。这份表只含公开出处与处理决定，不含研究缓存或私人工作记录。其中：

- subdivision_surfaces.rst有57个唯一图片文件，全部登记，包括四面体序列、曲面片/参数域/基函数、曲面拼合、价数与隔离、流形/非流形、细分与离散化、拓扑数据、属性插值、Loop对照、边界、半锐折痕及三角面规则。
- mod_notes.rst有8个唯一图片文件，全部登记，包括少控制线、高价数反例、封口方法、密度过渡、对齐、折痕及编辑器。正文没有用其他主题替代必须讲清的拓扑、边界、折痕与极限区别。
- Geri’s Game作品页的4幅剧照与2个页首图像均不作为授权开放素材；只用该页交叉验证作品信息。1998论文全文未成功读取，因此没有虚列“全文图片已核对”的结论。

## AI与原创性

AI用于一手来源定位、中文解释草稿、独立数值代码与图像绘制。所有新机制图与三维输出为本次确定性计算和排版，非AI生成历史照片。人物照片为原文件；没有生成替身人像、原设备或电影截图。正文不声称亲历研发现场或亲测商业软件。
