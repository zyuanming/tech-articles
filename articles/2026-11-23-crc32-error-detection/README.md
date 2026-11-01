# CRC-32：那条 4 字节的尾巴

每一帧以太网、每一个 ZIP 条目、每一张 PNG 都挂着一小段只回答一个问题的数：这段字节还是刚才那段吗？这一篇把这个数的来历拆开——把字节看成 GF(2) 上的多项式，做一次除法，取余数。然后讲它能保证什么（所有 ≤32 位的突发错误）、第一个漏网的在第 33 位（图案就是生成多项式自己）、以及它完全挡不住的两种情形：对调换字节之外的故意篡改，和「错在哪儿」。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 28 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png
```

两个脚本都是确定性的，重跑得到逐字节相同的图。`run_model.py` 只用标准库（自写 GF(2) 长除法、自写 xorshift32）；`build_figures.py` 需要 Pillow（3.14.7 / 12.3.0，见 `examples/run-environment.json`）。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，20 张图按出现顺序编号 |
| `assets/01..20-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `originals/` | 两张 Commons 原图，未改动 |
| `examples/crc.py` | 模型：GF(2) 运算、8 个标准变体、突发穷举、漏检率实验、帧布局 |
| `examples/run_model.py` | 写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |

## 关于数字

正文里每一个数都来自 `examples/results.json`；图也一样。8 个变体的自检值全部对上公开的 CRC 目录，逐位实现与查表实现在同一串文本上给出同一个值——这两件事是「模型没有把反射或初值搞反」的证据，比「看起来对」可靠。

模型能实测的部分有边界：突发错误穷举到 16 位（17–32 位靠证明），随机漏检率用 8 位 CRC（32 位在这种样本量下测不出来），码距只在很短的报文范围内穷举。`sources.md` 里逐条写明了哪些是设定值、哪些没算、哪些没验证。
