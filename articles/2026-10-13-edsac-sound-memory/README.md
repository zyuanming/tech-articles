# EDSAC：在时间里保存信息

[从正文开始阅读](read.md)。文章面向有兴趣、尚未学习计算机硬件的读者。静态图文已经完整解释机制；代码不是阅读前提。

- `read.md`：完整文章。
- `sources.md`：事实支撑、逐图来源、开放许可与模型边界。
- `cover.png`：独立原创封面。
- `assets/`：正文原创图与剑桥原始历史照片。照片保持下载字节，不裁切、不生成历史细节。
- `examples/delay_model.py`：八时隙理想循环模型，Python标准库即可运行。
- `examples/results.json`：模型实际运行结果，包含读出、改写、关掉反馈、等待计算与检查结果。
- `examples/build_figures.py`：原创图的可复现绘制代码，使用Pillow与Noto Sans CJK字体。
- `licenses/`：第三方许可原文及本篇原创作品许可说明。

## 复算

在文章目录下运行：

```sh
python examples/delay_model.py
```

程序仅覆盖同目录的`examples/results.json`。无网络、账户、硬件和水银操作。该模型不仿真EDSAC指令、电路或声学。

可选重绘：

```sh
python examples/build_figures.py
```

本次运行环境为Python3.12.14、Pillow12.3.0，Noto Sans CJK字体来自环境已有安装。重绘脚本将覆盖原创PNG和封面；不处理第三方照片。其他系统需将脚本中的字体路径指向本机对应字体，不必安装任何历史模拟器。

正文、原创教学图与这两个原创Python脚本以CC BY 4.0提供；历史照片按`sources.md`中所列许可分别处理。引用时署名“学生探索系列”，并标明修改与许可链接；不得把第三方照片的原署名去掉。
