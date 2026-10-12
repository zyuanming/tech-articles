# 可复现的球体追踪小实验

## 二维检查

只需Python 3.12或相近支持版本的标准库。本文实际运行3.12.14。

```bash
python sphere_lab.py results.json
```

脚本执行10000个盒点测试、20000条射线对照及定点边界，打印JSON并可写入给定文件。随机种子20261012，输入顺序固定。只验证解析圆与轴对齐盒；不是任意隐式函数的通用鲁棒求交器。

march要求传入精确有符号距离函数、单位方向、外部起点。factor只缩小步长，不缩小终止判断。NEAR_SURFACE代表到表面不超过epsilon，不代表射线必定有精确交点。RANGE_CLEAR只排除[0,t_max]；BUDGET未完成判定；START_INSIDE拒绝内部起点；OVERSHOOT、STALLED、INVALID_DISTANCE暴露异常而不是伪装命中。

可以在Python里导入march、circle_sdf、box_sdf，修改epsilon、factor、budget和origin。故意测试factor>1时实现会拒绝；高估反例在脚本中另行直接计算，避免把不安全选项混进正常接口。

## 三维图像

本文实际使用Python 3.12.14、NumPy 2.3.5和Pillow。安装所需依赖后：

```bash
python render_scene.py output-images
```

生成两个960×720 PNG与控制台计数JSON。全部几何、相机、材质由代码定义，不下载场景资产。主射线每像素1样本，最多256次查询；颜色是简单直接光和环境项。没有间接光、抗锯齿或GPU实现。

阴影另设128次预算；实际39个未决阴影被当作未遮挡，这是明确的演示近似，可能导致漏阴影。本文不把运行时间当成基准，也未亲测任何手机或真实游戏。

## 许可

这两个文件为本稿独立编写的教学代码，© zyuanming，CC BY 4.0：https://creativecommons.org/licenses/by/4.0/ 。使用或改编请署名、链接许可并说明修改。不提供生产环境鲁棒性担保。
