# 来源、数字与没做的事

《一亿次加法之后，和少了多少》。本文的所有数字都由 `examples/run_model.py` 算出，写进 `examples/results.json`（6968 字节），图由 `examples/build_figures.py` 读同一个文件画出。两份脚本都只用标准库（画图另需 Pillow），重跑得到逐字节相同的输出。

## 图

10 张（`assets/01..09` 与 `cover.png`）全部原创绘制，身份是**教学示意**：不是任何数值库或硬件的截图，也不是某个真实程序的内存布局。画法在 `examples/figkit.py`，每个标签的字号、是否越界、是否互相重叠、与背景的对比度、下方留白，都在 `save()` 里当场断言，几何不成立就抛异常。

逐张说明（编号按正文出现顺序）：

- `01-swallow.png`：一条数轴，刻度是 2^53 附近真实存在的双精度数，每隔 2 一个。红色实心点是起点，红色虚线指向「加 1 会落在的位置」——两个刻度正中间，那里没有对应的数。
- `02-trace.png`：3 项 × 5 列的账本。左五列是 Kahan 每一步的 x、y = x − c、t = s + y、c、s；最后一列是 Neumaier 在同一串数上算出的 c。红色是 Kahan 的 c（第二行起全为 0），青色是 Neumaier 的 c（第二行起为 1）。
- `03-harmonic.png`：横轴项数（1000 到 1000000，对数），纵轴绝对误差（对数，四格分别是 0、1e−15、1e−13、1e−11）。红线是直接相加，琥珀线是两两相加，空心的青圈与蓝圈是 Kahan 与 Neumaier——它们的误差是 0，对数轴画不出 0，所以画在最下面那一行。
- `04-order.png`：四根柱子，同一批数的四种加法顺序下直接相加的绝对误差，柱顶标数值。
- `05-cancel.png`：三根柱子，20000 组抵消测试里给出精确结果的比例（86.2% / 92.1% / 99.9%）。纵轴上限留到 120%，好让柱顶的数字有地方放。
- `06-cost.png`：四根柱子，每个数在内循环里的四则运算次数（1 / 1 / 4 / 5）。
- `07-variance.png`：表，三种方差算法在 n = 1000 与 n = 100000 上的误差，红色是误差失控的一次扫。
- `08-decide.png`：六种情形与对应做法的对照表。
- `09-takeaways.png`：三条结论。
- `cover.png`：1080 × 1080，标题加三行数字。

图里的每个数字都来自 `results.json`，画图脚本不另算公式。

## 数字

`run_model.py` 里八个实验，各自的输入与结果：

1. `swallow`：`float(2**53) + 1.0 == float(2**53)` 为真；从 2^53 起连续加十次 1.0，十次全都不变（`ladder_stuck`）；加 2.0 才前进一步，`plus_two_moves_by` = 2.0；`ulp_at_base` = 2.0。
2. `traces`：序列 `[1, 1e16, −1e16]`。精确和 `math.fsum` = 1.0，直接相加 0.0，Kahan 0.0，Neumaier 1.0。逐步中间量原样写进 `results.json`，正文图 2 就是这张表。Kahan 第二行 `c` = 0 的原因：`t − s = 1e16 − 1` 在 1e16 处（ulp = 2）只能给 1e16。
3. `harmonic`：n = 1000 / 10000 / 100000 / 1000000，直接相加的绝对误差 1.776e−15 / 3.375e−14 / 9.237e−14 / 7.354e−13；Kahan 与 Neumaier 四组全为 0；两两相加 1.776e−15 / 0 / 3.553e−15 / 1.776e−15。
4. `order`：同一批一百万个倒数和，四种顺序下直接相加 7.354e−13（原顺序）/ 4.796e−14（倒过来）/ 7.194e−13（洗牌）/ 4.796e−14（排序），Kahan 四组全为 0。
5. `cancel`：20000 组，长度 3..12，符号随机、量级 1e−30..1e30。与精确值逐位相同：直接相加 17249 组（86.245%），Kahan 18420 组（92.1%），Neumaier 19987 组（99.935%，即 13 组不精确）。Kahan 比直接相加还差的有 263 组（1.315%）。`worst` 记录了比值最大的那一组（直接相加恰好精确，Kahan 不精确），正文抄了这七个数。
6. `representation`：从 1e16 起加 1e−8 共一百万次，精确和 1e16 + 0.01；`math.fsum`、直接相加、Kahan、Neumaier 返回的都是 1e16，因为该量级 ulp = 2，`representable` 为假。
7. `ops`：静态计数。直接相加每项 1 次加法；Kahan 1 加 3 减；Neumaier 2 加 2 减 1 次比较；两两相加共 n − 1 次加法，摊到每项约 1 次。**不是耗时**——本文没有任何计时。
8. `variance`：均值 1e8、标准差 1 的数据。n = 1000 时真值 1.027366，一次扫得 10.0（误差 8.97），两遍误差 0，Welford 误差 2.6e−9；n = 100000 时真值 0.999924，一次扫得 434（误差 433），两遍 0，Welford 6.2e−9。

