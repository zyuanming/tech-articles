# 图像来源、逐图职责与计算约定

## 本篇解决的问题

本篇围绕“一个屏幕像素到哪张素材的哪一格取颜色”，承接同一双房间，解释墙/地板纹理、最近邻取样、重复、透明角色图及朝向选择。它不重写既有透视校正插值推导，也不是完整Doom纹理系统或现代过滤方法教程。

真实游戏截图来自官方；素材来自固定版本；本篇房间图、取样对照和方向图由原创程序生成。制作时没有运行Doom、Chocolate Doom或地图编辑器，没有声称亲测游戏抖动、帧率或GPU行为。

## 一手代码与支撑范围

id Software固定代码：[a77dfb96cb91780ca334d0d4cfd86957558007e0 / Linux Doom 1.10](https://github.com/id-Software/DOOM/tree/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10)，核对日期2026-10-13。原文件与固定官方树的Git blob核过字节，仅阅读，没有安装或执行该项目。

- [r_data.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_data.c)：完整墙纹理与patch图块组合、列资料，以及精灵宽度/偏移等装入。本文brick.png是开发源图块，模型直接重复使用；不自动等同引擎完整texture定义。
- [r_draw.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_draw.c)：R_DrawColumn按竖列从源列取颜色，R_DrawSpan按水平跨度更新两方向地址；两者通过colormap转换颜色编号。本文没有把代码里的某个掩码推广为所有素材尺寸的通用规则。
- [r_plane.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_plane.c)：平面绘制的距离、取样起点和行内步进。正文只说明墙列/水平地面跨度的分工，不要求读者先理解全部定点运算。
- [r_things.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_things.c)：R_InitSpriteDefs、R_InstallSpriteLump解析图像条目中的帧/朝向编码及翻转标记；R_ProjectSprite按视点与对象方向挑选图像；R_DrawMaskedColumn按有内容的列段绘制并跳过空白。开发PNG文件名沿用命名约定，经典代码读取的是打包图像条目，不是.png文件。
- [Freedoom官方截图页](https://freedoom.github.io/screenshots.html)：本文实际截图来自Phase 1 / Chocolate Doom；320×200渲染输出经过显示比例与像素清晰度调整为1600×1200；截图按Freedoom自身许可提供。

## 固定素材、原文件与权利

所有Freedoom开发素材取自固定提交：[3ac019628d70b812ffb722f7f2365771b76a9d29](https://github.com/freedoom/freedoom/tree/3ac019628d70b812ffb722f7f2365771b76a9d29)。它表示取材快照，不伪称某个正式发行版本。

Copyright © 2001-2024 Contributors to the Freedoom project。完整BSD-3-Clause版权、条件、免责声明保存在[Freedoom-COPYING.txt](licenses/Freedoom-COPYING.txt)，[贡献者清单](licenses/Freedoom-CREDITS.txt)随附。不暗示项目为文章背书；本文正文CC BY 4.0不替换原素材许可。

### 官方实际画面

- assets/01-real-game.png：[官方原文件p1_4.png](https://freedoom.github.io/img/screenshots/p1_4.png)，1600×1200原尺寸、原字节，复用首篇已核材料。职责是把墙面、地板与角色放在真实游戏背景里。截图不能证明本文模型用了同一个关卡、角色帧、相机或内部渲染状态。
- 截图页明确将这些截图以Freedoom自身许可提供，因此按BSD-3-Clause保留完整条款使用。没有因为Doom源码开放而复制商业原版游戏美术。

### 墙与地板真实原图

- [assets/brick-original.png](assets/brick-original.png)：[patches/brick.png原文件](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/patches/brick.png)，128×128，保留原字节。
- [assets/floor-original.png](assets/floor-original.png)：[flats/floor0_1.png原文件](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/flats/floor0_1.png)，64×64，保留原字节。
- 这两张图与前篇已核文件相同。砖图是带调色板的PNG；实际坐标(112,12)保存颜色索引159，该PNG调色板第159项为RGB(55,63,39)。这个159只描述源PNG记录，不冒称某一Doom运行帧或编译后的COLORMAP索引。

### 真实角色原图与朝向复用

以下五个PNG均从固定官方树取回，并核对Git blob字节；同属TROO的A帧，保留原尺寸原字节。原文件的透明索引为0，解码后透明度只有0与255，本例不是半透明混色。

- [trooa1.png](assets/trooa1.png)，48×60，[原文件](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/sprites/trooa1.png)：第1朝向。
- [trooa2a8.png](assets/trooa2a8.png)，44×61，[原文件](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/sprites/trooa2a8.png)：第2按原方向，第8水平翻转。
- [trooa3a7.png](assets/trooa3a7.png)，46×60，[原文件](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/sprites/trooa3a7.png)：第3按原方向，第7水平翻转。
- [trooa4a6.png](assets/trooa4a6.png)，46×62，[原文件](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/sprites/trooa4a6.png)：第4按原方向，第6水平翻转。
- [trooa5.png](assets/trooa5.png)，45×59，[原文件](https://raw.githubusercontent.com/freedoom/freedoom/3ac019628d70b812ffb722f7f2365771b76a9d29/sprites/trooa5.png)：第5朝向。

棋盘背景是新增辅助，掩码是从真实透明信息可视化；镜像图是明确标注的原像素水平翻转，不是另一张独立源图，不是新绘角色。模型中的角色使用真实第1朝向PNG，尺寸/底部定位为教学约定，不是复刻游戏对象的patch偏移与碰撞体。

## 逐图职责与身份

纯示意、新增排版与原创计算图部分依本库CC BY 4.0；含Freedoom图块/角色的衍生展示仍保留BSD-3-Clause要求。以下均不是AI生成的假游戏截图或实拍。

- cover.png：独立封面，用同一带角色教学模型提示“图案如何进入像素”，不计正文机制图。
- assets/02-model-base-colors.png、03-model-textured.png：同一房间与视点，只改变表面取色方式，解释几何与外观是两份数据。纯色图每面用底色，纹理图按明确方向取真实图块；不假称仅更换原版Doom某设置。
- assets/04-real-surface-images.png：128×128砖图与64×64地板原图的最近邻放大，提供真实图案视觉锚点。
- assets/05-source-address.png：原砖图框选(104,4)到(120,20)的16×16区域，右边放大并标其中(112,12)一格；原图坐标与局部地址对应。
- assets/06-one-screen-pixel.png：同一房间中标画布第180列、第136行位置；沿视线寻找表面的模型解释，不声称经典Doom每像素都做同种求交。
- assets/07-address-chain.png：画布格心→墙点→素材位置→源格的分步地址转换，避免从“贴图”一词直接跳到结果。
- assets/08-exact-color.png：真实源格RGB(55,63,39)及三个分量；模型先原样用色，数值与画面可核对。
- assets/09-repeating-image.png：真实砖图横向重复两次，标0/128/256边界，解释140回到第12列。没有补画新的砖纹。
- assets/11-floor-top-view.png：同一64×64真实图块铺4列、3行形成256×192平面；网格和箭头为新增辅助。
- assets/10-B-floor-grid.png：眼睛进入同一B房间后，真实地板图块与64单位网格的投影。展示近/远缩放，不把图案当屏幕平贴。
- assets/12-nearest-enlargement.png：从上述16×16局部再取内部(4,4)到(12,12)，即原图(108,8)到(116,16)的8×8，作两种最近邻放大；解释一源格可供多屏幕格使用。
- assets/13-minification.png：同一真实16×16区域缩为4×4，取样坐标组由2/6/10/14变成3/7/11/15；16输出格有10格实际变色。是受控取样对照，不是引擎帧率或闪烁实测。
- assets/14-column-and-span.png：同一B模型中，黄色线落在后墙的一段竖列，青线落在地板横向跨度；源码分工示意，不是运行追踪截图。
- assets/21-real-palette-entry.png：原PNG实际(112,12)格→索引159→该PNG调色板RGB(55,63,39)，说明编号与RGB不是同一件事。
- assets/15-real-sprite-mask.png：真实48×60角色图及其0/255透明轮廓；棋盘、黑白掩码是辅助视图，不是游戏本身画出的背景。
- assets/16-model-with-sprite.png：把真实角色图按教学底部/大小约定放进同一B，透明处不覆盖原画面。原创计算，非Doom截图。
- assets/17-transparent-or-rectangle.png：同一模型局部，左侧故意将透明索引0的底色也画上，右侧正确跳过。蓝绿色来自原PNG该编号的RGB，不是假造错误效果或游戏缺陷。
- assets/18-real-sprite-views.png：五个真实源PNG与三次按命名标记的水平翻转组成八朝向；它们共同承担一次方向对照，不能当八张独立采集图片计数。A姿态固定，不冒充时间动画。
- assets/19-view-selection.png：角色固定朝西，观察者在西/南/东分别用1/3/5朝向；说明选择依赖双方相对方向，而不只取决于玩家转头。
- assets/20-mirrored-view.png：实际trooa3a7图与水平镜像，解释一源图服务两方向的记录方式。两张对照不冒称两张不同原文件。
- assets/22-color-pipeline.png：表面/对象、源图位置、颜色与透明/明暗、最终画布四个环节收束，不代替前文真实材料和计算结果。

## 模型与数值约定

- A：x0～256、y0～192、地板0/天花128；B：x256～512、y0～192、地板24/天花96。恢复无第三篇新增挡墙的状态，未改变早期几何。
- 默认眼睛(128,96,41)，朝+x，不俯仰、不滚转；原生教学画布320×200、f160，水平视野90°、方形显示像素、无状态栏。按最近邻3倍导出960×600，不复刻DOS的4:3显示比例。
- 第180列136行取中心(180.5,136.5)。在x256面上落点(256,79.6,11.8)；共享下墙纹理从y192沿y减小方向作列、从本段顶z24向下作行，一地图单位对一源格。地址(112.4,12.2)，按最近格心/包含格约定选择(112,12)。不对所有经典墙段的对齐、pegging或偏移作同样保证。
- 其他x常数墙同样以192−y为纹理列、本面顶减z为行；y常数墙从该面起点x增加作列、顶减z作行。水平面列为x、行为192−y，取格后各自对64重复。墙图块对128重复。
- 为清楚核数，本篇没有模型亮度乘数，选中格的最终RGB仍为(55,63,39)。这不是否认经典引擎的亮度表，也不是说明RGB数值等同物理发光强度。
- 地板视点只改为(288,96,65)，仍朝+x；B地板24，离地41。网格标实际图块的64单位边界，是新增叠色辅助，不是源图自带亮线。
- 图像计算仍为本次原创逐像素射线/轴对齐面求交、最近表面选择。经典Doom不是用此程序绘图；正文另按一手源码说明墙列与平面跨度。
- 角色位置(352,96,24)，本模型按原48×60像素对应48×60地图单位，矩形底边中点定位，平面与画布平行；对每个像素比较深度，只有角色更近且源格不透明才覆盖。没有使用原引擎的角色碰撞/patch锚点参数。
- 方向示意按R_ProjectSprite的32位角度表达式核了四个正方向：对象朝西，观察者西/南/东/北对应图1/3/5/7。无需假称运行过该程序才能核对表达式；一般角度量化、共线边界不在本篇展开。
- [wall_sample.py](examples/wall_sample.py)为原创Python标准库/Fraction地址算例，依[MIT许可](licenses/Example-Code-MIT.txt)。只算本例下墙地址，不读取PNG、不联网、不绘制完整画面，不是原Doom实现。第三方素材不因此改成MIT。

## 制作披露

AI辅助核对公开一手源码、组织原创解释、编写并运行模型/数值检查、制作中文教学图。真实图片保留原文件与许可；放大、裁取、透明可视化和镜像均说明方法，没有补画成伪实图。没有安装运行外部游戏项目，没有虚构游戏操作、截图相机状态或设备性能。浏览器和发布状态不属于本文内容声明。
