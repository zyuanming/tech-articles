# 来源、实验与配图说明

本文为原创中文教学文章。正文与原创教学图采用 CC BY 4.0；配套独立示例程序采用 examples/README.md 所列 MIT 许可。文稿、代码和教学示意制作使用了 AI 辅助，并以一手材料、实际运行记录及独立图文审读核验。没有用生成图冒充真人、真实旧设备或软件截图。

## 一手材料与支持范围

1. Melvin E. Conway, *Design of a Separable Transition-Diagram Compiler*, Communications of the ACM 6(7), July 1963, pp.396–408，DOI 10.1145/366663.366704。[作者保存的原论文](https://melconway.com/Home/pdf/compiler.pdf)。本篇实际核对原生扫描第396—398页：Case工作年份、Burroughs220、协程模块交接、保存继续位置，以及原文对Joel Erdwinn的共同发展说明。没有声称读完整篇COBOL编译器论文，也不采用“独自发明”或“首次”的强断言。
2. [Python 3.12语言参考：yield表达式及生成器方法](https://docs.python.org/3.12/reference/expressions.html#yield-expressions)。支持创建/启动、yield与send双向值、保存执行状态、throw和close的接口边界。访问时页面为3.12.15；本文实测运行环境是CPython3.12.14。没有把所有协程实现等同于Python生成器；本文生成器把执行权交回调用者。
3. Guido van Rossum、Phillip J. Eby，[PEP 342 — Coroutines via Enhanced Generators](https://peps.python.org/pep-0342/)，创建于2005-05-10，目标Python2.5。用于历史脉络与能力扩展背景；旧提案中的历史细节不作为所有现代实现的统一规范。
4. [Python 3.12：Coroutines and Tasks](https://docs.python.org/3.12/library/asyncio-task.html)。支持async函数调用、协程对象、等待与Task调度的区别。第13节仅作进一步阅读地图，不声称实现完整事件循环。
5. [Conway本人对编程工具工作的回顾](https://www.melconway.com/Home/Inventor.html)。作为人物资料核查补充，未据此虚构故事现场。本篇人物是Melvin E. Conway，不是研究生命游戏的John Horton Conway。

## 相关原图与没有采用的素材

原论文第397页图1为星号压缩子程序，图2为协程形式，图3为直接交接与磁带中转；第398页图4为COBOL编译器模块结构。它们均已纳入来源核查清单，但本次没有取得公开重分发许可，因此只提供上述原文查看链接，未复制进公开仓库。原图没有被声称已经以原创图代为完整收齐。第398页后半部的字符分类表以及后续语法分析/声明/条件生成图表不用于本篇机制讲解。

作者官网可访问原论文，并不等于其中图像采用开放许可。ACM出版社原页面本次返回403后即停止，没有绕过限制。已先行正常取得的作者原PDF仅用于私下研究核验，不纳入交付包。

已主动查过作者主页、Commons定向检索及人物图片候选；没有为本篇确认到可用的Melvin Conway肖像或Burroughs220原尺寸照片。第三方演示文稿出现的人像未获得逐图许可核对，未采用；作者主页的New Yorker漫画标有权利保留，未采用。本篇以机制探索为主，用原创状态与运行轨迹图辅助，不用不相关同名人物照片，也不推断全网不存在合法素材。

## 自设实验与边界

所有数字来自本文自设程序，而非第三方性能报告。

- 主例：初始10，send(3)后交出13，再send(5)以StopIteration.value=18结束。对应日志为“进入”“清理”。
- 双实例、末尾练习和正文TinyCharge正常路径另行核对。TinyCharge只演示阶段卡，接口不是Python生成器接口；完整ChargeMachine只匹配下列限定集合。
- 六种动作：next、send(-2)、send(0)、send(3)、close、throw(ValueError实例)。长度0—5全部9331条序列，逐步比较44790次动作的返回/异常类型/结束值/状态/日志。send(5)主例另测，不算在六动作枚举中。
- 两任务轮流：A1/B1/A2/B2/A3/B3；不让出的任务先执行A1/A2/A3/A4再到B1。逻辑顺序实验，没有多线程、网络I/O、帧率或硬件跑分。
- 异常比较范围不包括任意用户类型、任意异常对象、重入、yield from或异步生成器；不是Python解释器或生产调度库正确性证明。
- 清理使用显式close核查，不依赖垃圾回收时机；本篇没有真的获取文件句柄或网络连接。

运行方法及许可见 [examples/README.md](examples/README.md)，完整源代码见 [coroutine_lab.py](examples/coroutine_lab.py)。

## 25项原创视觉

以下均为本篇程序绘制的原创教学示意。不是原论文图、截图或旧机器复原。较小副标题用于限定范围；核心值与控制位置分别用大字标示。

| 文件 | 教学作用 |
|---|---|
|01-game-pauses.png|游戏充能流程中两次等待与执行权交回|
|02-restart-or-resume.png|重新调用与保存继续位置的区别|
|03-history.png|1961/1963/2005三个有来源的历史节点|
|04-data-and-control.png|数据方向与控制交接方向的区分|
|05-stream-or-batch.png|交替处理与分阶段保存结果|
|06-two-way-window.png|yield向外交值、send向内送值|
|07-created-and-first-next.png|创建不执行、第一次next才进入|
|08-send-three.png|第一次send恢复后的逐步运算|
|09-return-eighteen.png|第二次send后通过正常结束交最终值|
|10-yield-versus-return.png|阶段输出与终局返回两种通道|
|11-saved-card.png|局部值与继续位置的概念工作卡|
|12-two-instances.png|共享代码、分开的执行状态|
|13-lifecycle.png|调用返回后观察到的静止状态；不排除运行状态|
|14-two-type-errors.png|初始非法send与恢复后加法错误的不同后果|
|15-manual-phases.png|自定义阶段编号，不是机器地址|
|16-transition-ledger.png|主例三个阶段转移|
|17-test-scope.png|实际测试数量与覆盖边界|
|18-round-robin.png|两任务六次推进的实际日志|
|19-no-preemption.png|不让出时不会自动切换的反例|
|20-interleave-and-parallel.png|交替与并行的不同执行结构|
|21-throw-and-finally.png|本例异常经过清理再传播|
|22-close-before-or-after.png|未启动与已进入try的关闭区别|
|23-mechanism-map.png|生成器、原生协程、调度器的接口边界|
|24-exercise.png|同一程序改变两份输入的练习|
|25-resume-trace.gif|实际主例四次观察的动画：创建/交出10/交出13/结束18|

GIF为4个实际编码帧，每帧1400毫秒循环；帧间时间为了阅读设定，不代表程序真实耗时。最后一帧是返回值，不是第三次yield。
