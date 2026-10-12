# BVH 学习实验

要求 Python 3.10+，只使用标准库。验证环境 Python 版本写入 results.json。坐标单位为无量纲模型单位，双精度浮点，随机种子20261012。原始实现代码按 [MIT](LICENSE) 许可。

## 运行

进入本目录，运行：

```sh
python bvh_lab.py --output results.json
python bvh_lab.py --output results.json --render scene.ppm
```

第二条命令先跑全部测试，再生成480×400的PPM图像；192000条相机射线，不做反弹和随机采样。图像用普通PPM查看器打开即可。没有外部库、网络请求、安装动作或GPU需求。

results.json 包含完整输入、主查询访问顺序、边界检查、随机核对、规模与移动实验；scene.json 包含渲染测试计数。输出文件在你指定的位置生成，不需要写入源码目录。

## 可核对结果

- 主场景12个三角形；主射线 O=(0,8,0)、D=(1,0,0)；最近命中 G，t≈3.3
- 暴力：12次三角形求交
- y-first 主树不缩短范围：9次盒求交、3次三角形求交
- y-first 主树近处优先并缩短：7次盒求交、1次三角形求交
- 完全重叠盒落空坏例：23次盒求交、12次三角形求交
- 113条固定射线：初始树591盒/68三角形；refit1939盒/83三角形；重建591盒/68三角形
- 20000条随机射线×3遍历模式，60000次比较零差异
- 10000次独立三角形算法核对零差异
- 规模场景12/192/3072：BVH分别2304/4352/6400次盒测试，每场景均256次三角形测试

## 如何改实验

main_scene(nx, ny) 生成规则网格；build(..., mode='y_first') 对应正文手算树；build() 默认最长中心跨度轴中位数分组。leaf_size 控制每叶容量上限，默认1。

traverse(..., shrink=False) 保留无穷远查询范围；near_first=False 使用固定子节点顺序；any_hit=True 找到任意有效命中即返回。注意任意命中与最近命中回答不同问题。

要探索新射线，可在 Python 中：

```python
from bvh_lab import main_scene, build, traverse
scene = main_scene()
root = build(scene, mode='y_first')
hit, counts = traverse(scene, root, (0, 10, 0), (1, 0, 0))
print(hit, counts.boxes, counts.triangles)
```

## 数据与数值边界

所有输入坐标、方向应是有限数；方向不可全零。代码用于正文小尺度示例。三角形测试为双面的行列式算法，近平行阈值为1e-12；退化和共面情形不作为普通点命中报告。它不是watertight求交内核，不承诺任意尺度浮点鲁棒性。

闭包围盒允许单点接触。t_min固定为0，t_max可限制有效射线段。只有单位方向时，t才等于沿射线行进的模型距离。

计数包含为了子树排序预先做的盒测试；栈里缓存的入口随后与最近距离比较，不算另一次盒求交。普通BVH与暴力共用主三角形函数，因此额外提供plane_oracle进行独立算法核对；随机核对仍不是正确性证明。

正文SAH数字和构建成本例子是手算模型，源码没有实现SAH、Morton/GPU构建器，也没有报告硬件计时。
