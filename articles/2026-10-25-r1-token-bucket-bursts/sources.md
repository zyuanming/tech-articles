# 来源、复算与许可

## 核心事实

Y. Bernet、S. Blake、D. Grossman、A. Smith，**An Informal Management Model for Diffserv Routers**，RFC 3290，May 2002，Informational。[原文入口](https://www.rfc-editor.org/rfc/rfc3290.txt)。

§3.3区分计量、处置和队列；§5.1.3区分严格与宽松令牌桶；附录A.2给出任意区间B+R×t的界；附录A.4明确满初值、截顶补充、完整包扣款、拒绝保持额度，并讨论发送资格时刻。本文从这些规则出发独立编写单桶模型，并重新构造A–I例子。FIFO排队的具体政策、固定窗边界、并发交错、连续流体耗尽计算是本文明确指定输入与假设的教学推导，不冒充RFC的原算例或现成生产实现。

本次可用的是原文返回的部分文本与ASCII，非完整原件或原站像素。随后原TXT下载403，未取得文件并停止该原件获取；准确已核/未核范围及所有已见相关视觉项的采用/排除理由见[来源视觉库存](source-visual-inventory.md)。没有把搜索摘要、总页数或未访问参考文献当成全文证据。

## 数值和真实运行

所有例子确定性，无随机种子。`examples/model.py`用Fraction表示精确有理数；`run_examples.py`产生逐事件前后额度、FIFO资格时间、空闲曲线、预算上界、流体曲线、固定窗判断和并发读改写交错；`results.json`为实际输出。并发反例的放行数从两次真实判定求和，不是手写成功数。

独立有限对照：四次到达依次0、1/4、1/2、3/4秒，费用1至7的全部7^4=2401种序列，用整数半额度时钟逐步补充和扣费，对照有理数实现。另对监管6个、整形8个放行事件的全部连续子序列，检查21+36=57个区间界。预算守恒推导承担一般性论证，有限枚举不承担普遍正确性证明。

图15来自真实Chromium打开原创本地教学HTTP应用，点击按钮，POST调用Python `run()`重执行模型，浏览器显示响应后截图。实际检查1062宽和354宽：响应等于复现JSON、没有脚本/响应错误、没有页面横溢，文字框/字号/字形/像素检查通过。图15公开的是1062宽截图；不能把手机缩略代理称为实际手机浏览器。它不是Linux tc、网络链路或生产API实测。

原创PNG通过字形cmap、字号、文字出界/越框/相交、对比和墨迹像素、实际PNG尺寸检查。数量驱动几何从JSON取得，柱条共轴；固定布局坐标和轴刻度为版式选择。原ASCII图的完整英文许可为22px证据附注，原ASCII为37px以保留边距（手机约12.3px），中文解释40px以上；不以小字附注替代正文解释。检查元数据见 `examples/figure-metadata.json`，复现方法见[示例说明](examples/README.md)。

## 逐图身份与用途

| 文件 | 新增理解作用 | 数值或素材来源 | 权利 |
|---|---|---|---|
| [00-cover.png](assets/00-cover.png) | 独立封面：并置短时额度与长期补充速率 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [01-two-paths.png](assets/01-two-paths.png) | 分清数据包路径与虚拟额度账本，统一单位 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [02-same-time.png](assets/02-same-time.png) | A/B/C三步用同轴库存条逐一展示同刻顺序和不补充 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [03-refill-steps.png](assets/03-refill-steps.png) | D/E/F逐步补充与拒绝不扣费，用同一时序算出每个前后值 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [04-token-trace.png](assets/04-token-trace.png) | 实际模型所有事件的额度折线与接受名单对照 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [05-idle-cap.png](assets/05-idle-cap.png) | 无消费空闲曲线显示达上限后继续等待不会额外积存 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [06-window-budget.png](assets/06-window-budget.png) | 共同长度单位可加的两来源预算；推导任意区间界 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [07-long-average.png](assets/07-long-average.png) | 不同时间尺度共轴比较平均上界，区分长期与短窗 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [08-fluid-burst.png](assets/08-fluid-burst.png) | 流体近似下B/(p-r)耗尽时间，显式不同于原子扣包 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [09-police-shape.png](assets/09-police-shape.png) | 同一输入两种动作的实际到达至放行时间线，标超大包 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [10-fifo-wait.png](assets/10-fifo-wait.png) | F实际等候分为队前等待与队首缺额等待，长度从结果计算 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [11-size-initial.png](assets/11-size-initial.png) | 费用超过B与初始余额不足的不同后果，初值同轴比较 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [12-fixed-window.png](assets/12-fixed-window.png) | 固定窗跨边界四请求反例，和明确另设B2的桶比较 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [13-atomicity.png](assets/13-atomicity.png) | 两个调用读同一余额的具体交错，指出原子边界 | 本篇results.json；布局参数为原创设计 | zyuanming，CC BY 4.0 |
| [14-rfc-meter.png](assets/14-rfc-meter.png) | 保留相关原始ASCII图及完整许可，说明测量结果与后续动作分开 | RFC3290 Fig4已有ASCII转录；中文解释为本篇新增 | Internet Society (2002)原通知；不适用本文CC BY 4.0 |
| [15-model-live.png](assets/15-model-live.png) | 展示真实可复现输入输出与独立检查，不是tc或网络设备实测 | 本篇教学网页实际响应；Python版本和数据见JSON | zyuanming，CC BY 4.0 |

## 授权与AI辅助

正文、图00–13、图15原创界面截图：zyuanming，采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，转载须署名、链接原作及许可并标明修改。代码、原创模型JSON与元数据采用[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/)。前两篇允许复用的CC0 Canvas API只复用绘图检查机制，未复用旧稿正文、旧图或旧主题的构图。

ChatGPT参与资料阅读、教学组织、中文草稿、模型与绘图代码生成和作者自检。数值由本次实际执行的程序得到，图15是实际网页运行截图，不是生成式模型伪造的软件界面。本篇没有人物或设备照片，也未生成伪实拍。

第三方RFC图14为原ASCII文字转录后的渲染，保留图中标签与连线，移除共同左缩进；新增中文标题说明、排版和下面完整原通知。未修改原文结论，也不声称复原原站截图。原ASCII转录在 `originals/rfc3290-figure4.txt`，完整版权及许可同时放在该文件、图14底部和PNG文本元数据中。本仓库不把这些材料再次授为CC BY或CC0。

## RFC原文完整版权声明

Copyright (C) The Internet Society (2002). All Rights Reserved.

This document and translations of it may be copied and furnished to others, and derivative works that comment on or otherwise explain it or assist in its implementation may be prepared, copied, published and distributed, in whole or in part, without restriction of any kind, provided that the above copyright notice and this paragraph are included on all such copies and derivative works. However, this document itself may not be modified in any way, such as by removing the copyright notice or references to the Internet Society or other Internet organizations, except as needed for the purpose of developing Internet standards in which case the procedures for copyrights defined in the Internet Standards process must be followed, or as required to translate it into languages other than English.

The limited permissions granted above are perpetual and will not be revoked by the Internet Society or its successors or assigns.

This document and the information contained herein is provided on an "AS IS" basis and THE INTERNET SOCIETY AND THE INTERNET ENGINEERING TASK FORCE DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL NOT INFRINGE ANY RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.
