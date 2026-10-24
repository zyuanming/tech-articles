# 来源与许可

- Robert D. Blumofe、Charles E. Leiserson，Scheduling Multithreaded Computations by Work Stealing：[论文原文镜像](https://perso.ens-lyon.fr/loris.marchal/docs-data-aware/papers/scheduling-multithreaded-comp-WS.pdf)。核查摘要及工作/跨度、fully strict限制、随机窃取与期望界；只作有限背景归纳。本文八任务图、成本与调度是独立教学构造，不复制论文图，也不把该定理推广到任意阻塞程序。
- [OpenCilk concepts](https://www.opencilk.org/doc/tutorials/opencilk-concepts/)：原项目对依赖结构、work、span及parallelism的解释；[work stealing词条](https://www.opencilk.org/doc/reference/glossary/work-stealing/)核实本地工作与空闲窃取机制。页面的原例图不属于本文八任务输入，且未据页面确认可再分发许可，未复制或描摹。

查阅日期2026-10-24。不存在第三方素材归档；assets/01—12均由examples/build_figures.py依据本篇独立数据绘制。逐图理解职责、实际像素宽高和字号见[figure-metadata.json](examples/figure-metadata.json)，每图在正文附近有图注。没有历史照片、产品界面或生产性能测量；不以模型图冒充它们。

运行Python 3.11+的 `python examples/model.py`，生成results.json；安装Pillow并提供Noto Sans CJK字体后，运行 `python examples/build_figures.py`。模型为单线程、整数时间、两工作者、零调度开销；初始分派固定，任务运行不可抢占，未模拟真正并发deque。断言检查每任务恰好一次、总工作守恒与时间下界。

原创正文及12张原创图：zyuanming，CC BY 4.0，https://creativecommons.org/licenses/by/4.0/ 。代码为MIT，以下许可独立适用于examples目录中原创Python代码：

Copyright (c) 2026 zyuanming

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

本文使用AI辅助一手资料检索、讲解、代码和制图；数字来自实际运行的教学程序。独立判断与复算仍需保留；没有声称运行过OpenCilk或测过真实并行加速。
