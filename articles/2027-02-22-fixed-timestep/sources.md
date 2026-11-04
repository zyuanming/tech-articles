# 来源与说明

## 图片

13 张正文图与 `cover.png` 全部是本文原创的教学示意，由 `examples/build_figures.py` 生成。几何断言写在 `examples/figkit.py` 里：文字不出画布、不互相压、任何字号的文字换算到 354 px 宽的显示宽度后不小于 12 px。没有使用照片、截图或第三方素材，因此不涉及第三方署名与许可。

这意味着图里没有一张是真实引擎的截图或内部状态快照。所有曲线都是 `examples/results.json` 里那批数画出来的，`build_figures.py` 只负责取值和摆放。

## 数字

正文和图片里的每个数字都由 `examples/timestep.py` 算出、`examples/run_model.py` 写进 `examples/results.json`，`examples/build_figures.py` 只从 `results.json` 取值。跑一遍：

```sh
cd examples && python3 run_model.py && python3 build_figures.py
```

纯标准库（画图需要 Pillow），`run_model.py` 约 0.3 秒，`build_figures.py` 约 3.4 秒。

模型设定：

- **跳跃**：v0 = 8 m/s、g = 30 m/s²、y 从 0 起，没有空气阻力，没有碰撞。g = 30 是取的手感值（地球是 9.8），因为 2D 平台游戏里常用两倍到三倍重力换更利落的跳跃弧线；换成 9.8 全部数字按比例变，结论不变。
- **两种顺序**：`v_first` 是 `v -= g·dt; y += v·dt`（半隐式/辛欧拉），`y_first` 是 `y += v·dt; v -= g·dt`（显式欧拉）。正文里「先加速度」「先动位置」指的就是这两种。
- **插值**：`x += (target−x)·k`，k = 0.1，每帧调一次。连续时间等价按 `k = 1−exp(−λ·dt)` 反解 λ。
- **弹簧**：x″ = −ω²x，ω = 2π（1 Hz），x(0) = 1、v(0) = 0，E = ½v² + ½ω²x²。10 秒、60 fps（600 步）、30 fps（300 步）各跑一遍。三种方法：显式欧拉、半隐式欧拉、RK4（经典四阶，不带自适应步长）。
- **累加器**：120 帧，帧时间在 10–28 ms 之间均匀随机，由 SplitMix64 生成，种子固定；dt = 1/60。卡顿实验把第 40 帧的帧时间改成 500 ms；闸门版把每帧时间截到 250 ms。
- **死亡螺旋**：每帧基础开销 20 ms，每步物理开销 c ms，每帧步数由累加器决定、步数又决定下一帧的耗时，跑到 120 帧或超过 5000 ms 为止。稳态值取最后几帧；发散标记为「仿真时间落后墙面时间超过 10 秒」。
- **穿透**：墙厚 0.1，dt = 1/60，物体速度恒定，墙心在五个步长范围内均匀随机（SplitMix64），每种速度 200 次试验。「穿透」= 这一步开始前在墙左、结束后在墙右，且中间没有采样点落在墙内。
- **浮点**：float32 用 `struct.pack('f', …)` 往返实现，没有用 numpy。一小时 = 216000 次累加 1/60。
- **双摆**：标准双摆方程（两个等长无质量杆、两个质点、无阻尼），RK4、dt = 1e-3、20 秒。初值 (θ₁, θ₂) = (2.1, 2.1)，扰动版把 θ₁ 加 1e-9。

关键数字的来历：

- **1.000 / 1.1333 / 1.0667**：60 fps 下两种顺序的离散最高点与连续解。手算过程在正文里。
- **−15.04% / −12.50% / −6.25% / −3.13% / −2.59% / −1.56% / −0.37%**：24 / 30 / 60 / 120 / 144 / 240 / 1000 fps 时 `v_first` 的相对偏差。
- **140 / 2.3333 / 2.3484 / 15.1 ms / 7·86·27**：120 帧抖动序列的步数、仿真时间、墙面时间、累加器余量、每帧步数的直方图。
- **30 / 15 / 250**：500 ms 卡顿那一帧在不设闸门、设 250 ms 闸门时补的步数，以及被丢掉的毫秒数。
- **48.5 / 183.5 / 482.5 / 5364**：c = 10 / 15 / 16 / 18 ms 时的稳态或末期帧时间。公式预期 50 / 200 / 500 / ∞——实测略低一点，因为递推里的步数按累加器离散地跳，而不是连续地跟。
- **0.385 / 0.675 / 0.840 / 0.925 / 0.985**：10 / 20 / 40 / 80 / 160 m/s 的实测穿透率；2 m/s 与 5 m/s 分别是 0 和 0.01。
- **2 / 4 / 7 / 14 / 27**：10 / 20 / 40 / 80 / 160 m/s 需要的子步数（规则是每子步位移 ≤ 墙厚）。
- **695 倍 / 5.5% / −1.1×10⁻⁵**：三种积分器在 600 步之后的能量偏差。695 是放大倍数，不是「多了 695 倍」的意思——原能量乘以 695。
- **1.3e−15 / −3.5e−7 / −2.79**：float64 60 帧、float32 60 帧、float32 一小时（216000 帧）的累加误差，单位秒。
- **1e−9 → 1.3**：双摆 20 秒内两个解的距离从 1e−9 涨到 1.3 弧度。

## 明确没有做的事

