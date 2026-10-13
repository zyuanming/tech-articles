# 来源、实际运行与素材权利

## 范围

本文解释已知接触之后如何改变运动：从真实盒子轨迹与一维手算进入，逐步引入动量、冲量、恢复系数、法线/切线、接触点速度、二维旋转响应、累计约束、摩擦、迭代、热启动和位置偏置。不会默认读者已经懂向量、角速度或转动惯量。公式到第17—18节才统一展开，前面的步骤与静态图独立可读。

本库既有GJK篇的核心是是否相交，高速子弹篇是首次接触时间，Verlet篇是时间积分中的能量误差。本篇不重复这三条主线；相关旧稿已经按固定提交核读。本文动画与复现是可选补充。

## 一手来源及支持范围

1. Erin Catto，[官方Publications目录](https://box2d.org/publications/)中的Sequential Impulses — GDC 2006，与[原讲义PDF](https://box2d.org/files/ErinCatto_SequentialImpulses_GDC2006.pdf)，题名Fast and Simple Physics using Sequential Impulses，共53页。核读Impulse、Integrate Velocities、Contact、Compute Incremental Impulse、Bias、Friction、Iterate、Accumulated Impulse、Warm Starting及Contact Persistence各部分。支持顺序更新、总冲量限制、负增量撤回、偏置及接触匹配机制。这里只引用并自行解释，不转载原幻灯片图片，也不主张这些数学全部最早由该讲义发明。
2. [官方Box2D-Lite仓库固定提交](https://github.com/erincatto/box2d-lite/tree/227b71b6974ea57ab7e96d40f6374287bd6a0e77)。实际核读README、Body.cpp、Arbiter.cpp、World.cpp、Collide.cpp和相关头文件。README支持2006教程背景；Body支持矩形惯量和静态逆质量；Arbiter支持接触点速度、法向/切向质量、累计clamp、热启动、摩擦混合与位置偏置；World支持每小步顺序。该Lite源码没有恢复系数e，也没有连续碰撞检测，本文不把现代Box2D功能投射给它。固定提交表示本次版本身份，不声称是2006年原会场存档。
3. Thomas Peacock、Nicolas Hadjiconstantinou，MIT 2.003J/1.053J Dynamics and Control I，Spring 2007，[Lecture6原讲义PDF](https://ocw.mit.edu/courses/2-003j-dynamics-and-control-i-spring-2007/e12ed118aeb1eb716db972ab23f4b982_lec06.pdf)，2007-02-26，共9页。支持冲量与动量变化、成对内力冲量、恢复系数与相对速度、一维碰撞的边界。无原图和大段原文转载。
4. [OpenStax University Physics Volume1 §9.2 Impulse and Collisions](https://openstax.org/books/university-physics-volume-1/pages/9-2-impulse-and-collisions)。核对冲量与动量变化、平均力乘作用时间的基本关系；没有复用其照片或配图。
5. [Box2D Simulation官方文档](https://box2d.org/documentation/md_simulation.html)，查阅时页面版本标识3.1.0。仅用于现代版本边界说明；其Restitution部分讨论恢复系数和低速碰撞处理。本文实测并非这个现代实现，不给出现代性能结论或参数推荐。

核读日期2026-10-13。本文没有人物照片、虚构对话或未核实的发明逸闻。讲义用于事实与机制查证，不因引用而改变原材料的权利。

## 两组计算的身份不能混在一起

### 原创解析模型

[impulse_lab.py](examples/impulse_lab.py)在Python3.12.14实际运行，完整结果见[analytic-results.json](examples/analytic-results.json)。e=0/0.5/1得到冲量2/3/4与正文所列速度；窄柱得到K=1.25、j=2.4、中心竖直速度−1.8、角速度+1.8；分离案例j=0。双点质量约束在8轮后速度为−1/256。

4000组随机代数案例，种子20261013，容差10⁻⁹；最大线动量误差约7.11×10⁻¹⁵、角动量约1.42×10⁻¹⁴、恢复关系约4.44×10⁻¹⁵、能量公式约1.14×10⁻¹³。检查只针对指定接触的解析公式，没有随机生成真实几何再运行完整碰撞检测。

### 未修改引擎核心的真实运行

实际使用g++14.2.0以-std=c++11 -O2编译。随附5个cpp、5个头文件及README、LICENSE共12个上游文件的Git blob SHA逐一与固定提交核对。原README字节作为README.upstream.txt保留，避免其完整仓库相对链接变成本例的断链。

原代码之外，仅本文驱动设置场景、执行World::Step并记录CSV。原始8份CSV在engine-output目录；32张单帧原始结果在rendered目录。可复现命令、每场景步长/重力/摩擦/轮数、字段阶段差异均见[示例说明](examples/README.md)。

- 正中与偏心两盒：无重力、无摩擦、无位置修正，步长1/240秒，20轮，不热启动，模拟1.5秒。不是连续碰撞检测。
- 两盒偏心的总水平动量最大偏差约6.32×10⁻⁶；统计同时检查关于同一原点的角动量。原始速度与角速度均来自引擎。
- 滑动：1/60秒步长、10轮、热启动、位置修正，4秒；地板50米长以保证观察期间不从边缘滑落。μ=0时末位置约16、水平速度5；μ=0.3时末位置约0.13、速度近零。
- 箱堆：8个质量1、边长1的盒子，1/60秒步长，10秒；四组1/10轮与热启动开/关全部保留。最大求解器接触重叠字段依次为1轮关0.22884202、1轮开0.170808643、10轮关0.139800787、10轮开0.0137618482。字段与绘图位置来自小步内不同阶段，不能当作当前画面姿态的重新检测值。
- 无帧率基准、无真实硬件碰撞实拍、无声称完全稳定或所有环境逐位可重现。代码运行与数据绘制均真实完成，但独立浏览器发布检查以发表时结果为准，不用本地静态代理冒充浏览器。

## 视觉清单与解释作用

正文34个图片节点，包括33张PNG与1个31帧GIF；封面另计。实际引擎输出承担明确的视觉锚点：正中/偏心同时间帧、运动动画、滑动位置与速度、完整四设置箱堆、动量曲线。其余原创解释图承担单位、方向、计算步骤与误区说明。原始附属帧不重复算正文图数。

所有PNG/GIF均为本文原创解释或原创结果渲染，没有复制官方演示画面、原讲义图、游戏截图或照片。数据来源与图像创作身份分别标明，不把自制方盒画面叫“现实物件实拍”。关键标注通常25—35px，720宽缩至354正文宽后约12.3—17.2px；需要另用手机比例复看版面。动画静态回退由图01提供，GIF每帧80ms而物理采样间隔约41.67ms，正文明确不是实时播放。

| 文件 | 本图的新增理解作用 | 原尺寸 |
| --- | --- | --- |
| [01-engine-impact-frames.png](assets/01-engine-impact-frames.png) | 真实引擎正中与偏心碰撞的同时间帧，先看见平移与旋转差别 | 720×1030 |
| [02-engine-impact.gif](assets/02-engine-impact.gif) | 31帧真实引擎数据动画，以运动方向和转角补静态对比，不是软件界面截图 | 720×640 |
| [03-detection-versus-response.png](assets/03-detection-versus-response.png) | 明确碰撞检测、首次接触时间和响应的职责分界 | 720×880 |
| [04-position-speed-time.png](assets/04-position-speed-time.png) | 建立位置、经过时间与带方向速度的基本单位 | 720×820 |
| [05-momentum-bars.png](assets/05-momentum-bars.png) | 用具体质量与速度建立动量账本，总动量不是速度相加 | 720×880 |
| [06-equal-opposite-impulse.png](assets/06-equal-opposite-impulse.png) | 具体手算相反冲量对不同质量的速度改变量 | 720×850 |
| [07-restitution-relative-speed.png](assets/07-restitution-relative-speed.png) | 恢复系数是分离相对速度与接近相对速度的比例 | 720×830 |
| [08-three-restitution-results.png](assets/08-three-restitution-results.png) | 三个实际解析计算结果揭示e控制反弹程度而非永远黏连 | 720×910 |
| [09-energy-versus-momentum.png](assets/09-energy-versus-momentum.png) | 同一碰撞三e的动能9到6/6.75/9，区分守恒量 | 720×830 |
| [10-contact-normal-tangent.png](assets/10-contact-normal-tangent.png) | 给出固定A到B法线约定与切向，不默认读者知道法线 | 720×850 |
| [11-relative-velocity-sign.png](assets/11-relative-velocity-sign.png) | 用具体速度对照接近为负、分离为正和相等为零 | 720×830 |
| [12-solve-impulse-stepwise.png](assets/12-solve-impulse-stepwise.png) | 不直接抛公式，从两物体速度变化逐步解出冲量3 | 720×990 |
| [13-separating-no-attraction.png](assets/13-separating-no-attraction.png) | 分离中的单接触不应再套负冲量把两物拉回 | 720×820 |
| [14-static-inverse-mass.png](assets/14-static-inverse-mass.png) | 解释静态物体逆质量为零的数值表示，不除以零 | 720×810 |
| [15-off-center-lever.png](assets/15-off-center-lever.png) | 画出接触点相对中心的位置，解释偏心冲量的旋转职责 | 720×960 |
| [16-contact-point-velocity.png](assets/16-contact-point-velocity.png) | 用向量叠加图说明中心速度不等于接触点速度 | 720×960 |
| [17-corner-on-narrow-post.png](assets/17-corner-on-narrow-post.png) | 实际单接触解析例子强调窄柱支撑而非整面地板 | 720×900 |
| [18-contact-effective-response.png](assets/18-contact-effective-response.png) | 将一般分母拆成平移和两项转动响应，给进阶公式清楚职责 | 720×870 |
| [19-contacts-share-body.png](assets/19-contacts-share-body.png) | 一个刚体的多个接触通过平移和角速度耦合 | 720×800 |
| [20-iteration-residual.png](assets/20-iteration-residual.png) | 真实手算模型每轮速度误差减半，解释多轮遍历接触的原因 | 720×920 |
| [21-accumulated-impulse.png](assets/21-accumulated-impulse.png) | 区分累计冲量非负与增量可负，说明不能把每个修正都截成非负 | 720×850 |
| [22-friction-budget.png](assets/22-friction-budget.png) | 摩擦方向和由累计法向冲量限定的切向范围 | 720×870 |
| [23-engine-slide-frames.png](assets/23-engine-slide-frames.png) | 真实Box2D-Lite滑动比较，固定比例展示无摩擦持续滑动和有摩擦停止 | 720×1740 |
| [24-engine-slide-speed.png](assets/24-engine-slide-speed.png) | 实际速度曲线连接摩擦模型与可见停止，不把经验阻尼当摩擦 | 720×850 |
| [25-engine-stack-comparison.png](assets/25-engine-stack-comparison.png) | 相同八箱初态的真实五秒输出，比较一个明确预算组合而非宣称只改一项 | 720×1030 |
| [26-engine-four-settings.png](assets/26-engine-four-settings.png) | 完整四组合实际输出避免只展示最优与最差来混淆变量 | 720×1570 |
| [27-warm-start-contact-id.png](assets/27-warm-start-contact-id.png) | 解释热启动需要接触匹配，避免把旧冲量当恒定作用力 | 720×820 |
| [28-penetration-bias.png](assets/28-penetration-bias.png) | 由具体重叠/slop/步长算出偏置速度，区分速度约束与位置误差 | 720×950 |
| [29-world-step-order.png](assets/29-world-step-order.png) | 区分一小步内迭代次数与物理时间推进，对应官方World步骤 | 720×920 |
| [30-engine-momentum-check.png](assets/30-engine-momentum-check.png) | 真实双盒CSV独立动量复算，明确条件与浮点误差 | 720×900 |
| [31-engine-code-responsibilities.png](assets/31-engine-code-responsibilities.png) | 真实所运行源文件职责与Lite无恢复系数的版本边界 | 720×930 |
| [32-whole-contact-route.png](assets/32-whole-contact-route.png) | 收束从目标接触速度到冲量及平移转动的完整链 | 720×930 |
| [33-inertia-size-matters.png](assets/33-inertia-size-matters.png) | 从相同质量不同尺寸的均匀矩形建立转动惯量与轴的明确含义 | 720×940 |
| [34-components-dot-cross.png](assets/34-components-dot-cross.png) | 为二维叉乘分母搭起坐标分量台阶，不突然引入矩阵与三维运算 | 720×960 |

## 权利

原创正文、封面、解释图与原创结果渲染采用[CC BY4.0](https://creativecommons.org/licenses/by/4.0/)。本文新增示例程序采用[MIT](examples/LICENSE)。随附Box2D-Lite原文件保留其原作者及原许可，见[vendor LICENSE](examples/vendor/box2d-lite/LICENSE)、各文件许可头及[上游清单](examples/upstream-manifest.json)；本文总许可不覆盖或替换这些第三方声明。

原讲义、教材和现代文档只链接引用，没有再发布其PDF、照片或截图。字体仅用于渲染，没有随文分发字体文件。
