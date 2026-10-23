## 核对与来源范围

本次实际运行了15000次固定种子随机缓存请求，每次输出与无缓存直接计算逐格比较，并检查容量计账；另用独立的简单列表LRU，对4个容量下全部3^6条六次请求串核对命中轨迹，共2916条。另用Fraction逐边插值核对8种输入组合的32个mip数组，共5440个输出格；还核对了动态项消失的七次请求边界与7项非法参数拒绝。这些是作者自查，不把它们称为第三方独立评审，也不声称测试覆盖所有可能的Python环境或历史引擎行为。

一手入口：
- [Abrash署名文章：Quake's Lighting Model: Surface Caching](https://valvedev.info/archives/abrash/chap68.html)，阅读了存档正文及Figure1、Figure3；存档不是id官网，但内容为作者署名技术原文，不用后人的博客代替其技术主张。
- [同档案Permissions and Author's Note](https://valvedev.info/archives/abrash/credits.html)，说明文章写作时期为1995—1997，2000年说明页将主要架构与所述多数技术归于Carmack，并列明复制条件。日期不混为同一事件。
- [id-Software/Quake的WinQuake/d_surf.c](https://github.com/id-Software/Quake/blob/master/WinQuake/d_surf.c)，实际阅读D_CacheSurface与D_SCAlloc相关段；未运行外站源码，也未重建完整引擎。
- [id源码README](https://github.com/id-Software/Quake/blob/master/readme.txt)，实际阅读代码许可与游戏数据保留权利段。本文不提供游戏数据。

原图权利：原Figure3对区分光照节点与可见纹理有信息价值，但档案许可要求未修改、非商业且文件保持一起；本篇没有据此获得摘取单图的复制许可，因此两张原图均不纳入交付，也不描摹其复合布局。16幅交付图均为独立创建的数值实验、表格或图表。它们不是游戏画面、硬件测量或历史照片。原作者保有原文原图权利；不主张原素材为开放许可。

本文没有复刻Quake：没有真实调色板、rover分配器、BSP/PVS、透视映射、真实动态灯、材质系统或纹理mip预处理。

## 编写与使用说明

正文由 AI 辅助编写，教学程序与数值示例经过实际运行核对。原创正文按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 提供；此声明不自动适用于图片、代码或第三方材料。第三方署名、限制和通知按上文及正文保留。
