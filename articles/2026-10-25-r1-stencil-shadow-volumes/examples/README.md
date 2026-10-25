# 可复算的阴影体教学模型

Python 3.12；本次运行 NumPy 2.4.6、Pillow 12.3.0。制图另用 fontTools 及 Noto Sans CJK 字体。建议创建虚拟环境后安装依赖；代码不代替完整图形引擎。

```sh
python -m pip install numpy pillow fonttools
python shadow_model.py
python build_figures.py
```

从本目录执行。`shadow_model.py` 生成 `results.json` 及 `output/` 内 27 张 160×128 原始 RGB PNG。没有随机数。图像颜色为 sRGB；计数图颜色只是可视映射，不把整数当光强。背景不纳入有效表面误差统计。

每个像素只有一条解析眼线，采用三角形求交和有向计数；独立遮挡真值是接收点到灯的线段／轴对齐盒相交。没有 GPU 光栅化、MSAA、速度测量，也不模拟硬件共边覆盖约定。恰好重复命中体三角剖分共边会触发断言，不能用重复交点拼凑正确答案。

空间单位任意；盒子、灯、相机、50°垂直视场与最近射线距离0.05在源码中明确。阴影体为有限k=20构造，前盖来自朝灯面，后盖来自这些面远移后反转，侧面连接轮廓边。逐边检查闭合和反向绕序。这不是把GPU Gems某段代码直接换语法，也不是无穷远齐次坐标实现。结构图另用k=2展示，实际数据保存于 `illustration_far`。

一维例在单独的坐标t上计算，不能把t=2、6当成三维盒的坐标。穷举484例、三维三个视图的48,964个有效采样输出均在JSON内；正文所列故意错误模式也由实际运算生成。`other-light-no-far-cap.png`是换灯后的删远盖反例，不能与原灯的正常图混作同条件对照。

启动本地查看器：

```sh
python ui.py --port 8080
```

浏览器打开 `http://127.0.0.1:8080/`，切换三个视角／灯光结果。它只显示已经算出的文件，没有声称实时GPU渲染。可选截图脚本需要Playwright与已有的Chromium：

```sh
python -m pip install playwright
python capture_ui.py --chromium /path/to/chromium
python build_figures.py
```

脚本只启动本地HTTP查看器，使用浏览器默认启动选项，实际切换并断言结果，然后保存正文截图；它不安装浏览器、不修改安全设置。图形字体文件候选不存在时制图直接报错，不能以缺中文字形的占位图继续。

代码 CC0-1.0；原创 JSON 数据 CC0-1.0；生成的教学图、原始模型图及界面截图 CC BY 4.0，署名 zyuanming。Pillow、NumPy、fontTools、Playwright及字体分别按其自身许可使用，未将其源码或字体打包进本文。
