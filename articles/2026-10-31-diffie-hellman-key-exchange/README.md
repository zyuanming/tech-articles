# 可复算说明

正文里每个数字都来自本目录的代码：幂表、交换结果、中间人的两把钥匙、攻击步数、
RFC 3526 素数的位数，以及那条小椭圆曲线的群阶。

## 跑一遍

```sh
python3 examples/run_model.py       # 全部实验 -> examples/results.json
python3 examples/build_figures.py   # 20 张正文图 + cover.png
python3 examples/photos.py          # 两位作者的肖像合成（需要 originals/）
```

要求：Python 3.10+，绘图需要 Pillow。除 Pillow 外只用标准库。

单独重画某张图：`python3 examples/build_figures.py 07`（只重画第 7 张）。

## 文件

| 文件 | 作用 |
| --- | --- |
| `examples/dh.py` | 模幂、穷举、大步小步法、RFC 3526 素数、中间人、椭圆曲线点加法 |
| `examples/run_model.py` | 跑全部实验，写 `results.json` |
| `examples/figkit.py` | 画图工具（MIT），自带字号与越界自检 |
| `examples/build_figures.py` | 20 张示意图 |
| `examples/photos.py` | 肖像合成与署名 |
| `examples/results.json` | 幂表、交换值、攻击实测、估算、曲线数据 |
| `originals/` | 两张 Wikimedia 原图，未经修改 |

## 三件要说清楚的事

1. 16–28 位的攻击是**真跑**的，耗时可复现；2048 位那一行是**算**的。
   我的机器上跑不了 2048 位的攻击，正因为跑不了。
2. 大步小步法不是最强的攻击。数域筛法（index calculus / NFS）对素域更有效，
   本文没有实现它——那样 2048 位就会变成「一年」而不是「10^1024 年」。
   文中「10^1024」这个数字指的是「开平方」这条朴素路线，不是人类最好的攻击。
3. 椭圆曲线那一节只演示点加法的规则与群阶，没有做任何真实密码学运算。
   y² = x³ + 7 mod 17 是教学用的玩具曲线，绝不安全。

## 可复现性

没有随机性需要固定：`small_prime` 与两个秘密指数的随机源都是显式的
`random.Random(seed)`，种子写在 `dh.py` 与 `run_model.py` 里。同一份代码在任何机器上
得到同一份 `results.json`（实测耗时字段除外，那个本来就会变）。

## 许可

代码 MIT，见 `../LICENSE-CODE.txt`。正文与图 CC BY 4.0。照片许可见 `sources.md`。
