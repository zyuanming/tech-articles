# 一次失败，不必从零开始

在 `abcabcabd` 里找 `abcabd`，朴素的写法要 4 个窗口、14 次字符比较；KMP 用 10 次，Boyer–Moore–Horspool 用 7 次。这一篇把这个小例子拉成四种算法、三种语料、两种对抗输入的账：省下来的到底是窗口数还是每窗口的比较数，KMP 为什么在英文上几乎赢不了，BMH 在什么输入上会塌成二次，以及 glibc 的 `strstr` 为什么最后选了 Two-Way。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 110 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 3.8 秒）
```

两个脚本都是确定性的，重跑得到相同的数字与图。只用标准库：随机语料由自己写的 SplitMix64 生成（种子 20270301），不依赖 `random` 的实现细节。`run_model.py` 慢在对抗输入那一段——朴素匹配在 n = 64000 时真的要比 7.68 亿次。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，13 张图按出现顺序编号 |
| `assets/01..13-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `examples/strsearch.py` | 四种算法（朴素、KMP、BMH、BM）+ 前缀函数、坏字符表、好后缀表 |
| `examples/run_model.py` | 跑全部实验，写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `figure-metadata.json` |
| `examples/figkit.py` | 画图小工具（几何断言、字号换算） |

## 关于数字

正文里每个数都来自 `examples/results.json`，图也一样。数的是**字符比较次数**，不是时间。六处可以手算复核：

1. 小例子 14 次：四个窗口的代价是 6、1、1、6。第一个窗口比了 5 次对上、1 次失败；后两个窗口都是第一个字符就不对。
2. KMP 的 10 次：第一段 6 次，失配后 `j = failure[4] = 2`，第二段只比 `c a b d` 四次，所以是 6 + 4。KMP 不是从窗口 3 重新开始，它没有回头。
3. BMH 的 7 次：第一次只看窗口 0 的最后一个字符，文本 `c` 对模式 `d` 失败，表说 `c` 挪 3 格；第二段整段 6 次全中。
4. 对抗输入 A 的公式：模式长 m = n/4，窗口数 n−m+1，每窗口比满 m 次，所以 m(n−m+1) ≈ 3n²/16。n = 64000 时是 7.68 亿，模型跑出 768016000，一位不差。
5. KMP 的 2n 上界：8000 个 a 的文本、模式 `aaaaaaab`，实测 15993 次比较，略低于 2n = 16000。
6. 前缀函数表 `[0,0,0,1,2,0]`：`abcabd` 每个前缀的「最长真前缀 = 真后缀」长度，逐个手算在正文第二节。

模型没做的事：任何墙钟计时、任何 libc / 标准库的实测、SIMD 与缓存效应、Unicode 归一化的实现、多字节编码下的真实语料。`sources.md` 里逐条写明哪些是文献、哪些是读了源码、哪些没做。

## 许可

正文与图：CC BY 4.0。代码（`examples/` 下所有 `.py`）：见 [LICENSE-CODE.txt](LICENSE-CODE.txt)。
