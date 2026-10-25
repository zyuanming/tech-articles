# 来源、图像与许可

本文为 2026-10-25 新作。原创正文与原创教学图按仓库 CC BY 4.0 发布；`examples` 中原创程序与数据按 CC0-1.0 发布。第三方原件保留自己的许可。AI 辅助完成资料检索、推导、中文表达和制图代码；数值由附带 Python 实际执行，图形为程序绘制或明确标注来源的原图，没有生成式模型伪造的软件界面或实拍。

## 一手来源与支持范围

1. **Khronos，glTF 2.0 Specification**：[官方文档](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)。本次读取页面标头为 Version 2.0.1，2021-10-11，提交 `8e798b02d254cea97659a333cfcb20875b62bdd4`，读取日期 2026-10-25。依据 Meshes、Textures、Materials、material.normalTextureInfo：NORMAL/TANGENT 属性、`B=cross(N,T)×w`、同三角形 w 一致、缺少切线时推荐 MikkTSpace、纹理左上原点、正常法线的线性 RGB 数据及解包、scale 与归一化。本文没有复制规范的图、表排版或大段文字；规范著作权仍属 Khronos，公开可读不等于单幅图可任意改绘再许可。
2. **Morten S. Mikkelsen，MikkTSpace 接口说明**：[作者仓库的 mikktspace.h](https://github.com/mmikk/MikkTSpace/blob/master/mikktspace.h)，[原始文本](https://raw.githubusercontent.com/mmikk/MikkTSpace/master/mikktspace.h)，读取 2026-10-25。Copyright 2011 Morten S. Mikkelsen，源文件采用 zlib 风格许可。依据其接口注释解释接缝顶点、符号、三角化与烘焙/着色器匹配；未复制实现。本文 `triangle_frame` 是单三角教学推导，既不声称 MikkTSpace 兼容实现，也不声称重新正交化可普遍保持烘焙一致。
3. **Eric Chadwick、DGG，CompareNormal**：[固定版本 README](https://github.com/KhronosGroup/glTF-Sample-Assets/blob/8f492390ddc7a2ae221a1369ef560589cf8c70fb/Models/CompareNormal/README.md)。版本提交 `8f492390ddc7a2ae221a1369ef560589cf8c70fb`；官方说明截图来自 Babylon.js Sandbox，用于对比省略/使用法线纹理。图像为作者示例，本文没有在 Babylon.js 重现这一截图，也没有下载模型后声称运行它。

主例、量化误差、手性反例、UV 求解、非均匀缩放的垂直性反例，以及程序生成高度函数的导数，均由本文独立推导和计算；不归因于规范规定了这些特定数值。颜色输出采用标准 sRGB 分段函数；输入法线按数值处理。本文不涉及 BC5 压缩、完整 PBR、皮肤变形和复杂引擎的切线插值实现。

## 实际原图、署名与完整许可

`assets/16-official-compare.jpg` 是 `originals/photos/CompareNormal-original.jpg` 的逐字节副本；原尺寸 **1649×792**，392666 字节，未裁切、重绘、加字或改变像素。

- [固定版本原图](https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/8f492390ddc7a2ae221a1369ef560589cf8c70fb/Models/CompareNormal/screenshot/screenshot_Large.jpg)
- Git blob SHA-1：`7a71f74ee64b972d6f0406df3ed829b15e4122e1`，本地完整文件已核一致。
- 原 README 署名：© 2024 Public；Eric Chadwick、DGG，Everything，CC0。glTF logo © 2017 The Khronos Group Inc.
- [模型原始许可文本，原样归档](originals/CompareNormal-LICENSE.txt)：声明覆盖模型及关联 text、image、binary 文件，使用 CC0 加 Khronos 商标说明；此许可说明文档本身 CC BY 4.0。文本内原仓库的相对路径保持原样，因此按纯文本归档；对应的可用本地许可链接如下。
- [完整 CC0-1.0 法律文本](originals/CC0-1.0.txt)
- [完整 Khronos 商标声明](originals/Khronos-Mark.txt)

原图内 glTF 标识仅随原模型截图保留作识别语境，没有将商标单独提取或宣称其受 CC0 授权，不暗示官方背书。正文中文解释两球差异，不要求读者辨识商标上的小字。引用的是模型专属许可覆盖的实际图像，并非仅从仓库代码许可推断图片授权。

## 一手资料的相关视觉库存

这里的“库存”限定为本次实际访问的一手资料及直接相关条目，不能理解为审视了 glTF 全部关联资源像素。

| 来源条目 | 获取与使用决定 | 权利与本篇对应 |
|---|---|---|
| glTF Figure 6，Normalized Texture Coordinates | 读到图注与相邻规范文字；未取得并逐像素审视该图原件。不复制，依据坐标定义独立建立本文三角与图像实验 | 原图仍属 Khronos；本文图07与正文解释左上原点/数学坐标图的差别，不冒称原图重现 |
| glTF 顶点属性表 NORMAL、TANGENT、TEXCOORD_n | 已读字段与限制；不用原表排版，改用具体数值讲单位轴与w | 本文图04、07、09，相关字段事实独立表述 |
| glTF normalTextureInfo 属性表及线性RGB/scale说明 | 已读。保留处理顺序，转为独立实验 | 图02、03、11、12、14 |
| glTF Figure 7 金属粗糙度材质说明 | 图注及相邻文本可定位；非本篇法线机制核心，没有核原像素，不转载 | 本篇未实现PBR，避免误导图像可数值对比 |
| glTF 其他场景层级、缓冲、相机、动画等图表 | 与本篇法线换基无直接解释义务，不采用；不声称全图像审读 | 无 |
| MikkTSpace 头文件 | 原始文本已读，无正文照片/效果图；关键资料是算法接口注释 | 不复制代码；图09、14讲符号与生产/运行匹配 |
| CompareNormal screenshot_Large.jpg | 成功获取、检查完整原像素；采用高清原件，不改图 | 模型专属CC0+商标条款；正文图16 |
| CompareNormal screenshot.jpg | 同一示例的导航缩略图，不重复采用 | 高清原件已保留；不为凑数量列第二张 |
| CompareNormal glTF/glb模型与其内部纹理 | 本文不加载该模型；采用官方实际效果作参照，自己的可复现平面实验补足机制 | 不宣称检验了未运行模型的全部材质、内部纹理和切线实现 |

## 逐图身份、解释义务与权利

下列原创图均为本篇新作，CC BY 4.0。数值、三角形顶点、箭头分量和条形长度来自 `examples/results.json` 或实跑原始输出。固定布局位置不表示数量。绘图基础 Canvas 接口复用本批 sRGB 文章的 CC0 代码；构图、数据与本篇所有输出新制作，没有复用旧批图片。

| 文件 | 解释义务与身份 |
|---|---|
| 00-cover.png | 同平面同光源，平坦/法线纹理实际CPU输出，揭示任务 |
| 01-normal.png | 原创法线、向光箭头示意，解释向量/点积；不是量测图 |
| 02-texture.png | 实跑96×96法线数据原像素预览和真实字节；最近邻放大 |
| 03-unpack.png | 理想值→解包→8位量化后方向，区分数学与字节 |
| 04-frame.png | 同一斜投影下T/B/N箭头，标明世界坐标；投影长度不当作空间长度 |
| 05-basis.png | 三个加权方向首尾相加，虚线合向量 |
| 06-light.png | 正确1/错误.64，共轴条长按数值生成 |
| 07-triangle.png | 世界与UV三角对应；导数长度2与单位切线不同；退化边界 |
| 08-rotation.png | 固定正交相机，方片绕Z90°，逆UV采样；正确TBN与局部分量直接当世界的真实结果 |
| 09-mirror.png | 镜像B方向、w和同一世界方向的局部分量变化 |
| 10-green.png | 真实翻转ny光照结果；与图像垂直翻转区分 |
| 11-filter-scale.png | 两方向平均缩短与四个scale实算结果 |
| 12-data.png | 正确数据读取/错误sRGB解码的实际CPU对照 |
| 13-limits.png | 同平面换灯实算；下半侧视示意的法线取自实跑纹理，不是高度 |
| 14-pipeline.png | 制作/数据/换基/光照/输出流程，边界为教学漫反射 |
| 15-live-demo.png | 原创Python网页真实Chromium点击截图，显示实际返回向量和渲染；不是第三方软件界面 |
| 16-official-compare.jpg | 第三方真实Babylon.js Sandbox原图，采用其独立CC0与商标条款，非本文原创图许可 |

原创绘图宽1062px，关键字≥40px，正文图可按354px缩放阅读；官方高清原图保持原尺寸，不将图内标识小字当教学说明。原始 `examples/output/normal-map-data.png` 不是带显示含义的彩色素材：按整数读取方向数据、不附sRGB块；其余实验输出为经过sRGB编码的显示RGB。生成器记录实际宽高与自动检查，查看图片与数字都不能代替实际引擎兼容测试。
