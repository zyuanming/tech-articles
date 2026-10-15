# 反向自动微分：可重复的小实验

正文：[read.md](read.md)。所有旋钮、计算图、参数与曲线都属于本文的教学程序，没有真实设备或训练模型。没有安装或运行JAX、PyTorch；对这些框架的讨论依据官方文档，不冒称框架实测。

## 运算模型

x、y及所有输出均为无量纲。u=xy，v=u+x，r=v−10，L=r²/2。主输入是(2,3)，练习输入是(1,2)。固定目标10；实际程序给常量也保留了节点，但正文只讨论可调输入x、y的梯度。

Value类以输入节点和当前局部导数记录依赖。先按对象身份收集拓扑顺序，清零梯度，从最终输出的1开始逆序累加。相同输入的重复使用边不会被去重；同值的不同节点也不会合并。程序适用于本文短小标量图，不实现高阶导数、张量广播或可变值的重新求值；要换输入应重新建图。深层图会受Python递归深度限制。

## 重跑

在文章目录执行：

```sh
python3 examples/run_autodiff.py --output ad-run-01
```

输出目录须尚不存在。程序只用标准库，不联网、不下载、不安装依赖。它生成results.json、finite-difference.csv、stdout.txt。

已保存的原始输出为[experiment-stdout.txt](originals/experiment-stdout.txt)；对应结构化结果在[expected-results.json](examples/expected-results.json)，差分表在[finite-difference.csv](examples/finite-difference.csv)。

实际检查包括：主例6节点数值与梯度、重复求导前清零、w=x*x与z=w+w的重复边、同值异节点；另在x∈{−2,−0.5,0,1,2,3}、y∈{−3,−1,0,2,3,5}的36组组合上，对比独立解析式r(y+1)、rx。没有随机项，没有需要设定的随机种子。

差分实验固定x=2、y=3，h=10^-1至10^-18，共18个步长，同时记录前向和中心差分。前向差分在精确算术中为−8+8h；本例中心差分在精确算术中恰好等于−8。这是二次函数的特殊抵消，不能据此推广一般误差阶。实际表使用Python float，末三项2+h==2。

梯度下降实验固定y=3，仅更新x。步长0.01得到x=2.08、L≈1.4112；步长0.2得到x=3.6、L≈9.68。程序用浮点容差核对这两个非整数结果。

## 重绘

```sh
python3 examples/build_figures.py --output redraw
```

需要已安装Pillow及Noto Sans CJK Regular/Bold字体。脚本读取随文expected-results.json，不访问外部数据。新目录生成assets/下14张正文PNG、独立cover.png和examples/figure-metadata.json。

所有图宽1062像素；最小绘图字号36像素，缩至354像素正文宽时约12像素。图2、14曲线是明确函数L=0.5(4x−10)²的绘制，图10是已保存差分运行结果。其他图是原创机制解释图；图12是内存策略示意，没有执行检查点算法或测量内存。原图不包含平台截图或浏览器验收证据。

本次环境版本和浮点信息见[run-environment.json](examples/run-environment.json)。在其他环境重跑时，差分尾数和PNG编码字节可能受Python、字体、Pillow版本影响；主例解析关系不依赖这些绘图细节。

## 许可

原创正文、14张正文图、独立封面与原创教学数据按[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)发布；原创代码按[MIT](LICENSE-CODE.txt)发布。没有转载第三方图片或论文原页；链接资料各自保留其原权利。出处与AI辅助情况见[sources.md](sources.md)。
