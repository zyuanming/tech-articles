# 来源、图像身份与计算范围

## 本篇的核心问题

本篇承接双房间例子，解释怎样从玩家相对位置求屏幕位置。它不重写BSP空间组织或遮挡文章，也不展开纹理坐标的透视校正插值。比例推导和教学图为本次原创；公开源码用于核对经典引擎确实做了哪些工作，不把原创模型当成Doom历史内部实现。

制作过程中未运行Doom、Chocolate Doom或地图编辑器。文中的两张实际游戏截图来自Freedoom官方，其余带纹理房间图为原创计算结果。没有从官方截图猜测相机参数，也没有宣称与截图关卡对应。

## 一手事实与版本

技术参照为id Software公开的Linux Doom 1.10，固定仓库提交：[a77dfb96cb91780ca334d0d4cfd86957558007e0](https://github.com/id-Software/DOOM/tree/a77dfb96cb91780ca334d0d4cfd86957558007e0)。检索、字节核对日期：2026-10-13。

- [r_main.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_main.c)：R_SetupFrame设置观察位置、眼高和朝向；R_InitTextureMapping构建角度与横向屏幕位置的对应；R_ScaleFromGlobalAngle求绘制比例。支撑正文第10节概述，不支撑“源码逐点直接执行本篇两行浮点除法”的说法。
- [r_bsp.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_bsp.c)：R_AddLine处理墙段相对方向、视野范围和横向屏幕范围。图22是原创几何裁剪解释，不是该函数逐行执行轨迹。
- [r_segs.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_segs.c)：R_StoreWallRange等过程将墙段缩放、上下高度和绘制范围对应起来。
- [r_draw.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_draw.c)：R_DrawColumn使用dc_x、dc_yl、dc_yh等值绘制一段竖直列。本文不展开光照、调色板、纹理取样或溢出边界。
- [Freedoom官方截图页](https://freedoom.github.io/screenshots.html)：支撑实际截图使用Chocolate Doom、320×200画面经显示比例调整和清晰放大，以及截图适用Freedoom自身许可。1600×1200是交付原文件大小，不是原生渲染分辨率。
- [Freedoom项目说明](https://freedoom.github.io/about.html)：Freedoom是独立自由游戏内容，不是Doom原版美术。Doom源码许可不自动授权商业WAD图像。

## 真实素材与权利

### 两张官方实际游戏画面

- assets/01-freedoom-perspective.png：Freedoom Phase 1 / Chocolate Doom官方截图，[原文件p1_3.png](https://freedoom.github.io/img/screenshots/p1_3.png)。1600×1200原尺寸、原字节；63371字节，SHA-256为ca6505d1199ff09a645d0e6f7da641a5dbf3208ee4dc1ef5a93d483351619c29。职责：开场先看到平屏呈现的空间纵深，再提出投影问题。
- assets/20-freedoom-return.png：同一官方页另一张实际截图，[原文件p1_2.png](https://freedoom.github.io/img/screenshots/p1_2.png)。1600×1200原尺寸、原字节；复用首篇已核材料。职责：理解屏幕坐标后，再看真实墙边、地板和画面行列的关系。它不是本文双房间的实机运行结果。
- 官方截图页明确以Freedoom自身许可提供上述截图。Copyright © 2001-2024 Contributors to the Freedoom project。完整BSD-3-Clause版权、条件与免责声明保留在[Freedoom-COPYING.txt](licenses/Freedoom-COPYING.txt)，[贡献者清单](licenses/Freedoom-CREDITS.txt)一并保留。不暗示项目为文章背书。

### 真实图块与放大展示

取材固定Freedoom提交：[3ac019628d70b812ffb722f7f2365771b76a9d29](https://github.com/freedoom/freedoom/tree/3ac019628d70b812ffb722f7f2365771b76a9d29)。这只是取材快照，不伪称某正式发行版本。

- [assets/02-brick-original.png](assets/02-brick-original.png)：[patches/brick.png原文件](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/patches/brick.png)，128×128；用于模型墙面。是源图块，不宣称它自动等同引擎内部完整texture定义。
- [assets/05-floor-original.png](assets/05-floor-original.png)：[flats/floor0_1.png原文件](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/flats/floor0_1.png)，64×64；用于模型水平面，并作为像素概念的真实视觉锚点。
- assets/05-real-pixel-grid.png：左边把完整64×64地板图块作最近邻放大；右边取原图左上起点(24,24)、宽高8×8的区域，再最近邻放大。黄色框与右侧格线是新增辅助标记，没有补画原像素或生成更高清纹理。
- 两个原图均保留原字节；图块、放大衍生展示与模型中的素材部分依BSD-3-Clause使用。本文的CC BY 4.0不替换这些条款。放大图的原创排版和中文标记属于本篇原创部分。

## 逐图职责与身份

下列为原创程序制图或模型计算，不是实机截图、照片，也不是AI生成的假游戏画面。原创图表部分依本库CC BY 4.0；含Freedoom素材的画面同时保留其BSD-3-Clause要求。

- cover.png：独立封面，提示一个墙点与屏幕位置的关系；右下为同一教学模型，不作为额外机制图计数。
- assets/02a-room-start.png、02b-room-forward.png：同一房间向前移动64的前后计算结果；一起解释人靠近而房间未变，变化并非把所有物体统一放大。
- assets/03-two-viewpoints.png：把前后两幅画面对应到同一地图上的两个观察位置，避免把状态变化误认为换了关卡。
- assets/04-screen-address.png：屏幕横向u、纵向v与中心位置；大格是定位示意，不冒称320×200像素逐格展示。
- assets/06-relative-coordinates.png：从眼睛O到同一目标点P，分解出前方128、右侧64。P在台阶上沿中间，不是新增地图顶点或柱子。
- assets/07-virtual-window.png：先建立连线与虚拟画布交点的直觉。前方临时画成纸面上方，非玩家转身；图内世界连线与前方距离采用横偏/前进=0.5。
- assets/08-same-ratio.png：大、小同形三角形解释64/128=0.5/1，给除法一个可看见的前提。
- assets/09-horizontal-number.png：把横偏比例转为中心右侧80，得到u=240；0和320为连续画布边界，不是声称第320列像素存在。
- assets/10-height-relative.png：P高度24减眼高41得到−17，展示负号对应“低于眼睛”。此侧视图只解释高度差，不用于读出水平距离。
- assets/11-vertical-number.png：把世界向上与屏幕行号向下的差别对应到负号，得到v=121.25。
- assets/12-projected-point.png：将计算位置放回同一房间，黄色标记位于P的投影；图像放大展示，坐标仍按320×200。
- assets/13-near-far-rectangle.png：真实高度都为72的近开口与远墙投影高度分别为90、30；开口只有轮廓，不能涂成实体墙。
- assets/14-forward-depth.png：同一正对相机的平墙各处前方距离相同，指向两侧的斜距却较长。
- assets/15-wrong-distance.png：故意把绘制高度所用的前方距离误换为平面斜距，直上沿、下沿变弯。两图仍按正确横向位置采样，只对高度除数做受控错误，不能把它当完整错误相机算法或实际游戏缺陷。
- assets/17-turn-directions.png：东、北两种朝向下，“前”和“右”的世界方向改变；观察位置不变。
- assets/16-room-north.png：上述90°转头后的实际模型计算结果，把方向变化落实到能看见的墙面。
- assets/19-fov-fans.png：同一位置f=160与320的视野示意；同一前方距离处，半宽比为1和0.5。较大f对应较窄视野，并非移动眼睛。
- assets/18-room-narrow.png：f翻倍、位置朝向不变后的实际模型结果；与开头移动视图共同区别两种变大。
- assets/21-behind-eye.png：前方d>0、眼睛所在平面d=0、身后d<0，补齐公式使用前提。
- assets/22-view-clipping.png：同一A房间北侧边，只有x=224～256进入朝东90°水平视野；橙色是应保留的部分。图内延长线只是视野边界辅助，不添加新房间。

## 教学计算参数与边界

- 平面坐标：x向右、y向上、z为竖直高度。A：x=0～256、y=0～192，地板0、天花128；B：x=256～512、y=0～192，地板24、天花96。
- 默认眼睛O=(128,96,41)，朝+x，不俯仰、不滚转。目标P=(256,32,24)；前方距离d=128，玩家右侧偏移s=64，相对高度q=−17。
- 教学画布320×200，中心(160,100)，f=160，水平视野90°；实际模型导出960×600，相应尺寸与f等比例放大3倍。按显示像素为方形处理，不含状态栏，不复刻历史4:3显示校正。
- 投影：u=160+160s/d，v=100−160q/d，要求d>0。P得到(240,121.25)；这是连续几何坐标，不是对像素覆盖规则的规定。
- 近开口屏幕矩形：(40,31.25)～(280,121.25)。远墙：(120,77.083333…)～(200,107.083333…)。高度90与30对应同一实际高度72、前方距离128与384。
- 前进视图仅将O改为(192,96,41)。转头视图仅朝+y。窄视野视图仅将f改为320。所有图均沿用同一几何和真实素材；没有更换房间来制造效果。
- 计算画面采用原创逐像素射线与轴对齐面求交，取最近表面，再按重复图块和固定面亮度着色。这是用于解释几何的绘图办法；经典Doom不是这样逐像素求交生成画面。未模拟其完整纹理对齐、调色板、光照、精灵、整数精度或性能。
- 图15反例的斜距为sqrt(d²+s²)，用于单独演示高度缩放错误；正文的“鱼眼式”仅描述该形变，不代表真实镜头分类。
- [project_point.py](examples/project_point.py)是独立原创Python标准库例子，使用Fraction准确分数重算位置，采用[MIT许可](licenses/Example-Code-MIT.txt)。它检查本篇数值、等比例射线方向和d≤0拒绝；不负责墙段裁剪、遮挡、碰撞、像素覆盖或帧率。

## 制作披露

本篇由AI辅助检索一手代码、组织原创解释、编写和运行本篇模型及算例、制作中文教学图。没有复制其他教程成篇内容；没有虚构实机游戏操作、原版硬件测试或编辑器操作经历。原始截图、真实图块、原创几何图、原创计算画面在正文就近说明身份。与投影主题无关的设备或人物照片不为增加图片数量加入。
