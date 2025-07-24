# PDERL 训练结果可视化指南

## 概述

本项目提供了 `visualize_results.py` 脚本来分析和可视化 PDERL 训练过程中生成的 CSV 数据文件。

## 快速开始

### 1. 安装依赖

```bash
pip install matplotlib pandas numpy
```

### 2. 基本使用

#### 交互式模式（推荐）
直接运行脚本，会自动检测 `results` 目录中的实验：

```bash
python visualize_results.py
```

#### 指定结果目录
```bash
python visualize_results.py -dir results/hopper_pderl
```

#### 只查看统计信息（不绘图）
```bash
python visualize_results.py -dir results/hopper_pderl --stats_only
```

#### 比较多个实验
```bash
python visualize_results.py -compare results/exp1 results/exp2 results/exp3
```

#### 不保存图片文件
```bash
python visualize_results.py -dir results/hopper_pderl --no_save
```

## 可视化内容

### 1. 训练曲线图

脚本会生成包含以下四个子图的训练曲线：

- **ERL Score**: 进化强化学习的游戏得分随游戏数变化
- **DDPG Reward**: DDPG 算法的奖励随帧数变化
- **ERL Score vs Frames**: 进化强化学习得分随帧数变化
- **ERL Score vs Time**: 进化强化学习得分随时间变化

每个图表都会显示：
- 最高分数
- 最终分数
- 网格线和趋势曲线

### 2. 选择统计图

显示神经进化过程中的选择统计：
- **Elite**: 精英个体选择比例
- **Selected**: 被选中个体比例
- **Discarded**: 被丢弃个体比例

### 3. 统计摘要

控制台输出包括：
- 最高分数、最终分数、平均分数、标准差
- 总游戏数和总帧数
- 训练参数信息位置

## CSV 文件说明

训练过程中会生成以下 CSV 文件：

| 文件名 | 内容 | 格式 |
|--------|------|------|
| `erl_score.csv` | ERL 得分随游戏数变化 | 游戏数, 得分 |
| `ddpg_score.csv` | DDPG 奖励随帧数变化 | 帧数, 奖励 |
| `frame_erl_score.csv` | ERL 得分随帧数变化 | 帧数, 得分 |
| `time_erl_score.csv` | ERL 得分随时间变化 | 时间(秒), 得分 |
| `elite_selection.csv` | 精英选择统计 | 帧数, 选择比例 |
| `selected_selection.csv` | 个体选择统计 | 帧数, 选择比例 |
| `discarded_selection.csv` | 个体丢弃统计 | 帧数, 丢弃比例 |
| `info.txt` | 训练参数和配置信息 | 文本格式 |

## 使用示例

### 示例 1: 分析单个实验

```bash
# 分析 hopper_pderl 实验结果
python visualize_results.py -dir results/hopper_pderl
```

输出：
```
=== 训练结果摘要: hopper_pderl ===

📊 ERL Score 统计:
  最高分数: 2988.04
  最终分数: 2950.06
  平均分数: 1876.32
  标准差: 1024.15
  总游戏数: 4464

🎯 DDPG Reward 统计:
  最高奖励: 2845.23
  最终奖励: 2756.89
  平均奖励: 1654.78
  总帧数: 892800
```

### 示例 2: 比较多个实验

```bash
# 比较不同环境或参数设置的实验
python visualize_results.py -compare results/hopper_pderl results/walker_pderl results/ant_pderl
```

### 示例 3: 快速查看统计信息

```bash
# 只查看数值统计，不生成图表
python visualize_results.py -dir results/hopper_pderl --stats_only
```

## 输出文件

脚本会在结果目录中生成以下可视化文件：
- `training_curves.png`: 训练曲线图
- `selection_stats.png`: 选择统计图

## 自定义分析

### 在 Python 中使用

```python
from visualize_results import load_csv_data, print_summary_stats

# 加载数据
data = load_csv_data('results/hopper_pderl/erl_score.csv')

# 自定义分析
print(f"训练改进: {data['y'].iloc[-1] - data['y'].iloc[0]:.2f}")
print(f"收敛游戏数: {data[data['y'] > data['y'].max() * 0.9]['x'].iloc[0]:.0f}")

# 打印摘要
print_summary_stats('results/hopper_pderl')
```

### 添加自定义指标

可以修改 `visualize_results.py` 来添加更多分析功能：

```python
def calculate_learning_efficiency(data):
    """计算学习效率"""
    if len(data) < 2:
        return 0
    
    # 计算每1000游戏的平均改进
    improvement_per_1k = (data['y'].iloc[-1] - data['y'].iloc[0]) / (data['x'].iloc[-1] / 1000)
    return improvement_per_1k

def detect_convergence(data, threshold=0.05):
    """检测收敛点"""
    # 计算滑动窗口内的变化率
    window_size = min(10, len(data) // 4)
    rolling_std = data['y'].rolling(window=window_size).std()
    
    # 找到标准差小于阈值的第一个点
    convergence_idx = rolling_std[rolling_std < threshold * data['y'].max()].index
    
    if len(convergence_idx) > 0:
        return data.iloc[convergence_idx[0]]['x']
    return None
```

## 故障排除

### 常见问题

1. **找不到 CSV 文件**
   - 确保训练已经运行并生成了结果文件
   - 检查结果目录路径是否正确

2. **图表显示异常**
   - 确保安装了 matplotlib: `pip install matplotlib`
   - 在服务器环境中可能需要设置: `export MPLBACKEND=Agg`

3. **中文字体显示问题**
   - 脚本已配置中文字体支持
   - 如仍有问题，可安装字体: `sudo apt-get install fonts-wqy-zenhei`

### 性能优化

对于大型数据集：

```python
# 数据采样以提高绘图性能
def downsample_data(data, max_points=1000):
    if len(data) <= max_points:
        return data
    
    step = len(data) // max_points
    return data.iloc[::step]
```

## 扩展功能

### 1. 添加 TensorBoard 支持

```python
from torch.utils.tensorboard import SummaryWriter

def csv_to_tensorboard(csv_file, log_dir, tag):
    """将 CSV 数据转换为 TensorBoard 格式"""
    data = load_csv_data(csv_file)
    writer = SummaryWriter(log_dir)
    
    for _, row in data.iterrows():
        writer.add_scalar(tag, row['y'], row['x'])
    
    writer.close()
```

### 2. 生成训练报告

```python
def generate_report(result_dir, output_file='training_report.html'):
    """生成 HTML 训练报告"""
    # 实现 HTML 报告生成逻辑
    pass
```

这个可视化工具让您能够：
- 🔍 快速了解训练进展
- 📊 比较不同实验效果
- 🎯 识别最佳超参数设置
- 📈 监控算法收敛性
- 🔧 调试训练问题

开始使用：`python visualize_results.py` 🚀