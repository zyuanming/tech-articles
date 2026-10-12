# 列线图理想几何实验

Python 3标准库即可；实际运行版本3.12.14。代码为本稿原创，CC BY 4.0，署名zyuanming / tech-articles。

运行全部有限检查，并重新生成三份A4矢量纸页：

```sh
python nomogram_lab.py --out results.json --paper-dir .
```

不会联网、安装软件或接触实物电路。加法与并联检查用Fraction精确分数；对数乘法用math浮点函数。所有输入范围、实际数目、误差和随机种子都在输出JSON中。检查失败会抛出异常，不报告PASS。

打印paper-addition.svg、paper-product.svg或paper-parallel.svg时，把整张图一起处理。三轴不可独自移动或改变纵向比例。全图共同的可逆线性拉伸仍保留共线，但可能让刻线难读。纸上有限刻线需要目测插值，毫米坐标是设计值，不是实物测量。

电阻页所有数值均按欧姆解释；不得只给某一条轴换单位。外轴10至100，中轴5至50。它仅用于理想电阻方程教学，不承担功率、容差、温度或安全设计。
