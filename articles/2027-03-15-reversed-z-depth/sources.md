# 来源与说明

## 图片

12 张正文图与 `cover.png` 全部是本文原创的教学示意，由 `examples/build_figures.py` 生成。几何断言写在 `examples/figkit.py` 里：文字不出画布、不互相压、任何字号的文字换算到 354 px 宽的显示宽度后不小于 12 px。没有使用照片、截图或第三方素材，因此不涉及第三方署名与许可。

图里的曲线、柱子、小格全部来自 `examples/results.json`；`build_figures.py` 只负责取值和摆放，不改数。图 10 的两块掩码（1000 个小格）直接来自 `subtract_after.trap_mask` 与 `subtract_after.matrix_mask`，一个格子就是一对相邻点，红色表示这一对被压成了同一个深度值。

## 数字

正文和图片里的每个数字都由 `examples/depth.py` 算出、`examples/run_model.py` 写进 `examples/results.json`，`examples/build_figures.py` 只从 `results.json` 取值。跑一遍：

```sh
cd examples && python3 run_model.py && python3 build_figures.py
```

纯标准库（画图需要 Pillow），`run_model.py` 约 0.21 秒，`build_figures.py` 约 3.5 秒。

模型设定：

- **全局参数**：`near = 0.1`、`far = 1000`（米），24 位定点（`q_fixed(bits=24)`，格距 2 的 −24 次方 = 5.9605e-8）与 float32（`struct.pack('<f', …)` 舍入）两种量化。
- **`curve`**：61 个对数分布的距离，画图 2 与图 7 的曲线用；每点记 `d_std`、`d_rev`。
- **`depth_values`**：六个整数距离上同时给 `d_std` 与 `d_rev`，图 2 的图例数字取自这里。
- **`steps`**：near = 0.1、far = 1000，六个距离上分别算定点、float32 标准、float32 反转的格距。`formula_std` 与 `formula_rev` 是连续估算值（用相对精度 v·2^−24 代替逐值的 ULP），用来核对离散热度的量级；反转那一列两者差最多一倍，差的正是浮点的八度边界（见下）。
- **`near_steps`**：near 取 0.1 / 1 / 10，z 取 20 / 100 / 500，共九组。
- **`near_sweep`**：z = 500 米，near 从 0.05 扫到 100（11 个值），只算定点。
- **`far_sweep`**：z = 500 米、near = 0.1，far 取 600、1000、2000、1e4、1e5、1e6。
- **`collapse`**：在 near 与 far 之间按对数取 20000 个距离，排序后逐对比较量化后的深度值。`indist` 是「相邻两点同值」的对数，`swap` 是「相邻两点顺序颠倒」的对数。反转映射存的值随距离递减，所以比较时显式传 `decreasing=True`（`collapse_count` 的默认假设是递增，不传会把 19999 个正常递减对全判成颠倒）。`merged_z` 记录被合并的那些对子分布在哪儿。
- **`threshold`**：`z_for_cell(target)` 二分找「格距长到 target」的距离。对每个间隙 `sep` 给三个距离：格距 = sep（`z_guarantee`，到此为止一定有保证）、格距 = 2·sep（`z_half`，此时一半的对子合并）、格距 = 10·sep（`z_all`，九成合并）。`threshold_near` 是同样三列，固定 1 厘米、near 取三档。
- **`merge_curves`**：图 9 的四条曲线。比例按 1 − sep/格距 算，夹在 [0,1]：间隙比一格窄时，两个面要么正好跨在格边两侧、要么同格，比例就是间隙与格距之比。这是几何近似，不含「两个面各自的位置先被投影矩阵舍入一次」的二阶效应。
- **`rev_worst`**：在 1 米到 999 米之间按对数取 40 个距离，逐点算反转 float32 的格距，取最大者。
- **`subtract_after`**：相机在原点、远平面 10000 米，100 米处横放 1000 个点、间隔 1 毫米。两条路径：投影矩阵直接给出反转深度（`projection(…, reverse=True)`），以及「先算标准深度、在 float32 里做 1 − x」。`trap_mask` / `matrix_mask` 是逐对的布尔掩码，图 10 直接画它们。
- **`premultiply`**：相机放在 1000 米外、远平面 10000 米，1000 个点、间隔分别取 0.5 / 0.2 / 0.05 米。`pipeline_pair` 给两条路径的量化结果：一条把 view 与 projection 预乘成一个 float32 矩阵再乘顶点，一条分开乘。世界坐标取负号，保证第 i 个点的距离随 i 增大，这样「相邻对」的方向与「递增/递减」的判断一致。
- **自检**：`selfcheck` 有四条——`std_depth(n) = 0`、`std_depth(f) = 1`、`rev_depth(n) = 1`、`rev_depth(f) = 0`，外加一条「near = 0.1 那一行定点与 float32 标准的相对差 < 1e-6」。

关键数字的来历：

