# 来源与说明

## 图片

两张实物照片来自 Wikimedia Commons，下载的是原始文件，只在宽度超过 1062 px 时按比例缩到 1062 宽（`examples/build_figures.py` 里的 `photo()` 只缩放，宽度已经小于 1062 的直接复制字节）。未裁切。

| 文件 | 原始尺寸 | 作者 | 许可 | 原始页面 |
| --- | --- | --- | --- | --- |
| `02-gpu-die.jpg` | 3939×3932 | Martijn Boer | 公有领域 | <https://commons.wikimedia.org/wiki/File:ATI_RV670_die_shot_-_27808926667.jpg> |
| `16-radeon.jpg` | 3260×2445 | Cjp24 | CC BY-SA 4.0 | <https://commons.wikimedia.org/wiki/File:ATI_Radeon_HD_2400_Pro,_128MB_(1).jpg> |

其余 16 张（`01`、`03`–`15`、`17`、`18` 和 `cover.png`）是本文原创的教学示意，由 `examples/build_figures.py` 生成，不是照片，也不代表任何真实芯片的内部结构或任何具体显卡的地址计算方式。

照片的身份只有一条：它拍的那个东西。`02-gpu-die.jpg` 是一颗 ATI RV670 的裸片，本文只用它引出"显卡把纹理按小块排"这件事，没有声称照片里某片区域就是纹理缓存，也没有核对过 RV670 的纹理分块尺寸；`16-radeon.jpg` 是一块 ATI Radeon HD 2400 Pro 显卡，同样只是场景照。文中关于纹理分块的描述（八乘八、块内按 Z 序或变体）是行业内公开的常见做法，不是从这两张照片测量出来的。

## 数字

正文和图片里的每个数字都由 `examples/zorder.py` 算出、`examples/run_model.py` 写进 `examples/results.json`，`examples/build_figures.py` 只从 `results.json` 取值（图 4–6、8、15 的路径另外 import 同一个模块现算）。跑一遍：

```sh
cd examples && python3 run_model.py && python3 build_figures.py
```

纯标准库，不需要安装任何东西（画图需要 Pillow）。`run_model.py` 约 6 秒。

模型设定：

- **网格**：二维实验用 256×256（65536 格），三维实验用 32×32×32（32768 格）。八乘八（64 格）只用于画图和"前缀是方块"的枚举。
- **三种顺序**：逐行（`y * n + x`）、Z 序（位交错，x 在偶数位、y 在奇数位；三维步长 3）、Hilbert（标准的迭代 `x y → d` 与 `d → x y` 变换）。
- **步长统计**：对全部相邻编号求欧氏距离，报告平均、95 分位、最大值，以及"超过 4 格"的个数。这里的距离是格数，不是字节数。
- **矩形段数**：把一个 w×h 矩形里所有格子的编号取出来排序，数有多少段连续的整数（每段 = 一次寻道 + 一次顺序扫描）。
  - **对齐**：左上角取 `max(w, h)` 的整数倍。
  - **随机偏移**：左上角均匀随机，每个形状 400 次，取平均。种子固定。
  - 注意：这里的「对齐」是按形状的较长边对齐，所以 64×8 这种形状在 y 方向也对齐到 64，而不是对齐到 8。正文第八节的表格就是这个设定下的结果。
- **缓存线**：每像素一字节，一条线 32 字节；数一个方块碰到几条线、以及最小到最大编号的跨度（字节）。这两个数都是精确值，不是采样。
- **压缩**：4096 个点、16 个团、每团高斯散射 σ=12 格，坐标钳到 1024×1024 网格内；按三种编号排序后，求相邻编号之差，再求"表示这个差值需要几位"（`floor(log2(d)) + 1`，差为 0 的情形被排除）。这是对变长编码成本的一个粗糙代理，不是真的跑了一遍 varint 编码器。
- **三维**：4×4×4 的立方体，对齐与随机偏移各 60 次。
- **随机数用自写的 xorshift32**（种子先过一次 LCG 再进 xorshift）。这一点是有意的：早期版本用 LCG，它的低位数几乎是周期性的，会让"随机偏移"退化成少数几个位置。换成 xorshift32 之后，随机偏移的段数才稳定在本文写的那些值上。

