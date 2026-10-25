# 复算 C 声明实验

输入是自造的整数样本，不是硬件测量。原始记录来自 GCC 14.2.0（Debian 14.2.0-19）、Linux x86_64、显式 C11 模式。数值与全部诊断见 [results.json](results.json)。代码 CC0 1.0；原创图与页面截图 CC BY 4.0，第三方短诊断的边界见 [来源说明](../sources.md)。

## 文件

- `main.c`：完整正例；使用已初始化对象和合法索引。包含故意保留的数组形参 `sizeof` 警告。
- `experiment.py`：编译运行正例，并编译六个负例；不执行负例。保存完整 stdout、stderr、命令与退出码。
- `build_figures.py`：从相邻 `results.json` 读取实际数字与箭头目标，生成13张原创示意图及其元数据。需 Pillow、fontTools、Noto Sans CJK 与 DejaVu Sans Mono。
- `viewer.html`：查看已保存记录的页面，选项只切换样例；需经 HTTP 打开。它不是在线编译器。
- `figure-metadata.json`：13张原创示意和3张实际浏览器截图的尺寸、字号、身份与用途。生成器只重建示意，不能把保留的截图声称成重新拍摄。

## 独立复算

先进入本目录，输出到文章目录以外的审计目录。以下相对目录按实际位置可调整，不要把二进制或临时负例写进文章目录。

```sh
PYTHONDONTWRITEBYTECODE=1 \
python experiment.py \
  --out ../../../../cdecl-audit
```

脚本会复制正例到输出目录，在那里编译，记录编译器版本。实验无随机种子。换平台时 `sizeof` 数值可能改变，诊断措辞和行号也可能改变；应比较类型行为及本机的对应尺寸关系，不强求字节完全相同。

仅重新生成随文这批图：

```sh
PYTHONDONTWRITEBYTECODE=1 \
python build_figures.py \
  --out ../../../../cdecl-figures
```

这条命令读取的是随文保存的 JSON。要按自己的实跑数据重新作图，可先复制整个 examples 目录到独立工作目录，在副本中用新 JSON 替换 `results.json`，再运行生成器。

从本目录提供记录页：

```sh
python -m http.server 8822 \
  --bind 127.0.0.1
```

然后在浏览器打开 `http://127.0.0.1:8822/viewer.html`。这只是本机静态文件服务；页面不接受、提交或执行任意 C 代码。读取失败会显示错误，正常载入后可查看成功记录和全部六个负例。

## 结果的边界

`grid` 是独立的二维数组，与 `samples` 只是第一行数值相同。图中两个步长分别来自 `element = grid[0]` 和 `rows = grid`；先做合法元素单位相减，再乘对应 `sizeof`，不跨无关对象减指针。

数组、指针、函数与函数指针均有独立用途。成功运行只核对本例路径，不能由声明推出空指针检查、数组长度检查、对象生命期或线程安全。没有执行越界访问、无效指针解引用、错误函数签名调用或不合法返回类型。
