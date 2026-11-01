# 来源与说明

## 图片

四张实物照片全部来自 Wikimedia Commons，下载的是原始文件，只在宽度超过 1062 px 时按比例缩到 1062 宽（`examples/build_figures.py` 里的 `photo()` 只缩放不重压，宽度已经小于 1062 的直接复制字节）。未裁切。

| 文件 | 原始尺寸 | 作者 | 许可 | 原始页面 |
| --- | --- | --- | --- | --- |
| `02-carmack.jpg` | 2000×3008 | QuakeCon | CC BY 2.0 | <https://commons.wikimedia.org/wiki/File:John_Carmack_-_QuakeCon_2008_-_02.jpg> |
| `15-quakecon.jpg` | 1600×1200 | QuakeCon | CC BY 2.0 | <https://commons.wikimedia.org/wiki/File:Quake_III_Arena_Duel_Finals_-_QuakeCon_2003_-_01.jpg> |
| `14-pentium3.jpg` | 924×864 | Lp（it.wikipedia） | Public domain | <https://commons.wikimedia.org/wiki/File:Intel_Pentium_III_Coppermine_die.jpg> |
| `19-sgi-indy.jpg` | 3732×2369 | Peter Wallén | CC BY 3.0 | <https://commons.wikimedia.org/wiki/File:SGI_Indy_(1).jpg> |

其余 17 张（`01`、`03`–`13`、`16`–`18`、`20`、`21` 和 `cover.png`）是本文原创的教学示意，由 `examples/build_figures.py` 生成，不是照片，也不代表任何真实设备的测绘图。

照片的身份只有一条：它拍的那个东西。`02-carmack.jpg` 是 2008 年 QuakeCon 上的 John Carmack，不是 1999 年写引擎时的他；`15-quakecon.jpg` 是 2003 年的比赛现场，不是 1999 年；`14-pentium3.jpg` 是 Pentium III Coppermine 的裸片照片，本文没有声称当年跑 Quake III 的就是这一颗；`19-sgi-indy.jpg` 是 SGI Indy 工作站，本文没有声称这条代码出自这台机器。

## 数字

正文和图片里的每个数字都由 `examples/rsqrt.py` 算出、`examples/run_model.py` 写进 `examples/results.json`，`examples/build_figures.py` 只从 `results.json` 取值（密集曲线另外 import 同一个模块采样）。跑一遍：

```sh
cd examples && python3 run_model.py && python3 build_figures.py
```

纯标准库，不需要安装任何东西。每次位运算后都做 float32 舍入（`struct.pack('<f', …)`），这一点和当年的 C 代码一致；**没有**模拟 x87 的 80 位中间结果，所以某些中间值可能和真机差最后一位。

关键数字的来历：

- **3.4369%**：只做位运算时，14 个倍频程（0.01 到 100）、2000 个采样点上的最大相对误差。
- **0.175147%**：一次牛顿迭代后的同一指标。**0.000466%** 是两次迭代。
- **σ = 0.0450466**：由原版常数反推，`(A·127 − 0x5f3759df) / A`，A = 1.5·2²³。
- **0x5f3759dd**：在原版前后各 300 个整数里搜"一次迭代后最坏误差"最小者。这个搜索的结果依赖采样密度，见下。
- **常数对比表**：`0x5f3759df`、`0x5f375a86`（Lomont 2003）、`0x5f37642f` 三个值各跑同一套指标。

## 明确没有做的事

- **没有实测性能。** 正文里"每次 1.2 ns 对 22 ns、一帧 3 ms 对 55 ms、差 18 倍"是**量级估计**，用的是当代 x86 上近似指令与 `sqrt`+`div` 常见延迟的量级，不是本文在 1999 年硬件上的测量。`results.json` 里的 `payload` 字段就是这组假设，换一组单价比例就变。
- **没有在原始硬件上验证位模式。** 模型按 IEEE-754 float32 规范做舍入，与 x86 结果应当一致，但本文没有在 Pentium III 上跑过。
- **没有确定这条代码的作者。** 常见的归因（Gary Tarolli、Greg Walsh、Cleve Moler 等）在公开讨论里都被提到过，也都被当事人以不同方式淡化过。本文只写"随 Quake III 流传"，不指定发明人；`18-timeline.png` 里也只放有公开记录可查的节点。
- **常数搜索不保证全局最优。** 误差曲线的峰很尖，采样 600 点与 2000 点会给出不同的"最好整数"（本文用 600 点在原版附近搜到 `0x5f3759dd`，Lomont 用更密采样给出 `0x5f375a86`）。两者差距在 1e-6 量级，说明这片地形几乎是平的。正文里把这个限制写出来了。
- **没有目视检查图片。** 见 `review.md`。

## 引用与延伸

- Quake III Arena 源码（2005 年以 GPL v2 公开），`code/game/q_math.c` 里的 `Q_rsqrt`。
- Chris Lomont, *Fast Inverse Square Root*（2003），推导与常数搜索。
- 本文的推导路线（用 log₂ 近似解出常数）与 Lomont 报告中的思路一致，但公式与图全部重算，没有复制报告里的数字。
