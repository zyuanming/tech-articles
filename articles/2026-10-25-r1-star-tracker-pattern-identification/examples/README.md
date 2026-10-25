# 复算本篇的两条链

这里分别提供原创教学模型和固定版本tetra3的真实输入运行。它们没有共享星表，也没有把TRIAD当作tetra3的实现。

## 教学计算与新图

测试环境：Python 3.12.14、NumPy 2.4.6、SciPy 1.17.0、Pillow 12.3.0、fontTools；绘图需要Noto Sans CJK字体。先进入本目录，执行：

```sh
PYTHONDONTWRITEBYTECODE=1 \
python run_examples.py
```

程序输出results.json与synthetic-sensor.tiff。没有随机输入或随机种子。合成图宽1024、高768；固定背景10、四个3×3信号块、一个亮孤点。代码里的centres、gains、patch与parameters给出完整输入。星斑净信号阈值为大于0，连通团至少3像素，星表匹配角容差0.005°、额外星验证半径2像素，均为此模型的教学选值。该无噪声阈值不适用于真实传感器。

像素中心采用整数(u,v)，u右、v下；相机右手系x右、y下、z前。单位射线是((u−cx)/f,(v−cy)/f,1)归一化。天空参考系也是右手系。用Rz(30°)Ry(20°)Rx(10°)生成真实候选，列向量先施最右旋转；另一处三角再绕天空z轴转100°，第四星额外偏移60、20像素以构成可排除的反例。

断言核对质心、恰好两个三角候选、六种顶点对应、第三射线经正旋转后的角残差、第四星仅留下正确候选、恢复所设旋转、正交性与行列式+1、变换相机后角距不变。近轴0.1像素误差和错误焦距1600像素另作已标明的局部反例。JSON保留全精度，正文仅四舍五入。

## 真实测试输入与固定软件

另行准备[ESA tetra3原仓库](https://github.com/esa/tetra3/tree/f9fa2eb9a32a5efc529e2d86f0b59f35b1e9028d)在commit `f9fa2eb9a32a5efc529e2d86f0b59f35b1e9028d`的本地副本；遵循该项目安装与数据条件。本篇不另分发默认数据库。将TETRA3_SOURCE设为该副本目录，然后执行：

```sh
PYTHONDONTWRITEBYTECODE=1 \
python run_tetra3.py \
  "$TETRA3_SOURCE"
```

包装器不联网。它先核源tetra3.py、默认数据库、README、LICENSE及两输入TIFF的SHA-256，防止不同版本冒充固定版本。只在一次性副本添加标准库math导入，并把两处`np.math.factorial`换成`math.factorial`以兼容NumPy 2.4.6；原副本保持字节不变，没有修改匹配算法。采用distortion=[−0.2,0.1]、solve_timeout=30000毫秒、return_visual=True、return_images=True；其余是该固定版默认参数。

注意坐标接口不同：tetra3质心数组每行为(y,x)，坐标相对左上角，像素中心带0.5偏置；本篇教学例是整数中心(u,v)。真实图原样保存软件返回，未把教学坐标套到它的内部相机坐标。软件中的FOV返回值是水平视场；README的标称11.4°没有定义轴向。

两次实际求解得到11、16个匹配及约6.4606、5.0244角秒内部RMSE。real-results.json记录有限结果、原输入SHA、显示分位界限与版本，不包含原星表记录、私有路径或耗时。耗时随机器改变，不是可逐字节复现的性能结论。不同依赖/平台可能有细微浮点差异，应同时比较数值容差与图义，不能拿哈希不相等直接断言算法失败。

real-alt40/60-display采用全幅线性分位拉伸；matches是软件新建黑底结果画布，centroids是软件以16位整除256显示后加标记的图。它们不是同一种亮度处理。包装器另存Alt40原返回的removed_background（float32）及binary_mask（bool）到real-alt40-stages.npz，并将参数、阈值、显示界限和像素计数写入同名JSON。默认25×25局部均值扣除、全局均方根的2倍阈值、binary_open=True；后者是二值掩码开运算，返回掩码包含此步骤。新图16按1%/99.9%分位显示去背景数组，二值真/假显示为255/0；全幅最近邻缩览，区域x=[236,276)、y=[278,318)最近邻放大12倍。它保留原算法计算的像素，不是手绘中间态。

新图生成器另外从第一张matches保真裁取x=[150,470)、y=[210,390)，最近邻放大3倍作中文图例。

完成上面两条链后执行：

```sh
PYTHONDONTWRITEBYTECODE=1 \
python build_figures.py
```

此步骤从results.json取模型数字与定量坐标；布局坐标、图号、概念性的示意夹角为绘图常量。条形共用比例并核排序；文字检查字形、边界、声明框、重叠、至少40像素字号、对比和墨迹；figure-metadata.json记录实际尺寸与身份。照片/软件原返回中的小标记保留原貌，用正文与局部放大解释，不把它们冒充40像素新标注。

如需保留本次文件，请先复制整篇到自己的复算目录，再运行；三个脚本会写入其所在文章的examples及assets。原始TIFF与上游许可副本不由这些脚本修改。

新写代码、合成数据与虚构星表为CC0-1.0；真实原件、真实阶段数组及软件派生图保留Apache 2.0来源，具体通知和边界见[来源说明](../sources.md)。两原TIFF在originals/photos，合成输入synthetic-sensor.tiff只是教学数据，不能混称第三张实拍。
