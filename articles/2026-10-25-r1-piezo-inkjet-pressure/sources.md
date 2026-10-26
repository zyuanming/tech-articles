# 事实、图像与许可

本文为全新中文解释与教学推导。正文及assets目录中的原创PNG由zyuanming发布，采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；Python代码与原创计算JSON采用[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/)。第三方材料独立标注，不受上述原创内容许可覆盖。

## 一手事实来源

- [MicroFab：Ink Jet Microdispenser](https://www.microfab.com/support/a-basic-ink-jet-setup/ink-jet-microdispenser)。已读完整解析正文，支撑管式压电器件、极性与变形、负压波向两端传播、供液端反射、液面移动与频闪观察。厂商图没有查到开放复用许可，未复制其照片、过程帧或结构图；原创图只说明自行设计的教学对象。
- [MicroFab：Drive Electronics](https://www.microfab.com/support/a-basic-ink-jet-setup/drive-electronics)。已读完整解析正文，支撑单极、双极、多段驱动以及时序和观测的角色。不将特定型号的电压限制或默认参数推广到其他设备；未复制其波形图或软件界面。
- [Herman Wijshoff，Drop formation mechanisms in piezo-acoustic inkjet，2007](https://briefs.techconnect.org/wp-content/volumes/Nanotech2007v3/pdf/696.pdf)。已读4页完整解析文字与图注，支撑声阻抗反射、实际观测与模拟的区别、尾部断裂与卫星类型、补液和喷嘴板润湿。未取得原版图像像素，未复制论文的实拍或Flow3D模拟图。正文数值没有使用论文中的设备参数。
- [CentroEPiaggio / IPJ-Bio项目](https://github.com/CentroEPiaggio/IPJ-Bio)。已读README与完整根许可、核对项目文件，并查看原装配图。用于设备构造的真实例证，不独立核验README提到的细胞存活实验，不作医疗结论。
- [Cavaleiro de Ferreira等，Development of an Inkjet Setup for Printing and Monitoring Microdroplets，2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9694169/)。实际已读解析文本第0—376行对应的内容，涵盖方法、结果、图1—9与表1—2的文字；补充材料只定位到清单，没有读取原文件。它使用落地滴图像进行监测，不能当作断滴高速序列。此前原图访问受到浏览器检查限制，未取得像素；2026-10-26 从用户提供的出版版PDF核验并提取图7a–e原嵌入PNG，本次采用a/e两个面板，详见下列补材说明。原访问限制记录保留，没有重访受限图页。

正文中的纳米位移、1µL腔体、30pL自由行程、顺应性、10mm声学距离、30µm喷嘴及液体参数全部是教学设定。封闭压力、脉冲叠加和局部流量是三个边界条件不同的计算；图与数值不声称设备测量、自由表面仿真或商业喷头拟合。几何、守恒、牛顿第二定律、圆管层流近似和无量纲换算由本文自行展开并复算。

## 逐图身份与作用

| 文件 | 理解作用 | 身份与许可 |
|---|---|---|
| assets/00-cover.png | 建立电压、壁面、压力波与液滴链条 | 全新原创示意，CC BY 4.0 |
| assets/01-structure.png | 辨认储液器、腔、驱动层、喷嘴与液面 | 全新原创概念剖面，CC BY 4.0 |
| assets/02-wall-motion.png | 比较扩腔和回缩，不固定所有器件极性 | 全新原创示意，CC BY 4.0 |
| assets/03-volume-account.png | 区分封闭压力极限与开放液路流量 | 原创示意与设定参数计算，CC BY 4.0 |
| assets/04-reflection.png | 呈现波的往返方向与时间 | 原创声学近似示意，CC BY 4.0 |
| assets/05-wave-timing.png | 共轴显示配准/错开的叠加差异 | 实际计算的线性脉冲模型，CC BY 4.0 |
| assets/06-nozzle-forces.png | 解释惯性、阻力与毛细的压力预算 | 原创集中参数示意，CC BY 4.0 |
| assets/07-flow-curve.png | 区别瞬时流量与时间积分体积 | 实际解析模型输出，CC BY 4.0 |
| assets/08-breakup.png | 指认液柱、细颈、主滴与可能的卫星 | 原创定性形状，非模拟，CC BY 4.0 |
| assets/09-viscosity.png | 同尺度比较只改变黏度的体积响应 | 实际解析模型输出，CC BY 4.0 |
| assets/10-deposition.png | 区分飞行球径与落地铺展 | 原创球冠计算，两球冠等体积同尺度，CC BY 4.0 |
| assets/11-voltage-stages.png | 对应电压边沿与壁面动作 | 全新原创波形示意，CC BY 4.0 |
| originals/photos/ipj-bio-assembled.jpg | 辨认真实项目的部件与装配 | 第三方CAD及实物合图，GNU GPL v2，见下 |
| assets/12-rump-formation.png | 辨认真实液柱伸长与脱离，比较喷前闲置条件 | Rump等图6a/b页面截图局部，CC BY 4.0，非高清原图 |
| assets/13-ferreira-deposit-a.png | 看3500 DAC设置的真实沉积轮廓与标尺 | Ferreira等图7a原像素裁切，CC BY 4.0 |
| assets/14-ferreira-deposit-e.png | 对照2700 DAC设置的沉积，区分驱动与滴径 | Ferreira等图7e原像素裁切，CC BY 4.0 |

## IPJ-Bio原件通知

来源：CentroEPiaggio / IPJ-Bio项目，原路径[Mechanics/assembled.jpg](https://github.com/CentroEPiaggio/IPJ-Bio/blob/33806b218e556edcab5219b16a0e871598955aed/Mechanics/assembled.jpg)，固定提交`33806b218e556edcab5219b16a0e871598955aed`，取得日期2026-10-25。

本库[原件](originals/photos/ipj-bio-assembled.jpg)保留3397×1902像素和原始3,740,538字节，未裁切、未添加标注、未重编码。左a是CAD分解，右b是实物照片；不将整幅称为实拍，也不将CAD重绘称为真实设备内部照片。SHA256为：

5d3e9f186515a482d53fc84ca3c9d23f49d8dbee61602ff71ddcb4686fef9fbd

按该第一方项目根目录GNU GPL Version 2许可，以项目文档原文件身份再分发；保留[完整许可](originals/ipj-bio/GPL-2.0.txt)与[原README](originals/ipj-bio/README.upstream.txt)。这不是作者逐图另发的CC授权，也未查明单独摄影者。判断依据是项目自述的设计制造范围、文件所在Mechanics目录、根许可适用全项目及未见相反的逐图版权通知；不是把任何代码仓库许可外推给第三方转载照片。

上游同时提供机械STL及电路源文档，可从[固定版本目录](https://github.com/CentroEPiaggio/IPJ-Bio/tree/33806b218e556edcab5219b16a0e871598955aed)取得；不声称存在未公开的JPEG可编辑合成文件。另一张项目电路PNG已登记但未转载：本文不讲电路设计，真实装配与原创驱动机制已承担本篇相关职责。

## 真实效果的历史STOP与本次补材

此前本稿仅有装配实物，真实液滴过程和落地效果构成STOP / HOLD缺口。MicroFab过程帧未查到开放许可；2022论文图页未取得像素。另查[Hashemi等2025预印本](https://arxiv.org/html/2501.13801v1)，已读完整解析正文，论文图文件访问受限；已取得的作者样本另受数据许可约束，具体版本未核实，未转载。原创断滴示意与模型曲线不能替代这些实证。2026-10-26 补入下面两项用户提供材料，分别承担真实形成过程与实际沉积的职责；未获准的Hashemi样本仍不采用。

## AI辅助与验证范围

本篇中文组织、代码、计算、图形与来源核对使用AI辅助。公式和数值实际运行，图的字号、包围盒、字形、对比与比例经过程序检查，并实际查看原图与手机比例静态代理。没有实际连接喷头、测量压力或拍摄液滴。照片为来源作者记录。静态代理不是平台截图，程序检查也不是独立审读结论。

## 2026-10-26 补入的真实材料

### Rump：喷射形成快照

Maaike Rump, Christian Diddens, Uddalok Sen, Michel Versluis, Detlef Lohse, Tim Segers, *Role of surfactants on droplet formation in piezoacoustic inkjet printing across microsecond-to-second timescales*, [arXiv:2406.02389v2, 31 October 2024](https://arxiv.org/html/2406.02389v2)。上游该版本明确列出 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)（[完整许可](https://creativecommons.org/licenses/by/4.0/legalcode)）。作者及版本、许可依据该第一方版本页；用户提供的第18页PNG本身没有题名或许可，不能仅凭截图独立认证这些信息。截图中的图6编号、70 µm喷嘴、1 CMC Dynol、2 ms/50 s闲置及图注与已核版本文字相符；未取得原站图文件，未做逐像素同一性比对，不称原尺寸图。

原始用户页面截图保存为 `originals/papers/rump-2024-figure6-page.png`，1232×1692；SHA-256 `9a417103b5f443b6663b23b1e3a0f7d9026ddf3471bd2e92261b46a0e4de90b5`。正文 `assets/12-rump-formation.png` 只裁取图6a/b：像素坐标左140、上543、右566、下828（左上为原点，右/下不含），426×285。没有插值放大、修补、锐化、生成或改写原标记；新增中文解释在正文，不嵌进原像素。完整页保留以核上下文，但不要求读者在手机放大整页才能理解主线。

图6a/b的10–120 µs是形成过程时刻；2 ms/50 s是喷前闲置。1 CMC为临界胶束浓度条件，不能把它当作本文设定的30 mN/m常数表面张力。图6中其他面板和文中方法另有速度、断开时刻、振荡法表面张力及统计；本稿不据裁出的a/b重新拟合这些曲线，不把快照叫作同一滴连续高速录像。正文中1 kHz、999滴与闲置后单次驱动来自该版本实验方法说明，不来自图像像素。

完整原图注：

> FIG. 6. Time-lapsed snapshots of droplet formation of 1 CMC Dynol from a 70 μm nozzle diameter for an idle time of (a) 2 ms and (b) 50 s. (c) Overlap of the droplet shapes at 100 μs from the experiments: 2 ms idle time in red and 50 s idle time in blue, showing clear differences. (d) The position of the liquid front for multiple idle times. (e) The velocity of the liquid front for multiple idle times. (f) The pinch-off time of the liquid column from the nozzle for multiple idle times; inset shows the length of the liquid column just after pinch-off from the nozzle for multiple idle times. (g) The surface tension measured from the head droplet’s oscillations for multiple idle times. The datapoint markers in (f) and (g) represent the mean while the error bars denote the standard deviation from at least three independent experimental realizations.

署名：Rump、Diddens、Sen、Versluis、Lohse、Segers；图6未另列摄影者。沿用原作CC BY 4.0，注明上述裁切和中文说明。截图第17页的图5也已核读，但与本文职责重复，未转载；不因此声称收齐论文全部图像。

### Cavaleiro de Ferreira：已沉积液滴

Beatriz Cavaleiro de Ferreira, Tiago Coutinho, Miguel Ayala Botto, Susana Cardoso (2022), *Development of an Inkjet Setup for Printing and Monitoring Microdroplets*, **Micromachines 13**, 1878, [DOI:10.3390/mi13111878](https://doi.org/10.3390/mi13111878)。用户提供出版版PDF共15页，首页 © 2022 by the authors, Licensee MDPI，采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)（[完整许可](https://creativecommons.org/licenses/by/4.0/legalcode)）。图7无单列第三方摄影署名或排除条款；图1注明改编自其他文献，本稿不采用图1，不将本许可泛化到所有第三方材料。

PDF SHA-256：`b58d81df5f94b884237d9dc73d1bab4807abf9823a78d4e224fa848b15cef22f`。图7位于PDF第10页：`originals/photos/ferreira-2022-figure7a-e.png` 为a–e五幅照片的原嵌入PNG，无损抽取，2439×480。正文a面板 `assets/13-ferreira-deposit-a.png` 裁切(172,0,621,480)，449×480；e面板 `assets/14-ferreira-deposit-e.png` 裁切(1992,0,2439,480)，447×480。保留a/e原编号、红色识别轮廓及50 µm标尺；未缩放、未改变明暗或轮廓，未把不同驱动条件误排成连续时序。原图f–h的统计和驱动曲线未转载；正文不从代表照片推算全部数据。

完整原图注：

> Figure 7. Evolution of the droplet diameter in terms of the amplitude of the actuation pulse. In (g) the first sequence of applied amplitudes of the first test is shown, which decreases from 3600 DAC units (0 s) to 2500 DAC units (919 s). In (f) the respective average diameters identified by the monitoring system and standard deviation are depicted. (a–e) show examples of the captured droplets for such a sequence of decreasing amplitude, namely, (a) 3500 DAC units, (b) 3300 DAC units, (c) 3100 DAC units, (d) 2900 DAC units and (e) 2700 DAC units. (h) shows an example of an actuation pulse.

本次AI辅助补充中文读图、许可整理与一致性核查；真实实验、照片及红色轮廓属于原研究团队。新图只补真实视觉证据，不更改原创模型计算，不代表本文实际使用过任一喷头，也不将不同实验的材料和设置拼成同一组验证。
