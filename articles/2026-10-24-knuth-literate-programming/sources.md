# 来源、素材与复现范围

2026-10-24核查。本篇核心是同一带命名片段的源如何生成不同顺序的程序和文档，不重复本库TeX全局断行文章。

## 一手资料

- Donald E. Knuth，*Literate Programming*，The Computer Journal 27(2)，1984，97–111，[出版记录与摘要](https://academic.oup.com/comjnl/article/27/2/97/343244)。本次实际取得元数据与摘要，完整出版者PDF需要购买，没有读取或绕取，不把摘要核查写成全文审读。
- [Knuth作者CWEB说明](https://cs.stanford.edu/~knuth/cweb.html)：本轮研究阶段实际核读作者页面中WEB与TeX关系、Levy于1987适配C、CTANGLE/CWEAVE两种输出与CWEB范围。写作后再次读取该页发生超时；不宣称复核了即时版本号。本文不用现代版本号，不以作者自述夸大为统计证明。
- [Knuth文学化编程专题页](https://cs.stanford.edu/~knuth/lp.html)：相关著作入口。本文技术机制以作者CWEB说明和独立教学实现支撑，未引用未取得的手册细节。

本文自制格式不是WEB/CWEB兼容实现。实际代码/图/段落是独立例子，不转录这些工具的源程序或手册配图，不把Python教学规则追溯成历史原实现。

## 第三方照片

[originals/photos/knuth-2011.jpg](originals/photos/knuth-2011.jpg)，Donald Knuth真实照片，Alex Handy摄，2011-01-11，Computer History Museum “Revolution”展览开幕活动。[Commons文件页](https://commons.wikimedia.org/wiki/File:Donald_Ervin_Knuth.jpg)，[CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/)，[完整许可](https://creativecommons.org/licenses/by-sa/2.0/legalcode)。复用本仓库已保留合法原件，未裁切、拉伸、修饰或重新压缩，不描述成1984或早期WEB写作现场。该照片继续按其单独许可分享，改编需遵守相应ShareAlike；文章其他独立作品不由此改为CC BY-SA。

## 原创图、程序、真实运行结果

assets/01—12为独立绘制的机制图和程序结果重排图，逐图职责见正文图注与examples/figure-metadata.json。07完整代码来自生成的文件，09/10错误文字来自实际错误测试，11数值来自实际运行错误变体；它们都不是编辑器、终端或历史软件截图。没有伪造界面。

examples/positive.lit是本例的唯一编辑源。tiny_lit.py定义最小解析、展开、文档生成；measure.py实际重新生成generated.py与generated.html，运行正常程序输出8，检查五组输入、缺失引用、循环引用和错误累加变体输出5。results.json记录这些结果与Python版本。格式只支持单定义、整行引用、空格缩进，不支持真实WEB/CWEB的完整特性，不作性能、团队效率或普适软件质量结论。build_figures.py使用Pillow与Noto CJK字体读结果绘图，无随机数。

生成HTML已保存供直接查看。本次用本地Chromium打开file://页面以截取真实文档输出时返回net::ERR_BLOCKED_BY_ADMINISTRATOR；停止该目标，不换入口绕过，未取得截图，也未把示意图伪装成截图。该限制仅影响文档页面截图，不影响本地生成、Python执行或代码图；后续站点浏览检查由整库构建流程另行验证，不在此声称通过。

原创正文、图、示例数据、格式定义、代码与HTML明确采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名文章题名与zyuanming，链接原文、许可并标明修改。第三方照片与外链文献不自动采用此许可。

AI辅助用于来源核对、中文解释、程序实现和执行、原创绘图及修改。未虚构采访、Knuth个人经历、历史现场或实际使用WEB/CWEB的经验。
