# 来源与素材

## 一、参考文献

- Max Planck 的黑体辐射定律，任何光学教科书都有推导。本文只用它的结果：给定温度 T，光谱辐射亮度 B(λ, T) 的形状，以及维恩位移 λ_max · T = 2.898 × 10⁻³ m·K。本文的黑体光谱按普朗克公式在 380–780 nm、每 5 nm 一点上直接求值。
- CIE. *Colorimetry*, 3rd edition, CIE 15:2004。用到的内容：CIE 1931 标准色度观察者的 x̄、ȳ、z̄ 三刺激值定义；色度坐标 x、y 的归一化；CIE 1960 UCS 的 u、v；相关色温（CCT）的定义与"在 u-v 平面上找黑体轨迹最近点"的算法。本文的 CCT 计算按这份标准的口径做，但没有引入标准里的 D 系列日光基函数表。
- Andrew J. Wyman, Peter-Pike Sloan, Peter Shirley. *Simple Analytic Approximations to the CIE XYZ Color Matching Functions*. Journal of Computer Graphics Techniques, 2(2), 2013。用到的内容：用多瓣高斯拟合复现 CIE 1931 配色函数。本文的 `cmf()` 就是这套拟合，好处是不用把 81 × 3 张表抄进代码，代价是百分之几的相对误差。
- J. von Kries. *Chromatic adaptation*（1902 年前后的工作，收在 von Kries 的视觉理论文集里）。用到的内容：色适应可以近似成三个感受器各自增益的乘积——也就是本文第十一节的"对角模型"。这个假设的现代表述与适用范围见 Mark D. Fairchild, *Color Appearance Models*, 3rd edition, 2013, 第 6–8 章。
- Gershon Buchsbaum. *A spatial processor model for object colour perception*. Journal of the Franklin Institute, 310(1), 1980。用到的内容：灰世界假设的来源——把场景的平均反射率当作中性灰来反推光源。本文第六节的算法是它的最简形式。
- Marc Ebner. *Color Constancy*. Wiley, 2007。用到的内容：Shades-of-Gray 用闵可夫斯基范数（本文取 p = 6）取代算术平均的做法，以及各类无监督估白算法在同一组场景上的失效模式。本文没有复现书里的完整实验，只借了算法形式。
- C. S. McCamy, H. Marcus, J. G. Davidson. *A color-rendition chart*. Journal of Applied Photographic Engineering, 2(3), 1976。用到的内容：ColorChecker 24 色卡的设计与用途（图 17）。
- David L. MacAdam. *Visual sensitivities to color differences in daylight*. Journal of the Optical Society of America, 32(5), 1942。用到的内容：色差椭圆实验，也就是"刚可分辨色差"这个概念的实验基础。本文用的 0.004（u-v 距离）是文献里常见的量级约定，不是从这篇论文里逐条查出来的数字。
- Günter Wyszecki, W. S. Stiles. *Color Science: Concepts and Methods, Quantitative Data and Formulae*, 2nd edition, 1982。用到的内容：色度学的标准记法与 CCT 计算的边界情况（色点离轨迹太远时 CCT 无意义）。

## 二、照片

两张，都来自 Wikimedia Commons。宽度大于 1062 px 的按比例缩到 1062 px 存放；原文件另存于 `originals/`，未改动。

| 图 | 文件 | 原图尺寸 | 许可 | 作者 | 来源 |
| --- | --- | --- | --- | --- | --- |
| 02 | `02-filament.jpg` | 2624 × 2008 | CC BY-SA 3.0 | Arnoldius | <https://commons.wikimedia.org/wiki/File:Electric_bulb_filament.jpg> |
| 17 | `17-colorchecker.jpg` | 4554 × 3500 | CC BY-SA 4.0 | Jacek Halicki | <https://commons.wikimedia.org/wiki/File:2024_X-Rite_ColorChecker_Passport_Photo_2_(1).jpg> |

许可只覆盖照片本身，不覆盖本文正文与示意图。两张照片都只当实物示例用：图 2 说明白炽灯的发光体长什么样，图 17 说明校色卡长什么样。本文没有从照片里取任何测量数据——照片里的相机、灯光、曝光都会影响颜色，拿它当色度样本是不成立的。

## 三、原创示意图

16 张（01、03–16、18）由 `examples/build_figures.py` 用 `figkit.py` 绘制，身份一律为**原创教学示意**：不是照片、不是相机实拍、不是光谱仪测量结果。图里的每个数字都来自 `examples/results.json`。

