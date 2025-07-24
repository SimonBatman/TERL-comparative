# ERL 实验结果可视化

本目录包含用于可视化 ERL（Evolutionary Reinforcement Learning）实验结果的最终工具。

## 📁 文件夹结构

```
plotting_results/
├── README_plotting.md          # 详细使用说明
├── INDEX.md                    # 本文件
├── plot_results_enhanced.py    # 增强版绘图工具
├── demo_enhanced_plotting.py   # 演示脚本
├── plot_reacher_results.py     # 原始Reacher绘图脚本
├── Reacher-v2/                 # Reacher-v2环境结果
│   ├── reacher-v2_erl_results.png
│   └── reacher-v2_erl_results.pdf
├── Ant-v2/                     # Ant-v2环境结果
│   ├── ant-v2_erl_results.png
│   └── ant-v2_erl_results.pdf
├── HalfCheetah-v2/             # HalfCheetah-v2环境结果
│   ├── halfcheetah-v2_erl_results.png
│   └── halfcheetah-v2_erl_results.pdf
├── Hopper-v2/                  # Hopper-v2环境结果（待生成）
├── Swimmer-v2/                 # Swimmer-v2环境结果（待生成）
└── Walker2d-v2/                # Walker2d-v2环境结果（待生成）
```

### 🔧 核心工具
- `plot_results_enhanced.py` - 增强版绘图工具（主要脚本）
- `plot_reacher_results.py` - 原始的 Reacher-v2 绘图脚本
- `demo_enhanced_plotting.py` - 功能演示脚本
- `README_plotting.md` - 详细使用说明文档

### 📊 生成的图表

现在所有图表都按环境自动分类到对应的子文件夹中，每个环境包含：
- PNG 格式图表（高分辨率位图）
- PDF 格式图表（矢量图）

## 🚀 快速使用

### 基本用法
```bash
# 生成 Reacher-v2 环境的图表（自动保存到 Reacher-v2/ 文件夹）
python plot_results_enhanced.py --base_dir ../runs/Reacher-v2

# 生成 Ant-v2 环境的图表（自动保存到 Ant-v2/ 文件夹）
python plot_results_enhanced.py --base_dir ../runs/Ant-v2

# 生成 HalfCheetah-v2 环境的图表（自动保存到 HalfCheetah-v2/ 文件夹）
python plot_results_enhanced.py --base_dir ../runs/HalfCheetah-v2
```

### 高级用法
```bash
# 论文格式：显示标准差误差线（推荐用于学术发表）
python plot_results_enhanced.py --base_dir ../runs/Reacher-v2 --confidence_interval --error_type std --smooth_sigma 15

# 统计格式：显示95%置信区间
python plot_results_enhanced.py --base_dir ../runs/Reacher-v2 --confidence_interval --error_type ci --smooth_sigma 15

# 批量处理多个环境
python demo_enhanced_plotting.py
```

### 查看详细文档
```bash
# 查看完整使用说明
cat README_plotting.md
```

## ✨ 新功能特性

- **🗂️ 自动分类**: 图表自动保存到对应环境的子文件夹
- **📁 智能组织**: 每个环境有独立的存储空间
- **🔄 增量更新**: 重新运行只更新对应环境的图表
- **🎯 精确定位**: 快速找到特定环境的结果

## 📈 图表说明

- **PNG 格式**: 高分辨率位图，适合在文档中使用
- **PDF 格式**: 矢量图，适合论文发表和打印
- **误差线**: 阴影区域表示多个种子结果的变化范围，支持两种类型：
  - **标准差误差线** (`--error_type std`): Mean ± Standard Deviation，适合论文发表
  - **95%置信区间** (`--error_type ci`): Mean ± 1.96 × Standard Error，适合统计分析
- **平均曲线**: 红色实线表示多个种子的平均性能
- **X轴**: 训练步数 (Million Steps)
- **Y轴**: 平均回报 (Performance)
- **自动坐标轴**: 根据不同环境自动调整Y轴范围

## 🔄 更新图表

当有新的实验数据时，只需重新运行对应的命令即可更新图表：

```bash
# 更新特定环境的图表（自动保存到对应文件夹）
python plot_results_enhanced.py --base_dir ../runs/[环境名称]

# 或运行演示脚本更新所有图表
python demo_enhanced_plotting.py
```

增强版工具会自动：
- 发现新的实验目录
- 调整坐标轴范围
- 生成高质量的可视化结果
- 按环境分类保存图表

## 📂 文件夹管理

- 每个环境的图表自动保存到以环境名命名的子文件夹
- 支持的环境：Reacher-v2, Ant-v2, HalfCheetah-v2, Hopper-v2, Swimmer-v2, Walker2d-v2
- 如果环境文件夹不存在，脚本会自动创建
- 便于版本控制和结果管理

---
*最后更新: 2025-07-15*