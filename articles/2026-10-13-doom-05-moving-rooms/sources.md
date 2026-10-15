# 来源、材料权利与计算边界

## 文章范围与材料身份

本文为Doom入门系列第5篇，解释普通移动中的占地、步高与净高检查，以及sector升降门/平台的高度更新。正文与中文教学图为AI辅助原创解释，不是历史作者自述。作者以公开一手代码和真实地图/图块校验机制、数值与可见结果；没有运行Doom、录制游戏、操作地图编辑器、测试真机性能或上传公众号。

真实游戏画面、真实素材文件、真实地图数据的可视化、原创模型计算和概念示意分别在图注标识。手机比例检查使用静态近似，不冒称浏览器或平台截图。图片数量不等于独立实验次数：门与平台的三状态分别合为一幅，不把面板冒充新增来源。

正文与原创中文说明采用CC BY 4.0；Freedoom材料及包含它们的衍生画面仍须遵守其自身许可。本文没有复用商业Doom的WAD美术，也不因引擎源码开放而推定原游戏图像可再分发。没有生成的假游戏截图或设备实拍。

## 1. 固定版本的一手机制依据

统一源码基准为[id Software / DOOM，a77dfb96cb91780ca334d0d4cfd86957558007e0](https://github.com/id-Software/DOOM/tree/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10)。以下为可检查的原始代码，不据现代移植版反推所有原版细节。

- [info.c：MT_PLAYER](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/info.c#L1108-L1132)：正常活玩家radius为16地图单位、height为56，不能等同于PNG尺寸或眼高，也不推广到死亡等所有状态。
- [p_map.c：P_CheckPosition、PIT_CheckLine与PIT_CheckThing](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/p_map.c)：由x±radius、y±radius构造轴对齐占地区，检查边线与其他物体。不是精确欧氏圆碰撞。文中只把竖向身体范围用于地板/天花容纳，不将该系统说成现代通用3D盒碰撞；经典普通物体相互阻挡路径也不能据此推导出任意上下穿越能力。
- [p_maputl.c：P_LineOpening](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/p_maputl.c#L300-L332)：两侧更高地板、更低天花决定开口；单面边无通行开口。身体触及多条边会继续收紧范围。
- [p_map.c：P_TryMove](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/p_map.c#L450-L497)：净高、当前z到有效天花的距离、上台阶高差分别检查。拒绝条件为净高小于物体高度、当前头顶放不下、上台阶超过24；等号只通过各自一项，仍非整步成功保证。玩家可跌落，24不是下降上限。穿墙、传送等例外不纳入普通示例。
- [p_mobj.c：P_XYMovement](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/p_mobj.c)、[p_map.c：P_SlideMove、P_HitSlideLine](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/p_map.c#L584-L788)：玩家普通移动受阻后滑墙；水平/竖直墙可去除对应分量，完整实现包含寻找阻挡、余量、重试与后备路径。正文示意不声称完整连续碰撞算法或精确复刻斜墙定点运算。
- [p_doors.c：T_VerticalDoor、EV_VerticalDoor](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/p_doors.c)：门改sector天花高度；手动类型31设为open，并清除该边特殊类型；normal到顶等待再下降，下降遇crushed改上升；open到顶停止，close等分支不同。
- [p_spec.c：P_FindLowestCeilingSurrounding](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/p_spec.c#L378-L401)与p_doors.c相应分支：所述普通/手动打开目标取相邻最低天花减4，不是全图最低。close30ThenOpen等类型不是这一目标规则。
- [p_floor.c：T_MovePlane](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/p_floor.c)、[p_map.c：P_ThingHeightClip、P_ChangeSector](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/p_map.c#L530-L557)、[p_plats.c：T_PlatRaise](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/p_plats.c#L52-L106)：贴地角色跟随新地板；非挤压平台上升途中的常规一步如受仍会阻挡的活实体影响，撤回地板高度并重新处理物体，再切为下降。正文明确排除到站分支：它即使回滚也可能返回pastdest。尸体、掉落物、crush=true等另有处理。回滚高度不等于撤销所有世界状态。
- [p_setup.c：P_LoadNodes](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/p_setup.c#L264-L294)、T_MovePlane与[r_segs.c](https://github.com/id-Software/DOOM/blob/a77dfb96cb91780ca334d0d4cfd86957558007e0/linuxdoom-1.10/r_segs.c)：BSP载入二维分割数据，所述运动修改高度而非平面边界，渲染读取当下sector高度。因此“这些升降不需重建二维BSP”是针对此结构和代码路径的归纳，不推广到改变x/y的动态几何。

作者新获取10份机制源码并复算Git blob SHA，均匹配固定提交；不执行这些源码。全文没有大段复制源码。

## 2. 真实Freedoom材料、版本与许可

Freedoom固定来源：[3ac019628d70b812ffb722f7f2365771b76a9d29](https://github.com/freedoom/freedoom/tree/3ac019628d70b812ffb722f7f2365771b76a9d29)。下列素材采用Freedoom BSD-3-Clause，保留完整[版权与许可](licenses/Freedoom-COPYING.txt)和[贡献者名单](licenses/Freedoom-CREDITS.txt)，版权归Freedoom contributors。许可与贡献者未删减；不暗示项目为本文背书。

- [官方截图页](https://freedoom.github.io/screenshots.html)明确其截图按与Freedoom相同的BSD许可使用，并说明Chocolate Doom的320×200图像被清晰放大与调整比例到1600×1200。[p1_1原图](https://freedoom.github.io/img/screenshots/p1_1.png)作为图01保留原字节/尺寸，复用系列已核证据。没有把截图里的房间称成本文MAP01门区，也未捏造它的动作前后帧。
- [patches/aqpanl01.png](https://github.com/freedoom/freedoom/blob/3ac019628d70b812ffb722f7f2365771b76a9d29/patches/aqpanl01.png)：128×128，8093字节，SHA-256 `9697093683e81d6fed56fda2f449b9f6ffc60a927709f259d633e199d54546c3`。本次新取官方原文件，用于图05及门模型。MAP01边827前侧上部纹理引用AQPANL01；[textures.cfg](https://github.com/freedoom/freedoom/blob/3ac019628d70b812ffb722f7f2365771b76a9d29/lumps/textures/textures.cfg)中AQPANL01为128×128、由同名patch在(0,0)组成。素材PNG、完整纹理定义和地图引用仍是三层数据，不混称。
- [patches/door2_1.png](https://github.com/freedoom/freedoom/blob/3ac019628d70b812ffb722f7f2365771b76a9d29/patches/door2_1.png)：96×96，3324字节，SHA-256 `9e63c5ffbb9526227e3a4ffd5494e0252fce7eb3889879b8fd96b91aec766cc8`。图05只说明另一种真实门材料，不把它说成所解析MAP01门的素材或单独的完整门纹理。
- [patches/brick.png](https://github.com/freedoom/freedoom/blob/3ac019628d70b812ffb722f7f2365771b76a9d29/patches/brick.png)128×128与[flats/floor0_1.png](https://github.com/freedoom/freedoom/blob/3ac019628d70b812ffb722f7f2365771b76a9d29/flats/floor0_1.png)64×64：复用系列此前已核原字节，并分别保留为brick-original.png、floor-original.png。
- [levels/map01.wad](https://github.com/freedoom/freedoom/blob/3ac019628d70b812ffb722f7f2365771b76a9d29/levels/map01.wad)：124013字节，SHA-256 `d9da5d7f8d97d6555182a04326f306dde6fd40da1186a6fec18143c7ccddd20d`，本地[相同原文件](examples/freedoom-map01.wad)。只读取地图记录，不运行关卡。各记录编号从0开始。

本次新材料与纹理定义文件均从官方固定提交获取，逐字节复算Git blob SHA；保留PNG而非下载站缩略图或手机代理。复用材料也逐一比对现存核准原字节。

## 3. 真实门区的可复核记录

MAP01的sector121：floor=-64，ceiling=-64。关联边号453、597、630、633、634、827；相邻双面边另一侧sector为40和130，两者floor=-64、ceiling=32。两侧单面边没有额外邻区。

linedef827原七字段为(613,483,4,31,0,564,5)：顶点编号613和483，flags=4，special=31，tag=0，正侧564、反侧5。顶点分别(1032,444)、(1144,444)，此边长度112；整条门区横向范围1024至1152，宽128，纵向444至460，深16。图07红线只标其中112长的边827，未把它误标成整条128边界。

sidedef564的偏移为(8,-64)，上部纹理AQPANL01，所属sector40。反侧5所属sector121。图08公开的是可理解的字段摘录，不是伪造编辑器面板。sector121外形与门类型来自原字节；手动打开目标28是基于当时邻区天花和原版规则的推算，不是运行帧实测。

## 4. 逐图职责与处理

除图01的官方原截图外，图02—20为原创计算、真实数据可视化或示意。封面是独立排版的原创教学封面，含同一门模型计算缩图。

- 01-real-game.png：官方实际画面，为墙/高低地面建立真实参照，原字节保留。不是同一门的录像证据。
- 02-door-states.png：同视点门天花24/64/92三状态计算，先看开缝但未容人；每个面板源320×200，放大到864×540，最近邻采样。面板不是三个独立游戏实测。
- 03-door-plan.png：明确门是从B前沿分出的16深区域、外轮廓未换世界。
- 04-door-section.png：三个高度剖面，对应净高0/40/68，解释“动天花”不是把图片缩小。
- 05-real-door-materials.png：两张新核真实原图分别放大到384×384；不同原尺寸如实标识。图像外观与机关规则分开。
- 06-real-map-overview.png：真实MAP01全部边线及sector121定位，直接绘制原字节，不是编辑器截图。
- 07-real-map-door.png：真实121区与邻区关系，纵向为教学可读性拉长，显式声明非等比例；区域框非房间完整边界，红边来自827号原记录。
- 08-real-door-records.png：实际高度、动作、材质字段分开，避免把文件名与门动作混淆。
- 09-player-body.png：32×32轴对齐占地、56身高和本系列41眼高的概念差别。不是人体照片、怪物尺寸或任意现代物理系统的通用模型。
- 10-body-wall.png：沿x展开的占用范围，给出中心未到墙而身体越界的反例；横向条形不是把方形占地改成矩形。
- 11-step-limit.png：普通上台阶必要条件中24/25的边界差异，其余条件仍需检查。
- 12-headroom.png：天花79/80对应净高55/56，画出不足1单位与刚好容纳，非全部通行保证。
- 13-slide.png：直墙旁去掉推墙部分、保留沿墙部分；概念方向图不是完整滑墙求解实测。
- 14-door-state-machine.png：普通normal门的状态与受阻反向，不混用MAP01的open类型。
- 15-door-top-height.png：本例相邻最低天花96减4得92，条形高度按同一比例。
- 16-platform-states.png：B内独立平台24/48/64三状态原创计算，明确空平台外观，不暗示载人可达这些高度。
- 17-platform-carry.png：贴地玩家随地板24/32/40更新，头顶80/88/96；侧剖面同一高度比例。
- 18-platform-blocked.png：普通非挤压平台上升中从40试42被活玩家阻挡，地板回退；不把到站和crush=true分支也这样解释。
- 19-plan-stays.png：两种独立高度变更均不挪动x/y边界，是二维BSP可复用的具体范围，不是所有动态几何结论。
- 20-update-loop.png：把候选、检查、接受/调整/撤回与绘制连接；概念摘要而非严格源码执行顺序。

原始材料的许可范围覆盖本文由它们计算的房间外观、材料放大图与地图可视化；文章的原创说明许可不抹去Freedoom版权条件。无未取得权利的人物/硬件照片，本题也没有以人物或硬件作为核心对象。

## 5. 教学模型与数值检查边界

房间A为x0..256、y0..192、地0顶128；B为x256..512、y0..192、地24顶96。门示例把B的x256..272划成D，地24，天花24/64/92；其余B从272开始。观察眼睛(128,96,41)、朝+x，320×200正方像素教学画布，水平视野90度、比例参数160，无HUD、不加光照变暗。

模型逐格穿过画布格心查找最近平面表面，仅为计算可见外观，不能当作经典Doom实际逐列渲染实现。x不变的墙取横向192−y，纵向从该墙段顶向下；y不变墙沿x取样；水平面取(x,192−y)。材料索引取向下整数并按图块宽高循环。D前方96..128为固定砖墙；门面从D天花到96，材料随门抬升，图案顶部位置定义为D天花+72。这是明确指定的教学对齐，不宣称复刻真实MAP01的偏移/pegging或前文模型所有花纹位置。

平台示例移除D，恢复原A/B开口。在B中x320..448、y32..160，平台地板24/48/64，顶96。外侧地面仍24，顶面与新增侧面按真实砖/地板图取色。无角色模型参与这三幅外观；载人计算在剖面中单独给出。

作者用未导入渲染器的标量平面求交/原图取色参考，核对六种状态的原生图像；边界上完全同距离的相邻平面保留可允许的取色集合，不偷换成逐位原版兼容声明。同时核对正式三面板中实际像素区域与原生结果的最近邻放大一致。

数值条件单独验证：净高0/40/68；台阶24/25；门区79/80对56身高；目标92和真实地图推算28；中心480/500与墙512；脚24/32/40/42对头80/88/96/98。枚举必要条件的逻辑等价只检查比较方向与边界，不是运行完整碰撞器，也不是测量性能。

## 6. AI辅助说明

AI用于规划教学顺序、撰写中文、查阅公开材料、编写只读解析与原创计算/绘图脚本，并进行文件和静态视觉自检。事实来自所列一手文件；没有AI生成图替代真实截图或原始素材。独立审读与实际站点发布检查属于各自验收环节，本页不自签独立审读或平台通过。
