# PDERL 云平台部署指南

本指南介绍如何在Linux云平台上部署和运行PDERL项目，充分利用GPU资源进行并行训练。

## 系统要求

- **操作系统**: Linux (Ubuntu 18.04+ 推荐)
- **GPU**: NVIDIA GPU with 16GB+ VRAM
- **CUDA**: 11.0+
- **Python**: 3.7+
- **内存**: 32GB+ RAM 推荐

## 部署步骤

### 1. 克隆项目

```bash
# 克隆项目到云平台
git clone https://github.com/your-username/TERL-comparative.git
cd TERL-comparative/pderl
```

### 2. 环境配置

```bash
# 创建conda环境
conda create -n erl_env python=3.8
conda activate erl_env

# 安装PyTorch (CUDA版本)
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# 安装其他依赖
pip install -r requirements.txt

# 安装MuJoCo和gym环境
pip install mujoco-py
pip install gym[mujoco]
```

### 3. 验证GPU环境

```bash
# 检查CUDA是否可用
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
python -c "import torch; print('GPU count:', torch.cuda.device_count())"
python -c "import torch; print('GPU name:', torch.cuda.get_device_name(0))"
```

### 4. 运行训练

#### 使用交互式脚本

```bash
# 给脚本执行权限
chmod +x run_parallel_experiments.sh

# 运行交互式训练脚本
./run_parallel_experiments.sh
```

#### 直接命令行运行

```bash
# GPU优化预设 (推荐用于16G显存，包含TensorBoard)
python parallel_train.py -env Walker2d-v2 -preset gpu_optimized -workers 5

# 启用TensorBoard的自定义训练
python parallel_train.py -env HalfCheetah-v2 -seeds 1 2 3 4 5 -workers 5 -use_cuda -use_tensorboard -log_weights

# 快速测试
python parallel_train.py -env Hopper-v2 -preset quick_test -workers 3

# 传统CSV记录方式
python parallel_train.py -env HalfCheetah-v2 -seeds 1 2 3 4 5 -workers 5 -use_cuda
```

### 5. TensorBoard监控

```bash
# 启动TensorBoard服务
tensorboard --logdir=parallel_experiments --port=6006 --host=0.0.0.0

# 在浏览器中访问
# http://your-server-ip:6006
```

## 📊 TensorBoard使用指南

### 启用TensorBoard记录
```bash
# 方法1: 使用gpu_optimized预设 (默认启用)
python parallel_train.py -env Hopper-v2 -preset gpu_optimized -workers 5

# 方法2: 手动启用TensorBoard
python parallel_train.py -env Hopper-v2 -seeds 1 2 3 4 5 -use_tensorboard -log_weights -workers 5
```

### 启动TensorBoard服务
```bash
# 在训练目录启动TensorBoard
tensorboard --logdir=parallel_experiments --port=6006 --host=0.0.0.0

# 后台运行
nohup tensorboard --logdir=parallel_experiments --port=6006 --host=0.0.0.0 > tensorboard.log 2>&1 &
```

### 访问TensorBoard
- 本地访问: `http://localhost:6006`
- 远程访问: `http://your-server-ip:6006`
- 云平台: 需要开放6006端口

### TensorBoard记录内容
- **性能指标**: ERL分数、DDPG奖励、最佳训练适应度
- **损失函数**: 策略梯度损失、行为克隆损失
- **进化统计**: 精英比例、选择比例、丢弃比例、种群新颖性
- **训练进度**: 游戏数量、训练时间
- **网络权重**: Actor和Critic网络权重分布 (可选)
- **自定义指标**: 训练效率、资源使用等

## 📊 预设配置说明

| 预设名称 | 描述 | 种子数量 | 训练帧数 | TensorBoard | 适用场景 |
|---------|------|---------|---------|-------------|----------|
| `quick_test` | 快速测试 | 3 | 50,000 | ❌ | 验证环境配置 |
| `standard` | 标准实验 | 5 | 默认 | ❌ | 常规训练 |
| `comprehensive` | 全面实验 | 10 | 默认 | ❌ | 完整评估 |
| `gpu_optimized` | GPU优化 | 5 | 1,000,000 | ✅ | 16G显存云平台 |
| `custom_seeds` | 自定义种子 | 5 | 默认 | ❌ | 特定种子实验 |

## 性能优化建议

### GPU内存优化

- **16G显存**: 建议最大并发数为5
- **24G显存**: 建议最大并发数为7-8
- **32G显存**: 建议最大并发数为10+

### 系统资源监控

```bash
# 监控GPU使用情况
watch -n 1 nvidia-smi

# 监控系统资源
htop

# 监控磁盘空间
df -h
```

### 长时间训练建议

```bash
# 使用screen或tmux保持会话
screen -S pderl_training
./run_parallel_experiments.sh
# Ctrl+A+D 分离会话

# 重新连接会话
screen -r pderl_training
```

## 结果管理

### 训练结果目录结构

```
parallel_experiments/
├── experiment_report.json          # 实验总结报告
├── Walker2d-v2_seed_1/
│   ├── training.log                # 训练日志
│   ├── info.txt                    # 实验信息
│   ├── tensorboard/                # TensorBoard日志 (如果启用)
│   │   └── events.out.tfevents.*   # TensorBoard事件文件
│   ├── erl_score.csv              # ERL分数记录 (向后兼容)
│   ├── ddpg_score.csv              # DDPG分数记录 (向后兼容)
│   ├── evo_net.pkl                 # 最终模型
│   └── models/                     # 周期性保存的模型
├── Walker2d-v2_seed_2/
│   └── ...
└── Walker2d-v2_seed_3/
    └── ...
```

### 结果分析

```bash
# 分析并行训练结果
python analyze_parallel_results.py

# 生成可视化图表
python visualize_results.py
```

### 模型测试

```bash
# 测试训练好的模型
python test_trained_model.py -model parallel_experiments/Walker2d-v2_seed_1/model_best.pkl -env Walker2d-v2
```

## 常见问题

### 1. CUDA内存不足

```bash
# 减少并发数
python parallel_train.py -env Walker2d-v2 -preset gpu_optimized -workers 3

# 或减少种群大小
python parallel_train.py -env Walker2d-v2 -seeds 1 2 3 -popsize 5 -workers 3
```

### 2. MuJoCo许可证问题

```bash
# 设置MuJoCo许可证路径
export MUJOCO_PY_MUJOCO_PATH=/path/to/mujoco
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/path/to/mujoco/bin
```

### 3. 训练中断恢复

```bash
# 检查现有实验
ls parallel_experiments/

# 从特定检查点恢复 (如果支持)
python run_pderl.py -env Walker2d-v2 -seed 1 -logdir parallel_experiments/Walker2d-v2_seed_1 -resume
```

## 性能基准

在配置为16G GPU内存的云平台上，预期性能：

- **Walker2d-v2**: ~2-3小时/实验 (100万帧)
- **HalfCheetah-v2**: ~2-4小时/实验
- **Ant-v2**: ~3-5小时/实验
- **并发5个实验**: 总时间约3-6小时

## 成本优化

1. **使用抢占式实例**: 成本可降低60-80%
2. **合理安排训练时间**: 避开高峰期
3. **及时释放资源**: 训练完成后立即停止实例
4. **批量实验**: 一次性运行多个环境的实验

## 技术支持

如遇到问题，请检查：

1. 训练日志: `parallel_experiments/*/training.log`
2. 系统资源: `nvidia-smi`, `htop`
3. 环境配置: `conda list`, `pip list`
4. CUDA版本: `nvcc --version`

更多详细信息请参考项目文档和可视化指南。