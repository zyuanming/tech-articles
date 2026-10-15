# 来源、实际运行与图片权利

## 核心范围与相邻旧稿

核心问题是具体实现一个从左往右读词元、通过左右门槛和前缀/中缀角色构建表达式AST的解析器。先看真实14/20砖排输出，再补词元、节点、游标、任务返回，逐步走完整个2+3*4，之后才引入左/右结合、前缀负号、括号、错误和代码。实验可选，主线不依赖运行或动画。

已核读本库[Hopper与编译器文章](https://github.com/zyuanming/tech-articles/blob/a93df95dec42846176ac05cb555f8fb656fd4e53/articles/2026-10-10-hopper-compilers/read.md)。旧稿沿词法、语法、语义、指令生成走全流程，展示过2+3*4的两棵树，但不实现树究竟怎样逐步构造。本篇沿用这个熟悉小例作为基础入口，新增重点是Pratt的严格比较、共享游标和每次调用的局部left、左右结合阈值、负指数前缀角色、括号消费边界及可运行差分验证，不重写Hopper史或编译流水线全史。正则、KMP和寄存器分配旧篇也不是同一核心问题。

## 来源与支撑范围

1. Vaughan R. Pratt，1973，[Top Down Operator Precedence](https://doi.org/10.1145/512927.512931)，Proceedings of the 1st annual ACM SIGACT-SIGPLAN symposium on Principles of programming languages，pp.41–51。ACM论文记录支持书目信息。本次原全文访问受限，没有取得该站扫描PDF，不冒称实看原扫描。
2. 同一论文的[公开重新排版转录](https://tdop.github.io/)，这是第三方转录的原论文文本，不是作者官网或史料扫描。核读§2.2的结合问题、§3 Implementation中的left、rbp/lbp严格比较、递归调用与nud/led角色，以及§4例子。本文只使用其机制并自行推导例子，不转载页面状态图、不复制整段论文，不把转录站当作新的发明人。
3. Robert Nystrom，《Crafting Interpreters》，[Compiling Expressions作者仓库原文](https://github.com/munificent/craftinginterpreters/blob/master/book/compiling-expressions.md)，特别是Parsing Infix Expressions与A Pratt Parser部分。作为现代语言实现的一手说明，用于核对词元两类处理、递归读右侧与结合性。该实现采用自己的优先级约定并输出字节码，本文则明确严格rbp<lbp和先建树的不同目标，不拼接两种条件的数表。没有复制书图、代码或作者主观评价。
4. [Python 3.12表达式规范§6.5](https://docs.python.org/3.12/reference/expressions.html#the-power-operator)及[§6.17](https://docs.python.org/3.12/reference/expressions.html#operator-precedence)，仅支持本篇所选算术子集的分组对照，尤其乘方右结合、前缀负号左右不对称与括号。语言规则不是所有语言的普适常数；优先级也不能自行决定有副作用操作数的求值先后。此网页在查阅时显示3.12.15文档，实际本地执行环境为3.12.14，两者身份不混写。
5. [Python ast官方文档](https://docs.python.org/3.12/library/ast.html)，用于ast.parse、ast.dump及BinOp/UnaryOp/Constant节点含义。ast.parse生成结构，不执行输入。本文没有对未知代码调用eval或exec。
6. Guido van Rossum、Pablo Galindo Salgado、Lysandros Nikolaou，[PEP 617](https://peps.python.org/pep-0617/)，Created 24-Mar-2020，Python-Version 3.9，支持CPython采用PEG解析器这条边界说明。本文结构对照不证明它内部使用Pratt。
7. [Graphviz DOT语言文档](https://graphviz.org/doc/info/lang.html)，支持节点/有向边描述及图布局工具的身份；实际使用的是已安装Graphviz2.42.4。本文不是Graphviz软件教程或性能测试。

核读日期2026-10-13。人物仅讲论文记录支持的姓名与发表身份，没有杜撰对话、动机或“偶然灵光”。引用来源用于查证，不改变来源文本的权利。

## 实际执行与边界

原创[parser_lab.py](examples/parser_lab.py)在Python3.12.14运行；结果完整保存在[results.json](examples/results.json)，真实CPython结构保存在[cpython-ast.txt](examples/cpython-ast.txt)。

- 严格rbp<lbp循环；加减(10,10)、乘除(20,20)、乘方(30,29)，前缀门槛25，EOF/右括号左强度0。
- 14个指定表达式与CPython AST结构对照；5000次随机生成表达式，种子314159，生成树深度参数4，操作符+ - * / **，名字damage/bonus及单数字原子；全部结构一致。
- 10个非法输入都被拒绝；7个指定算式的值与手算目标一致。8/0成功建树，求值报ZeroDivisionError。幂右门槛29改30的实际参数变异产生预期左右结合结构差异。
- 输出12个具体案例的词元、树、事件、调用次数。主例消费5普通词元，调用表达式函数3次，最大深度2；根任务深度0，EOF不消费。
- 数值中2**3**2=512，(2**3)**2=64；-2**2=-4，(-2)**2=4，2**-3=0.125；12+damage*4在damage=3时等于24。
- 砖排原PNG由[render_tiles.py](examples/render_tiles.py)实际取Parser与evaluate的输出绘制，Pillow12.3.0，两张均600×100且同格尺寸；不是游戏实图。图01是这两张原结果加就近说明的版式，图27为回顾复用，不将面板/复用结果拆成新增实证数量。
- Graphviz实际运行dot -Tpng/-Tsvg，根据原创DOT关系输出两组PNG/SVG。正文收录normal-graphviz.png原工具输出，其余保留可核对。前面的中文图是解释过程的原创图，不冒充软件截图。
- 事件动画根据实际results中事件取6个状态；它与图11静态步骤互补，6帧只计一张动画。
- 核心直接连节点、关闭追踪的固定规则解析在词元模型下线性；trace会反复把增长子树序列化，额外日志工作可能超线性。词法识别、任意精度数值运算、绘图、测试不含在核心O(n)断言里。
- 教学边界：最多3000字符，解析任务depth>128拒绝，数值绝对值不大于10^12、幂指数绝对值不大于16，非有限或复数拒绝；后续递归求值/序列化还有宿主栈限制。不是完整语言或通用安全沙箱。没有速度基准、生产引擎实测或“所有输入都正确”的证明。

## 视觉职责与文件清单

正文28个图片节点：26张原创解释/结果PNG、1个六帧事件GIF、1张真实Graphviz PNG。独立封面另计。原始砖排、另一组Graphviz输出与SVG作为附属可复核文件，不能再算成正文额外图。关键原创标注25—34px，720宽缩至354正文宽后约12.3—16.7px；实际版面由手机比例复看核验。

| 文件 | 本图新增理解作用 | 原尺寸 |
| --- | --- | --- |
| `assets/01-actual-tile-output.png` | 真实程序把两个分组结果画成14与20块同尺度砖排 | 720×840 |
| `assets/02-tokens-not-characters.png` | 先从实际多位数和变量名解释词元，不把字符逐个当数 | 720×850 |
| `assets/03-two-possible-trees.png` | 同样操作数的两种结构对应14和20，说明解析任务 | 720×1000 |
| `assets/04-parse-before-evaluate.png` | 区分词法、建树、求值和可见输出，避免把优先级等同算术 | 720×910 |
| `assets/05-tree-glossary.png` | 解释根、孩子、叶子和子树，为递归返回对象建模 | 720×830 |
| `assets/06-one-shared-cursor.png` | 把游标和已建好的left分开，强调不会反复扫描 | 720×760 |
| `assets/07-minus-two-roles.png` | 用负号和减法解释前缀/中缀处理，不让同一个字符只有一个动作 | 720×800 |
| `assets/08-strict-threshold.png` | 明确严格rbp小于lbp，等值停止是左结合的关键 | 720×810 |
| `assets/09-binding-table.png` | 把运算符左强度与右侧调用门槛放在同一张清晰表 | 720×860 |
| `assets/10-three-parser-tasks.png` | 显式展示递归帧各有left但共享游标，解释尚未返回时的状态 | 720×1000 |
| `assets/11-main-trace-static.png` | 给主例全部关键状态的静态回退，不依赖动画 | 720×1050 |
| `assets/12-trace.gif` | 实际事件日志驱动的游标和left同步动画，六帧只计一个视觉 | 720×840 |
| `assets/13-return-a-subtree.png` | 圈出调用返回的整棵乘法树，降低递归对象的抽象程度 | 720×850 |
| `assets/14-subtraction-association.png` | 减法两棵树数值反例，说明左结合是语法约定 | 720×960 |
| `assets/15-equal-power-stops.png` | 解释等强度终止时不消费词元，因此外层可完成左结合 | 720×800 |
| `assets/16-power-association.png` | 右结合幂与左结合的512/64反例，实际树与值对应 | 720×990 |
| `assets/17-one-threshold-changes-tree.png` | 实际参数变异把右结合改成左结合，说明两种绑定数职责 | 720×830 |
| `assets/18-unary-and-power.png` | 把前缀负号与幂的分组差异画成真实树 | 720×980 |
| `assets/19-prefix-threshold.png` | 用25与30的具体比较解释一元负号范围 | 720×750 |
| `assets/20-parenthesis-contract.png` | 明确左括号调用表达式，右括号由调用方核对并消费 | 720×890 |
| `assets/21-double-star-token.png` | 说明最长符号优先匹配，解析门槛不能修复错误词元化 | 720×760 |
| `assets/22-real-error-locations.png` | 显示四种实际拒绝输入的精确位置与可懂错误职责 | 720×1000 |
| `assets/23-parse-versus-runtime-error.png` | 真实除零反例分离语法错误和求值错误 | 720×830 |
| `assets/24-cpython-actual-structure.png` | 保留真实CPython AST层级并清楚区分结果同与算法同 | 720×850 |
| `assets/25-linear-work-deep-stack.png` | 区分线性总工作量与最坏递归深度，不承诺任意长输入安全 | 720×850 |
| `assets/26-historical-mechanism.png` | 以论文身份与原机制收束历史，不杜撰人物故事或照片 | 720×860 |
| `assets/27-whole-route.png` | 将核心机制接回真实可见结果，形成读者可复述闭环 | 720×980 |
| `examples/normal-graphviz.png` | 实际解析树经Graphviz直接布局的工具输出，对照手工解释图 | 443×611 |

写前视觉计划已落实到字符/词元、树形、游标、门槛、递归帧、逐步返回、反例、错误、实际工具与输出。第16节沿用第15节负号图，就近解释任务起始阶段与中缀循环阶段；第22节代码是前面已解释动作的压缩，不另造满页代码截图；第25节动手建议复用已经看过的结果，不强制读者运行实验。其他关键章节均配其对象或实际状态的视觉。

## 原材料范围、许可与AI辅助

本文没有转载论文状态图、书中插图、人物肖像、软件界面或第三方游戏素材；核心真实锚点是实际程序生成的砖排、Graphviz原输出和CPython原始文本。结构树和算术符号是本文从明确输入独立构造。没有AI生成的伪历史照片或伪运行截图。

原创正文、解释图、封面、原创输入及程序输出采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名“tech-articles 原创探索文章”，附原文、许可及修改说明。原创Python代码采用[MIT许可](examples/LICENSE.txt)。Graphviz和Python软件本身的许可证不会因此改变，本文不分发其软件或声称第三方为本篇背书。

使用AI辅助研究、写作、编码和绘制原创解释图；标作程序输出的材料均由随附代码/明确工具真实运行产生。手机比例排版代理只用于检查可读性，不是实际浏览器或平台预览证明。
