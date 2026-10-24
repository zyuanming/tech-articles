# 来源与许可

- Norm Hardy，[The Confused Deputy](https://css.csail.mit.edu/6.858/2015/readings/confused-deputy.html)，MIT保存的当事人原文。原文明确更改非关键细节；本文只归纳权限来源混淆的背景，照片转换例、权限图、数值与代码为独立构造，不复刻史实或虚构对白。
- Robert N. M. Watson等，[Capsicum: practical capabilities for UNIX](https://www.cl.cam.ac.uk/research/security/capsicum/papers/2010usenix-security-capsicum-website.pdf)，2010，核查§2能力模式、受限文件描述符、权利子集与隔间化设计。原论文图1—5用于作者理解设计，未确认其图片开放再分发许可，不复制、截屏或照描；本文以独立的照片转换图讲授权限。
- FreeBSD官方[cap_rights_limit](https://man.freebsd.org/cgi/man.cgi?query=cap_rights_limit)、[cap_enter](https://man.freebsd.org/cgi/man.cgi?query=cap_enter)：仅核查接口职责；不使用历史论文cap_new作为当前接口教学，不声称已运行FreeBSD。

查阅日期2026-10-24。assets/01—12均为原创关系图或独立内存模型结果；无第三方图片归档。逐图职责、宽高、字号与几何检查见[figure-metadata.json](examples/figure-metadata.json)。正文简短历史背景不以人物传记为主线，不生成或伪造历史现场。

复现：Python3.11+执行 `python examples/model.py`，Pillow/Noto Sans CJK环境执行 `python examples/build_figures.py`。所有对象均为内存字符串；程序没有打开业务文件、访问账号、改变操作系统权限或测试漏洞。Broker及调用接口是假设的可信边界；who由测试驱动代入可信主体，本模型未实现主体鉴别，不能让不可信请求者自由自报身份。Python对象本身不构成对恶意同进程代码的隔离。验证五项授权结果、账本不变与可撤销门/直接引用的区别。

原创正文及12张原创图：zyuanming，CC BY 4.0，https://creativecommons.org/licenses/by/4.0/ 。原创Python代码独立采用MIT：

Copyright (c) 2026 zyuanming

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

本文使用AI辅助资料研究、叙述、代码与制图；所有程序结果为实际执行的教学模型输出，不能作为安全认证或生产沙箱测试结论。
