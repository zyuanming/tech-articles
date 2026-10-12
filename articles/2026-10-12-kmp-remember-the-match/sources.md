# 来源、图像与可重复实验

原创中文正文由zyuanming发布，采用CC BY 4.0；第三方图片继续遵守各自许可，不并入统一正文许可。本文使用AI辅助研究、写作和校验。22张教学图按明确字符位置、比较记录和状态值编程绘制，是原创算法示意，不是旧计算机屏幕或历史现场照片；两张人物照片保存所下载原文件的原尺寸与原字节。

## 一手资料与事实范围

1. Donald E. Knuth、James H. Morris Jr.、Vaughan R. Pratt，*Fast Pattern Matching in Strings*，SIAM Journal on Computing，6(2)，323—350，1977年6月。[期刊记录](https://epubs.siam.org/doi/10.1137/0206024)；[约翰斯·霍普金斯大学托管论文](https://www.cs.jhu.edu/~misha/Spring23/Knuth77.pdf)。实际阅读印刷页323—328的开篇、朴素搜索与改进算法发展，338—339的历史章节，另查看331与334以核对两幅编号图及算法边界。没有声称逐页读完28页，也不将本文称为原论文翻译。
2. 同一论文第7节是本文历史段的直接依据：Morris在1969年夏为CDC 6400文本编辑器寻求无需让文件输入回退的方法；Knuth在1970年从Cook的理论结果提炼算法；Pratt改进结构并与Morris交流。它是作者回顾，不是本稿作者亲历。1977是期刊发表年，论文还列出更早的报告。本文没有补写现场对白，也不把共同发现改成某一人的单独发明。
3. [Carnegie Mellon University，Heidi Opdyke，2018-05-04](https://www.cmu.edu/news/stories/archives/2018/may/morris-computing-pioneers.html)，*Former SCS Dean Shares Personal History With Computing Pioneers*。用于核对James H. Morris Jr.的计算机科学家身份与KMP共同发现者身份，给读者进一步阅读其本人讲座回顾的入口。未采用报道里与本文无关的个人经历或名言。
4. [Python官方Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)与[Unicode Standard Annex #15：Unicode Normalization Forms](https://www.unicode.org/reports/tr15/)。支持码点序列、组合字符与规范化的区别。本文的搜索器不做规范化、大小写折叠或字素簇切分；不声称规范化后的下标能直接映回原字符串。

## 原论文信息图与覆盖边界

正文核心是单模式匹配的状态复用。原论文323—328页的行内字符对齐、表项与程序展示，由本稿自设ABABABACABA / ABABACA例子的03—12图和代码重新推导，不复制论文排版、截图或原例文字。本文采用从0编号的现代前缀函数pi；论文采用的优化next与其下标约定不同，数值不能直接互抄。

原Fig.1（331页）是多模式trie转移表，Fig.2（334页）是周期性字符串结构论证，均属于本文没有展开的另一层问题，故不加入正文。读者可以在完整原论文中查看。没有核到该论文扫描页可在本公共素材包再分发的开放许可，所以不收录扫描图；不能把大学网页可下载误当成开放授权。334页还明确讨论用较简单回退函数时，单个文本字符可触发多次比较；本稿14图给出另一组独立反例，不给教学代码套用优化版本的逐字符延迟保证。

## 两张人物原图

- `assets/knuth-2011-original.jpg`，2256×1496，940501字节。Alex Handy，*Donald Ervin Knuth*，2011-01-11在Computer History Museum的Revolution展览开幕活动摄。[Commons文件页](https://commons.wikimedia.org/wiki/File:Donald_Ervin_Knuth.jpg)，[可下载原件](https://upload.wikimedia.org/wikipedia/commons/0/07/Donald_Ervin_Knuth.jpg)，[CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/)。未裁切、未改色、未修改。这不是1969或1970年的照片。下载字节的SHA-1为`6fc5fe956f31609be9b59b83dc084bd04d01bdb9`，与文件页记录一致。
- `assets/pratt-2009-original.jpg`，1102×1424，1012018字节。Vaughan Pratt自摄；[Commons文件页与版本历史](https://commons.wikimedia.org/wiki/File:VaughanPratt.JPG)，[当前原件](https://upload.wikimedia.org/wikipedia/commons/b/b2/VaughanPratt.JPG)，[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)。页面概述仍保留早期日期，但替换照片的历史记录及当前文件EXIF指向2009-07-31；Bubba73于2016-03-19作色彩调整。本稿采用该当前版本，保留原字节，未再次修改；不把“我未修改”写成“这张图从未修改”。当前文件SHA-1为`d56eb5fb8af5b93497dad8b8d7e05569c693a3e6`，已实际核对。

两图各自保留署名、标题、来源和许可；按版面缩放显示不替换仓库原件。若再改编图片，须遵守对应相同方式共享许可及其完整条款。人物、摄影者、机构均未被宣称为本文背书。

Morris人物肖像已主动查看CMU的对应人物报道；未核到适用于本稿的开放复用依据，故只给原站查看链接，不下载用于公开稿，不拿英国同名政治人物的照片替代。本文是算法原理探索，不用缺乏依据的生成肖像填补人物位置。Knuth另一个427×505候选图没有被放大冒充高分辨率原件，最终采用上述2256×1496原图。

## 24幅图的职责

01明确连续匹配与从0编号；02重复工作；03具体失配；04保留的事实；05真前后缀；06安全跳过；07同一个文本字符；08结束位置与起点；09pi表；10建表延长；11建表回退；12严格变短的链；13摊还总账；14单字符多次比较；15两组明确输入的计数；16重叠匹配；17空模式；18跨块状态；19码点序列；20接口合同；21历史路径；22手算练习。加上两张人物原图，共24幅。

15图两组横条采用各自的像素比例，不能跨组直接比较条长；数值与正文一致。13图画的是状态值的变化，不是耗时曲线。所有字符格、指针、回退箭头及pi值均按正文例子计算，不是装饰性伪终端截图。

## 可以实际运行的实验

[标准库Python程序](examples/kmp_experiment.py)包含前缀函数、记录比较次数的单次搜索、朴素对照与跨块StreamMatcher。实际运行范围：

- 二进制文本长度0—9、二进制模式长度0—6，共129921对输入，全部命中位置与朴素对照一致；有限穷举不是对无限输入的证明。
- 主例匹配[2]，搜索比较12次，对照19次；40个A对AAAAB为76次与180次；AAAAAC对AAAAAB为11次与6次。计数不含建表，没有墙钟跑分，也不据此评价Python内置搜索。
- AAAAA / AAA得到[0,1,2]；ABABCABABCAB / ABABCAB得到[0,5]；另核汉字码点输入与空模式边界约定。
- 主例全部78种三块切分，包括空块，均返回起点2。StreamMatcher只接受非空模式，模式表占O(m)空间；不保存全部历史文本。此结论不包括外层解码缓冲或收集全部输出的位置列表。

程序运行后会在同目录写出本次结果JSON，便于自己核对；文中结论来自实际执行，不是假装在线服务实测。Python代码为本稿原创教学实现；不套用原论文程序的版权或性能结论。
