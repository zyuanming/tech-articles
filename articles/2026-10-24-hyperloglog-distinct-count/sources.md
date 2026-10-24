# 来源与许可

- Philippe Flajolet、Éric Fusy、Olivier Gandouet、Frédéric Meunier，[*HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm*](https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf)，2007。已查阅摘要、引言与基本随机模型，支持作者/论文年份、不同元素计数目标、均匀哈希模型、分桶综合与约1.04/√m的常用相对标准误差尺度。未将它解释成单次误差上界，也不复述未重现的产品性能数字。
- Stefan Heule、Marc Nunkesser、Alexander Hall，[*HyperLogLog in Practice: Algorithmic Engineering of a State of The Art Cardinality Estimation Algorithm*](https://research.google.com/pubs/archive/40671.pdf)，2013。已读原文第2—3页经典HLL原始估计、α常数、小范围切换、线性计数公式，以及64位哈希和后续改进的区分。正文教学代码使用64位与经典小范围规则，没有实现全部HLL++改进，不声称与某个系统的二进制格式兼容。
- 逐桶max合并和不能一般删除的说明，由寄存器“只保存最大观测值”这一明确定义直接推出。短教学哈希、自拟16桶向量、实际SHA-256截取实验全部独立构造，见 `examples/verify.py` / `results.json`。不同盐下的32轮试验是有限确定性复现，不是对哈希独立性的数学证明。

## 图像

图1—14均由本仓库文章创作团队原创，采用CC BY 4.0。没有重印论文图片、用户日志、真实产品界面或人物肖像。所有“访客”只用自拟字母/整数编号表示，非真实个人数据。

| 文件 | 新增的理解作用 | 原始依据/变更 |
|---|---|---|
| assets/01-distinct.png | 访问数与不同身份数的区别 | 自拟输入，原创 |
| assets/02-hash.png | 相同身份固定映射 | 教学哈希表，原创 |
| assets/03-zero-probability.png | 前导零的稀有程度 | 公平位模型计算，原创 |
| assets/04-split.png | 选桶位与观测位分开 | 教学哈希表，原创 |
| assets/05-update.png | max更新与重复不变 | results.json，原创 |
| assets/06-registers.png | 索引与寄存器状态 | results.json，原创 |
| assets/07-harmonic.png | 两种平均对离群值反应 | results.json，原创 |
| assets/08-estimate.png | 原始估计的完整代入 | results.json，原创 |
| assets/09-empty.png | 空集合揭示偏差 | results.json，原创 |
| assets/10-linear-counting.png | 空桶修正的数值直觉 | results.json，原创 |
| assets/11-merge.png | 实际摘要逐桶合并 | results.json，原创 |
| assets/12-deletion.png | 无法恢复次大值的反例 | 自拟观测集合，原创 |
| assets/13-errors.png | 不同盐下真实误差散点 | results.json，原创 |
| assets/14-budget.png | 桶数与理论常用尺度 | results.json，原创 |

原创正文和上述图片采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名 zyuanming / tech-articles，转载保留原链接并注明修改。引用论文及其图片不自动适用本篇许可；原文仅链接阅读，未归档第三方图。

独立代码采用MIT，完整文本见 `examples/LICENSE`。Python 3运行 `python examples/verify.py`；绘图另需Pillow、fontTools、Noto Sans CJK，运行 `python examples/build_figures.py`。输入整数、盐值0—31、SHA-256前64位大端截取、桶数、误差统计和运行版本均可由代码/结果复现。没有测真实网站访客，没有把理论标准误差当作有限实验的保证。

AI辅助：资料梳理、中文起草、代码与教学图由AI辅助完成；实际运行数值核对、重复不变和合并等价检查。未虚构采访、人物对白或亲历体验。
