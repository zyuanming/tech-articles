# 来源、实验与素材许可

## 一手依据与事实边界

1. John McCarthy、Paul W. Abrahams、Daniel J. Edwards、Timothy P. Hart、Michael I. Levin，*LISP 1.5 Programmer's Manual*，MIT Press，1962；本次可访问扫描标注第二版、1985 年第十五次印刷，前言日期为 1962-08-17。[扫描入口](https://softwarepreservation.computerhistory.org/LISP/book/LISP%201.5%20Programmers%20Manual.pdf)。实际核读解析文字是标题/版权/前言与第一章 §1.1—1.6，另有下一章开头的一个返回窗口；不是全册 116 页。主要支持符号与配对、M/S 两种表示、五个基本操作、关联表、`eval`/`apply`、`lambda`、`label` 以及“教学定义不同于实际系统”的界限。前言将总体设计归于 McCarthy，手册写作归于 Levin，解释器实现归于 Russell 与 Edwards；不能把整个系统说成一人独作。页面所载美国政府用途复制条款并非一般公众再分发许可。
2. John McCarthy，*A Micro-Manual for Lisp — Not the Whole Truth*，*ACM SIGPLAN Notices* 13(8)，1978 年 8 月，215—216 页。[两页原作扫描入口](https://www.cse.sc.edu/~mgv/csce330f14/micromanualLISP.pdf)。已实际返回并核读两页全部解析文字，但 OCR 的代码字符有破损，原像素没有取得。它用于对照十条规则、常量、非 NIL 判真与递归；本文不复制其解释器长列表，也不把其中 `EQUAL`/`EQ` 混成相同语义。
3. Computer History Museum, Software Preservation Group，[LISP 1.5 family](https://softwarepreservation.computerhistory.org/LISP/lisp15_family.html)。本次正文只实际核读返回的开头至 Applications 一节部分（工具行 0—80），用于交叉定位手册作者、日期与系统贡献者。该站公开展示手册，不构成对本仓库转发整册或页面图片的授权。
4. John McCarthy，*Recursive Functions of Symbolic Expressions and Their Computation by Machine, Part I*，*Communications of the ACM* 3(4)，184—195，1960 年 4 月，DOI 10.1145/367177.367199。[出版者书目入口](https://cacm.acm.org/research/recursive-functions-of-symbolic-expressions-and-their-computation-by-machine-part-i/)。书目日期由出版者搜索结果及手册前言支持；本次正文页访问拒绝，未读原论文全文，不声称逐行复刻或核完原图。
5. McCarthy，*History of Lisp*，[作者站作品入口](https://jmc.stanford.edu/articles/lisp/lisp.pdf)。只获得搜索摘录与失败获取，未取得全文，不用它支撑轶事、对白、发明动机或具体实现细节。

原论文、History、手册和微型手册的直接原件获取均有访问拒绝，已停止重取；既有成功解析窗口保留为文字核对依据，不能充当原像素检查。详细的相关公式/结构采用或排除范围见[视觉库存](source-visual-inventory.md)。

## 本文模型的选择

新写 Python 实现参照 LISP 1.5 第一章 §1.6 的关联表教学架构：`eval` 处理表达式，`apply` 处理函数与参数值；`label` 把名字绑定到内部函数描述，随后调用该描述。1978 微型手册解释器的 LABEL 分支绑定整份 LABEL 描述，不能把两套环境轨迹混用。本文图中只建立一次 `first` 名字绑定，后续调用累积的是各层 `x` 绑定。

与该手册早期理论记号明确不同的教学约定：统一小写符号；空表与 `nil` 同一；`t/nil` 自求值；非 `nil` 均为真；以 `nil` 替代早期段落的 `F`。`eq` 严格限符号原子；`car/cdr` 仅接受配对；未定义情况用明确错误报告。解析器、参数个数检查、重复形参检查、步数上限、HTTP 页面和调用记录都是本文新增设施。程序没有闭包环境捕获，没有把它包装成现代 Scheme 或 Common Lisp。

表达式、Pair 结构、环境表、进入/返回事件和父调用编号由[实验生成器](examples/experiment.py)实际运行[解释器](examples/evaluator.py)产生，完整保存在[results.json](examples/results.json)。图的节点数、列表格子、参数绑定、递归边和返回值从这些数据读取；绘图脚本中的坐标、行距、字号是排版常量。接口概览图是规则示意，不标为某次调用轨迹。

实验环境为 Python 3.12.14。成功 16 例、预期错误 9 例、解析打印往返 5 例；覆盖空表、点对、符号相等、参数绑定、递归、动态遮蔽、未捕获环境和错误分支。求值从左到右；没有随机输入。无穷递归例在 100 次 eval/apply 进入预算处中断。界面默认限制为 500 次。有限样例不构成语言实现正确性的完整证明。

## 逐图用途与身份

下列 PNG 均为本文新制作，作者/署名为 zyuanming；教学图由 AI 辅助编写生成器制作。它们没有复制第三方扫描页、原公式排版、人物照片或历史机器界面。

| 图片 | 新增理解作用 | 身份 |
|---|---|---|
| 00-cover | 三个递归输入逐步缩小，建立问题 | 原创封面，输入来自模型 |
| 01-pairs | 两个真实 Pair 的左右格、cdr 边及 nil 终点 | 原创结构图 |
| 02-quote | 同一表达式被引用或执行的差别 | 原创路径示意，返回内容来自模型 |
| 03-operations | car/cdr/cons 四次计算；正常表与点对的差别 | 原创实际结果图 |
| 04-predicates | atom/eq、空表与 nil 的具体返回值 | 原创实际结果图 |
| 05-cond | 真分支执行与错误分支未执行；强制执行的错误 | 原创反例图 |
| 06-eval-apply | 表达式、值、函数体在两个接口间如何转交 | 原创规则示意 |
| 07-binding | 形参与实参值配对，形成关联表 | 原创事件图 |
| 08-call-frames | 同次调用各 eval 帧的输入与最终输出 | 原创事件图，按进入顺序排列 |
| 09-recursive-env | label 名字绑定和逐层 x 遮蔽 | 原创环境轨迹 |
| 10-recursion-tree | 从完整 parent 链提取递归调用边与返回 | 原创调用图 |
| 11-dynamic | 查找当前环境中第一个 x，解释缺失闭包捕获 | 原创查找图 |
| 12-errors | 明确模型拒绝的输入与预算边界 | 原创错误结果图 |
| 14-nested-pairs | 外层 car 进入内层表、两条 cdr 链各自终止 | 原创实际结构图 |
| 13-live-evaluator | 真正执行前述程序的页面与绑定结果 | 本文自制软件真实浏览器截图 |

全部图片宽 1062 像素；程序教学图关键字号至少 40 像素，真实软件截图正文 42 像素。缩至 354 像素宽时仍保留对应可读字号。截图是本地 HTTP 应用实际响应，使用安装的 Chromium 默认安全配置；界面身份是现代 Python 教学程序。它不属于历史原件，也不证明 1960 系统的实际性能。

## 许可与 AI 辅助

原创正文及原创 PNG：© 2026 zyuanming，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。转载需署名、链接来源与许可，并说明修改。

本篇 `examples/` 中 Python、HTML、JSON 代码与数据：采用 [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/)。`figurekit.py` 的基础 Canvas API 复用本仓库同批已公开 CC0 工具，图的构图、说明、输入与数据均为本篇新制作。生成的原创图像仍按上段 CC BY 4.0 发布。

第三方作品的文字、商标和扫描原件不纳入上述许可。本仓库仅提供来源链接与必要事实说明，未分发其页面或图片。

AI 辅助参与资料定位、中文起草、解释器与图示程序、测试及作者自检；所有声称运行的例子均实际运行，历史图像没有生成或伪造。作者自检不能替代非作者独立审读。
