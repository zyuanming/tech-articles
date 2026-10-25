# 外部归并的可复现文件实验

原创代码 CC0-1.0，原创结果数据与教学图 CC BY 4.0。实际执行基线为 Python 3.12.14。算法只用标准库；制图需要 Pillow、fontTools 和中文字体，浏览器截图另需 Playwright 与已安装的 Chromium。

在本目录运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python run_examples.py
PYTHONDONTWRITEBYTECODE=1 python build_figures.py
```

`external_sort.py` 读写固定八字节记录（小端uint32键、uint32原序号），先对受限批次排序，再逐文件读块进行多路归并。工作目录必须为空；实验只创建自己的临时输入及中间文件，不覆盖用户文件。原输入保留。孤段也复制到新一代，全部中间代保留到实验助手退出时一起清理；这不是磁盘空间最优策略，也没有事务持久性保证。

`run_examples.py` 实际创建文件、调用排序核心，再用独立全量排序基线验证。生成测试键列表、读取最终输出与基线排序会占全量小实验数据内存，不纳入核心内存分析。小主例开启完整轨迹以绘图；较大用例关闭轨迹。核心仍存run路径列表，其元数据随段数增长；Python对象、堆、文件库缓冲都不包含在正文64字节抽象数据槽预算内。

主例24条、每段6条、每块2条、三路；较大例10000条、每段256条、每块32条、八路，使用独立`Random(20261025)`。另外364个穷举小输入和81个随机文件用例，共445个。程序统计非空应用块及实际字节，不统计空EOF探测、实验输入生成、校验读取，也不声称测量系统调用或物理磁盘传输。结果写入`results.json`，生成器从结果读取数值和数量驱动几何。

真实教学界面：

```bash
PYTHONDONTWRITEBYTECODE=1 python demo_web.py
```

打开它打印的本地回环地址，点击按钮重新进行自建文件实验。界面不展示私人路径。需要重拍正文截图时，将证据保存在仓库之外：

```bash
export MERGE_EVIDENCE="$HOME/merge-browser-evidence"
PYTHONDONTWRITEBYTECODE=1 python capture_demo.py \
  --chromium /usr/bin/chromium \
  --evidence "$MERGE_EVIDENCE"
PYTHONDONTWRITEBYTECODE=1 python build_figures.py
```

截图脚本在1062和354像素视口真实点击、检查返回阶段计数和横向溢出；1062像素截图作为正文图，其余截图与检查记录仅写到指定证据目录。重现数字不依赖浏览器像素完全相同；字体/浏览器变化可能改变截图字节。
