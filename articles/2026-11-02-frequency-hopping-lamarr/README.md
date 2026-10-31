# 可复算说明

正文里每个数字都来自这里：21.4% 的跳被打断、176 倍的功率、19.44 dB 的处理增益、
失步一跳之后 1.27% 的对齐率。

## 跑一遍

```sh
python3 examples/run_model.py       # 全部测量 -> examples/results.json
python3 examples/build_figures.py   # 14 张示意图 + cover.png
python3 examples/photos.py          # 5 张真实素材（需要 originals/）
```

只要 Python 3.10+；画图需要 Pillow。**测量部分只用标准库。**

## 文件

| 文件 | 作用 |
| --- | --- |
| `examples/fh.py` | 跳频序列、四类干扰机、功率账、同步与反应时间实验 |
| `examples/run_model.py` | 跑全部测量，写 `results.json` |
| `examples/figkit.py` | 画图工具（MIT），自带字号与越界自检 |
| `examples/build_figures.py` | 14 张示意图与封面 |
| `examples/photos.py` | 5 张真实素材的版式（肖像、专利扫描、钢琴卷） |
| `examples/results.json` | 全部测量结果 |

## 五件要说清楚的事

1. **这是模型，不是实测。** 10 dB 的 J/S 门槛、30 倍的干扰功率、1 ms 的跳长
   都是假设值。它们的作用是把机制算清楚，不代表任何真实系统。
2. **"一跳"是一个整包。** 没有误码率模型，没有编码与重传：被干扰者盖住的跳
   直接算丢。真实链路会好一些（有交织会差一些），但不影响这里的结论。
3. **88 个频点来自专利原文**（"88 rows of perforations … 88 different carrier
   frequencies"），不是工程规格；频点间隔、带宽都没有建模。
4. **跳频序列是确定性的**：16 位移位寄存器 + 折叠 + 拒绝采样。χ² 用来验证
   它足够均匀，不追求密码学强度。
5. **历史数字单独标注**：专利申请/授权日期来自专利首页扫描件；蓝牙 1600 跳/秒、
   GSM 217 跳/秒、SINCGARS 约 100 跳/秒 属于公开规格，与本文模型无关。

## 许可

代码 MIT，见 `../LICENSE-CODE.txt`。正文与原创图 CC BY 4.0。
真实素材的许可与出处见 `sources.md`。
