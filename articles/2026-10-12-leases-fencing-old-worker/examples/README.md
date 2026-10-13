# 运行围栏小实验

在Python3.12运行 `python fencing_lab.py`。无需依赖、网络、账户、数据库或集群。它是原创有限状态教学模型，输出所有规模计数、开头记分轨迹以及故意破坏前提的反例。

先看主例：A41先读100；B登记42、读100并写120；A41后写110被拒绝。再改边界实验，观察“先读再登记”和“检查/写入不原子”为什么分别出错。

有限枚举保证只覆盖代码写明的单资源/单次操作模型，不代表真实发号、持久化、网络协议或生产系统已经验证。正文与sources列出条件。

## MIT License

Copyright (c) 2026 zyuanming

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
