# 暂停、恢复与清理的可运行实验

Python 3.12，标准库即可。在本目录运行 `python coroutine_lab.py`。

程序把本篇原生成器与原创有限状态机逐步对照，枚举六动作的0至5长度序列；打印9331序列、44790动作和具体轨迹。正常输入主例、异常结束、启动前关闭、双任务轮流及不自动抢占均有断言。不是通用协程库，也没有性能测试或网络操作。程序只打印JSON，不写数据文件。

## 示例程序许可

MIT License

Copyright (c) 2026 tech-articles contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
