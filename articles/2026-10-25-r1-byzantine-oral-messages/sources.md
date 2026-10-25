# 来源、模型与图像权利

## 事实来源

1. Leslie Lamport, Robert Shostak, Marshall Pease, [The Byzantine Generals Problem](https://lamport.azurewebsites.net/pubs/byz.pdf), *ACM Transactions on Programming Languages and Systems*, 4(3), July 1982, pp.382–401。原件总计20页，**本次可用于核对的材料仅为若干实际返回的文字窗口，不是全文20页**：pp.382—385及p.386开头的问题定义、IC1/IC2、三人不可区分性解释和分组归约；p.386的近似时间问题开头；p.390的有效性引理与部分归纳证明；pp.394—395的一般图推广算法局部步骤；p.398关于可靠传送、直接来源识别及缺报假设开头的片段。其他段落不能作为本次已核读证据，尤其口信完整算法定义、一般定理完整证明、签名算法细节和同步时间界讨论。本文的递归构造、消息计数与一般正确性解释由教学推导和独立实现展开，不声称原文相应段落已经全部逐行核对。
2. [Leslie Lamport: My Writings，条目46](https://lamport.azurewebsites.net/pubs/pubs.html#byz)：另行核对作者、期刊、年月、页码与ACM权利通知。该页关于研究背景的叙述属于作者回忆；正文没有把回忆扩写成历史故事。官网通知明确网络转载不属于一般个人/课堂复制许可，不能把公开可读视为CC授权。

访问边界：直接下载原PDF返回403，未取得文件；现已停止该原件、同论文镜像和原图像素获取。未核读范围不能用页数元数据或片段之外的推测补齐，已获得的局部文字也不等于原图像素检查。本文未重新分发原论文或图版；相关视觉库存与未核范围见[source-visual-inventory.md](source-visual-inventory.md)。

## 新图的身份与理解作用

以下所有PNG均为本篇新制作，宽1062像素。00为独立封面，01—15为原创解释图或Python同步模型输出可视化，16为默认Chromium显示本篇真实只读教学报告的截图。不是第三方软件界面、军事实拍或真实分布式网络测量。具体元数据见[figure-metadata.json](examples/figure-metadata.json)。

|文件|新增的理解作用|数据与身份|
|---|---|---|
|00-cover.png|给出坏指挥官分裂消息与忠诚者统一结果的任务|bad_c，原创封面|
|01-channel.png|直接sender识别不等于转述可验证|原创信道结构示意|
|02-bad-first.png|列全坏C第一轮三条定向消息|bad_c.events|
|03-bad-relays.png|列全第二轮六条定向转述|bad_c.events|
|04-bad-vectors.png|三位接收者有序向量和自己直收项|bad_c.top|
|05-majority.png|实际一进二退计数和固定默认规则|bad_c.top.counts，点数读数据|
|06-good-commander.png|好C的首轮及坏D分别发送的不同值|good_c.events|
|07-good-vectors.png|整行不同但忠诚来源两列保留原命令|good_c.top|
|08-missing.png|截止前未到与截止后缺报归一的区别|missing，时间线不按实测时长绘制|
|09-recursion-tree.png|OM2局部路径、参与者移除、OM0停止|higher.events，虚线只展开同一节点|
|10-honest-subtree.png|把忠诚A的子问题输出填回顶层A列|higher.reductions，C/A子问题|
|11-faulty-subtree.png|坏B子问题中忠诚者获得相同列值|higher.reductions，C/B子问题|
|12-top-reduction.png|五位忠诚者顶层完整向量的三比三平票|higher.top|
|13-growth.png|共同尺度展示单次广播的真实消息槽计数|growth.slots；条长同轴从数值计算|
|14-three-worlds.png|三个世界中A、B各自的不可区分初始观察|worlds输入与程序计算视图；非任意协议的测试证明|
|15-guarantees.png|一般正确性为何必须分成两类指挥官|原创逻辑结构示意|
|16-live-report.png|实际主例、槽数、有限测试和越界失败结果|Python 3.12.14生成JSON，Chromium真实localhost截图|

## 复算与限制

执行实现、固定故障策略、三值穷举范围、各独立随机种子及消费顺序、消息计数口径见[examples/README.md](examples/README.md)。结果值从[results.json](examples/results.json)读取；没有把手写结果伪装成实算。83组四人验证和100组七人测试只检验有限模型，不是一般正确性证明、生产性能测量或真实攻击评估。截屏报告展示实际数值，不把测试通过等同于协议实现可部署。

## 许可与AI辅助

本文正文与全部原创PNG由zyuanming发布，采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。转载应署名、链接文章和许可，并注明修改。`examples/`中的原创Python、HTML及自产JSON采用[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)。正文中的论文名称、事实引用和第三方材料权利仍属各自权利人；未复制原论文PDF、图版、照片或界面，CC BY 4.0不向第三方材料扩张。

本篇使用AI辅助结构设计、中文撰写、算法实现、绘图、资料核对与自检；示例程序实际执行，报告实际在浏览器加载。没有生成或冒用历史照片，没有虚构作者亲测经历。作者自检与后续独立审读是不同步骤，不把自检结果称为独评结论。
