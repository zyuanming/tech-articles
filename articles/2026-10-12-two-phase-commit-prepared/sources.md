# 一手来源、模型与原图说明

本篇原创中文正文、23张原创PNG与原创11帧动画采用CC BY 4.0；两张第三方照片分别保留自身许可，不能套用正文许可。实验程序采用examples/README.md所列MIT。文本、代码和教学图使用AI辅助，经过实际运行、一手核查与非作者独立完整图文审读；剑、宝石、入场券和甲乙库都是虚构教学对象。

## 论文与官方事实

1. Jim Gray、Leslie Lamport，*Consensus on Transaction Commit*，ACM Transactions on Database Systems 31(1)，2006年3月，133—160页。[微软官方论文入口及Lamport回忆说明](https://www.microsoft.com/en-us/research/publication/consensus-on-transaction-commit/)，[作者技术报告修订版PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2004/01/consensus-on-transaction-commit.pdf)。本次取得的37页PDF首页列MSR-TR-2003-96、2004年1月1日，以及2004/2005/2017修订日期；采用报告内部页码与期刊页码分开描述，不把2017修订说成2006原排版。
2. 实际原生查看报告封面、内部1—3页、5—7页和26—28页，对应PDF1、4、5、6、8、9、10、29、30、31页。内部1—3页用于故障模型、状态和安全性；5—7页用于2PC过程、持久顺序、消息与阻塞；26—28页用于附录仅检查安全性、忽略询问/NO优化消息及“曾发送消息集合”的模型范围。另按文本核查相关上下文，未声称37页全文逐页精读，也不声称本文实现Paxos Commit。
3. 论文入口页上的研究经过按Lamport本人回忆处理。正文只简述两位作者曾一起比较传统2PC与Paxos的关系，不添加虚构对白、地点、心情或首创归属。
4. [PostgreSQL 18 PREPARE TRANSACTION](https://www.postgresql.org/docs/18/sql-prepare-transaction.html)，核读Description与Notes：准备状态持久化、随后提交或回滚、外部事务管理器的用途、仍持锁及遗留风险。[18版Two-Phase Transactions](https://www.postgresql.org/docs/18/two-phase.html)补充WAL与跨检查点准备事务的记录方式。本篇不运行这些接口，不改配置，也不提供未经查证整体决定的清理操作。

5. [CMU 15-445/645 Fall 2019两阶段锁课程讲义](https://15445.courses.cs.cmu.edu/fall2019/slides/17-twophaselocking.pdf)，实际查看印刷幻灯片13（PDF第21页），支持锁的增长/收缩阶段与2PC是不同问题的简短术语辨析。未转载讲义图，不声称完整课程已读。

正文普通流程从协调者向所有参与者询问开始；原论文图2从某参与者主动准备开始，二者的消息起点并不相同。本文未用原论文3N−1消息计数套到自己的画法，也没有把图示等待间隔当作真实性能。

## 原始信息图范围

上述报告内部第3页图1是资源管理器状态图，第5页图2是正常2PC消息流，都已实际查看，是本篇直接相关的两张原始图。原件版权页要求公开再发布另获许可，本文不转载这两张原图，只提供原PDF链接；本文状态和时序图是为自设交换例子重构的机制讲解，不声称原图文件已经公开备份。

原报告Paxos、Paxos Commit的后续图及详细规格不属于本篇展开范围，没有用原创示意掩盖它们未转载。PostgreSQL所引用段落未含需要转载的正文信息图。

## 两幅原照片

### Leslie Lamport

[04-leslie-lamport-original.jpg](assets/04-leslie-lamport-original.jpg)，393×500像素、39002字节，来自[本人网站原JPEG](https://lamport.azurewebsites.net/leslie.jpg)。本次正常读取作者原URL，取得文件与本库已有原照逐字节相同，完整保留，没有裁切、放大重采样或重绘。

[Commons精确文件说明](https://commons.wikimedia.org/wiki/File:Leslie_Lamport.jpg)保存2004年本人答复的公开许可记录：允许对本人网站此照片及后来替换的新照片作任意用途使用，记录为copyrighted free use。这里按本人许可使用，并保留Leslie Lamport及来源署名；不标作CC、公共领域或无版权。拍摄具体日期未确认，不把网页上传时间说成拍摄时间，也不把照片说成合作论文现场。

### Jim Gray

[05-jim-gray-original.jpg](assets/05-jim-gray-original.jpg)，702×1003像素、95475字节，是[微软原书The Fourth Paradigm](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/09/4th_paradigm_book_complete_lr-1.pdf)PDF第268页/印刷234页内嵌的完整JPEG，直接提取，未裁切、未重采样、未改色。

作品名：*Jim Gray on Tenacious, January 2006*；摄影Tony Hey，2006年1月。原书印刷252页/PDF286页列准确署名；PDF6页版权声明：除另有注明外采用CC BY-SA 3.0 United States，此图专门署名没有另列Rights reserved。保留Copyright ©2009 Microsoft Corporation出版物通知与Tony Hey摄影署名。

许可：[CC BY-SA 3.0 US](https://creativecommons.org/licenses/by-sa/3.0/us/)，[完整法律文本](https://creativecommons.org/licenses/by-sa/3.0/us/legalcode)。复用须保留适当署名、作品名、来源与许可，改编须另遵守相同方式共享与修改说明等适用义务；收录不表示本人、摄影师或出版社背书本文。本文原创内容许可不覆盖这幅照片。

[Commons同作品说明](https://commons.wikimedia.org/wiki/File:Jim_Gray_on_Tenacious_2006.jpg)交叉支持摄影者、日期与CC BY-SA 3.0 US。其700×1001文件与本篇702×1003内嵌文件不是同一字节版本，不混称。本篇使用的是已经合法取得的原书图像，没有绕过访问限制。

## 原创实验与可核范围

[examples/two_phase_lab.py](examples/two_phase_lab.py)只用Python标准库，在CPython3.12.14实际运行。没有真实数据库、网络、锁管理或文件持久化。每次持久状态转移视为原子动作；准备落稳与发送YES、决定落稳与发送决定分别建模，因此包括持久化后尚未发送的状态。

- 一笔事务，参与者名单预先固定；状态W/P/C/A分别为工作中、已准备、已提交、已撤销。协调者决定未定/C/A。编号与消息身份在整个运行中不复用。
- 发过的YES与已收到YES用参与者集合表示，最终决定发送用布尔值表示。消息“曾经发过”不等于必将被收到；接收可以永远不发生。这个抽象用于安全性，不是消息队列实现或活性保证。
- 节点失效抽象为暂停动作，恢复从持久状态继续；不描述磁盘毁坏、伪造消息、成员变动、协调者并发选主或永久丢失持久状态。
- 正确规则下，n=1/2/3/4分别有20/104/602/3668可达状态，27/224/1818/14388条非自环转移。每步核参与者与协调者最终决定不反转，没有同时出现C和A；协调者决定C时，所有参与者均处于P或C。
- 分别核7/58/471/3812个按已见身份重复计票不增加票数的集合检查。重复最终决定由终局状态的幂等忽略表达，没有模拟重复消息的实际通信成本。
- 三个独立错误版本，分别允许P超时撤销、P自行提交、三人多数YES即提交。广度优先搜索实际找到三条有限反例，事件序列由程序打印，不是假想的运行结果。
- 正常例子从初始到全部提交共11个记录状态。第9个状态是协调者发送COMMIT，第10个B提交，第11个A提交。动画据该实际轨迹生成，每帧1300毫秒，仅是展示节奏。
- 两个相同参与者观察的隐藏世界：A/B均P，YES已发并已收齐，协调者持久决定分别C或A，均尚未发送。冻结协调者后，正确规则下参与者没有可自行动作改变的状态；这是特定阻塞现场，不是说所有协调者故障都让任何事务永久阻塞。

代码中的`timeout_action`仅接受W/P/C/A四状态，返回说明文字而非执行数据库操作。有限枚举不是一般活性证明；本篇也没有调用论文的TLA+模型检查器，不能把作者当年的TLC结果冒充本次运行。

## 26项视觉的职责

|编号|解释任务|
|---|---|
|01|两个本地正确决定仍可能拆开交换|
|02|协调者和资源管理器的逻辑角色|
|03|等待与相反终局的区别|
|04|Lamport本人网站完整照片|
|05|Gray原书完整照片|
|06|prepared需保存实际承诺条件|
|07|持久准备先于YES|
|08|第一阶段请求与身份答复|
|09|重复消息不能增加参与者票数|
|10|持久决定先于发送|
|11|同一提交决定的通知可先后到达|
|12|NO导致整体撤销的示意|
|13|相同本地观察、相反隐藏决定|
|14|超时自撤销导致矛盾终局|
|15|自行提交也可能与另一方冲突|
|16|多数资源不能替代全员资源|
|17|可靠最终证据与只有prepared的区别|
|18|协调者恢复后继续同一决定|
|19|超时规则取决于状态|
|20|枚举模型五类持久与消息信息|
|21|真实prepared可能继续占用锁|
|22|原子提交与隔离问题的边界|
|23|2PC、2PL与共识不能按名字混淆|
|24|实际有限枚举数量与三个坏版本|
|25|最后提交通知未达的练习|
|26|正常路径11个实际状态动画|
