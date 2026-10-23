# 来源、素材权利与 AI 辅助说明
- Maged M. Michael，《Hazard Pointers: Safe Memory Reclamation for Lock-Free Objects》，IEEE TPDS 15(6)，2004。实际读取公开论文web返回的首页与机制介绍：说明共享引用为何不能随移除立即回收、单写多读保护槽与退休后扫描的基本设计。这里不复述其性能实验，也不把其进度结论扩大到本文代码。[原论文公开地址](https://www.eecg.utoronto.ca/~amza/ece1747h/papers/hazard_pointers.pdf)。
- WG21 P1121R3，2021-04-09，Michael等，《Hazard Pointers: Proposed Interface and Wording for Concurrency TS 2》。本地实际阅读机制、域、使用示例及保护期相关段，实际查看第5页。它帮助确认保护期和延后回收的区分；这是当年的提案，不是本文声称的现行C++标准API。[原提案](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p1121r3.pdf)。
上面两项是概念与历史定位，正文的所有具体调度数、错误轨迹、集合数据、成本算例与有限模型论证均由本文自写实验生成或推导，没有复制原论文的性能结果/算法代码。

提案机制页以文字条列为主，作为本地核证有价值，但复制页面不能替代本稿逐事件实验；没有确认可将原页图像用于本次发布的授权，因此不将原页纳入交付，不描摹其排版。2004论文原图未实际取得，也不纳入交付。16幅交付图全部独立制作，不主张原论文或提案有开放图像许可。本文不提供法律许可判断，也不提供生产C++内存序配方。




## AI 辅助与许可范围

本文使用 AI 辅助资料整理、讲解撰写、教学代码和原创图示制作；实验结果来自文中说明的实际程序运行，不是实地或生产系统测量。

原创文章正文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。这一正文许可不自动适用于代码、图片和第三方素材；第三方材料保留文中列明的原作者、许可与限制。
