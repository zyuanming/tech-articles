# 来源与素材

原创中文正文由zyuanming发布，CC BY 4.0。该声明不自动扩展至图片与代码。

## 方法及历史依据

- Ford Jr., L. R. and Fulkerson, D. R., Maximal Flow Through a Network, Canadian Journal of Mathematics 8 (1956), pp.399–404。原文扫描件：https://www.cs.yale.edu/homes/lans/readings/routing/ford-max_flow-1956.pdf 。期刊元信息：https://doi.org/10.4153/CJM-1956-045-5 。首段归问题于T. Harris；第1节最小割定理，第2节特殊平面网络计算，第3节最短路径对偶。本文没有将现代DFS代码写成该论文原代码，也不把2018网站上线日期当出版时间。
- MIT 6.854, Maximum Flow：https://courses.csail.mit.edu/6.854/20/Notes/n06-flow.html 。剩余图、反向额度、可达集最小割证书、整数终止、钻石网络容量反例。该教学页是本文目标机制来源，HTML无嵌入图像，包含字符画钻石网络；本文用原创四节点图按自设容量解释，没有漏收可下载原图。
- David Karger, Basic Flow Algorithms and Capacity Scaling：https://courses.csail.mit.edu/6.854/21/Notes/n07-flow_computation.html 。瓶颈、整型容量、容量规模与增广次数。正文的M参数构造只计算次数，不引用现代性能数字。
- Edmonds, Jack and Karp, Richard M., Theoretical Improvements in Algorithmic Efficiency for Network Flow Problems, JACM 19(2), 1972, pp.248–264：https://web.eecs.umich.edu/~pettie/matching/Edmonds-Karp-network-flow.pdf 。该历史论文作为进一步阅读；本文复杂度直接核对MIT最短增广路讲义：https://courses.csail.mit.edu/6.854/21/Scribe/s7-blockingFlows/unit-capacity.html ，其中明确证明O(m²n)。正文只在边界段提到Edmonds–Karp，不展开人物传记。

## 原图核对与采用边界

Ford/Fulkerson的1956扫描论文共六页，实看全部页。含Fig.1（三条容量2分支的多源多汇反例）和Fig.2（非特定平面类型的图）。它们服务论文的另两项讨论，不是本文四节点剩余网络主线；期刊版权归Canadian Mathematical Society，未取得开放图像许可，因此仅链接原论文，不提取图片公开再分发，也不声称本文收录论文全部插图。

Ford与Fulkerson仅作必要历史归属，没有身份和公开复用依据均核实的肖像，未采用肖像，也未使用同名人物或生成肖像。本文不是人物视觉传记。

## 原创图与代码

assets下16张PNG均为原创教学图，原生输出1152×832，无代理图替代。

01-capacity：原图5条边容量1。02-first-path：s-a-b-t。03-first-flow：第一次流量/容量。04-forward-only：仅剩s-b、a-t正向可用。05-reverse-meaning：a-b已用1与b-a撤回1。06-residual：完整正额度残量图。07-second-path：s-b-a-t。08-delta：+1、−1、+1的联合修改。09-final-flow：外圈四边各1，中间0。10-cut：S={s}容量2。11-conservation：a流入1流出1。12-certificate：可行流2与割上界2。13/14-matching：甲可做X/Y、乙只可X的重配对。15-bad-paths：外圈M、中间1。16-path-cost：构造例2M与2次增广的计算曲线，非耗时测量。

examples/experiment.py为完整Python3标准库教学程序，实际运行两次增广分别s-a-b-t和s-b-a-t，最大流2；五条原边流量[1,1,0,1,1]，含结果断言。递归DFS只服务小例，不声称为可直接部署的大图实现。

本文使用AI辅助调研与写作；原创教学图按明确设定由代码生成，合成演示与真实来源图已区分。
