# 来源与许可

- Edsger W. Dijkstra、C. S. Scholten，[Termination detection for diffusing computations，EWD684原文转录](https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD684.html)。实际查阅扩散计算、工作/反向信号、cornet首项最后移除、deficit与参与树不变量P3及两个定理。本文采用父指针/逐消息回执的教学变体，不声称是原文cornet与count的逐行实现；三节点三任务轨迹和所有图均独立设计，非历史现场或原论文图复刻。

查阅日期2026-10-24。原手稿及论文插图未确认开放再分发许可，因此不复制扫描或截图；正文提供原站链接。12张图全部是独立消息、账目、参与树或程序结果图，逐图职责、宽高、字号和机械检查见[figure-metadata.json](examples/figure-metadata.json)。人物名字仅标来源贡献，不虚构生平故事、对白、动机或肖像。

复现：Python3.11+运行 `python examples/model.py`，Pillow/Noto Sans CJK环境运行 `python examples/build_figures.py`。模型只处理固定三任务：R初始发A、B；A完成再发B；B不派生。穷举任意在途消息投递与本地任务执行选择，按在途集合排列去重，共37状态，1个去重终止状态，最大未结账3，没有错误终止。断言覆盖欠账守恒、父关系及无环、宣布时全空与三任务完成；不是无限系统证明，不模拟失效/重启/消息重复或不公平调度。

原创正文与12张原创图：zyuanming，CC BY 4.0，https://creativecommons.org/licenses/by/4.0/ 。原创Python代码独立采用MIT：

Copyright (c) 2026 zyuanming

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

本文使用AI辅助资料研究、讲解、代码与制图；结果来自实际执行的教学模型，不是设备、生产服务或网络性能实测。
