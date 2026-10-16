# 来源、图像身份与 AI 辅助说明

核查日期：2026-10-16。正文为面向学生的原创机制讲解。文中的棋局局面取自公开对局的常见着法序列；教学树、教学例子中的数字、搜索测量、Zobrist 手算示例与全部图表均由本文作者实际运行本仓库代码得到，不是原论文实验数据，也不是真实棋手的对局分析。

## 一手来源及支持范围

1. Claude E. Shannon，*Programming a Computer for Playing Chess*，Philosophical Magazine 41(314)，1950 年 3 月。用于核对 A 型/B 型策略的划分与香农对机器下棋问题的表述。本文不复述其评估项细节，也不把 1950 年的方案当成现代引擎的设计。
2. Alan M. Turing，*Intelligent Machinery*（1948，NPL 报告）与 Turing、Champernowne 的棋程序（后世称 Turochamp）。用于核对：程序由两人在 1948 年设计、当时机器无法运行、图灵 1952 年与 Alick Glennie 对局时由人工执行。本文没有 Turochamp 的原始代码，正文只描述其算法大意（列出双方走法、打分、取最高），并明确标注它从未上机运行。
3. John McCarthy 在 1956 年达特茅斯会议上提出 α-β 并推荐给 Alex Bernstein（Bernstein "unconvinced"）；Allen Newell 与 Herbert A. Simon 1958 年称 α-β"appears to have been reinvented a number of times"；Alexander Brudno 1963 年独立发表；Donald Knuth 与 Ronald W. Moore 1975 年整理；Judea Pearl 证明其期望最优性。以上沿革用于正文的历史段落，出处见下条与 [Alpha–beta pruning 条目](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)所列原始文献。本文没有把 α-β 归功于单一发明人。
4. Albert Lindsey Zobrist，*A New Hashing Method with Application for Game Playing*，Tech. Rep. 88，威斯康星大学麦迪逊分校计算机科学系。**这份报告的年份在不同文献里不一致**（维基百科条目引作 1969 年，很多后续论文引作 1970 年），本文没有核对到报告原件，因此正文不写年份，只写报告编号。用于核对 Zobrist 键的构造（每"棋子×格子"一个随机位串、按位异或组合）与增量更新方式。正文的 64 位随机数由本仓库固定种子生成，与原文的具体数值无关。
5. Eugene W. Myers 关于 O(ND) 差异算法的论文不属于本文范围；本文引用的搜索文献仅限上列各条。
6. Ken Thompson 的计算机象棋工作（1971 年为第一版 Unix 写的 `chess`、与 Joseph Condon 合作的 Belle、四至六子残局库）用于正文历史段落。Belle 的"世界冠军"称号与时间范围按公开记录表述，本文没有复现其硬件或棋力测试。
7. Deep Blue 的沿革（ChipTest → Deep Thought → Deep Blue）、1996 与 1997 两场比赛结果、1997 年版本的搜索深度（通常 6—8 层、部分局面超过 20 层）、Levy 与 Newborn 关于每层约 50—70 Elo 的估计，以及第一局第 44 手的随机走法事件，均按 [Deep Blue 条目](https://en.wikipedia.org/wiki/Deep_Blue_(chess_computer))及其所列原始资料核对。卡斯帕罗夫本人否认状态下滑与焦虑有关，正文如实保留这一分歧。

## 本文实际运行的实验

`examples/measure.py` 在纯 Python 标准库上运行，环境记录见 `examples/run-environment.json`。

- **走法生成正确性**：用 perft 对照三个公开的标准测试局面。初始局面 perft(1..4) = 20 / 400 / 8902 / 197281；Kiwipete 局面 = 48 / 2039 / 97862；第三个残局局面 = 14 / 191 / 2812 / 43238。全部与公开基准值一致。这是本文唯一与外部已知数值直接比对的实验。
- **极小化极大与 α-β**：同一局面 `r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq -`，同一评估函数，节点数与耗时见 `examples/measurements.json`。
- **走法顺序**：三种排序（生成顺序、MVV-LVA 吃子优先、同分打乱）在深度 5 的节点数。
- **置换表**：深度 4/5/6 在有表与无表两种情况下的节点数、探测数与命中数。深度 4、5 有表反而更慢，正文如实写出。
- **Zobrist**：16 步真实着法序列上逐步比较增量键与重算键；另有 4,000 步随机走子得到的 3,045 个局面用于碰撞检查。**这不是碰撞概率的证明**，只是本文实验范围内的观测。
- **地平线与静止搜索**：两个局面上深度 2—5 的评分，以及加静止搜索后的评分与节点数。静止搜索不展开非吃子走法，因此不会无限递归；本文没有实现迭代加深、杀手走法或历史启发。

**本文没有实现**：迭代加深、空着剪枝、主变例搜索、评估函数的调参、开局库、残局库、多线程或任何硬件加速。正文所有"秒数"都是这套纯 Python 实现在本文机器上的耗时，不能外推为其他实现或深蓝的性能。

## 原件图片盘点与使用边界

本文正文没有引用任何论文、书籍或游戏的原始图片。香农 1950 年论文、Turochamp 的手稿与 Deep Blue 的比赛棋谱均未随本文重新分发。

正文使用 7 张第三方真实照片，全部来自 Wikimedia Commons，均在正文中作为独立图片出现，并保留作者与许可：

| 文件 | 内容 | 作者 | 许可 |
|---|---|---|---|
| originals/photos/real-01-chess-set.jpg | 斯汤顿棋具俯视 | Wilfredor | CC0 |
| originals/photos/real-02-shannon.jpg | 克劳德·香农肖像 | Konrad Jacobs（瑞典国家科技博物馆藏） | CC BY 2.0 |
| originals/photos/real-03-turing.jpg | 艾伦·图灵，1951-03-29 摄 | Elliott & Fry | 公有领域 |
| originals/photos/real-04-mccarthy.jpg | 约翰·麦卡锡 | "null0" | CC BY-SA 2.0 |
| originals/photos/real-05-thompson-ritchie.jpg | 汤普森与里奇，1973 | 作者不详 | 公有领域 |
| originals/photos/real-06-deep-blue.jpg | 深蓝机柜（美国国家历史博物馆） | Anton Chiang | CC BY 2.0 |
| originals/photos/real-07-deep-blue-chip.jpg | 深蓝处理器 | Erik Pitti | CC BY 2.0 |

处理说明：

- 棋具原图为 5355×5354、13,325,356 字节，超过公众号每图 5,000,000 字节的限制。发布用副本按 LANCZOS 缩放到 1600×1600（394,815 字节），完整画面保留，未裁切、未生成内容；未修改的原件另存于私有工程。
- 汤普森与里奇照片本身只有 310×201 像素，这是该历史文件的原始尺寸，本文未放大后称其为高清。
- 香农、图灵、麦卡锡三张肖像按原文件尺寸嵌入，只做等比缩放与居中裁切以适配版面，没有改动人物、背景或添加内容。三张肖像的拍摄年代各不相同（图灵 1951 年、香农为瑞典国家科技博物馆藏件、麦卡锡为斯坦福时期照片），图注与正文均未暗示它们来自所讲述的历史现场。
- 未使用任何生成模型制造的人像、现场照片或伪历史照片。

**第三方 CC BY-SA 素材范围**：麦卡锡肖像采用 CC BY-SA 2.0。相应图片保留该许可；如对该图作改编，须按 CC BY-SA 2.0 的要求分享，保留作者、来源、许可链接及修改说明。本文对它的处理是等比缩放与居中裁切。文章集合不据此把其他独立作品统一改为 CC BY-SA。

## 原创视觉及证据身份

- 图 02、10、23 与封面：真实局面的棋盘摆法，由本仓库程序绘制，不是照片。
- 图 03—09、11、12、13、15、16：原创机制示意，数字取自 `examples/measurements.json` 或 `examples/horizon.json` 的实际运行结果。
- 图 07 的评分数字（+50、−900）是**为讲清 β 截断规则而选的教学值**，不是真实棋局的评分，图注与正文均已标明。
- 图 14：16 步真实着法序列上增量键与重算键相等的逐步核对结果。
- 图 17—22：第三方真实照片与原创文字说明的合成图；合成只做版面排布，没有改动照片内容。
- 图 01：第三方真实照片，未叠加任何图形或文字说明。
- cover.png：本文独立设计的封面，不计入正文图。

详细尺寸、最小字号与身份见 [figure-metadata.json](examples/figure-metadata.json)。全部原创图由可复现的 Python/Pillow 程序绘制，字号下限 40 设计像素（1062 像素宽画布，按 354 像素显示宽度折算约 13.3 像素）。

## AI 辅助的真实范围

本文由 Anthropic 的 Claude 在用户授权的技术科普文章任务中辅助研究、构思、撰写中文、编写并执行搜索程序、制作程序图、核查数值并修订。走法生成器用 perft 对照公开基准值校验，其余数值全部实际运行并保存原始输出。AI 生成的文字、代码与图本身不作为外部事实证据；历史段落中的年份、人物与事件以公开一手来源核对，未能核到原文的细节已在正文或本文件中说明。本文没有假装作者亲历过任何一场比赛或与任何当事人有过交流。

原创正文、原创图、封面与原创实验数据采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名可注明本篇题名及文章发布者；原创代码采用 [MIT](LICENSE-CODE.txt)。第三方照片、论文与外链资料的权利保留于各自权利人，不包含在上述授权中。
