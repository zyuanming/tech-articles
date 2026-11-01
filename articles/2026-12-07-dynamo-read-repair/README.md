# 三个副本，一个落后：读修复与暗示移交

写只落了两个副本，第三个怎么办。

Dynamo 那篇论文最容易被跳过的部分，是它怎么处理"写没落到位"。这篇文章把这条线单独拎出来：一致性哈希把键放到环上，R 和 W 决定读写各碰几个副本，R + W > N 保证两个集合相交；可一旦有机器挂了，相交的前提就没了，于是需要松散法定人数、暗示移交、读修复、反熵。七个方案跑在同一个假集群上，同一套故障，用同一份代码量出旧值比例、落后副本数和收敛速度。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 26 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 5 秒）
```

两个脚本都是确定性的，重跑得到逐字节相同的图。`run_model.py` 只用标准库（自写 xorshift32、FNV-1a、一致性哈希环、Merkle 树比对）；`build_figures.py` 需要 Pillow（3.14.7 / 12.3.0，见 `examples/run-environment.json`）。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，18 张图按出现顺序编号 |
| `assets/01..18-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `originals/` | 两张 Commons 原图，未改动 |
| `examples/dynamo.py` | 模型：环、副本、读写、故障、暗示、反熵、法定人数抽样、Merkle 成本 |
| `examples/run_model.py` | 写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `examples/figure-metadata.json` |
| `examples/figure-metadata.json` | 每张图的尺寸、字号下限、用途与身份（18 行，按 `path` 排序） |

## 关于数字

正文和图里的每一个数字都由 `examples/dynamo.py` 算出，没有一个是手写进去的。几次抽样也可以独立复核：

- R=1、W=1 时，读集与写集在三个副本里错开的概率是 2/3：写落在 3 个副本里的任意一个，读也只问一个，9 种组合里有 6 种两边不相交。模型抽样给 66.7%。
- 4096 个键、16 叉的哈希树，只有一个叶子不同：根、16 个桶、下钻那一桶的 16 页、下钻那一页的 16 个叶子，两边各算一次，加起来 98 个；一把梭是 4096 × 2 = 8192 个。
- 三副本里落后的那份，靠读修复要等它出现在读集里：R=2 时一次读有 2/3 的概率碰到某个指定副本，这不是"修得快"的意思。

有两处结论本身是"负面"的，文章没有绕开：E 方案（反熵）的旧值比例比 D 方案（只有暗示移交）还高 0.6 个百分点，单次运行不足以支撑"反熵更能降旧值读"的说法；G 方案（R=3、W=3）在结束时完全一致，却有 52% 的写凑不齐三个副本。这两条都是从同一份代码里跑出来的，没有为叙事挑过参数。

`sources.md` 里写明了模型设定、每个数字的来历，以及明确没做的事（没实现向量时钟的分支合并、没有跨机房延迟、没有介质故障、没有做目视看图）。
