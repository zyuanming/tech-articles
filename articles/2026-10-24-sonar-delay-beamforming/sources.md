# 来源、图像权利与复算范围

原创正文与明确标为原创的教学图分别采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。第三方素材仍按各自权利使用，不纳入正文统一许可。引用来源页面不代表取得其中所有图片的许可。

## 事实与模型

- [MIT OCW：2.682 Acoustical Oceanography，Lecture11](https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/520494b38732649598f85bf5bc722d9e_MIT2_682S12_lec11.pdf)，2012：平面波延时、近场聚焦、栅瓣及窄带相移与宽带时延的区别。仅参考事实和数学原则，未复制其插图或文字表达。
- [Kongsberg：EM712数据表](https://www.kongsberg.com/contentassets/2c197a1f0a33461b9642276e31b67fb7/datasheet_em_712.pdf)，387595/C，2022-03：实际系统使用时间延迟波束形成支持宽带；这是不同于照片EM304的型号。
- [NOAA：Multibeam Sonar](https://oceanexplorer.noaa.gov/technology/sonar-multibeam/)：船底阵列、回波时间、声速和测深应用。
- 1500m/s、10kHz、0.075m间距、四/八理想点元件为本文独立远场教学模型；所有方向曲线以真实来向30度固定，扫描处理假设角度。

本文的说明与手算步骤为原创表达。AI参与检索辅助、中文草稿、计算代码与教学图制作；未虚构实测、人物对白、现场经历或收听体验。数字为可重算模型，不能充作设备规格或测量记录。

## 逐图来源与变更

| 文件 | 作者及原链接 | 权利 | 用途与变更 |
| --- | --- | --- | --- |
| `originals/photos/transducer.jpg` | **Charlie Wilkins、David Blessing、Michael Peperato**，NOAA Ocean Exploration；[EM304对象页面](https://oceanexplorer.noaa.gov/multimedia/okeanos-explorations-ex2101-features-em304-media-transducer1/)，[原文件链接](https://oceanexplorer.noaa.gov/wp-content/uploads/2021/05/transducer1-hires.jpg) | 依[NOAA Ocean Exploration FAQ](https://oceanexplorer.noaa.gov/faqs/)与[NOAA版权FAQ](https://oceanservice.noaa.gov/about/faq.html)中无另注版权资料的公共领域说明使用，保留三位作者署名 | 复用本库已存原照片，不改像素、不裁剪；不代表四元教学模型或EM712型号。 |
| `assets/01.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 平面波到达顺序；由附带代码产生，非实测/历史照片 |
| `assets/02.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 路程差三角几何；由附带代码产生，非实测/历史照片 |
| `assets/03.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 到达时间表；由附带代码产生，非实测/历史照片 |
| `assets/04.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 补偿时间与到达相加；由附带代码产生，非实测/历史照片 |
| `assets/05.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 四路原始相位错位；由附带代码产生，非实测/历史照片 |
| `assets/06.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 对齐相加；由附带代码产生，非实测/历史照片 |
| `assets/07.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 方向扫描模型；由附带代码产生，非实测/历史照片 |
| `assets/08.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 方向扫描模型；由附带代码产生，非实测/历史照片 |
| `assets/09.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 方向扫描模型；由附带代码产生，非实测/历史照片 |
| `assets/10.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 宽带时延与固定相移区别；由附带代码产生，非实测/历史照片 |
| `assets/11.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 平面近似的边界；由附带代码产生，非实测/历史照片 |

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
