# 来源、事实边界与制作说明

核实日期：2026-10-14。本文讲基础检索思路，教学三特征与真实小库实验均为本文实现，不是某款商业游戏的代码、性能或成品截图。

## 算法的一手资料

1. Daniel Holden、Oussama Kanoun、Maksym Perepichka、Tiberiu Popa，2020，Learned Motion Matching，ACM Transactions on Graphics，DOI [10.1145/3386569.3392440](https://doi.org/10.1145/3386569.3392440)。[作者公开PDF](https://theorangeduck.com/media/uploads/other_stuff/Learned_Motion_Matching.pdf)。第3节先描述基础Motion Matching，后面的章节才讲学习替代。论文的示例特征包含两脚位置与速度、髋速度及多个未来位置与朝向；并非本文的三项简化。论文中60Hz下20/40/60帧的未来采样，也不是本文120Hz下60帧的半秒。
2. Daniel Holden，[Motion-Matching示例仓库](https://github.com/orangeduck/Motion-Matching)。本次阅读database.h、controller.cpp、spring.h，核对特征归一化、检索、接续以及足部处理。作者实现按特征组统计尺度并带权重，本文人工0.25/1米尺度不冒充该统计过程。作者代码中的特征向量权重经过平方后影响距离，不能与本文直接乘在轨迹平方代价上的λ混为一谈。MIT代码许可不自动覆盖仓库引用的动作数据。
3. Daniel Holden，2021-09-23，[Code vs Data Driven Displacement](https://www.theorangeduck.com/page/code-vs-data-driven-displacement)。支持碰撞/移动对象、显示角色、从动作提取地面参考骨的区分，以及接续、位移调整、脚接触之间的取舍。本文没有下载、转载作者演示视频，也没有把文中截图作为公开素材。

基础Motion Matching的出现早于2020论文，本文没有宣称由该论文首次发明，也不把某次演讲年份当成发明年份。

## CMU真实数据和格式

4. [CMU Graphics Lab Motion Capture Database](http://mocap.cs.cmu.edu/)、[FAQ](http://mocap.cs.cmu.edu/faqs.php)、[subject16目录](http://mocap.cs.cmu.edu/search.php?subjectnumber=16)。使用16.asf及16_15.amc（walk）、16_17.amc（walk, 90-degree left turn）、16_19.amc（walk, 90-degree right turn）。原文件及SHA256随文保留。目录提供这几段的120Hz采样率；FAQ说明长度转换及数据使用条件。官方公开站点使用HTTP，本篇保留实际取得文件的哈希用于确定复现输入，不把哈希说成发布方数字签名。
5. CMU Info页面链接的[ASF/AMC格式说明](https://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Jeff/ASF-AMC.html)，用于核对骨架层级、静态轴与动态旋转。该说明采用行向量约定，本文列向量实现转换了矩阵次序，不能把两种记法直接照抄拼接。
6. [CMU工具页](http://mocap.cs.cmu.edu/tools.php)链接的James McCann AMC Viewer源代码，用作核对根世界平移与骨段方向组合的另一份实现参考。本文没有编译、运行或转载这份查看器代码。随文解析器是独立实现，适用范围限定为本次subject16文件。

数据归属、使用条件与修改说明集中在[NOTICE](third-party/NOTICE.md)。数据文件可公开取得，不表示它们是CC0或CC BY。未使用另一仓库中的LAFAN1数据，也未将其非商业、禁止演绎条件忽略后换用同名代码许可。

## 图片分别证明什么

- 图1、2：CMU骨架数据经本文正向运动学与投影绘制，分别展示当前状态和同一片段的真实不同时刻。
- 图3至11：原创解释图。四候选与标量接续均为人工教学例。图6的条长来自实际分项代价；图9曲线来自实际计算，不是观测人体测量。
- 图12：CMU三段的根地面轨迹，同起点同初始方向同尺度；片尾时间条是分区示意，不按三段长度绘制。
- 图13：本文真实离线查询的数字，不是游戏基准测试。
- 图14：真实数据派生骨架动画，16个显示时刻逐个来自原记录；首尾加停顿，未施加混合或锁脚。
- 图15：同一起点对齐后两个真实姿势的比较。三维端点距离与屏幕投影分开，数字来自计算。
- 封面：独立原创概念图，不是第三方游戏画面。

本文没有使用生成式图像伪造动作捕捉现场、人物、设备或游戏截图。没有为凑配图数量重复转载同一照片。

## AI辅助与可复现性

正文组织、程序和解释图制作有AI辅助；公开包保存原始输入、独立实现、实际输出和数据身份，让读者能够重跑并核查主张。程序的断言与数值实验只覆盖注明的输入和条件，不代替动画师对完整角色控制器的评估。

原创正文、人工数据和纯解释图采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；代码采用MIT；CMU内容及含其派生数据的文件遵守其独立条件。不同来源的许可不能合并成一句“全部自由使用”。
