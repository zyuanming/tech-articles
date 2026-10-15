# 来源、图像身份与权利

核查日期：2026-10-15。本篇六变量四子句配置题、决定顺序、图形布局、枚举实验和中文讲解为原创构造，不是论文例题或图表的逐项翻译。

## 一手出处与支撑范围

1. [João P. Marques-Silva、Karem A. Sakallah：GRASP: A Search Algorithm for Propositional Satisfiability](https://people.eecs.berkeley.edu/~alanmi/courses/2005_290A/papers/grasp.pdf)，IEEE Transactions on Computers 48(5)，506–521，1999 年 5 月。核对论文标题、作者、年份，并参考其第 2 节对子句、单位传播与蕴含图的定义，第 3 节关于冲突分析、学习、回跳、唯一蕴含点的机制。历史表述仅称该论文系统讨论这些方法，不宣称其作者独自发明了所有回溯或学习思想。本文没有引用其性能数字，也未复制原图。
2. [MiniSat 官方论文目录](https://minisat.se/Papers.html)及 [An Extensible SAT-solver，作者托管扩展版](https://minisat.se/downloads/MiniSat.pdf)，Niklas Eén、Niklas Sörensson，SAT 2003。这里的 2003 指会议年份；[Springer 出版记录](https://doi.org/10.1007/978-3-540-24605-3_37)将其修订论文集的出版与版权年份记为 2004，页码 502–518。两者应区分。支撑两位作者、会议年份、紧凑可扩展求解器设计的简述。本文不把扩展版的小版本号当成 2003 年软件版本，也未实际运行 MiniSat。
3. [MiniSat 作者仓库 Solver.cc](https://raw.githubusercontent.com/niklasso/minisat/master/minisat/core/Solver.cc)。用于核对当前层计数、倒序遍历理由、第一 UIP 停止条件、回跳目标以及学习子句管理的实际代码组织。正文附带 Python 为原创教学实现，不复制该源码；该外部仓库的许可仍按原仓库规定。

## 原创视觉覆盖

01 决定层与跨层回跳；02 六个布尔开关；03 原题四条规则；04 满足、单位、冲突三个状态；05 实际赋值轨迹；06 实际理由图；07 消去 v；08 消去 u 并学习；09 一般归结的逻辑依据；10 当前层路径与 UIP 切口；11 回跳后强制赋值；12 64 个真实枚举结果逐格显示；13 学习对两个 z 分支都有效；14 实际验证的一份完整解。另有独立封面。

所有 PNG 均由本目录原创程序绘制，没有第三方照片、论文截图、界面截图或生成式历史图片。逻辑节点、连线、赋值轨迹与真值表就是本题关键对象；本篇不依赖人物或设备照片讲述机制。论文原图供读者通过原链接查阅，未获开放再分发许可，不纳入公开目录。

原创中文正文、图像、实验数据按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 发布；原创程序按 [MIT](LICENSE-CODE.txt) 发布。外部论文、网页和代码保持其自身权利，本篇许可不扩展到这些外部材料。

## AI 辅助情况

本篇使用 AI 辅助研究、写作、编程、绘图与本地验证。没有虚构采访、亲历、历史对白或工业求解器实测。公开代码与结果允许读者实际复算；内部审读和手机静态代理不属于正文或平台发布证据。
