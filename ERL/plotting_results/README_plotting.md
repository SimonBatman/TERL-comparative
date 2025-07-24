# ERL实验结果可视化工具

本工具用于可视化ERL（Evolutionary Reinforcement Learning）实验的训练结果，专注于生成论文格式的均值±标准差图表。

## 主要功能

- **论文格式输出**：专注于生成均值±标准差的图表，符合学术论文要求
- **自动数据读取**：自动扫描指定目录下的实验结果文件
- **统一命名规则**：图表直接以环境名命名，简洁明了
- **高质量PNG输出**：生成高分辨率PNG图表，减少文件占用
- **批量处理**：支持同时处理多个实验环境
- **智能清理**：可选择清理旧的结果文件和临时文件

## 使用方法

### 基本用法

```bash
# 绘制单个环境的结果
python plot_erl_final.py --env Reacher-v2

# 绘制所有环境的结果
python plot_erl_final.py --env all

# 清理旧文件并重新生成
python plot_erl_final.py --env all --clean
```

### 高级用法

```bash
# 论文格式：显示标准差误差线（推荐用于学术发表）
python plot_results_enhanced.py --base_dir runs/Reacher-v2 --confidence_interval --error_type std

# 统计格式：显示95%置信区间
python plot_results_enhanced.py --base_dir runs/Reacher-v2 --confidence_interval --error_type ci

# 调整平滑参数
python plot_results_enhanced.py --base_dir runs/Ant-v2 --smooth_sigma 15

# 组合使用标准差误差线和平滑
python plot_results_enhanced.py --base_dir runs/Ant-v2 --confidence_interval --error_type std --smooth_sigma 20

# 自定义输出文件名
python plot_results_enhanced.py --base_dir runs/Reacher-v2 --output_prefix my_reacher_results

# 使用不同的 TensorBoard 标签
python plot_results_enhanced.py --base_dir runs/Reacher-v2 --tag charts/episodic_return
```

### 编程接口

```python
from plot_results_enhanced import plot_experiment_results

# 基本绘图
fig, ax = plot_experiment_results(
    base_dir="runs/Reacher-v2",
    show_confidence_band=False
)

# 带置信区间的绘图
fig, ax = plot_experiment_results(
    base_dir="runs/Ant-v2",
    show_confidence_band=True,
    smooth_sigma=15,
    figsize=(12, 8)
)
```

## 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--env` | str | 必需 | 环境名称或 `all` (处理所有环境) |
| `--clean` | flag | False | 是否清理旧的结果文件 |
| `--smooth_factor` | float | 0.6 | 高斯平滑因子 (0-1) |
| `--figsize` | str | `10,6` | 图表尺寸 (宽,高) |

## 输出文件

脚本会在当前目录中生成以下文件：

- `{环境名}.png` - 高分辨率PNG图表（均值±标准差格式）

## 使用示例

### 处理单个环境
```bash
# 生成 Reacher-v2 环境的图表
python plot_erl_final.py --env Reacher-v2
```

### 批量处理所有环境
```bash
# 处理所有可用环境
python plot_erl_final.py --env all
```

### 清理并重新生成
```bash
# 清理旧文件并重新生成所有图表
python plot_erl_final.py --env all --clean
```

## 数据要求

### 目录结构
```
runs/
├── Reacher-v2/
│   ├── Reacher-v2__0__1752480611/
│   │   └── events.out.tfevents.xxx
│   ├── Reacher-v2__1__1752480613/
│   │   └── events.out.tfevents.xxx
│   └── Reacher-v2__7__1752480616/
│       └── events.out.tfevents.xxx
└── Ant-v2/
    ├── Ant-v2__0__1752299150/
    │   └── events.out.tfevents.xxx
    └── ...
```

### TensorBoard 标签
默认读取 `charts/best_fitness` 标签，可通过 `--tag` 参数修改。

## 演示脚本

运行 `demo_enhanced_plotting.py` 查看各种功能的演示：

```bash
python demo_enhanced_plotting.py
```

演示包括：
1. 基本用法
2. 带置信区间的绘图
3. 自动发现功能
4. 批量处理多个环境
5. 自定义参数使用

## 主要改进

相比原始的 `plot_reacher_results.py`，增强版具有以下优势：

1. **✓ 自动发现**: 无需手动指定每个实验目录
2. **✓ 通用性**: 支持任意环境，不限于 Reacher-v2
3. **✓ 自适应**: 自动调整坐标轴范围，适应不同数据分布
4. **✓ 灵活性**: 丰富的参数选项和编程接口
5. **✓ 鲁棒性**: 更好的错误处理和异常情况处理
6. **✓ 可维护性**: 模块化设计，易于扩展和修改

## 依赖要求

```bash
pip install numpy matplotlib pandas scipy tensorboard
```

## 故障排除

### 常见问题

1. **找不到数据**: 确保目录路径正确，且包含 TensorBoard 事件文件
2. **CUDA 警告**: 可以忽略，不影响功能
3. **内存不足**: 对于大量数据，可以减少 `smooth_sigma` 参数

### 调试技巧

```python
# 检查发现的实验目录
from plot_results_enhanced import auto_discover_experiment_dirs
experiment_dirs = auto_discover_experiment_dirs("runs/Reacher-v2")
print(experiment_dirs)
```