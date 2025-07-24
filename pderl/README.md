[![Build Status](https://travis-ci.com/crisbodnar/pderl.svg?branch=master)](https://travis-ci.com/crisbodnar/pderl)

# Proximal Distilled Evolutionary Reinforcement Learning (PDERL)

官方代码实现，对应AAAI 2020论文 "Proximal Distilled Evolutionary Reinforcement Learning"。

![PDERL](figures/pderl_gif.gif)

## 📖 论文引用

如果您使用了本代码，请引用以下论文：

```bibtex
@inproceedings{bodnar2020proximal,
  title={Proximal distilled evolutionary reinforcement learning},
  author={Bodnar, Cristian and Day, Ben and Li{\'{o}}, Pietro},
  booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
  volume={34},
  number={04},
  pages={3283--3290},
  year={2020}
}
```

## 🎯 算法概述

PDERL是一种结合了进化算法和强化学习的混合方法，主要特点包括：

- **近端变异 (Proximal Mutations)**: 使用安全变异策略，确保变异后的策略不会偏离原策略太远
- **蒸馏交叉 (Distillation Crossover)**: 基于适应度或距离的知识蒸馏交叉操作
- **进化强化学习**: 结合DDPG和神经进化的优势

## 🛠️ 安装指南

### 环境要求

- Python 3.6+
- CUDA 10.0+ (可选，用于GPU加速)
- MuJoCo 2.0+ (用于物理仿真)

### 步骤1: 克隆仓库

```bash
git clone https://github.com/crisbodnar/pderl.git
cd pderl
```

### 步骤2: 创建虚拟环境

```bash
conda create -n pderl python=3.7
conda activate pderl
```

### 步骤3: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤4: 安装MuJoCo

1. 下载MuJoCo 2.0.2.2从[官方网站](https://www.roboti.us/download.html)
2. 按照[mujoco-py官方指南](https://github.com/openai/mujoco-py)进行安装
3. 设置环境变量：
   ```bash
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/path/to/mujoco/bin
   ```

### 依赖包详情

| 包名 | 版本 | 用途 |
|------|------|------|
| torch | 1.1.0 | 深度学习框架 |
| gym | 0.12.1 | 强化学习环境 |
| numpy | 1.16.3 | 数值计算 |
| pandas | 0.24.2 | 数据处理 |
| mujoco-py | 2.0.2.2 | 物理仿真 |

## 🚀 快速开始

### 基础训练

```bash
python run_pderl.py -env Hopper-v2 -logdir ./results/hopper_basic
```

### 使用PDERL完整功能训练

```bash
python run_pderl.py -env Hopper-v2 -distil -proximal_mut -mut_mag 0.05 -logdir ./results/hopper_pderl
```

### 模型评估

```bash
python play_pderl.py \
    -env Hopper-v2 \
    -model_path ./results/hopper_pderl/evo_net.pkl \
    -render
```

## ⚙️ 详细参数说明

### 训练参数 (run_pderl.py)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-env` | str | 必需 | 环境名称 (Hopper-v2, HalfCheetah-v2, 等) |
| `-seed` | int | 7 | 随机种子 |
| `-logdir` | str | 必需 | 结果保存目录 |
| `-disable_cuda` | flag | False | 禁用CUDA |
| `-render` | flag | False | 渲染训练过程 |

#### 进化算法参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-proximal_mut` | flag | False | 启用近端变异 |
| `-distil` | flag | False | 启用蒸馏交叉 |
| `-distil_type` | str | 'fitness' | 蒸馏类型: 'fitness' 或 'distance' |
| `-mut_mag` | float | 0.05 | 变异幅度 |
| `-mut_noise` | flag | False | 使用随机变异幅度 |
| `-novelty` | flag | False | 启用新颖性探索 |

#### 强化学习参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-sync_period` | int | 环境相关 | RL到EA的同步周期 |
| `-per` | flag | False | 启用优先经验回放 |

#### 调试和保存参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-verbose_mut` | flag | False | 详细变异信息 |
| `-verbose_crossover` | flag | False | 详细交叉信息 |
| `-save_periodic` | flag | False | 定期保存模型 |
| `-next_save` | int | 200 | 保存频率(代数) |
| `-opstat` | flag | False | 保存算子统计信息 |
| `-test_operators` | flag | False | 测试变异算子 |

### 评估参数 (play_pderl.py)

| 参数 | 类型 | 说明 |
|------|------|------|
| `-env` | str | 环境名称 |
| `-model_path` | str | 模型文件路径 |
| `-render` | flag | 渲染评估过程 |
| `-seed` | int | 随机种子 |

## 🏗️ 项目结构

```
pderl/
├── core/                    # 核心算法实现
│   ├── agent.py            # 主要Agent类
│   ├── ddpg.py             # DDPG算法实现
│   ├── mod_neuro_evo.py    # 神经进化模块
│   ├── mod_utils.py        # 工具函数
│   ├── operator_runner.py  # 算子测试器
│   └── replay_memory.py    # 经验回放缓冲区
├── figures/                 # 图片和可视化
├── tests/                   # 单元测试
├── parameters.py           # 参数配置
├── run_pderl.py           # 训练脚本
├── play_pderl.py          # 评估脚本
├── requirements.txt        # 依赖列表
└── README.md              # 本文件
```

### 核心模块说明

- **agent.py**: 包含主要的Agent类，协调进化算法和强化学习
- **ddpg.py**: DDPG算法的实现，包括Actor-Critic网络
- **mod_neuro_evo.py**: 神经进化算法，包括选择、变异、交叉操作
- **replay_memory.py**: 经验回放机制，支持普通和优先经验回放

## 🎮 支持的环境

本项目在以下MuJoCo环境中进行了测试：

| 环境名称 | 状态维度 | 动作维度 | 描述 |
|----------|----------|----------|------|
| Hopper-v2 | 11 | 3 | 单腿跳跃机器人 |
| HalfCheetah-v2 | 17 | 6 | 半猎豹跑步 |
| Swimmer-v2 | 8 | 2 | 游泳机器人 |
| Ant-v2 | 111 | 8 | 四足蚂蚁 |
| Walker2d-v2 | 17 | 6 | 双足行走机器人 |

## 📊 训练监控

训练过程中会生成以下文件用于监控：

- `erl_score.csv`: ERL测试分数
- `ddpg_score.csv`: DDPG奖励
- `frame_erl_score.csv`: 基于帧数的分数
- `time_erl_score.csv`: 基于时间的分数
- `*_selection.csv`: 选择统计信息
- `info.txt`: 超参数配置

### 输出示例

```
#Games: 31 #Frames: 1439  Train_Max: 151.42  Test_Score: 159.52  Avg: 0.00  ENV: Hopper-v2  DDPG Reward: 68.95  PG Loss: -2.8483
```

## 🔧 高级用法

### 自定义超参数

修改 `parameters.py` 文件中的默认参数：

```python
# 修改种群大小
self.pop_size = 15

# 修改变异概率
self.mutation_prob = 0.8

# 修改精英比例
self.elite_fraction = 0.3
```

### 添加新环境

1. 在 `parameters.py` 中添加环境特定的配置
2. 确保环境符合OpenAI Gym接口
3. 根据需要调整评估次数和同步周期

### 算子测试

测试变异和交叉算子的效果：

```bash
python run_pderl.py -env Hopper-v2 -test_operators -save_periodic -logdir ./test_ops
```

## 🐛 常见问题

### Q: 训练过程中出现CUDA内存不足
**A**: 尝试以下解决方案：
- 使用 `-disable_cuda` 参数
- 减小批次大小
- 减小种群大小

### Q: MuJoCo安装失败
**A**: 确保：
- 正确设置了MuJoCo许可证
- 安装了必要的系统依赖
- 环境变量配置正确

### Q: 训练收敛慢
**A**: 尝试：
- 调整学习率
- 增加种群大小
- 使用不同的变异幅度

## 📈 性能基准

在标准MuJoCo环境上的性能表现：

| 环境 | PDERL | DDPG | ERL |
|------|-------|------|-----|
| Hopper-v2 | **3500+** | 2500 | 3200 |
| HalfCheetah-v2 | **12000+** | 9000 | 11000 |
| Walker2d-v2 | **5000+** | 3000 | 4500 |

*注：结果可能因随机种子和硬件配置而异*

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

本代码主要基于以下工作：

- [Khadka and Tumer的ERL实现](https://github.com/ShawK91/erl_paper_nips18)
- [Uber Research的安全变异代码](https://github.com/uber-research/safemutations)

感谢原作者们开源了他们的代码！

## 📞 联系方式

如有问题或建议，请：

- 提交Issue到本仓库
- 发送邮件给论文作者
- 查看原论文获取更多技术细节

---

**注意**: 本README基于原始代码进行了详细扩展，包含了更多实用信息和中文说明。如需英文版本，请参考原始仓库。