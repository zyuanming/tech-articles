# 来源、图像权利和模型范围

2026-10-24核查。本篇核心是用控制存储中的步骤调度已有数据通路，和旧EDSAC延迟线文章的声学存储问题不同。

## 已实际查阅的一手资料

- [Wilkes个人档案Short Biography](https://www.cl.cam.ac.uk/archive/mvw1/short-biography.html)：核读1951年前后微程序提议与此前EDSAC工作的关系。个人档案属于当事人自述/简介，未扩展成逐日发明故事。
- M. V. Wilkes、J. B. Stringer，1953，*Micro-programming and the design of the control circuits in an electronic digital computer*，[出版者记录与原文Extract](https://www.cambridge.org/core/journals/mathematical-proceedings-of-the-cambridge-philosophical-society/article/microprogramming-and-the-design-of-the-control-circuits-in-an-electronic-digital-computer/4F7EDCBEB735637790E7170503908323)，49(2)，230–238。实际核读题名、作者、期刊年代及开头关于结构规则性、维护和控制复杂性的段落；完整正文受限，本次没有宣称完整核读1953论文或复现其电路。网页2008年上线日期不是论文发表年份。
- [剑桥Archive photos](https://www.cl.cam.ac.uk/relics/archive_photos.html)的照片身份与下级许可段。没有把EDSAC I延迟线照片误认成EDSAC 2控制存储。

1951原文再版与1992 EDSAC2论文未能取得完整正文；因此不描述原机微指令位宽、矩阵细节、原始电路时序或“世界第一”比较。正文现代模型的每一部件、数字和地址是本文选择，并非这些历史论文的转录。

## 第三方照片

唯一第三方正文图：[originals/photos/wilkes-with-delay-lines.jpg](originals/photos/wilkes-with-delay-lines.jpg)，复用仓库已保留原件，未经裁切、拉伸、增补或重新压缩。原文件：https://www.cl.cam.ac.uk/relics/jpegs/delay_lines.jpg 。身份：Wilkes与EDSAC延迟线管组，原档案未给本文可确认的精确拍摄日，因此不补写日月。

署名原文：Copyright Department of Computer Science and Technology, University of Cambridge. Reproduced by permission.

许可：[CC BY 2.0 UK](https://creativecommons.org/licenses/by/2.0/uk/)，随文保留[完整许可文本](licenses/CC-BY-2.0-UK.html)。此处使用档案照片下级页的专列许可，不以网站其他页的CC BY4.0覆盖它。该照片不适用本文原创内容许可。

## 原创图和验证范围

assets/01—12为原创教学图；图注和examples/figure-metadata.json逐图说明理解职责。图显示逻辑通路/控制关系，不显示历史芯片版图、电子管接线或实测波形。examples/measure.py使用Python标准库，记录三微步与256组小整数加法检查，输出results.json；图中教学数取自这一确定模型。无随机数。内存读视为原子动作、整数不溢出；不模拟真实时序、总线电气冲突或存储延迟。

原创正文、图、模型数据、原创代码明确采用[CC BY4.0](https://creativecommons.org/licenses/by/4.0/)，署名文章题名与发布者zyuanming，链接原文、许可并标明修改。照片、论文、外链原文继续保留各自权利。

AI辅助用于一手资料检索、事实范围核对、中文解释、模型编程、运行计算、原创绘图与修订。没有生成历史照片，没有声称采访、亲见历史机器或亲测原硬件。

## 链接查看的关键实物

[EDSAC II control matrix rack](https://www.cl.cam.ac.uk/relics/jpegs/edsac99.26.jpg)，身份与CC BY 2.0 UK许可均由同一剑桥档案页明确。该独立目标首次原文件归档请求在网络代理CONNECT阶段返回403，未取得本地字节；没有重试或改入口绕取。正文在首次历史介绍处提供原图链接，不把链接算成本地图片，也不将延迟线照片冒称控制矩阵。未改变原图或复制未取得的内容。
