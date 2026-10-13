# 来源、图像身份与计算范围

## 核心问题与旧文关系

本篇是按读者明确要求展开的独立Doom零基础系列第三篇，承接前两篇的同一双房间，解释“先同侧、后检查另一侧外框”怎样提前排除整组墙。已有两篇BSP文章保留不改；本篇有意重新讲解其核心主题，不以换标题冒充一个全新主题。

新增解释以可对应的模型画面、两层分组、明确投影范围和真实MAP01节点记录为主，不从向量叉积或代码递归起步。本篇没有运行Doom、Chocolate Doom或地图编辑器，没有实测剪枝次数、帧率或历史机器性能。

## 一手事实依据

id Software代码固定参照：[a77dfb96cb91780ca334d0d4cfd86957558007e0 / Linux Doom 1.10](https://github.com/id-Software/DOOM/tree/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10)。核对日期2026-10-13；这是公开代码参照，不称为本次运行的1993年DOS程序。

- [doomdata.h](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/doomdata.h)：mapnode_t保存分割起点、方向、两个孩子的包围框与引用；mapseg_t包含端点、linedef引用和side；mapsubsector_t保存连续seg范围；NF_SUBSECTOR标记末端引用。支撑节点、seg和subsector的身份。
- [r_main.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_main.c)：R_PointOnSide确定观察点在哪侧；渲染从numnodes−1的根开始。本文只用水平/竖直分割作手算，不把教学比较符号冒充源码任意方向、定点精度和共线边界的完整实现。
- [r_bsp.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_bsp.c)：R_RenderBSPNode先处理玩家所在子侧，再以R_CheckBBox检查另一侧。R_CheckBBox从当前位置判断外框相对视野的横向范围，并用已封闭区间测试；“可能可见”不保证各墙真可见。
- 同文件的R_ClipSolidWallSegment会更新solidsegs；R_ClipPassWallSegment使用已有记录进行裁剪，但不把自己的范围加入封闭表。R_AddLine区分单侧实墙、闭合双侧边与仍有开口的边；本文只解释普通不透明墙及普通开口，不涵盖天空特殊处理和视觉技巧。
- [p_setup.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/p_setup.c)：P_LoadNodes、P_LoadSegs、P_LoadSubsectors从地图相应数据块装入既有结构；并非每次转头都重新建树。
- [Freedoom截图页](https://freedoom.github.io/screenshots.html)：确认本文两张截图来自Phase 1 / Chocolate Doom，原320×200输出被清晰放大并调整显示比例为1600×1200；同时明确截图以Freedoom自身许可复用。

## 真实数据的固定版本与可复核数值

Freedoom素材与MAP01固定提交：[3ac019628d70b812ffb722f7f2365771b76a9d29](https://github.com/freedoom/freedoom/tree/3ac019628d70b812ffb722f7f2365771b76a9d29)。此处只表示取材快照，不伪称某个正式发行版。

[原MAP01文件](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/levels/map01.wad)与[本文保留副本](examples/freedoom-map01.wad)同字节：124013字节，SHA-256 d9da5d7f8d97d6555182a04326f306dde6fd40da1186a6fec18143c7ccddd20d。它与首篇取材相同，沿用已核来源与许可。

- NODES：19712字节，每记录28字节，共704个。根是最后一个，编号703。
- 根起点(400,−1280)，方向(−16,0)，因此分割直线y=−1280。子引用依次为567、702；它们仍是节点，不是叶子或墙编号。
- 根孩子0外框：左−248、右2176、下−1280、上1600。孩子1外框：左−192、右544、下−1800、上−1280。图中按文件记录绘出，未把两种颜色虚构成编辑器选择结果。
- SSECTORS：2820字节，每记录4字节，共705个。SEGS：27168字节，每记录12字节，共2264个。LINEDEFS共1272条；SECTORS共206个。
- 从根追踪，全部704节点和705末端组各到达一次；各末端seg范围合法且总数2264。这里只做静态文件结构检查，不表示运行时会访问全部记录。
- 图中玩家1起点来自THINGS：平面(−192,−192)、朝向0。它不是对任何官方截图相机位置的反求。
- 真实拆分样例：linedef539端点(1024,−544)和(1696,−544)。同一side=0对应seg671：(1024,−544)→(1248,−544)，seg663：(1248,−544)→(1696,−544)。两段合起来恰为原边；特意核同一侧，避免混淆正反面与切分。
- 附带[inspect_bsp.py](examples/inspect_bsp.py)用Python标准库只读上述文件并打印记录，不执行地图为程序、不运行引擎、不联网。

## 真实图像、原文件与许可

Freedoom素材版权：Copyright © 2001-2024 Contributors to the Freedoom project。本文随附[完整BSD-3-Clause条款、条件与免责声明](licenses/Freedoom-COPYING.txt)和[贡献者清单](licenses/Freedoom-CREDITS.txt)。不暗示Freedoom为文章背书，正文CC BY 4.0不改变第三方素材许可。

- assets/01-freedoom-foreground.png：官方[原文件p1_1.png](https://freedoom.github.io/img/screenshots/p1_1.png)，1600×1200，60607字节；保留原尺寸原字节。职责：开场让前景墙面与远处可见场景成为真实视觉对象。它不是本文两房间，也不把截图内任何背景对象声称为本文实测被剪枝的墙。
- assets/22-freedoom-return.png：官方[原文件p1_3.png](https://freedoom.github.io/img/screenshots/p1_3.png)，1600×1200原字节；复用第二篇已核材料。职责：末尾把“只留下可见部分”的机制放回真实游戏画面；不声称从图上读取了引擎内部处理统计。
- [assets/brick-original.png](assets/brick-original.png)：128×128，[Freedoom patches/brick.png](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/patches/brick.png)，用于模型墙面，保留原字节；它是源图块，不自动等于引擎内部完整texture定义。
- [assets/floor-original.png](assets/floor-original.png)：64×64，[Freedoom flats/floor0_1.png](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/flats/floor0_1.png)，用于模型地板/天花板，保留原字节。
- 地图可视化、素材在原创模型中的重复展示仍保留Freedoom BSD条款。本文没有复制商业Doom WAD美术，也不把其源码GPL扩展为游戏图像授权。

## 逐图教学职责

以下图像由本次原创程序制作。纯几何示意和新增中文排版属本文原创CC BY 4.0；真实地图数据及图块仍按上述BSD许可。它们不是假实拍或假编辑器界面。

- cover.png：独立封面，以同一加墙模型提示遮挡主题，不计入正文概念说明。
- assets/02a-room-open.png、02b-room-blocked.png：同一观察位置、同一双房间加实墙前后计算结果；两张共同承担一次状态变化说明，不是两个无关案例，也不是Doom运行截图。
- assets/03-added-wall-plan.png：新增墙体与原房间、玩家、后墙的确切平面关系。墙厚16，y32～160，左右开口未承诺可通行。
- assets/04-first-cut.png：沿x256作第一次分组；红色墙体与虚线分组线身份不同。
- assets/05-second-cut.png：只在B内沿x384继续分组，分割线穿过空气也合法；不是往场景中增加看不见的实体墙。
- assets/06-group-tree.png：从地图分组关系引入树、节点和两个子组；仅展开两层，B前半组仍需进一步切分，不是一棵完整合法WAD树。
- assets/07-split-edge.png：B北边256～512按384拆成首尾相接两段，解释记录拆分不意味着墙上开缝。
- assets/08-near-first-ray.png：同一视线先经过眼睛所在侧，再到另一侧；支持近侧优先，不声称所有墙按中心距离全排序。
- assets/09-move-order.png：观察点从x128到x448时的候选访问次序，尚未进行遮挡跳过；既有分割线不变。
- assets/10-solid-columns.png：实际模型画面叠加80/240边界及封闭横条；展示封闭的是继续望向后方的横向方向，不表示整列所有像素都涂成墙。
- assets/11-occlusion-record.png：空记录→近墙封闭80～239→后候选100～219被包含。为凸显因果，仅跟踪中间新增墙的记录，非声称完整引擎只保存这条区间。
- assets/12-back-bounding-box.png：将B后半全部包在x384～512、y0～192矩形中，说明用外框替许多墙做粗检查。
- assets/13-covered-box.png：后半框的100～220边界完全落入80～240封闭边界，支持整组拒绝。
- assets/14-partial-box.png：前半框40～280仍有两侧空隙，不能排除整组；框内是否真有墙可见仍待细查。
- assets/15-opening-column.png：原无新增实墙的模型中央列仍能看到远墙，下方示意分出上方结构/中间开口/下方结构；说明画过上墙和台阶不等于整列对后方封闭。
- assets/16-traversal-checklist.png：把同侧优先、远侧框检查、必要时深入三个动作收束成可重复流程。
- assets/17-skipped-branch.png：同一教学树上把后半组标灰，视觉对应“有足够遮挡证据才跳过”；不把示意变成引擎运行追踪截图。
- assets/18-real-map-root.png：实际MAP01的1272条原边、根分割线、实存两个子框与实际玩家1起点；由真实数据绘图，不是手绘猜测，不与官方截图硬配同房间。
- assets/19-real-node-record.png：真实WAD提取记录的中文可读排版，解释根线、子引用与记录数量；非软件界面截图。
- assets/21-sector-vs-subsector.png：同一真实文件206/705两个数量与两种职责，防止sector与subsector因英文相似被混淆。
- assets/20-real-seg-split.png：将同一side的真实linedef539与两个seg按坐标对齐；解释静态结构里的拆分确实存在，而不是用正反面数量冒充。

## 原创模型与数值约定

- 继续用A：x0～256、y0～192、地板0/天花128；B：x256～512、y0～192、地板24/天花96。眼睛(128,96,41)，朝+x，教学画布320×200、f160、水平视野90°，方形显示像素且无状态栏；导出图960×600。不是经典DOS显示比例参数复刻。
- 新增实墙占地x256～272、y32～160，封住连接处这一段的整个可望穿高度。原来两侧开口、A/B高度、外墙不变。B前半形状因此有凹凸，手选上层分割x256、x384只是分组示意，未生成完整节点树。
- 实墙面向A的平面x256，前方距离128，两端相对右偏−64/+64，因此u=80/240。B后半框最宽角范围来自x384，前方256、右偏±96，得到u100/220。B前半框从x256开始，得到40/280。
- 为记账，连续边界区间80～240教学离散为包含80、不包含240，即整数列80～239；另两段同理。源码实际角度表、边界量化与临界列遵循自身规则，本篇不保证逐列相同。
- 后半框内任一点x≥384、y在0～192，从眼睛到该点的射线在x256处横向y必在48～144内，严格落在新墙y32～160内。后半房间z24～96对应交点高度也在墙体完整高度范围内。因此本例不是仅靠外观猜“远处大概会被挡住”。
- 模型绘图使用原创逐像素射线/轴对齐面求交、最近表面选择、重复真实图块和固定面亮度。它不是经典Doom的绘图算法，没有据此推出Doom速度、遮挡表内容或最终精确像素。
- [blocked_columns.py](examples/blocked_columns.py)用普通集合表示教学列账本，测试闭区间80～239能否覆盖候选100～219与40～279；不复刻源码solidsegs的合并实现，不处理竖直开口、碰撞、光照或性能。
- 本篇两个教学Python脚本依[MIT许可](licenses/Example-Code-MIT.txt)。附带WAD仍是Freedoom BSD内容，并不因为与脚本同目录就改为MIT。

## 制作披露

AI用于辅助核对一手源码、组织原创解释、编写和实际运行数据读取/模型/教学账本程序、制作中文图解。没有复制其他教程成篇文字，没有虚构本人游玩、编辑器操作或历史硬件实测。图形、真实数据和实际游戏画面各自说明身份；本篇不需要人物或硬件介绍，因此没有为凑图数添加无关照片。
