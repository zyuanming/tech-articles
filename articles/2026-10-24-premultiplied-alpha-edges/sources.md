# 来源与素材说明

原创正文由AI辅助研究、推导、写作与修订；程序和全部图像由AI辅助编写并实际运行，不声称作者亲自体验商业软件。正文与原创图、数据：zyuanming，CC BY 4.0；examples中的原创代码：MIT。

## 一手依据及支撑范围

- [W3C Compositing and Blending Level 1，§5.1](https://www.w3.org/TR/compositing-1/#simplealphacompositing)：source-over、预乘颜色和输出alpha的公式。实际读取规范相关正文；本文例子和逐步推导自设，不照译规范。
- [Alvy Ray Smith, Image Compositing Fundamentals, Technical Memo 4, 1995-08-15](https://alvyray.com/Memos/CG/Microsoft/4_comp.pdf)：覆盖与不透明度两种解释，预乘与非预乘表示以及分组合成。实际阅读原作者备忘录；不是对1984年原论文的逐页转载。
- [W3C CSS Color 4：sRGB转换](https://www.w3.org/TR/css-color-4/#predefined-sRGB)：作为颜色空间进一步阅读入口；本文sRGB分段公式在公开代码列明，0.5转码结果由代码独立重算。

未复制这些文档的图片。W3C相关章节的方块示例与Smith备忘录图不作为本篇素材：本文改用不同红/蓝输入以及实际圆点缩放、模糊结果覆盖同一教学职责。来源网页公开可读不意味着其中每幅图都获得本库授权。本文不是人物史文章，没有使用或生成任何人物肖像。

## 图像逐项职责

全部实际文件、尺寸、最小字号和身份见 [figure-metadata.json](examples/figure-metadata.json)，可由 [lab.py](examples/lab.py)与[绘图辅助代码](examples/figurelib.py)重建。所有14幅图片原链接均为本篇代码与参数，没有第三方图像；署名zyuanming，CC BY 4.0。没有裁切或修改第三方素材。

|文件|作用与身份|
|---|---|
|01-edge.png|同一圆点缩放的实际程序输出，展示错误与修正|
|02-rgba.png|RGB与alpha分离的示意，蓝块只是隐藏RGB可视化|
|03-coverage.png|覆盖与均匀透过的不同空间模型|
|04-over.png|红蓝贡献分解及真实色块|
|05-two-alpha.png|两透明图层后的剩余覆盖|
|06-wrong-filter.png|非预乘插值的实际渐变结果|
|07-right-filter.png|预乘插值的实际渐变结果|
|08-blur.png|实际高斯模糊输出，非软件截图|
|09-associate.png|同一顺序的分组合成结果|
|10-order.png|改变前后顺序的真实输出|
|11-linear.png|实际编码灰度差别|
|12-precision.png|8位整数下极低alpha量化反例|
|13-double.png|双乘alpha的真实渐变输出|
|14-cutout.png|连续合成与阈值裁剪的真实对照|

图像中的计算数值由同次运行的results.json复算；示意长度仅在图注明确的贡献分解中按数值比例绘制。字体Noto Sans CJK只用于位图文字渲染，没有在仓库重新分发字体文件。图01兼作本文入口图，无重复封面文件。
