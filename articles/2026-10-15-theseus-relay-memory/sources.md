# 出处、模型边界与素材权利

核对日期：2026-10-15。文中历史规则以 Shannon 本人的演示报告为主要依据；教学迷宫、证明组织、代码、路径和计数图为本篇构造，不是历史录像的逐帧测量。

## 1. 一手技术与历史资料

### Claude E. Shannon，Presentation of a Maze-Solving Machine

- 1951 年 3 月 15—16 日第八次控制论会议报告，会议记录于 1952 年出版。这里读的是 N. J. A. Sloane 与 Aaron D. Wyner 编《Claude Elwood Shannon: Collected Papers》（1993）重印，第 681—687 页，PDF 第 717—723 页。
- [实际阅读的完整扫描本](https://www.jonglage.net/theorie/notation/siteswap-avancee/refs/books/Claude%20Shannon%20-%20Collected%20Papers.pdf#page=717)。该链接是扫描本载体，不是作者机构；报告作者及会议来源以扫描本题头、正文、书中编号 70 的书目为准。
- p.681：5×5 隔板、感知触头、两个方向电机、可移动目标、非随机策略、再跑与陌生起点、改变隔板后的循环演示。
- p.682 图 1：机械与面板示意；p.683 图 2：作者与设备照片。两张相关原图均有明确页链接供查看，未把扫描图改标原创。
- p.684：约 75 个全机继电器；每格两个记忆继电器；逆时针旋转；碰墙也写入方向；当前入格第一候选跳过来处；24 计数后改回探索。
- p.685：目标策略、最后离开方向消掉死胡同/环路；计数切换；并非必选最佳路线。
- p.686：目标模式遇墙转向但不立即换模式；若要寻找最短路需更多存储与比较；无目标时继续寻找。
- p.687：向量场解释；反向不唯一，不能仅从最终记忆还原来路。
- 报告是演示与问答文字，不是完整电路施工图。本篇不补造复位线路、触点时序、机械速度，不把感知触头版与鼠形版的每项细节合并成精确规格。

### OMRON，Overview of General Purpose Relays

- [官方技术说明](https://www.ia.omron.com/support/guide/36/introduction.html)
- 支撑线圈、磁作用、触点、常规释放及锁存继电器的区别。本文图 2 是自绘简化原理图，不复制厂家结构图，也不声称该厂家型号被用于历史机器。
- 该页有多种结构、动作与产品图。本文只引作通用原理出处，无开放复用许可的厂家图均不放入本篇附件。

### Nokia Bell Labs 的历史与媒体资料

- [Information Theory Turns 75](https://www.nokia.com/bell-labs/about/history/innovation-stories/information-theory-turns-75/)：含 Theseus the Mouse 影片入口，明确介绍磁性鼠与继电器迷宫。
- [该页链接的影片](https://www.youtube.com/embed/nS0luYZd4fs)：提供读者观看入口；本文未声称完整播放或测量此视频。不可用影片入口的存在替代其全部画面、声音已检查的证据。
- [百年媒体资料中的 Claude Shannon and Theseus 照片](https://www.nokia.com/about-us/newsroom/media-resources/nokia-bell-labs-centennial/)：用于把读者引向真实设备与人物资料。网站版权与公开传播条款见 [Nokia Terms of use](https://www.nokia.com/notices/terms/)。未把“有下载按钮”视作给整张历史图片的开放再授权，故只提供链接。
- [ZKM 馆藏影片条目](https://zkm.de/en/artwork/theseus-mouse-with-a-memory)：记录 1952 年、16 mm 转视频、8:27 与 AT&T Archives and History Center 来源。它是现代馆藏说明，本文不依其简化的墙状态描述覆盖 Shannon 本人报告的规则。

## 2. 与史料不同、属于本文的东西

- 3×3 A—I 迷宫、初始方向全西、A 起点与 C 目标。
- “进入方向”按回头边处理且只跳过入格第一候选的事件级实现；不模拟电机与继电器的全部时序。
- 以成功跨格作为计数单位、九格门槛 8、只关 F—C、24 次截断观察以及不清空箭头的策略切换。
- 全部路径、8/6、6/0、7/0、24/1 未到达、14/7 到达，以及 4096/1494/20 等数值都来自公开代码的实际运行。
- 最后出口的严格递增证明，是本文的解释；25 个格子的无环到达路径最多 24 条边，是数学推导。不声称后者就是设计者的私人动机。
- BFS 仅用作最短路比较，不是历史机器的算法，也不参与事件模型决策。

## 3. 肖像与版权

`assets/00-shannon.jpg`：ClaudeShannon MFO3807.jpg，Konrad Jacobs 摄。采用此前文章已合法取得的完整文件，284×400、37183 字节，逐字节复制；没有重新压缩、扩图、裁剪、补画或去水印。

- [Commons 文件、许可与 VRT 记录](https://commons.wikimedia.org/wiki/File:ClaudeShannon_MFO3807.jpg)
- [来源机构条目](https://opc.mfo.de/detail?photo_id=3807)
- Commons 标记权利人为 MFO，许可 [CC BY-SA 2.0 Germany](https://creativecommons.org/licenses/by-sa/2.0/de/)，VRT 票据号 2008042410024381；机构现行简略页版权字段为 unknown，本文采用的是 Commons 明确许可及其授权确认的这一文件版本，不把机构简略页当成新的许可。
- 该 Commons 版本已有黑白调整与水印移除历史；这些修改不是本篇所做。拍摄日期未核实，2015 年条目日期不当作拍摄日期。
- 文件 SHA-1：`47b8102ca2aac79a4b54bd788e83fee213601ce4`，与文件页当前结构化校验值一致。
- 完整许可 URI：[https://creativecommons.org/licenses/by-sa/2.0/de/legalcode](https://creativecommons.org/licenses/by-sa/2.0/de/legalcode)。本肖像不改用 CC BY 4.0。集合中其他独立原创内容按各自许可，不声称肖像权利人背书。

## 4. 原创图和输出

`assets/01-machine.png` 至 `assets/15-results.png`，以及独立的 `cover.png`：本篇原创教学图。没有生成式伪历史照片，没有复制原报告的图面、设备照片或厂家图。图 1 是功能框图，图 2 是通用原理，图 3 是教学编码，图 4—15 是自构迷宫、其解释或真实程序日志绘图。

原创正文和上述原创图以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 授权，署名 zyuanming；[完整许可](licenses/CC-BY-4.0.txt)。原创 Python 代码采用 [MIT](LICENSE-CODE.txt)。结果 JSON/CSV 为本篇原创模型数据，按 CC BY 4.0 提供。

原报告两张图、Nokia 设备照、影片、其他链接资料的权利未转移给本文。它们通过原站链接查看，不能因本文许可而自由复制。

## 5. AI 辅助使用说明

本篇中文写作、研究梳理、模型与绘图代码由 OpenAI AI 助手辅助生成并迭代；程序已实际运行，数值与图由对应输出复算。并非作者亲手操作了 Theseus，亦非对原机作了新的测量。肖像是真实第三方照片，未用生成式图像工具替代历史实物。文中“我们”指读者可以跟随的教学演算，不代表虚构的历史见闻。