- **没有跑任何真实引擎。** 全文没有 Unity / Unreal / Godot / Box2D 的实测，也没有 benchmark、没有 FPS 统计、没有 profiler。所有「引擎会怎样」的说法都来自下面列的文档，不是我的机器上跑出来的。
- **没有测真实的帧时间序列。** 10–28 ms 的抖动是我写在模型里的均匀分布，不是我录的一段真实 vsync 序列。真实分布长尾得多（有 100 ms 的 GC 停顿、有 33 ms 的掉帧），累加器的 hist 图在真实机器上会更歪。
- **没有测 GPU、驱动和 vsync。** 正文里「画面时间」只是一个标量帧时间；真实的呈现时间、合成器延迟、帧队列深度都没有建模。
- **没有读 Unity 的文档。** 我原本想引 Unity 的 `Time.maximumDeltaTime`（0.333 s 那个默认值），但那几张文档页是客户端渲染的，静态 HTML 里读不到内容，所以正文没有引 Unity 的任何具体默认值。保留的引擎事实只有 Godot 4 的 `physics/common/max_physics_steps_per_frame = 8` 与 `physics/common/physics_ticks_per_second = 60`，以及它文档里「physics spiral of death」那段原文。
- **没有验证 Fiedler 文章的修订经历。** 正文引的是 2004 年 6 月 10 日那一版（页面标注的发布日期），代码片段与引文都按页面上的现行文本抄。这篇文章二十来年里有过排版修订，我没有比对历史版本。
- **没有核对 Box2D 的实现。** TOI 与 speculative collision 的机制按 Box2D 3.x 文档页的描述写，没有读 `b2_solver.c` 之类源码，也没有实验它的 TOI 在本模型那种极端速度下是否会退化。
- **没有测编译器与 CPU 的浮点差异。** 正文说换编译器可能把 `a*b+c` 合成 FMA、换 CPU 可能用 x87 的 80 位中间结果——这是浮点环境的通识，不是我在两台机器上量出来的。第 12 张图只演示了「相同代码 + 差 1e-9 的初值」会怎样，没有演示同一份代码在不同机器上分叉。
- **没有给李雅普诺夫指数做正经估计。** 正文那个「约 1.0 / 秒」是我从 0–20 秒平均增长率（ln(1.3/1e-9)/20 = 1.05）和 10–20 秒段（1.16）顺手算的，不是用两条邻近轨道回归出来的指数，也没做收敛性检查。
- **文献条目没有逐条核对页码。** Hairer / Lubich / Wanner 那本只用来支撑「辛方法长期不漂能量」这个背景结论，Strang 那本只用于 RK4 的基础讲法；两本我都没有在写这一篇时翻到具体页码，正文也没有引用它们的公式编号。
- **没有目视检查图片。** 见 `review.md`。

## 模型与真实实现的差别

四处值得记住：

1. **真实的时间来源是单调时钟加浮点减法。** 我用的是直接给定的帧时间。真实代码里 `frameTime = now − last`，`now` 是 `clock_gettime(CLOCK_MONOTONIC)` 或者 `QueryPerformanceCounter`，几十小时之后这两个 double 相减会开始丢有效位。正文第 9 节那一小时的漂移只算了累加器的部分，没算这一步。
2. **真实引擎的物理步长不是恒定的。** 大多数引擎会在「固定步长」上再叠一层「如果这一帧的步数超过上限就缩放 dt」的妥协（Godot 的 `physics_jitter_fix`、Unity 的 `Time.timeScale` 与 `maximumDeltaTime` 都会动到实际步长），所以「固定 dt」在工程里往往只是「通常固定」。
3. **一次物理步的开销不是常数。** 我的模型里每步都是 c 毫秒；真实的每步开销随接触数、休眠体数量、Broadphase 里 AABB 的重叠程度剧烈变化，死亡螺旋在真实机器上更像「某些帧特别贵」而不是「每帧均匀变贵」。
4. **碰撞不是点采样。** 我的穿透模型只看每步首尾两个位置；真实引擎的 Broadphase 是 AABB 对，Narrowphase 有 margin、有 speculative contact，所以同样的速度下实测穿透率会比我的模型低——我的数是「不加任何补救时的上界」，不是「Box2D 的表现」。

## 引用与延伸

- G. Fiedler, *Fix Your Timestep!*, Gaffer On Games, 2004-06-10，https://gafferongames.com/post/fix_your_timestep/ 。固定步长的四种写法、累加器、`frameTime > 0.25` 的闸门、渲染插值的 `alpha = accumulator / dt`、「spiral of death」这个名字，以及「物理行为取决于你传进去的 delta time」这句判断，都出自这一篇。正文的两段引文按页面现行文本抄录。
- Godot Engine 4 文档，*ProjectSettings*，`physics/common/max_physics_steps_per_frame`（默认 8）、`physics/common/physics_ticks_per_second`（默认 60）、`physics/common/physics_interpolation`，https://docs.godotengine.org/en/stable/classes/class_projectsettings.html 。「physics spiral of death」那段解释也在这个条目下。
- Box2D 文档，*Overview*（continuous collision 一节），https://box2d.org/documentation/ 。离散时间步导致隧穿、TOI 与 speculative collision 两种补救。
- E. Hairer, C. Lubich, G. Wanner, *Geometric Numerical Integration: Structure-Preserving Algorithms for Ordinary Differential Equations*, 2nd ed., Springer, 2006。辛积分器为什么长期不漂能量、显式欧拉的每步放大因子 1 + (ω·dt)²、以及「辛方法保能量在振荡而非单调漂移」的标准叙述都在前几章。正文只用了结论，没有引用它的定理编号；也没有核对具体章节页码。
- G. Strang, *Computational Science and Engineering*, Wellesley-Cambridge Press, 2007。RK4 与相图的基础讲法（背景，正文没有引用具体结论）。
- IEEE 754-2019, *IEEE Standard for Floating-Point Arithmetic*。浮点加法的舍入、以及加法不满足结合律，是标准的直接结果；(1.0+1e16)−1e16 = 0 那个例子是我自己算的，不是抄来的。
