# # 九成满的表，查不到要走 56 步

4099 个槽的表装到九成满，查一个存在的键平均走 5.6 步，查一个不存在的键平均走 56 步。同一张表、同一条规则——「撞了就试下一个槽」——代价差十倍，而这条规则从 1957 年一直用到今天的哈希表里。这一篇从一张能手算的 7 格表出发，把簇（cluster）、Knuth 的两个公式、Robin Hood 的让位、墓碑删除、SwissTable 的分组比较串起来，最后回答一个工程问题：装载率到几成就该扩容。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 47 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 1 秒）
```

两个脚本都是确定性的，重跑得到逐字节相同的图与数字。`run_model.py` 只用标准库：随机数是 splitmix64（不是 Python 内置 `hash`，那个随进程随机化，不可复现），表长取素数，探测次数由实现自己数。

`run_model.py` 里最慢的一段是 65 537 个槽那张表装到 98%（`finite` 实验），约 25 秒。不需要它的话，删掉那一段就回到 20 秒左右。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，12 张图按出现顺序编号 |
| `assets/01..12-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `examples/probe.py` | 模型：线性探测、Robin Hood、双散列、Knuth 公式 |
| `examples/run_model.py` | 写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |
| `examples/figkit.py` | 画图小工具（几何断言、字号换算） |

## 关于数字

正文里每一个数都来自 `examples/results.json`，图也一样。四处可以手算复核：

1. 手算表 `toy`：m = 7，键 1、8、15、2、9 的起点分别是 1、1、1、2、2，轮流往后挤，最后落成一条 5 格长的簇（槽 1 到槽 5）；删掉 8 之后查 15 仍是 3 次，因为墓碑跳过去了。
2. 公式 `α = 5/7`：`½(1+1/(2/7)) = 2.25`，`½(1+1/(2/7)²) = 6.625`。
3. 格子图 `grid`：m = 64 装 57 个键，最长一条簇 25 格；同一批键取前 32 个，最长 7 格。
4. Robin Hood 手算 `rhdemo`：m = 11 依次插 8、9、19、30，最后槽 8 是 8（距离 0）、槽 9 是 19（距离 1）、槽 10 是 30（距离 2）、槽 0 是 9（距离 2），让位发生 2 次。

模型没做的事：任何真实库的吞吐与延迟、缓存命中率、HashDoS 复现。`sources.md` 里逐条写明哪些是设定值、哪些没算、哪些是文献背景。
