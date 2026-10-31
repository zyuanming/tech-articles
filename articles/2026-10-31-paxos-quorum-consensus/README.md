# 可复算说明

本文所有数字和消息图来自本目录的代码。没有手工录入的数值，没有从教科书抄的曲线。

## 跑一遍

```sh
python3 examples/run_model.py       # 4 个场景 -> examples/results.json
python3 examples/build_figures.py   # 24 张正文图 + cover.png
python3 examples/photos.py          # 2 张照片版式（需要 originals/）
```

要求：Python 3.10+，绘图需要 Pillow。除 Pillow 外只用标准库。

单独重画某张图：`python3 examples/build_figures.py 12`（只重画第 12 张，
`figure-metadata.json` 里其余记录会保留）。

## 文件

| 文件 | 作用 |
| --- | --- |
| `examples/paxos.py` | 事件队列模拟器：接受者、提议者、带延迟的消息 |
| `examples/run_model.py` | 跑 4 个场景，写 `results.json` |
| `examples/figkit.py` | 画图工具（MIT），自带字号与越界自检 |
| `examples/build_figures.py` | 24 张示意图 |
| `examples/photos.py` | 两张照片的缩放与署名条 |
| `examples/results.json` | 全部消息轨迹、接受者状态、统计数据 |
| `examples/figure-metadata.json` | 每张图的尺寸、最小字号、身份、来源 |
| `originals/` | 两张 Wikimedia 原图，未经修改 |

## 四个场景

1. `happy`：一个提议者，编号 1，五台接受者。跑出一轮完整的 20 条消息。
2. `race`：P1 先成功，P2 用编号 2 稍后进场，第一阶段带回 X 并继承它。
3. `naive`：同一个场景，`honour=False`，P2 忽略第一阶段的值，X 和 Y 都被选定。
4. `contention`：k=1..6 个提议者同时抢，每个 k 跑 60 遍，统计最大编号。

## 确定性

`Sim` 的延迟由 `random.Random(seed)` 生成，队列按 `(时间, 序号)` 排序，同一个 seed 永远得到同一条轨迹。`results.json` 用 seed 1（happy）、5（race / naive）和 0..59（contention）。

## 模型没做的事

- 没有磁盘和 fsync：第 14 节的落盘顺序是协议要求，不是本目录代码的行为；
- 没有丢包与永久分区，只有随机延迟；
- 没有成员变更、快照、日志落盘；
- 第 15 节的活锁图是构造的调度，不是模拟输出，图内已标注。

想让安全性当场坏掉：把 `run_model.py` 里 `naive` 那段删掉 `honour=False`，
或者直接在 `examples/paxos.py` 的 `choose_value` 里注释掉 `self.value = value`。

## 许可

代码 MIT，见 `../LICENSE-CODE.txt`。正文与图 CC BY 4.0。两张照片的许可各不相同，
以正文末尾与 `examples/figure-metadata.json` 为准。
