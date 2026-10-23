### 来源、实际阅读范围与边界

- [NASA/JPL NAIF：Rotation](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/rotation.html)：实际读约定、欧拉映射危险、单位四元数/乘法、轴角推导相关段；其坐标旋转与向量旋转号法已明确区分。未声称全文逐段阅读，也未运行SPICE代码。
- [Ken Shoemake，1985原论文](https://www.cs.cmu.edu/~kiranb/animation/p245-shoemake.pdf)：实际读首页及第246–249页相关旋转、SLERP、双覆盖段，并查看首页版权和第249页原小图。本文不声称完整复现样条算法。
- [SciPy Slerp官方说明](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Slerp.html)：用于核对相邻关键姿态间固定轴/恒速/最短路径说明；本文代码不是调用或移植SciPy实现。
- [Markley，Spacecraft Attitude Representations目录](https://ntrs.nasa.gov/citations/19990110711)：仅使用目录信息，未将摘要作为全文证据，未采用其中图片。

公开版本的15张图及程序均为本篇原创教学构造；图14仅链接原站，原ACM图片不随本仓库归档。不是引擎运行截图、硬件实测或上游论文实验复现。用AI辅助整理和代码制图，所有示例值来自所附代码与明确公式。

## 编写与使用说明

正文由 AI 辅助编写，教学程序与数值示例经过实际运行核对。原创正文按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 提供；此声明不自动适用于图片、代码或第三方材料。第三方署名、限制和通知按上文及正文保留。
