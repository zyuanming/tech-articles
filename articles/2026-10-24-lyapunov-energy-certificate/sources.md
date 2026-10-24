# 来源与素材说明

- Russ Tedrake，作者维护的《Underactuated Robotics》[Lyapunov Analysis](https://underactuated.mit.edu/lyapunov.html)：核对局部/全局稳定条件、正定性、径向无界、LaSalle不变性原理与有阻尼系统零导数集合的区别。实际查阅日期2026-10-24。不是Lyapunov本人历史原论文，本文未据此编写生平或发明年代。
- 本文弹簧模型、数值状态、局部反例及Euler步长分析为独立教学推导。所有曲线由随文代码实际计算，不复刻来源页面插图，不声称为真实实验。

## 逐图身份与作用

assets/01.png：原创弹簧装置结构示意，正方向箭头非瞬时速度。
assets/02.png：同一弹簧模型解析位置/速度曲线。
assets/03.png：上述解析轨迹的能量。
assets/04.png：有阻尼模型状态轨迹。
assets/05.png：无阻尼模型反例；显示轴比例不同。
assets/06.png：x²与x正定性对照。
assets/07.png：原创嵌套子水平集示意；箭头非数值轨迹。
assets/08.png：独立一维局部模型的导数。
assets/09.png：同一局部模型的方向线。
assets/10.png：Euler离散特征值模长平方解析表达式。
assets/11.png：两套明确不同模型的精确解。
assets/12.png：同一弹簧模型三个初始位移的解析轨迹。

以上图片和计算代码均为本稿原创，CC BY 4.0；无第三方图片，没有把生成图冒充设备照片。源页的摆、能量曲线等教学图未复制；本文讲述的对象是独立弹簧模型，已用原创结构及实际计算输出覆盖。

AI用于研究辅助、文章组织、数学复算代码与制图代码编写。数值复算范围见examples/README.md；并未进行实车、硬件或课堂读者实验。
