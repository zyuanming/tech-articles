# 来源与素材

## 参考

- John M. Chowning, *The Synthesis of Complex Audio Spectra by Means of Frequency
  Modulation*, Journal of the Audio Engineering Society 21(7), 1973。
  本文所有公式的原始出处：边带位置 fc ± n·fm、振幅 J_n(I)、以及"比率决定谐波性"。
- US Patent 4,018,121, *Method of Synthesizing a Musical Sound*, John M. Chowning,
  1975 年 5 月 2 日申请，1977 年 4 月 19 日授权，权利人斯坦福大学董事会。
- John M. Chowning, *FM Synthesis of Complex Audio Spectra*（Stanford CCRMA 讲义）。
  包络与算子连接方式的工程描述。
- Yamaha, *DX7 Operating Manual*（1983）。32 种算法、6 个算子、四段包络的
  参数结构以此为准。
- F. W. Olver 等, *NIST Handbook of Mathematical Functions*, 第 10 章（贝塞尔函数）。
  用于核对 J_n 的数值。
- Julius O. Smith III, *Mathematics of the Discrete Fourier Transform*。
  FFT 与窗函数的背景。
- 关于调频带宽的 Carson 规则：J. R. Carson, *Notes on the Theory of Modulation*,
  Proceedings of the IRE, 1922。

## 事实核对说明

- Chowning 发现这一现象的年份按公开记载写 1967 年；"颤音开得太大"是广泛
  流传的叙述版本，本文按此表述，没有核对原始实验记录。
- 专利日期取文件首页：申请 1975-05-02（延续 1974-03-26 的申请），授权 1977-04-19。
- 斯坦福对 Yamaha 的授权普遍记为 1973 年；DX7 销量普遍记为"二十万台上下"，
  两者都是量级表述。
- "DX7 实际是调相"是工程界的共识（Yamaha 的实现方式），专利标题仍叫
  frequency modulation；本文第 3 节写明了这个差别。
- 时间线里的年份按公开的产品与文献年份表述，不精确到月份。

## 图片

16 张示意图与封面由 `examples/build_figures.py` 生成，属原创教学示意。
频谱、包络、边带计数全部从 `examples/results.json` 读取，没有手写数值。

三份真实素材：

| 文件 | 内容 | 作者 | 许可 | 原页 |
| --- | --- | --- | --- | --- |
| `assets/02-dx7.jpg` | Yamaha DX7（Museum of Making Music 藏品） | doryfour | CC BY-SA 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Yamaha_DX7_synthesizer,_Museum_of_Making_Music.jpg) |
| `assets/03-chowning.jpg` | John Chowning 肖像 | Commons 上传者 | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:Chowning.jpg) |
| `assets/04-patent-sheet.png` | US 4,018,121 附图 1（第 2 页，150 dpi 渲染） | 美国专利商标局 | 公有领域 | [Commons](https://commons.wikimedia.org/wiki/File:US4018121A_Method_of_synthesizing_a_musical_sound,_by_John_M._Chowning_(filed_in_1975-05-02,_published_in_1977-04-19).pdf) |

处理方式：等比缩放（DX7 到 620 高、肖像到 560 高、专利附图到 980 高）、
加署名条；肖像原图 452×608 被放大约 1.2 倍，已在图内注明。原件在 `originals/`。

## 缺口

- 没有 GS-1（1980 年第一台商用 FM 合成器）的实物照片。
- 没有 Chowning 在 CCRMA 工作的现场照片，也没有 1970 年代 PDP-10 的照片。
- 没有音频文件。文中所有"听起来像"都是文字描述，不是可听的证据。
- 专利共 17 张附图，本文只用了第 1 张。

## AI 辅助说明

正文由作者撰写，测量与绘图代码由作者编写并实际运行。没有使用生成式图像模型；
DX7 照片、Chowning 肖像、专利附图都是真实文件，许可与出处如上。
