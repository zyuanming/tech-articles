# 来源、图像与执行记录

核对日期2026-10-11。原创中文正文由zyuanming以CC BY 4.0发布；图片与代码不因正文声明自动获得相同授权；未使用第三方肖像或第三方图文件。

## 一手依据

1. Jeffrey S. Vitter, Random Sampling with a Reservoir, ACM TOMS 11(1), 1985, 37–57。作者大学网站原文：https://www.ittc.ku.edu/~jsv/Papers/Vit85.Reservoir.pdf ，DOI https://doi.org/10.1145/3147.3165 。第2节p.39将Algorithm R归于Alan Waterman；本文不把它归为Vitter发明。论文重点包括Algorithm Z、跳过记录、CPU与I/O成本范围。
2. NIST Dictionary of Algorithms and Data Structures, reservoir sampling：https://xlinux.nist.gov/dads/HTML/reservoirSampling.html 。提供Algorithm R内存变体定义、等概率子集、Knuth归功于Alan G. Waterman、X/Y/Z通过跳跃减少随机数。
3. Python随机数接口只使用标准库的randrange(i)与Random(seed)，实验已运行。未将Mersenne Twister的可复现性等同于密码学安全。

## 目标来源视觉核对

目标简明算法说明为NIST条目，正文没有图片，零图不需收取。为历史及算法归属读取Vitter论文：原文包含Table I（算法CPU/随机数复杂度比较）、Table II（VAX 11/780的历史实测秒数），未见标为Figure的图片。两表不是本文新实验，且论文明确再出版须相应许可；不复制论文截图和表格，避免把未取得的再发布权利当作CC。本文不声称复现论文性能。该排除不妨碍用原创图讲解自己的概率例子。

Vitter、Waterman仅出现在必要归属段，不是人物视觉传记；没有身份和复用权利均核实的肖像，未采用肖像，未以合成人像替代。本文主线为概率不变量及同一五记录实例。

## 图像逐项映射（均原创）

01-stream.png：五次到达与两格容量。02-biased-coin.png：固定1/2替换的四条最终概率1/8、1/8、1/4、1/2。03-one-slot.png：1/i曲线。04-fill.png：A、B填满。05-third-tickets.png：三签两替换。06-third-outcomes.png：AB/AC/BC。07-fourth-tickets.png：四签。08-fifth-tickets.png：五签。09-trace.png：预先指定抽签2、4、1的可能轨迹。10-survival.png：2/4×4/5=2/5。11-subsets.png：五选二十组合。12-exact-subsets.png：fractions.Fraction精确枚举分支，十组全为1/10。13-monte-carlo.png：100000次、每次十选三、Random(2026)，计数为[29801,30003,29968,30041,29861,30033,30062,30022,29987,30222]。14-storage.png：保留min(N,2)条。15-duplicates.png：两个红记录和一个蓝记录。16-window.png：全历史与最近三条。17-skipping.png：N−2次抽签对比sum(2/i,i=3..N)期望替换，纵轴对数，无CPU耗时主张。

全部图为1152×832 PNG；原始生成文件，不用缩略图代替。本文不设置“实测证明所有输入正确”的结论：精确枚举检验N=5,k=2；蒙特卡洛检验有限实验；一般正确性来自归纳/组合推理。

本文使用AI辅助调研与写作；原创教学图按明确设定由代码生成，合成演示与真实来源图已区分。
