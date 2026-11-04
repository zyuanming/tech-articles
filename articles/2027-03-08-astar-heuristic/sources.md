# 来源与说明

## 图片

12 张正文图与 `cover.png` 全部是本文原创的教学示意，由 `examples/build_figures.py` 生成。几何断言写在 `examples/figkit.py` 里：文字不出画布、不互相压、任何字号的文字换算到 354 px 宽的显示宽度后不小于 12 px。没有使用照片、截图或第三方素材，因此不涉及第三方署名与许可。

图里的格子、障碍、展开范围、路径都来自 `examples/results.json`；`build_figures.py` 只负责取值和摆放，不改数。三张地图图（06、07）里每个格子画一次：先按 Dijkstra 的展开集涂浅色，再按 A* 的展开集涂青色，最后叠路径——先画后画的顺序就是「谁走过这里」的叠加关系。

## 数字

正文和图片里的每个数字都由 `examples/astar.py` 算出、`examples/run_model.py` 写进 `examples/results.json`，`examples/build_figures.py` 只从 `results.json` 取值。跑一遍：

```sh
cd examples && python3 run_model.py && python3 build_figures.py
```

纯标准库（画图需要 Pillow），`run_model.py` 约 0.22 秒，`build_figures.py` 约 3.0 秒。整批实验一共几百次 A*，图都很小，慢不起来。

模型设定：

- **计数的定义**：`expansions` 是「从堆里弹出、并且确实被处理」的次数——被闭表挡住的重弹不计。`generated` 是入堆次数（同一格子可能入堆多次）。`open_max` 是堆里同时存在的最大条目数，也就是内存的代理。`cost` 是走出来的路径代价，`reopenings` 是「把已闭的格子重新打开」的次数。
- **`tie_break`**：堆的键从 `(f, counter)` 变成 `(f, h, counter)`，同 f 时先弹 h 小的。`counter` 是自增计数，保证堆里的顺序不受 Python 元组比较或哈希影响。
- **重开闭表**：`reopen=False` 时，弹出到已闭的格子直接丢弃；`reopen=True` 时，若发现更便宜的 g，就把格子从闭表里删掉重新入堆，`reopenings` 加一。
- **斜走不贴墙角**：八方向时，斜着走要求两侧的直角邻居都不是墙，否则跳过。这条在 `neighbors()` 里，用了之后图上就看不到「从两个墙的夹缝里斜穿」的路。
- **空地**：6×6，起点 (0,0)，终点 (5,5)，四方向与八方向各跑一遍，每遍三种配置：Dijkstra、A*、A* 加 `tie_break`。
- **墙图**：9×7，`x = 4`、`y = 1..6` 为墙，只剩 `(4,0)` 一个缺口；起点 (0,3)，终点 (8,3)。四方向与八方向各跑一遍。
- **随机地图**：33×33，`scatter_map(n, density, seed)` 按 SplitMix64（种子 77）撒障碍，18% 与 25% 各一张（181 与 255 个墙），起点 (0,0)、终点 (32,32)。density 再往上（32%、40%）起终点会断开，`optimal_cost` 返回 `None`，所以没有更高的那两档。
- **`sweep`**：在 18% 障碍那张图上把 w 从 1.00 加到 5.00，步长 0.25，共 17 个点，其余参数不变。
- **一致性检验**：21×21、密度 20%、种子 20270301 的同一张图，跑两遍——斜走按 `math.sqrt(2.0)` 计价、斜走按 1.0 计价——对 octile、切比雪夫、欧氏三种 h 逐边检查 `h(u) − h(v) ≤ c(u,v)`，记最大超出量。
- **闭表反例**：8×8、10 道墙、斜走同价（`diag_cost=1.0`），最优代价 9.0。同一张图上跑欧氏（不允许重开、允许重开）、切比雪夫、octile 四种配置。
- **随机小图**：300 组，尺寸 6×6 到 9×9，密度 20%，种子 20270308。每组先求出最优代价，再跑欧氏 h（不允许重开、允许重开）对比，统计次优次数与最大差。
- **自检**：`astar.py` 里没有独立的自检函数；数字的正确性靠第七节那组手算复核（`f = 10`、`5√2`、`14.0`、`10.48528`）和 `Dijkstra`/`A*` 在两个小图上给出相同代价。

关键数字的来历：

- **36 / 36**：空地 6×6 上 Dijkstra 与 A* 的展开数。整张图 36 个格子，f 全是 10，所以 A* 一个都省不下。
- **11 / 30**：加 `tie_break` 之后，空地上 36 → 11，墙图上四方向 48 → 30。
- **6**：八方向空地上 A* 的展开数，就是对角线上的六个格子；Dijkstra 还是 36。
- **48 / 45 / 46 / 25**：墙图上四方向与八方向的 Dijkstra 与 A* 展开数。
- **906 / 278**：18% 障碍图上的展开数，对应正文的 83.2% 与 25.5%，省下 69.3%。A* 的 278 个格子是 Dijkstra 那 906 个的真子集，这一点在 `run_model.py` 里没有写成断言，是写这一篇时用集合比较核过的。
- **52 / 125**：同一张图上 Dijkstra 与 A* 的开表峰值。
- **809 / 445**：25% 障碍图上的展开数。
- **278 → 63 → 47 → 46**：w 分别取 1.00、1.25、2.00、2.50 时的展开数；1.25 起代价锁死在 51.6985。
- **51.1127 / 51.6985 / 60.6274 / 65.2132**：两张随机地图上的最优代价与 w=2、w=3 的代价。
- **10.14 / 2.33**：18% 障碍图上，被省掉的 628 个格子与 A* 展开的 278 个格子，到「起点连终点」这条直线的平均距离（横向偏差）。25% 那张是 11.28 与 4.70。
- **9.0 / 10.0 / 28**：斜走同价那张 8×8 图上，最优代价、欧氏 h 给出的代价、切比雪夫 h 的展开数。
- **3 / 2 / 1.0**：300 组随机小图里，欧氏 h 给出次优的次数（不允许重开）、允许重开后仍次优的次数、最大差距。

