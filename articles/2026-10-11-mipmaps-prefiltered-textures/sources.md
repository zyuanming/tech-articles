# 图片与参考来源

本文原创正文采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。第三方图片、论文及其余素材保留各自权利，不因收录而受正文统一授权覆盖。

本文使用AI辅助调研与写作；原创教学图按文中明确设定由代码生成，合成计算图与真实来源图已区分。

## 配图

- `assets/01-filter-comparison.png`至`18-experiment.png`：本文原创教学示意与合成计算图。生成程序为`examples/generate_figures.py`。图1用相同自设纹理、相同透视映射比较单点、基础层双线性及Mipmap混层；不是游戏截图、硬件基准或真实场景摄影。其余图为文中算例的几何、颜色或状态表示。
- `assets/ms-mip1.jpg`、`ms-mip2.jpg`、`ms-mip3.jpg`：Microsoft，危险标志纹理三层。原页[Texture filtering with mipmaps](https://learn.microsoft.com/en-us/windows/uwp/graphics-concepts/texture-filtering-with-mipmaps)。依据[MicrosoftDocs/windows-dev-docs文档许可](https://github.com/MicrosoftDocs/windows-dev-docs/blob/docs/LICENSE)，CC BY 4.0；原文件未改动，不表示微软背书。原文件依次为[64层](https://learn.microsoft.com/en-us/windows/uwp/graphics-concepts/images/mip1.jpg)、[128层](https://learn.microsoft.com/en-us/windows/uwp/graphics-concepts/images/mip2.jpg)、[256层](https://learn.microsoft.com/en-us/windows/uwp/graphics-concepts/images/mip3.jpg)。该目标解释页的三幅正文图均已在相关段落中收录。

## 一手资料与继续阅读

- Lance Williams，1983，[Pyramidal Parametrics](https://users.cs.northwestern.edu/~ago820/cs395/Papers/Williams_1983.pdf)。用于纹理采样窗口、预过滤多分辨率表示及发表年份；本文不复制论文图片或整页，论文版权不属于本文。
- [Microsoft Learn：Texture filtering with mipmaps](https://learn.microsoft.com/en-us/windows/uwp/graphics-concepts/texture-filtering-with-mipmaps)，层级与示例原图。
- [Direct3D 11.3 Functional Specification](https://microsoft.github.io/DirectX-Specs/d3d/archive/D3D11_3_FunctionalSpec.htm)，纹理采样与LOD规则。正文的单参数ρ是教学简化，不冒充完整规范。
- Pharr、Jakob、Humphreys，[Physically Based Rendering第四版：Image Texture](https://www.pbr-book.org/4ed/Textures_and_Materials/Image_Texture)，图像金字塔、三线性、EWA。该书图片未在本文转载，读者可在原页比较作者的渲染结果。
- Microsoft DirectXTex：[Filter Flags](https://github.com/microsoft/DirectXTex/wiki/Filter-Flags)与[ScaleMipMapsAlphaForCoverage](https://github.com/microsoft/DirectXTex/wiki/ScaleMipMapsAlphaForCoverage)，数据语义、sRGB与透明覆盖率处理。

本文不是人物传记。Williams仅用于交代技术发表的历史背景；未取得适当复用依据的肖像没有采用，也不使用生成肖像代替。本文所有自设数值的适用条件见正文。
