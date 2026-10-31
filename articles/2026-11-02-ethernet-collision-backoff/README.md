# 可复算说明

正文里每个数字都从这里来：ALOHA 与分槽 ALOHA 的吞吐、退避要撞几次、
两个杠杆算出的有效吞吐、速率与合法网段长度的关系。

## 跑一遍

```sh
python3 examples/run_model.py       # 全部测量 -> examples/results.json
python3 examples/build_figures.py   # 19 张示意图 + cover.png
python3 examples/photos.py          # 3 张照片的版式（需要 originals/）
```

要求：Python 3.10+，绘图需要 Pillow。除 Pillow 外只用标准库。

单独重画某张图：`python3 examples/build_figures.py 14`。

## 文件

| 文件 | 作用 |
| --- | --- |
| `examples/net.py` | 模拟器：ALOHA、分槽 ALOHA、退避、时隙算术 |
| `examples/run_model.py` | 跑全部测量，写 `results.json` |
| `examples/figkit.py` | 画图工具（MIT），自带字号与越界自检 |
| `examples/build_figures.py` | 19 张示意图与封面 |
| `examples/photos.py` | 照片合成与署名 |
| `examples/results.json` | 全部测量结果 |
| `originals/` | 四张 Wikimedia 原图，未经修改 |

## 三个模型，各自的假设

1. **ALOHA / 分槽 ALOHA**：泊松到达，帧长固定为 1 个时间单位，碰撞即全帧作废、
   不重传。所以算出来的是"成功传出去的帧 ÷ 时间"，和课本的 `G·e^(-2G)`、
   `G·e^(-G)` 可以直接对。
2. **退避实验**（`contention`）：n 台机器都有帧要发，每轮各自从窗口里抽一个格数，
   抽到唯一的最小值者赢。这是"抽签"这一层的抽象，不含帧的传输时间，
   也不含"边听边说"。窗口策略是唯一变量：`binary` = 2^k，`fixed2` = 2，
   `fixedn` = n。
3. **有效吞吐**（`efficiency`）：`1 / (1 + 冲突次数 × 每次冲突的代价)`。
   冲突次数取自上面的实测，代价是假设值（ALOHA 1.0，CSMA/CD 0.05）。
   这是算术，不是模拟——正文里明确写了"80% 是模型算术"。

## 四件要说清楚的事

1. ALOHA 的峰值是 1/(2e) = 18.39%，分槽是 1/e = 36.79%。实测点会在这两个数附近
   上下浮动 1–2 个百分点，因为模拟用的是有限长时间、有限个槽。
2. 退避实验里"撞几次"的口径是**冲突轮数**，不是"浪费了多少微秒"。它回答的是
   "要几轮才有人赢"，换算成时间还要乘上窗口大小和时隙。
3. `fixed2` 那一组在 16 台以上会撞满上限（我给了 12），所以曲线在 12 处是一条横线。
   这不是"收敛到 12"，是"到上限还没收敛"。想验证的话把 `cap` 调到 30 再跑。
4. 速率与距离表里算的是**半双工 CSMA/CD 的算术上限**：`时隙 × 2e8 / 2`。
   真实标准的选择不同（百兆全双工、千兆载波扩展），正文第 12 节解释了这件事。

## 许可

代码 MIT，见 `../LICENSE-CODE.txt`。正文与图 CC BY 4.0。照片许可见 `sources.md`。
