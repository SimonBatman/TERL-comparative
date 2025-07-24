# PDERL 并行训练指南

本指南介绍如何使用PDERL并行训练脚本在同一环境下使用不同随机种子进行多个并行实验。

## 📋 目录

- [快速开始](#快速开始)
- [脚本说明](#脚本说明)
- [使用方法](#使用方法)
- [预设配置](#预设配置)
- [结果分析](#结果分析)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 🚀 快速开始

### 方法1: 使用批处理脚本 (推荐)

```bash
# 1. 激活环境
conda activate erl_env

# 2. 运行批处理脚本
.\run_parallel_experiments.bat
```

### 方法2: 直接使用Python脚本

```bash
# 标准实验 (5个种子)
python parallel_train.py -env Hopper-v2 -preset standard

# 快速测试 (3个种子，较少训练步数)
python parallel_train.py -env Hopper-v2 -preset quick_test

# 自定义种子
python parallel_train.py -env Hopper-v2 -seeds 1 2 3 4 5
```

## 📁 脚本说明

### 1. `parallel_train.py` - 主要并行训练脚本

**功能特性:**
- 支持多个随机种子的并行训练
- 自动资源监控和进程管理
- 预设配置和自定义参数
- 实时进度显示和错误处理
- 自动生成实验报告

### 2. `run_parallel_experiments.bat` - Windows批处理脚本

**功能特性:**
- 交互式界面，易于使用
- 自动检查conda环境
- 预设环境和配置选择
- 一键启动并行训练

### 3. `analyze_parallel_results.py` - 结果分析脚本

**功能特性:**
- 统计分析和性能对比
- 可视化图表生成
- 最佳模型识别
- 详细报告生成

## 🎯 使用方法

### 基本命令格式

```bash
python parallel_train.py [选项]
```

### 主要参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-env` | 训练环境名称 | `-env Hopper-v2` |
| `-preset` | 预设配置 | `-preset standard` |
| `-seeds` | 自定义种子列表 | `-seeds 1 2 3 4 5` |
| `-workers` | 最大并发数 | `-workers 4` |
| `-logdir` | 基础日志目录 | `-logdir my_experiments` |
| `-use_cuda` | 使用CUDA加速 | `-use_cuda` |

### 训练参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-popsize` | 种群大小 | 10 |
| `-rollout_size` | Rollout大小 | 1 |
| `-num_frames` | 训练帧数 | 1000000 |

## ⚙️ 预设配置

### 1. `quick_test` - 快速测试
- **种子**: [1, 2, 3]
- **训练帧数**: 50,000
- **种群大小**: 5
- **适用场景**: 快速验证代码和环境

### 2. `standard` - 标准实验
- **种子**: [1, 2, 3, 4, 5]
- **训练帧数**: 1,000,000 (默认)
- **适用场景**: 常规实验和论文结果

### 3. `comprehensive` - 全面实验
- **种子**: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
- **训练帧数**: 1,000,000 (默认)
- **适用场景**: 深入研究和统计分析

### 4. `custom_seeds` - 自定义种子
- **种子**: [7, 42, 123, 456, 789]
- **适用场景**: 特定种子的重现实验

### 查看所有预设

```bash
python parallel_train.py --list-presets
```

## 📊 使用示例

### 示例1: 标准Hopper实验

```bash
python parallel_train.py -env Hopper-v2 -preset standard
```

### 示例2: 快速Walker2d测试

```bash
python parallel_train.py -env Walker2d-v2 -preset quick_test -use_cuda
```

### 示例3: 自定义HalfCheetah实验

```bash
python parallel_train.py -env HalfCheetah-v2 -seeds 1 5 10 15 20 -popsize 15 -workers 3
```

### 示例4: 大规模Ant实验

```bash
python parallel_train.py -env Ant-v2 -preset comprehensive -num_frames 2000000
```

## 📈 结果分析

### 基本分析

```bash
# 分析实验结果
python analyze_parallel_results.py -dir parallel_experiments

# 仅生成统计报告
python analyze_parallel_results.py -dir parallel_experiments --stats-only

# 跳过图表生成
python analyze_parallel_results.py -dir parallel_experiments --no-plots
```

### 生成的文件

**统计报告:**
- `analysis_report.csv` - 详细数据表
- `summary_statistics.txt` - 汇总统计
- `best_models.json` - 最佳模型信息
- `experiment_report.json` - 实验执行报告

**可视化图表:**
- `performance_distribution.png` - 性能分布箱线图
- `seed_comparison_*.png` - 种子间性能对比
- `learning_curves_*.png` - 学习曲线对比
- `performance_correlation.png` - 性能相关性分析

## 📁 目录结构

```
parallel_experiments/
├── experiment_report.json          # 实验执行报告
├── analysis_report.csv             # 分析报告
├── summary_statistics.txt          # 统计汇总
├── best_models.json               # 最佳模型信息
├── performance_distribution.png    # 性能分布图
├── seed_comparison_hopper.png     # 种子对比图
├── learning_curves_hopper.png     # 学习曲线图
├── performance_correlation.png    # 相关性分析图
├── Hopper-v2_seed_1/              # 实验1目录
│   ├── training.log               # 训练日志
│   ├── evo_net.pkl                # 主模型文件
│   ├── erl_score.csv              # ERL分数记录
│   ├── ddpg_score.csv             # DDPG分数记录
│   └── info.txt                   # 实验信息
├── Hopper-v2_seed_2/              # 实验2目录
└── ...
```

## 💡 最佳实践

### 1. 资源管理

```bash
# 根据CPU核心数设置并发数
python parallel_train.py -env Hopper-v2 -preset standard -workers 4

# 监控系统资源使用情况
# 脚本会自动显示CPU和内存使用率
```

### 2. 实验设计

```bash
# 先进行快速测试验证环境
python parallel_train.py -env Hopper-v2 -preset quick_test

# 再进行正式实验
python parallel_train.py -env Hopper-v2 -preset standard
```

### 3. 结果管理

```bash
# 使用有意义的目录名
python parallel_train.py -env Hopper-v2 -preset standard -logdir hopper_baseline_exp

# 定期分析结果
python analyze_parallel_results.py -dir hopper_baseline_exp
```

### 4. 模型演示

```bash
# 找到最佳模型后进行演示
python play_pderl.py -env Hopper-v2 -model_path parallel_experiments/Hopper-v2_seed_3/evo_net.pkl -render
```

## 🔧 故障排除

### 常见问题

**1. 环境未激活**
```bash
# 解决方案
conda activate erl_env
```

**2. 内存不足**
```bash
# 减少并发数
python parallel_train.py -env Hopper-v2 -preset standard -workers 2

# 或使用快速测试配置
python parallel_train.py -env Hopper-v2 -preset quick_test
```

**3. CUDA错误**
```bash
# 不使用CUDA
python parallel_train.py -env Hopper-v2 -preset standard

# 检查CUDA可用性
python test_env_setup.py
```

**4. 进程卡死**
```bash
# 使用Ctrl+C停止所有进程
# 脚本会自动清理子进程
```

### 调试技巧

**1. 查看训练日志**
```bash
# 实时查看某个实验的日志
tail -f parallel_experiments/Hopper-v2_seed_1/training.log
```

**2. 检查实验状态**
```bash
# 查看实验报告
cat parallel_experiments/experiment_report.json
```

**3. 验证模型文件**
```bash
# 列出所有模型文件
find parallel_experiments -name "*.pkl"
```

## 🎯 高级用法

### 1. 批量环境实验

```bash
# 创建批量脚本
for env in Hopper-v2 Walker2d-v2 HalfCheetah-v2; do
    python parallel_train.py -env $env -preset standard -logdir "batch_exp_${env}"
done
```

### 2. 参数扫描

```bash
# 不同种群大小的实验
for popsize in 5 10 15 20; do
    python parallel_train.py -env Hopper-v2 -seeds 1 2 3 -popsize $popsize -logdir "popsize_${popsize}"
done
```

### 3. 结果对比

```bash
# 分析多个实验目录
python analyze_parallel_results.py -dir experiment1
python analyze_parallel_results.py -dir experiment2
# 然后手动对比结果
```

## 📞 技术支持

如果遇到问题，请：

1. 首先运行环境测试: `python test_env_setup.py`
2. 查看训练日志文件
3. 检查系统资源使用情况
4. 尝试使用快速测试配置

## 📚 相关文档

- [DEMO_GUIDE.md](DEMO_GUIDE.md) - 模型演示指南
- [VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md) - 可视化指南
- [README.md](README.md) - 项目主要文档

---

**祝您实验顺利！** 🎉