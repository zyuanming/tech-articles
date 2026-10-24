# 来源与许可

- [SimPy Time and Scheduling](https://simpy.readthedocs.io/en/latest/topical_guides/time_and_scheduling.html)：实际查阅模拟时间、顺序处理同刻事件、堆队列与递增eid。本文是自己写的整数时间模型，额外明确完成事件优先，未宣称复制SimPy完整内部排序或运行SimPy。
- [SimPy Environments](https://simpy.readthedocs.io/en/4.1.0/topical_guides/environments.html)：普通环境与实时环境的区别，说明模拟时间不等于墙钟等待。
- [Python heapq](https://docs.python.org/3/library/heapq.html)：标准库最小堆操作契约。正文不复述旧库存的堆维护原理，只使用其最早事件功能。

查阅日期2026-10-24。四作业输入与所有数据、图为独立教学构造，无第三方图像复制，无打印机照片或产品性能宣称。逐图用途、实际宽高、字号与几何检查见[figure-metadata.json](examples/figure-metadata.json)。

复现：Python3.11+运行 `python examples/model.py`，安装Pillow及Noto Sans CJK后运行 `python examples/build_figures.py`。实际处理8事件，得到服务[0,4]、[4,6]、[6,7]、[8,10]；等待0/3/2/0，总等待与队长时间面积均5。模型还运行两种到达/完成同刻优先级（本输入结果相同），以及独立的超时不交换反例与代号取消例。无随机性、sleep、线程或实际外设。

原创正文与12张原创图：zyuanming，CC BY 4.0，https://creativecommons.org/licenses/by/4.0/ 。原创Python代码独立采用MIT：

Copyright (c) 2026 zyuanming

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

本文使用AI辅助资料研究、讲解、代码与制图；结果来自实际执行的教学模型，不是设备、生产服务或网络性能实测。
