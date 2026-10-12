# tech-articles

公开技术文章、科普长文与配图的独立存档。一份 Markdown 正文与相对路径素材同时服务微信公众号排版和网页阅读；公众号是主要发布渠道，网页是辅助展示。

## 许可

除非另有说明，本仓库由 zyuanming 发布的原创文章正文采用 [Creative Commons Attribution 4.0 International（CC BY 4.0）](https://creativecommons.org/licenses/by/4.0/) 许可。转载、改编和商业使用均应按许可要求署名、链接原文及许可，并注明修改。完整条款见 [CC BY 4.0 法律文本](https://creativecommons.org/licenses/by/4.0/legalcode.zh-hans)。

第三方图片、原文引用、商标及其他第三方素材不适用上述统一授权；其权利仍归各自权利人，复用时须遵循每篇文章和素材来源中列明的许可、署名及其他要求。未标注开放许可的素材，不因收录在本仓库而获得再授权。

## 内容组织

当前收录 120 份文章版本（含 1 份技术教学试稿）；6 组同题不同成稿保留相互链接，不把版本数当成独立选题数。文章目录见 [catalog.json](catalog.json)。

每篇位于 `articles/YYYY-MM-DD-slug/read.md`，图片使用相对路径。正文中的原有来源与事实边界保持，额外许可信息见各篇 `sources.md`。CERN NeXT 照片因分发条款限制，仅链接官方原页。内部研究资料、审读记录、凭据、运行日志及公众号后台状态不属于这个公开存档。

这是全新的独立仓库，不包含写作工程的私有 Git 历史。

## 更新文章与阅读网站

1. 在对应文章目录修改 `read.md` 与配图；保留高清原件、署名和许可通知。
2. 运行 `python tools/index_articles.py` 更新阅读目录及文件校验记录。
3. 运行 `python tools/validate_content.py` 检查正文、相对链接与素材字节。
4. 如需本地网站，安装 `requirements-site.txt` 后运行 `python tools/build_site.py`；静态输出位于 `_site/`。网站 HTML 完全由 Markdown 派生，不是第二份手工维护的正文。

公众号使用同一份 Markdown 和相对素材，在私有发布工程中加载真实 hash 绑定审读、视觉许可记录与独立封面。缺少这些输入时如实停在待补状态；公开归档或网站上线都不代表已经上传公众号。公开仓库不保存公众号凭据或后台状态。

受限图片的私有补充只放在私有工程，按各自许可使用；不扩大本仓库的素材授权。

## 学生探索系列

新增十篇由直觉问题逐步走到手算、实验与适用边界，覆盖游戏引擎、几何算法、信号与分布式系统，共184幅正文配图。阅读入口见 [学生探索系列](docs/student-exploration-2026-10-11.md)。教程代码与采样音频是相应文章的附属实验，使用限制见各篇说明。

新的六条探索路线正逐篇增加，已入库文章见 [探索系列续篇](docs/student-exploration-series-2026-10-11.md)。目录只列实际可读的完整成稿。

写作与配图约定见 [AGENTS.md](AGENTS.md)；它们约束后续新增内容，不回写历史成稿。
