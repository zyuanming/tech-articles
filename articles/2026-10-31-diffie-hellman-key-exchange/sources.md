# 来源与素材

## 一手文献

- Whitfield Diffie, Martin E. Hellman, *New Directions in Cryptography*,
  IEEE Transactions on Information Theory 22(6), Nov. 1976, pp. 644–654。
  本文的协议结构、安全性假设与「公开渠道建立秘密」的表述以此文为准。
- Ralph C. Merkle, *Secure Communications over Insecure Channels*,
  Communications of the ACM 21(4), Apr. 1978。谜题方案与「Merkle 更早」的说法依据此文，
  以及 Diffie–Hellman 论文对它的引用。
- R. Rivest, A. Shamir, L. Adleman, *A Method for Obtaining Digital Signatures and
  Public-Key Cryptosystems*, Communications of the ACM 21(2), Feb. 1978。
- M. Kivinen, M. Kojo, *More Modular Exponential (MODP) Diffie-Hellman groups for
  Internet Key Exchange (IKE)*, RFC 3526, May 2003。第 7 节的 2048 位素数取自第 3 节，
  构造式与生成器 g = 2 均照抄原文；本文用 Miller–Rabin 复核过它的素性。
- E. Rescorla, *The Transport Layer Security (TLS) Protocol Version 1.3*, RFC 8446,
  Aug. 2018。第 11 节关于 TLS 1.3 只保留 (EC)DHE 的说法依据此文。
- D. Adrian et al., *Imperfect Forward Secrecy: How Diffie-Hellman Fails in Practice*,
  CCS 2015（Logjam）。第 7 节关于共享参数被集中攻击的经验来自此文。

## 事实核对说明

- GCHQ 的时间线（Ellis 1969、Cocks 1973、Williamson 1974、1997 年解密）来自公开的
  解密档案叙述，本文按二手叙述的谨慎程度表述。
- 图灵奖年份 2015、Shor 算法 1994、X25519 的 32 字节公钥属于公开的通行事实。
- 「256 位椭圆曲线约等于 3072 位模素数方案」是 NIST 等机构给出的对照建议，
  不是精确的等价，文中按「大约」表述。
- 第 6 节 16–28 位的攻击是实际运行的结果；2048 位那一行是算术估算，文中已分开标注。

## 图片

20 张示意图与封面由 `examples/build_figures.py` 生成，属原创教学示意。
图内的幂表、交换值、攻击步数、椭圆曲线群阶读自 `examples/results.json`。

一张照片合成：

| 文件 | 内容 | 作者 | 许可 | 原页 |
| --- | --- | --- | --- | --- |
| `assets/21-two-authors.jpg` | Diffie 与 Hellman 肖像（两张合成） | 左：Duncan.Hull；右：未署名（Commons 记录） | CC BY-SA 4.0 / CC BY-SA 3.0 | [Diffie](https://commons.wikimedia.org/wiki/File:Whitfield_Diffie_Royal_Society.jpg) · [Hellman](https://commons.wikimedia.org/wiki/File:Martin-Hellman.jpg) |

处理方式：左图裁掉下方、等比缩放到 420 像素高；右图从 240×280 等比放大到 420 像素高，
放大后细节有限，文中与图内均已注明。两张都未修改画面内容。原图在 `originals/`。

## 缺口

- 没有 Diffie–Hellman 1976 年论文原件的扫描图（版权不明，未使用）。
- Hellman 的可用照片只有 240×280 这一张，无法提供更高清的肖像。
- 没有 GCHQ 相关场所或档案的照片。

## AI 辅助说明

正文由作者撰写，模拟与绘图代码由作者编写并实际运行。没有使用生成式图像模型。
