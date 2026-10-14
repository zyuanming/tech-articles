# 来源、实验身份与素材许可

正文：[read.md](read.md)。资料读取与本地实验日期：2026-10-14 UTC。

## 一手资料及所支撑的范围

### 1. Malcolm Featonby，AWS Builders' Library

[Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)；[官方PDF](https://d1.awsstatic.com/builderslibrary/pdfs/making-retries-safe-with-idempotent-apis-malcolm-featonby.pdf)。PDF共9页，封面版权2020；没有据此推断文章首次发表日。

采用其对结果不确定、调用者提供意图标识、参数相同不必然同一意图、令牌与相关改变需共同原子承诺、迟到请求、资源生命周期和同键异参的工程解释。PDF印刷页1–2为无响应/参数推测，页3为调用者与ID/原子变更，页4–5为语义等价响应，页6–7为迟到/生命周期，页8为参数不匹配。本文“创建游戏房间”和SQLite代码是新的教学实例，不是该文的真实游戏案例，也不是AWS内部实现复刻。

本页3张相关正文信息图已按原文件核查，但PDF版权为All rights reserved，未取得开放再授权依据，因此不收录在公开assets、原件目录或正文许可中。读者可沿原文查看。本文所有流程图重新围绕本地程序和数据设计，不是对AWS原图换色翻译。

### 2. RFC 9110，HTTP Semantics

[9.2.2节：Idempotent Methods](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)，2022年6月。

用于区分预期效果、实际请求处理次数、日志副作用和响应可能不同。本文不是幂等键HTTP标准的实现，也未把任意POST宣称为天然幂等。201只是本例保存的创建成功结果字段；无真实HTTP请求测试。

### 3. SQLite官方文档

- [Transactions](https://www.sqlite.org/lang_transaction.html)：同一时刻只有一个写事务；BEGIN IMMEDIATE先尝试写事务，可能SQLITE_BUSY；事务结束与错误处理。网页标示更新2026-02-18，不当成本机运行版本。
- [CREATE TABLE](https://www.sqlite.org/lang_createtable.html)：主键、唯一性和NULL细节。普通SQLite表的PRIMARY KEY不能自动替代所有NOT NULL声明；本例两列显式NOT NULL。
- [Atomic Commit in SQLite](https://www.sqlite.org/atomiccommit.html)：事务原子性与存储/文件系统假设。文档主要解释rollback模式；本文只借用事务承诺，不重复实现恢复协议。
- [SQLite版权说明](https://www.sqlite.org/copyright.html)：SQLite本体及交付文档的公有领域说明，不扩展为任何第三方GUI、wrapper或云平台素材许可。

本次运行由Python 3.12.14标准库sqlite3调用SQLite 3.53.1，journal_mode=DELETE、synchronous=FULL、连接timeout=10秒。网页更新日期、Python版本和SQLite运行库版本各自独立。

### 4. Stripe官方具体接口契约

[Idempotent requests](https://docs.stripe.com/api/idempotent_requests)，读取日2026-10-14。该页当时明确区分API v1和API v2，未给出锁定文档修订日。

只用于提醒读者不同产品及版本的契约不同。API v1对保存首次状态/正文、至少24小时后可清理、验证/并发冲突是否保存等有具体说明；这不是全行业统一规则，也不是本文10 tick实验的依据。正文没有运行Stripe API、支付或账户操作。不要将API v1边界扩大成其全部接口或未来版本。

### 5. AWS Prescriptive Guidance

[Transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)。采用Intent、Motivation和Issues中的边界：数据库与外部通知分开，可能只成功一边；发件箱也不排除消息重复，消费者仍需对应处理。本文不实现该模式，也不复用该页架构图。

## 实验证据与局限

- [实际结构化结果](examples/expected-results.json)保留12个案例中的调用结果和实际查库记录。
- [环境记录](examples/run-environment.json)与[程序原始标准输出](originals/experiment-stdout.txt)对应同一次本地运行；stdout为文本原件，不是终端截图。
- [实验代码](examples/run_experiment.py)只操作新建的本地教学数据库文件；完整命令和每例说明见[README](README.md)。各案例独立从空库开始。
- 无回音先通过调用方忽略返回值模拟，不称真实网络丢包；后续os._exit是在指定位置实际结束子进程，不冒称断电、操作系统故障或故障点穷举。两线程并发是真实执行，但线程赢家没有预设；展示排序不表示执行顺序固定。
- “房间”是rooms表中的记录，不是实际网络游戏进程。没有支付、邮件、第三方API或外部服务副作用；单库事务不能推广为所有外部动作的一次执行保证。

## 14张正文图与独立封面

所有图片为本篇原创，制图脚本见[build_figures.py](examples/build_figures.py)，逐图用途/身份/字号见[figure-metadata.json](examples/figure-metadata.json)。图中颜色区分请求、成功、冲突与等待，具体对象和时序由相邻中文解释。没有生成式伪造照片、虚构真实游戏UI或伪装网络抓包。

- 01：两个隐藏服务器状态对应相同无回音，教学时序。
- 02：两次不受保护调用的真实rooms行，依据unsafe_response_ignored重排。
- 03：K17重复与K18新意图区别，同参数可以不同意图。
- 04：同一数据库的房间与回执字段，采用safe_response_ignored实际值作说明。
- 05：本例事务与已有回执分支；括线是数据库事务范围，不是同步时刻。
- 06：safe_response_ignored的真实两次返回和最终数量。
- 07：effect_first、marker_first两种实际终止反例的提交窗口。
- 08：before_commit、after_commit两个子进程退出实验的真实状态计数。
- 09：concurrent_same_key的实际两连接结果与写事务串行示意。
- 10：same_key_different_parameters的真实参数冲突，不暗示固定行业错误码。
- 11：receipt_expired实际清理后迟到重试，10/11为教学tick。
- 12：resource_lifecycle的实际关闭状态与原创建结果。
- 13：本地事务与外部动作的保护边界，非生产架构图。
- 14：客户端意图的保存、未知、确认、新建四个阶段，非真实客户端UI。
- 封面：同键重复请求汇到同一房间结果的原创概括图，不另计正文图。

真实输出图只保留关键字段，并作中文重排；图中不展示的完整数据在JSON中。没有以“重新排版”声称取得某个商业软件截图。

## 许可与AI辅助

原创正文、原创解释图及本次原创教学输出采用CC BY 4.0；原创实验/制图程序采用[MIT](LICENSE-CODE.txt)。第三方资料只链接并在上述范围内释义；其版权不因本文许可而改变。

AI参与资料查找、方案讨论、初稿、代码和解释图制作及审读辅助。数据由保存的代码在所列本地环境实际执行产生；没有把语言模型预测冒充实验输出，没有声称作者亲历AWS内部工程、实际运营游戏服务器或测试真实网络/电源故障。
