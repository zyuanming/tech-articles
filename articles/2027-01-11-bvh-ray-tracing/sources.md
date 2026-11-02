# 来源与许可

## 一、文字参考

1. Wikipedia, *Bounding volume hierarchy*。存取方式：`https://en.wikipedia.org/wiki/Bounding_volume_hierarchy?action=raw`（2026-11 抓取，19 289 字节）。用于：BVH 的定义与「父节点不相交则子节点不必测」的表述（原文件第 3 段）、包围盒选择的权衡与轴对齐包围盒「几字节、求交快」的说明（第 1 节）、节点属性的建议（子树内图元要靠近、根附近剪枝收益最大、兄弟盒子重叠要少）、二分树在实践中占绝对多数、自上而下构造最流行、SAH 常与等宽分桶一起用（第 2 节）、遍历时「先走近的那个孩子，若找到比另一个盒子更近的交点就安全跳过」这条优化（第 63 行）、以及 BVH 被用于光线追踪之外的点定位与最近邻任务（第 123 行）。
2. Wikipedia, *Ray tracing (graphics)*。存取方式：`https://en.wikipedia.org/wiki/Ray_tracing_(graphics)?action=raw`（2026-11 抓取）。用于：Arthur Appel 1968 年用光线求最近表面并朝光源发线判断阴影（第 24 行）、Turner Whitted 1979 年首次给出递归光线追踪（镜面反射、折射、抗锯齿）并在贝尔实验室拍出《The Compleat Angler》（第 30 行）、BVH 用于减少求交计算（第 217 行）。
3. Wikipedia, *Utah teapot*。存取方式：`https://en.wikipedia.org/wiki/Utah_teapot?action=raw`（2026-11 抓取）。用于：模型由犹他大学的 Martin Newell 于 1975 年制作（第 18 行）、壶是 Melitta 品牌、由 Lieselotte Kantner 设计（第 16 行）、实物 1974 年在盐湖城 ZCMI 百货购得、1984 年捐给波士顿计算机博物馆、1990 年后藏于山景城计算机历史博物馆、馆藏编号 X398.84（第 68 行）、妻子 Sandra 提议画家里的茶具、他在 Tektronix 存储管上调贝塞尔控制点（第 51 行）、他把数据公开后别人开始复用（第 55 行）。
4. Crossref 元数据（`https://api.crossref.org/works`），用于核对三条文献的标题、作者、机构、年份与 DOI：
   - Steven M. Rubin, Turner Whitted, *A 3-dimensional representation for fast rendering of complex scenes*, SIGGRAPH '80, 1980-07，DOI `10.1145/800250.807479`，作者机构为 Bell Laboratories, Holmdel, New Jersey。
   - Jeffrey Goldsmith, John Salmon, *Automatic Creation of Object Hierarchies for Ray Tracing*, IEEE Computer Graphics and Applications, 1987-05，DOI `10.1109/mcg.1987.276983`。
   - Ingo Wald, *On fast Construction of SAH-based Bounding Volume Hierarchies*, 2007 IEEE Symposium on Interactive Ray Tracing, 2007-09，DOI `10.1109/rt.2007.4342588`。

**没有读过的**：本文没有读 Rubin & Whitted 1980、Goldsmith & Salmon 1987、Wald 2007 三篇论文的正文，只核对了 Crossref 的题录。所以正文只写「谁在什么年份提出/给出了什么」，不写它们的算法细节、数据规模或结论强度。Whitted 那篇论文的年份有一处小分歧：Wikipedia 的引用字段写 1979（SIGGRAPH 会议年），期刊版是 1980 年的 *Communications of the ACM*；正文按 Wikipedia 的 1979 写。

**一处刻意没写**：正文没有说「BVH 是谁发明的」。Wikipedia 的 BVH 条目通篇没有历史段落，我没有别的可靠来源能确认这个荣誉该给谁，所以只写了 1980 年 Rubin 与 Whitted 的那篇「把场景组织成层次结构来加速求交」——这是一篇确实存在、可以被引用的论文，至于它是不是最早的一篇，本文不下判断。

## 二、照片（1 张）

| 图 | 文件 | 作者 | 许可 | 原尺寸 |
| --- | --- | --- | --- | --- |
| 图 17 | `Utah_Teapot_circa_1974,_Computer_History_Museum.jpg` | The wub | **CC BY-SA 4.0** | 4484×3363 |

来自 Wikimedia Commons（`File:Utah Teapot circa 1974, Computer History Museum.jpg`），拍摄于 2023-07-15，拍摄地点是山景城的计算机历史博物馆。原图保存在 `originals/`，未做裁剪、调色或重压缩；`assets/` 里的版本只在宽度超过 1062 px 时等比缩小一次（Pillow `LANCZOS`，JPEG 质量 92，从 4484 缩到 1062）。

图注里的「1970 年代」不是笔误：壶是 1974 年买的，模型数据是 1975 年做的，文件名里的 circa 1974 指的是壶本身。正文里这两个年份都写出来了，没有把壶的年代和模型的年代混成一个。

同一次检索还下载了 `File:Original Utah Teapot.jpg`（Marshall Astor 摄于 2007-01-10，CC BY-SA 2.0，1840×1380，拍的也是同一只壶）。它最后没有用上：一张壶的照片已经够说明「实物还在」，再放第二张同角度、同对象的照片只是重复。**该文件已从 `originals/` 删除**，不随文章发布，所以也不再需要保留它的许可声明；此处记录一笔是为了说明这张照片曾经下载、为什么没用。

