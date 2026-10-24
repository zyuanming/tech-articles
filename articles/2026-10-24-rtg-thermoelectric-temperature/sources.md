# 来源、图像权利与复算范围

原创正文与明确标为原创的教学图分别采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。第三方素材仍按各自权利使用，不纳入正文统一许可。引用来源页面不代表取得其中所有图片的许可。

## 事实与模型

- [NASA：How Does a Radioisotope Thermoelectric Generator Work? The Seebeck Effect](https://science.nasa.gov/resource/how-does-a-radioisotope-thermoelectric-generator-rtg-work-the-seebeck-effect/)：衰变供热、热电偶串联、无转动转换部件。
- [Ferrotec：Thermoelectric Reference Guide, 13.0 Power Generation](https://thermal.ferrotec.com/technology/thermoelectric-reference-guide/thermalref13/)：V=SΔT、内阻带来的压降、负载电流与功率。本文400微伏/K、100对、4欧姆和100W热输入均为自定教学条件，不引用为产品参数。
- [Northwestern University Thermoelectrics：Engineering](https://thermoelectrics.matsci.northwestern.edu/thermoelectrics/engineering.html)：热电输出涉及电输运和热输运，常系数电路并不能单独决定热效率。

本文的说明与手算步骤为原创表达。AI参与检索辅助、中文草稿、计算代码与教学图制作；未虚构实测、人物对白、现场经历或收听体验。数字为可重算模型，不能充作设备规格或测量记录。

## 逐图来源与变更

| 文件 | 作者及原链接 | 权利 | 用途与变更 |
| --- | --- | --- | --- |
| `originals/photos/rtg.jpg` | NASA/JPL-Caltech；[Voyager RTG对象原页](https://science.nasa.gov/resource/voyagers-radioisotope-thermoelectric-generator-rtg-2/) | 按[NASA媒体政策](https://www.nasa.gov/nasa-brand-center/images-and-media/)和[JPL图像使用政策](https://www.jpl.nasa.gov/jpl-image-use-policy/)使用，保留署名，不暗示背书 | 本库既有RTG实物照片字节，本次无改动。 |
| `assets/01.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 区分热流与电输出；由附带代码产生，非实测/历史照片 |
| `assets/02.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 开路电压的作用平衡示意；由附带代码产生，非实测/历史照片 |
| `assets/03.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 热通路与电连接方向；由附带代码产生，非实测/历史照片 |
| `assets/04.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 可手算电压斜率；由附带代码产生，非实测/历史照片 |
| `assets/05.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 串联累计电压非串联温差；由附带代码产生，非实测/历史照片 |
| `assets/06.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 闭合电路的串联分压；由附带代码产生，非实测/历史照片 |
| `assets/07.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 固定温差负载匹配曲线；由附带代码产生，非实测/历史照片 |
| `assets/08.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 同尺度热电功率分流；由附带代码产生，非实测/历史照片 |
| `assets/09.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 散热鳍片的作用；由附带代码产生，非实测/历史照片 |
| `assets/10.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 冷端温度影响温差；由附带代码产生，非实测/历史照片 |

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
