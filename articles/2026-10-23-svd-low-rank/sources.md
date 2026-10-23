# 来源、素材权利与 AI 辅助说明

- [MIT 18.065，第6讲SVD](https://ocw.mit.edu/courses/18-065-matrix-methods-in-data-analysis-signal-processing-and-machine-learning-spring-2018/resources/lecture-6-singular-value-decomposition-svd/)：实际读取课程摘要的奇异向量、AᵀA联系与秩1层定位；未声称看完整视频。文中“正交可能含反射”是为避免把口头旋转解释过度推广而明确补充。
- [MIT 18.065，第7讲Eckart–Young](https://ocw.mit.edu/courses/18-065-matrix-methods-in-data-analysis-signal-processing-and-machine-learning-spring-2018/resources/lecture-7-eckart-young-the-closest-rank-k-matrix-to-a/)：实际摘要明确低秩近似与Frobenius度量。本文具体例子和推导自行展开，未翻译课堂全文。
- [MIT 10.34讲义第6讲](https://ocw.mit.edu/courses/10-34-numerical-methods-applied-to-chemical-engineering-fall-2015/b3d5967d107c09284ab273a74fa33212_MIT10_34F15_Lec06.pdf)：读SVD维度/性质段并实际查看PDF第10页的指纹压缩对照。该图展示压缩的历史教学用法，但不承担本文实验；本文未使用该图、未描摹其布局或指纹。
- [NumPy官方svd文档](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html)：首次实际返回的说明支持full_matrices=False形状及(u*s)@vh重建。本地实验版本NumPy 2.3.5；绘图用Matplotlib 3.10.8、Pillow，仅核心代码需要NumPy。
- [MIT OCW使用条款](https://ocw.mit.edu/pages/privacy-and-terms-of-use/)标明CC BY-NC-SA及具体使用边界；本次后续用途未确认为非商业，原源图不纳入交付。本文16图均为自写数学图与实际数值数组输出，不借原图许可为新内容背书，不使用MIT标识、人物像或第三方照片。




## AI 辅助与许可范围

本文使用 AI 辅助资料整理、讲解撰写、教学代码和原创图示制作；实验结果来自文中说明的实际程序运行，不是实地或生产系统测量。

原创文章正文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。这一正文许可不自动适用于代码、图片和第三方素材；第三方材料保留文中列明的原作者、许可与限制。
