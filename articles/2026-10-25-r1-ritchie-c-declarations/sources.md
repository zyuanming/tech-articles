# 来源、实验与许可

本文由 zyuanming 发布。正文与原创教学图采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；转载须署名、链接原文与许可，并说明修改。原创 C、Python、HTML 代码及本次数值实验 JSON 采用 [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)。这不改变第三方资料的权利。

## 一手历史材料

Dennis M. Ritchie，[The Development of the C Language](https://www.nokia.com/bell-labs/about/dennis-m-ritchie/chist.html)，1993年 HOPL-II 回顾论文，1996年收入论文集。作者电子重印页的文字已覆盖阅读，包括 Embryonic C、Critique 与页首版权说明。支持范围是“声明结构仿照使用结构”的设计解释、作者对这种写法的反思，以及回顾发表日期与早期演变的区别。它不是1970年代现场记录，也不是现行标准。

原文页注明 ©1993 ACM，作者提供电子重印，进一步出版须联系 ACM 或作者。公开可读不等于开放复用；本文没有转载原论文页面、原图、完整程序块或肖像。采样数组与全部现代实验为新写。原 HTML 下载遭403拒绝后停止获取；已读解析文字仍可核对，但原页面像素和完整图片标签列表未核。逐项清点见 [视觉清单](source-visual-inventory.md)。

## 现代技术资料的实际覆盖

- [GNU C Language Manual](https://www.gnu.org/software/c-intro-and-ref/manual/c-intro-and-ref.html)：已取得官方站检索返回的相关文字段落，包括数组与指针声明、数组形参调整、函数指针声明及 `sizeof` 对形参的作用。整页与若干章节正文打开超时，不能称读过整本手册。只用实际返回范围支持对应概念，不采用检索中无关的 GNU 扩展。
- [Declaring Function Pointers](https://www.gnu.org/software/c-intro-and-ref/manual/html_node/Declaring-Function-Pointers.html)、[Array parameters are pointers](https://www.gnu.org/software/c-intro-and-ref/manual/html_node/Array-Parm-Pointer.html)、[Type Size](https://www.gnu.org/software/c-intro-and-ref/manual/html_node/Type-Size.html)：为读者提供官方定位。相关内容也见上述整本手册的检索返回；不声称各页原像素已审视。
- [GCC C Dialect Options](https://gcc.gnu.org/onlinedocs/gcc/C-Dialect-Options.html)：已读官方检索返回中 C11 模式说明。该在线文档随版本变化；本文不沿用其“默认标准”，而是明确传入 `-std=c11`，实际编译器版本另存于 JSON。
- [WG14 N1570 草案](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)：本次未取得正文，打开超时，原件下载随后403，已停止。仅记录核对目标，未当作已亲读的标准条款证据，也未从镜像补取。

GNU 手册、GCC 文档和 Ritchie 回忆均为独立作品；没有通过另一网站转取被拒绝的同一原件。网页导航、截图缺失与其他未读范围，不推断为原站“没有图片”。

## 实验是什么，能证明什么

实际环境：GCC（Debian 14.2.0-19）14.2.0、Linux x86_64、C11 模式，`__STDC_VERSION__` 为201112，`CHAR_BIT` 为8。所有输入为自造教学样本，不是传感器采集。无随机步骤。

`main.c` 实际计算元素访问、函数返回值、指针与数组大小；`experiment.py` 记录编译和执行的退出码、原始标准输出与标准错误，并实际提交六个不合法样例进行诊断。正例故意保留数组形参 `sizeof` 警告，以展示该形参已调整成指针；未将它隐藏成无警告结果。

指针步长先由同一数组内合法相减得到单位数量，再乘实际所指类型大小；没有跨不相关对象相减、打印函数指针的非标准转换、地址探针或未定义行为演示。`grid` 与 `samples` 是两个不同对象，图中跨行演示只取 `grid`。负例不执行。一次实现的诊断与返回值不是所有 C 实现的形式证明，也不把4/8/12等字节数写成普遍标准要求。

## 逐图身份与理解作用

图中几何、标签与实际数据的连接，以及尺寸、字号、文字审计保存在 [figure-metadata.json](examples/figure-metadata.json)。格数和箭头目标来自样本及指针差 JSON，字节条形长度共用比例；其余位置、留白、配色是版式参数，不是模型测量。

| 文件 | 身份与新增作用 | 权利 |
|---|---|---|
| 00-cover | 独立封面，用括号对照两种声明 | 原创 CC BY 4.0 |
| 01-object | 数组元素、下标与元素指针 | 原创 CC BY 4.0 |
| 02-build | 由解引用整行、取元素回推声明 | 原创 CC BY 4.0 |
| 03-binding | 两种结合结构对应不同类型层次 | 原创 CC BY 4.0 |
| 04-links | 三个指针实际重排样本访问顺序 | 原创 CC BY 4.0 |
| 05-row | 一个指针与整行对象分开 | 原创 CC BY 4.0 |
| 06-steps | 同一 grid 上整数指针与行指针步进 | 原创 CC BY 4.0 |
| 07-functions | 返回数据指针与经函数指针调用两条路径 | 原创 CC BY 4.0 |
| 07b-reader-type | 从名字向外读取复杂声明的类型层次 | 原创 CC BY 4.0 |
| 08-reader | 调用 reader，获得地址后再读取整数 | 原创 CC BY 4.0 |
| 09-sizes | 实测 sizeof 在共同字节尺度上的差别 | 原创 CC BY 4.0 |
| 10-parameters | 调用处转换与形参调整，以及内层行宽 | 原创 CC BY 4.0 |
| 11-typedef | 类型别名简化与 const 所在层次 | 原创 CC BY 4.0 |
| 12-run-report | 真实 Chromium 页面：本次成功运行记录 | 原创页面 CC BY 4.0，数据 CC0 |
| 13-wrong-row | 同一查看器中真实的不兼容指针诊断 | 原创页面 CC BY 4.0；诊断短句见下 |
| 14-illegal-return | 同一查看器中真实的非法返回类型诊断 | 原创页面 CC BY 4.0；诊断短句见下 |

最后三张是实际 HTTP 教学结果页的浏览器截图，1062像素视口、设备像素比1；读取本次已保存的记录，不承诺实时编译，不是 GNU 官方界面或 Ritchie 原机画面。界面与排版由本文原创；GCC 输出中的短错误文字、类型名和定位行仅作必要技术引证，不将 GCC 软件许可推断为对第三方文档或图片的再授权。未采用第三方照片、文档页面截图、商标图或历史代码图块。

## AI 辅助与复核范围

AI 辅助检索、中文写作、设计原创图解和编写程序。数值由实际 GCC 编译运行取得，Python 从 JSON 生成图形；图像不是生成式模型伪造的实拍。作者逐图检查原图和354像素静态代理，查看器也在真实354像素浏览器视口检查全部选项。静态代理不是浏览器截图，作者自检也不代替非作者独立审读。
