# 来源、图像与实验

原创中文正文由zyuanming发布，CC BY 4.0。该声明不自动扩展至图片、音频与代码；第三方原作保持自身权利。

## 方法与历史

- Claude E. Shannon, Communication in the Presence of Noise, Proceedings of the IRE 37(1), January 1949, pp.10–21。原文扫描：https://fab.cba.mit.edu/classes/S62.12/docs/Shannon_noise.pdf 。第II节采样定理、带限约束及重建；历史脚注承认先前数学/通信研究，本文不作单一发明者叙事。1949为原发表年份，不把1998再版页头当作原年份。本文采用最高频率严格低于半采样率的安全表述，并单列恰好边界的正弦过零反例。
- Analog Devices FAQ, Why is an input filter necessary when digitizing a baseband signal? https://www.analog.com/en/resources/faqs/FAQ_antialiasing_filter.html 。输入频带外分量折回后无法与真实低频区分、输入端抗混叠滤波。该页文字提及“diagram below”，实际取得的HTML与正文提取中未含可下载的该图；只使用已读事实，不声称原图已收入。
- Analog Devices MT-002, What the Nyquist Criterion Means to Your Sampled Data System Design：https://www.analog.com/media/en/training-seminars/tutorials/mt-002.pdf ，供滤波过渡带和采样率选择进一步阅读，本文不复制其图，不引用其产品实测数字。

## 第三方效果演示（仅链接）

Pixelmaniac pictures, The wagon-wheel effect, 2014。文件页：https://commons.wikimedia.org/wiki/File:The_wagon-wheel_effect.ogv 。作者在许可段明确释放公共领域；当前2014-04-25版本说明移除早版音乐，1920×1080、约82秒。说明称摄像机24帧/秒，本文没有把该视频的条件与自己的8帧模型混同。

只链接可访问的文件说明页和原站播放，不将视频/截图作为本地正文图。本文没有取得可供保真截帧的原视频文件，不用预览缩略图冒充原文件，也不声称自己实测视频中的转速。

本篇以原理与自建观测实验为主，不是Shannon或Nyquist人物传记；没有采用肖像或合成肖像。

## 原创16图映射

01-wheel-frames：单一可识别辐条，顺时针7圈/秒，8帧/秒，四个采样时刻。02-two-turns：315°与−45°同终点，示意瞬时帧，不含曝光积分。03-samples-only：n/8处离散余弦值。04-one-hz：cos(2πt)。05-seven-hz：cos(14πt)。06-same-samples：两曲线及相同黑点。07-angle：45°、315°有相同横投影。08-alias-map：abs((f+4)%8−4)，仅画等效频率位置，不替代一般相位关系。09-nyquist-edge：sin(8πt)在n/8处全零。10-interpolation：真实设定余弦与样本间折线。11-before-filter：自建理想保留1Hz，非滤波器运行测量。12-transition：自建余弦形幅频过渡，非产品响应。13-decimation：每3点留1点的流程图；声音另用6倍降采样。14-audio：7kHz/1kHz，8kHz采样的毫秒图。15-sample-faster：16Hz采样区分1Hz/7Hz。16-bits-vs-time：同一时间点，不同幅值量化。

图片均为原始生成PNG1152像素宽；11图高度992，其余832。源代码从定义直接生成，不二次编辑第三方图。

## 音频与程序（全部为合成教学实验）

examples/experiment.py使用Python3标准库math/struct/wave。实际运行，八样本的浮点最大差3.1086244689504383e-15，断言<1e-12。合成音频均1秒、单声道、16位PCM、峰值8191（约满量程1/4），10毫秒淡入淡出。

- assets/original-7khz-48k.wav：7kHz余弦，48kHz采样。
- assets/aliased-7khz-8k.wav：前文件的PCM每六点取一点，故意不做低通，新采样率8kHz。
- assets/reference-1khz-8k.wav：直接生成1kHz、8kHz参考。

后两份PCM数组逐项完全相同，已用断言检查。无麦克风、ADC、扬声器频响实测，也未宣称以耳朵听过所有播放端效果。

本文使用AI辅助调研与写作；原创教学图按明确设定由代码生成，合成演示与真实来源图已区分。
