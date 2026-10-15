# 来源、器件照片与模型边界

查阅日期：2026-10-13。

## 核心问题与去重

本篇回答：串行超声脉冲怎样通过传播时延、检测再生与回送持续存储；怎样按管和时隙找到一个字；温度与反射为何影响可靠性。

已定点复读旧稿[《计算机的内存，曾经是一张穿满小铁环的网》](https://zyuanming.github.io/tech-articles/articles/2026-10-09-core-memory-woven-bits/read.html)。旧稿以磁化方向、重合电流选址、破坏性读出、位平面与磁芯绳区别为核心。本稿不重写这些机制，只有访问方式的一处简短对照。

本篇读者只需认识0、1与加减乘除。先讲位、脉冲和时隙，再介绍换能器、时钟、再生、字和等待时间。贯穿小例10110010被分成A=1011与B=0010；八个2微秒时隙构成16微秒的教学环，不是历史EDSAC的字长或容量。

## 事实来源及其证据层级

1. [剑桥The Relics Project馆藏数据库，EDSAC I筛选](https://www.cl.cam.ac.uk/relics/database/?machine=EDSAC+I)。原始研究机构保存的实物与David Wheeler回忆性解说：CL-4/97短延迟线，外形274×50×50毫米、约35位、电—声—电转换、检波、时钟控制回送、2微秒间隔、约1微秒包宽、约13.5 MHz载波、石英与水银匹配、短管反射处理、温控方案；CL-25/97为恒温控制器；CL-2/97说明电路机架具体用途未知。数值中的“约”及回忆身份保留；外形尺寸不冒称有效声程。馆藏编号的97是入藏/建档年份，不是制造年份。
2. [The start of the EDSAC log](https://www.cl.cam.ac.uk/relics/elog.html)。William S. Renwick当时所写日志，由David Wheeler转录。1949-05-06日条记0—99平方表、2分35秒、第一组四根tank运行。注释把一组定义为16根，每根16个35位长字。正文首日128短字/64长字为按4根与每管容量推算，不冒称原日志逐字写有128；不把通常的初期512短字全配置套到首日。后续调试日条也显示扩充与接线是过程。
3. [Some EDSAC statistics](https://www.cl.cam.ac.uk/events/EDSAC99/statistics.html)。剑桥1999年纪念资料汇编：引述Wilkes与Renwick的1949年报告说明每根32个17位数、32管共1024短字、相邻位置可组成35位数；短管作算术/控制状态用途；二组各512短字、第二组1952年启用。它是机构汇编并含原文摘录，不冒称本次读到1949报告的完整原版。本文不使用该页指令吞吐量计算来代替存储访问时间。未进一步把扩充启用年份等同于所有管子无故障满容量的可靠运行年份。
4. [Echo EDSAC Simulator用户与参考说明，第5.3—5.4节](https://www.cl.cam.ac.uk/events/EDSAC99/simulators/echo/flat.html)。剑桥托管的现代模拟器文档，支持18位置与17位有效字、35位长字和夹心位的区别。它不是原机测量记录。本篇没有安装或运行Echo，亦未把现代界面当作历史设备照片。
5. [EDSAC Architecture](https://www.cl.cam.ac.uk/events/EDSAC99/simulators/india/arch.html)。剑桥托管的另一份模拟器架构说明，支持主存32根、每根576个循环时序位置、每36位置中一个位置用于间隔的说明。该页把后期完整配置概述为512个35位长字，不足以证明首日容量；本文与日志分阶段核对。有关反射的器件差异采用CL-4/97的具体回忆，不把该架构页泛化描述套到所有长管。
6. [David Wheeler：The EDSAC Order Code, Explanatory Notes](https://www.cl.cam.ac.uk/relics/orders.notes.html)。参与者对1949指令格式的回忆，确认17位短存储位置与指令长度；本篇没有扩展成指令集教程。
7. [剑桥Archive photos](https://www.cl.cam.ac.uk/relics/archive_photos.html#EDSACI)。照片的题名、身份与有明确标注时的拍摄日期来源。1947实验台、1948机房、Wilkes与管组、日志页具有不同视觉职责；不把不同阶段照片混成首日现场。未标准确日期的Wilkes照片不自行补日期。

华威的《Tutorial Guide to the EDSAC Simulator》2021年版曾通过检索服务读到相关说明；直接本地取PDF时收到403，已停止该入口，没有改路下载、安装软件或补造原件。本稿的事实链使用上面已列可核资料，不附该PDF、不宣称完成该PDF逐页核读。剑桥statistics页面可由检索服务读取，本地下载曾遇502；未把网络失败视为史料不存在。

## 哪些数字是我们的推导？

- 八个时隙×2微秒=16微秒，是缩小教学环；每个四位字占8微秒。
- B开头的相位是8微秒，每16微秒重现。请求3→开始8→收齐16；请求9→开始24→收齐32。收齐按整个最后时隙结束计，不声称末位只能在结束瞬间才被检测到。
- 均匀相位下平均等待开头为半圈；没有把这条理想结论当作请求分布、CPU调度、指令执行或真实设备响应的保证。
- 32×18=576时序位置；每位置2微秒给出1152微秒。它是位节拍与队列的计算，不是拿外壳长度反推声速，更不是单条指令耗时。
- 32×17=544有效位（全部短格式）；16×35=560有效位（全部长格式）。两种计数不能与时序位置数混用。
- 四根运行管对应4×32=128短字位置；第一完整组16×32=512；两组32×32=1024。首日推算不是首个程序的实用占用量。
- 声程/声速和有限波传播、信号阈值、相位错位的图，属于独立教学推导。没有给出未经核实的水银声速、温度系数、容许温差、实际电压或真实故障率。

## 原链接图像范围及逐图权利

馆藏筛选页有日志本封面、机架三视图、短延迟线、温控器、电子管提取器、纸带和其他器物。本题保留直接参与存储机制说明的短管、机架正面与背面、温控器；机架电子管局部作为补充源文件留存并在下表链接，不充当新增正文图。日志本封面由更有证据意义的日志第一页替代。纸带、喇叭、纸带接合器、磁芯测试器等不承担本篇核心问题，未为了图数全塞入正文。页面导航和重复缩略图不算信息图。

Archive photos是覆盖多台机器与多年的长目录。选用EDSAC I相关的实验存储台、1948年机房、Wilkes与管组、日志第一页四张；排除重复人物姿态、无关机器、磁带、纸带和后来的EDSAC II。原始尺寸下载，不把站内缩略图再放大冒称高清。既有照片不裁切，不增补、不生成历史细节。

两套许可必须分别看：

- [Relics默认许可](https://www.cl.cam.ac.uk/relics/#copyrightandlicense)：下级页未另列时，CC BY 4.0。馆藏器件图片适用此项；[原站完整许可文件](https://www.cl.cam.ac.uk/relics/Computer-Lab-Creative-Commons-CC4BY-LICENSE.txt)副本在[licenses/cambridge-CC-BY-4.0.txt](licenses/cambridge-CC-BY-4.0.txt)。
- [Archive photos下级版权段](https://www.cl.cam.ac.uk/relics/archive_photos.html#Copyright_Licencing)：明确链接CC BY 2.0 UK，因此这四张历史照片保留该许可，不能用上级默认条款冲掉下级专列许可。[完整法律文本](https://creativecommons.org/licenses/by/2.0/uk/legalcode)的本地副本在[licenses/CC-BY-2.0-UK.html](licenses/CC-BY-2.0-UK.html)。

馆藏器件照片署名：© University of Cambridge Computer Laboratory。
历史档案照片保留原站所要求的署名：Copyright Department of Computer Science and Technology, University of Cambridge. Reproduced by permission.

| 本地原件 | 原文件与许可 | 身份及新增理解作用 |
| --- | --- | --- |
| [short-tank-original.jpg](assets/short-tank-original.jpg) | [CL.4-97.jpg](https://www.cl.cam.ac.uk/relics/jpegs/CL.4-97.jpg)，CC BY 4.0 | 开篇看真实短管与尺度，再区分短管与主存长管 |
| [chassis-front-original.jpg](assets/chassis-front-original.jpg) | [CL.2-97.jpg](https://www.cl.cam.ac.uk/relics/jpegs/CL.2-97.jpg)，CC BY 4.0 | 回送与再生需要真实电子电路；具体原用途未知 |
| [chassis-back-original.jpg](assets/chassis-back-original.jpg) | [CL.2-97.back.jpg](https://www.cl.cam.ac.uk/relics/jpegs/CL.2-97.back.jpg)，CC BY 4.0 | 看见正面看不到的元件与连接，不把它识别成已知检波电路 |
| [chassis-detail-original.jpg](assets/chassis-detail-original.jpg) | [CL.2-97.detail.jpg](https://www.cl.cam.ac.uk/relics/jpegs/CL.2-97.detail.jpg)，CC BY 4.0 | 补充可查看的电子管局部，未计入正文图 |
| [thermostat-original.jpg](assets/thermostat-original.jpg) | [CL.25-97.jpg](https://www.cl.cam.ac.uk/relics/jpegs/CL.25-97.jpg)，CC BY 4.0 | 把时延同步问题落实到真实温控器 |
| [experimental-tank-1947-original.jpg](assets/experimental-tank-1947-original.jpg) | [edsac99.23.jpg](https://www.cl.cam.ac.uk/relics/jpegs/edsac99.23.jpg)，CC BY 2.0 UK | 1947年6月实验台，说明延迟线与电子设备一起发展 |
| [wilkes-long-tanks-original.jpg](assets/wilkes-long-tanks-original.jpg) | [delay_lines.jpg](https://www.cl.cam.ac.uk/relics/jpegs/delay_lines.jpg)，CC BY 2.0 UK | 主存管成组安装，与开篇短管形成物件尺度、用途对照 |
| [log-page-original.jpg](assets/log-page-original.jpg) | [edsac99.30.jpg](https://www.cl.cam.ac.uk/relics/jpegs/edsac99.30.jpg)，CC BY 2.0 UK | 第一手日志页，支持阶段意识；用转录辅助释读小字 |
| [edsac-room-1948-original.jpg](assets/edsac-room-1948-original.jpg) | [edsac99.9.jpg](https://www.cl.cam.ac.uk/relics/jpegs/edsac99.9.jpg)，CC BY 2.0 UK | 1948年6月机房，把小器件放回整台机器背景 |

## 原创视觉的逐节职责

正文共22个图像引用：14张原创机制图、8张真实历史/馆藏照片。另有独立封面、1张仅供补充查看的机架局部原件。照片正反面、同图面板与模型样本均不拆分吹大图数。图数只是文件核对信息，配图按照解释需求选择。

| 原创图 | 解释职责 |
| --- | --- |
| 01-bits-and-slots.png | 有脉冲与空时隙如何共同表示10110010 |
| 02-electric-sound-electric.png | 石英换能器的电—声—电三步转换 |
| 03-propagation-delay.png | 传播时间的来源，不把波误解为液体整体流动 |
| 04-regeneration-loop.png | 检波、时钟再生、回送/写入的完整闭环 |
| 05-regenerate-not-amplify.png | 阈值判定可抑制形变，但不能恢复已越过错误门槛的位 |
| 06-time-ring.png | 同一串八位在五个时刻的读口顺序；一圈后恢复 |
| 07-tank-and-time-address.png | 选管与等待字两层寻址 |
| 08-wait-for-word.png | 同一B在不同请求相位下的等待与接收时长分开 |
| 09-overwrite-one-word.png | 在回送交接点定时替换B，其余时隙继续保持 |
| 10-short-and-long-words.png | 17/18/35/36的容量与时序计数，夹心位的来源 |
| 11-capacity-stages.png | 首日运行、第一组完整配置、第二组启用分开 |
| 12-temperature-and-timing.png | 脉冲到达与时钟窗口错位，不冒称实际温漂曲线 |
| 13-reflection-is-not-feedback.png | 多次反射的干扰与受控电反馈不是同一回事 |
| 14-access-comparison.png | 顺序经过读口与按地址直接选择单元的区别 |
| cover.png | 独立入口封面，画波包与回送路径，不假装历史实拍 |

原创图宽720像素，关键字一般27—36像素，少量次级说明25像素。按354像素正文宽度缩放，对应关键字约13.3—17.7像素、最小说明约12.3像素。历史原件尺寸与清晰度按实物保留；手写日志用正文中文解释，不以放大原件替代教学图字号要求。

## 实际计算和复现范围

[delay_model.py](examples/delay_model.py)是独立写作的标准库Python模型。运行环境Python3.12.14，无随机数。核心是长度8的队列：每时隙读出队首，把保留位或新位追加到队尾。事件时间、槽序号、读值、送回值全部保存于[results.json](examples/results.json)。

检查包含：8000组下一次字开头计算；三个循环读出；关闭反馈后填零；在第一圈B时隙替换、下一圈读到更新；阈值正确恢复和阈下错误反例。真实历史EDSAC没有在本次任务中运行，模型没有实现电子管逻辑、声波衰减、频散、容差、写入控制建立时间或CPU忙碌状态。

[build_figures.py](examples/build_figures.py)使用Pillow12.3.0和环境已有Noto Sans CJK字体，读取同一results.json产生全部原创图。无外部图片生成服务、没有复制他人机制图。绘图脚本不处理历史照片。图内的“机械包络”、时间窗和空隙块是功能示意，不能当成历史实际电路波形或物理尺寸图。

## AI辅助与许可

本篇使用AI辅助资料检索、史料核对、原创写作、编程、计算、制图和排版检查。没有声称亲历机房、亲自拍摄、采访历史人物或测量原机；没有生成伪历史照片。照片原件来自已列剑桥源。

原创正文、原创教学图、封面、两个原创脚本和模型数据明确按CC BY 4.0提供。代码许可在本篇单独声明，不靠“正文开放”推定代码授权。第三方照片分别保留CC BY 4.0或CC BY 2.0 UK与原署名；网页、论文等其他原内容仍归各权利人。[原创作品许可说明](licenses/ORIGINAL-WORKS.md)。
