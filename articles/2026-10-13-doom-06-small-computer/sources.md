# 来源、材料权利与计算边界

## 范围与材料身份

这是六篇Doom入门系列的最后一篇，核心是重复工作的安排：列内步进、定点表示、预计算查表、紧凑颜色表示、软件资源缓存与低细节取舍。正文与中文教学图为AI辅助原创说明。没有运行Doom、测量历史硬件、使用游戏地图编辑器或录制设置切换；没有把Python图像处理耗时当成原版性能。

正文、原创说明和纯教学示意采用CC BY 4.0。第三方截图、图块、照片、地图及它们的衍生画面保留各自的权利；不能因正文许可而忽略素材条件。没有使用商业Doom的WAD美术，没有把开源引擎许可外推到游戏资产。现代主板原照、官方游戏截图、真实数据可视化、原创模型处理分别标明身份；没有AI生成的伪设备照片或假游戏截图。

## 1. 固定版本的一手机制依据

统一代码基准为[id Software / DOOM，a77dfb96cb91780ca334d0d4cfd86957558007e0，linuxdoom-1.10](https://github.com/id-Software/DOOM/tree/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10)。作者取得以下12份官方文件，复算其Git blob SHA与SHA-256，不执行原项目。该公开Linux代码不被说成1993年DOS每条指令的等价证据。

- [r_draw.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_draw.c)：R_DrawColumn取素材、经颜色映射写屏幕，frac按fracstep递增，dest按SCREENWIDTH递增；不是每格重做全部几何。R_DrawColumnLow把同一结果写到相邻两列。本文未声称去掉全部乘除，也未按操作类别臆测性能倍数。
- [r_segs.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_segs.c)：列间墙尺度与顶底边界也采用增量安排。本文不展开这条额外推导，只用它确认“重复工作的组织”不限于一种变量。
- [m_fixed.h](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/m_fixed.h)：FRACBITS为16、FRACUNIT为1左移16位，fixed_t为int。本文按该实现所用32位有符号整数解释16.16，不声称所有C平台的int都由语言保证为32位。
- [m_fixed.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/m_fixed.c)：FixedMul用long long保存中间乘积再右移16位。FixedDiv先作范围保护；FixedDiv2中整数除法路径位于未启用的条件编译分支，实际启用路径使用double后转回fixed_t。正文明确保留这一反例，不宣传“完全没有浮点”。
- [tables.h](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/tables.h)、[tables.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/tables.c)：FINEANGLES为8192，finesine有10240项；图13来自该文件数值，不是自行算一份近似值后称作原表。
- [r_main.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_main.c)：finecosine指向finesine往后FINEANGLES/4的位置。文件中保留的表生成式含i+0.5，说明半格偏移；该生成段被条件编译禁用，不是说游戏每帧仍执行它。显示细节设置也会影响viewwidth/detailshift；本文图19仅仿照双列复用思想，非完整原版设置模拟。
- [w_wad.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/w_wad.c#L471-L501)：W_CacheLumpNum在副本不存在时分配并读取，已有副本时更新标签后复用。调用者决定标签，不能由WAD目录推知每个块的生命周期。
- [z_zone.h](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/z_zone.h)、[z_zone.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/z_zone.c)：PU_PURGELEVEL为100、PU_CACHE为101；分配器寻找空间时可清除可回收块，释放会清空其持有者指针。不是每次使用就删除、不是全部常驻，也不是严格LRU或CPU硬件缓存。
- [doomdef.h](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/doomdef.h)、[d_main.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/d_main.c)：320×200尺寸常量、TICRATE=35和D_DoomLoop中的更新/显示路径。35是逻辑时间安排，不构成每台机器固定达到35帧的实测。图21上下点数是工作类别示意，不是逐秒时序记录。

本文只给出少量必要标识、定义与数值摘录，没有分发引擎源码或整张数值表。公式与容量算例为原创教学计算；机制解释不替代具体平台性能测量。

## 2. 真实Freedoom材料与许可

材料版本为[Freedoom，3ac019628d70b812ffb722f7f2365771b76a9d29](https://github.com/freedoom/freedoom/tree/3ac019628d70b812ffb722f7f2365771b76a9d29)。这些材料采用BSD-3-Clause，版权归Freedoom contributors，完整保留[版权与许可](licenses/Freedoom-COPYING.txt)及[贡献者名单](licenses/Freedoom-CREDITS.txt)。没有暗示项目为本文背书。

- [官方截图页](https://freedoom.github.io/screenshots.html)明确其截图采用与Freedoom相同的BSD许可，说明来自Chocolate Doom的320×200画面经清晰放大和显示比例调整成为1600×1200。[p1_3原图](https://freedoom.github.io/img/screenshots/p1_3.png)作为图01保留原字节，63371字节，SHA-256为`ca6505d1199ff09a645d0e6f7da641a5dbf3208ee4dc1ef5a93d483351619c29`。没有把它的房间说成本文双房间或所解析MAP01的某个已定位房间。
- [patches/brick.png](https://github.com/freedoom/freedoom/blob/3ac019628d70b812ffb722f7f2365771b76a9d29/patches/brick.png)：128×128索引PNG，SHA-256为`b035a3c174da129174140698de5b07116dec90e916125e07cdf8dc34da9adda5`；原文件另存[brick-original.png](assets/brick-original.png)。本篇裁取、放大和读取的是这一实际源文件。
- [flats/floor0_1.png](https://github.com/freedoom/freedoom/blob/3ac019628d70b812ffb722f7f2365771b76a9d29/flats/floor0_1.png)：64×64，SHA-256为`4717123789da26475b5ee17d9887cd337cf1d60de550e2c5f27f0bc35eb53f44`。本篇沿用的第四篇双房间画面使用它作为水平面材料，没有新增一个假素材来源。
- [levels/map01.wad](https://github.com/freedoom/freedoom/blob/3ac019628d70b812ffb722f7f2365771b76a9d29/levels/map01.wad)：124013字节，SHA-256为`d9da5d7f8d97d6555182a04326f306dde6fd40da1186a6fec18143c7ccddd20d`；保留[同字节原文件](examples/freedoom-map01.wad)。只解析数据，不运行关卡。实际目录有11个条目，包括零长度的MAP01标记；图17节选7个有内容的地图块。

这些材料复用系列此前已核验的官方文件，本篇再次校验原字节。图块放大与房间结果仍保留Freedoom许可条件。源PNG的颜色编号只按该PNG自带颜色表解释，不能直接当作打包WAD或最终屏幕的同编号颜色。

## 3. 现代主板实物照片

图02来自[Raspberry Pi Documentation固定仓库版本](https://github.com/raspberrypi/documentation/tree/208ec7debc5b30b3ce6a1426eff453f2359f2165)：[rpi4b.jpg原件](https://github.com/raspberrypi/documentation/blob/208ec7debc5b30b3ce6a1426eff453f2359f2165/documentation/asciidoc/computers/sbcs/images/rpi4b.jpg)。署名来源为Raspberry Pi Documentation；未声称查到个人摄影师或拍摄日期。图为Raspberry Pi 4 Model B，硬件身份可与[官方产品说明](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)对应；这里只展示现代板上处理器与内存的物理区分，不作购买推荐、不作为Doom历史电脑或性能证据。

原图1920×1344，214590字节；Git blob SHA为`673b63bdd7850998fc0efc5e7e8755e42ae4ae98`，SHA-256为`b0d9e7752fee94e84c5d8ae5496f44e88617028da749cdbcffb331e4945d7b42`。公开图02完整保留原字节，没有裁剪、标注或画面生成。

该文档仓库的[LICENSE.md](https://github.com/raspberrypi/documentation/blob/208ec7debc5b30b3ce6a1426eff453f2359f2165/LICENSE.md)给出[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)链接与完整Attribution-ShareAlike条款。其开头链接文字漏写ShareAlike，但目标与条款都明确含相同方式共享；本文依照完整CC BY-SA 4.0条件，而非按较宽松的纯署名许可处理。已保留[完整原许可文件](licenses/Raspberry-Pi-Documentation-CC-BY-SA-4.0.md)。此照片自身不改标为本文原创CC BY 4.0，亦不因嵌入文章而失去原许可。

## 4. 逐图职责、输入与变换

正文共22幅图，包含各自面板而不把面板当成额外图源。除01与02的原文件外，其他图为原创排版、真实数据可视化或明确的教学结果；中文说明不能被误认成原游戏界面。

- 01-real-game.png：官方实际游戏画面；把像素工作与真实墙、地面、物件连接。身份与来源见第2节。
- 02-computer-photo.jpg：现代主板真实原照；给CPU和内存名称配实物参照。身份、原字节与许可见第3节。
- 03-work.png：更新、可见性、生成颜色的职责示意；没有虚构百分比、计时条或逐行执行顺序。
- 04-room-column.png：复用第四篇同一原创双房间结果，黄色标出一小列的位置。该图只定位对象，不将后续手算地址冒称该列原版内部状态。
- 05-real-column.png：真实128×128砖图放大到512×512；右侧裁取列108..115、行8..19的8×12区域，最近邻放大32倍，框出列112、行12..15。没有生成纹理细节。
- 06-sample-addresses.png：8个手算地址12.25至15.75，逐格对应向下取整后的源行12、12、13、13、14、14、15、15；色块读取真实PNG第112列。
- 07-increment.png：从起点重复算与按步长接着算的表达式对照。说明结果相同，未称测出加法比乘法快几倍。
- 08-fixed-unit.png：元与分连接细单位的直觉；65536倍只是另一把尺，不能混算元与纹理坐标单位。
- 09-fixed-values.png：三个数转换到固定小份的结果，配少量原代码定义。16.16的表示依该32位实现，不推广所有int平台。
- 10-fixed-multiply.png：1.5×2.25，从两个缩放输入到较宽中间乘积，再除回一份缩放，最后读回3.375，四步完整分开。
- 11-fixed-error.png：0.1特设向下舍入例；十次累计偏小，不能推出源码所有路径都采用相同舍入方式。
- 12-direction.png：长度1、朝右上45°的箭头，给水平/竖直份额建立几何直觉。不是坐标变换的完整推导，也不要求先掌握向量。
- 13-real-table.png：原数组6个真实表项，显示存下整数与除以65536后的六位小数。第0项25体现半格采样，未用理想sin(0)=0替换原数据。
- 14-table-reuse.png：先读取全部10240项，绘图时每8项取一点连接成趋势曲线；刻度为数组位置。余弦偏移2048的说明是实际共用关系，不是复制另一张表；曲线不是逐点精度检验图。
- 15-frame-bytes.png：未压缩的单幅画面容量比较，条长比例1:3；另计768字节调色板。不展示整个进程内存或磁盘压缩率。
- 16-palette.png：原图16×16局部最近邻放大24倍；黄色圈列112、行12，编号159和RGB(55,63,39)直接来自该PNG。不是引擎最终调色板截图。
- 17-real-wad.png：直接解析真实MAP01的目录字段，展示7块名字、文件偏移与字节长度；不是伪造编辑器/十六进制工具界面，不表示这些块全用PU_CACHE。
- 18-cache.png：无副本、已有副本、被回收后再需要的三种状态。回收不是每次第二次读取后必定发生；三框说明可能情形，非固定调用时序或LRU队列。
- 19-low-detail.png：同一原生320×200模型画面与每两列复用一份样本的实际处理结果，上下面板均最近邻放大到864×540。具体处理是目的x读取原图x的最大不超过它的偶数列；不是游戏设置截图或原版投影逐像素仿真。
- 20-low-detail-zoom.png：图19两份原生结果的同一16×16区域，列164..179、行118..133，最近邻放大24倍，对照横向细节变化。
- 21-tics.png：世界更新与画面显示的概念区别，点数不代表该段真实次数，35只来自逻辑常量；无机器测评或保证帧率。
- 22-series.png：六篇理解路线，顺序是课程关系，不是引擎执行流水线。

封面为原创中文排版，含同一双房间模型缩图，沿用Freedoom材料许可；不是新增官方游戏图。所有正式图保留本地发布原文件，手机比例代理只用于作者检查，不作为素材交付或浏览器截图。

## 5. 可复核的数值与模型边界

双房间沿用第四篇：A平面x0..256、y0..192，地0顶128；B为x256..512、y0..192，地24顶96；眼睛(128,96,41)、朝+x，320×200教学画布，水平视野90度、比例160。本篇从第四篇已经计算的960×600最近邻结果还原320×200，不重新运行3D游戏或声称新增投影算法。图19第二份画面用一列复制成两列，仍写满64000格，其中15634格与原样不同；这是图像差异，不是性能指标。

小列地址为12.25+i×0.5，i从0到7；固定表示为802816+i×32768。二者读回相同。整数乘法例98304×147456=14495514624，除65536得221184，再读回3.375。0.1向下舍入得6553，读回0.0999908447265625；十次合计0.999908447265625。最小正步长1/65536；32位有符号16.16范围为−32768至32768−1/65536。

finesine实际10240项，所摘编号0、1、2、1024、2048、4096分别为25、75、125、46358、65535、−25。表项按4字节计算为40960字节，不等于C源文件124254字节。320×200×1=64000字节；×3=192000字节；256×3=768字节。容量计算不代表整个游戏所需内存。

WAD解析采用小端有符号32位目录字段，每项16字节。本文件11个目录项，目录范围及每块范围均在124013字节原文件内。图17数据依次为：THINGS(116905,2000)、LINEDEFS(5766,17808)、VERTEXES(118905,4932)、SEGS(53947,27168)、SSECTORS(114085,2820)、NODES(23574,19712)、SECTORS(48591,5356)，括号中为文件偏移和长度，均以字节计。

作者复核包括固定来源的字节哈希、真实表读取、精确分数与定点步进、全部双列复制结果、正式面板与局部图的实际像素。它们验证本文指定输入与输出，不替代完整Doom执行、硬件测量或独立审读。

## 6. AI辅助说明

AI用于设计教学顺序、查阅公开一手材料、撰写中文、编写只读解析和原创绘图/验证脚本，并进行文件和离线手机比例检查。事实取自以上材料；没有以生成图替代真实原照或资源文件。非作者独立审读、发布构建与线上实际浏览器检查分别验收，本页不自签独评或平台通过。