关键数字的来历：

- **27 / 011011**：`morton2(5, 3)`，图 3。
- **1.988 / 1.665 / 1.000**：三种顺序在 256×256 上的平均步长；对应 95 分位 1.00 / 3.16 / 1.00，最长 255.0 / 255.0 / 1.0，超过 4 格的次数 255 / 2047 / 0。
- **8.00 / 1.00 / 1.00**：八乘八对齐方块在三种顺序下的段数。**14.28 / 8.15**：同样的方块随机偏移时，Z 序与 Hilbert 的段数。
- **62.01 vs 32.27 vs 32.00**：三十二乘三十二的方块，随机偏移。
- **8 条线 / 1800 字节**：八乘八方块在逐行存法下碰到的缓存线条数与地址跨度；**2 条 / 64 字节**：Z 序。十六乘十六对应 **16 条 / 3856 字节** 与 **8 条 / 256 字节**。
- **4.31 / 3.61 / 3.55 位**：三种排序下相邻编号之差的平均位数。
- **16.00 / 1.00 / 24.37**：三维对齐立方体的逐行段数、Z 序段数，以及随机偏移的 Z 序段数。

## 明确没做的事

- **没有目视看图**。成稿所用的模型不支持读图，`review.md` 里记了 `VISUAL_REVIEW_NOT_RUN`。图里的几何由 `figkit.py` 的断言（越界、重叠、字号下限、颜色登记）机械检查，但"好不好看、好不好懂"没有经过人眼。
- **没有在真机上测缓存命中率**。第九节的"条数"是从地址算出来的，不是跑 perf 或 GPU 计数器测出来的。真实的缓存有组相联、有预取、有 TLB，本文的模型一个都没算。
- **没有核对具体硬件的分块格式**。第十二节描述的是"切成八乘八小块、块内按 Z 序或变体"这一类通用做法。各家 GPU 的具体 swizzle 模式（块大小、块内顺序、是否有 XOR 混淆）不一样，本文没有对着任何一份寄存器文档逐位核对。
- **没有实测数据库**。第七、八节的段数是"排序数组 + 数连续段"，不是真的对一个空间数据库跑查询。真实的 R 树、Hilbert R 树、PostGIS 的 GiST 索引有自己的代价模型。
- **压缩那一节只是代理指标**。算的是"差值需要几位"，没有实现变长编码，也没有比较 end-to-end 的字节数。
- **三维只做了 32³ 和 4³ 立方体**，没有覆盖体素引擎里常见的非立方体查询（比如 1×N×N 的切片）。
- **Morton 1966 的原文没有读到**。文中关于那份 IBM 技术报告的年代、机构、动机（大地测量数据库的磁带排序）来自公开的二手叙述，没有对照原件。
- **没有比较别的曲线**。Morton 与 Hilbert 之外，还有 Sierpiński、Peano、Moore 曲线，以及 Z 序的各种变体（比如按位取反后再交错）。本文没有做横向测评。

## 引用与延伸

- Morton, G. M. *A Computer Oriented Geodetic Data Base and a New Technique in File Sequencing*. IBM Canada, 1966.（Z 序的原始技术报告）
- Hilbert, D. *Über die stetige Abbildung einer Linie auf ein Flächenstück*. Mathematische Annalen 38, 1891.
- Finkel, R. A., Bentley, J. L. *Quad Trees: A Data Structure for Retrieval on Composite Keys*. Acta Informatica 4, 1974.
- Orenstein, J. A., Merrett, T. H. *Spatial Query Processing in an Object-Oriented Database System*. SIGMOD 1984.（Z 序进数据库）
- Moon, B., Jagadish, H. V., Faloutsos, C., Saltz, J. H. *Analysis of the Clustering Properties of the Hilbert Space-Filling Curve*. IEEE TKDE 13(1), 2001.（Hilbert 的聚类性质分析）
- Intel. *Intel 64 and IA-32 Architectures Software Developer's Manual*, BMI2 指令集部分（`PDEP` / `PEXT`）。
