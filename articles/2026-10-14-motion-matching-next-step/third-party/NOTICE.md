# CMU真实动作数据与派生图：独立条件

## 来源与致谢

数据来自[CMU Graphics Lab Motion Capture Database](http://mocap.cs.cmu.edu/)。该数据库由NSF EIA-0196217资助建立。感谢Carnegie Mellon University Graphics Lab提供公开动作数据。本文作者的解析、实验和图解不表示CMU认可或担保结论。

[数据目录：subject16](http://mocap.cs.cmu.edu/search.php?subjectnumber=16)。本次随文保留四份原始文件，2026-10-14取得；没有改写、裁剪或补造原始记录：

- [16.asf](../originals/cmu/16.asf)，7257字节，SHA256：2323f876564610f84bfbec9b90b8ebffb57515673b7f4a45b0fb0849af465bdb。
- [16_15.amc](../originals/cmu/16_15.amc)，375603字节，SHA256：0873a7753a04c34de2a94dc768b61ef4ed8395f0bd351c2019864b16883b0f89。
- [16_17.amc](../originals/cmu/16_17.amc)，413355字节，SHA256：a59f9c90eb2af8197c6390edddbcf761bbec1cf03b6907128212102fe2123a2c。
- [16_19.amc](../originals/cmu/16_19.amc)，326604字节，SHA256：691d578a676bf9e091dac59001a6cb78daa7141ad5639f943c684dee7f4e64e6。

下载源为CMU官方subjects/16目录中的同名文件，例如[16.asf原件](http://mocap.cs.cmu.edu/subjects/16/16.asf)。ASF在服务器上可能被标为video/x-ms-asf，但这里的内容是文本骨架格式，不是视频文件。

## 使用条件

CMU[首页](http://mocap.cs.cmu.edu/)允许研究使用及商业产品使用，但禁止直接转售这些数据或其转换版本；[FAQ](http://mocap.cs.cmu.edu/faqs.php)明确允许复制、修改和再分发动作数据。首页另请发表者致谢数据库，本文已在上方保留致谢。

这是CMU站点给出的特定条件，**不是CC0、CC BY或MIT数据许可**。复用时应阅读上述完整原说明并保留适当来源与致谢；不要把数据或转换版本本身拿去直接转售。本文的原创正文、解释图许可不替代CMU条件。

## 本篇做了哪些转换

- 将ASF骨段长度和AMC根平移换成米；根据静态轴、逐帧角度和层级计算骨段末端。
- 从根朝向建立地面局部坐标，提取左脚尖前向位置及半秒后的地面位移；保存完整特征与检索得分。
- 选择注明的源帧，以原创线条、投影、颜色、文字标注和地面网格绘制；省略手指与拇指小骨段。没有使用第三方人体网格或商业游戏角色模型。
- 第2图分别平移展示位置；第12图保留相对初始地面轨迹；第14图每4源帧取一幅，另加首尾显示停顿；第15图比较已对齐起点的两个姿势。

包含CMU派生内容的公开文件：assets/01-input-pose.png、02-frames-and-continuation.png、12-real-library.png、13-real-query.png、14-real-playback.gif、15-remaining-jump.png；examples/features.csv、render-samples.json、expected-results.json中的real/files等真实数据部分；originals/experiment-stdout.txt中的真实数据结果。它们保留本说明所列的原数据条件，不以正文CC BY 4.0一并替换。

其余人工教学例、纯解释图与文字为本文原创。原始文件没有加水印或修改字节。骨架图是数据派生绘制，不是现场录像、原始相机标记点、原作者截图或“已实现游戏效果”的证据。
