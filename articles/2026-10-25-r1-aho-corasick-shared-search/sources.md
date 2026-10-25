# 来源、许可与复算范围

本文是 2026-10-25 的 r1 新制作版本。正文、图形构图与示例代码均为本篇新写，未使用旧批次的正文、图片或历史未知上传对象。

## 事实来源

1. Alfred V. Aho、Margaret J. Corasick，*Efficient String Matching: An Aid to Bibliographic Search*，Communications of the ACM 18(6)，333–340，1975，DOI [10.1145/360825.360855](https://dl.acm.org/doi/10.1145/360825.360855)。用于核对作者、发表年、标题及“固定关键词集合的出现位置搜索”这一论文问题。书目及摘要可检索；本次未成功取得出版商全文，因此不宣称逐页核验原论文，不采用原论文图像、性能数字或历史成本叙事。
2. [aho-corasick 1.1.5 实现方文档](https://docs.rs/aho-corasick/1.1.5/aho_corasick/)。已读概览、重叠与不同匹配语义、流式接口和 prefilter 说明。仅支持现代库接口及性能取舍的事实，不用现代实现反推 1975 年的内部细节；随文 Python 为本篇教学实现，不是该 Rust 库的移植。
3. 正文对失败后缀、输出链、扫描摊还界和示例的解释是独立教学推演，具体数值由 [ac.py](examples/ac.py) 与 [results.json](examples/results.json) 支撑；有限测试不能替代理论证明，也不构成生产环境基准。

## 图片及其解释作用

全部图片都是新绘制的教学示意，不是历史原图、真实产品截图或实测设备照片；没有第三方视觉素材需要再分发。本文的核心对象是字符串与状态图，不涉及需要用照片辨认的实体设备。相关原论文图未收录：全文未取得，且未取得再分发许可；本文以原创结构图和实际教学程序输出表达机制，不将替代图冒称原图。

| 文件 | 新增的理解作用 |
|---|---|
| `00-cover.png` | 独立封面，建立词表、共享机器与文本的关系 |
| `01-trie.png` | 看见前缀共享与完整词仍可继续延伸 |
| `02-failure.png` | 区分不消费字符的后缀跳转和消费字符的树边 |
| `03-trace.png` | 对照逐字符执行的状态、失败发生点与输出 |
| `04-overlap.png` | 对照同一坐标尺度上的全部半开区间 |
| `05-stream.png` | 看见块间保留的状态和全局位置 |

图中运行结果来自 `results.json`，生成代码见 [build_figures.py](examples/build_figures.py)，尺寸与最小字号见 [figure-metadata.json](examples/figure-metadata.json)。这些是原创模型图及执行结果的绘制，不是软件屏幕截图。使用 Noto Sans CJK 字体绘制文字；字体文件未随稿分发。

## 许可

- 原创正文及六张 PNG 图：由 zyuanming 发布，采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名时请链接本篇并注明修改。
- 本篇 `examples/` 内的原创 Python 代码、生成的 JSON 数据与元数据：以 [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) 提供。生成的 PNG 图仍按上一项 CC BY 4.0。
- 外链论文和文档不在本篇授权范围内；没有因其公众可见而声称获得再授权。

## AI 辅助与复算

正文草拟、教学代码与程序制图使用了 OpenAI AI 助手；没有把生成图片说成实拍，也没有捏造亲测硬件或历史经历。算法代码在 Python 3.12.14 下实际运行，图像由 Pillow 与 Noto Sans CJK 渲染。实验输入、完整轨迹和确定性测试数量均保存在公开示例中，不依赖随机种子。

正文命中的四个区间、10 种切块方式、8001 组二进制小输入比较以及其他边界检查都可重新运行。图形几何自检只检查文字、边界、字号与像素，不能自动证明图义正确；公开示例不包含内部审读记录或运行日志。
