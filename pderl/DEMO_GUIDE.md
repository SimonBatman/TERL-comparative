# PDERL 模型演示指南

## 概述

本指南介绍如何使用 PDERL 项目中的模型演示工具来展示训练好的智能体在各种环境中的表现。

## 🎯 可用工具

### 1. play_pderl.py - 基础演示脚本
原始的模型演示脚本，用于单次运行训练好的模型。

### 2. demo_play.py - 增强演示工具
功能更丰富的演示工具，支持交互式选择、批量测试和多次试验。

## 🚀 快速开始

### 方法一：使用基础演示脚本

```bash
# 基本用法
python play_pderl.py -env Hopper-v2 -model_path demo_test/evo_net.pkl

# 启用渲染（观看智能体表现）
python play_pderl.py -env Hopper-v2 -model_path demo_test/evo_net.pkl -render

# 设置随机种子
python play_pderl.py -env Hopper-v2 -model_path demo_test/evo_net.pkl -seed 42
```

### 方法二：使用增强演示工具

#### 交互式模式（推荐）
```bash
python demo_play.py
```

这将启动交互式界面，让您：
- 选择可用的模型文件
- 选择测试环境
- 设置渲染、试验次数等参数

#### 命令行模式
```bash
# 单次测试
python demo_play.py -env Hopper-v2 -model demo_test/evo_net.pkl

# 多次试验（获得平均性能）
python demo_play.py -env Hopper-v2 -model demo_test/evo_net.pkl -trials 5

# 不渲染（快速测试）
python demo_play.py -env Hopper-v2 -model demo_test/evo_net.pkl -trials 3 -no_render

# 批量测试模式
python demo_play.py -batch
```

## 🌍 支持的环境

| 环境名称 | 描述 | 推荐用途 |
|---------|------|----------|
| `Hopper-v2` | 单腿跳跃机器人 | 平衡和跳跃控制 |
| `Walker2d-v2` | 双足行走机器人 | 步态学习 |
| `HalfCheetah-v2` | 半身猎豹机器人 | 高速奔跑 |
| `Ant-v2` | 四足蚂蚁机器人 | 多足协调 |
| `Swimmer-v2` | 游泳机器人 | 流体环境导航 |
| `Reacher-v2` | 机械臂到达任务 | 精确控制 |

## 📁 模型文件位置

训练过程中会在以下位置保存模型：

```
项目根目录/
├── demo_test/
│   ├── evo_net.pkl              # 最新保存的模型
│   └── models/
│       ├── evo_net_actor_50.pkl # 第50代演员网络
│       ├── evo_net_actor_100.pkl# 第100代演员网络
│       └── ...
├── results/
│   └── [实验名称]/
│       └── evo_net.pkl          # 实验结束时的最佳模型
└── test_run/
    └── evo_net.pkl              # 测试运行的模型
```

## 🎮 演示示例

### 示例 1：快速测试新训练的模型

```bash
# 训练一个简短的模型
python run_pderl.py -env Hopper-v2 -logdir quick_test -save_periodic -next_save 25

# 等待训练保存模型后，测试表现
python demo_play.py -env Hopper-v2 -model quick_test/evo_net.pkl -trials 3
```

### 示例 2：比较不同训练阶段的模型

```bash
# 测试早期模型（第50代）
python demo_play.py -env Hopper-v2 -model demo_test/models/evo_net_actor_50.pkl -trials 5 -no_render

# 测试后期模型（第150代）
python demo_play.py -env Hopper-v2 -model demo_test/models/evo_net_actor_150.pkl -trials 5 -no_render
```

### 示例 3：跨环境性能测试

```bash
# 使用批量模式测试模型在多个环境中的表现
python demo_play.py -batch
```

## 📊 性能解读

### 奖励分数参考

| 环境 | 随机策略 | 良好表现 | 优秀表现 |
|------|----------|----------|----------|
| Hopper-v2 | ~100 | >1000 | >3000 |
| Walker2d-v2 | ~50 | >2000 | >4000 |
| HalfCheetah-v2 | ~-500 | >2000 | >10000 |
| Ant-v2 | ~100 | >3000 | >6000 |

