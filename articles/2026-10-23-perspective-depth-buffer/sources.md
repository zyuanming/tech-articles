## 来源、核验范围与图像权利

1. Nathan Reed，NVIDIA，2021，《Visualizing Depth Precision》：https://developer.nvidia.com/blog/visualizing-depth-precision/ 。实际阅读作者正文，核对投影深度的1/z关系、整数与浮点的精度分布及反向映射条件；未把页面的AI摘要当作者论证，未执行源站代码。本文推导、参数选择、实验代码和图均为独立制作，不复制该文图形布局。
2. Microsoft，《Configuring Depth-Stencil Functionality》：https://learn.microsoft.com/en-us/windows/win32/direct3d11/d3d10-graphics-programming-guide-depth-stencil 。实际返回正文核对测试/写入设置的区分，以及共面表面的深度冲突用途背景；不照抄示例代码。
3. Microsoft，《D3D11_COMPARISON_FUNC enumeration》：https://learn.microsoft.com/en-us/windows/win32/api/d3d11/ne-d3d11-d3d11_comparison_func 。实际返回正文核对 LESS、EQUAL、LESS_EQUAL、GREATER 的比较含义。

本篇16张交付图均来自独立公式、原创布局与自写模型输出。曾核看 NVIDIA 原图及其官方条款，因条款不提供本文所需公开再发布许可，没有采用、裁切或照描原图；公开可浏览不等于开放许可。NVIDIA条款实际到达页面：https://www.nvidia.com/en-eu/about-nvidia/terms-of-service/ 。未采用原站图片。

Khronos glDepthFunc 与 glClipControl 文档未列为本篇已读事实来源；上述 Microsoft 来源仅使用其公开正文。


## 编写与使用说明

正文由 AI 辅助编写，教学程序与数值示例经过实际运行核对。原创正文按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 提供；此声明不自动适用于图片、代码或第三方材料。第三方署名、限制和通知按上文及正文保留。
