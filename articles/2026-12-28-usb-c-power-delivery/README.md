# # 两根线怎么谈出 240 W

把充电器插上，0.3 秒里发生了两件事：前 150 ms 是模拟的（一个 5.1 kΩ 电阻和几个微安的恒流源），之后是数字的（BMC 编码、22 字节报文、CRC、四大功率档、e-marker、20 mV 步进的 PPS）。这篇文章把这两层拆开，每一层都用同一份模型算给你看。所有数字来自 `examples/pd.py`，跑一遍不到一秒。

- 正文：[read.md](read.md)
- 来源与许可：[sources.md](sources.md)
- 审读记录：[review.md](review.md)
- 代码许可：[LICENSE-CODE.txt](LICENSE-CODE.txt)

## 复现

```
python3 examples/run_model.py      # 生成 examples/results.json（约 1 秒）
python3 examples/build_figures.py  # 生成 assets/ 与 cover.png（约 4 秒）
```

`run_model.py` 只用标准库（CRC-32、BMC 编解码、4b5b 查表、报文组帧、功率规则表、PPS 量化、线损计算）。`build_figures.py` 需要 Pillow（3.14.7 / 12.3.0，见 `examples/run-environment.json`）。两个脚本都是确定性的，重跑得到逐字节相同的图。

## 结构

| 路径 | 内容 |
| --- | --- |
| `read.md` | 正文，18 张图按出现顺序编号 |
| `assets/01..18-*` | 正文用图（1062 px 宽），与 `examples/figure-metadata.json` 一一对应 |
| `cover.png` | 1080×1080 封面 |
| `originals/` | 三张 Commons 原图，未改动 |
| `examples/pd.py` | 模型：CC 识别、BMC、4b5b、帧与 CRC、时序、功率规则、PPS、e-marker、线损 |
| `examples/run_model.py` | 写出 `results.json` |
| `examples/build_figures.py` | 画图，写出 `examples/figure-metadata.json` |
| `examples/figure-metadata.json` | 每张图的尺寸、字号下限、用途与身份（18 行，按 `path` 排序） |

## 关于数字

正文和图里的每个数字都由 `examples/pd.py` 算出。几个可以手算复核的：

- CC 上 80 / 180 / 330 µA 乘 5.1 kΩ 是 0.408 / 0.918 / 1.683 V；三个合法区间是 0.15–0.61 / 0.61–1.16 / 1.16–2.45 V。两头都取 ±10%，三档仍然不串档，最窄余量 0.202 V。
- 单比特错的容差是「半格」：一帧 176 位，所以时钟差上限是 0.25 ÷ 176 = 1420 ppm；实测第一个错出现在 1400 ppm。相位偏 0.24 格时零错，偏 0.25 格时 176 位里错 95 位（94 个 0 全被读成 1）。
- 一条 Source_Capabilities 是 2 + 16 + 4 = 22 字节 = 176 位；4b5b 之后 220 位；按每位 64 个采样点算是 14 080 个采样点。CRC 是 0x711DC203，把 176 位里任意一位翻过来，176 次全部抓到。
- 全零的 6 字节负载，不编码时最长同值段 48 位，4b5b 之后 4 位；2000 个随机负载的平均最长段从 5.86 位降到 4.96 位。
- 从插上到 20 V 是 312 ms：150 ms 去抖 + 12 ms 三次报文 + 150 ms 升压（100 mV/ms 爬 15 V）。
- 同一根 0.1 Ω 的线送 100 W：5 V 要 20 A、线上烧 40 W（40%）；20 V 只要 5 A、烧 2.5 W。比值正好 16 倍。240 W 在 48 V 下还是 5 A，线损 2.5 W，占 1%。

有一处结论值得单说：**100 W 在 5 V 下是物理上做不到的**，不是效率问题——20 A 已经超出任何 USB-C 触点的能力。所以从 7.5 W 涨到 240 W，电流几乎没变（1.5 A → 5 A），涨的全是电压（5 V → 48 V）。

`sources.md` 里写明了参考文献、三张照片的许可、每张图的数字来源、模型的简化假设，以及明确没做的事（没有实测设备、没有读规范原文、没有目视看图）。
