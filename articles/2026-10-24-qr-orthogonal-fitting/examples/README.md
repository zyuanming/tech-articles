# 复现

Python 3，NumPy（本次2.3.5）、Pillow、fontTools、Noto Sans CJK。运行 `python lab.py`。

输入t=(0,1,2)，b=(1,2,2)，模型b≈c+mt。构造薄Q、R，检查Q转置Q=I、QR=A，回代系数(7/6,1/2)、A转置残差=0、误差平方和1/6。浮点断言允许舍入，非形式化证明。

图3是独立二维投影示例；图11是Aε=[[1,1],[0,ε]]的条件数；图12是(3,4)反射到(5,0)的二维示例，不与主例三个分量混淆。原始数字data.json，图片尺寸与字体检查figure-metadata.json。

代码未实现可接收任意矩阵的生产QR，图中Gram–Schmidt为教学步骤。正文、代码、数据、图CC BY 4.0。
