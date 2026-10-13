# 资料、复算与配图说明

## 本文范围

本篇解释双门槛的状态记忆、反相与非反相的区别、理想比较器正反馈如何改变参考电压，以及不能自动拒绝全摆幅弹跳或短脉冲的边界。没有实际接线、采集温度、运行芯片、观察示波器或测量风扇。所有程序显示和波形中的输入均为声明的测试数据或数学模型；硬件照片来自官方文档，不是本文亲拍。

## 一手来源与支持范围

1. Otto H. Schmitt, *A thermionic trigger*, Journal of Scientific Instruments 15 (1938), pp.24–26, DOI 10.1088/0950-7671/15/1/305。[原论文扫描件，由UC Berkeley教授Kris Pister页面提供](https://people.eecs.berkeley.edu/~pister/publications/FamousPapers/Schmitt1937.pdf)。PDF共4页，首张是检索封面，论文从PDF第2页下半部开始；印刷第24页上半部尚为前一篇文章。明确区分正文收稿1937-11-26与1938发表，不因文件名认定1937发表。作者完整名Otto H. Schmitt，不使用同名其他人物照片。原论文谈电子管触发、两转换条件及温控/照明应用；未声称软件规则是原电路逐器件模拟，未主张作者发明全部滞回现象。扫描件和原论文插图不随本文再分发。

2. Texas Instruments, [Understanding Schmitt Triggers, SCEA046B, Revised April 2025](https://www.ti.com/lit/ab/scea046b/scea046b.pdf)。共4页。用于上下转换门槛、滞回宽度、缓慢输入及应用边界。本文未复制TI原图或原表，未把该说明中的泛例规格表当成SN74HC14具体规格。TI资源保留其版权及使用条件。

3. Texas Instruments, [SN54HC14 / SN74HC14 Hex Schmitt-Trigger Inverters, SCLS085L, Revised February 2025](https://www.ti.com/lit/ds/symlink/sn74hc14.pdf)，[官方产品入口](https://www.ti.com/product/SN74HC14)。本文采用SN74HC14，非SN54。§5.5 Electrical Characteristics – 74在PDF/印刷第5页：VCC=4.5V、TA=25℃，VT+最小/典型/最大1.55/2.5/3.13V，VT−为0.9/1.6/2.45V，ΔVT为0.4/0.9/2.1V。数值用于图20的原创范围图，不称实测；不能跨器件独立取极值相减来替代宽度规格。六路独立反相通道来自器件功能说明。未用此器件参数描述RP2040。

4. Raspberry Pi, 官方 `pico-sdk` 固定提交 `079c6f39023649b154152db30f1d781e884879bc`：[GPIO接口头文件](https://github.com/raspberrypi/pico-sdk/blob/079c6f39023649b154152db30f1d781e884879bc/src/rp2_common/hardware_gpio/include/hardware/gpio.h)中 `gpio_set_input_hysteresis_enabled` 的注释明确输入滞回（Schmitt trigger）可启用或关闭；[RP2040寄存器头文件](https://github.com/raspberrypi/pico-sdk/blob/079c6f39023649b154152db30f1d781e884879bc/src/rp2040/hardware_regs/include/hardware/regs/pads_bank0.h)的 `PADS_BANK0_GPIO0_SCHMITT` 字段支持对应控制。两份固定源码均已实际读取，支持第13—14节关于输入接口功能的陈述；没有从照片推断内部结构，也没有把本文理想2/3V门槛移植到该芯片。[官方芯片介绍](https://www.raspberrypi.com/documentation/microcontrollers/microcontroller-chips.html)说明RP2040用于Pico等开发板。另提供[RP2040数据表](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)供进一步阅读；本轮独评未复核该PDF，不以其具体页码或章节作为已核证据。

5. [Raspberry Pi官方文档固定提交208ec7debc5b30b3ce6a1426eff453f2359f2165](https://github.com/raspberrypi/documentation/tree/208ec7debc5b30b3ce6a1426eff453f2359f2165)：两幅原始硬件照片及许可身份来源。逐文件链接、Git blob SHA与本地SHA-256见下节。这里引用的是正式文档中的实物照片，不是重新生成的产品想象图。

## 两张第三方照片的独立权利

- 摄影作品权利主体/署名：Raspberry Pi Ltd；来源：Raspberry Pi documentation。
- 许可：[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)。仓库LICENSE.md首行简称漏写ShareAlike，但链接与随后的完整条款均为Attribution-ShareAlike 4.0，本文按完整条款标识，不改称CC BY 4.0。
- 公开保存[完整许可](originals/Raspberry-Pi-Documentation-LICENSE.md)，保留全部条款；图15与图16未裁剪、未加字、未改变像素。网页等比显示不改变源图文件。
- 另保留[原始照片身份清单](originals/photo-manifest.json)。正文其他原创图没有拿照片作训练、拼合或伪造实物。
- 官方标识留在原照中仅为对象识别，不暗示Raspberry Pi背书本文。公开的第三方照片仍受其各自许可约束，文章整体正文许可不覆盖改授这两图。

### originals/pico-original.png

[固定来源](https://github.com/raspberrypi/documentation/blob/208ec7debc5b30b3ce6a1426eff453f2359f2165/documentation/asciidoc/computers/raspberry-pi/images/pico.png)；Git blob `d36e87d79899fc1c3a91828ac765958a01d0a548`；SHA-256 `cbd8f9e22c3a45123f2d916ea996e99beb236dcaaaca0430cd2575a91bdf5a33`；562252字节。

### originals/rp2040-original.jpg

[固定来源](https://github.com/raspberrypi/documentation/blob/208ec7debc5b30b3ce6a1426eff453f2359f2165/documentation/asciidoc/microcontrollers/microcontroller-chips/images/rp2040.jpg)；Git blob `3ec60937b5091a321bc885f60c042154ad70249b`；SHA-256 `583a6ce6f12236788d3f953d0005244ab97f4459d8e8f40bd25025a2c113a4a1`；35906字节。

## 原创计算口径与复现

[核心程序](examples/schmitt_lab.py)、[原始601样本CSV](examples/trace.csv)、[运行结果JSON](examples/results.json)、[完整运行说明](examples/README.md)。核心只用Python标准库；原创显示另使用Pillow 12.3.0与Noto Sans CJK。没有把作者自检称为独立审读或平台验收。

- 9样本单阈值序列0,0,1,0,1,0,0,0,0；双阈值0,0,1,1,1,1,1,1,0。初始0，切换分别4、2次。
- 12秒601样本，单阈值切换26次，双阈值2次。每项数值可在CSV逐行核对；浮点sin生成小幅波动，边界按大于等于/小于等于处理。该计数仅属于这条测试输入。
- 558组离散边界/初态检查、5000组固定种子20261013带内记忆检查，另验证无穷大、NaN及非法门槛被拒绝。不是对任意真实控制系统的安全证明。
- 反相示例用非反相状态的1−state表示逻辑高低；图18上门槛2.5V、下门槛1.6V是为看清方向而固定的理想值，不带器件公差、传播延迟或输出电流模型。
- 理想正反馈节点假定比较器输入电流为0、参考源2.5V、两个电阻10kΩ/40kΩ，输出恰为0V或5V。所有电压相对于同一参考地。电流平衡给V=2+0.2O，故上下门槛3V/2V。它不是74HC14内部电路，也不是器件接线指南。
- 图27为精确一阶指数模型的采样：t<0.05秒时0，之后3.3(1−exp(−(t−0.05)/0.05))。301点，步长0.001秒。时间常数0.05秒，经过一个时间常数完成约63.212%的变化。
- 游戏提示测试距离8、4.9、5.1、4.8、6、7.1，进入≤5、退出≥7、初始隐藏，得到0,1,1,1,1,0。场景像素仅用于显示测试输入，非商业游戏或实际距离测量。
- 图10、11、18的横轴为从0计的离散样本序号。阶梯线表示保持前一样本的显示约定，不是连续时间硬件波形复原。

## 全图的新增解释作用

32张正文图片、另有封面；没有用图像数量代替教学职责。原始程序帧不另计作正文图片；下列照片与教学图身份分开。

- [assets/01-software-fan-frames.png](assets/01-software-fan-frames.png)：同一组数值喂给两种规则的实际程序显示，先看见闪烁与保持。原创教学图/计算显示，CC BY 4.0。
- [assets/02-trace-comparison.png](assets/02-trace-comparison.png)：实际601样本计算的输入与两种状态轨迹，不当传感器测量。原创教学图/计算显示，CC BY 4.0。
- [assets/03-single-threshold.png](assets/03-single-threshold.png)：逐样本读出单阈值为何抖动，解释大于等于边界。原创教学图/计算显示，CC BY 4.0。
- [assets/04-two-levels.png](assets/04-two-levels.png)：把启动和关闭条件分开，带内保持不是第三种输出。原创教学图/计算显示，CC BY 4.0。
- [assets/05-hand-walk.png](assets/05-hand-walk.png)：完整9样本状态账本支持逐步手算与边界检查。原创教学图/计算显示，CC BY 4.0。
- [assets/06-state-machine.png](assets/06-state-machine.png)：两状态与两个相反方向转换，明确记忆的最小存储。原创教学图/计算显示，CC BY 4.0。
- [assets/07-same-input-memory.png](assets/07-same-input-memory.png)：相同输入不同路径产生不同输出，避免单值函数误解。原创教学图/计算显示，CC BY 4.0。
- [assets/08-hysteresis-loop.png](assets/08-hysteresis-loop.png)：用双方向箭头读滞回回线，区别输入轴与时间轴。原创教学图/计算显示，CC BY 4.0。
- [assets/09-noise-stays-inside.png](assets/09-noise-stays-inside.png)：波形仍有噪声但状态可不切换，避免把滞回当滤波。原创教学图/计算显示，CC BY 4.0。
- [assets/10-full-swing-bounce.png](assets/10-full-swing-bounce.png)：反例证明两阈值本身不保证消除满摆幅机械弹跳。原创教学图/计算显示，CC BY 4.0。
- [assets/11-short-pulse.png](assets/11-short-pulse.png)：明确滞回不是按持续时间拒绝脉冲的机制。原创教学图/计算显示，CC BY 4.0。
- [assets/12-window-versus-history.png](assets/12-window-versus-history.png)：用同输入区分窗口比较器的无记忆判断与滞回。原创教学图/计算显示，CC BY 4.0。
- [assets/13-amplitude-versus-time.png](assets/13-amplitude-versus-time.png)：区分幅度记忆和时间稳定性要求及可组合性。原创教学图/计算显示，CC BY 4.0。
- [assets/14-startup.png](assets/14-startup.png)：避免把带内状态记忆误解为上电自动拥有确定历史。原创教学图/计算显示，CC BY 4.0。
- [assets/15-pico-photo.png](assets/15-pico-photo.png)：官方Pico板实际照片：白色按键、中央RP2040与两侧焊盘给输入电路物件参照。第三方照片，权利见上。
- [assets/16-rp2040-photo.jpg](assets/16-rp2040-photo.jpg)：官方RP2040封装正反面实照，将数字输入滞回落实到真实集成芯片。第三方照片，权利见上。
- [assets/17-pad-location.png](assets/17-pad-location.png)：根据官方RP2040文档独立概括施密特输入所在位置。原创教学图/计算显示，CC BY 4.0。
- [assets/18-inverting-response.png](assets/18-inverting-response.png)：把非反相软件开关与74HC14反相输出明确拆开。原创教学图/计算显示，CC BY 4.0。
- [assets/19-six-independent-gates.png](assets/19-six-independent-gates.png)：六路反相器不是六级串联，不把功能图当接线图。原创教学图/计算显示，CC BY 4.0。
- [assets/20-threshold-spec-ranges.png](assets/20-threshold-spec-ranges.png)：从TI真实规格重绘范围和典型值，不误配跨器件极值。原创教学图/计算显示，CC BY 4.0。
- [assets/21-ideal-comparator.png](assets/21-ideal-comparator.png)：用加减端电压比较建立正反馈推导的必要基础。原创教学图/计算显示，CC BY 4.0。
- [assets/22-resistance-weight.png](assets/22-resistance-weight.png)：先解释两电阻支路与电流约束，再引出加权电压。原创教学图/计算显示，CC BY 4.0。
- [assets/23-divider-equation.png](assets/23-divider-equation.png)：从节点电流相加为零到加权参考，明确符号和单位。原创教学图/计算显示，CC BY 4.0。
- [assets/24-output-moves-reference.png](assets/24-output-moves-reference.png)：具体算出输出高低造成3V/2V两个门槛。原创教学图/计算显示，CC BY 4.0。
- [assets/25-positive-feedback-rise.png](assets/25-positive-feedback-rise.png)：把再生翻转拆成四个因果步骤，而非给正反馈贴标签。原创教学图/计算显示，CC BY 4.0。
- [assets/26-inverting-loop.png](assets/26-inverting-loop.png)：连接数值推导与反相滞回曲线，区分前面的非反相例。原创教学图/计算显示，CC BY 4.0。
- [assets/27-filter-before-switch.png](assets/27-filter-before-switch.png)：实际指数模型显示滤波改变输入，和滞回的状态改变分工不同。原创教学图/计算显示，CC BY 4.0。
- [assets/28-history-dates.png](assets/28-history-dates.png)：分开发明人物原论文收稿与发表，避免用文件名替代史实。原创教学图/计算显示，CC BY 4.0。
- [assets/29-game-prompt.png](assets/29-game-prompt.png)：实际双阈值距离状态驱动的原创游戏提示，迁移到游戏开发。原创教学图/计算显示，CC BY 4.0。
- [assets/30-three-questions.png](assets/30-three-questions.png)：以状态、边界和限制归纳主线而不是重复术语。原创教学图/计算显示，CC BY 4.0。
- [assets/31-feedback-circuit.png](assets/31-feedback-circuit.png)：完整两电阻正反馈拓扑，把输出参考和比较器输入的真实连接关系画明白。原创教学图/计算显示，CC BY 4.0。
- [assets/32-wider-band-tradeoff.png](assets/32-wider-band-tradeoff.png)：比较同一上门槛不同下门槛，展示稳定与退出时机的代价而不偷换成固定延时。原创教学图/计算显示，CC BY 4.0。

封面为原创两门槛概念图，CC BY 4.0。表格/公式式图用于逐步解释，真实照片负责硬件对象，程序显示与数值曲线负责可观察结果；不把示意图称为仪器测量。

## 误解边界

- 两阈值不是两个输出之外的第三种“半开”；带内保存原状态。
- 滞回不是窗口判断，不是滤波，也不是固定时长的去抖。可以组合，但职责不同。
- 小于滞回宽度的有限输入范围无法同时覆盖两门槛，因此不能反复切换；仍可能有第一次切换。
- 短脉冲越上门槛可能保留状态；跨两门槛的全摆幅弹跳仍可反复切换。
- 正反馈模型没有承诺任何具体芯片的阈值或启动状态；现实应用仍需查电源、输入范围、公差、速度和负载。
- 没有提供高压电子管、市电或实际风扇功率线路实验，未运行实体电路。
