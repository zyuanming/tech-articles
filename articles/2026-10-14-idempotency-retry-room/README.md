# 创建房间重试：本地SQLite实验与图解

正文：[read.md](read.md)。本例真正执行的是Python标准库sqlite3对数据库文件的操作，没有启动游戏服务器、HTTP服务器或邮件系统。

## 复现环境与命令

本次：Python 3.12.14、SQLite 3.53.1；制图Pillow 12.3.0，Noto Sans CJK Regular/Bold及DejaVu Sans Mono。

实验无需网络、第三方Python包或安装操作。在文章副本目录运行：

```sh
python3 examples/run_experiment.py --output room-retry-run-01
```

输出目录必须还不存在。程序在这个新目录保留12个SQLite数据库、results.json、environment.json与stdout.txt。数据库仅含教学玩家p7/p8、K17/K18和duo/squad模式，没有真实用户数据。子进程在指定位置直接退出是实验的一部分，预期退出码86、87、88、89由父进程核对；不是整个实验失败。

[expected-results.json](examples/expected-results.json)是本次真实运行得到的结构化结果；[run-environment.json](examples/run-environment.json)记录实际版本和实验范围；[原始标准输出](originals/experiment-stdout.txt)保留程序打印的文字，不是终端截图。数据中的status=201是模拟接口字段，没有实际HTTP报文。

## 数据模型与操作契约

- rooms：id、owner、mode、active；R001等是整数主键按固定格式显示，不是随机真实服务器编号。
- receipts：actor、operation_key、parameters、http_status、response_body、retained_since。actor与operation_key均显式NOT NULL，组成复合主键。表只服务create-room；actor假定来自已经验证的身份，不是任意未认证输入。
- naive_markers：只用于故意写坏的“记号先提交”反例，不是推荐数据模型。
- 正常路径先校验mode并将单字段参数规范化为JSON，再BEGIN IMMEDIATE、查询回执、核对原参数、按需插入房间和回执、一起提交，提交后返回。缓存重复分支不会再次插入房间。
- 此处规范化不处理任意业务参数的语义等价；duo和squad是明确不同值。编号仅示意，不提供生产级唯一性、安全性或客户端持久化实现。
- 接口结果中的replayed是实验观察标记，不属于回执保存的响应正文。保存结果正文只含mode与room_id；正常首次和复用分支都从相同规范JSON构造返回数据。
- 每个案例单独初始化一个空数据库，R001因而会在不同数据库中重新出现。不同案例不可当成一个不断累加的运行历史。

## 12个实际案例

1. unsafe_response_ignored：普通创建两次；第一次返回值被调用方忽略，最后2间房。
2. safe_response_ignored：p7/K17/duo两次；最后1间房1份回执，第二次replayed=true。
3. new_intent_same_parameters：p7/K17与p7/K18、都duo，2间房2份回执。
4. same_key_different_parameters：先duo后squad，同键拒绝，仍1间房。
5. same_key_different_actor：p7与p8各用K17，不同作用域，2间房。
6. before_commit：子进程插入房间后、写回执和提交前os._exit(86)；重新连接读0房0回执，同键重试后1/1。
7. after_commit：两表提交后、函数返回前os._exit(87)；重新连接已是1/1，重试仍1/1。
8. effect_first：故意把房间独立提交，随后os._exit(88)，没有回执；正常带键重试再建一间，最终2房1回执。
9. marker_first：故意独立提交裸记号后os._exit(89)；错误的“见过就跳过”重试留下0房1记号。
10. concurrent_same_key：两个线程、各自一个连接、共同barrier起跑；谁先取得写事务未固定。结果按replayed排序方便复验，不修改真实房间数据。实际一份创建、一份复用，同为R001，最后1/1。
11. receipt_expired：时间0建房，保留期为10个教学tick，时间11删除retained_since <= 1的回执；房间不删除。旧键再来建立R002，最终2房1新回执。这是边界反例，不是推荐保留策略。
12. resource_lifecycle：创建后active改为false，重试取回旧R001，不将资源重新开放。

## 事务与故障边界

数据库journal_mode=DELETE、synchronous=FULL；每个连接timeout=10秒。BEGIN IMMEDIATE在查询前取得写事务，SQLite同库写事务串行化。此实现并不只锁相同键，不适合作为吞吐量演示；等待可超时，BUSY不等于原操作一定没发生。

实际终止的是子进程，不是断电、操作系统崩溃、磁盘损坏或真实网络丢包。实验不穷举所有崩溃点，不证明设备兑现同步写入承诺。程序没有对邮件、外部服务、文件写入和真实游戏进程提供共同事务。

## 重绘说明

在文章副本中运行：

```sh
python3 examples/build_figures.py
```

需要已经安装的Pillow和上述字体；脚本不联网、不安装软件。它读取expected-results.json，先核对图中固定标记与输出关键值一致，再生成14张正文图和独立封面，写figure-metadata.json。真实数据图是对实际输出的排版，不是终端/网页/游戏UI截图；示意箭头不是抓包。

每图用途与身份记录于[figure-metadata.json](examples/figure-metadata.json)。正文图无第三方照片或架构图复制；全部根据本文小例、真实SQLite输出及已核机制原创绘制。字体与图像跨版本字节一致性不作保证；本次同环境的实际复验另行记录。

代码采用[MIT](LICENSE-CODE.txt)，原创正文与解释图CC BY 4.0。来源与AI辅助说明见[sources.md](sources.md)。
