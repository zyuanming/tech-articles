# 来源与素材记录

核对日期：2026-10-11。原创中文正文由 zyuanming 发布，CC BY 4.0；第三方素材逐项保留自身权利，不纳入该授权。

## 事实来源与范围

- 主要解释来源与目标配图页：Craig Reynolds, Boids: Background and Update，https://www.red3d.com/cwr/boids/ 。1986模型时间、三条局部规则、邻域、早期预测回避、1987短片、空间查找。页面正文六张图全部保留原件并进入read.md。
- 论文元信息：https://www.red3d.com/cwr/papers/1987/boids.html 。正式发表为Computer Graphics 21(4), SIGGRAPH 1987, pp.25–34。
- 作者提供的论文OCR再版：https://www.red3d.com/cwr/papers/1987/SIGGRAPH87.pdf 。读取行为组合/加速度预算与模型边界，PDF自行说明无图。未把其全文或页面截图收入公开素材；其刊载复制条件不视为开放再发布许可。
- 三鸟坐标、权重、加权求和、同步更新及全部现代二维实验是本文自建教学例子，不冒充原论文代码。正文标准库算术例实际运行；100个体NumPy模拟实际运行，种子12、步长0.1、空间边长10、感知半径2.2、分离半径0.6、速度上限1.2、加速度上限0.7。

## 逐项第三方图片映射

目标页：https://www.red3d.com/cwr/boids/ 。作者署名Craig Reynolds。以下均按原URL取得完整GIF，未截取、未重绘、未放大、未压缩；页面所供原件本身是小尺寸历史网络图片，不能声称高清历史影像。六图没有另一个高清原文件链接。

1. images/flocking_around_19.gif → assets/flocking_around_19.gif → 开篇1986模拟；279×199，6949字节。
2. images/neighborhood.gif → assets/neighborhood.gif → 局部邻域；183×158，2329字节。
3. images/separation.gif → assets/separation.gif → 分离；217×145，3253字节。
4. images/alignment.gif → assets/alignment.gif → 对齐；217×145，3494字节。
5. images/cohesion.gif → assets/cohesion.gif → 聚合；217×145，3522字节。
6. images/downflockquad.gif → assets/downflockquad.gif → 1987动画效果；160×120，14271字节。

上述六项原文件URL均为 https://www.red3d.com/cwr/boids/images/ 加文件名。上述六张图未明示开放许可，不属于本文原创正文的CC BY 4.0授权，也不表示已取得作者的开放再授权。文末按原页集中署名；后续转载者须自行确认图片复用依据。尚无证据表明作者主页的肖像可开放复用，故未采用；文章主线是局部运动机制，未改用生成肖像或同名运动员。

## 原创图片与实验文件

assets/01-three-birds.png至assets/15-wrap-distance.png共15张均为原创教学图，由本文明确数值及程序生成。08/09/10/11是实际教学模拟快照，其余是几何/向量/信息流示意；14-obstacle-lookahead不是保证安全的求解结果。全部PNG1152×832，中文字体Noto Sans CJK；最高质量当前生成文件，无代理图替代。

examples/simulate.py为原创可复现实验（依赖NumPy），输出第0、40、100、180步CSV；正文的三鸟演算仅依赖Python标准库。原创正文的CC BY 4.0声明不自动扩展到图片及代码。

本文使用AI辅助调研与写作；原创教学图按明确设定由代码生成，合成演示与真实来源图已区分。
