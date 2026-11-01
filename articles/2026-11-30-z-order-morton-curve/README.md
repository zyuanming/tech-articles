# 一条线穿过六十四格：Z 序怎么把二维压成一维

把二维坐标压成一个整数键，代价是什么，值不值。

这一篇从一个八乘八的网格开始：把 x 和 y 的二进制位交替插在一起，六十四个格子就排成了一条"Z"字形的线。然后一节一节地追问它到底买到了什么——为什么对齐的方块在编号上是连续的一段，为什么方块挪一格优势就掉一半，为什么显卡的纹理非要按八乘八的小块排，为什么三维体素引擎宁可用它存节点却不拿它当查询索引。中间拿 Hilbert 曲线做了个对照，最后给出一张"什么时候别用它"的清单。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 6 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png
```

两个脚本都是确定性的，重跑得到逐字节相同的图。`run_model.py` 只用标准库（自写位交错、Hilbert 编号、xorshift32）；`build_figures.py` 需要 Pillow（3.14.7 / 12.3.0，见 `examples/run-environment.json`）。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，18 张图按出现顺序编号 |
| `assets/01..18-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `originals/` | 两张 Commons 原图，未改动 |
| `examples/zorder.py` | 模型：位交错、Hilbert 编号、步长统计、矩形段数、三维、压缩、xorshift32 |
| `examples/run_model.py` | 写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |

## 关于数字

正文和图里的每一个数字都由 `examples/zorder.py` 算出。模型里的三件事都是可以直接手算核对的：位交错（`morton2(5, 3) == 27`，图 3）、Hilbert 编号是 0 到 63 的一个排列且相邻编号恰好相邻（图 8，最长步长 1.000）、对齐方块在 Z 序下编号连续（图 9，一段）。

有两处结论本身是"负面"的，文章没有绕开：随机偏移的方块，Z 序的段数比逐行还多（图 10，八乘八 14.28 对 8.00）；三维里随机偏移的立方体也一样（图 14，24.37 对 16.00）。这两条都是从同一份代码里跑出来的，没有为叙事挑过参数。

`sources.md` 里写明了模型设定、每个关键数字的来历，以及明确没做的事（没在真机上测缓存命中率、没对着某款 GPU 的寄存器文档核对分块格式、没做目视看图）。
