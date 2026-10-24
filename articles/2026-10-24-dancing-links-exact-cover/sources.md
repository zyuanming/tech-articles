# 来源与许可

- Donald E. Knuth，[*Dancing links*](https://arxiv.org/abs/cs/0011047)，arXiv提交日期2000-11-15。本文实际查阅其原始摘要与元数据，用于核实作者、日期、可逆双链局部操作、精确覆盖及拼块身份约束这几个出处性主张；未把摘要阅读冒充全文大型实验核验，也不使用其大型拼板性能数字。
- David S. Hardin，[*Verification of a Rust Implementation of Knuth’s Dancing Links using ACL2*](https://arxiv.org/pdf/2311.08862)，EPTCS 393 (2023), 161–174，DOI 10.4204/EPTCS.393.13。已读第1—2页的精确覆盖定义和保留被删节点邻居说明、第7—8页remove/restore代码及第11页恢复定理的前提。它是作者对自己Rust实现的研究，不是Knuth原论文；这里只用来交叉核对摘链/接链机制与恢复前提，不把其形式化证明归给本文Python程序。
- 六编号七包为独立构造，不取自上述论文。二维求解器和小例推导独立编写；主例128种行子集、200张随机小矩阵、每节点字段恢复的核对见 `examples/verify.py` 和 `results.json`。有限测试不等于形式化证明。

## 图片来源

图1—12由本仓库文章创作团队独立绘制，均采用 CC BY 4.0。没有复制或改绘上述论文的具体图片/版面。双链关系与稀疏表是独立例子的算法示意，不是历史原稿照片或软件截图。

| 文件 | 新增的理解作用 | 原始依据与变更 |
|---|---|---|
| assets/01-packages.png | 七种包包含的编号 | 自拟算例，原创 |
| assets/02-matrix.png | 每列恰好一次的完整模型 | results.json，原创 |
| assets/03-choose-g.png | 选行引起的冲突排除 | results.json，原创 |
| assets/04-empty-column.png | 未满足空列代表失败 | results.json，原创 |
| assets/05-solution.png | A、D、E成功分支 | results.json，原创 |
| assets/06-unlink.png | 摘链但保留旧邻居 | 独立L/x/R示意，原创 |
| assets/07-relink.png | 两侧指针恢复原位置 | 独立L/x/R示意，原创 |
| assets/08-sparse.png | 仅14个非零节点的行列关系 | results.json，原创 |
| assets/09-cover.png | cover列1具体移除哪些节点 | results.json，原创 |
| assets/10-reverse-order.png | 操作与撤销的逆序 | 自拟G分支，原创 |
| assets/11-small-column.png | 最少候选列的启发式 | results.json，原创 |
| assets/12-verification.png | 完整解集与恢复验证范围 | results.json，原创 |

原创正文与上述原创图采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名 zyuanming / tech-articles，保留原文链接并注明修改。一手论文和它们的图不自动套用本库许可；这里只提供来源链接。

代码独立创作，采用 MIT，全文许可见 `examples/LICENSE`。运行 `python examples/verify.py` 复现所有核对；图形另需 Pillow、fontTools、Noto Sans CJK，运行 `python examples/build_figures.py`。没有复制Knuth原代码，也没有运行他人的Rust证明工具。

AI辅助：资料整理、中文起草、原创代码与示意图由AI辅助完成，正文数值与状态实际由程序重算。未虚构历史人物故事、访谈或亲历实验。
