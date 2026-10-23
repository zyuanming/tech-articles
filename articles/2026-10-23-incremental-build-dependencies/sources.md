# 来源、素材权利与 AI 辅助说明

- GNU Make官方手册[How make Processes a Makefile](https://www.gnu.org/software/make/manual/html_node/How-Make-Works.html)：读取该节时间戳与目标处理的公开正文。这里只抽出普通判断，不复现完整Make规则。
- Bazel官方[Remote Caching](https://bazel.build/remote/caching)：实际返回正文中的action、动作缓存与CAS、输入/环境说明；仅借用架构术语，不复制配置，也不引用其随版本变化的特定开关行为为永恒事实。
- Bazel官方[Hermeticity](https://bazel.build/basics/hermeticity)：实际返回定义、输入隔离与非确定性来源段。本文把原则落在独立玩具实验，不称运行过Bazel。
- Mokhov、Mitchell、Peyton Jones，2018，[Build Systems à la Carte](https://www.microsoft.com/en-us/research/wp-content/uploads/2018/03/build-systems.pdf)，DOI [10.1145/3236774](https://doi.org/10.1145/3236774)：阅读§1–2相关段与Figures1/3/4的文字说明，实际查看封面与Figure1所在页。调度与重建判定分离、静态/动态依赖和提前截断是重要阅读线索；本文未读完29页，不转述其完整Haskell框架。

封面肉眼可见CC BY 4.0与作者版权；Figure1对经典传播有信息价值，但本文用不同的操作/输入与连续实验解释字节不变、回滚和错误键，交付16图均为独立程序绘图，不复刻该三联图布局，也没有截取原页。原图只保留为核证材料，不必为“多图”强塞进文章。代码为本篇自写，不执行或复制来源Haskell/远端构建配置。

科学图是实际模型结果或明确标注的示意，不是生成的真实工程截图。


## AI 辅助与许可范围

本文使用 AI 辅助资料整理、讲解撰写、教学代码和原创图示制作；实验结果来自文中说明的实际程序运行，不是实地或生产系统测量。

原创文章正文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。这一正文许可不自动适用于代码、图片和第三方素材；第三方材料保留文中列明的原作者、许可与限制。
