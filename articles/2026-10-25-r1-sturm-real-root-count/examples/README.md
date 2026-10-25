# Sturm 精确有理数教学实现

代码和自产数值 JSON：CC0。原创图和本地报告截图：CC BY 4.0。第三方依赖保留各自许可，本文没有打包它们。

运行环境核验：Python 3.12.14、SymPy 1.14.0。核心 `sturm_exact.py` 只需 Python 标准库；实验核验脚本还需 SymPy；绘图需 Pillow、fontTools，并安装 Noto CJK 与 DejaVu Sans 字体；浏览器截图需 Playwright 和系统 Chromium。

在本目录执行：

```bash
PYTHONDONTWRITEBYTECODE=1 python run_examples.py
PYTHONDONTWRITEBYTECODE=1 python build_figures.py
```

前者写出 `results.json`，包含精确分数字符串、实际隔离树、独立核验结果及浮点绘图采样。后者从这个文件生成15张新图和元数据。浮点采样只用于画曲线，不参与根计数。版式坐标、颜色、通用数学表达式不属于实验数值。

要查看实际结果报告，另开一个终端：

```bash
python -m http.server 8133 --bind 127.0.0.1
```

在浏览器打开 `http://127.0.0.1:8133/report.html`。这是只读JSON报告，不提供任意输入或调用Python的后端。可用以下命令重拍桌面正文图和手机检查图。从本examples目录运行时，示例相对路径会把审计文件放在仓库外的sturm-audit目录；也可换成其他文章目录之外的临时位置：

```bash
python capture_report.py --audit-dir ../../../../sturm-audit
```

`build_figures.py` 会重新生成15张程序图的元数据；截图文件的尺寸与检查记录由 `capture_report.py` 补入同一份元数据，因此应按先画图、后截图的顺序复现完整16图清单。系统 Chromium 路径为 `/usr/bin/chromium`，没有附加禁用安全机制的启动参数。

## 输入与接口约定

系数从低次到高次，`[0,-1,0,1]` 表示x³−x。接受整数、Fraction、有理数字符串；拒绝float。空系数或全零系数为零多项式，拒绝有限根计数。非零常数返回0。区间要求a<b，相等或反向均报错。

`count(p,a,b,ends='(]')` 返回不同实根数，自动平方自由化。四个合法的ends为`(]`、`[]`、`()`、`[)`。没有权重或重数总和模式。

`isolate(p,a,b,max_width=Fraction(1,4),max_nodes=10000)` 返回`(intervals,nodes)`，覆盖且只覆盖(a,b]内的根。输出区间左开右闭，每个恰有一个不同实根，宽度不超过max_width。达到资源上限抛出异常，不给出“完成”的假象。函数没有自动选择全实轴根界。

有理数长除法保留原始负余数。gcd可取首一表示，但不能把建成的各链项无条件变成首一，因为负倍缩放会破坏符号变化。

## 核验范围

独立因式基准使用种子2026102513的局部随机数生成器：80次，每次从−3到3、间隔1/2的有理根池随机取1至5个不同根，各重复1至3次，前乘−3、−1、1或2；每例抽10对端点并核四种开闭规则，总计3,200次。`run_examples.py`公开完整消费顺序，不能只用种子另造一组数据冒充同批结果。

SymPy独立对照6组输入的闭区间计数与完整链；另核x²−2隔离端点平方、零/常数/相等与反向端点/浮点拒绝、二分子节点根数可加性。数值有限核验不是一般正确性证明。
