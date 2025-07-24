# PDERL 云平台快速部署指南

🚀 **一键部署到云平台，充分利用GPU资源进行并行强化学习训练**

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/TERL-comparative.git
cd TERL-comparative/pderl
```

### 2. 一键环境设置

```bash
# 给脚本执行权限
chmod +x cloud_setup.sh

# 运行一键部署脚本
./cloud_setup.sh
```

### 3. 开始训练

```bash
# 交互式训练 (推荐)
./run_parallel_experiments.sh
# 选择环境 -> 选择gpu_optimized预设 -> 启用TensorBoard

# 或直接运行GPU优化训练
python parallel_train.py -env Walker2d-v2 -preset gpu_optimized -workers 5
```

### 4. 启动TensorBoard监控

```bash
# 在新终端中运行
tensorboard --logdir=parallel_experiments --port=6006 --host=0.0.0.0
# 访问: http://your-server-ip:6006
```

## 📊 预设配置

| 预设 | 描述 | 种子数 | TensorBoard | 适用场景 |
|------|------|--------|-------------|----------|
| `gpu_optimized` | GPU优化 | 5 | ✅ | 16G显存云平台 |
| `quick_test` | 快速测试 | 3 | ❌ | 环境验证 |
| `standard` | 标准实验 | 5 | ❌ | 常规训练 |
| `comprehensive` | 全面实验 | 10 | ❌ | 完整评估 |

## 支持的环境

- **Hopper-v2** - 单腿跳跃机器人
- **Walker2d-v2** - 双足行走机器人  
- **HalfCheetah-v2** - 半猎豹奔跑
- **Ant-v2** - 四足蚂蚁
- **Swimmer-v2** - 游泳机器人
- **Reacher-v2** - 机械臂到达

## 性能建议

### GPU内存配置
- **16G显存**: 最大5个并发
- **24G显存**: 最大7-8个并发
- **32G显存**: 最大10+个并发

### 预期训练时间 (16G GPU)
- **Walker2d-v2**: ~2-3小时/实验
- **HalfCheetah-v2**: ~2-4小时/实验
- **Ant-v2**: ~3-5小时/实验

## 常用命令

```bash
# 查看所有预设
python parallel_train.py --list-presets

# 自定义训练
python parallel_train.py -env HalfCheetah-v2 -seeds 1 2 3 4 5 -workers 5

# 监控GPU使用
watch -n 1 nvidia-smi

# 分析结果
python analyze_parallel_results.py

# 可视化结果
python visualize_results.py
```

## 长时间训练

```bash
# 使用screen保持会话
screen -S pderl_training
./run_parallel_experiments.sh
# Ctrl+A+D 分离会话

# 重新连接
screen -r pderl_training
```

## 结果目录

```
parallel_experiments/
├── experiment_report.json     # 实验总结
├── Walker2d-v2_seed_1/
│   ├── training.log           # 训练日志
│   └── *.pkl                  # 训练模型
└── ...
```

## 故障排除

### CUDA内存不足
```bash
# 减少并发数
python parallel_train.py -env Walker2d-v2 -preset gpu_optimized -workers 3
```

### MuJoCo问题
```bash
# 检查MuJoCo环境
python -c "import mujoco_py; print('MuJoCo OK')"
```

### 环境测试
```bash
# 测试单个环境
python -c "import gym; env = gym.make('Walker2d-v2'); print('Environment OK')"
```

## 文件说明

- `cloud_setup.sh` - 一键环境设置脚本
- `run_parallel_experiments.sh` - 交互式训练脚本
- `parallel_train.py` - 并行训练主程序
- `requirements.txt` - 依赖包列表
- `CLOUD_DEPLOYMENT.md` - 详细部署文档

## 技术支持

遇到问题请检查：
1. 训练日志: `parallel_experiments/*/training.log`
2. GPU状态: `nvidia-smi`
3. 环境配置: `conda list`

---

🎯 **目标**: 在云平台上高效运行PDERL并行训练，充分利用GPU资源

📊 **结果**: 获得多个随机种子的训练结果，提高实验可靠性

🔬 **分析**: 使用内置工具分析和可视化训练结果