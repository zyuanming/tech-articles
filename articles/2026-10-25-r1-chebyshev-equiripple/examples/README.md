# Chebyshev 等波纹的可复算例子

所有输入无量纲，主例为 f(x)=x⁴、x∈[-1,1]、次数预算≤3；无随机数。代码与输出数据 CC0；生成图片及报告截图 CC BY 4.0。

依赖：Python 3.12、NumPy、SymPy、Pillow、fontTools；截图另需 Playwright 和系统 Chromium。中文字体候选为 Noto Sans CJK，缺失时报错，不静默退回。此次版本见 results.json。

在本目录执行：

```sh
PYTHONDONTWRITEBYTECODE=1 python run_examples.py
PYTHONDONTWRITEBYTECODE=1 python build_figures.py
```

run_examples.py 执行：

- 独立递推 T₀…T₁₂，与 SymPy Chebyshev 实现逐项精确比较。
- 确认误差恒等式、五个精确交错峰、完整导数因式分解。
- 求连续均匀权重下最小二乘的正规方程，精确积分误差平方，遍历端点与符号求得的所有驻点比较最大绝对误差。
- 对 x⁴ 固定执行三轮教学交换：解五元线性方程，求残差导数的全部三次方程根，筛选区间内实根并连同端点排序。此例有五个交错极值，将它们全部替换为新参考点。一般函数不保证这种结构；断言失败即停止。本实现不是通用Remez求解器，没有全局收敛或通用停止保证。
- 计算稀疏网格漏峰、区间外输入、Chebyshev截断反例、最后的常数扰动练习及区间映射。

曲线801点（区间外601点）只是绘图采样。全区间最优性的证书是正文的平方恒等式与交错根数证明；浮点寻峰不是严格区间算术。

build_figures.py 读取 results.json 才能绘图。几何检查、字形存在、墨迹、字号、对比、元数据尺寸核对在保存前执行。figure_canvas.py 的通用检查API沿用库内CC0 helper，所有本篇构图和数据为新制。先运行 build_figures 再截图，因为前者会重建元数据。

真实报告截图：仍从本篇的 `examples` 目录运行。下面的相对审计目录位于仓库外，可换成其他公开仓库外的位置：

```sh
PYTHONDONTWRITEBYTECODE=1 python capture_report.py \
  --audit-dir ../../../../chebyshev-audit
```

它临时在127.0.0.1:8155提供本目录只读网页，用默认系统Chromium分别以1062与354像素浏览；关闭服务后退出。没有禁用浏览器安全选项。正式截图为 assets/14-live-report.png，浏览器几何记录与移动截图写入指定审计目录。报告不是任何第三方数学软件的界面。
