# 资料与视觉素材清单

本文：《游戏里的烟，怎样跟着空气卷起来？》。核对日期：2026-10-14。

## 一手依据与边界

1. Jos Stam，[Stable Fluids](https://www.josstam.com/_files/ugd/cf1fd6_898fe9b63df946689101b8d074f8efba.pdf)，SIGGRAPH 1999，pp.121–128；[正式DOI书目](https://doi.org/10.1145/311535.311548)。实际核对了作者公开版本的8页全文及所有原图。此处PDF页码按文件第1至8页计：
   - 第1至3页：图形动画动机、搬运/扩散/投影的组合与稳定性解释。
   - 第2页：明确承认过强数值耗散及多数工程用途的精度局限。
   - 第4页：原实现采用格心速度样本。
   - 第5页：较复杂的轨迹追踪；不是本文一次直线回溯的逐行原型。
   - 第6页：自由表面问题不在其处理范围内。
   - 第8页Fig.4：原算法的渲染结果。希望看历史原始视觉的读者可直接看此页。
2. Jos Stam，[Real-Time Fluid Dynamics for Games](https://www.josstam.com/_files/ugd/cf1fd6_9989229efbd34a26ba5ccd913721a2ac.pdf)，GDC 2003。核对相关文字及PDF第7、8、10、12、13页：直线回溯、四邻插值、两次投影的速度更新次序、耗散局限和历史说明。它与1999版不是逐项完全相同的实现。
3. [作者Publications目录](https://www.josstam.com/publications)：用于核对两项作品身份。本文不声称Stam发明了流体方程、投影法或回溯插值本身；2003历史说明也把相关思路追溯到更早工作。
4. [NASA/LaRC，Smoke Flow Visualization for SLS](https://www.nasa.gov/image-article/smoke-flow-visualization-sls/)，页面日期2013-09-20：仅支撑真实烟流可视化试验场景和图片身份，不作为本文算法精度的验证。
5. [NASA Images and Media使用规范](https://www.nasa.gov/nasa-brand-center/images-and-media/)：核对教育/资讯用途、署名、第三方材料、可辨人物、机构标识及不得暗示背书等条件。不能推成“所有NASA照片、所有用途都自动自由使用”。

两篇论文的原图未核得适用于本项目的开放转载许可，因此提供作者原文和准确页码链接，没有把原论文截图放入本文，也没有把原图换色描摹后冒称原创。作者站公开下载不等于取得转载许可。

关于凸权重的范围、四格联立求解、离散相容算子和守恒区别的解释，来自本文明确给定的教学模型与实际重算；不是把作者论文未写的句子假托给作者。

## NASA照片原件

- 原URL：[smoke_test_7.jpg](https://www.nasa.gov/wp-content/uploads/2023/03/smoke_test_7.jpg)
- 原件：[originals/nasa-sls-smoke-test-7.jpg](originals/nasa-sls-smoke-test-7.jpg)，1041×781，142,534字节。
- 正文文件assets/02-nasa-smoke-flow.jpg与原件逐字节相同，未裁剪、改色或生成补绘。
- 信用：NASA/LaRC；页面未标明另一个第三方版权持有人。
- 本文采用其真实试验场景用于教育/资讯解释，图注保留机构信用和出处。图中有可辨人物，不用作本文推广封面、广告或产品包装，也不暗示图中人士、NASA或LaRC认可本文内容。
- 照片不是本文拍摄、不是Stable Fluids渲染，也不是AI生成。NASA不负责本文原创模型、程序或解释的准确性。

## 原创视觉逐图职责

| 文件 | 新增的理解作用与数据身份 |
|---|---|
| 01-computed-sequence.png | 同一实际运行的第0/10/20/40步；先见染料被卷动，四幅不是四套方法 |
| 02-nasa-smoke-flow.jpg | 现实中的烟流可视化对象与工具；唯一第三方正文照片，权利如上 |
| 03-dye-and-velocity.png | 同一第20步的染料和速度，区别亮度与运动方向；箭头为格心平均后稀疏展示 |
| 04-backtrace.png | 同一目标(2,2)向旧位置(0.5,0.75)回查，网格不随之移动 |
| 05-bilinear-two-stages.png | 手算四角0/4/8/12，经水平2/10再得8 |
| 06-convex-weights.png | 具体非负权重与数轴解释不产生新极值的原因 |
| 07-explicit-vs-backtrace.png | 同一初态、移动1.5格的一步反例，明确仅比较所选显式上风式 |
| 08-implicit-diffusion.png | 独立两格(0,12)联立新值得到(4,8)，解释“隐式” |
| 09-volume-balance.png | 固定体积流入3、流出1的失衡，建立不可压缩约束 |
| 10-four-cells-before.png | 独立封闭四格与共享流量，揭示各格不能独立修正 |
| 11-four-cell-potentials.png | qA=0、qB=2.5、qC=0.5、qD=2如何改变同一条边 |
| 12-four-cells-after.png | 校正后保留0.5环流；每格平衡不代表速度归零 |
| 13-mac-storage.png | 本文现代原创MAC实现的样本位置，区别原论文格心实现 |
| 14-projection-measured.png | 第一步实际投影前后散度热图与速度箭头，同一标尺不夸大差异 |
| 15-one-step.png | 对应实际程序的阶段次序，说明两次投影及当前关闭的物理项 |
| 16-dissipation-measured.png | 同一运行第0/120步，黏性/染料扩散为0时仍出现耗散和总量变化 |
| 17-repeated-interpolation.png | 独立恒速平移、同终点不同插值次数，区分轨迹误差与糊化 |
| cover.png | 独立封面，使用原创第20步实际计算的等比中央裁切，不采用NASA人物照片 |

原创图可由[制图脚本](examples/build_figures.py)及[复现说明](README.md)重建。颜色、数字和坐标均对应明确模型；不是实物测量图。保存的[预期结果](examples/expected-results.json)包含输入、环境、每步统计和测试值；[图像元数据](examples/figure-metadata.json)记录原创图作用及有效字号。图中没有统一装饰性AI历史照片或伪游戏界面。

## 许可与AI辅助

- 原创正文、解释图、计算结果图：Creative Commons Attribution 4.0，见[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。
- 原创求解器和制图脚本：MIT，完整文本见[LICENSE-CODE.txt](LICENSE-CODE.txt)。
- NASA原图及其副本：适用NASA机构规则，非本文CC BY许可授予对象。论文、作者页面与第三方软件各归其权利人。
- AI辅助用于资料检索、教学结构、文字起草、原创程序和图形代码、核算与审读。数值由公开随文代码实际运行得到；解释图由Pillow绘制，未使用生成式图像伪造照片或实验。NASA照片保持原始身份，不能把AI辅助内容归为NASA作品或暗示NASA审核。
