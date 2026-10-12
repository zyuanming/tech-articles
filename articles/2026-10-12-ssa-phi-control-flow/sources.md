# 来源、图像取舍与实际实验范围

本文是原创中文解释。AI辅助用于检索、中文组织、原创机制示意绘制和代码实现；历史、定义、代码和最终图文分别核验。没有虚构亲历、研究者对白、真实编译器性能测试。全部正文图、GIF和示例代码为本稿原创，采用CC BY 4.0；没有把第三方照片或论文图纳入这个许可。

## 一手事实

1. Ron Cytron, Jeanne Ferrante, Barry K. Rosen, Mark N. Wegman, F. Kenneth Zadeck, **Efficiently Computing Static Single Assignment Form and the Control Dependence Graph**, *ACM Transactions on Programming Languages and Systems*13(4), October1991, pp451–490，DOI[10.1145/115372.115320](https://doi.org/10.1145/115372.115320)。[原论文PDF，UT Austin课程托管](https://www.cs.utexas.edu/~pingali/CS380C/2010/papers/ssaCytron.pdf)。
   - 原首页给出五位作者、1989年POPL前身与期刊October1991。少数机构数据库把日期表示成Jan10，本文以实际期刊页脚为准。
   - 451–455页：工程构造成本、定义与使用、常量传播、支配边界的动机。458页：按前驱选择phi及循环实例。
   - 464–465页：支配、严格支配和支配边界定义；第5节讨论构造和重命名。478–479页：去SSA、复制与死phi等边界。
   - 上述主要页已查看原生页面，其他局部通过PDF文本定位；没有声称全40页每条证明均已精读。本文的分数、奖励、累加和交换例子独立设计，不复制原图的布局或整段程序。

2. UC San Diego Jacobs School of Engineering，2006-06-12，**Programming Languages Award Recognizes Impact of Renaming Technique in Compilers**。[大学原报道](https://jacobsschool.ucsd.edu/news/release/547?id=547)。
   - 本文历史段采用Ferrante本人具名回忆：1985年Berkeley访学、重命名研究、与Cytron合作及控制依赖思路的结合。明确是事后回忆，不把报道中的修辞改编成现场对白。
   - 五位研究者是协作关系；本文不把SSA所有思想归为某一天、某一人的单独发明。

3. LLVM **18.1.8**，*Language Reference Manual*：[phi](https://releases.llvm.org/18.1.8/docs/LangRef.html#phi-instruction)、[well-formedness](https://releases.llvm.org/18.1.8/docs/LangRef.html#well-formedness)、[select](https://releases.llvm.org/18.1.8/docs/LangRef.html#select-instruction)。
   - phi的类型/值/前驱配对、位于块开头、输入值使用视作发生在来边，以及运行时按刚执行的前驱选值。
   - 本文没有把phi与不依赖IR分支的select混为一谈。LLVM专门示例只使用很小的i32常量；Python教学解释器使用无界整数，不声称二者覆盖相同的全部语义。

4. LLVM **18.1.8**，*The LLVM Target-Independent Code Generator*，[SSA deconstruction phase](https://releases.llvm.org/18.1.8/docs/CodeGenerator.html#the-ssa-deconstruction-phase)。支持phi需要保持语义地消去、复制与寄存器相关处理的说明；本文不实现完整后端。另参见[项目自己的PHIElimination实现说明](https://llvm.org/doxygen/PHIElimination_8cpp_source.html)中复制及必要拆边的职责；后者是查阅时的项目文档，不混称固定18.1.8代码实测。

5. Kenneth Zadeck，**The Development of Static Single Assignment Form**，[2009原讲义](https://compilers.cs.uni-saarland.de/ssasem/talks/Kenneth.Zadeck.pdf)，[2009-04-27至30研讨会原页](https://compilers.cs.uni-saarland.de/ssasem/)。作为历史背景核对：数据流分析成本、SSA发展是多个研究方向结合。只核读其中相关内容；没有采用个人健康叙述或把作者的工程评价扩写成普遍定律。正文关键历史事实仍以上面原论文和具名报道为准。

## 原文视觉素材为何没有复制进来

- 1991论文首页有ACM版权通知，复制许可带直接商业利益限制，重新发表另需许可。本文不把“网上能读到PDF”解释成可在公开文章包任意再发布。
- 相关原图可在原PDF直接查看：453页图1–3（中间表示/直线重命名/分支phi），454页图4（常量传播），458页图6（循环SSA），464页图9（CFG与支配树），第4–5节算法图（支配边界、phi放置、重命名），479页图16（死phi相关示例）。原稿全部留在其原始链接，没有截图冒充开放许可原件。
- UCSD报道包含Ferrante肖像与2006年Ferrante、Zadeck、Wegman合影。页面带Regents版权及all rights reserved，未核到适用于这些图片的开放再发布许可；因此保留原站查看链接，不复制照片。
- 曾主动寻找可合法复用的人物照片。Commons具体Ferrante2023文件页未成功取得，随后常规请求返回403，即停止；未取原图、未核该文件作者与许可，未借Wikidata缩略图或换入口绕过限制。不以“Commons常有开放图”代替具体文件核验。
- 这篇的核心对象是程序表示、控制流和值的来处，而非视觉人物传记。26幅原创图把这些对象完整展开；没有AI生成“历史人物照片”填补素材缺口。LLVM语法的展示是本稿自写示例，不是声称截取了实际编译器运行界面。

## 每幅原创视觉的作用

01–03：同名不同值、直路重命名、定义—使用关系。

04：有来源的两类历史问题，不是独自发明时间线。

05–07：分支汇合难题、phi来路配对、两次具体执行。

08–11：基本块控制流、两种箭头、支配、phi输入的边使用。

12–15：循环的两类来路、SSA循环、静态/动态区别、n=4实际轨迹。

16–17：同一块phi的并行赋值语义与错误覆盖反例。示意中的先读后提交是语义要求，不是假定CPU指令同时发生。

18–19：菱形和循环头的支配边界。图中的着色是教学突出，不是原论文截图或性能热图。

20–21：已知同常量的合并与沿使用关系传播；本文保守分析不含完整SCCP。

22–24：去SSA的边上交值直觉、内存别名边界、自写LLVM配对记法。

25：三项本解释器实际拒绝的非法例。

26：11帧GIF，源自解释器实际n=4事件序列；交付GIF的全部实际解码帧参与审读，非只核首帧。

所有图使用原创布局和中文说明，图像数量服从每个中间步骤，不将连续动画拆成独立篇幅。可打印或放大读图，但关键标签仍应在手机比例下可读。

## 实验与未执行范围

[ssa_lab.py](examples/ssa_lab.py)、[实验说明](examples/README.md)、[bonus.ll](examples/bonus.ll)。

实际环境Python3.12.14，标准库；未安装或执行LLVM。正文短Python例已执行，返回6；循环头phi轨迹依次为(0,0)、(1,0)、(2,1)、(3,3)、(4,6)。

- 9826组菱形输入，对比原始/常量替换版与独立条件表达式。
- 311个求和输入，对比Python的sum(range(n))。
- 1701组交换输入，对比直接同时交换。
- 2000个随机CFG，种子199110；固定点支配集合与独立删顶点后的可达性一致。
- 3个非法例实际拒绝；不由此声称检查器能捕获所有恶意或非法IR。
- 常量例实际路径加法数1→0，仅为模型计数；没有编译时间、CPU运行时间、内存峰值或生产编译器优化效果的测量。

代码不含前端、不自动构造任意源语言SSA、不实现SSA消除/寄存器分配、不处理指针别名和异常。有限测试不替代一般正确性证明。原创正文、图、代码的CC BY 4.0许可不扩张到上述第三方文献、照片、商标或项目源代码。
