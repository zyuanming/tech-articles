# 来源与许可

- [Linux官方Sequence counters and sequential locks](https://www.kernel.org/doc/html/latest/locking/seqlock.html)：实际查阅Introduction、seqcount_t、seqlock_t与三种读者路径；支撑裸计数器与写者锁的区别、抢占/中断约束、指针生命周期风险及重试饥饿。本篇10/20与11/22、全部交错和模4回绕均为独立教学输入，不是Linux实测。
- [Linux kernel memory barriers](https://www.kernel.org/doc/html/latest/core-api/wrappers/memory-barriers.html)：核查抽象内存访问与源代码顺序不能充当跨CPU可见性保证。文档本身声明为指导而非完备硬件规范；本文未据此提供生产实现。
- [C++工作草案intro.races](https://eel.is/c++draft/intro.races)：核查冲突访问、同步与数据竞争边界，未把顺序Python模型称为C++实现。

查阅日期2026-10-24。来源均作为事实核查，未复制源页图、代码或历史照片。assets/01—12全部原创，逐图职责、像素尺寸、字号与机械检查见[figure-metadata.json](examples/figure-metadata.json)。模型输出图不是操作系统运行截图。

复现：Python3.11+运行 `python examples/model.py` 得到results.json，Pillow及Noto Sans CJK字体环境中运行 `python examples/build_figures.py`。实际模型枚举6种裸读交错、70种序号交错；后者2次接纳、68次拒绝，所有接纳对满足预设不变量。模型没有线程、真实指针、CPU重排或C++数据竞争；交错数量不能当实际重试概率。两写者反例是展示前提失效的独立示意，不宣称由单写者枚举验证。

原创正文、12张原创图由zyuanming以CC BY 4.0提供：https://creativecommons.org/licenses/by/4.0/ 。原创Python代码独立采用MIT：

Copyright (c) 2026 zyuanming

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

本文使用AI辅助研究、写作、制图与代码；结果由教学程序实际执行获得，不声称测试Linux或生产并发性能。
