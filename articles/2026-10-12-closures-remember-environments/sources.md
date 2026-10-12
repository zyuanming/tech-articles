# 来源、图像与实验说明

原创中文正文由zyuanming发布，采用CC BY 4.0。本文使用AI辅助研究、写作、编程绘图和校验。22幅原创图是程序语义与关系示意，不是真实地址、调试器、编译器或游戏引擎截图。另有1张Peter Landin肖像；其具体来源声明独立列出，不能把整库正文许可套到第三方照片或论文上。

## 一手来源及实际阅读范围

1. P. J. Landin，*The Mechanical Evaluation of Expressions*，The Computer Journal 6(4)，308—320，1964年1月。[出版者书目](https://academic.oup.com/comjnl/article-abstract/6/4/308/375725)；[Tufts课程档案原论文](https://www.cs.tufts.edu/comp/150FP/archive/peter-landin/mechanical-eval.pdf)。已实际下载13页原件，读取316—319页的环境、closure、SECD状态、实现与共享讨论，并查看316—317页原排版。本文历史段只转述这部分定义及四个角色，没有声称逐行研究全文，也没有将SECD说成实体计算机。正文的分数、按钮与计数器是新造例子，不是Landin原文例子的翻译。
2. Python3.12[执行模型§4.2](https://docs.python.org/3.12/reference/executionmodel.html)，支持名字绑定、嵌套函数作用域、运行时取值及UnboundLocalError边界；[简单语句中的nonlocal](https://docs.python.org/3.12/reference/simple_stmts.html#the-nonlocal-statement)，支持重新绑定最近外层函数中已存在的名字。本文只讨论给出的函数/循环代码，没有把普通类属性、注解作用域、exec/eval的规则简单混入同一口诀。
3. Python3.12[数据模型，用户定义函数](https://docs.python.org/3.12/reference/datamodel.html#user-defined-functions)，实际读取`__closure__`、cell_contents、`__code__`、`__defaults__`和`__globals__`条目；[函数定义](https://docs.python.org/3.12/reference/compound_stmts.html#function-definitions)，核默认参数在执行定义时求值及可变默认对象的行为。网页小版本可能随维护变化，本文实际运行环境单独固定为CPython3.12.14，不把文档标头的小版本当作运行版本。
4. Python官方[编程FAQ：循环中定义的函数](https://docs.python.org/3.12/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result)，用于核对延后读取及默认参数办法。本文用外层函数内部的def和三个字符串按钮，未照搬官方平方列表例子。此结果限定Python相应绑定规则，不泛化为其他语言所有for循环。
5. Jeremy Hylton，[PEP227：Statically Nested Scopes](https://peps.python.org/pep-0227/)，实际读介绍、规范及实现讨论，尤其flat closures、cell/free变量、避免保留无关对象的设计考虑。这是Python2时代的历史设计文档，其中当时不能直接重绑定外层名字的限制不代表Python3当前行为；现代nonlocal以当前参考手册及[PEP3104](https://peps.python.org/pep-3104/)核对。正文没有把旧PEP中的语法限制照搬到现在。
6. Luca Cardelli，*Compiling a Functional Language*，1984。[作者论文目录](https://www.lucacardelli.name/indexPapers.html)；[作者提供PDF](https://www.lucacardelli.name/Papers/CompilingML.A4.pdf)。实际读该PDF第4页§4的函数对象、自由变量、环境、调用与副作用共享，第1—2页仅核背景；作者文件页脚有1995年排版时间，不当作论文首发年。本文显式代码—环境对的教学模型借此核机制，不宣称是CPython生成代码，也不复制该ML实现的指针布局或性能结论。

## 核心资料的图像范围

Landin本文所用316—317页以形式定义和状态转换式说明机制，没有一张需要按原数据复现的性能曲线；本文07把四个角色独立画成中文关系示意，不是论文截图。其余页的符号结构、递归与表示技术不属于本文要完整教授的主题。论文扫描没有查到开放图版再分发许可，因此完整原件仅以原站链接提供，不将页面裁图公开。

Cardelli相关§4也是文字与机制说明；本文19—21是自设数据表示和共享图，不把历史ML布局换个名字当Python实现。其余章节的类型推导、模式匹配、数据布局及机器指令不是本篇主题。原文件保留出版版权，没有重新打包其页面。Python所用官方章节没有与本文例子对应的原始正文信息图，本文22幅教学图均为新作。

## Peter Landin肖像

- 本地文件：`assets/landin-public-portrait.jpg`，603×700，357225字节，保留下载字节，不裁切、不调色、不AI放大。
- [作品说明页](https://www.eurekalert.org/multimedia/966309)标题为*Peter Landin Passport picture*，发布机构Queen Mary University of London，Credit为Daniel Landin。本文据此写“图片署名”，未额外推断摄影者或拍摄年份。图片只是肖像，不含护照号码等证件资料。
- 作品页明确列Usage Restrictions为“No restrictions.”，License为“Public Domain”。此处依据这件作品的机构发布声明复用，不依据“网上能看到”、人物已故或猜测版权年限。保留作品标题、机构、署名与原站方便核验；不将声明扩展到同页所有其他图片。
- 下载来自原作品页实际给出的[公开图像文件](https://mediasvc.eurekalert.org/Api/v1/Multimedia/618255fb-4c3f-43d4-a3af-602775c8b8f2/Rendition/low-res/Content/Public)。该接口名称包含low-res，故准确称“原站公开提供版本”，不声称已经取得档案最高分辨率原件；当前603×700对手机正文肖像展示足够。它不是作者制作的QA代理。
- 已尝试原机构新闻页，访问返回403，未绕过。作品说明可读取，独立公开图像链接正常下载成功；未改请求身份或猜测受限高清地址。同一资料库其他旅途、家庭或不明会议照片不承担本文闭包教学任务，未作为填数素材收入。

## 22幅原创图的职责

01不同计分器；02创建/返回/调用三个时刻；03参数与外部名字；04共用代码和不同环境；05调用结束与信息寿命；06词法定义关系；07SECD角色；08函数/cell/对象；09实际属性对照；10同组共享；11两组交错调用账本；12别名与新工厂；13nonlocal目标；14循环创建时间线；15循环后调用；16三次工厂；17默认参数；18引用与深复制区别；19代码—环境对；20显式调用参数；21保留共享关系；22三个诊断问题。

图中的箭头表示本文标明的“指向、关联或查找”，不是语言规定的物理地址方向。图14三栏是同一绑定在不同时间的状态，不是三个独立绑定；图16才是三次工厂调用。代码对象共享是本次CPython运行的实际观察，不是所有实现都必须满足的物理表示要求。

## 实际实验

[closure_lab.py](examples/closure_lab.py)仅用Python标准库，实际环境为CPython3.12.14。

- make_score(10)与make_score(100)输入7分别得17、107；调用者有局部bonus=1000不改变前者结果。
- 实际检查自由变量名为bonus；两函数代码对象相同，bonus cell不同，cell内容10和100。
- A从0、B从100开始，依次A加/A加/B加/A读/B读返回1、2、101、2、101。同一工厂的add/read共享cell，不同工厂不共享；别名继续把A变到3。
- 循环后调用返回C/C/C，默认参数办法及三次工厂均为A/B/C。默认参数版本例的`__closure__`是None，默认字符串在`__defaults__`。列表默认值实验分别检查追加同一列表与改绑外部名字，不把保留引用说成深复制。
- bonus从−20到20、points从−30到30，2501组输入与显式代码—环境对结果一致。固定种子1964，对五个计数器的10000次交错操作，与另一份整数记录逐项比较通过。
- 这些是有限例子与实现检查，不是语言实现形式证明，也没有游戏帧率、内存占用或运行速度测试。本文不会从某个闭包存在就推断整个外层栈帧必须永久保留。
