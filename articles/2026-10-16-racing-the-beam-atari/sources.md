# 来源、图像身份与 AI 辅助说明

核查日期：2026-10-16。正文为面向学生的原创机制讲解。文中的主机、芯片、人物、公司与年份以公开一手来源核对；全部时序数字、周期账、像素位置、碰撞结果与渲染画面来自本文作者实际运行本仓库的模型。

## 一手来源及支持范围

1. Steve Wright，*Stella Programmer's Guide*，1979 年 12 月 3 日。这是 Atari 内部流出的 TIA 编程指南，本文时序部分的主要依据。核对内容：一帧 262 行、每行 228 个色时钟（3.58 MHz）、每 3 个色时钟 1 个机器周期（228 ÷ 3 = 76）、典型的 3 行垂直同步 + 37 行垂直消隐 + 192 行画面 + 30 行溢出、每行 68 个色时钟水平消隐 + 160 个色时钟画面、非画面行共提供 5,320 个机器周期、RESPx 与"水平定位只能落在 15 个色时钟间隔上、移动寄存器填补 +7 到 −8"、HMOVE 必须紧跟 WSYNC、NUSIZ 的复制与尺寸、playfield 20 位与镜像/复制、碰撞寄存器的位定义。本文的模型按这份文档的时序实现。
2. TIA 的无帧缓冲设计、五种活动物体（2 玩家 + 2 导弹 + 1 球 + 场地）、每行从寄存器重新生成、碰撞用 15 个触发器、RDY 引脚用于 WSYNC 同步、以及"垂直同步由 CPU 程序触发、TIA 没有行计数器"，用于正文第 1—4 节与第 9 节。出处为 [Television Interface Adaptor 条目](https://en.wikipedia.org/wiki/Television_Interface_Adaptor)及其所列原始资料。
3. Atari 2600 的硬件规格（6507 @ 1.19 MHz、128 字节 RAM、卡带 4 KB、bank switching 扩展到 64 KB、160 × 192 NTSC 最大分辨率、40 × 192 场地分辨率、128 色），出处为 [Atari 2600 hardware 条目](https://en.wikipedia.org/wiki/Atari_2600_hardware)。本文没有实测真实主机的分辨率和颜色数，这些是规格值。
4. MOS 6507 与 6502 的关系（28 引脚 DIP、地址线 13 根、去掉中断引脚、与 6502 共用硅片层只差金属化层），出处为 [MOS Technology 6507 条目](https://en.wikipedia.org/wiki/MOS_Technology_6507)。
5. Jay Miner 设计 TIA、因内存昂贵而放弃帧缓冲、后续设计 ANTIC/CTIA 与 Amiga 定制芯片组、以及他的生卒年（1932—1994），出处为 [Jay Miner 条目](https://en.wikipedia.org/wiki/Jay_Miner)与 TIA 条目。
6. Atari 2600 的上市时间（1977 年 9 月前后，首发九款游戏、2 KB 卡带）、Cyan Engineering 与 MOS 的 6502/6507/RIOT 方案、Bushnell 关于专用机器开发成本与三个月货架寿命的表述、1976 年出售给 Warner、《太空侵略者》家用版（1980）成为爆款、《Adventure》（1980）与其彩蛋、1982 年《Pitfall!》与 Activision 的成立，出处为 [Atari 2600 条目](https://en.wikipedia.org/wiki/Atari_2600)、[Atari, Inc. 条目](https://en.wikipedia.org/wiki/Atari,_Inc.)、[David Crane 条目](https://en.wikipedia.org/wiki/David_Crane_(programmer))、[Warren Robinett 条目](https://en.wikipedia.org/wiki/Warren_Robinett)、[Pitfall! 条目](https://en.wikipedia.org/wiki/Pitfall!)、[Nolan Bushnell 条目](https://en.wikipedia.org/wiki/Nolan_Bushnell)。
7. 《Pitfall!》的 255 个场景由代码生成、而不是逐个存储；生成依据是一个可正可反的计数器，其 8 位用于决定背景等细节。出处为 [Pitfall! 条目](https://en.wikipedia.org/wiki/Pitfall!)的"Development"一节。**正文与图 18 只描述到"8 位计数器按固定规则生成 255 个场景"这一层**，没有断言具体的位序、反馈多项式或宝物分布算法，因为本文没有核对到原始代码。
8. Crane 关于"设计 10 分钟、编程约 1000 小时、大部分时间用于压缩代码塞进 4 KB"的表述，以及 Activision 四人 1979 年离开 Atari 的经过与 Kassar 的回应，出自 David Crane 条目与 Pitfall! 条目所引的访谈与报道。正文如实保留这是当事人回忆。
9. 《太空侵略者》家用版迫使开发者"逐行改玩家图形"以画出更多外星人，出处为 TIA 条目的"Drawing the display"一节。

## 本文实际运行的模型

`examples/run_model.py` 只依赖 Python 标准库；绘图另需 Pillow。环境记录见 `examples/run-environment.json`。

模型包含三部分：

- **6507 解释器**（`cpu6507.py`）：只实现样例 kernel 用到的操作码，但每一条都按文档记录的机器周期计数。WSYNC 通过挂起 CPU 到行末实现。
- **TIA 显示模型**（`tia.py`）：228 个色时钟一行、160 个可见像素、playfield 的 20 位串行输出与镜像/复制、玩家/导弹/球的宽度与复制、RESPx 定位、HMPx 与 HMOVE、15 个碰撞触发器。图形与颜色寄存器按光束位置**逐像素重放**，所以写晚了的寄存器会从它被写入的那个像素起才生效——这是第 7 节能看到画面的原因。
- **迷你汇编器**（`asm.py`）与**样例 kernel**（`kernel.py`）。

### 模型明确不是的东西

- 它**不是模拟器**，不能运行任何真实的 2600 游戏 ROM，也不支持 bank switching、音频、手柄、PAL/SECAM 时序。
- 它**不是周期精确的**。RESPx 的写入到物体出现之间，模型使用固定的 5 个色时钟输出延迟。真实芯片的这个偏移取决于写入落在周期内的哪个相位；本文没有核对到确切值，因此把它作为**本模型选定的常数**明确写进代码与 README，而不是当成硬件事实。
- 它**不模拟** HMOVE 的"梳齿"伪影、VDEL 垂直延迟、RSYNC、音频、以及 TIA 的模拟信号输出。
- 图 10—13、封面里的画面是**本模型的渲染输出，不是真实主机截图**。真实游戏的画面属于各自权利人，本文没有复制任何游戏截图。
- 正文所有"机器周期"数字来自模型对样例 kernel 的逐条指令统计，可以复算；但它描述的是**本文写的这段 kernel**，不是任何真实游戏的 kernel。

## 原件图片盘点与使用边界

本文正文没有复制任何游戏画面、卡带封面艺术或厂商宣传图。所有游戏相关内容都以文字描述并链接到公开页面。

正文使用 9 张第三方真实照片，全部来自 Wikimedia Commons：

| 文件 | 内容 | 作者 | 许可 |
|---|---|---|---|
| originals/photos/real-01-console.jpg | Atari 2600 四开关版与摇杆 | Evan-Amos | 公有领域 |
| originals/photos/real-02-joystick.jpg | CX40 摇杆 | Rama | CC BY-SA 2.0 fr |
| originals/photos/real-03-pitfall-cart.jpg | Pitfall! 卡带 | JoRgE-1987 | CC BY-SA 4.0 |
| originals/photos/real-04-motherboard.jpg | Atari 2600 主板（1982 年四开关版） | Tetrodotoxine | CC BY-SA 4.0 |
| originals/photos/real-05-6502.jpg | MOS MPS 6502 芯片 | ZyMOS | CC BY-SA 4.0 |
| originals/photos/real-06-scanline.jpg | 电视扫描线高速合成照片 | Tristantech | CC BY-SA 3.0 |
| originals/photos/real-07-videosignal.jpg | PAL 视频信号的扫描行波形 | Shaddack | CC BY-SA 4.0 |
| originals/photos/real-08-jay-miner.jpg | Jay Miner，1990 年 | Michael C. Battilana / Cloanto IT srl | CC BY 2.0 |
| originals/photos/real-09-bushnell.jpg | Nolan Bushnell，2013 年 | Tech Cocktail | CC BY-SA 2.0 |
| originals/photos/real-10-crane.jpg | David Crane，2011 年 | Joe Grand | CC BY-SA 2.0 |
| originals/photos/real-11-robinett.jpg | Warren Robinett，2015 年 | Official GDC | CC BY 2.0 |

处理说明：

- David Crane 原图为 3000 × 4000、5,739,357 字节，超过公众号每图 5,000,000 字节的限制。发布用副本按 LANCZOS 缩放到 1200 × 1600（230,075 字节），完整画面保留，未裁切、未生成内容；未修改的原件另存于私有工程。
- Atari 2600 主机原图 3,940 × 2,300、2,514,681 字节，主板原图 3,933 × 2,285、3,005,261 字节，均在限制内，未做压缩。
- Warren Robinett 照片原文件只有 332 × 442 像素，这是该文件的原始尺寸，本文未放大后称其为高清。
- 全部照片只做等比缩放与居中裁切以适配版面，没有改动人物、设备或背景，也没有添加内容。人物肖像的拍摄年代各不相同（Miner 1990 年、Crane 2011 年、Robinett 2015 年、Bushnell 2013 年），图注均写明拍摄场合，未暗示它们来自所讲述的历史现场。
- 未使用任何生成模型制造的人像、主机照片、卡带照片或伪历史截图。

**第三方 CC BY-SA 素材范围**：本组照片中主板、6502、Pitfall! 卡带、扫描线照片、摇杆、Bushnell、Crane 采用 CC BY-SA 许可（版本见上表）。相应图片保留各自注明版本的 CC BY-SA 许可；如对这些图作改编，须按该许可要求分享，保留作者、来源、许可链接及修改说明。本文对它们的处理是等比缩放与居中裁切。文章集合不据此把其他独立作品统一改为 CC BY-SA。

## 原创视觉及证据身份

- 图 03、04、05、06、07、08、09、21 与封面：原创机制示意与时间账，数字来自本模型的实际统计。
- 图 10、11、12、13、14：**本模型实际运行样例 kernel 得到的渲染输出**，不是真实主机截图，也不是任何真实游戏的画面。图 12 的 87 行差异、图 13 的 16/16/32 行计数、图 14 的碰撞位，都是 `examples/results.json` 里的实测值。
- 图 15、16、17、18、19、20：第三方真实照片与原创文字说明的合成图；合成只做版面排布，没有改动照片内容。
- 图 01、02：第三方真实照片，未叠加任何图形或文字说明。
- cover.png：本文独立设计的封面，不计入正文图；其中的画面是本模型的渲染输出。

详细尺寸、最小字号与身份见 [figure-metadata.json](examples/figure-metadata.json)。全部原创图由可复现的 Python/Pillow 程序绘制，字号下限 40 设计像素（1062 像素宽画布，按 354 像素显示宽度折算约 13.3 像素）。

## AI 辅助的真实范围

本文由 Anthropic 的 Claude 在用户授权的技术科普文章任务中辅助研究、构思、撰写中文、编写并执行显示模型、制作程序图、核查数值并修订。时序数字与硬件规格以《Stella 程序员指南》和公开条目核对；模型本身的实际输出保存在 `examples/results.json` 与 `originals/model-stdout.txt`。AI 生成的文字、代码与图本身不作为外部事实证据；模型的选择与限制（尤其是 RESPx 输出延迟这个自定常数）已在正文、README 与本文件中明确标注。本文没有假装作者用过真实主机、写过真实卡带或接触过任何当事人。

原创正文、原创图、封面与原创实验数据采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名可注明本篇题名及文章发布者；原创代码采用 [MIT](LICENSE-CODE.txt)。第三方照片的权利保留于各自权利人，不包含在上述授权中。
