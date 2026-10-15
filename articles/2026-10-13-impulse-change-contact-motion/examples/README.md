# 可选复现：小算术与真实引擎运行

静态正文已经包含主要推理。这里是愿意动手读代码的读者可以选择的补充，不是读懂文章的前置作业。

## 文件身份

- [impulse_lab.py](impulse_lab.py)：本文独立的二维瞬时、无摩擦、单接触解析模型，以及简化双质量约束账本。带恢复系数e；不含碰撞检测和时间积分。
- [analytic-results.json](analytic-results.json)：该模型的实际结果，含4000组固定种子随机代数检查。
- [engine_driver.cpp](engine_driver.cpp)：本文编写的命令行驱动，调用未修改的Box2D-Lite核心代码。
- [upstream-manifest.json](upstream-manifest.json)：原文件路径、固定提交、Git blob SHA、随附路径与SHA256。随附12件原仓库文件字节未改；原README另存为[README.upstream.txt](vendor/box2d-lite/README.upstream.txt)，避免把上游完整仓库的相对链接误当成本例的导航。
- [原源码许可](vendor/box2d-lite/LICENSE)与每个源码文件的原作者许可头原样保留。未分发第三方讲义PDF或官方演示程序界面图。
- `engine-output/`：8份真实运行CSV与[统计汇总](engine-output/summary.json)。
- [analyze_engine.py](analyze_engine.py)：由CSV复算动量、角动量、动能及接触字段摘要；不是物理求解器。
- [render_engine.py](render_engine.py)：只读取CSV中的位置、角度和尺寸，绘制原创方盒子与网格。它不计算物理轨迹。
- `rendered/`：32张实际CSV帧的原始渲染结果。正文的多帧排版与解释图另在assets目录。不能把这些附属帧重复计入正文图数。

## 路线一：只算一个接触

在这个examples目录运行：

```sh
python impulse_lab.py
```

本次实际环境为Python3.12.14；这条路线只使用标准库。运行会重新写入analytic-results.json。

核心设置：A质量2、速度(3,0)，B质量1、速度(0,0)，法线(1,0)，接触在两者中心连线上。e取0、0.5、1时，冲量分别为2、3、4，速度结果分别为(2,2)、(1.5,3)、(1,4)。

窄柱例子：柱子静态；盒子质量2、惯量4/3、中心(0,1)、速度(0,−3)，接触点(1,0)，法线(0,1)，e=0。得到j=2.4，盒子中心竖直速度−1.8，角速度+1.8。接触点仍有+1.8的水平速度，只有竖直分量为0。

4000组检查的随机种子为20261013，检查容差10⁻⁹。随机案例构造的是两个物体共享指定接触点后的代数问题，并没有确认两个实际几何形状是否在此点碰撞。

## 路线二：重新编译、运行Box2D-Lite

本例只需要已有C++编译器，不需要官方图形界面或OpenGL。实际采用g++14.2.0，编译命令如下：

```sh
g++ -std=c++11 -O2 -I vendor/box2d-lite/include \
  engine_driver.cpp \
  vendor/box2d-lite/src/Arbiter.cpp \
  vendor/box2d-lite/src/Body.cpp \
  vendor/box2d-lite/src/Collide.cpp \
  vendor/box2d-lite/src/Joint.cpp \
  vendor/box2d-lite/src/World.cpp \
  -o box2d-driver
mkdir -p engine-output
./box2d-driver center 20 0 0 > engine-output/center.csv
./box2d-driver offset 20 0 0 > engine-output/offset.csv
./box2d-driver stack 1 0 0.3 > engine-output/stack-1-0.csv
./box2d-driver stack 1 1 0.3 > engine-output/stack-1-1.csv
./box2d-driver stack 10 0 0.3 > engine-output/stack-10-0.csv
./box2d-driver stack 10 1 0.3 > engine-output/stack-10-1.csv
./box2d-driver slide 10 1 0 > engine-output/slide-0.csv
./box2d-driver slide 10 1 0.3 > engine-output/slide-0.3.csv
python analyze_engine.py
```

命令行四个参数依次是场景、每步迭代轮数、热启动开关、摩擦系数。这个教学驱动假定使用上面列出的有效参数，并不是面向任意外部输入的完整应用。

本次采用官方erincatto/box2d-lite的固定提交227b71b6974ea57ab7e96d40f6374287bd6a0e77。核心源码未改，没有给它加上恢复系数e。

### 两盒碰撞

两个质量1、宽高1的均匀盒子。A初始中心(−2,0)或(−2,0.65)，速度(4,0)；B在(0,0)静止。无重力、无摩擦，关闭位置修正；步长1/240秒，360步，20轮求解，不热启动。

两物体的位置和转角由原World::Step推进。CSV记录固定小步后的结果，不是在精确首次接触时刻做连续求解。

### 箱堆

静态地板50×1，中心(0,−0.5)，上表面位于y=0。上面8个质量1、宽高1的盒子，第i只（从1开始）中心(0,0.51+(i−1)×1.01)。重力(0,−10)，全部摩擦系数0.3。步长1/60秒，共600步。

四种设置分别为1/10轮与热启动关/开。所有设置都开启累计冲量与位置偏置修正。对比只描述这个初态与观察时间，不保证其他场景或更长时间相同。

### 滑动

同样50米长地板。一个质量1、宽高1的盒子位于(−4,0.51)，初速(5,0)，重力(0,−10)。步长1/60秒，共240步，10轮、热启动和位置修正开启。两次运行分别把地板与盒子的摩擦都设为0或0.3。

## 只重绘，不重跑物理也可以

已有Python与Pillow环境时，在examples目录运行：

```sh
python render_engine.py
```

本次使用Pillow12.3.0。渲染器会重建rendered目录的32张PNG。它只消费已保存的CSV，因此不需要C++编译器。

例如[正中碰撞0.8秒](rendered/center-192.png)、[偏心碰撞0.8秒](rendered/offset-192.png)、[十轮热启动箱堆10秒](rendered/stack-10-1-600.png)、[有摩擦滑动4秒](rendered/slide-0.3-240.png)都是这条路径得到的实际输出。

正文GIF采样物理帧0、10、20……300，共31帧，每帧显示80毫秒（GIF时间单位为10毫秒，制作时请求83毫秒被格式量化为80毫秒）。物理采样间隔约41.67毫秒，因此播放经过时间不是模拟经过时间，具体以图上的t为准。正文图01是0、72、192帧的静态回退。

## CSV字段与核验边界

长度单位米，时间秒，质量千克，角度弧度。frame是小步序号，body是驱动数组中的物体编号；x/y、angle、vx/vy、omega为位置、转角、平移速度和角速度。width/height/mass为物体参数。

contacts与max_penetration来自求解器本小步保存的接触信息，而该行位置已完成本小步推进。不能把它们当成对当前绘图姿态重新几何测量的结果。第0帧还没执行接触更新，因此这两个字段为0。

地板使用源码规定的静态表示，CSV质量为FLT_MAX；做动态物体动量分析时不能把这个大数拿来制造无意义的静态能量。本文守恒复算只针对无地板、无重力、无位置修正的center与offset双盒运行。

跨编译器与浮点环境可能有数值差异。本次没有测帧率，没有实拍现实碰撞，也没有声称本例涵盖连续碰撞检测、复杂形状、3D旋转或完整的材料形变。

## 许可

本文新增的Python/C++示例采用[MIT许可](LICENSE)。vendor中的上游文件适用其各自保留的原许可；这份MIT文件不覆盖或替换第三方作者署名。本文原创结果渲染与解释图采用CC BY 4.0。
