# 来源、逐图说明与真实边界

## 一手资料与支撑范围

1. [scikit-learn 1.8.0 PCA接口](https://scikit-learn.org/1.8/modules/generated/sklearn.decomposition.PCA.html)及[同版本分解指南](https://scikit-learn.org/1.8/modules/decomposition.html#pca)：核对中心化而非自动标准化、方向与方差排序、SVD实现及报告方差的n−1口径。版本固定1.8.0，与本文实际交叉检查一致。本文主计算不是复制文档的图片或代码。
2. [OpenCV 4.13.0：PCA入门](https://docs.opencv.org/4.13.0/d1/dee/tutorial_introduction_to_pca.html)：核对以点位置、均值和主方向估计物体方向这一应用边界。没有安装或运行OpenCV；本文照片实验实际使用NumPy和Pillow，不把官方示例运行结果当作本次结果。
3. [UCI Iris对象页](https://archive.ics.uci.edu/dataset/53/iris)与其[下载包](https://archive.ics.uci.edu/static/public/53/iris.zip)：提供150行、4项cm测量、类别字段、源数据差异提醒与CC BY 4.0许可。本文实际下载原包、读原文件，不使用网页缩略图；物种标签只用于计算后的上色。
4. [USGS Iris versicolor照片记录](https://www.usgs.gov/media/images/iris-versicolor-blue-flag-iris-howard-county-md-helen-lowe-metzman)：提供实物身份、USGSBIML Team署名、Helen Lowe Metzman的标本/照片贡献、Public Domain权利和原图入口。[原件与派生处理说明](originals/RIGHTS.md)保留具体区别。网页2019-12-17不是本文推定的拍摄日。

数学推导使用原创四点小例逐步计算；标准线性代数关系与实际数值交叉核验，不以工具测试次数代替证明。本篇不叙述PCA的单人发明史；没有将未取得的历史论文正文当作已读一手证据。

## 本次实际执行

Python3.12.14、NumPy2.3.5、Pillow12.3.0；scikit-learn1.8.0/full作为额外交叉检查。输入、固定种子、输出定义、方差分母、图像坐标与限制见[实验README](examples/README.md)。[完整结果](examples/results/results.json)包含原数据指纹及可重算数值。

照片选区是阈值操作的结果，不是人工标注的生物学分割；主轴是位置分布的方向，不是花朵语义朝向。Iris数据全150行拟合是探索展示，不是独立预测评估。四点玩具数据与随机断言用的合成数据均明确标为教学/合成，不冒称实测。

## 图片清单与每图职责

文件编号保留生成材料的标识，不是正文顺序号。

正文21个图片节点，其中1幅GIF共10帧；封面另1幅。不把动画帧、拼版面板或原件附件计作更多独立正文图片。

除26、32及其对应原始处理输出含USGS照片/派生影像外，其余均为原创教学图、代码实际计算的数据图或动画。文件28、29、31来自CC BY 4.0的UCI数据再分析，保留数据署名；未复用官方示例图。

- [02-four-points.png](assets/02-four-points.png)：建立坐标、二维与贯穿四点的实体位置。原创，CC BY 4.0。
- [03-drop-one-coordinate.png](assets/03-drop-one-coordinate.png)：先看损失，再引入更好的方向。原创，CC BY 4.0。
- [04-center-translation.png](assets/04-center-translation.png)：中心化只平移，不改变点之间相对形状。原创，CC BY 4.0。
- [05-perpendicular-foot.png](assets/05-perpendicular-foot.png)：将正交投影具体化为垂足与残差。原创，CC BY 4.0。
- [06-one-point-reconstruction.png](assets/06-one-point-reconstruction.png)：精确数字绑定单点垂足，防止只会比喻不会算。原创，CC BY 4.0。
- [07-unit-direction.png](assets/07-unit-direction.png)：解释单位方向而非默默预设向量知识。原创，CC BY 4.0。
- [11-three-variances.png](assets/11-three-variances.png)：方向比较以同一尺度条形图呈现。原创，CC BY 4.0。
- [12-pythagorean-split.png](assets/12-pythagorean-split.png)：平方损失等价关系的几何依据。原创，CC BY 4.0。
- [14-rotating-ruler.gif](assets/14-rotating-ruler.gif)：同一几何模型随角度连续改变，首帧即最优45度；静态回退由图11承担。原创，CC BY 4.0。
- [15-second-direction.png](assets/15-second-direction.png)：第二主方向补回剩余的正交变化。原创，CC BY 4.0。
- [16-two-component-recovery.png](assets/16-two-component-recovery.png)：保留全部方向是坐标变换，丢方向才有维度损失。原创，CC BY 4.0。
- [21-variance-not-label.png](assets/21-variance-not-label.png)：把原二维位置与投影后一维读数上下对照，直接显示异色点共用读数。原创，CC BY 4.0。
- [22-units-change-direction.png](assets/22-units-change-direction.png)：等物理数据的数字缩放能改变PCA目标。原创，CC BY 4.0。
- [24-outlier-turns-axis.png](assets/24-outlier-turns-axis.png)：实际计算显示单离群值及平方损失敏感性。原创，CC BY 4.0。
- [25-equal-variance.png](assets/25-equal-variance.png)：相同特征值的方向不唯一及不稳定边界。原创，CC BY 4.0。
- [26-real-iris-object.png](assets/26-real-iris-object.png)：实际物件视觉锚点，明确照片与数据样本的身份边界。USGS Public Domain原照的分析派生；中文标注CC BY 4.0。
- [27-four-feature-rulers.png](assets/27-four-feature-rulers.png)：用示意部件把四列测量含义讲清，不冒充解剖实拍。原创，CC BY 4.0。
- [28-two-original-features.png](assets/28-two-original-features.png)：真实数据先从普通散点读起，与PCA区别。UCI CC BY 4.0数据的原创分析图，CC BY 4.0。
- [29-iris-pca-result.png](assets/29-iris-pca-result.png)：真实4维PCA运算结果，标签未参与拟合。UCI CC BY 4.0数据的原创分析图，CC BY 4.0。
- [31-four-feature-reconstruction.png](assets/31-four-feature-reconstruction.png)：从抽象投影回到实际尺寸误差，显示非零损失。UCI CC BY 4.0数据的原创分析图，CC BY 4.0。
- [32-threshold-changes-input.png](assets/32-threshold-changes-input.png)：实际阈值处理、掩模与轴输出证明输入定义的重要性。USGS Public Domain原照的分析派生；中文标注CC BY 4.0。

封面为原创四点几何图，CC BY 4.0。图14首帧为45度，正文静态图11、12及相邻手算保留方向比较与损失分账；动画不是理解主线的唯一渠道。实物照片的原像素没有当作数学测量尺，也没有把示意花部件当成照片解剖标注。

## 许可与AI辅助

原创正文、图解和分析说明CC BY 4.0；[原创脚本MIT](examples/LICENSE)。USGS原照Public Domain，UCI原数据CC BY 4.0，分别保留身份，不由正文许可覆盖重授。本文使用AI辅助资料检索、写作与制图程序制作；没有生成伪实拍、虚构摄影经历、植物测量、真实游戏运行或现场观察。
