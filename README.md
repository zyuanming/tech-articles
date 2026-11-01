# tech-articles

中文技术长文的公开存档。每篇都从一个人能想明白的问题出发，走到能手算、能跑代码、能说清边界的地方。

## 在线阅读

**https://zyuanming.github.io/tech-articles/**

首页可按标题搜索、按日期筛选。单篇网页的地址形如：

```
https://zyuanming.github.io/tech-articles/articles/2026-11-02-lz77-sliding-window/read.html
```

也可以直接在 GitHub 里点 `articles/<slug>/read.md` 看 Markdown 原文，图片用相对路径，会正常显示。

网站由 GitHub Pages 自动构建：push 到 `main` 后，`.github/workflows/pages.yml` 跑校验、生成 `_site/` 并发布。**网页是从 `read.md` 派生出来的，不是另一份要手工维护的正文。**

全部篇目（标题、日期、图片数、正文 sha256）在 [catalog.json](catalog.json) 里。

## 一篇长什么样

```
articles/2026-11-02-lz77-sliding-window/
  read.md                正文。唯一的正文，网页和公众号都从它生成
  sources.md             来源、引文位置、图片出处与许可、写明的缺口
  review.md              审读记录：审的哪个版本、查了哪几条线、哪些没做（2026-11 起随文提交）
  assets/                正文实际引用的图（相对路径）
  originals/             未改动的原始下载文件（有第三方素材时才有）
  cover.png              这篇文章自己的封面
  examples/              可运行的模型：程序、results.json、绘图脚本、元数据
  README.md              这篇怎么跑、踩了什么坑
  LICENSE-CODE.txt       示例代码许可（带示例程序的文章才有，多为 MIT）
```

每篇都遵守三条：

- **数字是跑出来的。** 正文里的数值由 `examples/` 下的程序实际算出并存进 `results.json`；图里的曲线从同一个文件读，不手画。改代码能让数字变，数字不能为了好看改。
- **真实和示意分开标。** 照片写明谁拍的、什么许可；示意图标为原创示意；两者不混，也不拿生成图冒充现场、人物或设备。
- **来源写到读到的程度。** 读了全文、只读到摘要、还是根本没有原始档案，`sources.md` 里逐条写；核不了的就写"没核"，不写成"已核实"。

## 许可

除非另有说明，本仓库由 zyuanming 发布的原创文章正文采用 [Creative Commons Attribution 4.0 International（CC BY 4.0）](https://creativecommons.org/licenses/by/4.0/) 许可。转载、改编和商业使用均应按许可要求署名、链接原文及许可，并注明修改。完整条款见 [CC BY 4.0 法律文本](https://creativecommons.org/licenses/by/4.0/legalcode.zh-hans)。

第三方图片、原文引用、商标及其他第三方素材不适用上述统一授权；其权利仍归各自权利人，复用时须遵循每篇文章和素材来源中列明的许可、署名及其他要求。未标注开放许可的素材，不因收录在本仓库而获得再授权。带示例程序的文章在自己的目录里附 `LICENSE-CODE.txt`，代码许可以那份为准。

## 在本地构建

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-site.txt

python3 tools/index_articles.py      # 刷新 catalog.json；改了 read.md 之后必须跑
python3 tools/validate_content.py    # 离线校验：id 唯一、hash 对得上、本地链接不逃逸、拒绝私有产物
python3 tools/build_site.py          # 生成 _site/，输出目录必须为空
```

`validate_content.py` 会拿 `catalog.json` 里冻结的 sha256 和实际正文比对——只改正文不重跑 `index_articles.py`，它会直接报 `Article hash mismatch`。这是有意的：网页、索引和正文必须是同一个版本。

## 关于这个仓库

公众号是主要发布渠道，这里是同源的公开存档。本仓库**只放定稿**，不放草稿、内部研究资料、审读过程日志、公众号凭据或后台状态；也不包含写作工程的私有 Git 历史。

- 写作与配图规则：[AGENTS.md](AGENTS.md)
- 2026 年 10 月各批次的目录页（历史归档，逐篇链接）：[docs/](docs/)

发现错别字、事实错误、图片署名或许可问题，开一个 issue 就行，别客气——正文里的每个数字都有对应程序，改起来不难。
