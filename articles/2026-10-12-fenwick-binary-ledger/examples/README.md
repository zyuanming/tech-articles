# Fenwick树教学实验

仅使用Python标准库。测试环境CPython3.12.14，无网络访问和外部依赖。

运行：

```sh
python fenwick_lab.py
```

程序输出JSON结果；全部断言成功才会结束。它验证正文整数例子、有限枚举的查询/修改及非负频率的票号查找；不是性能基准，也不证明任意生产系统正确。

`add(i, delta)` 是增加量，位置从1开始。`prefix(0)`合法，`add(0, delta)`被拒绝。`select_nonnegative(ticket)` 要求调用者保证所有底层计数非负；函数检查票号范围，不额外保存原数组来验证非负前提。

## MIT License

Copyright (c) 2026 tech-articles contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
