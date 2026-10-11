# 来源与素材

原创中文正文由zyuanming发布，CC BY 4.0。图片、代码与商标不因正文声明自动获得同样许可。

## 明确版本的一手资料

- Unity Entities 1.0文档当前固定文档元信息实际为1.0.16，页面生成时间2024-02-22；本文据此写1.0.16，不称最新版本。Archetypes concepts：https://docs.unity3d.com/Packages/com.unity.entities@1.0/manual/concepts-archetypes.html 。同组件集合、16KiB块、各类型数组、实体ID数组、紧密填洞。页中仅品牌logo与小型archetype图标，无核心解释图；图标不作无信息量装饰。
- Structural changes concepts，版本1.0.16：https://docs.unity3d.com/Packages/com.unity.entities@1.0/manual/concepts-structural-changes.html 。增删组件引起迁移、普通组件值变化不属于结构变化、直接引用失效、同步点及命令缓冲。
- Entities concepts，版本1.0.16：https://docs.unity3d.com/Packages/com.unity.entities@1.0/manual/concepts-entities.html 。实体身份与数据的区别。
- Bevy ECS 0.16.1官方包README：https://docs.rs/crate/bevy_ecs/0.16.1 。实体/组件/系统、查询、系统访问分析、显式依赖、Table默认与SparseSet可选。本文不把0.16.1功能写成当前所有版本保证，也不引用工具后来可能跳到latest页的内容。
- 所有对象编号、坐标、64字节对象/缓存行、理想对齐及M次读取范围均为自建教学设定。缓存行计数实验只计算假定地址，不声称测量硬件缓存、DDR流量或游戏帧率。

## 第三方图：真实官方编辑器截图

目标视觉页：https://docs.unity3d.com/Packages/com.unity.entities@1.0/manual/editor-archetypes-window.html 。正文只有一张编辑器图（另有导航logo），该图仅在原文链接查看，未收入公开稿。

- 原文件：https://docs.unity3d.com/Packages/com.unity.entities@1.0/manual/images/editor-archetypes-window.png
- 公开稿仅链接原站，无本地图片引用
- 作者/机构：Unity Technologies
- 内容：Entities 1.0.16官方文档示例项目的Archetypes窗口，不是本文实验截图
- 未对原图作改动；因非商业许可范围不适合不明后续用途，仅链接原页
- 许可依据：该页面页脚直接链接 https://docs.unity3d.com/Manual/TermsOfUse.html ，其中非代码手册/参考资料条款为CC BY-NC-ND 4.0：https://creativecommons.org/licenses/by-nc-nd/4.0/ 。未取得商业复用依据，不以本篇原创正文的CC BY 4.0声明扩大该图的权利范围。

## 原创解释图与可复现实验

16张原创PNG各1152×832。01-scene为四个实体及PVH组件；02-query为P/V交集；03-update为0.5秒更新位置；04-used-fields为移动只读P/V；05-aos-lines为8×64字节对象；06-soa-lines为两组8×8字节组件；07-traffic为触及512/128字节的算术，不是4倍性能；08-component-inside区分组件与字段；09-archetypes三种集合分组；10-chunk-rows为同一行对应同一实体；11-migration为30加V迁组；12-swap-remove临时加入50演示填洞；13-defer为命令回放；14-schedule为数据依赖；15-storage-tradeoff为无数值的定性取舍；16-id-map为稳定身份和可变存储位置。

examples/experiment.py包含两个独立小实验：标准库字典查询/坐标更新；假定地址的不同缓存行集合计数。两者实际运行并含断言。字典示例没有连续内存或引擎跑分结论。

本文使用AI辅助调研与写作；原创教学图按明确设定由代码生成，合成演示与真实来源图已区分。
