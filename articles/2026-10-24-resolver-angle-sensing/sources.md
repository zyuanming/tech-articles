# 来源、图像权利与复算范围

原创正文与明确标为原创的教学图分别采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。第三方素材仍按各自权利使用，不纳入正文统一许可。引用来源页面不代表取得其中所有图片的许可。

## 事实与模型

- [Analog Devices：Precision Resolver-to-Digital Converter Measures Angular Position and Velocity](https://www.analog.com/en/resources/analog-dialogue/articles/precision-rtdc-measures-angular-position-and-velocity.html)，Jakub Szymczak、Shane O’Meara、Johnny Gealon、Christopher Nelson De La Rama：励磁、正余弦包络、极对数与跟踪转换器。本文投影与四样本同步解调为独立教学模型，不声称复制某款转换器。
- [Texas Instruments：Using the AMC1210 in Resolver Motor Control Systems](https://www.ti.com/lit/pdf/sbaa144)，Mike Hartshorne，2006：旋转变压器的双路幅度调制信号及同步解调处理。
- [Apollo 11 Mission Report](https://www.nasa.gov/wp-content/uploads/static/apollo50th/pdf/A11_MissionReport.pdf)，NASA，1969，Figure16-14/page16-36：仅支撑交会雷达天线位置的resolver与耦合数据单元接口，不是多普勒测速图。

本文的说明与手算步骤为原创表达。AI参与检索辅助、中文草稿、计算代码与教学图制作；未虚构实测、人物对白、现场经历或收听体验。数字为可重算模型，不能充作设备规格或测量记录。

## 逐图来源与变更

| 文件 | 作者及原链接 | 权利 | 用途与变更 |
| --- | --- | --- | --- |
| `assets/apollo-radar.png` 与 `originals/apollo-radar.pdf` | NASA，NASA-S-69-3788；[Apollo 11报告原文件](https://www.nasa.gov/wp-content/uploads/static/apollo50th/pdf/A11_MissionReport.pdf)，图16-14 | NASA美国政府工程材料，按[NASA媒体使用政策](https://www.nasa.gov/nasa-brand-center/images-and-media/)使用，保留署名，不暗示背书 | 复用既有单页摘录及其PNG渲染；本次不改像素。正文另以中文新图解释关键关系。 |
| `assets/01.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 建立角度零位和正方向；由附带代码产生，非实测/历史照片 |
| `assets/02.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 30度的正交投影与归一化幅度；由附带代码产生，非实测/历史照片 |
| `assets/03.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 一条正弦幅度不能唯一确定全周角度；由附带代码产生，非实测/历史照片 |
| `assets/04.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 线圈有效磁轴正交的概念模型，不是绕组施工图；由附带代码产生，非实测/历史照片 |
| `assets/05.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 分清载波快振荡与轴角度缓慢变化；由附带代码产生，非实测/历史照片 |
| `assets/06.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 同励磁参考用于两路同步解调；由附带代码产生，非实测/历史照片 |
| `assets/07.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 负系数表现为与励磁反相而非负的峰峰值；由附带代码产生，非实测/历史照片 |
| `assets/08.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 四象限的符号组合；由附带代码产生，非实测/历史照片 |
| `assets/09.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 相同通道增益与角度比值关系；由附带代码产生，非实测/历史照片 |
| `assets/10.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 增益不匹配对整圈轨迹的影响；由附带代码产生，非实测/历史照片 |
| `assets/11.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 角度包裹与跨零差值；由附带代码产生，非实测/历史照片 |

正文只使用上表列出的第三方材料。参考资料的其他插图、动画帧和产品示意未在本文复制；本文用独立绘制图完成自身推导，不将源页缩略图、播放器或导航图当作正文配图。照片保留真实设备身份，原创图不是原机结构复刻。实际尺寸及原创图最小字号见 `examples/figure-metadata.json`；历史原件与照片字体未测量，不计入原创图字号统计。

## 可复算文件与许可

`python examples/build_figures.py` 先计算模型数据写入 `results.json`，再读取绘图。本轮实际运行版本为 Python 3.12.14、Pillow 12.3.0、fontTools 4.61.1，字体为系统 Noto Sans CJK；无随机抽样、无外部服务调用。`results.json` 为本文原创模型数据，采用 [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)。原创 Python 代码采用下列 MIT 许可；第三方 Python 库仍保留各自许可。

```text
MIT License

Copyright (c) 2026 tech-articles contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
