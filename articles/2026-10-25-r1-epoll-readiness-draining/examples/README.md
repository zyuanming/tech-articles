# epoll 本地实验

需要 Linux 与 Python 3.12；实验只用标准库。存档实跑：Linux 发布号数字部分 6.18.55、Python 3.12.14。使用非阻塞 AF_UNIX/SOCK_STREAM socketpair，全部 epoll 轮询超时为零；没有随机种子、外部服务和性能计时。

先在终端进入本文的 `examples` 目录，再运行以下命令。输出目录位于仓库之外；如果你的目录层级不同，请调整这个相对路径。

```sh
export PYTHONDONTWRITEBYTECODE=1
mkdir -p ../../../../epoll-audit
python experiment.py \
  --output \
  ../../../../epoll-audit/run.json
```

程序直接执行并验证：LT/ET 部分读取、ET 未排空时新增数据、通知后被其他读取者先取走数据、换行协议拼接、EOF、ONESHOT、部分写与恢复、两个端点的预算轮转。JSON 保存符号端点、事件标志、输入、实际字节和操作顺序，没有 fd 数字或主机标识。若本机结果不同，保留失败与结果，不能为得到图中的答案而修改输出。

`results.json` 是本文采用的科学数据。`experiment.py` 未指定 `--output` 时会写当前目录的 `results.json`，因此普通复验请使用上面的独立输出路径。实验主要用断言检查当前指定输入；修改输入或读取长度后，应一并更新相应断言。`EINTR` 是代码处理分支，本次没有注入信号；错误路径也不冒称全覆盖。Python 某些接口会自动重试信号中断。

写实验的 65,536 字节、请求发送缓冲 4,096 是输入参数；第一次接纳 8,064、查询缓冲 8,192 等是存档运行输出，不是跨机器保证。输出队列全部内容由接收侧核对。公平性实验先按符号名称入队，再按两字节预算轮转，不声称这是 epoll 的事件排序。

## 本地教学页面

```sh
python demo_web.py --port 8920
```

浏览器打开 `http://127.0.0.1:8920`。点击“运行实验”会调用 Python 重新创建 socket 并运行实验，不是回放 `results.json`；模式选择可显示 LT 或 ET 的步骤。服务器只监听本机回环地址；按 Ctrl+C 停止。网页截图是原创教学工具的真实效果，不是 Linux 自带监控界面。

## 重新生成图片

只在准备重新制作整套输出时执行以下步骤；它们会更新本文目录内的图片与元数据。需要 Pillow、fontTools；真实浏览器截图另需 Playwright Python 包及系统 Chromium，中文字体使用 Noto Sans CJK。生成器找不到中文字体会报错。

```sh
python -m pip install \
  pillow fonttools playwright
python build_figures.py
python capture_demo.py
```

`build_figures.py` 读取现有 `results.json`，生成 00–13 的解释图并更新 `figure-metadata.json`。字节格子随字符串长度生成，写入色段以实际接纳字节数除以整段长度计算；版式位置与字体大小只是布局常量。生成器检查字符覆盖、出界、文字越框、重叠、字号、对比、墨迹像素和实际尺寸。

`capture_demo.py` 启动本地页面，使用系统 Chromium 默认启动设置，实际点击运行，检查 354 与 1062 像素宽下 LT/ET 两种选择，再保存 14 号图与 `demo-capture.json`。截图 CSS 宽 354、设备比例 3，原图宽 1062；不是把小图插值放大。此时重新运行的结果与原存档属于两次实验；环境不同应核对后再更新正文数字。

## 文件与许可

- `experiment.py`：可复现实验及断言；`results.json`：本文科学数据。
- `build_figures.py`：原创图生成器；`figure-metadata.json`：尺寸、字体与身份。
- `demo_web.py`：真实运行教学界面；`capture_demo.py`：截图与浏览器检查。
- `demo-capture.json`：浏览器版本、视口和实际语义结果。

原创代码及 JSON 数据由 zyuanming 以 [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) 提供；原创图与界面截图采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。外部软件、字体与第三方文档各自保留原许可，未打包进本篇。正文、素材与来源边界见[来源说明](../sources.md)。
