# 来源、图像与实验说明

原创中文正文由zyuanming发布，采用CC BY 4.0。本文使用AI辅助研究、写作、编程绘图和校验。24幅原创教学图（23幅静态图和1个25帧GIF）由明确方程与数值记录绘制；不是游戏引擎截图、芯片测试或真实弹簧测量。另有1张原尺寸历史设备照片，按下述独立权利依据使用。第三方论文、讲义与照片不自动纳入正文许可。

## 一手来源与实际使用范围

1. Loup Verlet，*Computer “Experiments” on Classical Fluids. I. Thermodynamical Properties of Lennard-Jones Molecules*，Physical Review 159，98—103，1967。[APS出版者记录](https://journals.aps.org/pr/abstract/10.1103/PhysRev.159.98)；[六页原论文扫描](https://norman.jiht.ru/student/morozov/Verlet67.pdf)。实际查看全部六页。98—99页支持864个粒子、位置更新式、邻居列表与UNIVAC 1107/CDC 6600计算设备。后四页为热力学结果及结论，不是本文三种弹簧积分器的实验来源。本文不声称Verlet在1967年首次发明了整个数值思想家族，也不将邻居列表提速等同于积分公式提速。
2. Ernst Hairer，2010年*Geometric Numerical Integration*课程，[Lecture 2: Symplectic integrators](https://www.unige.ch/~hairer/poly_geoint/week2.pdf)，实际读前3页的辛欧拉、Störmer–Verlet、对称性和阶数说明；[Lecture 4: Long-time integration of Hamiltonian systems](https://www.unige.ch/~hairer/poly_geoint/week4.pdf)，实际阅读与查看4—5页谐振子、稳定性及长期能量讨论。本文只取可见的一个线性模型，不把更一般的长期几何积分定理说成无条件保证。
3. [GROMACS 2025.4官方手册，Velocity Verlet小节](https://manual.gromacs.org/2025.4/reference-manual/algorithms/molecular-dynamics.html#the-velocity-verlet-integrator)。实际读更新式(31)及相邻的(29)—(32)、速度所在时刻和leapfrog区别。本文三子步骤与该分步形式相符，但实验代码为独立新作，未运行GROMACS，也未复制其软件性能或分子体系数据。
4. [ENS校友协会的Loup Verlet纪念文章](https://www.archicubes.ens.fr/lassociation/m%C3%A9moire-normalienne/notices/verlet-loup-1949-s)，用于核对人物身份和继续查找肖像；正文的1967研究事实以原论文为准，没有补造人物对白或动机。

## 原资料中的图与重要对象

1967论文Fig.1—3讨论状态方程、等温线及同位素分离相关量；表I—IV为热力学结果。它们不展示本文弹簧模型或积分器能量误差，未转成本文的实验图。原论文保留出版版权，没有查到可将扫描图公开再分发的依据，因此提供完整原文件查看链接，不公开裁图。

Hairer Lecture 2的Fig.1是摆系统的面积保持对比；Lecture 4相关图讲能量行为。本文用自设参数的线性弹簧重新计算相图和能量曲线，既不临摹讲义图线，也不把讲义中的非线性摆改名为本文模型。讲义未发现明确开放图版许可，原图只在作者站查看。GROMACS本题核心velocity Verlet小节以公式说明；同页的Fig.7解释相邻leapfrog小节。本文14—15独立说明速度Verlet的三个子步骤，未假称转载官方图。该长页面另外的速度分布、截断漂移及通信图不属于本文教学问题；未从代码许可推断文档图可复用。

已主动检索Loup Verlet可靠肖像，包括Commons、ENS纪念页及[出版社作者页](https://www.editionsducerf.fr/contributeur/loup-verlet/)。未找到同时核实身份、原图与适当公开复用依据的照片；没有使用同名人像或生成假的历史肖像。本文核心是方法原理，以真实计算机展品和原创机制图补足设备与概念视觉。

## 唯一第三方照片

- 文件：`assets/cdc-6600-chassis-original.jpg`。
- 作品：*CDC 6600 chassis and cooling panel at CHM*；摄影者Tomwsulcer；拍摄日期2015-12-24；作者标为自作。
- [Commons原说明页](https://commons.wikimedia.org/wiki/File:CDC_6600_chassis_and_cooling_panel_at_CHM.jpg)；[原尺寸JPEG](https://upload.wikimedia.org/wikipedia/commons/0/03/CDC_6600_chassis_and_cooling_panel_at_CHM.jpg)。1769×2034，862545字节；文件Git以外的原始SHA-1为`381c5ab015d9a1aaf672c7e604dbd1e960e60656`。保留原字节，没有裁切、调色或去除标识。
- 原作者以[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)发布。此结论来自该作品的明确声明，不是因为照片能在网上访问。保留作者、标题与原站链接便于追溯。
- 它是计算机历史博物馆的机箱/冷却面板，不是Verlet当年使用的纽约大学机器之现场照片，也不证明本文程序曾在该机上运行。

## 24幅原创图的教学分工

01三算法运动动画；02弹簧与力方向；03能量交换；04显式欧拉第一步；05能量放大代数；06固定总时间下缩小步长；07真实空间与相平面；08向外螺旋；09旧/新速度顺序；10辛欧拉椭圆；11向前向后展开；12位置记忆通用示意；13初始化；14速度Verlet子步骤；15第一步账本；16长时间能量对数图；17同数据局部放大；18本例邻近不变量；19六步数值周期；20相位误差；21无量纲稳定条件；22边界反例；23诊断量；24步长减半练习。

GIF由同一实验函数给出，显示n=0、2、…、48的25个状态，即模拟时间0—9.6秒，相邻两帧相差0.4模拟秒。播放间隔350毫秒是展示设置，不声称实时播放。图12是通用分项示意，箭头不按贯穿算例的数值比例；图16对数与图17线性刻度不同，图22左右面板分别采用线性和对数纵轴，不能把屏幕斜率直接比较。

## 可复算实验与边界

[oscillator.py](examples/oscillator.py)只用Python标准库，全部数据来自明确更新式，不联网、不调用游戏引擎。主实验m=k=1、x0=1、v0=0、h=0.2、500步，共100秒。

- 第一步显式欧拉(x,v,E)=(1,−0.2,0.52)，半隐式为(0.96,−0.2,0.4808)，速度Verlet为(0.98,−0.198,0.499802)。
- 500步实际能量比例范围：显式欧拉1—328601581.5797；半隐式0.9090924—1.1111103；速度Verlet0.99000018—1。这里的比例不是通用算法性能指标。
- 484个分数算术案例核显式欧拉能量恒等式；随机种子1967，10000次位置递推与速度Verlet逐步比较一致（浮点容差）。另核本例二次不变量和单步时间反演；这些有限测试不冒充一般理论证明。
- h=1时数值周期6秒，30秒后的真实解使用cos(30)、−sin(30)。h=2及2.2反例都取初速度0.1，避免用特殊零初速掩盖边界增长。
- “能量有界”“相位准确”“复杂游戏物理稳定”是不同要求。本文未将线性谐振子的稳定区间推广到碰撞、约束、变步长、速度依赖力或任意非线性系统。

以上代码与原创图为本稿新作的教学材料。正文与全部25幅图的阅读顺序以read.md为准。
