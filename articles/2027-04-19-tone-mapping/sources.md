# 来源与边界

## 这篇文章在讲什么

同一段过曝的场景，8 位屏幕只有 256 格。色调映射就是决定「这些格子怎么分」的那一步。文章用四条能手算的曲线把代价摊开：截断（什么都不做）、Reinhard 的 `x/(1+x)`、带白点的版本、以及一条常见的 ACES 有理拟合。量的东西只有三样——每档曝光占多少码值、对数斜率（局部对比度）随输入怎么变、连续渐变经过曲线之后最长的一段重复有多长。

## 事实支撑范围

### 一、本稿自己算出来的（14 条自验）

`examples/run_model.py` 里的 `selfcheck()` 逐条断言，全部为真：

1. sRGB 编解码往返可逆（0.001 / 0.05 / 0.214041 / 0.5 / 0.9 / 1.0，误差 < 1e−12）
2. sRGB 编码 0.5 对应线性 0.214041
3. Reinhard 在 0.18 处给 0.152542
4. 白点 8 的版本在 8.0 处正好给 1.0
5. 四条曲线在 12 个采样点上都单调不减
6. 截断把 1 到 8 压成 1 个码值
7. Reinhard 在 8 到 16 只剩不到 10 个码值（实测 7）
8. 截断的对数斜率恒为 1
9. Reinhard 在 8 处的对数斜率不到 0.12（实测 0.111）
10. ACES 拟合在 0.18 处给 0.2669
11. ACES 拟合在 1.0 处没有到 1（实测 0.8038）
12. Reinhard 永不达到 1（1000 处 0.9990）
13. 中灰经 Reinhard 后需要抬 20% 以上才回到 0.18（实测 1.2195）
14. 渐变送进截断后，最长一段重复超过 5000 个采样（实测 7171）

这些都是纯算术，`python3 examples/run_model.py` 可当场重算。数字的来源是 `results.json`，图只读它、不重算。

### 二、有文献的

- **Reinhard, Stark, Shirley, Ferwerda 2002**，*Photographic Tone Reproduction for Digital Images*，SIGGRAPH 2002 会议录 pp. 267–276，DOI `10.1145/566570.566575`；期刊版 *ACM Transactions on Graphics* 21(3)。文章用的 `y = x/(1+x)` 与白点版本 `y = x(1 + x/w²)/(1+x)` 出自此文。本稿只用了这两个公式，没有复述它完整的算法（那篇还有 dodge-and-burn 那一层）。该文 2023 年在 *Seminal Graphics Papers* Vol. 2 重印（pp. 661–670，DOI `10.1145/3596711.3596781`），那是重印本，不是原文。
- **Tumblin & Rushmeier 1993**，*Tone reproduction for realistic images*，*IEEE Computer Graphics and Applications* 13(6):42–48，DOI `10.1109/38.252554`。文中「1993 年提出亮度匹配思路」指这篇。本稿只记概念，没有用它的算法。
- **Durand & Dorsey 2002**，*Fast Bilateral Filtering for the Display of High-Dynamic-Range Images*，*ACM Transactions on Graphics* 21(3):257–266，DOI `10.1145/566654.566574`（会议版 DOI `10.1145/566570.566574`）。图中「局部算子 / 光晕」那一行指这一路做法；本稿没有实现它，光晕是定性说明。
- **Drago et al. 2003**，*Adaptive Logarithmic Mapping for Displaying High Contrast Scenes*，*Computer Graphics Forum* 22(3):419–426，DOI `10.1111/1467-8659.00689`。属于同类曲线，本稿没有画它、也没有引用它的任何数值。
- **IEC 61966-2-1**（sRGB 标准）。传输函数用的是标准分段式：`v ≤ 0.0031308` 时线性 `12.92 v`，否则 `1.055 v^(1/2.4) − 0.055`。代码里没有近似。
- **ACES**：完整规范由美国电影艺术与科学学院（AMPAS）牵头制定，核心是 RRT + ODT。本稿**没有读规范原文**，用的只是引擎里流传很广的那条有理拟合 `x(2.51x + 0.03) / (x(2.43x + 0.59) + 0.14)`，而且**没有取到这条拟合的一手出处**（谁、哪一年、哪篇文章）。所以正文、图、代码里一律叫「ACES 拟合」，不叫「ACES 曲线」，也不声称它与官方实现等价。

### 三、属于本稿实测、但没有理论支撑的

