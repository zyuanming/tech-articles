# 可复现的法线换基与软件渲染

代码与原创结果数据：CC0-1.0。输出教学图：CC BY 4.0。第三方截图按上级来源附页许可。这里不是 glTF 加载器、MikkTSpace 实现或完整 PBR 渲染器。

在本目录运行（Python 3.12，Pillow、fontTools；截图另需 Playwright 和系统 Chromium）：

```sh
python run_examples.py
python capture_demo.py
python build_figures.py
```

`normal_map.py` 提供单三角基、解包、变换和CPU渲染。`run_examples.py` 写出 `results.json` 与 `output`。随机检查只有一组，独立 `Random(20261025)`，1000组绕Z轴旋转往返；结果还包含主例、8位量化、镜像、退化UV、过滤、scale、非均匀缩放垂直性验证。

`demo_web.py` 运行后打印本地端口；点击按钮会重新执行 Python 算式及CPU图像。`capture_demo.py` 使用系统 `/usr/bin/chromium` 的默认启动配置；验证返回数据和354/1062视口宽度后截图，不读取远端网页。截图展示的是当前运行的Python版本。`build_figures.py` 使用系统 Noto Sans CJK 字体生成原创图，记录 `figure-metadata.json`；原图16只作字节复制，不重编码。

固定输入：主例理想RGB(.68,.74,.9)，T=(0,1,0)，B=(-1,0,0)，N=(0,0,1)，L=(-.48,.36,.8)。理想向量长度已为1；量化后再归一化，不能混用两者结果。

另一套图像实验：96×96，XY单位正方形，固定正交相机从+Z朝向表面；u右、v下，T=+X、B=−Y、N=+Z、w=−1。高度函数只用于生成法线，几何不位移。频数4、幅度.025；像素中心取样；原法线量化8位，纹理用最近邻。旋转分支绕世界Z90°，屏幕坐标先逆旋转回UV，T/B正旋转；`rotated-wrong`故意直接把局部分量当世界方向，遗漏整个TBN，不仅是漏旋转。

灯是normalize(.6,.4,1)，换灯分支为normalize(−.6,.4,1)。材质线性RGB(.42,.58,.72)，因子.08+.92×max(0,n·L)，其中.08为人为常量项。输出按sRGB分段函数编码、四舍五入到8位。没有阴影、镜面、曝光映射、透视或物理光强测量。

`output/normal-map-data.png` 无sRGB标记，字节就是数据，读取时除255后2c−1；其他输出PNG与教学预览是显示颜色并写入sRGB块。不要把预览PNG重新当已正确配置的引擎数据纹理。

记录环境：Python 3.12.14。各图/输出的实际尺寸和数值都随结果文件公开。教学代码偏重可追溯性，未优化速度；不把1000组有限检查当数学证明。
