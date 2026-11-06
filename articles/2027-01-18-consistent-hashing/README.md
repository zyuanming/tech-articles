# # 加一台机器，90.9% 的 key 都搬了家

十台缓存机，二十万个 key。加一台本来该搬 9% 的数据，用 `h % N` 分片实际搬了 90.9%。

这篇文章讲一致性哈希怎么把这个数压回 9%：把 key 和节点钉在同一个圆上，量正比于变化量而不是总量；再讲为什么一台机器一个点不够（最忙的机器扛 2.31 倍平均负载），虚拟节点怎么修（128 个点 → 1.11 倍），以及连表都不存的 jump hash。所有数字来自 `examples/` 里一份两百多行、只用标准库的模型。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 6 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 35 秒）
```

`ch.py` 与 `run_model.py` 只用 `hashlib` / `bisect` / `math` / `random`。`build_figures.py` 需要 Pillow（3.14.7 / 12.3.0，见 `examples/run-environment.json`）。两个脚本都是确定性的，重跑得到逐字节相同的图。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，19 张图按出现顺序编号 |
| `assets/01..19-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面（取模 90.9% / 环 9.6% / 理想 9.1% 三条横条） |
| `originals/` | 一张 Commons 原图（David Karger 肖像），未改动 |
| `examples/ch.py` | 模型：取模、哈希环（含虚拟节点与弧段）、jump hash、几个统计小工具 |
| `examples/run_model.py` | 写出 `results.json`（十组实验） |
| `examples/build_figures.py` | 画图，写出 `examples/figure-metadata.json` |
| `examples/figure-metadata.json` | 每张图的尺寸、字号下限、用途与身份（19 行，按 `path` 排序） |
| `examples/figkit.py` | 画图用的几何引擎（画布宽度、安全边带、字号下限的检查都在这里） |

## 关于数字

同一批 key（20 万个）、同一批节点（10 台），四组方案在同一条跑道上对比：

| 方案 | 加一台要搬 | 少一台要搬 | 最忙/平均 | 要存的点 | 查找 |
| --- | --- | --- | --- | --- | --- |
| `h % N` | 90.93% | 89.88% | — | 10 | 取模 |
| 环，每节点 1 个点 | 5.72% | — | 2.31 | 10 | 二分 3.49 次 |
| 环，每节点 128 个点 | 9.64% | 10.25% | 1.11 | 1280 | 二分 10.39 次 |
| jump hash | 9.14% | 9.92% | 1.01 | 0 | 循环 2.93 圈 |

理论上限：扩容 1/11 = 9.09%，缩容 1/10 = 10%。取模的 90.93% 正好等于 10/11。

可以手算复核的几条：

1. `h % 10 == h % 11` 的概率是 1/11，所以搬家 10/11 = 90.9%。
2. 20 万 ÷ 10 = 2 万，`hist.v1` 的均值就是 20000（最忙 46128，最闲 7970）。
3. 1280 个点二分需要 log₂1280 ≈ 10.32 次，实测 10.39。
4. 4096 个桶的 jump 平均 8.87 圈，ln 4096 = 8.32。
5. 每节点 1 个点时最宽的一段弧占环的 23.1%，平均值是 10%。

## 结论

加机器本该只搬 9% 的数据。取模做不到，因为它把 N 放进了运算；环做到了，因为一个 key 只看它右边第一个节点是谁。代价是要存一张环表，而表的大小由虚拟节点数决定——128 个点是工程上常见的一段甜区。

`read.md` 里对每个数字都给了对应的实验和口径；哪些结论不该外推，`sources.md` 第四节写清楚了。
