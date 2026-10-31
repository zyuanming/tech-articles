# 来源与素材

## 一手材料

- **US 2,292,387 B1**, *Secret Communication System*, Hedy Kiesler Markey and
  George Antheil. 申请日 1941-06-10（Serial No. 397,412），授权日 1942-08-11，
  6 项权利要求，分类号 250-2。
  本文引用的三处原文（用途、88 行孔与 88 个载波频率、两种同步手段）都来自
  这份文件，扫描件见 `originals/patent-front.jpg` 与 `originals/patent-sheet1.jpg`，
  正文图片见 `assets/05-patent-front.jpg`、`assets/06-patent-sheet1.jpg`。
- 专利附图第 1 张（发射端与接收端框图）与首页同属美国专利商标局的公开档案，
  在美国属公有领域。

## 参考（二手）

- 关于 Lamarr 生平（1914 维也纳出生、1933《神魂颠倒》、1937 赴美、1997 EFF
  先锋奖、2000 年去世）采用公开传记与 EFF 公告的常见表述，未逐条核对档案。
- 关于 Antheil（1900 生、*Ballet Mécanique*、自动钢琴同步装置、《Bad Boy of
  Music》）采用常见音乐史叙述。
- 蓝牙经典（79 个频点、1600 跳/秒）、GSM 慢跳频（217 跳/秒）、SINCGARS
  （约 100 跳/秒）、802.11-1997 的 FHSS 物理层，取自各自规范或公开技术资料。
- 1950–60 年代扩频技术的多条独立路线（军用抗干扰电台、卫星测距、线性调频、
  RAKE 接收机）为通史性表述。

## 事实核对说明

- 专利授权日、申请日、权利要求数、发明人地址均以首页扫描件的 OCR 文本为准。
- 本文明确写出：专利有效期内（1942–1959）该系统没有实战使用；Lamarr 未从中
  获得报酬；"Wi-Fi 用了她的专利"是错误说法。这三条与流行的通稿相反，按档案写。
- "从军火商丈夫的晚宴上听来机密"标注为传闻，没有档案支持。
- 时间线里的年份按公开资料表述；1959 年既是专利到期年，也是 Antheil 去世年。

## 图片

14 张示意图与封面由 `examples/build_figures.py` 生成，属原创教学示意；
所有曲线与百分比都从 `examples/results.json` 读取。

5 张真实素材：

| 文件 | 内容 | 许可 | 原页 |
| --- | --- | --- | --- |
| `assets/02-hedy.jpg` | Hedy Lamarr，1940 | 公有领域 | [Commons](https://commons.wikimedia.org/wiki/File:Hedy_lamarr_-_1940.jpg) |
| `assets/03-antheil.jpg` | George Antheil | 公有领域 | [Commons](https://commons.wikimedia.org/wiki/File:George_Antheil.jpg) |
| `assets/04-piano-roll.jpg` | 自动钢琴纸卷 | CC BY 2.0（Shannon Prickett） | [Commons](https://commons.wikimedia.org/wiki/File:Player_Piano_%26_piano_rolls_(photo_by_Shannon_Prickett).jpg) |
| `assets/05-patent-front.jpg` | 专利首页 | 公有领域（USPTO） | [Commons](https://commons.wikimedia.org/wiki/File:Patent_Case_File_No._2,292,387,_Secret_Communication_System,_Inventors_Hedy_Kiesler_Markey_and_George_Antheil_-_DPLA_-_128f022cfd9421aa10de72958a7edf90_(page_8).jpg) |
| `assets/06-patent-sheet1.jpg` | 专利附图第 1 张 | 公有领域（USPTO） | 同上档案，page 6（2343×3410） |

处理方式：等比缩放、加姓名/出处条；原始尺寸分别为 1104×1455、711×1024、
2160×1440、2343×3410、2343×3410。原件在 `originals/`。

专利扫描件属于"档案扫描"，不是"真实照片"——`figure-metadata.json` 里的
`identity` 字段如实区分这两类。

## 缺口

- 没有 Lamarr 与 Antheil 的合影。
- 没有 1940 年代美国海军鱼雷或跳频电台的实物照片（专利档案里的附图已收）。
- 没有 802.11-1997 FHSS 设备的照片。
- 没有两人在 1940 年代会面的地点照片。

## AI 辅助说明

正文由作者撰写；跳频模型、测量与绘图代码由作者编写并实际运行。没有使用
生成式图像模型。5 张真实素材的身份、许可与出处如上。
