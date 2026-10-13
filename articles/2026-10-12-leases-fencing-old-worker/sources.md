# 来源、素材与模型范围

原创中文正文、22张教学PNG和8帧动画采用CC BY 4.0。两张原作者信息图单独采用其来源页CC BY 3.0，不套用正文许可。程序按examples/README.md中的MIT许可。写作、程序与教学示意使用AI辅助；数值实际执行，最终交非作者完整独立图文审读，未审不作为完成稿公开。游戏记分、A/B、100/110/120与41/42都是自设例子，不是现场事故复盘。

## 一手来源与支持范围

1. Mike Burrows，*The Chubby lock service for loosely-coupled distributed systems*，7th USENIX OSDI，2006。[Google正式书目](https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/)，[Google原PDF](https://research.google.com/archive/chubby-osdi06.pdf)。本次正常取得117687字节、16页原文件；原生实读PDF第1、4、5、7页。第1页支持服务目标与工程背景；第4–5页第2.3/2.4节支持锁代号、advisory lock、sequencer三项内容与接收方检查；第7页第2.8节用于租约和会话语境。没有声称完整16页精读。
2. Martin Kleppmann，[How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)，2016-02-08，含2016-02-09更新。实际核“Protecting a resource with a lock”和“Making the lock safe with fencing”、两幅信息图、文末书籍来源说明与网站许可。正文只用其暂停/迟到请求/资源端代号思想和历史日期，不沿用旧软件版本的时间实现断言，不转述GC具体事件为本次实测，也不对当年的Redlock争论作今日产品结论。
3. Flavio Junqueira，[Note on fencing and distributed locks](https://fpjdotme.wordpress.com/2016/02/10/note-on-fencing-and-distributed-locks/)，2016-02-10。实际完整读正文，重点“Getting shared resources involved”中资源先建立epoch与拒绝旧写入、“Distributed resources”中多接收点问题。本文不把当年Kafka/ZooKeeper实现细节套到现版，也不实施文中的生产配置。
4. [Hazelcast 5.5.0 FencedLock官方Java API](https://docs.hazelcast.org/docs/5.5.0/javadoc/com/hazelcast/cp/lock/FencedLock.html)，核Fencing Tokens与lockAndGetFence说明，支持重入同token、完全释放后再次获取token变大、外部资源需配合检查。仅阅读固定版本，不安装或运行软件，不声称本篇模拟类是其实现。API文档中的“exactly-once”针对该锁API，本文没有将它外推成外部资源操作恰好一次。

本文的“先activate、再read、再write”是为一个读改写记分例子明确化的原创教学协议，不冒称所有fencing实现都必须有同名三个API。其他设计可以合并步骤，但必须另外证明它们的语义与应用所需保证。

## 两张来源信息图，原文件完整保留

原文正文仅有以下两张相关信息图，均已从其明确原URL正常HTTP200取得。书封、订阅组件和CC图标属于页面导航或附属内容，不纳入正文信息图。

- [source-unsafe-lock-original.png](assets/source-unsafe-lock-original.png)，1100×400、35437字节。作品名 *Unsafe access to a resource protected by a distributed lock*，Martin Kleppmann，2016。[原PNG](https://martin.kleppmann.com/2016/02/unsafe-lock.png)。
- [source-fencing-tokens-original.png](assets/source-fencing-tokens-original.png)，1100×400、35752字节。作品名 *Using fencing tokens to make resource access safe*，Martin Kleppmann，2016。[原PNG](https://martin.kleppmann.com/2016/02/fencing-tokens.png)。

许可依据是原作者文章页面实际页脚：“除另有说明外，网站内容采用CC BY 3.0 Unported”。文章注明两图也来自作者的 *Designing Data-Intensive Applications*，该来源说明已保留；所读取页面未给这两张网站图另列排除CC的许可。本文按其网站明确授权使用该网页提供的图文件，不据此授权整本书或书的其他图。

许可：[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)，[完整法律文本](https://creativecommons.org/licenses/by/3.0/legalcode)。两图保持下载原字节，没有裁切、翻译文字、重采样或改色；保留作者、作品名、文章及图源、许可链接，不表示作者背书本文。读者可打开原PNG查看完整英文标注；正文原创中文分步图提供手机尺度下的解释，不将这些示意冒充原图。

Chubby论文图1系统结构、图2会话故障转移，没有确认单独公开再分发许可，提供原PDF查看，不转载；本文没有以自己的框图声称收齐其原件。Hazelcast所引用API页的一幅字符时序图也只在原页查看，未将代码许可推定为文档图许可。Junqueira正文未含需收录的机制图片。

人物素材方面，已查找Mike Burrows和Kleppmann可靠身份来源；检索到的Mike Burrows自行车设计师同名类别不属于论文作者，未使用。Kleppmann一张Commons会议照说明页正常获取返回403，停止访问该URL，未下载照片、不绕路获取、不生成替代真人。本文为机制与工程史文章，保留可直接核实的原论文与作者原机制图，不声称具备人物肖像。

## 原创程序的实际验证

[examples/fencing_lab.py](examples/fencing_lab.py)使用Python标准库，本次CPython 3.12.14实际运行。全程是内存状态与排列枚举，没有网络、锁服务、真实时间、fsync、数据库或真实多机测试。

前提：一份身份固定的资源；可信、唯一且按授予顺序严格递增的持有者代号；每任仅一次加分读改写；每任按登记/读/写顺序；资源操作原子且可靠保存；恢复不让代号回退。模型假定客户端与发号结果不伪造，不证明拜占庭安全、身份认证、发号共识或持久化实现。

- n=1/2/3，各有1/20/1680种跨参与者交错。每人的增量取−2、0、3，分别有3/9/27组向量。完整运行3/180/45360次，合计45543次，共409329个原子步骤。
- 每步断言代号单调；接受的写入来自当前代；分数等于100加上所有已经接受的增量。只有成功写入才算贡献，拒绝操作不被伪计为已完成。
- 另枚举1至4的代号组成的全部长度6序列，共4096条，包括重复与回退请求，核登记后代号保持已见最大值。
- 8帧动画来自程序main_trace的实际8状态。1400ms每帧是阅读节奏，不是请求耗时或租约时长；到期只是情境标记。
- 分别实际执行边界反例：新代号尚未登记时旧写入仍可接受；资源忘代号；发号重用；先读后登记；非原子检查与效果；同代乱序；另附请求ID原子去重例。各段故意违背相应前提，不能将它们当正常实现。
- 正文Resource类是模型同义的短版（默认epoch0、value100），完整程序采用dataclass便于构造恢复状态。正文类另作提取执行并对照；未把未运行代码称为亲测。

## 25项视觉职责

22幅原创静态图依次负责：丢失更新；三角色；租约/进程双时间线；客户端检查缝；递增代号；唯一与有序；资源围栏；发号与登记边界；正确完整顺序；过早读反例；两种合法次序；三个API条件；资源原子性；忘记围栏；重用代号；同代乱序；三个身份概念；交错枚举；测试规模；实际副作用边界；多资源范围；保证与限制。

另有8帧动画及上述两张完整原作者PNG。没有通过把同一图拆成重复小图凑数；步骤图对应不同条件、机制或反例。