## 文献与文档

算法出处，按 DOI 核过卷期页码：

- Hart, Nilsson, Raphael, *A Formal Basis for the Heuristic Determination of Minimum Cost Paths*, IEEE Transactions on Systems Science and Cybernetics 4(2):100–107, 1968，DOI `10.1109/TSSC.1968.300136`。A* 与「h 不高估则最优」的原始出处。
- Dijkstra, *A note on two problems in connexion with graphs*, Numerische Mathematik 1:269–271, 1959，DOI `10.1007/BF01386390`。三页，第二个问题是两点间最短路。
- Pohl, *Heuristic search viewed as path finding in a graph*, Artificial Intelligence 1(3–4):193–204, 1970，DOI `10.1016/0004-3702(70)90007-X`。把 h 乘上系数写进 f 的做法，以及代价不超过 w·C* 的那条界，通常追溯到他这篇。
- Dechter, Pearl, *Generalized best-first search strategies and the optimality of A**, Journal of the ACM 32(3):505–536, 1985，DOI `10.1145/3828.3830`。把 A* 的最优性条件（h 不高估、闭表的处理方式）系统化的一篇。
- Korf, *Depth-first iterative-deepening: an optimal admissible tree search*, Artificial Intelligence 27(1):97–109, 1985，DOI `10.1016/0004-3702(85)90084-0`。IDA*，用重算换内存的那条路。
- Russell, Norvig,《人工智能：一种现代的方法》第 4 版第 3 章。一致性（consistent heuristic）的定义、一致 ⇒ 闭表可以不重开、以及加权 A* 的 w·C* 上界，正文按这一章的写法复述。教科书里的「一致被破坏」反例是一张手写 h 值的图，不是几何地图。

读过的网页：

- Amit Patel, *Introduction to A\**, Red Blob Games, 2014 年起持续更新，`https://www.redblobgames.com/pathfinding/a-star/introduction.html`。抓下来读过：它把广度优先、Dijkstra、A* 排成一条「插入 h」的线，并明确建议「想用 Greedy Best First 的时候，考虑改用带不可采纳（inadmissible）启发式的 A*」。正文第八节把「不可采纳」写成了「主动放弃最优性」。
- Godot 引擎文档 `AStar2D`（stable 分支），`https://docs.godotengine.org/en/stable/classes/class_astar2d.html`。读过的是：`_compute_cost` 是「两个点之间的代价」，`_estimate_cost` 是「到终点的估计」，两者都可被脚本覆盖；`add_point` 的 `weight_scale` 要求「0.0 或更大」，且它乘的是 `_compute_cost` 的结果（即地形权重），不是启发式。文档没有任何一句要求 `_estimate_cost` 不高估——正文第十节说的「检查是你的活」指的就是这件事。

## 明确没有做的事

- **没有计时**。全文没有任何毫秒数。展开次数少不等于墙钟快——真实实现的瓶颈常在堆操作、内存与缓存，Python 模型给不出这个答案。
- **没有把手写 h 值的反例做成图**。教科书里「不一致但不高估」的反例要手写 h 表，本文这批地图上没有出现这种病——它们的不一致都伴随高估，两种毛病混在第九节那 300 张随机图里，没法拆开。
- **没有拆解「重开救回多少」**。300 张随机图上，不重开 3 张次优、允许重开 2 张，减少的那一张算不算「一致性缺口的贡献」，我没做控制实验。
- **没有测真实游戏关卡**。六张地图全是自己生成的：空地、一道墙、两张随机障碍图、两张小图。没有 nav mesh、没有多层地形代价、没有从真实项目导出的地形数据。
- **没有比较 JPS、双向搜索、层级寻路**。正文提到 IDA* 只是为了说明「内存那条路另有解法」，没有实测。
- **没有证明 w·C* 上界**。正文只写「这条界存在、实测都在界内」，证明在 Pohl 1970 与 AIAMA 第 3 章里。
- **没有跑 `AStar2D`**。Godot 那一段只引用文档对两个钩子的定义，没有在该引擎里复现任何实验。

## AI 辅助说明

正文与代码由 AI 助手（Claude）在同一轮会话里写出来，审读也是同一个助手做的，独立性有限。所有数字都能用 `run_model.py` 重跑得到；引用到的 DOI 逐条查过 Crossref 的标题、卷期、页码；两个网页都是实际抓下来读过正文的，抓不到正文的来源没有引用。
