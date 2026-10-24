# 来源、图像权利与模型边界

2026-10-24核查。本篇专讲理想触点网络的逻辑分析与合成；不是信息熵、编码或Theseus迷宫存储的旧题重讲。

## 一手依据与核读范围

- Claude E. Shannon，1938，*A Symbolic Analysis of Relay and Switching Circuits*，[Caltech公开原文扫描](https://paradise.caltech.edu/ist4/lectures/shannon38.pdf)。实际核读引言、§II的hindrance定义、串并联、命题逻辑对应、否定、等价化简与时间假设相关段落；并检查全文目录与后续时间相关讨论。扫描为论文汇编重印，封面脚注注明1938论文提交、会议信息及源于MIT硕士论文。正文不混用这些日期，也不声称是原始学位论文的逐页复刻。原文hindrance用0=闭路、1=开路；本文明确另用导通变量1=闭路。正文小例、线路、证明、计算数据和时序均为独立设计，非复制原图。
- [欧姆龙继电器分类与真实产品展示](https://www.ia.omron.com/products/category/relays/)、[官方结构介绍](https://www.ia.omron.com/support/guide/36/introduction.html)、[官方术语](https://www.ia.omron.com/support/guide/36/explanation_of_terms.html)：核对电磁驱动触点、常开/常闭与普通继电器的用途级说明。结构介绍整页读取超时，搜索返回其官方摘要；没有宣称完整读取此页或具体产品数据表。原文不使用任何型号的额定值或实测响应时间。

MIT学位论文存储页出现机器人检查，未绕过。1938已发表文章在Caltech正常公开，可直接阅读，并非用来绕开MIT受限原件。

## 第三方图逐图记录

[originals/photos/shannon.jpg](originals/photos/shannon.jpg)：Claude Shannon真实肖像。摄影Konrad Jacobs，©MFO；[Commons文件页](https://commons.wikimedia.org/wiki/File:ClaudeShannon_MFO3807.jpg)，[MFO来源记录](https://opc.mfo.de/detail?photo_id=3807)，[CC BY-SA 2.0 DE](https://creativecommons.org/licenses/by-sa/2.0/de/)，[完整许可](https://creativecommons.org/licenses/by-sa/2.0/de/legalcode)。复用仓库已经保存、与上述文件身份一致的284×400字节版本，本篇未修改、裁剪或重压缩。

Commons记录授权由VRT确认，票据2008042410024381；既有版本有2019黑白调整和2025水印移除，正文已说明。MFO现页Copyright unknown与Commons授权版本记录不同，本文保留具体CC BY-SA 2.0 DE许可而不擅改公有领域。文件上传日期不作为拍摄日期，照片不描述为1938现场。改编该肖像应按相同许可版本或兼容许可分享；此义务针对图像，不把文章其他独立作品改成同一许可。

## 真实继电器原页与未归档范围

普通电磁继电器的真实外观与厂商结构信息在首次介绍处链接官方产品及结构页。未发现可据以把官方产品照片和技术插图再发布到本库的开放图像许可，因此没有下载归档或复制截图；结构介绍访问还发生超时。依仓库图像规则保留原站查看入口，本文自绘两状态线圈/触点作用图承担结构解释。官方图片不计入本地配图数，也不宣称获得CC授权。原创图未冒充任何型号、历史设备或测量仪表界面。

## 原创图与计算

assets/01—12逐图职责见正文图注及examples/figure-metadata.json：完整电源负载回路；线圈未激励/激励两状态；串联四态；并联一条有效路径；四触点主例；抽公共许可后的三触点；八态对账；错误变换反例；互补触点；异或合成；不同切换时刻反例。02与03属于同一机制的连续两个状态，不用分帧数量夸大不同概念数量。

examples/measure.py为Python标准库程序，无随机数。枚举八态检查F=G；枚举四态检查其他说明；trace中的t为任意教学时间单位，非毫秒或测得数据。触点数量4与3只针对教学图；不推算真实继电器数量、成本或速度。原始数据results.json供绘图读取。生成图宽840px、关键字最小32px，尺寸与身份逐图记录；照片字号NOT_MEASURED。

原创正文、原创教学图、模型数据与原创代码单独明确采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名文章题名与zyuanming，链接原文与许可并说明修改。第三方材料不自动套此许可。

AI辅助用于来源检索与核对、中文解释、程序计算、原创绘图与修订。没有生成历史照片，未虚构访谈、亲历或真实电路实验。
