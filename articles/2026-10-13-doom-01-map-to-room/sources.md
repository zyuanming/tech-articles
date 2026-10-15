# 来源、图像身份与复用范围

## 本文解决什么

本文为独立 Doom 入门系列第一篇，专门解释经典地图的平面边界、sector 高度与两侧开口。它不重写已有两篇 BSP 文章，也不把较晚移植版的全部功能等同于 1993 年原版。

技术核对对象为 id Software 公开的 Linux Doom 1.10。本文没有在制作环境中运行 Doom、Chocolate Doom 或编辑器；真实游戏截图由 Freedoom 官方提供，编辑器面板来自项目文档。文中的透视图由本次原创教学模型计算，不能据此推断经典 Doom 的内部绘制流程或性能。

## 一手事实来源与支撑边界

- id Software：[doomdata.h](https://github.com/id-Software/DOOM/blob/master/linuxdoom-1.10/doomdata.h)。支撑 WAD 地图分块、x/y 顶点、边端点与边侧索引、边侧纹理与 sector 关联、sector 的一对高度及其他属性。它不是一份包含所有特殊视觉效果的教程。
- Ultimate Doom Builder：[terminology.html](https://github.com/UltimateDoomBuilder/UltimateDoomBuilder/blob/bfb9653951445c7a4e4c46b1600e14358e901e44/Help/terminology.html)。支撑边的右侧/正面约定、sector 形状由边及边侧关系确定、一个 sector 可包含多个封闭区域、常见地图元素术语。
- id Software：[r_segs.c](https://github.com/id-Software/DOOM/blob/master/linuxdoom-1.10/r_segs.c)。支撑从相邻区域高度判断上、下墙段以及墙纹理绘制分工。本文的普通双矩形例子没有纳入天空特殊处理、缺纹理技巧或其他漏洞效果。
- id Software：[P_LineOpening，p_maputl.c](https://github.com/id-Software/DOOM/blob/master/linuxdoom-1.10/p_maputl.c)。支撑开口顶取较低天花板、底取较高地板。源码直接保存 top−bottom；教程展示的 max(0, top−bottom) 是原创计算器的截零表示，不冒称源码原式。
- id Software：[P_TryMove，p_map.c](https://github.com/id-Software/DOOM/blob/master/linuxdoom-1.10/p_map.c)。支撑几何开口不等于完整可通行判断，仍有物体高度、台阶及其他碰撞条件。
- id Software：[r_data.c](https://github.com/id-Software/DOOM/blob/master/linuxdoom-1.10/r_data.c)。支撑墙 texture 与 patch 图块的区别。本篇展示的 brick 是 Freedoom 源素材图块，不宣称它自动等于引擎内部完整 texture 定义。
- [1997 年源码发布说明](https://github.com/id-Software/DOOM/blob/master/README.TXT)。John Carmack 署名 1997-12-23，提及斜坡等可增补功能。历史原文中保留的旧许可措辞，不应替换仓库目前标示的 GPL 2.0；该代码许可也不授权 Doom 商业 WAD 美术。
- Freedoom：[项目说明](https://github.com/freedoom/freedoom)、[关于素材与原版区别](https://freedoom.github.io/about.html)、[官方截图页](https://freedoom.github.io/screenshots.html)。支撑 Freedoom 是独立自由内容项目而非 Doom 原版美术；截图页明确说明所用引擎、显示比例和截图复用许可。

## 真实数据固定版本

Freedoom 取材固定提交：[3ac019628d70b812ffb722f7f2365771b76a9d29](https://github.com/freedoom/freedoom/tree/3ac019628d70b812ffb722f7f2365771b76a9d29)。检索日期为 2026-10-13；这是本次源码树快照，不伪称特定正式发行版。

- [MAP01 原文件](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/levels/map01.wad)：124013 字节；SHA-256 d9da5d7f8d97d6555182a04326f306dde6fd40da1186a6fec18143c7ccddd20d。
- 图11使用 LINEDEFS，17808 字节 ÷ 每条14字节 = 1272条；SECTORS，5356字节 ÷ 每条26字节 = 206条。
- 图12使用从0编号的 sector 0，floorheight=0、ceilingheight=128。从 SIDEDEFS 的 sector 索引反查相应 LINEDEFS，而不是凭图像猜出房间形状。
- 本文保留[同字节 MAP01 数据](examples/freedoom-map01.wad)与[只读检查脚本](examples/inspect-map.py)。运行检查脚本使用 Python 标准库，无网络请求；它读取附带 WAD，不运行关卡或其中的任何代码。
- 本例从本地 MAP01 读取的边界、开场官方截图、文档编辑器面板来自不同对象，正文已就近区别，不声称它们描述同一地点。

## 各图的教学职责、出处与权利

### 真实游戏画面

- assets/01-freedoom-gameplay.png：官方 Freedoom Phase 1 / Chocolate Doom 截图；用于先识别真实游戏中的地板、墙面与远近空间。来源页：[截图页](https://freedoom.github.io/screenshots.html)；[原文件](https://freedoom.github.io/img/screenshots/p1_2.png)。1600×1200 原文件原尺寸保留，没有裁切或重新生成。官方说明渲染基于320×200，并做显示比例和像素清晰度调整；本文不把1600×1200称为原生渲染分辨率。
- assets/17-freedoom-creature-scene.png：同一官方截图页的另一张 Phase 1 / Chocolate Doom 实际运行画面；[原文件](https://freedoom.github.io/img/screenshots/p1_4.png)，1600×1200原字节。置于精灵解释附近，把独立对象图像与游戏里的对象对应起来；不声称该画面恰用13c的那一帧，也不声称属于本文原创双房间。
- 截图页明确将这些截图置于 Freedoom 自身许可下。因此按 BSD-3-Clause 使用。Copyright © 2001-2024 Contributors to the Freedoom project；完整条款保存在 [Freedoom-COPYING.txt](licenses/Freedoom-COPYING.txt)，贡献者清单保存为 [Freedoom-CREDITS.txt](licenses/Freedoom-CREDITS.txt)。不暗示项目为文章背书。

### 真实编辑器界面

- assets/06-editor-sector-panel.jpg：Ultimate Doom Builder 项目文档的 sector 信息面板原图，230×107；用于对应 Ceiling、Floor、Height 的实际字段。来源：[原项目文件](https://github.com/UltimateDoomBuilder/UltimateDoomBuilder/blob/bfb9653951445c7a4e4c46b1600e14358e901e44/Help/gzdb/features/sectors_mode/sector_info.jpg)；[原文件下载](https://raw.githubusercontent.com/UltimateDoomBuilder/UltimateDoomBuilder/bfb9653951445c7a4e4c46b1600e14358e901e44/Help/gzdb/features/sectors_mode/sector_info.jpg)。保留原字节，正文另作大字中文释读。
- 这是项目自身文档中的软件界面图，选取的这张面板没有 Doom 商业贴图或其他游戏美术。项目根目录的 [GPL v3 许可](https://github.com/UltimateDoomBuilder/UltimateDoomBuilder/blob/bfb9653951445c7a4e4c46b1600e14358e901e44/LICENSE.txt)随原图保存于 [UltimateDoomBuilder-GPL-3.0.txt](licenses/UltimateDoomBuilder-GPL-3.0.txt)，原始图片与源位置均保留。该处理仅适用于这张无第三方游戏美术的项目界面图，不把整个仓库中的所有截图自动视为商业 Doom 素材再分发授权。
- 界面所属具体程序发布版本在该原图内没有标明，正文只称项目文档示例，不虚构运行版本或本次操作经历。它显示的 sector 0 与本文实际 Freedoom MAP01 sector 0、原创 A 房间分别属于不同对象。

### 真实关卡与图像文件

- assets/11-real-map01-plan.png：从实际 Freedoom MAP01 的 LINEDEFS/顶点原数据绘出的整关平面；职责是让读者看见真实关卡的规模及边界分布。
- assets/12-real-sector0.png：从同一文件的真实 sector0 关联关系提取边界与高度；职责是把刚学的“属性记录与形状分工”落到真实数据。这两张是数据可视化，不是编辑器截图。原地图数据依 BSD-3-Clause，本文新增的中文标注依 CC BY 4.0；两者均需保留相应权利。
- assets/13a-brick-original.png：[Freedoom 原墙用图块 brick.png](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/patches/brick.png)。保留原尺寸原字节。
- assets/13b-floor-original.png：[Freedoom 原地板图块 floor0_1.png](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/flats/floor0_1.png)。保留原尺寸原字节。
- assets/13c-sprite-original.png：[Freedoom 原精灵帧 trooa1.png](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/sprites/trooa1.png)。保留原尺寸原字节，不声称它是 Doom 原版怪物。
- assets/13-real-assets.png：将以上三个真实素材作最近邻放大排列，帮助辨认纹理图块和透明精灵的区别；没有生成、补画或润饰游戏像素。组合只是一个素材图组，不把其中小图当成额外正文图数量来宣传。
- assets/14-model-textured.png：将同一教学几何模型改用上述 Freedoom 图块着色，职责是对比“换外观，几何不变”。它是原创模型计算结果，不是实际引擎运行截图；图中的第三方纹理仍遵循 BSD-3-Clause。
- 上述 Freedoom 数据、图像、衍生展示均随附完整 BSD-3-Clause 版权/条件/免责声明与贡献者清单。本文的统一正文授权不覆盖或替代这些条款。

### 原创教学图

以下图像由本次程序绘制，非 AI 生成的游戏截图、历史照片或实拍。原创部分依仓库的 CC BY 4.0 使用。

- cover.png：独立封面，提示平面到房间的主题；不计正文概念说明图。
- assets/02-two-room-plan.png：贯穿小例的俯视布局与观察方向。
- assets/03-vertices-and-lines.png：x/y 地址、六个顶点及共享边。
- assets/04-linedef-sides.png：有向边两侧与区域关联；说明右侧/正面是数据方向约定。
- assets/05-height-intervals.png：A、B各一对高度与净高，初步建立竖直空气范围直觉。
- assets/07-room-cutaway.png：同一坐标/高度的立体剖开形状；移走前侧面与顶面以看清内部。
- assets/08a-model-level.png、08b-model-step.png、08c-model-opening.png：同一相机下，仅依次改变B地板和天花板的三步教学计算图；合起来承担一次机制分步说明，不是三个无关样例，也不是实机连续截图。
- assets/09-shared-opening-section.png：同一A、B的侧剖面，把上墙/开口/下墙对应到高度数字。
- assets/10-overlap-formula.png：把两个竖直区间重叠，解释为何底取max、顶取min。
- assets/15-room-over-room.png：固定同一x、y，比较一段与两段分离空气，解释普通sector表示的边界。
- assets/16-visible-vs-walkable.png：几何开口、图像和阻挡规则的职责边界。栏杆画面是原创示意，不是实际引擎测试。

## 教学几何与图像计算的范围

- 平面：A覆盖x=0～256、y=0～192；B覆盖x=256～512、y=0～192。x向右，y向上，z为竖直高度。
- 最终高度：A地板0、天花128；B地板24、天花96。共享边x=256。
- 三步计算图相机固定在(128,96,41)，看向+x，水平视野90°；竖直画面居中，不滚转、不俯仰。
- 图像计算采用本次独立的针孔相机与逐像素射线/轴对齐平面求交，取最近可见表面；它只用来让几何变化准确对应到画面。经典 Doom 不是用这段教学绘图程序渲染；本文也没有声称逐像素求交是其历史方案。
- 纯色步骤图用颜色区分区域；纹理图用重复图块加固定面亮度，未仿制 Doom 完整光照、调色板、纹理列、平面跨度或精灵裁剪。
- [opening.py](examples/opening.py)是独立原创教学脚本，采用[MIT许可](licenses/Example-Code-MIT.txt)。它验证区间开口，不计算玩家通行、碰撞或帧率。示例包括等高、抬地板/降天花、闭合、无重叠和负地板高度。

## 为什么没有直接打包原版 Doom 的关卡美术

[原版E1M1地图来源页](https://doomwiki.org/wiki/File:E1M1_map.png)将其列为受版权保护地图并说明该网站自身的 fair-use 理由；这不是给其他出版物的通用开放许可。因此本文只直达链接该图，不复制到本公开素材包，也不把Doom源码GPL外推到原WAD内容。

本文没有把未知许可的工具截图、原版游戏贴图或照片生成一张“差不多”的假实图来代替。与首篇机制无关的人物照、硬件照不为凑数加入；后续谈具体历史人物或设备时再就近提供适当真实视觉。

## 制作披露

本文使用 AI 辅助检索一手资料、组织解释、编写原创计算和制图程序，并由程序实际读取上述合法WAD和运行小算例。没有复制其他教程的成篇文字；没有声称亲手玩过本文截图关卡、操作过截图中的编辑器或测过历史硬件。所有真实来源材料与原创示意/计算结果在正文和本页分别标示。
