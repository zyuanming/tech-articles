# 可复现的 Count-Min 教学实验

原创代码采用 CC0-1.0；原创输出数据及教学图片采用 CC BY 4.0。实际基线：Python 3.12.14。核心算法与复算仅用标准库；图片生成需要 Pillow 与 fontTools，浏览器截图另需 Playwright 和已经安装的 Chromium。

在本目录执行：

```bash
PYTHONDONTWRITEBYTECODE=1 python run_examples.py
PYTHONDONTWRITEBYTECODE=1 python build_figures.py
```

`cms.py` 是非负整数增量的普通 CMS 核心。哈希函数是调用方传入的；示例使用公开固定映射，不提供生产级随机哈希族。构造接受可迭代的函数集合。`merge` 要求同样宽度及同一组函数对象，是保守的教学配置校验，不是跨进程序列化协议。

`run_examples.py` 重算十二个事件、所有短流、每个合并切分点、单行全部256个随机映射、三行最小误差的精确分布及固定种子的10000次抽样。另用独立的一般线性计数表实际执行B的−2、−4更新，记录每步真实频率、完整表、A候选值及是否出现负频率；该演算不调用拒绝负增量的 `CountMin.add`。结果写入 `results.json`；精确枚举和抽样是两个不同证据。

`build_figures.py` 从结果数据绘制原创结构和实验图，并检查文字范围、重叠、字号、字形、对比及实际像素；保存前按内容裁剪。数据条使用共同尺度，数值由运行结果读取。`figure-metadata.json` 列明图片身份和用途。

真实执行界面可直接运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python demo_web.py
```

它在本地回环地址随机选端口，打印地址；用浏览器打开后点击按钮。页面重新执行 `cms.demo()`，展示实际 Python 输出，精确账本只用于比较，不是 CMS 内部存储。它不是 Redis。

需要重拍截图时，在仓库外的个人环境安装可选依赖，不要把虚拟环境或检查证据写进文章目录。将浏览器可执行路径传给脚本：

```bash
export CMS_EVIDENCE="$HOME/cms-browser-evidence"
PYTHONDONTWRITEBYTECODE=1 python capture_demo.py \
  --chromium /usr/bin/chromium \
  --evidence "$CMS_EVIDENCE"
PYTHONDONTWRITEBYTECODE=1 python build_figures.py
```

截图脚本真实点击按钮、检查返回数据与横向溢出，在1062像素和354像素视口运行。正文图片是1062像素截图；354像素图和运行记录只进入指定证据目录。浏览器字体或版本改变时，截图字节可以不同；数值结果应一致。
