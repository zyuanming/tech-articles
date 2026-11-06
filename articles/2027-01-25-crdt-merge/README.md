# # 手机删、平板加，最后谁算数

两台设备同时改同一个购物车：手机删了 apple，平板加了 apple。两条修改都是用户真的做的，都得算数——可合并的结果不能取决于谁的网速快。

这篇文章讲 CRDT 怎么把这种「冲突」变成一道加法题：合并要守交换、结合、幂等三条律，破了哪一条都会出现两台机器算出两个答案。所有数字来自 `examples/` 里一份六百多行的模型，五种 CRDT 与两种朴素做法在同一条跑道上对比。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 1 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 5 秒）
```

`crdt.py` 与 `run_model.py` 只用 `hashlib` / `json` / `math` / `random`。`build_figures.py` 需要 Pillow（3.14.7 / 12.3.0，见 `examples/run-environment.json`）。两个脚本都是确定性的，重跑得到逐字节相同的图。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，19 张图按出现顺序编号 |
| `assets/01..19-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面（三格 7 / 5 / 2 → 14） |
| `originals/` | INRIA 报告 PDF 原件与按页渲染的封面裁图 |
| `examples/crdt.py` | 模型：五种 CRDT 与两种朴素做法，各自的合并函数 |
| `examples/run_model.py` | 写出 `results.json`（九组实验） |
| `examples/build_figures.py` | 画图，写出 `examples/figure-metadata.json` |
| `examples/figure-metadata.json` | 每张图的尺寸、字号下限、用途与身份（19 行，按 `path` 排序） |
| `examples/figkit.py` | 画图用的几何引擎（画布宽度、安全边带、字号下限的检查都在这里） |

## 关于数字

同一批状态、同一批合并，八种规则走同样的测试台：

| 合并规则 | 200 种顺序的结果数 | 重复投递 1 / 2 / 5 次之后 |
| --- | --- | --- |
| LWW 寄存器 | 1 | 草稿 v3（三次都一样） |
| G-Counter | 1 | 14 / 14 / 14 |
| PN-Counter | 1 | 11 / 11 / 11 |
| 2P-Set | 1 | 状态不变 |
| OR-Set | 1 | 状态不变 |
| G-Set | 1 | 状态不变 |
| 后到覆盖 | 3 | 2 / 2 / 2 |
| 合并相加 | 1 | 14 / 28 / 70 |

断网愈合是另一个场景：`{A,B}` 与 `{C}` 断开，两侧各加 100 次、一共 300 次。

| 规则 | 愈合后记住的增量 | 真相 |
| --- | --- | --- |
| G-Counter | 300 | 300 |
| PN-Counter | 300 | 300 |
| 合并相加 | 300 | 300 |
| 后到覆盖 | 100 | 300 |

可以手算复核的几条：

1. G-Counter 三格 7 / 5 / 2，取最大之后还是 7 / 5 / 2，和为 14。
2. 同一份状态投 5 次：取最大得 14，「合并相加」得 70。
3. PN-Counter：14 − 3 = 11。
4. 分区两侧各 100 次：合并后 300；后到覆盖只剩 100。
5. OR-Set 的 apple：标签 `{A#1, B#2}` 减作废 `{A#1}` 剩 `{B#2}`，所以还在。

## 结论

- 合并的三条律（交换、结合、幂等）不是学术洁癖：后到覆盖破第一条，合并相加破第三条，各有各的错法。
- 计数器要记「每台各加了多少」，不是「最后的值」；集合要记「加过什么、删过什么」，冲突才会变成并集。
- 并发加与删要有明确的取舍，加赢还是删赢是产品语义，不是对错。
- 代价都在状态里：两千次操作后 OR-Set 的状态是 53 KB，G-Set 只有 12 KB，多出来的都是墓碑。