### 实际测试结果示例

```
🎮 运行演示: Hopper-v2
📁 模型路径: results/hopper_pderl/evo_net.pkl
🎲 随机种子: 7
🖥️ 渲染: 是

🔄 试验 1/1
✅ 奖励: 3555.03

📊 平均奖励 (1 次试验): 3555.03
```

这个结果表明模型在 Hopper-v2 环境中达到了优秀水平。

## 🔧 故障排除

### 常见问题

1. **找不到模型文件**
   ```
   ❌ 未找到模型文件！
   ```
   **解决方案**：
   - 确保已经运行过训练并保存了模型
   - 检查模型文件路径是否正确
   - 使用 `python demo_play.py` 查看可用模型

2. **环境渲染问题**
   ```
   Creating window glfw
   ```
   **解决方案**：
   - 确保安装了 OpenGL 支持
   - 在服务器环境中使用 `-no_render` 参数
   - 检查显卡驱动是否正常

3. **CUDA 相关错误**
   ```
   RuntimeError: CUDA out of memory
   ```
   **解决方案**：
   - 修改 `play_pderl.py` 中的设备设置：
     ```python
     parameters.device = torch.device('cpu')  # 使用CPU
     ```

### 性能优化建议

1. **快速测试**：使用 `-no_render` 和较少的试验次数
2. **准确评估**：使用多次试验（3-5次）获得稳定的平均性能
3. **可视化观察**：使用 `-render` 观察智能体的行为模式

## 🎯 高级用法

### 自定义评估脚本

```python
from demo_play import run_demo

# 自定义评估函数
def evaluate_model_suite(model_path, environments, trials=3):
    results = {}
    for env in environments:
        avg_reward = run_demo(env, model_path, render=False, trials=trials)
        results[env] = avg_reward
        print(f"{env}: {avg_reward:.2f}")
    return results

# 使用示例
envs = ['Hopper-v2', 'Walker2d-v2', 'HalfCheetah-v2']
results = evaluate_model_suite('demo_test/evo_net.pkl', envs)
```

### 模型性能监控

```python
import time
from pathlib import Path

def monitor_training_progress(model_dir, test_env='Hopper-v2', interval=300):
    """监控训练进度，定期测试模型性能"""
    model_path = Path(model_dir) / 'evo_net.pkl'
    
    while True:
        if model_path.exists():
            reward = run_demo(test_env, str(model_path), render=False, trials=1)
            print(f"[{time.strftime('%H:%M:%S')}] 当前性能: {reward:.2f}")
        
        time.sleep(interval)  # 等待5分钟

# 使用示例（在训练过程中运行）
# monitor_training_progress('demo_test')
```

## 📈 结果分析

### 性能趋势分析

```python
# 分析不同训练阶段的性能
stages = [50, 100, 150]
performances = []

for stage in stages:
    model_path = f'demo_test/models/evo_net_actor_{stage}.pkl'
    if Path(model_path).exists():
        reward = run_demo('Hopper-v2', model_path, render=False, trials=3)
        performances.append((stage, reward))
        print(f"第{stage}代: {reward:.2f}")

# 绘制性能曲线
import matplotlib.pyplot as plt

if performances:
    stages, rewards = zip(*performances)
    plt.plot(stages, rewards, 'o-')
    plt.xlabel('训练代数')
    plt.ylabel('平均奖励')
    plt.title('训练进度 vs 性能')
    plt.show()
```

## 🎉 最佳实践

1. **训练监控**：定期保存模型并测试性能
2. **多环境验证**：在多个环境中测试模型的泛化能力
3. **统计显著性**：使用多次试验确保结果的可靠性
4. **可视化观察**：通过渲染观察智能体的行为是否合理
5. **性能基准**：建立性能基准来评估改进效果

开始您的 PDERL 模型演示之旅：
```bash
python demo_play.py
```

🚀 享受观看您的智能体学习和表现的过程！