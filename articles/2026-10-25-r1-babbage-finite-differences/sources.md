# 来源、图像职责与许可

> **公开状态：待补真实素材稿，整体仍为 HOLD。** 2026-10-26 先公开现有稿件，不代表真实素材缺口已解除或独评已正式通过。尚缺可辨认的真实差分机整体、数位或机构局部及相关历史输出素材。现有图是数学与机械数位的教学表示，不是实机照片、原机构图纸或历史制表实物。

核验日期：2026-10-25。

## 事实来源与支持范围

1. [Computer History Museum，The Engines](https://www.computerhistory.org/babbage/engines/)。机构对其专题展览对象的说明；支持十进制数位轮、差分机与分析机的区别、二号设计时期、31位与七阶能力、1832年一号完成部分、自动打印与制版意图。已读取该页全部解析文字；未取得原HTML或原图像素，不把文字图注当成图像审视。本文不采用其中对一号工程停工年的细节，以免将两馆不同的停工年份记述混并。
2. [CHM，How it Works](https://www.computerhistory.org/babbage/howitworks/)。已读取全部解析文字，包括 x²+4 的差分法教学例及寄存器说明。来源的末端差分延长顺序不等于本文同行向前差分的就地更新次序。本文换用新多项式独立推导，没有复制馆方图版，也没有把本篇Python顺序当成原机机械相位。
3. [Science Museum，Charles Babbage’s Difference Engines and the Science Museum](https://www.sciencemuseum.org.uk/objects-and-stories/charles-babbages-difference-engines-and-science-museum)。馆藏及现代建造项目的机构记述；支持数表任务、1832年完成部分、1847—1849设计期、1991计算部分与2002打印机构的区别，以及手摇动力。已读取全部解析文字与图注；原图像素及完整HTML图像列表未取得。本文不采用未能独立核实的轶事对白、损失估算或动机推断。
4. [CHM，2008年5月5日新闻稿](https://computerhistory.org/press-releases/babbage-engine-exhibit/)。同时代机构公告，支持第二台现代二号差分机的2008年5月10日开幕及现场演示安排。不是作者的观展记录，也不是现代装置的计时数据。已读取全部解析文字；原页面图片未取得。

以上页面提供史实和原图定位，公开可见并不等于图像有开放许可，故不复制未明确授权的馆方图片。未查阅链接出去的技术手册全文，不借手册标题声称掌握进位机构细节。

核心原页相关图、公式、效果的逐项采用/排除理由见[来源视觉库存](source-visual-inventory.md)。

## 实物视觉来源与取得边界

下列是不同摄影作品，各自有明确的来源页许可说明，但本次原文件取得均受访问限制；没有保存、转载或以缩略图冒充高清原件。它们仍是未补齐的实物视觉，不能由原创框图抵销。

| 作品与作者 | 来源页所列权利与原尺寸 | 本文使用情况 |
|---|---|---|
| [Babbage Difference Engine.jpg](https://commons.wikimedia.org/wiki/File:Babbage_Difference_Engine.jpg)，Geni，2008年9月 | 作者提供多重许可，可选[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)；3503×2535 | 原像素未取得，不转载 |
| [Babbages difference engine 1832.jpg](https://commons.wikimedia.org/wiki/File:Babbages_difference_engine_1832.jpg)，Sebastian Wallroth，2001年10月14日摄影 | 作者放弃至公有领域，并提供法律不允许放弃时的无条件使用授权；原始上传版本1280×960 | 目标是2008年原始上传版本，非2012年第三方修图；原像素未取得，不转载 |
| [Difference engine.JPG](https://commons.wikimedia.org/wiki/File:Difference_engine.JPG)，Allan J. Cronin / Canticle，2009年3月 | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)可选；3597×3139 | 原像素未取得，不转载 |
| [Charles Babbage’s Difference Engine No. 2](https://commons.wikimedia.org/wiki/File:Charles_Babbage%27s_Difference_Engine_No._2_(2586166238).jpg)，Erik Pitti，2008年6月12日 | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/)；2816×2112；来源为摄影者Flickr作品 | 原像素未取得，不转载；照片描述中的1837设计年未采用，历史日期以机构资料为准 |

这里列的是照片作者的权利声明和摄影元数据，不是给本文附加第三方照片授权。实际补入照片时仍须保留原件、完整署名、适用通知及修改说明，并重新核验照片中的对象与本文图注。

## 本文新图

所有PNG为全新原创教学图，数值由 `examples/run_examples.py` 实际生成并从 `results.json` 读取。它们不是截图、设备实拍、历史图纸或历史原机实测。图片宽1062像素；设计字号及身份见 `examples/figure-metadata.json`。

| 图 | 新增理解作用 |
|---|---|
| 00-cover | 独立封面，把公式与下一步四格状态连接 |
| 01-direct | 展开立方乘算，让最初四个函数值有来路 |
| 02-table | 固定前向差分行位置，并显示三阶恒定 |
| 03-update | 展示一次推进中每次写回后的混合状态 |
| 04-order | 同样初值反向写回，明确错误16的由来 |
| 05-registers | 一个状态数与多个十进制数位之间的区别 |
| 06-carry | 由实际加法事件拆解073+063的进位 |
| 07-errors | 三阶初值多一后，误差跨多步逐阶传播 |
| 08-overflow | 同例到三位容器边界，高位丢失不等于数学失效 |
| 09-step | 相同公式在步长变化后需要新的初始差分 |
| 10-boundary | 指数数列没有在有限阶差分后恒定的反例 |

当前没有第三方照片文件，`originals/photos/`无可交付原件；“整体装置＋可辨数位/机构细节”的真实视觉义务尚未满足。

## 复算、AI辅助与许可

主例是整数多项式 y(n)=n³+2n+1；数表、所有差分、状态变更和反例都实际执行。另有205组起点/步长、每组30项的6150次精确整数比对。十进制加法示范仅为非负三位教学容器；负起点测试只属于Python整数多项式递推，不是负数齿轮编码。没有随机采样、性能计时、真实装置测量或浏览器截图。

AI参与了选题细化、公开来源检索、正文推导与写作、程序和图像生成、自检。来源中的历史事实与本篇独立算例明确区分，没有生成或声称生成历史实拍。

正文与全部原创PNG采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名zyuanming。代码及本篇原创计算JSON采用[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/)。Canvas检查API来自本仓库已标CC0的r1 Quickselect生成器，构图、标注及数据为新制作。外链第三方作品保留各自权利，不适用本文统一许可。
