# 来源与许可

- J Strother Moore，[A Linear-Time Majority Vote Algorithm](https://www.cs.utexas.edu/~moore/best-ideas/mjrty/)，作者本人说明“与 Bob Boyer 在1980年提出”的回忆，以及严格多数存在时的候选保证；[逐步演示页](https://www.cs.utexas.edu/~moore/best-ideas/mjrty/example.html)支持计数三条更新规则。本文不是该网页翻译，输入序列、图和中文解释均独立创作。
- Robert S. Boyer、J Strother Moore，[MJRTY: A Fast Majority Vote Algorithm，技术报告](https://www.cs.utexas.edu/~boyer/ftp/ics-reports/cmp32.pdf)，支持异名配对保留多数与程序思路。本文不为该报告标注未能确认的出版年份；1980年只用于作者本人的提出时间回忆。
- 本文9张纸条、无多数候选C反例、顺序改变与有限穷举均由附带 `examples/verify.py` 实际生成/核对。一般正确性解释由异名配对不变量直接推出；不依赖有限测试作全称证明。

## 图片

图1—12全部由本篇独立绘图代码生成，作者为本仓库文章创作团队，采用 CC BY 4.0。无第三方肖像、历史照片、网站截图或论文图的复制。作者网页的互动演示仅链接阅读，不将其界面当作本文原创图片。

| 文件 | 新增的理解作用 | 原始依据与处理 |
|---|---|---|
| assets/01-majority.png | 九张中的六张过半 | 自拟纸条模型，原创 |
| assets/02-mode.png | 众数未必严格过半 | 4/3/2自拟例，统一尺度原创 |
| assets/03-pair-proof.png | 两种合法抵消 | 自拟纸条模型，原创 |
| assets/04-state.png | 余堆压缩为两个变量 | 自拟纸条模型，原创 |
| assets/05-trace-start.png | 主例前四步归零 | results.json，原创 |
| assets/06-trace-end.png | 主例后五步计数变化 | results.json，原创 |
| assets/07-count-not-frequency.png | 余量不等于真实频数 | results.json，原创 |
| assets/08-counterexample.png | 最少票也可能是候选 | results.json，原创 |
| assets/09-two-passes.png | 第二遍验证的必要性 | results.json，原创 |
| assets/10-zero.png | 全部异名配对不可能过半 | 自拟纸条模型，原创 |
| assets/11-order.png | 无多数时顺序影响候选 | results.json，原创 |
| assets/12-verification.png | 有限穷举范围 | results.json，原创 |

原创正文和上述图片采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名 zyuanming / tech-articles，并保留原链接及修改说明。文献、网页及其图片不自动适用本篇许可。

代码全部独立编写，采用 MIT，完整条款见 `examples/LICENSE`。运行 `python examples/verify.py` 复现29,524次对照；绘图另需Pillow、fontTools及Noto Sans CJK，执行 `python examples/build_figures.py`。不宣称在真实投票或生产数据上做过实验。

AI辅助：资料整理、起草、教学图与代码由AI辅助完成；代码实际运行，图注、数值与适用条件据输出核对。没有虚构人物对白、采访或亲历。
