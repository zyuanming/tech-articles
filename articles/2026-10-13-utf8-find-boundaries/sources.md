# 来源、实验与图片说明

## 这篇文章解释什么

核心问题是：从一个合法 UTF-8 字节流的中途进入，如何凭局部字节找回下一个码点边界；为什么这种自同步不等于纠错、输入验证或字素分割。贯穿例为 A中𠮷B，字节 41 E4 B8 AD F0 A0 AE B7 42。“𠮷”明确为 U+20BB7。

正文、教学构图与例子是为本篇独立编写的解释，不是翻译某一篇来源。本文使用 AI 辅助资料查找、写作、编程和原创教学制图。实验均为本地字符串与编码模型，没有实测网络、硬件或生产系统。

## 事实的一手依据

- [Unicode 17.0 第3章](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)，重点是 3.9 与 3.9.3、表3-6和3-7、定义D92。支持标量值范围、代理码点排除、最短形式、UTF-8字节布局与合法性。未分配位置和非字符不等于病式字节序列，参见同章一致性要求。本文的槽位示意是据规则重做的教学图，没有嵌入规范的截图或原表图片。
- [RFC 3629，F. Yergeau，2003年11月](https://www.rfc-editor.org/info/rfc3629/)，重点是第3、4、6、10、12、13节。支持ASCII兼容、自同步特征、1—4字节限制、过长编码与无效序列、历史方案区别。字节编号与手算结果另外交由配套程序核对。
- [Rob Pike、Ken Thompson：Hello World](https://9p.io/sys/doc/utf.html)。支持Plan 9面对旧字节流接口的设计约束、早期方案的自同步问题、此前系统改造与后来编码替换的区别。该链接是包含后续更新的HTML版本，不把它说成未改动的1993年扫描件；正文不复刻原文全部叙事。
- [Pike关于UTF-8历史的邮件与所附档案](https://www.cl.cam.ac.uk/~mgk25/ucs/utf-8-history.txt)。餐馆桌垫叙述来自2003年回忆；材料同时包括对1992年邮件和代码记录的核查。正文把回忆与档案分开，不虚构对白、准确餐馆日期或现场照片。
- [Python codecs：增量解码器](https://docs.python.org/3/library/codecs.html)。支持增量接口与final参数的行为约定。具体E4/B8/AD输出、严格与替换策略均由Python 3.12.14实跑；不会把持续更新的文档网页版本冒充运行环境版本。
- [Unicode UAX #29](https://www.unicode.org/reports/tr29/)，支持扩展字素簇是高于码点边界的分割层次，默认规则可能需要语言或应用定制。本篇不实现或测试完整字素分割。
- [Unicode UTF/BOM FAQ](https://www.unicode.org/faq/utf_bom.html)与[Compression FAQ](https://www.unicode.org/faq/compression.html)，用于区分编码形式与压缩、解释不同文本的空间需求。本文未声称哪一种编码对所有文本最省空间。

上述网页查阅于2026-10-13。原文著作权归各自权利人；列出参考资料不表示获得对第三方原文、商标或图片的再授权。

## 原链接图像清点与人物材料

本文的核心对象是字节流、编码布局与边界，不依赖一张特定设备照片。所读《Hello World》HTML正文未含嵌入的img图片；其代码、公式与文字不被另算为“原图”。Unicode规范中的UTF-8规则表是事实参考，本篇用原创大字布局解释，并未把原表截图冒充原创。

正文提供两张真实人物照片的外链，未将其图片文件打包进本文：

- [Rob Pike在2010年OSCON，Kevin Shockey摄影](https://commons.wikimedia.org/wiki/File:Rob-pike-oscon.jpg)。文件页标注CC BY 2.0。它是2010年活动照片，绝非1992年设计现场。
- [Brian Kernighan与Ken Thompson，A. C. Diller摄影，2019年5月4日](https://commons.wikimedia.org/wiki/File:Brian_Kernighan_and_Ken_Thompson.jpg)。文件页标注CC BY-SA 4.0，场景是Vintage Computer Festival East采访。本文只链接来源页，没有裁掉另一人物后改变场景含义。

未使用AI生成的历史人物肖像、餐馆桌垫或伪造史料。外链照片的作者、许可与其他权利仍以其来源页为准，本文的CC BY 4.0不覆盖它们。

## 真实运行的实验与边界

[utf8_lab.py](examples/utf8_lab.py)只依赖Python标准库；[results.json](examples/results.json)是实际输出。本次Python为3.12.14，内置Unicode数据库15.0.0。测试的是现代UTF-8稳定的标量值/字节规则，未声称验证Unicode17的全部新字符属性。

- 穷举1112064个标量值，教学编码器逐个与Python编码比较，并严格解码回原数；长度分布为128、1920、61440、1048576。
- 穷举256个一字节及65536个两字节完整输入，接受/拒绝与Python严格解码一致；合法数量128与18304。
- 检查九字节样本全部10个进入位置（含末尾），每次跳过续字节最多3个。
- 穷举样本8个可切边界的256种分块方式，增量解码全部恢复原文。
- 检查10个明确非法例子，包含过长编码、代理值、范围越界、错误续字节与截断。另断言不完整流在final=True时抛错、E4 41 AD替换为�A�、Latin-1解释差异和“文”的手算答案。

这些是有限可复现的模型测试，不是全体任意长度字节串的穷举，也不是生产解析器安全审计、性能基准或网络抓包。

[可拖动实验](examples/boundary-lab.html)只接受固定合法样本上的0—9位置，使用浏览器内置TextEncoder/TextDecoder显示剩余后缀；它不将“非续字节”当未知输入合法的证据。关闭脚本时有文字回退，正文另有完整静态解释。图13动画的9帧分别代表9个非末尾起点，整幅动画计为一张正文图。

## 原创视觉清单

正文共27个视觉对象：26张PNG与1个GIF；另有独立封面。不是把GIF帧、图内面板或交互状态分别算作额外图片。位槽、索引、分类树、手算分装、流缓冲、反例与历史约束各承担不同解释职责。下表字号是原图720像素宽的关键标注基准；缩到约354像素时，26像素约为12.8像素。主体信息仍在相邻正文解释，不要求放大查看才能读懂主线。

| 文件 | 新增的理解作用 | 宽×高 | 关键字基准 |
| --- | --- | --- | --- |
| `assets/01-cut-through-text.png` | 把已编码文本从“中”的中部切开，提出恢复边界的问题 | 720×665 | 26 px |
| `assets/02-three-layers.png` | 字形、码点、字节三个层次相互关联但不能混称 | 720×815 | 28 px |
| `assets/03-one-byte.png` | 八个位与一个字节数值的关系 | 720×565 | 27 px |
| `assets/04-hex-as-shorthand.png` | 1110与0100分别缩写为E和4，补齐十六进制前置 | 720×665 | 26 px |
| `assets/05-ascii-keeps-place.png` | ASCII兼容及常见分隔符不会出现在多字节内部 | 720×660 | 26 px |
| `assets/06-lead-versus-tail.png` | 前缀控制与数据负载分色，建立字节角色 | 720×655 | 28 px |
| `assets/07-four-envelope-sizes.png` | 完整1—4字节布局与负载位容量，非逐字截图 | 720×1270 | 28 px |
| `assets/08-split-zhong.png` | 中码点的16位被按4/6/6实际拆分 | 720×815 | 26 px |
| `assets/09-encode-zhong.png` | 同一负载插入不同前缀，生成三个字节 | 720×853 | 26 px |
| `assets/10-four-byte-character.png` | 补充平面汉字的实际四字节位布局 | 720×1090 | 28 px |
| `assets/11-whole-byte-stream.png` | 四个码点连成九字节，分组与首尾角色同时显示 | 720×585 | 26 px |
| `assets/12-find-next-boundary.png` | 逐步分类B8、AD、F0，区分重同步与找回丢失数据 | 720×700 | 26 px |
| `assets/13-every-cut.gif` | 九个不同切点下的跳过数与完整后缀；首帧自洽 | 720×740 | 27 px |
| `assets/14-prefix-tree.png` | 前缀分类树解释为什么尾部与首部互斥 | 720×755 | 26 px |
| `assets/15-backward-bound.png` | 四字节最大长度给出的局部反向定位范围 | 720×608 | 26 px |
| `assets/16-candidate-not-valid.png` | E4 41 AD反例：形式起点不等于合法完整序列 | 720×620 | 28 px |
| `assets/17-validation-gates.png` | 解码器从结构、最短性、数值三个层次拒绝非法输入 | 720×760 | 26 px |
| `assets/18-overlong-slash.png` | 过长编码以同一斜杠对照，解释最短性必要 | 720×770 | 28 px |
| `assets/19-scalar-value-ranges.png` | 标量值范围和代理空洞，避免只背1—4字节 | 720×700 | 26 px |
| `assets/20-stream-chunks.png` | 跨网络块的半个码点需要缓存，而不是丢弃 | 720×711 | 26 px |
| `assets/21-incremental-state.png` | 逐块真实输出与缓冲状态，解释有状态流解码 | 720×830 | 26 px |
| `assets/22-grapheme-versus-codepoint.png` | 预组字符与组合重音展示1个与2个码点的视觉对应 | 720×775 | 26 px |
| `assets/23-deletion-and-resync.png` | 删字节的局部损坏与后续可定位性分开 | 720×638 | 27 px |
| `assets/24-encoding-is-agreement.png` | 字节合法性不足以识别未知来源编码的可运行反例 | 720×635 | 26 px |
| `assets/25-which-length.png` | 相同可见单位在码点数与字节数两种指标下不同 | 720×920 | 26 px |
| `assets/26-design-constraints.png` | 把历史设计取舍表现为同时满足的三项约束 | 720×711 | 26 px |
| `assets/27-error-policy.png` | 相同非法输入在严格/替换策略下的真实输出 | 720×690 | 26 px |

封面为原创主题构图，用于文章入口，不将封面另算一张正文解释图。

## 许可

原创正文、原创教学图与原创封面采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。署名可使用“tech-articles 原创探索文章”，并链接到本文及许可、标明修改。配套原创程序与交互代码采用[MIT许可](examples/LICENSE.txt)。本篇图中没有重新打包第三方照片或原文截图；所链接第三方材料保留各自权利。
