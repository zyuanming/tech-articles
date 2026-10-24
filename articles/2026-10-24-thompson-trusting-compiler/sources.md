# 来源、素材权利与模型边界

2026-10-24实际核查。

1. Ken Thompson，*Reflections on Trusting Trust*，Communications of the ACM 27(8)，1984-08，761–763。[原论文PDF](https://www.cs.cmu.edu/~rdriley/487/papers/Thompson_1984_ReflectionsonTrustingTrust.pdf)，实际读三页文本：自复制、转义自举、两个模式与结论。没有复制原图或大段引文。文中星号模型为原创，不是原论文程序或真实攻击复现。
2. David A. Wheeler，[DDC作者说明](https://dwheeler.com/trusting-trust/)，实际读技术摘要、误解澄清、确定性、独立性与源码对应不等于安全的边界。只概述自父编译器的简化流程，未把本篇Python状态模型当作其2009年完整证明或GCC实验。
3. [Ken Thompson, 2019肖像原页](https://commons.wikimedia.org/wiki/File:Ken_Thompson,_2019.jpg)，A.C.Diller，CC BY-SA4.0。复用本仓库2026-10-11正则文章已存照片副本，不再次下载、不再次修改。原存副本含已有裁切；本文不声称它是未裁切相机原件。实际使用文件 originals/photos/ken-thompson-2019.jpg。

照片保持[CC BY-SA4.0](https://creativecommons.org/licenses/by-sa/4.0/)，复用或改编须保留作者、来源、许可、修改说明，改编按相同许可分享。文章集合不据此整体换成CC BY-SA。照片为2019年人物肖像，非1984年现场。

## 图与代码

assets/01—12为原创控制关系、逐字符对照、代际轨迹和DDC概念图，职责逐图写在正文及examples/figure-metadata.json。没有使用论文扫描图、伪软件截图或生成照片。模型results.json由measure.py实际运行生成；标记只改变惰性字典字段或字符串，未实现真实编译器、机器码、系统植入、自我复制程序或DDC工具。实际检查四代传递、相同构建结果和独立参照差异。图中DDC流程是原理示意，不是模型执行出真实DDC的证据。

原创正文、原创图、数据和本篇原创代码明确采用[CC BY4.0](https://creativecommons.org/licenses/by/4.0/)，署名文章题名及zyuanming，保留原文与许可链接并标明修改。第三方照片和原论文不包含在该许可内。

AI辅助用于原文研究、中文写作、模型和图形程序、实际运行与修订；没有声称亲历演讲、采访或亲自拍摄，没有将AI文本当成事实来源。
