# 审读记录

sha256 `cd334c5020338a5eaae911ee424c7b280ddf41b6d93e27317849f12f0b4cf31c` · 87 行 · 4043 字符 · 插图 7 张

## 查证线

这一轮把官方仓库的源码抓下来对照了一遍（`id-Software/DOOM`，`linuxdoom-1.10`，两条链接都返回 200）：

- `r_bsp.c` 里 `R_RenderBSPNode` 在 552 行开始，递归前先 `side = R_PointOnSide(viewx, viewy, bsp)`，然后 `R_RenderBSPNode(bsp->children[side])`，再用 `if (R_CheckBBox(bsp->bbox[side^1]))` 守住另一侧。正文说的「先访问玩家所在一侧；再检查另一侧的包围盒」就是这个顺序，正文给的 `#L520-L580` 范围覆盖了整段函数。
- 叶子分支确实是 `bspnum & NF_SUBSECTOR` 时转 `R_Subsector`，与「叶子对应 subsector」的说法一致。
- 那个左右判断在 `r_main.c` 的 `R_PointOnSide` 里，先按 `node->dx` / `node->dy` 为零退化情形处理，再算 `dx = x - node->x`、`dy = y - node->y`，用符号位比较定侧——正文写的 `(Bx−Ax)×(Py−Ay)−(By−Ay)×(Px−Ax)` 就是同一件事的一般写法，符号约定方向换了会一起翻，正文也点明了这一点。
- `sources.md` 里 `README.TXT`、`doomdata.h`、Bethesda 的 22 周年页、Carmack 的 CC BY 2.0 肖像，都是原站链接；1993 年 DOS 版本没有本地运行，正文已声明只读源码。

## 这一轮改了什么

原稿 47 段 / 114 句 / 2304 字，4 项 WARN：段均句数 2.43、平均段长 49.0、≤2 句段 57.4%、加粗 1.3‰。终稿 29 段 / 111 句 / 2304 字，0 项 WARN：平均句长 21.2、标准差 11.8、最长句 52、段均句数 3.83、平均段长 79.4、≤2 句段 14%、加粗 0、数字密集段 0%。

- 十八处碎段并回上下文：开头「世界里有什么 / 值不值得画」两句并一段；sector 的地板与天花板高度、边界、台阶、门与升降台并一段；subsector 与 sector 的区别紧跟定义一段。
- 加粗全删，原来加亮的是 `BSP`、`subsector`、`seg`、`linedef` 这几个术语；删掉星号后它们仍在句子里当名词用，不影响识别。
- 叉积那行独立公式并进了前后文，读起来是「若分割线从 A 指向 B，玩家在 P，计算：…。结果的正负区分两侧」，不再是一行公式孤悬。
- 伪代码块、源码链接、七张图、所有数字（40 到 120 列、60 到 100 列）一字未动；`refresh_article.py check` 报 `INVARIANTS_OK`。

## 没做的

- 没有重画 7 张图，也没有查手机端字号；图注里的颜色与轴含义没有逐张补，记 `VISUAL_REVIEW_NOT_RUN`。
- 没有在本地编译 Linux Doom 或跑一遍渲染，源码对照停在「读函数、对顺序」，没有实测帧率或省下的遍历次数。
- 没有展开 `R_CheckBBox` 内部怎么用 `viewangletox` 与 `xtoviewangle` 做屏幕列裁剪，正文只说到「包围盒投影落在已封闭范围」这一层。
- 没有讨论 BSP 之外的 PVS、portal 渲染等后来方案，第 11 节把范围收在「场景大体静止」这一条前提里。
- 这份审读由写正文的同一个 AI 在同一轮里完成，不是陌生审稿人。
