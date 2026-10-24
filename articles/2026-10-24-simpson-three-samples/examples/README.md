# 复现

Python 3 + Pillow + fontTools + Noto Sans CJK，运行 `python lab.py`。

simpson接受正偶数小段数n；本稿多项式实验输入端点为Fraction，保持精确有理数结果。实际断言0..3次多项式精确性及x4步距减半误差比16。数据中的隐藏波峰曲线用浮点sin计算，只用于绘图；其积分1来自正文三角恒等式，不由采样猜出。

本示例不是自适应求积库，也未对任意不连续/振荡/无界函数提供误差保证。所有图、代码、数据CC BY 4.0。几何检查结果保存figure-metadata.json，独立审读不由此替代。