- **48 厘米**：900 米处 24 位定点的格距，0.48275 米。同一位置的 float32 标准映射也是 0.48275。
- **7.4 微米**：900 米处 float32 反转的格距，7.366e-6 米。反转存的值是 1.1112e-5，float32 在那里的 ULP 是 9.1e-13，斜率是 1.235e-7 每米，两者相除即得。
- **0.900 / 0.990 / 0.999 / 0.9999**：1、10、100、500 米处的标准深度值，对应「前十年吃掉九成」。
- **298 / 149 / 29.8 / 14.9 / 1.48 / 0.134 毫米**：near 取 0.05 / 0.1 / 0.5 / 1 / 10 / 100 时 500 米处的格距。它们按 1/near 缩放，基准是 near = 0.1 时的 148.997 毫米；near 每乘 10，格距就除 10，多出来的一点偏差来自 (f−n)/(n·f) 里 near 也动了 f−n。
- **66 / 66 / 0**：20000 个对数点上，定点、float32 标准、float32 反转各自被压成同值的相邻对数。定点与 float32 标准同为 66，是因为两者在远端完全重合。
- **795 / 927 米**：被合并的对子里，第一对与中位数的位置。
- **129.5 / 183.2 / 409.6 米**：1 厘米间隙的保证界限、一半界限、全并界限。
- **834 / 1000**：事后做 1 − d 时，1000 个点里 834 对被压成同一个值；矩阵直算是 0。
- **495 / 409 / 563 与 487 / 737 / 922**：相机在 1000 米外时，预乘与分开乘在三个间距下的合并对数；颠倒对数分别是 0 / 216 / 191 与 0 / 0 / 0。

## 文献与文档

深度精度的出处，按 DOI 核过卷期页码：

- Upchurch, Desbrun, *Tightening the Precision of Perspective Rendering*, Journal of Graphics Tools 16(1):40–56, 2012，DOI `10.1080/2151237x.2012.649987`。用误差分析比较各种深度布局，也是「把 view 与 projection 预乘会引入额外误差」这一条的主要来源。
- Lapidous, Jiao, *Optimal depth buffer for low-cost graphics hardware*, Proceedings of the ACM SIGGRAPH/EUROGRAPHICS workshop on Graphics hardware (HWWS '99), 67–73, 1999，DOI `10.1145/311534.311579`。把深度反过来存以换取精度的那篇。
- Nathan Reed, *Depth Precision Visualized*, 2015-07-03，`https://reedbeta.com/blog/depth-precision-visualized/`。抓下来读过全文（21 KB 静态 HTML）。正文里「d 是 1/z 的线性重映射」「反转 Z 让 float 缓冲几乎零错误率」「分离 view/projection 只是把颠倒换成合并」「far 几乎无影响」这几条都出自这篇，图也照着它的四张对照图重画成了自己的版本（没有使用它的图）。
- NVIDIA 开发者站转载的同一篇，`https://developer.nvidia.com/content/depth-precision-visualized`（55 KB）。内容与上一条一致，用来核对转载没有改动数字。
- Emil Persson 关于「1/z 在屏幕空间线性」的笔记：正文第十一节只提到「Reed 的文章引了它」，我没有直接抓取 Persson 的原页，因此没有引用它的具体措辞。

## 关于浮点的那个锯齿

图 8 里反转那条线不是平滑的。原因是 float32 的 ULP：值落在 [2^(e−1), 2^e) 里时，间距是 2^(e−24)；距离再远一点，存的值掉进下一个八度，间距减半，而 1/z 的斜率按 z² 变小，两个效应叠加成锯齿。`steps` 里同时留了 `formula_rev`（用相对精度 v·2^−24 估的连续值）和 `f32_rev`（逐值算 ULP 的离散步长），两者差最多一倍，这个差就是齿高。

## 明确没有做的事

- **没有在真实 GPU 上跑**。全文没有帧率、没有带宽、没有填充率。所有结论都是「量化后的深度值是否相等」，不含视口变换、光栅化、深度测试的实现细节。
- **没有测 MSAA、深度压缩、layered depth**。这些会改变「相邻两个面能不能分开」的实际表现，模型没有覆盖。
- **没有分析阴影贴图与对数深度缓冲**。对数深度（logarithmic depth buffer）是另一条路，正文没有比较它与反转 Z 的取舍，也没有实验。
- **没有在引擎里验证**。文中没有引用任何引擎的实现细节，也没有在 Unity、Unreal、Godot 里复现实验。
- **没有做二阶级联误差**。`merge_prob` 用的是几何近似（比例 = 1 − sep/格距），没有把「两个面各自被投影矩阵舍入一次」也算进去，所以图 9 的斜坡是理想化的。
- **没有把 `1 − d` 的失败做成分位数**。第十一节只给「834 / 1000」这一个总数，没有按距离分层看哪一段最惨。

## AI 辅助说明

正文与代码由 AI 助手（Claude）在同一轮会话里写出来，审读也是同一个助手做的，独立性有限。所有数字都能用 `run_model.py` 重跑得到；引用到的 DOI 逐条查过 Crossref 的标题、卷期、页码；Reed 与 NVIDIA 两页都是实际抓下来读过正文的，抓不到正文的来源没有引用。
