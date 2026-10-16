# Atari 2600 显示模型：可复算材料

正文：[read.md](read.md)。来源与许可：[sources.md](sources.md)。

这是一套教学模型：一颗按真实机器周期计数的 6507 解释器、一颗按真实行时序工作的 TIA 显示模型、一个迷你汇编器，以及几段真实的 kernel 程序。它**不是模拟器**——不能运行任何真实游戏 ROM，也不支持音频、手柄、bank switching 或 PAL/SECAM。

它存在的目的是让正文里每一个周期数、每一个像素位置、每一幅画面都能被重新跑出来。

## 运行

环境记录见 [run-environment.json](examples/run-environment.json)。模型只用 Python 标准库；绘图另需 Pillow 与一款中文字体。

在本篇目录中执行：

```sh
python examples/run_model.py        # 跑四组实验，写 results.json 与 frame-*.png
python examples/build_figures.py    # 重绘全部正文图与封面
```

首次运行时的原始标准输出保存在 `originals/model-stdout.txt`。

绘图程序会按以下顺序寻找中文字体：

```text
/System/Library/Fonts/Hiragino Sans GB.ttc               （macOS）
/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc   （Linux）
/Library/Fonts/Arial Unicode.ttf
/System/Library/Fonts/STHeiti Medium.ttc
```

找不到任何一款时程序直接报错，不会退回默认字体。

## 模型怎么工作

一行是 228 个色时钟，其中 160 个可见。一个机器周期是 3 个色时钟，所以一行有 76 个机器周期。

`frame.py` 逐行运行 CPU：跑满 76 个周期，或者直到 CPU 因写 WSYNC 而被挂起。每一行的寄存器写入都被记录下**它在第几个色时钟发生**。可见行在渲染时按光束位置**逐像素重放**这些写入，所以写得晚的寄存器只影响它之后的那段画面——这正是第 7 节能看到画面坏掉的原因。消隐行只提交寄存器状态，不渲染。

`tia.py` 里的位置与图形模型：

- playfield：20 位，每位 4 个色时钟，按 CTRLPF 镜像或复制成 40 位（160 个色时钟）。
- 玩家：8 像素移位寄存器，按 NUSIZ 复制 1—3 份或放大 2/4 倍，可按 REFP 水平翻转。
- 导弹与球：宽度 1/2/4/8 个色时钟。
- RESPx：写入那一刻，物体的水平位置从头开始算。写入发生在第 k 个机器周期时，物体出现在第 3k + 5 个色时钟。
- HMPx 与 HMOVE：HMOVE 把各物体的微调量（−8 到 +7）加到当前位置上。
- 碰撞：15 个触发器，按文档的位定义在逐像素扫描中置位。

### 模型明确不是的东西

- **不是周期精确的。** RESPx 写入到物体出现之间的 5 个色时钟输出延迟，是**本模型选定的常数**，不是核对到的硬件值。真实芯片的偏移取决于写入落在周期内的哪个相位。
- **不模拟** HMOVE 的梳齿伪影、VDEL 垂直延迟、RSYNC、音频、TIA 的模拟信号输出。
- **不模拟** 真实主机的时钟抖动、NTSC 与 PAL 的差异、以及不同电视机的容忍度。
- 渲染出的画面是**模型输出**，不是真实主机截图，也不是任何真实游戏的画面。

## 四组实验

1. **位置标定**：延时循环的圈数与精灵像素位置的对应关系。每多一圈右移 15 个像素。
2. **渲染一帧**：样例 kernel 跑满 192 行，输出 `frame-pong.png`；换一组数据输出 `frame-pong-moved.png`。
3. **时序超支**：在每行开头插入 16 条 NOP（32 个机器周期），记录有多少行与正常版本不同、哪些寄存器写在了光束之后。
4. **闪烁与碰撞**：两帧各画两个物体、合成出四个；以及让球与挡板重叠后读取碰撞寄存器。

样例 kernel 的一行开销由模型逐条指令统计：`STA WSYNC` 3 周期 + 6 组 `LDA abs,X`/`STA zp` 共 42 周期 + `INX` 2 + `CPX` 2 + `BNE` 3 = **52 个周期**，一行预算 76 个，余量 24 个。

## 文件

- [tia.py](examples/tia.py)：TIA 显示与碰撞模型。
- [cpu6507.py](examples/cpu6507.py)：6507 解释器，只实现样例用到的操作码，但周期数按文档记录。
- [asm.py](examples/asm.py)：迷你汇编器。
- [kernel.py](examples/kernel.py)：样例 kernel、位置标定、整帧运行。
- [frame.py](examples/frame.py)：逐行驱动与事件记录。
- [run_model.py](examples/run_model.py)：四组实验，输出 `results.json` 与帧 PNG。
- [figkit.py](examples/figkit.py)：绘图工具。每张图在保存前会检查文字是否出画布、是否越出所声明的框、是否互相重叠、字号是否低于下限、文字与背景的对比度是否够读。
- [build_figures.py](examples/build_figures.py)：全部正文图与封面。

## 限制

模型无法运行真实游戏，因此**不能**用来复现任何真实游戏的画面、周期数或技巧细节。正文里关于真实游戏的描述（《太空侵略者》逐行换图形、《Pitfall!》的 8 位计数器、《Adventure》的彩蛋）来自公开资料，不是本模型的运行结果，正文与来源说明中已分别标注。

## 许可

原创文字、原创图、封面与原创实验数据：CC BY 4.0。原创代码：MIT，完整文本见 [LICENSE-CODE.txt](LICENSE-CODE.txt)。第三方照片保留各自权利，许可与处理说明见 [sources.md](sources.md)。
