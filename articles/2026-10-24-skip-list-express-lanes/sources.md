# 来源与许可

- William Pugh，*Skip Lists: A Probabilistic Alternative to Balanced Trees*，Communications of the ACM 33(6), 1990。[作者论文的大学保存副本](https://15721.courses.cs.cmu.edu/spring2018/papers/08-oltpindexes1/pugh-skiplists-cacm1990.pdf)。已阅读的论文内容支持各层前向指针、有序搜索、记录update前驱、插入删除的局部拼接、独立随机高度及概率性能边界。本文不引用其具体机器性能数字，不声称本文实验复现了原文基准。
- 七键表、查28、插25、删21以及5,000次混合操作与四规模计数实验均为独立构造。数学期望由几何级数解释；一般期望复杂度的简述不替代论文正式概率分析。
- 原论文图、版面及伪代码未复制到本文；原链接供进一步阅读。本文代码按上述规则独立实现，是顺序教学模型，无生产级并发安全承诺。

## 图片来源

图1—13均为本仓库文章创作团队原创，由 `examples/build_figures.py` 绘制，采用CC BY 4.0。没有第三方照片、产品界面、论文原图或历史文物图。节点位置是逻辑排版，不是真实内存布局。

| 文件 | 新增的理解作用 | 数据及变更 |
|---|---|---|
| assets/01-lane.png | 底层完整、上层稀疏 | 自拟结构，原创 |
| assets/02-towers.png | 同节点多个下一站 | results.json，原创 |
| assets/03-search-high.png | 高层不跨越目标 | results.json，原创 |
| assets/04-search-low.png | 降层直到最终确认 | results.json，原创 |
| assets/05-predecessors.png | 三层前驱书签 | results.json，原创 |
| assets/06-splice.png | 先接旧下一站再改前驱 | 自拟局部赋值，原创 |
| assets/07-inserted.png | 插入后结构 | results.json，原创 |
| assets/08-deleted.png | 删除后结构 | results.json，原创 |
| assets/09-coin.png | 高度与连续升层结果 | results.json，原创 |
| assets/10-level-expectation.png | 各层期望数量 | results.json，原创模型计算 |
| assets/11-bad-luck.png | 所有节点矮的退化 | 自拟反例，原创 |
| assets/12-space.png | 平均指针数的空间账 | results.json，原创模型计算 |
| assets/13-costs.png | 实际链接检查次数 | results.json，原创运行结果 |

原创正文及上述图采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名 zyuanming / tech-articles，保留原文链接并注明修改。文献本身及其图片不自动采用本篇许可。

代码独立编写并采用 MIT，见 `examples/LICENSE`。`python examples/verify.py` 复现实验；绘图另需 Pillow、fontTools、Noto Sans CJK，运行 `python examples/build_figures.py`。随机种子、具体试验规模、输出版本与结果保存在 `results.json`。图13比较的是定义明确的操作次数，不是运行时间或产品排名。

AI辅助：资料梳理、中文起草、代码和教学图由AI辅助完成，实际运行程序并核对输入输出。没有虚构历史对白、采访或真实设备实验。
