# 来源、实验与素材权利

本篇由 zyuanming 发布。原创正文、原创解释图及原创教学界面截图采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，转载请署名、链接来源与许可并说明修改。`examples` 中原创 Python 代码和 JSON 科学数据采用 [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)。没有将第三方页面、软件或字体纳入上述授权。

## 一手文档与支持范围

核验日期：2026-10-25。Linux 页面来自 man7.org 所展示的 Linux man-pages 项目 6.19，页面自身标注其来自 6.19 tarball；这不是本文实跑内核版本。Python 官方页面本次显示 3.12.15 文档，实跑解释器为 3.12.14。

下面的 L 范围指本次文档文本展开后的行号，用于精确说明已读范围，不是原 HTML 固有行号。已读窗口取并集，不能把网页“总行数”当成已读取全文。各页面直接原 HTML 下载均返回 403，未取得原 HTML 和页面原像素，之后停止该页面、已解析引用及同内容镜像的继续请求。保留此前已经获得的文本证据，未把下载失败说成无事实依据，也不把文本当成原图像素检查。

| 来源 | 已读文本范围 / 展开总范围 | 对本篇的支持与边界 |
|---|---|---|
| [epoll(7)](https://man7.org/linux/man-pages/man7/epoll.7.html) | L0–394 / L0–401 | 兴趣与就绪集合，LT/ET 管道例，非阻塞与 EAGAIN，多次事件及合并，ONESHOT，ET 同时关注 IN/OUT 的替代策略，流短读判断与用户 ready 队列。未核 L395–401 和原页面像素。 |
| [epoll_ctl(2)](https://man7.org/linux/man-pages/man2/epoll_ctl.2.html) | L0–271 / L0–271 | ADD/MOD/DEL，IN/OUT/RDHUP/HUP/ERR，ONESHOT rearm，HUP 后仍须消费尾部。文本全范围已读，原 HTML、完整图像清单及像素未核。 |
| [read(2)](https://man7.org/linux/man-pages/man2/read.2.html) | L0–170 / L0–177 | 正数短读、零返回、EAGAIN/EWOULDBLOCK 和 EINTR；本文限定正数请求长度、流式 socket。未核 L171–177 与原像素。 |
| [write(2)](https://man7.org/linux/man-pages/man2/write.2.html) | L0–213 / L0–220 | 部分写、剩余后缀、EAGAIN/EWOULDBLOCK、EINTR 与其他错误。未核 L214–220 与原像素，不借文件持久性段落推导网络完成语义。 |
| [epoll_wait(2)](https://man7.org/linux/man-pages/man2/epoll_wait.2.html) | L0–199 / L0–199 | 返回事件信息、零超时、毫秒单位、信号打断。文本全范围已读，原像素未核；不把内核轮转等同本文应用轮转。 |
| [socket(2)](https://man7.org/linux/man-pages/man2/socket.2.html) | L64–152 / L0–278 | SOCK_STREAM 双向字节流、不保留记录边界、NONBLOCK。其余范围未读，不声称全页视觉清单。 |
| [Python 3.12 select](https://docs.python.org/3.12/library/select.html) | L0–36、L141–276 / L0–364 | epoll 接口适用 Linux、register/modify/unregister/poll、事件表、秒单位及信号自动重试说明。未读 L37–140、L277–364；不把邻近 poll/kqueue 规则套到 epoll。 |

正文引用以上接口事实；字节串、操作序列、协议解析、应用队列与图形布局为本文原创例子。没有引用 Linux 内核内部源码结构或特定算法复杂度，没有将这些接口页冒称对本机内核源代码的核验。

## 相关原始视觉与代码库存

逐项采用、排除理由及未取得范围见[原始视觉库存](source-visual-inventory.md)。已读文档主要提供文本流程、函数原型和事件表；没有取得可供转载的页面原像素或图片原件。本篇不复制第三方整页、代码示例或表格图像，不将外部文字改画后冒称原图。原创实验与真实工具截图补足可观察证据，不能替代未完成的原像素检查。

## 本篇每张图的理解作用

下列均为新制作、宽 1062 像素。00–13 为原创解释图或真实实验数据的可视化，均不是内核监控截图；14 为真实浏览器截图。逐图尺寸与字体记录在 [figure-metadata.json](examples/figure-metadata.json)。

| 文件 | 新增理解作用 | 数据及权利 |
|---|---|---|
| 00-cover.png | 独立封面：把通知与仍在原处的字节并置 | `partial`；原创 CC BY 4.0 |
| 01-objects.png | 端点缓冲、兴趣集合、就绪事件分开 | `partial` 加接口关系示意；原创 CC BY 4.0 |
| 02-wait.png | 等待前后观察到的六字节不变 | `partial` 的两次 peek；原创 CC BY 4.0 |
| 03-lt-et.png | 同输入同读取量逐步比较两种通知模式 | `partial` 两次真实实验；原创 CC BY 4.0 |
| 04-drain.png | cdef、ef、空的变化和 EAGAIN 结束条件 | `partial.drained`；原创 CC BY 4.0 |
| 05-read-results.png | 读取结果与处理动作分支 | 接口事实的原创解释，非分支实测覆盖报告；CC BY 4.0 |
| 06-stale.png | 通知后先被读取，稍后读取会 EAGAIN | `stale` 顺序实跑；原创 CC BY 4.0 |
| 07-framing.png | 排空与完整消息是两个边界 | `framing` 真实三轮输入与解析；原创 CC BY 4.0 |
| 08-eof.png | 半关闭先尾部数据后零返回 | `eof`；原创 CC BY 4.0 |
| 09-partial-write.png | 按比例区分内核已接纳和应用剩余量 | `writing`；原创 CC BY 4.0 |
| 10-output-policy.png | 按需可写兴趣及写入进度 | 原创应用策略图，不声明所有分支已注入实测；CC BY 4.0 |
| 11-fairness.png | 预算用尽重排队，确认耗尽再移出 | `fairness.trace`；原创 CC BY 4.0 |
| 12-oneshot.png | LT 也可 ONESHOT，须 MOD 才恢复报告 | `oneshot`；原创 CC BY 4.0 |
| 13-new-activity.png | ET 未排空时新增字节，本次仍可再通知 | `new_activity`；原创 CC BY 4.0 |
| 14-live-demo.png | 点击后真实运行的教学工具与结果 | `capture_demo.py` 实际 Chromium 截图；原创 CC BY 4.0 |

## 实验范围与可复算性

[experiment.py](examples/experiment.py)使用标准库真实调用 Linux socketpair 与 epoll。公开结果用 A/B 表示端点，保存输入、返回标志、字节数和读取顺序，不包含外部服务内容、主机名或账号数据。实验结果见 [results.json](examples/results.json)，运行与重制方法见[说明](examples/README.md)。

实跑系统为 Linux，内核发布号仅记录必要数字部分 6.18.55；Python 3.12.14。没有人为设置时间延迟，没有性能时间轴。所有事件轮询超时为零。数据中的事件列表与部分写长度来自本机观测；不同内核、socket 类型、缓冲配置和并发活动可能改变具体结果，接口规则与教学观察应分开理解。没有测 TCP 拥塞、网络分包、生产负载或多线程竞态。

生成器的字节格子来自实际字符串，条形分界来自实际写入量 / 总输入量；A/B 用户态轮转明确使用按名称排序的初始策略。每张原创图运行几何、字形与像素检查，并检查 354 像素比例可读性。真实页面截图使用 Chromium 154.0.8037.57；354 CSS 像素、设备比例 3，另检查 1062 CSS 像素和两个模式。原始截图没有终端提示符、账号或主机状态。

AI 辅助用于文档梳理、写作、实验代码及绘图。数值、事件和界面来自程序实际执行；AI 没有生成假的系统截图。EINTR、所有其他错误与生产关闭竞态未做穷尽实验；相关文字来自已读接口说明。作者自检不等于非作者独立审读，也不等于任何平台发布。
