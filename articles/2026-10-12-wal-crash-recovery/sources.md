# 来源、素材与实验边界

正文与22张原创静态教学图、原创恢复动画采用CC BY 4.0。Jim Gray照片有独立的CC BY-SA 3.0 US许可，不由正文许可覆盖。实验代码按examples/README.md中的MIT许可。写作、代码和教学示意使用AI辅助，并通过实际运行、一手资料核查及非作者完整图文审读验证；自设数字与状态图不是数据库产品实测。

## 一手事实对应范围

1. Jim Gray，*The Transaction Concept: Virtues and Limitations*，VLDB 1981，144—154页。[原论文PDF](https://www.cs.utexas.edu/~dahlin/Classes/GradOS/papers/Gray81.pdf)。实际查阅首页144、日志与DO/UNDO/REDO相关149—150页原生扫描，以及151页有关提交恢复的文字段。用于1981论文身份、事务与日志恢复的历史背景；不声称全文逐页精读，不把WAL的全部发明归给Gray，也不把论文中的神话类比说成真实人物轶事。
2. C. Mohan、Don Haderle、Bruce Lindsay、Hamid Pirahesh、Peter Schwarz，*ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging*，ACM Transactions on Database Systems 17(1)，1992年3月，94—162页。[原论文扫描](https://www.cs.cmu.edu/~15849g/readings/mohan92.pdf)。实际原生核读94、97、104页，另查阅页LSN与重复历史的相关文本。94页支持作者、年月、重演历史及回滚记录；97页说明WAL先后依赖；104页定义steal/no-steal与force/no-force。本文没有实现完整ARIES，不把本篇简化的全日志重放说成其真实完整流程。IBM研究页面的书目信息可另查，但本次保存的网页只返回Site Unavailable提示，未用该HTML冒充论文正文。
3. [PostgreSQL 18：28.3 Write-Ahead Logging](https://www.postgresql.org/docs/18/wal-intro.html)。核读该页，用于日志先持久化再写数据文件，以及提交不必等待全部数据页写回的基本原理。引用版本固定为18，不借此描述PostgreSQL必须采用本文旧值/新值UNDO日志。本文也没有采纳该页文件系统设置建议或修改任何数据库配置。
4. [SQLite：Write-Ahead Logging](https://www.sqlite.org/wal.html)，重点第2节至2.3节、第4节。用于说明SQLite WAL的页内容追加、提交、检查点与文件保留是特定实现，不能与本篇steal模型混写。官方文档说明同步设置影响断电耐久性；本篇不据此给出配置推荐或宣称启用WAL就无条件耐久。
5. Tony Hey、Stewart Tansley、Kristin Tolle编，*The Fourth Paradigm: Data-Intensive Scientific Discovery*，Microsoft Research，2009年第二次印刷v1.1。[微软原书PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/09/4th_paradigm_book_complete_lr-1.pdf)。实际查看PDF第6页版权声明、PDF第268页/印刷234页Jim Gray照片，以及PDF第286页/印刷252页的准确照片署名。仅用于本篇采用照片的来源、身份、日期和权利链，不把整本书当作本文WAL技术来源。

## 原始论文图与公开素材范围

Gray原文149—150页图3、4、5涉及DO/UNDO/REDO、推迟实际动作和可重启操作，已实际查看。正文讨论的相关原图没有确认公开再分发许可，因此只链接原PDF，不复制到公开库；原文其他通信/两阶段提交示意不属于本篇核心讲解范围。

ARIES本文采用范围以摘要、WAL协议段和缓冲策略定义为主。原文其他完整恢复结构、日志链和协议图用于更完整算法，不能用本文简化图声称已复现。原论文未获本库再分发许可，仅提供查看链接。两份数据库官方说明在本篇使用段落中没有需要转载的正文信息图。

本篇唯一第三方图像是下列照片，确实取得并逐图查看了原书内嵌JPEG，不以页面截图、预览缩略图或AI重绘替代。

### Jim Gray照片：单独的权利说明

- 文件：[04-jim-gray-tenacious-original.jpg](assets/04-jim-gray-tenacious-original.jpg)。原书PDF内嵌JPEG，702×1003像素，95475字节；未重采样、未裁切、未调色、未添加字样。网页显示缩放不改变交付文件。
- 作品：*Jim Gray on Tenacious, January 2006*。摄影：Tony Hey；2006年1月。人物身份及图注由出版物明确标注。
- 来源：Microsoft Research上述原书，印刷234页照片，252页照片署名。书籍版权页声明除另有注明者外采用Creative Commons Attribution-ShareAlike 3.0 United States；此图的专门署名未另列Rights reserved。保留出版物的Copyright ©2009 Microsoft Corporation通知，以及此图Tony Hey摄影署名。
- 许可：[CC BY-SA 3.0 United States](https://creativecommons.org/licenses/by-sa/3.0/us/)，[完整法律文本](https://creativecommons.org/licenses/by-sa/3.0/us/legalcode)。再分发须保留适当署名、作品名、来源与许可；改编另须按许可履行相同方式共享及修改说明等要求。本库收录未改原图，不意味着Tony Hey、Gray或Microsoft认可本篇。
- 交叉核验：[Commons同作品文件说明](https://commons.wikimedia.org/wiki/File:Jim_Gray_on_Tenacious_2006.jpg)同样列Tony Hey、2006年1月及CC BY-SA 3.0 US。该站记录的图像是700×1001像素，本篇未把它与原书702×1003的嵌入文件混称为相同字节，也不声称取得相机底片或更高分辨率摄影原档。

## 原创模拟器的条件

[wal_lab.py](examples/wal_lab.py)只用Python标准库，实际在CPython3.12.14运行。它没有I/O持久化实现、数据库、网络请求或硬件断电操作。

假设：事务串行且编号不复用；上一笔提交日志持久化之后才运行下一笔；一次数据页写回完整；持久日志是完整前缀；保留从已知一致起点开始的完整日志；崩溃只删除易失状态；恢复期间没有其他访问。只实现正常写入、提交和崩溃恢复，不实现并发、主动回滚API、日志截断、媒体丢失或损坏检测。

- 主程序日志：T1把A100→70、B40→70并提交；T2把A70→80、B70→60，随后可以提交。主图崩溃点没有T2提交记录。
- 对该固定程序，枚举79个可达状态、156条合法转移。逐状态检查恢复与独立提交式参考状态相符；再在恢复每次页赋值之后模拟崩溃，共292个恢复中断点，重新执行仍正确。
- 初始两数与两次转移量分别遍历range(-2,3)，共625个程序、49375个可达状态。负值是算术测试，不是允许负库存的业务政策。
- 参考检查器维护事务私有写集，只在持久提交处发布；不使用持久数据页推测结果。可达状态记录两页写回的版本序号，因此数值碰巧相等的不同历史不被错误合并。
- 另有明确坏序反例：数据页先于日志持久化、成功承诺先于提交记录持久化；同一未提交事务连续改一页时，正序撤销给出错误结果。有限枚举不替代一般正确性论证。
- 动画由实际主例恢复轨迹生成：70/40、70/70、80/70、80/60、80/70、70/70。最终GIF实际6帧，每帧1500毫秒，循环；节奏只是便于阅读，不代表恢复耗时。

## 教学视觉索引

22张PNG与动画均是原创机制图；04是上列第三方照片。

|编号|教学任务|
|---|---|
|01|两页转移的半成品|
|02|内存与持久页的两个层次|
|03|原子性与持久性的不同承诺|
|04|有来源与单独许可的Gray真实照片|
|05|串行、页原子性、日志前缀等模型边界|
|06|两条修改与一条提交的顺序账|
|07|对应日志落稳之后才能写回数据页|
|08|持久提交之后才能确认成功|
|09|已提交页落后，需要REDO|
|10|未提交页先写回，需要UNDO|
|11|T1提交与T2未提交混在持久页上|
|12|按日志顺序重做四次赋值|
|13|倒序撤销T2的两次赋值|
|14|同一页连续修改时正序撤销的反例|
|15|简化恢复函数的输入输出合同|
|16|恢复再崩溃时保留完整证据|
|17|赋值与重复业务扣减的区别|
|18|steal与force两开关带来的恢复责任|
|19|真实ARIES超出本模型的机制|
|20|主例五个实际可达状态的分支，非79点完整图|
|21|实际有限验证范围与坏顺序反例|
|22|持久提交与客户端看到回复之间的间隙|
|23|媒体毁坏、并发等不在本模型内|
|24|主例完整六次恢复赋值动画|
