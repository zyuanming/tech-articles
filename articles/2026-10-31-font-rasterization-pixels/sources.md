# 来源与素材

## 参考

- Donald E. Knuth, *The METAFONTbook*, Addison-Wesley, 1986；以及 Knuth 关于
  TeX/Metafont 的公开叙述（1977 年起，目标是让低分辨率设备上的数学公式也能看）。
- Adobe Systems, *PostScript Language Reference*（第三版，1999）。轮廓、填充规则、
  非零环绕规则的定义以此为准。
- Apple, *TrueType Reference Manual*。二次贝塞尔、hinting 字节码、指令集。
- Microsoft, *OpenType Specification*（TrueType 与 CFF 两种轮廓）。
- FreeType 文档与源码（`ftgrays.c` 的扫描线填充、`ftobjs.c` 的 hinting 调用）。
- Chris Green, *Improved Alpha-Tested Magnification for Vector Textures and Special
  Effects*, SIGGRAPH 2007。距离场文字渲染的出处。
- V. Chlumský, *Shape Decomposition for Multi-channel Distance Fields*, 2014（MSDF），
  文中只在「另一条路」一小节提到它的思路，没有实现。
- E. Reinhard 等关于 sRGB 与显示 gamma 的标准描述；本文的 gamma 曲线用 IEC 61966-2-1
  的 sRGB 编码公式。

## 事实核对说明

- 时间线里的年份（Metafont 1977、Adobe 1982、LaserWriter 1985、TrueType 1991、
  OpenType 1996、ClearType 2000）按公开的产品与文献年份表述，不精确到月份。
- 「macOS 在 2018 年的 Mojave 里取消次像素抗锯齿」指的是系统默认关闭该选项，
  不是删掉了实现。
- NeXT 显示器的灰度级数按 2 位（4 级）表述。
- 本文没有引用任何实测的市场数据或性能基准；所有数字都来自本目录的代码。

## 图片

21 张示意图与封面由 `examples/build_figures.py` 生成，属原创教学示意。
其中的「像素面板」是 `examples/glyph.py` 对本文自定义字形的真实渲染输出，
不是从任何字体文件中截取的图像。

一张照片合成：

| 文件 | 内容 | 作者 | 许可 | 原页 |
| --- | --- | --- | --- | --- |
| `assets/22-knuth-and-next.jpg` | Donald Knuth 与 NeXTstation（两张合成） | 左：Flickr 用户（Commons 记录）；右：未署名（Commons 记录） | CC BY-SA 2.5 / CC BY-SA 3.0 | [Knuth](https://commons.wikimedia.org/wiki/File:KnuthAtOpenContentAlliance.jpg) · [NeXTstation](https://commons.wikimedia.org/wiki/File:NeXTstation.jpg) |

处理方式：两张都等比缩放到 420 像素高、底部加署名条，未修改画面内容。原图在 `originals/`。

## 缺口

- 没有 Metafont 源码页或 Knuth 手稿的照片。
- 没有 1990 年代屏幕次像素结构的显微照片，次像素那一节用的是示意图。
- 汉字字形的渲染没有做实测——本文的模型只处理 `O` 和 `I` 两个教学字形，
  真实汉字的 hinting 复杂度远高于此，文中已注明。

## AI 辅助说明

正文由作者撰写，测量与绘图代码由作者编写并实际运行。没有使用生成式图像模型。
