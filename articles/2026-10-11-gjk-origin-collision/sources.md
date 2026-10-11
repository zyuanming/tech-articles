# 来源与素材记录

核对日期：2026-10-11。原创中文正文由 zyuanming 发布，采用 CC BY 4.0；第三方图保留自身许可，不纳入正文授权。

## 原理与历史

- Gilbert、Johnson、Keerthi，A Fast Procedure for Computing the Distance Between Complex Objects in Three-Dimensional Space，IEEE Journal of Robotics and Automation 4(2)，1988年4月。原论文：https://graphics.stanford.edu/courses/cs448b-00-winter/papers/gilbert.pdf 。用于作者、年份、距离问题与机器人/CAD应用背景；未复刻论文全文、扫描页或图片，也未把本文二维教学过程称作原论文完整程序。
- Box2D 3.1.0碰撞几何文档：https://box2d.org/documentation/md_collision.html 。凸性、形状距离、凸形状适用范围。距离API：https://box2d.org/documentation/group__distance.html 。文档版本以本次核对为准，不承诺将来的接口相同。
- Jeff Linahan，A Geometric Interpretation of the Boolean Gilbert-Johnson-Keerthi Algorithm，https://arxiv.org/abs/1505.07873 。用于布尔GJK的几何解释与原点包含关系；本文不引用其性能比较结论。
- dyn4j Gjk.java：https://github.com/dyn4j/dyn4j/blob/master/src/main/java/org/dyn4j/collision/narrowphase/Gjk.java 。用于布尔/距离功能、迭代与容差设置，以及穿透信息交由后续求解器（默认EPA）的具体实现例子，不代表所有引擎相同。

本文的二维形状、三次支持查询、重心权重、平移分离和见证点全部是自设教学例子。短代码只复核这个例子，不是完整GJK求解器。形状均含内部；接触算相交，分离证明使用严格负点积。所有坐标图横纵使用相同比例。

## 第三方图片

目标解释页是Box2D碰撞几何文档。本篇为多来源原创讲解，并非该页面的逐节翻译：选用与凸性和GJK距离直接相关的两幅图。该页其他圆、胶囊、绕序、ghost collision、碰撞流形、TOI和动态树等插图属于不同主题，不纳入本篇。

1. https://box2d.org/documentation/convex_concave.svg → originals/box2d-convex_concave.svg → assets/box2d-convex_concave.png。
2. https://box2d.org/documentation/distance.svg → originals/box2d-distance.svg → assets/box2d-distance.png。

两项署名：© 2022 Erin Catto。官方源仓库的[MIT许可](https://github.com/erincatto/box2d/blob/v3.1.0/LICENSE)涵盖软件及相关文档；完整许可保留于[BOX2D-LICENSE.txt](originals/BOX2D-LICENSE.txt)。原SVG保持下载字节；兼容PNG使用Inkscape按1200像素宽渲染，无内容增删、裁切或文字改写。不是以预览截图代替原文件。

## 原创教学图与复算

assets/01-two-shapes.png至18-degenerate.png，共18幅，1200×840，使用中文Noto Sans CJK字体。几何、箭头、网格按所示数值生成；非实际引擎截图，非历史影像。examples/generate_figures.py包含生成逻辑（Pillow与NumPy）。正文标准库代码已执行，三次支持点与加权原点一致。

历史人物只用于交代算法名称与论文背景，未采用权利依据不明确的肖像，也未用生成肖像替代真实人物。原创正文CC BY 4.0声明不自动扩展到原创图片或代码。

本文使用AI辅助调研与写作；原创教学示意由代码按明确设定生成，真实来源图与合成示意已区分。
