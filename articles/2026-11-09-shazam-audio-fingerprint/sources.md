# 来源

## 历史与产品事实

- **Avery Wang, "An Industrial-Strength Audio Search Algorithm", ISMIR 2003.**
  会议论文集条目（该文是本文算法流程的原始公开描述：谱峰、组合哈希、偏移直方图）。
  <https://ismir2003.ismir.net/papers/Wang.pdf>
  说明：我没有逐段核对原文措辞，本文的算法描述是按这套经典流程重写的实现；文中没有引用原文的图表或数字。

- **美国专利 US 6,990,453 B2，"System and methods for recognizing sound and music signals in high noise and distortion"，2006-01-24 授权。**
  <https://patents.google.com/patent/US6990453B2/en>
  用于确认申请与授权时间、发明人、以及"谱峰 + 组合哈希 + 时间偏移投票"三个步骤在权利要求里的表述。

- **Shazam 的 2580 短号与 2002 年英国上线。**
  这是被大量报道的产品史事实，我引用的是公开报道的共识版本，没有找到当年的一手公告。
  <https://www.theguardian.com/technology/2018/sep/24/apple-shazam-music-recognition-app>

- **Apple 收购 Shazam（2018）。**
  收购金额"约 4 亿美元"来自媒体报道，不是 Apple 官方公告的数字；正文已标注"公开报道"。
  <https://www.apple.com/newsroom/2018/09/apple-completes-acquisition-of-shazam/>

- **Chromaprint / AcoustID。**
  开源的另一条指纹路线，用于说明"同一问题有不同算法"。
  <https://acoustid.org/chromaprint>

## 建模依据

- 谱图与谱峰的经典处理：Oppenheim & Schafer, *Discrete-Time Signal Processing*，短时傅里叶变换与窗函数章节。
- 组合哈希与偏移投票的结构：同上面的 ISMIR 2003 论文与专利。
- 对数频率轴对速度变化的容忍：SoundHound / dejavu 等开源实现的常见做法（例如 <https://github.com/worldveil/dejavu>）。

## 图片

全部 18 张图都是原创教学示意，由 `examples/build_figures.py` 生成，数据来自
`examples/run_model.py` 输出的 `results.json`（谱图面板是模型算出的真实谱图，不是手绘）。

- 没有使用任何第三方图片，因此没有外部许可需要保留。
- 时间线（图 15）里的年份来自上面列出的公开记录。
- **肖像缺口**：Avery Wang 的照片没有找到可自由使用的授权版本，正文因此没有配人物肖像；
  这一项在 `review.md` 里记为已知缺口，不用其他图片代替。
