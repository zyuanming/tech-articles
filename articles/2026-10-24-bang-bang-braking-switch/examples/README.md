# 复算

Python 3 + Pillow + fontTools + Noto Sans CJK。运行 `python lab.py`。

主模型x'=v,v'=u，|u|≤1m/s²，起点x=0m,v=0m/s，目标x=4m,v=0m/s。分段解析公式，采样间隔0.01s；程序断言4秒恰好到达及延迟切换的4.41米停车位置。图9添加限速1m/s，图10平滑曲线仅为示意，图12初态另设为(3,3)，不混用范围。

data.json为可复算数据；figure-metadata.json为几何/字体检查结果与用途。有限数值检查不是对真实设备的认证。代码、教学数据、图采用CC BY 4.0。
