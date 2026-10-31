# 可复算说明

正文里每个数字都从这里来：边带的条数、贝塞尔函数的取值、带宽与 Carson 规则的差、
混叠折回的位置、自反馈把正弦变成噪声的过程。

## 跑一遍

```sh
python3 examples/run_model.py       # 全部测量 -> examples/results.json
python3 examples/build_figures.py   # 16 张示意图 + cover.png
python3 examples/photos.py          # 3 张照片/文件的版式（需要 originals/）
```

要求：Python 3.10+，绘图需要 Pillow。除 Pillow 外只用标准库——**没有 numpy**，
FFT 是自己写的 30 行 radix-2。

单独重画某张图：`python3 examples/build_figures.py 12`。

## 文件

| 文件 | 作用 |
| --- | --- |
| `examples/fm.py` | 调相波形、FFT、贝塞尔函数、包络、四组实验 |
| `examples/run_model.py` | 跑全部测量，写 `results.json` |
| `examples/figkit.py` | 画图工具（MIT），自带字号与越界自检 |
| `examples/build_figures.py` | 16 张示意图与封面 |
| `examples/photos.py` | 照片与专利附图的版式 |
| `examples/results.json` | 全部测量结果 |
| `originals/` | 三份 Wikimedia 原件（含专利 PDF 与从它渲染的附图） |

## 四件要说清楚的事

1. **本文算的是调相（PM），不是调频（FM）。** 公式是 `sin(2πfc t + I·sin(2πfm t))`，
   相位上加偏移。历史上 DX7 也是这么实现的，只是名字一直叫 FM。真调频
   （对频率积分）在相位上的效果相同，但载波频率会随调制漂移。
2. **"几条线"的口径是"−60 dB 以上的局部极大值"**，载波和两边都算。换个门限，
   数字就变——正文里每次都写明了门限（−40 / −45 / −55 / −60）。
3. **贝塞尔函数用积分算**（Simpson 法，20000 步），不是查表。J₂(2) = 0.3528，
   与教科书一致，可以用来自检。
4. **混叠那一节是"算 + 验"**：先用 |J_n| > 0.01 找出最高边带，算出它折叠后应该
   落在哪里，再回到频谱里找那条线。找到了（误差在 2 Hz 内），才写进正文。

## 许可

代码 MIT，见 `../LICENSE-CODE.txt`。正文与图 CC BY 4.0。照片与专利附图许可见 `sources.md`。
