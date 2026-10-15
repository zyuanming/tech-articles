# 复算这次冲突

在文章目录下执行：

```text
python examples/run_conflict.py --output my-run
```

Python 标准库即可。输出目录必须尚不存在，程序不会覆写旧实验。作者实际运行：Python 3.12.14。

固定变量编号：1=p，2=z，3=x，4=u，5=v，6=w。`problem.cnf` 用 DIMACS 表示原来的四条子句；负整数表示否定，0 结束一条子句。程序内使用同样的规则，固定主动选择 p=1、z=1、x=1，并在每次选择后做单位传播。

输出 `results.json` 包含完整赋值轨迹、理由与前驱、两次归结、回跳层、撤销的赋值、回跳后被强迫的 x=0、24 个满足赋值以及 24 种子句扫描顺序的检查。`truth-table.csv` 列出全部 64 个完整赋值。`stdout.txt` 是简短运行结果。

公开存档分别为 [expected-results.json](expected-results.json)、[truth-table.csv](truth-table.csv)、[原始标准输出](../originals/experiment-stdout.txt)。没有随机数或外部 SAT 求解器。没有执行时间排名。

原始扫描顺序 C1、C2、C3、C4 产生 C3 冲突；逆向处理轨迹中当前层的最新赋值，先消去 v，再消去 u。学习子句为 (-1,-3)，即 ¬p∨¬x。回跳层为 1，保留 p=1，并通过新子句强制 x=0。

检查范围：64 个完整赋值在加子句前后满足性逐一相等，24 个解不变；被新子句排除的 16 个赋值均原本非法；两次归结分别检查 64 个赋值，共 128 次；四条原子句全部 24 种排列都得到同一学习子句和回跳层。另对一份完整满足赋值做实际检查。穷举是这个六变量模型的额外实现检查，不代替正文对归结规则的一般证明。

这是一个有断言的教学实验，不是接受任意输入的完整 CDCL 求解器：没有实现一般搜索循环、变量活动度、双监视文字、重启或学习子句数据库管理。不能把它用于证明任意输入无解。

## 重画图

```text
python examples/build_figures.py --output redraw
```

制图实际使用 Pillow 12.3.0 和 Noto Sans CJK 字体；字体路径在脚本中明示，可按本机安装调整。图 12 读取公开真值表，图 14 读取实际核验的完整解；其余为同一固定实验的原创推导示意。全部 14 张正文图与独立封面均可重画。`figure-metadata.json` 记录逐图职责、尺寸与最小字号。

原创代码按 [MIT](../LICENSE-CODE.txt) 许可；原创数据和图按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可。
