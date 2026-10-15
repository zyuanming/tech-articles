# 一手来源与权利

核查日期：2026-10-15。正文的虚拟加热盒、数值、代码、图像与反例均为原创教学构造。不是下列来源的实验数据或图片复制。

- [Lennart Ljung本人2008年Hyderabad讲义，System Identification: From Data to Model](https://isy.gitlab-pages.liu.se/staff/lenlj48/en/hyder/hyderabad.pdf)。封面给出2008-02-22；讲义讨论动态系统、输入输出、模拟与预测、参数化、输入信号与测量选择。支持正文第12节历史/学术语境。真实飞机研究数据属于原讲义，本文未重绘或复制为自己的数据。
- [MathWorks，System Identification Overview](https://www.mathworks.com/help/ident/gs/about-system-identification.html)。支持动态建模需要结构、参数和数据，采样/激励/信噪比与实验设计、模拟和预测的区别。正文的两参数推导与具体数值为自行构造，非官方示例翻译。
- [MathWorks，Specify Estimation and Validation Data](https://www.mathworks.com/help/ident/ug/specifying-estimation-and-validation-data.html)。支持用不同数据估计与验证的工作原则。未使用该产品或复制其界面。
- [MathWorks，What Is Residual Analysis?](https://www.mathworks.com/help/ident/ug/what-is-residual-analysis.html)。支持一步残差、白性/与过去输入独立性的检查思路及OE/IV/闭环等条件差异。本文仅计算明示的样本自相关，未冒称运行官方resid检验。

## 视觉清单

01 稳态相同而冷却不同；02 虚拟加热盒输入/输出实体示意；03 采样时间对齐；04 旧状态保留与输入增量；05 两条参数约束；06 扰动下的记录/预测；07 实际平方误差地形；08 稳态可辨识性不足；09 训练输入输出；10 独立验证输入及输出对比；11 一步预测与自由运行；12 残差时间形状；13 百份扰动的参数散点；14 残差自相关；15 范围外的饱和歧义；独立封面另绘。

本目录没有真实设备照片、第三方工具截图、论文原图、研究者人像或权利不明图片。数学/虚拟实验主体由实际运行数据和原创示意承担；器件示意明确不是实拍。15正文PNG及封面由原创build_figures.py生成；数值曲线由附带expected-results.json读取或根据其中数据计算。

原创中文、教学数据、图像与封面采用[CC BY4.0](https://creativecommons.org/licenses/by/4.0/)，原创代码采用完整[MIT许可](LICENSE-CODE.txt)。外部网页、讲义和品牌仍保留自身权利，本文的许可不再授权它们。

AI辅助研究、撰写、编程、图像制作与验证。无虚构实测、采访、亲历或人工手绘主张。公开附上程序与数据便于重算；私有审读、静态手机排版代理和发布状态不随正文传播。
