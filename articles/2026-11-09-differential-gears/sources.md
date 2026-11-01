# 来源

## 事实

**差速器的结构与运动学**
- <https://en.wikipedia.org/wiki/Differential_(mechanical_device)>（二手）
- 用于：第二节的零件名称（环形齿轮 / 行星架 / 行星轮 / 半轴齿轮）、"行星架转速是两个半轴转速的平均"这一关系、以及第四节"转速比只与几何有关"的表述。

**限滑差速器与扭矩偏置**
- <https://en.wikipedia.org/wiki/Limited-slip_differential>（二手）
- 用于：第八节的偏置比（bias ratio）定义、摩擦片式与 Torsen 式的区别。

**Torsen 与 Gleasman**
- <https://en.wikipedia.org/wiki/Torsen>（二手）
- 用于：时间线里"1958 年 Gleasman 发明 Torsen"与"零扭矩一侧无法分配扭矩"的说法。原始专利（US 2,859,641 等）本次未读。

**1827 年 Pecqueur 的专利**
- <https://en.wikipedia.org/wiki/On%C3%A9siphore_Pecqueur>（二手）
- 用于：时间线第一条。法国专利的原文没有找到电子版，本文只写"为蒸汽马车申请了差速器专利"，没有引用专利号。

**James Starley 的 1877 年三轮车差速器**
- <https://en.wikipedia.org/wiki/James_Starley>（二手）；图注依据是 Commons 上那张 1889 年书页的说明
- 用于：第七节。Starley 的具体专利号本次未核对。

**1911 年英军教程**
- 图片本身：<https://commons.wikimedia.org/wiki/File:Differential_gear_of_a_motor_car_rear_axle_(Army_Service_Corps_Training,_Mechanical_Transport,_1911).jpg>（公有领域，HMSO 1911 年出版物扫描）
- 用于：第七节那张剖面图。上传者 Andy Dingley 是扫描者，不是原作者。

**μ 与滚阻的量级**
- 干沥青 ≈ 0.9、湿滑 ≈ 0.35、冰面 ≈ 0.1 是工程手册里的常见量级，本文按这些数量级取值，**不是**任何一次实测。型号、胎压、温度都会让实际值偏离。

## 模型里哪些是设定值

- 轮距 1.55 m、轮径 0.65 m、整车 1400 kg、传动轴扭矩 2730 Nm：都是"常见紧凑型后驱车"的量级，用来把公式跑出一组自洽的数字，不对应某一款车。
- 转弯几何用同心圆近似（内外轮绕同一圆心），真实汽车是阿克曼几何，内外前轮转角不同。
- 没有轮胎侧偏模型：实际转弯时轮胎有滑移角，横摆与轮速都比这里复杂。
- 拖行距离那几行（`09-welded.png`）算的是几何上的强制位移，不是轮胎磨损量。真实磨损还取决于载荷、温度和胎面配方。

## 图片

三张照片全部来自 Wikimedia Commons，许可与作者按下表独立保留；正文的 CC BY 4.0 **不覆盖**这三张照片。

| 文件 | 原文件 | 作者 / 机构 | 许可 |
| --- | --- | --- | --- |
| `assets/02-cutaway.jpg` | [File:Differentialgetriebe2.jpg](https://commons.wikimedia.org/wiki/File:Differentialgetriebe2.jpg) | DrJunge（own work） | CC BY-SA 3.0 |
| `assets/10-manual-1911.jpg` | [File:Differential gear of a motor car rear axle (Army Service Corps Training, Mechanical Transport, 1911).jpg](https://commons.wikimedia.org/wiki/File:Differential_gear_of_a_motor_car_rear_axle_(Army_Service_Corps_Training,_Mechanical_Transport,_1911).jpg) | 英国陆军后勤部队教程（HMSO，1911）；Andy Dingley 扫描 | 公有领域 |
| `assets/11-starley.jpg` | [File:Starley Tricycle Differential.jpg](https://commons.wikimedia.org/wiki/File:Starley_Tricycle_Differential.jpg) | Bury & Hillier，*Cycling*（2nd ed., 1889） | 公有领域 |

原图完整尺寸保存在 `originals/`：`differential-cutaway.jpg`（2048×1536）、`army-corps-1911.jpg`（790×571）、`starley-tricycle.jpg`（1957×1929）。`assets/` 里的对应文件只在宽度超过 1062 px 时做过一次等比缩小（`02-cutaway.jpg` 与 `11-starley.jpg` 两张），没有裁切、没有调色；`10-manual-1911.jpg` 宽度 790 px，小于画布宽，因此是原字节拷贝。

其余 14 张（`01`、`03`–`09`、`12`–`17`）是本文原创的示意图与数据图，由 `examples/build_figures.py` 生成，identity 记为「原创教学示意」。封面 `cover.png` 同为原创。

**身份说明**：`02-cutaway.jpg` 是真实照片（实物剖切件）；`10` 与 `11` 是出版物的扫描件（档案扫描件）。示意图与照片在正文里都标了身份，不互相顶替。

**缺口**：Pecqueur 1827 年的专利图、Starley 的专利原件、以及 `Around the Corner`（1937，Jam Handy 为雪佛兰拍的差速器教学片）的画面，本篇都没有收入。前三者没有找到可自由使用的电子版；1937 年那部片子本身是公有领域，但抽帧需要转码，属于另一轮工作。

## 代码

`examples/diff.py`、`examples/run_model.py`、`examples/build_figures.py` 为原创，MIT（见 `LICENSE-CODE.txt`）。`examples/figkit.py` 是本仓库多篇文章共用的绘图工具，同样 MIT。模型只用 Python 标准库（`build_figures.py` 另需 Pillow，见 `run-environment.json`）。
