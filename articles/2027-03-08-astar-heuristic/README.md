# A* 为什么会白忙一场

空地 6×6、四方向，Dijkstra 展开 36 个格子，A* 也展开 36 个——整张图一共 36 个，连顺序都一样。这一篇从这个「一个不省」的起点往前走：八方向为什么突然只碰 6 格，一道墙为什么把四方向的 A* 打回原形，33×33 有障碍的图上 906 怎么变成 278，把 h 乘以 w 之后展开数为什么又掉到 47 而代价只多 1.15%，以及斜走同价的网格上欧氏距离为什么能让 A* 走出 10 而不是 9。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 0.22 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 3.0 秒）
```

两个脚本都是确定性的，重跑得到相同的数字与图（`results.json` 大小 233606 字节）。只用标准库：随机障碍由自己写的 SplitMix64 生成（地图种子 77、一致性检验种子 20270301、随机小图种子 20270308），不依赖 `random` 的实现细节，也不依赖哈希顺序——堆的键里带一个自增计数。

`build_figures.py <N>` 可以只重画第 N 张，但那样会把 `examples/figure-metadata.json` 截断成一张，正式出图请整跑。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，12 张图按出现顺序编号 |
| `assets/01..12-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `examples/astar.py` | 网格、五种启发式、A*（含允许/禁止重开闭表、同分按 h 排序）、`SplitMix64` |
| `examples/run_model.py` | 跑全部实验，写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |
| `examples/figkit.py` | 画图小工具（几何断言、字号换算） |

`astar.py` 的入口是 `search(grid, start, goal, h=..., weight=1.0, reopen=True, tie_break=False)`，返回 `expansions`、`generated`、`open_max`、`cost`、`path`、`reopenings`、`trace`。`expansions` 是「弹出并处理」的次数，也是它进闭表的次数；`open_max` 是堆里同时存在的最大条目数。

## 关于数字

正文里每个数都来自 `examples/results.json`，图也一样。数的是**展开次数、开表峰值与路径代价**，不是时间。六处可以手算复核：

1. 空地上 f 恒等于 10：第 i 个格子（沿上边框）`g = i`、`h = (5−i) + 5 = 10−i`，相加得 10。推广到任意格子也对，因为 `x + y + (5−x) + (5−y) = 10`。
2. 八方向空地上 `f = 5√2 = 7.0710678…`，模型给出 7.0711（斜走代价用 `math.sqrt(2.0)`）。展开 6 格就是对角线上的 (0,0) 到 (5,5)。
3. 墙图的最优代价：四方向 3 + 3 + 1 + 4 + 3 = 14（右 3、上 3、穿缺口 1、右 4、下 3）；八方向 6 段斜走（6√2 = 8.48528）加 2 段直走 = 10.48528，模型给出 10.4853。模型给出 14.0 与 10.4853。
4. `sweep` 的分段：w = 1.00 → 278，1.25 → 63，1.50 → 53，1.75 → 51，2.00 → 47，2.25 → 47，2.50 起一直 46 到 5.00。代价从 1.25 起就锁死在 51.6985；51.6985 / 51.1127 = 1.01146，与 `ratio` 字段的 1.0115 一致。
5. 高估一步的账：8×8 斜走同价，左上角到右下角的实际最短步数是 7，欧氏距离 √(7² + 7²) = 9.899，比真实代价大 2.899，于是 h 把「斜着走」说成贵。模型在该图上跑出的最优是 9.0，欧氏给出 10.0。
6. 一致性的那个数：√2 − 1 = 0.41421，正是斜走同价时 octile 与欧氏的 `worst_excess`。√2 定价下三种 h 的超出量都是 0.0。

模型没做的事：任何墙钟计时（正文里也没有计时结论）、JPS 与跳点剪枝、nav mesh 与层级寻路、双向搜索、IDA* 的实测、多层地形代价（`cost` 矩阵在实验里全是 1.0，只有斜走的 √2 与「斜走同价」的 1.0 两种定价）、真实游戏关卡的数据。`sources.md` 里逐条写明哪些是文献、哪些是读了文档、哪些没做。

## 许可

正文与图：CC BY 4.0。代码（`examples/` 下所有 `.py`）：见 [LICENSE-CODE.txt](LICENSE-CODE.txt)。