- 「每档曝光占多少码值」是把 4000 个采样点送进曲线、数 `srgb_encode` 之后取整的结果。采样密度会影响具体数值（采样越多越接近真值），代码里的 4000 是固定值，换掉会有小改动。
- 「最长的一段重复」同理，用 8192 个采样点扫 0 到 8。`longest_run` 的绝对值依赖采样密度，只有同一批数据内部互相比较才有意义——文章里所有比较都在同一批采样下。
- 条带的「宽窄」在真实屏幕上还受抖动（dithering）影响。真实管线常在量化时加一点噪声把硬台阶打散；本稿直接四舍五入，所以图 7 看到的是**不做抖动时的最坏情况**。

## 十张图逐张

| 文件 | 画的是什么 | 数据来源 |
| --- | --- | --- |
| `assets/01-curves.png` | 四条曲线在 0.001 到 64 的形状，灰虚线是 y = x，蓝圈标中灰 0.18 | `results.json` 的 `table` 与曲线定义 |
| `assets/02-swatches.png` | 八个输入值（0.05…16）在四条曲线下的实际 sRGB 颜色 | `table` 里的线性值 + `srgb_encode` |
| `assets/03-codes-per-stop.png` | 七档曝光各占多少码值，三条曲线分组对照 | `octaves` |
| `assets/04-slope.png` | 对数斜率随输入变化，灰线是 1（对比度原样） | `loglog_slope`，步长 1e−4 |
| `assets/05-shoulder.png` | 1 到 16 倍亮度段，竖线标白点 8 | 曲线直接计算 |
| `assets/06-toe.png` | 0 到 0.2 暗部段，与 y = x 对照 | 曲线直接计算 |
| `assets/07-banding.png` | 0 到 8 的渐变经过四条曲线后的实际颜色条 | `srgb_encode` 逐列着色；文字里的数字来自 `ramps` |
| `assets/08-decide.png` | 按情形选做法的对照表 | `ramps`、`midgray`、文献（局部算子那一行） |
| `assets/09-takeaways.png` | 三句话 | 上文结论 |
| `cover.png` | 封面：同一段渐变在截断与 Reinhard 下的对比条 | `srgb_encode` + 两条曲线 |

十张都是原创绘制（figkit 生成，无第三方素材），不涉及外部版权。封面用 CC BY 4.0，与正文一致。

## 代码与复现

```
cd examples
python3 run_model.py     # 写 results.json，打印 14 条自验
python3 build_figures.py # 只读 results.json，写 10 张 PNG + figure-metadata.json
```

`tone.py` 是唯一的数学实现，约 100 行：`srgb_decode` / `srgb_encode` / `code8` / `clamp01` / `reinhard` / `reinhard_white` / `aces_fit` / `loglog_slope` / `codes_in_range` / `ramp_stats`。`figkit.py` 是画图工具，MIT，与正文无关。

## 没做的事

1. **没有用真实 HDR 图片跑过。** 本稿全部是 1 维（单个像素的亮度）计算，没有读入任何图片、没有做空间处理。所谓「条带」是数出来的，不是在照片上量出来的。
2. **没有实现完整的 ACES RRT + ODT。** 只有那条有理拟合。
3. **没有做局部算子的实验。** Durand–Dorsey 只出现在决策表的一行里，光晕是定性说明。
4. **没有做抖动。** 图 7 是不抖动时的最坏情况。
5. **没有讨论色度。** 只处理亮度一个通道；真实管线在色度上还有一套（色相保持、饱和度补偿），本稿没碰。
6. **没有做观察者实验。** 「看着平」「黑得下去」是描述，不是测量。
7. **没有测性能。** 四条曲线的计算量差异（除一次 vs 除两次）没有测耗时。
8. **没有讨论时间域。** 视频里逐帧独立做色调映射会闪烁，那是另一个问题。
9. **没有画 Drago 2003 的曲线。** 只在来源里记了 DOI。

## AI 辅助范围

材料检索、公式实现、脚本、图与草稿由 AI 在同一次会话里完成；文献的 DOI 与卷期页码经过 Crossref 核对，但**未逐篇读原文**——文中对这几篇的描述只到「提出了什么思路 / 公式出自哪篇」这一层，没有复述它们的实验。ACES 那一节明确写了「没读规范原文、没取到拟合的一手出处」。审读记录见 `review.md`，其中列出了这次没有独立复核的部分。