`selfcheck` 是十三条断言的与，当前全真：2^53 加 1 被吞掉、连续加十次不动、加 2 才前进、`[1, 1e16, −1e16]` 的精确和是 1、Kahan 在这串上是 0、Neumaier 是 1、百万项上 Kahan 误差小于直接相加、换个顺序直接相加的结果就变、Neumaier 在抵消测试里精确次数最多、Kahan 确实有更差的情况、和存不下时四种方法给同一个数、Welford 误差小于一次扫、Kahan 每项四次运算。

可以手算复核的八处：

1. 2^53 = 9007199254740992，53 位有效位意味着此处 ulp = 2^53 × 2^−52 = 2；加 1 正好半个 ulp，按取偶停在原处。
2. Kahan 在那 3 项上的第二行：s = 1、y = 1e16，`t = 1 + 1e16` 舍入到 1e16；`t − s = 1e16 − 1` 也舍入到 1e16（差了 1，而该量级 ulp 是 2）；于是 c = 0。
3. Neumaier 同一行：|1| < |1e16|，走 `c += (x − t) + s` = (1e16 − 1e16) + 1 = 1。
4. n = 1000 的直接相加误差 1.776e−15 = 2 个 ulp（7.4854 处 ulp = 8.88e−16）。n = 1000000 的 7.354e−13 约 413 个 ulp（14.3927 处 ulp = 1.78e−15）。
5. 三种方法的精确率：17249/20000 = 86.245%，18420/20000 = 92.1%，19987/20000 = 99.935%，263/20000 = 1.315%。
6. 一次扫算方差时，Σx² ≈ 1e19，此处 ulp = 2048；除以 n = 1000 之后，每一次舍入的贡献就是约 2。实测误差 8.97 ≈ 4 个 ulp，量级对得上。
7. 1e16 + 0.01：0.01 < ulp/2 = 1，舍入后仍是 1e16。`math.fsum` 做的是「精确求和再舍入一次」，结果也是 1e16。
8. 调和级数 n = 1e6 的精确值 14.392726722865724 由 `math.fsum` 给出，四种顺序里的 Kahan 都返回这个数。

## 文献

- Kahan, W. *Pracniques: further remarks on reducing truncation errors*. Communications of the ACM 8(1), 1965, 40. DOI `10.1145/363707.363723`（Crossref：卷 8、期 1、页 40、1965 年 1 月；作者 Kahan）。正文里那四行就是这篇的算法。
- Neumaier, A. *Rundungsfehleranalyse einiger Verfahren zur Summation endlicher Summen*. ZAMM 54(1), 1974, 39–51. DOI `10.1002/zamm.19740540106`（Crossref：卷 54、期 1、页 39–51、1974 年 1 月）。正文的分支修正与「最后返回 s + c」出自这篇。
- Dekker, T. J. *A floating-point technique for extending the available precision*. Numerische Mathematik 18, 1971, 224–242. DOI `10.1007/BF01397083`。正文提到的 Fast2Sum（`t − s` 在 |s| ≥ |y| 时精确）属于这一路的技巧。
- Welford, B. P. *Note on a Method for Calculating Corrected Sums of Squares and Products*. Technometrics 4(3), 1962, 419–420. DOI `10.1080/00401706.1962.10490022`。图 07 里那个单遍方差递推。
- Shewchuk, J. R. *Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates*. Discrete & Computational Geometry 18(3), 1997, 305–363. DOI `10.1007/PL00009321`。`math.fsum` 用的无损变换出自这篇；正文只把它当「逐位精确」的参照，没有展开算法。
- Higham, N. J. *Accuracy and Stability of Numerical Algorithms*, 2nd ed., SIAM, 2002. 求和的误差界与补偿求和的正式分析在这本书里；正文提到它时没有引用具体页码，也没有据此推公式。

## 没有做的事

- **没有测耗时。** `ops` 是静态计数，不是基准。本机上 Python 循环开销远大于一次浮点加法，量出来的比值说明不了 C、GPU 或某数值库的情况。
- **没有实测编译器优化。** 正文提到 `-ffast-math` / `--use_fast_math` 可能让补偿失效，这是已知的、有文档记载的行为，本文没有编译任何程序验证。
- **没有实现 Shewchuk 的无损变换**，只是调用 `math.fsum` 当参照值。
- **没有做并行归约或 GPU 上的补偿求和实验**，正文只说「c 要跟着一起传」，没有实测。
- **没有给出误差界的推导**，所有误差都是实测值，没有和理论界做比较。
- **没有覆盖 long double、Kahan–Babučka、Double-double 双倍精度求和**，也没有触及浮点异常（上溢、NaN 传播）。
- 只用了 CPython 的 float64；没有测 NumPy、Julia、C 或任何 SIMD 实现。

## AI 辅助

实验设计、代码、图、正文由 AI 编写，用户给出选题方向与交付规范。所有数字都能用 `examples/kahan.py` 里的函数手算复现；文献条目逐条过了 Crossref 的卷期页码，`math.fsum` 的行为由 CPython 文档与 Shewchuk 1997 支撑。审读由同一个 AI 在同一轮内完成，独立性有限。
