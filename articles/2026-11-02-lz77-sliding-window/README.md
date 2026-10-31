# 可复算说明

正文里每个数字都来自这里：压缩率、匹配长度分布、距离分布、贪心与懒匹配的差距、
全同字节能压到多少、随机数据会膨胀多少。

## 跑一遍

```sh
python3 examples/run_model.py       # 全部测量 -> examples/results.json
python3 examples/build_figures.py   # 17 张正文图 + cover.png
python3 examples/photos.py          # 2 张肖像（需要 originals/）
```

要求：Python 3.10+，绘图需要 Pillow。**测量部分只用标准库**（`zlib` 用来做对照组）。

## 文件

| 文件 | 作用 |
| --- | --- |
| `examples/lz.py` | LZ77 编码器 / 解码器 / 位宽账 / 五组实验 |
| `examples/run_model.py` | 跑全部测量，写 `results.json` |
| `examples/figkit.py` | 画图工具（MIT），自带字号与越界自检 |
| `examples/build_figures.py` | 17 张示意图与封面 |
| `examples/photos.py` | 两张肖像的版式 |
| `examples/results.json` | 全部测量结果 |
| `examples/corpus/alice.txt` | 语料：《爱丽丝梦游仙境》第一章，公有领域 |

## 四件要说清楚的事

1. **这是教学版 LZ77**：定长 token（字面量 9 bit，匹配 24 bit）、单条哈希链、
   没有熵编码。它跑出来的 0.519 不能和 gzip 的 0.361 直接比高低，
   只能用来解释机制。`zlib.compress(level=9)` 只作对照。
2. **每一份输出都做了解码回环**：`compress()` 之后立刻 `decompress()` 并断言
   等于原文。任何一次测量如果编码器写错了，脚本会当场失败而不是给出一个好看的数。
3. **`MIN_MATCH = 3`、`MAX_MATCH = 258`、`WINDOW = 32768`** 取的是 deflate 的规格，
   不是本文发明的，这样"每个指针 15 bit"才说得通。
4. **语料是真实的，日志与随机数据是合成的**。日志用固定模板生成（`make_log`），
   随机字节用线性同余生成器（`random_bytes`），都在代码里，可以复现。

## 许可

代码 MIT，见 `../LICENSE-CODE.txt`。正文与图 CC BY 4.0。
`corpus/alice.txt` 是公有领域文本（Project Gutenberg #11，Lewis Carroll, 1865）。
两张肖像的许可见 `sources.md`。
