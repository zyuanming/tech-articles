# 来源、许可与复算范围

本文是 2026-10-25 的 r1 新制作版本。正文、原创教学图与示例代码均为本篇新写，未使用旧批次的正文、图片或历史未知上传对象。本次在同篇补充过程图、真实教学界面截图与有明确 MIT 许可的实现方 ASCII 图对照，不新建重复文章。

## 事实来源

1. Alfred V. Aho、Margaret J. Corasick，*Efficient String Matching: An Aid to Bibliographic Search*，Communications of the ACM 18(6)，333–340，1975，DOI [10.1145/360825.360855](https://dl.acm.org/doi/10.1145/360825.360855)。用于核对作者、发表年、标题及“固定关键词集合的出现位置搜索”这一论文问题。书目及摘要可检索；本次未成功取得出版商全文，因此不宣称逐页核验原论文，不采用原论文图像、性能数字或历史成本叙事。
2. [aho-corasick 1.1.5 实现方文档](https://docs.rs/aho-corasick/1.1.5/aho_corasick/)。已读概览、重叠与不同匹配语义、流式接口和 prefilter 说明。仅支持现代库接口及性能取舍的事实，不用现代实现反推 1975 年的内部细节；随文 Python 为本篇教学实现，不是该 Rust 库的移植。
3. 正文对失败后缀、输出链、扫描摊还界和示例的解释是独立教学推演，具体数值由 [ac.py](examples/ac.py) 与 [results.json](examples/results.json) 支撑；有限测试不能替代理论证明，也不构成生产环境基准。

4. [实现方 1.1.5 DESIGN.md](https://github.com/BurntSushi/aho-corasick/blob/1.1.5/DESIGN.md)，核读 Basics、失败连接、实现布局与预过滤说明；采用其中两幅 `abcd/cef` ASCII 图，见[带图对照附页](source-figures.md)。这是现代设计文档，不是原论文。固定到发布标签 1.1.5，未取得不可变提交 SHA；公开转录与可访问网页代码块核对，不称原文件字节副本。

## 图片及其解释作用

视觉材料分为三类：原创教学示意、一次真实本地教学 web 界面截图、实现方 MIT ASCII 图的转录与等宽重排渲染。主线图仍用 `he/she/his/hers`，密集输出反例与附页换词表时均明确说明。相关原论文全文未取得，图表数量和内容未核，未取得其图片再分发许可；没有访问绕取途径，也没有将原创图冒称原论文图。

| 文件 | 新增的理解作用 |
|---|---|
| `00-cover.png` | 独立封面，建立词表、共享机器与文本的关系 |
| `01-trie.png` | 看见前缀共享与完整词仍可继续延伸 |
| `02-failure.png` | 区分不消费字符的后缀跳转和消费字符的树边 |
| `03-trace.png` | 对照逐字符执行的状态、失败发生点与输出 |
| `04-overlap.png` | 对照同一坐标尺度上的全部半开区间 |
| `05-stream.png` | 看见块间保留的状态和全局位置 |
| `06-insert.png` | 同一词表逐词插入，区分复用节点与新增路径 |
| `07-bfs.png` | 深度层序与实际先进先出队列，解释浅层依赖 |
| `08-build-failure.png` | 从已知 `sh→h` 和 `h` 的 `e` 出边构建 `she→he` |
| `09-output-link.png` | 分开失败边、输出链接和不变的主状态 |
| `10-fallback-steps.png` | 展开主线三次失败链，显示字符在回退中不被消费 |
| `11-depth.png` | 同输入深度折线和总账，区分失败次数与下降层数 |
| `12-output-count.png` | 另换词表 `a/aa/aaa`，九条同尺度命中带显示输出量 |
| `13-live-demo.png` | Playwright 真正点击本地教学页面，显示实时双块匹配与验证摘要 |
| `14-multi-failure.png` | 显式追加 `x` 的变体中，一个字符引起两次失败 |
| `15-source-trie.png`、`16-source-failure.png` | 实现方原文两幅 ASCII 结构的等宽重排渲染；MIT，非原站截图 |

原六图 `00`–`05` 保留原图片字节。主线数值来自 [results.json](examples/results.json)，补充插桩来自 [visual-results.json](examples/visual-results.json)；分别用 [build_figures.py](examples/build_figures.py) 与 [build_visual_figures.py](examples/build_visual_figures.py) 生成。尺寸与最小字号见 [figure-metadata.json](examples/figure-metadata.json)。使用 Noto Sans CJK 与 DejaVu Sans Mono；不分发字体文件。构建后程序检查字形、文字边界、字号、对比、像素与实际尺寸，图义再由读者对照正文判断。

真实截图来自本篇 [demo_web.py](examples/demo_web.py)，它只绑定 `127.0.0.1`，每次按钮请求重新执行匹配及测试。截图由 [capture_demo.py](examples/capture_demo.py) 调用系统 Chromium 154.0.8037.57 实际点击取得，Python 3.12.14，1062px 宽，关键字号 42px；[执行摘要](examples/demo-capture.json)可核四输出与测试数量。它是本篇教学软件的实际画面，不是终端截图、生产产品、平台预览或性能测试。页面没有私有路径、账号和日志。

## 可访问原来源的图、表、示例清单

这份清单只覆盖下面已核页面可提取的正文内容；没有声称遍历所有外链和全部 API 页面。未取得页面 DOM/像素的穷尽媒体统计，故不把“文本提取中没出现图片”误说成网页没有其他素材。

| 来源内的项目 | 采用或排除范围 |
|---|---|
| DESIGN Basics 的 `abcd/cef` ASCII 树 | 已采用：附页保存转录、原编号、星号和可读渲染 |
| DESIGN 随后加入 `S3→S5` 的 ASCII 图 | 已采用：与上一图配对，中文说明方向和省略的根失败边 |
| DESIGN 朴素搜索伪码 | 仅来源，本文有独立朴素基准，不转载 |
| DESIGN `has_prefix` 示例 | 不转载，判断开头不同于本文全部位置搜索 |
| DESIGN 带失败循环的 `contains` 示例 | 仅机制对照，首命中不能冒充本文全部重叠输出 |
| DESIGN DFA `contains` 示例 | 不转载，本文不实现完整 DFA |
| DESIGN 两个转移表索引表达式 | 不图化，底层布局优化超出本篇主线 |
| DESIGN 两组 prefilter 模式列表示例 | 不转载，SIMD 预过滤超出范围 |
| docs.rs 1.1.5 概览的基础搜索代码与断言 | 接口来源，未作为本篇运行截图 |
| 概览的 ASCII 大小写示例 | 不转载，本文未教该选项 |
| 概览的流式替换示例 | 链接来源，替换不等于全部重叠搜索 |
| 概览的标准 `Sam` 与 leftmost-first `Samwise` 两例 | 末节语义区别的来源，不冒称本篇亲测 |
| [MatchKind](https://docs.rs/aho-corasick/1.1.5/aho_corasick/enum.MatchKind.html) 的 `abcd/b`、`a/ab` 与顺序互换、`Sam/Samwise` 对照 | 语义范围来源，不展开或转载不同词表的附加图 |
| docs.rs 类型/模块/trait目录、GitHub导航 | 排除，与教学对象无关 |
| ACM 原论文正文图表、cr.yp.to 镜像内容 | 已遇 403，停止；数量、页码、完整素材范围未核，未采用，也未绕过访问限制 |

GitHub 网页正文及版本标签可读；原文件下载受限、API 请求不可用，未重试或另换路径取得受限文件。ASCII 与许可采用可访问网页文本的转录，不冒称下载原件。MIT 的文档授权与通知要求见附页及 [完整许可](originals/LICENSE-MIT.txt)。原来源中的代码与预期断言不是第三方真实运行截图；外链文档也不因公众可见而自动获得本篇再授权。

## 许可

- 原创正文、`00`–`14` 的原创教学图及本篇界面截图：由 zyuanming 发布，采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名时请链接本篇并注明修改。
- 本篇 `examples/` 内的原创 Python 代码、生成的 JSON 数据与元数据：以 [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) 提供。生成的 PNG 图仍按上一项 CC BY 4.0。
- `originals/design-trie.txt`、`originals/design-failure.txt` 及 `15`–`16` 渲染图来自 Andrew Gallant，单独按 MIT 保留版权、许可和免责声明；不是 CC BY 原创图。中文说明仍为原创；源图渲染程序是本篇原创 CC0 代码。
- 外链论文和文档不在本篇原创授权范围内；没有因其公众可见而声称获得再授权。

## AI 辅助与复算

正文草拟、教学代码、程序制图、本次视觉缺口补正、教学 web 界面和来源转录整理使用了 OpenAI AI 助手；没有把生成图片说成实拍，也没有捏造亲测硬件或历史经历。算法代码在 Python 3.12.14 下实际运行，图像由 Pillow 与 Noto Sans CJK 渲染。实验输入、完整轨迹和确定性测试数量均保存在公开示例中，不依赖随机种子。

正文命中的四个区间、10 种切块方式、8001 组二进制小输入比较以及其他边界检查都可重新运行。图形几何自检只检查文字、边界、字号与像素，不能自动证明图义正确；公开示例不包含内部审读记录或运行日志。

补充插桩实际核验了四次插入路径、BFS 顺序、主线三次失败、上升 8 层/下降 5 层/最终深度 3、追加 x 的两次连续失败、密集输出反例的全部 9 项。过程图和界面都使用实际程序数据；真实浏览器截图与模型重绘具有不同身份，不能互相替代。
