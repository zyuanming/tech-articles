# Pratt表达式解析：可选运行材料

这些是本文原创教学程序与实际结果，不是CPython解析器源码。静态正文无需运行即可理解。代码MIT，本文自制图片和实际输出CC BY 4.0。

## 核心复算：只需Python标准库

实际运行版本Python 3.12.14。从本目录运行：

```sh
python parser_lab.py
```

脚本只在自己的目录中生成/更新`results.json`、两个`.dot`文件和`cpython-ast.txt`。不联网、不调用shell执行输入、不使用eval或exec。`ast.parse(..., mode='eval')`中的eval是解析模式名称，不是执行函数。

检查内容：14指定结构、随机种子314159的5000次随机表达式结构比较、10非法输入、7数值断言、一个乘方门槛变异、除零的解析/求值分离。比较对象是Python ast返回结构；并不意味着CPython使用Pratt。

`results.json`保留12个具体案例的词元位置、最终树、完全括号化写法、数值或求值错误、事件日志、表达式函数调用次数和最大嵌套深度。

主例2+3*4：5个普通词元、3次表达式调用、最大任务深度2（外层为0），结果14。EOF是额外哨兵，不计入消费的普通词元数。

## 支持的语法与限制

ASCII整数、ASCII字母/下划线开头的名字，+ - * / **，一元正负号，分组括号。空白忽略。禁止01这样的非零前导零数字，00仍表示0。无浮点文本、比较、赋值、隐式乘法、函数调用、属性、导入或语句。

规则是严格rbp < lbp继续：加减(10,10)，乘除(20,20)，乘方(30,29)，前缀正负号右门槛25，右括号/EOF左强度0。第一个数为左强度，第二个为读右边的门槛。不要混用另一种非严格比较的数字表。

文本最多3000字符，解析任务depth大于128时报ParseError。数值求值拒绝绝对值超过10^12、非有限值或复数；乘方指数绝对值限16。名字由调用者提供的字典取值（示例damage=3）。这些是教学边界，不是通用沙箱安全承诺；深的左结合树在后续递归求值/序列化时仍可能受Python调用栈限制。

默认不启用trace时核心建树的节点工作量为线性；trace=True会在事件里反复序列化子树，不能宣称含追踪/绘图的全过程也是O(n)。词法识别和大整数运算另计。

## 原始砖排PNG

可选Pillow用于画图，本文执行时版本12.3.0。已有这个依赖时运行：

```sh
python render_tiles.py
```

生成600×100的normal-tiles.png与grouped-tiles.png。每格宽26像素、起点间隔28像素；两图使用相同坐标规则。数量由Parser→evaluate实际返回的14和20决定，不是手写图注推定。若不运行，可直接打开已有文件。

## 真实Graphviz输出

本文使用已安装的Graphviz 2.42.4，生成命令：

```sh
dot -Tpng -Gdpi=160 normal-ast.dot -o normal-graphviz.png
dot -Tsvg normal-ast.dot -o normal-graphviz.svg
dot -Tpng -Gdpi=160 grouped-ast.dot -o grouped-graphviz.png
dot -Tsvg grouped-ast.dot -o grouped-graphviz.svg
```

.dot是本文程序根据实际树写出的节点和边，PNG/SVG是工具实际输出；它们不含Graphviz软件源码，不转载书图或论文图。布局可能随Graphviz/字体版本改变，比较树关系时不要要求跨版本像素完全相同。

## 三个可选问题

```python
from parser_lab import Parser, compact, evaluate
print(compact(Parser('2**3**2').parse()))
print(compact(Parser('2**3**2', power_right=30).parse()))
for s in ['-2**2','(-2)**2','2**-3']:
    t=Parser(s).parse()
    print(s,compact(t),evaluate(t))
```

第一行结构`(2**(3**2))`，第二行`((2**3)**2)`；后三个值分别−4、4、0.125。
