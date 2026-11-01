# 来源

## 事实

**限速器与安全钳的整体结构**
- <https://en.wikipedia.org/wiki/Elevator>（二手）
- 用于：第一节的零件名称（限速器、限速绳、张紧轮、安全钳、导轨）、"绳的两端连在轿厢上、绕过底部张紧轮"这一走线、以及"限速绳由轿厢带动，因此绳速等于轿厢速度"的关系。

**限速器的触发速度与甩块机构**
- <https://en.wikipedia.org/wiki/Safety_governor>（二手）
- 用于：第二、三节的"测的是速度不是加速度"、甩块—弹簧—棘爪的动作顺序、以及离心力随转速平方增长这一条。

**Otis 与 1854 年水晶宫演示**
- <https://en.wikipedia.org/wiki/Elisha_Otis>（二手）
- 用于：第八节的年份、地点（纽约水晶宫，Exhibition of the Industry of All Nations）、以及"砍断吊绳、平台下坠几英寸后被卡住"这一情节。当年的报纸原文没有查。

**楔块式安全钳与自锁**
- <https://en.wikipedia.org/wiki/Elevator_safety_gear>（二手）
- 用于：第五节楔块的方向（上窄下宽、往上挤）、渐进式安全钳用弹簧限制夹紧力这一设计、以及楔角与摩擦角决定自锁的定性说法。具体的 N = D / tan(α + φ) 是本文按单斜面滑块自行推导的简化式，不是引自某份规范。

**EN 81 / GB 7588 的通行表述**
- 触发速度不低于额定的 115%、平均减速度不超过 1 g 左右：这两条是公开资料里对电梯安全规范（EN 81-20/-50、GB 7588 系列）常见要求的转述。
- **本文没有逐条核对规范原文，正文也没有写条款号。** 要用于工程判断，请查现行有效的规范文本。

**埃菲尔铁塔电梯限速器**
- <https://commons.wikimedia.org/wiki/File:Otis_Wheel_Governor,_Eiffel_Tower.jpg>
- 该图出自 *Engineering News*, Vol. 28 No. 28（1892）。Commons 的 extmetadata 把作者标为 "Multiple Authors"，没有给出更细的署名；本文按"1892 年工程期刊插图"标注。

## 模型里哪些是设定值

- 额定速度 1.75 m/s、轿厢加一半载荷 1200 kg、绳轮直径 200 mm、甩块 0.25 kg（重心离轴 60 mm）、导轨摩擦系数 0.15：都是"常见量级"，用来把公式跑出一组自洽的数字，不对应某一款电梯。
- 反应延迟 0.15 s、夹紧力爬升 0.08 s：这是本文设定的时间常数，用来演示"触发不等于刹住"。图 7 把它拆成 40 / 60 / 50 / 80 毫秒四段，同样是估算。**真实数值我没有测过。**
- 减速度 6 m/s²：选定值，用来和 3 / 9 / 12 m/s² 做对照（图 12、图 13）。
- 楔块用单斜面滑块模型：N = D / tan(α + φ)，假设纯滑动、无变形、单接触面。真实安全钳是多面受力、碟簧非线性，图 10 的曲线只能读趋势。
- 40 kg 钢、比热 470 J/(kg·K)：用来把制停能量换算成温升，是钢材的常见量级。
- 20 m 提升高度、限速绳 0.25 kg/m（一圈 10 kg）、张紧轮 40 kg：用来算绳的张力（196 N）和绳被突然停住时的冲力。绳的弹性、滑轮惯量都没有算。

## 图片

四张照片/扫描件全部来自 Wikimedia Commons，许可与作者按下表独立保留；正文的 CC BY 4.0 **不覆盖**这四张图。

| 文件 | 原文件 | 作者 / 机构 | 许可 |
| --- | --- | --- | --- |
| `assets/02-governor.jpg` | [File:Elevator speed governor.jpg](https://commons.wikimedia.org/wiki/File:Elevator_speed_governor.jpg) | Darklanlan（own work） | CC BY 4.0 |
| `assets/11-safety-gear.jpg` | [File:Keilfangvorrichtung Aufzugsbau.jpg](https://commons.wikimedia.org/wiki/File:Keilfangvorrichtung_Aufzugsbau.jpg) | Coptercam（own work） | 公有领域 |
| `assets/15-otis-1854.jpg` | [File:Elisha OTIS 1854.jpg](https://commons.wikimedia.org/wiki/File:Elisha_OTIS_1854.jpg) | 佚名版画，1854 年 | 公有领域 |
| `assets/16-eiffel-1892.jpg` | [File:Otis Wheel Governor, Eiffel Tower.jpg](https://commons.wikimedia.org/wiki/File:Otis_Wheel_Governor,_Eiffel_Tower.jpg) | *Engineering News*, 1892；Commons 标为 Multiple Authors | 公有领域 |

原图完整尺寸保存在 `originals/`：`governor.jpg`（1072×803）、`safety-gear.jpg`（640×480）、`otis-1854.jpg`（3567×3514）、`eiffel-governor.jpg`（1214×875）。`assets/` 里的对应文件只在宽度超过 1062 px 时做过一次等比缩小（`02`、`15`、`16` 三张），没有裁切、没有调色；`11-safety-gear.jpg` 宽 640 px，小于画布宽，因此是原字节拷贝。

其余 14 张（`01`、`03`–`10`、`12`–`14`、`17`、`18`）是本文原创的示意图与数据图，由 `examples/build_figures.py` 生成，identity 记为「原创教学示意」。封面 `cover.png` 同为原创。

**身份说明**：`02` 与 `11` 是真实照片（机房里的限速器、楔块式安全钳实物）；`15` 与 `16` 是档案扫描件（1854 年版画、1892 年期刊插图）。示意图不顶替实物照片，版画也不当照片用。

**缺口**：Otis 1861 年专利（US 31,128）里的附图、以及各家电梯厂家的安全钳坠落试验视频，本篇都没有收入。专利图在 Commons 上有公有领域版本（`File:ElevatorPatentOtis1861.jpg`），但正文没有用到它的具体内容，收入会变成"为了配图而配图"；试验视频没有可自由使用的版本。

## 代码

`examples/elevator.py`、`examples/run_model.py`、`examples/build_figures.py` 为原创，MIT（见 `LICENSE-CODE.txt`）。`examples/figkit.py` 是本仓库多篇文章共用的绘图工具，同样 MIT。模型只用 Python 标准库（`build_figures.py` 另需 Pillow，见 `run-environment.json`）。
