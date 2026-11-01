# 听歌识曲：它是怎么从三秒杂音里认出歌名的

从波形到谱图、谱峰、组合哈希、偏移投票的完整链路，配一个只用标准库、两秒跑完的小模型。

- 正文：[`read.md`](read.md)
- 来源与许可：[`sources.md`](sources.md)
- 审读记录：[`review.md`](review.md)
- 封面：`cover.png`

## 复现

需要 Python 3.10 以上，只用标准库。

```bash
cd examples
python3 run_model.py       # 写出 results.json（所有数字的唯一来源）
python3 build_figures.py   # 重新生成 assets/ 与 figure-metadata.json
```

`run_model.py` 的输出和正文里的表格逐条对应；如果改了模型参数，正文里的数字要一起改。

## 结构

| 文件 | 作用 |
| --- | --- |
| `examples/shazam.py` | 指纹模型：合成、分帧、FFT、找峰、组键、查表、投票 |
| `examples/run_model.py` | 跑完全部实验，写 `results.json` |
| `examples/build_figures.py` | 18 张示意图的绘制代码 |
| `examples/figkit.py` | 画图工具（画布宽度、字号下限、越界检查） |
| `examples/figure-metadata.json` | 每张图的尺寸、最小字号、用途、身份 |
| `originals/` | 图片原件归档位置（本文的图全部由代码生成） |

## 关于数字

正文里出现的每个数都来自 `results.json`。模型是缩小的：4 kHz 采样、512 点 FFT、三首合成小曲。
绝对票数不可外推到真实系统，能外推的是"票聚不聚"这个判别方式。
