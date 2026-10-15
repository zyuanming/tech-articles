# 出处、素材与制作说明

核查日期：2026-10-14。本文以同一原创标量程序为解释主线；下面区分机制资料、历史原文和本地实际运行结果。

## 一手机制资料

1. [PyTorch：Overview of PyTorch Autograd Engine](https://pytorch.org/blog/overview-of-pytorch-autograd-engine/)。官方实现团队文章，2021-06-08，文中实现背景为PyTorch 1.8。支持正向求值、反向局部链式传播、输出种子1、共享输入的贡献先累加再传播等机制。本文未复制其图或代码；文章中反向乘积的术语较松，本篇使用下述JAX文档的前向JVP/反向VJP区分。
2. [JAX：Forward- and reverse-mode autodiff](https://docs.jax.dev/en/latest/jacobian-vector-products.html)。支持前向与反向的方向、单输出多输入的成本优势、多输出时一趟反传不等于完整Jacobian。正文只使用条件明确的同量级表述，不把示意常数倍变成通用运行时间保证。
3. [JAX：Control autodiff’s saved values with jax.checkpoint](https://docs.jax.dev/en/latest/notebooks/autodiff_remat.html)。支持保存必要中间量、检查点重算与存储/计算交换。本文图12为原创策略示意，不是JAX运行结果或内存实测。
4. [PyTorch：Autograd mechanics](https://docs.pytorch.org/docs/main/notes/autograd.html)，重点为How autograd encodes the history、Saved tensors、Gradients for non-differentiable functions。支持本次执行图、保存前向值和不可导点的框架特定约定。普通数学导数不存在与软件返回约定值严格分开，不推广到所有框架。

## 历史原文

5. Seppo Linnainmaa, *Taylor expansion of the accumulated rounding error*, BIT 16, 146–160 (1976)。[出版记录与DOI](https://doi.org/10.1007/BF01931367)；[可读原文镜像](https://papers.baulab.info/papers/also/Linnainmaa-1976.pdf)。原文第152–153页Algorithm T说明末项系数置1、逆序读取运算并向操作数累加局部导数贡献；同文讨论求导计算本身的舍入误差与保存成本。正文只据此说明1976年的数值分析用途，不据参考文献中的1970年学位论文作未核验的发明优先权判断。
6. David E. Rumelhart, Geoffrey E. Hinton, Ronald J. Williams, *Learning representations by back-propagating errors*, Nature 323, 533–536 (1986)。[出版记录及摘要](https://www.nature.com/articles/323533a0)；[作者托管原文](https://www.cs.toronto.edu/~hinton/absps/naturebp.pdf)。用于神经网络权重学习的历史语境；不声称它首次发明一般反向自动微分。未转载论文页面。

## 原创实验与图片

全部14张正文图及封面为本篇程序原创绘制，没有AI生成的历史照片、框架截图或第三方人物图。每图职责、尺寸、字体记录见[figure-metadata.json](examples/figure-metadata.json)。

- 图1–8：原创双旋钮例子、局部导数和共享节点图。数值由随文标准库程序实际运行核对。
- 图9：三种微分思路的原创对比图，不是现成工具的产品界面。
- 图10：18次前向差分实际输出的误差图；原始数据同时保留中心差分以供复核。
- 图11–13：模式选择、检查点及绝对值尖角的原创机制图。没有声称实现或测量框架的这些设施。
- 图14：固定y=3时的原函数曲线及两次实际更新结果。

本例所有数据均人为定义、可完整复算。没有真实传感器采样、机器学习训练或第三方数据集。实验代码和图像代码均为本篇新写，没有从所引文档复制实现。

## AI辅助与权利

本篇由AI助手协助研究、组织中文解释、编写原始标量实验与绘图代码，并在本地实际运行、检查数值及图像。文中“实际运行”仅指这些公开可重跑程序，不表示使用过商业训练系统或亲历历史事件。

原创正文、原创图与原创教学数据：CC BY 4.0。原创代码：MIT，见LICENSE-CODE.txt。Noto字体仅用于渲染成图，不随本文分发字体文件。所链接原论文、官方文档及其中图片不因被引用而获得本篇许可。
