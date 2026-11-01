# 来源与许可

## 一、文字参考

1. Wikipedia, *USB hardware*, 小节 “USB Power Delivery”. 存取方式：`https://en.wikipedia.org/wiki/USB_hardware?action=raw`（2026-10 抓取，169 146 字节），PD 小节在原文件第 850–952 行。用于：PD 1.0 / 2.0 / 3.1 的年份与功率上限、2.0 与 3.x 的功率规则表、EPR 的 28 / 36 / 48 V 档位、DFP / UFP / 双角色端口的定义、240 W 线缆的标识要求。
2. USB Implementers Forum, *USB Power Delivery Specification*（Rev 3.1，需注册下载）。本文用到的是它的公开结论（电压档、电流上限、20 mV 步进、报文结构），**没有逐条核对规范原文的措辞**；文中的字段名与位序以 Wikipedia 的表格和公开技术资料为准，模型实现见 `examples/pd.py`。
3. Enos, Nate & Gosselin, Brian, *A Primer on USB Type-C and USB Power Delivery Applications and Requirements*, Texas Instruments, 2022-03, `https://www.ti.com/lit/slyy109`。延伸阅读，用于核对 CC 引脚的恒流源 / Rd 下拉这套识别方式与 e-marker 的角色。
4. IEEE 802.3（100BASE-TX）与 ANSI FDDI 的 4b5b 码表。本文第 9 节的 16 行码表与这两处标准一致，实现写在 `examples/pd.py` 的 `FOURB5B`。

## 二、照片（3 张）

| 图 | 文件 | 作者 | 许可 | 原尺寸 |
| --- | --- | --- | --- | --- |
| 图 1 | `USB_Type-C_plug_20170626_crop.jpg` | Santeri Viinamäki | **CC BY-SA 4.0** | 2217×2193 |
| 图 13 | `USB-C_cable_2017_A.jpg` | Fructibus | **CC0** | 3872×2904 |
| 图 17 | `USB-C_connector_on_a_laptop.jpg` | Logant547 | **CC BY 4.0** | 3060×4080 |

三张都来自 Wikimedia Commons，原图保存在 `originals/`，未做任何裁剪、调色或重压缩。正文与 `assets/` 里的版本只在宽度超过 1062 px 时等比缩小一次（Pillow `LANCZOS`，JPEG 质量 92）。

CC0 那张在法律上不需要署名，本文仍标出作者，是因为照片本身有价值，署名是基本的礼貌。

## 三、15 张示意图的数字来源

每张图的每个数字都来自 `examples/results.json`，没有一个是手写的。

| 图 | 内容 | 数据来源（`results.json` 的键） |
| --- | --- | --- |
| 2 | CC 恒流源与 Rd | `cc.rd_ohm`、`cc.rows[*].ip_ua` |
| 3 | 三档电压与合法区间 | `cc.rows[*].v_cc / margin_lo / margin_hi`、`cc.bands`、`cc.worst_band_change` |
| 4 | 正插 / 反插 | `flip.cases[*].pins / v_cc1 / v_cc2 / low_pin` |
| 5 | BMC 波形 | `bmc.bits`、`bmc.wave`、`bmc.edges_per_bit`、`bmc.ui_samples` |
| 6 | 相位与频率扫描 | `bmc.sweep`、`bmc.fsweep`、`bmc.first_bad`、`bmc.first_freq`、`bmc.limit_ppm`、`bmc.window_ui` |
| 7 | 帧长与编码后位数 | `frame.message.frame_len / bits / ndo`、`frame.fourb5b_bits`、`frame.bmc_samples`、`frame.single_bit_caught` |
| 8 | 游程对比 | `fourb5b.raw_max / raw_mean / c5_max / c5_mean / zero_raw / zero_c5 / ones_c5` |
| 9 | 16 位头 | `frame.message.header`、`frame.message.header_fields` |
| 10 | PDO 字段 | `frame.message.ndo`；20 V / 3.25 A 的编码按 `fixed_pdo()` 手算复核 |
| 11 | 时间线与 Vbus | `trace.events`、`trace.vbus`、`trace.ramp_ms_5_to_20`、`trace.attach_to_ready`、`config.ramp_mv_per_ms` |
| 12 | 功率阶梯 | `rules.rules`、`rules.at_5v_for_100w`、`rules.at_20v_for_100w` |
| 14 | e-marker 降档 | `emarker.cases[0, 2, 5]`、`emarker.lost_100w.fallback_w` |
| 15 | 线损 | `loss.rows`、`loss.r_cable` |
| 16 | PPS 台阶与线阻补偿 | `pps.rows`、`pps.v_steps`、`pps.i_step_ma`、`pps.max_err_mv`、`pps.drop` |
| 18 | 五句话 | 全文结论，无新数字 |

## 四、模型的设定与简化

`examples/pd.py` 是一个纯算术模型，不连接任何真实端口、不驱动任何硬件。明确设定：

- **CC 识别**：Rd = 5100 Ω 名义值，恒流源 80 / 180 / 330 µA；区间边界取 0.15–0.61 / 0.61–1.16 / 1.16–2.45 V。开路判定为「保持 3.3 V」。
- **BMC**：一个比特 64 个采样点；接收端在每格的 1/4 与 3/4 处采样；比较两次采样电平是否相同。**没有做重同步**，所以频率扫描的曲线在 63 个错处饱和（见第 7 节正文）。
- **4b5b**：使用 100BASE-TX / FDDI 的 16 个数据码，每个 4 位换成 5 位；nibble 顺序为低 4 位在前。
- **帧**：2 字节头 + 4 个固定电压 PDO + 4 字节 CRC；CRC 为标准反射 CRC-32（多项式 `0x04C11DB7`，反射写法 `0xEDB88320`），初值与末取反都与公开实现一致，并已用 `123456789 → 0xCBF43926` 自查。
- **时序**：去抖 150 ms，每条报文 6 ms（一问一答），VBUS 斜坡 100 mV/ms。斜坡速率是模型选择，不是规范数值；真实充电器的斜坡各不相同。
- **功率规则表**：按「≤ X W 就用 V 伏」的分档写成查表，属于对公开规则的整理，**不是规范原文的转述**。`picks` 里「选满足条件的最低电压档」也是模型的选档策略。
- **PPS**：3.3–21.0 V，20 mV 一步（886 个台阶），电流 50 mA 一步（101 档），误差按四舍五入到最近的台阶计算。
- **e-marker**：只建模三档上限（无 / 5 A / EPR），不建模它的发现流程与 VCONN 供电细节。
- **线损**：线缆按 0.1 Ω 的回路电阻计，损耗 = I²R。

## 五、明确没有做的事

1. **没有实测任何真实设备。** 没有用示波器看过 CC 波形，没有抓到过真实 PD 报文，所有曲线都来自模型。
2. **没有读规范原文。** 字段名、位序、功率档位取自公开资料；规范措辞与边界条件（例如 PPS 的 APDO 字段细节、EPR 的三段式进入流程）本文没有逐条实现。
3. **没有建模 USB 2.0 / 3.x 的数据通道。** 方向切换、alt mode、DisplayPort 隧道都只在第 18 节用一句话提到。
4. **没有建模安全与故障路径。** 过流、过温、短路、VCONN 短路、CC 抖动重试都不在模型里。
5. **没有做参数扫描。** 电阻容差只取 ±10% 两个端点，没有扫全区间；PPS 台阶只取了 6 个目标电压。
6. **没有目视检查生成的图。** 每一张图都在 `figkit` 的几何闸门下生成（不出画布、不重叠、字号不低于 38 px、单元格不出安全带），但“好不好看”没有人工看过。
