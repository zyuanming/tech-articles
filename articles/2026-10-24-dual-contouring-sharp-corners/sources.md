# 来源、实现与图像权利

本文由AI辅助研究、推导、编程、写作与制图。原创正文、原创图及数据：zyuanming，CC BY4.0；原创代码MIT。全部数学例子与图像为本篇自设。

## 一手依据

Tao Ju、Frank Losasso、Scott Schaefer、Joe Warren，[Dual Contouring of Hermite Data](https://www.cs.rice.edu/~jwarren/papers/dualcontour.pdf)，2002。实际阅读作者公开论文的摘要、§2均匀网格、Hermite交点/单位法线、QEF及对偶连接部分。本文只提炼所需的技术定义，没有翻译或复刻论文全文；原论文包含八叉树、自适应简化、多材质及拓扑处理，本篇均未实现。

核心例子为单位格的(0.7,0.6)直角；完整实际实验是精确轴对齐矩形的二维均匀网格提取。交点通过48次二分求得，法线取已知面方向；并不声称其输入是任意噪声扫描、距离场或现代生产资产。欠约束时以交点均值为参考求最小二乘修正；有界最优只作为独立算例，不伪称主程序具有通用约束优化器。

原论文Fig1—3及后续示例模型未获得本次明确再分发依据，不归档；其身份是作者的研究结果，不能因PDF可读就套用本库CC BY。本文用独立矩形、格内角点、数值反例及可复现输出覆盖需要解释的结构。没有生成任何伪历史照片、论文截图或游戏界面。

## 全部配图

原链接：[lab.py](examples/lab.py)、[results.json](examples/results.json)。均署名zyuanming、CC BY4.0，无第三方素材及修改。实际文件信息见[figure-metadata.json](examples/figure-metadata.json)。图01兼入口图。

1. 01-sharp：真实二维提取对照，原角标红。
2. 02-signs：四角符号的信息不足。
3. 03-cut-corner：相同交点直连为何切角。
4. 04-normals：两交点的法线。
5. 05-tangent-lines：延伸切线恢复角。
6. 06-error：实际误差函数采样与候选分数。
7. 07-dual-connect：变号边与相邻格代表点的连接关系。
8. 08-full-grid：实际完整网格、代表点及轮廓。
9. 09-three-d：沿三维原网格边观察的示意投影，非三维实验输出。
10. 10-flat：平坦区域欠约束。
11. 11-outside：近乎平行约束交点出格。
12. 12-bounded：独立算例的真正有界最优与裁剪点。
13. 13-hidden：小结构完全漏采的反例。
14. 14-resolution：两档网格实际结果。

图中未把误差函数最优解释成任意网格的拓扑或形状保证。字体只用于位图文字，无字体文件重新分发。
