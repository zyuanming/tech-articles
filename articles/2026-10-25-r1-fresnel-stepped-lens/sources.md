# 来源、许可与核验范围

本文是新写的几何光学教学文章。正文及原创 PNG 由 zyuanming 发布，采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，复用需署名、链接来源及许可、注明修改。配套 Python 代码与生成的数值 JSON 按 [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) 提供。第三方作品不受这两项统一授权覆盖。

## 事实来源

1. [NPS：Fresnel Lens](https://www.nps.gov/articles/fresnel-lens.htm)，页面更新于 2024-07-25。已核可读正文，支持灯塔的多玻璃片组件、固定与旋转照明、闪光特征等背景。本文不把该页的视距数字移用成教学模型性能，也不据此声称每套历史装置结构相同。
2. [NPS：The Fresnel Lens，Anacapa](https://www.nps.gov/chis/learn/historyculture/fresnellens.htm)，页面更新于 2016-06-10。已核可读正文，支持 Anacapa 的三等旋转折反射装置、1932 年安装和后来展示的叙述；其透镜制造年与安装年没有混用。照片署名 Reed McCluskey/NPS，但原像素本次未取得，没有复制该图。
3. [Edmund Optics：Advantages of Fresnel Lenses](https://www.edmundoptics.com/knowledge-center/application-notes/optics/advantages-of-fresnel-lenses/)。已核全文主体的可读文字、五个有关图像条目与视频入口，支持现代环槽透镜的用途、制造概述和槽面朝向说明。本文没有取得该厂商图像的再分发许可，未复制其图。厂商关于常用安装方向的说明不等于本例薄元件局部斜面模型的最优性证明。
4. [法国文化部：Cordouan’s first lens](https://cordouan.culture.gouv.fr/en/cordouans-first-lens)。仅检索定位，正文读取未成功；没有据搜索摘要写入 1823 年或该页尺寸。它不是本文已核事实的依据。

Snell 定律、界面反射系数与薄透镜近轴关系用于公开、可复算的教学推导。具体半径、焦距、折射率、槽距、坏区宽度和有限物距例子均是本文输入；数字不是从任何实物测得。特别是 1.48/1.49/1.50 没有绑定实际波长，不是某种材料的色散表。

## 已采用的第一方现代实物与效果照片

[June Glasses 固定快照](https://github.com/perseus784/June_Glasses/tree/5cb0a0e185b1e890d7701af918ed61c152dd4a54)，项目作者 Paarvendhan（GitHub: perseus784）。已读取完整 README、根 LICENSE，采用照片已逐张查看实际原像素，并与原文件核对字节。该快照的提交日期为 2020-09-04，不作为照片拍摄日期，也不作为项目首次制作日期。

许可判断范围：根许可证为 GNU GPL v3，README 以第一人称叙述自制装置并连续展示制作与测试照片，媒体目录未另列排除许可。结合这些证据，本篇按项目自身文档照片随项目 GPL v3 分发的范围采用；不是仅凭“GitHub 公开”推定自由使用，也不是摄影者另行逐图授权的声明。该判断不覆盖作者外链、第三方界面、商标或肖像的其他权利。

以下七件照片与正文/原创图保持可分离，均保存未修改 JPEG；只更换本地文件名，不裁切、不重编码、不加字、不拼图。照片采用 GNU GPL v3，不适用本文原创 CC BY 4.0。随附[完整上游 LICENSE](originals/LICENSE-June-Glasses-GPL-3.0.txt)，包括再分发条件及免责通知；原照片与可下载文件为同一字节。完整尺寸、上游文件名、固定版本及 SHA-256 见[照片清单](originals/photo-manifest.json)。

| 本文原件 | 上游文件 | 新增作用 |
|---|---|---|
| [纸板开口](originals/photos/june-cardboard-2.jpg) | cardboard(2).jpg | 真实装配中局部环纹与透明组合片分开辨认 |
| [塑料壳模块](originals/photos/june-making-2.jpg) | making(2).jpg | 开口、模块本体与电线关系 |
| [整机前侧](originals/photos/june-device-2.jpg) | device(2).jpg | 物件身份，明确前伸大片是反射组合片 |
| [整机内侧](originals/photos/june-device-3.jpg) | device(3).jpg | 不同视角确认模块与镜架关系 |
| [桌面视野效果](originals/photos/june-hud-2.jpg) | hud(2).jpg | 透明视野边界与真实文字叠像同框 |
| [浅背景效果](originals/photos/june-hud-4.jpg) | hud(4).jpg | 真实相机记录及局限 |
| [深背景效果](originals/photos/june-hud-6.jpg) | hud(6).jpg | 不同环境中的可见叠像，不作定量对比 |

这些照片支持现代自制装置的存在、元件使用与相机记录的可见效果，不提供本文模型中的折射率、焦距或槽距；不证明裸片全部环纹、制造截面、人眼清晰度或历史灯塔结构。本文没有执行上游设备程序。README 中关于人眼近点、透镜普遍清晰度等简化说法没有当作一般光学规律转述。

## 未采用的历史对象照片范围

以下两个摄影作品的作者、作品描述和许可文字已核到；图链接只定位到了资源，未得到可供本次目视核验的原像素。它们没有嵌入正文或存入本篇图片目录，不能把许可已核写成原图已看。

- [Pöllö：Fresnel lens system of Soderskar lighthouse.JPG](https://commons.wikimedia.org/wiki/File:Fresnel_lens_system_of_Soderskar_lighthouse.JPG)，描述为 Söderskär 灯塔透镜系统，页面列日期 2008-07-20，作者自摄，标为 [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)。若后续依法采用，应署名 Pöllö、链接作品与许可，并注明裁切或其他修改。
- [Pöllö：The sea seen through a Fresnel lens system.jpg](https://commons.wikimedia.org/wiki/File:The_sea_seen_through_a_Fresnel_lens_system.jpg)，描述为从 Bengtskär 灯塔透镜系统看芬兰湾海面，页面列日期 2009-07-27，作者自摄，标为 [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)。元数据另有相邻日期，本文不据此推断精确拍摄时刻。原像素未核，不能声称已看到了具体畸变。

Anacapa 的机构照片亦未取得原像素。NPS 署名不能自动推成全部网站素材都是公有领域；本篇未复制它，也未外推授权。上述真实对象可由原页进一步查阅。原创光线图不弥补历史装置实物照片的缺口。

## 原创图逐项用途

| 文件 | 新增理解作用 | 身份与范围 |
|---|---|---|
| 00-cover.png | 独立封面建立不同高度光线聚向同一点的任务 | 薄参考面模型 |
| 01-steps.png | 连续轮廓、分区和轴向移近三个阶段 | 概念截面，不按加工比例 |
| 02-snell.png | 区分光轴、法线、入射角、出射角和偏转角 | r = 40 mm 实算局部放大 |
| 03-rays.png | 从各半径逐一反求所需法线倾角 | 单色轴上理想模型 |
| 04-translation.png | 反驳保持方向就保持落点 | 1 mm 平移实算，图中移位放大 |
| 05-sphere.png | 同近轴焦距的球面局部方向仍可不同焦 | 换曲面方向，非厚球面追迹 |
| 06-zone.png | 同一个平槽内三条光的落点不同 | 30～40 mm 环带局部展开 |
| 07-pitch.png | 同轴比较三种槽距的径向残差 | 模型输出，非测得焦斑 |
| 08-edges.png | 槽缘固定宽度与槽距之间的代价 | 局部假设占比，非总效率 |
| 09-dispersion.png | 固定工作面改变 n 后不能同焦 | 三个假设 n，颜色仅编码路径 |
| 10-loss.png | 材料变薄后界面反射仍在 | 未镀膜、无吸收、首程直透 |
| 11-reverse.png | 将聚光路径倒过来理解准直 | 同一理想路径反向，非灯塔结构 |
| 12-imaging.png | 区分接住光与物点成像 | 换用薄透镜近轴近似 |
| 13-ring-section.png | 正面环带对应径向截面、分清工作面与槽壁 | 模型结构示意，不是加工图 |

所有原创图均新制作。图像数据来自实际运行的 `examples/trace.py` 与 `results.json`；没有伪造终端、工具界面或实验照片。它们不声称设备实测。详见[逐项来源视觉库存](source-visual-inventory.md)。

## AI 辅助与验证

本稿使用 AI 辅助检索公开出处、组织教学结构、推导与编写程序、生成中文标注和自查。计算代码实际执行，图像由代码实际生成；没有把模型输出称为真实硬件性能。作者检查了原创图的原尺寸与手机比例代理，代理不是浏览器截图。几何检查与数学、事实、图义判断是不同验证范围；来源读取受限的范围保留如上。
