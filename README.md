# ERL (Evolutionary Reinforcement Learning) 算法实现

本项目实现了 ERL（进化强化学习）算法，结合了神经进化和 DDPG 强化学习的优势，在连续控制任务上取得了优异的性能。

## 项目结构

```
ERL/
├── core/                    # 核心算法模块
│   ├── ddpg.py             # DDPG 算法实现
│   ├── mod_neuro_evo.py    # 神经进化算法
│   ├── mod_utils.py        # 工具函数和类
│   └── replay_memory.py    # 经验回放缓冲区
├── run_erl.py              # 主运行文件
├── run_multiple_seeds.bat  # 多种子批量运行脚本
├── run_multiple_seeds_3parallel.bat # 3并行批量运行脚本
├── GoBigger.yml            # Conda 环境配置文件
├── R_ERL/                  # 结果保存目录
└── runs/                   # TensorBoard 日志目录
```

## 环境配置

### 方法一：使用现有的 erl_env 环境

如果您已经有 `erl_env` 环境，可以直接激活使用：

```bash
conda activate erl_env
```

### 方法二：从 GoBigger.yml 创建新环境

使用提供的环境配置文件创建新的 Conda 环境：

```bash
# 创建环境
conda env create -f GoBigger.yml

# 激活环境
conda activate GoBigger
```

### 主要依赖包

- **Python**: 3.6.13
- **PyTorch**: 1.8.1+cu111
- **Gym**: 0.21.0
- **MuJoCo-py**: 2.1.2.14
- **NumPy**: 1.19.2
- **TensorBoard**: 1.15.0
- **其他**: matplotlib, pandas, scipy 等

## 支持的训练环境

本项目支持以下 MuJoCo 连续控制环境：

- **HalfCheetah-v2** - 半猎豹跑步任务
- **Ant-v2** - 四足机器人行走任务
- **Reacher-v2** - 机械臂到达任务
- **Walker2d-v2** - 双足机器人行走任务
- **Swimmer-v2** - 游泳机器人任务
- **Hopper-v2** - 单足跳跃机器人任务

## 运行指令

### 单次训练

```bash
# 激活环境
conda activate erl_env  # 或 conda activate GoBigger

# 运行单个环境训练
python run_erl.py -env HalfCheetah-v2 -seed 7
python run_erl.py -env Ant-v2 -seed 42
python run_erl.py -env Swimmer-v2 -seed 1
```

### 参数说明

- `-env`: 指定训练环境（必需）
- `-seed`: 随机种子，默认为 7

## 批量执行

### 使用批处理文件进行批量训练

项目提供了两个批处理脚本用于批量执行：

#### 1. 标准多种子训练 (`run_multiple_seeds.bat`)

```batch
# 直接双击运行或在命令行执行
run_multiple_seeds.bat
```

**可自定义配置项：**

```batch
# 在批处理文件中修改以下变量
set ENV_NAME=HalfCheetah-v2     # 训练环境
set CONDA_ENV=erl_env           # Conda 环境名
set PYTHON_SCRIPT=run_erl.py    # Python 脚本名
set SEEDS=1 2 3 5 42           # 种子列表（空格分隔）
set START_DELAY=3               # 启动延迟（秒）
```

#### 2. 三并行训练 (`run_multiple_seeds_3parallel.bat`)

```batch
# 适用于资源有限的情况，同时运行3个实验
run_multiple_seeds_3parallel.bat
```

**可自定义配置项：**

```batch
set ENV_NAME=Swimmer-v2         # 训练环境
set CONDA_ENV=erl_env           # Conda 环境名
set SEEDS=0 1 7                # 3个种子（空格分隔）
set START_DELAY=3               # 启动延迟（秒）
```

### 自定义批量执行脚本

您可以根据需要修改批处理文件：

1. **更改环境**: 修改 `ENV_NAME` 为目标环境
2. **更改种子**: 修改 `SEEDS` 列表
3. **更改延迟**: 调整 `START_DELAY` 避免资源冲突
4. **更改环境名**: 修改 `CONDA_ENV` 匹配您的环境

## TensorBoard 可视化

### 启动 TensorBoard

```bash
# 激活环境
conda activate erl_env

# 启动 TensorBoard（查看所有实验）
tensorboard --logdir=runs

# 启动 TensorBoard（查看特定环境）
tensorboard --logdir=runs/HalfCheetah-v2

# 指定端口
tensorboard --logdir=runs --port=6007
```

### 访问可视化界面

在浏览器中打开：`http://localhost:6006`（默认端口）

### 可视化指标

- **charts/best_fitness**: 进化算法最佳适应度
- **charts/rl_return**: DDPG 智能体回报
- **训练进度**: 实时监控训练过程
- **对比分析**: 多种子实验对比

## 结果保存

训练结果保存在以下位置：

- **模型文件**: `R_ERL/evo_net` - 最佳进化网络
- **训练数据**: `R_ERL/*.csv` - 训练统计数据
- **TensorBoard 日志**: `runs/` - 可视化日志

## 算法特点

### ERL 核心优势

1. **双重学习机制**: 结合进化算法的全局搜索和 DDPG 的梯度优化
2. **知识迁移**: RL 智能体与进化种群间的双向知识流动
3. **鲁棒性强**: 多个智能体并行训练，降低失败风险
4. **自适应参数**: 针对不同环境的智能参数调整

### 训练流程

1. **进化阶段**: 评估种群个体，执行选择、交叉、变异
2. **强化学习阶段**: DDPG 智能体收集经验并更新参数
3. **知识同步**: 将 RL 智能体参数迁移到进化种群

## 性能监控

### GPU 使用监控

```bash
# 实时监控 GPU 使用情况
nvidia-smi

# 持续监控
watch -n 1 nvidia-smi
```

### 训练进度监控

- 查看命令行输出的训练统计
- 使用 TensorBoard 实时可视化
- 检查 `R_ERL/` 目录下的 CSV 文件

## 故障排除

### 常见问题

1. **MuJoCo 许可证问题**: 确保 MuJoCo 许可证正确安装
2. **CUDA 版本不匹配**: 检查 PyTorch 和 CUDA 版本兼容性
3. **内存不足**: 减少并行进程数量或调整批次大小
4. **环境依赖**: 确保所有依赖包正确安装

### 调试建议

- 先运行单个种子确保环境正常
- 检查 TensorBoard 日志是否正常生成
- 监控系统资源使用情况
- 查看详细的错误日志

## 引用

如果您使用了本项目的代码，请引用相关论文：

```bibtex
@article{erl2018,
  title={Evolution-Guided Policy Gradient in Reinforcement Learning},
  author={Author Name},
  journal={Conference/Journal Name},
  year={2018}
}
```

## 许可证

本项目遵循 MIT 许可证。详见 LICENSE 文件。

---

**注意**: 确保在运行前正确配置 MuJoCo 环境和相关依赖。如有问题，请检查环境配置和依赖安装。