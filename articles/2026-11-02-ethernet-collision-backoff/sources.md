# 来源与素材

## 参考

- Robert M. Metcalfe, *Alto Ethernet*, Xerox PARC 内部备忘录, 1973 年 5 月。
  以太网最早的书面方案，文中"共享电缆 + 随机重发"的骨架出自这份备忘录。
- Robert M. Metcalfe, David R. Boggs, *Ethernet: Distributed Packet Switching for
  Local Computer Networks*, Communications of the ACM 19(7), 1976。
  正式论文，含 2.94 Mbit/s 实验网络的描述与吞吐分析。
- Norman Abramson, *The ALOHA System — Another Alternative for Computer
  Communications*, AFIPS 1970。ALOHA 协议与 17% 左右的实测利用率。
- Lawrence G. Roberts, *Extensions of Packet Communication Technology to a
  Hand-Held Terminal System*, AFIPS 1972。分槽 ALOHA 的提出。
- Leonard Kleinrock, Fouad A. Tobagi, *Packet Switching in Radio Channels*,
  IEEE Transactions on Communications, 1975。载波侦听与 CSMA 的分析框架。
- IEEE 802.3 标准（1983 年首版及其后续修订）。时隙 512 bit、最小帧 64 字节、
  退避窗口 2^k 且 k ≤ 10、退避上限 16 次、jam 32 bit、帧间隔 96 bit 时间的来源。
- Andrew S. Tanenbaum, David J. Wetherall, *Computer Networks*。ALOHA 与 CSMA/CD
  的效率公式（`1/(1 + 6.4a)`）与经典曲线形状，用于对照本文的模拟结果。
- DEC/Intel/Xerox, *The Ethernet, A Local Area Network: Data Link Layer and
  Physical Layer Specifications*（DIX 规范, 1980）。

## 事实核对说明

- 1973 年备忘录的月份按公开记载表述为"5 月"，没有核对原件上的日期。
- 实验以太网的参数（2.94 Mbit/s、最长 1 公里、最多 256 台机器）取自 1976 年论文，
  与后来的 10 Mbit/s 标准不同，正文中分开表述。
- 时隙 51.2 微秒、最小帧 64 字节、最大帧 1518 字节、载荷上限 1500 字节
  按 IEEE 802.3 的常用表述。
- 时间线里的年份（1973、1976、1980、1983、1990、1995、1999、2006）
  按公开的产品与标准年份表述，不精确到月份。
- 本文没有引用任何真实网络上的实测吞吐。文中所有"实测"指跑 `examples/net.py`
  得到的数，正文"边界"一节已声明。

## 图片

19 张示意图与封面由 `examples/build_figures.py` 生成，属原创教学示意。
其中的曲线与表格数字全部从 `examples/results.json` 读取，没有手写数值。

三张照片（其中一张是双图合成）：

| 文件 | 内容 | 作者 | 许可 | 原页 |
| --- | --- | --- | --- | --- |
| `assets/02-metcalfe-and-memo.jpg` | Robert Metcalfe 肖像 + 1973 年备忘录封面与首页 | 左：美国国家技术奖官方照（未署名）；右：Robert Metcalfe | 公有领域 / 公有领域 | [肖像](https://commons.wikimedia.org/wiki/File:Robert_Metcalfe_National_Medal_of_Technology.jpg) · [备忘录](https://commons.wikimedia.org/wiki/File:Metcalfe_Memo_Establishing_Basic_Principles_of_Ethernet_(Cover_%2B_1st_page).jpg) |
| `assets/03-xerox-alto.jpg` | Xerox Alto I（1973），计算机历史博物馆 | The wub | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Xerox_Alto_I,_1973,_Computer_History_Museum.jpg) |
| `assets/19-ethernet-connector.jpg` | 早期以太网 AUI 接头，上有 Metcalfe 签名 | Daderot | CC0 | [Commons](https://commons.wikimedia.org/wiki/File:Early_Ethernet_connector_-_signed_by_Bob_Metcalfe.jpg) |

处理方式：等比缩放到 620 或 420 像素高、底部加署名条；肖像原图 229×350，
在合成图里被放大到 420 高（约 1.2 倍），已在图内注明。原图在 `originals/`。

## 缺口

- 没有 ALOHA 网络（夏威夷大学）或 Abramson 本人的照片。
- 没有粗同轴电缆"吸血抽头"安装过程的实景照片；正文用早期 AUI 接头实物代替，
  并在图注里写清了它是什么。
- 没有令牌环的实物图，第 14 节只在文字里对比，没有配图。
- 802.3 标准原文是付费文档，本文引用的是公开可查的常用参数，没有逐条对照原件。

## AI 辅助说明

正文由作者撰写，模拟与绘图代码由作者编写并实际运行。没有使用生成式图像模型；
所有照片都是 Wikimedia Commons 上的真实照片，署名与许可如上。
