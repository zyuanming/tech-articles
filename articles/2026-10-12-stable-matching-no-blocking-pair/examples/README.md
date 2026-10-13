# 稳定匹配教学实验

仅使用Python标准库，在CPython3.12.14实际运行，无网络和外部依赖。

```sh
python matching_lab.py
```

程序打印JSON。全部断言通过后才会正常结束；枚举46673份n≤3的完整偏好，再验证固定种子1000份n=4样本。检查器通过逐份枚举全部匹配并寻找阻塞对，与构造算法分开实现。

输入范围：两边相同人数，每份排序均为0到n−1的完整排列，没有并列，每人认为所有候选都可接受。`deferred`返回按左侧人员索引的匹配和事件日志。代码是教学实验，不是任意外部输入校验器，也不处理群体联动、名额约束、不可接受对象或真实录取。

## MIT License

Copyright (c) 2026 tech-articles contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
