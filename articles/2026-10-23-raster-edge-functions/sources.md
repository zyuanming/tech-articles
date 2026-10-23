## 来源、阅读范围与图像权利说明

1. Microsoft Learn，Rasterization Rules，公开页面读取到三角形、采样与多采样章节及后部说明；本文只借其核对 top-left 边界原则与多采样区别。
https://learn.microsoft.com/en-gb/windows/win32/direct3d11/d3d10-graphics-programming-guide-rasterizer-stage-rules
2. Fabian Giesen，Triangle rasterization in practice，2013-02-08。读取正文至结尾，核对边函数、整数偏置、子像素和坐标约定区别；评论区不是本文证据基础。原文示例代码明确注明未测试；本文没有执行或复制该代码。
https://fgiesen.wordpress.com/2013/02/08/triangle-rasterization-in-practice/
3. Fabian Giesen，Optimizing the basic rasterizer，2013-02-10。实际读取开头至增量公式与基础循环附近，只核对边函数的仿射逐步性质，不声称读完全文或做过作者后续优化。
https://fgiesen.wordpress.com/2013/02/10/optimizing-the-basic-rasterizer/

Microsoft Learn 使用条款的文档/图像部分限制图像复制和再传输，未取得原图另行明确许可，因此不收录原图，也不描摹其布局。原图保留来源链接供读者访问。条款依据：https://learn.microsoft.com/en-us/legal/termsofuse 。

16 图均由本篇自写模型及独立数学构造原生绘制，不是原图描摹，不含论文扫描、官网照片或 NVIDIA 受限图。公开网页不等于开放图片许可。本篇的有向面积推导、数值例、测试设计、代码和图中实验数据是本次原创工作；外部文章只作上述有限原则核对。没有复制长段原文、原站代码或外部代码执行。

范围声明：模型不包含三维裁剪、透视校正、深度缓冲、背面剔除、MSAA、保守光栅化、GPU 位宽模拟与 tile 实现。代码输出是教学模型的验证结果，不是 API 一致性认证。

## 编写与使用说明

正文由 AI 辅助编写，教学程序与数值示例经过实际运行核对。原创正文按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 提供；此声明不自动适用于图片、代码或第三方材料。第三方署名、限制和通知按上文及正文保留。
