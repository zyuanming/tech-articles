# 来源、数据、实际运行与视觉权利

## 内容范围与学习台阶

核心问题是已知虚拟声源位置后，怎样把同一声音变成左右两条不同的波形。先看实际双耳响应与实体KEMAR，再认识样本/声道/方向/时间/频率，最后用三数字输入推导卷积。旧FFT文章关注频率变换计算的复用，本篇不重复FFT算法；相关概念只解释到能读幅度图的程度。试听和运行脚本均为可选，静态正文可以独立理解。

文中没有声称真人听辨实验、个人听力测量、现场录音、游戏引擎实测或实时头部追踪已经实施。可复算的数值与文件生成，不能代替主观定位研究。

## 一手来源与支撑范围

1. Bill Gardner、Keith Martin：[HRTF Measurements of a KEMAR Dummy-Head Microphone](https://sound.media.mit.edu/resources/KEMAR.html)，MIT Media Laboratory，1994。[完整技术说明](https://sound.media.mit.edu/resources/KEMAR/hrtfdoc.txt)为Technical Report #280，May 1994。官网标注页面1994-05-18、最后修订2000-07-18，不能把网页修订日期写成测量年份。支持KEMAR设备、伪随机测试序列、710位置、44.1 kHz、1.4米，以及测量链、扬声器补偿和compact处理方法。
2. 同项目[FAQ](https://sound.media.mit.edu/resources/KEMAR/KEMAR-FAQ.txt)：Q11双耳共同处理与时差，Q14响应中的测量链与耳机补偿边界，Q17移动方向与卷积，Q18卷积不是逐项相乘，Q19不同采样率应重采样，Q20距离/房间/反射需额外建模。本文响应来自[compact.zip](https://sound.media.mit.edu/resources/KEMAR/compact.zip)，不是完整512样本原始集合。
3. Simone Spagnol、Kristján Bjarki Purkhús、Rúnar Unnthórsson、Sverrir Karl Björnsson：[The Viking HRTF Dataset](https://itsadive.create.aau.dk/wp-content/uploads/2019/05/SMC2019_paper.pdf)，Proceedings of the 16th Sound & Music Computing Conference，2019，pp.55–60。图1实物测量装置，图2耳廓模具制作，图3二十只硅胶左耳廓。论文首页明示CC BY 3.0 Unported，图上未见单列的第三方例外。这里介绍的是2019年另一项研究，不是MIT1994现场；其中十九种耳廓来自博物馆仿真人头模具，另含KEMAR耳廓的硅胶复制品，不能说成二十名真人参与者。论文的个体形状与定位误差讨论支撑通用响应的局限，但本文没有复跑Viking测量或使用其声学数据库。
4. [W3C Web Audio API 1.0](https://www.w3.org/TR/webaudio-1.0/#hrtf-panning)，W3C Recommendation，17 June 2021，§6.3.1/§6.3.2区分equalpower与HRTF。本文引用固定版本的机制描述，并收录§6.3.2 HRTF panner原图；不是声称测试了当前各浏览器实现或推荐某个兼容性行为。
5. [Microsoft Research：Spatial Audio](https://www.microsoft.com/en-us/research/project/spatial-audio/)，研究机构项目介绍，用于游戏已知声源坐标、听者间差异、头部运动与环境空间线索的应用背景。不把机构综述冒称原始人体实验结果，也不复制其无独立开放图片许可的照片。

查询与核读日期：2026-10-13。数学算例、数字幅度曲线、代码与输出为本文自行推导/执行，不是从来源抄录当年的性能表。

## compact输入究竟是什么

输入是MIT compact压缩包中的四个文件，字节保持原样。每个都是556字节的WAV：44100 Hz，16位PCM，双声道，每声道128样本。程序按小端有符号整数读取，除以32768得到数字幅度。

- H0e000a.wav：仰角0°、方位0°。
- H0e090a.wav：仰角0°、方位90°，声源在头右侧。
- H0e180a.wav：仰角0°、方位180°。
- H40e000a.wav：仰角40°、方位0°。

compact是基于左侧小耳廓测量、按镜像方位配对的对称集合，并做扬声器逆滤波/截取。它不是每个方向未经处理、各不相同的左右耳直录。正前、正后、前上40°文件的两个通道逐样本相等，是这组数据构造的性质，不外推到所有人。

128/44100约2.902494毫秒；最后一个点编号127，因此首末点之间127/44100约2.879819毫秒。截取后的时轴不能用来直接读1.4米绝对传播时间。

## 确实执行的计算

使用[原创audio_lab.py](examples/audio_lab.py)，Python3.12.14、NumPy2.3.5。脚本没有联网或录音；输出[results.json](examples/results.json)和五个WAV，运行会覆盖自身目录内同名生成文件。输入原始响应不会修改。

- 原创干声由NumPy默认PCG64生成器、种子20261013构造：90毫秒均匀随机噪声乘Hann窗，四次放在0.2/0.65/1.1/1.55秒。总输入88200样本。不是游戏脚步或第三方录音。
- 对每个方向各做两次完整时间域卷积，产生每声道88327样本。输出保留127格滤波尾巴；不声称实时优化、FFT加速、方向插值或动态混响实现。
- 包括干声在内的所有文件均乘同一个增益约0.0921919340。写入时乘32767、四舍五入为16位整数；重读误差不超过半量化步加浮点容差，峰值约0.2800073。数字不削顶不代表实际耳边声压的保证。
- 右方响应最大绝对峰位置为左42、右5，差37格约0.839002毫秒；按每声道自身峰值5%门限寻找首次越线，得到左30、右3，差27格约0.612245毫秒。后者是明示阈值定义；两者都不冒称唯一生理ITD。
- 右方响应均方根左约0.0290812672、右约0.1420263785，右/左约4.8837754。此数字幅度概括量不等于主观响度或dB SPL。
- 幅度频率图按0到16000 Hz、50 Hz一步，计算有限响应的离散时间傅里叶表达式，再取20log10幅度；对数下限1e-8仅用于避免log0。左右共用数字参考，没有分别归一化。图中只画幅度，不包含完整HRTF的相位信息。
- 手算输入[1,2,0]、响应[1,0.5]得到[1,2.5,1,0]；单位脉冲逐样本复制四套双耳响应。固定独立种子123456的800组随机短数组，双循环定义与NumPy结果最大绝对差3.552713678800501e-15，断言阈值1e-12。
- 五个生成文件全部重新读取检查帧数、声道、采样率、数字范围与量化差。没有声称作者主观听出了每个方向。

试听只是手动HTML audio控件播放已有文件，没有JavaScript音频处理、自动播放、麦克风请求或外部资源。静态图文不依赖试听结果。

## 原链接中的图片范围

MIT主页包含人物照片及导航元素，未给照片明确独立复用依据，未复制；技术说明与FAQ以文字和数学为主，本文取原始数据自行可视化，不生成假的历史实验照片。Viking论文图1—3分别承担本文关键硬件、耳廓制作、形状差异的真实视觉职责，均收录原始JPEG图块，没有截屏、裁切重采样、上色或加中文到原像素。

Viking图4—7是该论文自身测量数据的频率/时延/统计比较；本文不分析或宣称复现那组数值实验，故不把它们混入MIT实际计算结果。保留完整论文链接供读者查阅，避免两套数据身份混淆。W3C §6.3.2唯一HRTF处理原图完整保存；规范的其他音频节点、距离锥等图不在本文接口示例范围内，未整套转载。

## 视觉与每图职责

正文30个图片节点：26张原创解释/实际数据PNG，3幅原始论文照片图块，1张W3C原图。封面另计，照片的面板不拆成多张宣传。主要原创关键标注25—34像素，720像素宽缩到354像素正文宽后约12.3—16.7像素；原始史料小字不冒称中文教学图，其关键含义已在相邻正文及中文大字号图解释。

| 文件 | 新增理解作用 | 原尺寸 |
| --- | --- | --- |
| `assets/01-measured-two-ears.png` | 用公开实测派生数据直观看同一声音到两耳后的差异 | 720×990 |
| `assets/02-pressure-and-samples.png` | 给采样、正负数字与声道一个视觉基础 | 720×780 |
| `assets/03-real-and-virtual.png` | 分开物理耳机位置与虚拟声源知觉，不承诺必然外化 | 720×780 |
| `assets/04-directions.png` | 明确MIT方位角与仰角，避免与图形引擎轴约定混淆 | 720×760 |
| `assets/05-time-difference.png` | 先用自设声程差解释亚毫秒时间差，不把简化路线冒充声学仿真 | 720×760 |
| `assets/06-onset-is-a-choice.png` | 用同一文件区分门限起点与最大峰，限制时间差解释 | 720×800 |
| `assets/07-frequency-foundation.png` | 解释频率单位，为频谱和频率相关的头影建立前提 | 720×800 |
| `assets/08-measured-frequency-left-right.png` | 实际左右频率曲线揭示非恒定音量差 | 720×820 |
| `assets/09-decibels-as-ratios.png` | 把频谱纵轴的对数单位降为可比较的幅度倍数 | 720×760 |
| `assets/10-paths-add.png` | 为耳廓多路径与频谱缺口提供相位相加的直观前提 | 720×850 |
| `assets/11-elevation-spectrum.png` | 实际前方与前上方频谱对比，展示上下方向不只是左右音量 | 720×820 |
| `assets/12-front-back-response.png` | 前后方向的左右相等反例，明确本数据的镜像构造 | 720×920 |
| `assets/13-measurement-chain.png` | 明确响应来自测量与处理，区分输入信号和恢复的脉冲响应 | 720×920 |
| `assets/14-unit-impulse.png` | 给脉冲和系统响应一个无连续数学的起点 | 720×780 |
| `assets/15-scale-and-delay.png` | 先说明线性叠加与固定系统前提，再使用卷积 | 720×820 |
| `assets/16-convolution-ledger.png` | 用移位缩放的四列账本逐个得到卷积输出 | 720×920 |
| `assets/17-output-tail.png` | 解释卷积输出长度与滤波尾巴，不丢最后样本 | 720×780 |
| `assets/18-two-convolutions.png` | 把一维手算提升为双耳输出的实际算法结构 | 720×850 |
| `assets/19-rendered-noise.png` | 展示实际生成输出，不用概念图代替真实运行结果 | 720×910 |
| `assets/20-time-and-frequency.png` | 明确HRIR与HRTF是相关表示，幅度图并非完整传递函数 | 720×880 |
| `assets/21-gain-is-not-hrtf.png` | 固定增益和延时无法重现实际频率幅度变化的反例 | 720×760 |
| `assets/22-common-gain.png` | 真实响应RMS比例说明双耳应共同缩放而非独立归一化 | 720×790 |
| `assets/23-head-tracking.png` | 用两个静态状态说明头部追踪为什么要更新相对方向 | 720×810 |
| `assets/24-game-audio-chain.png` | 放回游戏音频全流程，区分双耳方向、混音与环境层 | 720×960 |
| `assets/25-sample-rate-matters.png` | 用同一27样本间隔反例解释重采样与改标签的区别 | 720×760 |
| `assets/26-three-cues.png` | 收束时间、强弱、频谱三个层次的不同职责 | 720×790 |
| `originals/viking-fig1-setup-original.jpeg` | 2019另一研究的测量装置与KEMAR实体 | 2500×2133 |
| `originals/viking-fig2-mould-original.jpeg` | 实体耳廓模型的制作材料与步骤 | 958×1187 |
| `originals/viking-fig3-pinna-original.jpeg` | 不同耳廓形状的实体对比 | 2000×1500 |
| `originals/w3c-hrtf-panner-original.png` | 真实规范中的HRTF双路卷积架构 | 644×419 |

写前逐节视觉清单已按最终阅读顺序落实。第2—8节先讲可见坐标与单位再读频谱；第9—12节照片、实际响应与处理链交替；第13—17节脉冲、缩放、移位、逐列求和、尾长、双路输出连续推进；第18—25节实际输出、表示差异、反例、个体照片、头转、游戏层次与采样率分别有对应图。第16节沿用上一节同一个账本，额外图解释输出尾长，不为了每个公式重复画表。

## 权利与署名

原创正文、原创解释图、封面、合成干声和原创计算输出贡献采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名“tech-articles 原创探索文章”，附原文、许可与修改说明。原创脚本与试听页面代码采用[MIT许可](examples/LICENSE.txt)。本篇使用AI辅助研究、写作、编程和制图；照片是原论文实物照片，不是生成图；波形是明确数据/程序结果，不是生成伪测量。

MIT输入数据Copyright 1994 MIT Media Laboratory，署名Bill Gardner与Keith Martin；官网允许免费使用并要求研究/商业使用时引用作者。完整数据通知保存在[MIT-DATA-NOTICE.txt](originals/MIT-DATA-NOTICE.txt)。派生曲线与方向音频同样明确保留来源署名，不声称MIT为本文背书。

Viking三幅照片：Copyright 2019 Simone Spagnol et al.；作者完整名单见上述文献，许可[CC BY 3.0 Unported](https://creativecommons.org/licenses/by/3.0/)。由作者公开PDF提取原JPEG对象，未改变像素；网页仅按版面缩放显示。来源为同一论文的图1、图2、图3。本文中文解释是新作，不是原作者的官方译文或背书。

W3C图：Copyright © 2021 W3C®（MIT、ERCIM、Keio、Beihang）。依据[Software and Document License 2015](https://www.w3.org/copyright/software-license-2015/)使用，原文件不改像素，完整许可、免责与修改声明保存在[W3C-NOTICE.txt](originals/W3C-NOTICE.txt)。上述材料不会因本文正文采用CC BY 4.0而改变原有权利。

## 随文原文件身份

- [H0e000a.wav](originals/H0e000a.wav)：556字节，SHA-256 `da4313c9ad89eb816930a3539e80f96f54887b857515fde537dcf6d4bc23bc46`。
- [H0e090a.wav](originals/H0e090a.wav)：556字节，SHA-256 `8b55a165d65d7d3651dc99ec739d9480ad9260165720f9142a7e7e25f7b6d40c`。
- [H0e180a.wav](originals/H0e180a.wav)：556字节，SHA-256 `3a9ee49bf72a93cb295a7700b90b786a23c919cc56e5d23c35b1247f97957aed`。
- [H40e000a.wav](originals/H40e000a.wav)：556字节，SHA-256 `591309f09c758c0df2d80622f92bf05cb681dbff37018e11599917b0ffdb0f0e`。
- [viking-fig1-setup-original.jpeg](originals/viking-fig1-setup-original.jpeg)：294106字节，SHA-256 `c99cbf74a69ae82d4eb0b54cf6e732f74862000914df2eebea7c8fc0a1158ba1`。
- [viking-fig2-mould-original.jpeg](originals/viking-fig2-mould-original.jpeg)：85041字节，SHA-256 `e3928cc824ce96c8ff945c62958182b90df9f55b231df1e6c6979ae429ea250a`。
- [viking-fig3-pinna-original.jpeg](originals/viking-fig3-pinna-original.jpeg)：145773字节，SHA-256 `b6be4cadf1d97621f37d9b92a867c5d08d9b24a186a21aba12d7904dd4d2900c`。
- [w3c-hrtf-panner-original.png](originals/w3c-hrtf-panner-original.png)：16473字节，SHA-256 `5cbf84a55d0cc38aa72d2b53fe65e49849258d51c70574e19bab90a4d3b4c72a`。
