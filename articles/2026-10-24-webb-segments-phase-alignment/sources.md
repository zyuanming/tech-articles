# 来源、图像权利与复算范围

原创正文与明确标为原创的教学图分别采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。第三方素材仍按各自权利使用，不纳入正文统一许可。引用来源页面不代表取得其中所有图片的许可。

## 事实与模型

- [NASA：Webb’s Mirrors](https://science.nasa.gov/mission/webb/webbs-mirrors/)：十八块分段主镜、驱动调节与工程背景。
- [NASA SVS：Webb Mirror Alignment Animations](https://svs.gsfc.nasa.gov/20358/)，2022-02-16发布：星像识别、叠像、粗调相、精调相、视场对准的职责。本文未复制动画，也未将自己的两孔径模型冒充真实调试结果。
- 两等幅相干波、正常入射镜面双程几何与一维双孔径远场曲线为本文逐步推导。双孔径单段宽度归一为1，中心间距为1.5，振幅模型为sinc(u)乘两段的相位和。

本文的说明与手算步骤为原创表达。AI参与检索辅助、中文草稿、计算代码与教学图制作；未虚构实测、人物对白、现场经历或收听体验。数字为可重算模型，不能充作设备规格或测量记录。

## 逐图来源与变更

| 文件 | 作者及原链接 | 权利 | 用途与变更 |
| --- | --- | --- | --- |
| `originals/photos/webb-test.jpeg` | NASA/Chris Gunn；[照片原页](https://www.flickr.com/photos/nasawebbtelescope/50733595786/)，[原尺寸入口](https://www.flickr.com/photos/nasawebbtelescope/50733595786/sizes/o/) | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/)；保留原作者、来源和许可 | 本库既有保留完整画面的缩小/JPEG压缩版本，本次按字节复用，无裁剪或重绘。 |
| `assets/01.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 镜片分段与中央开口；由附带代码产生，非实测/历史照片 |
| `assets/02.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 相同入射方向与不同镜面反射方向；由附带代码产生，非实测/历史照片 |
| `assets/03.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 相长相消的连续波形；由附带代码产生，非实测/历史照片 |
| `assets/04.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 光程到相位的线性转换；由附带代码产生，非实测/历史照片 |
| `assets/05.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 反射位移双程系数；由附带代码产生，非实测/历史照片 |
| `assets/06.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 区分倾斜和活塞；由附带代码产生，非实测/历史照片 |
| `assets/07.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 相位箭头与强度；由附带代码产生，非实测/历史照片 |
| `assets/08.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 光程相位和中心强度；由附带代码产生，非实测/历史照片 |
| `assets/09.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 两孔径远场分布非Webb真实PSF；由附带代码产生，非实测/历史照片 |
| `assets/10.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 两波长约束；由附带代码产生，非实测/历史照片 |
| `assets/11.png` | 本文原创，tech-articles contributors | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 已知多样性辅助相位恢复；由附带代码产生，非实测/历史照片 |

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