## 三、18 张示意图的来源

除图 17 外，其余 17 张都是本仓库脚本生成的原创示意，画法见 `examples/build_figures.py`。图里的每一个数字都来自 `examples/results.json` 或 `bvh.py` 的现场渲染，没有一个是手写的。

| 图 | 内容 | 数据来源 |
| --- | --- | --- |
| 1 | 场景渲染（320×180，4 倍抗锯齿） | `bvh.render()` 现场重渲染；`hero.rays`、`hero.tests` 记在 `results.json` |
| 2 | 渲染循环五步 | 无数字；结构示意 |
| 3 | 光线与球求交 | 无数字；`t0`、`t1` 由图上那条示意光线实时解一元二次方程算出 |
| 4 | 朴素遍历 | 无数字；示意图里的 4 条光线 × 8 个图元是编的，页面下方注明了 |
| 5 | slab 判定 | 无数字；盒子和光线的坐标是示意图，区间由 `slab()` 同一套公式现场算出 |
| 6 | BVH 树形 | `build.sah.nodes / leaves / depth / sah_ops` |
| 7 | 俯视图 | `topview.spheres`、`topview.boxes`（前两层节点的真实包围盒） |
| 8 | 三种切法对照表 | `build.{mid,spatial,sah}.*`、`compare.rows.*.tests_per_ray` |
| 9 | SAH 代价曲线 | `sah_profile.rows[*].{split,left,right,cost}`（11 个候选切点，`axis=2`） |
| 10 | 两张渲染并排 | `bvh.render()` 现场重渲染；左图是朴素、右图是 BVH，`compare.pixel_sha256` 与 `identical` |
| 11 | 每光线求交对比 | `compare.rows.{naive,mid,sah,spatial}.tests_per_ray`、`scene.prims`、`speedup` |
| 12 | 开销分解 | `compare.rows.sah.{nodes,pruned,tests,rays}` |
| 13 | 图元数缩放 | `scaling[*].{spheres,prims,bvh,naive}` |
| 14 | 遍历三变体 | `traversal.{normal,far_first,no_prune}.{tests,nodes}`、`traversal.rays` |
| 15 | 逐像素热力图 | `heatmap.values / max / mean`（160×90 纯主光线的求交次数） |
| 16 | 光线构成 | `rays.{primary,total,secondary_per_primary}` |
| 17 | 茶壶实物 | 见上一节 |
| 18 | 四条结论 | 无新数字；引用了 `scene.prims` 与 `compare.rows.sah.tests_per_ray` |

封面（`cover.png`）用的就是图 1 那张渲染，右侧两个数取自 `scene.prims` 与 `compare.rows.sah.tests_per_ray`。

## 四、模型做了什么，没做什么

正文最后一节写了同一份清单，这里补充与来源相关的部分。

**算了的**：光线与球、光线与轴对齐平面的解析求交；包围盒 slab 判定；`mid` / `spatial` / `sah` 三种建树，以及各自的比较次数；带距离剪枝的遍历，以及访盒数、剪枝数、求交数的计数；Whitted 风格的一次漫反射阴影 + 一次镜面反射；4 倍超采样抗锯齿；地板「无限平面 vs 144 块砖」的对照实验。

**没算的**：SIMD、GPU、打包遍历、真实材质与全局光照、建树的时间开销（只数比较次数）。所以正文里没有「每秒多少帧」「比某某渲染器快多少」这类结论——这个模型没有资格谈墙上时间。

**几个可以手算复核的数**：

- 朴素遍历的求交次数必须正好等于「光线数 × 图元数」。`run_model.py` 里有一条断言守着这件事；160×90 那一帧是 25 495 × 464 = 11 829 680。
- 92.6 倍 = 464.0 ÷ 5.0127。取的是同一帧、同一批光线的总求交次数之比。
- SAH 曲线最低点：代价 276 237 = 左盒表面积 × 222 + 右盒表面积 × 242，左边 222 + 右边 242 = 464，正好是根节点的全部图元。
- 热力图平均 3.92 是 14 400 条纯主光线的算术平均；正文里 5.01 那条用的是含阴影线与反射线的 25 495 条光线，两个口径都在正文和图注里标出来了，没有混用。
- 「无限平面」对照实验里，无限平面版本只有 321 个图元（320 球 + 1 块大平面），每条光线却要 4.22 次求交，比 464 个图元的砖地版本（3.95）还多。这条结论来自 `results.json` 的 `floor` 键，同一批 3600 条光线。

## 五、审读范围

- 正文与图的数字一致性：逐项与 `results.json` 对过。
- 渲染一致性：`build_figures.py` 每次运行都会重渲染 160×90 那一帧，断言 sha256 与 `results.json` 里的 `pixel_sha256` 一致，不一致就直接报错退出。这是一条比人工看图更硬的检查。
- **`VISUAL_REVIEW_NOT_RUN`**：本次成稿所用的模型不能读图，17 张示意图和那张照片**没有经过目视检查**。`figkit` 的自动检查（越界、文字重叠、字号下限、安全边带、底色越界）全部通过，但它查不出「图画得对不对、好不好看」。