| 图 | 内容 | 数字来源（`results.json` 字段） |
| --- | --- | --- |
| 01 | 五个温度的黑体光谱 | `planck_family.curves`（2000/3000/4500/6500/9000 K） |
| 03 | 单色光边界与黑体轨迹 | `spectral_locus`、`locus` |
| 04 | 白纸在七种光源下的三通道读数 | `algorithms[0].rows[*].white_rgb`、`raw_err_deg` |
| 05 | 灰世界假设示意 | 算法示意的色块布局，无数值结论 |
| 06 | 绿色占比与三种方法的误差 | `dominance[*].green_frac / gray_world / shades_p6 / max_rgb` |
| 07 | 有白纸场景的四方法误差表 | `algorithms[0].rows[*].methods` |
| 08 | 没白纸场景的四方法误差表 | `algorithms[1].rows[*].methods` |
| 09 | 七种光源的红蓝比 | `algorithms[0].rows[*].true_rb` |
| 10 | 对角校正的几何含义 | `true_rb`（2000 K 那一行的比例，用作示意刻度） |
| 11 | 对角模型与全矩阵 | 公式对比，无数值 |
| 12 | 元激发的两条反射率 | `metamer.rows[0].spec_a / spec_b / rgb_a / rgb_b / uv_dist` |
| 13 | 元激发在两种光源下的分裂 | `metamer.rows[*].cam_rel / cam_rel_a / uv_dist` |
| 14 | 人眼色差与 JND 阈值 | `metamer.rows[*].uv_dist`、`metamer.jnd_uv` |
| 15 | 两种最近点算法的色温差 | `cct[*].T_by_xy / T_by_uv / diff_k` |
| 16 | 常见光源的色温与白纸读数 | `algorithms[0].rows[*].T / white_rgb / true_rb` |
| 18 | 五条结论 | 总结，数字来自上述各项 |

## 四、模型的设定与简化

`examples/wb.py` 是一个刻意做小的模型。下面这些简化会影响绝对数值，但不影响文章要讲的那几条关系——凡是依赖简化的地方，正文都写明了。

- **波长采样**：380–780 nm，每 5 nm 一个点，81 个采样。真实的光谱数据常用 1 nm 或 5 nm 表，5 nm 对宽光谱足够。
- **配色函数**：用 Wyman–Sloan–Shirley 的多瓣高斯拟合，不是官方表格。可见光区的相对误差在百分之几。
- **假相机**：三条高斯形感光曲线，中心 600 / 545 / 450 nm，宽度（σ）45 / 40 / 30 nm，峰高都取 1.0。真实传感器的曲线更宽、重叠更多，所以真实的串色比这篇文章里更严重，对角模型的误差也更大。
- **光源**：黑体。D65 用 6504 K 的黑体代替，真实 D65 是 CIE 日光基函数组合，色坐标有百分之几的差别。
- **场景**：21 块平色块。随机色块的反射率是"0.05–0.25 的随机底色 + 两三个高斯峰"（峰心 420–660 nm，宽度 20–60 nm，幅度 0.1–0.55）；绿色块是一个 550 nm、宽 35 nm、幅度 0.55 的峰；白纸是平坦的 0.9。没有镜面反射、没有荧光、没有阴影和几何遮挡。
- **成像**：只有三通道积分，没有噪声、没有饱和、没有去马赛克、没有 sRGB 传输函数、没有色调曲线。所以文章里的"角度"是线性 RAW 空间的角度，不是你从 JPEG 上量的角度。
- **估白算法**：灰世界（算术平均）、Shades-of-Gray（p = 6）、最大 RGB、已知灰卡。没有实现任何基于机器学习的方法，也没有实现贝叶斯/色域映射那一类。
- **对角校正**：只用增益，不做法向量的全矩阵拟合。图 11 只是在讲两者结构上的差别，没有做数值对比。

## 五、明确没做的事

1. 没有用真实相机、没有 RAW 文件、没有实际拍摄。所有"相机读数"都来自上面那三条假感光曲线。
2. 没有实测光谱。文中所有光谱都是模型按普朗克公式或合成反射率算出来的。
3. 没有引入真实的 CIE 配色函数表、D65 相对光谱功率分布表、ColorChecker 每块的实际反射率。图 17 只用它的外观，没有从它取数。
4. 没有讨论个体观察者差异（observer metamerism）与色适应变换（Bradford、CAT02）。这两件事都在"三通道不够"这个结论的下游。
5. 没有做多光谱/四通道相机的对照实验。正文里"上四通道能补一部分"是定性判断，本文没有验证。
6. 没有目视检查渲染出来的图片：本次审读的模型不能读图，`review.md` 里记了 `VISUAL_REVIEW_NOT_RUN`。图的行宽、字号、重叠是由 `figkit.py` 的自动闸门把关的，不是人眼看过的。
7. 没有核对照片里物体的型号与状态（图 2 的灯泡型号、图 17 的色卡批次），只用了 Commons 文件描述里的信息。
