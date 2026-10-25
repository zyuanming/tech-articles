# 可复现的sRGB计算与图像处理

原创代码CC0-1.0，原创结果数据及图00—15采用CC BY 4.0。图16依据W3C示例条件重计算，按文章来源附页保留W3C许可，不把其示例条件改授为本库原创授权。

实际环境：Python3.12.14，Pillow12.3.0，fontTools4.61.1；浏览器为已安装的Chromium，通过Playwright调用。核心算术和结果JSON只需要Python标准库，制图需要中文字体、Pillow、fontTools。代码域限于有限0..1，非完整HDR或色域转换库。

在本目录执行：

```bash
PYTHONDONTWRITEBYTECODE=1 python run_examples.py
PYTHONDONTWRITEBYTECODE=1 python build_figures.py
```

`srgb.py`实现精确分段encode/decode、四舍五入8位量化和教学混合。`run_examples.py`实际输出所有曲线、像素、二维缩小、滤波、alpha、预乘、量化和近似误差数据；没有拿显示器作物理测量。往返采样1001点、所有256个8位码、1280组混合及6个阈值邻点检查。阈值有限常数存在细小不连续，容差明确，未声明所有实数精确互逆。

`build_figures.py`读取JSON生成图00—14及来源附图16，检查字形、文字边界/重叠/字号、对比、像素与尺寸。实际处理效果按最近邻放大展示，避免展示阶段另加滤波。每幅PNG写入sRGB chunk（rendering intent0）；它声明已计算好的像素编码身份，不替代encode。`figure-metadata.json`记录图身份和用途。

真实运行页面：

```bash
PYTHONDONTWRITEBYTECODE=1 python demo_web.py
```

只监听本地回环地址的随机端口，打印地址后在浏览器打开、点击按钮。服务器实时调用核心公式，不是预制终端图。

可用已安装的浏览器重拍：

```bash
export SRGB_EVIDENCE="$HOME/srgb-browser-evidence"
PYTHONDONTWRITEBYTECODE=1 python capture_demo.py \
  --chromium /usr/bin/chromium \
  --evidence "$SRGB_EVIDENCE"
PYTHONDONTWRITEBYTECODE=1 python build_figures.py
```

截图脚本在1062/354视口实际点击，核返回值、无横溢/JS异常，并读取色块中心像素128/188；给截图补sRGB chunk时断言全部像素字节不变。1062截图用于正文，354截图和浏览器执行记录只保存在指定仓库外目录。字体/浏览器版本改变可改变截图字节，不改变数学预期。
